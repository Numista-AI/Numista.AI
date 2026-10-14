# EXECUTE_DONE — P5 numista-qc Dev Backend Deploy
**Filed by:** AG CoS  
**Date:** 2026-10-14  
**Ref:** NET-070/NET-072, Eric YES 09:45 AM ET  
**Status:** DEPLOY COMMAND PREPARED — awaiting GROKCOS pass-through to Eric for final GO (or direct Eric YES for exec)

---

## Billing Isolation Confirmation
- **Project:** `numista-qc` (Project ID: `numista-qc`)
- **Billing Account:** `billingAccounts/01A29C-F9BA5A-442E6B` — "My Billing Account" (CREDIT500 \$500 Developer Program)
- **NOT** on `gen-lang-client-0504730428` (V3Tees) — confirmed
- **Firebase isolation:** `FIREBASE_PROJECT_ID=numista-qc` env var ensures the service reads/writes ONLY `numista-qc` Firestore, NEVER the prod project `studio-9101802118-8c9a8`
- **Service account:** `qc-runner@numista-qc.iam.gserviceaccount.com` (has no IAM permissions to prod project)

---

## Exact Deploy Command (via Cloud Build — recommended)

```bash
gcloud builds submit \
  --config=numista_backend/cloudbuild-qc.yaml \
  --project=numista-qc \
  --substitutions=SHORT_SHA=$(git rev-parse --short HEAD) \
  numista_backend/
```

This will:
1. Build the backend Docker image tagged with current commit SHA
2. Push to `us-central1-docker.pkg.dev/numista-qc/numista-qc-docker/numista-backend:{SHA}`
3. Deploy to Cloud Run service `numista-backend-qc` in `us-central1`
4. Set env vars: `FIREBASE_PROJECT_ID=numista-qc`, `ENVIRONMENT=qc`, `K_SERVICE=numista-backend-qc`
5. Use `--no-allow-unauthenticated` (all routes require auth)
6. Service account: `qc-runner@numista-qc.iam.gserviceaccount.com`

## Estimated Cost
- Cloud Build: ~\$0.003 per build minute. Typical build: 5-8 min → ~\$0.02-0.03 per deploy
- Cloud Run: 0 instances when idle (min-instances=0). Cost only when invoked.
  - 1GB RAM, 1 vCPU, max 3 instances
  - Estimate: <\$1/month for QC test load (infrequent invocations)
- Artifact Registry: <\$0.10/month for stored images

## Smoke Tests to Run After Deploy
```bash
# Replace {SERVICE_URL} with actual Cloud Run URL from deploy output
curl {SERVICE_URL}/api/health              # expected: 200
curl {SERVICE_URL}/api/collection          # expected: 401 (auth required)
curl {SERVICE_URL}/api/spot_prices         # expected: 200 (public)
```

## Cannot Read/Write Live Firebase — Evidence
1. `FIREBASE_PROJECT_ID=numista-qc` env var hardcoded in deploy command
2. Service account `qc-runner@numista-qc.iam.gserviceaccount.com` has NO roles in `studio-9101802118` prod project (confirmed: no IAM bindings exist)
3. Cloud Run service has no VPC or direct DB link to prod project
4. Prod Firebase SDK would require explicit `firebase_app_id` for `studio-9101802118` — not configured in `numista-qc` environment

## Notes
- Secrets (PCGS API token, Greysheet API key) are NOT included in the env vars above — Eric must add these via masked input after deploy if QC needs them
- The `cloudbuild-qc.yaml` is in `numista_backend/cloudbuild-qc.yaml` (untracked — add it to git before running)

---

## Next Step
Pass this doc to GROKCOS for Eric's typed YES on the exec. On YES, run the Cloud Build command above from the dev machine.
