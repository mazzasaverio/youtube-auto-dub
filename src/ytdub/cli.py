"""``ytdub`` command-line interface — the primary, comfortable way to run this locally.

    ytdub dub "https://youtu.be/VIDEO_ID" --target en
    ytdub dub "https://youtu.be/VIDEO_ID" --source it --target es --tts openvoice

The result is a share-ready MP4 (H.264 + AAC, faststart) under ``data/output/`` that you
can send straight over WhatsApp/Telegram.
"""

from __future__ import annotations

from pathlib import Path

import typer

from ytdub import __version__
from ytdub.config import Settings, detect_device
from ytdub.logging import setup_logging

app = typer.Typer(add_completion=False, help="Local-first open-source YouTube dubbing.")


@app.command()
def dub(
    url: str = typer.Argument(..., help="YouTube URL (watch, shorts or youtu.be)."),
    target: str = typer.Option("en", "--target", "-t", help="Target language (ISO-639-1)."),
    source: str | None = typer.Option(
        None, "--source", "-s", help="Source language; omit to auto-detect."
    ),
    tts: str = typer.Option("xtts", "--tts", help="TTS backend: 'xtts' or 'openvoice'."),
    translator: str = typer.Option(
        "argos", "--translator", help="Translator: 'argos' (offline) or 'nllb'."
    ),
    asr_model: str = typer.Option(
        "small", "--asr-model", help="Whisper size: tiny/base/small/medium/large-v3."
    ),
    data_dir: Path = typer.Option(
        Path("data"), "--data-dir", help="Where downloads/work/output live."
    ),
    reencode: bool = typer.Option(
        False, "--reencode", help="Force H.264 re-encode for max compatibility."
    ),
    cookies_from_browser: str | None = typer.Option(
        None,
        "--cookies-from-browser",
        help="Use a browser's cookies if YouTube asks to 'confirm you're not a bot' "
        "(e.g. chrome, firefox, edge).",
    ),
    cookies: Path | None = typer.Option(
        None, "--cookies", help="Path to a Netscape-format cookies.txt for yt-dlp."
    ),
    log_level: str = typer.Option("INFO", "--log-level", help="DEBUG/INFO/WARNING/ERROR."),
) -> None:
    """Download a video and produce a dubbed, share-ready copy in another language."""
    setup_logging(log_level)
    from ytdub.pipeline import dub as run_dub

    settings = Settings(
        data_dir=data_dir.resolve(),
        source_lang=source,
        target_lang=target,
        tts_backend=tts,
        translator=translator,
        asr_model=asr_model,
        reencode_video=reencode,
        cookies_from_browser=cookies_from_browser,
        cookies_file=cookies,
    )
    result = run_dub(url, settings)
    typer.secho(f"\n✅ Dubbed video: {result.output_path}", fg=typer.colors.GREEN, bold=True)


@app.command()
def info() -> None:
    """Print version and the auto-detected compute device."""
    typer.echo(f"ytdub {__version__}")
    typer.echo(f"device: {detect_device()}")


if __name__ == "__main__":
    app()
