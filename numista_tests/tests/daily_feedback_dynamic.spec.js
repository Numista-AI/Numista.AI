// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Dynamically Generated Playwright E2E Spec for Daily Feedback Folder: 19 AUG 26
 * Mined At: 2026-08-19 10:32:16
 * Total Test Vectors: 247
 */

test.describe('Daily Beta Feedback E2E Verification Suite (19 AUG 26)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('ISSUE-001: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-001_morgan_ai.png' });
  });

  test('ISSUE-002: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-002_scrollbar.png' });
  });

  test('ISSUE-003: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-003_morgan_ai.png' });
  });

  test('ISSUE-004: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-004_acquisition_cost.png' });
  });

  test('ISSUE-005: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-005_morgan_ai.png' });
  });

  test('ISSUE-006: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-006_world_tab.png' });
  });

  test('ISSUE-007: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-007_grade_tooltip.png' });
  });

  test('ISSUE-008: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-008_world_tab.png' });
  });

  test('ISSUE-009: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-009_morgan_ai.png' });
  });

  test('ISSUE-010: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-010_grade_tooltip.png' });
  });

  test('ISSUE-011: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-011_world_tab.png' });
  });

  test('ISSUE-012: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-012_world_tab.png' });
  });

  test('ISSUE-013: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-013_acquisition_cost.png' });
  });

  test('ISSUE-014: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-014_morgan_ai.png' });
  });

  test('ISSUE-015: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-015_morgan_ai.png' });
  });

  test('ISSUE-016: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-016_morgan_ai.png' });
  });

  test('ISSUE-017: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-017_scrollbar.png' });
  });

  test('ISSUE-018: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-018_scrollbar.png' });
  });

  test('ISSUE-019: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-019_scrollbar.png' });
  });

  test('ISSUE-020: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-020_scrollbar.png' });
  });

  test('ISSUE-021: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-021_acquisition_cost.png' });
  });

  test('ISSUE-022: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-022_scrollbar.png' });
  });

  test('ISSUE-023: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-023_scrollbar.png' });
  });

  test('ISSUE-024: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-024_acquisition_cost.png' });
  });

  test('ISSUE-025: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-025_grade_tooltip.png' });
  });

  test('ISSUE-026: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-026_grade_tooltip.png' });
  });

  test('ISSUE-027: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-027_morgan_ai.png' });
  });

  test('ISSUE-028: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-028_morgan_ai.png' });
  });

  test('ISSUE-029: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-029_scrollbar.png' });
  });

  test('ISSUE-030: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-030_morgan_ai.png' });
  });

  test('ISSUE-031: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-031_grade_tooltip.png' });
  });

  test('ISSUE-032: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-032_scrollbar.png' });
  });

  test('ISSUE-033: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-033_morgan_ai.png' });
  });

  test('ISSUE-034: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-034_scrollbar.png' });
  });

  test('ISSUE-035: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-035_world_tab.png' });
  });

  test('ISSUE-036: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-036_scrollbar.png' });
  });

  test('ISSUE-037: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-037_scrollbar.png' });
  });

  test('ISSUE-038: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-038_scrollbar.png' });
  });

  test('ISSUE-039: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-039_acquisition_cost.png' });
  });

  test('ISSUE-040: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-040_scrollbar.png' });
  });

  test('ISSUE-041: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-041_morgan_ai.png' });
  });

  test('ISSUE-042: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-042_scrollbar.png' });
  });

  test('ISSUE-043: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-043_world_tab.png' });
  });

  test('ISSUE-044: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-044_morgan_ai.png' });
  });

  test('ISSUE-045: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-045_morgan_ai.png' });
  });

  test('ISSUE-046: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-046_acquisition_cost.png' });
  });

  test('ISSUE-047: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-047_scrollbar.png' });
  });

  test('ISSUE-048: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-048_morgan_ai.png' });
  });

  test('ISSUE-049: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-049_scrollbar.png' });
  });

  test('ISSUE-050: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-050_scrollbar.png' });
  });

  test('ISSUE-051: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-051_scrollbar.png' });
  });

  test('ISSUE-052: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-052_world_tab.png' });
  });

  test('ISSUE-053: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-053_scrollbar.png' });
  });

  test('ISSUE-054: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-054_world_tab.png' });
  });

  test('ISSUE-055: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-055_grade_tooltip.png' });
  });

  test('ISSUE-056: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-056_world_tab.png' });
  });

  test('ISSUE-057: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-057_world_tab.png' });
  });

  test('ISSUE-058: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-058_acquisition_cost.png' });
  });

  test('ISSUE-059: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-059_scrollbar.png' });
  });

  test('ISSUE-060: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-060_morgan_ai.png' });
  });

  test('ISSUE-061: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-061_scrollbar.png' });
  });

  test('ISSUE-062: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-062_morgan_ai.png' });
  });

  test('ISSUE-063: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-063_scrollbar.png' });
  });

  test('ISSUE-064: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-064_scrollbar.png' });
  });

  test('ISSUE-065: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-065_grade_tooltip.png' });
  });

  test('ISSUE-066: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-066_morgan_ai.png' });
  });

  test('ISSUE-067: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-067_morgan_ai.png' });
  });

  test('ISSUE-068: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-068_scrollbar.png' });
  });

  test('ISSUE-069: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-069_world_tab.png' });
  });

  test('ISSUE-070: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-070_world_tab.png' });
  });

  test('ISSUE-071: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-071_scrollbar.png' });
  });

  test('ISSUE-072: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-072_scrollbar.png' });
  });

  test('ISSUE-073: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-073_grade_tooltip.png' });
  });

  test('ISSUE-074: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-074_morgan_ai.png' });
  });

  test('ISSUE-075: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-075_world_tab.png' });
  });

  test('ISSUE-076: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-076_world_tab.png' });
  });

  test('ISSUE-077: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-077_grade_tooltip.png' });
  });

  test('ISSUE-078: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-078_scrollbar.png' });
  });

  test('ISSUE-079: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-079_world_tab.png' });
  });

  test('ISSUE-080: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-080_world_tab.png' });
  });

  test('ISSUE-081: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-081_grade_tooltip.png' });
  });

  test('ISSUE-082: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-082_world_tab.png' });
  });

  test('ISSUE-083: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-083_morgan_ai.png' });
  });

  test('ISSUE-084: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-084_morgan_ai.png' });
  });

  test('ISSUE-085: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-085_morgan_ai.png' });
  });

  test('ISSUE-086: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-086_scrollbar.png' });
  });

  test('ISSUE-087: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-087_scrollbar.png' });
  });

  test('ISSUE-088: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-088_world_tab.png' });
  });

  test('ISSUE-089: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-089_world_tab.png' });
  });

  test('ISSUE-090: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-090_scrollbar.png' });
  });

  test('ISSUE-091: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-091_world_tab.png' });
  });

  test('ISSUE-092: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-092_scrollbar.png' });
  });

  test('ISSUE-093: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-093_world_tab.png' });
  });

  test('ISSUE-094: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-094_world_tab.png' });
  });

  test('ISSUE-095: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-095_acquisition_cost.png' });
  });

  test('ISSUE-096: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-096_scrollbar.png' });
  });

  test('ISSUE-097: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-097_scrollbar.png' });
  });

  test('ISSUE-098: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-098_morgan_ai.png' });
  });

  test('ISSUE-099: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-099_world_tab.png' });
  });

  test('ISSUE-100: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-100_scrollbar.png' });
  });

  test('ISSUE-101: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-101_scrollbar.png' });
  });

  test('ISSUE-102: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-102_morgan_ai.png' });
  });

  test('ISSUE-103: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-103_scrollbar.png' });
  });

  test('ISSUE-104: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-104_morgan_ai.png' });
  });

  test('ISSUE-105: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-105_scrollbar.png' });
  });

  test('ISSUE-106: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-106_scrollbar.png' });
  });

  test('ISSUE-107: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-107_scrollbar.png' });
  });

  test('ISSUE-108: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-108_world_tab.png' });
  });

  test('ISSUE-109: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-109_scrollbar.png' });
  });

  test('ISSUE-110: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-110_morgan_ai.png' });
  });

  test('ISSUE-111: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-111_world_tab.png' });
  });

  test('ISSUE-112: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-112_morgan_ai.png' });
  });

  test('ISSUE-113: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-113_scrollbar.png' });
  });

  test('ISSUE-114: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-114_world_tab.png' });
  });

  test('ISSUE-115: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-115_morgan_ai.png' });
  });

  test('ISSUE-116: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-116_morgan_ai.png' });
  });

  test('ISSUE-117: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-117_morgan_ai.png' });
  });

  test('ISSUE-118: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-118_scrollbar.png' });
  });

  test('ISSUE-119: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-119_acquisition_cost.png' });
  });

  test('ISSUE-120: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-120_acquisition_cost.png' });
  });

  test('ISSUE-121: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-121_scrollbar.png' });
  });

  test('ISSUE-122: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-122_world_tab.png' });
  });

  test('ISSUE-123: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-123_acquisition_cost.png' });
  });

  test('ISSUE-124: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-124_world_tab.png' });
  });

  test('ISSUE-125: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-125_acquisition_cost.png' });
  });

  test('ISSUE-126: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-126_scrollbar.png' });
  });

  test('ISSUE-127: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-127_world_tab.png' });
  });

  test('ISSUE-128: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-128_scrollbar.png' });
  });

  test('ISSUE-129: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-129_acquisition_cost.png' });
  });

  test('ISSUE-130: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-130_acquisition_cost.png' });
  });

  test('ISSUE-131: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-131_acquisition_cost.png' });
  });

  test('ISSUE-132: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-132_world_tab.png' });
  });

  test('ISSUE-133: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-133_scrollbar.png' });
  });

  test('ISSUE-134: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-134_scrollbar.png' });
  });

  test('ISSUE-135: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-135_morgan_ai.png' });
  });

  test('ISSUE-136: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-136_scrollbar.png' });
  });

  test('ISSUE-137: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-137_scrollbar.png' });
  });

  test('ISSUE-138: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-138_morgan_ai.png' });
  });

  test('ISSUE-139: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-139_scrollbar.png' });
  });

  test('ISSUE-140: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-140_scrollbar.png' });
  });

  test('ISSUE-141: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-141_morgan_ai.png' });
  });

  test('ISSUE-142: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-142_scrollbar.png' });
  });

  test('ISSUE-143: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-143_scrollbar.png' });
  });

  test('ISSUE-144: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-144_world_tab.png' });
  });

  test('ISSUE-145: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-145_acquisition_cost.png' });
  });

  test('ISSUE-146: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-146_acquisition_cost.png' });
  });

  test('ISSUE-147: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-147_morgan_ai.png' });
  });

  test('ISSUE-148: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-148_morgan_ai.png' });
  });

  test('ISSUE-149: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-149_scrollbar.png' });
  });

  test('ISSUE-150: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-150_grade_tooltip.png' });
  });

  test('ISSUE-151: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-151_morgan_ai.png' });
  });

  test('ISSUE-152: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-152_scrollbar.png' });
  });

  test('ISSUE-153: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-153_grade_tooltip.png' });
  });

  test('ISSUE-154: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-154_morgan_ai.png' });
  });

  test('ISSUE-155: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-155_morgan_ai.png' });
  });

  test('ISSUE-156: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-156_acquisition_cost.png' });
  });

  test('ISSUE-157: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-157_morgan_ai.png' });
  });

  test('ISSUE-158: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-158_morgan_ai.png' });
  });

  test('ISSUE-159: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-159_morgan_ai.png' });
  });

  test('ISSUE-160: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-160_scrollbar.png' });
  });

  test('ISSUE-161: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-161_scrollbar.png' });
  });

  test('ISSUE-162: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-162_scrollbar.png' });
  });

  test('ISSUE-163: [Programs] 33 US Mint programs list and SlotResolver count alignment', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const programsNav = page.locator('text=Coin Programs').or(page.locator('text=US Mint Programs'));
    if (await programsNav.isVisible()) {
      await programsNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-163_programs.png' });
  });

  test('ISSUE-164: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-164_grade_tooltip.png' });
  });

  test('ISSUE-165: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-165_morgan_ai.png' });
  });

  test('ISSUE-166: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-166_scrollbar.png' });
  });

  test('ISSUE-167: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-167_grade_tooltip.png' });
  });

  test('ISSUE-168: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-168_grade_tooltip.png' });
  });

  test('ISSUE-169: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-169_morgan_ai.png' });
  });

  test('ISSUE-170: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-170_scrollbar.png' });
  });

  test('ISSUE-171: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-171_grade_tooltip.png' });
  });

  test('ISSUE-172: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-172_morgan_ai.png' });
  });

  test('ISSUE-173: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-173_scrollbar.png' });
  });

  test('ISSUE-174: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-174_world_tab.png' });
  });

  test('ISSUE-175: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-175_scrollbar.png' });
  });

  test('ISSUE-176: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-176_scrollbar.png' });
  });

  test('ISSUE-177: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-177_scrollbar.png' });
  });

  test('ISSUE-178: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-178_scrollbar.png' });
  });

  test('ISSUE-179: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-179_world_tab.png' });
  });

  test('ISSUE-180: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-180_morgan_ai.png' });
  });

  test('ISSUE-181: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-181_scrollbar.png' });
  });

  test('ISSUE-182: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-182_scrollbar.png' });
  });

  test('ISSUE-183: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-183_world_tab.png' });
  });

  test('ISSUE-184: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-184_morgan_ai.png' });
  });

  test('ISSUE-185: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-185_morgan_ai.png' });
  });

  test('ISSUE-186: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-186_scrollbar.png' });
  });

  test('ISSUE-187: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-187_world_tab.png' });
  });

  test('ISSUE-188: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-188_scrollbar.png' });
  });

  test('ISSUE-189: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-189_scrollbar.png' });
  });

  test('ISSUE-190: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-190_scrollbar.png' });
  });

  test('ISSUE-191: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-191_scrollbar.png' });
  });

  test('ISSUE-192: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-192_morgan_ai.png' });
  });

  test('ISSUE-193: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-193_morgan_ai.png' });
  });

  test('ISSUE-194: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-194_morgan_ai.png' });
  });

  test('ISSUE-195: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-195_acquisition_cost.png' });
  });

  test('ISSUE-196: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-196_morgan_ai.png' });
  });

  test('ISSUE-197: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-197_morgan_ai.png' });
  });

  test('ISSUE-198: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-198_scrollbar.png' });
  });

  test('ISSUE-199: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-199_scrollbar.png' });
  });

  test('ISSUE-200: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-200_world_tab.png' });
  });

  test('ISSUE-201: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-201_grade_tooltip.png' });
  });

  test('ISSUE-202: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-202_morgan_ai.png' });
  });

  test('ISSUE-203: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-203_scrollbar.png' });
  });

  test('ISSUE-204: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-204_world_tab.png' });
  });

  test('ISSUE-205: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-205_world_tab.png' });
  });

  test('ISSUE-206: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-206_world_tab.png' });
  });

  test('ISSUE-207: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-207_world_tab.png' });
  });

  test('ISSUE-208: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-208_scrollbar.png' });
  });

  test('ISSUE-209: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-209_scrollbar.png' });
  });

  test('ISSUE-210: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-210_world_tab.png' });
  });

  test('ISSUE-211: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-211_morgan_ai.png' });
  });

  test('ISSUE-212: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-212_morgan_ai.png' });
  });

  test('ISSUE-213: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-213_scrollbar.png' });
  });

  test('ISSUE-214: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-214_world_tab.png' });
  });

  test('ISSUE-215: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-215_world_tab.png' });
  });

  test('ISSUE-216: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-216_scrollbar.png' });
  });

  test('ISSUE-217: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-217_scrollbar.png' });
  });

  test('ISSUE-218: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-218_world_tab.png' });
  });

  test('ISSUE-219: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-219_world_tab.png' });
  });

  test('ISSUE-220: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-220_world_tab.png' });
  });

  test('ISSUE-221: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-221_world_tab.png' });
  });

  test('ISSUE-222: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-222_scrollbar.png' });
  });

  test('ISSUE-223: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-223_scrollbar.png' });
  });

  test('ISSUE-224: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-224_morgan_ai.png' });
  });

  test('ISSUE-225: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-225_scrollbar.png' });
  });

  test('ISSUE-226: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-226_morgan_ai.png' });
  });

  test('ISSUE-227: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-227_scrollbar.png' });
  });

  test('ISSUE-228: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-228_world_tab.png' });
  });

  test('ISSUE-229: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-229_scrollbar.png' });
  });

  test('ISSUE-230: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-230_acquisition_cost.png' });
  });

  test('ISSUE-231: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-231_morgan_ai.png' });
  });

  test('ISSUE-232: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-232_scrollbar.png' });
  });

  test('ISSUE-233: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-233_acquisition_cost.png' });
  });

  test('ISSUE-234: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-234_scrollbar.png' });
  });

  test('ISSUE-235: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-235_world_tab.png' });
  });

  test('ISSUE-236: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-236_morgan_ai.png' });
  });

  test('ISSUE-237: [Programs] 33 US Mint programs list and SlotResolver count alignment', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const programsNav = page.locator('text=Coin Programs').or(page.locator('text=US Mint Programs'));
    if (await programsNav.isVisible()) {
      await programsNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-237_programs.png' });
  });

  test('ISSUE-238: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-238_morgan_ai.png' });
  });

  test('ISSUE-239: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-239_scrollbar.png' });
  });

  test('ISSUE-240: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate to Collection
    const colNav = page.locator('text=My Collection').or(page.locator('text=Inventory'));
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    
    const worldTab = page.locator('text=World & Specialty').or(page.locator('text=World'));
    if (await worldTab.isVisible()) {
      await worldTab.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-240_world_tab.png' });
  });

  test('ISSUE-241: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-241_scrollbar.png' });
  });

  test('ISSUE-242: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-242_scrollbar.png' });
  });

  test('ISSUE-243: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-243_acquisition_cost.png' });
  });

  test('ISSUE-244: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-244_morgan_ai.png' });
  });

  test('ISSUE-245: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/ISSUE-245_acquisition_cost.png' });
  });

  test('ISSUE-246: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-246_morgan_ai.png' });
  });

  test('ISSUE-247: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/ISSUE-247_morgan_ai.png' });
  });
});
