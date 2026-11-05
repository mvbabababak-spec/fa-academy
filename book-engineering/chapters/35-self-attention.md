# جلد سوم، فصل ۳ — Self-Attention، چندسری و ماسک علّی

**The Art & Science of Building Intelligence | Babak & Ai | فصل سراسری ۳۵ از نقشهٔ پنج‌جلدی**

**تاریخ مرجع: ۵ نوامبر ۲۰۲۶؛ منابع برخط در همین تاریخ بازبینی شدند.**

## ۱. از Attention میان‌دنباله‌ای به رابطه‌های درون یک دنباله

در فصل ۳۴ یک پرس‌وجو را با کلیدها مقایسه کردیم و مقدارها را ترکیب کردیم. در **Self-Attention**، پرس‌وجو، کلید و مقدار از یک دنبالهٔ واحد ساخته می‌شوند. اگر ورودی لایه `X` باشد، سه projection آموختنی روی همان `X` اعمال می‌شوند و هر موقعیت می‌تواند از موقعیت‌های دیگر نمایش تازه‌ای بسازد. «Self» به مبدأ مشترک `Q/K/V` اشاره دارد؛ معنایش این نیست که سه ماتریس یا سه نقش یکی هستند.

توجه Self می‌تواند دوسویه باشد: در یک لایهٔ رمزگذار، هر موقعیت اجازه دارد کل دنباله را ببیند. اما مدل خودرگرسیو که واژهٔ بعدی را پیش‌بینی می‌کند، نباید هنگام آموزش از پاسخ‌های آینده استفاده کند؛ برای آن **ماسک علّی (Causal Mask)** لازم است. پس Self-Attention و ماسک علّی دو مفهوم جدا هستند: یکی می‌گوید `Q/K/V` از کجا می‌آیند؛ دیگری تعیین می‌کند هر پرس‌وجو کدام کلیدها را می‌تواند ببیند [۱].

**پیش‌نیاز:** فرمول Attention و شکل‌های `Q/K/V` در فصل ۳۴، بردار و ضرب ماتریسی از جلدهای پیشین. **هدف:** Self-Attention را از توجه میان‌دنباله‌ای تشخیص دهید؛ سرهای متعدد را تقسیم و دوباره ادغام کنید؛ ماسک علّیِ بدون خطای یک‌خانه‌ای بسازید؛ و با تغییر ورودی آینده، آزمون کنید که خروجی‌های گذشته نشت اطلاعات نداشته باشند.

![شکل ۳-۳-۱ — در Self-Attention، یک توالی X برای ساخت Q/K/V (Query، Key، Value) به کار می‌رود؛ H سر با projectionهای مستقل موازی محاسبه و پس از الحاق با W_O ترکیب می‌شوند. ماتریس ماسک پایین‌مثلثی موقعیت‌های j≤i را باز و j>i را مسدود می‌کند؛ پرس‌وجوی t2 فقط t0 تا t2 را می‌بیند.](assets/images/babak-ai/v3-ch03-self-attention.webp)

**شکل ۳-۳-۱ — چندسری و دید علّی.** ردیف `i` به پرس‌وجوی موقعیت `i` و ستون `j` به کلید موقعیت `j` مربوط است. خانهٔ سبز مجاز است؛ خانهٔ قرمز آینده است و به softmax راه داده نمی‌شود. در مثال تصویری، موقعیت ۲ خودِ موقعیت ۲ را می‌بیند، اما موقعیت‌های ۳ و ۴ را نه.

## ۲. Self-Attention چه چیزی را محاسبه می‌کند؟

ورودی لایه را `X ∈ R^{B×L×d_model}` بگیرید: `B` تعداد نمونه‌ها، `L` طول دنباله و `d_model` بُعد ویژگی است. این فصل یک طراحی متداول را دنبال می‌کند که در آن ماتریس‌های خطی، `Q`، `K` و `V` را از همین `X` تولید می‌کنند:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="کیو برابر ایکس دبلیو کیو؛ کی برابر ایکس دبلیو کی؛ وی برابر ایکس دبلیو وی"><mrow><mi>Q</mi><mo>=</mo><mi>X</mi><msub><mi>W</mi><mi>Q</mi></msub><mo>,</mo><mspace width="0.5em"/><mi>K</mi><mo>=</mo><mi>X</mi><msub><mi>W</mi><mi>K</mi></msub><mo>,</mo><mspace width="0.5em"/><mi>V</mi><mo>=</mo><mi>X</mi><msub><mi>W</mi><mi>V</mi></msub></mrow></math>

