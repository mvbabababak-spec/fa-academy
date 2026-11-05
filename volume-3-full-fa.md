# هنر و علم ساخت هوش — جلد سوم

**The Art & Science of Building Intelligence | Babak & Ai**

وضعیت: ۱۴ فصل در نقشه؛ 7 فصل از ۱۴ فصل تا این انتشار نگارش و آزموده شده‌اند. این فایل Markdown است؛ PDF و EPUB تولید نشده‌اند.

## فهرست فصل‌های منتشرشده

- فصل 1 (سراسری 33) — توکن‌سازی، واژگان و توکن‌های ویژه
- فصل 2 (سراسری 34) — Attention، Query/Key/Value و پیاده‌سازی ماتریسی
- فصل 3 (سراسری 35) — Self-Attention، چندسری و ماسک علّی
- فصل 4 (سراسری 36) — موقعیت، RoPE، اتصال باقیمانده، LayerNorm و FFN
- فصل 5 (سراسری 37) — Encoder، Decoder و مدل‌های Encoder–Decoder
- فصل 6 (سراسری 38) — زمینه بلند، KV Cache، GQA، Sparse Attention و MoE
- فصل 7 (سراسری 39) — Transformer چندوجهی: اتصال رمزگذارهای تصویر و صوت

---

# جلد سوم، فصل ۱ — توکن‌سازی، واژگان و شناسه‌های ویژه

**The Art & Science of Building Intelligence | Babak & Ai | فصل سراسری ۳۳ از نقشه پنج‌جلدی**

**تاریخ مرجع: ۵ نوامبر ۲۰۲۶؛ منابع برخط در همین تاریخ بازبینی شدند.**

## ۱. از متن تا ورودی مدل: شش مرحله را یکی نگیریم

مدل زبانی رشته‌ای از نویسه‌های نمایشی را مستقیماً «نمی‌خواند». پیش‌پردازش متن، توکن‌سازی و تبدیل به شناسه، به مدل دنباله‌ای از عددهای صحیح می‌دهد؛ سپس یک جدول تعبیه، برای هر شناسه برداری قابل‌آموزش فراهم می‌کند. شبکه عصبی روی بردارها و دنباله پردازش می‌کند. این مراحل مرتبط‌اند، اما یکی نیستند: توکن‌ساز نه معنا را تضمین می‌کند و نه به‌تنهایی بردار یا پاسخ مدل را می‌سازد.

**پیش‌نیاز:** رشته، تابع و UTF-8 در جلد اول؛ شناسه و تعبیه (Embedding) در فصل ۱۱ جلد دوم، برابر فصل سراسری ۳۲. **هدف:** مسیر متن تا شناسه را توصیف کنید، روش‌های واژه‌سازی را مقایسه کنید، یک Byte-Level BPE کوچک بسازید، شناسه‌های ویژه را بشناسید و ارتباط واژگان و جدول تعبیه را آزمون کنید. **پس از این فصل:** در فصل ۳۴ امتیازهای Query/Key/Value را روی نمایش برداری می‌سازیم؛ این فصل سازوکار Attention را آموزش نمی‌دهد.

نمای ریاضیِ مرحله توکن‌سازی چنین است: یک متن x به دنباله‌ای از شناسه‌های صحیح در واژگان با اندازه V تبدیل می‌شود؛ تعداد شناسه‌ها می‌تواند از تعداد واژه‌ها یا نویسه‌های متن بیشتر یا کمتر باشد.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="توکن‌ساز T متن x را به دنباله i یک تا i ال تبدیل می‌کند؛ هر شناسه بین صفر و وی منهای یک است"><mrow><mi>T</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>=</mo><mo>(</mo><msub><mi>i</mi><mn>1</mn></msub><mo>,</mo><msub><mi>i</mi><mn>2</mn></msub><mo>,</mo><mi>…</mi><mo>,</mo><msub><mi>i</mi><mi>L</mi></msub><mo>)</mo><mo>,</mo><mspace width="0.5em"/><msub><mi>i</mi><mi>j</mi></msub><mo>∈</mo><mo>{</mo><mn>0</mn><mo>,</mo><mi>…</mi><mo>,</mo><mi>V</mi><mo>−</mo><mn>1</mn><mo>}</mo></mrow></math>

متن جایگزین فرمول: `T(x)=(i₁,…,iL)`؛ هر `ij` یکی از شناسه‌های صفر تا `V−1` است. نماد `L` طول دنباله توکن‌ها و `V` اندازه واژگان این توکن‌ساز است.

![شکل ۳-۱-۱ — نمونه آموزشی Byte-Level BPE: دو نمونه abab و abac؛ پس از سه بار مشاهده جفت ab، ادغام ab شناسه ۲۶۰ می‌گیرد و abab به [۲۶۰، ۲۶۰] تبدیل می‌شود؛ سپس شناسه‌ها به جدول تعبیه می‌روند. شناسه‌ها متعلق به واژگان اسباب‌بازی این شکل‌اند.](assets/images/babak-ai/v3-ch01-tokenization.webp)

**شکل ۳-۱-۱ — از متن به شناسه و بردار.** راهنمای برچسب‌های دوزبانه در شکل: «متن ورودی / Raw text»، «پیش‌توکن‌ساز / Pre-tokenizer»، «بایت‌های UTF-8 / UTF-8 bytes»، «ادغام پرتکرار / Frequent merge»، «شناسه توکن / Token IDs»، «جدول تعبیه / Embedding table» و «بردارها / Vectors». در مثال کوچک، `ab` در مجموعه آموزش سه بار کنار هم می‌آید؛ ادغام نخست شناسه ۲۶۰ دارد و `abab` به دو توکن `ab` تبدیل می‌شود. شناسه و اندازه بردار نمونه‌اند، نه شناسه‌های مدل زبانی واقعی.

یک خط لوله متداول می‌تواند این مراحل را داشته باشد: ۱) نرمال‌سازی اختیاری، ۲) پیش‌توکن‌سازی (Pre-tokenization)، ۳) الگوریتم واژه‌سازی، ۴) افزودن نشانه‌های ویژه و تبدیل به شناسه، ۵) افزودن تعبیه و ورودی‌های دیگر مدل. کتابخانه‌های مختلف ممکن است مراحل را ترکیب یا جابه‌جا کنند؛ قرارداد دقیق همان مدل را بخوانید [۳، ۵].

## ۲. یونیکد، فارسی و تفاوت «نویسه» با «بایت»

رشته در Python توالی کدپوینت‌های Unicode است؛ کدپوینت، بایت UTF-8 و نویسه‌ای که چشم یک واحد می‌بیند الزاماً یکسان نیستند. یک حرف می‌تواند با علامت ترکیبی نمایش داده شود؛ یک ایموجی هم ممکن است چند کدپوینت داشته باشد. قواعد مرزبندی نویسه دیداری، واژه و جمله در Unicode جداگانه تعریف می‌شوند و برای هر زبان یا کاربرد می‌توان به قواعد عمومی نیاز داشت [۸]. بنابراین `len(text)` در Python تعداد کدپوینت‌ها را می‌شمارد، نه لزوماً تعداد نویسه‌های دیداری و نه تعداد توکن‌های مدل.

در فارسی، فاصله و نیم‌فاصله، اعراب، رقم‌ها و نویسه‌های عربیِ ظاهراً مشابه اهمیت دارند. برای نمونه، «ی» فارسی و «ي» عربی، یا «ک» فارسی و «ك» عربی، کدپوینت‌های متفاوت‌اند؛ نیم‌فاصله U+200C نیز از فاصله معمولی جداست. برخی متن‌ها این تفاوت‌ها را ناخواسته از صفحه‌کلید یا منبع داده به ارث می‌برند. تبدیل خودکار همه آن‌ها به یک صورت می‌تواند در یک مجموعه سودمند و در مجموعه دیگر تغییر معنای شناسه، نام یا متن اصلی باشد؛ تصمیم باید با قرارداد داده و آزمون روشن گرفته شود.

نرمال‌سازی NFC شکل‌های هم‌ارز کانونی را یکسان می‌کند؛ NFKC افزون بر آن، هم‌ارزی‌های سازگاری را نیز اعمال می‌کند و در نتیجه ممکن است تمایزهای نمایشی یا معنایی را حذف کند. استاندارد Unicode شکل‌های نرمال‌سازی را تعریف می‌کند، اما انتخاب شکل مناسب را برای هر مدل تضمین نمی‌کند [۷]. اگر توکن‌ساز متن را تغییر دهد، بازسازی معمولاً متن نرمال‌شده را می‌دهد، نه لزوماً همان بایت‌های ورودی. برای آموزش و استنتاج باید سیاست نرمال‌سازی یکسان باشد؛ برای بازبینی سند اصلی، متن مبنا و نگاشت offsetها را نگه دارید.

نمونه پایتون برای دیدن تفاوت، نه برای اعمال خودکار بر هر متن:

```python
import unicodedata

text = "A\u030a"  # A و علامت حلقه ترکیبی
print(len(text), len(text.encode("utf-8")))
print(unicodedata.normalize("NFC", text))
```

در مثال، دو کدپوینت قبل از نرمال‌سازی به یک نویسه مرکب در NFC تبدیل می‌شوند؛ تعداد بایت‌ها هم با تعداد کدپوینت‌ها برابر نیست. هر نرمال‌ساز باید در فایل تنظیمات توکن‌ساز ثبت و روی ورودی‌های مرزی آزموده شود.

## ۳. پیش‌توکن‌سازی: مرزهای اولیه

پیش‌توکن‌ساز (Pre-tokenizer) متن را با قواعدی مثل فاصله، رقم یا نشانه‌گذاری به قطعه‌های اولیه می‌شکند. این کار می‌تواند جلوی ادغام میان دسته‌های خاص را بگیرد و سرعت آموزش واژگان را بالا ببرد. اما «واژه» تعریف طبیعی و یکسانی برای همه زبان‌ها نیست: اتصال‌واژه، پسوند، نشانه‌گذاری، عدد و کد به تصمیم‌های متفاوت نیاز دارند. یک الگوی ساده Python برای آموزش مناسب است، ولی جایگزین توکن‌ساز مدل نیست [۳].

برای مثال، `AI, model!` را می‌توان به قطعه‌های `AI`، `,`، فاصله، `model` و `!` تقسیم کرد؛ توکن‌ساز دیگری شاید فاصله را به ابتدای قطعه بعدی بچسباند. این تفاوت کوچک روی شناسه‌ها و طول ورودی اثر می‌گذارد. در پروژه این فصل از الگوی آموزشی استفاده می‌کنیم که فاصله‌های پیاپی، دنباله‌های `\w` و هر نویسه غیرواژه‌ای را جدا می‌کند و با آزمون ثابت می‌کند هیچ متن ورودی حذف یا جابه‌جا نشده است. این الگو مرزبندی دقیق Unicode یا مدل زبانی تجاری نیست.

**نکته:** توکن‌سازی، پیش‌توکن‌سازی و نرمال‌سازی سه واژه برای یک عملیات نیستند. اگر قطعه ورودی در نمودار دیده نمی‌شود، ممکن است در نرمال‌سازی حذف یا در پیش‌توکن‌ساز به قطعه دیگری پیوسته باشد؛ ابتدا تنظیمات هر مرحله را بررسی کنید.

## ۴. واژه، نویسه، زیرواژه و بایت

واژه‌سازی در سطح واژه فرهنگ‌نامه‌ای ساده می‌سازد، اما واژه تازه یا شکل صرفی نادیده را ممکن است به `[UNK]` تبدیل کند؛ نگهداری همه صورت‌ها هم اندازه واژگان را بالا می‌برد. در سطح نویسه، مجموعه پایه کوچک است، اما دنباله بلند می‌شود و مدل باید پیوندهای دورتر را یاد بگیرد. روش زیرواژه (Subword) میان اندازه واژگان و طول دنباله مصالحه برقرار می‌کند؛ قطعه زیرواژه الزاماً تکواژ یا بخش معنادار زبان‌شناختی نیست.

| روش | ایده کلی | مزیت احتمالی | محدودیت و وابستگی |
|---|---|---|---|
| واژه‌محور (Word-level) | نگاشت واژه کامل به شناسه | قطعه‌ها برای انسان خوانا هستند | واژگان بزرگ و مسئله واژه خارج از واژگان |
| نویسه‌محور (Character-level) | یک نویسه یا واحد تعریف‌شده در هر گام | پوشش ساده با الفبای کوچک | دنباله معمولاً بلندتر و «نویسه» وابسته به تعریف است |
| BPE | ادغام تکرارشونده جفت‌های پرتکرار | واژگان ثابت با قطعه‌های پرتکرار | نتیجه به داده آموزش، مرزها و ترتیب ادغام وابسته است |
| WordPiece | واژگان زیرواژه و قطعه‌بندی بر اساس مدل | در برخی خانواده‌ها قطعه‌بندی کارآمد | تابع هدف آموزش و علامت‌گذاری وابسته به مدل است |
| Unigram | انتخاب مجموعه قطعه‌ها با مدل احتمالی | امکان چند قطعه‌بندی محتمل در برخی پیاده‌سازی‌ها | نمونه‌گیری یا مسیر قطعه‌بندی به تنظیمات وابسته است |
| Byte-Level BPE | شروع از ۲۵۶ مقدار بایت و ادغام بایت‌های متوالی | پوشش بایتی برای هر متن UTF-8 معتبر | قطعه منفرد ممکن است خوانا نباشد؛ الگوریتم تولیدی پیچیده‌تر است |

BPE در پردازش زبان برای نمایش واژه‌های نادر به صورت چند زیرواحد به کار رفت [۱]. در Byte-Level BPE، چون هر متن UTF-8 معتبر به دنباله‌ای از بایت‌های ۰ تا ۲۵۵ تبدیل می‌شود، داشتن همه بایت‌های پایه امکان بازنمایی متن دیده‌نشده را می‌دهد؛ این ویژگی یعنی «نویسه ناشناخته لازم نیست»، نه اینکه مدل متن ناشناخته را بفهمد [۴]. الگوریتم‌ها و کتابخانه‌ها یکسان نیستند: WordPiece، BPE و Unigram شیوه آموزش و قطعه‌بندی متفاوت دارند؛ SentencePiece می‌تواند مدل زیرواژه را مستقیماً از جمله خام بسازد و هم BPE و هم Unigram را پشتیبانی می‌کند [۲، ۳].

## ۵. یک گام BPE را دستی دنبال کنیم

مجموعه آموزشی کوچک را `abab` و `abac` بگیرید. برای این مثال ASCII هر حرف یک بایت است. جفت‌های مجاور را بشمارید:

| جفت | تعداد در `abab` | تعداد در `abac` | مجموع |
|---|---:|---:|---:|
| `ab` | ۲ | ۱ | ۳ |
| `ba` | ۱ | ۱ | ۲ |
| `ac` | ۰ | ۱ | ۱ |

پس ادغام نخست `ab` است. به طور کلی در گام t جفتی انتخاب می‌شود که شمار وقوع آن در دنباله‌های آموزشی فعلی بیشترین باشد؛ در صورت تساوی باید قاعده رفع تساوی تثبیت شود.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="در هر گام، جفت پی از مجموعه جفت‌های مجاور که بیشترین تعداد را دارد برای ادغام انتخاب می‌شود"><mrow><msub><mi>p</mi><mi>t</mi></msub><mo>=</mo><munder><mi>argmax</mi><mrow><mo>(</mo><mi>u</mi><mo>,</mo><mi>v</mi><mo>)</mo><mo>∈</mo><mi>P</mi></mrow></munder><msub><mi>count</mi><mi>t</mi></msub><mo>(</mo><mi>u</mi><mo>,</mo><mi>v</mi><mo>)</mo></mrow></math>

متن جایگزین فرمول: در گام `t` جفت مجاور `(u,v)` با بیشترین شمار را از میان جفت‌های مجاز `P` برمی‌گزینیم. این شمار از قطعه‌های آموزش همان گام است، نه از داده آزمون.

در پروژه شناسه ویژه PAD برابر ۰، BOS برابر ۱، EOS برابر ۲ و UNK برابر ۳ است؛ سپس بایت با شناسه `4 + مقدار بایت` نمایش داده می‌شود. پس `a` با کد ASCII برابر ۹۷، شناسه ۱۰۱ دارد و `b` شناسه ۱۰۲. شناسه ادغام اول از `4+256=260` شروع می‌شود. پس از ادغام `ab`، `abab` به `[260, 260]` و `abac` به `[260, 101, 103]` تبدیل می‌شوند. این عددها فقط در همین واژگان اسباب‌بازی درست‌اند؛ با تغییر شناسه‌های ویژه یا ترتیب ادغام، عوض می‌شوند.

## ۶. واژگان، شناسه‌ها و توکن‌های ویژه

واژگان (Vocabulary) نگاشت میان قطعه‌ها و شناسه‌های صحیح است. شناسه فقط جایگاه در یک واژگان مشخص است؛ ۱۰۲ از ۱۰۱ «بزرگ‌تر» یا معنادارتر نیست. شناسه‌های دو توکن‌ساز را بدون واژگان و ترتیب ادغام مشترک نمی‌توان برابر دانست. ذخیره مدل باید هم واژگان و قواعد پیش‌پردازش را داشته باشد و هم، جداگانه، اندازه و وزن‌های شبکه را ثبت کند.

توکن ویژه (Special Token) ورودی ساختاری با شناسه اختصاصی است. نمونه‌های رایج عبارت‌اند از:

| نام رایج | کارکرد معمول | نکته احتیاطی |
|---|---|---|
| BOS | آغاز دنباله یا پیام | همه مدل‌ها آن را نمی‌افزایند |
| EOS | پایان دنباله یا نوبت | معنای پایان در هر مدل و قالب فرق می‌کند |
| PAD | هم‌اندازه‌سازی دسته‌ای | باید ماسک توجه/زیان با قرارداد مدل هماهنگ باشد |
| UNK | نمایش خارج از واژگان | در توکن‌ساز بایتی ممکن است لازم نباشد |
| MASK | نشانه جای خالی برای هدف آموزشی | برای همه مدل‌های مولد علّی به‌کار نمی‌رود |
| SEP و نشانه‌های نقش | جداسازی متن یا نقش‌ها | نام و قالب گفت‌وگو مدل‌محور است |

رشته قابل‌مشاهده مانند `<|bos|>` فقط نگارش انسانی است؛ شناسه داخلی، فهرست ویژه‌ها و رفتار API تعیین می‌کنند که در ورودی واقعاً یک توکن کنترلی باشد یا رشته‌ای معمولی. در کد این فصل، `encode("<|bos|>")` متن را مثل بایت عادی می‌کد؛ BOS فقط با `add_bos=True` افزوده می‌شود. هنگام ساخت قالب گفت‌وگو یا پردازش متن نامطمئن، به ظاهر رشته تکیه نکنید؛ سیاست همان توکن‌ساز و قالب پیام را بیازمایید [۵].

اگر به یک مدل ازپیش‌آموزش‌دیده توکن تازه اضافه کنید، فقط نام آن را به فایل واژگان نوشتن کافی نیست؛ ماتریس تعبیه مدل نیز باید اندازه سازگار بگیرد و ردیف تازه نیازمند مقداردهی و یادگیری مناسب است [۵]. تغییر توکن‌ساز بدون نسخه‌بندی و به‌روزرسانی مدل می‌تواند شناسه‌های قبلی را به ردیف‌های نادرست وصل کند.

## ۷. از شناسه به بردار تعبیه

اگر واژگان `V` توکن و هر بردار `d` مؤلفه داشته باشد، جدول تعبیه `E` شکل `V×d` دارد. برای شناسه `i`، مدل ردیف متناظر را برمی‌دارد؛ این یک lookup است، نه محاسبه معنای واژه از عدد شناسه.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="جدول تعبیه ای شکل وی در دی دارد و بردار موقعیت j برابر ردیف جدول با شناسه توکن تی j است"><mrow><mi>E</mi><mo>∈</mo><msup><mi>ℝ</mi><mrow><mi>V</mi><mo>×</mo><mi>d</mi></mrow></msup><mo>,</mo><mspace width="0.5em"/><msub><mi>x</mi><mi>j</mi></msub><mo>=</mo><msub><mi>E</mi><mrow><msub><mi>t</mi><mi>j</mi></msub><mo>,</mo><mo>:</mo></mrow></msub></mrow></math>

متن جایگزین فرمول: `E` جدولی با `V` ردیف و `d` ستون است؛ برای شناسه `tj`، بردار `xj` از ردیف همان شناسه برداشته می‌شود.

در یک دسته شامل `B` دنباله، هرکدام با طول `L`، شناسه‌ها شکل `B×L` و خروجی lookup شکل `B×L×d` دارند. PyTorch این رفتار را با `nn.Embedding(num_embeddings, embedding_dim)` ارائه می‌کند؛ ورودی آن شاخص‌های صحیح و خروجی، بردارهای ردیف‌های انتخاب‌شده است [۶]. در نمونه ما `V=261`، `d=8` و سه شناسه به ماتریسی با شکل `(3, 8)` می‌رسند.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="شناسه‌ها شکل بی در ال دارند و پس از تعبیه، بردارها شکل بی در ال در دی دارند"><mrow><mi>IDs</mi><mo>∈</mo><msup><mi>ℤ</mi><mrow><mi>B</mi><mo>×</mo><mi>L</mi></mrow></msup><mo>⇒</mo><mi>Embedding</mi><mo>(</mo><mi>IDs</mi><mo>)</mo><mo>∈</mo><msup><mi>ℝ</mi><mrow><mi>B</mi><mo>×</mo><mi>L</mi><mo>×</mo><mi>d</mi></mrow></msup></mrow></math>

متن جایگزین فرمول: ورودی شناسه‌ها شکل `B×L` و خروجی تعبیه شکل `B×L×d` دارد؛ `B` تعداد دنباله‌ها، `L` طول و `d` بُعد بردار است.

```python
import torch
from torch import nn

ids = torch.tensor([260, 101, 103], dtype=torch.long)
embedding = nn.Embedding(num_embeddings=261, embedding_dim=8, padding_idx=0)
vectors = embedding(ids)
print(tuple(vectors.shape))  # (3, 8)
```

این نمونه با CPU اجرا شد و در آزمون پروژه، ردیف PAD از گرادیان به‌روزرسانی نشد. بردار lookup اولیه به شناسه وابسته است و برای یک ID ثابت همان ردیف را برمی‌گرداند؛ بازنمایی زمینه‌ای پس از عبور از لایه‌های شبکه تغییر می‌کند. تعبیه و وضعیت زمینه‌ای (Contextual Hidden State) را یکی نگیرید. کد محاسبه Query/Key/Value در فصل بعد می‌آید.

## ۸. طول دنباله، پنجره متن و سنجش

مدل پنجره ورودی را معمولاً با تعداد توکن‌ها می‌سنجد، نه تعداد واژه‌های فارسی، نویسه‌های دیداری یا بایت‌ها. یک متن واحد در دو توکن‌ساز می‌تواند تعداد و مرزهای متفاوت داشته باشد. بنابراین هنگام برش متن، برآورد هزینه یا مقایسه مدل‌ها، همان توکن‌ساز و نسخه‌ای را به‌کار ببرید که مدل با آن آموزش دیده یا مستند شده است. عدد «متوسط تعداد بایت در توکن» برای همه زبان‌ها، مدل‌ها، کدها و نشانه‌گذاری‌ها ثابت نیست [۴].

در آزمایش همین پروژه می‌توان نسبت تشخیصی تعداد توکن‌های خروجی به بایت‌های UTF-8 را گزارش کرد؛ نسبت کمتر از ۱ به معنی فشرده‌ترشدن همین نمایش بایتی است، نه نمره کیفیت مدل.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="نسبت تشخیصی آر برابر تعداد شناسه‌های خروجی تقسیم بر تعداد بایت‌های متن UTF-8 است"><mrow><mi>r</mi><mo>=</mo><mfrac><msub><mi>N</mi><mtext>tokens</mtext></msub><msub><mi>N</mi><mtext>UTF-8 bytes</mtext></msub></mfrac></mrow></math>

متن جایگزین فرمول: `r = تعداد توکن‌های خروجی / تعداد بایت‌های UTF-8 متن`. این معیار فقط مقایسه قطعه‌بندی همین متن و همین توکن‌ساز است و معیار فهم یا انصاف نیست.

برای بازرسی توکن‌ساز تازه، تنها به میانگین طول بسنده نکنید. چند زبانه و نمونه‌های نیم‌فاصله، رقم فارسی، نشانه‌گذاری، کد، متن ترکیبی و نویسه نادر را جدا بررسی کنید؛ بازسازی رفت‌وبرگشت، نرخ UNK در صورت وجود، توزیع طول دنباله، اندازه واژگان، offsetها، موارد بریده‌شده و مجوز corpus را ثبت کنید. داده ارزیابی باید از آموزش جدا و نماینده کاربرد آینده باشد. طول کمتر یک هدف مهندسی ممکن است، اما به خودی خود فهم بهتر، پوشش برابر زبان‌ها یا کیفیت پایین‌تر/بالاتر را اثبات نمی‌کند.

## ۹. پروژه قابل بازتولید: BPE کوچک روی CPU

پروژه `book-engineering/projects/33-tokenization/` یک توکن‌ساز آموزشی Byte-Level BPE با کتابخانه استاندارد می‌سازد. در مرحله آموزش، شش رشته ساختگی کوتاه به قطعه‌های اولیه تقسیم و به بایت تبدیل می‌شوند؛ ۲۴ ادغام پرتکرار ثبت می‌شود. سه رشته دیگر فقط برای ارزیابی رفت‌وبرگشت و شمار توکن استفاده می‌شوند. این داده‌ها برای تمرین‌اند، نه برای نتیجه‌گیری درباره کیفیت زبان فارسی یا یک مدل واقعی. هیچ وزن LLM آموزش داده نمی‌شود.

