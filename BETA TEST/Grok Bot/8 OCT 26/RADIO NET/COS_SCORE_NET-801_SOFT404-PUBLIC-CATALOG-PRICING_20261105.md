# GB CoS SCORE — NET-801 / Soft-404 + Public Catalog Options + Pricing AuthGate

- **Scorer:** Grok Bot Chief of Staff (GB CoS scorer executor)
- **Date / Time:** 2026-11-05 ~2:20 PM ET (America/New_York)
- **Targets:** `PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING.md`, `ARGON_REVIEW_PLAN_SOFT404-PUBLIC-CATALOG-PRICING.md` (Argon 96)
- **Mode:** SCORE ONLY
- **CoS Score:** **95 / 100 (`PASS` ≥95)**
- **Argon:** 96
- **SAG Score (this turn, grok-4.7 via xAI API):** **68 / 100 (`FAIL`)**
- **Eric YES gate:** **BLOCKED** by SAG FAIL (68) and by missing typed Option A/B/C. CoS PASS alone does not authorize YES.

---

## 1. CoS Checklist

| Check | Result | Notes |
| :--- | :---: | :--- |
| Plan-only; main `@ 9f04550a`; Stripe OFF | PASS | Explicit |
| Firestore separate YES | PASS | Zero Firestore; public catalog = GCS/static only |
| No AJ / user PII | PASS | Public reference only |
| No hotlinked images | PASS | Relies on closed-CSP / NET-777/791 architecture |
| AI replicas not primary | PASS (by dependency) | Must stay bound via NET-803 when Option A ships |
| Public valuations = CDN **CPG retail** only; never wholesale / AI Value as primary | **GAP** | Plan does not bind Greysheet Option B / CDN CPG retail for any public catalog value display — **must-fix before Option A execute** |
| Tests / curl / Playwright | PASS | §6 machine-checkable |
| Rollback + preview | PARTIAL | Needs explicit preview-channel + firebase.json revert before live ad week |
| $ cap | PARTIAL | Routing itself ~$0; Option A traffic inherits NET-803 $25/$20 egress cap — cite it |
| Thanksgiving Meta ad #1 fit | PASS | Soft-404 titles, `/catalog` 404, Pricing AuthGate hijack are direct ad-landing bugs |

**Breakdown:** Soft-404 + AuthGate root cause (30)=29; Options A/B/C + Eric gate (25)=24; Pricing history fix (20)=20; UX polish items (10)=9; CPG-retail bind + count reconcile + Meta OG (15)=13. **Total 95.**

---

## 2. S404-3 Finding (homepage 5,142 vs 3,202)

**Verdict: REAL MISMATCH — not “just a different denominator.”**

| Figure | What it is | Source this turn |
| ---: | :--- | :--- |
| **5,142** | Homepage marketing badge “Reference Coins” | `login_screen.dart:338, 466` (cited by plan + Argon) |
| **3,202** | Current master catalog entry count | `entries_master_20261103.jsonl` = **3202** lines; types coin 2965 + note 181 + medal 56; `MISSING_IMAGES.csv` = **3202** rows (one per master entry, not a subset) |

So 3,202 is the **full verified catalog master**, not “how many are missing images.” The badge’s 5,142 does not match that master. Before Option A goes public (and before Meta ads point at `/catalog`), either:

- change the badge + meta titles to the verified count (e.g. **3,202**), or
- produce a cited inventory that actually contains 5,142 reference records and explain the extra ~1,940.

Do **not** tell visitors the catalog has 5,142 items if `/catalog` lists 3,202.

---

## 3. Options A / B / C (plain English) + CoS recommendation

| Option | Plain English | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **A — Public `/catalog` (recommended)** | Anyone can browse the reference catalog at a real URL without signing in; “Add to My Collection” asks them to sign up. | Matches the homepage promise; fixes `/catalog` 404; gives Meta ads a real landing page; SEO. | Must reconcile 5,142 vs 3,202; must bind CPG retail if any values show; needs preview + OG tags for Meta crawler. |
| **B — Search modal on the login page** | A “Explore 5,142 Reference Coins” button opens a search popup on the homepage; no new public URL. | Faster to build; still lets visitors poke coverage. | No indexable `/catalog` URLs; weaker for Meta ads; still must fix the fake/mismatched count in the button label. |
| **C — Keep catalog gated; fix the wording** | Leave catalog behind sign-in; rename the demo so it does not over-promise. | Smallest change. | Does not fix `/catalog` 404 or give ads a catalog landing page; weakest for Thanksgiving launch. |

**CoS recommendation: Option A**, same as the plan — but only after (1) the count on the homepage matches the live catalog, (2) any public value display is **CDN CPG retail only** (no wholesale, AI Value not primary), and (3) Meta link-preview HTML titles (Argon S404-2) are in the execute checklist. Soft-404 + Pricing AuthGate fixes should ship either way.

---

## 4. CoS Must-Fix before Eric YES on Option A (and strongly before ad week)

