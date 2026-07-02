
import sys, os
from pathlib import Path
import requests

# Set encoding for PowerShell/Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add numista_backend to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from numista_scraper.storage import db, download_image, upload_to_gcs, update_coin_images_in_databases
    
    print("[Migration] Starting GCS Image Migration...")
    
    col_ref = db.collection("definitive_reference")
    # Stream all documents to check for external URLs
    docs = col_ref.stream()
    
    migrated_count = 0
    limit = 20 # Batch limit for this run
    
    for doc in docs:
        if migrated_count >= limit:
            break
            
        data = doc.to_dict()
        doc_id = doc.id
        obv_url = data.get("image_url_obverse")
        rev_url = data.get("image_url_reverse")
        
        updated = False
        new_obv = obv_url
        new_rev = rev_url
        
        # Check obverse
        if obv_url and "storage.googleapis.com" not in obv_url and "http" in obv_url:
            print(f"  Migrating obverse for {doc_id}: {obv_url}")
            img_bytes = download_image(obv_url)
            if img_bytes:
                ext = obv_url.split(".")[-1].split("?")[0]
                if len(ext) > 4: ext = "jpg"
                gcs_path = f"coins/{doc_id}_obv.{ext}"
                new_url = upload_to_gcs(img_bytes, gcs_path)
                if new_url:
                    new_obv = new_url
                    updated = True
        
        # Check reverse
        if rev_url and "storage.googleapis.com" not in rev_url and "http" in rev_url:
            print(f"  Migrating reverse for {doc_id}: {rev_url}")
            img_bytes = download_image(rev_url)
            if img_bytes:
                ext = rev_url.split(".")[-1].split("?")[0]
                if len(ext) > 4: ext = "jpg"
                gcs_path = f"coins/{doc_id}_rev.{ext}"
                new_url = upload_to_gcs(img_bytes, gcs_path)
                if new_url:
                    new_rev = new_url
                    updated = True
                    
        if updated:
            update_coin_images_in_databases(doc_id, new_obv, new_rev)
            migrated_count += 1
            print(f"  ✅ Successfully migrated {doc_id}")

    print(f"\nFinished. Migrated {migrated_count} records.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
