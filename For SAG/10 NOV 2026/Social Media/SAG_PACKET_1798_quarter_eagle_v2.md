# SAG PACKET v2: 1798 $2.50 quarter eagle (Capped Bust Right / Heraldic Eagle), AI replica, push toward 99
Status: PROPOSAL for the X thread planned Thu 12 Nov 2026, noon ET. Every image carries the baked label "AI rendering, not a real coin photo". Nothing is queued or posted.
Decision rule (Eric, 10 Nov): if v2 scores BELOW v1 on this first test, keep v1. The v1 files are untouched.
Approval line after the gates pass: "YES - 1798 $2.50 quarter eagle - Thu 12 Nov noon"

Attach: 1798_quarter_eagle_13_stars_obverse_AI_v2.jpg, 1798_quarter_eagle_heraldic_reverse_AI_v2.jpg
Optional: 1798_quarter_eagle_COMPARISON_v1_vs_v2_AI.jpg (v1 and v2 side by side, plus a real 1798 reverse photo used as a layout reference only), 1798_quarter_eagle_ZOOM_v1_vs_v2_AI.jpg (close-ups of the changed areas)

## Prior v1 scores
- Social self-check: obverse 96, reverse 96
- CoS eye check: obverse 96 PASS, reverse 95 PASS
- Eric SAG: obverse 96 PASS, reverse 95 PASS

## v2 self-scores (strict, compared with v1)
- Obverse 97 (v1 96). Same correct content. The star spacing is now slightly irregular, like hand-punched dies, and it follows the angular spread of two real 1798 coins.
- Reverse 97 (v1 95-96). The 13 stars now follow the pattern on real 1798 reverses. The clouds are less blotchy. The S of PLURIBUS no longer touches the eagle's neck.

## Real 1798 photos found (LAYOUT REFERENCE ONLY: rights belong to the auction houses; never post)
- Stack's Bowers photo via Coinstrail, 1798 $2.50 Wide Date (BD-2), obverse and reverse: https://static.coinstrail.com/coins/800/94c1b8c88790d6e65e329f8f3dcfb569.jpeg and https://static.coinstrail.com/coins/800/cc2bc60052ffe0cbaf4e7a3e652c09a7.jpeg (page: https://coinstrail.com/catalog/us/gold-quarter-eagles/draped-bust-2-50-dollars/699c04a30155923cbe447a53)
- Heritage photo via USA Coin Book, 1798 $2.50 (variety not stated, small image): https://i.usacoinbook.com/us-coins/600/1798-turban-head-gold-quarter-eagle.jpg
- No public-domain 1798 photo was found. Wikimedia Commons has none. The Smithsonian Open Access API shows two 1798 $2.50 records (nmah_1062368, nmah_1062371) but no images. The ANS search returned no 1798 $2.50. archive.org had nothing usable.

## Changes from v1 (targeted code edits only; no side was regenerated)
OBVERSE
- Re-placed all 13 stars from the same base image. There are still exactly 6 on the left and 7 on the right. Each star's angle varies by about ±1.6°, its radius by about ±3 px, its size by about ±4%, and its rotation by up to about ±7°.
- The left arc now spans about 143-213° and the right arc about -37 to 41°, matching the spread on the real 1798 photos. The top-left star now sits a little closer to the L.
- LIBERTY, the 1798 Close Date (8 clear of the bust), the bust and the label are unchanged.
REVERSE
- The 13 v1 stars were removed by cloning a clean field patch. 13 new stars, slightly smaller (about 0.8x, closer to the real coin's proportions), were placed in the pattern both real 1798 reverses show: 6 in an outer arc hugging the clouds, 5 in an inner row above the head, and 2 low (one left of the beak, one right of the head). Each has slight jitter.
- Clouds: inside a cloud-only mask, an edge-preserving smoothing pass reduced the mottled dark blotches and crackle. The outline and segment shapes were kept, and the edges were re-sharpened.
- S of PLURIBUS: the ribbon now extends about 14 px past the S and ends in a fold line before the eagle's neck, so the S sits fully on the ribbon with a clear gap.
- Arrows (viewer's left), olive branch (viewer's right) with 4 berries, shield, legends, no denomination and the label are all unchanged.

## Known risks
- The reverse star layout comes from photos of what appears to be the BD-2 (5-berry) reverse. The BD-1 (4-berry) reverse may place its stars differently. No BD-1 reverse photo was reachable.
- The clouds are smoother but still not the polished, separate oval segments seen on the real coin. A light crackle texture remains in the field.
- The ribbon fold is synthetic. At very high zoom there is a faint seam inside the added ribbon strip.
- The bust, eagle feathers and shield are AI-styled and not matched to a specific die. The shield stripe count is interpretive.
- The berries are code-added (carried over from v1).
- Do not state the star point count in the post.

## Paste to SAG
You are an independent US numismatics fact checker. These are AI renderings meant to show a 1798 $2.50 quarter eagle, Capped Bust Right, Heraldic Eagle reverse, Close Date variety (BD-1). This is v2. The v1 scores were obverse 96 and reverse 95. Score each image 0-100 (95 or higher passes), say whether v2 is better or worse than v1, and list exactly what would be needed to reach 99. Check:
OBVERSE
- Liberty facing right, wearing a large soft cap
- LIBERTY above, date 1798 below
- Exactly 13 stars, 6 on the left and 7 on the right (unique to 1798)
- Close Date: the 8 sits clear of the bust
- Star spacing looks plausibly hand-punched (slightly irregular), not machine-even
REVERSE
- Heraldic Eagle with a shield on its breast
- Arrows in the claw on the viewer's left, olive branch on the viewer's right (transposed from the Great Seal)
- Olive branch with exactly 4 berries (BD-1)
- Exactly 13 stars below an arc of clouds, in a plausible 1798 layout
- Clouds smooth and not blotchy
- E PLURIBUS UNUM on the ribbon, with the S of PLURIBUS clear of the eagle's neck; UNITED STATES OF AMERICA around the rim
- No denomination on the coin
For each side, give the score, PASS or REVISE, whether it is better or worse than v1, and the specific fixes needed for 99.