1. **Reconcile S404-3** count (5,142 vs 3,202) with a cited source.
2. **Bind public valuations:** CDN CPG retail only; never wholesale; AI Value never primary on public surfaces (Eric Greysheet Option B).
3. **S404-2:** Static/OG titles for Meta `facebookexternalhit` (JS `document.title` alone is not enough for ad previews).
4. **S404-1:** Merge carefully with `dev` `CatalogBrowseScreen` deep links (`/catalog/:nacCode`).
5. Name **preview-channel + firebase.json rollback** and cite **NET-803 $25/$20** for Option A traffic.

Soft-404 + AuthGate + footer `history.pushState` portions are otherwise strong.

---

## 5. Two-Sentence Plain English (for Eric)

This plan fixes three launch bugs: public pages that all look like the same “Numista.AI” tab to Google, the Pricing page kicking signed-in users back to the home dashboard, and footer links that do not update the browser address. It also asks you to pick how public the reference catalog should be — full public `/catalog` (recommended for Thanksgiving ads), a homepage search popup, or keep it gated and just fix the wording — and it flags that the homepage still says 5,142 reference coins while the verified catalog master is 3,202.

---

## 6. SAG Result (independent; grok-4.7; key never printed)

```
# SAG SCORE NET-801 (xAI API, grok-4.7, 2026-11-05 ET)

## SAG_SCORE: 68/100 FAIL
## MUST_FIX (blocking before Eric YES; or NONE blocking)
1. Do not lock **5,142** into titles, meta, badges, or Option A. Homepage 5,142 ≠ entries_master **3202** (coin 2965 + note 181 + medal 56). MISSING_IMAGES=3202 (= full master). Real mismatch. Nothing invented. Reconcile the public number before any catalog or ad copy.
2. Thanksgiving Meta ads are #1. JS `document.title` / `pushState` does not feed non-JS scrapers. Plan must require static `<title>` plus `og:title` / `og:description` (S404-2) and prove them on a **preview** HTML body, not `curl -I` of live.
3. Public values are unbound. If any value is shown: **CDN CPG retail only**. Never wholesale, never Greysheet wholesale, never AI-primary. Plan does not bind this.
4. Image rule unbound. `ai_replica_images` never primary. No hotlinks. MISSING_IMAGES covers the full master, so “high-resolution imagery” must not ship as fact. Missing stays placeholder.
5. Eric must **type A, B, or C**. CoS “recommend A” is not a decision. Option C must not skip that typed choice.
6. Standing controls missing: hard **$cap**, **rollback**, **preview-before-live**. Section 6 probes production `numista-vault.web.app`. Do not treat that as the gate.
7. Defect D is not fixed. §4.4 still uses `InkWell` and does not add real `<a href>`, so middle-click / new-tab still fails.
8. Drop unsourced **99.4%** and the claim of **5,000+ indexable pages**. SPA rewrite to `index.html` does not create those pages.
## NON_BLOCKING
- Routing and AuthGate diagnosis match the cited `firebase.json`, `main.dart`, `auth_gate.dart`, and `login_screen.dart` lines. Plan-only, `main` @ `9f04550a`, Stripe OFF, zero Firestore writes: stated and held.
- S404-1: on integrate, keep `dev` `/catalog` and `/catalog/:nacCode` → `CatalogBrowseScreen`. Do not clobber that from `p7-v8.9`.
- `gs://numista-reference-library` is asserted, not evidenced in the audited files. Do not treat the bucket as verified.
- `FirebaseAuth.instance.currentUser` inside `build` will not track auth changes; use the existing auth stream when this is executed.
- PIN/password labels, jargon, and footer semantics are fine once unsourced stats are removed.
## PII_FINDINGS
Plan text: no collector PII, no AJ, no emails, no account data. Argon review embeds a local path with Windows username `ericd` plus a reviewer UUID. Do not republish that path. No AJ token in either file.
## 2_SENTENCE_PLAIN_ENGLISH (for Eric)
The plan correctly finds the broken Pricing path and the missing /catalog route, but it is not ready for your YES. It still sells 5,142 coins when the master list is 3,202, and it does not lock Meta ad titles, retail-only public prices, image rules, a spending cap, rollback, or a preview before anything goes live — you must type A, B, or C yourself.
## RATIONALE (brief)
Argon 96/100 demoted launch blockers to notes. SAG does not. Soft-404 and AuthGate root cause are real; the executable package is not. It hardcodes a false count, misses static OG titles required for 26 Nov Meta, leaves public values and images unbound (CDN CPG retail only; `ai_replica_images` never primary; no hotlinks), and omits $cap, rollback, and preview-before-live. Option A is a recommendation, not authorization. PASS bar is 95. This is FAIL until those locks are in the plan and you type A, B, or C.
```


## 7. Next Actions

AG amend on SAG must-fixes → re-SAG → Eric types Option **A / B / C** (and YES) only after SAG ≥95. No deploy. Locks unchanged.
