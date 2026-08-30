# Pitch Deck Hardening — Implementation Plan v2

**Status: NOT EXECUTION-READY.** All 3 conflicts resolved. Awaiting Eric's decision after next Gemini + Grok pass.

---

## §1 — Decision Matrix

| # | Source | Suggestion | Verdict | Why |
|---|---|---|---|---|
| G1 | Gemini v1 | Replace "1921 High Relief Peace Dollar" with 1893-S Morgan Dollar | **ADOPTED** | Eric confirmed. Factually correct, ties to Morgan brand. |
| G2 | Gemini v1 | Soften "Accuracy: 98.4%" to ">95% (internal beta)" | **MODIFIED** → per Grok MF-4 | ">95%" is still an invented number. New text: "held-out eval in progress." See §3 Fix 2. |
| G3 | Gemini v1 | Remove "500,000+" image count, replace with "curated corpus from collector submissions and public-domain archives" | **MODIFIED** → per Grok MF-4 | Drop the number entirely, but also drop "proprietary" since PD coin images can't be owned. New text references only public-domain sources. See §3 Fix 3. |
| G4 | Gemini v1 | Global replace "Gemini 3.5" → "Gemini 3.7 Flash" | **MODIFIED** → per Grok MF-2 | Blind global replace repeats the error. Production code is mixed: Cloud Functions = `gemini-3.7-flash`, Dart client = `gemini-3.5-flash`. **See CONFLICT §2-A.** |
| G5 | Gemini v1 | Add Founder & Team slide | **ADOPTED** | Both Gemini and Grok agree. Eric confirmed "all of the above" layered credentials. |
| G6 | Gemini v1 | Add Competitive Landscape slide | **ADOPTED** | Both agree. Eric confirmed no direct AI competitor. Strip legal adjectives from differentiator sentence per Grok. |
| G7 | Gemini v1 | Reframe "The Ask" with $2K tier and expansion narrative | **MODIFIED** → per Grok MF-3 | Keep the honest framing, but the Ask cannot request fine-tuning on a model where tuning is not confirmed supported. **See CONFLICT §2-B.** |
| G8 | Gemini v1 | Add milestones timeline to CTA | **MODIFIED** → per Grok Agree/Accept | Keep milestone strip as a device, but only mark "Completed" what a reviewer can click on `numista-vault.web.app` today. See §3 Fix 8. |
| G9 | Gemini v1 | Add vertical expansion (stamps, art, baseball cards, sneakers) to roadmap | **MODIFIED** → per Grok Push-back | Drop sneakers and art from the Ask. Keep stamps and sports cards only. Numismatic SoR story is diluted by lifestyle collectibles. |
| X1 | Grok MF-1 | Build a claim register; ban "court-admissible," "irrevocable," "legally defensible," "100% fair-share" until attorney sign-off and SoR write-path is live | **ADOPTED** | Grok is right. These are legal-grade claims ahead of the actual write-path. See §4 Claim Register. |
| X2 | Grok MF-2 | Cite the actual deployed model ID from production, not marketing shorthand | **ADOPTED** in principle | **See CONFLICT §2-A.** Need Eric to confirm which model the deck should name. |
| X3 | Grok MF-3 | Kill the fine-tune Ask or change the SKU | **ADOPTED** in principle | **See CONFLICT §2-B.** |
| X4 | Grok MF-4 | Corpus and accuracy language still too hot — no invented numbers | **ADOPTED** | See §3 Fix 2, Fix 3. |
| X5 | Grok MF-5 | Delivery scope incomplete — v1 misses README, embedded JS strings, asset paths | **ADOPTED** | v2 includes grep verification appendix. See §6. |
| X6 | Grok Push-back | PCGS is not "instant cert validation" — describe at actual maturity | **ADOPTED** | See §3 Fix 6. |
| X7 | Grok Push-back | Morgan simulator is scripted — label it a sandbox | **ADOPTED** | See §3 Fix 7. |
| X8 | Grok Edge | "pre-seeded demo," not "100+ production collections" | **ADOPTED** | See §3 Fix 9. |
| X9 | Grok Edge | Keep "Numista.AI" with .AI every time on title slides | **ADOPTED** | Prevents confusion with Numista.com. |
| X10 | Grok Edge | Broken assets — `Logo Avatar/logo_owl.png` will 404 from attached folder layout | **NOTED** | Path is correct relative to `pitch_deck.html` in the same parent directory. Works in browser when opened from `Pitch Deck/`. Not broken. But README should document this. |

