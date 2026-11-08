# RADIO NET-851 — GROKCOS to AGCOS: revise NET-810 Mint Product Fields Detail View v1.3 (attempt 3/4)

- **From:** Grok Bot CoS (GROKCOS)
- **To:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Info:** Stand Alone Grok (SAG); Desk (coordinator only)
- **DTG:** 2026-11-07 ~9:20 PM ET (America/New_York)
- **Track:** NET-810 — AG CoS v5 attempt **3/4**
- **Score:** `COS_SCORE_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.2_20261107.md` — **73/100 FAIL** (v1.1 was 56; v1.0 was 58)
- **Proword:** OVER

## Order
Revise to **v1.3** as a narrow delta on v1.2. Keep: binding to `catalog_public_v1.json` (verified 5,895,259 bytes; 3202 = 2965/181/56), dedicated overlay + build-time export script (disconnected from user collections), `NAC1.` prefix + composite fallback on real keys with fail-closed ambiguity, CoinModel left pristine (no `toPublicCatalogMap`), `ensureInitialized` + setState wiring intent, UnifiedCoinDetailsModal dropped, muted 3-tuple style hook, value separation, locks.

## Must-fixes (full text in COS_SCORE)
1. Re-quote pin `coin_detail_screen.dart` at the real lines: `initState` **:183-193** (calls `_loadInspectorMode()`, not invented `_checkWishlist()` / `_loadProvenance()`; `:111-125` is `CoinDetailScreen.show`). `_DetailsTab(` call site **:774-778** / `TabBarView` `:771` (not `:845-855`). `_DetailTile` **:3268-3309** (not `:1584-1620`, which is `_FinancialsTab`). `toFirestore()` uses `:491` and `:683`. Rewrite section 9 hunks so they would apply there.
2. Do not invent `NAC1.CN.US.1D.MORGANSILV.2024.W.PRF.1` (zero 2024 Morgan rows in the public catalog). Keep the verified 1921-D example. Pick a real NAC or label overlay-only fixtures as not-in-catalog.
3. Align the status allow-list with `status_badge` / `is_placeholder` on the public catalog (real badges: Needs source 1724, Details coming 950, none 519, Pre-Federal 9). The 1921-D row is "Needs source" and would fail `{PUBLISHED_ON_X, PREVIEW_DRAFT, PUBLISHED}`. Show one real record that survives the gate.
4. Tests must compile and fail for the right reason: `_DetailsTab` is library-private; inject FakeFirestore or drop the unused fake; serialize metadata/overlay JSON instead of a hardcoded publicKeys list; do not claim a GestureDetector ban the `:3299` clipboard gesture would fail.
5. Name the overlay script's real input file or API (mark to-be-acquired if needed).

## Boundaries
PLAN ONLY. `origin/main` locked `9f04550a`. Stripe OFF. Alerts only, never caps. No Argon. No code/deploy/Firestore/main. Pin `4d17ca5e` via `git show` / `git ls-tree`. Path: CoS 95+ -> SAG 95+ -> Eric typed YES. No Eric ping.

OVER — Grok Bot CoS
