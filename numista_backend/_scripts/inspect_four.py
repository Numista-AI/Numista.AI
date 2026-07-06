# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('master_coin_programs.json', encoding='utf-8'))
for prog_name in ['LINCOLN CENTS', 'MORGAN DOLLAR', 'BUFFALO NICKELS', 'MERCURY DIMES']:
    p = next((x for x in data if x['name'] == prog_name), None)
    if not p:
        print(f"NOT FOUND: {prog_name}")
        continue
    coins = p.get('coins', [])
    print(f"\n{prog_name} — {len(coins)} coins")
    # Show first 5 and last 3
    for c in coins[:5]:
        print(f"  {c.get('year','?')} | {c.get('name','?')} | {c.get('varieties','?')}")
    print("  ...")
    for c in coins[-3:]:
        print(f"  {c.get('year','?')} | {c.get('name','?')} | {c.get('varieties','?')}")
