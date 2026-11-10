# Numista.Ai: Proposed Pricing and an All-Collectibles Revenue ESTIMATE
Prepared 10 Nov 2026 for Eric Seaman. Read-only research: nothing in Stripe, the app or the site was changed.

> **Everything in Part 2 is an ESTIMATE**, not a forecast or a promise. Sourced facts have a link. Anything I made up for the model is labeled **ASSUMPTION**. Anything I couldn't find is **UNKNOWN**.

---

## Summary

**Prices (draft, accepted by Eric for the Stripe test setup on 7 Nov 2026, not yet public):**

| Plan | Monthly | Yearly | Coin limit |
|---|---|---|---|
| Free | $0 | $0 | 10 coins (settled 1 Nov); one 8 Nov plan still says 20 (see conflicts) |
| Copper | $4.99 | $49.99 | 11–100 |
| Silver | $8.99 | $89.99 | 101–249 (8 Nov plan says 250) |
| Platinum | $10.99 | $109.00 | 250–500 |
| Gold | $15.99 | $150.00 | 501+ unlimited (8 Nov plan says 1,000) |
| Lifetime | ON HOLD | | $500 was recorded on 29 Oct, then put on hold. No $1,500 source exists |

Extras: $30 one-time **Beta Special** (6 months, 101+ coins); **Christmas 2026** 50% off the first yearly payment (26 Nov–25 Dec); **full export** at 6× the monthly price ($29.94 / $53.94 / $65.94 / $95.94), with **Free and Legacy export at $95.94**; **AI top-up** $5 per 1,000 items; **Legacy** cutoff 26 Nov 2026 00:00 ET. All prices are plus tax.

**Revenue ESTIMATE (annual run-rate at the end of each year, gross, before fees and tax):**

| Scenario | Year 1 (coins only) | Year 3 (+ postcards, stamps, sports cards) | Year 5 (all 7 categories) |
|---|---|---|---|
| Conservative | 45 paying, **$2.7K** | 231 paying, **$13.6K** | 542 paying, **$31K** |
| Base | 225 paying, **$18K** | 1,200 paying, **$94K** | 3,002 paying, **$222K** |
| Optimistic | 900 paying, **$86K** | 5,712 paying, **$529K** | 16,500 paying, **$1.46M** |

**Plain-English takeaway:** coins alone look like a lifestyle-sized business: tens of thousands to low hundreds of thousands a year, and around $570K a year only if things go very well. Stamps and postcards fit the same 60+ audience and are cheap to add. Sports cards, Pokémon and sneakers are big markets, but they're crowded with funded, free apps, so they add less than their size suggests unless Numista.Ai wins on something specific.

---

## PART 1: Proposed subscription prices, with sources

### 1.1 Public site (checked 10 Nov 2026)
- https://numista.ai and https://numista.ai/pricing show only the title, a Gemini line and the "not affiliated with Numista.com" disclaimer. The page's structured data says `"price": "0"`, USD. **No tiers are published yet.**
- An earlier audit found the pricing page saying "Free During Beta, Pricing TBA" (Chief of Staff transcript, position 8549).

### 1.2 Tier prices
| Tier | Monthly | Yearly | Where found (date) |
|---|---|---|---|
| Copper | $4.99 | $49.99 | Pricing Plan v3.2 in `/workspace/sag/NET-706-R5.md` §5.1 (1 Nov); Stripe sandbox setup memo `/workspace/stripe-plan/20261107_PRIVATE_stripe_setup_prep.md` (7 Nov); laptop `docs\PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.2.md` line 69 (8 Nov) |
| Silver | $8.99 | $89.99 | same three sources |
| Platinum | $10.99 | $109.00 | same three sources |
| Gold | $15.99 | $150.00 | same three sources |

