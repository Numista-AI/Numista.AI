# Numista.AI — Standalone Repository Rules & AI Advisor Guidelines

> **Purpose:** This document consolidates all mandatory repository rules, branching policies, deployment SOPs, infrastructure mandates, versioning protocols, and engineering guardrails for Numista.AI (`MyVertexProject`). Upload or reference this file in any standalone AI advisor (Gemini, Claude, ChatGPT, Grok, custom GPTs, sidecar agents).
>
> **Last Updated:** August 2026

---

## 1. Git Branching, Push & Commit Rules

### Rule 1 — Push to `dev` is the Finish Line
- Code verification on a local machine is **NOT** sufficient to consider a task complete.
- Before writing `walkthrough.md` or declaring any task/goal complete, you MUST execute the following sequence:
  1. Stage modified source files:
     ```bash
     git add <files>
     ```
  2. Commit with a descriptive message following Conventional Commits format:
     ```bash
     git commit -m "<type>(<scope>): <summary>"
     ```
  3. Pull and rebase against `dev`:
     ```bash
     git pull --rebase origin dev
     ```
  4. Push to `dev`:
     ```bash
     git push origin dev
     ```
  5. Confirm push output shows `dev -> dev`.
- *A task that is not pushed to GitHub is NOT done — it is only done locally.*

### Rule 2 — Session Start Sync Check
- At the start of every coding session, run:
  ```bash
  git status
  git log --oneline origin/main..HEAD
  git log --oneline origin/dev..HEAD
  ```
- If local `dev` is ahead of `origin/dev`, push those commits first before making new changes to avoid stranded commits.

### Rule 3 — Strict Execution Order
- The mandatory order of operations:
  ```
  Code changes → git add → git commit → git pull --rebase origin dev → git push origin dev → confirm → walkthrough.md / GOAL_COMPLETE
  ```

### Rule 4 — Excluded Artifacts & Scratch Files
- **NEVER** stage or commit the following:
  - `scratch/` directory (test scripts, one-off analysis)
  - `output/` directory
  - `*.firebase/*.cache` files
  - `numista_backend/database/*.db` files
  - Scraper or audit reports (`numista_backend/latest_scraper_report.md`, `sourcing_audit_report.md`)
- Keep these listed in `.gitignore`.

### Rule 5 — No Concurrent Push Conflicts
- **Do NOT** run multiple concurrent agent sessions that touch or edit the same files.
- If suspecting a parallel session is mid-push, run `git fetch origin` and check `git log --oneline origin/dev..HEAD`.
- For long-running overnight tasks, use a single `/goal` session.

### Rule 6 — Mandatory Gemini Model Policy
- Before changing any Gemini model ID (e.g. `gemini-3.5-flash` to `gemini-3.6-flash`):
  1. Read the latest PDF documentation in: `C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules\`
  2. Verify the shutdown date and recommended replacement model.
  3. **NEVER** downgrade to a model that has an earlier shutdown date.
  4. If a model returns 404, verify the `location='global'` setting before assuming retirement.

### Rule 7 — NEVER Push Directly to `main` (Production Protection)
- **CRITICAL:** Pushing to `main` deploys directly to the live production site (`https://numista.ai` / `numista-vault.web.app`).
- AI Agents MUST **NEVER**:
  - Push to `main` directly
  - Run `git merge` targeting `main`
  - Run `git checkout main` followed by any push
  - Ask "do you want me to merge to main?" and then execute it
- All code changes MUST be committed and pushed to `dev` (or feature branch `agent/*`).
- **Exceptions:**
  1. The sole designated deploy conversation (`7485fc0a-544c-4a5f-8e87-ff9e22099b5e`) when the user explicitly requests "Prepare to Deploy".
  2. Commits containing ONLY documentation files (`walkthrough.md`, `AGENTS.md`, `REPOSITORY_RULES.md`, scan reports, `*.md` in `scratch/`).

---

## 2. Infrastructure & Single Active Project Mandates

### Single Active GCP/Firebase Project
- **Active GCP Project ID:** `studio-9101802118-8c9a8` ("AJ's AI Coin App")
- **GCP Project Number:** `568985927038`
- **Firebase Hosting Site ID:** `numista-vault`
- **DELETED GHOST PROJECT:** `numista-ai` was permanently deleted on 2026-06-23. **NEVER** reference, configure, or deploy to `numista-ai`.

### Production Service URLs
| Service | Environment / URL | Details |
|---|---|---|
| **Live Frontend** | `https://numista.ai` | Firebase Hosting (`numista-vault`) |
| **Backend API** | `https://numista-backend-568985927038.us-central1.run.app` | Cloud Run (`us-central1`) |
| **Local Dev** | `http://localhost:8080` | Flutter web local dev server |

