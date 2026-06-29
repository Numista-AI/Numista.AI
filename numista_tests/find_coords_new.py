import cv2
import numpy as np

img = cv2.imread('c:/Users/ericd/Documents/MyVertexProject/numista_tests/demo_new.png')
if img is None:
    print("Error: Could not read image file!")
    exit(1)

h, w, c = img.shape
print(f"Image dimensions: {w}x{h}")

sidebar = img[:, 0:200]
gray = cv2.cvtColor(sidebar, cv2.COLOR_BGR2GRAY)
print(f"Gray min: {np.min(gray)}, max: {np.max(gray)}, mean: {np.mean(gray)}")

# Let's find rows where max pixel in that row is > some threshold
row_maxes = np.max(gray, axis=1)
row_indices = np.where(row_maxes > 30)[0]
print(f"Number of rows with max > 30: {len(row_indices)}")

# Group contiguous rows
in_blob = False
start_y = 0
blobs = []
for y in range(h):
    if row_maxes[y] > 30:
        if not in_blob:
            in_blob = True
            start_y = y
    else:
        if in_blob:
            in_blob = False
            blobs.append((start_y, y - 1))

print("Detected sidebar blobs:")
for i, (sy, ey) in enumerate(blobs):
    center_y = (sy + ey) // 2
    height = ey - sy + 1
    # print average horizontal profile of this blob to check width/density
    blob_gray = gray[sy:ey+1, :]
    col_sums = np.sum(blob_gray, axis=0)
    leftmost = np.where(col_sums > 0)[0]
    if len(leftmost) > 0:
        start_x = leftmost[0]
        end_x = leftmost[-1]
    else:
        start_x = 0
        end_x = 0
    print(f"Blob {i}: y={sy} to {ey}, center_y={center_y}, height={height}, x_range={start_x} to {end_x}")
