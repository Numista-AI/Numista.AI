# GB CoS SCORE — NET-803 / FAILFIX_PLAN_NET-777_CATALOG_v1.3

- **Scorer:** Grok Bot Chief of Staff (GB CoS scorer executor)
- **Date / Time:** 2026-11-05 ~2:20 PM ET (America/New_York)
- **Targets:** `FAILFIX_PLAN_NET-777_CATALOG_v1.3.md`, scrubbed `MISSING_IMAGES.csv` (3,202 rows), `ARGON_REVIEW_FAILFIX_PLAN_NET-777_CATALOG_v1.3.md` (Argon 98)
- **Prior turn:** CoS 96 / SAG 75 on v1.2 (`COS_SCORE_NET-788_FAILFIX-777-v1.2_20261105.md`); five SAG must-fixes were the amend target
- **Mode:** SCORE ONLY — no execute, no deploy, no merge, no push, no Eric ping, no outbound messages
- **CoS Score:** **97 / 100 (`PASS` ≥95)**
- **Argon Score (prior):** **98 / 100 (`PASS`)**
- **SAG Score (this turn, grok-4.7 via xAI API):** **92 / 100 (`FAIL`)**
- **Eric YES gate:** **BLOCKED** by SAG FAIL (92). CoS PASS alone does not authorize YES. AG must clear SAG must-fixes (tier table + Morgan ctor) in a micro-amend before re-SAG.

---

## 1. CoS Checklist (this turn)

