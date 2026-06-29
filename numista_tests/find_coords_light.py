import cv2
import numpy as np

img = cv2.imread('c:/Users/ericd/Documents/MyVertexProject/numista_tests/demo_new.png')
if img is None:
    print("Error: Could not read image!")
    exit(1)

h, w, c = img.shape
sidebar = img[:, 0:200]
gray = cv2.cvtColor(sidebar, cv2.COLOR_BGR2GRAY)

# Look for dark pixels (text/icons) on bright background
dark_pixels = gray < 200

# Sum along rows to find vertical density of dark pixels
row_sums = np.sum(dark_pixels, axis=1)

in_blob = False
start_y = 0
blobs = []
for y in range(h):
    if row_sums[y] > 50: # Threshold for dark pixels in a row
        if not in_blob:
            in_blob = True
            start_y = y
    else:
        if in_blob:
            in_blob = False
            blobs.append((start_y, y - 1))

print("Detected sidebar blobs (dark pixels on light background):")
for i, (sy, ey) in enumerate(blobs):
    center_y = (sy + ey) // 2
    height = ey - sy + 1
    # print details
    print(f"Blob {i}: y={sy} to {ey}, center_y={center_y}, height={height}")
