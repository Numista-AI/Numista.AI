# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import subprocess
import json
import sys
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Construct subprocess arguments to avoid shell parsing / escaping issues
cmd = [
    "gcloud", "logging", "read",
    'resource.type="cloud_run_revision" AND resource.labels.service_name="numista-backend" AND textPayload:"Sourcing images and market data for:"',
    "--limit=120",
    "--project=studio-9101802118-8c9a8",
    "--format=json"
]

print("Fetching logs from Google Cloud Logging...")
res = subprocess.run(cmd, capture_output=True, text=True, shell=True)

if res.returncode != 0:
    print("Error fetching logs:")
    print(res.stderr)
    sys.exit(1)

try:
    logs = json.loads(res.stdout)
    print(f"Retrieved {len(logs)} log entries.")
    
    unique_items = []
    seen = set()
    
    for entry in logs:
        text = entry.get("textPayload", "")
        # Extract title from "Sourcing images and market data for: {title}"
        match = re.search(r"Sourcing images and market data for:\s*(.+)$", text)
        if match:
            item = match.group(1).strip()
            if item not in seen:
                seen.add(item)
                unique_items.append(item)
                
    # Sort them
    unique_items.sort()
    
    print("\n============================================================")
    print(f"List of {len(unique_items)} Coin Gaps Filled in the Latest Run:")
    print("============================================================")
    for idx, item in enumerate(unique_items, 1):
        print(f" {idx:3d}. {item}")
    print("============================================================")
except Exception as e:
    print("Error parsing JSON:", e)
    print("Raw output sample:", res.stdout[:500])
