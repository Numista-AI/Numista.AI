# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
test_binder_scan.py — Phase 1 local validation test.

Tests the /api/analyze_binder_scan endpoint against the two binder photos
provided by the user (Alternate Mint page and US Map page).

Usage:
    python test_binder_scan.py --local          # Tests against local uvicorn (port 8080)
    python test_binder_scan.py --prod           # Tests against Cloud Run endpoint
    python test_binder_scan.py --image path1 path2  # Custom image paths

The test saves results to binder_scan_test_result.json for inspection.
"""

import argparse
import json
import sys
import time
import requests
from pathlib import Path

LOCAL_URL  = "http://localhost:8080"
PROD_URL   = "https://numista-backend-568985927038.us-central1.run.app"
TEST_EMAIL = "eric@numista.ai"

def run_test(base_url: str, image_paths: list[str]):
    endpoint = f"{base_url}/api/analyze_binder_scan"
    print(f"\n{'='*60}")
    print(f"  NUMISTA.AI — Binder Scan Endpoint Test")
    print(f"  Endpoint : {endpoint}")
    print(f"  Images   : {image_paths}")
    print(f"{'='*60}\n")

    # Build multipart form
    files  = []
    opened = []
    for path in image_paths:
        p = Path(path)
        if not p.exists():
            print(f"  ⚠️  Image not found: {path} — skipping")
            continue
        suffix = p.suffix.lower()
        mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}.get(suffix, "image/jpeg")
        fh = open(p, "rb")
        opened.append(fh)
        files.append(("images", (p.name, fh, mime)))

    if not files:
        print("  ❌ No valid images found. Aborting.")
        sys.exit(1)

    data = {
        "user_email": TEST_EMAIL,
    }

    print(f"  📤 Sending {len(files)} image(s) to backend...")
    t0 = time.time()

    try:
        resp = requests.post(endpoint, data=data, files=files, timeout=120)
        elapsed = time.time() - t0
    finally:
        for fh in opened:
            fh.close()

    print(f"  ⏱️  Response in {elapsed:.1f}s  |  HTTP {resp.status_code}")

    if resp.status_code != 200:
        print(f"\n  ❌ Error response:\n{resp.text[:2000]}")
        sys.exit(1)

    result = resp.json()

    # ── Print summary ─────────────────────────────────────────────────────────
    print(f"\n  📖 Book Title     : {result.get('book_title', 'N/A')}")
    print(f"  📋 Programs       : {result.get('programs_detected', [])}")
    print(f"  🪙  Total Slots    : {result.get('total_slots', 0)}")
    print(f"  ✅  Coins Present  : {result.get('present_count', 0)}")
    print(f"  🔴  Coins Absent   : {result.get('absent_count', 0)}")
    print(f"  🆕  New Coins      : {len(result.get('new_coins', []))}")
    print(f"  ❓  Mint Clarif.   : {result.get('mint_clarification_needed', False)}")
    print(f"\n  Notes: {result.get('analysis_notes', 'None')[:200]}")

    # ── Page breakdown ────────────────────────────────────────────────────────
    print(f"\n  {'─'*50}")
    print(f"  PAGE ANALYSIS:")
    for page in result.get("pages", []):
        print(f"    Page {page.get('page_index', '?'):>2} | "
              f"Type: {page.get('page_type', '?'):<22} | "
              f"Mint: {page.get('mint_assigned', '?')} ({page.get('mint_confidence', '?')}) | "
              f"Slots: {page.get('slots_detected', '?')}")
        print(f"           Reasoning: {page.get('mint_reasoning', '')[:80]}")

    # ── Sample present coins ──────────────────────────────────────────────────
    present = [s for s in result.get("coin_slots", []) if s.get("present")]
    absent  = [s for s in result.get("coin_slots", []) if not s.get("present")]

    print(f"\n  {'─'*50}")
    print(f"  SAMPLE PRESENT COINS (first 10 of {len(present)}):")
    for s in present[:10]:
        warn = " ⚠️ MINT UNCERTAIN" if s.get("mint_uncertain") else ""
        note = f" | {s.get('slot_condition_note', '')}" if s.get("slot_condition_note") else ""
        print(f"    {s.get('year','?')}-{s.get('mint','?')} {s.get('subject','?')}{warn}{note}")

    print(f"\n  SAMPLE ABSENT COINS (first 10 of {len(absent)}):")
    for s in absent[:10]:
        print(f"    {s.get('year','?')}-{s.get('mint','?')} {s.get('subject','?')}")

    # ── Validation warnings ───────────────────────────────────────────────────
    warnings = [s for s in result.get("coin_slots", []) if s.get("validation_warning")]
    if warnings:
        print(f"\n  ⚠️  VALIDATION WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    {w.get('year','?')} {w.get('subject','?')}: {w.get('validation_warning','')}")

    # ── Save full result ───────────────────────────────────────────────────────
    out_path = Path("binder_scan_test_result.json")
    out_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(f"\n  💾 Full result saved to: {out_path.absolute()}")
    print(f"\n  {'='*60}")
    print(f"  ✅ Test PASSED — endpoint responded successfully.")
    print(f"  {'='*60}\n")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the binder scan endpoint.")
    parser.add_argument("--local",  action="store_true", help="Test against local server")
    parser.add_argument("--prod",   action="store_true", help="Test against Cloud Run")
    parser.add_argument("--images", nargs="+", metavar="PATH", help="Image file paths")
    args = parser.parse_args()

    base_url = LOCAL_URL if args.local else PROD_URL

    if args.images:
        image_paths = args.images
    else:
        # Default: look for binder test images in the current directory
        candidates = [
            "test_binder_alternate_mint.jpg",
            "test_binder_map.jpg",
        ]
        image_paths = [p for p in candidates if Path(p).exists()]
        if not image_paths:
            print("No test images specified and no default test images found.")
            print("Usage: python test_binder_scan.py --image path/to/page1.jpg path/to/page2.jpg")
            print("       python test_binder_scan.py --local --image page1.jpg page2.jpg")
            sys.exit(1)

    run_test(base_url, image_paths)
