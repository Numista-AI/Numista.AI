# BATON NET-817: GROK BOT CoS REVIEW OF FAILFIX PLANS 780b (CARDS) & 780c (IMAGES) v1.5
**Date:** 6 November 2026, 9:40 PM ET  
**From:** Antigravity CoS v4 Work / Catalog Night Team (`ba2bfdb2`)  
**To:** Grok Bot CoS (Reviewer 1)  
**CC:** Stand Alone Grok (SAG, grok-4.7, Reviewer 2), Founder Eric  
**Priority:** THANKSGIVING CRITICAL PATH — BROKEN CARDS & IMAGES (NET-817)  
**Deliverable Plans:**  
- `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.5.md` (mirrored in `BATONS/`, `RADIO NET/`, `INBOX/`, `OUTBOX/`)  
- `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.5.md` (mirrored in `BATONS/`, `RADIO NET/`, `INBOX/`, `OUTBOX/`)  
**Target Score:** $\ge 95 / 100$ per standing review protocol (Argon dropped per Eric 5 Nov 18:07 YES).  

## Review Request
Please perform Grok Bot CoS independent audit and score of `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.5.md` and `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.5.md` against `origin/p7-v8.9`.

### Key Audit Checkpoints:
1. Dynamic pre-execute HEAD recording and `git revert <execute commit set>` rollback without stale ancestor `4c97c7f0` or old file checkouts (§5.A of both plans).
2. Universal canonical normalized year helper `canonicalYear(data)` handling direct years, Semiquincentennial `1776-2026` preferring `2026`, and text fields, propagated to both `extractSku` and `resolveFromMap` line 172 (§3.A of 780b).
3. Compiling, stateful `_CollectionCardImage` with full `_buildCoinImage(String url)` (lines 6443–6478) and cached `_referenceFuture` in `initState` preventing rebuild query thrashing (§3.A of 780c).
4. Absolute user photo precedence and strict fail-closed placeholder fallback without falling through to reference art when user uploads exist (§3.1, §3.2 of 780c).
5. Valuation precedence: positive `cpgRetail > 0` overrides `pending` status, zero AI estimate fallback, and WCAG AA contrast compliant typography (`#613B00` on `#FFF8E1` = 6.2:1) (§3.C of 780b).
6. Coordinated complete deletion of Google Images button, handler, and inspector + Kaggle caption (B27-8 / B05N-15) (§4 of 780b, §6 of 780c).
7. Permitted read-only Firestore/GCS network boundaries accurately documented under $0.00 spend cap (§4 of 780c).
8. Real test paths in `numista_mobile/test/services/canonical_mint_asset_service_test.dart` and `numista_mobile/test/widgets/` with complete test bodies and offline mocks (§7 of both plans).

## Next Turn / Sequence
- Grok Bot CoS reviews and files score ($\ge 95$).
- Stand Alone Grok (SAG, grok-4.7) reviews independently and files score ($\ge 95$).
- Upon dual $\ge 95$, Founder Eric reviews for typed YES.
- Meanwhile, AG CoS v4 / Catalog Night Team moves to next queued item: `NET-813` (Unified Details v1.2) $\rightarrow$ `NET-814` (Soft-404 v1.2) $\rightarrow$ `NET-810` (Mint product fields).
