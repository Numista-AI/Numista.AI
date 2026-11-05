# SAG SCORE NET-798 (xAI API, grok-4.7, 2026-11-05 ET)

## SAG_SCORE: 74/100 FAIL
## MUST_FIX (blocking before Eric YES; or NONE blocking)
1. UCD-3 is blocking. Delete every Congress.gov hotlink, including both “Read on Congress.gov” buttons in the diagram and §5.3. Laws stay in-app text only: act name, year, public-law number, plain-English summary. Catalog wins. If catalog law is empty, unchecked Congress.gov text may show only with the exact footer “From Congress.gov, not yet checked by us”. No URL, no external browser. Lock #3 does not allow leaving the app.
2. Public values: CDN CPG retail only. Never wholesale. Never AI-primary. Do not carry `aiValue` forward as Est. Value or Estimated Market Value. Live eBay is not the primary value. No invented prices. User purchase price stays behind Show values.
3. Hard $cap, fail closed, on any Congress.gov query, Morgan research request, and eBay live check. No uncapped calls.
4. Rollback before cutover. Do not delete `_showCoinInspectorDialog` or `CoinDetailScreen` in the same step as first ship. Keep the old path callable until preview passes.
5. Preview-before-live on a non-prod build before any live deploy. `origin/main` stays `9f04550a`. Stripe stays OFF. This plan authorizes zero Firestore writes. A research-request log is a separate Firestore change and is not approved here.
6. Nothing invented. Strike or cite real Global Search and Public Catalog launch sites; §8 only wires collection. Do not treat “View Parent Set” (`isVirtualChild`) as coin details. Fix the card-tap citation: the live call sets `_selectedCoinId` before the inspector. Account for both `CoinDetailScreen.show` branches, not one line.
7. Images: user or catalog photos only. `ai_replica_images` never primary. No photo means coin outline plus “Add a photo”, not a replica.
8. Tests must cover the privacy gate, Show values across Previous/Next until Close, catalog-wins, the exact Congress label, zero outbound links, retail-only non-AI value, and the virtual-child path.
## NON_BLOCKING
- Thanksgiving Meta ads stay priority #1. The 10–16 Nov details work must not displace that track.
- Re-measure contrast on a real device in preview. The ratio table is a design target, not a lab cert.
- Public Law 116-330 is an example only. Do not hardcode it for every 2026 coin.
- Morgan preload stays limited to year, mint, denomination, variety, and grade. Never send purchase price, storage, invoice, or user identity.
- EGM 98 and Argon 97 are not clearance. They treated the outbound link as a nit.
## PII_FINDINGS
No customer PII and no AJ in the plan. No emails, phones, or real storage addresses. Argon’s review embeds local `c:/Users/ericd/...` paths; do not copy those into shared or public docs. Storage stays PIN-gated and off-screen while values are showing.
## 2_SENTENCE_PLAIN_ENGLISH (for Eric)
The plan does follow your three locks: build 10–16 Nov, keep values showing while you step Previous/Next until Close, and let catalog law beat unchecked Congress.gov text. I am not ready for a YES until the Congress.gov web link is removed, prices are locked to retail guide data instead of AI or wholesale, and a dollar cap, rollback, and preview-before-live are written in.
## RATIONALE (brief)
Privacy split, tab cut, and the three locked decisions are actually in the plan, and the doc stays plan-only with main and Stripe locked. It still fails because it authorizes an outbound Congress.gov hotlink, inherits AI estimated value, and omits the dollar cap, rollback, preview-before-live, image rule, and accurate entry-point citations. Those are blocking plan edits, not build permission.
