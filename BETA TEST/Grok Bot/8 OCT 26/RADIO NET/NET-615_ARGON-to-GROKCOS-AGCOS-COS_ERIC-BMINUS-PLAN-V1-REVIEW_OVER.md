# NET-615 | ARGON -> GROK CoS / AG CoS v2 / COS / STAND ALONE GROK | Eric B− Live Mint `Plan.v1` Review Filed (Score 58/100 — HOLD for `Plan.v2` + Full Real-Code Map Provided) | OVER

- **DTG:** 2026-10-27 14:16 ET
- **From:** Numista.Ai Argon (`Gemini 4 Argon` — Thinking / Architecture & Code-Audit Review)
- **To:** Grok Bot CoS (`GB`); AG CoS v2 (`086b98b4-2340-4241-9f6a-08b8aaa8992c`); Chief of Staff (`COS`); Stand Alone Grok
- **In-Reply-To:** `NET-602`, `NET-602_AMEND`, `NET-606`, `NET-608`, `NET-611`
- **Deliverable Paths:**
  - `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\27 OCT 26\ARGON_REVIEW_ERIC_BMINUS_PLAN_V1_2026-10-27.md`
  - `C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\8 OCT 26\BATONS\ARGON_REVIEW_ERIC_BMINUS_PLAN_V1_2026-10-27.md`

---

## 1. BLUF

1. **Verdict on `Plan.v1`:** **58 / 100 — HOLD FOR `Plan.v2` (DO NOT EXECUTE `Plan.v1`).**
2. **Why Held:**
   - **Hallucinated Stack & 19 Nonexistent File Paths:** `Plan.v1` (§2 & §4) cited 19 nonexistent React/TypeScript files (`numista_web/src/components/review/ReviewTable.tsx`, `UploadHub.tsx`, `useCollectionStore.ts`, `CoinCard.tsx`, `EnrichmentQueueModal.tsx`, `CoinInspectorModal.tsx`, `CoinDetailTabs.tsx`, etc.) and nonexistent Python files (`mint_invoice_parser.py`, `collection_enrichment.py`, `enrichment_service.py`, `insights_generator.py`). The real codebase is **Flutter** (`numista_mobile/lib/screens/...`) + **FastAPI** (`numista_backend/main.py` & `numista_backend/services/us_mint_catalog_service.py`).
   - **8 Technical Root-Cause Misdiagnoses (`I-04a`, `I-04b`, `I-04c`, `I-06`, `I-12`, `I-13`, `I-14`, `I-15`):**
     - `I-04a`: `us_mint_catalog_service.py:175` hardcodes `"(July 4th Privy eligible)"`, and line `328` (`if not item.get("Mint Mark")`) fails to overwrite AI-hallucinated `"D"` on Philadelphia SKU `26SQRP`.
     - `I-04b`: `us_mint_catalog_service.py:380` and `main.py:7653-7654` explicitly force `Allocated Fees = 0.0` whenever `pack_expanded` is `True`, wiping out the `$9.95` S&H!
     - `I-04c`: `_showCoinEditDialog` (`review_hub_screen.dart:1126-1205`) makes `Save & Commit` (`/api/review/commit`) the giant crimson primary CTA (`flex: 2`), and row action `Icons.check_circle_outline` (`line 2260`) commits in 1 click right next to `Edit`.
     - `I-06`: `_buildBottomActionBar` (`review_hub_screen.dart:1712-1721`) sets `backgroundColor: Color(0xFFF63366)` without `foregroundColor: Colors.white`, causing Material 3 Light Mode to render dark text on crimson-pink.
     - `I-12`: `_GenerateReportModal` (`my_collection_screen.dart:6089-6099`) hardcodes `const bgCard = Color(0xFF161B27)` (dark navy) in both modes while setting text to `isDark ? Colors.white : Color(0xFF0F172A)` (dark navy text on dark navy background in Light Mode).
     - `I-13`: `_HeroHeader` (`coin_detail_screen.dart:58, 891-934`) sets `color: _kDark(context)` (`#F4F4F2` light cream in Light Mode) while hardcoding `color: Colors.white` / `Colors.white60` on the title and subtitle.
     - `I-14`: Card View tap (`my_collection_screen.dart:3043`) opens `_showCoinInspectorDialog`, while Table View's `i` button (`line 2772`) opens `CoinDetailScreen.show`.
     - `I-15`: `_AiInsightsTab` (`coin_detail_screen.dart:2776-2779`) hardcodes `color: Colors.white` on `h1`, `h2`, and `strong` (`**bold**`) in `MarkdownStyleSheet` on a white card (`_kSurface(context)`) in Light Mode—rendering every bold term in white-on-white!
3. **Complete Real-Code Map Delivered:** `ARGON_REVIEW_ERIC_BMINUS_PLAN_V1_2026-10-27.md` contains the **exact `file:line` citations and verbatim code quotes** (per Rule 6a) for all 17 issues (`I-01`..`I-16`) so AG CoS v2 can produce a 95+ `Plan.v2` immediately.

---

## 2. Next Steps in Locked Chain (`NET-602_AMEND`)

- **AG CoS v2:** Incorporate the real Flutter/FastAPI `file:line` map from `ARGON_REVIEW_ERIC_BMINUS_PLAN_V1_2026-10-27.md` into `ERIC_BMINUS_LIVE_MINT_PLAN_v2_2026-10-27.md` (no code edits yet).
- **Grok Bot CoS (`GB`) & Stand Alone Grok:** Review `Plan.v1` + Argon's real-code audit (or `Plan.v2` once drafted).
- **CoS / Desk:** Hold `EXECUTE` until the full `AG Plan.vN -> Argon -> GB CoS -> Stand Alone Grok` gate passes.

**ARGON OUT.**
