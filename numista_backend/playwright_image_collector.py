"""
playwright_image_collector.py
==============================
Uses the Playwright MCP server's page session (already running) to navigate to
Heritage Auctions search pages and collect image URLs for all 32 graded currency docs.

Since this must be run interactively with Playwright MCP, this script instead:
1. Reads the search_plan.json
2. Prints JS to be evaluated in the browser
3. The caller (Antigravity) will paste these URLs and collect results

ALTERNATIVE: We use requests with the HA API directly with proper cookies.
The HA search results API returns JSON at a different endpoint.
"""
import json, os, re
from urllib.parse import quote_plus

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(SCRIPT_DIR, "_cert_scraper_cache", "search_plan.json"), encoding="utf-8") as f:
    plans = json.load(f)

# Print all URLs for the agent to navigate to one by one
print("=== HERITAGE AUCTIONS SEARCH URLS ===")
print("Navigate to each, then run JS to extract image URL\n")

JS_EXTRACT = (
    "() => { "
    "const imgs = Array.from(document.querySelectorAll('img[src*=\"heritagestatic\"]'))"
    ".filter(i=>i.alt && i.alt.length>5 && !['logo','employee','hand','add','avatar'].some(w=>i.alt.toLowerCase().includes(w)));"
    "if(!imgs.length) return JSON.stringify({found:false});"
    "const i = imgs[0];"
    "const hiRes = i.src.replace(/w=\\d+/,'w=900').replace(/h=\\d+/,'h=600');"
    "return JSON.stringify({found:true, title:i.alt, hiRes, thumb:i.src}); }"
)

for idx, p in enumerate(plans, 1):
    print(f"\n--- [{idx:2}/{len(plans)}] Ref#{p['ref_num']}  {p['service']}  {p['desc'][:55]} ---")
    print(f"URL: {p['ha_url']}")
    print(f"JS:  {JS_EXTRACT}")
