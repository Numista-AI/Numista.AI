# Numista.AI — Feedback System: Current State Brief
**Date:** 23 AUG 2026
**Purpose:** Pre-planning context document — what exists, what is broken, what we are building

---

## What the System Currently Does (Working)

### Channel 1 — MORGAN In-App Interview
Users submit feedback inside the app via a floating action button (FAB) or automatic triggers.

Flow:
  Flutter client -> BetaFeedbackService -> POST /api/feedback/callable (Cloud Run)
                 -> Gemini analysis (issue_type, severity, root cause, fix area)
                 -> Firestore: beta_feedback/{doc_id}
                 -> Firebase Function: alert email to eric@numista.ai
                 -> Firebase Function: monthly rollup in feedback_insights

The callable endpoint handles 7 modes:
  CHECK, EXTRACT, SUBMIT, DISMISS, UPLOAD_URL, CORRECTION, ADMIN_RESOLVE

### Channel 2 — Admin Feedback Screen (In-App Portal)
admin_feedback_screen.dart — live dashboard inside the Flutter app.
Streams directly from Firestore beta_feedback collection.
Features: filter by category/status, view screenshots, change status (OPEN/TRIAGED/RESOLVED).

### Channel 3 — Daily Feedback Miner (Partially Set Up)
daily_feedback_test_miner.py — scans .docx, .md, .txt files from a local folder
and converts them into structured test vectors -> numista_tests/fixtures/daily_feedback_manifest.json.
NOTE: Currently pointed at the wrong folder (see gap below).

---

## The Critical Gap

The .eml files in this folder are NOT emails from testers — they are the Firebase alert
notification emails that Numista's own system sent to eric@numista.ai after in-app
feedback was submitted. The actual feedback data (transcript, Gemini analysis, etc.)
is already in Firestore.

Gaps identified:
  1. Antigravity cannot query Firestore — no script exists to read beta_feedback
  2. The feedback miner is pointed at the wrong base directory
  3. No documented protocol for Antigravity to handle feedback sessions

---

## The 2 Feedback Items From Today (23 AUG 2026)

Both were submitted via the Fallback Form (not the full MORGAN interview).
Both are MEDIUM severity Bug Reports on app version 4.1.0-beta.

Item 1:
  Feedback ID: f724a3ae6821626a2779b4faab05bfc9f2f52a8f
  User UID:    HQ6o1EwlDKO5WLLKj7bhm3SvRUW2
  Page:        Unknown (route: /)
  Message:     "I have 4 1 dollar coins. the valuation in [VALUE_REDACTED].
                the list indicates i have washington quarters which is wrong"
  Firestore:   https://console.firebase.google.com/project/studio-9101802118-8c9a8/firestore/databases/-default-/data/~2Fbeta_feedback~2Ff724a3ae6821626a2779b4faab05bfc9f2f52a8f

Item 2:
  Feedback ID: 253599ed538447dcc05ac0e2c17a86350181fb4d
  User UID:    HQ6o1EwlDKO5WLLKj7bhm3SvRUW2
  Page:        Unknown (route: /)
  Message:     "view binder short cut does not work"
  Firestore:   https://console.firebase.google.com/project/studio-9101802118-8c9a8/firestore/databases/-default-/data/~2Fbeta_feedback~2F253599ed538447dcc05ac0e2c17a86350181fb4d

NOTE: Both submissions came from the same user UID. This may indicate a single tester
who encountered 2 separate issues. Both items are currently OPEN in Firestore.

---

## Proposed Solution (Summary)

Build fetch_open_feedback.py — a Python script using Firebase Admin SDK that:
  - Queries Firestore for all OPEN beta_feedback documents
  - Prints a summary table + full transcript per item to stdout
  - Antigravity runs this on demand whenever the founder asks for a feedback check
  - After review, Antigravity can mark items TRIAGED and create fix plans

Also fix daily_feedback_test_miner.py base path:
  FROM: C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING
  TO:   C:\Users\ericd\Documents\MyVertexProject\Beta Testing Feedback

Full plan: See FEEDBACK_SYSTEM_PLAN.md in this folder.

---

## Key File References

  numista_backend/routes/feedback_callable_route.py   — Cloud Run callable (7 modes)
  numista_backend/functions/feedbackIntelligence.js   — Firebase Function (email + insights)
  numista_mobile/lib/services/beta_feedback_service.dart — Flutter client
  numista_mobile/lib/screens/admin_feedback_screen.dart  — In-app admin dashboard
  numista_qa_runner/daily_feedback_test_miner.py         — Local file miner (needs path fix)
  beta_feedback_rubric.md                                — Triage severity rubric (P0-P3)
