from app.services import youtube_downloader, audio_processor, video_assembler
from loguru import logger
import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.video_schema import VideoDownloadRequest
from pytube import extract
from fastapi import APIRouter, File, UploadFile, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse
import os
from starlette.status import HTTP_404_NOT_FOUND
import re
from typing import Dict

router = APIRouter()

# Global dictionary to track the status of tasks
task_status: Dict[str, str] = {}


# Retrieve the DATA_DIR from environment variable or use default
DATA_DIR = os.getenv("DATA_DIR", "/home/sam/github/youtube-auto-dub/backend/data")

def extract_video_id(url: str) -> str:
    """
    Extracts the video ID from a YouTube URL.
    """
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, str(url))
    return match.group(1) if match else None


@router.post("/download/")
async def download_video(request: VideoDownloadRequest, background_tasks: BackgroundTasks):
    # Correctly access youtube_url from the request object
    video_id = extract_video_id(request.url)
    if not video_id:
        logger.error("Invalid YouTube URL provided.")
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    try:
        url = str(request.url)
        logger.info(f"Received download request for URL: {url}")

        video_id = extract.video_id(url)
        if not video_id:
            logger.error("Invalid YouTube URL provided.")
            raise HTTPException(status_code=400, detail="Invalid YouTube URL.")

        video_path, audio_path = youtube_downloader.download_video_and_audio(
            url, DATA_DIR
        )

        caption_path = youtube_downloader.download_italian_captions(video_id, DATA_DIR)
        translated_text = (
            youtube_downloader.translate_captions(caption_path)
            if caption_path
            else None
        )

        output_path = os.path.join(
            DATA_DIR, "final_videos", os.path.basename(video_path)
        )
        task_status[video_id] = "Processing"

        background_tasks.add_task(
            process_audio_and_assemble_video,
            video_path,
            audio_path,
            output_path,
            translated_text,
            video_id
        )

        return {"video_id": video_id, "status": "Processing started"}
    except Exception as e:
        logger.error(f"Error in download_video endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{video_id}")
def get_task_status(video_id: str):
    status = task_status.get(video_id, "Not Found")
    return {"video_id": video_id, "status": status}

@router.get("/download-video/{video_id}")
async def download_video(video_id: str):
    video_path = os.path.join(DATA_DIR, "final_videos", f"{video_id}.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Video not found")
    return FileResponse(video_path, media_type="video/mp4", filename=f"{video_id}.mp4")


def process_audio_and_assemble_video(
    video_path: str, audio_path: str, output_path: str, text_to_speak: str, video_id: str
):
    try:
        style = "default"
        speed = 1.0
        language = "English"
        encode_message = "@MyShell"

        text_to_use = text_to_speak if text_to_speak else "Default text here"

        processed_audio_path = os.path.join(
            DATA_DIR, "processed_audios", "processed_output.mp3"
        )
        audio_processor.process_audio(
            audio_input_path=audio_path,
            audio_output_path=processed_audio_path,
            text=text_to_use,
            style=style,
            speed=speed,
            language=language,
            encode_message=encode_message,
        )

        video_assembler.merge_audio_with_video(
            video_path, processed_audio_path, output_path
        )

        task_status[video_id] = "Completed"

    except Exception as e:
        task_status[video_id] = "Failed"
        logger.error(f"Error in process_audio_and_assemble_video: {e}")
