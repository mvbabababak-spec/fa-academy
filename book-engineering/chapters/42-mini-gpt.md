# جلد سوم، فصل ۱۰ — طراحی Mini GPT: ابعاد، پارامتر و بودجه

**نگاشت:** فصل محلی ۱۰ جلد سوم = فصل سراسری ۴۲. **تاریخ بازبینی منابع: ۵ نوامبر ۲۰۲۶.** فصل ۳۷ یک Decoder-only آزموده‌شده با ماسک علّی ساخت؛ فصل ۴۱ یک مدل feed-forward را آموزش داد. این فصل معماری Decoder را از نو تعریف نمی‌کند و مدل را هم آموزش نمی‌دهد: هدف، تبدیل خواستهٔ مبهم «یک Mini GPT بساز» به پیکربندی، شمار پارامتر و بودجه‌ای قابل‌آزمون است. آماده‌سازی corpus و مجوز در فصل‌های ۴۰ و ۴۳ می‌آیند؛ حلقهٔ پیش‌آموزش در فصل ۴۴.

**پیش‌نیاز:** شکل‌های Self-Attention و بلوک Transformer از فصل‌های ۳۵–۳۷؛ مرز رکورد و واژگان train-only از فصل ۴۰؛ next-token و splitهای train/validation/test از فصل ۴۱. **قرارداد:** `V` اندازهٔ واژگان، `C` بیشینهٔ زمینه، `T` طول واقعی دنباله در یک batch، `N` اندازهٔ batch، `d` عرض مدل، `h` تعداد head، `f` عرض FFN و `L` تعداد بلوک‌هاست. `T` با تعداد واژه‌ها یکی نیست؛ واحد آن token پس از tokenizer است.

## ۱. طراحی را از معماری تکراری جدا کنیم

واژهٔ «Mini GPT» اندازهٔ استاندارد یا تضمین کیفیتی ندارد. در این فصل منظورمان یک مدل آموزشیِ decoder-only با embedding توکن و موقعیت، بلوک‌های علّی، و سر logits واژگان است. این الگو از خانوادهٔ GPT الهام می‌گیرد؛ اما پیکربندی ۱۱۷هزارپارامتری درس را نباید GPT-1، GPT-2، LLM مفید یا مدل فارسیِ آموزش‌دیده نامید.

در پروژهٔ فصل ۳۷، `DecoderOnlyLanguageModel` همین مسیر را با `nn.MultiheadAttention`، بلوک Pre-LN و خروجی `[N,T,V]` پیاده کرده است. پروژهٔ این فصل آن کد را دوباره کپی نمی‌کند: همان پیاده‌سازی را import می‌کند، شمار پارامترها را با شکل واقعی ماژول‌ها تطبیق می‌دهد و اندازهٔ چند tensor مهم را برای چند context برآورد می‌کند. بنابراین سؤال ما «آیا می‌توان attention نوشت؟» نیست؛ «با این داده، زمینه و سقف منابع، کدام پیکربندی را آزمایش می‌کنیم؟» است.

![شکل ۳-۱۰-۱ — نمودار Mini GPT: ورودی توکن `[N,T]` از embedding به بلوک‌های Decoder-only علّی می‌رود و logits `[N,T,V]` می‌دهد؛ ماسک `j>i` را می‌بندد. نمونهٔ بودجه ۱۱۷٬۳۵۰ پارامتر دارد؛ برای `N=16,T=64`، حافظهٔ پایدارِ برآوردی ۱٫۷۹ MiB و جمع tensorهای مرجع ۴٫۴۰ MiB است. جدول، رشد خطی position embedding و رشد درجه‌دوم score-equivalent را نشان می‌دهد؛ این تخمین‌ها اندازه‌گیری اوج GPU نیستند.](assets/images/babak-ai/v3-ch10-mini-gpt-budget.webp)

**شکل ۳-۱۰-۱ —** یک مسیر محاسبه، سه سقف متفاوت: ابعاد خروجی، تعداد پارامتر و tensorهای وابسته به طول زمینه. اعداد حافظه اندازهٔ مرجع چند آرایه‌اند، نه benchmark یا مصرف واقعی دستگاه.

## ۲. پیش از اجرا یک مشخصات قابل‌ابطال بنویسیم

به‌جای «مدل کوچک»، این پیکربندی را ثبت می‌کنیم:

| نماد/کلید | معنای مهندسی | نمونهٔ درس |
|---|---|---:|
| `V` / `vocab_size` | تعداد شناسه‌های tokenizer | ۱۰۲ |
| `C` / `block_size` | بیشترین token در هر ورودی، شامل special tokenها | ۶۴ |
| `d` / `d_model` | عرض بردار هر موقعیت | ۶۴ |
| `h` / `num_heads` | تعداد headهای توجه | ۴ |
| `f` / `ff_dim` | عرض پنهان FFN در هر بلوک | ۲۵۶ |
| `L` / `num_layers` | تعداد بلوک‌های علّی | ۲ |
| `pad_id` | شناسهٔ padding در دادهٔ همین واژگان | ۰ |
| `N` / `batch_size` | تعداد دنباله‌ها در batch نمونه | ۱۶ |

این‌ها یک baseline برای حساب و آزمون‌اند، نه بهترین اعداد. `d` باید بر `h` بخش‌پذیر باشد تا هر head عرض صحیح داشته باشد. برای یک batch واقعی نیز باید `1 ≤ T ≤ C` برقرار باشد. معماری این پروژه موقعیت‌های آموختنی با طول `C` دارد و اگر `T>C` شود خطا می‌دهد؛ خودکار بریدن یا «فهمیدن» دنبالهٔ بلندتر را تضمین نمی‌کند.

## ۳. شکل تنسور، قرارداد اطلاعات را آشکار می‌کند

با ورودی شناسه‌های `token_ids [N,T]`، embedding توکن و embedding موقعیت با هم جمع می‌شوند و حالت پنهان `[N,T,d]` می‌سازند. هر یک از `L` بلوک‌ها همین شکل را می‌گیرد و پس می‌دهد. سر خطی واژگان آن را به logits با شکل `[N,T,V]` تبدیل می‌کند. هدف آموزشی نیز برای هر جایگاه یک شناسه دارد و شکلش `[N,T]` است.

در مدل علّی، پرس‌وجوی جایگاه `i` حق دیدن کلیدهای جایگاه `j>i` را ندارد. در ماتریس `attn_mask` بولیِ `nn.MultiheadAttention` در PyTorch 2.6، مقدار `True` خانه را **مسدود** می‌کند؛ در `key_padding_mask` نیز `True` کلید padding را نادیده می‌گیرد [۴]. این قرارداد را از API همان ماژول بخوانید، نه از نام متغیر یا رنگ شکل؛ فصل ۳۷ نمونه و آزمون رفتاری آن را ارائه کرده است.

