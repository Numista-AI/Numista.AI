import csv, glob, json, os, re, hashlib
R='/workspace/morgan_pilot/raw'; O='/workspace/morgan_pilot/scrub'
docs=[]; log=[]
EMAIL=re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
PRICE=re.compile(r'\$\s?\d[\d,]*\.\d{2}')
def scrub(t):
    n0=len(t)
    t,a=EMAIL.subn('[email removed]',t)
    t,b=re.subn(r'Welcome,(\s|\\n)*[A-Z][A-Za-z]+','Welcome, [user]',t)
    t,c=re.subn(r'\bEric\b(?! David Custer)|\bERIC\b(?! DAVID)','[owner]',t)
    t,d=PRICE.subn('[price removed]',t)
    t,e=re.subn(r'\bHOLIDAY\d{4}\b','[promo]',t)
    return t,(a,b,c,d,e)
def add(did,title,uri,stype,publisher,text,src):
    text,counts=scrub(text)
    docs.append(dict(id=did,title=title,uri=uri,source_type=stype,publisher=publisher,text=text,orig_file=src))
    log.append((src,did,stype,len(text),counts))
def slug(s): return re.sub(r'[^a-z0-9_-]+','-',s.lower()).strip('-')[:60]
# 1) saved pages
RE6={'22WS':'https://www.usmint.gov/american-women-quarters-2022-silver-proof-set-22WS.html',
 '23WS':'https://www.usmint.gov/american-women-quarters-2023-silver-proof-set-23WS.html',
 '24WS':'https://www.usmint.gov/american-women-quarters-2024-silver-proof-set-24WS.html',
 '25WS':'https://www.usmint.gov/american-women-quarters-2025-silver-proof-set-25WS.html',
 '22WP':'https://www.usmint.gov/american-women-quarters-2022-proof-set-22WP.html',
 '23WP':'https://www.usmint.gov/american-women-quarters-2023-proof-set-23WP.html',
 '24WP':'https://www.usmint.gov/american-women-quarters-2024-proof-set-24WP.html',
 '25WP':'https://www.usmint.gov/american-women-quarters-2025-proof-set-25WP.html',
 'MASTER_AWQMA':'https://www.usmint.gov/american-women-quarters-2022-rolls-and-bags-maya-angelou-MASTER_AWQMA.html',
 'MASTER_AWQSM':'https://www.usmint.gov/american-women-quarters-2025-rolls-and-bags-stacey-park-milbern-MASTER_AWQSM.html'}
OTHER={'pr_2022_awq_designs.txt':('usmint.gov press release (saved copy): United States Mint Announces Designs for 2022 American Women Quarters Program Coins','https://www.usmint.gov/news/press-releases (2022 AWQ designs, saved copy)'),
 'pr_2024_awq_designs.txt':('usmint.gov press release (saved copy): United States Mint Announces Designs for 2024 American Women Quarters Program Coins','https://www.usmint.gov/news/press-releases (2024 AWQ designs, saved copy)'),
 'littleton_checklist.txt':('Littleton Coin Co. checklist LC-8804 US Women Quarters 2022-2025','littleton-checklist-LC-8804 (saved copy)'),
 'ngc_awq_series.txt':('NGC Coin Explorer: American Women Quarters (2022-2025)','https://www.ngccoin.com/coin-explorer/ (AWQ series, saved copy)'),
 'row02_maya_angelou_2022_pcgs.txt':('PCGS CoinFacts: 2022-S 25C Maya Angelou (saved copy)','https://www.pcgs.com/coinfacts (2022-S Maya Angelou, saved copy)')}