متن جایگزین فرمول: `Q=XW_Q`، `K=XW_K`، `V=XW_V`. ورودی هر سه projection یکسان است، اما وزن‌های یادگرفتنی‌شان مستقل‌اند.

برای توجه یک‌سر، موقعیت `i` بردارهای `q_i`، `k_i` و `v_i` دارد. امتیاز `q_i` با همهٔ `k_j`ها، وزن هر `v_j` را می‌سازد؛ در self-attention غیرعلّی همهٔ موقعیت‌ها مجازند. در حالت علّی، جایگاه‌های آینده حذف می‌شوند. در هیچ‌کدام نباید فرض کنیم عدد موقعیت به‌تنهایی معنای واژگانی آماده‌ای دارد.

در معماری Transformer، این projectionها بین لایه‌ها بازنمایی‌های زمینه‌ای را تولید می‌کنند. سازوکار توجه فقط یکی از اجزای بلوک Transformer است؛ Residual، LayerNorm، Feed-Forward و نمایش موقعیت در فصل‌های بعدی نقشه می‌آیند و در پروژهٔ این فصل پیاده‌سازی نشده‌اند.

## ۳. چرا چند سر؟

یک سر توجه برای هر پرس‌وجو یک توزیع وزن روی کلیدها و یک جمع وزن‌دار می‌سازد. **Multi-Head Attention** به‌جای یک projection واحد، `h` projection متفاوت برای `Q/K/V` می‌آموزد؛ هر سر در فضای ویژگی خود attention انجام می‌دهد. سپس خروجی سرها کنار هم قرار می‌گیرد و projection نهایی آن‌ها را ترکیب می‌کند [۱].

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="سر ام برابر توجه کیو دبلیو کیو ام، کی دبلیو کی ام، وی دبلیو وی ام؛ چندسر برابر الحاق سرها ضربدر دبلیو او"><mrow><msub><mi>head</mi><mi>m</mi></msub><mo>=</mo><mi>Attention</mi><mo>(</mo><mi>Q</mi><msubsup><mi>W</mi><mi>m</mi><mi>Q</mi></msubsup><mo>,</mo><mi>K</mi><msubsup><mi>W</mi><mi>m</mi><mi>K</mi></msubsup><mo>,</mo><mi>V</mi><msubsup><mi>W</mi><mi>m</mi><mi>V</mi></msubsup><mo>)</mo><mo>,</mo><mspace width="0.5em"/><mi>MultiHead</mi><mo>=</mo><mi>Concat</mi><mo>(</mo><msub><mi>head</mi><mn>1</mn></msub><mo>,</mo><mi>…</mi><mo>,</mo><msub><mi>head</mi><mi>h</mi></msub><mo>)</mo><msup><mi>W</mi><mi>O</mi></msup></mrow></math>

متن جایگزین فرمول: سر `m` attention روی سه projection مخصوص خودش انجام می‌دهد؛ خروجی همهٔ سرها الحاق و در `W_O` ضرب می‌شود. `Concat` اتصال روی محور ویژگی است، نه میانگین‌گیریِ خروجی سرها.

در نمونهٔ اصلی Transformer، `h=8` و در آن پیکربندی `d_k=d_v=d_model/h=64` بود [۱]. در پروژهٔ کوچک این فصل، برای سادگی `d_model` را به `h` بخش مساوی تقسیم می‌کنیم و `d_h=d_model/h` می‌گیریم؛ بنابراین `d_model` باید بر `h` بخش‌پذیر باشد. این یک قرارداد رایجِ پیاده‌سازی است، نه قانون ریاضی برای هر شکل ممکن از attention. یک projection ترکیبی `d_model→d_model` و reshape به سرها، نمایش فشردهٔ همان بخش‌های آموختنی است.

