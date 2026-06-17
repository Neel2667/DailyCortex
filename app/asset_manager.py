"""Asset Orchestrator — Pexels stock footage, user assets, and cache management."""
import asyncio
import hashlib
import aiofiles
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import httpx
from urllib.parse import quote_plus

from app.config import get_settings
from app.models import Scene, DirectorCut

settings = get_settings()
PEXELS_API_URL = "https://api.pexels.com/videos/search"


def _keyword_hash(keywords: List[str]) -> str:
    """Deterministic hash for cache keys."""
    return hashlib.sha256(" ".join(sorted(keywords)).encode()).hexdigest()[:16]


async def fetch_pexels_clips(
    keywords: List[str],
    per_page: int = 3,
    min_duration: int = 5,
    max_duration: int = 15,
) -> List[str]:
    """Fetch short Pexels clips matching keywords. Returns list of local file paths."""
    if not settings.pexels_api_key:
        return []

    cache_key = _keyword_hash(keywords)
    cache_dir = settings.cache_dir / "pexels" / cache_key
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Check cache first
    cached = sorted(cache_dir.glob("*.mp4"))
    if cached:
        return [str(p) for p in cached]

    query = " ".join(keywords)
    headers = {"Authorization": settings.pexels_api_key}
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "landscape",
        "size": "large",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(PEXELS_API_URL, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()

    clips = data.get("videos", [])
    downloaded: List[str] = []

    for i, clip in enumerate(clips):
        # Prefer HD files
        video_files = clip.get("video_files", [])
        hd_file = next(
            (f for f in video_files if f.get("width") == 1920 and f.get("height") == 1080),
            next(
                (f for f in video_files if f.get("quality") in ("hd", "sd")),
                None,
            ),
        )
        if not hd_file:
            continue

        url = hd_file["link"]
        out_path = cache_dir / f"{i}_{clip['id']}.mp4"

        try:
            async with httpx.AsyncClient(timeout=60) as dl_client:
                stream = await dl_client.get(url, follow_redirects=True)
                stream.raise_for_status()
                async with aiofiles.open(out_path, "wb") as f:
                    await f.write(stream.content)
                downloaded.append(str(out_path))
        except Exception as e:
            print(f"[AssetManager] Failed to download {url}: {e}")
            continue

    return downloaded


async def fetch_pexels_for_scene(
    scene: Scene,
    per_scene: int = 3,
) -> List[str]:
    """Fetch Pexels clips for a single scene's visual keywords."""
    if not scene.visual_keywords:
        return []
    return await fetch_pexels_clips(
        keywords=scene.visual_keywords,
        per_page=per_scene,
    )


async def fetch_all_scene_assets(
    director_cut: DirectorCut,
    per_scene: int = 3,
    max_parallel: int = 4,
) -> Dict[str, Dict[str, Any]]:
    """Fetch all Pexels clips for all scenes in parallel.
    
    Returns: {scene_id: {"stock_clips": [...], ...}}
    """
    sem = asyncio.Semaphore(max_parallel)
    
    async def fetch_one(scene: Scene) -> Tuple[str, List[str]]:
        async with sem:
            clips = await fetch_pexels_for_scene(scene, per_scene)
            return scene.scene_id, clips
    
    tasks = [fetch_one(scene) for scene in director_cut.scenes]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    assets: Dict[str, Dict[str, Any]] = {}
    for result in results:
        if isinstance(result, Exception):
            # Log but don't fail - some scenes might have no footage
            print(f"[AssetManager] Scene fetch failed: {result}")
            continue
        scene_id, clips = result
        assets[scene_id] = {
            "stock_clips": clips,
            "mograph_clips": [],  # Populated by Animation Factory
            "text_overlays": [],   # Populated by Text Renderer
        }
    
    return assets


def get_user_assets(category: str) -> List[str]:
    """List available user assets from the mounted library."""
    asset_dir = settings.asset_dir / category
    if not asset_dir.exists():
        return []
    
    extensions = {
        "images": ["*.jpg", "*.jpeg", "*.png", "*.webp"],
        "clips": ["*.mp4", "*.mov"],
        "svgs": ["*.svg"],
    }
    
    paths = []
    for ext in extensions.get(category, []):
        paths.extend(asset_dir.glob(ext))
    return sorted(str(p) for p in paths)


def build_user_asset_index() -> Dict[str, List[str]]:
    """Build an index of all user assets by category."""
    return {
        "images": get_user_assets("images"),
        "clips": get_user_assets("clips"),
        "svgs": get_user_assets("svgs"),
    }


def select_user_assets_for_scene(
    scene: Scene,
    asset_index: Dict[str, List[str]],
    max_per_scene: int = 2,
) -> List[str]:
    """Heuristically select user assets that match a scene's visual keywords."""
    selected = []
    keywords = set(k.lower() for k in scene.visual_keywords)
    
    for category in ["images", "clips", "svgs"]:
        for asset_path in asset_index.get(category, []):
            # Simple heuristic: filename contains keyword
            filename = Path(asset_path).stem.lower()
            if any(kw in filename or filename in kw for kw in keywords):
                selected.append(asset_path)
                if len(selected) >= max_per_scene:
                    break
        if len(selected) >= max_per_scene:
            break
    
    return selected
