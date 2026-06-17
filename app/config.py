"""Configuration and settings for the Cinematic Brain Hacks Video Engine."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Keys
    groq_api_key: str = ""
    pexels_api_key: str = ""

    # Paths
    workspace: Path = Path("/app")
    data_dir: Path = Path("/data")
    cache_dir: Path = Path("/data/cache")
    render_dir: Path = Path("/data/renders")
    asset_dir: Path = Path("/app/assets")
    mograph_factory_dir: Path = Path("/app/mograph_factory")

    # Video defaults
    target_resolution: tuple[int, int] = (1920, 1080)
    target_fps: int = 30
    target_bitrate: str = "8M"

    # Audio
    tts_voice: str = "en-US-GuyNeural"  # or en-GB-SoniaNeural
    target_lufs: float = -14.0

    # Performance
    max_parallel_scenes: int = 2
    max_parallel_mograph_renders: int = 4
    target_render_multiplier: float = 2.0  # 2x = 10min video in <20min

    # Music library
    music_library_path: Path = Path("/data/music")
    sfx_library_path: Path = Path("/data/sfx")

    # Hugging Face Space
    hf_space: bool = True

@lru_cache
def get_settings() -> Settings:
    return Settings()
