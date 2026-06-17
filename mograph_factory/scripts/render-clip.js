#!/usr/bin/env node
/**
 * CORTEX RENDER — Animation Factory Capture Script
 * Uses Playwright + Chrome DevTools Protocol to capture React/Framer Motion
 * components as transparent video clips.
 *
 * Usage:
 *   node render-clip.js --props scene_props.json --output /data/cache/mograph/s01_hero.mov
 */
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30;
const WIDTH = 1920;
const HEIGHT = 1080;

async function parseArgs() {
  const args = process.argv.slice(2);
  const flags = {};
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, '');
    flags[key] = args[i + 1];
  }
  if (!flags.props || !flags.output) {
    console.error('Usage: node render-clip.js --props <json_path> --output <mov_path> [--duration 5000]');
    process.exit(1);
  }
  const props = JSON.parse(fs.readFileSync(flags.props, 'utf8'));
  const durationMs = parseInt(flags.duration || props.durationMs || 5000, 10);
  return { props, outputPath: flags.output, durationMs };
}

async function startDevServer() {
  // Serve the built mograph_factory app
  const { createServer } = require('vite');
  const server = await createServer({
    root: path.join(__dirname, '..'),
    server: { port: 3456, host: '127.0.0.1', middlewareMode: false },
  });
  await server.listen();
  const url = `http://127.0.0.1:3456`;
  console.log(`▸ Dev server running at ${url}`);
  return { server, url };
}

async function captureToVideo(page, url, renderProps, outputPath, durationMs) {
  const totalFrames = Math.ceil((durationMs / 1000) * FPS);

  // Navigate and inject props
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.evaluate((rp) => {
    window.CORTEX_RENDER = rp;
  }, renderProps);
  // Wait for React to mount and settle initial frame
  await page.waitForTimeout(300);

  // Start CDP screencast
  const client = await page.context().newCDPSession(page);
  await client.send('Animation.setPlaybackRate', { playbackRate: 0 });

  // Prepare FFmpeg stdin pipe for raw RGBA -> ProRes with alpha
  const ffmpeg = spawn('ffmpeg', [
    '-y',
    '-f', 'rawvideo',
    '-pix_fmt', 'rgba',
    '-s', `${WIDTH}x${HEIGHT}`,
    '-r', String(FPS),
    '-i', '-',
    '-c:v', 'prores_ks',
    '-profile:v', '4444',
    '-pix_fmt', 'yuva444p10le',
    '-vendor', 'ap10',
    '-qscale:v', '9',
    '-an',
    outputPath,
  ], { stdio: ['pipe', 'inherit', 'inherit'] });

  let frameCount = 0;
  let startTime = Date.now();

  // Use CDP Page.screencastFrame is not ideal for high-freq capture.
  // Instead, we use Chrome Headless's experimental --dump-dom or
  // we use page.screenshot in a tight loop. For Phase 0, we use the
  // reliable screenshot loop piped to FFmpeg.

  const screenshotOpts = {
    type: 'png',
    omitBackground: true,
  };

  // Advance animation frame-by-frame via requestAnimationFrame + setTimeout hack
  for (let i = 0; i < totalFrames; i++) {
    const elapsed = (i / FPS) * 1000;
    // Advance any JS timers/animations by this amount via CDP
    await client.send('Runtime.evaluate', {
      expression: `
        if (window.__cortex_advance) {
          window.__cortex_advance(${elapsed});
        } else {
          // fallback: tick RAF manually
          const start = performance.now();
          while (performance.now() - start < ${1000 / FPS}) {}
        }
      `,
    });

    const buf = await page.screenshot(screenshotOpts);
    ffmpeg.stdin.write(buf);
    frameCount++;

    if (frameCount % 30 === 0) {
      const pct = ((frameCount / totalFrames) * 100).toFixed(1);
      const elapsedSec = ((Date.now() - startTime) / 1000).toFixed(1);
      console.log(`  Frame ${frameCount}/${totalFrames} (${pct}%) — ${elapsedSec}s elapsed`);
    }
  }

  ffmpeg.stdin.end();
  await new Promise((resolve, reject) => {
    ffmpeg.on('close', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`FFmpeg exited ${code}`));
    });
  });

  const totalSec = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log(`▸ Rendered ${frameCount} frames in ${totalSec}s → ${outputPath}`);
}

async function main() {
  const { props, outputPath, durationMs } = await parseArgs();
  console.log(`\n🎬 CORTEX RENDER — Animation Factory`);
  console.log(`   Component: ${props.componentId}`);
  console.log(`   Duration:  ${durationMs}ms`);
  console.log(`   Output:    ${outputPath}`);

  const { server, url } = await startDevServer();

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

  try {
    await captureToVideo(page, url, props, outputPath, durationMs);
  } finally {
    await browser.close();
    await server.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
