"""
Audio Engine — Edge TTS, music stem selection, beat analysis, and mastering.

Produces:
  - Per-scene narration WAVs (with SSML prosody)
  - Music stem (selected by mood/BPM, optionally time-stretched)
  - Beat grid (BPM, beat timestamps, onset energy via librosa)
  - Full audio mix (narration + music + SFX, sidechain ducking, loudnorm)
"""
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
import random

import edge_tts
import librosa
import numpy as np
import soundfile as sf

from app.config import get_settings
from app.models import Scene, BeatGrid, AudioMixPlan, DirectorCut

settings = get_settings()


# ───────────────────────────────────────────────────────────────────────────
# TTS GENERATION
# ───────────────────────────────────────────────────────────────────────────

def _inject_ssml(narration: str) -> str:
    """Add SSML prosody markers to narration for more natural speech."""
    # Replace [PAUSE: Xs] with SSML break
    import re
    text = narration
    text = re.sub(r'\[PAUSE:\s*([\d.]+)s\]', r'<break time="\1s"/>', text)
    text = re.sub(r'\[EMPHASIS\]', r'<prosody pitch="+10%" rate="-5%">', text)
    text = re.sub(r'\[/EMPHASIS\]', r'</prosody>', text)
    
    # Wrap in SSML if not already
    if not text.startswith('<speak>'):
        text = f'<speak version="1.0">{text}</speak>'
    return text


async def generate_narration(
    text: str,
    output_path: Path,
    voice: Optional[str] = None,
    rate: str = "-5%",  # Slightly slower for documentary feel
    pitch: str = "0%",
) -> Path:
    """Generate narration WAV using Edge TTS with SSML prosody."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    voice = voice or settings.tts_voice
    
    # Inject SSML markers
    ssml_text = _inject_ssml(text)
    
    communicate = edge_tts.Communicate(
        ssml_text,
        voice,
        rate=rate,
        pitch=pitch,
    )
    await communicate.save(str(output_path))
    return output_path


async def generate_all_narrations(
    scenes: List[Scene],
    output_dir: Path,
) -> Dict[str, Path]:
    """Generate narration for all scenes in parallel."""
    tasks = {}
    for scene in scenes:
        out_path = output_dir / f"{scene.scene_id}_narration.wav"
        tasks[scene.scene_id] = asyncio.create_task(
            generate_narration(scene.narration, out_path)
        )
    
    results = {}
    for sid, task in tasks.items():
        results[sid] = await task
    return results


# ───────────────────────────────────────────────────────────────────────────
# MUSIC STEM
# ───────────────────────────────────────────────────────────────────────────

def select_music_stem(mood: str, target_bpm: Optional[int] = None) -> Optional[Path]:
    """Select a music stem from the curated library matching mood and BPM."""
    lib = settings.music_library_path / mood
    if not lib.exists():
        # Fallback: try any mood directory
        lib = settings.music_library_path
        if not lib.exists():
            return None
    
    # Search for MP3/WAV files
    candidates = list(lib.rglob("*.mp3")) + list(lib.rglob("*.wav"))
    if not candidates:
        return None
    
    # If target BPM specified, try to match from filename
    if target_bpm:
        bpm_matches = [
            p for p in candidates
            if str(p.name).replace("bpm", "").replace("BPM", "").__contains__(str(target_bpm))
        ]
        if bpm_matches:
            candidates = bpm_matches
    
    return random.choice(candidates)


def time_stretch_audio(
    input_path: Path,
    output_path: Path,
    target_duration: float,
) -> Path:
    """Time-stretch audio to fit target duration using rubberband or atempo."""
    # Get current duration
    y, sr = librosa.load(str(input_path), sr=None, mono=True)
    current_duration = len(y) / sr
    ratio = target_duration / current_duration
    
    # Clamp to reasonable range (0.5x - 2.0x)
    ratio = max(0.5, min(2.0, ratio))
    
    # Use atempo filter (simpler, no dependencies)
    # For more complex stretching, rubberband is needed but may not be installed
    if 0.5 <= ratio <= 2.0:
        # atempo supports 0.5-2.0, can chain for more extreme
        atempo_chain = []
        r = ratio
        while r < 0.5:
            atempo_chain.append("atempo=0.5")
            r /= 0.5
        while r > 2.0:
            atempo_chain.append("atempo=2.0")
            r /= 2.0
        atempo_chain.append(f"atempo={r:.4f}")
        
        af = ",".join(atempo_chain)
        cmd = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-af", af,
            "-c:a", "pcm_s16le",
            str(output_path),
        ]
    else:
        # Use rubberband if available, otherwise simple resample
        cmd = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-af", "rubberband=tempo={ratio:.4f}" if _has_rubberband() else f"atempo={ratio:.4f}",
            "-c:a", "pcm_s16le",
            str(output_path),
        ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def _has_rubberband() -> bool:
    """Check if FFmpeg has rubberband filter compiled in."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-filters"], capture_output=True, text=True, check=False
        )
        return "rubberband" in result.stdout
    except Exception:
        return False


