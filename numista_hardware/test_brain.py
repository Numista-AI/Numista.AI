import os
import shutil
import pandas as pd
from datetime import datetime
from identify_coin import run_numista_report

# --- CONFIGURATION ---
MAIN_DIR = r"C:\Users\ericd\Documents\MyVertexProject\AJ's AI Coin Collection app"
DISPUTE_LOG = os.path.join(MAIN_DIR, 'numista_dispute_log.csv')
VERIFIED_DIR = os.path.join(MAIN_DIR, "verified_images")

def archive_verified_coin(slug, obv_path, rev_path):
    """Handles the permanent renaming logic you established."""
    os.makedirs(VERIFIED_DIR, exist_ok=True)
    
    # Matching your preferred format: Name_Side_Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    new_obv_name = f"{slug}_Obverse_{timestamp}.jpg"
    new_rev_name = f"{slug}_Reverse_{timestamp}.jpg"
    
    shutil.copy(obv_path, os.path.join(VERIFIED_DIR, new_obv_name))
    shutil.copy(rev_path, os.path.join(VERIFIED_DIR, new_rev_name))
    
    print(f"📁 Archived permanently as: {new_obv_name}")

def log_dispute(original_slug, corrected_slug, obv_path, rev_path):
    """Logs the correction to our 'Expert Clash' ledger."""
    train_dir = os.path.join(MAIN_DIR, "training_data")
    os.makedirs(train_dir, exist_ok=True)
    
    entry_id = f"correction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Save to the CSV Ledger
    new_row = pd.DataFrame([{
        "Capture_ID": entry_id,
        "AI_Initial_Guess": original_slug,
        "User_Correction": corrected_slug,
        "Status": "Pending_Review",
        "Consensus_Count": "0",
        "Expert_Notes": "Initial user correction."
    }])
    
    if not os.path.isfile(DISPUTE_LOG):
        new_row.to_csv(DISPUTE_LOG, index=False)
    else:
        new_row.to_csv(DISPUTE_LOG, mode='a', header=False, index=False)
    print(f"✅ Dispute Logged for: {corrected_slug}")

def test_pipeline():
    temp_obv = os.path.join(MAIN_DIR, "captures", "obverse_peak.jpg")
    temp_rev = os.path.join(MAIN_DIR, "captures", "reverse_peak.jpg")

    print("\n--- Numista.AI: Full Identity & Archive Cycle ---")
    result = run_numista_report(temp_obv, temp_rev)
    if not result: return

    slug = result.get('file_slug', 'unknown')
    conf = result.get('confidence_score', 0)

    # 1. Human-in-the-Loop Check
    if conf < 95:
        print(f"⚠️ LOW CONFIDENCE ({conf}%). AI suggest: {slug}")
        choice = input("Accept (y) / Correct (c): ").lower()
        if choice == 'c':
            corrected_slug = input("Enter the correct ID: ")
            log_dispute(slug, corrected_slug, temp_obv, temp_rev)
            slug = corrected_slug

    # 2. Permanent Renaming & Archiving
    archive_verified_coin(slug, temp_obv, temp_rev)

if __name__ == "__main__":
    test_pipeline()