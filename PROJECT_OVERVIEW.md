# CORTEX RENDER — Project Overview for Next AI

> **Date:** 2026-06-17
> **Status:** Architecture finalized, Phase 0 foundation partially built. Hook Cadence System redesign pending.
> **Project Goal:** A fully automated generative video engine that produces 8–10 minute cinematic YouTube documentaries on brain hacks. No templates. No dead frames. Unique visual identity per video.

---

## What This Project Is

CORTEX RENDER is a **generative cinematic video engine** that creates professional YouTube documentaries from scratch using:
- **Groq API** (LLM director that writes scripts + shot lists + visual themes)
- **React + Framer Motion** (headless animation factory, rendered via Playwright + Chromium)
- **FFmpeg** (compositor that assembles stock footage, motion graphics, text, audio into final video)
- **Pexels** (stock footage B-roll, composited as background texture)
- **Edge TTS** (narration voice)
- **Curated music stem library** (algorithmically selected by mood/BPM)
- **librosa** (beat analysis for audio-reactive motion)

Every video is unique. No two videos share the same edit pattern, layout, transition sequence, or color treatment. The system is designed for **Hugging Face Spaces** deployment (Docker container).

---

## Critical Locked Decisions

These are non-negotiable architectural decisions that have already been made and must be respected:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Music/SFX** | **Option A** — Curated local royalty-free stem library (categorized by mood/BPM) | Zero copyright risk, deterministic beat-matching, fast |
| **Framer Motion Pipeline** | **Option B** — On-demand rendering per video | Every video gets unique motion graphics (color, data, duration, physics). Adds ~90–120 sec per build but allows true generative output |
| **Real-Time Definition** | **Option A** — Fast batch rendering (<2× video duration) | 10-min video renders in <20 min. Parallel scene FFmpeg jobs + single-pass compositing |
| **Visual Quality Target** | Match `v3.html` reference exactly | Premium dark documentary aesthetic, 130+ particle systems, spring physics typography, SVG brain illustrations, layered compositing, film grain, vignette |
| **Stock Footage** | **Keep Pexels** — composited as background texture, never used raw | Treated with Ken Burns, color grading, and always overlaid with motion graphics |
| **Video Length** | 8–10 minutes (480–600 seconds) | YouTube long-form sweet spot |
| **Resolution** | 1920×1080, 30fps | Standard 1080p |
| **No AI-generated imagery/video** | CONFIRMED — Groq only for script/logic; no text-to-image or text-to-video models | Use Pexels + user assets + code-driven motion graphics only |

---

## The Hook Cadence System (MOST RECENT — PENDING IMPLEMENTATION)

This is the **brilliant insight from the last conversation** that must be the center of the redesign. Do NOT proceed without understanding this.

### The Problem With Algorithm-Only Thinking

Pure "fast cuts + no dead air" gets 60% retention. The channels that hit 80%+ retention (Psych2Go, BE AMAZED, Top Fives, Bright Side) use **narrative dopamine loops** — not just visual speed.

### The Solution: Three-Layer Hook System

Every video must be structured with **5–7 nested open loops** (curiosity gaps) in the script, matched by a **visual tension arc** that maps to those loops.

#### 1. Micro-Hooks (Every 15–30 seconds)
- A sentence or visual element that raises a micro-question
- Script: "But here's the problem — your brain doesn't know the difference between scrolling Instagram and winning a lottery."
- Visual: Sudden cut to brain scan lighting up, or split-screen comparison
- **Every scene must have a `micro_hook` field** — exact line and timestamp where the visual must "snap" to attention

#### 2. Medium Hooks (Every 60–90 seconds)
- Bigger open loop that won't pay off for 2–3 minutes
- Script: "There's one brain region that makes this decision for you. And if you know how to hack it, you'll never procrastinate again. We'll get to that in a minute. First, let me show you why willpower is a myth."
- Visual: Full visual reset — new layout family, new color grade, dramatic typography entrance
- **Every scene has a `hook_role` field**: `tease`, `escalation`, `payoff`, `rest`

#### 3. Big Hook / Cliffhanger (Every 3–4 minutes)
- Major revelation that the entire chapter has been building toward
- Script: "Remember that 2-minute rule I mentioned at the start? It works because of something called 'task initiation energy' — and once I explain this, you'll understand why every productivity app you've ever used was wrong."
- Visual: Most intense animation in the chapter. Full-screen takeover. Beat-synced pulse. Color grade shift to `revelatory` or `euphoric`.
- **The climax scene pays off 2–3 open loops simultaneously** — this is the dopamine cascade

