/**
 * Screenshot utility using Puppeteer.
 * Takes a full-page screenshot of a localhost URL.
 *
 * Usage: node screenshot.mjs http://localhost:3000 [label]
 * Saves to: ./temporary screenshots/screenshot-N.png (or screenshot-N-label.png)
 */
import { existsSync, mkdirSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCREENSHOT_DIR = join(__dirname, 'temporary screenshots');

async function takeScreenshot() {
  const url = process.argv[2] || 'http://localhost:3000';
  const label = process.argv[3];

  // Ensure screenshot directory exists
  if (!existsSync(SCREENSHOT_DIR)) {
    mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }

  // Determine next screenshot number
  const existing = readdirSync(SCREENSHOT_DIR).filter(f => f.endsWith('.png'));
  const maxNum = existing.reduce((max, f) => {
    const m = f.match(/screenshot-(\d+)/);
    return m ? Math.max(max, parseInt(m[1])) : max;
  }, 0);
  const nextNum = maxNum + 1;

  const suffix = label ? `-${label}` : '';
  const filename = `screenshot-${nextNum}${suffix}.png`;
  const filepath = join(SCREENSHOT_DIR, filename);

  // Launch puppeteer
  const puppeteer = await import('puppeteer');
  const puppeteerLib = puppeteer.default || puppeteer;

  let browser;
  try {
    // Try puppeteer-test first, then default cache location
    const cacheDir = process.env.PUPPETEER_CACHE_DIR ||
      'C:/Users/nateh/AppData/Local/Temp/puppeteer-test/';

    // Try system Chrome first, fall back to puppeteer cache
    const chromePaths = [
      'C:/Program Files/Google/Chrome/Application/chrome.exe',
      'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
      '/usr/bin/google-chrome',
      '/usr/bin/chromium-browser',
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    ];

    let executablePath;
    const fs2 = await import('fs');
    for (const p of chromePaths) {
      if (fs2.existsSync(p)) {
        executablePath = p;
        break;
      }
    }

    browser = await puppeteerLib.launch({
      headless: true,
      executablePath: executablePath || undefined,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-blink-features=AutomationControlled',
        '--disable-gpu',
        '--disable-software-rasterizer',
      ],
      defaultViewport: {
        width: 1280,
        height: 1400,
        deviceScaleFactor: 1,
      },
    });

    const page = await browser.newPage();

    // Set user agent to avoid bot detection
    await page.setUserAgent(
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    );

    // Navigate with network idle
    await page.goto(url, { waitUntil: 'networkidle0', timeout: 30000 });

    // Take full-page screenshot
    await page.screenshot({
      path: filepath,
      fullPage: true,
      type: 'png',
    });

    console.log(`📸 Screenshot saved: ${filepath}`);
    console.log(`   Size: ${(await import('fs')).statSync(filepath).size} bytes`);
  } catch (err) {
    console.error('❌ Screenshot failed:', err.message);
    process.exit(1);
  } finally {
    if (browser) await browser.close();
  }
}

takeScreenshot();
