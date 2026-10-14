# EXECUTE_DONE: CREDIT500 Dev-Spend Inventory (NET-024)
**Author:** Antigravity / Gemini 3.8
**Date:** 2026-10-13 ~20:40 ET
**Baton:** BATON_CREDIT500_DEV-SPEND_AGCOS_WILCO.md
**Radio:** NET-024 (response filed as NET-063)
**Credit:** $500 + $18 Gemini on My Billing Account (01A29C-F9BA5A-442E6B), **expires 29 Dec 2026**

> ADVISORY ONLY — No billing changes, no deploys, no IAM changes without Eric typed YES per change.

---

## TASK 1 — GCP Project Inventory

### Project: `studio-9101802118-8c9a8` (LIVE PRODUCTION)
**Billing:** Numista.Ai (010E3C-D8346A-91A35E)
**Role:** Live production — numista-vault.web.app + numista-backend Cloud Run

| Service | Details |
|---------|---------|
| **Cloud Run** | `numista-backend` (us-central1), `numista-scan-service` (us-central1), `app` (us-west1), `numista-app` (us-central1), `onfeedbackcreated` (us-central1) — all READY |
| **Cloud Functions** | `annotate-http`, `annotate_gcs`, `app`, `onFeedbackCreated` |
| **Firestore** | 1 DB: `(default)` — NATIVE, us-central1, free tier, version retention 1h |
| **Firebase Storage** | `studio-9101802118-8c9a8.firebasestorage.app` |
| **GCS Buckets** | 22 buckets — user uploads, training docs, estate reports, reference library, vision, Mint images, Firestore exports, build artifacts |
| **Secrets** | `EBAY_CERT_ID`, `NUMISTA_GMAIL_APP_PASSWORD` |
| **APIs** | Cloud Run ✅, Cloud Functions ✅, Vertex AI / Agent Platform ✅, Firebase ✅, Firestore ✅, BigQuery ✅, Cloud Build ✅, Secret Manager ✅ |
| **Budget** | morgan-pilot budget: \$5 (separate from prod spend) |

**Cost exposure:** This project is on the Numista.Ai billing account — costs come from Eric's own account, NOT from the \$500 credit.

---

### Project: `numista-qc` (DEV CANDIDATE)
**Billing:** My Billing Account (01A29C-F9BA5A-442E6B) ← **\$500 credit lives here**
**Role:** Dev / QC — Firebase, Firestore, BigQuery enabled. No Cloud Run deployed yet.

| Service | Details |
|---------|---------|
| **Cloud Run** | NOT ENABLED — API disabled (confirmed by gcloud probe) |
| **Firestore** | 2 DBs: `(default)` + `default` — both NATIVE, us-central1. One is free-tier (created Aug 24, 2026). |
| **GCS Buckets** | 0 buckets (empty storage) |
| **APIs** | Firebase ✅, Firestore ✅, BigQuery ✅ (all BigQuery variants enabled), Cloud Run ❌ (not enabled), Cloud Functions ❌ (not checked but likely disabled), Vertex AI ❌ (not enabled) |
| **Budget** | \$50/month alert budget on My Billing Account (covers numista-qc + gen-lang-client) |

**Note:** `numista-qc` was created Aug 2026 — it has the Firestore scaffold in place. Two Firestore databases exist; the second (`default`, non-free-tier) may be from a QC experiment. No compute services enabled yet.

---

### Project: `numista-morgan-pilot` (SMALL PILOT)
**Billing:** Numista.Ai (010E3C-D8346A-91A35E)
**Role:** Morgan pilot sandbox — storage services only. \$5 budget cap.

| Service | Details |
|---------|---------|
| **APIs** | Storage only (GCS). No Firestore, no Cloud Run, no Firebase. |
| **Budget** | \$5 cap |

**Assessment:** Very limited. Not useful for dev workloads. Budget too small.

---

### Project: `gen-lang-client-0504730428` (V3TEES / OLD)
**Billing:** My Billing Account (01A29C-F9BA5A-442E6B)
**Role:** Old V3Tees project — Artifact Registry, Firebase services. Likely dormant.

**Assessment:** Not relevant to Numista.AI sprint. Spending credit here would be wasted.

---

## TASK 2 — Proposal: Move Dev/Staging/Field Tester/Beta Load to `numista-qc`

### What the \$500 can fund (Oct 13 → Dec 29, 2026 ≈ 77 days ≈ 11 weeks)

#### Option A — Minimal Dev Backend (RECOMMENDED)
Enable Cloud Run on `numista-qc` and deploy `numista-backend` (dev Docker image) to it. All dev/QC testing hits this endpoint instead of prod.

