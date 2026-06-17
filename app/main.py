"""
CORTEX RENDER — FastAPI Orchestrator
Generative cinematic video engine for brain hacks documentaries.
"""
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.models import (
    GenerateRequest,
    GenerationJob,
    DirectorCut,
    ThemeManifest,
    JobStatus,
    SceneAssetManifest,
)

settings = get_settings()
app = FastAPI(
    title="CORTEX RENDER",
    description="Generative cinematic video engine for brain hacks documentaries.",
    version="1.0.0",
)

# In-memory job store (replace with Redis/DB for production)
jobs: dict[str, GenerationJob] = {}

# Serve rendered videos
render_dir = Path(settings.render_dir)
render_dir.mkdir(parents=True, exist_ok=True)
app.mount("/videos", StaticFiles(directory=render_dir), name="videos")

# Serve assets (for UI preview)
app.mount("/assets", StaticFiles(directory=settings.asset_dir), name="assets")


@app.get("/")
async def root():
    return {
        "engine": "CORTEX RENDER",
        "version": "1.0.0",
        "status": "online",
        "endpoints": [
            "/generate",
            "/jobs/{job_id}",
            "/directors-cut/{job_id}",
            "/preview-scene/{job_id}/{scene_id}",
            "/videos",
        ],
    }


@app.post("/generate", response_model=GenerationJob)
async def generate_video(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Start a new generative video production job."""
    job_id = str(uuid.uuid4())[:12]
    job = GenerationJob(
        job_id=job_id,
        topic=request.topic,
        target_duration=request.target_duration or 540,  # 9 min default
        status=JobStatus.queued,
        created_at=datetime.utcnow().isoformat(),
        progress_percent=0.0,
    )
    jobs[job_id] = job

    # Background task: kick the full pipeline
    background_tasks.add_task(run_pipeline, job_id, request)

    return job


@app.get("/jobs/{job_id}", response_model=GenerationJob)
async def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.get("/directors-cut/{job_id}")
async def get_directors_cut(job_id: str):
    """Return the Director's Cut JSON for a job (if generated)."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    if job.directors_cut is None:
        raise HTTPException(status_code=202, detail="Director's Cut not yet generated")
    return job.directors_cut


@app.get("/preview-scene/{job_id}/{scene_id}")
async def preview_scene(job_id: str, scene_id: str):
    """Return a rendered preview (MP4 or PNG frame) for a single scene."""
    preview_path = render_dir / f"{job_id}_scene_{scene_id}_preview.mp4"
    if not preview_path.exists():
        raise HTTPException(status_code=404, detail="Scene preview not yet rendered")
    return FileResponse(preview_path, media_type="video/mp4")


@app.get("/download/{job_id}")
async def download_video(job_id: str):
    """Download the final mastered video."""
    final_path = render_dir / f"{job_id}_final.mp4"
    if not final_path.exists():
        raise HTTPException(status_code=404, detail="Final video not yet rendered")
    return FileResponse(
        final_path,
        media_type="video/mp4",
        filename=f"cortex_render_{job_id}.mp4",
    )


@app.get("/health")
async def health():
    return {"status": "ok", "disk_cache_mb": get_disk_cache_size()}


# ============== PIPELINE ORCHESTRATOR (stub for Phase 0) ==============

async def run_pipeline(job_id: str, request: GenerateRequest):
    """Full generative pipeline. Stubbed for Phase 0."""
    job = jobs[job_id]
    job.status = JobStatus.running
    job.progress_percent = 0.0

    try:
        # Step 1: Brain (Director's Cut + Theme Manifest)
        job.status = JobStatus.brain_active
        job.progress_percent = 5.0
        await asyncio.sleep(2)  # Placeholder for Groq API call

        # Step 2: Asset Procurement
        job.status = JobStatus.assets_fetching
        job.progress_percent = 15.0
        await asyncio.sleep(2)

        # Step 3: Animation Factory (Mograph rendering)
        job.status = JobStatus.mograph_rendering
        job.progress_percent = 30.0
        await asyncio.sleep(3)

        # Step 4: Audio Engine (TTS + Music + Beat detection)
        job.status = JobStatus.audio_mixing
        job.progress_percent = 50.0
        await asyncio.sleep(2)

        # Step 5: Compositor (Scene assembly + transitions)
        job.status = JobStatus.compositing
        job.progress_percent = 75.0
        await asyncio.sleep(3)

        # Step 6: Final mastering
        job.status = JobStatus.mastering
        job.progress_percent = 95.0
        await asyncio.sleep(1)

        # Create a dummy final file for Phase 0 demo
        final_path = render_dir / f"{job_id}_final.mp4"
        _generate_test_video(final_path, request.topic)

        job.status = JobStatus.completed
        job.progress_percent = 100.0
        job.output_path = f"/videos/{job_id}_final.mp4"
        job.completed_at = datetime.utcnow().isoformat()

    except Exception as e:
        job.status = JobStatus.failed
        job.error = str(e)
        raise


def _generate_test_video(path: Path, topic: str):
    """Generate a test colorbar video with FFmpeg so the download endpoint works."""
    import subprocess
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "testsrc=duration=5:size=1920x1080:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=1000:duration=5",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast",
        str(path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def get_disk_cache_size() -> int:
    try:
        import shutil
        total, used, free = shutil.disk_usage(settings.cache_dir)
        return int(used / (1024 * 1024))
    except Exception:
        return 0
