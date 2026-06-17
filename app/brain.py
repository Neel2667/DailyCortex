"""The Director — Groq LLM integration for script and visual direction.

Phase 1: Now generates the Hook Cadence (5-7 nested open loops) before scenes,
then assigns hook_role, visual_intensity, and keyframes to every scene.
"""
import json
import asyncio
from typing import Optional

import httpx
from app.config import get_settings
from app.models import DirectorCut, ThemeManifest, Scene, HookRole, HookCadence, OpenLoop, MicroHook, Keyframe

settings = get_settings()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

PASS1_SYSTEM_PROMPT = """You are a senior documentary scriptwriter for a premium YouTube channel specializing in brain science and cognitive psychology. Your audience is 18-34, curious, and values actionable insights.

Write a spoken-word narration script for an 8-10 minute video on the requested topic. The script should be:
- Engaging, conversational, and scientifically accurate
- Structured with clear narrative arcs: Hook, Problem, Science, Hack, Proof, Payoff
- Approximately 140-160 words per minute (1200-1500 words total for 8-10 min)
- Mark natural pauses with [PAUSE: 0.5s] and emphasis cues with [EMPHASIS]
- Include timestamps for major section breaks in [SECTION: HH:MM:SS] format
- End with a clear CTA and a tease for the next video

CRITICAL: Embed 5-7 CURIOUSITY LOOPS throughout the script. Each loop should:
1. Open with a question, promise, or mystery (tease line)
2. Close with the answer, reveal, or demonstration (payoff line) 2-5 minutes later
3. At the climax (70-80% mark), close 2-3 loops simultaneously for maximum dopamine release
4. The very first hook must open in the first sentence (no intro, no welcome)
5. Include a callback to the first hook in the final 30 seconds (memory loop)

Example loop structure:
- Loop 1 (Big Promise): "There's a 2-minute brain hack that makes procrastination impossible." [opens 0:00] → closes at 7:30
- Loop 2 (Science Mystery): "Scientists discovered this isn't about willpower." [opens 0:45] → closes at 2:30
- Loop 3 (Stat Shock): "One in five adults procrastinate, but the scary number is what happens after 24 hours." [opens 2:30] → closes at 4:00
- Loop 4 (Paradox): "The more you tell yourself to focus, the less you actually focus." [opens 4:00] → closes at 6:00
- Loop 5 (Trick Tease): "It's called the 2-Minute Initiation Protocol." [opens 6:00] → closes at 7:30

Output ONLY the narration text with markers. Do not include any other formatting."""

