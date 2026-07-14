"""Translated-subtitle (.srt) output.

A dubbed video is more useful with a matching subtitle track: it lets the viewer follow
along, and it's an easy way to eyeball translation quality. We emit an SRT built from the
translated segments, on the original video timeline.
"""

from __future__ import annotations

from pathlib import Path

from ytdub.models import Segment


def _timestamp(seconds: float) -> str:
    """Format seconds as an SRT timestamp ``HH:MM:SS,mmm``."""
    if seconds < 0:
        seconds = 0.0
    millis = int(round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(segments: list[Segment], path: Path, *, translated: bool = True) -> Path:
    """Write ``segments`` to an SRT file. Uses the translation when available."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for i, seg in enumerate(segments, start=1):
        text = (seg.translated if translated else seg.text) or seg.text
        lines.append(str(i))
        lines.append(f"{_timestamp(seg.start)} --> {_timestamp(seg.end)}")
        lines.append(text.strip())
        lines.append("")  # blank separator
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
