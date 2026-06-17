# Cinematic Brain Hacks Video Engine — System Design v2

> **Quality Target:** Match the density, smoothness, and premium feel of the `v3.html` reference — but as a **generative, non-template hybrid** of stock footage + web-native motion graphics. Every video is a unique film. No two scenes share the same composition.

---

## 1. Core Philosophy: The Generative Engine

We do not use templates. Instead, we define a **vocabulary of visual archetypes** and a **registry of web components**. The Groq "Director" selects from this vocabulary and composes a unique film per topic. The Compositor assembles it with stochastic rules that guarantee zero repetition.

**The Golden Rule:** Every frame has 3+ layers of motion. No dead frames. No repeated transitions. No repeated scene layouts within the same video.

---

## 2. Video Structure: Chapters & Scenes (8–10 Minutes)

To maintain the fast-paced, short-scene density of the reference while hitting 8–10 minutes, we use a **Chapter-Scene hierarchy**:

| Level | Count | Duration | Purpose |
|-------|-------|----------|---------|
| **Video** | 1 | 8–10 min | Complete documentary |
| **Chapters** | 4–6 | 1.5–2.5 min each | Thematic sections (e.g., "The Problem", "The Science", "The Hack", "The Proof", "The Payoff") |
| **Scenes** | 5–8 per chapter | 10–25 sec each | Single visual idea + narration beat |

**Total scenes per video:** 20–48 scenes. Short, punchy, varied.

**Scene Archetypes** (the vocabulary the Director uses):

### A. Hook Archetypes (Openers)
- **Question Bomb** — Provocative question with kinetic typography + particle burst
- **Stat Shock** — Big number reveal with live counter + animated bar chart
- **Story Teaser** — Narrative hook with cinematic footage + text overlay
- **Myth Bust** — "It's not laziness..." style reveal with brain visualization
- **Personal Mirror** — "You are doing X right now" with relatable footage + data cards

### B. Evidence Archetypes (Body)
- **Science Scan** — Brain region SVG with labels, pulse rings, data readouts
- **Study Drop** — Research paper citation with animated chart, confidence intervals
- **Comparison Split** — Side-by-side before/after or A vs B (animated comparison bars)
- **Timeline Flow** — Historical or biological timeline with animated SVG paths
- **Data Infographic** — D3/Canvas charts (bar race, line graph, heatmap, donut morph)
- **Analogy Visual** — Metaphorical animation (e.g., "brain as a traffic control system")
- **Expert Quote** — Pull quote with footage B-roll + elegant text animation
- **Real World Scan** — Fast montage of stock footage with contextual text overlays

### C. Action Archetypes (The Hack)
- **Step Reveal** — Numbered steps with animated cards, timer rings, progress bars
- **Habit Loop** — Circular/cyclical animation showing cue → routine → reward
- **Protocol Grid** — Checklist or protocol with animated check marks and status fills
- **Quick Win** — "2-minute trick" with countdown animation + before/after state flip
- **Tool Showcase** — App/productivity tool interface with animated UI mockups

### D. Payoff Archetypes (Closers)
- **Transformation Summary** — Key takeaways with animated icon grid + text
- **CTA Pulse** — Subscribe/try-it with action pills, flourishes, diamond lines
- **Next Hook** — Tease next video with suspense typography + glitch reveals
- **Credit Roll** — Animated credits with contributor names, sources, music info

**The Director (Groq) composes chapters by selecting archetypes from these pools.** No chapter repeats the same archetype twice. No two consecutive scenes use the same layout family.

---

## 3. The Theme Engine: Unique Identity Per Video

Every video must feel like it has a unique visual identity, not just "the engine's default look." The Director generates a **Theme Manifest** based on the topic's mood.

### Theme Manifest JSON
```json
{
  "theme_id": "dopamine-detox-2026",
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
  },
  "archetype_weights": {
    "question_bomb": 0.8,
    "stat_shock": 0.9,
    "science_scan": 0.7,
    "step_reveal": 0.8,
    "cta_pulse": 0.6
  }
}
```

**Theme Generation Rules:**
- The Director analyzes the topic (e.g., "Dopamine Detox" = clinical/clean/cyan; "Lucid Dreaming" = mystical/purple/gold; "Memory Palaces" = architectural/warm/amber).
- It selects a **color system** from a curated palette bank (16 pre-designed color systems, but the Director can also request custom tints).
- It selects a **motion language** (snappy vs. smooth vs. glitchy vs. organic).
- It biases archetype weights toward what fits the topic (e.g., "The Science of Sleep" weights `science_scan` and `timeline_flow` higher).

