import cv2
import numpy as np

img = cv2.imread('C:/Users/ericd/.gemini/antigravity/brain/408674cb-50e1-4a19-b1b5-e36e157db358/microscope_scanner_result.png')
h, w, c = img.shape

# Sidebar is on the left: x from 0 to 160.
sidebar = img[:, 0:160]

# Convert to HSV or RGB to look for the highlighted option.
# In Flutter, selected options are typically highlighted with a background color or a side indicator.
# Let's inspect the RGB values of the sidebar rows to find the highlighted background.
# The default sidebar background is dark. Let's find rows that are lighter (highlighted).
row_means = np.mean(sidebar, axis=1)

# Let's print the average color of each row in the menu area (y=150 to y=600)
# to see where the highlight is located.
print("Row average intensities (y=150 to 600):")
for y in range(150, 600, 10):
    chunk = sidebar[y:y+10, :]
    mean_val = np.mean(chunk)
    print(f"y={y}-{y+10}: mean={mean_val:.2f}")