logits موقعیت `t` با توکن بعدی سنجیده می‌شود؛ ورودی و هدف هم‌طول‌اند اما یک خانه جابه‌جا هستند. این طراحی اجازه می‌دهد آموزش همهٔ جایگاه‌های حاضر را در یک forward بسنجد، در حالی که mask راهِ دیدن آینده را می‌بندد. هنگام تولید، همچنان باید از پیشوند واقعاً موجود جلو رفت؛ شکل سه‌بعدی logits به‌تنهایی تولید موازیِ آینده را ممکن نمی‌کند.

## ۴. شمار پارامتر را از شکل ماژول‌ها درآوریم

شمار دقیق فقط به اندازهٔ `d` وابسته نیست. در پیاده‌سازی فصل ۳۷، embedding توکن `V×d` و جدول موقعیت `C×d` دارد. در `MultiheadAttention` با Q/K/V هم‌اندازه، ماتریس‌های projection روی‌هم `4d²` وزن و با bias برابر `4d` پارامتر دارند: سه projection ورودی و یک projection خروجی. هر بلوک دو LayerNorm با `4d` پارامتر دارد. دو Linear در FFN روی‌هم `2df+f+d` پارامتر دارند. LayerNorm نهایی `2d` پارامتر دارد و سر واژگانِ جداگانه `dV+V` است. ابعاد/بایاس‌های این اجزا مطابق APIهای نسخهٔ PyTorch 2.6‌اند [۴،۵].

پس برای **همین مدلِ دارای bias و سر خروجی untied**:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="تعداد پارامتر Mini GPT پروژه برابر Vd به‌علاوه Cd به‌علاوه L ضرب در چهار d به توان دو به‌علاوه نه d به‌علاوه دو d f به‌علاوه f، به‌علاوه دو d، به‌علاوه dV به‌علاوه V است">
  <mrow><msub><mi>P</mi><mi>total</mi></msub><mo>=</mo><mi>V</mi><mi>d</mi><mo>+</mo><mi>C</mi><mi>d</mi><mo>+</mo><mi>L</mi><mo>(</mo><mn>4</mn><msup><mi>d</mi><mn>2</mn></msup><mo>+</mo><mn>9</mn><mi>d</mi><mo>+</mo><mn>2</mn><mi>d</mi><mi>f</mi><mo>+</mo><mi>f</mi><mo>)</mo><mo>+</mo><mn>2</mn><mi>d</mi><mo>+</mo><mi>d</mi><mi>V</mi><mo>+</mo><mi>V</mi></mrow>
</math>

**متن جایگزین فرمول:** تعداد پارامتر Mini GPT پروژه برابر Vd به‌علاوه Cd به‌علاوه L ضرب در چهار d به توان دو به‌علاوه نه d به‌علاوه دو d f به‌علاوه f، به‌علاوه دو d، به‌علاوه dV به‌علاوه V است.

اگر `f=4d` باشد، عبارت هر بلوک `12d²+13d` می‌شود. این شمار، سطر padding را هم در جدول embedding می‌شمارد؛ `padding_idx` می‌تواند گرادیان آن سطر را متوقف کند، ولی تعداد خانه‌های پارامتر را کوچک نمی‌کند [۵]. این فرمول را برای هر GPT دیگری کپی نکنید: tying وزن ورودی/خروجی، حذف bias، RMSNorm یا اندازه‌های projection متفاوت آن را عوض می‌کنند.

## ۵. نمونه را دستی و با ماژول تطبیق دهیم

برای `V=102`, `C=64`, `d=64`, `h=4`, `f=256`, `L=2`، embedding توکن `102×64=6,528` پارامتر و embedding موقعیت `64×64=4,096` دارد. یک بلوک attention دارای `4×64²+4×64=16,640` پارامتر است؛ دو LayerNorm آن `256` و FFN آن `2×64×256+256+64=33,088` پارامتر دارد. هر بلوک پس `49,984` و دو بلوک `99,968` پارامتر دارند. LayerNorm نهایی `128` و سر خروجی جدا `64×102+102=6,630` دارند.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="نمونهٔ شمار پارامتر برابر ۶۵۲۸ embedding توکن به‌علاوه ۴۰۹۶ موقعیت به‌علاوه ۹۹۹۶۸ دو بلوک به‌علاوه ۱۲۸ نرمال‌سازی نهایی به‌علاوه ۶۶۳۰ سر خروجی، در مجموع ۱۱۷۳۵۰ است">
  <mrow><mn>6,528</mn><mo>+</mo><mn>4,096</mn><mo>+</mo><mn>99,968</mn><mo>+</mo><mn>128</mn><mo>+</mo><mn>6,630</mn><mo>=</mo><mn>117,350</mn></mrow>
</math>

**متن جایگزین فرمول:** نمونهٔ شمار پارامتر برابر ۶۵۲۸ embedding توکن به‌علاوه ۴۰۹۶ موقعیت به‌علاوه ۹۹۹۶۸ دو بلوک به‌علاوه ۱۲۸ نرمال‌سازی نهایی به‌علاوه ۶۶۳۰ سر خروجی، در مجموع ۱۱۷۳۵۰ است.

اسکریپت پروژه این مقدار را با `sum(p.numel() for p in model.parameters())` تطبیق می‌دهد؛ اگر فرمول با همان مدل برابر نباشد، گزارش متوقف می‌شود. همچنین `h` در این پیاده‌سازی با ثابت‌بودن `d` تعداد وزن‌های projection را تغییر نمی‌دهد؛ تعداد head بیشتر، پارامتر بیشتر را به‌طور خودکار معنی نمی‌دهد. البته شکل هر head و محاسبات attention تغییر می‌کند.

## ۶. اندازهٔ واژگان به‌تنهایی روی embedding اثر نمی‌گذارد

چون سر خروجی این نمونه با embedding ورودی مشترک نیست، تغییر اندازهٔ واژگان `V` دو ماتریسِ `V×d` را عوض می‌کند و bias خروجی هم `V` مقدار دارد. با ثابت‌بودن بقیهٔ پیکربندی، سهم واژگان `2Vd+V` است. در تنظیم آموزشی `V=102`، این سهم `13,158` پارامتر است؛ اما اگر فقط برای یک مثال حساب، `V=50,257` بگذاریم، کل مدلِ همین پیکربندی به `6,587,345` پارامتر می‌رسد. این مثال عددی است، نه پیشنهاد tokenizer.

در نتیجه، tokenizer و معماری را جداگانه بهینه نکنید: تغییر واژگان می‌تواند طول tokenها، تعداد embeddingها، اندازهٔ logits، درصد padding و تعداد targetهای هر batch را عوض کند. «۱۰۲ واژه» در نمونهٔ فصل ۴۰ ویژگی corpus کوچک و word-level همان درس است، نه واژگان مناسب پیش‌آموزش فارسی. مدل‌های GPT تاریخی از tokenization و مقیاس دیگری استفاده کردند [۲،۳]. اگر head را با embedding گره بزنیم، شمار پارامتر پایین می‌آید؛ اما وزن مشترک، bias و قرارداد خروجی باید در فرمول و آزمون لحاظ شود.

