<!-- Stand Alone Grok review via xAI API model grok-4.7 , context-free prompt, 2026-11-01. A PASS still requires Eric's typed YES. No execution authorized. -->

# SAG Review: NET-706-R5
SCORE: 72/100
VERDICT: REVISE

## Summary
Detailed docs-only campaign plan with gates, privacy diffs, a test matrix, and several code citations. It is not executable as written: the Purchase return path conflicts with the cited router, signup pixel snippets do not match Citation 3, the new verify-session endpoint is unbound to the payer, and the price catalog is unsourced and inconsistent with the only cited prices and tier keys.

## Must-fix (blocking)
- Purchase plumbing is broken against the plan’s own citations. `success_url` stays hash-form (`/#/settings?stripe=success&session_id=...`, §3.4 / Citation 6). Citation 2 is path-based and does not list `/settings`. Fragment query params are not `Uri.base.queryParameters` (§4.2). No parser is specified. TEST-11 cannot pass.
- §3.2 Google path requires `UserCredential cred` and `additionalUserInfo.isNewUser`. Citation 3 discards the popup result (`await _auth.signInWithPopup(provider)`) and has a redirect branch that does not yield `isNewUser` inline. Email snippet omits the cited `updateDisplayName` / `UiVariantService.refresh` lines. Not marked as a safe insertion.
- `/api/stripe/verify-session` (§3.4) has no authn/authz rule tying `session_id` to the Firebase user / Checkout `metadata.user_uid`. Session id in the URL is a payment-status and amount oracle.
- §5 prices, $625 spend, and $500 vs $1,500 lifetime figures have no authority citation. They conflict with Citation 7 (`Pro ($4.99/mo)` / `Estate ($29/yr)`) and Citation 5 keys (`pro`, `numismatist`, `dealer`, `estate`, …). Paid coin limits are absent under “Core Entitlements.” Lookup-key → gatekeeper mapping is missing.
- Rule 1 is not operationally closed: no Stripe `billing_address_collection` / shipping disable, despite Checkout being in scope.
- Rule 2 is absent: no statement on receipt/invoice scans or name + ship-to redaction before storage.

## Should-fix
- Dedup is `SharedPreferences` only (§3.2, §3.4). No `event_id`, no Conversions API. Other browser/device double-fires `CompleteRegistration` and `Purchase`.
- State that pixel + domain tag must survive `flutter build web` (static `index.html` is often regenerated).
- TEST-01/02 use a non-resolving glob host (`numista-vault--p7-gate-*.web.app`). Station id is `numista-qc`; hosting site name is unexplained.
- Privacy AFTER text still says data is shared only with unnamed “trusted” providers while sending events to Meta (§7.3). Name Meta in that provider list or the two sentences conflict.
- PageView on every tab switch (§3.1) will inflate the optimization event. Limit to real route changes.
- Client `path.startsWith('/attorney')` (Citation 2) vs hosting-only `/attorney_portal` (§4.2) is unresolved.
- Do not publish unsourced lifetime candidates even as “on hold.”

## Risks
- Sandbox cutover can ship a success URL the cited router never reads, so `Purchase` never fires or fires with a client-side amount if implementers “fix” it locally.
- Unauthenticated verify-session leaks `amount_usd` and paid/unpaid state to anyone with the id (Referer, history, logs).
- Meta Pixel sends IP, cookies, and `fbclid` to Meta; browser blocking and iOS limits will under-count. Client-only guards will not match Ads Manager.
- Unknown-path UTMs 404 by design (TEST-12); attribution on bad ad URLs is dropped.
- `fbq` via `js.context.callMethod` has no load-failure path; skipped first `PageView` plus a blocked pixel yields zero `PageView`.

## Security & Privacy Rule Check
1. No user home addresses are ever collected. — **COMPLIANT** (policy text only). §7.1: “intentionally does NOT collect users' home addresses”; §7.2–§7.3 privacy diffs repeat that. Not closed in Stripe Checkout (see Must-fix).
2. Receipt/invoice scans have the person's name and ship-to address automatically redacted BEFORE storage. — **NOT ADDRESSED**. No receipt, invoice, ship-to, or pre-storage redaction control. Scans are only “Scanned images … Gemini” (§7.2).
3. Nothing is invented: prices, bucket names, SKUs, figures must be sourced/verifiable in the plan, not fabricated or assumed. — **VIOLATION**. §1.1 `$625` and §5 tier prices / export dollars / lifetime `$500` vs `$1,500` lack a source doc or code cite. Cited prices (Citation 7) and tier keys (Citation 5) disagree. `numista-vault` preview host is not tied to station `numista-qc`. Proposed `lookup_key`s are labeled proposed (acceptable). Pixel id is cited to `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md` (not reproduced).

## Notes on verifiability
- Epoch `1795669200000` matches `2026-11-26T05:00:00Z`. Annual-savings and 6× export arithmetic match the stated monthly prices. Those checks do not source the prices.
- Citations 1–9 are partial. Rewrite line map (§4.2, lines 21–133 and 248) is mostly uncited; only Citation 4 (claim rewrites + headers) is shown. Standalone review cannot confirm “no `**` rewrite” or the `/privacy` line numbers.
- §3.2 “server confirms” is client Firebase Auth, not a Numista backend confirm. `isNewUser` is not in Citation 3.
- Commit tips `9f04550a`, `32d4b42e`, `9b55f3d9`, domain-verification token, and dataset `2540753249725498` are assertions. Spec file is named, not attached. Byte-verbatim pixel claim is unverifiable here.
- Hero strings are explicitly placeholders (§1.1, §6.2). That part does not invent final copy.