---

## §2 — Conflicts (ALL RESOLVED)

### ✅ RESOLVED §2-A — Model Name: Gemini 3.7 Flash

**Decision:** Use **"Gemini 3.7 Flash"** everywhere in the deck.

**Rationale:** Production Cloud Functions (`feedbackIntelligence.js`, `mappingController.js`, `integration_service.js`) already run `gemini-3.7-flash`. Remaining `gemini-3.5-flash` references in Dart client code will be upgraded separately by another agent. Deck is forward-accurate.

All 20 occurrences of "Gemini 3.5" across HTML (9), MD (5), Dart (5), README (1) will be replaced with "Gemini 3.7 Flash". This includes the easily-missed L1508 JS thinking animation string.

---

### ✅ RESOLVED §2-B — Fine-Tune Ask Replaced with Three-Pillar Credit Deployment

**Decision:** Rewrite the Ask around eval sets + Document AI + BigQuery ML. No fine-tuning claim. Fine-tuning referenced only conditionally.

**The three pillars for the Ask slide:**

1. **Curated Numismatic Eval & Benchmarking Sets (Vertex AI Gen AI Eval):**
   > "Build curated numismatic eval sets from public-domain archives and collector submissions to systematically benchmark Gemini multimodal accuracy on die variety, crack, and mint error classification tasks."

2. **Custom Document AI Processors:**
   > "Train and deploy custom Document AI parsing models for specialized dealer invoices, auction catalogs, and estate inventories."

3. **BigQuery ML & Vector Search:**
   > "Deploy credits toward BigQuery ML predictive pricing models (Greysheet/CDN wholesale valuation trends) and Vertex AI Vector Search / embeddings for visual coin matching."

**Conditional fine-tune note (roadmap only, not the Ask):**
> "Evaluate supervised fine-tuning on tuning-eligible Gemini models as multimodal tuning endpoints become generally available for domain adapters."

---

### ✅ RESOLVED §2-C — Attorney Portal: LIVE ✅

**Decision:** Attorney portal is **live and deployed** on both `numista-vault.web.app` and `numista.ai`. Milestone gets ✅.

**Verification evidence:**
- `main.dart` L66-86: Deep-link route guard detects `/attorney` or `?uid=...&token=...`, skips auth, mounts `AttorneyPortalScreen`
- `firebase.json` L40-43: Hosting rewrites route all paths to `/index.html` for Flutter Web client-side routing
- `firestore.rules` L24-28: Public single-document `get` access on `/users/{email}/estate_reports/{reportId}` without login
- `estate_report_service.dart` L74-76: Link generated as `https://numista.ai/attorney?uid=...&token=...` (canonical domain)
- Both `numista.ai` and `numista-vault.web.app` serve the same Flutter Web build

**Observed production behavior (Grok tested 27 AUG 2026, Eric confirmed error):**
- Bare `https://numista.ai/attorney` → Sign In / Create Account (not an attorney-specific state)
- `https://numista.ai/attorney?uid=demo&token=test` → Attorney Access chrome loads, then Firestore `permission-denied` error
- Valid uid + valid token → Read-only estate report renders correctly

**Deck milestone language:**
> `✅ Token-gated attorney report route — deployed (valid uid+token required)`

**Speaker note:** "The attorney portal requires a real uid and report token generated from the Estate Planning screen. We will provide a time-boxed demo token for the live review session."

**Eric note:** You confirmed an error when testing this 27 AUG — will address tomorrow. This does NOT block the deck plan; the route is deployed code. The milestone just needs honest framing.

---

## §3 — Fixes with Proof-Pairs

Every fix below shows the old text and the new text. If I cannot quote a new sentence, the item is not done.

### Fix 1: Coin Example (Slide 5)

