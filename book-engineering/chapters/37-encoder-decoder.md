# جلد سوم، فصل ۵ — Encoder، Decoder و مدل‌های Encoder–Decoder

**The Art & Science of Building Intelligence | Babak & Ai | فصل سراسری ۳۷ از نقشهٔ پنج‌جلدی**

**تاریخ مرجع: ۵ نوامبر ۲۰۲۶؛ منابع برخط در همین تاریخ بازبینی شدند.**

## ۱. سه آرایش، سه قرارداد برای جریان اطلاعات

در فصل‌های ۳۴ تا ۳۶ سازوکار توجه، ماسک علّی و اجزای یک بلوک را دیدیم. اکنون پرسش در مقیاس کل مدل است: **هر موقعیت چه بخش‌هایی از ورودی را می‌بیند و مدل باید چه نوع خروجی‌ای بسازد؟** پاسخ به این پرسش، سه آرایش مشهور را از هم جدا می‌کند: رمزگذارِ تنها (Encoder-only)، رمزگشایِ تنها (Decoder-only) و رمزگذار–رمزگشا (Encoder–Decoder).

نکتهٔ کلیدی این است که این نام‌ها «سه وظیفهٔ غیرقابل‌تغییر» نیستند. معماری، الگوی اتصال و مسیر اطلاعات را توصیف می‌کند؛ هدف پیش‌آموزش، سر خروجی، داده و روش تنظیم برای وظیفه تعیین می‌کنند مدل چه چیزی یاد بگیرد. یک مدل encoder-only معمولاً برای ساخت بازنمایی و برچسب‌گذاری به کار می‌رود؛ decoder-only معمولاً دنباله را ادامه می‌دهد؛ و encoder–decoder معمولاً ورودی را به خروجی متنیِ شرطی تبدیل می‌کند. واژهٔ «معمولاً» مهم است: این‌ها گرایش‌های رایج‌اند، نه ممنوعیت یا تضمین.

**پیش‌نیاز:** شکل `Q/K/V` و Self-Attention در فصل‌های ۳۴–۳۵، موقعیت و بلوک باقیمانده در فصل ۳۶، و بردار/ماتریس از جلدهای پیشین. **هدف:** شکل سه معماری را رسم کنید؛ تفاوت دید دوسویه، ماسک علّی و cross-attention را توضیح دهید؛ و برای یک قرارداد ورودی/خروجی، انتخاب معماری را همراه با محدودیتش توجیه کنید.

![شکل ۳-۵-۱ — مقایسهٔ سه جریان اطلاعات: در Encoder-only هر توکن معتبر به همهٔ توکن‌های ورودی دسترسی دارد و بازنمایی‌ها به سر وظیفه می‌روند؛ در Decoder-only ماتریس علّی فقط گذشته و جایگاه جاری را باز می‌گذارد؛ در Encoder–Decoder خروجی حافظهٔ Encoder با cross-attention به Decoder علّی می‌رسد تا دنبالهٔ هدف ساخته شود. خانهٔ روشن در ماتریس‌ها مجاز است؛ PyTorch برای ماسک بولی قرارداد وارونهٔ True=مسدود دارد.](assets/images/babak-ai/v3-ch05-architecture-matrix.webp)

**شکل ۳-۵-۱ — معماری را از مسیر اطلاعات بخوانید.** خانهٔ روشن در سه ماتریس یعنی دسترسی مجاز. در پنل سوم، ورودی منبع فقط یک بردار خلاصه نیست: Decoder می‌تواند در هر گام به موقعیت‌های حافظهٔ رمزگذار توجه کند. نمونه‌های پایین شکل، وظایف رایج‌اند، نه دسته‌بندی انحصاری.

## ۲. Transformer اصلی: Encoder و Decoder کنار هم

Transformer مقالهٔ اصلی برای **تبدیل یک دنباله به دنباله‌ای دیگر** ساخته شد؛ نمونهٔ مهم آن ترجمه است [۱]. اگر `x` دنبالهٔ منبع و `y` دنبالهٔ هدف باشد، Encoder منبع را به دنباله‌ای از بازنمایی‌های زمینه‌ای تبدیل می‌کند. سپس Decoder با دیدن پیشوندِ هدف و خروجی Encoder، توکن‌های هدف را یکی‌یکی پیش‌بینی می‌کند.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="اچ ای برابر رمزگذار ایکس؛ احتمال وای با شرط ایکس برابر حاصل‌ضرب احتمال هر توکن وای تی با شرط ایکس و توکن‌های پیشین هدف"><mrow><msub><mi>H</mi><mi>E</mi></msub><mo>=</mo><mi>Encoder</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>,</mo><mspace width="1em"/><mi>p</mi><mo>(</mo><mi>y</mi><mo>|</mo><mi>x</mi><mo>)</mo><mo>=</mo><munderover><mo>∏</mo><mrow><mi>t</mi><mo>=</mo><mn>1</mn></mrow><mi>T</mi></munderover><mi>p</mi><mo>(</mo><msub><mi>y</mi><mi>t</mi></msub><mo>|</mo><mi>x</mi><mo>,</mo><msub><mi>y</mi><mrow><mo>&lt;</mo><mi>t</mi></mrow></msub><mo>)</mo></mrow></math>

متن جایگزین فرمول: `H_E=Encoder(x)` و `p(y|x)=∏_{t=1}^T p(y_t | x, y_<t)`. `H_E` حافظهٔ دنباله‌ای است؛ `y_<t` توکن‌های هدف پیش از گام `t` هستند.

در Encoder اصلی، هر لایه Self-Attention روی توکن‌های ورودی و سپس شبکهٔ پیش‌خور موقعیت‌مند دارد. در Decoder اصلی، Self-Attention ماسک علّی می‌گیرد و یک زیرلایهٔ جداگانهٔ **توجه رمزگذار–رمزگشا** (cross-attention) اضافه می‌شود: پرس‌وجوها از حالت‌های Decoder می‌آیند، کلیدها و مقدارها از خروجی Encoder. پس از هر زیرلایه نیز مسیر باقیمانده و LayerNorm قرار دارد [۱]. جزئیات Pre-LN/Post-LN می‌تواند میان پیاده‌سازی‌ها عوض شود؛ فصل ۳۶ این تفاوت را معرفی کرد.

