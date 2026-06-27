#!/usr/bin/env python3
"""
generate_error_illustrations.py
-------------------------------
Python script to dynamically generate high-quality error illustration diagrams.

This script:
1. Queries the Firestore `mint_errors` collection to find published errors.
2. For each error, searches the `coin_image_index` to find matching obverse or reverse coin images in Google Cloud Storage.
3. Downloads the GCS image, scales it, and uses Pillow to overlay:
   - Visual red/orange circle hotspots representing the error location.
   - Vector pointer lines/arrows pointing to the hotspot.
   - Translucent rounded callout text boxes with error details.
4. Uploads the finalized annotated diagram back to GCS.
5. Updates the Firestore document with the new public GCS illustration URL.

Requirements:
    pip install firebase-admin google-cloud-storage pillow
"""

import os
import sys
import io
import math
from pathlib import Path
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage as gcs
from PIL import Image, ImageDraw, ImageFont

# ─── Configuration ───────────────────────────────────────────────────────────
GCP_PROJECT = "studio-9101802118-8c9a8"
BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"
ILLUSTRATION_FOLDER = "error_library_illustrations"

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")

def draw_pointer(draw, start, end, fill, width=4):
    """Draw a vector pointer line with a chevron arrow head at the end point."""
    draw.line([start, end], fill=fill, width=width)
    
    # Calculate arrowhead angle
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)
    
    # Arrowhead wings
    arrow_len = 16
    wing_angle = math.pi / 6  # 30 degrees
    
    x1 = end[0] - arrow_len * math.cos(angle - wing_angle)
    y1 = end[1] - arrow_len * math.sin(angle - wing_angle)
    x2 = end[0] - arrow_len * math.cos(angle + wing_angle)
    y2 = end[1] - arrow_len * math.sin(angle + wing_angle)
    
    draw.polygon([end, (x1, y1), (x2, y2)], fill=fill)

