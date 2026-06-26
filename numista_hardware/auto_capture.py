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
        import sys
        # 1. Try bundled path (if running inside PyInstaller bundle)
        if hasattr(sys, "_MEIPASS"):
            key_file = os.path.join(sys._MEIPASS, "serviceAccountKey.json.json")
        else:
            # 2. Try development path relative to this script
            _here = os.path.dirname(os.path.abspath(__file__))
            key_file = os.path.abspath(
                os.path.join(_here, "..", "numista_backend", "serviceAccountKey.json.json")
            )
            if not os.path.exists(key_file):
                # Fallback to CWD-based path
                key_file = os.path.abspath(
                    os.path.join(os.getcwd(), "..", "numista_backend", "serviceAccountKey.json.json")
                )
                
        if os.path.exists(key_file):
            import google.oauth2.service_account as sa
            creds = sa.Credentials.from_service_account_file(key_file)
            _db = firestore.Client(credentials=creds, project="studio-9101802118-8c9a8")
            logging.info(f"Firestore client initialized with service account key: {key_file}")
        else:
            logging.warning(f"Service account key not found at {key_file}. Falling back to ADC.")
            _db = firestore.Client(project="studio-9101802118-8c9a8")
    return _db

USER_EMAIL = None
FIRESTORE_COINS_PATH = None
FIRESTORE_COMMANDS_PATH = None

# Global watcher reference
_watcher = None

def set_user_email(email):
    global USER_EMAIL, FIRESTORE_COINS_PATH, FIRESTORE_COMMANDS_PATH, _watcher
    USER_EMAIL = email
    FIRESTORE_COINS_PATH = f"users/{USER_EMAIL}/coins"
    FIRESTORE_COMMANDS_PATH = f"commands/{USER_EMAIL}/pending"
    
    # Restart the Firestore command watcher for the new user
    if _watcher:
        try:
            _watcher.unsubscribe()
        except Exception:
            pass
    _watcher = start_command_watcher()
    logging.info(f"Agent paired to {email}")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": [
    "https://numista.ai",
    "https://www.numista.ai",
    "https://numista-vault.web.app",
    "http://localhost:*",
    "http://127.0.0.1:*",
]}}, allow_private_network=True)

# Live preview frame store (thread-safe)
import threading as _threading
_frame_lock = _threading.Lock()
_latest_frame_jpg: bytes = b""

# Event used to pause the idle preview while capture_worker owns the camera
_idle_pause_event = _threading.Event()  # SET = idle thread should stop; CLEAR = run normally
# Event set by idle thread once it has released the camera (capture_worker waits on this)
_idle_stopped_event = _threading.Event()  # SET = idle thread has released camera

# --- NEW GENERIC HARDWARE SELECTOR ---
# OPTIONS: "AUTOFOCUS_WEBCAM", "MANUAL_MICROSCOPE"
CAMERA_TYPE = "MANUAL_MICROSCOPE"

# Active and preferred camera indices
active_camera_idx = -1
preferred_camera_idx = None

# Set to True to show the local OpenCV window during scanning.
# This is the preferred mode: the user uses the cv2 window to manually
# focus the microscope, then the scan proceeds. The web UI shows step/
# sharpness status but is NOT the primary camera view.
SHOW_CV2_WINDOW = True

def get_camera_settings(type):
    if type == "AUTOFOCUS_WEBCAM":
        return {"width": 1920, "height": 1080, "autofocus": 1}
    else: # Works for both Tomlov and Jiusion
        return {"width": 1920, "height": 1080, "autofocus": 0}

def get_preview_camera_settings():
    """Lower-resolution settings for the idle preview stream.
    1280x720 is fast enough for a USB-2 microscope and still sharp
    enough for the user to judge focus and framing.
    """
    return {"width": 1280, "height": 720, "autofocus": 0}

# --- CLOUD SYNC HELPERS ---
def upload_to_gcs_local(file_path, destination_blob_name):
    """Uploads a local file to GCS using the project's service account key."""
    try:
        import sys
        # 1. Try bundled path (if running inside PyInstaller bundle)
        if hasattr(sys, "_MEIPASS"):
            key_file = os.path.join(sys._MEIPASS, "serviceAccountKey.json.json")
        else:
            # 2. Try development path relative to this script
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


