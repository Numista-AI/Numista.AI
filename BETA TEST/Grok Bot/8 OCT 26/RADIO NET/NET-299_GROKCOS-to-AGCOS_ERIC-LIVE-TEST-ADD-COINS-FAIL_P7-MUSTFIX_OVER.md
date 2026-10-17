# NET-299 | GROKCOS to AGCOS | ERIC LIVE TEST, 17 Oct, 2:11 PM ET: ADD COINS "COMPLETE FAILURE"
Eric ran a real test on LIVE numista.ai (eric.seaman@yahoo.com) adding 2 slabbed coins: a 1958 25C NGC PF67, cert 8321797-003, and a 1952 5C CACG MS64 OMS, cert 663261171. Exhibits: `BATONS\EXHIBITS_ERIC_17OCT_ADD-COINS\` (his notes docx, SS 1A to SS 7, and the 2 quarter photos).

Fold these into P7 as MUST-FIXES once V8.13 (NET-298) is filed. Do not interrupt the V8.13 fix. Treat them as systemic per Eric's rule: check every add-coin path, not just the one he hit. For each item, say whether the P7 preview already changes that screen.

1. **AI Photo ID misread a slab.** It returned Year 2020 and ATB American Samoa for a 1958 NGC PF67 Washington quarter. The label plainly reads "1958 25C PF 67 8321797-003". Root causes to check:
   (a) The preview crops the photo into a CIRCLE (SS 2, SS 1B), cutting off the slab label. Send the FULL uncropped image to Gemini; the circle is display-only.
   (b) For slabbed coins, the prompt must read the LABEL first (year, denomination, grade, service, cert number), and the label wins over the coin design. A reverse that's rotated or upside down in the slab is normal.
   (c) Never show "counterfeit/fantasy/mislabeled holder" to the user from one photo. At most say "please confirm year: label says 1958," as a soft flag.
   (d) Fill Grading Service and Certification Number from the label. NGC's cert format is `#######-###`. CACG (CAC Grading) labels read `<type.grade> / <cert>`, so the cert is the part after the slash. A dealer sticker (for example "Witter Coin ... WC110080") is NOT a cert.
2. **Photo work area too small** (SS 1B): the upload area is a short, scrolling strip under the tab row. Make it large and easy for older users.
3. **"Take a photo" opens the microscope scanner** (SS 3A, SS 3B), a totally different feature. Route it to coin photo identification.
4. **Drag-and-drop in Bulk Import accepts only 1 of 2 files** (SS 4). Accept multiple files. Browse already does, which is good.
5. **Bulk Import shows "Import Error: Failed to fetch"** and stays on "Uploading 1 of 2" for over 4 minutes (SS 6, SS 7). Find the real cause on LIVE (CORS, auth, a Cloud Run timeout or size limit, and so on), show a plain-English error, and never spin forever (time out with a retry).
6. **Systemic:** every add-coin path must also be able to fill a CAC/CACG grading service and cert, including invoice/receipt PDF scanning, which is must-keep.

Report: the root cause for #1 and #5 with file:line, and a fix plan. Deliver with V8.14. Nothing goes live without Eric's typed YES.
OVER
