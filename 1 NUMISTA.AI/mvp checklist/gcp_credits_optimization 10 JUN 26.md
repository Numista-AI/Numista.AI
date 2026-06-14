# Numista.AI — Google Cloud for Startups Credits Optimization Guide

> **Status:** June 2026 | **Project:** `studio-9101802118-8c9a8` | **Credits expiry:** ~End of 2026

---

## Executive Summary

You're currently using GCP credits on a narrow slice of available services: Cloud Run, Cloud Firestore, Cloud Storage, Firebase Hosting, and Gemini via Vertex AI. This is a solid foundation, but **a large portion of your credit budget is likely untouched** — and with expiry approaching, this is the right time to accelerate investment into services that will make Numista.AI more capable, scalable, and defensible.

---

## 🔍 What You're Currently Using (and Known Costs)

| Service | How You Use It | Est. Monthly Impact |
|---------|---------------|---------------------|
| **Cloud Run** | `scan-service`, `sync-worker`, `main-app` | Low-Med (pay per request) |
| **Cloud Firestore** | Primary DB — all coins, programs, wishlists, commands | Med (reads/writes scale with users) |
| **Cloud Storage (GCS)** | Reference images (~4.5M row index), microscope uploads | Med (4.5M+ objects) |
| **Gemini via Vertex AI** | `gemini-3-flash-preview` for scan + coin ID + AI chat | Med-High (token-based) |
| **Firebase Hosting** | Flutter web build | Low (static files) |
| **Firebase Auth** | User authentication | Low (free tier) |
| **Artifact Registry** | Docker images for Cloud Run | Low |

> [!NOTE]
> Your GCS reference library (~4.5M row index) is your biggest storage cost driver. Make sure CORS, caching headers (`Cache-Control: public, max-age=31536000`), and CDN delivery are properly configured — this reduces egress costs significantly.

---

## 🚀 High-Value Services You Should Start Using NOW

These services are **included in GCP for Startups credits** and directly match your roadmap items.

---

### 1. ✅ Vertex AI — Tune a Custom Gemini Model for Coin ID

**Why:** You already have training data (`Coin program Training Data/`, `training_output/`, annotation pipelines). Right now you're using a generic `gemini-3-flash-preview` for coin identification. A **fine-tuned model** will dramatically improve accuracy on numismatic images.

**How to activate:**
- Go to **Vertex AI Studio → Tuning** in the Cloud Console
- Use your existing labeled checklist/coin image data
- Fine-tune `gemini-1.5-flash` or `gemini-2.0-flash` on coin ID tasks
- Deploy as a Vertex AI endpoint and point `identify_coin.py` at it

**Credit cost:** Fine-tuning jobs consume GPU hours — **perfect for burning credits** before expiry. A tuning run on ~10K examples costs a fraction of what it would on a paid account.

**Roadmap connection:** Directly enables your *Human-AI Trainer screen* and improves the hardware agent's coin ID confidence.

---

### 2. 🗄️ Cloud SQL (PostgreSQL) — Replace Ad-Hoc CSV/Log Files

**Why:** You have dozens of `.csv`, `.txt`, and `.json` files in `numista_backend/` that serve as operational data stores (master logs, missing image lists, staging files). This is technical debt that creates sync issues and makes querying hard.

**How to activate:**
- Spin up a **Cloud SQL PostgreSQL** instance (micro, `us-central1` — same region as your Cloud Run)
- Migrate: `numista_master_log.csv`, staging CSVs, `missing_coin_images.csv`, `local_images.csv`
- Your `app.py` already has DB-like query patterns — connect via Cloud SQL Auth Proxy (you already have `cloud-sql-proxy.exe`!)

**Credit cost:** A `db-f1-micro` instance is ~$7–9/month. With credits, run a `db-g1-small` or even `db-custom-2-7680` to handle admin workloads comfortably.

**Win:** Eliminates file sync race conditions, makes `audit_*.py` scripts queryable in seconds vs. file scans.

---

### 3. 📊 BigQuery — Analytics on Your Collection Data

**Why:** You're already thinking in data pipelines. BigQuery is free for the first 10GB of storage and 1TB of queries/month, and **startup credits cover well beyond that**.

**How to activate:**
- Export Firestore snapshots to BigQuery using the **Firestore → BigQuery Export** connector (built-in in Firebase)
- Analyze: most popular coin programs, scan success rates, user growth, AI confidence trends
- Run ad-hoc queries against your `numista_master_log.csv` data

