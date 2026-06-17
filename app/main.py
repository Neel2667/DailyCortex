"""
CORTEX RENDER — FastAPI Orchestrator
Generative cinematic video engine for brain hacks documentaries.

Pipeline Architecture:
  1. Brain: Groq 2-pass generates Director's Cut + Hook Cadence
  2. Assets: Pexels clips + user assets fetched in parallel
  3. Audio: TTS narrations + music stem + beat analysis + mixing
  4. Mograph: Animation Factory renders React components to transparent video
  5. Compositor: FFmpeg assembles scenes with transitions, color grades, beat sync
  6. Master: Final concat + loudnorm + H.264 export

Endpoints:
  POST /generate          → Start a new video generation job
  GET  /jobs/{job_id}     → Check job status + progress
  GET  /directors-cut/{id} → Preview the generated shot-list
  GET  /download/{id}     → Download final mastered video
  GET  /health            → System health + disk cache
"""
import asyncio
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, BackgroundTasks, HTTPException
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

# Module imports (will be wired in the pipeline)
from app import brain, asset_manager, audio_engine, compositor

settings = get_settings()
app = FastAPI(
    title="CORTEX RENDER",
    description="Generative cinematic video engine for brain hacks documentaries.",
    version="1.0.0",
)

# In-memory job store (replace with Redis/DB for production)
jobs: Dict[str, GenerationJob] = {}

# Serve rendered videos and static previews
render_dir = Path(settings.render_dir)
render_dir.mkdir(parents=True, exist_ok=True)
app.mount("/videos", StaticFiles(directory=render_dir), name="videos")

# Serve user assets (for preview)
app.mount("/assets", StaticFiles(directory=settings.asset_dir), name="assets")

# Serve preview.html (component showcase)
preview_dir = Path(__file__).parent.parent
if (preview_dir / "preview.html").exists():
    app.mount("/preview", StaticFiles(directory=preview_dir, html=True), name="preview")


# ═══════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

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
            "/download/{job_id}",
            "/health",
        ],
    }


