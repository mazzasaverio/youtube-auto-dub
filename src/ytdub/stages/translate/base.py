"""Translator interface + factory.

Translation is pluggable so users can trade convenience for quality without touching
the pipeline:

  * ``argos`` — Argos Translate. Fully offline, CPU, tiny models, one pip install.
    The default: it keeps the "runs on any PC, for free" promise.
  * ``nllb``  — Meta NLLB-200 via transformers. Higher quality, heavier (pulls torch).

Both translate **segment by segment**, preserving the timing structure — unlike the
old code, which flattened the whole transcript into a single blob before translating.
"""

from __future__ import annotations

from typing import Protocol

from ytdub.models import Segment


class Translator(Protocol):
    """Translate source-language text into the target language.

    ``max_chars`` is an optional *soft* length budget: backends that can produce several
    candidates (e.g. NLLB) use it to prefer a rendering that fits the segment's time
    window, which reduces how much the dub has to be sped up. Backends that can't just
    ignore it.
    """

    def translate(
        self, text: str, source_lang: str, target_lang: str, max_chars: int | None = None
    ) -> str: ...


def get_translator(name: str) -> Translator:
    """Instantiate a translator backend by name."""
    name = name.lower()
    if name == "argos":
        from ytdub.stages.translate.argos import ArgosTranslator

        return ArgosTranslator()
    if name == "nllb":
        from ytdub.stages.translate.nllb import NllbTranslator

        return NllbTranslator()
    raise ValueError(f"Unknown translator backend: {name!r} (expected 'argos' or 'nllb')")


def translate_segments(
    segments: list[Segment],
    translator: Translator,
    source_lang: str,
    target_lang: str,
    *,
    chars_per_sec: float | None = None,
    max_speedup: float = 1.4,
) -> list[Segment]:
    """Translate each segment's text, returning new segments with ``.translated`` set.

    When ``chars_per_sec`` is given, each segment gets a length budget derived from its
    time window (``duration * chars_per_sec * max_speedup``) so the translator can favour
    a rendering that fits — this is what tightens the dub's rhythm. Empty translations
    fall back to the source text so a segment is never silently dropped.
    """
    out: list[Segment] = []
    for seg in segments:
        budget = None
        if chars_per_sec:
            budget = max(20, int(seg.duration * chars_per_sec * max_speedup))
        translated = translator.translate(
            seg.text, source_lang, target_lang, max_chars=budget
        ).strip()
        out.append(seg.with_translation(translated or seg.text))
    return out
