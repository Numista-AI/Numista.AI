# Walkthrough — Sprint 3: Monetization, Estate Expansion & Public Feeds (2026-07-26)

Sprint 3 has been fully implemented, verified, and pushed to `origin/dev`. This milestone advances overall project completion from **72.2% → 81.5%**.

---

## 🚀 Accomplishments & Architecture Completed

```
========================================================================================
                                SPRINT 3 COMPLETED ARCHITECTURE
========================================================================================
  [ Flutter Web: /wishlist/{token} ] ----> (GET /public_wishlists/{token}) -> [ Firestore (Public Read-Only) ]
  [ Flutter Web / Desktop UI       ] ----> (GET /api/news/feed) ------------> [ FastAPI (12h Cache / De-dup) ]
  [ wishlist_screen.dart           ] ----> (POST /api/wishlist/create-share) -> [ FastAPI (Backend Write Only) ]
  [ wishlist_screen.dart           ] ----> (POST /api/epn/normalize) --------> [ FastAPI (Dictionary + Gemini) ]
  [ attorney_portal.dart           ] ----> (GET /api/estate/generate-url) ---> [ FastAPI (GCS Signing + Audit Log) ]
  [ stripe_service.dart            ] ----> (POST /api/stripe/checkout) ------> [ Stripe API + Idempotent Webhook ]
========================================================================================
```

### 1. Public Wish List & EPN Monetization
- **Backend-Only Snapshot Creation**: `POST /api/wishlist/create-share` in `main.py` generates an opaque token (`wishlist_xxx`) and writes denormalized wishlist snapshots directly via Firebase Admin SDK.
- **Strict Firestore Security Rules**: Added rules for `/public_wishlists/{token}` permitting `allow read: if true;` and `allow write: if false;` (clients cannot write directly).
- **Public Wishlist Web View**: Built `PublicWishlistViewScreen` with a `"Public Gift Wish List — Snapshot as of [Date]"` header, read-only item cards, and "Find on eBay" buttons attached to EPN campaign `5339148752`. Registered deep-link routing in `main.dart` for clean web URLs (`numista.ai/wishlist/{token}`).
- **EPN Query Normalization**: `POST /api/epn/normalize-search` maps informal collector nicknames (`"wheatie"`, `"jfk half"`, `"mercury dime"`) to standard US Mint nomenclatures (`"Lincoln Wheat Cent"`, `"Kennedy Half Dollar"`) via zero-latency dictionary lookup with Gemini LLM fallback.

### 2. Attorney Portal & 5-State Legal Engine
- **Backend GCS Signed Link Generation**: `GET /api/estate/generate-appraisal-url` generates 7-day GCS signed links securely on Cloud Run without exposing GCP service account credentials to client code.
- **Audit Logging**: Logs every signed link issuance to `/users/{uid}/estate_audits` (capturing requester UID, state selected, expiration date, IP address, and user agent).
- **5-State Probate Engine**: Expanded `estate_fiduciary_service.dart` to support legal statutory rules and small estate thresholds for **New Jersey (NJ)**, **Florida (FL)**, **California (CA)**, **Texas (TX)**, **South Carolina (SC)**, **New York (NY)**, and **North Carolina (NC)**, enforcing expiration safety checks against `/config/probate`.
- **Legal Disclaimer**: Added a prominent non-dismissible legal notice banner to `AttorneyPortalScreen`.

### 3. Stripe Billing Integration & Webhook Gatekeeper
- **Stripe Checkout & Portal Endpoints**: `POST /api/stripe/create-checkout-session` and `POST /api/stripe/create-customer-portal` in `main.py` connected to `stripe_config.py` and `tier_gatekeeper.py`.
- **Webhook Signature & Idempotency**: `POST /api/stripe/webhook` verifies `stripe-signature` headers and checks Firestore `/stripe_events/{eventId}` for deduplication before handling `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, and `invoice.payment_failed`.
- **Client Service & Config**: Built `stripe_service.dart` and created `numista_backend/.env.template`.

### 4. Market Intel Live Numismatic News Feed Proxy
- **CORS-Free Proxy Endpoint**: `GET /api/news/feed` in `main.py` aggregates top 5 news sources (CoinWorld, US Mint, CoinWeek, Greysheet) with 12-hour in-memory caching and title deduplication.
- **Client Service**: Created `market_news_service.dart` with offline `SharedPreferences` caching, wired directly to `HomeDashboard`.

---

## 🧪 Verification Results

1. **Backend Unit Tests (`pytest`)**:
   - `16/16` tests passed 100% in 9.75 seconds.
2. **Python Syntax Compilation**:
   - `python -m py_compile` passed clean across `main.py`, `stripe_config.py`, and `tier_gatekeeper.py`.
3. **Dart Code Analyzer**:
   - `0 errors` found across `numista_mobile`.
4. **Git Synchronization**:
   - Pushed cleanly to `origin/dev` (commit `063f020`).

---

## 📁 Modified & New Source Files

- **[firestore.rules](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/firestore.rules)**: Added public read / backend-only write rules for `/public_wishlists` and `/stripe_events`.
- **[main.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py)**: Added Sprint 3 proxy endpoints for EPN normalization, wishlist creation, GCS signing, Stripe Checkout/webhooks, and news feed aggregation.
- **[.env.template](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/.env.template)**: Environment key template for Stripe credentials.
- **[public_wishlist_view_screen.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/public_wishlist_view_screen.dart)**: Read-only web snapshot view.
- **[stripe_service.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/stripe_service.dart)**: Stripe checkout and customer portal client.
- **[market_news_service.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/market_news_service.dart)**: News proxy client with offline cache.
- **[main.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/main.dart)**: Added `/wishlist/{token}` deep-link web route handler.
- **[wishlist_screen.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/wishlist_screen.dart)**: Added Share Wish List action button and modal.
- **[estate_fiduciary_service.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/estate_fiduciary_service.dart)**: Added 5-State probate engine rule evaluator.
- **[attorney_portal_screen.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/attorney_portal_screen.dart)**: Added legal disclaimer banner.
- **[home_dashboard.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/home_dashboard.dart)**: Connected Market Intel feed to `MarketNewsService`.
- **[good_ideas_tracker.md](file:///c:/Users/ericd/Documents/MyVertexProject/Good%20Ideas%20Tracker/good_ideas_tracker.md)**: Updated progress metrics to **81.5%**.
