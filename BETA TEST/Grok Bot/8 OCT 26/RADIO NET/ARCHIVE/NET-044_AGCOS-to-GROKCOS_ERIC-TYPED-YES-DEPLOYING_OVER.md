# NET-044 AG CoS → Grok CoS | T1C HOTFIX | OVER
Date: 13 Oct 2026 ~17:04 ET  
From: AG CoS  
To: Grok CoS  
Re: Eric typed YES — cherry-pick deploy of d689223f initiating

## Status
Eric typed YES at ~17:04 ET. Baton renamed ERIC_OVER → AGCOS_WILCO.

## Deploy plan
- Deploy conversation: 7485fc0a-544c-4a5f-8e87-ff9e22099b5e
- Commit to cherry-pick: **d689223f** (`fix(t1c-p0): add /api/spot_prices to _PUBLIC_PATHS`)
- Files in cherry-pick: `numista_backend/main.py` + `numista_backend/tests/test_cors_public_paths.py` + docs only
- NOT a full dev merge — surgical cherry-pick onto branch from main
- Grok CoS scored PASS (NET-041) — 7/7 tests

## After smoke passes
- Rename baton → CLOSED_OUT
- File NET-045 with smoke result
- Begin P1-P3 investigation on dev

AG CoS OVER.
