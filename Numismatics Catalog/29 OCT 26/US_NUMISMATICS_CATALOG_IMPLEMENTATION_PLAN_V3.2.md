# NET-646 Catalog Plan v3.2 — Change List on v2.4

**Author:** drafted by Claude in Antigravity, filed as Argon (AG CoS). · **Date:** 2026-10-29 · **Status:** DOCS-ONLY, NO EXECUTE. No code, commits or pushes.
**Freeze holds:** `origin/dev` 9b55f3d9, `origin/main` 9f04550a.
**Responds to:** GB CoS v3.1 (93, two blockers) and the founder answers of 29 Oct 7:08 PM ET. The 6:50 PM and earlier answers still stand. **Pass mark: 95.**
**Companion:** `NET-646_V3.0_APPENDIX_WRITE_AUDIT.md`, with the additions in §11 of this plan. No other file is normative.

## 0. How to read this

- **Base:** v2.4. **v3.2 supersedes v3.1 and everything before it in full.**
- **One of each:** router, rules diff, tier table, counter, inventory, gate.
- **Founder answers win** wherever they conflict with an earlier plan.

### 0.1 v3.1 and v3.0 blockers and fixes

| # | Blocker | Fix | § |
| :--- | :--- | :--- | :--- |
| GB-A, SAG-1 | The webhook writes `users.stripe_tier` and never the doc the cap reads; no status check; events can be lost; checkout carries no email | The webhook updates `user_entitlements`. It checks subscription status, writes the event marker in the same transaction, and returns 500 so Stripe retries. A daily reconcile catches lost events. Checkout metadata carries the email and key. | 4 |
| Found | Checkout (`payment_routes.py` ~50–73) charges 499 cents for **any** tier string the client sends, and the webhook trusts `metadata.target_tier`. A client could pay \$4.99 and be granted `sovereign` or `power_user`. | The server validates the tier, picks the price id, and derives the tier from the subscription's price id, never from client text. | 4.1 |
| GB-B, SAG-2 | Currency and world_items updates can forge `count_weight_q`; delete subtracts it, so the counter goes negative | Rules reject client writes of weight fields on every item collection. Delete never trusts the stored weight: it clamps and logs. Counters are floored at 0. | 3.2, 6 R1/R2 |
| GB-C, SAG-3 | Free and guest users mint set coins at 1/4, ungroup to loose, and reach about 40 loose items | Per-doc `lifetime_charged_q`. Weight 1/4 only for children the server links to a server-created shell. Ungroup adds the difference to lifetime, and is blocked (never deletes) if over the cap. | 3.2 |
| GB-D, SAG-4 | Group, ungroup, break-up and clear-all exceed 500 documents | Every multi-doc operation runs in batches of at most 150 docs per transaction, with a resumable operation record. | 3.4 |
| GB-E, SAG-5 | `main.py:356` builds its own client; the guard misses `.add()` and merge-creates | The guard patches the Firestore library classes in-process, so every client is covered. `CollectionReference.add` is wrapped. Merge-set on item paths is blocked outside the funnel. A build-failing test lists any client built outside the allowlist. | 3.8 |
| SAG risks | `stripe_tier` forge; `ai_usage`/`config` not locked in the diff; helper placement; wishlist W1 diff; settle crossing a month; restore and chunk retry idempotency; seed double count | Each closed in the section named. | 2, 3, 5, 6, 7 |
| Both | Legacy loophole for anonymous accounts linked after the cutoff | Legacy comes from a snapshot of non-anonymous accounts taken at the cutoff. | 2.3 |
| Both | `GUEST_ITEM_CAP` used as items and as quarters | `GUEST_ITEM_CAP_ITEMS = 5`, `GUEST_ITEM_CAP_Q = 20`. | 1.1 |
| **GB v3.1-1** | Set-link and weight fields stay client-editable after P3. Group assumes a fixed 4:1, so a client unlink plus a regroup frees 3 quarters each cycle. | The set link `set_shell_id` is server-only from P1. At P3 all set fields (`is_set`, `set_id`, `parent_set_id`, `set_contents`) are client-update-denied on all three item collections. Group and ungroup use each doc's **stored weight delta**, never a fixed 4:1. | 3.2, 6 |
| **GB v3.1-2** | A top-up payment that arrives after a newer subscription event is dropped by the high-water-mark check | One-time payments bypass the check and rely on the event marker alone. | 4.2 |
| GB minor | Restore on a read-only account unspecified | Allowed. | 4.4 |
| GB minor | 222 vs 149 client constructions | Both counts stated. P0 lists the server-image ones. | 11 |

## 1. Founder decisions (as of 6:50 PM ET)

### 1.1 Tiers and caps

| Display | Code name | Items | Cap in quarters | Monthly | Yearly |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Guest (anonymous) | `guest` | 5 whole items | `GUEST_ITEM_CAP_Q = 20` | — | — |
| **Free** | `free` | 10 lifetime | 40 | — | — |
| **Copper** | `pro` | 11–100 | 400 | \$4.99 | \$49.99 |
| **Silver** | `numismatist` | 101–249 | 996 | \$8.99 | \$89.99 |
| **Platinum** | `dealer` | 250–500 | 2,000 | \$10.99 | \$109 |
| **Gold** | `sovereign` | 500+ (unlimited) | none | \$15.99 | \$150 |
| **Lifetime** | — | **ON HOLD, not built** | | | |

The order is intentional (founder). No code depends on the rationale. Platinum is inclusive of 500 items. Gold starts at 501.

- **Existing `estate` and `family_estate` holders become Gold.** They leave the price map and the upgrade ladder. Ladder: `free → pro → numismatist → dealer → sovereign`.
- **Legacy:** created before 00:00 ET 27 Nov 2026 (`2026-11-27T05:00:00Z`, epoch ms 1795755600000). Unlimited items, even when paying. **An anonymous account linked to an email after the cutoff is not Legacy** (§2.3).
- **AJ (`jseaman1204@gmail.com`):** a named unlimited exception (`NAMED_UNLIMITED`) **with no AI cap** (`ai_cap_exempt`), recorded as a founder decision (7:08 PM). The founder's personal account is `eric.seaman@yahoo.com` (founder, 7:16 PM). It gets no special handling: it resolves like any other account (Legacy if it existed as a non-anonymous account before the cutoff, otherwise Free).
- **Weights:** a loose item is 4 quarters. A set coin is 1 quarter (1/4 item). A set shell is 0. Weight fields are server-only.
- **Morgan adds count** toward the cap (`actor = user`).
- **Cancel:** the account becomes read-only: all items stay visible, no new adds, restore from trash is allowed, and unused top-up credits are forfeited (§4.4).
- **Retry after delete:** the 30-day edge case is accepted.
- **Shelved and stopping:** the guest demo seed and the beta checklist stop working (they are denied by rules at P3).
- **Future work, out of scope:** eBay affiliate through the Wish List, selective ads.

### 1.2 AI caps (founder amounts; §5)

| | Month 2 onward (about 20% of monthly price) |
| :--- | :--- |
| Guest | \$0.10 |
| Free | \$0.25 |
| Copper | \$1.00 |
| Silver | \$1.75 |
| Platinum | \$2.25 |
| Gold | \$3.25 |
| Legacy | \$3.25, or the paid tier's cap if higher |
| AJ (named) | no cap |

**First month = one month of plan price** (\$4.99, \$8.99, \$10.99, \$15.99). Buyable top-up blocks: \$5 per 1,000 items scanned (final); unused credits are forfeited on cancel. **Guest AI cap: \$0.10. AJ: no AI cap.** Daily `deepdive` and `invoice_scan` limits are retired. Target margin 70–80%; accounts over 1,000 items may run at break-even for their first year (initial view, may change).

## 2. Entitlements

### 2.1 One document

`user_entitlements/{user_doc_key}`, server-only, at the top level under `match /databases/{database}/documents`.

