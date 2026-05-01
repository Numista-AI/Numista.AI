"""
Re-runs the mint mark type/description tagging with all em-dashes
replaced by ASCII hyphens, which are safe for PDF Helvetica font.
"""
import sys, json, re, os
sys.stdout.reconfigure(encoding='utf-8')

master_path = os.path.join(os.path.dirname(__file__), "master_coin_programs.json")
with open(master_path, "r", encoding="utf-8") as f:
    master = json.load(f)

def safe(text):
    """Replace typographic characters that PDF Helvetica cannot render."""
    if not text:
        return text
    return (text
        .replace('\u2014', ' - ')   # em-dash
        .replace('\u2013', '-')     # en-dash
        .replace('\u2018', "'")     # left single quote
        .replace('\u2019', "'")     # right single quote
        .replace('\u201C', '"')     # left double quote
        .replace('\u201D', '"')     # right double quote
        .replace('\u2026', '...')   # ellipsis
    )

DESCRIPTIONS = {
    "EDGE": safe(
        "EDGE-LETTERED SERIES: The mint mark is on the EDGE (side) of the coin. "
        "Look along the rim. You will see a small letter (P, D, or S) between the "
        "date and design lettering."
    ),
    "OBVERSE_PORTRAIT": safe(
        "Look on the FRONT (obverse) of the coin. The mint mark is a small letter "
        "near the portrait - typically to the left or right of the subject's "
        "neckline or lower bust."
    ),
    "OBVERSE_DATE": safe(
        "Look on the FRONT (obverse) of the coin. The mint mark is a small letter "
        "just to the right of or just below the date."
    ),
    "REVERSE_EAGLE": safe(
        "Look on the BACK (reverse) of the coin. The mint mark is a small letter "
        "to the left of the eagle's tail feathers or lower wing."
    ),
    "REVERSE_LOWER": safe(
        "Look on the BACK (reverse) of the coin. The mint mark is a small letter "
        "in the lower portion of the reverse design."
    ),
    "REVERSE_UPPER": safe(
        "Look on the BACK (reverse) of the coin. The mint mark is a small letter "
        "in the upper portion of the reverse, above the main design element."
    ),
    "NONE": safe(
        "No mint mark exists on coins of this type/era. All coins of this "
        "series were struck at the Philadelphia Mint (no mark required)."
    ),
}

