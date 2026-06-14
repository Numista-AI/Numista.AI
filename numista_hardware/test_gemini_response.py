"""Diagnose gemini-3.5-flash JSON response format and test the full agent pipeline."""
import os, json, logging, time
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

from dotenv import load_dotenv
load_dotenv('.env')

from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

# ── Test 1: Can gemini-3.5-flash return structured JSON? ─────────────────────
print("=== Test 1: gemini-3.5-flash JSON mode ===")
img = client.files.upload(file='captures/2023_Roosevelt_Dime_D_Obverse_20260523_1322.jpg')
resp = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=['Describe this image in JSON with key "description".', img],
    config=types.GenerateContentConfig(response_mime_type='application/json')
)
print("Raw response (first 500):", repr(resp.text[:500]))
try:
    d = json.loads(resp.text)
    print("JSON parsed OK, keys:", list(d.keys())[:5])
except Exception as e:
    print("JSON PARSE FAILED:", e)
    # Try stripping markdown fences
    text = resp.text.strip().lstrip('```json').lstrip('```').rstrip('```').strip()
    try:
        d = json.loads(text)
        print("JSON OK after stripping fences. FIX NEEDED in identify_coin.py")
    except:
        print("Still fails even after stripping fences")

# ── Test 2: Full identify_coin pipeline ──────────────────────────────────────
print("\n=== Test 2: run_numista_report pipeline ===")
from identify_coin import run_numista_report
t = time.time()
r = run_numista_report(
    'captures/2023_Roosevelt_Dime_D_Obverse_20260523_1322.jpg',
    'captures/2023_Roosevelt_Dime_D_Reverse_20260523_1322.jpg'
)
elapsed = round(time.time() - t, 1)
if r and r.get('year'):
    print(f"SUCCESS in {elapsed}s: {r.get('file_slug')} | {r.get('grade')}")
elif r:
    print(f"Partial result in {elapsed}s: slug={r.get('file_slug')}, year={r.get('year')}")
    print("  → JSON parse likely failing; response fell to fallback")
else:
    print(f"FAILED after {elapsed}s: run_numista_report returned None")