PASS2_SYSTEM_PROMPT = """You are a cinematic director AI. You receive a documentary narration script and produce a detailed shot-list called the "Director's Cut."

You MUST follow this EXACT procedure. Do not skip steps:

STEP 1 — IDENTIFY OPEN LOOPS (5-7 loops)
Read the script and identify all curiosity gaps. For each loop:
- loop_id: L1, L2, L3...
- tease_line: the exact question/promise from the script
- tease_at_sec: when it first appears (absolute timestamp)
- payoff_line: the exact answer/reveal from the script
- payoff_at_sec: when it closes (absolute timestamp, 2-5 minutes later)
- visual_tension: which scenes open, escalate, and pay off this loop
- intensity_arc: visual intensity values (0.0-1.0) rising toward 1.0 at payoff
- loop_type: "big" (3-4 min) or "medium" (2-3 min) or "micro" (15-30 sec)

STEP 2 — MAP TENSION ARC
For every scene, assign:
- hook_role: "tease" (opens a loop), "escalation" (builds tension), "payoff" (closes a loop), "rest" (breathes between loops), "callback" (references earlier hook), or "bridge" (connects sections)
- visual_intensity: 0.0-1.0 (tease=0.8, escalation=0.3-0.6, payoff=1.0, rest=0.2, callback=0.7, bridge=0.4)

STEP 3 — PLACE MICRO-HOOKS
Every 15-30 seconds of the video, place a micro-hook:
- at_sec: absolute timestamp
- line: the exact hook line from narration
- visual_snap: the visual action that creates the snap (text_color_shift, split_screen_compare, counter_slow_build, pulse_burst, text_zoom_in, glitch_flash, overlay_swap, camera_pan)

STEP 4 — IDENTIFY CALLBACK
The final 30 seconds must reference the first hook. Capture:
- callback_reference: the exact intro hook line being referenced

STEP 5 — GENERATE THEME MANIFEST
Choose a color system, typography, and motion language that matches the topic's emotional tone.

STEP 6 — GENERATE SCENES (20-48 scenes, 10-45 sec each)
For each scene, you must output:
- scene_id: S01, S02...
- start_sec: absolute timestamp
- duration_sec: 10-45 seconds (never more, never less)
- hook_role: from STEP 2
- visual_intensity: from STEP 2
- keyframes: 3-4 internal micro-events (use at_sec relative to scene start, 0-45 sec)
  * visual_action: text_slam, data_enter, overlay_pulse, counter_tick, comparison_reveal, particle_burst, color_shift, zoom_in, zoom_out, icon_appear, line_draw, split_open, fade_swap
  * element: the visual element identifier
- narration: the exact spoken text for this scene (split from the full script)
- mood: curious, tense, euphoric, calm, mysterious, urgent, hopeful
- pacing: slow, medium, fast, burst
- visual_keywords: 2-5 Pexels search terms
- animation_trigger: component ID from registry
- color_grade: warm_gold, cool_blue, high_contrast_mono, neural_green, clinical_cyan, deep_purple, amber_dawn, midnight
- beat_sync_intensity: 0.0-1.0 (higher for action/payoff, lower for rest/explanatory)
- b_roll_strategy: single, layered, picture_in_picture
- text_overlay: text, style, position, accent_words
- transition_out: auto or specific transition
- layout_family: center_hero, split_screen, full_text, data_dominant, footage_dominant, overlay_heavy, minimal

CRITICAL RULES:
- NO DEAD FRAMES: Every scene must have 3-4 keyframes with visual actions
- NO REPEAT LAYOUTS: The same layout_family cannot appear in 2 consecutive scenes
- NO REPEAT TRANSITIONS: Never use the same transition twice in a row
- COLOR ROTATION: Alternate between at least 2 color grades within each chapter
- PAYOFF SCENES: Must be the most visually intense (intensity 1.0), with all keyframes firing
- REST SCENES: Still need particles, breathing text, ambient motion (intensity 0.2)
- CHAPTER STRUCTURE: 4-6 chapters (Hook, Science, Hack, Payoff), 5-8 scenes per chapter
- THE FIRST SCENE: Must start with a tease (hook_role="tease", intensity=0.8). No intro, no logo, no "welcome back."
- THE FINAL SCENE: Must be a callback (hook_role="callback") referencing the first hook

You must output a valid JSON object. Here is the exact schema:

{
  "video_id": "string",
  "title": "string",
  "target_duration_sec": integer (480-600),
  "mood_arc": ["curious", "tense", "revelatory", "calm", "hopeful"],
  "theme_manifest": {
    "theme_id": "string",
    "topic_mood": "string",
    "color_system": {
      "void": "#0a0e27", "primary": "#hex", "secondary": "#hex", "tertiary": "#hex", "accent": "#hex", "text": "#f4f4f5", "text_dim": "#a1a1aa"
    },
    "typography": { "headline": "Space Grotesk", "body": "Inter", "accent_font": "Fraunces Italic" },
    "motion_language": { "easing": "cubic-bezier(0.16, 1, 0.3, 1)", "stagger_base": 0.15, "particle_density": 130, "grid_opacity": 0.025, "grain_intensity": 0.06 }
  },
  "hook_cadence": {
    "open_loops": [
      {
        "loop_id": "L1",
        "tease_line": "string",
        "tease_at_sec": 0.0,
        "payoff_line": "string",
        "payoff_at_sec": 0.0,
        "visual_tension": { "tease_scene": "S01", "escalation_scenes": ["S02", "S03"], "payoff_scene": "S22" },
        "intensity_arc": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        "loop_type": "big|medium|micro"
      }
    ],
    "micro_hooks": [
      { "at_sec": 0.0, "line": "string", "visual_snap": "text_color_shift|split_screen_compare|counter_slow_build|pulse_burst|text_zoom_in|glitch_flash|overlay_swap|camera_pan" }
    ],
    "callback_reference": "string",
    "tension_peak_sec": 0.0
  },
  "scenes": [
    {
      "scene_id": "S01",
      "start_sec": 0,
      "duration_sec": 15,
      "hook_role": "tease|escalation|payoff|rest|callback|bridge",
      "visual_intensity": 0.0-1.0,
      "keyframes": [
        { "at_sec": 0, "visual_action": "text_slam", "element": "hero_title" },
        { "at_sec": 5, "visual_action": "particle_burst", "element": "particle_field" },
        { "at_sec": 10, "visual_action": "data_enter", "element": "stat_counter" }
      ],
      "narration": "exact spoken text",
      "mood": "curious|tense|euphoric|calm|mysterious|urgent|hopeful",
      "pacing": "slow|medium|fast|burst",
      "visual_keywords": ["pexels keywords"],
      "animation_trigger": "QuestionBomb|StatShock|BrainScan|StepCard|...",
      "color_grade": "warm_gold|cool_blue|high_contrast_mono|neural_green|clinical_cyan|deep_purple|amber_dawn|midnight",
      "beat_sync_intensity": 0.0-1.0,
      "b_roll_strategy": "single|layered|picture_in_picture",
      "text_overlay": { "text": "", "style": "title_reveal|subtitle_burn|pull_quote|data_label|kicker", "position": "center", "accent_words": [] },
      "transition_out": "auto|crossfade|light_leak_wipe|directional_wipe|zoom_in|zoom_out|glitch_skip|radial_reveal|slide_left|slide_right|iris_close|motion_blur|dissolve_glow",
      "layout_family": "center_hero|split_screen|full_text|data_dominant|footage_dominant|overlay_heavy|minimal"
    }
  ]
}

Choose animation_trigger from: QuestionBomb, StatShock, MythBust, StoryTeaser, PersonalMirror, BrainScan, StudyDrop, ComparisonSplit, TimelineFlow, DataInfographic, ExpertQuote, StepReveal, HabitLoop, ProtocolGrid, QuickWin, ToolShowcase, TransformationSummary, CTAPulse, NextHook, CreditRoll, ParticleField, KineticType, BrainSVG, BarRaceChart, FloatingCard, NeuralNetwork, ProgressTaskList, ActionPill, TimerRing, FlourishLines, LightLeakSweep, GlitchText."""


