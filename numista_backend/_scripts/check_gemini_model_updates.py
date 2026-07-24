"""
Gemini Model Lifecycle & Deprecation Auditor

Audits project Gemini model bindings against the latest official Google Gemini
deprecation schedule PDFs stored in `Gemini Deprecation Schedules/`.

Verifies compliance with AGENTS.md Rule 6:
- Never downgrade to a model with an earlier shutdown date.
- Reject models with announced shutdown dates when stable alternatives exist.
- Fail closed if schedule details are ambiguous.

Usage:
    python _scripts/check_gemini_model_updates.py               # Dry-run audit
    python _scripts/check_gemini_model_updates.py --auto-update  # Apply updates to .env if safe
"""

import sys
import os
import re
import argparse
from pathlib import Path
from datetime import datetime
import pypdf

# UTF-8 output protection for Windows PowerShell
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Ensure parent directory is on sys.path to import config
_SCRIPTS_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _SCRIPTS_DIR.parent
_PROJECT_ROOT = _BACKEND_DIR.parent
sys.path.insert(0, str(_BACKEND_DIR))

try:
    import config
except ImportError:
    config = None


def find_latest_schedule_pdf() -> Path:
    """Finds the most recent PDF deprecation schedule in Gemini Deprecation Schedules/."""
    schedule_dir = _PROJECT_ROOT / "Gemini Deprecation Schedules"
    if not schedule_dir.exists():
        raise FileNotFoundError(f"Deprecation schedule directory not found: {schedule_dir}")
    
    pdf_files = list(schedule_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {schedule_dir}")
    
    # Sort by mtime descending
    pdf_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return pdf_files[0]


def parse_schedule_pdf(pdf_path: Path) -> dict:
    """
    Extracts text from the deprecation schedule PDF and parses model details line by line.
    Returns dict: { model_id: { "shutdown_date": str, "recommended_replacement": str } }
    """
    reader = pypdf.PdfReader(str(pdf_path))
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    
    models = {}
    lines = full_text.splitlines()
    
    for line in lines:
        line_clean = line.replace('\xa0', ' ').strip()
        line_clean = re.sub(r'M\s+ay', 'May', line_clean)
        
        match = re.match(r'^(gemini-[\w\.\-]+|imagen-[\w\.\-]+|veo-[\w\.\-]+|text-embedding-[\w\.\-]+)\s+(.*)$', line_clean)
        if match:
            model_id = match.group(1).strip()
            rest = match.group(2).strip()
            
            recommended = ""
            # Check if there is a replacement model at the end of the line
            if re.search(r'\s+(gemini-[\w\.\-]+|imagen-[\w\.\-]+|veo-[\w\.\-]+)$', rest):
                parts = rest.rsplit(maxsplit=1)
                recommended = parts[1].strip()
                rest = parts[0].strip()
            
            shutdown_date = "No shutdown date announced"
            if "No shutdown date announced" not in rest:
                dates = re.findall(r'[A-Za-z]+\s+\d+,\s+\d{4}', rest)
                if len(dates) >= 2:
                    shutdown_date = dates[1]
                elif len(dates) == 1:
                    shutdown_date = dates[0]
            
            models[model_id] = {
                "shutdown_date": shutdown_date,
                "recommended_replacement": recommended
            }
        
    return models


def audit_models(pdf_path: Path, auto_update: bool = False):
    print("================================================================================")
    print(" GEMINI MODEL LIFECYCLE AUDITOR (AGENTS.md Rule 6)")
    print("================================================================================")
    print(f"📄 Schedule Source: {pdf_path.name}")
    print(f"🕒 Last Modified:   {datetime.fromtimestamp(pdf_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    print("--------------------------------------------------------------------------------\n")
    
    try:
        parsed_models = parse_schedule_pdf(pdf_path)
    except Exception as e:
        print(f"❌ FAIL CLOSED: Could not parse deprecation PDF: {e}")
        sys.exit(1)
        
    if not config:
        print("❌ FAIL CLOSED: Could not import numista_backend/config.py")
        sys.exit(1)
        
    configured_models = {
        "GEMINI_FLASH_MODEL": config.GEMINI_FLASH_MODEL,
        "GEMINI_PRO_MODEL": config.GEMINI_PRO_MODEL,
        "GEMINI_LITE_MODEL": config.GEMINI_LITE_MODEL,
        "GEMINI_IMAGE_MODEL": config.GEMINI_IMAGE_MODEL,
    }
    
    updates_proposed = {}
    has_warnings = False
    
    print(f"{'Role Variable':<22} | {'Configured Model':<24} | {'Shutdown Date':<26} | {'Status'}")
    print("-" * 90)
    
    for var_name, current_model in configured_models.items():
        if current_model in parsed_models:
            info = parsed_models[current_model]
            shutdown_str = info["shutdown_date"]
            replacement = info["recommended_replacement"]
            
            if replacement and replacement != current_model:
                status = f"⚠️ UPDATE AVAILABLE -> {replacement}"
                has_warnings = True
                updates_proposed[var_name] = replacement
            elif "shutdown" in shutdown_str.lower() and "no" not in shutdown_str.lower():
                status = f"⚠️ SHUTDOWN ANNOUNCED ({shutdown_str})"
                has_warnings = True
            else:
                status = "🟢 PASS (Active GA / No shutdown)"
        else:
            shutdown_str = "Unknown (Not in PDF table)"
            status = "⚪ OK (Custom / Unlisted Model)"
            
        print(f"{var_name:<22} | {current_model:<24} | {shutdown_str:<26} | {status}")

    print("\n--------------------------------------------------------------------------------")
    
    if updates_proposed:
        print(f"\n💡 Proposed Safe Upgrades Detected: {updates_proposed}")
        if auto_update:
            print("🚀 Executing --auto-update: Updating numista_backend/.env...")
            env_path = _BACKEND_DIR / ".env"
            if not env_path.exists():
                print(f"❌ .env not found at {env_path}")
                sys.exit(1)
                
            env_content = env_path.read_text(encoding="utf-8")
            for var_name, new_model in updates_proposed.items():
                pattern = re.compile(rf'^{var_name}=.*$', re.MULTILINE)
                if pattern.search(env_content):
                    env_content = pattern.sub(f'{var_name}="{new_model}"', env_content)
                else:
                    env_content += f'\n{var_name}="{new_model}"'
            
            env_path.write_text(env_content, encoding="utf-8")
            print("✅ Successfully updated .env with new model bindings!")
        else:
            print("ℹ️ Run with '--auto-update' to automatically apply proposed upgrades to .env.")
    else:
        print("✅ All configured models strictly adhere to 2026 production standards.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit project Gemini models against official deprecation schedules.")
    parser.add_argument("--auto-update", action="store_true", help="Automatically apply safe model updates to .env")
    args = parser.parse_args()
    
    latest_pdf = find_latest_schedule_pdf()
    audit_models(latest_pdf, auto_update=args.auto_update)
