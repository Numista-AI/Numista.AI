# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import sys, re, urllib.request
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')

WIKI_URL = "https://en.wikipedia.org/wiki/Sacagawea_dollar"
req = urllib.request.Request(WIKI_URL, headers={"User-Agent": "NumistaAI-DataSync/1.0"})
html = urllib.request.urlopen(req).read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")

for table in soup.find_all("table"):
    rows = table.find_all("tr")
    for row in rows[:10]:
        cells = row.find_all(["th", "td"])
        text = [c.get_text(separator=" ", strip=True) for c in cells]
        if len(text) >= 2:
            print(text[:5])
    print("---")
