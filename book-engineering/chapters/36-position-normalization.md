# جلد سوم، فصل ۴ — موقعیت، RoPE، اتصال باقیمانده، LayerNorm و FFN

**The Art & Science of Building Intelligence | Babak & Ai | فصل سراسری ۳۶ از نقشهٔ پنج‌جلدی**

**تاریخ بازبینی منابع: ۵ نوامبر ۲۰۲۶؛ منابع برخط در همین تاریخ بازبینی شدند.**

## ۱. مسئلهٔ نظم: attention واژهٔ «قبل» را از خود بردار نمی‌خواند

ضرب‌های `QKᵀ` می‌گویند نمایش دو موقعیت چقدر با هم سازگار است؛ اما به‌تنهایی نمی‌گویند یکی پیش از دیگری آمده است. Self-Attention کامل با وزن‌های مشترک، وقتی نشانهٔ جایگاه و ماسک وابسته به اندیس ندارد، نسبت به جابه‌جایی توکن‌های ورودی **هم‌وردا** است: اگر ورودی را جابه‌جا کنیم، خروجی‌ها نیز به همان آرایش جابه‌جا می‌شوند. لایه هنوز نمی‌تواند از خود بردارها بفهمد کدام واژه اول بوده است. در مسئلهٔ زبانی، فرق «گربه دنبال سگ رفت» و «سگ دنبال گربه رفت» اهمیت دارد؛ پس معماری باید اطلاعات موقعیت را به نمایش یا محاسبهٔ attention برساند [۱].

این اطلاعات را نباید با معنا یا ترتیب زمانیِ برچسب‌ها یکی گرفت. مدل فقط یک قرارداد عددی می‌گیرد؛ یادگیری رابطهٔ زبانی کار داده و وزن‌های آموزش‌دیده است. اگر ترتیب در وظیفه مهم نباشد، یا موقعیت‌ها در داده با قرارداد متفاوتی تعریف شوند، همان انتخاب ممکن است مناسب نباشد.

**پیش‌نیاز:** شکل‌های `B×L×d_model` و `Q/K/V` از فصل‌های ۳۴–۳۵، ضرب ماتریسی و توابع از جلدهای پیشین. **هدف:** سه خانوادهٔ موقعیت را از هم تمیز دهید؛ تفاوت جمع‌کردن `PE` با چرخاندن `Q/K` را توضیح دهید؛ مسیر باقیمانده و جایگاه `LayerNorm` را دنبال کنید؛ و FFN را از زیرلایه‌ای که موقعیت‌ها را با هم ترکیب می‌کند تشخیص دهید.

![شکل ۳-۴-۱ — PE سینوسی به embedding جمع می‌شود؛ در RoPE زوج‌های Q و K با زاویهٔ موقعیت می‌چرخند و V دست‌نخورده می‌ماند. بلوک Pre-LN دو مسیر residual دارد، LayerNorm روی ویژگی‌ها عمل می‌کند و FFN هر موقعیت را با وزن مشترک پردازش می‌کند.](assets/images/babak-ai/v3-ch04-position-block.webp)

**شکل ۳-۴-۱ — موقعیت و بلوک.** در نمودار بالا دو راه متفاوت برای تزریق ترتیب آمده‌اند. پایین، attention و FFN زیرلایه‌های جدا با مسیرهای باقیمانده‌اند. بلوک تصویرشده Pre-LN است؛ مدل‌های دیگر ممکن است ترتیب LayerNorm را عوض کنند.

## ۲. سه خانوادهٔ پاسخ به مسئلهٔ موقعیت

سه قرارداد پرکاربرد را از هم جدا کنیم:

| خانواده | محل تزریق اطلاعات | نمونه | محدودیت کلیدی |
|---|---|---|---|
| مطلقِ آموختنی | بردار وابسته به هر جایگاه به embedding اضافه می‌شود | جدول `P[pos]` | جدول طول بیشینهٔ معینی دارد؛ خارج آن نیازمند تصمیم تازه است |
| مطلقِ ثابت | بردار تابعی از شمارهٔ موقعیت به embedding اضافه می‌شود | سینوسیِ Transformer اولیه | پارامتر یادگرفتنی ندارد، اما تعمیم به طول‌های خیلی دور تضمین نیست |
| نسبی/چرخشی | رابطهٔ جایگاه در score یا بردارهای `Q/K` وارد می‌شود | RoPE | فرکانس، scaling و الگوی آموزش بر طول مؤثرند |

این دسته‌بندی ساده است؛ طرح‌های واقعی می‌توانند ترکیبی باشند. دو ردیف اول معمولاً «افزودن بردار» به stream بازمانده را نشان می‌دهند؛ RoPE به جای افزودن یک جدول به `X`، جفت مؤلفه‌های پرس‌وجو و کلید را می‌چرخاند.

