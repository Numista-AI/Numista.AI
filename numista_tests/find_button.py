import cv2
import numpy as np

img = cv2.imread('C:/Users/ericd/.gemini/antigravity/brain/408674cb-50e1-4a19-b1b5-e36e157db358/microscope_scanner_diagnostics.png')
h, w, c = img.shape
print(f"Image shape: {w}x{h}")

# Convert to RGB for easier color comparison
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Search for the orange button "Free Scan Preview"
# Orange is around R:240, G:150, B:10. Let's find pixels matching this.
orange_mask = (img_rgb[:, :, 0] > 200) & (img_rgb[:, :, 1] > 120) & (img_rgb[:, :, 1] < 180) & (img_rgb[:, :, 2] < 50)
orange_y, orange_x = np.where(orange_mask)
if len(orange_x) > 0:
    print(f"Orange button found at approx x: {int(np.mean(orange_x))}, y: {int(np.mean(orange_y))}")

# Search for the teal button "Try It Free"
# Teal is around R:10-20, G:140-160, B:125-145 (or similar). Let's use a mask.
teal_mask = (img_rgb[:, :, 0] < 50) & (img_rgb[:, :, 1] > 100) & (img_rgb[:, :, 2] > 100)
teal_y, teal_x = np.where(teal_mask)
if len(teal_x) > 0:
    print(f"Teal button found at approx x: {int(np.mean(teal_x))}, y: {int(np.mean(teal_y))}")

# Let's print some pixels around x=680, y=936 (wait, y cannot be 936 in 720 height, so y is likely around 631)
# Let's inspect the area from x=550 to x=800, and y=600 to y=700
# We can find where the white button "Browse Demo" with grey border is.
# It should be to the left of the Teal button.
if len(teal_x) > 0:
    teal_center_x = int(np.mean(teal_x))
    teal_center_y = int(np.mean(teal_y))
    # Browse Demo is to the left of Try It Free. In the HTML:
    # <Browse Demo button> <Try It Free button>
    # Let's look at the region to the left of teal button: x between teal_center_x - 250 and teal_center_x - 50
    # and y around teal_center_y.
    print(f"Searching for 'Browse Demo' button left of teal button (x: {teal_center_x - 250} to {teal_center_x - 50}, y: {teal_center_y - 25} to {teal_center_y + 25})...")
    # Let's find white-ish pixels (R>240, G>240, B>240) in this region
    region = img_rgb[teal_center_y - 25:teal_center_y + 25, teal_center_x - 250:teal_center_x - 50]
    white_mask = (region[:, :, 0] > 240) & (region[:, :, 1] > 240) & (region[:, :, 2] > 240)
    white_y, white_x = np.where(white_mask)
    if len(white_x) > 0:
         approx_x = teal_center_x - 250 + int(np.mean(white_x))
         approx_y = teal_center_y - 25 + int(np.mean(white_y))
         print(f"Browse Demo button found at approx x: {approx_x}, y: {approx_y}")
