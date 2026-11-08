from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parent.parent
out=root/'assets/images/babak-ai/ch06-parallel.webp';out.parent.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(1600,980),'#101321');d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def t(xy,s,size,color='#edf2ff',rtl=False,anchor='mt',heavy=False):
 d.text(xy,s,font=ImageFont.truetype(bold if heavy else font,size,layout_engine=ImageFont.Layout.RAQM),fill=color,direction='rtl' if rtl else 'ltr',anchor=anchor)
def box(coords,fill='#252d50',line='#7788ca'):
 d.rounded_rectangle(coords,radius=22,fill=fill,outline=line,width=3)
t((1510,55),'جریان مفهومی محاسبه شتاب‌یافته',46,rtl=True,anchor='ra',heavy=True)
t((90,140),'ACCELERATED COMPUTING · CONCEPTUAL',25,'#a3b2d4',anchor='la')
box((85,270,470,560));t((278,310),'آماده‌سازی و کنترل',34,rtl=True,heavy=True);t((278,375),'CPU / HOST',29,'#9acddd');t((278,445),'داده و دستور کار',27,'#c9d5ec',rtl=True)
box((1110,270,1510,560));t((1310,310),'محاسبه موازی',35,rtl=True,heavy=True);t((1310,375),'GPU / ACCELERATOR',26,'#9acddd');t((1310,445),'واحدهای اجرایی',27,'#c9d5ec',rtl=True)
d.line((490,352,1095,352),fill='#74dbe7',width=6);d.polygon([(1095,352),(1074,340),(1074,364)],fill='#74dbe7')
d.line((1095,475,490,475),fill='#b5a8ff',width=6);d.polygon([(490,475),(511,463),(511,487)],fill='#b5a8ff')
t((800,300),'کار و داده',29,rtl=True,heavy=True);t((800,492),'نتیجه',29,'#dad2ff',rtl=True,heavy=True)
box((170,670,1430,820),'#1d303e','#58bacb');t((800,705),'انتقال، ظرفیت و پهنای باند نیز هزینه دارند',34,rtl=True,heavy=True);t((800,765),'SHARED OR SEPARATE MEMORY DEPENDS ON THE SYSTEM',22,'#aec9da')
im.save(out,'WEBP',quality=88,method=6);print(out,im.size,out.stat().st_size,'bytes')
