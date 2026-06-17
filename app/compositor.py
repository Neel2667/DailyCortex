"""The Generative Compositor — FFmpeg-based cinematic scene assembly."""
import subprocess
import random
import json
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

from app.config import get_settings
from app.models import Scene, DirectorCut, BeatGrid, TransitionType

settings = get_settings()

# Transition pool with weighted probabilities per mood transition
TRANSITION_POOL = list(TransitionType)

# Track used transitions to enforce no-repeat-within-4 rule
_used_transitions: List[TransitionType] = []
_used_layouts: List[str] = []
_used_text_zones: List[str] = []


def pick_transition(from_mood: str, to_mood: str, intensity: float) -> TransitionType:
    """Stochastic transition selection with no-repeat guard."""
    global _used_transitions
    candidates = [t for t in TRANSITION_POOL if t not in _used_transitions[-4:]]
    if not candidates:
        candidates = TRANSITION_POOL
    chosen = random.choice(candidates)
    _used_transitions.append(chosen)
    return chosen


def pick_layout(forbidden: List[str]) -> str:
    """Pick a layout family not used in the last 3 scenes."""
    from app.models import LayoutFamily
    candidates = [l.value for l in LayoutFamily if l.value not in forbidden[-3:]]
    if not candidates:
        candidates = [l.value for l in LayoutFamily]
    chosen = random.choice(candidates)
    _used_layouts.append(chosen)
    return chosen


def build_scene_filtergraph(
    scene: Scene,
    stock_paths: List[str],
    mograph_path: Optional[str],
    text_overlay_path: Optional[str],
    beat_grid: BeatGrid,
    output_path: Path,
) -> List[str]:
    """Build an FFmpeg filter_complex for a single scene."""
    # This is a Phase 0 stub. The real implementation will build a full
    # filtergraph with zoompan, overlay, color grade, and text burn.
    # For now, we concatenate the first stock clip with a color grade.

    if not stock_paths:
        # Fallback: generate a colorbar with text
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c={scene.color_grade}:s=1920x1080:d={scene.duration_sec}",
            "-vf", f"drawtext=text='{scene.scene_id}':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
            str(output_path),
        ]
        return cmd

    input_flags = []
    for i, p in enumerate(stock_paths[:2]):
        input_flags += ["-i", p]

    filters = []
    # Ken Burns zoompan on first clip
    filters.append(
        f"[0:v]zoompan=z='min(zoom+0.001,1.15)':d={int(scene.duration_sec * 30)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',"
        f"eq=gamma=1.1:saturation=1.2:contrast=1.05[v0]"
    )

    if len(stock_paths) > 1:
        # Crossfade two clips
        xfade_dur = 1.0
        v1_dur = scene.duration_sec - xfade_dur
        filters.append(f"[1:v]trim=0:{v1_dur},setpts=PTS-STARTPTS[v1]")
        filters.append(f"[v0][v1]xfade=transition=fade:duration={xfade_dur}:offset={scene.duration_sec - xfade_dur}[vstock]")
    else:
        filters.append("[v0]copy[vstock]")

    # Overlay mograph if available
    if mograph_path and Path(mograph_path).exists():
        input_flags += ["-i", mograph_path]
        mograph_idx = len(stock_paths[:2])
        filters.append(f"[vstock][{mograph_idx}:v]overlay=format=auto[v1]")
    else:
        filters.append("[vstock]copy[v1]")

    # Color grade via curves / eq (simple mood mapping)
    grade_map = {
        "cool_blue": "curves=r='0/0 0.5/0.4 1/1':g='0/0 0.5/0.5 1/1':b='0/0 0.5/0.7 1/1'",
        "warm_gold": "curves=r='0/0 0.5/0.6 1/1':g='0/0 0.5/0.5 1/1':b='0/0 0.5/0.3 1/1'",
        "neural_green": "curves=r='0/0 0.5/0.3 1/1':g='0/0 0.5/0.7 1/1':b='0/0 0.5/0.4 1/1'",
        "high_contrast_mono": "hue=s=0,curves=r='0/0 0.5/0.5 1/1':g='0/0 0.5/0.5 1/1':b='0/0 0.5/0.5 1/1'",
        "clinical_cyan": "eq=saturation=1.3:contrast=1.1,curves=r='0/0 0.5/0.2 1/1':g='0/0 0.5/0.6 1/1':b='0/0 0.5/0.8 1/1'",
    }
    grade_filter = grade_map.get(scene.color_grade, "copy")
    filters.append(f"[v1]{grade_filter}[vgraded]")

    # Text overlay
    if text_overlay_path and Path(text_overlay_path).exists():
        input_flags += ["-i", text_overlay_path]
        txt_idx = len(stock_paths[:2]) + (1 if mograph_path else 0)
        filters.append(f"[vgraded][{txt_idx}:v]overlay=format=auto[vfinal]")
    else:
        # Burn text via drawtext if no overlay image
        txt = scene.text_overlay.text if scene.text_overlay else scene.scene_id
        safe_txt = txt.replace(":", "\\:").replace("'", "\\'")
        filters.append(f"[vgraded]drawtext=text='{safe_txt}':fontsize=48:fontcolor=white:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:x=(w-text_w)/2:y=(h-text_h)/2[vfinal]")

    filters.append("[vfinal]format=yuv420p[output]")
    filter_str = ";".join(filters)

    cmd = [
        "ffmpeg", "-y",
        *input_flags,
        "-filter_complex", filter_str,
        "-map", "[output]",
        "-t", str(scene.duration_sec),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]
    return cmd


async def render_scene(
    scene: Scene,
    stock_paths: List[str],
    mograph_path: Optional[str],
    text_overlay_path: Optional[str],
    beat_grid: BeatGrid,
    output_path: Path,
) -> Path:
    """Render a single scene to a temporary MP4 segment."""
    cmd = build_scene_filtergraph(scene, stock_paths, mograph_path, text_overlay_path, beat_grid, output_path)
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg scene render failed: {stderr.decode()[:500]}")
    return output_path


async def concatenate_scenes(scene_paths: List[Path], output_path: Path) -> Path:
    """Concatenate scene segments with the concat demuxer."""
    concat_list = settings.cache_dir / "concat_list.txt"
    concat_list.write_text("\n".join(f"file '{p}'" for p in scene_paths))

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(output_path),
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg concat failed: {stderr.decode()[:500]}")
    return output_path


async def master_final(
    video_path: Path,
    audio_path: Path,
    output_path: Path,
) -> Path:
    """Final mastering: normalize audio, mux, apply loudnorm."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg master failed: {stderr.decode()[:500]}")
    return output_path
