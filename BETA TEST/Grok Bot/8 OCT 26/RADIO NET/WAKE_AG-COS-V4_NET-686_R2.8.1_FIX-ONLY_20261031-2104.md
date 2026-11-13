# WAKE_AG-COS-V4_NET-686_R2.8.1_FIX-ONLY (20261031-2104)
FROM: GB CoS. Plan only. Full Review Cycle.

Argon scored R2.8 89 REVISE (GEMINI38_REVIEW_NET-647_R2.8_2026-10-31.md / NET-685). File a fix-only FAILFIX_PLAN_NET-647_R2.8.1 that folds in Argon MUST-FIX 1-6 verbatim.

Fixes to fold in:
1. Full 252-item audit, including Argon's 13 non-2026 wrong-image items (Kansas/Arkansas substring, ATB 'mount'/'island'/'river'/'cumberland' token steals, the 1962 Lincoln, San Antonio Missions, the 5 ATB obverse files, and the 4 items with OBV=None). Fix the matcher with whole-token, exact-name and year matching, and add a regression test that includes Kansas vs Arkansas.
2. The 2026 canonical override must apply even when the URL is non-null (the 5 docs listed), unless the image is a /users/ or /microscope/ upload. Fix the swapped 2023 ASE obverse/reverse files, which are verified by MD5. Add the year-less Peace Reverse Proof file and the 3 SemiQ dime files to the --no-clobber upload list. List every object before upload.
3. Quote review_hub_screen.dart 2040-2058 verbatim. Use the stored unit_cost first, then a ROUND_HALF_UP divide.
4. E4a: add the Title-Case keys, 'Cost', and paper_trail.purchase_price.
5. E4b: use the existing _conditionLabel.
6. Cite _CollectionCardImage at 6358-6360. Limit the year-guard regex to the decoded filename basename, with dimensions stripped.

Keep Section 8, the 39/39 tracker matrix.
State how existing pre-fix docs display, and prove image paths resolve on p7-gate.
No writes to Eric's account without his separate typed YES.
Locks are unchanged. The 3 AM stand-down applies.
