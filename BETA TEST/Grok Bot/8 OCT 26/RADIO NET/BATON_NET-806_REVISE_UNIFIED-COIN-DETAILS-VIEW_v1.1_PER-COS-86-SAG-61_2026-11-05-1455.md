# BATON NET-806 - To: AG CoS v4 - PLAN ONLY: Unified Coin Details View v1.1 (CoS 86 / SAG 61 FAIL)
Source: GB CoS ~2:55 PM ET 5 Nov. Argon 97, EGM 98; CoS **86 FAIL**, SAG **61 FAIL**. Eric's two asks (values stay until Close across Prev/Next; unchecked Congress.gov laws labeled) ARE met — keep them. Score file: `COS_SCORE_NET-798_UNIFIED-COIN-DETAILS-VIEW_20261105.md`. **Take after NET-805** (build window 10-16 Nov).

Fix:
1. `StorageLocationPinService` does not exist — stop treating it as real; storage stays hidden until a PIN design gets a separate YES.
2. Step 3 call sites: 2736, **3044**, **2761**, **2773**, **3122**; re-quote verbatim (3043/2758/911/913 are wrong).
3. Public/guest mode hide-list (no purchase, cost, invoice, retailer, storage, PIN, Edit/Delete/Verify/Wishlist) — or drop "Public Catalog" from launchers.
4. Value source = CDN CPG retail only; no wholesale; AI value labeled; Live eBay not a public price.
5. Feature flag + preview channel + rollback; don't delete legacy views in the same build; code-freeze before 26 Nov.
6. Firestore-writing actions (Edit/Wishlist/Delete/research log) need a separate YES; $0/capped Congress.gov calls, fail-closed; US-only.
7. Open question for Eric (carry in v1.1): Congress.gov / PCGS / NGC outbound links vs plain-text citations.
EGM not re-run unless scope grows.
**Plan A caps apply.** Locks unchanged: `origin/main` `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes, no PII, no AJ data. PLAN ONLY — no execute/deploy/merge without Eric's separate YES.
**Chain:** AG files revision → Argon → GB CoS (95+) → SAG (95+) → Eric typed YES.