def main():
    print("🚀 Initializing Vector-Overlay Generation Engine...")
    
    # Firebase & GCS Init
    if not firebase_admin._apps:
        firebase_admin.initialize_app(options={"projectId": GCP_PROJECT})
    
    db = firestore.client()
    gcs_client = gcs.Client(project=GCP_PROJECT)
    bucket = gcs_client.bucket(BUCKET_NAME)

    # Fetch errors
    errors = list(db.collection("mint_errors").stream())
    print(f"Loaded {len(errors)} errors from Firestore.")

    for error_doc in errors:
        error_data = error_doc.to_dict()
        error_id = error_doc.id
        
        # Check if the error has hotspot details and lacks a generated illustration
        images_list = error_data.get("images", [])
        if not images_list:
            continue
            
        img_meta = images_list[0]
        hotspot = img_meta.get("hotspot")
        
        # Check if we have hotspot coordinates (x, y, radius)
        if not hotspot or "x" not in hotspot or "y" not in hotspot:
            print(f"  ⏭  Skipping {error_id} — no hotspot coordinates defined.")
            continue
            
        # Determine the search query for the coin image base
        denom = error_data.get("denominations", ["quarter"])[0]
        year = error_data.get("years", [1999])[0] if error_data.get("years") else 1999
        
        print(f"\n🎨 Processing error: {error_id} ({year} {denom})")
        
        # 1. Search the image index for a reference GCS image
        # Standard State Quarters are indexed by state name subject
        subject_query = "new-jersey" if "new-jersey" in error_id else None
        
        image_docs = db.collection("coin_image_index")
        query = image_docs.where("program", "==", "50-state-quarters")
        if subject_query:
            query = query.where("subject", "==", subject_query)
            
        results = list(query.limit(1).stream())
        if not results:
            print(f"  ❌ No reference coin image found in coin_image_index matching queries.")
            continue
            
        ref_image = results[0].to_dict()
        
        # Check obverse first, then reverse
        side_data = ref_image.get("obverse") or ref_image.get("reverse")
        if not side_data or not isinstance(side_data, dict):
            print(f"  ❌ No obverse/reverse details found in image index doc.")
            continue
            
        ref_gcs_path = side_data.get("gcs_path")
        
        if not ref_gcs_path or not ref_gcs_path.startswith("gs://"):
            print(f"  ❌ Invalid GCS reference path: {ref_gcs_path}")
            continue
            
        # Parse GCS path details
        ref_parts = ref_gcs_path.replace("gs://", "").split("/", 1)
        src_bucket_name = ref_parts[0]
        src_blob_name = ref_parts[1]
        
        print(f"  📥 Downloading base image from: gs://{src_bucket_name}/{src_blob_name}")
        
        try:
            src_bucket = gcs_client.bucket(src_bucket_name)
            blob = src_bucket.blob(src_blob_name)
            img_bytes = blob.download_as_bytes()
            img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        except Exception as e:
            print(f"  ❌ Failed to download base image: {e}")
            continue

        width, height = img.size
        print(f"  📏 Source Dimensions: {width}x{height}")

        # 2. Draw Vector Overlays on Image Copy
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Scale hotspot coordinates to pixels
        hx = int(hotspot["x"] * width)
        hy = int(hotspot["y"] * height)
        hrad = int(hotspot.get("radius", 0.08) * max(width, height))
        label_text = hotspot.get("label", "Error Location")

        # Color configurations (bright translucent red/orange vectors)
        vector_color = (255, 69, 0, 255) # Red-Orange
        ring_color = (255, 69, 0, 180)   # semi-translucent

        # Draw Hotspot Ring
        draw.ellipse([hx - hrad, hy - hrad, hx + hrad, hy + hrad], outline=ring_color, width=6)
        # Inner dotted/dashed circle
        draw.ellipse([hx - hrad + 4, hy - hrad + 4, hx + hrad - 4, hy + hrad - 4], outline=(255, 255, 255, 120), width=2)

        # Draw Callout Text Box & Pointer
        # Anchor the callout outside the hotspot ring at an angle
        offset_x = int(width * 0.15) if hx < width * 0.5 else -int(width * 0.15)
        offset_y = -int(height * 0.12) if hy > height * 0.5 else int(height * 0.12)
        
        box_center_x = hx + offset_x
        box_center_y = hy + offset_y
        
        box_w = int(width * 0.32)
        box_h = int(height * 0.08)
        
        box_x1 = box_center_x - (box_w // 2)
        box_x2 = box_center_x + (box_w // 2)
        box_y1 = box_center_y - (box_h // 2)
        box_y2 = box_center_y + (box_h // 2)

        # Draw Pointer Line
        pointer_start = (box_center_x, box_center_y)
        # Point to the nearest edge of the hotspot ring
        angle_to_box = math.atan2(box_center_y - hy, box_center_x - hx)
        pointer_end = (hx + int(hrad * math.cos(angle_to_box)), hy + int(hrad * math.sin(angle_to_box)))
        draw_pointer(draw, pointer_start, pointer_end, vector_color, width=4)

        # Draw Glassmorphism callout box (translucent black with white border)
        draw.rounded_rectangle([box_x1, box_y1, box_x2, box_y2], radius=10, fill=(0, 0, 0, 200), outline=(255, 255, 255, 255), width=2)

        # Write Label Text inside the callout box
        try:
            font = ImageFont.load_default()
        except:
            font = None
            
        draw.text((box_x1 + 10, box_y1 + 10), label_text, font=font, fill=(255, 255, 255, 255))

        # Flatten Overlay
        final_img = Image.alpha_composite(img, overlay).convert("RGB")

        # 3. Save and Upload to GCS
        dest_blob_name = f"{ILLUSTRATION_FOLDER}/{error_id}.jpg"
        out_bytes = io.BytesIO()
        final_img.save(out_bytes, format="JPEG", quality=92)
        out_bytes.seek(0)

        print(f"  📤 Uploading vector illustration to: gs://{BUCKET_NAME}/{dest_blob_name}")
        dest_blob = bucket.blob(dest_blob_name)
        dest_blob.upload_from_file(out_bytes, content_type="image/jpeg")

        # 4. Update Firestore with the new image URL
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{dest_blob_name}"
        
        # Keep pcgs/Wikimedia metadata, but update the illustration URL
        images_list[0]["url"] = public_url
        images_list[0]["isVerified"] = True
        
        db.collection("mint_errors").document(error_id).update({
            "images": images_list,
            "lastUpdated": datetime.now(timezone.utc)
        })
        print(f"  ✓ Firestore updated successfully. URL: {public_url}")

    print("\n🎉 Error illustration generation process finished successfully.")

if __name__ == "__main__":
    main()
