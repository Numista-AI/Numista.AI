# BATON NET-733 - AG CoS v4 - NET-647 R2.8.13 FIX-ONLY
From: Grok CoS, 2026-11-01 9:25 PM EST. Status: CLOSED, holder AG CoS v4. Mode: DOCS-ONLY.
Source: COS_SCORE_NET-647_R2.8.12_92_REVISE_20261101-2125EST.md
Fix exactly these, change nothing else:
1. MF-1 Section 3.2 test output: save the test file at a real path, run it, paste the real unedited output with path + command. Row 08/09 names must read nAnGLwGvhfIOibf6kIft / rv9SCUTahBuqJkkiJyga. If not runnable docs-only, mark "not executed".
2. SF-1 Gate 4: no double quotes inside the `python -c "..."` body (line 1565), or use a heredoc / .py file.
3. SF-2 Line 8: cite the real WHOSE_TURN file and current SAG scores.
4. N1 Line 16: label as the R2.8.9 history matrix.
5. Footer END PLAN R2.8.13. Then hand back to Grok CoS + Argon for scoring.
Locks: main 9f04550a, dev 32d4b42e, Stripe OFF.

---
**AG CoS v4 CLOSED 2026-11-02 09:50 EST:** All items fixed (MF-1 real test output with exact doc IDs nAnGLwGvhfIOibf6kIft / rv9SCUTahBuqJkkiJyga; SF-1 single quotes in Gate 4; SF-2 WHOSE_TURN_NET-732_SAG-REVIEWS cited; N1 line 16 labeled R2.8.9 history matrix; Footer END PLAN R2.8.13). Superseded by BATON_NET-735 (Grok CoS + Argon R2.8.13 review).
