"""
Quick check: what Silver Eagle keys are in coin_image_index?
Also checks Eric's testing account for coin image_url_obverse fields.
"""
import os
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")

from google.cloud import firestore
import google.auth

credentials, _ = google.auth.default()
db = firestore.Client(credentials=credentials, project="studio-9101802118-8c9a8")

# 1. Check silver eagle entries in image index
docs = list(db.collection("coin_image_index").stream())
silver_eagle = [d for d in docs if "american-eagle-silver" in d.id]
print(f"Silver eagle docs in index: {len(silver_eagle)}")
for d in silver_eagle:
    data = d.to_dict()
    print(f"  Key: {d.id}")
    print(f"    year={data.get('year')}, mint={data.get('mint')}, program={data.get('program')}")

# 2. Check Eric's coins and their image_url_obverse fields
print("\n=== Eric's Coins (eric.seaman@yahoo.com) ===")
coins = list(db.collection("users").document("eric.seaman@yahoo.com").collection("coins").stream())
print(f"Total coins: {len(coins)}")
with_image = 0
without_image = 0
for c in coins:
    data = c.to_dict()
    img = data.get("image_url_obverse", "")
    if img:
        with_image += 1
        print(f"  [HAS IMAGE] {data.get('Year','')} {data.get('Mint Mark','')} {data.get('Program/Series','')} -> {img[:80]}")
    else:
        without_image += 1

print(f"\nCoins with image_url_obverse: {with_image}")
print(f"Coins WITHOUT image_url_obverse: {without_image}")
if coins:
    sample = coins[0].to_dict()
    print(f"\nSample coin fields: {list(sample.keys())}")
    print(f"  Program/Series: {sample.get('Program/Series','')}")
    print(f"  Denomination: {sample.get('Denomination','')}")
    print(f"  Theme/Subject: {sample.get('Theme/Subject','')}")