async def generate_directors_cut(topic: str, target_duration: int = 540, style_bias: Optional[str] = None) -> DirectorCut:
    """Two-pass generation: Script → Director's Cut with Hook Cadence."""
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    # --- Pass 1: Script with embedded curiosity loops ---
    pass1_payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": PASS1_SYSTEM_PROMPT},
            {"role": "user", "content": f"Topic: {topic}\nTarget duration: {target_duration} seconds\nStyle bias: {style_bias or 'cinematic documentary, no stock-photo feel, high motion density, 5-7 nested curiosity loops, dopamine-driven pacing'}"},
        ],
        "temperature": 0.75,
        "max_tokens": 4096,
    }

    async with httpx.AsyncClient(timeout=120) as client:
        r1 = await client.post(GROQ_API_URL, headers=headers, json=pass1_payload)
        r1.raise_for_status()
        script_text = r1.json()["choices"][0]["message"]["content"]

    # --- Pass 2: Director's Cut + Hook Cadence ---
    pass2_payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": PASS2_SYSTEM_PROMPT},
            {"role": "user", "content": f"NARRATION SCRIPT:\n{script_text}\n\nGenerate the Director's Cut JSON for this script. Target total duration: {target_duration} seconds. Follow ALL 6 steps in the system prompt. The first scene MUST be a tease (hook_role=tease, visual_intensity=0.8). The final scene MUST be a callback (hook_role=callback). Include 5-7 open loops. Every scene MUST have 3-4 keyframes."},
        ],
        "temperature": 0.65,
        "max_tokens": 4096,
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=120) as client:
        r2 = await client.post(GROQ_API_URL, headers=headers, json=pass2_payload)
        r2.raise_for_status()
        raw_json = r2.json()["choices"][0]["message"]["content"]
        dc_dict = json.loads(raw_json)

    # Validate hook cadence exists
    if "hook_cadence" not in dc_dict:
        raise ValueError("Groq output missing hook_cadence. Retry with stronger prompt.")
    if len(dc_dict.get("hook_cadence", {}).get("open_loops", [])) < 3:
        raise ValueError(f"Only {len(dc_dict['hook_cadence']['open_loops'])} open loops found. Need 5-7. Retry with temperature=0.75.")

    # Validate first scene is tease
    scenes = dc_dict.get("scenes", [])
    if scenes and scenes[0].get("hook_role") != "tease":
        scenes[0]["hook_role"] = "tease"
        scenes[0]["visual_intensity"] = max(scenes[0].get("visual_intensity", 0.5), 0.8)
    if scenes and scenes[-1].get("hook_role") != "callback":
        scenes[-1]["hook_role"] = "callback"
        scenes[-1]["visual_intensity"] = max(scenes[-1].get("visual_intensity", 0.5), 0.7)

    return DirectorCut(**dc_dict)
