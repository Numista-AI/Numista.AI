# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
#!/usr/bin/env python3
import os
import sys
import re
import argparse
import firebase_admin
from firebase_admin import credentials, firestore

# Mappings for standardizing theme names to official US Mint titles
PRESIDENTIAL_DOLLARS_MAP = {
    "washington": "George Washington",
    "george washington": "George Washington",
    "john adams": "John Adams",
    "adams, john": "John Adams",
    "jefferson": "Thomas Jefferson",
    "thomas jefferson": "Thomas Jefferson",
    "madison": "James Madison",
    "james madison": "James Madison",
    "monroe": "James Monroe",
    "james monroe": "James Monroe",
    "john quincy adams": "John Quincy Adams",
    "john q adams": "John Quincy Adams",
    "john q. adams": "John Quincy Adams",
    "adams, john q": "John Quincy Adams",
    "adams, john q.": "John Quincy Adams",
    "jackson": "Andrew Jackson",
    "andrew jackson": "Andrew Jackson",
    "van buren": "Martin Van Buren",
    "martin van buren": "Martin Van Buren",
    "william henry harrison": "William Henry Harrison",
    "william h harrison": "William Henry Harrison",
    "william h. harrison": "William Henry Harrison",
    "harrison, william henry": "William Henry Harrison",
    "tyler": "John Tyler",
    "john tyler": "John Tyler",
    "polk": "James K. Polk",
    "james polk": "James K. Polk",
    "james k polk": "James K. Polk",
    "james k. polk": "James K. Polk",
    "taylor": "Zachary Taylor",
    "zachary taylor": "Zachary Taylor",
    "fillmore": "Millard Fillmore",
    "millard fillmore": "Millard Fillmore",
    "pierce": "Franklin Pierce",
    "franklin pierce": "Franklin Pierce",
    "buchanan": "James Buchanan",
    "james buchanan": "James Buchanan",
    "lincoln": "Abraham Lincoln",
    "abraham lincoln": "Abraham Lincoln",
    "andrew johnson": "Andrew Johnson",
    "grant": "Ulysses S. Grant",
    "ulysses grant": "Ulysses S. Grant",
    "ulysses s grant": "Ulysses S. Grant",
    "ulysses s. grant": "Ulysses S. Grant",
    "hayes": "Rutherford B. Hayes",
    "rutherford hayes": "Rutherford B. Hayes",
    "rutherford b hayes": "Rutherford B. Hayes",
    "rutherford b. hayes": "Rutherford B. Hayes",
    "garfield": "James A. Garfield",
    "james garfield": "James A. Garfield",
    "james a garfield": "James A. Garfield",
    "james a. garfield": "James A. Garfield",
    "james garﬁeld": "James A. Garfield",
    "james garﬁ eld": "James A. Garfield",
    "arthur": "Chester A. Arthur",
    "chester arthur": "Chester A. Arthur",
    "chester a arthur": "Chester A. Arthur",
    "chester a. arthur": "Chester A. Arthur",
    "grover cleveland": "Grover Cleveland (First Term)",
    "grover cleveland (term 1)": "Grover Cleveland (First Term)",
    "grover cleveland (term 2)": "Grover Cleveland (Second Term)",
    "grover cleveland (1st term)": "Grover Cleveland (First Term)",
    "grover cleveland (2nd term)": "Grover Cleveland (Second Term)",
    "cleveland (term 1)": "Grover Cleveland (First Term)",
    "cleveland (term 2)": "Grover Cleveland (Second Term)",
    "cleveland (1st term)": "Grover Cleveland (First Term)",
    "cleveland (2nd term)": "Grover Cleveland (Second Term)",
    "cleveland first term": "Grover Cleveland (First Term)",
    "cleveland second term": "Grover Cleveland (Second Term)",
    "benjamin harrison": "Benjamin Harrison",
    "mckinley": "William McKinley",
    "william mckinley": "William McKinley",
    "theodore roosevelt": "Theodore Roosevelt",
    "t roosevelt": "Theodore Roosevelt",
    "teddy roosevelt": "Theodore Roosevelt",
    "taft": "William Howard Taft",
    "william howard taft": "William Howard Taft",
    "william h taft": "William Howard Taft",
    "william h. taft": "William Howard Taft",
    "wilson": "Woodrow Wilson",
    "woodrow wilson": "Woodrow Wilson",
    "harding": "Warren G. Harding",
    "warren harding": "Warren G. Harding",
    "warren g harding": "Warren G. Harding",
    "warren g. harding": "Warren G. Harding",
    "coolidge": "Calvin Coolidge",
    "calvin coolidge": "Calvin Coolidge",
    "hoover": "Herbert Hoover",
    "herbert hoover": "Herbert Hoover",
    "franklin d roosevelt": "Franklin D. Roosevelt",
    "franklin d. roosevelt": "Franklin D. Roosevelt",
    "franklin d, roosevelt": "Franklin D. Roosevelt",
    "fdr": "Franklin D. Roosevelt",
    "truman": "Harry S. Truman",
    "harry truman": "Harry S. Truman",
    "harry s truman": "Harry S. Truman",
    "harry s. truman": "Harry S. Truman",
    "eisenhower": "Dwight D. Eisenhower",
    "dwight eisenhower": "Dwight D. Eisenhower",
    "dwight d eisenhower": "Dwight D. Eisenhower",
    "dwight d. eisenhower": "Dwight D. Eisenhower",
    "ike": "Dwight D. Eisenhower",
    "kennedy": "John F. Kennedy",
    "john kennedy": "John F. Kennedy",
    "john f kennedy": "John F. Kennedy",
    "john f. kennedy": "John F. Kennedy",
    "jfk": "John F. Kennedy",
    "lyndon johnson": "Lyndon B. Johnson",
    "lyndon b johnson": "Lyndon B. Johnson",
    "lyndon b. johnson": "Lyndon B. Johnson",
    "lbj": "Lyndon B. Johnson",
    "nixon": "Richard M. Nixon",
    "richard nixon": "Richard M. Nixon",
    "richard m nixon": "Richard M. Nixon",
    "richard m. nixon": "Richard M. Nixon",
    "ford": "Gerald R. Ford",
    "gerald ford": "Gerald R. Ford",
    "gerald r ford": "Gerald R. Ford",
    "gerald r. ford": "Gerald R. Ford",
    "reagan": "Ronald Reagan",
    "ronald reagan": "Ronald Reagan",
    "george h w bush": "George H.W. Bush",
    "george h.w. bush": "George H.W. Bush",
    "george hw bush": "George H.W. Bush",
    "george h. w. bush": "George H.W. Bush",
    "bush, george h.w.": "George H.W. Bush",
}

