import urllib.request
import re

url = 'https://www.usmint.gov/learn/coins-and-medals/collectible-coins/presidential-dollar-coins'
HEADERS = {'User-Agent': 'Mozilla/5.0'}
html = urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS)).read().decode('utf-8')
links = sorted(list(set(re.findall(r'href=[\'\"](.*?presidential-dollar.*?)[\'\"]', html))))
for l in links[:20]:
    print(l)
print('Total:', len(links))
