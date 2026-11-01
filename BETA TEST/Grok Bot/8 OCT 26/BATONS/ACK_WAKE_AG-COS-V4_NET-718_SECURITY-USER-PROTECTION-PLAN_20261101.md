# ACK WAKE AG CoS v4 - NET-718 - SECURITY & USER-PROTECTION PLAN
**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**To:** Grok CoS, Argon (SAG Technical Auditor), Founder Eric  
**Date:** 2026-11-01 5:45 PM ET  
**Reference:** `WAKE_AG-COS-V4_NET-718_SECURITY-USER-PROTECTION-PLAN_20261101.md`  
**Status:** ACKNOWLEDGED & EXECUTED.

1. **Security Plan Completed & Filed:** `SECURITY_PLAN_NET-718_USER-PROTECTION_20261101.md` has been authored and distributed to `RADIO NET/`, `BATONS/`, `INBOX/`, `OUTBOX/`, and `For SAG/`.
2. **All 10 Spec Requirements Fully Addressed:**
   - **Item 1 (No postal addresses anywhere):** Audited `estate_models.dart`, `scan_service/main.py:695`, `estate_fiduciary_service.dart:71`. Plan eliminates `'Primary Storage / Home Safe'` default across backend & mobile models; updates CSV template in `web/add_coins.html:1332`; confirms zero postal address fields in signup schemas.
   - **Item 2 (Auto-redaction of scans):** Specifies pre-storage in-memory Document AI Specialized Invoice Parser entity detection (`ship_to_address`, `bill_to_address`, `receiver_name`, `customer_id`) + pixel-level blackout rectangles (`#000000`) before GCS write. Zero unredacted storage in temp buckets/caches. Low-confidence fallback canvas. Dedicated dry-run audit report script (`_scripts/dry_run_receipt_redaction_audit.py`) for existing AJ scans with zero writes/deletes.
   - **Item 3 (Strip EXIF/GPS):** Universal client-side HTML5 canvas re-encoding (web) & native stripping (mobile) + universal server-side Pillow backstop middleware `_sanitize_image_exif` stripping tag `0x8825` from all JPEG/PNG/WEBP/HEIC uploads while preserving orientation `0x0112`.
   - **Item 4 (Values private by default):** Deletes `"owner_email": req.user_email` from `/public_wishlists/{token}` snapshot in `main.py:12745`; strips financial values by default; adds privacy masking mode to Attorney Portal (`attorney_portal_screen.dart:520, 704`); display names default to "Numista Collector".
   - **Item 5 (2FA prompted above threshold):** Firebase Auth Identity Platform TOTP Multi-Factor Authentication prompt above collection FMV threshold (`$5,000` baseline example) [ERIC DECISION]; unconditionally mandatory for Aunt Janet account.
   - **Item 6 (Rules audit & emulator tests):** Identified cross-user read gap in `firestore.rules:190` (`family_groups/{groupId}`); replaced with strict membership rule. Designed 6-point automated emulator test suite (`firestore_storage_security.test.ts`).
   - **Item 7 (Secret Manager & key scan):** Verified runtime secrets in Secret Manager; planned `gitleaks` and `trufflehog` full git history scan; detailed 5-step operational key rotation protocol.
   - **Item 8 (Meta pixel event safety):** Reconciled with NET-706 R5: Pixel sends events only (`PageView`, `CompleteRegistration`, `InitiateCheckout`, `Purchase`), zero user PII, zero coin metadata/cert numbers, zero collection FMV valuations. Software tier price only for Purchase attribution [ERIC DECISION].
   - **Item 9 (Data minimization):** Designed `DELETE /api/user/account` workflow (Auth + Firestore + GCS + Stripe cleanup); 14-day Cloud Logging retention; logger email/PII masking.
   - **Item 10 (Site copy proposal):** Formulated plain-language security promise for Landing Page, Privacy Policy, and Estate Planning screens [ERIC DECISION].
3. **Turn & Baton Passed:** Baton passed to Grok CoS & Argon for scoring ($\ge 95$ threshold): `BATON_NET-718_GROKCOS-ARGON_SECURITY-PLAN-REVIEW_20261101.md`.
4. **Queue Continuity:** AG CoS v4 advances immediately to **NET-647 R2.8.10 Mint FAIL-FIX Plan**, followed by **NET-705 US Catalog Site Plan**.
