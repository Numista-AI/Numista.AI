"""
code_reader.py — Numista QC Suite Layer 4
AST-approximation scan of numista_mobile/lib/ (Dart source).
Finds Text() widget calls and their argument expressions.
Does NOT execute Dart code. Does NOT modify any source file.
Protected files are skipped via SUITE_MANIFEST.json allowlist.

Output: staging/code_scan_{date}.json (never auto-executed)
"""

import os
import re
import sys
import json
import datetime
from pathlib import Path

FLUTTER_SRC = Path(r'C:\Users\ericd\Documents\MyVertexProject\numista_mobile\lib')
STAGING_DIR = Path(__file__).parent / 'staging'
STAGING_DIR.mkdir(exist_ok=True)

# Load protected files from manifest
MANIFEST_PATH = Path(__file__).parent.parent / 'SUITE_MANIFEST.json'

def load_protected_files():
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH) as f:
            return json.load(f).get('protected_files', [])
    return []

# Regex targeting Dart Text() widget constructor calls
# Matches: Text('literal') or Text(variable) or Text(expression)
TEXT_WIDGET_RE = re.compile(
    r'\bText\s*\(\s*'
    r'(?:'
    r"'([^'\\]*(?:\\.[^'\\]*)*)'"    # single-quoted string literal
    r'|"([^"\\]*(?:\\.[^"\\]*)*)"'   # double-quoted string literal
    r'|(\$\{[^}]+\}|\w+(?:\.\w+)*)'  # variable or interpolation
    r')\s*[,)]'
)


def is_protected(filepath, protected_files):
    name = Path(filepath).name
    for prot in protected_files:
        if prot in str(filepath) or prot == name:
            return True
    return False


def scan_file(dart_file, protected_files):
    if is_protected(dart_file, protected_files):
        return []

    results = []
    try:
        source = dart_file.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        return [{'file': str(dart_file), 'error': str(e)}]

    for m in TEXT_WIDGET_RE.finditer(source):
        line_num = source[:m.start()].count('\n') + 1
        arg = m.group(1) or m.group(2) or m.group(3) or ''
        results.append({
            'file': str(dart_file.relative_to(FLUTTER_SRC)),
            'line': line_num,
            'widget_type': 'Text',
            'argument_expression': arg[:200],  # cap length
        })

    return results


def main():
    if not FLUTTER_SRC.exists():
        print(f'[code_reader] ERROR: Flutter source not found at {FLUTTER_SRC}')
        sys.exit(1)

    protected_files = load_protected_files()
    print(f'[code_reader] Protected files: {protected_files}')
    print(f'[code_reader] Scanning {FLUTTER_SRC}...')

    dart_files = list(FLUTTER_SRC.rglob('*.dart'))
    print(f'[code_reader] Found {len(dart_files)} Dart files.')

    all_results = []
    for f in dart_files:
        all_results.extend(scan_file(f, protected_files))

    print(f'[code_reader] Found {len(all_results)} Text() widget instances.')

    today = datetime.date.today().isoformat()
    out_path = STAGING_DIR / f'code_scan_{today}.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)

    print(f'[code_reader] Output written: {out_path}')
    print('[code_reader] Done. Pass code_scan output to test_synthesizer.py for spec generation.')


if __name__ == '__main__':
    main()
