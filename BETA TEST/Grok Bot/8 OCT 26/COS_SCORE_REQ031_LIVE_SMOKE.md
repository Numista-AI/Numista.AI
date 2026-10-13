# COS SCORE - T1 REQ_031 LIVE SMOKE (FT_SMOKE_REQ031_LIVE.md, prod 463150c1 / PR #256)
Scored by: Grok CoS, 12 Oct 2026 ~8:05 PM ET.

## Verdict: PASS. Live sign-in lockdown works; no rollback needed.
- FT: "All four checks PASS on the screens. The scanned coin went into grokbot's own account, so the wrong-account risk did not happen." Total Coins 313 at start and end; test coins deleted.

## FT's open question, answered from code
FT: "A direct unauthenticated POST to `/api/identify_group_photo` returned **422** (missing fields), not **401**."
- The 422 is FastAPI rejecting the missing form fields before the handler runs (main.py:5351 `user_email: str = Form(...)`, :5352 `image: UploadFile = File(...)`). Nothing is read or analyzed.
- With the fields present and no token, the first line in the handler is main.py:5368 `owner_key = _authenticate_request(authorization, user_email)`, which raises 401 (main.py:2897-2898). So it fails closed.
- Small bug: that 401 is caught by main.py:5506 `except Exception as e:` and returned as **500** (`status_code=500`, :5509). The app would show "Failed to analyze group photo" instead of "please sign in again". Fix: add `except HTTPException: raise` before :5506, and grep every endpoint for the same `_authenticate_request` inside `try/except Exception` pattern (systemic rule). Not urgent; bundle with the next backend deploy.

## Other FT findings routed
- Review Hub: single-coin scan offers only "Save separately" and skips Review Hub. Not a REQ_031 problem; test Review Hub routing with an invoice scan in the T3/T3b smoke.
- Ask Morgan greeting says "312 coins" vs Dashboard 313 (pre-existing count mismatch). Ticket for AG; same family as the set-expansion counting rules.

Ball: T1 to AG CoS for the 500-vs-401 follow-up (dev only, no deploy without Eric's typed YES).
