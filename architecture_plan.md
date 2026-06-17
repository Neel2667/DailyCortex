# Cinematic Brain Hacks Video Engine — Architecture & Automation Plan

> **Goal:** A fully automated, generative (non-template) video production system that creates 8–10 minute professional YouTube documentaries on "brain hacks" niche topics. The system uses a library of high-quality user assets + Pexels stock footage, composited with cinematic motion graphics (React / Framer Motion), beat-synced audio, and AI-directed editing. No AI-generated imagery or video — only AI-generated *direction* and *code*.

---

## 1. Vision & Product Definition

| Attribute | Decision |
|-----------|----------|
| **Video Length** | 8–10 minutes |
| **Resolution** | 1920×1080 (1080p), 30fps |
| **Visual Style** | Cinematic documentary, not slideshow |
| **Motion Source** | Stock footage (Pexels) + User assets + Code-driven infographics (React/Framer Motion) |
| **Audio** | Narration (Edge TTS), trending background music, dynamic SFX |
| **Edit Style** | Generative — no fixed templates; unique cuts per video |
| **Deployment** | Hugging Face Space (Docker) |
| **AI Boundaries** | Groq only for *script/brain/logic*; NO text-to-image or text-to-video models |

---

## 2. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HUGGING FACE SPACE                            │
│  (Docker Container: Python + Node.js + FFmpeg + Edge TTS)           │
└─────────────────────────────────────────────────────────────────────┘
                                   │
    ┌──────────────┐    ┌──────────┴──────────┐    ┌────────────────┐
    │   USER INPUT │    │     THE BRAIN       │    │  ASSET LAYER   │
    │  (Topic/Seed)  │───▶│   (Groq API)        │    │                │
    └──────────────┘    │  Script + Director's  │◄───│ • Pexels API   │
                        │      Cut JSON         │    │ • User Library │
                        └──────────┬──────────┘    │ • Anim Factory │
                                   │               └────────────────┘
                                   ▼
                    ┌────────────────────────────┐
                    │   GENERATIVE COMPOSITOR    │
                    │   (Python + FFmpeg Engine) │
                    │                            │
                    │  • Stochastic edit rules   │
                    │  • Cinematic transitions   │
                    │  • Color grading / LUTs    │
                    │  • Beat-synced motion      │
                    └──────────┬─────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
    ┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
    │   AUDIO MIXER   │ │   SCENE      │ │   SCENE      │
    │  (Edge TTS +    │ │  RENDERER 1  │ │  RENDERER N  │
    │   Music/SFX)    │ │ (FFmpeg)     │ │ (FFmpeg)     │
    └─────────────────┘ └──────┬───────┘ └──────┬───────┘
                               │                │
                               └────────────────┘
                                        │
                                        ▼
                           ┌─────────────────────┐
                           │   FINAL CONCAT &    │
                           │   MASTER EXPORT     │
                           │   (MP4 / H.264)     │
                           └─────────────────────┘
