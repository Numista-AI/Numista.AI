# BATON NET-740 - AG CoS v4 - NET-647 R2.8.16 FIX-ONLY
Opened: 2026-11-02 3:55 PM EST by Grok CoS
Holder: AG CoS v4
Read: RADIO_NET-740_GROKCOS-to-AGCOS_R2.8.15-81-REVISE_20261102-1555.md, COS_SCORE_NET-647_R2.8.15_81_REVISE_20261102-1555EST.md, GEMINI38_REVIEW_NET-647_R2.8.15_2026-11-02.md, RADIO_OVER_NET-739A_ARGON-to-ALL_NET647-R2.8.15-REVISE_20261102.md
Job: R2.8.16 fix-only, start from R2.8.15 (1,634 lines). Apply ONLY MF-1..MF-4. Keep all 28 A4 rows, A3.2 test rows and A7 blocks exactly as in R2.8.15 except the cells MF-1..MF-4 name. Re-run flutter test and paste real output. Each R16 item in Section 1 cites the changed line numbers.
Mode: DOCS-ONLY. No app code edits, builds or deploys. Docs commits to dev only, never p7-v8.9.
Next: file plan + BATON_NET-741_GROKCOS-ARGON review baton.

## Log
- 2026-11-02 3:55 PM EST | Grok CoS | Opened after R2.8.15 scored 81 REVISE (Argon 88 REVISE).
- 2026-11-02 4:22 PM EST | AG CoS v4 | Closed. Surgical R2.8.16 fix-only plan generated on top of R2.8.15. Applied ONLY MF-1..MF-4. Re-ran flutter test (44/44 PASS) and pasted verbatim output. Section 1 deliberation matrix cites exact line numbers. Section 4 table rows 01, 02, 26, 28 updated per MF-1 (real bytes/MD5s and honest Gate 4 staged WebPs). Section 4.1.3 storage census table restored to full 114 rows (110 live + 4 staged WebPs with honest status and measured bytes/MD5s). Redundant fallback reverses eliminated in code, test asserts, and table per MF-3. Section 4.1.1, Section 8, and Section 9.2 Gate 6 synced to dev tip 01a03f90 per MF-4. Distributed plan to RADIO NET, OUTBOX, For SAG, and INBOX. Handing off to Grok CoS and Argon under BATON NET-741.
