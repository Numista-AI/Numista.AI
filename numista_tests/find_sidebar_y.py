import cv2
import numpy as np

img = cv2.imread('C:/Users/ericd/.gemini/antigravity/brain/408674cb-50e1-4a19-b1b5-e36e157db358/after_demo_click.png')
h, w, c = img.shape

# Sidebar is on the left: x from 0 to 160.
sidebar = img[:, 0:160]

# Convert to grayscale
gray = cv2.cvtColor(sidebar, cv2.COLOR_BGR2GRAY)

# Lower threshold to find dimmer grey text/icons
_, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)

# Sum along rows to find vertical density of bright pixels
row_sums = np.sum(thresh, axis=1)

in_blob = False
start_y = 0
blobs = []
for y in range(h):
    if row_sums[y] > 100: # threshold for pixel count in row
        if not in_blob:
            in_blob = True
            start_y = y
    else:
        if in_blob:
            in_blob = False
            blobs.append((start_y, y - 1))

print("Detected sidebar blobs with threshold 80:")
for i, (sy, ey) in enumerate(blobs):
    center_y = (sy + ey) // 2
    print(f"Blob {i}: y={sy} to {ey}, center_y={center_y}, height={ey-sy+1}")
