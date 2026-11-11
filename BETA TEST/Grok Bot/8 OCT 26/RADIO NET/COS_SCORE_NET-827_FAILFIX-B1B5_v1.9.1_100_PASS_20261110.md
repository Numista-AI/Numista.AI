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

**Eric decision (t2560u, relayed by CoS 7:57 PM ET, recorded after scoring; no rescore, plan unchanged):** RX (A1 §9.4, the rules step that closes the client-writable `power_user`/`creation_timestamp` free-limits gap) is now **REQUIRED before go-live**, not optional; it still needs its own scoped Eric YES naming HOLD `41b8bd5f`. Note: the SAG packet was already submitted at about 7:56 PM ET with the pre-amendment record (SHA `d3db8668…f3ee`) and a prompt that did not state this.

## Authority statement
This score **grants no code, git, deploy, Firestore, Firestore rules, Firebase Auth, Storage, Stripe, Secret Manager or go-live authority**. HOLDs `74611e05…` and `41b8bd5f…` and the go-live addendum `c2b6ac93…` (NOT ACTIVE) stay in force. main stays `9f04550a` and Stripe live stays OFF. RX additionally needs its own scoped Eric YES naming HOLD `41b8bd5f`.