skipped=[]
for f in sorted(glob.glob(R+'/rerun5_pages/*.txt')+glob.glob(R+'/rerun6_pages/*.txt')):
    b=os.path.basename(f); folder=os.path.basename(os.path.dirname(f))
    raw=open(f,encoding='utf-8',errors='replace').read()
    if not raw.strip(): skipped.append(folder+'/'+b+' (empty)'); continue
    if raw.startswith('### Result "'):
        try: raw=json.loads(raw[len('### Result '):].strip().split('\n')[0])
        except Exception: raw=raw.replace('\\n','\n')
    raw=raw.replace('\\n','\n')
    m=re.search(r'The Wayback Machine - (https?://\S+)',raw)
    title=raw.split(' | ')[0][:150] if ' | ' in raw[:200] else None
    if m:
        uri=m.group(1); raw=raw[m.start():]  # drop toolbar text before the Wayback URL line
    elif b in OTHER:
        title,uri=OTHER[b]
    else:
        u=re.search(r'https://www\.usmint\.gov/[a-z0-9-]+-[0-9A-Z]{4}\.html',raw)
        it=re.search(r'Item Number: ([A-Z0-9_]+)',raw)
        uri=u.group(0) if u else (RE6.get(it.group(1)) if it else None)
        if uri is None: skipped.append(folder+'/'+b+' (no url)'); continue
        uri=uri+' (live fetch saved copy)'
    if title is None:
        t=re.search(r'(American Women Quarters 20\d\d [^\n]{0,60}?(Silver Proof Set|Proof Set|Rolls and Bags - [A-Za-z .\-]+))',raw)
        title=(t.group(1) if t else b)[:150]
    low=uri.lower()
    if 'usmint.gov' in low: stype,pub='us_mint','U.S. Mint'
    elif 'pcgs' in low: stype,pub='third_party','PCGS'
    elif 'ngc' in low: stype,pub='third_party','NGC'
    else: stype,pub='third_party','Littleton Coin Co.'
    add('page-'+slug(folder+'-'+b[:-4]),title,uri,stype,pub,raw,folder+'/'+b)
# 2) Morgan packs (context only) - drop price/value/collection/PII columns; rename current_value
DROP=re.compile(r'price|market|collection|owner|user|account|email|uid|cost|paid|purchase',re.I)
packs=sorted(glob.glob(R+'/*_SOURCED.csv'))+[R+'/coins/american_women_quarters_2022-2025.csv']
dropped_cols=set()
for f in packs:
    rows=list(csv.DictReader(open(f,encoding='utf-8-sig')))
    b=os.path.basename(f)
    keep=[k for k in rows[0].keys() if not DROP.search(k)]; dropped_cols|=set(rows[0].keys())-set(keep)
    out=open(O+'/'+b,'w',newline='',encoding='utf-8'); w=csv.writer(out)
    hdr=['catalog_entry_now' if k=='current_value' else k for k in keep]; w.writerow(hdr)
    lines=[]
    for i,r in enumerate(rows,1):
        vals=[scrub(r[k] or '')[0] for k in keep]; w.writerow(vals)
        lines.append(f'[row {i}] '+' | '.join(f'{h}: {v}' for h,v in zip(hdr,vals) if v))
    out.close()
    add('pack-'+slug(b[:-4]),'Morgan evidence pack (scrubbed): '+b,'morgan-sme-database/'+b,'morgan_pack','Numista.Ai Morgan SME database','\n\n'.join(lines),b)
src=open(R+'/sources/sources_silver_eagles_women_quarters.md',encoding='utf-8').read()
add('pack-sources-silver-eagles-women-quarters','Morgan sources list (scrubbed)','morgan-sme-database/sources/sources_silver_eagles_women_quarters.md','morgan_pack','Numista.Ai Morgan SME database',src,'sources/sources_silver_eagles_women_quarters.md')
json.dump(docs,open(O+'/docs.json','w'),ensure_ascii=False)
tot=sum(len(d['text']) for d in docs)
print('docs',len(docs),'chars',tot,'max',max(len(d['text']) for d in docs))
print('by type',{t:sum(1 for d in docs if d['source_type']==t) for t in set(d['source_type'] for d in docs)})
print('dropped cols',dropped_cols); print('skipped',skipped)
agg=[sum(x[4][i] for x in log) for i in range(5)]; print('scrub counts (emails,welcome-user,owner-name,prices,promo):',agg)
with open(O+'/SCRUB_LOG.csv','w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['orig_file','doc_id','source_type','chars','emails','welcome_user','owner_name','prices','promo'])
    for s,d,t,n,c in log: w.writerow([s,d,t,n,*c])
