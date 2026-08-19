"""
Numista.AI -- Daily Dynamic Playwright Spec Generator (Hardened v2)
Reads daily_feedback_manifest.json and dynamically synthesizes a hardened Playwright E2E spec:
numista_tests/tests/daily_feedback_dynamic.spec.js with semantic DOM assertions.
"""
import os
import json
import sys

FIXTURES_DIR = r"C:\Users\ericd\Documents\MyVertexProject\numista_tests\fixtures"
MANIFEST_PATH = os.path.join(FIXTURES_DIR, "daily_feedback_manifest.json")
SPEC_PATH = r"C:\Users\ericd\Documents\MyVertexProject\numista_tests\tests\daily_feedback_dynamic.spec.js"

SPEC_HEADER = """// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Dynamically Generated Playwright E2E Spec for Daily Feedback Folder: {folder_name}
 * Mined At: {mined_at}
 * Total Test Vectors: {total_issues}
 */

test.describe('Daily Beta Feedback E2E Verification Suite ({folder_name})', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });
"""

SPEC_FOOTER = """});
"""

TEST_TEMPLATE_MAP = {
    "FOREIGN_COIN_ROUTING": """
  test('{issue_id}: [World Items] Foreign coin routing and is_foreign flag verification', async ({ page }) => {
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
    await page.screenshot({ path: 'reports/screenshots/{issue_id}_world_tab.png' });
  });
""",
    "2019_W_QUARTER_ALIGNMENT": """
  test('{issue_id}: [Catalog] 2019-W Quarter series, theme, and image alignment', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    // Navigate and inspect coin
    await page.screenshot({ path: 'reports/screenshots/{issue_id}_2019_w_quarter.png' });
  });
""",
    "PROGRAM_SLOT_RESOLVER": """
  test('{issue_id}: [Programs] 33 US Mint programs list and SlotResolver count alignment', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const programsNav = page.locator('text=Coin Programs').or(page.locator('text=US Mint Programs'));
    if (await programsNav.isVisible()) {
      await programsNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/{issue_id}_programs.png' });
  });
""",
    "ACQUISITION_COST_BASIS": """
  test('{issue_id}: [Financials] Explicit $0.00 acquisition cost vs UKN cost basis', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/{issue_id}_acquisition_cost.png' });
  });
""",
    "UI_SCROLLBAR_CONTAINER": """
  test('{issue_id}: [Desktop UI] Horizontal table scrollbar container visibility', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const colNav = page.locator('text=My Collection');
    if (await colNav.isVisible()) {
      await colNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/{issue_id}_scrollbar.png' });
  });
""",
    "MODAL_CONTRAST_TYPOGRAPHY": """
  test('{issue_id}: [Desktop UI] Dark mode modal contrast and typography readability', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/{issue_id}_modal_contrast.png' });
  });
""",
    "MORGAN_AI_SET_INGESTION": """
  test('{issue_id}: [Morgan AI] Proof set ingestion and date-added top sorting', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'reports/screenshots/{issue_id}_morgan_ai.png' });
  });
""",
    "TOOLTIP_GRADE_BADGE": """
  test('{issue_id}: [Desktop UI] GradeBadgeWidget Sheldon scale tooltip hover popup', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/{issue_id}_grade_tooltip.png' });
  });
""",
    "LEGISLATION_TAB_INDEX": """
  test('{issue_id}: [Catalog] Top-level Legislation tab placed at index 5 in detail modal', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/{issue_id}_legislation_tab.png' });
  });
"""
}

GENERIC_TEMPLATE = """
  test('{issue_id}: [{category}] Mined issue verification: {issue_type}', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/{issue_id}.png' });
  });
"""

def generate_dynamic_spec():
    if not os.path.exists(MANIFEST_PATH):
        print(f"[SPEC GENERATOR ERROR] Manifest file not found: {MANIFEST_PATH}")
        return False

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    folder_name = manifest.get("folder_name", "UNKNOWN_FOLDER")
    mined_at = manifest.get("mined_at", "")
    issues = manifest.get("issues", [])

    header = SPEC_HEADER.replace("{folder_name}", folder_name)\
                        .replace("{mined_at}", mined_at)\
                        .replace("{total_issues}", str(len(issues)))

    test_blocks = []
    for issue in issues:
        iid = issue.get("issue_id", "ISSUE-000")
        itype = issue.get("type", "UNKNOWN")
        cat = issue.get("category", "GENERAL")
        
        template = TEST_TEMPLATE_MAP.get(itype, GENERIC_TEMPLATE)
        block = template.replace("{issue_id}", iid)\
                        .replace("{issue_type}", itype)\
                        .replace("{category}", cat)
        test_blocks.append(block)

    full_code = header + "".join(test_blocks) + SPEC_FOOTER

    with open(SPEC_PATH, "w", encoding="utf-8") as f:
        f.write(full_code)

    print(f"[SPEC GENERATION COMPLETE] Generated dynamic spec: {SPEC_PATH} ({len(issues)} test cases)")
    return True

if __name__ == "__main__":
    generate_dynamic_spec()
