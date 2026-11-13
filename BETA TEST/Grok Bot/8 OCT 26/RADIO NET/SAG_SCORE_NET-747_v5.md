# SAG SCORE NET-747 v5 (via xAI API grok-4.7, 2026-11-04 ET)

SAG SCORE: 95/100 — PASS

Concur with GB CoS **95 PASS** and binding conditions C1–C5. Do **not** concur with Argon **97** as a reading of this file: CoS’s quote audit holds. The plan’s whitelist is the 11-row table in §3.3-W (includes `National Numismatic Collection`), and the §3.2-3 renames are generic series names (Lincoln Cent, Jefferson Nickel, Modern Commemorative Dollars, American Women Quarters), not “Coin Set / Nickel Set / Dollar Set.” Argon’s `\beric\b` note is not in v5; do not add it.

All eight v4 must-fixes are closed in the plan body. No v6 rewrite is required if Eric’s YES carries the binding conditions below. YES on the plan file alone, ignoring C1, is not authorized.

## v4 must-fix closeout

1. **Whitelist — closed.** One list only: §3.3-W (exact, case-sensitive spans; mask then re-scan; no bare-word pass). Includes `si.edu/collections/` (173), `National Numismatic Collection` (329), Gallica credit, both Lilly phrases, `collectors still hunt`, `a-collectors-guide`. `herbarium` is gone. §0 item 3 and §4.1-4 point at §3.3-W only. CoS re-ran the census; counts match.
2. **Image path — closed.** §3.2-5: local `url` / `full_url` / `file` become `reference_images/<basename>`, or are dropped; `seed_images/`, `/workspace`, `gs://`, `users/`, `googleapis` are forbidden. §3.1: `fold_source` is computed-from only and never emitted. §0 item 1 and §4.1-4 say “zero non-whitelisted,” not “zero collection wording.”
3. **Gate — closed in normative text.** §3.3 scans the built JSON and rendered HTML, fail-closed, with a planted-leak negative test. §3.2-3 binds the 12 renames to full `nac_code`s and says STOP if the set does not match. §8.1 (A)-2 asserts **1,070 occurrences**, not `len(lines)==1070`. §8.2-1 stays fail-closed. (The §8.1 snippets are still not copy-paste runnable — should-fix, not a return of the v4 sample-string check.)
4. **Newest — closed.** §4.1-2: pool `fold_source != "seed_images"` = 590; order is file date (one value), then `year` desc (nulls last), then `nac_code` asc; two-run assert; disclosure sentence is specified. CoS: 590 (435/99/56), 5 null-year.
5. **Email — closed.** §4.7: no email field; no name, contact, or free-text identity fields.
6. **Varieties — closed.** §3.1 output allow-list is `{name, attribution, reference_work}`; strip list drops `varieties[].source` and `varieties[].status`. §2’s `{source, status}` describes the master input (CoS: 186), not the emit.
7. **Badge priority — closed.** §4.3: one badge, **Pre-Federal > Details coming > Needs source**; other state as detail text; overlap record `NAC1.BN.US.D40.NOTE.1778.BEP.BASE.2` named.
8. **Dry-run / no bare `derived` — closed.** §3.3-D and §3.3-W: post-rewrite dry-run, whitelisted vs non-whitelisted, go only if non-whitelisted == 0, no bare-word exemption.

## MUST-FIXES

None.

## BINDING CONDITIONS (attach to YES; do not execute without them)

1. **C1 overrides §3.1 and §4.3.** `is_pre_federal` / Pre-Federal badge = `pre_federal == true` only → **9**. `NAC1.MD.US.GEORGEWASH.MEDAL.1789.XX.BASE.3` (year 1789, `pre_federal=false`) gets no Pre-Federal badge. Era bucket `< 1792` in §4.6 may still list it. Do not implement §3.1’s `year < 1792 OR pre_federal == true` (that is 10).
2. **C2.** One builder and one validator entrypoint. One input path, defaulted to the real `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl` (CoS/Argon). Not the three strings now in the header, §8.1, and §0-v5.
3. **C3.** `BOUND_12` = the 12 `nac_code`s written in §3.2-3, literally. Lilly series stays excluded and whitelisted.
4. **C4.** No personal-name token list in the repo. Do not add `\beric\b` or any real name. Keep whole-word `\bAJ\b` only as already specified.
5. **C5.** Firestore rules deploy or Firestore writes: separate Eric YES. Preview channel `p7v12` only. No `build.py` / `finalize.py`. `origin/main` stays `9f04550a`.

## SHOULD-FIXES

1. **§3.1 / §2 / §4.3 / §8.2-4 still disagree on paper.** §3.1 defines `is_pre_federal` as `year < 1792` or `pre_federal == true`. §2 and §4.3 say 9 pre-1792 items. §4.3 “never on >=1792” does not exclude 1789. §8.2-4 leaves the pick open. C1 is the execute rule; a later edit should make those four places say the same thing so a builder does not follow §3.1 alone.
2. **§8.1 (C)-3** uses undefined `BOUND_12_FROM_3_2`. Paste the 12 codes from §3.2-3 into the assert.
3. **§8.1 (C)-1** `--whitelist-exact §3.3-W` is not a path. Hardcode the §3.3-W table in the validator so the flagless §8.2-1 command cannot drop the whitelist and fail museum URLs (the v4 failure mode).
4. **Input path still three ways** (header `NET-747_inputs\…`, §8.1 `INBOX/NET-747_inputs/…`, real INBOX path above). §0-v5 marked “one input path” not adopted. C2 closes it at execute; the file should still be one string.
5. **Two script roots:** §3.1 `scripts/catalog/build_public_catalog.py` vs §3.3 / §8 `tools/catalog/pii_gate_validator.py`. Pick one tree.
6. **§4.1-2** still says “top 12–24.” Order is deterministic; cardinality is not. Pin one N (24, the top of the stated range) and assert that count on both runs.
7. **Ask Morgan action still undefined** (§4.2, §4.4, §5.1 style only). §0-v5 left it open. At build, call the existing p7v12 Ask Morgan entry only. Do not add a route or a new chat surface. Argon’s `AiChatScreen` / `onAskMorganWithQuery` citation was not verified by CoS; do not treat it as settled plan text.
8. **§1** says “26 Nov Must-Ships.” CoS states the locked launch is 27 Nov. Wording only — confirm before execute. Catalog work still pauses if a must-ship blocks.
9. **§3.2-5** emits `reference_images/<basename>` and does not name the asset-bundle directory. Confirm one public prefix at build so rewritten `file` values resolve. This is not a PII gap; the forbidden-path rewrite is already specified.

## Rejected (do not fold into the build)

- Argon numbered whitelist of 10, “Coin Set” rename table, “Recently Added — 24 Cards / `entries_20261103` = 590,” §4.7 dropdown form, and `numista_backend/scripts/pii_gate_validator.py` paths — not in this plan. CoS: `entries_20261103` = 528; 590 is `fold_source != "seed_images"`.
- Argon `\beric\b` / “1,059 americanhistory URLs.” Not in v5. CoS: 191 occurrences; adding the name would itself put a name in source.

## Not reopened

Branch `catalog-browse-p7v12` from `p7v12` only; live site untouched; Stripe OFF; allow-list field map; 81+966+23 source rewrite to `"Numista.Ai reference photo"`; composition provenance strip (1,724); album rows keyed by `nac_code`; sources emit `{label, url, title}` only; era intervals; medal order after coins and notes; placeholders 951; sourced mintages 4 and `"Needs source"` 3,198; preview channel only; five must-ships preempt catalog work.