# NET-474 GROK CoS -> ARGON, AG CoS: DEMO A THEN B, PROCEED (OVER)

**Date:** 24 Oct 2026
**Demo convo:** e44c3575-a82a-41fe-b478-0911c5fbc3f7

## APPROVAL
Eric approved through AG CoS relay: "Plan approved. Proceed with Target A first, then Target B."

1. **Target A goes FIRST.** File: numista_mobile/lib/services/batch_valuation_service.dart
   - currency write path: write to currencyPath, not coinsPath
   - also write the Golden Schema 'AI Estimated Value' field
   - fix the resume progress math
2. **Target B goes SECOND.** File: numista_backend/services/transfer_service.py
   - privacy sanitize: also strip Golden Schema and paper_trail fields
   - delete ghost pending archive docs on a partial claim
   - keep the sender's full archive (no overwrite with the sanitized copy)

## BUDGET
Max about $10 in AI spend. Use local tests first (mocked Firestore).

## RULES (Rule 1 / 6a / 8)
- Pure LF line endings. Write the tests. Check that every test exits 0 (pytest, flutter test, flutter analyze).
- Commit files by explicit path only. Push to origin/dev.
- **NO live deploy. NO merge to main.**

## DECONFLICT
- The P7 QTY one-fix (2x should become QTY 2, after the NET-473 PARTIAL FAIL) is a **SEPARATE track**. Do not put it in the A or B commits.
- If AG CoS is busy with QTY, finish the QTY plan and build first, or use a separate worktree. **Do not block QTY.**

## ROLES
- Argon: thinking and review only, for the A plan and then the B plan.
- AG CoS: does the coding, on **Flash Low only (no Claude)**.

OVER