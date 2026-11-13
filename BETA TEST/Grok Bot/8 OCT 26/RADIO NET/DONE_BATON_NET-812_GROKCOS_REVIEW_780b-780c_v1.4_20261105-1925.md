# BATON NET-812 — Forward Review: Grok Bot CoS — FAILFIX Plans 780b Cards + 780c Images v1.4
**To:** Grok Bot CoS  
**Cc:** Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 (`ba2bfdb2`)  
**Date:** 5 November 2026, 7:25 PM ET  
**Target:** FAILFIX Plan 780b Cards v1.4 (`docs/FAILFIX_PLAN_NET-780b_CARDS_v1.4.md`) & 780c Images v1.4 (`docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.4.md`)  
**Goal:** GB CoS Review $\ge 95$ Pass $\rightarrow$ SAG Review $\ge 95$ Pass $\rightarrow$ Founder Eric Typed YES  
**Protocol Update:** Argon Reviewer DROPPED per Founder Eric YES 6:07 PM ET 5 Nov FIN OPS. Forward chain: AG plan -> GB CoS (>=95) -> SAG (>=95) -> Founder Eric typed YES.  
**Mode:** SCORE ONLY. Zero code execution, zero deployments, zero Firestore writes/seeding or security rules changes.

---

## Must-Fix Verification Checklist for Grok Bot CoS Reviewer:

1. [x] **Rollback Grounding:** Pinned pre-execute SHA `4c97c7f0`. Reverts execute commits cleanly back to `4c97c7f0`. No `9f04550a` checkout. No GCS deactivation guarantee claims under this $0/no-cloud YES.
2. [x] **Valuation Chip Line 3170:** Anchored to line 3170. Positive CDN retail price formatted and displayed whenever `valCpg > 0`, regardless of `enrichment_status`. Gold `'Valuation Pending'` chip rendered only when `valCpg <= 0`. Zero AI estimate fallback in primary card slot.
3. [x] **Negative Lookbehind Nickel/Cent Regex:** `r'(?:\b5c\b|(?<!\d)5¢|\bfive cents?\b|\bnickel\b)'` correctly handles real `¢` symbol without boundary failure and rejects `"15¢"` and `"25c"`.
4. [x] **Real Image API via `FutureBuilder`:** Imaginary `resolveReferenceAsset` struck. Real `CoinImageService.fetchReferenceImages(...)` async method utilized with `FutureBuilder<CoinImageResult>`, loading spinner, and defined placeholder.
5. [x] **Resolution Precedence Preserves 26EA:** 1. User photo -> 2. Canonical Mint (`resolveFromMap`) -> 3. Allowlisted own-origin direct URL -> 4. Reference library (`fetchReferenceImages`) -> 5. Local silhouette placeholder.
6. [x] **Expanded Own-Origin Allowlist:** Matches real `firebase.json:276` CSP. Includes `numista-reference-library`, `numista-catalog-assets`, and `numista-uploads-studio-*`. Rejects external Wikimedia URLs before network fetch.
7. [x] **Census & Hard $0 Scope:** 3,202 master entries from `docs/MISSING_IMAGES.csv`. Bulk scraping and GCS mutations explicitly out of scope. Zero deployments, zero Firestore writes.