| Field | Meaning |
| :--- | :--- |
| `legacy` | Bool, set by the cutoff snapshot (§2.3) |
| `named_unlimited`, `ai_cap_exempt`, `grandfathered_tier` | AJ exception (unlimited items, no AI cap); `sovereign` for estate/family_estate holders |
| `paid_tier`, `last_paid_tier`, `subscription_status`, `grace_until`, `stripe_customer_id`, `stripe_subscription_id`, `stripe_event_hwm`, `paid_activated_at` | Written only by `apply_subscription_state` (§4.2) |
| `read_only` | Bool (§4.4) |
| `lifetime_quarters` | Charged to the user, never decremented |
| `active_quarters` | Present now, floored at 0 |
| `ai_scan_credits` | Top-up credits (§5.3) |
| `minted_at`, `minted_from`, `seed_counts_at` | Provenance |

**Item tier is computed at read time from these fields.** It is never frozen at mint, so upgrades, downgrades and cancels change enforcement.

### 2.2 Tier resolution (replaces `get_user_tier` for the funnel)

Item cap, in order:
1. Anonymous token: `guest`.
2. `named_unlimited` or `legacy`: **unlimited** (even if `paid_tier` is set).
3. `grandfathered_tier` (`sovereign`): Gold, unlimited.
4. `paid_tier` with `subscription_status` in `active` or `trialing`, or `past_due` before `grace_until`: that tier's cap. Anything else is not paid.
5. `free`.

`users.stripe_tier` is no longer read by the funnel. It is still written as a mirror for non-funnel code, and live rules already block client writes to it (live `_serverOnlyKeys()`, line 86 includes `stripe_tier` and `tier`).

**AI tier:** Legacy gets `max(paid tier's cap, Gold's cap)`. Everyone else gets their item tier's cap. `ai_cap_exempt` accounts (AJ) have no AI cap.

### 2.3 Who is Legacy (snapshot, not creation time alone)

Creation time cannot tell an account that was always an email account from an anonymous account linked later. The uid stays the same when a guest links, so the Auth creation time is the guest's. v3.1 closes this with a snapshot.

1. **Snapshot script** `numista_backend/scripts/snapshot_legacy.py`, **required, run once at the cutoff, within minutes after `2026-11-27T05:00:00Z`. Owner: Grok CoS (founder, 7:08 PM): scheduled, run through AG, and confirmed done by Grok CoS on the radio. A dry-run runs the day before.** The script lists all Auth users with a **non-empty `provider_data`** (anonymous users have none) and a creation time before the cutoff. For each, it creates `user_entitlements/{key}` with `legacy: true` (create-only, idempotent, dry-run first, not run until Eric types YES). It then writes `config/entitlement_policy.legacy_snapshot_done_at`.
2. **Before the snapshot completes, after the cutoff:** an account with no entitlement doc gets `503 ENTITLEMENT_SNAPSHOT_PENDING`.
3. **After the snapshot completes:** an account with no doc is **not** Legacy. It mints as `free` (or `guest`). This is what keeps a late-linked guest out.
4. **Before the cutoff (now to Nov 27):** lazy mint creates `legacy: true` for a non-anonymous account (non-empty `provider_data`), and `guest` for an anonymous one. This keeps early funnel use working. The snapshot is create-only, so it never overwrites a doc minted earlier. A guest doc is keyed by uid and is never Legacy.
5. `NAMED_UNLIMITED` accounts and estate/family_estate holders are written by the same script in the same create.

**Seeding and the Auth lookup both happen before the transaction** (§2.4), so nothing slow runs in the retry loop.

### 2.4 Lazy mint and seeding

1. Pre-read `user_entitlements/{key}`. If it exists, use it.
2. If missing, resolve per §2.3 (reads Auth `get_user(uid)` for `provider_data` and creation time). An Auth failure returns `503 ENTITLEMENT_UNAVAILABLE`.
3. **Seed existing items.** For every key the account may own (`users/{email}`, `users/{uid}`), stream `coins`, `currency`, `world_items` with a field mask (`is_set`, `set_id`, `parent_set_id`, `count_weight_q`). Weight each doc:
   - Server-stamped (`count_weight_q` present): that value.
   - Unstamped (pre-funnel or client-written): **4**, except an unstamped `is_set: true` doc referenced by at least one child's `set_id`, which is 0. Client-written `set_id` and `is_set` never earn a 1/4 weight.
   Sum across keys. `active_quarters` and `lifetime_quarters` both start at the sum.
4. In the add transaction, `tx.create(ref, minted)` only if absent. If another request won, retry with the winner's doc.

- **Seed drift:** a pre-P3 direct write can land between the seed read and the create. The nightly job logs it (§3.3 invariant 4) and a reviewed manual action fixes it. Seeding only matters for capped tiers, because Legacy is unlimited.
- **Double count:** if both keys hold copies of the same item, P0 flags the account for review, and the seed counts each doc once (by path).

### 2.5 Keys and the deployed rules file

- **Key:** `resolve_user_doc_key(user)` is the lowercased, trimmed email, else the uid. Matches `AuthService.coinsPath`, `currencyPath` and `userDocPath` (`auth_service.dart:80-113`). Guests use the uid.
- **`isOwner`** compares the token email exactly (live line 13). A mixed-case token email fails closed. P0 records any such account. It is an existing issue and is not fixed here.
- **Deployed rules file:** `numista_mobile/firestore.rules` (339 lines at 9b55f3d9, identical on `main`). `.github/workflows/deploy-production.yml` runs `firebase deploy --only firestore:rules --project studio-9101802118-8c9a8` with `working-directory: numista_mobile`, and `numista_mobile/firebase.json` points `firestore.rules` at it. `numista_backend/firestore.rules` (248 lines) is not deployed (`numista_backend/firebase.json` declares only `functions`). P0 adds a "NOT LIVE" header, exports the live ruleset and diffs it against `main`. Gate 1 fails if the backend copy changes.

## 3. Server enforcement on every add path

### 3.1 The funnel

`collection_funnel.py`: `add_items`, `delete_item`, `restore_item`, `clear_all`, `group`, `ungroup`, `mint_template`, `break_up`. Only it writes item docs and entitlement counters.

Endpoints: `POST /api/v1/collection/items`, `.../items/bulk`, `DELETE .../items/{collection}/{doc_id}`, `POST .../sets/mint-template`, `.../sets/group`, `.../sets/ungroup`, `POST .../clear-all`.

**Server-assigned fields:** `is_set`, `set_id`, `parent_set_id`, `added_by`, `count_weight_q`, `lifetime_charged_q`, `actor`. A request that sends any of them gets `422`. `actor` comes from route authentication (user token gives `user`, internal service credential gives `system`), never the request body. Set membership is created only by `mint_template`, `group` and `break_up`.

### 3.2 Weights, charged quarters, and sets

| Doc | `count_weight_q` | `lifetime_charged_q` at creation |
| :--- | :--- | :--- |
| Loose coin, currency item, world item | 4 | 4 |
| Set coin (server-linked to a server-created shell) | 1 | 1 |
| Set shell | 0 | 0 |

`lifetime_charged_q` is the quarters already charged to this doc against the lifetime count. It never goes down.

- **Group** (the server verifies that every child exists, belongs to the account, is not a shell, and is not already linked to a set by the server link `set_shell_id`; the shell is created in the same transaction): each child is linked by writing the server-only `set_shell_id`. **The weight change uses the child's stored weight, never a fixed 4:1.** For each child, `old_w` is its clamped stored weight (classified like the seed if missing or implausible), `new_w = 1`, and `delta_active = new_w - old_w`, applied as a signed change. A child already at weight 1 contributes 0. `lifetime_charged_q` is unchanged, so lifetime does not refund. A repeated regroup therefore cannot free quarters.
- **Ungroup** (founder: ungroup adds to the lifetime count): the server removes `set_shell_id` and the set fields. For each child, `old_w` is the stored weight, `new_w = 4`, `delta_active = 4 - old_w`, and `delta_charged = 4 - lifetime_charged_q` (0 for a coin that was loose first, 3 for a coin created as a set coin). Then `lifetime_quarters += sum(delta_charged)`, `lifetime_charged_q = 4`, and `active_quarters += sum(delta_active)`.
  - **Cap check:** Free and guest need `lifetime_quarters + sum(delta_charged) <= cap_q`. Capped paid tiers need `active_quarters + sum(delta_active) <= cap_q`. Legacy and Gold: none.
  - **Over the cap: blocked with `403 QUOTA_EXCEEDED`. Nothing is deleted and nothing changes.**
  - This closes the loop of minting set coins at 1/4 and ungrouping them, because a set-created coin pays its missing 3 quarters at ungroup.
