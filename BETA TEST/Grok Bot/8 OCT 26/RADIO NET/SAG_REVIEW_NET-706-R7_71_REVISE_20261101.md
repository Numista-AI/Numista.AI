<!-- Stand Alone Grok review via xAI API model grok-4.7 , context-free prompt, 2026-11-01. A PASS still requires Eric's typed YES. No execution authorized. -->

# SAG Review: NET-706-R7
SCORE: 71/100
VERDICT: REVISE

## Summary
R7 is careful and well-cited, and it correctly stops claiming Stripe can be set to “never.” It does not close the address rule: Checkout `auto` can still collect a street address, and TEST-14 does not fail when that happens. The R7-3 “one reader” change also breaks Purchase: `attributionParams()` drops `stripe` and `session_id`. Commercial prices remain CoS-memory figures, not verifiable artifacts. Do not treat this as launch-ready.

## Must-fix (blocking)
1. Rule 1 is still open. `billing_address_collection="auto"` plus card-only is not “never collect a home address.” §7.4 states Stripe may still show street fields and marks that **UNVERIFIED**. TEST-14 passes if settings match even when street fields appear. Either use a flow that cannot collect street/home address (and fail the test if those fields render), or do not ship Checkout until that is proven. Disclosure in §7.2/§7.3 does not satisfy “never collected.”
2. §4.2 replaces `hashQuery()` with `attributionParams()`, which returns only `utm_*` and `fbclid`. §3.4 and TEST-11 need `stripe` and `session_id` from the fragment (`/#/settings?stripe=success&session_id=cs_...`). As written, Purchase never fires. Keep one splitter; do not filter checkout keys out of the Purchase reader. Unit-test both URL shapes for attribution and for `session_id`.
3. Rule 3: §5.2 prices ($4.99/$49.99, $8.99/$89.99, $10.99/$109, $15.99/$150, $95.94, $500, $625) are “CoS memory” / “CoS record,” not a quoted artifact. Gate 2 confirmation is not a source. Quote the record or mark every such figure **UNVERIFIED** and keep it out of implementation scope. Same for unsourced `10 calls/min`, `18pt`, and `48x48dp`.

## Should-fix
- §7.1 “never asks… no scan text, no log” overclaims relative to §7.4 and to scan paths owned by NET-718. Make NET-718 SEC-1/SEC-2 green a launch gate before any receipt upload stays enabled; do not claim redaction in privacy copy until then.
- “No personal data is shared with third-party advertisers” (§7.2/§7.3) is still in tension with sending Pixel events (IP, UA, URL, fbclid) to Meta. Name Meta as a recipient. Drop “physical location” if IP is processed.
- No cited webhook/fulfillment path. Prove tier grant is not client-return-only, and that the webhook cannot persist `customer_details` or the raw event.
- Purchase dedup is client-only (`meta_purchase_fired_{session_id}`). Add a server flag and Meta `event_id`. Strip `session_id` from the URL before `fbq` (Pixel may send `location.href`, fragment included).
- Pass server `currency` into `Purchase`; do not assume USD. Do not fire `value: 0` on a paid comp.
- Rate limit is prose only (“if one exists… otherwise Firestore/in-memory”). Multi-instance in-memory will not hold. Put the limiter in the endpoint snippet.
- TEST-01/02 `curl` URL contains an unexpanded `*` channel glob.
- PageView on tab switch will over-count. Capture attribution before the router rewrites the URL. `Uri.splitQueryString` needs a malformed-query guard.
- Caller-supplied `success_url` (`tier_gatekeeper.py:198`) must stay server-fixed (no open redirect).
- Gate 2 does not block on hero placeholders or on replacing “Free During Beta -- Pricing TBA” / “completely free” (§6.1) before paid ads. Gold→unlimited vs `family_estate` 2500 is an entitlement inversion; require an explicit confirm.
- `numista-vault` project id is only implied by the preview hostname; cite `.firebaserc` or equivalent.

## Risks
- US cards may still be prompted for a street billing address; that address lives at Stripe even if Numista never copies it.
- Ads, site copy (“completely free”), and code ($4.99/mo, $29/yr; free=20 until NEW WORK) can disagree. Wrong CoS-memory prices become live SKUs after a casual YES.
- No CAPI: ad blockers and iOS will under-count `Purchase`; Meta will optimize on a biased signal. Client dedup can be cleared and replayed.
- Cutoff `1795669200000` grants `family_estate` to accounts created before 2026-11-26 00:00 ET. Clock skew or early clicks mint legacy tier, not free=10.
- `cs_` id in the success fragment can reach Meta via the pixel URL.
- Email signup still uses `pin` as the Firebase password (existing). Short numeric PINs are brute-forceable; this plan does not set a length floor.

## Security & Privacy Rule Check
1. No user home addresses are ever collected. **VIOLATION**. §7.4: “there is no value that guarantees no street address”; “Stripe may still show street fields when it decides a card needs them.” §7.2 tells users Stripe “may ask for a billing ZIP/postal code or address.” TEST-14 does not fail that case. Not storing `customer_details` is necessary and not sufficient.
2. Receipt/invoice scans have the person's name and ship-to address automatically redacted BEFORE storage. **NOT ADDRESSED**. §7.5 quotes NET-718 R5 (“raw scan is never stored”; name and ship-to/bill-to “burned out”; else reject) and adds no upload path, but redaction is not implemented here and is not a Gate 4/5 blocker while §7.5 says existing scan paths remain in NET-718.
3. Nothing is invented: prices, bucket names, SKUs, figures must be sourced/verifiable in the plan, not fabricated or assumed. **VIOLATION**. §5.2: figures “held in CoS memory; NOT in code.” $625 is “CoS record 1 Nov 2026” with no quoted record (§1.1 points at §5.2). Lookup keys are labeled proposed (acceptable). `10 calls/min`, `18pt`, `48x48dp`, and project id `numista-vault` are unsourced. Code figures with file:line ($4.99, $29, free=20, epoch) are tagged correctly.

## Notes on verifiability
- Standalone review: no repo, so file:line citations and the `customer_details` grep (0 hits at `32d4b42e`) were not re-checked.
- Epoch `1795669200000` = 2026-11-26T05:00:00Z = 00:00 EST checks out arithmetically. Thanksgiving 2026-11-26 and a 7-day window through 2026-12-02 check out.
- Stripe `auto` / `required` quote matches the cited Create Checkout Session reference; “no never value” is fair.
- Pixel snippet and domain token are “byte-verbatim” from `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md`, which is not attached. Dataset id `2540753249725498` is internally consistent only.
- ERIC-DECISION prices, $625, and Plan v3.2 are not verifiable from this text. Placeholder “400 years” / “2026 US Mint master releases” are not sourced facts.
- §4.2’s claim that line 248 `"source": "**"` is headers-only is not in Citation 4 (ends ~line 135).