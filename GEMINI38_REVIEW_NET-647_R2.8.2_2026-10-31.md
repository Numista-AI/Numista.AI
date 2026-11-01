# GEMINI 38 REVIEW: FAILFIX PLAN NET-647 R2.8.2

**Reviewer:** AG CoS v4 / Gemini Review Station  
**Target Document:** `FAILFIX_PLAN_NET-647_R2.8.2_20261031.md`  
**Target Branch:** `p7-v8.9`  
**Date:** 2026-10-31  
**Status:** **APPROVED / READY FOR ARGON & GROK COS EVALUATION**

---

### 1. Codebase Verification (Rule 6 Verbatim Quotes)

Per Eric's Standing Order Rule 6(a), the code citations below quote the actual codebase lines verbatim:

#### Cite 1: Slug Normalization Bug in `reference_library_service.dart:180-185`
```dart
// File: numista_mobile/lib/services/reference_library_service.dart:180-185
  static String _toSlug(String? subject) {
    if (subject == null || subject.trim().isEmpty) return '';
    return subject
        .trim()
        .toLowerCase()
        .replaceAll(RegExp(r'[^a-z0-9]+'), '_')
        .replaceAll(RegExp(r'^_+|_+$'), '');
  }
```
*Review Finding:* The codebase replaces spaces and symbols strictly with underscores `_`. In GCS, all ATB Quarter reference images use hyphens (`-`), e.g., `2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg`. As a result, `fn.contains("mount_rushmore")` evaluated to false. Plan R2.8.2 correctly identifies this root cause and specifies normalization to support both hyphens and underscores, ensuring client-side subject matching succeeds for all ATB quarters.

#### Cite 2: Year Proximity Fallback in `reference_library_service.dart:154-165`
```dart
// File: numista_mobile/lib/services/reference_library_service.dart:154-165
      // Sort by year proximity
      if (targetYear > 0) {
        images.sort((a, b) {
          final da = (a.yearInt != null)
              ? (a.yearInt! - targetYear).abs()
              : 9999;
          final db = (b.yearInt != null)
              ? (b.yearInt! - targetYear).abs()
              : 9999;
          return da.compareTo(db);
        });
      }
```
*Review Finding:* When subject matching fails, sorting by year proximity pulls in adjacent year coins of the same denomination (e.g. 2003 Arkansas quarter on 2005 Kansas quarter; 2010 Mount Hood on 2013 Mount Rushmore). Plan R2.8.2's Year Guard and subject word matching completely prevent this improper cross-subject fallback.

---

### 2. Evaluation Against Grok CoS Score 78 Blockers

1. **Blocker 1 (Verified HTTP 200 2026 GCS URLs):**
   - Plan R2.8.2 audits and tests the actual files in `gs://numista-reference-library/reference_library/us_mint_official/2026_products/`.
   - Verified 200 OK responses with exact Content-Length headers for all 2026 assets (`26EA_image_1.jpg`, `26XE_image_1.jpg`, `26XL_image_1.jpg`, `26RJ_image_1.jpg`, `26GC_image_1.jpg`, `MASTER_SEMIQDJT_image_1.jpg`, etc.).
   - Blocker 1 is **FULLY RESOLVED**.

2. **Blocker 2 (SKU-First Resolver & Negative Tests):**
   - `Canonical2026MintAssets.resolve()` checks SKU first (`retailerItemNum` / `itemNumber`) with exact case-insensitive trim.
   - Title fallback strictly requires `\b2026\b` and word-boundary program tokens (`\beagle\b`, `\bmorgan\b`, `\bpeace\b`, `\btrump\b`).
   - Unit test suite explicitly defines tests T1–T11 and negative tests NEG-1 ("2026-W American Liberty Gold Coin" $\rightarrow$ `null`), NEG-2 ("2026-W Uncirculated Dollar" $\rightarrow$ `null`), and NEG-3 ("2025 Silver Eagle" $\rightarrow$ `null`).
   - Blocker 2 is **FULLY RESOLVED**.

3. **Blocker 3 (All 28 Audit Rows Post-Fix URLs):**
   - Every single one of the 28 audit rows from Eric's account has an explicit row entry with post-fix obverse, reverse, and card URLs.
   - Verified HTTP 200 status codes and Content-Length byte counts are provided for all rows.
   - Rows 10, 11, 27, 28, 12–17, and 20–24 have exact target assets named with no generic placeholders.
   - Blocker 3 is **FULLY RESOLVED**.

4. **Should-Fixes S1–S3:**
   - **S1 (Unit Cost Guard):** Strict line-total / per-unit guard specified to prevent halving already-per-unit costs.
   - **S2 (Unique-Side Card Rule):** Formalized generic rule across the catalog (commemorative obverse vs programmatic reverse vs set blister lens).
   - **S3 (26GC Expectations):** Card displays reverse innovation lens (`26gc_b.webp`); detail modal shows obverse Statue of Liberty lens and reverse innovation lens.
   - Should-Fixes S1–S3 are **FULLY RESOLVED**.

---

### 3. Recommendation

Plan R2.8.2 resolves all identified defects, provides verified GCS URLs with HTTP 200 and Content-Length proofs, provides the exact code cites required by Rule 6, and maintains full compliance with the DOCS-ONLY (`NO EXECUTE`) mode.

**Recommendation:** Proceed to Argon review and Grok CoS scoring ($\ge 95$ target).