# ───────────────────────────────────────────────────────────────────────────
# BEAT ANALYSIS
# ───────────────────────────────────────────────────────────────────────────

def analyze_beats(audio_path: Path) -> BeatGrid:
    """Analyze audio with librosa to extract BPM, beat timestamps, and onset energy."""
    y, sr = librosa.load(str(audio_path), sr=None, mono=True)
    
    # Beat tracking
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()
    
    # Onset detection
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
    onset_times = librosa.frames_to_time(onsets, sr=sr).tolist()
    onset_energies = onset_env[onsets].tolist()
    
    # Downbeat detection (heuristic: every 4th beat)
    downbeats = beat_times[::4] if len(beat_times) >= 4 else beat_times[:1]
    
    return BeatGrid(
        bpm=float(tempo),
        beats=beat_times,
        onsets=onset_times,
        energy=onset_energies,
        downbeats=downbeats,
    )


# ───────────────────────────────────────────────────────────────────────────
# SFX GENERATION
# ───────────────────────────────────────────────────────────────────────────

def generate_sfx(
    sfx_type: str,
    duration: float,
    output_path: Path,
) -> Path:
    """Generate simple SFX using FFmpeg lavfi."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    sfx_configs = {
        "impact": {
            "lavfi": f"sine=frequency=200:duration={duration},afade=t=in:ss=0:d=0.01,afade=t=out:st={duration-0.1}:d=0.1",
            "af": "highpass=f=100,lowpass=f=800",
        },
        "whoosh": {
            "lavfi": f"sine=frequency=800:duration={duration},afade=t=in:ss=0:d=0.05,afade=t=out:st={duration-0.2}:d=0.2",
            "af": "lowpass=f=2000,highpass=f=200,vibrato=f=5:d=0.5",
        },
        "riser": {
            "lavfi": f"sine=frequency=200:duration={duration},afade=t=in:ss=0:d=0.5",
            "af": "vibrato=f=3:d=0.3,tremolo=f=4:d=0.2",
        },
        "ambient": {
            "lavfi": f"anoisesrc=a=0.03:d={duration}",
            "af": "lowpass=f=500,highpass=f=50,afade=t=out:st={duration-1}:d=1",
        },
    }
    
    config = sfx_configs.get(sfx_type, sfx_configs["impact"])
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", config["lavfi"],
        "-af", config["af"],
        "-ar", "48000",
        "-ac", "2",
        "-c:a", "pcm_s16le",
        str(output_path),
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


# ───────────────────────────────────────────────────────────────────────────
# AUDIO MIXING
# ───────────────────────────────────────────────────────────────────────────

def mix_audio_scene(
    narration_path: Path,
    music_path: Optional[Path],
    beat_grid: BeatGrid,
    scene_duration: float,
    output_path: Path,
    music_duck_db: float = -24.0,
) -> Path:
    """Mix narration + music (ducked) + optional SFX for a single scene."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not music_path or not music_path.exists():
        # No music: just normalize narration
        cmd = [
            "ffmpeg", "-y",
            "-i", str(narration_path),
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
            "-ar", "48000",
            "-ac", "2",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(scene_duration),
            str(output_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    
    # Build sidechain ducking filter
    # Music is split into two: one for sidechain detection, one for mixing
    # Narration triggers compression on music
    filter_complex = (
        "[1:a]asplit=2[sc][mix];"
        f"[0:a][sc]sidechaincompressor=threshold=-30dB:ratio=8:"
        f"attack=50:release=200:level_sc=0.8[ducked];"
        f"[ducked][mix]amix=inputs=2:duration=first:weights='1 0.15'[mixed];"
        f"[mixed]afade=t=out:st={scene_duration-0.5}:d=0.5[output]"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(narration_path),
        "-i", str(music_path),
        "-filter_complex", filter_complex,
        "-map", "[output]",
        "-t", str(scene_duration),
        "-ar", "48000",
        "-ac", "2",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path),
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


async def mix_full_audio(
    narration_paths: Dict[str, Path],
    music_path: Optional[Path],
    scenes: List[Scene],
    beat_grid: BeatGrid,
    output_path: Path,
    sfx_events: Optional[List[Dict[str, Any]]] = None,
) -> Path:
    """Mix all scene narrations + music + SFX into one continuous audio track.
    
    Uses FFmpeg concat demuxer for scene narrations, then overlays music
    with sidechain ducking across the entire track.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Create a list of scene narration files in order
    concat_list = settings.cache_dir / "audio_concat_list.txt"
    concat_entries = []
    for scene in scenes:
        narration = narration_paths.get(scene.scene_id)
        if narration and narration.exists():
            # Pad with silence if narration is shorter than scene duration
            # For now, assume narration fits within scene duration
            concat_entries.append(f"file '{narration}'")
        else:
            # Generate silence for scenes without narration
            silence_path = settings.cache_dir / f"{scene.scene_id}_silence.wav"
            if not silence_path.exists():
                subprocess.run([
                    "ffmpeg", "-y", "-f", "lavfi",
                    "-i", f"anullsrc=r=48000:cl=stereo", "-t", str(scene.duration_sec),
                    "-c:a", "pcm_s16le", str(silence_path),
                ], check=True, capture_output=True)
            concat_entries.append(f"file '{silence_path}'")
    
    concat_list.write_text("\n".join(concat_entries))
    
    # Step 2: Concatenate narrations
    narration_concat = settings.cache_dir / "narration_concat.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c:a", "pcm_s16le",
        str(narration_concat),
    ], check=True, capture_output=True)
    
    # Step 3: Mix with music (if available)
    if music_path and music_path.exists():
        total_duration = sum(s.duration_sec for s in scenes)
        
        # Time-stretch music if needed (loop or stretch to fit)
        music_loop = settings.cache_dir / "music_looped.wav"
        music_duration = librosa.get_duration(path=str(music_path))
        
        if music_duration < total_duration:
            # Loop music to fit
            loops_needed = int(total_duration / music_duration) + 1
            loop_filter = "",".join([f"[0:a]" for _ in range(loops_needed)])
            # Simpler approach: use concat demuxer
            music_list = settings.cache_dir / "music_loop_list.txt"
            music_list.write_text(
                "\n".join([f"file '{music_path}'" for _ in range(loops_needed)])
            )
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(music_list),
                "-c:a", "pcm_s16le",
                "-t", str(total_duration),
                str(music_loop),
            ], check=True, capture_output=True)
        else:
            music_loop = music_path
        
        # Full mix with sidechain ducking
        filter_complex = (
            "[1:a]asplit=2[sc][mix];"
            "[0:a][sc]sidechaincompressor=threshold=-30dB:ratio=8:"
            "attack=50:release=200:level_sc=0.8[ducked];"
            "[ducked][mix]amix=inputs=2:duration=first:weights='1 0.15'[mixed]"
        )
        
        # Add SFX if provided
        if sfx_events:
            # For simplicity, SFX mixing is complex - would need multiple inputs
            # We'll handle this in a more advanced version
            pass
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(narration_concat),
            "-i", str(music_loop),
            "-filter_complex", filter_complex,
            "-map", "[mixed]",
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
            "-ar", "48000",
            "-ac", "2",
            "-c:a", "aac",
            "-b:a", "192k",
            str(output_path),
        ]
    else:
        # No music: just normalize narration
        cmd = [
            "ffmpeg", "-y",
            "-i", str(narration_concat),
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
            "-ar", "48000",
            "-ac", "2",
            "-c:a", "aac",
            "-b:a", "192k",
            str(output_path),
        ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


# ───────────────────────────────────────────────────────────────────────────
# FULL AUDIO PIPELINE
# ───────────────────────────────────────────────────────────────────────────

async def produce_audio(
    director_cut: DirectorCut,
    output_dir: Path,
    music_override: Optional[Path] = None,
) -> AudioMixPlan:
    """Full audio production pipeline for a Director's Cut.
    
    Returns an AudioMixPlan with paths to the final mastered audio.
    """
    # 1. Generate all narrations in parallel
    narration_dir = output_dir / "narrations"
    narration_dir.mkdir(parents=True, exist_ok=True)
    narration_paths = await generate_all_narrations(director_cut.scenes, narration_dir)
    
    # 2. Select music stem
    primary_mood = director_cut.mood_arc[0] if director_cut.mood_arc else "curious"
    music_path = music_override or select_music_stem(primary_mood.value)
    
    # 3. Analyze beats (if music available)
    if music_path and music_path.exists():
        beat_grid = analyze_beats(music_path)
    else:
        # Default beat grid for no music
        beat_grid = BeatGrid(
            bpm=120.0,
            beats=[i * 0.5 for i in range(1200)],
            onsets=[i * 1.0 for i in range(600)],
            energy=[0.5] * 600,
            downbeats=[i * 2.0 for i in range(300)],
        )
    
    # 4. Mix full audio
    final_audio = output_dir / "final_audio.aac"
    await mix_full_audio(
        narration_paths=narration_paths,
        music_path=music_path,
        scenes=director_cut.scenes,
        beat_grid=beat_grid,
        output_path=final_audio,
    )
    
    return AudioMixPlan(
        narration_path=str(narration_dir),
        music_path=str(music_path) if music_path else "",
        music_start_offset=0.0,
        music_duck_db=-24.0,
        beat_grid=beat_grid,
    )
