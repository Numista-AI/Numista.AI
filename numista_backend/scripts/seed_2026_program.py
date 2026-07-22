#!/usr/bin/env python3
"""
seed_2026_program.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Registers the 2026 America250 Semiquincentennial Series (Currency and Collectibles)
into SQLite (numista_coins.db) under 'definitive_reference' and Firestore under 'global_programs'.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore

# DB path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(_SCRIPT_DIR)
DB_PATH = os.path.join(BACKEND_DIR, "database", "numista_coins.db")

# Firebase setup
CRED_PATH = os.path.join(BACKEND_DIR, "serviceAccountKey.json.json")

def init_firestore():
    if not firebase_admin._apps:
        if os.path.exists(CRED_PATH):
            cred = credentials.Certificate(CRED_PATH)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
    return firestore.client()

# Canonical 2026 U.S. Mint Dataset
CURRENCY_COINS = [
    {
        "id": "2026_cent",
        "denomination": "One Cent",
        "official_title": "1776 ~ 2026 Collectible Cent",
        "mintage_year": "2026",
        "dual_dated": True,
        "obverse_description": "Victor David Brenner Lincoln",
        "reverse_description": "Union Shield",
        "program": "America250 Core",
        "circulation_type": "Collectible Only (Bags/Rolls/Sets)",
        "varieties": ["P-UNC", "D-UNC", "S-PROOF"],
        "aliases": ["2026 penny", "2026 cent", "250th penny", "dual dated cent"]
    },
    {
        "id": "2026_nickel",
        "denomination": "Five Cents",
        "official_title": "1776 ~ 2026 Jefferson Nickel",
        "mintage_year": "2026",
        "dual_dated": True,
        "obverse_description": "Thomas Jefferson",
        "reverse_description": "Monticello",
        "program": "America250 Core",
        "circulation_type": "Circulating",
        "varieties": ["P-UNC", "D-UNC", "S-PROOF"],
        "aliases": ["2026 nickel", "250th nickel", "dual dated nickel"]
    },
    {
        "id": "2026_dime",
        "denomination": "One Dime",
        "official_title": "Emerging Liberty Dime",
        "mintage_year": "2026",
        "dual_dated": True,
        "obverse_description": "Liberty over Tyranny",
        "reverse_description": "Eagle clutching arrows",
        "program": "America250 Core",
        "circulation_type": "Circulating",
        "varieties": ["P-UNC", "D-UNC", "S-PROOF", "S-SILVER"],
        "aliases": ["2026 dime", "liberty dime", "250th dime"]
    },
    {
        "id": "2026_quarter_mayflower",
        "denomination": "Quarter Dollar",
        "official_title": "America250 Quarter #1: Mayflower Compact",
        "mintage_year": "2026",
        "dual_dated": True,
        "obverse_description": "Two Pilgrims embracing",
        "reverse_description": "The Mayflower",
        "program": "America250 Quarters Program",
        "circulation_type": "Circulating",
        "varieties": ["P-UNC", "D-UNC", "S-PROOF", "S-SILVER"],
        "aliases": ["mayflower quarter", "2026 mayflower", "quarter 1 2026"]
    },
    {
        "id": "2026_quarter_valleyforge",
        "denomination": "Quarter Dollar",
        "official_title": "America250 Quarter #2: Revolutionary War",
        "mintage_year": "2026",
        "dual_dated": True,
        "obverse_description": "Commander George Washington",
        "reverse_description": "Continental Army at Valley Forge",
        "program": "America250 Quarters Program",
        "circulation_type": "Circulating",
        "varieties": ["P-UNC", "D-UNC", "S-PROOF", "S-SILVER"],
        "aliases": ["valley forge quarter", "revolutionary war quarter", "2026 quarter 2"]
    },
    {
        "id": "2026_quarter_declaration",
        "denomination": "Quarter Dollar",
        "official_title": "America250 Quarter #3: Declaration of Independence",
        "mintage_year": "2026",
        "dual_dated": True,
        "obverse_description": "Thomas Jefferson",
        "reverse_description": "Liberty Bell",
        "program": "America250 Quarters Program",
        "circulation_type": "Circulating",
        "varieties": ["P-UNC", "D-UNC", "S-PROOF", "S-SILVER", "P-PRIVY-JULY4", "D-PRIVY-JULY4"],
        "aliases": ["declaration quarter", "liberty bell quarter 2026", "quarter 3 2026", "july 4th privy quarter", "july 4th quarter"]
    },
    {
        "id": "2026_quarter_constitution",
        "denomination": "Quarter Dollar",
        "official_title": "America250 Quarter #4: U.S. Constitution",
        "mintage_year": "2026",
        "dual_dated": True,
        "obverse_description": "James Madison",
        "reverse_description": "Independence Hall (WE THE PEOPLE)",
        "program": "America250 Quarters Program",
        "circulation_type": "Circulating",
        "varieties": ["P-UNC", "D-UNC", "S-PROOF", "S-SILVER"],
        "aliases": ["constitution quarter", "we the people quarter", "madison quarter"]
    },
    {
        "id": "2026_quarter_gettysburg",
        "denomination": "Quarter Dollar",
        "official_title": "America250 Quarter #5: Gettysburg Address",
        "mintage_year": "2026",
        "dual_dated": True,
        "obverse_description": "Abraham Lincoln",
        "reverse_description": "Two hands grasping in unity",
        "program": "America250 Quarters Program",
        "circulation_type": "Circulating",
        "varieties": ["P-UNC", "D-UNC", "S-PROOF", "S-SILVER"],
        "aliases": ["gettysburg quarter", "lincoln quarter 2026", "unity quarter"]
    },
    {
        "id": "2026_half_dollar",
        "denomination": "Half Dollar",
        "official_title": "Enduring Liberty Half Dollar",
        "mintage_year": "2026",
        "dual_dated": True,
        "obverse_description": "Statue of Liberty",
        "reverse_description": "Hands passing Liberty's Torch",
        "program": "America250 Core",
        "circulation_type": "Circulating",
        "varieties": ["P-UNC", "D-UNC", "S-PROOF", "S-SILVER"],
        "aliases": ["2026 half dollar", "liberty half dollar", "250th half"]
    }
]

COLLECTIBLE_COINS = [
    {
        "id": "2026_dollar_trump",
        "denomination": "One Dollar",
        "official_title": "Commemorative Presidential Dollar: Donald J. Trump",
        "mintage_year": "2026",
        "dual_dated": False,
        "obverse_description": "President Donald J. Trump",
        "reverse_description": "Great Seal Bald Eagle",
        "program": "Presidential $1 Coin Program",
        "circulation_type": "Collectible Non-Circulating",
        "varieties": ["P-UNC", "D-UNC", "S-PROOF"],
        "aliases": ["trump dollar", "2026 presidential dollar", "gold trump dollar"]
    },
    {
        "id": "2026_buffalo_gold",
        "denomination": "Fifty Dollars",
        "official_title": "1776 ~ 2026 American Buffalo Gold Coin (with 250 Privy)",
        "mintage_year": "2026",
        "dual_dated": True,
        "obverse_description": "James Earle Fraser Native American",
        "reverse_description": "American Buffalo / Bison",
        "program": "American Buffalo Coin Program",
        "circulation_type": "Collectible Non-Circulating",
        "varieties": ["W-PROOF", "W-UNC"],
        "aliases": ["buffalo gold 2026", "2026 buffalo gold", "250th buffalo gold"]
    },
    {
        "id": "2026_eagle_silver",
        "denomination": "One Dollar",
        "official_title": "1776 ~ 2026 American Silver Eagle (with 250 Privy)",
        "mintage_year": "2026",
        "dual_dated": True,
        "obverse_description": "Adolph A. Weinman Walking Liberty",
        "reverse_description": "Emily Damstra Eagle Landing",
        "program": "American Silver Eagles",
        "circulation_type": "Collectible Non-Circulating",
        "varieties": ["W-PROOF", "S-PROOF", "W-UNC", "P-UNC"],
        "aliases": ["silver eagle 2026", "2026 silver eagle", "250th silver eagle"]
    },
    {
        "id": "2026_eagle_gold",
        "denomination": "Fifty Dollars",
        "official_title": "1776 ~ 2026 American Gold Eagle (with 250 Privy)",
        "mintage_year": "2026",
        "dual_dated": True,
        "obverse_description": "Augustus Saint-Gaudens Liberty",
        "reverse_description": "Jennie Norris Eagle Portrait",
        "program": "American Eagle Gold Coin Program",
        "circulation_type": "Collectible Non-Circulating",
        "varieties": ["W-PROOF", "W-UNC"],
        "aliases": ["gold eagle 2026", "2026 gold eagle", "250th gold eagle"]
    },
    {
        "id": "2026_innovation_dollar",
        "denomination": "One Dollar",
        "official_title": "2026 American Innovation $1 Coin (with 250 Privy)",
        "mintage_year": "2026",
        "dual_dated": False,
        "obverse_description": "Statue of Liberty",
        "reverse_description": "American Innovation Theme",
        "program": "American Innovation $1 Coin Program",
        "circulation_type": "Collectible Non-Circulating",
        "varieties": ["P-UNC", "D-UNC", "S-PROOF", "S-REVERSE-PROOF"],
        "aliases": ["innovation dollar 2026", "2026 innovation dollar"]
    },
    {
        "id": "2026_morgan_dollar",
        "denomination": "One Dollar",
        "official_title": "2026 Morgan Silver Dollar (with 250 Privy)",
        "mintage_year": "2026",
        "dual_dated": False,
        "obverse_description": "George T. Morgan Liberty",
        "reverse_description": "Eagle clutching olive branch and arrows",
        "program": "Morgan Dollars",
        "circulation_type": "Collectible Non-Circulating",
        "varieties": ["P-PROOF", "P-UNC"],
        "aliases": ["morgan 2026", "2026 morgan dollar"]
    },
    {
        "id": "2026_peace_dollar",
        "denomination": "One Dollar",
        "official_title": "2026 Peace Silver Dollar (with 250 Privy)",
        "mintage_year": "2026",
        "dual_dated": False,
        "obverse_description": "Anthony de Francisci Liberty",
        "reverse_description": "Eagle perched on rock looking at dawn",
        "program": "Peace Dollars",
        "circulation_type": "Collectible Non-Circulating",
        "varieties": ["P-PROOF", "P-UNC"],
        "aliases": ["peace 2026", "2026 peace dollar"]
    },
    {
        "id": "2026_companion_medal",
        "denomination": "Medal",
        "official_title": "2026 Semiquincentennial Companion Silver Medal",
        "mintage_year": "2026",
        "dual_dated": False,
        "obverse_description": "Historical Liberty Representation",
        "reverse_description": "Eagle with United States Seal",
        "program": "U.S. Medals",
        "circulation_type": "Collectible Non-Circulating",
        "varieties": ["P-PROOF"],
        "aliases": ["semiquincentennial medal", "2026 silver companion medal"]
    }
]

def seed_sqlite():
    print(f"Connecting to SQLite: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Combine datasets
    all_coins = CURRENCY_COINS + COLLECTIBLE_COINS
    
    inserted = 0
    for coin in all_coins:
        doc_id = f"ref_america250_{coin['id']}"
        year = "1776 ~ 2026" if coin["dual_dated"] else coin["mintage_year"]
        
        # Build a single baseline reference coin
        cur.execute("""
            INSERT OR REPLACE INTO definitive_reference 
            (year, denomination, mint_mark, variety, note, series, category, doc_id, design_obverse, design_reverse, composition) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            year,
            coin["denomination"],
            "", # empty standard mint mark
            coin["official_title"], # variety holds the name
            coin["circulation_type"], # note holds details
            coin["program"],
            "coin" if coin["denomination"] != "Medal" else "medal",
            doc_id,
            coin["obverse_description"],
            coin["reverse_description"],
            "99.9% Silver" if "Silver" in coin["official_title"] or "Morgan" in coin["official_title"] or "Peace" in coin["official_title"] else "Standard Alloy"
        ))
        inserted += 1
        
    conn.commit()
    conn.close()
    print(f"Successfully seeded {inserted} coins into SQLite 'definitive_reference'.")

