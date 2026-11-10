# Code Reviewer (Argon) — Go-live review: NET-816 Catalog Chunk 1 + NET-827 Stripe Checkout v1.2

Filed 10 Nov 2026, about 11:15 AM ET. Code pin: p7-v8.9 `c547b7a0`. Plan reviewed: NET-827 v1.2, SHA-256 `273a3268933f9bc1dba25812deecec6c761b3e8de58fa23b45844f1e409ed39d`.

## BLUF

- **NET-816 Catalog Chunk 1: MUST-FIX (1 Blocker, 1 Major).** The face values and the "No face value" chip are correct for all 3,202 catalog rows, and the chunk writes no data. But the /catalog link does not open on Hosting, and the Half dime fix inflates collection melt for 90% silver Half dimes about 10x.
- **NET-827 Stripe Checkout v1.2: MUST-FIX (2 Blockers, 3 Major). DO NOT attach live Stripe keys to the code that exists now.** v1.2 is not built yet. The current checkout lets any signed-in user buy unlimited power_user/sovereign access for $4.99/month, and cancellations usually leave paid access in place.
- **Docs-only claim c547b7a0..999daf14: VERIFIED.** 21 commits, 335 paths, all .md/.txt/.bak docs; no app, config, rules or Hosting files.
- Under the stop rule (wrong charge / wrong access / data loss), B1 and B2 block real payments even at FT 90+. A1 blocks calling /catalog "live".

## Must-Fix

| ID | Sev | Where (c547b7a0) | Problem in plain English | Impact |
|---|---|---|---|---|
| A1 | Blocker | numista_mobile/firebase.json (rewrites only /wishlist, /claim); main.dart ~133-180 | No /catalog rewrite, so numista.ai/catalog 404s; #/catalog also misses (no path URL strategy). | Catalog unreachable. No money/data impact. |
| A2 | Major | melt_value_service.dart:113 (half dime first), :192 (?? 0.77344), :238 (0.05 maps only to nickel) | 90% silver Half dime now falls to the Morgan dollar silver weight. | Dashboard value ~10x too high for those coins (max of AI vs melt). No data loss. |
| B1 | Blocker | payment_routes.py:52-53, :75, :223-224; tier_gatekeeper.py:41-60 | Price comes from the tier NAME; anything not estate/family_estate is $4.99/mo, and the webhook grants whatever tier string was sent. | Wrong access: power_user/sovereign (unlimited) for $4.99/mo. |
| B2 | Blocker | payment_routes.py:208, :212-240; tier_gatekeeper.py:140-150 | Later subscription/invoice events can't find the user (uid only on session), are marked processed anyway; invoice.paid can rewrite stripe_tier to "pro". | Cancel/deletion doesn't remove paid access; no retry. |
| B3 | Major | payment_routes.py:60, :223 | Promo codes allowed on every session; webhook never checks amount_total or payment_status. | Any coupon (incl. a future 100% code) still grants full tier. |
| B4 | Major | payment_routes.py:~53, :196-240 | No idempotency key on session create; webhook dedupe is read-then-write, not a transaction. | Possible double charge; overlapping events double-apply. |
| B5 | Major | payment_routes.py:220-238 | charge.refunded and charge.dispute.created ignored (plan defers to Phase 2). | Refund/dispute keeps paid tier. Not safe for real cards. |

## Christmas code (26 Nov 2026 00:00 UTC rule)

Not in the repo today, so nothing is redeemable from code. **But the v1.2 plan's own snippet is unsafe:** it creates the promotion code with active=True and only expires_at=1798243199 (25 Dec 23:59:59 UTC). Stripe has no start time on that object. Running it before 26 Nov makes the code live immediately, and today's server accepts it on monthly sessions. Fix: keep the code inactive until 2026-11-26T00:00:00Z AND reject it server-side (session create + webhook) before that instant. Plan amendment needed.

## Keys

No live key committed (placeholders only). But stripe_config.py loads STRIPE_SECRET_KEY from env, then .env, then Streamlit secrets — no Secret Manager client and no test/live mode check. "Live keys only from Secret Manager" is enforced only by deployment config, which this review cannot see. Do not leave a test webhook secret on the production service.

## Verified OK

