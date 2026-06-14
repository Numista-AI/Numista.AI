# Numista.AI — Launch Readiness Assessment & Next Sprint Plan
**Date:** June 9, 2026 | **Target Launch:** November 1, 2026 | **Time Remaining:** ~20 weeks

---

## TL;DR — Are We On Pace?

> **Verdict: Yes — but the margin is tighter than it looks.**

The platform is architecturally sound and feature-rich for a Beta. The core loop works end-to-end: invoice → Review Hub → commit → collection, plus microscope scan, PCGS import, checklist scan, and AI chat. That's legitimately impressive for where the project started.

The risk to November 1 is **polish debt and untested paths** — not missing architecture. The items below represent the gap between "works for Eric" and "works for strangers."

---

## Current Platform State (as of June 9, 2026)

### ✅ Working / Solid
| Feature | Status |
|---------|--------|
| Flutter web app (desktop + mobile layout) | ✅ Deployed, responsive |
| Firebase Auth (email + Google Sign-In) | ✅ Working |
| My Collection screen (data grid, sort, filter, inline edit) | ✅ Solid |
| Coin Detail screen (4-tab: Details, Financials, Provenance, AI Insights) | ✅ Complete |
| Add Coins Hub (Manual, PCGS, Checklist, Roll, CSV tabs) | ✅ Working |
| Review Hub (commit, bulk edit, item-type badges, Set cards) | ✅ Implemented |
| Invoice PDF ingestion + AI extraction → Review Queue | ✅ Working |
| Universal item routing (coin/set/stamp/supply/currency/medal) | ✅ In code, needs backend deploy |
| Supplies Screen | ✅ Built |
| Wishlist + eBay EPN live prices | ✅ Working |
| Microscope Scanner (hardware agent, OpenCV, Gemini Vision) | ✅ Working (single-user) |
| AI Checklist Scanner (Gemini Vision → checklist_entries) | ✅ Working |
| PCGS Import (cert#, CSV, duplicate detection) | ✅ Working |
| AI Chat (Gemini, numismatic Q&A) | ✅ Working |
| Home Dashboard (portfolio metrics, spot prices, news, release notes) | ✅ Working |
| Human AI Trainer (grade review + nickname community board) | ✅ Implemented |
| Onboarding Wizard (guest mode, guided first-run) | ✅ Working |
| Guest/Browse Demo mode | ✅ Working |
| Supplies inventory screen | ✅ Built |
| Automated daily GitHub backup | ✅ Running |
| Cloud Run backend (scan service, review commit, break-up-set) | ✅ Deployed |
| Reference library (6k+ Kaggle images in GCS + Firestore) | ✅ Uploaded |
| Live spot prices (metals-api.com) | ✅ Working |
| NewsAPI numismatic feed | ✅ Working |

### 🟡 Partially Done / Needs Work
| Feature | Gap |
|---------|-----|
| Universal item routing backend | Designed (Jun 8 plan), **not yet deployed to Cloud Run** |
| Human AI Trainer backend | Grade review endpoints exist, but `/api/grade_review/stats` and `/api/nicknames/*` **need verification** |
| Binder Scan (Human AI Trainer, `_CoinCropImage`) | `/api/coin_crop` endpoint referenced — confirm it's in Cloud Run |
| Training data pipeline | Conversation `0ece54a1` — saving training data for Gemini fine-tuning |
| Firestore security rules | New collections (`pending_items`, `supplies_log`) need rules added |
| Production build checklist | Service worker kill-switch process documented but not yet verified end-to-end |
| App version counter in release notes | Still showing `v3.2 Beta / 2026-04-25` — needs updating |

### 🔴 Not Built / Known Gaps
| Feature | Notes |
|---------|-------|
| Multi-user hardware agent | `USER_EMAIL` hardcoded to `eric@numista.ai` |
| AI Chat session persistence | No Firestore-backed history across sessions |
| iOS App Store distribution | Needs Apple Developer account + physical Mac |
| Deep Dive AI reports (Gemini Pro) | Placeholder/stub in current AI Insights tab |
| eBay snipe/alert integration | Wishlist has pricing, no alert/snipe flow |
| Numista.com API integration | Originally planned in Apr 10 roadmap, not done |
| "Similar Coins" reference panel | Planned Apr 12, not implemented |
| Live silver spot price (melt value) | Hardcoded `$32.50/troy oz` in hardware agent |
| Parallel multi-page checklist scanning | Sequential only |
| Subscription / billing tier logic | Not started |

---

## Gap Analysis: What Matters for November 1

### Launch Definition
For November 1, "launch" most likely means:
- Public-facing web app that a stranger can sign up for and use
- Stable enough for invited beta users (the AJ Seaman account + others)
- Core features working without hand-holding
- No embarrassing crashes on happy paths

This is **not** full iOS App Store + Google Play launch. That's a different bar.

### Critical Path Items (Launch Blockers)
These must be done before handing the URL to anyone new:

1. **Auth error investigation** — Conversation `4c976d33` shows account authentication errors being investigated. Auth is the front door; if it's broken for new users, nothing else matters.
2. **Backend: Deploy universal item routing** — The Jun 8 plan is written; it needs to be deployed.
3. **Firestore security rules** — `pending_items` and `supplies_log` collections have no rules yet. Any security scan will find this.
4. **Production build validation** — The `PROD_BUILD_CHECKLIST.md` steps have never been run on the current codebase. Do a clean production build.
5. **Multi-user onboarding** — The `jseaman1204@gmail.com` account needs to fully work. Test the entire flow as that user: sign up → invoice upload → commit → collection.

### High-Value Items (Makes Launch Worth It)
6. **"Similar Coins" reference panel** — Visual delight moment. Easy to implement with existing reference library.
7. **Live melt value** (replace `$32.50` hardcode) — Needed for hardware agent to be useful to anyone.
8. **AI Chat session persistence** — Right now conversations vanish on page reload. Basic expectation.
9. **Release notes update** — Change `v3.2 Beta / 2026-04-25` to current date.
10. **Welcome/marketing page polish** — The `welcome_screen.dart` and `login_screen.dart` are the first impression.

### Can Wait (Post-Launch)
- iOS App Store (requires Apple hardware, 4-8 weeks of own lead time, not this sprint)
- Numista.com API
- Subscription/billing tiers
- Multi-user hardware agent
- Parallel checklist scanning

---

## 30–40 Hour Sprint Plan (Next Work Block)

Organized into 5 work blocks. Estimated hours are per block. Total: ~35 hours.

---

### 🔴 Block 1 — Foundation & Deploy (6–8 hours)
*These are gate items. Nothing else matters if these are broken.*

- [ ] **B1.1** (2h) — Investigate and fix the authentication errors from conversation `4c976d33`. Confirm new account signup works end-to-end for a fresh user.
- [ ] **B1.2** (3h) — Deploy the June 8 universal item routing plan to Cloud Run. This includes: updated extraction prompt, routing logic (`item_type` field), helper functions `_parse_cost` / `_apply_defaults`, and updated return value. Then re-process the 4 problem PDF files and verify stamp disambiguation.
- [ ] **B1.3** (1h) — Add Firestore security rules for `pending_items` and `supplies_log` collections (same pattern as `review_queue`).
- [ ] **B1.4** (1h) — Verify all Human AI Trainer backend endpoints are live: `/api/grade_review/stats`, `/api/grade_review/queue`, `/api/grade_review/submit`, `/api/nicknames/stats`. Fix any that are missing.

---

### 🟡 Block 2 — jseaman1204 Account & Invoice Pipeline (6–8 hours)
*The intended first real user. Everything must work for them.*

- [ ] **B2.1** (2h) — Re-process all 47 invoice files through the updated backend for the `jseaman1204@gmail.com` account. Verify: stamps go to `pending_items`, supplies to `supplies_log`, sets show in Review Hub with Break Up / Keep as Set buttons.
- [ ] **B2.2** (2h) — Walk through the entire review-and-commit flow for jseaman's coins. Fix any commit errors. Verify `source_file` traceability shows correctly.
- [ ] **B2.3** (2h) — Run `missing_images_report.py` for the jseaman account. Address the top 20 coins missing images by running Phase 2 ingestion scripts for those programs.
- [ ] **B2.4** (1h) — Verify the Supplies screen shows all supply items from jseaman's invoices with correct totals.

---

### 🟠 Block 3 — Production Build + Security Pass (4–5 hours)
*Run the PROD_BUILD_CHECKLIST for real.*

- [ ] **B3.1** (1h) — Run `flutter analyze`. Fix any errors or warnings (there should be zero for a prod build).
- [ ] **B3.2** (1h) — Execute PROD_BUILD_CHECKLIST.md: remove service worker kill-switch, bump `pubspec.yaml` version to `v3.5`, run `flutter build web --release`.
- [ ] **B3.3** (1h) — Deploy to Firebase Hosting. Smoke-test live site: Auth → Dashboard → Collection → Add Coins → Review Hub → Commit.
- [ ] **B3.4** (1h) — Review Firestore rules comprehensively. Ensure users can only read/write their own `users/{email}` paths.
- [ ] **B3.5** (1h) — Test the app in incognito as a brand-new user (no pre-existing data). Confirm the onboarding wizard fires correctly and the guest mode works.

---

### 🟢 Block 4 — High-Value Feature Polish (10–12 hours)
*These turn "it works" into "it's impressive."*

- [ ] **B4.1** (3h) — **"Similar Coins" reference panel.** In `coin_detail_screen.dart`, add a "Similar in Reference Library" row on the Details tab. Query `reference_library` Firestore by denomination + year (±5 years), display top 6 thumbnail images. Tap to expand. This is a big delight moment.
- [ ] **B4.2** (2h) — **Live melt value** in hardware agent. Replace the hardcoded `$32.50` in `numista_hardware/pcgs_service.py` with a live metals API call (metals-api.com free tier). Cache for 1 hour.
- [ ] **B4.3** (2h) — **AI Chat session persistence.** Store conversation history in Firestore `users/{email}/ai_chat_sessions/{sessionId}`. Load last 10 messages on screen open. This is a basic user expectation.
- [ ] **B4.4** (2h) — **Login screen polish.** `login_screen.dart` is the public face. Review it critically: Is the value proposition clear? Is the layout premium? Add 2-3 feature callout bullets ("Scan your collection in seconds", "AI-powered coin identification", "Track your portfolio value live").
- [ ] **B4.5** (1h) — **Release notes update.** Add a `v3.5 Beta` entry in `home_dashboard.dart` reflecting June 2026 work: universal item routing, supplies tracking, binder scan, AI trainer board, set lifecycle management.
- [ ] **B4.6** (1h) — **Silver spot price in collection view.** Add 🥈 silver badge and live melt value to the `My Collection` data grid (currently only in the scan result).

---

### 🔵 Block 5 — Training Data & AI Quality (5–6 hours)
*Improves scan accuracy — directly affects user trust.*

- [ ] **B5.1** (2h) — Follow up on conversation `0ece54a1` (Saving Numista Training Data). Ensure the training data pipeline for Gemini fine-tuning is saving correctly to the right format. Confirm the dataset is growing with each scan.
- [ ] **B5.2** (2h) — Batch-label the 1,444 `balabaskar` Kaggle images with unknown metadata. Run `numista_hardware/batch_label_reference_images.py` (or create it) to call Gemini Vision on each and update their Firestore docs with `denomination` and `year`.
- [ ] **B5.3** (1h) — Run `flutter analyze` one final time and verify 0 issues. Do a smoke-test of the full app after all changes in Blocks 1–4 are integrated.

---

## Hour Summary

| Block | Focus | Est. Hours |
|-------|-------|-----------|
| Block 1 | Foundation & Deploy | 6–8h |
| Block 2 | jseaman Account Pipeline | 6–8h |
| Block 3 | Production Build + Security | 4–5h |
| Block 4 | Feature Polish | 10–12h |
| Block 5 | Training Data & AI Quality | 5–6h |
| **Total** | | **31–39 hours** |

---

## 20-Week Remaining Roadmap (Rough)

| Weeks | Theme |
|-------|-------|
| Weeks 1–2 (now) | This sprint — foundation + polish |
| Weeks 3–5 | Beta user onboarding (5–10 invited users). Collect feedback. Fix bugs. |
| Weeks 6–8 | Subscription/billing tier design + Stripe integration |
| Weeks 9–11 | iOS App Store prep (needs Apple hardware — plan for this now!) |
| Weeks 12–14 | Marketing site, landing page, SEO |
| Weeks 15–17 | Load testing, performance optimization, analytics |
| Weeks 18–19 | Final QA, security audit, app store submission |
| Week 20 | 🚀 November 1 Launch |

> [!WARNING]
> **iOS is the longest-lead-time item.** App Store review takes 1–7 days, but preparing a submission (provisioning profiles, screenshots, App Store Connect setup, TestFlight beta) takes 2–4 weeks of focused effort — and requires Apple Developer Program membership ($99/year) and a physical Mac. If iOS at launch is a requirement, this needs to start by **mid-August at the latest**.

> [!IMPORTANT]
> **The pace question answered:** At ~35 hours per sprint and running 2 sprints/month, you have roughly 160–170 hours of work available before November 1. The gap items above represent ~35 hours. That leaves 130+ hours for beta polish, marketing, iOS prep, and buffer. **You're on pace — provided you start treating the next 4 weeks as pre-launch beta hardening, not feature development.**

---

## Recommended First Day Back (Tomorrow)

1. `B1.1` — Fix the auth error first. Nothing else matters.
2. `B1.2` — Deploy the Jun 8 routing plan to Cloud Run.
3. `B2.1` — Run jseaman's invoices through the updated backend.
4. End of day: smoke-test the live site as jseaman1204@gmail.com.
