"""Synchronize stage — duration alignment. **The piece the original repo lacked.**

Different languages carry information at different densities, so a translated line is
rarely the same length as the original. Left alone (as in the old code, which glued one
big blob of TTS onto the video), the dub drifts out of sync within seconds.

Strategy — pragmatic, and the same one used by modern open-source dubbers:

  1. For each segment, compare the synthesized clip's duration to its original time
     window.
  2. If the clip is *too long*, speed it up (pitch-preserving ffmpeg atempo), capped at
     ``max_speedup`` so speech stays intelligible; beyond the cap we let it overflow
     rather than turn it into chipmunk audio.
  3. Optionally allow a small slow-down (down to ``max_slowdown``) when a clip is much
     shorter than its window, otherwise just leave a natural pause.
  4. Lay every aligned clip onto a single silent timeline at its *original* start time.

The result is a full-length audio track locked to the source video's timing.
"""

from __future__ import annotations

from pathlib import Path

from ytdub.ffmpeg import time_stretch
from ytdub.logging import stage_logger
from ytdub.models import Segment

log = stage_logger("sync")


def _trim_silence(seg, silence_thresh_db: float = -40.0):
    """Strip leading/trailing silence so a clip's speech starts right at its slot.

    Loose TTS clips often carry ~100-300 ms of leading silence; trimming it tightens
    onset alignment with the original video.
    """
    from pydub.silence import detect_leading_silence

    lead = detect_leading_silence(seg, silence_threshold=silence_thresh_db)
    trail = detect_leading_silence(seg.reverse(), silence_threshold=silence_thresh_db)
    end = len(seg) - trail
    return seg[lead:end] if end > lead else seg


def align(
    segments: list[Segment],
    *,
    out_path: Path,
    total_duration: float,
    max_speedup: float = 1.4,
    max_slowdown: float = 0.85,
    work_dir: Path,
) -> Path:
    """Build one time-aligned dubbed WAV covering the whole video.

    ``total_duration`` is the source video length (seconds); the output is at least that
    long so the mux keeps the tail of the video even if speech ends earlier.
    """
    from pydub import AudioSegment

    work_dir.mkdir(parents=True, exist_ok=True)

    voiced = [s for s in segments if s.audio_path is not None]
    if not voiced:
        raise RuntimeError("No synthesized segments to synchronize.")

    # Timeline must span the whole video AND any clip that overflows past the end.
    timeline_end = max(total_duration, max(s.end for s in voiced))
    timeline = AudioSegment.silent(duration=int(timeline_end * 1000) + 200)

    stretched_total = 0.0
    for seg in voiced:
        window = seg.duration

        # Trim leading/trailing silence so speech starts exactly at the segment slot.
        trimmed = _trim_silence(AudioSegment.from_file(seg.audio_path))
        trimmed_path = work_dir / f"trim_{seg.index:04d}.wav"
        trimmed.export(trimmed_path, format="wav")
        clip_dur = len(trimmed) / 1000.0

        factor = 1.0
        if window > 0.05 and clip_dur > window:
            # Too long -> speed up, capped.
            factor = min(clip_dur / window, max_speedup)
        elif window > 0.05 and clip_dur < window * max_slowdown:
            # Much too short -> gently slow down toward the window (never below cap).
            factor = max(clip_dur / window, max_slowdown)

        if abs(factor - 1.0) > 1e-3:
            aligned = work_dir / f"aligned_{seg.index:04d}.wav"
            time_stretch(trimmed_path, aligned, factor)
            stretched_total += 1
        else:
            aligned = trimmed_path

        clip = AudioSegment.from_file(aligned)
        timeline = timeline.overlay(clip, position=int(seg.start * 1000))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    timeline.export(out_path, format="wav")
    log.success(
        f"Aligned {len(voiced)} segments ({stretched_total} time-stretched) "
        f"-> {out_path.name} ({timeline_end:.0f}s)"
    )
    return out_path
