"""
scrape_mint_images.py
=====================
Downloads high-resolution coin images from usmint.gov.

SETUP (required before each session):
  1. Log into your US Mint account at https://www.usmint.gov
  2. Open DevTools (F12) -> Network tab
  3. Click any page, find the request to usmint.gov
  4. Right-click the request -> "Copy" -> "Copy as cURL"
  5. Extract the Cookie: header value and paste it below as COOKIES

COIN PROGRAMS TO SCRAPE (in priority order per missing_images_report):
  1. Lincoln Cents    - /coins/coin-programs/lincoln-cent/
  2. State Quarters   - /coins/coin-programs/50-state-quarters-program/
  3. Eisenhower Dollar- /coins/coin-programs/eisenhower-dollar/
  4. Morgan Dollar    - /coins/coin-programs/morgan-silver-dollar/
  5. American Silver Eagle - /coins/coin-programs/american-silver-eagle/
  6. Kennedy Half     - /coins/coin-programs/kennedy-half-dollar/
  7. Jefferson Nickel - /coins/coin-programs/jefferson-nickel/
  8. Roosevelt Dime   - /coins/coin-programs/roosevelt-dime/
  9. Peace Dollar     - /coins/coin-programs/peace-dollar/
  10. Buffalo Nickel  - /coins/coin-programs/buffalo-nickel/
  11. Mercury Dime    - /coins/coin-programs/mercury-dime-winged-liberty-head-dime/
  12. Barber Coinage  - /coins/coin-programs/barber-coinage/
  13. Presidential Dollars - /coins/coin-programs/presidential-dollar/
  14. Native American - /coins/coin-programs/native-american-dollar/
  15. ATB Quarters    - /coins/coin-programs/america-the-beautiful-quarters/

Run:
    python scrape_mint_images.py                          # all programs
    python scrape_mint_images.py --program lincoln-cent   # one program
    python scrape_mint_images.py --dry-run                # list URLs only
    python scrape_mint_images.py --upload-gcs             # upload to GCS

Output: C:\\Users\\ericd\\Documents\\MyVertexProject\\Manual downloaded Coin Images\\US Mint\\HighRes_Scrape\\
"""

