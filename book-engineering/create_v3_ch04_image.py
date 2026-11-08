"""Create a compact bilingual position/Transformer-block diagram for chapter 36."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/images/babak-ai/v3-ch04-position-block.webp"
W, H = 1600, 1000
BG = "#0b1220"
CARD = "#111c2e"
LINE = "#334a68"
WHITE = "#f2f6ff"
MUTED = "#bdc9dd"
CYAN = "#55d6e8"
PURPLE = "#b39bff"
GREEN = "#68d6a7"
ORANGE = "#ffc978"
PINK = "#ff8da1"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def font(size, bold=False, mono=False):
    path = MONO if mono else (BOLD if bold else SANS)
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)


def text(draw, xy, value, size=24, color=WHITE, bold=False, direction="rtl", anchor=None, mono=False):
    draw.text(xy, value, font=font(size, bold, mono), fill=color, direction=direction,
              language="fa" if direction == "rtl" else "en", anchor=anchor)


def box(draw, coords, outline=LINE, fill=CARD, radius=22, width=3):
    draw.rounded_rectangle(coords, radius=radius, fill=fill, outline=outline, width=width)


def center(draw, coords, value, size, color=WHITE, bold=False, direction="rtl", mono=False):
    x1, y1, x2, y2 = coords
    f = font(size, bold, mono)
    bounds = draw.textbbox((0, 0), value, font=f, direction=direction,
                           language="fa" if direction == "rtl" else "en")
    tw, th = bounds[2] - bounds[0], bounds[3] - bounds[1]
    draw.text((x1 + (x2-x1-tw)/2, y1 + (y2-y1-th)/2 - bounds[1]), value,
              font=f, fill=color, direction=direction,
              language="fa" if direction == "rtl" else "en")


def arrow(draw, a, b, color=CYAN, width=5):
    draw.line((a, b), fill=color, width=width)
    x1, y1 = a; x2, y2 = b
    sign = 1 if x2 >= x1 else -1
    draw.polygon([(x2, y2), (x2-14*sign, y2-10), (x2-14*sign, y2+10)], fill=color)


im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)
box(d, (40, 32, 1560, 125), outline="#2c4261", fill="#101b2d", radius=28, width=2)
text(d, (1515, 57), "ترتیب را به دنباله بده، مسیر یادگیری را نگه دار", 31, WHITE, True, "rtl", "ra")
text(d, (75, 73), "POSITION  •  RoPE  •  RESIDUAL  •  FFN", 16, CYAN, True, "ltr", "la")

# Two position encodings enter attention in different ways.
box(d, (55, 165, 745, 495), outline=PURPLE)
text(d, (705, 185), "دو راهِ کُدگذاری موقعیت", 28, WHITE, True, "rtl", "ra")
text(d, (88, 225), "A  SINUSOIDAL: جمع با embedding", 18, CYAN, True, "ltr", "la")
center(d, (90, 257, 700, 310), "X + PE(pos)  →  Q, K, V", 25, WHITE, True, "ltr", True)
# A small smooth signal diagram with distinct frequencies.
chart = (105, 328, 420, 455)
d.rounded_rectangle(chart, radius=16, fill="#0d1727", outline="#344964", width=2)
for y in (360, 390, 420):
    d.line((120, y, 405, y), fill="#23364e", width=1)
for color, period, amp, phase in ((CYAN, 110, 24, 0), (ORANGE, 48, 16, 0.7), (PURPLE, 21, 9, 0.3)):
    pts=[]
    import math
    for px in range(0, 281, 2):
        py=392-amp*math.sin(2*math.pi*px/period+phase)
        pts.append((120+px, py))
    d.line(pts, fill=color, width=3)
center(d, (440, 338, 720, 372), "زوج sin/cos", 19, ORANGE, True, "rtl")
center(d, (440, 379, 720, 415), "فرکانس‌های متفاوت", 16, MUTED, False, "rtl")
center(d, (440, 420, 720, 456), "بردارها هم‌بُعدند", 16, GREEN, False, "rtl")

box(d, (855, 165, 1545, 495), outline=ORANGE)
text(d, (1505, 185), "B  ROTARY: چرخش جفت‌های Q و K", 26, WHITE, True, "rtl", "ra")
text(d, (895, 230), "RoPE: Q, K rotate; V unchanged", 17, CYAN, True, "ltr", "la")
# Coordinate axes and a rotation arc.
origin=(1050,375)
d.line((origin[0]-95,origin[1],origin[0]+130,origin[1]), fill="#49617e", width=2)
d.line((origin[0],origin[1]+75,origin[0],origin[1]-95), fill="#49617e", width=2)
d.line((origin,(1130,315)), fill=PURPLE, width=6)
d.line((origin,(1110,275)), fill=ORANGE, width=6)
d.arc((1003, 328, 1100, 425), start=300, end=345, fill=GREEN, width=4)
text(d, (1080, 340), "mθᵢ", 19, GREEN, True, "ltr")
text(d, (1485, 310), "(q₂ᵢ, q₂ᵢ₊₁)", 20, PURPLE, True, "ltr", "ra", True)
text(d, (1485, 355), "→ R(mθᵢ)q", 19, WHITE, False, "ltr", "ra", True)
text(d, (1485, 409), "qₘᵀkₙ به فاصله n−m حساس می‌شود", 17, MUTED, False, "rtl", "ra")

box(d, (240, 520, 1360, 585), outline="#36516d", fill="#17243a", radius=18, width=2)
center(d, (265, 525, 1335, 580), "attention ترتیب‌محور نیست؛ جایگاه را جداگانه یا با چرخش وارد کن", 23, WHITE, True, "rtl")

# Pre-LN residual block schematic.
box(d, (55, 620, 1545, 925), outline=GREEN)
text(d, (1495, 642), "بلوک Pre-LN: دو زیرلایه، دو مسیر باقیمانده", 27, WHITE, True, "rtl", "ra")
text(d, (90, 650), "RESIDUAL STREAM", 16, CYAN, True, "ltr", "la")
flow=[
    ((95,720,270,825), PURPLE, "LayerNorm", "نرمال‌سازی ویژگی"),
    ((350,720,565,825), CYAN, "Self-Attention", "ترکیب موقعیت‌ها"),
    ((685,720,860,825), GREEN, "+ Residual", "x + attention"),
    ((945,720,1110,825), PURPLE, "LayerNorm", "پیش از FFN"),
    ((1190,720,1370,825), ORANGE, "FFN", "D → dff → D"),
    ((1400,720,1510,825), GREEN, "+ x", "باقی‌مانده"),
]
for rect, color, title, sub in flow:
    box(d, rect, outline=color, radius=16, width=2)
    x1,y1,x2,y2=rect
    center(d,(x1+4,y1+15,x2-4,y1+58),title,18,color,True,"ltr" if title.isascii() else "rtl")
    center(d,(x1+4,y1+61,x2-4,y2-8),sub,14,MUTED,False,"rtl")
for a,b,c in [((275,772),(338,772),CYAN),((570,772),(675,772),CYAN),((865,772),(938,772),PURPLE),((1115,772),(1180,772),ORANGE),((1375,772),(1390,772),GREEN)]:
    arrow(d,a,b,c,4)
# Identity route, drawn above the two main transformations.
d.line((100,690,1515,690), fill="#5f7a9a", width=3)
d.line((100,690,100,713), fill="#5f7a9a", width=3)
d.line((1515,690,1515,713), fill="#5f7a9a", width=3)
text(d,(805,668),"identity path",15,MUTED,True,"ltr",anchor="mm")
text(d,(90,866),"FFN weights are shared across positions within a layer; each layer has its own weights.",13,CYAN,True,"ltr","la")
text(d,(90,892),"Residuals preserve a direct path; LayerNorm has learned γ and β.",13,GREEN,True,"ltr","la")

im.save(OUT, "WEBP", quality=90, method=6)
print(f"Wrote {OUT.relative_to(ROOT)}: {W}x{H}, {OUT.stat().st_size} bytes")