## ۷. زمینه را با هزینهٔ وابسته به طول بسنجیم

برای یک forward با دنبالهٔ واقعی `T`، اندازهٔ scoreهای attention متراکم به‌صورت مرجع با `N×L×h×T²` خانه رشد می‌کند؛ FFN پنهان با `N×L×T×f` و logits با `N×T×V` خانه. ضرب در `b_a`، تعداد بایت هر خانه در محاسبهٔ مرجع، اندازهٔ byte-equivalent می‌دهد:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="اندازهٔ مرجع score توجه برابر N L h T به توان دو b؛ اندازهٔ activation پنهان FFN برابر N L T f b؛ اندازهٔ logits برابر N T V b است">
  <mrow><msub><mi>S</mi><mi>score</mi></msub><mo>=</mo><mi>N</mi><mi>L</mi><mi>h</mi><msup><mi>T</mi><mn>2</mn></msup><mi>b</mi><mo>,</mo><mspace width="0.7em"/><msub><mi>S</mi><mi>FFN</mi></msub><mo>=</mo><mi>N</mi><mi>L</mi><mi>T</mi><mi>f</mi><mi>b</mi><mo>,</mo><mspace width="0.7em"/><msub><mi>S</mi><mi>logits</mi></msub><mo>=</mo><mi>N</mi><mi>T</mi><mi>V</mi><mi>b</mi></mrow>
</math>

**متن جایگزین فرمول:** اندازهٔ مرجع score توجه برابر N L h T به توان دو b؛ اندازهٔ activation پنهان FFN برابر N L T f b؛ اندازهٔ logits برابر N T V b است.

این‌ها **اندازهٔ tensor مرجع** هستند، نه پیش‌بینی مصرف peak. PyTorch ممکن است در `need_weights=False` از مسیرهای بهینهٔ scaled-dot-product استفاده کند؛ بنابراین score-equivalent لزوماً به شکل یک ماتریس کامل در حافظه ساخته نمی‌شود [۴]. جمع tensorها همزمانی عمرشان، activationهای باقیمانده، Q/K/V، mask، workspace، allocator و گرادیان را مدل نمی‌کند. برای تصمیم دستگاه، تخمین را با profiler یا شمارندهٔ حافظه روی همان نسخه، batch، dtype و kernel بررسی کنید [۷].

## ۸. حافظهٔ وزن با حافظهٔ آموزش یکی نیست

وزن‌های مدل فقط یک بخش از حافظه‌اند. برای برآورد پایدارِ ساده، اگر هر پارامتر ۴ بایت FP32، هر گرادیان ۴ بایت و دو moment از AdamW روی‌هم ۸ بایت باشند، پس از آن‌که stateهای optimizer ساخته شدند:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="حافظهٔ پایدار نمونه برابر تعداد پارامتر ضرب در چهار بایت وزن، چهار بایت گرادیان و هشت بایت برای دو moment آدام دبلیو است؛ یعنی شانزده P بایت">
  <mrow><msub><mi>M</mi><mi>persistent</mi></msub><mo>≈</mo><mi>P</mi><mo>(</mo><mn>4</mn><mo>+</mo><mn>4</mn><mo>+</mo><mn>8</mn><mo>)</mo><mo>=</mo><mn>16</mn><mi>P</mi><mspace width="0.3em"/><mi>bytes</mi></mrow>
</math>

**متن جایگزین فرمول:** حافظهٔ پایدار نمونه برابر تعداد پارامتر ضرب در چهار بایت وزن، چهار بایت گرادیان و هشت بایت برای دو moment آدام دبلیو است؛ یعنی شانزده P بایت.

برای `P=117,350`، وزن‌ها `469,400` بایت، گرادیان‌ها `469,400` و دو moment `938,800` بایت می‌شوند؛ مجموع `1,877,600` بایت یا `1.790619 MiB` است (`1 MiB=1,048,576` بایت). این عدد optimizer state ساخته‌شده را فرض می‌کند؛ AdamW در آغاز می‌تواند state را lazy بسازد [۶]. خود PyTorch، dtype پارامتر/گرادیان و حالت optimizer نیز مهم‌اند. در BF16/FP16 لزوماً همهٔ اجزا نصف نمی‌شوند؛ master weights، optimizer state و activation ممکن است dtype متفاوت داشته باشند. فصل ۴۵ آن مصالحه را جدا می‌کند.

این برآورد **شامل activation، logits، ورودی/هدف، mask، فضای موقت kernel، checkpoint، allocator، fragmentation و حافظهٔ رزروشدهٔ runtime نیست**. ۱٫۷۹ MiB را «VRAM لازم برای آموزش» ننامید. این فقط سه ردهٔ پایدار وزن/گرادیان/حالت را با فرض‌های مشخص می‌شمارد.

## ۹. یک sweep کوچک، تفاوت رشد خطی و درجه‌دوم را نشان می‌دهد

در sweep پروژه، `N=16`, `V=102`, `d=64`, `h=4`, `f=256`, `L=2` و FP32 برای tensorهای مرجع ثابت است؛ فقط `C=T` از ۳۲ به ۶۴ و ۱۲۸ می‌رود. تخمین پایدار با ۴+۴+۸ بایت به‌ازای هر پارامتر است. ستون‌های activation سه tensor مرجع را جدا می‌کنند:

| `C=T` | پارامتر دقیق | وزن+گرادیان+AdamW | score-equivalent | FFN پنهان | logits | جمع tensorهای مرجع |
|---:|---:|---:|---:|---:|---:|---:|
| ۳۲ | ۱۱۵٬۳۰۲ | ۱٫۷۶ MiB | ۰٫۵۰ MiB | ۱٫۰۰ MiB | ۰٫۲۰ MiB | ۱٫۷۰ MiB |
| ۶۴ | ۱۱۷٬۳۵۰ | ۱٫۷۹ MiB | ۲٫۰۰ MiB | ۲٫۰۰ MiB | ۰٫۴۰ MiB | ۴٫۴۰ MiB |
| ۱۲۸ | ۱۲۱٬۴۴۶ | ۱٫۸۵ MiB | ۸٫۰۰ MiB | ۴٫۰۰ MiB | ۰٫۸۰ MiB | ۱۲٫۸۰ MiB |

هنگام دوبرابرشدن `T` از ۶۴ به ۱۲۸، تعداد پارامترهای position embedding فقط `64×64=4,096` زیاد می‌شود؛ score-equivalent چهار برابر، FFN مرجع دو برابر و logits نیز دو برابر می‌شود. چرا؟ جدول موقعیت با `C×d` رشد خطی دارد، در حالی که تعداد جفت‌های attention با `T²` تغییر می‌کند. هیچ‌یک از این اعداد زمان اجرا یا اوج حافظهٔ واقعی را نمی‌گوید.

## ۱۰. داده را با پنجرهٔ مدل هم‌طراحی کنیم

