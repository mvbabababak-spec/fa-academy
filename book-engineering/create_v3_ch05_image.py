"""Create a bilingual architecture comparison diagram for chapter 37."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/images/babak-ai/v3-ch05-architecture-matrix.webp"
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


def text(draw, xy, value, size=22, color=WHITE, bold=False, direction="rtl", anchor=None, mono=False):
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


def matrix(draw, x, y, allowed, cell=31, gap=4, allow_color=GREEN, deny_color="#29364a"):
    for row in range(len(allowed)):
        for col in range(len(allowed[row])):
            color = allow_color if allowed[row][col] else deny_color
            x0, y0 = x + col*(cell+gap), y + row*(cell+gap)
            draw.rounded_rectangle((x0,y0,x0+cell,y0+cell), radius=5, fill=color)


def token_row(draw, x, y, labels, width=76, gap=12, color=CYAN):
    for i, label in enumerate(labels):
        x0 = x + i*(width+gap)
        box(draw, (x0,y,x0+width,y+42), outline=color, fill="#16253a", radius=12, width=2)
        center(draw, (x0+2,y+1,x0+width-2,y+41), label, 16, color, True, "ltr", True)


im = Image.new("RGB", (W,H), BG)
d = ImageDraw.Draw(im)
box(d,(42,30,1558,125),outline="#2c4261",fill="#101b2d",radius=25,width=2)
text(d,(1515,52),"سه جریان اطلاعات؛ سه انتخاب معماری",31,WHITE,True,"rtl","ra")
text(d,(75,76),"ENCODER  •  DECODER  •  CROSS-ATTENTION",16,CYAN,True,"ltr","la")

panels=[(48,155,535,790,PURPLE),(556,155,1043,790,ORANGE),(1051,155,1552,790,GREEN)]
for x1,y1,x2,y2,color in panels:
    box(d,(x1,y1,x2,y2),outline=color,fill=CARD,radius=22,width=3)

# Encoder-only: every valid source position can read the full source.
center(d,(65,170,518,215),"۱) Encoder-only",25,PURPLE,True,"ltr")
center(d,(72,224,511,258),"ورودی یک‌دنباله‌ای",17,MUTED,False,"rtl")
token_row(d,112,265,["x₁","x₂","x₃"],width=70,gap=17,color=PURPLE)
arrow(d,(282,310),(282,333),PURPLE,4)
center(d,(78,330,280,365),"Self-Attention دوطرفه",16,WHITE,True,"rtl")
matrix(d,105,372,[[1,1,1],[1,1,1],[1,1,1]],cell=34,gap=5,allow_color=GREEN)
center(d,(283,380,503,408),"هر توکن ← همهٔ متن",15,GREEN,True,"rtl")
center(d,(283,410,503,442),"(به‌جز padding)",14,MUTED,False,"rtl")
arrow(d,(282,493),(282,515),PURPLE,4)
token_row(d,112,520,["h₁","h₂","h₃"],width=70,gap=17,color=CYAN)
box(d,(91,585,494,643),outline=PURPLE,fill="#17243a",radius=14,width=2)
center(d,(103,589,482,638),"Pooling / [CLS] → سر وظیفه",17,WHITE,True,"ltr")
center(d,(79,665,504,714),"رده‌بندی • برچسب‌گذاری توکن\nبازهٔ پاسخ • بازنمایی",15,MUTED,False,"rtl")

# Decoder-only: causal self-attention over one growing token stream.
center(d,(573,170,1026,215),"۲) Decoder-only",25,ORANGE,True,"ltr")
center(d,(580,224,1019,258),"پیشوند و خروجی در یک stream",17,MUTED,False,"rtl")
token_row(d,620,265,["x₁","x₂","x₃","?"],width=65,gap=14,color=ORANGE)
arrow(d,(801,310),(801,333),ORANGE,4)
center(d,(586,330,786,365),"Self-Attention علّی",16,WHITE,True,"rtl")
matrix(d,617,372,[[1,0,0,0],[1,1,0,0],[1,1,1,0],[1,1,1,1]],cell=31,gap=5,allow_color=ORANGE,deny_color="#3b2637")
center(d,(776,375,1018,414),"ردیف i فقط j≤i\n(خانهٔ قرمز: آینده)ⁱ",14,MUTED,False,"rtl")
arrow(d,(801,531),(801,553),ORANGE,4)
box(d,(603,559,996,617),outline=ORANGE,fill="#17243a",radius=14,width=2)
center(d,(615,563,984,612),"توزیع توکن بعدی → ادامهٔ متن",17,WHITE,True,"rtl")
center(d,(582,648,1018,714),"تکمیل • گفت‌وگو • تولید آزاد\nآموزش معمول: پیش‌بینی توکن بعدی",15,MUTED,False,"rtl")

# Encoder-decoder: a source memory conditions a separate autoregressive target.
center(d,(1066,170,1537,215),"۳) Encoder–Decoder",25,GREEN,True,"ltr")
center(d,(1069,223,1535,255),"ورودی و خروجی جدا",17,MUTED,False,"rtl")
token_row(d,1116,260,["x₁","x₂","x₃"],width=63,gap=12,color=CYAN)
arrow(d,(1323,303),(1323,320),CYAN,4)
box(d,(1090,324,1509,373),outline=CYAN,fill="#16253a",radius=13,width=2)
center(d,(1102,327,1497,369),"Encoder: زمینهٔ دوسویه",17,WHITE,True,"rtl")
arrow(d,(1323,374),(1323,389),CYAN,4)
box(d,(1090,392,1509,432),outline=CYAN,fill="#173044",radius=12,width=2)
center(d,(1102,394,1497,429),"حافظهٔ منبع Hₑ",16,CYAN,True,"ltr",True)
arrow(d,(1323,433),(1323,449),GREEN,4)
box(d,(1090,451,1509,512),outline=GREEN,fill="#16253a",radius=13,width=2)
center(d,(1102,453,1497,480),"Decoder: causal self-attn",15,WHITE,True,"ltr")
center(d,(1102,481,1497,507),"+ cross-attn به Hₑ",15,GREEN,True,"ltr")
arrow(d,(1323,513),(1323,531),GREEN,4)
token_row(d,1116,536,["y₁","y₂","…"],width=63,gap=12,color=GREEN)
center(d,(1070,597,1533,648),"ترجمه • خلاصه‌سازی • تبدیل ورودی به متن",15,MUTED,False,"rtl")
center(d,(1070,661,1533,706),"Decoder هر گام را با منبع شرطی می‌کند",14,GREEN,True,"rtl")

# Cross-attention connector from encoder memory to decoder block.
d.line((1517,410,1530,410,1530,481,1512,481),fill=PINK,width=4)
d.polygon([(1512,481),(1525,473),(1525,489)],fill=PINK)
text(d,(1512,445),"K,V",13,PINK,True,"ltr","ra",True)

box(d,(50,822,1550,952),outline="#36516d",fill="#121f32",radius=20,width=2)
text(d,(1510,842),"نقشهٔ انتخاب: شکلِ ورودی/خروجی را با جریان اطلاعات جور کن",21,WHITE,True,"rtl","ra")
center(d,(75,875,515,926),"متن → بازنمایی/برچسب/بازه",17,PURPLE,True,"rtl")
center(d,(580,875,1018,926),"پیشوند → ادامهٔ بعدی",17,ORANGE,True,"rtl")
center(d,(1070,875,1525,926),"منبع → متنِ هدفِ شرطی",17,GREEN,True,"rtl")
text(d,(75,962),"ماتریس‌ها «خانهٔ روشن = مجاز» را نشان می‌دهند؛ در PyTorch برای bool-mask، True یعنی مسدود.",13,MUTED,False,"rtl","la")

im.save(OUT,"WEBP",quality=91,method=6)
print(f"Wrote {OUT.relative_to(ROOT)}: {W}x{H}, {OUT.stat().st_size} bytes")
