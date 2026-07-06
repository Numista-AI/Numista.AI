# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
scrape_memoir_coin.py
=====================
Scrapes all coin product images from memoir-coin.com.

The site uses Shoplazza (Chinese e-commerce platform).
Images hosted on staticdj.com CDN - no authentication required.

Strategy:
  1. Fetch sitemap.xml to find all product URLs
  2. For each product page, extract all staticdj.com images (full resolution)
  3. Download and organize by product name

Run:
    python scrape_memoir_coin.py                 # download everything
    python scrape_memoir_coin.py --dry-run       # count only
    python scrape_memoir_coin.py --upload-gcs    # also push to GCS

Output: C:\\Users\\ericd\\Documents\\MyVertexProject\\Manual downloaded Coin Images\\memoir_coin\\
"""

import argparse
import json
import os
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

# ─── CONFIG ────────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path(r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\memoir_coin")
BASE_URL   = "https://www.memoir-coin.com"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.memoir-coin.com/',
}

GCS_BUCKET = "numista-uploads-studio-9101802118-8c9a8"
GCS_PREFIX = "reference_images/memoir_coin"


# ─── HELPERS ───────────────────────────────────────────────────────────────────

def fetch(url: str) -> str | None:
    """Fetch URL, return text content or None."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            charset = r.headers.get_content_charset() or 'utf-8'
            return r.read().decode(charset, errors='replace')
    except Exception as e:
        print(f"  [error] {url} -> {e}")
        return None


def download_bytes(url: str) -> bytes | None:
    """Download binary content."""
    try:
        req = urllib.request.Request(url, headers={**HEADERS, 'Accept': 'image/*'})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except Exception as e:
        print(f"  [dl error] {e}")
        return None


def get_full_res(url: str) -> str:
    """Strip size suffix to get original-resolution staticdj URL."""
    # e.g.  abc123_900x.jpg  ->  abc123.jpg
    #       abc123_900x600.jpg -> abc123.jpg
    return re.sub(r'(_\d+x\d*)', '', url)


def extract_images_from_html(html: str) -> list[str]:
    """Extract all unique full-res staticdj.com image URLs from HTML."""
    raw = re.findall(
        r'(?:https?:)?//img\.staticdj\.com/([a-f0-9]{32}(?:_\d+x\d*)?\.(?:jpg|jpeg|png|webp))',
        html, re.I
    )
    # Get full-res versions of all found URLs, deduplicated
    seen = set()
    result = []
    for r in raw:
        # Strip size suffix to get original
        base = re.sub(r'_\d+x\d*\.', '.', r)
        full_url = f"https://img.staticdj.com/{base}"
        if full_url not in seen:
            seen.add(full_url)
            result.append(full_url)
    return result


def get_product_urls_from_sitemap() -> list[str]:
    """Try to get all product URLs from sitemap.xml."""
    urls = []
    for sitemap_url in [
        f"{BASE_URL}/sitemap.xml",
        f"{BASE_URL}/sitemap_products_1.xml",
    ]:
        content = fetch(sitemap_url)
        if not content:
            continue
        found = re.findall(r'<loc>(https?://www\.memoir-coin\.com/products/[^<]+)</loc>', content)
        if found:
            print(f"  Sitemap {sitemap_url.split('/')[-1]}: {len(found)} product URLs")
            urls.extend(found)

    # Also check sitemap index
    sitemap_index = fetch(f"{BASE_URL}/sitemap.xml")
    if sitemap_index:
        sub_sitemaps = re.findall(r'<loc>(https?://[^<]+sitemap[^<]*\.xml[^<]*)</loc>', sitemap_index)
        for sub in sub_sitemaps:
            if 'product' in sub.lower():
                content = fetch(sub)
                if content:
                    found = re.findall(r'<loc>(https?://www\.memoir-coin\.com/products/[^<]+)</loc>', content)
                    if found:
                        print(f"  Sub-sitemap: {len(found)} product URLs")
                        urls.extend(found)
                time.sleep(0.3)

    return list(dict.fromkeys(urls))  # deduplicate


def scrape_collection_page(collection_slug: str) -> list[str]:
    """Scrape a collection page for product links."""
    product_urls = []
    page = 1
    while True:
        url  = f"{BASE_URL}/collections/{collection_slug}?page={page}"
        html = fetch(url)
        if not html:
            break

        # Find product links
        found = re.findall(r'href="(/products/[^"?#]+)"', html)
        found = [f"{BASE_URL}{h}" for h in found]
        found = list(dict.fromkeys(found))

        if not found or page > 20:
            break

        product_urls.extend(found)

        # Check for "next page"
        if f'page={page + 1}' not in html and 'next' not in html.lower():
            break
        page += 1
        time.sleep(0.4)

    return list(dict.fromkeys(product_urls))


