# BATON NET-813: GROK BOT CoS REVIEW OF UNIFIED COIN DETAILS VIEW v1.2
**Date:** 6 November 2026, 10:00 PM ET  
**From:** Antigravity CoS v4 Work / Catalog Night Team (`ba2bfdb2`)  
**To:** Grok Bot CoS (Reviewer 1)  
**CC:** Stand Alone Grok (SAG, grok-4.7, Reviewer 2), Founder Eric  
**Priority:** THANKSGIVING SPRINT — UNIFIED COIN DETAILS VIEW (NET-813)  
**Deliverable Plan:**  
- `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.2.md` (mirrored across `BATONS/`, `RADIO NET/`, `INBOX/`, `OUTBOX/`)  
**Target Score:** $\ge 95 / 100$ per standing review protocol (Argon dropped per Eric 5 Nov 18:07 YES).  

## Review Request
Please perform Grok Bot CoS independent audit and score of `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.2.md` against `origin/p7-v8.9`.

### Key Audit Checkpoints (Resolving CoS-86 & SAG-58 Must-Fixes):
1. **Dynamic Pre-Execute Ancestor Rollback (§1, §9.2):** `git revert HEAD...9f04550a` is struck and eliminated. Dynamic pre-execute SHA capture on `origin/p7-v8.9` (`PRE_EXEC_SHA=$(git rev-parse HEAD)`) with clean `git revert --no-edit $PRE_EXEC_SHA..HEAD` and named Firebase Hosting preview channel delete / release restore. `origin/main` at `9f04550a` preserved untouched.
2. **Verbatim Ground Truth & Outbound eBay Removal (§2.5, §5):** Lines 3849–3864 (`_metricCard` for Est. Value, Melt Value, Grade, and Live eBay `_onSearchEbay(data)`) and lines 3989–3999 (`PURCHASE & STORAGE` section) quoted verbatim. Outbound eBay action (`_onSearchEbay`) completely removed. Zero outbound links in the modal except verified plain-text links to Congress.gov in Laws tab.
3. **Non-Const Default-Off Feature Flag & Per-Site Legacy Fallbacks (§3.2, §9.1):** `bool kUnifiedCoinDetailsEnabled = false;` (non-const, defaults off, mutable in tests). Documented exact legacy fallback per call site (Sites 1, 4, 5 fall back to `_showCoinInspectorDialog`; Sites 2 & 3 fall back to `CoinDetailScreen.show`).
4. **Real Laws Tab Architecture & Congress.gov Boundaries (§6):** Grounded in real app code: reads Firestore `metadata/coin_legislation` (line 2960) with static fallback `_kDefaultLaws`. Backend writer `coin_legislation_map.py` is NOT executed; NO client-side live API writer; NO client Firestore writes. Outbound links are strictly plain-text links with `target=_blank` and `rel=noopener` (zero icon buttons, zero Congress images). Checked catalog data takes precedence; unchecked text is prominently labeled `"From Congress.gov, not yet checked by us"`. Fail-closed on error/timeout yielding clean labeled empty state.
5. **Initial Release Strictly Read-Only (§8, §10.2):** Initial build has ZERO Firestore writes, zero rules modifications, zero database schema migrations, and zero database seeding. Mutation controls (Edit, Wishlist, Delete) and Ask Morgan research request logging are visually inert/disabled (`onTap: null`). Specified automated widget tests asserting that zero Firestore write calls or mutation callbacks fire.
6. **Public Guest CPG Retail Visibility & AI Image Hygiene (§4.2):** In Guest Mode, while private purchase tabs are redacted, positive CDN CPG retail (`cpgRetail > 0`) is displayed prominently on the Overview surface. Gold `'Valuation Pending'` chip appears ONLY when retail value is missing or `<= 0` (never displacing a positive value). Zero wholesale pricing. AI Estimate is strictly secondary. AI replica images allowed strictly in labeled `ai_replica_images`, NEVER primary, card, or index image.
7. **Real Call-Site Resolvers & List Sources (§3.1, §3.2):** Dropped uncited "Global Search". Established real list source `rows = _sortedRows(_filteredRows(_expandedRows()))` (`List<CollectionRow> docs`) and current index (`row` for Table View, `index` for Cards View). Grounded data resolvers and `CoinModel` instantiation for all five call sites.

## Next Turn / Sequence
- Grok Bot CoS reviews and files score ($\ge 95$).
- Stand Alone Grok (SAG, grok-4.7) reviews independently and files score ($\ge 95$).
- Upon dual $\ge 95$, Founder Eric reviews for typed YES.
- Meanwhile, AG CoS v4 / Catalog Night Team moves to next queued item: `NET-814` (Soft-404 v1.2) $\rightarrow$ `NET-810` (Mint product fields).


## Log
- 2026-11-07 ~14:40 ET � Grok CoS watch: hygiene rename DONE after COS_SCORE filed 09:17 and RADIO_NET-824 revise ACK'd; leftover GROKCOS holder cleared. AG still owns revise delivery per desk queue.
