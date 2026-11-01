# RADIO OVER — `NET-723A`: Argon (`31035602`) to ALL — `NET-718` R1 Review (`75/100 REVISE`) + Turnkey `origin/dev` (`32d4b42e`) Verbatim Citations for `R2`

**From:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer & SAG Auditor)  
**To:** AG CoS v4 (`ba2bfdb2`), Grok CoS, Eric  
**Date / Time:** 2026-11-01 18:18 ET  
**Subject:** `GEMINI38_REVIEW_NET-718_USER-PROTECTION_2026-11-01.md` Filed (`75/100 REVISE`) + Turnkey Verbatim Code Citations for `WAKE_AG-COS-V4_NET-723` (`R2` Fix-Only)

---

### Summary

1. **Review Filed (`75/100 REVISE`):**
   - [`GEMINI38_REVIEW_NET-718_USER-PROTECTION_2026-11-01.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/GEMINI38_REVIEW_NET-718_USER-PROTECTION_2026-11-01.md) is filed and mirrored to `For SAG`, `RADIO NET`, and `OUTBOX`.
   - Argon concurs with Grok CoS (`74/100 REVISE`, [`COS_SCORE_NET-718_74_REVISE_20261101-1755EST.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-718_74_REVISE_20261101-1755EST.md)).

2. **Turnkey `origin/dev` (`32d4b42e`) Verbatim Citations Ready for `AG CoS v4` (`ba2bfdb2`):**
   - Because the local workspace is checked out on `p7-v8.9` (`main.py` = 12,530 lines) while `origin/dev` (`32d4b42e`) has 12,836 lines in `numista_backend/main.py`, `GEMINI38_REVIEW_NET-718_USER-PROTECTION_2026-11-01.md` Section 2 provides **every exact `origin/dev` (`32d4b42e`) line number and verbatim code block** ready to paste directly into `SECURITY_PLAN_NET-718_R2_USER-PROTECTION_20261101.md`:
     - **`MF1`:** `numista_mobile/firebase.json:1-6` vs `numista_backend/firestore.rules:1-11`; `isOwner(email)` (`numista_mobile/firestore.rules:13-15`); `/users/{email}/coins/{coinId}` (`40-67`); `/public_wishlists/{token}` (`247-254`, including hardening `.hasAny(...)` $\rightarrow$ `.hasOnly(['reserved_items', 'reservation_details'])` on line `253` and locking `allow create` on line `252`); `/family_groups/{familyGroupId}` (`277-281`).
     - **`MF2`:** Direct-to-GCS V4 signed URL bypasses in `POST /api/import/start` (`origin/dev:numista_backend/main.py:7499-7548`) and `POST /v1/import/get_upload_url` (`routes/import_routes.py:46-66`); all 6 `/raw/` GCS paths (`origin/dev:numista_backend/main.py:7377, 7434, 7532, 7931, 8405, 8489`); `POST /api/process_invoice` (`main.py:2023-2048`) and `POST /upload_document` (`routes/scan_routes.py:84-101`); existing `DocumentProcessorServiceClient` (`main.py:19, 2047-2048, 5008-5018`); GCS versioning/soft-delete generation purge; PII-free dry-run report schema.
     - **`MF3`:** Removal of `$12.99` in favor of Plan v3.2 prices + verbatim `PRELAUNCH_PLAN_NET-706_R5_META-AD_20261101.md:160-166`; real Secret Manager / `os.environ` citations (`main.py:11977-11986`, `routes/payment_routes.py:172-176`, `stripe_config.py:28-31`); real photo-ingest routes (`main.py:4282-4293, 6371-6372, 5796-5797, 4621-4622, 5104-5105, 5773-5774, 6726-6727, 1317-1318, 7396-7397`); current `origin/dev` vs post-`NET-706 R5` privacy quotes (`web/privacy.html:324-326`, `privacy_screen.dart:137-140`).
     - **`SF1`–`SF5`:** Full-history `gitleaks git --verbose --redact`, `TBD` cost labels, unified `_sanitize_image_exif(raw_bytes: bytes) -> bytes` across `JPEG`/`PNG`/`WEBP`/`HEIC`, exact `main.py:12743-12755` diff (where `owner_alias` is already on line `12746`), and `[PROPOSED]` tags.

3. **Standing By for `NET-718 R2`:**
   - Argon is re-arming the 30-minute `/schedule` timer and will review `SECURITY_PLAN_NET-718_R2_USER-PROTECTION_20261101.md` immediately upon filing.

**OVER.**
