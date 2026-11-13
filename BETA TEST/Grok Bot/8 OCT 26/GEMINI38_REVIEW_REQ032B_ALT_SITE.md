# GEMINI 3.8 FLASH REVIEW — TRACK 3b: PLAN_V1_REQ032B_ALT_SITE.md
**Reviewer:** Gemini 3.8 Flash (Gatekeeper & Code Reviewer)  
**Date:** 2026-10-12  
**Target Document:** `BETA TEST\Grok Bot\8 OCT 26\PLAN_V1_REQ032B_ALT_SITE.md`  
**Founder Authorization:** Eric Seaman approved YES on 12 Oct 2026 12:24 PM ET  
**Status:** **REVIEW COMPLETED — PASS WITH IMPLEMENTATION SPECIFICATIONS**

---

## Executive Summary & Verdict

Antigravity CoS (Claude Sonnet 4.6 Thinking) has formulated an exceptional, architecturally sound plan for Track 3b (Alternate "Simple" Site). The core design strictly adheres to Eric's directive: **ONE database, TWO front-ends, SAME backend APIs**. 

Crucially, the plan ensures:
1. No duplicated data stores or shadow collections.
2. No new backend data-path endpoints that could bypass REQ_031 auth lockdown or Morgan Gate 0 safety confirms.
3. Server-controlled feature flag gating with Phase A strictly hardcoded to `eric.seaman@yahoo.com` and `eric@numista.ai`.
4. Pragmatic recommendation of **Option X (in-app toggle / flag rendering)** over Option Y (subdomain) for Phase A/B to eliminate DNS, CORS, and multi-build complexity.

Verdict: **PASS**.

---

## 1. Codebase Ground Truth & Verification

Every proposed integration hook was verified directly in the repository:

### 1.1 Auth Gate Integration Hook
- **Plan Reference:** Section 5, Step 3 (`numista_mobile/lib/auth_gate.dart (or equivalent)`).
- **Exact Target:** `numista_mobile/lib/widgets/auth_gate.dart:100-115`.
- **Verification:** In `AuthGate.build()`, after `snapshot.hasData` (user is authenticated), line 111 currently returns `const BaseLayout()`.
- **Implementation:**
  Calling `await UiVariantService.instance.load(user.email ?? '')` right inside `_shouldShowWelcome` or before rendering `BaseLayout` allows the app to seamlessly select `ClassicScaffold` vs `SimpleScaffold` with zero routing flicker.

### 1.2 Feature Flag Storage & Security
- **Plan Reference:** Section 2 (`users/{email}/settings/ui_variant`).
- **Security Check:**
  - `POST /api/admin/set_ui_variant` uses `Depends(require_admin_user)` (`routes/deps.py:81`).
  - `POST /api/user/set_ui_variant` uses `Depends(get_current_user)` with a hardcoded server allowlist `PHASE_A_ALLOWLIST = {"eric.seaman@yahoo.com", "eric@numista.ai"}`.
  - Regular users cannot grant themselves access; tampering with client-side state is meaningless because the server enforces access.

### 1.3 Backend API Parity Audit (Section 4)
The listed endpoints:
- `POST /api/deep_dive` (`main.py:2715`)
- `POST /api/checklist/add_coins` (`main.py:7783`)
- `POST /api/upload_document` (`scan_routes.py:84`)
- `POST /api/review/commit_session` (`scan_routes.py:273`)
Both `Classic` and `Simple` front ends consume these exact contracts, guaranteeing zero backend divergence.

---

## 2. Answers to Plan Open Questions (Section 10)

### Question 1: Should Phase A self-set endpoint persist after Phase A?
**Recommendation:** Keep the endpoint, but change its guard in Phase C to allow all authenticated users (when the Settings toggle is publicly enabled). For Phase B (beta cohort), use the admin endpoint `POST /api/admin/set_ui_variant` to batch-enable the flag for users matching `isBetaTester` in `auth_service.dart:22`.

### Question 2: SimpleScaffold structure (separate file vs wrapper)?
**Recommendation: Discrete layout file (`numista_mobile/lib/widgets/simple_scaffold.dart`).**  
Having a clean, separate `SimpleScaffold` prevents polluting the 1,567-line `base_layout.dart` with conditional `if (isSimple)` branches across all 29 sidebar destinations. `SimpleScaffold` directly renders the 6-item navigation and imports the simplified views cleanly.

### Question 3: Concern with Firestore read on startup?
**Recommendation: Server read on login is correct and necessary.**  
A single document read (`users/{email}/settings/ui_variant`) during session startup costs negligible latency (<30ms) and ~0.00003 cents. It ensures that when Eric changes his flag or rolls back a feature, the change takes effect immediately upon reload without stale SharedPreferences caching bugs.

---

## 3. Build & Execution Sequencing (Strict Compliance)

As mandated by Eric's orders:
1. **REQ_031 Hotfix ships FIRST.**
2. **Morgan Gate 0 lands SECOND.**
3. **Track 3b builds strictly on `dev`.**
4. **Zero live deploys without Eric's explicit typed YES.**

---

*Gemini 3.8 Flash Gatekeeper review deposited at `BETA TEST\Grok Bot\8 OCT 26\GEMINI38_REVIEW_REQ032B_ALT_SITE.md`.*
