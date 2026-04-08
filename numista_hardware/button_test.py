import cv2
import numpy as np
import os

# Calibrated for your LED-lit peak of 2300+
SNAP_THRESHOLD = 2100 

def calculate_sharpness(image):
    # Core Laplacian Variance calculation - The industry standard for peak detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def run_focus_capture():
    # Use index 1 (your verified Jiusion USB microscope)
    cap = cv2.VideoCapture(1) 
    stable_count = 0
    
    print(f"Numista.AI: High-Res Focus Mode Active.")
    print(f"Targeting: {SNAP_THRESHOLD}+ for peak clarity.")

    while True:
        ret, frame = cap.read()
        if not ret: break

        score = calculate_sharpness(frame)
        
        # UI Feedback: Visual "Focus Meter"
        # Green if ready for capture, Red if focusing
        color = (0, 255, 0) if score > SNAP_THRESHOLD else (0, 0, 255)
        cv2.putText(frame, f"Sharpness: {int(score)}", (10, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Automatic Snap Logic: Triggers only when peak clarity is met and stable
        if score > SNAP_THRESHOLD:
            stable_count += 1
            # Wait for 10 stable frames to ensure hands are off the wheel
            if stable_count > 10:
                if not os.path.exists('captures'): os.makedirs('captures')
                
                # We save this as the 'reverse_peak.jpg' for our AI script
                file_path = "captures/reverse_peak.jpg"
                cv2.imwrite(file_path, frame)
                
                print(f"--- PEAK CLARITY REACHED: {int(score)} ---")
                print(f"Image saved as: {file_path}")
                break 
        else:
            stable_count = 0

        cv2.imshow('Numista.AI - Focus Meter (Press Q to quit)', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()
    print("Microscope closed. Ready for AI Analysis.")

if __name__ == "__main__":
    run_focus_capture()