**Old (HTML L937):**
> `Balances high-value "trophy" coins (e.g. 1921 High Relief Peace Dollar) against bullion lots to eliminate favoritism.`

**New:**
> `Balances high-value "trophy" coins (e.g. 1893-S Morgan Dollar) against bullion lots to eliminate favoritism.`

Files: `pitch_deck.html`

---

### Fix 2: Accuracy Claim (Slide 7)

**Old (HTML L1074, JS L1579):**
> `Latency: ~1.2s • Accuracy: 98.4%`

**New:**
> `Held-out eval in progress`

Files: `pitch_deck.html` (both the visible default text at L1074 AND the `gcpNodes.vertex.metric` JS string at L1579). The unsourced "Latency: ~1.2s" is also removed — no measured run to cite.

---

### Fix 3: Image Dataset (Slide 11/13)

**Old (HTML L1300):**
> `Fine-tune custom Gemini 3.5 Vision adapters on proprietary 500,000+ high-resolution numismatic image datasets for sub-millimeter die crack and mint error classification.`

**New:**
> `Build curated numismatic eval sets from public-domain archives and collector submissions to benchmark Gemini vision accuracy on die variety and mint error classification tasks.`

**Old (MD L182):**
> `Fine-tune Gemini 3.5 vision adapters on 500k+ numismatic image dataset for sub-millimeter die crack and mint error classification.`

**New:**
> `Build curated numismatic eval sets from public-domain sources to benchmark Gemini vision accuracy on die crack and mint error classification.`

**Old (Dart L750):**
> `'Fine-tune Gemini 3.5 vision adapters on 500k+ numismatic image dataset for sub-millimeter die crack classification.'`

**New:**
> `'Build curated numismatic eval sets from public-domain sources to benchmark Gemini vision accuracy on die crack classification.'`

---

### Fix 4: Gemini Model Name (Global — RESOLVED: Gemini 3.7 Flash)

**Old → New for all 20 occurrences:**
> `Gemini 3.5` → `Gemini 3.7 Flash`

Surface count for replacement:

| File | Occurrences | Locations |
|---|---|---|
| `pitch_deck.html` | 9 | L689, L831, L898, L1055, L1071, L1148, L1300, L1508, L1578 |
| `NUMISTA_AI_GOOGLE_STARTUP_PITCH_DECK.md` | 5 | L16, L44, L82, L126, L182 |
| `pitch_deck_screen.dart` | 5 | L313, L435, L649, L685, L750 |
| `README.md` | 1 | L25 |
| **Total** | **20** | |

L1508 (HTML): the Morgan "Thinking with Gemini 3.5..." animation string inside `sendPrompt()` JS function — easily missed in a naive search-and-replace. New text: `"Thinking with Gemini 3.7 Flash..."`

---

### Fix 5: Legal Language Softening (Multiple Slides)

**Old (HTML, various):**
> `court-admissible PDF Numismatic Passports` (Slide 3, L804)

> `court-ready Numismatic Passports (PDF) with irrevocable QR authentication codes` (Slide 3, L804)

> `Legally Defensible Estate Passports` (Slide 3, L802)

> `100% Algorithmic` (Slide 1, L695)

**New:**
> `comprehensive PDF Numismatic Reports` (Slide 3)

> `Numismatic Collection Reports (PDF) with timestamped QR verification codes` (Slide 3)

> `Comprehensive Estate Collection Reports` (Slide 3)

> `Algorithmic` (Slide 1 — drop "100%")

**Old (MD):**
> `Legally Defensible Estate Passports` (L75)

> `court-admissible PDF Numismatic Passports with QR-token verification` (L75)

> `100% Algorithmic Fair-Share Estate Division & Irrevocable Passports` (L45)

**New:**
> `Comprehensive Estate Collection Reports` (L75)

> `PDF Numismatic Collection Reports with timestamped QR verification` (L75)

> `Algorithmic Fair-Share Estate Division & Timestamped Collection Reports` (L45)

---

### Fix 6: PCGS Pipeline Maturity (Slide 3, Slide 6, Slide 10)

