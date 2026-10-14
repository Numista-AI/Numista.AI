# UX GATE – P7 Add-Coins Flow V4 (dev commit 65711b71)
UX Designer | 14 Oct 2026, ~5:30 PM ET | Repo: Numista-AI/Numista.AI (local clone on EDS_Laptop, branch dev)

## Verdict: **FAIL** (for 60+ phone users)
The code fixes are good and the cert option is now on the first screen. But on a phone, three of the four paths have tap targets or text too small for 60+ users, and the photo button never opens the camera. Until those are fixed, someone who uses an iPhone reasonably well still can't do this without help.

## What I reviewed and how
- **Code only, NOT rendered.** No test URL exists yet (NET-107 is still open), and running the Flutter app here would need its backend and sign-in. Sizes below come from the code values (px = Flutter logical px = iPhone points).
- Files at 65711b71: `numista_mobile/lib/screens/add_coins_hub.dart` (Add screen, cert tab, slab photo-read, verify link, confirm/save) and `program_manager_screen.dart` (checklist "+" add another copy).
- Checked against: the 6 Oct top-5 fixes (`mockups/fix2-text-size`, `fix5-add-coin`), the Morgan-first v2 plan (`05-slab-cert`, `04-confirm-card`), and Eric's bar (48–56px taps, 18px+ text, plain words, one main action, minimalist, slab label beats AI, nothing saved without OK).
- No sign-in, no data touched.

## What passes
- "Add by Cert # (PCGS / NGC / CAC)" is the **first** card on the Add screen. It's easy to find. ✅
- Nothing is saved without the user's OK. NGC/CAC go to a confirm card with a "Confirm & Add to My Collection" button, and a duplicate cert asks before adding. ✅
- Slab label beats AI: the photo-read only fills the cert #, then the user taps Look Up. No AI guess replaces the label. ✅
- The NGC link format is right (`.../certlookup/8321797-003/67/`). ✅

## Findings by path

### 1. Cert tab
- **Findability: good** from the top card. But the card just flips open an 8-tab strip ("Upload Files, AI Photo ID, Manual Entry, Cert Lookup, Add by SKU, Roll/Jar/Batch, World & Specialty, Mint Set") **under** the 4 cards, header and tip banner. On an 844px-tall iPhone the cert form gets roughly the bottom third of the screen. The 6 Oct fix #5 removed exactly this 8-tab layout.
- **Phone use: poor.** Help text is 11–14px grey (#94A3B8, low contrast), e.g. "GRADER", "8-digit → PCGS…", "Cloudflare-passed from browser context". The cert field, camera icon and "Look Up" are squeezed into one row on a 390px screen. The keyboard is text, not numbers. Jargon includes "Grader", "Auto-detects grader", "PCGS Bearer Token", "no public cert API", and "Advanced Options (PCGS Token & Bulk Import)".
- On the NGC/CAC card, labels are 11px caps and fields are 14px. It shows 2 bordered buttons in purple/sky colors (not the single deep blue).

### 2. Slab photo-read
- **Findability: poor.** It's a 46×50px grey camera icon with no words. Its only label is a tooltip, and tooltips don't show on a phone tap.
- **Phone use: blocker.** It uses `ImageSource.gallery` only, so tapping it opens the photo library, **not the camera**. A collector holding a slab expects to take a picture. Results show as a 3-second toast ("Cert # … detected — tap Look Up"), which is too fast to read, and the user then has to find Look Up.

### 3. NGC verify link
- **Findability: OK.** It's a full-width button on the NGC card.
- **Phone use: below bar.** It has 12px text and ~10px padding, so it's about 40px tall (under 48). It says "Verify Cert on NGC.com →", but the site is ngccoin.com. If tapped **before** Grade is typed, the link is `.../certlookup/<cert>//` with an empty grade. The card also asks the user to type name/year/grade/denomination by hand when the slab already shows them.

### 4. "+ add another copy" on filled checklist slots
- **Findability: blocker.** It's a 12px "+" icon with 3px padding, so the **tap target is ~18×18px** (bar is 48). It has no words, only a tooltip. It sits next to a 12px green "owned" chip. Users 60+ won't see it or hit it.
- **Phone use: confusing.** It always opens the **cert tab** with nothing filled in. For a raw coin (e.g. a 2nd Washington dollar from a P/D/S set) that's the wrong path, and the coin name from the slot is lost.

## Fix list (ranked by impact)
1. **BLOCKER – Add another copy:** make it a labeled button, "+ Add another", at least 48px tall. Open a confirm card pre-filled with that slot's coin (name, year, mint), with "Has a slab? Enter cert #" as a secondary choice. Don't drop the user into an empty cert tab.
2. **BLOCKER – Slab photo:** make it a labeled button, "📷 Take a photo of the slab label", at least 56px tall, that opens the **camera** (with "choose from photos" as a second choice). Show the result on screen (not a 3-second toast): "We read cert # 1234567 (NGC). Is that right? [Yes, look it up]".
3. **BLOCKER – Text size and contrast on the cert flow:** all labels, hints and help text at least 18px and dark (#334155 or darker, no #94A3B8 for words). Field text at least 18px, fields at least 56px tall. Use a number keypad for the cert # (allow the "-" for NGC).
4. **BLOCKER – One screen, one action:** when "Add by Cert #" is tapped, show the cert form as its own full screen (back arrow, no 8-tab strip, no 4 cards above it), as in Morgan-first `05-slab-cert`. Keep one deep-blue primary button per step ("Look up" → "Save to my collection").
5. **NICE-TO-HAVE – NGC verify:** make it at least 48px tall with 18px text. Call it "Check this slab on NGC's website" and disable it (or drop the grade from the link) until Grade is filled. Fix "NGC.com" → "ngccoin.com".
6. **NICE-TO-HAVE – Plain words:** remove or hide "Grader", "Auto-detects…", "API", "Cloudflare", "Bearer Token", "Advanced Options". Say "Who graded it? PCGS / NGC / CAC / Not sure", using chips at least 48px tall. Remove the "Explore 7 Ways…" 11px banner.
7. **NICE-TO-HAVE – Less typing for NGC/CAC:** have the slab photo also read name/year/grade from the label and pre-fill them for the user to OK (label wins, user confirms).
8. **NICE-TO-HAVE – Style:** one accent color (deep blue) instead of purple/sky/pink/green per grader, and no italic 900-weight header, to match the Morgan-first v2 style.

## To re-gate
Fix 1–4, then rerun this review **rendered** on the NET-107 test URL with the grokbot test account at 390×844 and 1024 wide, alongside the Field Tester walkthrough.
