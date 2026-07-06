# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
generate_gap_images.py
======================
AI-generates images for coins that have no match in the GCS reference library.
Uses Imagen 3 via Vertex AI.

The 42 remaining gaps are:
  - 26 "blank" series (1860s-1900s) -> Liberty Seated / Barber era by year
  - 16 Time Capsule Year Sets (1934-1964) -> generic mint set image
"""

import time
import re
from datetime import datetime, timezone

import google.auth
from google.cloud import firestore, storage as gcs
from google import genai
from google.genai import types as genai_types

# ── CONFIG ─────────────────────────────────────────────────────────────────────
PROJECT    = 'studio-9101802118-8c9a8'
LOCATION   = 'us-central1'
BUCKET     = 'numista-uploads-studio-9101802118-8c9a8'
USER_EMAIL = 'jseaman1204@gmail.com'
MODEL_ID   = 'imagen-3.0-generate-002'

# Year -> likely series for blank-series coins (1860s-1900s are Barber/Liberty Seated era)
def guess_series(year_str: str, denom: str) -> str:
    try:
        year = int(year_str)
    except (ValueError, TypeError):
        return 'historic US silver coin'

    denom_l = (denom or '').lower()

    if year < 1793:
        return 'early American colonial coin'
    elif year <= 1857:
        return 'early American large cent'
    elif year <= 1864:
        return 'Flying Eagle or Indian Head cent'
    elif year <= 1909:
        if 'dollar' in denom_l:
            return 'Liberty Seated silver dollar'
        elif 'half' in denom_l:
            return 'Liberty Seated half dollar'
        elif 'quarter' in denom_l:
            return 'Barber quarter'
        elif 'dime' in denom_l:
            return 'Barber dime'
        elif 'nickel' in denom_l:
            return 'Liberty Head nickel'
        elif 'cent' in denom_l or 'penny' in denom_l:
            return 'Indian Head cent'
        else:
            return 'Barber silver coin'
    elif year <= 1921:
        return 'Morgan silver dollar'
    elif year <= 1935:
        return 'Peace silver dollar'
    else:
        return 'historic US coin'

def build_prompt(year: str, series: str, denom: str, theme: str) -> str:
    if series == 'Time Capsule Year Set' or 'capsule' in (series or '').lower():
        return (
            f"A professional numismatic photograph of a United States {year} annual "
            f"mint coin set, showing multiple historic US coins arranged on a dark "
            f"velvet background. The coins include a penny, nickel, dime, quarter, "
            f"and half dollar from {year}. Studio lighting, white background, "
            f"ultra high resolution coin photography."
        )

    guessed = guess_series(year, denom) if not series or series == '(blank)' else series
    denom_desc = denom if denom else 'coin'

    return (
        f"A professional numismatic photograph of a United States {year} {guessed} "
        f"{denom_desc}, obverse side showing Liberty design. "
        f"The coin is centered on a pure white background, with dramatic studio "
        f"lighting highlighting the coin's relief details and luster. "
        f"Ultra high resolution, 4K, coin photography, no shadows, "
        f"photorealistic, museum quality."
    )


def main():
    creds, _ = google.auth.default()
    fs_client  = firestore.Client(credentials=creds, project=PROJECT)
    gcs_client = gcs.Client(credentials=creds, project=PROJECT)
    bucket     = gcs_client.bucket(BUCKET)

    client = genai.Client(vertexai=True, project=PROJECT, location=LOCATION)

    coins_ref = (fs_client.collection('users')
                 .document(USER_EMAIL)
                 .collection('coins'))
    all_coins = list(coins_ref.stream())
    gaps = [c for c in all_coins
            if not (c.to_dict().get('image_url_obverse') or '').strip()]

    print(f'Generating AI images for {len(gaps)} coins...\n')
    now = datetime.now(timezone.utc).isoformat()

    success = 0
    errors  = 0

    for i, coin in enumerate(gaps):
        d      = coin.to_dict()
        year   = str(d.get('Year', '') or '')
        series = str(d.get('Program/Series', '') or '')
        denom  = str(d.get('Denomination', '') or '')
        theme  = str(d.get('Theme/Subject', '') or '')
        ref_no = str(d.get('Personal Ref #', '') or coin.id[:8])

        prompt = build_prompt(year, series, denom, theme)
        label  = f"{year} {series or guess_series(year, denom)}"[:60]

        print(f"  [{i+1:2d}/{len(gaps)}] {label}")
        print(f"         Prompt: {prompt[:80]}...")

        # Retry loop with exponential backoff for quota errors
        max_retries = 4
        for attempt in range(max_retries):
            try:
                response = client.models.generate_images(
                    model=MODEL_ID,
                    prompt=prompt,
                    config=genai_types.GenerateImagesConfig(
                        number_of_images=1,
                        aspect_ratio="1:1",
                        safety_filter_level="block_few",
                        person_generation="dont_allow",
                    )
                )

                if not response.generated_images:
                    print(f"         SKIP — no image returned")
                    errors += 1
                    break

                img_bytes = response.generated_images[0].image.image_bytes

                # Save to GCS
                safe_label = re.sub(r'[^\w\-]', '_', label.lower())[:50]
                blob_name  = f'ai_generated/{safe_label}_{ref_no}.png'
                blob       = bucket.blob(blob_name)
                blob.upload_from_string(img_bytes, content_type='image/png')

                img_url = f'https://storage.googleapis.com/{BUCKET}/{blob_name}'

                # Write to Firestore
                coins_ref.document(coin.id).update({
                    'image_url_obverse': img_url,
                    'image_source':      'ai_generated_imagen3',
                    'image_updated_at':  now,
                })

                print(f"         OK -> {blob_name}")
                success += 1
                time.sleep(8)  # stay under quota: ~7 req/min
                break

            except Exception as e:
                err_str = str(e)
                if '429' in err_str or 'Quota' in err_str:
                    wait = 60 * (attempt + 1)  # 60s, 120s, 180s, 240s
                    print(f"         QUOTA HIT (attempt {attempt+1}) — waiting {wait}s...")
                    time.sleep(wait)
                    if attempt == max_retries - 1:
                        print(f"         FAILED after {max_retries} attempts")
                        errors += 1
                else:
                    print(f"         ERROR: {e}")
                    errors += 1
                    time.sleep(5)
                    break

    print(f"\n{'='*60}")
    print(f"  AI Generation Complete!")
    print(f"  Generated: {success}")
    print(f"  Errors:    {errors}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
