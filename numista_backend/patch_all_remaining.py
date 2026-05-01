"""
Final batch patch — all remaining programs:
- Flying Eagle & Indian Head Cents
- Liberty Head (V) Nickels
- Liberty Walking Half Dollars
- Franklin Half Dollars
- Peace Dollars
- Eisenhower Dollars
- Susan B. Anthony Dollars
- American Silver Eagle (bullion)
- Barber Quarters, Dimes, Halves
- U.S. Proof Sets
- 2026 U.S. Circulating Coins
- Littleton Guide (skip / mark as non-checklist)
"""
import sys, json, re, os
sys.stdout.reconfigure(encoding='utf-8')

master_path = os.path.join(os.path.dirname(__file__), "master_coin_programs.json")
with open(master_path, "r", encoding="utf-8") as f:
    master = json.load(f)


def nv(v):
    """Normalize a variety string to {id, label}."""
    if isinstance(v, dict):
        return v
    s = str(v).strip()
    if not s or s == 'No Mint Mark':
        return {"id":"P","label":"P"}
    return {"id": re.sub(r'[^A-Za-z0-9\-\s]','',s).replace(' ','-'), "label": s}


def mint_from_name(name):
    """Infer variety list from a coin name like '1916-D' or '1921-S'."""
    n = str(name).upper()
    if '-CC' in n:   return [{"id":"CC","label":"CC"}]
    if '-O'  in n:   return [{"id":"O","label":"O"}]
    if '-S'  in n:   return [{"id":"S","label":"S"}]
    if '-D'  in n:   return [{"id":"D","label":"D"}]
    if '-W'  in n:   return [{"id":"W","label":"W"}]
    if 'PROOF' in n: return [{"id":"S-PROOF","label":"S Proof"}]
    return [{"id":"P","label":"P"}]


