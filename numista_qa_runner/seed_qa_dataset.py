"""
Numista.AI -- QA Dataset Seeder & Lockfile Sanitation Manager
Seeds synthetic test vectors for the Domain Completeness & Legal-Grade QC Suite.
Supports lockfile reconciliation (.qa_sandbox_lock) and process-kill resilient teardown.
"""
import os
import json
import time
import datetime
import google.auth
from google.cloud import firestore

SANDBOX_EMAIL = "qa_bot_sandbox@numista.ai"
LOCKFILE_PATH = os.path.join(os.path.dirname(__file__), ".qa_sandbox_lock")
MASTER_CSV = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\qa_dataset_master_numista_schema.csv"

# Comprehensive Synthetic QA Test Vectors
SYNTHETIC_VECTORS = [
    {
        "id": "VECTOR_2026_UNC_SET",
        "name": "2026 United States Mint Uncirculated Coin Set",
        "Year": "2026",
        "Mint Mark": "P&D",
        "Denomination": "Mint Set",
        "Program/Series": "US Mint Annual Sets",
        "Theme/Subject": "Uncirculated Set 2026",
        "Condition": "Uncirculated",
        "Surface & Strike Quality": "Business",
        "Holder Type": "OGP",
        "Quantity": 1,
        "is_mint_set": True,
        "set_broken_up": False,
        "parent_set_id": None,
        "constituent_coin_ids": ["VECTOR_2026_UNC_P_INNOV", "VECTOR_2026_UNC_D_INNOV"],
        "canonical_set_sku": "USM-2026-UNC",
        "Purchase Cost": "35.00",
        "AI Estimated Value": "35.00",
        "Metal Content": "Clad & Copper-Nickel",
        "category": "coin",
        "inventoryStatus": "owned"
    },
    {
        "id": "VECTOR_2026_UNC_P_INNOV",
        "name": "2026-P Innovation Dollar",
        "Year": "2026",
        "Mint Mark": "P",
        "Denomination": "$1",
        "Program/Series": "American Innovation Dollars",
        "Theme/Subject": "2026 Innovation",
        "Condition": "Uncirculated",
        "Surface & Strike Quality": "Business",
        "Holder Type": "OGP",
        "Quantity": 1,
        "is_mint_set": False,
        "set_broken_up": False,
        "parent_set_id": "VECTOR_2026_UNC_SET",
        "constituent_coin_ids": [],
        "canonical_set_sku": "USM-2026-UNC",
        "Purchase Cost": "0.00",
        "AI Estimated Value": "0.00",
        "Metal Content": "Manganese-Brass Clad",
        "category": "coin",
        "inventoryStatus": "owned"
    },
    {
        "id": "VECTOR_2026_UNC_D_INNOV",
        "name": "2026-D Innovation Dollar",
        "Year": "2026",
        "Mint Mark": "D",
        "Denomination": "$1",
        "Program/Series": "American Innovation Dollars",
        "Theme/Subject": "2026 Innovation",
        "Condition": "Uncirculated",
        "Surface & Strike Quality": "Business",
        "Holder Type": "OGP",
        "Quantity": 1,
        "is_mint_set": False,
        "set_broken_up": False,
        "parent_set_id": "VECTOR_2026_UNC_SET",
        "constituent_coin_ids": [],
        "canonical_set_sku": "USM-2026-UNC",
        "Purchase Cost": "0.00",
        "AI Estimated Value": "0.00",
        "Metal Content": "Manganese-Brass Clad",
        "category": "coin",
        "inventoryStatus": "owned"
    },
    {
        "id": "VECTOR_2026_SILVER_PROOF",
        "name": "2026 Silver Proof Set",
        "Year": "2026",
        "Mint Mark": "S",
        "Denomination": "Proof Set",
        "Program/Series": "US Mint Silver Proof Sets",
        "Theme/Subject": "2026 Silver Proof",
        "Condition": "PR-70",
        "Surface & Strike Quality": "Proof",
        "Holder Type": "OGP",
        "Quantity": 1,
        "is_mint_set": True,
        "set_broken_up": False,
        "parent_set_id": None,
        "constituent_coin_ids": [],
        "canonical_set_sku": "USM-2026-SIL-PRF",
        "Purchase Cost": "105.00",
        "AI Estimated Value": "105.00",
        "Metal Content": "99.9% Silver",
        "category": "coin",
        "inventoryStatus": "owned"
    },
    {
        "id": "VECTOR_HISTORICAL_MORGAN",
        "name": "1893-S Morgan Silver Dollar",
        "Year": "1893",
        "Mint Mark": "S",
        "Denomination": "Dollar",
        "Program/Series": "Morgan Dollars",
        "Theme/Subject": "Liberty Head",
        "Condition": "VF-30",
        "Surface & Strike Quality": "Business",
        "Holder Type": "PCGS Slab",
        "Grading Service": "PCGS",
        "Certification Number": "12345678",
        "Quantity": 1,
        "is_mint_set": False,
        "set_broken_up": False,
        "parent_set_id": None,
        "constituent_coin_ids": [],
        "Purchase Cost": "3500.00",
        "AI Estimated Value": "4200.00",
        "Metal Content": "90% Silver",
        "Melt Value": "22.50",
        "category": "coin",
        "inventoryStatus": "owned"
    },
    {
        "id": "VECTOR_CLASSIC_COMMEM",
        "name": "1925 Stone Mountain Memorial Half Dollar",
        "Year": "1925",
        "Mint Mark": "",
        "Denomination": "Half Dollar",
        "Program/Series": "Classic Commemoratives",
        "Theme/Subject": "Stone Mountain",
        "Condition": "MS-64",
        "Surface & Strike Quality": "Business",
        "Holder Type": "NGC Slab",
        "Grading Service": "NGC",
        "Certification Number": "87654321",
        "Quantity": 1,
        "is_mint_set": False,
        "set_broken_up": False,
        "parent_set_id": None,
        "constituent_coin_ids": [],
        "Purchase Cost": "85.00",
        "AI Estimated Value": "120.00",
        "Metal Content": "90% Silver",
        "Melt Value": "11.25",
        "category": "coin",
        "inventoryStatus": "owned"
    },
    {
        "id": "VECTOR_PRE33_GOLD",
        "name": "1907 Saint-Gaudens $20 Gold Double Eagle",
        "Year": "1907",
        "Mint Mark": "",
        "Denomination": "$20",
        "Program/Series": "Pre-1933 Gold",
        "Theme/Subject": "Saint-Gaudens High Relief",
        "Condition": "MS-65",
        "Surface & Strike Quality": "Business",
        "Holder Type": "PCGS Slab",
        "Quantity": 1,
        "is_mint_set": False,
        "set_broken_up": False,
        "parent_set_id": None,
        "constituent_coin_ids": [],
        "Purchase Cost": "2100.00",
        "AI Estimated Value": "2650.00",
        "Metal Content": "90% Gold",
        "Melt Value": "2320.00",
        "category": "coin",
        "inventoryStatus": "owned"
    },
    {
        "id": "VECTOR_PAPER_MONEY",
        "name": "1899 $5 Silver Certificate - Indian Head",
        "Year": "1899",
        "Mint Mark": "",
        "Denomination": "$5",
        "Program/Series": "Obsolete Currency & Large Notes",
        "Theme/Subject": "Chief Running Antelope",
        "Condition": "Very Fine 25",
        "Surface & Strike Quality": "Paper",
        "Holder Type": "PMG Sleeve",
        "Quantity": 1,
        "is_mint_set": False,
        "set_broken_up": False,
        "parent_set_id": None,
        "constituent_coin_ids": [],
        "Purchase Cost": "450.00",
        "AI Estimated Value": "650.00",
        "Metal Content": "Paper",
        "category": "paper_currency",
        "inventoryStatus": "owned"
    },
    {
        "id": "VECTOR_WORLD_COIN",
        "name": "1911 Great Britain Gold Sovereign",
        "Year": "1911",
        "Mint Mark": "",
        "Denomination": "Sovereign",
        "Program/Series": "World Gold Coins",
        "Theme/Subject": "King George V",
        "Condition": "MS-62",
        "Surface & Strike Quality": "Business",
        "Holder Type": "Raw",
        "Quantity": 1,
        "is_mint_set": False,
        "set_broken_up": False,
        "parent_set_id": None,
        "constituent_coin_ids": [],
        "Purchase Cost": "550.00",
        "AI Estimated Value": "580.00",
        "Metal Content": "22k Gold",
        "Melt Value": "565.00",
        "category": "world_coin",
        "inventoryStatus": "owned"
    }
]