**Immediate queries you could run:**
```sql
-- Which programs have the most user-owned coins?
SELECT program_series, COUNT(*) as coins_owned FROM coins GROUP BY 1 ORDER BY 2 DESC;

-- What's the average AI confidence score by coin type?
SELECT denomination, AVG(CAST(verification_confidence AS INT64)) FROM coins GROUP BY 1;
```

**Credit cost:** Near-zero for your data volumes. But this unlocks **business intelligence** you can't get from Firestore alone.

---

### 4. 🔍 Vertex AI Search — Power Your Reference Library

**Why:** Users currently browse/search coins via the Flutter UI hitting Firestore. With ~4.5M reference entries, search performance and relevance degrade. **Vertex AI Search** (formerly Enterprise Search) gives you a production-grade semantic search engine.

**How to activate:**
- Create a Vertex AI Search data store, import from GCS or BigQuery
- Replace or augment your `reference_service.dart` Firestore queries with Vertex AI Search API calls
- Supports natural language queries: *"1921 Morgan Dollar MS-63 Denver"*

**Credit cost:** First 1,000 search queries/month free; credits cover heavy testing and production ramp.

**Win:** Users find coins faster, and it directly improves the `AIChatScreen` experience.

---

### 5. ⚙️ Cloud Scheduler + Cloud Tasks — Replace Windows Task Scheduler

**Why:** Your daily backup runs via Windows Task Scheduler on your local machine. If your machine is off, the backup relies on a `StartWhenAvailable` flag. Critical jobs like Firestore data sync, GCS image indexing, and PCGS token refresh should not depend on your laptop being on.

**How to activate:**
- **Cloud Scheduler:** Cron trigger → Cloud Run endpoint or Pub/Sub topic
- **Cloud Tasks:** Queue-based execution for bulk jobs like `sync_local_images_to_gcs.py` and `run_phase2_*.py` ingestion scripts

**Specific jobs to migrate:**
| Current | Migrate To |
|---------|-----------|
| `numista_auto_backup.ps1` (Windows Task Scheduler) | Cloud Scheduler → GitHub Actions (or Cloud Run job) |
| `sync_local_images_to_gcs.py` (manual) | Cloud Scheduler → Cloud Run Job |
| `build_image_index.py` (manual) | Cloud Scheduler weekly trigger |
| `audit_*.py` scripts (manual) | Cloud Scheduler nightly |

**Credit cost:** Cloud Scheduler is $0.10/job/month. Practically free.

---

### 6. 🔔 Firebase Cloud Messaging (FCM) — Push Notifications

**Why:** Your wishlist screen has eBay live pricing, and the roadmap mentions eBay alerts. FCM is **completely free** and Firebase-native — you already use Firebase Auth and Firestore.

**How to activate:**
- Add FCM to your Flutter app (already in the Firebase ecosystem)
- When a wishlist coin drops in price on eBay → trigger a FCM push via Cloud Function
- Hardware scan completed → push notification to mobile app (replaces the 500ms polling loop)

**Win:** Eliminates the `GET http://localhost:5000/get-status` 500ms polling — replace with a real-time FCM event from the hardware agent writing to Firestore, which triggers a Cloud Function that sends FCM.

---

### 7. 🤖 Cloud Functions (2nd Gen) — Event-Driven Architecture

**Why:** You have `functions/` directory in `numista_backend` but it appears underutilized. You're doing many operations synchronously in Cloud Run that should be event-driven.

**High-value functions to build:**
```
Firestore onCreate: users/{uid}/coins/{docId}
  → Trigger "Deep Dive AI Report" async (Gemini Pro analysis)
  → Send FCM notification: "Your coin has been added!"

GCS onFinalize: microscope/{email}/...
  → Auto-run PCGS enrichment
  → Update Firestore coin record with final GCS URLs

Cloud Scheduler daily:
  → Refresh eBay prices for all wishlist items
  → Rotate PCGS bearer token check
  → Nightly Firestore → BigQuery export
```

**Credit cost:** 2M free invocations/month. Credits cover compute beyond that.

---

### 8. 🗺️ Vertex AI — Grounding with Google Search for AI Chat

**Why:** Your `AIChatScreen` uses Gemini for numismatic Q&A but has no persistent context and no real-world grounding. Vertex AI now supports **Grounding with Google Search** — the model can search current numismatic news, coin prices, and PCGS population reports in real-time.

**How to activate:**
- Enable the `google_search_retrieval` tool in your Gemini API calls
- Replace the current stateless chat with **conversation history stored in Firestore** (already on your roadmap)
- Add grounding to give users up-to-date coin market data

