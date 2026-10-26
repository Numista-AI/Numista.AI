# MORGAN PILOT RESTART — COMMANDS V1
**Machine:** EDS_Laptop (PowerShell). **Project:** `numista-morgan-pilot` only.
**Do not run until Eric completes AUTH (step 0).**

Working dir:
```
cd "C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\8 OCT 26\MORGAN_PILOT\scripts"
```

## 0) AUTH (Eric — interactive)
```powershell
gcloud auth login
gcloud auth application-default login
gcloud config set account eric@numista.ai
# Leave default project as studio-9101802118-8c9a8 if preferred — scripts force pilot via path + header.
gcloud auth print-access-token   # must print a token
gcloud projects describe numista-morgan-pilot --format="value(projectId,lifecycleState)"
```
Tell CoS **AUTH_OK** when those succeed.

## 1) Sanity — engine + docs still there?
```powershell
python -c "from dex import *; s,j=call('GET', f'{COL}/engines/morgan-pilot-search'); print(s, j.get('name'), j.get('searchEngineConfig')); s2,j2=call('GET', f'{COL}/dataStores/morgan-docs/branches/default_branch/documents', params={'pageSize':5}); print('docs', s2, len(j2.get('documents',[])), 'next', j2.get('nextPageToken','')[:20])"
```
- Expect engine 200, Enterprise, empty searchAddOns.
- If engine missing: re-run `python setup.py` then `python engine.py` (creates `morgan-docs` + `morgan-pilot-search`).
- If docs empty: rebuild upload batches from scrubbed Mint Wayback pages (see 13 Oct SUMMARY) then `python upload.py`. Prefer **incremental** re-import of Morgan-dollar Mint pages only for Batch A.

## 2) Wire Batch A rows
```powershell
copy /Y rows_morgan_dollars_batch_a.py rows.py
# Confirm pilot.py MAXF=10 (edit if still 40):
#   MAXF = 10
# Optional QCAP stay 200
```

## 3) Probe one query (cheap)
```powershell
python probe.py
# or:
python -c "from dex import *; SC=f'{COL}/engines/morgan-pilot-search/servingConfigs/default_search:search'; s,j=call('POST',SC,body={'query':'2024 Morgan Silver Dollar Philadelphia Mint uncirculated','pageSize':3,'contentSearchSpec':{'snippetSpec':{'returnSnippet':True}}},log_resp=False); print(s, len(j.get('results',[])))"
```
If 0 results relevant to Morgan 2024, upload Batch A Mint Wayback HTML/txt first (inline import; no bucket).

## 4) Overnight Batch A
```powershell
New-Item -ItemType Directory -Force -Path ..\run, ..\out | Out-Null
# pilot.py writes to scripts\run — or set OUT in pilot; after run, copy results:
python pilot.py
# Optional subset: python pilot.py 1,2,3,4,5
```
When complete, CoS builds RESULTS.csv + DETAILS.csv + SUMMARY.md into `MORGAN_PILOT\out\` (same columns as 13 Oct).

## 5) Morning billing check (Eric or FIN OPS)
Console → Billing → Reports → project `numista-morgan-pilot` → last 7 days → Group by **SKU**.
- OK: Vertex AI Search / Discovery Engine + matching credit.
- STOP: Cloud Storage, Vertex AI Gemini, Compute, Cloud Run → kill switch in RESTART_PLAN_V1.md.

## Kill switch (any one)
1. Billing → Account management → disable billing on `numista-morgan-pilot`
2. Delete engine `morgan-pilot-search` + data stores
3. Shut down project (30-day undo)

## Hard rules
- Never point these scripts at `studio-9101802118-8c9a8`
- Never enable Advanced Answers / Grounded Generation
- Never write Firestore / live catalog
- WAKE / baton never authorizes deploy
