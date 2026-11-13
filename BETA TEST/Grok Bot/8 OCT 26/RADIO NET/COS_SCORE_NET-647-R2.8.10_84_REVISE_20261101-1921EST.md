# COS_SCORE — NET-647 R2.8.10 Mint FAIL-FIX — 84/100 REVISE
Scorer: GB CoS | Filed 2026-11-01 7:21 PM EST | Plan: RADIO NET\FAILFIX_PLAN_NET-647_R2.8.10_20261101.md (1442 lines) | Baton reviewed: NET-728
Checked against: origin/p7-v8.9 d919bcf9 (cited branch) and origin/dev 32d4b42e. Pass bar 95. Docs only; nothing committed/deployed/contacted.

## Verified PASS
- GCS: 119 unique URLs HEAD-tested. 116 = 200. 404s: bare prefix `.../reference_library` (prose), `2023_products/23rh_b.webp`, `23rh_c.webp` (disclosed STAGED Gate 0).
- Section 4.1.3: all 95 live rows match HEAD Content-Length + x-goog-hash MD5 AND the paged bucket listing (7260 objects) exactly.
- Field case vs live dump (28 docs): `Year` in 28/28, `year` in 0; code reads `data['year'] ?? data['Year']` — OK.
- Test doc IDs/accounts: all 28 match ERIC_28_ROWS_FIRESTORE_SKU_DUMP. No invented doc IDs.
- Section 7 citations: 7.1, 7.2, 7.4, 7.5 match p7-v8.9 verbatim (they do NOT match dev 32d4b42e — plan cites p7-v8.9, acceptable). 7.3 range is one line short (closing `}` is line 571).
- `dart analyze` on proposed resolver: no issues.
- Resolver fed the FULL live Firestore docs: all 28 rows resolve as the tests expect.

## MUST-FIX (blocking)
1. **Unit tests 41/42, not 42/42.** Row 03 (`a59853c1…`, 26XL) fails: `Expected: not null, Actual: <null>`. Cause: the test fixture omits `Retailer Item No.` (`26XL`) that the live doc has, so the "real Firestore field map" claim is false for Row 03. Fix: paste the full live field map (or at least `Retailer Item No.`) into the Row 03 fixture; re-run and paste the real `dart test` output.
2. **MF10 MD5 invented.** Line 29 claims dime reverse md5_hex `e2679b5fbb4221f6db6343f6edde9b4f`. Live/listing value is `8533943d7d88a011adaf372476bfe1f3` (`hTOUPX2IoBGtrzckdr/h8w==`, 1,336,791 B) — the plan's own table (lines 1104, 1134) agrees with live. Fix line 29.
3. **23RH primaries are live 404s.** Resolver lines 341-342 return `23rh_b.webp` / `23rh_c.webp` as obverse/reverse, and the Row 28 test (877-878) enshrines them. Either primary must be live URLs now with staged files swapped in after Gate 4, or add a hard Gate 0 block: no cutover until both HEAD 200 with matching MD5 in 4.1.3.
4. **Gate 4 text contradicts MF6.** Line 1434 says HEAD "200 OK" only; MF6 says Gate 4 checks prefix, Content-Type, bytes and MD5. Make Gate 4 match MF6. Also line 1436 says dev "frozen at 9b55f3d9" while line 7 says dev tip 32d4b42e — fix.

## SHOULD-FIX
5. 11 live docs use the key `Program / Series` (spaces); code reads only `Program/Series` and `program_series`. Add the variant (and a test) or state it is intentionally ignored.
6. Line 61: a ```dart fence wraps prose. Fix the markdown.
7. 7.3 cite → `coin_image_service.dart:535-571`.

## Score
Evidence/citations 24/25 · Correctness vs live data 23/30 (MF2 invented MD5, 404 primaries) · Tests 16/20 (41/42) · Gates/rollout 12/15 (Gate 4 vs MF6) · Hygiene 9/10; total **84/100 — REVISE**. Fix-only round: NET-729 to AG.
