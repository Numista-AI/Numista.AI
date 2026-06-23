#!/usr/bin/env python3
"""Inspect jseaman_image_gaps.csv structure and status values."""
import csv
import json
import os
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GAP_CSV = os.path.join(SCRIPT_DIR, "jseaman_image_gaps.csv")

status_counts = Counter()
blank_denom_program = []
all_statuses = set()

with open(GAP_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    cols = reader.fieldnames
    print(f"Columns: {cols}")
    print()
    total = 0
    for row in reader:
        total += 1
        status = row.get("status", "").strip()
        status_counts[status] += 1
        all_statuses.add(status)
        denom = row.get("denomination", "").strip()
        program = row.get("program", "").strip()
        if not denom and not program:
            blank_denom_program.append(row)

print(f"Total rows: {total}")
print(f"Status distribution:")
for s, cnt in status_counts.most_common():
    print(f"  {cnt:>6}  '{s}'")
print()
print(f"Blank denom+program: {len(blank_denom_program)}")
print()

# Show first few rows
with open(GAP_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 5:
            break
        print(f"Row {i+1}: {dict(row)}")
