const { defineConfig, devices } = require('@playwright/test');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../numista_tests/.env') });

// Read qa_base_url from SUITE_MANIFEST.json — when set, Layer 2 CRUD is activated
const _manifest = JSON.parse(fs.readFileSync(path.join(__dirname, 'SUITE_MANIFEST.json'), 'utf8'));
const _qaBaseUrl = _manifest.qa_base_url;
const _baseURL = (_qaBaseUrl && _qaBaseUrl !== 'REPLACE_WITH_QA_DEPLOYMENT_URL')
    ? _qaBaseUrl
    : (process.env.PLAYWRIGHT_BASE_URL || 'https://numista.ai');


module.exports = defineConfig({
  // testDir is NOT set here — each run specifies the layer directory explicitly
  timeout: 120000,
  retries: 1,
  workers: 1,
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'reports/qc-results.json' }],
    ['list'],
  ],
  use: {
    baseURL: _baseURL,
    headless: true,
    viewport: { width: 1920, height: 1080 },  // Desktop ONLY — no mobile viewports
    screenshot: 'on',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    // auth.setup.js runs once, saves fixtures/auth-token.json
    {
      name: 'setup',
      testMatch: /auth\.setup\.js/,
    },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
        launchOptions: {
          args: [
            '--window-size=1920,1080',
            '--use-gl=angle',
            '--use-angle=swiftshader',
            '--ignore-gpu-blocklist',
          ],
        },
      },
      // Layer 2 functional tests use pre-loaded auth token from setup
      dependencies: ['setup'],
    },
  ],
  outputDir: 'screenshots',
  // staging/ directory is explicitly excluded — generated specs are never auto-run
  testIgnore: ['**/staging/**', '**/_archived/**'],
});
