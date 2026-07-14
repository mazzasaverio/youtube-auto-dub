"""Argos Translate backend — offline, CPU, free.

Argos ships small CTranslate2 models per language pair. On first use for a given
``source -> target`` pair we download and install that pair automatically (a few tens
of MB), then everything runs locally with no network and no API keys.
"""

from __future__ import annotations

from ytdub.logging import stage_logger

log = stage_logger("translate")


class ArgosTranslator:
    def __init__(self) -> None:
        self._installed: set[tuple[str, str]] = set()

    def _ensure_pair(self, source_lang: str, target_lang: str) -> None:
        """Install the ``source -> target`` package on demand (once per pair)."""
        pair = (source_lang, target_lang)
        if pair in self._installed:
            return

        import argostranslate.package as package
        import argostranslate.translate as translate

        installed_codes = {lang.code for lang in translate.get_installed_languages()}
        if source_lang in installed_codes and target_lang in installed_codes:
            self._installed.add(pair)
            return

        # The pair is not installed yet: refresh the index, find and install it.
        try:
            package.update_package_index()
        except Exception as exc:  # offline and not yet installed -> actionable error below
            log.warning(f"Could not refresh Argos package index: {exc}")

        available = {(p.from_code, p.to_code): p for p in package.get_available_packages()}
        pkg = available.get(pair)
        if pkg is None:
            raise RuntimeError(
                f"No Argos Translate package for {source_lang} -> {target_lang}. "
                "Consider the 'nllb' translator for broader language coverage."
            )
        log.info(f"Installing Argos package {source_lang}->{target_lang} (first run only)")
        package.install_from_path(pkg.download())
        self._installed.add(pair)

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if source_lang == target_lang or not text.strip():
            return text
        self._ensure_pair(source_lang, target_lang)
        import argostranslate.translate as translate

        return translate.translate(text, source_lang, target_lang)