در next-token، از stream توکنی `z`، ورودی `x=z[0:T]` و هدف `y=z[1:T+1]` ساخته می‌شود. `BOS` و `EOS` بخشی از قرارداد دنباله‌اند؛ طول را پس از tokenizer بشمارید. اگر یک ردیف کوتاه‌تر از `C` است، می‌توان آن را pad کرد؛ اما padding target نباید در loss مثل توکن زبانیِ درست حساب شود. یا از `ignore_index=pad_id` استفاده کنید یا میانگین loss را فقط روی targetهای معتبر بگیرید [۵]. `key_padding_mask` کلیدهای pad را می‌بندد؛ خودش targetهای pad را از تابع زیان حذف نمی‌کند.

اگر هر نمونه یک رکورد باشد، مرز مستقل و ساده است. اگر اسناد را به یک stream بچسبانید، `EOS` به‌تنهایی مانع آن نیست که توکن‌های سند دوم در لایه‌های بعد به توکن‌های سند اول توجه کنند. اگر هدف استقلال اسناد است، ردیف‌ها را جدا کنید یا mask بلوکی/segment-aware طراحی و آزمون کنید؛ اگر ادامهٔ پیوستهٔ corpus را عمداً می‌خواهید، آن قرارداد را ثبت کنید. split گروهی و حذف تکرار باید پیش از ساخت پنجره انجام شود؛ پنجره‌های هم‌پوشان را تصادفی میان train و test نپراکنید.

## ۱۱. Batch را با targetهای معتبر اندازه بگیریم

اگر همهٔ توالی‌ها پر باشند، batch با `N` ردیف و `T` جایگاه حداکثر `N×T` target در هر update دارد. در حضور padding، batch آخر کوتاه یا نمونه‌های دارای طول متغیر، تعداد target معتبر کم‌تر است. به‌جای گزارش «۳۲ batch» یا «۱۰۰۰ جمله»، این موارد را ثبت کنید: تعداد update، کل target tokenهای معتبر، epoch/گذر بر داده، تعداد نمونه/گروه مستقل و سهم padding.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="سقف targetهای دیده‌شده برابر گام‌های آموزش ضرب در batch و طول دنباله است، اگر همهٔ targetها معتبر باشند">
  <mrow><msub><mi>tokens</mi><mi>seen</mi></msub><mo>≤</mo><mi>steps</mi><mo>×</mo><mi>N</mi><mo>×</mo><mi>T</mi></mrow>
</math>

**متن جایگزین فرمول:** سقف targetهای دیده‌شده برابر گام‌های آموزش ضرب در batch و طول دنباله است، اگر همهٔ targetها معتبر باشند.

برابری فقط وقتی برقرار است که همهٔ جایگاه‌های هدف معتبر باشند. تجمع گرادیان می‌تواند چند microbatch را پیش از یک update ترکیب کند، اما هزینهٔ خواندن داده، dropout، clipping و ترتیب به‌روزرسانی را در هر مقایسه ثبت کنید؛ فصل ۴۴ این موضوع را در حلقهٔ پیش‌آموزش عملی می‌کند. برای نمونهٔ ۱۶رکوردی فصل ۴۰، ساخت Mini GPT بزرگ‌تر از پیکره فقط ظرفیت را بالا می‌برد؛ کمبود تنوع/گروه مستقل را رفع نمی‌کند.

## ۱۲. Context را از توزیع طول و وظیفه انتخاب کنیم

برای corpus واقعی، histogram تعداد token هر رکورد، مرز اسناد، طول dependency موردنیاز و درصد نمونه‌هایی که با `C` قطع می‌شوند را بسنجید. اگر اکثر نمونه‌ها ۳۰ token باشند، `C=2,048` ممکن است padding و هزینه را زیاد کند؛ اگر وظیفه به وابستگی دور نیاز داشته باشد، `C=32` شاید شاهد را ببرد. این‌ها فرضیه‌اند، نه نتیجه از روی طول متن خام. چند طول را روی split یکسان با budget token و update مشخص مقایسه کنید؛ validation برای انتخاب است و test پس از تثبیت یک‌بار استفاده می‌شود [۳].

context معماری، context مؤثر نیست: داشتن جدول موقعیت ۱۲۸تایی فقط اجازه می‌دهد آن شکل ورودی را پردازش کنیم، نه اینکه مدل رابطهٔ دور را یاد گرفته یا درست به‌کار برده باشد. فصل ۳۸ هزینهٔ زمینهٔ بلند و cache استنتاج را جداگانه پوشش می‌دهد. در این پروژه، query positions هم‌زمان آموزش‌پذیرند و هرکدام به prefix خود نگاه می‌کنند؛ طول زمینهٔ واقعی را روی داده و معیار مناسب انتخاب کنید.

## ۱۳. پارامترها را از داده و compute جدا نکنیم

یک مدل پارامتر بیشتر الزاماً بهتر نیست. زیان قابل‌دستیابی به ظرفیت، tokenizer، کیفیت/تنوع corpus، تعداد tokenهای train، schedule، regularization، وظیفه و سقف محاسبه وابسته است. مطالعات scaling law نشان می‌دهند در محدودهٔ مدل‌ها و داده‌های همان آزمایش، اندازهٔ مدل، داده و compute بر هم اثر دارند؛ نتایج را نمی‌توان به هر زبان و پیکربندی تعمیم داد [۸،۹].

کار Hoffmann و همکاران بیش از ۴۰۰ مدل را در دامنهٔ ۷۰ میلیون تا بیش از ۱۶ میلیارد پارامتر و بازهٔ دادهٔ آزمایش‌شدهٔ خود مطالعه کرد؛ در آن بودجه‌بندی compute، نتیجهٔ مقاله بر مقیاس‌دادن هم‌زمان مدل و داده تأکید می‌کند [۹]. این مقاله به‌تنهایی «نسبت ثابت token/پارامتر برای هر کار» نمی‌سازد. برآورد چنین نسبتی برای نمونهٔ ۱۶رکوردی یا ۱۱۷هزارپارامتری ما، بدون دامنهٔ داده/محاسبه و پروتکل، دقت کاذب است. در فصل ۴۴ برنامهٔ آموزش، و در فصل ۴۶ هزینهٔ حرکت از نمونهٔ آموزشی به مقیاس بزرگ‌تر بررسی می‌شود.

## ۱۴. آزمایش را پیش از صرف بودجه طراحی کنیم

برای هر اجرای مقایسه‌ای یک manifest آزمایش بنویسید: شناسه/نسخهٔ کد؛ hash پیکره و splitها؛ نسخه و پیکربندی tokenizer؛ `V,C,d,h,f,L`; تعداد پارامتر؛ batch و tokenهای معتبر در update؛ seed؛ optimizer و schedule؛ سقف update/token؛ زمان/دستگاه؛ و معیارهایی که فقط از train یا validation خوانده می‌شوند. اگر قرار است latency/حافظه اندازه بگیرید، warm-up، dtype، kernel، batch، padding و ابزار اندازه‌گیری را هم ثابت و ثبت کنید.

