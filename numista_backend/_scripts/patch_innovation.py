# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import json
import os

file_path = os.path.join(os.path.dirname(__file__), 'master_coin_programs.json')

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for prog in data:
    if prog.get('name') == 'INNOVATION DOLLARS':
        coins = prog.get('coins', [])
        
        # Remove any existing 2024-2026 if they exist but lack subjects
        coins = [c for c in coins if c['year'] not in ['2024', '2025', '2026']]
        
        new_coins = [
            {'year': '2024', 'name': 'Illinois Steel Plow', 'varieties': ['P', 'D', 'S', 'Proof']},
            {'year': '2024', 'name': 'Alabama Saturn V Rocket', 'varieties': ['P', 'D', 'S', 'Proof']},
            {'year': '2024', 'name': 'Maine DC Defibrillator', 'varieties': ['P', 'D', 'S', 'Proof']},
            {'year': '2024', 'name': 'Missouri George Washington Carver', 'varieties': ['P', 'D', 'S', 'Proof']},
            
            {'year': '2025', 'name': 'Arkansas Raye Montague', 'varieties': ['P', 'D', 'S', 'Proof']},
            {'year': '2025', 'name': 'Michigan Ford Model T', 'varieties': ['P', 'D', 'S', 'Proof']},
            {'year': '2025', 'name': 'Florida Space Shuttle', 'varieties': ['P', 'D', 'S', 'Proof']},
            {'year': '2025', 'name': 'Texas Artificial Heart', 'varieties': ['P', 'D', 'S', 'Proof']},
            
            {'year': '2026', 'name': 'Iowa Dr. Norman Borlaug', 'varieties': ['P', 'D', 'S', 'Proof']},
            {'year': '2026', 'name': 'Wisconsin Cray-1 Supercomputer', 'varieties': ['P', 'D', 'S', 'Proof']},
            {'year': '2026', 'name': 'California Steve Jobs Apple', 'varieties': ['P', 'D', 'S', 'Proof']},
            {'year': '2026', 'name': 'Minnesota Mobile Refrigeration', 'varieties': ['P', 'D', 'S', 'Proof']},
        ]
        
        coins.extend(new_coins)
        prog['coins'] = coins
        break

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
print("Updated INNOVATION DOLLARS in master_coin_programs.json")