```

---

## 3. The Generative Pipeline (Step-by-Step Automation)

### Step 1: Topic Ingestion
User provides a topic seed (e.g., `"The Dopamine Fasting Protocol"`). The system adds a random "creative seed" to ensure every video is unique.

### Step 2: The Director's Cut (Groq LLM)
The Brain (Groq `llama-3.3-70b` or equivalent) generates:
1. **Narrative Script** — 8–10 min spoken word with timestamps.
2. **Director's Cut JSON** — A shot-list / scene breakdown containing:
   - `scene_id`, `start_time`, `duration`, `narration_text`
   - `mood`: `tense`, `curious`, `euphoric`, `calm`, `mysterious`
   - `pacing`: `slow`, `medium`, `fast`, `burst`
   - `visual_keywords`: for Pexels search
   - `animation_trigger`: which infographic concept to overlay
   - `color_grade`: `warm_gold`, `cool_blue`, `high_contrast_mono`, `neural_green`
   - `beat_sync_intensity`: `0.0` to `1.0` (how tightly cuts/pulses align to music)
   - `transition_type`: `auto` (generative engine decides based on mood)
   - `b_roll_strategy`: `single`, `layered`, `picture_in_picture`

### Step 3: Asset Procurement
- **Narration**: `edge-tts` generates WAV per scene with SSML prosody (pause, emphasis).
- **Music**: Music Engine selects or generates a track matching mood & BPM target.
- **SFX**: Impact sounds, whooshes, and ambient textures mapped to transitions and key phrases.
- **Stock Footage**: Pexels API fetches 3–5 short clips per scene (max 15s each). Clips are cached locally by keyword hash.
- **User Assets**: SVG infographics, diagrams, and high-res images pulled from the mounted library.
- **Motion Graphics**: Pre-rendered React/Framer Motion clips are selected from the **Animation Asset Library**.

### Step 4: Audio Analysis & Beat Mapping
The Music Engine analyzes the chosen track with `librosa`:
- Extracts **BPM** and **beat timestamps**.
- Extracts **onset strength** (energy spikes).
- The Compositor uses these timestamps to:
  - Snap scene cuts to the nearest beat (if `beat_sync_intensity > 0.5`).
  - Trigger zoom/pulse on high-energy onset points.
  - Duck music volume (sidechain compression) during narration peaks.

### Step 5: The Generative Compositor (Cinematic Assembly)
This is the heart of the system. For each scene, the compositor does NOT use a template. Instead, it runs a **stochastic cinematic rule engine**:

1. **Select Transition**: From a weighted pool based on the *previous* scene's mood + current mood. No two identical transitions in a row.
2. **Apply Stock Montage**: Crossfade 2–4 short Pexels clips within the scene using `xfade` or `gltransition`. Never leave a static image > 3 seconds.
3. **Apply Ken Burns**: If an image is used, it gets a slow zoom/pan (`zoompan` filter) with randomized direction per scene.
4. **Overlay Infographic**: The selected React/Framer Motion clip is composited as a PiP or full-screen overlay with alpha blending. Its playback speed can be subtly adjusted to match beat BPM.
5. **Color Grade**: Apply mood-based FFmpeg `eq` curves (gamma, saturation, contrast) or a pre-baked LUT.
6. **Text Overlay**: Dynamic text (scene titles, key quotes) are rendered as high-quality WebP/PNG with alpha from a headless HTML renderer, then burned in with `overlay`.
7. **Audio Mix**: Merge narration, music (ducked -14dB during speech), and SFX on the beat.

### Step 6: Parallel Scene Rendering
Scenes are rendered in parallel subprocesses (Python `concurrent.futures`). Each scene outputs a temporary high-bitrate MP4 segment.

### Step 7: Final Concatenation & Mastering
- Segments are losslessly concatenated (`concat demuxer`).
- A final FFmpeg pass applies:
  - Audio normalization (`loudnorm`)
  - Introduction / Outro bumper (if provided)
  - Export to final 1080p H.264 MP4.

---

## 4. Core Modules Deep Dive

### 4.1 The Brain (Groq API)
**Prompt Engineering Strategy:**
- Use a structured system prompt that forces the LLM to output valid JSON (Director's Cut schema).
- Provide 3-shot examples of cinematic pacing for 8–10 min videos.
- Instruct the LLM to embed "beat drop cues" in the script where visual intensity should spike.
- **Two-pass generation**:
  1. **Pass 1**: Write the narrative script (spoken word only).
  2. **Pass 2**: Feed the script back to Groq to generate the Director's Cut JSON, ensuring timestamps align with word-per-minute pacing (~150 WPM for documentary style).

### 4.2 Asset Orchestrator
| Source | Role | Cache Strategy |
|--------|------|----------------|
| **Pexels** | B-roll texture & environment | Downloaded to `./cache/pexels/{hash}.mp4`. TTL: 7 days. |
| **User Library** | Branded infographics, diagrams, premium clips | Mounted volume or HF Dataset. Loaded at boot. |
| **Animation Factory** | Code-driven motion graphics | Pre-rendered to `./cache/mographs/{type}_{duration}.mov` (alpha). |

### 4.3 The Animation Factory (React + Framer Motion)
**Purpose:** Generate reusable, high-quality motion graphic clips that feel like After Effects work — but are code-driven.

**How it works:**
- A standalone Node.js/React app exists inside the container.
- It receives props via JSON: `type`, `duration`, `theme`, `data_points`, `color_palette`.
- It renders the animation using **Framer Motion** and **SVG/Canvas** in a headless Chromium browser (Playwright).
- The browser tab is captured via Chrome DevTools Protocol (CDP) screenshots at 30fps, piped into FFmpeg in real-time to encode a video clip.
- **Output**: Short, seamless-looped or fixed-duration clips (e.g., `neural_pulse_5s.mov`, `dopamine_spike_8s.mov`).
- These clips are stored in the Animation Asset Library and treated like any other footage by the Compositor.

**Why this works for performance:**
- Animation clips are rendered **once** and cached. The main video assembly does NOT need a browser — it uses pure FFmpeg overlays, which is extremely fast.
- This separates the heavy web-render work from the fast assembly work.

**Example Framer Motion concepts to pre-build:**
- Neural Network Pulse (nodes lighting up along a synapse path)
- Neurotransmitter Flow (particles moving through a channel)
- Brain Region Highlight (SVG brain map with glowing regions)
- Data Reveal (bar charts growing with spring physics)
- Text Disintegration (typography exploding into particles on a key beat)

### 4.4 The Cinematic Compositor (FFmpeg Engine)
**Philosophy:** Every frame must have motion. Every cut must have intent.

**Key FFmpeg Filtergraphs:**
- **Motion from Stillness**: `zoompan=z='zoom+0.001':d=125` combined with `crop` panning.
- **Layered Compositing**: `overlay` with `format=yuv420` and alpha channel support for motion graphic clips.
- **Cinematic Transitions**: `xfade` (gltransition library) for cross-zoom, directional wipes, and light-leak dissolves.
- **Dynamic Pacing**: Scene duration is not fixed. The engine shaves or extends padding based on narration length + beat proximity. Cuts happen on the *off-beat* or *down-beat* depending on mood.
- **Color Grading**: `eq` + `curves` + `hue` filters, or fast LUT application via `lut3d`. Mood determines the LUT.

**Anti-Slideshow Rules (Hardcoded):**
1. No image displayed > 3 seconds without zoom/pan or overlay.
2. No stock clip used > 15 seconds without a cut to another angle.
3. Every scene must have ≥2 visual layers (background + overlay/animation).
4. Text cannot sit static; it must fade, slide, or scale in.
5. Transitions must vary; no repeat of the same transition within 30 seconds.

### 4.5 Audio & Music Engine
**Narration:**
- `edge-tts` (Python) with voices like `en-US-GuyNeural` or `en-GB-SoniaNeural`.
- SSML injection for pauses (`<break time="500ms"/>`) and emphasis based on punctuation.

**Background Music:**
- **Option A (Recommended)**: Integrate a royalty-free music API (e.g., Epidemic Sound, Artlist) or a curated local library of stems categorized by mood/BPM. The engine picks a track, time-stretches it to fit video length (with `rubberband` or `atempo`), and loops seamlessly.
- **Option B (Generative AI)**: If copyright is not a concern and an API is available (e.g., Suno, Udio), generate a unique track per video. *Decision needed.*

**SFX:**
- AI-generated SFX via an API (e.g., ElevenLabs Sound Effects) for unique whooshes, risers, and impacts.
- Or a pre-curated Freesound library for speed.

**Mixing:**
- Narration at `-6dB` RMS.
- Music ducked to `-24dB` during speech (dynamic sidechain via `acompressor` or volume envelope automation).
- SFX peaks at `-10dB`.

### 4.6 Beat Sync & Audio-Reactive Motion
- **Tempo Extraction**: `librosa.beat.beat_track` maps every beat frame.
- **Reactive Parameters**: These parameters are passed into the FFmpeg filter_complex as variables:
  - **Zoom intensity**: On strong beats, `zoompan` zooms 1.0 → 1.05 over 10 frames.
  - **Overlay opacity**: Motion graphic alpha pulses 0.8 → 1.0 on the beat.
  - **Transition speed**: Cuts on beat snaps happen within 2 frames for snappy feel; off-beat transitions use 12-frame dissolves for calm feel.
- **Beat Grid**: A shared JSON file (`beat_grid.json`) is produced by the Audio Engine and consumed by the Compositor so video and audio are perfectly aligned in a single pass.

---

## 5. Data Models (Key JSON Schemas)

### 5.1 Director's Cut (from Groq)
```json
{
  "video_id": "uuid",
  "title": "The Dopamine Fasting Protocol",
  "target_duration_sec": 540,
  "mood_arc": ["curious", "tense", "revelatory", "calm"],
  "scenes": [
    {
      "scene_id": "s01",
      "start_sec": 0,
      "duration_sec": 45,
      "narration": "In 2019, a Silicon Valley engineer discovered...",
      "mood": "curious",
      "pacing": "medium",
      "visual_keywords": ["silicon valley", "engineer", "computer code"],
      "animation_trigger": "neural_network_pulse",
      "color_grade": "cool_blue",
      "beat_sync_intensity": 0.3,
      "b_roll_strategy": "single",
      "text_overlay": { "text": "Dopamine Fasting", "style": "title_reveal" },
      "transition_out": "auto"
    }
  ]
}
```

### 5.2 Beat Grid (from Audio Engine)
```json
{
  "bpm": 128.5,
  "beats": [0.00, 0.47, 0.93, 1.40, ...],
  "onsets": [0.00, 2.34, 4.12, ...],
  "energy": [0.2, 0.8, 0.3, ...]
}
```

### 5.3 Animation Asset Manifest
```json
{
  "assets": [
    {
      "id": "neural_network_pulse",
      "type": "framer_motion_svg",
      "duration": 5,
      "loop": true,
      "alpha": true,
      "tags": ["brain", "neurons", "tech"]
    }
  ]
}
```

---

## 6. Performance & "Real-Time" Assembly Strategy

**The Challenge:** 8–10 minutes of 1080p compositing is heavy. A pure Python/browser frame-by-frame approach would take 30+ minutes.

**The Solution: Three-Tier Pipeline**

| Tier | Speed | Role |
|------|-------|------|
| **Fast Assembly** | ~1.5x–3x real-time | FFmpeg `filter_complex` subprocesses (no browser) |
| **Parallel Scenes** | 4–8 scenes at once | `ProcessPoolExecutor` based on CPU cores |
| **Pre-Rendered Mographs** | Instant overlay | Already-encoded clips, FFmpeg `overlay` only |

**Optimizations:**
1. **Scene-based Parallelism**: Each scene is a self-contained FFmpeg job. 10 min video ≈ 12 scenes → render in parallel on 4 cores = ~3x speedup.
2. **Single-pass Compositing**: Design `filter_complex` graphs so each scene renders in one FFmpeg invocation (no intermediate files).
3. **Hardware**: Hugging Face CPU Spaces can run multi-core. FFmpeg is highly optimized for SIMD. If a GPU is available (ZeroGPU), use `h264_nvenc` for encoding. Otherwise, `libx264` with `veryfast` preset for speed, `medium` for final export.
4. **Streaming Output**: While final export is not instant, the architecture is designed so that the *assembly* (the decision-making) happens in seconds; the *encode* is the bottleneck. This is "real-time assembly" in the sense of edit decision lists, not live streaming.

---

## 7. Quality Guardrails (Anti-Slideshow System)

To guarantee the output never looks like a PowerPoint:

1. **Motion Mandate**: Every asset entering the timeline gets a motion filter applied (zoom, pan, or drift) unless it is already a moving stock clip.
2. **Cut Density**: Average shot length (ASL) target is 4–6 seconds. The engine enforces a cut every 3–8 seconds depending on pacing.
3. **Layer Depth**: Minimum 2 layers per scene (background + 1 overlay). High-energy scenes get 3 layers (background + mograph + text).
4. **Generative Variance**: A `random.seed` derived from the script hash ensures the edit decisions (transitions, zoom direction, color grade) are deterministic but *unique per video*. No two videos share the same edit pattern.
5. **Cinematic LUTs**: 8 pre-baked color grades (LUTs) mapped to moods. No raw footage leaves the system without grading.
6. **Audio Polish**: Normalized loudness (`-14 LUFS` for YouTube). Music never competes with voice. SFX punctuate, not annoy.

---

## 8. Deployment on Hugging Face Spaces

**Space Type**: `Docker` (not Gradio/Streamlit default).

**Why Docker?**
- We need `ffmpeg`, `node.js`, `python`, `playwright` dependencies, and system fonts in one image.
- We need persistent storage for caches (Hugging Face Spaces allow a writable `/data` directory).

**Dockerfile Overview:**
- Base: `ubuntu:22.04`
- Install: `ffmpeg`, `python3.11`, `nodejs-20`, `chromium` (for Playwright), `librosa` dependencies.
- Python packages: `fastapi`, `uvicorn`, `edge-tts`, `librosa`, `soundfile`, `requests`, `python-dotenv`.
- Node packages: `react`, `react-dom`, `framer-motion`, `playwright`, `http-server`.
- Expose port for FastAPI + optional React UI.

**File Structure in Space:**
```
/workspace
├── /app
│   ├── main.py                 # FastAPI orchestrator
│   ├── brain.py                # Groq API wrapper & prompt templates
│   ├── compositor.py           # FFmpeg scene assembler
│   ├── audio_engine.py         # Edge TTS, music, SFX, beat analysis
│   ├── asset_manager.py        # Pexels fetch + user asset indexing
│   ├── cache/                  # Downloaded videos, TTS, music
│   └── renders/                # Final output MP4s
├── /mograph_factory            # React + Framer Motion app
│   ├── src/
│   ├── public/
│   └── render_clip.js          # Playwright headless capture script
├── /assets                     # User-provided high-quality library
│   ├── images/
│   ├── clips/
│   └── svgs/
└── Dockerfile
```

**Scaling / Limits:**
- HF Free CPU Spaces have ~16GB RAM and 2 vCPU. Parallel scene rendering should be capped at `cpu_count - 1`.
- Video output is stored in `/data` (persistent) and can be served via FastAPI static file mount.
- For heavy use, consider a `ZeroGPU` upgrade or external compute (modal.com, runpod) triggered from HF.

---

## 9. Tech Stack Summary

| Layer | Technology | Justification |
|-------|------------|---------------|
| **Orchestration** | Python 3.11 + FastAPI | Best for FFmpeg subprocess control, async task management |
| **LLM Brain** | Groq API (`llama-3.3-70b` or `mixtral-8x7b`) | Fast inference, cheap, excellent JSON adherence |
| **Script / JSON** | Pydantic | Strict validation of Director's Cut schema |
| **TTS** | `edge-tts` (Python) | High quality, free, fast, natural prosody |
| **Stock Video** | Pexels API | Free tier, high-quality short clips, no attribution required |
| **Animation Source** | React + Framer Motion + Playwright | User-requested stack; captured to video clips |
| **Video Compositing** | FFmpeg (CLI + `ffmpeg-python`) | Industry standard, fast, infinite filter flexibility |
| **Transitions** | `gltransition` (FFmpeg) | GPU-accelerated cinematic transitions |
| **Audio Analysis** | `librosa` + `soundfile` | Beat detection, tempo, onset strength |
| **Music/SFX** | Curated local stem library (categorized by mood/BPM) | Zero copyright risk, fast, deterministic beat-matching |
| **Deployment** | Hugging Face Docker Space | Easy sharing, persistent `/data`, free tier available |
| **UI (Optional)** | React static build or Gradio | For triggering builds and previewing Director's Cut |

---

## 10. Open Decisions & Recommended Next Steps

Before we begin implementation, we need to lock in three critical decisions:

### ✅ LOCKED DECISION 1: Music & SFX Strategy → Option A
**Curated local library of royalty-free stems** (categorized by mood/BPM), algorithmically mixed/looped per video. Zero copyright risk, fast, deterministic, easy to beat-match with `librosa`. AI-generated music (Suno/Udio) may be added later as a premium upgrade module.

### ✅ LOCKED DECISION 2: Framer Motion → Video Pipeline → Option B
**On-demand rendering per video.** The Animation Factory renders Framer Motion clips at build-time based on the Director's Cut JSON (e.g., specific data values, color palettes, duration tweaks). This adds ~2–5 minutes of headless-browser capture per video but allows true generative motion graphics (no two videos share the same mograph asset). 

> **Performance Budget Note:** With a 10-minute video target of <20 min total render, on-demand mograph rendering is acceptable. We will parallelize clip rendering (4–6 clips at once) and keep clips short (3–8 sec). Estimated mograph phase: 90–120 sec. Remaining ~16–17 min for FFmpeg assembly is well within the parallel-scene pipeline budget.

### ✅ LOCKED DECISION 3: Definition of "Real-Time" → Option A
**Fast batch rendering:** 10-minute video must output in <20 minutes (sub-2×). This is achieved via parallel scene FFmpeg jobs, single-pass compositing, and optimized `libx264` presets. "Real-time" refers to rapid automated edit-decision and assembly, not live streaming.

> **HF Spaces Implication:** Free CPU Spaces (2 vCPU, 16 GB RAM) will run scene renders sequentially or with limited parallelism. To hit the <20 min target consistently, we may cap parallel scene jobs to 2 concurrent FFmpeg processes. If render times exceed budget, we will add a queue/worker pattern (e.g., Celery or async `ProcessPoolExecutor`) rather than streaming.

---

## 11. Implementation Roadmap (Suggested Order)

1. **Phase 0: Foundation**
   - Set up HF Docker Space with Python, Node, FFmpeg, Playwright.
   - Build the FastAPI skeleton and `/generate` endpoint.

2. **Phase 1: The Brain & Audio**
   - Integrate Groq API for script + Director's Cut JSON.
   - Integrate `edge-tts` and build the Audio Engine with `librosa` beat detection.
   - Build a local music/SFX library (pending Decision 1).

3. **Phase 2: Asset Pipeline**
   - Pexels API integration + caching.
   - User asset library mounting + indexing.
   - Build the first 5 Framer Motion infographic clips and the Playwright capture pipeline.

4. **Phase 3: The Generative Compositor**
   - Build the FFmpeg rule engine with transitions, color grades, and Ken Burns.
   - Implement parallel scene rendering.
   - Integrate beat-sync motion overlays.

5. **Phase 4: Polish & Quality**
   - Anti-slideshow guardrails & validation.
   - Final audio mastering (`loudnorm`).
   - End-to-end testing with 3 full 8-minute videos.

6. **Phase 5: UI & Deployment**
   - Build a minimal React/Gradio UI to trigger generation and show previews.
   - Deploy to HF Space.

---

*End of Plan. Ready to finalize the three open decisions and proceed to Phase 0.*
