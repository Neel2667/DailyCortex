"""Pydantic models for all JSON schemas in the pipeline."""
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any
from enum import Enum

# ============== ENUMS ==============

class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    brain_active = "brain_active"
    assets_fetching = "assets_fetching"
    mograph_rendering = "mograph_rendering"
    audio_mixing = "audio_mixing"
    compositing = "compositing"
    mastering = "mastering"
    completed = "completed"
    failed = "failed"

class Mood(str, Enum):
    curious = "curious"
    tense = "tense"
    euphoric = "euphoric"
    calm = "calm"
    mysterious = "mysterious"
    urgent = "urgent"
    hopeful = "hopeful"

class Pacing(str, Enum):
    slow = "slow"
    medium = "medium"
    fast = "fast"
    burst = "burst"

class ColorGrade(str, Enum):
    warm_gold = "warm_gold"
    cool_blue = "cool_blue"
    high_contrast_mono = "high_contrast_mono"
    neural_green = "neural_green"
    clinical_cyan = "clinical_cyan"
    deep_purple = "deep_purple"
    amber_dawn = "amber_dawn"
    midnight = "midnight"

class LayoutFamily(str, Enum):
    center_hero = "center_hero"
    split_screen = "split_screen"
    full_text = "full_text"
    data_dominant = "data_dominant"
    footage_dominant = "footage_dominant"
    overlay_heavy = "overlay_heavy"
    minimal = "minimal"

class TransitionType(str, Enum):
    crossfade = "crossfade"
    light_leak_wipe = "light_leak_wipe"
    directional_wipe = "directional_wipe"
    zoom_in = "zoom_in"
    zoom_out = "zoom_out"
    glitch_skip = "glitch_skip"
    radial_reveal = "radial_reveal"
    slide_left = "slide_left"
    slide_right = "slide_right"
    iris_close = "iris_close"
    motion_blur = "motion_blur"
    dissolve_glow = "dissolve_glow"

# ============== REQUESTS ==============

class GenerateRequest(BaseModel):
    topic: str = Field(..., description="The brain hack topic seed")
    target_duration: Optional[int] = Field(default=540, ge=300, le=900, description="Target duration in seconds (5–15 min)")
    style_bias: Optional[str] = Field(default=None, description="Optional creative direction override")
    mood_override: Optional[Mood] = Field(default=None, description="Force a specific mood arc")
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")

# ============== THEME MANIFEST ==============

class ColorSystem(BaseModel):
    void: str = "#0a0e27"
    primary: str = "#14b8a6"
    secondary: str = "#f472b6"
    tertiary: str = "#818cf8"
    accent: str = "#fbbf24"
    text: str = "#f4f4f5"
    text_dim: str = "#a1a1aa"

class Typography(BaseModel):
    headline: str = "Space Grotesk"
    body: str = "Inter"
    accent_font: str = "Fraunces Italic"

class MotionLanguage(BaseModel):
    easing: str = "cubic-bezier(0.16, 1, 0.3, 1)"
    stagger_base: float = 0.15
    particle_density: int = 130
    grid_opacity: float = 0.025
    grain_intensity: float = 0.06

class ThemeManifest(BaseModel):
    theme_id: str
    topic_mood: str
    color_system: ColorSystem
    typography: Typography
    motion_language: MotionLanguage
    archetype_weights: dict[str, float] = Field(default_factory=dict)

# ============== DIRECTOR'S CUT ==============

class TextOverlay(BaseModel):
    text: str
    style: str = "title_reveal"  # or subtitle_burn, pull_quote, data_label, kicker
    position: str = "center"  # top-left, top-center, top-right, center, bottom-left, bottom-center, bottom-right
    accent_words: list[str] = Field(default_factory=list)

class Scene(BaseModel):
    scene_id: str
    start_sec: float
    duration_sec: float
    narration: str
    mood: Mood
    pacing: Pacing
    visual_keywords: list[str] = Field(default_factory=list)
    animation_trigger: str = "auto"  # component ID from registry
    color_grade: ColorGrade
    beat_sync_intensity: float = Field(ge=0.0, le=1.0, default=0.3)
    b_roll_strategy: Literal["single", "layered", "picture_in_picture"] = "single"
    text_overlay: Optional[TextOverlay] = None
    transition_out: TransitionType | Literal["auto"] = "auto"
    layout_family: LayoutFamily = "center_hero"
    # Generative engine will fill these:
    transition_in: Optional[TransitionType] = None
    selected_stock_clips: list[str] = Field(default_factory=list)
    selected_mograph_components: list[str] = Field(default_factory=list)
    text_anchor_zone: Optional[str] = None
    color_grade_variant: Optional[str] = None

class DirectorCut(BaseModel):
    video_id: str
    title: str
    target_duration_sec: int
    mood_arc: list[Mood]
    theme_manifest: ThemeManifest
    scenes: list[Scene]

# ============== AUDIO / BEAT ==============

class BeatGrid(BaseModel):
    bpm: float
    beats: list[float]
    onsets: list[float]
    energy: list[float]

class AudioMixPlan(BaseModel):
    narration_path: str
    music_path: str
    music_start_offset: float = 0.0
    music_duck_db: float = -24.0
    sfx_events: list[dict[str, Any]] = Field(default_factory=list)
    beat_grid: BeatGrid

# ============== ASSET MANIFEST ==============

class SceneAssetManifest(BaseModel):
    scene_id: str
    stock_clips: list[str] = Field(default_factory=list)
    mograph_clips: list[str] = Field(default_factory=list)
    text_overlays: list[str] = Field(default_factory=list)
    color_grade_lut: Optional[str] = None
    transition_asset: Optional[str] = None

# ============== JOB ==============

class GenerationJob(BaseModel):
    job_id: str
    topic: str
    target_duration: int
    status: JobStatus
    created_at: str
    progress_percent: float = 0.0
    directors_cut: Optional[DirectorCut] = None
    theme_manifest: Optional[ThemeManifest] = None
    audio_mix_plan: Optional[AudioMixPlan] = None
    scene_manifests: Optional[list[SceneAssetManifest]] = None
    output_path: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
