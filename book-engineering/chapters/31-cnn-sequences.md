# جلد دوم، فصل ۱۰ — شبکه‌های کانولوشنی و بازگشتی

**هنر و علم ساخت هوش | Babak & Ai | فصل سراسری ۳۱**

تاریخ اجرا و مراجعه به منابع: ۵ نوامبر ۲۰۲۶.

## ۱. چرا ساختار داده مهم است؟

در فصل ۹ یک بردار را با MLP طبقه‌بندی کردیم. تصویر علاوه بر مقدار پیکسل، همسایگی مکانی دارد؛ توالی نیز ترتیب و وابستگی زمانی دارد. شبکه کانولوشنی (Convolutional Neural Network یا CNN) با فیلترهای مشترک از ساختار محلی استفاده می‌کند و شبکه بازگشتی (Recurrent Neural Network یا RNN) وضعیت را در طول توالی منتقل می‌کند. این سوگیری‌ها مفیدند، اما به‌خودی‌خود تضمین‌کننده تعمیم، انصاف یا فهم صحنه نیستند.

**پیش‌نیاز:** فصل‌های ۶ تا ۹ جلد دوم. **هدف:** محاسبه ابعاد CNN، آموزش تصویر با آزمون مستقل و تحلیل خطا، و توضیح تفاوت RNN، LSTM و GRU. آزمایش تصویر با CPU و داده کوچک موجود در scikit-learn انجام شده؛ آموزش مدل توالی در این فصل انجام نشده است.

## ۲. تصویر، کانال و فیلتر

در PyTorch ترتیب تصویر دسته‌ای `(N,C,H,W)` است: اندازه دسته، تعداد کانال، ارتفاع و عرض. فیلتر روی یک پنجره محلی حرکت می‌کند و وزن‌هایش در مکان‌های مختلف مشترک‌اند. `Conv2d` طبق مستندات در واقع **هم‌بستگی متقابل** بدون وارونگی هسته را محاسبه می‌کند [۱]؛ در گفتار رایج آن را کانولوشن می‌نامیم. کانال‌های خروجی نقشه‌های ویژگی‌اند و مقدار آن‌ها لزوماً مفاهیم قابل نام‌گذاری انسانی نیست.

برای بعد ورودی `H`، هسته `K`، padding متقارن `P`، گام `S` و dilation برابر `D`: `Hout=floor((H+2P−D(K−1)−1)/S+1)`. برای `H=8,K=3,P=1,S=1,D=1` خروجی ۸ است. ۸ فیلتر، یک کانال ورودی و بایاس در هر فیلتر، `8*(1*3*3+1)=80` پارامتر دارند. pooling تعداد پارامتر آموزش‌پذیر ندارد، اما اطلاعات را فشرده می‌کند.

فرمول شکل ارتفاع کانولوشن؛ متن جایگزین: کفِ حاصل تقسیم ارتفاع به‌علاوه دو برابر padding منهای dilation ضرب اندازه هسته منهای یک، سپس منهای یک، بر stride، به‌علاوه یک.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="ارتفاع خروجی کانولوشن برابر کفِ نسبت ارتفاع به علاوه دو padding منهای dilation ضرب K منهای یک و منهای یک بر stride به علاوه یک"><mrow><msub><mi>H</mi><mi>out</mi></msub><mo>=</mo><mo>⌊</mo><mfrac><mrow><mi>H</mi><mo>+</mo><mn>2</mn><mi>P</mi><mo>−</mo><mi>D</mi><mo>(</mo><mi>K</mi><mo>−</mo><mn>1</mn><mo>)</mo><mo>−</mo><mn>1</mn></mrow><mi>S</mi></mfrac><mo>+</mo><mn>1</mn><mo>⌋</mo></mrow></math>

![شکل ۲-۱۰-۱: ورودی تک‌کاناله ۸ در ۸ با کانولوشن هشت‌کاناله، pooling به ۴ در ۴، تخت‌سازی ۱۲۸ و خروجی ده logit می‌رسد.](assets/images/babak-ai/v2-ch10-cnn.webp)

