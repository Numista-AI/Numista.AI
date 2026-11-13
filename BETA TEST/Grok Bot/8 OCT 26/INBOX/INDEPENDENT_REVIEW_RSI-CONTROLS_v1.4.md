# Independent advisory review — RSI-CONTROLS v1.4 (replacement writer GB-RSI-Replacement-20261109-A, try 1/4, documented track 7/10)
Written: 2026-11-09 7:02 PM EST by executor subagent. ADVISORY ONLY — not the CoS G1 score, not SAG, no filing/authority/counter change.

## Coverage and identity (box documents only; no git/source/peer/query)
| File | Lines/Bytes | SHA-256 | Check |
|---|---|---|---|
| v14-replacement/PLAN_RSI-CONTROLS_PROCESS-CONTROLS_v1.4.md | 505 / 56,464 | f07505baa3e3a93c06d2950fba21a3a44d766168b47b7eb219a2c619f1a2172f | match; read in full |
| v14-replacement/CLOSURE_MAP_RSI-CONTROLS_v1.4.md | 39 / 9,688 | 2ee2a82811901838141b449be104a4a479ddca3e013463038fd0ce97fc7ecfb2 | match; read in full |
| v14-replacement/HASH_MANIFEST_RSI-CONTROLS_v1.4.md | 28 / 2,800 | f7c11a42abdfd9b01b15eebc10840d645ed1457b4f2d654f17ccb2c3cd6b8c3a | match; read in full |
| v14-replacement/DIFF_PLAN_RSI-CONTROLS_v1.3-to-v1.4.diff | 352 / 51,588 | 9dfc43d73fe44f7ab71fe5100c6e40ad9340caa12c4efc2ddb658c9829514d27 | match; 18 hunks; body byte-identical to my own `diff -u` of v1.3→v1.4 (only header path lines differ) |
| COS_SCORE…v1.3_94_REVISE_REPLACE-WRITER_20261109.md | 46 / 7,614 | 1e6b0ae9beaaf69d94b90461fe96636552eec464db2f932a6e179069cfa71351 | match; read in full |
| v13-intake/PLAN…v1.3.md (baseline) | 491 | ada465220dd79efd8c946759e0ef28af8143b9de50cdc7578ebba31c7b573549 | unchanged |
Also present but not part of the plan: `.build_v14.py` (217 lines, SHA 457f2372b346e5dd417421694a06c43450f72ba39654b959ab9f9360d8f4ee57, matches manifest) — a writer-side document-edit script, not product code; process note only, no deduction.
Hunks touch only header/§0.1/§1.7/§2.1–2.2/§3.1–3.3/§5.1–5.2/§6.2 G-1 input row/§7.2–7.3/§8.2/§10/§11. §4, §6.1, §6.3, §8.1, §8.3, §9 byte-unchanged → MF2/MF5/MF6 text preserved.

## MF1 — repair proposed; I find it closes the finding (0)
- L133–134: attempt = formal delivery of a unique packet "by or for" the writer, **completeness/preflight/score-independent**; deficient or SAY-AGAIN packets cannot be disowned. L135 pre-delivery drafts exempt. Fixes v1.3 L131 "complete packet" loophole.
- L144: declaring owner = owner of the gate the packet was delivered to, in its existing disposition record; no timeout, no new layer; unrecorded = pending, never failed. Matches CoS 94 MF1 instruction exactly.
- L146–147 ordinal fixed at delivery; retirement fires on gate-owner-recorded terminal non-pass at 4th; L168 terminal PASS only after all required plan-quality passes (CoS-only pass stays pending at G-2) — consistent with L176–180 dedup; L170/L172/L317/L388/L397 aligned.
- L136 "one pending packet per writer per track" is a consequence of the existing post-delivery-supersession rule, not a new gate. No material defect.

