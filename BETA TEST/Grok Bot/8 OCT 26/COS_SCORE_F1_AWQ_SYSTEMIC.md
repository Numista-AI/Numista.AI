# COS_SCORE_F1_AWQ_SYSTEMIC - ITERATE
From: Grok CoS. 13 Oct 2026 ~6:45 PM ET. DEV ONLY. No Firestore / sync_canon / live deploy.

Scored: NET-053 + `awq_systemic_check.py` (AG scratch) + commit `6b92e2c6` against NET-050/NET-052 (checklist PDF + scanner slot matching).

## Verdict: ITERATE
The script re-runs clean for me (89 PASS / 0 FAIL), and the inline `_derive_strike_fields` copy matches `numista_backend/main.py:8179`. But it checks catalog data only. It never runs `SlotResolver` (`numista_mobile/lib/utils/slot_resolver.dart`), never renders a checklist PDF, and never scans anything. NET-052 asked for proof (screenshots or FT log). And my own check found a real slot-matching regression it missed.

### Finding 1 (real regression): Edith Kanaka'ole slot will go dark
- Before apply (`15d4b047~1`): catalog name `Edith Kanaka'ole` (ASCII apostrophe).
- After apply: `Edith Kanaka` + U+02BB okina + `ole`.
- Scanner `services/checklist_parser.py` lines 32/33/186 still emit ASCII `Edith Kanaka'ole`. Existing user coins most likely carry ASCII too.
- `SlotResolver._normalizeSubject` (line ~205) only lowercases, trims and strips a year prefix. The theme path (line ~238-240) is EXACT equality, no fallback. So ASCII theme != okina slot, and the slot stays dark on the checklist and the PDF once Firestore is synced.

### Finding 2 (risk, verify): renamed slots vs existing user coins
`Dr. Pauli Murray` -> `Rev. Dr. Pauli Murray`, `Patsy Mink` -> `Patsy Takemoto Mink`, `Stacey Milbern` -> `Stacey Park Milbern`. The scanner maps new scans to the new names, but any EXISTING coin stored with an old Theme/Subject fails the same exact-equality test. Needs a read-only count of old-name coins (AJ + Eric accounts) or an alias in the resolver. No live writes.

### Finding 3 (test quality)
- Parser-name check appends a PASS ("NOTE ... does NOT contain") when a name is missing, so it can't fail. Make it a FAIL.
- Import the real `_derive_strike_fields` from `main.py` instead of an inline copy.

## Owed before PASS
1. Fix: normalize apostrophe variants (ASCII ', U+2018, U+2019, U+02BB) in `_normalizeSubject` (and the parser title map), OR keep the catalog display name with okina but match on a normalized key. Plus old->new name aliases if Finding 2 shows old-name coins.
2. Dart unit test: AWQ Kanaka'ole ASCII coin lights okina slot, and old-name Murray/Mink/Milbern coins light their renamed slots. Run `flutter test` for all `slot_resolver_*_test.dart`; paste results.
3. Tier 1/2 code change -> `GEMINI38_REVIEW_F1_AWQ_SLOT_FIX.md` with the changed code quoted.
4. Dev-only evidence: AWQ checklist PDF render (or FT log path) showing all 100 slots incl. Kanaka'ole S-SILVER-PROOF, from a dev/test account only.

Hard holds: dev only, no live data writes, Firestore sync needs a separate Eric typed YES.
