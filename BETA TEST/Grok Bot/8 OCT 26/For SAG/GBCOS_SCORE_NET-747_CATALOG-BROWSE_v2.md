# GB CoS SCORE: NET-747 Catalog Browse Plan v2
- Scored by: GB CoS, 2026-11-03 ~2:00 PM ET. Read-only: no code, no git, no deploys.
- Plan: INBOX\AG_PLAN_NET-747_CATALOG-BROWSE_v2.md (272 lines). Argon v2 claimed 97 PASS.
- Facts checked against entries_master_20261103.jsonl (box copy, 3,202 records).

## SCORE: 82 / 100. VERDICT: REVISE (95 needed)

Argon's 97 does not hold up. Argon says the allow-list is "aligned" (plan line 24), but the jsonl shows otherwise. The plan also has count errors and a PII strip list that is not complete.

## Facts from the jsonl (verified)
- 3,202 records: 2,965 coins, 181 notes and 56 medals (field `type`, not `category`).
- 951 records have "details coming" (`display_label`). OK.
- 9 records have `pre_federal`=True. OK (plan line 118).
- `varieties` is a list of objects {name, attribution, reference_work, source, status}. OK.
- 4 records have a sourced `mintage`. 3,198 are "not yet sourced".
- Neither `created_at` nor `date_added` appears in any record.
- `primary_image` is on all 3,202 records. `type_image` is on 966.
- These fields exist but are not on the plan's strip list: `seed_status` (1,724), `fold_source` (value e.g. "seed_images"), `record_status`, `needs_fact_check`, `published_on_x`, `program`, `measurement_note`.
- The substring "collection" appears 20,129 times in the raw file and "seed" 11,382 times.

## MUST-FIX
1. **The allow-list names fields that do not exist (Req 1 and 4; plan line 64; the claim at line 24 is false).**
   - The plan lists `category, year_start, year_end, mint, weight_grams, edge, obverse, reverse, notes, references, created_at`. None of these are in the jsonl.
   - The real keys are `type, year, mint_facility, mint_mark_on_coin, weight_g, diameter_mm, history, sources, mintage, series, era, designer, denomination, composition, figures`.
   - `primary_image`, `type_image`, `secondary_image`, `extra_images`, `varieties`, `pre_federal`, `pre_federal_state` and `display_label` are not on the allow-list at all. As written, the site would publish no images, no varieties and no Pre-Federal flag.
   - Fix: rewrite the allow-list against the real keys and name each nested sub-field that is allowed.
2. **The PII and seed strip is not complete (Req 4, critical; plan lines 68 and 100).**
   - Add `seed_status`, `fold_source`, `record_status`, `needs_fact_check` and `published_on_x` (unless approved) to the strip list or a deny-by-default rule.
   - Add a scrub step for "seed" and "collection" text inside nested values (image paths, sources, history). Line 100 only *confirms* zero tokens; it does not say how they get removed.
   - The automated scan (lines 78-81) must include the seed and collection tokens, and the gate must fail on any hit.
3. **Counts are wrong (Nothing-is-invented rule).**
   - Coins are listed as 2,906 at lines 108 and 190. The jsonl has 2,965.
   - "Sourced mintages = 0 / 100% Needs source" at lines 54 and 255 is wrong: 4 records have a sourced mintage.
   - Fix the numbers, and show a sourced mintage, with its source, where one exists.
4. **Newest has no date field (Req 10; plan lines 64 and 95).**
   - `created_at` is on the allow-list, but no record has it, and no record has `date_added` either.
   - Spell out the fallback: use the Catalog Research file date and **show a visible note saying the date comes from the file**. Line 95 never says the site discloses this.
   - Say how seeds are excluded from Newest (which field), and that this must not leak any seed wording.
5. **Ask Morgan button colour (Req 5; plan line 128).**
   - The requirement is a separate **navy** Ask Morgan button. The plan has a white button with a blue outline.
   - Match the spec, or cite where UX signed off on the change.
6. **No Firestore or rules guard is stated (plan line 153; lines 266-272).**
   - The intake "review queue" needs storage, but the plan never says that firestore.rules deploys or Firestore writes need Eric's separate YES (rules are project-wide and reach LIVE).
   - Add this to section 1 and section 9. Line 228 says "p7v12 Deploy" after YES. Make sure that YES covers the preview channel only, and that nothing goes live.

## Verified OK (with line refs)
- Never run build.py or finalize.py (lines 49 and 269). Varieties are objects (line 53).
- primary_image is an exact match and type_image shows "date may differ" (lines 139-141).
- Seeds appear only inside the checklist and never in their own list (lines 91-95). The 951 are name-only with a neutral outline (lines 96-98).
- PII manual audit: 100 records, at least 50 from the seed (line 83). The automated scan covers all 3,202 (line 78).
- Owl 160-200px, 64px search box, in-progress box, and section order Browse, Newest, Coverage, Missing (lines 107-111 and 124-129).
- Pre-Federal blue-outline pill. Gray badges, one per card, never red. Detail view shows "Mintage: Needs source" (lines 118-121).
- "Show as table" toggle (line 110). Foreign coins get one line (line 146).
- Form: labels above fields, (optional), Send, and "Thanks - we'll look into it." (lines 150-151).
- Type sizes 20/24/30/40, tap targets 48px, 200% zoom and phone width (lines 156-158).
- Soft-404 reuses NotFoundScreen with noindex (lines 164-170).
- Branch catalog-browse-p7v12 from p7v12; never main or live; must-ships and NET-746 come first (lines 30-38 and 267-271).

## Non-blocking notes
- N-a: Line 261 still says badges meet "15.39:1 / 12.63:1" for all text. Fine, but use the UX-file numbers only.
- N-b: Line 183: if an SEO policy needs a real 404, that is a later item. Do not add Cloud Run in this track.
- N-c: Line 145: the era buckets overlap at 1837 and 1873. Make the ranges half-open.
- N-d: The 9 Morgan weight-conflict rejects are not in the master. Confirm none of them shows up as a placeholder.
- N-e: Line 153 mentions captcha and rate-limiting. Name the provider later, and note that it must not collect PII.