def seed_firestore(db):
    print("Uploading program records to Firestore 'global_programs'...")
    
    # helper to build coins list
    def build_coins_list(coin_list):
        result = []
        for coin in coin_list:
            varieties_list = []
            for v in coin["varieties"]:
                label = v
                if v == "P-UNC": label = "P (Uncirculated)"
                elif v == "D-UNC": label = "D (Uncirculated)"
                elif v == "S-PROOF": label = "S (Proof - Clad)"
                elif v == "S-SILVER": label = "S (Proof - Silver)"
                elif v == "P-PRIVY-JULY4": label = "P (July 4th Privy Mark)"
                elif v == "D-PRIVY-JULY4": label = "D (July 4th Privy Mark)"
                elif v == "W-PROOF": label = "W (Proof)"
                elif v == "W-UNC": label = "W (Uncirculated)"
                elif v == "S-REVERSE-PROOF": label = "S (Reverse Proof)"
                elif v == "P-PROOF": label = "P (Proof)"
                varieties_list.append({"id": v, "label": label})
                
            result.append({
                "id": coin["id"],
                "name": coin["official_title"],
                "varieties": varieties_list,
                "year": "2026",
                "aliases": coin["aliases"]
            })
        return result

    # 1. Currency Program
    currency_doc = {
        "name": "2026 America250 - Circulating Currency",
        "category": "Circulating Coin Programs",
        "years": "2026",
        "mint_mark_locations": "OBVERSE_PORTRAIT",
        "mint_mark_type": "OBVERSE_PORTRAIT",
        "mint_mark_description": "P or D under obverse portrait or right side",
        "coins": build_coins_list(CURRENCY_COINS),
        "last_synced": firestore.SERVER_TIMESTAMP
    }
    db.collection("global_programs").document("2026_semiquincentennial_currency").set(currency_doc)
    print("  - Seeded Firestore: global_programs/2026_semiquincentennial_currency")
    
    # 2. Collectibles Program
    collectibles_doc = {
        "name": "2026 America250 - Numismatic Collectibles",
        "category": "Collectible Programs",
        "years": "2026",
        "mint_mark_locations": "MIXED",
        "mint_mark_type": "MIXED",
        "mint_mark_description": "Varies by coin. Look for special '250' Privy marks.",
        "coins": build_coins_list(COLLECTIBLE_COINS),
        "last_synced": firestore.SERVER_TIMESTAMP
    }
    db.collection("global_programs").document("2026_semiquincentennial_collectibles").set(collectibles_doc)
    print("  - Seeded Firestore: global_programs/2026_semiquincentennial_collectibles")

if __name__ == "__main__":
    seed_sqlite()
    try:
        db = init_firestore()
        seed_firestore(db)
        print("All database seeding complete!")
    except Exception as e:
        print(f"Firestore seeding skipped or failed: {e}")
