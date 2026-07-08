#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
# Force UTF-8 stdout on Windows so checkmarks print cleanly
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
add_release_note.py — Numista.AI Release Notes Automation
==========================================================
Prepends a new release entry to home_dashboard.dart AND appends
it to RELEASE_NOTES.md in one step.

Usage (interactive):
    python add_release_note.py

Usage (non-interactive / agent mode):
    python add_release_note.py \
        --version "v4.1" \
        --date "2026-07-15" \
        --description "My Feature Name" \
        --changes "Fix A|Fix B|Fix C"

The pipe character | separates bullet points in --changes.
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

# ── Paths (relative to this script) ──────────────────────────────────────────
PROJECT_ROOT   = Path(__file__).parent
DART_FILE      = PROJECT_ROOT / "numista_mobile" / "lib" / "screens" / "home_dashboard.dart"
RELEASE_NOTES  = PROJECT_ROOT / "RELEASE_NOTES.md"

# ── Regex: find the opening of _versionHistory ───────────────────────────────
VERSION_LIST_RE = re.compile(
    r"(const _versionHistory = <_Release>\[)\r?\n",
    re.MULTILINE
)

# Detect the current latest version from RELEASE_NOTES.md
LATEST_VERSION_RE = re.compile(r"^## (v[\d.]+[^\s]*)", re.MULTILINE)

def get_current_version() -> str:
    """Read the first ## vX.Y line from RELEASE_NOTES.md."""
    if not RELEASE_NOTES.exists():
        return "v0.0"
    text = RELEASE_NOTES.read_text(encoding="utf-8")
    m = LATEST_VERSION_RE.search(text)
    return m.group(1) if m else "v0.0"

def suggest_next_version(current: str) -> str:
    """Auto-increment the last numeric segment (e.g. v4.0 → v4.1)."""
    m = re.match(r"(v\d+\.)(\d+)(.*)", current)
    if m:
        return f"{m.group(1)}{int(m.group(2)) + 1}{m.group(3)}"
    return current + ".1"

def build_dart_entry(version: str, dt: str, description: str, changes: list[str]) -> str:
    """Return a _Release(...) Dart block string."""
    escaped = [c.replace("'", "\\'") for c in changes]
    bullets  = "\n".join(f"      '{c}'," for c in escaped)
    return (
        f"  _Release(\n"
        f"    version: '{version}',\n"
        f"    date: '{dt}',\n"
        f"    description: '{description.replace(chr(39), chr(92)+chr(39))}',\n"
        f"    isLatest: true,\n"
        f"    changes: [\n"
        f"{bullets}\n"
        f"    ],\n"
        f"  ),"
    )

def build_md_entry(version: str, dt: str, description: str, changes: list[str]) -> str:
    """Return a markdown ## block for RELEASE_NOTES.md."""
    bullets = "\n".join(f"- {c}" for c in changes)
    return (
        f"## {version} — {dt}\n"
        f"**{description}**\n\n"
        f"{bullets}\n"
    )

def patch_dart(entry_block: str) -> bool:
    """
    Inject the new _Release block at the top of _versionHistory,
    clear isLatest on the previously-first entry, and write back.
    """
    if not DART_FILE.exists():
        print(f"ERROR: Cannot find {DART_FILE}", file=sys.stderr)
        return False

    text = DART_FILE.read_text(encoding="utf-8")

    # 1. Flip the old top-entry's isLatest: true → false
    text = re.sub(
        r"(const _versionHistory = <_Release>\[\r?\n  _Release\(.*?isLatest: )true",
        lambda m: m.group(0).replace("isLatest: true", "isLatest: false"),
        text,
        count=1,
        flags=re.DOTALL
    )

    # 2. Inject the new entry at the top of the list
    match = VERSION_LIST_RE.search(text)
    if not match:
        print("ERROR: Could not find _versionHistory list in home_dashboard.dart", file=sys.stderr)
        return False

    insert_pos = match.end()
    text = text[:insert_pos] + entry_block + "\n" + text[insert_pos:]

    DART_FILE.write_text(text, encoding="utf-8")
    return True

