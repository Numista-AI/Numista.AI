import csv
import json
import os
import sys

# Reconfigure stdout to use utf-8 to avoid charmap errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

golden_schema_path = r"c:\Users\ericd\Documents\MyVertexProject\numista_backend\coin-schema.json"
with open(golden_schema_path, "r", encoding="utf-8") as f:
    schema = json.load(f)

required_fields = schema["required"]
properties = list(schema["properties"].keys())

print(f"Golden Schema fields ({len(properties)}): {properties}\n")

files_to_check = [
    r"c:\Users\ericd\Documents\MyVertexProject\AJ's Coins Backup 8 APR 26.csv",
    r"c:\Users\ericd\Documents\MyVertexProject\AJ_Currency_Parsed.csv",
    r"c:\Users\ericd\Documents\MyVertexProject\AJ_Currency_Parsed_v2.csv",
    r"c:\Users\ericd\Documents\MyVertexProject\AJ_Manual_Image_Sourcing_Currency.csv",
]

for file_path in files_to_check:
    print("=" * 80)
    print(f"File: {os.path.basename(file_path)}")
    if not os.path.exists(file_path):
        print("ERROR: File does not exist")
        continue

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            headers = next(reader)

        print(f"Total columns: {len(headers)}")
        print(f"Headers: {headers}")

        # Check required fields
        missing_required = [req for req in required_fields if req not in headers]
        if missing_required:
            print(f"❌ Missing required fields: {missing_required}")
        else:
            print("✅ All required fields present")

        # Match columns with properties
        matching = [col for col in headers if col in properties]
        extra = [col for col in headers if col not in properties]
        print(f"Matching golden schema fields ({len(matching)}): {matching}")
        print(f"Extra/non-standard fields ({len(extra)}): {extra}")

    except Exception as e:
        print(f"ERROR: Failed to read file: {e}")
