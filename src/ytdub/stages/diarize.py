"""Diarization stage — *who* speaks *when* (optional, for multi-voice dubbing).

When enabled, we run speaker diarization on the source audio, tag every transcribed
segment with a speaker label, and later clone one voice per speaker. This is what makes
a multi-speaker video come out dubbed in *multiple* voices instead of one.

Diarization is **opt-in** (``--diarize``) because the default backend, pyannote, needs a
free Hugging Face token and a one-time model-terms acceptance — friction we keep out of
the zero-config path. With it off, the whole video is cloned in a single dominant voice.

The overlap-matching (:func:`assign_speakers`) is pure and unit-tested; only the
:func:`diarize` model call needs the heavy dependency.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from ytdub.logging import stage_logger
from ytdub.models import Segment

log = stage_logger("diarize")


@dataclass
class SpeakerTurn:
    start: float
    end: float
    speaker: str


def assign_speakers(segments: list[Segment], turns: list[SpeakerTurn]) -> list[Segment]:
    """Tag each segment with the speaker whose turns overlap it most.

    Pure function: given transcription segments and diarization turns (both on the same
    timeline, in seconds), return new segments with ``.speaker`` set. A segment with no
    overlap falls back to the nearest turn's speaker, so nothing is left unlabeled.
    """
    if not turns:
        return segments

    out: list[Segment] = []
    for seg in segments:
        best_speaker: str | None = None
        best_overlap = 0.0
        for turn in turns:
            overlap = min(seg.end, turn.end) - max(seg.start, turn.start)
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = turn.speaker

        if best_speaker is None:  # no overlap -> nearest turn by midpoint distance
            mid = (seg.start + seg.end) / 2
            best_speaker = min(
                turns, key=lambda t: abs((t.start + t.end) / 2 - mid)
            ).speaker

        out.append(
            Segment(
                index=seg.index,
                start=seg.start,
                end=seg.end,
                text=seg.text,
                translated=seg.translated,
                audio_path=seg.audio_path,
                speaker=best_speaker,
            )
        )
    return out


def diarize(audio_path: Path, *, device: str = "cpu", hf_token: str | None = None) -> list[SpeakerTurn]:
    """Run pyannote speaker diarization and return the speaker turns.

    Requires ``pip install 'ytdub[diarize]'`` and a Hugging Face token (env ``HF_TOKEN``)
    after accepting the model terms at hf.co/pyannote/speaker-diarization-3.1.
    """
    from pyannote.audio import Pipeline  # lazy, heavy

    token = hf_token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        raise RuntimeError(
            "Diarization needs a Hugging Face token. Accept the terms at "
            "hf.co/pyannote/speaker-diarization-3.1 and set HF_TOKEN."
        )

    log.info("Loading pyannote speaker-diarization-3.1")
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1", use_auth_token=token
    )
    if device in ("cuda", "mps"):
        import torch

        pipeline.to(torch.device(device))

    diarization = pipeline(str(audio_path))
    turns = [
        SpeakerTurn(start=float(turn.start), end=float(turn.end), speaker=str(speaker))
        for turn, _, speaker in diarization.itertracks(yield_label=True)
    ]
    n_speakers = len({t.speaker for t in turns})
    log.success(f"{len(turns)} turns across {n_speakers} speaker(s)")
    return turns
