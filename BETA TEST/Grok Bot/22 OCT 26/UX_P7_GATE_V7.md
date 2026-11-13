# UX re-gate P7 V8.18.15 (22 Oct 2026). Verdict: FAIL (close, 2 items left)
The banner reads v8.18.15. 0 console errors. Nothing saved.
1. Neutral heading, and the real cert 53652580 looks up correctly ("Coin Found!", PR70DCAM 2025-W): PASS
2. No camera: friendly message plus "Upload a photo instead": PASS
3. Tap targets: FAIL. All the items from the last gate are fixed at 48 or more. Still under 48:
   - NGC card "Check this slab on ngccoin.com" and Cancel: 40
   - Sidebar "Send Beta Feedback" and "Sign Out": 32
   - Photo page "Take Photo" and "Upload" links: 40
   Text is about 18-20px (estimated; borderline PASS).
4. NGC not-found card: PASS with a wording note. It names the cert and grader and says what to try, but it mixes "not found" with "not supported". Suggested wording: "We can't look up NGC numbers automatically yet. Snap the label or type the details below."
5. Label photo: FAIL.
   - The clear PCGS photo can't be read.
   - The CACG front spins for over 2 minutes, then times out.
   - The CACG rear can't be read.
   - The app never fills in details and never says the cert is on the back (only the static tip does).
6. Front-photo confirm card: mint shows "W (West Point)", Cancel is there, nothing is cut off: PASS
Screenshots: box /workspace/numista-ux/p7gate23/
