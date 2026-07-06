# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import os, sys, google.auth
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from google.cloud import storage
creds, _ = google.auth.default()
c = storage.Client(credentials=creds, project="studio-9101802118-8c9a8")
bucket = c.bucket("numista-uploads-studio-9101802118-8c9a8")
blobs_iter = bucket.list_blobs(prefix="kaggle/", delimiter="/")
list(blobs_iter)  # consume to populate prefixes
for p in sorted(blobs_iter.prefixes):
    folder = p.rstrip("/").split("/")[-1]
    count  = len(list(bucket.list_blobs(prefix=p)))
    print(f"  {folder:35s} {count:5d} images")
