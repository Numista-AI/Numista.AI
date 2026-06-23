#!/usr/bin/env python3
"""Find the 40 unclassified coins with blank denomination AND blank program in the gap CSV."""
import csv
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GAP_CSV = os.path.join(SCRIPT_DIR, "jseaman_image_gaps.csv")
PASS1_LOG = os.path.join(SCRIPT_DIR, "reverse_enrichment_log.json")
PASS2_LOG = os.path.join(SCRIPT_DIR, "reverse_enrichment_pass2_log.json")

with open(PASS1_LOG, encoding="utf-8") as f:
    pass1 = json.load(f)
with open(PASS2_LOG, encoding="utf-8") as f:
    pass2 = json.load(f)

all_done = {r["doc_id"] for r in pass1 if r.get("result") == "success"}
all_done |= {r["doc_id"] for r in pass2 if r.get("result") == "success"}

print(f"Total done (pass1+pass2): {len(all_done)}")

# Find rows in CSV with blank denom AND blank program (truly unclassified)
blank_both = []
all_rows = []
with open(GAP_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        status = row.get("status", "").strip()
        if status not in ("obverse_only", "missing_reverse", ""):
            continue
        doc_id = row.get("doc_id", "").strip()
        denom = row.get("denomination", "").strip()
        program = row.get("program", "").strip()
        all_rows.append(row)
        if not denom and not program:
            blank_both.append({
                "doc_id": doc_id,
                "year": row.get("year", "").strip(),
                "mint_mark": row.get("mint_mark", "").strip(),
                "already_done": doc_id in all_done
            })

print(f"Total gap CSV obverse-only rows: {len(all_rows)}")
print(f"Coins with BLANK denom+program: {len(blank_both)}")
done_count = sum(1 for c in blank_both if c["already_done"])
not_done_count = len(blank_both) - done_count
print(f"  Already done: {done_count}")
print(f"  Still pending: {not_done_count}")
print()

# Show all of them
for c in blank_both:
    status = "DONE" if c["already_done"] else "PENDING"
    print(f"  [{status}] {c['doc_id']}  year={c['year']}  mint={c['mint_mark']}")

# Also show CSV columns
with open(GAP_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    print(f"\nCSV columns: {reader.fieldnames}")
