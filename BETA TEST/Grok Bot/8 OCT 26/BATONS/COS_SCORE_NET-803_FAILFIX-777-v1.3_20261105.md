# GB CoS SCORE — NET-803 / FAILFIX_PLAN_NET-777_CATALOG_v1.3 (+ MISSING_IMAGES.csv)

- **Scorer:** Grok Bot Chief of Staff (GB CoS scorer executor)
- **Date / Time:** 2026-11-05 ~2:40 PM ET (America/New_York)
- **Targets:** `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.3.md` (359 lines), `docs/MISSING_IMAGES.csv` (3,202 rows), `RADIO NET/ARGON_REVIEW_FAILFIX_PLAN_CATALOG_v1.3.md`
- **Mode:** SCORE ONLY — no code run in repo, no deploy, no merge, no Firestore, no Eric ping, no outbound messages
- **Argon Score (prior):** 98 / 100 PASS
- **CoS Score:** **85 / 100 (`FAIL` <95)**
- **SAG Score (this turn, grok-4.7 via xAI API, key never printed):** **70 / 100 (`FAIL`)**
- **Eric YES gate:** **BLOCKED.** Revise baton **NET-804** filed to AG CoS v4 for v1.4.

Why CoS is lower than Argon: this turn CoS checked the plan against the real repo (read-only `git show dev:` / `Select-String`) and live site, not just against the plan's own claims. Several "RESOLVED" rows do not hold against the code.

---

## 1. The 5 SAG must-fixes from NET-788, verified against the actual files

| # | SAG must-fix | Plan v1.3 lines (quoted) | Repo / CSV reality (this turn) | CoS verdict |
|---|---|---|---|---|
| 1 | AI replicas only in `ai_replica_images`, never primary/card/index | L63 "**AI-generated coin replicas may live ONLY in the labeled metadata field `ai_replica_images`.**" L64 "**AI replicas are STRICTLY FORBIDDEN from being assigned to `primary_image`, `type_image`, card art, or the public browse index.**" L271 "Any AI replica image is stored exclusively in full detail records under `ai_replica_images`." | Plan text only (no code yet). Consistent with Eric's 5 Nov 10:04 AM decision. | **CLOSED** |
| 2 | Rollback + preview-before-live | L300 `gsutil versioning set on gs://numista-catalog-assets`; L312 `git checkout HEAD~1 -- numista_mobile/firebase.json`; L315 "revert the version pointer ... back to the prior known good index (`catalog_index_v20261103.json`)"; L322 `firebase hosting:channel:deploy pre-ads-preview --expires 7d`; L332 "Only upon Field Tester sign-off and Founder Eric's explicit typed YES" | `catalog_index_v20261103.json` does **not exist**; the live asset is `assets/catalog/catalog_public_v1.json` (5,895,259 bytes, `dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart:60`). `HEAD~1` is not a pinned rollback target. Preview gate itself is good. | **PARTIAL** |
| 3 | CSV hygiene | L95 "All 81 ... reclassified ... Zero blank external mirror rows remain." L96 "Zero boolean strings remain." L98 "`$0.00` across all 3,202 rows." L357 "CSV fully scrubbed and verified 100% clean" | Verified: 0 blank `candidate_source`; 0 `True/False` mint marks; all `$0.00`; 0 album/club titles in `series`; all 3,202 `PASSED_GENERIC_ONLY`. **But:** (a) §2.D table L106–109 still says 2,273 / 747 / 181 / 1 while the CSV is **2,354 / 666 / 181 / 1**; (b) 147 `mint_mark` cells hold issuer/designer text (e.g. `Bureau of Engraving and Printing` 59, `Franklin Mint` 15, `Morgan, George T.` 1); (c) **15 Franklin Mint medals (1969–73) and Medallic Art Co. medals (1932, 1969–71) are labeled `Public Domain (US Govt / Pre-1929)` — false**; (d) 1,181 staged-laptop rows carry a blanket PD label with no per-asset provenance. "100% clean" is not supportable. | **PARTIAL** |
| 4 | Hard monthly $ cap + alert | L114 "**Hard Monthly Cap:** **$25.00 / month** covering GCS storage + Cloud CDN egress." L119–120 alerts at $20 / $25. L121 "Tier 4 studio photography utilizes existing owned equipment only." | Cloud Billing budgets/alerts **notify; they do not stop spend**. No kill-switch or owner action named. Live site is **Firebase Hosting** (`firebase.json` `"public": "build/web"`), not Cloud CDN; L115 estimate counts ~400 KB JSON per visit and no image bytes. | **PARTIAL** |
| 5 | Signed-in Ask Morgan uses MorganChatPopout, not `/?route=AiChatScreen` | L194–205 `showDialog(... child: MorganChatPopout( initialPrompt: 'Tell me about ...' ), )`; L207 "wired to Gemini 3.5 Flash backend" | Real constructor (`numista_mobile/lib/widgets/morgan_chat_popout.dart:11-16`): `const MorganChatPopout({super.key, this.initialQuery, required this.onClose, this.onNavigateToCollection})`. Snippet uses a non-existent `initialPrompt` and omits required `onClose` → **will not compile**. Widget is a draggable overlay used at `base_layout.dart:1094`, not a Dialog child. "Gemini 3.5 Flash" unverified. Direction is right; spec is wrong. | **PARTIAL** |

