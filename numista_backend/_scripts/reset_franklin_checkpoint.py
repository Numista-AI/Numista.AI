# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
reset_franklin_checkpoint.py
─────────────────────────────────────────────────────────────────────────────
Removes all franklin_*.png entries from the kaggle_vision_checkpoint.json so
they get re-processed on the next Vision Pass run (with the fixed prompt that
now includes franklin-half-dollar as a valid program).

Run AFTER Session 2 stops (at 11:03) and BEFORE starting Session 3.

Usage:
    python _scripts/reset_franklin_checkpoint.py --dry-run
    python _scripts/reset_franklin_checkpoint.py
"""
import json, argparse, re
from pathlib import Path

CHECKPOINT = Path("_scripts/kaggle_vision_checkpoint.json")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not CHECKPOINT.exists():
        print("No checkpoint file found.")
        return

    with open(CHECKPOINT, encoding="utf-8") as f:
        cp = json.load(f)

    before = len(cp["processed"])

    # Remove all franklin entries (keep everything else)
    to_remove = [p for p in cp["processed"] if re.search(r'franklin', p, re.I)]
    kept      = [p for p in cp["processed"] if p not in to_remove]

    print(f"Checkpoint entries before : {before:,}")
    print(f"Franklin entries found    : {len(to_remove)}")
    print(f"Entries after removal     : {len(kept):,}")

    if args.dry_run:
        print("\nDRY RUN — no changes made.")
        if to_remove:
            print("Sample entries that would be removed:")
            for p in to_remove[:5]:
                print(f"  {p}")
        return

    cp["processed"] = kept
    # Reset skip/indexed counts conservatively (will re-accumulate on next run)
    cp["skipped"] = max(0, cp.get("skipped", 0) - len(to_remove))

    with open(CHECKPOINT, "w", encoding="utf-8") as f:
        json.dump(cp, f, indent=2)

    print(f"\n✅ Checkpoint updated — {len(to_remove)} franklin entries removed.")
    print(f"   Next Vision Pass will re-process all franklin_*.png images")
    print(f"   using the fixed prompt with 'franklin-half-dollar' included.")

if __name__ == "__main__":
    main()
