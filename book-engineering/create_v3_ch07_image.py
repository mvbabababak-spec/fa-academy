"""Create a bilingual diagram of multimodal encoders and fusion routes."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/images/babak-ai/v3-ch07-multimodal-bridge.webp"
W, H = 1600, 1000
BG = "#091321"
CARD = "#111e31"
LINE = "#344c68"
WHITE = "#f2f6ff"
MUTED = "#bac9df"
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


def box(draw, coords, outline=LINE, fill=CARD, radius=18, width=3):
    draw.rounded_rectangle(coords, radius=radius, fill=fill, outline=outline, width=width)


def center(draw, coords, value, size, color=WHITE, bold=False, direction="rtl", mono=False):
    x1, y1, x2, y2 = coords
    f = font(size, bold, mono)
    kwargs = {"direction": direction, "language": "fa" if direction == "rtl" else "en"}
    bounds = draw.textbbox((0, 0), value, font=f, **kwargs)
    tw, th = bounds[2] - bounds[0], bounds[3] - bounds[1]
    draw.text((x1 + (x2-x1-tw)/2, y1 + (y2-y1-th)/2 - bounds[1]), value,
              font=f, fill=color, **kwargs)


def text(draw, xy, value, size=18, color=WHITE, bold=False, direction="rtl", anchor=None, mono=False):
    draw.text(xy, value, font=font(size, bold, mono), fill=color,
              direction=direction, language="fa" if direction == "rtl" else "en", anchor=anchor)


def arrow(draw, start, end, color=CYAN, width=4):
    draw.line((start, end), fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2-x1) >= abs(y2-y1):
        sign = 1 if x2 >= x1 else -1
        draw.polygon([(x2,y2),(x2-13*sign,y2-8),(x2-13*sign,y2+8)], fill=color)
    else:
        sign = 1 if y2 >= y1 else -1
        draw.polygon([(x2,y2),(x2-8,y2-13*sign),(x2+8,y2-13*sign)], fill=color)


def tag(draw, coords, label, color, size=14, direction="ltr", mono=False):
    box(draw, coords, outline=color, fill="#15263b", radius=10, width=2)
    center(draw, coords, label, size, color, True, direction, mono)


im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)
box(d, (40, 25, 1560, 125), outline="#304765", fill="#101b2d", radius=24, width=2)
text(d, (1515, 45), "از سیگنال تا پیوند چندوجهی", 31, WHITE, True, "rtl", "ra")
text(d, (75, 74), "IMAGE  •  TEXT  •  AUDIO  •  ALIGNMENT  •  FUSION", 15, CYAN, True, "ltr", "la")

# Three input-specific encoders.
panels = [
    (55, 155, 520, 495, PURPLE, "تصویر", "IMAGE PATCHES"),
    (600, 155, 1065, 495, CYAN, "متن", "TOKEN SEQUENCE"),
    (1090, 155, 1545, 495, ORANGE, "صوت", "AUDIO FRAMES"),
]
for x1, y1, x2, y2, color, title, subtitle in panels:
    box(d, (x1, y1, x2, y2), outline=color, fill=CARD, radius=22, width=3)
    center(d, (x1+15, y1+12, x2-15, y1+58), title, 24, color, True, "rtl")
    center(d, (x1+18, y1+58, x2-18, y1+89), subtitle, 13, MUTED, True, "ltr")

# Visual inputs / tokens.
# Image patch mosaic.
for row in range(2):
    for col in range(4):
        x0, y0 = 135 + col*52, 260 + row*48
        fill = ["#4b426c", "#315263", "#776843", "#3a6c62"][(row+col) % 4]
        box(d, (x0, y0, x0+43, y0+38), outline="#7786a1", fill=fill, radius=6, width=1)
center(d, (105, 367, 470, 397), "patchify + positional information", 14, WHITE, True, "ltr")
box(d, (105, 408, 470, 463), outline=PURPLE, fill="#1b2437", radius=13, width=2)
center(d, (117, 412, 458, 459), "Vision Transformer\npatch tokens → pooled vector", 15, WHITE, True, "ltr")

# Text token row.
for i, token in enumerate(("<s>", "a", "red", "car", "</s>")):
    x0 = 657 + i*73
    tag(d, (x0, 274, x0+62, 314), token, CYAN, 13, "ltr", True)
center(d, (630, 352, 1035, 389), "tokenizer + padding mask + positions", 14, WHITE, True, "ltr")
box(d, (650, 408, 1015, 463), outline=CYAN, fill="#132838", radius=13, width=2)
center(d, (662, 412, 1003, 459), "Text Transformer\ntoken states → pooled vector", 15, WHITE, True, "ltr")

# Audio frame bars.
for i in range(8):
    x0 = 1150 + i*42
    height = 22 + (i*19 % 53)
    d.rounded_rectangle((x0, 323-height, x0+27, 323+height), radius=5,
                        fill=ORANGE if i % 2 == 0 else "#bb8f54")
center(d, (1120, 368, 1515, 397), "waveform → log-Mel / time frames", 14, WHITE, True, "ltr")
box(d, (1130, 408, 1505, 463), outline=ORANGE, fill="#2b2432", radius=13, width=2)
center(d, (1142, 412, 1493, 459), "Audio Transformer\nframe tokens → pooled vector", 15, WHITE, True, "ltr")

# Output arrows and normalized embeddings.
for xmid, color in ((287, PURPLE), (832, CYAN), (1317, ORANGE)):
    arrow(d, (xmid, 495), (xmid, 542), color, 3)
tag(d, (205, 545, 370, 588), "z_image", PURPLE, 16, "ltr", True)
tag(d, (750, 545, 915, 588), "z_text", CYAN, 16, "ltr", True)
tag(d, (1235, 545, 1400, 588), "z_audio", ORANGE, 16, "ltr", True)

# Lower left: shared normalized embedding space.
box(d, (50, 625, 770, 940), outline=GREEN, fill="#101f31", radius=22, width=3)
center(d, (75, 637, 745, 683), "مسیر A — هم‌ترازی embedding", 22, GREEN, True, "rtl")
center(d, (80, 681, 740, 717), "نرمال‌سازی → ماتریس شباهت → InfoNCE / retrieval", 14, WHITE, True, "rtl")
# Simple diagonal-positive similarity matrix.
cell = 30
sx, sy = 110, 738
for row in range(4):
    for col in range(4):
        x0, y0 = sx+col*39, sy+row*36
        fill = GREEN if row == col else "#293951"
        d.rounded_rectangle((x0, y0, x0+cell, y0+cell), radius=6, fill=fill)
        center(d, (x0, y0, x0+cell, y0+cell), "+" if row == col else "−", 15, "#081521" if row == col else MUTED, True, "ltr")
text(d, (730, 760), "قطر: جفت مثبت", 15, GREEN, True, "rtl", "ra")
text(d, (730, 805), "غیرقطر: منفی‌های batch", 14, MUTED, False, "rtl", "ra")
center(d, (76, 891, 744, 925), "بردار نزدیک ≠ شاهد ناحیه‌ای یا پاسخِ grounded", 14, PINK, True, "rtl")

# Lower right: cross-attention to token-level context.
box(d, (805, 625, 1550, 940), outline=PINK, fill="#101f31", radius=22, width=3)
center(d, (830, 637, 1525, 683), "مسیر B — تبادل توکن با Cross-Attention", 22, PINK, True, "rtl")
# Text queries on left, visual/audio key-value memories on right.
for i in range(3):
    tag(d, (850, 735+i*49, 950, 771+i*49), f"Q{i+1}", CYAN, 15, "ltr", True)
for i in range(4):
    tag(d, (1335, 717+i*40, 1440, 752+i*40), f"K,V {i+1}", PURPLE if i < 2 else ORANGE, 13, "ltr", True)
# Multi-query arrows show interaction rather than pairwise cosine.
for start, end in [((950,753),(1335,736)),((950,753),(1335,816)),((950,802),(1335,776)),((950,851),(1335,856))]:
    arrow(d, start, end, LINE, 2)
box(d, (1033, 749, 1250, 832), outline=PINK, fill="#252238", radius=15, width=2)
center(d, (1043, 753, 1240, 828), "Cross-Attention\nQ: متن\nK,V: تصویر / صوت", 14, WHITE, True, "ltr")
center(d, (832, 898, 1524, 926), "جزئیات بیشتر؛ هزینه و نیاز به دادهٔ جفت‌شده هم بیشتر", 14, MUTED, True, "rtl")

im.save(OUT, "WEBP", quality=92, method=6)
print(f"Wrote {OUT.relative_to(ROOT)}: {W}x{H}, {OUT.stat().st_size} bytes")
