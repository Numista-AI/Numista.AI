# SAG REVIEW — NET-827 FAILFIX B1-B5 plan v1.9.1 (Code Writing)

- Reviewer: Stand Alone Grok through xAI API, model grok-4.7, temperature 0
- Date: 2026-11-10, America/New_York
- Artifact under review: A1 SHA-256 ec9c50b49c4d19d45a4a545b3171b98bb8aeb26761036070c9cadabbde0bfddb (159,766 B)
- Packet SHA-256: 84c26956ae754b02224f1bfdd61f92076dce6968e184c0ecac0fbb192f513438
- API response id: 4765de99-bbe4-9a44-b8c1-104a41daf16b
- Attempts: ['ok']
- Authority: Eric 7:13 PM ET (t2553u), SAG review via API only. Mode: SCORE ONLY; no execute, deploy, Firestore, main, or Stripe changes.

**83 / 100 — REVISE.** Full A1 reviewed (not bound by A2’s 100). SHA-256 reviewed: `ec9c50b49c4d19d45a4a545b3171b98bb8aeb26761036070c9cadabbde0bfddb`. This review grants no build, deploy, Firestore, rules, Stripe, or other permission.

### Material findings

1. **Beta Special grant can sell a permanent paid tier for $30** (payment correctness, fail-open).  
   **A1 L285, L370, L373, L382, L394.** Session metadata is only `user_uid`, `target_tier`, `interval`, `discount_kind` — no Beta marker. The grant transaction unconditionally sets `users/{uid}.stripe_tier` and `subscription_status="active"`, and the same transaction’s ledger line is `kind: "subscription"|"beta"`. Beta “on grant” only *adds* `beta_special_until` / `beta_special_purchased`. §4.4 then says a Beta refund must **not** touch `stripe_tier`. Schema still requires `tier` in `PURCHASABLE` (L285 area / §4.1). A free user can send `tier=estate` + `beta_special=true`, pay 3000 cents, and keep Gold after the 6 months and after refund. §7.1 never asserts `stripe_tier` is unchanged by a Beta purchase.  
   **Minimal fix:** Server-set `metadata.purchase_kind=beta|subscription`. Beta grant writes only `entitlements` Beta fields, ledger `kind=beta`, and unlock; it must not set `stripe_tier` or `subscription_status`. Refund/lost-dispute still must not clear a *pre-existing* subscription tier. Pytest: free user buys Beta → `stripe_tier` absent, unlimited until expiry, then lock to 10; existing Copper + Beta refund → Copper remains.

2. **Full refund / cancel / lost dispute can fail to revoke if `stripe_tier` lives on `users/{email}`** (Eric: full refund and lost dispute revoke).  
   **A1 L383, L396, L486.** Revoke only “clears” `users/{uid}.stripe_tier`. `load_entitlement_profile` does `profile = dict(email_doc); profile.update(uid_doc)`, so a missing uid field keeps the email value. A3 `payment_routes.py:206-225` and `:233-238` write `stripe_tier` to `target_id = user_uid or customer_email`; invoice/subscription events often lack `client_reference_id`, so production tiers can sit on `users/{email}`. Today’s cancel sets `stripe_tier="free"` (A3 L234), which would overwrite in that merge; this plan replaces that with clear-on-uid-only. A field delete does not revoke.  
   **Minimal fix:** On every revoke, set `stripe_tier` to null on **both** `users/{uid}` and `users/{email}` (null must be present so the merge overwrites). Pytest: `stripe_tier` only on `users/{email}`, subscription full-refund → effective tier free and overflow locks.

3. **Required import-graph test cannot pass as written** (execution).  
   **A1 §7.3 (~L1218) and §4.11 row 18.** §7.3 fails if any module imported from `main.py` (including inside functions) contains a data-client constructor or a production bucket literal outside `bucket_for`. A3 `main.py:10623-10624` imports `scripts.refresh_vertex_data_store.py`. The plan itself says that file has a bucket at `:12` (writer-asserted; file not in A3) and is not routed through `env_guard`, and it is not in the §3 file list. The 503-before-call note does not exempt the static walk. §3 then tells the builder to stop. Runtime preview is still fail-closed if the 503 is first; the plan is not executable as specified.  
   **Minimal fix:** Allowlist that module in §7.3 (only caller returns 503 in preview before import/call; production unchanged) **or** add it to §3 and guard it. Re-walk other function-level imports the same way.

### Six checks

(a) **Payment/entitlement:** Subscription allowlist, `price_data` cents (499/4999, 899/8999, 1099/10900, 1599/15000), Christmas `1795669260–1798261199` annual-only no-stack, lease, and partial-vs-full refund rules match Eric; **Beta grant (L370/L382) and email-doc revoke (L383/L396/L486) do not.**  
(b) **Lock/unlock/CSV:** Matches Eric — top-level `locked_coins`, never deleted, both folders deduped, coins only, CSV always and not limit-blocked, lazy lock with server add/by-id checks; Q13 order left open (`created_at` → `added_at` → 0).  
(c) **Rules/permissions:** No NET-827 rules change; A3 `firestore.rules:345-348` deny-all covers `locked_coins`, `entitlements`, `stripe_customers`, `stripe_payments` (no owner lock-out). Optional RX diff matches A3 `:55-58`, `:63-66`, `:85-88`, `:110`, `:115`. Residual: client-writable `power_user` / `creation_timestamp` (A3 rules `:85-88`; risks 14–15) stay open until RX.  
(d) **Preview/secrets:** Separate preview project, test keys, env_guard fail-closed, no p7-gate sign-in, synthetic Auth-only testers, holds and Stripe-live OFF held; no secrets in the plan.  
(e) **PS 5.1 / tests / RX:** PV and RX blocks are PS 5.1-shaped (`Invoke-Native`, temp files, SHA-before-write, live re-read, git-blob rollback); D2’s backup clobber is closed. **§7.3 vs §4.11 row 18 is an execution break (finding 3).**  
(f) **Evidence / regression:** Checked citations match A3 (rules deny-all, `payment_routes.py:32/46-75/102-105/141-143/210-238`, `tier_gatekeeper.py:160-168/325-351`, `main.py:342/349/10624`, roll/wishlist `added_at`). No R1–R5 or N1–N3 regression. `scripts/refresh_vertex_data_store.py:12` is writer-asserted. Cosmetic only: `Coin` vs `CoinModel`.
