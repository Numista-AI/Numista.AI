#!/usr/bin/env python3
"""
tools/catalog/pii_gate_validator.py
Automated fail-closed PII and internal token scanner for public catalog JSON.
Enforces Section 3.3 and C1-C4 rules with negative planted-leak tests.
"""

import argparse
import json
import os
import re
import sys

DEFAULT_INPUT_PATH = os.path.join(
    "numista_mobile", "assets", "catalog", "catalog_public_v1.json"
)

# Section 3.3-W: Exact whitelist (Case-sensitive)
EXACT_WHITELIST = [
    "National Numismatic Collection",
    "si.edu/collections/",
    "si.edu/collection/",
    "metmuseum.org/art/collection/",
    "numismatics.org/collection/",
    "numismatics.org/collectionimages/",
    "coin collection; public domain",
    "Josiah K. Lilly Jr. Collection",
    "acquired with the Lilly Collection",
    "collectors still hunt",
    "a-collectors-guide",
]

# Forbidden tokens (case-insensitive unless specified)
FORBIDDEN_TOKENS = [
    r"collection",
    r"collector",
    r"derived",
    r"seed",
    r"owner",
    r"album",
    r"gs://",
    r"googleapis",
    r"users/",
    r"/workspace",
    r"seed_images/",
    r"\bAJ\b",
]

def mask_whitelisted_text(text):
    """Masks exact whitelist occurrences so they do not trigger forbidden token hits."""
    masked = text
    for wl in EXACT_WHITELIST:
        if wl in masked:
            # Replace with equivalent length of safe characters
            masked = masked.replace(wl, " " * len(wl))
    return masked

def scan_text_for_leaks(text):
    """
    Scans text for forbidden tokens after masking whitelist.
    Returns list of (token, match_text, context_snippet) hits.
    """
    masked = mask_whitelisted_text(text)
    hits = []
    for token_pattern in FORBIDDEN_TOKENS:
        if token_pattern == r"\bAJ\b":
            # Word-bounded AJ check (case-sensitive)
            flags = 0
        else:
            # Case-insensitive check
            flags = re.IGNORECASE

        for m in re.finditer(token_pattern, masked, flags=flags):
            start = max(0, m.start() - 30)
            end = min(len(text), m.end() + 30)
            snippet = text[start:end].replace("\n", " ")
            hits.append((token_pattern, m.group(0), snippet))
    return hits

def run_dry_run(input_path):
    print(f"--- Running Dry-Run on {input_path} ---")
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Census of whitelist hits
    print("§3.3-W Whitelist Matches in post-sanitization catalog:")
    for wl in EXACT_WHITELIST:
        count = text.count(wl)
        print(f"  [{count:3d} hits] '{wl}'")

    # Scan for non-whitelisted leaks
    leaks = scan_text_for_leaks(text)
    print(f"\nNon-whitelisted hits: {len(leaks)}")
    if leaks:
        for pat, matched, snip in leaks[:10]:
            print(f"  FAIL: token='{pat}' matched='{matched}' snippet='...{snip}...'")
        return 1
    print("SUCCESS: Zero non-whitelisted token leaks detected.")
    return 0

def run_negative_test(input_path):
    print("--- Running Planted-Leak Negative Test ---")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        clean_text = f.read()

    test_tokens = [
        ("collection", "from a private collection"),
        ("collector", "donated by a private collector"),
        ("derived", "this field is collection-derived"),
        ("seed", "originating from seed images"),
        ("owner", "owner names withheld"),
        ("album", "stored in a collector album"),
        ("gs://", "gs://numista-vault-bucket/test.jpg"),
        ("googleapis", "https://storage.googleapis.com/test"),
        ("users/", "C:/users/ericd/test.jpg"),
        ("/workspace", "/workspace/seed/test.jpg"),
        ("seed_images/", "assets/catalog/seed_images/test.jpg"),
        (r"\bAJ\b", "certified by AJ for grading"),
    ]

    all_passed = True
    for token_id, planted_str in test_tokens:
        corrupted_text = clean_text + f"\n// PLANTED: {planted_str}\n"
        leaks = scan_text_for_leaks(corrupted_text)
        if not leaks:
            print(f"  FAIL: Planted leak '{planted_str}' for token '{token_id}' was NOT detected!")
            all_passed = False
        else:
            print(f"  PASS: Planted leak for '{token_id}' successfully detected ({len(leaks)} hit).")

    if all_passed:
        print("ALL NEGATIVE TESTS PASSED: Fail-closed gate verified functional.")
        return 0
    else:
        print("NEGATIVE TESTS FAILED: Gate did not catch all planted leaks.")
        return 1

def main():
    parser = argparse.ArgumentParser(description="PII & Internal Token Gate Validator")
    parser.add_argument("--input", default=DEFAULT_INPUT_PATH, help="Path to catalog JSON")
    parser.add_argument("--dry-run", action="store_true", help="Perform census dry-run")
    parser.add_argument("--negative-test", action="store_true", help="Run planted-leak verification")
    args = parser.parse_args()

    if args.negative_test:
        sys.exit(run_negative_test(args.input))

    if args.dry_run:
        sys.exit(run_dry_run(args.input))

    print(f"Validating catalog at: {args.input}")
    if not os.path.exists(args.input):
        print(f"ERROR: Input file does not exist: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    leaks = scan_text_for_leaks(text)
    if leaks:
        print(f"GATE FAILED: {len(leaks)} non-whitelisted leaks detected!", file=sys.stderr)
        for pat, matched, snip in leaks:
            print(f"  Hit: token='{pat}' matched='{matched}' in: '...{snip}...'", file=sys.stderr)
        sys.exit(1)

    print("GATE PASSED: 0 non-whitelisted leaks detected. Catalog is clean.")
    sys.exit(0)

if __name__ == "__main__":
    main()
