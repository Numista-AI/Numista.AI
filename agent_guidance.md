# Numista.AI - Agent Guidance & Standing Rules
> **ANTIGRAVITY: Read this file at the start of every session before making any changes.**
> Last updated: 2026-06-23

---

## 🔴 MANDATORY FIRST READ — Before Anything Else

**Read `SOURCE_OF_TRUTH.md` in the project root before touching any file, config, or infrastructure.**

```
c:\Users\ericd\Documents\MyVertexProject\SOURCE_OF_TRUTH.md
```

This file contains the verified GCP project ID, Firebase Hosting site, Cloud Run service name, registry paths, and deployment commands — all confirmed from actual files on disk on 2026-06-23. Do not guess at any of these values. Do not rely on training data. Read the file.

> There is exactly ONE active Firebase/GCP project: `studio-9101802118-8c9a8` ("AJ's AI Coin App").
> The ghost project `numista-ai` was deleted 2026-06-23. Do not reference it.

---

## âš ï¸ RULE 0 â€” NEVER TRUST TRAINING DATA FOR VERSION NUMBERS

**This is the most important rule added June 16, 2026.**

My training data has a knowledge cutoff and is frequently **wrong or stale** about package versions, SDK releases, and deprecation dates. The user has had to correct me multiple times on Google SDK versions.

### Mandatory Version Verification Protocol

Before writing any version constraint into `requirements.txt`, `pubspec.yaml`, `package.json`, or any config file:

1. **Always verify live** using one of these commands:
   ```powershell
   # Python packages â€” check live PyPI
   pip index versions <package-name>

   # npm/Node packages
   npm view <package-name> version

   # Flutter/Dart packages
   dart pub outdated
   ```

2. **Never assert** a version number from memory. Say "I believe X is the latest, let me verify" and then run the check.

3. **For Google SDKs specifically** â€” check the deprecation schedules folder (see below) AND verify PyPI. Google SDK versions change frequently and my training data is often behind.

---

## ðŸ“‹ GOOGLE DEPRECATION SCHEDULES â€” MANDATORY READING

The user maintains official Google deprecation schedule PDFs here:

```
C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules\
```

**Current files:**
- `Gemini Deprecation Schedules 14 APR 2026.pdf`
- `Gemini Deprecation Schedules 9 June 2026.pdf`
- `Gemini Models as of 11 JUN 2026.png`

**Rule:** At the start of any session that involves Google AI SDKs, Gemini models, Vertex AI, or Firebase â€” read the most recent file in this folder before writing any code or making version recommendations.

**Current known facts (as of June 16, 2026):**
- `google-genai` (new unified SDK): **v2.8.0** is latest stable
- `google-generativeai` (legacy SDK): peaked at v0.8.6 â€” do NOT use
- `vertexai.generative_models` (old Python SDK): **shutting down June 24, 2026** â€” do NOT use
- Active Gemini models: `gemini-3.6-flash` (primary via `config.py`), `gemini-3.1-pro-preview` (pro tasks)
- Backend now uses Python **3.11-slim** base image

---

## ?? Project Context

- **Company:** SGroup LLC (solo operator â€” Eric is the only developer)
- **Product:** Numista.AI â€” a coin collection management app at https://numista.ai
- **Stack:** Flutter (mobile & web), Python (FastAPI backend on Cloud Run), Firebase Hosting, Google Cloud (Vertex AI, BigQuery, GCS)
- **GCP Project:** `studio-9101802118-8c9a8`

---

## ?? CRITICAL DEPLOYMENT RULES â€” NEVER SKIP THESE

### Rule 1 â€” Always Deploy to BOTH Environments

**A task is NOT complete until BOTH of these are updated:**

| Environment | URL | How to update |
|---|---|---|
| **Local Dev** | `http://localhost:8080` | `flutter run -d chrome` (via `launch_numista.ps1`) |
| **Live Production** | `https://numista.ai` | Run `deploy_production.ps1` (see below) |

> ?? Do NOT mark any task as "Done" or "Complete" until the live site at **https://numista.ai** reflects the change and has been verified.

