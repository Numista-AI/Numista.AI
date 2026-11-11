# SAG MANUAL FULL-PLAN REVIEW PACKET - NET-827 Stripe Checkout fail-fix B1-B5, plan v1.9.1 (Code Writing)

Prepared 2026-11-10 (America/New_York) by the GB CoS packet preparer. This packet is sent once to Stand Alone Grok through the xAI API under Eric's 7:13 PM ET authorization (t2553u), which covers SAG review only.

## 1. What you are asked to do
- **Exact artifact under review:** A1, `PLAN_NET-827_FAILFIX-B1B5_STRIPE-CHECKOUT-PREVIEW_v1.9.1_CODE-WRITING_20261110.md`, SHA-256 `ec9c50b49c4d19d45a4a545b3171b98bb8aeb26761036070c9cadabbde0bfddb`, 159766 bytes, 1627 lines. Line anchors (L#) refer to A1's own lines (line 1 = first line after A1's BEGIN marker).
- **Review type:** a fresh, independent FULL-PLAN review of A1 as a whole, not a confirmation of the CoS score and not a diff review.
- **Pass bar:** an explicit PASS requires a score >=95 AND no unresolved material or critical finding. A score >=95 is not automatically a PASS; REVISE at any score is acceptable. No outcome is expected.
- **Material defects only:** correctness, safety, permissions, execution. Cosmetics are non-scoring. External prerequisites (Eric creating a test project, secrets, YES gates) are not plan defects.

## 2. Status and honest distinctions
- **A2 (GB CoS 100/100 PASS on v1.9.1)** is the CoS score only. It does not bind you. A2 names exactly A1 (SHA above). v1.9.1 is v1.9 (A4, CoS 96 PASS, SHA `0434dfce…`) plus a scoped +163/-29 line change closing A4's D1 (grant needed a `users/{uid}` doc; A1 L288, L368, L1135) and D2 (RX live-SHA gate, post-deploy verify, rollback fallback; A1 L1391-1565), A4's advisory 1 (lock order created_at -> added_at -> epoch 0; A1 L454, L1143, L1148) and advisory 5 (admin `/subscription-status`; A1 L524-527). A1 Section 12 lists the changes. Review the WHOLE plan, not only these.
- **Counts:** NET-827 fail-fix track attempt 5 of 10; writer Code Writing try 2 of 4. Earlier: v1.6 CoS 84, v1.7 CoS 86 (A6), v1.8 CoS 85 (A5), v1.9 CoS 96 PASS (A4; never sent to SAG). An earlier, different-scope v1.2 plan had a SAG 96 PASS on 10 Nov; that does not transfer.
- **Plan-only:** A1 authorizes nothing. No code, deploy, Firestore or Firestore-rules change, Firebase Auth change, Stripe action (test or live), spend or merge is authorized by A1, A2 or this review. After a SAG PASS, Founder Eric's scoped typed YES is still required for each gated step. HOLDs `74611e05` (never deploy `c547b7a0`) and `41b8bd5f` (no live deploy, no merge to main, no live keys) stay in force; `origin/main` stays `9f04550a`; Stripe live stays OFF. The optional rules step RX (A1 9.4) is a production change needing its own YES naming HOLD `41b8bd5f`.
- **Source evidence:** A3 contains real, line-numbered excerpts extracted by the preparer from git `a3d7dca20fbbaf06a522205b22d0740b600de52b` (the commit A1 cites). Client Firebase config values in `firebase_options.dart` are redacted (marked). `origin/main` `9f04550a` is not in the clone, so nothing in A3 is from main. A4 records about 90 of the v1.9 citations spot-checked against this commit with 0 wrong; A2 records every new v1.9.1 citation checked. If you need a line A3 does not include, treat A1's citation as writer-asserted and say so; do not invent code.
- **Eric's open decisions (not defects):** lock order (A1 open question 13) and whether locked coins count toward the Beta Special 100-coin minimum (open question 16).

## 3. Eric's binding decisions (judge A1 against these)
Free 10 coins; Copper (pro) 11-100; Silver (numismatist) 101-249; Platinum (dealer) 250-500; Gold (estate) 501+ unlimited (JSON null + `unlimited: true`). Prices (cents, monthly/annual): pro 499/4999; numismatist 899/8999; dealer 1099/10900; estate 1599/15000. Christmas: 1795669260-1798261199 (26 Nov 2026 12:01 AM ET to 25 Dec 2026 11:59:59 PM ET), server-side, never early, annual only, no stacking. Beta Special: $30 one-time, >100 coins, unlimited 6 months, once ever, blocked at create with auto-refund backstop; at expiry overflow coins are locked (not viewable/editable) and never deleted; a basic CSV of all coins and items always available on any tier; lazy lock OK but every add/view/edit path checks expiry server-side. Partial refunds logged only; full refunds and lost disputes revoke. Non-US buyers allowed, USD only, Stripe Tax off, billing address auto. Preview = separate backend with test Firestore and Stripe test keys, never production. Synthetic testers ft-preview-01..04@numista.ai in production Auth for verification only, no production Firestore data, no stored passwords, deleted after Field Tester; nobody signs in on p7-gate. Unverified Stripe shapes and Christmas rounding accepted if fail-closed. pytest via project venv, BLOCKED if unavailable. Scripts must run on Windows PowerShell 5.1.

## 4. Whole-plan areas to cover
Session create (allowlist, price_data, discounts, idempotency, return URLs); webhook claim lease and fulfillment; user resolution; Beta Special and backstop refund; refunds/disputes ledger; limits and JSON; entitlement/effective limit; dedupe count; lock/unlock via top-level `locked_coins` (chunking, concurrency, restore to origin folder); add paths and by-id 403; client-SDK create limit; server-only storage map and the claim that no rules change is needed; CSV export (auth, ownership, injection guard); env_guard and the 22-row client inventory; bucket guard; PV-0..PV-6 scripts; tests (pytest, Jest emulator, import graph); hosting deploy and rollback; GL/LK go-live steps; optional RX (additive diff, backup and SHA check, deploy, rollback); open questions and risks.

## 5. Requested output (concise)
1. Integer score /100 and explicit disposition: PASS or REVISE.
2. Material/critical findings only, each with A1 line numbers, A3 code evidence where relevant, why it is material, and the minimal fix (or "none").
3. Six one-line checks with anchors: (a) payment/entitlement correctness; (b) lock/unlock/CSV versus Eric's decisions; (c) Firestore rules and permissions (no lock-out, server-only state); (d) preview isolation and secrets/Stripe-OFF safety; (e) PowerShell 5.1 scripts, tests and gates (including RX); (f) evidence honesty (citations vs A3) and no regression versus A4/A5.
4. Confirmation that you reviewed the full A1, with the exact A1 SHA-256 you reviewed.

## 6. Byte-exact embedding and extraction rule
Each artifact appears between a line `<<<BEGIN ARTIFACT id=... sha256=... bytes=... lines=... path=...>>>` and a line `<<<END ARTIFACT id=...>>>`. The artifact's exact bytes begin immediately after the newline that ends the BEGIN line and run for exactly `bytes` bytes; the END line begins immediately after them. No escaping or transformation was applied (UTF-8). `lines` counts newline characters. There are exactly 7 artifacts.

| ID | Role | Source path | SHA-256 | Bytes | Lines |
|---|---|---|---|---|---|
| A1 | Plan v1.9.1 (Code Writing) - EXACT ARTIFACT UNDER REVIEW | `/workspace/net827-claude/src/PLAN_NET-827_FAILFIX-B1B5_STRIPE-CHECKOUT-PREVIEW_v1.9.1_CODE-WRITING_20261110.md` | `ec9c50b49c4d19d45a4a545b3171b98bb8aeb26761036070c9cadabbde0bfddb` | 159766 | 1627 |
| A2 | GB CoS score record for v1.9.1 - 100/100 PASS (CoS only; NOT SAG) | `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\COS_SCORE_NET-827_FAILFIX-B1B5_v1.9.1_100_PASS_20261110.md` | `d3db8668de8554a9ca680a3b3c0ce03788835b3167ef5d342db59c768ce6f3ee` | 12141 | 166 |
| A3 | Real code excerpts, line-numbered, from git a3d7dca2 (packet-preparer extracted) | `(generated on box from /workspace/net827-claude/repo at a3d7dca2)` | `450fa2ccd7910aacf8f985a3159cf0dc8e033ae3820bc253e13adf3958623948` | 116163 | 2766 |
| A4 | GB CoS score record for v1.9 - 96/100 PASS (D1/D2 that v1.9.1 claims to close) | `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\COS_SCORE_NET-827_FAILFIX-B1B5_v1.9_96_PASS_20261110.md` | `3b98bff555460ad4224781ea089524203105a8feb123cdc44df1ca536fae04f3` | 21352 | 195 |
| A5 | GB CoS score record for v1.8 - 85/100 REVISE (regression reference: R1-R5) | `/workspace/net827-claude/` | `cbf4fb6cd0f8c657825d033b31c08fabc5ff7638e68a4cd604ae025e3505ec02` | 18288 | 117 |
| A6 | GB CoS score record for v1.7 - 86/100 REVISE (regression reference: N1-N3, Eric decisions) | `/workspace/net827-claude/` | `e824859910136284854c688cb2e2033b75f8bc0e8755f456be2a352cdbb33bba` | 17838 | 125 |
| A7 | CoS harvest review of Carbon v1.9 (do-not-copy X1-X12, gaps G1-G9; reference) | `/workspace/net827-claude/` | `653b3c8c225942529130cbdf4bf7671ece9127f78af23739643ed9f4849aeccb` | 30310 | 350 |

A2 and A4 are also on EDS_Laptop at the paths shown (SHA-256 verified by readback). A5-A7 are box copies under `/workspace/net827-claude/`.

## A1 - Plan v1.9.1 (Code Writing) - EXACT ARTIFACT UNDER REVIEW

<<<BEGIN ARTIFACT id=A1 sha256=ec9c50b49c4d19d45a4a545b3171b98bb8aeb26761036070c9cadabbde0bfddb bytes=159766 lines=1627 path=PLAN_NET-827_FAILFIX-B1B5_STRIPE-CHECKOUT-PREVIEW_v1.9.1_CODE-WRITING_20261110.md>>>
# NET-827 Stripe Checkout Preview Plan v1.9.1 (replaces v1.9, v1.8, v1.7 and all earlier versions)

Attempt: NET-827 fail-fix track attempt 5 of 10; writer Code Writing try 2 of 4. Base: v1.9 (CoS 96 PASS, SHA-256 `0434dfce1218a530842c1aa6f89707eedc90451ae4cb768beac8c226e3dfed70`); v1.9.1 changes only the four scoped items listed in Section 12. v1.9 base: v1.7 (CoS 86). Closes v1.7 record N1-N3, v1.8 record R1-R5 and advisories 1-8, v1.7 advisories A1-A7, and the nine "Remaining gaps" of the CoS harvest review of Carbon v1.9 (harvest file SHA-256 `653b3c8c225942529130cbdf4bf7671ece9127f78af23739643ed9f4849aeccb`). Carries over from Carbon v1.8 only: N2 (no synthetic-tester sign-in on p7-gate; HTTP-only checks against the preview backend), the preview-service-account-has-no-production-IAM check, and A1-A6.
Status: PLAN ONLY. Writing this plan performed no code, git, deploy, Firestore, Firestore-rules, Firebase Auth, Storage, Stripe, Cloud Run, GCS or Secret Manager action. All code reading was read-only at `a3d7dca20fbbaf06a522205b22d0740b600de52b`.
Gates: CoS 95 → full-plan SAG 95 on the exact same file SHA → Eric's typed scoped YES. Live payments need a further separate gate (Section 9, LK steps). The optional rules hardening step RX (Section 9.4) is a PRODUCTION change and needs its own scoped Eric YES that names HOLD `41b8bd5f`; NET-827 does not need it and does not run it.

Code-citation convention: every `file:line` below is a path under the repo root of the checkout at `a3d7dca2` (`numista_backend/...`, `numista_mobile/...`). The CoS copies in `src/tip/` are byte-identical (checked by SHA-256: `deps.py` ebcac530…, `main.py` 4c0bdbe6…, `payment_routes.py` e5c1571c…, `tier_gatekeeper.py` c361a2b3…, `firestore.rules` e650713b… = `numista_mobile/firestore.rules`).

## 0. Fixed facts and decisions

- Branch `p7-v8.9` only. `origin/main` stays `9f04550a45fa4da082ba8948c2d89a521a90fa45` (that commit is not in the box's shallow clone, so nothing in this plan relies on its contents). Base code `c547b7a0`; backend files are byte-identical at tip `a3d7dca20fbbaf06a522205b22d0740b600de52b`.
- Holds: `74611e05` (never deploy `c547b7a0`, not even as a rollback target); `41b8bd5f` (no live deploy, no merge to main, no live keys); addendum `c2b6ac93` is not active.
- Christmas code (Eric, binding; the code string is deliberately not written in this plan): from **26 Nov 2026 12:01:00 AM ET** to **25 Dec 2026 11:59:59 PM ET**. ET is EST (UTC-5) on both dates.
  - Start = 2026-11-26 05:01:00 UTC = epoch **1795669260** (check: 1795651200 = 26 Nov 00:00 UTC; +18000 s = 00:00 EST = 1795669200; +60 s = 1795669260).
  - End = 2026-12-26 04:59:59 UTC = epoch **1798261199** (matches the sandbox coupon `redeem_by`).
  - Both re-verified at plan time with Python `zoneinfo("America/New_York")` (offset −5:00 on both dates). Enforced server-side (Section 5); never active early. The code string itself never appears in the repo or this plan.
- Coin tiers (Eric, binding): Free 10 coins; Copper 11–100; Silver 101–249; Platinum 250–500; Gold unlimited (501+). Unlimited is JSON `null` plus `"unlimited": true`. Overflow coins are locked, never deleted.
- Beta Special (Eric, binding): $30 one-time, unlimited coins for 6 months, once per account ever (a refund never re-opens it). Blocked at checkout if the buyer has 100 coins or fewer; automatic refund as a backstop.
- Beta Special expiry (Eric, binding): coins over the limit are locked (not viewable or editable in the app) until upgrade, never deleted. A basic CSV of all coins and items, including locked ones, is always downloadable on any tier.
- Refunds (Eric, binding): partial refunds keep access (log only). Full refunds and lost disputes remove paid access.
- Buyers (Eric, binding): non-US buyers allowed; USD only; Stripe Tax off; `billing_address_collection="auto"`.
- Preview (Eric, binding): separate preview backend with its own test Firestore and Stripe **test** keys; never production `numista-backend`, never production Firestore or production Storage.
- Test users (Eric, binding): `ft-preview-01..04@numista.ai` in production Firebase Auth, verification only, no stored passwords, no production Firestore data, deleted after Field Tester.
- Unverified Stripe data shapes (Eric, binding): accepted; recorded in the first gated sandbox run; the code fails closed if they differ.
- **Who may use p7-gate during NET-827: no real users.** No human (not Eric, not beta testers, not the synthetic testers) signs in on the `p7-gate` web app while NET-827 is open. Testing is pytest (Section 7) plus scripted HTTP calls to the preview backend (Section 8). Reason: the p7-gate build sends API calls to the preview backend but its Firebase SDK still talks to production Firestore (`numista_mobile/lib/firebase_options.dart:53,63,71` pin `projectId: 'studio-9101802118-8c9a8'`), so a sign-in would mix production and test data.
- Stripe Tax stays off. `/catalog` and Live eBay Check stay public. Budgets are alerts only.
- No secrets, promo code strings, or invented SHAs/URLs/Stripe IDs/bucket names appear in this plan. Anything not known is written "UNKNOWN; record at execution time".
- Do not modify `melt_value_service.dart` or the catalog test. `numista_mobile/firebase.json` is not modified (it routes `/api/**` to `numista-backend` and holds the `/catalog` rewrites).
- **NET-827 makes no Firestore rules change.** The lock and every new server-only field are enforced on the server and stored only in new top-level collections that the current, unchanged rules already deny to every client (`numista_mobile/firestore.rules:345-348`, "Deny everything else"). Section 4.9 shows why this is sound. The rules hardening in Section 9.4 (RX) is optional, deferred to the go-live gate, and fully specified there.

### Price ladder (P1, kept from record; server is the only source of price)

| Tier | Internal key | Monthly (cents) | Annual (cents) | Coins |
|---|---|---|---|---|
| Copper | `pro` | 499 | 4999 | 11–100 |
| Silver | `numismatist` | 899 | 8999 | 101–249 (Eric decided) |
| Platinum | `dealer` | 1099 | 10900 | 250–500 |
| Gold | `estate` | 1599 | 15000 | 501 and up, unlimited |

Beta Special: $30 (3000 cents) one-time, `mode=payment`, 6 calendar months (`relativedelta(months=6)`), only for users with **more than 100 coins (101+)**. Eligibility checked server-side at session create and again at fulfillment.

## 0a. Plain-English summary for Eric

- **What this plan does:** it fixes the five checkout problems (B1–B5) and builds a test copy of the backend that only uses test money (Stripe test keys) and a test database. Nothing in it touches the live site, the live database or live payments.
- **Locked coins:** when a Beta Special runs out (or a refund or lost dispute drops a plan), the coins over the plan limit are moved into a sealed back room, like moving stock from the sales floor into a locked cage. Customers can't see or change them in the app, but nothing is thrown away. When they upgrade, every coin goes back on the exact shelf it came from. The basic CSV download always lists every coin and item, locked or not.
- **No rules change needed now:** the "sealed back room" is a storage area the live security rules already block for every user. So we do not have to touch the live rules to make the lock work. A small, optional tightening of the rules is written out for later (go-live), with its own YES, test, exact command and undo.
- **Double counting fixed:** some customers have the same coin stored in two places (under their email and under their account number). The count, the lock and the CSV now treat a coin that appears twice as one coin.
- **Test copy can't reach live data:** every place in the backend that opens the database or file storage now goes through one guard. The test copy refuses to start if it is pointed at the live project or a live storage bucket, and its service account has no permissions on the live project (checked by command before anyone uses it).
- **Who may use the preview web page:** nobody signs in on p7-gate during NET-827. All testing is done by script against the test backend.
- **Open questions only you can answer** are listed in Section 10 (for example which coins get locked first: today's code locks the newest).

## 1. Change lists

### 1a. v1.2 → v1.3 (retained)

1. Server-side tier allowlist and price table; `power_user`, `sovereign`, `family_estate`, legacy names rejected (B1).
2. uid/tier on `subscription_data.metadata`; customer→uid map; email-as-doc-id fallback removed; events never marked done without a user update (B2).
3. Grant only on `payment_status=='paid'` or allowlisted $0 F&F; amounts verified against server price (B3).
4. Idempotency key on session create, one active checkout per user, transactional event claim (B4).
5. `charge.refunded` and `charge.dispute.*` handled (B5).
6. Christmas start/end gate, annual-only, no stacking (C1).
7. Live-keys steps LK-1…LK-8 named, not run (K1).
8. Separate preview Cloud Run service (PX1).
9. Beta eligibility 101+ (PX2); preview URL recorded at deploy time (PX3); real-checkout tests separately gated (PX4).
10. `TIER_COIN_LIMITS` free=10, estate unlimited, JSON-safe (L1/L2).
11. Honest FT checks needing no Firestore writes.

### 1b. v1.6 → v1.7 (CoS D1-D8; retained unchanged)

D1 env guard + PV-3/PV-4; D2 customer map + subscription-metadata resolution, never default `pro`; D3 60 s lease; D4 one discount model (automatic Christmas, server-validated F&F promotion code, no stacking); D5 `amount_subtotal` + allowlisted coupon + 1-cent tolerance; D6 `stripe_payments` ledger-mapped refunds; D7 revoke only on a lost dispute; D8 real paths. Gold 501+ correction; 5:36 PM ET Eric decisions; v1.6 advisories 1-10.

### 1c. v1.7 → v1.9 (this version)

1. **Preview isolation, whole backend (v1.7 N1, v1.8 R3/R4, harvest H6/G7).** Every runtime Firestore client, Storage client and Firebase Admin initialisation reachable from `main.py` goes through `numista_backend/env_guard.py` (inventory with file:line in §4.11). Storage clients are wrapped so that, in preview, any production bucket name is refused. The production default bucket is the real `numista-uploads-studio-9101802118-8c9a8` (`numista_backend/main.py:342`). A pytest walks the `main.py` import graph and fails if any reachable module builds a data client outside `env_guard` (§7.3). PV-4 checks project-level and bucket-level IAM (§6.6).
2. **Preview app vs production Firestore (v1.7 N2; carried from v1.8).** Synthetic testers never sign in on p7-gate; checks are HTTP-only against the preview backend (§0, §6.3, §8). PV-4.5 checks production for stray synthetic data by uid and email and has a YES-gated delete limited to the four accounts (§6.6).
3. **Lock that works in the app without a rules change (v1.7 N3, v1.8 R1, harvest H2/G1/G3/G4/G9).** Locked coins are moved by the backend (Admin SDK) out of the client-readable coin folders into the new top-level collection `locked_coins/{owner_key}/coins/{coin_id}` (owner key = the uid or email of the folder the coin came from), which today's rules already deny to all clients (`numista_mobile/firestore.rules:345-348`). Client list queries stay unfiltered and keep working; locked coins are simply absent. Unlock puts each copy back in the exact folder it came from. No rules change, no app query change (§4.8, §4.9).
4. **Dedupe (v1.8 R2, harvest H3/H4).** Count, lock, unlock and CSV always read BOTH `users/{email}/coins` and `users/{uid}/coins` and treat one document id as one coin. Only coins are locked or counted; currency and wishlist are exported but never locked or counted (§4.8, §4.10).
5. **New server-only state is client-proof (found in this review).** `beta_special_until`, `beta_special_purchased`, `stripe_subscription_id`, `stripe_customer_id` (for revocation and the billing portal), `checkout_pending` and `dispute_review` live in the new top-level `entitlements/{uid}` document, also denied to clients by `firestore.rules:345-348`. Today only the keys in `_serverOnlyKeys()` (`firestore.rules:85-88`) are protected on `users/{id}`, so a field such as `beta_special_until` written there could be set by the user. `stripe_tier` stays on `users/{uid}` (already server-only). The billing-portal route stops trusting the client-writable `users/{id}.stripe_customer_id` (`numista_backend/routes/payment_routes.py:102-105`) (§4.9).
6. **Restored tests (v1.8 R5, harvest H9/H10/G2).** v1.7's §4.8 test list is back, plus cross-user CSV, migrated-user dedupe, chunking over 250 coins, legacy email-path lock/unlock round trip, 403 `LOCKED_PENDING_UPGRADE`, and rules emulator tests in the existing Jest file run against the UNCHANGED rules file (§7.1, §7.2).
7. **Advisories:** v1.7 A1-A6 (carried from v1.8: ledger skip when no payment intent; missing `created_at` handled and errors fail closed; `session_created` window; typed `beta_special_until`; tab/CR CSV prefix; PV-6 `-Action` parameter); v1.8 advisories 1-8 (p7-gate users, PV-4.5 uids + delete, bucket IAM, password typed at run time, `get_user_tier` signature, open question 4 closed, heading order, PV-6 `-Action`).
8. **Harvest "Do not copy" list obeyed:** no whole-file rules text, no rules text at all in NET-827; tier limits exactly as v1.7; lock/unlock rewritten with chunking and origin paths; no rules deploy in NET-827 (the go-live RX step uses a byte-exact live-ruleset backup and `Invoke-Native`); PV-4.5/PV-6 use the PV-5 temp-file pattern with the pattern guard; v1.7 env_guard Stripe checks kept; v1.7 pytest/venv block kept; no unverified SHA; Jest, not Mocha.
9. **Route path corrected:** the checkout route is `POST /api/stripe/create-checkout-session` (router prefix `/api/stripe`, `numista_backend/routes/payment_routes.py:26,32`), not `/api/payment/...` as v1.8 §8 said.

## 2. Closure table

### 2a. Original findings and v1.6 record (all closed in v1.7; kept unchanged)

| ID | Item | Closed by | Section |
|---|---|---|---|
| B1 | Price/tier from client string | `PURCHASABLE` allowlist + server price table; 400 before any Stripe call | 4.1 |
| B2 | User/tier resolution | customer map written at grant (now in server-only docs); subscription metadata; no email fallback; never default `pro` | 4.3 |
| B3 | Grant without payment proof | paid + `amount_subtotal` + allowlisted coupon + 1-cent tolerance | 4.3 |
| B4 | Idempotency/race | idempotency key; transactional claim with 60 s lease | 4.1, 4.2 |
| B5 | Refund/dispute | ledger-mapped full-refund revoke; partial log only; revoke only on `lost` | 4.4 |
| C1 | Christmas leak | server clock gate at create and webhook; annual only; coupon id in env only at LK-8 | 5 |
| K1 | Live keys | LK-1…LK-8, not run | 9.3 |
| L1/L2 | Free 10; Gold unlimited JSON-safe | `TIER_COIN_LIMITS` exactly as v1.7; `null` + `unlimited: true` | 4.5 |
| P1 | Price ladder | §0 table, `price_data` | 0, 4.1 |
| U1 | US-only | withdrawn by Eric; non-US, USD, Tax off, billing auto | 4.1 |
| X1-X5 | F&F flag, tests, unwired second checkout, Dart allowlist, return URLs | unchanged from v1.7 | 3, 4.1, 4.6, 4.7, 7 |
| PX1-PX4 | Preview isolation, Beta 101+, preview URL, gated real checkout | v1.7 + this version's full guard | 0, 6, 8 |
| D1-D8 | v1.6 deductions | unchanged v1.7 closures; D1 residual finished by N1 below | 4.x, 6 |
| v1.6 adv. 1-10 | Gold 501, quoted placeholders, channel list, NET-816 sequencing, `checkout_pending`, free=20 tests, `power_user` inf, cancel lock, LK-3 service, header time | unchanged v1.7 closures | 4.1, 4.5, 9 |

### 2b. v1.7 record (86): N1-N3 and advisories

| ID | Deduction / advisory | How v1.9 closes it | Section |
|---|---|---|---|
| N1 (−5) | Preview backend still reaches production (`main.py:349/352`, `subaccount_routes.py:26`, CSV client unspecified) | every reachable data client routed through `env_guard` (full inventory incl. `main.py:349,352,358,4430,9606`, `subaccount_routes.py:26`); bucket guard; `main.py` coin routes in scope; CSV uses the guarded client; PV-4 project + bucket IAM check; import-graph pytest | 3, 4.11, 6.1, 6.6, 7.3 |
| N2 (−5) | Preview app writes production Firestore directly | no human signs in on p7-gate; synthetic testers HTTP-only via scripted client; PV-4.5 read-only check by uid and email + YES-gated delete of the four accounts' docs only | 0, 6.3, 6.6, 8 |
| N3 (−4) | "Locked in the app" not deliverable; email-keyed coins missed | locked coins moved to client-denied `locked_coins/{owner_key}/coins/{coin_id}` (denied by current rules `firestore.rules:345-348`, no rules change); both coin folders always read and deduped by id; CSV includes locked + both folders + currency + wishlist; client-direct adds reconciled server-side | 4.8, 4.9, 4.10 |
| A1 | Ledger key when no payment intent | skip ledger write at grant when PI is None; `invoice.paid` writes it | 4.3 |
| A2 | `lock_overflow_coins` skips coins without `created_at`; swallows errors | missing/unparseable `created_at` = epoch 0; lock/unlock raise; callers fail closed | 4.8 |
| A3 | `decide_grant` lacks `created` | `session_created` checked against the window | 4.3 |
| A4 | `beta_special_until` type | stored as Firestore Timestamp in `entitlements/{uid}`; `to_epoch` parses Timestamp/number/ISO; parse failure = expired | 4.8 |
| A5 | CSV prefix for tab/CR | `=`, `+`, `-`, `@`, tab, CR prefixed with `'` | 4.10 |
| A6 | PV-6 hand edit; webhook endpoint step | PV-5/PV-6 script takes `-Action create|delete`; PV-2b names the test webhook endpoint creation | 6.4, 6.5 |
| A7 | Header attempt count | header says attempt 4 of 10 | header |

### 2c. v1.8 record (85): R1-R5 and advisories

| ID | Deduction / advisory | How v1.9 closes it | Section |
|---|---|---|---|
| R1 (−6) | Rules change would lock every user out of their own list queries on live; create rule undecided; no emulator tests, deploy, rollback; production change not named | **no rules change in NET-827.** Client list queries and the rules file stay exactly as they are; locked coins leave the readable folders (Option a, top-level client-denied collection). Create limit: server routes reject over-limit adds (403); client-SDK creates (allowed by `firestore.rules:55-58`, rules can't count) are reconciled server-side at the next server touch (moved to the locked collection, newest first). Emulator tests against the unchanged file prove owner list still works and locked/entitlement collections are denied. Optional go-live hardening RX is additive only, with emulator tests, byte-exact live backup, exact deploy command and runnable rollback, and is named a PRODUCTION change under HOLD `41b8bd5f` needing its own scoped Eric YES | 0, 4.8, 4.9, 7.2, 9.4 |
| R2 (−3) | Dual-path counting double-counts migrated users; currency/wishlist wrongly locked | union of both folders deduped by document id (no migration shortcut); coins only counted/locked; currency/wishlist exported only; pytest 200 identical coins in both folders = 200, Silver locks 0, CSV 200 coin rows | 4.8, 4.10, 7.1 |
| R3 (−3) | Invented bucket `numista-vault-user-content` | real production default `numista-uploads-studio-9101802118-8c9a8` (`main.py:342`); preview must set `USER_CONTENT_BUCKET` to a different bucket; guard refuses every production bucket found in code; PV-1 creates the preview bucket; PV-3 sets it with a placeholder guard; PV-4 checks it; pytest for default and refusal | 4.11, 6.1, 6.4, 6.6, 7.1 |
| R4 (−2) | Unguarded clients (`brain_processor.py`, `services/canon_sync_service.py`, `numista_scraper`, `routes/deps.py` storage, plain storage clients in `main.py`, `estate_routes.py`, `support_routes.py`) | each one listed with file:line and routed through `env_guard`; production-only admin/scraper features also return 503 in preview; Firebase Admin default app initialised for Auth only; `firebase_admin.firestore.client()` forbidden in runtime code; import-graph pytest | 3, 4.11, 7.3 |
| R5 (−1) | v1.7 lock/CSV tests dropped (incl. unauthenticated CSV) | v1.7 list restored verbatim plus cross-user, dedupe, chunking, legacy round trip, 403 code, emulator cases | 7.1, 7.2 |
| v1.8 adv. 1 | Who may use p7-gate | nobody signs in on p7-gate during NET-827 | 0, 6.3 |
| v1.8 adv. 2 | PV-4.5 uids and delete script | checks `users/{email}` and `users/{uid}` and all their subcollections; YES-gated `-Action delete` limited to those 8 paths | 6.6 |
| v1.8 adv. 3 | Bucket-level IAM not checked | PV-4 checks bucket IAM on every production bucket named in code; folder/org grants noted as not covered | 6.6 |
| v1.8 adv. 4 | Scripted client password | typed at run time (`Read-Host -AsSecureString`), held in memory, never written | 8 |
| v1.8 adv. 5 | `effective_limit` signature | `get_user_tier(user_profile)` stays one-argument and unchanged; Beta handled in `effective_limit` | 4.8 |
| v1.8 adv. 6 | Open question 4 conflicts with no sign-in | closed: no in-app tester button; scripted client only | 10 |
| v1.8 adv. 7 | Heading order | sections in order | all |
| v1.8 adv. 8 | PV-6 hand edit | `-Action` parameter | 6.5 |

### 2d. Harvest review "Remaining gaps" (Carbon v1.9 harvest)

| Gap | What was open | How v1.9 closes it | Section |
|---|---|---|---|
| G1 | Rules: incremental edit only | NET-827 has no rules edit at all. RX (optional, go-live) is additive only: `'locked_coins'` added to both wildcard exclusion lists, an explicit deny block, `locked_pending_upgrade` blocked on coin create/update, extra server-only keys; every other line byte-identical; exact diff given | 4.9, 9.4 |
| G2 | Emulator tests in the existing Jest file, incl. wildcard, entitlement, `is_demo`, unfiltered list | `numista_mobile/firestore.rules.test.js` extended; cases run against the unchanged file for NET-827 and against the RX file for RX | 7.2 |
| G3 | Rules deploy step (real backup, `Invoke-Native`, runnable rollback, named production change, sequencing) | RX: read-only REST backup of the live ruleset written byte-exact, SHA-256 compared with `e650713b…`; `Invoke-Native`; runnable rollback block; named PRODUCTION change under HOLD `41b8bd5f`; sequenced after go-live of the backend | 9.4 |
| G4 | Lock/unlock implementation (union, dedupe, origin path, chunked, set-then-delete, idempotent, order, tests) | `lock_overflow_coins`/`unlock_user_coins` spec: union + dedupe by id, one locked doc per source copy with its origin path, batches of at most 200 copies = 400 writes (< 500), set and delete in the same atomic batch, re-run safe, restore never overwrites; order = today's (newest locked) as an OPEN QUESTION; pytest for >250 overflow and legacy round trip | 4.8, 7.1, 10 |
| G5 | `TIER_COIN_LIMITS` / `get_user_tier` | exactly v1.7 §4.5; `get_user_tier` unchanged; Beta in `effective_limit` | 4.5, 4.8 |
| G6 | Existing `locked_pending_upgrade == true` coins in production | the new code never uses that flag for access; a read-only count (PV-0) records how many exist; unlock clears the flag to `false` when it restores a user; any production cleanup is a separate go-live YES | 4.8, 6.4 |
| G7 | Import-graph-scoped client test; `support_routes` to the Firestore getter | `tests/test_no_unguarded_clients.py` walks the `main.py` import graph; `support_routes.py:38` (a Firestore client) → `env_guard.get_firestore()` | 4.11, 7.3 |
| G8 | env_guard Stripe checks; production mode | v1.7 `load_data_config`/`check_stripe_key` kept; bucket function added; production's `STRIPE_EXPECTED_MODE` is set from a recorded read-only check at the go-live gate (GL-1), never guessed | 6.1, 9.3 |
| G9 | Direct request for a locked coin should be 403 `LOCKED_PENDING_UPGRADE`, not 404 | coin detail/edit routes look in `locked_coins/{uid|email}/coins/{coin_id}` (403, no coin data) when the coin is not in the source folder | 4.8 |

### 2e. CoS steering directions for this attempt (10 Nov 7:18 PM ET)

| # | Direction | Done? | Section |
|---|---|---|---|
| 1 | Use the harvest "Reusable" list (no p7-gate sign-in; separate `locked_coins`; real bucket default; client guard list incl. `support_routes.py` fix; dedupe by id, coins only; restored tests) | Yes | 0, 4.8, 4.10, 4.11, 6.1, 7 |
| 2 | Obey "Do not copy" | Yes (see 1c item 8) | 1c |
| 3 | Rules: ADD only, rest byte-identical, current SHA-256 and rollback, `locked_coins` in the catch-all exclusions, users never write their own account entitlements | Yes, as the optional go-live step RX; NET-827 itself needs no rules change (preferred server-side route allowed by the assignment) | 4.9, 9.4 |
| 4 | Tier limits exactly v1.7; unlimited is `null` | Yes | 4.5 |
| 5 | Lock/unlock: both folders, dedupe, batches ≤ 500 writes, restore to source folder | Yes | 4.8 |
| 6 | Lock order: keep today's (newest locked), cite code, OPEN QUESTION | Yes (`numista_backend/tier_gatekeeper.py:327-334`) | 4.8, 10 |
| 7 | Close every harvest gap and add to the closure table | Yes (2d) | 2d |

### 2f. v1.9 record (CoS 96 PASS): items fixed in v1.9.1

| ID | Deduction / advisory | How v1.9.1 closes it | Section |
|---|---|---|---|
| D1 (−2) | Grant needs a `users/{uid}` doc nothing guarantees | checkout create ensures `users/{uid}` with `set({}, merge=True)` in the `checkout_pending` transaction (no fields written, no entitlement field); the grant proceeds without the doc when `checkout_pending.session_id` matches or `firebase_auth.get_user(uid)` succeeds, and its merge writes create the doc; unproven uid → retry, never a grant; pytest for email-only users (Silver, Beta, F&F), deleted doc, unknown uid | 4.1, 4.3, 7.1 |
| D2 (−2) | RX deploy does not confirm the live SHA; post-deploy step can overwrite the backup | backup written to a temp name and kept only if SHA = `e650713b…`, an existing backup never overwritten; deploy block re-reads the live ruleset and compares its SHA immediately before `firebase deploy`, and checks the backup SHA; scripted post-deploy verify in its own folder against the RX SHA; rollback falls back to the SHA-checked git blob `a3d7dca2:numista_mobile/firestore.rules` and verifies live afterwards | 9.4 |
| Adv. 1 | Lock order for client-created coins | sort time = `created_at`, else `added_at`, else epoch 0 (fields verified at `main.py:2747`, `tier_gatekeeper.py:327`, `roll_entry_dialog.dart:379`, `wishlist_screen.dart:983`); roll-wizard fixture test; Q13 stays open for Eric | 4.8, 7.1, 10 |
| Adv. 5 | `/subscription-status` admin path | own lookup reconciles the caller only; admin lookup of another user is read-only (no reconcile, no write) and returns the stated field set for the one queried key, with `admin_view`/`reconciled`/`owner_keys`; non-admin other → 403 | 4.8, 7.1 |

## 3. File-by-file scope

All paths verified at `a3d7dca2`. The builder works in an isolated worktree (§9) and changes only these files.

| File | Change |
|---|---|
| `numista_backend/env_guard.py` (new) | data config, Stripe key check, guarded Firestore/Storage providers, bucket guard, Firebase Admin Auth-only init (§6.1) |
| `numista_backend/routes/payment_routes.py` | rewrite checkout/webhook/portal per §4.1-§4.4; `/subscription-status` calls `enforce_entitlement`, returns JSON-safe `coin_limit`/`unlimited`, `locked`, `restore_conflicts`; JSON-safe `power_user` allowance |
| `numista_backend/schemas/payment_schemas.py` | `tier: Literal[...]` of purchasable keys; `interval: Literal["month","year"]`; `beta_special: bool = False`; `promo: Optional[str]` (max 64) |
| `numista_backend/tier_gatekeeper.py` | init via `env_guard` (`:13-29`); `TIER_COIN_LIMITS` per §4.5 (`:41-50`); `check_and_enforce_coin_limit` uses `within_limit` (`:242-244`); new `to_epoch`, `load_entitlement_profile`, `effective_limit`, `entitlement_ok`, `count_unique_coins`, `enforce_entitlement`, `require_can_add`; `lock_overflow_coins`/`unlock_user_coins` rewritten (`:325-351`) per §4.8; `get_coin_count` (`:160-168`) raises instead of returning 0; `get_user_tier` and `create_upgrade_checkout_session` untouched |
| `numista_backend/stripe_config.py` | call `env_guard.check_stripe_key` when a key is present (§6.1) |
| `numista_backend/routes/deps.py` | rows 1-3 of §4.11 |
| `numista_backend/main.py` | rows 5-11 and 17-22 of §4.11; mount the export router; add checks at the add paths and by-id routes listed in §4.8; `/api/collection/count` (`:8722`) calls `enforce_entitlement` |
| `numista_backend/routes/export_routes.py` (new) | CSV export (§4.10) |
| `numista_backend/routes/subaccount_routes.py` | row 15 |
| `numista_backend/routes/support_routes.py` | row 16 |
| `numista_backend/routes/estate_routes.py` | row 12 |
| `numista_backend/routes/import_routes.py` | row 13; add checks at `:76-118`, `:236-242` |
| `numista_backend/routes/feedback_callable_route.py` | row 14 |
| `numista_backend/routes/cert_routes.py`, `routes/morgan_routes.py`, `routes/scan_routes.py`, `routes/grade_review_routes.py`, `services/transfer_service.py` | add check / by-id 403 lookup at the lines listed in §4.8 only |
| `numista_backend/brain_processor.py` | row 17 |
| `numista_backend/services/canon_sync_service.py` | row 18 |
| `numista_backend/numista_scraper/storage.py`, `numista_scraper/scrapers.py`, `numista_scraper/config.py` | rows 19-21 |
| `numista_backend/tests/test_net827_checkout.py` (new) | §7.1 checkout/webhook/portal cases |
| `numista_backend/tests/test_net827_entitlement.py` (new) | §7.1 count/lock/unlock/add/by-id cases |
| `numista_backend/tests/test_net827_export.py` (new) | §7.1 CSV cases |
| `numista_backend/tests/test_env_guard.py` (new) | §7.1 guard cases |
| `numista_backend/tests/test_no_unguarded_clients.py` (new) | §7.3 import-graph check |
| `numista_backend/test_tier_gatekeeper.py` | existing "limit = 20" assumptions (around `:195`) updated to 10 and the Silver/Gold limits |
| existing tests that patch replaced names (known: `tests/test_idor_fixes.py:480` patches `routes.payment_routes.get_coin_count`; `tests/test_tier_gatekeeper_beta.py`, `tests/test_stripe_auth.py`) | updated only as needed to the new names/behaviour; each listed in the commit message |
| `numista_mobile/firestore.rules.test.js` | tests only (§7.2); `numista_mobile/firestore.rules` itself is **not** changed in NET-827 |
| `numista_mobile/lib/services/stripe_service.dart` | allowlist (§4.7) + `refreshEntitlement()` |
| `numista_mobile/lib/screens/base_layout.dart` | one fire-and-forget `StripeService.refreshEntitlement()` call in `initState` (`:196-197`) |
| Not touched | `numista_mobile/firestore.rules`, `numista_mobile/firebase.json`, `melt_value_service.dart`, catalog test, `create_upgrade_checkout_session` (X3), `scan_service/`, standalone scripts |

Any other existing test that fails after the change is fixed in the same commit and listed in the commit message; if fixing it needs a non-test file outside this list, stop and report.

## 4. Code specs

### 4.1 Allowlist, prices, session create (B1, P1, U1, X5, B4) — unchanged from v1.7 except the two storage locations marked §4.9

```python
import hashlib
import time
from typing import Optional

PURCHASABLE = {
    "pro":         {"month": 499,  "year": 4999,  "label": "Copper"},
    "numismatist": {"month": 899,  "year": 8999,  "label": "Silver"},
    "dealer":      {"month": 1099, "year": 10900, "label": "Platinum"},
    "estate":      {"month": 1599, "year": 15000, "label": "Gold"},
}
BETA_SPECIAL_CENTS = 3000
BETA_MIN_COINS_EXCLUSIVE = 100   # eligible only if coin_count > 100
XMAS_START = 1795669260          # 26 Nov 2026 00:01 America/New_York
XMAS_END = 1798261199            # 25 Dec 2026 23:59:59 America/New_York


def resolve_price(tier: str, interval: str) -> int:
    if tier not in PURCHASABLE or interval not in ("month", "year"):
        raise ValueError("tier_not_purchasable")
    return PURCHASABLE[tier][interval]


def checkout_idempotency_key(uid: str, tier: str, interval: str, bucket: int) -> str:
    raw = f"{uid}|{tier}|{interval}|{bucket}"
    return "co_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:40]


def time_bucket(now: Optional[float] = None, seconds: int = 300) -> int:
    return int((now if now is not None else time.time()) // seconds)
```

Session create rules:
- Auth required via `get_current_user`; uid comes from the token, never the body.
- Reject (HTTP 400) any `tier` not in `PURCHASABLE` before any Stripe call. Reject `beta_special` (4xx) unless the server-counted coins are more than 100 (503 if the count cannot be read; never default to eligible), and reject with 409 if `entitlements/{uid}.beta_special_purchased` is already true (server-only document, §4.9). Coins are counted with the deduped `count_unique_coins` (§4.8).
- Use `price_data` with `unit_amount` from `resolve_price`; `recurring={"interval": interval}` for subscriptions; `mode="payment"` for Beta Special with one-time `price_data`.
- `allow_promotion_codes=False`. Buyers never type a code on the Stripe page. Discounts are decided only by the server (D4), at most one per session, never stacked:

```python
def _coupon_id_of(pc):
    """Coupon id of a Stripe PromotionCode; tolerates both API shapes."""
    c = pc.get("coupon")
    if c is None:
        c = (pc.get("promotion") or {}).get("coupon")
    return c if isinstance(c, str) else (c or {}).get("id")


def lookup_ff_promotion(stripe_mod, code, ff_coupon_id):
    """Return the promotion-code id if `code` is an active F&F promotion code, else None."""
    result = stripe_mod.PromotionCode.list(code=code, active=True, limit=1)
    for pc in result.data:
        if _coupon_id_of(pc) == ff_coupon_id:
            return pc.get("id")
    return None


def pick_discount(now, interval, beta_special, ff_promotion_id, xmas_coupon_id):
    """Return (kind, discount_param). kind is 'none', 'ff' or 'xmas'."""
    if beta_special:
        return "none", None
    if ff_promotion_id is not None:
        return "ff", {"promotion_code": ff_promotion_id}
    if interval == "year" and XMAS_START <= now <= XMAS_END and xmas_coupon_id:
        return "xmas", {"coupon": xmas_coupon_id}
    return "none", None
```

  - **Christmas (model a, automatic):** on every `interval == "year"` subscription session created inside `XMAS_START..XMAS_END` the server attaches the Christmas coupon. There is no request field for it, so nothing can be claimed early, and monthly sessions simply never receive it (no 400 rule is needed). Beta Special never receives it.
  - **F&F (server-validated promotion code):** the optional request field `promo` is looked up with `lookup_ff_promotion`. If it is not an active promotion code of the allowlisted F&F coupon, the request fails with 400 before any session is created. If valid, the session gets `discounts=[{"promotion_code": <id>}]`. Passing the promotion code (not the bare coupon) keeps Stripe's `max_redemptions` cap (Eric created it with 500) enforced by Stripe. F&F works on monthly and annual, and wins over Christmas (no stacking). Beta Special ignores `promo`.
  - Coupon and promotion-code ids come from env settings (names UNKNOWN; record at execution time). No code strings appear in the repo or this plan.
  - The chosen `kind` is written to `metadata.discount_kind` so the webhook can check it.
- `client_reference_id=uid`; `metadata={"user_uid": uid, "target_tier": tier, "interval": interval, "discount_kind": kind}`; for subscriptions also `subscription_data={"metadata": {same}}` (so later invoice/subscription events carry uid and tier).
- Non-US billing addresses are allowed (Eric, 10 Nov 5:14 PM ET; supersedes the earlier US-only answer). Set `billing_address_collection="auto"`. Stripe Tax stays off. USD pricing for all buyers; foreign tax/legal obligations are not assessed here (open risk, §10).
- Idempotency: pass `idempotency_key=checkout_idempotency_key(...)` as a request option. One active checkout per user: store `checkout_pending={session_id, expires_at}` on the server-only `entitlements/{uid}` document via transaction (§4.9); set the Checkout `expires_at` to now + 1860 s. A second create while `checkout_pending` is unexpired returns the existing session URL or 409. `checkout_pending` is cleared on `checkout.session.completed`, `checkout.session.expired` and `checkout.session.async_payment_failed`, and is ignored once its `expires_at` has passed.
- **Account doc at create (v1.9.1 D1):** in the same transaction that writes `checkout_pending`, the server ensures `users/{uid}` exists with `set({}, merge=True)` (Admin SDK, guarded client; uid from the verified token only). No field is written, so no entitlement field (`stripe_tier`, `tier`, `beta_tester`, `admin`, `power_user`, `creation_timestamp` or any other) is touched, and every existing field on that doc (e.g. the sort preference the app writes at `numista_mobile/lib/screens/my_collection_screen.dart:359-362`) is preserved. Reason: many accounts have only `users/{email}` (`numista_mobile/firestore.rules:69-73`); subcollection writes under `users/{uid}/…` do not create the parent doc; the grant writes `users/{uid}` (§4.3). If this write fails, the create returns 503 and no Stripe session is created.
- Return URLs (X5): `success_url`/`cancel_url` built from an allowlisted origin set (production `https://numista.ai` and the p7-gate preview URL recorded at deploy time, UNKNOWN now); a request `Origin` not in the set falls back to the production origin. Default return URL `https://numista.ai/#/settings`.
- Stripe Tax off (no `automatic_tax`).

### 4.2 Event claim with lease (B4, D3) — unchanged from v1.7

```python
import time
from google.cloud import firestore

LEASE_SECONDS = 60


def claim_event(snap_dict, now):
    """Pure decision: 'claim', 'skip_done' or 'lease_active'."""
    if snap_dict is None:
        return "claim"
    status = snap_dict.get("status")
    if status == "done":
        return "skip_done"
    if status == "processing" and now - float(snap_dict.get("ts", 0)) < LEASE_SECONDS:
        return "lease_active"
    return "claim"          # stale lease, retry or failed


@firestore.transactional
def claim_event_txn(transaction, ref, now):
    snap = ref.get(transaction=transaction)
    decision = claim_event(snap.to_dict() if snap.exists else None, now)
    if decision == "claim":
        transaction.set(ref, {"status": "processing", "ts": now}, merge=True)
    return decision
```

Caller: `skip_done` returns 200; `lease_active` returns HTTP 500 (Stripe redelivers later); `claim` proceeds. Phase 2 sets `status` to `done` only after the Firestore writes succeeded; on a retryable problem set `retry` and return 500; on a permanent problem set `failed`, log, and return 200 so Stripe stops retrying. Pytest covers a second claim inside the lease (`lease_active`), a stale lease (`claim`), and a done event (`skip_done`).


Today's code this replaces (for the builder): `numista_backend/routes/payment_routes.py:46-75` takes any `req.tier`, hard-codes 2900/499 cents, sets `allow_promotion_codes=True` and fixed return URLs; `:196-202` marks idempotency by existence only; `:221` defaults the tier to `"pro"`; `:210` falls back to the email as the user key. All replaced by §4.1-§4.4.
### 4.3 Webhook fulfillment (B2, B3, D2, D5; A1, A3 carried from v1.8)

```python
def discount_coupon_id(full_session):
    """Coupon id from a Session retrieved with expand=['total_details.breakdown']."""
    try:
        discounts = full_session["total_details"]["breakdown"]["discounts"]
        if not discounts:
            return None
        return discounts[0]["discount"]["coupon"]["id"]
    except (KeyError, TypeError, IndexError):
        return None


def decide_grant(session, price_cents, discount_kind, coupon_id, allowed, session_created=None):
    """Return (ok, reason). `allowed` maps 'xmas'/'ff' to the allowlisted coupon ids from env.
    `session_created` is checked against Christmas window if discount_kind == 'xmas'."""
    status = session.get("payment_status")
    subtotal = session.get("amount_subtotal")
    total = session.get("amount_total")
    if subtotal != price_cents or total is None:
        return False, "subtotal_mismatch"
    if discount_kind == "none":
        return (status == "paid" and total == price_cents), "no_discount_total"
    if status not in ("paid", "no_payment_required"):
        return False, "not_paid"
    if coupon_id is None or coupon_id != allowed.get(discount_kind):
        return False, "coupon_not_allowlisted"
    if discount_kind == "ff":
        return total == 0, "ff_total"
    # Christmas: verify session created inside window (Advisory A3)
    # Fail closed: a Christmas grant needs the session's own `created` time (v1.9 tightening of v1.8)
    if session_created is None or not (XMAS_START <= session_created <= XMAS_END):
        return False, "xmas_outside_window"
    # Christmas: Stripe computes the 50 percent; accept its rounding within 1 cent
    return (0 < total <= price_cents and abs(total * 2 - price_cents) <= 1), "xmas_total"
```
Rules:
- `price_cents` is recomputed server-side from `metadata.target_tier` and `interval` (never from the event amount). The plan does not compute the discounted total itself, so Copper (2499.5) and Silver (4499.5) half-cent results are accepted whichever way Stripe rounds (tolerance 1 cent, checked against `amount_subtotal`). Beta Special uses 3000 with kind `none`.
- `session_created` is the Session's `created` (epoch seconds) from the re-retrieved Session; for kind `xmas` a missing value fails closed (A3).
- The Session is re-retrieved with `expand=["total_details.breakdown"]` to read the applied coupon id. If the coupon id cannot be read when a discount was expected, do not grant: mark the event `failed` and log. The Stripe response shape (`total_details.breakdown.discounts[].discount.coupon.id`, and the promotion-code coupon field) is not verified in this plan; it is recorded in the gated sandbox step (§8) and `decide_grant` fails closed if it differs (Eric accepted).
- Tier from metadata must be in `PURCHASABLE`; otherwise no grant. **A tier is never defaulted** (today's `"pro"` default at `numista_backend/routes/payment_routes.py:221` is removed).
- User resolution for `checkout.session.completed` and async events: `client_reference_id`, then `metadata.user_uid`. **No email fallback** (today's `payment_routes.py:210` fallback is removed). If no `users/{uid}` doc exists (v1.9.1 D1; normally impossible after the create-time write above, e.g. a session made before D1 shipped or a doc deleted since): the grant still proceeds when the uid is proven by `entitlements/{uid}.checkout_pending.session_id == session.id`, or else by `firebase_auth.get_user(uid)` succeeding; the grant transaction's merge writes then create `users/{uid}`. Only if neither proves the uid: log, set `retry`, return 500 (never `done`, never a grant to an unproven uid). A paying customer whose account exists therefore always gets access.
- **Grant transaction** (single Firestore transaction on the guarded client):
  - `users/{uid}`: set `stripe_tier` (already a server-only key, `numista_mobile/firestore.rules:85-88`), `subscription_status="active"`, `grace_period_until=None`.
  - `entitlements/{uid}` (server-only, §4.9): set `stripe_subscription_id`, `stripe_customer_id`; clear `checkout_pending`.
  - `stripe_customers/{customer_id}` = `{uid}` (server-only top-level collection, §4.9).
  - Ledger `stripe_payments/{payment_intent_id}` = `{uid, kind: "subscription"|"beta", tier, subscription_id, granted: true}` **only when `payment_intent` is present**; for subscription sessions where it is None at completion, skip it and rely on `invoice.paid` (A1).
  - After commit, call `unlock_user_coins(uid, email)` up to the new effective limit (§4.8), so an upgrade returns previously locked coins to their original folders. If unlock raises, the event is set `retry` and returns 500 (the grant already committed is idempotent on redelivery).
- **Later subscription events** (`invoice.paid`, `customer.subscription.updated`, `customer.subscription.deleted`) have no session fields: uid comes from `stripe_customers/{customer}`; if missing, retrieve the subscription by id and use `subscription.metadata.user_uid`; if still unknown, set `retry`, return 500. Tier from `subscription.metadata.target_tier`, validated against `PURCHASABLE`; missing/invalid → change nothing, `failed`, log.
  - `invoice.paid`: if `status == "paid"`, re-affirm `stripe_tier` and write a ledger entry for the invoice's payment intent (newer API versions may nest it under `invoice.payments`; unverified shape, recorded in §8, fail closed if absent).
  - `customer.subscription.updated`: `active`/`trialing` set the tier; `canceled`/`unpaid` are handled as a cancel; `past_due` only logs.
  - `customer.subscription.deleted`: cancel (below).
  - `invoice.payment_failed`: keep today's 3-day grace bookkeeping (`payment_routes.py:227-232`); no lock, no revoke.
- Pytest includes an `invoice.paid` and a `subscription.updated` event with no session fields, resolving through the map, then the subscription metadata, then failing closed.
- `checkout.session.async_payment_succeeded` grants; `async_payment_failed` grants nothing and clears `checkout_pending`; `checkout.session.expired` clears `checkout_pending`.
- **Beta Special:** re-check coins > 100 at fulfillment with `count_unique_coins` (§4.8). If 100 or fewer, or if `entitlements/{uid}.beta_special_purchased` is already true: do not grant and **automatically refund** (backstop; the primary control is the block at create). Backstop: `stripe.Refund.create(payment_intent=<pi from session>, idempotency_key="refund_" + session_id)`; log; ledger entry with `granted: false`; record `beta_refund_issued` on the event. If the count cannot be read at fulfillment, set `retry` and return 500 (never grant on an unknown count). On grant, in the transaction: `entitlements/{uid}.beta_special_until = now + relativedelta(months=6)` stored as a Firestore Timestamp (tz-aware UTC datetime), `beta_special_purchased = true` (permanent; refunds and expiry never clear it).
- **Cancellation** (`subscription.deleted`, or `updated` to `canceled`/`unpaid`): only if `entitlements/{uid}.stripe_subscription_id` equals the cancelled subscription, clear `users/{uid}.stripe_tier`. Never change `beta_tester`, lifetime, or users covered by the legacy `creation_timestamp < 1795669200000` rule (`numista_backend/tier_gatekeeper.py:140-152`; they outrank `stripe_tier`, rule kept). Then call `lock_overflow_coins(uid, email)` to the **effective** limit (§4.8; comped users lock nothing). Never a hard-coded Free 10 (today's `payment_routes.py:234-238` sets `stripe_tier="free"` and locks to Free; replaced).
- **Billing portal** (`payment_routes.py:82-123`): the customer id is read from server-only `entitlements/{uid}.stripe_customer_id`, and used only if `stripe_customers/{customer_id}.uid == uid`. The client-writable `users/{id}.stripe_customer_id` read at `payment_routes.py:102-105` is no longer trusted (a user could otherwise point the portal at another customer). If none: today's lookup/create by the token email (`:107-114`), then write both server-only docs.
- Existing `estate` users (legacy $29/yr): no automatic change; their `stripe_tier` stays until their subscription ends; Gold becomes unlimited for them. Open question 3.

### 4.4 Refund/dispute (B5, D6, D7) — unchanged from v1.7 except the server-only subscription id

Every grant with a payment intent and every paid invoice writes `stripe_payments/{payment_intent_id}` with `{uid, kind, tier, subscription_id, granted}`. Handlers map `charge.payment_intent` through this ledger.

- `charge.refunded`:
  - Partial refund (`amount_refunded < amount`): log only, access kept (Eric decided).
  - Full refund: look up the ledger by payment intent.
    - `kind == "beta"` and `granted`: set `entitlements/{uid}.beta_special_until` to now (ends the unlimited period), keep `beta_special_purchased`, **do not touch `stripe_tier`**; then `lock_overflow_coins(uid, email)` to the effective limit.
    - `granted == false` (backstop or never-granted purchase): revoke nothing.
    - `kind == "subscription"`: if `entitlements/{uid}.stripe_subscription_id` equals the ledger's `subscription_id`, clear `users/{uid}.stripe_tier`; then lock to the effective limit.
    - No ledger entry: log, set the event `failed` with a review flag; change nothing.
- `charge.dispute.created`: log and set `entitlements/{uid}.dispute_review = true`. **No revoke.**
- `charge.dispute.closed`: status `lost` revokes exactly as the full-refund rules above; status `won` does nothing.
- Coins are never deleted. Lock timing: only on cancel, full refund, lost dispute (effective tier), plus the expiry/reconcile rule in §4.8. Never at checkout create.
- Pytest: full refund of a Beta purchase (ends Beta, leaves `stripe_tier`); backstop refund of a Copper subscriber's ungranted Beta (no revoke); full refund of a subscription invoice (clears tier, locks); dispute created (no revoke); dispute lost (revokes); dispute won (nothing); partial refund (nothing).

### 4.5 Limits (L1, L2) — exactly as v1.7 (harvest G5, CoS direction 4)

```python
TIER_COIN_LIMITS = {
    "free": 10,
    "pro": 100,
    "numismatist": 249,
    "dealer": 500,
    "estate": None,          # unlimited (JSON-safe)
    "family_estate": 2500,
    "sovereign": None,
    "power_user": None,
}


def within_limit(tier: str, count: int) -> bool:
    limit = TIER_COIN_LIMITS.get(tier, TIER_COIN_LIMITS["free"])
    return limit is None or count <= limit
```

API (`/subscription-status`) returns `coin_limit: null` plus `"unlimited": true` instead of `float('inf')`; the same helper is applied to `TIER_DAILY_ALLOWANCES` so existing `power_user`/`sovereign` accounts no longer fail JSON encoding (`payment_routes.py:149,158`). Tier capacities: Copper 11-100, Silver 101-249 (limit 249), Platinum 250-500 (limit 500), Gold 501 and up (unlimited). `within_limit(tier, count)` means "may hold `count` coins"; adding a coin is allowed only if `within_limit(tier, count + 1)`. `check_and_enforce_coin_limit` (`tier_gatekeeper.py:242-244`, currently `coin_count > limit`, which raises `TypeError` on `None`) is changed to use `within_limit`. Pytest: Silver 249 ok and 250 over; Platinum 500 ok and 501 over; Gold 10000 ok; free 10 ok and 11 over; JSON round-trip of `/subscription-status` for estate and power_user; the existing "limit = 20" test assertions updated to 10.

### 4.6 F&F flag (X1)
F&F purchases are gated by the server-validated promotion code (§4.1), not by a user flag. Where the plan or code reads the comped flag it is `beta_tester`, never `is_beta_tester` (the gate in `get_user_tier` reads `beta_tester`).

### 4.7 Dart (X4)

```dart
class PurchasableTier {
  static const allowed = <String>{'pro', 'numismatist', 'dealer', 'estate'};
  static bool isAllowed(String tier) => allowed.contains(tier);
}
```

`StripeService` must call `PurchasableTier.isAllowed(tier)` before the request and throw `ArgumentError` otherwise. Use `\$` for any literal dollar sign in Dart strings.

Entitlement refresh (new, §4.8 reconcile trigger): `StripeService.refreshEntitlement()` calls `GET $kApiBaseUrl/api/stripe/subscription-status?uid=<FirebaseAuth uid>` with `HttpAuthClient` and ignores errors (fire-and-forget; the server is the control, this only makes the lazy lock run once per app session). It is called once from `_BaseLayoutState.initState` (`numista_mobile/lib/screens/base_layout.dart:196-197`). The app never calls `/subscription-status` today (no match in `numista_mobile/lib`), so without this call a user who only uses direct-Firestore screens would never trigger the lazy lock.

### 4.8 Entitlement, coin count, lock and unlock (Eric decisions; v1.7 N3, v1.8 R1/R2, A2, A4, harvest G4/G5/G6/G9)

**Facts in today's code this design is built on (read-only at `a3d7dca2`):**
- Coins live in two kinds of folder. Most server routes and the app use `users/{email}/coins` (e.g. `numista_backend/main.py:8738`, `numista_mobile/lib/screens/base_layout.dart:110-114`, `numista_mobile/lib/services/set_grouping_service.dart:38`); some use `users/{uid}/coins` (`numista_backend/routes/scan_routes.py:312`, `numista_backend/routes/import_routes.py:118,242`, `numista_backend/routes/attorney_routes.py:251`, `numista_mobile/lib/services/beta_checklist_service.dart:355`). `migrate_legacy_collection_chunked` (`numista_backend/tier_gatekeeper.py:67-110`) copies email-folder docs to the uid folder **with the same document ids** and never deletes the originals; it has no caller in the runtime code today (only its definition matches a repo-wide grep), so copies exist only where it was run in the past.
- Today's count (`tier_gatekeeper.py:160-168`) reads one folder and **returns 0 on any error** (fails open). Today's lock (`tier_gatekeeper.py:325-337`) orders one folder by `created_at` ascending and flags index `>= limit` with `locked_pending_upgrade` (so the **newest** coins are locked, the oldest stay visible); Firestore's `order_by` silently drops docs without `created_at`; one batch for all docs (fails over 500); errors are printed and swallowed. Today's unlock (`:340-351`) flips the flag back. No app code reads `locked_pending_upgrade` (no match in `numista_mobile/lib`), so today's flag never hid anything.
- The rules let the owner read and delete every coin and create coins directly (`numista_mobile/firestore.rules:40-67`, `isOwner` at `:13-15` accepts email or uid). Rules cannot count documents.

**Design (no rules change):**
- **Unit counted** = one coin document id (a "lot"), exactly as today's `get_coin_count` counts documents. Only `coins` folders count. `currency`, `wishlist` and every other subcollection are never counted and never locked (harvest H4).
- **Owner keys** for a signed-in user = `{uid, email}` from the verified ID token (email lower-cased; if the raw token email differs from its lower-case form, both are read). Never from the request body or query.
- **Dedupe:** `visible_ids = ids(users/{uid}/coins) ∪ ids(users/{email}/coins)`; the same id in both folders is one coin (no `migration_status` shortcut, because new coins keep landing in the email folder after a migration).
- **`count_unique_coins(db, uid, email, include_locked)`**: returns `len(visible_ids)`, plus, when `include_locked` is true, the ids in `locked_coins/{uid}/coins` ∪ `locked_coins/{email}/coins` not already visible (one coin counted once). Any read error raises (callers return 503; never 0 — today's fail-open at `tier_gatekeeper.py:166-168` is removed). **Limit checks** (add paths, lock, unlock room) use `include_locked=False` (visible coins only). **Beta Special eligibility** (> 100 coins, at create and at fulfillment, §4.1/§4.3) uses `include_locked=True`: every coin the buyer owns counts, including coins locked after an earlier downgrade, because Beta Special's purpose is to unlock a large collection.
- **Locked store:** `locked_coins/{owner_key}/coins/{coin_id}` — a new **top-level** collection. One locked doc per source copy, under the same owner key as its source folder, holding `{coin_id, source_path, data, locked_at, lock_reason, sort_epoch}` where `data` is the original document's fields unchanged. No client can read, list, create, update or delete anything there under the current rules: no `match` block covers `/locked_coins/...`, so only `match /{document=**} { allow read, write: if false; }` (`firestore.rules:345-348`) applies. The Admin SDK used by the backend bypasses rules. Because the coin is physically gone from the client-readable folder, every existing app screen and every existing list query simply doesn't see it, with no query change and no rules change (this avoids the v1.8 "rules are not filters" lock-out completely).
- **Lock order (OPEN QUESTION 13 for Eric, not a decision):** keep today's direction from `tier_gatekeeper.py:327-334` — sort unique coins oldest first, keep the first `limit` visible, lock the rest (the newest). **Sort time (v1.9.1, CoS advisory 1):** `to_epoch(created_at)`; if that is missing or unparseable, `to_epoch(added_at)`; if that is also missing or unparseable, epoch 0 (treated as oldest, so kept visible, and never skipped: A2). `created_at` is what the server writes (e.g. `firestore.SERVER_TIMESTAMP` at `numista_backend/main.py:2747`) and what today's lock orders by (`tier_gatekeeper.py:327`); `added_at` (an ISO-8601 string, no `created_at`) is what the app's direct coin creates write: the roll wizard (`numista_mobile/lib/widgets/roll_entry_dialog.dart:374-384`, field at `:379`) and wishlist "found" (`numista_mobile/lib/screens/wishlist_screen.dart:979-984`, field at `:983`). Ties broken by coin id. For a coin with two copies, its sort time is the earlier of the two. The same value is stored as `sort_epoch` on the locked doc.
- **Effective limit** (one helper for every path; `get_user_tier` stays exactly as `tier_gatekeeper.py:132-157`, one argument — v1.8 advisory 5):

```python
from datetime import datetime

def to_epoch(val):
    """None if missing; 0.0 if present but unparseable (fails closed: treated as expired / oldest)."""
    if val is None:
        return None
    if hasattr(val, "timestamp"):            # Firestore Timestamp / DatetimeWithNanoseconds / datetime
        try:
            return float(val.timestamp())
        except Exception:
            return 0.0
    if isinstance(val, (int, float)):
        v = float(val)
        return v / 1000.0 if v > 1e11 else v  # millisecond epochs (as in creation_timestamp) → seconds
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return 0.0
    return 0.0


def load_entitlement_profile(db, uid, email):
    """Merged view of users/{uid} and users/{email}; raises on any read error."""
    uid_doc = (db.collection("users").document(uid).get().to_dict() or {}) if uid else {}
    email_doc = (db.collection("users").document(email).get().to_dict() or {}) if email and email != uid else {}
    ent = db.collection("entitlements").document(uid).get().to_dict() or {}
    profile = dict(email_doc)
    profile.update(uid_doc)                   # webhook writes stripe_tier to users/{uid}
    for k in ("is_lifetime_family_estate", "is_ai_qc_account", "beta_tester", "power_user"):
        profile[k] = bool(uid_doc.get(k) or email_doc.get(k))   # comp flags may live on either doc
    if profile.get("creation_timestamp") is None:
        profile["creation_timestamp"] = email_doc.get("creation_timestamp")
    return profile, ent


def effective_limit(profile, ent, now_ts, limits):
    """None = unlimited."""
    if profile.get("power_user") is True:     # today's bypass, tier_gatekeeper.py:238 (open risk 15)
        return None
    until = to_epoch(ent.get("beta_special_until"))   # stored as Firestore Timestamp (A4)
    if until is not None and until > now_ts:  # unexpired Beta Special: unlimited on any tier
        return None
    tier = get_user_tier(profile)             # unchanged
    return limits.get(tier, limits["free"])


def entitlement_ok(limit, count):
    return limit is None or count <= limit
```

  Merging the two user docs can only add access (a comp flag set on either doc counts), so it can never lock a comped user's coins; `firestore.rules:69-73` says those flags live on `users/{email}`, while the webhook writes `users/{uid}`.

- **Lock (`lock_overflow_coins(db, uid, email, limit, reason, now)`; replaces `tier_gatekeeper.py:325-337`):**
  1. `limit is None` → return 0.
  2. Stream both coin folders (full docs). Group copies by coin id. If unique count ≤ limit → return 0.
  3. Sort unique coins as above; the coins after the first `limit` are to be locked (every copy of each).
  4. Process copies in chunks of **at most 200 copies** per Firestore transaction (2 writes each = at most 400 writes, under the 500-write limit). Inside the transaction, re-read each source doc: if it no longer exists, skip it (already moved or deleted by the user before the lock); else `set` `locked_coins/{owner_key}/coins/{coin_id}` with the fresh data and `delete` the source. Set and delete commit together or not at all, so a coin is never in neither place, and a client edit made just before the move is not lost.
  5. Any error raises (no print-and-continue). Earlier chunks stay committed and consistent; a re-run continues where it stopped (idempotent: moved coins are no longer in the source).
- **Unlock (`unlock_user_coins(db, uid, email, limit)`; replaces `tier_gatekeeper.py:340-351`):**
  1. Read `locked_coins/{uid}/coins` and `locked_coins/{email}/coins`. Group by coin id.
  2. Room = unlimited if `limit is None`, else `limit − len(visible_ids)`; restore whole coins oldest-first (`sort_epoch` ascending) while room allows.
  3. Chunks of at most 200 copies per transaction: re-read the target `source_path`; if a document already exists there, do **not** overwrite — leave the locked copy, set `restore_conflict: true` on it, log, and count it (reported in `/subscription-status` as `restore_conflicts`); else `set` the source with `data` exactly and `delete` the locked copy. Each copy returns to the exact folder it came from (email folder → email folder, uid folder → uid folder).
  4. Legacy flags (harvest G6): after restoring, any visible coin in either folder with `locked_pending_upgrade == true` is updated to `false` (chunks of at most 400 updates). The new code never reads that flag for access.
  5. Errors raise.
- **Reconcile (`enforce_entitlement(db, uid, email, now)`):** load profile → limit → `visible = len(visible_ids)`; if `limit` is not None and `visible > limit`, call `lock_overflow_coins`; if `limit` allows more and locked coins exist, call `unlock_user_coins`. Returns `{limit, visible, locked, restore_conflicts}`. Called by: `/api/stripe/subscription-status`, checkout create, the webhook after every grant/cancel/refund/lost dispute, `/api/collection/count` (`main.py:8722`), every add path below before it checks, and every by-id coin route below before it answers. It is the lazy lock for Beta expiry (Eric allowed lazy) and the server-side catch for client-SDK creates.
- **`/api/stripe/subscription-status` caller rules (v1.9.1, CoS advisory 5).** Today (`numista_backend/routes/payment_routes.py:130-164`): the `uid` query value must equal the caller's token uid or email unless the token has the `admin` claim (`:141-143`, else 403 `Forbidden`); it then returns `{uid, stripe_tier, subscription_status, grace_period_until, coin_count, coin_limit, daily_ai_allowance, deepdive_count, invoice_scan_count}` for that `uid`, with `coin_count` from `users/{uid}/coins` only via `get_coin_count(uid)` (`:144-161`, count at `:147`) and any error as 500 (`:162-164`); the admin path today performs reads only. v1.9.1:
  - **Own lookup** (value equals the token uid or email; admin or not): `enforce_entitlement` on the caller's own token keys `{uid, email}`, then the same fields as today with `coin_count` = deduped visible coins, `coin_limit` JSON-safe plus `unlimited`, and `locked`, `restore_conflicts`; a read error → 503.
  - **Non-admin, other value:** 403 `Forbidden`, unchanged.
  - **Admin, other value:** a **read-only report; no reconcile.** `enforce_entitlement`, `lock_overflow_coins` and `unlock_user_coins` are never called for another user, so an admin lookup never moves anyone's coins. Owner key = the query value only (lower-cased if it contains `@`; no lookup of the other key, so coins under the user's other key are not included — the admin queries both keys to see both). It returns the same field names as the own lookup, computed from that one key (`coin_count` = visible coins in `users/{key}/coins`, `locked` = docs in `locked_coins/{key}/coins`, `stripe_tier`/`coin_limit` from `load_entitlement_profile` + `effective_limit` on that key; `entitlements/{key}` is read only when the key is a uid, so Beta status shows only for a uid query), plus `admin_view: true`, `reconciled: false`, `owner_keys: [key]`. `restore_conflicts` is the count of `restore_conflict: true` docs under that key. A read error → 503. No write of any kind.
- **Add paths** (reject 403 `{"error": "tier_limit_exceeded", "limit": ..., "count": ...}` when `not entitlement_ok(limit, visible + n_new)`; a read error returns 503, never allow): `main.py:2541-2701` `execute_add_coin`; `main.py:3511-3527` `/api/review/commit`; `main.py:3711-3728` `/api/review/keep_set_as_is`; `main.py:5201-5227` `/api/confirm_binder_scan`; `main.py:8827-8907` `/api/checklist/add_coins`; `routes/import_routes.py:76-118` `/import_spreadsheet` and `:236-242` `/v1/import/commit_batch`; `routes/cert_routes.py:309-336` `/cert_save`; `routes/morgan_routes.py:143-217` `/api/morgan/confirm` and `:340-371` `/api/coins/restore/{coin_id}`; `routes/scan_routes.py:290-312` `/review/commit_session`; and the receiving side of a transfer claim (`services/transfer_service.py:383` `claim_transfer`, imported at `main.py:12098`; only when the received item resolves to the `coins` folder, `services/transfer_service.py:60-84`). The new check does **not** call `create_upgrade_checkout_session` (X3: left unwired and untouched); `check_and_enforce_coin_limit` gets only v1.7's `within_limit` fix.
- **Client-SDK adds** (`firestore.rules:55-58` lets the owner create coins directly; rules can't count): not blockable without a rules change. Server-side control: the next `enforce_entitlement` (at the latest the app-start call in §4.7) moves the over-limit coins — the newest, i.e. the ones just added (their `added_at` is the add time, so they sort newest; v1.9.1) — into the locked store. Nothing is deleted, the coins appear in the CSV, and they return on upgrade. This is stated as the create-limit design for NET-827; a rules-level block is not possible because rules cannot count.
- **View/edit/delete paths:** because locked coins are not in the coin folders, every existing list, detail, edit and delete route (e.g. `main.py:2910` details, `:2938` update, `:3022` undo-add, `:4357` coin crop, `:8722` count, `:8986` clear, `routes/grade_review_routes.py:88-112`, `routes/sandbox_routes.py:24-43`, `services/transfer_service.py:87-121`) can neither see nor change them, with no change. User "clear collection" and sandbox clear therefore never delete locked coins. **By-id routes** (details, update, undo-add, coin crop, grade submit, transfer initiate, `/api/coins/restore/{coin_id}`): when the coin id is not found in the caller's folders, look up `locked_coins/{uid|email}/coins/{coin_id}`; if present return **403 `{"error": "LOCKED_PENDING_UPGRADE"}`** (no coin data), else today's 404 (harvest G9). The builder lists every route touched, with its check, in the commit message; any user coin route found without the add check (if it adds) or the 403 lookup (if by id) is a defect.
- **Production existing flags (G6):** PV-0 (read-only) counts coins with `locked_pending_upgrade == true` in production. They are visible today and stay visible; no production change happens in NET-827.

### 4.9 Server-only state and why NET-827 needs no Firestore rules change (v1.8 R1, CoS direction 3, harvest G1)

- **What the current rules protect** (`numista_mobile/firestore.rules`, SHA-256 `e650713b9051904fa52efbe046b13986ad5896a435b89cea13a1ac53da2f9c86`, the file `numista_mobile/firebase.json:2-5` deploys): on `users/{email}` (which also matches a uid, `:13-15`), the owner may create and update the doc as long as no key in `_serverOnlyKeys()` = `tier, stripe_tier, beta_tester, is_lifetime_family_estate, is_ai_qc_account, is_bot_account, sandbox_cleared, admin` is touched (`:85-104`); delete is denied (`:103`). Every other key on the user doc is client-writable. Every `users/{email}/{sub}/...` subcollection not in the exclusion list is owner read/write (`:108-116`). Anything not matched is denied (`:345-348`).
- **Consequence:** any new field the server must control cannot go on `users/{id}` (except under an existing server-only key) and cannot go in a new `users/{id}/<sub>` subcollection (the wildcard at `:108-116` would let the owner read and write it — the harvest X2 point).
- **v1.9 storage map (all new server-only state is top-level, matched only by the deny-all at `:345-348`):**

| Data | Location | Client access under current rules |
|---|---|---|
| `stripe_tier` | `users/{uid}` (as today) | read own; write denied (`_serverOnlyKeys`) |
| `beta_special_until` (Timestamp), `beta_special_purchased`, `stripe_subscription_id`, `stripe_customer_id`, `checkout_pending`, `dispute_review` | `entitlements/{uid}` (new) | none |
| locked coins | `locked_coins/{owner_key}/coins/{coin_id}` (new) | none |
| customer → uid map | `stripe_customers/{customer_id}` (new) | none |
| payment ledger | `stripe_payments/{payment_intent_id}` (new) | none |
| event claims | `stripe_events/{event_id}` (exists, `payment_routes.py:199`) | none |

  A repo-wide grep at `a3d7dca2` finds no existing use of the names `entitlements`, `locked_coins`, `stripe_customers` or `stripe_payments` as collections in the backend, and no `match` block for them in the rules, so nothing else reads or writes them and they are denied to clients today.
- **Users can never write their own entitlements:** the only entitlement fields on the user doc (`stripe_tier`, `tier`, `beta_tester`, lifetime, `admin`) stay server-only exactly as today; every new entitlement field is in a client-denied document. Nothing in v1.9 widens any client write.
- **Owner list queries keep working:** the coin rules (`:40-67`) and all client queries are unchanged, so the v1.8 lock-out cannot happen.
- **Pre-existing gaps found (not caused by NET-827; recorded, not fixed here):** `creation_timestamp` (read by `tier_gatekeeper.py:146-152` to grant `family_estate`) and `power_user` (read at `tier_gatekeeper.py:238`) are client-writable on the user doc today; neither is written anywhere in `numista_mobile/lib` or the backend runtime. They are open risks 14 and 15 (Section 10) and are closed by the optional rules step RX (§9.4), which needs its own production YES.
- **Proof without deploying anything:** the Jest emulator tests in §7.2 run against the unchanged rules file and assert owner list/create/update still succeed and every new collection is denied.

### 4.10 CSV export (Eric decision; v1.7 N1/N3, v1.8 R2/R5, A5, harvest H11)

- New `numista_backend/routes/export_routes.py`, router mounted in `main.py` next to the other routers (`main.py:96-117` imports). `GET /api/export/collection.csv`, dependency `get_current_user` (`routes/deps.py:69-79`); unauthenticated → 401. Owner keys come only from the verified token (`uid`, `email`); the endpoint takes no user parameter at all, so another user's data cannot be requested. Uses the guarded Firestore client (`env_guard.get_firestore()` via `routes.deps.db`), so in preview it reads only the test project.
- Available on every tier at all times; it never calls `enforce_entitlement` and is never blocked by the limit or by Beta expiry.
- Rows, deduped by `(item_type, item_id)`:
  - `coin` — union of `users/{uid}/coins` and `users/{email}/coins` (one row per coin id; the email-folder copy's fields win when both exist) with `locked=false`;
  - `coin` — union of `locked_coins/{uid}/coins` and `locked_coins/{email}/coins` (fields from `data`) with `locked=true`; a coin id that is somehow both visible and locked appears once, `locked=false`;
  - `currency`, `banknotes`, `world_items`, `wishlist` — union of both owner keys (`banknotes`/`currency` per `services/transfer_service.py:60-84`; `world_items` per `numista_mobile/lib/services/beta_checklist_service.dart:366`). Exported only; never counted or locked.
- Columns: `item_type, item_id, locked, source_path`, then the sorted union of all field names; scalar values as text, maps/lists as compact JSON, Timestamps as ISO-8601 UTC. (Exact field names vary by document; nothing is invented.)
- Formula-injection guard (A5): any cell starting with `=`, `+`, `-`, `@`, tab or carriage return is prefixed with `'`.
- Streams with `StreamingResponse`, `Content-Disposition: attachment; filename="numista_collection.csv"`. A read error returns 503 (never a partial file presented as complete).

### 4.11 Runtime data-client guard: complete inventory (v1.7 N1, v1.8 R3/R4, harvest H6/G7)

Found by walking every module `main.py` imports (module-level and inside functions) and grepping them for Firestore, Storage and Firebase Admin construction at `a3d7dca2`. Every row is in the §3 file list.

| # | Location (file:line) | Today | v1.9 change |
|---|---|---|---|
| 1 | `routes/deps.py:21,24` | `firestore.Client(project="studio-…")` | `db = env_guard.get_firestore()` (name kept, so the 18 routers and 2 services that import `db` from `routes.deps` — e.g. `routes/payment_routes.py:15`, `routes/feedback_callable_route.py:31`, `services/vector_rag_service.py:23` — are covered without edits) |
| 2 | `routes/deps.py:25` | `gcs.Client(project=…)` | `storage_client = env_guard.get_storage()` (guarded wrapper; used by `routes/import_routes.py:17,53,96` and `routes/feedback_callable_route.py:31,494`) |
| 3 | `routes/deps.py:40-48` | Firebase Admin default app on production | `env_guard.init_firebase_admin()` — default app with `projectId = FIREBASE_AUTH_PROJECT_ID`, used for ID-token verification only |
| 4 | `tier_gatekeeper.py:13-29` | own Admin init + `firestore.client()` (default app = production Auth project) | `env_guard.init_firebase_admin()`; `db = env_guard.get_firestore()` |
| 5 | `main.py:345-349` | `firestore.Client(credentials=…, project=PROJECT_ID)` (`PROJECT_ID` from `FIREBASE_PROJECT_ID`, default production, `main.py:335`) | `db = env_guard.get_firestore()` |
| 6 | `main.py:352` | `gcs.Client(...)` | `gcs_client = env_guard.get_storage()` |
| 7 | `main.py:357-358` | `firebase_admin.initialize_app()` | `env_guard.init_firebase_admin()` |
| 8 | `main.py:342` (+ `:4149`, `:6900`, `:7188`, `:7250`, `:7341`, `:7646`, `:8408`, `:8540`) | `USER_CONTENT_BUCKET = "numista-uploads-studio-9101802118-8c9a8"` | `USER_CONTENT_BUCKET = env_guard.bucket_for("numista-uploads-studio-9101802118-8c9a8", "USER_CONTENT_BUCKET")` (production result identical to today) |
| 9 | `main.py:4407,4430` | `_gcs.Client()`; bucket name parsed from a coin's image URL | `env_guard.get_storage()`; wrapper refuses production buckets in preview |
| 10 | `main.py:9606-9607` | `gcs.Client()`, bucket `numista-reference-library` | `env_guard.get_storage()` + `bucket_for("numista-reference-library", None)` |
| 11 | `main.py:12279-12283` | `gcs_client.bucket(os.environ.get("GCS_BUCKET_NAME", "studio-9101802118-8c9a8-uploads"))` | `bucket_for("studio-9101802118-8c9a8-uploads", "GCS_BUCKET_NAME")` |
| 12 | `routes/estate_routes.py:20,42` | `BUCKET_NAME` from `GCS_BUCKET_NAME` (default `studio-9101802118-8c9a8-uploads`); plain `storage.Client()` | `bucket_for(...)` same default and override; `env_guard.get_storage()` |
| 13 | `routes/import_routes.py:21,53,96` | bucket `studio-9101802118-8c9a8-uploads`; `:96` bucket parsed from a request URI | `bucket_for("studio-9101802118-8c9a8-uploads", None)`; `:96` goes through the guarded wrapper |
| 14 | `routes/feedback_callable_route.py:36-37,494` | `GCS_BUCKET = "studio-9101802118-8c9a8-uploads"` | `bucket_for("studio-9101802118-8c9a8-uploads", None)` |
| 15 | `routes/subaccount_routes.py:23-27` | lazy `firestore.Client(project="studio-…")` | `get_db()` returns `env_guard.get_firestore()` |
| 16 | `routes/support_routes.py:35-39` | lazy `firestore.Client()` (a **Firestore** client) | `_get_db()` returns `env_guard.get_firestore()` |
| 17 | `brain_processor.py:44-56` (line 51) | module-level `firestore.Client(credentials=…, project=PROJECT_ID)`; imported lazily at `main.py:10609` | `db = env_guard.get_firestore()`. (`brain_processor.py:311` is inside a docstring "Manual invocation only" example, not runtime; left as is.) Route `main.py:10597-10612` returns 503 in preview |
| 18 | `services/canon_sync_service.py:10-11,21-26` | `firestore.Client` + `storage.Client` on production, bucket `studio-9101802118-8c9a8-uploads`; imported at `main.py:10623` | `get_gcp_clients()` returns `env_guard.get_firestore(), env_guard.get_storage()`; bucket via `bucket_for`; route `main.py:10615-…` (`/api/admin/brain/sync_canon`) returns 503 in preview (it also calls `scripts/refresh_vertex_data_store.py`, bucket at `:12`, which is not run in preview) |
| 19 | `numista_scraper/storage.py:15-16,22-38` | module-level Admin init on production, `firestore.client()`, `gcs_storage.Client(project=…)`, `bucket = …bucket("numista-uploads-studio-…")` | `db = env_guard.get_firestore()`; `gcs_client = env_guard.get_storage()`; `bucket = gcs_client.bucket(env_guard.bucket_for(BUCKET_NAME, None))`; no Admin init |
| 20 | `numista_scraper/scrapers.py:146,705,731` | `firestore.client()` (Admin default app) | `env_guard.get_firestore()` |
| 21 | `numista_scraper/config.py:117-124,186-193` | Admin `initialize_app()` + `_fs.client()` | `env_guard.get_firestore()`; no Admin init |
| 22 | Scraper entry points `main.py:3334-3341` (deep-dive auto-scraper trigger, user-reachable), `main.py:10192` (cron scraper), `main.py:10457-10463` (`/api/scraper/scrape-url`) | start `numista_scraper` | in preview: the deep-dive trigger is skipped (no scrape thread), the two routes return 503 |

`numista_scraper` gets its clients from `env_guard` (a leaf module with no app imports), not from `routes.deps`, so the scraper package does not depend on the app (harvest H6 note).

**AI/search clients (not data stores; unchanged):** `routes/deps.py:29`, `main.py:436`, `main.py:2040,4870` (Document AI), `services/vector_rag_service.py:37-39`, `routes/cert_routes.py:403,421`, `services/variety_detector.py:63`, `numista_scraper/grading_advisor.py:9,12`, `vertex_search/coin_search_endpoint.py:24`, `morgan_knowledge.py:228`. In preview they point at the production project, where the preview service account has zero roles (PV-4), so calls fail with permission denied (fail closed). They read no user data from production Firestore or Storage. Those features are out of NET-827 test scope.

**Not part of the preview service:** `scan_service/main.py:58,188-194` and `scan_service/estate_pdf_builder.py:313-317` belong to the separate scan service; `main.py` imports only the pure `scan_service/collection_inventory.py` (`main.py:3081`), whose header says it must not import `main.py`. The ~400 standalone scripts in `numista_backend/` (e.g. `upload_*.py`, `_scripts/`) are not imported by `main.py` and are not in the import-graph test.

**Bucket guard rule:** production bucket names found in code: `numista-uploads-studio-9101802118-8c9a8` (`main.py:342`, `numista_scraper/config.py:12`), `studio-9101802118-8c9a8-uploads` (`routes/import_routes.py:21`, `routes/feedback_callable_route.py:37`, `routes/estate_routes.py:20`, `services/canon_sync_service.py:11`, `main.py:12281`), `numista-reference-library` (`main.py:9607`), `studio-9101802118-8c9a8.firebasestorage.app` (`numista_mobile/lib/firebase_options.dart:55,64,73`) and `numista-uploads-studio-9101802118-8c9a8.firebasestorage.app` (`scan_service/estate_pdf_builder.py:317`). In preview the guarded wrapper refuses all of them, plus any name containing `studio-9101802118-8c9a8`.

## 5. Christmas code (C1, D4) — unchanged from v1.7


- Window: `XMAS_START = 1795669260` (26 Nov 2026 12:01 AM America/New_York) to `XMAS_END = 1798261199` (25 Dec 2026 11:59:59 PM America/New_York), enforced server-side, never active early.
- Model (a), automatic: the server attaches the Christmas coupon to annual subscription sessions created inside the window (§4.1 `pick_discount`). No code is typed by the buyer and no request field exists, so the "client claims it early" path does not exist.
- Stripe coupons have no active/inactive state (promotion codes do). The controls are therefore: (1) the server gate above; (2) the Christmas coupon id is placed in the service's env only at LK-8, after the start instant, so before then the server has nothing to attach; (3) the Stripe coupon's own `redeem_by` equals `XMAS_END`; (4) the webhook re-checks the session `created` time against the window and the coupon id against the allowlist (`decide_grant`).
- Annual-only: monthly sessions never receive it. Coupon `applies_to` is product-level, so annual-only is enforced by the server, not by Stripe. No stacking: one discount per session (`pick_discount`); Beta Special never carries a discount.
- Test mode uses an injectable clock `get_now()` overridden in pytest; no waiting. The preview/test coupon uses the same logic.
- Coupon id from env (name UNKNOWN; record at execution time). No code strings in repo.


## 6. Preview backend (PX1, PX3, D1; v1.7 N1/N2, v1.8 R3/R4)

Reason: the p7-gate build defaults `kApiBaseUrl` to production Cloud Run `numista-backend` (`numista_mobile/lib/constants.dart:13-16`), which uses production Firestore and cannot be redeployed (HOLD `41b8bd5f`). So the preview gets its own backend, built into the preview with `--dart-define=API_BASE_URL=<preview URL>`. Eric decided: separate preview backend, its own test Firestore, Stripe test keys, never production Cloud Run, Firestore or Storage.

### 6.1 `numista_backend/env_guard.py` (new; v1.7 functions kept, bucket guard and providers added)

**Env settings (names fixed by this plan):** `NUMISTA_ENV` (`production` default, or `preview`), `FIRESTORE_PROJECT_ID`, `FIRESTORE_DATABASE_ID` (default `(default)`), `FIREBASE_AUTH_PROJECT_ID` (project whose ID tokens are verified; default production), `STRIPE_EXPECTED_MODE` (`live` or `test`), `USER_CONTENT_BUCKET` (required in preview; optional override in production, default `numista-uploads-studio-9101802118-8c9a8`). Existing names still honoured exactly as today in production: `GCS_BUCKET_NAME` (`routes/estate_routes.py:20`, `main.py:12281`). `FIREBASE_PROJECT_ID` (`main.py:335`) stays only for the AI clients that use `PROJECT_ID`; it no longer selects Firestore.

```python
import os
from pathlib import Path

PROD_PROJECT_ID = "studio-9101802118-8c9a8"
PROD_USER_CONTENT_BUCKET = "numista-uploads-studio-9101802118-8c9a8"
PROD_BUCKETS = frozenset({
    "numista-uploads-studio-9101802118-8c9a8",
    "studio-9101802118-8c9a8-uploads",
    "numista-reference-library",
    "studio-9101802118-8c9a8.firebasestorage.app",
    "numista-uploads-studio-9101802118-8c9a8.firebasestorage.app",
})
_BACKEND_DIR = Path(__file__).resolve().parent


class EnvGuardError(RuntimeError):
    pass


def is_production_bucket(name):
    name = (name or "").strip()
    return name in PROD_BUCKETS or PROD_PROJECT_ID in name


def load_data_config(env=None, backend_dir=_BACKEND_DIR):
    env = os.environ if env is None else env
    mode = env.get("NUMISTA_ENV", "production")
    if mode not in ("production", "preview"):
        raise EnvGuardError("NUMISTA_ENV must be production or preview")
    project = env.get("FIRESTORE_PROJECT_ID", "")
    database = env.get("FIRESTORE_DATABASE_ID", "(default)")
    auth_project = env.get("FIREBASE_AUTH_PROJECT_ID", PROD_PROJECT_ID)
    preview_bucket = env.get("USER_CONTENT_BUCKET", "")
    if mode == "production":
        project = project or PROD_PROJECT_ID
        if project != PROD_PROJECT_ID:
            raise EnvGuardError("production must use the production Firestore project")
    else:
        if not project:
            raise EnvGuardError("preview requires FIRESTORE_PROJECT_ID")
        if project == PROD_PROJECT_ID:
            raise EnvGuardError("preview must not use the production Firestore project")
        if not preview_bucket or is_production_bucket(preview_bucket):
            raise EnvGuardError("preview must set a non-production USER_CONTENT_BUCKET")
        if list(Path(backend_dir).glob("serviceAccountKey*.json")):
            raise EnvGuardError("preview must not ship a service account key file")
    return {"mode": mode, "project": project, "database": database,
            "auth_project": auth_project, "preview_bucket": preview_bucket}


_CFG = None


def config():
    global _CFG
    if _CFG is None:
        _CFG = load_data_config()      # raises at import time → the service refuses to start
    return _CFG


def check_stripe_key(key, mode, expected=None):          # v1.7, unchanged
    is_live = key.startswith(("sk_live_", "rk_live_"))
    is_test = key.startswith(("sk_test_", "rk_test_"))
    if not (is_live or is_test):
        raise EnvGuardError("unrecognised Stripe key prefix")
    if mode == "preview" and is_live:
        raise EnvGuardError("preview must use a Stripe test key")
    if expected not in ("live", "test"):
        raise EnvGuardError("STRIPE_EXPECTED_MODE must be live or test")
    if (expected == "live") != is_live:
        raise EnvGuardError("Stripe key mode does not match STRIPE_EXPECTED_MODE")


def build_firestore_client(cfg):                          # v1.7, unchanged
    from google.cloud import firestore
    return firestore.Client(project=cfg["project"], database=cfg["database"])


def bucket_for(prod_default, override_env=None, cfg=None, env=None):
    """Production: exactly today's value (override env or default). Preview: the one preview bucket."""
    cfg = cfg or config()
    env = os.environ if env is None else env
    if cfg["mode"] == "production":
        return (env.get(override_env) if override_env else None) or prod_default
    bucket = cfg["preview_bucket"]
    if is_production_bucket(bucket):
        raise EnvGuardError("preview bucket must not be a production bucket")
    return bucket


def resolve_user_content_bucket(cfg=None, env=None):      # harvest H5, real default
    return bucket_for(PROD_USER_CONTENT_BUCKET, "USER_CONTENT_BUCKET", cfg, env)


class GuardedStorageClient:
    """Delegates to google.cloud.storage.Client; in preview refuses production buckets."""
    _CHECKED = ("bucket", "get_bucket", "lookup_bucket")

    def __init__(self, inner, cfg):
        self._inner = inner
        self._cfg = cfg

    def _check(self, bucket_or_name):
        name = getattr(bucket_or_name, "name", bucket_or_name)
        if self._cfg["mode"] == "preview" and is_production_bucket(name):
            raise EnvGuardError("preview refused production bucket: %s" % name)

    def bucket(self, name, *a, **k):
        self._check(name)
        return self._inner.bucket(name, *a, **k)

    def get_bucket(self, b, *a, **k):
        self._check(b)
        return self._inner.get_bucket(b, *a, **k)

    def lookup_bucket(self, name, *a, **k):
        self._check(name)
        return self._inner.lookup_bucket(name, *a, **k)

    def __getattr__(self, item):
        if item.startswith("__"):            # keep hasattr/copy semantics
            raise AttributeError(item)
        if self._cfg["mode"] == "preview":
            raise EnvGuardError("storage call not allowed in preview: %s" % item)
        return getattr(self._inner, item)


_FS = None
_GCS = None


def get_firestore():
    global _FS
    if _FS is None:
        _FS = build_firestore_client(config())
    return _FS


def get_storage():
    global _GCS
    if _GCS is None:
        from google.cloud import storage
        cfg = config()
        _GCS = GuardedStorageClient(storage.Client(project=cfg["project"]), cfg)
    return _GCS


def init_firebase_admin():
    """Default Firebase app for ID-token verification only. Never used for Firestore."""
    import firebase_admin
    from firebase_admin import credentials
    if firebase_admin._apps:
        return
    cfg = config()
    keys = [p for p in (_BACKEND_DIR / "serviceAccountKey.json", _BACKEND_DIR / "serviceAccountKey.json.json") if p.exists()]
    if cfg["mode"] == "production" and keys:                 # today's local-dev behaviour, deps.py:41-46
        firebase_admin.initialize_app(credentials.Certificate(str(keys[0])), {"projectId": cfg["auth_project"]})
    else:
        firebase_admin.initialize_app(options={"projectId": cfg["auth_project"]})


def require_production(feature):
    """Production-only admin/scraper features: 503 in preview."""
    if config()["mode"] != "production":
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="%s is disabled in preview" % feature)
```

Behaviour: **fail closed.** A preview with `FIRESTORE_PROJECT_ID` unset or equal to production, `USER_CONTENT_BUCKET` unset or a production bucket, or a key file in the image refuses to start; a production service whose Firestore project isn't production refuses to start; a preview with a live or missing Stripe key refuses to start (`stripe_config.py` calls `check_stripe_key(key, config()["mode"], os.environ.get("STRIPE_EXPECTED_MODE"))` whenever a key is present, and in preview treats a missing key as an error). Production's `STRIPE_EXPECTED_MODE` is set at the go-live gate from a recorded read-only check (GL-1, §9.3); it is never guessed in this plan. In production every resolved project and bucket equals today's value, so production behaviour is unchanged.

`firebase_admin.firestore.client()` is **forbidden** in runtime code: the default Firebase app is initialised on `FIREBASE_AUTH_PROJECT_ID` (production Auth), so that call would reach production Firestore from the preview. The import-graph test (§7.3) enforces it.

### 6.2 ID-token verification

The preview backend verifies ID tokens with `firebase_auth.verify_id_token` (`routes/deps.py:52-67`) against `FIREBASE_AUTH_PROJECT_ID` = production Auth. Verification uses Google's public signing keys and needs no IAM on the production project. All Firestore and Storage access uses the test project via `env_guard`. Admin calls that would need production IAM (e.g. user lookups) fail closed in preview.

### 6.3 Who uses p7-gate, and how testers reach the preview (v1.7 N2; carried from v1.8)

- **No real users on p7-gate during NET-827.** No human — Eric, beta testers, or anyone else — signs in on the p7-gate web app. The synthetic testers never sign in on p7-gate either.
- Testing is pytest (§7) and the scripted HTTP client (§8) against the preview backend URL directly. That client gets an ID token from production Firebase Auth (sign-in by REST, which creates no Firestore data) and calls the preview backend; nothing touches production Firestore.
- Pages may be loaded signed-out to confirm the build serves; no sign-in.

**Synthetic preview testers (Eric approved; unchanged list):**

| Email | Purpose |
|---|---|
| `ft-preview-01@numista.ai` | Free tier / limits |
| `ft-preview-02@numista.ai` | Paid checkout (test card) |
| `ft-preview-03@numista.ai` | Beta Special eligibility (101+ coins; the coins live in the test Firestore only, seeded by PV-5b) |
| `ft-preview-04@numista.ai` | F&F and Christmas discount paths |

Production Firebase Auth only, verification only; no document is ever created for them in production Firestore; passwords typed by Eric at run time and never written to any file.

### 6.4 Gated steps PV-0 to PV-3 and PV-5b (none run now; each needs Eric's typed YES; none touch `numista-backend`)

- **PV-0** (read-only, production, Eric's own ADC): counts only, no document contents printed (script below). Records harvest G6 (coins with the old flag) and open risks 14/15.
- **PV-1** Eric creates or approves the separate test Firebase/GCP project with its own Firestore (project id UNKNOWN; record), a dedicated preview service account holding Firestore and Storage roles on that test project only and **no role on `studio-9101802118-8c9a8`**, and one preview Storage bucket in the test project (name UNKNOWN; record; must not be any name in `PROD_BUCKETS` or contain `studio-9101802118-8c9a8`).
- **PV-2** Eric stores the Stripe **test** secret key and a test webhook signing secret in Secret Manager in the test project (secret names UNKNOWN; record). The code reads `STRIPE_SECRET_KEY` (`numista_backend/stripe_config.py:30`) and `STRIPE_WEBHOOK_SECRET` (`numista_backend/routes/payment_routes.py:174`); `stripe_config.py:29` also reads `STRIPE_PUBLISHABLE_KEY`; if it is absent `load_stripe_keys` only logs a warning (`stripe_config.py:78-86`), so it is not mounted. In preview the webhook route refuses unsigned events because Cloud Run sets `K_SERVICE` (`routes/payment_routes.py:172-189`), so PV-2b is required before any webhook test.
- **PV-2b** After PV-3, Eric creates the **test-mode** webhook endpoint in his Stripe sandbox pointing at `<preview URL>/api/stripe/webhook` with the events used in §4.3/§4.4 (`checkout.session.completed`, `checkout.session.expired`, `checkout.session.async_payment_succeeded`, `checkout.session.async_payment_failed`, `invoice.paid`, `invoice.payment_failed`, `customer.subscription.updated`, `customer.subscription.deleted`, `charge.refunded`, `charge.dispute.created`, `charge.dispute.closed`), and puts its signing secret in the PV-2 secret (new version), then redeploys with PV-3 (same SHA).
- **PV-3** deploy the preview service (block below).
- **PV-4** read-only isolation proof (§6.6).
- **PV-4.5** read-only production check for synthetic-tester data by uid and email; delete only with a separate YES (§6.6).
- **PV-5** create the four synthetic testers; **PV-5b** seed `ft-preview-03` with 101+ test coins in the **test** Firestore only; **PV-6** delete the testers after Field Tester (§6.5; PV-5b block below).

PV-0 (read-only; Windows PowerShell 5.1; temp-file pattern; project venv; prints counts only):

```powershell
$ErrorActionPreference = 'Stop'
$py = 'C:\Users\ericd\Documents\MyVertexProject\numista_backend\.venv\Scripts\python.exe'
$script = Join-Path $env:TEMP 'net827_pv0_counts.py'
@'
from google.cloud import firestore
PROD = "studio-9101802118-8c9a8"
db = firestore.Client(project=PROD)
def count(q):
    return q.count().get()[0][0].value
out = {}
try:
    out["coins_with_locked_pending_upgrade_true"] = count(db.collection_group("coins").where("locked_pending_upgrade", "==", True))
except Exception as e:
    out["coins_with_locked_pending_upgrade_true"] = "BLOCKED: " + type(e).__name__ + " (a collection-group index may be needed; creating one is a production change and is NOT done)"
out["users_with_power_user_true"] = count(db.collection("users").where("power_user", "==", True))
# cutoff 1795669200000 ms is the legacy grant in tier_gatekeeper.py:146-149
out["users_with_creation_timestamp_below_cutoff"] = count(db.collection("users").where("creation_timestamp", "<", 1795669200000))
for k, v in out.items():
    print(k, v)
'@ | Set-Content -Encoding UTF8 $script
try {
    & $py $script
    if ($LASTEXITCODE -ne 0) { throw "PV-0 failed: $LASTEXITCODE" }
} finally {
    Remove-Item $script -ErrorAction SilentlyContinue
}
```

PV-3 (Windows PowerShell 5.1; harvest H7 plus a key-file check; run from a worktree of the built SHA; if `gcloud run deploy --source` cannot build the existing backend — it has a `Dockerfile` with `CMD ["uvicorn", "main:app", ...]` at `numista_backend/Dockerfile` — the step is BLOCKED with the exact error):

```powershell
$ErrorActionPreference = 'Stop'
function Invoke-Native {
    param([scriptblock]$Cmd)
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $Cmd } finally { $ErrorActionPreference = $old }
    if ($LASTEXITCODE -ne 0) { throw "Native command failed: $LASTEXITCODE" }
}
$repo              = 'C:\Users\ericd\Documents\MyVertexProject'
$ProdProject       = 'studio-9101802118-8c9a8'
$ProdBuckets       = @('numista-uploads-studio-9101802118-8c9a8','studio-9101802118-8c9a8-uploads','numista-reference-library','studio-9101802118-8c9a8.firebasestorage.app','numista-uploads-studio-9101802118-8c9a8.firebasestorage.app')
$PreviewProject    = '<PREVIEW_PROJECT_UNKNOWN>'
$Service           = '<PREVIEW_SERVICE_UNKNOWN>'
$Sa                = '<PREVIEW_SERVICE_ACCOUNT_UNKNOWN>'
$KeySecret         = '<TEST_KEY_SECRET_NAME_UNKNOWN>'
$WhSecret          = '<TEST_WEBHOOK_SECRET_NAME_UNKNOWN>'
$UserContentBucket = '<PREVIEW_USER_CONTENT_BUCKET_UNKNOWN>'
$sha               = '<BUILT_SHA_UNKNOWN_RECORD_AT_EXECUTION>'
foreach ($v in @($PreviewProject, $Service, $Sa, $KeySecret, $WhSecret, $UserContentBucket, $sha)) {
    if ($v -like '<*') { throw "placeholder not filled: $v" }
}
if ($PreviewProject -eq $ProdProject)                { throw 'preview project must not be the production project' }
if ($Service -eq 'numista-backend')                  { throw 'must never deploy over numista-backend' }
if ($ProdBuckets -contains $UserContentBucket -or $UserContentBucket -like "*$ProdProject*") { throw 'preview must not use a production bucket' }
if ($sha -like 'c547b7a0*')                          { throw 'c547b7a0 is held and must never be deployed' }
$wt = Join-Path $env:TEMP 'net827_backend'
if ($wt.StartsWith($repo)) { throw 'worktree must be outside the repo' }
$envVars = "NUMISTA_ENV=preview,FIRESTORE_PROJECT_ID=$PreviewProject,FIREBASE_AUTH_PROJECT_ID=$ProdProject,STRIPE_EXPECTED_MODE=test,USER_CONTENT_BUCKET=$UserContentBucket"
$secrets = "STRIPE_SECRET_KEY=${KeySecret}:latest,STRIPE_WEBHOOK_SECRET=${WhSecret}:latest"
Set-Location $repo
try {
    Invoke-Native { git worktree add --detach $wt $sha }
    $src = Join-Path $wt 'numista_backend'
    if (Get-ChildItem -Path $src -Recurse -Filter 'serviceAccountKey*' -ErrorAction SilentlyContinue) { throw 'a service account key file is in the build source' }
    Invoke-Native { gcloud run deploy $Service --source $src --project $PreviewProject --region us-central1 --service-account $Sa --set-env-vars $envVars --set-secrets $secrets --allow-unauthenticated --quiet }
} finally {
    Set-Location $repo
    if (Test-Path $wt) { git worktree remove --force $wt }
    git worktree prune
}
```

(`--allow-unauthenticated` is needed because Stripe calls the webhook without a Google identity; app routes still require a Firebase ID token, `routes/deps.py:69-79`. `.dockerignore` already excludes `serviceAccountKey*.json` (`numista_backend/.dockerignore:20`) and git worktrees contain no untracked files; the explicit check is belt-and-braces.)

PV-5b (test Firestore only; seeds 105 coins for `ft-preview-03` under `users/{uid}/coins` so the Beta Special path is testable; refuses the production project):

```powershell
$ErrorActionPreference = 'Stop'
$PreviewProject = '<PREVIEW_PROJECT_UNKNOWN>'
$Uid03          = '<FT_PREVIEW_03_UID_FROM_PV5_OUTPUT>'
foreach ($v in @($PreviewProject, $Uid03)) { if ($v -like '<*') { throw "placeholder not filled: $v" } }
if ($PreviewProject -eq 'studio-9101802118-8c9a8') { throw 'seeding must never target production' }
$py = 'C:\Users\ericd\Documents\MyVertexProject\numista_backend\.venv\Scripts\python.exe'
$script = Join-Path $env:TEMP 'net827_pv5b.py'
@'
import sys
from google.cloud import firestore
project, uid = sys.argv[1], sys.argv[2]
if project == "studio-9101802118-8c9a8":
    raise SystemExit("refusing production")
db = firestore.Client(project=project)
batch = db.batch()
for i in range(105):
    batch.set(db.collection("users").document(uid).collection("coins").document("seed_%03d" % i),
              {"Year": "1921", "Denomination": "1 Dollar", "is_demo": False, "is_demo_cleared": False, "created_at": firestore.SERVER_TIMESTAMP})
batch.commit()
print("seeded 105 test coins in", project)
'@ | Set-Content -Encoding UTF8 $script
try {
    & $py $script $PreviewProject $Uid03
    if ($LASTEXITCODE -ne 0) { throw "PV-5b failed: $LASTEXITCODE" }
} finally {
    Remove-Item $script -ErrorAction SilentlyContinue
}
```

### 6.5 PV-5 / PV-6 synthetic tester accounts

PV-5 / PV-6 (one script, `-Action create` for PV-5, `-Action delete` for PV-6; v1.7 script unchanged except the parameter — A6 / v1.8 advisory 8):

```powershell
param([Parameter(Mandatory=$true)][ValidateSet('create','delete')][string]$Action)
$ErrorActionPreference = 'Stop'
$py = 'C:\Users\ericd\Documents\MyVertexProject\numista_backend\.venv\Scripts\python.exe'
$script = Join-Path $env:TEMP 'net827_ft_users.py'
@'
import getpass
import re
import sys
import firebase_admin
from firebase_admin import auth

PROD_AUTH_PROJECT = "studio-9101802118-8c9a8"
PATTERN = re.compile(r"^ft-preview-0[1-4]@numista\.ai$")
action = sys.argv[1]
emails = ["ft-preview-0%d@numista.ai" % n for n in range(1, 5)]
firebase_admin.initialize_app(options={"projectId": PROD_AUTH_PROJECT})
for email in emails:
    if not PATTERN.match(email):
        raise SystemExit("refusing non-synthetic email: " + email)
    if action == "create":
        password = getpass.getpass("password for " + email + ": ")
        user = auth.create_user(email=email, password=password, email_verified=True)
        print("created", email, user.uid)
    elif action == "delete":
        try:
            user = auth.get_user_by_email(email)
        except auth.UserNotFoundError:
            print("absent", email)
            continue
        auth.delete_user(user.uid)
        print("deleted", email, user.uid)
    else:
        raise SystemExit("action must be create or delete")
if action == "delete":
    for email in emails:
        try:
            auth.get_user_by_email(email)
            raise SystemExit("still present: " + email)
        except auth.UserNotFoundError:
            print("confirmed gone", email)
'@ | Set-Content -Encoding UTF8 $script
try {
    & $py $script $Action
    if ($LASTEXITCODE -ne 0) { throw "$Action failed: $LASTEXITCODE" }
} finally {
    Remove-Item $script -ErrorAction SilentlyContinue
}
```

PV-6 runs only **after Field Tester has finished**, and after PV-4.5 `check` (and, if it found anything, PV-4.5 `delete` under its own YES). If the script cannot run (no venv, no ADC), the step is BLOCKED with the exact error and Eric deletes the four accounts in the Firebase console; NET-827 is not complete until all four are confirmed gone. The test Firestore project's data is left in place unless Eric types YES to delete it.

### 6.6 PV-4 isolation proof and PV-4.5 production check

PV-4 (read-only; harvest H8 extended to every production bucket named in code; v1.8 IAM check kept):

```powershell
$ErrorActionPreference = 'Stop'
function Invoke-NativeCapture {
    param([scriptblock]$Cmd)
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { $out = & $Cmd 2>&1 } finally { $ErrorActionPreference = $old }
    return @{ Code = $LASTEXITCODE; Out = ($out | Out-String) }
}
$ProdProject    = 'studio-9101802118-8c9a8'
$ProdBuckets    = @('numista-uploads-studio-9101802118-8c9a8','studio-9101802118-8c9a8-uploads','numista-reference-library','studio-9101802118-8c9a8.firebasestorage.app','numista-uploads-studio-9101802118-8c9a8.firebasestorage.app')
$PreviewProject = '<PREVIEW_PROJECT_UNKNOWN>'
$Service        = '<PREVIEW_SERVICE_UNKNOWN>'
foreach ($v in @($PreviewProject, $Service)) { if ($v -like '<*') { throw "placeholder not filled: $v" } }
$r = Invoke-NativeCapture { gcloud run services describe $Service --project $PreviewProject --region us-central1 --format=json }
if ($r.Code -ne 0) { throw "describe failed: $($r.Out)" }
$json = $r.Out
$svc  = $json | ConvertFrom-Json
$envs = $svc.spec.template.spec.containers[0].env
$fp   = ($envs | Where-Object { $_.name -eq 'FIRESTORE_PROJECT_ID' }).value
$mode = ($envs | Where-Object { $_.name -eq 'NUMISTA_ENV' }).value
$ucb  = ($envs | Where-Object { $_.name -eq 'USER_CONTENT_BUCKET' }).value
$sem  = ($envs | Where-Object { $_.name -eq 'STRIPE_EXPECTED_MODE' }).value
if ($mode -ne 'preview')             { throw "NUMISTA_ENV is '$mode', expected preview" }
if ($fp -ne $PreviewProject)         { throw "FIRESTORE_PROJECT_ID is '$fp', expected the preview project" }
if ($fp -eq $ProdProject)            { throw 'preview points at the production Firestore project' }
if (-not $ucb -or $ProdBuckets -contains $ucb -or $ucb -like "*$ProdProject*") { throw "USER_CONTENT_BUCKET '$ucb' is missing or production" }
if ($sem -ne 'test')                 { throw "STRIPE_EXPECTED_MODE is '$sem', expected test" }
if ($json -match 'numista-backend')  { throw 'preview configuration references numista-backend' }
$Sa = $svc.spec.template.spec.serviceAccountName
if (-not $Sa) { throw 'preview serviceAccountName missing in Cloud Run spec' }
$p = Invoke-NativeCapture { gcloud projects get-iam-policy $ProdProject --flatten="bindings[].members" --filter="bindings.members:serviceAccount:$Sa" --format="value(bindings.role)" }
if ($p.Code -ne 0) { throw "project IAM read failed: $($p.Out)" }
if ($p.Out.Trim() -ne '') { throw "preview service account $Sa holds roles on the production project: $($p.Out)" }
foreach ($b in $ProdBuckets) {
    $bp = Invoke-NativeCapture { gcloud storage buckets get-iam-policy "gs://$b" --format=json }
    if ($bp.Code -ne 0) {
        if ($bp.Out -match '404|not found|does not exist') { "bucket $b not found: recorded, not applicable"; continue }
        throw "bucket IAM read failed for ${b}: $($bp.Out)"
    }
    if ($bp.Out -match [regex]::Escape($Sa)) { throw "preview service account $Sa has a binding on production bucket gs://$b" }
}
'PV-4 passed: config isolated; preview SA has no project-level or bucket-level roles on production (folder/org-level grants are not covered by this check)'
```

What PV-4 proves: the deployed configuration and IAM. Runtime isolation is the in-process guard (§6.1, tested in §7). CORS already allows the p7-gate URL (`main.py:54`, applied at `main.py:293-294`).

PV-4.5 (production; `-Action check` is read-only and prints paths only, never document contents; `-Action delete` needs its own typed Eric YES and deletes only under the four synthetic accounts; temp-file pattern; pattern guard; run after PV-5, before use and again before PV-6):

```powershell
param([ValidateSet('check','delete')][string]$Action = 'check')
$ErrorActionPreference = 'Stop'
$py = 'C:\Users\ericd\Documents\MyVertexProject\numista_backend\.venv\Scripts\python.exe'
$script = Join-Path $env:TEMP 'net827_pv45.py'
@'
import re
import sys
import firebase_admin
from firebase_admin import auth
from google.cloud import firestore

PROD = "studio-9101802118-8c9a8"
PATTERN = re.compile(r"^ft-preview-0[1-4]@numista\.ai$")
action = sys.argv[1]
if action not in ("check", "delete"):
    raise SystemExit("action must be check or delete")
firebase_admin.initialize_app(options={"projectId": PROD})
db = firestore.Client(project=PROD)
keys = []
for n in range(1, 5):
    email = "ft-preview-0%d@numista.ai" % n
    if not PATTERN.match(email):
        raise SystemExit("refusing non-synthetic email: " + email)
    keys.append(email)
    try:
        keys.append(auth.get_user_by_email(email).uid)
    except auth.UserNotFoundError:
        pass
found = []
for key in keys:
    ref = db.collection("users").document(key)
    if ref.get().exists:
        found.append(ref.path)
    for sub in ref.collections():
        if next(iter(sub.limit(1).stream()), None) is not None:
            found.append(ref.path + "/" + sub.id)
for p in found:
    print("FOUND", p)
if action == "check":
    if found:
        print("PV-4.5: synthetic data found in production Firestore; STOP and ask Eric")
        sys.exit(1)
    print("PV-4.5 passed: no synthetic-tester data in production Firestore")
else:
    for key in keys:
        db.recursive_delete(db.collection("users").document(key))
        print("deleted users/" + key + " (recursive)")
'@ | Set-Content -Encoding UTF8 $script
try {
    & $py $script $Action
    if ($LASTEXITCODE -ne 0) { throw "PV-4.5 $Action failed: $LASTEXITCODE" }
} finally {
    Remove-Item $script -ErrorAction SilentlyContinue
}
```

## 7. Verification (FT) with honest coverage (v1.7 §7 kept; lock/CSV tests restored — v1.8 R5; harvest H9/H10)

All run without any production write.

### 7.1 Local pytest (Firestore/GCS mocked by `numista_backend/conftest.py`), from a project virtual environment, never from PATH (Eric decided). Windows PowerShell 5.1 (v1.7 block, unchanged):

```powershell
$ErrorActionPreference = 'Stop'
function Invoke-Native {
    param([scriptblock]$Cmd)
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $Cmd } finally { $ErrorActionPreference = $old }
    if ($LASTEXITCODE -ne 0) { throw "Native command failed: $LASTEXITCODE" }
}
Set-Location 'C:\Users\ericd\Documents\MyVertexProject\numista_backend'
try {
    if (-not (Test-Path 'requirements.txt')) { throw 'requirements.txt not found' }
    Invoke-Native { py -m venv .venv }
    Invoke-Native { .\.venv\Scripts\python -m pip install -r requirements.txt pytest }
    Invoke-Native { .\.venv\Scripts\python -m pytest }
    'PYTEST PASSED'
} catch {
    "BLOCKED: $($_.Exception.Message)"
    exit 1
}
```

If `py` is not found, or any step fails, the step is recorded as BLOCKED with the exact error text and is never reported as passed. `.venv` is already ignored by `.gitignore` (`**/.venv/`). The whole existing suite (`numista_backend/tests/`) must still pass (no regression).

New test files and cases (all Stripe calls mocked; Firestore via an in-memory fake that supports `collection/document/get/set/delete/stream/transaction`, so the lock tests exercise real move logic, not a `MagicMock`):

`tests/test_net827_checkout.py` (v1.7 list, unchanged): allowlist rejects `power_user`, `sovereign`, `family_estate`, `bogus` (400, Stripe `create` not called); price table; subtotal mismatch / unpaid / uncoupon'd discount → no grant; Christmas coupon attached on annual in-window only (before start, after end, monthly: none); half-cent Christmas totals for Copper and Silver accepted; F&F valid/invalid promo; no stacking; no-user → event not `done`; claim lease cases; invoice and subscription events without session fields; refund and dispute cases in §4.4; Beta at 100 coins blocked at create (Stripe `create` not called), 101 allowed; (v1.9) Beta eligibility counts locked coins too: 60 visible + 50 locked = 110 → allowed; 60 visible + 40 locked = 100 → blocked; the same coin id visible and locked counts once; second Beta purchase after a refund blocked; backstop refund called once (`stripe.Refund.create` mocked); limits cases in §4.5. Added in v1.9.1 (D1): a user with only `users/{email}` (no `users/{uid}`) creates a Silver checkout → `users/{uid}` exists afterwards with no fields written by the create; then `checkout.session.completed` → granted (`stripe_tier` = `numismatist` on `users/{uid}`, event `done`); an existing `users/{uid}` with `default_sort_field` keeps it after the create (merge); the create-time write fails → 503 and Stripe `create` not called; `users/{uid}` deleted between create and webhook while `checkout_pending.session_id` matches → granted and the doc recreated; same with no `checkout_pending` but `firebase_auth.get_user` succeeding → granted; a uid with no doc, no matching `checkout_pending` and `get_user` raising → no grant, `retry`, 500; the same three grant cases for Beta Special and F&F. Added in v1.9.1 (admin): admin token, other uid → the field set above with `admin_view: true`, `reconciled: false`, and zero writes recorded by the fake (no coin moved even when that user is over the limit); admin token, own uid → reconcile runs; non-admin, other uid → 403. Added in v1.9: Christmas coupon with `session.created` missing → no grant (fail closed); a client-supplied `stripe_customer_id` on `users/{id}` is ignored by the billing portal, which uses only `entitlements/{uid}` verified by `stripe_customers/{cus}.uid == uid` (another user's customer id → 403); the checkout route is `POST /api/stripe/create-checkout-session` (route-table assertion).

`tests/test_net827_entitlement.py`:
- `to_epoch`: Timestamp, datetime, seconds, milliseconds, ISO string with `Z`, unparseable string → 0.0, missing → None.
- `effective_limit`: unexpired Beta → None on every tier (incl. `free`, `numismatist`); expired Beta → the tier limit; `power_user` → None; `beta_tester` / lifetime / `creation_timestamp < 1795669200000` → `family_estate` limit exactly as today; tier limits exactly §4.5 (`free` 10, `pro` 100, `numismatist` (Silver) 249, `dealer` (Platinum) 500, `estate` (Gold) None).
- `load_entitlement_profile`: comp flag only on `users/{email}` still counts; `stripe_tier` from `users/{uid}`; a read error raises (→ 503 at the route).
- Dedupe: 200 coins with the same ids in both folders count as 200, not 400; 150 email-only + 100 uid-only distinct = 250; mixed-case token email reads both forms.
- Only coins count: 50 currency + 50 wishlist + 10 coins on Free → count 10, nothing locked, currency/wishlist untouched.
- Lock: expired Beta with 300 unique coins on Platinum (`dealer`, 500) → nothing locked; on Silver (`numismatist`, 249) → 51 newest locked, oldest 249 visible; missing `created_at` coins sort by `added_at` (v1.9.1); coins with neither are kept (oldest) and none skipped; a roll-wizard-shaped coin (`added_at` ISO string, no `created_at`, `source: roll_wizard`) added last sorts newest; ties by id deterministic; a coin with copies in both folders is locked as a whole (both copies, each under its own owner key, `source_path` exact).
- Chunking: 260 copies to lock → at least 2 transactions, none over 200 copies / 400 writes; failure injected in chunk 2 → exception raised (no swallow), chunk 1 consistent, re-run completes with no duplicates.
- Concurrency: source deleted between stream and transaction → skipped, no locked ghost; source edited between stream and transaction → the locked copy holds the edited data.
- Unlock: upgrade to Gold restores all; upgrade with room for 10 restores the 10 oldest; each copy back to its exact folder; existing doc at `source_path` → not overwritten, `restore_conflict: true`, reported; legacy `locked_pending_upgrade: true` cleared to false after restore.
- Legacy round trip: a coin flagged `locked_pending_upgrade: true` by today's code stays visible and counted; `enforce_entitlement` applies the new design consistently.
- Reconcile on create: 10 server-added coins (`created_at` Timestamps) plus 1 roll-wizard-shaped direct client create (`added_at` = now, no `created_at`) on Free → `enforce_entitlement` moves that newest 1 into `locked_coins` and none of the 10 (v1.9.1 fixture).
- Add paths: each route listed in §4.8 at the limit → 403 `tier_limit_exceeded`; a Firestore read error during the check → 503 (never allowed); transfer claim of a coin at the limit → 403; claim of currency at the limit → allowed.
- By-id routes: a locked coin id → 403 `LOCKED_PENDING_UPGRADE` with no coin fields in the body; an unknown id → today's 404; another user's locked coin id → 404 (the lookup uses only the caller's owner keys).
- Cross-user: user A's token never reads or moves user B's coins in count, lock, unlock, CSV or by-id lookups.
- Clear collection (`main.py:8986`) and sandbox clear never delete `locked_coins` docs.

`tests/test_net827_export.py` (restored from v1.7 §4.8 — v1.8 R5):
- Expired Beta with 300 coins on Silver (`numismatist`): add 403, locked coin by-id 403, CSV still contains all 300 coins (249 `locked=false`, 51 `locked=true`) plus currency, banknotes, world_items and wishlist rows.
- Not expired: unlimited, nothing locked.
- Upgrade unlocks; CSV shows all `locked=false`.
- Formula-injection: cells starting with `=`, `+`, `-`, `@`, tab, CR are prefixed with `'`.
- **Unauthenticated CSV request → 401.** A query parameter naming another user is ignored (only the caller's rows).
- Duplicate coin across both folders → one row; Firestore read error → 503, no partial body.
- Available on Free with 0 coins (header only).

`tests/test_env_guard.py`:
- v1.7 cases: production with missing project → production; production with another project → refuses; preview missing project / production project → refuses; live key in preview → refuses; key/mode mismatch → refuses; `STRIPE_EXPECTED_MODE` unset with a key → refuses.
- Bucket: preview without `USER_CONTENT_BUCKET` → refuses; preview with each of the five production bucket names, and with any name containing `studio-9101802118-8c9a8` → refuses; preview with a `serviceAccountKey.json` in the backend dir (tmp path) → refuses.
- `bucket_for`: production returns today's exact value for every call site in §4.11 (rows 8, 10-14, 18, 19), including the `GCS_BUCKET_NAME` override; preview returns the preview bucket for all.
- `GuardedStorageClient`: in preview, `.bucket(<each production name>)`, `.get_bucket`, `.lookup_bucket` raise; `.bucket(<preview bucket>)` delegates; any other attribute raises; in production all calls delegate unchanged.
- `init_firebase_admin` passes `projectId = FIREBASE_AUTH_PROJECT_ID`; is idempotent.
- `require_production` → 503 in preview for the brain reprocess, canon sync, cron scraper and scrape-url routes; the deep-dive scrape thread is not started in preview.

The static import-graph test is in §7.3.

Proves logic only, not Stripe or Google behaviour.

### 7.2 Firestore rules emulator tests (no deploy; harvest H10)

Added to the existing `numista_mobile/firestore.rules.test.js` (Jest, emulator at `127.0.0.1:8080`, lines 33-40; `package.json` script `jest firestore.rules.test.js`), run against the **unchanged** `firestore.rules` (SHA-256 `e650713b…2f9c86`):

```powershell
$ErrorActionPreference = 'Stop'
function Invoke-Native {
    param([scriptblock]$Cmd)
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $Cmd } finally { $ErrorActionPreference = $old }
    if ($LASTEXITCODE -ne 0) { throw "Native command failed: $LASTEXITCODE" }
}
Set-Location 'C:\Users\ericd\Documents\MyVertexProject\numista_mobile'
try {
    Invoke-Native { npm install }
    Invoke-Native { firebase emulators:exec --only firestore "npx jest firestore.rules.test.js" }
    'RULES TESTS PASSED'
} catch {
    "BLOCKED: $($_.Exception.Message)"
    exit 1
}
```

(The emulator is local; `emulators:exec` deploys nothing. If Java or the Firebase CLI is missing, BLOCKED with the exact error.)

Cases:
1. Owner (email token) unfiltered `getDocs(collection(db, "users/<email>/coins"))` succeeds (no lock-out; v1.8 R1 regression test).
2. Owner (uid token) unfiltered list of `users/<uid>/coins` succeeds.
3. Owner create coin with `is_demo: false` and `is_demo_cleared: false` succeeds; update of another field succeeds; existing `is_demo` cases still pass unchanged.
4. Owner read/list/write of `locked_coins/<email>/coins/x`, `locked_coins/<uid>/coins/x` → fails.
5. Owner read/write of `entitlements/<uid>`, `stripe_customers/cus_x`, `stripe_payments/pi_x`, `stripe_events/evt_x` → fails.
6. Owner set `stripe_tier`, `tier`, `beta_tester`, `admin` on own user doc → fails; owner delete own user doc → fails.
7. Non-owner read of another user's coins → fails.
8. Owner currency and wishlist read/write still succeed (they are never locked).

RX variant (only if §9.4 is chosen): the same file run against the RX candidate rules adds: owner create/update coin with `locked_pending_upgrade` → fails; owner set `power_user`, `creation_timestamp`, `stripe_customer_id`, `stripe_subscription_id`, `beta_special_until`, `beta_special_purchased` on own user doc → fails; cases 1-8 still pass; a new user's first create of their profile without those keys still succeeds.

### 7.3 Static import-graph test (local) and HTTP checks against the preview (no sign-in on p7-gate)

`tests/test_no_unguarded_clients.py` (static import graph; harvest H9 with the v1.8 gaps closed): AST walk from `main.py` following every import, module-level **and inside functions** (so `brain_processor`, `services.canon_sync_service`, `numista_scraper.*`, `services.transfer_service` are included). Fails if any module other than `env_guard.py` contains `firestore.Client(`, `firestore.client(`, `storage.Client(`, `gcs.Client(`, `_gcs.Client(`, `gcs_storage.Client(` or `firebase_admin.initialize_app(`, or a string literal equal to a production bucket name outside an `env_guard.bucket_for(...)` call's first argument. Allowlisted (documented, AI/search only): the rows under "AI/search clients" in §4.11. Excluded (not imported by `main.py`): `scan_service/` except `collection_inventory.py`, standalone scripts. The test must find the 22 inventory rows' modules in its walk (assert the module set contains them), so a dropped module fails the test.

After deploy, HTTP only:

- Unauthenticated `POST <preview URL>/api/stripe/create-checkout-session` → 401.
- Unsigned `POST <preview URL>/api/stripe/webhook` → 400.
- Unauthenticated `GET <preview URL>/api/export/collection.csv` → 401.
- `GET <preview URL>/api/stripe/subscription-status?uid=x` without a token → 401.
Proves routing, auth and signature enforcement only.

### 7.4 Dart

`flutter analyze` exit code 0 and `flutter test` on any new test (§4.7 `refreshEntitlement`: called once from `base_layout.dart` `initState` after sign-in; a failure is logged and never blocks the app).

Not proven here: real payment flow, Stripe-side discount amounts and the Stripe response field shapes used in `decide_grant` and `lookup_ff_promotion`, refunds and disputes against real charges.

## 8. Gated real-checkout tests (PX4; v1.7 N2)

Test-card checkouts write Firestore, which after PV-1 is only the separate test Firestore. Each needs its own typed Eric YES, uses the synthetic testers only, and is never reported as a pass of FT. **No sign-in on p7-gate**: the tester path is a scripted HTTP client run by Eric on his laptop:

1. Eric runs the script below; it asks for the tester email and password at run time (`Read-Host -AsSecureString`; never written to disk or echoed).
2. It reads the public web `apiKey` from `numista_mobile/lib/firebase_options.dart:50` at run time (not copied into the plan) and calls `https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=<apiKey>` to get an ID token from production Firebase Auth. This creates no Firestore data.
3. It calls `POST <preview URL>/api/stripe/create-checkout-session` with `Authorization: Bearer <token>` and the plan body, and prints only the HTTP status and the returned `checkout_url`.
4. Eric opens `checkout_url` in his browser and pays with a Stripe test card (`4242…`). The test webhook (PV-2b) fulfils into the test Firestore.
5. The script then calls `GET <preview URL>/api/stripe/subscription-status?uid=<uid>` and prints the status JSON.

```powershell
param([Parameter(Mandatory=$true)][string]$PreviewUrl, [Parameter(Mandatory=$true)][string]$Tier, [ValidateSet('month','year')][string]$Interval = 'month', [string]$Promo = '', [switch]$BetaSpecial)
$ErrorActionPreference = 'Stop'
if ($PreviewUrl -match 'numista-backend') { throw 'must target the preview service, never numista-backend' }
$opts = Get-Content 'C:\Users\ericd\Documents\MyVertexProject\numista_mobile\lib\firebase_options.dart' -Raw
$m = [regex]::Match($opts, "apiKey:\s*'([^']+)'")
if (-not $m.Success) { throw 'apiKey not found in firebase_options.dart' }
$apiKey = $m.Groups[1].Value
$email = Read-Host 'tester email'
if ($email -notmatch '^ft-preview-0[1-4]@numista\.ai$') { throw 'synthetic testers only' }
$sec = Read-Host 'password' -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
try { $pw = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
$signin = Invoke-RestMethod -Method Post -Uri "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=$apiKey" -ContentType 'application/json' -Body (@{ email = $email; password = $pw; returnSecureToken = $true } | ConvertTo-Json)
$pw = $null
$h = @{ Authorization = "Bearer $($signin.idToken)" }
$req = @{ tier = $Tier; interval = $Interval }
if ($Promo -ne '') { $req.promo = $Promo }
if ($BetaSpecial) { $req.beta_special = $true }
$body = $req | ConvertTo-Json
$r = Invoke-RestMethod -Method Post -Uri "$PreviewUrl/api/stripe/create-checkout-session" -Headers $h -ContentType 'application/json' -Body $body
"checkout_url: $($r.checkout_url)"
Read-Host 'Pay with a Stripe test card in the browser, then press Enter'
Invoke-RestMethod -Method Get -Uri "$PreviewUrl/api/stripe/subscription-status?uid=$($signin.localId)" -Headers $h | ConvertTo-Json -Depth 5
```

(Body fields `tier`, `interval`, optional `promo` and `beta_special` are the §4.1 request model (today's model has only `tier`, `numista_backend/schemas/payment_schemas.py:8-10`); if they differ at build time the builder updates this script in the same commit. If the endpoint rejects the call, the run is recorded as failed with the exact status; nothing is retried against production.)

Planned runs: ft-preview-01 Free limits (add 11th coin → 403; CSV works); ft-preview-02 Silver (`-Tier numismatist -Interval month`) paid → grant; refund in the Stripe test dashboard → access removed, coins over 10 locked, CSV complete; ft-preview-03 Beta Special after PV-5b seeding (105 coins → allowed), and a second Beta attempt → blocked; ft-preview-04 F&F promo and (only on or after 26 Nov 2026 12:01 AM ET) Christmas `year`. The first gated run also records the real Stripe field shapes that `decide_grant` and `lookup_ff_promotion` rely on, and a sandbox Christmas total for Copper and Silver (rounding). If a shape differs, the code fails closed (no grant) and the difference is reported; nothing is guessed.

## 9. Deploy, live keys, rollback

### 9.1 Sequencing and pre-deploy record (v1.7, unchanged)

Sequencing: the NET-827 preview deploy to `p7-gate` replaces the NET-816 preview currently there (`a3d7dca2`), so it waits until NET-816 has had its own YES and Field Tester pass, per the queued baton.

Pre-deploy (read-only) record, Windows PowerShell 5.1: p7-gate's current state and the current production backend revision. Commands (read-only):

```powershell
$ErrorActionPreference = 'Stop'
function Invoke-Native {
    param([scriptblock]$Cmd)
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $Cmd } finally { $ErrorActionPreference = $old }
    if ($LASTEXITCODE -ne 0) { throw "Native command failed: $LASTEXITCODE" }
}
Set-Location 'C:\Users\ericd\Documents\MyVertexProject\numista_mobile'
Invoke-Native { firebase hosting:channel:list --project studio-9101802118-8c9a8 }
Invoke-Native { gcloud run services describe numista-backend --project studio-9101802118-8c9a8 --region us-central1 --format="value(status.latestReadyRevisionName)" }
```

The record names RT-A (a known commit that is not held and is recorded as the commit currently on p7-gate, if recoverable) or RT-B (no redeploy; the default). If neither can be proven, use RT-B.

### 9.2 Preview deploy and rollback (v1.7, unchanged except the YES wording)

Preview backend: PV-0 to PV-6 (§6.4-§6.6). Hosting deploy (also used for the RT-A redeploy, with `$PreviewUrl = ''` so the rolled-back build has no override):

```powershell
$ErrorActionPreference = 'Stop'
function Invoke-Native {
    param([scriptblock]$Cmd)
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $Cmd } finally { $ErrorActionPreference = $old }
    if ($LASTEXITCODE -ne 0) { throw "Native command failed: $LASTEXITCODE" }
}
$repo       = 'C:\Users\ericd\Documents\MyVertexProject'
$sha        = '<BUILT_SHA_UNKNOWN_RECORD_AT_EXECUTION>'
$PreviewUrl = '<PREVIEW_URL_UNKNOWN_RECORD_AT_EXECUTION>'   # set to '' for an RT-A redeploy
if ($sha -like '<*') { throw 'fill $sha first' }
if ($sha -like 'c547b7a0*') { throw 'c547b7a0 is held and must never be deployed' }
if ($PreviewUrl -like '<*') { throw 'fill $PreviewUrl first (or set it to an empty string for RT-A)' }
$wt = Join-Path $env:TEMP 'net827_build'
if ($wt.StartsWith($repo)) { throw 'worktree must be outside the repo' }
$defineArgs = @()
if ($PreviewUrl -ne '') { $defineArgs += "--dart-define=API_BASE_URL=$PreviewUrl" }
Set-Location $repo
try {
    Invoke-Native { git worktree add --detach $wt $sha }
    Set-Location (Join-Path $wt 'numista_mobile')
    Invoke-Native { flutter build web --release --base-href "/" @defineArgs }
    Invoke-Native { firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8 }
} finally {
    Set-Location $repo
    if (Test-Path $wt) { git worktree remove --force $wt }
    git worktree prune
}
```

Eric's YES must name: the built commit SHA, the targets (p7-gate and the preview backend service), and the rollback target. It must also state: no Firestore rules change, no production Cloud Run change, `numista-backend` untouched, main stays `9f04550a`, holds `74611e05` and `41b8bd5f` stand.

Rollback: source: `git revert --no-edit <sha>`. Hosting: redeploy RT-A to p7-gate with the block above, or RT-B (leave as is; channel deletion only with Eric's typed YES). Preview backend: delete or route-disable only the preview Cloud Run service and its test secrets in the test project (exact names recorded at creation); never touch `numista-backend`. The test Firestore project is left in place unless Eric types YES to delete it. Channel and service deletion each need Eric's typed YES.

### 9.3 Live keys and go-live (K1): GL-1, LK-1…LK-8. DO NOT RUN NOW.

Precondition: HOLD `41b8bd5f` lifted by new CoS written confirmation plus Eric's separate typed YES. Eric performs these in his own Stripe/Google login; no agent creates or reads keys. main stays `9f04550a` until then.
- **GL-1 (new; harvest X5/G8)** Before the v1.9 backend reaches production: Eric records, read-only, whether the production `STRIPE_SECRET_KEY` today is a live or a test key (prefix only, read by Eric in the Secret Manager console; never copied into any file or chat), and sets `STRIPE_EXPECTED_MODE` on `numista-backend` to match in the same go-live deploy. Because `env_guard.check_stripe_key` refuses to start when a key is present and `STRIPE_EXPECTED_MODE` is missing or mismatched, the go-live deploy is not done without GL-1; if GL-1 cannot be read, go-live is BLOCKED (fail closed; production keeps running the current revision). The go-live deploy also sets nothing else new in production: `NUMISTA_ENV` defaults to `production`, `FIRESTORE_PROJECT_ID` defaults to production, `USER_CONTENT_BUCKET` defaults to today's bucket.
- LK-1 Eric creates live products/prices matching §0 (the server uses `price_data`, so these are for reporting only).
- LK-2 Eric creates the live F&F coupon with its promotion code (max 500 redemptions) and, ahead of the start, the live Christmas coupon (50% off, `once`, `redeem_by` 1798261199). A coupon has no inactive state, so the control is the server gate plus withholding the coupon id from the service env until LK-8.
- LK-3 Eric stores the live secret key in Secret Manager under a name chosen then (UNKNOWN now), mounted only on `numista-backend` (the production Cloud Run service) under the later go-live gate.
- LK-4 Eric creates the live webhook endpoint (`https://<production backend>/api/stripe/webhook`, same event list as PV-2b) with its own signing secret, stored as a separate secret.
- LK-5 Code mode check: `env_guard.check_stripe_key` refuses to start when the key prefix (live vs test) does not match `STRIPE_EXPECTED_MODE` (set at GL-1, then `live`).
- LK-6 Confirm no test webhook secret is mounted on the production service.
- LK-7 Smoke test with a real card only under separate Eric YES.
- LK-8 At or after 1795669260, Eric sets the Christmas coupon id in the production service env (the server gate still enforces the window).

### 9.4 Optional rules hardening RX (PRODUCTION change; not part of NET-827's preview; CoS direction 3; harvest G1/G3)

**Status: not needed for NET-827 and not run in NET-827.** It closes the pre-existing open risks 14 and 15 and adds defence in depth. It is a **production change** (the Firestore rules are shared by every environment that uses project `studio-9101802118-8c9a8`; the preview's test Firestore has its own rules). It runs only under HOLD `41b8bd5f` being lifted, with **its own scoped Eric YES** naming: "RX rules change, file SHA-256 <new SHA>, backup SHA-256 e650713b…2f9c86, rollback block 9.4-R". Sequenced after the v1.9 backend is live in production (so locked coins already live in `locked_coins` and nothing relies on the flag). It is never bundled with any other deploy.

**Current file:** `numista_mobile/firestore.rules`, SHA-256 `e650713b9051904fa52efbe046b13986ad5896a435b89cea13a1ac53da2f9c86` (deployed by `numista_mobile/firebase.json:2-5`; `.firebaserc` default `studio-9101802118-8c9a8`). `numista_backend/firestore.rules` (SHA-256 `d087e8ae…`) is a different, undeployed file (`numista_backend/firebase.json` deploys functions only) and is not touched.

**Exact diff (additions only; every other byte identical; line numbers from the current file):**

```diff
@@ firestore.rules:55-58 (coin create) @@
       allow create: if isOwner(email)
                     && request.resource.data.keys().hasAll(['is_demo', 'is_demo_cleared'])
                     && request.resource.data.is_demo == false
-                    && request.resource.data.is_demo_cleared == false;
+                    && request.resource.data.is_demo_cleared == false
+                    && !request.resource.data.keys().hasAny(['locked_pending_upgrade']);
@@ firestore.rules:63-66 (coin update) @@
       allow update: if isOwner(email)
                     && !request.resource.data.diff(resource.data)
                           .affectedKeys()
-                          .hasAny(['is_demo', 'is_demo_cleared']);
+                          .hasAny(['is_demo', 'is_demo_cleared', 'locked_pending_upgrade']);
@@ firestore.rules:86-87 (_serverOnlyKeys) @@
       return ['tier', 'stripe_tier', 'beta_tester', 'is_lifetime_family_estate',
-              'is_ai_qc_account', 'is_bot_account', 'sandbox_cleared', 'admin'];
+              'is_ai_qc_account', 'is_bot_account', 'sandbox_cleared', 'admin',
+              'creation_timestamp', 'power_user', 'stripe_customer_id', 'stripe_subscription_id',
+              'beta_special_until', 'beta_special_purchased', 'locked_pending_upgrade'];
@@ firestore.rules:110 and :115 (both wildcard exclusion lists; identical edit) @@
-        && !(sub in ['settings', 'estate_reports', 'morgan_action_log', 'trash', 'audit_log', 'coins', 'profile', 'morgan_proposals', 'subaccounts', 'subscription', 'transferred_coins', 'transferred_currency']);
+        && !(sub in ['settings', 'estate_reports', 'morgan_action_log', 'trash', 'audit_log', 'coins', 'profile', 'morgan_proposals', 'subaccounts', 'subscription', 'transferred_coins', 'transferred_currency', 'locked_coins']);
@@ firestore.rules:345 (insert before the "Deny everything else" comment) @@
+    // ── NET-827 server-only collections (explicit; also covered by the deny-all) ──
+    match /locked_coins/{document=**} { allow read, write: if false; }
+    match /entitlements/{document=**} { allow read, write: if false; }
+    match /stripe_customers/{document=**} { allow read, write: if false; }
+    match /stripe_payments/{document=**} { allow read, write: if false; }
+
     // ── Deny everything else ──────────────────────────────────────────────────
```

Every change only removes client permissions (adds conditions or exclusions) or adds explicit denies; no rule grants anything new. Users still create and update their own profile doc (needed by the app) but can never write any entitlement or limit field on it (direction 3: users never write their own account entitlements). Pre-checks before the YES: `git grep -n "creation_timestamp\|power_user\|stripe_customer_id\|stripe_subscription_id\|beta_special\|locked_pending_upgrade" -- numista_mobile/lib` returns nothing (true at `a3d7dca2`; re-run at RX time; any match makes RX BLOCKED until reviewed), and §7.2's RX variant passes in the emulator. A CI-style check confirms the diff: `git diff --stat` shows only `numista_mobile/firestore.rules` and the test file, and `git diff -U0` contains only the hunks above.

**Backup (read-only, before deploy; byte-exact live ruleset via the Firebase Rules REST API; v1.9.1 D2: written to a temp name and kept only if its SHA-256 matches; an existing backup is never overwritten):**

```powershell
$ErrorActionPreference = 'Stop'
$ProdProject = 'studio-9101802118-8c9a8'
$Expected    = 'e650713b9051904fa52efbe046b13986ad5896a435b89cea13a1ac53da2f9c86'
function Get-Sha256Hex([byte[]]$bytes) {
    $h = [Security.Cryptography.SHA256]::Create()
    try { return (($h.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join '') } finally { $h.Dispose() }
}
$token = (& gcloud auth print-access-token)
if ($LASTEXITCODE -ne 0 -or -not $token) { throw 'no access token' }
$h = @{ Authorization = "Bearer $token"; 'x-goog-user-project' = $ProdProject }
$rel = Invoke-RestMethod -Headers $h -Uri "https://firebaserules.googleapis.com/v1/projects/$ProdProject/releases/cloud.firestore"
$rs  = Invoke-RestMethod -Headers $h -Uri "https://firebaserules.googleapis.com/v1/$($rel.rulesetName)"
if ($rs.source.files.Count -ne 1) { throw "expected 1 source file, got $($rs.source.files.Count)" }
$bytes = (New-Object Text.UTF8Encoding $false).GetBytes($rs.source.files[0].content)
$sha = Get-Sha256Hex $bytes
"live ruleset: $($rel.rulesetName)  sha256: $sha"
if ($sha -ne $Expected) { throw "live rules differ from e650713b...; STOP: RX is BLOCKED until Eric and CoS review the live file (nothing written)" }
$backupDir = Join-Path $env:TEMP 'net827_rules_backup'
$backup    = Join-Path $backupDir 'firestore.rules'
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
if (Test-Path $backup) {
    $old = (Get-FileHash -Algorithm SHA256 $backup).Hash.ToLower()
    if ($old -ne $Expected) { throw "an existing backup has SHA $old (not e650713b...); STOP: do not overwrite it; ask Eric and CoS" }
    'existing backup already matches e650713b...; kept unchanged'
} else {
    $tmp = Join-Path $backupDir 'firestore.rules.tmp'
    [IO.File]::WriteAllBytes($tmp, $bytes)
    $chk = (Get-FileHash -Algorithm SHA256 $tmp).Hash.ToLower()
    if ($chk -ne $Expected) { Remove-Item $tmp -Force; throw "written backup SHA $chk does not match; nothing kept" }
    Move-Item -Path $tmp -Destination $backup
    'backup written and verified'
}
'{"firestore":{"rules":"firestore.rules"}}' | Set-Content -Encoding ASCII (Join-Path $backupDir 'firebase.json')
```

**Deploy (only after the YES; rules only, never indexes or hosting; from a worktree of the RX commit; v1.9.1 D2: the live ruleset is re-read and its SHA-256 compared immediately before `firebase deploy`; this block never writes the backup folder):**

```powershell
$ErrorActionPreference = 'Stop'
function Invoke-Native {
    param([scriptblock]$Cmd)
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $Cmd } finally { $ErrorActionPreference = $old }
    if ($LASTEXITCODE -ne 0) { throw "Native command failed: $LASTEXITCODE" }
}
function Get-Sha256Hex([byte[]]$bytes) {
    $h = [Security.Cryptography.SHA256]::Create()
    try { return (($h.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join '') } finally { $h.Dispose() }
}
$repo        = 'C:\Users\ericd\Documents\MyVertexProject'
$ProdProject = 'studio-9101802118-8c9a8'
$Expected    = 'e650713b9051904fa52efbe046b13986ad5896a435b89cea13a1ac53da2f9c86'
$rxSha       = '<RX_COMMIT_SHA_UNKNOWN_RECORD_AT_EXECUTION>'
$rxFile      = '<RX_FILE_SHA256_FROM_THE_YES>'
foreach ($v in @($rxSha, $rxFile)) { if ($v -like '<*') { throw "placeholder not filled: $v" } }
$backup = Join-Path $env:TEMP 'net827_rules_backup\firestore.rules'
if (-not (Test-Path $backup)) { throw 'run the backup block first' }
if ((Get-FileHash -Algorithm SHA256 $backup).Hash.ToLower() -ne $Expected) { throw 'backup file SHA is not e650713b...; STOP' }
$wt = Join-Path $env:TEMP 'net827_rules'
if ($wt.StartsWith($repo)) { throw 'worktree must be outside the repo' }
Set-Location $repo
try {
    Invoke-Native { git -c core.autocrlf=false worktree add --detach $wt $rxSha }
    Set-Location (Join-Path $wt 'numista_mobile')
    $got = (Get-FileHash -Algorithm SHA256 'firestore.rules').Hash.ToLower()
    if ($got -ne $rxFile.ToLower()) { throw "rules file SHA $got does not match the YES" }
    # Immediately before deploy: re-read the LIVE ruleset (in memory only) and require e650713b...
    $token = (& gcloud auth print-access-token)
    if ($LASTEXITCODE -ne 0 -or -not $token) { throw 'no access token' }
    $h = @{ Authorization = "Bearer $token"; 'x-goog-user-project' = $ProdProject }
    $rel = Invoke-RestMethod -Headers $h -Uri "https://firebaserules.googleapis.com/v1/projects/$ProdProject/releases/cloud.firestore"
    $rs  = Invoke-RestMethod -Headers $h -Uri "https://firebaserules.googleapis.com/v1/$($rel.rulesetName)"
    if ($rs.source.files.Count -ne 1) { throw "expected 1 live source file, got $($rs.source.files.Count)" }
    $live = Get-Sha256Hex ((New-Object Text.UTF8Encoding $false).GetBytes($rs.source.files[0].content))
    if ($live -ne $Expected) { throw "live rules changed since the backup (sha $live); STOP: nothing deployed" }
    "live rules confirmed e650713b... ($($rel.rulesetName)); deploying"
    Invoke-Native { firebase deploy --only firestore:rules --project studio-9101802118-8c9a8 }
} finally {
    Set-Location $repo
    if (Test-Path $wt) { git worktree remove --force $wt }
    git worktree prune
}
```

(`core.autocrlf=false` keeps the worktree file byte-identical to the commit so the SHA in the YES is the LF file's SHA; the YES records that it is the LF SHA.)

**Post-deploy verification (scripted; own folder; expected SHA = the RX file; never touches the backup folder):**

```powershell
$ErrorActionPreference = 'Stop'
function Get-Sha256Hex([byte[]]$bytes) {
    $h = [Security.Cryptography.SHA256]::Create()
    try { return (($h.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join '') } finally { $h.Dispose() }
}
$ProdProject = 'studio-9101802118-8c9a8'
$rxFile      = '<RX_FILE_SHA256_FROM_THE_YES>'
if ($rxFile -like '<*') { throw 'placeholder not filled: rxFile' }
$verifyDir = Join-Path $env:TEMP 'net827_rules_verify'
if ($verifyDir -eq (Join-Path $env:TEMP 'net827_rules_backup')) { throw 'verify folder must not be the backup folder' }
New-Item -ItemType Directory -Force -Path $verifyDir | Out-Null
$token = (& gcloud auth print-access-token)
if ($LASTEXITCODE -ne 0 -or -not $token) { throw 'no access token' }
$h = @{ Authorization = "Bearer $token"; 'x-goog-user-project' = $ProdProject }
$rel = Invoke-RestMethod -Headers $h -Uri "https://firebaserules.googleapis.com/v1/projects/$ProdProject/releases/cloud.firestore"
$rs  = Invoke-RestMethod -Headers $h -Uri "https://firebaserules.googleapis.com/v1/$($rel.rulesetName)"
$bytes = (New-Object Text.UTF8Encoding $false).GetBytes($rs.source.files[0].content)
[IO.File]::WriteAllBytes((Join-Path $verifyDir 'live_after_rx.rules'), $bytes)
$sha = Get-Sha256Hex $bytes
"live after RX: $($rel.rulesetName)  sha256: $sha"
if ($sha -ne $rxFile.ToLower()) { throw "live rules are not the RX file; run Rollback 9.4-R now" }
'PV-RX verify passed: live rules equal the RX file'
```

Then a signed-in smoke by Eric on production (open the app, collection loads, add a coin) only if Eric chooses — no synthetic tester signs in on production. If the smoke fails, run Rollback 9.4-R.

**Rollback 9.4-R (runnable; restores the byte-exact backup, or, if the backup is missing or does not match, the same bytes from git at `a3d7dca2`):**

```powershell
$ErrorActionPreference = 'Stop'
function Invoke-Native {
    param([scriptblock]$Cmd)
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $Cmd } finally { $ErrorActionPreference = $old }
    if ($LASTEXITCODE -ne 0) { throw "Native command failed: $LASTEXITCODE" }
}
function Get-Sha256Hex([byte[]]$bytes) {
    $h = [Security.Cryptography.SHA256]::Create()
    try { return (($h.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join '') } finally { $h.Dispose() }
}
$repo        = 'C:\Users\ericd\Documents\MyVertexProject'
$ProdProject = 'studio-9101802118-8c9a8'
$Expected    = 'e650713b9051904fa52efbe046b13986ad5896a435b89cea13a1ac53da2f9c86'
$backupDir   = Join-Path $env:TEMP 'net827_rules_backup'
$backup      = Join-Path $backupDir 'firestore.rules'
$deployDir   = $null
if ((Test-Path $backup) -and ((Get-FileHash -Algorithm SHA256 $backup).Hash.ToLower() -eq $Expected)) {
    $deployDir = $backupDir
    'using the verified backup'
} else {
    'backup missing or not e650713b...; using git blob a3d7dca2:numista_mobile/firestore.rules'
    $deployDir = Join-Path $env:TEMP 'net827_rules_rollback'
    New-Item -ItemType Directory -Force -Path $deployDir | Out-Null
    $out = Join-Path $deployDir 'firestore.rules'
    $psi = New-Object Diagnostics.ProcessStartInfo
    $psi.FileName = 'git'
    $psi.Arguments = "-C `"$repo`" cat-file blob a3d7dca2:numista_mobile/firestore.rules"
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $p = [Diagnostics.Process]::Start($psi)
    $fs = [IO.File]::Create($out)
    try { $p.StandardOutput.BaseStream.CopyTo($fs) } finally { $fs.Close() }
    $p.WaitForExit()
    if ($p.ExitCode -ne 0) { throw "git cat-file failed: $($p.ExitCode)" }
    $sha = (Get-FileHash -Algorithm SHA256 $out).Hash.ToLower()
    if ($sha -ne $Expected) { throw "git blob SHA $sha is not e650713b...; STOP and ask Eric and CoS" }
    '{"firestore":{"rules":"firestore.rules"}}' | Set-Content -Encoding ASCII (Join-Path $deployDir 'firebase.json')
}
Set-Location $deployDir
Invoke-Native { firebase deploy --only firestore:rules --project studio-9101802118-8c9a8 }
$token = (& gcloud auth print-access-token)
if ($LASTEXITCODE -ne 0 -or -not $token) { throw 'rolled back, but no token to verify; verify by hand' }
$h = @{ Authorization = "Bearer $token"; 'x-goog-user-project' = $ProdProject }
$rel = Invoke-RestMethod -Headers $h -Uri "https://firebaserules.googleapis.com/v1/projects/$ProdProject/releases/cloud.firestore"
$rs  = Invoke-RestMethod -Headers $h -Uri "https://firebaserules.googleapis.com/v1/$($rel.rulesetName)"
$live = Get-Sha256Hex ((New-Object Text.UTF8Encoding $false).GetBytes($rs.source.files[0].content))
if ($live -ne $Expected) { throw "after rollback live sha is $live, not e650713b...; escalate to Eric now" }
'Rolled back and verified: live rules are e650713b...'
```

The backup folder is written only by the backup block, only once, and only with bytes whose SHA-256 is `e650713b…`; no later step writes to it. Rollback is a production change too and is pre-approved only as part of RX's YES.

## 10. Open questions / facts not available

Closed by Eric (incl. 10 Nov 5:36 PM ET: expiry/overflow lock + CSV, synthetic preview testers, unverified Stripe shapes accepted): Christmas start/end (12:01 AM ET 26 Nov to 11:59:59 PM ET 25 Dec), Silver 249, Beta capacity (unlimited for 6 months), Beta once per account ever including refunds, Beta at 100 coins or fewer (block at create + auto-refund backstop), partial refunds (log only), non-US allowed, preview isolation with its own test Firestore, pytest via venv. CoS correction applied: Gold unlimited from 501.

1. **OPEN RISK (Eric, 10 Nov 5:16 PM ET):** foreign sales tax/legal review is deferred. It must be reviewed before any marketing outside the US. Non-US buyers are allowed now; Stripe Tax is off.
2. The production backend's current Stripe env (live or test key) is not verifiable here; recorded at GL-1 (§9.3) before go-live, never guessed.
3. Existing legacy `estate` ($29/yr) users: proposed no change; confirm.
4. CLOSED (v1.8 advisory 6): no in-app upgrade button for testers; testers use the scripted HTTP client only (§8), because nobody signs in on p7-gate.
5. Sandbox monthly/yearly price-ID mapping is unverified; not needed (the server uses `price_data`).
6. Preview project, service name, URL, service account, preview bucket, test secret names, test Firestore id, built SHA and rollback target: UNKNOWN; record at execution time.
7. Whether `py` exists on EDS_Laptop: unknown until the step runs (BLOCKED if not).
8. CLOSED (Eric): expiry/overflow handling is specified in §4.8.
9. CLOSED (Eric): synthetic testers `ft-preview-01..04@numista.ai` in production Auth, listed in §6.3 with cleanup PV-6.
10. Stripe response shapes used by `decide_grant` and `lookup_ff_promotion` (`total_details.breakdown.discounts`, promotion-code coupon field) and Stripe's real rounding of the Christmas total on Copper/Silver are not verified; Eric accepted this as written (10 Nov 5:36 PM ET): they are recorded in the first gated sandbox run, and the code fails closed if they differ.
11. CLOSED: CSV columns are specified in §4.10 (fixed leading columns, then the sorted union of each document's own fields; nothing invented); lock ordering moved to 13.
12. Whether `gcloud run deploy --source` can build the existing backend (it has `numista_backend/Dockerfile`, `CMD` at line 24); BLOCKED with the exact error if not.
13. **OPEN QUESTION (Eric): lock order.** The plan keeps today's behaviour (`numista_backend/tier_gatekeeper.py:327-334`: oldest coins stay visible, the newest are locked), with the add time read from `created_at`, else `added_at` (v1.9.1, §4.8), so coins added directly in the app are ordered by when they were added. Eric may instead choose "most valuable stay visible" or "user picks"; either would be a later change. Until Eric answers, today's order applies.
14. **OPEN RISK (pre-existing, not caused by NET-827):** `creation_timestamp` on the user doc is client-writable and grants `family_estate` when below 1795669200000 (`numista_backend/tier_gatekeeper.py:146-149`). A user could set it to get 2,500 coins free. Closed only by RX (§9.4), a production change needing its own YES. PV-0 records how many users have it.
15. **OPEN RISK (pre-existing):** `power_user: true` on the user doc is client-writable and bypasses all limits (`numista_backend/tier_gatekeeper.py:238`, kept by `effective_limit`). Closed only by RX. PV-0 records how many users have it.
16. **CONFIRM (Eric):** Beta Special eligibility counts every coin the buyer owns, including coins locked after an earlier downgrade (§4.8 `count_unique_coins(..., include_locked=True)`). Limit checks count visible coins only.
17. PV-0's collection-group count of `locked_pending_upgrade == true` may need a Firestore index; creating one is a production change, so that single count is recorded BLOCKED instead. Nothing else depends on it.
18. `origin/main` `9f04550a` is not in the box clone; every file:line in this plan is from `a3d7dca2`. The builder re-checks each cited line on the branch before editing; a mismatch is reported, not guessed.
19. Design limit: a coin created directly by the app (client SDK, allowed by `firestore.rules:55-58`) above the limit stays visible until the next server touch (at the latest the app-start `refreshEntitlement`, §4.7), then is moved to the locked store. Rules cannot count, so a hard block would need a server-only create path, which is out of scope.
20. AI and search features (Vertex, Document AI, Gemini) in the preview point at the production project, where the preview service account has no roles, so they fail (permission denied). Out of NET-827 test scope.
21. PV-4 proves project-level and bucket-level IAM only; folder or organisation-level grants to the preview service account are not checked (none are expected; Eric confirms at PV-1).

## 11. Self-audit record (10 Nov 2026, America/New_York)

Method: every `path:line` citation in this file was extracted by script and the cited lines were printed from the checkout at `a3d7dca20fbbaf06a522205b22d0740b600de52b` and read against the claim (152 distinct citations; none out of range). Relative citations (`:13-15`, `:345-348`, etc.) were checked against the file named in the same sentence. Results:

- Firestore rules: `numista_mobile/firestore.rules` SHA-256 `e650713b9051904fa52efbe046b13986ad5896a435b89cea13a1ac53da2f9c86` (re-computed); `isOwner` `:13-15`; coin block `:40-67` (create `:55-58`, update `:63-66`); profile note `:69-73`; `_serverOnlyKeys` `:85-88`; user doc `:96-104`; wildcard exclusion lists `:110` and `:115`; "Deny everything else" comment `:345`, deny-all block `:346-348`. `numista_backend/firestore.rules` = `d087e8ae…` (different, not deployed; `numista_backend/firebase.json` is functions only). `numista_mobile/firebase.json:2-5` deploys rules and indexes; `.firebaserc` default = production.
- Routes: `routes/payment_routes.py:26` prefix `/api/stripe`; `:32` `/create-checkout-session`; `:82` `/create-customer-portal`; `:130` `/subscription-status`; `:166` `/webhook`; `:174-175` webhook secret and `K_SERVICE` production check.
- Clients: inventory rows 1-22 of §4.11 each re-read; 18 routers + 2 services import `db` from `routes.deps` (grep count; one more importer is under `_scripts/`, a standalone script not imported by `main.py`); storage clients use only `.bucket(...)` (18 call sites: 11 `gcs_client`, 6 `storage_client`, 1 `_gcs_client`), which `GuardedStorageClient` covers.
- Buckets: the five production names in §4.11 are literal strings in the cited lines; the appraisal default is at `main.py:12281` (corrected from an earlier draft's `:12282`). No invented bucket name appears; the preview bucket is a placeholder recorded at PV-1.
- Env vars: `FIREBASE_PROJECT_ID` (`main.py:335`), `GCS_BUCKET_NAME` (`routes/estate_routes.py:20`, `main.py:12281`), `STRIPE_SECRET_KEY` / `STRIPE_PUBLISHABLE_KEY` (`stripe_config.py:29-30`), `STRIPE_WEBHOOK_SECRET` (`routes/payment_routes.py:174`), `K_SERVICE` / `ENVIRONMENT` / `ALLOW_UNAUTHENTICATED` (`routes/deps.py:73-77`), `API_BASE_URL` (`numista_mobile/lib/constants.dart:13-16`) exist today. New names introduced by this plan (not in the repo yet, by design): `NUMISTA_ENV`, `FIRESTORE_PROJECT_ID`, `FIRESTORE_DATABASE_ID`, `FIREBASE_AUTH_PROJECT_ID`, `STRIPE_EXPECTED_MODE`, and `USER_CONTENT_BUCKET` as an env name (today it is only a Python constant at `main.py:342`).
- Fields: `locked_pending_upgrade` (`tier_gatekeeper.py:334`), `creation_timestamp` cutoff `1795669200000` (`tier_gatekeeper.py:146-149`), `power_user` (`tier_gatekeeper.py:238`), `stripe_customer_id` read at `routes/payment_routes.py:105`, `stripe_events` at `:199`, `created_at` order at `tier_gatekeeper.py:327`. A `git grep` of `numista_mobile/lib` for `creation_timestamp|power_user|stripe_customer_id|stripe_subscription_id|beta_special|locked_pending_upgrade` returns nothing. New collections `entitlements`, `locked_coins`, `stripe_customers`, `stripe_payments` are unused today.
- Tests: `numista_mobile/firestore.rules.test.js` (Jest, emulator `127.0.0.1:8080` at `:33-40`); `package.json` script `jest firestore.rules.test.js`; `.gitignore:35` `**/.venv/`; `numista_backend/.dockerignore:20` `serviceAccountKey*.json`; `numista_backend/Dockerfile:24` `CMD ["uvicorn", "main:app", ...]`; `google-cloud-firestore==2.26.0` in `requirements.txt:48`.
- Consistency checks done: tier limits identical in §0, §4.5, §7.1; Christmas epochs identical in §0, §4.1, §5, §9.3; checkout route `/api/stripe/create-checkout-session` everywhere (no `/api/payment`); locked path `locked_coins/{owner_key}/coins/{coin_id}` everywhere; Beta eligibility counts locked coins (§4.8, §7.1, §10 item 16) while limits count visible coins only; test file names identical in §3 and §7.1; section references in §2 point to existing sections.
- v1.8 mistakes absent (harvest "do not copy"): no Firestore list-query rule; no double counting (union by id); currency and wishlist never locked; no `numista-vault-user-content`; every client in the v1.8 R4 list is in §4.11; v1.7 lock/CSV tests (incl. unauthenticated CSV) restored in §7.1.
- Not verifiable here (stated, not guessed): `origin/main` `9f04550a` contents (not in the clone); production Stripe key mode (GL-1); live ruleset bytes (read at RX time, compared with `e650713b…`); preview names; whether PV-0's collection-group count needs an index; Stripe response shapes (first gated sandbox run).

## 12. Diff summary vs v1.9 (v1.9.1; only these changes)

1. **Header:** version label v1.9.1; attempt 5 of 10, Code Writing try 2 of 4; base v1.9 (CoS 96 PASS, SHA `0434dfce…`).
2. **D1 (§4.1, §4.3, §7.1):** checkout create ensures `users/{uid}` with `set({}, merge=True)` in the `checkout_pending` transaction, writing no fields. The grant no longer needs a pre-existing `users/{uid}` when the uid is proven by `checkout_pending` or Firebase Auth. New pytest cases cover email-only buyers (Silver, Beta, F&F), a deleted doc and an unknown uid. Checked offline against `google-cloud-firestore==2.26.0`, the pinned version (`requirements.txt:48`): `set({}, merge=True)` builds an `update` write with an empty field mask and no precondition. That creates the document if it is missing and changes no field if it exists.
3. **D2 (§9.4):** the backup is written to a temp file and kept only if its SHA matches; an existing backup is never overwritten. The deploy block re-reads the live ruleset and checks its SHA (and the backup's) immediately before `firebase deploy`. The post-deploy check is scripted, uses its own folder, and expects the RX SHA. Rollback falls back to the SHA-checked git blob at `a3d7dca2` and verifies the live rules afterwards. The worktree uses `core.autocrlf=false` so the YES SHA refers to the LF file.
4. **Lock order (§4.8, §7.1, §10 Q13):** sort time is `created_at`, then `added_at`, then epoch 0. The test uses a roll-wizard-shaped fixture. Q13 stays open for Eric.
5. **Admin lookups (§4.8, §7.1):** exact `/subscription-status` behaviour for an own lookup, a non-admin looking up someone else (403), and an admin looking up someone else (read-only, no reconcile, stated field set).
6. **Closure table:** new §2f with rows D1, D2, advisory 1 and advisory 5.
7. **This section.** Nothing else changed. The other v1.9 advisories (2-4, 6, 7) are not addressed here.

**Self-audit of the new citations (re-read at `a3d7dca2`; backend files also byte-identical in `src/tip`):**
- `src/tip/payment_routes.py` (= `numista_backend/routes/payment_routes.py`, SHA `e5c1571c…`) `:130-164`: `:141-143` admin bypass and 403; `:144-161` profile, tier, `get_coin_count(uid)` at `:147`, and the returned keys at `:151-161`; `:162-164` error → 500.
- `src/tip/tier_gatekeeper.py:327`: `order_by("created_at")`.
- `src/tip/main.py:2747`: `"created_at": firestore.SERVER_TIMESTAMP`.
- `numista_mobile/lib/widgets/roll_entry_dialog.dart:374-384`, with `'added_at': DateTime.now().toIso8601String()` at `:379` and no `created_at`.
- `numista_mobile/lib/screens/wishlist_screen.dart:979-984`, with `added_at` at `:983`; `Coin.toFirestore()` (`numista_mobile/lib/models/coin_model.dart:248`) writes neither `created_at` nor `added_at`.
- `numista_mobile/lib/screens/my_collection_screen.dart:359-362`: merge write of `default_sort_field` / `default_sort_asc` to `users/{uid}`.
- `numista_mobile/firestore.rules:69-73`: profile flags live on `users/{email}`.
- `numista_mobile/lib/screens/ai_chat_screen.dart:1653` also has an `added_at`, but it sits inside an `owner_photos` entry, not on the coin, so it is not used.
- The `numista_mobile` files are not among the `src/tip` copies; they are cited from the repo checkout.
<<<END ARTIFACT id=A1>>>

## A2 - GB CoS score record for v1.9.1 - 100/100 PASS (CoS only; NOT SAG)

<<<BEGIN ARTIFACT id=A2 sha256=d3db8668de8554a9ca680a3b3c0ce03788835b3167ef5d342db59c768ce6f3ee bytes=12141 lines=166 path=COS_SCORE_NET-827_FAILFIX-B1B5_v1.9.1_100_PASS_20261110.md>>>
# DESIGNATED CoS PLAN SCORE: NET-827 Stripe Checkout fail-fix B1–B5, plan v1.9.1 (writer: Code Writing)

**Score: 100 / 100, PASS.** The pass mark is 95. Only material defects count (correctness, safety, permissions, execution). Cosmetics are not deducted; external prerequisites are not plan defects.
Scored by GB CoS (designated CoS gate), 10 Nov 2026, about 8:05 PM ET (America/New_York).
**Count: NET-827 fail-fix track attempt 5 of 10; writer Code Writing try 2 of 4.** Both counts match the plan header (line 3).

## Plan scored
- `/workspace/net827-claude/src/PLAN_NET-827_FAILFIX-B1B5_STRIPE-CHECKOUT-PREVIEW_v1.9.1_CODE-WRITING_20261110.md`
- SHA-256 **`ec9c50b49c4d19d45a4a545b3171b98bb8aeb26761036070c9cadabbde0bfddb`**, 159,766 bytes, 1,627 lines. Both match the claim. Re-hashed at the end of scoring: unchanged.
- Base: v1.9, SHA `0434dfce…3dfed70`, which I scored 96 PASS (D1 −2, D2 −2).
- Code checked read-only at `a3d7dca20fbbaf06a522205b22d0740b600de52b`.
- `google-cloud-firestore==2.26.0` (the pinned version, `requirements.txt:48`) was checked from the official wheel.

## (a) Diff integrity
- `diff v1.9 v1.9.1` gives **+163 / −29** (1,493 − 29 + 163 = 1,627). It has 17 hunks, and every hunk is one of the items below:
  - header lines 1 and 3;
  - §2f, the new closure table;
  - §4.1 (D1);
  - §4.3 line 368 (D1);
  - §4.8 lines 454, 524–527 and 529 (lock order and the admin path);
  - §7.1 lines 1135, 1143 and 1148 (tests);
  - §9.4 (D2: backup, deploy, post-deploy verify, rollback, closing note);
  - §10 Q13;
  - §12, the new diff summary.
- The other 1,464 v1.9 lines are byte-identical and in the same order. The 29 replaced lines are only these scoped edits.
- §12 "Nothing else changed" is true.

## (b) D1 (grant needs `users/{uid}`): **closed, sound against the code**

**What v1.9.1 does**
- **At checkout create** (line 288): it writes `set({}, merge=True)` on `users/{uid}`, with the uid taken from the verified token. Any failure returns 503.
- **At grant** (line 368):
  - If the doc is missing, the uid is proven by `checkout_pending.session_id == session.id`, or else by `firebase_auth.get_user(uid)`.
  - Once proven, the merge writes in the grant transaction create the doc.
  - An unproven uid gets retry and a 500; it is never granted.
- **Tests** (line 1135):
  - email-only buyers for Silver, Beta and F&F;
  - an existing sort preference is kept;
  - a failed create-time write returns 503 with no Stripe `create` call;
  - a doc deleted before the webhook arrives;
  - the `get_user` fallback;
  - an unknown uid (no grant, retry).

**Verified**
- `set({}, merge=True)` in firestore 2.26.0 (`_helpers.py:867-892`, `DocumentExtractorForMerge._get_update_mask` at `:854-864`) builds one `update` write with an empty `DocumentMask` and no precondition. That creates a missing doc and changes no field on an existing one, as §12 claims.
- **Creating an empty `users/{uid}` changes no current behaviour:**
  - `get_user_profile` (`tier_gatekeeper.py:112-130`) returns `{}` whether the doc is missing or empty, with no email fallback to hide.
  - The app's readers of `users/{uid}` treat a missing doc and an empty doc the same: `my_collection_screen.dart:323-324` checks `exists && containsKey`, and `estate_planning_screen.dart:164-170` uses `snap.data() ?? {}`.
  - `load_entitlement_profile` merges an empty uid doc as a no-op.
  - No Cloud Function trigger exists on `users/{uid}`.
- No entitlement field is written. Rules are unaffected (Admin SDK).
- **Proving the uid is sound:** the uid comes from the server-set `client_reference_id`, so either proof only guards against deleted accounts. In the preview, `get_user` fails closed (no production IAM, §6.2), but the create-time write and the `checkout_pending` proof cover the normal path.

## (c) D2 (RX safety): **closed; PowerShell 5.1-correct**

**Backup (lines 1393–1427)**
- It computes the SHA in memory and throws before writing anything if the live rules are not `e650713b…`.
- It refuses to overwrite an existing backup unless that backup already matches.
- It writes to `firestore.rules.tmp`, re-hashes the file, and renames it only if the SHA matches. Otherwise it deletes the temp file and throws.
- `firebase.json` is still written for the rollback.

**Deploy (lines 1431–1477)**
- It checks the backup file's SHA against `e650713b…`, not just that the file exists.
- After the worktree and RX-file SHA checks, **immediately before `firebase deploy`**, it re-reads the live ruleset over REST, in memory only, and requires `e650713b…`.
- It never writes the backup folder.

**Post-deploy verify (lines 1481–1506)**
- Scripted, using its own `net827_rules_verify` folder (guarded against being the backup folder).
- Expects the RX SHA, and says to run the rollback if it doesn't match.

**Rollback 9.4-R (lines 1510–1563)**
- It uses the backup only if its SHA is `e650713b…`.
- Otherwise it extracts **`a3d7dca2:numista_mobile/firestore.rules`** byte-exactly. It uses `git cat-file blob` through `Diagnostics.Process`, copying stdout as a raw stream, which avoids PowerShell's pipeline encoding.
- It SHA-checks the extracted file against `e650713b…` (the blob at `a3d7dca2` is `e650713b…`, verified in the repo), writes `firebase.json` as ASCII, deploys, and then re-reads the live rules and verifies.

**PowerShell 5.1:** all of it works.
- `[Security.Cryptography.SHA256]::Create()` and `Dispose()` exist in .NET Framework 4.x.
- `WriteAllBytes` and `UTF8Encoding($false)` write no BOM.
- `Get-FileHash` exists in PowerShell 4 and later.
- Native calls are wrapped in `Invoke-Native` or have an explicit `$LASTEXITCODE` check.

## (d) Lock order: `created_at`, then `added_at`, then epoch 0. **Correct; citations verified**
- `main.py:2747`: `"created_at": firestore.SERVER_TIMESTAMP`.
- `tier_gatekeeper.py:327`: `order_by("created_at")`.
- `roll_entry_dialog.dart:374-384`: `'added_at': DateTime.now().toIso8601String()` at `:379`, with no `created_at`.
- `wishlist_screen.dart:979-984`: `added_at` at `:983`.
- `coin_model.dart:248`: `toFirestore()` writes neither field.
- `ai_chat_screen.dart:1653`: an `added_at` inside a photo entry, correctly excluded.
- The lock test (line 1143) and the reconcile fixture (line 1148: 10 `created_at` coins plus 1 roll-wizard coin; only the roll-wizard coin is locked) match the code. Q13 stays open for Eric.

## (e) Admin `/subscription-status` path: **matches `payment_routes.py:130-164`; no writes**
- **Verified in the code:**
  - `:141-143`: the admin claim bypasses the uid check, else 403 `Forbidden`.
  - `:144-147`: profile, tier and `get_coin_count(uid)`.
  - `:151-161`: the nine returned keys.
  - `:162-164`: any error returns 500.
  - Today's admin path does reads only.
- **v1.9.1:**
  - An own lookup reconciles the caller's own keys.
  - A non-admin looking up anyone else gets 403.
  - An admin looking up someone else gets a read-only report on the single queried key. `enforce_entitlement`, `lock_overflow_coins` and `unlock_user_coins` are never called, and the response adds `admin_view: true`, `reconciled: false` and `owner_keys`.
  - The test asserts the fake records zero writes, even for an over-limit user.
- The admin path can never move another user's coins.

## (f) `core.autocrlf=false` for the RX worktree: **accepted (harmless)**
- `git -c core.autocrlf=false worktree add` only makes the checkout byte-identical to the commit (LF), so the YES SHA is unambiguous. The repo has no `.gitattributes` that would override it.
- It doesn't affect Eric's main worktree, any config file, or the deployed bytes, beyond making them match the commit. It also closes v1.9 advisory 7.

## (g) No regressions; X1–X12 clean; Eric's decisions hold
- Everything outside the 17 hunks is byte-identical to v1.9 (96 PASS), so every v1.9 closure stands:
  - N1–N3, R1–R5 and v1.8 advisories 1–8;
  - no rules change in NET-827, with the deny-all at `firestore.rules:346` covering `locked_coins`, `entitlements`, `stripe_customers` and `stripe_payments`;
  - limits exactly as in v1.7, unlimited as null;
  - nobody signs in on p7-gate;
  - PowerShell 5.1 scripts;
  - holds, main and Stripe live unchanged.
- Re-grepping the plan for the do-not-copy items (`49e77cf7`, `numista-vault-user-content`, `subscription_tier`, `999999`, `firestore:rules:get`, `python -c`, `mocha`, `users/{uid}/locked_coins`) finds only the R3 history row (line 126) and the self-audit (line 1605).
- None of the new text touches prices, the Christmas window, Beta Special, refunds, buyers, preview isolation, the synthetic testers or the pytest rule.

## New citations spot-checked (all of them)
- `payment_routes.py:130-164` / `:141-143` / `:144-161` / `:147` / `:151-161` / `:162-164`
- `tier_gatekeeper.py:327` and `:112-130`
- `main.py:2747`
- `roll_entry_dialog.dart:374-384` / `:379`
- `wishlist_screen.dart:979-984` / `:983`
- `coin_model.dart:248`
- `ai_chat_screen.dart:1653`
- `my_collection_screen.dart:359-362`
- `firestore.rules:69-73`
- `requirements.txt:48`

All were accurate. Cosmetic only: the class is `CoinModel`, not "`Coin`".

## Deductions
**None.** Total: 100 − 0 = **100, PASS.**

## Advisories (not scored)
1. **When the account-doc write happens at checkout create.**
   - The conflict: line 288 puts the `users/{uid}` write "in the same transaction that writes `checkout_pending`". But `checkout_pending` holds the Stripe `session_id` (line 287), which only exists after the Stripe call. Meanwhile, line 288 and the test (line 1135) require "write fails → 503, Stripe `create` not called".
   - Suggested build: one transaction before the Stripe call that checks for an existing pending session, writes `users/{uid}` with merge, and reserves `checkout_pending` with no id yet. Then call Stripe. Then set `session_id`.
   - Either order is safe: no wrongful grant, and an unpaid session simply expires. So this is a note for the builder, not a defect.
2. **`added_at` has no timezone.** It is local time, from Dart's `toIso8601String()`, while `created_at` is a UTC Timestamp. On Cloud Run (UTC), a naive ISO time is read as UTC, so an app-added coin can sort up to about 5 hours (ET offset) earlier than it really is. This only matters for coins added within hours of each other, it falls under lock order (Q13), and nothing is lost. Optionally, write `created_at` on client creates later.
3. **Carried from v1.9, unchanged:**
   - Client-writable `power_user` and `creation_timestamp` (risks 14 and 15). Eric to decide whether RX becomes a go-live precondition.
   - `enforce_entitlement` read cost on big collections; use id-only reads.
   - The 10 MiB transaction limit for large coin docs; cap chunks by bytes.
   - PV-4 merges stderr into its JSON parse (fails closed).

## Writer assessment (Code Writing, try 2)
- **Good:**
  - A clean, tightly scoped revision: exactly the four requested items, with a diff summary that proves the scope.
  - Both deductions closed with code-verified mechanics, including checking the pinned Firestore library's merge semantics and using a binary-safe git blob rollback that works in PowerShell 5.1.
  - Every new citation is accurate.
- **Weak:** one ordering ambiguity in the create path (advisory 1).

## Next step
- **PASS at the CoS gate.** Next: one full-plan SAG review through the xAI API, on this exact SHA `ec9c50b4…`, authorized by Eric at 7:13 PM ET (t2553u) for SAG review only.
- Eric's open decisions are unchanged (not deductions):
  - Q13 lock order;
  - Q16 whether locked coins count toward the Beta 100-coin minimum;
  - Q3 legacy `estate` users;
  - whether RX becomes a go-live precondition.
- Nothing was filed to Desk and no agent was messaged.

## Authority statement
This score **grants no code, git, deploy, Firestore, Firestore rules, Firebase Auth, Storage, Stripe, Secret Manager or go-live authority**. HOLDs `74611e05…` and `41b8bd5f…` and the go-live addendum `c2b6ac93…` (NOT ACTIVE) stay in force. main stays `9f04550a` and Stripe live stays OFF. RX additionally needs its own scoped Eric YES naming HOLD `41b8bd5f`.
<<<END ARTIFACT id=A2>>>

## A3 - Real code excerpts, line-numbered, from git a3d7dca2 (packet-preparer extracted)

<<<BEGIN ARTIFACT id=A3 sha256=450fa2ccd7910aacf8f985a3159cf0dc8e033ae3820bc253e13adf3958623948 bytes=116163 lines=2766 path=CODE_EXCERPTS_NET-827_v1.9.1_a3d7dca2.md>>>
# REAL CODE EXCERPTS for NET-827 v1.9.1 review

Extracted read-only by the packet preparer from git checkout `a3d7dca20fbbaf06a522205b22d0740b600de52b` (clean worktree; GitHub Numista-AI/Numista.AI branch p7-v8.9 history). Format: `<line number>| <source line>`. Excerpts are verbatim except where marked REDACTED (Firebase client config values in firebase_options.dart). Nothing here is from origin/main 9f04550a (not in the clone).


## numista_mobile/firestore.rules — Deployed Firestore rules (full file; deployed by numista_mobile/firebase.json)


~~~~ numista_mobile/firestore.rules:1-350
1| rules_version = '2';
2| 
3| service cloud.firestore {
4|   match /databases/{database}/documents {
5| 
6|     // ── Helper functions ──────────────────────────────────────────────────────
7|     // Returns true if the request comes from a signed-in, non-anonymous user.
8|     function isAuthenticated() {
9|       return request.auth != null && !request.auth.token.firebase.sign_in_provider.matches('anonymous');
10|     }
11| 
12|     // Returns true if the signed-in user's email or UID matches the {email} path segment.
13|     function isOwner(email) {
14|       return request.auth != null && (request.auth.token.email == email || request.auth.uid == email);
15|     }
16| 
17|     // ── Estate reports — attorney portal token access ─────────────────────────
18|     // The report document ID IS the access token (a crypto-random UUID).
19|     // Any request that knows the exact reportId may GET that single document.
20|     // This enables the no-auth attorney portal while keeping data private
21|     // (the UUID is unguessable; the user controls the link).
22|     // IMPORTANT: This rule must come BEFORE the wildcard /users/{email}/{document=**}
23|     // rule so Firestore evaluates the more specific path first.
24|     match /users/{email}/estate_reports/{reportId} {
25|       allow read:  if isOwner(email);  // owner sees all their reports (list + get)
26|       allow write: if false;           // backend SA only
27|     }
28| 
29|     // ── ADDENDUM B: Field-level rules for protected demo/sandbox keys ─────────
30|     // These more-specific match blocks are evaluated BEFORE the wildcard
31|     // /users/{email}/{document=**} block below.
32|     //
33|     // Allowed on create: is_demo: false only (never is_demo: true).
34|     //   Client may explicitly stamp is_demo: false and is_demo_cleared: false on
35|     //   new real-coin creates (Option 1 of the ITEM 6 coding constraint).
36|     //   This keeps real coins visible once the WHERE is_demo == false filter ships.
37|     // Blocked on update: client may never change is_demo or is_demo_cleared on
38|     //   existing documents. Only Admin SDK / backend service account may do so.
39|     // Admin SDK bypasses all rules (standard Firestore behavior).
40|     match /users/{email}/coins/{coinId} {
41|       // Owner reads their own coins (list + get)
42|       allow read: if isOwner(email);
43| 
44|       // Owner deletes their own coins (soft-archive is done server-side;
45|       // hard delete is not used in this sprint, but not blocked at rules level)
46|       allow delete: if isOwner(email);
47| 
48|       // Owner creates a new coin:
49|       //   - is_demo MUST be present in the document AND explicitly false.
50|       //     get('is_demo', false) != true would allow omitting the field entirely;
51|       //     the display filter WHERE is_demo == false would then hide that coin.
52|       //   - is_demo_cleared MUST be present AND explicitly false.
53|       //   Admin SDK / Cloud Run creators bypass these rules and must write both
54|       //   fields in the payload (enforced by server-side payload unit tests).
55|       allow create: if isOwner(email)
56|                     && request.resource.data.keys().hasAll(['is_demo', 'is_demo_cleared'])
57|                     && request.resource.data.is_demo == false
58|                     && request.resource.data.is_demo_cleared == false;
59| 
60|       // Owner updates an existing coin:
61|       //   - may not change is_demo (any direction)
62|       //   - may not change is_demo_cleared (any direction)
63|       allow update: if isOwner(email)
64|                     && !request.resource.data.diff(resource.data)
65|                           .affectedKeys()
66|                           .hasAny(['is_demo', 'is_demo_cleared']);
67|     }
68| 
69|     // NOTE: match /users/{email}/profile was removed (13 Oct 2026).
70|     //   The app does not use a profile subcollection directly.
71|     //   sandbox_cleared, is_lifetime_family_estate, is_ai_qc_account, and
72|     //   beta_tester all live on the users/{email} doc itself and are guarded
73|     //   by _serverOnlyKeys() / _noEntitlementChange() below.
74| 
75|     // ── Settings (ui_variant, etc. — server-only writes via Admin SDK) ─────────
76|     match /users/{email}/settings/{doc} {
77|       allow read: if request.auth != null && request.auth.token.email == email;
78|       allow write: if false;  // server-only writes via Admin SDK
79|     }
80| 
81|     // Server-only entitlement fields — owner MUST NOT be able to set these.
82|     // The server (Admin SDK) sets them; any client write that touches them is denied.
83|     // On create: those fields must be absent (or default false/null).
84|     // On update: the diff must not include any of these keys.
85|     function _serverOnlyKeys() {
86|       return ['tier', 'stripe_tier', 'beta_tester', 'is_lifetime_family_estate',
87|               'is_ai_qc_account', 'is_bot_account', 'sandbox_cleared', 'admin'];
88|     }
89|     function _noEntitlementChange() {
90|       return !request.resource.data.diff(resource.data).affectedKeys().hasAny(_serverOnlyKeys());
91|     }
92|     function _noEntitlementOnCreate() {
93|       return !request.resource.data.keys().hasAny(_serverOnlyKeys());
94|     }
95| 
96|     match /users/{email} {
97|       allow read: if isOwner(email);
98|       // Owner may create their own user doc only if entitlement fields are absent.
99|       allow create: if isOwner(email) && _noEntitlementOnCreate();
100|       // Owner may update only if they don't touch any entitlement field.
101|       allow update: if isOwner(email) && _noEntitlementChange();
102|       // Deletes not allowed from client (would lose all data).
103|       allow delete: if false;
104|     }
105|     // Subcollections the owner CAN read+write (wishlist, review_queue, etc.)
106|     // coins and profile are excluded because they have more-specific blocks above.
107|     // server-only subcollections are excluded so writes are blocked.
108|     match /users/{email}/{sub}/{docId} {
109|       allow read, write: if isOwner(email)
110|         && !(sub in ['settings', 'estate_reports', 'morgan_action_log', 'trash', 'audit_log', 'coins', 'profile', 'morgan_proposals', 'subaccounts', 'subscription', 'transferred_coins', 'transferred_currency']);
111|     }
112|     // Nested docs within writable subcollections
113|     match /users/{email}/{sub}/{docId}/{rest=**} {
114|       allow read, write: if isOwner(email)
115|         && !(sub in ['settings', 'estate_reports', 'morgan_action_log', 'trash', 'audit_log', 'coins', 'profile', 'morgan_proposals', 'subaccounts', 'subscription', 'transferred_coins', 'transferred_currency']);
116|     }
117|     // Server-only subcollections — owner may read but NOT write (server SA only)
118|     match /users/{email}/settings/{docId} {
119|       allow read: if isOwner(email);
120|       allow write: if false;
121|     }
122|     match /users/{email}/estate_reports/{docId} {
123|       allow read: if isOwner(email);
124|       allow write: if false;
125|     }
126|     match /users/{email}/morgan_action_log/{docId} {
127|       allow read: if isOwner(email);
128|       allow write: if false;
129|     }
130|     match /users/{email}/trash/{docId} {
131|       allow read: if isOwner(email);
132|       allow write: if false;
133|     }
134|     match /users/{email}/audit_log/{docId} {
135|       allow read: if isOwner(email);
136|       allow write: if false;
137|     }
138|     match /users/{email}/morgan_proposals/{docId} {
139|       allow read: if isOwner(email);
140|       allow write: if false;
141|     }
142|     match /users/{email}/subaccounts/{docId} {
143|       allow read: if isOwner(email);
144|       allow write: if false;
145|     }
146|     match /users/{email}/subscription/{docId} {
147|       allow read: if isOwner(email);
148|       allow write: if false;
149|     }
150|     match /users/{email}/transferred_coins/{docId} {
151|       allow read: if isOwner(email);
152|       allow write: if false;
153|     }
154|     match /users/{email}/transferred_currency/{docId} {
155|       allow read: if isOwner(email);
156|       allow write: if false;
157|     }
158| 
159|     // ── Global programs (reference data — public read, no writes from client) ─
160|     match /global_programs/{programId} {
161|       allow read: if true;
162|       allow write: if false;  // backend service account only
163|     }
164| 
165|     // ── Coins reference (reference library — public read, no writes from client) ─
166|     match /coins_reference/{document=**} {
167|       allow get, list: if true;
168|       allow write: if false;  // backend service account only
169|     }
170| 
171| 
172|     // ── Config (PCGS token, NewsAPI key, eBay public config, etc.) ─────────────
173|     // Read access needed by the Flutter client to fetch non-sensitive platform config.
174|     // Client secrets (e.g. cert_id) are strictly prohibited and unreadable (REQ-023E M4).
175|     // Write access restricted to admin (backend service account bypasses rules).
176|     match /config/ebay {
177|       allow read: if isAuthenticated() && (resource == null || !('cert_id' in resource.data));
178|       allow write: if false;  // backend service account only
179|     }
180| 
181|     match /config/{document=**} {
182|       allow read: if isAuthenticated() && (resource == null || !('cert_id' in resource.data));
183|       allow write: if false;  // backend service account only
184|     }
185| 
186|     // ── Coin image index (reference library — authenticated read) ─────────────
187|     // Non-sensitive reference data built by build_image_index.py from GCS buckets.
188|     // Any signed-in user may read; only the backend service account may write.
189|     match /coin_image_index/{document=**} {
190|       allow read: if isAuthenticated();
191|       allow write: if false;  // backend service account only
192|     }
193| 
194|     // ── Coin set index (reference library — authenticated read) ───────────────
195|     // Pre-cataloged set manifests populated by the backend ingestion pipeline.
196|     // Any signed-in user may read; only the backend service account may write.
197|     match /coin_set_index/{document=**} {
198|       allow read: if isAuthenticated();
199|       allow write: if false;  // backend service account only
200|     }
201| 
202|     // ── Mint Error Library (reference data — authenticated read) ──────────────
203|     // Public-facing error encyclopedia populated by the backend ingestion pipeline.
204|     // Any signed-in user may read; client writes are forbidden (backend SA only).
205|     match /mint_errors/{errorId} {
206|       allow read:  if isAuthenticated();
207|       allow write: if false;  // backend service account only
208|     }
209| 
210|     // ── Backend-managed collections ───────────────────────────────────────────
211|     match /pending_items/{document=**} {
212|       allow read, write: if false; // backend service account only
213|     }
214| 
215|     match /supplies_log/{document=**} {
216|       allow read, write: if false; // backend service account only
217|     }
218| 
219|     match /admin_grade_flags/{document=**} {
220|       allow read, write: if false; // backend service account only
221|     }
222| 
223|     // ── Microscope / Hardware Agent Commands ──────────────────────────────────
224|     match /commands/{email}/pending/{commandId} {
225|       allow create: if isOwner(email);
226|       allow read, write: if false; // Only agent (SA) reads/deletes
227|     }
228| 
229|     match /commands/{email}/results/{resultId} {
230|       allow read: if isOwner(email);
231|       allow write: if false; // Only agent (SA) writes
232|     }
233| 
234|     // ── Beta Feedback ─────────────────────────────────────────────────────────
235|     // ALL writes (create, update, delete) go through the Cloud Run callable.
236|     // The callable uses the Firebase Admin SDK (bypasses these rules).
237|     // Admin reads are done via service account; tester reads blocked.
238|     // Clients may read their own submissions (status tracking).
239|     match /beta_feedback/{feedbackId} {
240|       // Tester: read own submission only (for post-submit correction check)
241|       allow get: if request.auth != null
242|                  && resource.data.user_id == request.auth.uid;
243|       // Admin or owner: list own submissions (via Admin SDK — bypasses rules; kept as belt-and-suspenders)
244|       allow list: if request.auth != null && (request.auth.token.admin == true || resource.data.user_id == request.auth.uid);
245|       // ALL writes: callable / Admin SDK only; client writes blocked
246|       allow create, update, delete: if false;
247|     }
248| 
249|     // ── Public Wishlists (family gift reservations) ───────────────────────────
250|     match /public_wishlists/{token} {
251|       allow get: if true;
252|       allow create: if request.auth != null;
253|       allow update: if request.resource.data.diff(resource.data).affectedKeys().hasAny(['reserved_items', 'reservation_details']);
254|     }
255| 
256|     // ── Estate Reports / Attorney Portal Tokens (Public Token Read, Hardened Owner Update) ────
257|     match /estate_reports/{token} {
258|       allow read: if request.auth != null && request.auth.token.email != null;
259|       allow write: if false; // server-only
260| 
261|       match /access_logs/{logId} {
262|         allow read, write: if false; // backend service account only
263|       }
264|     }
265| 
266|     // ── Attorney Portal Tokens (ITEM B — B5) ─────────────────────────────────
267|     // SHA-256 hashes of raw attorney tokens.
268|     // All reads and writes go through Cloud Run (POST /api/attorney/issue,
269|     // GET /api/attorney/snapshot, POST /api/attorney/revoke).
270|     // No client SDK may read or write this collection directly —
271|     // including the authenticated owner.
272|     // Admin SDK bypasses these rules (standard Firestore behavior).
273|     match /attorney_tokens/{tokenHash} {
274|       allow read, write: if false;  // Cloud Run + Admin SDK only
275|     }
276| 
277|     // ── Family Sub-Account Resource Groups (authenticated member access) ──────
278|     match /family_groups/{familyGroupId} {
279|       allow read: if request.auth != null;
280|       allow write: if request.auth != null && request.auth.uid == resource.data.primary_owner_uid;
281|     }
282| 
283|     // ── Help Tickets ──────────────────────────────────────────────────────────
284|     // Base document: no grant token, no diagnostic data — safe for admin queue read.
285|     // Sensitive sub-document (private/grant_and_diag): allow read, write: if false
286|     // → backend service account only (Admin SDK bypasses rules).
287|     match /tickets/{ticket_id} {
288|       // User creates their own ticket; grant_active must be false on create
289|       allow create: if isAuthenticated()
290|                     && request.resource.data.user_id == request.auth.uid
291|                     && request.resource.data.get('grant_active', false) == false;
292| 
293|       // User reads own tickets; admin reads all (base doc only — no sensitive fields here)
294|       allow read: if isAuthenticated()
295|                   && (resource.data.user_id == request.auth.uid
296|                       || request.auth.token.admin == true);
297| 
298|       // User may update subject/description/status only while no grant is active
299|       allow update: if isAuthenticated()
300|                     && resource.data.user_id == request.auth.uid
301|                     && resource.data.get('grant_active', false) == false;
302| 
303|       allow delete: if false;
304| 
305|       // ── Sensitive private sub-document ─────────────────────────────────────
306|       // Contains support_grant (token_hash) and diagnostic_package.
307|       // ONLY the backend service account (Admin SDK) may read or write this.
308|       match /private/{doc} {
309|         allow read, write: if false;
310|       }
311| 
312|       // ── Messages ────────────────────────────────────────────────────────────
313|       // User posts and reads their own ticket messages.
314|       // Support posts and reads via backend Admin SDK only (not direct Firestore).
315|       match /messages/{message_id} {
316|         allow create: if isAuthenticated()
317|                       && get(/databases/$(database)/documents/tickets/$(ticket_id))
318|                            .data.user_id == request.auth.uid;
319|         allow read:   if isAuthenticated()
320|                       && get(/databases/$(database)/documents/tickets/$(ticket_id))
321|                            .data.user_id == request.auth.uid;
322|         allow update, delete: if false;
323|       }
324|     }
325| 
326|     // ── Support Access Audit Log ──────────────────────────────────────────────
327|     // Backend service account writes. Admin may read for audit review.
328|     // Clients cannot write audit log entries.
329|     match /support_access_logs/{log_id} {
330|       allow read:  if request.auth != null && request.auth.token.admin == true;
331|       allow write: if false;  // backend service account only via Admin SDK
332|     }
333| 
334|     // NET-748: read-only SKU dictionary lookups for Add by SKU.
335|     // Named docs only. {skuId} is a single-segment variable, NOT recursive.
336|     match /global_metadata/usmint_sku_dictionary/skus/{skuId} {
337|       allow get: if isAuthenticated();
338|       allow list, write: if false;
339|     }
340|     match /global_metadata/littleton_sku_dictionary/skus/{skuId} {
341|       allow get: if isAuthenticated();
342|       allow list, write: if false;
343|     }
344| 
345|     // ── Deny everything else ──────────────────────────────────────────────────
346|     match /{document=**} {
347|       allow read, write: if false;
348|     }
349|   }
350| }
~~~~

## numista_mobile/firebase.json — Mobile firebase.json (full)


~~~~ numista_mobile/firebase.json:1-311
1| {
2|   "firestore": {
3|     "rules": "firestore.rules",
4|     "indexes": "firestore.indexes.json"
5|   },
6|   "hosting": {
7|     "site": "numista-vault",
8|     "public": "build/web",
9|     "trailingSlash": false,
10|     "ignore": [
11|       "firebase.json",
12|       "**/.*",
13|       "**/node_modules/**"
14|     ],
15| 
16|     "redirects": [
17|       {
18|         "source": "https://www.numista.ai/**",
19|         "destination": "https://numista.ai/:splat",
20|         "type": 301
21|       },
22|       {
23|         "source": "/app",
24|         "destination": "/",
25|         "type": 301
26|       },
27|       {
28|         "source": "/blog",
29|         "destination": "/about",
30|         "type": 301
31|       },
32|       {
33|         "source": "/signin",
34|         "destination": "/login",
35|         "type": 301
36|       },
37|       {
38|         "source": "/forgot",
39|         "destination": "/reset-password",
40|         "type": 301
41|       },
42|       {
43|         "source": "/reset",
44|         "destination": "/reset-password",
45|         "type": 301
46|       }
47|     ],
48| 
49|     "rewrites": [
50|       {
51|         "source": "/api/**",
52|         "run": {
53|           "serviceId": "numista-backend",
54|           "region": "us-central1"
55|         }
56|       },
57|       {
58|         "source": "/add_coins.html",
59|         "destination": "/add_coins.html"
60|       },
61|       {
62|         "source": "/scraper_dashboard.html",
63|         "destination": "/scraper_dashboard.html"
64|       },
65|       {
66|         "source": "/privacy",
67|         "destination": "/privacy.html"
68|       },
69|       {
70|         "source": "/terms",
71|         "destination": "/terms.html"
72|       },
73|       {
74|         "source": "/catalog",
75|         "destination": "/index.html"
76|       },
77|       {
78|         "source": "/catalog/**",
79|         "destination": "/index.html"
80|       },
81|       {
82|         "source": "/about",
83|         "destination": "/index.html"
84|       },
85|       {
86|         "source": "/pricing",
87|         "destination": "/index.html"
88|       },
89|       {
90|         "source": "/features",
91|         "destination": "/index.html"
92|       },
93|       {
94|         "source": "/faq",
95|         "destination": "/index.html"
96|       },
97|       {
98|         "source": "/login",
99|         "destination": "/index.html"
100|       },
101|       {
102|         "source": "/reset-password",
103|         "destination": "/index.html"
104|       },
105|       {
106|         "source": "/signup",
107|         "destination": "/index.html"
108|       },
109|       {
110|         "source": "/demo",
111|         "destination": "/index.html"
112|       },
113|       {
114|         "source": "/",
115|         "destination": "/index.html"
116|       },
117|       {
118|         "source": "/index.html",
119|         "destination": "/index.html"
120|       },
121|       {
122|         "source": "/wishlist",
123|         "destination": "/index.html"
124|       },
125|       {
126|         "source": "/wishlist/**",
127|         "destination": "/index.html"
128|       },
129|       {
130|         "source": "/attorney_portal",
131|         "destination": "/index.html"
132|       },
133|       {
134|         "source": "/claim",
135|         "destination": "/index.html"
136|       },
137|       {
138|         "source": "/claim/**",
139|         "destination": "/index.html"
140|       }
141|     ],
142| 
143|     "headers": [
144|       {
145|         "source": "**/*.@(js|css|wasm)",
146|         "headers": [
147|           {
148|             "key": "Cache-Control",
149|             "value": "public, max-age=31536000, immutable"
150|           }
151|         ]
152|       },
153|       {
154|         "source": "/index.html",
155|         "headers": [
156|           {
157|             "key": "Cache-Control",
158|             "value": "no-cache, no-store, must-revalidate"
159|           }
160|         ]
161|       },
162|       {
163|         "source": "/",
164|         "headers": [
165|           {
166|             "key": "Cache-Control",
167|             "value": "no-cache, no-store, must-revalidate"
168|           }
169|         ]
170|       },
171|       {
172|         "source": "/flutter_service_worker.js",
173|         "headers": [
174|           {
175|             "key": "Cache-Control",
176|             "value": "no-cache, no-store, must-revalidate"
177|           }
178|         ]
179|       },
180|       {
181|         "source": "/flutter_bootstrap.js",
182|         "headers": [
183|           {
184|             "key": "Cache-Control",
185|             "value": "no-cache, no-store, must-revalidate"
186|           }
187|         ]
188|       },
189|       {
190|         "source": "/version.json",
191|         "headers": [
192|           {
193|             "key": "Cache-Control",
194|             "value": "no-cache, no-store, must-revalidate"
195|           }
196|         ]
197|       },
198|       {
199|         "source": "/main.dart.js",
200|         "headers": [
201|           {
202|             "key": "Cache-Control",
203|             "value": "no-cache, no-store, must-revalidate"
204|           }
205|         ]
206|       },
207|       {
208|         "source": "**/*.@(png|jpg|jpeg|gif|svg|ico|webp)",
209|         "headers": [
210|           {
211|             "key": "Cache-Control",
212|             "value": "public, max-age=86400"
213|           }
214|         ]
215|       },
216|       {
217|         "source": "/manifest.json",
218|         "headers": [
219|           {
220|             "key": "Cache-Control",
221|             "value": "public, max-age=3600"
222|           },
223|           {
224|             "key": "Content-Type",
225|             "value": "application/manifest+json"
226|           }
227|         ]
228|       },
229|       {
230|         "source": "/robots.txt",
231|         "headers": [
232|           {
233|             "key": "Cache-Control",
234|             "value": "public, max-age=86400"
235|           },
236|           {
237|             "key": "Content-Type",
238|             "value": "text/plain; charset=utf-8"
239|           }
240|         ]
241|       },
242|       {
243|         "source": "/sitemap.xml",
244|         "headers": [
245|           {
246|             "key": "Cache-Control",
247|             "value": "public, max-age=86400"
248|           },
249|           {
250|             "key": "Content-Type",
251|             "value": "application/xml; charset=utf-8"
252|           }
253|         ]
254|       },
255|       {
256|         "source": "**",
257|         "headers": [
258|           {
259|             "key": "X-Frame-Options",
260|             "value": "SAMEORIGIN"
261|           },
262|           {
263|             "key": "X-Content-Type-Options",
264|             "value": "nosniff"
265|           },
266|           {
267|             "key": "Referrer-Policy",
268|             "value": "strict-origin-when-cross-origin"
269|           },
270|           {
271|             "key": "Permissions-Policy",
272|             "value": "camera=(self), microphone=(), geolocation=(), payment=()"
273|           },
274|           {
275|             "key": "Strict-Transport-Security",
276|             "value": "max-age=63072000; includeSubDomains; preload"
277|           },
278|           {
279|             "key": "X-DNS-Prefetch-Control",
280|             "value": "on"
281|           },
282|           {
283|             "key": "Content-Security-Policy",
284|             "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
285|           }
286|         ]
287|       }
288|     ]
289|   },
290|   "flutter": {
291|     "platforms": {
292|       "android": {
293|         "default": {
294|           "projectId": "studio-9101802118-8c9a8",
295|           "appId": "1:568985927038:android:efb96a51420403078b072f",
296|           "fileOutput": "android/app/google-services.json"
297|         }
298|       },
299|       "dart": {
300|         "lib/firebase_options.dart": {
301|           "projectId": "studio-9101802118-8c9a8",
302|           "configurations": {
303|             "android": "1:568985927038:android:efb96a51420403078b072f",
304|             "web": "1:568985927038:web:9ea56548eed27d5a8b072f",
305|             "windows": "1:568985927038:web:14e303f30991f9e78b072f"
306|           }
307|         }
308|       }
309|     }
310|   }
311| }
~~~~

## numista_mobile/.firebaserc — .firebaserc (full)


~~~~ numista_mobile/.firebaserc:1-5
1| {
2|   "projects": {
3|     "default": "studio-9101802118-8c9a8"
4|   }
5| }
~~~~

## numista_backend/firebase.json — Backend firebase.json (full; functions only)


~~~~ numista_backend/firebase.json:1-7
1| {
2|   "functions": {
3|     "source": "functions",
4|     "runtime": "nodejs20"
5|   }
6| }
7| 
~~~~

## numista_backend/firestore.rules — Backend rules file (not deployed): deny-all


~~~~ numista_backend/firestore.rules:236-248
236|     // ── Beta Feedback (testers can create documents; admin reads via SA) ──────
237|     match /beta_feedback/{feedbackId} {
238|       allow create: if request.auth != null
239|                    || (request.resource.data.keys().hasAll(['ratings', 'comment', 'created_at']));
240|       allow read, update, delete: if false;
241|     }
242| 
243|     // ── Deny everything else ──────────────────────────────────────────────────
244|     match /{document=**} {
245|       allow read, write: if false;
246|     }
247|   }
248| }
~~~~

## numista_backend/routes/payment_routes.py — Stripe routes today (full file)


~~~~ numista_backend/routes/payment_routes.py:1-241
1| """
2| Stripe Billing, Checkout Sessions, Customer Portal, and Webhook Routes
3| """
4| 
5| import os
6| import json
7| import uuid
8| import time
9| from datetime import datetime, timezone, timedelta
10| from typing import Optional, Dict, Any
11| from fastapi import APIRouter, HTTPException, Request, Depends
12| import stripe
13| from stripe_config import load_stripe_keys
14| from schemas.payment_schemas import StripeCheckoutRequest
15| from routes.deps import db, logger, get_current_user
16| from tier_gatekeeper import (
17|     get_user_profile,
18|     get_user_tier,
19|     get_coin_count,
20|     TIER_COIN_LIMITS,
21|     TIER_DAILY_ALLOWANCES,
22|     unlock_user_coins,
23|     lock_overflow_coins,
24| )
25| 
26| router = APIRouter(prefix="/api/stripe", tags=["Stripe Payments & Subscriptions"])
27| 
28| stripe_keys = load_stripe_keys()
29| if stripe_keys.get("secret_key"):
30|     stripe.api_key = stripe_keys["secret_key"]
31| 
32| @router.post("/create-checkout-session")
33| async def api_stripe_checkout(
34|     req: StripeCheckoutRequest,
35|     _user: Dict[str, Any] = Depends(get_current_user),
36| ):
37|     """
38|     Creates a Stripe Checkout Session for Pro, Numismatist, Dealer, Estate, or Family Estate subscriptions.
39|     Accepts client_reference_id = user_uid and supports promotion/coupon codes.
40|     Requires a valid Firebase ID token. Stripe failures return HTTP 502 — never a mock URL.
41|     """
42|     if not stripe.api_key:
43|         logger.error("Stripe checkout rejected: secret key is not configured")
44|         raise HTTPException(status_code=502, detail="Stripe is not configured")
45| 
46|     try:
47|         user_uid = _user.get("uid") or _user.get("user_id") or ""
48|         user_email = (_user.get("email") or "").strip().lower()
49|         tier = req.tier.lower()
50|         unit_amount = 2900 if tier in ["estate", "family_estate"] else 499
51|         interval = "year" if tier in ["estate", "family_estate"] else "month"
52|         
53|         session = stripe.checkout.Session.create(
54|             payment_method_types=['card'],
55|             mode='subscription',
56|             customer_email=user_email,
57|             client_reference_id=user_uid,
58|             allow_promotion_codes=True,
59|             line_items=[{
60|                 'price_data': {
61|                     'currency': 'usd',
62|                     'product_data': {
63|                         'name': f"Numista.AI {req.tier.capitalize()} Tier Subscription",
64|                         'description': "AI Grading, Unlimited Checklists & Legal Estate Suite"
65|                     },
66|                     'unit_amount': unit_amount,
67|                     'recurring': {'interval': interval}
68|                 },
69|                 'quantity': 1,
70|             }],
71|             success_url="https://numista.ai/#/settings?stripe=success",
72|             cancel_url="https://numista.ai/#/settings?stripe=cancel",
73|             metadata={"user_uid": user_uid, "target_tier": tier}
74|         )
75|         return {"checkout_url": session.url, "session_id": session.id}
76|     except HTTPException:
77|         raise
78|     except Exception:
79|         logger.exception("Stripe checkout session creation failed")
80|         raise HTTPException(status_code=502, detail="Unable to create Stripe checkout session")
81| 
82| @router.post("/create-customer-portal")
83| async def api_stripe_customer_portal(
84|     current_user: Dict[str, Any] = Depends(get_current_user),
85| ):
86|     """
87|     Generates a self-serve Stripe Customer Portal session link for plan management.
88|     Requires a valid Firebase ID token. User identity comes from the token only —
89|     query/body user_email is intentionally NOT accepted (prevents IDOR).
90|     Stripe failures return HTTP 502 — never a mock URL.
91|     """
92|     if not stripe.api_key:
93|         logger.error("Stripe customer portal rejected: secret key is not configured")
94|         raise HTTPException(status_code=502, detail="Stripe is not configured")
95| 
96|     user_email = (current_user.get("email") or "").strip().lower()
97|     uid        = current_user.get("uid") or current_user.get("user_id") or user_email
98| 
99|     try:
100|         target_id = uid or user_email
101|         stripe_customer_id = None
102|         user_doc_ref = db.collection("users").document(target_id)
103|         user_doc = user_doc_ref.get()
104|         if user_doc.exists:
105|             stripe_customer_id = (user_doc.to_dict() or {}).get("stripe_customer_id")
106| 
107|         if not stripe_customer_id:
108|             existing = stripe.Customer.list(email=user_email, limit=1)
109|             if existing.data:
110|                 stripe_customer_id = existing.data[0].id
111|             else:
112|                 new_cust = stripe.Customer.create(email=user_email, metadata={"uid": target_id})
113|                 stripe_customer_id = new_cust.id
114|             user_doc_ref.set({"stripe_customer_id": stripe_customer_id}, merge=True)
115| 
116|         if not stripe_customer_id:
117|             raise HTTPException(status_code=502, detail="Unable to resolve Stripe customer")
118| 
119|         portal_session = stripe.billing_portal.Session.create(
120|             customer=stripe_customer_id,
121|             return_url="https://numista.ai/#/settings"
122|         )
123|         return {"portal_url": portal_session.url}
124|     except HTTPException:
125|         raise
126|     except Exception:
127|         logger.exception("Failed to generate Stripe Customer Portal session")
128|         raise HTTPException(status_code=502, detail="Unable to create Stripe customer portal session")
129| 
130| @router.get("/subscription-status")
131| async def api_subscription_status(
132|     uid: str,
133|     _user: Dict[str, Any] = Depends(get_current_user),
134| ):
135|     """
136|     Queries current subscription tier, coin usage, daily AI tokens, and grace period status.
137|     """
138|     caller_uid = _user.get("uid") or _user.get("user_id") or ""
139|     caller_email = (_user.get("email") or "").strip().lower()
140|     is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"
141|     if not _user.get("admin") and not is_dev_guest:
142|         if uid.strip() != caller_uid and uid.strip().lower() != caller_email:
143|             raise HTTPException(status_code=403, detail="Forbidden")
144|     try:
145|         profile = get_user_profile(uid)
146|         tier = get_user_tier(profile)
147|         coin_count = get_coin_count(uid)
148|         coin_limit = TIER_COIN_LIMITS.get(tier, TIER_COIN_LIMITS["free"])
149|         ai_allowance = TIER_DAILY_ALLOWANCES.get(tier, TIER_DAILY_ALLOWANCES["free"])
150| 
151|         return {
152|             "uid": uid,
153|             "stripe_tier": tier,
154|             "subscription_status": profile.get("subscription_status", "active"),
155|             "grace_period_until": profile.get("grace_period_until"),
156|             "coin_count": coin_count,
157|             "coin_limit": coin_limit,
158|             "daily_ai_allowance": ai_allowance,
159|             "deepdive_count": profile.get("deepdive_count", 0),
160|             "invoice_scan_count": profile.get("invoice_scan_count", 0),
161|         }
162|     except Exception as e:
163|         logger.exception("Error getting subscription status")
164|         raise HTTPException(status_code=500, detail=str(e))
165| 
166| @router.post("/webhook")
167| async def api_stripe_webhook(request: Request):
168|     """
169|     Handles Stripe webhooks with signature verification, Firestore idempotency,
170|     and 3-day grace period for invoice.payment_failed before downgrade.
171|     """
172|     payload = await request.body()
173|     sig_header = request.headers.get("stripe-signature")
174|     webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
175|     is_prod = os.environ.get("K_SERVICE") or os.environ.get("ENVIRONMENT") == "production"
176|     
177|     event = None
178|     if webhook_secret:
179|         if not sig_header:
180|             raise HTTPException(status_code=400, detail="Missing signature header")
181|         try:
182|             event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
183|         except Exception as e:
184|             logger.error(f"Stripe webhook signature verification failed: {e}")
185|             raise HTTPException(status_code=400, detail="Invalid signature")
186|     else:
187|         if is_prod:
188|             logger.error("[CRITICAL] Stripe webhook rejected: STRIPE_WEBHOOK_SECRET is not configured in production!")
189|             raise HTTPException(status_code=400, detail="Stripe webhook secret is missing")
190|         logger.warning("[DEV MODE] STRIPE_WEBHOOK_SECRET not set; parsing unverified JSON payload.")
191|         try:
192|             event = json.loads(payload.decode('utf-8'))
193|         except Exception:
194|             raise HTTPException(status_code=400, detail="Invalid JSON payload")
195| 
196|     event_id = event.get("id", str(uuid.uuid4()))
197|     
198|     # 1. Idempotency Check in Firestore
199|     event_ref = db.collection("stripe_events").document(event_id)
200|     if event_ref.get().exists:
201|         logger.info(f"[Stripe Webhook] Duplicate event {event_id} skipped.")
202|         return {"status": "skipped_duplicate", "event_id": event_id}
203| 
204|     event_type = event.get("type", "")
205|     data_obj = event.get("data", {}).get("object", {})
206|     user_uid = data_obj.get("client_reference_id") or data_obj.get("metadata", {}).get("user_uid")
207|     customer_email = data_obj.get("customer_email") or data_obj.get("email")
208|     stripe_customer_id = data_obj.get("customer")
209| 
210|     target_id = user_uid or customer_email
211| 
212|     if target_id:
213|         user_doc_ref = db.collection("users").document(target_id)
214|         update_payload = {
215|             "updated_at": datetime.now(timezone.utc).isoformat()
216|         }
217|         if stripe_customer_id:
218|             update_payload["stripe_customer_id"] = stripe_customer_id
219| 
220|         if event_type in ["checkout.session.completed", "customer.subscription.updated", "invoice.paid"]:
221|             tier_val = data_obj.get("metadata", {}).get("target_tier", "pro")
222|             update_payload["stripe_tier"] = tier_val
223|             update_payload["subscription_status"] = "active"
224|             update_payload["grace_period_until"] = None
225|             user_doc_ref.set(update_payload, merge=True)
226|             unlock_user_coins(target_id)
227|         elif event_type == "invoice.payment_failed":
228|             # 3-day grace period
229|             grace_until = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
230|             update_payload["subscription_status"] = "past_due"
231|             update_payload["grace_period_until"] = grace_until
232|             user_doc_ref.set(update_payload, merge=True)
233|         elif event_type == "customer.subscription.deleted":
234|             update_payload["stripe_tier"] = "free"
235|             update_payload["subscription_status"] = "canceled"
236|             update_payload["grace_period_until"] = None
237|             user_doc_ref.set(update_payload, merge=True)
238|             lock_overflow_coins(target_id, TIER_COIN_LIMITS["free"])
239| 
240|     event_ref.set({"processed_at": datetime.now(timezone.utc).isoformat(), "type": event_type})
241|     return {"status": "success", "event_type": event_type}
~~~~

## numista_backend/schemas/payment_schemas.py — Checkout request model today (full)


~~~~ numista_backend/schemas/payment_schemas.py:1-10
1| """
2| Stripe and Payment DTO Schemas
3| """
4| 
5| from pydantic import BaseModel, Field
6| from typing import Optional
7| 
8| class StripeCheckoutRequest(BaseModel):
9|     user_email: Optional[str] = None
10|     tier: str  # 'pro' or 'estate'
~~~~

## numista_backend/tier_gatekeeper.py — Tier gatekeeper today (full file)


~~~~ numista_backend/tier_gatekeeper.py:1-351
1| import os
2| import stripe
3| import firebase_admin
4| from firebase_admin import credentials, firestore
5| from datetime import datetime, timezone
6| from fastapi import HTTPException, status
7| from stripe_config import load_stripe_keys
8| 
9| # ==============================================================================
10| # 🛠️ FIREBASE ADMIN SDK INITIALIZATION
11| # ==============================================================================
12| 
13| PROJECT_ID = "studio-9101802118-8c9a8"
14| 
15| if not firebase_admin._apps:
16|     sa_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
17|     if not os.path.exists(sa_path):
18|         sa_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json.json")
19|     if os.path.exists(sa_path):
20|         cred = credentials.Certificate(sa_path)
21|         firebase_admin.initialize_app(cred, {
22|             'projectId': PROJECT_ID
23|         })
24|     else:
25|         firebase_admin.initialize_app(options={
26|             'projectId': PROJECT_ID
27|         })
28| 
29| db = firestore.client()
30| 
31| try:
32|     stripe_keys = load_stripe_keys()
33|     stripe.api_key = stripe_keys.get("secret_key")
34| except Exception as e:
35|     print(f"[Tier Gatekeeper] Warning: Could not initialize Stripe keys: {e}")
36| 
37| # ==============================================================================
38| # 📊 USER TIERS CONFIGURATION (6-Tier Spectrum)
39| # ==============================================================================
40| 
41| TIER_COIN_LIMITS = {
42|     "free": 20,
43|     "pro": 100,
44|     "numismatist": 250,
45|     "dealer": 500,
46|     "estate": 1000,
47|     "family_estate": 2500,
48|     "sovereign": float("inf"),
49|     "power_user": float("inf"),
50| }
51| 
52| TIER_DAILY_ALLOWANCES = {
53|     "free": {"deepdive": 3, "invoice_scan": 1},
54|     "pro": {"deepdive": 25, "invoice_scan": 15},
55|     "numismatist": {"deepdive": 50, "invoice_scan": 30},
56|     "dealer": {"deepdive": 100, "invoice_scan": 50},
57|     "estate": {"deepdive": 500, "invoice_scan": 250},
58|     "family_estate": {"deepdive": 1500, "invoice_scan": 750},
59|     "sovereign": {"deepdive": 5000, "invoice_scan": 2500},
60|     "power_user": {"deepdive": float("inf"), "invoice_scan": float("inf")}
61| }
62| 
63| # ==============================================================================
64| # 🔄 LEGACY MIGRATION & USER PROFILE LOGIC
65| # ==============================================================================
66| 
67| def migrate_legacy_collection_chunked(legacy_email: str, new_uid: str):
68|     """
69|     Migrates legacy subcollections from users/{legacy_email} to users/{new_uid}
70|     using safe 400-item batch chunks to prevent exceeding Firestore's 500-op limit.
71|     Sets 'migration_status: completed' on users/{new_uid} to run exactly once.
72|     """
73|     try:
74|         user_uid_ref = db.collection("users").document(new_uid)
75|         uid_doc = user_uid_ref.get()
76|         if uid_doc.exists and (uid_doc.to_dict() or {}).get("migration_status") == "completed":
77|             return
78| 
79|         subcollections = ["coins", "currency", "wishlist", "staging_area"]
80|         total_migrated = 0
81| 
82|         for subcoll in subcollections:
83|             docs = db.collection("users").document(legacy_email).collection(subcoll).stream()
84|             batch = db.batch()
85|             op_count = 0
86| 
87|             for doc in docs:
88|                 target_ref = user_uid_ref.collection(subcoll).document(doc.id)
89|                 batch.set(target_ref, doc.to_dict(), merge=True)
90|                 op_count += 1
91|                 total_migrated += 1
92| 
93|                 if op_count >= 400:
94|                     batch.commit()
95|                     batch = db.batch()
96|                     op_count = 0
97| 
98|             if op_count > 0:
99|                 batch.commit()
100| 
101|         user_uid_ref.set({
102|             "legacy_email": legacy_email,
103|             "migration_status": "completed",
104|             "migrated_at": datetime.now(timezone.utc).isoformat(),
105|             "migrated_doc_count": total_migrated
106|         }, merge=True)
107|         print(f"[Tier Gatekeeper] Successfully migrated {total_migrated} docs from {legacy_email} -> {new_uid}")
108|     except Exception as e:
109|         print(f"[Tier Gatekeeper] Error during legacy migration for {legacy_email}: {e}")
110| 
111| 
112| def get_user_profile(user_identifier: str) -> dict:
113|     """
114|     Reads the user document from Firestore.
115|     Checks users/{uid} first. If missing or email-like, checks users/{email} fallback.
116|     """
117|     try:
118|         doc_ref = db.collection("users").document(user_identifier)
119|         doc = doc_ref.get()
120|         if doc.exists:
121|             return doc.to_dict() or {}
122| 
123|         if "@" in user_identifier:
124|             return {}
125| 
126|         return {}
127|     except Exception as e:
128|         print(f"[Tier Gatekeeper] Error reading profile for {user_identifier}: {e}")
129|         return {}
130| 
131| 
132| def get_user_tier(user_profile: dict) -> str:
133|     """Resolves subscription tier (stripe_tier -> tier -> beta/lifetime flags -> 'free').
134| 
135|     Beta access NEVER expires on the server — the cutoff (accounts created before
136|     2026-11-26T05:00Z) is enforced on the client by account creationTime.
137|     The server treats beta_tester=True as permanent family_estate regardless of any
138|     beta_access_expires field written by the Aug 2026 backfill script.
139|     """
140|     if user_profile.get("is_lifetime_family_estate") or user_profile.get("is_ai_qc_account"):
141|         return "family_estate"
142|     if user_profile.get("beta_tester"):
143|         return "family_estate"  # permanent — do NOT check beta_access_expires
144| 
145|     # Also grant beta tier if account was created before the Facebook ad launch (1795669200000 ms epoch)
146|     creation_ts = user_profile.get('creation_timestamp')
147|     if creation_ts is not None:
148|         try:
149|             if int(creation_ts) < 1795669200000:
150|                 return 'family_estate'
151|         except (ValueError, TypeError):
152|             pass
153| 
154|     tier = user_profile.get("stripe_tier") or user_profile.get("tier")
155|     if tier:
156|         return str(tier).lower().strip()
157|     return "free"
158| 
159| 
160| def get_coin_count(user_identifier: str) -> int:
161|     """Calculates total coins in users/{user_identifier}/coins via count()."""
162|     try:
163|         coins_ref = db.collection("users").document(user_identifier).collection("coins")
164|         results = coins_ref.count().get()
165|         return results[0][0].value
166|     except Exception as e:
167|         print(f"[Tier Gatekeeper] Error counting coins for {user_identifier}: {e}")
168|         return 0
169| 
170| # ==============================================================================
171| # 💳 STRIPE CHECKOUT & PORTAL SESSIONS
172| # ==============================================================================
173| 
174| def create_upgrade_checkout_session(user_id: str, email: str, target_tier: str, success_url: str, cancel_url: str) -> str:
175|     sec_key = os.getenv("STRIPE_SECRET_KEY")
176|     if not sec_key:
177|         raise ValueError("STRIPE_SECRET_KEY is not set in environment.")
178|     stripe.api_key = sec_key
179| 
180|     price_map = {
181|         "pro": os.getenv("STRIPE_PRICE_PRO", "price_1ProMockID"),
182|         "numismatist": os.getenv("STRIPE_PRICE_NUMISMATIST", "price_1NumismatistMockID"),
183|         "dealer": os.getenv("STRIPE_PRICE_DEALER", "price_1DealerMockID"),
184|         "estate": os.getenv("STRIPE_PRICE_ESTATE", "price_1EstateMockID"),
185|         "family_estate": os.getenv("STRIPE_PRICE_FAMILY_ESTATE", "price_1FamilyEstateMockID"),
186|         "sovereign": os.getenv("STRIPE_PRICE_SOVEREIGN", "price_1SovereignMockID"),
187|     }
188| 
189|     price_id = price_map.get(target_tier.lower(), price_map["pro"])
190| 
191|     session = stripe.checkout.Session.create(
192|         payment_method_types=["card"],
193|         customer_email=email,
194|         client_reference_id=user_id,
195|         line_items=[{"price": price_id, "quantity": 1}],
196|         mode="subscription",
197|         allow_promotion_codes=True,
198|         success_url=success_url,
199|         cancel_url=cancel_url,
200|         metadata={"user_uid": user_id, "user_email": email, "target_tier": target_tier}
201|     )
202|     return session.url
203| 
204| 
205| def create_customer_portal_session(user_id: str, email: str, return_url: str) -> str:
206|     sec_key = os.getenv("STRIPE_SECRET_KEY")
207|     if not sec_key:
208|         raise ValueError("STRIPE_SECRET_KEY is not set in environment.")
209|     stripe.api_key = sec_key
210| 
211|     user_doc_ref = db.collection("users").document(user_id)
212|     user_doc = user_doc_ref.get()
213|     customer_id = (user_doc.to_dict() or {}).get("stripe_customer_id") if user_doc.exists else None
214| 
215|     if not customer_id and stripe.api_key:
216|         existing = stripe.Customer.list(email=email, limit=1)
217|         if existing.data:
218|             customer_id = existing.data[0].id
219|         else:
220|             cust = stripe.Customer.create(email=email, metadata={"uid": user_id})
221|             customer_id = cust.id
222|         user_doc_ref.set({"stripe_customer_id": customer_id}, merge=True)
223| 
224|     if not customer_id:
225|         customer_id = f"cus_mock_{hash(user_id) & 0xffffffff}"
226| 
227|     session = stripe.billing_portal.Session.create(customer=customer_id, return_url=return_url)
228|     return session.url
229| 
230| # ==============================================================================
231| # 🛡️ FEATURE GATEKEEPING & ATOMIC USAGE
232| # ==============================================================================
233| 
234| def check_and_enforce_coin_limit(user_identifier: str, success_url: str = "https://numista.ai/#/settings?stripe=success", cancel_url: str = "https://numista.ai/#/settings?stripe=cancel") -> bool:
235|     user_profile = get_user_profile(user_identifier)
236|     tier = get_user_tier(user_profile)
237| 
238|     if tier == "power_user" or user_profile.get("power_user") is True:
239|         return True
240| 
241|     coin_count = get_coin_count(user_identifier)
242|     limit = TIER_COIN_LIMITS.get(tier, TIER_COIN_LIMITS["free"])
243| 
244|     if coin_count > limit:
245|         tier_order = ["free", "pro", "numismatist", "dealer", "estate", "family_estate", "sovereign"]
246|         try:
247|             current_idx = tier_order.index(tier)
248|             next_tier = tier_order[current_idx + 1] if current_idx + 1 < len(tier_order) else "sovereign"
249|         except ValueError:
250|             next_tier = "pro"
251| 
252|         email = user_profile.get("email") or user_identifier
253|         try:
254|             checkout_link = create_upgrade_checkout_session(user_identifier, email, next_tier, success_url, cancel_url)
255|         except Exception as ex:
256|             checkout_link = None
257| 
258|         detail = {
259|             "error": "tier_limit_exceeded",
260|             "message": f"Tier limit exceeded: You have {coin_count} items, but your {tier.capitalize()} tier limit is {limit} items.",
261|             "stats": {"coin_count": coin_count, "limit": limit, "tier": tier, "next_tier": next_tier},
262|             "upgrade_url": checkout_link
263|         }
264|         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
265| 
266|     return True
267| 
268| 
269| def check_and_increment_daily_usage(user_identifier: str, feature_type: str) -> bool:
270|     user_profile = get_user_profile(user_identifier)
271|     tier = get_user_tier(user_profile)
272| 
273|     if tier == "power_user" or user_profile.get("power_user") is True:
274|         return True
275| 
276|     today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
277|     family_group_id = user_profile.get("family_group_id")
278| 
279|     if family_group_id:
280|         target_ref = db.collection("family_groups").document(family_group_id)
281|         target_doc = target_ref.get()
282|         data = target_doc.to_dict() or {} if target_doc.exists else {}
283| 
284|         last_date = data.get("last_reset_utc", "")
285|         if last_date != today_str:
286|             target_ref.set({"last_reset_utc": today_str, "deepdive_count": 0, "invoice_scan_count": 0}, merge=True)
287|             data["deepdive_count"] = 0
288|             data["invoice_scan_count"] = 0
289| 
290|         allowance = TIER_DAILY_ALLOWANCES.get("family_estate")
291|         limit = allowance.get(feature_type, 1500)
292|         current_count = data.get(f"{feature_type}_count", 0)
293| 
294|         if current_count >= limit:
295|             return False
296| 
297|         target_ref.update({
298|             f"{feature_type}_count": firestore.Increment(1),
299|             "last_reset_utc": today_str
300|         })
301|         return True
302| 
303|     target_ref = db.collection("users").document(user_identifier)
304|     last_date = user_profile.get("last_usage_date", "")
305| 
306|     if last_date != today_str:
307|         target_ref.set({"last_usage_date": today_str, "deepdive_count": 0, "invoice_scan_count": 0}, merge=True)
308|         user_profile["deepdive_count"] = 0
309|         user_profile["invoice_scan_count"] = 0
310| 
311|     allowance = TIER_DAILY_ALLOWANCES.get(tier, TIER_DAILY_ALLOWANCES["free"])
312|     limit = allowance.get(feature_type, 0)
313|     current_count = user_profile.get(f"{feature_type}_count", 0)
314| 
315|     if current_count >= limit:
316|         return False
317| 
318|     target_ref.update({
319|         f"{feature_type}_count": firestore.Increment(1),
320|         "last_usage_date": today_str
321|     })
322|     return True
323| 
324| 
325| def lock_overflow_coins(user_id: str, limit: int):
326|     try:
327|         coins_ref = db.collection("users").document(user_id).collection("coins").order_by("created_at")
328|         docs = list(coins_ref.stream())
329|         if len(docs) <= limit:
330|             return
331|         batch = db.batch()
332|         for idx, doc in enumerate(docs):
333|             is_locked = idx >= limit
334|             batch.update(doc.reference, {"locked_pending_upgrade": is_locked})
335|         batch.commit()
336|     except Exception as e:
337|         print(f"[Tier Gatekeeper] Error locking overflow coins for {user_id}: {e}")
338| 
339| 
340| def unlock_user_coins(user_id: str):
341|     try:
342|         coins_ref = db.collection("users").document(user_id).collection("coins").where("locked_pending_upgrade", "==", True)
343|         docs = list(coins_ref.stream())
344|         if not docs:
345|             return
346|         batch = db.batch()
347|         for doc in docs:
348|             batch.update(doc.reference, {"locked_pending_upgrade": False})
349|         batch.commit()
350|     except Exception as e:
351|         print(f"[Tier Gatekeeper] Error unlocking coins for {user_id}: {e}")
~~~~

## numista_backend/routes/deps.py — Shared deps: db, storage_client, Admin init, auth (full file)


~~~~ numista_backend/routes/deps.py:1-132
1| """
2| routes/deps.py
3| --------------
4| Centralized dependencies, shared database clients, logging, and authentication middleware
5| for all Numista.AI APIRouters.
6| """
7| 
8| import os
9| import logging
10| from datetime import datetime, timezone
11| from typing import Optional, Dict, Any
12| from fastapi import Request, HTTPException, Depends
13| from google.cloud import firestore, storage as gcs
14| import firebase_admin
15| from firebase_admin import credentials, auth as firebase_auth
16| from google import genai
17| from google.genai import types as genai_types
18| 
19| logger = logging.getLogger("numista_backend.deps")
20| 
21| PROJECT_ID = "studio-9101802118-8c9a8"
22| 
23| # ── 1. Firestore & Storage Singletons ─────────────────────────────────────────
24| db = firestore.Client(project=PROJECT_ID)
25| storage_client = gcs.Client(project=PROJECT_ID)
26| 
27| # ── 2. Google GenAI Client (google-genai==1.71.0 Vertex AI standard) ───────────
28| try:
29|     genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
30|     logger.info("Successfully initialized Vertex AI Google GenAI Client.")
31| except Exception as ge:
32|     logger.warning(f"Failed to initialize Vertex AI GenAI Client: {ge}")
33|     genai_client = None
34| 
35| # Model Constants (Rule 6 compliant)
36| MODEL_FLASH = "gemini-3.8-flash"
37| MODEL_PRO = "gemini-3.1-pro-preview"
38| 
39| # ── 3. Firebase Admin SDK Initialization ──────────────────────────────────────
40| if not firebase_admin._apps:
41|     sa_path = os.path.join(os.path.dirname(__file__), "..", "serviceAccountKey.json")
42|     if not os.path.exists(sa_path):
43|         sa_path = os.path.join(os.path.dirname(__file__), "..", "serviceAccountKey.json.json")
44|     if os.path.exists(sa_path):
45|         cred = credentials.Certificate(sa_path)
46|         firebase_admin.initialize_app(cred, {'projectId': PROJECT_ID})
47|     else:
48|         firebase_admin.initialize_app(options={'projectId': PROJECT_ID})
49| 
50| # ── 4. Authentication Middleware Dependencies ─────────────────────────────────
51| 
52| def verify_firebase_bearer_token(request: Request) -> Optional[Dict[str, Any]]:
53|     """Extracts Authorization Bearer token (or query token) and verifies via Firebase Admin SDK."""
54|     auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
55|     token = None
56|     if auth_header and auth_header.startswith("Bearer "):
57|         token = auth_header.split("Bearer ")[1].strip()
58|     elif request.query_params.get("token"):
59|         token = request.query_params.get("token", "").strip()
60|     if not token:
61|         return None
62|     try:
63|         decoded_token = firebase_auth.verify_id_token(token)
64|         return decoded_token
65|     except Exception as e:
66|         logger.warning(f"Firebase token verification failed: {e}")
67|         return None
68| 
69| async def get_current_user(request: Request) -> Dict[str, Any]:
70|     """FastAPI dependency requiring a valid Firebase ID Token."""
71|     if hasattr(request.state, "user") and request.state.user:
72|         return request.state.user
73|     is_prod = os.environ.get("K_SERVICE") or os.environ.get("ENVIRONMENT") == "production"
74|     decoded = verify_firebase_bearer_token(request)
75|     if not decoded:
76|         if not is_prod and os.environ.get("ALLOW_UNAUTHENTICATED") == "1":
77|             return {"email": "dev_guest@numista.ai", "uid": "dev_guest_uid", "admin": False}
78|         raise HTTPException(status_code=401, detail="Authentication token missing or invalid")
79|     return decoded
80| 
81| async def get_current_user_email(request: Request, user: Dict[str, Any] = Depends(get_current_user)) -> str:
82|     """FastAPI dependency returning verified user email from token."""
83|     email = user.get("email")
84|     if not email:
85|         raise HTTPException(status_code=401, detail="User email not present in authentication token")
86|     return email
87| 
88| async def require_admin_user(request: Request, user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
89|     """FastAPI dependency requiring the Firebase custom claim 'admin': True.
90| 
91|     The email allowlist (eric@, admin@) has been intentionally removed — an unverified
92|     signup with those addresses would bypass this guard. Admin status is granted only
93|     by the bootstrap_admin_claim.py script via the Firebase Admin SDK.
94|     """
95|     if user.get("admin") is not True:
96|         raise HTTPException(status_code=403, detail="Admin privileges required")
97|     return user
98| 
99| 
100| def check_and_increment_rate_cap(uid: str, endpoint: str, daily_limit: int, is_admin: bool = False) -> None:
101|     """Per-user daily cap helper storing counts in _rate_limits/{uid}/{endpoint}/{YYYY-MM-DD}.
102| 
103|     1. Reads Firestore _rate_limits/{uid}/{endpoint}/{today_date} doc
104|     2. If count >= daily_limit: raise HTTPException(429, "Daily limit reached")
105|     3. Else: increment count atomically (use Firestore Increment)
106|     4. If Firestore read fails: raise HTTPException(429) - fail closed
107|     Admin users are exempt.
108|     """
109|     if is_admin:
110|         return
111|     today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
112|     clean_uid = str(uid).strip()
113|     clean_endpoint = str(endpoint).strip().lstrip("/")
114|     doc_ref = db.collection("_rate_limits").document(clean_uid).collection(clean_endpoint).document(today_date)
115|     try:
116|         snap = doc_ref.get()
117|         current_count = 0
118|         if snap.exists:
119|             data = snap.to_dict() or {}
120|             current_count = data.get("count", 0)
121|         if current_count >= daily_limit:
122|             raise HTTPException(status_code=429, detail="Daily limit reached")
123|         doc_ref.set({"count": firestore.Increment(1)}, merge=True)
124|     except HTTPException:
125|         raise
126|     except Exception as e:
127|         logger.warning(f"Rate cap check failed for {clean_uid}/{clean_endpoint}: {e}")
128|         raise HTTPException(status_code=429, detail="Daily limit reached")
129| 
130| 
131| _check_and_increment_rate_cap = check_and_increment_rate_cap
132| 
~~~~

## numista_backend/stripe_config.py — Stripe key loading (full)


~~~~ numista_backend/stripe_config.py:1-153
1| import os
2| import logging
3| from dotenv import load_dotenv
4| 
5| # Setup logging for backend tracking/auditing
6| logger = logging.getLogger(__name__)
7| 
8| # Load environment variables from a .env file (if present)
9| load_dotenv()
10| 
11| def load_stripe_keys():
12|     """
13|     Safely loads Stripe API keys from the application environment (os.environ)
14|     or falls back to Streamlit's st.secrets if Streamlit is available in the current context.
15| 
16|     This function is designed to handle missing credentials gracefully by logging
17|     actionable warnings rather than crashing the application startup.
18| 
19|     Returns:
20|         dict: A dictionary containing 'publishable_key' and 'secret_key'.
21|               Values will be None if loading fails.
22|     """
23|     stripe_keys = {
24|         "publishable_key": None,
25|         "secret_key": None
26|     }
27|     
28|     # 1. Primary Attempt: Load from Environment Variables (standard backend/.env method)
29|     pub_key = os.environ.get("STRIPE_PUBLISHABLE_KEY")
30|     sec_key = os.environ.get("STRIPE_SECRET_KEY")
31|     
32|     # 2. Secondary Attempt: Fallback to Streamlit st.secrets (if run in Streamlit context)
33|     is_streamlit_context = False
34|     streamlit_error = None
35|     
36|     if not (pub_key and sec_key):
37|         try:
38|             import streamlit as st
39|             is_streamlit_context = True
40|             
41|             # Retrieve keys if they exist in Streamlit secrets
42|             if "STRIPE_PUBLISHABLE_KEY" in st.secrets:
43|                 pub_key = pub_key or st.secrets["STRIPE_PUBLISHABLE_KEY"]
44|             if "STRIPE_SECRET_KEY" in st.secrets:
45|                 sec_key = sec_key or st.secrets["STRIPE_SECRET_KEY"]
46|                 
47|         except ImportError:
48|             # Streamlit is not installed in this environment, which is expected on production Cloud Run
49|             is_streamlit_context = False
50|         except Exception as se:
51|             streamlit_error = se
52|             
53|     # 3. Validation and SDK Initialization
54|     if pub_key and sec_key:
55|         # Basic validation to ensure the values are not empty strings
56|         if not pub_key.strip() or not sec_key.strip():
57|             logger.warning("Stripe keys found, but one or both are empty strings.")
58|             return stripe_keys
59|             
60|         # Ensure they are set in os.environ for global library compatibility
61|         os.environ["STRIPE_PUBLISHABLE_KEY"] = pub_key.strip()
62|         os.environ["STRIPE_SECRET_KEY"] = sec_key.strip()
63|         
64|         stripe_keys["publishable_key"] = pub_key.strip()
65|         stripe_keys["secret_key"] = sec_key.strip()
66|         
67|         # Configure Stripe Python SDK if installed
68|         try:
69|             import stripe
70|             stripe.api_key = stripe_keys["secret_key"]
71|             logger.info("Successfully configured Stripe SDK api_key.")
72|         except ImportError:
73|             logger.debug("Stripe SDK is not installed. Skipping direct stripe.api_key assignment.")
74|             
75|         return stripe_keys
76|         
77|     else:
78|         # Construct error details
79|         missing_vars = []
80|         if not pub_key:
81|             missing_vars.append("STRIPE_PUBLISHABLE_KEY")
82|         if not sec_key:
83|             missing_vars.append("STRIPE_SECRET_KEY")
84|         
85|         error_msg = f"Missing Stripe keys in environment variables: {', '.join(missing_vars)}"
86|         logger.warning(error_msg)
87|         
88|         # If running in Streamlit, show the diagnostic warning in the UI
89|         if is_streamlit_context:
90|             try:
91|                 import streamlit as st
92|                 st.warning("⚠️ **Stripe Configuration Missing or Incomplete**")
93|                 st.markdown(
94|                     f"""
95|                     We encountered an issue loading the Stripe API keys:
96|                     `Error: {error_msg}`
97|                     
98|                     Please ensure you have configured your local development secrets file:
99|                     1. Create or open the secrets file at `.streamlit/secrets.toml` in your project root.
100|                     2. Add the following key-value pairs using your Stripe test keys:
101|                     ```toml
102|                     STRIPE_PUBLISHABLE_KEY = "pk_test_..."
103|                     STRIPE_SECRET_KEY = "sk_test_..."
104|                     ```
105|                     3. Save the file and restart your Streamlit app.
106|                     """
107|                 )
108|             except Exception as ui_err:
109|                 logger.error(f"Failed to render Streamlit warning: {ui_err}")
110|                 
111|         return stripe_keys
112| 
113| # Standalone validator entrypoint
114| if __name__ == "__main__":
115|     # Check if we can run Streamlit testing CLI/UI or fallback to basic terminal print
116|     try:
117|         import streamlit as st
118|         
119|         # Streamlit is available, run the visual validation dashboard
120|         st.set_page_config(page_title="Stripe Key Validator", page_icon="💳", layout="centered")
121|         st.title("💳 Stripe Key Validation Tool")
122|         st.write("Checking credentials in both environment variables (`.env`) and `st.secrets`...")
123|         
124|         st.divider()
125|         
126|         keys = load_stripe_keys()
127|         
128|         if keys["publishable_key"] and keys["secret_key"]:
129|             st.success("🎉 **Stripe keys loaded successfully!**")
130|             masked_pub = keys["publishable_key"][:12] + "..." + keys["publishable_key"][-8:]
131|             masked_sec = keys["secret_key"][:12] + "..." + keys["secret_key"][-8:]
132|             st.info(
133|                 f"""
134|                 **Loaded Keys (Masked):**
135|                 - **STRIPE_PUBLISHABLE_KEY**: `{masked_pub}`
136|                 - **STRIPE_SECRET_KEY**: `{masked_sec}`
137|                 """
138|             )
139|     except ImportError:
140|         # Fallback to standard command-line validation (for FastAPI/Cloud Run environments)
141|         print("=" * 60)
142|         print("💳 Stripe Keys CLI Validator (FastAPI Backend)")
143|         print("=" * 60)
144|         keys = load_stripe_keys()
145|         if keys["publishable_key"] and keys["secret_key"]:
146|             masked_pub = keys["publishable_key"][:12] + "..." + keys["publishable_key"][-8:]
147|             masked_sec = keys["secret_key"][:12] + "..." + keys["secret_key"][-8:]
148|             print(f"[SUCCESS] Stripe keys loaded successfully!")
149|             print(f"  - STRIPE_PUBLISHABLE_KEY: {masked_pub}")
150|             print(f"  - STRIPE_SECRET_KEY:      {masked_sec}")
151|         else:
152|             print("[WARNING] Stripe keys are not configured. Check your '.env' file.")
153|         print("=" * 60)
~~~~

## numista_backend/main.py — main.py excerpts: CORS, clients, bucket, created_at, scraper trigger, by-id/count/clear routes, admin/scraper routes, transfer claim, appraisal bucket


~~~~ numista_backend/main.py:48-58
48| 
49| ALLOWED_ORIGINS = [
50|     "https://numista.ai",
51|     "https://www.numista.ai",
52|     "https://numista-vault.web.app",      # Firebase Hosting (production)
53|     "https://numista-vault.firebaseapp.com",  # Firebase Hosting (alt URL)
54|     "https://numista-vault--p7-gate-8avtpz22.web.app",  # P7 test channel
55|     "http://localhost:8080",
56|     "http://127.0.0.1:8080",
57|     "http://localhost:5000",
58|     "http://localhost:3000",
~~~~

~~~~ numista_backend/main.py:288-296
288| # incoming requests, runs last on outgoing responses).
289| # Placing CORSMiddleware here (after default_deny_auth_middleware and observability_middleware)
290| # ensures it is outermost and attaches Access-Control-Allow-* headers to ALL responses,
291| # including 401 unauthenticated errors returned by default_deny_auth_middleware.
292| app.add_middleware(
293|     CORSMiddleware,
294|     allow_origins=ALLOWED_ORIGINS,
295|     allow_origin_regex=ALLOWED_ORIGIN_REGEX,
296|     allow_credentials=True,
~~~~

~~~~ numista_backend/main.py:330-360
330|         return res
331|     except Exception as e:
332|         logger.error(f"RAG query endpoint error: {e}")
333|         return {"query": req.query, "answer": f"RAG search error: {str(e)}", "status": "error"}
334| 
335| PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "studio-9101802118-8c9a8")
336| LOCATION = "global"
337| 
338| # --- GCS USER CONTENT BUCKET ------------------------------------------------
339| # All user-uploaded files live here under a structured path:
340| #   gs://numista-user-content/{user_email}/{content_type}/{uuid}/
341| # Sub-folders: binder_scans/ | checklists/ | microscope/ | invoices/
342| USER_CONTENT_BUCKET = "numista-uploads-studio-9101802118-8c9a8"
343| 
344| # Initialize Firebase/Firestore 
345| _sa_path = Path(__file__).parent / "serviceAccountKey.json"
346| if _sa_path.exists():
347|     os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(_sa_path.resolve())
348| credentials, _ = google.auth.default()
349| db = firestore.Client(credentials=credentials, project=PROJECT_ID)
350| 
351| # Initialize GCS client (shares same SA credentials)
352| gcs_client = gcs.Client(credentials=credentials, project=PROJECT_ID)
353| 
354| # Initialize Firebase Admin SDK (for verify_id_token in deep_dive auth)
355| import firebase_admin
356| from firebase_admin import auth as fb_auth
357| if not firebase_admin._apps:
358|     firebase_admin.initialize_app()
359| 
360| # In-memory micro-cache for Grade Review Stats to bypass eventual consistency replication latency
~~~~

~~~~ numista_backend/main.py:2740-2750
2740|             "greysheet_bid": bid_val,
2741|             "greysheet_ask": ask_val,
2742|             "valuation_source": val_source,
2743|             "ai_value_status": ai_value_status,
2744|             "valuation_updated_at": datetime.now(timezone.utc).isoformat(),
2745|             "last_modified_by": "Morgan AI Assistant",
2746|             "Source": "Morgan AI Assistant Chat",
2747|             "created_at": firestore.SERVER_TIMESTAMP,
2748|         }
2749|         if dry_run:
2750|             snap = {k: v for k, v in coin_data.items() if k not in ("greysheet_bid", "greysheet_ask", "greysheetBid", "greysheetAsk")}
~~~~

~~~~ numista_backend/main.py:3332-3342
3332|                 logger.warning(f"Deep dive: knowledge base lookup warning: {kb_err}")
3333| 
3334|         # -- 3b. Auto-Scraper Trigger for Missing Coins -------------------------
3335|         lower_query = request.query.lower()
3336|         if any(x in lower_query for x in ["do we have", "is there", "add info for", "find images for", "scrape", "ordered", "released", "buy"]):
3337|             import re
3338|             import threading
3339|             import sqlite3
3340|             from numista_scraper.config import DB_PATH
3341|             from numista_scraper.url_scraper import scrape_url
3342| 
~~~~

~~~~ numista_backend/main.py:4145-4150
4145|     """
4146|     Uploads bytes to the user-content GCS bucket.
4147|     Returns the public gs:// URI.
4148|     """
4149|     bucket = gcs_client.bucket(USER_CONTENT_BUCKET)
4150|     blob   = bucket.blob(dest_path)
~~~~

~~~~ numista_backend/main.py:4405-4432
4405| 
4406|         # Download the full binder page from GCS
4407|         from google.cloud import storage as _gcs
4408|         import re as _re
4409| 
4410|         # Parse GCS URL: could be gs:// or https://storage.googleapis.com/
4411|         if gcs_url.startswith('gs://'):
4412|             bucket_name, blob_name = gcs_url[5:].split('/', 1)
4413|         elif 'storage.googleapis.com' in gcs_url:
4414|             m = _re.match(
4415|                 r'https://storage\.googleapis\.com/([^/]+)/(.+)', gcs_url)
4416|             if not m:
4417|                 raise HTTPException(status_code=400,
4418|                     detail='Cannot parse GCS URL.')
4419|             bucket_name, blob_name = m.group(1), m.group(2)
4420|         else:
4421|             # Not a GCS URL (could be Firebase Storage CDN URL)
4422|             # Fall back to full-page display
4423|             return {
4424|                 'status':    'fallback',
4425|                 'message':   'Image not in GCS -- showing full binder page.',
4426|                 'image_url': gcs_url,
4427|                 'coin_id':   coin_id,
4428|             }
4429| 
4430|         _gcs_client = _gcs.Client()
4431|         bucket = _gcs_client.bucket(bucket_name)
4432|         blob   = bucket.blob(blob_name)
~~~~

~~~~ numista_backend/main.py:8720-8742
8720| 
8721| 
8722| @app.get("/api/collection/count")
8723| def collection_count(
8724|     authorization: Optional[str] = Header(None),
8725|     user_email: str = "",
8726|     _user: dict = Depends(get_current_user),
8727| ):
8728|     """Return expanded coin/lot counts. Token-verified with ownership check.
8729| 
8730|     Returns:
8731|         { "owner": str, "user_email": str, "coins": int, "lots": int, "sets": int }
8732|     """
8733|     try:
8734|         owner_key = _authenticate_request(authorization, user_email if user_email else None, current_user=_user)
8735|         target_owner = user_email.strip().lower() if user_email else owner_key
8736| 
8737|         # --- Expand and count ---
8738|         coins_ref = db.collection('users').document(target_owner).collection('coins')
8739|         docs = coins_ref.stream()
8740|         inventory, stats = expand_collection_inventory(docs)
8741|         counts = count_coins_and_lots(inventory)
8742| 
~~~~

~~~~ numista_backend/main.py:8984-8990
8984| 
8985| 
8986| @app.post("/api/collection/clear")
8987| def collection_clear(
8988|     req: ClearCollectionRequest,
8989|     user: Dict[str, Any] = Depends(get_current_user),
8990| ):
~~~~

~~~~ numista_backend/main.py:9603-9609
9603|     Checks the version status of the SQLite catalog.
9604|     """
9605|     try:
9606|         storage_client = gcs.Client()
9607|         bucket = storage_client.bucket("numista-reference-library")
9608|         blob = bucket.get_blob("numista_coins.db")
9609|         if blob:
~~~~

~~~~ numista_backend/main.py:10188-10194
10188|     # Set lock
10189|     lock_ref.set({"running": True, "started_at": time.time()})
10190| 
10191|     try:
10192|         from numista_scraper.agent import NumistaScraperAgent
10193|         
10194|         agent = NumistaScraperAgent(mode=mode)
~~~~

~~~~ numista_backend/main.py:10595-10626
10595| 
10596| @app.post("/api/admin/brain/reprocess")
10597| async def reprocess_knowledge(req: BrainKnowledgeUpdate, _admin: dict = Depends(require_admin_user)):
10598|     """Triggers a re-process of a document with new instructions."""
10599|     doc_ref = db.collection('brain_knowledge_base').document(req.doc_id)
10600|     doc = doc_ref.get()
10601|     if not doc.exists:
10602|         raise HTTPException(status_code=404, detail="Document not found")
10603|     
10604|     data = doc.to_dict()
10605|     file_path = Path(data['file_path'])
10606|     
10607|     # In a real scenario, we'd trigger the processor asynchronously
10608|     # For now, we call it directly (blocking for the API call)
10609|     from brain_processor import absorb_document
10610|     absorb_document(file_path, req.intent)
10611|     
10612|     return {"status": "reprocessing_started"}
10613| 
10614| 
10615| @app.post("/api/admin/brain/sync_canon")
10616| async def sync_brain_canon_to_gcp(_admin: dict = Depends(require_admin_user)):
10617|     """
10618|     On-demand sync:
10619|     1. Formats approved/high-confidence Brain docs into Markdown payloads and uploads to GCS.
10620|     2. Triggers Vertex AI Search Data Store re-indexing.
10621|     """
10622|     try:
10623|         from services.canon_sync_service import sync_canon_to_gcs
10624|         from scripts.refresh_vertex_data_store import refresh_vertex_data_store
10625| 
10626|         sync_result = sync_canon_to_gcs()
~~~~

~~~~ numista_backend/main.py:10455-10465
10455| 
10456| 
10457| @app.post("/api/scraper/scrape-url")
10458| def scrape_url_endpoint(data: ScrapeUrlRequest, _admin: dict = Depends(require_admin_user)):
10459|     """
10460|     Trigger scraping of a specific URL (e.g. Wikipedia Semiquincentennial page).
10461|     """
10462|     try:
10463|         from numista_scraper.url_scraper import scrape_url
10464|         results = scrape_url(data.url, dry_run=data.dry_run)
10465|         return {"status": "success", "results": results}
~~~~

~~~~ numista_backend/main.py:12094-12100
12094|     token_uid = current_user.get("email") or current_user.get("uid") or ""
12095|     if not token_uid:
12096|         raise HTTPException(status_code=401, detail="Unable to identify user from token")
12097|     try:
12098|         from services.transfer_service import claim_transfer
12099|         result = claim_transfer(
12100|             db=db,
~~~~

~~~~ numista_backend/main.py:12276-12284
12276|             "items": items[:50] if items else []
12277|         })
12278| 
12279|         if gcs_client:
12280|             try:
12281|                 bucket_name = os.environ.get("GCS_BUCKET_NAME", "studio-9101802118-8c9a8-uploads")
12282|                 gcs_path = f"users/{req.user_email}/appraisals/Appraisal_Schedule_{_dt.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
12283|                 blob = gcs_client.bucket(bucket_name).blob(gcs_path)
12284|                 blob.upload_from_string(pdf_bytes, content_type="application/pdf")
~~~~

## numista_backend/routes/import_routes.py — Import routes: bucket and uid-folder coin writes


~~~~ numista_backend/routes/import_routes.py:15-23
15| from schemas.import_schemas import SignedUrlRequest, ImportProcessRequest, ImportStartRequest, CommitBatchRequest
16| from services.common import GOLDEN_SCHEMA_MAPPING, normalize_colloquial_header, safe_get_str, normalize_slang_term
17| from routes.deps import db, storage_client, logger, get_current_user, PROJECT_ID, _check_and_increment_rate_cap
18| 
19| router = APIRouter(prefix="/api", tags=["Spreadsheet & Document Bulk Ingestion"])
20| 
21| BUCKET_NAME = "studio-9101802118-8c9a8-uploads"
22| 
23| # ── Helper Functions ─────────────────────────────────────────────────────────
~~~~

~~~~ numista_backend/routes/import_routes.py:50-56
50|     blob_name = f"imports/{user_id}/{uuid.uuid4().hex}_{req.filename}"
51|     
52|     try:
53|         bucket = storage_client.bucket(BUCKET_NAME)
54|         blob = bucket.blob(blob_name)
55|         signed_url = blob.generate_signed_url(
56|             version="v4",
~~~~

~~~~ numista_backend/routes/import_routes.py:90-120
90|         _check_and_increment_rate_cap(user_id, "import_spreadsheet", 5)
91|     session_id = import_session_id or f"imp_{uuid.uuid4().hex[:8]}"
92| 
93|     # 1. Obtain bytes from GCS or Direct Upload
94|     if gcs_uri and gcs_uri.startswith("gs://"):
95|         parts = gcs_uri.replace("gs://", "").split("/", 1)
96|         bucket = storage_client.bucket(parts[0])
97|         blob = bucket.blob(parts[1])
98|         contents = blob.download_as_bytes()
99|         filename = parts[1].split("/")[-1]
100|     elif file:
101|         contents = await file.read()
102|         filename = file.filename or "upload.csv"
103|     else:
104|         raise HTTPException(status_code=400, detail="Must provide direct file upload or gcs_uri")
105| 
106|     try:
107|         df = _read_spreadsheet_bytes(contents, filename)
108|     except Exception as e:
109|         raise HTTPException(status_code=400, detail=f"Failed to parse file: {e}")
110| 
111|     headers = list(df.columns)
112|     mapping = {h: normalize_colloquial_header(h) for h in headers}
113| 
114|     # 2. Fetch existing user collection for 3-tier deduplication
115|     existing_certs = set()
116|     existing_combos = set()
117|     try:
118|         existing_docs = db.collection("users").document(user_id).collection("coins").get()
119|         for d in existing_docs:
120|             data = d.to_dict() or {}
~~~~

~~~~ numista_backend/routes/import_routes.py:236-244
236| @router.post("/v1/import/commit_batch")
237| async def commit_batch(req: CommitBatchRequest, user: Dict[str, Any] = Depends(get_current_user)):
238|     """
239|     Executes non-blocking partial batch commits from staging to users/{userId}/coins.
240|     """
241|     user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"
242|     coins_ref = db.collection("users").document(user_id).collection("coins")
243|     staging_ref = db.collection("users").document(user_id).collection("staging_area")
244| 
~~~~

## numista_backend/routes/estate_routes.py — Estate routes: bucket and storage client


~~~~ numista_backend/routes/estate_routes.py:18-22
18| router = APIRouter(prefix="/api/v1/estate", tags=["Estate Planning & Attorney Portal"])
19| 
20| BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "studio-9101802118-8c9a8-uploads")
21| 
22| # ==============================================================================
~~~~

~~~~ numista_backend/routes/estate_routes.py:40-44
40|     """Yields file byte chunks directly from GCS without loading full PDF into RAM."""
41|     try:
42|         storage_client = storage.Client()
43|         bucket = storage_client.bucket(bucket_name)
44|         blob = bucket.blob(blob_path)
~~~~

## numista_backend/routes/support_routes.py — Support routes: lazy Firestore client


~~~~ numista_backend/routes/support_routes.py:30-40
30| # ── Firestore client (shared with main app) ─────────────────────────────────
31| _db: Optional[firestore.Client] = None
32| _auth_client = None  # firebase_admin.auth module reference
33| 
34| 
35| def _get_db() -> firestore.Client:
36|     global _db
37|     if _db is None:
38|         _db = firestore.Client()
39|     return _db
40| 
~~~~

## numista_backend/routes/subaccount_routes.py — Subaccount routes: lazy Firestore client


~~~~ numista_backend/routes/subaccount_routes.py:20-28
20| # Lazy-initialized Firestore client
21| _db = None
22| 
23| def get_db():
24|     global _db
25|     if _db is None:
26|         _db = firestore.Client(project="studio-9101802118-8c9a8")
27|     return _db
28| 
~~~~

## numista_backend/routes/feedback_callable_route.py — Feedback route: bucket


~~~~ numista_backend/routes/feedback_callable_route.py:28-38
28| from google.cloud import firestore, storage as gcs
29| from pydantic import BaseModel
30| 
31| from .deps import db, genai_client, get_current_user, require_admin_user, storage_client, MODEL_FLASH
32| 
33| logger = logging.getLogger("numista_backend.feedback_callable")
34| router = APIRouter(prefix="/api/feedback", tags=["MORGAN Feedback Callable"])
35| 
36| PROJECT_ID = "studio-9101802118-8c9a8"
37| GCS_BUCKET = "studio-9101802118-8c9a8-uploads"
38| GCS_STANDARD_PREFIX = "feedback_screenshots"
~~~~

~~~~ numista_backend/routes/feedback_callable_route.py:490-496
490|         raise HTTPException(status_code=500, detail="Lock missing draft_doc_id")
491| 
492|     # GCS signed PUT URL
493|     object_name = f"{GCS_STANDARD_PREFIX}/{uid}/{draft_doc_id}/screenshot.jpg"
494|     bucket = storage_client.bucket(GCS_BUCKET)
495|     blob = bucket.blob(object_name)
496|     expiry = timedelta(minutes=UPLOAD_URL_EXPIRY_MINUTES)
~~~~

## numista_backend/routes/scan_routes.py — Scan route: uid coin folder


~~~~ numista_backend/routes/scan_routes.py:308-314
308| 
309|         if not staged_docs:
310|             return {"status": "no_items", "message": "No active staged items found for session"}
311| 
312|         coins_col = db.collection("users").document(caller_uid).collection("coins")
313|         audit_col = db.collection("users").document(caller_uid).collection("audit_log")
314|         queue_col = db.collection("users").document(caller_uid).collection("review_queue")
~~~~

## numista_backend/services/canon_sync_service.py — Canon sync: production clients


~~~~ numista_backend/services/canon_sync_service.py:1-27
1| import os
2| import json
3| import logging
4| from datetime import datetime
5| from pathlib import Path
6| from google.cloud import storage, firestore
7| import google.auth
8| 
9| # --- CONFIGURATION ---
10| PROJECT_ID = "studio-9101802118-8c9a8"
11| BUCKET_NAME = "studio-9101802118-8c9a8-uploads"
12| CANON_PREFIX = "canon_library"
13| 
14| logging.basicConfig(
15|     level=logging.INFO,
16|     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
17| )
18| logger = logging.getLogger("CanonSyncService")
19| 
20| 
21| def get_gcp_clients():
22|     """Initializes Google Cloud clients with default credentials."""
23|     credentials, _ = google.auth.default()
24|     db = firestore.Client(credentials=credentials, project=PROJECT_ID)
25|     storage_client = storage.Client(credentials=credentials, project=PROJECT_ID)
26|     return db, storage_client
27| 
~~~~

## numista_backend/brain_processor.py — Brain processor: module-level Firestore client


~~~~ numista_backend/brain_processor.py:40-56
40| )
41| logger = logging.getLogger("BrainProcessor")
42| 
43| # Initialize Clients
44| db = None
45| genai_client = None
46| try:
47|     _sa_path = Path(__file__).parent / "serviceAccountKey.json"
48|     if _sa_path.exists():
49|         os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(_sa_path.resolve())
50|     credentials, _ = google.auth.default()
51|     db = firestore.Client(credentials=credentials, project=PROJECT_ID)
52|     genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
53|     logger.info("BrainProcessor clients initialized successfully.")
54| except Exception as e:
55|     logger.error(f"Failed to initialize clients: {e}")
56|     raise RuntimeError(f"BrainProcessor cannot start — auth/client init failed: {e}") from e
~~~~

## numista_backend/numista_scraper/storage.py — Scraper storage: Admin init, clients, bucket


~~~~ numista_backend/numista_scraper/storage.py:1-40
1| import os
2| import sqlite3
3| import requests
4| from google.cloud import storage as gcs_storage
5| from google.oauth2 import service_account
6| import firebase_admin
7| from firebase_admin import credentials, firestore
8| 
9| # Load configuration settings
10| try:
11|     from .config import DB_PATH, KEY_PATH, BUCKET_NAME, GCP_PROJECT, get_scrape_proxy
12| except ImportError:
13|     DB_PATH = "database/numista_coins.db"
14|     KEY_PATH = "serviceAccountKey.json.json"
15|     BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"
16|     GCP_PROJECT = "studio-9101802118-8c9a8"
17|     def get_scrape_proxy(): return {"http": None, "https": None}
18| 
19| # ─── Initialization ──────────────────────────────────────────────────────────
20| 
21| # Initialize Firebase Admin if not already initialized
22| try:
23|     firebase_admin.get_app()
24| except ValueError:
25|     if os.path.exists(KEY_PATH):
26|         firebase_admin.initialize_app(credentials.Certificate(str(KEY_PATH)))
27|     else:
28|         # Fallback to Application Default Credentials
29|         firebase_admin.initialize_app(options={"projectId": GCP_PROJECT})
30| 
31| db = firestore.client()
32| 
33| # Initialize Google Cloud Storage
34| if os.path.exists(KEY_PATH):
35|     sa_creds = service_account.Credentials.from_service_account_file(str(KEY_PATH))
36|     gcs_client = gcs_storage.Client(credentials=sa_creds, project=GCP_PROJECT)
37| else:
38|     gcs_client = gcs_storage.Client(project=GCP_PROJECT)
39| bucket = gcs_client.bucket(BUCKET_NAME)
40| 
~~~~

## numista_backend/numista_scraper/scrapers.py — Scraper: firestore.client()


~~~~ numista_backend/numista_scraper/scrapers.py:144-148
144|     try:
145|         from firebase_admin import firestore
146|         db = firestore.client()
147|         doc = db.collection("config").document("pcgs").get()
148|         token = doc.to_dict().get("bearerToken") if doc.exists else None
~~~~

~~~~ numista_backend/numista_scraper/scrapers.py:703-707
703|     try:
704|         from firebase_admin import firestore
705|         db = firestore.client()
706|         doc = db.collection("config").document("usmint").get()
707|         if doc.exists:
~~~~

~~~~ numista_backend/numista_scraper/scrapers.py:729-733
729|     try:
730|         from firebase_admin import firestore
731|         db = firestore.client()
732|         doc = db.collection("config").document("usmint").get()
733|         if doc.exists:
~~~~

## numista_backend/numista_scraper/config.py — Scraper config: bucket, Admin init


~~~~ numista_backend/numista_scraper/config.py:10-14
10| # GCP/Firebase Config
11| GCP_PROJECT = "studio-9101802118-8c9a8"
12| BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"
13| 
14| # Scraper Settings
~~~~

~~~~ numista_backend/numista_scraper/config.py:114-125
114|     if not os.environ.get("SKIP_REMOTE_PROXY_CHECK") and (force_check or (now - _last_check_time > _CHECK_INTERVAL_SEC)):
115|         _last_check_time = now
116|         try:
117|             from firebase_admin import firestore as _fs, initialize_app, _apps, credentials
118|             if not _apps:
119|                 if os.path.exists(KEY_PATH):
120|                     cred = credentials.Certificate(str(KEY_PATH))
121|                     initialize_app(cred)
122|                 else:
123|                     initialize_app()
124|             db = _fs.client()
125|             doc = db.collection("config").document("webshare_proxies").get()
~~~~

~~~~ numista_backend/numista_scraper/config.py:184-194
184|     """Load proxy list from Firestore config/webshare_proxies."""
185|     try:
186|         from firebase_admin import firestore as _fs, initialize_app, _apps, credentials
187|         if not _apps:
188|             if os.path.exists(KEY_PATH):
189|                 cred = credentials.Certificate(str(KEY_PATH))
190|                 initialize_app(cred)
191|             else:
192|                 initialize_app()
193|         db = _fs.client()
194|         doc = db.collection("config").document("webshare_proxies").get()
~~~~

## numista_backend/services/transfer_service.py — Transfer service: item collections, claim


~~~~ numista_backend/services/transfer_service.py:58-90
58| 
59| 
60| def resolve_item_collections(item_data: dict, uid: str, db: firestore.Client):
61|     """
62|     Dynamically resolves the target subcollection reference for an item.
63|     Primary canonical name for paper money is 'banknotes', with fallback check for legacy 'currency' subcollection.
64|     """
65|     clean_uid = uid.strip().lower() if "@" in uid else uid.strip()
66|     item_type = str(item_data.get("item_type") or item_data.get("category") or "").lower()
67| 
68|     is_paper_money = item_type in ["paper_currency", "banknote", "currency", "paper_money", "note"] or "FR-" in str(item_data.get("Variety", ""))
69| 
70|     subcollection = "banknotes" if is_paper_money else "coins"
71|     ref = db.collection("users").document(clean_uid).collection(subcollection)
72| 
73|     # Fallback lookup for legacy accounts that might hold paper money under 'currency'
74|     if is_paper_money and "id" in item_data:
75|         item_id = item_data["id"]
76|         try:
77|             if not ref.document(item_id).get().exists:
78|                 legacy_ref = db.collection("users").document(clean_uid).collection("currency")
79|                 if legacy_ref.document(item_id).get().exists:
80|                     return legacy_ref
81|         except Exception:
82|             pass
83| 
84|     return ref
85| 
86| 
87| def initiate_transfer(
88|     db: firestore.Client,
89|     user_a_id: str,
90|     item_ids: List[str],
~~~~

~~~~ numista_backend/services/transfer_service.py:380-390
380|     }
381| 
382| 
383| def claim_transfer(
384|     db: firestore.Client,
385|     user_b_id: str,
386|     transfer_id: str,
387|     claim_pin: str,
388|     selected_item_ids: Optional[List[str]] = None
389| ) -> Dict[str, Any]:
390|     """
~~~~

## numista_backend/functions/index.js — Cloud Functions (full; no coin triggers)


~~~~ numista_backend/functions/index.js:1-61
1| ﻿const { onRequest } = require("firebase-functions/v2/https");
2| const { onDocumentCreated } = require("firebase-functions/v2/firestore");
3| const logger = require("firebase-functions/logger");
4| const admin = require("firebase-admin");
5| const app = require("./server");
6| 
7| // Initialize Firebase Admin (safe to call multiple times)
8| if (!admin.apps.length) {
9|   admin.initializeApp();
10| }
11| 
12| // ── Existing HTTP function ────────────────────────────────────────────────────
13| exports.app = onRequest({ region: "us-west1", minInstances: 0 }, app);
14| 
15| // ── Feedback Intelligence trigger ────────────────────────────────────────────
16| // Fires within seconds of every new beta_feedback document being created.
17| // Pipeline: Gemini analysis → enrich Firestore doc → email alert → monthly rollup
18| const {
19|   analyzeWithGemini,
20|   sendAlertEmail,
21|   updateInsights,
22|   enrichFeedbackDoc,
23| } = require("./feedbackIntelligence");
24| 
25| exports.onFeedbackCreated = onDocumentCreated(
26|   {
27|     document: "beta_feedback/{docId}",
28|     region: "us-central1",
29|     secrets: ["NUMISTA_GMAIL_APP_PASSWORD"],
30|     timeoutSeconds: 120,
31|     memory: "512MiB",
32|   },
33|   async (event) => {
34|     const snap = event.data;
35|     if (!snap) {
36|       logger.warn("onFeedbackCreated: no snapshot data");
37|       return;
38|     }
39| 
40|     const doc = snap.data();
41|     const docId = event.params.docId;
42|     logger.info(`onFeedbackCreated: processing ${docId} type=${doc.issue_type}`);
43| 
44|     try {
45|       // 1. Gemini analysis (parallel-safe — reads only)
46|       const analysis = await analyzeWithGemini(doc);
47|       logger.info(`Analysis complete for ${docId}`, { tags: analysis.pattern_tags });
48| 
49|       // 2-4. Write back, send email, update rollup (in parallel)
50|       await Promise.allSettled([
51|         enrichFeedbackDoc(docId, analysis),
52|         sendAlertEmail(doc, analysis),
53|         updateInsights(doc, analysis),
54|       ]);
55| 
56|       logger.info(`onFeedbackCreated: complete for ${docId}`);
57|     } catch (err) {
58|       logger.error(`onFeedbackCreated: unhandled error for ${docId}`, err);
59|     }
60|   }
61| );
~~~~

## numista_backend/Dockerfile — Backend Dockerfile (full)


~~~~ numista_backend/Dockerfile:1-24
1| # Use the official Python lightweight image.
2| # https://hub.docker.com/_/python
3| FROM python:3.11-slim
4| 
5| # Allow statements and log messages to immediately appear in the Knative logs
6| ENV PYTHONUNBUFFERED=True
7| 
8| # Copy local code to the container image.
9| ENV APP_HOME=/app
10| WORKDIR $APP_HOME
11| COPY . ./
12| COPY NumisMate_Collection_Template.xlsx .
13| 
14| # Install system dependencies for pillow-heif (HEIC→JPEG conversion)
15| RUN apt-get update && apt-get install -y --no-install-recommends libheif-dev && rm -rf /var/lib/apt/lists/*
16| 
17| # Upgrade pip first to ensure the latest resolver handles complex dependency trees correctly.
18| RUN pip install --upgrade pip
19| 
20| # Install production dependencies.
21| RUN pip install --no-cache-dir --upgrade-strategy eager -r requirements.txt
22| 
23| # Run the web service on container startup using Uvicorn.
24| CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
~~~~

## numista_backend/.dockerignore — .dockerignore


~~~~ numista_backend/.dockerignore:15-24
15| app.py
16| 
17| # Sensitive secrets and keys
18| .env
19| .env.*
20| serviceAccountKey*.json
21| ebay_token.txt
22| *.log
23| scratch/
24| error_logs/
~~~~

## numista_backend/tests/test_idor_fixes.py — Existing subscription-status test


~~~~ numista_backend/tests/test_idor_fixes.py:470-484
470|     assert resp.status_code == 403
471|     assert resp.json()["detail"] == "Forbidden"
472| 
473| 
474| def test_subscription_status_token_a_uid_a_not_403():
475|     """Token A requesting own subscription status -> passes ownership check."""
476|     app.dependency_overrides[get_current_user] = lambda: _user_a()
477|     client = TestClient(app, raise_server_exceptions=False)
478|     with patch("routes.payment_routes.get_user_profile", return_value={}):
479|         with patch("routes.payment_routes.get_user_tier", return_value="free"):
480|             with patch("routes.payment_routes.get_coin_count", return_value=0):
481|                 resp = client.get("/api/stripe/subscription-status?uid=user_A")
482|                 assert resp.status_code != 403
483| 
484| 
~~~~

## numista_mobile/firestore.rules.test.js — Existing Jest rules test harness


~~~~ numista_mobile/firestore.rules.test.js:1-45
1| /**
2|  * firestore.rules.test.js
3|  * =======================
4|  * ADDENDUM B — Firestore field-level rules unit tests
5|  * Tests the affectedKeys() guards on is_demo, is_demo_cleared, sandbox_cleared.
6|  *
7|  * Run: npx @firebase/rules-unit-testing  (from numista_mobile/)
8|  * Or:  firebase emulators:exec --only firestore "npx jest firestore.rules.test.js"
9|  *
10|  * Acceptance criteria from ITEM 6 + v4.1 Addendum B:
11|  *   [ ] Client SDK attempt to set is_demo: true on own coin returns PERMISSION_DENIED
12|  *   [ ] Client SDK attempt to change is_demo_cleared on own coin returns PERMISSION_DENIED
13|  *   [ ] Client SDK attempt to change sandbox_cleared on own profile returns PERMISSION_DENIED
14|  *   [ ] Client SDK can create a coin with is_demo: false (allowed)
15|  *   [ ] Client SDK can create a coin without is_demo field (allowed; backfill covers it)
16|  *   [ ] Client SDK can update other coin fields without touching is_demo (allowed)
17|  */
18| 
19| const { initializeTestEnvironment, assertFails, assertSucceeds } =
20|   require("@firebase/rules-unit-testing");
21| const { doc, setDoc, updateDoc, getDoc, collection, getDocs } = require("firebase/firestore");
22| const fs = require("fs");
23| const path = require("path");
24| 
25| const PROJECT_ID = "studio-9101802118-8c9a8";
26| const RULES_PATH = path.join(__dirname, "firestore.rules");
27| 
28| let testEnv;
29| let ownerCtx;
30| let otherCtx;
31| 
32| beforeAll(async () => {
33|   testEnv = await initializeTestEnvironment({
34|     projectId: PROJECT_ID,
35|     firestore: {
36|       rules: fs.readFileSync(RULES_PATH, "utf8"),
37|       host: "127.0.0.1",
38|       port: 8080,
39|     },
40|   });
41| 
42|   // Owner: authenticated user whose email matches the path
43|   ownerCtx = testEnv.authenticatedContext("owner_uid", { email: "testowner@numista.ai" });
44| 
45|   // Other user: different uid and email
~~~~

## numista_mobile/package.json — Mobile package.json (full)


~~~~ numista_mobile/package.json:1-17
1| {
2|   "name": "numista-firestore-rules-tests",
3|   "version": "1.0.0",
4|   "description": "Firestore security rules unit tests for Numista.AI",
5|   "scripts": {
6|     "test": "jest firestore.rules.test.js"
7|   },
8|   "devDependencies": {
9|     "@firebase/rules-unit-testing": "^4.0.1",
10|     "firebase": "^11.0.0",
11|     "jest": "^29.0.0"
12|   },
13|   "jest": {
14|     "testEnvironment": "node",
15|     "testTimeout": 30000
16|   }
17| }
~~~~

## numista_mobile/lib/constants.dart — API base URL default


~~~~ numista_mobile/lib/constants.dart:10-17
10| // Project:  studio-9101802118-8c9a8
11| // Service:  numista-backend  (revision 00061-lbh, Jun 14 2026)
12| // Region:   us-central1
13| const String kApiBaseUrl = String.fromEnvironment(
14|   'API_BASE_URL',
15|   defaultValue: 'https://numista-backend-568985927038.us-central1.run.app',
16| );
17| 
~~~~

## numista_mobile/lib/firebase_options.dart — Firebase options (apiKey/appId values redacted by packet preparer)


~~~~ numista_mobile/lib/firebase_options.dart:45-75
45|         );
46|     }
47|   }
48| 
49|   static const FirebaseOptions web = FirebaseOptions(
50|     apiKey: '<REDACTED>',
51|     appId: '<REDACTED>',
52|     messagingSenderId: '<REDACTED>',
53|     projectId: 'studio-9101802118-8c9a8',
54|     authDomain: 'studio-9101802118-8c9a8.firebaseapp.com',
55|     storageBucket: 'studio-9101802118-8c9a8.firebasestorage.app',
56|     measurementId: 'G-EPZEHXZR5P',
57|   );
58| 
59|   static const FirebaseOptions android = FirebaseOptions(
60|     apiKey: '<REDACTED>',
61|     appId: '<REDACTED>',
62|     messagingSenderId: '<REDACTED>',
63|     projectId: 'studio-9101802118-8c9a8',
64|     storageBucket: 'studio-9101802118-8c9a8.firebasestorage.app',
65|   );
66| 
67|   static const FirebaseOptions windows = FirebaseOptions(
68|     apiKey: '<REDACTED>',
69|     appId: '<REDACTED>',
70|     messagingSenderId: '<REDACTED>',
71|     projectId: 'studio-9101802118-8c9a8',
72|     authDomain: 'studio-9101802118-8c9a8.firebaseapp.com',
73|     storageBucket: 'studio-9101802118-8c9a8.firebasestorage.app',
74|     measurementId: 'G-7R4F1W3Q03',
75|   );
~~~~

## numista_mobile/lib/screens/base_layout.dart — Base layout: email-folder coin read; initState


~~~~ numista_mobile/lib/screens/base_layout.dart:105-118
105|   Future<List<MorganSearchResult>> _onMorganSearch(String query) async {
106|     try {
107|       final email = FirebaseAuth.instance.currentUser?.email ?? '';
108|       if (email.isEmpty) return [];
109|       final q = query.toLowerCase();
110|       final snap = await FirebaseFirestore.instance
111|           .collection('users')
112|           .doc(email)
113|           .collection('coins')
114|           .get();
115|       return snap.docs
116|           .where((d) {
117|             final data = d.data();
118|             final denom   = (data['Denomination']   ?? '').toString().toLowerCase();
~~~~

~~~~ numista_mobile/lib/screens/base_layout.dart:190-200
190|         );
191|       }
192|     }
193|   }
194| 
195|   @override
196|   void initState() {
197|     super.initState();
198|     _loadDefaultTab();
199|     _loadDesktopPrefs();
200|  
~~~~

## numista_mobile/lib/screens/my_collection_screen.dart — Only app write of users/{uid} doc (sort prefs)


~~~~ numista_mobile/lib/screens/my_collection_screen.dart:350-366
350|   Future<void> _saveSortPreferences(int colIdx, bool asc) async {
351|     try {
352|       final prefs = await SharedPreferences.getInstance();
353|       await prefs.setInt('col_sort_index', colIdx);
354|       await prefs.setBool('col_sort_asc', asc);
355| 
356|       final user = FirebaseAuth.instance.currentUser;
357|       if (user != null) {
358|         final fieldName = (colIdx >= 0 && colIdx < _columns.length) ? _columns[colIdx].field : 'created_at';
359|         await FirebaseFirestore.instance.collection('users').doc(user.uid).set({
360|           'default_sort_field': fieldName,
361|           'default_sort_asc': asc,
362|         }, SetOptions(merge: true));
363|       }
364|     } catch (e) {
365|       debugPrint('[MyCollection] Error saving sort prefs: $e');
366|     }
~~~~

## numista_mobile/lib/widgets/roll_entry_dialog.dart — Roll wizard: client SDK coin create (added_at, no created_at)


~~~~ numista_mobile/lib/widgets/roll_entry_dialog.dart:364-392
364| 
365|   // ── Commit to Firestore ───────────────────────────────────────────────────
366|   Future<void> _commit() async {
367|     final rollId = 'roll_${_denom}_${DateTime.now().millisecondsSinceEpoch}';
368|     final email  = AuthService.userEmail;
369|     final col    = FirebaseFirestore.instance.collection('users').doc(email).collection('coins');
370|     var batch    = FirebaseFirestore.instance.batch();
371|     int count    = 0;
372| 
373|     for (final coin in _preview) {
374|       final doc = col.doc();
375|       batch.set(doc, {
376|         ...coin,
377|         'roll_id':          rollId,
378|         'roll_type':        _rollType?.name ?? 'unknown',
379|         'added_at':         DateTime.now().toIso8601String(),
380|         'source':           'roll_wizard',
381|         // ITEM 6: stamp is_demo: false so real coins remain visible after display filter ships
382|         'is_demo':          false,
383|         'is_demo_cleared':  false,
384|       });
385|       count++;
386|       if (count % 400 == 0) {
387|         await batch.commit();
388|         batch = FirebaseFirestore.instance.batch();
389|       }
390|     }
391|     await batch.commit();
392| 
~~~~

## numista_mobile/lib/services/set_grouping_service.dart — Set grouping: email-folder coins


~~~~ numista_mobile/lib/services/set_grouping_service.dart:34-40
34|     
35|     final userEmail = AuthService.userEmail;
36|     
37|     final coinsRef = FirebaseFirestore.instance
38|         .collection('users').doc(userEmail).collection('coins');
39|     
40|     // Read all target coins and validate none are already in a set
~~~~

## numista_mobile/lib/services/beta_checklist_service.dart — Beta checklist: uid-folder coins, world_items


~~~~ numista_mobile/lib/services/beta_checklist_service.dart:350-370
350|       final doc = await docRef.get();
351|       final detected = <String>[];
352| 
353|       // 1. Manual entry check (limit 1)
354|       final manualCoinsSnap = await _firestore
355|           .collection('users').doc(uid).collection('coins')
356|           .where('source', isEqualTo: 'manual').limit(1).get();
357|       if (manualCoinsSnap.docs.isNotEmpty) detected.add('task_3_manual_entry');
358| 
359|       // 2. Currency check (limit 1)
360|       final currSnap = await _firestore
361|           .collection('users').doc(uid).collection('currency').limit(1).get();
362|       if (currSnap.docs.isNotEmpty) detected.add('task_12_currency');
363| 
364|       // 3. World items / foreign coins check (world_items OR is_foreign: true, limit 1 each)
365|       final worldSnap = await _firestore
366|           .collection('users').doc(uid).collection('world_items').limit(1).get();
367|       final foreignCoinSnap = await _firestore
368|           .collection('users').doc(uid).collection('coins')
369|           .where('is_foreign', isEqualTo: true).limit(1).get();
370|       if (worldSnap.docs.isNotEmpty || foreignCoinSnap.docs.isNotEmpty) {
~~~~

## numista_mobile/lib/screens/wishlist_screen.dart — Wishlist found: client SDK coin create (added_at)


~~~~ numista_mobile/lib/screens/wishlist_screen.dart:972-986
972|     );
973|     if (confirmed != true || !mounted) return;
974|     try {
975|       final coin = item.coin!;
976|       final email = AuthService.userEmail;
977|       await FirebaseFirestore.instance
978|         .collection('users').doc(email).collection('coins')
979|         .add({
980|           ...coin.toFirestore(),
981|           'Condition': condition,
982|           'source': 'wish_list_found',
983|           'added_at': DateTime.now().toIso8601String(),
984|         });
985|       await WishlistService.removeFromWishlist(item.id);
986|       if (!mounted) return;
~~~~

## numista_mobile/lib/models/coin_model.dart — CoinModel.toFirestore (no created_at/added_at)


~~~~ numista_mobile/lib/models/coin_model.dart:246-262
246|   }
247| 
248|   Map<String, dynamic> toFirestore() {
249|     return {
250|       'Year': year,
251|       'Mint Mark': mintMark,
252|       'Denomination': denomination,
253|       'Program/Series': programSeries,
254|       'Theme/Subject': themeSubject,
255|       'Variety': variety,
256|       'Condition': condition,
257|       'Strike Type': strikeType,
258|       'Holder Type': holderType,
259|       'Grading Service': gradingService,
260|       'Certification Number': certificationNumber,
261|       'Metal Content': metalContent,
262|       'Quantity': quantity,
~~~~

## numista_mobile/lib/screens/ai_chat_screen.dart — added_at inside owner_photos entry (not a coin field)


~~~~ numista_mobile/lib/screens/ai_chat_screen.dart:1645-1656
1645|                 .collection('users').doc(userEmail).collection('coins').doc(setId);
1646|             await docRef.update({
1647|               'owner_photos': [
1648|                 {
1649|                   'id': DateTime.now().millisecondsSinceEpoch.toRadixString(36),
1650|                   'url': photoUrl,
1651|                   'storage_path': gcsPath,
1652|                   'caption': setName,
1653|                   'added_at': DateTime.now().toIso8601String(),
1654|                 }
1655|               ],
1656|             });
~~~~

## numista_mobile/lib/screens/estate_planning_screen.dart — Reads users/{uid} doc with data() ?? {}


~~~~ numista_mobile/lib/screens/estate_planning_screen.dart:158-172
158|     if (_uid.isEmpty) {
159|       setState(() { _tierLoaded = true; });
160|       return;
161|     }
162|     _tierSub = FirebaseFirestore.instance
163|         .collection('users')
164|         .doc(_uid)
165|         .snapshots()
166|         .listen((snap) {
167|       if (!mounted) return;
168|       final data = snap.data() ?? {};
169|       final stripeTier = (data['stripe_tier'] as String?) ?? (data['tier'] as String?) ?? 'free';
170|       final isLife     = data['is_lifetime_family_estate'] == true;
171|       final isQc       = data['is_ai_qc_account'] == true;
172|       final isBeta     = data['beta_tester'] == true;
~~~~

## numista_mobile/lib/screens/my_collection_screen.dart — Reads users/{uid} doc (exists && containsKey)


~~~~ numista_mobile/lib/screens/my_collection_screen.dart:320-326
320|       }
321|       final user = FirebaseAuth.instance.currentUser;
322|       if (user != null) {
323|         final doc = await FirebaseFirestore.instance.collection('users').doc(user.uid).get();
324|         if (doc.exists && doc.data() != null) {
325|           final data = doc.data()!;
326|           if (data.containsKey('default_sort_field') && data.containsKey('default_sort_asc')) {
~~~~
<<<END ARTIFACT id=A3>>>

## A4 - GB CoS score record for v1.9 - 96/100 PASS (D1/D2 that v1.9.1 claims to close)

<<<BEGIN ARTIFACT id=A4 sha256=3b98bff555460ad4224781ea089524203105a8feb123cdc44df1ca536fae04f3 bytes=21352 lines=195 path=COS_SCORE_NET-827_FAILFIX-B1B5_v1.9_96_PASS_20261110.md>>>
# DESIGNATED CoS PLAN SCORE: NET-827 Stripe Checkout fail-fix B1–B5, plan v1.9 (writer: Code Writing)

**Score: 96 / 100, PASS.** The pass mark is 95. Only material defects count (correctness, safety, permissions, execution). Cosmetics are not deducted, and external prerequisites are not counted as plan defects.
Scored by GB CoS (designated CoS gate), 10 Nov 2026, about 7:45 PM ET (America/New_York).
**Count: NET-827 fail-fix track attempt 4 of 10; writer Code Writing try 1 of 4.** Both counts were checked against the plan header (line 3) before scoring.

## Plan scored
- `/workspace/net827-claude/src/PLAN_NET-827_FAILFIX-B1B5_STRIPE-CHECKOUT-PREVIEW_v1.9_CODE-WRITING_20261110.md`
- SHA-256 **`0434dfce1218a530842c1aa6f89707eedc90451ae4cb768beac8c226e3dfed70`**, 142,586 bytes, 1,493 lines. Re-hashed at the start and again at the end of scoring; both matched.
- Every line was read, and claims were checked against the code at `a3d7dca20fbbaf06a522205b22d0740b600de52b` (box clone `/workspace/net827-claude/repo`, clean worktree).

## What this was scored against
- All of Eric's binding decisions in the v1.6–v1.8 records:
  - tier limits and the 7 Nov price ladder;
  - the Christmas window;
  - Beta Special: $30, more than 100 coins, unlimited for 6 months, once ever, blocked at create with an auto-refund backstop, overflow locked and never deleted, a CSV always available, a lazy lock allowed;
  - refunds and disputes;
  - non-US buyers, USD only, Stripe Tax off;
  - the separate preview backend;
  - the synthetic testers;
  - unverified Stripe shapes accepted as long as they fail closed;
  - pytest via the venv.
- The v1.7 record (N1–N3) and the v1.8 record (R1–R5 and advisories 1–8).
- The Carbon v1.9 harvest (`653b3c8c…`): do-not-copy items X1–X12 and gaps G1–G9.
- The 11 CoS check points in the 7:37 PM ET task.
- Treated as **Eric's open decisions, not deductions:**
  - lock order (open question 13);
  - whether locked coins count toward the Beta Special 100-coin minimum (open question 16).

## The 11 check points

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | N1–N3 and R1–R5 truly closed | **Closed** | See the closure matrix below. |
| 2 | No harvest do-not-copy items | **None found** | See X1–X12 under the closure matrix. A grep of the plan for `49e77cf7`, `numista-vault`, `subscription_tier`, `999999`, `firestore:rules:get`, `python -c`, `mocha` and `users/{uid}/locked_coins` finds only line 126 (the R3 history row) and line 1492 (the self-audit). |
| 3 | No rules change; `locked_coins/{owner_key}/coins/{coin_id}` is denied to the owner | **Confirmed** | `numista_mobile/firestore.rules` (SHA `e650713b…`, the file `numista_mobile/firebase.json:2-5` deploys) has exactly one `match /{` block: `:346` `match /{document=**} { allow read, write: if false; }`. Every other match is under `/users/{email}/…` or another named collection. None of them matches a top-level `locked_coins`, `entitlements`, `stripe_customers` or `stripe_payments` path, so only the deny-all applies to the owner (and to everyone else). `numista_backend/firestore.rules` (`d087e8ae…`) has the same deny-all at `:244` and is not deployed (`numista_backend/firebase.json` covers functions only). |
| 4 | Optional RX step | **Mostly correct; one material gap (D2)** | Additive only: every hunk adds a condition, an exclusion or an explicit deny, and the hunk line numbers are exact (`:55-58`, `:63-66`, `:85-88`, `:110`, `:115`, `:345`). The user-doc update rule uses `diff().affectedKeys()` (`_noEntitlementChange`, `:89-91`), so adding keys to `_serverOnlyKeys` cannot block normal profile updates. Real command: `firebase deploy --only firestore:rules --project studio-9101802118-8c9a8`. REST backup with a SHA compare; a runnable rollback; its own scoped Eric YES naming HOLD `41b8bd5f`; never bundled. **Gap:** the deploy block does not itself confirm the live-rules SHA (D2). |
| 5 | Lock/unlock | **Correct** | Union of the email and uid folders, deduped by doc id. Coins only. At most 200 copies per transaction (400 writes, under 500). Each copy is restored to its exact `source_path`; restore conflicts are never overwritten. Errors raise. Legacy flags are cleared in chunks of at most 400. |
| 6 | Tier limits exactly as in v1.7; unlimited is null | **Correct** | §4.5: free 10, pro 100, numismatist 249, dealer 500, estate None, family_estate 2500, sovereign None, power_user None. `/subscription-status` returns `coin_limit: null` plus `unlimited: true`. The same values appear in §0, §4.5 and §7.1. |
| 7 | No human sign-ins on p7-gate | **Correct** | §0 and §6.3: nobody signs in on p7-gate, including Eric, beta testers and the synthetic testers. §8 is a scripted HTTP client. The only signed-in smoke test is Eric's optional check on production after RX, not on p7-gate. |
| 8 | All Eric decisions hold | **Yes** | See the closure matrix. |
| 9 | Scripts run on PowerShell 5.1 | **Yes** | Every native call uses `Invoke-Native` or `Invoke-NativeCapture` with a `$LASTEXITCODE` check. Python runs from a temp file, never `-c`; the UTF-8 BOM that `Set-Content` writes is accepted by Python. The rules backup is written with UTF-8 without a BOM, and there is no `>` redirection. Placeholder guards are in place. Worktrees sit outside the repo. `c547b7a0` is refused, and so is `numista-backend`. |
| 10 | At least 30 of 152 citations spot-checked | **About 90 checked, 0 wrong** | See the citation spot-check below. |
| 11 | Size adds no contradictions | **No material contradiction** | Tier limits, Christmas epochs, the route, the locked path, the test file names and the Beta counting rule are consistent across sections. One false factual claim about client creates is recorded as advisory 1 (it falls under the lock-order open decision). |

## Citation spot-check (about 90 of 152, all at `a3d7dca2`)

All of the following were printed from the repo and matched the plan's claim.
- **`routes/payment_routes.py`:** `:15` (imports `db` from `routes.deps`), `:26`, `:32`, `:46-75`, `:82`, `:102-105`, `:130`, `:149`, `:158`, `:166`, `:172-189`, `:196-202`, `:199`, `:210`, `:221`, `:227-238`.
- **`tier_gatekeeper.py`:**
  - `:13-29`, `:41-50`, `:67-110`, `:132-157`, `:146-149`;
  - `:160-168` (returns 0 on error);
  - `:238`;
  - `:325-337` (single batch; `order_by created_at`; newest locked);
  - `:340-351`.
- **`main.py`:**
  - `:54`, `:293-294`, `:335`, `:342`, `:345-349`, `:352`, `:357-358`;
  - `:2910`, `:2938`, `:3022`, `:3081`, `:3334-3341`;
  - `:4149`, `:4357`, `:4407`, `:4430`;
  - `:8722`, `:8738`, `:8986`;
  - `:9606-9607`;
  - `:10192`, `:10457-10463`, `:10609`, `:10623`;
  - `:12098`, `:12279-12283`.
- **`routes/deps.py`:** `:21`, `:24`, `:25`, `:40-48`, `:52-67`, `:69-79`.
- **`routes/import_routes.py`:** `:17`, `:21`, `:53`, `:96`, `:118`, `:242`.
- **Other backend routes:**
  - `scan_routes.py:312`, `attorney_routes.py:251`;
  - `support_routes.py:35-39` (a Firestore client);
  - `subaccount_routes.py:23-27`;
  - `estate_routes.py:20`, `:42`;
  - `feedback_callable_route.py:36-37`, `:494`.
- **Backend config, scraper and services:**
  - `stripe_config.py:29-30`, `:78-86`; `schemas/payment_schemas.py:8-10`;
  - `Dockerfile:24`; `.dockerignore:20`; `.gitignore:35`; `requirements.txt:48` (`google-cloud-firestore==2.26.0`);
  - `brain_processor.py:51`; `services/canon_sync_service.py:10-11`, `:21-26`; `services/transfer_service.py:60-84`, `:383`;
  - `numista_scraper/scrapers.py:146`, `:705`, `:731`; `numista_scraper/config.py:12`, `:117-124`, `:186-193`; `numista_scraper/storage.py:15-16`, `:22-38`.
- **`numista_mobile`:**
  - `firestore.rules:13-15`, `:40`, `:55-58`, `:63-66`, `:69-73`, `:85-88`, `:96-104`, `:110`, `:115`, `:345-348`;
  - `firebase.json:2-5`; `.firebaserc` default (production);
  - `firestore.rules.test.js:33-40`; the `package.json` test script;
  - `lib/screens/base_layout.dart:110-114`, `:196-197` (`initState`);
  - `lib/services/set_grouping_service.dart:38`; `lib/services/beta_checklist_service.dart:355`, `:366`;
  - `lib/constants.dart:13-16`; `lib/firebase_options.dart:50`, `:55`, `:64`, `:73`;
  - `tests/test_idor_fixes.py:478-482` (`?uid=` assertion).
- **Plan statements confirmed by grep:**
  - no app code reads `locked_pending_upgrade`, `power_user`, `creation_timestamp`, `stripe_customer_id` or `beta_special`;
  - the app never calls `/subscription-status`;
  - `check_and_enforce_coin_limit` has no runtime caller;
  - Cloud Functions have no coin triggers (`functions/index.js` has only `onFeedbackCreated`), so moving a coin fires no side effect.

## Closure matrix

**v1.7 record**

| Item | Status | Evidence |
|---|---|---|
| N1 Preview reaches production | **Closed** | 22-row inventory (§4.11), each row verified. Covers every client from the v1.8 R4 list plus `numista_scraper/config.py`. `env_guard` gives a guarded Firestore client, a guarded storage wrapper with `bucket_for`, and an Admin app used for Auth only. `firebase_admin.firestore.client()` is forbidden. Import-graph test (§7.3). PV-4 checks IAM at both the project and bucket level. |
| N2 Preview app writes production | **Closed** | Nobody signs in on p7-gate; testing uses the scripted client. |
| N3 "Locked in the app" | **Closed** | Locked coins are physically moved to the rules-denied top-level `locked_coins`, so every existing client query simply doesn't see them, with no rules change and no lock-out. By-id routes return 403 `LOCKED_PENDING_UPGRADE`. |

**v1.8 record**

| Item | Status | Evidence |
|---|---|---|
| R1 Rules lock-out | **Closed** | No rules change. Emulator test 1 (an unfiltered owner list succeeds) is the regression test. |
| R2 Double counting | **Closed** | Union by id; 200 duplicates count as 200 (test). Currency and wishlist are never counted or locked. |
| R3 Invented bucket | **Closed** | The real buckets are used (`main.py:342`, etc.). The preview bucket is required and must not be a production bucket. PV-1, PV-3 and PV-4 cover it, with tests. |
| R4 Unscoped modules | **Closed** | 22 rows, with the module-set assertion in the import-graph test. |
| R5 Tests dropped | **Closed** | §7.1 lock, CSV and export tests restored, including an unauthenticated CSV request getting 401 and a cross-user check. |

**v1.8 advisories 1–8:** closed.
- 1: p7-gate users (§6.3).
- 2: PV-4.5 checks uid and email; prints paths only; a YES-gated delete limited to the four accounts.
- 3: bucket IAM is checked; folder and org grants are noted as unchecked.
- 4: passwords are typed at run time.
- 5: `get_user_tier` is unchanged and takes one argument.
- 6: closed.
- 7: cosmetic.
- 8: `-Action` parameter.

**Harvest X1–X12:** none present.
- X1/X2: no full rules file and no `users/{uid}/locked_coins`.
- X3: limits and `get_user_tier` intact.
- X4: chunked writes, restore to the origin folder, today's lock order.
- X5: v1.7 `env_guard` with `rk_live_`, the production project check, and GL-1 instead of a live default.
- X6: REST backup, `Invoke-Native`, a runnable rollback, the hold named.
- X7/X8: temp-file pattern, `projectId`, `numista_backend\.venv`, pattern guard, gone-check.
- X9: venv plus BLOCKED.
- X10: no `49e77cf7`.
- X11: header is v1.9.
- X12: Jest.

**Eric's binding decisions**

| Decision | Status |
|---|---|
| B1–B5 and D1–D8 payment logic (allowlist, `price_data`, lease, one discount, subtotal/coupon/1-cent check, ledger refunds, revoke on a lost dispute only) | Unchanged from v1.7 |
| Prices 499/4999, 899/8999, 1099/10900, 1599/15000 | Correct (§4.1) |
| Christmas `1795669260`–`1798261199`, server-side, annual only, never early, no stacking | Correct (§4.1, §5). v1.9 also makes the webhook fail closed when the session `created` time is missing. |
| Beta Special | Correct: $30; more than 100 coins (counted with deduping); blocked at create; auto-refund backstop; 6 months as a Timestamp; `beta_special_purchased` permanent and server-only |
| Partial refund logged only; full refund or lost dispute revokes; a dispute opening does not | Correct (§4.4) |
| Expiry: overflow locked, never deleted; CSV always available; lazy lock with server checks | Correct. Lazy reconcile runs on every add path, by-id route, count and status call, plus the app-start `refreshEntitlement`. |
| Non-US buyers, USD, Tax off, billing address `auto` | Correct |
| Preview isolation; synthetic testers; unverified shapes accepted (fail closed); pytest via venv | Correct |
| Holds `74611e05` and `41b8bd5f`; main `9f04550a`; live payments off; no secrets or invented IDs | Correct. HOLD is named in the YES wording (§9.2) and in RX (§9.4). |

## Deductions (material only)

| # | Pts | Area | Evidence | Why it matters | Exact fix |
|---|---|---|---|---|---|
| D1 | −2 | **Correctness / execution: a paid grant needs a `users/{uid}` doc that nothing guarantees** | Plan §4.3 line 358: "If no `users/{uid}` doc exists: log, set `retry`, return 500 (never `done`)." Code: the only app write to `users/{uid}` as a document is the sort preference (`numista_mobile/lib/screens/my_collection_screen.dart:359`); the rules note says profile flags live on `users/{email}` (`firestore.rules:69-73`); subcollection writes under `users/{uid}/…` do not create the parent doc. Today's webhook creates the doc with `set(..., merge=True)` (`payment_routes.py:210-238`). In the preview, PV-5b seeds only `users/{uid}/coins` and nothing creates `users/{uid}` for ft-preview-01..04. | A customer whose account has only a `users/{email}` doc pays and is **never granted**. The event retries until Stripe gives up: money is taken, there is no access, and no refund. The §8 gated runs (ft-preview-02 Silver, ft-preview-03 Beta, ft-preview-04 F&F) would also fail to grant in the test Firestore. It fails closed (no wrongful grant), so −2. | The uid is trustworthy: it comes from the server-set `client_reference_id`, taken from the verified token at create. Either (a) at checkout create, in the same transaction as `checkout_pending`, `set(users/{uid}, {}, merge=True)` with no entitlement keys; or (b) in the grant transaction, create `users/{uid}` with `merge=True` when it is missing but `entitlements/{uid}.checkout_pending.session_id` matches the session (or `firebase_auth.get_user(uid)` succeeds). Add pytest: a user with only `users/{email}` buys Silver and is granted; a uid with no account is not. |
| D2 | −2 | **Safety (production rules change): the RX deploy gate does not confirm the live SHA, and the post-deploy step can destroy the backup** | §9.4 lines 1389–1395: the backup block **writes** the live ruleset to `%TEMP%\net827_rules_backup\firestore.rules` (line 1392) **before** it compares the SHA (line 1395). The deploy block's only precondition is `Test-Path` on that file (line 1414). Line 1431: "re-run the backup block's REST read into a second folder", but the backup block hard-codes the folder and `$Expected = e650713b…`, so a literal re-run after RX overwrites the backup with the RX bytes and throws. Rollback (line 1446) then refuses because the backup SHA no longer matches, and the fallback (line 1452, the file at `a3d7dca2`) is not scripted. | If the live rules differ from `e650713b…` (for example, deployed from a CRLF checkout or edited in the console), the backup throws, but the file it left behind satisfies the deploy gate, so RX can be deployed over an unknown live ruleset. Rollback then refuses to restore it. A stale backup from an earlier run also passes the gate. This is the exact "confirm the live-rules SHA before deploy" requirement. RX is optional and separately gated, so −2. | In the deploy block, immediately before `firebase deploy`: re-read the live ruleset over REST, require its SHA to equal `e650713b…`, and require the backup file's SHA to equal it as well; otherwise throw. In the backup block, write to a temp name and rename only after the SHA matches, or delete the file on mismatch. Give a separate scripted post-deploy verify (its own folder and expected SHA = `$rxFile`) that never touches the backup folder. Script the rollback fallback: `git show a3d7dca2:numista_mobile/firestore.rules`, written without a BOM and SHA-checked, then deployed. |

**Total: 100 − 4 = 96, PASS.**

## Advisories (not scored)
1. **Lock order for client-created coins (falls under Eric's open decision 13; the plan's claim is wrong against the code).**
   - The plan's claim: §4.8 line 515 says reconcile locks "the newest, i.e. the ones just added", and §7.1 line 1134 tests "11 coins on Free after a direct client create → moves the newest 1".
   - The code: the real client create path, the roll wizard (`numista_mobile/lib/widgets/roll_entry_dialog.dart:374-384`), writes `added_at` (an ISO string) and **no `created_at`**.
   - The effect: under §4.8 line 444, a missing `created_at` counts as epoch 0, the oldest. So client-added coins stay visible and the user's older, server-added coins (`created_at` = `SERVER_TIMESTAMP`, e.g. `main.py:2747`) get locked instead. Nothing is deleted and the visible count is still enforced; only *which* coins lock changes.
   - Suggested fix: sort on `created_at`, then `added_at`, then epoch 0, and use a roll-wizard-shaped fixture in the test. Present this to Eric along with open question 13.
2. **Client-writable `power_user` and `creation_timestamp` (open risks 14 and 15, pre-existing).**
   - `effective_limit` now applies the `power_user` bypass on every coin-limit and lock path; until now that bypass sat on the unused `check_and_enforce_coin_limit`.
   - Any user can set either field on their own user doc today and get unlimited coins or `family_estate` (2,500 coins), and so avoid the Beta-expiry lock and the paid ladder.
   - The plan discloses this and closes it only through the optional RX, as the CoS directed. Recommendation: Eric decides before go-live whether RX (or at least the `power_user`/`creation_timestamp` part) becomes a precondition of GL/LK.
3. **Cost and latency.** `enforce_entitlement` runs before every add path and every by-id coin route, and needs the ids of both coin folders. For large collections, specify id-only reads (a `select([])` projection) for the count, and stream full docs only when a lock is actually needed.
4. **Transaction size.** 200 full coin documents per transaction can exceed Firestore's 10 MiB request limit if coin docs are large. A raised error would then return 503 on that user's add and by-id paths on every request. Also cap each chunk by bytes (for example ≤ 4 MiB of `data`) and test a large-doc case.
5. **`/subscription-status` admin path.** Today an admin token may pass any `uid` (`payment_routes.py:141-143`). Reconcile uses only the caller's own token keys (§4.8). State what the endpoint returns, and whose coins it reconciles, when an admin queries another uid.
6. **PV-4 JSON parse.** `Invoke-NativeCapture` merges stderr into the JSON (`2>&1`), so a gcloud warning on stderr makes `ConvertFrom-Json` throw. That fails closed; capture stdout only for the JSON.
7. **RX CRLF.** If Eric's checkout uses CRLF line endings, the SHAs of both the RX file and the live ruleset may differ from the LF-based `e650713b…`. The checks fail closed, but record which line ending the YES SHA refers to.

## Writer assessment (Code Writing, try 1)
- **Good:**
  - The strongest NET-827 plan so far.
  - The design avoids a rules change completely: physically moving coins to a top-level, deny-all collection is the right answer to the v1.8 "rules are not filters" lock-out.
  - Every v1.7 and v1.8 item is closed with verifiable citations, and roughly 90 checked citations were all accurate.
  - The harvest was used correctly: the good parts were kept and every do-not-copy item was left out.
  - The writer found real pre-existing gaps (client-writable `power_user`/`creation_timestamp`, the billing portal trusting a client-writable customer id, `get_coin_count` failing open, the untrusted `stripe_customer_id`) and handled each honestly.
- **Weak:**
  - The RX gate relies on operator discipline rather than enforcing the SHA in the deploy step.
  - The grant precondition (`users/{uid}` must exist) was carried forward without checking how user docs are actually created.

## Next step
- **PASS at the CoS gate.** Next is a full-plan SAG review on the exact same file SHA, `0434dfce…`.
- A SAG packet has been built locally and **not submitted**. Path, size and SHA are reported to CoS separately.
- D1 and D2 should be fixed in the build or a v1.9.1 (the fixes are small and specified above). Changing the plan file changes its SHA, and SAG must review the exact file.
- Eric's open decisions (unchanged, not deductions):
  - Q13: lock order (see advisory 1);
  - Q16: whether locked coins count toward the Beta 100-coin minimum;
  - Q3: legacy `estate` users;
  - whether RX becomes a go-live precondition (advisory 2).
- Nothing was filed to Desk and no agent was messaged.

## Authority statement
This score **grants no code, git, deploy, Firestore, Firestore rules, Firebase Auth, Storage, Stripe, Secret Manager or go-live authority**. HOLDs `74611e05…` and `41b8bd5f…` and the go-live addendum `c2b6ac93…` (NOT ACTIVE) stay in force. main stays `9f04550a` and Stripe live stays OFF. RX additionally needs its own scoped Eric YES naming HOLD `41b8bd5f`.
<<<END ARTIFACT id=A4>>>

## A5 - GB CoS score record for v1.8 - 85/100 REVISE (regression reference: R1-R5)

<<<BEGIN ARTIFACT id=A5 sha256=cbf4fb6cd0f8c657825d033b31c08fabc5ff7638e68a4cd604ae025e3505ec02 bytes=18288 lines=117 path=COS_SCORE_NET-827_FAILFIX-B1B5_v1.8_85_REVISE_20261110.md>>>
# DESIGNATED CoS PLAN SCORE: NET-827 Stripe Checkout fail-fix B1–B5, plan v1.8 (writer: AG Gemini 4 Carbon)

**Score: 85 / 100, REVISE.** The pass mark is 95. Only material defects count (correctness, safety, permissions, execution). Cosmetics are not deducted, and external prerequisites are not counted as plan defects.
Scored by GB CoS (designated CoS gate), 10 Nov 2026, about 7:15 PM ET (America/New_York).
**Count: NET-827 fail-fix track attempt 3 of 10; writer AG Carbon try 1 of 4.** Carbon has tries 2–4 left.

## Plan scored
- `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\Carbon\PLAN_NET-827_FAILFIX-B1B5_STRIPE-CHECKOUT-PREVIEW_v1.8_AG-CARBON_20261110.md`
- SHA-256 **`bcc3f2d33b4799f2d4f8d4b17e0cac226bdc223184248d3e75de6e9c452a2e38`**, 65,130 bytes, 834 lines. Copied to the box (`/workspace/net827-claude/src/`). Size and hash match the Desk report.
- Every line read. It was also diffed against v1.7 (19 hunks) to confirm what changed.

## What this was scored against
- All of Eric's binding decisions in the v1.6 and v1.7 records, including the 5:36 PM ET decisions:
  - Gold 501+ unlimited; Platinum 250–500.
  - Overflow coins locked in the app, never deleted.
  - Basic CSV of all coins always available.
  - Every add/view/edit path checks expiry server-side.
  - Synthetic `ft-preview-0N@numista.ai` testers: production Auth only, no production Firestore data, cleanup after Field Tester.
  - Unverified Stripe shapes and rounding accepted, failing closed.
- N1–N3 and advisories A1–A6 from the v1.7 record (86, REVISE). The task named "two advisories"; all six were checked.
- **Code checked read-only at `a3d7dca20fbbaf06a522205b22d0740b600de52b`:**
  - Every Firestore/GCS/Firebase Admin client reachable from `main.py`, found by walking its imports (module-level and lazy).
  - `main.py:340-358, 4149, 4430, 9606`; `routes/deps.py`, `routes/estate_routes.py`, `routes/support_routes.py`, `routes/subaccount_routes.py`.
  - `brain_processor.py`, `services/canon_sync_service.py`, `numista_scraper/{storage,scrapers,config}.py`.
  - `tier_gatekeeper.py` (migration, `lock_overflow_coins`, `unlock_user_coins`).
  - `numista_mobile/firestore.rules`, `numista_mobile/firebase.json`, and client coin queries and writes under `numista_mobile/lib/`.

## N1–N3 and advisory closure (from v1.7)

| ID | v1.7 item | v1.8 status | Evidence |
|---|---|---|---|
| N1 | Preview backend still reaches production (`main.py`, `subaccount_routes`) | **Partly closed.** New defects R3 and R4 | The four clients named in v1.7 are now guarded (`main.py:349/352`, `subaccount_routes.py:26`, `export_routes` via `deps.get_db()`). `main.py` coin routes are in scope. PV-4 now has a real IAM check that the preview SA holds zero roles on `studio-9101802118-8c9a8`, so production access fails closed at the IAM layer. But: the "entire backend" claim is false (R4), and the new bucket guard uses an invented production bucket name (R3). |
| N2 | Preview app writes production Firestore directly | **Closed for the synthetic testers** | Option (b) is adopted: `ft-preview-01..04` must never sign in on p7-gate. All checkout tests go through a scripted client against the preview backend with an ID token (§8 lines 735–745). PV-4.5 is a read-only production check before use and cleanup. **FT still works:** §7 (venv pytest, unauthenticated/unsigned-webhook probes, `flutter analyze`) never needed an app sign-in, and §8 scripted runs cover the checkout path. **Eric's test-user decision still holds:** production Auth for verification only, no production Firestore data, listed, PV-6 cleanup after FT, passwords typed at run time. See advisory 1 on other humans using p7-gate. |
| N3 | "Locked in the app" not deliverable; email-keyed coins missed | **Not closed.** New defects R1, R2, R5 | The plan now adds Firestore rules, client filtering and dual-path coverage. But the rules as specified lock every user out of their collection (R1), dual-path counting double-counts migrated users (R2), and the §4.8 test list was dropped (R5). |
| A1 | Ledger key when no PI at grant | **Closed** | §4.3 line 297 skips the write when `payment_intent` is None and relies on `invoice.paid`. |
| A2 | `lock_overflow_coins` skips no-`created_at` coins, fails open | **Closed** | §4.8 line 367: missing timestamp = epoch 0; raise on error. |
| A3 | `decide_grant` lacks `created` window | **Closed** | `session_created` window check (lines 268–287). |
| A4 | `beta_special_until` type | **Closed** | `parse_until_ts` handles number, ISO string and Timestamp; parse failure = 0.0 = expired, which fails closed. |
| A5 | CSV prefix for tab/CR | **Closed** (§4.8 line 425). Line 69 of the change list has a literal line break inside the backticks; cosmetic. |
| A6/A7 | Attempt count / PV-6 hand edit | Count fixed. PV-6 still uses a one-line hand edit (advisory, unchanged). |

## Previously-closed items: still closed (verified against the diff)
- B1–B5, D1–D8 logic unchanged except the A1/A3 edits above:
  - allowlist and price table;
  - customer map and no default tier;
  - 60 s lease;
  - one discount model with F&F promotion code and 500 cap;
  - subtotal + coupon + 1-cent check;
  - ledger-mapped refunds;
  - revoke only on a lost dispute.
- Free 10, Silver 249, Platinum 500, Gold 501+ unlimited, JSON-safe incl. `power_user`.
- Christmas `1795669260` (26 Nov 2026 12:01 AM ET) to `1798261199` (25 Dec 2026 11:59:59 PM ET), server gate at create and webhook, annual only, no stacking.
- Beta Special: $30, 101+, block at create plus auto-refund backstop, 6 months, once ever.
- Partial refund log only. Non-US / billing auto / USD / Tax off.
- K1 LK-1…LK-8 not run. Holds, `c547b7a0` refusal, main pinned, live off, no secrets or invented Stripe IDs.
- PS 5.1 shape and isolated worktrees. pytest via venv, BLOCKED on failure.
- PV-5 synthetic tester script unchanged and still well guarded.

## New deductions on v1.8 (each one is material)

| # | Pts | Area | Evidence | Why it matters | Exact fix |
|---|---|---|---|---|---|
| R1 | −6 | **Safety: the Firestore rules change locks users out of production** (high-risk area) | §4.8 lines 410–421, §3 line 131: `isNotLocked()` = `!('locked_pending_upgrade' in resource.data) \|\| resource.data.locked_pending_upgrade != true`, applied to client `read`. Code: the app lists coins with unfiltered queries, e.g. `base_layout.dart:110-114` `.collection('users').doc(email).collection('coins').get()` and `set_grouping_service.dart:38,107,188` (25 coin-collection call sites). Existing coin docs have no `locked_pending_upgrade` field. `numista_mobile/firebase.json` deploys `firestore.rules` to `studio-9101802118-8c9a8`. | **Firestore rules are not filters.** A list query is rejected outright unless the query itself guarantees the rule. No unfiltered query can prove `locked_pending_upgrade != true`, and a `where(... != true)` filter drops every doc that lacks the field (all existing coins). Deployed as written, **every user's collection list fails** with permission denied, including on the live numista.ai app. That app runs main `9f04550a`, which can't be updated (HOLD `41b8bd5f`). A rules deploy to the production project is a live production change, but the plan doesn't name it against the hold. Also missing: rules text for `create` (left as "fails closed … **or** defer create through the backend"; rules can't count documents); emulator tests (`firestore.rules.test.js` exists and is not used); a deploy command and the rollback it says is "documented"; and the client query/badge changes are not in the §3 file list (the stop rule then blocks the builder). | Don't gate client **list** reads on a per-document field without a migration. Either (a) keep the rules read-permissive for now and enforce "not viewable" by moving locked coins' data out of the client-readable doc (e.g. backend moves locked coins to a rules-denied `users/{id}/locked_coins` subcollection, restored on upgrade, never deleted, included in the CSV); or (b) a YES-gated Admin-SDK backfill of `locked_pending_upgrade: false` on every coin, then all client queries add `where('locked_pending_upgrade', '==', false)`, **then** the rules change, deployed only after the updated app is live. In both cases: protect `locked_pending_upgrade` from client writes (add it to the `affectedKeys` deny list and to create); state the create-limit design concretely; add rules emulator tests (owner list works with zero locked coins, a locked get is denied, a non-owner is denied, existing creates/updates incl. upload-driven `update`s still pass); give the PS 5.1 `firebase deploy --only firestore:rules` block with a pre-deploy copy of the current rules and a rollback block; and record that it is a production change needing the hold lifted or Eric's explicit scoped YES that names the hold. |
| R2 | −3 | Correctness: dual-path coin counting double-counts migrated users | §4.8 line 368, line 408, line 424: lock, unlock and CSV "query and process both `users/{uid}/coins` AND legacy `users/{email}/coins`, as well as … `currency`, `wishlist`". Code: `migrate_legacy_collection_chunked` (`tier_gatekeeper.py:67-110`) **copies** email-path docs to the uid path (same doc ids) and never deletes the originals. | For every migrated user, each coin exists twice. A combined count doubles their total: a Silver user with 200 coins counts as 400 and **151 paid-for coins get locked**. The CSV lists every coin twice. Folding `currency` and `wishlist` into the coin lock is not Eric's decision (he said coins over the plan limit). Wishlist items are not owned coins, so this wrongly locks them. | Use one source per user: the uid path if `users/{uid}.migration_status == "completed"`, else the email path. Or de-duplicate by doc id before counting, locking or exporting. Lock coins only. Currency/wishlist go in the CSV but are never locked or counted. Add pytest: a migrated user with the same 200 coins in both paths counts as 200 and locks nothing on Silver; the CSV has 200 rows. |
| R3 | −3 | Correctness / safety: invented production bucket in the new guard | §6 lines 500–508: `resolve_user_content_bucket` defaults production to `"numista-vault-user-content"` and blocks only that name in preview. Code: `main.py:342` `USER_CONTENT_BUCKET = "numista-uploads-studio-9101802118-8c9a8"` (used at `main.py:4149`, `6900`). `numista-vault-user-content` appears nowhere in the repo. PV-3 `$envVars` doesn't set `USER_CONTENT_BUCKET`. | (1) When this code reaches production, **user uploads and imports go to a bucket that doesn't exist** (or isn't the real one). That's an upload regression. (2) The preview guard doesn't block the real production bucket, so a preview set to `numista-uploads-studio-…` would pass the guard. (3) PV-3 deploys without `USER_CONTENT_BUCKET`, so the preview refuses to start. That fails closed, but the step can't succeed as written. | Use the real name: production default `numista-uploads-studio-9101802118-8c9a8`; preview must set a different bucket and must not equal that name. Add `USER_CONTENT_BUCKET=<PREVIEW_BUCKET_UNKNOWN>` with a placeholder guard to PV-3, a PV-1 step to create the preview bucket in the test project, and a PV-4 check. Pytest the default and the preview refusal. |
| R4 | −2 | Execution / accuracy: "all clients across the entire backend" is not true | §1c line 49 and §2 N1 ("all 4 client inits"); §6 line 445 still says only `deps.py`/`tier_gatekeeper.py`. Runtime-reachable clients not in scope: `brain_processor.py:51,311` (`firestore.Client(project=PROD)`; imported by `main.py:10609`); `services/canon_sync_service.py:24-25` (prod Firestore + GCS; `main.py:10623`); `numista_scraper/storage.py:29-38` and `scrapers.py:146,705,731` (`firebase_admin` default-app `firestore.client()`, which in preview is initialised on the **production** Auth project); `routes/deps.py:25` `storage_client` (prod project); `main.py:358` default `initialize_app()`; unscoped `gcs.Client()` at `main.py:4430,9606`, `routes/estate_routes.py:42`; `routes/support_routes.py:38`. | Thanks to the new PV-4 IAM check these fail closed (permission denied) rather than write production, so this is −2, not more. But the in-process guard doesn't cover them. The "file outside this list → stop" rule means a builder who finds them must stop. Any default-app `firebase_admin.firestore.client()` in preview targets production by design of `FIREBASE_AUTH_PROJECT_ID`. | List these modules in §3 and route each through `env_guard` (or `deps.get_db()` / `get_gcs_client()`). Initialise the Firebase Admin default app for Auth only, and forbid `firebase_admin.firestore.client()` in runtime code. Add a pytest or grep check that fails if any runtime module constructs a Firestore/GCS client outside `env_guard`. |
| R5 | −1 | Test coverage regression (CSV ownership) | v1.7 §4.8 pytest bullet (expired Beta 300 coins: add 403, locked view 403, CSV has all 300; upgrade unlocks; injection prefix; unauthenticated CSV rejected) was **removed** in v1.8 (diff hunk 351–354 → 407–426), and §7 doesn't list §4.8 cases. | The CSV-leak check you asked for (auth/ownership) and the lock behaviour lose their named tests. The ownership logic is still correct as written (uid and token email, never the request). | Restore the v1.7 list and add: a user A token can't export user B's coins (incl. B's email path); a migrated-user dedupe case (R2); and rules emulator cases (R1). |

**Total: 100 − 15 = 85, REVISE.**

## Closure matrix (v1.8)

| Item | Status |
|---|---|
| B1–B5, D1–D8 | Closed (unchanged) |
| Free 10 / Silver 249 / Platinum 500 / Gold 501+ unlimited, JSON-safe | Closed |
| Prices per 7 Nov ladder | Closed |
| Christmas window, server-side, never early, annual-only, no stacking | Closed (A3 strengthens) |
| Beta 101+, block + backstop, 6 months, once ever | Closed |
| Partial refund log only; full refund / lost dispute revoke | Closed |
| Non-US, billing auto, USD, Tax off | Closed (foreign tax/legal = open risk) |
| Overflow locked, never deleted, upgrade unlocks (server) | Closed in logic; **counting wrong for migrated users (R2)** |
| Locked coins not viewable/editable **in the app** | **Open (R1)**: the rules as written cause a lock-out |
| Every add/view/edit path checks expiry | Server routes closed; client create path undecided (R1) |
| CSV of all coins incl. locked, any tier | Partly: both paths covered; **duplicates (R2)** |
| CSV can't leak another user's coins | Closed in logic (uid and token email only); **test dropped (R5)** |
| CSV within preview isolation | Closed (guarded `deps.get_db()`) |
| Preview backend never touches production | **Partly**: named clients guarded, IAM check added; R3 bucket, R4 unscoped modules |
| Preview app never writes production Firestore (synthetic testers) | Closed (no tester sign-in; scripted tests; PV-4.5) |
| Synthetic testers: named, listed, no production data, cleanup after FT, no stored passwords | Closed |
| FT/test plan still works without p7-gate tester sign-in | Closed |
| Stripe shapes / rounding accepted, fail closed | Closed |
| Live keys via named later step, no secrets | Closed |
| pytest via venv, BLOCKED if unavailable | Closed |
| Holds, `c547b7a0`, main pinned, live off, Eric's scoped YES | Closed for code/hosting; **the rules deploy is an unacknowledged production change (R1)** |

## Advisories (not scored)
1. **Other people on p7-gate.** The p7-gate build still points `API_BASE_URL` at the preview backend while its Firebase client stays on production. Any real person who signs in there (Eric or beta testers) gets mixed results: client reads/writes go to production, API calls go to the test project, and their backend-side data lands in the test project. State who may sign in on p7-gate during NET-827 (suggest: nobody signs in; or deploy hosting without the override and test the API by script only).
2. **PV-4.5** says it checks "synthetic UIDs and emails" but queries only `users/{email}` (UIDs are known after PV-5). It also says stray documents are deleted, but gives no delete script. Add UID checks and a guarded, YES-gated delete limited to the four accounts.
3. **PV-4 IAM check** sees only project-level bindings. Bucket-level or folder/org grants aren't covered; note this, or add `gcloud storage buckets get-iam-policy` for the production buckets.
4. The §8 scripted client needs the tester password to get an ID token. State that it is typed at run time (`getpass`/`Read-Host -AsSecureString`) and never stored, matching PV-5.
5. `effective_limit` calls `get_tier_fn(user_doc, now_ts)`, but today's `get_user_tier(user_profile)` takes one argument. State the new signature.
6. Open question 4 ("in-app upgrade button for testers") conflicts with the §8 sign-in prohibition. Close it.
7. The §1 heading still says "v1.6 → v1.7", and 1c sits before 1b. Cosmetic.
8. PV-6 still relies on hand-editing one line. Use an `-Action` parameter.

## Writer assessment (AG Carbon, try 1)
- **Good:** took every v1.7 item seriously. N2 is cleanly closed, with a workable scripted test path. A1–A6 are closed. The IAM layer is now verified. Nothing previously closed regressed in the payment logic.
- **Weak:** the new code paths weren't checked against the code. The rules design would lock users out of production, the migration copy creates duplicates, the production bucket name is invented, and the "entire backend" claim wasn't verified. One previously-present test list was dropped.

## Next step
- **REVISE.** Carbon try 2 of 4 (track attempt 4 of 10), using this record. Close R1–R5, keep everything else unchanged.
- R1 is the priority. A Firestore rules change must not ship in a form that can lock out existing users. It needs emulator tests, a migration/sequence, and an explicit production-change gate.
- **No SAG packet is built,** and nothing is filed to Desk routes.

## Authority statement
This score **grants no code, git, deploy, Firestore, Firestore rules, Firebase Auth, Storage, Stripe, Secret Manager or go-live authority**. HOLDs `74611e05…` and `41b8bd5f…` and the go-live addendum `c2b6ac93…` (NOT ACTIVE) stay in force. main stays `9f04550a`, and Stripe live stays OFF.
<<<END ARTIFACT id=A5>>>

## A6 - GB CoS score record for v1.7 - 86/100 REVISE (regression reference: N1-N3, Eric decisions)

<<<BEGIN ARTIFACT id=A6 sha256=e824859910136284854c688cb2e2033b75f8bc0e8755f456be2a352cdbb33bba bytes=17838 lines=125 path=COS_SCORE_NET-827_FAILFIX-B1B5_v1.7_86_REVISE_20261110.md>>>
# DESIGNATED CoS PLAN SCORE: NET-827 Stripe Checkout fail-fix B1–B5, plan v1.7 (writer: Claude, final try)

**Score: 86 / 100, REVISE.** The pass mark is 95. Only material defects count (correctness, safety, permissions, execution). Cosmetics are not deducted, and external prerequisites are not counted as plan defects.
Scored by GB CoS (designated CoS gate), 10 Nov 2026, about 6:00 PM ET (America/New_York).
**Count: NET-827 fail-fix track attempt 2 of 10; writer Claude try 2 of 2 (final).** (The plan header says "track attempt 1 of 10"; the CoS record counts v1.6 as attempt 1, so v1.7 is attempt 2. Cosmetic.)

**Per Eric's 4/10 rule, Claude's 2 tries are now used. A new writer is needed for attempt 3.**

## Plan scored
- `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\PLAN_NET-827_FAILFIX-B1B5_STRIPE-CHECKOUT-PREVIEW_v1.7_CLAUDE_20261110.md`
- SHA-256 **`b3f956534a7af2de67cd6f8d897e18cae7b7b375e0dbdf93724cec56ea2d8650`**, 53,625 bytes, 687 lines. Copied to the box (`/workspace/net827-claude/src/`). Size and hash match Claude's report.
- Every line read. Only v1.7 is scored.

## What this was scored against
- **Eric's binding decisions from the v1.6 record** (Free 10 for life; Silver 101–249; 7 Nov price ladder; Christmas 26 Nov 2026 12:01 AM ET to 25 Dec 2026 11:59:59 PM ET, server-side, never early; Beta Special $30 / 101+ / unlimited 6 months / once ever / block at create plus auto-refund backstop; partial refunds log only; full refund and lost dispute revoke; non-US allowed, billing auto, USD, Tax off; separate preview backend with its own test Firestore and test keys, never production; live keys only via a named later step; pytest via venv, BLOCKED if unavailable).
- **New Eric decisions since v1.6 (binding):**
  - Gold unlimited from **501**; Platinum 250–500 (CoS's earlier "250" was a CoS error).
  - Beta Special expiry: coins over the limit are **locked in the app (not viewable or editable)** until upgrade, never deleted. A very basic CSV of all coins and items, including locked ones, is always downloadable on any tier. Lazy lock on `/subscription-status` is OK, but **every add/view/edit path must check expiry server-side**.
  - Synthetic preview testers in production Firebase Auth are OK **for verification only**: named `ft-preview-0N@numista.ai`, **no production Firestore data**, listed in the plan, deleted by a cleanup step after Field Tester. No passwords stored.
  - Unverified Stripe field shapes and Christmas rounding: accepted; record them in the first gated sandbox run and fail closed.
  - CSV route: must not leak another user's coins and must stay inside the preview isolation rules.
- **D1–D8 from the v1.6 record** (84, REVISE), and everything that record listed as correct.
- **Code checked read-only** at `a3d7dca2`: `routes/payment_routes.py`, `routes/deps.py`, `routes/subaccount_routes.py`, `routes/support_routes.py`, `main.py` (Firestore/GCS init and collection routes), `tier_gatekeeper.py` (incl. `lock_overflow_coins`, `unlock_user_coins`, legacy email→uid migration), `requirements.txt`, `numista_mobile/firestore.rules`, `numista_mobile/lib/firebase_options.dart`, client Firestore use under `numista_mobile/lib/`.

## D1–D8 closure (from v1.6)

| ID | v1.6 defect | v1.7 status | Evidence |
|---|---|---|---|
| D1 | Preview isolation not in code; no deploy/verify blocks | **Partly closed** (residual becomes new N1) | New `env_guard.py` with fail-closed `load_data_config`/`check_stripe_key`, wired into `routes/deps.py` and `tier_gatekeeper.py`; named env settings; ID-token project named; PV-3 deploy and PV-4 read-only blocks in PS 5.1 with placeholder guards, `numista-backend` and `c547b7a0` refusals (§6 lines 365–562). But `main.py` and `subaccount_routes.py` keep their own hard-coded production Firestore clients (N1). |
| D2 | Customer map never written; renewal tier source unspecified | **Closed** | Map written inside grant transaction; later events resolve via map → subscription metadata → retry; tier from subscription metadata, never defaulted (§4.3 lines 259–266). |
| D3 | Lease removed | **Closed** | 60 s lease in `claim_event`, `lease_active` → 500, pytest cases (§4.2). |
| D4 | No end-to-end discount model | **Closed** | Automatic Christmas on in-window annual only; F&F via server-validated promotion code keeping Stripe's 500 cap; `pick_discount` one discount, no stacking; coupon-state control corrected (§4.1, §5, LK-2). |
| D5 | Half-cent Christmas totals denied | **Closed** | `amount_subtotal` + allowlisted coupon id + 1-cent tolerance; Stripe rounding accepted per Eric (§4.3 lines 237–258). |
| D6 | Refund revokes wrong entitlement | **Closed** | `stripe_payments` ledger mapping; Beta refund ends `beta_special_until` only; ungranted backstop revokes nothing; subscription refund clears tier then locks to effective limit (§4.4). See advisory A1 on the ledger key. |
| D7 | Dispute revoked on open | **Closed** | `dispute.created` logs + flag only; revoke only on `closed`/`lost`; won does nothing (§4.4). |
| D8 | Wrong file paths | **Closed** | Real paths in §3, `routes/deps.py` and `test_tier_gatekeeper.py` added. |

## Previously-correct items: unchanged (verified)
- B1 allowlist and price table unchanged (§0, §4.1). Prices match the 7 Nov ladder exactly.
- Free 10, Silver 249 unchanged; **Gold now 501+ unlimited, Platinum 500** per Eric's correction, with pytest 500 ok / 501 over (§4.5). JSON-safe `null` + `unlimited: true`, now also for `power_user` allowances.
- Christmas instants re-verified: `1795669260` = 2026-11-26 05:01:00 UTC = 12:01 AM EST; `1798261199` = 2026-12-26 04:59:59 UTC = 11:59:59 PM EST 25 Dec. Server gate at create and webhook, injectable clock.
- Beta Special rules unchanged (101+, block at create, backstop refund with idempotency key, 6 months, once ever, permanent flag).
- Partial refund log only; non-US / billing auto / USD / Tax off; B4 idempotency key + one active checkout (now with clearing rule).
- Cancel never touches comped/legacy users; now locks only to the effective tier.
- K1 LK-1…LK-8 not run; LK-3 names `numista-backend`; key-mode check.
- Gates/holds, `c547b7a0` excluded, main pinned, live off, no secrets or invented IDs.
- PS 5.1 shape (Stop, `Invoke-Native` with `$LASTEXITCODE`, TEMP worktree with outside-repo guard, `--detach`, `try/finally` + `git worktree prune`, quoted placeholders with guards).
- pytest via `.venv\Scripts\python -m pytest`, BLOCKED on failure.
- v1.6 advisories 1–10 all folded in.

## New Eric decisions: check

| Decision | Status |
|---|---|
| Gold 501+, Platinum 250–500 | **Met** (§0, §4.5) |
| Overflow locked, never deleted; upgrade unlocks | **Met on the server** (§4.8, §4.3 `unlock_user_coins`) |
| Every add/view/edit path checks expiry server-side; lazy lock OK | **Met for server routes as written**, but the app's direct Firestore reads/writes are add/view paths the plan does not cover (N3), and coin routes in `main.py` are outside the allowed scope (N1) |
| "Not viewable or editable" in the app | **Not met** (N3) |
| CSV of all coins incl. locked, any tier | **Partly met**: route, auth, formula-injection guard, pytest. May miss email-keyed coins (N3) |
| CSV cannot leak another user's coins | **Met**: auth required, uid from the token, never from the request; unauthenticated pytest. No cross-user path found |
| CSV stays within preview isolation | **Not stated**: which Firestore client the new route uses is unspecified; must be the guarded `deps` client (N1) |
| Synthetic testers named, listed, cleanup after FT, no passwords stored | **Met** (§6 table, PV-5 `getpass` + pattern guard + temp script removed, PV-6 after FT, console fallback) |
| Synthetic testers: no production Firestore data | **Not met** (N2) |
| Unverified Stripe shapes / rounding accepted, recorded in first gated run, fail closed | **Met** (§4.3, §8, §10 item 10) |

## New deductions on v1.7 (each one is material)

| # | Pts | Area | Evidence | Why it matters | Exact fix |
|---|---|---|---|---|---|
| N1 | −5 | Safety / execution: preview isolation still incomplete in the backend (D1 residual) | Plan §1b item 1 and §6 line 373: "both Firestore initialisations (`routes/deps.py`, `tier_gatekeeper.py`)". §3 line 100/106: `main.py` "one line only … no other change". Code: `main.py:349` `db = firestore.Client(credentials=credentials, project=PROJECT_ID)` (production) and `main.py:352` `gcs_client` with production bucket `numista-uploads-studio-9101802118-8c9a8` (line 342); `routes/subaccount_routes.py:26` `firestore.Client(project="studio-9101802118-8c9a8")`. Coin routes such as `/api/collection/count`, `/api/collection/clear` live in `main.py` (lines 8722, 8986). | There are at least **four** production data clients, not two. The in-process guard covers only two of them, and the plan forbids touching `main.py`. So in the preview service, most of the app's routes (including coin routes) would still aim at production Firestore and production Storage. The only thing stopping writes is the PV-1 IAM setup, and PV-4 checks env vars, not IAM. §4.8 also requires adding expiry checks to every coin route, but the `main.py` coin routes can't be edited under "one line only", so the builder has to stop or break scope. The new CSV route's client is unspecified. | Bring `main.py`'s Firestore/GCS init and `subaccount_routes.py` into scope and route them through `env_guard` (or import the guarded `deps` client). Make the preview bucket an env setting, guarded the same way. Allow the §4.8 check lines in `main.py` coin routes. Say `export_routes.py` uses the guarded `deps` client. Add a PV-4 read-only IAM check, e.g. `gcloud projects get-iam-policy studio-9101802118-8c9a8 --flatten=bindings[].members --filter="bindings.members:serviceAccount:$Sa" --format=value(bindings.role)`, which must return nothing. |
| N2 | −5 | Safety / Eric's binding decision: the preview app writes production Firestore directly | `numista_mobile/lib/firebase_options.dart:53,63,71` pin `projectId: 'studio-9101802118-8c9a8'`. 56 Dart files use `cloud_firestore` (157 `FirebaseFirestore.instance` uses), e.g. `my_collection_screen.dart:359` writes `users/{uid}`; `base_layout.dart:110-114` and `set_grouping_service.dart:38` read `users/{email}/coins`. `firestore.rules:40-48` let the owner read, create and delete their own coins. Plan §6/§8 change only `--dart-define=API_BASE_URL`, and §8 lets testers "sign in on the p7-gate preview … through the in-app upgrade flow". | `API_BASE_URL` reroutes only backend HTTP calls. The Flutter app still talks to **production Firestore** directly through the Firebase SDK. A synthetic tester who signs in on p7-gate will create and read documents in production Firestore. That breaks Eric's conditions: "no production Firestore data" for the testers, and "the preview never touches production Firestore". PV-6 deletes only the Auth accounts, so any production docs would be left behind. | Pick one: (a) the preview build points the client Firestore at the test project too (a second `FirebaseApp` for Firestore with test-project options via `--dart-define`, keeping Auth on production for verification only), with a pytest/analyze check; or (b) synthetic testers never sign in to the app. They use only the scripted client against the preview backend, and the in-app path is removed from §8. Either way, add a read-only check plus a YES-gated cleanup that removes any production Firestore docs under the four synthetic uids and emails before PV-6. |
| N3 | −4 | Correctness: the lock decision can't be met as specified ("not viewable or editable in the app"; CSV of all coins) | §4.8 puts all enforcement in backend routes. Code: the app reads coins straight from Firestore (above), and `firestore.rules` `match /users/{email}/coins/{coinId}` allows owner `read` and `delete` with no `locked_pending_upgrade` condition. Client `create` is allowed, bypassing the server add check. Coins are stored under both `users/{email}/coins` (legacy; rules and app use email) and `users/{uid}/coins` (migration in `tier_gatekeeper.py:67-110`). §4.8 CSV and `lock_overflow_coins` key on uid only. | Locked coins stay **viewable** (and deletable) in the app through direct Firestore reads. Over-limit **adds** still go through client-side creates. Server-side checks alone can't deliver Eric's "locked in the app". The uid-only CSV and lock can miss email-keyed coins, so the "CSV of all coins" promise can fail for legacy users, and their overflow never locks. | Add `firestore.rules` changes to scope (deny client `get/list/update/delete` where `resource.data.locked_pending_upgrade == true`; send over-limit adds through the server or check the limit in rules), with `firestore.rules.test.js` cases. A rules deploy is a production change, so give it its own Eric-YES gated step with a rollback. Make the app filter or label locked coins. Make the CSV and lock/unlock cover both the `users/{uid}` and `users/{legacy_email}` coin paths (and items: currency, wishlist), with pytest. |

**Total: 100 − 14 = 86, REVISE.**

## Closure matrix (v1.7)

| Item | Status |
|---|---|
| B1 tier/price allowlist | Closed |
| B2 user/tier resolution | Closed (D2) |
| B3 paid/amount/promo | Closed (D5; shapes accepted, fail closed) |
| B4 idempotency + lease | Closed (D3) |
| B5 refunds/disputes | Closed (D6, D7) |
| Free 10 / Silver 249 / Platinum 500 / Gold 501+ unlimited, JSON-safe | Closed |
| Prices per 7 Nov ladder | Closed |
| Christmas window, server-side, never early, annual-only, no stacking | Closed (D4) |
| Beta 101+, block + backstop, 6 months, once ever | Closed |
| Partial refund log only; full refund / lost dispute revoke | Closed |
| Non-US, billing auto, USD, Tax off | Closed (foreign tax/legal = open risk, not a defect) |
| Overflow lock, never deleted, upgrade unlocks | **Server side closed; app side open (N3)** |
| Every add/view/edit path checks expiry | **Open (N1 `main.py` scope, N3 client paths)** |
| CSV export: all coins incl. locked, any tier | **Partly (N3 email-keyed coins)** |
| CSV: no cross-user leak | Closed |
| CSV: preview isolation | **Open (N1, client unspecified)** |
| Separate preview backend + test Firestore + test keys; never production | **Partly: guard + deploy + check exist; `main.py`/`subaccount_routes` clients (N1) and client-direct Firestore (N2) open** |
| Synthetic testers: named, listed, cleanup after FT, no stored passwords | Closed |
| Synthetic testers: no production Firestore data | **Open (N2)** |
| Live keys via named later step, no secrets | Closed |
| pytest via venv, BLOCKED if unavailable | Closed |
| CR reconcile items (F&F flag, cancel vs comped, unused checkout, Dart allowlist, return URLs) | Closed |
| PS 5.1 / isolated worktree / no shared-tree checkout | Closed |
| `c547b7a0` never deployed; holds; main `9f04550a`; live off | Closed |
| Eric's scoped YES before deploy / Stripe action | Closed |

## Advisories (not scored)
1. **Ledger key at grant.** A subscription-mode Checkout Session usually has no `payment_intent`, and an F&F $0 session has none at all. Writing `stripe_payments/{payment_intent_id}` inside the grant transaction (§4.3 line 261) would fail on `None`. Skip the ledger write at grant when there is no PI and rely on the `invoice.paid` entry. Newer Stripe API versions also moved the invoice's PI under `invoice.payments`. This falls under the accepted unverified shapes: record it in the first sandbox run.
2. `lock_overflow_coins` uses `order_by("created_at")`, so Firestore skips coins with no `created_at` and they are never locked or counted. It also swallows errors with `print`, which fails open. Make the pytest cover a coin with no `created_at`, and have callers fail closed when the lock fails.
3. §5 item (4) says the webhook re-checks the session `created` time against the window, but `decide_grant` doesn't take `created`. Add it to the code spec.
4. `effective_limit` compares `beta_special_until > now`. State the stored type (Firestore timestamp vs epoch float) so the comparison can't raise.
5. CSV injection guard: also prefix cells starting with tab or CR.
6. PV-6 tells the operator to hand-edit one line. A `-Action` parameter would be safer. The test Stripe webhook endpoint creation isn't a named step (it's implied in PV-2).
7. Header attempt count: "track attempt 1 of 10" should be 2 of 10. Cosmetic.

## Writer assessment (Claude, try 2)
- **Strong pass on the v1.6 list:** D2–D8 are fully closed, with clean, testable code specs. Every previously-correct item is intact. All the new Eric decisions are written in, and all ten v1.6 advisories are applied. The synthetic-tester script is well guarded.
- **What it missed:** the codebase beyond the files the packet showed. `main.py` and a route module keep their own production clients, the Flutter app talks to production Firestore directly, and the Firestore rules allow reading locked coins. So preview isolation and "locked in the app" aren't fully delivered. These are the areas a follow-on writer has to cover. The fixes are listed above.

## Next step
- **REVISE. Per Eric's 4/10 rule, Claude's 2 tries are used. A new writer is needed for NET-827 attempt 3.** That writer should start from v1.7 (keep everything closed above) and close N1–N3.
- Track count: 2 of 10 used. The 4/10 trigger and the Claude 7/8 heads-up rules aren't reached.
- **No SAG packet is built,** and nothing is filed to Desk routes.

## Authority statement
This score **grants no code, git, deploy, Firestore, Firebase Auth, Stripe, Secret Manager or go-live authority**. HOLDs `74611e05…` and `41b8bd5f…` and the go-live addendum `c2b6ac93…` (NOT ACTIVE) stay in force. main stays `9f04550a`, and Stripe live stays OFF.
<<<END ARTIFACT id=A6>>>

## A7 - CoS harvest review of Carbon v1.9 (do-not-copy X1-X12, gaps G1-G9; reference)

<<<BEGIN ARTIFACT id=A7 sha256=653b3c8c225942529130cbdf4bf7671ece9127f78af23739643ed9f4849aeccb bytes=30310 lines=350 path=HARVEST_NET-827_CARBON-v1.9_FOR-CODE-WRITING_20261110.md>>>
# HARVEST REVIEW: NET-827 Carbon v1.9, reusable material for code writing

**Type:** HARVEST REVIEW. Not a scored attempt, and it does not count toward the 10 (Eric, t2554u: "Don't waste the V1.9 at least have it reviewed and pull out the good stuff.").
Reviewed by GB CoS, 10 Nov 2026, about 7:40 PM ET (America/New_York). Code checked read-only at `a3d7dca20fbbaf06a522205b22d0740b600de52b`.

## Source copy actually reviewed
- `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\Carbon\PLAN_NET-827_FAILFIX-B1B5_STRIPE-CHECKOUT-PREVIEW_v1.9_AG-CARBON_20261110.md`
- **SHA-256 `041c1ce3b5e89b78fcf662ec1cea707e6b44f8ec0c99bc3077548db8846c4a80`, 76,104 bytes, 1,056 lines, laptop mtime 10 Nov 2026 7:12:55 PM ET.** The identical mirror is in the `10 NOV 2026` folder. Box copy: `/workspace/net827-claude/src/`.
- The originally cited copy (67,847 B, SHA `3829de42…f5db`) was overwritten by Carbon at 7:12:55 PM ET and was **not** reviewed; those bytes are gone.
- The file's own header (lines 1–3) still says "v1.8 … attempt 3 of 10, try 1 of 4". The body is v1.9 (change list §1d, lines 70–112).
- Line numbers below refer to this 041c1ce3 copy.

## Bottom line
- **Reusable:**
  - the **design idea** for the lock (move overflow coins into a client-denied `locked_coins` subcollection, Option a);
  - the **real-bucket guard** and the PV-3/PV-4 bucket and IAM checks;
  - the **list of runtime clients to guard** (with one correction);
  - the **dedupe-by-doc-id** approach;
  - the **p7-gate no-sign-in policy**;
  - the **restored test list**.
- **Not reusable as written:**
  - the Firestore rules text (it would open entitlement fields to clients);
  - the `TIER_COIN_LIMITS` / `get_user_tier` rewrite (it breaks comped users and the price ladder);
  - the lock/unlock functions without fixes;
  - the rules deploy/rollback script;
  - the PV-4.5 and PV-6 scripts;
  - the env_guard Stripe/production changes.
- §4.1–§4.4 payment logic, Christmas, Beta Special, refunds/disputes and LK steps are byte-for-byte carry-overs of v1.8 (already closed in the v1.8 record). Reuse them from v1.7/v1.8 or here; nothing new was added there.

## Per-item check against the code (v1.8 deductions R1–R5 and the p7-gate advisory)

| Item | Does v1.9 fix it correctly? | Verdict |
|---|---|---|
| R1 Firestore rules lockout | **Concept yes, text no.** Moving locked coins to a separate client-denied subcollection does avoid the "rules are not filters" lockout: coin list queries stay unfiltered and permissive. But the rules text (lines 573–607) is a whole-file rewrite that, if pasted, **deletes every other rule** in the 350-line production file and **lets clients write their own `users/{id}` doc**, including `stripe_tier`, `beta_tester` and `admin`, which today are blocked by `_serverOnlyKeys()` (`firestore.rules` ~84–103). That's free Gold for anyone. If instead only the `locked_coins` block is added, the existing wildcard `match /users/{email}/{sub}/{docId}` (allows owner read/write unless `sub` is in an exclusion list that doesn't include `locked_coins`) **still grants owner read/write to `locked_coins`**, because rules are OR'd. So the lock is defeated either way. The coin create/update text also drops the existing `is_demo`/`is_demo_cleared` guards. The deploy script uses a non-existent CLI command and an unfilled rollback. | **Partly** (design reusable; rules text and deploy script do-not-copy) |
| R2 Double-counted coins | **Mostly.** Dedupe by doc id (lines 495–513) is right: the migration copies with identical ids (`tier_gatekeeper.py:67-110`). Coins-only locking (line 433) is right. But the shortcut "if `migration_status == completed`, read only `users/{uid}/coins`" (line 431) is **wrong for this app**: the client still reads and writes coins under `users/{email}/coins` (about 30 call sites, e.g. `base_layout.dart:110-114`, `set_grouping_service.dart:38`), and some under `users/{uid}/coins` (`beta_checklist_service.dart:355-376`). After migration, new coins land on the email path, and a uid-only read would miss them (undercount, missing CSV rows). | **Partly**: always union both paths and dedupe by id; drop the migration shortcut |
| R3 Invented bucket | **Yes.** The production default is now the real `numista-uploads-studio-9101802118-8c9a8` (matches `main.py:342`). Preview must set a different bucket. PV-3 passes `USER_CONTENT_BUCKET` with a placeholder guard. PV-4 checks it and the bucket IAM. The PV-1 bucket name `numista-preview-user-content-test` is a proposal; record the real one at execution. | **Fixed** |
| R4 Unguarded clients | **Mostly.** The list (lines 729–749) matches my import-graph scan of `main.py`. One error: `routes/support_routes.py:38` is a **Firestore** client (`firestore.Client()`), not `storage.Client()`; it must route to `deps.get_db()`. The AST test (line 749) is scoped to "no file in `numista_backend/`", which would fail on about 400 standalone scripts (`_scripts/`, `upload_*.py`, etc.); scope it to the runtime import graph of `main.py`. Routing `numista_scraper` through `routes.deps` creates a dependency from a standalone package back to the app; a guarded provider in `env_guard` is cleaner. | **Mostly fixed** (one mislabel, test scope wrong) |
| R5 Dropped tests | **Yes.** v1.7's §4.8 list is restored, plus a cross-user CSV test, the migrated-dedupe test and rules emulator cases (lines 609–629, 983–992). But the rules tests are described as "Mocha/Chai" in a new `numista_mobile/tests/` file; the repo already has a **Jest** harness at `numista_mobile/firestore.rules.test.js` with `package.json` `"test": "jest firestore.rules.test.js"`. Extend that file. The rules test list also lacks the two cases that would have caught the R1 text errors (see Remaining gaps). | **Fixed in substance**; harness and path need adjusting |
| p7-gate users advisory | **Yes.** No human (Eric or beta testers) signs in on p7-gate during the NET-827 window; tests are pytest plus scripted CLI only (lines 751–756). | **Fixed** |

## Reusable sections (verbatim, with v1.9 line ranges)

### H1. p7-gate no-sign-in policy (lines 751–756), reuse as is
~~~~
### Advisory A1: p7-gate User Sign-In Prohibition Policy
During the NET-827 preview testing window, **NO human users (neither Eric nor beta testers) shall sign in on `p7-gate`**.
Testing is conducted exclusively via:
- Automated pytests (§7) using mocked/virtual environments.
- Scripted CLI tests (§8) calling the preview backend Cloud Run URL directly with synthetic ID tokens.
This prevents mixed-project data anomalies where web client writes land in production Firestore while API calls land in preview.
~~~~

### H2. Lockout analysis and Option (a) concept (lines 434–448), reuse the reasoning, not the rule text
~~~~
- **Client Lockout Prevention via Subcollection Design — Option (a) (R1):**
  - *Problem:* Applying `locked_pending_upgrade != true` to client `read` rules rejects all client collection list queries because Firestore rules are not filters, and existing coin documents have no `locked_pending_upgrade` field. Deploying such a rule locks out all existing users across production!
  - *Solution (Option a):*
    - Keep client `read` rules permissive for owned coins in `users/{userId}/coins/{coinId}`:
      `allow read: if request.auth != null && (request.auth.uid == userId || request.auth.token.email.lower() == userId.lower());`
    - When coins overflow the plan limit, backend `lock_overflow_coins` (using Admin SDK) moves overflow coin documents into a subcollection:
      `users/{userId}/locked_coins/{coinId}`
    - In `numista_mobile/firestore.rules`:
      ```javascript
      match /users/{userId}/locked_coins/{coinId} {
        allow read, write: if false; // Denied to all client SDKs; backend Admin SDK only!
      }
      ```
    - Because the mobile/web client queries `users/{userId}/coins`, any coins moved into `users/{userId}/locked_coins` are physically absent from the client query result. The client app naturally cannot view, read, edit, or delete them!
    - When the user upgrades (§4.3), backend `unlock_user_coins` (using Admin SDK) moves coin documents back from `users/{userId}/locked_coins` to `users/{userId}/coins`.
~~~~
Fixes required before use: see H3 notes and the Do-not-copy list (rules text).

### H3. Dedupe-by-doc-id core of `lock_overflow_coins` (lines 495–513), reuse with fixes
~~~~
    coins_map = {}  # coin_id -> doc_data
    # 1. Read uid path
    for doc in user_ref.collection("coins").stream():
        data = doc.to_dict()
        data["_id"] = doc.id
        data["_path"] = doc.reference
        coins_map[doc.id] = data

    # 2. If not migrated, check email path and deduplicate
    if not migration_done and email:
        email_ref = db.collection("users").document(email.lower())
        for doc in email_ref.collection("coins").stream():
            if doc.id not in coins_map:
                data = doc.to_dict()
                data["_id"] = doc.id
                data["_path"] = doc.reference
                coins_map[doc.id] = data

    total_coins = len(coins_map)
~~~~
Required fixes when coding:
- Always union both paths. Remove the `migration_done` shortcut (lines 491–493, 504).
- Keep each coin's **origin path** and lock into `locked_coins` under that **same parent** (email or uid doc), so unlock can restore it to the path the client actually reads.
- Commit in chunks of 250 coins or fewer (2 writes each; Firestore's batch limit is 500). Write `set` before `delete` so a re-run is safe.
- Lock order needs an Eric decision. Today's code keeps the **oldest** `limit` coins visible and locks the newest (`tier_gatekeeper.py:325-336`). v1.9 locks the **oldest** (line 524 comment vs line 487 docstring disagree). Keep today's behaviour unless Eric says otherwise.

### H4. Coins-only scope (line 433), reuse as is
~~~~
  - **Lock coins ONLY:** Currency and wishlist are NEVER locked and NEVER counted against tier coin limits. Wishlist items are not owned coins; currency is separate.
~~~~

### H5. Real-bucket guard in env_guard (lines 653–654 and 699–713), reuse
~~~~
PROD_PROJECT_ID = "studio-9101802118-8c9a8"
PROD_USER_CONTENT_BUCKET = "numista-uploads-studio-9101802118-8c9a8"

def resolve_user_content_bucket(cfg, env=None):
    """
    Advisory R3 Fix:
    Uses the real production bucket: numista-uploads-studio-9101802118-8c9a8.
    In preview mode, requires USER_CONTENT_BUCKET env var to be set and strictly
    forbids matching the production bucket name.
    """
    env = os.environ if env is None else env
    bucket = env.get("USER_CONTENT_BUCKET", "")
    if cfg["mode"] == "preview":
        if not bucket or bucket == PROD_USER_CONTENT_BUCKET:
            raise EnvGuardError("preview must specify a dedicated non-production USER_CONTENT_BUCKET")
    else:
        bucket = bucket or PROD_USER_CONTENT_BUCKET
    return bucket
~~~~
Use with the v1.7/v1.8 `load_data_config` and `check_stripe_key` (see Do-not-copy D5), plus a pytest for the production default and the preview refusal.

### H6. Runtime client inventory (lines 729–749), reuse with one correction
~~~~
### Full Scope of Backend Clients Routed via Guard (R4):
To ensure zero accidental access to production Firestore or GCS from the preview backend, all runtime-reachable clients are scoped:
1. `routes/deps.py`:
   - Line 25 `storage_client = storage.Client(project=PROJECT_ID)` is replaced with `get_gcs_client()`.
   - Exports `get_db()`, `get_gcs_client()`, and `get_user_content_bucket()`.
2. `brain_processor.py`:
   - Lines 51 and 311 `firestore.Client(project=PROD)` replaced with `routes.deps.get_db()`.
3. `services/canon_sync_service.py`:
   - Lines 24-25 production `firestore.Client(...)` and `storage.Client(...)` replaced with `routes.deps.get_db()` and `routes.deps.get_gcs_client()`.
4. `numista_scraper/storage.py` & `scrapers.py`:
   - Replace calls to `firebase_admin.firestore.client()` (storage.py:29-38; scrapers.py:146, 705, 731) with `routes.deps.get_db()`.
   - Explicit rule: `firebase_admin.firestore.client()` is **strictly forbidden** in runtime code, because the default Firebase app is initialized with `FIREBASE_AUTH_PROJECT_ID` (production Auth).
5. `main.py`:
   - Line 349 (`db = firestore.Client(...)`) replaced with `deps.get_db()`.
   - Line 352 (`gcs_client = gcs.Client(...)`) replaced with `deps.get_gcs_client()`.
   - Line 358: `initialize_app()` initialized for Firebase Auth only.
   - Lines 4430 and 9606: unscoped `gcs.Client()` replaced with `deps.get_gcs_client()`.
6. `routes/estate_routes.py` (line 42) & `routes/support_routes.py` (line 38):
   - Unscoped `storage.Client()` replaced with `deps.get_gcs_client()`.
7. **Automated Enforcement:**
   - Added `numista_backend/tests/test_no_unscoped_clients.py` asserting via AST that no file in `numista_backend/` constructs `firestore.Client` or `storage.Client` directly outside `env_guard.py`, and no file invokes `firebase_admin.firestore.client()`.
~~~~
Corrections:
- `routes/support_routes.py:38` is `firestore.Client()` and goes to `get_db()`.
- Scope the AST test to modules reachable from `main.py` (module-level and lazy imports), not every file in `numista_backend/`.
- My scan also lists the `routes/deps.py:46-48` and `tier_gatekeeper.py:21-29` init lines, already in scope.

### H7. PV-3 deploy block with bucket guard (lines 768–813), reuse
~~~~
```powershell
$ErrorActionPreference = 'Stop'
function Invoke-Native {
    param([scriptblock]$Cmd)
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $Cmd } finally { $ErrorActionPreference = $old }
    if ($LASTEXITCODE -ne 0) { throw "Native command failed: $LASTEXITCODE" }
}
$repo              = 'C:\Users\ericd\Documents\MyVertexProject'
$ProdProject       = 'studio-9101802118-8c9a8'
$ProdBucket        = 'numista-uploads-studio-9101802118-8c9a8'
$PreviewProject    = '<PREVIEW_PROJECT_UNKNOWN>'
$Service           = '<PREVIEW_SERVICE_UNKNOWN>'
$Sa                = '<PREVIEW_SERVICE_ACCOUNT_UNKNOWN>'
$KeySecret         = '<TEST_KEY_SECRET_NAME_UNKNOWN>'
$WhSecret          = '<TEST_WEBHOOK_SECRET_NAME_UNKNOWN>'
$UserContentBucket = '<PREVIEW_USER_CONTENT_BUCKET_UNKNOWN>'
$sha               = '<BUILT_SHA_UNKNOWN_RECORD_AT_EXECUTION>'

foreach ($v in @($PreviewProject, $Service, $Sa, $KeySecret, $WhSecret, $UserContentBucket, $sha)) {
    if ($v -like '<*') { throw "placeholder not filled: $v" }
}
if ($PreviewProject -eq $ProdProject)       { throw 'preview project must not be the production project' }
if ($Service -eq 'numista-backend')         { throw 'must never deploy over numista-backend' }
if ($UserContentBucket -eq $ProdBucket)     { throw 'preview must not use production user content bucket' }
if ($sha -like 'c547b7a0*')                 { throw 'c547b7a0 is held and must never be deployed' }

$wt = Join-Path $env:TEMP 'net827_backend'
if ($wt.StartsWith($repo)) { throw 'worktree must be outside the repo' }
$envVars = "NUMISTA_ENV=preview,FIRESTORE_PROJECT_ID=$PreviewProject,FIREBASE_AUTH_PROJECT_ID=$ProdProject,STRIPE_EXPECTED_MODE=test,USER_CONTENT_BUCKET=$UserContentBucket"
$secrets = "STRIPE_SECRET_KEY=${KeySecret}:latest,STRIPE_WEBHOOK_SECRET=${WhSecret}:latest"

Set-Location $repo
try {
    Invoke-Native { git worktree add --detach $wt $sha }
    $src = Join-Path $wt 'numista_backend'
    Invoke-Native { gcloud run deploy $Service --source $src --project $PreviewProject --region us-central1 --service-account $Sa --set-env-vars $envVars --set-secrets $secrets --allow-unauthenticated --quiet }
} finally {
    Set-Location $repo
    if (Test-Path $wt) { git worktree remove --force $wt }
    git worktree prune
}
```
~~~~

### H8. PV-4 isolation check with project and bucket IAM (lines 815–861), reuse
~~~~
```powershell
$ErrorActionPreference = 'Stop'
function Invoke-NativeCapture {
    param([scriptblock]$Cmd)
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { $out = & $Cmd } finally { $ErrorActionPreference = $old }
    if ($LASTEXITCODE -ne 0) { throw "Native command failed: $LASTEXITCODE" }
    return $out
}
$ProdProject    = 'studio-9101802118-8c9a8'
$ProdBucket     = 'numista-uploads-studio-9101802118-8c9a8'
$PreviewProject = '<PREVIEW_PROJECT_UNKNOWN>'
$Service        = '<PREVIEW_SERVICE_UNKNOWN>'
foreach ($v in @($PreviewProject, $Service)) { if ($v -like '<*') { throw "placeholder not filled: $v" } }

$json = (Invoke-NativeCapture { gcloud run services describe $Service --project $PreviewProject --region us-central1 --format=json }) -join "`n"
$svc  = $json | ConvertFrom-Json
$envs = $svc.spec.template.spec.containers[0].env
$fp   = ($envs | Where-Object { $_.name -eq 'FIRESTORE_PROJECT_ID' }).value
$mode = ($envs | Where-Object { $_.name -eq 'NUMISTA_ENV' }).value
$ucb  = ($envs | Where-Object { $_.name -eq 'USER_CONTENT_BUCKET' }).value

if ($mode -ne 'preview')             { throw "NUMISTA_ENV is '$mode', expected preview" }
if ($fp -ne $PreviewProject)         { throw "FIRESTORE_PROJECT_ID is '$fp', expected preview project" }
if ($fp -eq $ProdProject)            { throw 'SECURITY DEFECT: preview points at production Firestore project' }
if (-not $ucb -or $ucb -eq $ProdBucket) { throw "SECURITY DEFECT (R3): USER_CONTENT_BUCKET is '$ucb', cannot be production bucket" }
if ($json -match 'numista-backend')  { throw 'preview configuration references numista-backend' }

# N1 Project-level IAM check: Verify preview Service Account has ZERO roles on production project
$Sa = ($svc.spec.template.spec.serviceAccountName)
if (-not $Sa) { throw "preview serviceAccountName missing in Cloud Run spec" }
$prodRoles = (Invoke-NativeCapture { gcloud projects get-iam-policy $ProdProject --flatten="bindings[].members" --filter="bindings.members:serviceAccount:$Sa" --format="value(bindings.role)" })
if ($prodRoles -and $prodRoles.Trim() -ne '') {
    throw "SECURITY DEFECT (N1): Preview service account $Sa holds IAM roles on production project: $prodRoles"
}

# A3 Bucket-level IAM check: Verify preview Service Account has ZERO roles on production storage bucket
$bucketPolicy = (Invoke-NativeCapture { gcloud storage buckets get-iam-policy gs://$ProdBucket --format=json }) -join "`n"
if ($bucketPolicy -match [regex]::Escape($Sa)) {
    throw "SECURITY DEFECT (R3/A3): Preview service account $Sa holds bucket-level permissions on production bucket gs://$ProdBucket"
}

'PV-4 isolation check passed: confirmed zero IAM access to production Firestore and Storage.'
```
~~~~
Note: the bucket check matches the SA email anywhere in the policy JSON, which is fine. It doesn't cover folder/org grants.

### H9. Restored test list (lines 623–629 and 983–992), reuse
~~~~
- **Restored & Expanded Test Suite (§4.8, R5):**
  1. Expired Beta Special with 300 coins: add coin returns 403; locked coins are moved to `users/{uid}/locked_coins` and thus absent from client app list queries; CSV export returns all 300 coins.
  2. Upgrade to Gold: unlocks all coins by moving them from `locked_coins` back to `coins`.
  3. Formula injection prefix: cells with `=`, `+`, `-`, `@`, `\t`, `\r` are escaped with `'`.
  4. Unauthenticated CSV export returns 401/403.
  5. Cross-user CSV rejection: User A token cannot export User B's coins or items (including B's legacy email path).
  6. Migrated user deduplication (R2): Migrated user with identical 200 coins in both `users/{email}/coins` and `users/{uid}/coins` counts as 200 (not 400), locks 0 coins on Silver tier (limit 249), and CSV exports exactly 200 coin rows.
~~~~
~~~~
Pytest suite includes:
- Free (10), Silver (249), Platinum (500), Gold (501+ unlimited), JSON-safe checks.
- Christmas window create & webhook verification; annual-only enforcement.
- Beta Special $30, 101+ limit, 6-month validity, once-ever block.
- Refund & dispute ledger mapping; lost dispute revoke.
- Expired Beta Special overflow locking (Option a subcollection `locked_coins`); upgrade unlocks back to `coins`.
- Migrated user deduplication: 200 identical coins in email and uid paths count as 200, lock 0 on Silver, CSV has 200 rows (R2).
- CSV export formula injection escaping (`'`, `=`, `+`, `-`, `@`, `\t`, `\r`) (A5).
- Cross-user CSV rejection: User A token cannot export User B's coins (R5).
- Real bucket resolution: default `numista-uploads-studio-9101802118-8c9a8`, preview requires distinct bucket (R3).
~~~~

### H10. Rules emulator test cases (lines 609–614), reuse the cases; put them in the existing Jest file
~~~~
- **Firestore Rules Unit Tests (`numista_mobile/tests/firestore.rules.test.js`):**
  A dedicated Mocha/Chai test suite executed against the Firebase Local Emulator (`firebase emulators:exec --only firestore "npm test"`):
  1. `test_owner_can_read_coins_without_lock_field`: Authenticated user can list `users/{uid}/coins` when docs lack `locked_pending_upgrade` field (asserts list query succeeds).
  2. `test_owner_cannot_read_or_write_locked_coins`: Authenticated user attempting `users/{uid}/locked_coins/{coinId}.get()` or `.set()` fails with Permission Denied (403).
  3. `test_owner_cannot_set_locked_field`: Authenticated user attempting `users/{uid}/coins/{coinId}.set({locked_pending_upgrade: true})` fails with Permission Denied.
  4. `test_user_cannot_read_other_users_coins`: User A token attempting to read User B's `users/{userB_uid}/coins` fails with Permission Denied.
~~~~

### H11. CSV export spec (lines 616–621), reuse with the H3 union-dedupe fix
~~~~
- **CSV Export (`routes/export_routes.py`):**
  - Authenticated `GET /api/export/collection/csv` using guarded `deps.get_db()`.
  - Exports basic CSV containing all owned items: active `coins`, `locked_coins`, `currency`, and `wishlist`.
  - Migrated user deduplication: if migrated, queries `users/{uid}` collections; else deduplicates between `users/{uid}` and `users/{email}` by document ID.
  - Formula injection escaping (A5): Cells starting with `=`, `+`, `-`, `@`, `\t` (tab), or `\r` (carriage return) are prefixed with `'` (single quote).
  - Cross-user isolation (R5): Returns only caller's own items (verified against caller's UID and email from ID token). Rejects caller attempts to export another user's collection.
~~~~
Also: the CSV must read `locked_coins` under **both** parent paths once H3's origin-path fix is applied.

### H12. Carry-overs (lines 184–365, 631–638, 1038–1047)
§4.1–§4.4, §5 and LK-1…LK-8 are the v1.8 text unchanged, already verified in the v1.8 record. Use either copy.

## DO NOT COPY (errors in v1.9)

| # | v1.9 lines | What's wrong | Evidence |
|---|---|---|---|
| X1 | 573–607 (full rules file) and 438, 450 | Pasted, it **replaces the whole production rules file**. It drops estate_reports, settings, server-only subcollections, config, reference data, `coin_image_index`, etc. It grants clients `write` on `users/{userId}`, which removes `_serverOnlyKeys()` and lets any user set `stripe_tier`/`beta_tester`/`admin` (privilege escalation, free paid tiers). It also lets clients delete their user doc (today `delete: if false`). Coin create/update **drop the `is_demo`/`is_demo_cleared` guards** (Addendum B). | `numista_mobile/firestore.rules` lines 40–67, 84–103, 105–114 |
| X2 | 443–445 / 593–595 alone | Adding only `match …/locked_coins/{coinId} { allow read, write: if false; }` **doesn't lock anything**, because the existing wildcard `/users/{email}/{sub}/{docId}` and `/{rest=**}` blocks allow the owner read/write when `sub` isn't excluded, and rules are OR'd. | `firestore.rules` ~105–114 |
| X3 | 370–404 (`TIER_COIN_LIMITS`, `within_limit`, `get_user_tier`) | **Breaks the price ladder and comped users.** `pro: 249` (Copper is 100), `numismatist: 500` (Silver is 249), `power_user: 10` (was unlimited), and `family_estate`/`sovereign` are removed, so beta testers fall to 10 coins and get locked. `get_user_tier` reads `subscription_tier`/`subscription_active` (fields the code doesn't use) and drops `stripe_tier`, `beta_tester`, lifetime and the legacy `creation_timestamp` rule. JSON "unlimited" changed to `-1/999999`, against v1.7's agreed `null` + `unlimited: true`. The `within_limit` argument order is swapped. | v1.7/v1.8 §4.5; `tier_gatekeeper.py:132-150` |
| X4 | 485–565 as written | Lock/unlock: a single batch can exceed Firestore's 500-write limit (e.g. 290 overflow coins = 580 writes). Locked email-path coins are moved under `users/{uid}/locked_coins` and unlocked back to `users/{uid}/coins`, a path the app doesn't read for legacy users, so coins "vanish" after upgrade. `migration_done` shortcut (see R2). Lock order is inverted versus today's code. | `tier_gatekeeper.py:325-351`; client email-path reads |
| X5 | 661–686, 716–727 (env_guard Stripe/production) | Production now defaults `STRIPE_EXPECTED_MODE=live` and refuses a test key. Stripe live is **OFF** under HOLD `41b8bd5f`, so production presumably runs sandbox keys (not verifiable here) and would refuse to start after merge. The production "must use the production project" check was removed, and `rk_live_` is no longer recognised. Use the v1.7/v1.8 versions. | v1.8 §6 lines 457–487 |
| X6 | 1013–1036 (rules deploy) | `firebase firestore:rules:get` is not a Firebase CLI command. `>` in PS 5.1 writes UTF-16. There's no `$LASTEXITCODE`/`Invoke-Native` check. The rollback is a comment with `--config "..."`, so it can't be run. It doesn't name HOLD `41b8bd5f` and doesn't sequence the rules after the updated app is live. | Firebase CLI; PS 5.1 behaviour |
| X7 | 863–915 (PV-4.5) | The cleanup branch is a comment (no-op) that still continues. It prints full production user docs (PII) to the console. It passes a multi-line script with embedded double quotes to `python -c`; Windows PowerShell 5.1 strips inner quotes on native calls, so the script breaks. `initialize_app()` has no projectId. The venv path is the repo root `.venv`, not `numista_backend\.venv` as in PV-5. Use the temp-file pattern from PV-5 (v1.7/v1.8). | PS 5.1 native-arg quoting |
| X8 | 917–953 (PV-6) | Same `-c` quoting problem. It lost PV-5's `^ft-preview-0[1-4]@numista\.ai$` pattern guard, the final `UserNotFoundError` verification and the console fallback. `initialize_app()` has no projectId. Keep the v1.7/v1.8 PV-6 and just add a `-Action` parameter. | v1.8 lines 564–608 |
| X9 | 958–966 (§7 pytest) | Drops venv creation and the BLOCKED catch from Eric's pytest rule, and points at a repo-root `.venv`. Keep the v1.7/v1.8 block. | v1.8 lines 703–723 |
| X10 | 1009 | "Target commit: `49e77cf7`" isn't in any CoS record and can't be verified here (shallow clone at `a3d7dca2`). Don't carry an unverified SHA; the built SHA is recorded at execution. | Records |
| X11 | 1–3 | Header says v1.8/attempt 3. Stale. | n/a |
| X12 | 610, 978 | Mocha/Chai and a new `tests/` path. The repo already uses Jest at `numista_mobile/firestore.rules.test.js`. | `numista_mobile/package.json` |

## Remaining gaps (nobody has closed these yet)
1. **Rules: incremental edit only.**
   - Add `'locked_coins'` to **both** wildcard exclusion lists.
   - Add `match /users/{email}/locked_coins/{docId} { allow read, write: if false; }`.
   - On coin `create`, require `locked_pending_upgrade` absent or false.
   - On coin `update`, add `locked_pending_upgrade` to the `affectedKeys` deny list.
   - Keep everything else byte-identical, and say so in the plan.
2. **Rules emulator tests in the existing Jest file.** Keep v1.9's four cases and add:
   - (a) the owner can't read or write `locked_coins` **via the wildcard**;
   - (b) the owner still can't set `stripe_tier`/`beta_tester` on the user doc;
   - (c) the existing `is_demo` create/update tests still pass;
   - (d) the owner's unfiltered list of `users/{email}/coins` succeeds.
3. **Rules deploy step.**
   - Use a real backup: the Rules REST API (`firebaserules.googleapis.com` releases/rulesets) read-only, or deploy from the git copy of the current `firestore.rules` at `9f04550a` as the rollback source.
   - Run it under `Invoke-Native`.
   - Give a runnable rollback block.
   - Name it as a production change under HOLD `41b8bd5f`, needing Eric's scoped YES.
   - Sequence it: the backend lock (move) code must be live before any coin is moved, and the rules can deploy independently because they only add denials on a new subcollection.
4. **Lock/unlock implementation.**
   - Union both paths, dedupe by id, keep the origin path, chunked batches, set-then-delete, idempotent re-run.
   - Unlock restores to the origin path.
   - Lock order needs an Eric decision (today: newest are locked).
   - Pytest for over 250 overflow coins (chunking) and for a legacy email-path user's lock and unlock round trip.
5. **`TIER_COIN_LIMITS` / `get_user_tier`.** Keep v1.7/v1.8 §4.5 exactly. If a `now_ts` parameter is added, it must keep every existing branch of `get_user_tier` (`stripe_tier`, `tier`, `beta_tester`, lifetime, legacy `creation_timestamp`) and only add the unexpired-`beta_special_until` = unlimited branch.
6. **Existing `locked_pending_upgrade == true` coins** written by today's flag-based `lock_overflow_coins` may already exist in production. The plan needs a one-time read-only count. If any exist, a YES-gated migration either moves them into `locked_coins` or clears the flag.
7. **AST/grep client test** scoped to the `main.py` import graph. The `support_routes` fix goes to `get_db()`.
8. **env_guard.** Use the v1.7/v1.8 `load_data_config`/`check_stripe_key` (explicit `STRIPE_EXPECTED_MODE`, production-project check) plus v1.9's bucket function. Confirm production's current Stripe mode before choosing its `STRIPE_EXPECTED_MODE` value.
9. **Server routes.** A direct request for a coin that now lives in `locked_coins` should return 403 `LOCKED_PENDING_UPGRADE`, not 404. The route must look in `locked_coins` to tell the two apart.

## Authority statement
This harvest review **grants no code, git, deploy, Firestore, Firestore rules, Firebase Auth, Storage, Stripe, Secret Manager or go-live authority**. It is not a score and doesn't count toward the 10. HOLDs `74611e05…` and `41b8bd5f…` stay in force; main stays `9f04550a`; Stripe live stays OFF. Nothing was filed and no agent was messaged.
<<<END ARTIFACT id=A7>>>

<<<END OF PACKET>>>