**Old (HTML L781):**
> `Instant PCGS certification scans`

**New:**
> `PCGS Public API cert lookups (browser-side, 1,000/day)`

**Old (Slide 10, L1250):**
> `Working pipelines for CSV, PCGS Cert, Document AI Invoices, Checklist OCR, USB Camera, and Manual.`

**New:**
> `Working pipelines for CSV, PCGS cert lookup, Document AI invoices, checklist OCR, USB microscope, and manual entry.`

---

### Fix 7: Morgan Simulator Label (Slide 4)

**Old (HTML L877):**
> `Try asking Morgan questions below to test the live simulator:`

**New:**
> `Try asking Morgan questions below in this scripted sandbox:`

**Old (HTML L898, badge):**
> `Gemini 3.5 Flash` (badge text — pending §2-A for model name)

**New badge text:**
> `Scripted Demo`

---

### Fix 8: Milestones — Only Mark Completed What Is Clickable Today (RESOLVED)

**Old (Gemini v1 plan):**
> `✅ Attorney Portal + Passport Generator — Completed`

> `✅ 7 Ingestion Pipelines Operational — Completed`

**New:**
> `✅ Production Web App Live — numista-vault.web.app`

> `✅ Morgan AI Chat — Live`

> `✅ Estate Fair-Division Solver — Live`

> `✅ Token-gated attorney report route — deployed (valid uid+token required)`

> `✅ Multi-Method Ingestion (CSV, Manual, USB Microscope, Checklist OCR, Document AI) — Live`

> `🎯 PCGS Cert Lookup (browser-side API) — Q4 2026`

> `🎯 First 100 Beta Collectors — Q4 2026`

> `🎯 B2B Estate Attorney Pilot (3 firms) — Q1 2027`

> `🎯 Vertical Expansion: Stamps & Sports Cards — Q2 2027`

> `🎯 Seed Fundraise & First Engineering Hire — Q3 2027`

Note: "7 Ingestion Pipelines" becomes "5 live + 1 in progress" (PCGS browser-side API pending).

---

### Fix 9: Demo Mode Language (Slide 10)

**Old (HTML L1255-1256):**
> `100+ Pre-Seeded Assets`

> `Instant guest & investor demo mode pre-populated across US Coins, Paper Currency, and World rarities.`

**New:**
> `Pre-Seeded Demo Collection`

> `Guest demo mode with representative US coins, paper currency, and world coins for instant evaluation.`

---

## §4 — Claim Register

Every marketing phrase tagged: **LIVE** (reviewer can verify today), **SPECIFIED** (in product plan, not shipped), **BANNED** (removed from deck until precondition met).

| Phrase | Current Slide | Status | Condition to Upgrade |
|---|---|---|---|
| "Court-admissible" | 3 | **BANNED** | Attorney review of output format + SoR write-path live |
| "Irrevocable QR passport" | 3 | **BANNED** | No revocation protocol defined; QR is a timestamp, not a seal |
| "Legally defensible" | 3 | **BANNED** | Attorney sign-off on admissibility |
| "100% Algorithmic Fair-Share" | 1 | **BANNED** | Drop "100%" — algorithm is real but "100%" implies legal guarantee |
| "7 Ingestion Pipelines Operational" | 1, 10 | **SPECIFIED** | PCGS pipeline blocked by Cloudflare; count is 5-6 live |
| "Attorney Portal — Completed" | 12/milestone | **LIVE (route only)** | Route deployed; valid uid+token renders report. Bare path = login. Invalid token = permission-denied. Milestone wording: "deployed (valid uid+token required)" |
| "Gemini 3.5" | All | **STALE → FIXED** | Replace all 20 occurrences with "Gemini 3.7 Flash". Add model-split speaker note in MD. |
| "98.4% Accuracy" | 7 | **BANNED** | No eval methodology exists |
| "500,000+ proprietary images" | 11 | **BANNED** | 57 images in GCS; PD images cannot be "proprietary" |
| "Instant PCGS cert validation" | 3, 6 | **BANNED** | Cloudflare blocks server-side; browser path untested |
| "Fine-tune Gemini vision adapters" | 11 | **BANNED** | 3.7 Flash tuning not confirmed supported |
| "Latency: ~1.2s" | 7 | **BANNED** | No measured run to cite |
| "littleton-v1" | 13/Ask | **BANNED** | Processor name not verifiable in GCP project |
| "100,000+ US & World Reference Types" | 10 | **SPECIFIED** | Live login shows 5,142 reference coins. Greysheet coverage is a different object. Needs linked evidence or reword. |
| "7,000+ items per user @ 60 FPS" | 10 | **SPECIFIED** | E2E tested but no linked report artifact. Link the test run or downgrade to SPECIFIED. |
| "$14.99-$29.99/mo B2C" | 9 | **LIVE** | Consistent across all files |
| "$199-$499/mo B2B" | 9 | **LIVE** | Consistent across all files |
| "LTV $680, CAC $65, 10.4x, 82%" | 9 | **SPECIFIED** | Projections, not actuals — already labeled "ESTIMATED" in HTML |
| "numista-vault.web.app" | 1, 10, 12 | **LIVE** | Verified |
| "Pre-seeded demo mode" | 10 | **LIVE** | After Fix 9 language change |
| "Morgan AI chat" | 4 | **LIVE** | Morgan is deployed on the live app |
| "Scripted sandbox" (deck simulator) | 4 | **LIVE** | After Fix 7 label change |

