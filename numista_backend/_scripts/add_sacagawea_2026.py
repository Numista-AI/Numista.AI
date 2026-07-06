# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""Add the 2026 Sacagawea coin (Oneidas at Valley Forge / Polly Cooper)."""
import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')

master_path = os.path.join(os.path.dirname(__file__), "master_coin_programs.json")
with open(master_path, "r", encoding="utf-8") as f:
    master = json.load(f)

for prog in master:
    if prog.get("name") == "Sacagawea & Native American Dollars":
        coins = prog.get("coins", [])
        years = {c.get("year") for c in coins}
        if "2026" not in years:
            coins.append({
                "year": "2026",
                "name": "Oneidas at Valley Forge / Polly Cooper",
                "varieties": [
                    {"id": "P", "label": "P"},
                    {"id": "D", "label": "D"},
                    {"id": "S-PROOF", "label": "S Proof"}
                ]
            })
            prog["coins"] = coins
            print("Added 2026 Oneidas / Polly Cooper")
        else:
            print("2026 already present")
        break

with open(master_path, "w", encoding="utf-8") as f:
    json.dump(master, f, indent=2, ensure_ascii=False)
print("Saved.")
