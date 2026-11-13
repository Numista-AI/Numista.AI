# CoS Score — NET-827 FAILFIX-B1B5 Stripe Checkout Preview, v1.9.2 (Code Writing)

**Score: 94 / 100. Result: REVISE** (PASS is 95 or higher)
- Scored: 10 Nov 2026, 8:26 PM ET. Track attempt 6/10, writer try 3/4. Scored adversarially, as CoS directed after my v1.9.1 score of 100 missed SAG's three findings.
- Plan: `PLAN_NET-827_FAILFIX-B1B5_STRIPE-CHECKOUT-PREVIEW_v1.9.2_CODE-WRITING_20261110.md`, 178,910 B, 1,680 lines, SHA-256 `c6c5f1b6eeeac2e8cda607bf5daa47776ddc683326ddbf7d6bc0964cb23971bc`. I hashed it at the start and again at the end, and it matched both times.
- Code checked against: `a3d7dca2` (rules `e650713b…`).
- Inputs: the v1.9.1 SAG review (83 REVISE, findings 1–3) and the baton `BATON_NET-827_CODE-WRITING_v1.9.2_FROM-SAG83_20261110-2016.md` (S1, S2, S3, E1, A1).
- Method: 95 = PASS. Only material defects count; there are no cosmetic deductions, and external prerequisites are not defects.
- SAG: **not submitted**, because the score is below 95 (Step 2 was skipped).

## (a) Diff scope — verified
- `diff` v1.9.1 → v1.9.2 shows **+94 / −41**, matching the claim.
- Every hunk maps to the header, a baton item (S1, S2, S3, E1, A1) or the closure text in §2g/§12. Nothing else changed.

## (b) S1, Beta can't buy a paid tier — CLOSED
- **Who sets `purchase_kind`:** the server, in the Session metadata. The client can't set it: Beta ignores `tier` and `interval` and writes no `target_tier`.
- **Webhook checks:** the webhook fails closed unless the value is `subscription` or `beta`.
  - `beta` requires `mode == payment` and `amount_subtotal == 3000`.
  - `subscription` requires `mode == subscription` and a recomputed price match.
  - Subscription events whose metadata isn't `subscription` are failed.
- **Spoof attempts all fail:**
  - The client can't write Session metadata at all.
  - A subscription session labelled `beta` fails the mode check.
  - A different price fails the subtotal check.
  - `allow_promotion_codes=False` (line 262), so a buyer can't apply their own discount.
- **What the Beta grant writes (line 386):** only the `entitlements` Beta fields, the email and the ledger entry (`kind: beta`). It never writes `stripe_tier`, `subscription_status` or `grace_period_until`.
- **After expiry or refund (line 523):** the limit falls back to `get_user_tier(profile)`.
  - A Copper subscriber who refunds Beta keeps Copper; the test is at line 415.
  - Adding `purchase_kind` to RX `_serverOnlyKeys` is harmless. The field never lives on the user doc.

## (c) S2, revoke clears the tier on every doc — CLOSED (advisories only)
- **What `revoke_paid_tier` writes:** a present null on `users/{uid}`, `users/{email}` and the raw-case email doc, in one transaction. A present null on the uid doc alone already defeats the `profile.update(uid_doc)` merge. Cancel, full refund and lost dispute all use it.
- **Retry-not-half-revoke:** atomic and sound.
- **Legacy fallback:** it only nulls `users/{email}` when **that doc's own** `stripe_customer_id` equals the event's customer.
  - An attacker can only change their own doc, so this can't be pointed at another user.
  - Two accounts can't share a customer id: Firebase emails are unique, and the app lower-cases them (`auth_service.dart:42,67,84`).
  - It can only remove access. **No real wrongful-revoke risk, so no deduction.**

## (d) S3, import-graph test — NOT CLOSED (deduction D1)
- **What checks out:** the allowlist reasoning for `scripts/refresh_vertex_data_store.py` is correct against the real code:
  - `:12` BUCKET_NAME, `:13` the gs:// URI, `:36` `DocumentServiceClient()`, `:37-49` the import;
  - no Firestore, Storage or Admin client in that file;
  - importer `main.py:10615-10624`, with `require_admin_user` at `:10616` and the imports at `:10623-10624`.
- **My own AST walk** from `main.py` (module-level and function-level imports) agrees with the plan on the graph: **66 modules**, with hits only in the 22 inventory modules plus `refresh_vertex_data_store.py:12`.
- **The defect:** the plan's claim that "after the §4.11 changes, the allowlisted line is the only remaining one" is false.

## (e) E1, RX required — CLOSED
- RX is marked REQUIRED throughout. GL-2 (line 1355) blocks every live key, webhook and backend go-live step until RX is deployed and the live SHA verified. RX is sequenced before the backend go-live and is never bundled with another deploy.
- **I recomputed the RX SHA independently.** I took `git cat-file blob a3d7dca2:numista_mobile/firestore.rules` (verified `e650713b…`) and applied the five §9.4 hunks (each matched once; the :110/:115 edit matched twice, as intended). Result: **18,508 B, `a6c7bcdb4f320ea2bf323e94e3481e9470ca708c1975a0897f8bce6a2786f2b5`**, exactly the plan's value.
- Both the deploy block (line 1467) and the verify block (line 1510) throw on any other SHA, after the placeholder check. Both are PowerShell 5.1-safe (`[Security.Cryptography.SHA256]`, `Get-FileHash`, no PS7-only syntax).

