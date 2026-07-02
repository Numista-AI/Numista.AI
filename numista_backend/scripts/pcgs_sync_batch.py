
import sys, os
from pathlib import Path
import json
import time

# Set encoding for PowerShell/Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add numista_backend to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from numista_scraper.agent import NumistaScraperAgent
    from numista_scraper.storage import db
    import test_pcgs_api as pcgs_api
    
    print("[PCGS Sync] Starting Census & Price Guide Auto-Sync...")
    
    agent = NumistaScraperAgent()
    col_ref = db.collection("definitive_reference")
    
    # Process a small batch for verification
    docs = col_ref.limit(10).stream()
    
    updated_count = 0
    
    for doc in docs:
        coin_data = doc.to_dict()
        doc_id = doc.id
        
        # 1. Resolve PCGS Number
        pcgs_no = agent.resolve_pcgs_no(coin_data)
        if not pcgs_no:
            print(f"  ⏭  Skipping {doc_id} — could not resolve PCGS number.")
            continue
            
        print(f"  🔄 Syncing {doc_id} (PCGS #{pcgs_no})...")
        
        # 2. Call PCGS API for CoinFacts
        # We'll use grade 65 as a representative sample
        status, data = pcgs_api.call('/coindetail/GetCoinFactsByGrade', {'PCGSNo': pcgs_no, 'GradeNo': 65, 'PlusGrade': 'false'})
        
        if status == 200 and isinstance(data, dict):
            # 3. Extract Census and Price Data
            population = data.get("Population")
            price = data.get("PriceGuideValue")
            
            # Update Firestore
            update_payload = {
                "pcgs_no": pcgs_no,
                "population_total": population,
                "price_guide": {
                    "ms65": price,
                    "last_updated": int(time.time())
                },
                "last_pcgs_sync": int(time.time())
            }
            
            col_ref.document(doc_id).update(update_payload)
            updated_count += 1
            print(f"  ✅ Updated {doc_id} with Population: {population}, Price: ${price}")
        else:
            print(f"  ⚠ PCGS API error for {pcgs_no}: {status}")
            
        time.sleep(1) # Be nice to the API
        
    print(f"\nFinished. Updated {updated_count} records.")
    
except Exception as e:
    print(f"❌ PCGS Sync Error: {e}")
    import traceback
    traceback.print_exc()
