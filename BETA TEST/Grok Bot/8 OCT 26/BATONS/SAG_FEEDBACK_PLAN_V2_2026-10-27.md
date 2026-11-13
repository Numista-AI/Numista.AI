# SAG_FEEDBACK_PLAN_V2_2026-10-27.md
- Source: Stand Alone Grok (Eric paste into CoS ~3:32 PM ET 27 Oct 2026)
- Chain: AG Plan.v2 → Argon 84 → GB CoS 82 → SAG 81 CONDITIONAL GO
- Next: AG writes Plan.v3 folding Argon GAP-1..4 + GB-1..3 + SAG locks below. NO EXECUTE yet.

**Blunt verdict: CONDITIONAL GO (81/100).** Fix the existing sweep, do not add a second engine. The catalog and UI gaps are real and must be closed before Eric's retest, but an authoritative overwrite on SKU match is the biggest risk in the plan as described.

### 1. Existing sweep vs new pre-check
Fix the existing `_run_duplicate_sweep`.
A second pre-check creates two sources of truth, double-counting risk, and another place the counter can drift. The worker already consumes the existing sweep's `duplicates_flagged`. The actual defects are narrow and local:
- The query/`import_session_id != session` filter silently drops any coin that lacks the field (common on older or manually entered items).
- The score never looks at SKU or invoice number, so a second upload of the same Mint SKU never flags.

Correct fix: treat missing `import_session_id` as eligible for comparison, and add strong SKU + invoice-number signals to the score. Keep the existing self-exclusion for the current batch. Do not invent a parallel engine.

### 2. Missing for a first-try pass on Eric's retest
The four reported symptoms map to four must-haves. Anything less and the retest will fail again:
- **Dupes:** Sweep must flag a second 26RJ (or any same-SKU/same-invoice) even when the existing coin has no `import_session_id`. Prove it with a Firestore dump of the sweep inputs and the counter.
- **Set enrichment:** 26RJ is absent from the catalog. Add a complete entry (is_set, set_id `uncirculated-coin-set-2026`, Theme/Subject or equivalent, images, Mint issue price 124.50, 20-coin metadata). Import must populate those fields so the new item is not blank/$0/no-image. Audit every other SKU on the test invoices the same way.
- **Contrast:** `_OwnerPhotoHero` white-on-cream is a hard fail. Force a readable color (or background) and verify the rendered pixel contrast on the actual cream surface, not just the code.
- **Set strip:** Horizontal strip must show all 20 coins without clipping the 5th (or any). Layout must handle the exact count used by 26RJ; screenshot the full strip.

Also required: no residual slash keys, preview-only backfill of Eric's existing test coins, and an explicit "no live writes until Eric's YES" gate. Without the catalog entry and the two UI fixes, the retest fails even if the sweep is perfect.

### 3. Risk of authoritative catalog overwrite on SKU match
High.
If the import path treats the catalog as the winner and overwrites existing coin fields on SKU match, it can destroy collector-specific data, manual corrections, different year/variant notes, or photos. For a collector app that is unacceptable.
Safe rule: catalog is authoritative only for *new* imports (fill blanks). On match, never overwrite non-blank fields unless an explicit, logged merge policy says otherwise. Prefer "fill missing only."

### 4. Score and recommendation
**81/100 — CONDITIONAL GO**

The direction is correct (fix the sweep in place, add the missing catalog entry, fix the two UI defects). It loses points for:
- the overwrite risk not being called out and constrained,
- incomplete verification criteria (no required Firestore dump of sweep inputs, no contrast screenshot, no full 20-coin strip proof),
- residual slash-key hygiene still unaddressed from prior rounds.

Go only after the plan explicitly locks: (a) sweep fix limited to missing-field inclusion + SKU/invoice scoring, (b) fill-missing-only catalog behavior, (c) the four retest proofs above, and (d) preview-only + Eric YES for any live write. Otherwise HOLD.
