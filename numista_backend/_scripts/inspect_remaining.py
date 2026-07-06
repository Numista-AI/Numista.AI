# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('master_coin_programs.json', encoding='utf-8'))
already_done = {
    'Lincoln Cents','Morgan Dollars','Buffalo Nickels','Mercury Dimes',
    'Kennedy Half Dollars','Roosevelt Dimes','Jefferson Nickels',
    'Washington Quarters (Classic)','50 State Quarters',
    'D.C. & U.S. Territories Quarters','America the Beautiful Quarters (National Parks)',
    'Presidential Dollars','Sacagawea & Native American Dollars',
    'American Women Quarters','American Innovation $1 Coin Program',
}
for p in data:
    if p['name'] not in already_done:
        coins = p.get('coins', [])
        v0 = coins[0].get('varieties','?') if coins else '?'
        print(f"TODO: {p['name']!r} | {len(coins)} coins | v: {v0}")
