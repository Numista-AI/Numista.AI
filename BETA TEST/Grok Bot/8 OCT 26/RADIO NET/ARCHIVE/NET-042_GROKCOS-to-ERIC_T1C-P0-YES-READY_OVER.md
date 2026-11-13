# NET-042 GROKCOS -> ERIC: T1C P0 HOTFIX ready for your typed YES
13 Oct 2026 ~4:54 PM ET. Re: NET-040 / NET-041. GROKCOS OVER -> ERIC for decision.

## What broke live
After the unified-bundle deploy, home/dashboard spot prices 401'd without CORS (Field Tester CONDITIONAL smoke). Root cause: `/api/spot_prices` missing from `_PUBLIC_PATHS` while Flutter calls it with plain `http.get` before sign-in.

## What passed on `dev`
| Item | Detail |
|------|--------|
| Commit | `d689223f` on `origin/dev` |
| Change | one line: `"/api/spot_prices"` in `_PUBLIC_PATHS` (`numista_backend/main.py`) + new cors/public-path tests |
| Gemini BUILD | `GEMINI38_REVIEW_T1C_HOTFIX_BUILD.md` (code quoted) |
| Grok score | **PASS** — NET-041; I re-ran cors/auth tests myself |
| Data risk | Non-sensitive commodity prices (yfinance); no PII |

## Your decision (OVER)
**Type YES** in chat (to Grok CoS or AG) to cherry-pick **only** the `main.py` + test hunks from `d689223f` onto a branch from `main`, then deploy. **Not** a full `dev` merge.

Until YES: no deploy / live writes.

## After YES
AG CoS wilco cherry-pick + deploy + smoke. Then continue P1 (Flutter web build / Hosting), P2 (Morgan Undo, onSnapshot), and confirm P3 home blank cleared. Systemic note in NET-041: middleware 401s still lack CORS — audit unauthenticated Flutter calls vs `_PUBLIC_PATHS`.

## Parked
- **F1 RERUN6**: AGCOS ITERATE (NET-038 fabricated 22WP/23WP/24WP) — under 2h since 4:34 PM; no new stall flag.
- **CREDIT500**: still WAIT-OUT (low pri).

Baton: `BATON_T1C_HOTFIX-PR258_ERIC_OVER.md`

No live deploy from this NET. OVER
