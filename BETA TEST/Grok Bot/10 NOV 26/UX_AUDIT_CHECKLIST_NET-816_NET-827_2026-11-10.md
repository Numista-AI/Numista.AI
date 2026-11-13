# UX audit checklist: NET-816 Catalog Chunk 1 + NET-827 Stripe Checkout v1.2
UX Designer, 10 Nov 2026, 11:05 AM ET. Read only. This is not an approval gate. Lens: could AJ (an 83-year-old collector, not tech-savvy) do it without help?
Ranking: MUST-FIX = would confuse or block an AJ-type user (unclear price, unclear what you're paying for, no clear way back, tiny tap targets, low contrast). SHOULD and NICE are separate.
Sources: live https://numista.ai/catalog and /pricing at 1280 wide (screenshots on the box under /workspace/numista-ux/audit-2026-11-10/live/), docs\FAILFIX_PLAN_NET-777_CATALOG_CHUNK1_v2.2.md, docs\PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.2.md.

## PART A. Findings today (live site + plans)

### Live /catalog
MUST-FIX
- A1. Searching "1921 morgan" returns 0 items. The most common search an older collector would try finds nothing, and the forgiving-search rule fails. (It may only be a data gap if Morgan dollars aren't loaded yet. If so, the empty state has to say that.)
- A2. Empty state: "No matching catalog items found." It doesn't say what to do next. Suggested copy: "We couldn't find that yet. Try just the year, or Ask Morgan." Add a big Ask Morgan button and a "Clear search" button with text, not a small link.
- A3. The card dialog shows data bugs, "Mint Mark: true" and "Composition: Composition". This reads as broken to a collector.
- A4. Small text across the page: card meta (year · denomination) about 12-14px, badges 12-14px, the "type photo (date may differ)" note about 11-12px, the "No photo yet" text about 11px. The rule is 18px body, and the catalog standard is 20px.
- A5. The card dialog closes only with an icon-only X. Add a labeled "Close" button of 48px or larger.
SHOULD
- A6. Long card titles are cut off with "…" ("Wi…", "Mon…"). Let titles wrap to 3 lines.
- A7. The "Coins (2,965)" count doesn't change with a search, while "0 items" shows elsewhere. The two numbers disagree.
- A8. Every card shows "No photo yet", so the catalog looks empty. Sort items with an image and a source first (agreed in the catalog plan).
- A9. The first tap on a card gives no visible response and feels laggy. Show a pressed state or loading feedback.
- A10. Grey meta text and the grey "Mintage: not yet sourced" are low contrast. Use #333 or darker.
- A11. The search clear X and the era dropdown arrow are icon-only. Add text labels.
NICE
- A12. A large empty gap above the heading at first load.
- A13. About 166 console errors (for Code Reviewer/AG, not UX).
- A14. The card dialog has no tabs. Once the unified details view (locked for 10-16 Nov) ships, the catalog should use the same layout.

### Live /pricing (today) vs the NET-827 plan
MUST-FIX
- B1. The live page says "Free During Beta, Pricing TBA … you will not be asked to pay for your active beta access", but NET-827 sells a $30 Beta Special. Both can't be true when checkout ships. The pricing copy must be rewritten with checkout, or users will feel tricked.
- B2. The live page doesn't show the tiers (Copper/Silver/Platinum/Gold, monthly and annual), and Eric's pre-26 Nov list requires the pricing tiers on the site.
- B3. Badges "BETA PRICING" and "OPEN PUBLIC BETA" are about 10-11px tan on beige, and the body text is about 13-14px. Both fail size, and the badges likely fail contrast.
- B4. The back arrow is icon-only. Use a labeled "Back" button, or a consistent nav that includes Home.
SHOULD
- B5. There's no pricing link from the catalog page. Add "Plans & prices" to the standard nav.
- B6. The "Explore Demo Vault" link is tan text, low contrast. Make it a real button.
FLAG FOR CoS (not UX to decide)
- B7. The coin limits don't match each other: the plan's free tier is 20 coins, memory says the free trial is "first 10 coins" (Eric, 1 Nov), and the tiers say Gold covers 1,000. CoS should confirm the one true number before the copy is written.

### NET-827 plan (no screens specified)
- C1. The plan has no pricing-page layout, button labels, or Settings success/cancel copy. I'll judge the preview as built, and I recommend the copy below so AG doesn't invent it.
- Recommended copy (plain words):
  - Plan card button: "Choose Silver, $8.99 a month". The price is always on the button.
  - Beta Special button: "Get 6 months for $30 (one payment, no auto-renew)".
  - Before Stripe opens: "You'll go to Stripe, our secure payment page. You can come back any time with the Back button."
  - Success, while waiting for the webhook: "Thank you! We're confirming your payment. This usually takes under a minute." Then "You're all set. Your Silver plan is active." and a big "Go to my collection" button.
  - Cancel: "No charge was made. You can choose a plan any time." with "Back to plans" and "Go to my collection" buttons.
  - Pending (ACH or similar): "Your payment is on its way. Your plan starts as soon as the bank confirms."
  - Overflow banner: the plan's copy is OK if the counts are in words people know. Use "Upgrade to Silver" as a button, never only a link.

## PART B. What I'll check on the p7-gate preview (after Field Tester scores it)
Widths: 1440 and 1024 are required, 390 is noted only. Also check at 200% browser zoom and with big system fonts.

### Catalog Chunk 1 (NET-816)
1. Card title 18px or larger (target 20px). Meta 18px or larger. Face-value amount readable. Amber chip text 18px or larger, with measured contrast of 4.5:1 or better (aim for 7:1).
2. Face value is honest: medals show "No face value", unknown values show "—" and never "$0.00", half cents show "$0.005". Chip copy: "Face value · No retail estimate".
3. Home dashboard "Face Value" and stats-bar totals still make sense after the parser change (e.g. Five Cents = $0.05). No real values in screenshots.
4. Search finds "1921 morgan", "morgan 1921", "morgan dollar" and "1921 morgn". If not, the empty state says what to do next.
5. The card dialog has a labeled Close, no "true" or "Composition: Composition" values, and a working "Ask Morgan about this coin" button.
6. Every tap target is 48px or larger: chips, filters, the Photos only toggle, sort, and cards.
7. The same top nav as the rest of the site, and the browser Back button returns to the same scroll spot.
8. Loading and error states use plain words, with no blank grid or spinner forever.

### Stripe Checkout v1.2 (NET-827), Stripe sandbox only, no real cards
9. The pricing page shows every tier with price, billing period, coin limit and what's included, in 20px text and with no fine print below 18px.
10. Every buy button names the plan and price. No unlabeled "Continue".
11. Beta Special clearly says "one payment, no auto-renew, 6 months".
12. A clear note before Stripe that you're leaving to a secure page and how to come back.
13. The success page (Settings ?stripe=success) shows a calm "confirming" state, then a confirmed plan name, and one big next-step button. It never claims to be active before the webhook.
14. The cancel page says "No charge was made" and gives a big way back.
15. Declined card, 3-D Secure, and pending ACH each show a plain-words message with the next step.
16. The overflow banner (101+ coins) is readable, says no coins are lost, and has a labeled Upgrade button.
17. The Christmas annual promo shows the real price before and after the discount. The monthly plans show no promo field, so users aren't confused.
18. Contrast is AA or better everywhere (AAA aimed), with no white-on-white or tan-on-beige.
19. Nothing on these screens shows a collection value or a storage location.

Deliverable after the preview: a PASS / FIX list in this same Must/Should/Nice format, with screenshots (example data only) and before/after mock(s) for any Must-Fix.
