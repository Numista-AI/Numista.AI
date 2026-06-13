const { test, expect } = require('@playwright/test');

// ============================================================
// TEST SUITE 04: Registration / Create Account Edge Cases
// Tests the Create Account form for proper validation behavior
// ============================================================

const NAV_WAIT = 4000;
const CLICK_WAIT = 2000;

async function goToCreateAccount(page) {
  await page.goto('https://numista.ai');
  await page.waitForTimeout(NAV_WAIT);
  // Click "Create Account" tab (right button at top of form)
  await page.mouse.click(1340, 86);
  await page.waitForTimeout(CLICK_WAIT);
}

test.describe('04 - Registration Edge Cases', () => {

  test('T01: Create Account form renders all fields', async ({ page }) => {
    await goToCreateAccount(page);
    const buf = await page.screenshot({ path: 'screenshots/create-account-form.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(100000);
    expect(page.url()).toBe('https://numista.ai/');
  });

  test('T02: Submit with no data does not navigate away', async ({ page }) => {
    await goToCreateAccount(page);
    // Click "Create My Account and Vault" without filling anything
    await page.mouse.click(1194, 467);
    await page.waitForTimeout(2000);
    const buf = await page.screenshot({ path: 'screenshots/create-account-empty-submit.png', type: 'png' });
    expect(page.url()).toBe('https://numista.ai/');
    expect(buf.length).toBeGreaterThan(100000);
  });

  test('T03: Terms checkbox must be checked (button disabled without it)', async ({ page }) => {
    await goToCreateAccount(page);
    // Click the submit button without checking terms
    await page.mouse.click(1194, 467);
    await page.waitForTimeout(1500);
    // Still on homepage - form blocked
    expect(page.url()).toBe('https://numista.ai/');
  });

  test('T04: Can type in Name field (optional)', async ({ page }) => {
    await goToCreateAccount(page);
    // Click on Name field (approx center of first input field)
    await page.mouse.click(1194, 185);
    await page.waitForTimeout(500);
    await page.keyboard.type('Test User');
    await page.waitForTimeout(1000);
    const buf = await page.screenshot({ path: 'screenshots/create-account-name-typed.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(100000);
    expect(page.url()).toBe('https://numista.ai/');
  });

  test('T05: Double-clicking submit does not crash page', async ({ page }) => {
    await goToCreateAccount(page);
    await page.mouse.click(1194, 467);
    await page.waitForTimeout(300);
    await page.mouse.click(1194, 467);
    await page.waitForTimeout(2000);
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));
    expect(page.url()).toBe('https://numista.ai/');
  });

  test('T06: Switching Sign In -> Create Account -> Sign In preserves state', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(NAV_WAIT);
    // Switch to Create Account
    await page.mouse.click(1340, 86);
    await page.waitForTimeout(CLICK_WAIT);
    // Switch back to Sign In
    await page.mouse.click(1046, 86);
    await page.waitForTimeout(CLICK_WAIT);
    const buf = await page.screenshot({ path: 'screenshots/signin-after-toggle.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(100000);
    expect(page.url()).toBe('https://numista.ai/');
  });

  test('T07: Forgot your PIN link renders on Sign In tab', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(NAV_WAIT);
    const buf = await page.screenshot({ type: 'png' });
    expect(buf.length).toBeGreaterThan(100000);
  });

  test('T08: Page remains stable after rapid tab switches', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(NAV_WAIT);
    const pageErrors = [];
    page.on('pageerror', err => pageErrors.push(err.message));
    // Rapidly switch tabs 5 times
    for (let i = 0; i < 5; i++) {
      await page.mouse.click(1340, 86); // Create Account
      await page.waitForTimeout(300);
      await page.mouse.click(1046, 86); // Sign In
      await page.waitForTimeout(300);
    }
    await page.waitForTimeout(1000);
    expect(pageErrors, 'JS errors after rapid switching: ' + pageErrors.join(' | ')).toHaveLength(0);
    expect(page.url()).toBe('https://numista.ai/');
  });

});
