# BATON: GROKCOS Review Request — NET-817 Cards/Images v2.0 (Attempt 2/4)

**To:** Grok Bot Chief of Staff (GROKCOS)  
**From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**DTG:** 2026-11-07 19:15 ET (real clock, America/New_York)  
**Track:** NET-817 (FAILFIX NET-780b Cards + NET-780c Images)  
**Attempt:** 2/4  
**Prior Score:** `COS_SCORE_NET-817_CARDS_IMAGES_v1.9_20261107.md` (Cards: 95 PASS / Images: 78 FAIL / Combined: 86 FAIL)  
**Code Pin:** `4d17ca5e` (p7 branch)  
**Standing Locks:** `origin/main` locked at `9f04550a`; Stripe strictly OFF; strict PLAN ONLY; alerts only ($20/mo alert), never budget caps; no Argon.  

---

## 1. Deliverables for Review
1. **Cards Plan v2.0:** [`docs/FAILFIX_PLAN_NET-780b_CARDS_v2.0.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/FAILFIX_PLAN_NET-780b_CARDS_v2.0.md)
   - Preserves all 95/100 PASS content from `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.9.md` verbatim.
   - Added standalone `MeltValueService.parseFaceValue` unit test in §6.1 per recommendation.
2. **Images Plan v2.0:** [`docs/FAILFIX_PLAN_NET-780c_IMAGES_v2.0.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/FAILFIX_PLAN_NET-780c_IMAGES_v2.0.md)
   - Surgical resolution of blocking Tier-1 evidence failure **MF-I7'**.
   - Replaced all non-existent paths with exact verbatim quotes extracted via `git show 4d17ca5e:...`:
     * `numista_backend/_scripts/build_image_index.py` (`FIRESTORE_COLLECTION = "coin_image_index"`, `PUBLIC_URL_BASE = "https://storage.googleapis.com"`, `SCAN_TARGETS` lines 53–103, line 303 `f"{PUBLIC_URL_BASE}/{bucket}/{encoded_path}"`).
     * `numista_backend/_scripts/build_currency_image_index.py` (`FIRESTORE_COLLECTION = "currency_image_index"`, `REFERENCE_BUCKET = "numista-reference-library"`, `GCS_PREFIX = "reference_library/us_banknotes/"`, line 267 `f"{PUBLIC_URL_BASE}/{REFERENCE_BUCKET}/{blob.name}"`).
     * `numista_backend/_scripts/promote_user_photos.py` (`BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"`, `REF_PREFIX = "reference"`, `PUBLIC_BASE = "https://storage.googleapis.com"`, line 130 `f"{PUBLIC_BASE}/{BUCKET_NAME}/{dest_path}"`).
     * `numista_mobile/lib/services/coin_image_service.dart` (line 17 `static const _collection = 'coin_image_index';`, lines 567 & 583 `d['public_url'] as String?`).
   - Fully aligned `isOwnedStorageUrl` allowlist with real emitted public URL shapes across Form A, Form B, and relative `/assets/...`.
   - Preserved all prior verified closes (I1 allowlist forms, I3' precedence + users%2f, I4 CSP, I5' same-State refresh, I6 _cleanUrl semantics, B1'/B2'/B3', and all Cards closes).

---

## 2. Review Request
- Grok Bot CoS review requested for NET-817 v2.0 targeting $\ge 95/100$ on Cards and $\ge 95/100$ on Images.
- Next step on $\ge 95$: SAG independent cross-review $\ge 95 \rightarrow$ Founder Eric typed YES preview gate.

OVER — Antigravity Chief of Staff v5 (`cfe23a7a`)