---

## 4. The Web Component Registry

The Animation Factory (React + Framer Motion + Playwright) can render any web-native component. We build a registry of **reusable, data-driven components** that accept the Theme Manifest as props and output cinematic motion.

### 4.1 Foundation Layer (Always Present)
These components are rendered once per video or per chapter and used as persistent backgrounds/overlays.

| Component | Tech | Props | Output |
|-----------|------|-------|--------|
| **ParticleField** | Canvas + RAF | `count`, `colors[]`, `speed`, `direction`, `twinkle` | Transparent `.mov` with 130+ drifting particles |
| **AmbientOrbit** | CSS + Framer | `orbits[]`, `colors[]`, `speeds[]` | Transparent `.mov` with 2–4 orbiting dots |
| **MeshGradient** | SVG + SMIL/Framer | `stops[]`, `duration`, `drift` | Background gradient video (can be blended with stock footage) |
| **GridOverlay** | CSS | `size`, `opacity`, `shiftSpeed`, `mask` | Grid lines with vignette mask |
| **FilmGrain** | CSS + SVG noise | `intensity`, `fps` | Grain overlay texture (seamless loop) |
| **Vignette** | CSS radial-gradient | `intensity`, `ellipseRatio` | Static edge darkening (can be FFmpeg `vignette` filter instead) |

### 4.2 Typography & Text Systems
| Component | Tech | Props | Output |
|-----------|------|-------|--------|
| **KineticType** | Framer Motion | `text`, `revealType` (word/line/char), `stagger`, `easing` | Text reveal animation |
| **HeroWordReveal** | Framer Motion | `lines[]`, `stagger`, `accentWords[]` | v3-style headline with word-by-word spring |
| **PullQuote** | Framer Motion + SVG | `quote`, `attribution`, `lineAnimation` | Elegant quote reveal with decorative lines |
| **DataLabel** | CSS + Framer | `label`, `value`, `unit`, `animation` | Floating card label (e.g., "Cognitive Load ↑ 47%") |
| **LiveCounter** | Framer Motion + RAF | `startValue`, `endValue`, `duration`, `format` | Ticking number animation |
| **SubtitleBurn** | Framer Motion | `text`, `duration`, `position` | Lower-third style text overlay |

### 4.3 Data Visualization & Infographics
| Component | Tech | Props | Output |
|-----------|------|-------|--------|
| **BarRaceChart** | React + Framer Motion | `data[]`, `duration`, `theme` | Animated bar chart race (categories re-rank) |
| **MorphDonut** | SVG + Framer Motion | `segments[]`, `transitionDuration` | Donut chart that morphs between states |
| **SparkLine** | SVG + Framer Motion | `data[]`, `strokeColor`, `fillGradient` | Animated line graph with draw-on effect |
| **ComparisonBars** | Framer Motion | `leftLabel`, `rightLabel`, `leftValue`, `rightValue`, `winner` | Side-by-side bar comparison |
| **ProgressTaskList** | Framer Motion | `tasks[]`, `fillDuration`, `stagger` | List with animated progress bars (v3-style) |
| **HeatmapGrid** | Canvas or SVG | `grid[]`, `colors[]`, `pulseSpeed` | Animated heatmap grid |
| **TimelineFlow** | SVG + Framer Motion | `events[]`, `pathStyle`, `nodeAnimation` | Horizontal or vertical timeline with node pulses |

### 4.4 Brain & Biology Visualizations
| Component | Tech | Props | Output |
|-----------|------|-------|--------|
| **BrainSVG** | SVG + SMIL/Framer | `regions[]`, `activeRegions[]`, `pulseRings[]`, `connectionLines[]` | Animated brain illustration with region labels |
| **NeuralNetwork** | SVG + Framer Motion | `nodes[]`, `connections[]`, `pulseSpeed` | Network graph with node lighting + line pulses |
| **NeurotransmitterFlow** | SVG + Framer Motion | `channels[]`, `particles[]`, `direction` | Particles flowing through channels |
| **SynapsePulse** | Canvas + RAF | `synapseCount`, `firingRate`, `colors` | Action potential visualization |
| **RegionHighlight** | SVG + Framer | `brainPath`, `highlightRegions[]`, `glowColor` | Specific brain regions glowing sequentially |

