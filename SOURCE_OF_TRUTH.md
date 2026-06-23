# Numista.AI — Definitive Source of Truth
> **AGENTS: Read this file before making any changes to infrastructure, deployment, or project config.**
> Last verified: 2026-06-23 (full audit session — all values confirmed from actual files on disk)

---

## ⚠️ CRITICAL: Only One Active Firebase Project

As of 2026-06-23, there is exactly **one** Firebase/GCP project for Numista.AI:

| Project | ID | Status |
|---|---|---|
| **AJ's AI Coin App** | `studio-9101802118-8c9a8` | ✅ THE ONLY LIVE PROJECT |
| `numista-ai` | (deleted) | ❌ DELETED 2026-06-23 — was a ghost project, never had real data |

> Do NOT create, reference, or deploy to any project other than `studio-9101802118-8c9a8`.

---

## GCP Project

| Field | Value |
|---|---|
| **GCP Project ID** | `studio-9101802118-8c9a8` |
| **GCP Project number** | `568985927038` |
| **Firebase Hosting site ID** | `numista-vault` |
| **GitHub Actions service account** | `github-actions-deployer@studio-9101802118-8c9a8.iam.gserviceaccount.com` |
| **GitHub Actions secret name** | `FIREBASE_SERVICE_ACCOUNT` |

---

## Production URLs

| Service | URL |
|---|---|
| **Live site (Flutter web)** | https://numista.ai |
| **Backend (Cloud Run)** | `https://numista-backend-568985927038.us-central1.run.app` |
| **Local dev** | http://localhost:8080 |

---

## Cloud Infrastructure

### Backend — Cloud Run
| Field | Value |
|---|---|
| **Service name** | `numista-backend` |
| **Region** | `us-central1` |
| **Registry** | `us-central1-docker.pkg.dev` (Artifact Registry — NOT gcr.io) |
| **Full image path** | `us-central1-docker.pkg.dev/studio-9101802118-8c9a8/cloud-run-source-deploy/numista-backend:latest` |
| **Base image** | `python:3.11-slim` |
| **Entry point** | `uvicorn main:app --host 0.0.0.0 --port 8080` |
| **RETIRED — never use** | `numista-app` service / `gcr.io` registry |

### Frontend — Firebase Hosting
| Field | Value |
|---|---|
| **GCP project** | `studio-9101802118-8c9a8` |
| **Firebase Hosting site** | `numista-vault` |
| **Flutter app directory** | `numista_mobile/` |
| **Build command** | `flutter build web --release --base-href "/"` |
| **Deploy command** | `firebase deploy --only hosting --project studio-9101802118-8c9a8` |

### GitHub Actions Service Account Roles (confirmed 2026-06-23)
| Role | Purpose |
|---|---|
| `roles/firebase.admin` | Firebase Hosting deploy |
| `roles/run.admin` | Cloud Run deploy |
| `roles/artifactregistry.writer` | Docker image push |
| `roles/storage.admin` | GCS access |
| `roles/cloudbuild.builds.editor` | Cloud Build |
| `roles/iam.serviceAccountUser` | Service account impersonation |

---

## Local File Config (confirmed from disk 2026-06-23)

| File | Key Value |
|---|---|
| `numista_mobile/.firebaserc` | `"default": "studio-9101802118-8c9a8"` |
| `numista_mobile/firebase.json` | `"site": "numista-vault"` |
| `numista_backend/.firebaserc` | `"default": "studio-9101802118-8c9a8"` |
| `.github/workflows/deploy-production.yml` | `--project studio-9101802118-8c9a8` |
| `numista_mobile/lib/constants.dart` | `kApiBaseUrl = 'https://numista-backend-568985927038.us-central1.run.app'` |
| `numista_mobile/lib/firebase_options.dart` | `projectId: 'studio-9101802118-8c9a8'` |

---

## Flutter App

| Field | Value |
|---|---|
| **Package name** | `numista_ai` |
| **Version** | `3.8.0+36` (as of 2026-06-23) |
| **Dart SDK** | `^3.11.3` |
| **Firebase AI SDK** | `firebase_ai: ^3.10.0` |

---

## Deployment Method (Authoritative)

1. **PRIMARY**: `git push origin main` → triggers `.github/workflows/deploy-production.yml` (deploys both frontend + backend)
2. **EMERGENCY frontend-only**: `.\deploy_production.ps1` from project root
3. **EMERGENCY backend-only**:
   ```powershell
   gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
   docker build -t us-central1-docker.pkg.dev/studio-9101802118-8c9a8/cloud-run-source-deploy/numista-backend:latest .
   docker push us-central1-docker.pkg.dev/studio-9101802118-8c9a8/cloud-run-source-deploy/numista-backend:latest
   gcloud run deploy numista-backend --image us-central1-docker.pkg.dev/studio-9101802118-8c9a8/cloud-run-source-deploy/numista-backend:latest --region us-central1 --project studio-9101802118-8c9a8 --quiet
   ```

> `numista_backend/cloudbuild.yaml` and `numista_backend/trigger_config.yaml` are **stale/legacy** — do not use.

---

## Key File Locations

| Purpose | Path |
|---|---|
| **This file** | `SOURCE_OF_TRUTH.md` (project root) |
| Agent standing rules | `agent_guidance.md` |
| Deployment SOP | `DEPLOYMENT_SOP.md` |
| GitHub Actions CI/CD | `.github/workflows/deploy-production.yml` |
| Emergency deploy (frontend) | `deploy_production.ps1` |
| Dev launcher | `launch_numista.ps1` |
| Flutter app | `numista_mobile/` |
| Python backend | `numista_backend/` |
| Architecture doc | `ARCHITECTURE.md` |
| Session log | `SESSION_LOG.md` |
