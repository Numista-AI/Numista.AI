# WAKE - AG CoS v4 - NET-718 - SECURITY & USER-PROTECTION PLAN (PLAN-ONLY) - 01 Nov 2026 4:40 PM ET

**From:** Grok CoS | **To:** AG CoS v4 | **Authority:** Eric typed "Yes, start the security plan now" (01 Nov 2026 4:35 PM ET) - authorizes PLAN drafting only.
**Mode:** DOCS-ONLY. Zero code edits, commits, deploys, GCS/Firestore writes. Locks: main 9f04550a, dev 32d4b42e, Stripe OFF.
**Queue:** #1 NET-716 (NET-706 R4 fix-only, Meta launch 26 Nov) -> #2 **NET-718 (this)** -> #3 NET-647 R2.8.10 -> #4 NET-705.
**Deadline:** Plan through Argon, Grok CoS >=95, SAG, Eric typed YES BEFORE 26 Nov 2026.
**Deliverable:** `SECURITY_PLAN_NET-718_USER-PROTECTION_<YYYYMMDD>.md` in INBOX + RADIO NET, plus RADIO_OVER + BATON to Grok CoS/Argon.

## Founder goal
A breach must never be a treasure map for home invaders. Aunt Janet (AJ account, 83, lives alone) holds our largest collection.

## Spec (all 10 required)
1. **No postal addresses anywhere.** Audit every form, schema, Firestore collection for address/phone/location fields; list each with file:line and removal plan.
2. **Auto-redaction of receipt/invoice scans.** Keep scan; black out ship-to/bill-to address + person name BEFORE storage (Document AI entities + OCR bounding boxes). Never store unredacted original - incl. temp buckets, logs, caches. Low confidence -> user review before save. Backfill plan for existing scans (AJ receipt PDFs) - DRY-RUN REPORT FIRST, no writes.
3. **Strip EXIF/GPS** on all uploaded photos (web + mobile), server-side as backstop.
4. **Values private by default.** No totals on public/shared/wishlist views unless user opts in. Display names optional.
5. **2FA prompted above collection-value threshold.** [ERIC DECISION] threshold ($5,000 is example only). Required for AJ.
6. **Firestore + Storage rules audit** - no cross-user reads; emulator test suite listed.
7. **Secrets in Secret Manager only**; repo leaked-key scan (plan the tool + history scan); rotation plan for any hit.
8. **Meta pixel sends event names only** - no PII, coin data, or values (reconcile with NET-706 Purchase event).
9. **Data minimization:** full account deletion (Auth + Firestore + Storage), short log retention, no PII in logs.
10. **Site copy PROPOSAL:** plain-words "we never ask where you live" line, [ERIC DECISION] to approve.

## Rules
- Cite real files + line numbers from origin/dev 32d4b42e. Anything new marked **PROPOSED**.
- Do not invent prices, SKUs, or costs; any GCP cost estimate must cite its source or be marked TBD.
- Include per-item: current state, gap, proposed fix, test, owner, est. effort, risk.
- Lessons/self-improvement section required.
- Agent claims are not approval; only Eric's typed YES executes.