### The Open Loop Script Template (The Golden Structure)

```
OPEN LOOP 1 (The Big Promise): [0:00]
"There's a 2-minute brain hack that makes procrastination impossible. 
I'm going to show you exactly how it works, but first you need to understand 
why your brain is wired to sabotage you."
→ LOOP 1 stays open until 7:30 (the hack reveal)

OPEN LOOP 2 (The Science Mystery): [0:45]
"Scientists at MIT discovered that this isn't about willpower. 
It's about something called 'dopamine prediction error.'"
→ LOOP 2 stays open until 2:30 (the brain scan reveal)

OPEN LOOP 3 (The Stat Shock): [2:30]
"One in five adults are chronic procrastinators. But that's not the scary number. 
The scary number is what happens after 24 hours of avoidance."
→ LOOP 3 stays open until 4:00 (the neural pathway animation)

OPEN LOOP 4 (The Paradox): [4:00]
"Here's the paradox: the more you tell yourself 'I need to focus,' 
the less you actually focus. Why? Because your prefrontal cortex 
and your amygdala are in a literal tug-of-war."
→ LOOP 4 stays open until 6:00 (the trick reveal)

OPEN LOOP 5 (The Trick Tease): [6:00]
"It's called the '2-Minute Initiation Protocol.' Not the 5-minute rule. Not the Pomodoro. 
Two minutes. And it works because it bypasses the amygdala entirely."
→ LOOP 5 stays open until 7:30 (the protocol reveal + demo)

CLOSURE 1: [7:30] — ALL LOOPS CLOSE AT ONCE. Dopamine payoff.
CLOSURE 2: [8:30] — Emotional resolution + CTA
CLOSURE 3: [9:15] — Next video hook (session continuation)
```

### The Visual Tension Curve

The Compositor maps `visual_intensity` to `hook_role`:

| Hook Role | Visual Intensity | Beat Sync | Visual Behavior |
|-----------|-----------------|-----------|-----------------|
| `tease` | 0.8 | 0.6 | Immediate impact, full-screen kinetic text, particle burst |
| `escalation` | 0.3–0.6 | 0.2–0.5 | Slow build, longer takes, bigger text, tension mounting |
| `payoff` | 1.0 | 0.9 | All animation systems fire, fastest cuts, color shift, beat drop |
| `rest` | 0.2 | 0.1 | Ambient particles, slow drift, breathing text — still alive but calm |

**Key Rule:** Visual intensity should RISE before the narrator says the payoff line. The animation starts building 5 seconds before the payoff line is spoken. At the payoff line, the visual "snaps" — particle burst, color grade shift, fast cut, beat drop.

---

## The Chapter-Scene Architecture (8–10 Minutes)

```
VIDEO (8–10 minutes, 480–600 seconds)
└── CHAPTER 1: THE HOOK (2 minutes, ~120 seconds)
    ├── Scene 1  (15 sec) — Question Bomb [L1_tease]
    ├── Scene 2  (20 sec) — Stat Shock [L2_tease]
    ├── Scene 3  (15 sec) — Myth Bust [L1_escalation]
    ├── Scene 4  (20 sec) — Story Teaser [L2_escalation]
    ├── Scene 5  (15 sec) — Personal Mirror [L3_tease]
    └── Scene 6  (15 sec) — Chapter Transition [L1_escalation]

└── CHAPTER 2: THE SCIENCE (2.5 minutes, ~150 seconds)
    ├── Scene 7  (20 sec) — Brain Scan [L2_payoff]
    ├── Scene 8  (20 sec) — Study Drop [L3_escalation]
    ├── Scene 9  (15 sec) — Comparison Split [L3_escalation]
    ├── Scene 10 (20 sec) — Timeline Flow [L4_tease]
    ├── Scene 11 (25 sec) — Data Infographic [L4_escalation]
    ├── Scene 12 (20 sec) — Expert Quote [rest]
    └── Scene 13 (15 sec) — Chapter Transition [L4_escalation]

└── CHAPTER 3: THE HACK (2.5 minutes, ~150 seconds)
    ├── Scene 14 (20 sec) — Step Reveal [L5_tease]
    ├── Scene 15 (20 sec) — Habit Loop [L5_escalation]
    ├── Scene 16 (20 sec) — Protocol Grid [L5_escalation]
    ├── Scene 17 (15 sec) — Quick Win [L1_payoff + L4_payoff]
    ├── Scene 18 (20 sec) — Tool Showcase [L5_escalation]
    └── Scene 19 (15 sec) — Chapter Transition [L5_escalation]

└── CHAPTER 4: THE PAYOFF (2 minutes, ~120 seconds)
    ├── Scene 20 (20 sec) — Transformation Summary [L1_payoff + L5_payoff]
    ├── Scene 21 (15 sec) — CTA Pulse [L3_payoff + L4_payoff]
    ├── Scene 22 (20 sec) — Next Hook [session continuation]
    └── Scene 23 (15 sec) — Credit Roll [rest]
```

