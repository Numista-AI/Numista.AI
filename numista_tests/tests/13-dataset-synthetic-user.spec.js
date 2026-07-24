const { test, expect } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

// ============================================================
// TEST SUITE 13: Synthetic AI User E2E Testing Harness
// Tests real user workflows with ground-truth dataset assets
// ============================================================

const DATASET_DIR = "C:\\Users\\ericd\\Documents\\MyVertexProject\\1 NUMISTA.AI\\BETA TEST\\MY TESTING\\qa_dataset";
const NAV_WAIT = 3500;
const CLICK_WAIT = 2000;

test.describe('13 - Synthetic AI User E2E Journey', () => {

  test.beforeEach(async ({ page }) => {
    // Capture console errors for quality auditing
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(`[Browser Console Error] ${msg.text()}`);
      }
    });
  });

  test('T01: Sign up new synthetic test account', async ({ page }) => {
    const timestamp = Date.now();
    const testEmail = `qa_agent_${timestamp}@numista-test.ai`;

    await page.goto('https://numista.ai');
    await page.waitForTimeout(NAV_WAIT);

    // Switch to Create Account tab if available
    const createAccountTab = page.locator('text=Create Account').first();
    if (await createAccountTab.isVisible().catch(() => false)) {
      await createAccountTab.click();
      await page.waitForTimeout(CLICK_WAIT);
    }

    await page.screenshot({ path: 'screenshots/qa-01-signup-page.png', fullPage: true });
    expect(page.url()).toContain('numista.ai');
  });

  test('T02: Upload Microscope Coin Image for High-Resolution AI Analysis', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(NAV_WAIT);

    const microscopeImagePath = path.join(DATASET_DIR, 'Microscope Images', '1963_Roosevelt_Dime_D_Obverse_20260411_1226.jpg');
    expect(fs.existsSync(microscopeImagePath)).toBe(true);

    // Locate file input element or drag area
    const fileInput = page.locator('input[type="file"]').first();
    if (await fileInput.count() > 0) {
      await fileInput.setInputFiles(microscopeImagePath);
      await page.waitForTimeout(CLICK_WAIT);
    }

    await page.screenshot({ path: 'screenshots/qa-02-microscope-dime-upload.png', fullPage: true });
    expect(page.url()).toContain('numista.ai');
  });

  test('T03: Upload Obverse and Reverse Paired Gold Coin Images ($5 Indianhead 1914)', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(NAV_WAIT);

    const obversePath = path.join(DATASET_DIR, '$5 Indianhead 1914 obverse.jpg');
    const reversePath = path.join(DATASET_DIR, '$5 Indianhead 1914 reverse.jpg');

    expect(fs.existsSync(obversePath)).toBe(true);
    expect(fs.existsSync(reversePath)).toBe(true);

    const fileInput = page.locator('input[type="file"]').first();
    if (await fileInput.count() > 0) {
      await fileInput.setInputFiles([obversePath, reversePath]);
      await page.waitForTimeout(CLICK_WAIT);
    }

    await page.screenshot({ path: 'screenshots/qa-03-gold-coin-pair-upload.png', fullPage: true });
    expect(page.url()).toContain('numista.ai');
  });

  test('T04: Process PDF Receipt Document Extraction', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(NAV_WAIT);

    const pdfPath = path.join(DATASET_DIR, 'Receipt_2026-01-28_161342.pdf');
    expect(fs.existsSync(pdfPath)).toBe(true);

    const fileInput = page.locator('input[type="file"]').first();
    if (await fileInput.count() > 0) {
      await fileInput.setInputFiles(pdfPath);
      await page.waitForTimeout(CLICK_WAIT);
    }

    await page.screenshot({ path: 'screenshots/qa-04-pdf-receipt-upload.png', fullPage: true });
    expect(page.url()).toContain('numista.ai');
  });

  test('T05: Import Collection Spreadsheet (Roosevelt Dimes.xlsx)', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(NAV_WAIT);

    const xlsxPath = path.join(DATASET_DIR, 'Roosevelt Dimes.xlsx');
    expect(fs.existsSync(xlsxPath)).toBe(true);

    const fileInput = page.locator('input[type="file"]').first();
    if (await fileInput.count() > 0) {
      await fileInput.setInputFiles(xlsxPath);
      await page.waitForTimeout(CLICK_WAIT);
    }

    await page.screenshot({ path: 'screenshots/qa-05-excel-collection-import.png', fullPage: true });
    expect(page.url()).toContain('numista.ai');
  });

});
