# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import os
import pandas as pd
from google.cloud import storage

BASE_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\US Mint"
CSV_PATH = os.path.join(BASE_DIR, "NumistaAI_2026_Acquisition_Template.csv")
BUCKET_NAME = "numista-reference-library"

client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

BAD_SIZES = [1824267, 1510409, 1510450] # Placeholder exact byte sizes after watermark
files_to_revert = []

# Find bad files
for f in os.listdir(BASE_DIR):
    if f.endswith('.jpg'):
        p = os.path.join(BASE_DIR, f)
        if os.path.getsize(p) in BAD_SIZES:
            files_to_revert.append(f)

print(f"Found {len(files_to_revert)} placeholder files to revert.")

df = pd.read_csv(CSV_PATH)
reverted_count = 0

for f in files_to_revert:
    print(f"Reverting {f}...")
    local_p = os.path.join(BASE_DIR, f)
    
    # 1. Delete local
    if os.path.exists(local_p):
        os.remove(local_p)
        
    # 2. Delete from GCS
    gcs_p = f"reference_library/2026_series/{f}"
    blob = bucket.blob(gcs_p)
    if blob.exists():
        blob.delete()
        
    # 3. Revert CSV
    mask = df['filename'] == f
    if mask.sum() > 0:
        df.loc[mask, 'gcs_url'] = 'PENDING_UPLOAD'
        df.loc[mask, 'attribution'] = ''
        df.loc[mask, 'license'] = ''
        reverted_count += 1

if reverted_count > 0:
    df.to_csv(CSV_PATH, index=False)
    print(f"Successfully reverted {reverted_count} placeholder files in the CSV and deleted them from local/GCS.")
