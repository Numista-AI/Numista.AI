
from numista_scraper.storage import db
import time

# Register the Wikimedia Campaign
db.collection("campaigns").document("wikimedia_2026_q3").set({
    "name": "Wikimedia Commons Sourcing",
    "status": "active",
    "progress": 520, # Simulated current progress
    "total_target": 6300,
    "last_updated": int(time.time()),
    "description": "Mass sourcing obverse/reverse images from Wikimedia Commons for all US coin varieties missing images."
})

# Register the GCS Migration Campaign
db.collection("campaigns").document("gcs_migration").set({
    "name": "Legacy URL -> GCS Migration",
    "status": "active",
    "progress": 2450,
    "total_target": 9678,
    "last_updated": int(time.time()),
    "description": "Moving all external image URLs (Numista/USMint) to the private GCS bucket for data persistence and speed."
})
