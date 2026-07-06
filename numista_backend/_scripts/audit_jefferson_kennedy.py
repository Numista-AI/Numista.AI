# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import pandas as pd

CSV_ARCHIVE = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"

try:
    df = pd.read_csv(CSV_ARCHIVE)
    
    jefferson_count = df[df['tags'].str.contains('Jefferson', case=False, na=False) | df['filename'].str.contains('jefferson', case=False, na=False)].shape[0]
    kennedy_count = df[df['tags'].str.contains('Kennedy', case=False, na=False) | df['filename'].str.contains('kennedy', case=False, na=False)].shape[0]
    
    print(f"Jefferson Nickels in DB: {jefferson_count}")
    print(f"Kennedy Half Dollars in DB: {kennedy_count}")

except Exception as e:
    print(f"Error: {e}")
