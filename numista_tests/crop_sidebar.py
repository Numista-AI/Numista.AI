import cv2

img = cv2.imread('C:/Users/ericd/.gemini/antigravity/brain/408674cb-50e1-4a19-b1b5-e36e157db358/microscope_scanner_result.png')
# Crop sidebar menu region
sidebar_menu = img[180:720, 0:160]

output_path = 'C:/Users/ericd/.gemini/antigravity/brain/408674cb-50e1-4a19-b1b5-e36e157db358/cropped_sidebar.png'
cv2.imwrite(output_path, sidebar_menu)
print(f"Cropped sidebar saved to: {output_path}")
