# Walkthrough: Numista.Ai Beta Test Feedback Fixes

All four categories of feedback from the beta testing review have been successfully implemented and verified:

## 1. Security: Client-Side and Backend PII Redaction
- **Web Client:** Added a checkbox option to let users opt into PII redaction. Added a `maskPII(text)` utility in JavaScript that masks email addresses and phone numbers before rendering them in lists.
- **Backend:** Updated both `/api/process_invoice` and `/api/import/process` prompts with explicit instructions to strip PII and replace it with `[REDACTED]` if the flag is enabled.

## 2. Performance: Client-Side Image Compression
- **Web Client:** Added a Canvas-based helper `compressImage()` in `web/add_coins.html` to automatically compress large image files down to a maximum of 1200px width/height and 80% JPEG quality before generating the signed GCS upload URLs. This reduces network payloads, speeds up uploads, and reduces backend API processing times.

## 3. Onboarding UX: "Free Scan" Preview
- **Mobile app:** Added a prominent, styled "Free Scan Preview" button to the `LoginScreen`.
- **Preview Screen:** Implemented `FreeScanPreviewScreen`, allowing users to select front/back photos of a coin using the file picker, upload them to the backend, run the AI scan without saving to Firestore, and view results with a call to action to sign up.

## 4. QA/Verification: "Verify Manually" Option
- **Mobile app:** Added a "Verify Manually" action button to the hero header in `coin_detail_screen.dart`. When clicked, it prompts a confirmation dialog and flags the coin in Firestore as `grade_review_status: 'pending'`.
- **Backend:** Updated `/api/grade_review/queue` to automatically query and include any coin with `grade_review_status == 'pending'` in the Human AI Trainer queue.