### 4.5 UI & Object Components
| Component | Tech | Props | Output |
|-----------|------|-------|--------|
| **FloatingCard** | Framer Motion | `label`, `value`, `sub`, `position`, `bobSpeed` | v3-style data card with bob animation |
| **StepCard** | Framer Motion | `number`, `title`, `description`, `icon` | Numbered step with bounce-in numeral |
| **ActionPill** | Framer Motion | `text`, `pulse`, `color` | CTA pill with pulsing dot |
| **ChecklistGrid** | Framer Motion | `items[]`, `checkAnimation`, `stagger` | Protocol checklist with animated checks |
| **TimerRing** | SVG + Framer Motion | `duration`, `color`, `countdown` | Animated countdown ring |
| **BeforeAfterFlip** | Framer Motion | `beforeContent`, `afterContent`, `flipTrigger` | 3D flip or wipe comparison |
| **PhotoCarousel** | Framer Motion | `images[]`, `transitionType`, `speed` | Ken Burns crossfade of still images |
| **MockupDevice** | CSS + Framer | `deviceType`, `screenContent`, `interaction` | Phone/browser mockup with animated UI |

### 4.6 Decorative & Transition Elements
| Component | Tech | Props | Output |
|-----------|------|-------|--------|
| **LightLeakSweep** | CSS gradient + Framer | `colors[]`, `direction`, `duration` | Light leak transition overlay |
| **FlourishLines** | SVG + Framer Motion | `style` (diamond/arrow/circle), `color` | Decorative divider animation |
| **GlitchText** | CSS + Framer | `text`, `intensity`, `trigger` | Occasional glitch reveal for edgy topics |
| **BadgePulse** | CSS + Framer | `text`, `dotColor`, `breathe` | Top-left scene badge with pulsing dot |
| **SceneWatermark** | CSS | `text`, `position`, `opacity` | Persistent brand watermark |

---

## 5. The Compositor: Stock Footage + Web Components

Every scene is a **layered composition**. The FFmpeg engine composites these layers in a single pass.

### Layer Stack (Bottom to Top)
```
Z-Layer 0: Background Stock Footage (Pexels) [or MeshGradient if no footage]
Z-Layer 1: Background Video Effects (Ken Burns on footage, or gradient drift)
Z-Layer 2: Persistent Foundation (ParticleField, AmbientOrbit, GridOverlay) — pre-rendered transparent video
Z-Layer 3: Scene-Specific Motion Graphic (BarRace, BrainSVG, StepCards, etc.) — pre-rendered transparent video
Z-Layer 4: Text Overlay (KineticType, SubtitleBurn) — pre-rendered or FFmpeg drawtext
Z-Layer 5: Decorative / Transition (LightLeak, Flourish) — pre-rendered or FFmpeg lut
Z-Layer 6: Vignette + Grain + Color Grade — FFmpeg filters
Z-Layer 7: Persistent UI (Badge, Watermark, Progress Bar) — FFmpeg overlay or pre-rendered
```

### Stock Footage Strategy (Pexels)
- **Never use raw Pexels clips as the only visual.** Every clip must have at least one motion graphic overlay or particle layer on top.
- **Clip length limit:** Max 8 seconds per clip. If a scene is 15 seconds, it uses 2–3 Pexels clips with a crossfade.
- **Clip treatment:** Every clip gets color-graded to match the video's Theme Manifest (FFmpeg `eq` + `curves`).
- **Ken Burns:** Static or slow footage gets zoom/pan via FFmpeg `zoompan` so it never sits still.
- **Search strategy:** The Director generates `visual_keywords` per scene. The Asset Manager fetches 3 clips per scene and the Compositor picks 1–2 based on beat sync needs.

### The No-Repeat Engine (Hard Rules)
To ensure every scene feels unique within a video:

1. **Layout Diversity Tracker:** A registry tracks which layout "family" was used in the last 3 scenes. Forbidden repeat.
   - Layout families: `center-hero`, `split-screen`, `full-text`, `data-dominant`, `footage-dominant`, `overlay-heavy`, `minimal`

2. **Transition Pool:** 12+ transition types. The Compositor maintains a "last used" queue (length 4). No transition can be re-used until it exits the queue.
   - Transitions: `crossfade`, `light-leak-wipe`, `directional-wipe`, `zoom-in`, `zoom-out`, `glitch-skip`, `radial-reveal`, `slide-left`, `slide-right`, `iris-close`, `motion-blur`, `dissolve-glow`

