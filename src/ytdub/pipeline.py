"""End-to-end orchestration: URL in, dubbed MP4 out.

    download -> transcribe -> translate -> build reference -> synthesize
             -> synchronize -> assemble

Every stage is imported lazily inside :func:`dub` so that importing this module (and
running ``ytdub --help``) never pulls in torch or a TTS engine.
"""

from __future__ import annotations

from pathlib import Path

from ytdub.config import Settings
from ytdub.logging import stage_logger
from ytdub.models import DubResult, Segment

log = stage_logger("pipeline")


def build_reference_clips(
    source_audio: Path,
    segments: list[Segment],
    out_dir: Path,
    max_seconds: float = 20.0,
) -> dict[str | None, Path]:
    """Build one clean voice reference per speaker for cloning.

    Segments are grouped by ``.speaker`` (all ``None`` in single-voice mode), and each
    speaker's own speech spans are concatenated — using real speech rather than a blind
    head crop keeps intro music/silence out of the timbre reference. Returns a mapping
    ``speaker -> reference.wav``.
    """
    from pydub import AudioSegment

    audio = AudioSegment.from_file(source_audio)
    out_dir.mkdir(parents=True, exist_ok=True)

    by_speaker: dict[str | None, AudioSegment] = {}
    for seg in segments:
        ref = by_speaker.setdefault(seg.speaker, AudioSegment.empty())
        if len(ref) >= max_seconds * 1000:
            continue
        by_speaker[seg.speaker] = ref + audio[int(seg.start * 1000) : int(seg.end * 1000)]

    clips: dict[str | None, Path] = {}
    for speaker, ref in by_speaker.items():
        if len(ref) == 0:  # fallback: head crop
            ref = audio[: int(max_seconds * 1000)]
        name = "reference.wav" if speaker is None else f"reference_{speaker}.wav"
        path = out_dir / name
        ref[: int(max_seconds * 1000)].export(path, format="wav")
        clips[speaker] = path
    return clips


def dub(url: str, settings: Settings | None = None) -> DubResult:
    """Run the full dubbing pipeline for a single YouTube URL."""
    settings = settings or Settings()

    from ytdub.stages import assemble, download, synchronize, transcribe
    from ytdub.stages.translate import get_translator, translate_segments
    from ytdub.stages.tts import get_tts, synthesize_segments

    log.info(f"Device={settings.device} | translator={settings.translator} | tts={settings.tts_backend}")

    # 1. Download video + normalized audio.
    dl = download.download(
        url,
        settings.downloads_dir,
        cookies_from_browser=settings.cookies_from_browser,
        cookies_file=settings.cookies_file,
    )
    work = settings.work_dir / dl.video_id
    work.mkdir(parents=True, exist_ok=True)

    # 2. Transcribe with word-level timing.
    segments, source_lang = transcribe.transcribe(
        dl.audio_path,
        model_size=settings.asr_model,
        device=settings.device,
        compute_type=settings.compute_type(),
        language=settings.source_lang,
    )
    if not segments:
        raise RuntimeError("Transcription produced no speech segments.")

    # 2b. Optional diarization -> tag each segment with a speaker (multi-voice).
    if settings.diarize:
        from ytdub.stages.diarize import assign_speakers, diarize as run_diarize

        turns = run_diarize(dl.audio_path, device=settings.device, hf_token=settings.hf_token)
        segments = assign_speakers(segments, turns)
        n = len({s.speaker for s in segments})
        log.success(f"Diarization: {n} distinct voice(s) will be cloned")

    # 3. Translate segment by segment.
    target = settings.target_lang
    if source_lang != target:
        translator = get_translator(settings.translator)
        segments = translate_segments(segments, translator, source_lang, target)
        log.success(f"Translated {len(segments)} segments {source_lang}->{target}")
    else:
        segments = [s.with_translation(s.text) for s in segments]
        log.info("Source language equals target; skipping translation.")

    # 4. One voice reference per speaker (a single default voice without diarization).
    references = build_reference_clips(dl.audio_path, segments, work / "refs")

    # 5. Synthesize each segment in its speaker's cloned voice.
    tts = get_tts(settings.tts_backend, settings.device)
    segments = synthesize_segments(
        segments, tts, speaker_wavs=references, language=target, out_dir=work / "clips"
    )

    # 6. Duration alignment -> single full-length track.
    dubbed_audio = synchronize.align(
        segments,
        out_path=work / "dubbed.wav",
        total_duration=dl.duration,
        max_speedup=settings.max_speedup,
        max_slowdown=settings.max_slowdown,
        work_dir=work / "aligned",
    )

    # 7. Mux onto the original video.
    out_path = settings.output_dir / f"{dl.video_id}.{target}.mp4"
    assemble.assemble(
        dl.video_path, dubbed_audio, out_path, reencode_video=settings.reencode_video
    )

    log.success(f"Done: {out_path}")
    return DubResult(
        video_id=dl.video_id,
        output_path=out_path,
        segments=segments,
        source_lang=source_lang,
        target_lang=target,
    )
