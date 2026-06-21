"""
inspect_new_zip.py
Opens the new pilot_confederate_5.zip and inspects its contents + images for QC.
"""
import os, sys, zipfile, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ZIP_PATH = r'C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Coin Images\Coins Images to Find\Downloads from Grok\pilot_confederate_5.zip'
EXTRACT_DIR = r'C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Coin Images\Coins Images to Find\Downloads from Grok\_new_extract'

# List zip contents
with zipfile.ZipFile(ZIP_PATH, 'r') as z:
    print('=== ZIP CONTENTS ===')
    for info in z.infolist():
        size_kb = info.file_size / 1024
        print(f'  {info.filename}  ({size_kb:.1f} KB)')
    
    # Extract for inspection
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    z.extractall(EXTRACT_DIR)
    print(f'\nExtracted to: {EXTRACT_DIR}')

# List what was extracted
print('\n=== EXTRACTED FILES ===')
for root, dirs, files in os.walk(EXTRACT_DIR):
    for f in files:
        full = os.path.join(root, f)
        size_kb = os.path.getsize(full) / 1024
        rel = os.path.relpath(full, EXTRACT_DIR)
        print(f'  {rel}  ({size_kb:.1f} KB)')
