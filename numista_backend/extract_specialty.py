import csv, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SPECIALTY = {'National Bank Note', 'Obsolete Currency', 'Bank Note',
             'Military Payment Certificate', 'Treasury Note', 'Error Note'}

rows = []
with open('grok_sourcing_list.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        if row['category'] in SPECIALTY:
            rows.append(row)

# Write specialty-only CSV for Grok
out = 'grok_specialty_sourcing.csv'
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

print(f'Specialty types for Grok: {len(rows)}')
print()
cats = {}
for r in rows:
    cats.setdefault(r['category'], []).append(r)

for cat, items in sorted(cats.items()):
    print(f'\n{cat} ({len(items)} types):')
    for item in items:
        tid   = item['type_id']
        denom = item['denomination']
        year  = item['year']
        desc  = item['example_description'][:65]
        print(f'  {tid}  denom={denom:8}  year={year:8}  {desc}')

print(f'\nWritten to: {out}')
