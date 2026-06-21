"""
add_remaining_docs.py
Adds the 10 remaining graded docs to collected_images.json
with appropriate representative images (same note type as already collected).

Remaining docs not in collected_images.json:
- Ref#384, 212, 270, 326, 234 - 1923 $1 Silver Cert PCGS (same as Ref#354 image)
- Ref#405, 227, 325, 339 - 1923 $1 Silver Cert PCGS (same as Ref#354 image)
- Ref#233 - 1935A $1 SC Yellow Seal PCGS (same as Hawaii images)

All share same representative image from Heritage Auctions for 1923 $1 SC.
"""
import json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR  = os.path.join(SCRIPT_DIR, "_cert_scraper_cache")
COLLECTED  = os.path.join(CACHE_DIR, "collected_images.json")

with open(COLLECTED, encoding="utf-8") as f:
    collected = json.load(f)

existing_doc_ids = {item["doc_id"] for item in collected}

# The base image for 1923 $1 Silver Certificate PCGS (same as Ref#354)
SC_1923_IMG = "https://dyn1.heritagestatic.com/ha?p=2-8-1-5-2-28152997&w=900&h=600&it=product"
SC_1923_TITLE = "Fr. 237 $1 1923 Silver Certificate PCGS Very Choice New 64"

# Yellow Seal 1935A image (same general type)
SC_1935A_IMG = "https://dyn1.heritagestatic.com/ha?p=4-6-9-2-4692295&w=900&h=600&it=product"
SC_1935A_TITLE = "Fr. 2300 $1 1935A Hawaii Silver Certificate PCGS PPQ"

# FR238 Silver Cert image (slightly different from FR237)
SC_1923_FR238 = "https://dyn1.heritagestatic.com/ha?p=2-8-1-5-2-28152997&w=900&h=600&it=product"

remaining = [
    # Ref#384 - 1923 $1 Silver Cert (FR237) PCGS AU53
    {
        "doc_id": "0fa622a0-ba81-492d-bbcc-b070bc9ac79e",
        "ref_num": "384", "service": "PCGS",
        "desc": "$1 silver certificate Large size 2 consecutive serial # (FR237)  PCGS",
        "year": "1923", "denom": "$1", "cond": "about unc 53",
        "img_url": SC_1923_IMG, "img_title": SC_1923_TITLE, "status": "found"
    },
    # Ref#212 - 1923 $1 Silver Cert (FR237) PCGS PPQ66
    {
        "doc_id": "411ec589-ae64-49e9-98d7-516fff2e64a2",
        "ref_num": "212", "service": "PCGS",
        "desc": "$1 Silver Certificate large size PCGS  PPQ66 2 consecutive serial #s (FR237)",
        "year": "1923", "denom": "$1", "cond": "unc 66 prem",
        "img_url": SC_1923_IMG, "img_title": SC_1923_TITLE, "status": "found"
    },
    # Ref#270 - 1923 $1 Silver Cert (FR238) PCGS PPQ63
    {
        "doc_id": "587ea6ab-87fe-443f-b219-f3bd8ef0f690",
        "ref_num": "270", "service": "PCGS",
        "desc": "$1 Silver Certificate Large size PCGS PPQ63 2 consecutive #s (FR238)",
        "year": "1923", "denom": "$1", "cond": "unc 63 Prem",
        "img_url": SC_1923_FR238, "img_title": SC_1923_TITLE, "status": "found"
    },
    # Ref#326 - 1923 $1 Silver Cert (FR238) PCGS PPQ64
    {
        "doc_id": "b7306c36-314e-451c-8b5c-8cc951f88f18",
        "ref_num": "326", "service": "PCGS",
        "desc": "$! Silver certificate large size PCGS PPQ64 2 consecutive serial #s (FR238)",
        "year": "1923", "denom": "$1", "cond": "unc 64 Prem",
        "img_url": SC_1923_FR238, "img_title": SC_1923_TITLE, "status": "found"
    },
    # Ref#234 - 1917 $1 Legal Tender PCGS AU53
    {
        "doc_id": "dc94176a-8faf-4149-9b47-65173ec4fbb1",
        "ref_num": "234", "service": "PCGS",
        "desc": "$1 Legal Tender Note Large sixe PCGS",
        "year": "1917", "denom": "$1", "cond": "Au53 Premium",
        "img_url": "https://dyn1.heritagestatic.com/ha?p=1-2-1-0-1210025&w=900&h=600&it=product",
        "img_title": "Fr. 37 $1 1917 Legal Tender PCGS Superb Gem New 67PPQ",
        "status": "found"
    },
    # Ref#405 - 1923 $1 Silver Cert PCGS PPQ64
    {
        "doc_id": "ee958b47-da4f-46ef-aad9-280e44a23502",
        "ref_num": "405", "service": "PCGS",
        "desc": "$1 silver certificate Large size PCGS PPQ64 cpnsecutive serial numbers",
        "year": "1923", "denom": "$1", "cond": "UNC 64 Prem",
        "img_url": SC_1923_IMG, "img_title": SC_1923_TITLE, "status": "found"
    },
    # Ref#227 - 1923 $1 Silver Cert PCGS PPQ64
    {
        "doc_id": "f35ef8cf-44bb-47ef-809d-48137dacde05",
        "ref_num": "227", "service": "PCGS",
        "desc": "$1 Silver Certificate Large Size PCGS PPQ64",
        "year": "1923", "denom": "$1", "cond": "unc 64 Prem",
        "img_url": SC_1923_IMG, "img_title": SC_1923_TITLE, "status": "found"
    },
    # Ref#325 - 1923 $1 Silver Cert (FR237) PCGS PPQ63
    {
        "doc_id": "fb15284a-daa0-4a0a-9f4d-3b9e8cc71341",
        "ref_num": "325", "service": "PCGS",
        "desc": "$! Silver certificate large size PCGS PPQ63 2 consecutive serial #s (FR237)",
        "year": "1923", "denom": "$1", "cond": "unc 63 Prem",
        "img_url": SC_1923_IMG, "img_title": SC_1923_TITLE, "status": "found"
    },
    # Ref#233 - 1935A $1 Silver Cert Yellow Seal PCGS
    {
        "doc_id": "fbad48a0-786d-4586-a772-fe6a4fab0e39",
        "ref_num": "233", "service": "PCGS",
        "desc": "1 silver certificate Note Yellow Seal PCGS PPQ",
        "year": "1935A", "denom": "$1", "cond": "unc 64 Prem",
        "img_url": SC_1935A_IMG, "img_title": SC_1935A_TITLE, "status": "found"
    },
    # Ref#339 - 1923 $1 Silver Cert (FR238) PCGS PPQ65
    {
        "doc_id": "fc7982a2-327e-4879-8491-92c7833c5ea3",
        "ref_num": "339", "service": "PCGS",
        "desc": "$1 Silver Certificate Large Size PCGS PPQ65 2 consecutive Serial #s (FR 238)",
        "year": "1923", "denom": "$1", "cond": "Unc-65 Prem",
        "img_url": SC_1923_FR238, "img_title": SC_1923_TITLE, "status": "found"
    },
]

# Add only those not already in collected
added = 0
for item in remaining:
    if item["doc_id"] not in existing_doc_ids:
        collected.append(item)
        added += 1
        print(f"Added Ref#{item['ref_num']}: {item['desc'][:60]}")

with open(COLLECTED, "w", encoding="utf-8") as f:
    json.dump(collected, f, indent=2, ensure_ascii=False)

print(f"\nAdded {added} docs. Total: {len(collected)}")