## ۳. Encoder-only: بازنماییِ دنباله با دید دوطرفه

در Encoder دوطرفه، توکن معتبرِ جایگاه `i` می‌تواند برای ساخت بازنمایی خود از توکن‌های پیش و پس از `i` استفاده کند. توجه اینجا **Self-Attention بدون ماسک علّی** است؛ ماسک padding همچنان لازم است تا مدل به جایگاه‌های خالی توجه نکند. هر لایه دنباله‌ای از بردارهای زمینه‌ای `H=[h₁,…,h_L]` تحویل می‌دهد.

BERT نمونهٔ شناخته‌شدهٔ این خانواده است: پیش‌آموزش آن از Masked Language Modeling استفاده می‌کرد تا بازنمایی توکن پنهان‌شده با بافت چپ و راست پیش‌بینی شود؛ مقالهٔ اصلی همچنین هدف Next Sentence Prediction را بررسی می‌کرد [۲]. چون خروجی Encoder برای همهٔ جایگاه‌ها در دسترس است، می‌توان روی آن سرهای متفاوتی گذاشت: طبقه‌بندی جمله، برچسب‌گذاری توکن (مثلاً NER)، پیش‌بینی بازهٔ آغاز/پایان برای پرسش‌وپاسخ استخراجی، یا سرِ بردارسازی که جداگانه برای بازیابی آموزش دیده باشد.

برای طبقه‌بندی جمله، یک پیاده‌سازی ممکن است نمایش `[CLS]` یا میانگینِ نمایش توکن‌های معتبر را به سر خطی بدهد. این دو انتخاب یکی نیستند و هیچ‌کدام به‌تنهایی تضمین نمی‌کنند embedding برای جست‌وجوی معنایی مناسب باشد؛ هدف آموزش و دادهٔ تطبیق‌یافته اهمیت دارند. Encoder-only استاندارد **به‌طور طبیعی** مسیر تولید خودرگرسیوِ یک متن نامحدود ندارد؛ می‌توان سر یا Decoder دیگری به آن افزود، اما آن‌گاه سامانه دیگر صرفاً همان مدل Encoder-only ساده نیست.

## ۴. Decoder-only: هر گام ادامهٔ پیشوند است

در Decoder-only رایج، هر توکن هنگام پیش‌بینی تنها پیشوند تا جایگاه خودش را می‌بیند. ماسک علّی خانه‌های مربوط به آینده را می‌بندد. مدل با هدف خودرگرسیو آموزش می‌بیند: از پیشوند، توکن بعدی را پیش‌بینی کن. GPT-3 نمونه‌ای پژوهشی از مدل زبانی خودرگرسیو است که در مقاله‌اش وظایف گوناگون با دستور و نمونه‌های درون‌متنی بررسی شدند [۳].

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="زیان زبان‌مدل برابر منفی مجموع لگاریتم احتمال توکن بعدی با شرط پیشوند قبلی"><mrow><msub><mi>ℒ</mi><mi>LM</mi></msub><mo>=</mo><mo>−</mo><munderover><mo>∑</mo><mrow><mi>t</mi><mo>=</mo><mn>1</mn></mrow><mrow><mi>T</mi><mo>−</mo><mn>1</mn></mrow></munderover><mi>log</mi><mi>p</mi><mo>(</mo><msub><mi>x</mi><mrow><mi>t</mi><mo>+</mo><mn>1</mn></mrow></msub><mo>|</mo><msub><mi>x</mi><mrow><mn>1</mn><mo>:</mo><mi>t</mi></mrow></msub><mo>)</mo></mrow></math>

متن جایگزین فرمول: `L_LM = −Σ_{t=1}^{T−1} log p(x_{t+1} | x_{1:t})`. در آموزش، همهٔ جایگاه‌های یک دنباله را می‌توان با ماسک علّی در یک گذرِ موازی محاسبه کرد؛ ولی در **تولید معمول** هر توکن تازه به توکن‌های تولیدشدهٔ قبل وابسته است، پس گام‌های خروجی به ترتیب اجرا می‌شوند. آموزش موازی و استنتاج ترتیبی را با هم اشتباه نگیریم.

واژهٔ «Decoder-only» از شباهت بلوک به Decoder Transformer می‌آید، اما در این نسخه Encoder منبع و cross-attention وجود ندارند؛ فقط Self-Attention علّی و زیرلایه‌های بلوک باقی می‌مانند. ورودی prompt و خروجیِ آینده یک جریان متنی واحدند. این قرارداد برای تکمیل، گفت‌وگو و تولید متن انعطاف‌پذیر است؛ اما مدل را نمی‌توان بی‌درنگ به یک طبقه‌بندِ دوسویه یا یک سامانهٔ پاسخ‌گوییِ استخراجی تبدیل‌شده فرض کرد—باید سر، prompt، داده و معیار مناسب انتخاب شود.

## ۵. Encoder–Decoder: متن منبع، حافظه و متن هدف

در آرایش Encoder–Decoder دو جریان جدا داریم. Encoder با دید دوطرفه دنبالهٔ منبع را می‌خواند و حافظهٔ `H_E` می‌سازد. Decoder ورودیِ شیفت‌داده‌شدهٔ هدف را با ماسک علّی می‌خواند و در هر لایه از cross-attention به `H_E` مراجعه می‌کند. اگر `H_D` خروجیِ میانی Decoder باشد، یکی از سرهای توجه میان‌دنباله‌ای چنین ساخته می‌شود:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="پرس‌وجو از حالت رمزگشا، کلید و مقدار از حافظه رمزگذار؛ توجه از پرس‌وجوی رمزگشا به همه منبع می‌رود"><mrow><mi>Q</mi><mo>=</mo><msub><mi>H</mi><mi>D</mi></msub><msub><mi>W</mi><mi>Q</mi></msub><mo>,</mo><mspace width="0.7em"/><mi>K</mi><mo>=</mo><msub><mi>H</mi><mi>E</mi></msub><msub><mi>W</mi><mi>K</mi></msub><mo>,</mo><mspace width="0.7em"/><mi>V</mi><mo>=</mo><msub><mi>H</mi><mi>E</mi></msub><msub><mi>W</mi><mi>V</mi></msub><mo>,</mo><mspace width="0.7em"/><mi>CrossAttention</mi><mo>(</mo><mi>Q</mi><mo>,</mo><mi>K</mi><mo>,</mo><mi>V</mi><mo>)</mo></mrow></math>