# ─── Idle Preview Worker ───────────────────────────────────────────────────────
def _idle_preview_worker():
    """
    Runs as a daemon thread from startup.
    Continuously reads frames from the microscope at a reduced resolution
    (1280×720) and stores them in _latest_frame_jpg so the Flutter app can
    show a live viewfinder at all times — not just during an active scan.

    A digital 2× macro zoom is applied so the preview field-of-view matches
    what the capture worker sees at the same microscope height — no need to
    raise/lower the microscope between preview and scan.

    The focus circle radius matches the capture overlay (cy * 0.85) so the
    user knows exactly what will be captured.

    When capture_worker starts it sets _idle_pause_event; this thread detects
    that, signals _idle_stopped_event (so capture_worker knows the camera is
    free), releases the camera, and waits.  When the scan finishes it clears
    the events and this thread reopens the camera automatically.
    """
    global _latest_frame_jpg
    logging.info("[PREVIEW] Idle preview worker started.")

    while True:
        # ── Wait if a scan is in progress (capture_worker owns the camera) ──
        # NOTE: threading.Event.wait() blocks until the flag is SET (True).
        # Since _idle_pause_event is already SET when we get here, wait()
        # would return immediately — not what we want.  We need to wait until
        # it is CLEARED (scan done), so we use a spin-wait instead.
        if _idle_pause_event.is_set():
            logging.info("[PREVIEW] Paused — waiting for scan to finish.")
            while _idle_pause_event.is_set():
                time.sleep(0.5)
            # give capture_worker a moment to fully release the camera
            time.sleep(1.0)
            logging.info("[PREVIEW] Resuming idle preview.")

        # ── Open camera ──────────────────────────────────────────────────────
        cap = None
        search_order = [preferred_camera_idx] if preferred_camera_idx is not None else [1, 2, 0]
        if preferred_camera_idx is not None:
            fallback = [1, 2, 0]
            if preferred_camera_idx in fallback:
                fallback.remove(preferred_camera_idx)
            search_order.extend(fallback)

        for idx in search_order:
            temp = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if temp.isOpened():
                ret, _ = temp.read()
                if ret:
                    cap = temp
                    global active_camera_idx
                    active_camera_idx = idx
                    logging.info(f"[PREVIEW] Camera opened at index {idx}")
                    break
            temp.release()

        if cap is None:
            logging.warning("[PREVIEW] No camera found — retrying in 5 s.")
            time.sleep(5)
            continue

        # Use lower resolution for a faster, lag-free viewfinder
        preview_settings = get_preview_camera_settings()
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  preview_settings["width"])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, preview_settings["height"])
        # Clamp the OpenCV frame buffer to 1 frame so we always get the
        # freshest image and avoid stale-frame lag buildup.
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Warm up
        for _ in range(6):
            cap.read()

        logging.info("[PREVIEW] Streaming idle frames (1280×720, 2× zoom).")
        last_microscope_check = time.time()
        while not _idle_pause_event.is_set():
            # If preferred camera index changed, break loop to reopen
            if preferred_camera_idx is not None and idx != preferred_camera_idx:
                logging.info(f"[PREVIEW] Preferred camera changed to {preferred_camera_idx}. Reopening...")
                break

            # If currently using built-in webcam (idx == 0), check if a microscope (1 or 2) is now connected
            if idx == 0 and time.time() - last_microscope_check > 5.0:
                last_microscope_check = time.time()
                for test_idx in [1, 2]:
                    test_cap = cv2.VideoCapture(test_idx, cv2.CAP_DSHOW)
                    if test_cap.isOpened():
                        test_ret, _ = test_cap.read()
                        if test_ret:
                            logging.info(f"[PREVIEW] Microscope detected at index {test_idx}! Switching from webcam...")
                            test_cap.release()
                            cap.release()
                            cap = None
                            break
                    test_cap.release()
                if cap is None:
                    # Break the streaming loop to reopen the camera using the standard selection order
                    break

            ret, frame = cap.read()
            if not ret or frame is None:
                logging.warning("[PREVIEW] Frame read failed — reopening camera.")
                break

            # Apply 2× digital macro zoom so the framing matches the capture
            # view — the user should not need to adjust microscope height
            # between preview and scan.
            frame = apply_macro_zoom(frame, zoom_factor=2.0)

            h, w = frame.shape[:2]
            cx, cy = w // 2, h // 2

            # ── Overlay banner ──────────────────────────────────────────────
            cv2.putText(
                frame, "PREVIEW -- Adjust zoom, then press Start Scan",
                (20, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 220, 255), 2,
            )
            # Focus ring — same radius formula as capture_worker so the user
            # sees exactly what will be captured.
            radius = int(cy * 0.85)
            cv2.circle(frame, (cx, cy), radius, (0, 220, 255), 2)

            # Lower JPEG quality (60) — the preview is for positioning, not
            # archival; this halves encode time vs. quality=70.
            ok, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            if ok:
                with _frame_lock:
                    _latest_frame_jpg = buf.tobytes()
            # 10 fps is more than enough for a positioning viewfinder and
            # keeps CPU load low between captures.
            time.sleep(0.10)

        # ── Streaming loop exited — release camera, signal capture_worker ────
        # The cv2 window is the primary focusing/scanning display.
        # The web UI only receives frames during an active scan (pushed by
        # capture_worker). This keeps the web layout compact and eliminates
        # idle-preview lag in the browser.
        cap.release()
        logging.info("[PREVIEW] Camera released — _idle_stopped_event set.")
        _idle_stopped_event.set()

        # Wait for the scan to fully complete before reopening the camera.
        # Same spin-wait: block until _idle_pause_event is CLEARED.
        if _idle_pause_event.is_set():
            while _idle_pause_event.is_set():
                time.sleep(0.5)
            _idle_stopped_event.clear()  # reset signal for next scan cycle
            time.sleep(1.0)