## ۳. کدگذاری سینوسی: موقعیت به اندازهٔ بُعد ویژگی

در Transformer اولیه، برای هر موقعیت `pos` یک بردار با همان بُعد embedding ساخته و به آن جمع می‌شد. مؤلفه‌های زوج و فرد موج‌هایی با فرکانس‌های متفاوت‌اند:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="پی ای در موقعیت پوز و بعد دو آی، سینوس پوز تقسیم بر ده هزار به توان دو آی تقسیم بر دی مدل؛ در بعد دو آی به علاوه یک، کسینوس همان زاویه"><mrow><msub><mi>PE</mi><mrow><mi>pos</mi><mo>,</mo><mn>2</mn><mi>i</mi></mrow></msub><mo>=</mo><mi>sin</mi><mo>(</mo><mfrac><mi>pos</mi><msup><mn>10000</mn><mfrac><mrow><mn>2</mn><mi>i</mi></mrow><msub><mi>d</mi><mi>model</mi></msub></mfrac></msup></mfrac><mo>)</mo><mo>,</mo><mspace width="1em"/><msub><mi>PE</mi><mrow><mi>pos</mi><mo>,</mo><mn>2</mn><mi>i</mi><mo>+</mo><mn>1</mn></mrow></msub><mo>=</mo><mi>cos</mi><mo>(</mo><mfrac><mi>pos</mi><msup><mn>10000</mn><mfrac><mrow><mn>2</mn><mi>i</mi></mrow><msub><mi>d</mi><mi>model</mi></msub></mfrac></msup></mfrac><mo>)</mo></mrow></math>

متن جایگزین فرمول: `PE[pos,2i]=sin(pos/10000^(2i/d_model))` و `PE[pos,2i+1]=cos(pos/10000^(2i/d_model))`.

زوج sin/cos برای یک فرکانس یک سیگنال دورانی می‌سازند؛ فرکانس‌های پایین و بالا به فاصله‌های متفاوت حساس‌اند. در `pos=0` همهٔ مؤلفه‌های زوج صفر و مؤلفه‌های فرد یک‌اند. اگر `E` جدول embedding واژه و `PE` ماتریس جایگاه باشد، ورودی block می‌تواند `X=E+PE` باشد. چون هر دو شکل `B×L×d_model` دارند، جمعشان تعریف‌پذیر است. کد فصل بُعد فرد را هم پشتیبانی می‌کند؛ در آن حالت مؤلفهٔ آخر یک زوج کامل ندارد.

روش ثابت پارامتر موقعیتیِ آموختنی نمی‌افزاید. این مزیت به معنی کیفیت برتر یا توانایی نامحدود برای طول توالی نیست؛ موج‌هایی که مدل در یک دامنه دیده، برای فاصله‌های دور ممکن است رفتاری متفاوت داشته باشند. نسبت پایهٔ ۱۰۰۰۰ هم جزئی از یک طرح است، نه ثابت طبیعت.

## ۴. موقعیت مطلق آموختنی و اطلاعات نسبی

جدول `P∈R^{Lmax×d_model}` می‌تواند برای هر خانه یک بردار جدا بیاموزد؛ نمایش ورودی `E+P` است. یادگیری مستقیم انعطاف می‌دهد، ولی تعداد پارامتر و طول جدول را به `Lmax` وابسته می‌کند. هنگام افزایش طول باید ردیف‌های تازه را چگونه تعیین کنیم؟ مقداردهی تصادفی، درون‌یابی یا تغییر دیگری فرض تازه‌ای وارد می‌کند؛ نتیجه باید دوباره سنجیده شود.

کدگذاری نسبی به جای پرسش «توکن در خانهٔ ۱۷ چه برداری دارد؟» می‌پرسد «دو موقعیت چند گام از هم فاصله دارند؟». خانواده‌های مختلف این فاصله را به امتیاز attention یا ویژگی‌های `Q/K` اضافه می‌کنند. RoPE یکی از روش‌هایی است که شمارهٔ مطلق را در بردارها می‌چرخاند و ضرب داخلی را به فاصلهٔ نسبی حساس می‌کند [۲].

## ۵. RoPE: دوران روی زوج مختصات `Q/K`