### Rule 2 â€” Production Deploy Script

Always use the single script to deploy to production. Do not run steps manually unless the script fails:

```powershell
# From the project root:
.\deploy_production.ps1
```

This script will:
1. Remove the dev service-worker kill-switch from `numista_mobile/web/index.html`
2. Run `flutter build web --release --base-href "/"`
3. Deploy via `firebase deploy --only hosting`
4. Restore the dev service-worker kill-switch
5. Print the live URL for verification

### Rule 3 â€” Verify the Live Site After Every Deploy

After running `deploy_production.ps1`, always confirm:
- [ ] https://numista.ai loads without errors
- [ ] The specific feature/fix that was changed is visible and working
- [ ] No console errors in browser DevTools

### Rule 4 â€” Backend Deploys Are Separate

If `numista_backend/main.py` was modified, the backend must also be deployed to Cloud Run separately. The deploy script does NOT handle this automatically.

```powershell
# Backend deploy (run from numista_backend/):
gcloud run deploy numista-backend --source . --project studio-9101802118-8c9a8 --region us-central1
```

### Rule 5 — ALWAYS Verify in an Incognito Window

**This is the #1 reason updates appear not to go live.** The service worker aggressively caches the app in the browser. Your regular browser tab will almost always show a stale version after a deploy.

> 🔴 **Never verify a production deploy using your regular browser tab.**
> ✅ **Always open a fresh Incognito / Private window to confirm the live site.**

Steps:
1. Open a new **Incognito** window (`Ctrl+Shift+N` in Chrome)
2. Navigate to **https://numista.ai**
3. Verify the specific change is live
4. Open **DevTools → Application → Service Workers** — confirm the worker is active
5. Check **DevTools → Console** — confirm zero errors

### Rule 6 — Follow the Full Deployment SOP

For the complete deploy checklist, timing estimates, and troubleshooting table, always refer to:

```
DEPLOYMENT_SOP.md  (project root)
```

When the user asks about deployment, pushing updates, or why a change isn't live — point them to `DEPLOYMENT_SOP.md` first.

---

## ?? Standard Session Checklist

Before starting any coding task:
1. Read this file (`agent_guidance.md`)
2. Confirm which environment the change targets (local only, or production too?)
3. Check `PROD_BUILD_CHECKLIST.md` if preparing a production release
4. Check `SESSION_LOG.md` for recent work context

Before ending any coding session:
1. Confirm the live site is updated if the task touched production-facing code
2. Append a summary to `SESSION_LOG.md`

---

## ?? Key File Locations

| Purpose | Path |
|---|---|
| Dev launcher | `launch_numista.ps1` |
| Production deploy | `deploy_production.ps1` |
| **Deployment SOP** | **`DEPLOYMENT_SOP.md`** |
| Production build checklist | `PROD_BUILD_CHECKLIST.md` |
| Flutter app | `numista_mobile/` |
| Python backend | `numista_backend/` |
| Hardware server | `numista_hardware/` |
| Playwright tests | `numista_tests/` |
| Architecture docs | `ARCHITECTURE.md` |

---

## ?? Things to NEVER Do

- Do NOT delete `numista_mobile/build/web/` â€” this is the production web build cache
- Do NOT run `flutter clean` unless explicitly asked (it deletes the web build)
- Do NOT push secrets, API keys, or `.env` files to Git
- Do NOT consider a task complete if only the local dev server was updated

---

## 📐 ARCHITECTURE.md — Keep It Current

**Rule:** Update `ARCHITECTURE.md` at the end of any session that changes:
- Cloud Run services (add, delete, update memory/scaling)
- Backend tech stack (Python version, packages, SDK versions)
- Flutter app structure or backend URL
- Firebase Hosting configuration
- New directories (`_scripts/`, `_archive/`, etc.)
- AI models in use

**Section to always update:** Section 9 (Deployment Architecture) — includes a "Last verified" date stamp. Change that date every time you touch it.

The file is at: `c:\Users\ericd\Documents\MyVertexProject\ARCHITECTURE.md`
