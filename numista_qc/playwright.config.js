const { defineConfig, devices } = require('@playwright/test');
require('dotenv').config({ path: require('path').join(__dirname, '../numista_tests/.env') });

module.exports = defineConfig({
  // testDir is NOT set here — each run specifies the layer directory explicitly
  timeout: 90000,
  retries: 1,
  workers: 1,
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'reports/qc-results.json' }],
    ['list'],
  ],
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'https://numista.ai',
    headless: true,
    viewport: { width: 1920, height: 1080 },  // Desktop ONLY — no mobile viewports
    screenshot: 'on',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: [
            '--use-gl=angle',
            '--use-angle=swiftshader',
            '--ignore-gpu-blocklist',
          ],
        },
      },
    },
  ],
  outputDir: 'screenshots',
  // staging/ directory is explicitly excluded — generated specs are never auto-run
  testIgnore: ['**/staging/**', '**/_archived/**'],
});
