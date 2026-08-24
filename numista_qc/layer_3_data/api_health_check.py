"""
api_health_check.py — Numista QC Suite
Read-only GET health probes against enumerated production endpoints only.
No auth headers. No Firestore. No /users/ /coins/ /estate/ /admin/ paths.

Allowed endpoints (complete list — adding any endpoint requires a plan revision):
  GET https://numista.ai/
  GET https://numista.ai/docs
  GET https://numista-backend-568985927038.us-central1.run.app/api/spot_prices
  GET https://numista-backend-568985927038.us-central1.run.app/health
"""

import sys
import time
import urllib.request
import urllib.error

ALLOWED_ENDPOINTS = [
    {
        'url': 'https://numista.ai/',
        'name': 'Homepage',
        'expected_status': 200,
        'timeout_s': 15,
    },
    {
        'url': 'https://numista-backend-568985927038.us-central1.run.app/api/spot_prices',
        'name': 'Spot Prices API',
        'expected_status': [200, 401],  # 401 OK (auth required but service alive)
        'timeout_s': 15,
    },
    {
        'url': 'https://numista-backend-568985927038.us-central1.run.app/health',
        'name': 'Backend Health',
        'expected_status': [200, 404],  # 404 if no /health route — not a failure
        'timeout_s': 10,
    },
]

# Forbidden path fragments — any URL containing these is refused
FORBIDDEN_PATH_FRAGMENTS = ['/users/', '/coins/', '/estate/', '/admin/', '/currency/', '/world_items/']


def check_endpoint(endpoint):
    url = endpoint['url']
    name = endpoint['name']
    expected = endpoint['expected_status']
    if isinstance(expected, int):
        expected = [expected]

    # Refuse forbidden paths
    for frag in FORBIDDEN_PATH_FRAGMENTS:
        if frag in url:
            return {'name': name, 'status': 'REFUSED', 'detail': f'Forbidden path fragment: {frag}'}

    # Anonymous GET — no auth headers
    req = urllib.request.Request(url, method='GET')
    req.add_header('User-Agent', 'Numista-QC-HealthCheck/1.0')

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=endpoint['timeout_s']) as resp:
            status = resp.status
            elapsed = round((time.time() - start) * 1000)
    except urllib.error.HTTPError as e:
        status = e.code
        elapsed = round((time.time() - start) * 1000)
    except urllib.error.URLError as e:
        return {'name': name, 'status': 'FAIL', 'detail': f'Connection error: {e.reason}', 'elapsed_ms': 0}

    ok = status in expected
    return {
        'name': name,
        'status': 'PASS' if ok else 'FAIL',
        'http_status': status,
        'elapsed_ms': elapsed,
        'detail': f'HTTP {status} in {elapsed}ms' if ok else f'Expected {expected}, got {status}',
    }


def main():
    print('[api_health_check] Running health probes...')
    results = [check_endpoint(ep) for ep in ALLOWED_ENDPOINTS]

    fails = []
    for r in results:
        status_str = r['status']
        print(f'  [{status_str}] {r["name"]}: {r["detail"]}')
        if status_str == 'FAIL':
            fails.append(r)

    print(f'\n[api_health_check] {len(results) - len(fails)}/{len(results)} endpoints healthy.')
    if fails:
        sys.exit(1)


if __name__ == '__main__':
    main()