# UX GATE: P7 ADD-COINS-FLOW V8 (re-gate, NET-194 preview)

**Result: FAIL overall** (much better than V7).
Tester: UX Designer (670397b2). Date: 2026-10-15 ~14:28 ET.
Preview: https://numista-vault--p7-v8-gate-ibg4oycd.web.app (dev 371989db, V8.2 6c68dd57).
Scope: signed-out demo only, phone 389px + tablet 1025px. No saves, no sign-in.
Screenshots: UX Designer box /workspace/numista-ux/p7v8/.

## PASS
- Demo guard: add blocked with plain message, zero add_coins requests.
- No /assets/assets 404s.
- $41,904.02 dashboard value no longer wraps on phone.
- Manual entry via 'Type it in': full screen, Mint Mark/Denomination not clipped, labels ~16px, Save 56px, Qty 1 stays 1.
- PIN: all 6 boxes visible.

## NOT TESTABLE in demo
- Confirm card (demo guard intercepts first; needs non-Eric test account or Field Tester).
- add_coins CORS (call never fired; not BLOCKED-BY-CORS, not FAIL).
- Plain-English errors (no error triggerable without submit).

## FAILs (fix in V8.3)
1. **Phone checklist (389px):** header title '2026 America250...' wraps one character per line; Download PDF clipped; coin names truncated ('Phila...'); checkboxes ~18px (need 48px tap target); card labels 11-13px (need 16px).
2. **'View Checklist' button and 'Advances overall record' caption overflow their card** at 389px AND 1025px.
3. **Year, Cost, Qty fields are type=text** with no numeric inputmode / keyboardType. Use numeric keyboard (decimal for Cost).
4. **'More ways > Manual Entry' tab is still a small inner scroller on tablet**; must be full height (match 'Type it in' full screen).
5. **Firestore 403 on runAggregationQuery in demo mode**; guard it (no Firestore aggregation calls when signed out/demo).
6. **Phone sign-in page:** double scrollbar; inner scroller clips right edge of Sign In button. One scroll container only.
7. **~60 repeating CORS errors on /api/mint-releases/upcoming** from the preview. Root cause belongs to the same backend CORS fix (live backend deploy = Eric's YES, NOT in this order), but the client must not retry-spam: single attempt or exponential backoff with a cap, fail quiet.
8. **Wording:** demo-guard message must say 'Create a free account to save' (not 'Sign in').

OVER.
