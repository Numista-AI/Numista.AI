# Helper for Discovery Engine REST calls on numista-morgan-pilot ONLY. Token is never printed or saved.
import subprocess, requests, json, time, os, datetime
P = 'numista-morgan-pilot'
BASE = 'https://discoveryengine.googleapis.com/v1'
LOC = f'projects/{P}/locations/global'
COL = f'{LOC}/collections/default_collection'
HERE = os.path.dirname(os.path.abspath(__file__))
LOGF = os.path.join(HERE, 'api_calls.log.jsonl')
_tok = None; _t = 0
def tok():
    global _tok, _t
    if not _tok or time.time() - _t > 1500:
        r = subprocess.run('gcloud auth print-access-token', shell=True, capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            raise SystemExit('TOKEN_FAIL: ' + r.stderr.strip()[:500])
        _tok = r.stdout.strip(); _t = time.time()
    return _tok
def call(method, path, body=None, params=None, base=BASE, log_resp=True):
    assert (P in path or '973425551443' in path or path.startswith('http')), 'refusing non-pilot path'
    url = path if path.startswith('http') else f'{base}/{path}'
    assert 'studio-9101802118' not in url
    h = {'Authorization': 'Bearer ' + tok(), 'X-Goog-User-Project': P, 'Content-Type': 'application/json'}
    for attempt in range(4):
        r = requests.request(method, url, headers=h, json=body, params=params, timeout=180)
        if r.status_code in (429, 500, 503) and attempt < 3:
            time.sleep(5 * (attempt + 1)); continue
        break
    try: j = r.json()
    except Exception: j = {'raw': r.text[:3000]}
    rec = {'ts': datetime.datetime.now().isoformat(timespec='seconds'), 'method': method, 'url': url, 'status': r.status_code}
    s = json.dumps(j, ensure_ascii=False)
    rec['resp'] = j if (log_resp and len(s) < 20000) else s[:2000]
    with open(LOGF, 'a', encoding='utf-8') as f: f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    return r.status_code, j
def wait_op(name, maxwait=900):
    t0 = time.time()
    while time.time() - t0 < maxwait:
        s, j = call('GET', name)
        if j.get('done'): return j
        time.sleep(10)
    return {'done': False, 'name': name}
