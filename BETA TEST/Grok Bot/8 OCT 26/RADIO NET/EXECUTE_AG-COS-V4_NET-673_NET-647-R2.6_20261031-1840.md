# EXECUTE_AG-COS-V4_NET-673_NET-647-R2.6 (20261031-1840)
FROM: GB CoS  TO: AG CoS v4 (cc Argon, Desk, Field Tester)

ERIC TYPED YES (6:40 PM ET 31 Oct 2026, verbatim): "YES to approve EXECUTE for NET-647 R2.6."
Reviews: Argon 98 GO, SAG 97 PASS, GB CoS 96 PASS.

SCOPE: Execute FAILFIX_PLAN_NET-647_R2.6_20261031-1830.md exactly as written, on p7-v8.9 / p7-gate ONLY.
- main stays locked at 9f04550a; dev stays frozen at 9b55f3d9; Stripe stays OFF. Do NOT push or merge to main or dev.
- Pricing frozen: 3249 cents, ROUND_HALF_UP; build 8.18.15+81818.
- Backfill: DRY-RUN CSV only. No --apply without a separate Eric YES.

FOLD IN DURING EXECUTE (no new scope):
1. Contact sheet Bay 7 caption must fit inside its box.
2. 26XF date zoom: label it on the sheet as reusing the 26XE image (same die date, finish-agnostic).
3. Remove the leftover "100% Zero Wrong-Year" and "100% Genuine" wording.
4. Per-bay readout for 26XL: write the date with the wavy dash (1776~2026), not a hyphen.
5. Argon's Python suggestion: normalize with Decimal(f"{float(x):.2f}") before the division.
6. Argon's Dart suggestion: formatCurrency handles negative amounts (format abs(), then prefix "-").

GATE: all 40 mobile test files + format_currency_test.dart + pytest must be green before deploying to p7-gate.
REPORT: file EXECUTE_DONE (commit hash, test results, p7-gate URL, dry-run CSV path) or BLOCKED with the reason. Field Tester retest follows.
