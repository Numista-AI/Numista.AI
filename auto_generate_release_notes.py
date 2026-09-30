#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_generate_release_notes.py — Automated Release Notes Generator
===================================================================
Automatically extracts recent git commits since the last logged release,
formats them into clean bullet points, increments the version number, and updates
both home_dashboard.dart and RELEASE_NOTES.md.

Can be triggered automatically:
  1. In GitHub Actions (.github/workflows/deploy-production.yml) right before `flutter build web`
  2. Via git pre-push hook (.git/hooks/pre-push)
  3. Manually: python auto_generate_release_notes.py
"""

import subprocess
import re
import sys
from datetime import date
from pathlib import Path

import add_release_note as arn

def get_k_app_version() -> str:
    """Extract kAppVersion constant from numista_mobile/lib/constants.dart."""
    constants_file = Path(__file__).parent / "numista_mobile" / "lib" / "constants.dart"
    if not constants_file.exists():
        return ""
    text = constants_file.read_text(encoding="utf-8")
    m = re.search(r"const\s+String\s+kAppVersion\s*=\s*['\"]([^'\"]+)['\"];", text)
    return m.group(1).strip() if m else ""

def get_last_release_info() -> tuple[str, str]:
    """Extract (last_version, last_date) from RELEASE_NOTES.md."""
    if not arn.RELEASE_NOTES.exists():
        return ("v4.0", "2026-01-01")
    text = arn.RELEASE_NOTES.read_text(encoding="utf-8")
    m = re.search(r"^## (v[\d.]+)\s*—\s*(\d{4}-\d{2}-\d{2})", text, re.MULTILINE)
    if m:
        return (m.group(1), m.group(2))
    return ("v4.0", "2026-01-01")

def get_commits_since_last_release(since_date: str) -> list[str]:
    """Fetch git commit messages since the given date (excluding release notes commits)."""
    try:
        res = subprocess.run(
            ["git", "log", f"--after={since_date}T00:00:00", "--oneline"],
            capture_output=True, text=True, check=True
        )
        lines = res.stdout.strip().splitlines()
        
        bullets = []
        for line in lines:
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            msg = parts[1].strip()
            
            # Filter out non-user-facing commits
            if (msg.startswith("release(") or 
                msg.startswith("chore: auto-backup") or 
                msg.startswith("Merge branch") or
                "walkthrough.md" in msg):
                continue
                
            # Clean conventional commit prefixes (e.g. feat(billing): message -> Billing: message)
            cleaned = re.sub(
                r"^(feat|fix|refactor|docs|style|perf|test|chore)\((.*?)\):\s*",
                lambda m: f"{m.group(2).capitalize()}: ",
                msg,
                flags=re.IGNORECASE
            )
            cleaned = re.sub(r"^(feat|fix|refactor|docs|style|perf|test|chore):\s*", "", cleaned, flags=re.IGNORECASE)

            # Strip any REQ tags (e.g. (REQ-023H), (REQ_016), REQ-023H) so they never leak into release notes
            cleaned = re.sub(r"\s*\(REQ[-_][^)]+\)", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\bREQ[-_]\w+\b", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

            if cleaned:
                cleaned = cleaned[0].upper() + cleaned[1:]
                if cleaned not in bullets:
                    bullets.append(cleaned)
                    
        return bullets
    except Exception as e:
        print(f"Warning: could not fetch git log: {e}", file=sys.stderr)
        return []

def main():
    last_version, last_date = get_last_release_info()
    k_app_version = get_k_app_version()
    today = date.today().isoformat()
    force = "--force" in sys.argv
    
    # If kAppVersion already has a release notes entry, skip auto-generation (REQ-023H)
    if not force and k_app_version:
        release_notes_text = arn.RELEASE_NOTES.read_text(encoding="utf-8") if arn.RELEASE_NOTES.exists() else ""
        if re.search(rf"^##\s+{re.escape(k_app_version)}\b", release_notes_text, re.MULTILINE):
            print(f"Skipping auto-generation: {k_app_version} already has a release notes entry.")
            return

    commits = get_commits_since_last_release(last_date)
    if not commits and not force:
        print(f"No new commits found since last release ({last_version} on {last_date}).")
        return

    new_version = k_app_version if (k_app_version and k_app_version != last_version) else arn.suggest_next_version(last_version)
    
    # Title from first feature scope or generic title
    title = "System Performance & Feature Updates"
    for c in commits:
        if ":" in c:
            scope = c.split(":", 1)[0].capitalize()
            title = f"{scope} Enhancements & Platform Updates"
            break
            
    display_bullets = commits[:8]
    if not display_bullets and not force:
        print("No user-facing changes to log.")
        return
        
    if force and not display_bullets:
        display_bullets = ["Automated build update and maintenance pass."]

    print(f"Auto-generating release notes for {new_version} ({today})...")
    dart_block = arn.build_dart_entry(new_version, today, title, display_bullets)
    md_block = arn.build_md_entry(new_version, today, title, display_bullets)
    
    ok_dart = arn.patch_dart(dart_block)
    ok_md = arn.patch_md(md_block)
    
    if ok_dart and ok_md:
        print(f"✅ Automatically updated {new_version} in home_dashboard.dart and RELEASE_NOTES.md")
    else:
        print("❌ Automation patch failed.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