متن جایگزین فرمول: `Q=H_D W_Q` و `K=H_E W_K`, `V=H_E W_V`; Query از Decoder است و Key/Value از حافظهٔ Encoder.

ترجمه نمونهٔ روشنِ نگاشت منبع به هدف است؛ خلاصه‌سازی، بازنویسی، تصحیح متن و تبدیل متن به قالب ساختاریافته نیز می‌توانند همین قرارداد را داشته باشند. T5 همهٔ مسئله‌های متنیِ مورد بررسی را در چارچوب ورودی‌متن/خروجی‌متن صورت‌بندی کرد و معماری Encoder–Decoder را به کار برد [۴]. BART با Encoder دوسویه و Decoder خودرگرسیو، متنِ خراب‌شده را بازسازی کرد و در مقاله برای تولید و فهم بررسی شد [۵]. این مثال‌ها نشان می‌دهند هدف پیش‌آموزش و شکل معماری دو محور مرتبط اما جدا هستند.

## ۶. سه الگوی دسترسی: کدام خانهٔ توجه باز است؟

برای ماتریس‌های زیر «۱ = مجاز» و «۰ = مسدود» را قرارداد بگیریم؛ ردیف `i` پرس‌وجو و ستون `j` کلید است. فرض کنیم منبع چهار توکن معتبر دارد و هدف سه جایگاه:

| سازوکار | نمونهٔ ماتریس دسترسی | تفسیر |
|---|---|---|
| Encoder self-attention | هر چهار ردیف `[1,1,1,1]` | هر توکن منبع به همهٔ منبع نگاه می‌کند |
| Decoder causal self-attention | `[1,0,0]`; `[1,1,0]`; `[1,1,1]` | ردیف `i` فقط جایگاه‌های `j≤i` را می‌بیند |
| Cross-attention | سه ردیفِ `[1,1,1,1]` | هر پرس‌وجوی هدف می‌تواند همهٔ جایگاه‌های منبع را ببیند |

در هر سه حالت، padding جداگانه پنهان می‌شود. به‌ویژه cross-attention برای ردیف منبعی که padding است نباید وزن معتبر بسازد. در PyTorch 2.6، در `nn.MultiheadAttention` برای ماسک بولی `True` یعنی **مسدود/نادیده گرفته‌شده**؛ این قرارداد با جدول بالا که ۱ را «مجاز» تعریف کردیم وارونه است [۶]. نام و شکل ماسک‌ها را از API همان نسخه بخوانید؛ وارونه‌کردن یک بولی کوچک می‌تواند جهت اطلاعات را عوض کند.

## ۷. معماری با هدف پیش‌آموزش یکی نیست

سه پرسش را جدا نگه داریم: (۱) چه اتصالاتی در مدل وجود دارد؟ (۲) هنگام آموزش چه هدفی بهینه می‌شود؟ (۳) پس از آموزش چه سر یا قالبی برای وظیفه می‌گذاریم؟ مثال‌ها:

- در BERT، Encoder دوطرفه است و هدفِ اصلیِ شناخته‌شدهٔ پیش‌آموزش MLM بود؛ موقعیت‌های ماسک‌شده از بافت چپ و راست پیش‌بینی می‌شوند [۲].
- در یک Decoder-only خودرگرسیو، توکن بعدی از پیشوند پیش‌بینی می‌شود [۳].
- T5 با Encoder–Decoder و هدف‌های text-to-text و span corruption مطالعه شد [۴].
- BART با Encoder–Decoder یاد می‌گیرد متنِ ورودیِ خراب‌شده را بازسازی کند [۵].

در آموزش seq2seq، هدف `y₁,…,y_T` معمولاً به ورودی Decoder با یک توکن آغازین شیفت می‌شود: ورودی `[BOS,y₁,…,y_{T−1}]`، برچسب‌ها `[y₁,…,y_T]`. این «teacher forcing» اجازه می‌دهد پیش‌بینی‌های موقعیت‌های هدف در یک گذر محاسبه شوند، در حالی که ماسک مانع دیدن پاسخ همان موقعیت یا آینده می‌شود. هنگام تولید، مدل فقط پیشوندِ واقعاً در دسترس را دارد و توکن جدید را به آن می‌افزاید. بنابراین یک آرایش ممکن است با هدف‌های آموزشی متفاوت، رفتارهای متفاوتی یاد بگیرد.

## ۸. مقایسهٔ فشردهٔ معماری‌ها

| بُعد | Encoder-only | Decoder-only | Encoder–Decoder |
|---|---|---|---|
| جریان اصلی | یک دنبالهٔ ورودی | یک جریان پیشوند/ادامه | منبع و هدف جدا |
| دید Self-Attention | دوسویه روی منبع معتبر | علّی؛ فقط گذشته و جاری | Encoder دوسویه؛ Decoder علّی |
| توجه بین منبع و هدف | ندارد در نسخهٔ ساده | ندارد در نسخهٔ ساده | cross-attention از هدف به حافظهٔ منبع |
| نمونهٔ پیش‌آموزش | MLM، مانند BERT [۲] | next-token LM، مانند GPT-3 [۳] | text-to-text/denoising، مانند T5 و BART [۴][۵] |
| خروجی معمول | برچسب، برچسب توکن، بازه یا بازنمایی | توکن بعدی و ادامهٔ متن | دنبالهٔ هدفِ شرطی بر منبع |
| پرسش شهودی | «این متن/توکن چیست؟» | «بعد از این پیشوند چه می‌آید؟» | «با دیدن این منبع، چه خروجی‌ای بسازم؟» |

