import json, requests, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

s = requests.Session()
s.headers.update({'User-Agent': 'NumistaAI/1.0 (eric@numista.ai)'})

with open('awq_index_full.json', encoding='utf-8') as f:
    idx = json.load(f)

# Test one obverse and a few reverses
test_keys = [
    '2023_american-women-quarters_obverse',
    '2023_bessie-coleman_american-women-quarters_reverse',
    '2023_eleanor-roosevelt_american-women-quarters_reverse',
    '2024_american-women-quarters_obverse',
    '2024_celia-cruz_american-women-quarters_reverse',
    '2024_mary-edwards-walker_american-women-quarters_reverse',
    '2024_patsy-mink_american-women-quarters_reverse',
]
for k in test_keys:
    if k not in idx: print(f'MISSING: {k}'); continue
    d = idx[k]
    side = 'obverse' if 'obverse' in d else 'reverse'
    url = d[side]['public_url']
    try:
        r = s.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type','?')
        size = r.headers.get('Content-Length','?')
        print(f'{"OK" if r.status_code==200 else "FAIL"} {r.status_code} {size:>10}b {ct:<20} {k}')
    except Exception as e:
        print(f'ERR {k}: {e}')