def capture_worker():
    global capture_status
    # Signal the idle preview to yield the camera before we open it
    _idle_pause_event.set()
    _idle_stopped_event.clear()  # will be set by idle thread when it releases
    capture_status["is_active"] = True
    capture_status["current_step"] = "STARTING"
    capture_status["error"] = None
    capture_status["status_message"] = "Initializing camera..."

    cap = None
    current_state = 0
    state_names = ["OBVERSE", "REVERSE", "COMPLETE"]

    try:
        # Force working directory to this script's location so all relative paths
        # (captures/, CSV manifest) work correctly even when run as a hidden process.
        _script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(_script_dir)
        logging.info("[CAP] Working directory: %s", _script_dir)

        # Wait for the idle preview thread to release the camera (max 5 s).
        # This eliminates the race condition where both threads hold the camera
        # simultaneously and the web preview shows the wrong side.
        if not _idle_stopped_event.wait(timeout=5.0):
            logging.warning("[CAP] Idle thread did not confirm release in 5 s — proceeding anyway.")
        time.sleep(0.5)  # cushion for OS to free the device

        # --- Robust Camera Initialization ---
        successful_idx = -1
        default_res = (640, 480)
        
        # Try USB indices (1, 2) before the integrated webcam (0)
        search_order = [preferred_camera_idx] if preferred_camera_idx is not None else [1, 2, 0]
        if preferred_camera_idx is not None:
            fallback = [1, 2, 0]
            if preferred_camera_idx in fallback:
                fallback.remove(preferred_camera_idx)
            search_order.extend(fallback)

        for idx in search_order:
            logging.info(f"[CAP] Probing camera index {idx}...")
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
            if temp_cap:
                temp_cap.release()

        if not cap:
            capture_status["error"] = "HARDWARE ERROR: No camera found on indices 0, 1, or 2. Check USB connection."
            logging.error("[CAP] No camera found.")
            return
        # ------------------------------------

        # Clamp the OpenCV frame buffer to prevent stale-frame lag and reduce the
        # chance of 'Camera connection lost' errors caused by a full buffer queue.
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

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

        logging.info("Starting main capture loop...")
        while current_state < 2:
            ret, frame = cap.read()
            if not ret or frame is None:
                # USB microscopes (especially Jiusion) can drop 1–3 frames due
                # to USB bandwidth bursts.  Retry up to 5 times with a short
                # sleep before declaring the connection lost.
                logging.warning("Primary frame read failed — entering retry loop.")
                _consecutive_fails = 0
                _MAX_CONSECUTIVE_FAILS = 5
                while _consecutive_fails < _MAX_CONSECUTIVE_FAILS:
                    time.sleep(0.1)
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        logging.info(f"[CAP] Frame recovered after {_consecutive_fails + 1} retry(ies).")
                        break
                    _consecutive_fails += 1
                    logging.warning(f"[CAP] Retry {_consecutive_fails}/{_MAX_CONSECUTIVE_FAILS} failed.")
                if not ret or frame is None:
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
                    if os.path.exists(filename):
                        logging.info(f"[CAP] Saved {filename} ({os.path.getsize(filename):,} bytes)")
                    else:
                        logging.error(f"[CAP] cv2.imwrite FAILED for {filename} — file not created!")
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

            # Debug window — only shown when SHOW_CV2_WINDOW is True.
            # In normal use the web UI is the authoritative display.
            if SHOW_CV2_WINDOW:
                cv2.imshow("Numista.AI - Hardware Agent Monitor [DEBUG]", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Encode annotated frame for live web preview (/frame endpoint)
            _ok, _buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            if _ok:
                with _frame_lock:
                    global _latest_frame_jpg
                    _latest_frame_jpg = _buf.tobytes()

    except Exception as e:
        logging.error(f"[CAP] Exception in capture_worker: {e}", exc_info=True)
        capture_status["error"] = f"CRITICAL ERROR: {e}"
        capture_status["status_message"] = "SCAN ERROR"
    finally:
        if cap:
            cap.release()
        cv2.destroyAllWindows()
        
        if current_state >= 2 and not capture_status.get("error"):
            capture_status["status_message"] = "ANALYZING IMAGES..."
            obv_path = "captures/obverse_peak.jpg"
            rev_path = "captures/reverse_peak.jpg"
            
            # Verify both files exist before calling Gemini
            for _p in [obv_path, rev_path]:
                if os.path.exists(_p):
                    logging.info(f"[GEMINI] Input file OK: {_p} ({os.path.getsize(_p):,} bytes)")
                else:
                    logging.error(f"[GEMINI] MISSING input file: {_p} — Gemini call will fail!")

            try:
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
            except Exception as e:
                logging.error(f"[CAP] Exception in report/save pipeline: {e}", exc_info=True)
                capture_status["error"] = f"Analysis error: {e}"

        capture_status["is_active"] = False
        # Signal idle preview to restart (clears the pause so the thread
        # re-opens the camera and resumes streaming)
        _idle_pause_event.clear()
        logging.info("[CAP] capture_worker done — idle preview will resume.")

# --- FLASK ROUTES ---
# NOTE: /start-scan is now handled by the Firestore command watcher below.
# The website writes to Firestore; the agent picks up the command here.
# This makes the trigger HTTPS-safe (no mixed-content browser errors).

@app.route('/start-scan', methods=['POST', 'OPTIONS'])
def start_scan_route():
    """Local legacy endpoint to trigger a scan from local index.html."""
    if request.method == 'OPTIONS':
        return '', 204
    if capture_status["is_active"]:
        return jsonify({"status": "error", "message": "Scan already in progress"})
    thread = threading.Thread(target=capture_worker, daemon=True)
    thread.start()
    logging.info("[CMD] capture_worker started via HTTP")
    return jsonify({"status": "success"})

@app.route('/confirm-flip', methods=['POST', 'OPTIONS'])
def confirm_flip_route():
    """Called by the web UI when the user clicks 'I've flipped the coin'.
    Immediately clears the flip lockout so the reverse capture begins
    without waiting for the auto-timer to expire."""
    if request.method == 'OPTIONS':
        return '', 204
    if not capture_status.get("is_active"):
        return jsonify({"status": "error", "message": "No scan in progress"}), 400
    if not capture_status.get("waiting_for_flip"):
        return jsonify({"status": "noop", "message": "Not currently waiting for flip"})
    # Clear the flip flag — capture_worker checks this each loop iteration
    capture_status["waiting_for_flip"] = False
    capture_status["flip_timer_start_ts"] = None
    logging.info("[CMD] Flip confirmed by user via /confirm-flip")
    return jsonify({"status": "success", "message": "Flip confirmed — scanning reverse"})

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

@app.route('/frame', methods=['GET'])
def live_frame():
    """Returns the latest annotated camera frame as JPEG.
    Flutter polls this ~300ms to show live preview during scanning."""
    from flask import Response
    with _frame_lock:
        data = _latest_frame_jpg
    if not data:
        return Response(status=204)  # No content — not scanning yet
    return Response(data, mimetype='image/jpeg',
                    headers={'Cache-Control': 'no-cache, no-store'})

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
    
    snapshot["paired_email"] = USER_EMAIL

    return jsonify(snapshot)

@app.route('/pair', methods=['POST', 'OPTIONS'])
def pair_agent_route():
    if request.method == 'OPTIONS':
        return '', 204
    data = request.json or {}
    email = data.get("email")
    if email:
        set_user_email(email)
        return jsonify({"status": "success", "paired_email": email})
    return jsonify({"status": "error", "message": "Email not provided"}), 400

@app.route('/list-cameras', methods=['GET'])
def list_cameras_route():
    available = []
    for idx in range(5):
        if active_camera_idx == idx:
            available.append(idx)
            continue
        temp = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if temp.isOpened():
            ret, _ = temp.read()
            if ret:
                available.append(idx)
        temp.release()
    return jsonify({"cameras": available, "active": active_camera_idx})

@app.route('/set-camera', methods=['POST', 'OPTIONS'])
def set_camera_route():
    if request.method == 'OPTIONS':
        return '', 204
    data = request.json or {}
    idx = data.get("index")
    if idx is None:
        return jsonify({"status": "error", "message": "Index not provided"}), 400
    
    global preferred_camera_idx
    preferred_camera_idx = int(idx)
    logging.info(f"[CMD] Preferred camera index set to {preferred_camera_idx}")
    return jsonify({"status": "success", "active": preferred_camera_idx})

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
    logging.info("  Flask status server  -> https://localhost:5000")
    if USER_EMAIL:
        logging.info("  Firestore commands   -> commands/%s/pending", USER_EMAIL)
    else:
        logging.info("  Firestore commands   -> Waiting for pairing...")
    logging.info("="*55)

    # Start idle preview worker so the Flutter app shows the camera feed
    # immediately, before the user presses Start Scan.
    _preview_thread = threading.Thread(
        target=_idle_preview_worker, daemon=True, name="IdlePreview"
    )
    _preview_thread.start()
    logging.info("[PREVIEW] Idle preview thread launched.")

    # Start Firestore command watcher (non-blocking — runs on SDK background thread)
    if USER_EMAIL:
        _watcher = start_command_watcher()

    # Load SSL cert so Chrome (HTTPS page) can reach this local server.
    # Flutter's hardware_service.dart calls https://localhost:5000 — the server
    # MUST be HTTPS or Chrome sends TLS handshakes that crash a plain HTTP server.
    import ssl as _ssl
    _here = os.path.dirname(os.path.abspath(__file__))
    _cert = os.path.join(_here, 'localhost.crt')
    _key  = os.path.join(_here, 'localhost.key')
    if os.path.exists(_cert) and os.path.exists(_key):
        _ctx = _ssl.SSLContext(_ssl.PROTOCOL_TLS_SERVER)
        _ctx.load_cert_chain(_cert, _key)
        logging.info("SSL cert loaded — serving HTTPS on port 5000")
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, ssl_context=_ctx)
    else:
        logging.warning("No SSL cert found — falling back to plain HTTP.")
        logging.warning("Run:  python gen_cert.py  to fix this.")
        logging.warning("Then trust the cert: visit https://localhost:5000 in Chrome and click Proceed.")
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