این جدول برای تشخیص الگوست، نه پیش‌بینی قطعی کیفیت. برای مثال، T5 می‌تواند طبقه‌بندی را با تولید نام برچسب صورت‌بندی کند؛ Decoder-only هم می‌تواند برچسب متنی تولید کند. باید نتیجه را با دادهٔ همان وظیفه و آزمون مستقل سنجید.

## ۹. یک مثال گام‌به‌گام: ترجمهٔ جمله

فرض کنیم منبع فارسی «پرنده روی درخت نشست» و هدف انگلیسی «The bird landed on the tree.» باشد.

۱. Tokenizer منبع، توکن‌های `x₁…x_{L_s}` را می‌سازد؛ ترتیب و شناسه‌ها قرارداد tokenizer هستند، نه معنای آماده. ۲. Encoder هر توکن منبع را با بافت چپ و راست بازنمایی می‌کند و ماتریس حافظه `H_E ∈ R^{B×L_s×d}` می‌دهد. ۳. ورودی Decoder با `[BOS]` آغاز می‌شود. در گام نخست، cross-attention می‌تواند از همهٔ موقعیت‌های `H_E` کلید/مقدار بخواند و Decoder توکن اول هدف را حدس می‌زند. ۴. پس از تولید توکن اول، آن توکن به پیشوند اضافه می‌شود؛ گام بعد فقط توکن‌های قبلی هدف را در Self-Attention می‌بیند، اما همچنان به حافظهٔ منبع دسترسی دارد. ۵. تولید با توکن پایان یا شرط توقف مشخص تمام می‌شود.

در آموزش، توکن‌های واقعی هدف را با شیفت یک‌خانه‌ای وارد Decoder می‌کنیم و احتمال هر توکن هدف را می‌سنجیم. در استنتاج، خروجی پیش‌بینی‌شده جای توکن واقعی را می‌گیرد. اگر ترجمه طول منبع `L_s` و طول هدف `L_t` داشته باشد، این دو طول لازم نیست برابر باشند. Cross-attention ماتریسی با ردیف‌های هدف و ستون‌های منبع دارد؛ در سطح مفهومی اندازه‌اش `L_t×L_s` است.

## ۱۰. وظیفه به‌تنهایی معماری را تعیین نمی‌کند

| وظیفه/قرارداد | گزینهٔ رایج برای شروع | چه چیزی باید افزوده/آزموده شود؟ |
|---|---|---|
| طبقه‌بندی احساس یک جمله | Encoder-only با pooling و سر کلاس‌بندی | دادهٔ برچسب‌دار، کالیبراسیون و آزمون دامنهٔ تازه |
| NER یا برچسب هر توکن | خروجی Encoder برای هر جایگاه + سر توکن | نگاشت زیرتوکن به واژه و معیار span/token |
| پرسش‌وپاسخ استخراجی از متن | Encoder دوطرفه با سر آغاز/پایان | متن زمینه و سؤال، حد پاسخ و نبود پاسخ |
| تولید پاسخ/خلاصه از سند | Encoder–Decoder یا Decoder-only شرطی‌شده | کیفیت محتوایی، ارجاع به منبع و توهم |
| ترجمه یا بازنویسی ورودی به خروجی | Encoder–Decoder یک گزینهٔ مستقیم | دادهٔ موازی، طول خروجی و معیار انسانی/وظیفه‌ای |
| تکمیل و گفت‌وگوی باز | Decoder-only یک گزینهٔ رایج | prompt، توقف، ایمنی، تأخیر و ارزیابی چندمرحله‌ای |
| بازیابی متن مشابه | Encoder/embedding مدلِ آموزش‌دیده برای شباهت | contrastive training، منفی‌ها و معیار رتبه‌بندی |
| تولید برچسب به‌صورت متن | هر مدل مولدِ سازگار با قالب | واژگان خروجی محدود، قالب معتبر و هزینهٔ تولید |

«گزینهٔ رایج» به معنی بهترین انتخاب همیشگی نیست. یک سیستم می‌تواند مدل Encoder را با Decoder بیرونی ترکیب کند؛ پاسخ‌گویی می‌تواند استخراجی یا مولد باشد؛ و یک مدل generative می‌تواند خروجی کوتاه مثل `positive` تولید کند. قرارداد مسئله، دادهٔ آموزش و شیوهٔ استقرار را کنار هم بررسی کنید.

## ۱۱. هزینه‌ها، مرزها و سه سوءبرداشت

۱. **«Encoder یعنی فقط فهم، Decoder یعنی فقط تولید.»** این عبارت برای شهود آغازین مفید است، اما کامل نیست. Encoder نمایش می‌سازد و یک head می‌تواند وظیفهٔ متنوعی روی آن اجرا کند؛ Decoder-only هم می‌تواند سؤال را پاسخ دهد یا برچسب تولید کند. Encoder–Decoder هر دو مسیر را در یک مدل ترکیب می‌کند.

۲. **«مدل Encoder–Decoder فقط دو Transformer مستقل است.»** نه؛ در Decoderِ seq2seq، cross-attention اتصال صریح به حافظهٔ Encoder است. حذف این زیرلایه یعنی Decoder دیگر مستقیماً منبع را نمی‌خواند. در نسخهٔ decoder-only ساده، اصلاً حافظهٔ encoder وجود ندارد.

۳. **«ماسک علّی فقط در زمان تولید لازم است.»** نه. در آموزش هدفِ خودرگرسیو نیز باید نشت توکن‌های آینده بسته شود؛ وگرنه هدف هر موقعیت از پاسخ خودش یا آینده قابل مشاهده می‌شود. در مقابل، Encoder دوسویه عمداً متن ورودی را از هر دو سمت می‌بیند.

هزینهٔ دقیق به طول‌ها، عرض مدل، تعداد لایه‌ها، kernel و پیاده‌سازی وابسته است؛ فصل ۳۸ هزینهٔ توجه، KV cache و زمینهٔ بلند را جداگانه بررسی می‌کند. در سطح کیفی، Encoder–Decoder حافظهٔ منبع و cross-attention دارد؛ decoder-only ورودی و تولید را در یک جریان مدل می‌کند؛ Encoder-only برای استخراج بازنمایی و سرهای وظیفه‌ای مناسب است. این توصیف به‌تنهایی سرعت، حافظه یا کیفیت را رتبه‌بندی نمی‌کند.

