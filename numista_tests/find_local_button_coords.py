import cv2
import numpy as np

img = cv2.imread('c:/Users/ericd/Documents/MyVertexProject/numista_tests/demo_new.png')
if img is None:
    print("Error: Could not read image!")
    exit(1)

h, w, c = img.shape
print(f"Image shape: {w}x{h}")

img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Search for the orange button "Free Scan Preview"
orange_mask = (img_rgb[:, :, 0] > 200) & (img_rgb[:, :, 1] > 120) & (img_rgb[:, :, 1] < 180) & (img_rgb[:, :, 2] < 50)
orange_y, orange_x = np.where(orange_mask)
if len(orange_x) > 0:
    print(f"Orange button found at approx x: {int(np.mean(orange_x))}, y: {int(np.mean(orange_y))}")

# Search for the teal button "Try It Free"
teal_mask = (img_rgb[:, :, 0] < 50) & (img_rgb[:, :, 1] > 100) & (img_rgb[:, :, 2] > 100)
teal_y, teal_x = np.where(teal_mask)
if len(teal_x) > 0:
    teal_center_x = int(np.mean(teal_x))
    teal_center_y = int(np.mean(teal_y))
    print(f"Teal button found at approx x: {teal_center_x}, y: {teal_center_y}")
    
    # Search for the white button "Browse Demo" to the left of the Teal button
    print(f"Searching for 'Browse Demo' button left of teal button (x: {teal_center_x - 250} to {teal_center_x - 50}, y: {teal_center_y - 25} to {teal_center_y + 25})...")
    region = img_rgb[teal_center_y - 25:teal_center_y + 25, teal_center_x - 250:teal_center_x - 50]
    white_mask = (region[:, :, 0] > 240) & (region[:, :, 1] > 240) & (region[:, :, 2] > 240)
    white_y, white_x = np.where(white_mask)
    if len(white_x) > 0:
         approx_x = teal_center_x - 250 + int(np.mean(white_x))
         approx_y = teal_center_y - 25 + int(np.mean(white_y))
         print(f"Browse Demo button found at approx x: {approx_x}, y: {approx_y}")
    else:
         print("Browse Demo button not found using white mask.")
else:
    print("Teal button not found.")