چند سر می‌تواند بازنمایی‌های متفاوتی فراهم کند، اما نام‌گذاری یک سر به «فاعل‌یاب» یا «مرجع‌یاب» بدون تحلیل و آزمون، از معادله نتیجه نمی‌شود. سرها را مستقل بررسی کنید و تفسیر معنایی را فرض قطعی نگیرید.

## ۴. ردگیری شکل‌ها در یک پیاده‌سازی چندسری

در حالت batch-first:

| مرحله | شکل | معنا |
|---|---|---|
| ورودی `X` | `B×L×d_model` | یک بردار برای هر موقعیت دنباله |
| `Q,K,V` پس از projection | `B×L×d_model` برای هرکدام | projectionهای جدا از ورودی مشترک |
| reshape و جابه‌جایی محور | `B×h×L×d_h` | `d_model=h×d_h` در این طراحی |
| ماتریس امتیاز هر سر | `B×h×L×L` | هر پرس‌وجو با همهٔ موقعیت‌های کلید سنجیده می‌شود |
| وزن و خروجی سر | `B×h×L×L` و `B×h×L×d_h` | softmax روی محور کلید، سپس ضرب در `V` |
| الحاق سرها | `B×L×d_model` | بازگشت محور سرها به ویژگی |
| projection خروجی | `B×L×d_model` | ترکیب آموختنی خروجی سرها |

در کد، projection تا زمانی که محور سر ساخته شود `[B,L,h,d_h]` است. سپس `transpose(1,2)` آن را به `[B,h,L,d_h]` می‌برد تا `QKᵀ` روی دو محور آخر درست باشد. پس از `A@V`، جابه‌جایی معکوس و `contiguous().view(...)` محورهای سر و ویژگی را به `[B,L,d_model]` برمی‌گردانند.

برای طول `L`، ماتریس امتیاز استاندارد هر سر `L×L` است. در طراحی dense با همهٔ سرها، حافظهٔ وزن‌ها متناسب با `B×h×L²` و محاسبهٔ ضرب‌های توجه متناسب با `B×h×L²×d_h` رشد می‌کند. این رشد توضیح می‌دهد چرا طول زمینه هزینه‌ساز است؛ ماسک علّی در نسخهٔ صریح این پروژه تعداد خانه‌های ماتریس را کم نمی‌کند، بلکه مسیرهای اطلاعاتی را محدود می‌کند. kernelهای بهینه ممکن است محاسبات را جور دیگری سازمان دهند؛ کارایی باید روی ورودی و سخت‌افزار هدف سنجیده شود [۱، ۳].

## ۵. ماسک علّی: قانون، نه تزئین نمودار

