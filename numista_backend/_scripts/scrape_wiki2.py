import urllib.request
from bs4 import BeautifulSoup
import json

req = urllib.request.Request("https://en.wikipedia.org/wiki/American_Innovation_dollars", headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')

wiki_data = []
for table in soup.find_all('table'):
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all(['th', 'td'])
        text = [cell.get_text().strip() for cell in cells]
        if len(text) > 3:
            wiki_data.append(text)

with open('wiki_data.json', 'w') as f:
    json.dump(wiki_data, f, indent=2)
print("Saved to wiki_data.json")
