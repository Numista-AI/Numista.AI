const { chromium } = require('@playwright/test');

async function run() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  const page = await context.newPage();
  await page.goto('https://numista.ai');
  await page.waitForTimeout(5000);

  const scrollInfo = await page.evaluate(() => {
    return {
      scrollHeight: document.documentElement.scrollHeight,
      clientHeight: document.documentElement.clientHeight,
      bodyScrollHeight: document.body.scrollHeight,
      windowInnerHeight: window.innerHeight,
      scrollY: window.scrollY
    };
  });

  console.log('Scroll Info:', scrollInfo);
  await browser.close();
}

run();
