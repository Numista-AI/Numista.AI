# GB CoS SCORE — NET-788 / FAILFIX_PLAN_NET-777_CATALOG_v1.2

- **Scorer:** Grok Bot Chief of Staff (GB CoS scorer executor)
- **Date / Time:** 2026-11-05 ~1:45 PM ET (America/New_York)
- **Targets:** `FAILFIX_PLAN_NET-777_CATALOG_v1.2.md`, `MISSING_IMAGES.csv` (3,202 rows), `ARGON_REVIEW_FAILFIX_PLAN_NET-777_CATALOG_v1.2.md`
- **Mode:** SCORE ONLY — no execute, no deploy, no merge, no push, no Eric ping, no outbound messages
- **CoS Score:** **96 / 100 (`PASS` ≥95)**
- **Argon Score (prior):** **96 / 100 (`PASS`)**
- **SAG Score (this turn, grok-4.7 via xAI API):** **75 / 100 (`FAIL`)**
- **Eric YES gate:** **BLOCKED** until AG files a v1.3 (or amend baton) clearing SAG MUST_FIX items below. CoS PASS alone does not authorize YES.

---

## 1. CoS Checklist (this turn)

| Check | Result | Notes |
| :--- | :---: | :--- |
| Plan-only; no deploy / no merge | PASS | Status line 7–8; Review Chain §8 |
| `origin/main` locked `@ 9f04550a` | PASS | Explicit standing lock |
| Stripe OFF | PASS | Explicit standing lock |
| Firestore writes / rules = separate Eric YES | PASS | Zero Firestore writes/seeding stated; YES on this plan ≠ Firestore/rules YES |
| No AJ / user PII in plan or CSV | PASS | Full CSV scan: 0 emails, phones, AJ tokens, owner names, streets, SSNs, Eric/aunt hits; all 3202 `PASSED_GENERIC_ONLY` |
| No outbound / hotlinked images on live site; internal GCS only | PASS | CSP bridge deleted; GCS-only serving; CSV `candidate_source` URLs are acquisition notes only (167 Wikimedia/Met/ANS) — must never become `src`/`href` |
| AI replicas only in labeled `ai_replica_images`, never primary | **GAP** | Standing catalog-first rule not named in v1.2 — logged as must-fix for v1.3 (does not alone drop CoS below 95 for plan-only review) |
| Nothing invented; sources cited | PASS | Line-cited Flutter/firebase.json/build script; master JSONL counts; batons |
| Cost $ caps | PASS* | `$0.00` acquisition + `~$0.032/mo` storage stated; SAG correctly flags missing hard egress/ad-traffic cap — non-blocking for CoS plan-only, required before execute |
| Rollback + test steps | PARTIAL | Per-fix Test Steps present for Fixes 1–6; **no dedicated rollback section** — SAG blocking |
| Fits Thanksgiving Meta ad launch priority | PASS (implicit) | Public catalog images, deep links, Ask Morgan CTA, `<2s` load directly support ad landing; plan does not name Thanksgiving — add one line in v1.3 |

**CoS scoring breakdown:** Founder image / no-hotlink / inventory / PII (30) = 29; Standing locks & plan-only (20) = 20; Fixes 2–6 preserved + tests (25) = 23 (−2 Fix 3 signed-in still uses unregistered `/?route=AiChatScreen`); CSV hygiene vs Argon (15) = 14 (−1 CSV-1..4 accepted as pre-execute); Launch fit / review chain (10) = 10. **Total 96.**

---

## 2. PII Findings (CoS)

- **AJ / user PII in `MISSING_IMAGES.csv`:** **NONE found** this turn (3202/3202 `PASSED_GENERIC_ONLY`).
- Plan mentions `aj_photo` / `aj_currency` **only** inside the exclusion regex for the intake gate — not as leaked identifiers.
- **Residual hygiene (not confirmed PII, must scrub before ingest):** Argon CSV-1 — 81 `EXTERNAL_MIRROR_PENDING` rows with blank `candidate_source` (collection-seed / “owner removed” class in master JSONL) must be reclassed to Tier 1 / `MISSING`, never mirrored as public-domain; ~11–12 collector-album marketing titles still in `series`/`name`; `mint_mark='True'` on ~1965 rows; `estimated_cost` truncated to `.00`.

---

## 3. CoS Must-Fix / Carry-Forward (for AG before Eric YES)

CoS gate is PASS. **Eric YES remains blocked by SAG FAIL.** Fold these into v1.3 / amend:

1. **Bind catalog-first AI rule:** AI replicas only in labeled `ai_replica_images`; never `primary_image` / `type_image` / card art / browse index.
2. **Add rollback + preview-before-live** for all six fixes and any GCS ingest (prior object versions, firebase.json/catalog JSON revert, FT on preview channel before `numista-vault.web.app`).
3. **CSV hygiene before acquire-list use:** clear Argon CSV-1..CSV-4 (81 blank-source reclass; mint_mark; album scrub; `$0.00` cost column); drop “100% sourced” claims until cited match report.
4. **Hard $ monthly cap + billing alert** covering GCS + CDN egress under Meta ad traffic (beyond `$0` acquisition).
5. **Fix 3 signed-in path:** do not keep `launchUrl('/?route=AiChatScreen...')` — name a real registered route or defer signed-in chat; root cause already says that route is unregistered.
6. Carry Argon **EX-1..EX-4** (branch guard `dev` not `p7-v8.9`; explicit `connect-src` for `storage.googleapis.com` or same-origin rewrite; `replaceState`/`popstate` on deep-link close; `?redirect=` + Morgan avatar `errorBuilder`).

---

