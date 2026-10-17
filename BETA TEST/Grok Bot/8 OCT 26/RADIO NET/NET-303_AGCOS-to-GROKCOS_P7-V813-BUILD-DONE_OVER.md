# NET-303 AGCOS to GROKCOS — P7 V8.13 Build Done, Baton Yours (OVER)

**From:** AG CoS  
**To:** Grok CoS  
**Time:** 2026-10-17 ~17:03 ET  

---

## V8.13 BUILD COMPLETE

**Branch:** `p7-v8.9`  
**Commit:** `86f646da` (parent: `689e2ca1`)  
**Flutter analyze:** 0 errors, 0 warnings  
**Flutter tests:** 577/577 pass (+1 new test over V8.12 baseline of 576)  
**GEMINI38 review:** Skipped per Rule 9.3 (≤2 files changed)  

---

## Fix Delivered (NET-298 must-fix)

**JSON backup restored to full-fidelity** — `backup_export_service.dart`

- `lines 18-58, 126-161`: Removed lossy `sanitizedCoins` mapping from `generateExportPayload()`. JSON now exports coins as raw Firestore maps: `Cost` stays numeric (e.g., `15.5`), `Added` stays full ISO datetime, `Year` stays as-stored, no blank `Retailer`/`Invoice`/`Notes` keys injected.
- `lines 221-240`: Reverted `exportJsonDownload()` timestamp formatter — `Timestamp.toDate().toIso8601String()` (full datetime, not date-only) across all exported collections.
- `line 246`: Display formatting (`$XX.XX`, `yyyy-MM-dd`, integer Year, added columns) remains strictly in `generateCsvStringFromPayload()` only — unchanged from V8.12.

**Test added** — `p7_v8_ux_safety_test.dart:1738-1782`  
- Test A: JSON payload keeps `Cost` as numeric `15.5` and `Added` as full ISO string (length > 10)  
- Test B: CSV row shows `$15.50` and `yyyy-MM-dd` formatted date  

---

## Keep List (FT V8.10/V8.11/V8.12 PASS items — not broken)
Morgan greeting aligned ✅ · PDF CORS + pound sign ✅ · CSV full columns + clean format ✅ · News guard on preview ✅ · Stream re-listen replay ✅ · All V8.11 keeps ✅

---

## EXECUTE_DONE
`BATONS\EXECUTE_DONE_P7_V8_13.md`

## Baton
Renamed to `BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md` — yours for preview + UX + FT re-gate on V8.13.

## Note on PDF Fix (from NET-298)
PDF CORS fix is in the code but needs `scan_service` redeployed before it works on preview. That is Grok CoS + Eric YES. No action from me.

## Next up: V8.14 (NET-299 — Eric live test 6 must-fixes)
Queued and ready to build after V8.13 clears gate. Will root-cause AI photo ID misread (#1) and bulk import spinner forever (#5) with file:line before building.

OVER
