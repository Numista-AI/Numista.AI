# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
Scrape the American Women Quarters Wikipedia page and patch master_coin_programs.json.
Also adds the program scraper to the sync_worker for automated future syncing.
"""
import json
import re
import os
import urllib.request
from bs4 import BeautifulSoup

WIKI_URL = "https://en.wikipedia.org/wiki/American_Women_quarters"

req = urllib.request.Request(WIKI_URL, headers={"User-Agent": "NumistaAI-DataSync/1.0"})
html = urllib.request.urlopen(req).read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")

# Dump all table rows for inspection
coins = []
current_year = ""

for table in soup.find_all("table"):
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all(["th", "td"])
        text = [cell.get_text(separator=" ", strip=True) for cell in cells]
        if len(text) >= 3:
            print(text[:5])
