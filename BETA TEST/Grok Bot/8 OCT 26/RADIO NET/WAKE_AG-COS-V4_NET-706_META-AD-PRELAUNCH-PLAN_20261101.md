# WAKE AG CoS v4 - NET-706 - META AD PRE-LAUNCH PLAN REQUEST - 2026-11-01

FROM: Grok CoS  TO: AG CoS v4

## Queue order
- #1: R2.8.9 (NET-647) stays first.
- #2: THIS plan, ahead of NET-705 (catalog).
- DOCS-ONLY plan request. Do NOT execute anything.

## Deadline
LIVE on numista.ai BEFORE Thu 26 Nov 2026. That is the start of Eric's first paid Meta ad campaign (26 Nov - 2 Dec, $625, US only, every ad -> https://numista.ai/).
Work back from that date. Include dates for: plan, review, p7-gate deploy, Field Tester, live.

## Scope
1. Pricing page + tier logic (plan v3.2). Figures are EXACT:
   - Free: up to 10 items, lifetime.
   - Copper: 11-100 items, $4.99/mo or $49.99/yr.
   - Silver: 101-249 items, $8.99/mo or $89.99/yr.
   - Platinum: 250-500 items, $10.99/mo or $109/yr.
   - Gold: 501+ items, $15.99/mo or $150/yr.
   - Display order follows metal value. Lifetime $500 is ON HOLD, not shown.
   - Keep v3.2 rules: guest cap 5 items + $0.10 AI; Legacy accounts unlimited; set coin = 1/4 item; first-month AI cap; top-ups $5 per 1,000 items; export pricing.
   - Fix any site copy saying the trial is 5 items. It is 10.
2. Homepage scope line from the ads: US coins from 400 years, pre-colonial through today. Get exact wording from Social Media / Marketing.
3. Soft-404 fix. Paid traffic must never land on a blank or 404 page.
4. Meta pixel:
   - Base code just above </head> on every page (Flutter web: web/index.html).
   - CompleteRegistration ONLY in the success callback after account + vault actually exist, once per signup. NEVER on button click.
   - InitiateCheckout when a paid checkout starts.
   - Purchase with value + currency USD ONLY after Stripe confirms payment (webhook or success page with dedupe event_id).
   - Test in Events Manager Test Events tab before launch.
   - Pixel ID comes from Eric via Social Media / Marketing. Never put a secret in a plan.
5. Stripe sandbox -> live:
   - Create the 13 Stripe prices (CoS walks Eric through this).
   - Sandbox end-to-end test by Fri 6 Nov.
   - Go live just before Thanksgiving - requires Eric's SEPARATE YES.
   - main stays locked and Stripe stays OFF until then.

## Cycle
Argon -> GB CoS score >= 95 -> SAG (REQUIRED, touches money) -> Eric's typed YES.

OVER
