# جلد دوم، فصل ۹ — ساخت و بازتولید شبکه عصبی با NumPy و PyTorch

**هنر و علم ساخت هوش | Babak & Ai | شماره سراسری ۳۰**

تاریخ مرجع: ۴ نوامبر ۲۰۲۶؛ مراجعه به منابع و اجرای آزمایش: ۵ نوامبر ۲۰۲۶.

## ۱. از قطعات جداگانه به سیستم قابل اجرا

در سه فصل گذشته لایه، زیان، گرادیان و بهینه‌ساز را جداگانه مطالعه کردیم. در این فصل یک شبکه کامل دودویی روی داده ساختگی می‌سازیم: ورودی، وزن، عبور رو به جلو، زیان پایدار، پس‌انتشار، به‌روزرسانی، ارزیابی و ذخیره/بارگذاری وزن‌ها. سپس **همان مسئله و تنظیمات** را در PyTorch بازتولید می‌کنیم. مقایسه منصفانه مستلزم یکسان بودن ورودی، مقدار اولیه، معماری، dtype، زیان، نرخ، ترتیب و تعداد گام‌هاست.

**پیش‌نیاز:** فصل‌های ۶، ۷ و ۸ جلد دوم و برنامه‌نویسی Python و NumPy. **هدف:** پیاده‌سازی و آزمون گرادیان هر پارامتر، مشاهده کاهش زیان، مقایسه دو چارچوب و سنجش بازیابی وزن. نمونه روی CPU اجرا شده؛ GPU و کاربرد حساس بررسی نشده‌اند.

## ۲. تعریف داده و پروتکل

مولد ثابت ۳۰۰ نقطه دوبعدی مستقل از بازه `[−1,1]` می‌سازد و برچسب مصنوعی `y=1 if x₁+0.7x₂>0 else 0` است. ۱۸۰ نمونه اول آموزش، ۶۰ نمونه بعد اعتبارسنجی و ۶۰ نمونه آخر آزمون‌اند؛ مولد مستقل و یکسان برای نقاط، و seed=42 است. داده خصوصی، فایل خارجی و برچسب انسانی وجود ندارد. این مسئله عمداً ساده و خطی‌جدایی‌پذیر است؛ کارایی بالا هیچ نتیجه‌ای درباره داده واقعی، انصاف یا عملکرد خارج توزیع ثابت نمی‌کند.

معماری ۲–۴–۱، فعال‌سازی tanh، زیان دودویی میانگین از logit، SGD تمام‌دسته با نرخ ۰٫۳ و ۳۰۰ گام **از پیش تعیین شده‌اند**. اعتبارسنجی برای گزارش است و در این نمونه هیچ تنظیمی با آن انتخاب نمی‌شود؛ آزمون یک‌بار بعد از آموزش گزارش می‌شود. در پروژه واقعی، ابرپارامترها را روی اعتبارسنجی یا CV انتخاب و آزمون را مستقل نگه دارید.

## ۳. طراحی شبکه و ابعاد

`X` شکل `(n,2)`، `W₁` شکل `(2,4)` و `b₁` شکل `(4,)` دارند؛ `H=tanh(XW₁+b₁)` شکل `(n,4)`، `W₂` شکل `(4,1)` و `b₂` شکل `(1,)` دارند. logit برابر `Z=HW₂+b₂` و شکل آن `(n,1)` است. تعداد پارامترها `(2×4)+4+(4×1)+1=17` است. در `nn.Linear`، PyTorch وزن را به شکل `(out,in)` نگه می‌دارد؛ هنگام کپی از NumPy باید ماتریس را ترانهاده کرد.

برای هر گام: زیان را از logit حساب کنید، گرادیان‌های تحلیلی را با وزن‌های همان گام بسازید، همه وزن‌ها را هم‌زمان به‌روزرسانی کنید. در PyTorch از `zero_grad()`، `loss.backward()` و `optimizer.step()` استفاده می‌کنیم [۱]. تبدیل مستقیم logit به کلاس در آستانه احتمال ۰٫۵ معادل شرط `z≥0` است؛ احتمالات و آستانه‌های دیگر نیازمند پروتکل خود هستند.

![شکل ۲-۹-۱: داده آموزش مشترک به پیاده‌سازی NumPy و PyTorch می‌رود؛ خروجی‌ها با هم مقایسه و سپس روی داده آزمون جدا گزارش می‌شوند.](assets/images/babak-ai/v2-ch09-network.webp)

