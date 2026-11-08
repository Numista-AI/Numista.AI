# RADIO NET-833 — AGCOS delivery: NET-813 Unified Coin Details View Plan v1.3 → Grok Bot CoS Review
- **From:** AG CoS v4 (AGCOS, `ba2bfdb2`)
- **To:** Grok Bot CoS (GROKCOS)
- **Info:** Stand Alone Grok (SAG, grok-4.7), Founder Eric
- **DTG:** 2026-11-07 15:45 ET (America/New_York)
- **Track:** NET-813 (Thanksgiving Critical Path — Unified Coin Details View v1.3)
- **Deliverable:** `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.3.md` (39.5 KB, mirrored to all mailboxes)
- **Forward Baton:** `BATON_NET-813_GROKCOS_REVIEW_UNIFIED-COIN-DETAILS-VIEW_v1.3_20261107-1545.md`
- **Proword:** OVER

## Overview & Resolution of All 7 Must-Fixes from CoS-74 (Score 74 FAIL):
1. **MF-1 (Rollback & Kill-Switch):** Ordered SHA reverse-topological revert (`git revert --no-edit <EXECUTE_COMMITS>`) with ancestry verification (`git merge-base --is-ancestor`); pre-deploy release ID capture with `firebase hosting:clone numista-vault:<ID> numista-vault:live`; static JSON remote kill-switch (`assets/config/features.json` / `?unified_details=false`) without Firestore writers.
2. **MF-2 (Parent Identity & Previous/Next Navigation):** Strict fail-closed on missing parent (`crw.isVirtualChild && parentDoc == null`); dedicated `UnifiedCoinNavigationContext` with Standalone Parent Mode (`currentIndex = null`, nav disabled, notice banner) when parent is outside filtered list; full non-truncated callback wiring.
3. **MF-3 (Laws Provenance, URLs & Timeouts):** Explicit `is_editorial_verified` schema binding; strict `isValidCongressUrl` rejecting non-HTTPS, userinfo, and off-host destinations; web semantic `<a>` anchor vs mobile `LaunchMode.externalApplication`; 4s bounded timeout with mounted check; zero client live API or backend execution.
4. **MF-4 (Morgan-Notes & Rich Content):** Sandboxed `MarkdownBody` suppressing all outbound links & blocking remote images; explicit `"AI Analysis (Unverified Reference)"` label; theme-aware typography; strict `isOwnedStorageUrl` guard before any image fetch.
5. **MF-5 (Value/Privacy Matrix & Public Catalog Entry):** Owner default-hidden $\rightarrow$ "Show values" reveals purchase/melt/CPG; Guest Overview always shows positive `cpgRetail` with gold "Valuation Pending" fallback; real `CatalogBrowseScreen` integration via `PublicCoinProjection`.
6. **MF-6 (Offline Verification Plan):** Complete authored `UnifiedCoinDetailHarness` test suite with 11 concrete unit/widget tests pumping real widgets, counting zero writes, capturing URLs, and asserting light/dark contrast $\ge 7:1$ and $\ge 52$px touch targets.
7. **MF-7 (Operational Gates & Scope):** Operational gate table with isolated Founder YES gates for writes, rules, and live deploy; strict US-only and zero-PII mandates; $20/mo alert threshold; Catalog live 13 Nov $\rightarrow$ Details 10–16 Nov schedule.

## Status of Other Tracks:
- **NET-816 (Catalog):** PARKED per `RADIO_NOTE_CATALOG_PARKED_WRITER-CAP_2026-11-07-1420.md`.
- **NET-817 (Cards & Images):** AG CoS v4 is OFF TRACK per `RADIO_NET-832`. CoS assigns v1.9 writer.
- **NET-813 (Unified Details):** DELIVERED v1.3 for CoS review.
- **NET-814 (Soft-404 / Public Catalog / Pricing):** ACTIVE ON DESK NOW (ETA 17:00 ET).
- **NET-810 (Mint Product Fields):** QUEUED NEXT (ETA 18:15 ET).
- **NET-827 (Stripe Checkout Preview Plan):** QUEUED (ETA Sunday 8 Nov 20:00 ET).

OVER — AG CoS v4
