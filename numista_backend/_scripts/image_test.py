# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""Quick image test for the binder scan endpoint."""
import requests, json, time, pathlib, base64, io

PROD = "https://numista-backend-568985927038.us-central1.run.app"
EMAIL = "eric@numista.ai"

print("=== NUMISTA.AI Binder Scan Image Test ===")

# Create a simple test image (white JPEG) as a minimal proxy
# In real use, the user would upload actual binder photos
from PIL import Image
img = Image.new("RGB", (640, 480), color=(200, 200, 200))
buf = io.BytesIO()
img.save(buf, format="JPEG", quality=85)
test_jpeg = buf.getvalue()
print(f"Created test image: {len(test_jpeg)//1024}KB")

print("\n[1] Testing /api/analyze_binder_scan with synthetic test image ...")
t0 = time.time()
try:
    resp = requests.post(
        f"{PROD}/api/analyze_binder_scan",
        data={"user_email": EMAIL, "binder_title": "50 State Commemorative Quarters Test"},
        files=[("images", ("test_binder_page.jpg", test_jpeg, "image/jpeg"))],
        timeout=120
    )
    elapsed = time.time() - t0
    print(f"    HTTP {resp.status_code} in {elapsed:.1f}s")
    if resp.status_code == 200:
        r = resp.json()
        print(f"    Book Title   : {r.get('book_title', 'N/A')}")
        print(f"    Total Slots  : {r.get('total_slots', 0)}")
        print(f"    Present      : {r.get('present_count', 0)}")
        print(f"    GCS URLs     : {r.get('image_gcs_urls', [])}")
        print("    PASS")
    else:
        print(f"    FAIL: {resp.text[:500]}")
except requests.exceptions.Timeout:
    elapsed = time.time() - t0
    print(f"    TIMEOUT after {elapsed:.0f}s")
except Exception as e:
    print(f"    ERROR: {e}")
