"""Create the accessible data-pipeline diagram for volume 3 chapter 40."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/images/babak-ai/v3-ch08-data-pipeline.webp"
W, H = 1600, 1000
BG, CARD, LINE = "#091321", "#111e31", "#344c68"
WHITE, MUTED = "#f2f6ff", "#bac9df"
CYAN, PURPLE, GREEN, ORANGE, PINK = "#55d6e8", "#b39bff", "#68d6a7", "#ffc978", "#ff8da1"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def font(size, bold=False, mono=False):
    path = MONO if mono else (BOLD if bold else SANS)
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)


def rounded(draw, coords, outline=LINE, fill=CARD, radius=18, width=3):
    draw.rounded_rectangle(coords, radius=radius, fill=fill, outline=outline, width=width)


def center(draw, coords, value, size, color=WHITE, bold=False, direction="rtl", mono=False):
    x1, y1, x2, y2 = coords
    f = font(size, bold, mono)
    kwargs = {"direction": direction, "language": "fa" if direction == "rtl" else "en"}
    bounds = draw.multiline_textbbox((0, 0), value, font=f, spacing=8, **kwargs)
    tw, th = bounds[2] - bounds[0], bounds[3] - bounds[1]
    draw.multiline_text(((x1 + x2 - tw) / 2, (y1 + y2 - th) / 2 - bounds[1]), value,
                        font=f, fill=color, spacing=8, align="center", **kwargs)


def text(draw, xy, value, size=18, color=WHITE, bold=False, direction="rtl", anchor=None, mono=False):
    draw.text(xy, value, font=font(size, bold, mono), fill=color,
              direction=direction, language="fa" if direction == "rtl" else "en", anchor=anchor)


def arrow(draw, start, end, color=CYAN, width=4):
    draw.line((start, end), fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2-x1) >= abs(y2-y1):
        sign = 1 if x2 >= x1 else -1
        draw.polygon([(x2, y2), (x2-13*sign, y2-8), (x2-13*sign, y2+8)], fill=color)
    else:
        sign = 1 if y2 >= y1 else -1
        draw.polygon([(x2, y2), (x2-8, y2-13*sign), (x2+8, y2-13*sign)], fill=color)


def tag(draw, coords, label, color, size=14, direction="ltr", mono=False):
    rounded(draw, coords, outline=color, fill="#15263b", radius=10, width=2)
    center(draw, coords, label, size, color, True, direction, mono)


im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)
rounded(d, (40, 25, 1560, 122), outline="#304765", fill="#101b2d", radius=24, width=2)
text(d, (1515, 42), "از منشأ تا پیکرهٔ آمادهٔ آموزش", 31, WHITE, True, "rtl", "ra")
text(d, (75, 76), "PERMISSION  •  PROVENANCE  •  SPLITS  •  TRAIN-ONLY VOCAB", 14, CYAN, True, "ltr", "la")

# Collection and evidence gate.
rounded(d, (55, 165, 350, 390), outline=PURPLE, fill=CARD, radius=22, width=3)
center(d, (72, 178, 333, 220), "منبع", 24, PURPLE, True, "rtl")
center(d, (80, 232, 325, 297), "self-written /\nexplicitly permitted", 17, WHITE, True, "ltr")
tag(d, (86, 323, 319, 365), "license + terms + date", PURPLE, 14, "ltr", True)

arrow(d, (350, 278), (415, 278), CYAN, 4)

rounded(d, (420, 165, 720, 390), outline=CYAN, fill=CARD, radius=22, width=3)
center(d, (438, 179, 702, 220), "منشأ و حریم خصوصی", 21, CYAN, True, "rtl")
tag(d, (458, 243, 683, 283), "manifest.jsonl", CYAN, 16, "ltr", True)
center(d, (444, 301, 696, 363), "source • attribution\ngroup_id • rights_note", 15, MUTED, True, "ltr")

arrow(d, (720, 278), (784, 278), GREEN, 4)

rounded(d, (790, 165, 1080, 390), outline=GREEN, fill=CARD, radius=22, width=3)
center(d, (808, 179, 1063, 220), "پاک‌سازی و audit", 22, GREEN, True, "rtl")
tag(d, (830, 244, 1041, 283), "NFC + hash", GREEN, 16, "ltr", True)
center(d, (815, 302, 1057, 363), "exact dedup\nkeep audit trail", 15, MUTED, True, "ltr")

arrow(d, (1080, 278), (1145, 278), ORANGE, 4)

rounded(d, (1150, 165, 1545, 390), outline=ORANGE, fill=CARD, radius=22, width=3)
center(d, (1170, 179, 1525, 220), "تقسیم گروهی با seed", 22, ORANGE, True, "rtl")
center(d, (1177, 235, 1518, 290), "group_id stays in one split", 16, WHITE, True, "ltr")
center(d, (1180, 310, 1515, 355), "deterministic • documented", 14, MUTED, True, "ltr")

# Branches: train alone may fit tokenizer.
arrow(d, (1350, 390), (1350, 465), GREEN, 4)
arrow(d, (1350, 465), (280, 465), GREEN, 4)
for x, label, color in [(280, "train", GREEN), (800, "validation", CYAN), (1320, "test", ORANGE)]:
    arrow(d, (x, 465), (x, 520), color, 4)
    rounded(d, (x-190, 522, x+190, 690), outline=color, fill="#101f31", radius=20, width=3)
    tag(d, (x-120, 540, x+120, 586), label, color, 18, "ltr", True)
    if label == "train":
        center(d, (x-168, 599, x+168, 674), "fit vocab / tokenizer\ntrain model later", 17, WHITE, True, "ltr")
    elif label == "validation":
        center(d, (x-168, 599, x+168, 674), "select settings\nnot model weights", 16, WHITE, True, "ltr")
    else:
        center(d, (x-168, 599, x+168, 674), "final holdout\nkeep unseen", 16, WHITE, True, "ltr")

# Only train points to vocab.
arrow(d, (280, 690), (280, 762), GREEN, 4)
rounded(d, (90, 770, 470, 880), outline=GREEN, fill="#122233", radius=20, width=3)
center(d, (107, 781, 453, 819), "V_train", 22, GREEN, True, "ltr", True)
center(d, (108, 826, 452, 865), "<pad> <unk> <bos> <eos>", 14, MUTED, True, "ltr", True)

# All partitions plus vocabulary flow to next chapter.
for x, color in [(800, CYAN), (1320, ORANGE)]:
    arrow(d, (x, 690), (x, 842), color, 3)
arrow(d, (470, 825), (570, 825), GREEN, 3)
rounded(d, (575, 775, 1515, 880), outline=PINK, fill="#211b2c", radius=20, width=3)
center(d, (600, 789, 1490, 829), "فصل ۴۱: دادهٔ جدا + tokenizer ثابت → حلقهٔ آموزش و ارزیابی", 20, PINK, True, "rtl")
center(d, (600, 838, 1490, 868), "test never fits the vocabulary • group overlap = 0", 14, MUTED, True, "ltr")

rounded(d, (55, 915, 1545, 975), outline="#304765", fill="#101b2d", radius=18, width=2)
center(d, (80, 920, 1520, 970), "مجوز را با URL، attribution و شرایط نگه‌دار؛ hash جایگزین مجوز یا بازبینی انسانی نیست.", 16, WHITE, True, "rtl")

im.save(OUT, "WEBP", quality=92, method=6)
print(f"Wrote {OUT.relative_to(ROOT)}: {W}x{H}, {OUT.stat().st_size} bytes")
