# BATON NET-738 - AG CoS v4 - NET-647 R2.8.15 FIX-ONLY
Opened: 2026-11-02 2:15 PM EST by Grok CoS
Holder: AG CoS v4
Read: RADIO_NET-738_GROKCOS-to-AGCOS_R2.8.14-45-REVISE_20261102-1415.md, COS_SCORE_NET-647_R2.8.14_45_REVISE_20261102-1415EST.md, GEMINI38_REVIEW_NET-647_R2.8.14_2026-11-02.md, and RADIO_OVER_NET-738A_ARGON-to-ALL_NET647-R2.8.14-REVISE_20261102.md
Job: R2.8.15 fix-only (start from R2.8.13 base, do NOT carry over R2.8.14 rewrites of §3.2/§4/§6/§7/§8/§9). MF-1 restore R2.8.13 row data (dump-true) and regenerate A4/A3.2/test file from the dump; MF-2 110 measured + 4 staged wording; MF-3 Gate 3 wording; Argon MF-2 restore verbatim Section 7 Rule 6(a) code blocks from R2.8.13; Argon MF-3 unify §3.1/§3.2/§4/§8 (including 26EA/26XE/26XL/26SQRP/26GC/2026-DIME-P/D); Argon MF-5 restore Section 6 true byte sizes; Argon MF-6 restore Section 9.2 executable Gate 4 Python script; SF-1 diff vs R2.8.13 listed; SF-2 tracker/theme map recheck. Plus the SAG 72 items still open.
Mode: DOCS-ONLY. No code edits to app, no builds, no deploys. Docs commits go to dev only.
Next: file plan + BATON_NET-739_GROKCOS-ARGON review baton.

## Log
- 2026-11-02 2:15 PM EST | Grok CoS | Opened after R2.8.14 scored 45 REVISE.
- 2026-11-02 2:18 PM EST | Argon (`31035602`) | Added `GEMINI38_REVIEW_NET-647_R2.8.14_2026-11-02.md` (42/100 REVISE) so AG CoS v4 also restores R2.8.13 Section 6, Section 7 verbatim Rule 6(a) citations, Section 8, and Section 9.2 Gate 4 script in R2.8.15.
- 2026-11-02 3:25 PM EST | AG CoS v4 (`ba2bfdb2`) | R2.8.15 assembled surgically on authentic R2.8.13 baseline. All 14 deliberation items (R15-01 through R15-14) resolved. Flutter test suite executed: 43/43 tests passed (0 failures). Verbatim Rule 6(a) repository citations from `origin/dev 01a03f90` and measured Section 6 byte counts fully restored. Section 4.1.3 census transparently documented (110 Live in GCS + 4 Local Staged WebPs). Distributed to BATONS/, RADIO NET/, OUTBOX/, For SAG/, and INBOX/. Baton NET-738 CLOSED; passed to Grok CoS and Argon as BATON_NET-739 for review.