**شکل ۲-۹-۱ — دو اجرای هم‌ارز.** این نمودار ترتیب آزمایش است؛ هیچ ردیف آزمون به آموزش وارد نمی‌شود. ذخیره و بارگذاری وزن پس از آموزش بررسی می‌شود.

## ۴. زیان، پس‌انتشار و کنترل عددی

`L=mean(logaddexp(0,Z)−Y*Z)`؛ این بیان پایدار آنتروپی متقاطع دودویی با logit است. `D_Z=(sigmoid(Z)−Y)/n`، سپس `dW₂=HᵀD_Z`، `db₂=sum(D_Z)`، `D_A=(D_ZW₂ᵀ)⊙(1−H²)`، `dW₁=XᵀD_A` و `db₁=sum(D_A)`؛ جمع‌های بایاس روی ردیف‌های دسته‌اند. از ضرب عنصری و ماتریسی به‌درستی استفاده کنید.

برای هر یک از ۱۷ پارامتر روی چهار نمونه آموزش، تقریب تفاضل مرکزی با ε=۱e−۶ در float64 در آزمون با گرادیان تحلیلی مقایسه می‌شود. سپس دو آموزش با مقدار اولیه یکسان انجام می‌شوند و logitهای آزمون مقایسه می‌شوند. تطبیق عددی نتیجه همین نسخه و سخت‌افزار است؛ مقایسه مدل‌های مستقل با مقداردهی تصادفی متفاوت انتظار تطبیق وزن ندارد.

## ۵. ذخیره، بازیابی و امنیت

در نمونه `state_dict` مدل PyTorch در پوشه موقت ذخیره، مدل هم‌معماری ساخته و وزن با `torch.load(...,weights_only=True,map_location='cpu')` بازیابی می‌شود؛ logit پیش و پس از بازیابی مقایسه می‌شود [۲،۳]. پوشه پس از اجرا خودکار حذف می‌شود؛ برای نگهداری واقعی، مسیر پایدار و سیاست نسخه‌بندی مشخص کنید. `weights_only=True` خطرات بارگذاری pickle را محدود می‌کند اما بارگذاری فایل نامطمئن همچنان خطر دارد؛ فقط فایل قابل اعتماد و بررسی‌شده را باز کنید.

این فایل تنها **وزن مدل برای استنتاج** است، نه checkpoint کامل ادامه آموزش. برای ادامه بازتولیدپذیر آموزش واقعی علاوه بر مدل به وضعیت بهینه‌ساز، شماره گام، scheduler، seed و وضعیت مولد تصادفی، داده و نسخه‌ها نیاز است؛ در این پروژه بازیابی همه آن‌ها پیاده‌سازی یا آزموده نشده است. `eval()` برای لایه‌های وابسته به حالت اهمیت دارد و `no_grad()` ثبت مشتق را خاموش می‌کند.

## ۶. پروژه کامل: NumPy و PyTorch

**اجرا:** Python 3.13.16، NumPy 2.3.5 و PyTorch 2.6.0+cpu؛ از پوشه `book-engineering/projects/30-neural-network` دستور `python neural_network.py` و سپس `python -m unittest -v`. در محیط مجازی CPU: `python -m pip install numpy==2.3.5` و `python -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu`. نصب نیازمند شبکه است؛ پس از نصب کد به داده یا شبکه خارجی نیاز ندارد.