TAGS = {
    "American Innovation $1 Coin Program": ("EDGE", None),
    "Presidential Dollars":                ("EDGE", None),
    "Sacagawea & Native American Dollars": ("MIXED", safe(
        "MIXED ERA: Sacagawea Dollars (2000-2008) have the mint mark on the "
        "REVERSE (back), below the eagle's tail. From 2009 onward (Native American "
        "series), the coin switched to edge-lettering - look along the EDGE (side) "
        "of the coin for the mint mark.")),
    "American Women Quarters":                            ("OBVERSE_PORTRAIT", None),
    "50 State Quarters":                                  ("OBVERSE_PORTRAIT", None),
    "D.C. & U.S. Territories Quarters":                   ("OBVERSE_PORTRAIT", None),
    "America the Beautiful Quarters (National Parks)":    ("OBVERSE_PORTRAIT", None),
    "Washington Quarters (Classic)": ("MIXED", safe(
        "MIXED ERA: On Washington Quarters struck before 1968, the mint mark is "
        "on the REVERSE (back) to the right of the eagle's tail. On quarters from "
        "1968 onward, the mint mark moved to the OBVERSE (front), to the right of "
        "Washington's ponytail above the date.")),
    "Barber Quarters": ("REVERSE_EAGLE", None),
    "Kennedy Half Dollars": ("OBVERSE_PORTRAIT", safe(
        "Look on the FRONT (obverse) of the coin. The mint mark is a small letter "
        "to the left of Kennedy's neckline. Note: 1965-1967 Kennedy halves "
        "have NO mint mark (all struck at Philadelphia during the transition).")),
    "Liberty Walking Half Dollars": ("MIXED", safe(
        "MIXED ERA: On 1916 and early 1917 Walking Liberty halves, the mint mark "
        "is on the OBVERSE (front), at the lower left near the date. From late 1917 "
        "onward, the mint mark moved to the REVERSE (back) at the lower left, "
        "below the pine branch.")),
    "Franklin Half Dollars": ("REVERSE_UPPER", safe(
        "Look on the BACK (reverse) of the coin. The mint mark is a small letter "
        "above the Liberty Bell, to the right of the crack.")),
    "Barber Half Dollars": ("REVERSE_EAGLE", None),
    "Eisenhower Dollars": ("OBVERSE_PORTRAIT", safe(
        "Look on the FRONT (obverse) of the coin. The mint mark is a small letter "
        "above the date, to the left of Eisenhower's neckline. "
        "NOTE: Philadelphia business-strike coins have NO mint mark. "
        "Denver (D) struck all clad business-strike coins. "
        "San Francisco (S) issued collector editions only (silver clad and proof).")),
    "Susan B. Anthony Dollars": ("OBVERSE_PORTRAIT", safe(
        "Look on the FRONT (obverse) of the coin. The mint mark is a small letter "
        "to the left of Susan B. Anthony's portrait, near the rim.")),
    "Morgan Dollars":  ("REVERSE_EAGLE", None),
    "Peace Dollars":   ("REVERSE_EAGLE", safe(
        "Look on the BACK (reverse) of the coin. The mint mark is a small letter "
        "to the left of the eagle's wing, below 'ONE DOLLAR'.")),
    "American Silver Eagles": ("OBVERSE_PORTRAIT", safe(
        "Look on the FRONT (obverse) of the coin. The mint mark location varies "
        "by year and type - typically near the lower left of the Walking Liberty "
        "design. Proof and burnished coins struck at West Point (W) or San "
        "Francisco (S) are marked; bullion strikes have no mint mark (Philadelphia).")),
    "Roosevelt Dimes": ("MIXED", safe(
        "MIXED ERA: On Roosevelt Dimes from 1946-1964 (silver), the mint mark is "
        "on the REVERSE (back), at the lower left between the torch and the letter "
        "'E' in 'E PLURIBUS UNUM'. From 1968 onward, the mint mark moved to the "
        "OBVERSE (front), above the date to the left.")),
    "Mercury Dimes":  ("REVERSE_LOWER", safe(
        "Look on the BACK (reverse) of the coin. The mint mark is a small letter "
        "to the left of the fasces (bundle of rods), at the lower left.")),
    "Barber Dimes":   ("REVERSE_LOWER", None),
    "Jefferson Nickels": ("MIXED", safe(
        "MIXED ERA: Pre-1942 Jefferson Nickels have the mint mark on the REVERSE "
        "(back), to the right of Monticello. The 1942-1945 War Nickels (35% silver) "
        "have a large mint mark above the dome of Monticello on the reverse. From "
        "1968 onward, the mint mark moved to the OBVERSE (front), to the right of "
        "Jefferson's portrait.")),
    "Buffalo Nickels": ("REVERSE_LOWER", safe(
        "Look on the BACK (reverse) of the coin. The mint mark is a small letter "
        "below the words 'FIVE CENTS', on the ground line beneath the buffalo.")),
    "Liberty Head (V) Nickels": ("REVERSE_LOWER", safe(
        "Look on the BACK (reverse) of the coin. The mint mark is a small letter "
        "to the left of 'CENTS', in the lower left of the reverse.")),
    "Lincoln Wheat Pennies": ("OBVERSE_DATE", safe(
        "Look on the FRONT (obverse) of the coin. The mint mark is a small letter "
        "just below the date, to the right. Philadelphia cents have NO mint mark.")),
    "Lincoln Memorial Cents": ("OBVERSE_DATE", safe(
        "Look on the FRONT (obverse) of the coin. The mint mark is a small letter "
        "just below the date, to the right. Philadelphia cents before 1980 "
        "have NO mint mark.")),
    "Lincoln Bicentennial Cents (2009)": ("OBVERSE_DATE", safe(
        "Look on the FRONT (obverse) of the coin. The mint mark is a small letter "
        "just below the date, to the right.")),
    "Lincoln Shield Cents": ("OBVERSE_DATE", safe(
        "Look on the FRONT (obverse) of the coin. The mint mark is a small letter "
        "just below the date, to the right.")),
    "Lincoln Cents": ("OBVERSE_DATE", None),
    "Flying Eagle & Indian Head Cents": ("REVERSE_LOWER", safe(
        "Look on the BACK (reverse) of the coin. The mint mark (S for San Francisco) "
        "is a small letter at the bottom of the reverse, below the wreath. "
        "Philadelphia cents have NO mint mark.")),
    "U.S. Proof Sets": ("REVERSE_LOWER", safe(
        "All U.S. Proof Sets are struck at the San Francisco Mint (S). "
        "The mint mark appears on each individual coin in its standard location "
        "for that denomination and era.")),
    "2026 U.S. Circulating Coins": ("OBVERSE_DATE", safe(
        "Look on the FRONT (obverse) of each coin. The mint mark (P for "
        "Philadelphia, D for Denver) is a small letter near the date.")),
}

tagged = 0
unmatched = []
for prog in master:
    name = prog.get("name", "")
    if name in TAGS:
        mtype, custom_desc = TAGS[name]
        prog["mint_mark_type"] = mtype
        prog["mint_mark_description"] = custom_desc if custom_desc else DESCRIPTIONS[mtype]
        tagged += 1
    elif prog.get("mint_mark_type"):
        # Already tagged but not in our map — sanitize existing descriptions
        if prog.get("mint_mark_description"):
            prog["mint_mark_description"] = safe(prog["mint_mark_description"])
    else:
        unmatched.append(name)

print(f"Tagged: {tagged} programs")
if unmatched:
    print("Unmatched:")
    for n in unmatched: print(f"  - {n!r}")

with open(master_path, "w", encoding="utf-8") as f:
    json.dump(master, f, indent=2, ensure_ascii=False)
print("Saved master_coin_programs.json")
