"""Create the original bilingual causal-mask and multi-head diagram for chapter 35."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/images/babak-ai/v3-ch03-self-attention.webp"
WIDTH, HEIGHT = 1600, 1000
BG = "#0b1220"
CARD = "#111c2e"
BORDER = "#355073"
WHITE = "#f3f7ff"
MUTED = "#c4d0e2"
CYAN = "#55d6e8"
PURPLE = "#b39bff"
GREEN = "#68d6a7"
ORANGE = "#ffc978"
RED = "#ff8297"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def font(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)


def txt(draw, xy, value, size=30, color=WHITE, bold=False, direction="rtl", anchor=None, mono=False):
    path = MONO if mono else (SANS_BOLD if bold else SANS)
    draw.text(xy, value, font=font(path, size), fill=color, direction=direction,
              language="fa" if direction == "rtl" else "en", anchor=anchor)


def rounded(draw, box, fill=CARD, outline=BORDER, radius=25, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def centered(draw, box, value, size, color, bold=False, direction="ltr", mono=False):
    x1, y1, x2, y2 = box
    f = font(MONO if mono else (SANS_BOLD if bold else SANS), size)
    bbox = draw.textbbox((0, 0), value, font=f, direction=direction,
                         language="fa" if direction == "rtl" else "en")
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x1 + (x2 - x1 - w) / 2, y1 + (y2 - y1 - h) / 2 - bbox[1]), value,
              font=f, fill=color, direction=direction,
              language="fa" if direction == "rtl" else "en")


def arrow(draw, start, end, color="#93a9c7", width=5):
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    if x2 >= x1:
        draw.polygon([(x2, y2), (x2 - 15, y2 - 11), (x2 - 15, y2 + 11)], fill=color)
    else:
        draw.polygon([(x2, y2), (x2 + 15, y2 - 11), (x2 + 15, y2 + 11)], fill=color)


image = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((40, 35, 1560, 125), radius=28, fill="#101b2d", outline="#263b59", width=2)
txt(draw, (1510, 58), "چند سر، یک توالی، بدون نگاه به آینده", 39, WHITE, True, "rtl", anchor="ra")
txt(draw, (75, 75), "SELF-ATTENTION  •  MULTI-HEAD  •  CAUSAL MASK", 21, CYAN, True, "ltr", anchor="la")

# A single X supplies Q, K, and V; independent projections feed each head.
flow = [
    ((55, 185, 365, 425), CYAN, "ورودی X", "یک توالی برای Q/K/V", "B × L × d_model"),
    ((435, 185, 815, 425), PURPLE, "فرافکنی‌های آموختنی", "Q = XWQ   K = XWK   V = XWV", "همان L موقعیت"),
    ((885, 185, 1225, 425), ORANGE, "H سر موازی", "هر سر فضای خودش را دارد", "B × H × L × dh"),
    ((1295, 185, 1545, 425), GREEN, "الحاق و WO", "Concat → خروجی", "B × L × d_model"),
]
for box, color, title, subtitle, shape in flow:
    rounded(draw, box, fill=CARD, outline=color, radius=24, width=3)
    x1, y1, x2, y2 = box
    centered(draw, (x1 + 10, y1 + 22, x2 - 10, y1 + 78), title, 24, color, True, "rtl")
    centered(draw, (x1 + 12, y1 + 94, x2 - 12, y1 + 152), subtitle, 18, WHITE, False, "rtl")
    centered(draw, (x1 + 10, y1 + 170, x2 - 10, y1 + 225), shape, 19, MUTED, True, "ltr", True)

arrow(draw, (375, 305), (420, 305), CYAN, 5)
arrow(draw, (825, 305), (870, 305), PURPLE, 5)
arrow(draw, (1235, 305), (1280, 305), GREEN, 5)
rounded(draw, (295, 455, 1305, 515), fill="#17243a", outline="#344964", radius=18, width=2)
txt(draw, (1275, 472), "برای هر سر، attention جداگانه؛ سپس الحاق، نه میانگین‌گیریِ خروجی سرها", 21, WHITE, True, "rtl", anchor="ra")

# Lower-triangular causal mask with labelled rows and columns.
rounded(draw, (65, 555, 730, 925), fill=CARD, outline=PURPLE, radius=25, width=3)
txt(draw, (700, 576), "ماسک علّی ۵×۵", 27, WHITE, True, "rtl", anchor="ra")
txt(draw, (92, 597), "CAUSAL: ALLOW j ≤ i", 16, CYAN, True, "ltr", anchor="la")
cell = 54
x0, y0 = 285, 655
for j in range(5):
    centered(draw, (x0 + j * cell, 615, x0 + (j + 1) * cell, 649), f"j={j}", 15, MUTED, True, "ltr", True)
for i in range(5):
    centered(draw, (225, y0 + i * cell, 278, y0 + (i + 1) * cell), f"i={i}", 15, MUTED, True, "ltr", True)
    for j in range(5):
        x1, y1 = x0 + j * cell, y0 + i * cell
        allowed = j <= i
        fill = "#174a42" if allowed else "#472536"
        color = GREEN if allowed else RED
        draw.rounded_rectangle((x1 + 3, y1 + 3, x1 + cell - 3, y1 + cell - 3),
                               radius=7, fill=fill, outline=color, width=2)
        centered(draw, (x1, y1, x1 + cell, y1 + cell), "✓" if allowed else "×", 23, color, True, "ltr")

# Explanation card for the row-wise visibility rule.
rounded(draw, (790, 555, 1535, 925), fill=CARD, outline=GREEN, radius=25, width=3)
txt(draw, (1495, 580), "قانون دید هر موقعیت", 28, WHITE, True, "rtl", anchor="ra")
txt(draw, (825, 602), "ATTENTION WEIGHT = 0 FOR FUTURE KEYS", 14, CYAN, True, "ltr", anchor="la")
centered(draw, (830, 640, 1495, 705), "j ≤ i  مجاز       •       j > i  بسته", 25, ORANGE, True, "rtl")
rounded(draw, (850, 730, 1475, 835), fill="#17243a", outline="#344964", radius=18, width=2)
txt(draw, (1445, 750), "نمونه: در موقعیت i=2، فقط t0، t1 و t2 دیده می‌شوند.", 21, WHITE, True, "rtl", anchor="ra")
txt(draw, (1445, 793), "t3 و t4 آینده‌اند؛ وزنشان در softmax دقیقاً صفر است.", 20, MUTED, False, "rtl", anchor="ra")
txt(draw, (825, 895), "SELF-ATTENTION USES THE SAME SEQUENCE FOR Q, K, V", 13, GREEN, True, "ltr", anchor="la")

image.save(OUT, "WEBP", quality=90, method=6)
print(f"Wrote {OUT.relative_to(ROOT)}: {WIDTH}x{HEIGHT}, {OUT.stat().st_size} bytes")
