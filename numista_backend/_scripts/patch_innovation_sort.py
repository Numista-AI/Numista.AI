# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import json
import os

file_path = os.path.join(os.path.dirname(__file__), 'master_coin_programs.json')

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for prog in data:
    if prog.get('name') == 'INNOVATION DOLLARS':
        coins = prog.get('coins', [])
        coins.sort(key=lambda x: x.get('year', '0'))
        prog['coins'] = coins
        break

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
print("Sorted INNOVATION DOLLARS")
