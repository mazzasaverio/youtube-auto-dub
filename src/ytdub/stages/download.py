"""Download stage — powered by yt-dlp.

Replaces the old ``pytube`` + ``youtube-dl`` combo, both of which break whenever
YouTube rotates its signatures. yt-dlp is the actively-maintained standard and is a
pure-Python pip dependency (it shells out to the ffmpeg we already require for muxing).

We fetch two artifacts:
  * the best MP4 video+audio stream (kept for the final mux), and
  * a clean 16 kHz mono WAV of the audio (what the ASR and voice-cloning stages want).
"""

from __future__ import annotations

import re
from pathlib import Path

from ytdub.logging import stage_logger
from ytdub.models import DownloadResult

log = stage_logger("download")

_ID_RE = re.compile(r"(?:v=|/shorts/|youtu\.be/|/)([0-9A-Za-z_-]{11})(?:[?&/]|$)")


def extract_video_id(url: str) -> str | None:
    """Best-effort 11-char YouTube id extraction (watch, shorts, youtu.be, embed)."""
    match = _ID_RE.search(url)
    return match.group(1) if match else None


def _cookie_opts(
    cookies_from_browser: str | None, cookies_file: Path | None
) -> dict:
    """yt-dlp cookie options.

    Some networks/IPs (datacenters, VPNs, CI) trigger YouTube's "confirm you're not a
    bot" check; passing your browser's cookies is the standard fix. On a normal home
    machine this is usually unnecessary.
    """
    opts: dict = {}
    if cookies_from_browser:
        opts["cookiesfrombrowser"] = (cookies_from_browser,)
    if cookies_file:
        opts["cookiefile"] = str(cookies_file)
    return opts


def download(
    url: str,
    downloads_dir: Path,
    *,
    cookies_from_browser: str | None = None,
    cookies_file: Path | None = None,
) -> DownloadResult:
    """Download ``url`` and return the local video path plus a 16 kHz mono WAV.

    yt-dlp handles shorts, age-gates, format selection and ffmpeg post-processing.
    """
    import yt_dlp  # lazy

    downloads_dir.mkdir(parents=True, exist_ok=True)
    outtmpl = str(downloads_dir / "%(id)s.%(ext)s")
    cookie_opts = _cookie_opts(cookies_from_browser, cookies_file)

    # First pass: grab the muxed MP4 we will later re-dub.
    video_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        **cookie_opts,
    }

    log.info(f"Fetching video metadata + stream: {url}")
    with yt_dlp.YoutubeDL(video_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    video_id: str = info["id"]
    title: str = info.get("title", video_id)
    duration = float(info.get("duration") or 0.0)
    video_path = downloads_dir / f"{video_id}.mp4"

    # Second pass: extract a normalized 16 kHz mono WAV for ASR + voice cloning.
    audio_path = downloads_dir / f"{video_id}.wav"
    audio_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(downloads_dir / f"{video_id}.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "wav"},
        ],
        # 16 kHz mono is what Whisper/cloning models expect.
        "postprocessor_args": {"extractaudio": ["-ar", "16000", "-ac", "1"]},
        **cookie_opts,
    }
    log.info("Extracting 16 kHz mono audio track")
    with yt_dlp.YoutubeDL(audio_opts) as ydl:
        ydl.extract_info(url, download=True)

    if not video_path.exists():
        raise FileNotFoundError(f"yt-dlp did not produce {video_path}")
    if not audio_path.exists():
        raise FileNotFoundError(f"yt-dlp did not produce {audio_path}")

    log.success(f"Downloaded '{title}' ({duration:.0f}s) -> {video_path.name}")
    return DownloadResult(
        video_id=video_id,
        title=title,
        video_path=video_path,
        audio_path=audio_path,
        duration=duration,
    )
