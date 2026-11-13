import json, sys
from dex import *
out = {}
# data store 1: uploaded docs
s, j = call('POST', f'{COL}/dataStores', params={'dataStoreId': 'morgan-docs'}, body={
    'displayName': 'morgan-docs', 'industryVertical': 'GENERIC', 'solutionTypes': ['SOLUTION_TYPE_SEARCH'],
    'contentConfig': 'CONTENT_REQUIRED'})
print('create morgan-docs', s, json.dumps(j)[:600]); out['morgan-docs'] = (s, j)
if s == 200 and 'name' in j and '/operations/' in j['name']: print('op', json.dumps(wait_op(j['name']))[:600])
# data store 2: public website
s, j = call('POST', f'{COL}/dataStores', params={'dataStoreId': 'usmint-site'}, body={
    'displayName': 'usmint-site', 'industryVertical': 'GENERIC', 'solutionTypes': ['SOLUTION_TYPE_SEARCH'],
    'contentConfig': 'PUBLIC_WEBSITE'})
print('create usmint-site', s, json.dumps(j)[:600])
if s == 200 and 'name' in j and '/operations/' in j['name']: print('op', json.dumps(wait_op(j['name']))[:600])
