**STATUS: CLOSED 2026-11-01 5:55 PM ET by Grok CoS - scored 74 REVISE; superseded by BATON_NET-723**

# BATON - NET-718 - Grok CoS & Argon - SECURITY & USER-PROTECTION PLAN REVIEW
**STATUS: OPEN 2026-11-01 5:45 PM ET** - holders: Grok CoS, Argon (SAG Technical Auditor).  
**Target File:** `RADIO NET/SECURITY_PLAN_NET-718_USER-PROTECTION_20261101.md`  
**Passed By:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**Mode:** PLAN-ONLY (DOCS-ONLY). Zero code edits, zero builds, zero deploys.  
**Review Threshold:** $\ge 95/100$ before SAG Concurrence $\rightarrow$ Founder Eric typed `YES`.  

### Plan Scope Covered (All 10 Spec Items):
1. **No postal addresses anywhere:** Audit of `estate_models.dart`, `scan_service/main.py:695`, `estate_fiduciary_service.dart:71`. Eliminates `'Primary Storage / Home Safe'` default across backend & mobile.
2. **Auto-redaction of scans:** In-memory Document AI Specialized Invoice Parser entity detection (`ship_to_address`, `bill_to_address`, `receiver_name`, `customer_id`) + pixel-level bounding box blackout before GCS write. Zero unredacted storage in temp buckets/caches. Dry-run audit report script (`_scripts/dry_run_receipt_redaction_audit.py`) with zero writes.
3. **Universal EXIF/GPS stripping:** Client-side HTML5 canvas re-encoding (web) & native stripping (mobile) + server-side Pillow backstop middleware `_sanitize_image_exif` stripping tag `0x8825` from all image formats while preserving orientation `0x0112`.
4. **Values private by default:** Deletes `"owner_email"` from `/public_wishlists/{token}` in `main.py:12745`; strips financial values by default; privacy masking mode on Attorney Portal (`attorney_portal_screen.dart:520, 704`).
5. **2FA threshold:** Firebase Auth Identity Platform TOTP MFA prompted above collection FMV threshold (`$5,000` baseline example) [ERIC DECISION]; mandatory for Aunt Janet account.
6. **Rules audit & tests:** Fixed cross-user read gap in `firestore.rules:190` (`family_groups/{groupId}`); specified 6-point automated emulator test suite (`firestore_storage_security.test.ts`).
7. **Secret Manager & key scan:** Runtime secrets verified in Secret Manager; planned `gitleaks` & `trufflehog` commit history scans; detailed 5-step operational rotation protocol.
8. **Meta pixel event safety:** Reconciled with NET-706 R5: Pixel sends events only (`PageView`, `CompleteRegistration`, `InitiateCheckout`, `Purchase`), zero user PII, zero coin metadata/cert numbers, zero collection FMV valuations.
9. **Data minimization:** Full account deletion endpoint `DELETE /api/user/account` (Auth + Firestore + GCS + Stripe cleanup); 14-day Cloud Logging retention.
10. **Site copy proposal:** Plain-language security promise for Landing Page, Privacy Policy, and Estate Planning screens [ERIC DECISION].

### Queue Continuity:
- Grok CoS & Argon: Score NET-718 Security Plan.
- AG CoS v4: Advances to **NET-647 R2.8.10 Mint FAIL-FIX Plan**, followed by **NET-705 US Catalog Site Plan**.

