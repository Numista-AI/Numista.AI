"""
build_search_queries.py  – Builds Heritage Auctions search URLs for all 32 graded docs.
Run this to get a list of (doc_id, service, ref_num, description, search_url) tuples.
"""
import json, re, os
from urllib.parse import quote_plus

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(SCRIPT_DIR, "graded_docs.json"), encoding="utf-8") as f:
    graded = json.load(f)

def build_query(data):
    desc  = str(data.get("Description", ""))
    year  = str(data.get("Year", ""))
    denom = str(data.get("Denomination", ""))
    noise = re.compile(r'\b(PMG|PCGS|PPQ|EPQ|EDQ|large|size|previously|mounted|consecutive|serial|numbers?)\b', re.IGNORECASE)
    clean = noise.sub(" ", desc)
    clean = re.sub(r'\s{2,}', ' ', clean).strip()[:60]
    parts = []
    if year: parts.append(year)
    parts.append(clean)
    return " ".join(p for p in parts if p).strip()

results = []
for g in graded:
    doc_id  = g["doc_id"]
    service = g["service"]
    data    = g["data"]
    ref_num = data.get("Personal Ref #", "?")
    desc    = data.get("Description","")
    year    = data.get("Year","")
    denom   = data.get("Denomination","")

    query = build_query(data)
    url   = f"https://currency.ha.com/c/search-results.zx?Nty=1&Ntt={quote_plus(query)}&N=790+231+4294967291"

    results.append({
        "doc_id":  doc_id,
        "service": service,
        "ref_num": ref_num,
        "year":    year,
        "denom":   denom,
        "desc":    desc,
        "cond":    data.get("Condition",""),
        "query":   query,
        "ha_url":  url,
        "found_img_url": None,
        "found_img_title": None,
        "gcs_url": None,
        "status":  "pending",
    })
    print(f"Ref#{ref_num:>4}  {service:<5}  {query[:70]}")

out = os.path.join(SCRIPT_DIR, "_cert_scraper_cache", "search_plan.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nSaved {len(results)} search plans to: {out}")