# The release year grid for Presidential $1 Coins
PRESIDENT_YEARS = {
    "George Washington": "2007",
    "John Adams": "2007",
    "Thomas Jefferson": "2007",
    "James Madison": "2007",
    "James Monroe": "2008",
    "John Quincy Adams": "2008",
    "Andrew Jackson": "2008",
    "Martin Van Buren": "2008",
    "William Henry Harrison": "2009",
    "John Tyler": "2009",
    "James K. Polk": "2009",
    "Zachary Taylor": "2009",
    "Millard Fillmore": "2010",
    "Franklin Pierce": "2010",
    "James Buchanan": "2010",
    "Abraham Lincoln": "2010",
    "Andrew Johnson": "2011",
    "Ulysses S. Grant": "2011",
    "Rutherford B. Hayes": "2011",
    "James A. Garfield": "2011",
    "Chester A. Arthur": "2012",
    "Grover Cleveland (First Term)": "2012",
    "Grover Cleveland (Second Term)": "2012",
    "Benjamin Harrison": "2012",
    "William McKinley": "2013",
    "Theodore Roosevelt": "2013",
    "William Howard Taft": "2013",
    "Woodrow Wilson": "2013",
    "Warren G. Harding": "2014",
    "Calvin Coolidge": "2014",
    "Herbert Hoover": "2014",
    "Franklin D. Roosevelt": "2014",
    "Harry S. Truman": "2015",
    "Dwight D. Eisenhower": "2015",
    "John F. Kennedy": "2015",
    "Lyndon B. Johnson": "2015",
    "Richard M. Nixon": "2016",
    "Gerald R. Ford": "2016",
    "Ronald Reagan": "2016",
    "George H.W. Bush": "2020",
}

def clean(v) -> str:
    if v is None: return ""
    if isinstance(v, float): return str(int(v))
    s = str(v).strip()
    return "" if s.lower() in ("nan", "none", "null", "") else s

def slugify(value: str) -> str:
    value = str(value).strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")

def make_coin_id(data: dict) -> str:
    parts = []
    for field, max_len in [("Year", 6), ("Mint Mark", 4), ("Denomination", 20),
                            ("Theme/Subject", 40), ("Variety", 20)]:
        val = clean(data.get(field))
        if val:
            parts.append(slugify(val)[:max_len].rstrip("-"))
    if not parts:
        series = clean(data.get("Program/Series"))
        if series:
            parts.append(slugify(series)[:30].rstrip("-"))
    return "_".join(parts) if parts else "unknown"

