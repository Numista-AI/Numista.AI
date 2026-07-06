# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
Generates 8 mint mark location template diagrams (one per position type).
Each is a clean line-art coin diagram with labeled arrow.

Types:
  EDGE            - arrow pointing to coin edge (sideways view)
  OBVERSE_PORTRAIT - arrow pointing to portrait area on obverse
  OBVERSE_DATE    - arrow pointing to area near date on obverse
  REVERSE_EAGLE   - arrow pointing to eagle's tail/wing on reverse
  REVERSE_LOWER   - arrow pointing to lower reverse area
  REVERSE_UPPER   - arrow pointing to upper reverse (dome/bell)
  MIXED           - split diagram showing two positions with era labels
  NONE            - no mint mark exists (transition years)
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'numista_mobile', 'assets', 'mint_mark_diagrams')
os.makedirs(OUT_DIR, exist_ok=True)

# ── Styling ───────────────────────────────────────────────────────────────────
W, H = 420, 200
BG = (255, 255, 255, 0)
COIN_FILL   = (245, 235, 195, 255)   # warm gold
COIN_EDGE   = (180, 140, 30, 255)
DOT_FILL    = (220, 30, 30, 255)     # red for mint mark location
ARROW_CLR   = (220, 30, 30, 255)
TEXT_CLR    = (50, 50, 50, 255)
LABEL_CLR   = (180, 140, 30, 255)

def get_font(size=14):
    for name in ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try: return ImageFont.truetype(name, size)
        except: pass
    return ImageFont.load_default()

def draw_coin(d, cx, cy, r, label="OBVERSE"):
    """Draw a coin circle with a center label."""
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=COIN_FILL, outline=COIN_EDGE, width=3)
    # Subtle inner ring
    d.ellipse([cx-r+6, cy-r+6, cx+r-6, cy+r-6], outline=(200,160,50,180), width=1)
    f = get_font(10)
    d.text((cx, cy+r-18), label, fill=LABEL_CLR, font=f, anchor="mm")

def draw_arrow(d, x1, y1, x2, y2):
    """Draw an arrow from (x1,y1) pointing TO (x2,y2)."""
    d.line([(x1,y1),(x2,y2)], fill=ARROW_CLR, width=3)
    # Arrowhead
    angle = math.atan2(y2-y1, x2-x1)
    size = 10
    p1 = (x2 - size*math.cos(angle-0.4), y2 - size*math.sin(angle-0.4))
    p2 = (x2 - size*math.cos(angle+0.4), y2 - size*math.sin(angle+0.4))
    d.polygon([x2,y2, p1[0],p1[1], p2[0],p2[1]], fill=ARROW_CLR)

def draw_dot(d, x, y, r=7):
    d.ellipse([x-r, y-r, x+r, y+r], fill=DOT_FILL, outline=(160,0,0,255), width=2)

def new_img():
    img = Image.new('RGBA', (W, H), BG)
    return img, ImageDraw.Draw(img)

def save(img, name):
    path = os.path.join(OUT_DIR, f"{name}.png")
    img.save(path)
    print(f"  Saved: {name}.png")
    return path

# ── EDGE ─────────────────────────────────────────────────────────────────────
img, d = new_img()
# Draw coin side view (thin rectangle = edge of coin)
d.rectangle([200, 75, 380, 105], fill=COIN_FILL, outline=COIN_EDGE, width=3)
# "S  2018" label inside edge
f = get_font(20)
d.text((215, 80), "S    •    2018", fill=(140,100,20,255), font=f)
# Arrow from left
draw_arrow(d, 10, 90, 198, 90)
# Label
f2 = get_font(12)
d.text((10, 10), "Look along the EDGE (side) of the coin.", fill=TEXT_CLR, font=f2)
d.text((10, 28), "The mint mark is a small letter", fill=TEXT_CLR, font=f2)
d.text((10, 44), "between the date and the design.", fill=TEXT_CLR, font=f2)
save(img, "EDGE")

# ── OBVERSE_PORTRAIT ─────────────────────────────────────────────────────────
img, d = new_img()
cx, cy, r = 100, 100, 80
draw_coin(d, cx, cy, r, "OBVERSE")
# Portrait area: roughly left-center
draw_dot(d, cx+25, cy+15)   # near neckline
draw_arrow(d, 280, 100, cx+32, cy+15)
f2 = get_font(12)
d.text((220, 50), "Look on the FRONT (obverse)", fill=TEXT_CLR, font=f2)
d.text((220, 68), "of the coin. The mint mark", fill=TEXT_CLR, font=f2)
d.text((220, 86), "is a small letter near the", fill=TEXT_CLR, font=f2)
d.text((220, 104), "portrait's neckline or", fill=TEXT_CLR, font=f2)
d.text((220, 122), "lower portrait area.", fill=TEXT_CLR, font=f2)
save(img, "OBVERSE_PORTRAIT")

