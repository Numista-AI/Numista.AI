# NET-827 Stripe Checkout Preview Plan v1.9.3 (replaces v1.9.2, v1.9.1, v1.9, v1.8, v1.7 and all earlier versions)

Attempt: v1.9.3; author SAG (via CoS API, attempt 7/10, SAG writer try 1/4). Base: v1.9.2 (CoS 94 REVISE, SHA-256 `c6c5f1b6eeeac2e8cda607bf5daa47776ddc683326ddbf7d6bc0964cb23971bc`); v1.9.3 changes only the items in §2h (D1, D1-claim, ADV1, ADV2, ADV4, ADV5). v1.9.2 base: v1.9.1 (CoS 100, SAG 83 REVISE, SHA-256 `ec9c50b49c4d19d45a4a545b3171b98bb8aeb26761036070c9cadabbde0bfddb`); v1.9.2 changes only the items listed in Section 12 (S1, S2, S3, E1, A1). v1.9.1 base: v1.9 (CoS 96 PASS, SHA-256 `0434dfce1218a530842c1aa6f89707eedc90451ae4cb768beac8c226e3dfed70`). v1.9 base: v1.7 (CoS 86). Closes v1.7 record N1-N3, v1.8 record R1-R5 and advisories 1-8, v1.7 advisories A1-A7, and the nine "Remaining gaps" of the CoS harvest review of Carbon v1.9 (harvest file SHA-256 `653b3c8c225942529130cbdf4bf7671ece9127f78af23739643ed9f4849aeccb`). Carries over from Carbon v1.8 only: N2 (no synthetic-tester sign-in on p7-gate; HTTP-only checks against the preview backend), the preview-service-account-has-no-production-IAM check, and A1-A6.
Status: PLAN ONLY. Writing this plan performed no code, git, deploy, Firestore, Firestore-rules, Firebase Auth, Storage, Stripe, Cloud Run, GCS or Secret Manager action. All code reading was read-only at `a3d7dca20fbbaf06a522205b22d0740b600de52b`.
Gates: CoS 95 → full-plan SAG 95 on the exact same file SHA → Eric's typed scoped YES. Live payments need a further separate gate (Section 9, LK steps). The rules hardening step RX (Section 9.4) is **REQUIRED before go-live** (v1.9.2 E1: Eric, 7:57 PM ET 10 Nov, "Definitely fix the 'Free Limits' bug"); it is a PRODUCTION change and needs its own scoped Eric YES that names HOLD `41b8bd5f`; the NET-827 preview does not need it and does not run it.

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
- **NET-827 makes no Firestore rules change.** The lock and every new server-only field are enforced on the server and stored only in new top-level collections that the current, unchanged rules already deny to every client (`numista_mobile/firestore.rules:345-348`, "Deny everything else"). Section 4.9 shows why this is sound. The rules hardening in Section 9.4 (RX) is required before go-live (v1.9.2 E1), runs at the go-live gate under its own YES, and is fully specified there.

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
- **No rules change needed now:** the "sealed back room" is a storage area the live security rules already block for every user. So we do not have to touch the live rules to make the lock work. A small tightening of the rules is written out for go-live and is **required** before go-live (you said "Definitely fix the 'Free Limits' bug"): it stops users from giving themselves free or unlimited coins. It still needs its own YES, with test, exact command and undo.
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
| R1 (−6) | Rules change would lock every user out of their own list queries on live; create rule undecided; no emulator tests, deploy, rollback; production change not named | **no rules change in NET-827.** Client list queries and the rules file stay exactly as they are; locked coins leave the readable folders (Option a, top-level client-denied collection). Create limit: server routes reject over-limit adds (403); client-SDK creates (allowed by `firestore.rules:55-58`, rules can't count) are reconciled server-side at the next server touch (moved to the locked collection, newest first). Emulator tests against the unchanged file prove owner list still works and locked/entitlement collections are denied. Go-live hardening RX (required before go-live, v1.9.2 E1) is additive only, with emulator tests, byte-exact live backup, exact deploy command and runnable rollback, and is named a PRODUCTION change under HOLD `41b8bd5f` needing its own scoped Eric YES | 0, 4.8, 4.9, 7.2, 9.4 |
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
| G1 | Rules: incremental edit only | NET-827 has no rules edit at all. RX (required before go-live, v1.9.2 E1) is additive only: `'locked_coins'` added to both wildcard exclusion lists, an explicit deny block, `locked_pending_upgrade` blocked on coin create/update, extra server-only keys; every other line byte-identical; exact diff given | 4.9, 9.4 |
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
| 3 | Rules: ADD only, rest byte-identical, current SHA-256 and rollback, `locked_coins` in the catch-all exclusions, users never write their own account entitlements | Yes, as the go-live step RX (required before go-live, v1.9.2 E1); the NET-827 preview itself needs no rules change (preferred server-side route allowed by the assignment) | 4.9, 9.4 |
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

### 2g. v1.9.1 record (CoS 100; SAG 83 REVISE): items fixed in v1.9.2

| ID | Finding | How v1.9.2 closes it | Section |
|---|---|---|---|
| S1 (SAG 1) | Beta Special grant set `stripe_tier` from the client's `tier`, so $30 could buy a permanent paid tier | server-set `purchase_kind` (`beta`/`subscription`) in Session metadata, never from the client; Beta ignores the request `tier`/`interval` and writes no `target_tier`; Beta grant writes only the Beta fields in `entitlements`, the ledger (`kind: beta`) and runs unlock, never `stripe_tier`/`subscription_status`; webhook fails closed on a missing or inconsistent `purchase_kind`; status endpoint reports Beta via `beta_special_active`/`beta_special_until`; `purchase_kind` added to RX's server-only keys; pytest (free user with `tier=estate` + Beta → no tier; after expiry and after refund → no paid tier; Copper + Beta refund → Copper kept) | 3, 4.1, 4.3, 4.4, 4.8, 4.9, 7.1, 7.2, 9.4 |
| S2 (SAG 2) | Revoke cleared only `users/{uid}.stripe_tier`; a tier on `users/{email}` survived the merge | `revoke_paid_tier` writes a present null `stripe_tier` on both `users/{uid}` and `users/{email}` (plus the raw-case email doc) for cancel, full refund and lost dispute; email from `entitlements.email` or Firebase Auth, else retry; revoke-only legacy fallback by matching `stripe_customer_id`; pytest with the tier only on the email doc → merged tier `free`, overflow locked | 4.3, 4.4, 4.8, 4.9, 7.1 |
| S3 (SAG 3) | Import-graph test could not pass: `main.py:10624` imports `scripts/refresh_vertex_data_store.py` (bucket literal `:12`) | file read; allowlisted by exact path for `:12` (Vertex AI Search client only, no data client, admin-only caller returns 503 first, no preview IAM); guarding rejected with reason; test matching rules made exact (AST calls; exact-equal bucket constants); plan-time re-walk of all 66 reachable modules; file added to §3 as not changed | 3, 4.11, 7.3 |
| E1 (Eric 7:57 PM ET) | RX was optional | RX marked **required before go-live** everywhere (header, §0, §0a, §2 rows, §4.9, §7.2, §9.4, §10 risks 14/15); new GL-2 blocks go-live until RX is deployed and verified; RX still needs Eric's own scoped YES under HOLD `41b8bd5f`; RX now protects `purchase_kind`; expected RX file SHA `a6c7bcdb…` derived and enforced; backup and rollback blocks unchanged (base SHA still `e650713b…`) | 0, 0a, 2, 4.9, 7.2, 9.3, 9.4, 10 |
| A1 (SAG advisory) | `checkout_pending` described as holding the session id before the session exists | real order stated: T1 reserves `checkout_pending` (state `creating`) and ensures `users/{uid}`, then Stripe create, then T2 stores `session_id`/`url`; failure handling for each step; `added_at` time-zone note | 4.1, 4.8, 7.1 |

### 2h. v1.9.2 record (CoS 94 REVISE): items fixed in v1.9.3

| ID | Finding | How v1.9.3 closes it | Section |
|---|---|---|---|
| D1 | Import-graph test fails on unguarded `numista_scraper/config.py:12` and `storage.py:15` | Guard `config.py:12` as `BUCKET_NAME = env_guard.bucket_for("numista-uploads-studio-9101802118-8c9a8", None)` (override None: production returns that exact bucket, never the preview bucket; preview returns the checked preview bucket, never a production bucket). Remove the `storage.py:15` fallback literal (fail closed; no bucket string). storage.py uses exactly `gcs_client.bucket(BUCKET_NAME)` (imported name; not wrapped again) | 3, 4.11, 7.3 |
| D1-claim | §7.3 said the allowlisted line was the only remainder after §4.11; false | Restated from the CoS 66-module walk: after v1.9.3 §4.11 only allowlisted `scripts/refresh_vertex_data_store.py:12` remains outside a `bucket_for` first argument | 7.3 |
| ADV1 | utf-8 text `ast.parse` raises on the BOM in `routes/sandbox_routes.py` and `routes/telemetry_routes.py` | Parse source as bytes (`ast.parse(path.read_bytes())`) or `utf-8-sig` | 7.3 |
| ADV2 | RX lib pre-check evidenced only at `a3d7dca2`; live main is not in the clone | Numbered step before the RX deploy: `git fetch origin main`; verify rev `9f04550a45fa4da082ba8948c2d89a521a90fa45`; git grep the same keys in that tree's `numista_mobile/lib`; any hit => STOP, RX blocked | 9.4 |
| ADV4 | Raw-case email source unstated (`entitlements.email` is lower-case) | Raw-case form is `firebase_auth.get_user(uid).email` | 4.3 |
| ADV5 | No resolvable email retried and never revoked, so the uid-doc tier survived | Clear `users/{uid}` first in its own transaction (present null defeats the merge), then retry 500 for the email doc(s); idempotent; not reported done | 4.3 |

## 3. File-by-file scope

All paths verified at `a3d7dca2`. The builder works in an isolated worktree (§9) and changes only these files.

| File | Change |
|---|---|
| `numista_backend/env_guard.py` (new) | data config, Stripe key check, guarded Firestore/Storage providers, bucket guard, Firebase Admin Auth-only init (§6.1) |
| `numista_backend/routes/payment_routes.py` | rewrite checkout/webhook/portal per §4.1-§4.4; `/subscription-status` calls `enforce_entitlement`, returns JSON-safe `coin_limit`/`unlimited`, `locked`, `restore_conflicts`; JSON-safe `power_user` allowance |
| `numista_backend/schemas/payment_schemas.py` | `tier: Optional[Literal[...]]` of purchasable keys (required when `beta_special` is false; ignored when true, v1.9.2 S1); `interval: Optional[Literal["month","year"]]` (same rule); `beta_special: bool = False`; `promo: Optional[str]` (max 64) |
| `numista_backend/scripts/refresh_vertex_data_store.py` | **not changed**; allowlisted by exact path in the import-graph test (§7.3, v1.9.2 S3) |
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
| `numista_backend/numista_scraper/storage.py`, `numista_scraper/scrapers.py`, `numista_scraper/config.py` | rows 19-21: `config.py:12` becomes `BUCKET_NAME = env_guard.bucket_for("numista-uploads-studio-9101802118-8c9a8", None)`; `storage.py:15` fallback literal removed; storage bucket expression is exactly `gcs_client.bucket(BUCKET_NAME)` (not `bucket_for(BUCKET_NAME)`) |
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
- **Purchase kind (v1.9.2 S1):** the server sets `purchase_kind = "beta"` when the request has `beta_special=true`, else `"subscription"`. It is never read from the client, never taken from any client-supplied metadata, and is written only by the server into the Session metadata. For `beta`, the request's `tier` and `interval` are **ignored** (never validated, used, priced or stored); the price is `BETA_SPECIAL_CENTS`, `mode="payment"`, and no `target_tier` is written. For `subscription`, `tier` and `interval` are required.
- Reject (HTTP 400) any subscription `tier` not in `PURCHASABLE` before any Stripe call. Reject `beta_special` (4xx) unless the server-counted coins are more than 100 (503 if the count cannot be read; never default to eligible), and reject with 409 if `entitlements/{uid}.beta_special_purchased` is already true (server-only document, §4.9). Coins are counted with the deduped `count_unique_coins` (§4.8).
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
- `client_reference_id=uid`; subscriptions: `metadata={"user_uid": uid, "user_email": email, "purchase_kind": "subscription", "target_tier": tier, "interval": interval, "discount_kind": kind}` and also `subscription_data={"metadata": {same}}` (so later invoice/subscription events carry uid, email, kind and tier); Beta Special: `metadata={"user_uid": uid, "user_email": email, "purchase_kind": "beta", "discount_kind": "none"}` (no `target_tier`, no `interval`). `email` is the lower-cased email from the verified token (v1.9.2 S1/S2). Idempotency key for Beta: `checkout_idempotency_key(uid, "beta_special", "once", bucket)`.
- Non-US billing addresses are allowed (Eric, 10 Nov 5:14 PM ET; supersedes the earlier US-only answer). Set `billing_address_collection="auto"`. Stripe Tax stays off. USD pricing for all buyers; foreign tax/legal obligations are not assessed here (open risk, §10).
- Idempotency: pass `idempotency_key=checkout_idempotency_key(...)` as a request option. One active checkout per user, on the server-only `entitlements/{uid}` document (§4.9), in this order (v1.9.2 A1; the Stripe session id cannot exist before step 2): (1) transaction T1, before any Stripe call: if an unexpired `checkout_pending` exists, return its stored session URL if it has one, else 409; otherwise write `checkout_pending={state: "creating", expires_at}` (and ensure `users/{uid}`, next bullet); (2) call Stripe `checkout.Session.create` with the Checkout `expires_at` set to now + 1860 s; (3) transaction T2: set `checkout_pending.session_id` and `checkout_pending.url` from the created Session. If step 2 fails, `checkout_pending` is deleted and the route returns 502 (today's Stripe-failure code). If step 3 fails, the route returns 503; the Session then simply expires unused, or, if the buyer still pays, the grant proves the uid through Firebase Auth (§4.3). `checkout_pending` is cleared on `checkout.session.completed`, `checkout.session.expired` and `checkout.session.async_payment_failed`, and is ignored once its `expires_at` has passed.
- **Account doc at create (v1.9.1 D1):** in transaction T1 above (the one that first writes `checkout_pending`, before the Stripe call; wording corrected in v1.9.2 A1), the server ensures `users/{uid}` exists with `set({}, merge=True)` (Admin SDK, guarded client; uid from the verified token only). No field is written, so no entitlement field (`stripe_tier`, `tier`, `beta_tester`, `admin`, `power_user`, `creation_timestamp` or any other) is touched, and every existing field on that doc (e.g. the sort preference the app writes at `numista_mobile/lib/screens/my_collection_screen.dart:359-362`) is preserved. Reason: many accounts have only `users/{email}` (`numista_mobile/firestore.rules:69-73`); subcollection writes under `users/{uid}/…` do not create the parent doc; the grant writes `users/{uid}` (§4.3). If this write fails, the create returns 503 and no Stripe session is created.
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
- `price_cents` is recomputed server-side: for `metadata.purchase_kind == "subscription"` from `metadata.target_tier` and `interval`; for `"beta"` it is `BETA_SPECIAL_CENTS` (v1.9.2 S1) (never from the event amount). The plan does not compute the discounted total itself, so Copper (2499.5) and Silver (4499.5) half-cent results are accepted whichever way Stripe rounds (tolerance 1 cent, checked against `amount_subtotal`). Beta Special uses 3000 with kind `none`.
- `session_created` is the Session's `created` (epoch seconds) from the re-retrieved Session; for kind `xmas` a missing value fails closed (A3).
- The Session is re-retrieved with `expand=["total_details.breakdown"]` to read the applied coupon id. If the coupon id cannot be read when a discount was expected, do not grant: mark the event `failed` and log. The Stripe response shape (`total_details.breakdown.discounts[].discount.coupon.id`, and the promotion-code coupon field) is not verified in this plan; it is recorded in the gated sandbox step (§8) and `decide_grant` fails closed if it differs (Eric accepted).
- `metadata.purchase_kind` must be `"subscription"` or `"beta"`; missing or anything else → no grant, event `failed`, log (fail closed, v1.9.2 S1). `beta` also requires Session `mode == "payment"` and `amount_subtotal == 3000`; `subscription` requires `mode == "subscription"`; a mismatch → no grant, `failed`. For `beta`, any `target_tier` in metadata is ignored. For `subscription`, the tier from metadata must be in `PURCHASABLE`; otherwise no grant. **A tier is never defaulted** (today's `"pro"` default at `numista_backend/routes/payment_routes.py:221` is removed).
- User resolution for `checkout.session.completed` and async events: `client_reference_id`, then `metadata.user_uid`. **No email fallback** (today's `payment_routes.py:210` fallback is removed). If no `users/{uid}` doc exists (v1.9.1 D1; normally impossible after the create-time write above, e.g. a session made before D1 shipped or a doc deleted since): the grant still proceeds when the uid is proven by `entitlements/{uid}.checkout_pending.session_id == session.id`, or else by `firebase_auth.get_user(uid)` succeeding; the grant transaction's merge writes then create `users/{uid}`. Only if neither proves the uid: log, set `retry`, return 500 (never `done`, never a grant to an unproven uid). A paying customer whose account exists therefore always gets access.
- **Grant transaction, `purchase_kind == "subscription"`** (single Firestore transaction on the guarded client):
  - `users/{uid}`: set `stripe_tier` (already a server-only key, `numista_mobile/firestore.rules:85-88`), `subscription_status="active"`, `grace_period_until=None`.
  - `entitlements/{uid}` (server-only, §4.9): set `stripe_subscription_id`, `stripe_customer_id`, `email` (from `metadata.user_email`, v1.9.2 S2); clear `checkout_pending`.
  - `stripe_customers/{customer_id}` = `{uid}` (server-only top-level collection, §4.9).
  - Ledger `stripe_payments/{payment_intent_id}` = `{uid, kind: "subscription", tier, subscription_id, granted: true}` **only when `payment_intent` is present**; for subscription sessions where it is None at completion, skip it and rely on `invoice.paid` (A1). The ledger `kind` is always copied from the server-set `metadata.purchase_kind`, never inferred.
- **Grant transaction, `purchase_kind == "beta"`** (v1.9.2 S1): writes **only** the Beta fields in `entitlements/{uid}` (`beta_special_until`, `beta_special_purchased`, `email` from `metadata.user_email`, and clears `checkout_pending`) and the ledger `stripe_payments/{payment_intent_id}` = `{uid, kind: "beta", granted: true}`. It **never** writes `stripe_tier`, `subscription_status` or `grace_period_until` on any user doc, and never writes `stripe_subscription_id` or `stripe_customers`. A Beta Session is `mode="payment"`, so its `payment_intent` is expected at completion; if it is missing after re-retrieval, set `retry`, return 500 (the ledger is needed for refunds; never `done` without it). The unlimited period comes only from `entitlements/{uid}.beta_special_until` via `effective_limit` (§4.8); any pre-existing `stripe_tier` (e.g. Copper) is left exactly as it was.
  - After commit (either kind), call `unlock_user_coins(uid, email)` up to the new effective limit (§4.8), so an upgrade returns previously locked coins to their original folders. If unlock raises, the event is set `retry` and returns 500 (the grant already committed is idempotent on redelivery).
- **Later subscription events** (`invoice.paid`, `customer.subscription.updated`, `customer.subscription.deleted`) have no session fields: uid comes from `stripe_customers/{customer}`; if missing, retrieve the subscription by id and use `subscription.metadata.user_uid`; if still unknown, set `retry`, return 500. Tier from `subscription.metadata.target_tier`, validated against `PURCHASABLE`; missing/invalid → change nothing, `failed`, log. If `subscription.metadata.purchase_kind` is present and is not `"subscription"`, change nothing, `failed`, log (v1.9.2 S1; Beta is never a subscription).
  - `invoice.paid`: if `status == "paid"`, re-affirm `stripe_tier` and write a ledger entry for the invoice's payment intent (newer API versions may nest it under `invoice.payments`; unverified shape, recorded in §8, fail closed if absent).
  - `customer.subscription.updated`: `active`/`trialing` set the tier; `canceled`/`unpaid` are handled as a cancel; `past_due` only logs.
  - `customer.subscription.deleted`: cancel (below).
  - `invoice.payment_failed`: keep today's 3-day grace bookkeeping (`payment_routes.py:227-232`); no lock, no revoke.
- Pytest includes an `invoice.paid` and a `subscription.updated` event with no session fields, resolving through the map, then the subscription metadata, then failing closed.
- `checkout.session.async_payment_succeeded` grants; `async_payment_failed` grants nothing and clears `checkout_pending`; `checkout.session.expired` clears `checkout_pending`.
- **Beta Special:** re-check coins > 100 at fulfillment with `count_unique_coins` (§4.8). If 100 or fewer, or if `entitlements/{uid}.beta_special_purchased` is already true: do not grant and **automatically refund** (backstop; the primary control is the block at create). Backstop: `stripe.Refund.create(payment_intent=<pi from session>, idempotency_key="refund_" + session_id)`; log; ledger entry with `granted: false`; record `beta_refund_issued` on the event. If the count cannot be read at fulfillment, set `retry` and return 500 (never grant on an unknown count). On grant, in the Beta grant transaction above: `entitlements/{uid}.beta_special_until = now + relativedelta(months=6)` stored as a Firestore Timestamp (tz-aware UTC datetime), `beta_special_purchased = true` (permanent; refunds and expiry never clear it). No tier is written (v1.9.2 S1); when `beta_special_until` passes, the user's effective limit is simply their own tier again (Free 10 unless they also pay for a subscription) and overflow locks lazily (§4.8). Expiry changes no tier because Beta never set one.
- **Revoke of a paid tier (`revoke_paid_tier(db, uid, email)`, v1.9.2 S2; v1.9.3 ADV4/ADV5):** lower-cased `email` comes from `entitlements/{uid}.email`, else `firebase_auth.get_user(uid).email`. The raw-case form, when it differs, comes only from `firebase_auth.get_user(uid).email` (the Auth record); `entitlements/{uid}.email` is the lower-cased value stored at grant from `metadata.user_email` and is not a raw-case source (v1.9.3 ADV4). If `get_user` raises but `entitlements.email` is present, write the lower-cased email doc and skip raw-case (do not fail the revoke for a missing raw-case). When an email is resolved, in one transaction, `set({"stripe_tier": None, "subscription_status": "canceled", "grace_period_until": None}, merge=True)` on **both** `users/{uid}` and `users/{email}` and, if the raw-case form differs, on that doc too. The `None` is written as a present null, not a field delete, so the `load_entitlement_profile` merge (`profile = dict(email_doc); profile.update(uid_doc)`, §4.8) can never fall back to a paid value left on the email doc; today's webhook writes `stripe_tier` to `users/{email}` whenever the event has no uid (`numista_backend/routes/payment_routes.py:206-213`, `:220-225`, `:233-238`). If neither email is available (v1.9.3 ADV5): first, in its own transaction, write that same present null on `users/{uid}` only (the present null alone defeats the merge), then set `retry` and return 500 for the email doc(s) (never a partial revoke reported `done`). Idempotent: repeating the uid null is the same merge write; a later retry that resolves an email applies the same null to those email doc(s). Revoke-only fallback for legacy subscriptions with no resolvable uid: if the event's Stripe customer's email is present (unverified shape, recorded in §8), null `stripe_tier` on `users/{email}` only when that doc's `stripe_customer_id` equals the event's customer (written there by today's webhook, `payment_routes.py:217-218`); this can only remove access, never grant it. `tier` and the comp flags are not touched. Used by cancellation, full refund and lost dispute (§4.4); never by Beta expiry or a Beta refund.
- **Cancellation** (`subscription.deleted`, or `updated` to `canceled`/`unpaid`): only if `entitlements/{uid}.stripe_subscription_id` equals the cancelled subscription, call `revoke_paid_tier(db, uid, email)` (v1.9.2 S2; was: clear `users/{uid}.stripe_tier` only). Never change `beta_tester`, lifetime, or users covered by the legacy `creation_timestamp < 1795669200000` rule (`numista_backend/tier_gatekeeper.py:140-152`; they outrank `stripe_tier`, rule kept). Then call `lock_overflow_coins(uid, email)` to the **effective** limit (§4.8; comped users lock nothing). Never a hard-coded Free 10 (today's `payment_routes.py:234-238` sets `stripe_tier="free"` and locks to Free; replaced).
- **Billing portal** (`payment_routes.py:82-123`): the customer id is read from server-only `entitlements/{uid}.stripe_customer_id`, and used only if `stripe_customers/{customer_id}.uid == uid`. The client-writable `users/{id}.stripe_customer_id` read at `payment_routes.py:102-105` is no longer trusted (a user could otherwise point the portal at another customer). If none: today's lookup/create by the token email (`:107-114`), then write both server-only docs.
- Existing `estate` users (legacy $29/yr): no automatic change; their `stripe_tier` stays until their subscription ends; Gold becomes unlimited for them. Open question 3.

### 4.4 Refund/dispute (B5, D6, D7) — unchanged from v1.7 except the server-only subscription id

Every grant with a payment intent and every paid invoice writes `stripe_payments/{payment_intent_id}` with `{uid, kind, tier, subscription_id, granted}` (`kind` copied from the server-set `metadata.purchase_kind`; Beta entries carry no `tier`, v1.9.2 S1). Handlers map `charge.payment_intent` through this ledger.

- `charge.refunded`:
  - Partial refund (`amount_refunded < amount`): log only, access kept (Eric decided).
  - Full refund: look up the ledger by payment intent.
    - `kind == "beta"` and `granted`: set `entitlements/{uid}.beta_special_until` to now (ends the unlimited period), keep `beta_special_purchased`, **do not touch `stripe_tier`**; then `lock_overflow_coins(uid, email)` to the effective limit.
    - `granted == false` (backstop or never-granted purchase): revoke nothing.
    - `kind == "subscription"`: if `entitlements/{uid}.stripe_subscription_id` equals the ledger's `subscription_id`, call `revoke_paid_tier(db, uid, email)` (both user docs, §4.3, v1.9.2 S2); then lock to the effective limit.
    - No ledger entry: log, set the event `failed` with a review flag; change nothing.
- `charge.dispute.created`: log and set `entitlements/{uid}.dispute_review = true`. **No revoke.**
- `charge.dispute.closed`: status `lost` revokes exactly as the full-refund rules above; status `won` does nothing.
- Coins are never deleted. Lock timing: only on cancel, full refund, lost dispute (effective tier), plus the expiry/reconcile rule in §4.8. Never at checkout create.
- Pytest: full refund of a Beta purchase (ends Beta, leaves `stripe_tier`); backstop refund of a Copper subscriber's ungranted Beta (no revoke); full refund of a subscription invoice (clears tier on both user docs, locks); dispute created (no revoke); dispute lost (revokes on both user docs); dispute won (nothing); partial refund (nothing). v1.9.2 S1/S2 cases are listed in §7.1.

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
- **Lock order (OPEN QUESTION 13 for Eric, not a decision):** keep today's direction from `tier_gatekeeper.py:327-334` — sort unique coins oldest first, keep the first `limit` visible, lock the rest (the newest). **Sort time (v1.9.1, CoS advisory 1):** `to_epoch(created_at)`; if that is missing or unparseable, `to_epoch(added_at)`; if that is also missing or unparseable, epoch 0 (treated as oldest, so kept visible, and never skipped: A2). `created_at` is what the server writes (e.g. `firestore.SERVER_TIMESTAMP` at `numista_backend/main.py:2747`) and what today's lock orders by (`tier_gatekeeper.py:327`); `added_at` (an ISO-8601 string, no `created_at`) is what the app's direct coin creates write: the roll wizard (`numista_mobile/lib/widgets/roll_entry_dialog.dart:374-384`, field at `:379`) and wishlist "found" (`numista_mobile/lib/screens/wishlist_screen.dart:979-984`, field at `:983`). Ties broken by coin id. For a coin with two copies, its sort time is the earlier of the two. The same value is stored as `sort_epoch` on the locked doc. Note (v1.9.2 A1): Dart `DateTime.now().toIso8601String()` writes the device's local time with **no time-zone offset**, so `to_epoch` reads `added_at` as UTC; ordering between an `added_at` coin and a `created_at` coin can be off by up to the device's UTC offset (hours). This only affects which coins lock first (Q13), never the count.
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

  Beta Special never sets `stripe_tier` (v1.9.2 S1): its unlimited period comes only from `entitlements/{uid}.beta_special_until` in `effective_limit`, and after expiry or a Beta refund the limit is `get_user_tier(profile)`'s own value. Revokes write a present null on both user docs (§4.3), so this merge never resurrects a revoked paid tier (v1.9.2 S2).

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
  - **Own lookup** (value equals the token uid or email; admin or not): `enforce_entitlement` on the caller's own token keys `{uid, email}`, then the same fields as today with `coin_count` = deduped visible coins, `coin_limit` JSON-safe plus `unlimited`, and `locked`, `restore_conflicts`, plus `beta_special_active` (bool) and `beta_special_until` (ISO-8601 UTC or null) from `entitlements/{uid}` (v1.9.2 S1: a Beta buyer's `stripe_tier` stays their own tier, e.g. `free`, so Beta status is reported by these two fields, never via `stripe_tier`); a read error → 503.
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
| `beta_special_until` (Timestamp), `beta_special_purchased`, `stripe_subscription_id`, `stripe_customer_id`, `checkout_pending`, `dispute_review`, `email` (v1.9.2 S2) | `entitlements/{uid}` (new) | none |
| locked coins | `locked_coins/{owner_key}/coins/{coin_id}` (new) | none |
| customer → uid map | `stripe_customers/{customer_id}` (new) | none |
| payment ledger (`kind` = server-set `purchase_kind`, v1.9.2 S1) | `stripe_payments/{payment_intent_id}` (new) | none |
| event claims | `stripe_events/{event_id}` (exists, `payment_routes.py:199`) | none |

  A repo-wide grep at `a3d7dca2` finds no existing use of the names `entitlements`, `locked_coins`, `stripe_customers` or `stripe_payments` as collections in the backend, and no `match` block for them in the rules, so nothing else reads or writes them and they are denied to clients today.
- **Users can never write their own entitlements:** the only entitlement fields on the user doc (`stripe_tier`, `tier`, `beta_tester`, lifetime, `admin`) stay server-only exactly as today; every new entitlement field is in a client-denied document. Nothing in v1.9 widens any client write.
- **Owner list queries keep working:** the coin rules (`:40-67`) and all client queries are unchanged, so the v1.8 lock-out cannot happen.
- **Pre-existing gaps found (not caused by NET-827; recorded, not fixed here):** `creation_timestamp` (read by `tier_gatekeeper.py:146-152` to grant `family_estate`) and `power_user` (read at `tier_gatekeeper.py:238`) are client-writable on the user doc today; neither is written anywhere in `numista_mobile/lib` or the backend runtime. They are open risks 14 and 15 (Section 10) and are closed by the rules step RX (§9.4), which is required before go-live (v1.9.2 E1) and needs its own production YES.
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
| 18 | `services/canon_sync_service.py:10-11,21-26` | `firestore.Client` + `storage.Client` on production, bucket `studio-9101802118-8c9a8-uploads`; imported at `main.py:10623` | `get_gcp_clients()` returns `env_guard.get_firestore(), env_guard.get_storage()`; bucket via `bucket_for`; route `main.py:10615-…` (`/api/admin/brain/sync_canon`) returns 503 in preview (it also calls `scripts/refresh_vertex_data_store.py`, bucket at `:12`, which is not run in preview); the `require_production` check is the first statement of the handler, before the function-level imports at `main.py:10623-10624` (v1.9.2 S3) |
| 19 | `numista_scraper/storage.py:15-16,22-38` | module-level Admin init on production, `firestore.client()`, `gcs_storage.Client(project=…)`, `bucket = gcs_client.bucket(BUCKET_NAME)` (`:38`); `:15` is the `except ImportError` fallback literal `BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"` | `db = env_guard.get_firestore()`; `gcs_client = env_guard.get_storage()`; delete the `:15` fallback literal and do not assign any bucket string in that `except` (fail closed; do not call `bucket` unless `BUCKET_NAME` was imported from `config`); `bucket = gcs_client.bucket(BUCKET_NAME)` using that imported name only (already one `bucket_for` result, row 21); do not call `bucket_for` again (not `bucket_for(BUCKET_NAME, None)`); no Admin init |
| 20 | `numista_scraper/scrapers.py:146,705,731` | `firestore.client()` (Admin default app) | `env_guard.get_firestore()` |
| 21 | `numista_scraper/config.py:12,117-124,186-193` | `:12` `BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"`; Admin `initialize_app()` + `_fs.client()` | `:12` `BUCKET_NAME = env_guard.bucket_for("numista-uploads-studio-9101802118-8c9a8", None)` (literal is the first argument; override env is None, so production returns that exact bucket and cannot be pointed at the preview bucket; preview returns the checked non-production preview bucket); `:117-124,186-193` `env_guard.get_firestore()`; no Admin init |
| 22 | Scraper entry points `main.py:3334-3341` (deep-dive auto-scraper trigger, user-reachable), `main.py:10192` (cron scraper), `main.py:10457-10463` (`/api/scraper/scrape-url`) | start `numista_scraper` | in preview: the deep-dive trigger is skipped (no scrape thread), the two routes return 503 |

`numista_scraper` gets its clients from `env_guard` (a leaf module with no app imports), not from `routes.deps`, so the scraper package does not depend on the app (harvest H6 note).

**AI/search clients (not data stores; unchanged):** `routes/deps.py:29`, `main.py:436`, `main.py:2040,4870` (Document AI), `services/vector_rag_service.py:37-39`, `routes/cert_routes.py:403,421`, `services/variety_detector.py:63`, `numista_scraper/grading_advisor.py:9,12`, `vertex_search/coin_search_endpoint.py:24`, `morgan_knowledge.py:228`. In preview they point at the production project, where the preview service account has zero roles (PV-4), so calls fail with permission denied (fail closed). They read no user data from production Firestore or Storage. Those features are out of NET-827 test scope.

**Not part of the preview service:** `scan_service/main.py:58,188-194` and `scan_service/estate_pdf_builder.py:313-317` belong to the separate scan service; `main.py` imports only the pure `scan_service/collection_inventory.py` (`main.py:3081`), whose header says it must not import `main.py`. The ~400 standalone scripts in `numista_backend/` (e.g. `upload_*.py`, `_scripts/`) are not imported by `main.py` and are not in the import-graph test.

**Bucket guard rule:** production bucket names found in code: `numista-uploads-studio-9101802118-8c9a8` (`main.py:342`, `numista_scraper/config.py:12`), `studio-9101802118-8c9a8-uploads` (`routes/import_routes.py:21`, `routes/feedback_callable_route.py:37`, `routes/estate_routes.py:20`, `services/canon_sync_service.py:11`, `main.py:12281`), `numista-reference-library` (`main.py:9607`), `studio-9101802118-8c9a8.firebasestorage.app` (`numista_mobile/lib/firebase_options.dart:55,64,73`) and `numista-uploads-studio-9101802118-8c9a8.firebasestorage.app` (`scan_service/estate_pdf_builder.py:317`). In preview the guarded wrapper refuses all of them, plus any name containing `studio-9101802118-8c9a8`. v1.9.3: the `numista_scraper/config.py:12` occurrence is that name as the first argument of `env_guard.bucket_for("numista-uploads-studio-9101802118-8c9a8", None)`, not a bare assignment; the `numista_scraper/storage.py:15` fallback literal is removed and is not a remaining name.

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

`tests/test_net827_checkout.py` (v1.7 list, unchanged): allowlist rejects `power_user`, `sovereign`, `family_estate`, `bogus` (400, Stripe `create` not called); price table; subtotal mismatch / unpaid / uncoupon'd discount → no grant; Christmas coupon attached on annual in-window only (before start, after end, monthly: none); half-cent Christmas totals for Copper and Silver accepted; F&F valid/invalid promo; no stacking; no-user → event not `done`; claim lease cases; invoice and subscription events without session fields; refund and dispute cases in §4.4; Beta at 100 coins blocked at create (Stripe `create` not called), 101 allowed; (v1.9) Beta eligibility counts locked coins too: 60 visible + 50 locked = 110 → allowed; 60 visible + 40 locked = 100 → blocked; the same coin id visible and locked counts once; second Beta purchase after a refund blocked; backstop refund called once (`stripe.Refund.create` mocked); limits cases in §4.5. Added in v1.9.2 (S1): a free user sends `tier=estate` with `beta_special=true` → Session `mode="payment"`, 3000 cents, metadata `purchase_kind="beta"` and no `target_tier`; `checkout.session.completed` → `stripe_tier` absent on both `users/{uid}` and `users/{email}`, `subscription_status` not written, `beta_special_until` set, `/subscription-status` shows `stripe_tier="free"`, `unlimited: true`, `beta_special_active: true`; after `beta_special_until` passes → effective tier free, limit 10, overflow locked; after a full refund of the Beta payment → Beta ended, still no paid tier, limit 10, overflow locked; an existing Copper (`pro`) subscriber buys Beta then refunds it → `stripe_tier` stays `pro`; a Beta Session whose metadata also carries `target_tier=estate` (simulated) → ignored, no tier; `purchase_kind` missing, unknown, or inconsistent with `mode`/amount → no grant, `failed`; a subscription event whose `subscription.metadata.purchase_kind` is not `subscription` → no change. Added in v1.9.2 (S2): `stripe_tier="numismatist"` only on `users/{email}` (legacy shape, no uid field) → subscription full refund, lost dispute and cancellation each leave `stripe_tier` as a present null on both docs and the merged `load_entitlement_profile` tier is `free`, overflow over 10 locked; the same with the tier on both docs; with the raw-case email doc also present → nulled too; email unknown (no `entitlements.email`, `get_user` raising) → `retry`, 500, no partial revoke reported `done`; legacy cancel with no uid but a matching `users/{email}.stripe_customer_id` → that doc nulled; non-matching customer id → nothing changed; `beta_tester`, lifetime and `tier` untouched by a revoke; a Beta refund never calls `revoke_paid_tier`. Added in v1.9.2 (A1): Stripe create failing after T1 → `checkout_pending` deleted, 502; T2 failing after the Session exists → 503, and a later completed event for that Session still grants via the Firebase Auth uid proof. Added in v1.9.1 (D1): a user with only `users/{email}` (no `users/{uid}`) creates a Silver checkout → `users/{uid}` exists afterwards with no fields written by the create; then `checkout.session.completed` → granted (`stripe_tier` = `numismatist` on `users/{uid}`, event `done`); an existing `users/{uid}` with `default_sort_field` keeps it after the create (merge); the create-time write fails → 503 and Stripe `create` not called; `users/{uid}` deleted between create and webhook while `checkout_pending.session_id` matches → granted and the doc recreated; same with no `checkout_pending` but `firebase_auth.get_user` succeeding → granted; a uid with no doc, no matching `checkout_pending` and `get_user` raising → no grant, `retry`, 500; the same three grant cases for Beta Special and F&F. Added in v1.9.1 (admin): admin token, other uid → the field set above with `admin_view: true`, `reconciled: false`, and zero writes recorded by the fake (no coin moved even when that user is over the limit); admin token, own uid → reconcile runs; non-admin, other uid → 403. Added in v1.9: Christmas coupon with `session.created` missing → no grant (fail closed); a client-supplied `stripe_customer_id` on `users/{id}` is ignored by the billing portal, which uses only `entitlements/{uid}` verified by `stripe_customers/{cus}.uid == uid` (another user's customer id → 403); the checkout route is `POST /api/stripe/create-checkout-session` (route-table assertion).

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

RX variant (required before go-live, §9.4): the same file run against the RX candidate rules adds: owner create/update coin with `locked_pending_upgrade` → fails; owner set `power_user`, `creation_timestamp`, `stripe_customer_id`, `stripe_subscription_id`, `beta_special_until`, `beta_special_purchased`, `purchase_kind` on own user doc → fails; cases 1-8 still pass; a new user's first create of their profile without those keys still succeeds.

### 7.3 Static import-graph test (local) and HTTP checks against the preview (no sign-in on p7-gate)

`tests/test_no_unguarded_clients.py` (static import graph; harvest H9 with the v1.8 gaps closed): AST walk from `main.py` following every import, module-level **and inside functions** (so `brain_processor`, `services.canon_sync_service`, `numista_scraper.*`, `services.transfer_service` are included). Fails if any module other than `env_guard.py` contains `firestore.Client(`, `firestore.client(`, `storage.Client(`, `gcs.Client(`, `_gcs.Client(`, `gcs_storage.Client(` or `firebase_admin.initialize_app(`, or a string literal equal to a production bucket name outside an `env_guard.bucket_for(...)` call's first argument. Allowlisted (documented, AI/search only): the rows under "AI/search clients" in §4.11, and (v1.9.2 S3) `scripts/refresh_vertex_data_store.py` by exact path, for its bucket literal at `:12` only. Justification (file read at `a3d7dca2`): it builds no Firestore or Storage client and no Firebase Admin app; its only client is `discoveryengine.DocumentServiceClient()` (`:36`), the same Vertex AI Search family as the already-allowlisted `vertex_search/coin_search_endpoint.py:24` and `morgan_knowledge.py:228`; the bucket name (`:12`) is used only to build a `gs://` URI string (`:13`) handed to a Vertex import request (`:37-49`), so it reads no user data through our code; its only importer is the admin-only `/api/admin/brain/sync_canon` (`main.py:10615-10624`, `require_admin_user` at `:10616`), which returns 503 in preview before that import (row 18); and in preview the service account has no role on the production project (PV-4), so even a call would fail closed. Guarding it with `bucket_for` was rejected: production would be unchanged, but in preview it would aim the production data store's import at the preview bucket, which is wrong. Matching rules (so the test passes exactly as written): source is parsed as bytes (`ast.parse(path.read_bytes())`) or with encoding `utf-8-sig`, because `routes/sandbox_routes.py` and `routes/telemetry_routes.py` start with a UTF-8 BOM (a utf-8 text read leaves U+FEFF and `ast.parse` raises); forbidden constructors are matched as AST `Call` nodes by dotted or bare name (`firestore.Client`, `firestore.client`, `storage.Client`, `gcs.Client`, `_gcs.Client`, `gcs_storage.Client`, `_fs.client`, and `initialize_app` whether called as `firebase_admin.initialize_app` or imported bare), so text inside docstrings does not count (`brain_processor.py:311` and `services/canon_sync_service.py:90` are docstrings); a bucket literal is an AST string constant **equal** to a production bucket name, so URLs that merely contain one (`services/us_mint_catalog_service.py:39-62`) do not count. A plan-time walk of the `main.py` import graph at `a3d7dca2` (66 modules, module-level and function-level imports; CoS AST walk) found production-bucket string constants only at `main.py:342`, `main.py:9607`, `main.py:12281`, `numista_scraper/config.py:12`, `numista_scraper/storage.py:15`, `routes/estate_routes.py:20`, `routes/feedback_callable_route.py:37`, `routes/import_routes.py:21`, `scripts/refresh_vertex_data_store.py:12` and `services/canon_sync_service.py:11` (`numista_scraper/url_scraper.py` and `agent.py` are not in the graph). After the v1.9.3 §4.11 changes, `main.py:342`, `main.py:9607`, `main.py:12281`, `numista_scraper/config.py:12`, `routes/estate_routes.py:20`, `routes/feedback_callable_route.py:37`, `routes/import_routes.py:21` and `services/canon_sync_service.py:11` are each the first argument of `env_guard.bucket_for(...)`, and the `numista_scraper/storage.py:15` fallback literal is removed; the only production-bucket literal remaining outside a `bucket_for` first argument is the allowlisted `scripts/refresh_vertex_data_store.py:12`. Excluded (not imported by `main.py`): `scan_service/` except `collection_inventory.py`, standalone scripts. The test must find the 22 inventory rows' modules in its walk (assert the module set contains them), so a dropped module fails the test.

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
- **GL-2 (v1.9.2 E1)** RX (§9.4) is deployed under its own scoped Eric YES (HOLD `41b8bd5f`) and its post-deploy verification has passed (live rules SHA-256 = `a6c7bcdb4f320ea2bf323e94e3481e9470ca708c1975a0897f8bce6a2786f2b5`). No live key, live webhook or backend go-live step runs before GL-2 passes; if RX is rolled back, go-live stops until RX is re-deployed and verified.
- LK-1 Eric creates live products/prices matching §0 (the server uses `price_data`, so these are for reporting only).
- LK-2 Eric creates the live F&F coupon with its promotion code (max 500 redemptions) and, ahead of the start, the live Christmas coupon (50% off, `once`, `redeem_by` 1798261199). A coupon has no inactive state, so the control is the server gate plus withholding the coupon id from the service env until LK-8.
- LK-3 Eric stores the live secret key in Secret Manager under a name chosen then (UNKNOWN now), mounted only on `numista-backend` (the production Cloud Run service) under the later go-live gate.
- LK-4 Eric creates the live webhook endpoint (`https://<production backend>/api/stripe/webhook`, same event list as PV-2b) with its own signing secret, stored as a separate secret.
- LK-5 Code mode check: `env_guard.check_stripe_key` refuses to start when the key prefix (live vs test) does not match `STRIPE_EXPECTED_MODE` (set at GL-1, then `live`).
- LK-6 Confirm no test webhook secret is mounted on the production service.
- LK-7 Smoke test with a real card only under separate Eric YES.
- LK-8 At or after 1795669260, Eric sets the Christmas coupon id in the production service env (the server gate still enforces the window).

### 9.4 Rules hardening RX — REQUIRED before go-live (PRODUCTION change; not part of NET-827's preview; v1.9.2 E1; CoS direction 3; harvest G1/G3)

**Status: REQUIRED before go-live (v1.9.2 E1: Eric, 7:57 PM ET 10 Nov, "Definitely fix the 'Free Limits' bug"); not needed for, and not run in, the NET-827 preview.** It closes the pre-existing open risks 14 and 15 (users setting `creation_timestamp` or `power_user` on their own user doc) and adds defence in depth. Go-live (GL-1/LK steps, §9.3) does not proceed until RX is deployed and its post-deploy verification has passed (GL-2). It is a **production change** (the Firestore rules are shared by every environment that uses project `studio-9101802118-8c9a8`; the preview's test Firestore has its own rules). It runs only under HOLD `41b8bd5f` being lifted, with **its own scoped Eric YES** naming: "RX rules change, file SHA-256 <new SHA>, backup SHA-256 e650713b…2f9c86, rollback block 9.4-R". Sequenced **before** the v1.9.2 backend go-live deploy: it only removes client permissions that neither the current app nor the current backend uses (pre-check below; the backend writes through the Admin SDK, which rules do not apply to), so it is safe ahead of the backend and leaves no window in which the new limits can be bypassed. It is never bundled with any other deploy. Expected RX file (the current file with exactly the hunks below applied, LF line endings): SHA-256 `a6c7bcdb4f320ea2bf323e94e3481e9470ca708c1975a0897f8bce6a2786f2b5`, 18,508 bytes (computed from `e650713b…` at plan time); the YES quotes this SHA, and the deploy and verify blocks refuse any other value.

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
+              'beta_special_until', 'beta_special_purchased', 'locked_pending_upgrade', 'purchase_kind'];
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

Every change only removes client permissions (adds conditions or exclusions) or adds explicit denies; no rule grants anything new. Users still create and update their own profile doc (needed by the app) but can never write any entitlement or limit field on it (direction 3: users never write their own account entitlements). Pre-checks before the YES: (1) `git grep -n "creation_timestamp\|power_user\|stripe_customer_id\|stripe_subscription_id\|beta_special\|locked_pending_upgrade\|purchase_kind" -- numista_mobile/lib` returns nothing (true at `a3d7dca2`; re-run at RX time; any match makes RX BLOCKED until reviewed); (2) the builder/Eric runs this against the code actually live in production before the RX deploy (`origin/main` `9f04550a45fa4da082ba8948c2d89a521a90fa45`, which is NOT in the box clone; do not skip this because the plan did not read that tree): `git fetch origin main`; verify `git rev-parse origin/main` equals `9f04550a45fa4da082ba8948c2d89a521a90fa45` (any other rev => STOP, RX blocked); `git grep -n "creation_timestamp\|power_user\|stripe_customer_id\|stripe_subscription_id\|beta_special\|locked_pending_upgrade\|purchase_kind" 9f04550a45fa4da082ba8948c2d89a521a90fa45 -- numista_mobile/lib`; any hit => STOP, RX blocked; (3) §7.2's RX variant passes in the emulator. A CI-style check confirms the diff: `git diff --stat` shows only `numista_mobile/firestore.rules` and the test file, and `git diff -U0` contains only the hunks above.

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
if ($rxFile.ToLower() -ne 'a6c7bcdb4f320ea2bf323e94e3481e9470ca708c1975a0897f8bce6a2786f2b5') { throw 'YES SHA is not the expected RX file SHA a6c7bcdb...; STOP' }
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
if ($rxFile.ToLower() -ne 'a6c7bcdb4f320ea2bf323e94e3481e9470ca708c1975a0897f8bce6a2786f2b5') { throw 'YES SHA is not the expected RX file SHA a6c7bcdb...; STOP' }
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
14. **OPEN RISK (pre-existing, not caused by NET-827):** `creation_timestamp` on the user doc is client-writable and grants `family_estate` when below 1795669200000 (`numista_backend/tier_gatekeeper.py:146-149`). A user could set it to get 2,500 coins free. Closed by RX (§9.4), which is **required before go-live** (v1.9.2 E1) and is a production change needing its own YES. PV-0 records how many users have it.
15. **OPEN RISK (pre-existing):** `power_user: true` on the user doc is client-writable and bypasses all limits (`numista_backend/tier_gatekeeper.py:238`, kept by `effective_limit`). Closed by RX, required before go-live (v1.9.2 E1). PV-0 records how many users have it.
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

## 12. Diff summary vs v1.9.1 (v1.9.2; only these changes)

1. **Header:** version label v1.9.2; attempt 6 of 10, Code Writing try 3 of 4; base v1.9.1 (SHA `ec9c50b4…`).
2. **S1 (Beta never sets a tier):**
   - §3: schema row; `tier`/`interval` optional for Beta.
   - §4.1: server-set `purchase_kind`; Beta metadata without `target_tier`; `user_email` in metadata; Beta idempotency key.
   - §4.3: `price_cents` by kind; `purchase_kind` validation; separate subscription and Beta grant transactions; subscription-event kind check; Beta expiry note.
   - §4.4: ledger `kind` source.
   - §4.8: `effective_limit` note; Beta fields in the status response.
   - §4.9: storage table rows.
   - §7.1: tests. §7.2 and §9.4: `purchase_kind` in RX.
3. **S2 (revoke both user docs):**
   - §4.3: new `revoke_paid_tier`; cancellation uses it.
   - §4.4: subscription refund and lost dispute use it; pytest line.
   - §4.8 note; §4.9 `entitlements.email`; §7.1 tests.
4. **S3 (import-graph test):** §3 row (file not changed); §4.11 row 18 (503 check before the imports); §7.3 allowlist with justification, exact matching rules and the plan-time re-walk result.
5. **E1 (RX required before go-live):**
   - Wording changed in: header Gates line, §0, §0a, the §2c R1 / §2d G1 / §2e direction-3 rows, §4.9, §7.2 RX variant, §9.4 heading/status/sequencing, §10 items 14-15.
   - New GL-2 in §9.3.
   - RX `_serverOnlyKeys` hunk and lib pre-check grep now include `purchase_kind`.
   - Expected RX file SHA-256 `a6c7bcdb4f320ea2bf323e94e3481e9470ca708c1975a0897f8bce6a2786f2b5` (18,508 bytes, LF) was derived by applying the exact §9.4 hunks to the `e650713b…` file. The deploy and verify blocks refuse any other YES SHA.
   - The backup and rollback blocks are byte-identical to v1.9.1: they depend only on `e650713b…`, which is unchanged.
6. **A1 (write order):** §4.1 checkout write order T1 → Stripe → T2, with failure handling; D1 bullet wording; §4.8 `added_at` time-zone note; §7.1 tests.
7. **Closure:** new §2g. Nothing else changed.
8. **v1.9.3 note:** SAG via CoS API, attempt 7/10, writer try 1/4; only §2h (D1, D1-claim, ADV1, ADV2, ADV4, ADV5). §7.1's `bucket_for` call-site parenthetical still says row 19; the call is row 21, and storage.py must not wrap again.

**Self-audit of the v1.9.2 citations (re-read at `a3d7dca2`; `src/tip/payment_routes.py` is byte-identical to `numista_backend/routes/payment_routes.py`, SHA `e5c1571c…`):**
- `payment_routes.py:206-213` (`user_uid` from `client_reference_id`/metadata, `target_id = user_uid or customer_email`, doc ref); `:217-218` (`stripe_customer_id` written to that doc); `:220-225` (grant writes `stripe_tier` from `metadata.target_tier`, default `"pro"`); `:233-238` (cancel writes `stripe_tier="free"` and locks to Free).
- `numista_backend/scripts/refresh_vertex_data_store.py` (read in full; not in `src/tip`): `:12` `BUCKET_NAME`, `:13` `gs://` URI, `:36` `discoveryengine.DocumentServiceClient()`, `:37-49` import request. No Firestore, Storage or Admin client.
- `main.py:10615` route, `:10616` `require_admin_user`, `:10623-10624` function-level imports (`src/tip/main.py` identical).
- AI/search peers: `vertex_search/coin_search_endpoint.py:24`, `morgan_knowledge.py:228`.
- Docstrings: `brain_processor.py:311`, `services/canon_sync_service.py:90`. URL constants: `services/us_mint_catalog_service.py:39-62`.
- RX: hunk anchor lines `:58`, `:66`, `:87`, `:110`, `:115`, `:345` re-checked byte-exact before deriving `a6c7bcdb…`.
- Import-graph re-walk: an AST script over 66 modules reachable from `main.py`. It found no hit outside the 22 inventory rows except `scripts/refresh_vertex_data_store.py:12`.

### 12b. Earlier record: diff summary vs v1.9 (v1.9.1; unchanged)

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
