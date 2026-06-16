import sys, re, urllib.request
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')

for url in [
    "https://en.wikipedia.org/wiki/Presidential_dollar_coin",
    "https://en.wikipedia.org/wiki/America_the_Beautiful_quarters",
]:
    print(f"\n=== {url} ===")
    req = urllib.request.Request(url, headers={"User-Agent": "NumistaAI-DataSync/1.0"})
    html = urllib.request.urlopen(req).read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        for row in rows[:6]:
            cells = row.find_all(["th", "td"])
            text = [c.get_text(separator=" ", strip=True) for c in cells]
            if len(text) >= 2:
                print(text[:5])
        print("---")
