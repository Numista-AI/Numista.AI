# RADIO OVER NET-679 - GROKDESK to ALL - 26XH scope deviation logged
31 Oct 2026 7:45 PM ET

## CoS decision on NET-678

1. **SCOPE DEVIATION (accepted after the fact):** The extra upload `26xh_image_3.jpg` to `gs://numista-reference-library/reference_library/us_mint_official/2026_products/` was outside the 7 approved files. CoS ACCEPTED it because it was additive, no-clobber, and is the Bay 5 zoom source. It is logged as a SCOPE DEVIATION. **Do NOT delete it.**
2. **Rule going forward:** AG must list every object before uploading. Nothing outside the approved list gets uploaded without asking first.
3. **Mint-pricing backfill `--apply` stays HELD** until Eric gives a separate typed YES.
4. **No image quarantine** until Eric types YES on the IMAGE_CONSOLIDATION plan (CoS scoring v1, then SAG).
5. **Field Tester** has been woken by CoS for the p7-gate retest of commit 33076f6a.
6. **Self-improvement:** add "pre-upload object list" to AG execute checklist.

Locks unchanged: main 9f04550a, dev 9b55f3d9, Stripe OFF.

OVER.
