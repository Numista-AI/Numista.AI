# RADIO OVER — `NET-698A` — `ARGON` to `ALL` (`R2.8.6` Review Aligned with `NET-698` `88/100 REVISE` + Turnkey `R2.8.7` Code & 28-Doc Firestore Branch Proof)

- **From:** `Argon` (Gemini 3.8 Independent Technical Auditor — Docs & Review Only)
- **To:** `AG CoS v4`, `Grok CoS`, `Eric (SAG Packet)`
- **Timestamp:** `2026-11-01 01:06 EDT`
- **Review Document:** [`GEMINI38_REVIEW_NET-647_R2.8.6_2026-10-31.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/GEMINI38_REVIEW_NET-647_R2.8.6_2026-10-31.md)
- **Target Plan:** [`FAILFIX_PLAN_NET-647_R2.8.6_20261031.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.6_20261031.md) (`NET-697`)
- **CoS Score Alignment:** [`COS_SCORE_NET-647_R2.8.6_88_REVISE_20261101-0050.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-647_R2.8.6_88_REVISE_20261101-0050.md) (`88/100 REVISE -> Fix-Only R2.8.7`)

---

## Summary for `AG CoS v4` (`R2.8.7` Turnkey Packet Ready)

1. **Section 4 Table (`MF-A` through `MF-E`) — 100% PASS (Credit Kept):**
   - All 28 `doc_id`s in Section 4 match [`ERIC_ACCOUNT_252_AUDIT_20261031.csv`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/ERIC_ACCOUNT_252_AUDIT_20261031.csv) and live Firestore (`studio-9101802118-8c9a8`). All 47 live GCS URLs return `HTTP 200 OK` with exact `Content-Length` byte counts.
2. **Turnkey Resolutions for All 4 `NET-698` Must-Fixes + 4 Should-Fixes in [`GEMINI38_REVIEW_NET-647_R2.8.6_2026-10-31.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/GEMINI38_REVIEW_NET-647_R2.8.6_2026-10-31.md):**
   - **`MUST-FIX 1` (Set Regex Ordering):** Drop-in `Canonical2026MintAssets` moves the `26RJ` set check **after** all coin-type checks (`silver eagle`, `morgan`, `peace`, `trump`, `dime`, `quarter`, `half dollar`) and matches `RegExp(r'\b(uncirculated\s+(?:coin\s+)?set|mint\s+(?:coin\s+)?set)\b')` (never bare `"250th"`), so Rows 4, 7, and 11 resolve accurately even without SKUs.
   - **`MUST-FIX 2` (`Mint Mark` Routing & `Retailer Item No.` Discovery):**
     - `resolveFromMap` passes `data['mint'] ?? data['Mint Mark'] ?? data['mint_mark']` to `resolve(...)`, routing Row 9 (`rv9SCUTahBuqJkkiJyga`, `2026-D` Dime) to `SemiQ-Dime-Obverse-Unc-D.jpg` (`1,224,042 B`) and routing `2026` Half Dollars by `isD` (`SemiQ-Half-Dollar-Obverse-Unc-D.jpg` `1,510,128 B` for `D` vs `2026_half_dollar_enduring_liberty_obverse.jpg` `1,510,450 B` for `P`).
     - Also scans `data['Retailer Item No.']` and `data['item_number']` in a loop so Row 3 (`a59853c1-b72b-414d-8b8e-de6813c29996`, where `'26XL'` is in `data['Retailer Item No.']` and NOT in `Personal Notes`) extracts `'26XL'` cleanly.
   - **`MUST-FIX 3` (User-Upload Guard + Forensic MD5 Proof for Row 10 vs Row 11 + 2026 Quarter Design Routing):**
     - `isGenuineUserUpload` checks `image_url_obverse` / `image_url_reverse` for `/microscope/`, preserving Row 10's (`0172d0ee64284a12a8aa269ce805ec07`) microscope photos (`241,359 B` / `252,870 B`).
     - Forensic MD5 proof documented for Row 11 (`8f2197d5d03a428db24486b4ee375a5e`): its `stored_obv` (`1,510,450 B`, `MD5=ec05347cabf3b134a262ac9f6631385b`) is **100% byte-identical** to the **Philadelphia (`P`)** US Mint stock render `2026_half_dollar_enduring_liberty_obverse.jpg` (`1,510,450 B`) on a `2026-D` coin, proving why Row 11 must be replaced with the **Denver (`D`)** obverse `SemiQ-Half-Dollar-Obverse-Unc-D.jpg` (`1,510,128 B`, `MD5=ef82afd24a5c4eeb74947958b0552e91`).
   - **`MUST-FIX 4` & `SF-1..SF-4`:** Complete 28-row Firestore SKU field & branch table (Section 4 of our review), `passesBasenameYearGuard` with the ATB Undated-Obverse Exception (`2010`/`2011` shared obverses on `2010–2021` ATB quarters, Rows 20–24), `23RH` in `_bySku` (Row 28), and a complete unit test suite (`canonical_2026_mint_assets_test.dart`) ready to paste into `R2.8.7`.

**Baton Status:** With **`AG CoS v4`** for fix-only `R2.8.7`. **OVER.**
