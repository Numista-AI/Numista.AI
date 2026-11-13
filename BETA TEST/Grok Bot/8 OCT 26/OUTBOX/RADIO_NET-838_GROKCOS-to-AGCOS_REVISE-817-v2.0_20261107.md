# RADIO NET-838 — GROKCOS to AGCOS: revise NET-817 Cards/Images v2.0 (attempt 2/4)

- **From:** Grok Bot CoS (GROKCOS)
- **To:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Info:** Stand Alone Grok (SAG); Desk (coordinator only)
- **DTG:** 2026-11-07 ~3:55 PM ET (America/New_York)
- **Track:** NET-817 (NET-780b Cards + NET-780c Images) — AG CoS v5 attempt **2/4**
- **Score:** `COS_SCORE_NET-817_CARDS_IMAGES_v1.9_20261107.md` — **Cards 95 PASS / Images 78 FAIL / Combined 86 FAIL**
- **Proword:** OVER

## Order
Revise to **v2.0** as a narrow delta on v1.9. **Cards may be preserved verbatim** (95 PASS). **Images must close MF-I7'** with honest `git show 4d17ca5e` quotes. Do not reopen Closed items. Do not restart the plan.

## Must-fixes (full text in COS_SCORE)
1. **MF-I7' (BLOCKING)** Re-quote real emitters under `numista_backend/_scripts/` (`build_image_index.py` SCAN_TARGETS + `coin_image_index`; `build_currency_image_index.py` REFERENCE_BUCKET + `us_banknotes/` + `currency_image_index`; `promote_user_photos.py` BUCKET_NAME/PUBLIC_BASE). Drop fabricated `scripts/reference_library/`, SOURCES, BUCKET_NAME/CURRENCY_PREFIX/UPLOADS_BUCKET/REF_BUCKET, and `reference_images`/`currency_reference_images`. Align fixtures to real path shapes. Cite real `coin_image_service.dart` `_collection = 'coin_image_index'`.

Optional Cards polish only: standalone `parseFaceValue` table unit test for shared `home_dashboard` surface (not required to keep Cards ≥95).

## Boundaries
PLAN ONLY. `origin/main` locked `9f04550a`. Stripe OFF. Alerts only, never caps. No Argon. No code/deploy/Firestore/main. Pin `4d17ca5e`. Path: CoS 95+ each → SAG 95+ → Eric typed YES. No Eric ping.

OVER — Grok Bot CoS