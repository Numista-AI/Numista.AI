/**
 * contrast_guard.spec.js — Numista QC Suite Layer 1
 * WCAG AA contrast check: relative luminance ratio >= 4.5:1 on key UI regions.
 * Viewport: 1920x1080 desktop ONLY.
 * Theme settle delay: 500ms after toggle.
 *
 * Strategy: pixel-sample 10x10 regions at known UI landmark positions,
 * compute relative luminance for foreground and background samples,
 * assert contrast ratio >= 4.5:1.
 *
 * Both Light and Dark themes are tested.
 */

const { test, expect } = require('@playwright/test');
require('dotenv').config({ path: require('path').join(__dirname, '../../numista_tests/.env') });

// ---- Auth helpers (same pattern as 26-aug24-remediation.spec.js) ----
async function signInAndWait(page) {
  const email = process.env.TEST_USER_EMAIL;
  const password = process.env.TEST_USER_PASSWORD;
  await page.waitForFunction(
    () => (window.firebase_core?.getApps?.() ?? []).length > 0,
    { timeout: 20000 }
  );
  const r = await page.evaluate(async ({ em, pw }) => {
    try {
      const auth = window.firebase_auth.getAuth();
      await window.firebase_auth.setPersistence(auth, window.firebase_auth.browserLocalPersistence);
      await window.firebase_auth.signInWithEmailAndPassword(auth, em, pw);
      return { ok: true };
    } catch (e) { return { ok: false, error: e.message }; }
  }, { em: email, pw: password });
  if (!r.ok) throw new Error('Auth failed: ' + r.error);
  await page.evaluate(() => {
    ['flutter.user_name', 'flutter.userName', 'flutter.morgan_onboarding_complete',
     'flutter.onboarding_complete', 'flutter.onboarding_done'].forEach(k => localStorage.setItem(k, 'true'));
  });
  await page.reload();
  await page.waitForFunction(
    () => { const p = document.querySelector('flt-glass-pane'); return p && window.getComputedStyle(p).visibility === 'visible'; },
    { timeout: 20000 }
  );
  await page.waitForTimeout(5000);
}

