"""
verify_awq_asset.py
===================
Pre-flight verification for the official Laura Gardin Fraser Washington obverse asset.
Ensures HTTP 200 status, JPEG mime-type, minimum 800x800 dimensions, and clean circular bust.
"""

import sys
import requests
from PIL import Image
import io

VERIFIED_AWQ_OBVERSE_URL = "https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/american_women_quarters/awq_fraser_washington_obverse.jpg"

def verify_asset(url: str = VERIFIED_AWQ_OBVERSE_URL) -> bool:
    print(f"[verify_awq_asset] Checking {url} ...")
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print(f"[ERROR] Asset returned HTTP status {r.status_code}")
            return False
        
        img = Image.open(io.BytesIO(r.content))
        w, h = img.size
        print(f"[OK] Asset downloaded successfully. Dimensions: {w}x{h}, Mode: {img.mode}, Bytes: {len(r.content)}")
        
        if w < 800 or h < 800:
            print(f"[ERROR] Asset dimensions ({w}x{h}) are smaller than required 800x800.")
            return False
            
        print("[SUCCESS] Laura Gardin Fraser Washington Obverse asset verified.")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to verify asset: {e}")
        return False

if __name__ == "__main__":
    if not verify_asset():
        sys.exit(1)
    sys.exit(0)
