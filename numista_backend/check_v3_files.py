#!/usr/bin/env python3
"""Spot-check the exact Wikimedia filenames used in v3."""
import json
import sys
import io
import time
from urllib.parse import quote
from urllib.request import Request, urlopen

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
            print(f"    pid={pid}")
    time.sleep(0.3)

files = [
    "File:1893-S Morgan dollar reverse.jpg",
    "File:Liberty Seated dollar reverse.jpg",
    "File:1877-CC Seated Liberty quarter reverse.jpg",
    "File:Barber quarter reverse.jpeg",
    "File:Barber half reverse.jpg",
    "File:Barber dime reverse.jpeg",
    "File:Mercury Dime reverse.jpg",
    "File:Walking Liberty Half Dollar 1945D Reverse.png",
    "File:Franklin Half 1963 D Reverse.png",
    "File:Kennedy half dollar reverse.jpg",
    "File:2015-W proof Roosevelt dime reverse.jpg",
    "File:Indian Head Buffalo Reverse.jpg",
    "File:1859 Indian Head cent reverse.png",
    "File:Wheat Penny reverse.jpg",
    "File:1911-D Indian Head quarter eagle reverse.jpg",
    "File:1916-S half eagle reverse.jpg",
    "File:1911 Indian Head eagle reverse.jpg",
    "File:Two cent piece, reverse, 1872.jpg",
    "File:Three cent nickel, reverse, 1865.jpg",
    "File:1889-p-morgan-dollar-reverse.jpg",
    "File:1921 Peace dollar reverse.jpg",
    "File:1875-S trade dollar reverse.jpg",
    "File:Standing Liberty Quarter reverse.jpg",
    "File:1853 Large Cent Rev.jpg",
    "File:Kennedy half dollar reverse.jpg",
    "File:Circulated Washington quarter reverse.jpg",
    "File:Shield nickel reverse.jpg",
    "File:Liberty Head Nickel Reverse.jpg",
]

for f in files:
    try:
        check(f)
    except Exception as e:
        print(f"  ERROR {f}: {e}")
