#!/usr/bin/env python3
"""Search Wikimedia Commons for correct filenames for Barber and Morgan coins."""
import json
import sys
import io
import time
from urllib.parse import quote
from urllib.request import Request, urlopen

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
UA = "NumistaAI/1.0 (eric@numista.ai)"

def search(term):
    api_url = (
        "https://commons.wikimedia.org/w/api.php"
        "?action=query"
        "&list=search"
        "&srnamespace=6"
        f"&srsearch={quote(term)}"
        "&srlimit=5"
        "&format=json"
    )
    req = Request(api_url, headers={"User-Agent": UA})
    with urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

def check(filename):
    api_url = (
        "https://commons.wikimedia.org/w/api.php"
        "?action=query"
        f"&titles={quote(filename)}"
        "&prop=imageinfo"
        "&iiprop=url"
        "&format=json"
    )
    req = Request(api_url, headers={"User-Agent": UA})
    with urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())
    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        ii = page.get("imageinfo", [{}])
        url = ii[0].get("url", "") if ii else ""
        return "OK" if pid != "-1" and url else "MISSING", url
    return "MISSING", ""

# Search terms
searches = [
    "Barber quarter coin reverse",
    "Barber half dollar coin reverse",
    "Barber dime coin reverse",
    "Morgan dollar coin reverse",
    "Seated Liberty dollar coin reverse",
    "Seated Liberty quarter coin reverse",
    "Indian Head quarter eagle coin reverse",
    "Indian Head half eagle coin reverse",
]

for term in searches:
    print(f"\n=== '{term}' ===")
    data = search(term)
    results = data.get("query", {}).get("search", [])
    for r in results:
        title = r.get("title", "")
        if title.lower().endswith((".jpg", ".jpeg", ".png")):
            status, url = check(title)
            print(f"  [{status}] {title}")
            if url:
                print(f"    {url[:100]}")
    time.sleep(0.3)
