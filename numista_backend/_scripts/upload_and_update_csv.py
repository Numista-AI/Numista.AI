# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import os
import pandas as pd
from google.cloud import storage

BASE_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\US Mint"
CSV_PATH = os.path.join(BASE_DIR, "NumistaAI_2026_Acquisition_Template.csv")
BUCKET_NAME = "numista-reference-library"

obverse_filename = "2026_quarter_dollar_revolutionary_war_obverse.jpg"
reverse_filename = "2026_quarter_dollar_revolutionary_war_reverse.jpg"

obverse_path = os.path.join(BASE_DIR, obverse_filename)
reverse_path = os.path.join(BASE_DIR, reverse_filename)

client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

obv_gcs_path = f"reference_library/2026_series/{obverse_filename}"
rev_gcs_path = f"reference_library/2026_series/{reverse_filename}"

# Upload obverse
print(f"Uploading {obverse_filename} to GCS...")
obv_blob = bucket.blob(obv_gcs_path)
obv_blob.upload_from_filename(obverse_path)
obv_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{obv_gcs_path}"
print(f"Uploaded obverse: {obv_url}")

# Upload reverse
print(f"Uploading {reverse_filename} to GCS...")
rev_blob = bucket.blob(rev_gcs_path)
rev_blob.upload_from_filename(reverse_path)
rev_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{rev_gcs_path}"
print(f"Uploaded reverse: {rev_url}")

# Update CSV
print("Updating CSV...")
df = pd.read_csv(CSV_PATH)

# Mask for the rows
obv_mask = df['filename'] == obverse_filename
rev_mask = df['filename'] == reverse_filename

if obv_mask.sum() > 0:
    df.loc[obv_mask, 'gcs_url'] = obv_url
    # Verify attribution and license as requested in prompt step 7
    df.loc[obv_mask, 'attribution'] = 'U.S. Mint'
    df.loc[obv_mask, 'license'] = 'Public Domain'

if rev_mask.sum() > 0:
    df.loc[rev_mask, 'gcs_url'] = rev_url
    df.loc[rev_mask, 'attribution'] = 'U.S. Mint'
    df.loc[rev_mask, 'license'] = 'Public Domain'

df.to_csv(CSV_PATH, index=False)
print("CSV updated successfully.")
