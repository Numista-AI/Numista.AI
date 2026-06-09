"""
test_routing.py  --  Verify item_type routing on problem invoices
Run: python test_routing.py
"""
import requests, json, time, sys, os

API      = "https://numista-backend-568985927038.us-central1.run.app"
EMAIL    = "test@numista.ai"
SCAN_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Scans AJ June 2026"

TARGETS = [
    {
        "file":         "Receipt_2026-06-03_102331.pdf",
        "label":        "STAMP TEST (West Point stamp)",
        "expect_stamp": True,
        "expect_set":   False,
    },
    {
        "file":         "Receipt_2026-06-03_092205.pdf",
        "label":        "SET TEST   (Ike Set auto-expand)",
        "expect_stamp": False,
        "expect_set":   True,
    },
    {
        "file":         "Receipt_2026-06-03_102135.pdf",
        "label":        "MIXED TEST (supplies + coins)",
        "expect_stamp": False,
        "expect_set":   False,
    },
    {
        "file":         "Receipt_2026-06-03_101410.pdf",
        "label":        "REGRESSION (clean coin invoice)",
        "expect_stamp": False,
        "expect_set":   False,
    },
]

results = {"pass": 0, "fail": 0, "warn": 0}

def check(label, ok, msg):
    if ok is True:
        tag = "[PASS]"; results["pass"] += 1
    elif ok is False:
        tag = "[FAIL]"; results["fail"] += 1
    else:
        tag = "[WARN]"; results["warn"] += 1
    print(f"      {tag}  {label}  --  {msg}")


print()
print("=" * 65)
print(f"  Numista.AI -- Item Routing Verification  {time.strftime('%H:%M:%S')}")
print("=" * 65)

for t in TARGETS:
    path = os.path.join(SCAN_DIR, t["file"])
    if not os.path.exists(path):
        print(f"\n  [SKIP] {t['file']} not found\n")
        results["warn"] += 1
        continue

    size_mb = os.path.getsize(path) / 1_048_576
    print(f"\n  Submitting: {t['file']}  ({size_mb:.1f} MB) ...")
    start = time.time()

    try:
        with open(path, "rb") as f:
            resp = requests.post(
                f"{API}/api/process_invoice",
                data={"user_email": EMAIL},
                files={"file": (t["file"], f, "application/pdf")},
                timeout=300,   # 5-minute timeout per file
            )
        elapsed = int(time.time() - start)

        if resp.status_code != 200:
            check(t["label"], False, f"HTTP {resp.status_code}: {resp.text[:200]}")
            print("  " + "-" * 63)
            continue

        j = resp.json()
        print()
        print(f"  --- {t['label']} ({elapsed}s) ---")
        print(f"      status:           {j.get('status')}")
        print(f"      extracted_items:  {j.get('extracted_items', 0)}")
        print(f"      set_records:      {j.get('set_records', 0)}")
        print(f"      set_coins_inside: {j.get('set_coins_inside', 0)}")
        print(f"      pending_items:    {j.get('pending_items', 0)}   (stamps)")
        print(f"      supplies_logged:  {j.get('supplies_logged', 0)}")

        # Item type breakdown
        data = j.get("data", [])
        if data:
            from collections import Counter
            counts = Counter(item.get("item_type", "unknown") for item in data)
            print(f"      item_type breakdown: {dict(counts)}")
        print()

        # ── STAMP checks ──────────────────────────────────────────────
        if t["expect_stamp"]:
            check("Stamp routed to pending_items",
                  j.get("pending_items", 0) > 0,
                  f"pending_items={j.get('pending_items',0)} (expect >0)")

            misfire = [
                item for item in data
                if item.get("item_type") == "coin"
                and "1937" in str(item.get("Year", ""))
                and any(kw in str(item.get("Denomination","")).lower()
                        for kw in ["nickel","buffalo","5c","5 cent"])
            ]
            check("1937 West Point NOT misclassified as coin",
                  len(misfire) == 0,
                  "Not in coin list" if not misfire
                  else f"STILL a coin: {misfire[0].get('Denomination')}")

            stamp_items = [d for d in data if d.get("item_type") == "stamp"]
            check("item_type=stamp present in response data",
                  len(stamp_items) > 0 or j.get("pending_items", 0) > 0,
                  f"{len(stamp_items)} stamp(s) in data, {j.get('pending_items',0)} pending")

        # ── SET checks ────────────────────────────────────────────────
        if t["expect_set"]:
            check("Set records detected",
                  j.get("set_records", 0) > 0,
                  f"set_records={j.get('set_records',0)} (expect >0)")

            check("set_coins_inside >= 8",
                  j.get("set_coins_inside", 0) >= 8,
                  f"set_coins_inside={j.get('set_coins_inside',0)}")

            set_items = [d for d in data if d.get("item_type") == "set"]
            for si in set_items:
                contents = si.get("set_contents") or []
                denom = si.get("Denomination") or si.get("Theme/Subject") or "(no denom)"
                check(f"Set '{denom[:40]}' has set_contents",
                      len(contents) > 0,
                      f"{len(contents)} coins in set_contents")
                check(f"Set '{denom[:40]}' has set_cost_label",
                      bool(si.get("set_cost_label")),
                      f"set_cost_label={si.get('set_cost_label')}")

        # ── REGRESSION checks ─────────────────────────────────────────
        if not t["expect_stamp"] and not t["expect_set"]:
            check("Coins extracted (regression)",
                  j.get("extracted_items", 0) > 0,
                  f"extracted_items={j.get('extracted_items',0)}")
            check("No spurious stamps/pending",
                  j.get("pending_items", 0) == 0,
                  f"pending_items={j.get('pending_items',0)}")

    except requests.Timeout:
        elapsed = int(time.time() - start)
        check(t["label"], False, f"TIMEOUT after {elapsed}s (>300s)")
    except Exception as e:
        check(t["label"], False, str(e))

    print("  " + "-" * 63)

print()
print("=" * 65)
print(f"  PASS: {results['pass']}   FAIL: {results['fail']}   WARN: {results['warn']}")
print("=" * 65)
print()