بُعد head را به زوج‌های `(2r, 2r+1)` تقسیم می‌کنیم. برای جفت `r`، فرکانس `θ_r=base^(−2r/d_h)` و موقعیت `m` زاویهٔ `mθ_r` می‌سازد. یک جفتِ بردار پرس‌وجو چنین می‌چرخد:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="بردار دو مؤلفه‌ای کیو چرخیده برابر ماتریس چرخش کسینوس و سینوس زاویهٔ ام تتا ضربدر جفت کیو است؛ ضرب داخلی جفت‌های چرخیده به اختلاف ان و ام وابسته می‌شود"><mrow><mo>[</mo><mtable><mtr><mtd><msup><mi>q</mi><mi>R</mi></msup><mo>₍</mo><mi>m</mi><mo>,</mo><mn>2</mn><mi>r</mi><mo>₎</mo></mtd></mtr><mtr><mtd><msup><mi>q</mi><mi>R</mi></msup><mo>₍</mo><mi>m</mi><mo>,</mo><mn>2</mn><mi>r</mi><mo>+</mo><mn>1</mn><mo>₎</mo></mtd></mtr></mtable><mo>]</mo><mo>=</mo><mo>[</mo><mtable><mtr><mtd><mi>cos</mi><mo>(</mo><mi>m</mi><msub><mi>θ</mi><mi>r</mi></msub><mo>)</mo></mtd><mtd><mo>−</mo><mi>sin</mi><mo>(</mo><mi>m</mi><msub><mi>θ</mi><mi>r</mi></msub><mo>)</mo></mtd></mtr><mtr><mtd><mi>sin</mi><mo>(</mo><mi>m</mi><msub><mi>θ</mi><mi>r</mi></msub><mo>)</mo></mtd><mtd><mi>cos</mi><mo>(</mo><mi>m</mi><msub><mi>θ</mi><mi>r</mi></msub><mo>)</mo></mtd></mtr></mtable><mo>]</mo><mo>[</mo><mtable><mtr><mtd><msub><mi>q</mi><mrow><mi>m</mi><mo>,</mo><mn>2</mn><mi>r</mi></mrow></msub></mtd></mtr><mtr><mtd><msub><mi>q</mi><mrow><mi>m</mi><mo>,</mo><mn>2</mn><mi>r</mi><mo>+</mo><mn>1</mn></mrow></msub></mtd></mtr></mtable><mo>]</mo></mrow></math>

متن جایگزین فرمول: `q^R_(m,2r:2r+2)=R(mθ_r)q_(m,2r:2r+2)`؛ همان دوران روی `k_n` هم اعمال می‌شود. سپس `(R(mθ)q)^T(R(nθ)k)=q^T R((n−m)θ)k`.

ماتریس دوران متعامد است، پس norm اقلیدسیِ هر جفت حفظ می‌شود؛ ولی جهتش به موقعیت وابسته است. با استفاده از `R(a)^T R(b)=R(b−a)`، ضرب داخلی `Q` در `m` و `K` در `n` به اختلاف `n−m` حساس می‌شود. این راهِ جبریِ ورود فاصلهٔ نسبی به امتیازهاست؛ معنی واژه یا نتیجهٔ ترجمه را خودش فراهم نمی‌کند [۲].

RoPE در استاندارد آموزشی روی `Q` و `K` اعمال می‌شود، نه `V`. پروژه هم همین قرارداد را آشکار می‌کند. برای زوج‌کردن کانال‌ها، `d_h` باید زوج باشد؛ `d_model` بخش‌پذیر بر تعداد سرها شرط جداگانه‌ای است. برای offsetهای cache یا batch ناهمسان قرارداد موقعیت می‌تواند پیچیده‌تر شود؛ تابع نمونه یک بردار موقعیت مشترک برای batch می‌گیرد.

## ۶. تعمیم طول: جدول ثابت، اما نتیجه همچنان تجربی

جدول آموختنیِ موقعیت یک سقف روشن دارد. کدگذاری سینوسی می‌تواند برای عدد موقعیت بزرگ‌تری محاسبه شود و RoPE هم به جدول آموختنی متکی نیست؛ با این حال «قابل محاسبه بودن» مساوی «تعمیم معتبر مدل» نیست. RoPE با فاصلهٔ زیاد الگوی چرخش متفاوتی می‌سازد؛ روش‌هایی مانند Position Interpolation شماره‌های موقعیت را در بازهٔ آموزش نگه می‌دارند و برای مدل‌های RoPE-based با fine-tuning ارزیابی شده‌اند [۶]. این یک روش مشخص و نتیجهٔ تجربی در تنظیم‌های مطالعه‌شده است، نه تضمین عمومی برای هر مدل یا وظیفه. هر تکنیک باید در context طولانی و روی معیارهای هدف آزموده شود، نه با ادعای خودکارِ «بی‌نهایت طول» [۲]. فصل ۳۸ هزینه و بعضی راهکارهای زمینهٔ بلند را جدا بررسی می‌کند.

## ۷. اتصال باقیمانده: شاخهٔ identity را گم نکن

