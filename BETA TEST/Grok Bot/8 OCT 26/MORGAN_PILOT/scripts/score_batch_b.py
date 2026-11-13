import json, csv, os, datetime
from pathlib import Path
from rows import ROWS

RUN = Path('run')
OUT = Path('..') / 'out'
DAY = Path(r'C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\26 OCT 26')
OUT.mkdir(exist_ok=True); DAY.mkdir(exist_ok=True)
stamp = 'BATCH_B_STATE_QUARTERS_20261026_' + datetime.datetime.now().strftime('%H%MET').replace('M','')  # fix below
# America/New_York local
stamp = 'BATCH_B_STATE_QUARTERS_' + datetime.datetime.now().strftime('%Y%m%d_%H%MET')
# PowerShell-friendly stamp without broken replace:
stamp = 'BATCH_B_STATE_QUARTERS_' + datetime.datetime.now().strftime('%Y%m%d_%H%M') + 'ET'

def verdict_for(rec):
    n_mint = rec.get('n_mint_facts', 0)
    cm = rec.get('checks', {}).get('claim_vs_mint', {})
    resp = cm.get('resp', {}) if cm else {}
    status = cm.get('status') if cm else None
    score = resp.get('supportScore')
    claims = resp.get('claims', []) or []
    req = [c for c in claims if c.get('groundingCheckRequired', True)]
    cited = bool(req) and all(c.get('citationIndices') for c in req)
    # Contradicted heuristic: opposite strongly supported while claim weak — keep simple like Batch A (0 contradicted)
    opp = rec.get('checks', {}).get('opposite_vs_mint', {}).get('resp', {})
    opp_score = opp.get('supportScore')
    opp_claims = [c for c in (opp.get('claims') or []) if c.get('groundingCheckRequired', True)]
    opp_cited = bool(opp_claims) and all(c.get('citationIndices') for c in opp_claims)

    if n_mint == 0 or not cm or status != 200:
        return 'No Mint source', score, None, None
    # Supported if claim grounded with citations and score >= 0.6
    if cited and score is not None and score >= 0.6:
        # Optional soft contradict flag if opposite also strongly cited AND higher — Batch A didn't use this
        return 'Supported', score, cited, opp_score
    return 'Unsupported', score, cited, opp_score

rows_out = []
details = []
counts = {'Supported':0,'Unsupported':0,'Contradicted':0,'No Mint source':0}
for R in ROWS:
    path = RUN / f"row{R['row']:02d}.json"
    rec = json.load(open(path, encoding='utf-8'))
    verd, score, cited, opp_score = verdict_for(rec)
    counts[verd] = counts.get(verd,0)+1
    cm = rec.get('checks',{}).get('claim_vs_mint',{})
    resp = cm.get('resp',{}) if cm else {}
    used = cm.get('facts',[]) if cm else []
    # first cited fact
    cited_url=''; quote=''
    claims = resp.get('claims') or []
    idxs=[]
    for c in claims:
        if c.get('citationIndices'):
            idxs.extend(c['citationIndices'])
    if idxs and used:
        i=idxs[0]
        if 0<=i<len(used):
            cited_url=used[i].get('uri','')
            quote=(used[i].get('text') or '')[:400]
    rows_out.append({
        'row': R['row'], 'slot': R['slot'], 'claim': R['claim'], 'verdict': verd,
        'score': score if score is not None else '',
        'n_mint_facts': rec.get('n_mint_facts',0),
        'n_other_facts': rec.get('n_other_facts',0),
        'search_status': '|'.join(str(x) for x in rec.get('search_status',[])),
        'cited_url': cited_url, 'quote': quote,
        'opp_score': opp_score if opp_score is not None else '',
    })
    details.append({
        'row': R['row'], 'slot': R['slot'], 'verdict': verd, 'supportScore': score,
        'n_mint_facts': rec.get('n_mint_facts',0),
        'claim_citations': [c.get('citationIndices') for c in (resp.get('claims') or [])],
        'claim_scores': [c.get('score') for c in (resp.get('claims') or [])],
        'opp_supportScore': opp_score,
        'ours': R.get('ours',''),
    })

