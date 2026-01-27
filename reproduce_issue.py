import pandas as pd

def clean_money_string(val):
    if not val: return 0.0
    try:
        s = str(val).replace('$', '').replace(',', '').strip()
        if not s: return 0.0
        return float(s)
    except: return 0.0

# Simulate load_collection returning empty DataFrame without columns
df = pd.DataFrame()

print("Created empty DataFrame")

try:
    # This mirrors app.py line 357 behavior
    print("Attempting to access 'Cost' column...")
    df['Cost_Clean'] = df['Cost'].apply(clean_money_string)
    print("Success!")
except KeyError as e:
    print(f"Caught expected error: {e}")
except Exception as e:
    print(f"Caught unexpected error: {e}")
