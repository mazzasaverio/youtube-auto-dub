"""Unit tests that exercise the real glue without downloading any ML models.

The important one is ``test_align_*``: it drives the duration-alignment stage (the piece
the original repo lacked) end-to-end on synthetic audio, so we verify timing behaviour
without a GPU or gigabytes of checkpoints.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ytdub.ffmpeg import _atempo_chain
from ytdub.models import Segment
from ytdub.stages.download import extract_video_id


def test_extract_video_id_variants():
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://youtube.com/shorts/pcydlhq2MWI?si=x") == "pcydlhq2MWI"
    assert extract_video_id("not a url") is None


def test_atempo_chain_single_and_multi():
    # Within the 0.5–2.0 window -> a single atempo filter.
    assert _atempo_chain(1.4) == ["atempo=1.400000"]
    # Above 2.0 -> chained so each stage stays in range and the product == factor.
    chain = _atempo_chain(3.0)[0]
    factors = [float(x.split("=")[1]) for x in chain.split(",")]
    assert all(0.5 <= f <= 2.0 for f in factors)
    assert abs(_product(factors) - 3.0) < 1e-6


def _product(values):
    out = 1.0
    for v in values:
        out *= v
    return out


def _tone(duration_ms: int, path: Path, freq: int = 220):
    from pydub.generators import Sine

    Sine(freq).to_audio_segment(duration=duration_ms).export(path, format="wav")
    return path


def test_align_builds_full_length_timeline(tmp_path):
    """A too-long clip is compressed; a short clip leaves a pause; timeline spans video."""
    from pydub import AudioSegment

    from ytdub.stages.synchronize import align

    # Segment 0: window 1.0s but a 3.0s clip -> must be sped up (capped at 1.4x).
    clip0 = _tone(3000, tmp_path / "c0.wav")
    # Segment 1: window 2.0s but only a 0.5s clip -> placed at 5.0s, pause after.
    clip1 = _tone(500, tmp_path / "c1.wav")

    segments = [
        Segment(index=0, start=0.0, end=1.0, text="a", translated="a", audio_path=clip0),
        Segment(index=1, start=5.0, end=7.0, text="b", translated="b", audio_path=clip1),
    ]

    out = align(
        segments,
        out_path=tmp_path / "dubbed.wav",
        total_duration=10.0,
        max_speedup=1.4,
        max_slowdown=0.85,
        work_dir=tmp_path / "work",
    )
    assert out.exists()
    dubbed = AudioSegment.from_file(out)
    # Timeline must cover the whole 10s video (plus small padding).
    assert len(dubbed) >= 10_000


def test_assign_speakers_by_overlap():
    from ytdub.stages.diarize import SpeakerTurn, assign_speakers

    segments = [
        Segment(index=0, start=0.0, end=2.0, text="a"),   # inside SPK_A
        Segment(index=1, start=5.0, end=7.0, text="b"),   # inside SPK_B
        Segment(index=2, start=2.5, end=3.2, text="c"),   # gap -> nearest (SPK_A)
    ]
    turns = [
        SpeakerTurn(0.0, 2.2, "SPK_A"),
        SpeakerTurn(4.8, 7.5, "SPK_B"),
    ]
    tagged = assign_speakers(segments, turns)
    assert [s.speaker for s in tagged] == ["SPK_A", "SPK_B", "SPK_A"]


def test_assign_speakers_no_turns_is_noop():
    from ytdub.stages.diarize import assign_speakers

    segments = [Segment(index=0, start=0.0, end=1.0, text="a")]
    assert assign_speakers(segments, []) == segments


def test_align_raises_without_audio(tmp_path):
    from ytdub.stages.synchronize import align

    segments = [Segment(index=0, start=0.0, end=1.0, text="a", translated="a")]
    with pytest.raises(RuntimeError):
        align(
            segments,
            out_path=tmp_path / "x.wav",
            total_duration=1.0,
            work_dir=tmp_path / "w",
        )


def test_srt_timestamp_and_write(tmp_path):
    from ytdub.subtitles import _timestamp, write_srt

    assert _timestamp(0) == "00:00:00,000"
    assert _timestamp(3661.5) == "01:01:01,500"

    segments = [
        Segment(index=0, start=0.0, end=1.5, text="ciao", translated="hi"),
        Segment(index=1, start=2.0, end=3.25, text="mondo", translated="world"),
    ]
    out = write_srt(segments, tmp_path / "s.srt")
    content = out.read_text(encoding="utf-8")
    # Uses the translation, not the source text, and standard SRT arrow formatting.
    assert "hi" in content and "world" in content and "ciao" not in content
    assert "00:00:00,000 --> 00:00:01,500" in content
    assert content.startswith("1\n")
