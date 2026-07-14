"""Small ffmpeg helpers shared by the sync and assemble stages.

We depend on the ``ffmpeg`` binary (already required by yt-dlp for muxing) rather than
on an extra Python DSP package, so the tool stays light and portable.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def ensure_ffmpeg() -> str:
    """Return the ffmpeg executable path or raise a clear, actionable error."""
    exe = shutil.which("ffmpeg")
    if not exe:
        raise RuntimeError(
            "ffmpeg not found on PATH. Install it (e.g. `sudo apt install ffmpeg`, "
            "`brew install ffmpeg`, or from https://ffmpeg.org/download.html)."
        )
    return exe


def _run(args: list[str]) -> None:
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed ({' '.join(args[:6])} ...):\n{proc.stderr[-2000:]}")


def _atempo_chain(factor: float) -> list[str]:
    """ffmpeg's atempo filter only accepts 0.5–2.0; chain factors for larger changes.

    ``factor`` > 1 speeds up (shorter output); < 1 slows down (longer output).
    Pitch is preserved, which is exactly what we want for dubbing.
    """
    factor = max(0.25, min(4.0, factor))
    stages: list[float] = []
    remaining = factor
    while remaining > 2.0:
        stages.append(2.0)
        remaining /= 2.0
    while remaining < 0.5:
        stages.append(0.5)
        remaining /= 0.5
    stages.append(remaining)
    return ["atempo=" + ",atempo=".join(f"{s:.6f}" for s in stages)]


def time_stretch(src: Path, dst: Path, factor: float) -> Path:
    """Change tempo by ``factor`` (pitch-preserving) via ffmpeg atempo. factor 1.0 = copy."""
    ensure_ffmpeg()
    if abs(factor - 1.0) < 1e-3:
        shutil.copyfile(src, dst)
        return dst
    _run([
        "ffmpeg", "-y", "-i", str(src),
        "-filter:a", *_atempo_chain(factor),
        "-ar", "24000", str(dst),
    ])
    return dst


def mux_audio(video: Path, audio: Path, out: Path, *, reencode_video: bool = False) -> Path:
    """Replace the video's audio track with ``audio``, producing a share-ready MP4.

    The output is tuned for messaging apps (WhatsApp/Telegram): AAC audio and
    ``+faststart`` so the file starts playing before it is fully downloaded. By default
    the video stream is copied (fast, lossless); set ``reencode_video`` to force a
    broadly-compatible H.264 (yuv420p) re-encode when the source codec is exotic.
    """
    ensure_ffmpeg()
    out.parent.mkdir(parents=True, exist_ok=True)
    video_args = (
        ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "23"]
        if reencode_video
        else ["-c:v", "copy"]
    )
    _run([
        "ffmpeg", "-y",
        "-i", str(video),
        "-i", str(audio),
        "-map", "0:v:0", "-map", "1:a:0",
        *video_args,
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest", str(out),
    ])
    return out
