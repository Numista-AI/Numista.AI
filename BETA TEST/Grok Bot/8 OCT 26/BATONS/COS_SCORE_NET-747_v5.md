# GB CoS SCORE — NET-747 v5 (Catalog Browse) — Attempt 5 of 10
- Plan: INBOX\AG_PLAN_NET-747_CATALOG-BROWSE_v5.md — MD5 81F888FD623D71C97C34B6F4ADD45F34, 419 lines (verified)
- Data: entries_master_20261103.jsonl — MD5 6164B138A3BF9A0C3A09A3917B0D8E39 on laptop and box (identical), 3,202 rows
- Argon review: INBOX\ARGON_REVIEW_NET-747_CATALOG-BROWSE_v5.md (97 PASS)
- Scored: 2026-11-04 ET by GB CoS. Plan not edited. Nothing executed.

## SCORE: 95 / 100 — PASS (binding build conditions below)

## Data facts re-run by CoS (python on the master)
| Claim | Plan | Actual | OK |
|---|---|---|---|
| pre_federal==true | 9 | 9 (rows 1-9) | yes |
| year<1792 | (10 open item) | 10; row 10 GW 1789 medal pre_federal=false | yes |
| 12 album nac_codes / rows 1250,1251,1252,1659,1920,1996,3081,3082,3084,3085,3086,3123 | yes | exact match; only other "Collection" in name/series is the Lilly series (row 1049) | yes |
| "This large collection includes" | 1849 $20 | row 199 NAC1.CN.US.20DOLLARS.COINS.1849.P.BASE.S | yes |
| harvey-b-jacobson CoinWeek URL | drop | row 27 NAC1.CN.US.5D.CAPBUST.1795.P.V2.4 (plan keys the drop by URL, so it lands) | yes |
| Whitelist counts (NNC 329, si.edu/collections/ 173, met 2, ANS 1+1, Gallica 3, Lilly 1+1, collectors still hunt 1, a-collectors-guide 1) | yes | all match | yes |
| "collection photo, owner removed" | 1,070 occ. | 1,070 | yes |
| Newest pool fold_source!=seed_images | 590 (435/99/56), 5 null-year | 590 (435/99/56), 5 null-year | yes |
| Placeholders | 951 | 951 | yes |
| varieties carry source/status | 186 | 186 | yes |

## Argon review — quote audit (do NOT trust its quotes)
Argon's verdict and data counts largely hold, but many of its "plan citations" are NOT in the v5 file:
1. Whitelist quoted as a numbered list of 10 at lines 179-193: actual is an 11-row table that also includes `National Numismatic Collection` (329). Misquote.
2. 12 renames quoted as "Coin Set / Nickel Set / Dollar Set": plan actually renames to generic series names (Lincoln Cent, Jefferson Nickel, Modern Commemorative Dollars, American Women Quarters). Fabricated quote.
3. "Recently Added — 24 Cards ... fold_source == entries_20261103 (590 records)": not in plan. Real counts: entries_20261103 = 528; 590 is fold_source != seed_images (incl. 62 suspect_fixed). Fabricated quote + wrong count.
4. §4.7 form field list (nac_code / field_name dropdown / suggested_correction / source_citation): not in plan. Plan §4.7 is description / year / type / source URL, no email. Fabricated.
5. Varieties JSON snippet ("J-10") and pii_gate_validator.py command paths under numista_backend/scripts: not in plan.
6. Ruling 2 (`\beric\b`): plan contains NO `eric` token anywhere (not §0 line 50, not §3.3 line 195). Argon's "1,059 americanhistory URLs" is also wrong (191 occurrences). The ruling is moot for v5. Do NOT add any real person's name to a token list in the repo — that would itself place a name in source (AJ PII rule). If a user-name guard is wanted, load it from an off-repo, untracked secret list.
7. Ruling 1 (strict pre_federal==true → 9): CORRECT and adopted.
8. Ask Morgan wiring: not verified by CoS against Dart (box has no current checkout confirmed); treat as non-binding implementation hint.

## Deductions (-5)
- -2: §3.1 line 144 still defines is_pre_federal as `year < 1792 OR pre_federal == true` (= 10) and §8.2-4 leaves it open; resolved only by Argon ruling, not in plan text.
- -1: script paths inconsistent (scripts/catalog/build_public_catalog.py vs tools/catalog/pii_gate_validator.py); §8.1 input path relative "INBOX/NET-747_inputs/..." vs real "1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/...".
- -1: §8.1 (C)-3 uses undefined placeholder BOUND_12_FROM_3_2.
- -1: §1 says "26 Nov must-ships"; locked launch is 27 Nov (wording only).

## Binding build conditions (no new plan version needed)
C1. is_pre_federal = (pre_federal == true) only → 9; GW 1789 medal gets no Pre-Federal badge (era bucket "<1792" may still list it under Pre-Federal & Founding era text — builder must not badge it).
C2. One builder/validator path and one input path, defaulted to the real INBOX\NET-747_inputs path.
C3. BOUND_12 list = the 12 nac_codes in §3.2-3, literally.
C4. No personal name tokens committed to repo.
C5. Firestore rules deploy / Firestore writes: separate Eric YES (unchanged). Preview p7v12 only.
