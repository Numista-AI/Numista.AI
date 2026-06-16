import json
data = json.load(open('master_coin_programs.json', encoding='utf-8'))
for p in data:
    print(f"{p['name']} | {p.get('category','?')} | {len(p.get('coins',[]))} coins")