- **Approval:** On 7 Nov 2026 at 11:28 AM ET, Eric told Chief of Staff "You have the regular prices", and the tiers were created exactly as drafted in **Stripe test mode only** (CoS transcript, positions 8779–8781). At 11:33 AM ET he said "Yes, plus tax" (same transcript passage).
- No live Stripe account exists, and app billing is off.
- **Yearly savings** vs. 12× monthly: Copper 16.5%, Silver 16.6%, Platinum 17.3%, Gold 21.8% (NET-706-R5 §5.1).
- **Conflict in code:** NET-706 R7 (1 Nov) notes that the only prices in code were then $4.99/mo and "$29/yr". Checkout in `payment_routes.py` charged 499 cents for any tier (Catalog Plan V3.3, 29 Oct).

### 1.3 Coin limits: the sources conflict
| Tier | Plan V3.3 (29 Oct) and NET-706 R7 (1 Nov, "Eric decision") | NET-827 v1.2 Stripe checkout plan (8 Nov, laptop) |
|---|---|---|
| Free | **10 coins, lifetime** (R7: "Free = 10 coins (settled)") | **20 coins** ("NET-372 … reinforced by Founder directive 3 Nov 2026") |
| Copper | 11–100 | 100 |
| Silver | 101–249 | 250 |
| Platinum | 250–500 | 500 |
| Gold | **501+ (unlimited)** | **1,000** |

Sources:
- V3.3: `MyVertexProject\Numismatics Catalog\29 OCT 26\US_NUMISMATICS_CATALOG_IMPLEMENTATION_PLAN_V3.3.md`, lines 39–46, mirrored on the box.
- R7: `/workspace/sag/PRELAUNCH_PLAN_NET-706_R7_META-AD_20261101.md`, lines 13 and 280–298.
- NET-827: `C:\Users\ericd\Documents\MyVertexProject\docs\PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.2.md`, lines 69–72 and 350–355.

Chief of Staff's own notes and the marketing drafts use **Free 10 and Gold 501+**, and so did Eric's 29 Oct decisions. **Eric needs to settle Free (10 or 20) and the top limits before checkout is built.**

### 1.4 One-time and special prices
| Item | Price | Source |
|---|---|---|
| **Free-tier full export** | **$95.94** (6 × Gold $15.99) | NET-706-R5 §5.1, "Settled – NET-714A"; V3.3 line 309 (founder, 7:17 PM, 29 Oct) |
| Legacy (never paid) full export | $95.94 | same |
| Copper / Silver / Platinum full export | $29.94 / $53.94 / $65.94 (6 × monthly, even on yearly plans) | V3.3 line 309. R7 marks this rule's source **UNVERIFIED**; only the Legacy figure is directly recorded |
| AI top-up | $5 per 1,000 items (credits forfeited on cancel) | NET-706-R5 §5.1; V3.3 line 71 |
| **Beta Special** | **$30 + tax, one-time, a full 6 calendar months**, 101+ coins only, no auto-renew | `/workspace/stripe-plan/20261107_beta_special_draft.md` (Eric via CoS, 7 Nov, 11:09–11:13 AM ET); Stripe sandbox price created 7 Nov |
| **Christmas 2026** | 50% off the **first yearly payment**, all 4 tiers, 26 Nov–25 Dec 2026. Examples: Copper ~$25, Silver ~$45, Platinum $54.50, Gold $75 | `/workspace/stripe-plan/20261107_christmas_offer_draft.md` (Eric via CoS, 7 Nov) |
| Friends & Family code | 100% off forever on any tier, 500 redemptions, closed manually when beta ends. AI allowance $10 in month 1, then $5/month, with top-ups at cost | Stripe private memo (7 Nov). The code itself is private and left out here on purpose |
| **Legacy accounts** | Accounts created before **26 Nov 2026 00:00 ET** (2026-11-26T05:00Z) keep permanent legacy beta access; AI cap = Gold's or the paid tier's, whichever is higher | NET-706-R5 §5.1 "Settled – NET-714A"; R7 §5.4 (Eric, 1 Nov); V3.3 lines 68 and 103 |
| Lifetime membership | **ON HOLD**. $500 recorded 29 Oct, then held; "$1,500" has no source | NET-706-R5 and R7 line 287 |
| Enhanced data-security add-on | $25/yr, target date TBD | `/workspace/bizplan/OPEN_QUESTIONS.md` #19 |
| AI cost caps per month (plan) | Guest $0.10, Free $0.25, Copper $1.00, Silver $1.75, Platinum $2.25, Gold $3.25 | V3.3 lines 62–68 |

