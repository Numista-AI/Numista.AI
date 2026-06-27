# Microscope Scanner Stability & Gemini Parsing Fixes

This implementation plan addresses two critical failures observed during the live scan test on June 27:
1. **Gemini JSON Output Corruption:** The AI vision model generated an infinite repetition loop (`"Denver)."` repeatedly) inside the `report` field, truncating the response mid-stream and causing all parsed coin details to return blank.
2. **Camera Viewfinder Freezing & Capture Mismatches:** The web UI stream froze during camera handoff, and timing/buffer issues resulted in the obverse side capture sequence being skipped or capturing duplicate reverse-side images.

## Proposed Changes

### 1. Hardening Gemini API Output Contracts

#### [MODIFY] [identify_coin.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_hardware/identify_coin.py)
* **Define Pydantic Schemas:** Create explicit `Pass1CoinData` and `Pass2VerificationData` models using Pydantic.
* **Structured Response Config:** Update the Google GenAI SDK configuration to pass `response_schema` in the `GenerateContentConfig`.
* **Configure Low Temperature:** Set `temperature=0.2` to prioritize deterministic and structured token output, reducing model hallucination/looping.
* **Add Robust JSON Repair Parser:** Implement `safe_parse_json()` that:
  - Detects repeating suffix loops (e.g. `Denver).`) and prunes them dynamically.
  - Automatically scans for and closes unclosed quotes, brackets, and braces.
  - Recovers valid fields even if the response was truncated mid-stream.

### 2. Eliminating Handoff Freezes & Aligning State Timers

#### [MODIFY] [auto_capture.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_hardware/auto_capture.py)
* **Viewfinder Warm-Up Updates:** Update the camera warm-up loop to feed frames directly into the web UI viewfinder queue (`_latest_frame_jpg`) so the interface does not appear frozen during initialization.
* **OpenCV Release Cushion:** Increase the thread cushion from `0.5s` to `1.5s` after the idle preview thread stops to give the USB controller/DirectShow driver time to free the device resource before the capture worker re-opens it.
* **Microscope Scan Resolution Optimization:** Set the microscope scan resolution to `1280x720` (matching the preview resolution) to prevent USB mode/buffer switching and crashes on standard USB microscopes.
* **Align State Machine Timers:** Change `FLIP_LOCKOUT_SECS` to `5.0` seconds to match the UI visual countdown timer.
* **Prevent CPU Starvation:** Add a short `time.sleep(0.01)` at the bottom of the active frame loop to yield CPU cycles and ensure smooth background server performance.

---

## Verification Plan

### Automated Tests
* Run `python test_gemini_response.py` to verify the full Gemini identification pipeline.
* Execute a script test using simulated scanner state inputs to confirm structured schemas parse correctly.

### Manual Verification
* Build and package the agent executable (`./build_agent.ps1`).
* Deploy the updated agent locally (`./install_agent.ps1`).
* Launch the agent and test the microscope scan flow via the web browser.
* Verify the live viewfinder doesn't freeze, and the obverse / reverse captures align perfectly.
