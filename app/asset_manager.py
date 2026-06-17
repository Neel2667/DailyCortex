"""Asset Orchestrator — Pexels stock footage, user assets, and cache management."""
import hashlib
import asyncio
import httpx
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote_plus

from app.config import get_settings

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
    cached = list(cache_dir.glob("*.mp4"))
    if cached:
        return [str(p) for p in cached]

    query = " ".join(keywords)
    headers = {"Authorization": settings.pexels_api_key}
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "landscape",
        "size": "large",  # 1920x1080 preferred
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
                out_path.write_bytes(stream.content)
                downloaded.append(str(out_path))
        except Exception as e:
            print(f"[AssetManager] Failed to download {url}: {e}")
            continue

    return downloaded


def get_user_assets(category: str) -> List[str]:
    """List available user assets from the mounted library."""
    asset_dir = settings.asset_dir / category
    if not asset_dir.exists():
        return []
    extensions = {"images": ["*.jpg", "*.jpeg", "*.png", "*.webp"], "clips": ["*.mp4", "*.mov"], "svgs": ["*.svg"]}
    paths = []
    for ext in extensions.get(category, []):
        paths.extend(asset_dir.glob(ext))
    return [str(p) for p in paths]
