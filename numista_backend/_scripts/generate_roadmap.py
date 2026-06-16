import json

# List of known entities to extract from the messy PDF dump
check_list = [
    "Delaware", "Pennsylvania", "New Jersey", "Georgia", "Connecticut",
    "Massachusetts", "Maryland", "South Carolina", "New Hampshire", "Virginia",
    "New York", "North Carolina", "Rhode Island", "Vermont", "Kentucky",
    "Tennessee", "Ohio", "Louisiana", "Indiana", "Mississippi",
    "Illinois", "Alabama", "Maine", "Missouri", "Arkansas",
    "Michigan", "Florida", "Texas", "Iowa", "Wisconsin",
    "California", "Minnesota", "Oregon", "Kansas", "West Virginia",
    "Nevada", "Nebraska", "Colorado", "North Dakota", "South Dakota",
    "Montana", "Washington", "Idaho", "Wyoming", "Utah",
    "Oklahoma", "New Mexico", "Arizona", "Alaska", "Hawaii",
    "District of Columbia", "Puerto Rico", "Guam", "American Samoa",
    "U.S. Virgin Islands", "Northern Mariana Islands"
]

extracted = []
with open('pdf_dump.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    
for state in check_list:
    if state in content:
        extracted.append({
            "program": "50_State_Quarters",
            "name": state,
            "side": "reverse"  # For State Quarters, only the reverse is unique
        })

# Include the shared Obverse
extracted.append({
    "program": "50_State_Quarters",
    "name": "Washington",
    "side": "obverse",
    "is_shared": True
})

roadmap = {
    "target_manifest": extracted,
    "total_targets": len(extracted)
}

with open("scrape_roadmap.json", "w") as f:
    json.dump(roadmap, f, indent=4)

print(f"Roadmap generated with {len(extracted)} targets.")
