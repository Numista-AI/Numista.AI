import pandas as pd

AJ_CSV = r"C:\Users\ericd\Documents\MyVertexProject\AJ's Coins Backup 8 APR 26.csv"
REF_CSV = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"

try:
    aj_df = pd.read_csv(AJ_CSV)
    ref_df = pd.read_csv(REF_CSV)
except Exception as e:
    print(f"Error loading CSVs: {e}")
    exit(1)

# Get unique programs in AJ's collection
# We combine Program/Series and Denomination for a distinct list
aj_unique = aj_df[['Program/Series', 'Denomination']].drop_duplicates().dropna()

ref_tags = " ".join(ref_df['tags'].dropna().astype(str).str.lower().tolist())
ref_filenames = " ".join(ref_df['filename'].dropna().astype(str).str.lower().tolist())

missing_programs = []
found_programs = []

for _, row in aj_unique.iterrows():
    prog = str(row['Program/Series']).strip()
    denom = str(row['Denomination']).strip()
    
    # Simplify the program name for searching (e.g. "Franklin Half Dollar" -> "Franklin")
    search_term = prog.lower().replace(denom.lower(), '').strip()
    if not search_term:
        search_term = prog.lower()
        
    search_term = search_term.replace('cent', '').replace('penny', '').replace('dollar', '').replace('quarter', '').strip()
    
    # If the core search term is found anywhere in the tags or filenames of the reference lib
    if search_term in ref_tags or search_term in ref_filenames:
        found_programs.append(f"{prog} ({denom})")
    else:
        missing_programs.append(f"{prog} ({denom})")

print(f"\nTotal Unique Programs in AJ's Collection: {len(aj_unique)}")

print(f"\n--- MISSION ACCOMPLISHED: HAVE IMAGES ({len(found_programs)}) ---")
for f in sorted(found_programs):
    print(f" - {f}")

print(f"\n--- MISSING: NO IMAGES FOUND ({len(missing_programs)}) ---")
for m in sorted(missing_programs):
    print(f" - {m}")

