# SAG Paste Packet: NET-646 Plan v3.2
Use this because the box SAG launch was blocked. Open Stand Alone Grok (grok-4.7), ATTACH these two files from this folder, then paste everything below the line:
1. US_NUMISMATICS_CATALOG_IMPLEMENTATION_PLAN_V3.2.md
2. NET-646_V3.0_APPENDIX_WRITE_AUDIT.md
Save the reply as SAG_NET-646_PLAN-V3.2_20261029.md in this folder.

---
You are a strict, independent senior reviewer of software architecture and implementation plans. You have no prior context about this project or any earlier reviews. Judge only the two attached documents. Be skeptical: verify technical claims (Firestore security rules syntax and OR semantics, transaction semantics and the 500-document limit, idempotency, counters, Stripe webhook ordering, write-guard coverage) rather than trusting the plan's own claims of closure.

Task: independent review of Plan v3.2 (NET-646) plus its write-site appendix (v3.0 appendix; the v3.1/v3.2 additions are in plan section 11). Pass mark is 95/100.

Earlier reviewer blockers to verify closed:
(A) Webhook wrote users.stripe_tier, not the entitlement doc the cap reads; no status check; lost events; no email in checkout metadata.
(B) currency/world_items updates could forge count_weight_q.
(C) Free/guest users could mint set coins at 1/4 and ungroup to about 40 loose items.
(D) Group/ungroup/break-up/clear-all exceeded the 500-doc transaction limit.
(E) The write guard missed main.py's own Firestore client, CollectionReference.add, and merge-set creates.
(F) Checkout charged 499 cents for any client-sent tier, and the webhook trusted metadata.target_tier (confirmed in the repo).
(G) Set fields stayed client-editable after P3, and group assumed a fixed 4:1 weight, so unlink plus regroup freed quarters.
(H) One-time top-up payments were dropped by the subscription high-water-mark check.

Founder decisions (real, do not penalize):
- Legacy = non-anonymous accounts created before 00:00 ET 27 Nov 2026, set by a cutoff snapshot. Unlimited items even when paying.
- Free: 10 items lifetime. Guest: 5 items.
- Copper 11-100 items, $4.99/mo or $49.99/yr.
- Silver 101-249 items, $8.99/mo or $89.99/yr.
- Platinum 250-500 items, $10.99/mo or $109/yr.
- Gold 500+ unlimited, $15.99/mo or $150/yr.
- Lifetime tier on hold. Set coins count as 1/4 item. Ungroup adds to the lifetime count. Daily limits retired.
- Monthly AI caps: Free $0.25, Copper $1, Silver $1.75, Platinum $2.25, Gold $3.25, Legacy $3.25, Guest $0.10. AJ has no AI cap. First month cap = one month of plan price.
- Top-ups: $5 per 1,000 items scanned, forfeited on cancel.
- Cancel = read-only with all items visible.
- Basic export (free) = zip of the CSV plus the user's own photos. Full export = 6x the monthly price of the last paid tier.
- Stripe goes live Nov 27 only if the AI caps are set.
- estate/family_estate holders become Gold. AJ is a named unlimited account. Morgan adds count toward the cap.
- 30-day retry edge case accepted. Guest seed and checklist stop at P3.
- Margin 70-80%; accounts over 1,000 items may break even in year 1. Force-update yes.
- Grok CoS owns the cutoff snapshot script.

Pending founder (do not penalize): full export for never-paid accounts, Legacy top-ups without a subscription, hand refunds, the founder email address, Stripe timing if P1 slips. Flag any other invented decision.

Do not describe what you will do; write the complete review now. Return markdown with exactly these sections:
1. Score: N/100
2. Verdict: GO / CONDITIONAL GO / NO-GO (planning only)
3. Prior blockers: status table (A-H)
4. Remaining blockers (ranked, max 5)
5. Invented decisions / founder-decision check
6. Risks
7. Reaches 95? (yes/no and why)
