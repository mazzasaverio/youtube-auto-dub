"""NLLB-200 backend — higher-quality neural MT (optional, heavier).

Meta's NLLB-200 (distilled 600M) covers 200 languages and clearly beats Argos on
fluency, at the cost of pulling in transformers + torch. Enabled with
``pip install 'ytdub[nllb]'`` and ``--translator nllb``.

NLLB uses its own BCP-47-ish language codes (e.g. ``ita_Latn``), so we map the common
ISO-639-1 codes the rest of the pipeline speaks onto them.
"""

from __future__ import annotations

from functools import lru_cache

from ytdub.config import detect_device
from ytdub.logging import stage_logger

log = stage_logger("translate")

_MODEL_NAME = "facebook/nllb-200-distilled-600M"

# Minimal ISO-639-1 -> NLLB code map (extend as needed).
_NLLB_CODES = {
    "en": "eng_Latn", "it": "ita_Latn", "es": "spa_Latn", "fr": "fra_Latn",
    "de": "deu_Latn", "pt": "por_Latn", "nl": "nld_Latn", "ru": "rus_Cyrl",
    "zh": "zho_Hans", "ja": "jpn_Jpan", "ko": "kor_Hang", "ar": "arb_Arab",
    "hi": "hin_Deva", "pl": "pol_Latn", "tr": "tur_Latn", "uk": "ukr_Cyrl",
}


def _nllb_code(lang: str) -> str:
    if lang in _NLLB_CODES:
        return _NLLB_CODES[lang]
    if "_" in lang:  # already an NLLB code
        return lang
    raise ValueError(f"Unsupported NLLB language code: {lang!r}")


class NllbTranslator:
    @staticmethod
    @lru_cache(maxsize=1)
    def _load():
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        device = detect_device()
        log.info(f"Loading NLLB-200 (distilled 600M) on {device}")
        tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(_MODEL_NAME)
        # mps/cuda if available; transformers handles cpu by default.
        if device in ("cuda", "mps"):
            model = model.to(device)
        return tokenizer, model, device

    def translate(
        self, text: str, source_lang: str, target_lang: str, max_chars: int | None = None
    ) -> str:
        if source_lang == target_lang or not text.strip():
            return text
        tokenizer, model, device = self._load()
        tokenizer.src_lang = _nllb_code(source_lang)
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        if device in ("cuda", "mps"):
            inputs = {k: v.to(device) for k, v in inputs.items()}
        bos = tokenizer.convert_tokens_to_ids(_nllb_code(target_lang))

        # Anti-hallucination: on short/odd fragments NLLB tends to run off and invent
        # boilerplate. Cap output length to ~2x the input and discourage repetition.
        input_len = int(inputs["input_ids"].shape[1])
        base = dict(
            forced_bos_token_id=bos,
            max_new_tokens=min(400, input_len * 2 + 16),
            no_repeat_ngram_size=3,
        )

        if not max_chars:
            generated = model.generate(**inputs, **base, num_beams=5)
            return tokenizer.batch_decode(generated, skip_special_tokens=True)[0]

        # Length-aware: return several beam candidates (varied phrasings/lengths) and
        # pick the fullest rendering that fits the time budget, else the shortest to
        # minimise the speed-up the sync stage would otherwise apply. Plain beam search
        # (no group/diverse beams) avoids transformers' trust_remote_code requirement.
        generated = model.generate(
            **inputs, **base, num_beams=6, num_return_sequences=6,
        )
        cands = [c.strip() for c in tokenizer.batch_decode(generated, skip_special_tokens=True)]
        cands = list(dict.fromkeys(c for c in cands if c))  # dedup, keep order
        if not cands:
            return text
        under = [c for c in cands if len(c) <= max_chars]
        return max(under, key=len) if under else min(cands, key=len)
