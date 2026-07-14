"""Text-to-speech / voice-cloning interface + factory.

The backend's job: synthesize *target-language* text in the *original speaker's* voice,
given a short reference clip of that speaker. Backends are swappable:

  * ``xtts``      — Coqui XTTS-v2. One pip install, multilingual, CPU-capable. Default.
  * ``openvoice`` — OpenVoice v2 (MeloTTS + tone-color converter). Fully MIT-licensed.

Keeping this behind a Protocol means the rest of the pipeline never cares which model
is producing the audio — you can A/B them with a single ``--tts`` flag.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ytdub.logging import stage_logger
from ytdub.models import Segment

log = stage_logger("tts")


class TTSBackend(Protocol):
    def synthesize(
        self, text: str, speaker_wav: Path, language: str, out_path: Path
    ) -> Path: ...


def get_tts(name: str, device: str) -> TTSBackend:
    name = name.lower()
    if name == "xtts":
        from ytdub.stages.tts.xtts import XttsBackend

        return XttsBackend(device=device)
    if name == "openvoice":
        from ytdub.stages.tts.openvoice_v2 import OpenVoiceV2Backend

        return OpenVoiceV2Backend(device=device)
    if name == "chatterbox":
        from ytdub.stages.tts.chatterbox import ChatterboxBackend

        return ChatterboxBackend(device=device)
    raise ValueError(
        f"Unknown TTS backend: {name!r} (expected 'xtts', 'chatterbox' or 'openvoice')"
    )


def synthesize_segments(
    segments: list[Segment],
    tts: TTSBackend,
    *,
    speaker_wavs: dict[str | None, Path],
    language: str,
    out_dir: Path,
) -> list[Segment]:
    """Synthesize a per-segment audio clip in the cloned voice of the segment's speaker.

    ``speaker_wavs`` maps a speaker label to its reference clip; ``None`` is the default
    voice used for unlabeled segments (single-voice mode has just ``{None: clip}``).

    Returns new segments with ``.audio_path`` set. Segments whose synthesis fails are
    logged and left without audio (the sync stage will treat them as silence).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    default_wav = speaker_wavs.get(None) or next(iter(speaker_wavs.values()))
    out: list[Segment] = []
    for seg in segments:
        text = seg.translated or seg.text
        speaker_wav = speaker_wavs.get(seg.speaker, default_wav)
        clip = out_dir / f"seg_{seg.index:04d}.wav"
        try:
            tts.synthesize(text, speaker_wav, language, clip)
            out.append(seg.with_audio(clip))
        except Exception as exc:
            log.error(f"TTS failed for segment {seg.index} ({text[:40]!r}): {exc}")
            out.append(seg)
    log.success(f"Synthesized {sum(s.audio_path is not None for s in out)}/{len(out)} segments")
    return out
