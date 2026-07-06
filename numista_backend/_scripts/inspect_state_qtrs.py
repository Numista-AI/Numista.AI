# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import sys, re, urllib.request
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')

for label, url in [
    ("50 State", "https://en.wikipedia.org/wiki/50_State_quarters"),
    ("DC Territories", "https://en.wikipedia.org/wiki/District_of_Columbia_and_United_States_Territories_quarters"),
]:
    print(f"\n=== {label}: {url} ===")
    req = urllib.request.Request(url, headers={"User-Agent": "NumistaAI-DataSync/1.0"})
    html = urllib.request.urlopen(req).read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        header = [c.get_text(strip=True) for c in rows[0].find_all(["th","td"])] if rows else []
        header_str = " ".join(header)
        if any(k in header_str for k in ["State", "Jurisdiction", "Year", "Quarter"]):
            for row in rows[:8]:
                text = [c.get_text(separator=" ", strip=True) for c in row.find_all(["th","td"])]
                if len(text) >= 2:
                    print(text[:5])
            print("---")
            break
