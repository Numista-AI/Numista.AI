# SAG SCORE NET-804 / FAILFIX_PLAN_NET-777_CATALOG_v1.4 (xAI API, grok-4.7, 2026-11-05 ~3:55 PM ET)

Inputs: plan text + GB CoS repo evidence (read-only, p7-v8.9 a5eeb19b / origin/dev / origin/main 9f04550a).

## SAG_SCORE: 85/100 FAIL

## MUST_FIX
1. Rollback in §9.A is unsafe against the repo. `git checkout 9f04550a -- numista_mobile/firebase.json` would strip dev’s extra catalog hosting lines. `catalog_public_v1.json` and `catalog_browse_screen.dart` do not exist at locked main `9f04550a`. No prior Firebase Hosting release and no `hosting:clone` path is named. Pin code rollback to dev `18a8b8e5` (or the pre-execute dev SHA) and name a prior Hosting release to clone back. Do not mark this RESOLVED while it still points at `9f04550a`.
2. §2.E and §9.A invent `gs://numista-catalog-assets` and `projects/numista-ai/topics/billing-budget-alerts`. Neither is verified. The live studio bucket is `numista-uploads-studio-9101802118-8c9a8` in a different project. `stop-public-egress` is plan text only. Name a human owner and a manual shutoff (disable public access or take the preview channel down). Firebase Hosting egress is the priced path ($0.15/GB after 10 GB); bucket IAM alone does not stop it. Do not invent bucket, topic, or project ids.

## NON_BLOCKING
1. `_onTypeChanged` is cited at 205–210; on origin/dev it is 209–214 (baton already gave 209–214). Foreign tab 598–603 and source link 1010–1017 match. Pre-federal 128–130 is close enough (real 129–130).
2. Closeout says outbound link and Foreign Coins were “Removed / RESOLVED.” This file is plan-only. origin/dev still has the Foreign Coins tab and `launchUrl` at 1010–1017. Desk must not treat those edits as already done.
3. No line that public values stay CDN CPG retail only, no wholesale. Ad landing host numista.ai is not confirmed.

## PII_FINDINGS
NONE

## 2_SENTENCE_PLAIN_ENGLISH
The image counts and the Ask Morgan popup now match the real code, but this plan is not safe to approve. The undo steps point at the frozen main copy, which does not contain the catalog files and would strip the catalog web settings, and the $25 stop names a storage bucket and billing alert that are not the live ones, with no person named to shut spending off by hand.

## RATIONALE
Tier split 2354/639/181/1/27 = 3202, mint-mark tokens, MorganChatPopout `initialQuery`/`onClose`/`onNavigateToCollection`, and the flag-only pre-federal check (9 records) match the repo. Locks (main `9f04550a`, Stripe off, no Firestore writes, AI replicas not primary, US-only and no outbound links as future edits) are stated correctly. The rollback pin contradicts the repo and would remove dev catalog hosting config, and the spend-stop resources are unverified inventions with no human fallback, so this cannot clear 95.

## REPO EVIDENCE SENT
REPO EVIDENCE (GB CoS, read-only, 5 Nov 2026 ~3:50 PM ET). Repo MyVertexProject; p7-v8.9 HEAD a5eeb19b; origin/main 9f04550a (locked). catalog_browse_screen.dart exists ONLY on dev/origin/dev (commit 18a8b8e5, 4 Nov); 9f04550a is NOT an ancestor of origin/dev.
1. morgan_chat_popout.dart lines 11-16 (p7-v8.9): const MorganChatPopout({super.key, this.initialQuery, required this.onClose, this.onNavigateToCollection}); hosted as overlay at base_layout.dart:1094. Plan snippet uses initialQuery/onClose/onNavigateToCollection -> MATCHES. Plan wraps it in showDialog (sized wrapper) - acceptable.
2. origin/dev catalog_browse_screen.dart UNCHANGED: Foreign Coins _TypeTab still at 599-602 (label 'Foreign Coins', _onTypeChanged('foreign')); '(source)' InkWell launchUrl(uri) still at 1010-1017. Plan v1.4 is PLAN ONLY, so removal is specified not done; but plan closeout table says "Removed ... RESOLVED" and Desk relayed it as "removed on dev". Plan cites Foreign tab 598-603 (ok). Plan cites _onTypeChanged at 205-210; real is 209-214 (baton gave 209-214). Pre-fed era at 129-130 real; plan says 128-130 ok.
3. docs/MISSING_IMAGES.csv: 3,202 rows. primary_acquisition_tier counts: Tier1 2354, Tier2 639, Tier3 181, Tier4 1, Tier5 27 = 3202 -> MATCHES plan §2.D.
4. mint_mark values: '' 1214, S 730, D 619, P 472, O 104, W 36, CC 27 -> all valid tokens; 147-cleanup count itself not independently re-derivable but end state clean.
5. pre_federal: dev catalog_public_v1.json has pre_federal true for 9 records (18 = is_pre_federal + pre_federal) -> C1 flag-only filter is valid.
6. $25 egress stop: Cloud Function stop-public-egress is PLAN text only; no code anywhere in repo. Plan names bucket gs://numista-catalog-assets and topic projects/numista-ai/topics/billing-budget-alerts; neither bucket nor project id is verified to exist (live studio bucket used today is numista-uploads-studio-9101802118-8c9a8 in a different project). Firebase Hosting egress priced ($0.15/GB after 10GB). No named human owner/manual action fallback.
7. Rollback: plan §9.A says "git checkout 9f04550a -- numista_mobile/firebase.json" and revert catalog index to "assets/catalog/catalog_public_v1.json at git commit 9f04550a". FACT: catalog_public_v1.json and catalog_browse_screen.dart do NOT exist at 9f04550a; dev's firebase.json has +8 catalog lines vs 9f04550a, so that checkout would strip catalog hosting config on dev. No prior Firebase Hosting release / hosting:clone rollback named (baton MF-7 asked for it). Correct pin would be dev SHA 18a8b8e5 (or the pre-execute dev SHA) + prior Hosting release id.
8. Non-blocking baton items: plan has no "CDN CPG retail only, no wholesale" line; ad landing host numista.ai not confirmed; Gemini 3.5 Flash dropped (ok). Preview checklist has Foreign-tab and zero-outbound-link checks (ok).
