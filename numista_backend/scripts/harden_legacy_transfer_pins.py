"""One-time hardening of pending LEGACY transfers: hash plaintext PINs (PLAN v1.2 section 6.3, N4).

DRY RUN BY DEFAULT. Applying writes to live Firestore, so it requires --apply AND --deploy-card DEC-###.
Usage:
    python scripts/harden_legacy_transfer_pins.py                      # dry run, prints counts only
    python scripts/harden_legacy_transfer_pins.py --apply --deploy-card DEC-123
Set TRANSFER_CLAIM_PEPPER in the environment first so the hashes are peppered.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write changes (needs --deploy-card)")
    ap.add_argument("--deploy-card", default="", help="DEPLOY card id, e.g. DEC-123")
    args = ap.parse_args()
    if args.apply and not re.fullmatch(r"DEC-\d{3,}", args.deploy_card or ""):
        print("REFUSED: --apply needs --deploy-card DEC-### (a live Firestore write requires its own DEPLOY card).")
        return 2
    if args.apply and not os.environ.get("TRANSFER_CLAIM_PEPPER"):
        print("REFUSED: set TRANSFER_CLAIM_PEPPER before applying so hashes are peppered.")
        return 2
    from google.cloud import firestore
    from services.transfer_service import harden_legacy_pins

    stats = harden_legacy_pins(firestore.Client(project="studio-9101802118-8c9a8"), apply=args.apply)
    print(("APPLIED " if args.apply else "DRY RUN ") + str(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())