| Item | Monthly Est. | Notes |
|------|-------------|-------|
| Cloud Run (dev backend, ~1 req/min load) | \$5–10/mo | 1 CPU / 512MB instance, min-instances=0 |
| Firestore reads/writes (dev load) | \$2–5/mo | Small collection, low traffic |
| GCS (dev uploads, coin images) | \$1–3/mo | ~10 GB dev test data |
| Cloud Build (CI deploys to QC) | \$2–5/mo | ~10 builds/week |
| Vertex AI / Gemini calls (dev scan testing) | \$10–30/mo | Dev scan tests with real Gemini |
| **Total est.** | **\$20–53/mo** | |

Over 11 weeks (2.75 months): **\$55–\$146 total** — well within \$500 budget.

#### Option B — Full Dev + Field Tester Environment
Add a separate Cloud Run instance for Field Tester traffic (authenticated beta users hitting QC backend instead of prod).

| Item | Monthly Est. | Notes |
|------|-------------|-------|
| Cloud Run (dev + field tester, ~10 req/min) | \$15–25/mo | 2 instances |
| Firestore (higher load) | \$5–15/mo | Field tester user docs |
| GCS | \$3–10/mo | Field tester uploads |
| Cloud Build | \$5–10/mo | More frequent CI |
| Vertex AI / Gemini (field tester scans) | \$20–60/mo | Real field tester usage |
| **Total est.** | **\$48–120/mo** | |

Over 11 weeks: **\$132–\$330 total** — within \$500 budget.

#### Option C — Add BigQuery Dataform Pipeline (Morgan SME data)
Use BigQuery (already enabled on numista-qc) for Morgan SME data pipeline / analytics. Dataform is already enabled.

| Item | Monthly Est. | Notes |
|------|-------------|-------|
| BigQuery storage + queries | \$5–15/mo | Morgan catalog data |
| Dataform runs | \$1–5/mo | ELT pipeline |
| **Additional to Option A** | **\$6–20/mo** | |

---

### Recommended Path (PROPOSAL — no action until Eric types YES per step)

1. **Enable Cloud Run API on `numista-qc`** — 1 gcloud command, no cost yet
2. **Deploy `numista-backend` dev image to `numista-qc` Cloud Run** — dev build only, `min-instances=0` (no idle cost)
3. **Point `kApiBaseUrl` (dev flavor)** at the new QC Cloud Run URL — Flutter flavor switch, no prod change
4. **Field Tester routing** — add QC_BACKEND Firebase Remote Config key; Field Tester app flavor uses QC URL
5. **Beta load testing** — run synthetic load tests against QC backend, not prod

**What does NOT move to QC:**
- Firebase Hosting (keep prod domain numista-vault.web.app)
- Prod Firestore (never touch prod data)
- Live Stripe webhooks (stay on prod)
- Secret Manager secrets (prod secrets stay in studio-9101802118-8c9a8; QC gets its own dummy secrets)

---

## TASK 3 — Risks, Rollback, Monthly Spend Estimate Oct–Dec

### Risks
| Risk | Mitigation |
|------|-----------|
| QC Firestore accidentally seeded with prod user data | Use synthetic test accounts only — never import prod Firestore export to QC |
| Credit expires Dec 29 before Thanksgiving launch | Option A costs \$55–146 total; well before expiry |
| Cloud Run cold starts slow QC testing | Set `--min-instances=0` (cheap) but document cold start; Field Tester can use `--min-instances=1` if needed (\$3–5/mo extra) |
| QC secrets differ from prod | QC backend gets stub secrets (test Stripe keys, etc.) — document them separately |
| Two Firestore DBs in numista-qc | Clean up the non-free-tier `default` DB if it's truly empty — saves money |

### Rollback
- If QC environment causes problems: disable Cloud Run API on numista-qc (zero cost instantly)
- Flutter app falls back to prod backend via config; no prod data at risk
- No IAM changes to prod project needed

### Monthly Spend Estimate (Oct–Dec)
| Period | Option A | Option B |
|--------|---------|---------|
| Oct 13–31 (2.5 wks) | \$12–30 | \$28–70 |
| Nov 1–30 (Thanksgiving sprint) | \$20–53 | \$48–120 |
| Dec 1–29 (post-launch) | \$15–40 | \$36–90 |
| **Total** | **\$47–123** | **\$112–280** |

**Buffer:** \$500 − \$18 Gemini credit = \$482 spendable. Option A leaves \$360–435 buffer. Option B leaves \$202–370 buffer. Both are safe.

**Recommendation:** Start with Option A (minimal dev backend). If Field Tester routing is needed before Thanksgiving, escalate to Option B — still well within budget.

---

## Summary
- **\$500 credit on My Billing Account expires 29 Dec 2026** — must spend before then or lose it
- **`numista-qc` is the right target** — Firebase/Firestore already provisioned, BigQuery enabled, on the correct billing account
- **Cloud Run needs to be enabled** on numista-qc (one command, Eric's YES required)
- **No prod changes required** — QC is fully isolated
- **Recommended spend: Option A (\$47–123 total)** — leaves \$380+ buffer for unexpected usage

> Next step: Eric types YES to enable Cloud Run on numista-qc and deploy dev backend.
