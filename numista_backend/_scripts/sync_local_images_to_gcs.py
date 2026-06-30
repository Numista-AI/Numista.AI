r"""
sync_local_images_to_gcs.py
─────────────────────────────────────────────────────────────────────────────
Compares local "Manual downloaded Coin Images" folder against GCS and:
  1. Reports which local images are ALREADY in GCS (by filename match)
  2. Reports which local images are NEW (not in GCS)
  3. Uploads new images to the correct GCS folder
  4. Optionally deletes local images after confirmed upload

Usage:
    python sync_local_images_to_gcs.py --report-only       # just compare
    python sync_local_images_to_gcs.py --upload            # compare + upload new
    python sync_local_images_to_gcs.py --upload --delete   # upload + delete local copies

The script maps local subfolders to GCS destination prefixes:
    AJ's\          → reference_library/bulk_programs/aj_collection/
    si_quarters\   → reference_library/bulk_programs/si_quarters/
    US Mint\       → reference_library/bulk_programs/us_mint_manual/
    wikipedia\...  → reference_library/bulk_programs/{subfolder}/
"""

import os
import sys
import argparse
import hashlib
from pathlib import Path
from google.cloud import storage
import google.auth

# ─── Config ───────────────────────────────────────────────────────────────────

PROJECT      = "studio-9101802118-8c9a8"
LOCAL_ROOT   = r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images"
GCS_BUCKET   = "numista-reference-library"
GCS_PREFIX   = "reference_library/bulk_programs"

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff"}