## 2. Other CoS checklist findings

| Check | Result | Evidence |
|---|---|---|
| Plan-only; no deploy/merge | PASS | L13, L18 |
| `origin/main` @ `9f04550a` | PASS | L15; `git rev-parse origin/main` = `9f04550a45fa…` this turn |
| Stripe OFF | PASS | L16 |
| Firestore writes/rules separate YES | PASS | L17 "NOT an approval for Firestore database writes, seeding, or Firestore security rules changes" |
| No AJ / user PII | PASS | CSV regex scan: 0 emails, phones, street addresses, AJ/family-name/owner/receipt/invoice tokens; `aj_photo`/`aj_currency` appear only in the exclusion regex (L127) |
| Catalog-first / AI never primary | PASS (text) | L62–66, L271 |
| No hotlinked / outbound images or links | **FAIL** | Existing live detail modal has a clickable outbound link: `dev:…/catalog/catalog_browse_screen.dart:1010-1017` `InkWell(onTap: () async { final uri = Uri.tryParse(sourceUrl); if (uri != null) await launchUrl(uri); }, child: const Text('(source)' …` — plan never removes it |
| Nothing invented; sources cited | **FAIL** | Plan cites `numista_mobile/lib/screens/catalog_browse_screen.dart`; real file is `…/screens/catalog/catalog_browse_screen.dart` and exists **only on `dev`**, not `p7-v8.9`. Quoted blocks are not verbatim: real 223–228 is `void _openAskMorgan({String? initialPrompt}) { Navigator.of(context).pushNamed('/?route=AiChatScreen', …` (not an IconButton); real 209–214 has no "BUG" comment; real method at 810 is `_showItemDetailModal`, not `_showDetailModal`; false PD license labels in CSV |
| $ caps | PARTIAL | Alert-only "hard cap" (see MF-4) |
| Rollback + tests | PARTIAL | Preview checklist good; rollback names a missing file |
| Fits Thanksgiving ad launch | PARTIAL | Plan names `numista-vault.web.app`; ads land on `https://numista.ai/` — confirm host |
| No wholesale values on public surfaces | NOT STATED | Add one line: public catalog shows CDN CPG retail only, never wholesale |
| US-only scope | **FAIL** | Public catalog still has a `Foreign Coins` tab: `dev:…/catalog_browse_screen.dart:599-602` `_TypeTab(label: 'Foreign Coins', … onTap: () => _onTypeChanged('foreign'))` |

**CoS scoring breakdown:** Founder image / no-outbound / PII (30) = 26 (−3 live `(source)` outbound link not removed, −1 false PD labels); Standing locks & plan-only (20) = 20; Fixes + tests + accurate code citations (25) = 20 (−3 wrong file/branch and non-verbatim quotes, −2 non-compiling MorganChatPopout snippet); CSV hygiene (15) = 12 (stale tier table, 147 non-mark mint_mark cells, false PD); Launch fit / rollback / $ cap / US-only (10) = 7 (alert-only cap, rollback to missing file, Foreign tab). **Total 85 — FAIL.**

---

## 3. CoS + SAG must-fixes for v1.4 (merged, in order)

