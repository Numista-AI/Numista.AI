# SAG UPLOAD PACKET — Meta Pixel signup attribution plan v6 (full-plan independent review)

Packaging only. This file is not a plan amendment and not a new submission. It embeds unchanged, hash-identified copies of the files listed below. Prepared 9 Nov 2026 (EST). Contains no keys, credentials or personal data.

## 1. Instructions to the reviewer (please read first)

You are a fresh, independent senior reviewer (full-plan SAG gate). Please:

1. **Read the entire embedded plan (File A) end to end** before scoring. Files B–D are context, not conclusions.
2. Give an **independent weighted score out of 100**; the pass threshold is **95**. State your rubric (areas and weights) and per-area deductions.
3. **Flag every blocker regardless of arithmetic.** Any critical defect (privacy leak, consent failure, sign-up/profile availability risk, unsafe stop/rollback, false measurement claim) means REVISE even if points would reach 95.
4. **Verify, don't anchor.** The internal CoS gave 97 (File D) and retained three findings (R1, N-1, N-2) as **not closed**. Check those yourself, and look for anything the earlier reviews missed. Do not adopt or average prior scores.
5. **No implementation and no approval inference.** This is a plan only. The owner's instruction: "Prepare the Meta Pixel plan only; no implementation until my YES." A pass here authorizes nothing. Implementation still needs the owner's separate typed YES and existing scoped permissions.
6. **Separate proven facts from open future verification gates.** The plan's 15 source gates (§1), IC-0 (§9) and prerequisites P-1–P-9 (§2) are unresolved hypotheses or future checks. Section 3 of this packet gives the archived official excerpts the plan cites. Anything not covered there is unverified. Judge whether each unverified item fails closed or only degrades measurement, as the plan claims.
7. For each finding, give the **minimum integrated repair** and its **regression risk** (what the repair could break elsewhere in the plan).
8. Do **not** propose new approval layers, standing cross-team policies, or anything that weakens user, consent or privacy protections. Don't propose expanding the plan into an analytics platform.
9. **Return:** a full assessment; the rubric table and score; **PASS or REVISE**; and findings, each backed by plan section and line number (File A lines are numbered as `L<n>|`). Your response will be pasted back unchanged to the internal Chief of Staff gate.

Context: Thanksgiving Meta campaign, 26 Nov – 2 Dec 2026. Goal: accurate, privacy-safe measurement of sign-ups with at most a minimal parameterless `CompleteRegistration`. Zero Meta script or requests in the Flutter SPA. Attempt ledger: global attempt 6 of 10 (replacement writer, try 2). Reviews add no attempts.

## 2. Contents and integrity

