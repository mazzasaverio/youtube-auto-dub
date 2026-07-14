"""Optional FastAPI server (install with ``pip install 'ytdub[api]'``).

The CLI is the primary entry point; this exists for programmatic/remote use. Job state
is kept in a simple in-process registry — fine for a single-worker local server. For a
real multi-worker deployment, back it with Redis or a database.

Run:  uvicorn ytdub.api:app --reload
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel

from ytdub.config import Settings
from ytdub.logging import setup_logging
from ytdub.pipeline import dub as run_dub

setup_logging()
app = FastAPI(title="ytdub", version="0.2.0")
_executor = ThreadPoolExecutor(max_workers=1)  # heavy models -> serialize by default


@dataclass
class Job:
    status: str = "queued"  # queued | processing | completed | failed
    output_path: str | None = None
    error: str | None = None
    detail: dict = field(default_factory=dict)


_JOBS: dict[str, Job] = {}


class DubRequest(BaseModel):
    url: str
    target_lang: str = "en"
    source_lang: str | None = None
    tts_backend: str = "xtts"
    translator: str = "argos"


def _process(job_id: str, req: DubRequest) -> None:
    _JOBS[job_id].status = "processing"
    try:
        settings = Settings(
            target_lang=req.target_lang,
            source_lang=req.source_lang,
            tts_backend=req.tts_backend,
            translator=req.translator,
        )
        result = run_dub(req.url, settings)
        _JOBS[job_id].status = "completed"
        _JOBS[job_id].output_path = str(result.output_path)
        _JOBS[job_id].detail = {
            "video_id": result.video_id,
            "segments": len(result.segments),
            "source_lang": result.source_lang,
            "target_lang": result.target_lang,
        }
    except Exception as exc:  # surface failures to the status endpoint
        _JOBS[job_id].status = "failed"
        _JOBS[job_id].error = str(exc)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.post("/dub")
async def create_dub(req: DubRequest, background_tasks: BackgroundTasks):
    from ytdub.stages.download import extract_video_id

    video_id = extract_video_id(req.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    _JOBS[video_id] = Job()
    background_tasks.add_task(_executor.submit, _process, video_id, req)
    return {"job_id": video_id, "status": "queued"}


@app.get("/status/{job_id}")
async def status(job_id: str):
    job = _JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Unknown job")
    return {"job_id": job_id, **asdict(job)}


@app.get("/download/{job_id}")
async def download(job_id: str):
    job = _JOBS.get(job_id)
    if not job or job.status != "completed" or not job.output_path:
        raise HTTPException(status_code=404, detail="Video not ready")
    return FileResponse(job.output_path, media_type="video/mp4", filename=f"{job_id}.mp4")
