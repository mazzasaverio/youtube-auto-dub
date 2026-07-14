"""Assemble stage — mux the aligned dub onto the original video.

Swaps the audio track only: the original video stream is stream-copied (no re-encode,
so it is fast and lossless) while the new audio is encoded to AAC.
"""

from __future__ import annotations

from pathlib import Path

from ytdub.ffmpeg import mux_audio
from ytdub.logging import stage_logger

log = stage_logger("assemble")


def assemble(
    video_path: Path, dubbed_audio: Path, out_path: Path, *, reencode_video: bool = False
) -> Path:
    log.info(f"Muxing dubbed audio onto {video_path.name}")
    result = mux_audio(video_path, dubbed_audio, out_path, reencode_video=reencode_video)
    log.success(f"Wrote {result}")
    return result
