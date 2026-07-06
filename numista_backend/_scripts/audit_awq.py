# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import os
import pandas as pd

# Define the 20 American Women Quarters
awq_roster = {
    "2022": ["Maya Angelou", "Sally Ride", "Wilma Mankiller", "Nina Otero-Warren", "Anna May Wong"],
    "2023": ["Bessie Coleman", "Edith Kanaka", "Eleanor Roosevelt", "Jovita Idar", "Maria Tallchief"],
    "2024": ["Pauli Murray", "Patsy Takemoto Mink", "Mary Edwards Walker", "Celia Cruz", "Zitkala-Sa"],
    "2025": ["Ida B. Wells", "Juliette Gordon Low", "Vera Rubin", "Stacey Park Milbern", "Althea Gibson"]
}

CSV_ARCHIVE = r"C:\Users\ericd\Documents\MyVertexProject\reference_library_export.csv"

# The three folders the user mentioned
folders = [
    r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\si_quarters",
    r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\si_quarters\American Women Quarters™ Program _ Smithsonian American Women's History Museum_files",
    r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\wikipedia\American_Women_quarters"
]

try:
    df = pd.read_csv(CSV_ARCHIVE)
    # Filter to AWQ
    awq_df = df[df['tags'].str.contains('American Women', na=False, case=False)]
    gcs_filenames = ' '.join(awq_df['filename'].dropna().str.lower().tolist())
except:
    gcs_filenames = ""

local_filenames = ""
for folder in folders:
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                local_filenames += f.lower() + " "

# Normalize strings for comparison
def is_found(name, source_str):
    name_simple = name.replace("-", " ").replace(".", "").replace("'", "").lower()
    source_simple = source_str.replace("-", " ").replace(".", "").replace("_", " ").lower()
    # Check if words match
    words = name_simple.split()
    # If the main identifying word is in the string, it's found
    # We use the surname usually
    key_word = words[-1]
    if key_word in source_simple:
        return True
    # If key word fails, check the full name
    if name_simple in source_simple:
        return True
    return False

missing = []

for year, women in awq_roster.items():
    for woman in women:
        # Check CSV first
        if is_found(woman, gcs_filenames):
            pass # We have it fully ingested
        # Check Staging next
        elif is_found(woman, local_filenames):
            pass # We have it staged
        else:
            missing.append(f"{year} - {woman}")

print(f"Total Missing: {len(missing)}")
for m in missing:
    print(f"- {m}")
