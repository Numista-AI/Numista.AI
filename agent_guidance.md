# Numista.AI — Agent Guidance & Standing Rules
> **ANTIGRAVITY: Read this file at the start of every session before making any changes.**
> Last updated: 2026-06-13

---

## ?? Project Context

- **Company:** SGroup LLC (solo operator — Eric is the only developer)
- **Product:** Numista.AI — a coin collection management app at https://numista.ai
- **Stack:** Flutter (mobile & web), Python (FastAPI backend on Cloud Run), Firebase Hosting, Google Cloud (Vertex AI, BigQuery, GCS)
- **GCP Project:** `studio-9101802118-8c9a8`

---

## ?? CRITICAL DEPLOYMENT RULES — NEVER SKIP THESE

### Rule 1 — Always Deploy to BOTH Environments

**A task is NOT complete until BOTH of these are updated:**

| Environment | URL | How to update |
|---|---|---|
| **Local Dev** | `http://localhost:8080` | `flutter run -d chrome` (via `launch_numista.ps1`) |
| **Live Production** | `https://numista.ai` | Run `deploy_production.ps1` (see below) |

> ?? Do NOT mark any task as "Done" or "Complete" until the live site at **https://numista.ai** reflects the change and has been verified.

### Rule 2 — Production Deploy Script

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

### Rule 3 — Verify the Live Site After Every Deploy

After running `deploy_production.ps1`, always confirm:
- [ ] https://numista.ai loads without errors
- [ ] The specific feature/fix that was changed is visible and working
- [ ] No console errors in browser DevTools

### Rule 4 — Backend Deploys Are Separate

If `numista_backend/main.py` was modified, the backend must also be deployed to Cloud Run separately. The deploy script does NOT handle this automatically.

```powershell
# Backend deploy (run from numista_backend/):
gcloud run deploy numista-backend --source . --project studio-9101802118-8c9a8 --region us-central1
```

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
| Production build checklist | `PROD_BUILD_CHECKLIST.md` |
| Flutter app | `numista_mobile/` |
| Python backend | `numista_backend/` |
| Hardware server | `numista_hardware/` |
| Playwright tests | `numista_tests/` |
| Architecture docs | `ARCHITECTURE.md` |

---

## ?? Things to NEVER Do

- Do NOT delete `numista_mobile/build/web/` — this is the production web build cache
- Do NOT run `flutter clean` unless explicitly asked (it deletes the web build)
- Do NOT push secrets, API keys, or `.env` files to Git
- Do NOT consider a task complete if only the local dev server was updated