import argparse
import json
import os
import re
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# ─── SESSION COOKIES (refreshed 2026-06-10) ──────────────────────────────────
COOKIES = ("dwanonymous_b2cf918be9f3733e2d19f7e7beb4b6d7=acvbZsuqmyvGOefBI1gzTaZ7oC; "
           "_gcl_au=1.1.1057773659.1781036199; _gcl_gs=2.1.k1$i1781036196$u212896144; "
           "_ga=GA1.1.1923473270.1781036199; __cq_uuid=acvbZsuqmyvGOefBI1gzTaZ7oC; "
           "_fbp=fb.1.1781036199980.972018829743289701; "
           "_pin_unauth=dWlkPU9EVmxZekEwTnpBdFpqa3paUzAwTVRjekxUZ3dOV0l0TWpBOU0ySm1OV00yWlRGaA; "
           "_ce.clock_data=-1739%2C24.246.138.41%2C1%2C16fee37559dbd42b448204446d02089f%2CChrome%2CUS; "
           "a1ashgd=wb4b97ond3000000wb4b97ond3000000; "
           "_gcl_aw=GCL.1781036204.CjwKCAjw857RBhAgEiwAI-1yKDXEbshjLtWmyNyX4iriIX_0pJil9e-bauCy9IiHAKwttGSHmaKbvBoCeBoQAvD_BwE; "
           "_gcl_dc=GCL.1781036204.CjwKCAjw857RBhAgEiwAI-1yKDXEbshjLtWmyNyX4iriIX_0pJil9e-bauCy9IiHAKwttGSHmaKbvBoCeBoQAvD_BwE; "
           "cqcid=acvbZsuqmyvGOefBI1gzTaZ7oC; __cq_dnt=0; dw_dnt=0; "
           "cf_clearance=ebBcScFZR9QVZZF5j1C2TckIS801YQ0Uw29QtcnXOSw-1781120329-1.2.1.1-R6vYVGJoD4sXoMBg4exiTPFL93DBLwKZwMb8ElkvE7NZuC5Oj0v4AOxVEdgrBpjKJ6dtQWTXNgLwrIfvsO23CHdfo4ycurvfQUvmbd7.poM7ldsmIvVU8KGokoXjDlaCgEPaxBVkTmQTK_SkvCgDg7DjIEGK23Lj_w8L_FjOjiudPuTU14Uma.LwrKSNyF3qTYyFhM19zXFqWivhR7UrX9tjPOS6RjN0fzJpDc.Kg_notXz4pOvUxha6mhGKwy25h0M9k1Vt3dRkuLqAyxVeLVUbOqbEpwCJUh8xPDn63FcgJTH9BE.F.rzOnvaH50IPPgearHi_0RS7Q18zKvt0ZQ; "
           "__cf_bm=n7cJQ.hmVGM73fUZGyaqrxlRhEOXzt0bSuDqXv8.p9o-1781120329.066505-1.0.1.1-5t_gjhcSGoSibr4JMj6sYsUOk8r7olXMmPIHLpI1wAOgYqCry7Q6QZptYpVknThOZLou0Pr_Yo3oxqaRBJrzx8zpMuhseW2Cs8gn5Z__cRUc.bdn1x8YjTeh6mylsawRtjtFxPvdSSTgxcwUwtVUSg; "
           "AMCVS_7A9335DD5CF935CA0A495FCD%40AdobeOrg=1; "
           "AMCV_7A9335DD5CF935CA0A495FCD%40AdobeOrg=179643557%7CMCIDTS%7C20614%7CMCMID%7C27507583095786729830571892975826703553%7CMCAAMLH-1781725130%7C7%7CMCAAMB-1781725130%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1781127530s%7CNONE%7CMCSYNCSOP%7C411-20621%7CvVersion%7C5.5.0; "
           "s_cc=true; cebs=1; "
           "dwsid=z2oWaK1J20eFDD3hp0kxLMV88iWVPn0M3bkl_XNCbAaF2Q3ulIi_n-TOxe7A1BcTkPzc7j6Jb-qtir-br1VPpA==; "
           "dwac_bcKmAiaageu6saaadbf1J7A92a=iPWiTuIzHDq6j9tXQ6rH-FLrTYF977ODQsE%3D|dw-only|USM13657498||USD|false|US%2FEastern|true; "
           "cquid=mK/4fKoufV2kYk1maHags5S0Ep914WfGI+GwqXDCdL0=|b83980aaac7d5af452acc14bc7123cafaeef222883452604c32fa5ec561f6061|b83980aaac7d5af452acc14bc7123cafaeef222883452604c32fa5ec561f6061; "
           "sid=vrnFb1d2N_YrqhgNhGpFoLSvISJvAZG9cx8; "
           "__cq_bc=%7B%22aarb-USM%22%3A%5B%7B%22id%22%3A%2226RJ%22%7D%5D%7D; "
           "AWSALB=yA4jrsFgyR8WIqwUnBf+4op10KcJqn68XtbW5ZlpvyNdYasPkYt+Fsrkd+JEP438i5dohLe8CI6FxqTyU+lqUmMYwfC9l6uTxhFKX/CuW/1uJOie9cW2eK/z2SD1; "
           "AWSALBCORS=yA4jrsFgyR8WIqwUnBf+4op10KcJqn68XtbW5ZlpvyNdYasPkYt+Fsrkd+JEP438i5dohLe8CI6FxqTyU+lqUmMYwfC9l6uTxhFKX/CuW/1uJOie9cW2eK/z2SD1; "
           "_rdt_uuid=1781036199826.4c22a90e-157e-48bb-bd79-39a100c086a2; "
           "_uetsid=1fccf660644011f1bc75f9c30c9dde39; _uetvid=1fcd1070644011f1818f8ba7b81e29dd; cebsp_=8")

# ─── CONFIG ────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\US Mint\HighRes_Scrape")
MINT_BASE   = "https://www.usmint.gov"
GCS_BUCKET  = "numista-reference-library"
GCS_PREFIX  = "reference_library/wikimedia_uscoin"

# ── Image Library sections (PRIMARY source - press quality, organized by type) ──
# URL pattern: https://www.usmint.gov/news/image-library/{section}
IMAGE_LIBRARY_SECTIONS = [
    "circulating",
    "commemorative",
    "bullion",
    "numismatic",
    "program",
    "historical",
    "annual-sets",
    "proof-sets",
    "silver-proof-sets",
    "quarter-proof-sets",
    "uncirculated-sets",
    "prestige-sets",
]