---

## §5 — New Slides (No New Architecture)

### NEW Slide 11: The Founder & Team
Content from `our_team_screen.dart`. No new claims. Directly mirrors the live app's "Our Team" page.

- **Eric Seaman** — Founder & Lead Developer
- US Army (Retired), 26 years — property accountability for mission-critical assets
- Google Veterans Launchpad Alumni
- Certified Google Cloud Generative AI Leader
- Origin: Built Numista.AI helping a family member organize a 50+ year coin collection
- **Morgan** — AI Numismatic Guide (brief card with avatar; details on Slide 4)
- Initials placeholder for headshot unless Eric provides one.

### NEW Slide 12: Competitive Landscape
No legal adjectives. No new claims. Table of alternatives and what they lack.

**Differentiator (cleaned of banned terms):**
> *"No existing tool combines AI-powered visual identification, real-time Greysheet/CDN wholesale pricing, senior-accessible ingestion, AND algorithmic estate division in one platform."*

### MODIFIED Slide 13: The Ask (pending §2-B)
Naming current $2K tier. Expansion narrative about hiring engineering talent and vertical growth. Credit deployment rewritten around whichever §2-B option Eric picks.

### MODIFIED Slide 14: Vision, Milestones & CTA
Milestone strip uses claim-register-verified statuses only. Dates per Fix 8.

---

## §6 — File Scope & Grep Verification Appendix

### Files Modified
1. `pitch_deck.html` — all fixes, 2 new slides, totalSlides 12→14, JS `gcpNodes` object, `sendPrompt()` thinking string, `morganResponses` object
2. `NUMISTA_AI_GOOGLE_STARTUP_PITCH_DECK.md` — all fixes, 2 new slide scripts, rewritten Ask
3. `pitch_deck_screen.dart` — all fixes, 2 new `_build*Slide()` methods, totalSlides 12→14
4. `README.md` — update slide count 12→14, update model name, note asset path requirements

### Post-Edit Grep Verification (Run Before Commit)
```powershell
# Zero results expected for each:
grep -rni "Gemini 3.5"        "Pitch Deck/"   # pending §2-A answer
grep -rni "98.4%"              "Pitch Deck/"
grep -rni "500,000"            "Pitch Deck/"
grep -rni "500k"               "Pitch Deck/"
grep -rni "court-admissible"   "Pitch Deck/"
grep -rni "irrevocable"        "Pitch Deck/"
grep -rni "legally defensible" "Pitch Deck/"
grep -rni "100% Algorithmic"   "Pitch Deck/"
grep -rni "instant PCGS"       "Pitch Deck/"

# Expected results:
grep -rni "totalSlides"        "Pitch Deck/"   # should show 14 in HTML + Dart
grep -rni "Slide 1 of"         "Pitch Deck/"   # should show "Slide 1 of 14"
```