**شکل ۲-۱۰-۱ — ابعاد مسیر تصویر.** ترجمه برچسب‌ها: ویژگی‌های مکانی و طبقه‌بندی؛ INPUT ورودی، CONV کانولوشن ۳×۳، MAX POOL بیشینه‌گیری، FLATTEN تخت‌سازی، LINEAR لایه خطی و logits امتیازهای خام؛ ترتیب محور کانال، ارتفاع، عرض است. بعد دسته برای خوانایی حذف شده است؛ ReLU بعد از کانولوشن و پیش از pooling قرار دارد.

## ۳. داده، مرزهای آزمایش و معماری

`load_digits` دارای ۱۷۹۷ تصویر ۸×۸ از ده رقم با شدت ۰ تا ۱۶ است [۲]. این مجموعه خود نسخه‌ای از بخش آزمون دیتاست اصلی UCI است؛ تقسیم ما **فقط درون نسخه scikit-learn** انجام می‌شود و آن را با تقسیم رسمی منبع اصلی اشتباه نگیرید. تقسیم طبقه‌بندی‌شده با seedهای ۴۲ و ۴۳ شامل ۱۰۷۷ آموزش، ۳۶۰ اعتبارسنجی و ۳۶۰ آزمون است؛ تصویرها بر ۱۶ ثابت شناخته‌شده تقسیم می‌شوند، نه با آماری محاسبه‌شده از آزمون. هویت نویسنده در این تقسیم کنترل نشده، پس تعمیم به نویسندگان کاملاً جدید ثابت نشده است.

معماری `Conv2d(1,8,3,padding=1) → ReLU → MaxPool2d(2) → Flatten → Linear(128,10)` و خروجی ده logit است. CrossEntropyLoss در آموزش به logit خام و برچسب صحیح کلاس نیاز دارد؛ softmax جداگانه پیش از آن در این کد لازم نیست. Adam نرخ ۰٫۰۱ و ۸ epoch، batch=64 و seed=42 از پیش ثابت شده‌اند. اعتبارسنجی فقط برای گزارش است؛ انتخاب و تکرار روی آزمون استقلال آن را از بین می‌برد.

## ۴. پروژه طبقه‌بندی تصویر و تحلیل خطا

**محیط اجرا:** Python 3.13.16، NumPy 2.3.5، scikit-learn 1.6.1، PyTorch 2.6.0+cpu. از پوشه پروژه، `python cnn_digits.py` و `python -m unittest -v` را اجرا کنید. مجموعه از بسته scikit-learn بارگیری می‌شود، به دریافت آنلاین جداگانه نیاز ندارد. نصب کتابخانه‌ها نیازمند شبکه است. پروژه داده یا فایل شخصی دریافت نمی‌کند.

```python
"""Small CPU CNN on sklearn digits, fixed train/validation/test split."""
import numpy as np
import torch
from torch import nn
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

def split():
    digits=load_digits();X=digits.images.astype('float32')[:,None,:,:]/16.0;y=digits.target.astype('int64')
    idx=np.arange(len(y));trainval,test=train_test_split(idx,test_size=.2,random_state=42,stratify=y)
    train,val=train_test_split(trainval,test_size=.25,random_state=43,stratify=y[trainval])
    return X,y,train,val,test

def model():
    return nn.Sequential(nn.Conv2d(1,8,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),nn.Flatten(),nn.Linear(8*4*4,10))

def fit(epochs=8):
    if epochs<1:raise ValueError('epochs must be positive')
    torch.manual_seed(42);torch.set_num_threads(1)
    X,y,tr,val,te=split();X=torch.from_numpy(X);y=torch.from_numpy(y);net=model();opt=torch.optim.Adam(net.parameters(),lr=.01);criterion=nn.CrossEntropyLoss()
    generator=torch.Generator().manual_seed(42)
    loader=torch.utils.data.DataLoader(torch.utils.data.TensorDataset(X[tr],y[tr]),batch_size=64,shuffle=True,generator=generator)
    net.train()
    for _ in range(epochs):
        for xb,yb in loader:
            opt.zero_grad(); loss=criterion(net(xb),yb);loss.backward();opt.step()
    net.eval()
    with torch.no_grad():
        v=net(X[val]);z=net(X[te]);pred=z.argmax(1);acc=(pred==y[te]).float().mean().item();v_loss=criterion(v,y[val]).item()
    cm=confusion_matrix(y[te].numpy(),pred.numpy(),labels=list(range(10)))
    wrong=[(int(te[i]),int(y[te][i]),int(pred[i])) for i in range(len(te)) if pred[i]!=y[te][i]]
    return net,{'train_n':len(tr),'val_n':len(val),'test_n':len(te),'val_loss':v_loss,'test_accuracy':acc,'confusion':cm,'errors':wrong}

def main():
    _,r=fit();print('train_n',r['train_n'],'val_n',r['val_n'],'test_n',r['test_n']);print('val_loss',round(r['val_loss'],6),'test_accuracy',round(r['test_accuracy'],6));print('confusion_matrix\n',r['confusion']);print('errors count',len(r['errors']),'first five (dataset index, true, predicted):',r['errors'][:5])
if __name__=='__main__':main()
```

