# Walkthrough — E2E Suite Remediation (2026-08-14)

## Overview
Morning audit (Aug 14) found 11 E2E failures across 4 newly added suites (18–21). All failures shared the same root cause and were resolved in this session.

## Root Cause
Suites 18–21 were written with `goto('/')` + a bare `flt-glass-pane` visibility assertion as their entry point. The Flutter glass pane only becomes visible when the app renders into a fully authenticated session. The automated nightly runner has no authenticated session established — it navigates to `/` and gets the public landing page, where `flt-glass-pane` never appears, causing all assertions to time out at 15 seconds.

## Fix Applied to All 4 Suites
Replaced `goto('/') + flt-glass-pane` gating with the `enterDemo()` helper already used by suites 01–17:

```js
async function enterDemo(page) {
  await page.goto('https://numista.ai');
  await page.waitForTimeout(4000);
  const demoBtn = page.getByRole('button', { name: /browse demo/i });
  if (await demoBtn.count() > 0) {
    await demoBtn.click();
  } else {
    await page.mouse.click(841, 647); // coordinate fallback
  }
  await page.waitForTimeout(4000);
  await page.setViewportSize({ width: 1280, height: 1000 });
  await page.waitForTimeout(1000);
}
```

Suite 21 (1920×1080 scrollbar test) uses the 1920×1080 viewport in `enterDemo()` instead of 1280×1000.

## Files Modified
- `numista_tests/tests/18-aug13-world-remediation.spec.js`
- `numista_tests/tests/19-aug12-programs-slot-resolver.spec.js`
- `numista_tests/tests/20-aug12-morgan-ai-proofsets.spec.js`
- `numista_tests/tests/21-aug12-ui-scrollbar-contrast.spec.js`

## Verified Results
- 11/11 tests passing (2 min run, single worker)
- Nightly suite will now show 143/145 active tests passing · 2 skipped (local server)

## Outstanding Items
| Item | Priority | Notes |
|---|---|---|
| 127 Dependabot alerts | Medium | Deferred to dedicated security session closer to Nov 2026 launch |
| Merge `dev → main` | Owner decision | 22 CVE fixes in `dev` not yet on `main` |
| Suites 18–21 semantic depth | Low | Tests now enter demo, but prod-account-specific assertions (provenance data, slot counts) should be re-evaluated as real prod account test vectors |
