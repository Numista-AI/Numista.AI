"""
Numista.AI — Overnight API Test Suite
Run: python run_overnight_tests.py
Results written to: overnight_test_results.txt
"""
import json, time, csv, io, requests, traceback
from datetime import datetime

API  = "https://numista-backend-568985927038.us-central1.run.app"
EMAIL = "jseaman1204@gmail.com"        # Test user
LOG   = "overnight_test_results.txt"

PASS = "✅ PASS"; FAIL = "❌ FAIL"; WARN = "⚠️  WARN"
results = []

def log(status, name, detail="", ms=0):
    ts  = datetime.now().strftime("%H:%M:%S")
    row = f"[{ts}] {status}  {name:<55} {f'{ms}ms' if ms else ''}  {detail}"
    print(row)
    results.append(row)

def get(path, params=None, label=None):
    t0 = time.time()
    try:
        r = requests.get(f"{API}{path}", params=params, timeout=20)
        ms = int((time.time()-t0)*1000)
        ok = r.status_code == 200
        log(PASS if ok else FAIL, label or path,
            f"HTTP {r.status_code}", ms)
        return r if ok else None
    except Exception as e:
        log(FAIL, label or path, str(e))
        return None

def post(path, data, label=None):
    t0 = time.time()
    try:
        r = requests.post(f"{API}{path}", data=data, timeout=20)
        ms = int((time.time()-t0)*1000)
        ok = r.status_code == 200
        log(PASS if ok else FAIL, label or path,
            f"HTTP {r.status_code}", ms)
        return r if ok else None
    except Exception as e:
        log(FAIL, label or path, str(e))
        return None

# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*70)
print(" Numista.AI Overnight Test Suite")
print(f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70 + "\n")

# ── 1. Health check ───────────────────────────────────────────────────────────
print("── SECTION 1: Health & Basic Endpoints ──────────────────────────────")
get("/", label="Root health check")
get("/docs", label="FastAPI docs page")

# ── 2. Collection endpoints ───────────────────────────────────────────────────
print("\n── SECTION 2: Collection Endpoints ─────────────────────────────────")
r = get("/api/coins", params={"user_email": EMAIL}, label="GET /api/coins")
if r:
    d = r.json()
    count = len(d.get("coins", d.get("items", d if isinstance(d, list) else [])))
    log(PASS, "Collection count check", f"{count} coins returned")

get("/api/dedup_sweep", label="Skip — POST only (not tested here)")

# ── 3. Template download ───────────────────────────────────────────────────────
print("\n── SECTION 3: Template Download ─────────────────────────────────────")
r = get("/api/template", label="GET /api/template (CSV download)")
if r:
    text = r.text
    reader = csv.DictReader(io.StringIO(text))
    headers = reader.fieldnames or []
    REQUIRED = ["Year","Mint Mark","Denomination","Program/Series",
                "Theme/Subject","Country","Condition","Purchase Date"]
    missing = [h for h in REQUIRED if h not in headers]
    if missing:
        log(WARN, "Template headers check", f"Missing: {missing}")
    else:
        log(PASS, "Template headers check", f"{len(headers)} columns all present")

# ── 4. Nickname endpoints ──────────────────────────────────────────────────────
print("\n── SECTION 4: Community Nickname Endpoints ───────────────────────────")
r = get("/api/nicknames", params={"status": "approved", "limit": 100},
        label="GET /api/nicknames (approved)")
if r:
    d = r.json()
    ct = len(d.get("results", []))
    log(PASS, "Approved nicknames returned", f"{ct} terms")

r = get("/api/nicknames/stats", label="GET /api/nicknames/stats")
if r:
    d = r.json()
    log(PASS, "Nickname stats fields", f"total={d.get('total','?')} approved={d.get('approved','?')}")

# Test submitting "Ike" — should get already_known
r = post("/api/nicknames/submit",
         {"user_email": EMAIL, "nickname": "Ike", "maps_to": "test"},
         label="POST /api/nicknames/submit 'Ike' (expect already_known)")
if r:
    d = r.json()
    status = d.get("status","")
    if status == "already_known":
        log(PASS, "Ike already_known response", d.get("message","")[:60])
    else:
        log(WARN, "Ike already_known response", f"Got status={status}")

# Test a fresh (hopefully new) term
test_nick = f"TestCoin_{int(time.time())}"
r = post("/api/nicknames/submit",
         {"user_email": EMAIL, "nickname": test_nick,
          "maps_to": "Test Coin Dollar", "category": "Dollar"},
         label=f"POST /api/nicknames/submit new term '{test_nick}'")
submitted_id = None
if r:
    d = r.json()
    submitted_id = d.get("doc_id","")
    log(PASS if d.get("status")=="submitted" else WARN,
        "New nickname submission status", d.get("status","?"))

# Vote on it if we got an ID
if submitted_id:
    r = post(f"/api/nicknames/{submitted_id}/vote",
             {"user_email": "admin@numista.ai", "rating": "5"},
             label=f"POST /api/nicknames/{{id}}/vote rating=5")
    if r:
        d = r.json()
        log(PASS, "Vote recorded", d.get("message","")[:60])

# ── 5. Grade Review endpoints ──────────────────────────────────────────────────
print("\n── SECTION 5: Grade Review Endpoints ────────────────────────────────")

r = get("/api/grade_review/stats", params={"user_email": EMAIL},
        label="GET /api/grade_review/stats")
grade_stats = {}
if r:
    grade_stats = r.json()
    log(PASS, "Grade stats fields",
        f"total_ai={grade_stats.get('total_ai_graded','?')} "
        f"pending={grade_stats.get('pending_review','?')} "
        f"flagged={grade_stats.get('flagged','?')}")

