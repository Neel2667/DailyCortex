#!/usr/bin/env node
/**
 * CORTEX RENDER — Animation Factory Capture Pipeline
 * 
 * Captures React/Framer Motion components as transparent video clips.
 * Uses deterministic time control for frame-accurate animation capture.
 * 
 * Usage:
 *   node scripts/render-clip.js <props.json> <output.mov>
 * 
 * Architecture:
 *   1. Build React app (if dist/ doesn't exist)
 *   2. Start static HTTP server on dist/
 *   3. Launch Playwright headless Chromium
 *   4. Inject deterministic time controller (overrides RAF, Date.now, performance.now)
 *   5. Navigate to page, inject component props via window.CORTEX_RENDER
 *   6. Frame capture loop: advance time → screenshot → save PNG
 *   7. FFmpeg compile PNG sequence → ProRes 4444 with alpha (yuva444p10le)
 *   8. Verify alpha channel with ffprobe
 *   9. Cleanup temp files
 */

const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const http = require('http');

const FPS = 30;
const FRAME_MS = 1000 / FPS;
const WIDTH = 1920;
const HEIGHT = 1080;

// MIME types for static server
const MIME_TYPES = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.mjs': 'application/javascript',
  '.css': 'text/css',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.otf': 'font/otf',
  '.json': 'application/json',
  '.ico': 'image/x-icon',
};

/**
 * Start a simple static HTTP server for the built app.
 */
function startServer(distDir) {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      const url = req.url === '/' ? '/index.html' : decodeURIComponent(req.url.split('?')[0]);
      const filePath = path.join(distDir, url);

      // Security: prevent directory traversal
      if (!filePath.startsWith(distDir)) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
      }

      let targetPath = filePath;
      if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
        const indexPath = path.join(filePath, 'index.html');
        if (fs.existsSync(indexPath)) {
          targetPath = indexPath;
        } else {
          res.writeHead(404);
          res.end('Not found');
          return;
        }
      }

      const ext = path.extname(targetPath).toLowerCase();
      res.writeHead(200, {
        'Content-Type': MIME_TYPES[ext] || 'application/octet-stream',
        'Cache-Control': 'no-cache',
      });
      res.end(fs.readFileSync(targetPath));
    });

    server.listen(3456, () => {
      console.log('▸ Static server running on http://localhost:3456');
      resolve(server);
    });
  });
}

/**
 * Time controller script injected into the browser before any page scripts run.
 * Makes all animations deterministic and frame-accurate.
 */
const TIME_CONTROLLER_SCRIPT = () => {
  const TimeController = {
    _time: 0,
    _rafs: new Map(),
    _rafId: 0,
    _timeouts: new Map(),
    _timeoutId: 0,
    _intervals: new Map(),
    _intervalId: 0,

    advance(ms) {
      this._time += ms;

      // Execute all pending requestAnimationFrame callbacks
      const rafCallbacks = Array.from(this._rafs.values());
      this._rafs.clear();
      rafCallbacks.forEach((cb) => {
        try { cb(this._time); } catch (e) { /* ignore */ }
      });

      // Execute expired setTimeout callbacks
      const now = this._time;
      const expiredTimeouts = [];
      this._timeouts.forEach((timeout, id) => {
        if (timeout.time <= now) {
          expiredTimeouts.push({ id, cb: timeout.cb });
        }
      });
      expiredTimeouts.forEach(({ id, cb }) => {
        this._timeouts.delete(id);
        try { cb(); } catch (e) { /* ignore */ }
      });
    },

    getTime() { return this._time; }
  };

  // Override global timing functions
  window.Date.now = () => TimeController.getTime();
  window.performance.now = () => TimeController.getTime();

  window.requestAnimationFrame = (cb) => {
    TimeController._rafId++;
    TimeController._rafs.set(TimeController._rafId, cb);
    return TimeController._rafId;
  };
  window.cancelAnimationFrame = (id) => {
    TimeController._rafs.delete(id);
  };

  const origSetTimeout = window.setTimeout;
  window.setTimeout = (cb, ms) => {
    if (typeof cb !== 'function') return -1;
    TimeController._timeoutId++;
    TimeController._timeouts.set(TimeController._timeoutId, {
      cb,
      time: TimeController.getTime() + (ms || 0)
    });
    return TimeController._timeoutId;
  };
  window.clearTimeout = (id) => {
    TimeController._timeouts.delete(id);
  };

  window.setInterval = (cb, ms) => {
    if (typeof cb !== 'function' || !ms) return -1;
    const id = TimeController._intervalId++;
    const tick = () => {
      try { cb(); } catch (e) { /* ignore */ }
      TimeController._timeouts.set(TimeController._intervalId++, {
        cb: tick,
        time: TimeController.getTime() + ms
      });
    };
    TimeController._timeouts.set(TimeController._intervalId++, {
      cb: tick,
      time: TimeController.getTime() + ms
    });
    return id;
  };
  window.clearInterval = (id) => {
    // Simple cleanup: intervals use timeouts internally
  };

  // Expose advance function for capture loop
  window.__cortex_advance = (ms) => TimeController.advance(ms);
  window.__cortex_get_time = () => TimeController.getTime();
};

