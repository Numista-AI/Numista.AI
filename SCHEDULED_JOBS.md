# Numista.AI — Scheduled Jobs Reference

This document describes all automated background jobs registered for the Numista.AI system.
Update this file whenever a new job is added, modified, or removed.

---

## Job 1 — Nightly Data Audit

| Field | Value |
|-------|-------|
| **Name** | `Numista.AI - Nightly Data Audit` |
| **Script** | `numista_backend/nightly_data_audit.py` |
| **Launcher** | `run_nightly_audit.bat` (root of project) |
| **Schedule** | Daily at **2:00 AM local time** |
| **Registered In** | Windows Task Scheduler (laptop) |
| **Cloud Backup** | GCP Cloud Scheduler → `POST /api/cron/run-audit` |
| **Output** | Firestore: `weekly_audits/audit_YYYY-MM-DD` |
| **Log** | `scratch/audit_scheduler.log` (git-ignored) |

### What It Does
- Scans all coins (4,500+) and banknotes (413+) for every user in `TARGET_USERS`
- Checks for: missing images, year mismatches in image URLs, missing denominations/years
- Writes a full summary report to Firestore `weekly_audits/` for the Admin portal
- Immediately followed (30s later) by the Auto-Resolver (Job 2)

### How to Disable
**Windows Task Scheduler**: `schtasks /delete /tn "Numista.AI - Nightly Data Audit" /f`
**GCP Cloud Scheduler**: `gcloud scheduler jobs delete numista-nightly-audit --location=us-central1`

---

## Job 2 — Audit Auto-Resolver

| Field | Value |
|-------|-------|
| **Name** | Runs as part of `run_nightly_audit.bat` |
| **Script** | `numista_backend/auto_resolve_audit.py` |
| **Schedule** | Daily at **2:00 AM + 30 seconds** (launched by Job 1's bat file) |
| **Safety Cap** | Max 200 auto-fixes per run |
| **Output** | Updates individual Firestore coin/currency docs; writes `resolution_summary` back to the audit doc |

### What It Does
Reads the day's audit document and triages each flagged item:

| Bucket | Condition | Action |
|--------|-----------|--------|
| `AUTO_FIXED` | Missing image found in SQLite reference DB | Updates Firestore coin doc with image URL |
| `NEEDS_REVIEW` | Year mismatch in URL, or missing image not in catalog | Sets `review_needed: true` on the Firestore doc |
| `INFORMATIONAL` | Missing PCGS cert, missing year on raw coin | Logged only — no Firestore write |

### Safety Rules
- **Never deletes** any Firestore record
- Only writes to fields it knows are safe (`image_url_obverse`, `image_url_reverse`, `review_needed`)
- Hard cap of 200 auto-fixes per run to prevent runaway writes

---

## Job 3 — GCP Billing Monitor (Manual / On-Demand)

| Field | Value |
|-------|-------|
| **Script** | `numista_backend/monitor_gcp_billing.py` |
| **IAM Fixed** | `roles/billing.admin` granted to `firebase-adminsdk-fbsvc@studio-9101802118-8c9a8.iam.gserviceaccount.com` on 2026-07-10 |
| **API Enabled** | `billingbudgets.googleapis.com` enabled on 2026-07-10 |
| **Schedule** | On-demand (run manually to check credit balance) |

### To Set a Budget Alert
To create an automated spend alert (e.g., warn if daily spend exceeds $15):
```bash
gcloud billing budgets create \
  --billing-account=010E3C-D8346A-91A35E \
  --display-name="Numista Daily Spend Alert" \
  --budget-amount=450USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90
```

---

## CI/CD Pipelines (GitHub Actions)

These are not scheduled jobs but are documented here for completeness.

| Workflow | File | Trigger |
|----------|------|---------|
| **CI — Dev Branch** | `.github/workflows/ci-dev.yml` | Every push/PR to `dev` |
| **E2E Tests** | `.github/workflows/numista-ai-tests.yml` | Every 2 days + push to `main` |
| **Deploy to Production** | `.github/workflows/deploy-production.yml` | Push to `main` only |

---

*Last updated: 2026-07-10 by Antigravity agent (vacation automation session)*
