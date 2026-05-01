from PIL import Image, ImageDraw, ImageFont
import os

width, height = 360, 150
img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
d = ImageDraw.Draw(img)

# Draw a curved rectangle on the RIGHT side of the image
d.rectangle([100, 40, 350, 110], fill=(255, 223, 0, 255), outline=(184, 134, 11, 255), width=3)

try:
    font = ImageFont.truetype("arial.ttf", 36)
except:
    font = ImageFont.load_default()

# The 'S' and '2018' in the gold box
d.text((120, 50), "S          2018", fill=(184, 134, 11, 255), font=font)

# Draw an arrow pointing to the "S" from the LEFT
d.line([(0, 80), (110, 80)], fill="black", width=3)
d.polygon([(110, 80), (95, 70), (95, 90)], fill="black")

out_path = os.path.join(os.path.dirname(__file__), '..', 'numista_mobile', 'assets', 'edge_mint_mark.png')
img.save(out_path)
print("Saved diagram to", out_path)