**Win:** AI Chat becomes dramatically more useful and accurate for coin valuation questions.

---

### 9. 🖼️ Vision AI / Document AI — Backup Scan Pipeline

**Why:** You use `gemini-3-flash-preview` for checklist OCR. Consider adding **Document AI** as a fallback or pre-processor. Document AI's Form Parser can extract checkbox states and text with high confidence, then pass structured results to Gemini for semantic matching.

**How to activate:**
- Try **Document AI Form Parser** on your checklist PDFs
- If checkboxes are pre-extracted, you reduce Gemini token usage by ~30–40% (less vision work)

**Credit cost:** Document AI is ~$1.50/1000 pages. Great for processing your existing checklist PDFs.

---

## 💰 Cost Optimization Quick Wins (Save Credits for What Matters)

> [!TIP]
> These don't spend more credits — they ensure you're not wasting what you have.

### GCS Optimization
- Confirm `Cache-Control: public, max-age=31536000` is set on all reference images (already documented in your architecture)
- Set **Lifecycle rules** on `microscope/` objects: archive to Nearline after 90 days, Coldline after 1 year
- Run `gsutil du -sh gs://studio-9101802118-8c9a8-uploads/` to see your actual storage breakdown

### Cloud Run Optimization
- Set **minimum instances to 0** for `sync-worker` (cold start is acceptable for background jobs)
- Set **minimum instances to 1** for `scan-service` only if latency on first scan is a UX problem
- Review `--concurrency` setting — `gemini-3-flash-preview` calls are I/O bound, so higher concurrency (up to 80) per instance reduces instance count

### Firestore Reads
- Your `reference_library_service.dart` streams from GCS. Confirm you're not re-reading the 4.5M row index on every app launch. Add local/in-memory caching.
- Add **Firestore indexes** for your most common queries (programs by category, coins by year+denomination)

### Gemini Token Usage
- Your chunking-by-page logic already reduces tokens ~65% — great
- Consider caching the `global_programs/{program_id}` Firestore read in Cloud Run's memory between requests (it's read-only data)

---

## 📅 Prioritized Action Plan (Before Credits Expire)

| Priority | Action | Effort | Credit Value | Timeline |
|----------|--------|--------|-------------|----------|
| 🔴 HIGH | Fine-tune Gemini on coin ID training data | Medium | $$$ (GPU hours) | This month |
| 🔴 HIGH | Enable Firestore → BigQuery export | Low | $ | This week |
| 🔴 HIGH | Migrate batch jobs to Cloud Scheduler | Low | $ | This week |
| 🟡 MED | Add Cloud SQL for operational CSV data | Medium | $$ | Next 2 weeks |
| 🟡 MED | Build 2–3 Cloud Functions (Deep Dive, eBay refresh) | Medium | $$ | Next month |
| 🟡 MED | Add FCM push notifications (hardware scan complete, eBay alerts) | Medium | $ | Next month |
| 🟡 MED | Set up Vertex AI Search for reference library | Medium | $$ | Next month |
| 🟢 LOW | Enable Grounding with Google Search in AI Chat | Low | $$ | When AI chat is persistent |
| 🟢 LOW | Add Document AI to checklist scan pipeline | Medium | $$ | When scan accuracy needs improving |
| 🟢 LOW | GCS Lifecycle rules + storage audit | Low | Saves $ | This week |

---

## 🎓 Key Links

- [GCP for Startups Dashboard](https://console.cloud.google.com/billing) — Check your credit balance and expiry date
- [Vertex AI Tuning](https://console.cloud.google.com/vertex-ai/studio/tuning) — Start a fine-tuning job
- [Firestore → BigQuery Export](https://firebase.google.com/docs/firestore/solutions/bigquery-export) — One-time setup
- [Cloud Scheduler](https://console.cloud.google.com/cloudscheduler) — Replace Windows Task Scheduler
- [Cloud Functions 2nd Gen](https://console.cloud.google.com/functions) — Event-driven triggers
- [Vertex AI Search](https://console.cloud.google.com/gen-app-builder) — Semantic search on your reference library

---

> [!IMPORTANT]
> **Check your actual credit balance and expiry date** in the GCP Billing Console. If you have, say, $50K in credits vs $5K, the strategy above shifts — more credits = bigger bets like running a fine-tuning job on a larger dataset, spinning up a Cloud SQL instance with higher specs, or deploying Vertex AI Search at scale.
> 
> Navigate to: **Cloud Console → Billing → Credits**