# ── Coin program pages (SECONDARY source - program-specific pages) ───────────
PROGRAMS = {
    "lincoln-cent":                          "Lincoln_cents",
    "50-state-quarters-program":             "United_States_quarters",
    "america-the-beautiful-quarters":        "ATB_quarters",
    "american-women-quarters":               "American_Women_quarters",
    "eisenhower-dollar":                     "Eisenhower_dollars",
    "morgan-silver-dollar":                  "Morgan_dollars",
    "american-silver-eagle":                 "American_eagle",
    "american-gold-eagle":                   "Gold_Eagles",
    "kennedy-half-dollar":                   "Kennedy_half_dollar",
    "jefferson-nickel":                      "Nickel",
    "roosevelt-dime":                        "Dime",
    "peace-dollar":                          "Peace_dollars",
    "buffalo-nickel":                        "Buffalo_nickels",
    "mercury-dime-winged-liberty-head-dime": "Mercury_dimes",
    "barber-coinage":                        "Barber_coinage",
    "presidential-dollar":                   "Presidential",
    "native-american-dollar":                "Native_American",
    "sacagawea-dollar":                      "Sacagawea",
    "semiquincentennial":                    "Bicentennial",
    "walking-liberty-half-dollar":           "Half_Dollar",
}

# Known US Mint image dam path patterns
MINT_IMAGE_PATTERNS = [
    r'(https?://www\.usmint\.gov/content/dam/usmint/image-library/[^\"\'\s]+\.(?:jpg|jpeg|png))',
    r'src="(//www\.usmint\.gov/content/dam[^\"\'\s]+\.(?:jpg|jpeg|png))"',
    r'"(//images\.usmint\.gov/[^\"\'\s]+\.(?:jpg|jpeg|png))"',
]


def get_headers() -> dict:
    h = {
        'User-Agent':      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept':          'text/html,application/xhtml+xml,*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer':         'https://www.usmint.gov/',
    }
    if COOKIES:
        h['Cookie'] = COOKIES
    return h


def fetch_html(url: str) -> str | None:
    try:
        req = urllib.request.Request(url, headers=get_headers())
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"  [error] {url}: {e}")
        return None


def extract_image_urls(html: str) -> list[str]:
    """Pull all high-res coin image URLs from a US Mint page."""
    found = set()
    for pattern in MINT_IMAGE_PATTERNS:
        for m in re.finditer(pattern, html, re.I):
            url = m.group(1)
            if url.startswith('//'):
                url = 'https:' + url
            # Skip thumbnails
            if not any(t in url for t in ['150x', '300x', '500x', 'thumbnail', 'icon']):
                found.add(url)
    return sorted(found)


def get_program_pages(slug: str) -> list[str]:
    """Get all page URLs for a coin program (handles pagination)."""
    base_url = f"{MINT_BASE}/coins/coin-programs/{slug}/"
    pages    = [base_url]

    html = fetch_html(base_url)
    if not html:
        return pages

    # Check for sub-pages or year-specific pages linked from the program page
    year_links = re.findall(
        rf'href="(/coins/coin-programs/{slug}/[^"#]+)"',
        html, re.I
    )
    for link in year_links:
        full = f"{MINT_BASE}{link}"
        if full not in pages:
            pages.append(full)

    # Also check for media-kit pages
    media_links = re.findall(r'href="(/news/media-kit[^"#]+)"', html, re.I)
    for link in media_links:
        full = f"{MINT_BASE}{link}"
        if full not in pages:
            pages.append(full)

    return list(dict.fromkeys(pages))


def download_image(url: str, dest: Path) -> bool:
    """Download one image. Returns True on success."""
    if dest.exists() and dest.stat().st_size > 1000:
        return True  # already have it
    try:
        req = urllib.request.Request(url, headers={**get_headers(), 'Accept': 'image/*'})
        with urllib.request.urlopen(req, timeout=30) as r:
            dest.write_bytes(r.read())
        return True
    except Exception as e:
        print(f"    [dl error] {e}")
        return False