3. **Component Uniqueness:** Within a single video, a specific web component (e.g., `BarRaceChart`) cannot be used more than once unless its data and visual treatment are radically different (different orientation, color, data shape).

4. **Color Grade Rotation:** The Theme Manifest defines 2–3 color grades. The Compositor rotates them across scenes so adjacent scenes don't feel identical.

5. **Text Position Rotation:** Text overlays cycle through 6 pre-defined anchor zones (top-left, top-center, top-right, center, bottom-left, bottom-center, bottom-right). No zone repeat within 3 scenes.

---

## 6. Audio-Visual Sync Architecture

The reference has subtle but powerful audio-reactive motion. We implement this via the **Beat Grid** shared between Audio Engine and Compositor.

### Beat Sync Points
1. **Scene Cut Snapping:** Scene transitions happen within ±0.15s of a beat if `beat_sync_intensity > 0.4`. The Compositor nudges scene duration slightly to hit the nearest beat.
2. **Overlay Pulse:** On strong beats (onset energy > 0.7), the opacity of motion graphic layers pulses 0.85 → 1.0 over 6 frames via FFmpeg `fade` or `eq`.
3. **Text Reveal Trigger:** Kinetic typography reveals can be timed to start on a beat or complete on a beat.
4. **Camera Zoom:** On beat drops, the `zoompan` on stock footage increases zoom velocity by 20% for 12 frames.
5. **Particle Burst:** High-energy beats trigger a temporary particle burst (increased velocity, color flash) in the ParticleField component.

### Implementation
The Audio Engine produces `beat_grid.json` with:
```json
{
  "bpm": 128,
  "beats": [0.00, 0.47, 0.93, ...],
  "onsets": [0.00, 2.34, 4.12, ...],
  "energy": [0.2, 0.8, 0.3, ...],
  "downbeats": [0.00, 1.87, 3.74, ...]
}
```
The Compositor reads this and applies filters at exact frame numbers.

---

## 7. The Animation Factory: On-Demand Render Pipeline

Since we chose **Option B (On-demand rendering per video)**, the Animation Factory must be fast and parallelized.

### Render Pipeline Per Scene
```
Director's Cut JSON → Scene Component Manifest
  → React App receives props (theme, data, duration, componentType)
  → Playwright opens headless Chromium (1920×1080, 30fps)
  → Chrome DevTools Protocol (CDP) captures screenshots at 30fps
  → Screenshots piped to FFmpeg stdin → encodes to ProRes/PNG + alpha
  → Output: scene_mograph_S04.mov (transparent, 1080p30)
```

### Parallelization Strategy
- The Animation Factory pre-renders all motion graphic clips **before** the main FFmpeg compositor starts.
- Clips are rendered in batches of 4 (matching CPU cores).
- Estimated render time: 2–3 minutes for 20–30 clips (each clip is 5–15 seconds).
- **Optimization:** Short clips are easier to render. The engine favors shorter mograph durations (looping if needed) over long renders.

### Component → Video Mapping
Each component in the registry is wrapped in a standard React "Clip Renderer" that:
1. Accepts a `duration` prop and auto-loops or truncates the animation to fit.
2. Renders at exactly 1920×1080 with a transparent background (`rgba(0,0,0,0)`).
3. Outputs a seamless loop if the animation is cyclical (particles, ambient orbits) or a fixed duration if it's a one-shot (chart reveal, step cards).

---

## 8. Quality Guardrails v2 (Anti-Slideshow + Anti-Repetition)

### Hard Rules (Enforced by the Compositor)
1. **Every scene has ≥3 animated layers** (background motion + mograph + text + decorative).
2. **No static image > 2 seconds** without Ken Burns or overlay.
3. **No stock clip > 8 seconds** without a cut or crossfade to another clip.
4. **Average Shot Length (ASL):** 4–7 seconds. The engine enforces this via scene duration limits.
5. **No repeated layout family within 3 scenes.**
6. **No repeated transition within 4 scenes.**
7. **No repeated text anchor zone within 3 scenes.**
8. **Color grade must shift** between at least 2 variants within a chapter.
9. **Text cannot be static.** It must be in a state of reveal, fade, or subtle drift.
10. **Background music must duck** -18dB during narration, with a 200ms attack/release curve.

---

