"""Patch Sacagawea & Native American Dollars coin data per Wikipedia corrections."""
import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')

master_path = os.path.join(os.path.dirname(__file__), "master_coin_programs.json")
with open(master_path, "r", encoding="utf-8") as f:
    master = json.load(f)

CORRECTIONS = {
    "2010": "Great Tree of Peace",
    "2013": "Treaty with the Lenape",
    "2021": "American Indians in the U.S. Military",
    "2024": "Indian Citizenship Act of 1924 (100th Anniversary)",
    "2025": "Mary Kawena Pukui",
    "2026": "Oneidas at Valley Forge / Polly Cooper",
}

for prog in master:
    if prog.get("name") == "Sacagawea & Native American Dollars":
        fixed = 0
        for coin in prog.get("coins", []):
            yr = str(coin.get("year", ""))
            if yr in CORRECTIONS:
                old = coin.get("name", "")
                coin["name"] = CORRECTIONS[yr]
                print(f"  {yr}: '{old}' -> '{coin['name']}'")
                fixed += 1
        print(f"Fixed {fixed} Sacagawea entries.")
        break

with open(master_path, "w", encoding="utf-8") as f:
    json.dump(master, f, indent=2, ensure_ascii=False)
print("Saved.")
