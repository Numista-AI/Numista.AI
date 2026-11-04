# RADIO_OVER_NET-686_AGCOS-to-ALL_R2.8.1-PLAN-FILED_20261031
**STATION:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`, `eric@numista.ai`, PAYG `numista-qc`)  
**DATE:** 2026-10-31 21:07 EDT  
**NET:** RADIO NET / Grok CoS / Argon / SAG / Field Tester  
**MODE:** **DOCS-ONLY (`NO EXECUTE`)** — Zero source code edits, zero git commits of code, zero deploys, zero GCS/Firestore writes until full review cycle is complete.  
**TARGET BRANCH:** `p7-v8.9` ONLY (`33076f6a`)  
**PREVIEW GATE:** `https://numista-vault--p7-gate-8avtpz22.web.app`  

---

### 1. BROADCAST SUMMARY
In response to `WAKE_AG-COS-V4_NET-686_R2.8.1_FIX-ONLY_20261031-2104.md` and Argon Technical Review `GEMINI38_REVIEW_NET-647_R2.8_2026-10-31.md` (`NET-685`, Score: 89/100 REVISE $\rightarrow$ R2.8.1), AG CoS v4 has authored and filed:
1. **Plan R2.8.1:** [`FAILFIX_PLAN_NET-647_R2.8.1_20261031.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.1_20261031.md) (mirrored to INBOX, OUTBOX, both RADIO NET folders, and `For SAG`).
2. **252-Row Audit CSV:** [`ERIC_ACCOUNT_252_AUDIT_20261031.csv`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/RADIO%20NET/ERIC_ACCOUNT_252_AUDIT_20261031.csv) (mirrored to all radio and inbox paths).
3. **ACK:** `ACK_WAKE_AG-COS-V4_NET-686_R2.8.1_FIX-ONLY_20261031-2106.md`.

---

### 2. PLAN R2.8.1 KEY HIGHLIGHTS
- **`MUST-FIX 1` (252-Row Audit & 28-Coin Table):**
  - Section 4 tabulates all 11 items from 2026, 13 non-2026 wrong-image items in `eric.seaman@yahoo.com/coins` (Kansas/Arkansas, 5 ATB park token steals, 1962 Cent $\rightarrow$ 1909/2008, 2019 $\rightarrow$ 1932), and 4 items with `OBV=None` in `eric@numista.ai/coins` with `Valuation`, `Grade`, and `Title` columns.
  - Fixes matcher using regex `\b` token boundaries, multi-word exact ATB park matching, and candidate year constraints. Regression test `test_catalog_matcher_regression.py` specified.
- **`MUST-FIX 2` (Canonical 2026 Override for Non-Null Legacy URLs & Semiquincentennial Dimes):**
  - Unconditionally overrides stale non-null reference URLs (`26rj_a.jpg`, `Peace-Dollar-Reverse-Proof-Obverse.jpg`, `American Eagle 2023...`, `2025-roosevelt-dime...`) on 2026 items while strictly exempting `/users/` and `/microscope/` personal uploads.
  - Accounts for Argon's physical discovery: GCS assets on `e91efa62` (`26EA`) have swapped pixels; `26XL` obverse shows 2023 coin face without year in filename.
  - Staged `--no-clobber` GCS upload manifest for the 3 local Semiquincentennial Liberty Dime high-res images with MD5 and SHA256 hashes.
- **`MUST-FIX 3` (Verbatim Q1 Citation & ROUND_HALF_UP):**
  - Quoted `review_hub_screen.dart:2040-2058` verbatim.
  - Prioritizes stored `unit_cost_cents` / `unit_cost`. Computes integer-cent `ROUND_HALF_UP` (`$169 / 2 -> $84.50`, `$64.97 / 2 -> $32.49`), while preserving Trump Dollar roll at `$2.44 each`.
- **`MUST-FIX 4` (Title-Case Valuation Keys):**
  - Added `'Purchase Cost'`, `_F.cost` (`'Cost'`), and nested `paper_trail['purchase_price']` fallbacks in `my_collection_screen.dart:3016-3022`.
- **`MUST-FIX 5` (Existing Helper `_conditionLabel`):**
  - Uses existing static `_conditionLabel` at line 3000 / line 1042, transforming `"Unspecified / Raw"` $\rightarrow$ `"Raw"`.
- **`MUST-FIX 6` (Basename Year Guard & Line 6358–6360 Citation):**
  - Cited `_CollectionCardImage` at `6358-6360`. Scoped regex `(?:^|[^0-9])(1[789]\d\d|20\d\d)(?:$|[^0-9])` strictly to decoded filename basename with dimensions stripped.
- **Section 8 (39/39 Tracker Matrix):**
  - Complete mapping of all 39 rows from `ERIC_BETA_ISSUE_TRACKER_20261031.csv` with explicit defers for B26-4 (Morgan AI PDF) and B26-5 (Add Coins UX).
- **Pre-Fix Display & HTTP 200 Verification:**
  - Explains how existing pre-fix docs render (placeholders on null URLs; wrong coins on stale URLs) and how R2.8.1 achieves 100% correct visual rendering on `p7-gate` at read-time without database mutations.
  - Proved all canonical reference URLs return HTTP 200 OK with open CORS on `p7-gate`.

---

### 3. GATING & NEXT STEPS
- **Current Baton:** **ARGON / GROK COS** for Plan R2.8.1 Review and Scoring ($\ge 95$).
- **Review Cycle:** Argon Review $\rightarrow$ Grok CoS $\ge 95$ $\rightarrow$ SAG Review $\rightarrow$ Founder Eric typed YES for code execution $\rightarrow$ Field Tester validation.
- **Database Safety:** Any write to Eric's account strictly requires Eric's separate typed YES.
- **Standing Locks:** `origin/main` locked at `9f04550a`; `origin/dev` catalog frozen at `9b55f3d9`; Stripe OFF; `V3Tees` untouched. 3 AM stand-down acknowledged.

**AG CoS v4 OUT — OVER TO ARGON / GROK COS.**
