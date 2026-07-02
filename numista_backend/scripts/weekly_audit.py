
import sys, os
from pathlib import Path
from datetime import datetime, timezone
import time

# Set encoding for PowerShell/Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add numista_backend to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from numista_scraper.agent import NumistaScraperAgent
    from numista_scraper.storage import db
    
    print("[Weekly Audit] Initializing automated system audit...")
    
    # 1. Initialize Agent
    agent = NumistaScraperAgent(mode="request")
    
    # 2. Run Audit (target="all", limit=0 means just audit)
    # Note: We need to modify agent.run to support audit-only mode if it doesn't
    processed_coins, processed_errors = agent.run(target="all", limit=0, dry_run=True)
    
    # 3. Read the report
    report_path = Path(__file__).parent.parent / "sourcing_audit_report.md"
    report_content = "Audit report not found."
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
            
    # 4. Save to Firestore under 'weekly_audits'
    ts = int(time.time())
    doc_id = f"audit_{ts}"
    db.collection("weekly_audits").document(doc_id).set({
        "timestamp": ts,
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "report_content": report_content,
        "summary": {
            "coins_processed": processed_coins,
            "errors_processed": processed_errors
        }
    })
    
    print(f"✅ Audit complete. Saved to Firestore: {doc_id}")
    
except Exception as e:
    print(f"❌ Audit Error: {e}")
    import traceback
    traceback.print_exc()
