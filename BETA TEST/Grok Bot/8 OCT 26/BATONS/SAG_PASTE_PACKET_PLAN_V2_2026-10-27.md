# PASTE INTO STAND ALONE GROK - Numista.Ai Mint B- Plan.v2 review (round 2 of 4)
You are the 4th reviewer in a locked chain (AG writes plan -> Argon -> Grok Bot CoS -> you -> execute). Please give blunt feedback, no code.

Context: Eric's 27 Oct beta test of Mint invoice import. Uploading a 2nd US Mint invoice for the 2026 Uncirculated Coin Set (SKU 26RJ) showed 0 Duplicates Flagged; the new 26RJ came in with blank Theme/Subject, no image, $0.00 value, no 20-COIN SET strip; "Footlocker" storage text was white on cream; the 20-coin strip cut off the 5th coin.

Reviews so far:
- Argon 84/100 CONDITIONAL GO. Gaps: (1) duplicate counter; (2) receipt normalizer drops Theme/Subject + Strike Type, catalog needs 26RJ set metadata (is_set, set_id uncirculated-coin-set-2026, images, Mint issue price 124.50); (3) _OwnerPhotoHero hardcoded white text; (4) CoinSetViewer horizontal strip clips coins.
- Grok Bot CoS 82/100 CONCUR CONDITIONAL GO with corrections: the worker DOES set duplicates_flagged from an existing _run_duplicate_sweep, so don't add a 2nd dupe engine. Real causes: the sweep loads existing coins with Firestore `import_session_id != session` (silently skips coins missing that field), and its score never compares SKU or invoice number. 26RJ is not in the Mint product catalog at all (add, plus audit every SKU on the test invoices). Backfill of Eric's test coins is preview-only; live writes need Eric's YES.

Questions for you:
1. Is fixing the existing sweep (include coins missing import_session_id + add SKU/invoice scoring) the right call vs. a new pre-check?
2. Anything missing for a first-try pass on Eric's retest (dupe, set enrichment, contrast, set strip)?
3. Any risk in an authoritative catalog overwrite on SKU match?
4. Score out of 100 and GO / CONDITIONAL GO / HOLD.
