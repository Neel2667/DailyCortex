# CORTEX RENDER — Technical Architecture

> Complete technical specification for the generative cinematic video engine. Read this after `PROJECT_OVERVIEW.md`.

---

## Table of Contents

1. [System Architecture Diagram](#1-system-architecture-diagram)
2. [Data Flow](#2-data-flow)
3. [Module Specifications](#3-module-specifications)
4. [JSON Schemas (Full Reference)](#4-json-schemas-full-reference)
5. [The Animation Factory Pipeline](#5-the-animation-factory-pipeline)
6. [The FFmpeg Compositor Pipeline](#6-the-ffmpeg-compositor-pipeline)
7. [Audio-Reactive Motion Engine](#7-audio-reactive-motion-engine)
8. [Performance Budget](#8-performance-budget)
9. [Deployment Guide](#9-deployment-guide)

---

## 1. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              HUGGING FACE SPACE                          │
│                   (Docker: Ubuntu + Python + Node + FFmpeg)            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
       ┌──────────────┐             │             ┌──────────────┐
       │  USER INPUT  │─────────────┼─────────────▶│   FASTAPI    │
       │ (Topic/Seed) │             │             │  ORCHESTRATOR │
       └──────────────┘             │             └──────┬───────┘
                                    │                    │
                                    │         ┌──────────┴──────────┐
                                    │         │   JOB QUEUE (async)   │
                                    │         └──────────┬──────────┘
                                    │                    │
                                    │                    ▼
                                    │    ┌─────────────────────────────┐
                                    │    │       THE DIRECTOR          │
                                    │    │     (brain.py / Groq API)   │
                                    │    │                             │
                                    │    │  Pass 1: Narration Script   │
                                    │    │  Pass 2: Director's Cut   │
                                    │    │  + Theme Manifest          │
                                    │    │  + Hook Cadence            │
                                    │    └─────────────────────────────┘
                                    │                    │
                                    │                    ▼
                                    │    ┌─────────────────────────────┐
                                    │    │     ASSET ORCHESTRATOR       │
                                    │    │  (asset_manager.py)          │
                                    │    │                              │
                                    │    │  • Pexels API fetch + cache  │
                                    │    │  • User asset library index  │
                                    │    │  • Music stem selection      │
                                    │    └─────────────────────────────┘
                                    │                    │
                                    │                    ▼
                                    │    ┌─────────────────────────────┐
                                    │    │      AUDIO ENGINE            │
                                    │    │  (audio_engine.py)            │
                                    │    │                              │
                                    │    │  • edge-tts narration        │
                                    │    │  • librosa beat analysis     │
                                    │    │  • Music stem mixing         │
                                    │    │  • SFX generation            │
                                    │    │  • Audio mastering           │
                                    │    └─────────────────────────────┘
                                    │                    │
                                    │                    ▼
                                    │    ┌─────────────────────────────┐
                                    │    │   ANIMATION FACTORY          │
                                    │    │  (mograph_factory/)          │
                                    │    │                              │
                                    │    │  • React + Framer Motion     │
                                    │    │  • Playwright headless       │
                                    │    │  • CDP screenshot capture    │
                                    │    │  • FFmpeg ProRes4444 pipe    │
                                    │    └─────────────────────────────┘
                                    │                    │
                                    │                    ▼
                                    │    ┌─────────────────────────────┐
                                    │    │    GENERATIVE COMPOSITOR     │
                                    │    │  (compositor.py / FFmpeg)     │
                                    │    │                              │
                                    │    │  • Stochastic edit rules     │
                                    │    │  • Layer stack assembly      │
                                    │    │  • Cinematic transitions     │
                                    │    │  • Color grading / LUTs      │
                                    │    │  • Beat-sync motion          │
                                    │    │  • Audio mux + loudnorm      │
                                    │    └─────────────────────────────┘
                                    │                    │
                                    │                    ▼
                                    │    ┌─────────────────────────────┐
                                    │    │      FINAL MASTER            │
                                    │    │  (H.264 1080p30 / AAC)       │
                                    │    └─────────────────────────────┘
                                    │
                                    ▼
                           ┌─────────────────────┐
                           │   STATIC FILE SERVE  │
                           │   (FastAPI /videos)  │
                           └─────────────────────┘
```

---

## 2. Data Flow

```
Step 1: Topic Ingestion
  User POST /generate { topic: "Why You Procrastinate", target_duration: 540 }
  → FastAPI creates Job (uuid) in memory store
  → Background task triggers pipeline

Step 2: The Director (Groq API — 2 Passes)
  Pass 1: Generate 1400-1500 word narration script
  Pass 2: Generate Director's Cut JSON + Theme Manifest + Hook Cadence

Step 3: Asset Procurement (Parallel)
  → Pexels API fetch: 3 clips per scene (cached by keyword hash)
  → edge-tts: generate narration WAV per scene (with SSML prosody)
  → Music stem selection: pick from library by mood/BPM
  → User asset library: index available images/clips/SVGs

Step 4: Audio Analysis
  → librosa: extract BPM, beat timestamps, onset energy
  → Produce beat_grid.json
  → Mix narration + music (sidechain ducking) + SFX
  → Apply loudnorm (-14 LUFS target)

Step 5: Animation Factory (Parallel batches)
  → For each scene's motion graphic component:
    - React App receives props (theme, data, duration, componentId)
    - Playwright opens headless Chromium (1920x1080, 30fps)
    - CDP captures screenshots at 30fps
    - Screenshots piped to FFmpeg stdin
    - Encodes to ProRes4444 with alpha (yuva444p10le)
  → Batch: 4 parallel renders at a time

Step 6: Generative Compositor (Parallel scenes)
  → For each scene:
    - Select transition (weighted pool, no-repeat-within-4)
    - Select layout family (no-repeat-within-3)
    - Select color grade (rotate within chapter)
    - Assemble layer stack via FFmpeg filter_complex:
      * Background stock footage (Ken Burns zoompan)
      * Crossfade multiple clips if needed
      * Overlay motion graphic clip (with alpha)
      * Overlay text (rendered WebP/PNG or drawtext)
      * Apply color grade (eq, curves, or lut3d)
      * Apply vignette + grain overlay
      * Burn scene badge + watermark
    - Beat sync: nudge cut timing to nearest beat if intensity > 0.4
    - Beat sync: pulse zoom/opacity on strong onsets

Step 7: Scene Concatenation
  → FFmpeg concat demuxer (no re-encode)
  → Produce intermediate video

Step 8: Final Mastering
  → Merge intermediate video with mastered audio
  → Apply final color pass (if needed)
  → Encode H.264 with libx264, medium preset, CRF 18
  → Apply faststart for web streaming
  → Store in /data/renders/{job_id}_final.mp4

Step 9: Serve
  → FastAPI /download/{job_id} serves the MP4
  → Job status updated to completed
```

---

## 3. Module Specifications

### 3.1 app/main.py — FastAPI Orchestrator

**Responsibilities:**
- HTTP API surface
- Job lifecycle management (in-memory store, replace with Redis for production)
- Background task dispatch (`asyncio.create_task` or `BackgroundTasks`)
- Static file serving for rendered videos
- Health checks and progress polling

**Endpoints:**
| Endpoint | Method | Input | Output | Async |
|----------|--------|-------|--------|-------|
| `/` | GET | — | JSON health | No |
| `/generate` | POST | `GenerateRequest` | `GenerationJob` | Yes (background) |
| `/jobs/{id}` | GET | job_id | `GenerationJob` | No |
| `/directors-cut/{id}` | GET | job_id | `DirectorCut` | No |
| `/preview-scene/{id}/{scene}` | GET | job_id, scene_id | MP4/PNG | No |
| `/download/{id}` | GET | job_id | MP4 (file download) | No |
| `/health` | GET | — | health JSON | No |

**Job Status Enum:**
```python
class JobStatus(str, Enum):
    queued = "queued"          # Job received, waiting
    running = "running"        # Pipeline started
    brain_active = "brain_active"      # Groq script generation
    assets_fetching = "assets_fetching" # Pexels + TTS + music
    mograph_rendering = "mograph_rendering" # Animation Factory
    audio_mixing = "audio_mixing"      # Beat analysis + mixing
    compositing = "compositing"        # FFmpeg scene assembly
    mastering = "mastering"            # Final encode + loudnorm
    completed = "completed"              # Ready for download
    failed = "failed"                  # Error logged
```

### 3.2 app/config.py — Settings & Paths

**Key Configuration:**
```python
class Settings(BaseSettings):
    groq_api_key: str                    # Required for Director
    pexels_api_key: str                  # Required for stock footage
    workspace: Path = Path("/app")
    data_dir: Path = Path("/data")     # HF Space persistent storage
    cache_dir: Path = Path("/data/cache")
    render_dir: Path = Path("/data/renders")
    asset_dir: Path = Path("/app/assets")
    mograph_factory_dir: Path = Path("/app/mograph_factory")
    target_resolution: tuple = (1920, 1080)
    target_fps: int = 30
    target_bitrate: str = "8M"
    tts_voice: str = "en-US-GuyNeural"
    target_lufs: float = -14.0
    max_parallel_scenes: int = 2       # HF CPU spaces: 2 vCPU
    max_parallel_mograph_renders: int = 4
    target_render_multiplier: float = 2.0  # 10min video in <20min
    music_library_path: Path = Path("/data/music")
    sfx_library_path: Path = Path("/data/sfx")
```

**HF Spaces Specifics:**
- Free CPU spaces: ~2 vCPU, 16GB RAM, no GPU
- Persistent writable directory: `/data`
- Docker port: 7860 (required by HF Spaces)
- Secrets managed via HF Space Settings → Secrets

### 3.3 app/models.py — Pydantic Schemas

This is the **single source of truth** for all JSON data structures. The entire pipeline communicates via these models.

**Core Models:**
- `GenerateRequest` — User input to start generation
- `GenerationJob` — Job state + progress tracking
- `DirectorCut` — The complete shot-list generated by Groq
- `ThemeManifest` — Unique visual identity per video
- `ColorSystem` — Hex palette for the video
- `Typography` — Font stack
- `MotionLanguage` — Easing curves, particle density, etc.
- `Scene` — Single shot (10–45 sec)
- `TextOverlay` — Typography specs per scene
- `BeatGrid` — librosa output (BPM, beats, onsets, energy)
- `AudioMixPlan` — Music stem selection + TTS + mixing params
- `SceneAssetManifest` — Downloaded/generated assets for a scene

**Critical: The `Scene` model must be extended for the Hook Cadence System.** Add:
- `hook_role: Literal["tease", "escalation", "payoff", "rest", "callback"]`
- `visual_intensity: float (0.0–1.0)`
- `micro_hooks: List[MicroHook]` with `{at_sec: float, visual_action: str, element: str}`
- `keyframes: List[Keyframe]` with `{at_sec: float, visual_action: str, element: str}`

**Critical: The `DirectorCut` model must include:**
- `hook_cadence: HookCadence` with `open_loops: List[OpenLoop]` and `callback_reference: str`

### 3.4 app/brain.py — The Director (Groq LLM)

**Two-Pass Generation:**

**Pass 1: Narration Script**
- System prompt: senior documentary scriptwriter, 140–160 WPM, 18–34 audience
- Requirements: cinematic pacing, SSML prosody markers (`[PAUSE: 0.5s]`, `[EMPHASIS]`), section timestamps `[SECTION: HH:MM:SS]`
- Output: raw spoken-word text, 1200–1500 words

**Pass 2: Director's Cut + Hook Cadence**
- System prompt: cinematic director AI with strict JSON schema enforcement
- Requirements: 20–48 scenes, 10–45 sec each, Hook Cadence with 5–7 open loops, Theme Manifest, archetype rotation, layout diversity
- Output: valid JSON matching `DirectorCut` Pydantic model
- `response_format: {"type": "json_object"}` (Groq supports this)

**Groq Model:** `llama-3.3-70b-versatile` (fast, cheap, good JSON adherence)

**Temperature:** Pass 1 = 0.75 (creative), Pass 2 = 0.65 (structured)

**Extension Needed:** The Pass 2 prompt must be rewritten to force the Hook Cadence structure BEFORE generating scenes. The LLM must:
1. Identify 5–7 open loops (tease line + payoff line + timestamp targets)
2. Map the tension arc (escalation scenes vs. payoff scenes)
3. Assign `hook_role` and `visual_intensity` to each scene
4. Place micro-hooks at 15–30 sec intervals within scenes
5. Only THEN generate the scene list with narration, visual keywords, and archetypes

### 3.5 app/asset_manager.py — Asset Orchestrator

**Pexels Integration:**
- API: `https://api.pexels.com/videos/search`
- Parameters: `query`, `per_page=3`, `orientation=landscape`, `size=large`
- Cache: `cache_dir / pexels / {keyword_hash} / {index}_{clip_id}.mp4`
- TTL: 7 days (or keep until disk pressure)
- Hash: SHA256 of sorted keywords, first 16 chars

**User Asset Library:**
- Mounted at `assets/images/`, `assets/clips/`, `assets/svgs/`
- Indexed at boot: glob all files, build lookup table by category
- No automatic generation — only user-provided high-quality assets

**Music Stem Selection:**
- Library: `music_library_path / {mood} / {bpm} /`
- Files: `.mp3`, `.wav`
- Simple heuristic: random selection from matching mood folder
- Production: parse BPM from filename or ID3 tags

### 3.6 app/audio_engine.py — Audio Production

**Edge TTS:**
- Library: `edge_tts` Python package
- Voices: `en-US-GuyNeural` (default), `en-GB-SoniaNeural` (alternative)
- SSML injection: `<break time="500ms"/>`, `<prosody pitch="+10%">...</prosody>`
- Output: WAV or MP3 per scene

**Beat Analysis:**
- Library: `librosa`
- Functions: `librosa.beat.beat_track()`, `librosa.onset.onset_strength()`, `librosa.onset.onset_detect()`
- Output: `BeatGrid` model (BPM, beat timestamps, onset timestamps, energy levels)

**Audio Mixing:**
- Tool: FFmpeg `filter_complex`
- Sidechain ducking: `sidechaincompressor` with `threshold=-30dB`, `ratio=8`, `attack=50ms`, `release=200ms`
- Music duck target: -18dB during narration, -24dB during speech peaks
- Final mastering: `loudnorm=I=-14:TP=-1.5:LRA=11`

**SFX Generation:**
- Simple generated tones: `sine=frequency={freq}:duration={dur}` via FFmpeg lavfi
- Curated mini-library: `sfx/` directory with impact, whoosh, riser, ambient files
- Triggered by transition types and key narrative beats

### 3.7 app/compositor.py — The Generative Compositor

**The Heart of the Engine.**

**Input per Scene:**
- `Scene` JSON (archetype, layout, color grade, duration, hook role, visual intensity)
- `stock_paths`: List of Pexels clips (max 2 per scene, 8 sec max per clip)
- `mograph_path`: Transparent ProRes4444 clip from Animation Factory
- `text_overlay_path`: Pre-rendered text overlay PNG/WebP with alpha
- `beat_grid`: Beat timestamps for sync
- `transition_in`: From previous scene
- `transition_out`: To next scene

**Layer Stack (Bottom to Top):**
```
Z0: Background stock footage (Pexels clip, Ken Burns zoompan)
Z1: Background effects (crossfade, mesh drift, or second clip)
Z2: Persistent foundation (particles + orbits + grid + grain) — pre-rendered or FFmpeg overlays
Z3: Scene mograph (BrainSVG, chart, etc.) — transparent overlay
Z4: Text overlay (kinetic typography) — pre-rendered or drawtext
Z5: Decorative / transition (light leak, flourishes) — pre-rendered
Z6: Vignette + color grade (FFmpeg eq, curves, lut3d)
Z7: Persistent UI (scene badge, watermark, progress bar) — pre-rendered
```

**FFmpeg Filter Complex Strategy:**
- Use `filter_complex` for all compositing in a single pass
- `zoompan` for Ken Burns on still images or slow footage
- `overlay` for alpha channel compositing (requires `format=auto` or `format=yuv420`)
- `xfade` or `gltransition` for crossfades between clips
- `eq` + `curves` for color grading per scene
- `vignette` filter (or pre-rendered overlay)
- `drawtext` for simple text, pre-rendered images for complex kinetic typography
- `fade` for opacity pulsing on beat sync
- `setpts` for speed adjustments (subtle 0.95–1.05x to match beat BPM)

**No-Repeat Engine:**
- Global state: `_used_transitions` (last 4), `_used_layouts` (last 3), `_used_text_zones` (last 3)
- `pick_transition()`: weighted pool excluding last 4
- `pick_layout()`: pool excluding last 3
- `pick_text_zone()`: pool excluding last 3
- `pick_color_grade()`: rotate through 2+ variants per chapter

**Beat Sync Engine:**
- Read `beat_grid.json`
- For each scene transition: find nearest beat timestamp, nudge scene duration ±0.15s to align
- For strong onsets (energy > 0.7) within a scene: add `zoompan` velocity burst or `fade` opacity pulse
- For downbeats: trigger text reveal start or particle burst

**Scene Rendering (Parallel):**
- Each scene is a self-contained FFmpeg process
- `ProcessPoolExecutor` or `asyncio.gather` with semaphore (max 2 concurrent for HF CPU)
- Each scene outputs: `cache_dir / {job_id} / scene_{scene_id}.mp4`

**Concatenation:**
- FFmpeg `concat` demuxer with `-c copy` (no re-encode)
- List file: `file 'path/to/scene1.mp4'` per line
- Concatenates all scene segments into intermediate video

**Final Mastering:**
- Merge intermediate video with mastered audio (narration + music + SFX)
- `loudnorm` audio filter
- `libx264` video encode, `-preset medium`, `-crf 18`, `-pix_fmt yuv420p`
- `-movflags +faststart` for web streaming
- Output: `render_dir / {job_id}_final.mp4`

---

## 4. JSON Schemas (Full Reference)

### 4.1 GenerateRequest
```json
{
  "topic": "Why You Procrastinate",
  "target_duration": 540,
  "style_bias": "cinematic documentary, high motion density, no stock-photo feel",
  "mood_override": "curious",
  "seed": 42
}
```

### 4.2 DirectorCut (Pending Hook Cadence Extension)
```json
{
  "video_id": "uuid-12-chars",
  "title": "Why You Procrastinate (And the 2-Minute Fix)",
  "target_duration_sec": 540,
  "mood_arc": ["curious", "tense", "revelatory", "calm", "hopeful"],
  "theme_manifest": {
    "theme_id": "procrastination-2026-uuid",
    "topic_mood": "clinical-curious",
    "color_system": {
      "void": "#0a0e27",
      "primary": "#14b8a6",
      "secondary": "#f472b6",
      "tertiary": "#818cf8",
      "accent": "#fbbf24",
      "text": "#f4f4f5",
      "text_dim": "#a1a1aa"
    },
    "typography": {
      "headline": "Space Grotesk",
      "body": "Inter",
      "accent_font": "Fraunces Italic"
    },
    "motion_language": {
      "easing": "cubic-bezier(0.16, 1, 0.3, 1)",
      "stagger_base": 0.15,
      "particle_density": 130,
      "grid_opacity": 0.025,
      "grain_intensity": 0.06
    }
  },
  "hook_cadence": {
    "open_loops": [
      {
        "loop_id": "L1",
        "tease_line": "There's a 2-minute brain hack that makes procrastination impossible.",
        "tease_at_sec": 0,
        "payoff_line": "The 2-Minute Initiation Protocol. Here's how it works.",
        "payoff_at_sec": 450,
        "visual_tension": {
          "tease_scene": "S01",
          "escalation_scenes": ["S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09", "S10", "S11", "S12"],
          "payoff_scene": "S22"
        },
        "intensity_arc": [0.2, 0.3, 0.4, 0.3, 0.5, 0.4, 0.6, 0.5, 0.7, 0.6, 0.8, 0.9, 1.0]
      }
    ],
    "micro_hooks": [
      {"at_sec": 15, "line": "But here's the problem...", "visual_snap": "text_color_shift"},
      {"at_sec": 85, "line": "Your brain doesn't know the difference.", "visual_snap": "split_screen_compare"}
    ],
    "callback_reference": "Why you can't focus (from intro hook)"
  },
  "scenes": [
    {
      "scene_id": "S01",
      "start_sec": 0,
      "duration_sec": 15,
      "hook_role": "tease",
      "visual_intensity": 0.8,
      "narration": "There's a 2-minute brain hack that makes procrastination impossible.",
      "mood": "curious",
      "pacing": "fast",
      "visual_keywords": ["brain scan", "neural network", "focus"],
      "animation_trigger": "QuestionBomb",
      "color_grade": "cool_blue",
      "beat_sync_intensity": 0.6,
      "b_roll_strategy": "single",
      "text_overlay": {
        "text": "Why You Procrastinate",
        "style": "title_reveal",
        "position": "center",
        "accent_words": ["Procrastinate"]
      },
      "transition_out": "light_leak_wipe",
      "layout_family": "center_hero",
      "keyframes": [
        {"at_sec": 0, "visual_action": "text_slam", "element": "hero_title"},
        {"at_sec": 5, "visual_action": "particle_burst", "element": "particle_field"},
        {"at_sec": 10, "visual_action": "fade_in", "element": "subtitle"}
      ]
    }
  ]
}
```

### 4.3 BeatGrid
```json
{
  "bpm": 128.5,
  "beats": [0.0, 0.47, 0.93, 1.40, 1.87, 2.34, ...],
  "onsets": [0.0, 2.34, 4.12, 6.51, ...],
  "energy": [0.2, 0.8, 0.3, 0.9, ...]
}
```

### 4.4 SceneAssetManifest
```json
{
  "scene_id": "S01",
  "stock_clips": ["/data/cache/pexels/abc123/0_12345.mp4"],
  "mograph_clips": ["/data/cache/mograph/s01_question_bomb.mov"],
  "text_overlays": ["/data/cache/text/s01_title.png"],
  "color_grade_lut": "cool_blue",
  "transition_asset": "/data/cache/transitions/light_leak_wipe.mp4"
}
```

### 4.5 AudioMixPlan
```json
{
  "narration_path": "/data/cache/tts/s01_narration.wav",
  "music_path": "/data/music/curious/128/stem_curious_128_03.mp3",
  "music_start_offset": 0.0,
  "music_duck_db": -24.0,
  "sfx_events": [
    {"at_sec": 0, "sfx_path": "/data/sfx/impact_01.wav", "volume": -10},
    {"at_sec": 14, "sfx_path": "/data/sfx/whoosh_02.wav", "volume": -12}
  ],
  "beat_grid": {
    "bpm": 128.5,
    "beats": [0.0, 0.47, ...],
    "onsets": [0.0, 2.34, ...],
    "energy": [0.2, 0.8, ...]
  }
}
```

### 4.6 GenerationJob
```json
{
  "job_id": "abc123def456",
  "topic": "Why You Procrastinate",
  "target_duration": 540,
  "status": "completed",
  "created_at": "2026-06-17T12:00:00Z",
  "progress_percent": 100.0,
  "directors_cut": { ... },
  "theme_manifest": { ... },
  "audio_mix_plan": { ... },
  "scene_manifests": [ ... ],
  "output_path": "/data/renders/abc123def456_final.mp4",
  "completed_at": "2026-06-17T12:20:00Z",
  "error": null
}
```

---

## 5. The Animation Factory Pipeline

### 5.1 React App Architecture

The Animation Factory is a **standalone React app** that renders a single component at a time based on injected props.

**Entry Point:** `mograph_factory/index.html` (1920×1080, transparent background)
**Runtime:** `mograph_factory/src/main.tsx` mounts React to `#root`
**Component Registry:** `mograph_factory/src/App.tsx` maps `componentId` to React components
**Props Injection:** `window.CORTEX_RENDER` object set by the capture script via Playwright

**Props Structure:**
```typescript
interface CortexRenderProps {
  componentId: string;      // e.g., "BrainSVG", "QuestionBomb"
  props: any;                 // Component-specific data
  durationMs: number;         // How long to render (e.g., 5000)
  width: number;              // 1920
  height: number;             // 1080
  fps: number;                // 30
  theme: ThemeManifest;       // Colors, fonts, easing
}
```

### 5.2 Playwright Capture Pipeline

**Script:** `mograph_factory/scripts/render-clip.js`

**Process:**
1. Parse CLI args: `--props` (JSON file), `--output` (video path), `--duration` (ms)
2. Start Vite dev server on `127.0.0.1:3456`
3. Launch Chromium headless (`--no-sandbox`, `--disable-gpu`, `--disable-background-timer-throttling`)
4. Navigate to dev server URL
5. Inject `window.CORTEX_RENDER` via `page.evaluate()`
6. Wait for React mount (300ms)
7. **Frame Capture Loop:**
   - For each frame (0 to durationMs, step 1000/30):
   - Advance browser timers via CDP `Runtime.evaluate` (tricky — Playwright's `clock` API may be better)
   - Take screenshot: `page.screenshot({ type: 'png', omitBackground: true })`
   - Write PNG buffer to FFmpeg stdin
8. **FFmpeg Pipe:**
   - Input: raw RGBA, 1920×1080, 30fps, from stdin
   - Codec: `prores_ks` with `profile:v 4444` (ProRes 4444 with alpha)
   - Pixel format: `yuva444p10le`
   - Output: transparent `.mov` file

**Optimization Challenges:**
- Playwright's `page.screenshot()` is slow (~50–100ms per frame). At 30fps, this is 3× real-time.
- **Alternative:** Chrome DevTools Protocol `Page.screencastFrame` is faster but less reliable in headless.
- **Alternative:** Use Chrome's `--headless=old` + `--dump-dom` is not helpful here.
- **Alternative:** Use `chrome-remote-interface` with CDP `Page.startScreencast` + `Page.screencastFrame` events. This captures frames directly from the browser compositor at native speed. This is the ideal approach for Phase 3 optimization.
- **Current approach (Phase 0):** Screenshot loop is acceptable for 20–30 clips × 5–15 seconds = ~100–150 seconds total capture time. Acceptable for 20-minute total render budget.

**Frame Advancement:**
- The hardest problem: Framer Motion uses `requestAnimationFrame` and real-time timers. In a headless browser, we need to "tick" time forward deterministically.
- **Strategy A:** Use Playwright's `page.clock` API (if available in version) to fast-forward time.
- **Strategy B:** Override `Date.now()`, `performance.now()`, and `requestAnimationFrame` in the page context to be frame-count based.
- **Strategy C:** Use `client.send('Animation.setPlaybackRate', { playbackRate: 0 })` to pause CSS animations, then manually advance.
- **Strategy D (Recommended):** Render the React component in a time-controlled environment. Instead of using real-time Framer Motion `animate()`, use `useAnimationFrame` with a custom time provider that advances by 33.33ms per frame. This is the most reliable approach for deterministic video rendering.

**Implementation D:**
```typescript
// In the React component, replace Framer Motion's real-time animations
// with a frame-controlled time provider:
const [frameTime, setFrameTime] = useState(0);
useEffect(() => {
  const interval = setInterval(() => {
    setFrameTime(t => t + 33.333); // 30fps
  }, 0); // Run as fast as possible
  return () => clearInterval(interval);
}, []);

// Then use frameTime as the animation driver instead of real-time
```
This is a significant architectural decision for the Animation Factory. The components should be designed to accept an optional `frameTime` prop that overrides real-time behavior.

---

## 6. The FFmpeg Compositor Pipeline

### 6.1 Single-Scene Filter Complex Example

```bash
ffmpeg -y \
  -i stock_clip_1.mp4 \
  -i stock_clip_2.mp4 \
  -i mograph_overlay.mov \
  -i text_overlay.png \
  -filter_complex "
    [0:v]zoompan=z='min(zoom+0.001,1.15)':d=450:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'[v0];
    [1:v]trim=0:10,setpts=PTS-STARTPTS[v1];
    [v0][v1]xfade=transition=fade:duration=1.0:offset=14.0[vstock];
    [vstock][2:v]overlay=format=auto:enable='between(t,0,15)'[v1];
    [v1][3:v]overlay=format=auto:enable='between(t,0,15)'[v2];
    [v2]eq=saturation=1.2:contrast=1.05:gamma=1.1,
         curves=r='0/0 0.5/0.4 1/1':g='0/0 0.5/0.5 1/1':b='0/0 0.5/0.7 1/1',
         vignette=PI/4[v3];
    [v3]drawtext=text='S01':fontsize=24:fontcolor=0x14b8a6:
         x=22:y=22:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf[vbadge];
    [vbadge]drawtext=text='Why You Procrastinate':fontsize=48:fontcolor=0xf4f4f5:
         x=(w-text_w)/2:y=(h-text_h)/2:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf[output]
  " \
  -map "[output]" -t 15 -c:v libx264 -preset veryfast -crf 23 -pix_fmt yuv420p \
  scene_S01.mp4
```

### 6.2 Beat Sync Parameter Injection

For a scene with `beat_sync_intensity=0.6`, the filter graph is enhanced:

```
[v3]zoompan=z='if(between(t,2.34,2.40),1.05,1.0)':d=1[vbeat]
```
This adds a 6-frame (0.2s) zoom burst at the onset timestamp 2.34s.

For opacity pulsing:
```
[v3]fade=t=in:st=2.34:d=0.1:alpha=0.15[vbeat]
```
This adds a brief opacity spike.

These are generated programmatically by reading the `beat_grid.json` and the scene's `start_sec` and `duration_sec`.

### 6.3 Transition Implementation

For `xfade` transitions between scenes (during concatenation):
```bash
# Instead of concat demuxer, use xfade for transitions:
ffmpeg -y \
  -i scene1.mp4 -i scene2.mp4 -i scene3.mp4 \
  -filter_complex "
    [0:v][1:v]xfade=transition=lightleak:duration=1.0:offset=14.0[v01];
    [v01][2:v]xfade=transition=zoomin:duration=1.0:offset=29.0[output]
  " \
  -map "[output]" -c:v libx264 -preset veryfast -crf 23 intermediate.mp4
```

However, xfade requires scenes to have extra padding for the transition duration. The Compositor must add 1 second of "handle" to each scene (extra footage before start and after end) so the crossfade has material to work with.

**Alternative for transitions:** Use `gltransition` (OpenGL GPU-accelerated transitions). Requires FFmpeg built with `--enable-libgltransition` or using the `gltransition` standalone tool. On CPU-only HF Spaces, this is not available. Stick to `xfade` or pre-rendered transition overlays.

**Pre-rendered transitions:** The Animation Factory can render 1-second transition overlays (light leak sweeps, directional wipes, etc.) as transparent ProRes clips, and the Compositor uses `overlay` to composite them during the overlap between scenes.

---

## 7. Audio-Reactive Motion Engine

### 7.1 Beat Grid Analysis

```python
import librosa

y, sr = librosa.load(audio_path, sr=None, mono=True)
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beat_frames, sr=sr)

onset_env = librosa.onset.onset_strength(y=y, sr=sr)
onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
onset_times = librosa.frames_to_time(onsets, sr=sr)
onset_energies = onset_env[onsets]

# Filter strong onsets (top 20% energy)
strong_onset_threshold = np.percentile(onset_energies, 80)
strong_onsets = onset_times[onset_energies > strong_onset_threshold]
```

### 7.2 Visual Beat Sync Mapping

```python
def get_beat_sync_params(beat_grid, scene_start, scene_duration, intensity):
    """Returns a list of (timestamp, action, magnitude) for the scene."""
    scene_end = scene_start + scene_duration
    sync_events = []
    
    # Find beats within this scene
    scene_beats = [b for b in beat_grid.beats if scene_start <= b < scene_end]
    
    for beat in scene_beats:
        # Find nearest onset energy
        nearest_onset_idx = min(range(len(beat_grid.onsets)), 
                               key=lambda i: abs(beat_grid.onsets[i] - beat))
        energy = beat_grid.energy[nearest_onset_idx]
        
        if energy > 0.7 and intensity > 0.5:
            sync_events.append({
                "timestamp": beat,
                "action": "zoom_burst",
                "magnitude": 1.0 + (energy * 0.05 * intensity)  # 1.0 → 1.025
            })
        elif energy > 0.5 and intensity > 0.3:
            sync_events.append({
                "timestamp": beat,
                "action": "opacity_pulse",
                "magnitude": 0.85 + (energy * 0.15 * intensity)  # 0.85 → 1.0
            })
    
    return sync_events
```

### 7.3 FFmpeg Filter Integration

The sync events are converted into FFmpeg `zoompan` or `fade` expressions:

```python
def build_beat_filters(sync_events, base_filter="[v]", output_label="[vbeat]"):
    filters = [base_filter]
    for i, event in enumerate(sync_events):
        if event["action"] == "zoom_burst":
            t = event["timestamp"]
            mag = event["magnitude"]
            filters.append(
                f"zoompan=z='if(between(t,{t},{t+0.2}),{mag},1.0)':d=1"
            )
        elif event["action"] == "opacity_pulse":
            t = event["timestamp"]
            mag = event["magnitude"]
            filters.append(
                f"fade=t=in:st={t}:d=0.1:alpha={mag}"
            )
    return ";".join(filters) + output_label
```

---

## 8. Performance Budget

### Target: 10-Minute Video in <20 Minutes

| Phase | Time Budget | Parallelism | Optimization |
|-------|-------------|-------------|--------------|
| Groq 2-Pass | 60 sec | Sequential | Fast API, cached if retry |
| Pexels Fetch | 30 sec | Async parallel | Cache hits reduce to 0 |
| TTS Generation | 60 sec | Async per scene | edge-tts is fast |
| Music Stem Select | 5 sec | Sequential | Local file lookup |
| Beat Analysis | 15 sec | Sequential | librosa on 10-min audio |
| **Mograph Render** | **120 sec** | **4 parallel** | Screenshot loop, target 30fps capture |
| **Scene Compositing** | **600 sec** | **2 parallel** | FFmpeg filter_complex, veryfast preset |
| Concatenation | 30 sec | Sequential | `-c copy` no re-encode |
| Final Master | 60 sec | Sequential | libx264 medium, crf 18 |
| **Total** | **~970 sec (~16 min)** | | |

### Bottlenecks & Mitigations

| Bottleneck | Mitigation |
|------------|------------|
| Playwright screenshot speed | Switch to CDP `Page.screencastFrame` in Phase 3 |
| FFmpeg CPU encoding | Use `libx264` `-preset veryfast` for scenes, `-preset medium` for final only |
| Memory pressure | Stream FFmpeg, don't buffer entire frames in memory |
| Disk I/O | Use `/data` (SSD on HF Spaces) for temp files |
| Groq rate limits | Implement retry with exponential backoff |
| Pexels rate limits | Cache aggressively, 7-day TTL |

### Scaling Options (Post-Phase 0)

| Scenario | Solution |
|----------|----------|
| Render time > 20 min | External GPU worker (Modal.com, RunPod) triggered from HF |
| Music library empty | Add seed download from Free Music Archive or similar |
| Pexels quality low | Add Pixabay or Videvo as fallback API |
| 2 vCPU insufficient | Upgrade to ZeroGPU or dedicated CPU space |
| Parallel scene limits | Use `asyncio.Semaphore(2)` instead of `ProcessPoolExecutor` |

---

## 9. Deployment Guide

### 9.1 Local Development

```bash
# 1. Clone repo
git clone git@github.com:YOUR_USERNAME/cortex-render.git
cd cortex-render

# 2. Python environment
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Node environment
cd mograph_factory
npm install
npm run build
cd ..

# 4. FFmpeg (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install ffmpeg

# 5. Environment
cp .env.example .env
# Edit .env with GROQ_API_KEY and PEXELS_API_KEY

# 6. Run
uvicorn app.main:app --reload --port 8000

# 7. Test
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Why You Procrastinate", "target_duration": 540}'
```

### 9.2 Hugging Face Spaces Docker Deployment

```bash
# 1. Push to GitHub
git push origin main

# 2. In HF Space settings:
#    - Factory: Docker
#    - Secrets: GROQ_API_KEY, PEXELS_API_KEY

# 3. HF Space will auto-build from Dockerfile
# 4. App available at: https://your-username-cortex-render.hf.space
```

### 9.3 Secrets Required

| Secret | Source | Purpose |
|--------|--------|---------|
| `GROQ_API_KEY` | groq.com | LLM script generation |
| `PEXELS_API_KEY` | pexels.com | Stock footage download |

Optional:
| Secret | Source | Purpose |
|--------|--------|---------|
| `HF_TOKEN` | huggingface.co | Push/pull datasets |
| `AWS_ACCESS_KEY` | aws.amazon.com | External S3 storage for assets |

---

## 10. Version History & Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 0: Foundation** | ✅ COMPLETE | Docker skeleton, FastAPI, Pydantic models, stub pipeline |
| **Phase 1: The Brain** | ⏳ PENDING | Hook Cadence integration into models + Groq prompts |
| **Phase 2: Asset Pipeline** | ⏳ PENDING | Pexels integration test, user asset upload endpoints |
| **Phase 3: Animation Factory** | ⏳ PENDING | Real Framer Motion components (ParticleField, BrainSVG, etc.) |
| **Phase 4: Compositor** | ⏳ PENDING | Full FFmpeg filter_complex, no-repeat engine, beat sync |
| **Phase 5: Audio** | ⏳ PENDING | Edge TTS test, librosa integration, music stem library seed |
| **Phase 6: End-to-End** | ⏳ PENDING | Wire all modules in main.py, test 3 full videos |
| **Phase 7: UI & Deploy** | ⏳ PENDING | React/Gradio UI, HF Space deploy, monitoring |

---

*End of Technical Architecture. Refer to `PROJECT_OVERVIEW.md` for business context and `HOOK_CADENCE.md` for the narrative design system.*
