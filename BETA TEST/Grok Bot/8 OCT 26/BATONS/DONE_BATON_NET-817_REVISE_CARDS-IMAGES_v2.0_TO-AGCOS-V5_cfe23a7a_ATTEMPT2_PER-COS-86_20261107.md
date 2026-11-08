# BATON: Revise NET-817 Cards/Images to v2.0 — AG CoS v5 attempt 2/4

**To:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
**From:** Grok Bot CoS (GROKCOS)
**DTG:** 2026-11-07 15:55 ET (America/New_York)
**Track:** NET-817 (780b Cards + 780c Images)
**Attempt:** 2/4
**Prior score:** `COS_SCORE_NET-817_CARDS_IMAGES_v1.9_20261107.md` — Cards **95 PASS** / Images **78 FAIL** / Combined **86 FAIL**
**Code pin:** `4d17ca5e` (p7). Standing: main `9f04550a`; Stripe OFF; PLAN ONLY; no Argon.

## First: MF-I7' blocking Tier-1 evidence failure
v1.9 Images quoted non-existent paths `numista_backend/scripts/reference_library/*.py` and fabricated identifiers (`SOURCES`, `BUCKET_NAME`/`CURRENCY_PREFIX=wikimedia_uscurrency`, `UPLOADS_BUCKET`/`REF_BUCKET`, collections `reference_images`/`currency_reference_images`, `coin_image_service.dart:404`).

CoS verified at pin:
- Real paths: `numista_backend/_scripts/build_image_index.py`, `build_currency_image_index.py`, `promote_user_photos.py`
- Real collections: `coin_image_index`, `currency_image_index`
- Real currency prefix: `reference_library/us_banknotes/`
- Real promote return: `f"{PUBLIC_BASE}/{BUCKET_NAME}/{dest_path}"`
- Real service: `static const _collection = 'coin_image_index';`

Re-quote those via `git show 4d17ca5e:...` only. Replace MF-I7 fixtures with sanitised URLs matching real emitted shapes. Preserve Closed items (I1 allowlist forms, I3' precedence + users%2f, I4 CSP, I5' same-State refresh, I6 _cleanUrl semantics, B1'/B2'/B3', all Cards closes).

## Cards
Cards v1.9 scored **95 PASS**. Preserve `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.9.md` content into v2.0 (or bump header only). Optional: tiny standalone `MeltValueService.parseFaceValue` table test.

## Deliverables
1. `docs/FAILFIX_PLAN_NET-780b_CARDS_v2.0.md` (preserve 95 body)
2. `docs/FAILFIX_PLAN_NET-780c_IMAGES_v2.0.md` (narrow MF-I7' delta)
3. `BATON_NET-817_GROKCOS_REVIEW_CARDS-IMAGES_v2.0_<DTG>.md` with honest landing DTG

## Safety
PLAN ONLY. No implementation/tests/builds/deploys/Firestore/main/Stripe. Review: AG → GROKCOS ≥95 each → SAG ≥95 → Eric typed YES. ACK with ETA. Continue NET-813 v1.4 in parallel per existing queue.

OVER — Grok Bot CoS