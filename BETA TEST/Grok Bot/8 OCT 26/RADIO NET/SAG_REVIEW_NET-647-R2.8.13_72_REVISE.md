<!-- Stand Alone Grok review via xAI API model grok-4.7 , context-free prompt, 2026-11-02. A PASS still requires Eric's typed YES. No execution authorized. -->

# SAG Review: NET-647-R2.8.13
SCORE: 72/100
VERDICT: REVISE

## Summary
Fix-only plan does not clear the R2.8.12 exit criteria it claims to close. Most live-row code, unit tests, and Section 4 paths agree for Rows 01–09 and 12–27, but Row 28 is inverted, the tracker is not synced to the resolver, path-census figures contradict each other, and the non-destructive upload guard misses a user-photo URL pattern the plan itself fixtures. Claimed “100% fidelity” and “43/43 PASS” are not verifiable from this document.

## Must-fix (blocking)
- Section 4 Row 28 swaps primary vs fallback relative to §3.1 and the Row 28 test. Code/test primary = `2023_series/...five_honorees_composite.jpg` + `...four_states_composite.jpg`; fallbacks = staged `23rh_b.webp` / `23rh_c.webp`. Table does the opposite and marks staged files as the row URLs. Same MF4 class the matrix says is closed.
- Path census is false. Body says `95/97` live and `2/97` staged; §4.1.3 says `104/108` live and `4/108` staged; MF3 says `104 found, 0 missing`. Resolver still references objects absent from §4.1.3: `bulk_programs/us_mint_manual/highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg`, and ATB obverses `2013-S`, `2018-D`, `2019-D`, `2020-D`. §6 `26rj_a.webp` (`244,540 B`) is in neither the resolver nor the GCS table.
- Non-destructive rule is broken on the plan’s own Row 11 fixture. Guard matches `studio-9101802118-8c9a8-uploads`, `/microscope/`, `/user_uploads/`. Row 11 URLs are `numista-uploads-studio-9101802118-8c9a8/users/eric@numista.ai/coins/...`. Guard returns false; test expects canonical overwrite. §4 Row 10 lists catalog URLs as that doc’s outcome while `resolveFromMap` returns null. No Gate 6 script says “skip user uploads,” so a table-driven write would clobber microscope photos.
- §8 is not “100% synchronized” to §3.1. B26-6 cites `26rj_a.webp` (code uses `26rj_e.jpg` / `26rj_b.jpg`). B26-1/B26-2 depend on staged `26ea_b.webp` / `26xe_b.webp`, which the resolver never references. B26-13 cites enduring-liberty P art; code’s non-D half obverse is the unverified `SemiQ-Half-Dollar-Obverse-Unc-P.jpg`. B26-15–19 and B26-22–26 cite `obverse-p.jpg` / `obverse-denver.jpg` / “undated” obverses that the year-mint map and Philadeplhia fallback do not use.
- `extractSku` still folds `Personal Notes` into `combined` for keyword SKU inference (`morgan`, `trump`, `proof set`, etc.). That contradicts §3 “Never uses Personal Notes for theme matching” and can still hijack a 2026 doc before denomination matching. Neighbor-note pollution is not closed.
- Mayflower P fallback obverse is the D scrape (`SemiQ-Mayflower-Obverse-Unc-D.jpg`). Violates §2 principle 3 (no cross-mint obverse substitution). Empty half-dollar mint labels SKU `2026-HALF-D` but selects the P obverse path.

## Should-fix
- Footer is `**END PLAN R2.8.12**` while the header is R2.8.13. SF1 is claimed fixed and is not.
- §2 says “42-test”; §3.2 header and log say 43 (28 docs + extra Row 10 reference + 14 synthetic). Pick one.
- Several “fallbacks” are byte-identical to primaries (same size and MD5): dime P obverse vs `2026_dime_emerging_liberty_obverse.jpg`; dime reverse vs emerging-liberty reverse; half reverse vs enduring-liberty reverse; Mayflower reverse vs `SemiQ-Mayflower-Reverse-Unc.jpg`. Not alternative assets.
- `26RH` / `26SQRP` fallback reverse URL equals primary obverse URL. `23RG` is hard-mapped to 2026 `26RG` images.
- Guard ignores `obverse_image` / `reverse_image` (fields §2.1 says are live) and `numista-uploads-studio-.../users/...`.
- Row 07: `Mint Mark` `D` vs notes “Philadelphia (P)”. Table asserts `2026-D` without resolving the conflict.
- B26-20 “resolution” keeps the 1909 wheat obverse that the tracker calls the defect.
- `cleanMint` uses `contains('S'|'D'|'W'|'P')`, so “West Point” classifies as `S`.

## Risks
- Gate 4 only HEAD-checks four staged webps. Two are unwired; `23RH` display uses composites until fallback. Staging does not fix the pixels users see.
- §9 has no Firestore remediation procedure, but §2.1 depends on a Gate 6 write. Table vs null-guard disagreement is an overwrite risk.
- Docs-only mode plus `flutter test` of `package:numista_mobile/...` (not the embedded source) means the 43/43 log does not prove this plan’s code. All `+N` lines share `00:00`.
- Plan publishes account emails, Firestore ids, and user-scoped microscope URLs. Duplicate doc id `be10e44c…` on two accounts is unexplained.
- Load-bearing filename typo `Philadeplhia` is consistent in-plan; a real bucket rename would 404 every undated P/W ATB obverse.

## Security & Privacy Rule Check
1. No user home addresses are ever collected. — COMPLIANT. Resolver and fixtures use year, mint, SKU, image URLs, and emails only. No street/home address field is read or stored. Emails are not home addresses.
2. Receipt/invoice scans have the person's name and ship-to address automatically redacted BEFORE storage. — NOT ADDRESSED. §7.5 cites `numista_backend/main.py:8369-8376` writing `receipt_id` and `logger.error(... traceback ...)`. No redaction of name or ship-to before storage.
3. Nothing is invented: prices, bucket names, SKUs, figures must be sourced/verifiable in the plan, not fabricated or assumed. — VIOLATION. Mutually exclusive counts (`95/97`, `104/108`, `0 missing`); §6/§9.1 byte sizes and MD5s for `26ea_b.webp`, `26xe_b.webp`, `26rj_a.webp` are absent from the GCS dump that §4.1.3 calls the source (23rh rows are `N/A (Staged)` there, then given exact MD5s in §9.1); Row 28 URLs are not the code’s URLs; half-dollar P path has no size/MD5. §5 `$64.97` is labeled an example, not a live price.

## Notes on verifiability
- In-plan agreement holds for Rows 01–09 and 12–27 URL strings across §3.1, §3.2, and §4, and several §4 MD5 prefixes match §4.1.3 (`26EA_image_1.jpg` `126209` / `cb25bbc19d…`; dime reverse `1336791` / `8533943d7d…`). That does not extend to Row 10 semantics, Row 11 guard, Row 28, §8, or the census.
- §7 “verbatim `origin/dev 32d4b42e`” citations are assertions. No blob hash or quoted `git show` output is in the plan. Standalone review cannot confirm them.
- `43/43 PASS` runs a scratch test that imports the package service under a docs-only constraint. It is not evidence that the Dart in §3.1 was executed.
- Bucket `numista-reference-library` and SKU tokens are repeated often enough to treat the names as in-plan claims, not as independently checked live objects.