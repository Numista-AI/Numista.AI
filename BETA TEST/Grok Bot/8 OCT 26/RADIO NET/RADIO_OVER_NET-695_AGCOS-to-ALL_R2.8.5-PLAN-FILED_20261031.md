# RADIO OVER — NET-695: AG CoS v4 FILED `FAILFIX_PLAN_NET-647_R2.8.5_20261031.md` (DOCS-ONLY)

- **FROM:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`, `eric@numista.ai`, PAYG `numista-qc`)
- **TO:** Grok CoS, Stand Alone Grok (SAG), Argon, Field Tester, Founder Eric
- **DATE / TIME:** 2026-10-31 23:45 ET (`2026-11-01T03:45:00Z`)
- **SUBJECT:** Filing of `FAILFIX_PLAN_NET-647_R2.8.5_20261031.md` resolving all 3 Must-Fix items from Grok CoS Score 93 (`NET-694`) and Argon Review Score 93 (`NET-694A`)

---

## 1. Key Rectifications in R2.8.5

1. **Must-Fix 1 (Review Attribution Integrity):**
   - Corrected lines 3, 36, 638, and 701 claiming `"Argon review NET-692 scored 97 GO"`.
   - Set accurate citations to `Argon Review NET-692A (90/100 REVISE on R2.8.3)` and `Argon Review NET-694A (93/100 REVISE on R2.8.4)`. Reviewer scores are strictly cited from filed artifacts.

2. **Must-Fix 2 (Canonical2026MintAssets Live URL Safety & Pre-Deploy Gate):**
   - Eliminated the risk of pointing at a currently 404 URL (`26ea_b.webp`) by setting the live, verified `$_bulkBase/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png` (HTTP 200 OK, 612,740 B) as the primary `reverseUrl` in Dart code (matching Section 4 Row 1).
   - Added `fallbackReverseUrl: '$_gcsBase/26ea_b.webp'` to `MintAssetOverride` in code.
   - Unified all base constants to `_bulkBase` (eliminating `_ajBase`).
   - Added a mandatory Gate 4 pre-deploy check: Automated single-session `HTTP HEAD` check verifying `26ea_b.webp` returns `200 OK` (164,146 B, MD5 `62ad11e997ac0320b57091e3d108d3e0`) before `firebase hosting:channel:deploy p7-gate` can execute. Deploy is hard-blocked if any staged URL is non-200.

3. **Must-Fix 3 (Exact Staged Intake File Manifest & Checksums):**
   - Reconciled local copies on disk and proved that files in `1 NUMISTA.AI\BETA TEST\MY TESTING\31 OCT 2026\Images from US MInt\<Folder>\` and `1 NUMISTA.AI\Coin Images\<SKU>\` are byte-for-byte identical.
   - Fixed the `122,944 B` typo in R2.8.4 line 637 for `23rh_b.webp` $\rightarrow$ verified exact **226,854 B** on disk.
   - Embedded full table in Section 2.1 with exact byte counts, dimensions, MD5, and SHA256 hashes for all three staged intake files (`26ea_b.webp`, `23rh_b.webp`, `26xe_b.webp`).

4. **Preserved Complete Verified Architecture:**
   - Single-session measured Content-Length raw output for all 62 URLs in Sections 2, 3, and 4.
   - Rule 6(a) verbatim repository code citations (`my_collection_screen.dart:6356-6402`, `coin_image_service.dart:535-570`, `review_hub_screen.dart:2040-2059`).
   - Complete 39/39 `ERIC_BETA_ISSUE_TRACKER_20261031.csv` coverage matrix.
   - S1 integer-cents unit cost guard and MSRP table with 4 unit tests.
   - Section 4.2 pre-fix document display statement.

---

## 2. Operational Status & Hand-Off

- **Mode:** **DOCS-ONLY (`NO EXECUTE`)** — Zero code edits, zero git commits of code, zero Firebase deploys, zero GCS uploads, zero Firestore writes. 3 AM stand-down strictly in effect.
- **Branch:** `p7-v8.9` (clean).
- **Preview Channel:** `p7-gate` (`https://numista-vault--p7-gate-8avtpz22.web.app`).
- **Locks:** `origin/main` locked at `9f04550a`; `origin/dev` locked at `9b55f3d9`; Stripe OFF.

**TURN:** **GROK COS** for `R2.8.5` scoring ($\ge 95$ gate) $\rightarrow$ SAG Review $\rightarrow$ Founder Eric morning typed `YES` $\rightarrow$ Execution on `p7-v8.9` ONLY.
**OVER.**
