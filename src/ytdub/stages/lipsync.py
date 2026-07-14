"""Lip-sync stage — make the on-screen mouth match the dubbed audio (optional).

Backend: **Wav2Lip** (open-source, https://github.com/Rudrabha/Wav2Lip). Given the
original video and our dubbed audio track, Wav2Lip re-renders the speaker's mouth to
match the new speech, so the dub no longer looks out of sync with the lips.

Why a subprocess instead of an in-process import? Wav2Lip pins an old ``librosa`` that
directly conflicts with the one coqui-tts needs, so the two cannot share a virtualenv.
We therefore drive Wav2Lip's ``inference.py`` in **its own environment** via subprocess.

Setup (see README):
  * clone Wav2Lip and create its venv,
  * download the ``wav2lip_gan.pth`` checkpoint,
  * point env vars at them:
      YTDUB_WAV2LIP_DIR=/path/to/Wav2Lip
      YTDUB_WAV2LIP_CKPT=/path/to/wav2lip_gan.pth
      YTDUB_WAV2LIP_PYTHON=/path/to/Wav2Lip/.venv/bin/python   # optional
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from ytdub.logging import stage_logger

log = stage_logger("lipsync")


def build_wav2lip_cmd(
    python: str, wav2lip_dir: Path, checkpoint: Path, face: Path, audio: Path, out: Path
) -> list[str]:
    """Construct the Wav2Lip ``inference.py`` command line (pure — unit-tested)."""
    return [
        python,
        str(wav2lip_dir / "inference.py"),
        "--checkpoint_path", str(checkpoint),
        "--face", str(face),
        "--audio", str(audio),
        "--outfile", str(out),
    ]


def _resolve_paths() -> tuple[str, Path, Path]:
    wav2lip_dir = os.getenv("YTDUB_WAV2LIP_DIR")
    checkpoint = os.getenv("YTDUB_WAV2LIP_CKPT")
    python = os.getenv("YTDUB_WAV2LIP_PYTHON") or sys.executable
    if not wav2lip_dir or not checkpoint:
        raise RuntimeError(
            "Lip-sync needs Wav2Lip. Set YTDUB_WAV2LIP_DIR and YTDUB_WAV2LIP_CKPT "
            "(and optionally YTDUB_WAV2LIP_PYTHON). See the README 'Lip-sync' section."
        )
    d, c = Path(wav2lip_dir), Path(checkpoint)
    if not (d / "inference.py").exists():
        raise FileNotFoundError(f"{d/'inference.py'} not found — is YTDUB_WAV2LIP_DIR correct?")
    if not c.exists():
        raise FileNotFoundError(f"Wav2Lip checkpoint not found: {c}")
    return python, d, c


def lipsync(video: Path, audio: Path, out_path: Path) -> Path:
    """Run Wav2Lip on ``(video, audio)`` and return the lip-synced video path.

    The output already carries the dubbed audio; the caller may still remux it for
    ``+faststart``. Raises with an actionable message if Wav2Lip isn't configured.
    """
    python, wav2lip_dir, checkpoint = _resolve_paths()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = build_wav2lip_cmd(python, wav2lip_dir, checkpoint, video, audio, out_path)
    log.info("Running Wav2Lip (this is slow on CPU; a GPU is strongly recommended)")
    proc = subprocess.run(cmd, cwd=str(wav2lip_dir), capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Wav2Lip failed:\n{proc.stderr[-2000:]}")
    if not out_path.exists():
        raise RuntimeError("Wav2Lip reported success but produced no output file.")
    log.success(f"Lip-synced video -> {out_path.name}")
    return out_path
