"""OpenVoice v2 backend (fully MIT-licensed alternative).

Pipeline, per segment:
  1. MeloTTS synthesizes the target-language text in a neutral base voice.
  2. A tone-color embedding (SE) is extracted from the original speaker's reference.
  3. ToneColorConverter transfers that timbre onto the synthesized speech.

This is the modern successor to the OpenVoice v1 path the original repo vendored, and
it keeps the whole stack under permissive MIT licensing.

Setup (see README): ``pip install 'ytdub[openvoice]'``, download the OpenVoice v2
checkpoints, and point ``YTDUB_OPENVOICE_CKPT`` at the ``checkpoints_v2`` directory.
"""

from __future__ import annotations

import os
from pathlib import Path

from ytdub.logging import stage_logger

log = stage_logger("tts")

# ISO-639-1 -> (MeloTTS language code, base-speaker SE filename in .../base_speakers/ses/)
_LANG_MAP = {
    "en": ("EN", "en-default.pth"),
    "es": ("ES", "es.pth"),
    "fr": ("FR", "fr.pth"),
    "zh": ("ZH", "zh.pth"),
    "ja": ("JP", "jp.pth"),
    "ko": ("KR", "kr.pth"),
}


class OpenVoiceV2Backend:
    def __init__(self, device: str = "cpu") -> None:
        self.device = device
        ckpt = os.getenv("YTDUB_OPENVOICE_CKPT", "checkpoints/checkpoints_v2")
        self.ckpt_dir = Path(ckpt).resolve()
        self._converter = None
        self._melo: dict[str, object] = {}

    def _get_converter(self):
        if self._converter is None:
            from openvoice.api import ToneColorConverter  # lazy

            cfg = self.ckpt_dir / "converter" / "config.json"
            ckpt = self.ckpt_dir / "converter" / "checkpoint.pth"
            if not cfg.exists() or not ckpt.exists():
                raise FileNotFoundError(
                    f"OpenVoice v2 converter checkpoints not found under {self.ckpt_dir}. "
                    "Download checkpoints_v2 and set YTDUB_OPENVOICE_CKPT (see README)."
                )
            log.info("Loading OpenVoice v2 ToneColorConverter")
            conv = ToneColorConverter(str(cfg), device=self.device)
            conv.load_ckpt(str(ckpt))
            self._converter = conv
        return self._converter

    def _get_melo(self, melo_lang: str):
        if melo_lang not in self._melo:
            from melo.api import TTS as MeloTTS  # lazy

            log.info(f"Loading MeloTTS base speaker ({melo_lang})")
            self._melo[melo_lang] = MeloTTS(language=melo_lang, device=self.device)
        return self._melo[melo_lang]

    def synthesize(self, text: str, speaker_wav: Path, language: str, out_path: Path) -> Path:
        import torch
        from openvoice import se_extractor

        if language not in _LANG_MAP:
            raise ValueError(
                f"OpenVoice v2 backend supports {sorted(_LANG_MAP)}; got {language!r}"
            )
        melo_lang, source_se_file = _LANG_MAP[language]
        out_path.parent.mkdir(parents=True, exist_ok=True)

        converter = self._get_converter()
        melo = self._get_melo(melo_lang)

        # 1. Base-voice synthesis with MeloTTS (first available speaker for the language).
        speaker_id = next(iter(melo.hps.data.spk2id.values()))
        tmp_wav = out_path.with_suffix(".base.wav")
        melo.tts_to_file(text, speaker_id, str(tmp_wav), speed=1.0)

        # 2. Source SE (base speaker) + target SE (original speaker reference).
        source_se = torch.load(
            self.ckpt_dir / "base_speakers" / "ses" / source_se_file,
            map_location=self.device,
        )
        target_se, _ = se_extractor.get_se(
            str(speaker_wav), converter, target_dir=str(out_path.parent), vad=True
        )

        # 3. Timbre transfer -> final clip.
        converter.convert(
            audio_src_path=str(tmp_wav),
            src_se=source_se,
            tgt_se=target_se,
            output_path=str(out_path),
            message="@ytdub",
        )
        tmp_wav.unlink(missing_ok=True)
        return out_path
