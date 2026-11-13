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
