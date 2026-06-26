import csv

with open('numista_marketing_breakdown.csv', encoding='utf-8') as f:
    c = list(csv.DictReader(f))
    print(f'Total: {len(c)}')
    print(f'Obverse: {sum(1 for r in c if r["Has Obverse Image"] == "Yes")}')
    print(f'Reverse: {sum(1 for r in c if r["Has Reverse Image"] == "Yes")}')
    print(f'Audited: {sum(1 for r in c if r["AI_Audited_Status"] == "Yes")}')
    print(f'History: {sum(1 for r in c if r["Has History"] == "Yes")}')
