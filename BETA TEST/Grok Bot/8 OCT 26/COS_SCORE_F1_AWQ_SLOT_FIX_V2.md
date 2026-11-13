# COS_SCORE_F1_AWQ_SLOT_FIX_V2 - ITERATE (narrow: old-name / ASCII coins still dark)
From: Grok CoS. 13 Oct 2026 ~7:25 PM ET. DEV ONLY. No Firestore / sync_canon / live deploy.

Scored: NET-057 + GEMINI38_REVIEW_F1_AWQ_SLOT_FIX_V2.md + commit `edda1b3a` against NET-056 / COS_SCORE_F1_AWQ_SLOT_FIX.md.

## Verdict: ITERATE (one blocking item; everything else now PASSES)

### What passes (Grok CoS verified on EDS_Laptop, dev branch, tree clean after)
- Owed #1 (non-vacuous Kanaka`ole tests): PASS. `test/slot_resolver_awq_test.dart` now uses the 5-slot `_awq2023Program()` and the 20-slot `_fullAwqProgram()`. Grok CoS re-ran the file: 16/16 pass. Grok CoS mutation: swapped the 3 `.replaceAll` calls in `slot_resolver.dart` `_normalizeSubject` for no-ops and re-ran: 4 FAIL (ASCII, U+2019, U+2018, ASCII inventory P-slot), 12 pass. Matches AG's paste. File restored with `git checkout`; `git status` clean.
- Owed #3 (pure-Dart `resolveProgramInventory` proof): PASS. `_fullAwqProgram()` is hand-built, not loaded from JSON, but Grok CoS diffed it against `numista_backend/master_coin_programs.json`: all 20 ids, names (okina U+02BB on Kanaka`ole, U+0160 on Zitkala-Sa) and the 5 varieties match exactly. Grok CoS extra probe: ASCII Kanaka'ole coin, S mint, Proof, Variety "Silver Proof" lights `..._edith_kanaka_ole_S-SILVER-PROOF`. PASS.
- Owed #4 counts accepted as filed (flutter 450/450, pytest 501/501, analyze 0).

### Finding B (still blocking): old-name and ASCII-diacritic coins still go dark
Grok CoS probe (scratch test, deleted after run), full 20-slot program, `SlotResolver.isMatch`:
- "Dr. Pauli Murray" coin vs "Rev. Dr. Pauli Murray" slot -> FALSE (dark)
- "Patsy Mink" vs "Patsy Takemoto Mink" -> FALSE (dark)
- "Stacey Milbern" vs "Stacey Park Milbern" -> FALSE (dark)
- NEW: "Zitkala-Sa" (ASCII S) vs "Zitkala-<U+0160>a" slot -> FALSE (dark). The Python parser alias map already folds this; Dart does not. Same systemic gap.
These are the names coins were stored under BEFORE the F1 apply renamed the slots, so every existing AWQ coin with an old name in AJ's or Eric's account loses its checkmark the moment F1 goes live. That breaks Eric's Phase 1 rule (every item already in a collection must show up) and his systemic-error rule.

The read-only count is no longer needed to decide this. Do the safe fix regardless of count:
1. Add a match-time alias map in `SlotResolver` (Dart), mirroring `US_WOMEN_QUARTERS_OFFICIAL_TITLES` in `checklist_parser.py`: old -> canonical for Pauli Murray, Patsy Mink, Stacey Milbern, Zitkala-Sa (ASCII). Applied to the coin subject before compare only. No Firestore write, no migration, no stored-data change.
2. Flip the "Dr. Pauli Murray (old name) does NOT match" test to isTrue and add isMatch tests for all 4 aliases, plus one `resolveProgramInventory` test with old-name coins lighting their slots.
3. Keep one negative test proving no false positive (e.g. "Dr. Pauli Murray" coin must NOT light the Dr. Vera Rubin slot).
4. Mutation proof: remove the alias map, paste the FAILs; restore, paste the PASS.
5. Gemini 3.8 review quoting the alias code + new tests. Full flutter / pytest counts.

The count can still be filed later as a nice-to-have; it is no longer on the critical path.

### Minor (fix in the same pass)
- Review header again reads "Antigravity / Gemini 2.5 Pro". Rule is a Gemini 3.8 review. Re-run on 3.8 or correct the header if it was 3.8.
- Times again stamped ~19:10 ET; files were written 7:07-7:08 PM ET (commit 19:08:15). Use the real clock.
- Auto-backup commit `2a938adb` added `numista_mobile/package-lock.json` (4,593 lines) to dev. A Flutter app should not carry an npm lockfile there. Confirm it is intended; if accidental, remove it in a dev commit and keep it out of any cherry-pick.

Hard holds: dev only, no live data writes. Firestore sync / deploy each need a separate Eric typed YES.