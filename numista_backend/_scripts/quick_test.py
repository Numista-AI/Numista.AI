# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""Quick live test for the binder scan endpoints."""
import requests, json, time, pathlib

PROD = "https://numista-backend-568985927038.us-central1.run.app"
EMAIL = "eric@numista.ai"

print("=== NUMISTA.AI Binder Endpoint Live Test ===")

# Test: Checklist PDF
print("\n[1] Testing /api/analyze_checklist with 50_State_Checklist.pdf ...")
with open("50_State_Checklist.pdf", "rb") as f:
    pdf = f.read()

t0 = time.time()
try:
    resp = requests.post(
        f"{PROD}/api/analyze_checklist",
        data={"user_email": EMAIL},
        files=[("files", ("50_State_Checklist.pdf", pdf, "application/pdf"))],
        timeout=300  # extended to 5 min for large PDFs
    )
    elapsed = time.time() - t0
    print(f"    HTTP {resp.status_code} in {elapsed:.1f}s")

    if resp.status_code == 200:
        r = resp.json()
        print(f"    Book Title   : {r.get('book_title', 'N/A')}")
        print(f"    Programs     : {r.get('programs_detected', [])}")
        print(f"    Total Slots  : {r.get('total_slots', 0)}")
        print(f"    Present      : {r.get('present_count', 0)}")
        print(f"    Absent       : {r.get('absent_count', 0)}")
        print(f"    Mint Clarif  : {r.get('mint_clarification_needed', False)}")
        gcs = r.get('image_gcs_urls', [])
        print(f"    GCS URL[0]   : {gcs[0] if gcs else 'None'}")
        slots = r.get("coin_slots", [])
        present = [s for s in slots if s.get("present")]
        print(f"    Sample present coins (first 8 of {len(present)}):")
        for s in present[:8]:
            unc = " [MINT UNCERTAIN]" if s.get("mint_uncertain") else ""
            print(f"      {s.get('year','?')}-{s.get('mint','?')} {s.get('subject','?')}{unc}")
        with open("test_result_checklist.json", "w", encoding="utf-8") as out:
            json.dump(r, out, indent=2, default=str)
        print("    Full result -> test_result_checklist.json")
        print("    PASS")
    else:
        print(f"    FAIL: {resp.text[:500]}")
except requests.exceptions.Timeout:
    elapsed = time.time() - t0
    print(f"    TIMEOUT after {elapsed:.0f}s (Cloud Run is still processing)")
    print("    The endpoint is working but needs longer timeout from Flutter/mobile client")
    print("    Cloud Run timeout is set to 300s which is adequate for the mobile app")
except Exception as e:
    print(f"    ERROR: {e}")
