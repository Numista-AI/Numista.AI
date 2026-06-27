# Numista.AI - Deployment SOP (Standard Operating Procedure)
> **Read this before every production push.**
> Last updated: 2026-06-22

---

## PRIMARY DEPLOYMENT METHOD - Push to Git

**The definitive way to deploy Numista.AI is to push code to the `main` branch.**

The GitHub Actions pipeline (`.github/workflows/deploy-production.yml`) automatically:
1. Builds the Flutter web app and deploys it to **Firebase Hosting** (numista.ai)
2. Builds the Docker image and deploys the Python backend to **Cloud Run** (`numista-backend`) via Artifact Registry

> **WARNING:** `deploy_production.ps1` is an **emergency fallback only** (frontend/Firebase Hosting exclusively).
> Do NOT use it as your default deploy path.

---

## GOLDEN RULE - When to Deploy

**Do NOT deploy after every single tweak. Do NOT wait until end of day.**

**Deploy once per focused work session** - typically 1-3 times per day.

| Session | Example |
|---|---|
| Morning session | Make 3-5 related tweaks -> test locally -> git push -> verify live |
| Afternoon session | Make 3-5 related tweaks -> test locally -> git push -> verify live |
| Evening (optional) | Only if needed and there is time to verify before stepping away |

> **Never deploy right before stepping away from your computer.** If something breaks, you need to be available to fix it.

---

## Why Updates May Not Appear on the Live Site

If you pushed but do not see the change on https://numista.ai, check these in order:

| # | Cause | Fix |
|---|---|---|
| 1 | **GitHub Actions pipeline still running** (most common) | Check `https://github.com/Numista-AI/Numista.AI/actions` |
| 2 | **Browser cache / service worker** | Verify in an **Incognito window** - always |
| 3 | **Flutter analyze failed** and aborted the build | Check the Actions log; fix errors and re-push |
| 4 | **pubspec.yaml version not bumped** | Bump the version before pushing |
| 5 | **Wrong Firebase project targeted** | Confirm `studio-9101802118-8c9a8` appears in deploy output |
| 6 | **Firebase deploy propagation delay** | Wait 60-90 seconds, then hard-refresh in Incognito |

---

## STEP-BY-STEP DEPLOY CHECKLIST

### Phase 1 - Before You Start Coding

- [ ] Local dev server is running (`launch_numista.ps1`)
- [ ] You know which files you are about to change
- [ ] You know if this affects the **frontend only** or **backend too**

---

### Phase 2 - While Coding

- [ ] Test every change at `http://localhost:8080` before deploying
- [ ] Group related tweaks together - deploy once when the group is done, not per-tweak
- [ ] Note if `numista_backend/main.py` was modified (CI/CD handles the backend deploy automatically on push)

---

### Phase 3 - Pre-Deploy

- [ ] `flutter analyze` passes with **zero errors**
- [ ] `pubspec.yaml` version number bumped (at minimum the build number: `1.0.x+N`)
- [ ] All local tests passing

---

### Phase 4 - Deploy

#### PRIMARY: Push to Git (always preferred)

```powershell
# Stage, commit, and push from project root
git add -A
git commit -m "Deploy: <brief description of what changed>"
git push origin main
```

GitHub Actions triggers `.github/workflows/deploy-production.yml` automatically.
Monitor progress at: `https://github.com/Numista-AI/Numista.AI/actions`

**Typical pipeline time: 8-12 minutes total.**

---

#### EMERGENCY FALLBACK: Use deploy_production.ps1 (frontend only)

Only use this if the GitHub Actions pipeline is unavailable or broken:

```powershell
# From project root - deploys frontend (Firebase Hosting) only
.\deploy_production.ps1
```

This script automatically:
1. Removes the dev service-worker kill-switch from `numista_mobile/web/index.html`
2. Runs `flutter analyze` (aborts if errors found)
3. Changes into `numista_mobile/` and runs `flutter build web --release --base-href "/"`
4. Changes into `numista_mobile/` and runs `firebase deploy --only hosting --project studio-9101802118-8c9a8`
5. Restores the dev service-worker kill-switch
6. Pings https://numista.ai for a 200 response

> **WARNING:** This does NOT deploy the backend. Use `git push` for full deployments.