for prog in master:
    name = prog.get("name","")

    # ── Flying Eagle & Indian Head Cents ─────────────────────────────────────
    if name == "Flying Eagle & Indian Head Cents":
        prog["years"] = "1856-1909"
        prog["category"] = "Cent"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P (no mark) | San Francisco - S |"
        for c in prog.get("coins",[]):
            raw = c.get("varieties",[])
            if not raw or raw == ['']:
                c["varieties"] = mint_from_name(c.get("name",""))
            else:
                c["varieties"] = [nv(v) for v in raw]
        print(f"Patched: {name} — {len(prog['coins'])} coins")

    # ── Liberty Head (V) Nickels ──────────────────────────────────────────────
    elif name == "LIBERTY HEAD NICKELS":
        prog["name"] = "Liberty Head (V) Nickels"
        prog["years"] = "1883-1912"
        prog["category"] = "Nickel"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P (no mark) | Denver - D | San Francisco - S |"
        for c in prog.get("coins",[]):
            raw = c.get("varieties",[])
            if not raw or raw == ['']:
                c["varieties"] = mint_from_name(c.get("name",""))
            else:
                c["varieties"] = [nv(v) for v in raw]
        print(f"Patched: Liberty Head (V) Nickels — {len(prog['coins'])} coins")

    # ── Liberty Walking Half Dollars ──────────────────────────────────────────
    elif name == "LIBERTY WALKING HALVES":
        prog["name"] = "Liberty Walking Half Dollars"
        prog["years"] = "1916-1947"
        prog["category"] = "Half Dollar"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P (no mark) | Denver - D | San Francisco - S |"
        for c in prog.get("coins",[]):
            raw = c.get("varieties",[])
            if not raw or raw == [''] or (len(raw)==1 and raw[0] in ('','P')):
                c["varieties"] = mint_from_name(c.get("name",""))
            else:
                c["varieties"] = [nv(v) for v in raw]
        print(f"Patched: Liberty Walking Half Dollars — {len(prog['coins'])} coins")

    # ── Franklin Half Dollars ─────────────────────────────────────────────────
    elif name == "Franklin Half Dollars":
        prog["years"] = "1948-1963"
        prog["category"] = "Half Dollar"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P (no mark) | Denver - D | San Francisco - S |"
        for c in prog.get("coins",[]):
            raw = c.get("varieties",[])
            if not raw or raw == ['']:
                c["varieties"] = mint_from_name(c.get("name",""))
            else:
                c["varieties"] = [nv(v) for v in raw]
        print(f"Patched: {name} — {len(prog['coins'])} coins")

    # ── Peace Dollars ─────────────────────────────────────────────────────────
    elif name == "Peace Dollars":
        prog["years"] = "1921-1935 (+ 2021, 2023)"
        prog["category"] = "Dollar"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P (no mark) | Denver - D | San Francisco - S |"
        for c in prog.get("coins",[]):
            raw = c.get("varieties",[])
            if not raw or (len(raw)==1 and raw[0] in ('','No Mint Mark')):
                c["varieties"] = mint_from_name(c.get("name",""))
            else:
                c["varieties"] = [nv(v) for v in raw]
        print(f"Patched: {name} — {len(prog['coins'])} coins")

    # ── Eisenhower Dollars ────────────────────────────────────────────────────
    elif name == "EISENHOWER DOLLAR":
        prog["name"] = "Eisenhower Dollars"
        prog["years"] = "1971-1978"
        prog["category"] = "Dollar"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |"
        # Eisenhower varieties already encoded in coin names; normalize them
        ike_coins = []
        for c in prog.get("coins",[]):
            raw = c.get("varieties",[])
            # The existing data has year+mintmark as both name AND variety — restructure
            cn = str(c.get("name", c.get("year","")))
            yr_match = re.match(r"^(\d{4})", cn)
            yr = yr_match.group(1) if yr_match else str(c.get("year",""))
            # Determine variety label
            if 'Silver Proof' in cn:
                v = [{"id":"S-SILVER-PROOF","label":"S Silver Proof"}]
            elif 'Silver Clad' in cn or 'Silver' in cn:
                v = [{"id":"S-SILVER","label":"S Silver Clad"}]
            elif '-S' in cn or 'S Proof' in cn:
                v = [{"id":"S-PROOF","label":"S Proof"}]
            elif '-D' in cn:
                v = [{"id":"D","label":"D"}]
            elif '-P' in cn or 'Bicentennial' in cn.title():
                v = [{"id":"P","label":"P"}]
            else:
                v = mint_from_name(cn)
            # Coin name = clean label
            clean_name = "Bicentennial Coinage" if '1976' in cn else "Eisenhower Dollar"
            ike_coins.append({"id":f"ike_{re.sub(r'[^a-z0-9]','_',cn.lower())}","year":yr,"name":clean_name,"varieties":v})
        prog["coins"] = ike_coins
        print(f"Patched: Eisenhower Dollars — {len(ike_coins)} coins")

    # ── Susan B. Anthony Dollars ──────────────────────────────────────────────
    elif name == "Susan B. Anthony Dollars":
        prog["years"] = "1979-1981, 1999"
        prog["category"] = "Dollar"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P | Denver - D | San Francisco - S |"
        # SBA already has excellent variety detail; just normalize
        for c in prog.get("coins",[]):
            raw = c.get("varieties",[])
            c["varieties"] = [nv(v) for v in raw] if raw else mint_from_name(c.get("name",""))
        print(f"Patched: {name} — {len(prog['coins'])} coins")

    # ── American Silver Eagle ─────────────────────────────────────────────────
    elif name == "AMERICAN SILVER EAGLE":
        prog["name"] = "American Silver Eagles"
        prog["years"] = "1986-2024"
        prog["category"] = "Bullion"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P | San Francisco - S | West Point - W |"
        for c in prog.get("coins",[]):
            raw = c.get("varieties",[])
            if not raw or raw == ['']:
                c["varieties"] = mint_from_name(c.get("name",""))
            else:
                c["varieties"] = [nv(v) for v in raw]
        print(f"Patched: American Silver Eagles — {len(prog['coins'])} coins")

    # ── Barber Quarters ───────────────────────────────────────────────────────
    elif name == "BARBER QUARTERS":
        prog["name"] = "Barber Quarters"
        prog["years"] = "1892-1916"
        prog["category"] = "Quarter"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P (no mark) | Denver - D | New Orleans - O | San Francisco - S |"
        for c in prog.get("coins",[]):
            raw = c.get("varieties",[])
            c["varieties"] = [nv(v) for v in raw] if raw else mint_from_name(c.get("name",""))
        print(f"Patched: Barber Quarters — {len(prog['coins'])} coins")

    # ── Barber Dimes ──────────────────────────────────────────────────────────
    elif name == "Barber Dimes":
        prog["years"] = "1892-1916"
        prog["category"] = "Dime"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P (no mark) | New Orleans - O | San Francisco - S |"
        for c in prog.get("coins",[]):
            raw = c.get("varieties",[])
            c["varieties"] = [nv(v) for v in raw] if raw else mint_from_name(c.get("name",""))
        print(f"Patched: {name} — {len(prog['coins'])} coins")

    # ── Barber Half Dollars ───────────────────────────────────────────────────
    elif name == "BARBER HALVES":
        prog["name"] = "Barber Half Dollars"
        prog["years"] = "1892-1915"
        prog["category"] = "Half Dollar"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P (no mark) | New Orleans - O | San Francisco - S |"
        for c in prog.get("coins",[]):
            raw = c.get("varieties",[])
            if not raw or raw == ['']:
                c["varieties"] = mint_from_name(c.get("name",""))
            else:
                c["varieties"] = [nv(v) for v in raw]
        print(f"Patched: Barber Half Dollars — {len(prog['coins'])} coins")

    # ── U.S. Proof Sets ───────────────────────────────────────────────────────
    elif name == "U.S. PROOF SETS":
        prog["name"] = "U.S. Proof Sets"
        prog["years"] = "1936-Present"
        prog["category"] = "Proof Sets"
        prog["mint_mark_locations"] = "All Proof Sets are struck at the San Francisco Mint (S)."
        for c in prog.get("coins",[]):
            raw = c.get("varieties",[])
            c["varieties"] = [nv(v) for v in raw] if raw else [{"id":"S-PROOF","label":"S Proof"}]
        print(f"Patched: U.S. Proof Sets — {len(prog['coins'])} coins")

    # ── 2026 U.S. Circulating Coins ───────────────────────────────────────────
    elif name == "2026 U.S. Circulating Coins":
        prog["years"] = "2026"
        prog["category"] = "Circulating"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P | Denver - D |"
        for c in prog.get("coins",[]):
            raw = c.get("varieties",[])
            if not raw or raw == ['']:
                c["varieties"] = [{"id":"P","label":"P"},{"id":"D","label":"D"}]
            else:
                c["varieties"] = [nv(v) for v in raw]
        print(f"Patched: {name} — {len(prog['coins'])} coins")

    # ── Littleton Guide (skip — not a coin checklist) ─────────────────────────
    elif "Littleton" in name:
        prog["category"] = "Reference"
        prog["_skip_checklist"] = True
        print(f"Marked as Reference (skip): {name}")

with open(master_path, "w", encoding="utf-8") as f:
    json.dump(master, f, indent=2, ensure_ascii=False)
print("\nmaster_coin_programs.json saved.")