| File | Original path (owner's workspace; not accessible to you) | SHA-256 of original bytes |
|---|---|---|
| A | `PLAN_META_PIXEL_SIGNUP_ATTRIBUTION_v6.md` | `8df72e6b558742ae388db965417cddf8f346d1992c056f5aa3f0350228533df3` |
| B | `CLOSURE_MAP_v6.md` | `6dd1ea01f1d2af376c1db92fd88941cb2b0a84496b2cfda979b9060d4658c0da` |
| C1 | `cos-review/v6/COS_REVIEW_META_PIXEL_v6.md` | `f5b20d69f63decc5df9ae6c60665b096839db9b931c57ef024d1c4e2225f27fa` |
| C2 | `cos-review/v6/SUMMARY.md` | `2d0d7b1dedac291f0f12453e9288b468c54e153301ad2a4c48c6387c8c6098a3` |
| D | `cos-review/v6/COS_GATE_DISPOSITION.md` | `42ec4059c33660921aa4945e620ed0c89d0e2e658d7429b1f551a98d3890a3dd` |
| E | `V6_SUBMISSION.sha256` | `2fb0cad249b424ea65eeb512d12a2a3753d6b0fc75f24648c2622e5855e61365` |

File A is embedded twice: once **with line-number prefixes**, for citing, and once **verbatim**, for byte-exact verification (the hash applies to the verbatim block content plus its final newline). Files B–E are embedded verbatim. Section 3 holds excerpts from the archived official sources, each with its archive SHA-256.

---

## FILE A (line-numbered view) — `PLAN_META_PIXEL_SIGNUP_ATTRIBUTION_v6.md`
SHA-256 `8df72e6b558742ae388db965417cddf8f346d1992c056f5aa3f0350228533df3` · 501 lines

````text
L1| # PLAN — Meta Pixel signup attribution (web), v6
L2| 
L3| **Status: PLAN ONLY.** Eric, 9 Nov 2026, 9:20 AM EST: "Prepare the Meta Pixel plan only; no implementation until my YES."
L4| 
L5| This document approves nothing: no implementation, Pixel or dataset creation, Meta setting, Test Events, DNS, Hosting site, deploy, rules change, Firestore write, ad or synthetic account. Every consent, canary, marker, rules, URL and deploy change below is **future, UNIMPLEMENTED and permission-gated**. Rule text, diagrams and pseudocode are plan text, not app code, and no Firestore collection, document or rule described here exists. Every test is a future contract; none has run. Nothing here asserts what the current code does beyond the cited audit records; IC-0 (§9) verifies it, and drift the design cannot absorb means STOP and a reviewed amendment.
L6| 
L7| **Gates** (unchanged since v3; v6 adds none). Each is a separate approval, in this order.
L8| 
L9| | Gate | Approval |
L10| |---|---|
L11| | G-1 | Independent CoS review ≥ 95 |
L12| | G-2 | Full-plan SAG ≥ 95 |
L13| | G-3 | Eric typed YES for implementation (feature branch, flags OFF), including acceptance of §4.7 and §13 residuals, the marker mode (§5.3) and counsel's P-6 decisions |
L14| | G-4 | Eric YES for subdomain, DNS and a new Hosting site (existing permission scope, unchanged) |
L15| | G-5 | Implementation; contracts T-1–T-12 and T-23 green |
L16| | G-6 | Eric YES for the local and preview test run (he may scope it to local only, §8.4) |
L17| | G-7a | Eric YES for the first production deploys (marker live; handoff tester-only; no Pixel). The request lists stop paths (a)–(c) of §6.4 by name so they run under this YES |
L18| | G-7b | Eric YES for the production Pixel: stage A tester-only, then stage B under the same YES, only on pass (§8). Stop paths (a)–(c) listed by name |
L19| 
L20| **Prepared** 9 Nov 2026 EST on the box, documentation only. No repo, source tree, laptop, Meta account, credential, DNS, Hosting or browser touched; no test, deploy, SAG or paid call; nobody contacted. Main stays locked at `9f04550a`. Stripe stays OFF.
L21| 
L22| **Attempt ledger (inherited; no reset).** Eric's rule, as relayed verbatim by Desk (original Eric message not retrieved; relay reference CoS transcript ≈ pos 7616): "if someone is still failing after 4 tries, somebody else take over. If NO ONE gets it right by 10 total attempts, you notify me and we break it down into smaller bite-size chunks."
L23| 
L24| | Global attempt | Writer | Submission | CoS gate result |
L25| |---|---|---|---|
L26| | 1–4 | original | v1–v4 | 87, 91, 92, 92 REVISE → writer retired |
L27| | 5 | replacement, try 1 | v5 | 94 REVISE, critical B1 (`cos-review/v5/COS_GATE_DISPOSITION.md`, 11:07:59 AM EST) |
L28| | **6** | **replacement, try 2** | **v6 (this file)** | pending; not self-scored |
L29| 
L30| If this writer is still failing after try 4 (v8), somebody else takes over; no success by global attempt 10 → Eric is notified and the work is split. Reviews, mirrors, rescores and hash files add zero. All earlier artifacts stay byte-identical (`PRESERVATION_V6_CHECK.sha256`). `CLOSURE_MAP_v6.md` maps B1–B3, N-A, N-B and this writer's new independent findings (Y1–Y8).
L31| 
L32| ---
L33| 
L34| ## 0. Goal and design
L35| 
L36| **Goal (Thanksgiving campaign, Thu 26 Nov – Wed 2 Dec 2026):**
L37| 1. **Measure of record:** a first-party, best-effort acquisition marker in its **own create-only document** (§5.3), counting new accounts whose browser's most recent `fbclid` landing carried the exact campaign tag within 7 days. Measurement can be lost; it can never block, delay or fail sign-up or any profile write.
L38| 2. **Optional:** one parameterless Meta `CompleteRegistration`, at most one locally authorized attempt per consenting new account, only from an isolated completion origin, never from the Flutter SPA, with no collector data.
L39| 3. Meta's own attribution is reported as Meta-reported only.
L40| 
L41| **Design core (unchanged):**
L42| 1. The Flutter SPA on `numista.ai` never loads Meta code and never makes a Meta request; its CSP gains no Meta or completion tokens.
L43| 2. A separate-origin static **completion document** (`go.numista.ai`, placeholder name fixed at G-4) is the only place the Pixel runs. No Flutter, Firebase, app data, auth or inline script.
L44| 3. After a confirmed, ready, consenting new account, the SPA binds the handoff with a 60 s nonce cookie, navigates top-level to the completion document, which verifies, makes one attempt and returns to a fixed URL.
L45| 
L46| **v6 structural changes:**
L47| - **Marker decoupled from the profile (B1).** v5's profile field and every profile-rule change are removed. The marker is a separate owner-keyed, create-only document written best-effort *after* the essential profile create succeeds; it is never awaited. Profile documents, profile rules and profile writes are untouched by this plan.
L48| - **Stops are never blocked by composition review (B2).** The Pixel kill touches only the completion site; app stops are one-constant mechanical diffs on the actual live release.
L49| - **Tracking parameters stripped from the app URL immediately after capture (B3)**, with truthful statements about what reaches Numista servers.
L50| 
L51| **Out of scope:** CAPI; PageView or landing Pixel; commerce events and value; Advanced Matching; audiences; native apps; appeals, ad launch, budget; staging; reachability probe; server tokens; any new server, function, dashboard, telemetry or analytics platform; legal decisions (counsel); any cross-team deploy policy.
L52| 
L53| ### 0.1 Facts and trust level
L54| | Claim | Source | Trust |
L55| |---|---|---|
L56| | No Pixel on `numista.ai`; current CSP blocks Facebook | SourceAuditor, 6 Nov (`/workspace/site-audit/thanksgiving_gap_audit_20261106.md:7`; `/workspace/site-audit-2026-11-06/THANKSGIVING_GAP_AUDIT_06NOV.md:84–87`) | Reported; IC-0 re-checks |
L57| | Candidate dataset `2540753249725498` | NET-706 R7 | Unverified (P-2) |
L58| | Old domain-verification tag | NET-706 R7 | Not reused (P-3) |
L59| | Hosting site `numista-vault`; preview `numista-vault--<ch>-*.web.app` | Earlier plans | IC-0 confirms |
L60| | Sign-up surfaces: email/PIN, Google popup, Google redirect | Earlier plans | IC-0 confirms which Google mode runs where |
L61| 
L62| ---
L63| 
L64| ## 1. Sources
L65| 
L66| Archived; hashes re-verified for this draft (each manifest run inside its directory): `sources-v2/` 19/19 OK, `sources-v3/` 10/10 OK.
L67| 
L68| **Meta (`sources-v2/`):** S-ADV `advanced.txt` L479 `fbq('set', 'autoConfig', false, 'FB_PIXEL_ID');` (boolean; L467 prose string not used; T-1); L492 CSP (`https://connect.facebook.net`, paths `/en_US/fbevents.js` and `/signals/config/{pixelID}?v={version}`); `trackSingle`; button-click auto-detection; `/tr`. S-GDPR (revoke "on every page"; data received incl. headers, IP, page location, referrer, Pixel ID, Facebook cookie, button clicks, field names). S-REF, S-SPA (not used), S-AM (third `init` argument; not used), S-DPO (`dataProcessingOptions` before `init`), S-GS, S-CT.
L69| 
L70| **Non-Meta (`sources-v3/`):** S-FBMS (multisite; per-site config; `--only hosting:TARGET_NAME`; deletion permanent). S-FBPV (preview URLs random, public). S-6265 (§8.5 no port isolation; step 11 `rfc6265.txt` L1299 replace on same name/domain/path; L719–723 duplicates coexist; §5.1.4 path-match). S-PSL (`web.app` L13988, `firebaseapp.com` L13706). S-RP (`no-referrer`). S-SS (`mdn_storage_sessionStorage.txt`: "partitioned by both origin and browser tabs"; "survives over page reloads and restores"; new tab = new session; opener copy).
L71| 
L72| **Source gates** (no archived text; future verification only). Each is used only where the design fails closed or degrades only measurement if the hypothesis is false:
L73| 
L74| | # | Hypothesis | If false |
L75| |---|---|---|
L76| | 1 | Events Manager / Test Events shows stage A receipt within 24 h (per-event detail optional) | Counts by time only; k not visible by +24 h = fail-and-investigate (§8.2) |
L77| | 2 | Domain verification and subdomain coverage | No stage B (P-3) |
L78| | 3 | AAM toggle | No stage B (P-4) |
L79| | 4 | Event configuration/AEM | No stage B (P-5) |
L80| | 5 | `fbclid` → `_fbc`/`fbc` | §5.2 written choice; marker unaffected |
L81| | 6 | Meta accepts `localhost` events | Local Pixel case skipped |
L82| | 7 | Preview channel stability | Re-create preview; never production |
L83| | 8 | Firebase write-ack semantics in the tree's SDK | Readiness unprovable → STOP |
L84| | 9 | Meta first-party cookie scope controls | §7 widening condition |
L85| | 10 | Cookies Hosting forwards to rewrites | Inventory treats all as forwarded |
L86| | 11 | sessionStorage survives a same-tab cross-origin round trip | No handoff; no marker doc (unmarked); normal boot |
L87| | 12 | Meta ad URL parameters deliver the exact `utm_campaign` | P-9(i) at G-7a; else referral mode |
L88| | 13 | A client's Firestore writes are acknowledged in issue order | A marker write pending at handoff navigation may be lost → unmarked only |
L89| | 14 | Firebase Hosting / Cloud Logging request-log behaviour and retention for this project | §5.5 claim already allows logged query strings; IC-0 records the actual setting |
L90| | 15 | Flutter service-worker caching keeps old builds for a bounded time | M-U grace (§5.4) is context, not an alarm rule |
L91| 
L92| ---
L93| 
L94| ## 2. Prerequisites (account facts at the named gate; nothing is asked now)
L95| | ID | Item | Gate |
L96| |---|---|---|
L97| | P-1 | Business portfolio and admin | G-6 |
L98| | P-2 | Production dataset confirmed, plus a separate test dataset | G-6 |
L99| | P-3 | Fresh domain verification for `numista.ai` (and `go.` if required) | G-7b |
L100| | P-4 | AAM OFF; automatic events/metadata OFF; screenshot | G-7b |
L101| | P-5 | Event configuration/AEM if required | G-7b |
L102| | P-6 | Counsel: checkbox copy, GPC, LDU, whether marker and landing capture need consent, marker retention and account-deletion handling | G-3 |
L103| | P-7 | Privacy text approved and live before stage B (§7) | G-7b |
L104| | P-8 | Subdomain name, DNS, new Hosting site | G-4 |
L105| | P-9 | (i) Every campaign ad's URL parameters contain `utm_campaign=numista_tg26` (ad preview link, no paid click) and the campaign reporting time zone recorded; (ii) objective viable with `CompleteRegistration` only | (i) G-7a; (ii) G-7b |
L106| 
L107| ---
L108| 
L109| ## 3. Event
L110| Only `CompleteRegistration`, no parameters, only from the completion document. No PageView anywhere.
L111| 
L112| ---
L113| 
L114| ## 4. Sign-up flow and handoff (SPA side)
L115| 
L116| ### 4.0 End-to-end traces (plan, not current-code claims)
L117| **Boot order (every app document, exact):**
L118| 1. **Landing capture** (§5.1) reads `fbclid`/`utm_campaign` from the URL.
L119| 2. **URL strip** (§5.1): `history.replaceState` removes `fbclid` and every `utm_*` parameter, preserving path, all other parameters and the hash route.
L120| 3. Firebase Auth initialisation; then the **single** `getRedirectResult` consumer.
L121| 4. Snapshot housekeeping (§4.2) and resume handling (§4.6); then normal routing.
L122| IC-0 confirms whether any SDK or script reads the URL before step 2; if one records or forwards it, STOP and amend (§9).
L123| 
L124| **Email/PIN:**
L125| 1. Form opens; checkbox rendered **unchecked** (only when the handoff is active and GPC is not set, §4.2); never pre-filled.
L126| 2. Submit: client-side validation first. Only after it passes, synchronously and immediately before the create call, write snapshot `nm_attempt` with `method:'email'`. A validation failure writes nothing.
L127| 3. Create fails (any error incl. `email-already-in-use`) → delete snapshot.
L128| 4. Create succeeds → trigger (§4.3) → **consume** snapshot → marker value and handoff inputs fixed in memory → existing first-run writes (unchanged) → DECIDE (§4.4).
L129| 5. When the existing **profile create** succeeds, issue the marker document create (§5.3), fire-and-forget. Nothing waits for it.
L130| 6. SUPPRESSED → existing first-run path. PASS → overlay, readiness (essential first-run ops only), resume record `pending`, cookie, navigate.
L131| 7. Completion → binding → (no-Pixel or Pixel) → `location.replace(RETURN_URL)` → fresh app doc → boot (URL is already clean) → resume `pending` → restore once → `consumed`.
L132| 8. Back after return → original doc (bfcache) sees `consumed` → reload; no first-run replay (§4.6).
L133| 
L134| **Google popup:** as email, except step 2 has no validation: the button click writes snapshot `method:'google_popup'` synchronously, then calls the popup in the same gesture. Popup closed/blocked/error → delete snapshot. `isNewUser == false` → delete snapshot; landing record untouched; no marker, no handoff. `isNewUser == true` → email steps 4–8.
L135| 
L136| **Google redirect (exact order):**
L137| 1. Page was already stripped at boot (step 2), so the URL handed to the redirect carries no `fbclid`/utm.
L138| 2. Click → write snapshot `method:'google_redirect'` synchronously → start redirect → document unloads.
L139| 3. Return to `numista.ai` in the same tab: boot step 1 finds no `fbclid` (the stored landing record from before is unchanged); step 2 no-op; step 3 the redirect consumer.
L140| 4. `isNewUser == true` → consume snapshot (S-SS, source gate 11) → email steps 4–8.
L141| 5. Null, error or `isNewUser == false` → delete snapshot.
L142| 6. Snapshot missing, expired, malformed, method mismatch or guarded → no handoff (SUPPRESSED `attempt`) and **no marker document** (counted as unmarked, §5.4). Sign-up never blocked.
L143| 7. Consent ticked after returning cannot count; only the pre-redirect snapshot exists.
L144| 
L145| ### 4.1 Ownership
L146| One future SPA service, `SignupAttributionHandoff`, owns: checkbox; landing capture and URL strip; snapshot and attempt-id guard; marker value and its best-effort write; DECIDE, readiness, overlay; binding cookie; resume record and bfcache. The marker part runs when `MARKER_ENABLED` is true, independent of the handoff flag (T-2). IC-0 maps these to real paths. T-1 asserts zero Meta references in the SPA.
L147| 
L148| ### 4.2 Consent checkbox and attempt snapshot
L149| **Checkbox.** One unchecked, optional checkbox directly above the email submit and the Google button(s); counsel copy (P-6); not required to sign up. Rendered only when the handoff is active for this browser (flag ON, and `CANARY_ONLY` false or `nm_meta_canary === '1'`) and `navigator.globalPrivacyControl !== true`. Never pre-filled. If P-6 requires consent for the marker, shown from G-7a to all non-GPC users with copy covering both uses. Existing consent UI reused only if IC-0 proves the same semantics. Sign-up UX change accepted at G-3 (§4.7).
L150| 
L151| **Snapshot** `nm_attempt`, app-origin **sessionStorage** (per tab):
L152| ```text
L153| { v:1, id:<128-bit random, base64url>, method:'email'|'google_popup'|'google_redirect',
L154|   consent:<checkbox checked AND GPC !== true>, campaign:<Boolean>, fbclid:<string|absent>,
L155|   exp:<now + 30 min> }
L156| ```
L157| `campaign` = an eligible landing record (§5.1) with `campaign_match === true` (referral mode: any eligible landing). `fbclid` copied only if `consent === true`. No uid, email, name, password, token, URL or utm value. If sessionStorage throws, no snapshot: sign-up proceeds, no handoff, no marker doc.
L158| 
L159| | Event | Action |
L160| |---|---|
L161| | Confirmed create (§4.3) | Read then delete `nm_attempt`. Valid only if well-formed, `method` matches, `exp` not passed, `id` not in `nm_attempt_used`; then add `id`. Delete `nm_landing` in every case |
L162| | Auth error, cancel, popup closed, existing-user sign-in | Delete `nm_attempt`; keep `nm_landing` |
L163| | Client-side validation fails | Nothing written (snapshot is written only after validation) |
L164| | App boot with a non-redirect snapshot | Delete |
L165| | Boot whose redirect consumer returns null/error with a redirect snapshot | Delete |
L166| | Missing, expired, malformed, mismatched, guarded | Delete if present; SUPPRESSED(`attempt`); no marker doc |
L167| 
L168| **Revocation.** Unchecking before the request means `consent:false`. After create no further Meta event is sent for the account. Revocation does not delete Meta cookies, recall data, stop an in-flight completion page or unload a script (§7).
L169| 
L170| **Shared devices.** Consent never carries over; the consumed landing record is deleted at create. Residual (§13): a landing left by someone who never signed up can mark another person's sign-up on the same browser within 7 days.
L171| 
L172| ### 4.3 Trigger
L173| - **Email/PIN:** server-confirmed create.
L174| - **Google:** `isNewUser == true` from the popup result or the single existing `getRedirectResult` consumer (never called twice; if none exists, exactly one is added by amendment).
L175| - **Never:** sign-in; failures; linking; anonymous upgrade; demo/guest; `authStateChanges` alone; token refresh; restart.
L176| 
L177| ### 4.4 DECIDE, readiness and UI that never interrupts input
L178| **Pre-checks** (synchronously after consumption, before any first-run UI); all must hold:
L179| 1. Handoff flag ON.
L180| 2. `CANARY_ONLY` false, or `localStorage nm_meta_canary === '1'`.
L181| 3. Snapshot valid and `consent === true`; GPC re-checked.
L182| 4. Attempt-id guard passed at consumption (`nm_attempt_used`: attempt ids only, pruned after 1 h; no uid).
L183| 5. Cookie probe: `navigator.cookieEnabled`; host-only `nm_probe=1; Path=/; Max-Age=5; Secure; SameSite=Strict` set, read back, deleted (local omits `Secure`).
L184| 6. Next first-run route in the IC-0 resume enum; else `not_resumable`.
L185| 
L186| Any failure → **SUPPRESSED(reason)**: existing first-run path, no overlay, no navigation.
L187| 
L188| **Readiness:** a full-screen, non-interactive "Finishing setup…" overlay (no inputs) shown instead of first-run UI, waiting for **server acknowledgement** of the essential first-run operations IC-0 lists (profile create; seeds and onboarding flags; pending-route persistence). The marker write is **not** awaited (source gate 13: issued right after the profile create, earlier than the later first-run writes, so it is normally acknowledged first; if not, the marker alone may be lost). Local-cache resolution does not count (source gate 8). `READY_MAX` = 10 s.
L189| 
L190| **On success:** write resume record `pending` (§4.6); nonce = 128-bit `crypto.getRandomValues`, base64url; set `nm_hoff` (§4.5); set in-memory `handoffStarted`; navigate via programmatic `<a rel="noreferrer">` to `COMPLETION_URL` + `?fbclid=<snapshot fbclid>` (only if present) + `#t=<nonce>`.
L191| 
L192| **On failure or timeout:** `not_ready`: remove overlay; continue existing first-run in place; never navigate later; never retried.
L193| 
L194| Nothing in the SPA awaits Meta or the marker.
L195| 
L196| ### 4.5 Binding cookie (unchanged; credited sound in v4 and v5 reviews)
L197| Value: only the nonce.
L198| 
L199| | Target | Set by the SPA | Read at `/r/registered` |
L200| |---|---|---|
L201| | Production | `nm_hoff=<nonce>; Domain=numista.ai; Path=/r/; Max-Age=60; Secure; SameSite=Strict` | Yes |
L202| | Local pair | `nm_hoff=<nonce>; Path=/r/; Max-Age=60; SameSite=Strict` (host-only `localhost`) | Yes (S-6265 §8.5) |
L203| | `web.app` preview | host-only on the preview app host | **No** (S-PSL): preview always fails closed |
L204| 
L205| Completion-page check (any failure → no Meta, immediate `location.replace(RETURN_URL)`): (1) fragment `t` well-formed, not consumed; (2) exactly one `nm_hoff`, equal to `t`; (3) expire all four variants `Domain=numista.ai`/host-only × `/r/`/`/` with `Max-Age=0; Secure; SameSite=Strict` (local: host-only pair); (4) re-read, any `nm_hoff` → fail; (5) `history.replaceState` drops the fragment, record nonce consumed (pruned 24 h), re-check GPC; (6) only then inject Meta (§6.2).
L206| 
L207| Proves: within 60 s this browser's SPA consumed a valid snapshot whose consent was captured before the sign-up request and issued this handoff. Residuals: self-forged cookies affect only that browser; cookie tossing from another `numista.ai` host (inventory, §9); fake events sent directly to Meta; **two tabs handing off within the same 60 s overwrite the single `nm_hoff`, so both fail closed** (undercount, disclosed §13).
L208| 
L209| ### 4.6 Resume record, return and Back
L210| `nm_resume` in app-origin sessionStorage: `{v:1, phase:'pending'|'consumed', route:<enum>, step:<enum>, exp:now+10 min}`. No private data.
L211| 
L212| | Situation | Behaviour |
L213| |---|---|
L214| | Fresh boot, `pending`, not expired | Restore route/step once; set `consumed` (tombstone until `exp`) |
L215| | Fresh boot, `consumed`/expired/malformed/absent | Normal signed-in boot |
L216| | bfcache restore of original doc (`pageshow.persisted` and `handoffStarted`), `pending` | Set `consumed`; remove overlay; continue existing first-run in place; never navigate again |
L217| | Same restore, `consumed`/expired/absent | `location.reload()` → normal signed-in boot; no first-run replay |
L218| | Back without bfcache | Browser reload → fresh-boot rows |
L219| 
L220| Per tab, so other tabs never consume it. Completion sends `Cache-Control: no-store` and replaces its own history entry. IC-0 STOPs if a normal signed-in boot re-issues first-run creation writes non-idempotently.
L221| 
L222| ### 4.7 UX changes and residuals Eric accepts at G-3
L223| After stage B (items 2–3 for consenting new users only): (1) optional checkbox on sign-up surfaces; (2) overlay up to 10 s; (3) one extra document (≤ 4.5 s) and a cold app boot, losing in-memory state outside the resume enum. Also, from G-7a for every visitor: the address bar drops `fbclid`/`utm_*` right after landing (a bookmark or copied link lacks them). Unreachable completion host: browser error page; account and acknowledged writes intact; Back per §4.6. **Decided:** no reachability probe. Domain-cookie-rejected browsers: one fail-closed round trip. Latency evidence is synthetic smoke only.
L224| 
L225| ---
L226| 
L227| ## 5. Data, attribution and internal measurement
L228| 
L229| ### 5.1 Landing record and URL strip
L230| - **Capture (boot step 1):** if the URL query (or, under hash routing, the fragment's query; IC-0 confirms) has a valid `fbclid` (`[A-Za-z0-9_-]{1,512}`):
L231|   - no record, or a record with a **different** `fbclid` → write `nm_landing` (app-origin localStorage) `{v:1, fbclid, campaign_match:<utm_campaign === META_CAMPAIGN_TAG>, captured_at:now}`;
L232|   - record with the **identical** `fbclid` → leave the record unchanged (original `captured_at` and `campaign_match` kept; reloads and repeats never extend eligibility).
L233|   - A landing with the tag but no valid `fbclid` records nothing. The utm value is never stored.
L234| - **Strip (boot step 2):** remove `fbclid` and every parameter whose name starts with `utm_`, from both the query and any hash-route query, preserving path, hash route and every other parameter in order; `history.replaceState` keeps the existing history state object. Runs whether or not the values were valid. If `replaceState` throws, capture still stands and the app continues.
L235| - **Eligible:** `now − captured_at ≤ 7 days`. **Deleted:** at consumption of a create (any decision); on expiry.
L236| - Capture before consent follows P-6; default is first-party capture, transmitted only via the completion URL after consent.
L237| - `META_CAMPAIGN_TAG` = `numista_tg26`, a single allowlisted build constant, exact and case-sensitive.
L238| - Capture and strip run only when `MARKER_ENABLED` or the handoff flag is ON; stop (c) sets both OFF and so disables them too.
L239| 
L240| ### 5.2 Click-attribution criterion (Pixel)
L241| Before stage B, the stage A HAR must show for each synthetic sign-up with a test `fbclid` a `CompleteRegistration` request whose `fbc` (or documented equivalent) contains it (plus source gate 5 text once archived). This proves the click ID is carried, not that Meta credits the campaign; `_fbc` time is completion time. If it fails, no widening until Eric chooses in writing: (a) count-only; (b) reviewed amendment; (c) tester-only, then stop (b).
L242| 
L243| ### 5.3 Acquisition marker document (measure of record; best-effort; decoupled)
L244| **Reuse first.** If IC-0 finds an existing server-side per-account acquisition record that already expresses this Boolean without raw IDs and without touching profile writes, it is reused by amendment.
L245| 
L246| **Otherwise (future, unimplemented):** collection `acq_meta`, document id = the new account's uid, exactly one key `meta_click` (Boolean). IC-0 confirms the collection name is unused.
L247| 
L248| **Value:**
L249| - Campaign mode (default): `meta_click = true` iff the consumed snapshot's `campaign === true`: the browser's **most recent `fbclid` landing** (later landings without `fbclid` do not change it) carried exact `utm_campaign=numista_tg26` and was ≤ 7 days old at sign-up start. Otherwise `false`.
L250| - Meaning, honestly: same-browser, last-`fbclid`-landing heuristic; includes shares of the ad URL and shared-device carry-over; excludes cross-device and older clicks; **not** proof of ad attribution.
L251| - Referral mode (only if Eric declines the tag at G-3, or P-9(i) is unconfirmed at G-7a): `campaign` = any eligible `fbclid`; metric named "Meta-referred sign-ups (ad or organic)" everywhere. Mode is a build constant recorded in the G-7a receipt; never mixed within a window or changed during the freeze. If an ad launches without the tag in campaign mode, M-A carries the caveat that its clicks are not counted.
L252| - P-6 consent variant: `true` also requires `consent === true`; metric prefixed "consenting".
L253| 
L254| **Write behaviour (all plan, none implemented):**
L255| - Issued once, only after the existing **profile create succeeds**, only when `MARKER_ENABLED` and a valid snapshot was consumed. A plain create of `acq_meta/{uid}` with `{meta_click}`; never a merge, never an update, never retried later, never backfilled.
L256| - **Fire-and-forget:** not awaited by sign-up, first-run, readiness or navigation; every error (denied, offline, timeout, quota, missing rules block) is caught and dropped; no UI, no retry loop. Offline: the SDK may queue it; if the tab closes first it is lost.
L257| - Profile create fails → no marker write (the account may exist in Auth without profile; counted in M-U0).
L258| - Missing/invalid snapshot → **no** marker document (unknown is not written as `false`).
L259| 
L260| **Rules block (pseudocode; additive, separate `match`; the profile rules and every other existing byte are untouched):**
L261| ```text
L262| match /acq_meta/{uid} {
L263|   allow create: if request.auth != null && request.auth.uid == uid
L264|                 && request.resource.data.keys().hasOnly(['meta_click'])
L265|                 && request.resource.data.meta_click is bool;
L266|   allow get:    if request.auth != null && request.auth.uid == uid;
L267|   allow list, update: if false;
L268|   allow delete: if request.auth != null && request.auth.uid == uid;
L269| }
L270| ```
L271| - **Create:** owner only, one Boolean key. **Read:** owner `get` only; no `list`. **Update:** never (a second create on an existing doc is an update, so denied and dropped). **Delete:** owner only, so account-deletion and data requests can remove it; a deleted marker only makes that account unmarked. Operators read through existing admin access (rules do not apply to it).
L272| - IC-0 checks for any existing broader `match` (e.g., recursive wildcards) that would also grant writes here. If one exists, the immutability above is not enforced (recorded; acceptable because the marker is client-asserted measurement), and nothing else changes.
L273| - **Availability property:** the profile document, profile rules and profile writes are unchanged. Therefore an old cached client, another plan's app or rules deploy, a rules set lacking this block, or this plan's own rollback can only stop marker writes (default deny → dropped), never sign-up or profile reads/writes (T-8h, T-24).
L274| 
L275| **Account deletion:** IC-0 records the existing deletion path. If it is client code in this tree, the G-3 implementation adds an owner delete of `acq_meta/{uid}` to it (this plan's files only). If it is server-side or elsewhere, the orphan-marker handling is a P-6 counsel item; this plan adds no server code.
L276| 
L277| **Aggregate read:** via the existing admin/console path IC-0 confirms; if none, a read-only aggregate query run by the §8.3 operator with existing admin access under the G-7a YES, joining Firebase Auth creation times with `acq_meta` and profile existence; outputs counts only; synthetic exclusion inside the query; no uid export; no deployed component.
L278| 
L279| **Privacy:** first-party; never sent to Meta; disclosed (P-7).
L280| 
L281| ### 5.4 Measurement definitions
L282| Window: 26 Nov 00:00:00 – 2 Dec 23:59:59 in the P-9 time zone (default America/New_York). "Created" = Firebase Auth creation time. Population **W** = non-synthetic Auth accounts created in the window. Synthetic = every uid in G-6, G-7a, G-7b and daily-canary receipts.
L283| 
L284| | ID | Metric | Definition | Use |
L285| |---|---|---|---|
L286| | M-A | Campaign-tagged sign-ups (**record**) | accounts in W with `acq_meta/{uid}.meta_click == true` | count; a floor (unmarked accounts are not counted) |
L287| | M-A% | Share of marker-written accounts | M-A ÷ accounts in W with any `acq_meta` doc | under the P-6 variant labelled "consenting campaign-tagged sign-ups as a share of all marker-written accounts (denominator includes non-consenting)" |
L288| | M-U | Unmarked accounts | accounts in W with no `acq_meta` doc | **context, not a must-be-0 alarm** (expected populations below) |
L289| | M-U0 | Auth without profile | accounts in W with no profile document (subset view) | context; an existing failure class this plan does not cause |
L290| | M-B | Meta-reported `CompleteRegistration` | Events Manager total in window | different population; reported with synthetic bound (§8.3) |
L291| | M-C | Meta-attributed results | Ads Manager | Meta's figure, unverified |
L292| 
L293| **Expected M-U populations:** accounts created by builds without the marker (service-worker-cached old builds; IC-0 records the caching strategy, source gate 15); other account-creation clients IC-0 inventories (e.g., native, admin, scripts); Auth created but profile create failed or the client saw an error/closed (M-U0); snapshot missing (storage blocked, redirect storage lost); marker write denied, dropped or lost offline; markers deleted by owners; foreign app/rules deploys that dropped the feature.
L294| **Grace:** for 72 h after any app deploy (this plan's or, when known, another's), unmarked web accounts from cached builds are expected.
L295| **Investigation cue (not automatic stop):** outside grace, a day where M-U ≥ 20% of that day's W with W ≥ 10 accounts, or any canary without its marker doc → compare live app/rules with the latest baseline receipt (§6.5). **No ratio is ever computed between M-B and M-A/M-A%.** A zero-Meta day is not an alarm.
L296| 
L297| ### 5.5 What goes where (truthful privacy statement)
L298| **Meta never receives from this plan:** email, name, phone, address, uid, collection data or values, NAC/cert numbers, photo URLs, receipts, estate/AJ data, Stripe IDs, form values, utm values. Meta receives: IP and user agent; Meta cookies; the completion URL `/r/registered[?fbclid=…]` without fragment; no referrer; `autoConfig` boolean `false`; `init` without matching parameters; AAM OFF (P-4).
L299| 
L300| **Numista servers:**
L301| - **Unchanged existing flows:** Firebase Auth and the existing profile and app data (including email and uid) continue to flow to Firebase exactly as today. This plan neither adds to nor removes them.
L302| - **Necessarily reach Numista Hosting:** the initial landing request (`numista.ai/…?fbclid=…&utm_…`) and the completion request (`go.numista.ai/r/registered?fbclid=…`). Hosting/Cloud request logs may record these query strings; IC-0 records whether request logging is on and its retention (source gate 14). The app cannot prevent this.
L303| - **New from this plan:** one `acq_meta/{uid}` document holding one Boolean.
L304| - **Not added:** no app code writes raw `fbclid` or utm values to Firestore, Functions, Storage or any app telemetry; no new analytics storage. The landing record and snapshot are browser-local.
L305| - **Minimisation control (source-gated):** the URL strip removes these parameters from the address bar before Auth initialisation, the redirect and later navigation. Whether every URL-reading SDK runs after the strip is an IC-0 finding (§9); any SDK that records or forwards the page URL before the strip, or any app telemetry that records it, means STOP and amend.
L306| 
L307| ---
L308| 
L309| ## 6. Completion site, constants, CSP, stops, composition
L310| 
L311| ### 6.1 Per-target constants (build time only)
L312| | Target | SPA `COMPLETION_URL` | Completion `RETURN_URL` | Dataset | Completion mode | `MARKER_ENABLED` | Backend |
L313| |---|---|---|---|---|---|---|
L314| | local | `http://localhost:<c>/r/registered` | `http://localhost:<a>/` | test | Pixel | ON | Emulators only (Auth + Firestore with the proposed rules); STOP if unsupported |
L315| | preview | paired preview completion URL | paired preview app URL only | none | no-Pixel | **OFF** | Production project (S-FBMS); synthetic uids receipted |
L316| | production | `https://go.numista.ai/r/registered` | `https://numista.ai/` | prod | no-Pixel (G-4/G-7a); Pixel (G-7b) | ON (OFF = stop c) | Production |
L317| 
L318| Also: handoff flag, `CANARY_ONLY`, `MARKER_MODE`, `META_CAMPAIGN_TAG='numista_tg26'`.
L319| 
L320| **Preview coverage (explicit):** preview binding always fails closed (§4.5), so preview validates only SUPPRESSED paths, overlay → completion → **binding fail** → return, URL strip and zero Meta. The full success path (binding pass, return, resume, Back) is exercised only locally (emulators) and at G-7a on production with testers. G-6 preview is not evidence for it.
L321| 
L322| **T-4 build assertions:** local/preview contain no production dataset, `numista.ai`, `go.numista.ai`; production contains no `web.app`, `firebaseapp.com`, `localhost`; preview has `MARKER_ENABLED=false`; each completion build has exactly one `RETURN_URL` (in `location.replace`, meta refresh `5;url=…`, Continue link); exactly one `nm_meta_canary` check active only under `CANARY_ONLY=true`; exactly one tag constant.
L323| 
L324| ### 6.2 Completion page (Pixel mode)
L325| 1. Run §4.5.
L326| 2. Inject base code (S-GS): `fbq('set', 'autoConfig', false, ID)`; `fbq('dataProcessingOptions', <P-6>)`; `fbq('init', ID)` (no third argument). No PageView, revoke/grant pair or `<noscript>`.
L327| 3. After script `load` only: `fbq('trackSingle', ID, 'CompleteRegistration')`. `T_LOAD` 3000 ms; error/block → nothing sent.
L328| 4. `T_FLUSH` 1000 ms → `location.replace(RETURN_URL)`; hard cap 4500 ms; meta refresh 5 s.
L329| No-Pixel mode runs §4.5 and returns. At most one locally authorized attempt; receipt not guaranteed; no retry, queue or dedup claim.
L330| 
L331| ### 6.3 CSP
L332| App unchanged (no Meta/completion tokens; RP3 untouched). Completion (T-10):
L333| ```text
L334| default-src 'none'; script-src 'self' https://connect.facebook.net;
L335| img-src https://www.facebook.com; connect-src https://www.facebook.com;
L336| base-uri 'none'; form-action 'none'; frame-ancestors 'none'
L337| ```
L338| Plus `Referrer-Policy: no-referrer`, `Cache-Control: no-store`. `connect-src` provisional. No-Pixel and placeholder builds: same minus Meta hosts.
L339| 
L340| ### 6.4 Stop and rollback paths
L341| Each runs under the G-7a/G-7b YES that names it; none is a new permission; none waits for a review. None is instant.
L342| 
L343| | Path | Mechanism | Composition check | Effect |
L344| |---|---|---|---|
L345| | (b) **Pixel kill** | Deploy the reviewed no-Pixel completion build (`--only hosting:<completion>`) | **Completion site only:** live completion release vs this plan's last completion receipt. Mismatch is recorded, and the kill still deploys (removing Meta is always the safe direction; no other plan deploys this site) | New loads run no Meta; pages inside their 4.5 s window unaffected; CDN cache applies. Never blocked by app or rules drift |
L346| | (a) Handoff off | New commit = the **actual current live app commit** + exactly one constant change (handoff flag → false); `--only hosting:<app>` | Diff vs the actual live commit must be exactly that constant (mechanical, receipted). Unrelated live changes from any plan are preserved. If the live build does not contain this feature, nothing to stop (recorded). If the live commit cannot be identified, record and rely on (b); no history rewrite | Marker continues; open tabs continue until reload |
L347| | (c) Marker off (also disables capture, strip and handoff) | Same as (a) but exactly two constants: `MARKER_ENABLED` → false and handoff flag → false | Same mechanical diff check (exactly those two constants) | No more marker writes; sign-up and profiles unaffected; verified by one synthetic sign-up plus one ordinary profile edit |
L348| | Rules block removal | Not a stop; never needed for safety | Full composition gate (non-stop) | Leaving the additive block is harmless; removal later only denies marker writes. **Order: app before rules, always** |
L349| | (d) Site disable/deletion | After (a) plus drain; deletion permanent (S-FBMS) | — | Last resort |
L350| | (e) Meta-side controls | Effects unverified | — | Browsers may still send |
L351| 
L352| Stops never rebase or rewrite history, never force-push, never touch main; each creates a new commit and a receipt.
L353| 
L354| ### 6.5 Composition and deploy provenance (this plan's own deploys only)
L355| **Completion config:** separate config/directory preferred; main `firebase.json` untouched (if array form is used, main block byte-identical, T-11). If this lands before RP3, RP3's own IC-0 must STOP for a composed baseline.
L356| **G-4:** fixed-bytes placeholder (redirect to `https://numista.ai/` + no-Meta policy), receipted.
L357| 
L358| **Non-stop deploys** (G-7a, marker-only G-7a, stage A, stage B, any later feature change) are **composition-gated:**
L359| 1. The target's live release (app and rules for app/rules deploys; completion only for completion deploys) matches the latest `LIVE_BASELINE` receipt (before the first: the IC-0 live baseline, incl. RP3/Images/Catalog if live). Mismatch → STOP, re-base, re-diff, re-review under the same gate.
L360| 2. Exact recorded feature-branch commit on that baseline; diff only this plan's files; rules diff = only the appended `acq_meta` block.
L361| 3. `--only hosting:<target>` or `--only firestore:rules`; never bare `--only hosting`.
L362| 4. Order: G-7a rules → completion (no-Pixel) → app; marker-only rules → app; stage A completion; stage B app.
L363| 5. New immutable receipt `LIVE_BASELINE_<n>.md` after each deploy (app commit, rules hash, completion commit).
L364| 
L365| **Stops** follow §6.4 instead and are never blocked by this gate.
L366| 
L367| **Future coordination (recorded, not enacted):** while unmerged, production runs bytes not on main. Another plan's non-composed app or rules deploy can drop the checkbox, handoff or marker writes. Because the marker is decoupled (§5.3), the worst case is lost measurement or handoff, **never** an account-availability or profile-write failure. The receipts exist for other plans' existing baseline checks; this plan sets no policy for them. Merging is outside this plan.
L368| 
L369| **Deploy freeze 26 Nov – 2 Dec:** no non-stop deploy of this plan. A feature lost to a foreign deploy during the window is not restored in the window (gap reported).
L370| 
L371| ---
L372| 
L373| ## 7. Disclosure (P-7; counsel and Eric)
L374| The privacy text must: name Meta as a recipient of IP, browser data, cookies, the completion URL (incl. any `fbclid`) and the event; state Meta cookies may be scoped to `numista.ai` (T-13); describe the landing record, the URL clean-up and the first-party `acq_meta` marker; state that Numista's hosting may log landing/completion URLs containing click IDs (per IC-0 retention); state revocation does not delete Meta cookies or data; make no anonymity or "no personal data" claims. It may state that collection contents, values, photos, certification numbers, names, emails and addresses are not sent to Meta. Meta cookies are not cleared on revocation.
L375| 
L376| **Meta cookie scope.** If T-13 shows `.numista.ai` scope, stage B requires (i) the stage-B re-inventory (§9) shows no reader transmitting `_fb*` off-origin, or each is excluded by amendment, and (ii) Eric's written acceptance under the G-7b YES. Otherwise no widening.
L377| 
L378| ---
L379| 
L380| ## 8. Production sequence (fail-closed; real users never see the Pixel before stage A passes)
L381| Synthetic runs use production accounts; uids in receipts; excluded from §5.4. **Synthetic accounts are left intact; deleting any is a separate destructive action needing its own approval.** "Added latency" = overlay shown → first-run route rendered in the return document (upper bound). Thresholds over a few runs are **smoke maxima, not population percentiles.**
L382| 
L383| ### 8.1 G-7a (production; no Pixel; handoff tester-only)
L384| Rules (append `acq_meta` block) → completion (no-Pixel) → app (`MARKER_ENABLED`, handoff ON, `CANARY_ONLY=true`). Real users get only the URL strip and the best-effort marker (plus the checkbox if P-6 requires marker consent). Fresh browser profile per run unless stated; canary runs set `nm_meta_canary='1'`; "campaign landing" = test `fbclid` + `utm_campaign=numista_tg26` + one unrelated parameter and a deep route.
L385| 
L386| | # | Device | Case | Handoff | `acq_meta` |
L387| |---|---|---|---|---|
L388| | 1 | desktop | Email, consent on, campaign landing; then one ordinary profile edit | yes | true |
L389| | 2 | desktop | Email, consent on, no landing; then one ordinary profile edit | yes | false |
L390| | 3 | desktop | Popup new, consent on, campaign landing | yes | true |
L391| | 4 | mobile | Redirect new, consent on, campaign landing | yes | true |
L392| | 5 | desktop | Email, consent off, campaign landing | no | true (false under P-6 variant) |
L393| | 6 | desktop | GPC on (checkbox hidden), no landing | no | false |
L394| | 7 | desktop | Email, consent on; Back from completion before return | `pending` row | false |
L395| | 8 | desktop | Email, consent on; after return, Back | `consumed` row → reload, no replay | false |
L396| | 9 | mobile | Redirect new, unticked at click, ticked after return | no | false |
L397| | 10 | desktop, run-1 profile | Second new account, box unticked, no new landing | no; box unchecked | false |
L398| | 11 | desktop | Email, consent on, `fbclid` landing without tag; re-open the same original landing URL twice before sign-up | yes | false; `captured_at` unchanged by the repeats |
L399| 
L400| **Pass:** all 11 match; every essential first-run document exists; profile edits in 1–2 succeed; marker docs exactly as expected and one per run; address bar after boot lacks `fbclid`/`utm_*` while the deep route and unrelated parameter survive; no duplicate first-run (7, 8); `nm_hoff` set/removed per HAR and cookie listing; **zero Meta requests** in every HAR; added latency max ≤ 8 s on handoff runs (desktop and mobile listed separately); no `not_ready`.
L401| **On fail:** handoff defect → stop (a); marker or URL-strip/capture defect → stop (c) (which also turns capture and strip off, §5.1). G-7b does not start.
L402| 
L403| ### 8.2 G-7b stage A (production Pixel, tester-only)
L404| Immediately before: stage-A re-inventory (§9). Deploy completion in Pixel mode (production dataset); app unchanged (`CANARY_ONLY=true`). Exactly 6 canary, consenting synthetic sign-ups, timestamps receipted:
L405| 
L406| | # | Device | Case | `acq_meta` |
L407| |---|---|---|---|
L408| | 1 | desktop | Email, campaign landing (`fbclid` A) | true |
L409| | 2 | mobile | Email, campaign landing (B) | true |
L410| | 3 | desktop | Email, `fbclid` C without tag | false |
L411| | 4 | desktop | Popup, campaign landing (D) | true |
L412| | 5 | mobile | Redirect, campaign landing (E) | true |
L413| | 6 | desktop | Email, no landing | false |
L414| 
L415| - **HAR (emitted):** exactly 6 `/tr` `CompleteRegistration` requests, one per run; no other Meta event, PageView, `ud[`/`udff[`, metadata; `dl` without fragment; `nm_hoff` gone before `fbevents`; `fbc` carries A–E for runs 1–5 (§5.2).
L416| - **Events Manager (received k):** evaluated **no earlier than +2 h and finally at +24 h** after the last run (source gate 1); counts by receipted time range; no per-browser trace claimed. k = 6 passes this item; k > 6 fail-and-investigate; k < 6 at +24 h fail-and-investigate, with at most one rerun per missed case when the HAR records a local non-design reason (rerun k evaluated the same way); still missing → fail.
L417| - Also: no CSP violations; T-13 scope recorded and §7 satisfied; §5.2 met or Eric's written choice; P-3, P-4, P-5, P-7, P-9(ii) done.
L418| **On fail:** stop (b); no widening.
L419| 
L420| ### 8.3 G-7b stage B (widen; same YES) and campaign watch
L421| - Immediately before: stage-B re-inventory (§9). Only if stage A passed and stage B completes by **25 Nov 23:59 ET**: app redeploy (composition-gated) with `CANARY_ONLY=false`. Otherwise the Pixel stays tester-only for the window.
L422| - **Operator and cadence:** the operator named in the G-7a receipt (Eric or the person he designates, using existing admin access only). Daily at about 9:00 AM ET, from the day after G-7a through 3 Dec: run the read-only count query (M-A, M-A%, M-U, M-U0 for the previous day and window-to-date) and, from 25 Nov through 2 Dec, two canary-marked consenting synthetic sign-ups (desktop email + campaign landing; mobile cellular Google redirect, no landing). Canary checks: account and essential first-run docs; one ordinary profile edit succeeds; marker doc correct; clean address bar; right route; HAR shows exactly one `CompleteRegistration` per run and nothing else (Pixel off or marker-only: zero Meta); latency recorded.
L423| - **Blind spots stated, not assumed away:** between daily checks nothing is observed; up to about a day of lost markers or broken handoffs can go unseen. This is proportionate only because this plan's design cannot cause profile-write or sign-up failures (§5.3); it does **not** assert that sign-up is healthy between checks, and outages from other causes are outside this plan's detection.
L424| - **Synthetic accounting:** HAR-emitted canary count N per period is receipted. Observed canary events are subtracted from M-B only where source gate 1 shows them individually, and only for ranges overlapping the receipted times; otherwise M-B is reported with real events in [total − N, total].
L425| - **Real-user stranding and latency are not observable** (no new telemetry). Protection: canaries; if IC-0 finds an existing onboarding-completion field, a read-only share comparison (pre- vs post-widening days, ≥ 30 accounts each side, else "insufficient"); support channels.
L426| - **Triggers:** canary handoff failure, missing return, `not_ready`, or latency > 8 s → stop (a). Canary marker missing/wrong → investigate composition; stop (c) only if this plan's marker code is at fault. Onboarding share down ≥ 10 pp (when evaluable) or a credible stranding report → stop (a). Any Meta request from the SPA, a PII parameter, or unexpected events → stop (b). M-U alone is a §5.4 investigation cue, not a stop.
L427| 
L428| ### 8.4 Timeline and marker-only fallback
L429| - Targets: G-7a by 20 Nov; stage A by 23 Nov (k final by 24 Nov); stage B by 25 Nov.
L430| - **Marker-only fallback:** if G-4 or the preview part of G-6 is not done by 20 Nov, G-7a deploys the same commit with the handoff OFF and no completion deploy: rules → app. Needs G-5 and the local part of G-6 (T-22, T-24 on emulators). Production checks under the G-7a YES: landings of runs 1, 4, 5, 11 (no checkbox, so no consent), handoff "no" for all, markers true, true, true, false, profile edit succeeds, clean address bar, zero Meta. Pixel off for the campaign.
L431| - If even marker-only cannot deploy by 24 Nov: no marker for the campaign; reporting is M-C only, labelled.
L432| 
L433| ---
L434| 
L435| ## 9. IC-0: future read-only verification (hashed receipt; drift → STOP and amend)
L436| **Full IC-0:** before G-3, re-run before G-7a.
L437| - Record: current commit/tree; live app and rules baseline (commit, hash); hosting config; app CSP; Meta presence; URL strategy; service-worker caching strategy (source gate 15); Hosting/Cloud request-log setting and retention (source gate 14).
L438| - Sign-up: call sites; which Google mode runs where; success points; the single redirect consumer; **every account-creation client** (web builds, native, admin tools, scripts).
L439| - First-run: operations and ack semantics; resume enum; profile create success point; whether a normal signed-in boot re-issues first-run writes non-idempotently (STOP).
L440| - Marker: `acq_meta` name unused; existing rules matches overlapping `acq_meta/{uid}` (recorded); existing acquisition record, consent UI, onboarding-completion field, admin aggregate path; account-deletion path.
L441| - **URL readers:** every script/SDK and app telemetry that reads or records `location`/page URL (error reporting, analytics, support widgets, Flutter bootstrap), and whether each runs before boot step 2. STOP if any records or forwards the URL before the strip, or if app telemetry records URLs containing the stripped parameters.
L442| - Cookies/hosts: every `Domain=numista.ai` cookie (STOP if any carries auth/uid/session/account data or is non-HttpOnly sensitive); every `numista.ai` host (STOP if untrusted script); every cookie reader (app, SDKs, Hosting rewrites; source gate 10).
L443| - Flag mechanism; emulator support; `/r/` unused on the app site.
L444| - Archive source gates 1–15 where possible.
L445| 
L446| **Re-inventories (read-only subset, same receipt format), immediately before stage A and again before stage B:** parent-domain cookies, `numista.ai` hosts, cookie readers and URL readers, since Meta's script first runs at stage A and real users first meet it at stage B. Any new finding → no deploy of that stage until amended.
L447| 
L448| ---
L449| 
L450| ## 10. Test contracts (future; none run)
L451| G-5 = T-1–T-12, T-23. G-6 = T-13–T-22, T-24 where applicable (preview limited per §6.1). §8 tables are production contracts.
L452| 
L453| | ID | Contract |
L454| |---|---|
L455| | T-1 | Static: no `fbq`/`fbevents`/`connect.facebook.net`/`facebook.com/tr` in the SPA; completion `autoConfig` literal boolean `false`. |
L456| | T-2 | Handoff OFF/empty constants → no handoff, no checkbox (unless P-6), marker still written; `MARKER_ENABLED` OFF → no `acq_meta` write and sign-up behaviour identical. |
L457| | T-3 | §4.3 trigger table; spy proves one redirect consumer. |
L458| | T-4 | Checkbox unchecked on open, never pre-filled, hidden under GPC; snapshot consent = checkbox at click; later ticks ignored; probe failure → `cookie_probe`; canary gating; §6.1 build assertions incl. preview `MARKER_ENABLED=false`. |
L459| | T-5 | Attempt-id guard: same id twice, reload, duplicated tab → ≤ 1 handoff; no uid stored locally. |
L460| | T-6 | Landing: different `fbclid` overwrites; identical `fbclid` keeps original `captured_at`/`campaign_match`; exact tag only (case/prefix/suffix/list → false); tag without `fbclid` → nothing; 7-day expiry; deleted at create. Strip: after boot the URL has no `fbclid`/`utm_*` in query or hash query, path/hash route/other parameters preserved in order, history state kept; strip runs before Auth init and the redirect consumer; `replaceState` failure tolerated. No app code path writes raw `fbclid`/utm to Firestore, Functions, Storage or telemetry (static + spy). Completion URL has only `fbclid`, only with consent. Nonce random. |
L461| | T-7 | `rel=noreferrer`. |
L462| | T-8 | (a) no `await` on Meta or marker; (b) flag ON vs OFF: identical account state, essential first-run writes, post-return route; (c) delayed essential write → `not_ready`, no later navigation; non-enum → `not_resumable`; (d) overlay has no inputs; (e) unreachable host → error page, Back → `pending` row; (f) Back after return → `consumed` → reload; (g) other tab never consumes `nm_resume`; **(h) marker write denied / rules block absent / offline / hanging / throwing → sign-up, readiness timing, first-run and later profile create, read and edit (merge and non-merge) all unaffected.** |
L463| | T-9 | Builds without `ENABLED`/`ID` → no-Pixel page; placeholder bytes match receipt. |
L464| | T-10 | Completion CSP/headers per §6.3; no inline script. |
L465| | T-11 | Main hosting block, app headers and the live rules baseline byte-identical apart from the appended `acq_meta` block; **no profile rule change.** |
L466| | T-12 | Empty `document.referrer` on completion; no `Referer` on Meta requests. |
L467| | T-13 | Real-host cookie listing with Domain scope; only `nm_hoff` from the app on `go.`, gone before Meta loads; `_fbp`/`_fbc` scope vs re-inventory. |
L468| | T-14 | Signed-in reloads, demo/guest, signed-out: zero Meta. |
L469| | T-15 | Local (gate 6) and stage A: one event per consenting new account; no fragment in `dl`; no `ud`/`udff`/PageView/metadata; §5.2. |
L470| | T-16 | Popup new = 1; redirect new = 1; returning = 0; ticked only after return = 0. |
L471| | T-17 | Delivery smoke: HAR emitted 6; k per §8.2 timing rules. |
L472| | T-18 | Binding failures each → 0 + immediate return: no cookie; wrong nonce; > 60 s; reused; reload; Back; `web.app`; two `nm_hoff` (incl. two tabs within 60 s → both 0); ineffective deletion. `nm_hoff` gone before `fbevents`. |
L473| | T-19 | Ad blocker/CSP block → nothing sent, return ≤ 4.5 s; no-JS → refresh at 5 s. |
L474| | T-20 | Reasons: `flag`, `canary`, `attempt`, `consent`, `gpc`, `guard`, `cookie_probe`, `not_new`, `not_ready`, `not_resumable`, `binding`, `load_timeout`, `blocked`, `sent`. |
L475| | T-21 | Stops per §6.4: (b) proceeds despite app/rules drift; diff vs the actual live commit is exactly one constant for (a) and exactly two for (c); unrelated live changes preserved; open tabs documented; app before rules. |
L476| | T-22 | Marker doc per §5.3 across email/popup/redirect, both modes: written only after profile create success; never awaited; missing snapshot → no doc; profile create failure → no doc; one doc per account. Emulators only. |
L477| | T-23 | Snapshot table (§4.2): written after validation, before the auth call; consumed once; deleted on error/cancel/sign-in/abandoned redirect/boot; validation failure writes nothing; expired/malformed/mismatch → SUPPRESSED, no doc; storage throwing → sign-up proceeds; no uid/email/utm inside. |
L478| | T-24 | Rules (emulator): `acq_meta` owner create with exactly one bool → allowed; extra key, non-bool, other uid, unauthenticated → denied; update/second create → denied; owner delete → allowed; owner get → allowed; list → denied. Profile rules unchanged; every profile operation of the current, a marker-less and a rollback build passes with and without the block. Count query on seeded emulator data (Auth with profile+marker, without marker, without profile; synthetic) yields M-A, M-A%, M-U, M-U0 exactly. |
L479| 
L480| ---
L481| 
L482| ## 11. Decisions and defaults
L483| **Fixed:** separate test dataset; no probe; 7-day eligibility; tag `numista_tg26` exact; identical-`fbclid` keeps original time; strip all `utm_*` and `fbclid`; marker in its own create-only doc, best-effort, never awaited, no backfill; unknown snapshot → no doc; owner may delete marker; no staging; no Meta cookie clearing; separate completion config preferred; anonymous upgrade and post-request consent never count; G-7a before G-7b; no widening after 25 Nov; freeze in window except stops; synthetic accounts left intact; no M-B/M-A ratio; preview `MARKER_ENABLED=false`.
L484| **Remaining decisions at existing gates:** G-3: §4.7/§13 acceptance, marker mode, P-6 (incl. retention/deletion). G-4: P-8. G-6: local-only scope or not. G-7a: P-9(i); operator named; stops (a)–(c) listed in the YES. G-7b: P-7, P-9(ii); stops listed; §5.2 choice only on failure; §7 acceptance only if scope is `.numista.ai`.
L485| 
L486| ## 12. Security preservation
L487| **App:** no third-party script; no CSP change; no profile-document or profile-rule change. New browser storage: localStorage `nm_landing`, `nm_attempt_used` (ids only), `nm_meta_canary` (tester-set); sessionStorage `nm_attempt`, `nm_resume`. Cookies: transient `nm_probe`, `nm_hoff`; possibly Meta `_fbp`/`_fbc` at `.numista.ai` (§7). New server data: `acq_meta/{uid}` with one Boolean. Rules: one appended `match` block.
L488| **Unchanged:** main-site hosting; RP3; owner-storage guard; Stripe OFF; existing Auth/profile data flows. The completion site has no Firebase, keys or Auth.
L489| 
L490| ## 13. Residuals and trade-offs (candid)
L491| - The marker is a same-browser, last-`fbclid`-landing, 7-day heuristic: misses cross-device/older clicks, storage-blocked browsers, lost redirect storage, dropped best-effort writes, owner deletions and old cached builds; includes shared-device carry-over, ad-URL shares and self-forged values. M-A is a floor; M-U shows the unmarked remainder without explaining it.
L492| - Referral mode, if chosen, cannot separate ad from organic Meta traffic.
L493| - M-B and M-A are different populations and never compared; M-C is unverified.
L494| - Landing and completion URLs with click IDs necessarily reach Numista Hosting and may sit in request logs for the configured retention.
L495| - Real-user stranding and latency are unobservable; detection of lost markers or handoffs is daily, not continuous.
L496| - Delivery to Meta is not guaranteed; stage A k < 6 can block widening even when the design is right.
L497| - Two tabs handing off within 60 s both fail closed (undercount).
L498| - Another plan's non-composed deploy can silently remove the feature; it cannot break sign-up or profiles. Features lost during the freeze are not restored in the window.
L499| - A pre-existing broad rules wildcard (if IC-0 finds one) leaves the marker mutable by its owner.
L500| - Synthetic production accounts (about 11 + 6 + 16 + reruns) remain.
L501| - The handoff machinery is heavier than the lean marker-only core; Eric may choose marker-only at G-7a by declining the handoff (a business trade-off; no question needed now).
````

=== END FILE A (line-numbered view) ===

---

## FILE A-verbatim — `PLAN_META_PIXEL_SIGNUP_ATTRIBUTION_v6.md` (exact bytes of File A)
SHA-256 `8df72e6b558742ae388db965417cddf8f346d1992c056f5aa3f0350228533df3` · 56447 bytes

````markdown
# PLAN — Meta Pixel signup attribution (web), v6

**Status: PLAN ONLY.** Eric, 9 Nov 2026, 9:20 AM EST: "Prepare the Meta Pixel plan only; no implementation until my YES."

This document approves nothing: no implementation, Pixel or dataset creation, Meta setting, Test Events, DNS, Hosting site, deploy, rules change, Firestore write, ad or synthetic account. Every consent, canary, marker, rules, URL and deploy change below is **future, UNIMPLEMENTED and permission-gated**. Rule text, diagrams and pseudocode are plan text, not app code, and no Firestore collection, document or rule described here exists. Every test is a future contract; none has run. Nothing here asserts what the current code does beyond the cited audit records; IC-0 (§9) verifies it, and drift the design cannot absorb means STOP and a reviewed amendment.

**Gates** (unchanged since v3; v6 adds none). Each is a separate approval, in this order.

| Gate | Approval |
|---|---|
| G-1 | Independent CoS review ≥ 95 |
| G-2 | Full-plan SAG ≥ 95 |
| G-3 | Eric typed YES for implementation (feature branch, flags OFF), including acceptance of §4.7 and §13 residuals, the marker mode (§5.3) and counsel's P-6 decisions |
| G-4 | Eric YES for subdomain, DNS and a new Hosting site (existing permission scope, unchanged) |
| G-5 | Implementation; contracts T-1–T-12 and T-23 green |
| G-6 | Eric YES for the local and preview test run (he may scope it to local only, §8.4) |
| G-7a | Eric YES for the first production deploys (marker live; handoff tester-only; no Pixel). The request lists stop paths (a)–(c) of §6.4 by name so they run under this YES |
| G-7b | Eric YES for the production Pixel: stage A tester-only, then stage B under the same YES, only on pass (§8). Stop paths (a)–(c) listed by name |

**Prepared** 9 Nov 2026 EST on the box, documentation only. No repo, source tree, laptop, Meta account, credential, DNS, Hosting or browser touched; no test, deploy, SAG or paid call; nobody contacted. Main stays locked at `9f04550a`. Stripe stays OFF.

**Attempt ledger (inherited; no reset).** Eric's rule, as relayed verbatim by Desk (original Eric message not retrieved; relay reference CoS transcript ≈ pos 7616): "if someone is still failing after 4 tries, somebody else take over. If NO ONE gets it right by 10 total attempts, you notify me and we break it down into smaller bite-size chunks."

| Global attempt | Writer | Submission | CoS gate result |
|---|---|---|---|
| 1–4 | original | v1–v4 | 87, 91, 92, 92 REVISE → writer retired |
| 5 | replacement, try 1 | v5 | 94 REVISE, critical B1 (`cos-review/v5/COS_GATE_DISPOSITION.md`, 11:07:59 AM EST) |
| **6** | **replacement, try 2** | **v6 (this file)** | pending; not self-scored |

If this writer is still failing after try 4 (v8), somebody else takes over; no success by global attempt 10 → Eric is notified and the work is split. Reviews, mirrors, rescores and hash files add zero. All earlier artifacts stay byte-identical (`PRESERVATION_V6_CHECK.sha256`). `CLOSURE_MAP_v6.md` maps B1–B3, N-A, N-B and this writer's new independent findings (Y1–Y8).

---

## 0. Goal and design

**Goal (Thanksgiving campaign, Thu 26 Nov – Wed 2 Dec 2026):**
1. **Measure of record:** a first-party, best-effort acquisition marker in its **own create-only document** (§5.3), counting new accounts whose browser's most recent `fbclid` landing carried the exact campaign tag within 7 days. Measurement can be lost; it can never block, delay or fail sign-up or any profile write.
2. **Optional:** one parameterless Meta `CompleteRegistration`, at most one locally authorized attempt per consenting new account, only from an isolated completion origin, never from the Flutter SPA, with no collector data.
3. Meta's own attribution is reported as Meta-reported only.

**Design core (unchanged):**
1. The Flutter SPA on `numista.ai` never loads Meta code and never makes a Meta request; its CSP gains no Meta or completion tokens.
2. A separate-origin static **completion document** (`go.numista.ai`, placeholder name fixed at G-4) is the only place the Pixel runs. No Flutter, Firebase, app data, auth or inline script.
3. After a confirmed, ready, consenting new account, the SPA binds the handoff with a 60 s nonce cookie, navigates top-level to the completion document, which verifies, makes one attempt and returns to a fixed URL.

**v6 structural changes:**
- **Marker decoupled from the profile (B1).** v5's profile field and every profile-rule change are removed. The marker is a separate owner-keyed, create-only document written best-effort *after* the essential profile create succeeds; it is never awaited. Profile documents, profile rules and profile writes are untouched by this plan.
- **Stops are never blocked by composition review (B2).** The Pixel kill touches only the completion site; app stops are one-constant mechanical diffs on the actual live release.
- **Tracking parameters stripped from the app URL immediately after capture (B3)**, with truthful statements about what reaches Numista servers.

**Out of scope:** CAPI; PageView or landing Pixel; commerce events and value; Advanced Matching; audiences; native apps; appeals, ad launch, budget; staging; reachability probe; server tokens; any new server, function, dashboard, telemetry or analytics platform; legal decisions (counsel); any cross-team deploy policy.

### 0.1 Facts and trust level
| Claim | Source | Trust |
|---|---|---|
| No Pixel on `numista.ai`; current CSP blocks Facebook | SourceAuditor, 6 Nov (`/workspace/site-audit/thanksgiving_gap_audit_20261106.md:7`; `/workspace/site-audit-2026-11-06/THANKSGIVING_GAP_AUDIT_06NOV.md:84–87`) | Reported; IC-0 re-checks |
| Candidate dataset `2540753249725498` | NET-706 R7 | Unverified (P-2) |
| Old domain-verification tag | NET-706 R7 | Not reused (P-3) |
| Hosting site `numista-vault`; preview `numista-vault--<ch>-*.web.app` | Earlier plans | IC-0 confirms |
| Sign-up surfaces: email/PIN, Google popup, Google redirect | Earlier plans | IC-0 confirms which Google mode runs where |

---

## 1. Sources

Archived; hashes re-verified for this draft (each manifest run inside its directory): `sources-v2/` 19/19 OK, `sources-v3/` 10/10 OK.

**Meta (`sources-v2/`):** S-ADV `advanced.txt` L479 `fbq('set', 'autoConfig', false, 'FB_PIXEL_ID');` (boolean; L467 prose string not used; T-1); L492 CSP (`https://connect.facebook.net`, paths `/en_US/fbevents.js` and `/signals/config/{pixelID}?v={version}`); `trackSingle`; button-click auto-detection; `/tr`. S-GDPR (revoke "on every page"; data received incl. headers, IP, page location, referrer, Pixel ID, Facebook cookie, button clicks, field names). S-REF, S-SPA (not used), S-AM (third `init` argument; not used), S-DPO (`dataProcessingOptions` before `init`), S-GS, S-CT.

**Non-Meta (`sources-v3/`):** S-FBMS (multisite; per-site config; `--only hosting:TARGET_NAME`; deletion permanent). S-FBPV (preview URLs random, public). S-6265 (§8.5 no port isolation; step 11 `rfc6265.txt` L1299 replace on same name/domain/path; L719–723 duplicates coexist; §5.1.4 path-match). S-PSL (`web.app` L13988, `firebaseapp.com` L13706). S-RP (`no-referrer`). S-SS (`mdn_storage_sessionStorage.txt`: "partitioned by both origin and browser tabs"; "survives over page reloads and restores"; new tab = new session; opener copy).

**Source gates** (no archived text; future verification only). Each is used only where the design fails closed or degrades only measurement if the hypothesis is false:

| # | Hypothesis | If false |
|---|---|---|
| 1 | Events Manager / Test Events shows stage A receipt within 24 h (per-event detail optional) | Counts by time only; k not visible by +24 h = fail-and-investigate (§8.2) |
| 2 | Domain verification and subdomain coverage | No stage B (P-3) |
| 3 | AAM toggle | No stage B (P-4) |
| 4 | Event configuration/AEM | No stage B (P-5) |
| 5 | `fbclid` → `_fbc`/`fbc` | §5.2 written choice; marker unaffected |
| 6 | Meta accepts `localhost` events | Local Pixel case skipped |
| 7 | Preview channel stability | Re-create preview; never production |
| 8 | Firebase write-ack semantics in the tree's SDK | Readiness unprovable → STOP |
| 9 | Meta first-party cookie scope controls | §7 widening condition |
| 10 | Cookies Hosting forwards to rewrites | Inventory treats all as forwarded |
| 11 | sessionStorage survives a same-tab cross-origin round trip | No handoff; no marker doc (unmarked); normal boot |
| 12 | Meta ad URL parameters deliver the exact `utm_campaign` | P-9(i) at G-7a; else referral mode |
| 13 | A client's Firestore writes are acknowledged in issue order | A marker write pending at handoff navigation may be lost → unmarked only |
| 14 | Firebase Hosting / Cloud Logging request-log behaviour and retention for this project | §5.5 claim already allows logged query strings; IC-0 records the actual setting |
| 15 | Flutter service-worker caching keeps old builds for a bounded time | M-U grace (§5.4) is context, not an alarm rule |

---

## 2. Prerequisites (account facts at the named gate; nothing is asked now)
| ID | Item | Gate |
|---|---|---|
| P-1 | Business portfolio and admin | G-6 |
| P-2 | Production dataset confirmed, plus a separate test dataset | G-6 |
| P-3 | Fresh domain verification for `numista.ai` (and `go.` if required) | G-7b |
| P-4 | AAM OFF; automatic events/metadata OFF; screenshot | G-7b |
| P-5 | Event configuration/AEM if required | G-7b |
| P-6 | Counsel: checkbox copy, GPC, LDU, whether marker and landing capture need consent, marker retention and account-deletion handling | G-3 |
| P-7 | Privacy text approved and live before stage B (§7) | G-7b |
| P-8 | Subdomain name, DNS, new Hosting site | G-4 |
| P-9 | (i) Every campaign ad's URL parameters contain `utm_campaign=numista_tg26` (ad preview link, no paid click) and the campaign reporting time zone recorded; (ii) objective viable with `CompleteRegistration` only | (i) G-7a; (ii) G-7b |

---

## 3. Event
Only `CompleteRegistration`, no parameters, only from the completion document. No PageView anywhere.

---

## 4. Sign-up flow and handoff (SPA side)

### 4.0 End-to-end traces (plan, not current-code claims)
**Boot order (every app document, exact):**
1. **Landing capture** (§5.1) reads `fbclid`/`utm_campaign` from the URL.
2. **URL strip** (§5.1): `history.replaceState` removes `fbclid` and every `utm_*` parameter, preserving path, all other parameters and the hash route.
3. Firebase Auth initialisation; then the **single** `getRedirectResult` consumer.
4. Snapshot housekeeping (§4.2) and resume handling (§4.6); then normal routing.
IC-0 confirms whether any SDK or script reads the URL before step 2; if one records or forwards it, STOP and amend (§9).

**Email/PIN:**
1. Form opens; checkbox rendered **unchecked** (only when the handoff is active and GPC is not set, §4.2); never pre-filled.
2. Submit: client-side validation first. Only after it passes, synchronously and immediately before the create call, write snapshot `nm_attempt` with `method:'email'`. A validation failure writes nothing.
3. Create fails (any error incl. `email-already-in-use`) → delete snapshot.
4. Create succeeds → trigger (§4.3) → **consume** snapshot → marker value and handoff inputs fixed in memory → existing first-run writes (unchanged) → DECIDE (§4.4).
5. When the existing **profile create** succeeds, issue the marker document create (§5.3), fire-and-forget. Nothing waits for it.
6. SUPPRESSED → existing first-run path. PASS → overlay, readiness (essential first-run ops only), resume record `pending`, cookie, navigate.
7. Completion → binding → (no-Pixel or Pixel) → `location.replace(RETURN_URL)` → fresh app doc → boot (URL is already clean) → resume `pending` → restore once → `consumed`.
8. Back after return → original doc (bfcache) sees `consumed` → reload; no first-run replay (§4.6).

**Google popup:** as email, except step 2 has no validation: the button click writes snapshot `method:'google_popup'` synchronously, then calls the popup in the same gesture. Popup closed/blocked/error → delete snapshot. `isNewUser == false` → delete snapshot; landing record untouched; no marker, no handoff. `isNewUser == true` → email steps 4–8.

**Google redirect (exact order):**
1. Page was already stripped at boot (step 2), so the URL handed to the redirect carries no `fbclid`/utm.
2. Click → write snapshot `method:'google_redirect'` synchronously → start redirect → document unloads.
3. Return to `numista.ai` in the same tab: boot step 1 finds no `fbclid` (the stored landing record from before is unchanged); step 2 no-op; step 3 the redirect consumer.
4. `isNewUser == true` → consume snapshot (S-SS, source gate 11) → email steps 4–8.
5. Null, error or `isNewUser == false` → delete snapshot.
6. Snapshot missing, expired, malformed, method mismatch or guarded → no handoff (SUPPRESSED `attempt`) and **no marker document** (counted as unmarked, §5.4). Sign-up never blocked.
7. Consent ticked after returning cannot count; only the pre-redirect snapshot exists.

### 4.1 Ownership
One future SPA service, `SignupAttributionHandoff`, owns: checkbox; landing capture and URL strip; snapshot and attempt-id guard; marker value and its best-effort write; DECIDE, readiness, overlay; binding cookie; resume record and bfcache. The marker part runs when `MARKER_ENABLED` is true, independent of the handoff flag (T-2). IC-0 maps these to real paths. T-1 asserts zero Meta references in the SPA.

### 4.2 Consent checkbox and attempt snapshot
**Checkbox.** One unchecked, optional checkbox directly above the email submit and the Google button(s); counsel copy (P-6); not required to sign up. Rendered only when the handoff is active for this browser (flag ON, and `CANARY_ONLY` false or `nm_meta_canary === '1'`) and `navigator.globalPrivacyControl !== true`. Never pre-filled. If P-6 requires consent for the marker, shown from G-7a to all non-GPC users with copy covering both uses. Existing consent UI reused only if IC-0 proves the same semantics. Sign-up UX change accepted at G-3 (§4.7).

**Snapshot** `nm_attempt`, app-origin **sessionStorage** (per tab):
```text
{ v:1, id:<128-bit random, base64url>, method:'email'|'google_popup'|'google_redirect',
  consent:<checkbox checked AND GPC !== true>, campaign:<Boolean>, fbclid:<string|absent>,
  exp:<now + 30 min> }
```
`campaign` = an eligible landing record (§5.1) with `campaign_match === true` (referral mode: any eligible landing). `fbclid` copied only if `consent === true`. No uid, email, name, password, token, URL or utm value. If sessionStorage throws, no snapshot: sign-up proceeds, no handoff, no marker doc.

| Event | Action |
|---|---|
| Confirmed create (§4.3) | Read then delete `nm_attempt`. Valid only if well-formed, `method` matches, `exp` not passed, `id` not in `nm_attempt_used`; then add `id`. Delete `nm_landing` in every case |
| Auth error, cancel, popup closed, existing-user sign-in | Delete `nm_attempt`; keep `nm_landing` |
| Client-side validation fails | Nothing written (snapshot is written only after validation) |
| App boot with a non-redirect snapshot | Delete |
| Boot whose redirect consumer returns null/error with a redirect snapshot | Delete |
| Missing, expired, malformed, mismatched, guarded | Delete if present; SUPPRESSED(`attempt`); no marker doc |

**Revocation.** Unchecking before the request means `consent:false`. After create no further Meta event is sent for the account. Revocation does not delete Meta cookies, recall data, stop an in-flight completion page or unload a script (§7).

**Shared devices.** Consent never carries over; the consumed landing record is deleted at create. Residual (§13): a landing left by someone who never signed up can mark another person's sign-up on the same browser within 7 days.

### 4.3 Trigger
- **Email/PIN:** server-confirmed create.
- **Google:** `isNewUser == true` from the popup result or the single existing `getRedirectResult` consumer (never called twice; if none exists, exactly one is added by amendment).
- **Never:** sign-in; failures; linking; anonymous upgrade; demo/guest; `authStateChanges` alone; token refresh; restart.

### 4.4 DECIDE, readiness and UI that never interrupts input
**Pre-checks** (synchronously after consumption, before any first-run UI); all must hold:
1. Handoff flag ON.
2. `CANARY_ONLY` false, or `localStorage nm_meta_canary === '1'`.
3. Snapshot valid and `consent === true`; GPC re-checked.
4. Attempt-id guard passed at consumption (`nm_attempt_used`: attempt ids only, pruned after 1 h; no uid).
5. Cookie probe: `navigator.cookieEnabled`; host-only `nm_probe=1; Path=/; Max-Age=5; Secure; SameSite=Strict` set, read back, deleted (local omits `Secure`).
6. Next first-run route in the IC-0 resume enum; else `not_resumable`.

Any failure → **SUPPRESSED(reason)**: existing first-run path, no overlay, no navigation.

**Readiness:** a full-screen, non-interactive "Finishing setup…" overlay (no inputs) shown instead of first-run UI, waiting for **server acknowledgement** of the essential first-run operations IC-0 lists (profile create; seeds and onboarding flags; pending-route persistence). The marker write is **not** awaited (source gate 13: issued right after the profile create, earlier than the later first-run writes, so it is normally acknowledged first; if not, the marker alone may be lost). Local-cache resolution does not count (source gate 8). `READY_MAX` = 10 s.

**On success:** write resume record `pending` (§4.6); nonce = 128-bit `crypto.getRandomValues`, base64url; set `nm_hoff` (§4.5); set in-memory `handoffStarted`; navigate via programmatic `<a rel="noreferrer">` to `COMPLETION_URL` + `?fbclid=<snapshot fbclid>` (only if present) + `#t=<nonce>`.

**On failure or timeout:** `not_ready`: remove overlay; continue existing first-run in place; never navigate later; never retried.

Nothing in the SPA awaits Meta or the marker.

### 4.5 Binding cookie (unchanged; credited sound in v4 and v5 reviews)
Value: only the nonce.

| Target | Set by the SPA | Read at `/r/registered` |
|---|---|---|
| Production | `nm_hoff=<nonce>; Domain=numista.ai; Path=/r/; Max-Age=60; Secure; SameSite=Strict` | Yes |
| Local pair | `nm_hoff=<nonce>; Path=/r/; Max-Age=60; SameSite=Strict` (host-only `localhost`) | Yes (S-6265 §8.5) |
| `web.app` preview | host-only on the preview app host | **No** (S-PSL): preview always fails closed |

Completion-page check (any failure → no Meta, immediate `location.replace(RETURN_URL)`): (1) fragment `t` well-formed, not consumed; (2) exactly one `nm_hoff`, equal to `t`; (3) expire all four variants `Domain=numista.ai`/host-only × `/r/`/`/` with `Max-Age=0; Secure; SameSite=Strict` (local: host-only pair); (4) re-read, any `nm_hoff` → fail; (5) `history.replaceState` drops the fragment, record nonce consumed (pruned 24 h), re-check GPC; (6) only then inject Meta (§6.2).

Proves: within 60 s this browser's SPA consumed a valid snapshot whose consent was captured before the sign-up request and issued this handoff. Residuals: self-forged cookies affect only that browser; cookie tossing from another `numista.ai` host (inventory, §9); fake events sent directly to Meta; **two tabs handing off within the same 60 s overwrite the single `nm_hoff`, so both fail closed** (undercount, disclosed §13).

### 4.6 Resume record, return and Back
`nm_resume` in app-origin sessionStorage: `{v:1, phase:'pending'|'consumed', route:<enum>, step:<enum>, exp:now+10 min}`. No private data.

| Situation | Behaviour |
|---|---|
| Fresh boot, `pending`, not expired | Restore route/step once; set `consumed` (tombstone until `exp`) |
| Fresh boot, `consumed`/expired/malformed/absent | Normal signed-in boot |
| bfcache restore of original doc (`pageshow.persisted` and `handoffStarted`), `pending` | Set `consumed`; remove overlay; continue existing first-run in place; never navigate again |
| Same restore, `consumed`/expired/absent | `location.reload()` → normal signed-in boot; no first-run replay |
| Back without bfcache | Browser reload → fresh-boot rows |

Per tab, so other tabs never consume it. Completion sends `Cache-Control: no-store` and replaces its own history entry. IC-0 STOPs if a normal signed-in boot re-issues first-run creation writes non-idempotently.

### 4.7 UX changes and residuals Eric accepts at G-3
After stage B (items 2–3 for consenting new users only): (1) optional checkbox on sign-up surfaces; (2) overlay up to 10 s; (3) one extra document (≤ 4.5 s) and a cold app boot, losing in-memory state outside the resume enum. Also, from G-7a for every visitor: the address bar drops `fbclid`/`utm_*` right after landing (a bookmark or copied link lacks them). Unreachable completion host: browser error page; account and acknowledged writes intact; Back per §4.6. **Decided:** no reachability probe. Domain-cookie-rejected browsers: one fail-closed round trip. Latency evidence is synthetic smoke only.

---

## 5. Data, attribution and internal measurement

### 5.1 Landing record and URL strip
- **Capture (boot step 1):** if the URL query (or, under hash routing, the fragment's query; IC-0 confirms) has a valid `fbclid` (`[A-Za-z0-9_-]{1,512}`):
  - no record, or a record with a **different** `fbclid` → write `nm_landing` (app-origin localStorage) `{v:1, fbclid, campaign_match:<utm_campaign === META_CAMPAIGN_TAG>, captured_at:now}`;
  - record with the **identical** `fbclid` → leave the record unchanged (original `captured_at` and `campaign_match` kept; reloads and repeats never extend eligibility).
  - A landing with the tag but no valid `fbclid` records nothing. The utm value is never stored.
- **Strip (boot step 2):** remove `fbclid` and every parameter whose name starts with `utm_`, from both the query and any hash-route query, preserving path, hash route and every other parameter in order; `history.replaceState` keeps the existing history state object. Runs whether or not the values were valid. If `replaceState` throws, capture still stands and the app continues.
- **Eligible:** `now − captured_at ≤ 7 days`. **Deleted:** at consumption of a create (any decision); on expiry.
- Capture before consent follows P-6; default is first-party capture, transmitted only via the completion URL after consent.
- `META_CAMPAIGN_TAG` = `numista_tg26`, a single allowlisted build constant, exact and case-sensitive.
- Capture and strip run only when `MARKER_ENABLED` or the handoff flag is ON; stop (c) sets both OFF and so disables them too.

### 5.2 Click-attribution criterion (Pixel)
Before stage B, the stage A HAR must show for each synthetic sign-up with a test `fbclid` a `CompleteRegistration` request whose `fbc` (or documented equivalent) contains it (plus source gate 5 text once archived). This proves the click ID is carried, not that Meta credits the campaign; `_fbc` time is completion time. If it fails, no widening until Eric chooses in writing: (a) count-only; (b) reviewed amendment; (c) tester-only, then stop (b).

### 5.3 Acquisition marker document (measure of record; best-effort; decoupled)
**Reuse first.** If IC-0 finds an existing server-side per-account acquisition record that already expresses this Boolean without raw IDs and without touching profile writes, it is reused by amendment.

**Otherwise (future, unimplemented):** collection `acq_meta`, document id = the new account's uid, exactly one key `meta_click` (Boolean). IC-0 confirms the collection name is unused.

**Value:**
- Campaign mode (default): `meta_click = true` iff the consumed snapshot's `campaign === true`: the browser's **most recent `fbclid` landing** (later landings without `fbclid` do not change it) carried exact `utm_campaign=numista_tg26` and was ≤ 7 days old at sign-up start. Otherwise `false`.
- Meaning, honestly: same-browser, last-`fbclid`-landing heuristic; includes shares of the ad URL and shared-device carry-over; excludes cross-device and older clicks; **not** proof of ad attribution.
- Referral mode (only if Eric declines the tag at G-3, or P-9(i) is unconfirmed at G-7a): `campaign` = any eligible `fbclid`; metric named "Meta-referred sign-ups (ad or organic)" everywhere. Mode is a build constant recorded in the G-7a receipt; never mixed within a window or changed during the freeze. If an ad launches without the tag in campaign mode, M-A carries the caveat that its clicks are not counted.
- P-6 consent variant: `true` also requires `consent === true`; metric prefixed "consenting".

**Write behaviour (all plan, none implemented):**
- Issued once, only after the existing **profile create succeeds**, only when `MARKER_ENABLED` and a valid snapshot was consumed. A plain create of `acq_meta/{uid}` with `{meta_click}`; never a merge, never an update, never retried later, never backfilled.
- **Fire-and-forget:** not awaited by sign-up, first-run, readiness or navigation; every error (denied, offline, timeout, quota, missing rules block) is caught and dropped; no UI, no retry loop. Offline: the SDK may queue it; if the tab closes first it is lost.
- Profile create fails → no marker write (the account may exist in Auth without profile; counted in M-U0).
- Missing/invalid snapshot → **no** marker document (unknown is not written as `false`).

**Rules block (pseudocode; additive, separate `match`; the profile rules and every other existing byte are untouched):**
```text
match /acq_meta/{uid} {
  allow create: if request.auth != null && request.auth.uid == uid
                && request.resource.data.keys().hasOnly(['meta_click'])
                && request.resource.data.meta_click is bool;
  allow get:    if request.auth != null && request.auth.uid == uid;
  allow list, update: if false;
  allow delete: if request.auth != null && request.auth.uid == uid;
}
```
- **Create:** owner only, one Boolean key. **Read:** owner `get` only; no `list`. **Update:** never (a second create on an existing doc is an update, so denied and dropped). **Delete:** owner only, so account-deletion and data requests can remove it; a deleted marker only makes that account unmarked. Operators read through existing admin access (rules do not apply to it).
- IC-0 checks for any existing broader `match` (e.g., recursive wildcards) that would also grant writes here. If one exists, the immutability above is not enforced (recorded; acceptable because the marker is client-asserted measurement), and nothing else changes.
- **Availability property:** the profile document, profile rules and profile writes are unchanged. Therefore an old cached client, another plan's app or rules deploy, a rules set lacking this block, or this plan's own rollback can only stop marker writes (default deny → dropped), never sign-up or profile reads/writes (T-8h, T-24).

**Account deletion:** IC-0 records the existing deletion path. If it is client code in this tree, the G-3 implementation adds an owner delete of `acq_meta/{uid}` to it (this plan's files only). If it is server-side or elsewhere, the orphan-marker handling is a P-6 counsel item; this plan adds no server code.

**Aggregate read:** via the existing admin/console path IC-0 confirms; if none, a read-only aggregate query run by the §8.3 operator with existing admin access under the G-7a YES, joining Firebase Auth creation times with `acq_meta` and profile existence; outputs counts only; synthetic exclusion inside the query; no uid export; no deployed component.

**Privacy:** first-party; never sent to Meta; disclosed (P-7).

### 5.4 Measurement definitions
Window: 26 Nov 00:00:00 – 2 Dec 23:59:59 in the P-9 time zone (default America/New_York). "Created" = Firebase Auth creation time. Population **W** = non-synthetic Auth accounts created in the window. Synthetic = every uid in G-6, G-7a, G-7b and daily-canary receipts.

| ID | Metric | Definition | Use |
|---|---|---|---|
| M-A | Campaign-tagged sign-ups (**record**) | accounts in W with `acq_meta/{uid}.meta_click == true` | count; a floor (unmarked accounts are not counted) |
| M-A% | Share of marker-written accounts | M-A ÷ accounts in W with any `acq_meta` doc | under the P-6 variant labelled "consenting campaign-tagged sign-ups as a share of all marker-written accounts (denominator includes non-consenting)" |
| M-U | Unmarked accounts | accounts in W with no `acq_meta` doc | **context, not a must-be-0 alarm** (expected populations below) |
| M-U0 | Auth without profile | accounts in W with no profile document (subset view) | context; an existing failure class this plan does not cause |
| M-B | Meta-reported `CompleteRegistration` | Events Manager total in window | different population; reported with synthetic bound (§8.3) |
| M-C | Meta-attributed results | Ads Manager | Meta's figure, unverified |

**Expected M-U populations:** accounts created by builds without the marker (service-worker-cached old builds; IC-0 records the caching strategy, source gate 15); other account-creation clients IC-0 inventories (e.g., native, admin, scripts); Auth created but profile create failed or the client saw an error/closed (M-U0); snapshot missing (storage blocked, redirect storage lost); marker write denied, dropped or lost offline; markers deleted by owners; foreign app/rules deploys that dropped the feature.
**Grace:** for 72 h after any app deploy (this plan's or, when known, another's), unmarked web accounts from cached builds are expected.
**Investigation cue (not automatic stop):** outside grace, a day where M-U ≥ 20% of that day's W with W ≥ 10 accounts, or any canary without its marker doc → compare live app/rules with the latest baseline receipt (§6.5). **No ratio is ever computed between M-B and M-A/M-A%.** A zero-Meta day is not an alarm.

### 5.5 What goes where (truthful privacy statement)
**Meta never receives from this plan:** email, name, phone, address, uid, collection data or values, NAC/cert numbers, photo URLs, receipts, estate/AJ data, Stripe IDs, form values, utm values. Meta receives: IP and user agent; Meta cookies; the completion URL `/r/registered[?fbclid=…]` without fragment; no referrer; `autoConfig` boolean `false`; `init` without matching parameters; AAM OFF (P-4).

**Numista servers:**
- **Unchanged existing flows:** Firebase Auth and the existing profile and app data (including email and uid) continue to flow to Firebase exactly as today. This plan neither adds to nor removes them.
- **Necessarily reach Numista Hosting:** the initial landing request (`numista.ai/…?fbclid=…&utm_…`) and the completion request (`go.numista.ai/r/registered?fbclid=…`). Hosting/Cloud request logs may record these query strings; IC-0 records whether request logging is on and its retention (source gate 14). The app cannot prevent this.
- **New from this plan:** one `acq_meta/{uid}` document holding one Boolean.
- **Not added:** no app code writes raw `fbclid` or utm values to Firestore, Functions, Storage or any app telemetry; no new analytics storage. The landing record and snapshot are browser-local.
- **Minimisation control (source-gated):** the URL strip removes these parameters from the address bar before Auth initialisation, the redirect and later navigation. Whether every URL-reading SDK runs after the strip is an IC-0 finding (§9); any SDK that records or forwards the page URL before the strip, or any app telemetry that records it, means STOP and amend.

---

## 6. Completion site, constants, CSP, stops, composition

### 6.1 Per-target constants (build time only)
| Target | SPA `COMPLETION_URL` | Completion `RETURN_URL` | Dataset | Completion mode | `MARKER_ENABLED` | Backend |
|---|---|---|---|---|---|---|
| local | `http://localhost:<c>/r/registered` | `http://localhost:<a>/` | test | Pixel | ON | Emulators only (Auth + Firestore with the proposed rules); STOP if unsupported |
| preview | paired preview completion URL | paired preview app URL only | none | no-Pixel | **OFF** | Production project (S-FBMS); synthetic uids receipted |
| production | `https://go.numista.ai/r/registered` | `https://numista.ai/` | prod | no-Pixel (G-4/G-7a); Pixel (G-7b) | ON (OFF = stop c) | Production |

Also: handoff flag, `CANARY_ONLY`, `MARKER_MODE`, `META_CAMPAIGN_TAG='numista_tg26'`.

**Preview coverage (explicit):** preview binding always fails closed (§4.5), so preview validates only SUPPRESSED paths, overlay → completion → **binding fail** → return, URL strip and zero Meta. The full success path (binding pass, return, resume, Back) is exercised only locally (emulators) and at G-7a on production with testers. G-6 preview is not evidence for it.

**T-4 build assertions:** local/preview contain no production dataset, `numista.ai`, `go.numista.ai`; production contains no `web.app`, `firebaseapp.com`, `localhost`; preview has `MARKER_ENABLED=false`; each completion build has exactly one `RETURN_URL` (in `location.replace`, meta refresh `5;url=…`, Continue link); exactly one `nm_meta_canary` check active only under `CANARY_ONLY=true`; exactly one tag constant.

### 6.2 Completion page (Pixel mode)
1. Run §4.5.
2. Inject base code (S-GS): `fbq('set', 'autoConfig', false, ID)`; `fbq('dataProcessingOptions', <P-6>)`; `fbq('init', ID)` (no third argument). No PageView, revoke/grant pair or `<noscript>`.
3. After script `load` only: `fbq('trackSingle', ID, 'CompleteRegistration')`. `T_LOAD` 3000 ms; error/block → nothing sent.
4. `T_FLUSH` 1000 ms → `location.replace(RETURN_URL)`; hard cap 4500 ms; meta refresh 5 s.
No-Pixel mode runs §4.5 and returns. At most one locally authorized attempt; receipt not guaranteed; no retry, queue or dedup claim.

### 6.3 CSP
App unchanged (no Meta/completion tokens; RP3 untouched). Completion (T-10):
```text
default-src 'none'; script-src 'self' https://connect.facebook.net;
img-src https://www.facebook.com; connect-src https://www.facebook.com;
base-uri 'none'; form-action 'none'; frame-ancestors 'none'
```
Plus `Referrer-Policy: no-referrer`, `Cache-Control: no-store`. `connect-src` provisional. No-Pixel and placeholder builds: same minus Meta hosts.

### 6.4 Stop and rollback paths
Each runs under the G-7a/G-7b YES that names it; none is a new permission; none waits for a review. None is instant.

| Path | Mechanism | Composition check | Effect |
|---|---|---|---|
| (b) **Pixel kill** | Deploy the reviewed no-Pixel completion build (`--only hosting:<completion>`) | **Completion site only:** live completion release vs this plan's last completion receipt. Mismatch is recorded, and the kill still deploys (removing Meta is always the safe direction; no other plan deploys this site) | New loads run no Meta; pages inside their 4.5 s window unaffected; CDN cache applies. Never blocked by app or rules drift |
| (a) Handoff off | New commit = the **actual current live app commit** + exactly one constant change (handoff flag → false); `--only hosting:<app>` | Diff vs the actual live commit must be exactly that constant (mechanical, receipted). Unrelated live changes from any plan are preserved. If the live build does not contain this feature, nothing to stop (recorded). If the live commit cannot be identified, record and rely on (b); no history rewrite | Marker continues; open tabs continue until reload |
| (c) Marker off (also disables capture, strip and handoff) | Same as (a) but exactly two constants: `MARKER_ENABLED` → false and handoff flag → false | Same mechanical diff check (exactly those two constants) | No more marker writes; sign-up and profiles unaffected; verified by one synthetic sign-up plus one ordinary profile edit |
| Rules block removal | Not a stop; never needed for safety | Full composition gate (non-stop) | Leaving the additive block is harmless; removal later only denies marker writes. **Order: app before rules, always** |
| (d) Site disable/deletion | After (a) plus drain; deletion permanent (S-FBMS) | — | Last resort |
| (e) Meta-side controls | Effects unverified | — | Browsers may still send |

Stops never rebase or rewrite history, never force-push, never touch main; each creates a new commit and a receipt.

### 6.5 Composition and deploy provenance (this plan's own deploys only)
**Completion config:** separate config/directory preferred; main `firebase.json` untouched (if array form is used, main block byte-identical, T-11). If this lands before RP3, RP3's own IC-0 must STOP for a composed baseline.
**G-4:** fixed-bytes placeholder (redirect to `https://numista.ai/` + no-Meta policy), receipted.

**Non-stop deploys** (G-7a, marker-only G-7a, stage A, stage B, any later feature change) are **composition-gated:**
1. The target's live release (app and rules for app/rules deploys; completion only for completion deploys) matches the latest `LIVE_BASELINE` receipt (before the first: the IC-0 live baseline, incl. RP3/Images/Catalog if live). Mismatch → STOP, re-base, re-diff, re-review under the same gate.
2. Exact recorded feature-branch commit on that baseline; diff only this plan's files; rules diff = only the appended `acq_meta` block.
3. `--only hosting:<target>` or `--only firestore:rules`; never bare `--only hosting`.
4. Order: G-7a rules → completion (no-Pixel) → app; marker-only rules → app; stage A completion; stage B app.
5. New immutable receipt `LIVE_BASELINE_<n>.md` after each deploy (app commit, rules hash, completion commit).

**Stops** follow §6.4 instead and are never blocked by this gate.

**Future coordination (recorded, not enacted):** while unmerged, production runs bytes not on main. Another plan's non-composed app or rules deploy can drop the checkbox, handoff or marker writes. Because the marker is decoupled (§5.3), the worst case is lost measurement or handoff, **never** an account-availability or profile-write failure. The receipts exist for other plans' existing baseline checks; this plan sets no policy for them. Merging is outside this plan.

**Deploy freeze 26 Nov – 2 Dec:** no non-stop deploy of this plan. A feature lost to a foreign deploy during the window is not restored in the window (gap reported).

---

## 7. Disclosure (P-7; counsel and Eric)
The privacy text must: name Meta as a recipient of IP, browser data, cookies, the completion URL (incl. any `fbclid`) and the event; state Meta cookies may be scoped to `numista.ai` (T-13); describe the landing record, the URL clean-up and the first-party `acq_meta` marker; state that Numista's hosting may log landing/completion URLs containing click IDs (per IC-0 retention); state revocation does not delete Meta cookies or data; make no anonymity or "no personal data" claims. It may state that collection contents, values, photos, certification numbers, names, emails and addresses are not sent to Meta. Meta cookies are not cleared on revocation.

**Meta cookie scope.** If T-13 shows `.numista.ai` scope, stage B requires (i) the stage-B re-inventory (§9) shows no reader transmitting `_fb*` off-origin, or each is excluded by amendment, and (ii) Eric's written acceptance under the G-7b YES. Otherwise no widening.

---

## 8. Production sequence (fail-closed; real users never see the Pixel before stage A passes)
Synthetic runs use production accounts; uids in receipts; excluded from §5.4. **Synthetic accounts are left intact; deleting any is a separate destructive action needing its own approval.** "Added latency" = overlay shown → first-run route rendered in the return document (upper bound). Thresholds over a few runs are **smoke maxima, not population percentiles.**

### 8.1 G-7a (production; no Pixel; handoff tester-only)
Rules (append `acq_meta` block) → completion (no-Pixel) → app (`MARKER_ENABLED`, handoff ON, `CANARY_ONLY=true`). Real users get only the URL strip and the best-effort marker (plus the checkbox if P-6 requires marker consent). Fresh browser profile per run unless stated; canary runs set `nm_meta_canary='1'`; "campaign landing" = test `fbclid` + `utm_campaign=numista_tg26` + one unrelated parameter and a deep route.

| # | Device | Case | Handoff | `acq_meta` |
|---|---|---|---|---|
| 1 | desktop | Email, consent on, campaign landing; then one ordinary profile edit | yes | true |
| 2 | desktop | Email, consent on, no landing; then one ordinary profile edit | yes | false |
| 3 | desktop | Popup new, consent on, campaign landing | yes | true |
| 4 | mobile | Redirect new, consent on, campaign landing | yes | true |
| 5 | desktop | Email, consent off, campaign landing | no | true (false under P-6 variant) |
| 6 | desktop | GPC on (checkbox hidden), no landing | no | false |
| 7 | desktop | Email, consent on; Back from completion before return | `pending` row | false |
| 8 | desktop | Email, consent on; after return, Back | `consumed` row → reload, no replay | false |
| 9 | mobile | Redirect new, unticked at click, ticked after return | no | false |
| 10 | desktop, run-1 profile | Second new account, box unticked, no new landing | no; box unchecked | false |
| 11 | desktop | Email, consent on, `fbclid` landing without tag; re-open the same original landing URL twice before sign-up | yes | false; `captured_at` unchanged by the repeats |

**Pass:** all 11 match; every essential first-run document exists; profile edits in 1–2 succeed; marker docs exactly as expected and one per run; address bar after boot lacks `fbclid`/`utm_*` while the deep route and unrelated parameter survive; no duplicate first-run (7, 8); `nm_hoff` set/removed per HAR and cookie listing; **zero Meta requests** in every HAR; added latency max ≤ 8 s on handoff runs (desktop and mobile listed separately); no `not_ready`.
**On fail:** handoff defect → stop (a); marker or URL-strip/capture defect → stop (c) (which also turns capture and strip off, §5.1). G-7b does not start.

### 8.2 G-7b stage A (production Pixel, tester-only)
Immediately before: stage-A re-inventory (§9). Deploy completion in Pixel mode (production dataset); app unchanged (`CANARY_ONLY=true`). Exactly 6 canary, consenting synthetic sign-ups, timestamps receipted:

| # | Device | Case | `acq_meta` |
|---|---|---|---|
| 1 | desktop | Email, campaign landing (`fbclid` A) | true |
| 2 | mobile | Email, campaign landing (B) | true |
| 3 | desktop | Email, `fbclid` C without tag | false |
| 4 | desktop | Popup, campaign landing (D) | true |
| 5 | mobile | Redirect, campaign landing (E) | true |
| 6 | desktop | Email, no landing | false |

- **HAR (emitted):** exactly 6 `/tr` `CompleteRegistration` requests, one per run; no other Meta event, PageView, `ud[`/`udff[`, metadata; `dl` without fragment; `nm_hoff` gone before `fbevents`; `fbc` carries A–E for runs 1–5 (§5.2).
- **Events Manager (received k):** evaluated **no earlier than +2 h and finally at +24 h** after the last run (source gate 1); counts by receipted time range; no per-browser trace claimed. k = 6 passes this item; k > 6 fail-and-investigate; k < 6 at +24 h fail-and-investigate, with at most one rerun per missed case when the HAR records a local non-design reason (rerun k evaluated the same way); still missing → fail.
- Also: no CSP violations; T-13 scope recorded and §7 satisfied; §5.2 met or Eric's written choice; P-3, P-4, P-5, P-7, P-9(ii) done.
**On fail:** stop (b); no widening.

### 8.3 G-7b stage B (widen; same YES) and campaign watch
- Immediately before: stage-B re-inventory (§9). Only if stage A passed and stage B completes by **25 Nov 23:59 ET**: app redeploy (composition-gated) with `CANARY_ONLY=false`. Otherwise the Pixel stays tester-only for the window.
- **Operator and cadence:** the operator named in the G-7a receipt (Eric or the person he designates, using existing admin access only). Daily at about 9:00 AM ET, from the day after G-7a through 3 Dec: run the read-only count query (M-A, M-A%, M-U, M-U0 for the previous day and window-to-date) and, from 25 Nov through 2 Dec, two canary-marked consenting synthetic sign-ups (desktop email + campaign landing; mobile cellular Google redirect, no landing). Canary checks: account and essential first-run docs; one ordinary profile edit succeeds; marker doc correct; clean address bar; right route; HAR shows exactly one `CompleteRegistration` per run and nothing else (Pixel off or marker-only: zero Meta); latency recorded.
- **Blind spots stated, not assumed away:** between daily checks nothing is observed; up to about a day of lost markers or broken handoffs can go unseen. This is proportionate only because this plan's design cannot cause profile-write or sign-up failures (§5.3); it does **not** assert that sign-up is healthy between checks, and outages from other causes are outside this plan's detection.
- **Synthetic accounting:** HAR-emitted canary count N per period is receipted. Observed canary events are subtracted from M-B only where source gate 1 shows them individually, and only for ranges overlapping the receipted times; otherwise M-B is reported with real events in [total − N, total].
- **Real-user stranding and latency are not observable** (no new telemetry). Protection: canaries; if IC-0 finds an existing onboarding-completion field, a read-only share comparison (pre- vs post-widening days, ≥ 30 accounts each side, else "insufficient"); support channels.
- **Triggers:** canary handoff failure, missing return, `not_ready`, or latency > 8 s → stop (a). Canary marker missing/wrong → investigate composition; stop (c) only if this plan's marker code is at fault. Onboarding share down ≥ 10 pp (when evaluable) or a credible stranding report → stop (a). Any Meta request from the SPA, a PII parameter, or unexpected events → stop (b). M-U alone is a §5.4 investigation cue, not a stop.

### 8.4 Timeline and marker-only fallback
- Targets: G-7a by 20 Nov; stage A by 23 Nov (k final by 24 Nov); stage B by 25 Nov.
- **Marker-only fallback:** if G-4 or the preview part of G-6 is not done by 20 Nov, G-7a deploys the same commit with the handoff OFF and no completion deploy: rules → app. Needs G-5 and the local part of G-6 (T-22, T-24 on emulators). Production checks under the G-7a YES: landings of runs 1, 4, 5, 11 (no checkbox, so no consent), handoff "no" for all, markers true, true, true, false, profile edit succeeds, clean address bar, zero Meta. Pixel off for the campaign.
- If even marker-only cannot deploy by 24 Nov: no marker for the campaign; reporting is M-C only, labelled.

---

## 9. IC-0: future read-only verification (hashed receipt; drift → STOP and amend)
**Full IC-0:** before G-3, re-run before G-7a.
- Record: current commit/tree; live app and rules baseline (commit, hash); hosting config; app CSP; Meta presence; URL strategy; service-worker caching strategy (source gate 15); Hosting/Cloud request-log setting and retention (source gate 14).
- Sign-up: call sites; which Google mode runs where; success points; the single redirect consumer; **every account-creation client** (web builds, native, admin tools, scripts).
- First-run: operations and ack semantics; resume enum; profile create success point; whether a normal signed-in boot re-issues first-run writes non-idempotently (STOP).
- Marker: `acq_meta` name unused; existing rules matches overlapping `acq_meta/{uid}` (recorded); existing acquisition record, consent UI, onboarding-completion field, admin aggregate path; account-deletion path.
- **URL readers:** every script/SDK and app telemetry that reads or records `location`/page URL (error reporting, analytics, support widgets, Flutter bootstrap), and whether each runs before boot step 2. STOP if any records or forwards the URL before the strip, or if app telemetry records URLs containing the stripped parameters.
- Cookies/hosts: every `Domain=numista.ai` cookie (STOP if any carries auth/uid/session/account data or is non-HttpOnly sensitive); every `numista.ai` host (STOP if untrusted script); every cookie reader (app, SDKs, Hosting rewrites; source gate 10).
- Flag mechanism; emulator support; `/r/` unused on the app site.
- Archive source gates 1–15 where possible.

**Re-inventories (read-only subset, same receipt format), immediately before stage A and again before stage B:** parent-domain cookies, `numista.ai` hosts, cookie readers and URL readers, since Meta's script first runs at stage A and real users first meet it at stage B. Any new finding → no deploy of that stage until amended.

---

## 10. Test contracts (future; none run)
G-5 = T-1–T-12, T-23. G-6 = T-13–T-22, T-24 where applicable (preview limited per §6.1). §8 tables are production contracts.

| ID | Contract |
|---|---|
| T-1 | Static: no `fbq`/`fbevents`/`connect.facebook.net`/`facebook.com/tr` in the SPA; completion `autoConfig` literal boolean `false`. |
| T-2 | Handoff OFF/empty constants → no handoff, no checkbox (unless P-6), marker still written; `MARKER_ENABLED` OFF → no `acq_meta` write and sign-up behaviour identical. |
| T-3 | §4.3 trigger table; spy proves one redirect consumer. |
| T-4 | Checkbox unchecked on open, never pre-filled, hidden under GPC; snapshot consent = checkbox at click; later ticks ignored; probe failure → `cookie_probe`; canary gating; §6.1 build assertions incl. preview `MARKER_ENABLED=false`. |
| T-5 | Attempt-id guard: same id twice, reload, duplicated tab → ≤ 1 handoff; no uid stored locally. |
| T-6 | Landing: different `fbclid` overwrites; identical `fbclid` keeps original `captured_at`/`campaign_match`; exact tag only (case/prefix/suffix/list → false); tag without `fbclid` → nothing; 7-day expiry; deleted at create. Strip: after boot the URL has no `fbclid`/`utm_*` in query or hash query, path/hash route/other parameters preserved in order, history state kept; strip runs before Auth init and the redirect consumer; `replaceState` failure tolerated. No app code path writes raw `fbclid`/utm to Firestore, Functions, Storage or telemetry (static + spy). Completion URL has only `fbclid`, only with consent. Nonce random. |
| T-7 | `rel=noreferrer`. |
| T-8 | (a) no `await` on Meta or marker; (b) flag ON vs OFF: identical account state, essential first-run writes, post-return route; (c) delayed essential write → `not_ready`, no later navigation; non-enum → `not_resumable`; (d) overlay has no inputs; (e) unreachable host → error page, Back → `pending` row; (f) Back after return → `consumed` → reload; (g) other tab never consumes `nm_resume`; **(h) marker write denied / rules block absent / offline / hanging / throwing → sign-up, readiness timing, first-run and later profile create, read and edit (merge and non-merge) all unaffected.** |
| T-9 | Builds without `ENABLED`/`ID` → no-Pixel page; placeholder bytes match receipt. |
| T-10 | Completion CSP/headers per §6.3; no inline script. |
| T-11 | Main hosting block, app headers and the live rules baseline byte-identical apart from the appended `acq_meta` block; **no profile rule change.** |
| T-12 | Empty `document.referrer` on completion; no `Referer` on Meta requests. |
| T-13 | Real-host cookie listing with Domain scope; only `nm_hoff` from the app on `go.`, gone before Meta loads; `_fbp`/`_fbc` scope vs re-inventory. |
| T-14 | Signed-in reloads, demo/guest, signed-out: zero Meta. |
| T-15 | Local (gate 6) and stage A: one event per consenting new account; no fragment in `dl`; no `ud`/`udff`/PageView/metadata; §5.2. |
| T-16 | Popup new = 1; redirect new = 1; returning = 0; ticked only after return = 0. |
| T-17 | Delivery smoke: HAR emitted 6; k per §8.2 timing rules. |
| T-18 | Binding failures each → 0 + immediate return: no cookie; wrong nonce; > 60 s; reused; reload; Back; `web.app`; two `nm_hoff` (incl. two tabs within 60 s → both 0); ineffective deletion. `nm_hoff` gone before `fbevents`. |
| T-19 | Ad blocker/CSP block → nothing sent, return ≤ 4.5 s; no-JS → refresh at 5 s. |
| T-20 | Reasons: `flag`, `canary`, `attempt`, `consent`, `gpc`, `guard`, `cookie_probe`, `not_new`, `not_ready`, `not_resumable`, `binding`, `load_timeout`, `blocked`, `sent`. |
| T-21 | Stops per §6.4: (b) proceeds despite app/rules drift; diff vs the actual live commit is exactly one constant for (a) and exactly two for (c); unrelated live changes preserved; open tabs documented; app before rules. |
| T-22 | Marker doc per §5.3 across email/popup/redirect, both modes: written only after profile create success; never awaited; missing snapshot → no doc; profile create failure → no doc; one doc per account. Emulators only. |
| T-23 | Snapshot table (§4.2): written after validation, before the auth call; consumed once; deleted on error/cancel/sign-in/abandoned redirect/boot; validation failure writes nothing; expired/malformed/mismatch → SUPPRESSED, no doc; storage throwing → sign-up proceeds; no uid/email/utm inside. |
| T-24 | Rules (emulator): `acq_meta` owner create with exactly one bool → allowed; extra key, non-bool, other uid, unauthenticated → denied; update/second create → denied; owner delete → allowed; owner get → allowed; list → denied. Profile rules unchanged; every profile operation of the current, a marker-less and a rollback build passes with and without the block. Count query on seeded emulator data (Auth with profile+marker, without marker, without profile; synthetic) yields M-A, M-A%, M-U, M-U0 exactly. |

---

## 11. Decisions and defaults
**Fixed:** separate test dataset; no probe; 7-day eligibility; tag `numista_tg26` exact; identical-`fbclid` keeps original time; strip all `utm_*` and `fbclid`; marker in its own create-only doc, best-effort, never awaited, no backfill; unknown snapshot → no doc; owner may delete marker; no staging; no Meta cookie clearing; separate completion config preferred; anonymous upgrade and post-request consent never count; G-7a before G-7b; no widening after 25 Nov; freeze in window except stops; synthetic accounts left intact; no M-B/M-A ratio; preview `MARKER_ENABLED=false`.
**Remaining decisions at existing gates:** G-3: §4.7/§13 acceptance, marker mode, P-6 (incl. retention/deletion). G-4: P-8. G-6: local-only scope or not. G-7a: P-9(i); operator named; stops (a)–(c) listed in the YES. G-7b: P-7, P-9(ii); stops listed; §5.2 choice only on failure; §7 acceptance only if scope is `.numista.ai`.

## 12. Security preservation
**App:** no third-party script; no CSP change; no profile-document or profile-rule change. New browser storage: localStorage `nm_landing`, `nm_attempt_used` (ids only), `nm_meta_canary` (tester-set); sessionStorage `nm_attempt`, `nm_resume`. Cookies: transient `nm_probe`, `nm_hoff`; possibly Meta `_fbp`/`_fbc` at `.numista.ai` (§7). New server data: `acq_meta/{uid}` with one Boolean. Rules: one appended `match` block.
**Unchanged:** main-site hosting; RP3; owner-storage guard; Stripe OFF; existing Auth/profile data flows. The completion site has no Firebase, keys or Auth.

## 13. Residuals and trade-offs (candid)
- The marker is a same-browser, last-`fbclid`-landing, 7-day heuristic: misses cross-device/older clicks, storage-blocked browsers, lost redirect storage, dropped best-effort writes, owner deletions and old cached builds; includes shared-device carry-over, ad-URL shares and self-forged values. M-A is a floor; M-U shows the unmarked remainder without explaining it.
- Referral mode, if chosen, cannot separate ad from organic Meta traffic.
- M-B and M-A are different populations and never compared; M-C is unverified.
- Landing and completion URLs with click IDs necessarily reach Numista Hosting and may sit in request logs for the configured retention.
- Real-user stranding and latency are unobservable; detection of lost markers or handoffs is daily, not continuous.
- Delivery to Meta is not guaranteed; stage A k < 6 can block widening even when the design is right.
- Two tabs handing off within 60 s both fail closed (undercount).
- Another plan's non-composed deploy can silently remove the feature; it cannot break sign-up or profiles. Features lost during the freeze are not restored in the window.
- A pre-existing broad rules wildcard (if IC-0 finds one) leaves the marker mutable by its owner.
- Synthetic production accounts (about 11 + 6 + 16 + reruns) remain.
- The handoff machinery is heavier than the lean marker-only core; Eric may choose marker-only at G-7a by declining the handoff (a business trade-off; no question needed now).
````

=== END FILE A-verbatim ===

---

## FILE B — `CLOSURE_MAP_v6.md` (closure map v6)
SHA-256 `6dd1ea01f1d2af376c1db92fd88941cb2b0a84496b2cfda979b9060d4658c0da` · 6938 bytes

````markdown
# v5 to v6 closure map (CoS v5: 94 REVISE incl. critical B1; gate record `cos-review/v5/COS_GATE_DISPOSITION.md`, 11:07:59 AM EST)

Replacement writer try 2 = global attempt 6 of 10. Not self-scored. Refs are to `PLAN_META_PIXEL_SIGNUP_ATTRIBUTION_v6.md`. Everything described is future, unimplemented plan text; every test is a future contract; nothing ran.

## A. v5 review findings
| v5 finding | v6 integrated closure | Contracts |
|---|---|---|
| **B1** (critical) profile-field marker couples measurement to profile writes; update rule denies non-merge overwrites; allowlist case only disclosed; rollback verified creates only; M-U blind to failed creates | Profile field and **every profile-rule change removed** (§0, §5.3, §12). Marker = separate `acq_meta/{uid}` doc with its own appended `match` block: owner create of exactly one Boolean; owner `get`; no `list`; no update; owner delete (account deletion/data requests). Written once, only **after the existing profile create succeeds**, fire-and-forget, never awaited, errors dropped, never retried or backfilled; missing snapshot → no doc. Availability property stated: old/cached clients, foreign app/rules deploys, a ruleset lacking the block and this plan's rollback can only stop marker writes. M-U redefined over **Auth-created** accounts with no marker doc; M-U0 = Auth without profile; expected populations, 72 h cached-build grace and other creation clients (IC-0 inventory) stated; investigation cue, not must-be-0 (§5.4). Rollback (c) verified with a sign-up **and** a profile edit (§6.4); G-7a runs 1–2 and daily canaries include a profile edit. | T-8h, T-11, T-22, T-24, §8.1 |
| **B2** composition STOP blocks stops; slow detection | §6.4: Pixel kill (b) checks only the completion site's own baseline and deploys even on mismatch (removing Meta is the safe direction; no other plan deploys that site). Stops (a)/(c) = actual live app commit + exactly one/two constants, mechanical diff receipt, unrelated live changes preserved, no review wait, no history rewrite, under the G-7a/G-7b YES that lists them by name (not self-permission). Non-stop deploys stay fully composition-gated (§6.5). §8.3 names operator (from the G-7a receipt, existing access only) and daily ~9 AM ET cadence for counts and canaries; blind spots between checks stated without assuming no outage. | T-21 |
| **B3** raw `fbclid`/utm stay in URL; false "never reaches Numista servers"; re-capture refreshes time | §4.0 exact boot order: capture → `replaceState` strip (`fbclid`, all `utm_*`, query and hash-query; path, route and other params preserved) → Auth init → redirect consumer; redirect therefore starts and returns on a clean URL. Identical `fbclid` keeps original `captured_at` (§5.1). §5.5 rewritten: landing and completion requests necessarily reach Numista Hosting and may be logged (source gate 14, IC-0 records retention); only claim is that no app code writes raw IDs to Firestore/Functions/Storage/telemetry and no new analytics storage; existing Firebase Auth/profile flows (email, uid) explicitly unchanged rather than denied. IC-0 URL-reader inventory with STOP (§9). §7 discloses logging and URL clean-up. | T-6, §8.1 |
| **N-A.1** cookie re-inventory timing | §9 read-only re-inventory (cookies, hosts, cookie readers, URL readers) immediately before stage A and again before stage B; §8.2/§8.3 call it. | T-13 |
| **N-A.2** preview marker | §6.1 preview `MARKER_ENABLED=OFF`; T-4 asserts. | T-4 |
| **N-A.3** preview success path | §6.1 "Preview coverage": preview validates only fail-closed paths; full success path only local and G-7a tester production. | — |
| **N-A.4** T-24/T-6 contradictions | T-6 and T-24 rewritten to the v6 design; T-11 now "no profile rule change". | T-6, T-24, T-11 |
| **N-B.1** M-U false alarms | §5.4 expected populations, grace, other clients, context-only cue. | T-24 |
| **N-B.2** wording / consent denominator | §5.3 "most recent `fbclid` landing (later landings without `fbclid` do not change it)"; §5.4 M-A% consent-variant label. | — |
| **N-B.3** k evaluation delay | §8.2 k evaluated no earlier than +2 h, final at +24 h (source gate 1). | T-17 |
| **N-B.4** two tabs within 60 s | §4.5 residual, §13, T-18. | T-18 |
| **N-B.5** leftover snapshot on validation failure | §4.0/§4.2: snapshot written only after client-side validation passes. | T-23 |

## B. New independent findings by this writer (Y), from re-running lifecycle, deploy, rollback and metrics against the separate-doc design
| ID | Finding | Closure |
|---|---|---|
| Y1 | Writing `false` when the snapshot is missing would hide losses inside the M-A% denominator | No doc on unknown; counted in M-U (§5.3, §4.0 redirect 6) |
| Y2 | A create-only, no-delete marker would orphan uid-keyed data after account deletion | Owner delete allowed; IC-0 deletion path; P-6 handles server-side cases (§5.3) |
| Y3 | An existing broad rules wildcard could also grant writes to the new path | IC-0 records it; only immutability weakens, never availability (§5.3, §13) |
| Y4 | Strip must precede the Google redirect so the redirect never carries the IDs | Exact boot order §4.0; T-6 |
| Y5 | Stop (c) must also disable capture/strip, or a strip defect has no stop | Capture/strip gated by the same constants; (c) flips two constants (§5.1, §6.4) |
| Y6 | Not awaiting the marker means it can be lost at handoff navigation | Issued before later first-run writes; loss affects measurement only (source gate 13) |
| Y7 | Re-capture test was impossible once the URL is stripped | G-7a run 11 re-opens the original landing URL (§8.1) |
| Y8 | Stop authority must be explicit to avoid self-permission | G-7a/G-7b YES requests list stops (a)–(c) by name (gate table) |

## C. Preserved from v5 (credited sound by the v5 review)
Email/popup/redirect lifecycle and snapshot rules; GPC handling; readiness; pending/consumed resume; tab scoping; attempt-id guard; at-most-once per consenting new account; binding cookie; Meta SDK order and CSP; exact-tag measurement with no M-B/M-A ratio; emitted-vs-received accounting; marker-only fallback; no new approval layers (G-1–G-7b unchanged).

## D. Inherited attempt ledger
v1 87, v2 91, v3 92, v4 92 (original writer, retired). v5 94 (replacement try 1, global 5). v6 = replacement try 2 = global 6 of 10. Replacement still failing after try 4 (v8) → another writer; no success by 10 total → notify Eric and split. Reviews/mirrors add zero.

## E. Open source and business gates (future)
Source gates 1–15 (§1; new: 13 write-ack order, 14 Hosting request logs, 15 service-worker caching). IC-0 and the stage A/B re-inventories (§9). P-1–P-9. G-3 acceptance of §4.7/§13, marker mode and P-6 (incl. marker retention/deletion). G-7a: P-9(i), named operator, stops listed. G-7b: P-7, P-9(ii), §5.2 choice only on failure, `.numista.ai` cookie acceptance only if observed.
````

=== END FILE B ===

---

## FILE C1 — `cos-review/v6/COS_REVIEW_META_PIXEL_v6.md` (full independent CoS technical review of v6)
SHA-256 `f5b20d69f63decc5df9ae6c60665b096839db9b931c57ef024d1c4e2225f27fa` · 12403 bytes

````markdown
# Independent CoS technical review: Meta Pixel signup attribution plan v6

**Reviewed in full (same independent reviewer as v5; did not write any plan):**
- `PLAN_META_PIXEL_SIGNUP_ATTRIBUTION_v6.md`, SHA `8df72e6b558742ae388db965417cddf8f346d1992c056f5aa3f0350228533df3`, 501 lines (verified).
- `CLOSURE_MAP_v6.md`.
- `cos-review/v5/COS_GATE_DISPOSITION.md`, plus my own v5 review and summary (unchanged; SHAs `fd2eb94b…2ac2` and `419c8eb5…530c`).
- Manifests: `V6_SUBMISSION.sha256` and `PRESERVATION_V6_CHECK.sha256` all OK; `sources-v2/` 19/19 and `sources-v3/` 10/10 OK.

**Nature:** technical preparation for the designated CoS gate. Not SAG, not a gate decision, no approval. **Not touched:** repo, tree, laptop, accounts, credentials, Meta, DNS, Hosting, browser, tests, deploys, SAG, paid APIs, peers; no public fetch needed. "L" = v6 line. All tests are future contracts; no runtime proof is required for a PLAN pass, and none is claimed. Source gates 1–15 remain **unresolved hypotheses**, and nothing here treats them as settled.

## Assessment: **97 / 100** — meets the 95 threshold; **no critical blocker open**
Same rubric and deduction scale as v1–v5 (87/91/92/92/94): −2 critical design defect, −1 material defect, −1 per minor precision bundle.

| Area (weight) | v5 | v6 | Driver |
|---|---|---|---|
| Privacy isolation & minimisation (20) | 18.5 | 19.5 | N-1 items 1, 3, 4 |
| Consent & lifecycle (20) | 19.5 | 20 | — |
| Measurement validity (15) | 14.5 | 14.5 | N-1 item 2 |
| Deploy safety, composition, rollback (20) | 17 | 19.5 | N-2 items 1–2 |
| Meta SDK / source discipline (10) | 10 | 10 | — |
| Gating, scope, side effects, proportionality (10) | 10 | 9 | R1 |
| Test contracts (5) | 4.5 | 4.5 | N-2 item 3 |
| **Total** | 94 | **97** | |

| # | Finding | Class | Weight |
|---|---|---|---|
| R1 | The unconditional strip of every `utm_*` for all visitors can silently break existing consumers of utm data, and no IC-0 STOP detects it | Material, closure-induced (partly from my own v5 B3 repair text) | −1 |
| N-1 | Rules and privacy wording precision (4 items) | Minor | −1 |
| N-2 | Ops and contract precision (3 items) | Minor | −1 |
| | **Total** | | **−3 → 97** |

R1 is not critical: it cannot affect account availability, consent or Meta data flow, and its repair is one IC-0 inventory line plus one STOP. **The CoS decision is yours.**

---

## v5 blockers: verification

### B1 (critical) — **CLOSED**
**Evidence:**
- The profile field and every profile-rule change are removed (L47, L273, L487, T-11 L465).
- The marker is a separate `acq_meta/{uid}` document (L246). It is created only after the profile create succeeds, fire-and-forget, never awaited, with every error dropped, no retry and no backfill (L255–258, L188, L194).
- The appended rules block is at L262–269.
- Rollback (c) is verified with a sign-up plus a profile edit (L347).
- Profile edits are in G-7a runs 1–2 and in the daily canaries (L388–389, L422).
- T-8h (L462) covers denied, missing-rules, offline, hanging and throwing writes, including merge and non-merge edits.
- T-24 (L478) covers current, marker-less and rollback builds, with and without the block.

**The traps you asked about, checked:**
- **No rules OR/wildcard trap on availability.** Firestore rules only grant; there is no deny that could override an existing allow. A separate `match /acq_meta/{uid}` cannot narrow any existing grant on profile or other paths. If an existing recursive wildcard overlaps the new path, it can only *add* access to `acq_meta`; it can never remove access elsewhere. A syntactically invalid ruleset is rejected at deploy, not served. Rules removal is app-before-rules and never needed for safety (L348). See N-1.1 for the confidentiality side of an overlap.
- **No async fault reaches account availability.** The write is not on the readiness list and is not awaited. If it is denied, the SDK rejects that one mutation and later queued writes proceed. Ordering is honestly left as source gate 13, which degrades measurement only (L88). T-8h covers a synchronous throw.
- **Rollback, cached, foreign and old clients** can only stop marker writes (L273, L367). This is now a design property, not a disclosure.

**Denominators and joins are honest:**
- W is defined over Auth creation time (L282).
- M-A is explicitly a floor (L286).
- M-A% is labelled as a share of marker-written accounts, including the consent variant (L287).
- An unknown snapshot writes no document instead of `false` (L258, Y1), so losses go to M-U, not into the denominator.
- M-U0 makes failed profile creates visible (L289).
- Expected M-U populations, the 72-hour grace and a context-only cue are stated (L293–295).
- The count query joins Auth, `acq_meta` and profile existence (L277), and T-24 seeds every class.

### B2 — **CLOSED**
- The Pixel kill (b) is checked only against the completion site and deploys even on mismatch (L345); T-21 (L475) covers it.
- App stops (a) and (c) are the actual live commit plus exactly one or two constants, checked by a receipted mechanical diff, with unrelated live changes preserved and no review wait (L346–347, L365).
- Authority exists only because the future G-7a/G-7b YES names stops (a)–(c) (L17–18, L341, L484). No self-permission and no new layer.
- Non-stop deploys remain fully composition-gated (L358–363).
- Cadence and operator are named, and the blind spots are stated honestly (L422–423).

### B3 — **CLOSED** (with closure-induced R1)
- Exact boot order: capture → strip → Auth init → single redirect consumer (L117–122). The redirect therefore starts and returns on a clean URL (L137–139).
- An identical `fbclid` keeps its original `captured_at` (L232); T-6 and run 11 test it (L460, L398).
- Logs are described truthfully (L302, L494, source gate 14).
- There is no impossible "never reaches Numista servers" claim and no "no personal data" claim. Existing Auth and profile flows are stated as unchanged rather than denied (L301, L374).
- IC-0 URL-reader inventory with STOP (L441).

### N-A and N-B — **all CLOSED**
- **N-A:**
  - Re-inventories before stage A and stage B, with "no deploy of that stage until amended" (L446, L404, L421).
  - Preview `MARKER_ENABLED=OFF` (L315, L322, T-4).
  - Preview fail-path-only coverage stated (L320).
  - T-6, T-11 and T-24 rewritten.
- **N-B:**
  - Other clients and cached-build grace (L293–294, L438).
  - Exact population names (L249, L282–291).
  - Bounded k timing at +2 h and finally +24 h (L416, L76).
  - Two-tab nonce undercount (L207, L472, L497).
  - Validation cleanup (L126, L163, T-23).

### Y1–Y8 (writer's new items)
| Y | Verdict |
|---|---|
| Y1 | Sound (no doc on unknown) |
| Y2 | Sound for privacy. It introduces delete-then-recreate mutability (N-1.2) |
| Y3 | Availability reasoning correct. The read-exposure side is incomplete (N-1.1) |
| Y4–Y8 | Sound |

---

## Material finding

### R1 — Unconditional `utm_*` strip can silently break existing utm consumers (−1)
**Evidence:**
- L119, L234 and L483: every `utm_*` parameter is removed for **every visitor** from G-7a, not only on `fbclid` landings and not only `utm_campaign`.
- My own v5 B3 repair text asked for the strip to run "before any auth or analytics initialisation". Done that way, any existing analytics or marketing consumer that reads utm parameters from the page URL after the strip (for example web analytics campaign attribution on non-Meta campaigns) loses them silently.
- IC-0 L441 STOPs only when a reader records or forwards the URL **before** the strip, or when telemetry records URLs that still contain the parameters. A consumer that *needs* utm after the strip is not detected.
- §4.7 (L223) discloses only the bookmark/copied-link effect.

This degrades existing business measurement for all traffic. It does not touch availability, consent or Meta data flow.

**Minimal repair:**
1. Add an IC-0 inventory line, "existing consumers of `utm_*`/`fbclid` (app code, analytics, marketing tools, other live plans)". If any exists, STOP and amend.
2. Narrow the default strip to `fbclid` plus `utm_*` only on landings that carried an `fbclid`, or let the existing consumer read before the strip. The choice is Eric's business trade-off at G-3.

Mirror the line in §4.7 and T-6.

## Minor notes (not blockers)

**N-1, rules and privacy wording (−1):**
1. **Broad-wildcard overlap also affects read confidentiality** (L272, Y3). The text says "only immutability weakens… nothing else changes". A broad `read`/`list` grant would also expose other users' uid→acquisition Booleans. IC-0 should record read/list overlap too, and STOP or amend if non-owners can read.
2. **Owner delete plus create allows a later re-create with any value** (L268, L271). The marker is therefore owner-mutable even without a wildcard. That is acceptable for client-asserted measurement, but L271 "a deleted marker only makes that account unmarked" and the "create-only/immutable" wording should say so (§13).
3. **The app's own Referrer-Policy is not recorded by IC-0** (L437). Subresource requests made before the strip carry the full landing URL as `Referer` under weak policies. Record it and treat weaker than `strict-origin-when-cross-origin` as an amend item.
4. **Account-deletion order** (L275). The owner delete of `acq_meta/{uid}` must run **before** the Auth user is deleted, because auth is needed for the rule.

**N-2, ops and contracts (−1):**
1. **L426 maps "any Meta request from the SPA" to stop (b).** That is the completion site, so it cannot stop an SPA request. It should be stop (c) (and (a)), plus (b) as belt-and-braces.
2. **L346: when a foreign live commit cannot be identified, only (b) remains.** The handoff still navigates to a no-Pixel completion page. State this residual, plus (d) as the last resort, in §13.
3. **L360 "diff only this plan's files"** is inherited wording. The feature necessarily edits existing sign-up, first-run and deletion files. Say "only this plan's changes".

## Whole-plan regression scan (no new scope invented)
These are unchanged and still sound:
- lifecycle traces (L116–143);
- the snapshot table (L159–166);
- at most one locally authorized attempt per consenting new account, with the attempt-id guard and snapshot deletion (L161, L182);
- the binding cookie (L196–207);
- Meta order, CSP and load-gated `trackSingle` (L324–338);
- no ratio (L295);
- emitted vs received accounting (L415–424);
- the marker-only fallback, which is truly independent of the subdomain and preview (L430).

No hidden or standing authorization was found:
- the operator and daily queries are explicitly under the G-7a YES (L422);
- stops are named in the future YES;
- synthetic deletion needs its own approval (L381);
- gates G-1–G-7b are unchanged.

The only closure-induced regression found is R1.

## Open future verification and business gates (explicit; not closed by drafting)
- **Source gates 1–15** (L74–90), including the new 13 (write-ack order), 14 (Hosting/Cloud request logs) and 15 (service-worker caching).
- **IC-0** full, before G-3 and again before G-7a, plus the re-inventories before stage A and stage B (L435–446).
- **P-1–P-9** (L94–105).
- **G-3:** §4.7/§13 acceptance, marker mode, counsel P-6 (including marker retention and deletion).
- **G-4:** P-8.
- **G-6:** local-only or not.
- **G-7a:** P-9(i), named operator, stops listed.
- **G-7b:** P-7, P-9(ii), stops listed, the §5.2 choice only on failure, `.numista.ai` acceptance only if observed.
- **Business (Eric, later):** marker-only versus handoff (L501), and the R1 strip scope.

## Ledger (inherited; no reset)
| Attempt | Result |
|---|---|
| Original writer, v1–v4 | 87/91/92/92, retired |
| v5, replacement try 1, global 5 | 94 REVISE (critical B1) |
| v6, replacement try 2, **global 6 of 10** | This review: 97 |

This review, mirrors and hash files add zero.

## Recommended next authorized action
The designated CoS gate decides. Technically, v6 meets the CoS threshold with no critical blocker. I recommend the CoS weigh whether R1's single IC-0/STOP line should be folded in before full-plan SAG (G-2). Any new text would be a new submission under the ledger unless the CoS rules otherwise. Nothing here authorizes SAG, implementation, accounts, deploys, tests, spend or contact.
````

=== END FILE C1 ===

---

## FILE C2 — `cos-review/v6/SUMMARY.md` (summary of the independent v6 review)
SHA-256 `2d0d7b1dedac291f0f12453e9288b468c54e153301ad2a4c48c6387c8c6098a3` · 2575 bytes

````markdown
# Summary: CoS technical review of Meta Pixel v6 (preparation for the designated CoS gate; not SAG; no approval)

**Assessment: 97 / 100.** Meets the 95 threshold; no critical blocker open. Same rubric as v1–v5. Full review: `COS_REVIEW_META_PIXEL_v6.md`. Plan SHA `8df72e6b…33df3` (501 lines) verified. All manifests and source archives OK.

**v5 findings:**
- **B1 (critical):** CLOSED.
  - Separate `acq_meta/{uid}` document; fire-and-forget after the profile create; not awaited; errors dropped.
  - Profile rules untouched. Firestore rules only grant, so there is no OR/wildcard availability trap.
  - Honest W, M-A floor, M-A%, M-U and M-U0 joins; T-8h and T-24 are real contracts.
- **B2:** CLOSED. Completion-only Pixel kill. Mechanical one- or two-constant app stops on the actual live commit. Authority only via a future YES that names the stops.
- **B3:** CLOSED. Capture → strip → Auth → redirect; identical-ID freshness kept; truthful logging statements.
- **N-A and N-B:** all CLOSED.
- **Y1–Y8:** sound, apart from the wording notes below.

**Remaining:**
- **R1 (−1, material, closure-induced; partly from my own v5 repair text):** the plan strips every `utm_*` for all visitors (L119, L234, L483), and no IC-0 STOP detects existing utm consumers that read after the strip. Existing campaign analytics can break silently.
  - **Repair:** an IC-0 inventory of existing `utm_*`/`fbclid` consumers with STOP and amend, and narrowing the strip (for example, only on `fbclid` landings) as Eric's G-3 choice.
- **N-1 (−1):**
  - a wildcard overlap also exposes reads (L272);
  - owner delete plus re-create makes the marker owner-mutable (L268–271);
  - IC-0 should record the app's Referrer-Policy;
  - delete the marker before the Auth user.
- **N-2 (−1):**
  - an SPA Meta request maps to stop (b), which cannot stop it; it should be (c) or (a) (L426);
  - the residual when a foreign live commit is unidentifiable (L346);
  - "this plan's files" wording (L360).

**Open future gates:** source gates 1–15, IC-0 and the stage A/B re-inventories, P-1–P-9, the G-3–G-7b decisions, and Eric's business choices (marker-only, strip scope).

**Ledger:** v1–v4 87/91/92/92 (retired); v5 94 (replacement try 1, global 5); v6 = replacement try 2, global 6 of 10. Reviews add zero.

**Next:** the CoS decides. Consider folding in R1's single STOP line before SAG; any new text is a new submission unless the CoS rules otherwise.

**Preservation:** BEFORE and AFTER hashes cover all 90 pre-existing files, including the v5 gate and my v5 review.
````

=== END FILE C2 ===

---

## FILE D — `cos-review/v6/COS_GATE_DISPOSITION.md` (designated CoS gate disposition for v6)
SHA-256 `42ec4059c33660921aa4945e620ed0c89d0e2e658d7429b1f551a98d3890a3dd` · 3688 bytes

````markdown
# Designated CoS gate disposition — Meta Pixel v6

Recorded: 2026-11-09 11:20:51 AM EST

Decision: **97/100, CoS PLAN PASS** for the immutable v6 submission only. No critical design blocker remains. This is the designated CoS decision, informed by independent technical preparation, not a delegated approval and not runtime verification.

Plan: `PLAN_META_PIXEL_SIGNUP_ATTRIBUTION_v6.md`
SHA-256: `8df72e6b558742ae388db965417cddf8f346d1992c056f5aa3f0350228533df3`
Independent review: `cos-review/v6/COS_REVIEW_META_PIXEL_v6.md`
Review SHA-256: `f5b20d69f63decc5df9ae6c60665b096839db9b931c57ef024d1c4e2225f27fa`

## CoS basis
CoS read the entire v6 plan and independent review, and the preceding v5 disposition. Moving the acquisition marker out of essential profile writes removes the profile-availability failure coupling. Independent completion-site kills and mechanical app stop diffs remove the prior composition deadlock. URL capture/strip order, stable landing age and candid request-log disclosure close the prior raw-URL claims. The lifecycle, consent, measurement populations and staged tester-only widening remain coherent as plan contracts. The unchanged rubric supports 97, with the material analytics-compatibility finding and two precision bundles still deducted rather than concealed.

## Findings retained, not closed
- R1: stripping every utm parameter for every visitor can disrupt existing campaign consumers; the IC-0 inventory does not explicitly catch consumers that need the stripped parameters later.
- N-1: broader rules can weaken read confidentiality, not only immutability; owner delete/re-create permits changes; app Referrer-Policy and account-deletion ordering need precision.
- N-2: SPA Meta-request stop mapping is imprecise; unidentified live-commit fallback leaves handoff navigation active; composition should refer to changes, not exclusive files.

These are actual review findings, not invented current-site facts. They remain explicit inputs to full-plan SAG and any subsequent amendment. Source gates 1–15, IC-0, prerequisites and all business/account/test/deploy decisions remain unresolved. The pass does not establish that current rules are safe or that any proposed test has passed. No text was silently amended. Any revised plan is a new immutable submission and must receive its own applicable reviews; this v6 pass does not automatically attach to revised bytes.

## Next authorized action and boundaries
Preparation of the review package is complete: the exact v6 plan, closure map, submission/preservation manifests, full independent review and this disposition are available locally. Next gate is **full-plan SAG >=95**, reviewing the entire exact plan plus retained findings, not a delta-only summary. No SAG request or paid call is made or authorized by this disposition. Do not infer permission from this file or a peer relay.

Eric's original instruction remains: prepare the plan only; no implementation until his YES. No implementation, repo/laptop/current-tree change, Meta/account/credential action, DNS/Hosting action, Firestore change, live test, synthetic account, paid API or deployment is authorized. Existing scoped permissions and Eric's typed YES remain separate requirements. No new approval layer is added.

## Ledger
Original writer: v1–v4 = 87/91/92/92, retired after four failed tries.
Replacement writer: v5 = 94 REVISE (try1/global5); **v6 = 97 CoS PLAN PASS (try2/global6 of10)**.
Reviews, gate records and mirrors add zero. No retry counter reset.

Preservation: plan hash verified; V6_SUBMISSION and PRESERVATION_V6_CHECK all OK; review before/after manifests identical. Earlier artifacts were not edited.
````

=== END FILE D ===

---

## FILE E — `V6_SUBMISSION.sha256` (submission manifest)
SHA-256 `2fb0cad249b424ea65eeb512d12a2a3753d6b0fc75f24648c2622e5855e61365` · 286 bytes

````markdown
8df72e6b558742ae388db965417cddf8f346d1992c056f5aa3f0350228533df3  PLAN_META_PIXEL_SIGNUP_ATTRIBUTION_v6.md
6dd1ea01f1d2af376c1db92fd88941cb2b0a84496b2cfda979b9060d4658c0da  CLOSURE_MAP_v6.md
9c1a743b595c193552fa07f211a8e921f46d74e71075a3d4a527545dfdc67c59  PRESERVATION_V6_CHECK.sha256
````

=== END FILE E ===

---

## 3. Archived official source excerpts cited by the plan

These excerpts come from the owner's archived copies, fetched 9 Nov 2026 (HTTP 200). The SHA-256 values match the archive manifests, which were re-verified while preparing this packet.
- Meta pages were archived as the official Markdown renderings. Their URLs are taken from the pages' own links, or from the archive file names where no self-link exists; those are marked "(URL per archive name)".
- "Plan cites" lists the File A lines that use each source.
- Excerpts are quoted exactly. Single-line text extractions show "…" around the quoted window.
- Anything the plan treats as a **source gate (1–15)** has **no** archived text and is **not** verified by anything below.

### S-ADV — Meta Pixel: Advanced
- Official URL: https://developers.facebook.com/documentation/meta-pixel/advanced
- Archive file: `sources-v2/advanced.txt` · SHA-256 `7092070c919ae1eaa1753475eb9938f4fb7e4e87a9c399430bc5f01e5dfb1a60`
- Plan cites: L68

````text
   14| 
   15| If you need to install the Pixel using a lightweight implementation, you can install it with an `<img>` tag. To do this, add the code below between an opening and closing `<noscript>` tag within your website's header or body, and replace `{pixel-id}` with your pixel's ID and `{standard-event}` with a [Standard Event](https://developers.facebook.com/documentation/meta-pixel/reference#standard-events).
   16| 
   17| ```
   18| <img src="https://www.facebook.com/tr?id={pixel-id}&ev={standard-event}" height="1" width="1" style="display:none"/>
   19| ```
…
  113| ## Tracking clicks on Buttons {#buttonclicks}
  114| 
  115| When a visitor clicks a button, the Meta Pixel's JavaScript code automatically detects and passes the relevant form fields to Meta.
  116| 
…
  431| ## Selective event tracking with multiple Pixels {#multipixels}
  432| 
  433| If you have multiple Pixels on the same page and would like to selectively fire events on each unique Pixel, the `trackSingle` and `trackSingleCustom` capabilities should be used.
  434| 
  435| Using the `track` function on pages that have multiple Pixels initialized (either using multiple base codes or even combining it within one base code) could produce over-firing or unexpected behavior and should be applied only in specific situations.
…
  459| 
  460| ```
  461| fbq('trackSingle', 'FB_PIXEL_ID', 'Purchase', customData);
  462| fbq('trackSingleCustom', 'FB_PIXEL_ID', 'CustomEvent', customData);
  463| ```
…
  465| ## Automatic Configuration
  466| 
  467| The Meta Pixel will send button click and page metadata (such as data structured according to Opengraph or Schema.org formats) from your website to improve your ads delivery and measurement and automate your Pixel setup. To configure the Meta Pixel to not send this additional information, in the Meta Pixel Base code, add `fbq('set', 'autoConfig', 'false', 'FB_PIXEL_ID')` above the init call.
  468| 
  469| ```
  470| <!-- Facebook Pixel Code -->
  471| <script>
  472| !function(f,b,e,v,n,t,s){
  473| if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  474| n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
  475| n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
  476| t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
  477| document,'script','https://connect.facebook.net/en_US/fbevents.js');
  478| // Line to enable Manual Only mode.
  479| fbq('set', 'autoConfig', false, 'FB_PIXEL_ID');
  480| //Insert Your Facebook Pixel ID below.
  481| fbq('init', 'FB_PIXEL_ID');
…
  488| ```
  489| 
  490| ## Content Security Policy
  491| 
  492| If your website has a [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP), you should allow JavaScript to load from `https://connect.facebook.net`. Note: The Pixel load scripts from two paths: `/en_US/fbevents.js` and `/signals/config/{pixelID}?v={version}`.
  493| 
````

### S-GDPR — Meta Pixel: General Data Protection Regulation
- Official URL: https://developers.facebook.com/documentation/meta-pixel/implementation/gdpr
- Archive file: `sources-v2/implementation_gdpr.txt` · SHA-256 `361bae7df352aee295faa0724526b1c73df8973a01f6ff7d07ed9483ec6af90a`
- Plan cites: L68

````text
   13| Businesses may want to implement code that creates a banner and requires affirmative consent (for example, an "I agree" checkbox at the top of the page) to use the Pixel. If you already have a system in place that addresses this need, such as a tag manager, you can make this code optional.
   14| 
   15| Use the following API to pause sending Pixel fires to Facebook, and once cookie consent is granted, send Pixel fires to Facebook. You need to call revoke on every page.
   16| 
   17| ```
   18| fbq('consent', 'revoke');
   19| fbq('consent', 'grant');
   20| ```
   21| 
   22| For example:
   23| 
   24| ```
   25| // Revoke consent before 'init' is called
   26| fbq('consent', 'revoke');
   27| fbq('init', '<your pixel ID>');
   28| fbq('track', 'PageView');
   29| ```
   30| 
   31| ```
   32| // Once affirmative consent has been granted
   33| fbq('consent', 'grant');
   34| ```
   35| 
   36| See our [Cookie Policy](https://www.facebook.com/policies/cookies/) for details about the cookies used and the data received. The Meta Pixel receives these types of data:
   37| 
   38| * **Http Headers** – Anything that is generally present in HTTP headers, a standard web protocol sent between any browser request and any server on the internet. This information may  include data like IP addresses, information about the web browser, page location, document, referrer and person using the website.
   39| * **Pixel-specific Data** – Includes Pixel ID and the Facebook Cookie.
   40| * **Button Click Data** – Includes any buttons clicked by site visitors, the labels of those buttons and any pages visited as a result of the button clicks.
   41| * **Optional Values** – Developers and marketers can optionally choose to send additional information about the visit through [conversion tracking](https://developers.facebook.com/documentation/meta-pixel/implementation/conversion-tracking). Example custom data events are conversion value, page type, and more.
   42| * **Form Field Names** – Includes website field names like 'email', 'address', 'quantity' for when you purchase a product or service. We don't capture field values unless you include them as part of [Advanced Matching](https://developers.facebook.com/documentation/meta-pixel/advanced/advanced-matching), or [conversion tracking](https://developers.facebook.com/documentation/meta-pixel/implementation/conversion-tracking).
   43| 
   44| ## Learn more
````

### S-REF — Meta Pixel API reference (standard events)
- Official URL: https://developers.facebook.com/documentation/meta-pixel/reference
- Archive file: `sources-v2/reference.txt` · SHA-256 `7b45303f2551e31a3241b319779b6d95fcb0f59a9a7e419d0a82d82cbfe72441`
- Plan cites: L68

````text
   12| | --- | --- | --- | --- |
   13| | `AddPaymentInfo` | When payment information is added in the checkout flow. *A person clicks on a save billing information button.* | `content_ids`, `contents`, `currency`, `value`<br><br>*Optional.* | ADD_PAYMENT_INFO |
   14| | `AddToCart` | When a product is added to the shopping cart.<br>*A person clicks on an add to cart button.* | `content_ids`, `content_type`, `contents`, `currency`, `value`<br><br>*Optional.*<br>*Required for Advantage+ catalog ads:<br><br>`contents`<br><br>*<br> | ADD_TO_CART |
   15| | `AddToWishlist` | When a product is added to a wishlist.<br>*A person clicks on an add to wishlist button.* | `content_ids`, `contents`, `currency`, `value`<br><br>*Optional.* | ADD_TO_WISHLIST |
   16| | `CompleteRegistration` | When a registration form is completed.<br>*A person submits a completed subscription or signup form.* | `currency`, `value`<br><br>*Optional.* | COMPLETE_REGISTRATION |
   17| | `Contact` | When a person initiates contact with your business via telephone, SMS, email, chat, etc.<br>*A person submits a question about a product.* | *Optional.* | CONTACT |
…
   44| | `predicted_ltv` | Integer, float | Predicted lifetime value of a subscriber as defined by the advertiser and expressed as an exact value. |
   45| | `search_string` | String | Used with the `Search` event. The string entered by the user for the search. |
   46| | `status` | Boolean | Used with the `CompleteRegistration` event, to show the status of the registration.<br><br>*Optional.* |
   47| | `value` | Integer or float | The value of a user performing this event to the business. |
````

### S-SPA — Meta Pixel for Single Page Applications (plan does not use disablePushState)
- Official URL: https://developers.facebook.com/documentation/meta-pixel/implementation/tag_spa (URL per archive name)
- Archive file: `sources-v2/implementation_tag_spa.txt` · SHA-256 `ba4f9b7df772819248b0ba9a9384f7b0510f1c5c73f9fb6a531d16d77390daab`
- Plan cites: L68

````text
    1| Meta Pixel Implementation for Single Page Applications# Meta Pixel Implementation for Single Page Applications
    2| 
    3| 
    4| 
    5| Single Page Applications (SPA) does not require a page to be reloaded when the URL changes therefore a different approach to event tracking with the Meta Pixel has to be followed.
    6| 
    7| ### Requirements
    8| 
    9| - The Pixel's [base code](https://developers.facebook.com/documentation/meta-pixel/get-started) must already be installed on the webpage where you will be tracking events.
   10| 
   11| **Note:** You can set `disablePushState` to `true` to stop sending `PageView` events on history state changes but it is not recommended.
   12| 
   13| ## Track a an Action
````

### S-AM — Meta Pixel: Advanced matching (plan uses no matching parameters)
- Official URL: https://developers.facebook.com/documentation/meta-pixel/advanced/advanced-matching
- Archive file: `sources-v2/advanced_advanced-matching.txt` · SHA-256 `ed8790616daff8da3653219ac8a4efa612ed03632aca840145dcadccd62bbf77`
- Plan cites: L68

````text
    9| To [automatically implement advanced matching](https://www.facebook.com/business/help/1993001664341800) use the [Events Manager](https://business.facebook.com/events_manager/).
   10| 
   11| ## Implementation
   12| 
   13| To use advanced matching, format the visitor's data as a JSON object and include it in the [pixel base code `fbq('init')` function call](https://developers.facebook.com/documentation/meta-pixel/get-started#base-code) as a third parameter.
   14| 
   15| Be sure to place advanced matching parameters in the pixel base code or the values will not be treated as manual advanced matching values.
   16| 
   17| For example, if your pixel ID was `283859598862258`, you could do this:
   18| 
   19| ```
   20| fbq('init', '283859598862258', {
   21|   em: 'email@email.com',         //Values will be hashed automatically by the pixel using SHA-256
   22|   fn: 'first_name',
   23|   ln: 'last_name'
   24|   ...
   25| });
   26| ```
````

### S-DPO — Meta Pixel: Data processing options for US users
- Official URL: https://developers.facebook.com/documentation/meta-pixel/implementation/data-processing-options (URL per archive name)
- Archive file: `sources-v2/implementation_data-processing-options.txt` · SHA-256 `c0ee8de48ab6a1ee542d47476694f35ec5931216477f0fbda7a5a6bd8013a109`
- Plan cites: L68

````text
   14| ## Implementation
   15| 
   16| | Implementation | Adding Data Processing Options |
   17| | --- | --- |
   18| | Browser Pixel | Update Pixel initialization code to specify the `dataProcessingOptions` method before you call `fbq('init')`.<br><br>To explicitly not enable Limited Data Use (LDU):<br><br>```
   19| fbq('dataProcessingOptions', []);
   20| fbq('init', '{pixel_id}');
   21| fbq('track', 'PageView');
   22| ```<br><br>To enable LDU and have Meta perform geolocation:<br><br>```
   23| fbq('dataProcessingOptions', ['LDU'], 0, 0);
   24| ```<br><br>To enable LDU and specify the location, e.g., for California:<br><br>```
   25| fbq('dataProcessingOptions', ['LDU'], 1, 1000);
   26| ``` |
   27| | Image tag | Add the following to the Pixel image tag:<br><br>* `dpo`: data processing options<br>* `dpoco`: data processing options country<br>* `dpost`: data processing options state<br><br>See [Reference](https://developers.facebook.com/documentation/ads-commerce/marketing-api/overview/data-processing-options#reference) for accepted values.<br><br>To explicitly not enable LDU, pass an empty value for the `dpo` parameter:<br><br>```
   28| <img src="https://www.facebook.com/tr?id={pixel_id}&ev=Purchase&dpo=" />
````

### S-GS — Get started with the Meta Pixel (base code)
- Official URL: https://developers.facebook.com/documentation/meta-pixel/get-started
- Archive file: `sources-v2/get-started.txt` · SHA-256 `3df760f7a03ffdd8ee2908ba8d5d6c227fe43007db6cf8e3e570061f625db5f2`
- Plan cites: L68, L326

````text
   28| 
   29| The base Pixel code contains your Pixel's ID in two places and looks like this:
   30| 
   31| ```
   32| <!-- Facebook Pixel Code -->
   33| <script>
   34|   !function(f,b,e,v,n,t,s)
   35|   {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
   36|   n.callMethod.apply(n,arguments):n.queue.push(arguments)};
   37|   if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
   38|   n.queue=[];t=b.createElement(e);t.async=!0;
   39|   t.src=v;s=b.getElementsByTagName(e)[0];
   40|   s.parentNode.insertBefore(t,s)}(window, document,'script',
   41|   'https://connect.facebook.net/en_US/fbevents.js');
   42|   fbq('init', '{your-pixel-id-goes-here}');
   43|   fbq('track', 'PageView');
   44| </script>
   45| <noscript>
   46|   <img height="1" width="1" style="display:none"
   47|        src="https://www.facebook.com/tr?id={your-pixel-id-goes-here}&ev=PageView&noscript=1"/>
   48| </noscript>
   49| <!-- End Facebook Pixel Code -->
   50| ```
````

### S-CT — Meta Pixel: Conversion tracking
- Official URL: https://developers.facebook.com/documentation/meta-pixel/implementation/conversion-tracking
- Archive file: `sources-v2/implementation_conversion-tracking.txt` · SHA-256 `79d9231b23d4bcbfa75b82c8fa3048e97b4f307cd6be6ad4b48dbd6e09a3e623`
- Plan cites: L68

````text
   36| ### Tracking Standard Events
   37| 
   38| All standard events are tracked by calling the Pixel's `fbq('track')` function, with the event name, and (optionally) a JSON object as its parameters. For example, here's a function call to track when a visitor has completed a purchase event, with currency and value included as a parameter:
   39| 
   40| ```js
   41| fbq('track', 'Purchase', {currency: "USD", value: 30.00});
   42| ```
   43| 
   44| If you called that function, it would be tracked as a purchase event in the Events Manager:
   45| 
   46| You can call the `fbq('track')` function anywhere between your web page's opening and closing `<body>` tags, either when the page loads, or when a visitor completes an action, such as clicking a button.
   47| 
   48| For example, if you wanted to track a standard purchase event _after a visitor has completed the purchase_, you could call the `fbq('track')` function on your _purchase confirmation page_, like this:
   49| 
   50| ```js
   51| <body>
   52|   ...
   53|   <script>
   54|     fbq('track', 'Purchase', {currency: "USD", value: 30.00});
   55|   </script>
   56|   ...
````

### S-FBMS — Firebase Hosting: Share project resources across multiple sites
- Official URL: https://firebase.google.com/docs/hosting/multisites
- Archive file: `sources-v3/firebase_hosting_multisites.txt` · SHA-256 `d84acb1cb05b823eaf1cb945b0448a7b2a20c218f215e6aa74c4599b97f9aa44`
- Plan cites: L70, L315, L349

````text
…one or more Firebase Hosting sites in a single Firebase project. Since the sites are all in the same Firebase project, all the sites can access the other Firebase resources of the project. Each site has its own hosting configuration . Each site hosts its own coll…

…other Firebase resources of the project. Each site has its own hosting configuration . Each site hosts its own collection of content. Each site can have one or more associated domains . By setting up mult…

…your local project directory. Command Description firebase emulators:start --only hosting Emulates the Hosting content and configuration of the default Hosting site at a locally hosted URL firebase emulators:start --only hosting: TARGET_NAME Emulates the Hosting content and configuration…

…e at a preview URL firebase hosting:channel:deploy \ CHANNEL_ID --only TARGET_NAME Deploys the Hosting content and configuration of the specified Hosting site at a preview URL firebase deploy --only hosting Deploys the Hosting content and configuration to the live channel of all Hosting sites configured in firebase.json firebase deploy --only hosting: TARGET_NAME Deploys the Hosting content and configuration to the live channel of the specified Hosting site Command Description (not recommended; use emulators:start instead) firebase s…

…has the same SITE_ID as your Firebase project ID. Caution: Deleting a site is a permanent action. If you delete a site, Firebase doesn't maintain records of deployed files or deployment history, and the SITE_ID cannot be reactivated by you or anyone…
````

### S-FBPV — Firebase Hosting: Test your web app locally, share changes, then deploy live (preview channels)
- Official URL: https://firebase.google.com/docs/hosting/test-preview-deploy
- Archive file: `sources-v3/firebase_hosting_preview_channels.txt` · SHA-256 `61bae18f13bd66cf012502d80615a4b569f0a695cae7506b3e37b014f441a368`
- Plan cites: L70

````text
…temporary URL. When using a preview URL, your web app interacts with your real backend for all project resources (with the exception of any "pinned" functions in your rewrites config ). Note that although preview URLs are difficult to guess (as they contain a random hash), they are public. So, anyone who knows the URL can access it. From the root of your local project directory, run the f…
````

### S-6265 — RFC 6265 HTTP State Management Mechanism
- Official URL: https://www.rfc-editor.org/rfc/rfc6265.txt
- Archive file: `sources-v3/rfc6265.txt` · SHA-256 `dc4177094813e85a44a7897b892b76bc09160b3a03aea44f0f511f3a98f91933`
- Plan cites: L70, L202

````text
  715|    The semantics of individual cookies in the Cookie header are not
  716|    defined by this document.  Servers are expected to imbue these
  717|    cookies with application-specific semantics.
  718| 
  719|    Although cookies are serialized linearly in the Cookie header,
  720|    servers SHOULD NOT rely upon the serialization order.  In particular,
  721|    if the Cookie header contains two cookies with the same name (e.g.,
  722|    that were set with different Path or Domain attributes), servers
  723|    SHOULD NOT rely upon the order in which these cookies appear in the
  724|    header.
  725| 
…
  890| 5.1.4.  Paths and Path-Match
  891| 
  892|    The user agent MUST use an algorithm equivalent to the following
  893|    algorithm to compute the default-path of a cookie:
  894| 
…
  916| 
  917|    4.  Output the characters of the uri-path from the first character up
  918|        to, but not including, the right-most %x2F ("/").
  919| 
  920|    A request-path path-matches a given cookie-path if at least one of
  921|    the following conditions holds:
  922| 
  923|    o  The cookie-path and the request-path are identical.
  924| 
  925|    o  The cookie-path is a prefix of the request-path, and the last
  926|       character of the cookie-path is %x2F ("/").
  927| 
  928|    o  The cookie-path is a prefix of the request-path, and the first
  929|       character of the request-path that is not included in the cookie-
  930|       path is a %x2F ("/") character.
  931| 
…
 1295|    10.  If the cookie was received from a "non-HTTP" API and the
 1296|         cookie's http-only-flag is set, abort these steps and ignore the
 1297|         cookie entirely.
 1298| 
 1299|    11.  If the cookie store contains a cookie with the same name,
 1300|         domain, and path as the newly created cookie:
 1301| 
 1302|         1.  Let old-cookie be the existing cookie with the same name,
 1303|             domain, and path as the newly created cookie.  (Notice that
 1304|             this algorithm maintains the invariant that there is at most
 1305|             one such cookie.)
 1306| 
 1307|         2.  If the newly created cookie was received from a "non-HTTP"
 1308|             API and the old-cookie's http-only-flag is set, abort these
 1309|             steps and ignore the newly created cookie entirely.
 1310| 
 1311|         3.  Update the creation-time of the newly created cookie to
 1312|             match the creation-time of the old-cookie.
…
 1749| 8.5.  Weak Confidentiality
 1750| 
 1751|    Cookies do not provide isolation by port.  If a cookie is readable by
 1752|    a service running on one port, the cookie is also readable by a
 1753|    service running on another port of the same server.  If a cookie is
 1754|    writable by a service on one port, the cookie is also writable by a
 1755|    service running on another port of the same server.  For this reason,
 1756|    servers SHOULD NOT both run mutually distrusting services on
 1757|    different ports of the same host and use cookies to store security-
 1758|    sensitive information.
 1759| 
 1760|    Cookies do not provide isolation by scheme.  Although most commonly
````

### S-PSL — Public Suffix List
- Official URL: https://publicsuffix.org/list/public_suffix_list.dat
- Archive file: `sources-v3/public_suffix_list.dat` · SHA-256 `dc00ceb7bb9256c41506b12a863db6a4b1c6021771eeccf5e073827750ac4b74`
- Plan cites: L70, L203

````text
    1| // This Source Code Form is subject to the terms of the Mozilla Public
    2| // License, v. 2.0. If a copy of the MPL was not distributed with this
    3| // file, You can obtain one at https://mozilla.org/MPL/2.0/.
    4| 
    5| // Please pull this list from, and only from https://publicsuffix.org/list/public_suffix_list.dat,
    6| // rather than any other VCS sites. Pulling from any other URL is not guaranteed to be supported.
…
13706| firebaseapp.com
…
13988| web.app
````

### S-RP — MDN: Referrer-Policy header
- Official URL: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Referrer-Policy
- Archive file: `sources-v3/mdn_referrer_policy.txt` · SHA-256 `7c1b0b1d6d304d086f5732d7748fdfddcbc34bb714a4ef2a88fcb487318712b2`
- Plan cites: L70

````text
…r-Policy header does not share this misspelling. Directives no-referrer The Referer header will be omitted: sent requests do not include any referrer information. no-referrer-when-downgrade Send t…
````

### S-SS — MDN: Window.sessionStorage
- Official URL: https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionStorage
- Archive file: `sources-v3/mdn_storage_sessionStorage.txt` · SHA-256 `81f36861049085fbc1e16b44d2c29434abd1e978323d0099086df66faa534f07`
- Plan cites: L70, L140

````text
…sessionStorage is similar to localStorage ; the difference is that while localStorage is partitioned by origin only, sessionStorage is partitioned by both origin and browser tabs (top-level browsing contexts). The data in sessionStorage is only kept for the duration of the page session. Whenever a document is loaded in a particular tab in the browser, a unique page session gets created and assigned to that particular tab. That page session is accessible only in that particular tab. The main document, and all embedded browsing contexts (iframes), are grouped by their origin and each origin has access to its own separate storage area. If the page has an opener , the sessionStorage is initially a copy of the opener's sessionStorage object. However, they are still separate and changes to one do not affect the other. To prevent the sessionStorage from being copied, use one of the techniques that remove opener (see Window.opener ). A page session lasts as long as the tab or the browser is open, and survives over page reloads and restores. Opening a page in a new tab or window creates a new session with the value of the top-level browsing context, which differs from how session cookies work. Closing the tab/w…
````

---

## 4. Explicitly unverified (do not treat as fact)
- **Source gates 1–15** in File A §1 (L74–L90). For example: Events Manager timing, domain verification, the AAM/AEM toggles, `fbclid`→`fbc`, localhost acceptance, preview stability, Firebase write-ack semantics and ordering, Meta cookie-scope controls, Hosting cookie forwarding and request logs, sessionStorage across a cross-origin round trip, ad URL parameters, and service-worker caching.
- **Everything about the current Numista code, rules, hosting, cookies, SDKs and account-creation clients.** IC-0 (§9) has not run. The only external facts are the audit records listed in §0.1.
- **All tests (T-1–T-24) and the production run tables (§8)** are future contracts. None has run.
- **No Pixel, dataset, Firestore document or rule, subdomain or deploy exists** for this plan.

=== END OF PACKET ===
