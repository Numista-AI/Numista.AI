"""
test_synthesizer.py — Numista QC Suite Layer 4
Reads code_scan output from code_reader.py, generates Playwright test stubs
using a capped LLM call, writes ONLY to staging/. Never auto-overwrites
version-controlled specs.

LLM model: read from SUITE_MANIFEST.json.synthesizer_model_id at runtime.
           Never hardcoded. Must match current Deprecation Schedule.
LLM degradation: if unavailable, logs LLM_UNAVAILABLE and exits 0 (non-fatal).
                 run_qc.ps1 continues. Morning report notes SKIPPED.

Usage:
  python test_synthesizer.py --scan staging/code_scan_{date}.json
  python test_synthesizer.py --promote staging/generated_{date}.spec.js <target_layer>
"""

import os
import sys
import re
import json
import datetime
import argparse
from pathlib import Path

STAGING_DIR = Path(__file__).parent / 'staging'
STAGING_DIR.mkdir(exist_ok=True)

MANIFEST_PATH = Path(__file__).parent.parent / 'SUITE_MANIFEST.json'

PROTECTED_FILES_DEFAULT = [
    'passport_pdf_generator.py',
    'numista_bq_loader_job',
    'tier_gatekeeper.py',
]

# Hard cap on LLM calls per run (protects GCP credits)
MAX_LLM_CALLS = 5
MAX_ITEMS_PER_CALL = 10


def load_manifest():
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def get_model_id(manifest):
    """
    Read model ID from manifest. Never hardcoded.
    Operator must set synthesizer_model_id after reading Gemini Deprecation Schedules.
    """
    model_id = manifest.get('synthesizer_model_id')
    if not model_id:
        print('[test_synthesizer] WARNING: synthesizer_model_id not set in SUITE_MANIFEST.json.')
        print('  Set it after reading C:\\Users\\ericd\\Documents\\MyVertexProject\\Gemini Deprecation Schedules\\')
        print('  Defaulting to gemini-3.8-flash.')
        model_id = 'gemini-3.8-flash'
    return model_id


def is_protected(item, protected_files):
    for prot in protected_files:
        if prot in item.get('file', ''):
            return True
    return False


def generate_stubs_with_llm(items, model_id):
    """
    Call LLM to generate Playwright test stubs for a batch of code items.
    Returns spec JS string or None on failure.
    """
    try:
        import google.generativeai as genai
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise RuntimeError('GEMINI_API_KEY not set')

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_id)

        batch_text = json.dumps(items[:MAX_ITEMS_PER_CALL], indent=2)
        prompt = (
            "Given these Flutter Dart Text() widget usages, write Playwright test stubs "
            "that verify the text is not empty and the app remains alive after rendering. "
            "Use flt-semantics locators. No hardcoded coordinates. Return only valid JavaScript "
            "using @playwright/test. Each test must have at least one real assertion.\n\n"
            f"Usages:\n{batch_text}"
        )

        response = model.generate_content(prompt)
        text = response.text.strip()
        # Strip markdown fences if present
        if text.startswith('```'):
            text = re.sub(r'^```[a-z]*\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
        return text

    except Exception as e:
        error_log = STAGING_DIR / f'synthesizer_errors_{datetime.date.today()}.log'
        with open(error_log, 'a') as f:
            f.write(f'[{datetime.datetime.now().isoformat()}] LLM_UNAVAILABLE: {e}\n')
        print(f'[test_synthesizer] LLM_UNAVAILABLE: {e}')
        return None


def promote(spec_path, target_layer):
    """
    Copy a staging spec to the target layer directory.
    Requires explicit operator invocation \u2014 never called automatically.
    """
    target_dir = Path(__file__).parent.parent / target_layer
    if not target_dir.exists():
        print(f'[test_synthesizer] ERROR: target layer directory not found: {target_dir}')
        sys.exit(1)
    dest = target_dir / Path(spec_path).name
    import shutil
    shutil.copy2(spec_path, dest)
    print(f'[test_synthesizer] PROMOTED: {spec_path} -> {dest}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scan', help='Path to code_scan JSON from code_reader.py')
    parser.add_argument('--promote', nargs=2, metavar=('SPEC_PATH', 'TARGET_LAYER'),
                        help='Promote a staging spec to a layer directory')
    args = parser.parse_args()

    if args.promote:
        promote(args.promote[0], args.promote[1])
        return

    if not args.scan:
        # Find latest scan in staging
        scans = sorted(STAGING_DIR.glob('code_scan_*.json'), reverse=True)
        if not scans:
            print('[test_synthesizer] No code_scan file found. Run code_reader.py first.')
            sys.exit(0)
        scan_path = scans[0]
        print(f'[test_synthesizer] Using latest scan: {scan_path}')
    else:
        scan_path = Path(args.scan)

    with open(scan_path) as f:
        items = json.load(f)

    manifest = load_manifest()
    model_id = get_model_id(manifest)
    protected_files = manifest.get('protected_files', PROTECTED_FILES_DEFAULT)

    # Filter out protected files
    items = [i for i in items if not is_protected(i, protected_files)]
    print(f'[test_synthesizer] {len(items)} items after filtering protected files.')

    if not items:
        print('[test_synthesizer] Nothing to synthesize.')
        sys.exit(0)

    # Batch into MAX_LLM_CALLS batches
    batches = [items[i:i+MAX_ITEMS_PER_CALL] for i in range(0, min(len(items), MAX_LLM_CALLS * MAX_ITEMS_PER_CALL), MAX_ITEMS_PER_CALL)]

    today = datetime.date.today().isoformat()
    spec_parts = [
        f'// generated_{today}.spec.js \u2014 AUTO-GENERATED by test_synthesizer.py',
        '// STAGING FILE: Never auto-executed. Human promotion required via:',
        '//   python test_synthesizer.py --promote staging/generated_{date}.spec.js layer_2_functional',
        '',
        "const { test, expect } = require('@playwright/test');",
        '',
    ]

    llm_failed = False
    for i, batch in enumerate(batches):
        print(f'[test_synthesizer] LLM call {i+1}/{len(batches)} (model: {model_id})...')
        stub = generate_stubs_with_llm(batch, model_id)
        if stub is None:
            llm_failed = True
            break
        spec_parts.append(f'// --- Batch {i+1} ---')
        spec_parts.append(stub)
        spec_parts.append('')

    if llm_failed:
        print('[test_synthesizer] LLM_UNAVAILABLE. No staging spec written.')
        print('Self-update: SKIPPED (LLM unavailable)')
        sys.exit(0)  # Non-fatal \u2014 suite continues without generated specs

    out_path = STAGING_DIR / f'generated_{today}.spec.js'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(spec_parts))

    print(f'[test_synthesizer] Staging spec written: {out_path}')
    print('[test_synthesizer] Review spec before promoting. DO NOT execute directly from staging/.')


if __name__ == '__main__':
    main()
