# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('master_coin_programs.json', encoding='utf-8'))
targets = ['kennedy', 'roosevelt', 'jefferson', 'lincoln', 'morgan', 'peace', 'buffalo', 'barber', 'mercury', 'eisenhower']
for p in data:
    name = p.get('name','').lower()
    if any(t in name for t in targets):
        coins = p.get('coins', [])
        print(f"{p['name']} | {len(coins)} coins | first: {coins[0].get('year','?') if coins else 'none'} | varieties sample: {coins[0].get('varieties','?') if coins else 'none'}")
