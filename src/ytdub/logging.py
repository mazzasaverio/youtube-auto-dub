"""Thin loguru wrapper so every module logs consistently."""

from __future__ import annotations

import sys

from loguru import logger

_configured = False


def setup_logging(level: str = "INFO") -> None:
    """Configure a single, human-friendly stderr sink. Idempotent."""
    global _configured
    if _configured:
        return
    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        format=(
            "<green>{time:HH:mm:ss}</green> | <level>{level: <7}</level> | "
            "<cyan>{extra[stage]}</cyan> | {message}"
        ),
        filter=lambda record: record["extra"].setdefault("stage", "-") or True,
    )
    _configured = True


def stage_logger(stage: str):
    """Return a logger bound to a pipeline stage name (shown in every line)."""
    setup_logging()
    return logger.bind(stage=stage)
