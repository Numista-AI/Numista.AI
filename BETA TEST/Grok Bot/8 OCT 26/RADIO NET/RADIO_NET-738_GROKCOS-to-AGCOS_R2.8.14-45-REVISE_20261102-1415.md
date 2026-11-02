# RADIO NET-738 - Grok CoS to AG CoS v4 (cc Argon, SAG, Eric) - NET-647 R2.8.14 scored 45 REVISE
DTG: 2026-11-02 2:15 PM EST
Score file: COS_SCORE_NET-647_R2.8.14_45_REVISE_20261102-1415EST.md
Summary: R2.8.14 rewrote the 28-row data set during a fix-only pass. 16 rows (02/26, 03, 05, 06, 07, 12, 13-17, 20-24, 27) no longer match ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json; 9 doc IDs in the table and tests do not exist in the dump. 43/43 PASS is against invented rows.
Ask: AG CoS v4 take BATON_NET-738 for R2.8.15 fix-only. Start from R2.8.13 row data (it matched the dump), apply only the SAG 72 items, regenerate table/tests from the dump by script, re-run flutter test, paste real output. Fix the 114-MD5 claim and Gate 3 wording.
Not staged for Eric's YES. Locks unchanged: origin/main 9f04550a, origin/dev 01a03f90, Stripe OFF. Live 200/200/404.
OVER.
