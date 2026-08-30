# Pitch Deck Hardening — Implementation Plan

Update the pitch deck across all three deliverables (HTML, Markdown, Dart) to address 6 factual fixes and 4 new slides/sections based on founder interview.

---

## Proposed Changes

### Factual Fixes (All Three Files)

#### Fix 1: Coin Example → 1893-S Morgan Dollar
- **Slide 5 (Estate Solver):** Replace `"1921 High Relief Peace Dollar"` with `"1893-S Morgan Dollar"` — the undisputed king of the Morgan series (\$5,000–\$200,000+)
- Files: `pitch_deck.html` (line 937), `pitch_deck_screen.dart` (not currently referenced, no change needed)

#### Fix 2: Soften Accuracy Claim
- **Slide 7 (GCP Architecture Explorer):** Change `"Accuracy: 98.4%"` to `"Accuracy: >95% (internal beta)"` in both the static HTML and the JS `gcpNodes.vertex` object
- Files: `pitch_deck.html` (lines 1074 and 1579)

#### Fix 3: Remove Specific Image Dataset Number
- **Slide 11 (GCP Ask):** Change `"proprietary 500,000+ high-resolution numismatic image datasets"` to `"a curated high-resolution numismatic image corpus sourced from collector submissions and public-domain archives"`
- Files: `pitch_deck.html` (line 1300), `NUMISTA_AI_GOOGLE_STARTUP_PITCH_DECK.md` (line 182), `pitch_deck_screen.dart` (line 750)

#### Fix 4: Gemini 3.5 → Gemini 3.7 Flash (Everywhere)
- Globally replace all references to "Gemini 3.5" with **"Gemini 3.7 Flash"** across all three files
- This matches the actual production model (`gemini-3.5-flash` is being upgraded to `gemini-3.7-flash` per release notes)
- Approximately 20+ occurrences across the three files

---

### New Content — Restructure to 14 Slides

The current deck is 12 slides. We'll add 2 new slides and rearrange for stronger flow:

#### [NEW] Slide 10.5 → New Slide 11: "The Founder & Team"

Content sourced from the live app's [our_team_screen.dart](file:///C:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/our_team_screen.dart):

**Eric Seaman — Founder & Lead Developer**
- 🎖️ **US Army (Retired)** — 26 years of service, primary focus: property accountability for millions of dollars in mission-critical assets
- 🎓 **Google Veterans Launchpad Alumni** — Completed Google's veteran entrepreneur training program
- 🧠 **Certified Google Cloud Generative AI Leader**
- 💡 **Origin Story:** Built Numista.AI at a family member's kitchen table while helping them organize a 50+ year coin collection — realized the same discipline from military inventory management could be powered by AI

**Morgan — AI Numismatic Guide** (brief mention with avatar, already covered on Slide 4)

> [!IMPORTANT]
> This slide positions you as exactly the kind of founder Google Cloud for Startups loves: a non-traditional builder with deep domain expertise, trained through Google's own programs, who built a real product.

---

#### [NEW] Slide 10.75 → New Slide 12: "Why Not _____? — Competitive Landscape"

| Alternative | What It Does | What It Lacks |
|---|---|---|
| **Spreadsheets (Excel/Sheets)** | Basic manual tracking | No AI identification, no live pricing, no wish lists, no coin history, no estate planning, no Greysheet/CDN integration |
| **PCGS CoinFacts / Set Registry** | Lookup tool & registry | No personal inventory management, no valuation engine, no estate division, no Morgan AI |
| **CoinManage (Desktop)** | Legacy Windows software | No cloud sync, no AI, no mobile, no Document AI, not maintained |
| **Heritage/GreatCollections** | Auction platforms | Sell-side only; no cataloging, no estate planning, no daily valuation |
| **Pen, Paper & Memory** | The true incumbent for seniors | Lost when the collector passes — the entire problem this solves |

**Differentiator callout:**
> *"No existing tool combines AI-powered visual identification, real-time Greysheet/CDN wholesale pricing, senior-accessible ingestion, AND legally defensible estate division in a single platform. Numista.AI is the first."*

---

#### [MODIFY] Slide 11 → New Slide 13: Reframe "The Ask"

Currently says "How We Will Deploy Google Cloud Startup Credits" but never names a number or context.

**Reframe:**
> *"We are currently in the Google Cloud for Startups program at the \$2,000 credit tier. We're applying for expanded support to accelerate our three highest-impact workloads..."*

