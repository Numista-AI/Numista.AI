# COS_SCORE_T1C_HOTFIX_DEPLOY (Grok CoS, 13 Oct 2026 ~5:15 PM ET)

Verdict: **PASS — T1C P0 deploy verified live. Baton already CLOSED_OUT.**

## Method check (cherry-pick, no full dev merge)
- PR #259 merged 13 Oct 2026 21:06:26Z — title "T1C P0: spot_prices public (Eric YES 13 Oct)".
- Merge SHA: `d3f7a2cddbcc2b7f32ece5384317c7de73b324fc`.
- Source fix: `d689223f` / cherry-pick `426d1d36` (main.py + test_cors_public_paths.py only for code). Matches Eric YES + NET-044 surgical rule.

## Independent live smoke (Grok CoS, EDS_Laptop, ~5:15 PM ET)
| URL | Code | Note |
|-----|------|------|
| GET https://numista.ai/api/spot_prices (no auth) | 200 | Gold/Silver/Platinum/Palladium JSON |
| OPTIONS https://numista.ai/api/spot_prices | 200 | ACAO=https://numista.ai |
| GET https://numista.ai/api/programs (no auth) | 401 | default-deny intact |
| GET https://numista.ai/api/collection_inventory (no auth) | 401 | default-deny intact |
| GET https://numista.ai/ | 200 | home loads |

Matches AG DEPLOY_DONE_T1C_HOTFIX + NET-045.

## Board
- BATON_T1C_HOTFIX-PR258_CLOSED_OUT.md — keep.
- Duplicates AGCOS_WILCO / ERIC_OVER already in `_STALE_RESURRECTED_13OCT` (NET-046).
- No Eric decision pending on T1C.

## Next (AG, per NET-046 — ACK)
1. F1 RERUN6 ITERATE — real Wayback for 22WP/23WP/24WP; rename baton to AGCOS_WILCO when fetching so the watch sees the move.
2. T1C P1–P3 on dev (nav/cache, Morgan Undo, onSnapshot, home blank re-check).
3. Systemic CORS / `_PUBLIC_PATHS` audit (NET-041 note).
4. CREDIT500 still WAIT-OUT after F1.

OUT
