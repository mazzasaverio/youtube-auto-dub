"""Transcribe stage — faster-whisper with word-level timestamps.

This is the piece the original repo was *missing*: instead of trusting YouTube's
(often absent or auto-generated) subtitles, we transcribe the actual audio and get
precise per-segment timing. That timing is the backbone of the later duration
alignment, so the dub tracks the picture instead of drifting.

faster-whisper runs on CTranslate2 (int8 on CPU), so it is fast and free on a laptop.
"""

from __future__ import annotations

import re
from pathlib import Path

from ytdub.logging import stage_logger
from ytdub.models import Segment

log = stage_logger("transcribe")

# A word that ends a sentence (keeps abbreviations like "U.S." from splitting early
# is out of scope — good enough for dubbing).
_SENTENCE_END = re.compile(r"[.!?…。！？]+[\"'”’)]?\s*$")


def build_sentence_segments(
    words: list[tuple[float, float, str]],
    *,
    max_chars: int = 200,
    max_duration: float = 12.0,
) -> list[Segment]:
    """Group word timestamps into sentence-bounded segments.

    Whisper's own segment boundaries can split mid-sentence, which hurts both
    translation (the MT model sees fragments) and sync (odd chunk lengths). Rebuilding
    on sentence punctuation — while capping length so a single chunk stays within what
    the TTS handles well — gives cleaner text and more natural timing.

    ``words`` is ``(start, end, text)`` tuples in order. Pure function (unit-tested).
    """
    segments: list[Segment] = []
    cur: list[tuple[float, float, str]] = []

    def flush() -> None:
        if not cur:
            return
        text = "".join(w[2] for w in cur).strip()
        if text:
            segments.append(
                Segment(index=len(segments), start=cur[0][0], end=cur[-1][1], text=text)
            )
        cur.clear()

    for w in words:
        cur.append(w)
        text_so_far = "".join(x[2] for x in cur).strip()
        duration = cur[-1][1] - cur[0][0]
        ends_sentence = bool(_SENTENCE_END.search(w[2]))
        too_long = len(text_so_far) >= max_chars or duration >= max_duration
        if ends_sentence or too_long:
            flush()
    flush()
    return segments

# Cache the (potentially large) model across calls in the same process.
_MODEL_CACHE: dict[tuple, object] = {}


def _get_model(model_size: str, device: str, compute_type: str):
    key = (model_size, device, compute_type)
    if key not in _MODEL_CACHE:
        from faster_whisper import WhisperModel  # lazy

        log.info(f"Loading Whisper '{model_size}' on {device} ({compute_type})")
        _MODEL_CACHE[key] = WhisperModel(model_size, device=device, compute_type=compute_type)
    return _MODEL_CACHE[key]


def transcribe(
    audio_path: Path,
    *,
    model_size: str,
    device: str,
    compute_type: str,
    language: str | None = None,
) -> tuple[list[Segment], str]:
    """Return ``(segments, detected_language)`` for ``audio_path``.

    ``language`` may be ``None`` to let Whisper auto-detect the source language.
    """
    # faster-whisper does not expose an "mps" device; treat it as CPU.
    fw_device = "cuda" if device == "cuda" else "cpu"
    model = _get_model(model_size, fw_device, compute_type)

    log.info(f"Transcribing {audio_path.name} (language={language or 'auto'})")
    raw_segments, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        word_timestamps=True,
        vad_filter=True,  # drop non-speech gaps -> tighter segment windows
    )

    # Collect word timestamps across all Whisper segments, then rebuild on sentence
    # boundaries. Fall back to raw segments if a model/run yields no word timings.
    words: list[tuple[float, float, str]] = []
    fallback: list[Segment] = []
    for seg in raw_segments:
        text = (seg.text or "").strip()
        if text:
            fallback.append(
                Segment(index=len(fallback), start=float(seg.start), end=float(seg.end), text=text)
            )
        for w in seg.words or []:
            if w.word:
                words.append((float(w.start), float(w.end), w.word))

    segments = build_sentence_segments(words) if words else fallback

    detected = info.language or (language or "unknown")
    log.success(f"{len(segments)} sentence segments, source language = {detected}")
    return segments, detected
