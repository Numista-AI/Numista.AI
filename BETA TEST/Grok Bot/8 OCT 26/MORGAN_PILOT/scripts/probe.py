import json, sys
from dex import *
DS = f'{COL}/dataStores/morgan-docs/branches/default_branch'
s, j = call('GET', f'{DS}/documents', params={'pageSize': 1000}, log_resp=False)
print('docs listed', s, len(j.get('documents', [])))
SC = f'{COL}/engines/morgan-pilot-search/servingConfigs/default_search:search'
body = {'query': '2022 Maya Angelou quarter mint marks Philadelphia Denver San Francisco', 'pageSize': 5,
        'contentSearchSpec': {'snippetSpec': {'returnSnippet': True},
                              'extractiveContentSpec': {'maxExtractiveSegmentCount': 3, 'returnExtractiveSegmentScore': True, 'numPreviousSegments': 1, 'numNextSegments': 1}}}
s, j = call('POST', SC, body=body, log_resp=False)
json.dump(j, open('probe_search.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('search', s, json.dumps(j, ensure_ascii=False)[:2500])
