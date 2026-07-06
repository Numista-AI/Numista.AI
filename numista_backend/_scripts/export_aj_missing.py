# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import pandas as pd
import re

AJ_CSV = r"C:\Users\ericd\Documents\MyVertexProject\AJ's Coins Backup 8 APR 26.csv"
REF_CSV = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"
OUT_CSV = r"C:\Users\ericd\Documents\MyVertexProject\AJ_Missing_Images_Target_List.csv"

try:
    aj_df = pd.read_csv(AJ_CSV)
    ref_df = pd.read_csv(REF_CSV)
except Exception as e:
    print(f"Error loading CSVs: {e}")
    exit(1)

aj_unique = aj_df[['Program/Series', 'Denomination']].drop_duplicates().dropna()

# Build a searchable corpus from the reference library
corpus = []
for _, row in ref_df.iterrows():
    entry = f"{row.get('tags', '')} {row.get('filename', '')} {row.get('category', '')}".lower()
    corpus.append(entry)
corpus_str = " ".join(corpus)

# Known aliases mapping AJ's exact strings to our database tags
ALIASES = {
    "america the beautiful": "america the beautiful",
    "american innovation": "innovation",
    "american women": "american women",
    "barber": "barber",
    "lincoln": "lincoln",
    "mercury": "mercury",
    "peace dollar": "peace",
    "roosevelt": "roosevelt",
    "sacagawea": "sacagawea",
    "standing liberty": "standing liberty",
    "state and territory quarters": "state quarter", # We have 50 state quarters
    "susan b. anthony": "susan b. anthony",
    "walking liberty": "walking liberty",
    "washington": "washington",
    "franklin half": "franklin",
    "native american": "native american",
    "jefferson": "jefferson",
    "kennedy": "kennedy",
    "bicentennial": "bicentennial",
    "presidential": "presidential",
    "national park": "america the beautiful",
    "innovation": "innovation",
    "us women": "american women",
    "vdb": "lincoln",
    "steel cent": "lincoln",
    "wartime nickel": "jefferson",
    "return to monticello": "jefferson",
    "seated liberty": "seated liberty"
}

missing_data = []

for _, row in aj_unique.iterrows():
    prog = str(row['Program/Series']).strip()
    denom = str(row['Denomination']).strip()
    
    prog_lower = prog.lower()
    denom_lower = denom.lower()
    
    # Clean the program name for baseline search
    search_term = prog_lower.replace(denom_lower, '').strip()
    search_term = re.sub(r'\(.*?\)', '', search_term) # remove stuff in parentheses
    search_term = search_term.replace('cent', '').replace('penny', '').replace('dollar', '').replace('quarter', '').replace('program', '').replace('series', '').strip()
    
    found = False
    
    # 1. Check strict alias matching first
    for aj_key, db_key in ALIASES.items():
        if aj_key in prog_lower:
            # Check if the DB key is actually in our corpus
            if db_key in corpus_str:
                found = True
                break
                
    # 2. Check general substring match if no alias matched
    if not found and len(search_term) > 3:
        if search_term in corpus_str:
            found = True
            
    if not found:
        missing_data.append({
            'Program/Series': prog,
            'Denomination': denom,
            'Status': 'Missing Images',
            'Image URLs Found': ''
        })

out_df = pd.DataFrame(missing_data)
# Drop duplicates just in case there are identicals
out_df = out_df.drop_duplicates(subset=['Program/Series'])
out_df = out_df.sort_values(by=['Program/Series'])
out_df.to_csv(OUT_CSV, index=False)
print(f"Successfully generated refined {OUT_CSV} with {len(out_df)} true missing targets.")
