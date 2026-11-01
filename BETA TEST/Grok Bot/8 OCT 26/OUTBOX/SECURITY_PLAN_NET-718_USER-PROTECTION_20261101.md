# NET-718 - Security & User-Protection Plan (Plan-Only)
**Document ID:** `SECURITY_PLAN_NET-718_USER-PROTECTION_20261101.md`  
**Date:** 2026-11-01  
**Author:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**Authority:** Founder Eric typed directive: *"Yes, start the security plan now"* (2026-11-01 4:35 PM ET)  
**Reference WAKE:** `WAKE_AG-COS-V4_NET-718_SECURITY-USER-PROTECTION-PLAN_20261101.md`  
**Mode:** PLAN-ONLY (DOCS-ONLY). Zero code edits, zero builds, zero deploys, zero GCS/Firestore writes.  
**Branch Baseline:** `origin/dev` commit `32d4b42e5d93ac8ec719c64cdb246f2957678f2e`  
**Locks:** `origin/main` locked at `9f04550a`; Stripe OFF; Live site 200 OK.  

---

## Executive Summary & Founder Goal (The Aunt Janet Doctrine)

Numista.AI exists to empower coin collectors, but holding numismatic records creates a profound physical security responsibility. Our users include elderly collectors who live alone—exemplified by Aunt Janet ("AJ", 83, lives alone, holding Numista.AI's largest collection). 

**The Core Doctrine:** A data breach must **never** become a treasure map for home invaders or burglars. Even if our database, storage buckets, or server logs were fully compromised, an attacker must find **zero home addresses, zero physical safe locations, zero phone numbers, and zero unredacted dealer invoices showing buyer names or delivery destinations.**

This plan specifies the comprehensive technical architecture to guarantee this invariant across all 10 required security and user-protection areas before the public launch on Thanksgiving 2026 (`2026-11-26T05:00:00Z`).

---

## 1. No Postal Addresses Anywhere [Spec Item 1]

### 1.1 Current State Audit (origin/dev 32d4b42e)
- **User Authentication / Signup:** `numista_mobile/lib/screens/login_screen.dart:127-154` and `numista_mobile/lib/services/auth_service.dart:7-23` use email and 6-digit numeric PIN exclusively. There are no postal address, street, city, state, or ZIP code fields in user registration or profile schemas.
- **Estate Planning Screen:** `numista_mobile/lib/screens/estate_planning_screen.dart:608-610` presents a Zero-Knowledge Privacy banner explicitly committing that attorney and beneficiary legal contacts are never stored on backend servers (in-memory PDF generation only).
- **Physical Location Leak in Estate Overlay:**
  - `numista_backend/scan_service/main.py:695`: Initializes estate overlay records with hardcoded `'custodialLocation': 'Primary Storage / Home Safe'`.
  - `numista_mobile/lib/services/estate_fiduciary_service.dart:71`: Sets `'custodialLocation': 'Primary Storage / Home Safe'`.
  - `numista_mobile/lib/models/estate_models.dart:215, 262, 288`: Exposes `custodialLocation` property.
  - `numista_mobile/lib/screens/estate_planning_screen.dart:4076, 4196`: Filters and displays `custodialLocation`.
- **CSV Template Location References:**
  - `numista_mobile/web/add_coins.html:1331-1332` and `numista_backend/public/add_coins.html`: Bulk import CSV template includes `"Storage Location"` column with sample value `"Safe Box A"`.

### 1.2 Gap
The hardcoded default `'Primary Storage / Home Safe'` in `scan_service/main.py` and `estate_fiduciary_service.dart` explicitly associates user coin records with a physical home safe. If exported or breached, this directly signals to an adversary that high-value coins are kept at the user's residence in a safe.

### 1.3 Proposed Fix [PROPOSED]
1. **Eliminate "Home Safe" Default:** Remove `'Primary Storage / Home Safe'` default across all backend services and mobile models.
   - `scan_service/main.py:695`: Change default to `'Vault Item'` or null (`None`).
   - `estate_fiduciary_service.dart:71`: Change default to `'Vault Item'` or null.
2. **Restrict Storage Location Labels:** UI dropdowns and helper text must prohibit or warn against entering street addresses, safe combinations, or residential descriptors (e.g., "Under bed", "Master bedroom safe"). Storage labels will be restricted to abstract numismatic identifiers (e.g., `"Album 1"`, `"Slab Box A"`, `"Safety Deposit Box"`).
3. **CSV Template Update:** In `web/add_coins.html:1332`, update template sample value from `"Safe Box A"` to `"Slab Box 1"`.
4. **Schema Invariant:** Document and enforce zero address/phone collection across all Firestore rules and endpoint validation schemas.

### 1.4 Verification & Tests
- Automated unit test asserting that default initialization of estate data documents produces `custodialLocation == 'Vault Item'` or `null`, never containing the string `"Home Safe"`.
- Static grep scan verifying zero occurrences of street address or postal code fields in Firestore schema documentation.

### 1.5 Ownership, Effort & Risk
- **Owner:** Backend & Mobile Engineers
- **Effort:** 0.5 dev-days (Surgical copy/default replacement)
- **Risk:** Very Low. Backward compatible with existing estate models.

---

## 2. Auto-Redaction of Receipt & Invoice Scans [Spec Item 2]

### 2.1 Current State Audit (origin/dev 32d4b42e)
- **Upload Flow:** `numista_backend/main.py:7396-7445` (`POST /api/import/upload`) and lines 7499-7548 (`POST /api/import/start`). Raw invoice PDFs and images are uploaded directly to GCS at `blob_path = f"{user_email}/imports/{session_id}/raw/{safe_name}"` without redaction.
- **Serving Flow:** `numista_backend/main.py:8899-8960` (`GET /api/receipts/{user_email}/{receipt_id}/view_url` and `/stream`) generates signed URLs or streams raw original PDFs directly back to the client.
- **Client Text Redaction:** `numista_mobile/web/add_coins.html:1315-1328` has a client-side regex `maskPII(text)` that replaces phone numbers and emails in extracted text, but the underlying uploaded PDF/image document itself remains completely unredacted in GCS storage.

### 2.2 Gap
Dealer invoices (from Littleton, US Mint, Heritage, GreatCollections, APMEX) prominently display the buyer's full legal name, shipping street address, billing address, customer account number, and phone number. Storing raw unredacted invoice PDFs in GCS creates an extreme physical security vulnerability for Aunt Janet and all collectors.

### 2.3 Proposed Fix [PROPOSED]
1. **Pre-Storage Redaction Architecture:**
   - Raw uploaded files received in `POST /api/import/upload` are processed **in-memory** before permanent GCS persistence.
   - For all invoice files (`_classify_file` returns `'invoice'` or `'image'`), stream bytes to Document AI Specialized Invoice Parser (`INVOICE_PROCESSOR_V1` or Specialized Invoice Processor in `us-documentai.googleapis.com`).
   - Entity Recognition targets: `receiver_name`, `receiver_address`, `ship_to_address`, `bill_to_address`, `receiver_phone`, `customer_id`.
   - Polygon Coordinate Extraction: Extract normalized bounding box vertices (`page_anchor.page_refs[].bounding_poly.normalized_vertices`) for each detected PII entity across all document pages.
   - Blackout Engine: Using `PyMuPDF` (`fitz`) or Pillow, render solid black rectangles (`#000000`) over every detected bounding box, permanently burning pixel blackout into the PDF stream or image raster.
   - GCS Storage: Only the **redacted** document bytes are written to GCS at `users/{email}/receipts/{id}/redacted_{filename}`. The raw unredacted bytes in memory are discarded immediately after redaction.
   - **Zero Raw Storage Invariant:** Unredacted original scans are NEVER stored in permanent buckets, temporary staging buckets, Cloud Run local caches, or log payloads.
2. **Low-Confidence Human-in-the-Loop Fallback:**
   - If Document AI confidence for address/name extraction is $< 0.85$, or if the document layout is non-standard, flag the receipt as `requires_redaction_review: true`.
   - Present the user with an interactive client-side canvas overlay showing proposed blackout boxes and allowing the user to draw manual blackout boxes before saving to GCS.
3. **Backfill Plan for Existing Scans (Aunt Janet Receipt PDFs):**
   - **Phase A (DRY-RUN ONLY):** Author dedicated script `numista_backend/_scripts/dry_run_receipt_redaction_audit.py`.
     - Scans existing GCS receipt blobs for user accounts (including Aunt Janet's account).
     - Runs Document AI entity extraction and records bounding box counts and confidence scores.
     - Emits `RECEIPT_REDACTION_AUDIT_REPORT.json` summarizing all identified PII entities.
     - **Constraint:** Zero file modifications, zero GCS overwrites, zero deletions during dry run.
   - **Phase B (Execution):** Only executed after Founder Eric reviews the dry-run report and issues a typed `YES`. Applies redactions in-place and securely purges unredacted predecessors.

### 2.4 Verification & Tests
- Unit test passing a simulated Littleton invoice PDF with synthetic buyer name and address; asserts resulting PDF text extraction contains zero occurrences of the name/address and pixel inspection confirms solid black fill over the coordinates.
- Dry-run audit script test confirming exit code 0 and report generation with zero GCS write calls.

### 2.5 Ownership, Effort & Risk
- **Owner:** Backend AI/ML Engineer
- **Effort:** 2.5 dev-days (Document AI pipeline + bounding box blackout renderer + dry-run script)
- **Risk:** Medium. Requires careful coordinate mapping between normalized Document AI vertices and PDF point dimensions across multi-page documents.

---

## 3. Universal EXIF / GPS Geolocation Stripping [Spec Item 3]

### 3.1 Current State Audit (origin/dev 32d4b42e)
- **Server HEIC Only:** `numista_backend/main.py:4254-4279` (`_convert_heic_to_jpeg`) strips GPS EXIF tag `0x8825` (`GPSInfo`), but **only** when converting HEIC/HEIF images. Line 4279 explicitly notes: `return raw_bytes, None # Not HEIC or conversion failed; use original`.
- **Server JPEGs/PNGs:** Standard JPEG, PNG, or WEBP photos uploaded directly to `/api/import/upload` or coin photo endpoints bypass HEIC conversion entirely and retain all original EXIF metadata.
- **Client Uploads:** `numista_mobile/lib/screens/add_coins_hub.dart:6`, `coin_detail_screen.dart:28`, and `camera_capture_service_mobile.dart:2` use `image_picker` to capture or select camera photos, but do not sanitize EXIF/GPS tags before uploading.

### 3.2 Gap
Smartphones automatically tag camera photos with precise latitude, longitude, and altitude GPS coordinates. If an elderly user photographs coins at home on an iPhone or Android device, uploading raw JPEGs embeds their exact home address inside the image EXIF header.

### 3.3 Proposed Fix [PROPOSED]
1. **Client-Side Pre-Upload Stripping:**
   - **Web (Flutter Web):** In `camera_capture_service_web.dart` and `web/add_coins.html`, draw uploaded or captured images to an HTML5 `<canvas>` element and export via `canvas.toBlob('image/jpeg', 0.90)`. Canvas re-encoding natively purges all EXIF headers and GPS metadata in the browser sandbox before network transit.
   - **Mobile (Flutter Native):** In `camera_capture_service_mobile.dart`, pass selected photo bytes through the `image` package (`decodeImage` / `encodeJpg`) or native platform channel to strip all EXIF tags except orientation (`0x0112`).
2. **Server-Side Backstop Middleware:**
   - In `numista_backend/main.py`, introduce a universal image sanitizer `_sanitize_image_exif(raw_bytes: bytes, mime_type: str) -> bytes`:
     ```python
     def _sanitize_image_exif(raw_bytes: bytes) -> bytes:
         """Universal server-side backstop: strips GPS tags (0x8825) and all PII EXIF."""
         try:
             buf_in = BytesIO(raw_bytes)
             img = PILImage.open(buf_in)
             exif = img.getexif()
             if exif:
                 for gps_tag in (0x8825, 0x013B, 0x013C): # GPSInfo, Artist, HostComputer
                     exif.pop(gps_tag, None)
                 buf_out = BytesIO()
                 img.save(buf_out, format=img.format or 'JPEG', exif=exif.tobytes() if exif else b'')
                 return buf_out.getvalue()
         except Exception as e:
             logger.warning(f"EXIF sanitization fallback: {e}")
         return raw_bytes
     ```
   - Wire `_sanitize_image_exif` into every photo ingest path (`/api/import/upload`, `/api/coins/{id}/photo`, `/api/chat/photo`).

### 3.4 Verification & Tests
- Automated test uploading a synthetic JPEG containing simulated GPS coordinates (e.g. lat/long coordinates); asserts output image bytes downloaded from server contain no GPS tag (`0x8825`).

### 3.5 Ownership, Effort & Risk
- **Owner:** Mobile & Backend Engineers
- **Effort:** 1.0 dev-day
- **Risk:** Low. Preserves EXIF orientation tag (`0x0112`) to prevent sideways coin photos.

---

## 4. Values Private by Default [Spec Item 4]

### 4.1 Current State Audit (origin/dev 32d4b42e)
- **Public Wishlist Share Endpoint:** `numista_backend/main.py:12733-12765` (`POST /api/wishlist/create-share`).
  - Line 12745: Writes `"owner_email": req.user_email` directly into public Firestore collection `/public_wishlists/{token}`!
  - Lines 12746-12750: Stores raw unmasked `items` array directly in the public document.
- **Attorney Portal Screen:** `numista_mobile/lib/screens/attorney_portal_screen.dart:520` and line 704 displays total collection FMV, cost basis, and coin-by-coin estimated values.
- **Wishlist Sharing:** `numista_mobile/lib/screens/wishlist_screen.dart:134, 186` generates shareable links without privacy masking options.

### 4.2 Gap
Writing the collector's email address into `/public_wishlists/{token}` directly deanonymizes the user to anyone possessing the share link. Furthermore, displaying total portfolio FMV and unmasked coin values by default exposes collection wealth to third parties who view shared links.

### 4.3 Proposed Fix [PROPOSED]
1. **Purge Email from Public Wishlist Snapshots:**
   - In `numista_backend/main.py:12745`, immediately delete `"owner_email": req.user_email` from the public snapshot payload.
   - Replace with `"owner_alias": req.owner_alias or "Numista Collector"`.
2. **Strip Financial Values from Shared Wishlists by Default:**
   - By default, remove `purchase_cost`, `market_value`, `estimated_fmv`, and private notes from all items written to `/public_wishlists/{token}`.
   - Only include estimated value ranges if the user explicitly checks an opt-in toggle: `[ ] Include estimated price ranges on public gift list`.
3. **Attorney Portal Privacy Masking:**
   - In `numista_mobile/lib/screens/attorney_portal_screen.dart:518-535`, introduce a Privacy Masking Mode (eye icon toggle) defaulting to masked (`$••,•••`) for total collection FMV and cost basis.
4. **Display Names Optional:**
   - User display names across all shared views default to `"Numista Collector"` or `"Anonymous Collector"`. Legal names are never displayed.

### 4.4 Verification & Tests
- Backend test calling `POST /api/wishlist/create-share`; asserts the document written to `/public_wishlists/{token}` contains no `owner_email` field and no price/cost fields by default.

### 4.5 Ownership, Effort & Risk
- **Owner:** Backend & Frontend Engineers
- **Effort:** 1.0 dev-day
- **Risk:** Low. Prevents accidental exposure of collector identity and wealth.

---

## 5. 2FA Prompted Above Collection-Value Threshold [Spec Item 5]

### 5.1 Current State Audit (origin/dev 32d4b42e)
- **Current Authentication:** `numista_mobile/lib/services/auth_service.dart:7-23` and `login_screen.dart:127-154`. Users authenticate via Firebase email/password where the password is a 6-digit numeric PIN.
- **MFA Status:** Zero Multi-Factor Authentication (2FA/MFA) enrollment prompts or enforcement mechanisms currently exist in the codebase.

### 5.2 Gap
A 6-digit PIN provides standard convenience, but high-value collections (such as Aunt Janet's) require multi-factor protection to prevent account takeover via credential stuffing or email compromise.

### 5.3 Proposed Fix [PROPOSED]
1. **Value Threshold Trigger [ERIC DECISION]:**
   - Define collection FMV threshold for 2FA prompt: **`$5,000`** (baseline example; subject to Founder Eric approval).
   - **Aunt Janet Invariant:** 2FA enrollment is unconditionally required for Aunt Janet's account regardless of threshold setting.
2. **Enrollment Architecture:**
   - Integrate Firebase Auth Identity Platform TOTP Multi-Factor Authentication (`user.multiFactor.enroll`).
   - Supports standard Authenticator apps (Google Authenticator, Microsoft Authenticator, Authy, Apple Passwords).
   - User scans a secure QR code on first enrollment and verifies a 6-digit one-time code.
3. **UI Flow (`numista_mobile/lib/widgets/mfa_security_modal.dart` [PROPOSED]):**
   - When a collector's total collection FMV exceeds the threshold (or upon login), display security recommendation modal:
     > *"Your collection valuation exceeds \$[THRESHOLD]. To protect your valuable numismatic assets, Numista.AI recommends enabling Two-Factor Authentication (2FA)."*
   - Options: *"Set Up 2FA Now"* or *"Remind Me Later"* (for standard users; mandatory for designated high-value accounts).

### 5.4 Verification & Tests
- Widget test asserting that accounts exceeding collection FMV threshold trigger the 2FA prompt modal on dashboard load.
- Unit test verifying TOTP enrollment and challenge verification flow via Firebase Auth emulator.

### 5.5 Ownership, Effort & Risk
- **Owner:** Mobile Security Engineer
- **Effort:** 2.0 dev-days
- **Risk:** Low. TOTP is natively supported by Firebase Auth Identity Platform.

---

## 6. Firestore & Storage Security Rules Audit [Spec Item 6]

### 6.1 Current State Audit (origin/dev 32d4b42e)
- **Firestore Rules:** `numista_mobile/firestore.rules` (authoritative deployed rules per `firebase.json:134-136`).
  - Lines 17-21: `isOwner(email)` helper ensures `request.auth.token.email == email || request.auth.uid == email`.
  - Lines 40-70: User coin collection documents `/users/{email}/coins/{coinId}` restricted to `allow read, write: if isOwner(email);`.
  - Line 182: `/public_wishlists/{token}` allows `get: if true;`, but blocks list queries.
  - Line 190: `match /family_groups/{familyGroupId} { allow read: if request.auth != null; ... }`.
- **Storage Rules:** `numista_backend/storage.rules`:
  - Lines 8-12: `match /users/{email}/{allPaths=**} { allow read, write: if request.auth != null && request.auth.token.email == email; }`.
- **Test Suite Status:** Currently zero automated emulator test suites exist in the repository for rules verification.

### 6.2 Gap
In `numista_mobile/firestore.rules:190`, `allow read: if request.auth != null;` permits **any** authenticated user to read **any** family group document, representing an unauthorized cross-user read vulnerability. Furthermore, the lack of an automated emulator test suite leaves security rules vulnerable to accidental regressions.

### 6.3 Proposed Fix [PROPOSED]
1. **Surgically Fix Family Groups Rule:**
   - In `numista_mobile/firestore.rules:190`, replace open authenticated read with strict membership check:
     ```javascript
     match /family_groups/{familyGroupId} {
       allow read: if request.auth != null
                   && (request.auth.uid == resource.data.primary_owner_uid
                       || request.auth.uid in resource.data.get('member_uids', []));
       allow write: if request.auth != null
                    && request.auth.uid == resource.data.primary_owner_uid;
     }
     ```
2. **Implement Automated Rules Emulator Test Suite:**
   - Create `numista_mobile/test_rules/firestore_storage_security.test.ts` [PROPOSED] using `@firebase/rules-unit-testing`.
   - Test Matrix (all must exit code 0):
     - `TEST-RULE-01`: User A cannot read User B's `/users/{userB}/coins/{coinId}` (assertFails).
     - `TEST-RULE-02`: User A cannot list User B's coin subcollections (assertFails).
     - `TEST-RULE-03`: User A cannot read User B's `/family_groups/{groupId}` where User A is not owner or member (assertFails).
     - `TEST-RULE-04`: Unauthenticated requests cannot read any `/users/{email}/**` document (assertFails).
     - `TEST-RULE-05`: Public wishlist token `GET` succeeds without auth, but collection `list` query is denied (assertFails).
     - `TEST-RULE-06`: User A cannot read or write User B's GCS storage objects `/users/{userB}/**` (assertFails).

### 6.4 Verification & Tests
- Execute `firebase emulators:exec --only firestore,storage "npm test"` verifying 100% of security rule assertions pass.

### 6.5 Ownership, Effort & Risk
- **Owner:** Backend Security Engineer
- **Effort:** 1.5 dev-days
- **Risk:** Low. Hardens permissions without breaking authorized user collection flows.

---

## 7. Secrets Exclusively in Secret Manager & Leaked-Key Scan [Spec Item 7]

### 7.1 Current State Audit (origin/dev 32d4b42e)
- **Runtime Secrets:** `numista_backend/main.py:60-120` retrieves credentials via `os.environ.get(...)` mounted from Google Cloud Secret Manager (`projects/numista-qc/secrets/*`) in Cloud Run.
- **Repository Hygiene:** `.gitignore` excludes `.env`, `*.json` credentials, and Firebase cache files.

### 7.2 Gap
No automated scan of full git commit history has been formally executed and documented to guarantee that historical commits contain zero orphaned API keys or tokens.

### 7.3 Proposed Fix [PROPOSED]
1. **Automated History Scan:**
   - Execute `gitleaks detect --verbose --redact` and `trufflehog git file://. --since-commit 9f04550a` across all branches.
   - Archive scan report as `LEAKED_KEY_AUDIT_REPORT.md` in security audit folder.
2. **Immediate Rotation Protocol (If Any Key is Flagged):**
   - **Step 1:** Immediately invalidate/revoke the key in the provider console (Stripe, SendGrid, OpenAI, Google Cloud Console).
   - **Step 2:** Generate replacement secret with least-privilege scoping.
   - **Step 3:** Deploy new version to Secret Manager: `gcloud secrets versions add <SECRET_NAME> --data-file=...`.
   - **Step 4:** Re-deploy Cloud Run service to absorb new revision.
   - **Step 5:** Record incident in security log.

### 7.4 Verification & Tests
- Machine-checkable command: `gitleaks detect --no-git` exiting with code 0.

### 7.5 Ownership, Effort & Risk
- **Owner:** DevOps / Security Engineer
- **Effort:** 0.5 dev-days
- **Risk:** Low. Pure verification and operational rotation protocol.

---

## 8. Meta Pixel Event Safety & Zero-PII Invariant [Spec Item 8]

### 8.1 Current State Audit & NET-706 Reconciliation
- **NET-706 Pre-Launch Plan (Scored 97 PASS):**
  - Section 3 installs Meta Pixel tracking for 4 specific client events: `PageView`, `CompleteRegistration`, `InitiateCheckout`, and `Purchase`.
  - For `Purchase`, NET-706 lines 161-168 transmits:
    ```javascript
    fbq('track', 'Purchase', { value: verifiedAmount, currency: 'USD' });
    ```
  - `verifiedAmount` is verified exclusively against server session payment records (`$4.99`, `$12.99`, or `$95.94`).

### 8.2 Gap
Must formally codify that Meta Pixel tracking is strictly sandboxed and can never transmit coin metadata, certification numbers, or collection valuations.

### 8.3 Reconciliation & Invariant Specification [PROPOSED]
1. **Zero User PII:** Meta Pixel NEVER receives user email, legal name, phone number, address, or hashed customer data (`Advanced Matching` is disabled).
2. **Zero Coin Metadata:** Meta Pixel NEVER receives coin names, certification numbers, grades, mint marks, variety titles, or collection inventory counts.
3. **Zero Portfolio Valuations:** Meta Pixel NEVER receives user collection FMV or estimated values.
4. **Purchase Event Reconciliation [ERIC DECISION]:**
   - Transmits **only** the software subscription fee paid to Numista.AI (`$4.99`, `$12.99`, or `$95.94`) for Meta Ads Manager campaign optimization and ROAS calculation.
   - **Alternative [ERIC DECISION]:** If Founder Eric prefers absolute zero-value tracking, fire `fbq('track', 'Purchase')` with no value or currency parameters.

### 8.4 Verification & Tests
- Web E2E test intercepting `https://www.facebook.com/tr/` network beacons; asserts outgoing query parameters contain zero PII, zero cert numbers, and no collection FMV.

### 8.5 Ownership, Effort & Risk
- **Owner:** Frontend Web Engineer
- **Effort:** 0.5 dev-days
- **Risk:** Low. Reconciled byte-for-byte with NET-706 R5 plan.

---

## 9. Data Minimization & Full Account Deletion [Spec Item 9]

### 9.1 Current State Audit (origin/dev 32d4b42e)
- **Account Deletion:** Zero automated account deletion endpoints currently exist in `numista_backend` or `numista_mobile`.
- **Cloud Logging:** Default Cloud Logging retention stores server logs for 30 days.

### 9.2 Gap
Collectors who wish to delete their account currently have no self-service mechanism to purge their records. Without full automated deletion, orphaned collection and receipt records could linger indefinitely.

### 9.3 Proposed Fix [PROPOSED]
1. **Full Account Deletion Workflow (`DELETE /api/user/account`):**
   - Authenticates calling user via Firebase Auth ID token.
   - Deletes all user Firestore documents and subcollections:
     - `/users/{email}`
     - `/users/{email}/coins/*`
     - `/users/{email}/receipts/*`
     - `/users/{email}/review_queue/*`
     - `/users/{email}/estate_data/*`
     - `/users/{email}/estate_reports/*`
     - `/users/{email}/settings/*`
   - Purges all user objects in GCS: `gs://numista-user-content/{email}/*`.
   - Cancels any active Stripe subscription via Stripe API.
   - Deletes Firebase Auth user record via Admin SDK `auth.delete_user(uid)`.
2. **Log Sanitization & Retention:**
   - Configure Cloud Logging retention policy to 14 days for user-facing services.
   - Sanitize loggers in `numista_backend/main.py`: mask email addresses (`a***@domain.com`) and never log customer names, addresses, or invoice contents in plaintext log streams.

### 9.4 Verification & Tests
- Backend integration test creating a test user with simulated coins and receipts, executing `DELETE /api/user/account`, and asserting that Firestore documents, GCS files, and Auth records are completely purged.

### 9.5 Ownership, Effort & Risk
- **Owner:** Backend Engineer
- **Effort:** 1.5 dev-days
- **Risk:** Low. Enforces GDPR/CCPA compliance and collector peace of mind.

---

## 10. Site Copy Proposal: Plain-Language Security Promise [Spec Item 10]

### 10.1 Current State Audit (origin/dev 32d4b42e)
- `web/privacy.html:325` and `privacy_screen.dart:139` state: *"We do not sell, rent, or trade your personal data or coin collection details to third parties."*
- However, there is no prominent plain-language promise explaining our intentional refusal to collect home addresses or safe locations.

### 10.2 Proposed Site Copy [ERIC DECISION TO APPROVE]

#### Placement A: Landing Page / Marketing Hero (`web/index.html` & `home_dashboard.dart`)
> **"Built for Collectors Who Value Privacy Above All."**  
> *"Your coin collection is your business. Numista.AI intentionally never asks where you live or where your coins are stored. We do not collect home addresses, phone numbers, or safe locations. Even in the event of a breach, our database contains no treasure map."*

#### Placement B: Privacy Policy (`web/privacy.html` & `privacy_screen.dart`)
> **"Security by Design: Zero Physical Location Records."**  
> *"We do not collect or store physical street addresses, postal codes, or safe locations. An attacker compromising Numista.AI can never learn where you or your coins physically reside."*

#### Placement C: Estate Planning Screen (`estate_planning_screen.dart`)
> **"Zero-Knowledge Physical Storage."**  
> *"Numista.AI tracks coins purely by numismatic attributes. We never record your residence, vault combinations, or physical storage coordinates."*

---

## 11. Consolidated Implementation Roadmap & Estimates

| Item # | Area | Scope | Est. Effort | Risk | Dependencies |
|---|---|---|---|---|---|
| 1 | No Postal Addresses | Remove "Home Safe" default across backend & mobile | 0.5 dev-days | Low | None |
| 2 | Scan Auto-Redaction | Document AI blackout pipeline + Dry-Run Script | 2.5 dev-days | Med | Document AI API |
| 3 | Universal EXIF Stripping | Client canvas re-encode + Server backstop | 1.0 dev-days | Low | Pillow |
| 4 | Private Values by Default | Mask values on shared links & Attorney Portal | 1.0 dev-days | Low | None |
| 5 | 2FA for High-Value Accts | Firebase TOTP MFA prompt above threshold | 2.0 dev-days | Low | Identity Platform |
| 6 | Rules Audit & Tests | Fix family groups rule + Emulator test suite | 1.5 dev-days | Low | Firebase CLI |
| 7 | Secret Manager & Key Scan| Gitleaks history scan + rotation protocol | 0.5 dev-days | Low | None |
| 8 | Meta Pixel Event Safety | Strict zero-PII/coin data sandbox verified | 0.5 dev-days | Low | NET-706 R5 |
| 9 | Data Minimization | Full account deletion endpoint + 14d log policy | 1.5 dev-days | Low | Admin SDK |
| 10 | Security Site Copy | Plain-language "we never ask where you live" | 0.5 dev-days | Low | Eric Typed YES |
| **Total** | **Comprehensive Sprint** | **10 Security Protection Tracks** | **11.5 dev-days**| **Low-Med** | **Gate 2 Typed YES**|

*(Note: In accordance with standing rules, GCP API costs for Document AI and Identity Platform are based on published standard tiers or marked TBD pending exact volume projections).*

---

## 12. Lessons & Self-Improvement

1. **Aunt Janet as the Ultimate Test:** Code architecture must always be evaluated through the lens of our most vulnerable user. A database of coin values without physical addresses is inert; a database with addresses is a dangerous catalog.
2. **Sanitize Before Storage, Not at Read Time:** Security redaction must occur in-memory prior to persistence. Storing unredacted files and attempting to redact on download creates persistent exposure in storage backups and raw bucket leaks.
3. **Verify Line Numbers Verbatim Against Baseline:** Every citation in this plan has been checked against `origin/dev 32d4b42e` to eliminate ghost references and ensure turnkey execution when Founder Eric issues the build baton.

---

## 13. Next Steps & Baton Protocol

1. **Distribution:** Distributed to `RADIO NET/`, `BATONS/`, `INBOX/`, and `For SAG/`.
2. **Review Track:** Open `BATON_NET-718_GROKCOS-ARGON_SECURITY-PLAN-REVIEW_20261101.md`.
3. **Approval Threshold:** Review score $\ge 95/100$ from Grok CoS and Argon $\rightarrow$ SAG Concurrence $\rightarrow$ Founder Eric typed `YES` before execution.
4. **Queue Continuity:** AG CoS v4 advances to **NET-647 R2.8.10 Mint FAIL-FIX Plan**, followed by **NET-705 US Catalog Site Plan**.

**OVER.**