یک زیرلایه مثل attention یا FFN را `F` و ورودی‌اش را `x` بنامیم. اتصال باقیمانده خروجی `F(x)` را با `x` جمع می‌کند: `x+F(x)`. اگر دو شکل یکی نباشند، جمع ساده تعریف ندارد؛ بنابراین زیرلایه‌های این بلوک خروجی را به `d_model` برمی‌گردانند. این شاخه مسیر مستقیمی برای اطلاعات و گرادیان فراهم می‌کند، اما تضمین نمی‌کند هر یادگیری آسان یا بدون افت است. باید آن را از خودِ attention جدا دید: attention روابط بین موقعیت‌ها را می‌آموزد، residual راه ترکیب ورودی با خروجی را می‌دهد [۱].

در یک block با دو زیرلایه، دو جمعِ جدا وجود دارد: یکی پیرامون self-attention و دیگری پیرامون FFN. تصویر فصل همین مسیر را رسم می‌کند. «Residual» به معنای حفظ اجباری یا برابر ماندن نمایش نیست؛ شاخهٔ آموختنی می‌تواند جمع را تغییر دهد.

## ۸. LayerNorm: نرمال‌سازی ویژگی‌ها برای هر موقعیت

برای بردار `x` روی `D` ویژگی، LayerNorm میانگین و واریانس همان محور را می‌گیرد، سپس مقیاس و bias آموختنی اعمال می‌کند:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="لایه نرمال سازی ایکس برابر ایکس منهای میانگین، تقسیم بر ریشه واریانس به علاوه اپسیلون، ضربدر گاما به علاوه بتا"><mrow><mi>LayerNorm</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>=</mo><mfrac><mrow><mi>x</mi><mo>−</mo><mi>μ</mi></mrow><msqrt><mrow><msup><mi>σ</mi><mn>2</mn></msup><mo>+</mo><mi>ε</mi></mrow></msqrt></mfrac><mo>⊙</mo><mi>γ</mi><mo>+</mo><mi>β</mi></mrow></math>

متن جایگزین فرمول: `y=(x−μ)/sqrt(σ²+ε) ⊙ γ + β`؛ در PyTorch `nn.LayerNorm(d_model)` با ورودی `[B,L,D]` محور آخر `D` را جداگانه برای هر `[b,l]` نرمال می‌کند [۵].

`γ` و `β` شکل `D` دارند و اگر affine فعال باشد آموخته می‌شوند. `ε` برای ثبات عددی افزوده می‌شود. PyTorch 2.6 واریانس biased، معادل `torch.var(..., correction=0)`، به کار می‌برد و آمار را از خود ورودی در train و eval می‌گیرد [۵]. پس unlike BatchNorm به میانگین نمونه‌های batch متکی نیست. انتخاب `normalized_shape` اشتباه می‌تواند ناخواسته ابعاد دیگری را نرمال کند؛ شکل تنسور را با قرارداد API تطبیق دهید.

## ۹. Pre-LN و Post-LN دو ترتیب یکسان نیستند

Transformer اولیه زیرلایه را درون residual جمع می‌کند و بعد LayerNorm می‌زند؛ این فرم **Post-LN** است. در **Pre-LN** اول ورودی زیرلایه نرمال می‌شود و نتیجه با stream باقیمانده جمع می‌شود:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="Post-LN خروجی لایه نرمال سازی ایکس به علاوه اف از ایکس است؛ Pre-LN خروجی ایکس به علاوه اف از لایه نرمال سازی ایکس است"><mrow><msub><mi>y</mi><mtext>Post</mtext></msub><mo>=</mo><mi>LayerNorm</mi><mo>(</mo><mi>x</mi><mo>+</mo><mi>F</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>)</mo><mo>,</mo><mspace width="1em"/><msub><mi>y</mi><mtext>Pre</mtext></msub><mo>=</mo><mi>x</mi><mo>+</mo><mi>F</mi><mo>(</mo><mi>LayerNorm</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>)</mo></mrow></math>

متن جایگزین فرمول: `Post-LN: LN(x+F(x))`; `Pre-LN: x+F(LN(x))`.

قرارگیری LayerNorm، مسیر گرادیان را عوض می‌کند. تحلیل Xiong و همکاران دربارهٔ warmup و اندازهٔ گرادیان در Post-LN/Pre-LN، به فرض‌ها و تنظیم‌های بررسی‌شده مربوط است؛ از آن نباید نتیجه گرفت که Pre-LN همیشه در تمام وظایف برنده است [۴]. بعضی Pre-LN معماری‌ها پیش از سر خروجی LayerNorm نهایی می‌افزایند. این پروژه دو ترتیب یک زیرلایه را نشان می‌دهد؛ آن یک معماری GPT کامل نیست.

## ۱۰. شبکهٔ پیش‌خورِ موقعیت‌مند (FFN)