کد کامل زیر همان فایل `tokenizer_bpe.py` است که آزموده شد. توکن‌ساز عمداً نرمال‌سازی Unicode نمی‌کند، از regex ساده آموزشی بهره می‌گیرد و میان قطعه‌های پیش‌توکن‌ساز ادغام نمی‌سازد. فایل JSON ذخیره‌شده، قواعد توکن‌ساز را ثبت می‌کند؛ وزن مدل یا جدول تعبیه آموزش‌دیده را ذخیره نمی‌کند.

```python
"""Tiny, deterministic byte-level BPE tokenizer for teaching (standard library only).

This is deliberately not a clone of tiktoken, GPT-2, or SentencePiece. It uses a
small Unicode-aware pre-tokenizer, no Unicode normalization, all 256 UTF-8 byte
values, and deterministic left-to-right application of learned merge ranks.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable
import json
import re

SPECIAL_TOKENS = {"<|pad|>": 0, "<|bos|>": 1, "<|eos|>": 2, "<|unk|>": 3}
SPECIAL_ID_TO_TOKEN = {value: key for key, value in SPECIAL_TOKENS.items()}
BYTE_OFFSET = len(SPECIAL_TOKENS)
BYTE_COUNT = 256
FORMAT_NAME = "babak-ai-toy-byte-bpe-v1"
PRETOKENIZER_NAME = r"whitespace runs | Unicode \w+ | single non-word characters"
# This simple pedagogical splitter preserves all input characters. It is not a
# production tokenizer's model-specific regular expression.
_PRETOKEN_RE = re.compile(r"\s+|\w+|[^\w\s]", flags=re.UNICODE)


def _pretokenize(text: str) -> list[str]:
    """Split text into chunks while preserving the exact concatenated string."""
    pieces = _PRETOKEN_RE.findall(text)
    if "".join(pieces) != text:
        raise ValueError("pre-tokenizer did not preserve the input")
    return pieces


def _merge_pair(sequence: list[int], pair: tuple[int, int], new_id: int) -> list[int]:
    """Merge non-overlapping occurrences of pair from left to right."""
    merged: list[int] = []
    index = 0
    while index < len(sequence):
        if index + 1 < len(sequence) and (sequence[index], sequence[index + 1]) == pair:
            merged.append(new_id)
            index += 2
        else:
            merged.append(sequence[index])
            index += 1
    return merged


class ByteBPE:
    """A compact byte-level BPE model with stable IDs and reversible decoding."""

    def __init__(self, merges: Iterable[tuple[int, int]] = ()) -> None:
        self._token_bytes: dict[int, bytes] = {
            BYTE_OFFSET + value: bytes([value]) for value in range(BYTE_COUNT)
        }
        normalized: list[tuple[int, int]] = []
        seen_pairs: set[tuple[int, int]] = set()
        known_ids = set(self._token_bytes)

        for rank, raw_pair in enumerate(merges):
            pair = tuple(raw_pair)
            if len(pair) != 2 or any(type(value) is not int for value in pair):
                raise ValueError("each merge must be a pair of integer token IDs")
            if pair in seen_pairs:
                raise ValueError("duplicate merge pair")
            if pair[0] not in known_ids or pair[1] not in known_ids:
                raise ValueError("merge refers to a token not defined earlier")
            new_id = BYTE_OFFSET + BYTE_COUNT + rank
            self._token_bytes[new_id] = self._token_bytes[pair[0]] + self._token_bytes[pair[1]]
            normalized.append(pair)
            seen_pairs.add(pair)
            known_ids.add(new_id)

        self.merges = tuple(normalized)

    @classmethod
    def train(cls, corpus: Iterable[str], num_merges: int = 24) -> "ByteBPE":
        """Learn frequent adjacent-byte merges from a small text corpus.

        Ties are broken by the numeric pair of token IDs. Corpus order therefore
        does not affect the result. Training data is not normalized.
        """
        if isinstance(corpus, str):
            raise TypeError("corpus must be an iterable of strings, not one string")
        if isinstance(num_merges, bool) or not isinstance(num_merges, int) or num_merges < 0:
            raise ValueError("num_merges must be a non-negative integer")
        try:
            texts = list(corpus)
        except TypeError as error:
            raise TypeError("corpus must be an iterable of strings") from error
        if not texts:
            raise ValueError("corpus must contain at least one text")
        if any(not isinstance(text, str) for text in texts):
            raise TypeError("every corpus item must be a string")

        sequences = [
            [BYTE_OFFSET + byte for byte in piece.encode("utf-8")]
            for text in texts
            for piece in _pretokenize(text)
            if piece
        ]
        merges: list[tuple[int, int]] = []

        for _ in range(num_merges):
            counts: Counter[tuple[int, int]] = Counter()
            for sequence in sequences:
                counts.update(zip(sequence, sequence[1:]))
            if not counts:
                break

            # Highest frequency wins; lexicographically smallest ID pair breaks ties.
            best_pair = min(counts, key=lambda pair: (-counts[pair], pair))
            new_id = BYTE_OFFSET + BYTE_COUNT + len(merges)
            sequences = [_merge_pair(sequence, best_pair, new_id) for sequence in sequences]
            merges.append(best_pair)

        return cls(merges)

    @property
    def vocab_size(self) -> int:
        """Number of special, byte, and learned-merge IDs in the model."""
        return BYTE_OFFSET + BYTE_COUNT + len(self.merges)

    def _encode_piece(self, piece: str) -> list[int]:
        ids = [BYTE_OFFSET + byte for byte in piece.encode("utf-8")]
        for rank, pair in enumerate(self.merges):
            if len(ids) < 2:
                break
            if any((ids[index], ids[index + 1]) == pair for index in range(len(ids) - 1)):
                new_id = BYTE_OFFSET + BYTE_COUNT + rank
                ids = _merge_pair(ids, pair, new_id)
        return ids

    def encode(self, text: str, *, add_bos: bool = False, add_eos: bool = False) -> list[int]:
        """Convert text to IDs. Special-token-looking text is treated as ordinary text."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        if not isinstance(add_bos, bool) or not isinstance(add_eos, bool):
            raise TypeError("add_bos and add_eos must be booleans")

        ids: list[int] = []
        if add_bos:
            ids.append(SPECIAL_TOKENS["<|bos|>"])
        for piece in _pretokenize(text):
            ids.extend(self._encode_piece(piece))
        if add_eos:
            ids.append(SPECIAL_TOKENS["<|eos|>"])
        return ids

    def decode(self, ids: Iterable[int], *, skip_special_tokens: bool = True) -> str:
        """Reconstruct UTF-8 text; malformed IDs or invalid byte sequences raise errors."""
        if not isinstance(skip_special_tokens, bool):
            raise TypeError("skip_special_tokens must be a boolean")
        output: list[str] = []
        byte_buffer = bytearray()

        def flush_bytes() -> None:
            if byte_buffer:
                output.append(bytes(byte_buffer).decode("utf-8", errors="strict"))
                byte_buffer.clear()

        try:
            values = list(ids)
        except TypeError as error:
            raise TypeError("ids must be an iterable of integers") from error

        for token_id in values:
            if isinstance(token_id, bool) or not isinstance(token_id, int):
                raise TypeError("token IDs must be integers")
            if token_id < 0 or token_id >= self.vocab_size:
                raise ValueError(f"token ID {token_id} is outside the vocabulary")
            if token_id in SPECIAL_ID_TO_TOKEN:
                flush_bytes()
                if not skip_special_tokens:
                    output.append(SPECIAL_ID_TO_TOKEN[token_id])
            else:
                byte_buffer.extend(self._token_bytes[token_id])
        flush_bytes()
        return "".join(output)

    def display_tokens(self, ids: Iterable[int]) -> list[str]:
        """Return diagnostic pieces; incomplete UTF-8 pieces use visible escapes."""
        shown: list[str] = []
        for token_id in ids:
            if isinstance(token_id, bool) or not isinstance(token_id, int):
                raise TypeError("token IDs must be integers")
            if token_id < 0 or token_id >= self.vocab_size:
                raise ValueError(f"token ID {token_id} is outside the vocabulary")
            if token_id in SPECIAL_ID_TO_TOKEN:
                shown.append(SPECIAL_ID_TO_TOKEN[token_id])
            else:
                shown.append(self._token_bytes[token_id].decode("utf-8", errors="backslashreplace"))
        return shown

    def save(self, path: str | Path) -> None:
        """Save every setting required to reproduce IDs; no learned LLM weights."""
        payload = {
            "format": FORMAT_NAME,
            "normalization": "none",
            "pretokenizer": PRETOKENIZER_NAME,
            "special_tokens": SPECIAL_TOKENS,
            "byte_offset": BYTE_OFFSET,
            "byte_count": BYTE_COUNT,
            "merges": [list(pair) for pair in self.merges],
        }
        Path(path).write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> "ByteBPE":
        """Load a saved toy tokenizer, rejecting incompatible metadata."""
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("format") != FORMAT_NAME:
            raise ValueError("unrecognized tokenizer format")
        if payload.get("normalization") != "none" or payload.get("pretokenizer") != PRETOKENIZER_NAME:
            raise ValueError("tokenizer preprocessing configuration differs")
        if payload.get("special_tokens") != SPECIAL_TOKENS:
            raise ValueError("special-token IDs differ")
        if payload.get("byte_offset") != BYTE_OFFSET or payload.get("byte_count") != BYTE_COUNT:
            raise ValueError("base byte vocabulary differs")
        merges = payload.get("merges")
        if not isinstance(merges, list):
            raise ValueError("merge table must be a list")
        return cls(merges)


TRAIN_CORPUS = (
    "مدل زبانی متن را به شناسه تبدیل می‌کند.",
    "مدل‌های زبانی از توکن‌ها استفاده می‌کنند.",
    "توکن‌سازی، متن را به دنباله‌ای از شناسه‌ها تبدیل می‌کند.",
    "AI models learn patterns from token sequences.",
    "A tokenizer maps text to token IDs and can decode the IDs.",
    "AI models learn patterns from token sequences.",
)
EVAL_TEXTS = (
    "مدل‌های تازه!",
    "tokenizer-v2",
    "می‌آموزد 🤖",
)


def main() -> None:
    # Small hand-check of the first merge, independent of the larger corpus.
    miniature = ByteBPE.train(["abab", "abac"], num_merges=1)
    print("mini_merges=", miniature.merges)
    print("abab_ids=", miniature.encode("abab"))

    baseline = ByteBPE.train(TRAIN_CORPUS, num_merges=0)
    tokenizer = ByteBPE.train(TRAIN_CORPUS, num_merges=24)
    baseline_count = sum(len(baseline.encode(text)) for text in EVAL_TEXTS)
    merged_count = sum(len(tokenizer.encode(text)) for text in EVAL_TEXTS)
    exact_round_trip = all(tokenizer.decode(tokenizer.encode(text)) == text for text in EVAL_TEXTS)
    print(f"train_texts={len(TRAIN_CORPUS)} eval_texts={len(EVAL_TEXTS)}")
    print(f"vocab_size={tokenizer.vocab_size} merges={len(tokenizer.merges)}")
    print(f"eval_tokens_byte_baseline={baseline_count} eval_tokens_bpe={merged_count}")
    print(f"eval_utf8_bytes={sum(len(text.encode('utf-8')) for text in EVAL_TEXTS)}")
    print(f"exact_round_trip={exact_round_trip}")
    sample = "abab"
    print("sample_pieces=", miniature.display_tokens(miniature.encode(sample)))
    print("sample_decoded=", miniature.decode(miniature.encode(sample)))


if __name__ == "__main__":
    main()
```

**اجرای ثبت‌شده:** Python 3.13.16، PyTorch 2.6.0+cpu و Chromium برای آزمون صفحه؛ آموزش BPE خود پروژه با CPU و بدون وابستگی خارجی اجرا می‌شود. از پوشه پروژه `python tokenizer_bpe.py` و `python -m unittest discover -v` را اجرا کنید؛ برای آزمون embedding، PyTorch CPU لازم است. ۱۱ آزمون توکن‌ساز و سه آزمون lookup موفق شدند. خروجی دستی `mini_merges=((101, 102),)` و `abab_ids=[260, 260]` بود. روی سه رشته ارزیابی، baseline بایتی ۵۹ توکن و BPE با ۲۴ ادغام ۳۶ توکن داد؛ ۵۹ بایت UTF-8 بود و بازسازی هر سه رشته دقیق ماند. این کاهش فقط نتیجه همین corpus کوچک و واژگان ساختگی است.

برای نمایش بردار، `nn.Embedding` با `num_embeddings` برابر اندازه همان واژگان و `embedding_dim=8` بسازید. آزمون شکل `(3,8)` و صفرماندن گرادیان ردیف PAD را بررسی می‌کند [۶]. اگر نسخه PyTorch شما متفاوت است، نسخه و خروجی را گزارش کنید. برنامه عمداً ادعا نمی‌کند که مدل زبانی آموزش یا آزمون کیفیت داده واقعی انجام شده است.

**عیب‌یابی:** اگر بازسازی رشته فارسی شکست خورد، ابتدا ادغام بایت‌ها، تبدیل UTF-8، نرمال‌سازی و جداکردن قطعه ویژه را بررسی کنید؛ متن را پیش از ذخیره بی‌صدا پاک‌سازی نکنید. اگر شناسه از اندازه embedding خارج بود، واژگان و وزن مدل ناهمگام‌اند. اگر توکن‌های متنی در خروجی کنسول به شکل `\x..` دیده می‌شوند، قطعه ممکن است وسط توالی چندبایتی UTF-8 افتاده باشد؛ دنباله کامل را decode کنید. خطای نصب `torch` فقط برای آزمون lookup است و آموزش BPE مستقل از آن اجرا می‌شود.

## ۱۰. پرسش‌ها، تمرین و معیار عبور

۱) تفاوت توکن، شناسه و تعبیه چیست؟ ۲) چرا تعداد `len(text)` برابر تعداد توکن مدل نیست؟ ۳) در BPE آموزشی، بعد از انتخاب جفت، ترتیب شناسه ادغام چرا باید ثبت شود؟ ۴) اگر Byte-Level BPE برای نویسه‌ای UNK ندهد، آیا آن نویسه را «می‌فهمد»؟ ۵) NFC و NFKC چه تفاوتی دارند؟ ۶) چرا مرز پیش‌توکن‌ساز در خروجی اثر می‌گذارد؟ ۷) اگر رشته `<|bos|>` در پیام کاربر دیده شود، آیا قطعاً شناسه BOS است؟ ۸) با `V=261` و `d=8` جدول تعبیه چند ردیف و چند ستون دارد؟ ۹) اگر سه شناسه به تعبیه ۸بعدی داده شوند، شکل خروجی چیست؟ ۱۰) چرا تعویض توکن‌ساز یک مدل آماده بدون تطبیق وزن‌ها خطاست؟

**تمرین محاسبه:** برای `abab` و `abac` جفت‌های `ab`، `ba` و `ac` را بشمارید؛ سپس یک ادغام را اجرا و دنباله شناسه‌ها را با بایت‌پایه ۴ محاسبه کنید. **تمرین کد:** `num_merges` را صفر، یک و ۲۴ بگذارید؛ شمار توکن‌ها و بازسازی را مقایسه کنید. یک رشته با نیم‌فاصله و یک متن ترکیبی فارسی–لاتین اضافه کنید. **پروژه تکمیلی:** corpus مجاز و مستند بسازید، متن‌های آموزش و ارزیابی را بر اساس سند یا منبع جدا کنید، baseline بایتی را حفظ کنید و توزیع طول، بازسازی، خطاهای مرزی و محدودیت زبان‌ها را گزارش دهید.

**معیار عبور:** حداقل ۸ پاسخ درست از ۱۰، محاسبه دستی درست، همه آزمون‌های پروژه موفق و گزارش شامل corpus/مجوز، جداسازی ارزیابی، baseline، اندازه و واحد معیار، تحلیل خطا، محدودیت نرمال‌سازی و دستور بازتولید. [پاسخ‌نامه مستقل فصل](book-engineering/answers/33-tokenization-fa.md) را پس از حل تمرین باز کنید.

## ۱۱. جمع‌بندی، به‌روزرسانی و منابع

توکن‌ساز مرز و شناسه می‌سازد؛ مدل از روی شناسه جدول تعبیه را می‌خواند و سپس نمایش‌های زمینه‌ای می‌آموزد. واژگان، نرمال‌سازی، پیش‌توکن‌ساز، ترتیب ادغام و نشانه‌های ویژه بخشی از قرارداد مدل‌اند. **مفهوم پایدار:** شناسه، برچسب قراردادی است و خودْ معنا ندارد. **وابسته به مدل و نسخه:** روش قطعه‌بندی، رشته‌های ویژه، اندازه واژگان و قواعد نرمال‌سازی. **بازبینی تا نوامبر ۲۰۲۶:** نسخه‌های جاری مستندات Transformer، توکن‌سازهای چندوجهی را نیز با توکن‌های ویژه مرتبط با تصویر/صوت توصیف می‌کنند [۵]؛ این نشانه‌ها به معنی نمایش همه محتوای تصویر یا صوت به صورت یک واژه متنی نیستند. هیچ الگوریتم توکن‌سازی «بهترین برای همه زبان‌ها و مدل‌ها» معرفی نمی‌شود. استانداردهای Unicode 18.0 در سال ۲۰۲۶ راهنمای نرمال‌سازی و مرزبندی‌اند؛ خودشان انتخاب توکن‌ساز یک مدل را تعیین نمی‌کنند [۷، ۸].

در فصل ۳۴ به جای تکرار این زنجیره، از دنباله بردارها به امتیازهای Query، Key و Value می‌رویم؛ سپس در فصل ۳۵ ماسک علّی و خطر نشت آینده را آزمون می‌کنیم.

**منابع مستقیم؛ تاریخ دسترسی برای مستندات زنده ۵ نوامبر ۲۰۲۶:**