## 9. Tech Stack (Confirmed & Extended)

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Orchestrator** | Python 3.11 + FastAPI | API, task queue, FFmpeg subprocess management |
| **Director (Brain)** | Groq API + Pydantic | Script + Theme Manifest + Director's Cut JSON generation |
| **Asset Manager** | Python + Pexels API + disk cache | Fetch, cache, index stock footage and user assets |
| **Animation Factory** | React 18 + Framer Motion + Playwright + CDP | Headless render of web components to transparent video clips |
| **Component Registry** | React component library + Storybook | All reusable data-viz, text, brain, UI, decorative components |
| **Audio Engine** | Python + edge-tts + librosa + FFmpeg | TTS, beat detection, music stem mixing, SFX, loudnorm |
| **Compositor** | FFmpeg (CLI) + filter_complex | Layer assembly, transitions, color grading, audio mix, final encode |
| **Transitions** | FFmpeg xfade + gltransition | Cinematic crossfades, wipes, zooms |
| **Music/SFX** | Curated local stem library (Decision A) | Mood/BPM categorized, algorithmically selected |
| **Deployment** | Hugging Face Docker Space | Container with Python, Node, FFmpeg, Chromium, Playwright |
| **Data Viz** | D3 (inside React components) | Complex charts, timelines, heatmaps |
| **Canvas Effects** | HTML5 Canvas + RAF (inside React) | Particle systems, sparklines, fluid simulations |
| **SVG Animation** | SVG + SMIL + Framer Motion | Brain illustrations, neural networks, decorative flourishes |

---

## 10. Implementation Roadmap (Revised)

### Phase 0: Foundation (1 week)
- Hugging Face Docker Space setup (Python, Node, FFmpeg, Chromium, Playwright)
- FastAPI skeleton with `/generate` and `/status` endpoints
- Environment wiring (Groq, Pexels, secrets)

### Phase 1: The Brain & Theme Engine (1 week)
- Groq prompt engineering for two-pass generation (Script + Director's Cut + Theme Manifest)
- Pydantic schemas for all JSON outputs
- Theme Manifest parser and validator

### Phase 2: Asset Pipeline (1 week)
- Pexels API integration + caching + proxy
- User asset library mount + indexing
- Audio Engine: edge-tts, librosa beat detection, music stem selection, SFX mixing

### Phase 3: Animation Factory v1 (2 weeks)
- React app scaffold with Playwright capture pipeline
- Build 10 core components: ParticleField, KineticType, BrainSVG, BarRaceChart, FloatingCard, StepCard, TimerRing, ComparisonBars, NeuralNetwork, ProgressTaskList
- CDP → FFmpeg pipe optimization for speed
- Batch rendering queue

### Phase 4: The Generative Compositor (2 weeks)
- FFmpeg filter_complex builder (layer stack, transitions, color grades)
- Scene assembly engine with parallel rendering
- No-Repeat Engine implementation (layout, transition, component trackers)
- Beat-sync integration

### Phase 5: Quality & Polish (1 week)
- Anti-slideshow validation (automated frame-by-frame motion detection)
- Audio loudnorm mastering (-14 LUFS)
- End-to-end testing with 3 full 8-minute videos
- Performance tuning (render time < 2× video duration)

### Phase 6: UI & Deployment (1 week)
- Minimal React UI for triggering generation, previewing Director's Cut, downloading final video
- Deploy to HF Space
- Documentation

---

## 11. Open Questions (Final Lock Before Code)

1. **Font Licensing:** Space Grotesk, Inter, and Fraunces are all Google Fonts (free). Confirm if you want to use these exactly, or if you have custom font preferences.

2. **Music Stem Library:** Do you have a starter set of royalty-free stems, or should I design the system to accept a folder of MP3/WAV files that you will populate later? The engine will work either way — we just need the category structure (mood/BPM folders).

3. **User Asset Library:** Do you have high-quality images/clips/SVGs to seed the library, or should we start with an empty library and rely on Pexels + generative motion graphics for the first videos?

4. **SFX Strategy:** Should SFX be part of the curated music stem library, or do you want a separate SFX engine (e.g., Freesound API or simple generated tones via Web Audio / FFmpeg `sine`)? The reference has minimal SFX but it adds polish.

5. **Are we ready to begin Phase 0?** (Yes = start building the Docker/HF Space skeleton immediately.)

---

*This system design enables the engine to produce videos of the quality demonstrated in `v3.html` while maintaining full generative uniqueness, no repetition, and the hybrid stock-footage + web-native motion graphics pipeline you requested.*