### Cloud Run Backend Specs
- **Service Name:** `numista-backend` (Region: `us-central1`)
- **Docker Registry:** `us-central1-docker.pkg.dev` (Artifact Registry — NOT `gcr.io`)
- **Full Image Path:** `us-central1-docker.pkg.dev/studio-9101802118-8c9a8/cloud-run-source-deploy/numista-backend:latest`
- **Base Image:** `python:3.11-slim`

---

## 3. Package Versioning & Dependency Protocols

### Rule 0 — Never Trust AI Training Data for Version Numbers
- AI training data has a knowledge cutoff and is frequently inaccurate for recent package releases and deprecation dates.
- **Mandatory Live Verification Protocol:**
  Before writing any version constraint into `requirements.txt`, `pubspec.yaml`, or `package.json`, verify live:
  ```powershell
  # Python packages (PyPI)
  pip index versions <package-name>

  # npm / Node packages
  npm view <package-name> version

  # Flutter / Dart packages
  dart pub outdated
  ```
- **Google SDK Rules:**
  - Standard Unified SDK: `google-genai` (v2.8.0+ is stable).
  - Retired SDKs: **DO NOT USE** legacy `google-generativeai` or `vertexai.generative_models` (retired June 2026).

---

## 4. Deployment & Verification Protocols

### Dual-Environment Mandate
- A production-facing task is **NOT COMPLETE** until both environments are updated and verified:
  1. **Local Dev:** `http://localhost:8080` (`flutter run -d chrome` via `launch_numista.ps1`)
  2. **Live Production:** `https://numista.ai` (deployed via `deploy_production.ps1`)

### Production Deployment Steps
- **Frontend Deploy:** Run `.\deploy_production.ps1` from project root. This automatically handles service worker kill-switch toggling, builds release web assets, and deploys to Firebase Hosting.
- **Backend Deploy:** If `numista_backend/` is modified, deploy Cloud Run separately:
  ```powershell
  gcloud run deploy numista-backend --source . --project studio-9101802118-8c9a8 --region us-central1
  ```
- **Automated CI/CD:** Merges into `main` via PR trigger `.github/workflows/deploy-production.yml`.

### Mandatory Incognito Verification Protocol
- Web service workers aggressively cache browser assets. **NEVER** verify production deployments in standard browser tabs.
- **Protocol:**
  1. Open a fresh **Incognito / Private Window** (`Ctrl+Shift+N` in Chrome).
  2. Navigate to `https://numista.ai`.
  3. Test and verify the modified feature.
  4. Inspect DevTools Console (`F12`) to confirm zero runtime errors.

---

## 5. Engineering Guardrails & Code Hygiene

1. **Never Guess Logic or Schemas:** Inspect authoritative source code before making changes.
2. **Empirical Log Diagnostics:** Inspect complete, un-truncated stack traces and logs before forming hypotheses. Never diagnose runtime errors blindly.
3. **No Symptom Masking:** Never resolve issues by swallowing exceptions, returning dummy 0-byte fallbacks, commenting out broken assertions, or deleting failing tests.
4. **No Unverified Success:** Never declare success without executing build or test verification commands (`pytest`, `flutter build`, `gcloud`, etc.).
5. **Preserve API Contracts:** When updating function signatures, search the codebase and update all invocation sites.
6. **Data Loss Safety:** Always confirm before executing destructive commands (`DROP TABLE`, `TRUNCATE`, `DELETE` without WHERE, `gsutil rm`, project deletion).
7. **Framework Specific Rules:**
   - **Next.js (`numista_admin`):** APIs and conventions differ from training data. Refer to `node_modules/next/dist/docs/`.
   - **Flutter (`numista_mobile/`):** **DO NOT** run `flutter clean` or delete `numista_mobile/build/web/` without explicit permission (preserves web build cache).

---

## 6. Project Documentation Standards

- **`SOURCE_OF_TRUTH.md`**: Definitive GCP/Firebase infrastructure values. Read before making config changes.
- **`ARCHITECTURE.md`**: Update Section 9 ("Deployment Architecture") and its "Last verified" date whenever Cloud Run, Python versions, Flutter SDK, directory structure, or AI models change.
- **`SESSION_LOG.md`**: Append session work summaries at the end of each session.
- **`agent_guidance.md`**: Standing guidance file for active agent sessions.
- **`DEPLOYMENT_SOP.md`**: Complete deployment checklist, timing estimates, and troubleshooting guide.
