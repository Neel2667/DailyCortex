"""Pydantic models for all JSON schemas in the pipeline."""
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any, List
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

class HookRole(str, Enum):
    """The narrative role of a scene within the hook cadence system."""
    tease = "tease"           # Opens a curiosity loop
    escalation = "escalation"  # Builds tension toward a payoff
    payoff = "payoff"         # Closes a curiosity loop (dopamine release)
    rest = "rest"             # Lets viewer breathe between loops
    callback = "callback"     # References an earlier hook (memory loop)
    bridge = "bridge"         # Connects two chapters/loops

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

# ============== HOOK CADENCE ==============

class Keyframe(BaseModel):
    """An internal visual micro-event within a scene (3-4 per scene)."""
    at_sec: float = Field(..., description="Timestamp within the scene (0 = scene start)")
    visual_action: str = Field(..., description="The visual action: text_slam, data_enter, overlay_pulse, counter_tick, comparison_reveal, particle_burst, color_shift, zoom_in, zoom_out, icon_appear, line_draw, split_open, fade_swap")
    element: str = Field(..., description="The visual element identifier this keyframe acts on")
    description: Optional[str] = Field(default=None, description="Human-readable description for debugging")

class MicroHook(BaseModel):
    """A micro-curiosity gap within a scene (every 15-30 seconds)."""
    at_sec: float = Field(..., description="Absolute video timestamp")
    line: str = Field(..., description="The exact hook line from the narration")
    visual_snap: str = Field(..., description="The visual action that creates the snap: text_color_shift, split_screen_compare, counter_slow_build, pulse_burst, text_zoom_in, glitch_flash, overlay_swap, camera_pan")

class VisualTension(BaseModel):
    """Which scenes build tension and which pay off for this open loop."""
    tease_scene: str = Field(..., description="scene_id that opens the loop")
    escalation_scenes: List[str] = Field(default_factory=list, description="scene_ids that build tension")
    payoff_scene: str = Field(..., description="scene_id that closes the loop")

class OpenLoop(BaseModel):
    """A curiosity gap that spans multiple scenes (medium: 2-3 min, big: 3-4 min)."""
    loop_id: str = Field(..., description="Unique identifier: L1, L2, ...")
    tease_line: str = Field(..., description="The exact question/promise that opens the loop")
    tease_at_sec: float = Field(..., description="Absolute timestamp where loop opens")
    payoff_line: str = Field(..., description="The exact answer/revelation that closes the loop")
    payoff_at_sec: float = Field(..., description="Absolute timestamp where loop closes")
    visual_tension: VisualTension = Field(..., description="Scene mapping for visual escalation")
    intensity_arc: List[float] = Field(default_factory=list, description="Visual intensity values (0.0-1.0) at each escalation scene, rising toward 1.0 at payoff")
    loop_type: str = Field(default="medium", description="micro | medium | big")

class HookCadence(BaseModel):
    """The complete curiosity architecture of the video."""
    open_loops: List[OpenLoop] = Field(..., description="5-7 nested curiosity gaps")
    micro_hooks: List[MicroHook] = Field(default_factory=list, description="15-30 second micro-hooks")
    callback_reference: Optional[str] = Field(default=None, description="The intro hook line referenced at the end (memory loop)")
    tension_peak_sec: float = Field(default=0.0, description="Absolute timestamp of the maximum visual intensity (big payoff)")

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
    
    # Hook Cadence Fields (NEW - Phase 1)
    hook_role: HookRole = Field(default=HookRole.bridge, description="The narrative role of this scene in the hook architecture")
    visual_intensity: float = Field(default=0.5, ge=0.0, le=1.0, description="How visually intense this scene should be (0.0=rest, 0.8=tease, 1.0=payoff)")
    keyframes: List[Keyframe] = Field(default_factory=list, description="3-4 internal visual micro-events within this scene")
    
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
    hook_cadence: HookCadence = Field(..., description="The curiosity architecture that drives retention")
    scenes: list[Scene]

# ============== AUDIO / BEAT ==============

class BeatGrid(BaseModel):
    bpm: float
    beats: list[float]
    onsets: list[float]
    energy: list[float]
    downbeats: list[float] = Field(default_factory=list, description="Strong beat positions for major transitions")

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
