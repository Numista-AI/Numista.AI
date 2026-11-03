# GB CoS score: AG_PLAN_NET-747_CATALOG-BROWSE_v4 (attempt 4 of 10)
Scored 2026-11-03 3:45 PM ET. **95/100 PASS**, with binding carry-forward conditions for EXECUTE.

## Checked against the files (not on Argon's word)
- The plan is 383 lines. The master has 3,202 rows. 1,070 records have the source 'collection photo, owner removed'; v4 rewrites them to 'Numista.Ai reference photo' and keeps primary_image.file.
- The Firestore YES guard is at lines 52 and 247. The deploy goes to the p7v12 preview only (lines 47-48).
- Correction to Argon: 'seed_images' appears once, at line 129. It's the internal fold_source value, which gets stripped, so it's not a public path.

## Deductions (-5)
- N-v4-1 (-3): the museum whitelist at lines 33 and 164 has si.edu/collection/ (singular), but the master has 173 si.edu/collections/ hits. As written, the build fails closed. That's safe, but it would block the build.
- Missing whitelist patterns (-1): numismatics.org/collection/, the Gallica 'coin collection; public domain' credit, NNC 'Lilly Collection' prose, 'collectors still hunt' and 'a-collectors-guide'.
- N-v4-3 (-1): images must mount at assets/catalog/reference_images/, never seed_images.

## Binding conditions for EXECUTE
1. Fix the whitelist (collection/ and collections/, plus the patterns above). Each whitelist entry must be an exact URL-prefix or exact-phrase match, never a bare-word exemption.
2. Use the reference_images path only.
3. The scanner still fails on any other hit. Do the 100-record hand check, at least 50 of them from the seed.
4. p7v12 preview only. Firestore and rules changes need Eric's separate YES.

Next: SAG review, then Eric's typed YES. Docs only.
