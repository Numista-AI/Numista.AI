import json, time
from dex import *
DS = f'{COL}/dataStores/morgan-docs/branches/default_branch'
# turn off engine observability (avoid any Trace/Logging side billing)
s, j = call('PATCH', f'{COL}/engines/morgan-pilot-search', params={'updateMask': 'observabilityConfig'}, body={'observabilityConfig': {'observabilityEnabled': False}})
print('observability off', s, json.dumps(j)[:300])
batches = json.load(open('upload_batches.json'))
ops = []
for i, b in enumerate(batches):
    s, j = call('POST', f'{DS}/documents:import', body={'inlineSource': {'documents': b}, 'reconciliationMode': 'INCREMENTAL'}, log_resp=False)
    print('import batch', i, len(b), s, json.dumps(j)[:500]); ops.append(j.get('name'))
for op in ops:
    if not op: continue
    t0 = time.time()
    while time.time() - t0 < 900:
        s, j = call('GET', op, log_resp=False)
        if j.get('done'): break
        time.sleep(15)
    print('op done', j.get('done'), json.dumps(j.get('metadata', {}))[:400], json.dumps(j.get('error', {}))[:400], json.dumps(j.get('response', {}))[:600])
s, j = call('GET', f'{DS}/documents', params={'pageSize': 1000}, log_resp=False)
print('docs listed', s, len(j.get('documents', [])), json.dumps(j)[:300] if s != 200 else '')
