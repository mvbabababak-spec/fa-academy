"""Create the original bilingual WebP matrix-flow diagram for volume 3 chapter 2."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/images/babak-ai/v3-ch02-attention.webp"
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
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def font(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)


def txt(draw, xy, value, size=30, color=WHITE, bold=False, direction="rtl", anchor=None, mono=False):
    path = MONO if mono else (SANS_BOLD if bold else SANS)
    draw.text(xy, value, font=font(path, size), fill=color, direction=direction,
              language="fa" if direction == "rtl" else "en", anchor=anchor)


def rounded(draw, box, fill=CARD, outline=BORDER, radius=28, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def centered_text(draw, box, value, size, color, bold=False, direction="ltr", mono=False):
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
txt(draw, (1510, 58), "از پرس‌وجو تا بردار خروجی", 42, WHITE, True, "rtl", anchor="ra")
txt(draw, (75, 75), "SCALED DOT-PRODUCT ATTENTION", 23, CYAN, True, "ltr", anchor="la")

# Source tensors and their distinct roles.
source_cards = [
    ((65, 170, 500, 365), CYAN, "Q   پرس‌وجو / Query", "از حالتِ پرس‌وجوکننده", "Lq × dk"),
    ((585, 170, 1015, 365), PURPLE, "K   کلید / Key", "از حالت‌های منبع", "Lk × dk"),
    ((1100, 170, 1535, 365), GREEN, "V   مقدار / Value", "اطلاعاتی که ترکیب می‌شوند", "Lk × dv"),
]
for box, color, title, subtitle, shape in source_cards:
    rounded(draw, box, fill=CARD, outline=color, radius=26, width=3)
    x1, y1, x2, y2 = box
    centered_text(draw, (x1 + 15, y1 + 15, x2 - 15, y1 + 70), title, 27, color, True, "rtl")
    centered_text(draw, (x1 + 15, y1 + 72, x2 - 15, y1 + 120), subtitle, 21, WHITE, False, "rtl")
    centered_text(draw, (x1 + 15, y1 + 128, x2 - 15, y1 + 180), shape, 24, ORANGE, True, "ltr", True)

# Cross-attention example: query may come from decoder, K/V from encoder.
rounded(draw, (270, 395, 1330, 470), fill="#17243a", outline="#344964", radius=20, width=2)
txt(draw, (1295, 414), "نمونهٔ توجه میان‌دنباله‌ای: Q از رمزگشا؛ K و V از رمزگذار", 23, WHITE, True, "rtl", anchor="ra")
txt(draw, (300, 437), "CROSS-ATTENTION EXAMPLE", 15, CYAN, True, "ltr", anchor="la")

# Matrix pipeline: product -> scale and row softmax -> weighted values.
boxes = [
    ((65, 550, 470, 765), CYAN, "امتیازها / Scores", "S = QKᵀ", "Lq × Lk"),
    ((600, 550, 1010, 765), ORANGE, "وزن‌ها / Weights", "A = softmax(S / √dk)", "Lq × Lk"),
    ((1140, 550, 1535, 765), GREEN, "خروجی / Output", "O = AV", "Lq × dv"),
]
for box, color, title, formula, shape in boxes:
    rounded(draw, box, fill=CARD, outline=color, radius=26, width=3)
    x1, y1, x2, y2 = box
    centered_text(draw, (x1 + 14, y1 + 16, x2 - 14, y1 + 62), title, 25, color, True, "rtl")
    centered_text(draw, (x1 + 12, y1 + 73, x2 - 12, y1 + 134), formula, 26, WHITE, True, "ltr", True)
    centered_text(draw, (x1 + 12, y1 + 145, x2 - 12, y1 + 190), shape, 22, MUTED, False, "ltr", True)

arrow(draw, (478, 655), (585, 655), CYAN, 5)
centered_text(draw, (485, 585, 580, 635), "/ √dk\n+ softmax", 17, ORANGE, True, "ltr", True)
arrow(draw, (1018, 655), (1125, 655), GREEN, 5)
centered_text(draw, (1022, 585, 1120, 635), "× V", 22, GREEN, True, "ltr", True)
# V joins the final product from above.
draw.line((1320, 365, 1320, 505), fill=GREEN, width=4)
arrow(draw, (1320, 505), (1320, 540), GREEN, 4)

# Clarify softmax's row-wise normalization and the weighted-sum interpretation.
rounded(draw, (100, 815, 1500, 925), fill="#17243a", outline="#344964", radius=20, width=2)
txt(draw, (1465, 835), "هر سطرِ A برای یک پرس‌وجو است و روی موقعیت‌های کلید جمعش ۱ می‌شود.", 23, WHITE, True, "rtl", anchor="ra")
txt(draw, (1465, 877), "خروجی هر سطر، ترکیبِ وزن‌دارِ ردیف‌های V است؛ وزن‌ها به‌تنهایی توضیح قطعی نیستند.", 20, MUTED, False, "rtl", anchor="ra")
txt(draw, (120, 897), "ROW-WISE NORMALIZATION  •  WEIGHTED SUM", 15, CYAN, True, "ltr", anchor="la")

image.save(OUT, "WEBP", quality=90, method=6)
print(f"Wrote {OUT.relative_to(ROOT)}: {WIDTH}x{HEIGHT}, {OUT.stat().st_size} bytes")
