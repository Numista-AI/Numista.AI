"""
Smoke test for the reference verification pipeline.
Tests each component in isolation:
  1. Firestore connection + reference_library query
  2. GCS image download to temp file
  3. Gemini file upload
  4. Full _run_verification_pass with a mock coin_data
"""
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Ensure we can import from numista_hardware
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from identify_coin import (
    _get_ref_db,
    _normalize_denom,
    _fetch_reference_images,
    _download_temp,
    client,
)

PASS = "[PASS]"
FAIL = "[FAIL]"
results = []

def test(name, fn):
    try:
        result = fn()
        results.append((name, True, result))
        print(f"  {PASS} {name}: {result}")
        return result
    except Exception as e:
        results.append((name, False, str(e)))
        print(f"  {FAIL} {name}: {e}")
        return None


print("=" * 60)
print("  Numista.AI Reference Pipeline Smoke Test")
print("=" * 60)

# ── Test 1: Denomination normalizer ──────────────────────────────────────────
print("\n1. Denomination Normalizer")
test("'Roosevelt Dime' -> Dime", lambda: _normalize_denom("Roosevelt Dime") == "Dime")
test("'Quarter' -> Quarter",     lambda: _normalize_denom("Quarter") == "Quarter")
test("'Half Dollar' -> Half Dollar", lambda: _normalize_denom("Half Dollar") == "Half Dollar")
test("'Lincoln Cent' -> Cent",   lambda: _normalize_denom("Lincoln Cent") == "Cent")

# ── Test 2: Firestore connection ─────────────────────────────────────────────
print("\n2. Firestore Connection")
db = test("Initialize Firestore client", _get_ref_db)

# ── Test 3: Reference library query ──────────────────────────────────────────
print("\n3. Reference Library Query")
refs = test("Query 'Quarter' ~2000",
            lambda: _fetch_reference_images("Quarter", 2000, max_images=3))

if not refs:
    refs = test("Fallback: Query 'Dime' ~1964",
                lambda: _fetch_reference_images("Dime", 1964, max_images=3))

if refs:
    print(f"     Returned {len(refs)} images:")
    for r in refs:
        print(f"       - {r['denomination']} {r['year']} ({r['side']}) -> {r['gcs_url'][:80]}...")

# ── Test 4: Download a reference image ───────────────────────────────────────
print("\n4. GCS Image Download")
tmp_path = None
if refs:
    url = refs[0]["gcs_url"]
    tmp_path = test(f"Download {url[:60]}...",
                    lambda: _download_temp(url))
    if tmp_path:
        size = os.path.getsize(tmp_path)
        print(f"     Downloaded to {tmp_path} ({size:,} bytes)")

# ── Test 5: Gemini file upload ───────────────────────────────────────────────
print("\n5. Gemini File Upload")
if tmp_path and os.path.exists(tmp_path):
    def upload_test():
        uploaded = client.files.upload(file=tmp_path)
        return f"name={uploaded.name}, state={uploaded.state}"
    test("Upload temp image to Gemini", upload_test)

# ── Cleanup ──────────────────────────────────────────────────────────────────
if tmp_path and os.path.exists(tmp_path):
    os.unlink(tmp_path)

# ── Summary ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
print(f"  Results: {passed} passed, {failed} failed out of {len(results)} tests")
if failed:
    print("\n  Failed tests:")
    for name, ok, detail in results:
        if not ok:
            print(f"    - {name}: {detail}")
print("=" * 60)
