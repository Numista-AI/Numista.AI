import pandas as pd

AJ_CSV = r"C:\Users\ericd\Documents\MyVertexProject\AJ's Coins Backup 8 APR 26.csv"

try:
    aj_df = pd.read_csv(AJ_CSV)
    
    # Filter for American Gold Eagle and $10 denom
    gold_eagles = aj_df[(aj_df['Program/Series'].str.contains('American Gold Eagle', case=False, na=False)) & 
                        (aj_df['Denomination'].astype(str) == '$10')]
    
    if len(gold_eagles) > 0:
        print(f"Found {len(gold_eagles)} $10 American Gold Eagle(s) in AJ's CSV:")
        for idx, row in gold_eagles.iterrows():
            print(f"- Year: {row['Year']} (Condition: {row['Condition']}, Cert: {row['Grading Cert #']})")
    else:
        print("Could not find any $10 American Gold Eagles in the CSV.")
        
except Exception as e:
    print(f"Error: {e}")
