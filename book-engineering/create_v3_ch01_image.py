"""Create the original, bilingual WebP diagram for volume 3 chapter 1."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/images/babak-ai/v3-ch01-tokenization.webp"
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
    draw.text(xy, value, font=font(path, size), fill=color, direction=direction, language="fa" if direction == "rtl" else "en", anchor=anchor)

def rounded(draw, box, fill=CARD, outline=BORDER, radius=28, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def centered_text(draw, box, value, size, color, bold=False, direction="rtl", mono=False):
    x1,y1,x2,y2=box
    f=font(MONO if mono else (SANS_BOLD if bold else SANS),size)
    bbox=draw.textbbox((0,0),value,font=f,direction=direction,language="fa" if direction=="rtl" else "en")
    w,h=bbox[2]-bbox[0],bbox[3]-bbox[1]
    txt(draw,(x1+(x2-x1-w)/2,y1+(y2-y1-h)/2-bbox[1]),value,size,color,bold,direction,mono=mono)

image = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(image)
# Soft geometric top accents.
draw.rounded_rectangle((40,35,1560,125), radius=28, fill="#101b2d", outline="#263b59", width=2)
txt(draw,(1510,58),"از متن تا شناسه و تعبیه",44,WHITE,True,"rtl",anchor="ra")
txt(draw,(75,75),"TEXT  →  TOKEN ID  →  EMBEDDING",23,CYAN,True,"ltr",anchor="la")

# Four stages across the upper half.
boxes=[(75,205,415,540),(465,205,805,540),(855,205,1195,540),(1245,205,1525,540)]
colors=[CYAN,PURPLE,ORANGE,GREEN]
labels=[
    ("متن ورودی","Raw text"),
    ("بایت‌های UTF-8","UTF-8 bytes"),
    ("ادغام پرتکرار","Frequent merge"),
    ("شناسه توکن","Token IDs"),
]
for box,color,(fa,en) in zip(boxes,colors,labels):
    rounded(draw,box,fill="#111c2e",outline=color,width=3)
    x1,y1,x2,y2=box
    txt(draw,((x1+x2)//2,y1+38),fa,27,WHITE,True,"rtl",anchor="ma")
    txt(draw,((x1+x2)//2,y1+83),en,20,color,True,"ltr",anchor="ma")
# Contents of each stage.
centered_text(draw,(95,330,395,445),"abab",44,WHITE,True,"ltr",mono=True)
centered_text(draw,(485,328,785,450),"a   b   a   b",32,WHITE,True,"ltr",mono=True)
centered_text(draw,(875,325,1175,455),"ab × 3  →  260",29,WHITE,True,"ltr",mono=True)
centered_text(draw,(1260,325,1510,455),"[260, 260]",27,WHITE,True,"ltr",mono=True)
# Short explanatory labels.
txt(draw,(395,482),"نمونه آموزشی",17,MUTED,False,"rtl",anchor="ra")
txt(draw,(785,482),"بایت‌های آغازین",17,MUTED,False,"rtl",anchor="ra")
txt(draw,(1175,482),"شناسه ادغام اول",17,MUTED,False,"rtl",anchor="ra")
txt(draw,(1498,482),"برای abab",17,MUTED,False,"rtl",anchor="ra")
# Arrows between upper stages.
for x1,x2 in [(420,458),(810,848),(1200,1238)]:
    y=375
    draw.line((x1,y,x2,y),fill="#93a9c7",width=5)
    draw.polygon([(x2,y),(x2-13,y-10),(x2-13,y+10)],fill="#93a9c7")

# Connector to the embedding lookup row.
draw.line((1385,550,1385,600,1180,600,1180,650),fill=GREEN,width=4)
draw.polygon([(1180,650),(1169,632),(1191,632)],fill=GREEN)

# Embedding table.
rounded(draw,(180,650,820,885),fill="#111c2e",outline=PURPLE,width=3)
txt(draw,(785,675),"جدول تعبیه",28,WHITE,True,"rtl",anchor="ra")
txt(draw,(215,690),"Embedding table",20,PURPLE,True,"ltr",anchor="la")
txt(draw,(785,735),"واژگان اسباب‌بازی: هر شناسه یک ردیف",20,MUTED,False,"rtl",anchor="ra")
# Rows and vector cells.
for row,(y,label,color) in enumerate([(785,"260",CYAN),(833,"101",ORANGE)]):
    txt(draw,(250,y),label,20,color,True,"ltr",anchor="lm",mono=True)
    for col in range(5):
        x=330+col*72
        shade=["#24465a","#2b5670","#345d78","#276875","#294e72"][(col+row)%5]
        draw.rounded_rectangle((x,y-14,x+55,y+14),radius=7,fill=shade,outline=color,width=1)
    if row==1:
        txt(draw,(738,y),"…",19,MUTED,False,"ltr",anchor="lm")

# Output vectors.
rounded(draw,(920,650,1430,885),fill="#111c2e",outline=CYAN,width=3)
txt(draw,(1395,675),"بردارها",28,WHITE,True,"rtl",anchor="ra")
txt(draw,(955,690),"Vectors",20,CYAN,True,"ltr",anchor="la")
centered_text(draw,(960,740,1390,810),"x₁ = E[260]    x₂ = E[260]",21,WHITE,True,"ltr",mono=True)
txt(draw,(1395,845),"برای این نمونه: شکل (۲، d)",19,MUTED,False,"rtl",anchor="ra")
# Link table to output vectors.
draw.line((820,765,910,765),fill=PURPLE,width=5)
draw.polygon([(910,765),(893,754),(893,776)],fill=PURPLE)

# Note strip.
rounded(draw,(180,920,1430,975),fill="#17243a",outline="#344964",radius=18,width=2)
txt(draw,(1400,937),"شناسه‌ها وابسته به واژگان و مدل‌اند؛ این اعداد فقط نمونه‌اند.",20,WHITE,True,"rtl",anchor="ra")
txt(draw,(205,948),"IDs depend on the model vocabulary.",16,CYAN,True,"ltr",anchor="la")

OUT.parent.mkdir(parents=True,exist_ok=True)
image.save(OUT,"WEBP",quality=89,method=6)
print(f"Wrote {OUT.relative_to(ROOT)}: {WIDTH}x{HEIGHT}, {OUT.stat().st_size} bytes")