Add a candid "What expanded support means for Numista.AI" box:
- **Technical:** Fund Vertex AI fine-tuning and BigQuery ML at scale
- **Strategic:** Google's endorsement accelerates fundraising conversations with investors — enabling the founder to hire dedicated engineering talent and shift focus to marketing and vertical expansion (stamps, art, baseball cards, sneakers)

> [!NOTE]
> This is unusually honest for a pitch deck, and that's the point. Google's program reviewers have seen 10,000 pitches from "AI-powered" startups. A retired Army supply sergeant who taught himself to code via Google's own programs, built a live product, and is asking for resources to grow? That story stands out.

---

#### [MODIFY] Slide 12 → New Slide 14: Add Milestones Timeline to CTA

Replace the current generic CTA with a milestone-anchored closing. Add a timeline strip above the action cards:

| Milestone | Target |
|---|---|
| ✅ MVP Live on GCP | **Completed** |
| ✅ 7 Ingestion Pipelines Operational | **Completed** |
| ✅ Morgan AI v1 Live | **Completed** |
| ✅ Attorney Portal + Passport Generator | **Completed** |
| 🎯 First 100 Beta Collectors | Q4 2026 |
| 🎯 B2B Estate Attorney Pilot (3 firms) | Q1 2027 |
| 🎯 Vertical Expansion: Stamps & Baseball Cards | Q2 2027 |
| 🎯 Seed Fundraise & First Engineering Hire | Q3 2027 |

---

### Slide Renumbering (12 → 14 slides)

| # | Current | New |
|---|---|---|
| 1–10 | Unchanged | Unchanged |
| — | — | **11 (NEW): The Founder & Team** |
| — | — | **12 (NEW): Competitive Landscape** |
| 11 | The GCP Ask | **13: The Google Cloud Partnership (reframed)** |
| 12 | Vision & CTA | **14: Vision, Milestones & CTA** |

Update `totalSlides` from 12 → 14 in the HTML JS, the Dart state, and the MD outline.

---

## Files Modified

#### [MODIFY] [pitch_deck.html](file:///C:/Users/ericd/Documents/MyVertexProject/Pitch%20Deck/pitch_deck.html)
- Fix coin example, accuracy claim, image dataset number
- Global Gemini 3.5 → 3.7 Flash
- Add 2 new slides (Team, Competitive Landscape)
- Reframe GCP Ask slide
- Add milestones timeline to CTA slide
- Update totalSlides counter

#### [MODIFY] [NUMISTA_AI_GOOGLE_STARTUP_PITCH_DECK.md](file:///C:/Users/ericd/Documents/MyVertexProject/Pitch%20Deck/NUMISTA_AI_GOOGLE_STARTUP_PITCH_DECK.md)
- All the same factual fixes
- Add Slide 11 & 12 written scripts
- Update Slide 13 ask framing
- Add milestones to Slide 14

#### [MODIFY] [pitch_deck_screen.dart](file:///C:/Users/ericd/Documents/MyVertexProject/Pitch%20Deck/pitch_deck_screen.dart)
- Gemini 3.7 Flash everywhere
- Fix image dataset text
- Add `_buildTeamSlide()` and `_buildCompetitiveLandscapeSlide()`
- Update totalSlides from 12 → 14

---

## Verification Plan

### Automated Tests
- `git status` — confirm only Pitch Deck files modified
- Open `pitch_deck.html` in browser and navigate all 14 slides to confirm no broken layout

### Manual Verification
- Keyword search: confirm zero remaining instances of "Gemini 3.5" (should all be "3.7 Flash")
- Keyword search: confirm zero remaining instances of "98.4%" or "500,000+"
- Confirm `totalSlides = 14` in both HTML JS and Dart state

## Open Questions

> [!IMPORTANT]
> **Milestone dates:** The dates I used (Q4 2026, Q1 2027, etc.) are placeholders. Are these roughly right, or do you want to adjust them?

> [!IMPORTANT]
> **Vertical expansion mention:** You mentioned stamps, art, baseball cards, and sneakers. Should I include ALL of those on the roadmap, or keep it tighter (e.g., just "stamps & sports cards")?

> [!IMPORTANT]
> **Profile photo:** Your live site uses a placeholder (`placehold.co/400x400?text=ES`). Do you have a real headshot you want used on the Team slide, or should I keep the stylized initials placeholder?