[۱] Rico Sennrich، Barry Haddow و Alexandra Birch، «Neural Machine Translation of Rare Words with Subword Units»، ACL 2016، DOI: [10.18653/v1/P16-1162](https://doi.org/10.18653/v1/P16-1162)، [متن در ACL Anthology](https://aclanthology.org/P16-1162/). نسخه پیش‌چاپ arXiv:1508.07909 نخست در ۲۰۱۵ ثبت و در ۱۰ ژوئن ۲۰۱۶ بازبینی شد: [arXiv](https://arxiv.org/abs/1508.07909).

[۲] Taku Kudo و John Richardson، «SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing»، EMNLP System Demonstrations، نوامبر ۲۰۱۸، صص. ۶۶–۷۱، DOI: [10.18653/v1/D18-2012](https://doi.org/10.18653/v1/D18-2012)، [ACL Anthology](https://aclanthology.org/D18-2012/).

[۳] Hugging Face, Tokenizers، «Components»، مستندات برخط با تاریخ انتشار صفحه نامشخص؛ مراجعه ۵ نوامبر ۲۰۲۶، [مستندات نرمال‌سازی، پیش‌توکن‌سازها و مدل‌ها](https://huggingface.co/docs/tokenizers/en/components).

[۴] OpenAI، مخزن `tiktoken` و بخش «What is BPE anyway?»؛ مخزن زنده با تاریخ نسخه این توضیح نامشخص، مراجعه ۵ نوامبر ۲۰۲۶، [README و کد](https://github.com/openai/tiktoken). آمار کارایی یا نسبت بایت‌به‌توکن مخزن، نتیجه عمومی برای همه زبان‌ها و مدل‌ها نیست.

[۵] Hugging Face, Transformers، «Tokenizer»، نسخه مستندات 5.22.1 که هنگام بازبینی در دسترس بود، مراجعه ۵ نوامبر ۲۰۲۶، [مستندات](https://huggingface.co/docs/transformers/v5.22.1/en/main_classes/tokenizer).

[۶] PyTorch Contributors، «`torch.nn.Embedding`»، مستندات نسخه 2.6، مراجعه ۵ نوامبر ۲۰۲۶، [مرجع API](https://docs.pytorch.org/docs/2.6/generated/torch.nn.Embedding.html).

[۷] Unicode Consortium، Unicode Standard Annex #15، «Unicode Normalization Forms»، نسخه Unicode 18.0.0، ۱۲ اوت ۲۰۲۶، [UAX #15](https://www.unicode.org/reports/tr15/).

[۸] Unicode Consortium، Unicode Standard Annex #29، «Unicode Text Segmentation»، نسخه Unicode 18.0.0، ۱ سپتامبر ۲۰۲۶، [UAX #29](https://www.unicode.org/reports/tr29/).

---

# جلد سوم، فصل ۲ — توجه: پرس‌وجو، کلید، مقدار و محاسبهٔ ماتریسی

**The Art & Science of Building Intelligence | Babak & Ai | فصل سراسری ۳۴ از نقشهٔ پنج‌جلدی**

**تاریخ مرجع: ۵ نوامبر ۲۰۲۶؛ مستندات و منابع برخط در همین تاریخ بازبینی شدند.**

## ۱. مسئله: کدام بخش از دنباله برای این خروجی لازم است؟

در فصل قبل متن را به شناسه و سپس به بردار تعبیه تبدیل کردیم. حالا دنباله‌ای از بردارها داریم. یک بردار خلاصهٔ ثابت ممکن است برای همهٔ ورودی‌های بلند کافی نباشد؛ سازوکار **توجه (Attention)** به هر موقعیت پرس‌وجو اجازه می‌دهد از میان مجموعه‌ای از بردارهای دیگر، ترکیبِ داده‌محوری بسازد. این نام یک تشبیه مهندسی است: مدل انسان نیست و وزن‌های محاسبه‌شده به‌خودی‌خود اثبات نمی‌کنند که یک واژه را «فهمیده» یا به آن «اهمیت انسانی» داده است.

**پیش‌نیاز:** بردار، ضرب ماتریسی، softmax و تعبیه در فصل‌های پیشین؛ به‌ویژه فصل ۳۳ دربارهٔ شناسه و تعبیه. **هدف این فصل:** نقش Query/Key/Value را توضیح دهید، ابعاد ضرب‌ها را پیش از اجرا کنترل کنید، امتیازهای dot-product را مقیاس و نرمال کنید، خروجی را به صورت جمع وزن‌دار به دست آورید و پیاده‌سازی آموزشی را با PyTorch بسنجید.

**مرز این فصل:** فرمول پایهٔ توجه و یک نمونهٔ میان‌دنباله‌ای را بررسی می‌کنیم. Self-Attention، چندسری (Multi-Head) و ماسک علّی در فصل ۳۵ می‌آیند؛ این فصل آن‌ها را پیاده‌سازی نمی‌کند.

## ۲. «توجه» یک ایدهٔ کلی است؛ این فصل یک صورت‌بندی مشخص را دنبال می‌کند

در پژوهش ترجمهٔ ماشینی، Bahdanau، Cho و Bengio در ۲۰۱۵ سازوکاری برای هم‌ترازی نرم پیشنهاد کردند: در هر گام رمزگشا، بر اساس وضعیت آن گام و حالت‌های رمزگذار، وزن‌هایی می‌سازد و از حالت‌های منبع بردار زمینه‌ای محاسبه می‌کند [۱]. امتیازدهی آن‌ها **افزایشی (additive)** بود؛ پس نباید همهٔ توجه‌ها را با ضرب داخلی یکی دانست.

مقالهٔ Transformer در ۲۰۱۷ صورت‌بندی **Scaled Dot-Product Attention** را ارائه کرد و آن را در معماری چندسری به کار برد [۲]. در این فصل فقط همین صورت‌بندی تک‌سری را باز می‌کنیم. سازوکار عمومی را می‌توان چنین خلاصه کرد: یک پرس‌وجو با کلیدها امتیاز سازگاری می‌گیرد؛ softmax امتیازها را به وزن تبدیل می‌کند؛ سپس همان وزن‌ها بردارهای مقدار را ترکیب می‌کنند. پرس‌وجو/کلید و مقدار می‌توانند از نمایش‌های متفاوتی ساخته شوند.

تمثیل آموزشی: هر **Query** می‌گوید «برای این موقعیت چه چیزی لازم دارم؟»؛ هر **Key** نشانه‌ای برای سنجش سازگاری با آن نیاز است؛ هر **Value** اطلاعاتی است که در صورت سازگاری به خروجی کمک می‌کند. این تمثیل نقش محاسباتی را روشن می‌کند، نه این‌که درون شبکه جست‌وجوی نمادین یا برچسب‌های معنایی آماده وجود داشته باشند.

## ۳. پرس‌وجو، کلید و مقدار از کجا می‌آیند؟

در توجه میان‌دنباله‌ای، برای سادگی یک ماتریس نمایشِ پرس‌وجو `X` و ماتریس نمایش منبع `Z` می‌گیریم. لایه‌های خطیِ آموختنی، هرکدام را به فضای مناسب می‌برند:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="کیو برابر ایکس دبلیو کیو؛ کی برابر زد دبلیو کی؛ وی برابر زد دبلیو وی"><mrow><mi>Q</mi><mo>=</mo><mi>X</mi><msub><mi>W</mi><mi>Q</mi></msub><mo>,</mo><mspace width="0.5em"/><mi>K</mi><mo>=</mo><mi>Z</mi><msub><mi>W</mi><mi>K</mi></msub><mo>,</mo><mspace width="0.5em"/><mi>V</mi><mo>=</mo><mi>Z</mi><msub><mi>W</mi><mi>V</mi></msub></mrow></math>

متن جایگزین فرمول: `Q=XW_Q`، `K=ZW_K` و `V=ZW_V`. وزن‌های خطی آموخته می‌شوند؛ در این نمایش ساده، bias را ننوشته‌ایم. `X` و `Z` می‌توانند طول‌های متفاوت داشته باشند. در مثال ترجمه، می‌توان `X` را نمایش رمزگشا و `Z` را نمایش رمزگذار گرفت. در صورت‌های دیگر ممکن است این ورودی‌ها از منبعی دیگر بیایند.

هر پرس‌وجو با کلیدها مقایسه می‌شود؛ کلید و مقدار برای هر موقعیت منبع، هم‌تراز می‌مانند، اما دو فرافکنی جداگانه‌اند. بنابراین «کلید» نسخهٔ دیگری از «مقدار» نیست: کلید در امتیازدهی شرکت می‌کند و مقدار در ترکیب خروجی. خود `Q`، `K` و `V` بردارهای آموختنیِ وابسته به داده و پارامترهای مدل‌اند؛ واژه‌ها یا برچسب‌های انسانی نیستند.

![شکل ۳-۲-۱ — جریان توجه ضرب‌داخلیِ مقیاس‌شدهٔ Q/K/V: Q با Kᵀ امتیازهای Lq×Lk می‌سازد؛ تقسیم بر ریشهٔ dk و softmax سطری وزن‌های A را می‌دهد؛ سپس A در V ضرب می‌شود تا خروجی Lq×dv به دست آید. مثال میان‌دنباله‌ای: Q از رمزگشا و K و V از رمزگذار می‌آیند.](assets/images/babak-ai/v3-ch02-attention.webp)

**شکل ۳-۲-۱ — از Q/K/V تا بردارهای خروجی.** ابعاد روی شکل نام‌گذاری شده‌اند تا محل هر ضرب روشن بماند. `Lq` تعداد پرس‌وجوها، `Lk` تعداد موقعیت‌های کلید/مقدار، `dk` بُعد کلید و `dv` بُعد مقدار است. در مثال، خروجی یک بردار به ازای هر پرس‌وجو دارد.

## ۴. اول ابعاد را حساب کنیم

فرض کنید در این فصل یک نمونهٔ دسته‌ای با `B` دنباله داریم و برای هر دنباله یک سر توجه به کار می‌بریم. شکل تانسورها چنین است:

| تانسور | شکل | توضیح |
|---|---|---|
| `Q` | `B × Lq × dk` | `B` دسته، `Lq` پرس‌وجو، `dk` مؤلفه برای هر پرس‌وجو |
| `K` | `B × Lk × dk` | `Lk` کلید منبع؛ بُعد ویژگی با `Q` برابر است |
| `V` | `B × Lk × dv` | یک مقدار متناظر با هر کلید؛ بُعد `dv` می‌تواند متفاوت باشد |
| `QKᵀ` | `B × Lq × Lk` | هر ردیف پرس‌وجو را با همهٔ کلیدها مقایسه می‌کند |
| `A` پس از softmax | `B × Lq × Lk` | برای هر پرس‌وجو یک وزن به ازای هر کلید |
| `AV` | `B × Lq × dv` | خروجی به ازای هر پرس‌وجو |

اگر به‌جای ضرب ماتریسیِ هر نمونه از تانسورهای سه‌بعدی استفاده کنیم، `Kᵀ` باید فقط دو محور آخر را جابه‌جا کند؛ در PyTorch این کار `key.transpose(-2, -1)` است. انتقال همهٔ محورهای دسته‌ای را جابه‌جا نمی‌کند.

بدون محور دسته‌ای، صورت ساده این است: `Q` شکل `Lq×dk`، `K` شکل `Lk×dk` و `V` شکل `Lk×dv` دارند. در نتیجه `QKᵀ` شکل `Lq×Lk` و حاصل `AV` شکل `Lq×dv` است. این کنترل ابعاد جلوی خطای رایجِ استفاده از `K` به‌جای `Kᵀ` یا نرم‌سازی روی محور اشتباه را می‌گیرد.

## ۵. امتیاز، مقیاس‌گذاری و نرمال‌سازی

ابتدا سازگاری پرس‌وجو و کلید را با ضرب داخلی می‌سنجیم. سپس امتیاز را بر ریشهٔ بُعد کلید تقسیم می‌کنیم و روی **محور کلیدها** softmax می‌گیریم:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="اسکور برابر کیو ضربدر ترانهاده کی، تقسیم بر ریشه دی کی؛ آلفای آی جی برابر سافت‌مکس سطری اسکور؛ خروجی او برابر آلفا ضربدر وی"><mrow><mi>S</mi><mo>=</mo><mfrac><mrow><mi>Q</mi><msup><mi>K</mi><mi>T</mi></msup></mrow><msqrt><msub><mi>d</mi><mi>k</mi></msub></msqrt></mfrac><mo>,</mo><mspace width="0.5em"/><msub><mi>α</mi><mrow><mi>i</mi><mi>j</mi></mrow></msub><mo>=</mo><mfrac><mrow><mi>exp</mi><mo>(</mo><msub><mi>S</mi><mrow><mi>i</mi><mi>j</mi></mrow></msub><mo>)</mo></mrow><mrow><munderover><mo>∑</mo><mrow><mi>m</mi><mo>=</mo><mn>1</mn></mrow><msub><mi>L</mi><mi>k</mi></msub></munderover><mi>exp</mi><mo>(</mo><msub><mi>S</mi><mrow><mi>i</mi><mi>m</mi></mrow></msub><mo>)</mo></mrow></mfrac><mo>,</mo><mspace width="0.5em"/><mi>O</mi><mo>=</mo><mi>AV</mi></mrow></math>

متن جایگزین فرمول: `S=QKᵀ/√dk`؛ وزن `αᵢⱼ=exp(Sᵢⱼ)/Σₘ exp(Sᵢₘ)`؛ خروجی `O=AV`. جمع softmax برای هر ردیف `i` روی همهٔ `Lk` کلیدهاست.

از آن‌جا که softmax روی محور آخر اجرا می‌شود، هر ردیف `A` غیرمنفی است و مجموعش، جز خطای گردکردن، ۱ می‌شود. هر ردیف خروجی نیز جمعی وزن‌دار از ردیف‌های `V` است. در حالت بدون ماسک و بدون dropout، این خروجی ترکیب محدبِ بردارهای مقدار همان نمونه است. این گزاره دربارهٔ محاسبهٔ همین لایه است، نه دربارهٔ معنای کلیِ پیش‌بینی نهایی.

### چرا بر `√dk` تقسیم می‌کنیم؟

اگر مؤلفه‌های `q` و `k` مستقل، میانگین‌شان صفر و واریانس هرکدام ۱ باشد، واریانس جمعِ ضرب‌های مؤلفه‌ای در `q·k` با `dk` رشد می‌کند. تقسیم بر `√dk` اندازهٔ معمول امتیازها را برای چنین فرضی در مقیاسی نزدیک‌تر نگه می‌دارد. بدون این مقیاس‌گذاری، softmax ممکن است برای بُعد بزرگ به ناحیهٔ تیز/اشباع برسد؛ در آن ناحیه مشتق نرم‌سازی کوچک می‌شود و یادگیری می‌تواند دشوارتر شود. همین انگیزه در مقالهٔ Transformer آمده است [۲].

این استدلال بر فرضی ساده دربارهٔ مؤلفه‌ها متکی است؛ توزیع‌های واقعی در شبکهٔ آموخته‌شده الزاماً مستقل یا واحد-واریانس نیستند. تقسیم بر `√dk` تضمین نمی‌کند که همهٔ امتیازها کوچک، کالیبره یا از نظر معنا درست باشند. همچنین این کار نرمال‌سازی طول بردار و محاسبهٔ شباهت کسینوسی نیست؛ فقط ضریب مقیاس در این صورت‌بندی است.

## ۶. مثال عددی: دو کلید، دو مقدار

برای دیدن هر مرحله، یک پرس‌وجو و دو موقعیت منبع انتخاب می‌کنیم:

```text
q = [1, 0]
k₁ = [1, 0]       v₁ = [10, 0]
k₂ = [0, 1]       v₂ = [ 0,10]
dk = 2
```

ضرب داخلی خام `q·k₁=1` و `q·k₂=0` است؛ پس امتیازهای مقیاس‌شده برابر `[1/√2, 0] ≈ [0.7071, 0]` می‌شوند. softmax روی همین دو موقعیت می‌دهد:

```text
α ≈ [0.66976, 0.33024]
```

در نتیجه:

```text
o = 0.66976 × [10, 0] + 0.33024 × [0, 10]
  ≈ [6.69762, 3.30238]
```

این نمونه نشان می‌دهد ضرب در `V` چگونه مقدارهای متناسب با وزن‌ها را ترکیب می‌کند. امتیاز بالاتر به معنی «ارزش انسانی بیشتر» نیست؛ فقط در این ماژول، برای این پرس‌وجو و این ورودی، ضریب وزن‌دهی بزرگ‌تری ساخته است.

## ۷. پیاده‌سازی و بررسی‌های پایه

در کد آموزشی، محاسبه را صریح نگه می‌داریم: `Q @ Kᵀ`، تقسیم بر `√dk`، `torch.softmax(..., dim=-1)` و سپس ضرب در `V`. خروجی دوم تابع وزن‌های `A` است تا بتوانیم شکل و مجموع هر ردیف را آزمایش کنیم. تابع تولیدی PyTorch خروجی توجه را می‌دهد و الزاماً خود ماتریس وزن را برنمی‌گرداند.

فایل آزموده‌شده در `book-engineering/projects/34-attention/attention.py` است؛ کد کامل آن در پایان همین فصل آمده است. تابع برای روشن‌بودن درس، ورودی سه‌بعدی، dtype شناور و شکل‌های سازگار را بررسی می‌کند. این نمونه یک سر دارد؛ projectionهای `W_Q/W_K/W_V` را باید مدل پیرامونی فراهم کند. پیاده‌سازی ماسک و dropout ندارد و جایگزین API کامل تولیدی نیست.

اجرای نمونهٔ کوچک:

```bash
cd book-engineering/projects/34-attention
python attention.py
python -m unittest -v
```

در آزمون CPU با PyTorch 2.6، نمونه وزن‌های حدود `[0.66976, 0.33024]` و خروجی حدود `[6.69762, 3.30238]` داد. آزمون‌ها هشت مورد را بررسی می‌کنند: مثال محاسبه‌شده، شکل‌های دسته‌ای با طول متفاوت پرس‌وجو و منبع، نرمال‌شدن ردیف‌ها، برابری خروجی با API مرجع در تلورانس، گرادیان‌های متناهی، softmax برای امتیازهای بزرگ متناهی و رد ورودی‌های ناسازگار. مقادیر ممیزشناور ممکن است با dtype، نسخه و kernel تفاوت‌های کوچک داشته باشند.

مستندات PyTorch 2.6 برای `torch.nn.functional.scaled_dot_product_attention` شکل‌های `query/key/value`، ضریب پیش‌فرض `1/√E` و انتخاب kernelهای بهینه را شرح می‌دهند [۳]. در همان نسخه، اگر `dropout_p` مثبت به تابع داده شود، dropout اعمال می‌شود؛ پس در استنتاج مقدار صفر را صریح بدهید، مگر آن‌که رفتار تصادفی عمداً خواسته شده باشد. اختلاف اندک میان اجرای آموزشی و kernelهای fused، به‌علت ترتیب/دقت عملیات ممیزشناور ممکن است؛ مقایسه با تلورانس مناسب را جایگزین انتظارِ تطبیق بیت‌به‌بیت کنید. مستندات نسخه‌دار را برای نسخهٔ نصب‌شده بخوانید؛ رفتار API می‌تواند تغییر کند.

## ۸. آزمون‌های معنایی و خطاهای رایج

پیش از اعتماد به پیاده‌سازی، این پرسش‌ها را پاسخ دهید:

1. آیا بعد آخر `Q` و `K` یکسان است؟ باید `dk` برابر باشد تا ضرب `QKᵀ` ممکن شود.
2. آیا طول محور کلید در `K` و `V` برابر است؟ هر وزن برای یک موقعیت کلید، همان ردیف مقدار را انتخاب می‌کند.
3. آیا softmax روی محور `Lk` اجرا می‌شود؟ در شکل سه‌بعدی ساده، این `dim=-1` است.
4. آیا شکل خروجی `[B,Lq,dv]` است؟ خروجی به تعداد پرس‌وجوهاست، نه الزاماً به طول منبع.
5. آیا ردیف‌های وزن مجموعی نزدیک ۱ دارند؟ این آزمون جهت softmax و محور نرمال‌سازی را بررسی می‌کند.
6. آیا `output` با `weights @ value` برابر است و گرادیان از `Q/K/V` می‌گذرد؟ این موارد را در آزمون‌ها می‌سنجیم.

خطاهای متداول عبارت‌اند از تقسیم بر `dk` به‌جای `√dk`، استفاده از `K` بدون ترانهاده، اعمال softmax روی محور پرس‌وجو، ناسازگاری طول کلید و مقدار، و این فرض که همهٔ پیاده‌سازی‌ها همواره امتیازها را بر `√dk` تقسیم می‌کنند. در APIهای مختلف ممکن است مقدار پیش‌فرض یا امکان تعیین scale فرق کند؛ پارامتر همان نسخه را بررسی کنید [۳].

در مدل واقعی، sequence padding، mask، dropout، batch، dtype و layout هم اهمیت دارند. در این فصل فقط حالت پایه را آزموده‌ایم و دربارهٔ صحت یک مدل کامل یا عملکرد GPU ادعایی نداریم. فصل ۳۵ به توسعه‌های معماریِ بعدی می‌پردازد.

## ۹. وزن توجه را با توضیح قطعی اشتباه نگیریم

وزن `αᵢⱼ` معنای ریاضی روشنی دارد: ضریب موقعیت `j` در جمع وزن‌دارِ خروجی همان ماژول، برای پرس‌وجوی `i`. اما از این تعریف به‌تنهایی نتیجه نمی‌شود که مقدار وزن، اهمیت علّی یا توضیح وفادارِ پیش‌بینی نهایی است.

Jain و Wallace در ۲۰۱۹ در چند مدل زبانی، شواهدی گزارش کردند که وزن‌ها ممکن است با بعضی سنجه‌های اهمیت ویژگی هم‌راستا نباشند و توزیع‌های متفاوتی بتوانند خروجی مشابه بدهند [۴]. Wiegreffe و Pinter همان سال تأکید کردند که نتیجه به تعریف «توضیح» و طراحی آزمون وابسته است و ارزیابی باید کل مدل را در نظر بگیرد [۵]. این دو مقاله محدودهٔ بحث روش‌شناختی را نشان می‌دهند؛ هیچ‌کدام مجوز نمی‌دهند که هر نقشهٔ توجه در هر معماری را بی‌قیدوشرط رد یا تأیید کنیم.

قاعدهٔ عملی: وزن‌ها را ابتدا به‌عنوان **ضرایب محاسباتی همین لایه** تفسیر کنید. اگر هدف توضیح‌پذیری است، تعریف توضیح و معیار وفاداری را روشن کنید، مدل و لایه را مشخص کنید، مقایسه و آزمون مداخله‌ای مناسب طراحی کنید و نتیجه را به همان شرایط محدود سازید. رنگ‌کردن وزن‌های بزرگ در یک heatmap به‌تنهایی شاهد تصمیم‌گیری مدل نیست.

## ۱۰. هزینهٔ محاسبه و انتخاب پیاده‌سازی

برای محاسبهٔ صریحِ همهٔ امتیازها، جدول `S` و وزن‌های `A` هرکدام `Lq×Lk` خانه دارند؛ هزینهٔ ضرب `QKᵀ` با ابعاد ویژگی رشد می‌کند و ضرب `AV` نیز به `dv` وابسته است. بنابراین طول دنباله، ابعاد و تعداد نمونه‌ها روی حافظه و زمان اثر می‌گذارند. این شمارش آموزشی به‌تنهایی سرعت واقعی را پیش‌بینی نمی‌کند: device، dtype، شکل دقیق ورودی و kernel انتخاب‌شده هم دخیل‌اند.

در PyTorch، API سطح‌بالای Scaled Dot-Product Attention می‌تواند kernel بهینهٔ سازگار با ورودی و backend را انتخاب کند [۳]. این انتخاب ممکن است در محاسبات ممیزشناور تفاوت جزئی ایجاد کند. برای کاربرد واقعی، شکل و dtype واقعی را روی سخت‌افزار هدف benchmark کنید؛ از سرعت اجرای نمونهٔ CPU یا از کوتاهی یک تابع نتیجه‌گیری نکنید. در این فصل صحت فرمول پایه را می‌آزماییم، نه برتری سرعت یک backend را.

## ۱۱. تمرین و جمع‌بندی

### تمرین‌ها

1. با سه کلید و سه مقدار دوبعدی، یک `Q` بسازید و `QKᵀ`، امتیازهای مقیاس‌شده، وزن‌ها و خروجی را دستی یا با ماشین‌حساب دنبال کنید. بررسی کنید وزن‌ها در کدام محور به ۱ جمع می‌شوند.
2. طول پرس‌وجوها را ۲ و طول منبع را ۵ بگذارید. شکل `Q`، `K`, `V`, `A` و `O` را بنویسید و توضیح دهید چرا شکل خروجی `Lq` را دنبال می‌کند.
3. فرض کنید `dk=16`. ضریب درست چیست؟ توضیح دهید چرا این عمل با نرمال‌سازی طول `q` و `k` فرق دارد.
4. در پروژه، `d_v` را از `d_k` متفاوت بگیرید و آزمون شکل را گسترش دهید. سپس آگاهانه softmax را روی محور نادرست اجرا کنید؛ کدام آزمون باید این خطا را آشکار کند؟
5. دو جمله بنویسید: یکی که نقش محاسباتی وزن `αᵢⱼ` را دقیق تعریف کند و دیگری که از ادعای توضیح‌پذیریِ بی‌پشتوانه پرهیز کند.

### آنچه باید به یاد بماند

- Query و Key برای ساخت امتیازها به فضای ویژگی هم‌اندازه فرافکنی می‌شوند؛ Valueها اطلاعات خروجی را حمل می‌کنند.
- صورت‌بندی این فصل `softmax(QKᵀ/√dk)V` است؛ softmax برای هر پرس‌وجو روی کلیدها اعمال می‌شود.
- شکل‌ها را پیش از اجرا بنویسید: امتیاز و وزن `Lq×Lk`، خروجی `Lq×dv`.
- در حالت پایه، وزن هر ردیف مجموعاً ۱ است و خروجی جمع وزن‌دار Valueهاست؛ تفسیر معنایی/توضیحیِ وزن‌ها نیازمند شواهد جداگانه است.
- API، dropout، backend و دقت عددی به نسخه و ورودی وابسته‌اند. این فصل ماسک علّی و Multi-Head را پوشش نمی‌دهد.

[جواب‌نامهٔ تشریحی فصل ۳۴](book-engineering/answers/34-attention-fa.md) · [پروژهٔ اجرایی و هشت آزمون](book-engineering/projects/34-attention/README.md)

## ۱۲. منابع بیرونی

1. Dzmitry Bahdanau, Kyunghyun Cho, Yoshua Bengio. “Neural Machine Translation by Jointly Learning to Align and Translate.” ICLR 2015؛ نسخهٔ arXiv:1409.0473 نخستین‌بار ۱ سپتامبر ۲۰۱۴ ثبت شد. [مقاله در arXiv](https://arxiv.org/abs/1409.0473). منبع اولیه برای توجه افزایشی و جمع وزن‌دار حالت‌های منبع.
2. Ashish Vaswani et al. “Attention Is All You Need.” NeurIPS 2017؛ arXiv:1706.03762، نسخهٔ نخست ۱۲ ژوئن ۲۰۱۷ و نسخهٔ بازنگری‌شدهٔ v7 در ۲ اوت ۲۰۲۳. [مقاله در arXiv](https://arxiv.org/abs/1706.03762) · [نسخهٔ NeurIPS](https://papers.neurips.cc/paper/7181-attention-is-all-you-need.pdf). منبع فرمول Scaled Dot-Product و انگیزهٔ مقیاس‌گذاری.
3. PyTorch. “`torch.nn.functional.scaled_dot_product_attention`.” مستندات نسخهٔ 2.6. [صفحهٔ رسمی API](https://docs.pytorch.org/docs/2.6/generated/torch.nn.functional.scaled_dot_product_attention.html). برای شکل ورودی/خروجی، scale پیش‌فرض، dropout و انتخاب kernel؛ نسخهٔ مستندات در این فصل عمداً مشخص شده است.
4. Sarthak Jain, Byron C. Wallace. “Attention is not Explanation.” NAACL-HLT 2019, pp. 3543–3556. [ACL Anthology](https://aclanthology.org/N19-1357/) · [DOI: 10.18653/v1/N19-1357](https://doi.org/10.18653/v1/N19-1357). یک سوی بحث دربارهٔ محدودیت تفسیر وزن‌های توجه.
5. Sarah Wiegreffe, Yuval Pinter. “Attention is not not Explanation.” EMNLP-IJCNLP 2019, pp. 11–20. [ACL Anthology](https://aclanthology.org/D19-1002/) · [DOI: 10.18653/v1/D19-1002](https://doi.org/10.18653/v1/D19-1002). تأکید بر تعریف توضیح و طراحی ارزیابی.

**دسترسی منابع برخط: ۵ نوامبر ۲۰۲۶.** مستندات API به نسخهٔ 2.6 ارجاع می‌دهند؛ نسخهٔ نصب‌شده و رفتار دقیق backend را برای پروژهٔ واقعی جداگانه وارسی کنید.

## پیوست: پیاده‌سازی کامل پروژه

فایل زیر همان نسخهٔ اجرا و آزمون‌شدهٔ `book-engineering/projects/34-attention/attention.py` است. این نمونهٔ سه‌بعدیِ آموزشی یک سر را اجرا می‌کند و برای روشن‌ماندن مفهوم، mask یا dropout ندارد.

```python
"""Small, explicit scaled dot-product attention for chapter 34 (CPU-friendly)."""
from __future__ import annotations

import math
import torch
import torch.nn.functional as F


def scaled_dot_product_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Compute one-head attention for [batch, sequence, feature] tensors.

    query: [B, Lq, dk], key: [B, Lk, dk], value: [B, Lk, dv]
    returns output [B, Lq, dv] and row-normalized weights [B, Lq, Lk].

    This teaching implementation intentionally has no mask or dropout. Those
    choices are model/training-specific and causal masking is the next chapter.
    """
    tensors = {"query": query, "key": key, "value": value}
    if any(not isinstance(tensor, torch.Tensor) for tensor in tensors.values()):
        raise TypeError("query, key, and value must be torch.Tensor objects")
    if any(tensor.ndim != 3 for tensor in tensors.values()):
        raise ValueError("expected rank-3 [batch, sequence, feature] tensors")
    if any(not tensor.is_floating_point() for tensor in tensors.values()):
        raise TypeError("query, key, and value must have floating-point dtype")
    if not (query.dtype == key.dtype == value.dtype):
        raise TypeError("query, key, and value must use the same dtype")
    if not (query.device == key.device == value.device):
        raise ValueError("query, key, and value must be on the same device")
    if query.size(0) != key.size(0) or key.size(0) != value.size(0):
        raise ValueError("batch dimensions must match")
    if query.size(-1) != key.size(-1):
        raise ValueError("query and key feature dimensions must match")
    if key.size(1) == 0 or value.size(1) == 0:
        raise ValueError("the key/value sequence must contain at least one position")
    if key.size(1) != value.size(1):
        raise ValueError("key and value sequence lengths must match")
    if query.size(-1) == 0 or value.size(-1) == 0:
        raise ValueError("feature dimensions must be non-empty")

    dk = query.size(-1)
    scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(dk)
    weights = torch.softmax(scores, dim=-1)
    output = torch.matmul(weights, value)
    return output, weights


def main() -> None:
    # One query, two keys, and two 2-D values; all calculations are on CPU.
    query = torch.tensor([[[1.0, 0.0]]], dtype=torch.float64)
    key = torch.tensor([[[1.0, 0.0], [0.0, 1.0]]], dtype=torch.float64)
    value = torch.tensor([[[10.0, 0.0], [0.0, 10.0]]], dtype=torch.float64)

    output, weights = scaled_dot_product_attention(query, key, value)
    reference = F.scaled_dot_product_attention(
        query, key, value, dropout_p=0.0, is_causal=False
    )
    print("device=cpu")
    print("scores_scaled=", (query @ key.transpose(-2, -1) / math.sqrt(2)).tolist())
    print("weights=", weights.tolist())
    print("output=", output.tolist())
    print("torch_reference_matches=", torch.allclose(output, reference, atol=1e-12, rtol=1e-12))


if __name__ == "__main__":
    main()
```

---

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

---

# جلد سوم، فصل ۴ — موقعیت، RoPE، اتصال باقیمانده، LayerNorm و FFN

**The Art & Science of Building Intelligence | Babak & Ai | فصل سراسری ۳۶ از نقشهٔ پنج‌جلدی**

**تاریخ مرجع: ۵ نوامبر ۲۰۲۶؛ منابع برخط در همین تاریخ بازبینی شدند.**

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

متن جایگزین: `q^R_(m,2r:2r+2)=R(mθ_r)q_(m,2r:2r+2)`؛ همان دوران روی `k_n` هم اعمال می‌شود. سپس `(R(mθ)q)^T(R(nθ)k)=q^T R((n−m)θ)k`.

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

متن جایگزین: `y=(x−μ)/sqrt(σ²+ε) ⊙ γ + β`؛ در PyTorch `nn.LayerNorm(d_model)` با ورودی `[B,L,D]` محور آخر `D` را جداگانه برای هر `[b,l]` نرمال می‌کند [۵].

`γ` و `β` شکل `D` دارند و اگر affine فعال باشد آموخته می‌شوند. `ε` برای ثبات عددی افزوده می‌شود. PyTorch 2.6 واریانس biased، معادل `torch.var(..., correction=0)`، به کار می‌برد و آمار را از خود ورودی در train و eval می‌گیرد [۵]. پس unlike BatchNorm به میانگین نمونه‌های batch متکی نیست. انتخاب `normalized_shape` اشتباه می‌تواند ناخواسته ابعاد دیگری را نرمال کند؛ شکل تنسور را با قرارداد API تطبیق دهید.

## ۹. Pre-LN و Post-LN دو ترتیب یکسان نیستند

Transformer اولیه زیرلایه را درون residual جمع می‌کند و بعد LayerNorm می‌زند؛ این فرم **Post-LN** است. در **Pre-LN** اول ورودی زیرلایه نرمال می‌شود و نتیجه با stream باقیمانده جمع می‌شود:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="Post-LN خروجی لایه نرمال سازی ایکس به علاوه اف از ایکس است؛ Pre-LN خروجی ایکس به علاوه اف از لایه نرمال سازی ایکس است"><mrow><msub><mi>y</mi><mtext>Post</mtext></msub><mo>=</mo><mi>LayerNorm</mi><mo>(</mo><mi>x</mi><mo>+</mo><mi>F</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>)</mo><mo>,</mo><mspace width="1em"/><msub><mi>y</mi><mtext>Pre</mtext></msub><mo>=</mo><mi>x</mi><mo>+</mo><mi>F</mi><mo>(</mo><mi>LayerNorm</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>)</mo></mrow></math>

متن جایگزین: `Post-LN: LN(x+F(x))`; `Pre-LN: x+F(LN(x))`.

قرارگیری LayerNorm، مسیر گرادیان را عوض می‌کند. تحلیل Xiong و همکاران دربارهٔ warmup و اندازهٔ گرادیان در Post-LN/Pre-LN، به فرض‌ها و تنظیم‌های بررسی‌شده مربوط است؛ از آن نباید نتیجه گرفت که Pre-LN همیشه در تمام وظایف برنده است [۴]. بعضی Pre-LN معماری‌ها پیش از سر خروجی LayerNorm نهایی می‌افزایند. این پروژه دو ترتیب یک زیرلایه را نشان می‌دهد؛ آن یک معماری GPT کامل نیست.

## ۱۰. شبکهٔ پیش‌خورِ موقعیت‌مند (FFN)

پس از attention، Transformer برای هر موقعیت یک MLP با وزن مشترک میان موقعیت‌ها اعمال می‌کند. ورودی و خروجی `D` بُعد دارند و میانه می‌تواند `d_ff` باشد:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="اف اف ان از ایکس برابر دبلیو دو، فعال ساز از دبلیو یک ایکس به علاوه بی یک، به علاوه بی دو؛ برای موقعیت‌های مختلف وزن‌ها مشترک‌اند"><mrow><mi>FFN</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>=</mo><msub><mi>W</mi><mn>2</mn></msub><mi>φ</mi><mo>(</mo><msub><mi>W</mi><mn>1</mn></msub><mi>x</mi><mo>+</mo><msub><mi>b</mi><mn>1</mn></msub><mo>)</mo><mo>+</mo><msub><mi>b</mi><mn>2</mn></msub></mrow></math>

متن جایگزین: `FFN(x)=W₂ φ(W₁x+b₁)+b₂`. در یک لایه، ماتریس‌های `W₁/W₂` برای همهٔ ردیف‌های `X` مشترک‌اند؛ اما لایه‌های مختلف پارامترهای جدا دارند [۱].

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

---

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

---

# جلد سوم، فصل ۶ — پنجرهٔ متن، KV Cache، GQA، توجه پراکنده و MoE

**The Art & Science of Building Intelligence | Babak & Ai | فصل سراسری ۳۸ از نقشهٔ پنج‌جلدی**

**تاریخ مرجع: ۵ نوامبر ۲۰۲۶؛ منابع پژوهشی این فصل در همین تاریخ بازبینی شدند.**

## ۱. یک پنجرهٔ بزرگ، یک مسئلهٔ کوچک‌شده نیست

در فصل‌های پیشین، Query/Key/Value، ماسک علّی، RoPE و بلوک Transformer را ساختیم. این فصل به پرسشی می‌پردازد که هنگام سرو مدل برجسته می‌شود: **اگر متن ورودی از چند هزار به ده‌ها هزار یا صدها هزار توکن برسد، چه چیزی در زمان و حافظه رشد می‌کند و چه تغییری واقعاً کمک می‌کند؟** پاسخ فقط «پنجره را بزرگ‌تر کن» نیست. طول توالی، هزینهٔ توجه، حافظهٔ KV، تعداد درخواست‌های هم‌زمان، الگوی دسترسی، معماری FFN و کیفیت استفاده از شواهد با هم درگیرند.

**هدف‌ها:** پس از این فصل بتوانید (۱) محدودیت پنجرهٔ اسمی را از توانایی مؤثر مدل جدا کنید؛ (۲) حافظهٔ KV را با واحد درست تخمین بزنید؛ (۳) نقش GQA/MQA، مدیریت cache، attention پراکنده و FlashAttention را از هم تشخیص دهید؛ (۴) هزینه و مزیت احتمالی MoE را بدون یکی‌گرفتن پارامتر فعال و کل وزن‌ها توضیح دهید؛ و (۵) یک ارزیابی زمینهٔ بلند طراحی کنید که فقط به «سوزن در انبار کاه» وابسته نباشد.

**پیش‌نیاز:** ضرب ماتریسی و ابعاد تنسور، Self-Attention و ماسک علّی از فصل‌های ۳۴–۳۵، و RoPE/بلوک Transformer از فصل ۳۶. **قرارداد:** `T` تعداد توکن‌ها پس از Tokenizer است؛ یک توکن الزاماً یک واژه نیست.

![شکل ۳-۶-۱ — نقشهٔ مصالحه‌های زمینهٔ بلند: ماتریس dense همهٔ جفت‌ها را با الگوی Sparse Attention محلی/سراسری مقایسه می‌کند؛ FlashAttention محاسبهٔ دقیق و متراکم را با tiling انجام می‌دهد، نه اینکه ذاتاً sparse باشد؛ تعداد KV head در GQA اندازهٔ KV Cache را تعیین می‌کند؛ در MoE، router هر توکن را به expert منتخب می‌فرستد و پارامتر فعال از پارامتر کل جداست؛ RULER، NoLiMa و OOLONG نمونه‌هایی برای سنجش استفادهٔ مؤثر از متن‌اند.](assets/images/babak-ai/v3-ch06-efficiency-map.webp)

**شکل ۳-۶-۱ — چهار تصمیم جدا، نه یک دکمهٔ «زمینهٔ بلند».** ماسک‌های پنل چپ الگوهای دسترسی را نشان می‌دهند؛ پنل میانی رابطهٔ تعداد KV head و cache را خلاصه می‌کند؛ پنل راست مسیر sparse routing در MoE را نمایش می‌دهد. تصویر نمودار پیچیدگی نظری است، نه benchmark سخت‌افزار.

## ۲. پنجرهٔ متن با زمینهٔ مؤثر یکی نیست

**پنجرهٔ متن** (context window) حدی معماری/سرویس برای موقعیت‌هایی است که مدل می‌تواند در یک درخواست یا گام پردازش کند. تعریف دقیقِ APIها می‌تواند فرق کند: بعضی سرویس‌ها ورودی و خروجی را در سقف کل می‌شمارند، بعضی حد خروجی جداگانه هم دارند؛ مستندات همان سرویس را بررسی کنید. دستور سیستم، تاریخچه، متن بازیابی‌شده، ابزارها، پیام کاربر و خروجیِ تولیدی همگی می‌توانند بودجه مصرف کنند. پیش از ارسال درخواست، تعداد **توکن**‌ها را با Tokenizer همان مدل حساب کنید، نه با شمارش کلمه یا نویسه.

**زمینهٔ مؤثر** (effective context) پرسش دیگری است: وقتی طول ورودی، محل شاهد، تعداد حواس‌پرت‌کن‌ها یا پیچیدگی استدلال تغییر می‌کند، مدل چه‌قدر از متن استفاده می‌کند؟ این ویژگی به مدل، روش آموزش، وظیفه و معیار بستگی دارد. اعلام سقف ۱۲۸K یا ۱M توکن، تضمین نمی‌کند که مدل همهٔ آن بخش را دقیق بازیابی، مقایسه یا جمع‌بندی کند. حتی بازیابی یک واقعیت منفرد از متن با یافتن چند واقعیت، پیوند دادنشان و محاسبهٔ یک پاسخ جمعی برابر نیست.

اگر ورودی بزرگ‌تر از بودجه است، بریدن خامِ ابتدا یا انتهای متن ممکن است شاهد را حذف کند. گزینه‌ها می‌توانند شامل retrieval/chunking، خلاصهٔ میانیِ قابل بازبینی، پنجرهٔ کوچک‌تر، یا مدل/سرویس دیگری باشند؛ هرکدام اطلاعاتی را از دست می‌دهند و باید روی وظیفهٔ واقعی آزموده شوند. «کل سند را در prompt جا دادیم» به‌تنهایی معیار موفقیت نیست.

## ۳. Attention: پیش‌پردازش و تولید دو هزینهٔ متفاوت دارند

برای دنباله‌ای با `T` توکن، attention متراکمِ معمول در هر لایه و سر، امتیازهای Query-Key را برای همهٔ جفت‌ها می‌سازد. هزینهٔ حسابیِ بخش attention در مرتبهٔ `O(T²d)` است؛ اگر ماتریس وزن‌های توجه به شکل معمول materialize شود، فضای موقت آن نیز با `T²` رشد می‌کند. در attention علّی فقط نیمهٔ پایینی ماتریس قابل استفاده است: تعداد جفت‌های مجاز `T(T+1)/2` است، که همچنان مرتبهٔ درجهٔ دوم دارد.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="تعداد جفت‌های مجاز در توجه علّی برابر تی ضرب در تی به‌علاوه یک تقسیم بر دو است؛ مرتبهٔ هزینهٔ attention برابر تی به توان دو ضرب در دی است"><mrow><msub><mi>N</mi><mi>pairs</mi></msub><mo>=</mo><mfrac><mrow><mi>T</mi><mo>(</mo><mi>T</mi><mo>+</mo><mn>1</mn><mo>)</mo></mrow><mn>2</mn></mfrac><mo>,</mo><mspace width="1em"/><mi>FLOPs</mi><mo>=</mo><mi>O</mi><mo>(</mo><msup><mi>T</mi><mn>2</mn></msup><mi>d</mi><mo>)</mo></mrow></math>

**پیش‌پردازش (prefill):** prompt حاضر است؛ مدل آن را در یک یا چند گذر پردازش می‌کند. **تولید (decode):** هر گام یک توکن تازه را به دنباله می‌افزاید. با cache، برای همان گام Query جدید با K/V قبلی سنجیده می‌شود؛ هزینهٔ attention هر توکن تازه با طول تاریخچه رشد می‌کند، ولی K/V پیشوند را لازم نیست از نو محاسبه کنیم. تولید چند توکن همچنان گام‌به‌گام وابسته است. «FlashAttention سریع است» نیز معنی نمی‌دهد که محاسبهٔ نظری همهٔ جفت‌های dense حذف شده باشد؛ آن نکته را در بخش ۹ جدا می‌کنیم.

| طول prompt علّی | جفت‌های مجاز در هر سر/لایه (تقریب دقیق با `T(T+1)/2`) | نسبت به 8K |
|---:|---:|---:|
| 8,192 توکن | 33,558,528 | 1× |
| 32,768 توکن | 536,887,296 | تقریباً 16× |

چهار برابر کردن طول، جفت‌های dense را تقریباً شانزده برابر می‌کند؛ این جدول زمان دیواری را پیش‌بینی نمی‌کند. kernel، پهنای باند، دقت عددی، اندازهٔ batch و سخت‌افزار بر زمان اثر دارند.

## ۴. KV Cache: آنچه در decode دوباره لازم نیست بسازیم

در هر لایهٔ خودتوجهی، مدل برای توکن‌های پردازش‌شده Key و Value می‌سازد. هنگام تولید، K/V توکن تازه به وضعیت قبلی افزوده و برای attention گام بعد استفاده می‌شود. این وضعیت موقتیِ وابسته به درخواست **KV Cache** نام دارد؛ با وزن‌های ثابت مدل، با activationهای موقت prefill و با تاریخچهٔ متن خام یکی نیست. در cross-attention یک مدل Encoder–Decoder، K/V حافظهٔ منبع نیز ممکن است جداگانه نگه‌داری شود؛ فرمول زیر فقط cache خودتوجهی را برآورد می‌کند.

اگر `L` تعداد لایه‌ها، `B` اندازهٔ batch، `T` طول cache، `H_KV` شمار KV head، `d` بُعد هر head و `b` بایت هر مقدار باشد، تخمین پایه چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="بایت حافظهٔ کی وی برابر دو ضرب در لایه‌ها، batch، طول دنباله، تعداد کی وی سرها، بُعد هر سر و بایت هر مقدار است"><mrow><msub><mi>M</mi><mi>KV</mi></msub><mo>=</mo><mn>2</mn><mo>×</mo><mi>L</mi><mo>×</mo><mi>B</mi><mo>×</mo><mi>T</mi><mo>×</mo><msub><mi>H</mi><mi>KV</mi></msub><mo>×</mo><mi>d</mi><mo>×</mo><mi>b</mi></mrow></math>

ضریب ۲ به K و V اشاره می‌کند. برای FP16 یا BF16 معمولاً `b=2` است؛ برای FP32، `b=4`. اندازه با طول و batch و تعداد KV head **خطی** است. این فرمول ظرفیت وزن‌ها، logits، activationها، workspace کرنل، حافظهٔ allocator، fragmentation، metadata، padding و cacheهای دیگر را شامل نمی‌شود؛ در عمل به‌اندازهٔ برآورد خام VRAM رزرو نکنید.

## ۵. مثال حافظه: 32K توکن روی یک مدل فرضی

فرض کنیم فقط برای برآورد، مدل ۳۲ لایه دارد، `d=128`، دقت cache برابر BF16، batch برابر ۱ و طول `T=32,768` است. شمار Query head را ۳۲ می‌گیریم و فقط تعداد KV head را میان گزینه‌ها عوض می‌کنیم:

| معماری نمونه | `H_KV` | KV Cache محاسبه‌شده برای هر درخواست |
|---|---:|---:|
| MHA | 32 | 16 GiB |
| GQA | 8 | 4 GiB |
| MQA | 1 | 0.5 GiB |

برای نمونهٔ GQA: `2×32×1×32,768×8×128×2 = 4,294,967,296` بایت، یعنی دقیقاً ۴ GiB با تعریف `1 GiB=2³⁰` بایت. در همین فرض‌ها GQA-8 چهار برابر کمتر از MHA-32 و MQA-1 هشت برابر کمتر از GQA-8 cache می‌خواهد. این نسبت دربارهٔ **همان معماری، طول، batch، head dimension و نوع عددی** است؛ از آن به‌تنهایی نسبت سرعت یا برابری کیفیت نتیجه نمی‌گیریم.

اگر همین درخواست‌ها هشت نمونهٔ هم‌زمان با طول کامل باشند، cache خام GQA-8 حدود ۳۲ GiB می‌شود؛ این هنوز وزن‌های مدل و حافظهٔ دیگر را کنار گذاشته است. سرو واقعی ممکن است هر لایه‌ای را با attention متفاوت، cache کم‌دقت، prefix مشترک، سقف طول یا سیاست زمان‌بندی اجرا کند. همیشه «هر درخواست» را با concurrency هدف ضرب کنید و اندازه‌گیری واقعی را کنار برآورد نگه دارید.

## ۶. از MHA به MQA و GQA: چند Query برای یک KV؟

در Multi-Head Attention (MHA)، هر Query head، Key و Value متناظر خودش را دارد (`H_KV=H_Q`). در Multi-Query Attention (MQA)، همهٔ Query headها K/V مشترک دارند (`H_KV=1`)؛ Shazeer این اشتراک را برای کاهش بار خواندن K/V در decode مطرح کرد [۳]. در Grouped-Query Attention (GQA)، Query headها به گروه‌هایی تقسیم می‌شوند و هر گروه یک KV head مشترک دارد؛ اگر `H_Q=32` و `H_KV=8` باشد، در این چینش چهار Query head برای هر KV head است [۴].

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="در جی کیو ای تعداد Query head برابر تعداد KV head ضرب در اندازهٔ گروه است؛ نسبت حافظهٔ cache به نسبت تعداد KV head وابسته است"><mrow><msub><mi>H</mi><mi>Q</mi></msub><mo>=</mo><msub><mi>H</mi><mi>KV</mi></msub><mo>×</mo><mi>G</mi><mo>,</mo><mspace width="1em"/><mfrac><msub><mi>M</mi><mi>GQA</mi></msub><msub><mi>M</mi><mi>MHA</mi></msub></mfrac><mo>≈</mo><mfrac><msub><mi>H</mi><mi>KV</mi></msub><msub><mi>H</mi><mi>Q</mi></msub></mfrac></mrow></math>

با بُعد head ثابت، بخش KV cache به `H_KV` متناسب است. اما Query headها و محاسبهٔ score/output آن‌ها باقی می‌مانند؛ بنابراین GQA چهار برابر cache کم‌تر در مثال بالا به معنی چهار برابر کاهش کل FLOPs، کل VRAM مدل یا latency نیست. تبدیل یک MHA checkpoint به MQA/GQA هم می‌تواند نیازمند uptraining باشد؛ آزمایش GQA روی T5 گزارش می‌کند که در تنظیمات پژوهش، GQA پس از uptraining کیفیتی نزدیک MHA و سرعتی نزدیک MQA داشت، نه اینکه این نتیجه برای هر مدل و هر وظیفه تضمین شود [۴].

## ۷. Cache را فقط فشرده نمی‌کنیم؛ آن را اداره هم می‌کنیم

در سرو هم‌زمان، cache درخواست‌ها طول‌های متغیر دارد و آزاد/رزروکردن قطعه‌های بزرگ پیوسته می‌تواند حافظه را هدر دهد. **PagedAttention**، معرفی‌شده در کار vLLM، K/V را در بلوک‌های ثابت و غیرپیوسته مدیریت می‌کند؛ بلوک‌ها در صورت نیاز تخصیص می‌یابند و بلوک‌های prefix مشترک می‌توانند میان چند دنباله بازاستفاده شوند [۵]. این رویکرد به بهره‌برداری بهتر از حافظه و اشتراک prefix کمک می‌کند؛ cache منطقی هر توکن و محاسبهٔ attention ناپدید نمی‌شوند. عددهای throughput مقالهٔ vLLM به مدل، workload و baselineهای همان آزمایش محدودند.

چند راه دیگر نیز وجود دارد، هرکدام با هزینه:

- **Prefix caching:** پیشوند تکراری (مثلاً دستور ثابت) را میان درخواست‌های سازگار reuse کنید؛ تفاوت در متن، وزن‌ها یا موقعیت‌ها ممکن است مانع reuse شود.
- **Quantization فشردهٔ cache:** بایت هر مقدار را کم می‌کند؛ خطای عددی، کیفیت، kernel و سربار تبدیل باید سنجیده شود. نمونهٔ پژوهشی KIVI برای طراحی ۲بیتی، Key را per-channel و Value را per-token کمّی می‌کند و نتایج خود را روی مدل‌های ارزیابی‌شده گزارش می‌کند؛ آن نسبت‌ها را به مدل/دقت دیگر تعمیم ندهید [۲۳].
- **Eviction یا sliding window:** K/V قدیمی را کنار می‌گذارد؛ حافظه کمتر می‌شود، اما شاهد دور ممکن است دیگر در دسترس نباشد. «token آغازین سراسری» یا retrieval می‌تواند بخشی از این مسئله را تغییر دهد، نه اینکه همهٔ آن را حل کند.
- **Offload و زمان‌بندی batch:** بخشی از cache را به حافظهٔ دیگر منتقل یا درخواست‌ها را زمان‌بندی می‌کند؛ پهنای باند و latency اضافه می‌شود.

برای سرو، معمولاً «چند درخواست هم‌زمان با چه توزیع طولی؟» به‌اندازهٔ طول بیشینه مهم است. یک cache آموزشی ساده که با هر توکن `cat` می‌کند، دادهٔ قبلی را کپی می‌کند؛ آن را با allocator بلوکی تولیدی اشتباه نگیرید. پروژهٔ این فصل همین تفاوت را آشکار می‌کند.

## ۸. Sparse Attention: هر جفتی لازم نیست به هر جفت برسد؟

در **توجه پراکنده** (Sparse Attention) مدل فقط بخشی از ارتباط‌های Query-Key را محاسبه می‌کند. الگو می‌تواند محلی، سراسری، تصادفی یا وابسته به انتخاب یادگرفتنی باشد. Longformer ترکیب پنجرهٔ محلی و توکن‌های سراسری را برای برخی وظایف متن بلند بررسی کرد [۶]؛ BigBird پنجرهٔ محلی، ارتباط‌های تصادفی و توکن‌های global را ترکیب کرد و در مقاله‌اش کاهش مرتبهٔ نظری و آزمایش‌های همان benchmark را گزارش داد [۷].

در یک الگوی ساده با پنجرهٔ محلی `W` و `G` توکن سراسری، تعداد یال‌های attention می‌تواند در حد `O(TW+TG)` باشد (با فرض الگوی مناسب و `W,G` کوچک نسبت به `T`). این مقایسه باید با attention dense از مرتبهٔ `O(T²)` سنجیده شود:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="برای attention محلی به‌علاوه global، جفت‌های توجه تقریبی از مرتبهٔ تی ضرب در پنجره به‌علاوه تی ضرب در تعداد توکن‌های سراسری‌اند؛ در dense مرتبه تی به توان دو است"><mrow><msub><mi>C</mi><mi>sparse</mi></msub><mo>≈</mo><mi>O</mi><mo>(</mo><mi>T</mi><mi>W</mi><mo>+</mo><mi>T</mi><mi>G</mi><mo>)</mo><mo>,</mo><mspace width="1em"/><msub><mi>C</mi><mi>dense</mi></msub><mo>=</mo><mi>O</mi><mo>(</mo><msup><mi>T</mi><mn>2</mn></msup><mo>)</mo></mrow></math>

این مرتبه فقط شمار جفت‌ها را تقریب می‌زند؛ توکن global، یال‌های تصادفی، طول پنجره، padding، تعداد لایه‌ها و kernel واقعی را باید در محاسبه گنجاند. اگر هر لایه فقط همسایه‌ها را ببیند، اطلاعات دور ممکن است طی چند لایه منتقل شود، اما این با یک دسترسی مستقیم به هر نقطه برابر نیست. توجه sparseِ دقیق روی الگوی مجاز، نسبت به **همان الگو** دقیق است؛ نسبت به denseِ کامل ممکن است اطلاعاتی را حذف کند. ماسکی که فقط روی ماتریس dense اعمال شود، از دید ریاضی sparsity نشان می‌دهد، اما اگر kernel محاسبهٔ خانه‌های بسته را واقعاً skip نکند، صرفاً با افزودن ماسک صرفه‌جویی سرعتی تضمین نمی‌شود.

## ۹. FlashAttention دقیق است؛ Sparse Attention نیست

**FlashAttention** با tiling و محاسبهٔ نرم‌ماکس به‌صورت مرحله‌ای، attention متراکمِ استاندارد را بدون materialize کردن ماتریس کامل امتیازها محاسبه می‌کند و رفت‌وآمد بین حافظهٔ سریع GPU و HBM را کاهش می‌دهد [۱]. در بیان الگوریتمی، خروجی attention دقیقِ همان رابطهٔ dense است (با اختلاف‌های معمول ممیز شناور)؛ اما شمار ضرب‌های اصلی همچنان مرتبهٔ `O(T²d)` است. **FlashAttention-2** نحوهٔ تقسیم کار و موازی‌سازی را تغییر داد و در پیکربندی‌های مقالهٔ خودش بهبودهایی گزارش کرد [۲].

پس دو محور جدا داریم: «چه جفت‌هایی را می‌خواهیم؟» و «آن جفت‌ها را چطور با کمترین I/O و حافظه اجرا کنیم؟» FlashAttention عمدتاً محور دوم است و به‌تنهایی توجه را پراکنده نمی‌کند؛ Sparse Attention محور اول را هم عوض می‌کند. نسخه‌های block-sparse یا kernelهای تخصصی می‌توانند این ایده‌ها را ترکیب کنند. این ترکیب برای سود واقعی باید روی GPU/نسخهٔ هدف benchmark شود؛ داشتن نام FlashAttention یا mask محلی در کد ساده، نتیجهٔ سرعت را ثابت نمی‌کند.

## ۱۰. Mixture of Experts: انتخاب مسیر محاسبه برای هر توکن

در یک لایهٔ **Mixture of Experts (MoE)**، به‌جای یک شبکهٔ پیش‌خور مشترک، چند expert (اغلب شبکه‌های FFN) و یک **router** داریم. Router برای بازنمایی هر توکن امتیاز می‌سازد، سپس یک یا چند expert را برمی‌گزیند. در یک MoE top-`k` ساده:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="خروجی لایهٔ MoE برابر مجموع خروجی expertهای انتخاب‌شده است که با وزن router ترکیب می‌شوند؛ مجموعهٔ انتخاب‌شده top k expert است"><mrow><mi>p</mi><mo>(</mo><mi>i</mi><mo>|</mo><mi>x</mi><mo>)</mo><mo>=</mo><mi>softmax</mi><mo>(</mo><msub><mi>W</mi><mi>r</mi></msub><mi>x</mi><mo>)</mo><mo>,</mo><mspace width="0.7em"/><mi>y</mi><mo>=</mo><munder><mo>∑</mo><mrow><mi>i</mi><mo>∈</mo><msub><mi>S</mi><mi>k</mi></msub></mrow></munder><msub><mi>g</mi><mi>i</mi></msub><mo>(</mo><mi>x</mi><mo>)</mo><msub><mi>E</mi><mi>i</mi></msub><mo>(</mo><mi>x</mi><mo>)</mo></mrow></math>

ایدهٔ **فعال‌سازی تنک** این است که برای هر توکن فقط بخشی از expertها اجرا شوند؛ در نتیجه ممکن است ظرفیت کل پارامترها از محاسبهٔ فعال هر توکن بزرگ‌تر باشد. این با Sparse Attention فرق دارد: MoE مسیر FFN را انتخاب می‌کند و به‌تنهایی attention یا KV Cache را کوچک نمی‌کند. اگر وزن همهٔ expertها روی چند GPU shard شده باشد، حافظهٔ وزن کل سامانه همچنان باید نگه‌داری/دسترسی شود؛ expert parallelism هم ارتباط شبکه‌ای و all-to-all اضافه می‌کند. عدد «پارامتر فعال» را معادل وزن کل لازم در VRAM نگیرید.

نمونهٔ موردی: گزارش DeepSeek-V3 مدلی با ۶۷۱ میلیارد پارامتر کل و ۳۷ میلیارد پارامتر فعال برای هر توکن را توصیف می‌کند؛ همان گزارش از DeepSeekMoE و Multi-head Latent Attention نیز استفاده می‌کند [۱۰]. این اعداد مشخصات گزارش همان مدل‌اند و به معنی «مدل ۳۷B است» یا تضمین latency/کیفیت برای هر کاربر نیستند. همچنین expertها الزاماً «متخصص انسان‌نام‌گذاری‌شده» نیستند؛ specialization در یک مدل خاص باید با تحلیل و آزمایش بررسی شود.

## ۱۱. Router، توازن بار و هزینهٔ ارتباطی

اگر تقریباً همهٔ توکن‌ها به یک expert بروند، expertهای دیگر کم‌استفاده می‌شوند و همان expertِ پرترافیک bottleneck می‌شود. در routing top-1ِ Switch، `fᵢ` سهم توکن‌هایی است که واقعاً به expert شمارهٔ `i` فرستاده شده‌اند و `Pᵢ` میانگین احتمال router برای همان expert است. یکی از lossهای سادهٔ توازن بار چنین است [۹]:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="در فرمول Switch، زیان کمکی برابر آلفا ضرب در تعداد expertها ضرب در مجموع سهم واقعی توکن‌های هر expert در میانگین احتمال router همان expert است"><mrow><msub><mi>ℒ</mi><mi>aux</mi></msub><mo>=</mo><mi>α</mi><mo>·</mo><mi>E</mi><mo>·</mo><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>E</mi></munderover><msub><mi>f</mi><mi>i</mi></msub><msub><mi>P</mi><mi>i</mi></msub></mrow></math>

این **یک نمونهٔ آموزشی top-1** است، نه loss واحد همهٔ MoEها. Capacity محدود، overflow یا حذف/بازگرداندن توکن، routing top-2، expert parallelism و معماری‌های متأخر قراردادهای دیگری دارند. loss یا bias توازن می‌تواند توکن‌ها را پخش‌تر کند، اما توازن تحمیلی با specialization و کیفیت هم مصالحه دارد.

گزارش DeepSeek-V3 راهبردی را شرح می‌دهد که به‌جای اتکای اصلی به loss کمکیِ سراسری، bias انتخاب expertها را برای توازن تنظیم می‌کند؛ نویسندگان همچنان loss کمکی کوچکِ توالی‌محور را برای جلوگیری از عدم‌تعادل شدید در یک توالی نگه می‌دارند [۱۰]. از سوی دیگر، توازن router در آموزش و توازن کارِ GPUها هنگام استنتاج مسئلهٔ یکسان نیست. پیش‌چاپ LLEP در ۲۰۲۶ بار نامتوازن expert parallelism را در زمان اجرا بررسی و rerouting پویا را پیشنهاد می‌کند؛ عددهای سرعت/حافظهٔ آن به اندازهٔ مدل، سخت‌افزار و پیکربندی آزمایش مقاله محدودند [۲۲].

## ۱۲. افزایش طول موقعیت، آموزش و پنجرهٔ API

اگر مدل با RoPE یا طرح موقعیتی دیگری آموزش دیده باشد، اجرای آن روی موقعیت‌های بسیار فراتر از دادهٔ آموزش می‌تواند کیفیت را خراب کند. Position Interpolation و YaRN نمونه‌هایی از روش‌های گسترش طول با تغییر مقیاس موقعیت و/یا ادامهٔ آموزش‌اند [۱۱][۱۲]. LongRoPE و LongRoPE2 نیز راهبردهای خود را برای گسترش پنجره و حفظ عملکرد کوتاه‌زمینه گزارش کرده‌اند [۱۳][۱۴]. این‌ها روش‌های پژوهشی/آموزشی‌اند، نه راهی که هر مدل را صرفاً با بالا بردن پارامتر API به مدل بلندزمینه تبدیل کند.

برای نمونه، LongRoPE2 گزارش می‌کند در آزمایش‌های خودش LLaMA3-8B را به ۱۲۸K زمینهٔ مؤثر رسانده و بیش از ۹۸٫۵٪ عملکرد کوتاه‌زمینه را حفظ کرده است؛ این ادعای مقاله با مدل، داده و benchmarkهای همان پژوهش معنا دارد [۱۴]. عنوان LongRoPE از آزمایش تا ۲ میلیون توکن سخن می‌گوید؛ این را نباید به هر مدل، هر وظیفه یا هر سرویس تعمیم داد [۱۳]. تعمیم موقعیتی، کیفیت شواهد دور، طول ورودی واقعی، بودجهٔ cache و هزینهٔ serving را جداگانه بسنجید.

از روی سقف API هم نتیجه نگیرید که وزن‌های مدل روی همان طول آموزش دیده‌اند؛ از روی طول آموزش نیز نتیجه نگیرید که هر درخواست با آن طول اقتصادی است. گزارش فنی خوب، «حد اعلام‌شده»، «طول آزموده‌شده»، «طول مؤثر در وظیفه» و «سقف/هزینهٔ سرو» را در چهار فیلد جدا می‌نویسد.

## ۱۳. زمینهٔ بلند را چطور ارزیابی کنیم؟

یک Needle-in-a-Haystack ساده می‌تواند مفید باشد، اما پاسخ درست به یک عبارت منفرد، توانایی جمع‌آوری چند قطعه و محاسبه روی آن‌ها را ثابت نمی‌کند. **RULER** بازیابی، تغییر تعداد/ویژگی needleها، چندگام و aggregation را می‌آزماید؛ مطالعهٔ منتشرشده‌اش ۱۷ مدل متن‌باز را در ۱۳ وظیفه بررسی کرد و نشان داد نتیجه با طول و دشواری کار افت می‌کند [۱۵]. نتیجهٔ هر نسخه و threshold همان مطالعه است، نه رتبه‌بندی همهٔ مدل‌های امروز.

**NoLiMa** هم‌پوشانی واژگانیِ سؤال و شاهد را کاهش می‌دهد تا مدل نتواند صرفاً با تطبیق لفظی needle را پیدا کند. در نسخهٔ بررسی‌شده، ۱۱ تا از ۱۳ مدل در طول ۳۲K به کمتر از نصف baseline کوتاه‌زمینهٔ خود رسیدند؛ این نتیجهٔ benchmark و مجموعهٔ مدل‌های مقاله است [۱۶]. **OOLONG** به‌جای یک شاهد، دسته‌بندیِ واحدهای متعدد، شمارش/تجمیع، روابط زمانی و پرسش‌های توزیعی را بررسی می‌کند؛ مقالهٔ COLM 2026 گزارش می‌کند حتی مدل‌های frontier آزمایش‌شده در دو بخش آن در ۱۲۸K زیر ۵۰٪ بودند [۱۷]. این benchmarkها وظایف متفاوت دارند؛ امتیازهایشان را مستقیم در یک جدول رتبه‌بندی ادغام نکنید.

برای محصول خود، پروتکل کوچک اما صریح بسازید: طول‌های چندگانه (مثلاً 4K، 8K، 16K، 32K)، محل شاهد در ابتدا/میانه/انتها، distractor، پرسش چندگامی و یک کار تجمیعی؛ ثابت نگه‌داشتن مدل/tokenizer/prompt؛ اندازه‌گیری دقت یا معیار وظیفه، latency prefill، توکن بر ثانیه در decode، حافظهٔ peak، batch و هزینه. نتیجهٔ کوتاه‌زمینه را baseline کنید. هر تغییر (GQA، mask، quantization، cache eviction) را با خط پایهٔ هم‌سخت‌افزار و هم‌پروتکل مقایسه کنید.

## ۱۴. مروری بر پژوهش‌های جدید تا نوامبر ۲۰۲۶

توجه sparse برای استفادهٔ عملی نیازمند co-design الگوریتم و kernel است. **Native Sparse Attention (NSA)** سه مسیر فشرده‌سازی، انتخاب بلوک و پنجرهٔ محلی را در یک طراحی trainable و hardware-aligned ترکیب می‌کند؛ نسخهٔ منتشرشده در ACL 2025 نتایج خود را با مدل و تنظیم همان مطالعه گزارش می‌کند [۱۸]. **Flash Sparse Attention (FSA)** در ICLR 2026 اجرای kernel NSA را برای اندازه‌های مختلف گروه GQA بازطراحی می‌کند؛ مقاله تا ۳٫۵ برابر کاهش latencyِ kernel نسبت به kernel مرجع خود گزارش می‌کند. این «سرعتِ kernel در پیکربندی‌های آزمایش‌شده» است، نه وعدهٔ همان نسبت برای کل محصول یا GPU دیگر [۱۹].

**COBS**، پیش‌چاپ ژوئیهٔ ۲۰۲۶، برای هر بلوک آمار فشردهٔ مرتبهٔ دوم پیشنهاد می‌کند تا بلوک‌های مهم برای attention انتخاب شوند. نویسندگان در benchmark retrievalِ RULER با زمینهٔ ۳۲K میانگین ۰٫۸۱۹۵ را در برابر ۰٫۲۹۹۹ برای baseline NSA و ۰٫۹۰۴۰ برای dense گزارش می‌کنند [۲۰]. اما این کار یک مطالعهٔ مکانیزم در مقیاس حدود ۱٫۲B، با پیش‌آموزش طول ۴K و fine-tuning روی دادهٔ تولیدشده به سبک RULER است؛ خود مقاله این محدودیت تعمیم را تصریح می‌کند. بنابراین عدد خوب، شاهدِ امیدوارکننده در پروتکل مقاله است، نه تأیید سامانهٔ frontier.

**Virtual Head Attention (VHA)** در پیش‌چاپ اکتبر ۲۰۲۶ از اختلاط خطیِ Queryها برای افزایش تنوع مجازی سرها و کاهش KV head در معماری خودش بهره می‌گیرد؛ نتایج کیفیت و cache آن متعلق به checkpointها و مقیاس‌هایی است که مقاله آزمایش کرده است [۲۱]. چون نسخهٔ بررسی‌شده پیش‌چاپ تازه است، آن را گزینهٔ پژوهشی برای ارزیابی بدانید، نه default تثبیت‌شده. پژوهش LLEP در بخش MoE نیز نشان می‌دهد که حتی بعد از انتخاب مدل، زمان‌بندی بار expert روی دستگاه‌ها مسئله‌ای جداست [۲۲].

**جمع‌بندی این مرور:** عددهای paper-specific را با نوع benchmark، اندازهٔ مدل، طول آموزش، سخت‌افزار و وضعیت انتشار نقل کنید. نتایج preprintهای ۲۰۲۶ برای شناخت جهت تحقیق مفیدند؛ پیش از تصمیم استقرار، نسخهٔ اصلی، کد/مجوز، kernelِ دستگاه هدف و آزمون مستقل خودتان را بازبینی کنید.

## ۱۵. راهنمای انتخاب: اول گلوگاه را اندازه بگیرید

| گلوگاه یا نیاز | گزینهٔ مناسب برای آزمایش | چه چیزی را حل نمی‌کند/چه چیزی باید سنجیده شود؟ |
|---|---|---|
| هزینهٔ I/O و حافظهٔ موقت attention dense در prefill | FlashAttention یا kernel دقیق/بهینهٔ معادل | FLOPs نظری dense را درجهٔ اول کم نمی‌کند؛ زمان واقعی به kernel و GPU وابسته است |
| KV Cache و پهنای باند decode | GQA/MQA، دقت cache، paging و prefix reuse | کیفیت/دقت عددی، latency، مدل وزن‌ها و محدودیت‌های API را جدا بسنجید |
| ورودی طولانی با وابستگی محلی/سراسری ساختاریافته | Sparse یا hybrid attention با kernel واقعی | انتخاب الگو می‌تواند شاهد حذف کند؛ mask dense به‌تنهایی سرعت نمی‌دهد |
| هزینهٔ FFN در مدل بزرگ و conditional compute | MoE و routing | وزن کل، ارتباط all-to-all، توازن بار و رفتار روی هر domain باقی می‌ماند |
| حد موقعیت مدل کوتاه‌زمینه | روش گسترش RoPE/موقعیت به‌علاوهٔ داده/تنظیم | افزایش سقف API تضمین استفادهٔ مؤثر یا حفظ کیفیت کوتاه نیست |
| اسناد بسیار بزرگ، ولی پرسش موضعی | retrieval و chunking؛ متن شواهد منتخب را به مدل بدهید | بازیابی می‌تواند شواهد پراکنده یا وابستگی کل‌سند را جا بیندازد |

این ابزارها می‌توانند ترکیب شوند، اما یکسان نیستند: GQA تعداد K/V را کم می‌کند، paging حافظه را اداره می‌کند، FlashAttention dense را بهتر اجرا می‌کند، Sparse Attention اتصالات را محدود می‌کند و MoE expertهای FFN را انتخاب می‌کند. برای نمونه، دستیار روی هشت سندِ ۳۲K با معماری فرضی مثال بخش ۵، فقط cache خام GQA-8 را حدود ۳۲ GiB می‌خواهد. اگر سؤال به چند بخش محدود است، retrieval شاید ورودی و cache را کم کند؛ اگر باید اطلاعات همهٔ سندها با هم تجمیع شود، ابتدا کیفیت aggregation را با نمونه‌های واقعی بسنجید. سپس concurrency و peak memory را اندازه بگیرید؛ انتخاب معماری از نام «long context» به‌تنهایی درنمی‌آید.

## ۱۶. پروژهٔ اجرایی: mask، GQA، cache و یک MoE کوچک

پروژهٔ CPU در `book-engineering/projects/38-long-context/` چهار جزء دارد: `causal_allowed_mask` و پنجرهٔ محلی؛ `grouped_query_attention` با شکل‌های `[B,H_Q,T_Q,d]` و `[B,H_KV,T_KV,d]`؛ cache افزایشی آموزشی؛ و MoE top-1 به سبک Switch به‌همراه تخمین حافظه. قرارداد mask پروژه **True=مجاز** است—APIهای دیگری ممکن است قرارداد bool-mask وارونه داشته باشند.

نمونهٔ کوچک:

```python
import torch
from efficient_attention import grouped_query_attention

q = torch.randn(1, 8, 4, 16)  # batch, Hq, Tq, d
k = torch.randn(1, 2, 4, 16)  # batch, Hkv, Tk, d
v = torch.randn_like(k)
output, probabilities = grouped_query_attention(q, k, v, causal=True)
print(output.shape)  # [1, 8, 4, 16]
```

اجرای کامل از پوشهٔ پروژه: `python -m unittest discover -v` و `python efficient_attention.py`. آزمون‌ها، هم‌ارزی GQA با مرجع ساده‌ای که K/V را برای سرها تکرار می‌کند، جلوگیری از خواندن آینده، مقایسهٔ decode افزایشی با attention علّی کامل، بایت دقیق مثال BF16، ورودی‌های نامعتبر و مسیر گرادیان/انتخاب expert را کنترل می‌کنند. اعداد وزن مدل تصادفی‌اند؛ پروژه کیفیت زبانی، throughput، latency یا سرعت GPU را اندازه نمی‌گیرد.

**نکتهٔ مهم:** برای شفافیت، `grouped_query_attention` ماتریس score متراکم می‌سازد، حتی وقتی mask محلی داده شود؛ پس کد نمونهٔ الگوریتمی است و kernel Sparse نیست. `KVCache` نیز با `torch.cat` append می‌کند و قبلی‌ها را کپی می‌کند. این محدودیت‌ها در README پروژه ثبت شده‌اند تا آموزش را با پیاده‌سازی production اشتباه نگیریم.

## ۱۷. تمرین‌ها، پروژهٔ تکمیلی و معیار عبور

۱. با فرمول `T(T+1)/2`، تعداد جفت‌های علّی مجاز را برای ۸K و ۳۲K بیابید و نسبت را تفسیر کنید. آیا نتیجهٔ زمان اجرا دقیقاً ۱۶ برابر است؟ چرا؟

۲. در مثال بخش ۵، با batch برابر ۴، cache خام MHA-32 و GQA-8 را محاسبه کنید. پاسخ را هم بایت و هم GiB بنویسید و دست‌کم سه نوع حافظهٔ حذف‌شده از برآورد را نام ببرید.

۳. تفاوت prefill و یک گام decode را شرح دهید. KV Cache کدام محاسبه را از نو انجام نمی‌دهد و کدام رشد را حذف نمی‌کند؟

۴. برای `H_Q=32` و `H_KV=4` اندازهٔ گروه Query را پیدا کنید. نسبت cache آن را به MHA با همان head dimension به دست آورید؛ دربارهٔ کیفیت یا latency چه نتیجه‌ای نمی‌توان گرفت؟

۵. یک ماتریس علّی ۵×۵ و یک پنجرهٔ محلی با `W=2` رسم کنید. در قرارداد پروژه `True` یعنی چه؟ چرا اعمال همان mask بر scoreهای متراکم به‌تنهایی بهبود سرعت را اثبات نمی‌کند؟

۶. با یک مثال توضیح دهید چرا FlashAttention و Sparse Attention دو دستهٔ متفاوت‌اند. کدام‌یک attention دقیق را با I/O کمتر هدف می‌گیرد و کدام‌یک جفت‌های قابل‌توجه را محدود می‌کند؟

۷. در یک MoE با ۶۴ expert و `k=2`، «پارامتر فعال هر توکن» و «پارامتر کل» را تعریف کنید. دو هزینهٔ توزیع expertها میان GPUها را نام ببرید. آیا MoE cache توجه را کاهش می‌دهد؟

۸. RULER، NoLiMa و OOLONG چه نوع دشواری‌هایی را می‌سنجند؟ طرح کوتاهی پیشنهاد دهید که retrieval منفرد، شاهد بدون هم‌پوشانی واژگانی و aggregation را جدا بسنجد.

۹. پروژه را اجرا کنید. تعداد KV head را از ۸ به ۲ تغییر دهید و تخمین حافظهٔ مثال را مقایسه کنید. سپس آزمون cache افزایشی را اجرا کنید؛ چه چیزی را ثابت می‌کند و چه چیزی را ثابت نمی‌کند؟

۱۰. برای سامانه‌ای با هشت درخواست هم‌زمان و اسناد تا ۳۲K توکن، دو طرح کاهش مصرف حافظه پیشنهاد دهید. برای هر طرح یک هزینه/ریسک و یک آزمون کیفیت یا latency بنویسید؛ تنها «حد context را زیاد می‌کنم» پاسخ کافی نیست.

**پروژهٔ تکمیلی:** برای سه طول prompt، یک baseline dense و یک گزینهٔ cache/GQA یا sparse انتخاب کنید؛ در سخت‌افزار قابل‌دسترسی یا شبیه‌ساز شفاف، مقدار cache نظری، peak memory مشاهده‌شده، prefill latency، decode tokens/s و نمرهٔ یک وظیفه را گزارش کنید. اگر GPU یا kernel مناسب ندارید، نتیجه را «اندازه‌گیری نشده» بنویسید و نتیجهٔ فرمول را با benchmark اشتباه نگیرید.

**معیار عبور:** دست‌کم ۸ پاسخ از ۱۰ پاسخ باید واحدها و قراردادهای درست داشته باشد؛ پروژه باید همهٔ آزمون‌های خود را بگذراند؛ و گزارش تکمیلی باید میان ادعای نظری، نتیجهٔ آزمایش مقاله و اندازه‌گیری محلی تمایز بگذارد. پاسخ تشریحی در [پاسخ‌نامهٔ فصل ۳۸](book-engineering/answers/38-long-context-fa.md) است؛ ابتدا خودتان حل کنید.

## ۱۸. جمع‌بندی: سقف، cache و کیفیت سه سؤال‌اند

پنجرهٔ اسمی حداکثر تعداد توکن را مشخص می‌کند؛ زمینهٔ مؤثر عملکرد روی وظیفهٔ واقعی است. Attention dense در prefill با طول به‌طور درجهٔ دوم رشد می‌کند؛ KV Cache در decode از تکرار محاسبهٔ K/V پیشوند جلوگیری می‌کند، اما خودِ حافظه با تعداد لایه، توکن، batch، KV head، بُعد و بایت هر مقدار رشد خطی دارد. GQA/MQA می‌تواند KV را کوچک کند؛ paging و prefix reuse نحوهٔ تخصیص/اشتراک cache را بهبود می‌دهند.

Sparse Attention الگوی ارتباط را محدود می‌کند و برای سود واقعی kernel مناسب می‌خواهد. FlashAttention اجرای dense را از نظر I/O و حافظهٔ موقت بهتر می‌کند، نه اینکه به‌خودی‌خود sparse شود. MoE فقط بخشی از FFNها را برای هر توکن فعال می‌کند، ولی هزینهٔ وزن کل، router، توازن بار و ارتباط بین دستگاه‌ها را حذف نمی‌کند. برای انتخاب، اول پیش‌پردازش، decode، KV، FFN یا کیفیت استدلال را bottleneck کنید؛ بعد گزینه را با معیارهای هم‌پروتکل بسنجید. فصل بعد، معماری Transformer را با تصویر و صوت هم‌تراز می‌کند: فصل ۳۹، Transformer چندوجهی.

## ۱۹. منابع بیرونی و تاریخ بازبینی

پیوندهای زیر در ۵ نوامبر ۲۰۲۶ بازبینی شدند. نتایج عددی هر مقاله فقط برای مدل، benchmark، سخت‌افزار و تنظیم‌هایی است که نویسندگان گزارش کرده‌اند. «پیش‌چاپ» بودن در فهرست مشخص شده است.

1. Dao, T., Fu, D. Y., Ermon, S., Rudra, A., & Ré, C. (2022). “FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness.” *NeurIPS 2022*. [arXiv:2205.14135](https://arxiv.org/abs/2205.14135) · [DOI](https://doi.org/10.48550/arXiv.2205.14135).
2. Dao, T. (2023). “FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning.” *ICLR 2024*. [arXiv:2307.08691](https://arxiv.org/abs/2307.08691).
3. Shazeer, N. (2019). “Fast Transformer Decoding: One Write-Head is All You Need.” arXiv preprint, arXiv:1911.02150. [متن مقاله](https://arxiv.org/abs/1911.02150).
4. Ainslie, J., Lee-Thorp, J., de Jong, M., Zemlyanskiy, Y., Lebrón, F., & Sanghai, S. (2023). “GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints.” *EMNLP 2023*, pp. 4895–4901. [ACL Anthology](https://aclanthology.org/2023.emnlp-main.298/) · DOI: [10.18653/v1/2023.emnlp-main.298](https://doi.org/10.18653/v1/2023.emnlp-main.298).
5. Kwon, W., Li, Z., Zhuang, S., et al. (2023). “Efficient Memory Management for Large Language Model Serving with PagedAttention.” *SOSP 2023*. [arXiv:2309.06180](https://arxiv.org/abs/2309.06180).
6. Beltagy, I., Peters, M. E., & Cohan, A. (2020). “Longformer: The Long-Document Transformer.” arXiv preprint, arXiv:2004.05150. [متن مقاله](https://arxiv.org/abs/2004.05150).
7. Zaheer, M., Guruganesh, G., Dubey, A., et al. (2020). “Big Bird: Transformers for Longer Sequences.” *NeurIPS 2020*. [arXiv:2007.14062](https://arxiv.org/abs/2007.14062).
8. Shazeer, N., Mirhoseini, A., Maziarz, K., et al. (2017). “Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer.” *ICLR 2017*. [arXiv:1701.06538](https://arxiv.org/abs/1701.06538).
9. Fedus, W., Zoph, B., & Shazeer, N. (2022). “Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity.” *Journal of Machine Learning Research, 23*(120), 1–39. [JMLR](https://jmlr.org/papers/v23/21-0998.html) · [arXiv:2101.03961](https://arxiv.org/abs/2101.03961).
10. DeepSeek-AI (2024). “DeepSeek-V3 Technical Report.” arXiv preprint, arXiv:2412.19437. [متن مقاله](https://arxiv.org/abs/2412.19437).
11. Chen, S., Wong, S., Chen, L., & Tian, Y. (2023). “Extending Context Window of Large Language Models via Position Interpolation.” arXiv preprint, arXiv:2306.15595. [متن مقاله](https://arxiv.org/abs/2306.15595).
12. Peng, B., Quesnelle, J., Fan, H., & Shippole, E. (2023). “YaRN: Efficient Context Window Extension of Large Language Models.” arXiv preprint, arXiv:2309.00071. [متن مقاله](https://arxiv.org/abs/2309.00071).
13. Ding, Y., Zhang, L. L., Zhang, C., et al. (2024). “LongRoPE: Extending LLM Context Window Beyond 2 Million Tokens.” arXiv preprint, arXiv:2402.13753. [متن مقاله](https://arxiv.org/abs/2402.13753).
14. Shang, N., Zhang, L. L., Wang, S., et al. (2025). “LongRoPE2: Near-Lossless LLM Context Window Scaling.” arXiv preprint, arXiv:2502.20082. [متن مقاله](https://arxiv.org/abs/2502.20082).
15. Hsieh, C.-P., Sun, S., Kriman, S., et al. (2024). “RULER: What’s the Real Context Size of Your Long-Context Language Models?” *COLM 2024*. [arXiv:2404.06654](https://arxiv.org/abs/2404.06654).
16. Modarressi, A., Deilamsalehy, H., Dernoncourt, F., et al. (2025). “NoLiMa: Long-Context Evaluation Beyond Literal Matching.” *ICML 2025*. [arXiv:2502.05167](https://arxiv.org/abs/2502.05167).
17. Bertsch, A., Pratapa, A., Mitamura, T., Neubig, G., & Gormley, M. R. (2026). “Oolong: Evaluating Long Context Reasoning and Aggregation Capabilities.” *COLM 2026*; arXiv version v2, 5 October 2026. [arXiv:2511.02817v2](https://arxiv.org/abs/2511.02817).
18. Yuan, J., Gao, H., Dai, D., et al. (2025). “Native Sparse Attention: Hardware-Aligned and Natively Trainable Sparse Attention.” *ACL 2025*, pp. 23078–23097. [ACL Anthology](https://aclanthology.org/2025.acl-long.1126/) · DOI: [10.18653/v1/2025.acl-long.1126](https://doi.org/10.18653/v1/2025.acl-long.1126) · [arXiv:2502.11089](https://arxiv.org/abs/2502.11089).
19. Yan, R., Jiang, Y., Chen, Z., et al. (2026). “FSA: An Alternative Efficient Implementation of Native Sparse Attention Kernel.” *ICLR 2026*. [arXiv:2508.18224v3](https://arxiv.org/abs/2508.18224) · [OpenReview/ML Anthology](https://mlanthology.org/iclr/2026/yan2026iclr-fsa/).
20. Tian, A., Ghai, A., Neelam, S., Vasania, Z., & Mishra, A. (2026). “COBS: Cumulant Order Block Sparse Attention.” arXiv preprint v1, submitted 10 July 2026, arXiv:2607.09052. [متن مقاله](https://arxiv.org/abs/2607.09052).
21. Ding, X., Wang, G., Zeng, J., et al. (2026). “Virtual Head Attention.” arXiv preprint v1, submitted 13 October 2026, arXiv:2610.17959. [متن مقاله](https://arxiv.org/abs/2610.17959).
22. Nguyen, X.-P., Pandit, S., Xu, A., Xiong, C., & Joty, S. (2026). “Least-Loaded Expert Parallelism: Load Balancing An Imbalanced Mixture-of-Experts.” arXiv preprint v1, submitted 23 January 2026, arXiv:2601.17111. [متن مقاله](https://arxiv.org/abs/2601.17111).
23. Liu, Z., Yuan, J., Jin, H., Zhong, S., Xu, Z., Braverman, V., Chen, B., & Hu, X. (2024). “KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache.” arXiv preprint, arXiv:2402.02750. [متن مقاله](https://arxiv.org/abs/2402.02750).

## ۲۰. پیوست: کد کامل پروژه

کد زیر با `book-engineering/projects/38-long-context/efficient_attention.py` همسان است؛ آزمون‌های خودکار در `test_efficient_attention.py` و راهنمای اجرا/محدودیت‌ها در `README.md` همان پوشه قرار دارند.

```python
"""Small CPU-friendly demos for KV cache, GQA, local masks, and Switch top-1 MoE.

This is instructional PyTorch code, not a fused or benchmarked GPU kernel.
The attention routine intentionally materializes dense score tensors; a boolean
local mask demonstrates semantics but does not itself skip dense computation.
"""
from __future__ import annotations

import math
from typing import Final

import torch
from torch import Tensor, nn


_INT_FIELDS: Final = (
    "query_length", "key_length", "window_size", "num_layers", "batch_size",
    "sequence_length", "num_kv_heads", "head_dim", "bytes_per_element",
)


def _positive_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


def causal_allowed_mask(
    query_length: int,
    key_length: int,
    *,
    query_offset: int | None = None,
    device: torch.device | str | None = None,
) -> Tensor:
    """Return [Tq,Tk] bool mask where True means that a query may read a key.

    With cached decoding, the default places the query block at the end of the
    key sequence. For example, Tq=1,Tk=5 lets the query read all five keys.
    """
    _positive_int(query_length, "query_length")
    _positive_int(key_length, "key_length")
    offset = key_length - query_length if query_offset is None else query_offset
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValueError("query_offset must be a non-negative integer")
    if offset + query_length > key_length:
        raise ValueError("query positions must lie within the key sequence")
    q_positions = torch.arange(query_length, device=device) + offset
    k_positions = torch.arange(key_length, device=device)
    return k_positions.unsqueeze(0) <= q_positions.unsqueeze(1)


def local_causal_allowed_mask(
    query_length: int,
    key_length: int,
    window_size: int,
    *,
    query_offset: int | None = None,
    device: torch.device | str | None = None,
) -> Tensor:
    """Causal window: each query reads itself and at most window_size-1 past keys."""
    _positive_int(window_size, "window_size")
    allowed = causal_allowed_mask(
        query_length, key_length, query_offset=query_offset, device=device
    )
    offset = key_length - query_length if query_offset is None else query_offset
    q_positions = torch.arange(query_length, device=device) + offset
    k_positions = torch.arange(key_length, device=device)
    recent_enough = k_positions.unsqueeze(0) >= (
        q_positions.unsqueeze(1) - window_size + 1
    )
    return allowed & recent_enough


def grouped_query_attention(
    query: Tensor,
    key: Tensor,
    value: Tensor,
    *,
    causal: bool = False,
    local_window: int | None = None,
    query_offset: int | None = None,
    allowed_mask: Tensor | None = None,
) -> tuple[Tensor, Tensor]:
    """Compute a transparent GQA reference attention.

    Shapes: query [B,Hq,Tq,D], key/value [B,Hkv,Tk,D], with Hq divisible by
    Hkv. Query heads are arranged in contiguous groups that share one KV head.
    ``allowed_mask`` is bool [Tq,Tk] or [B,Tq,Tk], and True means allowed.
    Returns output [B,Hq,Tq,D] and probabilities [B,Hq,Tq,Tk].

    This reference expands work into a dense score tensor. It checks behavior;
    it does not provide sparse or production-kernel speedups.
    """
    tensors = (query, key, value)
    if any(not isinstance(tensor, Tensor) or tensor.ndim != 4 for tensor in tensors):
        raise ValueError("query, key, and value must be rank-4 tensors")
    if any(not tensor.is_floating_point() for tensor in tensors):
        raise ValueError("query, key, and value must use floating-point dtypes")
    if query.device != key.device or key.device != value.device:
        raise ValueError("query, key, and value must be on the same device")
    if query.dtype != key.dtype or key.dtype != value.dtype:
        raise ValueError("query, key, and value must have the same dtype")
    batch, query_heads, query_length, head_dim = query.shape
    key_batch, kv_heads, key_length, key_dim = key.shape
    if batch < 1 or query_heads < 1 or query_length < 1 or key_length < 1 or head_dim < 1:
        raise ValueError("batch, head counts, sequence lengths, and head_dim must be positive")
    if key_batch != batch or value.shape != key.shape:
        raise ValueError("key and value must have matching [B,Hkv,Tk,D] shapes")
    if key_dim != head_dim:
        raise ValueError("query, key, and value head dimensions must match")
    if kv_heads < 1 or query_heads % kv_heads != 0:
        raise ValueError("the positive number of query heads must be divisible by KV heads")
    if not isinstance(causal, bool):
        raise ValueError("causal must be a bool")
    if local_window is not None:
        _positive_int(local_window, "local_window")
        if not causal:
            raise ValueError("local_window is supported only with causal=True")
    if query_offset is not None and not causal:
        raise ValueError("query_offset is meaningful only with causal=True")

    mask: Tensor | None = None
    if causal:
        if local_window is None:
            mask = causal_allowed_mask(
                query_length, key_length, query_offset=query_offset, device=query.device
            )
        else:
            mask = local_causal_allowed_mask(
                query_length, key_length, local_window,
                query_offset=query_offset, device=query.device,
            )
    if allowed_mask is not None:
        if allowed_mask.dtype != torch.bool or allowed_mask.device != query.device:
            raise ValueError("allowed_mask must be a bool tensor on the query device")
        valid_shapes = ((query_length, key_length), (batch, query_length, key_length))
        if tuple(allowed_mask.shape) not in valid_shapes:
            raise ValueError("allowed_mask must have shape [Tq,Tk] or [B,Tq,Tk]")
        mask = allowed_mask if mask is None else (mask & allowed_mask)
    if mask is not None and not bool(mask.any(dim=-1).all()):
        raise ValueError("every query must have at least one allowed key")

    groups = query_heads // kv_heads
    grouped_query = query.reshape(batch, kv_heads, groups, query_length, head_dim)
    scores = torch.einsum("bhgqd,bhkd->bhgqk", grouped_query, key)
    scores = scores / math.sqrt(head_dim)
    if mask is not None:
        expanded_mask = mask if mask.ndim == 2 else mask[:, None, None, :, :]
        scores = scores.masked_fill(~expanded_mask, torch.finfo(scores.dtype).min)
    work_dtype = torch.float32 if scores.dtype in (torch.float16, torch.bfloat16) else scores.dtype
    probabilities = torch.softmax(scores.to(work_dtype), dim=-1).to(query.dtype)
    grouped_output = torch.einsum("bhgqk,bhkd->bhgqd", probabilities, value)
    output = grouped_output.reshape(batch, query_heads, query_length, head_dim)
    return output, probabilities.reshape(batch, query_heads, query_length, key_length)


class KVCache:
    """Minimal append-only self-attention KV cache for a decoding demonstration.

    ``torch.cat`` copies existing data on append; real serving systems commonly
    preallocate or page KV blocks instead. This class is deliberately simple.
    """
    def __init__(self) -> None:
        self.key: Tensor | None = None
        self.value: Tensor | None = None

    @property
    def num_tokens(self) -> int:
        return 0 if self.key is None else int(self.key.shape[2])

    def append(self, key: Tensor, value: Tensor) -> tuple[Tensor, Tensor]:
        if (not isinstance(key, Tensor) or not isinstance(value, Tensor)
                or key.ndim != 4 or value.ndim != 4):
            raise ValueError("new key and value must be rank-4 [B,Hkv,T,D] tensors")
        if key.shape != value.shape or any(size < 1 for size in key.shape):
            raise ValueError("new key and value must have matching, non-empty shapes")
        if key.device != value.device or key.dtype != value.dtype:
            raise ValueError("new key and value must share device and dtype")
        if not key.is_floating_point():
            raise ValueError("new key and value must be floating point")
        if self.key is None:
            self.key, self.value = key, value
        else:
            assert self.value is not None
            if key.shape[:2] != self.key.shape[:2] or key.shape[3] != self.key.shape[3]:
                raise ValueError("new cache chunk has incompatible batch, head, or feature size")
            if key.device != self.key.device or key.dtype != self.key.dtype:
                raise ValueError("new cache chunk must share the existing device and dtype")
            self.key = torch.cat((self.key, key), dim=2)
            self.value = torch.cat((self.value, value), dim=2)
        return self.key, self.value

    def get(self) -> tuple[Tensor, Tensor]:
        if self.key is None or self.value is None:
            raise ValueError("the KV cache is empty")
        return self.key, self.value



def estimate_kv_cache_bytes(
    *,
    num_layers: int,
    batch_size: int,
    sequence_length: int,
    num_kv_heads: int,
    head_dim: int,
    bytes_per_element: int = 2,
) -> int:
    """Estimate self-attention K+V bytes; excludes weights, workspaces, and metadata."""
    values = {
        "num_layers": num_layers,
        "batch_size": batch_size,
        "sequence_length": sequence_length,
        "num_kv_heads": num_kv_heads,
        "head_dim": head_dim,
        "bytes_per_element": bytes_per_element,
    }
    for name, value in values.items():
        _positive_int(value, name)
    return (
        2 * num_layers * batch_size * sequence_length * num_kv_heads
        * head_dim * bytes_per_element
    )


def switch_top1_load_balance_loss(
    probabilities: Tensor,
    selected_experts: Tensor,
    *,
    alpha: float = 1.0,
) -> Tensor:
    """Switch-style top-1 auxiliary loss: alpha * E * sum_i(f_i * P_i).

    ``probabilities`` is [N,E], ``selected_experts`` is [N]. This formula is
    the simple top-1 case; it is not a universal loss for top-k MoE routers.
    """
    if probabilities.ndim != 2 or selected_experts.ndim != 1:
        raise ValueError("probabilities must be [N,E] and selected_experts [N]")
    token_count, expert_count = probabilities.shape
    if token_count < 1 or expert_count < 2 or selected_experts.shape[0] != token_count:
        raise ValueError("load-balancing inputs must contain tokens and at least two experts")
    if not probabilities.is_floating_point() or selected_experts.dtype != torch.long:
        raise ValueError("probabilities must be floating point and selections torch.long")
    if probabilities.device != selected_experts.device:
        raise ValueError("probabilities and selections must be on the same device")
    if not math.isfinite(alpha) or alpha < 0:
        raise ValueError("alpha must be finite and non-negative")
    if not bool(torch.isfinite(probabilities).all()) or bool((probabilities < 0).any()):
        raise ValueError("router probabilities must be finite and non-negative")
    row_sums = probabilities.sum(dim=-1)
    if not torch.allclose(row_sums, torch.ones_like(row_sums), atol=1e-5, rtol=1e-5):
        raise ValueError("each router probability row must sum to one")
    if bool((selected_experts < 0).any()) or bool((selected_experts >= expert_count).any()):
        raise ValueError("selected expert index is outside the expert range")

    fractions = torch.nn.functional.one_hot(
        selected_experts, num_classes=expert_count
    ).to(probabilities.dtype).mean(dim=0).detach()
    mean_probability = probabilities.mean(dim=0)
    return alpha * expert_count * torch.sum(fractions * mean_probability)


class SwitchTop1MoE(nn.Module):
    """Small token-routed top-1 MoE; no capacity limit or distributed dispatch."""
    def __init__(
        self,
        d_model: int,
        hidden_dim: int,
        num_experts: int = 4,
        *,
        aux_loss_weight: float = 0.01,
    ) -> None:
        super().__init__()
        _positive_int(d_model, "d_model")
        _positive_int(hidden_dim, "hidden_dim")
        if isinstance(num_experts, bool) or not isinstance(num_experts, int) or num_experts < 2:
            raise ValueError("num_experts must be an integer of at least two")
        if not math.isfinite(aux_loss_weight) or aux_loss_weight < 0:
            raise ValueError("aux_loss_weight must be finite and non-negative")
        self.d_model = d_model
        self.num_experts = num_experts
        self.aux_loss_weight = float(aux_loss_weight)
        self.router = nn.Linear(d_model, num_experts, bias=True)
        self.experts = nn.ModuleList(
            nn.Sequential(
                nn.Linear(d_model, hidden_dim),
                nn.GELU(),
                nn.Linear(hidden_dim, d_model),
            )
            for _ in range(num_experts)
        )

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        if not isinstance(x, Tensor) or x.ndim not in (2, 3):
            raise ValueError("x must have shape [N,D] or [B,T,D]")
        if x.shape[-1] != self.d_model or any(size < 1 for size in x.shape):
            raise ValueError("x must be non-empty and end with d_model features")
        if not x.is_floating_point():
            raise ValueError("x must be a floating-point tensor")
        original_shape = x.shape
        flat = x.reshape(-1, self.d_model)
        probabilities = torch.softmax(self.router(flat), dim=-1)
        selected = probabilities.argmax(dim=-1)
        selected_probability = probabilities.gather(1, selected[:, None]).squeeze(1)

        output = torch.zeros_like(flat)
        for expert_index, expert in enumerate(self.experts):
            token_indices = torch.nonzero(selected == expert_index, as_tuple=True)[0]
            if token_indices.numel() == 0:
                continue
            expert_input = flat.index_select(0, token_indices)
            expert_output = expert(expert_input)
            gate_weight = selected_probability.index_select(0, token_indices).unsqueeze(-1)
            output = output.index_add(0, token_indices, expert_output * gate_weight)

        aux_loss = switch_top1_load_balance_loss(
            probabilities, selected, alpha=self.aux_loss_weight
        )
        return output.reshape(original_shape), aux_loss, selected.reshape(original_shape[:-1])


def demo() -> None:
    torch.manual_seed(38)
    batch, query_heads, kv_heads, length, head_dim = 1, 8, 2, 5, 16
    query = torch.randn(batch, query_heads, length, head_dim)
    key = torch.randn(batch, kv_heads, length, head_dim)
    value = torch.randn_like(key)
    output, _ = grouped_query_attention(query, key, value, causal=True)
    print(f"causal GQA output: {tuple(output.shape)}")

    cache = KVCache()
    cached_key, cached_value = cache.append(key[:, :, :2], value[:, :, :2])
    cached_key, cached_value = cache.append(key[:, :, 2:3], value[:, :, 2:3])
    print(f"KV cache tokens after two appends: {cache.num_tokens}")
    print(f"cached shapes: {tuple(cached_key.shape)}, {tuple(cached_value.shape)}")

    gqa_bytes = estimate_kv_cache_bytes(
        num_layers=32, batch_size=1, sequence_length=32768,
        num_kv_heads=8, head_dim=128, bytes_per_element=2,
    )
    mha_bytes = estimate_kv_cache_bytes(
        num_layers=32, batch_size=1, sequence_length=32768,
        num_kv_heads=32, head_dim=128, bytes_per_element=2,
    )
    print(f"illustrative 32K BF16 cache: GQA-8={gqa_bytes / 2**30:.1f} GiB; MHA={mha_bytes / 2**30:.1f} GiB")

    moe = SwitchTop1MoE(d_model=16, hidden_dim=32, num_experts=4)
    hidden = torch.randn(2, 3, 16)
    moe_output, aux_loss, expert_ids = moe(hidden)
    print(f"top-1 MoE output: {tuple(moe_output.shape)}; aux_loss={aux_loss.item():.4f}")
    print(f"selected expert IDs: {expert_ids.tolist()}")


if __name__ == "__main__":
    demo()
```

---

# جلد سوم، فصل ۷ — Transformer چندوجهی: اتصال رمزگذارهای تصویر و صوت

**The Art & Science of Building Intelligence | Babak & Ai | فصل سراسری ۳۹ از نقشهٔ پنج‌جلدی**

**تاریخ مرجع و بازبینی منابع: ۵ نوامبر ۲۰۲۶.** این فصل بخش ۷ جلد سوم را می‌بندد؛ فصل بعدی در نقشه، پروژهٔ دادهٔ کوچک است و هنوز جزو این فصل نیست.

**پیش‌نیاز:** تعبیه و توکن‌سازی از فصل ۳۳، Attention و Q/K/V از فصل ۳۴، ماسک از فصل ۳۵، بلوک Transformer از فصل ۳۶، معماری Encoder/Decoder از فصل ۳۷ و ملاحظات زمینه/هزینه از فصل ۳۸. **هدف:** تبدیل هر سیگنال به توکن‌های مناسب، ساختن بازنمایی‌های قابل‌مقایسه، انتخاب میان هم‌ترازی و ادغام، و تشخیص جاهایی که «نزدیک بودن embedding» را نباید فهم یا استدلال فرض کرد.

![شکل ۳-۷-۱ — مسیرهای چندوجهی: تصویر به وصله‌های ViT، صوت به فریم‌های log-Mel و متن به توکن‌ها تبدیل می‌شوند؛ encoderهای جدا با InfoNCE در فضای embedding هم‌تراز می‌شوند، یا توکن‌های یک مدالیته با cross-attention از مدالیتهٔ دیگر اطلاعات می‌گیرند.](assets/images/babak-ai/v3-ch07-multimodal-bridge.webp)

**شکل ۳-۷-۱ — دو هدف جدا: هم‌ترازی بردارهای خلاصه برای جست‌وجو، و تبادل اطلاعات میان توکن‌ها برای وظیفهٔ مشترک.** نمودار مفهومی است؛ اندازهٔ بلوک‌ها یا طول پیکان‌ها مقیاس، کیفیت یا سرعت مدل واقعی را اندازه‌گیری نمی‌کند.

## ۱. چرا یک Transformer را به بیش از یک نوع داده وصل می‌کنیم؟

مدلی که تنها متن می‌بیند از عکس، گفتار، صدای محیط یا ویدئو به شکل مستقیم اطلاعات ندارد. در یک مدل چندوجهی (multimodal)، هر ورودی ابتدا به بازنمایی‌ای تبدیل می‌شود که مدل بتواند محاسبه کند؛ بعد باید تصمیم بگیریم بازنمایی‌ها فقط قابل‌مقایسه باشند یا هنگام حل وظیفه با هم تعامل کنند. این دو نیاز متفاوت‌اند: **retrieval** می‌خواهد «کدام متن با این عکس/صوت جورتر است؟» را پاسخ دهد؛ **پرسش‌وپاسخ** ممکن است لازم داشته باشد چند ناحیهٔ تصویر و چند واژهٔ پرسش به‌صورت مرحله‌ای به هم توجه کنند.

مسیر کلی فصل چنین است: (الف) سیگنال‌ها را به توالیِ مناسب هر رمزگذار ببریم؛ (ب) یک فضای مشترک بسازیم و زیان هم‌ترازی را بفهمیم؛ (ج) تفاوت embeddingِ دوسویه با cross-attention را ببینیم؛ (د) زمان، داده، آزمون و محدودیت‌ها را در طراحی وارد کنیم. «چندوجهی» به‌تنهایی نه معماری یگانه‌ای است، نه تضمین فهم همه‌چیز.

## ۲. هر مدالیته باید قرارداد ورودی خودش را داشته باشد

**مدالیته** (modality) نوعی سیگنال با ساختار و واحد ویژهٔ خود است. متن معمولاً به شناسه‌های توکن تبدیل می‌شود؛ تصویر ممکن است به وصله‌های پیکسلی یا ویژگی‌های چندمقیاسی شکسته شود؛ صوت از موج نمونه‌برداری‌شده یا ویژگی‌هایی مانند log-Mel به فریم‌ها/توکن‌ها می‌رسد. برای Transformer نهایی، همه می‌توانند توالیِ بردار باشند؛ اما تبدیل اولیه و معنای موقعیت در هرکدام یکی نیست.

| ورودی | نمونهٔ نمایش خام/میانی | توالی‌ای که encoder می‌بیند | قراردادهایی که باید ثبت شوند |
|---|---|---|---|
| متن | رشته، شناسهٔ توکن | `[B,L,d]` | tokenizer، زبان، نشانه‌های ویژه، padding و ماسک |
| تصویر | RGB یا کانال‌های دیگر | `[B,N_v,d]` | اندازه/نسبت تصویر، patch/crop، normalization و ترتیب وصله‌ها |
| صوت | waveform یا log-Mel | `[B,N_a,d]` | نرخ نمونه‌برداری، کانال، پنجره/گام، مدت، VAD و padding |
| ویدئو | فریم‌ها همراه timestamp؛ گاهی audio track | `[B,N_t,d]` یا توالی interleaved | fps، timestamp، هم‌زمان‌سازی، نرخ فریم و نگه‌داشتن قطعه‌ها |

این شکل‌ها شماتیک‌اند و batch، padding یا tokenهای ویژه را ساده کرده‌اند. اگر دو نمونه از یک صحنه باشند اما timestamp، crop یا transcript ناسازگار داشته باشند، صرفاً هم‌شکل بودن تنسورها جفت معناییِ درست نمی‌سازد.

## ۳. تصویر به توالی: وصله‌های ViT

در Vision Transformer (ViT) ساده، تصویر `H×W` به مربع‌های `p×p` شکسته می‌شود؛ هر وصله مسطح/پروجکت می‌شود تا یک بردار بسازد و به آن موقعیت داده می‌شود. تعداد وصله‌ها، در نبود padding و crop، چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="تعداد وصله‌های تصویر برابر ارتفاع تقسیم بر اندازهٔ وصله ضرب در عرض تقسیم بر اندازهٔ وصله است؛ attention متراکم روی N وصله تقریباً با N به توان دو رشد می‌کند"><mrow><mi>N</mi><mo>=</mo><mfrac><mi>H</mi><mi>p</mi></mfrac><mo>×</mo><mfrac><mi>W</mi><mi>p</mi></mfrac><mo>,</mo><mspace width="1em"/><mi>Cost</mi><mo>(</mo><mi>attention</mi><mo>)</mo><mo>≈</mo><mi>O</mi><mo>(</mo><msup><mi>N</mi><mn>2</mn></msup><mi>d</mi><mo>)</mo></mrow></math>

برای تصویر `224×224` و `p=16` داریم `14×14=196` وصله. دو برابر کردن هر بُعد به `448×448` تعداد وصله‌ها را چهار برابر (`784`) و جفت‌های dense را حدود شانزده برابر می‌کند، اگر معماری و mask ثابت بمانند. این نسبت هزینهٔ نظری توجه است، نه پیش‌بینی latency کل؛ patch embedding، MLP، batching، kernel و سخت‌افزار نیز دخیل‌اند. ViT نشان داد Transformer می‌تواند دنبالهٔ وصله‌های تصویر را پردازش کند؛ پیش‌آموزش، داده و انتقال به وظیفه هم در نتیجهٔ آن کار اهمیت داشتند [۱].

**پیام مهندسی:** وضوح را فقط برای «جزئیات بیشتر» بالا نبرید. OCR، نمودار و تصویر سند ممکن است به crop/وضوح بیشتری نیاز داشته باشند؛ طبقه‌بندی کلی شاید با وضوح کمتر کافی باشد. ثبت تعداد وصله‌ها، cropها و معیار خطا کمک می‌کند معلوم شود هزینه کجا صرف شده است.

## ۴. متن هم یک encoder دارد، نه یک رشتهٔ جادویی

در مسیر تصویر–متن، tokenizer متن را به شناسه‌ها تبدیل می‌کند؛ embedding و Transformer بازنمایی توکن‌ها را می‌سازند؛ سپس یک pooling rule (مثلاً end-of-text، توکن ویژه یا میانگین masked) و projection، یک بردار خلاصه تولید می‌کنند. جزئیات انتخاب pooling و tokenizer بخشی از checkpoint است؛ تعویضشان بدون ارزیابی ممکن است فضای embedding را ناسازگار کند.

در CLIP، رمزگذار تصویر و رمزگذار متن جداگانه بازنمایی می‌سازند و با جفت‌های تصویر–شرح آموزش می‌بینند؛ همین طراحی، محاسبهٔ متن‌ها و تصاویر را جدا می‌کند و برای جست‌وجو مناسب است [۲]. مدل متن در چنین سامانه‌ای لزوماً یک LLM مولد نیست. همچنین «بردار متن با بردار تصویر مقایسه شد» به این معنا نیست که مدل توانسته متن را با ناحیهٔ دقیق تصویر یا ترتیب چند رویداد پیوند دهد.

برای متن فارسی، باید tokenizer، داده، نیم‌فاصله، خط، نویسه‌های مخلوط، زبان شرح و شیوهٔ pooling را جدا آزمود. پشتیبانی از چند زبان در مدل‌کارت یا مقاله جایگزین آزمون روی پرس‌وجوها و تصاویر موردنیاز شما نیست.

## ۵. فضای embedding مشترک: نزدیک‌بودن را با چه چیزی می‌سنجیم؟

فرض کنید encoder تصویر بردار `hᵛ` و encoder متن بردار `hᵗ` می‌سازد. projectionهای جدا آن‌ها را به بُعد مشترک می‌برند و معمولاً نرمال‌سازی L2 می‌کنند. شباهت cosine میان بردارهای نرمال‌شده برابر ضرب داخلی آن‌ها است؛ عدد بزرگ‌تر یعنی مدل در فضای آموخته‌شده آن جفت را نزدیک‌تر گذاشته است، نه اینکه یک احتمالِ کالیبره‌شده یا داوریِ انسانی باشد.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="بردار تعبیهٔ واحد برابر projection بر طول اقلیدسی آن است؛ شباهت کسینوسی دو بردار نرمال‌شده برابر ضرب داخلی آن‌هاست"><mrow><mi>z</mi><mo>=</mo><mfrac><mrow><mi>W</mi><mi>h</mi></mrow><msub><mrow><mo>∥</mo><mi>W</mi><mi>h</mi><mo>∥</mo></mrow><mn>2</mn></msub></mfrac><mo>,</mo><mspace width="1em"/><mi>sim</mi><mo>(</mo><msub><mi>z</mi><mi>i</mi></msub><mo>,</mo><msub><mi>z</mi><mi>j</mi></msub><mo>)</mo><mo>=</mo><msubsup><mi>z</mi><mi>i</mi><mi>⊤</mi></msubsup><msub><mi>z</mi><mi>j</mi></msub></mrow></math>

با داشتن یک پرس‌وجوی تصویری، می‌توان embedding آن را با embedding شرح‌های ازپیش‌محاسبه‌شده مقایسه کرد و top-k را بازیابی کرد. در reverse retrieval، متن query است و تصاویر candidate. این سازوکار **هم‌ترازی سراسری** را بهینه می‌کند؛ ممکن است «یک سگ روی کاناپه» و «یک سگ در پارک» را به‌خاطر واژهٔ مشترک نزدیک بگذارد، هرچند رابطهٔ فضایی متفاوت باشد.

## ۶. InfoNCE: جفت درست را میان جفت‌های دسته پیدا کن

در دسته‌ای با `B` جفت متن–تصویر، encoderها ماتریس شباهت `B×B` می‌سازند. قطر ماتریس جفت‌های مثبتِ داده‌شده است؛ خانه‌های دیگر در حالت ساده منفی فرض می‌شوند. دما/مقیاس logits بر تیزی توزیع اثر دارد. زیان contrastiveِ متن‌به‌تصویر و تصویر‌به‌متن میانگین گرفته می‌شود:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="لوگیت تصویر متن برابر مقیاس ضربدر ضرب داخلی embeddingهای نرمال‌شده است؛ هدف هر سطر جایگاه مثبت روی قطر ماتریس شباهت است"><mrow><msub><mi>s</mi><mrow><mi>i</mi><mi>j</mi></mrow></msub><mo>=</mo><mi>α</mi><mo>·</mo><msubsup><mi>z</mi><mi>i</mi><mi>image</mi></msubsup><msubsup><mi>z</mi><mi>j</mi><mi>text</mi></msubsup><mo>,</mo><mspace width="0.8em"/><msub><mi>y</mi><mi>i</mi></msub><mo>=</mo><mi>i</mi></mrow></math>

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="زیان تصویر به متن منفی میانگین لگاریتم احتمال کلاس جفت درست است؛ زیان دوطرفه میانگین مسیر تصویر به متن و متن به تصویر است"><mrow><msub><mi>L</mi><mrow><mi>i</mi><mo>→</mo><mi>t</mi></mrow></msub><mo>=</mo><mo>−</mo><mfrac><mn>1</mn><mi>B</mi></mfrac><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>B</mi></munderover><mi>log</mi><mfrac><mrow><mi>exp</mi><mo>(</mo><msub><mi>s</mi><mrow><mi>i</mi><mi>i</mi></mrow></msub><mo>)</mo></mrow><mrow><munderover><mo>∑</mo><mrow><mi>j</mi><mo>=</mo><mn>1</mn></mrow><mi>B</mi></munderover><mi>exp</mi><mo>(</mo><msub><mi>s</mi><mrow><mi>i</mi><mi>j</mi></mrow></msub><mo>)</mo></mrow></mfrac><mo>,</mo><mspace width="0.8em"/><mi>L</mi><mo>=</mo><mfrac><mrow><msub><mi>L</mi><mrow><mi>i</mi><mo>→</mo><mi>t</mi></mrow></msub><mo>+</mo><msub><mi>L</mi><mrow><mi>t</mi><mo>→</mo><mi>i</mi></mrow></msub></mrow><mn>2</mn></mfrac></mrow></math>

این یک نمونهٔ هدف است، نه تنها راه آموزش چندوجهی. کد پروژه برای هر جفت modality همین زیان متقارن را روی batch کوچک اجرا می‌کند. اگر چند caption واقعاً دربارهٔ یک تصویر باشند، فرض «فقط قطر مثبت است» می‌تواند هم‌معناها را به‌اشتباه منفی بخواند؛ کیفیت داده و ساخت loss را همراه با مدل طراحی کنید.

## ۷. مثبت و منفی را خود داده تعیین نمی‌کند

«مثبت» و «منفی» برچسب‌های آموزشی‌اند، نه حقیقت جهان. دو شرح متفاوت ممکن است هر دو درست باشند؛ دو تصویر متفاوت ممکن است هر دو یک شیء یا مفهوم را نشان دهند. در مقابل، شرح کلی می‌تواند با تصویر جور باشد اما رنگ، شمار، نسبت فضایی یا زمان را جا بیندازد. جفت‌های اشتباه یا شرح‌های کم‌کیفیت به مدل یاد می‌دهند shortcutهای آماری را دنبال کند.

InfoNCE معمولی برای هر جفت، بقیهٔ اعضای همان batch را منفی می‌گیرد. وقتی batch بزرگ‌تر می‌شود، سیگنال منفی بیشتری داریم، ولی احتمال جفت‌های هم‌معنا/تکراری یا false negative هم بالا می‌رود. زیان sigmoid خانوادهٔ SigLIP برای جفت‌ها هدف دودویی را به‌کار می‌گیرد و به نرمال‌سازی سراسری softmax روی ماتریس شباهت به همان شکل CLIP وابسته نیست؛ این یک تغییر تابع زیان است، نه تضمین پاک‌بودن برچسب‌ها یا برتری روی همهٔ داده‌ها [۳].

کنترل‌های عملی: تکرار تصویر و متن را پیدا کنید؛ شرح‌های چندگانه را نگه دارید؛ جفت‌های مبهم را جدا برچسب بزنید؛ در صورت امکان چند مثبت برای یک نمونه ثبت کنید؛ و روی گروه‌هایی با محتوای مشابه معیار بگیرید. افزایش batch به‌تنهایی جای پاک‌سازی، اسناد داده و تحلیل false negative را نمی‌گیرد.

## ۸. Dual-encoder یا cross-encoder: جست‌وجو با فهم جفت فرق دارد

**Dual-encoder:** هر تصویر/متن را یک بار مستقل encode می‌کند؛ سپس شباهت بردارها را برای مقایسهٔ تعداد زیادی candidate می‌سنجد. embeddingهای corpus را می‌توان پیش‌محاسبه و در index جست‌وجو کرد. به همین دلیل این طرح معمولاً مرحلهٔ نخستِ مقیاس‌پذیر برای retrieval است.

**Cross-encoder:** دو ورودی را با هم وارد لایه‌های تعامل می‌کند؛ مثلاً توکن‌های متن مستقیماً به توکن‌های تصویر توجه می‌کنند. از آن‌جا که تعامل هر جفت باید جدا محاسبه شود، معمولاً آن را روی shortlistی که dual-encoder بازیابی کرده اجرا می‌کنند. Cross-encoder ممکن است به رابطهٔ جزئی‌تری پاسخ دهد، اما اگر به تصویر/شرح دقیق وابسته باشد همچنان می‌تواند شکست بخورد؛ اسم معماری کیفیت را تضمین نمی‌کند.

| پرسش محصول | انتخاب اولیهٔ معقول | آنچه باید سنجید |
|---|---|---|
| «از صدها هزار تصویر کدام‌ها با این query می‌خوانند؟» | Dual-encoder + index + reranker اختیاری | Recall@k، latency، زبان/دامنهٔ query |
| «به پرسش دربارهٔ ناحیه یا رابطه پاسخ بده» | encoder تصویری با تعامل متنی، localization یا decoder | شواهد ناحیه‌ای، خطای OCR، grounded answer |
| «جملهٔ شنیده‌شده را از آرشیو صدا پیدا کن» | audio–text encoder یا زنجیرهٔ ASR + retrieval | نویز، لهجه، زبان، طول و زمان‌بندی |

## ۹. Cross-attention: پل میان توکن‌ها

برای queryهای متن، `Q` از توکن‌های متن و `K,V` از توکن‌های تصویر (یا صوت) می‌آیند؛ وزن‌ها تعیین می‌کنند هر query چه بخشی از حافظه را بخواند. باقیمانده، نرمال‌سازی و شبکهٔ پیش‌خور، خروجی را دوباره در مسیر Transformer قرار می‌دهند. اگر متن چند پرسش دارد، هر توکن پرسش می‌تواند به جاهای متفاوتی از تصویر توجه کند؛ این تعامل از یک شباهت میان دو بردار خلاصه غنی‌تر است، ولی به‌تنهایی grounding درست را تضمین نمی‌کند.

BLIP-2 یک نمونه از پل کم‌پارامتر میان encoder تصویری منجمد و LLM منجمد است: Querying Transformer (Q-Former) از encoder تصویر اطلاعات می‌گیرد و به مسیر زبانی می‌رساند [۹]. Flamingo نیز اتصال مدل دیداری و زبانی ازپیش‌آموزش‌دیده و ورودی‌های متن/تصویر درهم‌تنیده را بررسی کرد [۱۰]. این‌ها نمونهٔ طراحی‌اند؛ تفاوت مرحلهٔ آموزش، تعداد پارامترهای قابل‌آموزش و داده را در مقایسه‌ها نگه دارید.

در پروژهٔ این فصل، توکن‌های متن query دو ماژول cross-attention مستقل‌اند: یکی حافظهٔ تصویر را می‌خواند و دیگری صوت را. نسخهٔ آموزشی به دلایل وضوح، temporal mask یا decoder مولد ندارد. پس آن را نمونهٔ **اتصال اطلاعات** بدانید، نه بازسازی معماری BLIP-2 یا Flamingo.

## ۱۰. صوت: از waveform تا فریم‌های قابل‌پردازش

موج دیجیتال دنباله‌ای از دامنهٔ سیگنال در نرخ نمونه‌برداری مشخص است. طول waveform به ثانیه و نرخ نمونه بستگی دارد؛ با تبدیل STFT می‌توان پنجره‌های کوتاه را به طیف و معمولاً فیلترهای Mel را به ویژگی‌های کم‌بعدتر تبدیل کرد. با پنجرهٔ ۲۵ms و گام ۱۰ms، فریم‌ها هر ۱۰ms جابه‌جا می‌شوند؛ مرز دقیق و نرخ‌ها وابسته به مدل و preprocessing است، نه استاندارد واحد همهٔ encoderها.

**نرخ نمونه‌برداری مهم است.** بازتفسیر waveform با نرخ دیگری—بدون resampling—سرعت و pitch مؤثر را عوض می‌کند. همچنین stereo-to-mono، clipping، normalization، silence/VAD و مدت crop روی نتیجه اثر دارند. شکل ورودی «`[B,mel,T]`» فقط قرارداد تنسور است؛ تعداد mel bins، window, hop, sample rate و normalization را باید در metadata مدل ثبت کرد.

کد پروژه waveform نمی‌خواند. ورودی آن feature ساختگیِ شبیه log-Mel است که چند فریم را با Conv1d گروه‌بندی می‌کند؛ این میان‌بُر آموزشی برای نشان‌دادن توکن‌های صوت است و جایگزین frontend صوت واقعی نیست.

## ۱۱. سه وظیفهٔ صوتی را یکی نگیریم

**بازنمایی گفتار:** wav2vec 2.0 روی صوتِ بدون متن، نمایش‌های latent را با هدف خودنظارتی/contrastive می‌آموزد و سپس برای کارهایی چون بازشناسی گفتار fine-tune می‌شود [۵]. **بازشناسی گفتار (ASR):** Whisper یک مسیر نظارت‌شدهٔ ضعیف‌برچسب‌خورده برای پیش‌بینی transcript و کارهای مرتبط بررسی کرد [۶]. **توصیف/جست‌وجوی صوت:** CLAP متن و صوت را برای retrieval و classification صفرنمونه‌ای در آزمایش‌های خودش هم‌تراز کرد [۷].

این دسته‌ها می‌توانند در یک محصول ترکیب شوند، اما برچسب و خروجی یکسان ندارند: transcript حرف‌ها را هدف می‌گیرد؛ embedding صوتی ممکن است ویژگی‌های رویداد را نگه دارد؛ caption می‌تواند «صدای زنگ و ترمز» را توصیف کند؛ تولید گفتار وظیفهٔ دیگری است. یک مدل speech encoder لزوماً صدای موتور، موسیقی یا هم‌زمانی دو گوینده را به‌خوبی تحلیل نمی‌کند.

پیش از انتخاب، پرسش را دقیق بنویسید: آیا به متن پیاده‌شده نیاز است، رخداد صوتی، speaker، زمان شروع رویداد، caption، یا پیوند audio و تصویر؟ سپس encoder، داده، معیار و سیاست حفظ فایل خام را با همین هدف تطبیق دهید.

## ۱۲. اتصال چند مدالیته: فضای مشترک همه‌به‌همه لازم نیست

یک راه ساده، ساخت جفت متن–تصویر و جداگانه متن–صوت است و نگاشت هر encoder به بُعد مشترک. سپس تصویر و صوت هم از طریق متن در گراف جفت‌ها قابل مقایسه می‌شوند، اما کیفیت این مسیر به پوشش مفاهیم و زبان در پیوندها وابسته است. ImageBind نشان داد در تنظیم مقالهٔ آن می‌توان شش مدالیته—تصویر، متن، صوت، عمق، حرارتی و IMU—را به فضای embedding مشترک برد، بدون اینکه هر ترکیب دوتایی مستقیماً دادهٔ paired داشته باشد [۸]. این ادعا به روش و آزمایش همان مقاله محدود است؛ جفت‌شدن از راه یک anchor همهٔ رابطه‌های ظریف یا modal gap را از میان نمی‌برد.

در طراحی داده، می‌توان جفت‌ها را به شکل گراف دید: گره‌ها modality/encoderها و یال‌ها نمونه‌های paired و هدف‌های آموزشی‌اند. یال کم‌پوشش یا نویزی روی مسیرهای چندمرحله‌ای اثر می‌گذارد. بنابراین علاوه بر کیفیت هر جفت، سؤال کنید هر مفهوم، زبان، طول، کانال صوت و شرایط تصویری با چه مسیرهایی به فضای مشترک می‌رسد.

## ۱۳. صوت و تصویر زمان‌مندند؛ هم‌ترازی فقط یک cosine نیست

در تصویر ثابت و جملهٔ کوتاه می‌توان یک embedding برای هر نمونه در نظر گرفت؛ اما ویدئو/صوت دنباله‌های زمان‌مند با نرخ‌های مختلف‌اند. یک ثانیهٔ ویدئو می‌تواند چندین frame داشته باشد و صوت در هر ثانیه هزاران نمونه؛ پس لازم است timestampها، chunkها و موقعیت‌های زمان‌محور را به توکن‌ها نسبت دهیم. هم‌ترازی سراسری شاید «صدای پارس و سگ» را نزدیک کند، ولی نمی‌گوید پارس دقیقاً کدام لحظه/فریم رخ داده است.

Qwen2.5-Omni در گزارش خود، برای ورودی ویدئو/صوت هم‌زمان از chunking encoderها و TMRoPE (Time-aligned Multimodal RoPE) برای موقعیت زمانی یاد می‌کند؛ در همان گزارش Thinker/Talker وظایف فهم/متن و تولید گفتار را در معماری مرتبط می‌کند [۱۳]. پژوهش TaRoPE در ۲۰۲۶ به mismatch نرخ فریم صوت/ویدئو و هم‌ترازی ویژگی‌های زمانی در یک وظیفهٔ خاصِ تشخیص هیجان صوتی–دیداری می‌پردازد؛ نتیجه‌اش را به همهٔ وظایف تعمیم ندهید [۱۵].

پروتکل پایه: timestamp یک رویداد را با دقت معلوم ثبت کنید؛ از frameهای نزدیک و قطعه‌های صوت هم‌زمان نمونه بگیرید؛ بررسی کنید resampling، crop و buffering زمان‌ها را جابه‌جا نکرده باشد؛ سپس هم retrieval کل کلیپ و هم تشخیص زمان رویداد را جدا ارزیابی کنید. بخش ۱۸ نمونه‌های تازه‌تر را مرور می‌کند.

## ۱۴. سه الگوی ادغام و جایی که تعامل رخ می‌دهد

| راهبرد | محل تعامل | مزیت معمول | هزینه/ریسک معمول |
|---|---|---|---|
| **Early fusion** | توکن‌های چند مدالیته زود در یک توالی ادغام می‌شوند | امکان مدل‌کردن وابستگی‌های مشترک در لایه‌ها | طول توالی/ماسک پیچیده‌تر؛ کمبود داده paired می‌تواند مشکل‌ساز شود |
| **Late fusion** | هر encoder جدا کار می‌کند؛ بردار یا score در پایان ترکیب می‌شود | محاسبهٔ مستقل و cache/index ساده‌تر | جزئیات ناحیه‌ای یا زمانی ممکن است در pooling گم شود |
| **Bridge / cross-attention** | چند query یا لایهٔ connector به encoder دیگر دسترسی دارد | راهی برای اتصال encoderهای ازپیش‌آموزش‌دیده و کاهش آموزش کامل | انتخاب تعداد query، اطلاعات حذف‌شده و bias encoder پایه مهم است |
| **Hybrid** | ترکیبی از late/bridge و ادغام در چند مرحله | امکان توازن هزینه و تعامل | دشوارتر برای ablation، اشکال‌زدایی و attribution خطا |

این‌ها خانواده‌های طراحی‌اند، نه ranking. نیاز محصول، نوع داده و بودجه تعیین می‌کند چه چیزی بسازیم. یک ablation منصفانه ثابت نگه می‌دارد: داده، split، pretrained checkpoint، optimizer، تعداد update و معیار؛ سپس فقط محل/نوع fusion را تغییر می‌دهد.

## ۱۵. Encoder را منجمد کنیم یا آموزش دهیم؟

اگر encoderهای ازپیش‌آموزش‌دیده داریم، **freeze** کردن وزن آن‌ها و آموزش یک projection/connector سبک می‌تواند آزمایش را ارزان‌تر و ساده‌تر کند. اما اگر زبان، دامنهٔ تصویر، sampling یا وظیفه با دادهٔ پایه فرق کند، نمای ثابت ممکن است اطلاعات لازم را نداشته باشد. در **partial unfreezing** لایه‌های بالایی یا adapterها آموزش می‌بینند؛ **full fine-tuning** آزادی بیشتری دارد، اما داده/حافظه و خطر forgetting و overfit را هم بالا می‌برد.

یک آزمایش مرحله‌ای: ابتدا baseline منجمد؛ بعد connector/LoRA؛ سپس unfreeze کنترل‌شده؛ همه با validation/test پاک و جدا. هزینه را با trainable parameters تنها نسنجید: activation، optimizer state، decoder و اندازهٔ sequence هم مصرف دارند. دقت روی دادهٔ train یا چند prompt دستی معیار انتخاب نهایی نیست.

## ۱۶. ارزیابی: retrieval، جزئیات و استدلال سه آزمون‌اند

**Retrieval:** Recall@k، MRR یا nDCG را روی gallery ثابت بسنجید؛ هم text→image و image→text، هم زبان‌ها/دامنه‌های جدا. **Local grounding:** برای اینکه تصویر/فریم کدام ناحیه شاهد پاسخ است، IoU/grounding یا بررسی انسانیِ ناحیه‌ای لازم است. **ASR:** WER/CER و خطا برحسب لهجه، نویز و زبان. **زمان‌مندی:** onset/segment، timestamp tolerance و رویداد هم‌زمان. **پرسش‌وپاسخ:** correctness باید همراه با شاهد و خطای hallucination بررسی شود؛ امتیاز embedding similarity جای پاسخ مستند نیست.

MMMU نمونه‌ای از benchmark چندرشته‌ای است که پرسش‌های تصویرمحور و استدلالی در موضوعات دانشگاهی را هدف می‌گیرد [۱۲]. چنین benchmarkی retrieval ساده را با VQA و grounding یکی نمی‌کند. پیش از استناد به امتیاز، نسخهٔ داده، split، روش prompt، ابزار کمکی، metric، آلودگی احتمالی و شرایط اجرای همان paper را ثبت کنید؛ یک بنچمارک به‌تنهایی همهٔ محصول را پوشش نمی‌دهد.

## ۱۷. «هم‌ترازی» چه چیزی را حل نمی‌کند؟

1. **سطحی‌بودن برچسب:** caption کوتاه ممکن است جزئیات ریز، روابط، نفی، تعداد یا ترتیب رخداد را نگوید.
2. **false negative و چند مثبت:** جفت‌های مشابه می‌توانند در batch به‌غلط منفی شوند؛ score یادگرفته‌شده حقیقت قطعی نیست.
3. **سوگیری پوشش:** وب‌داده ممکن است بعضی زبان‌ها/فرهنگ‌ها، صداها، چهره‌ها، اسناد یا شرایط ضبط را بیش/کم‌تر نمایندگی کند. «multilingual» در عنوان paper تضمین برابری برای زبان/وظیفهٔ شما نیست؛ SigLIP 2 مثلاً recipe و ارزیابی چندزبانهٔ خودش را گزارش می‌کند [۴].
4. **leakage و مجوز:** near-duplicate میان train/test، حق استفادهٔ تصویر/صوت، رضایت و دادهٔ حساس باید بررسی شود. مقالهٔ DataComp توجه پژوهش را صریحاً به ساخت/فیلتر مجموعه‌داده و ارزیابی استاندارد می‌برد [۱۱]؛ این کار جایگزین بررسی حقوقی dataset مشخص نیست.
5. **shortcut و تغییر دامنه:** پس‌زمینه یا watermark می‌تواند label را لو بدهد؛ تغییر دوربین/نویز/زبان retrieval را عوض می‌کند.
6. **اعتماد کاذب:** نزدیک‌ترین vector ممکن است نامرتبط باشد، و مدل مولد می‌تواند با اطمینان پاسخ نادرست بسازد. threshold باید با calibration و هزینهٔ خطای محصول سنجیده شود.

برای تصمیم عملی، نمونه‌های خطا را به علت دسته‌بندی کنید: preprocessing، coverage، label, geometry/time, model capacity, evaluation leakage یا prompt. تا وقتی منبع خطا مشخص نیست، اضافه‌کردن داده و پارامتر صرفاً هزینه را زیاد می‌کند.

## ۱۸. پژوهش‌های تازه تا ۵ نوامبر ۲۰۲۶: نشانه‌اند، نه نسخهٔ نهایی

**SigLIP 2 (۲۰۲۵)** خانواده‌ای از encoderهای چندزبانهٔ تصویر–متن را با recipe شامل captioning، self-supervision و data curation گزارش می‌کند و localization/dense feature را هم ارزیابی می‌کند [۴]. **Qwen2.5-Omni (۲۰۲۵)** به stream چندوجهی متن، تصویر، صوت و ویدئو و تولید هم‌زمان متن/گفتار می‌پردازد [۱۳]. این‌ها دو سطح متفاوت‌اند: encoder embedding برای retrieval با سیستم end-to-end که چند نوع خروجی/وظیفه دارد یکی نیست.

**WAVE** در ICLR 2026، از مدل زبانی چندوجهی برای embeddingهای متن، صوت، ویدئو و ورودی صوتی–دیداری، feature fusion سلسله‌مراتبی و آموزش مشترک استفاده می‌کند؛ مقالهٔ خودش retrieval هر-به-هر و embedding وابسته به prompt را در benchmarkهای خودش گزارش می‌کند [۱۴]. این نتیجه را «هر مدل بزرگ خودبه‌خود audio/video را خوب embed می‌کند» تعبیر نکنید.

**Virtual Encoders in Multimodal Transformers** (نسخهٔ ۱۹ اکتبر ۲۰۲۶، مقالهٔ کارگاهی ACCV 2026) بررسی می‌کند که Transformer مشترک، وقتی encoder ادراکیِ کامل جداگانه ندارد، ممکن است در لایه‌های ابتدایی/میانی محاسبهٔ encoderمانندی انجام دهد [۱۶]. این یک تحلیل پژوهشی تازه دربارهٔ مرز عملکردیِ perception است، نه راهنمای قطعی برای حذف همهٔ encoderهای اختصاصی. ادبیات چندوجهی سریع تغییر می‌کند؛ تاریخ نسخه و محدودیت همان کار را کنار هر نتیجه نگه دارید.

## ۱۹. پروژهٔ کوچک، آزمون‌ها و مسیر تصمیم‌گیری

در `projects/39-multimodal-transformer/` سه encoder تصادفی با PyTorch ساخته شده‌اند: وصله‌های تصویر، توکن‌های متن و ویژگی‌های شبیه log-Mel. سه projection به بُعد مشترک می‌رسند؛ زیان سه‌طرفهٔ InfoNCE جفت‌های image–text، image–audio و text–audio را مقایسه می‌کند؛ شاخهٔ جداگانه‌ای نیز توکن‌های متن را با cross-attention به تصویر و صوت وصل می‌کند. خروجی مورد انتظار: embeddingهای `[4,16]`، توکن‌های متنِ ادغام‌شده `[4,6,32]`، loss متناهی و گرادیان.

```bash
cd book-engineering/projects/39-multimodal-transformer
python -m unittest discover -v
python multimodal_alignment.py
```

۱۵ آزمون shape، قرارداد ماسک، طول معتبر صوت، نرمال‌سازی، جفت مرتب/به‌هم‌ریخته، گرادیان شاخه‌ها و ورودی نامعتبر را بررسی می‌کنند. وزن تصادفی و دادهٔ مصنوعی‌اند؛ این پروژه **retrieval، آموزش معنادار، کیفیت alignment، سرعت، waveform واقعی یا تولید زبان را نشان نمی‌دهد**. کد کامل در بخش ۲۰ و توضیح اجرا در [README پروژه](book-engineering/projects/39-multimodal-transformer/README.md) است.

### تمرین و پروژهٔ تکمیلی

1. تصویر `384×256` با وصلهٔ `16×16` چند وصله دارد؟ اگر هر دو بُعد دو برابر شوند، نسبت تعداد وصله و جفت‌های dense چه می‌شود؟ فرض‌های مرزی را بنویسید.
2. در batch چهار، چرا InfoNCE ساده سه عضو دیگر را منفی می‌گیرد؟ یک مثال بیاورید که این فرض false negative بسازد و یک اصلاح داده/loss پیشنهاد کنید.
3. برای جست‌وجوی میلیون تصویر، چرا dual-encoder را می‌توان مرحلهٔ نخست گرفت؟ cross-encoder را در چه مرحله‌ای به‌کار می‌برید؟ هزینه و metric هر مرحله را جدا کنید.
4. نمونهٔ گفتار با نرخ 16 kHz را می‌خواهید برای مدلی با frontend تعریف‌شده در 24 kHz آماده کنید. چرا تغییر برچسب sample rate بدون resampling نادرست است؟ دست‌کم چهار metadata لازم را فهرست کنید.
5. ویدئویی از آشپزی دارید که یک صدای کوتاه هم‌زمان با یک فریم رخ می‌دهد. چه دادهٔ زمانی، fusion و metric لازم است تا رویداد را پیدا کنید، نه فقط کلیپ مشابه را؟
6. طرح dataset متن–تصویر–صوت کوچک بسازید: مجوز/رضایت، چند caption، split براساس منبع، حذف duplicate، annotation خطا و test زبان/گروه‌ها را مستند کنید.
7. در کد، اگر متن هم‌تراز با تصویر است ولی فایل صوتی از کلیپ دیگری آمده، کدام lossها جفت غلط را تشویق می‌کنند؟ چه guard در dataset pipeline اضافه می‌کنید؟
8. پروژهٔ تکمیلی: frozen encoderهای pretrained را جایگزین encoderهای toy کنید؛ retrieval دوطرفه، false negative، زمان استنتاج و دقت روی یک set جدا را گزارش کنید. مدل‌کارت و محدودیت مجوز را ضمیمه کنید.

برای پاسخ تشریحی به [پاسخ‌نامهٔ فصل ۳۹](book-engineering/answers/39-multimodal-transformer-fa.md) رجوع کنید. فصل بعدی طبق نقشه، فصل سراسری ۴۰ است؛ موضوع آن دادهٔ کوچک و آماده‌سازی آن خواهد بود و این فصل آن محتوا را پیشاپیش نمی‌نویسد.

### راهنمای انتخاب در یک دقیقه

- **پیداکردن/مرتب‌کردن تعداد زیادی نمونه:** dual-encoder، embeddingهای cacheشدنی و معیار retrieval.
- **گفت‌وگوی دقیق دربارهٔ ناحیه/جزئیات:** cross-attention یا مدل grounding، همراه با آزمون ناحیه‌ای و شاهد.
- **گفتار به متن:** ASR و معیار transcript؛ **رویداد صوتی به شرح:** audio–text alignment و معیار retrieval/caption.
- **رویداد audio–video زمان‌مند:** timestamp، chunk alignment و آزمون زمانی؛ یک embedding سراسری کافی نیست.
- **مدل موجود را به دامنهٔ تازه ببر:** ابتدا split و خط پایه، سپس connector/adapter و در پایان unfreeze کنترل‌شده.

### منابع بیرونی و تاریخ بازبینی

منابع اولیه/مقالات:

1. Dosovitskiy et al., “An Image is Worth 16×16 Words: Transformers for Image Recognition at Scale,” ICLR 2021, [arXiv:2010.11929](https://arxiv.org/abs/2010.11929). مراجعه: ۵ نوامبر ۲۰۲۶.
2. Radford et al., “Learning Transferable Visual Models From Natural Language Supervision,” 2021, [arXiv:2103.00020](https://arxiv.org/abs/2103.00020). مراجعه: ۵ نوامبر ۲۰۲۶.
3. Zhai et al., “Sigmoid Loss for Language Image Pre-Training,” ICCV 2023, [arXiv:2303.15343](https://arxiv.org/abs/2303.15343). مراجعه: ۵ نوامبر ۲۰۲۶.
4. Tschannen et al., “SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features,” 2025, [arXiv:2502.14786](https://arxiv.org/abs/2502.14786). مراجعه: ۵ نوامبر ۲۰۲۶.
5. Baevski et al., “wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations,” NeurIPS 2020, [arXiv:2006.11477](https://arxiv.org/abs/2006.11477). مراجعه: ۵ نوامبر ۲۰۲۶.
6. Radford et al., “Robust Speech Recognition via Large-Scale Weak Supervision,” 2022, [arXiv:2212.04356](https://arxiv.org/abs/2212.04356). مراجعه: ۵ نوامبر ۲۰۲۶.
7. Wu et al., “Large-scale Contrastive Language-Audio Pretraining with Feature Fusion and Keyword-to-Caption Augmentation,” ICASSP 2023, [arXiv:2211.06687](https://arxiv.org/abs/2211.06687). مراجعه: ۵ نوامبر ۲۰۲۶.
8. Girdhar et al., “ImageBind: One Embedding Space To Bind Them All,” CVPR 2023, [arXiv:2305.05665](https://arxiv.org/abs/2305.05665). مراجعه: ۵ نوامبر ۲۰۲۶.
9. Li et al., “BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models,” ICML 2023, [arXiv:2301.12597](https://arxiv.org/abs/2301.12597). مراجعه: ۵ نوامبر ۲۰۲۶.
10. Alayrac et al., “Flamingo: a Visual Language Model for Few-Shot Learning,” NeurIPS 2022, [arXiv:2204.14198](https://arxiv.org/abs/2204.14198). مراجعه: ۵ نوامبر ۲۰۲۶.
11. Gadre et al., “DataComp: In search of the next generation of multimodal datasets,” NeurIPS 2023 Datasets and Benchmarks, [arXiv:2304.14108](https://arxiv.org/abs/2304.14108). مراجعه: ۵ نوامبر ۲۰۲۶.
12. Yue et al., “MMMU: A Massive Multi-discipline Multimodal Understanding and Reasoning Benchmark for Expert AGI,” CVPR 2024 Oral, [arXiv:2311.16502](https://arxiv.org/abs/2311.16502). مراجعه: ۵ نوامبر ۲۰۲۶.
13. Xu et al., “Qwen2.5-Omni Technical Report,” 2025, [arXiv:2503.20215](https://arxiv.org/abs/2503.20215). مراجعه: ۵ نوامبر ۲۰۲۶.
14. Tang et al., “WAVE: Learning Unified & Versatile Audio-Visual Embeddings with Multimodal LLM,” ICLR 2026، [صفحهٔ رسمی ICLR](https://www.iclr.cc/virtual/2026/poster/10009925)، [arXiv:2509.21990](https://arxiv.org/abs/2509.21990)، [پروژهٔ رسمی](https://github.com/TCL606/WAVE). مراجعه: ۵ نوامبر ۲۰۲۶.
15. Koo et al., “Multimodal Self-Attention Network with Temporal Alignment for Audio-Visual Emotion Recognition,” پذیرفته‌شده در ICASSP 2026، [arXiv:2603.11095](https://arxiv.org/abs/2603.11095). مراجعه: ۵ نوامبر ۲۰۲۶.
16. Ogata & Nakashima, “Virtual Encoders in Multimodal Transformers,” نسخهٔ ۱۹ اکتبر ۲۰۲۶؛ مقالهٔ کارگاهی ACCV 2026، [arXiv:2609.26513](https://arxiv.org/abs/2609.26513). مراجعه: ۵ نوامبر ۲۰۲۶.

ادعاهای تجربی در متن به وظیفه، checkpoint، benchmark و شرایط گزارش‌شده در همان منبع محدودند. «آخرین تحولات» به معنی پوشش کامل همهٔ آثار تا آن تاریخ نیست.

## ۲۰. پیوست: کد کامل پروژه

فایل زیر همان کدی است که در پروژه آزموده می‌شود؛ برای اجرا و آزمون به‌روزرسانی‌های منبع را در `projects/39-multimodal-transformer/` ببینید.

```python
"""Tiny CPU-friendly encoders for image, text, and audio alignment.

This pedagogical model demonstrates patch/token encoders, a shared embedding
space, symmetric contrastive learning, and text-query cross-attention to visual
and audio context. It uses random weights and synthetic features: it is not a
pretrained model, dataset, benchmark, or production multimodal assistant.
"""
from __future__ import annotations

import math

import torch
import torch.nn.functional as F
from torch import Tensor, nn


def _positive_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


def _masked_mean(tokens: Tensor, padding_mask: Tensor | None = None) -> Tensor:
    """Mean-pool [B,T,D], ignoring positions where a bool mask is True."""
    if padding_mask is None:
        return tokens.mean(dim=1)
    weights = (~padding_mask).unsqueeze(-1).to(tokens.dtype)
    return (tokens * weights).sum(dim=1) / weights.sum(dim=1).clamp_min(1.0)


def _transformer(d_model: int, num_heads: int, depth: int) -> nn.TransformerEncoder:
    layer = nn.TransformerEncoderLayer(
        d_model=d_model,
        nhead=num_heads,
        dim_feedforward=4 * d_model,
        dropout=0.0,
        activation="gelu",
        batch_first=True,
        norm_first=True,
    )
    return nn.TransformerEncoder(layer, num_layers=depth, enable_nested_tensor=False)


class VisionPatchEncoder(nn.Module):
    """Patchify a fixed-size batch of images and encode the patch sequence."""

    def __init__(
        self,
        d_model: int,
        num_heads: int,
        *,
        patch_size: int = 8,
        image_channels: int = 3,
        max_patches: int = 256,
        depth: int = 1,
    ) -> None:
        super().__init__()
        _positive_int(d_model, "d_model")
        _positive_int(num_heads, "num_heads")
        _positive_int(patch_size, "patch_size")
        _positive_int(image_channels, "image_channels")
        _positive_int(max_patches, "max_patches")
        _positive_int(depth, "depth")
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        self.image_channels = image_channels
        self.patch_size = patch_size
        self.max_patches = max_patches
        self.patch_projection = nn.Conv2d(
            image_channels, d_model, kernel_size=patch_size, stride=patch_size
        )
        self.position = nn.Parameter(torch.zeros(1, max_patches, d_model))
        nn.init.normal_(self.position, std=0.02)
        self.encoder = _transformer(d_model, num_heads, depth)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, images: Tensor) -> Tensor:
        if not isinstance(images, Tensor) or images.ndim != 4:
            raise ValueError("images must have shape [B,C,H,W]")
        if not images.is_floating_point():
            raise ValueError("images must be floating-point tensors")
        batch, channels, height, width = images.shape
        p = self.patch_size
        if batch < 1 or channels != self.image_channels or height < p or width < p:
            raise ValueError("images need a non-empty batch, configured channels, and at least one patch")
        if height % p or width % p:
            raise ValueError("image height and width must be divisible by patch_size")
        patches = self.patch_projection(images).flatten(2).transpose(1, 2)
        if patches.shape[1] > self.max_patches:
            raise ValueError("image produces more patches than max_patches")
        patches = self.encoder(patches + self.position[:, : patches.shape[1]])
        return self.norm(patches)


class TextTokenEncoder(nn.Module):
    """Encode token IDs with a padding-aware bidirectional Transformer."""

    def __init__(
        self,
        vocab_size: int,
        d_model: int,
        num_heads: int,
        *,
        pad_id: int = 0,
        max_length: int = 64,
        depth: int = 1,
    ) -> None:
        super().__init__()
        _positive_int(vocab_size, "vocab_size")
        _positive_int(d_model, "d_model")
        _positive_int(num_heads, "num_heads")
        _positive_int(max_length, "max_length")
        _positive_int(depth, "depth")
        if isinstance(pad_id, bool) or not isinstance(pad_id, int) or not 0 <= pad_id < vocab_size:
            raise ValueError("pad_id must be a token ID in the vocabulary")
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        self.vocab_size = vocab_size
        self.pad_id = pad_id
        self.max_length = max_length
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=pad_id)
        self.position = nn.Embedding(max_length, d_model)
        self.encoder = _transformer(d_model, num_heads, depth)
        self.norm = nn.LayerNorm(d_model)

    def forward(
        self,
        token_ids: Tensor,
        padding_mask: Tensor | None = None,
    ) -> tuple[Tensor, Tensor]:
        if not isinstance(token_ids, Tensor) or token_ids.ndim != 2:
            raise ValueError("token_ids must have shape [B,L]")
        if token_ids.dtype != torch.long:
            raise ValueError("token_ids must use torch.long")
        batch, length = token_ids.shape
        if batch < 1 or length < 1 or length > self.max_length:
            raise ValueError("token batch must be non-empty and no longer than max_length")
        if bool(((token_ids < 0) | (token_ids >= self.vocab_size)).any()):
            raise ValueError("token_ids contain an ID outside the vocabulary")
        if padding_mask is None:
            padding_mask = token_ids.eq(self.pad_id)
        elif (
            not isinstance(padding_mask, Tensor)
            or padding_mask.dtype != torch.bool
            or tuple(padding_mask.shape) != tuple(token_ids.shape)
            or padding_mask.device != token_ids.device
        ):
            raise ValueError("padding_mask must be bool [B,L] on the token device; True means padding")
        if bool(padding_mask.all(dim=1).any()):
            raise ValueError("each text row must contain at least one unmasked token")
        positions = torch.arange(length, device=token_ids.device).unsqueeze(0)
        x = self.embedding(token_ids) + self.position(positions)
        x = self.encoder(x, src_key_padding_mask=padding_mask)
        x = self.norm(x).masked_fill(padding_mask.unsqueeze(-1), 0.0)
        return x, padding_mask


class AudioFrameEncoder(nn.Module):
    """Encode log-Mel-like [B,n_mels,T] features in fixed-size frame groups."""

    def __init__(
        self,
        n_mels: int,
        d_model: int,
        num_heads: int,
        *,
        frame_stride: int = 4,
        max_audio_tokens: int = 256,
        depth: int = 1,
    ) -> None:
        super().__init__()
        _positive_int(n_mels, "n_mels")
        _positive_int(d_model, "d_model")
        _positive_int(num_heads, "num_heads")
        _positive_int(frame_stride, "frame_stride")
        _positive_int(max_audio_tokens, "max_audio_tokens")
        _positive_int(depth, "depth")
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        self.n_mels = n_mels
        self.frame_stride = frame_stride
        self.max_audio_tokens = max_audio_tokens
        self.frame_projection = nn.Conv1d(
            n_mels, d_model, kernel_size=frame_stride, stride=frame_stride
        )
        self.position = nn.Embedding(max_audio_tokens, d_model)
        self.encoder = _transformer(d_model, num_heads, depth)
        self.norm = nn.LayerNorm(d_model)

    def forward(
        self,
        features: Tensor,
        lengths: Tensor | None = None,
    ) -> tuple[Tensor, Tensor]:
        if not isinstance(features, Tensor) or features.ndim != 3:
            raise ValueError("audio features must have shape [B,n_mels,T]")
        if not features.is_floating_point():
            raise ValueError("audio features must be floating-point tensors")
        batch, n_mels, frames = features.shape
        stride = self.frame_stride
        if batch < 1 or n_mels != self.n_mels or frames < stride:
            raise ValueError("audio features need a non-empty batch, configured n_mels, and enough frames")
        if lengths is None:
            lengths = torch.full((batch,), frames, dtype=torch.long, device=features.device)
        elif (
            not isinstance(lengths, Tensor)
            or lengths.dtype != torch.long
            or tuple(lengths.shape) != (batch,)
            or lengths.device != features.device
        ):
            raise ValueError("lengths must be torch.long [B] on the feature device")
        if bool(((lengths < stride) | (lengths > frames)).any()):
            raise ValueError("each valid audio length must be between frame_stride and T")
        x = self.frame_projection(features).transpose(1, 2)
        if x.shape[1] > self.max_audio_tokens:
            raise ValueError("audio produces more tokens than max_audio_tokens")
        valid_tokens = torch.div(lengths, stride, rounding_mode="floor")
        padding_mask = (
            torch.arange(x.shape[1], device=features.device).unsqueeze(0)
            >= valid_tokens.unsqueeze(1)
        )
        positions = torch.arange(x.shape[1], device=features.device).unsqueeze(0)
        x = self.encoder(x + self.position(positions), src_key_padding_mask=padding_mask)
        x = self.norm(x).masked_fill(padding_mask.unsqueeze(-1), 0.0)
        return x, padding_mask


class TextCrossModalFusion(nn.Module):
    """Let text queries read image and audio token sequences via cross-attention."""

    def __init__(self, d_model: int, num_heads: int) -> None:
        super().__init__()
        _positive_int(d_model, "d_model")
        _positive_int(num_heads, "num_heads")
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        self.image_attention = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.audio_attention = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.norm1 = nn.LayerNorm(d_model)
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Linear(4 * d_model, d_model)
        )
        self.norm2 = nn.LayerNorm(d_model)

    def forward(
        self,
        text_tokens: Tensor,
        image_tokens: Tensor,
        audio_tokens: Tensor,
        text_padding_mask: Tensor,
        audio_padding_mask: Tensor,
    ) -> Tensor:
        image_context, _ = self.image_attention(
            text_tokens, image_tokens, image_tokens, need_weights=False
        )
        audio_context, _ = self.audio_attention(
            text_tokens,
            audio_tokens,
            audio_tokens,
            key_padding_mask=audio_padding_mask,
            need_weights=False,
        )
        fused = self.norm1(text_tokens + image_context + audio_context)
        fused = self.norm2(fused + self.feed_forward(fused))
        return fused.masked_fill(text_padding_mask.unsqueeze(-1), 0.0)


class TinyMultimodalAligner(nn.Module):
    """Three encoders with a shared space plus text-to-image/audio fusion.

    Inputs are normalized image tensors, text token IDs and log-Mel-like audio
    features. The returned shared embeddings suit contrastive retrieval demos;
    ``fused_text_tokens`` illustrates cross-attention but is not a generator.
    """

    def __init__(
        self,
        vocab_size: int = 64,
        *,
        pad_id: int = 0,
        n_mels: int = 16,
        d_model: int = 32,
        embed_dim: int = 16,
        num_heads: int = 4,
        patch_size: int = 8,
        max_image_patches: int = 256,
        max_text_length: int = 64,
        audio_frame_stride: int = 4,
        max_audio_tokens: int = 256,
        depth: int = 1,
    ) -> None:
        super().__init__()
        for name, value in (
            ("vocab_size", vocab_size), ("n_mels", n_mels), ("d_model", d_model),
            ("embed_dim", embed_dim), ("num_heads", num_heads), ("depth", depth),
        ):
            _positive_int(value, name)
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        self.vision = VisionPatchEncoder(
            d_model, num_heads, patch_size=patch_size,
            max_patches=max_image_patches, depth=depth,
        )
        self.text = TextTokenEncoder(
            vocab_size, d_model, num_heads, pad_id=pad_id,
            max_length=max_text_length, depth=depth,
        )
        self.audio = AudioFrameEncoder(
            n_mels, d_model, num_heads, frame_stride=audio_frame_stride,
            max_audio_tokens=max_audio_tokens, depth=depth,
        )
        self.fusion = TextCrossModalFusion(d_model, num_heads)
        self.image_projection = nn.Linear(d_model, embed_dim)
        self.text_projection = nn.Linear(d_model, embed_dim)
        self.audio_projection = nn.Linear(d_model, embed_dim)
        self.fused_projection = nn.Linear(d_model, embed_dim)

    def forward(
        self,
        images: Tensor,
        token_ids: Tensor,
        audio_features: Tensor,
        *,
        text_padding_mask: Tensor | None = None,
        audio_lengths: Tensor | None = None,
    ) -> dict[str, Tensor]:
        if not all(isinstance(value, Tensor) for value in (images, token_ids, audio_features)):
            raise ValueError("all modality inputs must be tensors")
        if images.ndim != 4 or token_ids.ndim != 2 or audio_features.ndim != 3:
            raise ValueError("inputs must be images [B,C,H,W], tokens [B,L], and audio [B,F,T]")
        batch = images.shape[0]
        if token_ids.shape[0] != batch or audio_features.shape[0] != batch or batch < 1:
            raise ValueError("image, text, and audio batches must have the same non-zero size")
        if images.device != token_ids.device or images.device != audio_features.device:
            raise ValueError("all modalities must be on the same device")

        image_tokens = self.vision(images)
        text_tokens, text_mask = self.text(token_ids, text_padding_mask)
        audio_tokens, audio_mask = self.audio(audio_features, audio_lengths)
        image_pooled = image_tokens.mean(dim=1)
        text_pooled = _masked_mean(text_tokens, text_mask)
        audio_pooled = _masked_mean(audio_tokens, audio_mask)
        fused_text_tokens = self.fusion(
            text_tokens, image_tokens, audio_tokens, text_mask, audio_mask
        )
        fused_text_pooled = _masked_mean(fused_text_tokens, text_mask)

        return {
            "image_tokens": image_tokens,
            "text_tokens": text_tokens,
            "audio_tokens": audio_tokens,
            "audio_padding_mask": audio_mask,
            "text_padding_mask": text_mask,
            "fused_text_tokens": fused_text_tokens,
            "image_embedding": F.normalize(self.image_projection(image_pooled), dim=-1),
            "text_embedding": F.normalize(self.text_projection(text_pooled), dim=-1),
            "audio_embedding": F.normalize(self.audio_projection(audio_pooled), dim=-1),
            "fused_embedding": F.normalize(self.fused_projection(fused_text_pooled), dim=-1),
        }


def symmetric_info_nce(
    first: Tensor,
    second: Tensor,
    *,
    logit_scale: float = 10.0,
) -> Tensor:
    """Symmetric in-batch InfoNCE for aligned [B,D] pairs, with B >= 2.

    The diagonal entries are the positive pairs; other entries are negatives
    for this batch. ``logit_scale`` is a positive multiplier, not log(scale).
    """
    if not isinstance(first, Tensor) or not isinstance(second, Tensor):
        raise ValueError("first and second must be tensors")
    if first.ndim != 2 or second.ndim != 2 or first.shape != second.shape:
        raise ValueError("embeddings must share the same [B,D] shape")
    if first.shape[0] < 2 or first.shape[1] < 1:
        raise ValueError("InfoNCE needs at least two paired examples and one feature")
    if not first.is_floating_point() or not second.is_floating_point():
        raise ValueError("embeddings must be floating point")
    if first.device != second.device or first.dtype != second.dtype:
        raise ValueError("embeddings must share device and dtype")
    if (
        isinstance(logit_scale, bool)
        or not isinstance(logit_scale, (int, float))
        or not math.isfinite(logit_scale)
        or logit_scale <= 0
    ):
        raise ValueError("logit_scale must be a finite positive number")
    a = F.normalize(first, dim=-1)
    b = F.normalize(second, dim=-1)
    logits = logit_scale * (a @ b.transpose(0, 1))
    labels = torch.arange(first.shape[0], device=first.device)
    return (F.cross_entropy(logits, labels) + F.cross_entropy(logits.T, labels)) / 2


def three_way_contrastive_loss(
    image_embeddings: Tensor,
    text_embeddings: Tensor,
    audio_embeddings: Tensor,
    *,
    logit_scale: float = 10.0,
) -> Tensor:
    """Average symmetric image-text, image-audio and text-audio objectives."""
    return (
        symmetric_info_nce(image_embeddings, text_embeddings, logit_scale=logit_scale)
        + symmetric_info_nce(image_embeddings, audio_embeddings, logit_scale=logit_scale)
        + symmetric_info_nce(text_embeddings, audio_embeddings, logit_scale=logit_scale)
    ) / 3.0


def demo() -> None:
    torch.manual_seed(39)
    model = TinyMultimodalAligner(d_model=32, embed_dim=16, num_heads=4)
    images = torch.rand(4, 3, 32, 32)
    token_ids = torch.tensor([
        [1, 7, 8, 0, 0, 0],
        [1, 9, 10, 11, 0, 0],
        [1, 12, 13, 0, 0, 0],
        [1, 14, 15, 16, 17, 0],
    ], dtype=torch.long)
    audio = torch.randn(4, 16, 64)  # synthetic log-Mel-like features, not waveforms
    audio_lengths = torch.tensor([64, 56, 48, 40], dtype=torch.long)
    output = model(images, token_ids, audio, audio_lengths=audio_lengths)
    loss = three_way_contrastive_loss(
        output["image_embedding"], output["text_embedding"], output["audio_embedding"]
    )
    loss.backward()
    print(f"shared embeddings: {tuple(output['image_embedding'].shape)} per modality")
    print(f"fused text tokens: {tuple(output['fused_text_tokens'].shape)}")
    print(f"synthetic three-way InfoNCE: {loss.item():.4f}")
    print(f"finite loss and gradients: {bool(torch.isfinite(loss)) and model.vision.patch_projection.weight.grad is not None}")


if __name__ == "__main__":
    demo()
```
