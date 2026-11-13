# BATON NET-750: AG CoS v4, NET-748 FAILFIX v2, FIX-ONLY, PLAN ONLY (from Antigravity Desk, 3 Nov 2026 10:45 AM ET, at GB CoS's request)
**AG's 2nd and FINAL try. Attempt 9 of 10.** If v2 fails review, GB CoS or SAG takes over (Eric's rule).
NO EXECUTE. No code, commits, or deploys.
- Input: INBOX\GEMINI38_REVIEW_NET-748_AG_v1_2026-11-03.md (Argon 78 REVISE, 5 must-fixes) and FAILFIX_PLAN_NET-748_AG_v1.md.
- v2 must:
  1. Close all 5 must-fixes. MF-1: match on whole words or the denomination field, NEVER a "cent" substring (that also catches "25 cents" and "semiquincentennial").
  2. Diff cleanly against v1, with no out-of-scope changes. Include a v1-to-v2 change list.
  3. Cite a source for every SKU (incl. 26SQRP) and every image mapping. Nothing invented.
  4. Put the firestore.rules change in its OWN separate step. Rules are project-wide and reach the LIVE site, so that step needs Eric's separate explicit YES. It is NOT preview-only. Keep it read-only and narrow.
- Review: Argon, then GB CoS 95+, then SAG, then Eric's typed YES.
- Locks: main 9f04550a, live untouched, Stripe OFF.
- Output: INBOX\FAILFIX_PLAN_NET-748_AG_v2.md, plus a note in WHOSE_TURN.md.
