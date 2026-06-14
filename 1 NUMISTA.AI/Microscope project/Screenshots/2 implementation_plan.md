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
5. **Dual-Side Capture Sequence**:
   - Introduce a workflow state: `OBVERSE` (Side 1) -> `REVERSE` (Side 2) -> `COMPLETE`.
   - **Step 1 (Obverse)**: Guide user to focus and stabilize on Side 1. Capture as `obverse_peak.jpg`.
   - **Step 2 (Prompt)**: Visually prompt the user with a message: "OBVERSE SAVED! Flip coin to Side 2 and refocus."
   - **Step 3 (Reverse)**: Once the user refocuses and stabilizes on Side 2, capture as `reverse_peak.jpg`.
6. **AI Integration (Hand-off)**:
   - Once both images are saved, automatically trigger the [identify_coin.py](file:///c:/Users/ericd/Documents/MyVertexProject/AJ%27s%20AI%20Coin%20Collection%20app/identify_coin.py) logic.
   - We will need to slightly modify [identify_coin.py](file:///c:/Users/ericd/Documents/MyVertexProject/AJ%27s%20AI%20Coin%20Collection%20app/identify_coin.py) to accept these specific filenames as inputs.
7. **Improved Visual UX (Feedback)**:
   - Status bar will clearly state "STEP 1: OBVERSE" or "STEP 2: REVERSE".
   - Success flash and "Flip Coin" message for transition.

## Verification Plan

### Automated/Manual Testing
- The script relies on a physical camera and manual wheel turning.
- Verification will be manual: The user will run `python auto_capture.py` locally.
- The user will adjust the microscope focus wheel.
- We will verify that:
  - The Focus Meter overlay updates in real-time.
  - An image is saved to `captures/` automatically when the image becomes sharp and stable.
  - Camera connection handles fallback gracefully.