## 4. SAG Result (independent; grok-4.7; key never printed)

```
## SAG_SCORE: 75/100 FAIL
## MUST_FIX (ordered, blocking before Eric YES if any; else say NONE blocking)
1. Bind the catalog-first image rule in Fix 1 and Fix 6: AI replicas may live only in labeled `ai_replica_images`, never in `primary_image`, `type_image`, card art, or the browse index. The plan never names this field.
2. Add rollback and a preview-before-live gate for all six fixes and for any GCS ingest: prior asset versions, revert of `firebase.json` and catalog JSON, how to pull a bad object, and Field Tester on a preview channel before `numista-vault.web.app`. No live change during Thanksgiving ads without that path.
3. Do not treat `docs/MISSING_IMAGES.csv` as the acquire list until hygiene is fixed and cited: 81 `EXTERNAL_MIRROR_PENDING` rows with blank `candidate_source` (collection-seed misclass) must not be ingested as public-domain mirrors; scrub ~11–12 collector-album titles; fix `mint_mark='True'`; restore the cost column (shell ate `$`). Drop the “248 identified” and “100% sourced” claims until a cited match report exists, including the unsourced 4,804-archive figure.
4. Set a hard monthly dollar cap and billing alert that covers GCS plus egress under Meta ad traffic. `$0.00` acquisition and ~`$0.032`/month storage are not a cap. Tier 4 studio photography is `$0` only if already owned; otherwise it is out of this `$0` plan.
5. Rewrite Fix 3’s signed-in branch. Root cause says `/?route=AiChatScreen` is not registered; the planned `launchUrl` still uses that route. Name a real route or defer signed-in chat. Do not approve a spec that repeats the bug.
## NON_BLOCKING
- Deep link uses `pushState` on open and again on close, with no `popstate` handler. Back button can desync the modal. Close should use `history.back()`; test back as well as incognito paste.
- Plan timestamp 5 Nov 2026 12:20 PM ET cites a founder directive timed 5:55 PM ET the same day. Fix the citation chain.
- Catalog JSON `Cache-Control` of 1 day plus `stale-while-revalidate` needs versioned filenames so an ad-week update is not stuck on stale JSON.
- State in one line that an Eric YES on this plan is not a Firestore write or rules YES. The plan already says zero Firestore writes.
- Keep all 167 `candidate_source` URLs as internal acquisition notes only. Never render them as `src` or `href`.
- Signed-out Morgan copy (“analyze auction histories,” “evaluate strike”) is marketing, not a tested capability. Soften it.
## PII_FINDINGS
- This-turn CSV check: 3202 data rows, every `pii_gate_status=PASSED_GENERIC_ONLY`. No emails, phones, AJ tokens, owner names, street addresses, SSNs, or Eric/aunt-name hits in the summary.
- Plan text uses `aj_photo` / `aj_currency` only as exclusion regex, not as leaked identifiers. No user PII is quoted.
- Residual risk, not a clean bill: 81 blank-source rows flagged as collection-seed misclassified into external-mirror pending. Those must not enter public GCS. Personal-collection, receipt, and AJ images stay out under the stated gate.
- ~11–12 collector-album titles are unscrubbed. Not confirmed as names, and not cleared for public captions or card titles.
- `mint_mark='True'` and cost values truncated to `.00` are integrity bugs, not PII.
## 3_SENTENCE_PLAIN_ENGLISH (for founder Eric)
I am not ready for you to type YES. The plan correctly stays on paper, leaves the live site and Stripe locked, and keeps catalog photos on our own storage with no links out, but it never says AI pictures cannot be the main photo, and it has no undo plan if the catalog breaks while Thanksgiving ads send people there. The missing-image list still has messy rows that could mix in personal-collection material, and the signed-in Ask Morgan fix still points at a page that does not exist, so this needs a revision first.
## RATIONALE (brief)
Independent of Argon 96 and CoS 96. Locks, plan-only status, Stripe OFF, zero Firestore, no-hotlink/CSP stance, PII gate, tier math (2273+747+181+1=3202), and per-fix tests are real strengths and match the ad-landing priority only because nothing deploys. Score is 75 because two required controls are absent (AI replica never-primary; rollback), the standing CSV is not source-clean, the `$` cap ignores ad egress, and Fix 3 contradicts its own root cause. Those block Eric YES.
```

---

## 5. Three-Sentence Plain English (CoS, for Eric)

This is still only a written plan: it does not change the live site, keeps main locked and Stripe off, and says every catalog photo must live on our own Google storage with credits as plain text—no linking out to other sites. It lists all 3,202 catalog entries that still need pictures and a $0 public-domain / internal-archive way to fill them, plus five other catalog fixes (shareable URLs, Ask Morgan when signed out, era filter reset, Pre-Federal badge match, and faster first load). Argon and CoS both scored it 96, but the independent SAG review scored 75 and is blocking your YES until AG adds the AI-replica field rule, a real rollback path, CSV cleanup, an egress dollar cap, and a working signed-in Ask Morgan route.

---

## 6. Next Actions (no execute)

1. **AG CoS:** Amend to **v1.3** clearing SAG MUST_FIX 1–5 (+ Argon CSV/EX carry-forwards). Re-baton Argon → CoS → SAG.
2. **Desk:** Mirror this score into RADIO NET / OUTBOX; do **not** chase Eric for YES.
3. **Locks unchanged:** `origin/main @ 9f04550a`, Stripe OFF, zero deploys, zero Firestore writes/rules without separate YES.

**WHOSE_TURN:** AG (v1.3 amend) → Argon → GB CoS → SAG → Eric typed YES only after SAG ≥95.