def apply_watermark(image_path: Path) -> None:
    """Add subtle 'U.S. Mint' watermark to downloaded images."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        img  = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", max(14, int(img.size[1] * 0.015)))
        except Exception:
            font = ImageFont.load_default()

        text    = "U.S. Mint"
        bbox    = draw.textbbox((0, 0), text, font=font)
        padding = int(img.size[0] * 0.02)
        x = img.size[0] - (bbox[2] - bbox[0]) - padding
        y = img.size[1] - (bbox[3] - bbox[1]) - padding

        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 100))
        draw.text((x, y),         text, font=font, fill=(255, 255, 255, 180))
        img.save(image_path, quality=95)
    except Exception:
        pass  # watermark is best-effort


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Download US Mint coin images")
    parser.add_argument("--program",    default="all", help="Program slug or 'all'")
    parser.add_argument("--dry-run",    action="store_true")
    parser.add_argument("--upload-gcs", action="store_true")
    args = parser.parse_args()

    if not COOKIES:
        print("\n" + "!"*60)
        print("  NO COOKIES SET!")
        print("  To get fresh cookies:")
        print("  1. Go to usmint.gov and log into your account")
        print("  2. F12 -> Network tab -> click any page")
        print("  3. Right-click the usmint.gov request -> Copy as cURL")
        print("  4. Paste the Cookie: value into COOKIES at top of this file")
        print("  Will try without auth (may get 403s on some pages)...")
        print("!"*60 + "\n")

    BASE_DIR.mkdir(parents=True, exist_ok=True)

    # Determine which programs to scrape
    if args.program == "all":
        target_programs = PROGRAMS
    elif args.program in PROGRAMS:
        target_programs = {args.program: PROGRAMS[args.program]}
    else:
        # Try as a partial match
        target_programs = {k: v for k, v in PROGRAMS.items() if args.program in k}
        if not target_programs:
            print(f"Unknown program '{args.program}'. Available:")
            for k in PROGRAMS:
                print(f"  {k}")
            return

    print(f"\n{'='*60}")
    print(f"  US Mint Image Scraper")
    print(f"  Programs: {len(target_programs)}")
    print(f"  Auth: {'YES (cookies set)' if COOKIES else 'NO (limited access)'}")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'LIVE DOWNLOAD'}")
    print(f"{'='*60}\n")

    total_downloaded = 0
    total_errors     = 0
    manifest_entries = []

    for slug, folder_name in target_programs.items():
        print(f"\n[{slug}]")
        out_dir = BASE_DIR / folder_name
        if not args.dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)

        # Get all pages for this program
        pages = get_program_pages(slug)
        print(f"  Pages to scan: {len(pages)}")

        all_image_urls = []
        for page_url in pages:
            html = fetch_html(page_url)
            if not html:
                continue
            imgs = extract_image_urls(html)
            print(f"  {page_url.split('/')[-1] or 'index'}: {len(imgs)} images")
            all_image_urls.extend(imgs)
            time.sleep(0.5)

        # Deduplicate
        all_image_urls = list(dict.fromkeys(all_image_urls))
        print(f"  Total unique images: {len(all_image_urls)}")

        if args.dry_run:
            for url in all_image_urls[:5]:
                print(f"    {url}")
            continue

        # Download each image
        prog_downloaded = 0
        prog_errors     = 0
        for img_url in all_image_urls:
            filename = img_url.split('/')[-1].split('?')[0]
            dest     = out_dir / filename

            if download_image(img_url, dest):
                apply_watermark(dest)
                print(f"  OK  {filename}")
                prog_downloaded += 1
            else:
                prog_errors += 1
            time.sleep(0.3)

        print(f"  [{slug}] Done: {prog_downloaded} downloaded, {prog_errors} errors")
        total_downloaded += prog_downloaded
        total_errors     += prog_errors

        manifest_entries.append({
            "program": slug,
            "folder":  folder_name,
            "images":  prog_downloaded,
        })
        time.sleep(1)

    # ── GCS Upload ─────────────────────────────────────────────────────────────
    if args.upload_gcs and not args.dry_run and total_downloaded > 0:
        print(f"\nUploading {total_downloaded} images to GCS...")
        try:
            import google.auth
            from google.cloud import storage as gcs
            creds, _ = google.auth.default()
            client   = gcs.Client(credentials=creds, project="studio-9101802118-8c9a8")
            bucket   = client.bucket(GCS_BUCKET)
            uploaded = 0
            for f in BASE_DIR.rglob("*.jpg"):
                blob_path = f"{GCS_PREFIX}/{f.parent.name}/{f.name}"
                blob = bucket.blob(blob_path)
                if not blob.exists():
                    blob.upload_from_filename(str(f), content_type="image/jpeg")
                    uploaded += 1
            for f in BASE_DIR.rglob("*.png"):
                blob_path = f"{GCS_PREFIX}/{f.parent.name}/{f.name}"
                blob = bucket.blob(blob_path)
                if not blob.exists():
                    blob.upload_from_filename(str(f), content_type="image/png")
                    uploaded += 1
            print(f"  Uploaded {uploaded} images to gs://{GCS_BUCKET}/{GCS_PREFIX}/")
        except Exception as e:
            print(f"  GCS error: {e}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  US Mint Scrape Complete!")
    print(f"  Total downloaded: {total_downloaded}")
    print(f"  Total errors:     {total_errors}")
    print(f"  Output: {BASE_DIR}")
    print(f"{'='*60}\n")

    if not args.dry_run and manifest_entries:
        (BASE_DIR / "MANIFEST.json").write_text(json.dumps({
            "source":     "usmint.gov",
            "scraped_at": datetime.now().isoformat(),
            "programs":   manifest_entries,
            "total":      total_downloaded,
        }, indent=2))


if __name__ == "__main__":
    main()