Checkout identity from verified Firebase token (not body); portal IDOR closed; amount is not a client field; webhook raw-body signature check, fails closed on Cloud Run if secret missing; tier writes are merge (no wipe); coins locked, never deleted; catalog chunk writes no Firestore and reads no user docs; medal chip only on type==medal, all 56 medals have null denomination.

## Unknowns (live-only)

Which Hosting site actually serves numista.ai; Secret Manager / Cloud Run env (live vs test keys); Stripe Dashboard coupons/promo codes already active; users with creation_timestamp < 1795669200000 (auto family_estate); deployed vs repo Firestore rules.

## Evidence and method

Static read-only cloud review (https://cursor.com/agents/bc-8faa7e77-0a81-562e-a040-3a5cd880e2be), plus my own spot-check of payment_routes.py, firebase.json and melt_value_service.dart at c547b7a0 via GitHub — B1, B2/B3 lines, A1 (no catalog rewrite) and A2 lines confirmed. No edits, pushes, merges, deploys, tests, or Stripe/Firebase/GCP calls. Full cloud report (SHA-256 aac3c129c961d2f80984c9a8a628a45e4fbf4d38b6698477cb7cc3bf0a61e826) appended below.

---

# Go-live review: NET-816 Catalog Chunk 1 and NET-827 Stripe Checkout

**Pin reviewed:** `c547b7a0ad22923d90042a259da9b56b2c0d6c0c` (checked out; `git rev-parse HEAD`).
**Branch tip checked:** `999daf14c4e96613aab5f6e9108e60a6cc7f0cc1` on `origin/p7-v8.9` after one `git fetch origin p7-v8.9` (local ref was stale at `63de1a45`).
**Attached NET-827 plan SHA-256:** `273a3268933f9bc1dba25812deecec6c761b3e8de58fa23b45844f1e409ed39d` (matches the uploaded v1.2 plan).
**Attached catalog plan SHA-256:** `e9677475b134d4964f302a7df484491d15e941c3c4dab593228b28935cc3dbfa`.

**No source edits, commits, pushes, branches, PRs, merges, deploys, app tests, emulators, or Stripe/Firebase/GCP API calls were made. No Secret Manager values and no user documents were read.** The only network use was the authorized `git fetch` of `p7-v8.9`. Catalog denomination counts below come from an offline local grouping of `catalog_public_v1.json`. Key files were classified with values redacted; the only Stripe key strings in git are placeholders.

---

## Docs-only claim after `c547b7a0`

`git diff --stat c547b7a0 999daf14` / `--name-only`: **21 commits, 335 paths. Application claim holds.**

| Extension | Count |
|---|---:|
| `.md` | 324 |
| `.txt` | 9 |
| `.bak_*` (backups of `WHOSE_TURN.md`) | 2 |

Zero paths under `numista_mobile/`, `numista_backend/`, `functions/`, `.github/`, and zero changes to `firebase.json`, `.firebaserc`, `firestore.rules`, or any `.dart` / `.py` / `.json` / `.yaml` / `.rules` file. The nine `.txt` files are SAG paste prompts and Muse notes. The two `.bak` files are markdown backups.

`git diff --name-only 76ffca1a^ c547b7a0` for `firebase.json` and `firestore.rules`: empty. Chunk 1’s code commits did not change Hosting rewrites or Firestore rules. Chunk 2 vs its parent (`76ffca1a` → `c547b7a0`) is only:

- `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`
- `numista_mobile/lib/services/melt_value_service.dart`
- `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`

---

## PART A — NET-816 Catalog Chunk 1

### BLUF: **MUST-FIX**

The public catalog screen, face-value parser, and medal chip match the approved v2.2 table for all 3,202 catalog rows, and this chunk does not write Firestore or read private user documents. Two material gaps block treating it as live on numista.ai:

1. A browser request for `/catalog` never reaches that screen, because Hosting has no rewrite for it.
2. The same parser change that fixes Half dime face value ($0.05) makes 90% silver Half dime melt use Morgan-dollar weight.

### Must-fix

| ID | Severity | Where (at `c547b7a0`) | What goes wrong | Money / access / data | Fix direction |
|---|---|---|---|---|---|
| A1 | **Blocker** | `numista_mobile/firebase.json:49-132` (rewrites end at `/claim/**`). Route is `numista_mobile/lib/main.dart:133-134` and `:155-180`. | Hosting rewrites `/wishlist` and `/claim` to `index.html`. There is no `/catalog` or `/catalog/**` rewrite. The file’s own comment says unknown paths are a real HTTP 404 (`main.dart:99-114`). `CatalogBrowseScreen` is constructed only from that startup path check (`main.dart:178`). Nothing else in `lib/` navigates to it. `https://numista.ai/#/catalog` also misses: hash URLs have `uri.path == '/'` (`main.dart:113-114`), and there is no `usePathUrlStrategy` anywhere under `numista_mobile/`. | The public catalog URL does not open. No charge and no data write. The feature is unreachable on this Hosting config. | Add the same style of rewrite used for `/wishlist` (`firebase.json:114-120`): `/catalog` and `/catalog/**` → `/index.html`. Path URLs then hit the existing Dart branch. Hash URLs still will not. |
| A2 | **Major** | `numista_mobile/lib/services/melt_value_service.dart:111-112` (new order), `:189-191`, `:230-237`. Callers: `header_stats_bar.dart:108` and `:115`; `home_dashboard.dart:299-300`, `:380-387`. | This commit moves `half dime` ahead of `dime`, so face value is $0.05 (correct on the catalog card). `_matchDenom` maps face `0.05` only to a `nickel` table key. `_ag90` has dime / quarter / half / dollar and no nickel (`:11-16`). A 90% silver Half dime therefore takes the `?? 0.77344` dollar weight (the Morgan/Peace ounce on `:16`). Before this commit, `dime` matched first, so the same string used the dime weight `0.07234`. Dashboard value is `max(AI estimate, live melt)` (`home_dashboard.dart:387`). | Collection melt for a 90% silver Half dime is about 10× the previous dime-weight figure, and can replace a lower AI estimate as the shown value. Catalog cards themselves do not call `compute`. No Stripe charge. No coin documents are deleted. | Give face `0.05` on the 90% silver table a half-dime ounce, or stop using the dollar weight when the face value is a coin the table does not list. |

### Face value and the “No face value” chip

Chip rule (`catalog_browse_screen.dart:1089-1164`):

- `item['type'] == 'medal'` → text **“No face value”**, and `parseFaceValue` is not called.
- Any other type → parsed amount, or an em dash when the parser returns 0. The amber “Face value · No retail estimate” chip still shows on that em dash. It is not the medal chip.

Offline grouping of `numista_mobile/assets/catalog/catalog_public_v1.json`: **3,202** rows (2,965 coin, 181 note, 56 medal), **71** type/denomination pairs, **66** non-null denomination strings. **0 medals have a denomination** (example: Libertas Americana medal, `catalog_public_v1.json:65-69`, `"denomination": null`). **0 non-medals have a null denomination.** Every non-medal denomination parses to the approved v2.2 value (0 mismatches).

So, in this catalog file:

- The medal chip does not hide a real face value.
- The em dash is only the approved zero set: multi-denomination sets, the planchet pair, `3.6 Candareens`, `CC` / `D` / `O`, `copper`, the five World’s Fair names, and `3¢–50¢`. The range guard (`melt_value_service.dart:69`) hits only `3¢–50¢` inside this file.
- A real face value **can** be hidden on a **collection** row, not a catalog row, when the denomination contains a digit, an optional “cent”, and a hyphen (the same guard). Example shape: `5 Cents - 1943`. The approved plan left that as a non-blocking advisory. It is not a new catalog-data defect.
- One catalog product shows a value the plan kept on purpose: `Dollar (two-coin set)` at `catalog_public_v1.json:216602` parses to **$1.00**, because the parenthetical is stripped and the remainder is “dollar” (`melt_value_service.dart:59` and `:118`). `Quarter (rolls/bags product)` parses to **$0.25**. Those are the approved numbers, and they are wrong if someone reads them as a set or roll total.

Half dime on the card is the correct **$0.05** (`catalog_public_v1.json:1391-1395`, denomination `Half dime`, type `coin`). The melt miss is A2, not the card.

### Writes, private data, rules

- The live `/catalog` screen loads `assets/catalog/catalog_public_v1.json` from the app bundle (`catalog_browse_screen.dart:59-63`). Asset is declared at `pubspec.yaml:97`.
- The “Send” control on the missing-item form only sets `_missingSubmitted` in widget state (`catalog_browse_screen.dart:789-795`). Nothing is stored.
- No Firestore, HTTP POST, or `SharedPreferences` use in `lib/screens/catalog/catalog_browse_screen.dart`. The catalog JSON keys are public reference fields (name, denomination, images, mintage, history). No email, uid, token, or user field.
- `UsNumismaticsCatalogScreen._handleAddToCollection` (`us_numismatics_catalog_screen.dart:68-88`) updates an in-memory map and a status string. It is not referenced from `main.dart`, so `/catalog` never opens it. It does not write Firestore.
- The catalog startup path does not call `Firebase.initializeApp` (contrast wishlist at `main.dart:66-68`). It does not read `users/{...}`.
- Firestore rules were not modified. Entitlement fields on `users/{email}` stay server-only (`numista_mobile/firestore.rules:85-101`). This chunk adds no catalog collection and no client rule that would let an anonymous visitor write or read another user’s coins.

---

## PART B — NET-827 Stripe Checkout v1.2

### BLUF: **MUST-FIX**

v1.2 is **not in the tree**. The checkout and webhook that exist at `c547b7a0` will, if a live secret key is attached, charge the wrong amount for any tier name the client sends and will leave paid access in place after cancel. Do not attach live Stripe keys to this code.

The plan’s own Christmas snippet does not encode a start time. Creating that promotion code before `2026-11-26T00:00:00Z` would make it redeemable immediately. That object is not in the repo today.

### Must-fix (defects in code that exists now)

| ID | Severity | Where | What goes wrong | Money / access / data | Fix direction |
|---|---|---|---|---|---|
| B1 | **Blocker** | `numista_backend/routes/payment_routes.py:49-73` and webhook `:220-226`. Schema: `schemas/payment_schemas.py:8-10` (`tier: str`, no enum). Limits: `tier_gatekeeper.py:41-50`. | The client cannot send a dollar amount. The client **can** send any tier string. The server charges **$4.99/month** (`unit_amount = 499`, interval `month`) for every name except `estate` and `family_estate`, which are **$29/year** (`2900`, interval `year`). The webhook then stores that same string as `stripe_tier`. `sovereign` and `power_user` are **not** in the $29 branch, and both have **unlimited** coins and AI allowance (`tier_gatekeeper.py:48-49`, `:59-60`). `check_and_enforce_coin_limit` returns immediately for `power_user` (`tier_gatekeeper.py:238-239`). | A signed-in user can open Checkout for `power_user` or `sovereign` at **$4.99/month** and receive unlimited access. `numismatist`, `dealer`, `gold`, `silver`, `platinum`, `copper`, and `beta_special` are also charged $4.99 and then stored under that name. `family_estate` is **$29/year** for a 2,500-coin / high AI tier. `pro` at $4.99 and `estate` at $29 match the comment in `stripe_service.dart:11` and are the only pair that matches this server. | Allowlist the tier on the server. Set the amount from a server table (or a server-side Stripe Price id), and grant only the tier that table says was paid. Ignore any amount or tier that is not on that list. |
| B2 | **Blocker** | Checkout create `payment_routes.py:53-74` (no `subscription_data`). Webhook identity and writes `:206-240`. Effective tier: `tier_gatekeeper.py:132-157`. | Checkout metadata is `user_uid` + `target_tier` on the **session only**. Subscription and invoice events usually have no `client_reference_id`, no `metadata.user_uid`, and often no email. `target_id` is then empty and the tier write is skipped (`:212`). The event is still marked processed (`:240`), so Stripe will not retry it. `invoice.paid` often **does** have `customer_email` and **does not** have `target_tier`, so the handler writes `users/{email}` with `stripe_tier = "pro"` (`:221-225`). | Cancel and `customer.subscription.deleted` leave the paying user’s tier in place. A renewal can overwrite `stripe_tier` to `pro` on a legacy user document keyed by email. `get_user_tier` also keeps `family_estate` whenever `is_lifetime_family_estate`, `is_ai_qc_account`, or `beta_tester` is set (`:140-143`), and whenever `creation_timestamp` is below `1795669200000` (`2026-11-26T05:00:00Z`, `:145-150`). A later `stripe_tier: free` would not remove those. Coins are not deleted: lock/unlock flips `locked_pending_upgrade` (`tier_gatekeeper.py:325-349`). | Put the Firebase uid and the paid tier on the subscription at create time. On every later event, resolve `customer` → that uid. Drop the email-as-document-id fallback. Do not mark the event done when no user document was updated. Decide explicitly what cancel does to `beta_tester` and lifetime flags; today those flags outrank `stripe_tier`. |
| B3 | **Major** | `payment_routes.py:58` and `:220-226`. | `allow_promotion_codes=True` on every session, including the $4.99 monthly ones. The webhook never reads `amount_total`, `payment_status`, or the coupon id. Access follows `metadata.target_tier` (default `"pro"`). | Any coupon that exists on the Stripe account, including a future 50% or 100% code, lowers the charge and still grants the full tier. A session that completes unpaid is treated as paid. Card-only (`:54`) makes the unpaid card case uncommon; the coupon case does not depend on that. | Turn promotion codes off until the annual-only rule and the coupon allowlist exist. Grant access only when `payment_status` is paid (or the amount is the expected F&F zero) **and** `amount_total` matches the server price for that tier. |
| B4 | **Major** | `payment_routes.py:53` (no idempotency key) and `:196-240`. | Duplicate protection is “read the event doc, later write it.” Two overlapping deliveries can both apply. Two checkout clicks create two sessions; completing both charges twice. A `subscription.deleted` that cannot see the user is stored as done (see B2). | Double charge if the buyer completes two sessions. Missed revocation is permanent for that event id. The tier write itself is a merge, so a repeated identical grant does not wipe the user document. | Idempotency key on session create, one active checkout per user. Claim the event in a transaction before fulfillment, and leave it retryable when the user was not found. |
| B5 | **Major** | `payment_routes.py:220-238` (handled types only). | Handled: `checkout.session.completed`, `customer.subscription.updated`, `invoice.paid`, `invoice.payment_failed` (3-day grace, `:227-232`), `customer.subscription.deleted` (only if a target id exists). `charge.refunded` and `charge.dispute.created` are ignored. The plan defers both to Phase 2. | A refund or dispute leaves the paid tier in place. With B2, cancellation usually does too. | Before live charges, revoke or lock on refund and dispute, and make deletion actually find the user (B2). Phase 2 is not safe for real cards. |

### (1) What is already true, and safe to keep

- Checkout identity comes from the verified Firebase token: `payment_routes.py:35` and `:47-48` (`_user.get("uid")`, token email). `req.user_email` is on the schema (`payment_schemas.py:9`) and is **not** used for the Stripe customer or the metadata uid. `StripeService` still sends `user_email` in the body (`stripe_service.dart:22-26`); the server ignores it for identity.
- Customer portal no longer takes a user email from the query or body. It uses `current_user` only (`payment_routes.py:82-97`). The Flutter caller does not send `user_email` (`stripe_service.dart:47-55`). This is the fix for the earlier portal IDOR.
- `get_current_user` verifies a Firebase ID token (`routes/deps.py:52-79`). The dev-guest bypass runs only when `K_SERVICE` is unset and `ENVIRONMENT` is not `production` and `ALLOW_UNAUTHENTICATED=1` (`deps.py:73-77`). Cloud Run sets `K_SERVICE`.
- Webhook uses the raw body (`payment_routes.py:172`) and `stripe.Webhook.construct_event` (`:182`). On Cloud Run, a missing `STRIPE_WEBHOOK_SECRET` is rejected (`:175-189`). The public allowlist is only so the webhook can skip the Firebase token (`main.py:159-162`); the signature check is inside the handler.
- Success URL (`payment_routes.py:71`) does not grant a tier. No screen under `numista_mobile/lib/` calls `StripeService`; nothing in `lib/` grants a tier from `?stripe=success`. Access is webhook-only. The API route is still mounted (`main.py:123`) and can be called with a bearer token.
- User-doc writes are `set(..., merge=True)` (`payment_routes.py:225`, `:232`, `:237`). They do not clear `beta_tester` or `is_lifetime_family_estate`. Clients cannot write those fields (`firestore.rules:85-101`).
- No `sk_live_` / `pk_live_` / live `whsec_` literal in git. `numista_backend/.env.template:5-7` and `.streamlit/secrets.toml` are placeholders (`sk_test_…`, `pk_test_…`, `whsec_…`). `stripe_config.py:8-9` and `:29-45` load `STRIPE_SECRET_KEY` from the environment, then a `.env` file if present (`load_dotenv`), then Streamlit secrets. There is no Secret Manager client and no check that the key is `sk_test_` vs `sk_live_`.

### (2) Plan items not built (expected, not scored as defects)

These are absent from `payment_routes.py`, `tier_gatekeeper.py`, and the Flutter caller. A later diff review should check them. They are not a reason to describe v1.2 as shipped.

- $30 one-time Beta Special, `mode=payment`, six calendar months via `relativedelta`, no auto-renew (plan §2.1, §4.1, §4.4).
- Copper / Silver / Platinum / Gold monthly and annual amounts (plan §2.2). Code prices are the legacy $4.99 / $29 pair (B1).
- `billing_cycle`, `pre_checkout_coin_count`, `app_version` metadata (plan §4.1).
- Annual-only `allow_promotion_codes`, monthly and Beta Special forced off (plan §3.2).
- Christmas coupon `xmas2026_50off_annual` and promotion code with `expires_at=1798243199` (plan §3.2). Repo search of `*.py` / `*.dart` / `*.yml` found no `xmas`, `christmas`, `1798243199`, or `STRIPE_PROMO`.
- F&F coupon, 500-cap, `is_friends_and_family`, `is_beta_tester`, `beta_access_type`, `$10` then `$5` AI allowance (plan §3.3).
- Transactional two-phase `stripe_events` lease, HTTP 500 while the lease is under 60s (plan §4.2). Current code is the read-then-write at `payment_routes.py:198-240`.
- Hold access until `checkout.session.async_payment_succeeded` (plan §4.3).
- Webhook rejection plus automatic refund when the Christmas coupon lands on a non-annual session (plan §3.2).
- Preview return URLs on `preview-catalog.numista.ai` (plan §4.1). Code returns to `https://numista.ai/#/settings` (`payment_routes.py:71-72` and `:121`).
- `invoice.paid` as a renewal that **refreshes the purchased tier** (plan §4.4). Current `invoice.paid` shares the “set tier from metadata, default pro” branch (B2).

`tier_gatekeeper.create_upgrade_checkout_session` (`:174-201`) is a second, unused checkout (only `check_and_enforce_coin_limit` calls it, and nothing in the request path calls that function). It uses env Price ids with mock fallbacks (`price_1ProMockID` and similar) and `allow_promotion_codes=True`. It is not the live Flutter path. Leave it unwired or it becomes another charge path.

### (3) Where the plan contradicts the code the builder must reconcile

| Topic | Plan | Code at `c547b7a0` | What the builder has to do |
|---|---|---|---|
| Price and mode | Server `price_data` amounts per tier; Beta Special is `mode=payment` at $30. | One `mode=subscription`. $4.99/mo or $29/yr from the tier **name** (`payment_routes.py:49-67`). | Replace the branch. Do not keep both. A client-supplied tier name must not choose an unlimited limit. |
| Who is charged | Token uid only. Plan agrees. | Already the token (`:47-48`). | Keep that. Do not reintroduce `req.user_email` as the customer. |
| Promo window | Christmas code active 26 Nov 2026 00:00:00 UTC through 25 Dec 2026 23:59:59 UTC. | No date check. `allow_promotion_codes=True` always (`:58`). | The plan snippet sets `active=True` at create time and only `expires_at=1798243199` (end). That timestamp is **2026-12-25 23:59:59 UTC**. There is no start field on the snippet. `Coupon.create` in the plan also has no `redeem_by`. Running that snippet before **2026-11-26T00:00:00Z** turns the code on immediately, and this server will accept it on monthly sessions too. Stripe’s `expires_at` does not block early redemption. Add a real start gate (leave `active` false until that instant, and reject the coupon in the webhook and in session create). Client-only checks would not be enough; the client does not see the code server-side today anyway. |
| F&F flag name | Writes `is_beta_tester: true`. | `get_user_tier` reads `beta_tester` (`tier_gatekeeper.py:142-143`). `is_friends_and_family` is not read. | Use the field name the gate actually honors, or teach the gate the new name. Writing `is_beta_tester` alone grants nothing. |
| Cancel vs comped users | `subscription.deleted` sets `stripe_tier` to `free`. | Even a successful free write loses to `beta_tester`, lifetime, and `creation_timestamp` (`tier_gatekeeper.py:140-150`). Nothing in this repo writes `creation_timestamp`; if production docs already have it and it is before `2026-11-26T05:00:00Z`, those accounts are `family_estate` regardless of Stripe. | Decide whether cancel overrides beta/lifetime. Do not assume `stripe_tier=free` changes what `get_user_tier` returns. |
| Refunds | Phase 2, log only (plan §4.5). | Ignored (B5). | For **live** cards this contradicts a safe go-live. Revoke before live mode, even though the preview plan deferred it. |
| Keys | Live keys only from Secret Manager; preview uses test secret names (plan §6). | Any string in `STRIPE_SECRET_KEY` is the API key (`stripe_config.py:29-70`, `payment_routes.py:28-30`). No mode check. | Inject the live key only into the production service, from Secret Manager, and do not also leave a test webhook secret on that service. A test webhook secret on a public URL would accept a forged event signed with the test secret. The code will not catch that mix. |
| Idempotency | Transaction, HTTP 500 while a lease is held (plan §4.2). | Read-then-write, HTTP 200 after skip (`payment_routes.py:198-202`). | Implement the transaction. The current 200-on-duplicate is fine for a finished event and wrong for an in-progress one. |
| App entry | Plan assumes the checkout endpoint is the product. | No screen calls `StripeService` (only `numista_mobile/test/services/bearer_header_integration_test.dart`). | Wiring a button to today’s endpoint ships B1–B5. Build the v1.2 session first. |

---

## Verified OK (short)

**Catalog**

- `/catalog` Dart branch is present and unauthenticated by design: `main.dart:154-180`. It shows `CatalogBrowseScreen` only.
- Medal chip and face line: `catalog_browse_screen.dart:1089-1196`. All 56 medals in the JSON have null denomination (sample `catalog_public_v1.json:65-69`).
- Parser matches the approved 66 denomination strings, including Half dime $0.05, `$1000` → 1000, `G$2½` → 2.50, and the intentional zeros: `melt_value_service.dart:53-129`.
- Bundle asset: `pubspec.yaml:92-97`.
- No catalog Firestore write. Rules for entitlement fields unchanged and server-only: `firestore.rules:85-101`.

**Payments**

- Token uid, not body user, on checkout: `payment_routes.py:35`, `:47-48`.
- Portal IDOR closed on the route the app calls: `payment_routes.py:82-114`, `stripe_service.dart:47-55`.
- Amount is not a client field: `payment_schemas.py:8-10`. The **tier string** is the hole (B1).
- Raw-body signature verify, and fail-closed on Cloud Run when the webhook secret is missing: `payment_routes.py:172-189`.
- Grace period on `invoice.payment_failed`: `payment_routes.py:227-232`.
- Coin rows are flagged, not deleted: `tier_gatekeeper.py:325-349`.
- No live key committed. Placeholders only: `.env.template:5-7`.

---

## Unknowns (only runtime or dashboard can prove)

- Whether the Firebase Hosting site that serves numista.ai is actually this `numista_mobile/firebase.json` (`site`: `numista-vault`, line 7). The repo file has no `/catalog` rewrite. A console-only rewrite would not show up here.
- Secret Manager contents, Cloud Run env bindings, and whether production `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` are live, test, or mixed.
- Stripe Dashboard: which Prices, Coupons, and Promotion Codes already exist; whether any code is `active` before 26 Nov 2026; webhook endpoint URL and signing secret; whether Tax is on. None of that is in git. This review did not call Stripe.
- Whether any `users/{id}` document has `creation_timestamp` below `1795669200000`. Nothing in this repo writes that field (`tier_gatekeeper.py:145-150` only reads it). If it is set, that account is `family_estate` until the cutoff regardless of Stripe.
- Stripe’s response to `Customer.list(email="")` if a token has a uid and no email (`payment_routes.py:96-108`). The portal no longer accepts a caller-supplied email. An empty token email is still passed through.
- Deployed Firestore rules vs `numista_mobile/firestore.rules`. This review did not read the live ruleset.

---

## What was not done

No file in the source tree was edited. No commit, push, branch, PR, merge, or deploy. No Flutter/pytest run, no emulator, no Stripe, Firebase, GCP, or Secret Manager API call, and no read of user documents. One `git fetch origin p7-v8.9` was used to obtain `999daf14` for the docs-only diff.