اگر دنباله را از صفر شماره‌گذاری کنیم، پرس‌وجوی `i` فقط اجازه دارد به کلیدهای `j≤i` توجه کند. ماسک جمع‌شوندهٔ `M` برای خانهٔ مجاز صفر و برای آینده منفی بی‌نهایت می‌گذارد:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="ام آی جی صفر است اگر جی کوچک‌تر مساوی آی باشد، و منفی بی‌نهایت اگر جی بزرگ‌تر از آی باشد؛ وزن آلفا سافت‌مکس امتیاز به اضافه ماسک است"><mrow><msub><mi>M</mi><mrow><mi>i</mi><mi>j</mi></mrow></msub><mo>=</mo><mrow><mo>{</mo><mtable><mtr><mtd><mn>0</mn></mtd><mtd><mtext>اگر </mtext><mi>j</mi><mo>≤</mo><mi>i</mi></mtd></mtr><mtr><mtd><mo>−</mo><mi>∞</mi></mtd><mtd><mtext>اگر </mtext><mi>j</mi><mo>&gt;</mo><mi>i</mi></mtd></mtr></mtable></mrow><mo>,</mo><mspace width="0.5em"/><mi>A</mi><mo>=</mo><mi>softmax</mi><mo>(</mo><mfrac><mrow><mi>Q</mi><msup><mi>K</mi><mi>T</mi></msup></mrow><msqrt><msub><mi>d</mi><mi>h</mi></msub></msqrt></mfrac><mo>+</mo><mi>M</mi><mo>)</mo></mrow></math>

متن جایگزین فرمول: `Mᵢⱼ=0` برای `j≤i` و `−∞` برای `j>i`. `A=softmax(QKᵀ/√d_h + M)`. softmax روی محور آخر است.

افزودن `−∞` پیش از softmax، وزن آن موقعیت را به صفر می‌رساند. برای دنبالهٔ پنج‌تایی، سطر صفر فقط ستون صفر را می‌بیند؛ سطر ۲ فقط ستون‌های صفر، یک و دو را. قطر باید باز بماند تا هر موقعیت بتواند خودش را ببیند. بستن قطر یا جابه‌جایی مثلث، خطای off-by-one یا جهت ماسک می‌سازد.

ماسک علّی با padding mask یکی نیست. اولی به ترتیب مکانی مربوط است و آینده را می‌بندد؛ دومی جایگاه‌های پرکننده را کنار می‌گذارد. در batch با طول‌های ناهمسان ممکن است به هر دو نیاز باشد. پروژهٔ این فصل طول ثابت دارد و padding mask ندارد.

همچنین ماسک علّی به‌تنهایی خط لولهٔ آموزش خودرگرسیو را کامل نمی‌کند: ورودی و هدف باید نسبت به یکدیگر یک موقعیت جابه‌جا باشند تا پیش‌بینیِ توکن بعدی ارزیابی شود، نه بازسازیِ برچسب همان موقعیت. آزمون پروژه تنها خودِ لایهٔ attention را می‌سنجد.

## ۶. چه زمانی ماسک علّی لازم است؟

برای رمزگذار دوسویه‌ای که باید هر موقعیت را با توجه به کل متن بازنمایی کند، دیدن دو سوی توالی می‌تواند بخشی از تعریف مسئله باشد و ماسک علّی لزوماً استفاده نمی‌شود. برای رمزگشای خودرگرسیو، هنگام آموزش همهٔ موقعیت‌ها به‌صورت موازی پردازش می‌شوند، اما هر موقعیت باید فقط متن پیشین و خودش را ببیند؛ ماسک این محدودیت را اعمال می‌کند [۱]. در استنتاج یک توکن در هر گام، مفهوم «آیندهٔ موجود در ورودی» شکل دیگری دارد، اما شرط اطلاعاتیِ نشت نکردنِ هدفِ هنوز پیش‌بینی‌نشده همچنان مهم است.

علّی‌بودن را به معنای «هرچیزی در سیستم از آینده مستقل است» تعمیم ندهید. ماسک این زیرلایه را محدود می‌کند. خطای ترتیب برچسب‌ها، ویژگی‌ای که از آینده محاسبه شده، یا مسیر دیگری در مدل می‌تواند جداگانه نشت بسازد؛ باید کل خط لوله را بر اساس قرارداد مسئله آزمود.

## ۷. آزمون قوی‌تر از نگاه‌کردن به ماسک: تغییر آینده

آزمون وزن‌ها بررسی می‌کند که خانه‌های `j>i` صفر باشند؛ آزمون مداخله‌ای، رفتار لایه را هم می‌سنجد: ورودی را تا موقعیت `k−1` ثابت نگه می‌داریم، مقدار موقعیت‌های `k` به بعد را به‌شدت عوض می‌کنیم و خروجی‌های موقعیت‌های کمتر از `k` را مقایسه می‌کنیم. در لایهٔ مستقلِ علّی و بدون dropout، خروجی‌های قبلی نباید تغییر کنند؛ وزن‌های قبلی هم نباید به کلیدهای آینده حساس باشند.

این آزمون در پروژه با seed ثابت و CPU اجرا می‌شود. هم تغییر خروجی و هم تغییر وزن را بررسی می‌کند؛ آزمون دیگری می‌سنجد که تغییر ورودیِ جاری می‌تواند بر خروجی همان موقعیت اثر بگذارد تا تست عدم نشت، مدل کاملاً بی‌اثر را به‌اشتباه تأیید نکند. این سنجش شواهدی برای همین پیاده‌سازی و ورودی‌هاست، نه اثبات امنیت یا صحت همهٔ پشتهٔ یک مدل زبانی.

## ۸. کد: از projection تا خروجی هر سر

پروژه `book-engineering/projects/35-self-attention/` ماژول را با `nn.Linear` می‌سازد و امتیاز، ماسک، softmax، جمع وزن‌دار و الحاق را آشکار نگه می‌دارد. `weights` را هم برمی‌گرداند تا آزمون‌ها بتوانند خانه‌های آینده را وارسی کنند. برای آموزش این انتخاب روشنگر است؛ در مدل production ممکن است API بهینه‌شده وزن‌ها را برنگرداند و kernelهای fused مسیر دیگری داشته باشند.

یک نکته دربارهٔ APIها: در مستندات نسخهٔ 2.6، ماسک بولی `torch.nn.functional.scaled_dot_product_attention` با `True` یعنی موقعیت **مجاز**؛ در `torch.nn.MultiheadAttention`، ماسک بولی `attn_mask` با `True` یعنی موقعیت **غیرمجاز** [۲، ۳]. یعنی در اولی برای دید علّی `tril` را به عنوان ماسک مجاز می‌دهیم، اما در دومی می‌توان مثلث بالای قطر را به عنوان خانهٔ مسدود داد. قرارداد را بر اساس همان API و نسخه بخوانید؛ یک ماسک را بی‌تبدیل میان دو تابع جابه‌جا نکنید.

در API سطح‌بالا نمونهٔ زیر از `nn.MultiheadAttention` استفاده می‌کند. `need_weights=False` برای مسیری که وزن‌ها لازم نیست، اجازه می‌دهد پیاده‌سازی به SDPA بهینه‌شده متکی باشد؛ رفتار و سرعت بسته به backend است. `is_causal` در مستندات MHA نسخهٔ 2.6 یک hint است و hint نادرست می‌تواند اجرای نادرست ایجاد کند؛ بنابراین در کد واقعی از ماسک درست و قرارداد مستند همان نسخه استفاده کنید [۲].

```python
import torch
from torch import nn

batch, length, d_model, heads = 2, 5, 8, 2
x = torch.randn(batch, length, d_model)
blocked_future = torch.ones(length, length, dtype=torch.bool).triu(diagonal=1)
mha = nn.MultiheadAttention(d_model, heads, batch_first=True)
output, _ = mha(x, x, x, attn_mask=blocked_future, need_weights=False)
print(tuple(output.shape))  # (2, 5, 8)
```

در تابع SDPA، معنای بولی برعکس است. این نمونه فقط یک mask را به F.scaled_dot_product_attention می‌دهد؛ `True` در مثلث پایین به معنی شرکت‌کردن در attention است:

```python
import torch
import torch.nn.functional as F

batch, heads, length, head_dim = 2, 3, 5, 4
q = torch.randn(batch, heads, length, head_dim)
k = torch.randn_like(q)
v = torch.randn_like(q)
allowed = torch.ones(length, length, dtype=torch.bool).tril()
y = F.scaled_dot_product_attention(q, k, v, attn_mask=allowed, dropout_p=0.0)
print(tuple(y.shape))  # (2, 3, 5, 4)
```

در نسخهٔ 2.6، تابع SDPA در صورت `dropout_p>0` dropout اعمال می‌کند؛ برای inference باید `dropout_p=0.0` بدهید. این تابع در همان مستندات beta اعلام شده و بسته به ورودی/backend می‌تواند kernel بهینه را انتخاب کند [۳]. ما در پروژه، dropout را اصلاً به کار نبرده‌ایم.

## ۹. هزینه و مرزهای مدل آموزشی

با `h` سر و طول `L`، ماتریس‌های امتیاز و وزن هر سر `L×L` هستند. در نسخهٔ denseِ این فصل، ماسک علّی پس از محاسبهٔ `QKᵀ` اعمال می‌شود؛ پس صرفِ ماسک در کد آموزشی، محاسبهٔ همهٔ زوج‌های موقعیت را حذف نمی‌کند. مشخصه‌های kernel بهینه و نسبت کار به حافظه به device، dtype، طول و نسخه بستگی دارد. به همین علت اندازه‌گیری زمان یک CPU کوچک را به GPU یا مدل واقعی تعمیم نمی‌دهیم [۱، ۳].

این پروژه همچنین **position encoding**، padding، dropout، Residual، LayerNorm، FFN، target shift، KV Cache، cross-attention و آموزش مدل را ندارد. position در فصل ۳۶ می‌آید؛ معماری کامل Decoder و تولید توکن موضوع فصل‌های بعدی نقشه است. اعداد و شکل‌های تمرین فقط برای توضیح و آزمون‌اند.

## ۱۰. تمرین‌ها و معیار عبور

1. برای `L=4`، ماتریس مجاز و ممنوع را با اندیس‌های صفر تا سه رسم کنید. دقیقاً مشخص کنید موقعیت ۱ چه ستون‌هایی را می‌بیند.
2. اگر `d_model=12` و `h=3` باشد، `d_h` چیست؟ شکل `Q` پس از projection، پس از reshape و ماتریس وزن چندسری را برای batch با اندازهٔ ۲ بنویسید.
3. چرا استفاده از `X` برای ساختن هر سه `Q/K/V` به‌تنهایی کافی نیست تا آینده بسته شود؟ چه قیدی باید بر softmax یا امتیازها اعمال شود؟
4. در `nn.MultiheadAttention` و `F.scaled_dot_product_attention`، مقدار True در ماسک بولی هرکدام چه معنایی دارد؟ یک test کوتاه بنویسید که از اشتباه علامت جلوگیری کند.
5. ورودی‌های موقعیت‌های ۴ و ۵ را عوض کنید. کدام خروجی‌ها باید ثابت بمانند؟ چرا آزمون «همهٔ خروجی‌ها ثابت‌اند» آزمون مناسبی نیست؟
6. چرا کاهش attention وزن‌دار به یک ماتریس `L×L` به معنای حذف هزینهٔ `L²` نیست؟ تفاوت ماسک اطلاعاتی و kernel sparse/بهینه را با زبان خود توضیح دهید.

**معیار عبور:** بتوانید شکل‌های `B×h×L×d_h` و `B×h×L×L` را درست دنبال کنید؛ با دست نشان دهید `j>i` مسدود است؛ ده تست پروژه را اجرا کنید؛ و دست‌کم یک آزمونِ تغییر آینده/ثبات گذشته را خودتان بازتولید کنید. پاسخ‌های تشریحی را پس از تلاش مستقل در [جواب‌نامهٔ فصل ۳۵](book-engineering/answers/35-self-attention-fa.md) ببینید. [پروژه و آزمون‌ها](book-engineering/projects/35-self-attention/README.md)

## ۱۱. جمع‌بندی

- در Self-Attention، `Q/K/V` از یک توالی ساخته می‌شوند؛ در cross-attention مبدأ Query و مبدأ Key/Value می‌توانند متفاوت باشند.
- در Multi-Head، projection هر سر جداست؛ نتایج در محور ویژگی الحاق و با `W_O` ترکیب می‌شوند.
- در ماسک علّی، موقعیت `i` فقط `j≤i` را می‌بیند. مثلث درست و قرارداد mask API را پیش از اجرا بررسی کنید.
- وزن آینده صفر، آزمون عدم نشت مفیدی است؛ تغییر ورودی‌های آینده و ثبات خروجی‌های گذشته آزمون مداخله‌ای مکملی است.
- ماسک علّی با padding mask فرق دارد و به‌تنهایی خط لولهٔ آموزش خودرگرسیو را کامل نمی‌کند.

## ۱۲. منابع بیرونی

1. Ashish Vaswani et al. “Attention Is All You Need.” NeurIPS 2017؛ arXiv:1706.03762، نسخهٔ نخست ۱۲ ژوئن ۲۰۱۷ و نسخهٔ بازنگری‌شدهٔ v7 در ۲ اوت ۲۰۲۳. [متن arXiv](https://arxiv.org/abs/1706.03762) · [نسخهٔ HTML v7](https://arxiv.org/html/1706.03762v7) · [نسخهٔ NeurIPS](https://papers.neurips.cc/paper/7181-attention-is-all-you-need.pdf). بخش‌های 3.2.2 و 3.2.3 برای Multi-Head، self-attention و ماسک علّی؛ بخش 4 برای هزینهٔ Self-Attention.
2. PyTorch. “`torch.nn.MultiheadAttention`.” مستندات نسخهٔ 2.6. [صفحهٔ رسمی API](https://docs.pytorch.org/docs/2.6/generated/torch.nn.MultiheadAttention.html). شکل ورودی، `attn_mask`، `is_causal` و رفتار `need_weights`.
3. PyTorch. “`torch.nn.functional.scaled_dot_product_attention`.” مستندات نسخهٔ 2.6. [صفحهٔ رسمی API](https://docs.pytorch.org/docs/2.6/generated/torch.nn.functional.scaled_dot_product_attention.html). ماسک بولی، `is_causal`, dropout و انتخاب kernel.

**تاریخ دسترسی به منابع برخط: ۵ نوامبر ۲۰۲۶.** قواعد ماسک در این فصل به نسخهٔ مشخص PyTorch 2.6 ارجاع دارند؛ نسخهٔ اجرایی پروژه و نسخهٔ production را هنگام استفاده کنترل کنید.

## پیوست: کد کامل پروژه

این همان `causal_multihead.py` است که پروژه و آزمون‌ها اجرا می‌کنند؛ تمام فرض‌های آن در بالای فایل و README ثبت شده‌اند.

```python
"""Explicit causal multi-head self-attention for chapter 35."""
from __future__ import annotations

import math
import torch
from torch import nn


class CausalMultiHeadSelfAttention(nn.Module):
    """Batch-first, fixed-length, causal self-attention with visible weights.

    Input/output: [batch, sequence, d_model]
    Returned weights: [batch, heads, query_position, key_position]

    This teaching module has no positional encoding, padding mask, or dropout.
    """

    def __init__(self, d_model: int, num_heads: int) -> None:
        super().__init__()
        if isinstance(d_model, bool) or not isinstance(d_model, int):
            raise TypeError("d_model must be an integer")
        if isinstance(num_heads, bool) or not isinstance(num_heads, int):
            raise TypeError("num_heads must be an integer")
        if d_model <= 0 or num_heads <= 0:
            raise ValueError("d_model and num_heads must be positive")
        if d_model % num_heads != 0:
            raise ValueError("d_model must be divisible by num_heads in this design")

        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=False)
        self.out_proj = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        if not isinstance(x, torch.Tensor):
            raise TypeError("x must be a torch.Tensor")
        if x.ndim != 3:
            raise ValueError("expected [batch, sequence, d_model] input")
        if not x.is_floating_point():
            raise TypeError("x must have floating-point dtype")
        if x.size(-1) != self.d_model:
            raise ValueError("input feature dimension must equal d_model")
        if x.size(1) == 0:
            raise ValueError("sequence length must be positive")
        if x.device != self.q_proj.weight.device:
            raise ValueError("input and module must be on the same device")
        if x.dtype != self.q_proj.weight.dtype:
            raise TypeError("input and module must use the same dtype")

        batch, length, _ = x.shape
        # Each projection has a separate learned parameter matrix; reshape splits
        # its output into head channels, then transpose puts heads before length.
        query = self.q_proj(x).view(batch, length, self.num_heads, self.head_dim).transpose(1, 2)
        key = self.k_proj(x).view(batch, length, self.num_heads, self.head_dim).transpose(1, 2)
        value = self.v_proj(x).view(batch, length, self.num_heads, self.head_dim).transpose(1, 2)

        scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(self.head_dim)
        # At query position i, only key positions j <= i are visible.
        allowed = torch.ones(length, length, dtype=torch.bool, device=x.device).tril()
        scores = scores.masked_fill(~allowed, float("-inf"))
        weights = torch.softmax(scores, dim=-1)
        per_head = torch.matmul(weights, value)
        concatenated = per_head.transpose(1, 2).contiguous().view(batch, length, self.d_model)
        return self.out_proj(concatenated), weights


def main() -> None:
    torch.manual_seed(3501)
    model = CausalMultiHeadSelfAttention(d_model=8, num_heads=2).eval()
    x = torch.randn(1, 5, 8)
    output, weights = model(x)
    future = weights.triu(diagonal=1)
    print("device=cpu")
    print("input_shape=", tuple(x.shape))
    print("output_shape=", tuple(output.shape))
    print("per_head_weights_shape=", tuple(weights.shape))
    print("max_future_weight=", future.abs().max().item())


if __name__ == "__main__":
    main()
```