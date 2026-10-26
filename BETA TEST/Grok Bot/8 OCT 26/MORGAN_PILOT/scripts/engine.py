import json
from dex import *
def mk(ids):
    s, j = call('POST', f'{COL}/engines', params={'engineId': 'morgan-pilot-search'}, body={
        'displayName': 'morgan-pilot-search', 'solutionType': 'SOLUTION_TYPE_SEARCH', 'industryVertical': 'GENERIC',
        'dataStoreIds': ids,
        'searchEngineConfig': {'searchTier': 'SEARCH_TIER_ENTERPRISE', 'searchAddOns': []}})
    print('create engine', ids, s, json.dumps(j)[:600]); return s, j
s, j = mk(['morgan-docs', 'usmint-site'])
if s != 200: s, j = mk(['morgan-docs'])
if s == 200 and '/operations/' in j.get('name', '') and not j.get('done'):
    import time; time.sleep(15)
s, j = call('GET', f'{COL}/engines/morgan-pilot-search'); print('engine', s, json.dumps(j, indent=1))
