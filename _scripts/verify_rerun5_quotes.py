import re
import os

md_path = r"C:\Users\ericd\OneDrive\Documents\1 NUMISTA.AI\MORGAN SME DATABASE\GEMINI38_REVIEW_EVIDENCE_PACK_2026-10-07_RERUN5_BATCH1_AWQ.md"
pages_dir = r"C:\Users\ericd\OneDrive\Documents\1 NUMISTA.AI\MORGAN SME DATABASE\rerun5_pages"

with open(md_path, "r", encoding="utf-8") as f:
    text = f.read()

rows = re.findall(r'## Row (\d+)[^\n]+\n- \*\*Morgan proposes:\*\* (.*?)\n- \*\*Gemini verdict:\*\* (.*?)\n- \*\*Independent Primary Source \((.*?)\):\*\* (.*?)\n- \*\*Identifier / Code:\*\* (.*?)\n- \*\*Quote \(<25 words\):\*\* "(.*?)"', text)

print(f"Parsed {len(rows)} rows.")

passed = 0
for r in rows:
    row_num = r[0]
    quote = r[-1]
    q_clean = re.sub(r'[^a-zA-Z0-9]', '', quote).lower()
    
    found = False
    for fn in os.listdir(pages_dir):
        if fn.endswith('.txt'):
            with open(os.path.join(pages_dir, fn), 'r', encoding='utf-8') as fp:
                t = fp.read()
            t_clean = re.sub(r'[^a-zA-Z0-9]', '', t).lower()
            if q_clean in t_clean:
                found = True
                break
    if found:
        passed += 1
    else:
        print(f"Row {row_num} FAILED: \"{quote}\"")

print(f"Mechanical check result: {passed} / {len(rows)} passed ({passed/len(rows)*100:.1f}%)")