**Total: ~23 scenes, ~9 minutes.**

**Key Rule:** No chapter repeats the same archetype twice. No two consecutive scenes use the same layout family. No two consecutive scenes use the same transition. No two consecutive scenes use the same color grade. Visual intensity must alternate between high and medium to create a breathing rhythm.

---

## The Visual System (v3.html Reference Quality)

The `v3.html` file in the project is the **absolute visual reference**. Every video must match this quality. Study it carefully.

### Color Palette (Locked)
| Role | Hex | Usage |
|------|-----|-------|
| **Void Background** | `#0a0e27` | Deep navy base, all scenes |
| **Primary Cyan** | `#14b8a6` | CTAs, progress, kicker lines, badges |
| **Secondary Pink** | `#f472b6` | Contrast moments, amygdala/fear regions |
| **Tertiary Indigo** | `#818cf8` | Secondary glow, neural connections |
| **Accent Gold** | `#fbbf24` | "The Hack" / payoff scenes, step numbers |
| **Typography White** | `#f4f4f5` | Headlines |
| **Typography Dim** | `#a1a1aa` | Body text, system info |

### Typography Stack (Locked)
- **Space Grotesk** — kicker labels, numbers, badges, UI metadata
- **Inter** — body text, system info
- **Fraunces (Italic)** — emotional accents inside headlines, "Procrastinate" word treatment

> **These are Google Fonts (free).** The Docker container must download them. The Playwright headless browser must render them correctly.

### The 5-Layer Visual Stack (Every Frame)
```
Z-Layer 0: Background (Pexels stock footage OR animated mesh gradient)
Z-Layer 1: Background Effects (Ken Burns on footage, or gradient drift)
Z-Layer 2: Persistent Foundation (ParticleField 130+, AmbientOrbit 3 dots, GridOverlay, FilmGrain)
Z-Layer 3: Scene-Specific Motion Graphic (BrainSVG, BarRaceChart, StepCards, etc.)
Z-Layer 4: Text Overlay (KineticType, SubtitleBurn, PullQuote)
Z-Layer 5: Decorative / Transition (LightLeak, FlourishLines)
Z-Layer 6: Vignette + Color Grade (FFmpeg eq/curves/lut3d)
Z-Layer 7: Persistent UI (Scene Badge, Watermark, Progress Bar)
```

### The "No Dead Frames" Rule (Hardcoded)
1. **Every scene has ≥3 animated layers** (background motion + mograph + text + decorative)
2. **No static image > 2 seconds** without Ken Burns or overlay
3. **No stock clip > 8 seconds** without a cut to another angle
4. **Average Shot Length (ASL):** 4–7 seconds internally enforced
5. **No repeated layout family within 3 scenes**
6. **No repeated transition within 4 scenes**
7. **No repeated text anchor zone within 3 scenes**
8. **Color grade must shift** between at least 2 variants within a chapter
9. **Text cannot be static** — must be in a state of reveal, fade, or subtle drift
10. **Background music ducks -18dB** during narration (sidechain compression via FFmpeg)

---

## The Framer Motion Component Registry

These are the components the Animation Factory must be able to render. Each component accepts the Theme Manifest as props and outputs a transparent video clip via Playwright.

### Foundation Layer (Always Present)
| Component | Tech | Props | Output |
|-----------|------|-------|--------|
| **ParticleField** | Canvas + RAF | `count`, `colors[]`, `speed`, `direction`, `twinkle` | Transparent `.mov` with 130+ drifting particles |
| **AmbientOrbit** | CSS + Framer | `orbits[]`, `colors[]`, `speeds[]` | Transparent `.mov` with 2–4 orbiting dots |
| **MeshGradient** | SVG + SMIL/Framer | `stops[]`, `duration`, `drift` | Background gradient video (can be blended with stock footage) |
| **GridOverlay** | CSS | `size`, `opacity`, `shiftSpeed`, `mask` | Grid lines with vignette mask |
| **FilmGrain** | CSS + SVG noise | `intensity`, `fps` | Grain overlay texture (seamless loop) |
| **Vignette** | CSS radial-gradient | `intensity`, `ellipseRatio` | Static edge darkening (can be FFmpeg `vignette` filter) |