def normalize_theme(theme_raw: str, year_raw: str) -> str:
    cleaned = str(theme_raw).strip().lower()
    y_str = str(year_raw).strip()
    
    # 1. Exact mapping matches
    if cleaned in PRESIDENTIAL_DOLLARS_MAP:
        return PRESIDENTIAL_DOLLARS_MAP[cleaned]
        
    # 2. Ambiguity resolution based on year/text
    if cleaned in ("adams", "adams, john"):
        if y_str == "2008":
            return "John Quincy Adams"
        else:
            return "John Adams"
            
    if cleaned == "harrison":
        if y_str == "2012":
            return "Benjamin Harrison"
        else:
            return "William Henry Harrison"
            
    if cleaned == "johnson":
        if y_str == "2011":
            return "Andrew Johnson"
        else:
            return "Lyndon B. Johnson"
            
    if cleaned == "roosevelt":
        if y_str == "2013":
            return "Theodore Roosevelt"
        elif y_str == "2014":
            return "Franklin D. Roosevelt"
            
    if cleaned in ("cleveland", "grover cleveland"):
        if "1893" in cleaned or "term 2" in cleaned or "second" in cleaned or "2nd" in cleaned or y_str == "1893":
            return "Grover Cleveland (Second Term)"
        else:
            return "Grover Cleveland (First Term)"
            
    # If it contains any parts of Grover Cleveland
    if "cleveland" in cleaned:
        if "1893" in cleaned or "term 2" in cleaned or "second" in cleaned or "2nd" in cleaned or "93-97" in cleaned:
            return "Grover Cleveland (Second Term)"
        elif "1885" in cleaned or "term 1" in cleaned or "first" in cleaned or "1st" in cleaned or "85-89" in cleaned:
            return "Grover Cleveland (First Term)"
        else:
            return "Grover Cleveland (First Term)"

    # Fallback to title case of original if no match
    return str(theme_raw).strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Perform writes to Firestore")
    parser.add_argument("--user", help="Limit to specific user email")
    args = parser.parse_args()

    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    KEY_PATH = os.path.join(backend_dir, "serviceAccountKey.json.json")

    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    users_ref = db.collection('users')
    if args.user:
        users = [users_ref.document(args.user).get()]
    else:
        users = list(users_ref.stream())

    print(f"Users to scan: {[u.id for u in users]}")
    total_scanned = 0
    total_updated = 0

    for user in users:
        email = user.id
        print(f"\nScanning user: {email}")
        coins_ref = db.collection('users').document(email).collection('coins')
        coins = list(coins_ref.stream())
        
        # Build set of all current coin_id values to prevent collisions when regenerating
        existing_coin_ids = set()
        for doc in coins:
            cid = doc.to_dict().get("coin_id")
            if cid:
                existing_coin_ids.add(cid)

        # Batch writes
        batch = db.batch()
        batch_count = 0

        for doc in coins:
            total_scanned += 1
            d = doc.to_dict()
            prog = d.get('Program/Series', '') or ''
            theme = d.get('Theme/Subject', '') or ''
            denom = d.get('Denomination', '') or ''
            year = d.get('Year', '') or ''
            
            # Refined matching logic: only target actual Presidential $1 Coins
            is_presidential = False
            
            # Normalise denom for comparison
            denom_cleaned = str(denom).lower().replace(' ', '').replace('$', '')
            
            # Explicitly exclude quarters, half dollars, nickels, cents
            is_excluded_denom = any(ex in denom_cleaned for ex in ["half", "50c", "quarter", "25c", "cent", "penny", "1c", "nickel", "5c"])
            
            if not is_excluded_denom:
                # 1. If program contains "presidential"
                if "presidential" in str(prog).lower():
                    is_presidential = True
                # 2. Or if denom represents $1 and theme resolves to a presidential coin that matches the release year grid
                elif denom_cleaned in ("dollar", "1", "1.00"):
                    std_theme_temp = normalize_theme(theme, year)
                    if std_theme_temp in PRESIDENT_YEARS:
                        expected_year = PRESIDENT_YEARS[std_theme_temp]
                        if str(year).strip() == expected_year:
                            is_presidential = True
            
            if not is_presidential:
                continue
                
            # Perform standardization
            std_theme = normalize_theme(theme, year)
            std_prog = "Presidential $1 Coin Program"
            
            # Check if fields changed
            changed = False
            updates = {}
            
            if theme != std_theme:
                updates['Theme/Subject'] = std_theme
                changed = True
            if prog != std_prog:
                updates['Program/Series'] = std_prog
                changed = True
                
            if changed:
                # Regenerate coin_id
                temp_dict = {**d, **updates}
                new_base_id = make_coin_id(temp_dict)
                
                # Ensure uniqueness
                final_cid = new_base_id
                suffix = 1
                current_cid = d.get("coin_id")
                while final_cid in existing_coin_ids and final_cid != current_cid:
                    suffix += 1
                    final_cid = f"{new_base_id}_{suffix}"
                
                if current_cid != final_cid:
                    updates['coin_id'] = final_cid
                    if current_cid in existing_coin_ids:
                        existing_coin_ids.remove(current_cid)
                    existing_coin_ids.add(final_cid)
                
                print(f"  [UPDATE] ID: {doc.id[:8]}... | Year: {year} | Program: '{prog}' -> '{std_prog}' | Theme: '{theme}' -> '{std_theme}' | coin_id: '{current_cid}' -> '{final_cid}'")
                
                if args.write:
                    # Use set(merge=True) to avoid ValueError: Invalid char in element with leading alpha: Theme/Subject
                    batch.set(doc.reference, updates, merge=True)
                    batch_count += 1
                    if batch_count >= 400:
                        batch.commit()
                        batch = db.batch()
                        batch_count = 0
                total_updated += 1

        if args.write and batch_count > 0:
            batch.commit()

    print(f"\nDone. Scanned: {total_scanned} coins. Updated/To Update: {total_updated}")

if __name__ == "__main__":
    main()
