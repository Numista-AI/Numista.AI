# COS SCORE - NET-647 FAILFIX PLAN R2.8.11 - 88/100 - REVISE - 2026-11-01 8:20 PM EST
Scorer: Grok CoS (independent re-verification; no plan or Argon claim trusted). Mode: DOCS-ONLY, read-only.
Plan scored: FAILFIX_PLAN_NET-647_R2.8.11_20261101.md (1,576 lines, 166,324 B). Review baton: NET-730. Fix-only wake: NET-731.
Argon scored 97 PASS (NET-730A). I do not concur: three of the "fixed" claims are not true in the file.

## Verdict: REVISE (88). Code is now good; the remaining problems are in the plan text. SAG NOT run. Small fix-only.

## What I verified myself
- MF-A FIXED. Diffed Section 7 blocks against `git show 32d4b42e:<path>` (origin/dev = 32d4b42e5d93ac8e): 7.1 47/47, 7.2 8/8 (em dash byte-checked, U+2014 both sides), 7.3 37/37, 7.4 8/8, 7.5 8/8.
- MF-B FIXED. `hasUserUploadedPhotos` (lines 97-118) catches /microscope/, studio-9101802118-8c9a8-uploads, scan_source microscope; `resolveFromMap` returns null first (line 207); positive and negative tests at 742 / 756.
- 4.1.1 FIXED (Row 11 doc 8f2197d5..., "250th Anniversary of American Independence", MD5 ef82afd24a... / cceb4ab85d...).
- Live smoke 8:15 PM EST: numista.ai 200, main.dart.js 200, bad path 404. Staged 26ea_b / 23rh_c still 404 (expected, not uploaded).

## MUST-FIX (plain English)
MF-1 Gate 4 script (Section 9.2, lines 1552-1567) still does NOT check MD5. The text above it lists 4 checks, but the Python only asserts status, Content-Type, and size. Add the x-goog-hash md5 check inside the loop: parse `md5=` from `x-goog-hash`, base64-decode, hex it, assert it equals the expected hex. (Argon also flagged this but called it non-blocking; it was the whole point of MF-C, so it blocks.)
MF-2 Resolution matrix (Section 1) still carries the wrong numbers MF-D asked to remove:
  - Line 29 MF10 row: dime reverse md5_hex still `e2679b5fbb4221f6db6343f6edde9b4f`; must be `8533943d7d88a011adaf372476bfe1f3`.
  - Line 21 MF2 row: Row 10 doc still `d49bb0fd-bc3f-4e08-9df5-cf6bfd31b7cd`; live Row 10 is `0172d0ee64284a12a8aa269ce805ec07`.
  The radio and WHOSE_TURN said both were corrected. They were not.
MF-3 Gate 6 (line 1570) still says "`dev` remains frozen at `9b55f3d9`". Dev tip is `32d4b42e`. WHOSE_TURN said this was fixed.

## SHOULD-FIX
SF-1 Stale version labels: line 3 "Plan Version: R2.8.10", line 12 "R2.8.10 Deliberation", line 14 "This plan (R2.8.10)", line 18 and 1495 "R2.8.10 Resolution". Change to R2.8.11 and point line 14 at the R2.8.10 scores (77 / 84 / Argon), not the R2.8.9 54.
SF-2 `resolveFromMap` primaryTitle (lines 213-221) reads 'Program/Series' but not 'Program / Series' (with spaces), the key 11 live docs use. Add it, as extractSku already does (159, 169).
SF-3 Line 8 queue text says NET-718 R3 is "undergoing Argon Review"; it is 98 PASS and staged in For SAG. Update or drop.

## NIT
N1 7.4 header cites 2282-2290 (9 lines) but the block is 8 lines (2282-2289).

## Score breakdown
Data accuracy 18/20 | URL/bucket truth 20/20 | Tests 14/15 | Guards 14/15 | Staging/gates 7/10 | Tracker/docs 8/10 | Claim honesty 2/5 | Review quotes 5/5 = 88/100

Next: R2.8.12 fix-only (MF-1..3, SF-1..3). Expect >=95 if those land exactly; nothing else may change.