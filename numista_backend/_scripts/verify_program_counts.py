import json
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate(r'c:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

map_path = r'c:\Users\ericd\Documents\MyVertexProject\numista_backend\_scripts\canonical_catalog_map.json'
with open(map_path, 'r', encoding='utf-8') as f:
    catalog_map = json.load(f)

program_aliases = catalog_map.get("program_aliases", {})

def resolve_slot_id(coin_doc, target_program_id, slot):
    explicit_id = coin_doc.get('program_slot_id') or coin_doc.get('canonical_id')
    if explicit_id and explicit_id == slot.get('program_slot_id'):
        return True

    series = str(coin_doc.get('Program/Series') or '').strip().lower()
    theme = str(coin_doc.get('Theme/Subject') or '').strip().lower()
    title = str(coin_doc.get('Title') or coin_doc.get('name') or coin_doc.get('official_title') or '').strip().lower()
    year = str(coin_doc.get('Year') or '').strip()
    denom = str(coin_doc.get('Denomination') or '').strip().lower()

    # 1. Program Alignment
    prog_id = program_aliases.get(series)
    if not prog_id:
        for alias, pid in program_aliases.items():
            if alias and (alias in series or series in alias):
                prog_id = pid
                break

    if not prog_id or prog_id != target_program_id:
        if target_program_id == '2026_semiquincentennial_currency' and ('2026' in series or 'semiquincentennial' in series or 'america250' in series):
            prog_id = '2026_semiquincentennial_currency'
        elif target_program_id == 'washington_quarters_classic' and ('washington' in series or 'quarter' in series):
            prog_id = 'washington_quarters_classic'
        else:
            return False

    slot_slug = slot.get('design_slug', '')
    slot_name = (slot.get('name') or '').lower()
    slot_year = str(slot.get('year') or '')

    # Rule M-04: Multi-Coin Mint Set
    if denom == 'set':
        set_coins = coin_doc.get('SetContents') or coin_doc.get('set_coins') or []
        set_str = ' '.join([str(x) for x in set_coins]).lower() + ' ' + theme + ' ' + title
        if set_str.strip():
            if slot_name and slot_name in set_str:
                return True
            if slot_slug and slot_slug.replace('_', ' ') in set_str:
                return True
        return False

    # Programs with specific designs:
    MULTI_DESIGN_PROGRAMS = {
        'fifty_state_quarters', 'presidential_dollars', 'america_the_beautiful_quarters',
        'american_women_quarters', 'american_innovation_dollars', '2026_semiquincentennial_currency',
        '2026_semiquincentennial_collectibles', 'lincoln_bicentennial_cents_2009', 'dc_territories_quarters'
    }

    if target_program_id in MULTI_DESIGN_PROGRAMS:
        # Require design match!
        if slot_name and ((theme and (slot_name in theme or theme in slot_name)) or (title and (slot_name in title or title in slot_name))):
            if not slot_year or not year or slot_year == year:
                return True
        if slot_slug:
            s_slug_clean = slot_slug.replace('_', ' ')
            if s_slug_clean and ((theme and (s_slug_clean in theme or theme in s_slug_clean)) or (title and (s_slug_clean in title or title in s_slug_clean))):
                if not slot_year or not year or slot_year == year:
                    return True
        if 'lowell' in slot_name and 'lowell' in theme:
            return True
        if 'mayflower' in slot_name and 'mayflower' in theme:
            return True
        return False

    # Single-design series (Roosevelt Dimes, Washington Classic, Morgan, Peace, SBA, Sacagawea)
    if slot_year and year:
        return slot_year == year

    if slot_name and ((theme and (slot_name in theme or theme in slot_name)) or (title and (slot_name in title or title in slot_name))):
        return True

    return False

def verify_user(email, expected_total_coins=None):
    print(f"\n=======================================================")
    print(f"VERIFYING GROUND TRUTH FOR: {email}")
    print(f"=======================================================")
    
    user_docs = list(db.collection('users').document(email).collection('coins').stream())
    actual_count = len(user_docs)
    print(f"Total coins in Firestore for {email}: {actual_count}")
    
    if expected_total_coins is not None:
        assert actual_count == expected_total_coins, f"Expected {expected_total_coins} coins, got {actual_count}!"

    global_progs = list(db.collection('global_programs').stream())

    program_results = {}

    for g_doc in global_progs:
        p_data = g_doc.to_dict()
        p_id = g_doc.id
        p_name = p_data.get('name', p_id)
        slots = p_data.get('coins', [])
        if not slots:
            continue

        collected_slots = set()

        for s in slots:
            slot_id = s.get('program_slot_id') or f"{p_id}_{s.get('name')}"
            for coin_d in user_docs:
                c_dict = coin_d.to_dict()
                if resolve_slot_id(c_dict, p_id, s):
                    collected_slots.add(slot_id)
                    break

        program_results[p_name] = {
            "collected": len(collected_slots),
            "total": len(slots),
            "pct": round((len(collected_slots) / len(slots)) * 100, 1) if slots else 0
        }

    print(f"\n--- PROGRAM COMPLETION SUMMARY ({email}) ---")
    for prog_name, res in program_results.items():
        if res['collected'] > 0:
            print(f"  [COLLECTED] {prog_name:<45} : {res['collected']}/{res['total']} ({res['pct']}%)")
        else:
            print(f"  [  EMPTY  ] {prog_name:<45} : 0/{res['total']}")

    return program_results

def main():
    eric_res = verify_user('eric.seaman@yahoo.com', expected_total_coins=40)

    print("\n--- ASSERTING HARD GROUND TRUTH FOR ERIC SEAMAN ---")
    assert eric_res.get('50 State Quarters', {}).get('collected') == 1, f"50 State Quarters expected 1, got {eric_res.get('50 State Quarters')}"
    assert eric_res.get('Presidential Dollars', {}).get('collected') == 12, f"Presidential Dollars expected 12, got {eric_res.get('Presidential Dollars')}"
    assert eric_res.get('America the Beautiful Quarters (National Parks)', {}).get('collected') == 1, f"ATB expected 1, got {eric_res.get('America the Beautiful Quarters (National Parks)')}"
    assert eric_res.get('Roosevelt Dimes', {}).get('collected') == 1, f"Roosevelt Dimes expected 1, got {eric_res.get('Roosevelt Dimes')}"
    assert eric_res.get('Sacagawea & Native American Dollars', {}).get('collected') == 2, f"Sacagawea expected 2, got {eric_res.get('Sacagawea & Native American Dollars')}"
    assert eric_res.get('Susan B. Anthony Dollars', {}).get('collected') == 2, f"SBA expected 2, got {eric_res.get('Susan B. Anthony Dollars')}"
    assert eric_res.get('Washington Quarters (Classic)', {}).get('collected') == 1, f"Washington Classic expected 1, got {eric_res.get('Washington Quarters (Classic)')}"

    print("\nSUCCESS: All Ground-Truth Hard Assertions PASSED for eric.seaman@yahoo.com! Zero slot over-inflation!")

    jseaman_res = verify_user('jseaman1204@gmail.com', expected_total_coins=4511)
    print("\nSUCCESS: Verification complete for jseaman1204@gmail.com! Evaluated 4,511 coins cleanly.")

if __name__ == '__main__':
    main()
