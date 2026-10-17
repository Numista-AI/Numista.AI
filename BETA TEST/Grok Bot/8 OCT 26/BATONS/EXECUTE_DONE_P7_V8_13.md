# EXECUTE_DONE: P7 V8.13 Build

**Date:** 2026-10-17 17:05 ET  
**Author:** AG CoS  
**Branch:** `p7-v8.9`  
**Commit SHA:** `86f646da4243effac1597230c5483b32314cb726` (short: `86f646da`)  
**Git Push Target:** `origin/p7-v8.9` (pushed `689e2ca1..86f646da`)  
**Flutter Analyze:** 0 errors, 0 warnings (`No issues found! (ran in 3.8s)`)  
**Flutter Test:** 577/577 passed (+1 new test over baseline 576)  

---

## 1. Summary of Changes & Fixes (NET-298)

| Item (NET-298) | Description | Verbatim File & Line Cites (`git show 86f646da`) | Verification |
|---|---|---|---|
| **Fix 1: Full-Fidelity JSON Backup** | Removed lossy coin sanitization from `generateExportPayload()`: `Cost` remains raw numeric (`15.5`), `Added` remains raw timestamp without date-only truncation, `Year` is not cast to int, and blank `Retailer`, `Invoice`, and `Notes` keys are not injected. Supported `mockCoins` parameter for zero-network testing. | `numista_mobile/lib/services/backup_export_service.dart:18-58, 126-161` | **PASS (code + unit test)**<br>Tested in `p7_v813_json_export_full_fidelity_and_csv_formatting`: JSON coin has `Cost == 15.5` (num), no injected blank keys, raw map preserved |
| **Fix 2: Full ISO Datetime in JSON Serialization** | Reverted `JsonEncoder` timestamp formatter in `exportJsonDownload()` and exposed `generateJsonStringFromPayload()`: converts `Timestamp` to `.toDate().toIso8601String()` and `DateTime` to `.toIso8601String()` (full datetime string > 10 chars), eliminating date-only truncation across all exported collections. | `numista_mobile/lib/services/backup_export_service.dart:221-240` | **PASS (code + unit test)**<br>Tested in `p7_v813_json_export_full_fidelity_and_csv_formatting`: JSON string has `Added` as full ISO datetime (`length > 10`) |
| **Fix 3: CSV-Only Display Formatting** | Maintained display formatting in `generateCsvStringFromPayload()` only: formatted `$XX.XX` Cost, `yyyy-MM-dd` Added date, integer Year, Qty/Retailer/Invoice/Notes columns with fallback support for `payload['collections']['coins']`. | `numista_mobile/lib/services/backup_export_service.dart:246` | **PASS (code + unit test)**<br>Tested in `p7_v813_json_export_full_fidelity_and_csv_formatting`: CSV row outputs `"$15.50"` and `"2024-10-17"` correctly |
| **Fix 4: UX Safety Test Suite** | Added `p7_v813_json_export_full_fidelity_and_csv_formatting` covering both Test A (full-fidelity JSON payload + serialization) and Test B (display formatting CSV generation). | `numista_mobile/test/p7_v8_ux_safety_test.dart:1-5, 1738-1782` | **PASS (unit test)**<br>Verified in full test run |

---

## 2. Verification Commands & Outputs

1. **`flutter analyze lib/`**
   ```
   Analyzing lib...
   No issues found! (ran in 3.8s)
   ```
   0 errors, 0 warnings.

2. **`flutter test --reporter compact`**
   ```
   00:21 +577: All tests passed!
   ```
   Baseline: 576 -> 577 (+1 new automated test). 100% passed.

3. **`git push origin p7-v8.9`**
   ```
   To https://github.com/Numista-AI/Numista.AI.git
      689e2ca1..86f646da  p7-v8.9 -> p7-v8.9
   ```

---

## 3. Scope and Policy
- ≤2 files modified: `numista_mobile/lib/services/backup_export_service.dart`, `numista_mobile/test/p7_v8_ux_safety_test.dart`
- Rule 9.3 applies (no GEMINI38 review needed for small surgical fixes ≤2 files).
- Baton not renamed (reserved for parent AG CoS).
