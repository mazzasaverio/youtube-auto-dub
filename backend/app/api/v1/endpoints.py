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


router = APIRouter()


# Retrieve the DATA_DIR from environment variable or use default
DATA_DIR = os.getenv("DATA_DIR", "/home/sam/github/youtube-auto-dub/backend/data")


@router.post("/download/")
async def download_video(
    request: VideoDownloadRequest, background_tasks: BackgroundTasks
):
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

        background_tasks.add_task(
            process_audio_and_assemble_video,
            video_path,
            audio_path,
            output_path,
            translated_text,
        )
        return {"message": "Video processing started.", "caption_path": caption_path}
    except Exception as e:
        logger.error(f"Error in download_video endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download-video/{video_id}")
async def download_video(video_id: str):
    video_path = os.path.join(DATA_DIR, "final_videos", f"{video_id}.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Video not found")
    return FileResponse(video_path, media_type="video/mp4", filename=f"{video_id}.mp4")


def process_audio_and_assemble_video(
    video_path: str, audio_path: str, output_path: str, text_to_speak: str
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

    except Exception as e:
        logger.error(f"Error in process_audio_and_assemble_video: {e}")
