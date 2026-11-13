# Eric Beta Test Issue Tracker (31 Oct 2026)

Total 39 | Open 39 | Not in any plan 1 | Repeated 10 | Founder confirmed 0

Status counts: {'Fixed on p7-gate, FT PASS': 14, 'Unverified': 14, 'Not in any plan': 1, 'Fixed but FT FAIL': 2, 'In plan (R2.7)': 7, 'In plan (R2.8)': 1}

|ID|Dates reported|Eric's words|Screen / area|Screenshot|Plan / ticket|Status|Last evidence|Next step|
|---|---|---|---|---|---|---|---|---|
|B26-1|26 Oct; 27 Oct AM|Missed the $9.95 shipping and handling... unable to add the fee|Review Hub fee (truck icon)|26OCT SS 1; 27OCT SS 3|NET-565; Plan v3 I-04b; NET-631|Fixed on p7-gate, FT PASS|FT_RESULT_NET631 PASS (Fee $9.95); NET647 FT said fee field not seen|Re-check fee in Eric's real account in R2.8 audit|
|B26-2|26 Oct|Main screen had no date, but when I clicked Edit the date was there|Review Hub card date|26OCT SS 1|NET-565|Unverified|FAILFIX_EXECUTE_P7_GATE_ERIC_23RH_SAVE_FEE_DATE (no FT result found)|Add to R2.8 FT checklist|
|B26-3|26 Oct|Unable to save|Edit Coin > Save|26OCT SS 3|NET-565|Unverified|No FT result for NET-565; NET647 FT #9 Save error on Set Location, fixed in R2.6 FT #4|Add Edit-Save to R2.8 FT checklist|
|B26-4|26 Oct|Morgan would only accept image files (not the PDF invoice)|Morgan AI chat attachments|none|none|Not in any plan|26 OCT docx only|Decide: let Morgan accept PDF invoices; add to R2.8 or UX backlog|
|B26-5|26 Oct; 27 Oct AM; 27 Oct PM; 29 Oct|Two ways to add by Cert, 2 ways by photo... Very confusing! / Mint Set vs Upload Files vs Upload a list?|Add Coins screen|26OCT SS 4; 27OCT SS 1; 29OCT slides 3-4|NET-585; Plan v3 I-01|Unverified|FT_RESULT_NET627 did not test I-01|Put I-01 on R2.8 FT checklist with a founder walk-through|
|B26-6|26 Oct; 27 Oct AM; 29 Oct|1 or 2 more clicks than it needed to be / clicked Upload Files, which I didn't need to|Invoice upload flow|26OCT SS 4-6; 29OCT slide 4|Plan v3 I-02; NET-647|Unverified|No FT click-count check found|Count clicks in R2.8 FT|
|B26-7|26 Oct|Wish I could enter the storage location right from this screen|Review Queue|26OCT SS 6|NET-585|Unverified|NET-585 execute file only; no FT|Add to R2.8 FT checklist|
|B26-8|26 Oct; 29 Oct|Had to scroll down (again) to get to next step|Bulk Import / Review Queue|26OCT SS 5-6; 29OCT slides 6, 9, 12|NET-647 #3-5|Fixed on p7-gate, FT PASS|FT_RESULT_NET647 #3, #4, #5 PASS|Founder retest|
|B27-1|27 Oct AM|July 4th Privy eligible... I don't know if we need that|Trump $1 roll row|27OCT SS 3|Plan v3 I-04a|Unverified|Not on any FT checklist|Add to R2.8 FT|
|B27-2|27 Oct AM|Added it via Edit, which then automatically saved it to my collection|Edit in Review Hub|27OCT SS 3|Plan v3 I-04c|Fixed on p7-gate, FT PASS|FT_RESULT_NET627 I-04c PASS|Founder retest|
|B27-3|27 Oct AM|Hitting Select All appeared to initiate a Delete|Review Hub|27OCT SS 4|Plan v3 I-05|Fixed on p7-gate, FT PASS|FT_RESULT_NET627 I-05 PASS|Founder retest|
|B27-4|27 Oct AM|Commit Selected... hard to read... does it delete or add?|Review Hub button|27OCT SS 4|Plan v3 I-06|Fixed on p7-gate, FT PASS|FT_RESULT_NET627 I-06 PASS|Founder retest|
|B27-5 (+E2, E4a, FT R2.6 #1)|27 Oct AM; 27 Oct PM; 31 Oct|None of the 3 had images... or valuations / STILL no images, no valuations. NOT GOOD / placeholders; Valuation Pending|My Collection cards + Review thumbnails|27OCT SS 5; 1351 SS 3; 31 Oct E2/E4|Plan v3 I-07/PM-01; R2.7 Q2, E2, E4a|Fixed but FT FAIL|FT_RESULT_NET631 PASS on grokbot, then FT_RESULT_NET673_R2.6 FAIL (gold $ placeholders); E2/E4 still in Eric's account|R2.7 fix + FT PASS in Eric's real account|
|B27-6 (+E4b)|27 Oct AM; 31 Oct|American Innovation had Unspecified for grade|Collection card grade|27OCT SS 5; 31 Oct E4|Plan v3 I-08; R2.7 E4b|In plan (R2.7)|Never FT tested; still wrong 31 Oct|R2.7 FT in Eric's account|
|B27-7|27 Oct AM|No rhyme or reason to how coins were sorted|My Collection|27OCT SS 5|Plan v3 I-09|Unverified|Not on any FT checklist|Add to R2.8|
|B27-8|27 Oct AM|I thought we did away with Google Images button?|Coin Inspector|27OCT SS 6|Plan v3 I-10|Fixed on p7-gate, FT PASS|FT_RESULT_NET627 P1 Google Images PASS|Founder retest|
|B27-9|27 Oct AM|Generate AI Report Now opened a state picker for estate tax... move to Estate Planning|My Collection CTA|27OCT SS 7|Plan v3 I-11|Unverified|FT_RESULT_NET627 AI Report CTA SKIP|Add to R2.8|
|B27-10|27 Oct AM|Replace Generate AI Report Now with something that will fill images and values|My Collection CTA|27OCT SS 5, SS 7|Plan v3 I-12|Unverified|FT_RESULT_NET627 SKIP|Add to R2.8|
|B27-11|27 Oct AM; 27 Oct PM|Impossible to read due to text/background colors... I prefer gold and black|Table view, card details|27OCT SS 7, 8, 10; 1351 SS 6-7|Plan v3 I-13; PM-06|Fixed on p7-gate, FT PASS|FT_RESULT_NET631 cream contrast PASS; NET647 PASS (gold/black preference not checked)|Founder retest; confirm gold/black|
|B27-12|27 Oct AM|Financials, Provenance, AI Insights... should also be present in Card view|Card view detail|27OCT SS 8|Plan v3 I-14|Unverified|Not on any FT checklist|Add to R2.8|
|B27-13|27 Oct AM|AI Insights had large gaps and/or unreadable text|Table view AI Insights|27OCT SS 9|Plan v3 I-15|Unverified|Not on any FT checklist|Add to R2.8|
|B27-14|27 Oct AM|Legislation Matched was blank|Table view|27OCT SS 10|Plan v3 I-16|Unverified|Not on any FT checklist|Add to R2.8|
|B27PM-1|27 Oct PM|No duplicates flagged|Review Hub duplicate check|1351 SS 1|NET-616 PM-02|Fixed on p7-gate, FT PASS|FT_RESULT_NET631 dup amber PASS; NET647 FT unconfirmed|Re-confirm in R2.8 FT|
|B27PM-2|27 Oct PM|Can't tell if I have two 2026 Uncirculated Coin Sets|My Collection cards + detail|1351 SS 3-4|NET-616 PM-04|Unverified|FT_RESULT_NET627 two-SKU check SKIP|Add to R2.8|
|B27PM-3|27 Oct PM|Set I just uploaded did not have 250th Anniversary under Theme/Subject|Search results|1351 SS 5|NET-616 PM-05|Fixed on p7-gate, FT PASS|FT_RESULT_NET627 SAG2 theme stamped|Founder retest|
|B27PM-4|27 Oct PM|Could not make the pop-up bigger... Lincoln quarter cut off|Card detail pop-up|1351 SS 6|NET-616 PM-06|Fixed on p7-gate, FT PASS|FT_RESULT_NET631 20-coin wrap PASS (pop-up resize not tested)|Check pop-up resize in R2.8|
|B29-1|27 Oct eve; 29 Oct|Upload an Invoice does nothing when clicked|Add Coins|29OCT slide 3|FOUNDER_NOTES_NET631; NET-647|Fixed on p7-gate, FT PASS|FT_RESULT_NET647 #1 PASS; NET673 #6 PASS|Founder retest|
|B29-2|27 Oct eve; 29 Oct|Only the bottom inch of the page scrolled / drop zone ~5% of screen|Add Coins / Folder-Drop|29OCT slides 5-6|FOUNDER_NOTES_NET631; NET-647|Fixed on p7-gate, FT PASS|FT_RESULT_NET647 #2, #3 PASS|Founder retest|
|B29-3|29 Oct|Search by Store/Dealer Name... remove it|Bulk Import|29OCT slide 7|NET-647 #7|Fixed on p7-gate, FT PASS|FT_RESULT_NET647 #7 PASS|Founder retest|
|B29-4|29 Oct|Having 2 links/buttons to the paper trail is pointless clutter|Review card|29OCT slide 13|NET-647 #8|Unverified|FT_RESULT_NET647 #8 UNCONFIRMED|Add to R2.8 FT|
|B29-5|29 Oct|These both do the same thing, so delete the top one that just says Storage|Review card|29OCT slide 14|NET-647 #9|Fixed on p7-gate, FT PASS|NET647 #9 FAIL then FT_RESULT_NET673 #4 PASS|Founder retest|
|B29-6 (+FT R2.6 #3)|29 Oct; 31 Oct|Should we put an each here? / 2-coin sets show $169.00 and $64.97 each|Review card price|29OCT slide 16; shots_net673|NET-647 #6; R2.7 Q1|Fixed but FT FAIL|FT_RESULT_NET673_R2.6: roll $2.44 PASS, 2-coin sets FAIL|R2.7 fix + FT|
|E1|31 Oct|Peace and Morgan share the same eagle photo|Eric's collection cards|31 Oct (Eric report)|R2.7 E1|In plan (R2.7)|FAILFIX_PLAN_NET-647_R2.7|Review cycle, then FT in Eric's account|
|E3|31 Oct|Unc Set card shows packaging|Eric's collection card|31 Oct|R2.7 E3/Q4|In plan (R2.7)|FAILFIX_PLAN_NET-647_R2.7|Review cycle, then FT in Eric's account|
|E5|31 Oct|Titles are truncated|Eric's collection cards|31 Oct|R2.7 E5|In plan (R2.7)|FAILFIX_PLAN_NET-647_R2.7|Review cycle, then FT in Eric's account|
|E6|31 Oct|2026 dimes show a 2025 Roosevelt image in the Inspector|Coin Inspector|31 Oct|R2.7 E6 (NET-681C)|In plan (R2.7)|FAILFIX_PLAN_NET-647_R2.7 section E6 + ACK NET-681C|Review cycle, then FT in Eric's account|
|E7|31 Oct|2026-W Silver Eagle Reverse tab shows a 2023 Walking Liberty|Coin Inspector|31 Oct|R2.7 E7 (NET-681C addendum)|In plan (R2.7)|FAILFIX_PLAN_NET-647_R2.7 section E7|Review cycle, then FT in Eric's account|
|FT-2|31 Oct|Only 9 of 11 cards show|Review Queue (FT, grokbot)|shots_net673 06b|R2.7 Q3|In plan (R2.7)|FT_RESULT_NET673_R2.6 FAIL|R2.7 FT|
|E8|31 Oct|Get my account 100% right|Whole account|31 Oct|R2.8 (NET-681D)|In plan (R2.8)|ACK NET-681D|Write R2.8, full review cycle|
