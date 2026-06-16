import urllib.request
import re

url = 'https://www.usmint.gov/learn/coins-and-medals/collectible-coins/presidential-dollar-coins'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Cookie': 'dwsid=ft4G18N-VkMRAIjwjUu3NTqHT3mWTwj-2PEVpT1SKuZZOHNSwXVqe9ZrQ4mgcq1XljLUj-twfW64DbZiU1kZvg==; cf_clearance=z6EX43B5Mui_qmHnJYCHT29UNGj6h2v.HNTPbAEd7tk-1776185100-1.2.1.1-wvpOAiiSdEox2e2GMJ.Sys.AXM8aLADUSTnqVWMhiEiQ7co5P1EDiplkKlB92Xp2RGlOmTjIRsMw5Cy3t4mWsfc.pNuA8YGlWZM2QzSJnq4mcbsALbON4fxRd8dH3ca94bsHI0tvRpujw12EFiQf9mOz2prOezI9ALH9_dEzl_ooJBeEt5o9cUGI1vw4WmbBQeGHxiIRn71JCy7vdUtrM0ocpLhCfTDPvgTnCwePRk2wuPZeP666chUeY_jTuCG4nIueagZaHAcSNKHwmh0YDehL20_b.qbhB6rAxUbg07GaW4NBFV.yhurDafgcU8F8aHAobMowgc8Xt_PcRU1HNg'}
try:
    html = urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS)).read().decode('utf-8')
    links = re.findall(r'href=[\'\"]([^\'\"]*president[^\'\"]*)[\'\"]', html, re.I)
    for l in list(set(links)): 
        print(l)
except Exception as e:
    print(f"Error: {e}")