### Typography & Text Systems
| Component | Tech | Props | Output |
|-----------|------|-------|--------|
| **KineticType** | Framer Motion | `text`, `revealType` (word/line/char), `stagger`, `easing` | Text reveal animation |
| **HeroWordReveal** | Framer Motion | `lines[]`, `stagger`, `accentWords[]` | v3-style headline with word-by-word spring |
| **PullQuote** | Framer Motion + SVG | `quote`, `attribution`, `lineAnimation` | Elegant quote reveal with decorative lines |
| **DataLabel** | CSS + Framer | `label`, `value`, `unit`, `animation` | Floating card label ("Cognitive Load ↑ 47%") |
| **LiveCounter** | Framer Motion + RAF | `startValue`, `endValue`, `duration`, `format` | Ticking number animation |
| **SubtitleBurn** | Framer Motion | `text`, `duration`, `position` | Lower-third style text overlay |

### Data Visualization & Infographics
| Component | Tech | Props | Output |
|-----------|------|-------|--------|
| **BarRaceChart** | React + Framer Motion | `data[]`, `duration`, `theme` | Animated bar chart race |
| **MorphDonut** | SVG + Framer Motion | `segments[]`, `transitionDuration` | Donut chart that morphs between states |
| **SparkLine** | SVG + Framer Motion | `data[]`, `strokeColor`, `fillGradient` | Animated line graph with draw-on effect |
| **ComparisonBars** | Framer Motion | `leftLabel`, `rightLabel`, `leftValue`, `rightValue`, `winner` | Side-by-side bar comparison |
| **ProgressTaskList** | Framer Motion | `tasks[]`, `fillDuration`, `stagger` | List with animated progress bars (v3-style) |
| **HeatmapGrid** | Canvas or SVG | `grid[]`, `colors[]`, `pulseSpeed` | Animated heatmap grid |
| **TimelineFlow** | SVG + Framer Motion | `events[]`, `pathStyle`, `nodeAnimation` | Horizontal or vertical timeline with node pulses |

### Brain & Biology Visualizations
| Component | Tech | Props | Output |
|-----------|------|-------|--------|
| **BrainSVG** | SVG + SMIL/Framer | `regions[]`, `activeRegions[]`, `pulseRings[]`, `connectionLines[]` | Animated brain illustration with region labels |
| **NeuralNetwork** | SVG + Framer Motion | `nodes[]`, `connections[]`, `pulseSpeed` | Network graph with node lighting + line pulses |
| **NeurotransmitterFlow** | SVG + Framer Motion | `channels[]`, `particles[]`, `direction` | Particles flowing through channels |
| **SynapsePulse** | Canvas + RAF | `synapseCount`, `firingRate`, `colors` | Action potential visualization |
| **RegionHighlight** | SVG + Framer | `brainPath`, `highlightRegions[]`, `glowColor` | Specific brain regions glowing sequentially |

### UI & Object Components
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

### Decorative & Transition Elements
| Component | Tech | Props | Output |
|-----------|------|-------|--------|
| **LightLeakSweep** | CSS gradient + Framer | `colors[]`, `direction`, `duration` | Light leak transition overlay |
| **FlourishLines** | SVG + Framer Motion | `style` (diamond/arrow/circle), `color` | Decorative divider animation |
| **GlitchText** | CSS + Framer | `text`, `intensity`, `trigger` | Occasional glitch reveal for edgy topics |
| **BadgePulse** | CSS + Framer | `text`, `dotColor`, `breathe` | Top-left scene badge with pulsing dot |
| **SceneWatermark** | CSS | `text`, `position`, `opacity` | Persistent brand watermark |

---

## The 12 Visual Archetypes (Scene Types)

These are the "cinematic shots" the Director (Groq LLM) chooses from. Each archetype is a unique visual language.

### A. Hook Archetypes (Chapter 1)
| Archetype | Visual Identity | Example |
|-----------|---------------|---------|
| **QuestionBomb** | Full-screen kinetic text fills screen, particles explode outward | "Why do you procrastinate?" |
| **StatShock** | Giant number slam + spring physics, live counter ticks | "1/5 adults" |
| **MythBust** | Split screen: "MYTH" → "TRUTH" | "You're lazy" → "Your brain is wired this way" |
| **StoryTeaser** | Cinematic footage + lower third | "In 2019, a researcher..." |
| **PersonalMirror** | "You are doing this right now" + relatable footage | Phone scrolling, fridge opening |

