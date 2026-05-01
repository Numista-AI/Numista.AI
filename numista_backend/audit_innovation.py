import pandas as pd

CSV_ARCHIVE = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"

try:
    df = pd.read_csv(CSV_ARCHIVE)
    
    # Filter to American Innovation
    ai_df = df[df['tags'].str.contains('Innovation', case=False, na=False) | df['filename'].str.contains('innovation', case=False, na=False)]
    
    unique_files = ai_df['filename'].unique()
    
    print(f"Total American Innovation Dollars uniquely indexed in GCS: {len(unique_files)}")
    
    # List them out so I can see what we have
    for f in sorted(unique_files):
        print(f" - {f}")

except Exception as e:
    print(f"Error: {e}")
