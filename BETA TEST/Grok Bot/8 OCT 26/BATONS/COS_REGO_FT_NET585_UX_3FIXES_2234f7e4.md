# COS_REGO - FT - NET-585 UX PREVIEW 3 FIXES (2234f7e4)

- **DTG:** 2026-10-27 ~10:25 AM ET | **From:** Grok CoS | **To:** Field Tester (cc AG CoS)
- **HOLD lifted:** `WAKE_FIELDTESTER_HOLD_NET585-NO-CANARY-UNTIL-COS-REGO_20261027-0840.md` superseded.
- **Preview:** https://numista-vault--p7-gate-8avtpz22.web.app (preview only, live OFF)
- **Score:** `BATONS\COS_SCORE_NET585_UX_3FIXES_2234f7e4_PASS_WITH_NOTES_20261027-1025.md`

## Test (Eric / tester account items only)
1. Add screen: "Add by Cert # (PCGS / NGC / CAC)" appears once; no 'Cert Lookup' tab in the tab bar; other 6 tabs open the right screen.
2. Tap the cert card: cursor is already in the cert box; Enter submits; success returns to hub with green SnackBar. Tap "View" and confirm it opens the coin (N2).
3. Deep-link entry to cert (if reachable) also works; note whether it auto-returns (N1, expected not to).
4. Review Hub: tap the storage badge / "+ Set Location" on a card, pick a preset, Save; badge updates without opening Edit Coin. Try Enter key and Clear (empty).
5. Regression spot-check: mint-pack flow still PASS.

File `FT_RESULT_NET585_...` + NET to Grok CoS. Report-only, no live writes beyond normal tester edits.