"""
cert_scraper_step1.py  –  STEP 1
Query all currency documents and extract PMG / PCGS cert numbers.

Outputs a JSON file: cert_hits.json  ready for Step 2.
"""
import os, re, sys, json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KEY_PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serviceAccountKey.json.json")
USER_EMAIL = "jseaman1204@gmail.com"
COLLECTION = f"users/{USER_EMAIL}/currency"
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", KEY_PATH)

import firebase_admin
from firebase_admin import credentials, firestore as fs_admin

try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(credentials.Certificate(KEY_PATH))

db = fs_admin.client()

# ── regex patterns ────────────────────────────────────────────────────────────
PMG_EXPLICIT   = re.compile(r'\bPMG\b[\s\-#]*([0-9]{6,10})\b', re.IGNORECASE)
PCGS_EXPLICIT  = re.compile(r'\bPCGS\b[\s\-#]*([0-9]{6,10})\b', re.IGNORECASE)
CERT_NO_LABEL  = re.compile(r'Cert(?:\.?\s*(?:No\.?|#))?\s*[:=]?\s*([0-9]{6,10})\b', re.IGNORECASE)
HASH_CERT      = re.compile(r'#\s*([0-9]{6,10})\b')   # generic  #12345678
SERIAL_LABEL   = re.compile(r'(?:Serial|Cert|Cert\.?)\s*[:=#]\s*([0-9]{6,10})\b', re.IGNORECASE)
PCGS_CERT_NO   = re.compile(r'PCGS\s+Cert(?:ified)?\s+No\.?\s*([0-9]{6,10})\b', re.IGNORECASE)
PMG_CERT_NO    = re.compile(r'PMG\s+Cert(?:ified)?\s+No\.?\s*([0-9]{6,10})\b', re.IGNORECASE)

# Dedicated field names to probe
CERT_FIELD_NAMES = [
    "cert_number", "Cert #", "Cert#", "PMG_cert", "pcgs_cert",
    "pmg_cert_number", "pcgs_cert_number", "cert_no", "certNumber",
    "pmg_cert", "pcgs_number",
]

def extract_cert(doc_id, data):
    """Return list of (cert_number, service) tuples for a single document."""
    hits = []

    # ── 1. Check dedicated fields first ──────────────────────────────────────
    for fname in CERT_FIELD_NAMES:
        val = data.get(fname)
        if val and str(val).strip():
            digits = re.search(r'([0-9]{6,10})', str(val))
            if digits:
                service = "PCGS" if "pcgs" in fname.lower() else "PMG"
                hits.append((digits.group(1), service, f"field:{fname}"))

    # ── 2. Scan Description text ──────────────────────────────────────────────
    desc = str(data.get("Description") or "")
    desc_lower = desc.lower()

    # Detect which services appear in the description
    has_pmg  = "pmg" in desc_lower or "paper money guaranty" in desc_lower
    has_pcgs = "pcgs" in desc_lower

    # PMG patterns
    for m in PMG_EXPLICIT.finditer(desc):
        hits.append((m.group(1), "PMG", "PMG explicit"))
    for m in PMG_CERT_NO.finditer(desc):
        hits.append((m.group(1), "PMG", "PMG Cert No"))

    # PCGS patterns
    for m in PCGS_EXPLICIT.finditer(desc):
        hits.append((m.group(1), "PCGS", "PCGS explicit"))
    for m in PCGS_CERT_NO.finditer(desc):
        hits.append((m.group(1), "PCGS", "PCGS Cert No"))

    # Generic "Cert No. 12345678" – attribute to whichever service appears nearby
    for m in CERT_NO_LABEL.finditer(desc):
        cert = m.group(1)
        # Peek 80 chars around the match for context
        ctx_start = max(0, m.start() - 80)
        ctx_end   = min(len(desc), m.end() + 80)
        ctx       = desc[ctx_start:ctx_end].lower()
        svc = "PMG" if "pmg" in ctx or "paper money" in ctx else ("PCGS" if "pcgs" in ctx else ("PMG" if has_pmg else ("PCGS" if has_pcgs else "UNKNOWN")))
        hits.append((cert, svc, "Cert label"))

    # Generic Serial / #XXXXXXXX near a service name
    for m in SERIAL_LABEL.finditer(desc):
        cert = m.group(1)
        ctx_start = max(0, m.start() - 80)
        ctx_end   = min(len(desc), m.end() + 80)
        ctx       = desc[ctx_start:ctx_end].lower()
        svc = "PMG" if "pmg" in ctx or "paper money" in ctx else ("PCGS" if "pcgs" in ctx else ("PMG" if has_pmg else "UNKNOWN"))
        hits.append((cert, svc, "Serial label"))

    # # XXXXXXX near a service name
    if has_pmg or has_pcgs:
        for m in HASH_CERT.finditer(desc):
            cert = m.group(1)
            ctx_start = max(0, m.start() - 120)
            ctx_end   = min(len(desc), m.end() + 120)
            ctx       = desc[ctx_start:ctx_end].lower()
            if "pmg" in ctx or "paper money" in ctx:
                hits.append((cert, "PMG", "hash cert near PMG"))
            elif "pcgs" in ctx:
                hits.append((cert, "PCGS", "hash cert near PCGS"))

    # De-duplicate (same cert+service)
    seen = set()
    deduped = []
    for cert, svc, reason in hits:
        key = (cert, svc)
        if key not in seen:
            seen.add(key)
            deduped.append((cert, svc, reason))

    return deduped


# ── Main ──────────────────────────────────────────────────────────────────────
print("Querying Firestore ...")
raw_docs = list(db.collection(COLLECTION).stream())
print(f"  → {len(raw_docs)} documents fetched")

all_hits  = []
all_keys  = set()
no_cert   = []

for doc in raw_docs:
    doc_id = doc.id
    data   = doc.to_dict() or {}
    all_keys.update(data.keys())

    certs = extract_cert(doc_id, data)

    desc = str(data.get("Description") or "")

    if certs:
        for cert, svc, reason in certs:
            entry = {
                "doc_id":       doc_id,
                "cert_number":  cert,
                "service":      svc,
                "reason":       reason,
                "description":  desc,
                "fields":       {k: str(v)[:200] for k, v in data.items()},
            }
            all_hits.append(entry)
            print(f"  ✓ {doc_id[:30]:<32}  {svc:<5}  #{cert}  ({reason})")
    else:
        no_cert.append(doc_id)

print(f"\n{'='*70}")
print(f"STEP 1 SUMMARY")
print(f"{'='*70}")
print(f"  Total docs scanned : {len(raw_docs)}")
print(f"  Cert hits found    : {len(all_hits)}")
print(f"  No cert found      : {len(no_cert)}")
print(f"\nUnique field keys across all docs:")
for k in sorted(all_keys):
    count = sum(1 for doc in raw_docs
                if (doc.to_dict() or {}).get(k) not in (None, "", []))
    print(f"  {k:<35} ({count}/{len(raw_docs)} docs)")

# Save for Step 2
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cert_hits.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(all_hits, f, indent=2, ensure_ascii=False)
print(f"\n→ Saved {len(all_hits)} hits to: {out_path}")

# Print first 10 full records for inspection
print(f"\n=== FIRST 10 CERT HITS (DETAILED) ===")
for h in all_hits[:10]:
    print(f"\nDoc: {h['doc_id']}")
    print(f"  Cert: #{h['cert_number']}  Service: {h['service']}  Reason: {h['reason']}")
    print(f"  Description: {h['description'][:200]!r}")
