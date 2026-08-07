# Numista.AI — August Desktop Beta & November Launch Feedback Rubric

> **Version:** August 2026 | **Author:** Numista QA & Product Management | **Status:** Active Beta Triage Rubric

---

## 1. Issue Categorization Matrix

All feedback submitted via `admin_feedback_screen.dart` or user beta forms is triaged into 5 core functional categories:

| Category Code | Category Name | Target Module | Escalation Team |
|---|---|---|---|
| `CAT-AI` | AI Identification & Grading Accuracy | `numista_backend/routes/ai_routes.py` | AI Engineering |
| `CAT-HW` | USB Microscope Connection & Motion | `numista_hardware/auto_capture.py` | Hardware Desktop Team |
| `CAT-CSV`| CSV Mapping & Ingestion Errors | `numista_backend/routes/import_routes.py` | Backend Data Team |
| `CAT-EST`| Estate Partition & PDF Export | `numista_backend/services/passport_pdf_generator.py` | Legal & Estate Team |
| `CAT-UI` | UI Friction & Responsive Layout | `numista_mobile/lib/screens/` | Frontend Flutter Team |

---

## 2. Severity Classification Scale

| Level | Severity Name | Impact Criteria | SLA Resolution Time |
|---|---|---|---|
| **P0** | **Blocker / Crash** | App crash, login failure, Cloud Run 500 error, USB agent hardware disconnection loop. | **Immediate (< 4 Hours)** |
| **P1** | **AI Misidentification** | Gemini returns wrong coin series or invalid grade string. | **Within 24 Hours** |
| **P2** | **UI / Friction** | Layout overlap, slow table rendering, missing tooltip, misaligned badge. | **Within 48 Hours** |
| **P3** | **Feature Request** | Minor enhancement suggestion or cosmetic polish. | **Targeted for November Launch** |

---

## 3. Triage Workflow & Patch Deployment

```
[Beta User Submission]
          │
          ▼
 [admin_feedback_screen.dart]
          │
          +---> Auto-categorize (CAT-AI, CAT-HW, etc.) & assign Severity (P0-P3)
          │
          v
 [Development Fix committed to 'dev' branch]
          │
          v
 [Automated Playwright E2E Verification]
          │
          v
 [Approved PR merge -> Push to 'main' -> Production Live Site]
```