# ── OBVERSE_DATE ─────────────────────────────────────────────────────────────
img, d = new_img()
cx, cy, r = 100, 100, 80
draw_coin(d, cx, cy, r, "OBVERSE")
# Near date: lower right quadrant
draw_dot(d, cx+45, cy+45)
draw_arrow(d, 280, 100, cx+45+5, cy+45-5)
f2 = get_font(12)
d.text((220, 50), "Look on the FRONT (obverse)", fill=TEXT_CLR, font=f2)
d.text((220, 68), "of the coin. The mint mark", fill=TEXT_CLR, font=f2)
d.text((220, 86), "is a small letter just to the", fill=TEXT_CLR, font=f2)
d.text((220, 104), "right of or below the date.", fill=TEXT_CLR, font=f2)
save(img, "OBVERSE_DATE")

# ── REVERSE_EAGLE ────────────────────────────────────────────────────────────
img, d = new_img()
cx, cy, r = 100, 100, 80
draw_coin(d, cx, cy, r, "REVERSE")
# Eagle tail: lower left quadrant
draw_dot(d, cx-35, cy+40)
draw_arrow(d, 280, 100, cx-35+8, cy+40-5)
f2 = get_font(12)
d.text((220, 50), "Look on the BACK (reverse)", fill=TEXT_CLR, font=f2)
d.text((220, 68), "of the coin. The mint mark", fill=TEXT_CLR, font=f2)
d.text((220, 86), "is a small letter to the left", fill=TEXT_CLR, font=f2)
d.text((220, 104), "of the eagle's tail or wing.", fill=TEXT_CLR, font=f2)
save(img, "REVERSE_EAGLE")

# ── REVERSE_LOWER ────────────────────────────────────────────────────────────
img, d = new_img()
cx, cy, r = 100, 100, 80
draw_coin(d, cx, cy, r, "REVERSE")
# Lower center/left
draw_dot(d, cx-20, cy+50)
draw_arrow(d, 280, 100, cx-20+8, cy+50-5)
f2 = get_font(12)
d.text((220, 50), "Look on the BACK (reverse)", fill=TEXT_CLR, font=f2)
d.text((220, 68), "of the coin. The mint mark", fill=TEXT_CLR, font=f2)
d.text((220, 86), "is a small letter in the", fill=TEXT_CLR, font=f2)
d.text((220, 104), "lower portion of the reverse.", fill=TEXT_CLR, font=f2)
save(img, "REVERSE_LOWER")

# ── REVERSE_UPPER ────────────────────────────────────────────────────────────
img, d = new_img()
cx, cy, r = 100, 100, 80
draw_coin(d, cx, cy, r, "REVERSE")
# Upper center
draw_dot(d, cx, cy-40)
draw_arrow(d, 280, 80, cx+5, cy-40+5)
f2 = get_font(12)
d.text((220, 50), "Look on the BACK (reverse)", fill=TEXT_CLR, font=f2)
d.text((220, 68), "of the coin. The mint mark", fill=TEXT_CLR, font=f2)
d.text((220, 86), "is a small letter in the", fill=TEXT_CLR, font=f2)
d.text((220, 104), "upper portion of the reverse", fill=TEXT_CLR, font=f2)
d.text((220, 122), "(above main design).", fill=TEXT_CLR, font=f2)
save(img, "REVERSE_UPPER")

# ── MIXED ────────────────────────────────────────────────────────────────────
# Two mini coins side by side with era labels
img, d = new_img()
# Left coin (earlier era = reverse)
cx1, cy1, r1 = 75, 100, 60
draw_coin(d, cx1, cy1, r1, "REVERSE")
draw_dot(d, cx1-25, cy1+30)
f2 = get_font(10)
d.text((cx1, cy1-r1-12), "Earlier era:", fill=TEXT_CLR, font=f2, anchor="mm")
# Right coin (later era = obverse)
cx2, cy2, r2 = 240, 100, 60
draw_coin(d, cx2, cy2, r2, "OBVERSE")
draw_dot(d, cx2+18, cy2+10)
d.text((cx2, cy2-r2-12), "Later era:", fill=TEXT_CLR, font=f2, anchor="mm")
# Arrow keys
draw_arrow(d, cx1-25-20, cy1+30, cx1-25-5, cy1+30)
draw_arrow(d, cx2+18+20, cy2+10, cx2+18+5, cy2+10)
f3 = get_font(11)
d.text((W//2, H-12), "Location changed between eras — see description above.", 
       fill=TEXT_CLR, font=f3, anchor="mm")
save(img, "MIXED")

# ── NONE ─────────────────────────────────────────────────────────────────────
img, d = new_img()
cx, cy, r = 100, 100, 80
draw_coin(d, cx, cy, r, "OBVERSE")
# Red X overlay
d.line([cx-30, cy-30, cx+30, cy+30], fill=(220,30,30,255), width=4)
d.line([cx+30, cy-30, cx-30, cy+30], fill=(220,30,30,255), width=4)
f2 = get_font(12)
d.text((220, 50), "No mint mark exists on", fill=TEXT_CLR, font=f2)
d.text((220, 68), "coins of this type/era.", fill=TEXT_CLR, font=f2)
d.text((220, 92), "All coins were struck at", fill=TEXT_CLR, font=f2)
d.text((220, 110), "Philadelphia (no mark).", fill=TEXT_CLR, font=f2)
save(img, "NONE")

print(f"\nAll 8 diagrams saved to: {OUT_DIR}")