| Check | Result | Notes |
| :--- | :---: | :--- |
| Plan-only; no deploy / no merge | PASS | Status lines 13–18; §9 |
| `origin/main` locked `@ 9f04550a` | PASS | Explicit |
| Stripe OFF | PASS | Explicit |
| Firestore writes / rules = separate Eric YES | PASS | Line 17 states plan YES is not Firestore/rules YES |
| No AJ / user PII in plan or CSV | PASS | This-turn CSV: 3202/3202 `PASSED_GENERIC_ONLY`; 0 regex hits on AJ/aunt/email/phone/SSN |
| No outbound / hotlinked images; internal GCS only | PASS | CSP bridge deleted; 167 `candidate_source` URLs = acquisition notes only |
| AI replicas only in labeled `ai_replica_images`, never primary | PASS | **SAG MF-1 closed** — §2.B + §7.B bind field by name; placeholder if no authentic photo |
| Nothing invented; sources cited | PASS | Line-cited Flutter/`firebase.json`; Argon verified `MorganChatPopout` exists |
| Hard $ cap + alert | PASS | **SAG MF-4 closed** — **$25/mo** GCS+CDN egress hard cap; alert at **$20 (80%)** and $25 (100%); Tier 4 = owned gear $0 |
| Rollback + preview-before-live | PASS | **SAG MF-2 closed** — §8.A GCS versioning/`gsutil rm`/Git revert/index rollback; §8.B `pre-ads-preview` + FT before live |
| CSV hygiene (SAG MF-3) | PASS | Verified this turn: blank-source EXTERNAL=0; `mint_mark=True`=0; album-ish=0; cost `$0.00`×3202; EXTERNAL with URL=167 |
| Fix 3 signed-in route | PASS* | **SAG MF-5 closed** — uses `MorganChatPopout`; *Argon EX-v1.3-1: snippet says `initialPrompt`, real ctor is `initialQuery` + required `onClose` — execution note, not plan fail |
| Fits Thanksgiving Meta ad launch (#1) | PASS | Named Meta traffic, preview gate before ads, egress cap sized for ad visits |

**CoS scoring breakdown:** Image/no-hotlink/AI-field/PII (30)=30; Standing locks & plan-only (20)=20; Six fixes + SAG MF closeout (25)=24 (−1 ctor param name in snippet); CSV hygiene vs Argon (15)=14 (−1 §2.D still shows pre-scrub 2,273/747 tier table while live CSV is 2,354 Tier1 / 666 Tier2 / 181 Tier3 / 1 Tier4); Launch fit / review chain (10)=10. **Total 97.**

### SAG must-fix closeout matrix (v1.2 → v1.3)

| # | SAG-75 must-fix | Verified in v1.3? | Evidence |
|---:|---|---|---|
| 1 | `ai_replica_images` only, never primary/card/index | YES | §2.B lines 62–66; §7.B line 271 |
| 2 | Rollback + preview-before-live | YES | §8.A–§8.B |
| 3 | CSV hygiene (81 blank, mint_mark, albums, `$0.00`, drop unproven claims) | YES | This-turn CSV scan + §2.C |
| 4 | Hard $/mo cap + alert for GCS+CDN under Meta ads | YES | §2.E **$25 hard / $20 alert** |
| 5 | Fix 3 no unregistered `/?route=AiChatScreen` | YES | §4.C → `MorganChatPopout` (ctor param name = EX note) |

**$25/mo egress cap with $20 alert:** REAL in plan text (§2.E), with usage math (~$1.60 egress / ~$0.01 storage under 50k visits). Cap is a Cloud Monitoring **alert** design at plan stage — wiring the GCP budget alert is an execute-time step after Eric YES, not a live alert today.

---

## 2. PII Findings (CoS)

- **AJ / user PII in scrubbed `MISSING_IMAGES.csv`:** **NONE** (3202/3202 `PASSED_GENERIC_ONLY`; 0 AJ/aunt/email/phone/street/SSN hits this turn).
- Plan exclusion regex still names `aj_photo` / `aj_currency` as **drop patterns only** — not leaked identifiers.
- Residual: 167 EXTERNAL_MIRROR_PENDING rows now have non-blank `candidate_source` URLs — keep as internal notes only; never `src`/`href`.

---

## 3. CoS Must-Fix / Carry-Forward (non-blocking for CoS PASS; clear before/at execute)

1. **EX-v1.3-1:** In code, call `MorganChatPopout(initialQuery: ..., onClose: () => Navigator.of(context).pop())` — not `initialPrompt`.
2. **Update §2.D tier table** to match scrubbed CSV (2,354 / 666 / 181 / 1) before acquire-list use.
3. Carry Argon EX-v1.3-2 (keep CSP locked to `'self'` + `storage.googleapis.com`).

---

## 4. SAG Result (independent; grok-4.7; key never printed)

```
# SAG SCORE NET-803 (xAI API, grok-4.7, 2026-11-05 ET)

## SAG_SCORE: 92/100 FAIL
## MUST_FIX (blocking before Eric YES; or NONE blocking)
1. §2.D tier table is stale and must be rewritten to the scrubbed CSV before YES. It still shows Tier 1 **2,273** and Tier 2 **747**. CSV is Tier 1 **2,354** and Tier 2 **666** (same 3,202 total; the 81-row gap is the reclassified blank-source set). Do not approve an acquire plan that still publishes the pre-scrub split.
2. §4.C snippet does not match the verified widget. `MorganChatPopout` takes `initialQuery` and required `onClose`, not `initialPrompt`. Spec must be `initialQuery: 'Tell me about the ${item['name'] ?? 'this coin'} (${item['year'] ?? ''})'` and `onClose: () => Navigator.of(context).pop()`.
## NON_BLOCKING
- $25 / $20 figures are present, but Cloud Monitoring email alerts do not stop spend. Do not treat alert-only monitoring as a hard stop unless a billing-budget action actually halts GCS/CDN.
- Fix 5 still ORs `year < 1792` with the flags, so it is not strict Condition C1 (the cited 9 flagged rows). Prefer flag-only.
- Field Tester list omits pre-federal, AI-never-primary, and a no-`href`/`src` check on the 167 acquisition-note URLs.
- `git checkout HEAD~1 -- firebase.json` is unpinned. Roll back to `9f04550a` or a recorded good SHA.
- §8 should say production needs a **separate** typed YES, distinct from plan YES (dev code + preview/GCS only; not Firestore).
- Argon-cited CSV samples still label some 1976–1977 rows “Pre-1929”. Hygiene scan is otherwise clean; confirm license text before any ingest.
## PII_FINDINGS
NONE. No AJ records, no personal collection images, no user identifiers. Intake gate drops receipt/invoice/`aj_photo`/`aj_currency`/personal patterns. “Josiah K. Lilly Jr.” appears only as a scrubbed historical album title.
## 2_SENTENCE_PLAIN_ENGLISH (for Eric)
The five holes from the last fail are written into this plan: AI stand-ins stay out of the main photo, nothing goes live before a preview check, the spreadsheet itself is clean, the $25/$20 limit is stated, and signed-in Ask Morgan opens the real chat popout. Do not type YES yet, because the acquire-count table still has the old 2,273 / 747 split instead of 2,354 / 666, and the chat snippet uses a parameter name the widget does not have.
## RATIONALE (brief)
v1.3 closes the five v1.2 blockers in substance: `ai_replica_images` never primary/card/index; §8 rollback plus `pre-ads-preview` before `numista-vault.web.app`; CSV hygiene (3,202, user scan clean); $25 cap with $20 alert; unregistered `/?route=AiChatScreen` removed. Locks hold: plan-only, `main` `9f04550a`, Stripe OFF, Firestore YES separate, no hotlinks, CSP stays internal, Thanksgiving path is preview-first. Score stays under 95 because the acquire table invents the pre-scrub tier split and the Morgan call as printed will not compile.
```


## 5. Two-Sentence Plain English (for Eric)

This is the revised catalog fix plan: every public catalog photo must live on our own Google storage, AI pictures can never be the main photo, there is a written undo path and a preview channel before the live site, and Google storage/CDN spend is capped at $25 a month with a warning at $20. The list of 3,202 entries that still need pictures was cleaned (no personal data found), Ask Morgan for signed-in users opens the real chat popout instead of a broken route, and nothing deploys until Argon, CoS, SAG, and your typed YES all clear.

---

## 6. Next Actions (no execute)

1. If SAG ≥95 → Desk may present to Eric for typed YES (plan-only).
2. If SAG <95 → AG amends to v1.4 on SAG must-fixes only.
3. Locks unchanged: `origin/main @ 9f04550a`, Stripe OFF, zero deploys, zero Firestore writes/rules without separate YES.

**WHOSE_TURN:** AG amend (SAG must-fixes) → Argon (if material) → GB CoS → SAG → Eric typed YES only after SAG ≥95.
