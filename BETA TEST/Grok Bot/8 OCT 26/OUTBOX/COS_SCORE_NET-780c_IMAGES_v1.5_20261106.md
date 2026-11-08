# NET-817 / NET-780c Images v1.5 — GB CoS

**58/100 — FAIL** (required: 95+). Reviewed 6 Nov 2026, approximately 9:38–9:43 PM EST.

The full evidence, prior-review reconciliation, branch pins, rubric, mirrors and shared approval gates are in `COS_SCORE_NET-817_CARDS_IMAGES_v1.5_20261106.md`. This is the individual Images score, not execution permission.

## Numbered must-fixes
1. Fix whole-class replacement: plan `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.5.md:114` starts replacement6360 inside the existing class; actual p7 `numista_mobile/lib/screens/my_collection_screen.dart:6356–6358` is its declaration/fields/constructor. Use an anchored complete class diff. Retain restored `_buildCoinImage`.
2. Preserve actual user aliases: plan220–230 detects camelCase uploads through the helper but never reads imageObverse/imageReverse, which real `canonical_mint_asset_service.dart:44–49` recognizes. Iterate valid aliases; empty earlier fields must not mask valid later fields. Keep invalid-user-photo fail-closed, never fallback art.
3. Fix future lifecycle and terminal state: plan136–163 caches by Map identity, refetches equivalent new maps, misses in-place changes, and starts reads before direct-image selection. Plan259–290 has no hung-query timeout. Real `coin_image_service.dart:562–579` performs sequential awaited reads. Use semantic request keys, injection, skipped unnecessary fetches and bounded fallback.
4. Ground image ownership and allowed URL forms: plan181–199 is not a verified bucket manifest; CSP276 permits transport origins, not ownership. Accept only verified owned storage/user forms and current same-origin; reject all unapproved hotlinks before fetch. Supply captured-network and legitimate-user/reference fixtures.
5. Remove **Hard $0.00 Spend Cap** at55 and348: standing rule is budget alerts only, never caps. Read-only Firestore/GCS can incur charges; no mutations is not zero-cost proof. Retain explicit permitted reads and no-write fence; use offline mocks in validation.
6. Replace non-tests at387–418 with actual widget pumping, injectable offline providers, request counts, precedence assertions, external rejection and timeout/cache/update tests. Two bodies have no assertions and none supplies the claimed mocks.
7. Correct incomplete shared Google deletions at366–373: actual p7 widget extends through3548 and handler through4406. Coordinate dev/p7 differences with NET-816, preserve consent functionality, require Eric YES on exact deletion list. Add separate writes/rules YES gates, US-only, AI-image laptop+GCS backups and 3:00 AM EST AG stand-down.
8. Correct NET-817 baton8–9 mirror claim: exact Images copies in INBOX/OUTBOX are absent. Docs/BATONS/RADIO NET match SHA256CD17B43CE145BAEA90389537BA1B644E491BA2403D359C252EBE71704E18AF37.

Source ref: p7-v8.9@4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235. Read-only laptop work; no tests/builds/writes/push/messages. User-first fail-closed ordering, included renderer method, dynamic rollback and honest read-network description are improvements, not proven runtime safety. Main remains locked9f04550a and Stripe OFF.
