import os
from google.cloud import storage
import PyPDF2

BUCKET_NAME = "numista-training-docs"
BLOB_NAME = "Numista.AI Training Data/US Mint Coin Programs/LC-KGW-50-State-Commemorative-Quarter-Checklist.pdf"
LOCAL_PDF = "50_State_Checklist.pdf"

print("Downloading PDF...")
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)
blob = bucket.blob(BLOB_NAME)
blob.download_to_filename(LOCAL_PDF)
print("Download complete. Parsing text...")

with open(LOCAL_PDF, "rb") as f:
    reader = PyPDF2.PdfReader(f)
    full_text = ""
    for idx, page in enumerate(reader.pages):
        full_text += f"\n--- Page {idx + 1} ---\n"
        full_text += page.extract_text()
        
print("Sample Text:")
print(full_text[:3000])

# Just dumping out the text to analyze the structure
with open("pdf_dump.txt", "w", encoding='utf-8') as out:
    out.write(full_text)
