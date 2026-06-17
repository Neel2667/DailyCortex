#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FACTORY_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${FACTORY_DIR}/test-output"

echo "🧪 CORTEX RENDER — Animation Factory Capture Test"
echo "═══════════════════════════════════════════════════════"
echo ""

cd "$FACTORY_DIR"

# ─── Step 1: Install dependencies ───
echo "▸ Installing npm dependencies..."
npm install --silent

# ─── Step 2: Build React app ───
echo "▸ Building React app for production..."
if [ -d dist ]; then
  rm -rf dist
fi
npm run build

# Verify build output
if [ ! -f "dist/index.html" ]; then
  echo "❌ Build failed: dist/index.html not found"
  exit 1
fi
echo "   ✅ Build complete: $(ls -1 dist/assets/ | wc -l) asset files"

# ─── Step 3: Run capture pipeline ───
echo ""
echo "▸ Running capture pipeline..."
mkdir -p "$OUTPUT_DIR"

node scripts/render-clip.js test-props.json "$OUTPUT_DIR/test-question-bomb.mov"

# ─── Step 4: Validate output ───
echo ""
echo "▸ Validating output..."

if [ ! -f "$OUTPUT_DIR/test-question-bomb.mov" ]; then
  echo "❌ Output file not found"
  exit 1
fi

FILE_SIZE=$(du -h "$OUTPUT_DIR/test-question-bomb.mov" | cut -f1)
echo "   ✅ Output file: $FILE_SIZE"

# Check with ffprobe
if command -v ffprobe &> /dev/null; then
  echo ""
  echo "📊 Output Stream Info:"
  ffprobe -v quiet -print_format json -show_streams "$OUTPUT_DIR/test-question-bomb.mov" | grep -E '(codec_name|pix_fmt|width|height|duration)'
  
  PIX_FMT=$(ffprobe -v error -select_streams v:0 -show_entries stream=pix_fmt -of csv=p=0 "$OUTPUT_DIR/test-question-bomb.mov")
  echo ""
  echo "   Pixel format: $PIX_FMT"
  
  if echo "$PIX_FMT" | grep -q "a"; then
    echo "   ✅ Alpha channel detected"
  else
    echo "   ⚠️  Alpha channel NOT detected (may still be present)"
  fi
else
  echo "   ⚠️  ffprobe not available for validation"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "🎉 Test complete. Output: $OUTPUT_DIR/test-question-bomb.mov"
echo ""
