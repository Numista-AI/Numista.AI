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
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
from identify_coin import run_numista_report
from google.cloud import storage
import shutil

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://numista.ai"}})

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
        # Look for the service account key in the root project directory
        key_file = os.path.abspath(os.path.join(os.getcwd(), "..", "serviceAccountKey.json.json"))
        if os.path.exists(key_file):
            client = storage.Client.from_service_account_json(key_file)
        else:
            client = storage.Client() # Fallback to default credentials
            
        bucket_name = "studio-9101802118-8c9a8-uploads"
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(file_path)
        return f"gs://{bucket_name}/{destination_blob_name}"
    except Exception as e:
        logging.error(f"GCS Local Upload Failed: {e}")
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
    """
    h, w = frame.shape[:2]
    size = min(h, w)
    cx, cy = w // 2, h // 2
    x1, y1 = cx - size // 2, cy - size // 2
    return frame[y1:y1+size, x1:x1+size]

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
    MIN_SHARPNESS_FLOOR = 3000.0 # Increased for Tomlov DM9 optics
    stability_threshold = 2.0 
    stable_frames_count = 0
    STABLE_RECORDS_MANDATORY = 15
    last_blurred = None
    motion_score = 0.0
    has_captured_this_side = False
    last_capture_time = 0.0
    side_lockout_duration = 3.0
    capture_cooldown = 4.0 
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
            if last_blurred is not None:
                diff = cv2.absdiff(blurred, last_blurred)
                motion_score = float(np.mean(diff))
                
                if motion_score < stability_threshold:
                    stable_frames_count += 1
                else:
                    stable_frames_count = 0
                
                if waiting_for_flip:
                    if (time.time() - flip_timer_start > 5.0) or (motion_score > 15.0):
                        waiting_for_flip = False
                if stable_frames_count >= STABLE_RECORDS_MANDATORY:
                    is_stable = True
            last_blurred = blurred.copy()

            # Logic
            is_in_focus = (sharpness_score > (max_sharpness * 0.8)) and (sharpness_score >= MIN_SHARPNESS_FLOOR)
            current_time = time.time()
            
            if is_in_focus and is_stable and not has_captured_this_side and not waiting_for_flip and (current_time - last_capture_time > capture_cooldown):
                side_name = state_names[current_state].lower()
                filename = f"captures/{side_name}_peak.jpg"
                
                # Auto-Crop to 1080x1080 Square
                cropped_img = crop_coin(frame)
                cv2.imwrite(filename, cropped_img)
                
                has_captured_this_side = True
                last_capture_time = current_time
                stable_frames_count = 0 

            # State Transition
            if has_captured_this_side:
                if current_state == 0:
                    if (current_time - last_capture_time > 5.0) or (sharpness_score < (max_sharpness * 0.6)):
                        current_state += 1
                        max_sharpness = 0.0
                        has_captured_this_side = False
                        waiting_for_flip = True
                        flip_timer_start = time.time()
                elif current_state == 1:
                    if (current_time - last_capture_time > 1.5):
                        current_state = 2
                        break

            # Update Global Status for polling
            capture_status.update({
                "current_step": state_names[current_state],
                "sharpness": int(sharpness_score),
                "max_sharpness": int(max_sharpness),
                "motion": round(motion_score, 2),
                "waiting_for_flip": waiting_for_flip,
                "status_message": "READY!" if is_in_focus and is_stable else ("FLIP COIN NOW" if waiting_for_flip else "FOCUSING...")
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

            # 5. Countdown Visual for Flip
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

@app.route('/start-scan', methods=['POST', 'GET'])
def start_scan():
    if capture_status["is_active"]:
        return jsonify({"status": "error", "message": "Scan already in progress"}), 400
    
    # Start worker in a new thread
    thread = threading.Thread(target=capture_worker)
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "success", "message": "Scan initiated"})

@app.route('/get-status', methods=['GET'])
def get_status():
    return jsonify(capture_status)

@app.route('/add-to-collection', methods=['POST'])
def add_to_collection():
    try:
        data = request.json
        logging.info(f"Received data: {data}")
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        logging.info(f"Capture status: {capture_status}")
        slug = data.get("file_slug", "manual_entry")
        timestamp = time.strftime("%Y%m%d_%H%M")
        
        # Paths
        verified_dir = "verified_images"
        if not os.path.exists(verified_dir):
            os.makedirs(verified_dir)
            
        # Copy from captures to verified
        # We look for the most recent captures we just made
        report = capture_status.get("last_report") or {}
        obv_src = report.get("image_obverse")
        rev_src = report.get("image_reverse")
        
        if obv_src and os.path.exists(obv_src):
            obv_filename = f"{slug}_Obverse_{timestamp}.jpg"
            new_obv = os.path.join(verified_dir, obv_filename)
            shutil.copy(obv_src, new_obv)
            # Cloud Upload
            gcs_obv = upload_to_gcs_local(new_obv, f"microscope/{obv_filename}")
            if gcs_obv: data["image_obverse_gcs"] = gcs_obv
            
        if rev_src and os.path.exists(rev_src):
            rev_filename = f"{slug}_Reverse_{timestamp}.jpg"
            new_rev = os.path.join(verified_dir, rev_filename)
            shutil.copy(rev_src, new_rev)
            # Cloud Upload
            gcs_rev = upload_to_gcs_local(new_rev, f"microscope/{rev_filename}")
            if gcs_rev: data["image_reverse_gcs"] = gcs_rev
            
        # Log to Master Log
        master_log = "numista_master_log.csv"
        import pandas as pd
        new_row = pd.DataFrame([{
            "original": slug,
            "new_file": f"{slug}_Obverse_{timestamp}.jpg",
            "attribution": "Numista.AI Hardware Agent",
            "date": timestamp,
            "country": data.get("country"),
            "gcs_obverse": data.get("image_obverse_gcs", ""),
            "gcs_reverse": data.get("image_reverse_gcs", "")
        }])
        
        if os.path.exists(master_log):
            new_row.to_csv(master_log, mode='a', header=False, index=False)
        else:
            new_row.to_csv(master_log, index=False)

        return jsonify({
            "status": "success", 
            "message": "Saved to Local Archive & Cloud Sync Initiated",
            "gcs_obverse": data.get("image_obverse_gcs"),
            "gcs_reverse": data.get("image_reverse_gcs")
        })
        
    except Exception as e:
        logging.error(f"Error adding to collection: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print("Numista.AI Server running at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