1. **Pin the real target:** `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` on `dev`; re-quote every block verbatim with real line numbers (`_openAskMorgan` 223–228, `_onTypeChanged` 209–214, era filter 129–130, `_showItemDetailModal` 810, loader 60).
2. **Remove the live outbound `(source)` link** at 1010–1017 (plain-text credit only). Keep all 167 `candidate_source` URLs internal notes, never `src`/`href`.
3. **US-only:** remove/hide the `Foreign Coins` tab (599–602) from the public catalog before ads.
4. **Fix the MorganChatPopout spec:** `initialQuery:` + required `onClose:`, and say how it is hosted (overlay like `base_layout.dart:1094`, or a dialog wrapper that supplies size/position). Drop the "Gemini 3.5 Flash" claim unless cited.
5. **CSV truth:** correct the Franklin Mint / Medallic Art (and any other private, post-1929) license labels and exclude them from PD ingest until a real license is cited; move non-mark text out of `mint_mark` (e.g. to `issuer`); update §2.D to 2,354 / 666 / 181 / 1; drop "100% clean".
6. **Real $ stop:** state that alerts don't stop spend; add an enforced stop (e.g. budget → Pub/Sub → disable billing or pull the image path) or a named human owner + action within N hours; price on Firebase Hosting egress including image bytes.
7. **Real rollback target:** pin `assets/catalog/catalog_public_v1.json` (+ git SHA) as the known-good index; name the prior Hosting release to roll back to, not `HEAD~1`.
8. Non-blocking: pre-federal filter should not keep `|| year < 1792` (SAG); add "CDN CPG retail only, no wholesale" line; confirm ad landing host (`numista.ai` vs `numista-vault.web.app`); add Foreign-tab/zero-`launchUrl` checks to the preview checklist.

---

## 4. SAG Result (independent; grok-4.7; key never printed)

SAG was given the v1.3 plan, the Argon v1.3 review, its own NET-788 result, and a CoS fact sheet of read-only repo/CSV checks (`/workspace/net803/sag/facts803.md` on the CoS box).

