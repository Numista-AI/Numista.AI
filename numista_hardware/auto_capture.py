import cv2
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
import numpy as np
import os
import time
import uuid
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
from identify_coin import run_numista_report
from pcgs_service import PCGSService

_pcgs = PCGSService()
from google.cloud import storage, firestore
import shutil

# --- FIRESTORE CLIENT ---
# Uses the same service account key as the rest of the project.
_db = None
def get_firestore_client():
    global _db
    if _db is None:
        key_file = os.path.abspath(os.path.join(os.getcwd(), "..", "numista_backend", "serviceAccountKey.json.json"))
        if os.path.exists(key_file):
            import google.oauth2.service_account as sa
            creds = sa.Credentials.from_service_account_file(key_file)
            _db = firestore.Client(credentials=creds, project="studio-9101802118-8c9a8")
        else:
            # Fallback: use Application Default Credentials
            _db = firestore.Client(project="studio-9101802118-8c9a8")
        logging.info("Firestore client initialized.")
    return _db

USER_EMAIL = "eric@numista.ai"
FIRESTORE_COINS_PATH = f"users/{USER_EMAIL}/coins"
FIRESTORE_COMMANDS_PATH = f"commands/{USER_EMAIL}/pending"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://numista.ai", "http://localhost:*", "http://127.0.0.1:*"]}})

# --- NEW GENERIC HARDWARE SELECTOR ---
# OPTIONS: "AUTOFOCUS_WEBCAM", "MANUAL_MICROSCOPE"
CAMERA_TYPE = "MANUAL_MICROSCOPE" 

def get_camera_settings(type):
    if type == "AUTOFOCUS_WEBCAM":
        return {"width": 1920, "height": 1080, "autofocus": 1}
    else: # Works for both Tomlov and Jiusion
        return {"width": 1920, "height": 1080, "autofocus": 0}

# --- CLOUD SYNC HELPERS ---
def upload_to_gcs_local(file_path, destination_blob_name):
    """Uploads a local file to GCS using the project's service account key."""
    try:
        # Use __file__ so the path is always correct regardless of CWD
        _here = os.path.dirname(os.path.abspath(__file__))
        key_file = os.path.abspath(
            os.path.join(_here, "..", "numista_backend", "serviceAccountKey.json.json")
        )
        if os.path.exists(key_file):
            client = storage.Client.from_service_account_json(key_file)
        else:
            logging.warning(f"[GCS] Key not found at {key_file} — falling back to ADC")
            client = storage.Client()  # Fallback to Application Default Credentials
            
        bucket_name = "studio-9101802118-8c9a8-uploads"
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.cache_control = "public, max-age=31536000"
        blob.upload_from_filename(file_path, content_type="image/jpeg")
        url = f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"
        logging.info(f"[GCS] ✅ Upload OK → {url}")
        return url
    except Exception as e:
        logging.error(f"[GCS] ❌ Upload FAILED for {file_path}: {e}")
        return None


# --- DIGITAL MACRO ZOOM LOGIC ---
def apply_macro_zoom(frame, zoom_factor=2.0):
    """
    Crops the center of the frame and resizes it to simulate a macro lens.
    """
    h, w = frame.shape[:2]
    # Calculate the cropping box
    cw, ch = int(w / zoom_factor), int(h / zoom_factor)
    x1, y1 = int((w - cw) / 2), int((h - ch) / 2)
    
    # Crop and then resize back to original display size
    cropped = frame[y1:y1+ch, x1:x1+cw]
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LANCZOS4)

def crop_coin(frame):
    """
    Crops the center square from a 1920x1080 frame to produce a clean 1080x1080 image.
    The on-screen centering circle guides the user to place the coin in the center,
    so a simple center crop is the correct and reliable approach.
    """
    h, w = frame.shape[:2]
    size = min(h, w)
    cx, cy = w // 2, h // 2
    x1, y1 = cx - size // 2, cy - size // 2
    return frame[y1:y1 + size, x1:x1 + size]



