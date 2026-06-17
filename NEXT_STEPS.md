# CORTEX RENDER — Next Steps for Next AI

> Prioritized task list. Start from the top. Do not skip steps unless explicitly instructed.

---

## 🔴 CRITICAL: Hook Cadence Integration (Start Here)

These are the most important missing pieces. The entire project depends on this.

### Task 1: Extend Data Models
**File:** `app/models.py`

- [ ] Add `HookRole` enum: `tease`, `escalation`, `payoff`, `rest`, `callback`
- [ ] Add `Keyframe` model: `at_sec: float`, `visual_action: str`, `element: str`, `description: Optional[str]`
- [ ] Add `MicroHook` model: `at_sec: float`, `line: str`, `visual_snap: str`
- [ ] Add `OpenLoop` model: `loop_id: str`, `tease_line: str`, `tease_at_sec: float`, `payoff_line: str`, `payoff_at_sec: float`, `visual_tension: dict`, `intensity_arc: List[float]`
- [ ] Add `HookCadence` model: `open_loops: List[OpenLoop]`, `micro_hooks: List[MicroHook]`, `callback_reference: str`
- [ ] Add `hook_role: HookRole` to `Scene` model
- [ ] Add `visual_intensity: float` to `Scene` model (0.0–1.0, default 0.5)
- [ ] Add `keyframes: List[Keyframe]` to `Scene` model
- [ ] Add `hook_cadence: HookCadence` to `DirectorCut` model
- [ ] Ensure all new fields have sensible defaults so existing tests don't break

### Task 2: Rewrite Groq Prompt for Hook Cadence
**File:** `app/brain.py`

- [ ] Rewrite `PASS2_SYSTEM_PROMPT` to force the LLM to:
  1. Identify 5–7 open loops BEFORE writing scenes
  2. Map tension arc (tease → escalation → payoff → rest)
  3. Assign visual_intensity to each scene
  4. Place micro-hooks at 15–30 sec intervals
  5. Only then generate the scene list
- [ ] Add 2–3 shot examples in the prompt showing the Hook Cadence JSON structure
- [ ] Test the prompt manually with a sample topic and verify the output contains 5–7 open loops
- [ ] Add validation: if the LLM output has <3 open loops, retry with temperature +0.1

### Task 3: Visual Intensity → Beat Sync Mapping
**File:** `app/compositor.py`

- [ ] Add `visual_intensity` parameter to `get_beat_sync_params()`
- [ ] Scale beat sync event magnitude by `visual_intensity` (1.0 = max effect, 0.2 = min effect)
- [ ] Ensure `tease` scenes (intensity 0.8) get more sync events than `rest` scenes (intensity 0.2)
- [ ] Add keyframe event handling: read `scene.keyframes` and generate FFmpeg filters for each `visual_action`

---

## 🟡 HIGH PRIORITY: Real Framer Motion Components

The stubs in `mograph_factory/src/App.tsx` need to become real, beautiful, animated components.

### Task 4: Build Core Foundation Components

- [ ] **ParticleField** — Canvas-based 130+ particle system with drift, twinkle, colors from theme
- [ ] **AmbientOrbit** — 3 colored dots orbiting at different speeds, colors from theme
- [ ] **MeshGradient** — SVG radial gradients with animated drift
- [ ] **GridOverlay** — CSS grid with mask and shift animation
- [ ] **FilmGrain** — CSS noise overlay with frame-shift animation

### Task 5: Build Typography Components

- [ ] **KineticType** — Text reveal with configurable type (word/line/char), stagger, easing
- [ ] **HeroWordReveal** — v3-style headline with word-by-word spring animation
- [ ] **PullQuote** — Elegant quote with decorative lines
- [ ] **DataLabel** — Floating label with value and unit (e.g., "Cognitive Load ↑ 47%")
- [ ] **LiveCounter** — Ticking number animation with spring physics
- [ ] **SubtitleBurn** — Lower-third style text with fade/slide

### Task 6: Build Data Visualization Components

- [ ] **BarRaceChart** — Animated bar chart race (categories re-rank with spring)
- [ ] **MorphDonut** — Donut chart that morphs between segment states
- [ ] **SparkLine** — SVG line graph with draw-on animation
- [ ] **ComparisonBars** — Side-by-side bar comparison with winner highlight
- [ ] **ProgressTaskList** — List with animated progress bars (v3-style)
- [ ] **TimelineFlow** — Horizontal timeline with node pulses and card expansions

### Task 7: Build Brain & Biology Components

- [ ] **BrainSVG** — Animated brain illustration with region labels, pulse rings, active dots
- [ ] **NeuralNetwork** — SVG network graph with node lighting and connection pulses
- [ ] **NeurotransmitterFlow** — Particles flowing through channels
- [ ] **SynapsePulse** — Action potential visualization with firing waves
- [ ] **RegionHighlight** — Specific brain regions glowing sequentially

