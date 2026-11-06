from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.jobs import JobStore
from app.worker import Worker
from app.generator import VideoGenerator
from app.scenarios import CONCEPTS

QUESTIONS = {details[0]: concept for concept, details in CONCEPTS.items()}


class VideoRequest(BaseModel):
    question: str


class Job(BaseModel):
    job_id: UUID
    question: str
    concept: str
    status: str
    stage: str | None = None
    error: str | None = None
    artifact_url: str | None = None


def create_app(database_path: str | Path = "jobs.sqlite3", executor=None, artifact_root: str | Path = "artifacts") -> FastAPI:
    store = JobStore(database_path)
    artifact_root = Path(artifact_root).resolve()
    worker = Worker(store, executor if executor is not None else VideoGenerator(artifact_root))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        store.initialize()
        worker.start()
        yield
        worker.stop()

    app = FastAPI(title="Chemistry Video Request Service", version="0.2.0", lifespan=lifespan)

    def get_job(job_id: UUID) -> dict:
        job = store.get(str(job_id))
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return job

    @app.post("/videos", response_model=Job, status_code=status.HTTP_202_ACCEPTED)
    def create_video(request: VideoRequest) -> dict:
        concept = QUESTIONS.get(request.question)
        if concept is None:
            raise HTTPException(status_code=422, detail="Unsupported question")
        job = {"job_id": str(uuid4()), "question": request.question, "concept": concept,
               "status": "queued", "stage": None, "error": None, "artifact_url": None}
        store.create(job)
        worker.wake()
        return job

    @app.get("/videos", response_model=list[Job])
    def list_videos() -> list[dict]:
        return store.list_jobs()

    @app.get("/videos/{job_id}", response_model=Job)
    def video_status(job_id: UUID) -> dict:
        return get_job(job_id)

    @app.get("/videos/{job_id}/file")
    def video_file(job_id: UUID):
        job = get_job(job_id)
        if job["status"] != "completed" or not job["artifact_url"]:
            raise HTTPException(status_code=409, detail="No video artifact is available")
        path = artifact_root / str(job_id) / "video.mp4"
        if not path.is_file() or path.stat().st_size == 0:
            raise HTTPException(status_code=404, detail="Video artifact is missing")
        return FileResponse(path, media_type="video/mp4", filename=f"{job_id}.mp4")

    return app


app = create_app()