```
## SAG_SCORE: 70/100 FAIL
## MUST_FIX (ordered, blocking before Eric YES; or 'NONE blocking')
1. Execution target is wrong. The screen is `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` on `dev` only. It is not at `lib/screens/catalog_browse_screen.dart` and it is not on `p7-v8.9`. Quoted blocks are not the repo (`_openAskMorgan` / `pushNamed`, `_showItemDetailModal`, no “BUG” comment). Pin `dev` and cite the real methods.
2. Standing no-outbound rule is not closed. Dev detail modal lines 1010–1017 are an InkWell `(source)` that calls `launchUrl(sourceUrl)`. The plan never deletes that link. Attributions stay plain text. The 167 `candidate_source` URLs stay internal notes, never `src` or `href`.
3. US-only scope is not closed. Dev lines 599–602 still expose a public `Foreign Coins` tab (`_onTypeChanged('foreign')`). Remove it. Do not put private-mint medals outside US coins/notes/currency (current and former states, territories, possessions) on the public index.
4. v1.2 must-fix 3 is not closed. Do not treat `docs/MISSING_IMAGES.csv` as the acquire list. Facts: 147 `mint_mark` values are not mint marks (issuer/designer strings, including `Morgan, George T.`); 15 Franklin Mint medals (1969–1973) and Medallic Art Co. medals are labeled `Public Domain (US Govt / Pre-1929)`, which is false; 1,181 staged-laptop rows use a blanket PD label with no per-asset provenance; §2.D still says 2,273 / 747 while the CSV is Tier1 2354 / Tier2 666 / Tier3 181 / Tier4 1. Drop the “100% clean” claim. Exclude false-PD rows from GCS ingest.
5. v1.2 must-fix 4 is not closed. $20/$25 Cloud Monitoring alerts do not stop spend. Say that. Add a real hard stop, priced on Firebase Hosting (`public: build/web`), not Cloud CDN, and include catalog image bytes, not only ~400 KB of JSON per visit. Procurement stays $0; Tier 4 is existing owned photos only.
6. v1.2 must-fix 2 is not closed. §8.A.3 rolls back to `catalog_index_v20261103.json`, which does not exist. The live asset is `assets/catalog/catalog_public_v1.json` (5,895,259 bytes). Pin that file and a tested SHA. `git checkout HEAD~1` is not a rollback.
7. v1.2 must-fix 5 is not closed as written. `MorganChatPopout` takes `initialQuery` and required `onClose`, not `initialPrompt`. The snippet would not compile. It is an overlay panel in `base_layout.dart`, not a drop-in dialog child. Do not claim Gemini 3.5 Flash; that is not verified.
## NON_BLOCKING
- v1.2 must-fix 1 is closed in plan text: AI replicas only in `ai_replica_images`, never `primary_image`, `type_image`, card art, or the browse index; placeholder SVG if no authentic photo.
- Pre-federal filter still ORs `year < 1792`, which was the misclassification. Use the C1 flag only.
- State in one line: no wholesale values on public catalog surfaces; CDN CPG retail only.
- Preview checklist must add: zero `launchUrl`, no Foreign tab, false-PD rows absent, first load against the real JSON name.
- Ad landing is named as `numista-vault.web.app`. Confirm that is the Thanksgiving host versus `numista.ai`.
- v1.2 nits that are actually in this text: `history.back()` plus `popstate`, versioned index filename, softer signed-out Morgan copy, Eric YES is not a Firestore/rules YES, Stripe OFF, `origin/main` @ `9f04550a`, plan-only until YES.
## PII_FINDINGS
- CSV fact check: 3,202 rows, every `pii_gate_status=PASSED_GENERIC_ONLY`. No emails, phones, street addresses, AJ/family-name/owner/receipt/invoice tokens. Cost column is `$0.00`. No collection value or ownership fields in the plan.
- Plan uses `aj_photo` / `aj_currency` only inside an exclusion regex, not as leaked identifiers.
- `Morgan, George T.` in `mint_mark` is the historical designer, not a user. It is bad catalog data, not user PII.
- Residual, not a clean bill for ingest: 81 rows are still “Pending Internal Staged Archive Scan.” Personal-collection, receipt, and AJ images stay out. The claimed hash index of user uploads is not shown in the facts.
## 3_SENTENCE_PLAIN_ENGLISH (for founder Eric, plain words)
I am not ready for you to type YES. The plan now says AI pictures cannot be the main photo, and it keeps the live site locked until a preview check, but the missing-image list still has wrong public-domain labels and bad mint marks, the $25 limit only emails you and does not stop the bill, and the live catalog still has an outside link and a Foreign Coins tab this plan never removes. It also names the wrong code file and an undo copy of the catalog that is not in the repo, so this needs another pass before you approve it.
## RATIONALE (brief)
Independent of Argon 98. Locks, plan-only status, Stripe OFF, separate Firestore YES, and the written AI-replica rule are real. Score is 70 because facts contradict the “all five RESOLVED / CSV 100% clean” table: alerts are not a hard cap and the meter is Firebase Hosting not Cloud CDN; rollback names a missing JSON; the signed-in snippet does not match `MorganChatPopout`; the cited screen path is wrong; a live `launchUrl` and a Foreign Coins tab are unfixed. Those block Eric YES.
```

---

## 5. Three-Sentence Plain English (CoS, for Eric)

The new catalog plan does now say AI pictures can never be the main photo, and it keeps everything on paper with main locked, Stripe off and a preview check before anything goes live. But when I checked it against the real code, it points at the wrong file, its Ask Morgan fix would not compile, it misses a clickable "(source)" link and a "Foreign Coins" tab that are on the catalog today, and the $25 "hard cap" is really just an email alert. The missing-image list is much cleaner but still calls some 1970s Franklin Mint medals "public domain," so I sent it back to AG for one more revision (v1.4) — no YES needed from you yet.

## 6. Next Actions (no execute)

1. **AG CoS v4:** take **BATON_NET-804** → file `FAILFIX_PLAN_NET-777_CATALOG_v1.4.md` (+ corrected `MISSING_IMAGES.csv`) clearing §3 items 1–7. Then Argon → GB CoS → SAG → Eric typed YES.
2. **Desk:** do not chase Eric for YES on NET-803.
3. Locks unchanged: `origin/main @ 9f04550a`, Stripe OFF, zero deploys, zero Firestore writes/rules without separate YES.

**WHOSE_TURN:** AG CoS v4 (v1.4 per NET-804) → Argon → GB CoS → SAG → Eric typed YES only after CoS ≥95 and SAG ≥95.
