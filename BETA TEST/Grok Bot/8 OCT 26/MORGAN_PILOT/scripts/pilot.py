import json, os, sys, time
from dex import *
from rows import ROWS
SC = f'{COL}/engines/morgan-pilot-search/servingConfigs/default_search:search'
GC = f'{LOC}/groundingConfigs/default_grounding_config:check'
OUT = os.path.join(HERE, 'run'); os.makedirs(OUT, exist_ok=True)
STATS = os.path.join(OUT, 'stats.json')
st = json.load(open(STATS)) if os.path.exists(STATS) else {'queries': 0, 'checks': 0, 'chars': 0}
QCAP = 200; MAXF = 10
def tier(sd):
    t = sd.get('source_type')
    return t if t in ('us_mint', 'third_party', 'morgan_pack') else 'third_party'
def search(q):
    if st['queries'] >= QCAP: raise SystemExit('QUERY CAP REACHED')
    body = {'query': q, 'pageSize': 8, 'contentSearchSpec': {'snippetSpec': {'returnSnippet': True},
            'extractiveContentSpec': {'maxExtractiveSegmentCount': 5, 'returnExtractiveSegmentScore': True, 'numPreviousSegments': 1, 'numNextSegments': 1}}}
    s, j = call('POST', SC, body=body, log_resp=False); st['queries'] += 1
    return s, j
def facts_from(results):
    facts = {}
    for res in results:
        for rank, r in enumerate(res.get('results', [])):
            d = r['document']; sd = d.get('structData', {}); t = tier(sd)
            if t == 'morgan_pack': continue   # Morgan's own claims are never evidence (circular)
            for seg in d.get('derivedStructData', {}).get('extractive_segments', []):
                for part, sc in [(seg, seg.get('relevanceScore', 0) + 0.02*(8-rank))] + [(p, seg.get('relevanceScore', 0) + 0.02*(8-rank) - 0.05) for p in seg.get('previous_segments', []) + seg.get('next_segments', [])]:
                    txt = part.get('content', '')
                    if not txt.strip(): continue
                    k = (d['id'], txt)
                    if k not in facts or facts[k]['sc'] < sc:
                        facts[k] = {'sc': sc, 'tier': t, 'doc': d['id'], 'uri': sd.get('uri', ''), 'title': sd.get('title', ''), 'publisher': sd.get('publisher', ''), 'text': txt}
    return sorted(facts.values(), key=lambda f: -f['sc'])
def check(answer, facts):
    facts = facts[:MAXF]
    body = {'answerCandidate': answer,
            'facts': [{'factText': f['text'], 'attributes': {'uri': f['uri'], 'title': f['title'][:200], 'tier': f['tier'], 'doc': f['doc']}} for f in facts],
            'groundingSpec': {'citationThreshold': 0.6, 'enableClaimLevelScore': True}}
    s, j = call('POST', GC, body=body, log_resp=False)
    st['checks'] += 1; st['chars'] += len(answer) + sum(len(f['text']) for f in facts)
    return s, j, facts
rows = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else list(range(1, 49))
for R in ROWS:
    if R['row'] not in rows: continue
    rec = {'row': R['row'], 'slot': R['slot'], 'claim': R['claim'], 'opposite': R['opposite'], 'queries': R['queries'], 'search_status': [], 'checks': {}}
    res = []
    for q in R['queries']:
        s, j = search(q); rec['search_status'].append(s); res.append(j)
    rec['search_raw'] = res
    F = facts_from(res)
    mint = [f for f in F if f['tier'] == 'us_mint']; other = [f for f in F if f['tier'] == 'third_party']
    rec['n_mint_facts'] = len(mint); rec['n_other_facts'] = len(other)
    if mint:
        s, j, used = check(R['claim'], mint); rec['checks']['claim_vs_mint'] = {'status': s, 'resp': j, 'facts': used}
        if R['opposite']:
            s, j, used = check(R['opposite'], mint); rec['checks']['opposite_vs_mint'] = {'status': s, 'resp': j, 'facts': used}
    cm = rec['checks'].get('claim_vs_mint', {}).get('resp', {})
    req = [c for c in cm.get('claims', []) if c.get('groundingCheckRequired', True)]
    mint_ok = bool(req) and all(c.get('citationIndices') for c in req)
    if not mint_ok and other:
        s, j, used = check(R['claim'], other); rec['checks']['claim_vs_nonmint'] = {'status': s, 'resp': j, 'facts': used}
    json.dump(rec, open(os.path.join(OUT, f"row{R['row']:02d}.json"), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(st, open(STATS, 'w'))
    summ = {k: (v['status'], v['resp'].get('supportScore')) for k, v in rec['checks'].items()}
    print('row', R['row'], 'search', rec['search_status'], 'mintF', len(mint), 'otherF', len(other), summ, flush=True)
print('STATS', json.dumps(st))