پس از attention، Transformer برای هر موقعیت یک MLP با وزن مشترک میان موقعیت‌ها اعمال می‌کند. ورودی و خروجی `D` بُعد دارند و میانه می‌تواند `d_ff` باشد:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="اف اف ان از ایکس برابر دبلیو دو، فعال ساز از دبلیو یک ایکس به علاوه بی یک، به علاوه بی دو؛ برای موقعیت‌های مختلف وزن‌ها مشترک‌اند"><mrow><mi>FFN</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>=</mo><msub><mi>W</mi><mn>2</mn></msub><mi>φ</mi><mo>(</mo><msub><mi>W</mi><mn>1</mn></msub><mi>x</mi><mo>+</mo><msub><mi>b</mi><mn>1</mn></msub><mo>)</mo><mo>+</mo><msub><mi>b</mi><mn>2</mn></msub></mrow></math>

متن جایگزین فرمول: `FFN(x)=W₂ φ(W₁x+b₁)+b₂`. در یک لایه، ماتریس‌های `W₁/W₂` برای همهٔ ردیف‌های `X` مشترک‌اند؛ اما لایه‌های مختلف پارامترهای جدا دارند [۱].

در مقالهٔ ۲۰۱۷ فعال‌ساز ReLU و inner dimension برابر `4d_model` در پیکربندی پایه بود. در مدل‌های دیگر GELU یا فعال‌سازهای دیگر و اندازه‌های متفاوت هم رایج‌اند؛ پروژه برای نمونه GELU و `d_ff=4d_model` را پیش‌فرض می‌گیرد. FFN خودش موقعیت‌ها را مخلوط نمی‌کند؛ می‌توان آن را یک تبدیل ویژگیِ جداگانه و یکسان برای هر ردیف دانست.

## ۱۱. دو زیرلایه کنار هم: یک block کوچک

در حالت Pre-LN که پروژه برای نمونه انتخاب می‌کند:

```text
x₁ = x₀ + SelfAttention(LN₁(x₀))
x₂ = x₁ + FFN(LN₂(x₁))
```

در روش سینوسی، `PE` به جریان ورودی اضافه می‌شود و attention از آن `Q/K/V` می‌سازد. در روش RoPE، دوران درون attention و فقط روی `Q/K` انجام می‌شود. پس از آن مسیر residual، LayerNorm و FFN در هر دو حالت شکل یکسانی دارند. این جداسازی کمک می‌کند بپرسیم تغییر نتیجه از encoding آمده یا از چینش زیرلایه‌ها.

این block در پروژه encoder-style و دوسویه است: علّی‌بودن و padding mask ندارد؛ فصل ۳۵ ماسک علّی را بررسی کرد و فصل ۳۷ تفاوت encoder و decoder را دنبال می‌کند. با این تحدید دامنه، آزمون‌های position و residual با ماسک آینده اشتباه نمی‌شوند.

## ۱۲. پروژهٔ قابل اجرا و آزمون‌های تمایزبخش

در `book-engineering/projects/36-position-normalization/` سه قطعه جداست: تابع sinusoidal، تابع RoPE برای `[B,H,L,d_h]`، و `PositionAwareTransformerBlock`. کد شکل attention، تقسیم سرها و residualها را آشکار می‌کند. بلوک تنها یک لایه است، از تمام موقعیت‌ها استفاده می‌کند و dropout ندارد؛ انتظار inference و آموزش مدل واقعی از آن نداشته باشید.

ده آزمون، شکل‌ها و موقعیت صفر را بررسی می‌کنند؛ RoPE norm را حفظ می‌کند و dot product برای دو فاصلهٔ مساوی یکسان می‌ماند؛ هر دو حالت موقعیت و هر دو ترتیب LayerNorm خروجی هم‌شکل می‌دهند؛ و گرادیان ورودی و وزن‌ها متناهی است. دستورها و خروجی نمونه در README پروژه‌اند؛ پاسخ تمرین‌ها نیز جداست تا پاسخ در متن فصل جلوتر از یادگیرنده نیاید.

## ۱۳. تمرین‌ها و معیار عبور

1. اگر ورودی یک self-attention بدون موقعیت جابه‌جا شود، چرا خروجی فقط جابه‌جا می‌شود؟ واژهٔ «هم‌وردا» را با مثال توضیح دهید.
2. برای `d_model=4` و `pos=0` مقادیر زوج و فرد PE را بنویسید. سپس برای `pos=1` فرمول را باز کنید.
3. تفاوت جدول آموختنیِ `P[pos]` و کدگذاری سینوسی را در تعداد پارامتر و طول خارج از دامنه مقایسه کنید؛ چرا از هیچ‌کدام تضمین طول دلخواه نتیجه نمی‌شود؟
4. RoPE کدام بردارها را می‌چرخاند؟ چرا norm حفظ می‌شود و فاصلهٔ نسبی چگونه وارد dot product می‌شود؟
5. `Pre-LN` و `Post-LN` را با فرمول بنویسید. اگر `[B,L,D]` داریم، `LayerNorm(D)` روی کدام محور آمار می‌گیرد؟
6. FFN چه تفاوتی با attention دارد؟ چرا عبارت «موقعیت‌مند» در اینجا به معنی داشتن embedding جایگاه اختصاصی نیست؟

