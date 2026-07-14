"""Data model shared across pipeline stages.

A dub run is a sequence of :class:`Segment` objects that flow through the stages,
each stage enriching them (translation text, then a synthesized audio path). Keeping
one immutable-ish carrier makes the pipeline easy to reason about and to test.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path


@dataclass
class Segment:
    """A single timed speech span from the source video.

    Timestamps are in **seconds** and refer to the original video timeline, which is
    what lets us re-align the dubbed audio later.
    """

    index: int
    start: float
    end: float
    text: str  # source-language text
    translated: str | None = None  # target-language text
    audio_path: Path | None = None  # synthesized (pre-sync) clip for this segment
    speaker: str | None = None  # diarization label (reserved for multi-voice support)

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)

    def with_translation(self, translated: str) -> "Segment":
        return replace(self, translated=translated)

    def with_audio(self, audio_path: Path) -> "Segment":
        return replace(self, audio_path=audio_path)


@dataclass
class DownloadResult:
    video_id: str
    title: str
    video_path: Path
    audio_path: Path
    duration: float


@dataclass
class DubResult:
    """Final output of a dub run."""

    video_id: str
    output_path: Path
    segments: list[Segment] = field(default_factory=list)
    source_lang: str = ""
    target_lang: str = ""
    subtitle_path: Path | None = None
