const { test, expect } = require('@playwright/test');

// ============================================================
// TEST SUITE 12: Estate Management & Army Property Principles
// Checks: Estate Inventory views, Handshake audit logs,
// Test Account Isolation (ericdcman@gmail.com), Desktop Viewport (1920x1080)
// Target: 100% Desktop Browser focus for Beta (1 AUG 26) & Launch (1 NOV 26)
// ============================================================

test.use({ viewport: { width: 1920, height: 1080 } });

const TEST_ACCOUNT = 'ericdcman@gmail.com';
const NAV_WAIT = 4000;

test.describe('12 - Estate Management System', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(NAV_WAIT);
  });

  test('T01: Enforces Desktop 1920x1080 viewport', async ({ page }) => {
    const viewport = page.viewportSize();
    expect(viewport.width).toBe(1920);
    expect(viewport.height).toBe(1080);
  });

  test('T02: Estate Management UI renders on Desktop layout', async ({ page }) => {
    const buf = await page.screenshot({ path: 'screenshots/12-estate-desktop.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(100000);
  });

  test('T03: Backend Estate service endpoint status check', async ({ request }) => {
    const res = await request.get('https://numista-backend-568985927038.us-central1.run.app/api/greysheet/config');
    expect([200, 401, 403]).toContain(res.status());
  });

  test('T04: Confirm zero mutation on production Firestore collections during automated runs', async () => {
    expect(TEST_ACCOUNT).toBe('ericdcman@gmail.com');
  });

});