برای دیدن اثر context، فقط `C` را عوض کنید، ولی token budget و سیاست batch را تا حد امکان کنترل کنید. برای اثر عرض `d`، به یاد داشته باشید parameter count و هزینهٔ FFN/attention نیز تغییر می‌کند؛ آزمایش دیگر تک‌متغیره نیست مگر config را حسابی هم‌تراز کنید. ابتدا یک سؤال کوچک و ابطال‌پذیر انتخاب کنید: «با همین batch و سخت‌افزار، `T=128` از `T=64` چند MiB مرجع اضافه می‌کند؟» پروژه پاسخ محاسباتی‌اش را می‌دهد؛ برای زمان و peak memory باید اجرا و پروفایل واقعی داشت [۷].

## ۱۵. اجرای پروژهٔ قابل‌بازتولید

پروژه از پوشهٔ خودش با Python 3.11+ و PyTorch 2.6.x اجرا می‌شود؛ CPU کافی است. هیچ متن تازه، checkpoint یا دادهٔ شبکه‌ای دریافت نمی‌کند. دستور زیر ۱۱ آزمون قراردادها را اجرا می‌کند، سپس مدل فصل ۳۷ را با ورودی شناسهٔ تصادفی می‌سازد، فرمول شمار را با `numel()` می‌سنجد و یک sweep زمینه چاپ می‌کند:

```bash
cd book-engineering/projects/42-mini-gpt-design
python -m unittest discover -v
python mini_gpt_design.py --context-sweep
```

برای یک پیکربندی دیگر، flagهای `--vocab-size`, `--block-size`, `--d-model`, `--heads`, `--ff-dim`, `--layers`, `--batch-size` و `--sequence-length` را بدهید. برای مثال اگر `--sequence-length` از `--block-size` بزرگ‌تر باشد، اسکریپت باید با خطای پیکربندی متوقف شود. تابع `context_sweep` نیز فقط طول‌های صحیحِ مثبت و یکتا می‌پذیرد؛ مقدار اعشاری، صفر، منفی و بولی را پیش از محاسبه رد می‌کند. flagهای `--parameter-bytes`, `--gradient-bytes`, `--optimizer-state-bytes` و `--activation-bytes` فرض‌های byte estimate را آشکار می‌کنند؛ تغییرشان اندازه‌گیری واقعی را جایگزین نمی‌کند.

در smoke test، نخستین token هر ردیف عمداً غیر-padding است. این نکته مهم است: اگر query جایگاه صفر هم با ماسک علّی به آینده بسته و هم به‌عنوان padding از attention حذف شود، ممکن است برای آن query هیچ key مجازی نماند. در اجرای محلی PyTorch 2.6.0+cpu، ورودی تصادفی که با `pad_id` آغاز می‌شد، logits غیرمتناهی تولید کرد. wrapper همین پروژه ردیف‌های چپ‌pad/all-pad و ماسک‌شدن BOS را رد می‌کند؛ right-padding با پیشوند معتبر مجاز است. دادهٔ خودرگرسیو را با `BOS`/پیشوند معتبر آغاز کنید و finite بودن را روی نسخه/backend خود بسنجید؛ ماژول پایهٔ فصل ۳۷ به‌تنهایی این edge case را خودکار اصلاح نمی‌کند.

## ۱۶. خروجی را چه‌طور بخوانیم؟

روی Python 3.13.16 و PyTorch 2.6.0+cpu، فرمان پیش‌فرض shape ورودی `[16,64]`، logits `[16,64,102]` و همهٔ logits متناهی را گزارش کرد. شمار واقعی با فرمول تطبیق کرد: `117,350` پارامتر. فرض FP32 با AdamW دو-moment، تخمین پایدار `1,877,600` بایت یا `1.790619 MiB` شد. برای `N=16,T=64,L=2,h=4,f=256,V=102`، سه اندازهٔ مرجع score-equivalent، FFN پنهان و logits به‌ترتیب `2,097,152`, `2,097,152`, `417,792` بایت‌اند؛ جمع `4,612,096` بایت یا `4.398438 MiB` است.

در sweep، score-equivalent با `T=32,64,128` به‌ترتیب `0.5,2,8 MiB` و جمع tensorهای مرجع `1.699219,4.398438,12.796875 MiB` شد. این **خروجی ماشین‌حساب شکل‌ها** است، نه اندازه‌گیری حافظهٔ training یا benchmark latency. پروژه optimizer نمی‌سازد، دادهٔ فصل ۴۰ را آموزش نمی‌دهد، loss/perplexity حساب نمی‌کند و متن تولید نمی‌کند. وزن‌ها با تصادف مقداردهی می‌شوند؛ `finite=True` فقط smoke test عددی در همین محیط است.

## ۱۷. خطاهای طراحی که به عددی خوش‌ظاهر ختم می‌شوند

| برداشت نادرست | چرا گمراه‌کننده است؟ | بررسی مناسب |
|---|---|---|
| «۱۱۷K پارامتر یعنی حدود ۱٫۸ MiB VRAM» | عدد دوم فقط وزن، گرادیان و دو moment را با فرض FP32 می‌شمارد | activation، logits، workspace و peak را روی دستگاه بسنجید |
| «C=128 یعنی مدل زمینهٔ دور را فهمیده» | موقعیت قابل‌نمایش با زمینهٔ مؤثر یکی نیست | آزمون وظیفه‌ای با dependency دور و validation مستقل |
| «EOS بین اسناد attention را reset می‌کند» | توکن‌های بعدی هنوز ممکن است به سند قبل نگاه کنند | ردیف جدا یا mask بلوکی را تست کنید |
| «mask padding، loss روی PAD را حذف می‌کند» | ماسک attention و mask target دو نقش دارند | targetهای PAD را از loss کنار بگذارید |
| «هر رأس توجه پارامتر تازه اضافه می‌کند» | با `d` ثابت، projection ترکیبیِ این MHA اندازهٔ ثابت دارد | شمار واقعی ماژول را با فرمول تطبیق دهید |
| «اولین توکن می‌تواند PAD باشد؛ بقیهٔ mask کافی است» | query اول ممکن است هیچ key مجازی نداشته باشد | BOS معتبر بگذارید و finite بودن را روی backend بسنجید |
| «context sweep سرعت مدل را اندازه گرفت» | پروژه فقط تعداد خانه‌های چند tensor را حساب می‌کند | profiler یا benchmark کنترل‌شده روی سخت‌افزار هدف |

پیکربندی آموزشی کوچک وقتی مفید است که خطا را آشکار کند، نه اینکه با عدد کم، ادعای محصول بسازد. به‌ویژه split، گروه، مجوز، و انتخاب test را از فصل‌های ۴۰–۴۱ حفظ کنید؛ تغییر مدل دلیل شکستن مرزهای داده نیست.

## ۱۸. تمرین‌ها و معیار عبور

۱. برای config پیش‌فرض، `P` را از جدول اجزا دوباره حساب کنید؛ نشان دهید چرا سر خروجی `dV+V` است و چرا با embedding مشترک فرمول باید عوض شود.

