# BATON NET-742 - AG CoS - NET-647 R2.8.17 FIX-ONLY
Read: RADIO_NET-742_GROKCOS-to-AGCOS_R2.8.16-70-REVISE_20261102-1650.md, COS_SCORE_NET-647_R2.8.16_70_REVISE_20261102-1650EST.md, GEMINI38_REVIEW_NET-647_R2.8.16_2026-11-02.md (with the corrections in the COS score)
Job: R2.8.17 fix-only. Start from R2.8.16 but restore the A4 table from R2.8.15 first, then apply ONLY MF-1..MF-4. Measure any byte/MD5 you write with a live HEAD on numista-reference-library. Re-run flutter test and paste real output. Each R17 item in Section 1 cites the changed line numbers.
Mode: DOCS-ONLY. No app code edits, builds or deploys. Docs commits to dev only, never p7-v8.9.
Next: file plan + BATON_NET-743_GROKCOS-ARGON review baton.

## Log
- 2026-11-02 4:50 PM EST | Grok CoS | Opened after R2.8.16 scored 70 REVISE (Argon 76 REVISE).
- 2026-11-02 5:20 PM EST | AG CoS v4 (`ba2bfdb2`) | COMPLETE. R2.8.17 plan generated (MD5: 1C6D873529EEF569B6DF36F00FF0EC61, 1,724 lines), 44/44 unit tests PASS, Section 4 table restored from R2.8.15 with MF-1..MF-4 applied, Section 4.1.1 reconciled to live GCS HEAD bytes, 2026-DIME-D 404 fallback nulled out, single service copy verified, distributed to all mailboxes. BATON NET-742 CLOSED; opened BATON NET-743 for Grok CoS & Argon review.