- **Set fields are server-only.** `set_shell_id` is server-only from P1. At P3, `is_set`, `set_id`, `parent_set_id` and `set_contents` are server-only too (§6), so a client cannot unlink, relink or regroup a coin. Until P3 the client can still edit `set_id` and `parent_set_id` as display fields, but they carry no weight: only a doc with a valid server link (`set_shell_id` pointing at an existing shell of this account) may weigh 1. The nightly recount counts any stamped weight-1 doc **without** a valid link as 4 and raises an alert, so a pre-P3 unlink gains nothing lasting.
- **Mint template:** the server creates the shell and children in one transaction. Children are set coins (weight 1, charged 1). Maximum 150 children, else `422`.
- **Break-up** (`/api/review/break_up_set`): the `review_queue` source is not counted. Children are created as set coins, in batches (§3.4). If the source was a counted doc in `coins`, it is deleted in the final batch and its weight removed.
- **Delete never trusts the stored weight.** It computes `w = min(max(stored, 0), 4)`. If the stored value is missing or implausible (more than 4 or negative), it classifies the doc as the seed does (unstamped: 4, or 0 for a valid referenced shell) and logs `weight_anomaly`. Then `active_quarters = max(0, active_quarters − w)`. `lifetime_quarters` never changes. Rules also stop clients from writing these fields (§6), so the anomaly path is defense in depth.

### 3.3 Counter transaction

**Two named quantities per call:**
- `created_all_q`: quarters of non-shell docs this call actually created, any actor.
- `created_user_q`: the part where `actor == user`.

**Cap checks:**
- Free, guest: `lifetime_quarters + created_user_q ≤ cap_q`.
- Capped paid: `active_quarters + created_all_q ≤ cap_q`.
- Legacy, named unlimited, Gold: none.
- `read_only`: any add returns `403 ACCOUNT_READ_ONLY` (§4.4).

**Doc ids are content-derived:** `uuid5(NAMESPACE, f"{key}:{idempotency_key}:{sha256(canonical_item_json)}:{ordinal}")`, with `ordinal` numbering identical items. Reordering a request does not change the ids.

Add, one transaction:
1. Read `user_entitlements/{key}` (mint per §2.4). **The entitlement read is inside the transaction.**
2. Read `users/{key}/catalog_idempotency/{idempotency_key}`.
3. Record exists with a different `payload_hash`: `409 IDEMPOTENCY_KEY_REUSED`.
4. Record exists with the same hash: return the stored result with `replayed: true`. Nothing is written.
5. Read each target id. Skip targets that already exist. Compute `created_all_q` and `created_user_q`.
6. Apply the cap checks above. Over the cap: `403 QUOTA_EXCEEDED` with `remaining_q`.
7. Write the new docs (stamped `count_weight_q`, `lifetime_charged_q`, `added_by`), the idempotency record, and the counters.

**Accepted case (founder: yes):** if a doc created by key K is deleted and K's record then expires, retrying K with the same payload creates the doc again and adds to `lifetime_quarters` again. Records live 30 days (a Firestore TTL policy on `ttl_expires_at`, plus a `ttl_expires_at > now` check on read, because TTL deletion lags). The client's maximum retry horizon is 7 days.

**Hash:** SHA-256 of canonical JSON of the request body without the idempotency key (sorted keys, separators `(',',':')`, UTF-8, money as `f"{Decimal(v):.2f}"`).

**Delete:** read the entitlement and target, in one transaction. A missing doc returns `200 {deleted: false}` and changes nothing. Otherwise delete the doc (to `trash` when asked) and subtract its clamped weight (§3.2).

**Restore:** keyed by `{key}:restore:{doc_id}`. The record makes a retry a no-op. It re-creates the doc with its stored weight and charged value, adds weight to `active_quarters`, and leaves lifetime unchanged. It is checked against the paid cap and not against the free lifetime. It is allowed on a read-only account (§4.4).

**Invariants** (each has a test in §8):
1. A replay or retry never changes a counter.
2. Delete changes only `active_quarters`, only when a doc existed, by its clamped weight.
3. Counters are written only in the transaction that writes the docs. There is no absolute rewrite.
4. A nightly job compares counters with a weighted recount and logs drift. It never writes. Reconciling is a manual, reviewed action. Both counters are floored at 0.

### 3.4 500-document limit (founder: stay under 500)

A transaction counts reads and writes. Every multi-doc operation therefore runs in **batches of at most 150 docs, one transaction each** (150 reads + 150 writes + about 4 bookkeeping docs, under 500).

| Operation | Batching |
| :--- | :--- |
| Add and bulk add | ≤150 items per transaction. Capped tiers and guests: one request is one transaction, all-or-nothing, so ≤150 items or `422`. Unlimited tiers chunk at 150 (key `{key}:{chunk}`). |
| Mint template | ≤150 children, one transaction. |
| **Group** | Batch 1: shell plus first ≤150 children. Later batches: next ≤150 children. |
| **Ungroup** | ≤150 children per batch. The shell is deleted in the last batch. |
| **Break-up** | ≤150 children per batch. |
| **Clear-all** | ≤150 deletes per batch. |

- **Operation record:** multi-batch operations write `users/{key}/catalog_idempotency/{op_id}` with `{kind, total, cursor, status}`. A retry with the same `op_id` resumes from `cursor`. It finds committed batches by the cursor and by the existing/missing-doc checks. Each batch is idempotent, so a retry never double-counts.
- **Cap precheck:** for ungroup, the whole operation's `Σ Δcharged` (and `3n` for paid) is checked before batch 1. Each batch re-checks. If a race pushes a later batch over the cap, that batch returns `403` and the operation stays resumable. Nothing is deleted.
- **Legal intermediate states:** after any committed batch, every doc is either grouped with a valid shell or loose, and the counters match. A 500-item Platinum group is four batches.
- **Chunk retry for unlimited tiers:** the response carries `partial: true` and the created ids, and the client retries with the same key, resuming by the record.

### 3.5 Failure behavior

Entitlement or Auth error: `503 ENTITLEMENT_UNAVAILABLE` with `Retry-After`. It is never `403`. Once the doc is read, a legacy or unlimited account skips the cap check.

### 3.6 Rollout phases and schedule

| Phase | What ships | Cap enforced |
| :--- | :--- | :--- |
| **P0** | Verify Appendix A and §11. Run the client audit script. Confirm the deployed rules file. Find real nested subcollections under currency and world_items. List every module that builds its own Firestore client. Confirm the Stripe webhook secret is set in production. | No |
| **P1** | Funnel, endpoints, client switch, server routes call the funnel, R1 guards, R3 keys, Stripe fixes (§4), write guard (§3.8). | Funnel traffic only |
| **P2** | Soak: 0 direct creates for 7 days from builds at or above P1 (log metric plus nightly recount). `config/min_app_version` set to the P1 build. | New builds |
| **P3** | Rules flip (§6). | **Every path** |

| Date (2026) | Milestone |
| :--- | :--- |
| Now (Oct 29) | Freeze holds. v3.2 scored. |
| ~Nov 3 | Eric's typed YES, if v3.2 passes 95. P0 starts. |
| ~Nov 10 | P1 merged to `dev`. |
| ~Nov 13 | P1 live. **Go/no-go checkpoint.** |
| ~Nov 20 | P2 soak done. P3 deployed. |
| **Nov 27 05:00Z** | Cutoff. Snapshot script (§2.3) run. Stripe goes live **only if** the AI-cap gate (§4.5) is met. |