### Task 8: Build UI & Action Components

- [ ] **FloatingCard** — Data card with bob animation, label/value/sub structure
- [ ] **StepCard** — Numbered step with bounce-in numeral
- [ ] **ActionPill** — CTA pill with pulsing dot
- [ ] **ChecklistGrid** — Protocol checklist with animated check marks
- [ ] **TimerRing** — SVG countdown ring with animated stroke
- [ ] **BeforeAfterFlip** — 3D flip or wipe comparison
- [ ] **MockupDevice** — Phone/browser mockup with animated UI elements

### Task 9: Build Decorative & Transition Components

- [ ] **LightLeakSweep** — Gradient light sweep across screen
- [ ] **FlourishLines** — Diamond + extending lines animation
- [ ] **GlitchText** — Digital glitch text reveal
- [ ] **BadgePulse** — Scene badge with pulsing dot
- [ ] **SceneWatermark** — Persistent brand watermark

**Critical Quality Gate:** Every component must look like `v3.html` when rendered. No shortcuts. No "close enough." If it doesn't match the reference aesthetic, rebuild it.

---

## 🟡 HIGH PRIORITY: Playwright Capture Optimization

### Task 10: Time-Controlled Rendering
**File:** `mograph_factory/scripts/render-clip.js` and React components

- [ ] Implement deterministic frame rendering (not real-time)
- [ ] Add `frameTime` prop to all React components
- [ ] Replace real-time `requestAnimationFrame` with frame-based animation driver
- [ ] Use Playwright `page.clock` or custom time provider
- [ ] Target: 30fps capture at 2× real-time speed (15 seconds of video in 7.5 seconds of capture)

### Task 11: ProRes4444 Output Validation
- [ ] Verify transparent `.mov` files actually have alpha channel
- [ ] Test overlay in FFmpeg: `overlay=format=auto` should blend correctly
- [ ] If alpha is broken, switch to PNG sequence + FFmpeg image2pipe

---

## 🟠 MEDIUM PRIORITY: FFmpeg Compositor Realization

### Task 12: Full Filter Complex Builder
**File:** `app/compositor.py`

- [ ] Implement `build_scene_filtergraph()` with real layer stack (not stub)
- [ ] Handle multiple stock clips with crossfade (`xfade`)
- [ ] Handle motion graphic overlay with alpha (`overlay=format=auto`)
- [ ] Handle text overlay (pre-rendered PNG or `drawtext`)
- [ ] Handle color grading (per-scene `curves` or `eq`)
- [ ] Handle vignette (FFmpeg `vignette` or pre-rendered overlay)
- [ ] Handle scene badge and watermark (`drawtext`)
- [ ] Handle transition handles (1-second padding for crossfades)

### Task 13: No-Repeat Engine
- [ ] Implement global state tracking for transitions, layouts, text zones
- [ ] Add `pick_transition()` with last-4 exclusion queue
- [ ] Add `pick_layout()` with last-3 exclusion queue
- [ ] Add `pick_text_zone()` with last-3 exclusion queue
- [ ] Add color grade rotation (2+ variants per chapter)

### Task 14: Beat Sync Integration
- [ ] Read `beat_grid.json` in scene rendering
- [ ] Nudge scene transitions to nearest beat (±0.15s tolerance)
- [ ] Add zoom burst on strong onsets (energy > 0.7)
- [ ] Add opacity pulse on medium onsets (energy > 0.5)
- [ ] Add particle velocity burst on downbeats

---

## 🟠 MEDIUM PRIORITY: Audio Pipeline Testing

### Task 15: Edge TTS Integration
- [ ] Test `edge_tts` with `en-US-GuyNeural` and `en-GB-SoniaNeural`
- [ ] Add SSML prosody injection (pauses, emphasis)
- [ ] Measure TTS quality and speed (should be <1 sec per sentence)

### Task 16: librosa Beat Analysis
- [ ] Test `librosa.beat.beat_track()` on a 10-minute music stem
- [ ] Verify BPM accuracy and beat timestamp precision
- [ ] Test `librosa.onset.onset_strength()` and onset detection
- [ ] Output validation: ensure `beat_grid.json` is valid and complete

### Task 17: Music Stem Library
- [ ] Create a seed library with 5–10 royalty-free stems per mood/BPM folder
- [ ] Or implement an upload endpoint for user-provided stems
- [ ] Test stem selection by mood matching
- [ ] Test time-stretching with FFmpeg `rubberband` or `atempo` if needed

---

## 🟢 LOW PRIORITY: End-to-End Pipeline & Deployment

### Task 18: Wire All Modules in Orchestrator
**File:** `app/main.py`

