# NET-029 GROKCOS to AGCOS: T1B V2 + T3b V4 PASS; T1 CLOSED; T3 F1-F2 REOPENED; F1 STALL REFRESH (13 Oct ~2:45 PM ET)
Re: NET-028. GROKCOS OVER.

Commit scored: `39125bac` on `origin/dev`. Dev-only. No live deploy.

## Scores
| Track | Verdict | Doc |
|-------|---------|-----|
| T1B V2 | **PASS** on dev | `COS_SCORE_REQ031B_BUILD_V2.md` |
| T3b V4 | **PASS** on dev | `COS_SCORE_REQ032B_BUILD_V4.md` |
| T1 remnant | **CLOSED/OUT** | `COS_SCORE_REQ031_REMNANT_CLOSED.md` |

## My verification
- pytest: **494 passed** (14.42s); auth walk `test_default_deny_auth.py` **20/20**.
- Emulator (Java 21 Temurin): **38/38** firestore.rules.test.js.
- Middleware full JWT verify at main.py:196; IDOR on subaccounts + attorney link; admin Depends on brain/cron/config/scraper/greysheet/batch routes; deep_dive `except HTTPException: raise` at :3407.
- Mobile rules: five server-only subcollections excluded + explicit write:false. Backend mirror still drifts (missing coins/profile exclusions) — follow-up only; deployed file is mobile.

## AG action now (OVER)
**T3 F1-F2** — baton `BATON_T3_REQ032-UX_AGCOS_OVER.md`. Missed fold into 39125bac. Still in login_screen.dart FreeScanPreviewScreen: fontSize 11/12/13 at :1250, :1299, :1301, :1360, :1394, :1395. Bump to textBodySm or >=14 + test; add email->tap PIN->keys widget test. Pass baton back to GROKCOS. **One Eric YES for T1B+T2+T3+T3b waits on this** (or Eric ships without F1-F2).

## Parked / stalled
- **T2** remains AGCOS WAIT-OUT (V3 PASS; one-YES bundle).
- **F1 RERUN6** STALL REFRESH: AGCOS OVER unmoved since 12 Oct 5:07 PM ET (AWQ dry-run + apply). Queued behind T3 F1-F2.
- **CREDIT500** still WAIT-OUT low-pri; T1B no longer blocking — pick up when capacity.
- Pre-deploy: confirm Eric Firebase `admin: true` claim read-only before YES.

## Batons this run
- `BATON_T1B_REQ031B_CLOSED_OUT.md`
- `BATON_T3B_ALT-SITE_CLOSED_OUT.md`
- `BATON_T1_REQ031_CLOSED_OUT.md`
- `BATON_T3_REQ032-UX_AGCOS_OVER.md` (reopened)
- T2 / F1 / CREDIT500 logs updated

No ERIC baton yet. No deploy. OVER
