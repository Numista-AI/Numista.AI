# Auto-Capture Python Logic

## Proposed Changes

### Auto-Capture Script
#### [NEW] auto_capture.py

Create a standalone Python script to handle the USB microscope camera feed and automatically capture images of coins when in focus and stable.

1. **Camera Initialization**:
   - Loop through indices `0, 1, 2` to find the active camera (`cv2.VideoCapture`).
   - Throw an error or exit gracefully if no camera is found.
2. **Sharpness Calculation (Laplacian Variance)**:
   - Convert video frames to grayscale.
   - Calculate the variance of the Laplacian: `cv2.Laplacian(gray, cv2.CV_64F).var()`.
   - Use this as a "Sharpness Score".
3. **Peak Detection**:
   - Maintain a rolling window or a recent historical maximum of the Sharpness Score.
   - If the current score is within a certain margin (e.g., 90-95%) of the historical maximum, we consider the image "in focus".
4. **Stability Detection (Noise Reduction)**:
   - Apply a **Gaussian Blur** to the grayscale frames before calculating the difference (`cv2.absdiff`).
   - This prevents pixel-level sensor noise/grain (common in digital microscopes) from being detected as movement.
   - Implement a **Stability Counter**: Require the motion score to be low for multiple consecutive frames (e.g., 5 frames) before triggering a capture.
5. **Dual-Side Capture Sequence (with Robust Transitions)**:
   - **Min Sharpness Floor (2000)**: Prevents accidental triggers from hands.
   - **Stability Confirmation Buffer**: Ensures stillness for ~0.5s before saving.
   - **Step 1 (Obverse)**: Capture `obverse_peak.jpg`.
   - **Step 2 (Flip Detection)**: Prompt "Flip Coin". Transition to Step 3 if sharpness drops below **60%** of peak OR after a **5-second timeout**.
   - **Step 3 (Reverse)**: Capture `reverse_peak.jpg`. Automatically finish and report.
6. **AI Integration & JSON Rename Workflow**:
   - **JSON Prompt Update**: Refactor [identify_coin.py](file:///c:/Users/ericd/Documents/MyVertexProject/AJ%27s%20AI%20Coin%20Collection%20app/identify_coin.py) to request a JSON response from Gemini, including a `file_slug` (e.g., `1999D-NJ-Quarter`).
   - **Timestamp Integration**: Use `time.strftime("%Y%m%d_%H%M")` to generate unique timestamps.
   - **Automated Renaming**: [auto_capture.py](file:///c:/Users/ericd/Documents/MyVertexProject/AJ%27s%20AI%20Coin%20Collection%20app/auto_capture.py) will use the returned `file_slug` to rename the `obverse_peak.jpg` and `reverse_peak.jpg` to `[slug]_Obverse_[timestamp].jpg` and `[slug]_Reverse_[timestamp].jpg`.
   - **Hardware Error Handling**: Add specific checks for Camera Index 1 (Jiusion Microscope) to handle accidental disconnects.
7. **Session Polish**:
   - **Clean Exit**: Window closes immediately after the final capture. 
   - **Report Output**: Display the AI report cleanly in the terminal.

## Verification Plan

### Automated/Manual Testing
- The script relies on a physical camera and manual wheel turning.
- Verification will be manual: The user will run `python auto_capture.py` locally.
- The user will adjust the microscope focus wheel.
- We will verify that:
  - The Focus Meter overlay updates in real-time.
  - An image is saved to `captures/` automatically when the image becomes sharp and stable.
  - Camera connection handles fallback gracefully.