- **Fixed:** the cutoff. A slip never removes Legacy status.
- **Soft-enforce fallback (checkpoint missed):** the funnel enforces for all funnel traffic, including the web build. A nightly job and an on-write check recount every post-cutoff and guest account from the real collections, counting every doc including unstamped ones (pre-P3 direct writes carry no stamp, so they count as user-added). Over-cap accounts get `over_cap: true`, and the funnel denies further adds and shows the upgrade prompt. No items are deleted. P3 ships as soon as the soak completes.
- **If P1 slips past Nov 20:** Stripe go-live and cap enforcement move to the P3 date (`config/entitlement_policy.cap_enforcement_start`, server-written, client-readable, write-denied by the live `config/**` rule). The cutoff stays Nov 27. `[PENDING ERIC]`.

### 3.7 Guests and shelved items

- **Guests** use the funnel as tier `guest` (keyed by uid), cap 20 quarters, lifetime like Free. Rules deny anonymous direct creates and deletes at P3. App Check on the funnel (monitor, then enforced) limits abuse, since the client API key can mint anonymous users.
- **Linking after the cutoff:** the linked account is keyed by its email, gets a fresh entitlement doc, and is `free`, not Legacy (§2.3). Guest items under the uid are summed into its seed.
- **Guest demo seed and beta checklist** stop working at P3. Both write directly, and the guest cap and shelving decisions mean no carve-out. The funnel path exists if they are revived.

### 3.8 Closing server writers

- **Library-level guard (primary, path-exact):** `firestore_guard.install()` runs at the top of `main.py` and `routes/deps.py` (idempotent). It patches the `google.cloud.firestore_v1` classes themselves, so **every client in the process is covered, including `main.py:356`'s own `firestore.Client`**: `DocumentReference.set/create/update/delete`, **`CollectionReference.add`**, `BaseWriteBatch.set/create/update/delete`, `Transaction.set/create/update/delete`, and `BulkWriter`.
- **Rule:** a write whose `ref.path` matches `users/*/(coins|currency|world_items)/*` must come from `collection_funnel.py`. It raises in tests and staging. In production it emits an `unfunneled_item_write` metric and alert.
- **`set(merge=True)` on an item path is blocked outside the funnel.** It can create a missing doc. Existing callers (`main.py:1544`, `3757`, `1991`, `grade_review_routes.py:355`) are converted to `update()`, which fails on a missing doc. `update()` is allowed for the `SYSTEM_WRITERS` allowlist (path, operation, reason).
- **Build-failing client rule:** `test_no_firestore_client_outside_allowlist` walks the import graph from `main.py` and fails if any module builds a `firestore.Client(` or `firestore.client()` outside the allowlist (`routes/deps.py`, `main.py`, `tier_gatekeeper.py` at P0). The guard patches the library, but this test makes a new client a deliberate allowlist entry. Admin scripts outside the server image are excluded and listed.
- **Static scan (secondary):** `test_no_unfunneled_item_writes` flags `.set(`, `.add(`, `.create(`, `.delete(`, `batch.*`, `tx.*`, `BulkWriter` on Firestore refs, tracing variable references inside a function. `.add(` is checked on Firestore references only, so Python `set.add` does not match.
- **Admin scripts** that create items go through the funnel with `actor=system`. Update-only scripts are allowlisted.
- **Rules OR semantics:** the emulator suite runs against the full post-edit file (§6 R5).

## 4. Stripe, billing, cancel and export

### 4.1 Checkout (fixes the client-chosen tier)

Today `payment_routes.py` builds inline `price_data` at 499 cents (2,900 for estate) for any `req.tier` string and puts `target_tier` in metadata. v3.1:
- Validate `req.tier` against `SOLD_TIERS = {pro, numismatist, dealer, sovereign}` and `req.interval` against `{month, year}`. Anything else returns `422`.
- Choose the price from env `STRIPE_PRICE_<PRO|NUMISMATIST|DEALER|SOVEREIGN>_<MONTHLY|YEARLY>`. A missing id fails closed (`502`). **No inline `price_data`, no mock defaults** (also removes the `price_1…MockID` fallback in `tier_gatekeeper.py` ~180–189).
- Metadata (on the session and in `subscription_data.metadata`): `{user_uid, user_email: <lowercased>, user_key: resolve_user_doc_key, target_tier}`. This is the `payment_routes.py:73` fix. `client_reference_id` stays the uid.
- The tier is **never** read from metadata by the webhook. It comes from the subscription's price id (§4.2).

### 4.2 Webhook `apply_subscription_state`

- **Events handled:** `checkout.session.completed` (subscription, top-up and full-export purchases), `customer.subscription.created/updated/deleted`, `invoice.paid`, `invoice.payment_failed`.
- **State from Stripe, not the payload shape:** retrieve the subscription (`stripe.Subscription.retrieve`), read `status` and the price id of its item, and map the price id to a tier through the table in §4.1 (monthly and yearly map to one tier). Unknown price id: log, change nothing, return 200.
- **Key:** `metadata.user_key`; else the entitlement doc found by `stripe_customer_id`; else the lowercased `customer_email`; else the uid. Unresolvable: write `stripe_unresolved/{event_id}`, alert, return 200.
- **Subscription events, one transaction:** skip if `event.created < stripe_event_hwm` (out-of-order). Otherwise write on `user_entitlements/{key}`: `paid_tier`, `last_paid_tier`, `subscription_status`, `grace_until`, ids, `paid_activated_at` (first activation), `stripe_event_hwm`, `read_only`, set `ai_scan_credits` to 0 when the subscription stops being paid (§4.4), **and the `stripe_events/{event_id}` marker in the same transaction.** The high-water mark applies to subscription state only.
- **One-time payments (top-ups, full export) bypass the high-water-mark check.** They rely on the event marker alone, keyed by the Stripe event id. In one transaction: create the marker, then grant (`ai_scan_credits += 1000 * quantity`, or mark the export purchased). A replay finds the marker and does nothing. They never read or write `stripe_event_hwm`, so a top-up that arrives after a newer subscription event is still granted. A payment for an account that is not eligible when it lands (not paid, not Legacy or named, or already cancelled) is written to `stripe_unresolved`, alerts, and is refunded by hand. It is never silently dropped and never granted.
- **Status rule:** `active` and `trialing` are paid. `past_due` is paid until `grace_until` (3 days, as today), then not paid. `canceled`, `unpaid`, `incomplete_expired` are not paid.
- **Failure:** any exception returns 500 so Stripe retries (up to 3 days). Because the marker commits with the state, an event cannot be marked processed and lost.
- **Mirror:** also set `users/{key}.stripe_tier` and `subscription_status` for non-funnel readers (server-only keys).
- **Reconcile job (daily):** for every entitlement with a `stripe_subscription_id`, retrieve the subscription and apply the same state function. This catches events lost beyond Stripe's retry window.
- **P0:** confirm `STRIPE_WEBHOOK_SECRET` is set in production. The code already rejects unsigned payloads there.

### 4.3 What `tier_gatekeeper.py` loses

`TIER_DAILY_ALLOWANCES`, `check_and_increment_daily_usage`, `lock_overflow_coins` and `unlock_user_coins` (cancel makes the account read-only instead; no items are hidden), `estate`/`family_estate` prices, and the `creation_timestamp` branch of `get_user_tier`. `check_and_enforce_coin_limit` is replaced by the funnel. `/api/payments/status` reports monthly AI usage, read-only state and quarters used instead of the daily fields.

### 4.4 Cancel = read-only

