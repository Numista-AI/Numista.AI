# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import os
import sys
import json
import time
import google.auth
from google import genai
from google.genai import types as genai_types

GCP_PROJECT_ID = "studio-9101802118-8c9a8"
VERTEX_LOCATION = "us-central1"

PDF_DIR = r"C:\Users\ericd\Documents\MyVertexProject\US Mint Coin Programs"
OUTPUT_FILE = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\master_coin_programs.json"

# Force UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def main():
    print(f"[Init] Authenticating...")
    try:
        credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        client = genai.Client(vertexai=True, project=GCP_PROJECT_ID, location=VERTEX_LOCATION, credentials=credentials)
    except Exception as e:
        print(f"[Error] Failed to authenticate: {e}")
        sys.exit(1)

    schema = {
        "type": "OBJECT",
        "properties": {
            "name": {"type": "STRING"},
            "years": {"type": "STRING"},
            "mint_mark_locations": {"type": "STRING"},
            "coins": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "year": {"type": "STRING"},
                        "name": {"type": "STRING"},
                        "varieties": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"}
                        }
                    }
                }
            }
        }
    }

    # Config block will be created inline in the call

    pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]
    print(f"[Dataset] Found {len(pdf_files)} PDF files to process in {PDF_DIR}.")

    results = []
    
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                results = json.loads(content) if content else []
        except Exception as e:
            print(f"[Warning] Failed to load existing output: {e}. Starting fresh.")
            results = []

    processed_files = {r.get("_source_file") for r in results if r.get("_source_file")}

    for i, file_name in enumerate(pdf_files):
        if file_name in processed_files:
            print(f"[{i+1}/{len(pdf_files)}] [Skipped] Already processed: {file_name}")
            continue

        print(f"[{i+1}/{len(pdf_files)}] Processing {file_name}...")
        file_path = os.path.join(PDF_DIR, file_name)
        
        try:
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()

            prompt = (
                "You are an expert numismatist data extractor. Analyze this US Mint coin checklist PDF.\n"
                "1. Extract the overarching series name (e.g. 'Morgan Dollars').\n"
                "2. Extract the overall year range.\n"
                "3. Carefully read any paragraph text to find the 'mint mark locations' description and explicitly output it.\n"
                "4. Extract EVERY coin listed. For each coin, capture its year, its full specific name (e.g. '1878 8 Tail Feathers'), and all the mint mark varieties (e.g. 'P', 'D', 'S', 'Proof') that are present as bubbles/checkboxes next to it.\n"
                "Return ONLY structured JSON adhering exactly to the provided schema."
            )

            pdf_part = genai_types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=[pdf_part, prompt],
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.0
                )
            )
            
            data = json.loads(response.text)
            data["_source_file"] = file_name
            results.append(data)
            
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
                
            print(f"  -> [SUCCESS] Extracted {len(data.get('coins', []))} coins.")
            
        except Exception as e:
            print(f"  -> [ERROR] Failed extracting {file_name}: {e}")
        
        time.sleep(3) 

    print(f"\n[Done] Finished extracting all files! Data saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
