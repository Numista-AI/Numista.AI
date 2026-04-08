"""
Numista.AI - Camera Diagnostic Tool
Run this BEFORE auto_capture.py to find your microscope's index.
"""
import cv2

print("Scanning for cameras on your system...")
print("=" * 40)

found = []
for idx in range(6):
    for backend_name, backend in [("DSHOW", cv2.CAP_DSHOW), ("MSMF", cv2.CAP_MSMF)]:
        cap = cv2.VideoCapture(idx, backend)
        if cap.isOpened():
            ret, frame = cap.read()
            status = "✅ CAN READ FRAMES" if ret else "⚠️  Opens but NO frames (locked or incompatible)"
            print(f"  Index {idx} [{backend_name}]: {status}")
            found.append(idx)
        cap.release()

print("=" * 40)
if found:
    print(f"Cameras detected at indices: {list(set(found))}")
    print("Your Jiusion microscope is the NON-webcam entry above.")
else:
    print("❌ No cameras found at all. Check USB connection.")
