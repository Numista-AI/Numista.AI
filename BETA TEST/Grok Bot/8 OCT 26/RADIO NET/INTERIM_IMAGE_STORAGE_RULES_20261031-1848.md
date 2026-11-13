# INTERIM IMAGE AND CATALOG STORAGE RULES (in force until PLAN_IMAGE_CONSOLIDATION is approved by Eric)
FROM: GB CoS  TO: ALL bots and AG  (20261031-1848)

SCOPE: Coins and bank notes first. Medals are in scope at lower priority (Eric 6:47 PM 31 Oct).
1. READ ONLY in GCS (studio-9101802118-8c9a8) and Firestore. No uploads, renames, moves or deletes, and no Firestore writes.
2. STAGE new images on the box at /workspace/image-intake/<your-bot>/<subject>/ (laptop: COIN IMAGES\_INTAKE\<bot>\). Never in the live buckets.
3. EVERY staged batch needs a MANIFEST.csv with these columns: proposed_name ({year}_{program}_{subject}_{side}[_mintcode][_variant], lowercase), side (obverse/reverse/edge/privy/ogp), unique_side (y/n), category (coin/note/medal), source_page_url, image_url, license, credit, accession_or_sku, resolution, sha256, added_by, date, status=PROPOSAL.
4. SOURCE ORDER: Mint/BEP/Treasury, then museums (Smithsonian NNC, ANS), then public domain, then verified user uploads. Only use what we're licensed to use. Search gs://numista-reference-library and Eric's photos first.
5. Send the manifest path to GB CoS. Nothing goes live until the intake plan passes the Review Cycle and Eric gives his YES. Once it does, staged batches move in with no re-work.
6. Keep everything out of V3Tees. No secrets in files or chat.

7. EXEMPTION (GB CoS 6:52 PM): Items in a plan Eric has already YES'd (e.g. NET-647 R2.6's 7 uploads to 2026_products) may proceed as written, no-clobber only and with no deletes.
