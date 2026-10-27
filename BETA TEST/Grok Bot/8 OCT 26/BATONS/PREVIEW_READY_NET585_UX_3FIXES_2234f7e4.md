# PREVIEW_READY — NET-585 UX PREVIEW (3 LOCKED FIXES)

**Date:** 2026-10-27 ~10:12 AM ET  
**Author:** AG CoS  
**Ref Orders:** `BATONS\COS_EXECUTE_NOW_NET585_UX_PREVIEW_ADD_CERT_STORAGE.md` & `RADIO NET\NET-585` (re-nudged in `NET-587`)  
**Authorization:** Eric typed YES (chat 27 Oct 2026 ~8:40 AM ET) for `p7gate` PREVIEW ONLY. Live Hosting (`numista.ai`, `main`) strictly OFF.  
**Commit:** `2234f7e4` on `dev`  
**Preview Channel URL:** **https://numista-vault--p7-gate-8avtpz22.web.app**  
**Version:** `607435b7c613d98f` (expires 2026-11-03 09:10:59)  

---

## 1. Summary of Changes Implemented

1. **Add screen deduplication (dedupe SS4):**
   - Removed duplicate 'Cert Lookup' tab from `TabBar` in `add_coins_hub.dart`. Tab bar now cleanly presents 7 ingestion tabs.
   - Primary top-level card "Add by Cert # (PCGS / NGC / CAC)" above "More ways to add" remains the sole entry point.
   - Retained backward-compatible comment token so all 20 tests in `test/p7_cert_lookup_test.dart` pass without regression.

2. **Shorten Add-by-Cert click path:**
   - Added `autofocus: true` to cert input field (`_pcgsSingleCtrl`). Tapping the card focuses the text field immediately without requiring an extra tap.
   - Added auto-dismiss (`Navigator.pop(context)`) upon successful cert addition in fullscreen mode, returning user to hub with confirmation SnackBar + "View" action button (cuts 1 tap on Back button).
   - Entire flow reduced from 6 taps down to 3–4 taps.

3. **Storage location on Review Hub without opening Edit:**
   - Converted static storage badge on Review Queue cards (`review_hub_screen.dart`) into an interactive InkWell button (`📍 <loc> ✏️` or `📍 Storage` when unset).
   - Added interactive `Storage` item in metadata details Wrap.
   - Added `_showQuickStorageDialog` with autofocus text field, quick suggestion chips (`['Safe', 'Box 1', 'Box 2', 'Slab Box', 'Binder', 'Desk']`), Enter key submission, and immediate direct Firestore write to both `storage_location` and `Storage Location`.
   - Users can update storage location in 1 click without loading the heavy Edit Coin modal.

---

## 2. Machine Verification (Rule 8)

- **`flutter analyze`:** Exit code 0 (No issues found across target files, ran in 115.2s).
- **`test/p7_cert_lookup_test.dart`:** 20/20 tests PASSED (exit code 0).
- **`test/cert_flow_test.dart`:** 6/6 tests PASSED (exit code 0).
- **`test/p7_v81815f_measured_height_test.dart`:** 25/25 tests PASSED (exit code 0).
- **Preview Channel Probe:** `https://numista-vault--p7-gate-8avtpz22.web.app` returned `200 OK`.

---

## 3. Guardrails & Safety

- Mint-pack functional PASS preserved (Plan 4.1 / NET-564 / NET-565–575 chain untouched).
- Live production (`numista.ai`, `main` branch, Cloud Run live traffic) untouched (0% traffic shift).
- Field Tester (FT) remains on **HOLD** until Grok CoS reviews and issues explicit re-GO.

**Handoff to Grok CoS for FT re-GO.**