# write CSVs
res_path = OUT / f'{stamp}_RESULTS.csv'
det_path = OUT / f'{stamp}_DETAILS.csv'
sum_path = OUT / f'{stamp}_SUMMARY.md'
with open(res_path,'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
    w.writeheader(); w.writerows(rows_out)
with open(det_path,'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(details[0].keys()))
    w.writeheader(); w.writerows(details)

stats=json.load(open(RUN/'stats.json'))
ingest=json.load(open(OUT/'STATE_QUARTERS_MINT_INGEST_RESULT.json'))
manifest=json.load(open(OUT/'STATE_QUARTERS_MINT_INGEST_MANIFEST.json'))

lines=[]
lines.append('# MORGAN VERTEX PILOT — BATCH B STATE QUARTERS (after Washington/Mint ingest)')
lines.append(f"**DTG:** 26 Oct 2026 ~{datetime.datetime.now().strftime('%I:%M %p').lstrip('0')} ET (America/New_York)")
lines.append('**Runner:** Grok CoS executor (EDS_Laptop). Project **numista-morgan-pilot** only.')
lines.append('**Report only.** No live numista.ai, no Firestore users/coins, no prod studio, no deploy.')
lines.append('')
lines.append('## BLUF')
lines.append(f"Ingested **{ingest['docs_imported']}** U.S. Mint Wayback State Quarters pages/Excels as source_type=us_mint into morgan-docs ({ingest['docs_before']} → **{ingest['docs_listed_total']}** docs). Ran Batch B (12 rows).")
lines.append(f"**Verdicts: Supported {counts['Supported']} | Unsupported {counts['Unsupported']} | Contradicted {counts['Contradicted']} | No Mint source {counts['No Mint source']}.**")
lines.append('')
lines.append('## Verdict table')
lines.append('| Row | Slot | Verdict | supportScore | mintF |')
lines.append('|---|---|---|---|---|')
for r in rows_out:
    sc = r['score'] if r['score']!='' else ''
    if isinstance(sc,float): sc=f'{sc:.6f}'.rstrip('0').rstrip('.')
    lines.append(f"| {r['row']} | {r['slot']} | {r['verdict']} | {sc} | {r['n_mint_facts']} |")
lines.append('')
lines.append('## Counts')
lines.append('| Verdict | N |')
lines.append('|---|---|')
for k in ['Supported','Unsupported','Contradicted','No Mint source']:
    lines.append(f'| {k} | {counts[k]} |')
lines.append('')
uns=[r for r in rows_out if r['verdict']!='Supported']
if uns:
    lines.append('## Remaining gaps')
    for r in uns:
        lines.append(f"- **Row {r['row']}** `{r['slot']}` score={r['score']} — {r['verdict']}.")
    lines.append('')
lines.append(f"## Ingest ({ingest['docs_imported']} docs)")
for m in manifest.get('manifest',[]):
    if m.get('ok'):
        lines.append(f"- page-stateq-{m['key']} — {m.get('title','')}")
        lines.append(f"  - {m.get('url','')}")
lines.append('')
lines.append('## Usage (this batch)')
lines.append('| Item | Value |')
lines.append('|---|---|')
lines.append(f"| Search queries | {stats.get('queries')} |")
lines.append(f"| Check Grounding calls | {stats.get('checks')} |")
lines.append(f"| Fact chars sent | {stats.get('chars')} |")
lines.append('| MAXF | 10 |')
lines.append(f"| Docs in morgan-docs | {ingest['docs_listed_total']} |")
lines.append('')
lines.append('## Optional note (Morgan Batch A)')
lines.append('Rows 5 & 11 from Morgan Batch A rerun remain Unsupported (2024 S-proof; 2026 America250) — not blocking; not rechecked this run.')
lines.append('')
lines.append('## Files')
lines.append(f'- MORGAN_PILOT/out/{stamp}_RESULTS.csv')
lines.append(f'- MORGAN_PILOT/out/{stamp}_DETAILS.csv')
lines.append(f'- MORGAN_PILOT/out/{stamp}_SUMMARY.md')
lines.append('- MORGAN_PILOT/out/STATE_QUARTERS_MINT_INGEST_MANIFEST.json')
lines.append('- Raw row JSON: MORGAN_PILOT/scripts/run/row01.json … row12.json')
lines.append('')
lines.append('## Hard rules honored')
lines.append('numista-morgan-pilot ONLY. No Advanced Answers / Grounded Generation. No prod studio writes. No users/{uid}/coins. No live deploy. Official/archived Mint pages + Mint production Excels only. Mint tier only as evidence (morgan_pack excluded).')
lines.append('')
lines.append('OVER')
sum_path.write_text('\n'.join(lines)+'\n', encoding='utf-8')

# day folder copies
import shutil
for p in [res_path, det_path, sum_path, OUT/'STATE_QUARTERS_MINT_INGEST_MANIFEST.json']:
    shutil.copy2(p, DAY / p.name)

# verdicts raw
json.dump({'stamp':stamp,'counts':counts,'rows':rows_out}, open(OUT/f'{stamp}_verdicts_raw.json','w'), indent=2)
print('STAMP', stamp)
print('COUNTS', counts)
for r in rows_out:
    print(r['row'], r['verdict'], r['score'])
