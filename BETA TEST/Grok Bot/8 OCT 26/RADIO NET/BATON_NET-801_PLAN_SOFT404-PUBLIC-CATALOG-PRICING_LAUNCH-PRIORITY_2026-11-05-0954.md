# NET-801 (LAUNCH PRIORITY) - Soft-404s, public catalog decision, Pricing button
PLAN ONLY. Queued AFTER NET-798 (and its EGM gate). Source: QC Steward no-silos site pass (read-only, 5 Nov ~9:40 AM ET), relayed by GB CoS. Full notes live with QC Steward. Cycle: Argon, then GB CoS 95+, then SAG, then Eric's typed YES. Plan A caps apply. Locks: main 9f04550a, Stripe OFF, no Firestore, no deploy, no PII. No execute without Eric's separate YES.

**Renumbered from NET-800** at ~9:54 AM ET 5 Nov: NET-800 was already taken by GB CoS 3 AM stand-down radio (`NET-800_GROKCOS-to-AGCOS_STAND-DOWN-0300_OVER.md`, commit b0b05808 in catalog_wt RADIO NET). Treat any Desk `BATON_NET-800_PLAN_SOFT404*` / `ACK_RADIO_NET-800_FILED*` as superseded by this NET-801 baton.

## Launch-priority (must cover in the plan)
1. **Soft-404s (ties to existing soft-404 must-ship before Meta ads 26 Nov):** `/catalog`, `/pricing`, `/about`, and bad paths all return HTTP 200 with the same page title. Footer links behave as buttons, not real URLs. Plan must fix real routing / status / titles so bad paths are true 404s (or proper redirects) and footer links are real navigable URLs.
2. **Catalog behind login vs homepage claim:** The catalog sits behind the login wall while the homepage claims **5,142 Reference Coins**. Plan must propose a **public** catalog/view option. Eric decides go / no-go on making it public; do not ship a public catalog without his typed YES.
3. **Pricing button:** QC Steward saw the Pricing button not open pricing (**UNVERIFIED**). Plan must check it on live/preview and fix if broken (route, handler, or link).

## Lower-priority ideas (list in the plan; do not block launch on these alone)
- `AI+ Community Verified` looks like a placeholder stat.
- PIN / password sign-in wording is confusing.
- `Morgan AI` and `Lateral transfer` jargon for older collectors.
- Footer disclaimer screen-reader / reading order.

## Out of scope this baton
- No code, deploy, Firestore, Stripe, or main merge.
- No PII. No AJ data.
- Do not run EGM on this unless CoS later marks it a big-feature plan (EGM gate is on NET-798 first).
