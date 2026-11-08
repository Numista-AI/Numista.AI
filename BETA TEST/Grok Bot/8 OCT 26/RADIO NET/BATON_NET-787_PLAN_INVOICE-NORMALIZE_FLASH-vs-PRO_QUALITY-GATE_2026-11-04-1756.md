# BATON NET-787 - PLAN ONLY: quality gate for moving invoice normalization from 3.1 Pro to 3.8 Flash (from the NET-778 audit)
Eric's conditional YES (typed 5:17 PM ET, relayed by CoS): "If it's 94% cheaper and is still capable of high quality work."
The plan must cover:
- A fixed set of real test invoices, non-PII or redacted (the ship-to name and address blacked out).
- Flash and Pro run side by side, with field-level accuracy on SKU, qty, unit price, fees and totals.
- Pass bar: Flash matches Pro on EVERY key field.
- A cost cap for the test.
- A rollback flag.
- Flash goes in ONLY if it passes.
Normal review cycle: Argon, then CoS 95+, then SAG, then Eric's typed YES. Queue this AFTER the FAILFIX plans. No code, no calls until approved.
