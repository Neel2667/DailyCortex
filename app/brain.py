"""The Director — Groq LLM integration for script and visual direction."""
import json
import asyncio
from typing import Optional
from dataclasses import dataclass

import httpx
from app.config import get_settings
from app.models import DirectorCut, ThemeManifest, Scene, Mood, ColorGrade, LayoutFamily, TransitionType

settings = get_settings()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# System prompts for two-pass generation
PASS1_SYSTEM_PROMPT = """You are a senior documentary scriptwriter for a premium YouTube channel specializing in brain science and cognitive psychology. Your audience is 18-34, curious, and values actionable insights.

Write a spoken-word narration script for an 8-10 minute video on the requested topic. The script should be:
- Engaging, conversational, and scientifically accurate
- Structured with clear narrative arcs: Hook, Problem, Science, Hack, Proof, Payoff
- Approximately 140-160 words per minute (1200-1500 words total for 8-10 min)
- Mark natural pauses with [PAUSE: 0.5s] and emphasis cues with [EMPHASIS]
- Include timestamps for major section breaks in [SECTION: HH:MM:SS] format
- End with a clear CTA and a tease for the next video

Output ONLY the narration text with markers. Do not include any other formatting."""

PASS2_SYSTEM_PROMPT = """You are a cinematic director AI. You receive a documentary narration script and produce a detailed shot-list called the "Director's Cut."

You must output a valid JSON object following this schema exactly:

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
  "scenes": [
    {
      "scene_id": "S01",
      "start_sec": 0,
      "duration_sec": 20-45,
      "narration": "exact spoken text for this scene",
      "mood": "curious|tense|euphoric|calm|mysterious|urgent|hopeful",
      "pacing": "slow|medium|fast|burst",
      "visual_keywords": ["pexels search keywords"],
      "animation_trigger": "component_id from registry",
      "color_grade": "warm_gold|cool_blue|high_contrast_mono|neural_green|clinical_cyan|deep_purple|amber_dawn|midnight",
      "beat_sync_intensity": 0.0-1.0,
      "b_roll_strategy": "single|layered|picture_in_picture",
      "text_overlay": { "text": "", "style": "title_reveal|subtitle_burn|pull_quote|data_label|kicker", "position": "center", "accent_words": [] },
      "transition_out": "auto|crossfade|light_leak_wipe|...",
      "layout_family": "center_hero|split_screen|full_text|data_dominant|footage_dominant|overlay_heavy|minimal"
    }
  ]
}

CRITICAL RULES:
- Scene duration must be 10-45 seconds. No longer. No shorter.
- Do not repeat the same layout_family in consecutive scenes.
- Alternate between footage-heavy and data-heavy scenes.
- Include 5-8 scenes per thematic "chapter" (total 20-48 scenes for 8-10 min).
- Every scene MUST have a visual_keywords array (for Pexels search) AND an animation_trigger.
- The color_grade should vary across scenes to avoid monotony.
- Beat sync intensity should be higher (>0.6) for action/hack scenes and lower (<0.3) for calm/explanatory scenes.
- Choose animation_trigger from: ParticleField, KineticType, BrainSVG, BarRaceChart, FloatingCard, StepCard, TimerRing, ComparisonBars, NeuralNetwork, ProgressTaskList, SparkLine, HeatmapGrid, TimelineFlow, SynapsePulse, BeforeAfterFlip, MockupDevice, GlitchText, ActionPill, FlourishLines.
- For the Theme Manifest, choose colors that match the topic's emotional tone. Use Space Grotesk, Inter, and Fraunces Italic exactly."""


async def generate_directors_cut(topic: str, target_duration: int = 540, style_bias: Optional[str] = None) -> DirectorCut:
    """Two-pass generation: Script → Director's Cut."""
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    # --- Pass 1: Script ---
    pass1_payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": PASS1_SYSTEM_PROMPT},
            {"role": "user", "content": f"Topic: {topic}\nTarget duration: {target_duration} seconds\nStyle bias: {style_bias or 'cinematic documentary, no stock-photo feel, high motion density'}"},
        ],
        "temperature": 0.75,
        "max_tokens": 4096,
    }

    async with httpx.AsyncClient(timeout=120) as client:
        r1 = await client.post(GROQ_API_URL, headers=headers, json=pass1_payload)
        r1.raise_for_status()
        script_text = r1.json()["choices"][0]["message"]["content"]

    # --- Pass 2: Director's Cut ---
    pass2_payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": PASS2_SYSTEM_PROMPT},
            {"role": "user", "content": f"NARRATION SCRIPT:\n{script_text}\n\nGenerate the Director's Cut JSON for this script. Target total duration: {target_duration} seconds."},
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

    # Validate and return Pydantic model
    return DirectorCut(**dc_dict)
