# EXECUTE_DONE_P7_V8_17.md

**Date:** 2026-10-18 ~19:53 ET  
**Author:** AG CoS P7 V8.17 Subagent  
**Branch:** `p7-v8.9`  
**Commit SHA:** `dbda922f7ae5c9b34e7ed60df10893b9d88fbd2b` (`dbda922f`)  
**Commit Message:** `fix(p7-v8.17): pin ?api= host regex to our project IDs only, extract resolveApiBase()`  

---

## 1. Summary of Changes
Targeted 2-file security fix pinning the `?api=` Cloud Run host regex strictly to Numista.AI project IDs, and extracting the pure function `resolveApiBase(origin, search, liveUrl)` with direct self-test coverage.

- `numista_mobile/web/add_coins.html`
- `numista_mobile/web/scraper_dashboard.html`

No backend code modified. No Dart code modified. No deploys performed.

---

## 2. File & Line Details

### `numista_mobile/web/add_coins.html`
- **`resolveApiBase(origin, search, liveUrl)`:** Lines 527–547
- **`ALLOWED_HOST_RE` (new pinned):** Line 541
  ```javascript
  var ALLOWED_HOST_RE = /^(?:[a-z0-9-]+---)?numista-(?:backend|scan-service)-(?:568985927038\.us-central1\.run\.app|qntvrqvxma-uc\.a\.run\.app)$/;
  ```
- **`ALLOWED_HOST_RE` (old broad, replaced):** Was at Line 563 (and self-test line 1176)
- **`getApiBaseUrl()` wrapper:** Lines 549–552
- **Self-tests:** Lines 1157–1173 (12 tests total: 4 accept + 8 reject)

### `numista_mobile/web/scraper_dashboard.html`
- **`resolveApiBase(origin, search, liveUrl)`:** Lines 522–542
- **`ALLOWED_HOST_RE` (new pinned):** Line 536
  ```javascript
  var ALLOWED_HOST_RE = /^(?:[a-z0-9-]+---)?numista-(?:backend|scan-service)-(?:568985927038\.us-central1\.run\.app|qntvrqvxma-uc\.a\.run\.app)$/;
  ```
- **`ALLOWED_HOST_RE` (old broad, replaced):** Was at Line 558 (and self-test line 926)
- **`getApiBaseUrl()` wrapper:** Lines 544–547
- **Self-tests:** Lines 907–923 (12 tests total: 4 accept + 8 reject)

---

## 3. Self-Test Counts & Verification
- **add_coins.html:** 12 tests (4 accept [a1–a4] + 8 reject [r1–r8]). Verified 100% pass via Node evaluation.
- **scraper_dashboard.html:** 12 tests (4 accept [a1–a4] + 8 reject [r1–r8]). Verified 100% pass via Node evaluation.
- **Broad regex elimination:** Confirmed via repository grep; only the pinned project IDs regex is present.

---

## 4. Rule Notes
- **Rule 9.3:** ≤2 files touched; no GEMINI38 review required.
- **Test execution:** HTML/JS-only change; no flutter or pytest runs required.
- **Git:** Staged explicit file paths only (no `git commit -a`), rebased on `origin/p7-v8.9`, pushed cleanly to `origin/p7-v8.9`.