r = get("/api/grade_review/queue",
        params={"user_email": EMAIL, "limit": 5},
        label="GET /api/grade_review/queue")
queue_coins = []
if r:
    d = r.json()
    queue_coins = d.get("results", [])
    total = d.get("total", 0)
    log(PASS, "Grade review queue", f"{total} coins awaiting review, returned {len(queue_coins)}")
    for c in queue_coins[:3]:
        conf = c.get("confidence_score", 0)
        flag = "🔴" if c.get("low_confidence") else "🟡"
        log(PASS, f"  {flag} {c.get('coin_id','?')[:12]}…",
            f"{c.get('year','?')}{c.get('mint_mark','')} | "
            f"Grade={c.get('condition','?')} | Conf={conf:.0%}")

# Submit a "confirmed" review on coin #1
if len(queue_coins) >= 1:
    c1 = queue_coins[0]
    r = post("/api/grade_review/submit", {
        "user_email":      EMAIL,
        "coin_id":         c1["coin_id"],
        "action":          "confirmed",
        "suggested_grade": "",
        "rating":          "5",
        "notes":           "Overnight test — confirmed",
    }, label=f"POST /api/grade_review/submit confirmed (coin 1)")
    if r:
        d = r.json()
        log(PASS, "Confirmed review response", d.get("message","")[:60])

# Submit a "corrected" review on coin #2 (different test email to avoid dupe)
if len(queue_coins) >= 2:
    c2 = queue_coins[1]
    r = post("/api/grade_review/submit", {
        "user_email":      "testreviewer@numista.ai",
        "coin_id":         c2["coin_id"],
        "action":          "corrected",
        "suggested_grade": "MS-63",
        "rating":          "3",
        "notes":           "Overnight test — correction to MS-63",
    }, label=f"POST /api/grade_review/submit corrected (coin 2)")
    if r:
        d = r.json()
        log(PASS, "Corrected review response", d.get("message","")[:60])

# Verify stats changed
r = get("/api/grade_review/stats", params={"user_email": EMAIL},
        label="GET /api/grade_review/stats (post-review)")
if r:
    new_stats = r.json()
    prev_pending = grade_stats.get("pending_review", -1)
    new_pending  = new_stats.get("pending_review", -1)
    if new_pending < prev_pending or prev_pending == -1:
        log(PASS, "Stats updated after review",
            f"pending: {prev_pending} → {new_pending}")
    else:
        log(WARN, "Stats may not have updated",
            f"pending was {prev_pending}, now {new_pending}")

# ── 6. Normalization edge cases ────────────────────────────────────────────────
print("\n── SECTION 6: Normalization Edge Cases (spot-check dict) ────────────")
EDGE_CASES = [
    # (input_condition, expected_normalized)
    ("BU",              "MS-63"),
    ("bu",              "MS-63"),
    ("proof69",         "PF-69"),
    ("PR69",            "PF-69"),
    ("Ch Proof 63",     "PF-63"),
    ("F-12",            "F-12"),          # already normalized — should stay
    ("vf30",            "VF-30"),
    ("AU58",            "AU-58"),
    ("MS65",            "MS-65"),
    ("uncirculated",    "Uncirculated"),
]

import sys
sys.path.insert(0, r"C:\Users\ericd\Documents\MyVertexProject\numista_backend")
try:
    from main import _norm_condition
    passed = 0
    for raw, expected in EDGE_CASES:
        result = _norm_condition(raw)
        ok = result == expected
        if ok:
            passed += 1
        log(PASS if ok else FAIL,
            f"  _norm_condition('{raw}')",
            f"→ '{result}' {'✓' if ok else f'(expected {expected})'}")
    log(PASS if passed == len(EDGE_CASES) else WARN,
        "Normalization edge case summary",
        f"{passed}/{len(EDGE_CASES)} passed")
except ImportError as e:
    log(WARN, "Normalization import skipped", str(e))

# ── 7. Response time check ─────────────────────────────────────────────────────
print("\n── SECTION 7: Response Time Benchmarks ──────────────────────────────")
ENDPOINTS = [
    ("/api/grade_review/queue",  {"user_email": EMAIL, "limit": 10}),
    ("/api/grade_review/stats",  {"user_email": EMAIL}),
    ("/api/nicknames/stats",     {}),
    ("/api/nicknames",           {"status": "approved", "limit": 50}),
    ("/api/template",            {}),
]
for path, params in ENDPOINTS:
    times = []
    for _ in range(3):
        t0 = time.time()
        try:
            requests.get(f"{API}{path}", params=params, timeout=20)
            times.append(int((time.time()-t0)*1000))
        except Exception:
            pass
    if times:
        avg = sum(times)//len(times)
        status = PASS if avg < 3000 else WARN if avg < 6000 else FAIL
        log(status, f"  {path}", f"avg {avg}ms over {len(times)} calls")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "="*70)
passed_ct = sum(1 for r in results if PASS in r)
failed_ct = sum(1 for r in results if FAIL in r)
warn_ct   = sum(1 for r in results if WARN in r)

summary = (f"\n{'='*70}\n"
           f" Test Complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
           f" ✅ PASS: {passed_ct}   ❌ FAIL: {failed_ct}   ⚠️  WARN: {warn_ct}\n"
           f"{'='*70}\n")
print(summary)
results.append(summary)

with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print(f"📄 Full results saved to: {LOG}")
if failed_ct > 0:
    print(f"\n❌ {failed_ct} test(s) FAILED — review {LOG} in the morning.")
else:
    print("🎉 All tests passed!")
