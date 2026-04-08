import os
import cv2
import shutil
from datetime import datetime
from identify_coin import run_numista_report

# --- CONFIGURATION ---
MAIN_DIR = r"C:\Users\ericd\Documents\MyVertexProject\AJ's AI Coin Collection app"
CAPTURES_DIR = os.path.join(MAIN_DIR, "captures")
VERIFIED_DIR = os.path.join(MAIN_DIR, "verified_images")
CAMERA_INDEX = 1 # Change to 1 or 2 if it opens your laptop webcam instead

def capture_live_coin():
    os.makedirs(CAPTURES_DIR, exist_ok=True)
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    if not cap.isOpened():
        print("❌ Error: Could not find Razer Kiyo.")
        return False

    print("📸 Kiyo Online. Center the coin. Press SPACE to Capture & Auto-Crop.")
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # Display the live feed
        cv2.imshow("Numista.AI - Auto-Crop Mode", frame)
        
        if cv2.waitKey(1) & 0xFF == ord(' '):
            # --- AUTO-CROP LOGIC ---
            # 1. Convert to Grayscale and Blur to reduce noise
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (7, 7), 0)
            
            # 2. Threshold the image (find the bright coin on dark background)
            _, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)
            
            # 3. Find contours (the outline of the coin)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Get the largest circular-ish object
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Add a small 20-pixel padding so we don't cut the edge of the coin
                padding = 20
                crop = frame[max(0, y-padding):min(frame.shape[0], y+h+padding), 
                             max(0, x-padding):min(frame.shape[1], x+w+padding)]
                
                save_frame = crop
                print("✂️ Auto-Crop Successful!")
            else:
                save_frame = frame
                print("⚠️ No coin detected, saving full frame.")

            obv_path = os.path.join(CAPTURES_DIR, "obverse_peak.jpg")
            cv2.imwrite(obv_path, save_frame)
            break

    cap.release()
    cv2.destroyAllWindows()
    return True

def run_full_scan():
    print("\n--- Numista.AI: Live Hardware-to-Brain Scan ---")
    
    # 1. Physical Capture
    if not capture_live_coin():
        return

    # 2. AI Analysis
    temp_obv = os.path.join(CAPTURES_DIR, "obverse_peak.jpg")
    temp_rev = os.path.join(CAPTURES_DIR, "obverse_peak.jpg") # Using same for test

    print("🧠 Analyzing with Gemini 3 Flash...")
    result = run_numista_report(temp_obv, temp_rev)
    
    if not result:
        print("❌ AI Error: Brain could not process image.")
        return

    slug = result.get('file_slug', 'unknown_coin')
    conf = result.get('confidence_score', 0)
    print(f"\nAI GUESS: {slug} ({conf}% Confidence)")

    # 3. Human Verification & Renaming
    choice = input("Accept (y) / Correct (c): ").lower()
    if choice == 'c':
        slug = input("Enter correct ID: ")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    final_name = f"{slug}_Obverse_{timestamp}.jpg"
    
    os.makedirs(VERIFIED_DIR, exist_ok=True)
    shutil.copy(temp_obv, os.path.join(VERIFIED_DIR, final_name))
    print(f"✨ SUCCESS: Permanently archived as {final_name}")

if __name__ == "__main__":
    run_full_scan()