def patch_md(entry_block: str) -> bool:
    """
    Prepend the new entry after the header/divider in RELEASE_NOTES.md.
    """
    if not RELEASE_NOTES.exists():
        RELEASE_NOTES.write_text(
            "# Numista.AI — Release Notes\n\n---\n\n" + entry_block + "\n",
            encoding="utf-8"
        )
        return True

    text = RELEASE_NOTES.read_text(encoding="utf-8")

    # Insert after the first --- divider line
    divider_match = re.search(r"^---\s*\n", text, re.MULTILINE)
    if divider_match:
        pos = divider_match.end()
        text = text[:pos] + "\n" + entry_block + "\n" + text[pos:]
    else:
        text = entry_block + "\n\n" + text

    RELEASE_NOTES.write_text(text, encoding="utf-8")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Add a new release note entry to Numista.AI"
    )
    parser.add_argument("--version",     default=None, help="Version string, e.g. v4.1")
    parser.add_argument("--date",        default=None, help="ISO date, e.g. 2026-07-15 (defaults to today)")
    parser.add_argument("--description", default=None, help="One-line release title")
    parser.add_argument("--changes",     default=None, help="Pipe-separated bullet points")
    args = parser.parse_args()

    current = get_current_version()
    suggested = suggest_next_version(current)

    # ── Gather inputs ─────────────────────────────────────────────────────────
    if args.version:
        version = args.version.strip()
    else:
        version = input(f"Version [{suggested}]: ").strip() or suggested

    if args.date:
        release_date = args.date.strip()
    else:
        today = date.today().isoformat()
        release_date = input(f"Release date [{today}]: ").strip() or today

    if args.description:
        description = args.description.strip()
    else:
        description = input("Description (one-line title): ").strip()
        if not description:
            print("ERROR: Description is required.", file=sys.stderr)
            sys.exit(1)

    if args.changes:
        changes = [c.strip() for c in args.changes.split("|") if c.strip()]
    else:
        print("Enter change bullets one per line. Empty line to finish:")
        changes = []
        while True:
            line = input("  • ").strip()
            if not line:
                break
            changes.append(line)
        if not changes:
            print("ERROR: At least one change bullet is required.", file=sys.stderr)
            sys.exit(1)

    # ── Build blocks ─────────────────────────────────────────────────────────
    dart_block = build_dart_entry(version, release_date, description, changes)
    md_block   = build_md_entry(version, release_date, description, changes)

    # ── Preview ───────────────────────────────────────────────────────────────
    print("\n" + "-" * 60)
    print("PREVIEW — Dart entry:")
    print(dart_block)
    print("-" * 60)
    print("PREVIEW — Markdown entry:")
    print(md_block)
    print("-" * 60)

    # Auto-confirm in non-interactive mode (all flags supplied)
    if args.version and args.description and args.changes:
        confirm = "y"
    else:
        confirm = input("\nApply these changes? [y/N]: ").strip().lower()

    if confirm != "y":
        print("Aborted — no changes made.")
        sys.exit(0)

    # ── Apply ─────────────────────────────────────────────────────────────────
    ok_dart = patch_dart(dart_block)
    ok_md   = patch_md(md_block)

    if ok_dart and ok_md:
        print(f"\n✅  {version} added successfully!")
        print(f"    • home_dashboard.dart updated (new LATEST = {version})")
        print(f"    • RELEASE_NOTES.md updated")
        print(f"\nNext steps:")
        print(f"    1. git add numista_mobile/lib/screens/home_dashboard.dart RELEASE_NOTES.md")
        print(f"    2. git commit -m \"release({version}): {description}\"")
        print(f"    3. git push origin main")
        print(f"    4. Deploy to Flutter Web / Cloud Run as appropriate.")
    else:
        print("\n❌  One or more patches failed — check errors above.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