- **Applies to:** an account that had a paid tier and is not Legacy or named unlimited, when its subscription is no longer paid (§4.2).
- **Effect:** `read_only: true`. All items stay visible. Adds return `403 ACCOUNT_READ_ONLY` with an upgrade prompt. Edits to existing items, deletes, **and restore from trash** still work (a restore only re-adds the user's own item and charges nothing to the lifetime count). **Unused top-up credits are forfeited** (`ai_scan_credits` set to 0). A re-subscribe clears read-only but does not bring credits back.
- **Legacy and named unlimited:** cancelling a paid plan does not make them read-only. They stay unlimited. Their AI cap falls back to the Legacy cap. Top-up credits bought while paying are forfeited when the subscription ends.
- **Free users who never paid** are not read-only. They keep their 10-item lifetime cap.
- **Cancel at period end:** the account stays paid until Stripe sends the final `subscription.deleted` or `status` change.

### 4.5 Go-live gate (founder: Stripe live Nov 27 only if AI caps are set)

- `config/ai_caps` holds the caps (§5). `config/entitlement_policy.stripe_live` is the switch. The checkout endpoints return `503 BILLING_NOT_ENABLED` unless **all** of: `ai_caps.complete == true` (every cap non-null, including `AI_CAP_GUEST`), `stripe_live == true`, every subscription, top-up and full-export price id is set, and `config/entitlement_policy.legacy_snapshot_done_at` is set (§2.3).
- Both config docs are client-readable and write-denied by the live `config/**` rule (live lines 181–184), and R5 tests that.
- All cap values are now set (§5.1), including the guest cap.

### 4.6 Export on cancel and the full export

- **Basic export (free, always available, including a cancelled or read-only account):** `GET /api/v1/export/basic.zip`, authenticated. The zip holds `items.csv` and a `photos/` folder with the user's **own photos** (`owner_photos`, `custom_*_image_url`) as files, so there are no expiring links. The CSV holds only data the user entered: `USER_EXPORT_FIELDS` = item name or list entry, quantity, notes, purchase price, purchase date, retailer, and a `photo_files` column naming the files in `photos/`. P0 turns the allowlist into exact keys from the add forms. Unknown fields are excluded by default.
- **Delivery without links:** the zip is streamed through the authenticated endpoint. A large collection (AJ has about 4,500 items) is built by a background job into a private bucket and downloaded through `GET /api/v1/export/jobs/{id}/download` (authenticated, ranged, resumable), never a signed link. Job results are kept 7 days as storage retention only, and the user can rebuild at any time.
- **Stays with Numista.AI (not in the basic export):** AI valuations (`ai_value_*`), stock and catalog images, AI-generated details and grades.
- **Full export (paid, includes AI data):** price = **6 x the monthly price of the user's last paid tier** (`last_paid_tier`): Copper \$29.94, Silver \$53.94, Platinum \$65.94, Gold \$95.94. It is always the monthly price, even for a yearly plan. It is sold as a one-time payment with fixed price ids `STRIPE_PRICE_FULL_EXPORT_<PRO|NUMISMATIST|DEALER|SOVEREIGN>` (no inline `price_data`). The webhook (§4.2) marks the purchase. `GET /api/v1/export/full` returns `402 FULL_EXPORT_NOT_PURCHASED` until then, and afterwards a zip with all item data including AI fields and photos, delivered the same authenticated way. An account that never paid has no `last_paid_tier` and gets `402 FULL_EXPORT_NO_PRICE` until Eric decides (§12).
- Paid subscribers keep their existing Estate PDF and CSV export (v2.4 §6.2).

## 5. AI cost caps

### 5.1 Values and periods

Constants in `config/ai_caps` (micro-dollars): `AI_CAP_FREE = 250000`, `PRO = 1000000`, `NUMISMATIST = 1750000`, `DEALER = 2250000`, `SOVEREIGN = 3250000`, `LEGACY = 3250000`, `AI_CAP_GUEST = 100000` (\$0.10).

- **First month = one month of plan price:** for 30 days from `paid_activated_at`, the cap is the tier's monthly price (499000, 899000, 1099000, 1599000 micro-dollars). After that, the table above. A tier change inside the first 30 days uses the new tier's first-month price.
- **Legacy:** `max(paid tier's cap, Gold's)`. The first-month window applies when the account is paying.
- **AJ (`ai_cap_exempt`):** no AI cap. `reserve` records her spend in the ledger and never returns `429`, and top-up credits are never drawn for her. Server jobs run on her behalf (invoice batches) pass her `user_key`, so her spend is still recorded.
- **Period key:** `first30` while inside the first-month window, else `YYYYMM` (America/New_York calendar month). `resets_at` is the next first-of-month 00:00 ET.

### 5.2 Wrapper `ai_budget`

- `reserve(user_key, est)` in a transaction reads the period doc and cap. If `used + est > cap`, return `429 AI_BUDGET_EXCEEDED` with `resets_at` (unless the account has top-up credits, §5.3). It returns a **reservation token holding the period key**.
- `settle(token, actual)` and `release(token)` apply to **that period key**, not "now", so a call that crosses midnight at a month boundary adjusts the right month. Both are idempotent per token.
- A failed call before billable output releases the estimate.
- **Ledger:** `ai_usage/{user_doc_key}/periods/{period_key}` (`cost_micros`, `calls`). Price table: a versioned `AI_PRICE_TABLE`. No model ID is named or changed.
- **Retired:** daily `deepdive` and `invoice_scan` limits.
- **Closure:** `test_no_unwrapped_ai_calls` flags `generate_content`, `genai` and `vertexai` calls outside `ai_budget`.
- **Kill switch:** `config/ai_kill_switch`.

### 5.3 Top-up blocks (founder: \$5 per 1,000 items scanned)

- One-time Stripe price `STRIPE_PRICE_AI_TOPUP_1000` (\$5 for 1,000 items scanned). A paid payment-mode `checkout.session.completed` adds `1000 * quantity` to `ai_scan_credits` through the one-time payment path in §4.2 (event marker only, no high-water-mark check).
- After the monthly cap is reached, each scanned item draws one credit. Credits are not tied to a period.
- **Forfeited on cancel:** when a subscription ends (§4.2, §4.4), `ai_scan_credits` is set to 0 in the same transaction. A re-subscribe does not restore them.
- A top-up checkout is offered only to accounts that are paid, Legacy or named unlimited. AJ never needs one.
- Open: whether a Legacy account that bought top-ups without a subscription keeps them (§12). The plan assumes it does.

## 6. `firestore.rules` — edits to the live file

All helper functions are added **once, at the top, directly under `match /databases/{database}/documents`, after `isOwner` (live line 15)**. They are never inside a `match` block, so `coins`, `currency` and `world_items` all see them. Every existing block stays.

```diff
+    function _catalogOnlyCoinKeys() {
+      return ['catalog_snapshot', 'catalog_nac_code', 'catalog_idempotency_key'];
+    }
+    function _serverAssignedKeys() {
+      return ['count_weight_q', 'lifetime_charged_q', 'added_by', 'actor', 'set_shell_id'];
+    }
+    function _isCatalogDocId(id) { return id.matches('^NAC1\\..*'); }
+    function _isCatalogSource() {
+      return request.resource.data.get('source', '') in ['catalog', 'US_NUMISMATICS_CATALOG'];
+    }
+    function _noServerKeysChanged() {
+      return !request.resource.data.diff(resource.data).affectedKeys().hasAny(_serverAssignedKeys());
+    }
+    function _setFieldKeys() {
+      return ['is_set', 'set_id', 'parent_set_id', 'set_contents'];
+    }
+    function _noSetFieldsChanged() {
+      return !request.resource.data.diff(resource.data).affectedKeys().hasAny(_setFieldKeys());
+    }
```

### R1. `coins` (live lines 40–74)

**P1:**

```diff
     match /users/{email}/coins/{coinId} {
       allow read: if isOwner(email);
       allow delete: if isOwner(email);
       allow create: if isOwner(email)
                     && request.resource.data.keys().hasAll(['is_demo', 'is_demo_cleared'])
                     && request.resource.data.is_demo == false
-                    && request.resource.data.is_demo_cleared == false;
+                    && request.resource.data.is_demo_cleared == false
+                    && !_isCatalogDocId(coinId)
+                    && !_isCatalogSource()
+                    && !request.resource.data.keys().hasAny(_catalogOnlyCoinKeys())
+                    && !request.resource.data.keys().hasAny(_serverAssignedKeys());
       allow update: if isOwner(email)
                     && !request.resource.data.diff(resource.data)
                           .affectedKeys()
-                          .hasAny(['is_demo', 'is_demo_cleared']);
+                          .hasAny(['is_demo', 'is_demo_cleared'])
+                    && !request.resource.data.diff(resource.data)
+                          .affectedKeys()
+                          .hasAny(_catalogOnlyCoinKeys())
+                    && _noServerKeysChanged();
     }
```

`set_shell_id` is server-only from P1 (it is in `_serverAssignedKeys()`), so a client cannot remove or change the server's set link. `is_set`, `set_id` and `parent_set_id` stay client-writable at P1 as display fields, because the live Mint-set and grouping code writes them directly. They earn no weight: unstamped docs weigh 4 and only a valid server link can weigh 1 (§2.4, §3.2). **At P3 they become server-only on all three item collections** through `_noSetFieldsChanged()` (below).

**P3:** in the `coins` block, replace the `delete` and `create` lines with `allow create, delete: if false;  // server funnel only; anonymous guests too`, and add the set-field guard to `update`:

```diff
-                    && _noServerKeysChanged();
+                    && _noServerKeysChanged()
+                    && _noSetFieldsChanged();
```

A client therefore cannot unlink, relink or regroup a coin. Only the funnel's group, ungroup, mint-template and break-up operations change set fields. Valuation merge `set` on existing docs is unaffected, because it does not touch set fields.

### R2. `currency`, `world_items`, and server-only blocks

Add `'currency'`, `'world_items'`, `'catalog_slot_counters'`, `'catalog_idempotency'`, `'catalog_meta'` to both `!(sub in [...])` lists (live lines 110 and 115). **There is no `{rest=**}` block for `currency` or `world_items`**, because `{rest=**}` also matches the parent doc. If P0 finds real subcollections, each gets a named block.

```diff
+    // P1
+    match /users/{email}/currency/{docId} {
+      allow read, delete: if isOwner(email);
+      allow create: if isOwner(email) && !_isCatalogDocId(docId) && !_isCatalogSource()
+                    && !request.resource.data.keys().hasAny(_serverAssignedKeys());
+      allow update: if isOwner(email) && _noServerKeysChanged();
+    }
+    match /users/{email}/world_items/{docId} {
+      allow read, delete: if isOwner(email);
+      allow create: if isOwner(email) && !_isCatalogDocId(docId) && !_isCatalogSource()
+                    && !request.resource.data.keys().hasAny(_serverAssignedKeys());
+      allow update: if isOwner(email) && _noServerKeysChanged();
+    }
+    match /users/{email}/catalog_slot_counters/{docId} { allow read: if isOwner(email); allow write: if false; }
+    match /users/{email}/catalog_meta/{docId}          { allow read: if isOwner(email); allow write: if false; }
+    match /users/{email}/catalog_idempotency/{docId}   { allow read, write: if false; }
+    match /user_entitlements/{email} { allow read: if isOwner(email); allow write: if false; }
+    match /ai_usage/{document=**}      { allow read, write: if false; }
+    match /stripe_events/{document=**} { allow read, write: if false; }
+    match /stripe_unresolved/{document=**} { allow read, write: if false; }
```

**P3 versions for the two item blocks, in full:**

```diff
     match /users/{email}/currency/{docId} {
-      allow read, delete: if isOwner(email);
-      allow create: if isOwner(email) && !_isCatalogDocId(docId) && !_isCatalogSource()
-                    && !request.resource.data.keys().hasAny(_serverAssignedKeys());
+      allow read: if isOwner(email);
+      allow create, delete: if false;
-      allow update: if isOwner(email) && _noServerKeysChanged();
+      allow update: if isOwner(email) && _noServerKeysChanged() && _noSetFieldsChanged();
     }
     match /users/{email}/world_items/{docId} {
-      allow read, delete: if isOwner(email);
-      allow create: if isOwner(email) && !_isCatalogDocId(docId) && !_isCatalogSource()
-                    && !request.resource.data.keys().hasAny(_serverAssignedKeys());
+      allow read: if isOwner(email);
+      allow create, delete: if false;
-      allow update: if isOwner(email) && _noServerKeysChanged();
+      allow update: if isOwner(email) && _noServerKeysChanged() && _noSetFieldsChanged();
     }
```

The explicit `ai_usage`, `stripe_events` and `stripe_unresolved` blocks document intent. A deny cannot override an allow, so R5 proves no other block matches those paths. `config/min_app_version`, `config/entitlement_policy`, `config/ai_caps` and `config/ai_kill_switch` fall under the live `config/**` rule: any signed-in user can read them (intended), and no client can write them.

### R3. `_serverOnlyKeys()` (live line 85)

- **Live today:** `tier`, `stripe_tier`, `beta_tester`, `is_lifetime_family_estate`, `is_ai_qc_account`, `is_bot_account`, `sandbox_cleared`, `admin` (live lines 85–88). So `stripe_tier` is already client-locked. The funnel no longer reads it anyway (§2.2).
- **Add:** `'power_user'`, `'subscription_tier'`, `'stripe_customer_id'`, `'creation_timestamp'`, `'subscription_status'`, `'grace_period_until'`, `'read_only'`. (`power_user` and `creation_timestamp` are honored by live code and writable by a client today.)
- **Gate:** `git grep -n -E "power_user|subscription_tier|stripe_customer_id|creation_timestamp|subscription_status|grace_period_until|read_only" -- numista_mobile/lib` must show no client write of these keys. The client never creates the `users/{email}` root doc. Its only user-doc write is `my_collection_screen.dart:358` (sort fields, `users/{uid}`).
- P0 scans `users` for client-written bad values of these keys and reports them.

### R4. `public_wishlists` (live lines 250–254), two steps

**W1 (no behavior change):**

```diff
-      allow update: if request.resource.data.diff(resource.data).affectedKeys().hasAny(['reserved_items', 'reservation_details']);
+      allow update: if request.resource.data.diff(resource.data).affectedKeys().hasOnly(['reserved_items', 'reservation_details']);
```

**W3 (after §7 W2 ships):**

```diff
-      allow create: if request.auth != null;
-      allow update: if request.resource.data.diff(resource.data).affectedKeys().hasOnly(['reserved_items', 'reservation_details']);
+      allow create: if false;
+      allow update: if false;
+      allow delete: if request.auth != null && resource.data.get('owner_uid', '') == request.auth.uid;
```

The server creates wishlists through `POST /api/v1/wishlist/share` and stamps `owner_uid`.

### R5. Rules tests (`numista_mobile/firestore.rules.test.js`, modular `setDoc`/`updateDoc`/`deleteDoc`, `firebase emulators:exec` against the full post-edit file)

- **Regression, one positive and one negative per existing block:** `estate_reports` (both), `settings` (both), `morgan_action_log`, `trash`, `audit_log`, `morgan_proposals`, `subaccounts`, `subscription`, `transferred_coins`, `transferred_currency`, `users/{email}`, both wildcard blocks, `global_programs`, `coins_reference`, `config/ebay`, `config/**`, `coin_image_index`, `coin_set_index`, `mint_errors`, `pending_items`, `supplies_log`, `admin_grade_flags`, `commands/{email}/pending` and `results`, `beta_feedback`, `public_wishlists`, `estate_reports`, its `access_logs`, `attorney_tokens`, `family_groups`, `tickets`, `tickets/{id}/private`, `tickets/{id}/messages`, `support_access_logs`, and the final deny.
- **P1:**
  - Manual create succeeds on coins, currency and world_items. Catalog id, `source: "catalog"`, `catalog_snapshot`, `count_weight_q`, `lifetime_charged_q`, `added_by` and `actor` are denied on all three.
  - **Set link:** a client `update` that removes or changes `set_shell_id` is denied at P1 on coins, currency and world_items.
  - **Forged weight:** a client `update` that sets `count_weight_q` or `lifetime_charged_q` on an existing coin, currency doc or world item is denied.
  - Valuation merge `set` on an existing coin and currency doc succeeds.
  - A write to `user_entitlements` is denied. A read of the account's own doc succeeds at the top-level path.
  - Setting `power_user`, `creation_timestamp`, `read_only` or `subscription_status` on `users/{email}` is denied.
  - A client write to `config/min_app_version`, `config/entitlement_policy`, `config/ai_caps` and `config/ai_kill_switch` is denied, and a signed-in read succeeds.
  - `ai_usage`, `stripe_events` and `stripe_unresolved` are denied for read and write.
  - The legacy wishlist reserve payload passes `hasOnly`. A payload that also sets `items` is denied.
- **Parents and wildcards:** every collection in the `!(sub in [...])` lists is denied through the wildcard. A signed-in account cannot create a `currency` or `world_items` doc through any other matching block.
- **P3:** a signed-in account's and an anonymous guest's `create` and `delete` on all three collections are denied. Update on existing docs succeeds. A merge `set` on a missing doc is denied. A client `update` that changes `is_set`, `set_id`, `parent_set_id` or `set_contents` is denied on all three collections, so a client cannot unlink or regroup a coin.

## 7. Public wishlist reserve (recipients reserve without signing in)

- **Today:** `public_wishlist_view_screen.dart:67-90` calls `update()` with `reserved_items` (list of ints) and `reservation_details.<n>`. The server `POST /api/v1/wishlist/reserve` exists (transaction, 48-hour lazy hold, name sanitizer, per-IP limiter) but stores a map, uses per-instance memory for the limiter, takes the client-supplied first `X-Forwarded-For` hop, never checks `expires_at`, and returns `444` for a missing token.
- **W1:** `hasOnly` (R4). Safe now.
- **W2:**
  - **One shape:** the server writes `reserved_items` as a map `{coin_id: {reserved_by, reserved_at}}`. The viewer and the owner banner (`wishlist_screen.dart:1039`, which does `List<int>.from(...)` and throws on a map) read the map and the legacy list.
  - **Client switch:** the viewer calls the server endpoint instead of `update()`.
  - **Shared limiter:** Firestore-backed, 10 per minute per IP, 30 per hour per token, 200 per token lifetime (engineering defaults, not founder decisions).
  - **IP:** the platform-appended hop (`TRUSTED_PROXY_HOPS`, default 1), never the client-supplied first hop.
  - **Expiry:** `410 WISHLIST_EXPIRED` past `expires_at`; `404` for a missing token.
  - **Name:** control characters stripped, 50 characters, first name or nickname only.
  - **Undo by the same person:** reserve returns a random 128-bit `reservation_secret`. Only its hash is stored, in `public_wishlists/{token}/private/reservations` (not matched by the non-recursive `public_wishlists/{token}` rule, so denied). `DELETE /wishlist/reserve` accepts that secret or the owner's sign-in.
  - **Bots:** App Check (reCAPTCHA), monitor first, then enforced.
- **W3:** `create` and `update` become `false` (R4). W2 and W3 ship together. Between W1 and W3 a token holder can still write the two reservation keys directly, which skips the shared limiter.
- **Residual:** a link holder can read reserved names (today's behavior). A leaked link allows up to the per-token cap in junk reservations. The owner clears them, and holds expire after 48 hours.

## 8. Tests (named; P0/P1 PR)

- **Tiers and entitlement:** `test_tier_table_matches_founder` (names, quarters 20/40/400/996/2000, prices in cents 499/4999, 899/8999, 1099/10900, 1599/15000), `test_legacy_unlimited_even_when_paying`, `test_named_unlimited_aj`, `test_estate_family_estate_holders_are_gold`, `test_tier_computed_at_read_not_frozen_at_mint`, `test_upgrade_downgrade_cancel_change_cap`, `test_snapshot_marks_non_anonymous_pre_cutoff_legacy`, `test_late_linked_anonymous_not_legacy`, `test_no_doc_after_snapshot_is_free_not_legacy`, `test_snapshot_pending_503`, `test_cutoff_is_2026_11_27T05Z`, `test_guest_cap_20q_and_5_items`, `test_guest_direct_write_denied_after_p3` (rules), `test_seed_unstamped_weighs_4_and_forged_set_id_earns_nothing`, `test_seed_shell_zero_only_if_referenced`, `test_seed_sums_email_and_uid_keys_once_per_path`, `test_free_11th_item_denied_on_each_path` (parametrized: manual, catalog, review commit, bulk, scan, mint template, roll wizard, import, Morgan add), `test_morgan_add_counts`, `test_client_cannot_send_server_fields_422`, `test_entitlement_error_503_not_403`.
- **Counter and sets:** `test_replay_no_increment`, `test_ids_independent_of_request_order`, `test_hash_mismatch_409_before_replay`, `test_delete_missing_doc_noop`, `test_delete_clamps_forged_weight_and_floors_at_zero`, `test_restore_retry_idempotent`, `test_group_requires_server_shell_and_owned_children`, `test_group_no_lifetime_refund`, **`test_set_coin_ungroup_charges_lifetime_and_blocks_over_cap`**, `test_loose_group_ungroup_no_double_charge`, `test_ungroup_blocked_never_deletes`, **`test_group_uses_stored_weight_delta_not_fixed_4_to_1`**, **`test_repeated_regroup_cannot_free_quarters`**, `test_client_cannot_write_set_fields_after_p3` (rules), `test_p1_client_cannot_remove_set_shell_id` (rules), `test_recount_counts_weight1_without_valid_link_as_4`, **`test_mint_set_coins_then_ungroup_cannot_exceed_free_cap`**, `test_break_up_counts_children_removes_counted_source`, `test_capped_bulk_single_txn_all_or_nothing`, `test_bulk_over_150_422_for_capped`, `test_two_tab_concurrent_add_counts_once_each`, `test_nightly_drift_job_never_writes`, `test_softenforce_counts_unstamped_docs`.
- **Batching (500 documents):** `test_group_500_items_runs_four_batches_each_under_500_docs`, `test_ungroup_resumes_from_cursor`, `test_clear_all_batches_of_150`, `test_batch_retry_no_double_count`, `test_ungroup_precheck_blocks_before_first_batch`.
- **Guard:** `test_guard_blocks_set_create_delete_batch_transaction_bulkwriter`, `test_guard_blocks_collection_add`, `test_guard_blocks_merge_set_on_item_path`, `test_guard_covers_main_py_own_client`, `test_no_firestore_client_outside_allowlist`, `test_no_unfunneled_item_writes`, `test_no_unwrapped_ai_calls`.
- **Stripe and cancel:** `test_checkout_rejects_unknown_tier_422`, `test_checkout_cannot_pay_copper_get_sovereign`, `test_checkout_uses_price_ids_not_price_data`, `test_checkout_metadata_has_email_and_user_key`, `test_price_env_missing_fails_closed`, `test_webhook_tier_from_price_id_not_metadata`, `test_unknown_price_id_changes_nothing`, `test_webhook_updates_entitlement_doc`, `test_webhook_status_active_trialing_only`, `test_past_due_grace_then_unpaid`, `test_event_marker_same_txn_no_loss`, `test_webhook_exception_returns_500`, `test_out_of_order_event_ignored`, `test_reconcile_job_fixes_lost_event`, `test_cancel_sets_read_only_all_items_visible`, `test_cancel_legacy_not_read_only`, `test_resubscribe_clears_read_only`, `test_billing_gate_503_until_ai_caps_complete`, **`test_topup_older_than_hwm_still_granted`**, `test_topup_replay_no_double_credit`, `test_topup_never_touches_hwm`, `test_topup_ineligible_account_goes_to_unresolved`, `test_cancel_forfeits_topup_credits`, **`test_read_only_account_can_restore_from_trash`**.
- **Export:** `test_basic_zip_has_csv_and_own_photos_no_links`, `test_basic_csv_excludes_ai_valuations_stock_images`, `test_basic_export_available_when_read_only`, `test_large_export_job_authenticated_download_no_signed_link`, `test_full_export_price_is_6x_monthly_of_last_tier`, `test_full_export_402_until_purchased`, `test_full_export_no_last_tier_402`.
- **AI:** `test_guest_cap_is_10_cents`, `test_aj_exempt_never_429`, `test_first_month_cap_is_plan_price`, `test_month2_caps_match_founder_table`, `test_legacy_cap_is_max_of_paid_and_gold`, `test_settle_uses_reserved_period_key`, `test_settle_release_idempotent`, `test_manual_add_never_blocked_by_ai_cap`, `test_daily_limits_removed`, `test_topup_credits_after_cap`, `test_kill_switch_503`.
- **Fallback:** `test_over_cap_flag_blocks_further_adds`, `test_cap_enforcement_start_date_respected`.
- **Wishlist:** `test_reserve_rate_limit_shared_across_instances`, `test_reserve_expired_410`, `test_buyer_secret_undoes_own_only`, `test_reserve_trusted_proxy_ip`.
- **Rules:** §6 R5.

## 9. Carried from earlier plans (restated)

| # | Change |
| :--- | :--- |
| C1 | **Routing:** `CN` to `coins`, `BN` to `currency`, `MD`/`TK`/`ST` to `world_items` (`nac_code_parser.dart:43-47`). |
| C2 | **Idempotency:** §3.3. |
| C3 | **One write-site inventory:** Appendix A plus §11. The Phase 1A allowlist includes every Flutter file in A.1 and A.3. |
| C4 | **Pydantic v2:** no `Field(..., decimal_places=2)`; use a `field_validator` that quantizes; `import Decimal`; store `purchase_price` as a quantized string. |
| C5 | **Guest limiter** uses the trusted proxy hop (§7). One limit: 30/min. |
| C6 | **Signed URLs:** do not gate IAM `signBlob` on `hasattr(creds, "sign_bytes")`. Use `google.auth.iam.Signer`. Call `firebase_admin.initialize_app()` once. |
| C7 | **Pagination:** v2.4 sorts in memory by `(year, kind_rank, nac_code)`. The cursor is the last `nac_code` (unique). No new index. A test runs the list endpoint over combinations of `kind`, `cc`, `facility`, `denomination_class`, `q`. |
| C8 | **Two-sided gate:** `comm -23` and `comm -13` both empty. Gate 1 also fails if `numista_backend/firestore.rules` changes. |
| C9 | **Seed:** v2.4's `numista_backend/data/catalog_dev_fixture.json` (15 canonical vectors, §2.2, updated per §9.3 item 8). A test loads every vector through `CatalogItem`. |
| C10 | **Commercial-authority regex:** word-boundary anchored; applies to `title`, `obverse_description`, `historical_notes` and citations. |
| C11 | **Julian 1977:** an AI-written addition (v2.5 listed it as pre-1929; v2.6 relabeled it GPO public domain under 17 U.S.C. § 105). It was published by the Token and Medal Society, so treat it as in copyright. Remove it from every public-domain or GPO row and drop `US_GPO_JULIAN_1977`. Use it only as a plain citation and cross-reference code. Copy no text, tables or images. |

## 10. v2.4 §9.3 file list, restated with v3.2 changes

**Part A: the 4 `BETA TEST/` removals** (unchanged): `git rm --cached` of the three `BETA TEST/Grok Bot/8 OCT 26/BATONS/*V2.2.md` files (local copies stay on disk), and restore `BETA TEST/Grok Bot/8 OCT 26/WHOSE_TURN.md` to `e0fdc2a5` in the git index.

**Part B**

| # | File | v3.2 status |
| :--- | :--- | :--- |
| 5 | `numista_backend/requirements.txt` | Pin `google-cloud-firestore==<version verified at P0, ≥2.16.0>` (aggregation support) and `stripe`. |
| 6 | `numista_backend/catalog_nac1.py` | Unchanged from v2.4 item 6. |
| 7 | `numista_backend/catalog_models.py` | Unchanged from v2.4 item 7, plus C4. |
| 8 | `numista_backend/data/catalog_dev_fixture.json` | Unchanged from v2.4 item 8 (C9). |
| 9 | `numista_backend/catalog_service.py` | Uses the funnel, mint and seed, the §3.3 transaction, `ai_budget`. Remove `_bootstrap_vault_counter_if_missing`, `vault_counters`, `catalog_trial_lifetime_adds`. |
| 10 | `numista_backend/routes/catalog_routes.py` | Unchanged from v2.4 item 10. |
| 11 | `numista_backend/tests/test_catalog_nac1_and_schema.py`, `numista_tests/test_nac1_validator.py` | Unchanged from v2.4 item 11. |
| 12 | `numista_backend/tests/test_catalog_routes_and_service.py` and the other v2.4 item 12 files | Add the §8 tests. |
| 13 | `numista_mobile/test/nac_code_parser_test.dart` | Unchanged from v2.4 item 13. |

**Added by v3.1 and v3.2**

| # | File |
| :--- | :--- |
| 14 | `numista_backend/collection_funnel.py`, `routes/collection_routes.py` |
| 15 | `numista_backend/firestore_guard.py`, wired into `main.py` and `routes/deps.py` |
| 16 | `numista_backend/ai_budget.py` and call-site wiring |
| 17 | `numista_backend/scripts/snapshot_legacy.py` (required, §2.3; owner Grok CoS) |
| 18 | `numista_backend/tier_gatekeeper.py` (§1.1, §2.2, §4.3) |
| 19 | `numista_backend/routes/payment_routes.py` (§4.1, §4.2), `routes/export_routes.py` (§4.6), the daily reconcile job |
| 20 | Server routes that create or delete items call the funnel (Appendix A.4); `merge-set` callers converted to `update()` |
| 21 | `numista_backend/routes/affiliate_routes.py` (§7) |
| 22 | `numista_mobile/firestore.rules` and `numista_mobile/firestore.rules.test.js` |
| 23 | Flutter: every file in Appendix A.1 and A.3, `public_wishlist_view_screen.dart`, `wishlist_screen.dart:1039`, the upgrade screen (four tiers, prices, read-only state), the cancel and export screen |
| 24 | `config/min_app_version`, `config/entitlement_policy`, `config/ai_caps`, `config/ai_kill_switch`, and the Flutter version check |
| 25 | Header comment on `numista_backend/firestore.rules` marking it non-live |

Gate 1 allows `numista_mobile/firestore.rules` and its test file only. **No execute** until the P0 inventory is verified and Eric types YES.

## 11. Appendix A additions (to `NET-646_V3.0_APPENDIX_WRITE_AUDIT.md`)

- **A.7 Server clients:** `main.py:356` (`db = firestore.Client(credentials=credentials, project=PROJECT_ID)`) is the main writer's own client, separate from `routes/deps.py:24`. The repo has 222 `firestore.Client(` or `firestore.client()` constructions including scripts and tests, and about 149 in non-test `.py` files (GB's count). The library-level guard (§3.8) covers all server-image clients. P0 lists the ones in the server image.
- **A.8 Set operations as funnel ops:** `add_coins_hub.dart:1997/2036/2067` becomes `mint_template`; `set_grouping_service.dart:75/86` becomes `group`; `:171/175` becomes `ungroup`; `/api/review/break_up_set` becomes `break_up`; `settings_screen.dart:1770` and `main.py:9340` become `clear_all`.
- **A.9 Merge-set callers converted to `update()`:** `main.py:1544`, `3757`, `1991`, `routes/grade_review_routes.py:355`.
- **A.10 Billing:** `payment_routes.py` checkout (~50–73) and webhook (~176–240); `tier_gatekeeper.py` `create_upgrade_checkout_session` (~174–204), `lock_overflow_coins`, `unlock_user_coins`.

## 12. Open items for Eric (`[PENDING ERIC]`)

Resolved by your 7:08 PM answers: the guest AI cap (\$0.10), top-up price and forfeiture on cancel, full-export price (6 x the monthly price of the last tier), the photo zip, AJ's AI cap (none), and the snapshot owner (Grok CoS).

1. **Full export for an account that never paid.** A Legacy Free account has no last tier, so no price exists. The endpoint returns `402 FULL_EXPORT_NO_PRICE`. Pick a price, or say they get it free.
2. **Legacy account that buys top-ups without a subscription:** keep the credits? The plan assumes yes.
3. **Founder account `eric.seaman@yahoo.com`** (your personal account) has no special handling. Say so if it should become a named unlimited or admin exception.
4. **Stripe prices to create:** 8 subscription prices, 1 top-up price, and 4 full-export prices (6 x monthly), and give the ids to the backend env.
5. **Stripe go-live timing** if P1 slips past Nov 20 (§3.6).
6. **Hand refunds:** a top-up or export payment that lands on an ineligible account is refunded by hand (§4.2). OK?

OVER — drafted by Claude in Antigravity, filed as Argon (AG CoS).