def safe_filename(s: str, max_len: int = 60) -> str:
    """Convert a string to a safe directory/filename."""
    s = re.sub(r'[^\w\s\-]', '', s.lower())
    s = re.sub(r'[\s_]+', '_', s.strip())
    return s[:max_len] or "unknown"


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scrape memoir-coin.com images")
    parser.add_argument("--dry-run",    action="store_true")
    parser.add_argument("--upload-gcs", action="store_true")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  memoir-coin.com Scraper")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"{'='*60}\n")

    # ── Step 1: Discover product URLs ──────────────────────────────────────────
    print("Step 1: Discovering products...")
    product_urls = get_product_urls_from_sitemap()
    print(f"  Sitemap: {len(product_urls)} product URLs")

    # Also try known collection slugs
    for slug in ["best-seller", "all", "coins", "challenge-coins",
                 "morgan-dollar", "commemorative-coins"]:
        col_urls = scrape_collection_page(slug)
        if col_urls:
            print(f"  Collection '{slug}': {len(col_urls)} products")
            product_urls.extend(col_urls)
        time.sleep(0.3)

    # Deduplicate
    product_urls = list(dict.fromkeys(product_urls))
    print(f"  Total unique product URLs: {len(product_urls)}")

    # ── Step 2: Also grab homepage images directly ─────────────────────────────
    print("\nStep 2: Scraping homepage images...")
    home_html = fetch(BASE_URL)
    home_images = extract_images_from_html(home_html) if home_html else []
    print(f"  Homepage: {len(home_images)} unique images")

    # ── Step 3: Scrape each product page ──────────────────────────────────────
    all_products = []
    total_images = 0

    # Add homepage as a pseudo-product
    if home_images:
        all_products.append({
            "title":  "homepage_featured",
            "url":    BASE_URL,
            "images": home_images,
        })
        total_images += len(home_images)

    if product_urls:
        print(f"\nStep 3: Scraping {len(product_urls)} product pages...")
        for i, url in enumerate(product_urls, 1):
            print(f"  [{i:3d}/{len(product_urls)}] {url.split('/')[-1][:50]}", end=" ")
            html = fetch(url)
            if not html:
                print("SKIP")
                continue

            images = extract_images_from_html(html)

            # Try to get product title
            title_match = re.search(r'<title>([^<|]+)', html)
            title = title_match.group(1).strip() if title_match else url.split('/')[-1]
            title = re.sub(r'\s*[-|]\s*memoir-coin.*$', '', title, flags=re.I).strip()

            print(f"-> {len(images)} images  [{title[:40]}]")

            if images:
                all_products.append({
                    "title":  title,
                    "url":    url,
                    "images": images,
                })
                total_images += len(images)

            time.sleep(0.5)

    print(f"\nTotal: {len(all_products)} products, {total_images} images\n")

    if args.dry_run:
        print("DRY RUN -- no files downloaded")
        print("Sample images:")
        for p in all_products[:3]:
            print(f"  {p['title']}")
            for img in p['images'][:2]:
                print(f"    {img}")
        return

    # ── Step 4: Download images ────────────────────────────────────────────────
    print("Step 4: Downloading images...")
    downloaded = 0
    errors     = 0

    for product in all_products:
        title    = product["title"]
        images   = product["images"]
        prod_dir = OUTPUT_DIR / safe_filename(title)
        prod_dir.mkdir(parents=True, exist_ok=True)

        for img_url in images:
            # Parse filename from URL
            img_name = img_url.split('/')[-1]
            ext      = img_name.rsplit('.', 1)[-1].lower() if '.' in img_name else 'jpg'
            dest     = prod_dir / img_name

            if dest.exists():
                downloaded += 1
                continue

            data = download_bytes(img_url)
            if data:
                dest.write_bytes(data)
                print(f"  OK  {prod_dir.name}/{img_name}")
                downloaded += 1
            else:
                errors += 1
            time.sleep(0.2)

    # ── Step 5: GCS upload (optional) ─────────────────────────────────────────
    if args.upload_gcs and downloaded > 0:
        print(f"\nStep 5: Uploading to GCS...")
        try:
            import google.auth
            from google.cloud import storage as gcs
            creds, _ = google.auth.default()
            client   = gcs.Client(credentials=creds, project="studio-9101802118-8c9a8")
            bucket   = client.bucket(GCS_BUCKET)
            uploaded = 0
            for f in OUTPUT_DIR.rglob("*"):
                if f.is_file() and f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp'):
                    blob_path = f"{GCS_PREFIX}/{f.parent.name}/{f.name}"
                    blob = bucket.blob(blob_path)
                    if not blob.exists():
                        mime = "image/jpeg" if f.suffix.lower() in ('.jpg', '.jpeg') else "image/png"
                        blob.upload_from_filename(str(f), content_type=mime)
                        uploaded += 1
            print(f"  Uploaded {uploaded} new images to gs://{GCS_BUCKET}/{GCS_PREFIX}/")
        except Exception as e:
            print(f"  GCS error: {e}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  Scrape complete!")
    print(f"  Products: {len(all_products)}")
    print(f"  Downloaded: {downloaded}  Errors: {errors}")
    print(f"  Saved to: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    # Write manifest
    manifest = OUTPUT_DIR / "MANIFEST.json"
    manifest.write_text(json.dumps({
        "source":     "memoir-coin.com",
        "scraped_at": datetime.now().isoformat(),
        "products":   len(all_products),
        "images":     downloaded,
        "note":       "Counterfeit coin vendor — images collected for reference/fraud awareness only"
    }, indent=2))


if __name__ == "__main__":
    main()
