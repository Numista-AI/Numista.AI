"""
Batch patch Lincoln Cents, Morgan Dollars, Buffalo Nickels, Mercury Dimes.
These are classic series — the existing per-date/mintmark coin structure
from the Littleton extraction is CORRECT. We just need to:
- Fix Lincoln Cents empty varieties and clean up names
- Normalize Morgan, Buffalo, Mercury variety arrays
- Update program metadata
"""
import sys, json, re, os
sys.stdout.reconfigure(encoding='utf-8')

master_path = os.path.join(os.path.dirname(__file__), "master_coin_programs.json")
with open(master_path, "r", encoding="utf-8") as f:
    master = json.load(f)


def normalize_variety(v):
    """Convert a string variety into a {id, label} dict."""
    if isinstance(v, dict):
        return v
    s = str(v).strip()
    if not s or s in ('', 'P', 'No Mint Mark'):
        return {"id": "P", "label": "P"}
    return {"id": re.sub(r'[^A-Za-z0-9\-]', '', s.replace(' ', '-')), "label": s}


def fix_lincoln_variety(year_str, coin_name):
    """Return the correct variety list for a Lincoln cent based on year and name."""
    yr = int(year_str) if str(year_str).isdigit() else 0
    name_up = coin_name.upper()

    # Determine mint from name
    if '-S VDB' in name_up or 'S VDB' in name_up:
        return [{"id": "S-VDB", "label": "S-VDB"}]
    elif 'VDB' in name_up:
        return [{"id": "P-VDB", "label": "P-VDB"}]
    elif name_up.endswith('-S') or ' S' in name_up[-3:]:
        return [{"id": "S", "label": "S"}]
    elif name_up.endswith('-D') or ' D' in name_up[-3:]:
        return [{"id": "D", "label": "D"}]
    elif 'PROOF' in name_up:
        return [{"id": "S-PROOF", "label": "S Proof"}]
    else:
        # Philadelphia (no mint mark pre-1980)
        return [{"id": "P", "label": "P"}]


for prog in master:
    prog_name = prog.get("name", "")

    # ── LINCOLN CENTS ─────────────────────────────────────────────────────────
    if prog_name == "LINCOLN CENTS":
        prog["name"] = "Lincoln Cents"
        prog["years"] = "1909-2025"
        prog["category"] = "Cent"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P (no mark pre-1909-S era) | Denver - D | San Francisco - S |"
        for coin in prog.get("coins", []):
            yr = str(coin.get("year", ""))
            name = str(coin.get("name", coin.get("year", "")))
            # Fix the coin display name — use the Littleton name which is already good (e.g. "1909-S VDB")
            coin["name"] = name
            # Fix empty varieties
            raw_v = coin.get("varieties", [])
            if not raw_v or (len(raw_v) == 1 and raw_v[0] == ''):
                coin["varieties"] = fix_lincoln_variety(yr, name)
            else:
                coin["varieties"] = [normalize_variety(v) for v in raw_v]
        print(f"Patched: {prog['name']} — {len(prog['coins'])} coins")

    # ── MORGAN DOLLARS ────────────────────────────────────────────────────────
    elif prog_name == "MORGAN DOLLAR":
        prog["name"] = "Morgan Dollars"
        prog["years"] = "1878-1921 (+ 2021, 2023)"
        prog["category"] = "Dollar"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P | Denver - D | New Orleans - O | San Francisco - S | Carson City - CC | West Point - W |"
        for coin in prog.get("coins", []):
            raw_v = coin.get("varieties", [])
            if not raw_v or raw_v == ['']:
                # Infer from coin name
                name = str(coin.get("name", ""))
                if '-CC' in name:   coin["varieties"] = [{"id":"CC","label":"CC"}]
                elif '-S' in name:  coin["varieties"] = [{"id":"S","label":"S"}]
                elif '-O' in name:  coin["varieties"] = [{"id":"O","label":"O"}]
                elif '-D' in name:  coin["varieties"] = [{"id":"D","label":"D"}]
                elif '-W' in name:  coin["varieties"] = [{"id":"W","label":"W"}]
                else:               coin["varieties"] = [{"id":"P","label":"P"}]
            else:
                coin["varieties"] = [normalize_variety(v) for v in raw_v]
        print(f"Patched: {prog['name']} — {len(prog['coins'])} coins")

    # ── BUFFALO NICKELS ───────────────────────────────────────────────────────
    elif prog_name == "BUFFALO NICKELS":
        prog["name"] = "Buffalo Nickels"
        prog["years"] = "1913-1938"
        prog["category"] = "Nickel"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P (no mark) | Denver - D | San Francisco - S |"
        for coin in prog.get("coins", []):
            raw_v = coin.get("varieties", [])
            if not raw_v or raw_v == ['']:
                name = str(coin.get("name", ""))
                if '-D' in name:   coin["varieties"] = [{"id":"D","label":"D"}]
                elif '-S' in name: coin["varieties"] = [{"id":"S","label":"S"}]
                else:              coin["varieties"] = [{"id":"P","label":"P"}]
            else:
                coin["varieties"] = [normalize_variety(v) for v in raw_v]
        print(f"Patched: {prog['name']} — {len(prog['coins'])} coins")

    # ── MERCURY DIMES ─────────────────────────────────────────────────────────
    elif prog_name == "MERCURY DIMES":
        prog["name"] = "Mercury Dimes"
        prog["years"] = "1916-1945"
        prog["category"] = "Dime"
        prog["mint_mark_locations"] = "Mint Mark Key: | Philadelphia - P (no mark) | Denver - D | San Francisco - S |"
        for coin in prog.get("coins", []):
            raw_v = coin.get("varieties", [])
            name = str(coin.get("name", ""))
            if not raw_v or raw_v == [''] or (len(raw_v) == 1 and raw_v[0] == ''):
                if '-D' in name:   coin["varieties"] = [{"id":"D","label":"D"}]
                elif '-S' in name: coin["varieties"] = [{"id":"S","label":"S"}]
                else:              coin["varieties"] = [{"id":"P","label":"P"}]
            else:
                coin["varieties"] = [normalize_variety(v) for v in raw_v]
        print(f"Patched: {prog['name']} — {len(prog['coins'])} coins")

with open(master_path, "w", encoding="utf-8") as f:
    json.dump(master, f, indent=2, ensure_ascii=False)
print("\nmaster_coin_programs.json saved.")
