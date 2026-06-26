import cv2
import numpy as np

img = cv2.imread('C:/Users/ericd/.gemini/antigravity/brain/408674cb-50e1-4a19-b1b5-e36e157db358/cropped_sidebar.png')
h, w, c = img.shape
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Find rows containing text or icons by checking row brightness
_, thresh = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY)
row_sums = np.sum(thresh, axis=1)

# Group contiguous rows
in_blob = False
start_y = 0
blobs = []
for y in range(h):
    if row_sums[y] > 50: # Threshold for content
        if not in_blob:
            in_blob = True
            start_y = y
    else:
        if in_blob:
            in_blob = False
            blobs.append((start_y, y - 1))

print("Menu items center-y in cropped sidebar (add 180 for original y):")
items = [
    "Error Library",
    "My Collection",
    "Review Hub",
    "Coin Programs",
    "Add New Coins",
    "World & Specialty",
    "Microscope Scanner",
    "Inventory",
    "My Wishlist",
    "Estate Planning",
    "Coin Search",
    "AI Deepdive",
    "AI Trainer Board",
    "Settings & Backup"
]

for i, (sy, ey) in enumerate(blobs):
    center_y = (sy + ey) // 2
    orig_y = center_y + 180
    label = items[i] if i < len(items) else f"Unknown item {i}"
    print(f"{label:<22} -- Crop Y: {center_y:<3} -- Original Y: {orig_y}")