### B. Evidence Archetypes (Chapter 2)
| Archetype | Visual Identity | Example |
|-----------|---------------|---------|
| **BrainScan** | SVG brain with regions lighting up, pulse rings, labels | Prefrontal cortex → amygdala |
| **StudyDrop** | Research paper citation card → morphs into chart | "Nature Neuroscience, 2021" |
| **ComparisonSplit** | Left vs Right bars growing side-by-side | "Low dopamine" vs "Healthy" |
| **TimelineFlow** | Horizontal line with nodes, each expands to mini-card | 0h → 6h → 24h → 48h |
| **DataInfographic** | Bar chart race, donut morph, heatmap | Donut: 80% → 20% junk dopamine |
| **ExpertQuote** | Quote on elegant card with subtle footage behind | "The brain rewires itself..." |

### C. Action Archetypes (Chapter 3)
| Archetype | Visual Identity | Example |
|-----------|---------------|---------|
| **StepReveal** | 3 cards flip in one by one, number + icon + description | "1. Remove notifications" |
| **HabitLoop** | Circular ring: CUE → ROUTINE → REWARD | Phone buzz → drawer → clear mind |
| **ProtocolGrid** | Checklist items auto-check with animated ticks | 5-item protocol |
| **QuickWin** | "2:00" countdown ring + before/after flip | Before: scattered → After: focused |
| **ToolShowcase** | Animated phone mockup showing app in action | Screen Time app locking |

### D. Payoff Archetypes (Chapter 4)
| Archetype | Visual Identity | Example |
|-----------|---------------|---------|
| **TransformationSummary** | 4 floating cards with icons + percentages | "Focus ↑ 40%, Stress ↓ 30%" |
| **CTAPulse** | "Subscribe" + "Try This" pills with pulsing dots | Diamond flourishes |
| **NextHook** | "Next: why your first instinct is wrong" | Glitchy suspense reveal |
| **CreditRoll** | Sources, music credits, team names scrolling | Parallax scroll |

**Key Rule:** Within a single video, the same archetype cannot be used twice unless the data and visual treatment are radically different. The Director selects 5–6 unique archetypes per chapter.

---

## The 7 Layout Families (Screen Composition)

| Family | Description | Usage Weight |
|--------|-------------|--------------|
| `center_hero` | Everything centered, text in middle, footage full-bleed | Openers, payoffs |
| `split_screen` | Left: text/data, Right: footage/animation | Comparisons, brain scans |
| `full_text` | Text dominates 80% of screen, minimal background | Quotes, statistics |
| `data_dominant` | Charts/graphics take 70%, text is small labels | Infographics, timelines |
| `footage_dominant` | Stock footage fills 80%, text is lower-third | Story teasers, expert clips |
| `overlay_heavy` | 3–4 layers stacked (footage + particles + text + badge) | High-intensity scenes |
| `minimal` | Just text + ambient particles, zen-like | Rest scenes, transitions |

**Key Rule:** Same layout family cannot be used in two consecutive scenes. The Compositor enforces this with a "last 3 used" queue.

---

## The 12 Cinematic Transitions

| Transition | Description | Mood |
|------------|-------------|------|
| `crossfade` | Standard dissolve | Calm, rest |
| `light_leak_wipe` | Light sweep across screen | Cinematic, dramatic |
| `directional_wipe` | Hard directional wipe | Fast, action |
| `zoom_in` | Push into next scene | Intensity, focus |
| `zoom_out` | Pull back to reveal | Big picture, summary |
| `glitch_skip` | Digital glitch flash | Tech, edgy |
| `radial_reveal` | Circle expanding from center | Reveal, mystery |
| `slide_left` | Push to left | Narrative flow |
| `slide_right` | Push to right | Narrative flow |
| `iris_close` | Circle closing to black | Chapter end, pause |
| `motion_blur` | Directional blur streak | Speed, energy |
| `dissolve_glow` | Soft glow dissolve | Gentle, emotional |

**Key Rule:** Same transition cannot be used within 4 transitions. Pool maintains a "last 4 used" queue. The Director can request `transition_out: "auto"` and the Compositor stochastically picks from the pool.

---

## The Theme Engine (Unique Identity Per Video)

Every video gets a `ThemeManifest` generated by Groq based on the topic. This ensures internal consistency but external uniqueness.

### Example Theme Manifests

