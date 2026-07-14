"""Central configuration.

All tunables live here so the pipeline can be driven identically from the CLI, the
optional API, or a plain Python call. Defaults are chosen so the whole thing runs
**locally, for free, on a CPU-only laptop** — a GPU is picked up automatically when
present but is never required.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache(maxsize=1)
def detect_device() -> str:
    """Best available torch device, without importing torch at module import time.

    Returns one of ``"cuda"``, ``"mps"`` (Apple Silicon) or ``"cpu"``. Falls back to
    ``"cpu"`` if torch is not installed, so the light core keeps working.
    """
    try:
        import torch  # noqa: PLC0415 — deliberately lazy
    except Exception:
        return "cpu"
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def default_compute_type(device: str) -> str:
    """faster-whisper compute type matched to the device (quality vs. speed/VRAM)."""
    return "float16" if device == "cuda" else "int8"


class Settings(BaseSettings):
    """Runtime configuration, overridable via env vars (prefix ``YTDUB_``) or ``.env``."""

    model_config = SettingsConfigDict(
        env_prefix="YTDUB_", env_file=".env", extra="ignore"
    )

    # --- Filesystem layout ------------------------------------------------
    data_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("YTDUB_DATA_DIR", "data")).resolve()
    )

    # --- Languages --------------------------------------------------------
    # `source_lang` may be None -> auto-detected by the ASR model.
    source_lang: str | None = None
    target_lang: str = "en"

    # --- Download ---------------------------------------------------------
    # Pass browser cookies to yt-dlp when YouTube demands "confirm you're not a
    # bot" (common on datacenter/VPN IPs; usually unneeded on a home machine).
    cookies_from_browser: str | None = None  # e.g. "chrome", "firefox", "edge"
    cookies_file: Path | None = None

    # --- Compute ----------------------------------------------------------
    device: str = Field(default_factory=detect_device)

    # --- ASR (faster-whisper) --------------------------------------------
    # tiny/base/small/medium/large-v3 — "small" is a good CPU default.
    asr_model: str = "small"
    asr_compute_type: str | None = None  # None -> derived from device

    # --- Translation ------------------------------------------------------
    translator: str = "argos"  # "argos" (offline default) | "nllb"

    # --- TTS / voice cloning ---------------------------------------------
    tts_backend: str = "xtts"  # "xtts" (default) | "openvoice"

    # --- Diarization (multi-voice) ---------------------------------------
    # When True, detect speakers and clone one voice per speaker. Needs the
    # [diarize] extra and a Hugging Face token (env HF_TOKEN).
    diarize: bool = False
    hf_token: str | None = None

    # --- Synchronization --------------------------------------------------
    # Cap on how much a segment may be sped up / slowed down to fit its
    # original time window. Beyond this we let it overflow rather than make
    # speech unintelligible. 1.0 == no stretch.
    max_speedup: float = 1.4
    max_slowdown: float = 0.85

    # --- Lip-sync (optional, Wav2Lip via subprocess) ---------------------
    # Re-render the mouth to match the dubbed audio. Needs Wav2Lip configured via
    # YTDUB_WAV2LIP_DIR / YTDUB_WAV2LIP_CKPT (see README). GPU strongly recommended.
    lipsync: bool = False

    # --- Output -----------------------------------------------------------
    # Re-encode the video to broadly-compatible H.264 for messaging apps when the
    # source codec is exotic. Off by default (stream-copy is fast and lossless);
    # the mux always adds +faststart so the result plays fine on WhatsApp/Telegram.
    reencode_video: bool = False

    def compute_type(self) -> str:
        return self.asr_compute_type or default_compute_type(self.device)

    # Convenience sub-directory accessors -------------------------------
    def sub(self, name: str) -> Path:
        p = self.data_dir / name
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def downloads_dir(self) -> Path:
        return self.sub("downloads")

    @property
    def work_dir(self) -> Path:
        return self.sub("work")

    @property
    def output_dir(self) -> Path:
        return self.sub("output")
