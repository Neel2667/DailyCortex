# CORTEX RENDER — Change Log & Conversation History

> This document records the complete conversation history and design decisions so the next AI can understand the project's evolution.

---

## 2026-06-17 — Initial Request & Architecture Planning

### User Request
- Build an app for YouTube that generates 8–10 minute long videos on brain hacks
- Uses infographics, animations, web technology (React, Framer Motion)
- Automatically summarizes scripts and renders visuals
- Deploy on Hugging Face Spaces
- Use: Groq API for script/brain, Edge TTS for voice, Pexels for stock videos
- High performance for real-time video assembly
- Engaging and dynamic with smooth transitions and synchronized audio
- Short and varied footages to maintain viewer interest
- Trending background music and SFX based on visual mood
- No templates — generative engine that crafts unique edits from scratch
- No AI-generated video/image — user-provided high-quality source assets
- Fully automated, professional and cinematic quality
- No cheap slideshow feel
- Audio-reactive motion synced to background music beat
- Dynamic pacing, smooth transitions, cinematic look

### AI Response
- Created comprehensive `architecture_plan.md`
- Designed high-level system architecture with Groq Director, Animation Factory, FFmpeg Compositor
- Proposed 3-phase pipeline: Brain → Assets → Compositor
- Identified 3 open decisions: Music/SFX, Framer Motion pipeline, Real-time definition

---

## 2026-06-17 — Decision Locking

### User Decisions
- **Music & SFX Strategy:** Option A (curated local stem library)
- **Framer Motion Pipeline:** Option B (on-demand rendering per video)
- **Real-Time Definition:** Option A (fast batch rendering <2× duration)

### AI Update
- Updated `architecture_plan.md` with locked decisions
- Added performance budget note for on-demand mograph rendering
- Confirmed HF Spaces implication (2 vCPU, cap parallel FFmpeg to 2)

---

## 2026-06-17 — Demo Request & Reference

### User Request
- Generate a demo showing how the app will look and feel
- User provided `v3.html` as a reference (attached to workspace)

### AI Response
- Created `demo.html` — interactive 6-stage prototype:
  - Stage 0: Landing (neural background, tech stack badges)
  - Stage 1: Topic input (glowing input, suggestion chips)
  - Stage 2: Processing (typewriter script, step progress, Groq simulation)
  - Stage 3: Director's Cut timeline (12 scene cards, mood badges, color swatches)
  - Stage 4: Scene preview (viewport with layered compositing, neural overlay, beat ring, metadata panel)
  - Stage 5: Final player (progress bar, scene markers, download, quality badges)
- Asked user to review and confirm visual direction

---

## 2026-06-17 — Visual Reference Analysis (v3.html)

### User Feedback
- `v3.html` is the reference quality target
- Keep Pexels stock footage
- Use everything available on web technology (charts, cards, infographics, comparison, animation)
- Combine stock footage + animation + graphics
- Each video has a different theme based on topic
- Scenes must be short and no repeat
- Increase chapters if needed

### AI Analysis of v3.html
- Color system: `#0a0e27` (void), `#14b8a6` (cyan), `#f472b6` (pink), `#818cf8` (indigo), `#fbbf24` (gold)
- Typography: Space Grotesk (headline/numbers), Inter (body), Fraunces Italic (emotional accents)
- Persistent elements: 130+ particle canvas, 3 orbiting ambient dots, grid overlay, film grain, vignette, scene badge, watermark, progress bar
- 5 scene archetypes: Title/Hook, Stat, Brain Science, The Hack, Payoff
- Every frame has 3–5 simultaneous animations
- No dead frames, no static text, no static images
- Animation physics: `cubic-bezier(0.16, 1, 0.3, 1)` (exponential out)
- Light leak sweep transitions, letterbox cinematic mode

### AI Redesign
- Created `system_design_v2.md` with:
  - Chapter-Scene hierarchy (4–6 chapters, 5–8 scenes per chapter, 20–48 total scenes)
  - 12 visual archetypes (Hook, Evidence, Action, Payoff categories)
  - 7 layout families (screen composition rotation)
  - 12 cinematic transitions (no-repeat-within-4 rule)
  - Theme Engine (unique color system per video based on topic mood)
  - Complete Component Registry (40+ React/Framer Motion components)
  - 5-layer visual stack (Z0–Z7)
- Asked user for confirmation on 4 open questions (fonts, music library, user assets, SFX)

---

## 2026-06-17 — Algorithm Research & Retention Optimization

### User Concern
- 10–25 seconds per scene might hurt retention
- User wants to research YouTube algorithm

### AI Research
- Searched YouTube algorithm 2025–2026
- Key findings:
  - Retention % (AVD) beats total watch time
  - 60%+ AVD is good, 70%+ is excellent
  - Session contribution is the #1 algorithm signal
  - Satisfaction surveys drive recommendations
  - 3–5 minute cliff is where most drop-offs happen
  - Fast cuts + no dead air is necessary but not sufficient
  - "Add B-roll, graphics, or new camera angles every 10–15 seconds"
  - "Trim every pause over 0.3 seconds"
  - "Your animated intro graphic is a retention tax"

### AI Response
- Proposed revised architecture with:
  - 3-minute big reveal and 50% mid-point reset
  - Shorter scenes after 5-minute mark
  - Internal keyframes within scenes (3–4 micro-changes per 10–25 sec scene)
