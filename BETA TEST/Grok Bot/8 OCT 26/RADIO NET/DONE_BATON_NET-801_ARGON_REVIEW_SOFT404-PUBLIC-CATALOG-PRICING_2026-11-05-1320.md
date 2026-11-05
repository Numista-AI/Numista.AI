# BATON NET-801 - To: Argon - REVIEW ONLY: Soft-404s, Public Catalog Decision, Pricing Button Plan
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**To:** Argon (Gemini 3.8)  
**Date:** 5 November 2026, 1:20 PM ET  
**Reference:** `BATON_NET-801_PLAN_SOFT404-PUBLIC-CATALOG-PRICING_LAUNCH-PRIORITY_2026-11-05-0954.md` (renumbered from NET-800)  
**Review Order:** Argon (Score 95+ required) -> Grok Bot CoS 95+ -> SAG -> Eric typed YES.  

---

## Files in docs/, INBOX, and BATONS:
1. `PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING.md` (Architecture & Implementation Plan)
2. `DONE_BATON_NET-801_PLAN_SOFT404-PUBLIC-CATALOG-PRICING_2026-11-05-1315.md`

---

## Tasks for Argon:
1. Quote ONLY from real files with real line numbers (see NET-767 rule).
2. **Verify Soft-404 Analysis & Routing Fix:**
   - Verify `firebase.json` omissions (`/catalog`, `/catalog/**`).
   - Verify `main.dart:119-141` (`isKnownPath`) and title hardcoding in line 291.
   - Verify `WebRouteHelper` dynamic title and history sync proposal.
3. **Verify Public Catalog Proposals & Eric Gate:**
   - Confirm 3 options provided (Option A: `/catalog`, Option B: modal, Option C: copy alignment).
   - Confirm explicit gate: Founder Eric decides go/no-go; zero execution or public catalog deployment without Eric's typed YES.
4. **Verify Pricing Button Root Cause Analysis:**
   - Confirm verification of `AuthGate` session hijack (`widgets/auth_gate.dart:106-159`) where authenticated users visiting `/pricing` are forcibly redirected to `BaseLayout`.
   - Confirm `login_screen.dart:566, 603` `InkWell` + `Navigator.push` lacks browser history push.
5. **Verify Lower-Priority Items:**
   - `AI+ Community Verified` (`login_screen.dart:340, 468`).
   - PIN/Password reset wording (`login_screen.dart:692, 721`).
   - Jargon reduction (`login_screen.dart:415, 416`).
   - Footer accessibility and reading order.
6. **Confirm Standing Locks:**
   - PLAN ONLY. Zero code modifications. Zero deployments.
   - `origin/main` locked at `9f04550a`.
   - Stripe locked OFF.
   - Zero Firestore writes / zero seeding.

---

**Output File:** `INBOX\ARGON_REVIEW_PLAN_SOFT404-PUBLIC-CATALOG-PRICING.md` with technical score, any must-fixes, and verdict.  
**Mode:** REVIEW ONLY. Nothing executes. No deploys without Eric's typed YES.
