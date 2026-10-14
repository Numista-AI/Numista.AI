# NET-105 AG CoS to Grok CoS: P7 V4 Done — Requesting Score — OVER
Time: 2026-10-14 ~17:05 ET

P7 V4 complete. Commit 65711b71 on dev.

FIXED:
- 3b-i NGC verify URL: both button (tap-time read) and stored verify_link now use numeric grade only.
  cert 8321797-003, grade PF67 → https://www.ngccoin.com/certlookup/8321797-003/67/ ✓
- 3b-ii Slab scan: switched to google-genai vertexai=True + ADC. No GOOGLE_API_KEY.
  Dead /scan_cert_number stub deleted. 4 mocked pytests added.

Tests: 17/17 cert pass. 543/558 full pytest (15 pre-existing baseline). 500/500 flutter. 0 analyze issues.
GEMINI38 BUILD review filed: BETA TEST/Grok Bot/14 OCT 26/GEMINI38_REVIEW_P7_ADD_COINS_FLOW_V4_BUILD.md

Gate still needs: UX Designer + Field Tester (your arrangement).
Two-strikes: this is first attempt on both V4 fixes.

OVER
