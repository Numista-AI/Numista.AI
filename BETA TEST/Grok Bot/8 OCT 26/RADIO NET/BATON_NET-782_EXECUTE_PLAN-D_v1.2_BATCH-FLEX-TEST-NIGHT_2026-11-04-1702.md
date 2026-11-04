# BATON NET-782 - EXECUTE Plan D v1.2: Batch/Flex Test Night
To: AG CoS v4   From: Antigravity Desk   4 Nov 2026 5:02 PM ET
QUEUE: after NET-778 and NET-780. Do not start before FIN OPS records the worst case.

AUTHORITY: Eric answered Chief of Staff's question at 4:57 PM ET on 4 Nov 2026 with "YES, execute Plan D".
Plan: Plan D v1.2 (NET-766) in INBOX. SAG scored it 96.

HARD LIMITS:
- 200 requests or fewer.
- Start no later than 12:30 AM ET.
- No new calls after 2:30 AM ET.
- Worst case under $5.
- 4 concurrent requests or fewer.
- At least 30 pairs.

NOT COVERED by this YES:
- Submitting a Batch job. If the plan needs one, STOP and file BLOCKED.
- Anything going to Firestore.

BEFORE START: FIN OPS must record the worst-case cost.
NO COLLISION with tonight's NET-760 catalog run (Catalog Research, which must stop by 3 AM). If the two would overlap on quota or project, STOP and file BLOCKED.
main stays 9f04550a, Stripe stays OFF.

REPORT: file EXECUTE_DONE_NET-782 with the request count, actual spend, pair results and stop time.

---
## AMENDMENT - FIN OPS WORST CASE (INBOX\FINOPS_WORSTCASE_NET-782.md, 5:06 PM ET)
The worst case is $4.05 and passes the limit ONLY IF ALL THREE of these hold. Confirm each one in writing in a PREFLIGHT_NET-782.md before the first call:
1. The model is Gemini 3.8 Flash ONLY.
2. Hard caps in the script: 6,000 input tokens or fewer and 1,500 output tokens or fewer per request.
3. Project numista-qc (My Billing Account).
NO-GO, so STOP and file BLOCKED, if any of these is true:
- It would use 3.1 Pro (worst case $6.00).
- It would reuse the main.py calls that allow up to 65,536 output tokens (up to about $98).
- It would run on numista-morgan-pilot (that collides with NET-760's $50 cap).
Budgets only send alerts. The script caps are the ONLY hard stop.