| Topic | Mood | Color System | Typography Feel | Motion Feel |
|-------|------|-------------|-----------------|-------------|
| "Dopamine Detox" | Clinical / Curious | Cyan `#14b8a6` + Deep Navy `#0a0e27` + Gold accents | Clean, spaced, scientific | Snappy, precise |
| "Lucid Dreaming" | Mystical / Euphoric | Purple `#9b5de5` + Indigo `#818cf8` + Soft Pink | Fluid, italic, dreamy | Slow, organic, drifting |
| "Memory Palace" | Architectural / Structured | Amber `#fbbf24` + Warm Gray `#a1a1aa` + Charcoal | Bold, geometric, classical | Staggered, deliberate |
| "Fear Response" | Tense / Urgent | Red `#ff6b6b` + Dark `#0a0e27` + Warning Orange | Sharp, high-contrast, urgent | Fast, staccato, glitchy |
| "Neuroplasticity" | Hopeful / Organic | Teal `#14b8a6` + Emerald `#10b981` + Cream | Soft, rounded, nurturing | Breathing, growing, elastic |

The Theme Manifest drives: color grades, particle colors, accent colors, font weights, easing curves, animation speeds, and archetype selection.

---

## The Audio-Reactive Motion System

The Audio Engine produces a `beat_grid.json` that the Compositor reads to sync visual motion to music.

```json
{
  "bpm": 128,
  "beats": [0.00, 0.47, 0.93, 1.40, ...],
  "onsets": [0.00, 2.34, 4.12, ...],
  "energy": [0.2, 0.8, 0.3, ...],
  "downbeats": [0.00, 1.87, 3.74, ...]
}
```

The Compositor uses this to:
1. **Snap scene cuts to nearest beat** (if `beat_sync_intensity > 0.4`)
2. **Overlay pulse on strong beats** (energy > 0.7): opacity 0.85 → 1.0 over 6 frames
3. **Text reveal trigger**: Kinetic typography starts on beat or completes on beat
4. **Camera zoom**: On beat drops, `zoompan` velocity increases 20% for 12 frames
5. **Particle burst**: High-energy beats temporarily increase particle velocity and add color flash

---

## Deployment Architecture (Hugging Face Spaces)

### Docker Multi-Stage Image
- Base: Ubuntu 22.04
- Python 3.11 + FastAPI + Pydantic + httpx + edge-tts + librosa + soundfile + numpy + scipy + ffmpeg-python + Pillow + aiofiles
- Node.js 20 + React 18 + Framer Motion 11 + Playwright + Vite + TypeScript
- FFmpeg (full build with filter_complex, xfade, gltransition)
- Chromium + Playwright dependencies
- Google Fonts (Space Grotesk, Inter, Fraunces) + system fonts

### File Structure
```
/workspace (or /app on HF Spaces)
├── Dockerfile                  # Multi-stage build
├── entrypoint.sh               # Boot sequence
├── requirements.txt            # Python deps
├── .env.example                # API keys template
├── README.md                   # Project overview
├── PROJECT_OVERVIEW.md         # This file — comprehensive spec
├── ARCHITECTURE.md             # Technical architecture details
├── HOOK_CADENCE.md             # Hook system spec (the big insight)
├── NEXT_STEPS.md               # What to build next
├── CHANGELOG.md                # Conversation history
│
├── app/                        # FastAPI + Pipeline orchestration
│   ├── main.py                 # API endpoints (6 endpoints defined)
│   ├── config.py               # Pydantic settings (all paths, keys, performance)
│   ├── models.py               # JSON schemas (DirectorCut, ThemeManifest, Scene, BeatGrid, etc.)
│   ├── brain.py                # Groq LLM integration (2-pass generation: Script → Director's Cut)
│   ├── asset_manager.py        # Pexels API + user asset library + cache
│   ├── audio_engine.py         # Edge TTS, librosa beat detection, music stem mixing, SFX
│   ├── compositor.py           # FFmpeg scene assembler, transitions, color grading, concatenation, mastering
│   └── __init__.py             # Package marker
│
├── mograph_factory/            # React + Framer Motion + Playwright capture
│   ├── index.html              # 1920x1080 transparent canvas
│   ├── vite.config.ts          # Vite config
│   ├── tsconfig.json           # TypeScript strict
│   ├── tsconfig.node.json      # Node types
│   ├── package.json            # React 18 + Framer Motion 11 + Playwright + Vite
│   ├── src/
│   │   ├── main.tsx            # React entry point
│   │   └── App.tsx             # Component registry + prop injection from window.CORTEX_RENDER
│   └── scripts/
│       └── render-clip.js      # Playwright → CDP → FFmpeg pipe (ProRes4444 with alpha)
│
├── assets/                     # User-provided high-quality library (seeded empty)
│   ├── music/                  # Stem library organized by mood/BPM
│   │   ├── curious/90/         # 90 BPM curious stems
│   │   ├── curious/110/
│   │   ├── curious/128/
│   │   ├── curious/140/
│   │   ├── tense/90/
│   │   ├── tense/110/
│   │   ├── tense/128/
│   │   ├── tense/140/
│   │   ├── revelatory/90/
│   │   ├── revelatory/110/
│   │   ├── revelatory/128/
│   │   ├── revelatory/140/
│   │   ├── calm/90/
│   │   ├── calm/110/
│   │   ├── calm/128/
│   │   └── calm/140/
│   ├── images/                 # User-provided high-res images
│   ├── clips/                  # User-provided premium video clips
│   ├── svgs/                   # User-provided SVG assets
│   └── sfx/                    # Sound effects (risers, impacts, whooshes)
│
├── cache/                      # Runtime cache (Pexels downloads, TTS, temp renders)
├── renders/                    # Final output MP4s
└── data/                       # Hugging Face Spaces persistent storage
    ├── cache/
    ├── renders/
    └── logs/
```

