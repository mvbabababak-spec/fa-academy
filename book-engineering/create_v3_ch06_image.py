"""Create a bilingual systems map for chapter 38 (local chapter 6)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/images/babak-ai/v3-ch06-efficiency-map.webp"
W, H = 1600, 1000
BG = "#0a1220"
CARD = "#111e31"
LINE = "#314764"
WHITE = "#f2f6ff"
MUTED = "#bac9df"
CYAN = "#55d6e8"
PURPLE = "#b39bff"
GREEN = "#68d6a7"
ORANGE = "#ffc978"
PINK = "#ff8da1"
RED = "#e98893"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def font(size, bold=False, mono=False):
    path = MONO if mono else (BOLD if bold else SANS)
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)


def text(draw, xy, value, size=20, color=WHITE, bold=False, direction="rtl", anchor=None, mono=False):
    draw.text(xy, value, font=font(size, bold, mono), fill=color, direction=direction,
              language="fa" if direction == "rtl" else "en", anchor=anchor)


def box(draw, coords, outline=LINE, fill=CARD, radius=18, width=3):
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


def arrow(draw, a, b, color=CYAN, width=4):
    draw.line((a, b), fill=color, width=width)
    x1, y1 = a
    x2, y2 = b
    if abs(x2-x1) >= abs(y2-y1):
        sign = 1 if x2 >= x1 else -1
        draw.polygon([(x2,y2),(x2-13*sign,y2-8),(x2-13*sign,y2+8)], fill=color)
    else:
        sign = 1 if y2 >= y1 else -1
        draw.polygon([(x2,y2),(x2-8,y2-13*sign),(x2+8,y2-13*sign)], fill=color)


def matrix(draw, x, y, allowed, cell=25, gap=4, allow_color=GREEN, deny_color="#26364c"):
    for row in range(len(allowed)):
        for col in range(len(allowed[row])):
            color = allow_color if allowed[row][col] else deny_color
            x0, y0 = x + col*(cell+gap), y + row*(cell+gap)
            draw.rounded_rectangle((x0,y0,x0+cell,y0+cell), radius=4, fill=color)


def tag(draw, coords, label, color, size=14, direction="ltr", mono=False):
    box(draw, coords, outline=color, fill="#15263b", radius=10, width=2)
    center(draw, coords, label, size, color, True, direction, mono)


im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)
box(d, (40, 25, 1560, 120), outline="#304765", fill="#101b2d", radius=24, width=2)
text(d, (1515, 48), "زمینهٔ بلند: گلوگاه‌ها و مصالحه‌ها", 31, WHITE, True, "rtl", "ra")
text(d, (75, 72), "CONTEXT  •  MEMORY  •  ATTENTION  •  ROUTING", 15, CYAN, True, "ltr", "la")

panels = [(45, 145, 550, 755, PURPLE), (565, 145, 1050, 755, CYAN), (1065, 145, 1555, 755, ORANGE)]
for x1, y1, x2, y2, color in panels:
    box(d, (x1, y1, x2, y2), outline=color, fill=CARD, radius=22, width=3)

# 1) Dense, sparse patterns, and the exact-but-IO-aware FlashAttention distinction.
center(d, (62, 157, 533, 202), "۱) هر توکن به کجا نگاه می‌کند؟", 22, PURPLE, True, "rtl")
center(d, (60, 205, 292, 237), "Dense: همهٔ جفت‌ها", 16, WHITE, True, "rtl")
center(d, (302, 205, 535, 237), "Sparse: همسایگی + global", 15, WHITE, True, "rtl")
full = [[1]*5 for _ in range(5)]
local_global = [
    [1,1,0,0,1],
    [1,1,1,0,1],
    [0,1,1,1,1],
    [0,0,1,1,1],
    [1,1,1,1,1],
]
matrix(d, 89, 250, full, cell=26, gap=5, allow_color=PURPLE)
matrix(d, 334, 250, local_global, cell=26, gap=5, allow_color=GREEN)
center(d, (59, 412, 295, 447), "O(T²)", 21, PURPLE, True, "ltr", True)
center(d, (298, 412, 540, 447), "O(TW + TG)", 19, GREEN, True, "ltr", True)
center(d, (57, 450, 543, 484), "W: پنجرهٔ محلی  |  G: توکن‌های سراسری", 14, MUTED, False, "rtl")
box(d, (73, 498, 523, 590), outline=PINK, fill="#1b2437", radius=15, width=2)
text(d, (502, 509), "FlashAttention", 18, PINK, True, "ltr", "ra")
center(d, (88, 540, 508, 578), "دقیق و Dense؛ tiling برای کاهش I/O\nنه الگوی Sparse و نه حذف هزینهٔ محاسبه", 14, WHITE, False, "rtl")
center(d, (66, 615, 529, 694), "ماسک محلی، اگر Dense اجرا شود،\nبه‌تنهایی سرعت Sparse ایجاد نمی‌کند.", 15, MUTED, True, "rtl")

# 2) The linearly growing KV cache and the role of H_kv in GQA.
center(d, (580, 157, 1035, 202), "۲) KV Cache: حافظه با طول رشد می‌کند", 22, CYAN, True, "rtl")
center(d, (580, 208, 1034, 241), "هر گام: K,V تازه به وضعیت قبلی افزوده می‌شود", 14, MUTED, False, "rtl")
for i in range(6):
    x0 = 600 + i*65
    box(d, (x0, 255, x0+56, 293), outline=CYAN if i < 5 else ORANGE,
        fill="#17283e", radius=9, width=2)
    center(d, (x0+2, 258, x0+54, 290), f"t{i+1}", 14, CYAN if i < 5 else ORANGE, True, "ltr", True)
center(d, (587, 305, 1028, 339), "K₁…Kₜ  +  V₁…Vₜ  |  در هر لایه", 16, WHITE, True, "ltr", True)
box(d, (592, 351, 1022, 414), outline=CYAN, fill="#15273d", radius=13, width=2)
center(d, (602, 355, 1012, 388), "KV bytes = 2·L·B·T·Hkv·d·b", 16, CYAN, True, "ltr", True)
center(d, (602, 386, 1012, 408), "b = bytes/element", 12, MUTED, False, "ltr", True)
# Proportional bars for a worked BF16 example.
labels = [("MHA-32", 320, PURPLE), ("GQA-8", 80, GREEN), ("MQA-1", 10, ORANGE)]
for idx, (label, bar_w, color) in enumerate(labels):
    y = 433 + idx*45
    text(d, (1014, y+4), label, 14, WHITE, True, "ltr", "ra", True)
    box(d, (612, y, 612+bar_w, y+24), outline=color, fill=color, radius=9, width=1)
    text(d, (620+bar_w, y+3), ("16 GiB" if idx == 0 else "4 GiB" if idx == 1 else "0.5 GiB"), 13, color, True, "ltr", "la", True)
center(d, (587, 574, 1028, 606), "L=32 · T=32K · BF16 · B=1 · d=128", 13, MUTED, False, "ltr", True)
center(d, (585, 620, 1031, 696), "GQA، تعداد KV head را کم می‌کند؛\nخودِ پنجره را بزرگ‌تر یا کیفیت را تضمین نمی‌کند.", 15, WHITE, True, "rtl")

# 3) Sparse expert activation does not mean fewer total weights.
center(d, (1080, 157, 1540, 202), "۳) MoE: انتخاب expert برای هر توکن", 22, ORANGE, True, "rtl")
# Token stream, routing paths, router and four experts.
expert_centers = (1158, 1273, 1388, 1503)
# Inputs arrive at the router; output paths illustrate two selected experts.
for x0 in (1126, 1188, 1250, 1312):
    d.line((x0, 273, x0, 295), fill=LINE, width=2)
    d.polygon([(x0,295),(x0-5,287),(x0+5,287)], fill=LINE)
# Draw output paths before the boxes so the router label remains unobstructed.
for x0 in expert_centers:
    d.line((1206, 361, x0, 432), fill=GREEN if x0 in (expert_centers[0], expert_centers[2]) else "#42546b", width=3)
    d.polygon([(x0,439),(x0-7,426),(x0+7,426)], fill=GREEN if x0 in (expert_centers[0], expert_centers[2]) else "#42546b")
for i, x0 in enumerate((1100, 1162, 1224, 1286)):
    tag(d, (x0, 235, x0+52, 273), f"x{i+1}", CYAN, 14, "ltr", True)
box(d, (1112, 305, 1300, 360), outline=ORANGE, fill="#2b2432", radius=13, width=2)
center(d, (1122, 309, 1290, 356), "Router\nTop-1", 15, ORANGE, True, "ltr")
for index, x0 in enumerate((1120, 1235, 1350, 1465), 1):
    color = GREEN if index in (1, 3) else LINE
    box(d, (x0, 439, x0+75, 489), outline=color, fill="#17283e", radius=12, width=2)
    center(d, (x0+4, 442, x0+71, 486), f"E{index}", 17, WHITE, True, "ltr", True)
center(d, (1090, 505, 1530, 542), "Router برای هر توکن یک expert منتخب را اجرا می‌کند؛ نمونهٔ مسیر سبز.", 13, MUTED, False, "rtl")
box(d, (1095, 557, 1528, 634), outline=PINK, fill="#1b2437", radius=14, width=2)
center(d, (1108, 562, 1515, 594), "پارامتر فعال / توکن  ≠  پارامتر کل", 17, PINK, True, "ltr")
center(d, (1108, 596, 1515, 626), "وزن expertها، router و ارتباط هم هزینه دارند", 13, WHITE, False, "rtl")
center(d, (1090, 650, 1532, 709), "Sparse routing، Sparse Attention نیست؛\nتوازن بار و جابه‌جایی بین دستگاه‌ها مهم است.", 14, MUTED, True, "rtl")

# Shared long-context evaluation strip.
box(d, (47, 780, 1553, 951), outline="#36516d", fill="#111f32", radius=22, width=2)
text(d, (1515, 798), "پنجرهٔ مجاز  ≠  زمینهٔ مؤثر", 23, WHITE, True, "rtl", "ra")
center(d, (65, 842, 535, 901), "RULER: بازیابی، چندگام و تجمیع", 16, PURPLE, True, "rtl")
center(d, (565, 842, 1047, 901), "NoLiMa: پرسش و شاهد با هم‌پوشانی واژگانی کم", 15, CYAN, True, "rtl")
center(d, (1070, 842, 1533, 901), "OOLONG: دسته‌بندیِ اقلام و شمارش در متن بلند", 15, ORANGE, True, "rtl")
text(d, (74, 921), "گزارش طول واقعی، دقت وظیفه، موقعیت شاهد، latency و مصرف حافظه؛ نامِ context window به‌تنهایی benchmark نیست.", 14, MUTED, False, "rtl", "la")

im.save(OUT, "WEBP", quality=91, method=6)
print(f"Wrote {OUT.relative_to(ROOT)}: {W}x{H}, {OUT.stat().st_size} bytes")
