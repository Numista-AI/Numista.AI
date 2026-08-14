# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import fitz
import os
import json
from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project='studio-9101802118-8c9a8', location='global')
model_id = 'gemini-3.5-flash'

pdf_files = [
    r'c:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\14 AUG 2026\CheckList Test\50 US States 14 AUG 26.pdf',
    r'c:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\14 AUG 2026\CheckList Test\ATB 14 AUG 26.pdf',
    r'c:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\14 AUG 2026\CheckList Test\DC  Territories.pdf'
]

results = {}

for pdf_path in pdf_files:
    fname = os.path.basename(pdf_path)
    doc = fitz.open(pdf_path)
    print(f'=== {fname} ({len(doc)} pages) ===')
    file_items = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes('png')
        
        prompt = (
            "Analyze this coin checklist scan page.\n"
            "Extract every coin entry where the checkbox or circle is FILLED/CHECKED or marked as owned, or has handwritten notes.\n"
            "Return ONLY valid JSON matching this schema:\n"
            "[\n"
            "  {\n"
            '    "year": "YYYY",\n'
            '    "mint": "P" or "D" or "S",\n'
            '    "theme_subject": "State or Park or Territory name",\n'
            '    "notes": "handwritten notes or location"\n'
            "  }\n"
            "]\n"
        )
        try:
            resp = client.models.generate_content(
                model=model_id,
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type='image/png'),
                    types.Part.from_text(text=prompt)
                ],
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    temperature=0.1
                )
            )
            data = json.loads(resp.text)
            print(f'  Page {page_num+1}: {len(data)} checked entries')
            for item in data:
                item['source_file'] = fname
                item['page'] = page_num + 1
                file_items.append(item)
                print(f"    [{item.get('year')} {item.get('mint')}] {item.get('theme_subject')} | Notes: {item.get('notes')}")
        except Exception as e:
            print(f'  Page {page_num+1} error: {e}')
            
    results[fname] = file_items

with open('numista_backend/_scripts/extracted_beta_checklist.json', 'w') as f:
    json.dump(results, f, indent=2)

print('\nDone! Saved to numista_backend/_scripts/extracted_beta_checklist.json')
