import pandas as pd

# Data from the React code's 'examples' array
data = [
    {
        "Country": "USA",
        "Year": "1964",
        "Mint Mark": "P",
        "Denomination": "Quarter",
        "Quantity": "1",
        "Program/Series": "Washington Quarters",
        "Theme/Subject": "Silver",
        "Condition": "MS-65",
        "Surface & Strike Quality": "Sharp, full luster",
        "Grading Service": "PCGS (Professional Coin Grading Service)",
        "Grading Certification Number": "12345678",
        "Cost": "$25.00",
        "Purchase Date": "15 JAN 2024",
        "Retailer/Website": "Local Coin Shop",
        "Metal Content": "90% Silver",
        "Melt Value": "$5.40",
        "Personal Notes": "Example entry - please delete before upload",
        "Personal Reference #": "REF-001",
        "Storage Location": "Safe Deposit Box A",
        "Variety (Legacy)": "N/A",
        "Notes (Legacy)": "Standard Silver Quarter"
    },
    {
        "Country": "USA",
        "Year": "1909",
        "Mint Mark": "S",
        "Denomination": "Penny",
        "Quantity": "1",
        "Program/Series": "Lincoln Cents",
        "Theme/Subject": "V.D.B.",
        "Condition": "VF-20",
        "Surface & Strike Quality": "Moderate wear, clear VDB",
        "Grading Service": "NGC (Numismatic Guaranty Company)",
        "Grading Certification Number": "98765432",
        "Cost": "$1200.00",
        "Purchase Date": "22 MAR 2023",
        "Retailer/Website": "Heritage Auctions",
        "Metal Content": "Copper",
        "Melt Value": "$0.02",
        "Personal Notes": "Example entry - please delete before upload",
        "Personal Reference #": "REF-002",
        "Storage Location": "Safe Deposit Box B",
        "Variety (Legacy)": "V.D.B. Variety",
        "Notes (Legacy)": "Key date Lincoln Cent"
    }
]

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel("NumisMate_Collection_Template.xlsx", index=False)
print("Template created: NumisMate_Collection_Template.xlsx")
