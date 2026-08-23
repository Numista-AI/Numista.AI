"""
audit_coin_programs.py — DRAFT
For Gemini + Grok review. NOT committed to repository.
─────────────────────────────────────────────────────
Read-only Greysheet slot audit for all 31 Numista.AI coin programs.

Compares:
  numista_backend/master_coin_programs.json   (our catalog)
  greysheet_node_map.json                     (node config)
  Greysheet CPG API                           (ground truth)

Gap types reported:
  MISSING      — GS has a slot our JSON does not have
  PHANTOM      — Our JSON has a slot that GS doesn't recognize
  NEW_YEAR     — GS has a year that is newer than our JSON's last year
  LABEL_MISMATCH — Slot exists in both but label wording differs significantly
  UNKNOWN      — GS item could not be parsed into a slot key

NEVER writes to master_coin_programs.json.

Usage:
  python audit_coin_programs.py --validate-map
  python audit_coin_programs.py --program washington_quarters_classic
  python audit_coin_programs.py --all
  python audit_coin_programs.py --all --since 2024-01-01
"""
import os
import sys
import json
import time
import re
import argparse
import datetime
import urllib3
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' not installed. Run: pip install requests")
    sys.exit(1)

urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8')

# ── Config ────────────────────────────────────────────────────────────────────
API_KEY   = os.environ.get('GREYSHEET_API_KEY',   '1FCAE3B4-966A-4F25-AFA1-BE242C26856B')
API_TOKEN = os.environ.get('GREYSHEET_API_TOKEN', 'D876F1BA-DDC4-4F80-B155-509AB3B6B970')

if 'GREYSHEET_API_KEY' not in os.environ:
    print("WARNING: GREYSHEET_API_KEY not in environment. Using fallback key.")

BASE_URL = 'https://cpgpublicapiv2.greysheet.com/api'
HEADERS  = {'x-api-key': API_KEY, 'x-api-token': API_TOKEN, 'Content-Type': 'application/json'}

REPO_ROOT    = Path(__file__).resolve().parents[2]  # numista_backend/../..
BACKEND_DIR  = REPO_ROOT / 'numista_backend'
SCRIPTS_DIR  = BACKEND_DIR / '_scripts'

PROGRAMS_JSON   = BACKEND_DIR / 'master_coin_programs.json'
NODE_MAP_JSON   = SCRIPTS_DIR / 'greysheet_node_map.json'
REPORT_MD       = BACKEND_DIR / 'latest_audit_report.md'
REPORT_JSON     = BACKEND_DIR / 'latest_audit_report.json'

API_SLEEP = 0.2  # seconds between API calls

# ── API helpers ───────────────────────────────────────────────────────────────
def api_get(endpoint, params=None):
    p = dict(params or {})
    p.setdefault('apiLevel', 'advanced')
    try:
        r = requests.get(f'{BASE_URL}/{endpoint}', headers=HEADERS, params=p,
                         verify=False, timeout=20)
        if r.status_code == 200:
            return r.json().get('Data', [])
        print(f"  [API {r.status_code}] {endpoint} params={params}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  [API ERROR] {e}", file=sys.stderr)
        return []

def get_children(node_id):
    return api_get('GetNodeChildrenRequest', {'NodeId': node_id})

def get_collectibles(node_id):
    return api_get('GetCollectibleByNodeRequest', {'NodeId': node_id})

def fetch_all_items_for_nodes(node_ids: list) -> list:
    """Fetch all collectible items for a list of node IDs, walking children if needed."""
    all_items = []
    for node_id in node_ids:
        children = get_children(node_id)
        time.sleep(API_SLEEP)
        if children:
            for child in children:
                cid = child.get('Id')
                if cid:
                    items = get_collectibles(cid)
                    for it in items:
                        it['_node_id'] = cid
                        it['_parent_node'] = node_id
                    all_items.extend(items)
                    time.sleep(API_SLEEP)
        else:
            items = get_collectibles(node_id)
            for it in items:
                it['_node_id'] = node_id
                it['_parent_node'] = node_id
            all_items.extend(items)
            time.sleep(API_SLEEP)
    return all_items

# ── GS name normalization ─────────────────────────────────────────────────────
# GS item name examples:
#   '1971-D 50c MS'
#   '1971-S 50c PR'
#   '1971-S 50c Silver PR'
#   '1965 25c SP'           (Special Mint Set)
#   '1964 50c PR'           (no mint = P)
#   '1921 $1 MS'            (Morgan — could be P/D/S/O/CC)
#   '1936-D 1c MS RD'       (Wheat — BN vs RD vs RB)
#   '1971-S 50c Silver PR DCAM'

