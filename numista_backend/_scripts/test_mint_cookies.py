import urllib.request, re

COOKIES = ('dwanonymous_b2cf918be9f3733e2d19f7e7beb4b6d7=acvbZsuqmyvGOefBI1gzTaZ7oC; '
           'cf_clearance=ebBcScFZR9QVZZF5j1C2TckIS801YQ0Uw29QtcnXOSw-1781120329-1.2.1.1-R6vYVGJoD4sXoMBg4exiTPFL93DBLwKZwMb8ElkvE7NZuC5Oj0v4AOxVEdgrBpjKJ6dtQWTXNgLwrIfvsO23CHdfo4ycurvfQUvmbd7.poM7ldsmIvVU8KGokoXjDlaCgEPaxBVkTmQTK_SkvCgDg7DjIEGK23Lj_w8L_FjOjiudPuTU14Uma.LwrKSNyF3qTYyFhM19zXFqWivhR7UrX9tjPOS6RjN0fzJpDc.Kg_notXz4pOvUxha6mhGKwy25h0M9k1Vt3dRkuLqAyxVeLVUbOqbEpwCJUh8xPDn63FcgJTH9BE.F.rzOnvaH50IPPgearHi_0RS7Q18zKvt0ZQ; '
           'dwsid=z2oWaK1J20eFDD3hp0kxLMV88iWVPn0M3bkl_XNCbAaF2Q3ulIi_n-TOxe7A1BcTkPzc7j6Jb-qtir-br1VPpA==; '
           'sid=vrnFb1d2N_YrqhgNhGpFoLSvISJvAZG9cx8; '
           'AWSALB=yA4jrsFgyR8WIqwUnBf+4op10KcJqn68XtbW5ZlpvyNdYasPkYt+Fsrkd+JEP438i5dohLe8CI6FxqTyU+lqUmMYwfC9l6uTxhFKX/CuW/1uJOie9cW2eK/z2SD1; '
           'AWSALBCORS=yA4jrsFgyR8WIqwUnBf+4op10KcJqn68XtbW5ZlpvyNdYasPkYt+Fsrkd+JEP438i5dohLe8CI6FxqTyU+lqUmMYwfC9l6uTxhFKX/CuW/1uJOie9cW2eK/z2SD1')

SECTIONS = ['circulating', 'commemorative', 'bullion', 'numismatic', 'historical']

total = 0
for section in SECTIONS:
    url = f'https://www.usmint.gov/news/image-library/{section}'
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Cookie': COOKIES,
            'Accept': 'text/html,*/*'
        })
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='replace')
        imgs = set()
        pattern = r'https?://www\.usmint\.gov/content/dam/usmint/image-library/[^\"\'\s<>]+\.(?:jpg|jpeg|png)'
        for m in re.finditer(pattern, html, re.I):
            u = m.group(0)
            if not any(t in u for t in ['150x', '300x', '500x', 'thumb', 'icon']):
                imgs.add(u)
        print(f'  {section}: {len(imgs)} images')
        for img in list(imgs)[:3]:
            print(f'    {img}')
        total += len(imgs)
    except Exception as e:
        print(f'  {section}: ERROR - {e}')

print(f'\nTOTAL: {total}')
