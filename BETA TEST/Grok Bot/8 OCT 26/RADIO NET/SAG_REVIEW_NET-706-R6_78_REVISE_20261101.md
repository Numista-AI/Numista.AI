<!-- Stand Alone Grok review via xAI API model grok-4.7 , context-free prompt, 2026-11-01. A PASS still requires Eric's typed YES. No execution authorized. -->

# SAG Review: NET-706-R6
SCORE: 78/100
VERDICT: REVISE

## Summary
R6 closes the hash-parser, Google `isNewUser`, verify-session authz, and price-tagging gaps with checkable code and tests. It does not close the two privacy invariants it claims to close: Checkout is still allowed to collect a billing address, and receipt redaction is only a pointer to an unseen plan. Campaign attribution is also split across two conflicting UTM readers. Not passable.

## Must-fix (blocking)
1. Rule 1 is not closed. §7.4 sets `billing_address_collection="auto"` and asserts this “never” yields a full street address (“often ZIP”). `auto` still lets Checkout collect line1/city/state when the payment method requires it; that is a home address, and collection already happened even if Firestore never stores `customer_details.address`. Portal “address editing OFF” is a manual Dashboard step, not code. No current `git grep` of `customer_details` / address writes is shown. TEST-14 on one test session does not prove the invariant. Policy text in §7.1–§7.3 (“deliberately do not collect home addresses”) would be false under this config.
2. Rule 2 is not closed in this document. §7.5 defers redaction to “NET-718 R4 SEC-1/SEC-2” without quoting the control, the write path, or repo evidence that receipt/invoice bytes are never stored. “This plan adds no upload path” does not prove existing Gemini/Cloud Storage scans are out of scope. Privacy copy is forbidden from claiming redaction, so the product invariant is unenforced here.
3. Attribution spec contradicts itself. §3.4 says `hashQuery()` is merged with `Uri.base.queryParameters` for UTM/fbclid. §4.2’s only code reads `Uri.base.queryParameters`. Hash landings and any Flutter hash redirect will drop `utm_*`/`fbclid`. TEST-13 never hits a fragment URL. One reader, one test, including `https://numista.ai/#/pricing?utm_source=meta&fbclid=...`.

## Should-fix
- §2.1 says the pixel and domain-verification tag “are installed” at `index.html` lines 114–115. Citation 1 of those lines has neither, and the mode is DOCS-ONLY. Mark as NEW WORK.
- M3 rate limit is “reuse a limiter if one exists; otherwise Firestore/in-memory.” In-memory is not a limit. Name the limiter, key, and 429 behavior.
- `hashQuery()` reads `Uri.base` and can throw from `Uri.splitQueryString`, so TEST-11’s “unit test” cannot run as written. Inject the fragment string.
- `tier_gatekeeper.py:198` caller-supplied `success_url`: specify append of `{CHECKOUT_SESSION_ID}` and an allowlist host. Not shown.
- `getRedirectResult()` call order vs other auth init is unspecified; uncaught errors can break startup. TEST-06 does not cover redirect.
- Purchase/registration dedupe keys are client `SharedPreferences` only (§3.2, §3.4 step 4). Another browser re-fires. Title “Deduplication Engine” overclaims. Persist a server-side fired flag keyed by uid/session id.
- TEST-05/06 say “server success”; §3.2 says confirmation is Firebase SDK only, no Numista backend call. Align the words.
- TEST-01/02 `curl` a glob host (`numista-vault--p7-gate-*.web.app`). Not executable. Cite `.firebaserc` / `firebase.json` for the site id.
- PageView skip-flag lives in `BaseLayout` state “or” a navigator observer. If `BaseLayout` remounts, in-app `PageView` is skipped forever or double-fires. Pin it to a process-lifetime observer.
- verify-session: `except Exception` maps Stripe outages to 404; `s.get` assumes dict-like Stripe objects; session id still hits API access logs via query string.

## Risks
- ZIP-only AVS still ties a payment to a location, which contradicts §7.1’s “never tied to a physical location” sentence even if street line1 is absent.
- §5.3 remaps Gold → `estate` and proposes `estate` 1000 → unlimited, and Silver 250 → 249. Implementing before Gate 2 changes live entitlements, including legacy `family_estate` / beta (`creation_timestamp < 1795669200000` still open vs Eric’s 27 Nov cutoff in §5.4).
- Browser-only Pixel (no CAPI, no `event_id`) will undercount under blockers/iOS; do not treat Pixel totals as paid revenue.
- Uniform 404 is right, but `Session.retrieve` runs before the owner check, so a leaked `cs_` id still burns Stripe calls up to the unspecified rate limit.
- Preview-channel and live curl tests are the only proof the pixel is in the first HTML byte. A later Flutter inject would fail Meta’s crawler and TEST-01/02 would be the only catch.

## Security & Privacy Rule Check
1. No user home addresses are ever collected. **VIOLATION.** §7.4: `billing_address_collection="auto"` and “Stripe asks only what the card network needs (often ZIP); never a full street address by default.” `auto` does not forbid street address. §7.1 / §7.2 / §7.3 claim home addresses are never collected. Non-persistence (“must not copy `customer_details.address`”) is not non-collection. Shipping unset and phone unset are necessary but not sufficient.
2. Receipt/invoice scans have the person's name and ship-to address automatically redacted BEFORE storage. **NOT ADDRESSED.** §7.5: “This plan adds no upload path and no scan storage. The rule … is owned by NET-718 R4 SEC-1/SEC-2 (in-memory redaction, raw never stored).” That control is not specified or evidenced in this plan. §7.5 also says privacy text must not claim redaction until that other plan ships.
3. Nothing is invented: prices, bucket names, SKUs, figures must be sourced/verifiable in the plan, not fabricated or assumed. **COMPLIANT** for prices/SKUs. §5 tags CODE vs ERIC-DECISION vs UNVERIFIED; $4.99/mo and $29/yr point at `payment_routes.py:50-51`; $625, metal prices, $95.94, and lifetime are tagged and Gate 2 blocks Stripe objects; lookup keys are proposed, not created. Caveat, not a second price invention: `numista-vault` in the preview host is unsourced, and the “never a full street address” sentence is an assumption stated as fact.

## Notes on verifiability
- Standalone review cannot re-run `git show 32d4b42e`. Verbatim blocks support auth popup discard (Citation 3), hash `success_url` without `session_id` (Citation 6), tier limits (Citation 5), legacy cutoff `1795669200000` (Citation 9), and absence of the pixel in current `index.html` (Citation 1).
- $4.99 / $29 literals and `price_1ProMockID` are not inside any verbatim block; only line references. `tier_gatekeeper.py:194/200/234` owner fields and default URL are asserted, not quoted.
- Pixel id `2540753249725498` and verification token are “byte-verbatim” from `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md`, which is not pinned to a commit in this plan.
- ERIC-DECISION rows cite CoS memory / clock times (29 Oct 2026, 1 Nov 2026), not an attached record. Honest labels, not independent proof. §5.4 correctly leaves the 26 Nov vs 27 Nov cutoff OPEN.
- “Production already returns real HTTP 404” (§4.1) has no captured status line in the plan.