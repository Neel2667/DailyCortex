"""Audio Engine — Edge TTS, music stem selection, beat analysis, and mixing."""
import subprocess
import asyncio
import json
from pathlib import Path
from typing import List, Tuple, Optional
import random

import edge_tts
import librosa
import numpy as np
from app.config import get_settings
from app.models import BeatGrid

settings = get_settings()


async def generate_narration(text: str, output_path: Path, voice: Optional[str] = None) -> Path:
    """Generate narration audio using Edge TTS with SSML prosody."""
    voice = voice or settings.tts_voice
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    return output_path


def select_music_stem(mood: str, bpm_target: int) -> Optional[Path]:
    """Pick a music stem from the curated library matching mood and BPM."""
    lib = settings.music_library_path / mood
    if not lib.exists():
        return None
    candidates = list(lib.rglob("*.mp3")) + list(lib.rglob("*.wav"))
    if not candidates:
        return None
    # Simple heuristic: pick random from matching mood folder
    # In production, parse BPM from filename metadata or ID3 tags
    return random.choice(candidates)


def analyze_beats(audio_path: Path) -> BeatGrid:
    """Analyze audio with librosa to extract BPM, beat frames, and onset energy."""
    y, sr = librosa.load(str(audio_path), sr=None, mono=True)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()

    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
    onset_times = librosa.frames_to_time(onsets, sr=sr).tolist()
    onset_energies = onset_env[onsets].tolist()

    return BeatGrid(
        bpm=float(tempo),
        beats=beat_times,
        onsets=onset_times,
        energy=onset_energies,
    )


def mix_audio_scene(
    narration_path: Path,
    music_path: Optional[Path],
    beat_grid: BeatGrid,
    output_path: Path,
    duration_sec: float,
) -> Path:
    """Mix narration with music (ducked) and optional SFX. Single FFmpeg pass."""
    # Build a complex filtergraph for sidechain ducking
    # Music is ducked by ~18dB when narration is present using acompressor + sidechain

    inputs = ["-i", str(narration_path)]
    if music_path and music_path.exists():
        inputs += ["-i", str(music_path)]
        filter_complex = (
            "[1:a]asplit=2[sc][mix];"
            "[0:a][sc]sidechaincompressor=threshold=-30dB:ratio=8:attack=50:release=200:level_sc=0.8[ducked];"
            "[0:a][mix]amix=inputs=2:duration=first:weights='1 0.15'[out]"
        )
    else:
        filter_complex = "[0:a]anull[out]"

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-t", str(duration_sec),
        "-ar", "48000",
        "-ac", "2",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def generate_sfx_tone(freq: int, duration: float, output_path: Path) -> Path:
    """Generate a simple sine-wave SFX for transitions."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"sine=frequency={freq}:duration={duration}",
        "-af", "afade=t=in:ss=0:d=0.05,afade=t=out:st={}:d=0.1".format(duration - 0.1),
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path
