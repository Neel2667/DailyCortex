#!/bin/bash
set -e

echo "🧠 CORTEX RENDER — Boot Sequence"

# Ensure data dirs exist (HF Spaces persistent storage)
mkdir -p /data/cache /data/renders /data/logs /data/music /data/sfx

# Pre-warm Playwright chromium cache
echo "▸ Verifying Chromium for Animation Factory..."
python3 -c "import subprocess; subprocess.run(['npx', 'playwright', 'chromium', '--version'], cwd='/app/mograph_factory', check=True)" 2>/dev/null || true

# Start FastAPI
echo "▸ Launching orchestrator on port 7860"
exec "$@"
