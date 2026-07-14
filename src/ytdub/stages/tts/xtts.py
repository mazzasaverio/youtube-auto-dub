"""Coqui XTTS-v2 backend (default).

XTTS-v2 does zero-shot voice cloning *and* multilingual synthesis in a single model:
give it the target-language text plus a few seconds of the original speaker, and it
speaks that text in that voice. Installed via ``pip install 'ytdub[xtts]'`` (the
maintained ``coqui-tts`` fork) and runs on CPU (faster on GPU).

Supported languages (ISO-639-1): en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh,
hu, ko, ja, hi.
"""

from __future__ import annotations

from pathlib import Path

from ytdub.logging import stage_logger

log = stage_logger("tts")

_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
_SUPPORTED = {
    "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl",
    "cs", "ar", "zh", "hu", "ko", "ja", "hi",
}


class XttsBackend:
    def __init__(self, device: str = "cpu") -> None:
        # XTTS supports cpu/cuda; treat Apple mps as cpu (unsupported by Coqui).
        self.device = "cuda" if device == "cuda" else "cpu"
        self._tts = None

    def _model(self):
        if self._tts is None:
            from TTS.api import TTS  # lazy; provided by coqui-tts

            log.info(f"Loading XTTS-v2 on {self.device} (first run downloads ~1.8 GB)")
            self._tts = TTS(_MODEL_NAME).to(self.device)
        return self._tts

    def synthesize(self, text: str, speaker_wav: Path, language: str, out_path: Path) -> Path:
        if language not in _SUPPORTED:
            raise ValueError(
                f"XTTS-v2 does not support language {language!r}. "
                f"Supported: {sorted(_SUPPORTED)}"
            )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        self._model().tts_to_file(
            text=text,
            speaker_wav=str(speaker_wav),
            language=language,
            file_path=str(out_path),
        )
        return out_path