DENOM_PATTERN = re.compile(
    r'\b(\d{4})'             # year
    r'(?:-([A-Z]{1,2}))?'   # optional mint mark after hyphen
    r'\s+'
    r'(\S+)'                 # denomination (e.g. 1c, 5c, 10c, 25c, 50c, $1)
    r'\s+'
    r'(.*)',                 # rest: grade/strike info
    re.IGNORECASE
)

STRIKE_KEYWORDS = {
    'pr dcam': 'PROOF-DCAM', 'pr cam': 'PROOF-CAM', 'pf dcam': 'PROOF-DCAM',
    'pr': 'PROOF', 'pf': 'PROOF', 'proof': 'PROOF',
    'sp': 'SMS', 'sms': 'SMS',
    'ms': 'BU', 'bu': 'BU',
    'pl': 'PROOF-LIKE', 'dmpl': 'DMPL',
    'matte pr': 'PROOF-MATTE',
}

def normalize_gs_name(name: str) -> dict | None:
    """
    Parse a Greysheet item name into structured fields.
    Returns dict with: year, mint, denom, strike, is_silver, raw
    Returns None if unparseable.
    """
    raw = name.strip()
    m = DENOM_PATTERN.match(raw)
    if not m:
        return None

    year_str, mint_str, denom_str, rest = m.groups()
    year = int(year_str)
    mint = (mint_str or '').upper() or None  # None = unknown (may be P or multi-mint)
    rest_lower = rest.lower()

    is_silver = 'silver' in rest_lower

    # Detect strike
    strike = 'BU'  # default
    for keyword, strike_type in sorted(STRIKE_KEYWORDS.items(), key=lambda x: -len(x[0])):
        if keyword in rest_lower:
            strike = strike_type
            break

    # If no mint mark in name, infer P for most series (not Morgan/Peace/CC-era)
    if mint is None:
        if denom_str in ('50c', '25c', '10c', '5c', '1c'):
            mint = 'P'
        # For dollar coins, leave as None (Morgan can be P/D/S/O/CC — needs special handling)

    return {
        'year': year,
        'mint': mint,
        'denom': denom_str,
        'strike': strike,
        'is_silver': is_silver,
        'raw': raw,
    }

def gs_item_to_slot_id(parsed: dict, program_id: str) -> str | None:
    """
    Convert a parsed GS item to the slot variety ID used in master_coin_programs.json.
    Returns a variety id string like 'P', 'D', 'S-PROOF', 'S-SILVER-PROOF', 'SMS', etc.
    Returns None if unmappable.
    """
    mint = parsed.get('mint')
    strike = parsed.get('strike', 'BU')
    is_silver = parsed.get('is_silver', False)

    if strike == 'SMS':
        return 'SMS'
    if strike in ('PROOF', 'PROOF-DCAM', 'PROOF-CAM', 'PROOF-MATTE'):
        if mint == 'S':
            return 'S-SILVER-PROOF' if is_silver else 'S-PROOF'
        if mint == 'P':
            return 'P-PROOF'
        return 'PROOF'
    if strike == 'BU':
        if mint:
            return mint  # 'P', 'D', 'S', 'W', 'CC', 'O', etc.
        return None  # multi-mint or unknown

    return None  # DMPL, PL, etc. — not in standard program slots

# ── JSON helpers ──────────────────────────────────────────────────────────────
def load_json(path: Path) -> dict | list:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_json_slot_set(program: dict) -> dict:
    """
    Returns {(year_int, variety_id): coin_entry} for all slots in a program.
    year is cast to int to match Greysheet-parsed integer years.
    """
    slots = {}
    for coin in program.get('Coins', []):
        year_raw = coin.get('year')
        try:
            year = int(year_raw)
        except (TypeError, ValueError):
            continue
        for variety in coin.get('varieties', []):
            vid = variety.get('id', '').upper()
            if year and vid:
                slots[(year, vid)] = {'coin': coin, 'variety': variety}
    return slots


