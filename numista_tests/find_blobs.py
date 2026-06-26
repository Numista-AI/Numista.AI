import cv2
import numpy as np

img = cv2.imread('C:/Users/ericd/.gemini/antigravity/brain/408674cb-50e1-4a19-b1b5-e36e157db358/microscope_scanner_diagnostics.png')
h, w, c = img.shape
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def print_blobs(name, mask):
    # Find contours of the mask
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"--- Blobs for {name} ---")
    for i, ctr in enumerate(contours):
        area = cv2.contourArea(ctr)
        if area > 100: # filter noise
            x, y, w_box, h_box = cv2.boundingRect(ctr)
            print(f"Blob {i}: x={x}, y={y}, width={w_box}, height={h_box}, area={area}, center=({x + w_box//2}, {y + h_box//2})")

# Blue colors (Sign In buttons, etc.)
# Blue is around R: 20-30, G: 100-110, B: 200 (or similar)
# Let's use a broad mask for blue: R < 80, G < 150, B > 150
blue_mask = (img_rgb[:, :, 0] < 80) & (img_rgb[:, :, 1] < 150) & (img_rgb[:, :, 2] > 150)
print_blobs("Blue", blue_mask)

# Orange color (Free Scan Preview button)
orange_mask = (img_rgb[:, :, 0] > 200) & (img_rgb[:, :, 1] > 120) & (img_rgb[:, :, 1] < 185) & (img_rgb[:, :, 2] < 50)
print_blobs("Orange", orange_mask)

# Teal colors (Try It Free button)
# Teal is around R: 10-20, G: 140-160, B: 125-145 (or similar)
# Let's search broadly: R < 60, G > 110, B > 110
teal_mask = (img_rgb[:, :, 0] < 60) & (img_rgb[:, :, 1] > 110) & (img_rgb[:, :, 2] > 110)
print_blobs("Teal/Green", teal_mask)
