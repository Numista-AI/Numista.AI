import cv2
import numpy as np

img = cv2.imread('C:/Users/ericd/.gemini/antigravity/brain/408674cb-50e1-4a19-b1b5-e36e157db358/microscope_scanner_result.png')
h, w, c = img.shape

# Sidebar is on the left: x from 0 to 160.
# Let's check a column of the background, say at x = 10 (where there is no text or icon)
# and print the RGB values for each row y.
background_col = img[:, 10, :]

# Print any rows where the background is significantly lighter than the base background.
# The base background is the most common color in this column.
colors, counts = np.unique(background_col, axis=0, return_counts=True)
base_bg = colors[np.argmax(counts)]
print(f"Base background color of sidebar: {base_bg}")

print("Rows with different background colors (potential highlights):")
y = 0
while y < h:
    color = background_col[y]
    # Check if the color differs from the base background
    diff = np.abs(color.astype(int) - base_bg.astype(int))
    if np.max(diff) > 5:
        # Find how long this color persists
        start_y = y
        while y < h and np.max(np.abs(background_col[y].astype(int) - base_bg.astype(int))) > 5:
            y += 1
        print(f"Highlight found: y={start_y} to {y-1}, height={y - start_y}, color={background_col[start_y]}")
    else:
        y += 1
