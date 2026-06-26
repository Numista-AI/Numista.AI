const { chromium } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

async function run() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  const page = await context.newPage();

  const logs = [];
  const addLog = (type, message) => {
    const logStr = `[${new Date().toISOString()}] [${type.toUpperCase()}] ${message}`;
    logs.push(logStr);
    console.log(logStr);
  };

  page.on('console', msg => {
    addLog(msg.type(), msg.text());
  });

  page.on('pageerror', err => {
    addLog('pageerror', `${err.name}: ${err.message}\nStack: ${err.stack}`);
  });

  page.on('requestfailed', request => {
    addLog('requestfailed', `${request.method()} ${request.url()} - ${request.failure()?.errorText || 'Unknown Error'}`);
  });

  page.on('response', response => {
    const status = response.status();
    if (status >= 400) {
      addLog('response_error', `${response.request().method()} ${response.url()} -> Status ${status}`);
    }
  });

  try {
    addLog('info', 'Navigating to https://numista.ai...');
    await page.goto('https://numista.ai', { waitUntil: 'load', timeout: 30000 });
    await page.waitForTimeout(5000);

    addLog('info', 'Clicking "Browse Demo" at (874, 673)...');
    await page.mouse.click(874, 673);
    await page.waitForTimeout(5000);

    addLog('info', 'Clicking "Microscope Scanner" at (80, 354)...');
    await page.mouse.click(80, 354);
    await page.waitForTimeout(6000);

    const artifactDir = 'C:\\Users\\ericd\\.gemini\\antigravity\\brain\\408674cb-50e1-4a19-b1b5-e36e157db358';
    const screenshotPath = path.join(artifactDir, 'microscope_scanner_result.png');
    await page.screenshot({ path: screenshotPath });
    addLog('info', `Screenshot saved to: ${screenshotPath}`);

    // Save logs to file
    const logsPath = path.join(artifactDir, 'diagnostics_console_logs.txt');
    fs.writeFileSync(logsPath, logs.join('\n'), 'utf8');
    addLog('info', `Logs written to: ${logsPath}`);

  } catch (error) {
    addLog('error', `Execution failed: ${error.message}\n${error.stack}`);
  } finally {
    await browser.close();
  }
}

run();