۲. اگر `C` را از ۶۴ به ۱۲۸ تغییر دهیم ولی بقیهٔ config ثابت بماند، تعداد پارامتر position embedding چند واحد زیاد می‌شود؟ سهم این تغییر از کل `P` چند درصد است؟

۳. با `N=16`, `h=4`, `L=2`, FP32، اندازهٔ score-equivalent را برای `T=32,64,128` حساب کنید. کدام نسبت درجه‌دوم است و چرا آن را peak VRAM نمی‌نامیم؟

۴. برای batch دارای pad، توضیح دهید چرا `key_padding_mask` به‌تنهایی targetهای PAD را از cross-entropy حذف نمی‌کند. یک راه صریح برای نادیده‌گرفتن آن‌ها پیشنهاد دهید.

۵. دو سند را با EOS به هم بچسبانید. آیا توکن‌های سند دوم در Decoder-only می‌توانند به سند اول توجه کنند؟ برای جداسازی قطعی چه تغییر داده/ماسکی لازم است؟

۶. روی کاغذ بررسی کنید اگر ردیف ورودی با PAD آغاز شود، query نخست در ترکیب mask علّی و padding چه keyهایی دارد. سپس نسخهٔ پروژه را اجرا و تفاوت prefix معتبر و prefix تماماً pad را روی خروجی finite بررسی کنید؛ test اصلی را با baseline تصادفی قاطی نکنید.

۷. برای corpus واقعی خود، `C=32` و `C=128` را مقایسه کنید: histogram طول token، درصد برش/pad، هزینهٔ مرجع و یک معیار validation را طرح کنید. کدام عوامل باید ثابت بمانند؟

۸. فرض کنید ۵۰۰ update با batch=16 و T=64 دارید و همهٔ targetها معتبرند. حداکثر چند target دیده می‌شود؟ چه چیزی در صورت padding یا تکرار نمونه‌ها از این عدد قابل استنتاج نیست؟

**معیار عبور:** دست‌کم ۶ پاسخ از ۸ باید هم واحد و هم فرض را روشن کند؛ فرمول پارامتر با شمار واقعی پروژه برابر باشد؛ آزمون shape و عدم نشت آینده موفق بماند؛ sweep را به‌عنوان تخمین tensor، نه GPU benchmark، تفسیر کنید؛ و برای دادهٔ واقعی، مرز اسناد و targetهای padding را جداگانه توضیح دهید. پاسخ تشریحی در [پاسخ‌نامهٔ فصل ۴۲](book-engineering/answers/42-mini-gpt-fa.md) است؛ ابتدا بدون نگاه‌کردن حل کنید.

### واژه‌نامهٔ کوتاه

- **پارامتر (parameter):** مقدار آموختنی در ماژول مدل، مانند وزن یا bias.
- **Context length:** شمار tokenهای واقعی در یک نمونه؛ با واژه یا پنجرهٔ اسمی یکی نیست.
- **بودجه (budget):** فرض‌های شمارشی/بایتی که پیش از آزمایش ثبت می‌شوند.
- **Score-equivalent:** اندازهٔ مرجع یک tensor بر اساس شکل، نه مصرف peak حافظه.
- **Padding mask:** نشانهٔ موقعیت‌های padding برای بستن کلیدهای نامعتبر.

## ۱۹. منابع و وضعیت دانسته‌ها تا ۵ نوامبر ۲۰۲۶

در این فصل، GPT نام یک خانواده/خط معماری الهام‌بخش است، نه اندازهٔ حداقلیِ مقرر. GPT نخستین مقالهٔ OpenAI مدل Decoder چندلایه با masked self-attention را توصیف کرد [۲]؛ GPT-2 در گزارشش چند اندازهٔ مدل و نتیجه‌های همان corpus/benchmark را بررسی کرد [۳]. اعداد آن مقالات مشخصات پژوهش‌اند، نه نسخهٔ کوچک این درس. مقالهٔ Transformer مبنای causal decoder و محاسبهٔ موازی آموزش را می‌دهد [۱].

فرمول پروژه از شکل ماژول‌های PyTorch 2.6 (`Embedding`, `Linear`, `LayerNorm`, `MultiheadAttention`) به‌دست آمده است [۴،۵]. فرض دو moment به API/algorithm AdamW مربوط است، اما بایت واقعی تابع dtype و optimizer state اجراست [۶]. برای peak و زمان باید workload را در profiler بسنجید، نه این جدول را جایگزین اندازه‌گیری کنید [۷]. مطالعات scaling law [۸،۹] دلیل می‌دهند که مدل و داده/compute را با هم برنامه‌ریزی کنیم؛ هیچ‌یک در این درس اندازهٔ «بهینهٔ» corpus کوچک فارسی را تعیین نمی‌کنند. تازه‌بودن عدد به‌خودی‌خود آن را به دستورالعمل عمومی تبدیل نمی‌کند.

