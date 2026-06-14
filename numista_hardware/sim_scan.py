"""
Simulate a full agent scan using existing captures.
This mimics exactly what capture_worker does after collecting both sides.
"""
import os, sys, time, logging
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # ensure correct working dir

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

import shutil

# Copy existing captures to simulate fresh scan output
obv_src = 'captures/2023_Roosevelt_Dime_D_Obverse_20260523_1322.jpg'
rev_src = 'captures/2023_Roosevelt_Dime_D_Reverse_20260523_1322.jpg'
obv_path = 'captures/obverse_peak.jpg'
rev_path = 'captures/reverse_peak.jpg'

shutil.copy2(obv_src, obv_path)
shutil.copy2(rev_src, rev_path)

logging.info("[SIM] Copied test images to obverse_peak.jpg / reverse_peak.jpg")
logging.info("[SIM] obverse_peak.jpg exists: %s (%d bytes)", 
             os.path.exists(obv_path), os.path.getsize(obv_path) if os.path.exists(obv_path) else 0)
logging.info("[SIM] reverse_peak.jpg exists: %s (%d bytes)", 
             os.path.exists(rev_path), os.path.getsize(rev_path) if os.path.exists(rev_path) else 0)

# Run the exact same analysis code as capture_worker
from dotenv import load_dotenv
load_dotenv('.env')
from identify_coin import run_numista_report

logging.info("[SIM] Calling run_numista_report...")
t = time.time()
coin_data = run_numista_report(obv_path, rev_path)
elapsed = round(time.time() - t, 1)

if coin_data and "file_slug" in coin_data:
    slug = coin_data["file_slug"]
    timestamp = time.strftime("%Y%m%d_%H%M")
    new_obv = f"captures/{slug}_Obverse_{timestamp}.jpg"
    new_rev = f"captures/{slug}_Reverse_{timestamp}.jpg"
    try:
        os.rename(obv_path, new_obv)
        os.rename(rev_path, new_rev)
        logging.info("[SIM] SUCCESS in %.1f s", elapsed)
        logging.info("[SIM]   file_slug: %s", slug)
        logging.info("[SIM]   year: %s", coin_data.get('year'))
        logging.info("[SIM]   denomination: %s", coin_data.get('denomination'))
        logging.info("[SIM]   grade: %s", coin_data.get('grade'))
        logging.info("[SIM]   is_silver: %s", coin_data.get('is_silver'))
        logging.info("[SIM]   saved as: %s / %s", new_obv, new_rev)
        print("\n✅ PIPELINE WORKING — coin would show in the UI")
    except Exception as e:
        logging.error("[SIM] Rename failed: %s", e)
else:
    logging.error("[SIM] FAILED after %.1f s — coin_data=%s", elapsed, coin_data)
    print("\n❌ PIPELINE BROKEN — would show 'Gemini analysis failed'")
