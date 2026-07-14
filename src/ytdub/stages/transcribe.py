"""Transcribe stage — faster-whisper with word-level timestamps.

This is the piece the original repo was *missing*: instead of trusting YouTube's
(often absent or auto-generated) subtitles, we transcribe the actual audio and get
precise per-segment timing. That timing is the backbone of the later duration
alignment, so the dub tracks the picture instead of drifting.

faster-whisper runs on CTranslate2 (int8 on CPU), so it is fast and free on a laptop.
"""

from __future__ import annotations

from pathlib import Path

from ytdub.logging import stage_logger
from ytdub.models import Segment

log = stage_logger("transcribe")

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

    segments: list[Segment] = []
    for i, seg in enumerate(raw_segments):
        text = (seg.text or "").strip()
        if not text:
            continue
        segments.append(
            Segment(index=len(segments), start=float(seg.start), end=float(seg.end), text=text)
        )

    detected = info.language or (language or "unknown")
    log.success(f"{len(segments)} segments, source language = {detected}")
    return segments, detected