async function main() {
  const propsFile = process.argv[2];
  const outputFile = process.argv[3];

  if (!propsFile || !outputFile) {
    console.error('❌ Usage: node scripts/render-clip.js <props.json> <output.mov>');
    console.error('   Example: node scripts/render-clip.js test-props.json /tmp/output.mov');
    process.exit(1);
  }

  if (!fs.existsSync(propsFile)) {
    console.error(`❌ Props file not found: ${propsFile}`);
    process.exit(1);
  }

  const props = JSON.parse(fs.readFileSync(propsFile, 'utf8'));
  const durationMs = props.durationMs || 5000;
  const frameCount = Math.ceil((durationMs / 1000) * FPS);
  const factoryDir = path.join(__dirname, '..');
  const distDir = path.join(factoryDir, 'dist');

  console.log('\n🎬 CORTEX RENDER — Animation Factory Capture');
  console.log('─────────────────────────────────────────────');
  console.log(`   Component:   ${props.componentId}`);
  console.log(`   Duration:    ${durationMs}ms`);
  console.log(`   Resolution:  ${WIDTH}x${HEIGHT}`);
  console.log(`   FPS:         ${FPS}`);
  console.log(`   Frames:      ${frameCount}`);
  console.log(`   Output:      ${outputFile}`);
  console.log('');

  // ─── Step 1: Build React app ───
  if (!fs.existsSync(path.join(distDir, 'index.html'))) {
    console.log('▸ Building React app...');
    const { execSync } = require('child_process');
    try {
      execSync('npm run build', { cwd: factoryDir, stdio: 'inherit' });
    } catch (e) {
      console.error('❌ Build failed:', e.message);
      process.exit(1);
    }
  } else {
    console.log('▸ Using existing build in dist/');
  }

  // ─── Step 2: Start static server ───
  const server = await startServer(distDir);

  // ─── Step 3: Launch Playwright ───
  console.log('▸ Launching headless Chromium...');
  const browser = await chromium.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-gpu',
      '--disable-dev-shm-usage',
      '--disable-background-timer-throttling',
      '--disable-backgrounding-occluded-windows',
      '--disable-renderer-backgrounding',
      '--force-color-profile=srgb',
      `--window-size=${WIDTH},${HEIGHT}`,
    ],
  });

  const context = await browser.newContext({
    viewport: { width: WIDTH, height: HEIGHT },
    deviceScaleFactor: 1,
  });

  const page = await context.newPage();

  // Inject time controller BEFORE any scripts run
  await page.addInitScript(TIME_CONTROLLER_SCRIPT);

  // ─── Step 4: Navigate and inject props ───
  await page.goto('http://localhost:3456');
  await page.evaluate((p) => {
    window.CORTEX_RENDER = p;
  }, props);

  // Wait for React to mount and initial animations to settle
  await page.waitForTimeout(500);

  // Verify the component is rendered
  const hasContent = await page.evaluate(() => {
    return document.body.innerText.length > 0 || document.querySelectorAll('svg, canvas, div').length > 5;
  });
  if (!hasContent) {
    console.warn('⚠️  Page appears empty — component may not have rendered correctly');
  }

  // ─── Step 5: Create temp directory for PNGs ───
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'cortex-render-'));
  console.log(`▸ Capturing ${frameCount} frames to ${tempDir}`);

  // ─── Step 6: Frame capture loop ───
  const captureStart = Date.now();
  for (let i = 0; i < frameCount; i++) {
    // Advance deterministic time by 1 frame
    await page.evaluate(() => window.__cortex_advance(1000 / 30));

    // Give browser compositor a tiny bit of real time to rasterize
    // This is the critical step: RAF callbacks fire synchronously above,
    // but the browser needs a moment to paint the updated DOM to the surface
    await page.waitForTimeout(10);

    // Capture screenshot with transparent background
    const buf = await page.screenshot({
      type: 'png',
      omitBackground: true,
    });

    fs.writeFileSync(path.join(tempDir, `frame_${String(i).padStart(4, '0')}.png`), buf);

    if (i % 30 === 0 || i === frameCount - 1) {
      const pct = ((i / frameCount) * 100).toFixed(1);
      const elapsed = ((Date.now() - captureStart) / 1000).toFixed(1);
      console.log(`  Frame ${String(i).padStart(4, '0')}/${frameCount} (${pct}%) — ${elapsed}s elapsed`);
    }
  }

  const captureTime = Date.now() - captureStart;
  const speedRatio = (durationMs / 1000) / (captureTime / 1000);
  console.log(`  ✅ Capture complete: ${captureTime}ms (${speedRatio.toFixed(1)}x real-time)`);

  // ─── Step 7: FFmpeg compile PNG sequence → ProRes 4444 ───
  console.log('▸ Encoding with FFmpeg (ProRes 4444 with alpha)...');
  const ffmpegStart = Date.now();

  await new Promise((resolve, reject) => {
    const ffmpeg = spawn('ffmpeg', [
      '-y',
      '-framerate', String(FPS),
      '-i', path.join(tempDir, 'frame_%04d.png'),
      '-c:v', 'prores_ks',
      '-profile:v', '4444',
      '-pix_fmt', 'yuva444p10le',
      '-vendor', 'ap10',
      '-qscale:v', '9',
      '-an',
      outputFile,
    ], { stdio: 'inherit' });

    ffmpeg.on('close', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`FFmpeg exited with code ${code}`));
    });
  });

  const ffmpegTime = Date.now() - ffmpegStart;
  console.log(`  ✅ Encoding complete: ${ffmpegTime}ms`);

  // ─── Step 8: Verify alpha channel ───
  const ffprobeResult = await new Promise((resolve) => {
    let output = '';
    const ffprobe = spawn('ffprobe', [
      '-v', 'error',
      '-select_streams', 'v:0',
      '-show_entries', 'stream=pix_fmt,width,height,codec_name',
      '-of', 'json',
      outputFile,
    ]);
    ffprobe.stdout.on('data', (d) => output += d.toString());
    ffprobe.on('close', () => resolve(output));
  });

  try {
    const info = JSON.parse(ffprobeResult);
    const stream = info.streams?.[0];
    if (stream) {
      console.log('');
      console.log('📊 Output Metadata');
      console.log('─────────────────────────────────────────────');
      console.log(`   Codec:       ${stream.codec_name}`);
      console.log(`   Resolution:  ${stream.width}x${stream.height}`);
      console.log(`   Pixel fmt:   ${stream.pix_fmt}`);
      if (stream.pix_fmt && stream.pix_fmt.includes('a')) {
        console.log('   ✅ Alpha channel: YES');
      } else {
        console.log('   ⚠️  Alpha channel: NOT DETECTED');
      }
    }
  } catch (e) {
    console.log('   ⚠️  Could not parse ffprobe output');
  }

  // Verify file size
  const stats = fs.statSync(outputFile);
  console.log(`   File size:   ${(stats.size / (1024 * 1024)).toFixed(1)} MB`);
  console.log('');
  console.log(`🎉 Output: ${outputFile}`);

  // ─── Step 9: Cleanup ───
  console.log('▸ Cleaning up temp files...');
  fs.rmSync(tempDir, { recursive: true, force: true });
  console.log('   ✅ Done');

  // ─── Shutdown ───
  await browser.close();
  server.close(() => {
    console.log('');
    console.log('─────────────────────────────────────────────');
    console.log('Pipeline complete.');
    process.exit(0);
  });
}

main().catch((err) => {
  console.error('\n❌ Pipeline error:', err.message);
  console.error(err.stack);
  process.exit(1);
});