- [ ] Replace stub `run_pipeline()` with real module calls:
  1. `brain.generate_directors_cut()`
  2. `asset_manager.fetch_pexels_clips()` (parallel per scene)
  3. `audio_engine.generate_narration()` (parallel per scene)
  4. `audio_engine.select_music_stem()` + `analyze_beats()` + `mix_audio_scene()`
  5. Animation Factory render (parallel batches)
  6. `compositor.render_scene()` (parallel, max 2)
  7. `compositor.concatenate_scenes()`
  8. `compositor.master_final()`
- [ ] Add progress tracking and update `job.progress_percent` after each step
- [ ] Add error handling and retry logic for each step
- [ ] Add timeout handling (total render time should not exceed 20 min)

### Task 19: UI & Frontend
- [ ] Build a minimal HTML/JS frontend for triggering generation
- [ ] Show job progress (poll `/jobs/{id}`)
- [ ] Show Director's Cut preview (timeline cards)
- [ ] Allow download of final video
- [ ] Or build a Gradio interface for simplicity

### Task 20: Hugging Face Spaces Deployment
- [ ] Ensure Dockerfile builds successfully
- [ ] Ensure all secrets are read from environment (not hardcoded)
- [ ] Test `/health` endpoint on HF Space
- [ ] Test `/generate` endpoint on HF Space with a real topic
- [ ] Verify render output is accessible via `/download/{id}`
- [ ] Add a `.github/workflows/ci.yml` for automated testing (optional)

---

## 🟢 LOW PRIORITY: Quality & Validation

### Task 21: Anti-Slideshow Validation
- [ ] Automated check: no scene has <2 animated layers
- [ ] Automated check: no static image > 2 seconds without zoom/pan
- [ ] Automated check: no stock clip > 8 seconds without cut
- [ ] Automated check: ASL (average shot length) target 4–7 seconds
- [ ] Automated check: no repeated transition within 4 scenes
- [ ] Automated check: no repeated layout within 3 scenes
- [ ] Automated check: text is always in motion (reveal, fade, or drift)

### Task 22: Retention Optimization Testing
- [ ] Generate 3 test videos with different topics
- [ ] Manually review each video for dead frames
- [ ] Measure internal scene pacing (keyframe density)
- [ ] Verify hook cadence (5–7 open loops per video)
- [ ] Verify visual intensity curve (tease → escalation → payoff → rest)
- [ ] Verify callback reference at the end

### Task 23: Performance Tuning
- [ ] Measure total render time for 10-minute video
- [ ] Identify slowest phase (likely mograph render or scene compositing)
- [ ] Optimize slowest phase:
  - If mograph: switch to CDP screencastFrame
  - If compositing: reduce filter complexity or use lower CRF for scenes
  - If audio: cache TTS outputs
- [ ] Target: <20 min for 10-min video on HF CPU Space

---

## 🎯 Success Criteria for Phase 1 (Hook Cadence + Models)

Before moving to Phase 3 (Animation Factory), these must be true:

1. [ ] `app/models.py` validates a `DirectorCut` with `hook_cadence` containing 5–7 open loops
2. [ ] `app/brain.py` generates a real `DirectorCut` from Groq with 5–7 open loops, micro-hooks, and keyframes
3. [ ] The generated `DirectorCut` has scenes with varying `hook_role` (tease, escalation, payoff, rest)
4. [ ] `app/compositor.py` reads `visual_intensity` and adjusts beat sync accordingly
5. [ ] At least 3 test `DirectorCut` JSONs are saved to `cache/` for validation

---

## 🎯 Success Criteria for Phase 3 (Animation Factory)

Before moving to Phase 4 (Compositor), these must be true:

1. [ ] `mograph_factory/src/App.tsx` has real components for all 12 archetypes
2. [ ] Each component renders beautifully at 1920×1080 with transparent background
3. [ ] `render-clip.js` successfully captures a 5-second clip in <10 seconds
4. [ ] The captured clip has a valid alpha channel (test in FFmpeg)
5. [ ] At least 5 different component types have been tested end-to-end

---

## 🎯 Success Criteria for Phase 6 (End-to-End)

Before declaring the project complete:

1. [ ] A 10-minute video can be generated from a single API call
2. [ ] The video contains 20–48 scenes with no repeated transitions
3. [ ] Every scene has 3–4 internal keyframes (visual micro-changes)
4. [ ] The video has a clear hook cadence with 5–7 open loops
5. [ ] The visual quality matches or exceeds `v3.html`
6. [ ] Render time is <20 minutes on HF CPU Space
7. [ ] Audio is properly mixed with sidechain ducking and -14 LUFS normalization
8. [ ] The video is downloadable via FastAPI endpoint

---

*Start with Task 1. Do not skip. Quality is non-negotiable.*
