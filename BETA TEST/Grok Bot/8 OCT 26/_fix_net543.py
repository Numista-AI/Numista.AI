from pathlib import Path
import re
base = Path(r'C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\8 OCT 26')
files = [
    base/'RADIO NET'/'NET-543_GROKCOS-to-AGCOS-ARGON-FT_COS-EXECUTE-PLAN-V31-MINTPACK_OVER.md',
    base/'RADIO NET'/'WAKES'/'WAKE_AGCOS_NET543-PLAN-V31-EXECUTE-NOW_20261026-1447.md',
    base/'BATONS'/'COS_EXECUTE_P7_GATE_MINTPACK_PLAN_V31.md',
]
for f in files:
    if not f.exists():
        print('MISSING', f)
        continue
    t = f.read_text(encoding='utf-8')
    orig = t
    t = t.replace('set_cost_label: ".00 (25 @ .44)"', 'set_cost_label: "$61.00 (25 @ $2.44)"')
    t = t.replace('visible **$61.00 (25 @ .44)**', 'visible **`$61.00 (25 @ $2.44)`**')
    t = t.replace('.00 (25 @ .44)', '$61.00 (25 @ $2.44)')
    t = t.replace('child catalog `` /', 'child catalog `$61` /')
    t = t.replace('\u0005', '')  # unlikely
    t = t.replace('\x15', '')
    # section sign replacements that became control char
    t = t.replace('\u0015' + '5', '\u00a75')
    t = t.replace('\u0015' + '6', '\u00a76')
    # also literal replacement of common corruption
    import codecs
    # Fix section marks showing as weird char before 5/6
    t = re.sub(r'.5 mechanisms', '\u00a75 mechanisms', t, count=3)
    t = re.sub(r'Plan v3\.1 .5', 'Plan v3.1 \u00a75', t)
    t = re.sub(r'EXECUTE Plan v3\.1 .5', 'EXECUTE Plan v3.1 \u00a75', t)
    t = re.sub(r'matches \*\*.6\*\*', 'matches **\u00a76**', t)
    t = re.sub(r'with .6 proof', 'with \u00a76 proof', t)
    t = re.sub(r'proof \(.6\)', 'proof (\u00a76)', t)
    if t != orig:
        f.write_text(t, encoding='utf-8')
        print('FIXED', f.name)
    else:
        print('NOCHANGE', f.name)
    for line in f.read_text(encoding='utf-8').splitlines():
        if '2.44' in line or '61.00' in line or 'set_cost' in line.lower() or 'shipping_amount' in line:
            print(' ', line[:120])
