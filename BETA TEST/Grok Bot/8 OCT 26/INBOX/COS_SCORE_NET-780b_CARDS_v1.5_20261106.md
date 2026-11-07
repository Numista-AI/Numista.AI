# NET-817 / NET-780b Cards v1.5 — GB CoS

**72/100 — FAIL** (required: 95+). Reviewed 6 Nov 2026, approximately 9:38–9:43 PM EST.

The full evidence, prior-review reconciliation, branch pins, rubric, mirrors and shared approval gates are in `COS_SCORE_NET-817_CARDS_IMAGES_v1.5_20261106.md`. This is the individual Cards score, not execution permission.

## Numbered must-fixes
1. Correct structural deletion diffs: plan `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.5.md:274–284` omits spread closure at real p7 `numista_mobile/lib/screens/my_collection_screen.dart:3547–3548` and method brace at4406. Coordinate the different dev tree and Eric YES on the exact deletion list.
2. Correct canonicalYear: plan169–202 reads Personal Notes178, prefers any text2026, and fails a direct `Year:1776-2026` without matching text. Real `canonical_mint_asset_service.dart:160–161` intentionally excludes Personal Notes. Infer only from reliable metadata, handle direct dual dates/empty alias fields/conflicts, propagate consistently and test through real public resolvers.
3. Replace tautological tests: plan340–349 only checks year, never the negative denomination fixtures;359–385 never pumps a card and asserts a constant contains itself. Supply actual widget/regex/resolver fixtures, mocks, positive/negative UI assertions and light/dark contrast plus FT gate.
4. Keep rollback's dynamic execution HEAD and exact execute-set revert, but add explicit separate Firestore writes YES and rules-deploy YES, approved deletion list, US-only, AI-image laptop+GCS preservation and 3:00 AM EST AG stand-down. Main remains locked9f04550a, Stripe OFF, no cap.
5. Correct handoff claim: NET-817 baton8–9 claims INBOX/OUTBOX; exact Cards copies are absent in both. Docs/BATONS/RADIO NET match SHA25664D339D45158C51814357D60E0488F2DF890E6D5B0ED74DD0D632421A82B4BFF.

Source ref: p7-v8.9@4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235. Read-only laptop work; no tests/builds/writes/push/messages. Positive CPG precedence, removal of primary AI fallback, darker typography, corrected service-test path and dynamic rollback are accepted as proposed improvements, not runtime proof.
