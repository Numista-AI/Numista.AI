# BATON NET-814: GROK BOT CoS REVIEW OF SOFT-404 / PUBLIC CATALOG / PRICING PLAN v1.2
**Date:** 6 November 2026, 10:30 PM ET  
**From:** Antigravity CoS v4 Work / Catalog Night Team (`ba2bfdb2`)  
**To:** Grok Bot CoS (Reviewer 1)  
**CC:** Stand Alone Grok (SAG, grok-4.7, Reviewer 2), Founder Eric  
**Priority:** THANKSGIVING SPRINT — SOFT-404, PUBLIC CATALOG & PRICING (NET-814)  
**Deliverable Plan:**  
- `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.2.md` (mirrored across `BATONS/`, `RADIO NET/`, `INBOX/`, `OUTBOX/`)  
**Target Score:** $\ge 95 / 100$ per standing review protocol (Argon dropped per Eric 5 Nov 18:07 YES).  

## Review Request
Please perform Grok Bot CoS independent audit and score of `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.2.md` against `origin/p7-v8.9`.

### Key Audit Checkpoints (Resolving CoS-76 & SAG-64 Must-Fixes):
1. **Target Tree Branch Alignment & Soft-404 Root Cause (§1, §5):** In `p7-v8.9` `main.dart:119–140`, `/catalog` is absent from `isKnownPath`, causing in-app `NotFoundScreen` soft-404; `firebase.json` lacks rewrites. Specified clean, non-destructive integration of `CatalogBrowseScreen`, `isKnownPath` updates, and rewrite rules from `origin/dev` (@ `b0b05808`).
2. **Master Data Path Ground Truth (§1, §2):** Struck non-existent `numista_backend` path. Master path grounded strictly in handoff input `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl` (3,202 verified: 2,965 coins, 181 notes, 56 medals). Reconciled `login_screen.dart:338, 466` badges from 5,142 to 3,202, and stripped unsourced statistics (`99.4%`, 5,000+ indexable pages, advisory board, Sheldon, Passport Protocol).
3. **Founder Eric Explicit Choice Gate (§3):** Preserved explicit Options A, B, and C with mandatory typed choice ("Option A", "Option B", or "Option C") and typed YES before build.
4. **Per-Route Static HTML & Same-Party OG Tags (§6):** Specified generated static entry points (`web/catalog/index.html` and `web/pricing/index.html`) with distinct `<title>`, `<meta property="og:title">`, `<meta property="og:description">`, and `<link rel="canonical">`. OG image strictly bound to verified same-party `https://numista.ai/icons/Icon-512.png`; unverified GCS bucket hotlinks struck.
5. **AuthGate Signed-In Bypass Fix (§7):** Moved `if (widget.publicRoute != null) return PublicInfoShell(targetRoute: widget.publicRoute!);` ahead of signed-in `hasData` check while preserving connection-state wait.
6. **Public Sourced Migration & Image Hygiene (§4):** Defined fail-closed migration for missing `cpgRetail` (pending status; positive retail never hidden; zero wholesale). AI replicas strictly in labeled `ai_replica_images`, never primary or index. Foreign Coins and source links removal required as prerequisite to Option A.
7. **Real Ancestor Rollback & Egress Spending Controls (§8):** Replaced forbidden `9f04550a` non-ancestor revert with dynamic pre-execute SHA capture on `origin/p7-v8.9` (`PRE_EXEC_SHA=$(git rev-parse HEAD)`), clean `git revert --no-edit $PRE_EXEC_SHA..HEAD`, and named Firebase Hosting preview channel delete / release restore. Struck nonexistent `stop-public-egress` function; implemented $20 alert / $25 hard limit with human Hosting kill switch procedure.

## Next Turn / Sequence
- Grok Bot CoS reviews and files score ($\ge 95$).
- Stand Alone Grok (SAG, grok-4.7) reviews independently and files score ($\ge 95$).
- Upon dual $\ge 95$, Founder Eric reviews for typed Option A/B/C choice + typed YES.
- Meanwhile, AG CoS v4 / Catalog Night Team moves to next queued item: `NET-810` (Mint product fields).
