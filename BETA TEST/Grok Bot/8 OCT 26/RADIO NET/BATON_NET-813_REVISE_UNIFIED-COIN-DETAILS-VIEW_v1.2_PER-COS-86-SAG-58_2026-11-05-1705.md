# BATON NET-813 - To: AG CoS v4 - PLAN ONLY: Unified Coin Details v1.2 (CoS 86 / SAG 58 FAIL on v1.1)
Source: GB CoS 5 Nov ~5:05 PM ET. Argon 98 PASS; CoS **86 FAIL**, SAG **58 FAIL**. Scores: `COS_SCORE_NET-806_UNIFIED-COIN-DETAILS-v1.1_20261105.md`, `SAG_SCORE_NET-806_20261105.md`. Build window 10-16 Nov only after critical catalog fixes.

Verified OK: all five call sites and contrast root cause; no fictional PIN service; guest hide-list; values persist until Close; CDN retail-only public value; Congress.gov-only Laws links with no images, checked catalog precedence and unchecked label; US-only/fail-closed; no AJ PII.

Fix:
1. **Rollback:** delete `git revert --no-commit HEAD...9f04550a`. Main is not ancestor of p7-v8.9; span is 2112 files (+282979/-11590). Record actual pre-execute p7 SHA and revert execute commit(s); named Hosting release restore if deployed. Flag-off is useful but not a substitute.
2. **Bind real call sites and fallback:** current virtual-child sites pass `effectiveId` + child map, icon sites build a parent model, and parent-set site passes uncast data. Specify resolver/list source for each; drop uncited Global Search. A const flag defaulting true cannot instantly roll back or be assigned in tests: use non-const default-off gate with per-site legacy fallback.
3. **Laws/read-only behavior:** existing Laws reads `metadata/coin_legislation`; backend writer calls Congress API and writes Firestore. Do not run writer or add live client API. Keep checked data precedence, plain `https://www.congress.gov` text links only with target=_blank/rel=noopener; remove other outbound eBay action.
4. **No writes under this YES:** §8 cannot allow existing legacy Edit/Wishlist/Delete callbacks in the initial release. All mutation buttons/callbacks and research logging are disabled/absent until separate Eric Firestore YES. Add tests that no write callback fires.
5. **Evidence and value display:** guest must still see positive cpgRetail even when private Purchase tab hidden; AI replica images never card. Correct fabricated value-code citation and show guest retail outside redacted area.
6. **Evidence boundaries:** checked catalog laws win; arbitrary Congress errors/timeouts yield labeled empty state, never invented law. AI Estimate remains experimental and never displaces positive CDN retail in primary slot. Private Purchase/Melt stays behind owner Show values and never on guest surface.

Locks: origin/main 9f04550a, Stripe OFF, zero execute/deploy, zero Firestore writes, no PII/AJ data. PLAN ONLY.
Chain: AG → Argon → GB CoS (95+) → SAG (95+) → Eric typed YES.
