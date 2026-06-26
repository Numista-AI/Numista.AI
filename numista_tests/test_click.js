const { chromium } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

async function run() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  const page = await context.newPage();
  
  await page.goto('https://numista.ai');
  await page.waitForTimeout(5000);

  console.log('Clicking Browse Demo at (874, 673)...');
  await page.mouse.click(874, 673);
  await page.waitForTimeout(5000);

  const artifactDir = 'C:\\Users\\ericd\\.gemini\\antigravity\\brain\\408674cb-50e1-4a19-b1b5-e36e157db358';
  const screenshotPath = path.join(artifactDir, 'after_demo_click.png');
  await page.screenshot({ path: screenshotPath });
  console.log(`Screenshot saved to: ${screenshotPath}`);
  console.log('Current URL:', page.url());

  await browser.close();
}

run();
