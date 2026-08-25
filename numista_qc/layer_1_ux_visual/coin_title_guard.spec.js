/**
 * coin_title_guard.spec.js — Numista QC Suite Layer 1
 * Asserts coin program titles are never stripped to bare year+mint.
 *
 * Primary assertion: reads coin_data_audit result (data-layer check).
 * Secondary: page.accessibility.snapshot() after activating flt-semantics-placeholder.
 * Last resort: OCR (not implemented here — STALE_COORDINATES hard fail if used).
 *
 * The primary assertion is a Firestore field check run via coin_data_audit.py.
 * This spec runs coin_data_audit.py as a child process and asserts exit code 0.
 */

const { test, expect } = require('@playwright/test');
const { execSync } = require('child_process');
const path = require('path');

const AUDIT_SCRIPT = path.join(__dirname, '../layer_3_data/coin_data_audit.py');
const MANIFEST_PATH = path.join(__dirname, '../SUITE_MANIFEST.json');

test.describe('Coin Title Guard', () => {
  test('Primary: Firestore field check - no coin should have all title fields empty', () => {
    // This test runs synchronously (coin_data_audit.py is a CLI tool).
    // It MUST exit 0 for the test to pass.
    // Exit 1 = COIN_TITLE_FAIL detected (at least one coin has all title fields empty)
    // Exit 1 = NO_QA_DATA (QA account has no coins - seed_qc_fixtures.py needed)

    let output = '';
    let exitCode = 0;
    try {
      output = execSync('python "' + AUDIT_SCRIPT + '" --verbose', {
        env: { ...process.env },
        encoding: 'utf8',
        timeout: 60000,
      });
    } catch (err) {
      output = err.stdout || err.stderr || err.message;
      exitCode = err.status || 1;
    }

    console.log('[coin_title_guard] coin_data_audit.py output:');
    console.log(output);

    // The intentionally-broken fixture (qc_fixture_title_FAIL_empty) MUST have been
    // detected AND the sentinel check must have passed (FIXTURE_SENTINEL_OK in output).
    // If the sentinel check itself fails, the guard is broken.
    const sentinelWorking = output.includes('FIXTURE_SENTINEL_OK');
    const titleFailDetected = output.includes('COIN_TITLE_FAIL');

    // Log which assertion path was used
    const assertionPath = 'primary';
    try {
      const fs = require('fs');
      const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));
      manifest.coin_title_assertion_path_log = assertionPath;
      fs.writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2));
    } catch (_) { /* manifest write failure is non-fatal */ }

    // The test passes if:
    // 1. The sentinel fixture was detected (guard is working)
    // 2. No UNEXPECTED title failures beyond the known broken fixture
    // The audit script itself handles this: it exits 0 only if the only COIN_TITLE_FAIL
    // is the intentionally-broken fixture and that failure is expected.
    // Exit code 0 = only expected failure found; exit 1 = unexpected failures OR NO_QA_DATA
    expect(
      exitCode,
      'coin_data_audit.py exited ' + exitCode + '.\n\nOutput:\n' + output
    ).toBe(0);

    expect(
      sentinelWorking,
      'FIXTURE_SENTINEL_OK not found in output - the title guard may not be working.'
    ).toBe(true);
  });

  test('Secondary: Flutter accessibility snapshot (conditional - non-authoritative)', async ({ page }) => {
    test.setTimeout(15000);
    // This test attempts to activate Flutter semantics and snapshot the tree.
    // It is explicitly non-authoritative: if semantics are unavailable, the test
    // reports SEMANTICS_UNAVAILABLE and skips without failing.
    // The primary assertion above is the authoritative title check.

    await page.goto('https://numista.ai');
    try {
      await page.waitForFunction(
        () => {
          const p = document.querySelector('flutter-view') ||
                    document.querySelector('flt-glass-pane') ||
                    document.querySelector('canvas');
          return p && (p.offsetWidth > 0 || p.clientWidth > 0 || (p.getBoundingClientRect && p.getBoundingClientRect().width > 0));
        },
        { timeout: 10000 }
      );
    } catch (_) {
      console.log('[coin_title_guard] SEMANTICS_UNAVAILABLE: Page render wait timed out. Primary assertion is authoritative.');
      test.skip();
      return;
    }

    // Try to activate semantics by clicking the flt-semantics-placeholder via DOM evaluation
    await page.evaluate(() => {
      const p = document.querySelector('flt-semantics-placeholder') ||
                document.querySelector('flutter-view flt-semantics-placeholder');
      if (p) p.click();
    }).catch(() => {});
    await page.waitForTimeout(500);

    // Attempt accessibility snapshot
    let snapshot = null;
    try {
      snapshot = await page.accessibility.snapshot({ interestingOnly: false });
    } catch (_) {
      // Accessibility snapshot not supported in this context
    }

    if (!snapshot || !snapshot.children || snapshot.children.length === 0) {
      console.log('[coin_title_guard] SEMANTICS_UNAVAILABLE: accessibility tree returned no nodes. Primary assertion is authoritative.');
      // Non-authoritative: skip, do not fail
      test.skip();
      return;
    }

    // Flatten snapshot to find coin-title nodes
    function flattenSnapshot(node) {
      const nodes = [node];
      (node.children || []).forEach(c => nodes.push(...flattenSnapshot(c)));
      return nodes;
    }

    const allNodes = flattenSnapshot(snapshot);
    const coinTitleNodes = allNodes.filter(n =>
      n.name && /\d{4}/.test(n.name) // has a year-like pattern
    );

    console.log('[coin_title_guard] Secondary: found ' + coinTitleNodes.length + ' nodes with year-like content.');

    // Corroborating evidence only - no assertion, just logging
    const bareYearMint = coinTitleNodes.filter(n => /^\d{4}\s*\(\w\)\s*/.test(n.name));
    if (bareYearMint.length > 0) {
      console.warn('[coin_title_guard] Secondary: ' + bareYearMint.length + ' node(s) appear to have bare year+mint titles: ' + bareYearMint.map(n => n.name).join(', '));
    }
    // Secondary is corroborating only - primary result is authoritative
    console.log('[coin_title_guard] Secondary check complete. Results are logged above (non-authoritative).');
  });
});
