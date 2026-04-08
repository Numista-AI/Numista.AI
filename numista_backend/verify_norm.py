from datetime import datetime
import pandas as pd

COIN_STANDARDS = {
    "denominations": {
        "Penny": ["1c", "Cent", "One Cent"],
        "Nickel": ["5c", "Five Cents", "V Nickel"],
        "Dime": ["10c", "Mercury Dime"],
        "Dollar": ["$1", "Silver Dollar"]
    },
    "metals": {
        "90% Silver": ["Fine Silver"],
        "Cupro-Nickel": ["Copper-Nickel"]
    }
}

def normalize_coin_data(df):
    if df.empty: return df
    
    def get_canonical(val, category):
        if not val: return val
        s_val = str(val).strip()
        for canonical, aliases in COIN_STANDARDS[category].items():
            if s_val.lower() == canonical.lower(): return canonical
            for alias in aliases:
                if s_val.lower() == alias.lower(): return canonical
        return val # no match found, keep original

    if 'Denomination' in df.columns:
        df['Denomination'] = df['Denomination'].apply(lambda x: get_canonical(x, 'denominations'))
    if 'Metal Content' in df.columns:
        df['Metal Content'] = df['Metal Content'].apply(lambda x: get_canonical(x, 'metals'))

    if 'Purchase Date' in df.columns:
        def clean_date(d):
            if not d or str(d).lower() in ['nan', 'nat', 'none', '']: return datetime.today().strftime('%Y-%m-%d')
            try:
                return pd.to_datetime(d).strftime('%Y-%m-%d')
            except:
                return datetime.today().strftime('%Y-%m-%d')
        df['Purchase Date'] = df['Purchase Date'].apply(clean_date)

    text_cols = ['Theme/Subject', 'Program/Series', 'Mint Mark']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: "" if str(x).lower().strip() in ['n/a', 'blank', 'nan', 'none'] else x)
            
    return df

print("Testing Normalization...")
data = [
    {
        'Denomination': '5c', 
        'Metal Content': 'Copper-Nickel', 
        'Purchase Date': None, 
        'Theme/Subject': 'N/A'
    },
    {
        'Denomination': 'Silver Dollar', 
        'Metal Content': 'Unknown', 
        'Purchase Date': '2023-01-01', 
        'Theme/Subject': 'Liberty'
    }
]
df = pd.DataFrame(data)
normalized = normalize_coin_data(df)

print(normalized[['Denomination', 'Metal Content', 'Purchase Date', 'Theme/Subject']])

if normalized.iloc[0]['Denomination'] == 'Nickel' and normalized.iloc[0]['Metal Content'] == 'Cupro-Nickel':
    print("\nSUCCESS: Normalization Works")
else:
    print("\nFAIL: Mappings Incorrect")
