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


def build_reference_clip(
    source_audio: Path, segments: list[Segment], out_path: Path, max_seconds: float = 20.0
) -> Path:
    """Concatenate the first voiced segments into a clean reference for voice cloning.

    Using actual speech spans (rather than a blind head crop) keeps intro music or
    silence out of the timbre reference the cloning model sees.
    """
    from pydub import AudioSegment

    audio = AudioSegment.from_file(source_audio)
    ref = AudioSegment.empty()
    for seg in segments:
        ref += audio[int(seg.start * 1000) : int(seg.end * 1000)]
        if len(ref) >= max_seconds * 1000:
            break
    if len(ref) == 0:  # fallback: head crop
        ref = audio[: int(max_seconds * 1000)]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ref[: int(max_seconds * 1000)].export(out_path, format="wav")
    return out_path


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

    # 3. Translate segment by segment.
    target = settings.target_lang
    if source_lang != target:
        translator = get_translator(settings.translator)
        segments = translate_segments(segments, translator, source_lang, target)
        log.success(f"Translated {len(segments)} segments {source_lang}->{target}")
    else:
        segments = [s.with_translation(s.text) for s in segments]
        log.info("Source language equals target; skipping translation.")

    # 4. Reference clip for voice cloning.
    reference = build_reference_clip(dl.audio_path, segments, work / "reference.wav")

    # 5. Synthesize each segment in the cloned voice.
    tts = get_tts(settings.tts_backend, settings.device)
    segments = synthesize_segments(
        segments, tts, speaker_wav=reference, language=target, out_dir=work / "clips"
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
