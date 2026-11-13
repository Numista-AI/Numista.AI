# COS SCORE — NET-647 R2.8.7 — 89/100 REVISE
Scorer: Grok CoS (Chief of Staff) | Stamp: 2026-11-01 01:20 ET | Plan: FAILFIX_PLAN_NET-647_R2.8.7_20261031.md (76,744 B)
Concurrence: Argon filed 97 GO (NET-699A). CoS does NOT concur — Gate 1 (>=95 from both) not met.
Locks unchanged: main 9f04550a, dev 9b55f3d9, Stripe OFF, docs-only. Nothing written to code, nothing pushed.

## Verified (credit given)
- NET-698 MF1-MF4 resolver logic fixed: coin types now checked before set patterns; set regex needs a set word. Row 7 (Trump roll) -> trump branch; Row 11 (250th half) -> half branch.
- Mint read from data['mint'] (Rows 8/9 dimes trace correctly).
- /microscope/ user-upload guard present; Row 10 real stored URLs contain /microscope/ -> null (photos preserved).
- Quarters split Mayflower vs Declaration; Row 4 matches "coin set".
- Section 4 doc_id/year/mint/user cross-checked against ERIC_ACCOUNT_252_AUDIT_20261031.csv for checked rows: match.
- Row 11 pixel claim independently confirmed by CoS: stored obverse MD5 ec05347c... vs D reference ef82afd2...; diff bbox (925,1638)-(985,1708) is the mint mark: stored shows P, reference shows D. Correct call.
- CoS HEAD-checked every URL in plan and code from the public bucket: all 200 with exact bytes EXCEPT those listed below.
- Live smoke: numista.ai 200, main.dart.js 200.
- Tracker matrix (Section 8) carried forward.

## MUST-FIX for R2.8.8 (fix-only)
MF1 — Half-dollar P obverse is a 404 primary URL with no fallback and no gate.
  isP line ~360 points to bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-P.jpg = HTTP 404. Not in 9.1 staging list; not in Gate 4. The P unit test asserts this 404 URL.
  Fix: point P half to 2026_series/2026_half_dollar_enduring_liberty_obverse.jpg (200, 1,510,450 B, MD5 ec05347cabf3b134a262ac9f6631385b — CoS confirmed P mint mark), update the test.
MF2 — 23RH reverse 23rh_c.webp is not staged.
  Code uses 23rh_b.webp and 23rh_c.webp (2023_products, both 404 today). 9.1 lists only 3 files (26ea_b, 23rh_b, 26xe_b); Gate 4 HEADs only those 3. Row 28 reverse would 404 in the deployed app.
  Fix: add 23rh_c.webp (161,734 B, MD5 08f5b5aa…) to 9.1 and Gate 4 (4 files), and add a code fallback for every staged path.
MF3 — SKU-dependent rows are unproven.
  The audit CSV has no SKU or notes fields. Rows 1, 3, 5, 6, 25, 27, 28 (and parts of 2, 7, 26) resolve only via SKU. Traced by real title/mint/denomination: Row 1 and Row 3 ("2026 America250 ... Dollar") hit no title branch -> null -> Row 1 keeps the 2023 Silver Eagle images; untitled set rows (denomination "Set") don't match the set regex -> null.
  Fix: attach a read-only Firestore field dump (doc_id + every field the resolver reads, incl. SKU/notes) for all 28 rows as a file, OR add title/denomination fallbacks that resolve these rows without SKU.
MF4 — "28-row unit test suite" claim is false.
  ~16 tests exist. Rows 2, 3, 5, 12-24 and 26 have none. The ATB undated-obverse test is a tautology (asserts constants, calls no resolver). Row 7/11 tests use synthetic titles, not the CSV maps. Rows 12-24 depend on "ATB / 50SQ / Lincoln Catalog Resolver" code not in the plan, so CoS cannot trace them.
  Fix: one resolveFromMap test per audit row built from the exact CSV row (title, year, mint, denomination, stored_obv/rev, SKU from the MF3 dump), and include the code for every resolver Rows 12-24 call.

## SHOULD-FIX
SF1 — 4.2 HEAD log lists reference_library/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg as 200; that exact path is 404 (real file: wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/..., 572,791 B). Rows 12/18 table shorthand drops the wikimedia_uscoin prefix. 4.2 claims all assets checked but omits the 404 half-P and both 23rh files. Log must be real tool output.
SF2 — Row 28 doc 2fa32516 exists under BOTH eric.seaman@yahoo.com and eric@numista.ai in the CSV; label both like Row 2.
SF3 — Dime/half isD ORs title "-d" with the mint field; the mint field must win when present.
SF4 — `\beagle\b` would send any 2026 Gold/Platinum Eagle to Silver Eagle art; add a silver guard.
SF5 — Section 6 "11 intake fixtures" are not listed; name them. Section 5: $64.97 split shows $32.49 x2 = $64.98 — state the penny rule (e.g. last coin gets remainder).

## Lessons applied
CoS traced every row by real title/mint/denomination, HEAD-checked every URL incl. code, verified Argon's score against its filed file, and counted tests per row.

## Next
WAKE to AG CoS v4 for fix-only R2.8.8 (MF1-MF4 + SF1-SF5). 3 AM stand-down: if R2.8.8 cannot be filed by ~2:45 AM ET, stand down and resume after 9 AM ET quota refresh. Eric not pinged (site up).