**نتیجه این اجرای CPU:** زیان اعتبارسنجی `0.187624`، دقت آزمون `0.930556` یا ۳۳۵ درست از ۳۶۰؛ ۲۵ خطا. مثلاً نمونه ۷۵۱ برچسب ۹ و پیش‌بینی ۴، نمونه ۹۶۵ برچسب ۳ و پیش‌بینی ۲ داشت. ماتریس در خروجی کامل کد با ردیفِ برچسب واقعی و ستونِ پیش‌بینی چاپ می‌شود؛ برای رقم ۸، چهار مورد ۱ پیش‌بینی شده‌اند. این شمارش توصیفی است؛ بدون مشاهده تصویر و بررسی داده، علت خطا را حدس قطعی نمی‌زنیم. شش آزمون جداسازی اندیس‌ها، ابعاد، دقت و ماتریس، تکرارپذیری، ورودی نامعتبر و شکل‌های توالی موفق بود.

## ۵. RNN و پس‌انتشار در زمان

در RNN ساده، `h_t=tanh(W_x x_t+W_h h_(t−1)+b)`؛ پارامترها در گام‌های زمان مشترکند. خروجی هر زمان به گذشته و ورودی کنونی وابسته است؛ RNN دوسویه در صورت فعال بودن از هر دو جهت استفاده می‌کند و برای پیش‌بینی علّی بدون مراقبت می‌تواند آینده را نشت دهد. پس‌انتشار در زمان (BPTT) شبکه را در طول گام‌ها باز می‌کند. ضرب مکرر مشتق‌ها ممکن است گرادیان را محو یا منفجر کند؛ clipping برای انفجار کمک می‌کند اما حل عمومی همه وابستگی‌های دور نیست.

برای دسته با `batch_first=True` ورودی `(N,L,F)` و خروجی یک‌لایه یک‌طرفه `(N,L,H)` است. حالت نهایی همچنان شکل `(1,N,H)` دارد؛ در توالی با طول متفاوت، padding باید با طول‌ها و mask یا packed sequence کنترل شود تا گام مصنوعی به‌عنوان داده واقعی تعبیر نشود. هنگام تقسیم سری زمانی از نشت آینده و پنجره‌های هم‌پوشان بین آموزش و آزمون جلوگیری کنید.

## ۶. LSTM و GRU

LSTM حالت سلولی `c_t` و حالت پنهان `h_t` را با دروازه‌های ورودی، فراموشی و خروجی کنترل می‌کند: `c_t=f_t⊙c_(t−1)+i_t⊙g_t` و `h_t=o_t⊙tanh(c_t)` [۳]. GRU حالت پنهان را با دروازه‌های reset و update ترکیب می‌کند و حالت سلولی جدا ندارد [۴]. این سازوکارها می‌توانند انتقال اطلاعات و گرادیان را بهتر کنند، ولی حافظه بی‌نهایت یا عملکرد بهتر در هر مسئله تضمین نیست.

