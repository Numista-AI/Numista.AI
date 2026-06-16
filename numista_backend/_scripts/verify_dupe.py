import pandas as pd

def identify_duplicates(new_df, existing_df):
    if existing_df.empty:
        new_df['Status'] = 'NEW'
        return new_df

    # Create composite keys for comparison
    def create_key(row):
        y = str(row.get('Year', '')).strip()
        m = str(row.get('Mint Mark', '')).strip().replace('None', '').replace('nan', '')
        d = str(row.get('Denomination', '')).strip()
        c = str(row.get('Condition', '')).strip()
        return f"{y}|{m}|{d}|{c}".lower()

    existing_keys = set(existing_df.apply(create_key, axis=1))
    
    # Apply status
    new_df['Status'] = new_df.apply(lambda x: 'DUPLICATE' if create_key(x) in existing_keys else 'NEW', axis=1)
    return new_df

# Test Case
print("Running Duplicate Logic Test...")

existing = pd.DataFrame([
    {'Year': '1964', 'Mint Mark': 'D', 'Denomination': 'Dime', 'Condition': 'VF-20'},
    {'Year': '2023', 'Mint Mark': None, 'Denomination': 'Penny', 'Condition': 'MS-65'} # None check
])

new_data = [
    {'Year': '1964', 'Mint Mark': 'D', 'Denomination': 'Dime', 'Condition': 'VF-20'}, # Expected DUPLICATE
    {'Year': '2023', 'Mint Mark': ' ', 'Denomination': 'Penny', 'Condition': 'MS-65'}, # Expected DUPLICATE (Empty vs None)
    {'Year': '1999', 'Mint Mark': 'S', 'Denomination': 'Quarter', 'Condition': 'Proof'} # Expected NEW
]
new = pd.DataFrame(new_data)

result = identify_duplicates(new, existing)
print("\nResults:")
print(result[['Year', 'Status']])

if result.iloc[0]['Status'] == 'DUPLICATE' and result.iloc[2]['Status'] == 'NEW':
    print("\nSUCCESS: Logic Verified")
else:
    print("\nFAIL: Logic Incorrect")