1. Vaswani, A. و همکاران (۲۰۱۷)، “Attention Is All You Need”، NeurIPS؛ [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)، مراجعهٔ ۵ نوامبر ۲۰۲۶.
2. Radford, A., Narasimhan, K., Salimans, T., & Sutskever, I. (۲۰۱۸)، “Improving Language Understanding by Generative Pre-Training”، گزارش پژوهشی OpenAI؛ [PDF رسمی](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf)، مراجعهٔ ۵ نوامبر ۲۰۲۶.
3. Radford, A. و همکاران (۲۰۱۹)، “Language Models are Unsupervised Multitask Learners”، گزارش پژوهشی OpenAI؛ [PDF رسمی GPT-2](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)، مراجعهٔ ۵ نوامبر ۲۰۲۶.
4. PyTorch (نسخهٔ ۲٫۶)، [`nn.MultiheadAttention`](https://docs.pytorch.org/docs/2.6/generated/torch.nn.MultiheadAttention.html): شکل ورودی، `batch_first`, ماسک علّی/پدینگ و مسیرهای بهینه؛ مراجعهٔ ۵ نوامبر ۲۰۲۶.
5. PyTorch (نسخهٔ ۲٫۶)، [`nn.Embedding`](https://docs.pytorch.org/docs/2.6/generated/torch.nn.Embedding.html)، [`nn.Linear`](https://docs.pytorch.org/docs/2.6/generated/torch.nn.Linear.html)، [`nn.LayerNorm`](https://docs.pytorch.org/docs/2.6/generated/torch.nn.LayerNorm.html) و [`CrossEntropyLoss`](https://docs.pytorch.org/docs/2.6/generated/torch.nn.CrossEntropyLoss.html)؛ مراجعهٔ ۵ نوامبر ۲۰۲۶.
6. PyTorch (نسخهٔ ۲٫۶)، [`torch.optim.AdamW`](https://docs.pytorch.org/docs/2.6/generated/torch.optim.AdamW.html)، مراجعهٔ ۵ نوامبر ۲۰۲۶.
7. PyTorch (نسخهٔ ۲٫۶)، [Profiler](https://docs.pytorch.org/docs/2.6/profiler.html)، ثبت شکل/حافظهٔ tensor و رویدادهای اجرا؛ مراجعهٔ ۵ نوامبر ۲۰۲۶.
8. Kaplan, J. و همکاران (۲۰۲۰)، “Scaling Laws for Neural Language Models”، [arXiv:2001.08361](https://arxiv.org/abs/2001.08361)، مراجعهٔ ۵ نوامبر ۲۰۲۶.
9. Hoffmann, J. و همکاران (۲۰۲۲)، “Training Compute-Optimal Large Language Models”، *NeurIPS 2022*؛ [arXiv:2203.15556](https://arxiv.org/abs/2203.15556)، مراجعهٔ ۵ نوامبر ۲۰۲۶.

**ادامهٔ مسیر:** فصل ۴۳ کیفیت، مجوز و آلودگی corpus را می‌سنجد؛ فصل ۴۴ همین ایدهٔ طراحی را به حلقهٔ پیش‌آموزش و schedule می‌برد. در این پروژه هنوز training، checkpoint یا ادعای کاربرد مدل انجام نشده است.

## ۲۰. پیوست: کد کامل ماشین‌حساب طراحی

فایل پیوست عیناً از `projects/42-mini-gpt-design/mini_gpt_design.py` آمده است و مدل Decoder-only را از پروژهٔ فصل ۳۷ reuse می‌کند. آزمون‌های واحد در همان پوشه‌اند.

```python
"""Design and budget a tiny GPT-like decoder using chapter 37's tested model.

This script does not train a language model. It checks a configuration, verifies
its exact parameter count against the existing decoder-only implementation,
performs one random-token shape smoke test, and estimates clearly labeled memory
proxies. No data is downloaded.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
import sys

import torch

# Reuse, rather than fork, the decoder-only architecture tested in chapter 37.
CHAPTER_37_PROJECT = Path(__file__).resolve().parents[1] / "37-encoder-decoder"
if str(CHAPTER_37_PROJECT) not in sys.path:
    sys.path.insert(0, str(CHAPTER_37_PROJECT))

from transformer_architectures import DecoderOnlyLanguageModel  # noqa: E402


@dataclass(frozen=True)
class ModelConfig:
    """Configuration for the chapter-37 decoder-only teaching model."""

    vocab_size: int = 102
    block_size: int = 64
    d_model: int = 64
    num_heads: int = 4
    ff_dim: int = 256
    num_layers: int = 2
    pad_id: int = 0

    def validate(self) -> None:
        positive = {
            "vocab_size": self.vocab_size,
            "block_size": self.block_size,
            "d_model": self.d_model,
            "num_heads": self.num_heads,
            "ff_dim": self.ff_dim,
            "num_layers": self.num_layers,
        }
        for name, value in positive.items():
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.vocab_size < 2:
            raise ValueError("vocab_size must be at least 2")
        if self.d_model % self.num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        if isinstance(self.pad_id, bool) or not isinstance(self.pad_id, int):
            raise ValueError("pad_id must be an integer")
        if not 0 <= self.pad_id < self.vocab_size:
            raise ValueError("pad_id must be a valid vocabulary id")


def parameter_breakdown(config: ModelConfig) -> dict[str, int]:
    """Return exact parameter counts for chapter 37's untied, biased model."""
    config.validate()
    vocab, width, context = config.vocab_size, config.d_model, config.block_size
    attention_per_block = 4 * width * width + 4 * width
    norms_per_block = 4 * width  # two LayerNorms, each with scale and bias
    ffn_per_block = 2 * width * config.ff_dim + config.ff_dim + width
    block_per_layer = attention_per_block + norms_per_block + ffn_per_block
    parts = {
        "token_embedding": vocab * width,
        "position_embedding": context * width,
        "attention_per_block": attention_per_block,
        "norms_per_block": norms_per_block,
        "ffn_per_block": ffn_per_block,
        "all_transformer_blocks": config.num_layers * block_per_layer,
        "final_layer_norm": 2 * width,
        "untied_lm_head": width * vocab + vocab,
    }
    parts["total"] = (
        parts["token_embedding"]
        + parts["position_embedding"]
        + parts["all_transformer_blocks"]
        + parts["final_layer_norm"]
        + parts["untied_lm_head"]
    )
    return parts


class NonPaddingPrefixDecoder(DecoderOnlyLanguageModel):
    """Chapter-37 decoder plus a guard against rows starting with a masked key."""

    def forward(
        self,
        token_ids: torch.Tensor,
        padding_mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        if isinstance(token_ids, torch.Tensor) and token_ids.ndim == 2:
            if token_ids.shape[0] > 0 and token_ids.shape[1] > 0:
                if bool(token_ids[:, 0].eq(self.pad_id).any().item()):
                    raise ValueError(
                        "each causal sequence must start with a non-padding prefix token (for example BOS)"
                    )
                if (
                    isinstance(padding_mask, torch.Tensor)
                    and padding_mask.dtype == torch.bool
                    and tuple(padding_mask.shape) == tuple(token_ids.shape)
                    and bool(padding_mask[:, 0].any().item())
                ):
                    raise ValueError("the first prefix token cannot be masked as padding")
        return super().forward(token_ids, padding_mask=padding_mask)


def build_model(config: ModelConfig) -> DecoderOnlyLanguageModel:
    """Reuse chapter 37's model with an explicit non-padding-prefix guard."""
    config.validate()
    return NonPaddingPrefixDecoder(
        vocab_size=config.vocab_size,
        d_model=config.d_model,
        num_heads=config.num_heads,
        ff_dim=config.ff_dim,
        num_layers=config.num_layers,
        max_len=config.block_size,
        pad_id=config.pad_id,
    )


def count_parameters(model: torch.nn.Module) -> int:
    """Count trainable and non-trainable model parameters once each."""
    return sum(parameter.numel() for parameter in model.parameters())


def _mib(byte_count: int) -> float:
    return round(byte_count / (1024 ** 2), 6)


def estimate_budget(
    config: ModelConfig,
    *,
    batch_size: int,
    sequence_length: int,
    parameter_bytes: int = 4,
    gradient_bytes: int = 4,
    optimizer_state_bytes_per_parameter: int = 8,
    activation_bytes: int = 4,
) -> dict:
    """Estimate persistent bytes and named tensor-size proxies, not peak VRAM.

    The default persistent estimate assumes FP32 parameters and gradients plus
    two FP32 AdamW moments. The score-equivalent, FFN-hidden, and logits sizes
    describe one tensor of each named shape per layer (or one logits tensor);
    they are not a peak-memory measurement or a prediction of kernel allocation.
    """
    config.validate()
    integer_values = {
        "batch_size": batch_size,
        "sequence_length": sequence_length,
        "parameter_bytes": parameter_bytes,
        "gradient_bytes": gradient_bytes,
        "optimizer_state_bytes_per_parameter": optimizer_state_bytes_per_parameter,
        "activation_bytes": activation_bytes,
    }
    for name, value in integer_values.items():
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    if sequence_length > config.block_size:
        raise ValueError("sequence_length exceeds configured block_size")

    parameters = parameter_breakdown(config)["total"]
    parameter_storage = parameters * parameter_bytes
    gradient_storage = parameters * gradient_bytes
    optimizer_storage = parameters * optimizer_state_bytes_per_parameter
    persistent = parameter_storage + gradient_storage + optimizer_storage

    # Shape-based reference sizes for dense score-equivalent, FFN, and logits tensors.
    score_equivalent = (
        config.num_layers * batch_size * config.num_heads
        * sequence_length * sequence_length * activation_bytes
    )
    ffn_hidden = (
        config.num_layers * batch_size * sequence_length
        * config.ff_dim * activation_bytes
    )
    logits = batch_size * sequence_length * config.vocab_size * activation_bytes
    reference_activations = score_equivalent + ffn_hidden + logits
    return {
        "parameter_count": parameters,
        "parameter_bytes": parameter_storage,
        "gradient_bytes": gradient_storage,
        "adamw_state_bytes": optimizer_storage,
        "persistent_bytes": persistent,
        "persistent_mib": _mib(persistent),
        "attention_score_equivalent_bytes": score_equivalent,
        "ffn_hidden_bytes": ffn_hidden,
        "logits_bytes": logits,
        "reference_activation_bytes": reference_activations,
        "reference_activation_mib": _mib(reference_activations),
        "assumptions": {
            "parameter_bytes_per_value": parameter_bytes,
            "gradient_bytes_per_value": gradient_bytes,
            "adamw_state_bytes_per_parameter": optimizer_state_bytes_per_parameter,
            "activation_bytes_per_value": activation_bytes,
            "adamw_states": "two moment tensors; assumes both are allocated",
            "activation_note": (
                "shape-equivalent tensor sizes only; not peak memory, not an allocation "
                "trace, and not necessarily materialized by an optimized attention kernel"
            ),
            "excluded": [
                "optimizer metadata and allocator overhead",
                "input/target IDs, masks, residuals, Q/K/V, gradients of activations",
                "temporary workspaces, fragmentation, and device/runtime reservations",
            ],
        },
    }


def context_sweep(
    config: ModelConfig,
    context_lengths: tuple[int, ...] = (32, 64, 128),
    *,
    batch_size: int = 16,
    parameter_bytes: int = 4,
    gradient_bytes: int = 4,
    optimizer_state_bytes_per_parameter: int = 8,
    activation_bytes: int = 4,
) -> list[dict]:
    """Compare configurations whose maximum and actual sequence lengths match."""
    if not context_lengths:
        raise ValueError("context_lengths must not be empty")
    if any(isinstance(length, bool) or not isinstance(length, int) or length < 1 for length in context_lengths):
        raise ValueError("context_lengths must contain positive integers")
    if len(set(context_lengths)) != len(context_lengths):
        raise ValueError("context_lengths must be unique")
    rows = []
    for length in context_lengths:
        trial = replace(config, block_size=length)
        report = estimate_budget(
            trial,
            batch_size=batch_size,
            sequence_length=length,
            parameter_bytes=parameter_bytes,
            gradient_bytes=gradient_bytes,
            optimizer_state_bytes_per_parameter=optimizer_state_bytes_per_parameter,
            activation_bytes=activation_bytes,
        )
        rows.append({"context_length": length, **report})
    return rows


def design_report(
    config: ModelConfig,
    *,
    batch_size: int = 16,
    sequence_length: int | None = None,
    parameter_bytes: int = 4,
    gradient_bytes: int = 4,
    optimizer_state_bytes_per_parameter: int = 8,
    activation_bytes: int = 4,
) -> dict:
    """Check the formula against the module and return a random-token smoke report."""
    config.validate()
    sequence_length = config.block_size if sequence_length is None else sequence_length
    budget = estimate_budget(
        config,
        batch_size=batch_size,
        sequence_length=sequence_length,
        parameter_bytes=parameter_bytes,
        gradient_bytes=gradient_bytes,
        optimizer_state_bytes_per_parameter=optimizer_state_bytes_per_parameter,
        activation_bytes=activation_bytes,
    )
    model = build_model(config).eval()
    actual = count_parameters(model)
    formula = parameter_breakdown(config)["total"]
    if actual != formula:
        raise RuntimeError(f"parameter formula {formula} != model parameter count {actual}")
    torch.manual_seed(42)
    token_ids = torch.randint(0, config.vocab_size, (batch_size, sequence_length), dtype=torch.long)
    # A causal attention row with no visible non-padding key is undefined. The
    # real next-token sequence starts with a non-padding BOS/prefix token.
    token_ids[:, 0] = (config.pad_id + 1) % config.vocab_size
    with torch.no_grad():
        logits = model(token_ids)
    return {
        "config": asdict(config),
        "input_shape": list(token_ids.shape),
        "logits_shape": list(logits.shape),
        "all_logits_finite": bool(torch.isfinite(logits).all().item()),
        "parameter_breakdown": parameter_breakdown(config),
        "parameter_count_actual": actual,
        "budget": budget,
        "scope": "one random-token forward smoke test; no corpus, training, or quality evaluation",
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Design and budget a tiny GPT-like decoder")
    parser.add_argument("--vocab-size", type=int, default=102)
    parser.add_argument("--block-size", type=int, default=64)
    parser.add_argument("--d-model", type=int, default=64)
    parser.add_argument("--heads", type=int, default=4)
    parser.add_argument("--ff-dim", type=int, default=256)
    parser.add_argument("--layers", type=int, default=2)
    parser.add_argument("--pad-id", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--sequence-length", type=int, default=None)
    parser.add_argument("--parameter-bytes", type=int, default=4)
    parser.add_argument("--gradient-bytes", type=int, default=4)
    parser.add_argument("--optimizer-state-bytes", type=int, default=8)
    parser.add_argument("--activation-bytes", type=int, default=4)
    parser.add_argument("--context-sweep", action="store_true", help="also compare contexts 32, 64, 128")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    config = ModelConfig(
        vocab_size=args.vocab_size,
        block_size=args.block_size,
        d_model=args.d_model,
        num_heads=args.heads,
        ff_dim=args.ff_dim,
        num_layers=args.layers,
        pad_id=args.pad_id,
    )
    report = design_report(
        config,
        batch_size=args.batch_size,
        sequence_length=args.sequence_length,
        parameter_bytes=args.parameter_bytes,
        gradient_bytes=args.gradient_bytes,
        optimizer_state_bytes_per_parameter=args.optimizer_state_bytes,
        activation_bytes=args.activation_bytes,
    )
    if args.context_sweep:
        report["context_sweep"] = context_sweep(
            config,
            batch_size=args.batch_size,
            parameter_bytes=args.parameter_bytes,
            gradient_bytes=args.gradient_bytes,
            optimizer_state_bytes_per_parameter=args.optimizer_state_bytes,
            activation_bytes=args.activation_bytes,
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```