---

## §7 — What This Plan Does NOT Do

Per your Rule 5, this plan does NOT:
- Add new architecture, YAML constraints, or extra features
- Touch `firestore.rules`, ITEM 6 backfill, hardware JWT, or any v4.1 product work
- Touch `ARCHITECTURE.md` — that doc still says `gemini-3.5-flash` / `gemini-3.5-pro`; updating it is a separate PR if Eric orders it
- Mark itself execution-ready — Eric decides after this Gemini + Grok pass

**Model-split speaker note (required in MD talking track per Grok v2 MF-D):**
> "Cloud Functions production services run `gemini-3.7-flash`. Flutter client-side calls are migrating from `gemini-3.5-flash` to `gemini-3.7-flash`. `ARCHITECTURE.md` in the repo still references 3.5; that doc update is a separate task."

---

## §8 — Honest Engineering Evaluation

### Where Grok Was Right and Gemini v1 Was Wrong

1. **Legal language.** Gemini v1 left "court-admissible," "irrevocable," "legally defensible," and "100% Algorithmic" untouched. Grok correctly flagged these as program risks, not copy issues. This was the biggest gap in v1.

2. **Fine-tune Ask.** Gemini v1 blindly upgraded the fine-tune language from "Gemini 3.5" to "Gemini 3.7 Flash" without checking whether tuning is supported. Grok caught this. The Ask would have asked Google Cloud for credits to do something their own model doesn't support — a credibility-killing mistake.

3. **Invented accuracy number.** Gemini v1 softened "98.4%" to ">95% (internal beta)" — still an invented number. Grok correctly pushed to eliminate invented metrics entirely.

4. **Scope undercount.** Gemini v1 listed line numbers for 3 files and missed the JS `gcpNodes` object, the `sendPrompt()` thinking string, and README.md entirely. That would have left stale strings after execution.

### Where Gemini v1 Was Right and Grok Didn't Add

1. **Coin example fix.** Gemini v1 spotted the "1921 High Relief Peace Dollar" error first and proposed 1893-S Morgan. Grok agreed.

2. **Founder slide.** Gemini v1 proposed the slide and structured the grill-me to get Eric's credential preferences. Grok agreed with the structure.

3. **Competitive landscape.** Gemini v1 built the table. Grok agreed with the device.

4. **Pricing consistency.** Gemini v1 verified all three files match. No corrections needed. Grok did not contest this.

### Where Both Were Wrong (Fixed in v2)

Neither v1 plan checked whether the attorney portal is actually accessible on the live site. Both assumed it without verification. v2 makes this an explicit question to Eric (§2-C).

---

### v2 → v2.1 Addendum: Where Grok v2 Caught Gemini v2

1. **Attorney portal over-described.** Gemini v2 wrote "bare `/attorney` shows expired/invalid state" based on reading code. Grok actually clicked production and found it shows Sign In. Grok was right — I described code intent, not observed behavior. Fixed.

2. **Unsourced latency.** Gemini v2 kept "Latency: ~1.2s" next to the eval phrase. Grok correctly flagged — no measured run exists. Removed.

3. **`littleton-v1` processor.** Gemini v2 introduced this name in the Ask as if it were a deployed Document AI processor. Grok searched the GitHub repo and found zero hits. Correct call — stripped.

4. **LIVE tag overuse.** Gemini v2 tagged "100,000+ Reference Types" and "7,000+ @ 60 FPS" as LIVE. Grok noted: live login shows 5,142 reference coins (not 100K), and the 60 FPS test has no linked artifact. Both downgraded to SPECIFIED.

5. **§7 contradicted §2.** Gemini v2 updated §2 to "RESOLVED" but left §7 saying "does NOT resolve the 3 conflicts." Copy error. Fixed.

### Where Grok v2 Was Accepted Without Objection

- Milestone strip: attorney portal reworded to match observed behavior
- Model-split speaker note added to §7
- PCGS stays out of the "Live" ingestion bullet (parked as Q4 target)
- `ARCHITECTURE.md` explicitly excluded from this PR's scope
