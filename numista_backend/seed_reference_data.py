#!/usr/bin/env python3
"""
seed_reference_data.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Populates the 'grading_scale' and 'numismatic_glossary' tables in numista.db
with the Sheldon scale benchmarks and numismatic terms.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sqlite3
import json

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_SCRIPT_DIR, "database", "numista.db")

# GCS Reference URLs
GCS_ANATOMY = "gs://studio-9101802118-8c9a8-uploads/academy/illustrations/anatomy_obverse.jpg"
GCS_REVERSE = "gs://studio-9101802118-8c9a8-uploads/academy/illustrations/anatomy_reverse.jpg"
GCS_COMPARISON = "gs://studio-9101802118-8c9a8-uploads/academy/illustrations/grade_comparison.jpg"

# Sheldon scale data
SHELDON_GRADES = [
    {
        "grade_code": "P-1",
        "grade_name": "Poor",
        "min_score": 1,
        "max_score": 1,
        "wear_description": "Heavily worn. Barely identifiable. Rims flat, details mostly gone.",
        "luster_description": "No original luster present.",
        "inspection_tips": "Look for the basic shape and silhouettes to identify denomination and date.",
        "illustration_url": GCS_ANATOMY
    },
    {
        "grade_code": "FR-2",
        "grade_name": "Fair",
        "min_score": 2,
        "max_score": 2,
        "wear_description": "Extremely heavy wear. Main details and date are barely readable.",
        "luster_description": "No original luster present.",
        "inspection_tips": "Make sure you can discern at least part of the date and major legend letters.",
        "illustration_url": GCS_ANATOMY
    },
    {
        "grade_code": "AG-3",
        "grade_name": "About Good",
        "min_score": 3,
        "max_score": 3,
        "wear_description": "Rims are worn down into the lettering, date is heavily worn but readable.",
        "luster_description": "No original luster present.",
        "inspection_tips": "Lettering is starting to merge with the border.",
        "illustration_url": GCS_ANATOMY
    },
    {
        "grade_code": "G-4",
        "grade_name": "Good",
        "min_score": 4,
        "max_score": 5,
        "wear_description": "Rims are fully intact but worn flat. Major design outlines are clear.",
        "luster_description": "No original luster present.",
        "inspection_tips": "Check that the outer rims are complete and distinct from the field.",
        "illustration_url": GCS_ANATOMY
    },
    {
        "grade_code": "VG-8",
        "grade_name": "Very Good",
        "min_score": 8,
        "max_score": 11,
        "wear_description": "Basic details visible. Rims are sharp but designs are mostly flat.",
        "luster_description": "No original luster.",
        "inspection_tips": "Look for initial design features inside the portrait or coat of arms.",
        "illustration_url": GCS_ANATOMY
    },
    {
        "grade_code": "F-12",
        "grade_name": "Fine",
        "min_score": 12,
        "max_score": 19,
        "wear_description": "Moderate wear on all design areas. Recessed lines and letters are clean and distinct.",
        "luster_description": "No original luster.",
        "inspection_tips": "Look for defined hair lines on obverse or clean feathers on reverse.",
        "illustration_url": GCS_ANATOMY
    },
    {
        "grade_code": "VF-20",
        "grade_name": "Very Fine",
        "min_score": 20,
        "max_score": 39,
        "wear_description": "Moderate to light wear. High design areas are worn flat, but all major details remain clear.",
        "luster_description": "No original luster.",
        "inspection_tips": "Check the central details of the portrait; they should be well-defined.",
        "illustration_url": GCS_ANATOMY
    },
    {
        "grade_code": "XF-40",
        "grade_name": "Extremely Fine",
        "min_score": 40,
        "max_score": 49,
        "wear_description": "Very light wear on the highest design surfaces. All features are sharp.",
        "luster_description": "Trace amounts of original mint luster may remain in protected areas.",
        "inspection_tips": "Examine under a loupe to check that only high points show flattening.",
        "illustration_url": GCS_ANATOMY
    },
    {
        "grade_code": "AU-50",
        "grade_name": "About Uncirculated",
        "min_score": 50,
        "max_score": 57,
        "wear_description": "Slight wear or friction on high points. Over half of the original luster remains.",
        "luster_description": "Significant original mint luster is present.",
        "inspection_tips": "Look for wear on Liberty's cheek, hair above the ear, or eagle's breast.",
        "illustration_url": GCS_COMPARISON
    },
    {
        "grade_code": "AU-58",
        "grade_name": "Choice About Uncirculated",
        "min_score": 58,
        "max_score": 59,
        "wear_description": "Only trace wear or friction on the absolute highest design details.",
        "luster_description": "Nearly full original mint luster. Highly reflective.",
        "inspection_tips": "Commonly called a 'slider' because it mimics Mint State. Check for trace luster breaks.",
        "illustration_url": GCS_COMPARISON
    },
    {
        "grade_code": "MS-60",
        "grade_name": "Mint State",
        "min_score": 60,
        "max_score": 62,
        "wear_description": "Zero wear. Heavy bag marks, scratches, or contact blemishes. Dull eye appeal.",
        "luster_description": "Original mint luster present, but may be dull, patchy, or scratched.",
        "inspection_tips": "Verify no circulation wear first, then note heavy surface marks or dullness.",
        "illustration_url": GCS_COMPARISON
    },
    {
        "grade_code": "MS-63",
        "grade_name": "Choice Mint State",
        "min_score": 63,
        "max_score": 64,
        "wear_description": "Zero wear. Moderate bag marks or contact spots. Average to nice strike.",
        "luster_description": "Nice original mint luster.",
        "inspection_tips": "Check focus areas like the face or central reverse for size of contact marks.",
        "illustration_url": GCS_COMPARISON
    },
    {
        "grade_code": "MS-65",
        "grade_name": "Gem Mint State",
        "min_score": 65,
        "max_score": 66,
        "wear_description": "Zero wear. Very few minor, light contact marks. Strong strike.",
        "luster_description": "Brilliant original mint luster. Strong eye appeal.",
        "inspection_tips": "Requires minimal contact marks under a loupe, especially in critical areas.",
        "illustration_url": GCS_COMPARISON
    },
    {
        "grade_code": "MS-70",
        "grade_name": "Perfect Mint State",
        "min_score": 70,
        "max_score": 70,
        "wear_description": "Zero wear. Flawless surface. Perfect strike.",
        "luster_description": "Maximum, blazing original mint luster. Superior eye appeal.",
        "inspection_tips": "Examine under 5x magnification. No marks, hairlines, or defects must be visible.",
        "illustration_url": GCS_COMPARISON
    }
]

# Glossary data
GLOSSARY_TERMS = [
    {
        "term": "Obverse",
        "definition": "The front or face side of a coin, typically depicting a portrait or main design element.",
        "category": "Terminology",
        "colloquial_mappings": ["heads", "front", "face"],
        "illustration_url": GCS_ANATOMY
    },
    {
        "term": "Reverse",
        "definition": "The back or tails side of a coin, typically depicting a seal, shield, or secondary design element.",
        "category": "Terminology",
        "colloquial_mappings": ["tails", "back"],
        "illustration_url": GCS_REVERSE
    },
    {
        "term": "Field",
        "definition": "The flat background portion of a coin's surface that does not contain raised design elements or lettering.",
        "category": "Terminology",
        "colloquial_mappings": ["background", "flat part"],
        "illustration_url": GCS_ANATOMY
    },
    {
        "term": "Luster",
        "definition": "The frosty, reflective sheen on the surface of an uncirculated coin, created by microscopic metal flow lines during minting.",
        "category": "Terminology",
        "colloquial_mappings": ["shine", "glow", "mint frost", "flash"],
        "illustration_url": GCS_COMPARISON
    },
    {
        "term": "Rim",
        "definition": "The raised protective border running around the outer edge of a coin's obverse and reverse.",
        "category": "Terminology",
        "colloquial_mappings": ["edge border", "border", "lip"],
        "illustration_url": GCS_ANATOMY
    },
    {
        "term": "Device",
        "definition": "The primary raised design element or portrait on a coin's surface.",
        "category": "Terminology",
        "colloquial_mappings": ["portrait", "design", "image", "figure"],
        "illustration_url": GCS_ANATOMY
    },
    {
        "term": "Planchet",
        "definition": "The blank metal disc prepared to correct size and weight before being struck by dies in the coin press.",
        "category": "Terminology",
        "colloquial_mappings": ["blank", "flan", "coin blank"],
        "illustration_url": ""
    },
    {
        "term": "Strike",
        "definition": "The process of stamping a planchet with dies, or the crispness and completeness of the resulting design.",
        "category": "Terminology",
        "colloquial_mappings": ["imprint", "stamping", "impress"],
        "illustration_url": ""
    },
    {
        "term": "Bag Marks",
        "definition": "Minor nicks, scratches, or contact blemishes caused by coins colliding with each other in shipping bags at the mint.",
        "category": "Terminology",
        "colloquial_mappings": ["contact marks", "nicks", "scratches", "dings"],
        "illustration_url": ""
    },
    {
        "term": "Slab",
        "definition": "The protective plastic holder used by professional grading services (like PCGS or NGC) to encapsulate graded coins.",
        "category": "Terminology",
        "colloquial_mappings": ["holder", "casing", "plastic shell"],
        "illustration_url": ""
    }
]

def main():
    print(f"Opening database: {DB_PATH}")
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create grading_scale table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grading_scale (
            grade_code         TEXT PRIMARY KEY,
            grade_name         TEXT NOT NULL,
            min_score          INTEGER NOT NULL,
            max_score          INTEGER NOT NULL,
            wear_description   TEXT NOT NULL,
            luster_description TEXT NOT NULL,
            inspection_tips    TEXT NOT NULL,
            illustration_url   TEXT
        )
    """)

    # Create numismatic_glossary table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS numismatic_glossary (
            term                TEXT PRIMARY KEY,
            definition          TEXT NOT NULL,
            category            TEXT DEFAULT 'General',
            colloquial_mappings TEXT NOT NULL,
            illustration_url    TEXT
        )
    """)

    # Insert grading_scale data
    print("Seeding grading_scale...")
    for grade in SHELDON_GRADES:
        cursor.execute("""
            INSERT OR REPLACE INTO grading_scale (
                grade_code, grade_name, min_score, max_score, 
                wear_description, luster_description, inspection_tips, illustration_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            grade["grade_code"],
            grade["grade_name"],
            grade["min_score"],
            grade["max_score"],
            grade["wear_description"],
            grade["luster_description"],
            grade["inspection_tips"],
            grade["illustration_url"]
        ))

    # Insert glossary data
    print("Seeding numismatic_glossary...")
    for item in GLOSSARY_TERMS:
        cursor.execute("""
            INSERT OR REPLACE INTO numismatic_glossary (
                term, definition, category, colloquial_mappings, illustration_url
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            item["term"],
            item["definition"],
            item["category"],
            json.dumps(item["colloquial_mappings"]),
            item["illustration_url"]
        ))

    conn.commit()
    conn.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    main()
