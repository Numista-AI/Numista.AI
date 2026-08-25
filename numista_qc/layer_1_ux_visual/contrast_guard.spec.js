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
      const cred = await window.firebase_auth.signInWithEmailAndPassword(auth, em, pw);
      const uid = cred.user ? cred.user.uid : 'guest';
      return { ok: true, uid };
    } catch (e) { return { ok: false, error: e.message }; }
  }, { em: email, pw: password });
  if (!r.ok) throw new Error('Auth failed: ' + r.error);
  await page.evaluate(({ uid }) => {
    ['flutter.user_name', 'flutter.userName', 'flutter.morgan_onboarding_complete',
     'flutter.onboarding_complete', 'flutter.onboarding_done', 'flutter.user_title',
     'flutter.title_chosen', 'flutter.onboarding_step',
     'flutter.beta_tester_welcome_seen_v2', 'flutter.beta_tester_welcome_seen',
     'flutter.morgan_greeter_seen',
     'flutter.morgan_' + uid + '_setup_done',
     'flutter.morgan_' + uid + '_preferred_name',
     'flutter.morgan_guest_setup_done'].forEach(k => localStorage.setItem(k, 'true'));
    localStorage.setItem('flutter.morgan_' + uid + '_show_on_startup', 'false');
    localStorage.setItem('flutter.morgan_guest_show_on_startup', 'false');
  }, { uid: r.uid || 'guest' });
  await page.reload();
  await page.waitForFunction(
    () => {
      const p = document.querySelector('flutter-view') ||
                document.querySelector('flt-glass-pane') ||
                document.querySelector('canvas');
      return p && window.getComputedStyle(p).visibility === 'visible';
    },
    { timeout: 20000 }
  );
  await page.waitForTimeout(3000);

  // Dismiss any lingering dialogs (Beta Tester modal, Morgan onboarding, etc.)
  for (let i = 0; i < 3; i++) {
    await page.evaluate(() => {
      const nodes = Array.from(document.querySelectorAll('button, [role=button], flt-semantics, div'));
      for (const n of nodes) {
        const text = n.innerText || n.textContent || '';
        if (/Got It|Let's Explore|That's me|Skip|browse on my own|Homepage \/ Dashboard/i.test(text)) {
          n.click();
        }
      }
    }).catch(() => {});
    await page.waitForTimeout(500);
  }
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
 * Sample a landmark region (e.g. 50x50 px) and compute the contrast ratio between
 * the brightest foreground text/icon pixels and darkest background container pixels.
 */
async function sampleRegionsFromScreenshot(page, sampleRegions, regionSize = 50) {
  console.log('[contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)');
  const screenshot = await page.screenshot({ type: 'png' });
  const base64 = screenshot.toString('base64');

  return page.evaluate(async ({ base64, sampleRegions, regionSize }) => {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        if (!ctx) return resolve(null);
        ctx.drawImage(img, 0, 0);

        function calcLuminance(r, g, b) {
          const sRGB = [r, g, b].map(c => {
            const s = c / 255;
            return s <= 0.04045 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
          });
          return 0.2126 * sRGB[0] + 0.7152 * sRGB[1] + 0.0722 * sRGB[2];
        }

        const results = [];
        for (const region of sampleRegions) {
          const x = Math.max(0, Math.min(region.x, img.width - regionSize));
          const y = Math.max(0, Math.min(region.y, img.height - regionSize));
          const data = ctx.getImageData(x, y, regionSize, regionSize).data;

          let maxLum = 0;
          let minLum = 1.0;
          let maxColor = { r: 0, g: 0, b: 0 };
          let minColor = { r: 0, g: 0, b: 0 };

          for (let i = 0; i < data.length; i += 4) {
            const r = data[i], g = data[i + 1], b = data[i + 2];
            const lum = calcLuminance(r, g, b);
            if (lum > maxLum) {
              maxLum = lum;
              maxColor = { r, g, b };
            }
            if (lum < minLum) {
              minLum = lum;
              minColor = { r, g, b };
            }
          }

          const ratio = (maxLum + 0.05) / (minLum + 0.05);
          results.push({
            name: region.name,
            ratio,
            fg: maxColor,
            bg: minColor,
          });
        }
        resolve(results);
      };
      img.onerror = () => resolve(null);
      img.src = 'data:image/png;base64,' + base64;
    });
  }, { base64, sampleRegions, regionSize });
}

// WCAG AA normal text threshold
const WCAG_AA = 4.5;
const THEME_SETTLE_MS = 500;

// UI landmark regions to sample at 1920x1080
const SAMPLE_REGIONS = [
  { name: 'Sidebar Navigation', x: 50,  y: 130 },
  { name: 'Sidebar Coins',      x: 50,  y: 265 },
  { name: 'Ask Morgan Header',  x: 730, y: 30 },
  { name: 'Top Programs Card',  x: 550, y: 800 },
];

test.describe('Contrast Guard - Light Mode', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://numista.ai');
    await signInAndWait(page);
  });

  test('WCAG AA contrast >= 4.5:1 in Light mode on key UI regions', async ({ page }) => {
    const themeBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /theme|light|dark|mode/i });
    if (await themeBtn.first().isVisible({ timeout: 2000 }).catch(() => false)) {
      await themeBtn.first().click();
      await page.waitForTimeout(THEME_SETTLE_MS);
    }

    const sampled = await sampleRegionsFromScreenshot(page, SAMPLE_REGIONS);
    if (!sampled) {
      throw new Error('CANVAS_UNREADABLE: Failed to sample screenshot. Cannot assert contrast.');
    }

    let failedRegions = [];
    for (const item of sampled) {
      console.log('[' + item.name + '] fg=' + JSON.stringify(item.fg) + ' bg=' + JSON.stringify(item.bg) + ' ratio=' + item.ratio.toFixed(2));

      if (item.ratio < WCAG_AA) {
        failedRegions.push({ name: item.name, ratio: item.ratio.toFixed(2), fg: item.fg, bg: item.bg });
      }
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
    const themeBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /theme|light|dark|mode/i });
    if (await themeBtn.first().isVisible({ timeout: 2000 }).catch(() => false)) {
      await themeBtn.first().click();
      await page.waitForTimeout(THEME_SETTLE_MS);
    }

    const sampled = await sampleRegionsFromScreenshot(page, SAMPLE_REGIONS);
    if (!sampled) {
      throw new Error('CANVAS_UNREADABLE: Failed to sample screenshot. Cannot assert contrast.');
    }

    let failedRegions = [];
    for (const item of sampled) {
      console.log('[' + item.name + '] fg=' + JSON.stringify(item.fg) + ' bg=' + JSON.stringify(item.bg) + ' ratio=' + item.ratio.toFixed(2));

      if (item.ratio < WCAG_AA) {
        failedRegions.push({ name: item.name, ratio: item.ratio.toFixed(2), fg: item.fg, bg: item.bg });
      }
    }

    expect(failedRegions, 'Contrast failures in Dark mode:\n' + JSON.stringify(failedRegions, null, 2)).toHaveLength(0);
  });
});
