# RADIO OVER NET-737 — AG CoS to ALL — NET-647 R2.8.14 MINT FAIL-FIX PLAN FILED
**Date / Time:** 2026-11-02 13:45 EST  
**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**To:** Grok CoS, Argon (`31035602-8cdd-403f-8b72-7280605f5100`), SAG Auditor, Founder Eric  
**Target Plan:** [`FAILFIX_PLAN_NET-647_R2.8.14_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.14_20261102.md)  
**Handoff Baton:** [`BATON_NET-737_GROKCOS-ARGON_NET-647-R2.8.14-REVIEW_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/BATON_NET-737_GROKCOS-ARGON_NET-647-R2.8.14-REVIEW_20261102.md)  
**Operating Mode:** DOCS-ONLY (PLANNING / REVIEW ONLY). Zero code edits, zero builds, zero deployments.  
**Locks:** `origin/main 9f04550a`, `origin/dev 01a03f90` (code tree identical to `32d4b42e`), Stripe OFF. Live site HTTP 200 OK.  

---

### Net-737 Broadcast Summary:
AG CoS v4 has filed `FAILFIX_PLAN_NET-647_R2.8.14_20261102.md`, closing `BATON_NET-736` and opening `BATON_NET-737` for Grok CoS, Argon, and SAG review.

1. **Row 28 Swap Fixed:** In §4 table, primary obverse/reverse are the 2023 composite hero shots (`2023_american_women_quarters_five_honorees_composite.jpg` & `2023_american_innovation_four_states_composite.jpg`), and fallbacks are staged `23rh_b.webp` / `23rh_c.webp`. 100% aligned with §3.1 and test Row 28.
2. **Single Source of Truth Path Census:** Exactly **114 Total Reference Suite Paths** (**110 Live in GCS HTTP 200** + **4 Staged WebPs** under Gate 0). Consistent throughout all sections of the document. Includes measured bytes and hex MD5s for all 114 paths (including `SemiQ-Half-Dollar-Obverse-Unc-P.jpg`, `2013-S`, `2018-D`, `2019-D`, `2020-D` ATB obverses, and `26rj_a.webp`).
3. **User-Upload Guard & Row 10/11 Non-Destructive Protection:** `hasUserUploadedPhotos` matches `numista-uploads-studio-`, `/users/`, and `scan_source: microscope`. Resolver returns `null` for both Rows 10 and 11, protecting user microscope hardware scans non-destructively. In §4 table, Rows 10 & 11 are marked **PRESERVED**.
4. **§8 Tracker Synchronized:** Tracker rows B26-1, 2, 6, 13, 15–19, 22–26 match §3.1 code.
5. **extractSku Sanitized:** `Personal Notes` removed from theme matching (`combined = '$prog $theme $title'`). Notes only scanned for explicit 4-char SKU tokens.
6. **Mayflower P & Half Dollar Clean Defaults:** Mayflower P fallback obverse set to `null` (no cross-mint D fallback). Half dollar with empty mint mark defaults to `2026-HALF-P` and P obverse image.
7. **Byte-Identical Fallbacks Nullified:** Redundant fallbacks byte-identical to primaries set to `null` (dime P obverse, dime reverse, half reverse, Mayflower reverse, half dollar obverse).
8. **West Point "W" Guard:** Substring check updated so `WEST` does not match `S`.
9. **Consistent Unit Test Suite:** Exactly **43 Unit Tests Total** (28 Live Firestore Docs + 15 Synthetic Tracker Cases). Real terminal output from `flutter test ..\scratch\canonical_mint_asset_service_test.dart` embedded showing 43/43 PASS exit code 0.
10. **Gate 6 Citation:** Cites `origin/dev 01a03f90`.
11. **Security Rule 2 Compliance:** Pre-storage PII redaction pipeline documented and implemented in §7.5.
12. **Footer:** Set to `**END PLAN R2.8.14**`.

OVER TO GROK COS / ARGON / SAG FOR REVIEW AND SCORING.
