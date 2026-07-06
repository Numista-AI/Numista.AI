# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import json
data = json.load(open('master_coin_programs.json', encoding='utf-8'))
for p in data:
    print(f"{p['name']} | {p.get('category','?')} | {len(p.get('coins',[]))} coins")
