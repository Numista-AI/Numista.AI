"""
Numista.AI -- Daily Beta Feedback Test Miner (Hardened v2)
Scans a designated daily beta testing folder (e.g. '13 AUG 2026', '19 AUG 2026', etc.),
parses all .docx, .md, and .txt feedback documents, extracts granular issue vectors WITHOUT
collapsing distinct complaints, and outputs: numista_tests/fixtures/daily_feedback_manifest.json.
"""
import os
import sys
import glob
import json
import time
import re

try:
    import docx
except ImportError:
    docx = None

BASE_FEEDBACK_DIR = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING"
FIXTURES_DIR = r"C:\Users\ericd\Documents\MyVertexProject\numista_tests\fixtures"
MANIFEST_PATH = os.path.join(FIXTURES_DIR, "daily_feedback_manifest.json")

def read_file_content(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".docx":
        if not docx:
            return ""
        try:
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            print(f"Error reading docx {file_path}: {e}")
            return ""
    elif ext in [".md", ".txt"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")
            return ""
    return ""

def find_target_folder(date_or_folder=None):
    if not os.path.exists(BASE_FEEDBACK_DIR):
        print(f"Base feedback directory not found: {BASE_FEEDBACK_DIR}")
        return None

    if date_or_folder:
        if os.path.isabs(date_or_folder) and os.path.isdir(date_or_folder):
            return date_or_folder
        candidate = os.path.join(BASE_FEEDBACK_DIR, date_or_folder)
        if os.path.isdir(candidate):
            return candidate

    subdirs = [os.path.join(BASE_FEEDBACK_DIR, d) for d in os.listdir(BASE_FEEDBACK_DIR) 
               if os.path.isdir(os.path.join(BASE_FEEDBACK_DIR, d)) and not d.startswith(".")]
    if not subdirs:
        return None
        
    subdirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return subdirs[0]

def extract_coin_entities(text):
    """Extracts year, denomination, and mint mark from text snippets."""
    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
    year = int(year_match.group(1)) if year_match else None
    
    mint_match = re.search(r"\b([PDSW])\b(?:\s*mint|\s*quarter|\s*dime|\s*cent|\s*dollar)", text, re.IGNORECASE)
    mint_mark = mint_match.group(1).upper() if mint_match else None
    
    denom = None
    for d in ["quarter", "dime", "cent", "nickel", "half dollar", "dollar", "fils", "euro", "peso", "libertad"]:
        if d in text.lower():
            denom = d.capitalize()
            break
            
    return year, mint_mark, denom

def mine_daily_feedback(target_folder=None):
    folder_path = find_target_folder(target_folder)
    if not folder_path:
        print("[MINER ERROR] No valid feedback folder found.")
        return None

    folder_name = os.path.basename(folder_path)
    print(f"=== MINING DAILY BETA FEEDBACK FOLDER: {folder_name} ===")
    print(f"Full Path: {folder_path}")

    feedback_files = []
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            if f.endswith((".docx", ".md", ".txt")) and not f.startswith("~$"):
                feedback_files.append(os.path.join(root, f))

    print(f"Discovered {len(feedback_files)} feedback documents.")

    mined_issues = []
    seen_snippets = set()
    issue_counter = 1

    for fpath in feedback_files:
        rel_path = os.path.relpath(fpath, folder_path)
        content = read_file_content(fpath)
        if not content:
            continue

        paragraphs = [p.strip() for p in content.split("\n") if len(p.strip()) > 20]

        for p in paragraphs:
            # Deduplicate exact identical duplicate text lines across docs
            p_clean = re.sub(r"\s+", " ", p.strip().lower())
            if p_clean in seen_snippets:
                continue

            low = p.lower()
            issue_type = None
            category = "GENERAL_FUNCTIONALITY"
            expected_behavior = ""
            
            # Classification rules with granular vectors
            if any(k in low for k in ["foreign", "world and specialty", "kuwait", "libertad", "euro cent"]):
                issue_type = "FOREIGN_COIN_ROUTING"
                category = "WORLD_ITEMS"
                expected_behavior = "Coin appears under [World] tab and is_foreign is true"
            elif any(k in low for k in ["san antonio", "west point", "america the beautiful", "national parks", "war in the pacific"]):
                issue_type = "2019_W_QUARTER_ALIGNMENT"
                category = "CATALOG_METADATA"
                expected_behavior = "Program is America the Beautiful Quarters and theme is San Antonio Missions"
            elif any(k in low for k in ["program", "checklist", "have/out of", "have/total", "33"]):
                issue_type = "PROGRAM_SLOT_RESOLVER"
                category = "MINT_PROGRAMS"
                expected_behavior = "All 33 official programs render with deterministic SlotResolver counts"
            elif any(k in low for k in ["acquisition cost", "cost basis", "pocket change", "jar", "free", "$0.00", "ukn"]):
                issue_type = "ACQUISITION_COST_BASIS"
                category = "PROVENANCE_FINANCIALS"
                expected_behavior = "Explicit $0.00 cost basis rendered for free/found coins"
            elif any(k in low for k in ["scroll", "scrollbar", "horizontal", "table"]):
                issue_type = "UI_SCROLLBAR_CONTAINER"
                category = "DESKTOP_UI"
                expected_behavior = "Horizontal scrollbar visible without scrolling to bottom"
            elif any(k in low for k in ["contrast", "text is hard to read", "dark mode"]):
                issue_type = "MODAL_CONTRAST_TYPOGRAPHY"
                category = "DESKTOP_UI"
                expected_behavior = "Dialog text maintains high contrast ratio in dark theme"
            elif any(k in low for k in ["morgan", "proof set", "add set", "2002"]):
                issue_type = "MORGAN_AI_SET_INGESTION"
                category = "AI_AGENT"
                expected_behavior = "Morgan AI ingests proof set with child coins and assigns correct mint mark"
            elif any(k in low for k in ["tooltip", "sheldon", "vf-30", "grade badge"]):
                issue_type = "TOOLTIP_GRADE_BADGE"
                category = "DESKTOP_UI"
                expected_behavior = "Hovering grade badge displays Sheldon descriptor popup"
            elif any(k in low for k in ["legislation", "congress.gov", "tab 5"]):
                issue_type = "LEGISLATION_TAB_INDEX"
                category = "CATALOG_METADATA"
                expected_behavior = "Legislation tab rendered at index 5 in detail modal"

            if issue_type:
                year, mint_mark, denom = extract_coin_entities(p)
                seen_snippets.add(p_clean)
                mined_issues.append({
                    "issue_id": f"ISSUE-{issue_counter:03d}",
                    "source_file": rel_path,
                    "type": issue_type,
                    "category": category,
                    "year": year,
                    "mint_mark": mint_mark,
                    "denomination": denom,
                    "snippet": p[:250],
                    "expected_behavior": expected_behavior,
                    "target_account": "eric.seaman@yahoo.com" if category != "AI_AGENT" else "ericdcman@gmail.com"
                })
                issue_counter += 1

    final_manifest = {
        "mined_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "folder_name": folder_name,
        "folder_path": folder_path,
        "total_files_parsed": len(feedback_files),
        "total_issues_extracted": len(mined_issues),
        "issues": mined_issues
    }

    os.makedirs(FIXTURES_DIR, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(final_manifest, f, indent=2)

    print(f"[MINING COMPLETE] Manifest written to {MANIFEST_PATH} with {len(mined_issues)} granular test vectors.")
    return final_manifest

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    mine_daily_feedback(target)
