import pandas as pd

CSV_ARCHIVE = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"
target_keywords = [
    "washington",
    "standing liberty",
    "barber",
    "seated liberty",
    "capped bust",
    "draped bust"
]

try:
    df = pd.read_csv(CSV_ARCHIVE)
    
    # Filter to Quarters
    quarters_df = df[df['denomination'].str.lower().str.contains('quarter', na=False)]
    
    results = {k: 0 for k in target_keywords}
    
    for _, row in quarters_df.iterrows():
        fname = str(row['filename']).lower()
        tags = str(row['tags']).lower()
        combined = fname + " " + tags
        
        for k in target_keywords:
            if k in combined:
                results[k] += 1
                
    print("Quarter Status Check:")
    for k, v in results.items():
        print(f"{k.title()}: {v} images found")
        
except Exception as e:
    print(f"Error reading CSV: {e}")
