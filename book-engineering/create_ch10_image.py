from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parent.parent;p=root/'assets/images/babak-ai/ch10-condition.webp';p.parent.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(1500,1000),'#101321');d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def t(xy,s,n,rtl=False,color='#edf2ff',anchor='mt',heavy=False):d.text(xy,s,font=ImageFont.truetype(bold if heavy else font,n,layout_engine=ImageFont.Layout.RAQM),fill=color,direction='rtl' if rtl else 'ltr',anchor=anchor)
def box(xy,fill):d.rounded_rectangle(xy,radius=24,fill=fill,outline='#8194d0',width=3)
t((1420,55),'تصمیم با شرط',48,True,anchor='ra',heavy=True);t((80,140),'IF / ELSE · CONTROL FLOW',25,color='#a3b4d7',anchor='la')
d.polygon([(750,220),(1100,375),(750,530),(400,375)],fill='#303d67',outline='#9aace7',width=4);t((750,332),'زمان ≥ هدف؟',36,True,heavy=True);t((750,392),'minutes >= goal',24,color='#a5c9df')
d.line((400,375,230,375,230,610),fill='#7bdae7',width=6);d.line((1100,375,1270,375,1270,610),fill='#c2adff',width=6)
d.polygon([(230,610),(218,591),(242,591)],fill='#7bdae7');d.polygon([(1270,610),(1258,591),(1282,591)],fill='#c2adff')
t((295,400),'درست',28,True,color='#8ce0eb',heavy=True);t((1205,400),'نادرست',28,True,color='#cbbcff',heavy=True)
box((50,620,500,800),'#243d4d');box((1000,620,1450,800),'#352d4d');t((275,665),'هدف محقق شد',33,True,heavy=True);t((1225,665),'تمرین را ادامه بده',33,True,heavy=True)
im.save(p,'WEBP',quality=88,method=6);print(p,im.size,p.stat().st_size)