**If backend also changed and CI/CD is unavailable**, run these emergency commands from `numista_backend/`:

```powershell
# From numista_backend/ - EMERGENCY BACKEND DEPLOY ONLY
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
docker build -t us-central1-docker.pkg.dev/studio-9101802118-8c9a8/cloud-run-source-deploy/numista-backend:latest .
docker push us-central1-docker.pkg.dev/studio-9101802118-8c9a8/cloud-run-source-deploy/numista-backend:latest
gcloud run deploy numista-backend `
  --image us-central1-docker.pkg.dev/studio-9101802118-8c9a8/cloud-run-source-deploy/numista-backend:latest `
  --region us-central1 `
  --project studio-9101802118-8c9a8 `
  --quiet

# From project root - EMERGENCY SCAN SERVICE DEPLOY ONLY
gcloud run deploy numista-scan-service `
  --source ./numista_backend/scan_service `
  --project studio-9101802118-8c9a8 `
  --region us-central1
```

> **Registry:** Always use `us-central1-docker.pkg.dev` (Artifact Registry). NEVER use `gcr.io`.
> **Service:** `numista-backend` is our main low-latency FastAPI app. `numista-scan-service` is our dedicated Flask scan and PDF generation app. Do not overwrite one with the other.

---

### Phase 5 - Post-Deploy Verification (MANDATORY)

> A deploy is NOT complete until you personally verify the live site.

1. **Open an Incognito window** (not your regular browser tab - it may show cached content)
2. Navigate to **https://numista.ai**
3. Verify the specific feature/fix you just deployed is visible and working
4. Open **DevTools Console** - confirm zero errors
5. Open **DevTools Application Service Workers** - confirm service worker is active

- [ ] Site loads without errors
- [ ] The changed feature works correctly on the live site
- [ ] No console errors in DevTools
- [ ] Service worker is registered and active

---

### Phase 6 - Log It

Append a brief entry to `SESSION_LOG.md`:

```
## YYYY-MM-DD - [Short description of what was deployed]
- Changes: [list what changed]
- Backend redeployed: Yes / No (via GitHub Actions)
- Verified live: Yes
```

---

## Things to NEVER Do

| NEVER | INSTEAD |
|---|---|
| Use `deploy_production.ps1` as your default deploy | Use `git push origin main` (primary method) |
| Push a Docker image to `gcr.io` | Always use `us-central1-docker.pkg.dev` (Artifact Registry) |
| Reference the retired `numista-app` Cloud Run service | Use `numista-backend` only |
| Deploy after every single small tweak | Group tweaks, deploy once per session |
| Verify the live site using your regular browser tab | Always verify in **Incognito** |
| Mark a task as done if only local dev was updated | Deploy AND verify live before marking done |
| Run flutter build steps manually | Use `git push` (primary) or `deploy_production.ps1` (emergency) |
| Deploy right before stepping away from your desk | Stay available to catch issues post-deploy |
| Run `flutter clean` unless explicitly needed | It deletes the web build cache |

---

## Key File Reference

| Purpose | Path |
|---|---|
| **This SOP** | `DEPLOYMENT_SOP.md` |
| GitHub Actions CI/CD pipeline | `.github/workflows/deploy-production.yml` |
| Emergency manual deploy script (frontend only) | `deploy_production.ps1` |
| Production build checklist | `PROD_BUILD_CHECKLIST.md` |
| Agent standing rules | `agent_guidance.md` |
| Session log | `SESSION_LOG.md` |
| Flutter app | `numista_mobile/` |
| Python backend | `numista_backend/` |

---

## How Long Does a Deploy Take?

### GitHub Actions (primary)

| Step | Time |
|---|---|
| Flutter build + Firebase Hosting deploy | ~5-8 minutes |
| Docker build + Cloud Run deploy | ~5-8 minutes (parallel) |
| Firebase CDN propagation | 30-90 seconds |
| **Total (typical)** | **~8-12 minutes** |

### Emergency script (frontend only)

| Step | Time |
|---|---|
| flutter analyze | ~30 seconds |
| flutter build web --release | 2-4 minutes |
| firebase deploy --only hosting | ~30 seconds |
| Firebase CDN propagation | 30-90 seconds |
| **Total (typical)** | **~4-6 minutes** |

Plan for ~15 minutes from push to confirmed live verification.
