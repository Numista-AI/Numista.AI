#!/usr/bin/env python3
"""Verify Wikimedia Commons filenames and find the correct ones."""
import json
import sys
import io
from urllib.parse import quote
from urllib.request import Request, urlopen

# Force UTF-8 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

UA = "NumistaAI/1.0 (eric@numista.ai)"

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
        status = "OK" if pid != "-1" and url else "MISSING"
        print(f"  [{status}] {filename}")
        if url:
            print(f"    URL: {url[:100]}")
        else:
            print(f"    NOT FOUND (pid={pid})")

files_to_test = [
    "File:Barber quarter reverse.jpg",
    "File:Barber Half Dollar Reverse.jpg",
    "File:Barber dime reverse.jpg",
    "File:Morgan dollar reverse.jpg",
    "File:1880-S Morgan Dollar rev.jpg",
    "File:Morgandollar-1891-rev.jpg",
    "File:Seated liberty quarter reverse 1853.jpg",
    "File:Seated Liberty quarter reverse.jpg",
    "File:Seated Liberty dollar reverse.jpg",
    "File:Seated liberty dollar, reverse, 1871.jpg",
    "File:Barber Quarter Reverse.jpg",
    "File:BarberHalfDollarReverseCloseup.jpg",
    "File:Barber Quarter, reverse.jpg",
    "File:Barber quarter, reverse, 1899.jpg",
    "File:1892O Barber Quarter Reverse.jpg",
    "File:1899 Barber quarter reverse.jpg",
    "File:Morgan silver dollar reverse.jpg",
    "File:Morgan dollar 1921 reverse.jpg",
]

for f in files_to_test:
    try:
        check(f)
    except Exception as e:
        print(f"  ERROR {f}: {e}")
