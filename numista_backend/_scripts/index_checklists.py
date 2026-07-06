# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import json
import re

def parse_eisenhower(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Extract years and mint marks
    matches = re.findall(r'(197[1-8](?:-[A-Z] (?:Variety I\*|Variety II\*\*|Silver Clad|Silver Proof|Proof)|-[A-Z]| (?:Variety I\*|Variety II\*\*))?)', text)
    matches = [m.replace('\n', ' ').strip() for m in matches]
    return {"program": "Eisenhower Dollar", "coins": matches}

def parse_presidential(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    presidents = []
    # simplistic heuristic for presidential names followed by dotted leaders
    lines = text.split('\n')
    for line in lines:
        if ' . . ' in line:
            name = line.split(' . . ')[0].strip()
            if name and not name.startswith('Mint Mark'):
                presidents.append(name)
    
    return {"program": "Presidential Dollar", "presidents": presidents}

eisenhower_data = parse_eisenhower('eisenhower.txt')
presidential_data = parse_presidential('presidential.txt')

index = {
    "Eisenhower": eisenhower_data,
    "Presidential": presidential_data
}

with open('indexed_coins.json', 'w', encoding='utf-8') as f:
    json.dump(index, f, indent=4)