```python
"""Train matching NumPy and PyTorch MLPs on synthetic independent splits."""
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
import torch
from torch import nn


def data():
    rng=np.random.default_rng(42); X=rng.uniform(-1,1,(300,2));y=(X[:,0]+0.7*X[:,1]>0).astype(float)[:,None]
    return (X[:180],y[:180]),(X[180:240],y[180:240]),(X[240:],y[240:])

def init():
    rng=np.random.default_rng(7)
    return {'W1':rng.normal(0,.3,(2,4)),'b1':np.zeros(4),'W2':rng.normal(0,.3,(4,1)),'b2':np.zeros(1)}

def logits(X,p):return np.tanh(X@p['W1']+p['b1'])@p['W2']+p['b2']

def loss_grad(X,y,p):
    if X.ndim!=2 or X.shape[1]!=2 or y.shape!=(len(X),1) or len(X)==0:raise ValueError('invalid shapes')
    h=np.tanh(X@p['W1']+p['b1']);z=h@p['W2']+p['b2'];loss=float(np.mean(np.logaddexp(0,z)-y*z))
    dz=(1/(1+np.exp(-np.clip(z,-500,500)))-y)/len(X); da=(dz@p['W2'].T)*(1-h*h)
    return loss,{'W1':X.T@da,'b1':da.sum(0),'W2':h.T@dz,'b2':dz.sum(0)}

def numerical_gradient(X,y,p,eps=1e-6):
    if eps<=0:raise ValueError('positive epsilon required')
    result={}
    for k,v in p.items():
        g=np.zeros_like(v)
        for i in np.ndindex(v.shape):
            a={n:x.copy() for n,x in p.items()};b={n:x.copy() for n,x in p.items()}
            a[k][i]+=eps;b[k][i]-=eps
            g[i]=(loss_grad(X,y,a)[0]-loss_grad(X,y,b)[0])/(2*eps)
        result[k]=g
    return result

def make_torch(p):
    model=nn.Sequential(nn.Linear(2,4),nn.Tanh(),nn.Linear(4,1)).double()
    with torch.no_grad():
        model[0].weight.copy_(torch.from_numpy(p['W1'].T.copy()));model[0].bias.copy_(torch.from_numpy(p['b1'].copy()))
        model[2].weight.copy_(torch.from_numpy(p['W2'].T.copy()));model[2].bias.copy_(torch.from_numpy(p['b2'].copy()))
    return model

def train_pair(X,y,steps=300,rate=.3):
    if steps<1 or rate<=0:raise ValueError('invalid training parameters')
    p=init();model=make_torch(p);X_t=torch.from_numpy(X);y_t=torch.from_numpy(y)
    optimizer=torch.optim.SGD(model.parameters(),lr=rate);criterion=nn.BCEWithLogitsLoss();first=loss_grad(X,y,p)[0]
    for _ in range(steps):
        _,g=loss_grad(X,y,p);p={k:p[k]-rate*g[k] for k in p}
        optimizer.zero_grad();loss=criterion(model(X_t),y_t);loss.backward();optimizer.step()
    return p,model,first,loss_grad(X,y,p)[0]

def reload_weights(model,path):
    torch.save(model.state_dict(),path);reloaded=make_torch(init())
    reloaded.load_state_dict(torch.load(path,map_location='cpu',weights_only=True));reloaded.eval();return reloaded

def main():
    (X,y),(Xv,yv),(Xt,yt)=data();p,model,first,last=train_pair(X,y);model.eval()
    val_loss=loss_grad(Xv,yv,p)[0];test_logits=logits(Xt,p)
    with torch.no_grad():torch_logits=model(torch.from_numpy(Xt)).numpy()
    accuracy=np.mean((test_logits>=0)==yt)
    with TemporaryDirectory() as tmp:
        restored=reload_weights(model,Path(tmp)/'weights.pt')
        with torch.no_grad():reloaded=restored(torch.from_numpy(Xt)).numpy()
    print(f'train_loss_before={first:.9f} train_loss_after={last:.9f} val_loss={val_loss:.9f}')
    print(f'test_accuracy={accuracy:.6f} samples train=180 val=60 test=60')
    print(f'max_numpy_torch_logit_diff={np.max(np.abs(test_logits-torch_logits)):.3e}')
    print(f'max_reload_logit_diff={np.max(np.abs(reloaded-torch_logits)):.3e}')
    print('fixed_protocol=true synthetic=true seed_data=42 seed_weights=7 device=CPU')
if __name__=='__main__':main()
```

**خروجی ثبت‌شده روی CPU:** زیان آموزش `0.693009536 → 0.058947023`؛ زیان اعتبارسنجی `0.076186755`؛ دقت آزمون `1.000000` روی ۶۰ نمونه ساختگی؛ بیشترین اختلاف logit دو پیاده‌سازی `1.776e-15` و اختلاف پس از بازیابی وزن صفر تا دقت نمایش. این اعداد نتیجه یک اجرا و مسئله ساده‌اند، نه تضمین کارایی واقعی. شش تست شامل تمام گرادیان‌ها، کاهش زیان، تطبیق چارچوب‌ها، بازیابی وزن، عدم هم‌پوشانی ردیف‌ها، بازتولید و ورودی نامعتبر موفق شدند.

**عیب‌یابی:** خطای ابعاد را با چاپ شکل `X`, `W₁`, `W₂`, y دنبال کنید؛ در انتقال وزن PyTorch ترانهاده لازم است. اگر زیان nan شد نرخ، ورودی و مقداردهی را بررسی کنید. اختلاف اندک اعشاری بین کتابخانه‌ها طبیعی است؛ اختلاف بزرگ نیاز به بررسی ترتیب گام، میانگین/مجموع زیان و dtype دارد. `weights_only` در نسخه‌های متفاوت رفتار وابسته به مستندات همان نسخه دارد.