# Map local top-level folder names → GCS subfolder names
FOLDER_MAP = {
    "AJ's":        "aj_collection",
    "si_quarters": "si_quarters",
    "US Mint":     "us_mint_manual",
    "wikipedia":   None,  # Use subfolder name directly (American_Women_quarters, etc.)
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def is_image(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTENSIONS

def gcs_dest_prefix(local_path: Path, local_root: Path) -> str:
    """Determine GCS prefix for a given local file."""
    rel = local_path.relative_to(local_root)
    parts = rel.parts  # e.g. ("US Mint", "HighRes_Scrape", "file.jpg")

    top_folder = parts[0]
    gcs_sub = FOLDER_MAP.get(top_folder)

    if gcs_sub is None:
        # wikipedia → use subfolder name
        if len(parts) >= 2:
            gcs_sub = parts[1].lower().replace(" ", "_")
        else:
            gcs_sub = top_folder.lower().replace(" ", "_")
    elif top_folder == "US Mint" and len(parts) >= 2:
        # Preserve US Mint subdirectory structure (HighRes_Scrape, etc.)
        sub = parts[1].lower().replace(" ", "_")
        gcs_sub = f"us_mint_manual/{sub}"

    return f"{GCS_PREFIX}/{gcs_sub}"


def main():
    parser = argparse.ArgumentParser(description="Sync local coin images to GCS")
    parser.add_argument("--report-only", action="store_true", help="Only compare, don't upload")
    parser.add_argument("--upload",      action="store_true", help="Upload new files to GCS")
    parser.add_argument("--delete",      action="store_true", help="Delete local files after verified upload")
    args = parser.parse_args()

    if args.delete and not args.upload:
        print("ERROR: --delete requires --upload")
        sys.exit(1)

    credentials, _ = google.auth.default()
    gcs = storage.Client(credentials=credentials, project=PROJECT)
    bucket = gcs.bucket(GCS_BUCKET)

    # ── 1. Build GCS filename set (just basenames for comparison) ─────────────
    print("Loading GCS image inventory...")
    gcs_filenames = set()
    gcs_paths     = {}  # basename → full GCS path (for display)
    for prefix in [
        "reference_library/",
    ]:
        blobs = bucket.list_blobs(prefix=prefix)
        for blob in blobs:
            fname = Path(blob.name).name
            if Path(blob.name).suffix.lower() in IMAGE_EXTENSIONS:
                gcs_filenames.add(fname.lower())
                gcs_paths[fname.lower()] = blob.name

    # Also check us_mint_coin_images bucket
    mint_bucket = gcs.bucket("us_mint_coin_images")
    for blob in mint_bucket.list_blobs():
        fname = Path(blob.name).name
        if Path(blob.name).suffix.lower() in IMAGE_EXTENSIONS:
            gcs_filenames.add(fname.lower())
            gcs_paths[fname.lower()] = f"us_mint_coin_images/{blob.name}"

    print(f"  GCS images found: {len(gcs_filenames):,}")

    # ── 2. Walk local folder ───────────────────────────────────────────────────
    local_root = Path(LOCAL_ROOT)
    local_images = [p for p in local_root.rglob("*") if p.is_file() and is_image(p)]
    print(f"  Local images found: {len(local_images):,}")

    already_in_gcs = []
    new_images     = []

    for local_path in sorted(local_images):
        fname_lower = local_path.name.lower()
        if fname_lower in gcs_filenames:
            already_in_gcs.append((local_path, gcs_paths[fname_lower]))
        else:
            new_images.append(local_path)

    # ── 3. Report ─────────────────────────────────────────────────────────────
    total_size_new = sum(p.stat().st_size for p in new_images)
    total_size_all = sum(p.stat().st_size for p in local_images)

    print(f"\n{'='*65}")
    print(f"  COMPARISON REPORT")
    print(f"{'='*65}")
    print(f"  Total local images:      {len(local_images):>5}")
    print(f"  Already in GCS:          {len(already_in_gcs):>5}  (safe to delete locally)")
    print(f"  NEW — not in GCS:        {len(new_images):>5}  ({total_size_new/1024/1024:.1f} MB to upload)")
    print(f"  Total local disk usage:  {total_size_all/1024/1024:.1f} MB")

    print(f"\n  Already in GCS (will be safe to delete):")
    for local_path, gcs_path in already_in_gcs[:20]:
        rel = local_path.relative_to(local_root)
        print(f"    ✓ {str(rel)[:60]}")
    if len(already_in_gcs) > 20:
        print(f"    ... and {len(already_in_gcs)-20} more")

    print(f"\n  NEW images (not yet in GCS):")
    for p in new_images[:40]:
        rel = p.relative_to(local_root)
        print(f"    + {str(rel)[:65]}")
    if len(new_images) > 40:
        print(f"    ... and {len(new_images)-40} more")

    if args.report_only:
        print("\n  (--report-only: no uploads performed)")
        return

    # ── 4. Upload new images ───────────────────────────────────────────────────
    if args.upload and new_images:
        print(f"\n  Uploading {len(new_images)} new images to GCS...")
        uploaded       = []
        failed         = []

        for i, local_path in enumerate(new_images, 1):
            dest_prefix = gcs_dest_prefix(local_path, local_root)
            blob_name   = f"{dest_prefix}/{local_path.name}"
            blob        = bucket.blob(blob_name)

            try:
                blob.upload_from_filename(str(local_path))
                public_url = f"https://storage.googleapis.com/{GCS_BUCKET}/{blob_name}"
                uploaded.append((local_path, blob_name))
                if i % 25 == 0 or i == len(new_images):
                    print(f"    [{i}/{len(new_images)}] Uploaded: {local_path.name[:60]}")
            except Exception as e:
                failed.append((local_path, str(e)))
                print(f"    [FAIL] {local_path.name}: {e}")

        print(f"\n  Upload complete: {len(uploaded)} succeeded, {len(failed)} failed")

        # ── 5. Delete local copies if all uploaded ─────────────────────────────
        if args.delete and not failed:
            print(f"\n  Deleting {len(uploaded)} local files (upload verified)...")
            deleted = 0
            for local_path, _ in uploaded:
                try:
                    local_path.unlink()
                    deleted += 1
                except Exception as e:
                    print(f"  [WARN] Could not delete {local_path.name}: {e}")

            # Also delete already_in_gcs local copies
            print(f"  Deleting {len(already_in_gcs)} local files already confirmed in GCS...")
            for local_path, _ in already_in_gcs:
                try:
                    local_path.unlink()
                    deleted += 1
                except Exception as e:
                    print(f"  [WARN] Could not delete {local_path.name}: {e}")

            # Clean up empty directories
            for dirpath in sorted(local_root.rglob("*"), reverse=True):
                if dirpath.is_dir():
                    try:
                        dirpath.rmdir()  # only removes if empty
                    except OSError:
                        pass

            print(f"\n  Deleted {deleted} local files.")
            print(f"  Local folder is now {'empty' if not any(local_root.rglob('*')) else 'has remaining files'}.")

        elif args.delete and failed:
            print(f"\n  WARNING: {len(failed)} uploads failed — local files NOT deleted.")
            print("  Fix the upload errors and re-run before deleting.")

    # ── 6. Re-run image index to pick up newly uploaded images ─────────────────
    if args.upload and uploaded:
        print("\n  Triggering image index update for newly uploaded files...")
        import subprocess
        result = subprocess.run(
            ["python", "build_image_index.py"],
            capture_output=True, text=True, cwd=str(Path(__file__).parent)
        )
        if result.returncode == 0:
            print("  Image index updated successfully.")
        else:
            print(f"  Index update had errors (check manually): {result.stderr[:200]}")


if __name__ == "__main__":
    main()