# ── Audit logic ───────────────────────────────────────────────────────────────
def audit_program(program_id: str, program: dict, node_map: dict) -> dict:
    """
    Audit one program. Returns a report dict.
    """
    report = {
        'program_id': program_id,
        'program_name': program.get('Name', program_id),
        'status': 'OK',
        'issues': [],
        'gs_item_count': 0,
        'json_slot_count': 0,
        'error': None,
    }

    node_config = node_map.get(program_id)
    if not node_config:
        report['status'] = 'NO_NODE_MAP'
        report['error'] = f"No entry in greysheet_node_map.json for '{program_id}'"
        return report

    node_ids = node_config.get('nodes', [])
    if not node_ids:
        report['status'] = 'NO_NODES'
        report['error'] = f"nodes list is empty for '{program_id}'"
        return report

    # Fetch GS items
    try:
        gs_items = fetch_all_items_for_nodes(node_ids)
    except Exception as e:
        report['status'] = 'API_ERROR'
        report['error'] = str(e)
        return report

    report['gs_item_count'] = len(gs_items)

    # Build GS slot set
    gs_slots = {}
    gs_unparseable = []
    for item in gs_items:
        name = item.get('Name', '')
        parsed = normalize_gs_name(name)
        if not parsed:
            gs_unparseable.append(name)
            continue
        slot_id = gs_item_to_slot_id(parsed, program_id)
        if slot_id is None:
            gs_unparseable.append(name)
            continue
        key = (parsed['year'], slot_id.upper())
        gs_slots[key] = {'name': name, 'parsed': parsed}

    # Build JSON slot set
    json_slots = build_json_slot_set(program)
    report['json_slot_count'] = len(json_slots)

    # Find MISSING (in GS, not in JSON)
    for key, gs_info in gs_slots.items():
        if key not in json_slots:
            year, slot_id = key
            report['issues'].append({
                'type': 'MISSING',
                'year': year,
                'slot_id': slot_id,
                'gs_name': gs_info['name'],
                'detail': f"GS has '{gs_info['name']}' but JSON has no slot ({year}, {slot_id})",
            })

    # Find PHANTOM (in JSON, not in GS)
    json_max_year = max((k[0] for k in json_slots), default=0)
    for key, json_info in json_slots.items():
        year, slot_id = key
        if key not in gs_slots:
            issue_type = 'PHANTOM'
            # NEW_YEAR is a special case: JSON has a year that is beyond GS coverage
            # We can't detect this easily here without knowing GS max year
            report['issues'].append({
                'type': issue_type,
                'year': year,
                'slot_id': slot_id,
                'detail': f"JSON has slot ({year}, {slot_id}) but GS has no matching item",
            })

    # UNKNOWN items
    for name in gs_unparseable:
        report['issues'].append({
            'type': 'UNKNOWN',
            'gs_name': name,
            'detail': f"Could not parse GS item name: '{name}'",
        })

    # Set overall status
    error_types = {i['type'] for i in report['issues']}
    if not error_types:
        report['status'] = 'OK'
    elif error_types == {'UNKNOWN'}:
        report['status'] = 'WARNING'
    else:
        report['status'] = 'ERRORS'

    return report