## ۷. تفسیر و محدودیت آزمایش

این آزمایش در سطح آموزشی کل چرخه پارامترها را نشان می‌دهد؛ اما داده تست مستقل ۶۰ نمونه‌ای قطعیت آماری و تعمیم بر دنیای واقعی را تضمین نمی‌کند. برچسب مصنوعی تابع خطی است؛ مدل پیچیده‌تر از خط پایه خطی است و هیچ برتری معماری از آن نتیجه نمی‌شود. اگر نیاز کاربردی وجود داشته باشد، خط پایه لجستیک، عدم‌قطعیت، برش‌های عملکردی، تحلیل خطا و پایداری در تغییر توزیع را با داده و پروتکل معتبر بررسی کنید.

مقدار اولیه NumPy با seed=7 ایجاد و عیناً به PyTorch منتقل شده است؛ از یک seed عددی در دو کتابخانه لزوماً آرایه اولیه یکسان به‌دست نمی‌آید. داده و وزن در حافظه روی CPU و float64 هستند. در کاربرد واقعی ممکن است پردازش دسته‌ای، ذخیره وضعیت کامل، استانداردسازی آموزش، کنترل حریم خصوصی و پایش خطا ضروری باشند.

## ۸. تمرین و ارزیابی

۱) ابعاد W₁ و W₂ چیست؟ ۲) تعداد پارامترها چند است؟ ۳) چرا وزن PyTorch ترانهاده می‌شود؟ ۴) چرا logit به BCEWithLogitsLoss داده می‌شود؟ ۵) چرا `zero_grad` لازم است؟ ۶) چه چیزهایی باید در دو پیاده‌سازی یکسان باشند؟ ۷) آیا دقت ۱۰۰٪ این داده، عملکرد واقعی را ثابت می‌کند؟ ۸) `weights_only` چه محدودیتی دارد؟ ۹) آیا فایل وزن برای ادامه کامل آموزش کافی است؟ ۱۰) نقش مجموعه اعتبارسنجی در این نمونه چیست؟

**محاسبه:** برای معماری ۲–۴–۱ تعداد وزن‌ها و بایاس‌ها را حساب کنید. **تمرین کد:** تعداد گام را کم کنید، زیان آموزش را گزارش و آزمون‌های خودکار را اجرا کنید؛ تغییر پروتکل را ثبت کنید. **پروژه:** داده مصنوعی مستقل تازه تعریف، مدل NumPy و PyTorch را با مقدار اولیه یکسان مقایسه، تمام گرادیان‌ها را بررسی و وزن را ذخیره/بارگذاری کنید؛ برای مقایسه ادعای تعمیم، خط پایه و آزمون مستقل اضافه کنید.

**معیار قبولی:** هشت پاسخ درست، محاسبه ۱۷ پارامتر، شش تست موفق و گزارش داده، seed، زیان، خطای تطبیق، بازیابی و محدودیت. [پاسخ‌نامه مستقل](book-engineering/answers/30-neural-network-fa.md).

## ۹. جمع‌بندی و منابع

ساخت شبکه شامل قرارداد داده، ابعاد، زیان، مشتق، بهینه‌ساز و ارزیابی است؛ بازتولید نیازمند ثبت تنظیمات و نسخه‌هاست. فصل ۱۰ جلد دوم CNN و مدل‌های بازگشتی را معرفی می‌کند؛ این فصل ادعای آموزش شبکه تصویر یا مدل توالی ندارد. **تحولات تا نوامبر ۲۰۲۶:** PyTorch 2.6 CPU در نمونه واقعی آزموده شده؛ APIهای نسخه‌های دیگر باید جداگانه بررسی شوند.

[۱] PyTorch contributors، [Autograd tutorial](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html)، ایجاد ۱۰ فوریه ۲۰۲۱، آخرین به‌روزرسانی ۱۶ ژانویه ۲۰۲۴، مراجعه ۵ نوامبر ۲۰۲۶. [۲] همان، [Save and Load the Model](https://docs.pytorch.org/tutorials/beginner/basics/saveloadrun_tutorial.html)، به‌روزرسانی ۲۵ سپتامبر ۲۰۲۵، مراجعه ۵ نوامبر ۲۰۲۶. [۳] همان، [torch.load نسخه 2.6](https://docs.pytorch.org/docs/2.6/generated/torch.load.html)، تاریخ انتشار نامشخص، مراجعه ۵ نوامبر ۲۰۲۶.
