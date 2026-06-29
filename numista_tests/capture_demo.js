const { chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: [
      '--use-gl=angle',
      '--use-angle=swiftshader',
      '--ignore-gpu-blocklist',
    ]
  });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 720 });

  page.on('console', msg => console.log(`[BROWSER CONSOLE] ${msg.type().toUpperCase()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`[BROWSER EXCEPTION] ${err.message}`));

  console.log("Navigating to http://localhost:8080 ...");
  await page.goto('http://localhost:8080');
  
  console.log("Waiting for flt-glass-pane to be attached...");
  await page.waitForSelector('flt-glass-pane', { state: 'attached', timeout: 30000 });
  
  console.log("Waiting 15 seconds for CanvasKit assets to download and render...");
  await page.waitForTimeout(15000);

  const screenshotPath = path.join(__dirname, 'demo_new.png');
  console.log(`Saving screenshot to ${screenshotPath} ...`);
  await page.screenshot({ path: screenshotPath });

  await browser.close();
  console.log("Done!");
})();
