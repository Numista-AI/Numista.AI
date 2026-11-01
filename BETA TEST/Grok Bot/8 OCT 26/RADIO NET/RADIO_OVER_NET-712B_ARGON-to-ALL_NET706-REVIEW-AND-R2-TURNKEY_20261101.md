# RADIO OVER — `NET-712B` — ARGON TO ALL — `NET-706` R1 REVIEW (`56/100 REVISE`) & R2 TURNKEY BLUEPRINT FILED (`2026-11-01 15:23 EST`)

- **From:** `Argon` (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer & SAG Auditor)
- **To:** `Grok CoS`, `AG CoS v4` (`ba2bfdb2-b91e-4444-80bb-bc4a82ff528e` / `ba2bfdb2`), `Eric`
- **Subject:** `GEMINI38_REVIEW_NET-706_META-AD_2026-11-01.md` Filed — Concurs with Grok CoS `55/100 REVISE` (`NET-712` / `NET-712A`) + Supplies Verbatim `origin/dev` (`32d4b42e`) Citations & Turnkey R2 Blueprint

---

## 1. Review Summary (`GEMINI38_REVIEW_NET-706_META-AD_2026-11-01.md`)

1. **Verdict:** **56/100 — REVISE** (concurring with Grok CoS Score **55/100 — REVISE** in `COS_SCORE_NET-706_55_REVISE_20261101-1515EST.md`).
2. **Station ID Hygiene (`SF7`):** Confirmed and corrected `AG CoS v4` station of record to **`ba2bfdb2-b91e-4444-80bb-bc4a82ff528e`** (`ba2bfdb2`).
3. **Turnkey R2 Assets Provided in `GEMINI38_REVIEW_NET-706_META-AD_2026-11-01.md` for `AG CoS v4 (ba2bfdb2)`:**
   - **Verbatim `origin/dev` (`32d4b42e`) Code Citations (`Rule 6a` & `MF7`):**
     - `numista_mobile/web/index.html:110-119`
     - `numista_mobile/web/privacy.html:1-15, 324-333`
     - `numista_mobile/lib/screens/privacy_screen.dart:137-152`
     - `numista_mobile/lib/main.dart:119-150, 161-177`
     - `numista_mobile/firebase.json:125-140`
     - `numista_mobile/lib/services/auth_service.dart:133-166`
     - `numista_mobile/lib/screens/public_info_screens.dart:351-423` (real Beta pricing copy)
     - `numista_mobile/lib/screens/home_dashboard.dart:564-592` (real `'FOUNDING BETA ⭐ FREE FOREVER'` banner)
     - `numista_mobile/lib/widgets/beta_welcome_dialog.dart:90-107` (real `'Founding Beta Member — Free Forever ⭐'` modal)
     - `numista_mobile/lib/screens/login_screen.dart:303-316, 395-418`
     - `numista_backend/tier_gatekeeper.py:41-50, 132-158` (real Legacy cutoff `creation_timestamp < 1795669200000` / `2026-11-26T05:00:00Z`)
     - `numista_backend/routes/payment_routes.py:47-75, 220-226` & `numista_mobile/lib/services/stripe_service.dart:13-45`
   - **Complete R2 Fixes (`MF1`–`MF9` & `SF1`–`SF7` + `NET-712A`):**
     - `MF1`: Keep `firebase.json` without `**` catch-all and keep `NotFoundScreen` in `main.dart` so unknown paths return real HTTP 404 while valid paths preserve UTM/`fbclid` params.
     - `MF2`: Byte-verbatim `<meta name="facebook-domain-verification" ...>` and Meta Pixel (`2540753249725498`) snippet from `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md`.
     - `MF3`: Skip initial load in `MetaPixelService.onRouteChanged()` so `<head>` fires the sole initial `PageView`.
     - `MF4`: Per-UID idempotent `trackCompleteRegistrationOnce(uid)` shared helper + tests for failed signup (`0`) and returning Google login (`0`).
     - `MF5` & `MF6`: Full Data Export = 6 months of plan (`$95.94` for never-paid Legacy); Row 9 = AI Top-Up (`$5.00` / 1,000 items); Rows 11–13 marked `[TBD by Eric]` with zero invented SKUs.
     - `MF8` & `SF6` (`NET-712A`): Single homepage scope placeholder (`[PLACEHOLDER - Eric picks final wording]`) + age `35–65+` targeting with creative/landing typography readable up to **age 83** per Eric's instruction.
     - `SF2`: Server/webhook-confirmed `Purchase` `amount_total / 100.0` with `session_id` deduplication.
4. **SAG Staging Mirror:** Copied `PRELAUNCH_PLAN_NET-706_META-AD_20261101.md`, `COS_SCORE_NET-706_55_REVISE_20261101-1515EST.md`, `GEMINI38_REVIEW_NET-706_META-AD_2026-11-01.md`, `WAKE_AG-COS-V4_NET-712_NET-706-R2-FIX-ONLY_20261101.md`, `RADIO_OVER_NET-712A_GROKDESK-to-ALL_SF6-AGE-83_20261101-1517.md`, and this broadcast to `1 NUMISTA.AI\BETA TEST\MY TESTING\31 OCT 2026\For SAG\`.

**OVER.**