@app.post("/generate", response_model=GenerationJob)
async def generate_video(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Start a new generative video production job."""
    job_id = str(uuid.uuid4())[:12]
    job = GenerationJob(
        job_id=job_id,
        topic=request.topic,
        target_duration=request.target_duration or 540,
        status=JobStatus.queued,
        created_at=datetime.now(timezone.utc).isoformat(),
        progress_percent=0.0,
    )
    jobs[job_id] = job

    background_tasks.add_task(run_pipeline, job_id, request)
    return job


@app.get("/jobs/{job_id}", response_model=GenerationJob)
async def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.get("/directors-cut/{job_id}")
async def get_directors_cut(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    if job.directors_cut is None:
        raise HTTPException(status_code=202, detail="Director's Cut not yet generated")
    return job.directors_cut


@app.get("/preview-scene/{job_id}/{scene_id}")
async def preview_scene(job_id: str, scene_id: str):
    preview_path = render_dir / f"{job_id}_scene_{scene_id}_preview.mp4"
    if not preview_path.exists():
        raise HTTPException(status_code=404, detail="Scene preview not yet rendered")
    return FileResponse(preview_path, media_type="video/mp4")


@app.get("/download/{job_id}")
async def download_video(job_id: str):
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
    import shutil
    try:
        total, used, free = shutil.disk_usage(settings.cache_dir)
        disk_usage_mb = {
            "total_mb": int(total / (1024 * 1024)),
            "used_mb": int(used / (1024 * 1024)),
            "free_mb": int(free / (1024 * 1024)),
        }
    except Exception:
        disk_usage_mb = {"error": "Could not read disk usage"}
    
    return {
        "status": "ok",
        "disk_cache_mb": disk_usage_mb,
        "active_jobs": len([j for j in jobs.values() if j.status not in (JobStatus.completed, JobStatus.failed)]),
        "completed_jobs": len([j for j in jobs.values() if j.status == JobStatus.completed]),
        "failed_jobs": len([j for j in jobs.values() if j.status == JobStatus.failed]),
    }


# ═══════════════════════════════════════════════════════════════════════════
# TEST ENDPOINTS (Development only)
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/test/fixture")
async def create_test_fixture():
    """Generate a test Director's Cut fixture without calling Groq (for testing)."""
    from app.models import (
        HookCadence, OpenLoop, VisualTension, MicroHook, Keyframe,
        ColorSystem, Typography, MotionLanguage, ThemeManifest,
        Scene, HookRole, TextOverlay,
    )
    
    job_id = str(uuid.uuid4())[:12]
    
    # Create a realistic test fixture
    director_cut = DirectorCut(
        video_id=job_id,
        title="Why You Procrastinate (Test Fixture)",
        target_duration_sec=540,
        mood_arc=["curious", "tense", "revelatory", "calm", "hopeful"],
        theme_manifest=ThemeManifest(
            theme_id=f"procrastination-test-{job_id}",
            topic_mood="clinical-curious",
            color_system=ColorSystem(),
            typography=Typography(),
            motion_language=MotionLanguage(),
        ),
        hook_cadence=HookCadence(
            open_loops=[
                OpenLoop(
                    loop_id="L1",
                    tease_line="There's a 2-minute brain hack that makes procrastination impossible.",
                    tease_at_sec=0.0,
                    payoff_line="The 2-Minute Initiation Protocol. Here's how it works.",
                    payoff_at_sec=450.0,
                    visual_tension=VisualTension(
                        tease_scene="S01",
                        escalation_scenes=["S02", "S03", "S04", "S05"],
                        payoff_scene="S20",
                    ),
                    intensity_arc=[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                    loop_type="big",
                ),
            ],
            micro_hooks=[
                MicroHook(at_sec=15.0, line="But here's the problem...", visual_snap="text_color_shift"),
                MicroHook(at_sec=85.0, line="Your brain doesn't know the difference.", visual_snap="split_screen_compare"),
            ],
            callback_reference="Why you can't focus (from intro hook)",
            tension_peak_sec=450.0,
        ),
        scenes=[
            Scene(
                scene_id="S01",
                start_sec=0.0,
                duration_sec=15.0,
                hook_role=HookRole.tease,
                visual_intensity=0.8,
                keyframes=[
                    Keyframe(at_sec=0.0, visual_action="text_slam", element="hero_title"),
                    Keyframe(at_sec=5.0, visual_action="particle_burst", element="particle_field"),
                    Keyframe(at_sec=10.0, visual_action="fade_in", element="subtitle"),
                ],
                narration="There's a 2-minute brain hack that makes procrastination impossible.",
                mood="curious",
                pacing="fast",
                visual_keywords=["brain", "focus", "neural network"],
                animation_trigger="QuestionBomb",
                color_grade="cool_blue",
                beat_sync_intensity=0.6,
                text_overlay=TextOverlay(
                    text="Why You Procrastinate",
                    style="title_reveal",
                    position="center",
                    accent_words=["Procrastinate"],
                ),
                transition_out="auto",
                layout_family="center_hero",
            ),
            Scene(
                scene_id="S02",
                start_sec=15.0,
                duration_sec=20.0,
                hook_role=HookRole.escalation,
                visual_intensity=0.4,
                keyframes=[
                    Keyframe(at_sec=0.0, visual_action="data_enter", element="stat_counter"),
                    Keyframe(at_sec=8.0, visual_action="counter_tick", element="live_number"),
                    Keyframe(at_sec=15.0, visual_action="text_shift", element="caption"),
                ],
                narration="One in five adults are chronic procrastinators. That's roughly 1.4 billion people.",
                mood="tense",
                pacing="medium",
                visual_keywords=["statistics", "numbers", "data"],
                animation_trigger="StatShock",
                color_grade="high_contrast_mono",
                beat_sync_intensity=0.3,
                transition_out="auto",
                layout_family="data_dominant",
            ),
            Scene(
                scene_id="S03",
                start_sec=35.0,
                duration_sec=20.0,
                hook_role=HookRole.escalation,
                visual_intensity=0.5,
                keyframes=[
                    Keyframe(at_sec=0.0, visual_action="overlay_pulse", element="brain_scan"),
                    Keyframe(at_sec=7.0, visual_action="comparison_reveal", element="region_label"),
                    Keyframe(at_sec=14.0, visual_action="line_draw", element="neural_connection"),
                ],
                narration="It's not laziness. It's your brain. Your prefrontal cortex wants to plan, but your amygdala screams danger.",
                mood="tense",
                pacing="medium",
                visual_keywords=["brain scan", "neuroscience", "prefrontal cortex"],
                animation_trigger="BrainSVG",
                color_grade="deep_purple",
                beat_sync_intensity=0.4,
                transition_out="auto",
                layout_family="split_screen",
            ),
            Scene(
                scene_id="S20",
                start_sec=450.0,
                duration_sec=20.0,
                hook_role=HookRole.payoff,
                visual_intensity=1.0,
                keyframes=[
                    Keyframe(at_sec=0.0, visual_action="text_slam", element="hero_title"),
                    Keyframe(at_sec=5.0, visual_action="particle_burst", element="particle_field"),
                    Keyframe(at_sec=10.0, visual_action="icon_appear", element="step_number"),
                ],
                narration="The 2-Minute Initiation Protocol. Here's how it works. Step 1: Pick the task.",
                mood="euphoric",
                pacing="fast",
                visual_keywords=["protocol", "steps", "action"],
                animation_trigger="StepCard",
                color_grade="warm_gold",
                beat_sync_intensity=0.9,
                transition_out="auto",
                layout_family="overlay_heavy",
            ),
        ],
    )
    
    # Save to cache
    fixture_path = settings.cache_dir / f"test_fixture_{job_id}.json"
    fixture_path.write_text(director_cut.model_dump_json(indent=2))
    
    return {
        "job_id": job_id,
        "fixture_path": str(fixture_path),
        "directors_cut": director_cut.model_dump(),
    }


# ═══════════════════════════════════════════════════════════════════════════
# PIPELINE ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════

def _update_job(job_id: str, status: JobStatus, progress: float, **kwargs):
    """Update job state atomically."""
    if job_id in jobs:
        jobs[job_id].status = status
        jobs[job_id].progress_percent = progress
        for key, value in kwargs.items():
            setattr(jobs[job_id], key, value)


async def run_pipeline(job_id: str, request: GenerateRequest):
    """
    Full generative pipeline orchestration.
    
    Phase 1: Brain — Director's Cut + Hook Cadence
    Phase 2: Assets — Pexels stock footage + user assets
    Phase 3: Audio — TTS + music stem + beat analysis + mixing
    Phase 4: Mograph — Animation Factory renders (parallel batches)
    Phase 5: Compositing — FFmpeg scene assembly + transitions + color grade
    Phase 6: Mastering — Concat + audio mux + loudnorm + H.264 export
    """
    job_output_dir = settings.cache_dir / job_id
    job_output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # ─────────────────────────────────────────────────────────────────
        # PHASE 1: The Brain (Groq 2-Pass Generation)
        # ─────────────────────────────────────────────────────────────────
        _update_job(job_id, JobStatus.brain_active, 5.0)
        
        director_cut: DirectorCut
        if settings.groq_api_key:
            try:
                director_cut = await brain.generate_directors_cut(
                    topic=request.topic,
                    target_duration=request.target_duration or 540,
                    style_bias=request.style_bias,
                )
            except Exception as e:
                print(f"[Brain] Groq generation failed: {e}. Using test fixture.")
                # Fallback: load a test fixture or generate a minimal one
                director_cut = await _load_or_create_fixture(job_id, request)
        else:
            print("[Brain] No GROQ_API_KEY set. Using test fixture.")
            director_cut = await _load_or_create_fixture(job_id, request)
        
        # Validate hook cadence
        if not director_cut.hook_cadence or not director_cut.hook_cadence.open_loops:
            print(f"[Brain] Warning: Hook cadence missing. Using fallback.")
            # Could add fallback hook generation here
        
        _update_job(job_id, JobStatus.brain_active, 15.0, directors_cut=director_cut)
        
        # ─────────────────────────────────────────────────────────────────
        # PHASE 2: Asset Procurement (Parallel)
        # ─────────────────────────────────────────────────────────────────
        _update_job(job_id, JobStatus.assets_fetching, 15.0)
        
        scene_assets = await asset_manager.fetch_all_scene_assets(
            director_cut=director_cut,
            per_scene=3,
            max_parallel=4,
        )
        
        # Also index user assets (for future use)
        user_asset_index = asset_manager.build_user_asset_index()
        
        _update_job(job_id, JobStatus.assets_fetching, 25.0)
        
        # ─────────────────────────────────────────────────────────────────
        # PHASE 3: Audio Production (TTS + Music + Beat Analysis + Mixing)
        # ─────────────────────────────────────────────────────────────────
        _update_job(job_id, JobStatus.audio_mixing, 25.0)
        
        audio_plan = await audio_engine.produce_audio(
            director_cut=director_cut,
            output_dir=job_output_dir / "audio",
        )
        
        _update_job(job_id, JobStatus.audio_mixing, 40.0, audio_mix_plan=audio_plan)
        
        # ─────────────────────────────────────────────────────────────────
        # PHASE 4: Animation Factory (Mograph Rendering — Parallel Batches)
        # ─────────────────────────────────────────────────────────────────
        _update_job(job_id, JobStatus.mograph_rendering, 40.0)
        
        # For each scene, render the motion graphic component
        mograph_outputs = {}
        for i, scene in enumerate(director_cut.scenes):
            component_id = scene.animation_trigger
            if not component_id or component_id == "auto":
                continue
            
            mograph_path = job_output_dir / "mographs" / f"{scene.scene_id}_{component_id}.mov"
            mograph_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Build render props
            render_props = {
                "componentId": component_id,
                "props": _build_component_props(scene, director_cut.theme_manifest),
                "durationMs": int(scene.duration_sec * 1000),
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "theme": director_cut.theme_manifest.model_dump(),
            }
            
            props_file = job_output_dir / "mographs" / f"{scene.scene_id}_props.json"
            props_file.write_text(json.dumps(render_props, indent=2))
            
            # Render via Animation Factory (subprocess call to render-clip.js)
            # In production, this runs in parallel batches
            try:
                proc = await asyncio.create_subprocess_exec(
                    "node", "mograph_factory/scripts/render-clip.js",
                    str(props_file), str(mograph_path),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                
                if proc.returncode == 0 and mograph_path.exists():
                    mograph_outputs[scene.scene_id] = str(mograph_path)
                    print(f"[Mograph] {scene.scene_id}: {mograph_path} ({mograph_path.stat().st_size / (1024*1024):.1f} MB)")
                else:
                    print(f"[Mograph] {scene.scene_id} failed: {stderr.decode()[:500]}")
            except Exception as e:
                print(f"[Mograph] {scene.scene_id} error: {e}")
            
            progress = 40 + (i / len(director_cut.scenes)) * 20
            _update_job(job_id, JobStatus.mograph_rendering, progress)
        
        # Update scene assets with mograph outputs
        for scene_id, mograph_path in mograph_outputs.items():
            if scene_id in scene_assets:
                scene_assets[scene_id]["mograph_clips"] = [mograph_path]
        
        _update_job(job_id, JobStatus.mograph_rendering, 60.0)
        
        # ─────────────────────────────────────────────────────────────────
        # PHASE 5: Compositing (FFmpeg Scene Assembly — Parallel)
        # ─────────────────────────────────────────────────────────────────
        _update_job(job_id, JobStatus.compositing, 60.0)
        
        final_video = await compositor.compose_video(
            director_cut=director_cut,
            scene_assets=scene_assets,
            beat_grid=audio_plan.beat_grid,
            audio_path=Path(audio_plan.narration_path).parent.parent / "final_audio.aac",  # Actually the mixed audio
            output_path=render_dir / f"{job_id}_final.mp4",
            max_parallel=settings.max_parallel_scenes,
        )
        
        _update_job(job_id, JobStatus.compositing, 95.0)
        
        # ─────────────────────────────────────────────────────────────────
        # PHASE 6: Mastering (already done in compose_video, but verify)
        # ─────────────────────────────────────────────────────────────────
        _update_job(job_id, JobStatus.mastering, 95.0)
        
        if final_video.exists():
            file_size_mb = final_video.stat().st_size / (1024 * 1024)
            print(f"[Master] Final output: {final_video} ({file_size_mb:.1f} MB)")
        else:
            raise RuntimeError("Final video not produced")
        
        _update_job(
            job_id,
            JobStatus.completed,
            100.0,
            output_path=f"/videos/{job_id}_final.mp4",
            completed_at=datetime.now(timezone.utc).isoformat(),
        )
        
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"[Pipeline] Job {job_id} failed:\n{error_msg}")
        _update_job(
            job_id,
            JobStatus.failed,
            jobs.get(job_id, GenerationJob(job_id=job_id, topic=request.topic, target_duration=request.target_duration or 540, status=JobStatus.failed, created_at="")).progress_percent,
            error=error_msg,
        )


def _build_component_props(scene: Scene, theme: ThemeManifest) -> Dict[str, Any]:
    """Build component-specific props from scene data and theme."""
    component_id = scene.animation_trigger
    
    # Base props available to all components
    base_props = {
        "theme": theme.model_dump(),
        "scene_id": scene.scene_id,
        "duration_sec": scene.duration_sec,
        "mood": scene.mood,
        "visual_intensity": scene.visual_intensity,
    }
    
    # Component-specific props
    component_props = {
        "QuestionBomb": lambda: {
            "question": scene.text_overlay.text if scene.text_overlay else scene.narration[:50],
            "accent_words": scene.text_overlay.accent_words if scene.text_overlay else [],
            "particle_burst": True,
        },
        "StatShock": lambda: {
            "number": "1",
            "suffix": "/5",
            "caption": scene.narration[:100],
            "context": "That's roughly 1.4 billion people",
        },
        "BrainSVG": lambda: {
            "active_regions": ["prefrontal", "amygdala"],
            "show_labels": True,
            "pulse_rings": True,
        },
        "StepCard": lambda: {
            "steps": [
                {"number": 1, "title": "Pick the task", "description": "The one you've been avoiding."},
                {"number": 2, "title": "Set 2 minutes", "description": "Promise yourself: just two minutes."},
                {"number": 3, "title": "Just begin", "description": "Action creates motivation."},
            ],
        },
        "KineticType": lambda: {
            "text": scene.text_overlay.text if scene.text_overlay else scene.narration[:80],
            "reveal_type": "word",
            "style": "title" if scene.hook_role == "tease" else "subtitle",
        },
        "ComparisonSplit": lambda: {
            "leftLabel": "Before",
            "rightLabel": "After",
            "leftValue": 85,
            "rightValue": 25,
            "unit": "%",
        },
        "FloatingCard": lambda: {
            "label": "Data Point",
            "value": "↑ 47%",
            "sub": "during stress",
        },
        "MeshGradient": lambda: {
            "stops": [theme.color_system.primary, theme.color_system.secondary, theme.color_system.tertiary],
        },
    }
    
    builder = component_props.get(component_id, lambda: {})
    return {**base_props, **builder()}


async def _load_or_create_fixture(job_id: str, request: GenerateRequest) -> DirectorCut:
    """Create a test Director's Cut when Groq is unavailable."""
    # Call the test fixture creation logic
    from app.models import (
        HookCadence, OpenLoop, VisualTension, MicroHook, Keyframe,
        ColorSystem, Typography, MotionLanguage, ThemeManifest,
        Scene, HookRole, TextOverlay, Mood, Pacing, ColorGrade, LayoutFamily,
    )
    
    return DirectorCut(
        video_id=job_id,
        title=f"{request.topic} (Test Fixture)",
        target_duration_sec=request.target_duration or 540,
        mood_arc=[Mood.curious, Mood.tense, Mood.revelatory, Mood.calm, Mood.hopeful],
        theme_manifest=ThemeManifest(
            theme_id=f"{request.topic.lower().replace(' ', '-')}-test-{job_id}",
            topic_mood="clinical-curious",
            color_system=ColorSystem(),
            typography=Typography(),
            motion_language=MotionLanguage(),
        ),
        hook_cadence=HookCadence(
            open_loops=[
                OpenLoop(
                    loop_id="L1",
                    tease_line="There's a 2-minute brain hack that makes procrastination impossible.",
                    tease_at_sec=0.0,
                    payoff_line="The 2-Minute Initiation Protocol. Here's how it works.",
                    payoff_at_sec=450.0,
                    visual_tension=VisualTension(
                        tease_scene="S01",
                        escalation_scenes=["S02", "S03", "S04", "S05"],
                        payoff_scene="S20",
                    ),
                    intensity_arc=[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                    loop_type="big",
                ),
            ],
            micro_hooks=[
                MicroHook(at_sec=15.0, line="But here's the problem...", visual_snap="text_color_shift"),
            ],
            callback_reference="Why you can't focus (from intro hook)",
            tension_peak_sec=450.0,
        ),
        scenes=[
            Scene(
                scene_id="S01",
                start_sec=0.0,
                duration_sec=15.0,
                hook_role=HookRole.tease,
                visual_intensity=0.8,
                keyframes=[
                    Keyframe(at_sec=0.0, visual_action="text_slam", element="hero_title"),
                    Keyframe(at_sec=5.0, visual_action="particle_burst", element="particle_field"),
                ],
                narration="There's a 2-minute brain hack that makes procrastination impossible.",
                mood=Mood.curious,
                pacing=Pacing.fast,
                visual_keywords=["brain", "focus"],
                animation_trigger="QuestionBomb",
                color_grade=ColorGrade.cool_blue,
                beat_sync_intensity=0.6,
                text_overlay=TextOverlay(text="Why You Procrastinate", style="title_reveal", position="center"),
                layout_family=LayoutFamily.center_hero,
            ),
            Scene(
                scene_id="S02",
                start_sec=15.0,
                duration_sec=20.0,
                hook_role=HookRole.escalation,
                visual_intensity=0.4,
                keyframes=[
                    Keyframe(at_sec=0.0, visual_action="data_enter", element="stat_counter"),
                ],
                narration="One in five adults are chronic procrastinators.",
                mood=Mood.tense,
                pacing=Pacing.medium,
                visual_keywords=["statistics"],
                animation_trigger="StatShock",
                color_grade=ColorGrade.high_contrast_mono,
                layout_family=LayoutFamily.data_dominant,
            ),
            Scene(
                scene_id="S03",
                start_sec=35.0,
                duration_sec=20.0,
                hook_role=HookRole.escalation,
                visual_intensity=0.5,
                keyframes=[
                    Keyframe(at_sec=0.0, visual_action="overlay_pulse", element="brain_scan"),
                ],
                narration="It's not laziness. It's your brain.",
                mood=Mood.tense,
                pacing=Pacing.medium,
                visual_keywords=["brain scan"],
                animation_trigger="BrainSVG",
                color_grade=ColorGrade.deep_purple,
                layout_family=LayoutFamily.split_screen,
            ),
            Scene(
                scene_id="S20",
                start_sec=450.0,
                duration_sec=20.0,
                hook_role=HookRole.payoff,
                visual_intensity=1.0,
                keyframes=[
                    Keyframe(at_sec=0.0, visual_action="text_slam", element="hero_title"),
                ],
                narration="The 2-Minute Initiation Protocol. Here's how it works.",
                mood=Mood.euphoric,
                pacing=Pacing.fast,
                visual_keywords=["protocol"],
                animation_trigger="StepCard",
                color_grade=ColorGrade.warm_gold,
                layout_family=LayoutFamily.overlay_heavy,
            ),
        ],
    )


# ═══════════════════════════════════════════════════════════════════════════
# STANDALONE TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
