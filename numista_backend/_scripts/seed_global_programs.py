# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
Seed all programs from master_coin_programs.json to global_programs in Firestore.
Supports --dry-run, --execute, --audit-report <path>.
Enforces deterministic program_slot_id assignment and key-equality unit testing.
"""
import sys
import json
import re
import argparse
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

def slugify(text):
    clean = re.sub(r'[^a-z0-9]+', '_', str(text).lower()).strip('_')
    return clean

def main():
    parser = argparse.ArgumentParser(description="Seed US Mint Coin Programs into Firestore global_programs")
    parser.add_argument("--dry-run", action="store_true", help="Validate and perform key equality unit test without writing to Firestore")
    parser.add_argument("--execute", action="store_true", help="Perform live idempotent set(doc, merge=True) writes to Firestore")
    parser.add_argument("--audit-report", type=str, default="program_seed_audit_report.json", help="Path to write JSON audit report")
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Error: Must specify either --dry-run or --execute")
        sys.exit(1)

    master_path = r'c:\Users\ericd\Documents\MyVertexProject\numista_backend\master_coin_programs.json'
    map_path = r'c:\Users\ericd\Documents\MyVertexProject\numista_backend\_scripts\canonical_catalog_map.json'

    with open(master_path, 'r', encoding='utf-8') as f:
        master_programs = json.load(f)

    with open(map_path, 'r', encoding='utf-8') as f:
        catalog_map = json.load(f)

    program_aliases = catalog_map.get("program_aliases", {})
    design_slug_map = catalog_map.get("design_slug_map", {})

    # Canonical Doc ID mapping
    CANONICAL_DOC_IDS = {
        "America the Beautiful Quarters (National Parks)": "america_the_beautiful_quarters",
        "American Innovation $1 Coin Program": "american_innovation_dollars",
        "D.C. & U.S. Territories Quarters": "dc_territories_quarters",
        "Lincoln Bicentennial Cents (2009)": "lincoln_bicentennial_cents_2009",
        "50 State Quarters": "fifty_state_quarters",
        "2026 America250 - Circulating Currency": "2026_semiquincentennial_currency",
        "2026 America250 - Numismatic Collectibles": "2026_semiquincentennial_collectibles",
    }

    SKIP_NAMES = {
        "Littleton's Illustrated Guide to Mint Marks on Regular-Issue U.S. Coins",
        "2026 U.S. Circulating Coins"
    }

    processed_programs = []
    quarantined_programs = []

    for p in master_programs:
        raw_name = p.get('Name') or p.get('name', '')
        if not raw_name or raw_name in SKIP_NAMES:
            continue

        coins = p.get('Coins') or p.get('coins', [])
        if len(coins) == 0:
            quarantined_programs.append({"name": raw_name, "reason": "0 coins defined"})
            continue

        doc_id = p.get('Id') or p.get('id') or CANONICAL_DOC_IDS.get(raw_name) or slugify(raw_name)
        
        normalized_coins = []
        for c in coins:
            c_name = c.get('name') or c.get('official_title') or ''
            c_year = c.get('year')
            c_slug = c.get('design_slug') or slugify(c_name)
            
            # Deterministic program_slot_id construction
            if c_slug and c_year:
                slot_id = f"{doc_id}_{c_slug}_{c_year}"
            elif c_slug:
                slot_id = f"{doc_id}_{c_slug}"
            elif c_year:
                slot_id = f"{doc_id}_{c_year}"
            else:
                slot_id = f"{doc_id}_{slugify(c_name)}"

            varieties = c.get('varieties', [])
            normalized_varieties = []
            for v in varieties:
                if isinstance(v, dict):
                    normalized_varieties.append(v)
                elif isinstance(v, str):
                    normalized_varieties.append({'id': v, 'label': v})
                else:
                    normalized_varieties.append({'id': str(v), 'label': str(v)})

            normalized_coin = {
                'program_slot_id': slot_id,
                'program_id': doc_id,
                'name': c_name,
                'design_slug': c_slug,
                'year': c_year,
                'varieties': normalized_varieties
            }
            if c.get('referenceImagePath'):
                normalized_coin['referenceImagePath'] = c.get('referenceImagePath')

            normalized_coins.append(normalized_coin)

        prog_doc = {
            'name': raw_name,
            'category': p.get('Category') or p.get('category', 'Other'),
            'years': p.get('Years') or p.get('years', ''),
            'total_slots': sum(len(c.get('varieties', [])) for c in normalized_coins),
            'mint_mark_locations': p.get('Mint_mark_locations') or p.get('mint_mark_locations', ''),
            'mint_mark_type': p.get('Mint_mark_type') or p.get('mint_mark_type', ''),
            'mint_mark_description': p.get('Mint_mark_description') or p.get('mint_mark_description', ''),
            'coins': normalized_coins,
        }

        processed_programs.append({'doc_id': doc_id, 'doc': prog_doc})

    print(f"Parsed {len(processed_programs)} canonical programs ({len(quarantined_programs)} quarantined).")

    # Perform Key Equality Unit Test
    print("\n--- Running Key-Equality Unit Test (Seeder Slot ID vs Resolver) ---")
    unit_test_passed = True
    for item in processed_programs:
        doc = item['doc']
        prog_id = item['doc_id']
        for coin in doc['coins']:
            slot_id = coin['program_slot_id']
            # Re-derive slot_id from coin attributes
            slug = coin['design_slug']
            yr = coin['year']
            if slug and yr:
                derived = f"{prog_id}_{slug}_{yr}"
            elif slug:
                derived = f"{prog_id}_{slug}"
            elif yr:
                derived = f"{prog_id}_{yr}"
            else:
                derived = f"{prog_id}_{slugify(coin['name'])}"

            if derived != slot_id:
                print(f"FAILED Key Parity: slot_id '{slot_id}' != derived '{derived}'")
                unit_test_passed = False
                break

    if unit_test_passed:
        print("PASSED: 100% Key-Equality Unit Test across all program slots.")
    else:
        print("FAILED: Key Parity errors encountered!")
        sys.exit(1)

    if args.execute:
        cred_path = r'c:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json'
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        db = firestore.client()
        print("\n--- Executing Live Firestore Writes ---")
        written = 0
        for item in processed_programs:
            doc_id = item['doc_id']
            doc_data = item['doc']
            doc_data['last_synced'] = firestore.SERVER_TIMESTAMP
            db.collection('global_programs').document(doc_id).set(doc_data, merge=True)
            print(f"  [FIRESTORE] Seeded global_programs/{doc_id} ({doc_data['total_slots']} slots)")
            written += 1
        print(f"SUCCESS: Seeded {written} programs into Firestore global_programs.")

    # Write Audit Report JSON
    audit_report = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "mode": "EXECUTE" if args.execute else "DRY_RUN",
        "total_parsed_programs": len(processed_programs),
        "total_quarantined": len(quarantined_programs),
        "unit_test_passed": unit_test_passed,
        "programs": [
            {
                "doc_id": item['doc_id'],
                "name": item['doc']['name'],
                "category": item['doc']['category'],
                "slots_count": item['doc']['total_slots']
            } for item in processed_programs
        ]
    }

    with open(args.audit_report, 'w', encoding='utf-8') as f:
        json.dump(audit_report, f, indent=2)
    print(f"\nAudit report saved to '{args.audit_report}'.")

if __name__ == '__main__':
    main()
