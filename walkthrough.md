# Walkthrough — Model Standardization & Policy Enforcement

I have standardized the entire codebase to use **`gemini-3.5-flash`** and implemented a mandatory policy to prevent future model deprecation issues.

## Changes Made

### 1. Model Standardization
- Reverted the manual change to `gemini-1.5-flash` (which is scheduled for shutdown in Oct 2026).
- Standardized over **200 files** (core backend and 100+ scripts) to use `gemini-3.5-flash`.
- Verified that `gemini-3.5-flash` is the current stable recommended model with no announced shutdown date.

### 2. Mandatory Policy Enforcement ("Hard Coding")
- Added a **MANDATORY** comment in all files where the model ID is defined:
  ```python
  # MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: 
  # C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules\
  MODEL = "gemini-3.5-flash"
  ```
- This ensures any future AI (or human) developer sees the path to the ground-truth deprecation documentation before making changes.

### 3. Agent Rules Update
- Updated [AGENTS.md](file:///c:/Users/ericd/Documents/MyVertexProject/.agents/AGENTS.md) with **Rule 5 — Mandatory Gemini Model Policy**.
- This rule explicitly forbids downgrading to models with earlier shutdown dates and requires reading the PDF schedule first.

## Verification Results

### Automated Verification
- Ran a standardization script across `numista_backend/` and `_scripts/`.
- Confirmed files are pointing to `gemini-3.5-flash`.
- Verified the presence of the mandatory warning comments.

### Manual Verification Required
- [ ] **Reauthentication**: The system currently requires `gcloud auth application-default login` to be run manually by the user to verify the `global` model connectivity.

## Git Status
- Changes staged, committed, and pushed to `origin/main`.
- Commit: `6784b86` ("feat(llm): standardize on gemini-3.5-flash and implement mandatory model policy")