## MF3 — repair proposed; mostly closes; residual −1 (narrow)
Fixed: L356–370 one population = unique delivered packets in stated cohort+window with terminal disposition by window end; numerator ⊂ denominator (PASS + terminal non-pass), reviews not units, ≤100% (L368); pending excluded both sides and reported (L369); historical-unknown excluded both sides, still cap-counted (L370) — no invented values; L182 aligned. Velocity replaced with non-tautological Packets-to-Dual-Pass per track/chunk (L345–350) with window/cohort (L347), four outcome classes incl. right-censored (L348), ≤2 only an aspirational pilot target over determined cases, not a gate (L349); MB-009 overclaim removed (L353).
Residual (material to the metric's computability, not cosmetic): L346 counts packets on track k "all writers, lineage inherited", while L347 admits tracks/chunks "whose first counted packet was formally delivered within the window" and L337–342 pilot candidates are all tracks with pre-pilot history (e.g. NET-813 v1.4+, NET-814 v1.3+, NET-817 RP chunks inheriting parent lineage per §4.2). Read literally, every pilot candidate's first counted packet predates the pilot window → empty pilot population; read loosely, pre-pilot historical packets enter the pilot count → contradicts L347/L361/L364 "never pooled". Start point for pilot-cohort counting (first pilot-eligible packet vs. lineage start; whether a split chunk restarts at 1 or inherits parent's 10) is undefined. Impact: the headline improvement metric Eric asked for cannot be computed unambiguously on the named pilot. Fix (one sentence): pilot count starts at the first pilot-eligible delivered packet; prior lineage count reported separately.

## MF4 — repair proposed; closes (0)
- Exact primary quote: L21 and L131 now match Desk 1257 verbatim (identical to adjudication L15 and CoS 94 L28; my prior direct read of 1257 also matches). L22 explicitly withdraws the v1.3 paraphrase, no intent finding. L190 unchanged and exact. Attribution honest: writer cites parent direct-read records (CoS 94 L27–28 verified correct line refs) and states it ran no transcript search.
- Honest disclosure: L17 says writer did not re-read RSI pos-6 (cites CoS 94 L31, correct). L23 widget text marked CoS-relayed, not recovered. L29/L36/L58/L66/L74/L77/L267/L274–278/L487–496 relabel baseline and all Select-String/Test-Path results WRITER-REPORTED/UNVERIFIED with true limits (command string ≠ proof of run/output/commit bytes). L78/L279–281 limit "BOX-COPY DIGEST MATCH" to /workspace/rsi copies (I confirm those three digests) and disclose the unreconciled v1.0 commit a3ba7cb8 vs 6fd0b7f3. Closure map "Known limits" restates these. This is correct, honest disclosure; absent fresh source checks were prohibited and are not penalized.
- Not a defect: L252/L351 still state the proposed future standard "verified on disk"; v1.4 does not meet it for EVD-04–06/08 and says so (closure map limits). Acceptable for a proposed, unapplied standard.

## MF2 / MF5 / MF6 — preserved (0 each)
Unchanged bytes for §4 (L186–243), §6.1/§6.3 (L287–329), §8.1/§8.3 (L377–429), §9 (L433–455); Stripe live OFF + track-scope test mode (L95/L325) intact; §8.2 changes only add MF1 alignment (L388, L397–399).

## New material regressions
None found. No new requirement, universal overlay, gate, timeout, or approval layer. Proposed vs execution boundary intact: PLAN ONLY (L92), unapplied watch text (L379–380), read-only schema (L414–423), Phase 2–4 gated on Eric typed YES (L477–479), sign-off disclaims any change (L505).

## Non-scoring precision (no deduction)
- L385 proposed watch text still says "Before scoring any AG submission" — with a non-AG writer this reads as excluding the replacement writer's packets from preflight; suggest "any submission".
- L120 ACK/Delivery still listed as a gate (writer discloses; CoS 94 non-scoring).
- L257 filing-time tier still "baton delivery and git push" (disclosed).
- L463/L475 "PREPARED, NOT YET DELIVERED" is correct at text-finalization; delivery status is a timestamp-semantics matter, not a defect.
- L38 still labels 18325434 "HEAD of origin/p7-v8.9" though L29/L40 mark it asserted/unverified — consistent enough.
- Closure map uses "REPAIR PROPOSED — PENDING G-1" for all repairs (no self-closure claims) — correct.

## External prerequisites (not plan failures)
SAG 95+, Eric scoped typed YES, runtime adapters, TM ledger receipts, source re-verification under future authorized work.

## Advisory candidate
MF1 0, MF2 0, MF3 −1, MF4 0, MF5 0, MF6 0 → **candidate 99 (range 98–100)**, ≥95 → PASS-level for G-1 plan quality. If parent judges the MF3 pilot-cohort start ambiguity non-material, 100; if parent judges it material enough to block, it remains a one-sentence repair and is the only one I found. Counts (for parent only): this is replacement writer delivered try 1/4, documented track 7/10. Advisory makes no score, SAG request, filing, or counter change.
