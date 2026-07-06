# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
Scan ALL GCS buckets in the project and inventory every image file.
Reports bucket names, object counts, and samples of image paths.
"""
import os
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")

from google.cloud import storage
import google.auth

credentials, _ = google.auth.default()
client = storage.Client(credentials=credentials, project="studio-9101802118-8c9a8")

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff'}

print("=== ALL GCS BUCKETS IN PROJECT ===\n")
all_buckets = list(client.list_buckets())
print(f"Total buckets found: {len(all_buckets)}\n")

for bucket in all_buckets:
    print(f"Bucket: gs://{bucket.name}")
    try:
        blobs = list(client.list_blobs(bucket.name))
        image_blobs = [b for b in blobs if any(b.name.lower().endswith(ext) for ext in IMAGE_EXTS)]
        total_blobs = len(blobs)
        total_images = len(image_blobs)
        
        # Size summary
        total_size_mb = sum(b.size or 0 for b in image_blobs) / 1024 / 1024
        
        print(f"  Total objects: {total_blobs}")
        print(f"  Image files:   {total_images} ({total_size_mb:.1f} MB)")
        
        # Show top-level folder breakdown
        folders = {}
        for b in image_blobs:
            top = b.name.split('/')[0] if '/' in b.name else '(root)'
            folders[top] = folders.get(top, 0) + 1
        if folders:
            print("  Folder breakdown:")
            for folder, count in sorted(folders.items(), key=lambda x: -x[1])[:15]:
                print(f"    {folder}/: {count} images")
        
        # Show 5 sample paths
        if image_blobs:
            print("  Sample paths:")
            for b in image_blobs[:5]:
                print(f"    gs://{bucket.name}/{b.name}")
        print()
    except Exception as e:
        print(f"  ERROR listing bucket: {e}\n")

print("=== DONE ===")
