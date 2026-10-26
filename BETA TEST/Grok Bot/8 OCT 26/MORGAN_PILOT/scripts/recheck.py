# Re-check (Check Grounding only, no new search queries) using the facts already returned for each row.
import json, os
from dex import *
from rows import ROWS
GC = f'{LOC}/groundingConfigs/default_grounding_config:check'
OUT = os.path.join(HERE, 'run')
st = json.load(open(os.path.join(OUT, 'stats.json')))
R = {r['row']: r for r in ROWS}
todo = {}
for n in [2,4,6,8,10,22,24,26,28,30,32,34,36,38,40]:
    rr = R[n]; y = rr['slot'].split('_')[-1].split('#')[0]
    first2 = rr['claim'].rsplit('. The ', 1)[0] + '.'
    todo[n] = first2 + f' The mint and mint mark of the {y} American Women Quarters Silver Proof Set is San Francisco - S.'
todo[3] = 'The 2022 Dr. Sally Ride quarter was minted at Philadelphia (P) and Denver (D). A 3-Roll Set of the 2022 Dr. Sally Ride quarter contains P, D and S coins.'
for n, claim in todo.items():
    f = os.path.join(OUT, f'row{n:02d}.json'); rec = json.load(open(f, encoding='utf-8'))
    facts = rec['checks']['claim_vs_mint']['facts']
    body = {'answerCandidate': claim,
            'facts': [{'factText': x['text'], 'attributes': {'uri': x['uri'], 'title': x['title'][:200], 'tier': x['tier'], 'doc': x['doc']}} for x in facts],
            'groundingSpec': {'citationThreshold': 0.6, 'enableClaimLevelScore': True}}
    s, j = call('POST', GC, body=body, log_resp=False)
    st['checks'] += 1; st['chars'] += len(claim) + sum(len(x['text']) for x in facts)
    rec['checks']['claim_vs_mint_recheck'] = {'status': s, 'resp': j, 'facts': facts, 'claim': claim}
    json.dump(rec, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('row', n, s, j.get('supportScore'), [(round(c.get('score', 0), 2), bool(c.get('citationIndices'))) for c in j.get('claims', [])], flush=True)
json.dump(st, open(os.path.join(OUT, 'stats.json'), 'w'))
print('STATS', json.dumps(st))
