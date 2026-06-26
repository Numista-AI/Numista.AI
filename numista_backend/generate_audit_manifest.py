import os
import sqlite3
import sys

# Ensure stdout supports UTF-8 on Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Resolve absolute paths relative to this script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "database", "numista_coins.db")
OUTPUT_MD_PATH = os.path.join(SCRIPT_DIR, "..", "Numista_Database_Audit_Manifest.md")

def make_md_table(headers, rows):
    """
    Formats a list of headers and rows into a clean markdown table.
    """
    if not rows:
        return "*No records found.*\n"
    
    # Table headers
    markdown = "| " + " | ".join(headers) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    
    # Table rows
    for r in rows:
        escaped_cells = []
        for cell in r:
            # Escape pipe symbols in cell values to protect markdown table structure
            val = str(cell if cell is not None else "").replace("|", "\\|").replace("\n", " ")
            escaped_cells.append(val)
        markdown += "| " + " | ".join(escaped_cells) + " |\n"
    return markdown

def run_audit():
    print("="*60)
    print("  Numista.AI - Database Audit Manifest Generator")
    print("="*60)

    if not os.path.exists(DB_PATH):
        print(f"ERROR: Local reference database not found at {DB_PATH}")
        sys.exit(1)

    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    markdown_sections = []
    
    # Title & Metadata
    markdown_sections.append("# Numista.AI - Database Audit Manifest\n")
    markdown_sections.append("Generated automatically by diagnostic audit worker to verify database integrity, schema alignment, and variety coverage.\n")

    # 1. DATABASE SUMMARY
    print("Auditing DATABASE SUMMARY...")
    cur.execute("""
        SELECT category, COUNT(*) as row_count 
        FROM definitive_reference 
        GROUP BY category
    """)
    summary_rows = [list(row) for row in cur.fetchall()]
    # Calculate totals
    total_rows = sum(r[1] for r in summary_rows)
    summary_rows.append(["total", total_rows])
    
    summary_table = make_md_table(["Category", "Total Row Count"], summary_rows)
    markdown_sections.append("## 1. Database Summary\n")
    markdown_sections.append("Verifies that baseline records (10,007 base coins) and parsed/expanded varieties exist in the definitive reference table.\n")
    markdown_sections.append(summary_table + "\n")

    # 2. HISTORIC COIN SAMPLE (1878 Morgan Dollars)
    print("Auditing HISTORIC COIN SAMPLE (1878 Morgan Dollars)...")
    cur.execute("""
        SELECT year, denomination, mint_mark, variety, note, doc_id 
        FROM definitive_reference 
        WHERE (series = 'Morgan Dollars' OR variety LIKE '%Morgan%') AND year = '1878' 
        LIMIT 5
    """)
    historic_rows = [list(row) for row in cur.fetchall()]
    historic_table = make_md_table(["Year", "Denomination", "Mint Mark", "Variety", "Historical Notes / Descriptions", "Document ID"], historic_rows)
    markdown_sections.append("## 2. Historic Coin Sample (1878 Morgan Dollars)\n")
    markdown_sections.append("Validates the division of variety identifiers vs. descriptive/historical notes.\n")
    markdown_sections.append(historic_table + "\n")

    # 3. PRIVY MARK CHECK (2021 Morgan Dollars)
    print("Auditing PRIVY MARK CHECK (2021 Morgan Dollars)...")
    cur.execute("""
        SELECT year, denomination, mint_mark, variety, note, doc_id 
        FROM definitive_reference 
        WHERE series = 'Morgan Dollars' AND year = '2021' AND (mint_mark = 'CC' OR mint_mark = 'O')
    """)
    privy_rows = [list(row) for row in cur.fetchall()]
    privy_table = make_md_table(["Year", "Denomination", "Mint Mark", "Variety", "Historical Notes", "Document ID"], privy_rows)
    markdown_sections.append("## 3. Privy Mark Check (2021 Morgan Dollars)\n")
    markdown_sections.append("Confirms that privy marks struck on Philadelphia coins are cataloged cleanly in the database.\n")
    markdown_sections.append(privy_table + "\n")

    # 4. MODERN 2026 EDGE CASE (2026-W Morgan Dollar)
    print("Auditing MODERN 2026 EDGE CASE (2026-W Morgan Dollar)...")
    cur.execute("""
        SELECT year, denomination, mint_mark, variety, note, doc_id 
        FROM definitive_reference 
        WHERE series = 'Morgan Dollars' AND year = '2026' AND mint_mark = 'W'
    """)
    edge_rows = [list(row) for row in cur.fetchall()]
    edge_table = make_md_table(["Year", "Denomination", "Mint Mark", "Variety", "Historical Notes", "Document ID"], edge_rows)
    markdown_sections.append("## 4. Modern 2026 Edge Case (2026-W Morgan Dollar)\n")
    markdown_sections.append("Verifies proper tracking of contemporary West Point Semiquincentennial mint issues.\n")
    markdown_sections.append(edge_table + "\n")

    # 5. BANKNOTE SUFFIX TEST (FRN District Letters)
    print("Auditing BANKNOTE SUFFIX TEST...")
    cur.execute("""
        SELECT year, denomination, variety, note, doc_id 
        FROM definitive_reference 
        WHERE category = 'banknote' 
          AND CAST(year AS INTEGER) >= 1928
          AND variety LIKE 'Fr. %-%' 
          AND (variety LIKE '%Boston%' OR variety LIKE '%New York%' OR variety LIKE '%Chicago%' OR variety LIKE '%District%')
        LIMIT 3
    """)
    banknote_rows = [list(row) for row in cur.fetchall()]
    banknote_table = make_md_table(["Year", "Denomination", "Variety (Friedberg Suffix)", "Note/District Description", "Document ID"], banknote_rows)
    markdown_sections.append("## 5. Banknote Suffix Test (12-District Federal Reserve Note Expansion)\n")
    markdown_sections.append("Verifies that small-size Federal Reserve Notes are programmatically expanded into 12 district varieties (A-L).\n")
    markdown_sections.append(banknote_table + "\n")

    # 6. ANOMALY COUNTS
    print("Auditing ANOMALY COUNTS...")
    # NULL Check
    cur.execute("""
        SELECT COUNT(*) FROM definitive_reference 
        WHERE year IS NULL OR denomination IS NULL OR mint_mark IS NULL OR 
              variety IS NULL OR note IS NULL OR series IS NULL OR 
              category IS NULL OR doc_id IS NULL
    """)
    null_count = cur.fetchone()[0]

    # Invalid year check using python regex
    cur.execute("SELECT year FROM definitive_reference WHERE year != ''")
    years_list = [row[0] for row in cur.fetchall()]
    import re
    invalid_year_count = sum(1 for y in years_list if not re.match(r"^(1|2)\d{3}(?:[-\s~]+(1|2)\d{3})?[A-Za-z]?$", y))

    # Missing denomination check
    cur.execute("""
        SELECT COUNT(*) FROM definitive_reference 
        WHERE denomination IS NULL OR denomination = ''
    """)
    missing_denom_count = cur.fetchone()[0]

    anomaly_rows = [
        ["Columns containing NULL values", null_count],
        ["Invalid 4-digit years (excluding empty/base coin types)", invalid_year_count],
        ["Empty or missing denomination strings", missing_denom_count]
    ]
    anomaly_table = make_md_table(["Anomaly Type Check", "Count"], anomaly_rows)
    markdown_sections.append("## 6. Anomaly Counts\n")
    markdown_sections.append("Performs sanitization checks for NULL fields, formatting issues, or empty values.\n")
    markdown_sections.append(anomaly_table + "\n")

    # Write output
    full_markdown = "\n".join(markdown_sections)
    print(f"Writing audit manifest to: {OUTPUT_MD_PATH}")
    with open(OUTPUT_MD_PATH, "w", encoding="utf-8") as f:
        f.write(full_markdown)

    conn.close()
    print("Audit manifest generation complete. Diagnostic successful.")

if __name__ == "__main__":
    try:
        run_audit()
    except Exception as e:
        print(f"CRITICAL ERROR running audit diagnostic: {e}", file=sys.stderr)
        sys.exit(1)