def get_firestore_db():
    sa_path = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json"
    if os.path.exists(sa_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path
    try:
        creds, _ = google.auth.default()
        return firestore.Client(credentials=creds, project="studio-9101802118-8c9a8")
    except Exception as e:
        print(f"Error connecting to Firestore: {e}")
        return None

def teardown_qa_sandbox(email=SANDBOX_EMAIL):
    """Purges all test items from the QA sandbox collection to ensure a clean slate."""
    db = get_firestore_db()
    if not db:
        return False
    print(f"=== PURGING QA SANDBOX FIRESTORE COLLECTION ({email}) ===")
    user_ref = db.collection("users").document(email)
    coins_ref = user_ref.collection("coins")
    docs = list(coins_ref.stream())
    
    if docs:
        batch = db.batch()
        count = 0
        for d in docs:
            batch.delete(d.reference)
            count += 1
            if count % 400 == 0:
                batch.commit()
                batch = db.batch()
        if count % 400 != 0:
            batch.commit()
        print(f"Purged {count} documents from {email}/coins.")
    else:
        print("Sandbox collection is already clean.")

    # Remove lockfile if present
    if os.path.exists(LOCKFILE_PATH):
        try:
            os.remove(LOCKFILE_PATH)
            print("Removed .qa_sandbox_lock.")
        except Exception as e:
            print(f"Warning: Could not remove lockfile: {e}")
    return True

def seed_qa_account(email=SANDBOX_EMAIL):
    """Reconciles lockfile, purges stale data, and seeds fresh synthetic vectors."""
    db = get_firestore_db()
    if not db:
        return False

    # Check lockfile reconciliation for process-kill recovery
    if os.path.exists(LOCKFILE_PATH):
        print("WARNING: Found existing .qa_sandbox_lock (previous run may have terminated abruptly).")
        print("Reconciling and forcing sandbox cleanup...")
        teardown_qa_sandbox(email)

    # Create lockfile
    lock_data = {
        "sandbox_account": email,
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "status": "RUNNING"
    }
    with open(LOCKFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(lock_data, f, indent=2)

    print(f"=== SEEDING {len(SYNTHETIC_VECTORS)} SYNTHETIC QA VECTORS INTO {email} ===")
    user_ref = db.collection("users").document(email)
    coins_ref = user_ref.collection("coins")

    batch = db.batch()
    for item in SYNTHETIC_VECTORS:
        doc_id = item["id"]
        doc_ref = coins_ref.document(doc_id)
        batch.set(doc_ref, item, merge=True)
    
    batch.commit()
    print(f"SUCCESS: Successfully seeded {len(SYNTHETIC_VECTORS)} vectors into users/{email}/coins!")
    return True

if __name__ == "__main__":
    seed_qa_account()
