import csv

with open('_scripts/eric_image_gap_report.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# Coins with no year
no_year = [r for r in rows if not r['year']]
print(f"Coins with NO year in Firestore: {len(no_year)}")
for r in no_year:
    print(f"  [{r['program_slug']}] {r['program_series']} | cond: {r['condition'][:40]}")

# Coins with at least one image matched
matched = [r for r in rows if r['obverse_status'] != 'MISSING' or r['reverse_status'] != 'MISSING']
print(f"\nCoins with at least one image: {len(matched)}")
for r in matched:
    print(f"  {r['year']} {r['program_series']} | OBV:{r['obverse_status']} REV:{r['reverse_status']}")

# Morgan Dollars with year data
morgan_w_year = [r for r in rows if 'morgan' in r['program_series'].lower() and r['year']]
print(f"\nMorgan Dollars WITH year data: {len(morgan_w_year)}")
for r in morgan_w_year:
    print(f"  {r['year']} {r['mint_mark']} slug:{r['program_slug']} | OBV:{r['obverse_status']} REV:{r['reverse_status']}")

# What years does the index have for morgan-dollar?
with open('_scripts/image_index_full.csv', encoding='utf-8') as f:
    idx = list(csv.DictReader(f))
morgan_idx = [r for r in idx if r['program'] == 'morgan-dollar']
print(f"\nMorgan Dollar entries in index: {len(morgan_idx)}")
for r in morgan_idx:
    print(f"  {r['doc_key']} -> {r['public_url'][:70]}")
