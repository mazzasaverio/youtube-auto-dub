import os
from pytube import YouTube
from loguru import logger
import youtube_dl

from googletrans import Translator


def translate_captions(caption_path: str):
    try:
        translator = Translator()
        with open(caption_path, "r") as file:
            italian_captions = file.read()

        # Remove timestamps and translate
        text_only_captions = "\n".join(
            line for line in italian_captions.split("\n") if not "-->" in line
        )
        translated_captions = translator.translate(
            text_only_captions, src="it", dest="en"
        ).text
        return translated_captions
    except Exception as e:
        logger.error(f"Error in translating captions: {e}")
        return None


def download_video_and_audio(url: str, data_dir: str):
    try:
        url = str(url)
        logger.info(f"Attempting to download video from URL: {url}")

        # Check if URL is a YouTube Shorts link and modify it
        if "youtube.com/shorts/" in url:
            # Extract the video ID from the URL
            video_id = url.split("/")[-1].split("?")[0]
            url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"Modified URL for YouTube Shorts: {url}")

        yt = YouTube(url)

        video_path = os.path.join(data_dir, "downloaded_videos", f"{yt.video_id}.mp4")
        audio_path = os.path.join(data_dir, "processed_audios", f"{yt.video_id}.mp3")

        yt.streams.filter(progressive=True, file_extension="mp4").first().download(
            filename=video_path
        )
        yt.streams.filter(only_audio=True).first().download(filename=audio_path)

        logger.info(f"Download successful for URL: {url}")
        return video_path, audio_path
    except Exception as e:
        logger.error(f"Error in download_video_and_audio: {e}")
        raise


from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)


def download_italian_captions(video_id: str, data_dir: str):
    try:
        caption_path = os.path.join(data_dir, "captions", f"{video_id}.it.srt")

        # Check if the captions file already exists
        if os.path.exists(caption_path):
            logger.info(
                f"Captions file {caption_path} already exists. Skipping download."
            )
            return caption_path

        logger.info(f"Attempting to download Italian captions for video ID: {video_id}")

        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        italian_transcript = transcript_list.find_transcript(["it"])

        transcript = italian_transcript.fetch()

        # Construct the caption data with timestamps
        captions = "\n".join(
            [
                f"{t['start']} --> {t['start'] + t['duration']}\n{t['text']}"
                for t in transcript
            ]
        )

        with open(caption_path, "w") as file:
            file.write(captions)

        logger.info("Downloaded and saved Italian captions successfully.")
        return caption_path

    except TranscriptsDisabled:
        logger.error("Captions are disabled for this video.")
    except NoTranscriptFound:
        logger.error("No Italian captions found for this video.")
    except Exception as e:
        logger.error(f"Error in downloading Italian captions: {e}")
