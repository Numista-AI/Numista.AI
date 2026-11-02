# BATON NET-736 — AG CoS — NET-647 R2.8.14 FIX-ONLY
**From:** GB CoS  **To:** AG CoS  **Date:** 2026-11-02  **Status:** CLOSED (Plan R2.8.14 filed, handoff to BATON_NET-737)
**Source:** RADIO NET\SAG_REVIEW_NET-647-R2.8.13_72_REVISE.md
**Supersedes:** BATON_NET-735 (CLOSED — SAG 72 REVISE governs over GB CoS 96)

## Rules
- DOCS ONLY: no code changes, no builds, no deploys. Push nothing except docs to p7-v8.9.
- Every count, path, size and MD5 must come from a real command with its output embedded. Nothing invented.
- main locked 9f04550a; Stripe OFF.

## MUST-FIX
1. **Row 28:** §4 table has primary/fallback swapped vs §3.1 code and test. In code, the 2023 composite JPGs are PRIMARY; 23rh_b.webp / 23rh_c.webp are FALLBACKS. Fix the table.
2. **Path counts:** body says 95/97 live, §4.1.3 says 104/108, MF3 says 104 found. Produce ONE source-of-truth list (command + output) including SemiQ-Half-Dollar-Obverse-Unc-P.jpg, the 2013-S, 2018-D, 2019-D, 2020-D ATB obverses, and 26rj_a.webp. Use that count everywhere.
3. **User-upload guard:** must match the numista-uploads-studio-9101802118-8c9a8/users/ paths used in Row 11 so microscope photos can never be overwritten. Also fix the Row 10 table to match the code (returns null).
4. **§8 tracker:** make it match §3.1 for B26-1, 2, 6, 13, 15–19, 22–26.
5. **extractSku:** must NOT use Personal Notes for theme matching.
6. **Mayflower P:** must not fall back to the D obverse (no cross-mint fallbacks). A half dollar with no mint mark gets a P SKU and the P image, consistently.

## SHOULD-FIX
- Footer: **END PLAN R2.8.14**.
- One consistent test count (42 vs 43).
- Remove fallbacks byte-identical to their primary (prove with MD5 output).
- West Point **W** must not be classified as S.
- Tests must exercise the §3.1 code itself, not a copy.
- Gate 6 cites dev **01a03f90**.
- Before YES: verify Rows 08, 09, 18, 19 against live Firestore (read-only, output embedded).

## Pass bar
95 from GB CoS, Argon and SAG. Then Eric's typed YES before any EXECUTE.

## Return
File FAILFIX_PLAN_NET-647_R2.8.14_20261102.md + RADIO_OVER to RADIO NET and Grok CoS INBOX.

## STALL FLAG - 2026-11-02 12:45 PM ET (Grok CoS handoff watch)
Baton opened 10:36 AM ET; unmoved ~2h09m (>= 2 working hours). Last AG activity: WHOSE_TURN.md 11:51 AM (R2.8.14 work underway). No FAILFIX_PLAN_NET-647_R2.8.14 filed yet. WAKE_AGCOS_NET-736-STALL_20261102-1245.md filed. Live 200/200/404. Next re-flag no sooner than 1:45 PM ET.



## Handoff
CLOSED 2026-11-02 13:45 EST by AG CoS v4. FAILFIX_PLAN_NET-647_R2.8.14_20261102.md filed. Handed off to BATON_NET-737.
