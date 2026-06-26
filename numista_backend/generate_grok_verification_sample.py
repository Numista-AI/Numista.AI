import os
import sys
import csv
import random
import firebase_admin
from firebase_admin import credentials, firestore

# Force UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SA_KEY = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json"
USER_EMAIL = "jseaman1204@gmail.com"
PROJECT_DIR = r"C:\Users\ericd\Documents\MyVertexProject"

if not firebase_admin._apps:
    cred = credentials.Certificate(SA_KEY)
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("Fetching healed coins from AJ's collection...")
col_ref = db.collection("users").document(USER_EMAIL).collection("coins")
docs = list(col_ref.stream())

healed_coins = []
for doc in docs:
    d = doc.to_dict()
    status = d.get("image_verification_status", "unverified")
    has_image = bool(d.get("image_url_obverse") or d.get("image_url_reverse"))
    if status == "unverified" and has_image:
        healed_coins.append((doc.id, d))

print(f"Total unverified coins with images: {len(healed_coins)}")
if not healed_coins:
    print("[ERR] No unverified coin images found.")
    sys.exit(1)

# Select 50 random coins
sample = random.sample(healed_coins, min(50, len(healed_coins)))

csv_path = os.path.join(PROJECT_DIR, "grok_verification_sample.csv")
md_path = os.path.join(PROJECT_DIR, "grok_verification_sample.md")

# Write CSV
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Coin_ID", "Year", "Mint_Mark", "Denomination", "Program_or_Series", 
        "Prior_Mismatches", "Obverse_Image_URL", "Reverse_Image_URL"
    ])
    for doc_id, data in sample:
        writer.writerow([
            doc_id,
            data.get("Year", ""),
            data.get("Mint Mark", ""),
            data.get("Denomination", ""),
            data.get("Program/Series", ""),
            data.get("image_fix_reason", "").replace("Auto-healed by audit pipeline: ", "").replace("Auto-healed by custom sourcing pipeline", "Custom Sourcing"),
            data.get("image_url_obverse", ""),
            data.get("image_url_reverse", "")
        ])

# Write Markdown
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# Grok Coin Image Verification Sample (50 Healed Coins)\n\n")
    f.write("Upload this document to Grok to verify the accuracy of the healed images. Grok's vision model can fetch the public GCS URLs and confirm they match the coin year, denomination, and design.\n\n")
    f.write("| # | Coin Details | Prior Issue | Obverse Image | Reverse Image |\n")
    f.write("|---|---|---|---|---|\n")
    for idx, (doc_id, data) in enumerate(sample):
        name = f"{data.get('Year', '')} {data.get('Mint Mark', '')} {data.get('Denomination', '')} ({data.get('Program/Series', '')})"
        reason = data.get("image_fix_reason", "").replace("Auto-healed by audit pipeline: ", "").replace("Auto-healed by custom sourcing pipeline", "Custom Sourcing")
        obv_url = data.get("image_url_obverse", "")
        rev_url = data.get("image_url_reverse", "")
        
        # We write them as plain text links for Grok to access
        f.write(f"| {idx+1} | **{name}**<br>ID: `{doc_id}` | {reason} | [Obverse Link]({obv_url}) | [Reverse Link]({rev_url}) |\n")

print(f"[OK] Grok verification CSV written: {csv_path}")
print(f"[OK] Grok verification MD written: {md_path}")
sys.exit(0)
