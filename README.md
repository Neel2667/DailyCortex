# CORTEX RENDER — Generative Cinematic Video Engine

> **Autonomous 8–10 minute brain hack documentaries.** No templates. No dead frames. Pure generative motion.

## Architecture Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   FastAPI   │───▶│    Brain    │───▶│  Animation  │───▶│   FFmpeg    │
│ Orchestrator│    │  (Groq LLM) │    │   Factory   │    │ Compositor  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │  Pexels API │
                                       │  + User Lib │
                                       └─────────────┘
```

## Quick Start (Local)

```bash
# 1. Install Python deps
pip install -r requirements.txt

# 2. Install Node deps + build mograph factory
cd mograph_factory && npm install && npm run build

# 3. Set keys
cp .env.example .env
# Edit .env with GROQ_API_KEY and PEXELS_API_KEY

# 4. Run
uvicorn app.main:app --reload --port 8000

# 5. Generate a video
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "The Dopamine Detox Protocol", "target_duration": 540}'
```

## Hugging Face Spaces

This project is designed to run as a **Docker Space** on Hugging Face.

1. Push this repo to a Hugging Face Docker Space.
2. Set `GROQ_API_KEY` and `PEXELS_API_KEY` in Space Secrets.
3. The Space will expose the FastAPI orchestrator on port 7860.

## Directory Structure

```
.
├── Dockerfile                  # Multi-stage build (Python + Node + FFmpeg + Chromium)
├── entrypoint.sh               # Boot sequence for HF Space
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables
│
├── app/                        # FastAPI + Pipeline orchestration
│   ├── main.py                 # API endpoints & job queue
│   ├── config.py               # Pydantic settings
│   ├── models.py               # JSON schemas (Director's Cut, Theme, etc.)
│   ├── brain.py                # Groq LLM integration (2-pass generation)
│   ├── asset_manager.py        # Pexels API + user asset library
│   ├── audio_engine.py         # Edge TTS, librosa beat detection, mixing
│   └── compositor.py           # FFmpeg generative scene assembly
│
├── mograph_factory/            # React + Framer Motion + Playwright
│   ├── index.html              # 1920x1080 transparent canvas
│   ├── src/
│   │   ├── main.tsx            # React entry point
│   │   └── App.tsx             # Component registry & prop injection
│   ├── scripts/
│   │   └── render-clip.js      # Playwright → FFmpeg capture pipeline
│   └── package.json            # React, Framer Motion, Playwright, Vite
│
├── assets/                     # User-provided high-quality library
│   ├── images/
│   ├── clips/
│   └── svgs/
│
├── cache/                      # Pexels downloads, TTS, temp renders
└── renders/                    # Final output videos
```

## Generative Pipeline

1. **Topic Ingestion** — User provides a topic seed.
2. **Pass 1: Script** — Groq writes a 1200–1500 word narration script.
3. **Pass 2: Director's Cut** — Groq generates a JSON shot-list with:
   - Scene breakdowns (20–48 scenes, 10–45 sec each)
   - Theme Manifest (unique color system, typography, motion language)
   - Component assignments (BrainSVG, BarRaceChart, etc.)
   - Beat sync cues and transition rules
4. **Asset Procurement** — Pexels clips fetched, TTS generated, music stem selected.
5. **Animation Factory** — Playwright renders React/Framer Motion components to transparent video clips.
6. **Audio Analysis** — `librosa` extracts BPM, beat timestamps, onset energy.
7. **Generative Compositor** — FFmpeg assembles layers with:
   - Ken Burns, crossfades, color grades, text overlays
   - Beat-synced zooms and opacity pulses
   - No-repeat transition engine
8. **Final Master** — Audio loudnorm (-14 LUFS), H.264 export, faststart.

## Quality Guardrails

- **Every frame has 3+ animated layers.** No dead frames.
- **No repeated layout, transition, or text zone within 3 scenes.**
- **Stock clips max 8 seconds.** Cut or crossfade before stagnation.
- **ASL target: 4–7 seconds.** No slideshow pacing.
- **Audio ducks -18dB during narration.** Sidechain compression via FFmpeg.

## License

MIT — The generative engine framework. User is responsible for music/SFX licensing and Pexels attribution compliance.
