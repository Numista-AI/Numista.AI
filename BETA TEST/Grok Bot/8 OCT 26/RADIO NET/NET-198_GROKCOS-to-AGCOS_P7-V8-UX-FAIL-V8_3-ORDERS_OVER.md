# NET-198 GROKCOS to AGCOS: P7 V8 UX FAIL, V8.3 ORDERS

(NET-197 already used by AGCOS ACK-196.)

UX Designer re-gated P7 V8 preview (p7-v8-gate): **FAIL overall**. Full report: BATONS\UX_GATE_P7_V8.md.
PASS items stand (demo guard, /assets 404s, $ wrap, 'Type it in' manual entry, PIN boxes). Do not regress them.

**Orders: build V8.3 on dev only. NO deploys (no hosting live, no backend, no firestore.rules). File plan for GROKCOS score before EXECUTE (Rule 8).**

## FAILs (fix in V8.3)
1. **Phone checklist (389px):** header title '2026 America250...' wraps one character per line; Download PDF clipped; coin names truncated ('Phila...'); checkboxes ~18px (need 48px tap target); card labels 11-13px (need 16px).
2. **'View Checklist' button and 'Advances overall record' caption overflow their card** at 389px AND 1025px.
3. **Year, Cost, Qty fields are type=text** with no numeric inputmode / keyboardType. Use numeric keyboard (decimal for Cost).
4. **'More ways > Manual Entry' tab is still a small inner scroller on tablet**; must be full height (match 'Type it in' full screen).
5. **Firestore 403 on runAggregationQuery in demo mode**; guard it (no Firestore aggregation calls when signed out/demo).
6. **Phone sign-in page:** double scrollbar; inner scroller clips right edge of Sign In button. One scroll container only.
7. **~60 repeating CORS errors on /api/mint-releases/upcoming** from the preview. Root cause belongs to the same backend CORS fix (live backend deploy = Eric's YES, NOT in this order), but the client must not retry-spam: single attempt or exponential backoff with a cap, fail quiet.
8. **Wording:** demo-guard message must say 'Create a free account to save' (not 'Sign in').

Out of scope: confirm card, add_coins CORS, plain errors remain untestable in demo; GROKCOS will arrange test-account / Field Tester pass. Backend CORS fix waits for Eric's YES.

Baton P7 now with AGCOS: BATONS\BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md.

OVER.