**معیار عبور:** ده آزمون پروژه را اجرا کنید؛ بتوانید با شکل `B×H×L×d_h` محل RoPE را نشان دهید؛ شکل دو جمع residual را ترسیم کنید؛ و تفاوت Pre/Post-LN را بدون ادعای برتری همیشگی بیان کنید. پاسخ تشریحی را پس از تلاش مستقل در [جواب‌نامهٔ فصل ۳۶](book-engineering/answers/36-position-normalization-fa.md) ببینید. [پروژه و آزمون‌ها](book-engineering/projects/36-position-normalization/README.md)

## ۱۴. جمع‌بندی

- بدون نشانهٔ موقعیت، self-attention نسبت به جایگشت هم‌ورداست؛ ترتیب باید وارد نمایش یا امتیاز شود.
- PE سینوسی و learned absolute به embedding افزوده می‌شوند؛ RoPE جفت‌های `Q/K` را می‌چرخاند و `V` را دست‌نخورده می‌گذارد.
- ماتریس دوران norm را حفظ می‌کند و dot product را به اختلاف موقعیت‌ها وابسته می‌کند؛ تعمیم به طول بیشتر همچنان باید سنجیده شود.
- Residual و LayerNorm دو کار متفاوت دارند؛ جای LayerNorm پیش یا پس از زیرلایه، یک انتخاب معماری است.
- FFN موقعیت‌به‌موقعیت اعمال می‌شود و وزن‌های همان لایه را میان موقعیت‌ها به اشتراک می‌گذارد؛ attention ارتباط میان موقعیت‌ها را می‌سازد.

### واژه‌نامهٔ کوتاه

- **کدگذاری مکانی (positional encoding):** نشانه‌ای از ترتیب موقعیت‌ها به نمایش ورودی.
- **RoPE:** چرخش وابسته به موقعیت در زوج مؤلفه‌های Query و Key.
- **اتصال باقیمانده (residual):** جمع ورودی زیرلایه با خروجی آن در مسیر بلوک.
- **LayerNorm:** نرمال‌سازی ویژگی‌ها در هر نمونه بر اساس محور تعریف‌شده.
- **FFN:** شبکهٔ پیش‌خورِ موقعیتی که پس از attention روی نمایش‌ها اعمال می‌شود.

## ۱۵. منابع بیرونی

