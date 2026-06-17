#!/bin/bash
# Validate a captured video clip

FILE="$1"

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Usage: validate-output.sh <video.mov>"
  exit 1
fi

echo "📊 Validating: $FILE"
echo "─────────────────────"

ffprobe -v quiet -print_format json -show_streams "$FILE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for stream in data.get('streams', []):
    if stream.get('codec_type') == 'video':
        print(f'Codec:       {stream.get(\"codec_name\", \"unknown\")}')
        print(f'Pixel fmt:   {stream.get(\"pix_fmt\", \"unknown\")}')
        print(f'Resolution:  {stream.get(\"width\")}x{stream.get(\"height\")}')
        print(f'Duration:    {stream.get(\"duration\", \"unknown\")}s')
        print(f'Bitrate:     {stream.get(\"bit_rate\", \"unknown\")}')
        
        pix_fmt = stream.get('pix_fmt', '')
        if 'a' in pix_fmt or 'A' in pix_fmt:
            print('Alpha:       ✅ YES')
        else:
            print('Alpha:       ❌ NO')
"

echo ""
echo "Frame analysis (first 3 frames):"
ffmpeg -i "$FILE" -vf "select='between(n,0,2)',showinfo" -f null - 2>&1 | grep -E 'Stream|Duration|Stream #|Stream mapping|Output'
