"""Chatterbox Multilingual backend (Resemble AI) — MIT, modern, high fidelity.

A cleaner, higher-quality alternative to XTTS/OpenVoice: MIT-licensed, ``pip install
chatterbox-tts`` with no legacy dependency pins, 23 languages, zero-shot cloning, and an
emotion-exaggeration control. In 2026 blind tests it clones more naturally than XTTS-v2.

Enabled with ``pip install 'ytdub[chatterbox]'`` and ``--tts chatterbox``.
"""

from __future__ import annotations

from pathlib import Path

from ytdub.logging import stage_logger

log = stage_logger("tts")

# Chatterbox Multilingual language ids (ISO-639-1) — the ones we map targets to.
_SUPPORTED = {
    "ar", "da", "de", "el", "en", "es", "fi", "fr", "he", "hi", "it", "ja",
    "ko", "ms", "nl", "no", "pl", "pt", "ru", "sv", "sw", "tr", "zh",
}


class ChatterboxBackend:
    def __init__(self, device: str = "cpu", exaggeration: float = 0.5) -> None:
        self.device = "cuda" if device == "cuda" else "cpu"
        self.exaggeration = exaggeration
        self._model = None

    def _get_model(self):
        if self._model is None:
            import torch
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS  # lazy

            log.info(f"Loading Chatterbox Multilingual on {self.device} (first run downloads weights)")
            if self.device == "cpu" and not torch.cuda.is_available():
                # Some chatterbox-tts builds torch.load a CUDA-saved tensor without a
                # map_location; force CPU so it loads on a GPU-less machine.
                _orig = torch.load
                torch.load = lambda *a, **k: _orig(*a, **{**k, "map_location": "cpu"})
                try:
                    self._model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
                finally:
                    torch.load = _orig
            else:
                self._model = ChatterboxMultilingualTTS.from_pretrained(device=self.device)
        return self._model

    def synthesize(self, text: str, speaker_wav: Path, language: str, out_path: Path) -> Path:
        if language not in _SUPPORTED:
            raise ValueError(
                f"Chatterbox does not support language {language!r}. Supported: {sorted(_SUPPORTED)}"
            )
        import torchaudio as ta

        model = self._get_model()
        wav = model.generate(
            text,
            language_id=language,
            audio_prompt_path=str(speaker_wav),
            exaggeration=self.exaggeration,
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        ta.save(str(out_path), wav, model.sr)
        return out_path
