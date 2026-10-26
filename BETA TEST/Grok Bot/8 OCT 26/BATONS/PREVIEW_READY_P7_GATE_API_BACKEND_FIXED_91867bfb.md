# PREVIEW READY — P7-GATE PREVIEW /api BACKEND FAIL-FIX VERIFIED
**FROM:** AG CoS  **TO:** Grok CoS, Field Tester  **INFO:** Argon, Eric  
**DATE:** 26 Oct 2026 ~11:55 AM ET  
**PREVIEW CHANNEL URL:** https://numista-vault--p7-gate-8avtpz22.web.app  
**BUILD VERSION:** v8.18.15h (Release 8.18.15 / 81818)  
**BACKEND PIN:** `https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app` (revision `numista-backend-00487-hub`, tag `p7gate`, B4 guard active)  
**SCAN SERVICE PIN:** `https://p7gate---numista-scan-service-qntvrqvxma-uc.a.run.app`  

---

## 1. BLUF & Resolution Summary
FAIL-FIX reported in NET-534 / `FAILFIX_EXECUTE_P7_GATE_HOSTING_API_REWRITE.md` is **RESOLVED** and verified on live preview.

### Root Cause
1. Previous preview upload in NET-532 deployed cached pre-existing build artifacts without invoking `flutter build web` with `--dart-define` backend overrides, leaving the frontend bundle at stale `v4.403` with default backend URL `https://numista-backend-568985927038.us-central1.run.app`.
2. In `numista_mobile/web/add_coins.html`, `getApiBaseUrl()` had a hardcoded `LIVE_URL` fallback that resolved to `568985927038.us-central1.run.app` unless an explicit `?api=` parameter was passed.

### Fix Implemented
1. Executed full fresh production Flutter web release compile:
   ```bash
   flutter build web --release \
     --dart-define=FLUTTER_ENV=prod \
     --dart-define=API_BASE_URL=https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app \
     --dart-define=SCAN_SERVICE_URL=https://p7gate---numista-scan-service-qntvrqvxma-uc.a.run.app
   ```
2. Updated `numista_mobile/web/add_coins.html`:
   ```javascript
   function getApiBaseUrl() {
     var P7GATE_URL = 'https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app';
     var LIVE_URL = 'https://numista-backend-568985927038.us-central1.run.app';
     var defaultUrl = (window.location && window.location.origin && window.location.origin.indexOf('--p7-gate-') !== -1)
       ? P7GATE_URL
       : LIVE_URL;
     return resolveApiBase(window.location.origin, window.location.search, defaultUrl);
   }
   ```
3. Deployed to Firebase Hosting preview channel `p7-gate` (`--project studio-9101802118-8c9a8 --site numista-vault`):
   - Version: `6827e011bc9e8619`
   - Expiration: `2026-11-02 10:54:18` (7 days)

---

## 2. Machine-Checked Proof & Smoke Verification

### (a) Page & App Version Label
- `version.json` check:
  ```json
  {"app_name":"numista_ai","version":"8.18.15","build_number":"81818","package_name":"numista_ai"}
  ```
- App version history in bundle contains `v8.18.15h`.

### (b) Frontend & add_coins.html Backend Binding
- `main.dart.js` fetched from `https://numista-vault--p7-gate-8avtpz22.web.app/main.dart.js`:
  - Contains string: `p7gate---numista-backend-qntvrqvxma-uc.a.run.app` -> **MATCH**
  - Contains string: `v8.18.15h` -> **MATCH**
- `add_coins.html` fetched from `https://numista-vault--p7-gate-8avtpz22.web.app/add_coins.html`:
  - Contains string: `https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app` -> **MATCH**
  - Preview origin auto-detection active: `origin.indexOf('--p7-gate-') !== -1` defaults to `P7GATE_URL`.

### (c) Production & Cloud Run Safety Constraints
- **NO** live Hosting deploy (`numista-vault.web.app` untouched).
- **NO** merge to `main`.
- **NO** Cloud Run live traffic shift (live traffic remains on baseline; `p7gate` tag accessed exclusively via tag URL).
- **NO** spend incurred.

---

## 3. Ready for Field Tester Re-GO
The preview channel is re-armed, verified, and ready for Field Tester to execute the full Invoices gate (26SQRP and subsequent PDFs) against the pinned `p7gate` revision (00487-hub / B4).
