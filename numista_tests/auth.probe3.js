// auth.probe3.js — extract Firebase config from the Flutter web app
// The app's main.dart.js / flutter_bootstrap.js embeds the Firebase config.
// We need projectId, apiKey, etc. to call initializeApp() ourselves.
const { chromium } = require('@playwright/test');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--ignore-gpu-blocklist'],
  });
  const page = await browser.newPage();

  // Intercept all JS responses to find Firebase config
  const configs = [];
  page.on('response', async (resp) => {
    if (resp.url().includes('.js') && resp.status() === 200) {
      try {
        const body = await resp.text();
        // Look for Firebase config object patterns
        const match = body.match(/apiKey:\s*["']([^"']+)["'][\s\S]{0,500}?projectId:\s*["']([^"']+)["'][\s\S]{0,500}?appId:\s*["']([^"']+)["']/);
        if (match) {
          configs.push({ url: resp.url(), apiKey: match[1], projectId: match[2], appId: match[3] });
        }
        // Also look for messagingSenderId and authDomain
        const match2 = body.match(/authDomain:\s*["']([^"']+)["']/);
        if (match2 && configs.length > 0) {
          configs[configs.length - 1].authDomain = match2[1];
        }
      } catch (_) {}
    }
  });

  await page.goto('https://numista.ai');
  await page.waitForTimeout(6000);

  // Also try to extract from page globals
  const pageConfig = await page.evaluate(() => {
    // Check if Firebase core has the app registered
    const apps = window.firebase_core?.getApps?.() ?? [];
    if (apps.length > 0) {
      const app = apps[0];
      return { fromApps: true, options: app.options };
    }
    return { fromApps: false };
  });

  console.log('Page-level Firebase apps:', JSON.stringify(pageConfig, null, 2));
  console.log('JS-intercepted configs:', JSON.stringify(configs, null, 2));

  const result = { pageConfig, configs };
  fs.writeFileSync('auth.probe3.json', JSON.stringify(result, null, 2));
  console.log('Saved to auth.probe3.json');

  await browser.close();
})();
