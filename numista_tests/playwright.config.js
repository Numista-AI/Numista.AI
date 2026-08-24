const { defineConfig, devices } = require('@playwright/test');
// Phase 3C: load .env for TEST_USER_EMAIL / TEST_USER_PASSWORD
require('dotenv').config();

module.exports = defineConfig({
  testDir: './tests',
  timeout: 60000,
  retries: 1,
  workers: 1,
  // NOTE: Always use `npx playwright test` (no --reporter flag) so this
  // config is used and JSON is always written to reports/test-results.json
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'reports/test-results.json' }],
    ['list']
  ],
  use: {
    baseURL: 'https://numista.ai',
    headless: true,
    viewport: { width: 1920, height: 1080 },
    screenshot: 'on',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    // Phase 3C: auth setup runs first, saves fixtures/auth-state.json
    {
      name: 'setup',
      testMatch: /auth\.setup\.js/,
    },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Reuse saved auth session for all tests
        storageState: 'fixtures/auth-state.json',
        launchOptions: {
          args: [
            '--use-gl=angle',
            '--use-angle=swiftshader',
            '--ignore-gpu-blocklist',
          ],
        },
      },
      dependencies: ['setup'],
    },
  ],
  outputDir: 'screenshots',
});
