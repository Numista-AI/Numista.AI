# DESK NOTE NET-754: Argon scored NET-747 plan v3 88 REVISE (2026-11-03 2:50 PM ET)

**BLUF:** Argon scored AG's catalog browse plan v3 88/100, REVISE to v4. Four of six checks pass. Two checks fail because the plan would still leak "collection" wording into the public catalog file. Nothing was coded, committed, or deployed.

**What passed:** the counts (3,202 = 2,965 coins + 181 notes + 56 medals; 4 sourced mintages), the "Newest entries" date note with seeds excluded, the navy Ask Morgan button, and the Firestore rules guard with deploy limited to the p7v12 preview.

**What must be fixed in v4 (Argon's must-fixes):**
- MF-v3-A: the plan lets the image "source" field through, and 989 type/secondary images carry "collection photo, owner removed". It also drops "file" from primary_image, which breaks 81 exact-year images.
- MF-v3-B: all 1,724 figures.composition entries say "collection-derived" / COLLECTION_DERIVED, and the figures sub-fields aren't limited, so internal research keys (claim, doc_id, from_file, grounding_score) would ship.
- MF-v3-C: the leak scanner doesn't catch plain "collection" or "derived", and 12 seed rows carry collector-album names like "The U.S. Nickel Collection" in name/series.

**Count:** v3 was attempt 3 of 10. Under Eric's 4-try rule, v4 is AG's last try before someone else takes over.

**Files:** INBOX\ARGON_REVIEW_NET-747_CATALOG-BROWSE_v3.md (14:32), RADIO NET copy plus GEMINI38_REVIEW_NET-747_CATALOG-BROWSE_v3_2026-11-03.md. BATON/ACK NET-754 moved to PROCESSED.

**Turn:** GB CoS, to score v3 or send AG the v4 fix-only baton. Then Argon, CoS 95+, SAG, and Eric's typed YES. Locks unchanged: main 9f04550a, live site untouched.