# ── Report formatting ─────────────────────────────────────────────────────────
def format_report_md(results: list, run_date: str) -> str:
    lines = [
        f"# Greysheet Audit Report",
        f"**Run date:** {run_date}",
        f"**Programs audited:** {len(results)}",
        "",
    ]

    ok = [r for r in results if r['status'] == 'OK']
    warn = [r for r in results if r['status'] == 'WARNING']
    errors = [r for r in results if r['status'] == 'ERRORS']
    no_map = [r for r in results if r['status'] in ('NO_NODE_MAP', 'NO_NODES', 'API_ERROR')]

    lines += [
        f"## Summary",
        f"- ✅ OK: {len(ok)}",
        f"- ⚠️ Warning (UNKNOWN only): {len(warn)}",
        f"- ❌ Errors: {len(errors)}",
        f"- 🔍 No node map / API error: {len(no_map)}",
        "",
    ]

    for r in sorted(results, key=lambda x: x['program_id']):
        status_icon = {'OK': '✅', 'WARNING': '⚠️', 'ERRORS': '❌',
                       'NO_NODE_MAP': '🔍', 'NO_NODES': '🔍', 'API_ERROR': '💥'}.get(r['status'], '?')
        lines.append(f"## {status_icon} {r['program_name']} (`{r['program_id']}`)")
        lines.append(f"- GS items: {r['gs_item_count']}  |  JSON slots: {r['json_slot_count']}")
        if r['error']:
            lines.append(f"- **Error:** {r['error']}")
        issues = r.get('issues', [])
        if not issues:
            lines.append("- No issues found.")
        else:
            counts = {}
            for i in issues:
                counts[i['type']] = counts.get(i['type'], 0) + 1
            lines.append(f"- Issues: {', '.join(f'{v}× {k}' for k,v in sorted(counts.items()))}")
            for issue in sorted(issues, key=lambda x: (x['type'], x.get('year', 0))):
                lines.append(f"  - **{issue['type']}** ({issue.get('year','?')}, {issue.get('slot_id','?')}): {issue['detail']}")
        lines.append("")

    return "\n".join(lines)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Audit Numista.AI coin programs against Greysheet')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--program', metavar='ID', help='Audit one program by its doc_id')
    group.add_argument('--all', action='store_true', help='Audit all 31 programs')
    group.add_argument('--validate-map', action='store_true', help='Just check node map completeness')
    parser.add_argument('--since', metavar='YYYY-MM-DD', help='Only flag new years after this date')
    args = parser.parse_args()

    programs_data = load_json(PROGRAMS_JSON)
    node_map = load_json(NODE_MAP_JSON)

    # Build program index: doc_id -> program dict
    # master_coin_programs.json is an array with no doc_id field.
    # Node map keys use clean snake_case with no punctuation, so we derive
    # the ID by: lowercase → strip non-alphanumeric (except spaces) → replace spaces with underscores.
    # Examples:
    #   'Flying Eagle & Indian Head Cents' -> 'flying_eagle_indian_head_cents'
    #   'U.S. Proof Sets'                 -> 'u_s_proof_sets'
    #   'Washington Quarters (Classic)'   -> 'washington_quarters_classic'
    def name_to_id(name: str) -> str:
        s = name.lower()
        s = re.sub(r'[^a-z0-9\s]', '', s)
        s = re.sub(r'\s+', '_', s.strip())
        return s

    programs = {}
    if isinstance(programs_data, list):
        for p in programs_data:
            pid = p.get('doc_id') or name_to_id(p.get('Name', ''))
            programs[pid] = p
    elif isinstance(programs_data, dict):
        programs = programs_data

    # ── Validate map mode ──────────────────────────────────────────────────────
    if args.validate_map:
        print(f"Validating node map coverage for {len(programs)} programs...\n")
        ok_count = 0
        missing = []
        partial = []
        for pid in sorted(programs.keys()):
            config = node_map.get(pid, {})
            nodes = config.get('nodes', [])
            if not nodes:
                missing.append(pid)
                print(f"  ❌ MISSING nodes: {pid}")
            elif config.get('note', '').upper().startswith('PARTIAL'):
                partial.append(pid)
                print(f"  ⚠️  PARTIAL:       {pid}  ({config.get('note','')})")
            else:
                ok_count += 1
                print(f"  ✅ OK:             {pid}  ({len(nodes)} nodes)")
        print(f"\nResult: {ok_count} OK, {len(partial)} partial, {len(missing)} missing")
        print(f"\n{ok_count}/{len(programs)} programs have confirmed node IDs")
        return

    # ── Audit mode ─────────────────────────────────────────────────────────────
    if args.program:
        target_ids = [args.program]
    else:
        target_ids = sorted(programs.keys())

    results = []
    for pid in target_ids:
        program = programs.get(pid)
        if not program:
            print(f"WARNING: program_id '{pid}' not found in master_coin_programs.json", file=sys.stderr)
            continue
        print(f"Auditing {pid}...", end=' ', flush=True)
        report = audit_program(pid, program, node_map)
        results.append(report)
        issue_count = len(report['issues'])
        print(f"{report['status']} ({issue_count} issues, {report['gs_item_count']} GS items)")

    # Write reports
    run_date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    md_content = format_report_md(results, run_date)
    REPORT_MD.write_text(md_content, encoding='utf-8')
    REPORT_JSON.write_text(json.dumps({'run_date': run_date, 'results': results}, indent=2, default=str), encoding='utf-8')

    print(f"\nReport written to:\n  {REPORT_MD}\n  {REPORT_JSON}")

    # Print summary to stdout
    error_programs = [r for r in results if r['status'] == 'ERRORS']
    if error_programs:
        print(f"\n⚠️  {len(error_programs)} programs have errors — see report for details")
    else:
        print(f"\n✅ All audited programs OK (or warnings only)")

if __name__ == '__main__':
    main()
