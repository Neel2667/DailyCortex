# Cinematic Brain Hacks Video Engine — Docker Image
# Multi-stage: heavy build deps first, then runtime layer

FROM ubuntu:22.04 AS base

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/local/share/playwright-browsers

# ——— System deps ———
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python + build tools
    python3.11 python3-pip python3.11-venv \
    build-essential cmake pkg-config \
    # FFmpeg (full build for filter_complex + xfade + gltransition support)
    ffmpeg libavcodec-dev libavformat-dev libavutil-dev libswscale-dev \
    # Node.js 20 (LTS)
    curl ca-certificates gnupg \
    # Playwright / Chromium deps
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 \
    libcairo2 libasound2 libcurl4 libxshmfence1 \
    # Fonts
    fonts-liberation fonts-noto-color-emoji fonts-noto-cjk \
    # Misc
    git wget unzip \
    && rm -rf /var/lib/apt/lists/*

# Node 20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && npm install -g npm@10

# ——— Python layer ———
WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# ——— Node / Mograph Factory layer ———
WORKDIR /app/mograph_factory

COPY mograph_factory/package.json mograph_factory/package-lock.json* ./
RUN npm ci --include=dev

# Install Playwright Chromium + deps
RUN npx playwright install chromium && \
    npx playwright install-deps chromium

# Build mograph factory (React app for headless capture)
COPY mograph_factory/ .
RUN npm run build

# ——— App layer ———
WORKDIR /app

COPY app/ ./app/
COPY assets/ ./assets/

# Persistent HF Space data dir
RUN mkdir -p /data/cache /data/renders /data/logs

# Expose FastAPI port
EXPOSE 7860

# Entrypoint script handles any runtime init
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
