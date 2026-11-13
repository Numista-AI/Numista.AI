# COS SCORE - P7 GATE V8.18.13 (p7-v8.9 @ a4a77e4c, parent 68c03e45) - FAIL (NET-394 not built)
Scored by GROKCOS, 2026-10-21 ~8:45 AM ET. AG NET-395, GEMINI38 PASS. Live untouched.

## Coverage
- NET-393 (UX V5): 5 of 5 items in the diff - neutral heading (add_coins_hub ~2796), friendly webcam error + [Upload a photo instead] (camera_capture_service_web.dart), tap targets >=48 / 18px text (add_coins_hub, base_layout), specific not-found card, CACG OCR investigation (cert_routes.py prompt + keep typed cert/prefill). Needs UX re-gate.
- NET-394 (FT a-f): 0 of 6. NET-395 section 3 says the commit "strictly resolves the 5 UX Gate V5 blockers". Diff confirms: no numista_backend/main.py change, no import/quantity/sets/dedup/condition code. (d) only partially touched: photo-label year prefill, not the manual save path that lost year+cert.

## Tests (clean worktree at a4a77e4c)
- flutter analyze: 0 errors/warnings, 2 infos. flutter test: 609 passed.
- pytest: 587 passed, 4 failed (same 4 pre-existing failures as 65072e6f/68c03e45).

## Preview: NOT REFRESHED
gcloud and firebase CLI credentials on EDS_Laptop expired ("Reauthentication failed"). Backend p7gate deploy and hosting channel deploy did not run. https://numista-vault--p7-gate-8avtpz22.web.app still serves V8.18.12 (backend 00476-hol). Eric must run `gcloud auth login` and `firebase login --reauth` on EDS_Laptop, then rerun the p7gate deploy.

## Rules: no firestore.rules change in this commit. beta_feedback owner-list extra still present (noted, untouched).

## Verdict: FAIL. Next: NET-400 -> AG builds V8.18.14 with NET-394 a-f only. UX may re-gate the NET-393 items once the preview is refreshed.