- User rejected pure algorithm approach and said: "we need both right script and visuals... we need hook time to time to keep viewer thinking and attached"

---

## 2026-06-17 — The Hook Cadence Insight (User's Brilliance)

### User Insight
- Fast cuts alone lose excitement
- Need hooks periodically to keep viewer thinking and attached
- This is the critical design insight that elevates the project from "algorithm-optimized" to "truly viral"

### AI Response
- Acknowledged the insight as brilliant
- Designed the **Three-Layer Hook System**:
  1. Micro-hooks (every 15–30 seconds): single sentence/visual that raises a micro-question
  2. Medium hooks (every 60–90 seconds): bigger open loop, 2–3 minute payoff
  3. Big hooks/cliffhangers (every 3–4 minutes): major revelation, closes multiple loops
- Explained the neuroscience: Information Gap Theory, Zeigarnik Effect, Dopamine Anticipation
- Created the **Open Loop Script Template** with 5 nested loops for a 9-minute video
- Mapped the **Visual Tension Curve** (visual intensity rises before narrative payoff)
- Designed the **Pattern Interrupt** system (hook type drives visual change, not random timer)
- Proposed new JSON schema extensions: `hook_role`, `visual_intensity`, `keyframes`, `open_loops`, `micro_hooks`, `callback_reference`
- Asked user to confirm redesign around Hook Cadence System

### User Confirmation
- **"yes thats brillient idea"**
- User requested SSH key generation and GitHub upload
- Reason: ensure next AI can understand the project in detail and continue from where we left off

---

## 2026-06-17 — Phase 0 Foundation & GitHub Upload

### AI Actions
- Generated SSH key: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEvIinWH+keWDuK73PK9rNAgytIP795AgU/vXb8u85Q9`
- Created comprehensive documentation:
  - `PROJECT_OVERVIEW.md` — complete project context, locked decisions, quality target, file structure, next steps
  - `ARCHITECTURE.md` — technical architecture, data flow, module specs, JSON schemas, animation pipeline, compositor pipeline, beat sync, performance budget, deployment
  - `HOOK_CADENCE.md` — the most important document: open loop system, narrative structure, visual tension curve, Groq prompt engineering, implementation checklist
  - `NEXT_STEPS.md` — prioritized task list for next AI, success criteria per phase
  - `CHANGELOG.md` — this file
- Built code skeleton:
  - `Dockerfile` — multi-stage Ubuntu + Python + Node + FFmpeg + Chromium
  - `entrypoint.sh` — HF Space boot sequence
  - `requirements.txt` — Python dependencies
  - `.env.example` — API key placeholders
  - `app/` — FastAPI + pipeline modules (main, config, models, brain, asset_manager, audio_engine, compositor)
  - `mograph_factory/` — React + Framer Motion + Playwright scaffold
  - `assets/` — directory structure for music, images, clips, svgs, sfx
- Initialized git repository and committed all files

---

## Current Status

| Phase | Status |
|-------|--------|
| Architecture & Planning | ✅ COMPLETE |
| Design Decisions | ✅ LOCKED |
| Visual Reference Analysis | ✅ COMPLETE |
| Algorithm Research | ✅ COMPLETE |
| Hook Cadence System | ✅ DESIGNED (pending implementation) |
| Phase 0 Foundation | ✅ BUILT (code skeleton + docs) |
| GitHub Upload | ⏳ IN PROGRESS (needs user to add SSH key to GitHub) |
| Hook Cadence Integration | ⏳ PENDING (Task 1–3 in NEXT_STEPS.md) |
| Framer Motion Components | ⏳ PENDING (Task 4–9) |
| Playwright Capture | ⏳ PENDING (Task 10–11) |
| FFmpeg Compositor | ⏳ PENDING (Task 12–14) |
| Audio Pipeline | ⏳ PENDING (Task 15–17) |
| End-to-End Pipeline | ⏳ PENDING (Task 18) |
| UI & Deployment | ⏳ PENDING (Task 19–20) |
| Quality Validation | ⏳ PENDING (Task 21–23) |

---

## Next AI Instructions

1. Read `PROJECT_OVERVIEW.md` first
2. Read `HOOK_CADENCE.md` second (this is the project's soul)
3. Read `ARCHITECTURE.md` third (technical implementation)
4. Read `NEXT_STEPS.md` fourth (task list)
5. Read the code in `app/` and `mograph_factory/src/`
6. Start with **Task 1: Extend Data Models** (add hook fields to `app/models.py`)
7. The user explicitly said: **"yes thats brillient idea"** — the Hook Cadence System is approved and mandatory
8. The user's quality target is `v3.html` — do not build anything cheaper than that reference
9. The user is building a product, not a prototype — build accordingly

---

## Key Files to Preserve

- `v3.html` — the user's visual reference (attached to workspace, not in git yet — should be in `uploads/`)
- `demo.html` — the AI's interactive demo (useful for understanding UI flow)
- `architecture_plan.md` — the original architecture plan (superseded by newer docs but contains context)
- `system_design_v2.md` — the system design that bridges architecture and v3 reference analysis

---

*End of Change Log. This project is alive. Build it with care.*
