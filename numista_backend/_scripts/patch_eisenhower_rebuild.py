"""
Rebuild Eisenhower Dollar data with accurate per-year, multi-variety structure.
Production years: 1971-1974, 1976 (Bicentennial), 1977-1978 (no 1975).

S-mint coins are collector editions only:
  - 1971-74, 76: 40% silver (business-strike brown/blue packs) + silver proof
  - 1972, 77, 78: copper-nickel proof only
"""
import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')

master_path = os.path.join(os.path.dirname(__file__), "master_coin_programs.json")
with open(master_path, "r", encoding="utf-8") as f:
    master = json.load(f)

IKE_DATA = [
    {
        "id": "ike_1971", "year": "1971", "name": "Eisenhower Dollar",
        "varieties": [
            {"id": "P",       "label": "P"},
            {"id": "D",       "label": "D"},
            {"id": "S-SILVER","label": "S Silver"},
            {"id": "S-PROOF", "label": "S Proof"},
        ]
    },
    {
        "id": "ike_1972", "year": "1972", "name": "Eisenhower Dollar",
        "varieties": [
            {"id": "P",       "label": "P"},
            {"id": "D",       "label": "D"},
            {"id": "S-PROOF", "label": "S Proof"},
        ]
    },
    {
        "id": "ike_1973", "year": "1973", "name": "Eisenhower Dollar",
        "varieties": [
            {"id": "P",       "label": "P"},
            {"id": "D",       "label": "D"},
            {"id": "S-SILVER","label": "S Silver"},
            {"id": "S-PROOF", "label": "S Proof"},
        ]
    },
    {
        "id": "ike_1974", "year": "1974", "name": "Eisenhower Dollar",
        "varieties": [
            {"id": "P",       "label": "P"},
            {"id": "D",       "label": "D"},
            {"id": "S-SILVER","label": "S Silver"},
            {"id": "S-PROOF", "label": "S Proof"},
        ]
    },
    {
        # 1976 Bicentennial — dated 1776-1976. Both P & D have Type 1 (thick) and Type 2 (thin) lettering.
        "id": "ike_1976", "year": "1976", "name": "Bicentennial Dollar (1776-1976)",
        "varieties": [
            {"id": "P-T1",    "label": "P Type 1"},
            {"id": "P-T2",    "label": "P Type 2"},
            {"id": "D-T1",    "label": "D Type 1"},
            {"id": "D-T2",    "label": "D Type 2"},
            {"id": "S-SILVER","label": "S Silver"},
            {"id": "S-PROOF", "label": "S Silver Proof"},
        ]
    },
    {
        "id": "ike_1977", "year": "1977", "name": "Eisenhower Dollar",
        "varieties": [
            {"id": "P",       "label": "P"},
            {"id": "D",       "label": "D"},
            {"id": "S-PROOF", "label": "S Proof"},
        ]
    },
    {
        "id": "ike_1978", "year": "1978", "name": "Eisenhower Dollar",
        "varieties": [
            {"id": "P",       "label": "P"},
            {"id": "D",       "label": "D"},
            {"id": "S-PROOF", "label": "S Proof"},
        ]
    },
]

for prog in master:
    if prog.get("name") == "Eisenhower Dollars":
        old_count = len(prog.get("coins", []))
        prog["coins"] = IKE_DATA
        print(f"Rebuilt Eisenhower: {old_count} stub coins -> {len(IKE_DATA)} proper entries")
        print("Varieties per year:")
        for c in IKE_DATA:
            vlist = ", ".join(v["label"] for v in c["varieties"])
            print(f"  {c['year']}: {vlist}")
        break

with open(master_path, "w", encoding="utf-8") as f:
    json.dump(master, f, indent=2, ensure_ascii=False)
print("\nSaved.")
