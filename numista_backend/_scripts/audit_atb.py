# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import pandas as pd

CSV_ARCHIVE = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"

try:
    df = pd.read_csv(CSV_ARCHIVE)
    
    # Filter to America the Beautiful
    atb_df = df[df['tags'].str.contains('America The Beautiful', case=False, na=False) | df['filename'].str.contains('atb', case=False, na=False)]
    
    unique_atb_files = atb_df['filename'].unique()
    
    print(f"Total America the Beautiful Quarters uniquely indexed in GCS: {len(unique_atb_files)}")
    
    years = atb_df['year'].unique()
    print(f"Years covered: {sorted(years)}")
    
    import json
    # Let's count them by year just to get a distribution
    counts = atb_df['year'].value_counts().to_dict()
    print("Files per year:")
    for y in sorted(counts.keys()):
        print(f" - {y}: {counts[y]}")

except Exception as e:
    print(f"Error: {e}")