### API Endpoints (FastAPI)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health + endpoint listing |
| `/generate` | POST | Start a new video generation job |
| `/jobs/{job_id}` | GET | Check job status + progress |
| `/directors-cut/{job_id}` | GET | Get the Director's Cut JSON |
| `/preview-scene/{job_id}/{scene_id}` | GET | Preview a single rendered scene |
| `/download/{job_id}` | GET | Download the final mastered video |
| `/health` | GET | System health + disk cache size |

---

## What Has Been Built So Far (Phase 0 Status)

### ✅ Completed
1. **Dockerfile** — Multi-stage Ubuntu 22.04 + Python + Node + FFmpeg + Chromium scaffold
2. **entrypoint.sh** — Boot sequence for HF Spaces
3. **requirements.txt** — All Python dependencies listed
4. **.env.example** — API key placeholders
5. **app/config.py** — Pydantic settings (paths, performance, API keys)
6. **app/models.py** — JSON schemas (DirectorCut, ThemeManifest, Scene, BeatGrid, Job, GenerationJob)
7. **app/main.py** — FastAPI skeleton with 6 endpoints, stub pipeline, test video generation
8. **app/brain.py** — Groq 2-pass prompts (Script + Director's Cut) with detailed system prompts
9. **app/asset_manager.py** — Pexels API fetch + cache + user asset indexing
10. **app/audio_engine.py** — Edge TTS, librosa beat detection, music stem selection, audio mixing, SFX generator
11. **app/compositor.py** — FFmpeg filtergraph builder, scene rendering, concatenation, loudnorm mastering
12. **mograph_factory/index.html** — 1920×1080 transparent canvas
13. **mograph_factory/src/main.tsx** — React entry point
14. **mograph_factory/src/App.tsx** — Component registry with 10 stub components
15. **mograph_factory/vite.config.ts** — Vite config
16. **mograph_factory/tsconfig.json** — TypeScript strict config
17. **mograph_factory/scripts/render-clip.js** — Playwright → CDP → FFmpeg ProRes4444 capture pipeline
18. **README.md** — Project overview and quick start

### ❌ NOT Yet Built (Next Steps for Next AI)
1. **The Hook Cadence System** — The `Scene` model needs `hook_role`, `visual_intensity`, `micro_hooks`, and `open_loops` fields. The Groq prompt needs to be rewritten to force 5–7 nested open loops before writing narration.
2. **Real Framer Motion Components** — Only stub components exist. Need to build: ParticleField, KineticType, BrainSVG, BarRaceChart, FloatingCard, StepCard, TimerRing, ComparisonBars, NeuralNetwork, ProgressTaskList, and 10+ more.
3. **Playwright Capture Optimization** — The render-clip.js script exists but needs testing and optimization. The current approach uses screenshot loop → FFmpeg pipe. May need to switch to Chrome DevTools Protocol Page.screencastFrame for better performance.
4. **FFmpeg Compositor Realization** — The compositor.py is a stub. Needs full filter_complex generation with xfade, gltransition, overlay, eq, curves, zoompan, and beat-sync parameter injection.
5. **Groq Prompt Engineering for Hook Cadence** — The brain.py prompts need to be rewritten to output the Hook Cadence JSON structure before the scene list.
6. **Music Stem Library** — Empty directory structure exists. Needs to be populated with royalty-free stems organized by mood/BPM. Or the system needs to accept a zip upload.
7. **User Asset Library** — Empty directories exist. Need upload endpoints and indexing.
8. **End-to-End Pipeline Wiring** — The main.py pipeline is a stub (sleeps and generates test colorbar). Needs to actually call brain.py → asset_manager.py → audio_engine.py → compositor.py in sequence.
9. **Testing and Validation** — Need to test the full pipeline with a real 8-minute video and measure render time, quality, and retention.
10. **Deployment to Hugging Face Spaces** — GitHub repo exists, but needs to be pushed and configured as a Docker Space with secrets.

---

## Context From Previous Conversations

This project went through multiple planning phases. The key evolution:

1. **Initial Request:** Build an automated YouTube video generator for brain hacks using React, Framer Motion, Edge TTS, Pexels, Groq, FFmpeg, deployed on Hugging Face.
2. **Architecture Planning:** We designed a generative (non-template) compositor with a Groq "Director" that writes scripts and shot lists, a React Animation Factory for motion graphics, and FFmpeg for assembly.
3. **Visual Reference:** The user provided `v3.html` (a premium motion graphics demo) as the exact quality target. We analyzed it deeply: 5-layer visual stack, 130+ particles, spring physics typography, SVG brain illustrations, film grain, vignette, color grading.
4. **Algorithm Research:** We researched the YouTube 2026 algorithm. Key findings: retention % beats total watch time; 60%+ AVD is good, 70%+ is excellent; session contribution is the #1 signal; satisfaction surveys matter; 3–5 minute cliff is where most drop-offs happen.
5. **The Hook Cadence Insight:** The user correctly identified that pure "fast cuts + no dead air" is insufficient. The real viral channels use **nested open loops** (curiosity gaps) in the script, matched by visual tension arcs. This is the most important design insight and must be the center of the next build phase.

---

## SSH Key (Generated)

An SSH key has been generated for this project:

```
Public Key: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEvIinWH+keWDuK73PK9rNAgytIP795AgU/vXb8u85Q9 cortex-render@engine.ai
```

**You must add this public key to your GitHub account** under Settings → SSH and GPG keys → New SSH key.

Then run the push commands below.

---

## How to Push This to GitHub

1. **Create a new GitHub repo** (e.g., `yourusername/cortex-render`)
2. **Add the SSH key** above to your GitHub account
3. **Run these commands** (already done in the workspace, but verify):

```bash
cd /home/user
git init
git remote add origin git@github.com:YOUR_USERNAME/cortex-render.git
git add -A
git commit -m "Phase 0: Foundation + Hook Cadence Architecture Design

- Docker multi-stage build (Python + Node + FFmpeg + Chromium)
- FastAPI orchestrator with 6 endpoints
- Groq 2-pass director (script + shot list)
- Pexels asset manager with cache
- Edge TTS + librosa audio engine
- FFmpeg compositor with filtergraph builder
- React + Framer Motion Animation Factory scaffold
- Playwright → CDP → FFmpeg capture pipeline
- Complete Pydantic models (DirectorCut, ThemeManifest, Scene, BeatGrid, Job)
- Hook Cadence System design (5-7 nested open loops, visual tension arcs)
- v3.html reference analysis (premium motion graphics quality target)
- YouTube 2026 algorithm research and retention optimization
- Project documentation (PROJECT_OVERVIEW, ARCHITECTURE, HOOK_CADENCE, NEXT_STEPS)"
git branch -M main
git push -u origin main
```

---

## For the Next AI: Start Here

1. Read `PROJECT_OVERVIEW.md` (this file) — understand the vision and locked decisions
2. Read `HOOK_CADENCE.md` — understand the most important design insight (open loops + visual tension)
3. Read `ARCHITECTURE.md` — understand the technical stack and module responsibilities
4. Read `NEXT_STEPS.md` — understand the prioritized task list
5. Read the code in `app/` and `mograph_factory/` — understand what's already built vs. what needs building
6. The most critical missing piece is the **Hook Cadence integration** into the `models.py`, `brain.py` prompts, and the `compositor.py` visual intensity mapping.
7. The second most critical piece is the **real Framer Motion components** — the stubs in `mograph_factory/src/App.tsx` need to become real, animated, beautiful components that match `v3.html` quality.

**The user's explicit quality target is `v3.html`.** Do not build anything that looks cheaper than that reference. Every frame must have 3+ animated layers. Every scene must have internal keyframes (3–4 micro-changes). No dead frames. No repeated transitions. No repeated layouts.

The user is building a product, not a prototype. Build accordingly.
