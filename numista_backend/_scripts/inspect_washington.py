# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('master_coin_programs.json', encoding='utf-8'))
p = [x for x in data if x['name'] == 'WASHINGTON QUARTERS'][0]
coins = p.get('coins', [])
print(f"Total coins: {len(coins)}")
for c in coins:
    print(c.get('year','?'), '-', c.get('name',''))