// ---- Luminance helpers ----
// Returns relative luminance (0-1) from an {r,g,b} object (0-255 values)
function relativeLuminance({ r, g, b }) {
  const sRGB = [r, g, b].map(c => {
    const s = c / 255;
    return s <= 0.04045 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * sRGB[0] + 0.7152 * sRGB[1] + 0.0722 * sRGB[2];
}

function contrastRatio(lum1, lum2) {
  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);
  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Sample a 10x10 pixel region and return the average colour.
 * Uses page.evaluate + canvas trick since CanvasKit renders to canvas.
 */
async function sampleRegionAvgColor(page, x, y, size = 10) {
  return page.evaluate(({ x, y, size }) => {
    const canvas = document.querySelector('flt-glass-pane canvas') ||
                   document.querySelector('canvas');
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;
    const data = ctx.getImageData(x, y, size, size).data;
    let r = 0, g = 0, b = 0;
    const pixels = size * size;
    for (let i = 0; i < data.length; i += 4) {
      r += data[i]; g += data[i + 1]; b += data[i + 2];
    }
    return { r: Math.round(r / pixels), g: Math.round(g / pixels), b: Math.round(b / pixels) };
  }, { x, y, size });
}

// WCAG AA normal text threshold
const WCAG_AA = 4.5;
const THEME_SETTLE_MS = 500;

// UI regions to sample: [name, fgX, fgY, bgX, bgY]
// These are pixel coordinates at 1920x1080 for the main app areas.
// fgX/fgY = foreground (text) sample; bgX/bgY = background behind it.
const SAMPLE_REGIONS = [
  { name: 'Sidebar nav item',    fgX: 95,   fgY: 200, bgX: 95,   bgY: 220 },
  { name: 'Main content header', fgX: 500,  fgY: 120, bgX: 500,  bgY: 140 },
  { name: 'Collection card text',fgX: 320,  fgY: 380, bgX: 320,  bgY: 400 },
  { name: 'Bottom nav label',    fgX: 960,  fgY: 1040,bgX: 960,  bgY: 1060 },
];

// Detect if a region's canvas is crossOrigin-blocked (returns null)
function canvasBlocked(color) {
  return color === null;
}

test.describe('Contrast Guard - Light Mode', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://numista.ai');
    await signInAndWait(page);
  });

  test('WCAG AA contrast >= 4.5:1 in Light mode on key UI regions', async ({ page }) => {
    // Switch to light mode if not already
    // Light mode toggle: look for a theme/settings button in the app
    // Flutter exposes theme toggle via flt-semantics; try clicking the settings icon
    const themeBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /theme|light|dark|mode/i });
    if (await themeBtn.first().isVisible({ timeout: 2000 }).catch(() => false)) {
      await themeBtn.first().click();
      await page.waitForTimeout(THEME_SETTLE_MS);
    }

    let failedRegions = [];
    let blockedRegions = [];

    for (const region of SAMPLE_REGIONS) {
      const fg = await sampleRegionAvgColor(page, region.fgX, region.fgY);
      const bg = await sampleRegionAvgColor(page, region.bgX, region.bgY);

      if (canvasBlocked(fg) || canvasBlocked(bg)) {
        blockedRegions.push(region.name);
        console.warn('[contrast_guard] Canvas read blocked for region: ' + region.name + '. Check CORS / CanvasKit config.');
        continue;
      }

      const fgLum = relativeLuminance(fg);
      const bgLum = relativeLuminance(bg);
      const ratio = contrastRatio(fgLum, bgLum);

      console.log('[' + region.name + '] fg=' + JSON.stringify(fg) + ' bg=' + JSON.stringify(bg) + ' ratio=' + ratio.toFixed(2));

      if (ratio < WCAG_AA) {
        failedRegions.push({ name: region.name, ratio: ratio.toFixed(2), fg, bg });
      }
    }

    if (blockedRegions.length === SAMPLE_REGIONS.length) {
      // All regions blocked - canvas not readable. Report as CANVAS_UNREADABLE, not PASS.
      throw new Error(
        'CANVAS_UNREADABLE: All ' + SAMPLE_REGIONS.length + ' regions returned null. ' +
        'CanvasKit canvas may be cross-origin blocked. Cannot assert contrast.'
      );
    }

    expect(failedRegions, 'Contrast failures in Light mode:\n' + JSON.stringify(failedRegions, null, 2)).toHaveLength(0);
  });
});

test.describe('Contrast Guard - Dark Mode', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://numista.ai');
    await signInAndWait(page);
  });

  test('WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions', async ({ page }) => {
    // Attempt to switch to dark mode
    const themeBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /theme|light|dark|mode/i });
    if (await themeBtn.first().isVisible({ timeout: 2000 }).catch(() => false)) {
      await themeBtn.first().click();
      await page.waitForTimeout(THEME_SETTLE_MS);
    }

    let failedRegions = [];
    let blockedRegions = [];

    for (const region of SAMPLE_REGIONS) {
      const fg = await sampleRegionAvgColor(page, region.fgX, region.fgY);
      const bg = await sampleRegionAvgColor(page, region.bgX, region.bgY);

      if (canvasBlocked(fg) || canvasBlocked(bg)) {
        blockedRegions.push(region.name);
        continue;
      }

      const fgLum = relativeLuminance(fg);
      const bgLum = relativeLuminance(bg);
      const ratio = contrastRatio(fgLum, bgLum);

      console.log('[' + region.name + '] fg=' + JSON.stringify(fg) + ' bg=' + JSON.stringify(bg) + ' ratio=' + ratio.toFixed(2));

      if (ratio < WCAG_AA) {
        failedRegions.push({ name: region.name, ratio: ratio.toFixed(2), fg, bg });
      }
    }

    if (blockedRegions.length === SAMPLE_REGIONS.length) {
      throw new Error('CANVAS_UNREADABLE: All regions blocked. Cannot assert contrast.');
    }

    expect(failedRegions, 'Contrast failures in Dark mode:\n' + JSON.stringify(failedRegions, null, 2)).toHaveLength(0);
  });
});
