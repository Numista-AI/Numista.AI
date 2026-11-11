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
