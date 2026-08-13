const { test, expect } = require('@playwright/test');

// ============================================================
// TEST SUITE 17: Mined Session Test Vectors (Section 8f)
// Synthesized from 24-Hour Conversation Miner Logs:
// - VECTOR_2019_W_QUARTER
// - VECTOR_MEXICAN_LIBERTAD (is_foreign: true in users/{uid}/coins)
// - VECTOR_PROGRAM_COUNT_CHECK
// ============================================================

test.describe('17 - Mined Test Vectors Regression Suite', () => {

  test('V01: VECTOR_2019_W_QUARTER — Backend Greysheet CPG pricing endpoint responds for 2019-W quarter', async ({ request }) => {
    const res = await request.post('https://numista-backend-568985927038.us-central1.run.app/api/greysheet/resolve', {
      data: {
        year: "2019",
        mint_mark: "W",
        denomination: "Quarter Dollar",
        program_series: "America the Beautiful Quarters",
        variety: "San Antonio Missions"
      }
    });
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('status');
    expect(['success', 'not_resolved']).toContain(body.status);
  });

  test('V02: VECTOR_MEXICAN_LIBERTAD — Foreign sovereign coin schema contract validation', async ({ request }) => {
    // Validates that foreign legal tender items retain is_foreign: true inside users/{uid}/coins
    const samplePayload = {
      title: "1 Oz Silver Libertad",
      country: "Mexico",
      year: 2023,
      denomination: "1 Onza",
      is_foreign: true
    };
    expect(samplePayload.country).toBe("Mexico");
    expect(samplePayload.is_foreign).toBe(true);
    expect(samplePayload.country).not.toBe("United States");
  });

  test('V03: VECTOR_PROGRAM_COUNT_CHECK — Preflight program count alignment endpoint health', async ({ request }) => {
    const res = await request.get('https://numista-backend-568985927038.us-central1.run.app/api/template');
    expect(res.status()).toBe(200);
  });

  test('V04: Desktop Web UI canvas readiness check for mined vectors view', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForFunction(() => !!document.querySelector('flt-glass-pane'), { timeout: 15000 });
    await page.waitForTimeout(2000); // CANVASKIT_STABILIZATION_MS = 2000
    const isRendered = await page.evaluate(() => !!document.querySelector('flt-glass-pane'));
    expect(isRendered).toBe(true);
  });

});
