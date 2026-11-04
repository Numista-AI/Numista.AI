# SAG_SCORE_NET-747_v4 (via api.x.ai grok-4.7, 3 Nov 2026)

SAG_SCORE_NET-747_v4

**Verdict: REVISE**  
**Score: 82/100**  
**Concurrence: No.** Do not concur with Argon 97, and do not concur with GB CoS 95 PASS. CoS’s defect list is right. Those defects are still in the plan text, so they are not “execute-time footnotes.” A typed YES on this file would authorize the wrong whitelist and no image-path rule.

Reviewed the plan text and the CoS score only. The 3,202-row master was not re-opened here. Plan-text gaps below are certain. Hit counts (173 `si.edu/collections/`, 1,070 source strings, 12 album rows) are CoS’s file check, accepted as the working census, not re-counted.

## Must-fixes (plan text, before any YES)

1. **Whitelist is wrong and would fail the build.** Sections 0 and 3.3 allow only `si.edu/collection/` (singular), `numismatics.org/collectionimages/`, `metmuseum.org/art/collection/`, plus three quoted phrases. They omit `si.edu/collections/`, `numismatics.org/collection/`, the Gallica credit, NNC Lilly prose that is not the exact string `Josiah K. Lilly Jr. Collection`, `collectors still hunt`, and `a-collectors-guide`. The scanner is a case-insensitive substring fail on `collection|collector|derived|seed|owner|album`. `si.edu/collection/` does not cover `si.edu/collections/`. As written, known museum URLs abort the build. Put every exemption in both whitelist sites as an **exact phrase or exact URL-prefix** only. Exempt only that matched span. Any other hit still exits 1. No bare-word pass. Copy phrases from the master; do not paraphrase. Keep `herbarium collection` only if that exact string is a verified credit, not a loose contains-check.

2. **Public image path is missing.** `reference_images/` does not appear. `seed_images` appears as `fold_source == "seed_images"`. State that public files mount only under `assets/catalog/reference_images/`, never `seed_images`, and that `url` / `full_url` / `file` values containing `seed_images`, `/workspace`, or `gs://` are rewritten or dropped before serialize. `fold_source` may be read to set `is_interleaved_checklist_only` and must not be emitted. Section 0’s “zero collection or owner wording is emitted” is false once museum credits are allowed; say “zero non-whitelisted hits.”

3. **Item (C) self-check does not check the gate.** (C)-1 compiles the regex and searches the literal `Sample clean numismatic text`. It never reads the master, never applies the whitelist, never fails a planted hit. That does not close BATON item D. Replace it with a check that (a) counts forbidden hits on the master, (b) lists remaining hits after the planned rewrites, (c) asserts each remainder is an exact whitelist entry, and (d) asserts a synthetic non-whitelisted `collection` string fails. Bind the 12 renames to the listed `nac_code`s, not `len == 12` on name/series. Input asserts do not prove the output file is clean; 8.2’s output scan stays mandatory and fail-closed.

4. **One file mtime cannot rank Newest.** Founder sort key is the jsonl timestamp, 3 Nov 2026, one value for every row. “Top 12–24” is then undefined. Specify a deterministic tie-break (named field or stable `nac_code` order) or a fixed sample rule, and keep the disclosure sentence.

5. **Zero-PII claim is false.** The intake form has optional email, and 4.7 also says the queue collects zero PII. Email is PII. Drop the field, or keep it, call it PII, ban it from `catalog_public_v1.json`, public HTML, and Firestore until a separate YES, and state where the off-repo queue retains it.

6. **`varieties` still emits `source` and `status`.** Images and figures drop those keys; varieties do not, and there is no scrub. Strip them, or rewrite them under the same token rule, before serialize. Do not assume the scanner will be the only control.

7. **One-badge rule has no priority.** Pre-Federal, Needs source, and Details coming can overlap. Card rule is one badge. State the winner (recommend Pre-Federal on the card; the other state as detail text only) so 951 placeholders and 9 pre-1792 rows cannot stack.

8. **Preflight `derived` and the other banned substrings on prose.** `derived` will hit ordinary history (“design derived from…”). Do not exempt the bare word. Require a dry-run token report on post-rewrite public fields and an exact-phrase whitelist or rewrite for every remaining legitimate hit before the build is treated as runnable.

## Should-fixes (not a second scope)

- Scrub key is `type == "collection-derived"` while the sources allow-list is `kind`. Scrub `kind`, `label`, and `tier`, or the scanner is the only backstop.
- Self-check paths say `INBOX/NET-747_inputs/`; inputs say `NET-747_inputs\`. One path.
- Confirm 1,070 is lines, not field occurrences, before the (A)-2 assert is binding.
- Define what the filled “Ask Morgan” button does (existing route only). Do not open a new chat or must-ship surface in this track.

## Sound — do not reopen

Branch `catalog-browse-p7v12` from `p7v12` only; `main` stays `9f04550a`; live site untouched; Stripe OFF; no `build.py` / `finalize.py`; Firestore rules and Firestore writes need a separate typed YES; allow-list field map; 81+966+23 source rewrite; composition provenance strip; album rename table; fail-closed scanner intent; era intervals; medal order; placeholder and mintage counts (4 + 3,198 = 3,202); preview channel only. Those stay.

## Why this is not PASS

CoS already deducted for the whitelist and the image path, then PASSed by parking the repair outside the plan. Eric’s YES is on the plan. This text still fails closed on museum URLs CoS found, never names `reference_images/`, and ships a scanner self-check that cannot fail. That is execute-blocking, not a style nit. Fix-only amendment (v4.1 or v5). No new product scope. Re-score after the eight must-fixes are in the plan body. No code, no deploy, no spend from this review.