# --- GLOBAL STATE ---
capture_status = {
    "is_active": False,
    "current_step": "IDLE",
    "sharpness": 0,
    "max_sharpness": 0,
    "motion": 0.0,
    "status_message": "Ready to scan.",
    "last_report": None,
    "error": None
}

def capture_worker():
    global capture_status
    capture_status["is_active"] = True
 
    # --- Robust Camera Initialization ---
    cap = None
    successful_idx = -1
    default_res = (640, 480)
    
    # Try USB indices (1, 2) before the integrated webcam (0)
    for idx in [1, 2, 0]:
        temp_cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if temp_cap.isOpened():
            # Quick check to see if we can actually read a frame
            ret, _ = temp_cap.read()
            if ret:
                cap = temp_cap
                successful_idx = idx
                default_res = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                logging.info(f"SUCCESS: Connected to camera at index {idx} (Default: {default_res[0]}x{default_res[1]})")
                break
        temp_cap.release()

    if not cap:
        capture_status["error"] = "HARDWARE ERROR: No camera found on indices 0, 1, or 2. Check USB connection."
        capture_status["is_active"] = False
        return
    # ------------------------------------

    settings = get_camera_settings(CAMERA_TYPE)
    logging.info(f"Applying settings for {CAMERA_TYPE}: {settings}")
    
    # Attempt resolution setup 
    s1 = cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings["width"])
    s2 = cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings["height"])
    logging.info(f"Requested {settings['width']}x{settings['height']}. Results: W={s1}, H={s2}")

    if CAMERA_TYPE == "AUTOFOCUS_WEBCAM":
        cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        capture_status["status_message"] = "WEBCAM: WAITING FOR AF LOCK..."
        time.sleep(2)
    else:
        capture_status["status_message"] = "MICROSCOPE: WARMING UP..."
        for i in range(20):
            ret, _ = cap.read()
            if not ret:
                logging.warning(f"Warning: Warming up frame {i} failed. Stream may be broken.")
                if i == 0:
                    logging.info("Attempting to reset to default resolution...")
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, default_res[0])
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, default_res[1])
            if i % 10 == 0:
                logging.info(f"Warming up... {i}/20")
        
        capture_status["status_message"] = "MICROSCOPE: MANUAL FOCUS REQUIRED"


    # Ensure captures directory exists
    if not os.path.exists("captures"):
        os.makedirs("captures")

    # Workflow Variables
    current_state = 0 
    state_names = ["OBVERSE", "REVERSE", "COMPLETE"]
    max_sharpness = 0.0
    MIN_SHARPNESS_FLOOR = 2000.0
    stability_threshold = 2.0 
    stable_frames_count = 0
    STABLE_RECORDS_MANDATORY = 45  # ~1.5 seconds of total stillness required
    last_blurred = None
    motion_score = 0.0
    has_captured_this_side = False
    last_capture_time = 0.0
    side_lockout_duration = 3.0
    capture_cooldown = 5.0
    FLIP_LOCKOUT_SECS = 8.0
    PRE_CAPTURE_DELAY = 3.0  # Seconds of locked-in holding before the shutter fires
    pre_capture_start = None  # None = not yet armed; float = timestamp when countdown started
    waiting_for_flip = False
    flip_timer_start = 0.0
    db_loaded = os.path.exists("numista_database_ready (1).csv")

    try:
        logging.info("Starting main capture loop...")
        while current_state < 2:
            ret, frame = cap.read()
            if not ret or frame is None:
                logging.warning("Primary frame read failed, retrying...")
                ret, frame = cap.read()
                if not ret:
                    error_msg = f"Camera connection lost during {state_names[current_state]} scan."
                    logging.error(error_msg)
                    capture_status["error"] = error_msg
                    break

            h, w = frame.shape[:2]
            cx, cy = w // 2, h // 2

            if CAMERA_TYPE == "AUTOFOCUS_WEBCAM":
                frame = apply_macro_zoom(frame, zoom_factor=2.5) # Adjust factor as needed

            # Sharpness Calculation
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sharpness_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())

            if sharpness_score > max_sharpness:
                max_sharpness = sharpness_score
            else:
                # Smooth decay: nudges the peak down slowly rather than snapping.
                # This stops the 'Success Zone' marker from jumping around.
                max_sharpness = max_sharpness * 0.95 + sharpness_score * 0.05

            # Stability Detection
            is_stable = False
            blurred = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # --- Coin Detection to prevent empty mat captures ---
            _, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            has_coin = False
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest_contour) > 10000:
                    has_coin = True
                    
            if last_blurred is not None:
                diff = cv2.absdiff(blurred, last_blurred)
                motion_score = float(np.mean(diff))
                
                # Only consider it stable if there's actually a coin visible
                if motion_score < stability_threshold and has_coin:
                    stable_frames_count += 1
                else:
                    stable_frames_count = 0
                
                # Reset pre-capture countdown if motion is detected
                if motion_score >= stability_threshold:
                    pre_capture_start = None

                if waiting_for_flip:
                    if (time.time() - flip_timer_start > FLIP_LOCKOUT_SECS):
                        waiting_for_flip = False
                        
                if stable_frames_count >= STABLE_RECORDS_MANDATORY:
                    is_stable = True
            last_blurred = blurred.copy()

            # Logic
            is_in_focus = (sharpness_score > (max_sharpness * 0.8)) and (sharpness_score >= MIN_SHARPNESS_FLOOR) and has_coin
            current_time = time.time()

            # --- PRE-CAPTURE COUNTDOWN ---
            # Only arm the countdown when the coin is locked-in, stable, not yet captured, and past cooldown
            ready_to_arm = (is_in_focus and is_stable and not has_captured_this_side
                            and not waiting_for_flip and (current_time - last_capture_time > capture_cooldown))

            if ready_to_arm:
                if pre_capture_start is None:
                    pre_capture_start = current_time  # Start the countdown
                    capture_status["pre_capture_start"] = pre_capture_start
                elif (current_time - pre_capture_start) >= PRE_CAPTURE_DELAY:
                    # Countdown complete — FIRE!
                    side_name = state_names[current_state].lower()
                    filename = f"captures/{side_name}_peak.jpg"
                    cropped_img = crop_coin(frame)
                    cv2.imwrite(filename, cropped_img)
                    has_captured_this_side = True
                    last_capture_time = current_time
                    stable_frames_count = 0
                    pre_capture_start = None
                    capture_status["pre_capture_start"] = None
            else:
                if pre_capture_start is not None:
                    pre_capture_start = None
                    capture_status["pre_capture_start"] = None  # Reset if conditions drop


            # State Transition
            if has_captured_this_side:
                if current_state == 0:
                    if (current_time - last_capture_time > 5.0) or (sharpness_score < (max_sharpness * 0.6)):
                        current_state += 1
                        max_sharpness = 0.0
                        has_captured_this_side = False
                        waiting_for_flip = True
                        flip_timer_start = time.time()
                        capture_status["flip_timer_start_ts"] = flip_timer_start

                elif current_state == 1:
                    if (current_time - last_capture_time > 1.5):
                        current_state = 2
                        break


            # Compute countdown seconds remaining for display
            capture_countdown_remaining = None
            if pre_capture_start is not None:
                capture_countdown_remaining = max(0.0, PRE_CAPTURE_DELAY - (current_time - pre_capture_start))

            # Update Global Status for polling
            if capture_countdown_remaining is not None:
                status_msg = f"HOLD STILL — {capture_countdown_remaining:.1f}s"
            elif waiting_for_flip:
                status_msg = "FLIP COIN NOW"
            elif is_in_focus and is_stable:
                status_msg = "READY!"
            else:
                status_msg = "FOCUSING..."

            capture_status.update({
                "current_step": state_names[current_state],
                "sharpness": int(sharpness_score),
                "max_sharpness": int(max_sharpness),
                "motion": round(motion_score, 2),
                "waiting_for_flip": waiting_for_flip,
                "status_message": status_msg
            })

            # --- HARDWARE AGENT UI (Professional Numismatic Overlay) ---
            
            # 1. Centering Circle (Focus Peak Indicator)
            circle_color = (255, 255, 255) # White
            if is_in_focus and is_stable:
                circle_color = (0, 255, 0) # Professional Bright Green
            
            # Dynamic Focus Ring (Large circle relative to frame height)
            radius = int(cy * 0.85)
            cv2.circle(frame, (cx, cy), radius, circle_color, 3) 
            cv2.putText(frame, "CENTER COIN IN CIRCLE", (cx - 160, cy - radius - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # 2. Translucent Info Panel (Top Left)
            overlay = frame.copy()
            cv2.rectangle(overlay, (20, 20), (420, 310), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

            # 3. Database Status Label
            if db_loaded:
                cv2.putText(frame, "DB: US MINT MANIFEST LOADED", (w - 300, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # 4. Dynamic Labels & Colors
            step_text = f"STEP {current_state + 1}: {state_names[current_state]}"
            sharp_text = f"Sharpness: {int(sharpness_score)} / {int(max_sharpness)}"
            
            bar_color = (0, 0, 255) # Red (Unfocused)
            if sharpness_score >= MIN_SHARPNESS_FLOOR:
                if is_in_focus:
                    bar_color = (0, 255, 255) # Yellow (Stable/Analyzing)
                    if is_stable:
                        bar_color = (0, 255, 0) # Green (Ready)
            
            if waiting_for_flip:
                bar_color = (150, 150, 0)

            # Rendering UI Elements
            cv2.putText(frame, step_text, (40, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            cv2.putText(frame, sharp_text, (40, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            
            # Focus Meter Bar (Scaled for 1080p width)
            cv2.rectangle(frame, (40, 140), (340, 160), (50, 50, 50), -1)
            if max_sharpness > 0:
                bw = int((sharpness_score / max_sharpness) * 300)
                cv2.rectangle(frame, (40, 140), (40 + bw, 160), bar_color, -1)
            
            # Success Zone Marker
            floor_x = int((MIN_SHARPNESS_FLOOR / (max_sharpness if max_sharpness > MIN_SHARPNESS_FLOOR else MIN_SHARPNESS_FLOOR * 1.5)) * 300)
            cv2.line(frame, (40 + floor_x, 135), (40 + floor_x, 165), (255, 255, 255), 2)
            cv2.putText(frame, "SUCCESS ZONE", (40 + floor_x, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            cv2.putText(frame, capture_status["status_message"], (40, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bar_color, 2)
            cv2.putText(frame, f"Motion: {motion_score:.2f}", (40, 275), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

            # 5. Pre-Capture Countdown Overlay
            if capture_countdown_remaining is not None:
                sub_overlay = frame.copy()
                cv2.rectangle(sub_overlay, (0, 0), (w, h), (0, 100, 0), -1)
                cv2.addWeighted(sub_overlay, 0.25, frame, 0.75, 0, frame)
                pct = 1.0 - (capture_countdown_remaining / PRE_CAPTURE_DELAY)
                angle = int(pct * 360)
                cv2.ellipse(frame, (cx, cy), (150, 150), -90, 0, angle, (0, 255, 0), 6)
                cv2.putText(frame, f"{capture_countdown_remaining:.1f}s", (cx - 45, cy + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 0), 4)
                cv2.putText(frame, "HOLD STILL", (cx - 125, cy + 65),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

            # 6. Countdown Visual for Flip
            if waiting_for_flip:
                elapsed = time.time() - flip_timer_start
                remaining = max(0, 5.0 - elapsed)
                angle = int((remaining / 5.0) * 360)
                
                # Darken background slightly
                sub_overlay = frame.copy()
                cv2.rectangle(sub_overlay, (0, 0), (w, h), (0, 0, 0), -1)
                cv2.addWeighted(sub_overlay, 0.3, frame, 0.7, 0, frame)
                
                # Large centered text
                cv2.putText(frame, "FLIP COIN", (cx - 150, cy), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 255, 255), 4)
                
                # Progress Ring
                cv2.ellipse(frame, (cx, cy), (120, 120), -90, 0, angle, (0, 255, 255), 4)
                cv2.putText(frame, f"{remaining:.1f}s", (cx - 35, cy + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            # Capture Flash Visual
            if has_captured_this_side and (time.time() - last_capture_time < 0.5):
                cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 255, 0), 20)

            cv2.imshow("Numista.AI - Hardware Agent Monitor", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        if cap:
            cap.release()
        cv2.destroyAllWindows()
        
        if current_state >= 2:
            capture_status["status_message"] = "ANALYZING IMAGES..."
            obv_path = "captures/obverse_peak.jpg"
            rev_path = "captures/reverse_peak.jpg"
            
            coin_data = run_numista_report(obv_path, rev_path)
            
            if coin_data and "file_slug" in coin_data:
                # ── PCGS Enrichment: silver detection + melt value + CoinFacts ──
                capture_status["status_message"] = "ENRICHING WITH PCGS DATA..."
                try:
                    coin_data = _pcgs.enrich_coin(coin_data)
                    silver_flag = "🥈 SILVER" if coin_data.get("is_silver") else "🔵 Not Silver"
                    logging.info(f"[PCGS] Enrichment complete — {silver_flag}  |  Metal: {coin_data.get('metal_content')}  |  Melt: {coin_data.get('melt_value_estimate')}")
                except Exception as pcgs_err:
                    logging.warning(f"[PCGS] Enrichment failed (non-fatal): {pcgs_err}")

                slug = coin_data["file_slug"]
                timestamp = time.strftime("%Y%m%d_%H%M")
                new_obv = f"captures/{slug}_Obverse_{timestamp}.jpg"
                new_rev = f"captures/{slug}_Reverse_{timestamp}.jpg"
                try:
                    os.rename(obv_path, new_obv)
                    os.rename(rev_path, new_rev)
                    coin_data["image_obverse"] = os.path.abspath(new_obv)
                    coin_data["image_reverse"] = os.path.abspath(new_rev)
                    capture_status["last_report"] = coin_data
                    capture_status["status_message"] = "SESSION COMPLETE"
                except Exception as e:
                    capture_status["error"] = f"Rename error: {e}"
            else:
                capture_status["error"] = "Gemini analysis failed or returned no data."

        capture_status["is_active"] = False

# --- FLASK ROUTES ---
# NOTE: /start-scan is now handled by the Firestore command watcher below.
# The website writes to Firestore; the agent picks up the command here.
# This makes the trigger HTTPS-safe (no mixed-content browser errors).

@app.route('/start-scan', methods=['POST'])
def start_scan_route():
    """Local legacy endpoint to trigger a scan from local index.html."""
    if capture_status["is_active"]:
        return jsonify({"status": "error", "message": "Scan already in progress"})
    thread = threading.Thread(target=capture_worker, daemon=True)
    thread.start()
    logging.info("[CMD] capture_worker started via HTTP")
    return jsonify({"status": "success"})

@app.route('/add-to-collection', methods=['POST', 'OPTIONS'])
def add_to_collection_route():
    if request.method == 'OPTIONS':
        return '', 204
    data = request.json or {}
    if not data:
        data = capture_status.get("last_report", {})
    if capture_status["is_active"]:
        return jsonify({"status": "error", "message": "Scan still running"})
    threading.Thread(target=_process_coin_save, args=(data,), daemon=True).start()
    return jsonify({"status": "success", "message": "Saving coin..."})

@app.route('/get-status', methods=['GET'])
def get_status():
    """Polled every 500ms by the Flutter app for live sharpness + progress."""
    snapshot = dict(capture_status)

    # Pull out ephemeral timing state (not JSON-serialisable as raw floats are fine,
    # but we compute the remaining seconds here at request time so the UI is accurate).
    pre_start = snapshot.pop("pre_capture_start", None)
    flip_start = snapshot.pop("flip_timer_start_ts", None)
    now = time.time()

    snapshot["capture_countdown_remaining"] = (
        round(max(0.0, 3.0 - (now - pre_start)), 1) if pre_start else None
    )
    snapshot["flip_time_remaining"] = (
        round(max(0.0, 8.0 - (now - flip_start)), 1)
        if flip_start and snapshot.get("waiting_for_flip")
        else None
    )

    return jsonify(snapshot)

# ─── Firestore Command Watcher ────────────────────────────────────────────────
def _process_coin_save(data: dict):
    """
    Shared logic used by both the Firestore save_coin command
    and the legacy HTTP /add-to-collection endpoint.
    Uploads images to GCS and writes a Firestore coin document.
    """
    slug = data.get("file_slug", "manual_entry")
    timestamp = time.strftime("%Y%m%d_%H%M")
    coin_id = str(uuid.uuid4())

    verified_dir = "verified_images"
    os.makedirs(verified_dir, exist_ok=True)

    report = capture_status.get("last_report") or {}
    obv_src = report.get("image_obverse")
    rev_src = report.get("image_reverse")
    bucket = "studio-9101802118-8c9a8-uploads"
    gcs_obv_url = None
    gcs_rev_url = None

    if obv_src and os.path.exists(obv_src):
        obv_filename = f"{slug}_Obverse_{timestamp}.jpg"
        new_obv = os.path.join(verified_dir, obv_filename)
        shutil.copy(obv_src, new_obv)
        gcs_url = upload_to_gcs_local(new_obv, f"microscope/{USER_EMAIL}/{obv_filename}")
        if gcs_url:
            gcs_obv_url = gcs_url
            # Move (not copy) so captures/ stays clean
            try:
                os.remove(obv_src)
            except OSError:
                pass
            logging.info(f"[SAVE] Obverse → {gcs_obv_url}")
        else:
            logging.error(f"[SAVE] ❌ Obverse GCS upload failed — local copy kept at {new_obv}")

    if rev_src and os.path.exists(rev_src):
        rev_filename = f"{slug}_Reverse_{timestamp}.jpg"
        new_rev = os.path.join(verified_dir, rev_filename)
        shutil.copy(rev_src, new_rev)
        gcs_url = upload_to_gcs_local(new_rev, f"microscope/{USER_EMAIL}/{rev_filename}")
        if gcs_url:
            gcs_rev_url = gcs_url
            try:
                os.remove(rev_src)
            except OSError:
                pass
            logging.info(f"[SAVE] Reverse → {gcs_rev_url}")
        else:
            logging.error(f"[SAVE] ❌ Reverse GCS upload failed — local copy kept at {new_rev}")

    year_val = data.get("year")
    coin_doc = {
        "id": coin_id,
        "Year": str(int(year_val)) if year_val else "",
        "Country": data.get("country", "USA"),
        "Denomination": data.get("denomination", ""),
        "Mint Mark": data.get("mint_mark", ""),
        "Condition": data.get("grade", "Ungraded"),
        "Program/Series": data.get("program_series", ""),
        "Theme/Subject": data.get("theme_subject", ""),
        "AI Estimated Value": data.get("ai_estimated_value", "Pending"),
        "Melt Value": data.get("melt_value_estimate", data.get("melt_value", "Pending")),
        "Metal Content": data.get("metal_content", ""),
        "Is Silver": data.get("is_silver", False),
        "PCGS Number": data.get("pcgs_number"),
        "Variety": data.get("variety", ""),
        "Cost": data.get("cost", "$0.00"),
        "Purchase Date": time.strftime("%Y-%m-%d"),
        "Storage Location": data.get("storage_location", "Hardware Scan"),
        "Personal Notes": data.get("report", ""),
        "Numismatic Report": data.get("report", ""),
        "Quantity": 1,
        "Grading Service": "Other/Raw/None",
        "deep_dive_status": "PENDING",
        "source": "Hardware Agent",
        "user_email": USER_EMAIL,
        "created_at": firestore.SERVER_TIMESTAMP,
        "image_url_obverse": gcs_obv_url or "",
        "image_url_reverse": gcs_rev_url or "",
        "scan_source": "microscope",
        "scan_date": timestamp,
        "verification_confidence": data.get("verification_confidence", ""),
        "reference_images_used": data.get("reference_images_used", 0),
    }


    db = get_firestore_client()
    db.collection(FIRESTORE_COINS_PATH).document(coin_id).set(coin_doc)
    logging.info(f"[SAVE] ✅ Coin written to Firestore → {coin_id}")

    # Write result back to Firestore so the website can show the confirmation
    db.collection(f"commands/{USER_EMAIL}/results").document(coin_id).set({
        "firestore_id": coin_id,
        "gcs_obverse": gcs_obv_url or "",
        "gcs_reverse": gcs_rev_url or "",
        "status": "saved",
        "saved_at": firestore.SERVER_TIMESTAMP,
    })
    return coin_id


def on_command_snapshot(doc_snapshots, changes, read_time):
    """Real-time Firestore listener — fires whenever a command document is added."""
    for change in changes:
        if change.type.name != 'ADDED':
            continue
        doc = change.document
        doc_dict = doc.to_dict()
        cmd = doc_dict.get('command')
        data = doc_dict.get('data') or {}
        logging.info(f"[CMD] Received command: {cmd}")

        # Acknowledge immediately (delete the command doc)
        doc.reference.delete()

        if cmd == 'start_scan':
            if capture_status["is_active"]:
                logging.warning("[CMD] Scan already in progress — ignoring start_scan")
                continue
            thread = threading.Thread(target=capture_worker, daemon=True)
            thread.start()
            logging.info("[CMD] capture_worker started")

        elif cmd == 'save_coin':
            if capture_status["is_active"]:
                logging.warning("[CMD] Scan still running — cannot save yet")
                continue
            threading.Thread(
                target=_process_coin_save, args=(data,), daemon=True
            ).start()

        else:
            logging.warning(f"[CMD] Unknown command: {cmd}")


def start_command_watcher():
    """Starts the Firestore real-time listener in its own daemon thread."""
    try:
        db = get_firestore_client()
        col_ref = db.collection(FIRESTORE_COMMANDS_PATH)
        # on_snapshot runs the callback on a background thread managed by the SDK
        watcher = col_ref.on_snapshot(on_command_snapshot)
        logging.info(f"[CMD] ✅ Firestore command watcher active → {FIRESTORE_COMMANDS_PATH}")
        return watcher
    except Exception as e:
        logging.error(f"[CMD] Failed to start command watcher: {e}", exc_info=True)
        return None

# NOTE: /add-to-collection HTTP endpoint removed.
# Coin saves are now triggered via the Firestore 'save_coin' command.
# This makes the flow work from any HTTPS browser without mixed-content blocks.

if __name__ == "__main__":
    logging.info("="*55)
    logging.info("  Numista.AI Hardware Agent")
    logging.info("  Flask status server  → http://localhost:5000")
    logging.info("  Firestore commands   → commands/%s/pending", USER_EMAIL)
    logging.info("="*55)

    # Start Firestore command watcher (non-blocking — runs on SDK background thread)
    _watcher = start_command_watcher()

    # Start Flask for /get-status polling (blocking)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