1. Ashish Vaswani et al. “Attention Is All You Need.” NeurIPS 2017؛ arXiv:1706.03762، نسخهٔ v7 مورخ ۲ اوت ۲۰۲۳. [متن arXiv](https://arxiv.org/abs/1706.03762) · [نسخهٔ HTML v7](https://arxiv.org/html/1706.03762v7). بخش‌های 3.3، 3.5 و 5.4 برای FFN، positional encoding و regularization؛ بخش 3.1 برای residual و LayerNorm.
2. Jianlin Su et al. “RoFormer: Enhanced Transformer with Rotary Position Embedding.” arXiv:2104.09864، نسخهٔ v5 مورخ ۸ نوامبر ۲۰۲۳. [متن arXiv](https://arxiv.org/abs/2104.09864) · [HTML v5](https://arxiv.org/html/2104.09864v5).
3. Jimmy Lei Ba, Jamie Ryan Kiros, Geoffrey E. Hinton. “Layer Normalization.” arXiv:1607.06450, 2016. [arXiv](https://arxiv.org/abs/1607.06450).
4. Ruibin Xiong et al. “On Layer Normalization in the Transformer Architecture.” ICML 2020; arXiv:2002.04745, v2 dated 29 June 2020. [arXiv](https://arxiv.org/abs/2002.04745) · [HTML v2](https://arxiv.org/html/2002.04745v2).
5. PyTorch 2.6.0. [`torch.nn.LayerNorm`](https://docs.pytorch.org/docs/2.6/generated/torch.nn.LayerNorm.html). `normalized_shape`، آخرین محورهای نرمال‌شده، `eps`، `elementwise_affine` و نوع واریانس.
6. Shouyuan Chen et al. “Extending Context Window of Large Language Models via Position Interpolation.” arXiv:2306.15595, v2 dated 28 June 2023. [arXiv](https://arxiv.org/abs/2306.15595) · [HTML v2](https://arxiv.org/html/2306.15595).

**تاریخ دسترسی به منابع برخط: ۵ نوامبر ۲۰۲۶.** فرمول‌های سینوسی و RoPE در متن با نسخه‌های ارجاع‌شده تطبیق داده شدند؛ رفتار API در پیاده‌سازی به PyTorch 2.6 ارجاع دارد. نتیجهٔ Position Interpolation به همان مقاله و تنظیم‌های ارزیابی‌شده محدود است.

## پیوست: کد کامل پروژه

کد زیر همان `transformer_block.py` پروژه است؛ پیاده‌سازی و محدودیت‌ها در README ثبت شده‌اند.


```python
"""Position schemes and a compact Transformer block for volume 3 chapter 36."""
from __future__ import annotations

import math

import torch
from torch import nn


def _positive_int(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def sinusoidal_encoding(
    length: int,
    d_model: int,
    *,
    positions: torch.Tensor | None = None,
    device: torch.device | str | None = None,
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    """Return [length, d_model] sinusoidal absolute position encodings.

    Odd model dimensions are supported; the last even coordinate simply has no
    paired odd coordinate. Positions are shared by all examples in the batch.
    """
    _positive_int("length", length)
    _positive_int("d_model", d_model)
    if not isinstance(dtype, torch.dtype) or not dtype.is_floating_point:
        raise TypeError("dtype must be a floating-point torch.dtype")

    if positions is None:
        pos = torch.arange(length, device=device, dtype=torch.int64)
    else:
        pos = torch.as_tensor(positions, device=device)
        if pos.ndim != 1 or pos.numel() != length:
            raise ValueError("positions must be a rank-1 vector with one value per token")
        if pos.dtype == torch.bool or pos.is_floating_point() or pos.is_complex():
            raise TypeError("positions must use an integer dtype")
        if torch.any(pos < 0).item():
            raise ValueError("positions must be non-negative")

    work_dtype = torch.float64 if dtype == torch.float64 else torch.float32
    pos = pos.to(dtype=work_dtype).unsqueeze(1)
    pair_indices = torch.arange(0, d_model, 2, device=pos.device, dtype=work_dtype)
    frequencies = torch.exp(pair_indices * (-math.log(10000.0) / d_model))
    angles = pos * frequencies.unsqueeze(0)

    encoding = torch.zeros(length, d_model, device=pos.device, dtype=work_dtype)
    encoding[:, 0::2] = torch.sin(angles)
    odd_count = encoding[:, 1::2].shape[1]
    if odd_count:
        encoding[:, 1::2] = torch.cos(angles[:, :odd_count])
    return encoding.to(dtype=dtype)


def apply_rope(
    x: torch.Tensor,
    positions: torch.Tensor | None = None,
    *,
    base: float = 10000.0,
) -> torch.Tensor:
    """Apply RoPE to [batch, heads, length, head_dim] query/key vectors.

    Coordinates are paired as (0,1), (2,3), ... . RoPE rotates queries and
    keys, not values. The teaching implementation uses one shared position
    vector for the batch and requires an even head dimension.
    """
    if not isinstance(x, torch.Tensor):
        raise TypeError("x must be a torch.Tensor")
    if x.ndim != 4:
        raise ValueError("expected [batch, heads, length, head_dim] input")
    if not x.is_floating_point():
        raise TypeError("x must have floating-point dtype")
    if x.size(-1) == 0 or x.size(-1) % 2:
        raise ValueError("head_dim must be a positive even integer for RoPE")
    if isinstance(base, bool) or not isinstance(base, (int, float)):
        raise TypeError("base must be a positive finite number")
    if not math.isfinite(base) or base <= 0:
        raise ValueError("base must be a positive finite number")

    length, head_dim = x.size(-2), x.size(-1)
    if length == 0:
        raise ValueError("sequence length must be positive")
    if positions is None:
        pos = torch.arange(length, device=x.device, dtype=torch.int64)
    else:
        pos = torch.as_tensor(positions, device=x.device)
        if pos.ndim != 1 or pos.numel() != length:
            raise ValueError("positions must be a rank-1 vector with one value per token")
        if pos.dtype == torch.bool or pos.is_floating_point() or pos.is_complex():
            raise TypeError("positions must use an integer dtype")
        if torch.any(pos < 0).item():
            raise ValueError("positions must be non-negative")

    work_dtype = torch.float64 if x.dtype == torch.float64 else torch.float32
    pair_indices = torch.arange(0, head_dim, 2, device=x.device, dtype=work_dtype)
    inv_freq = torch.exp(pair_indices * (-math.log(float(base)) / head_dim))
    angles = pos.to(dtype=work_dtype).unsqueeze(1) * inv_freq.unsqueeze(0)
    cos = angles.cos().to(dtype=x.dtype)[None, None, :, :]
    sin = angles.sin().to(dtype=x.dtype)[None, None, :, :]

    even, odd = x[..., 0::2], x[..., 1::2]
    rotated = torch.empty_like(x)
    rotated[..., 0::2] = even * cos - odd * sin
    rotated[..., 1::2] = even * sin + odd * cos
    return rotated


class PositionAwareTransformerBlock(nn.Module):
    """Single batch-first, full self-attention block with visible sublayers.

    `position_mode` is either `sinusoidal` (add to the residual stream) or
    `rope` (rotate Q and K). `norm_order` is `pre` or `post`. This block has no
    causal/padding mask or dropout; it is an encoder-style teaching example.
    """

    def __init__(
        self,
        d_model: int,
        num_heads: int,
        d_ff: int | None = None,
        *,
        position_mode: str = "sinusoidal",
        norm_order: str = "pre",
        rope_base: float = 10000.0,
    ) -> None:
        super().__init__()
        _positive_int("d_model", d_model)
        _positive_int("num_heads", num_heads)
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        if position_mode not in {"sinusoidal", "rope"}:
            raise ValueError("position_mode must be 'sinusoidal' or 'rope'")
        if norm_order not in {"pre", "post"}:
            raise ValueError("norm_order must be 'pre' or 'post'")
        if position_mode == "rope" and (d_model // num_heads) % 2:
            raise ValueError("RoPE requires an even head_dim")
        if isinstance(rope_base, bool) or not isinstance(rope_base, (int, float)):
            raise TypeError("rope_base must be a positive finite number")
        if not math.isfinite(rope_base) or rope_base <= 0:
            raise ValueError("rope_base must be a positive finite number")

        if d_ff is None:
            d_ff = 4 * d_model
        _positive_int("d_ff", d_ff)
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.position_mode = position_mode
        self.norm_order = norm_order
        self.rope_base = float(rope_base)

        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model),
        )

    def _self_attention(self, x: torch.Tensor, positions: torch.Tensor | None) -> torch.Tensor:
        batch, length, _ = x.shape
        qkv = self.qkv(x).view(batch, length, 3, self.num_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)
        query, key, value = qkv.unbind(dim=0)
        if self.position_mode == "rope":
            query = apply_rope(query, positions, base=self.rope_base)
            key = apply_rope(key, positions, base=self.rope_base)

        scores = query @ key.transpose(-2, -1) / math.sqrt(self.head_dim)
        weights = torch.softmax(scores, dim=-1)
        per_head = weights @ value
        combined = per_head.transpose(1, 2).contiguous().view(batch, length, self.d_model)
        return self.out_proj(combined)

    def forward(self, x: torch.Tensor, positions: torch.Tensor | None = None) -> torch.Tensor:
        if not isinstance(x, torch.Tensor):
            raise TypeError("x must be a torch.Tensor")
        if x.ndim != 3:
            raise ValueError("expected [batch, sequence, d_model] input")
        if not x.is_floating_point():
            raise TypeError("x must have floating-point dtype")
        if x.size(1) == 0:
            raise ValueError("sequence length must be positive")
        if x.size(-1) != self.d_model:
            raise ValueError("input feature dimension must equal d_model")
        if x.device != self.qkv.weight.device:
            raise ValueError("input and module must be on the same device")
        if x.dtype != self.qkv.weight.dtype:
            raise TypeError("input and module must use the same dtype")

        if self.position_mode == "sinusoidal":
            encoding = sinusoidal_encoding(
                x.size(1), self.d_model, positions=positions,
                device=x.device, dtype=x.dtype,
            )
            x = x + encoding.unsqueeze(0)

        if self.norm_order == "pre":
            x = x + self._self_attention(self.norm1(x), positions)
            x = x + self.ffn(self.norm2(x))
        else:
            x = self.norm1(x + self._self_attention(x, positions))
            x = self.norm2(x + self.ffn(x))
        return x


def main() -> None:
    torch.manual_seed(3601)
    x = torch.randn(2, 6, 16)
    model = PositionAwareTransformerBlock(
        d_model=16, num_heads=4, position_mode="rope", norm_order="pre"
    ).eval()
    positions = torch.arange(10, 16)
    with torch.no_grad():
        output = model(x, positions)
    encoding = sinusoidal_encoding(6, 16)
    print("device=cpu")
    print("mode=rope, norm_order=pre")
    print("input_shape=", tuple(x.shape))
    print("output_shape=", tuple(output.shape))
    print("sinusoidal_shape=", tuple(encoding.shape))
    print("output_finite=", torch.isfinite(output).all().item())


if __name__ == "__main__":
    main()
```
