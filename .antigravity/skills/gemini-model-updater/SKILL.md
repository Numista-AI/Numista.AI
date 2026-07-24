---
name: gemini-model-updater
description: Safely audits and updates Gemini model bindings across Python and JavaScript against official Google deprecation schedule PDFs while maintaining strict compliance with Rule 6 and Rule 7.
---

# Gemini Model Updater Skill

Use this skill when auditing or updating Gemini model bindings for Numista.AI.

## Workflow Instructions

1. **Run Model Auditor**:
   Execute the model lifecycle auditor to check current configured models against the latest PDF deprecation schedule:
   ```powershell
   python numista_backend/_scripts/check_gemini_model_updates.py
   ```

2. **Verify Rule 6 Compliance**:
   - Ensure no proposed replacement has an earlier shutdown date than the current model.
   - Confirm that location settings (`location='global'` for Vertex AI 3.x models) are honored.

3. **Apply Model Updates (If Safe)**:
   When a new GA model is confirmed safe, apply environment updates:
   ```powershell
   python numista_backend/_scripts/check_gemini_model_updates.py --auto-update
   ```

4. **Execute Verification**:
   - Run backend pytest suite:
     ```powershell
     pytest numista_backend/tests
     ```
   - Test Vertex AI model binding:
     ```powershell
     python numista_backend/_scripts/verify_vertex_model.py
     ```
   - Test multimodal coin identification:
     ```powershell
     python numista_backend/_scripts/identify_coin.py
     ```

5. **Commit & Push to Dev (Rule 7)**:
   ```powershell
   git add numista_backend/config.py numista_backend/.env SCAN_REPORT.md agent_guidance.md
   git commit -m "chore(gemini): update model bindings to latest GA release"
   git pull --rebase origin dev && git push origin dev
   ```
   *NEVER push directly to `main` or merge to `main` without explicit user approval.*
