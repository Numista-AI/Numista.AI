import pandas as pd

# Mocking the constants from app.py
DISPLAY_ORDER = [
    "Country", "Year", "Mint Mark", "Denomination", "Quantity", 
    "Program/Series", "Theme/Subject", "Condition", "Surface & Strike Quality", 
    "Grading Service", "Grading Cert #", "Cost", "Purchase Date", 
    "Retailer/Website", "Metal Content", "Melt Value", "Personal Notes", 
    "Personal Ref #", "AI Estimated Value", "Storage Location"
]

def get_empty_collection_df():
    system_cols = ['id', 'deep_dive_status', 'Numismatic Report', 'potentialVariety', 'imageUrlObverse', 'imageUrlReverse']
    final_cols = DISPLAY_ORDER + [c for c in system_cols if c not in DISPLAY_ORDER]
    return pd.DataFrame(columns=final_cols)

def clean_money_string(val):
    if not val: return 0.0
    try:
        s = str(val).replace('$', '').replace(',', '').strip()
        if not s: return 0.0
        return float(s)
    except: return 0.0

# Simulate load_collection returning the new empty DataFrame properly
df = get_empty_collection_df()

print("Created empty DataFrame using new helper")
print(f"Columns: {df.columns.tolist()}")

try:
    # This mirrors app.py line 357 behavior
    print("Attempting to access 'Cost' column...")
    # This should NOT fail now because Cost is in columns
    if 'Cost' in df.columns:
        df['Cost_Clean'] = df['Cost'].apply(clean_money_string)
        print("Success! 'Cost' column accessed and processed.")
    else:
        print("FAILURE: 'Cost' column missing!")
except KeyError as e:
    print(f"Caught UNEXPECTED error: {e}")
except Exception as e:
    print(f"Caught unexpected error: {e}")