### 1.5 Existing business-plan model (for cross-checking)
`/workspace/bizplan/Numista_Ai_Financial_Projections_SUMMARY.md` (6 Nov, all ASSUMPTIONS) projects subscribers at the end of month 12 of Dec 2026–Nov 2027:

| Scenario | Subscribers | 12-month revenue |
|---|---|---|
| Conservative | 24 | ~$2.4K |
| Base | 78 | ~$8.5K |
| Optimistic | 163 | ~$19.5K |

My Year 1 coin numbers below are higher in Base and Optimistic, because I assume a wider reach (ads plus coin clubs).

---

## PART 2: Revenue ESTIMATE

### 2.1 Method
For each category:

**Reachable US collectors × adoption % (share who sign up) × paid conversion % × average revenue per paying user (ARPPU) per year = annual revenue run-rate.**

- **Adoption ramps up** over a category's first five years. In years 1/2/3/4/5 after launch it reaches 15% / 35% / 55% / 75% / 100% of the target adoption below. (ASSUMPTION)
- **Launch order** (ASSUMPTION; follows Eric's order):

| Year | Calendar (approx.) | Categories added |
|---|---|---|
| Y1 | 2027 | US coins (Numista.Ai) |
| Y2 | 2028 | Postcards and stamps (new all-collectibles name) |
| Y3 | 2029 | Sports cards |
| Y4 | 2030 | Pokémon/TCG and comic books |
| Y5 | 2031 | Sneakers |

- Results are **paying subscribers on hand at year-end × yearly ARPPU**, net of churn. That is a run-rate, not cash collected in the year.
- Figures are **gross**. Not deducted:
  - Stripe fees (about 3%),
  - the Apple/Google cut if sold in-app (15% for small developers, 30% otherwise),
  - sales tax (charged on top).
- **ARPPU for coins** (ASSUMPTION): Base **$80/yr**. This assumes a mix of about 50% Copper, 25% Silver, 15% Platinum and 10% Gold, with many on yearly billing; the straight average is about $85. Conservative $60 (mostly Copper, Christmas half-price year). Optimistic $95.
- Younger categories get a lower ARPPU ($50/$60/$80) because Collectr charges $59.99/yr and many card apps are free.

### 2.2 Inputs by category (sources)

| Category | US collector population (sourced) | Reachable "active" collectors used: Cons / Base / Opt (ASSUMPTION) | App benchmarks and pricing (sourced) |
|---|---|---|---|
| **US coins** | **250K–500K active US collectors** (expert estimates, [ANA blog, Nov 2024](https://blog.money.org/coin-collecting/collectors)); 38% of adults have ever collected; **US Mint FY2025 numismatic sales $490.1M, 2.894M units** ([Treasury OIG-26-021](https://oig.treasury.gov/system/files/2026-03/OIG-26-021-%28secured%29.pdf)); PCGS Collectors Club 30K+ ([PCGS](https://www.pcgs.com/news/pcgs-celebrates-40th-anniversary)) | 250K / 375K / 500K | CoinSnap 10M+ Play installs, $39.99/yr ([App Store](https://apps.apple.com/us/app/coinsnap-coin-identifier/id1634551626)); Greysheet Collector $100/yr ([App Store](https://apps.apple.com/us/app/greysheet-rare-coin-pricing/id1546090211)); PCGS Club Silver $69/Gold $149/yr; CoinManage $39.95 one-time ([Liberty Street](https://www.libertystreet.com/coinmanage_purchasing_options.htm)); Numista.com 300K registered, ~47K active, global ([forum](https://en.numista.com/forum/topic163872.html)). Details in `Investor_Deck_Market_Competitor_Data_2026-11-05.md` |
| **Postcards** | **UNKNOWN**. No national count found. Clubs are small (Metropolitan Postcard Club NYC 200+ members, [WRAL/NYT](https://www.wral.com/postcard-people/17294829/)). Often called the third-largest collecting hobby ([Wikipedia](https://en.wikipedia.org/wiki/Deltiology), weak) | 50K / 100K / 200K (pure ASSUMPTION) | Colnect catalogs postcards and stamps, free, with a paid Premium ([Wikipedia](https://en.wikipedia.org/wiki/Colnect)); Premium price **UNKNOWN** (a forum report says ~$100/yr, unverified). No dedicated big US postcard app found |
| **Stamps** | **APS 22,601 individual members (31 Dec 2025)**. APS says there's no accurate count of US collectors, and one national dealer has **100K+ active customers a year** ([APS 2026 Strategic Plan](https://stamps.org/Portals/0/APS_2026%20Strategic%20Plan_FINAL.pdf)). APS membership fell from 52,183 (2000) to 25,546 (2023) ([APS history](https://stamps.org/about/history/membership-historical-data)) | 100K / 150K / 250K | StampManage USA $39.95, Deluxe $89.95 download ([StampManage](https://www.stampcollectingsoftware.com/stampmanage_purchasing_options.htm)); Colnect (above); APS dues $45/yr ([APS](https://stamps.org/membership)) |
| **Sports cards** | **23% of US households** collect sports memorabilia, and about 22% of Americans (51% of collectors) collect sports cards; younger people are twice as likely as 55+ (Seton Hall/YouGov poll, Nov 2025, n=1,564, [SHU](https://blogs.shu.edu/sportspoll/2026/06/30/collecting-sports-memorabilia-is-a-financial-investment-and-a-hobby/)). US adults 18+: ~267.0M (Census Vintage 2024, [Census](https://www.census.gov/newsroom/press-kits/2025/2024-population-estimates-characteristics.html)) | 3M / 5M / 8M (a "serious" slice of the broad 22%) | **CollX 3M+ users, 400K MAU** (Mar 2025), Pro **$9.99/mo or $99.99/yr**, Gold $249/yr, raised $10M ([TechCrunch](https://techcrunch.com/2025/03/07/collx-raises-10m-to-grow-its-card-collection-marketplace/)); **Ludex Pro $24.99/mo or $239.99/yr**, raised $8M+ ([Ludex](https://www.ludex.com/membership/)); PSA app free |
| **Pokémon/TCG** | **19% of adults who bought toys for themselves bought Pokémon cards for themselves** in the prior 6 months; only about a quarter of them play the game (Circana, Mar 2025, via [Retail Brew](https://www.retailbrew.com/stories/2025/06/06/collectible-trading-cards-and-adults-drive-toy-sales-in-2025-circana)). Total US Pokémon collectors **UNKNOWN** | 3M / 5M / 8M | **Collectr 4M+ users, 8-figure ARR, PRO $7.99/mo or $59.99/yr**, bootstrapped ([BetaKit](https://betakit.com/how-collectr-bootstrapped-a-trading-card-hobby-into-an-eight-figure-business/)); CollX and Ludex also cover TCG |
| **Comic books** | Collector count **UNKNOWN** (only informal figures of ~1.5M–2M). North American comics and graphic-novel sales hit **$2.2B in 2025** ([ICv2](https://icv2.com/articles/news/view/61573/icv2-white-paper-comics-graphic-novel-sales-reached-new-high-2025)) | 0.5M / 1M / 2M | **CLZ Comics $1.99/mo or $19.99/yr** (7-day trial), plus CovrPrice values $89.99/yr ([CLZ forum](https://club.clz.com/t/new-member/14122), [AppPricer](https://apppricer.com/app/320501548)); **Key Collector Comics $3.99/mo or $39.99/yr**, 4.8★ ([App Store](https://apps.apple.com/us/app/key-collector-comics-app/id1189623811), [AppPricer](https://apppricer.com/app/1189623811)) |
| **Sneakers** | **7% of US adults call themselves sneakerheads**, mostly 18–34 (YouGov, Feb 2018, [YouGov](https://yougov.com/en-us/articles/20322-sneakerheads-willing-to-miss-work-school-buy-pair)). 7% × 267M ≈ 18.7M, but that figure is 8 years old | 2M / 4M / 8M | **GOAT ~1.3–1.5M weekly active iOS users in the US**, Q1 2025 (Sensor Tower AI summary, [link](https://sensortower.com/blog/2025-q1-ios-top-5-apparel-units-us-64767e9ae1714cfff19fd682)); StockX users **UNKNOWN**; **CheckCheck** 3M+ downloads, 2M+ checks ([press release](https://news.marketersmedia.com/checkcheck-unveils-strategic-evolution-from-sneaker-authentication-app-to-comprehensive-multi-category-platform/89162538)), credits ~$0.76–$1.33 each ([CheckCheck](https://getcheckcheck.com/pricing)) |

**Free-to-paid conversion benchmarks (sourced):** RevenueCat's State of Subscription Apps 2025 covers 75K+ apps. Within 35 days of download:
- the median conversion to paid is **1.9%** overall,
- freemium apps convert **2.18%**,
- hard-paywall apps convert **12.11%**,
- top-quartile apps convert 4.6%,
- the median trial-to-paid rate is **34.8%**.

Sources: [RevenueCat PDF](https://www.revenuecat.com/pdf/state-of-subscription-apps-2025.pdf), [RevenueCat blog](https://www.revenuecat.com/blog/growth/contextual-paywall-targeting), [summary](https://www.rocketshiphq.com/revenuecat-state-of-subscription-apps-2025-summary/). Numista.Ai's 10-coin Free cap acts close to a paywall for anyone with a real collection, so I use rates between the freemium and hard-paywall figures. Paying-user counts for CollX, Collectr, CoinSnap, CLZ and the others are **UNKNOWN**.

### 2.3 Model assumptions per category (all ASSUMPTION)
| Category | Launch year | Adoption target after 5 yrs (Cons / Base / Opt) | Paid conversion of sign-ups | ARPPU $/yr | Why |
|---|---|---|---|---|---|
| US coins | Y1 | 4% / 8% / 15% | 3% / 5% / 8% | 60 / 80 / 95 | Core product. 60+ audience, Morgan AI, Mint-invoice import; no dominant US coin manager |
| Postcards | Y2 | 3% / 6% / 12% | 3% / 5% / 8% | 60 / 80 / 95 | Same older audience; little app competition; uncatalogued, so AI ID is harder |
| Stamps | Y2 | 3% / 6% / 12% | 3% / 5% / 8% | 60 / 80 / 95 | Same audience; competitors are desktop software and Colnect |
| Sports cards | Y3 | 0.2% / 0.5% / 1.5% | 2% / 3% / 5% | 50 / 60 / 80 | Crowded: CollX, Ludex, Collectr, PSA, many of them free |
| Pokémon/TCG | Y4 | 0.2% / 0.5% / 1.5% | 2% / 3% / 5% | 50 / 60 / 80 | Collectr dominates with 4M+ users |
| Comic books | Y4 | 0.5% / 1.5% / 3% | 3% / 4% / 6% | 50 / 65 / 85 | CLZ and Key Collector are cheap ($20–$40/yr) and well liked |
| Sneakers | Y5 | 0.1% / 0.3% / 1% | 2% / 3% / 5% | 50 / 60 / 80 | Marketplaces (GOAT, StockX) own the user; low demand for paid tracking |

### 2.4 Results by phase (users / paying / annual revenue run-rate), ESTIMATE
| Scenario | Year | P1 Coins: users / paid / revenue | P2 Postcards+Stamps | P3 Sports cards+Pokémon | P4 Comics+Sneakers | **TOTAL users / paid / revenue** |
|---|---|---|---|---|---|---|
| Conservative | Y1 | 1,500 / 45 / $2,700 | not launched | not launched | not launched | **1,500 / 45 / $2,700** |
| Conservative | Y3 | 5,500 / 165 / $9,900 | 1,575 / 48 / $2,835 | 900 / 18 / $900 | not launched | **7,975 / 231 / $13,635** |
| Conservative | Y5 | 10,000 / 300 / $18,000 | 3,375 / 102 / $6,075 | 5,400 / 108 / $5,400 | 1,175 / 32 / $1,612 | **19,950 / 542 / $31,087** |
| Base | Y1 | 4,500 / 225 / $18,000 | not launched | not launched | not launched | **4,500 / 225 / $18,000** |
| Base | Y3 | 16,500 / 825 / $66,000 | 5,250 / 263 / $21,000 | 3,750 / 112 / $6,750 | not launched | **25,500 / 1,200 / $93,750** |
| Base | Y5 | 30,000 / 1,500 / $120,000 | 11,250 / 563 / $45,000 | 22,500 / 675 / $40,500 | 7,050 / 264 / $16,890 | **70,800 / 3,002 / $222,390** |
| Optimistic | Y1 | 11,250 / 900 / $85,500 | not launched | not launched | not launched | **11,250 / 900 / $85,500** |
| Optimistic | Y3 | 41,250 / 3,300 / $313,500 | 18,900 / 1,512 / $143,640 | 18,000 / 900 / $72,000 | not launched | **78,150 / 5,712 / $529,140** |
| Optimistic | Y5 | 75,000 / 6,000 / $570,000 | 40,500 / 3,240 / $307,800 | 108,000 / 5,400 / $432,000 | 33,000 / 1,860 / $155,100 | **256,500 / 16,500 / $1,464,900** |

### 2.5 Results by category, ESTIMATE
| Scenario | Year | Category | Registered users | Paying subscribers | Annual revenue run-rate |
|---|---|---|---|---|---|
| Conservative | Y1 | US coins | 1,500 | 45 | $2,700 |
| Conservative | Y3 | US coins | 5,500 | 165 | $9,900 |
| Conservative | Y3 | Postcards | 525 | 16 | $945 |
| Conservative | Y3 | Stamps | 1,050 | 32 | $1,890 |
| Conservative | Y3 | Sports cards | 900 | 18 | $900 |
| Conservative | Y5 | US coins | 10,000 | 300 | $18,000 |
| Conservative | Y5 | Postcards | 1,125 | 34 | $2,025 |
| Conservative | Y5 | Stamps | 2,250 | 68 | $4,050 |
| Conservative | Y5 | Sports cards | 3,300 | 66 | $3,300 |
| Conservative | Y5 | Pokemon/TCG | 2,100 | 42 | $2,100 |
| Conservative | Y5 | Comic books | 875 | 26 | $1,312 |
| Conservative | Y5 | Sneakers | 300 | 6 | $300 |
| Base | Y1 | US coins | 4,500 | 225 | $18,000 |
| Base | Y3 | US coins | 16,500 | 825 | $66,000 |
| Base | Y3 | Postcards | 2,100 | 105 | $8,400 |
| Base | Y3 | Stamps | 3,150 | 158 | $12,600 |
| Base | Y3 | Sports cards | 3,750 | 112 | $6,750 |
| Base | Y5 | US coins | 30,000 | 1,500 | $120,000 |
| Base | Y5 | Postcards | 4,500 | 225 | $18,000 |
| Base | Y5 | Stamps | 6,750 | 338 | $27,000 |
| Base | Y5 | Sports cards | 13,750 | 413 | $24,750 |
| Base | Y5 | Pokemon/TCG | 8,750 | 262 | $15,750 |
| Base | Y5 | Comic books | 5,250 | 210 | $13,650 |
| Base | Y5 | Sneakers | 1,800 | 54 | $3,240 |
| Optimistic | Y1 | US coins | 11,250 | 900 | $85,500 |
| Optimistic | Y3 | US coins | 41,250 | 3,300 | $313,500 |
| Optimistic | Y3 | Postcards | 8,400 | 672 | $63,840 |
| Optimistic | Y3 | Stamps | 10,500 | 840 | $79,800 |
| Optimistic | Y3 | Sports cards | 18,000 | 900 | $72,000 |
| Optimistic | Y5 | US coins | 75,000 | 6,000 | $570,000 |
| Optimistic | Y5 | Postcards | 18,000 | 1,440 | $136,800 |
| Optimistic | Y5 | Stamps | 22,500 | 1,800 | $171,000 |
| Optimistic | Y5 | Sports cards | 66,000 | 3,300 | $264,000 |
| Optimistic | Y5 | Pokemon/TCG | 42,000 | 2,100 | $168,000 |
| Optimistic | Y5 | Comic books | 21,000 | 1,260 | $107,100 |
| Optimistic | Y5 | Sneakers | 12,000 | 600 | $48,000 |

### 2.6 The three assumptions that matter most
1. **Coin adoption (the share of reachable US collectors who sign up).** Coins are 39–58% of Year-5 revenue and 100% of Year 1. Going from 8% to 4% halves Base coin revenue; going to 15% nearly doubles it. Nobody knows the real number until the 26 Nov launch and the $625 Meta ad produce real signup data.
2. **Paid conversion (3% / 5% / 8%).** The real rate depends on whether Free stays at 10 coins or becomes 20, and on whether the Christmas and Friends & Family offers pull people into paid plans or let them stay free. RevenueCat's medians run from 2.2% (freemium) to 12.1% (hard paywall), so this one input can swing revenue 2–4×.
3. **Reachable population for each new category**, especially the young card, Pokémon and sneaker markets. Their populations are huge (millions), but Numista.Ai's realistic share there is tiny. The postcard count is pure guesswork (UNKNOWN), and the stamp count rests on APS's 22.6K members plus one dealer's 100K customers.

ARPPU ($60–$95) matters less: the tier prices are known, and only the mix between tiers is unknown.

### 2.7 Risks
- **Crowded, well-funded card and sneaker markets.**
  - CollX has raised $15.5M+ (TechCrunch 2023 and 2025).
  - Ludex has raised more than $8M.
  - Collectr reached 8-figure ARR with 4M+ users.
  - The Collectors group (PSA, PCGS) was valued at $4.3B in 2022.
  - GOAT and StockX own sneaker collectors through their marketplaces.
  - Competing there needs a clear wedge, such as one app for a whole household's collections, estate and insurance reports, or helping older collectors' heirs. Matching features alone won't be enough.
- **Name conflict with Numista.com.** Numista.com is a well-known 2007 catalog with 300K registered users worldwide. The site already carries a "not affiliated" disclaimer. A rename for the all-collectibles app is a chance to drop the conflict entirely; check trademarks first (open question #34 in the business plan).
- **Audience fit.** Coins, stamps and postcards skew 60+ (APS points to the "silver tsunami" of retirees), which matches Numista.Ai's design for older collectors. Cards, Pokémon and sneakers skew 18–34: Seton Hall found 30% of 18–34s collect sports memorabilia vs. 17% of 55+, and sneakerheads are mostly 18–34. One app for both groups risks a confusing experience. Consider a calm "classic" mode alongside a faster, social "modern" mode.
- **Shrinking older hobbies.**
  - US Mint numismatic units fell 19% in FY2025.
  - APS membership roughly halved from 2000 to 2023.
  - Inherited collections, though, are a real opportunity for valuation and export features.
- **AI cost and accuracy** grow with each new category (Morgan must not bluff). Postcards have no standard catalog, which makes AI identification harder.
- **App-store fees:** selling inside iOS or Android apps cuts 15–30% of revenue unless subscriptions are sold on the web through Stripe.
- **Execution:** Numista.Ai is a one-person company, and the bizplan's Base case needs a part-time coder from Mar 2027. Each new category means new catalog data, licensing and AI tuning.

### 2.8 What would improve this estimate
- Real numbers from the 26 Nov launch: signups per ad dollar, Free→paid rate, tier mix, yearly vs. monthly split.
- Coin club and show surveys.
- An actual count of US postcard collectors, perhaps through postcard-show organizers.
- Colnect's US user count and Premium price, and APS help reaching its 100K-customer dealer audience.

*Model file: `/workspace/revmodel/model.py` (edit the inputs and re-run to change any assumption).*