## ۱۲. پروژهٔ اجرایی: یک ورودی، سه مسیر

در پروژهٔ CPU‌پسند، از `nn.MultiheadAttention` نسخهٔ PyTorch 2.6 برای نشان‌دادن سه الگو استفاده می‌کنیم [۶]. همهٔ مدل‌ها وزن تصادفی دارند و فقط یک لایهٔ کوچک‌اند؛ آن‌ها را LLM آموزش‌دیده یا نمونه‌ای از کیفیت واقعی ندانید. قرارداد شکل‌ها چنین است:

- Encoder-only: `source_ids [B,L_s] → class logits [B,C]`؛ بدنهٔ Encoder نیز برای هر توکن `[B,L_s,d]` بازنمایی می‌دهد.
- Decoder-only: `token_ids [B,L] → logits [B,L,V]`؛ logits هر جایگاه برای پیش‌بینی توکن بعدی به کار می‌رود.
- Encoder–Decoder: `source_ids [B,L_s]` و ورودی شیفت‌شدهٔ هدف `[B,L_t] → logits [B,L_t,V]`.

```python
from transformer_architectures import (
    EncoderOnlyClassifier, DecoderOnlyLanguageModel,
    EncoderDecoderTransformer, make_padding_mask, shift_right,
)
import torch

source = torch.tensor([[1, 4, 5, 0], [1, 6, 7, 0]])
target = torch.tensor([[8, 9, 2], [10, 11, 2]])
decoder_input = shift_right(target, bos_id=1)
src_pad = make_padding_mask(source, pad_id=0)
tgt_pad = make_padding_mask(decoder_input, pad_id=0)
seq2seq = EncoderDecoderTransformer(vocab_size=16)
logits = seq2seq(source, decoder_input, src_pad, tgt_pad)
print(logits.shape)  # torch.Size([2, 3, 16])
```

در `nn.MultiheadAttention`، `batch_first=True` یعنی شکل `[batch, sequence, feature]`; `key_padding_mask=True` یک کلید padding را نادیده می‌گیرد و در `attn_mask` بولی `True` یعنی آن خانه مسدود است [۶]. این دو معنا را در آزمون‌ها عمداً بررسی می‌کنیم. کد کامل و آزمون‌های نشت آینده و اتصال به حافظه در پیوست و پوشهٔ پروژه‌اند.

## ۱۳. تمرین‌ها و معیار عبور

۱. با یک جملهٔ چهارتوکنی، ماتریس مجاز Encoder و Decoder علّی را بنویسید و مشخص کنید در کدام معماری جایگاه سوم می‌تواند توکن چهارم را ببیند. ۲. برای ترجمهٔ طول منبع ۵ و طول هدف ۳، ابعاد ماتریس cross-attention را مشخص کنید. ۳. تفاوت هدف MLM در BERT و next-token در GPT را با یک مثال کوتاه بیان کنید. ۴. چرا Decoder-only می‌تواند در زمان آموزش همهٔ logits را موازی حساب کند، ولی تولید معمول را گام‌به‌گام انجام می‌دهد؟ ۵. برای NER، طبقه‌بندی احساس، خلاصه‌سازی و ترجمه یک گزینهٔ آغازین پیشنهاد دهید و برای هر کدام یک دلیل و یک محدودیت بنویسید. ۶. چرا نمی‌توان از عنوان Encoder-only نتیجه گرفت که embedding آن برای جست‌وجوی معنایی آماده است؟ ۷. ورودی decoder در teacher forcing را برای هدف `[a,b,c,EOS]` و `BOS` مشخص کنید. ۸. پروژه را اجرا کنید و با تغییر یک توکن آینده، بررسی کنید که logits موقعیت‌های قبلی Decoder-only تغییر نکنند؛ سپس در مدل Encoder، همان آزمایش را برای خروجی موقعیت صفر انجام دهید. ۹. یک آزمون گرادیان بنویسید که نشان دهد زیان خروجی seq2seq به embedding دست‌کم یک توکن منبع وابسته است.

**معیار عبور:** دست‌کم ۷ پاسخ از ۹ پاسخ باید شامل قرارداد ماسک و مسیر اطلاعات درست باشد؛ پروژه باید همهٔ آزمون‌ها را بگذراند، خروجی سه معماری finite باشد، و دلیل انتخاب برای هر وظیفه همراه یک محدودیت گزارش شود. پاسخ تشریحی در [پاسخ‌نامهٔ فصل ۳۷](book-engineering/answers/37-encoder-decoder-fa.md) است؛ ابتدا بدون نگاه‌کردن حل کنید.

## ۱۴. جمع‌بندی: ورودی را می‌فهمیم یا ادامه می‌دهیم؟

Encoder-only متن ورودی را با دید دوسویه به نمایش‌های زمینه‌ای تبدیل می‌کند؛ Decoder-only با ماسک علّی توکن بعدی را از پیشوند پیش‌بینی می‌کند؛ Encoder–Decoder یک منبعِ جدا دارد و Decoder از راه cross-attention به نمایش آن سر می‌زند. Transformer اصلی برای تبدیل دنباله به دنباله، هر دو پشتهٔ Encoder و Decoder را به هم وصل کرد. BERT، GPT، T5 و BART مثال‌هایی از انتخاب‌های متفاوت در معماری و هدف آموزش‌اند، نه قانون‌هایی که هر وظیفه فقط یک پاسخ داشته باشد.

برای انتخاب، ابتدا شکل ورودی و خروجی را دقیق کنید؛ سپس الگوی دید، هدف آموزش، head، داده، معیار و هزینه را کنار هم بگذارید. بعد انتخاب را با خط پایه و آزمونِ همان وظیفه بسنجید. در فصل بعد از سطح معماری به هزینهٔ استنتاج و زمینهٔ بلند می‌رویم: پنجرهٔ متن، KV Cache، GQA، توجه پراکنده و MoE.

## ۱۵. منابع بیرونی

