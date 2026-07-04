
from numista_scraper.storage import db
import time

print("[Cleanup] Removing incorrect PCGS #7130 from non-coin records...")

col_ref = db.collection("definitive_reference")
# Find all records with PCGS #7130
docs = col_ref.where("pcgs_no", "==", "7130").stream()

cleaned_count = 0
for doc in docs:
    data = doc.to_dict()
    category = data.get("category", "").lower()
    variety = data.get("variety", "").lower()
    
    # If it's a banknote or doesn't mention Morgan/Dollar, it's likely wrong
    if "banknote" in category or "note" in category or ("morgan" not in variety and "dollar" not in variety):
        print(f"  Cleaning {doc.id} ({category})")
        col_ref.document(doc.id).update({
            "pcgs_no": None,
            "population_total": None,
            "price_guide": None
        })
        cleaned_count += 1

print(f"Done. Cleaned {cleaned_count} records.")
