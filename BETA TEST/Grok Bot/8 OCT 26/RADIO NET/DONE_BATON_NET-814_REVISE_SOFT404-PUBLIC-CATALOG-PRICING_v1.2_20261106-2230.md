# DONE BATON NET-814: REVISE SOFT-404 / PUBLIC CATALOG / PRICING PLAN v1.2 (CoS 76 / SAG 64 FAILFIX)
**Date:** 6 November 2026, 10:30 PM ET  
**From:** Antigravity CoS v4 Work / Catalog Night Team (`ba2bfdb2`)  
**To:** Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**Status:** COMPLETED & DELIVERED (PLAN ONLY)  
**Deliverable Document:**  
- `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.2.md`  

## 1. Summary of Completed Actions
1. **Resolved All CoS-76 / SAG-64 Must-Fixes:**
   - **Target Tree Branch Alignment & Soft-404 Elimination (§1, §5):** Grounded soft-404 root cause in target tree `p7-v8.9` `main.dart:119–140` where `/catalog` is absent from `isKnownPath` (rendering `NotFoundScreen`), and `firebase.json` lacks rewrites. Specified clean, non-destructive integration of `CatalogBrowseScreen`, `isKnownPath` updates, and rewrite rules from `origin/dev` (@ `b0b05808`).
   - **Correct Master Data Sourcing (§1, §2):** Struck non-existent `numista_backend` path. Corrected master path strictly to handoff input `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl` with verified 3,202 census (2,965 coins, 181 notes, 56 medals). Reconciled marketing badges (`login_screen.dart:338, 466`) from 5,142 to 3,202, and removed unsourced statistics (`99.4%`, 5,000+ indexable pages, advisory board, Sheldon, Passport Protocol).
   - **Options A, B, and C Explicit Gate (§3):** Articulated Options A (Full Public Catalog), B (Homepage Modal), and C (Members Only). Maintained mandatory Founder Eric typed choice ("Option A", "Option B", or "Option C") and typed YES before any build.
   - **Per-Route Static HTML & Verified OG Tags (§6):** Specified generated static entry points (`web/catalog/index.html` and `web/pricing/index.html`) with distinct `<title>`, `<meta property="og:title">`, `<meta property="og:description">`, and `<link rel="canonical">`. Sourced OG image strictly from verified same-party asset `https://numista.ai/icons/Icon-512.png` with local fallback. Struck unverified bucket hotlinks.
   - **AuthGate Signed-In Bypass Fix (§7):** Identified that signed-out sessions already wait on auth state and honor `publicRoute`, but signed-in sessions take `BaseLayout`/`WelcomeScreen` before checking `publicRoute`. Moved `if (widget.publicRoute != null) return PublicInfoShell(targetRoute: widget.publicRoute!);` ahead of the signed-in branch.
   - **Public Sourced Migration & Image Hygiene (§4):** Defined fail-closed migration from `catalog_public_v1.json` for missing `cpgRetail` (defaults to pending; positive retail never hidden; zero wholesale). AI replicas permitted strictly in labeled `ai_replica_images`, never primary or index. Foreign Coins and source links removal required as prerequisite to Option A.
   - **Real Ancestor Rollback & Egress Spending Controls (§8):** Permanently struck forbidden `9f04550a` non-ancestor revert. Pinned dynamic pre-execute SHA capture on `origin/p7-v8.9` (`PRE_EXEC_SHA=$(git rev-parse HEAD)`) with clean `git revert --no-edit $PRE_EXEC_SHA..HEAD` and named Firebase Hosting preview channel delete / release restore. Struck nonexistent `stop-public-egress` function; implemented $20 alert / $25 hard limit with human Hosting kill switch procedure.
2. **Forward Review Baton Filed:**
   - Filed `BATON_NET-814_GROKCOS_REVIEW_SOFT404-PUBLIC-CATALOG-PRICING_v1.2_20261106-2230.md`.
   - Passed turn to Grok Bot CoS for independent review scoring ($\ge 95$).