همهٔ پیوندهای زیر در ۵ نوامبر ۲۰۲۶ بازبینی شدند. تاریخ مقاله با تاریخ نسخهٔ برخط یکی نیست؛ نتیجه‌های آزمایشی هر مقاله فقط در تنظیم‌ها و داده‌های همان مطالعه معتبرند.

1. Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). “Attention Is All You Need.” *Advances in Neural Information Processing Systems 30*. arXiv نسخهٔ v7، بازنگری ۲ اوت ۲۰۲۳. [متن HTML](https://arxiv.org/html/1706.03762v7) · [DOI arXiv](https://doi.org/10.48550/arXiv.1706.03762).
2. Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). “BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.” *NAACL-HLT 2019*, pp. 4171–4186. [ACL Anthology](https://aclanthology.org/N19-1423/) · [DOI](https://doi.org/10.18653/v1/N19-1423).
3. Brown, T. B., Mann, B., Ryder, N., et al. (2020). “Language Models are Few-Shot Learners.” *NeurIPS 2020*. [صفحهٔ مقاله و چکیده](https://papers.nips.cc/paper/2020/hash/1457c0d6bfcb4967418bfb8ac142f64a-Abstract.html) · [arXiv](https://arxiv.org/abs/2005.14165).
4. Raffel, C., Shazeer, N., Roberts, A., et al. (2020). “Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer.” *Journal of Machine Learning Research, 21*(140), 1–67. [متن JMLR](https://jmlr.org/papers/v21/20-074.html).
5. Lewis, M., Liu, Y., Goyal, N., et al. (2020). “BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension.” *ACL 2020*, pp. 7871–7880. [ACL Anthology](https://aclanthology.org/2020.acl-main.703/) · [DOI](https://doi.org/10.18653/v1/2020.acl-main.703).
6. PyTorch Contributors. “`torch.nn.MultiheadAttention`,” مستندات نسخهٔ 2.6؛ تاریخ انتشار صفحه نامشخص. [API و قرارداد mask](https://docs.pytorch.org/docs/2.6/generated/torch.nn.MultiheadAttention.html).

## پیوست: کد کامل پروژه

فایل زیر با `book-engineering/projects/37-encoder-decoder/transformer_architectures.py` همسان است و آزمون‌های جداگانه در همان پوشه قرار دارند.

```python
"""Small CPU-friendly examples of encoder-only, decoder-only and seq2seq Transformers.

The module is instructional, not a pretrained language model. Boolean attention
masks follow PyTorch nn.MultiheadAttention 2.6 semantics: True means blocked.
"""
from __future__ import annotations

import torch
from torch import Tensor, nn


def _check_config(vocab_size: int, d_model: int, num_heads: int, ff_dim: int,
                  num_layers: int, max_len: int, pad_id: int) -> None:
    if vocab_size < 2:
        raise ValueError("vocab_size must be at least 2")
    if d_model < 1 or num_heads < 1 or d_model % num_heads:
        raise ValueError("d_model must be positive and divisible by num_heads")
    if ff_dim < 1 or num_layers < 1 or max_len < 1:
        raise ValueError("ff_dim, num_layers and max_len must be positive")
    if not 0 <= pad_id < vocab_size:
        raise ValueError("pad_id must be a valid vocabulary id")


def _check_tokens(token_ids: Tensor, vocab_size: int, name: str) -> None:
    if not isinstance(token_ids, Tensor) or token_ids.ndim != 2:
        raise ValueError(f"{name} must have shape [batch, length]")
    if token_ids.dtype != torch.long:
        raise ValueError(f"{name} must use torch.long token ids")
    if token_ids.shape[0] < 1 or token_ids.shape[1] < 1:
        raise ValueError(f"{name} must contain a non-empty batch and sequence")
    if token_ids.min().item() < 0 or token_ids.max().item() >= vocab_size:
        raise ValueError(f"{name} contains an id outside the vocabulary")


def _check_padding_mask(mask: Tensor | None, token_ids: Tensor, name: str) -> Tensor | None:
    if mask is None:
        return None
    if mask.dtype != torch.bool or tuple(mask.shape) != tuple(token_ids.shape):
        raise ValueError(f"{name} must be a boolean tensor with the same [batch, length] shape")
    return mask


def make_padding_mask(token_ids: Tensor, pad_id: int = 0) -> Tensor:
    """Return True at padding tokens, the key_padding_mask convention in PyTorch."""
    if token_ids.ndim != 2 or token_ids.dtype != torch.long:
        raise ValueError("token_ids must be a rank-2 torch.long tensor")
    if pad_id < 0:
        raise ValueError("pad_id must be non-negative")
    return token_ids.eq(pad_id)


def causal_mask(length: int, device: torch.device | None = None) -> Tensor:
    """Boolean [T,T] mask: True blocks keys strictly to the right of each query."""
    if length < 1:
        raise ValueError("length must be positive")
    return torch.ones((length, length), dtype=torch.bool, device=device).triu(1)


def shift_right(target_ids: Tensor, bos_id: int) -> Tensor:
    """Teacher-forcing input: [BOS, y0, ..., y_(T-2)] for target [y0, ..., y_(T-1)]."""
    if target_ids.ndim != 2 or target_ids.dtype != torch.long:
        raise ValueError("target_ids must be a rank-2 torch.long tensor")
    if target_ids.shape[0] < 1 or target_ids.shape[1] < 1 or bos_id < 0:
        raise ValueError("target_ids and bos_id must be non-empty/non-negative")
    bos = torch.full((target_ids.shape[0], 1), bos_id,
                     dtype=torch.long, device=target_ids.device)
    return torch.cat((bos, target_ids[:, :-1]), dim=1)


class TokenPositionEmbedding(nn.Module):
    """Learned token plus absolute position embeddings for a teaching example."""
    def __init__(self, vocab_size: int, d_model: int, max_len: int, pad_id: int) -> None:
        super().__init__()
        self.max_len = max_len
        self.token = nn.Embedding(vocab_size, d_model, padding_idx=pad_id)
        self.position = nn.Embedding(max_len, d_model)

    def forward(self, token_ids: Tensor) -> Tensor:
        length = token_ids.shape[1]
        if length > self.max_len:
            raise ValueError(f"sequence length {length} exceeds max_len={self.max_len}")
        positions = torch.arange(length, device=token_ids.device).unsqueeze(0)
        return self.token(token_ids) + self.position(positions)


class BidirectionalEncoderBlock(nn.Module):
    """Pre-LN encoder block: unmasked self-attention, then a position-wise FFN."""
    def __init__(self, d_model: int, num_heads: int, ff_dim: int) -> None:
        super().__init__()
        self.norm_attn = nn.LayerNorm(d_model)
        self.self_attn = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(nn.Linear(d_model, ff_dim), nn.GELU(), nn.Linear(ff_dim, d_model))

    def forward(self, x: Tensor, key_padding_mask: Tensor | None = None) -> Tensor:
        qkv = self.norm_attn(x)
        attended, _ = self.self_attn(
            qkv, qkv, qkv, key_padding_mask=key_padding_mask, need_weights=False
        )
        x = x + attended
        return x + self.ff(self.norm_ff(x))


class CausalDecoderBlock(nn.Module):
    """Pre-LN decoder-only block: causal self-attention and a position-wise FFN."""
    def __init__(self, d_model: int, num_heads: int, ff_dim: int) -> None:
        super().__init__()
        self.norm_attn = nn.LayerNorm(d_model)
        self.self_attn = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(nn.Linear(d_model, ff_dim), nn.GELU(), nn.Linear(ff_dim, d_model))

    def forward(self, x: Tensor, key_padding_mask: Tensor | None = None) -> Tensor:
        qkv = self.norm_attn(x)
        attended, _ = self.self_attn(
            qkv, qkv, qkv,
            attn_mask=causal_mask(x.shape[1], device=x.device),
            key_padding_mask=key_padding_mask,
            need_weights=False,
        )
        x = x + attended
        return x + self.ff(self.norm_ff(x))


class EncoderDecoderBlock(nn.Module):
    """Decoder block with causal self-attention, source cross-attention and an FFN."""
    def __init__(self, d_model: int, num_heads: int, ff_dim: int) -> None:
        super().__init__()
        self.norm_self = nn.LayerNorm(d_model)
        self.self_attn = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.norm_cross = nn.LayerNorm(d_model)
        self.cross_attn = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(nn.Linear(d_model, ff_dim), nn.GELU(), nn.Linear(ff_dim, d_model))

    def forward(self, target: Tensor, memory: Tensor,
                target_padding_mask: Tensor | None = None,
                memory_padding_mask: Tensor | None = None) -> Tensor:
        q = self.norm_self(target)
        attended, _ = self.self_attn(
            q, q, q,
            attn_mask=causal_mask(target.shape[1], device=target.device),
            key_padding_mask=target_padding_mask,
            need_weights=False,
        )
        target = target + attended

        # Queries come from the decoder; keys and values are the encoder memory.
        cross_query = self.norm_cross(target)
        cross, _ = self.cross_attn(
            cross_query, memory, memory,
            key_padding_mask=memory_padding_mask,
            need_weights=False,
        )
        target = target + cross
        return target + self.ff(self.norm_ff(target))


class BidirectionalEncoder(nn.Module):
    """Encoder backbone returning one contextual vector per source token."""
    def __init__(self, vocab_size: int, d_model: int = 32, num_heads: int = 4,
                 ff_dim: int = 64, num_layers: int = 1, max_len: int = 128,
                 pad_id: int = 0) -> None:
        super().__init__()
        _check_config(vocab_size, d_model, num_heads, ff_dim, num_layers, max_len, pad_id)
        self.vocab_size, self.pad_id = vocab_size, pad_id
        self.embedding = TokenPositionEmbedding(vocab_size, d_model, max_len, pad_id)
        self.layers = nn.ModuleList(
            BidirectionalEncoderBlock(d_model, num_heads, ff_dim) for _ in range(num_layers)
        )
        self.final_norm = nn.LayerNorm(d_model)

    def forward(self, source_ids: Tensor,
                source_padding_mask: Tensor | None = None) -> Tensor:
        _check_tokens(source_ids, self.vocab_size, "source_ids")
        source_padding_mask = _check_padding_mask(
            source_padding_mask, source_ids, "source_padding_mask"
        )
        if source_ids.shape[1] > self.embedding.max_len:
            raise ValueError("source sequence exceeds max_len")
        if source_padding_mask is None:
            source_padding_mask = make_padding_mask(source_ids, self.pad_id)
        x = self.embedding(source_ids)
        for layer in self.layers:
            x = layer(x, key_padding_mask=source_padding_mask)
        return self.final_norm(x)


class EncoderOnlyClassifier(nn.Module):
    """Bidirectional encoder plus a masked-mean classification head."""
    def __init__(self, vocab_size: int, num_classes: int, d_model: int = 32,
                 num_heads: int = 4, ff_dim: int = 64, num_layers: int = 1,
                 max_len: int = 128, pad_id: int = 0) -> None:
        super().__init__()
        if num_classes < 2:
            raise ValueError("num_classes must be at least 2")
        self.pad_id = pad_id
        self.encoder = BidirectionalEncoder(
            vocab_size, d_model, num_heads, ff_dim, num_layers, max_len, pad_id
        )
        self.classifier = nn.Linear(d_model, num_classes)

    def forward(self, source_ids: Tensor,
                source_padding_mask: Tensor | None = None) -> Tensor:
        if source_padding_mask is None:
            source_padding_mask = make_padding_mask(source_ids, self.pad_id)
        hidden = self.encoder(source_ids, source_padding_mask)
        valid = (~source_padding_mask).unsqueeze(-1).to(hidden.dtype)
        pooled = (hidden * valid).sum(dim=1) / valid.sum(dim=1).clamp_min(1.0)
        return self.classifier(pooled)


class DecoderOnlyLanguageModel(nn.Module):
    """Causal decoder-only model; logits at t predict the next target token."""
    def __init__(self, vocab_size: int, d_model: int = 32, num_heads: int = 4,
                 ff_dim: int = 64, num_layers: int = 1, max_len: int = 128,
                 pad_id: int = 0) -> None:
        super().__init__()
        _check_config(vocab_size, d_model, num_heads, ff_dim, num_layers, max_len, pad_id)
        self.vocab_size, self.pad_id = vocab_size, pad_id
        self.embedding = TokenPositionEmbedding(vocab_size, d_model, max_len, pad_id)
        self.layers = nn.ModuleList(
            CausalDecoderBlock(d_model, num_heads, ff_dim) for _ in range(num_layers)
        )
        self.final_norm = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size)

    def forward(self, token_ids: Tensor,
                padding_mask: Tensor | None = None) -> Tensor:
        _check_tokens(token_ids, self.vocab_size, "token_ids")
        padding_mask = _check_padding_mask(padding_mask, token_ids, "padding_mask")
        if token_ids.shape[1] > self.embedding.max_len:
            raise ValueError("token sequence exceeds max_len")
        if padding_mask is None:
            padding_mask = make_padding_mask(token_ids, self.pad_id)
        x = self.embedding(token_ids)
        for layer in self.layers:
            x = layer(x, key_padding_mask=padding_mask)
        return self.lm_head(self.final_norm(x))


class EncoderDecoderTransformer(nn.Module):
    """Conditional autoregressive Transformer with separate source and target streams."""
    def __init__(self, vocab_size: int, d_model: int = 32, num_heads: int = 4,
                 ff_dim: int = 64, num_layers: int = 1, max_len: int = 128,
                 pad_id: int = 0) -> None:
        super().__init__()
        _check_config(vocab_size, d_model, num_heads, ff_dim, num_layers, max_len, pad_id)
        self.vocab_size, self.pad_id = vocab_size, pad_id
        self.source_embedding = TokenPositionEmbedding(vocab_size, d_model, max_len, pad_id)
        self.target_embedding = TokenPositionEmbedding(vocab_size, d_model, max_len, pad_id)
        self.encoder_layers = nn.ModuleList(
            BidirectionalEncoderBlock(d_model, num_heads, ff_dim) for _ in range(num_layers)
        )
        self.encoder_norm = nn.LayerNorm(d_model)
        self.decoder_layers = nn.ModuleList(
            EncoderDecoderBlock(d_model, num_heads, ff_dim) for _ in range(num_layers)
        )
        self.decoder_norm = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size)

    def encode(self, source_ids: Tensor,
               source_padding_mask: Tensor | None = None) -> Tensor:
        _check_tokens(source_ids, self.vocab_size, "source_ids")
        source_padding_mask = _check_padding_mask(
            source_padding_mask, source_ids, "source_padding_mask"
        )
        if source_ids.shape[1] > self.source_embedding.max_len:
            raise ValueError("source sequence exceeds max_len")
        if source_padding_mask is None:
            source_padding_mask = make_padding_mask(source_ids, self.pad_id)
        memory = self.source_embedding(source_ids)
        for layer in self.encoder_layers:
            memory = layer(memory, key_padding_mask=source_padding_mask)
        return self.encoder_norm(memory)

    def decode(self, target_input_ids: Tensor, memory: Tensor,
               target_padding_mask: Tensor | None = None,
               memory_padding_mask: Tensor | None = None) -> Tensor:
        _check_tokens(target_input_ids, self.vocab_size, "target_input_ids")
        if target_input_ids.shape[1] > self.target_embedding.max_len:
            raise ValueError("target sequence exceeds max_len")
        target_padding_mask = _check_padding_mask(
            target_padding_mask, target_input_ids, "target_padding_mask"
        )
        if memory.ndim != 3 or memory.shape[0] != target_input_ids.shape[0]:
            raise ValueError("memory must be [same batch, source length, d_model]")
        if memory.shape[1] < 1 or memory.shape[2] != self.lm_head.in_features:
            raise ValueError("memory has an invalid source length or feature dimension")
        if memory_padding_mask is not None:
            if (memory_padding_mask.dtype != torch.bool
                    or tuple(memory_padding_mask.shape) != tuple(memory.shape[:2])):
                raise ValueError("memory_padding_mask must be boolean [batch, source length]")
        x = self.target_embedding(target_input_ids)
        for layer in self.decoder_layers:
            x = layer(
                x, memory,
                target_padding_mask=target_padding_mask,
                memory_padding_mask=memory_padding_mask,
            )
        return self.lm_head(self.decoder_norm(x))

    def forward(self, source_ids: Tensor, target_input_ids: Tensor,
                source_padding_mask: Tensor | None = None,
                target_padding_mask: Tensor | None = None) -> Tensor:
        if source_padding_mask is None:
            source_padding_mask = make_padding_mask(source_ids, self.pad_id)
        if target_padding_mask is None:
            target_padding_mask = make_padding_mask(target_input_ids, self.pad_id)
        memory = self.encode(source_ids, source_padding_mask)
        return self.decode(
            target_input_ids, memory, target_padding_mask, source_padding_mask
        )


def demo() -> None:
    torch.manual_seed(7)
    source = torch.tensor([[1, 4, 5, 0], [1, 6, 7, 0]], dtype=torch.long)
    target = torch.tensor([[8, 9, 2], [10, 11, 2]], dtype=torch.long)
    decoder_input = shift_right(target, bos_id=1)
    source_padding = make_padding_mask(source, pad_id=0)
    target_padding = make_padding_mask(decoder_input, pad_id=0)

    encoder = EncoderOnlyClassifier(vocab_size=16, num_classes=3)
    decoder = DecoderOnlyLanguageModel(vocab_size=16)
    seq2seq = EncoderDecoderTransformer(vocab_size=16)
    print("encoder-only logits:", tuple(encoder(source, source_padding).shape))
    print("decoder-only next-token logits:", tuple(decoder(source, source_padding).shape))
    print("encoder-decoder logits:", tuple(
        seq2seq(source, decoder_input, source_padding, target_padding).shape
    ))
    print("decoder input:", decoder_input.tolist())
    print("all outputs finite:", all(torch.isfinite(x).all().item() for x in (
        encoder(source, source_padding), decoder(source, source_padding),
        seq2seq(source, decoder_input, source_padding, target_padding),
    )))


if __name__ == "__main__":
    demo()
```
