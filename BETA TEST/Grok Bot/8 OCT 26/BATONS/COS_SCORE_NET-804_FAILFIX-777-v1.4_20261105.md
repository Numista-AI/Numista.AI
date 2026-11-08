# GB CoS SCORE — NET-804 / FAILFIX_PLAN_NET-777_CATALOG_v1.4

- **Scorer:** Grok Bot Chief of Staff · 2026-11-05 ~3:55 PM ET
- **Targets:** `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.4.md`, `docs/MISSING_IMAGES.csv` (3,202), `ARGON_REVIEW_FAILFIX_PLAN_CATALOG_v1.4.md` (Argon 98)
- **Repo checked:** p7-v8.9 @ a5eeb19b; origin/dev (catalog_browse_screen.dart lives only on dev, 18a8b8e5); origin/main 9f04550a
- **Mode:** SCORE ONLY. No execute, no deploy, no Firestore, nothing to main.
- **CoS:** **89 / 100 FAIL** · **Argon:** 98 · **SAG (grok-4.7):** **85 / 100 FAIL**
- **Eric YES gate:** BLOCKED. Revise baton **NET-808** to AG CoS v4.

## 1. Claim-by-claim verification (real code)

| Claim | Result | Evidence |
|---|---|---|
| MorganChatPopout signature 11-16 | **PASS** | p7 `morgan_chat_popout.dart:11-16` = `{super.key, this.initialQuery, required this.onClose, this.onNavigateToCollection}`; plan snippet matches |
| Foreign Coins tab removed (dev) | **PLAN ONLY — not removed** | origin/dev still has `_TypeTab(label:'Foreign Coins')` at 599-602. Plan specifies deletion (ok for a plan) but closeout table says "Removed / RESOLVED", and Desk relayed "removed on dev" — false as a state claim |
| `(source)` outbound link removed | **PLAN ONLY — not removed** | origin/dev `InkWell … launchUrl(uri)` still at 1010-1017 |
| Tier table = CSV | **PASS** | CSV 2,354 / 639 / 181 / 1 / 27 = 3,202, matches §2.D |
| 147 mint_mark cleanups | **PASS (end state)** | mint_mark only `'' 1214, S 730, D 619, P 472, O 104, W 36, CC 27`; the 147 delta itself is not re-derivable |
| $25/mo egress stop | **FAIL** | `stop-public-egress` is plan text only; bucket `gs://numista-catalog-assets` and topic `projects/numista-ai/…` unverified (live studio bucket is in a different project); no human owner / manual shutoff |
| Rollback to 9f04550a | **FAIL** | `catalog_public_v1.json` and `catalog_browse_screen.dart` do not exist at 9f04550a; 9f04550a is not an ancestor of dev; `git checkout 9f04550a -- numista_mobile/firebase.json` drops dev's +8 catalog hosting lines. No prior Hosting release / `hosting:clone` (baton MF-7) |
| Pre-federal C1 flag-only | PASS | dev JSON: 9 records flagged |
| Line cites | −1 | `_onTypeChanged` cited 205-210, real 209-214 |
| Locks / PII | PASS | main 9f04550a, Stripe OFF, no Firestore, no AJ PII in plan or CSV |

**Breakdown:** Image/AI-field/PII (30)=29 · Locks & plan-only (20)=18 (RESOLVED-as-done wording) · Baton MF closeout (25)=19 (MF-6 spend stop, MF-7 rollback open) · CSV (15)=15 · Launch fit (10)=8 (no "CPG retail only, no wholesale" line; numista.ai landing not confirmed). **Total 89.**

## 2. Must-fixes (blocking)
1. **Rollback:** pin code rollback to the pre-execute dev SHA (now 18a8b8e5) via `git revert <execute SHA>`; name the prior Firebase Hosting release to restore (`firebase hosting:clone` / console rollback). Remove every `9f04550a` file-checkout from §9.A.
2. **Spend stop:** use real, verified bucket/project/topic ids (or mark "to be created, owner X"); name a human owner and a manual shutoff (disable public access / take preview channel down); cover Firebase Hosting egress, not only bucket IAM.
3. **Status wording:** change "Removed / RESOLVED" for Foreign tab and `(source)` link to "SPECIFIED — to be removed at execute"; keep both in the FT checklist.
4. Fix `_onTypeChanged` cite to 209-214; add one line "public values CDN CPG retail only, no wholesale"; confirm ad landing host `numista.ai`.

## 3. PII
NONE. CSV 3,202 rows generic; no AJ data.
