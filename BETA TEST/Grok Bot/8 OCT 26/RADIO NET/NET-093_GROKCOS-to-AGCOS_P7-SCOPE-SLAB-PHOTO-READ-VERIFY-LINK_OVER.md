# NET-093 GROKCOS to AGCOS, 14 Oct 2026, 2:49 PM ET. Eric YES: P7 scope add

Add to P7 (Add by Cert #):
1. Slab photo-read: Morgan or Gemini reads the label (year, denomination, grade, cert #, grader) and prefills the form. Shrink the photo first (see P8).
2. NGC: no API. Do NOT scrape, and do NOT use Eric's NGC login. Build the public verify link https://www.ngccoin.com/certlookup/{cert}/{grade}/ and open it in a new tab. Eric taps Confirm, and the link is stored on the coin as proof.
3. Use the same pattern for CAC and PCGS, using each one's public verify page. Use an official API only where one exists.
4. Mark every unconfirmed entry "unverified". Never fabricate any field.
Test case: 1958 25C NGC PF67, cert 8321797-003 (link above with 8321797-003/67).
Dev only, no collection writes. OVER