آزمون پروژه شکل خروجی RNN، LSTM و GRU را برای ورودی `(3,5,2)` و hidden=4 می‌سنجد: خروجی `(3,5,4)` و حالت پنهان `(1,3,4)`؛ LSTM علاوه بر آن حالت سلولی دارد. این تست صرفاً قرارداد شکل را بررسی می‌کند، نه یادگیری، کیفیت پیش‌بینی یا برتری معماری.

## ۷. انتخاب، خطاها و کاربرد مسئولانه

CNN برای داده شبکه‌ای و ساختار مکانی مناسب است؛ RNNها ترتیب را در وضعیت خلاصه می‌کنند و اجرای زمانی آن‌ها اغلب کمتر از روش‌های تماماً موازی قابل موازی‌سازی است. Transformer و attention در جلد سوم بررسی می‌شوند؛ مقایسه عددی بین آن‌ها اینجا انجام نشده است. هنگام استقرار تصویر به مجوز داده، حریم خصوصی، کیفیت، خطای زیرگروه‌ها و حساسیت به تغییر نور و دستگاه توجه کنید. تقسیم تصادفی تصویر بدون کنترل نویسنده، تخمینی محدود از سناریوی عملی است.

عیب‌یابی: جابه‌جایی کانال و بعد دسته سبب خطای شکل می‌شود؛ logit و برچسب را با قالب درست به زیان بدهید؛ پیش از ارزیابی `eval()` و `no_grad()` را به‌کار ببرید؛ با seed ثابت همچنان نسخه‌ها و دستگاه را ثبت کنید. برای توالی، محاسبه حالت را میان کاربران مستقل ناخواسته به اشتراک نگذارید.

## ۸. تمرین، پروژه و ارزیابی

۱) شکل تصویر در PyTorch چیست؟ ۲) با kernel=3 و padding=1 خروجی ۸ چگونه محاسبه می‌شود؟ ۳) چند پارامتر لایه کانولوشن پروژه دارد؟ ۴) چرا logit خام به زیان می‌دهیم؟ ۵) ماتریس خطا را چگونه می‌خوانیم؟ ۶) چرا تقسیم نویسنده‌محور مهم است؟ ۷) RNN یک‌سویه چگونه از آینده محافظت می‌کند؟ ۸) مشکل گرادیان در توالی بلند چیست؟ ۹) دو حالت LSTM چیست؟ ۱۰) آیا GRU حافظه نامحدود دارد؟

**تمرین عملی:** یک epoch را تغییر دهید، عدد را فقط روی اعتبارسنجی مقایسه و قبل از انتخاب نهایی پروتکل را ثبت کنید. **پروژه:** با داده مجاز و آزمون جدا CNN بسازید، خط پایه، ماتریس خطا، نمونه‌های خطا و محدودیت تقسیم را گزارش کنید؛ اگر توالی دارید وابستگی زمانی و نشت را کنترل کنید. معیار قبولی: حداقل ۸ پاسخ درست، محاسبه ۸۰ پارامتر، اجرای شش تست و گزارش محدودیت. [پاسخ‌نامه](book-engineering/answers/31-cnn-sequences-fa.md).

## ۹. جمع‌بندی و منابع

CNN از اشتراک فیلتر در مکان استفاده می‌کند؛ RNN، LSTM و GRU ترتیب را با حالت بازگشتی مدل می‌کنند. فصل بعد embedding، خودرمزگذار، GAN و انتشار را معرفی می‌کند. این فصل از PyTorch 2.6 استفاده کرده؛ تازه‌ترین بودن API یا کیفیت نسخه‌های بعد آزموده نشده است.

[۱] PyTorch، [Conv2d 2.6](https://docs.pytorch.org/docs/2.6/generated/torch.nn.Conv2d.html). [۲] scikit-learn، [load_digits 1.6](https://scikit-learn.org/1.6/modules/generated/sklearn.datasets.load_digits.html). [۳] PyTorch، [LSTM 2.6](https://docs.pytorch.org/docs/2.6/generated/torch.nn.LSTM.html). [۴] PyTorch، [GRU 2.6](https://docs.pytorch.org/docs/2.6/generated/torch.nn.GRU.html). تاریخ انتشار صفحه‌ها نامشخص، مراجعه ۵ نوامبر ۲۰۲۶.