## (f) A1, checkout write order — CLOSED
- The order is T1 (ensure `users/{uid}`, reserve `checkout_pending` as `creating` with no id), then Stripe create, then T2 (store the id and URL).
- **If Stripe fails:** the pending entry is deleted and the call returns 502.
- **If T2 fails:** the call returns 503. The buyer never got a URL, so they can't pay that session, and it expires. The user is blocked from a new checkout (409) until the pending entry expires, about 31 minutes. That fails safe.
- If a payment somehow arrives anyway, `users/{uid}` already exists from T1, so the grant works.
- Two parallel creates are serialized by T1; the second gets 409.

## (g) Regressions, X1–X12, Eric's decisions — clean
- **Do-not-copy items:** re-grepping for `49e77cf7`, `subscription_tier`, `999999`, `firestore:rules:get`, `python -c`, `mocha` and `users/{uid}/locked_coins` finds none of them. `numista-vault-user-content` appears only on the history row (126) and in the self-audit (1624).
- **Untouched areas:** the diff doesn't touch prices, the Christmas window, F&F, preview isolation, the holds or main.
- **Eric's decisions hold:** RX required (t2560u), holds 74611e05 and 41b8bd5f, main at 9f04550a, Stripe live OFF.

## New citations spot-checked — all accurate
- `payment_routes.py:206-238`: target_id, stripe_customer_id at :217-218, the "pro" default at :221, cancel → "free" at :233-238
- `refresh_vertex_data_store.py:12/13/36/37-49`
- `main.py:10615/10616/10623-10624`
- `vertex_search/coin_search_endpoint.py:24` (SearchServiceClient)
- `morgan_knowledge.py:228`
- `brain_processor.py:311` (docstring)
- `services/canon_sync_service.py:90` (docstring)
- `services/us_mint_catalog_service.py:39-62` (URLs that contain a bucket name but don't equal it)

## Deductions
**D1 (−6): S3 isn't closed. The import-graph test fails exactly as written.** This reopens SAG finding 3, and the plan claims the problem is closed.
- **The test rule (§7.3, line 1231):** fail on "a string literal equal to a production bucket name outside an `env_guard.bucket_for(...)` call's first argument". It also says a bucket literal is an AST string constant **equal** to the name.
- **Two such literals survive every §4.11 change:**
  1. `numista_scraper/config.py:12`: `BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"`. Row 21 changes only the Admin init and Firestore client at :117-124 and :186-193. The plan's own Bucket guard rule (line 617) lists `config.py:12` as a production bucket literal.
  2. `numista_scraper/storage.py:15`: the same literal, in the `except ImportError` fallback. Row 19 keeps it and calls `env_guard.bucket_for(BUCKET_NAME, None)`, which passes a Name, not the literal.
- **Effect:** the walk reaches both modules (`storage.py` is in the inventory), so the test fails on both lines. A builder following the plan exactly gets a red test and must either stop or change the plan's design on their own. That's the same failure SAG found in v1.9.1.
- **Fix (one or two lines):**
  - In row 21, set `config.py:12` to `BUCKET_NAME = env_guard.bucket_for("numista-uploads-studio-9101802118-8c9a8", None)`.
  - In row 19, delete the `storage.py:15` fallback literal (or apply the same expression) and use `gcs_client.bucket(BUCKET_NAME)`.
  - Or explicitly allowlist both lines with a justification.
  - Then re-run the plan-time walk and restate which lines remain.

**Total: 100 − 6 = 94, REVISE.**

## Advisories (not scored)
1. **Test parsing:** `routes/sandbox_routes.py` and `routes/telemetry_routes.py` start with a UTF-8 BOM. `ast.parse(open(p, encoding="utf-8").read())` raises "invalid non-printable character U+FEFF". The plan should say to parse bytes (`ast.parse(path.read_bytes())`) or read with `utf-8-sig`, so the test runs exactly as written.
2. **RX pre-check target:** RX now runs before the backend go-live, against production clients running main `9f04550a`. The "no client writes these keys" pre-check is evidenced only at `a3d7dca2`, and main isn't in my clone, so I couldn't verify it. Run the pre-check against the commit actually live in production, not just the branch. On this branch's history, none of the new RX keys was ever written by app code (`git log -S`).
3. **Legacy cancels:** today's legacy `checkout.session.completed` writes `stripe_tier` to `users/{uid}` (`payment_routes.py:208-215`). The legacy fallback nulls only `users/{email}`, so a legacy subscriber's uid-doc tier survives cancel. That isn't a regression (today's `subscription.deleted` writes nothing in that case either), and Stripe live is OFF, so there should be no live legacy subscribers. Still, consider also resolving the uid by `users.stripe_customer_id == customer` for a revoke.
4. **Raw-case doc:** when `entitlements.email` is present it's lower-case, so the plan doesn't say where the raw-case form comes from. Say it comes from `get_user(uid).email`. Low impact, because the app lower-cases emails.
5. **Fail-open revoke:** if no email can be resolved, the revoke retries and never revokes. Consider nulling `users/{uid}` first, which on its own is enough for the server merge, then retrying the email docs. Very unlikely in practice, because email is stored at grant.

## Constraints honoured
- No agents messaged, nothing filed via Desk, no repo writes, no deploy, no Stripe, no Firestore writes.
- SAG was not called (score below 95).
- Holds 74611e05 and 41b8bd5f are in force; main stays at 9f04550a; Stripe live stays OFF.
