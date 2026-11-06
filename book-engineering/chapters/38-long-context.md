# جلد سوم، فصل ۶ — پنجرهٔ متن، KV Cache، GQA، توجه پراکنده و MoE

**The Art & Science of Building Intelligence | Babak & Ai | فصل سراسری ۳۸ از نقشهٔ پنج‌جلدی**

**تاریخ بازبینی منابع: ۵ نوامبر ۲۰۲۶؛ منابع پژوهشی این فصل در همین تاریخ بازبینی شدند.**

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

**متن جایگزین فرمول:** تعداد جفت‌های مجاز در توجه علّی برابر تی ضرب در تی به‌علاوه یک تقسیم بر دو است؛ مرتبهٔ هزینهٔ attention برابر تی به توان دو ضرب در دی است.

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

**متن جایگزین فرمول:** بایت حافظهٔ کی وی برابر دو ضرب در لایه‌ها، batch، طول دنباله، تعداد کی وی سرها، بُعد هر سر و بایت هر مقدار است.

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

**متن جایگزین فرمول:** در جی کیو ای تعداد Query head برابر تعداد KV head ضرب در اندازهٔ گروه است؛ نسبت حافظهٔ cache به نسبت تعداد KV head وابسته است.

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

**متن جایگزین فرمول:** برای attention محلی به‌علاوه global، جفت‌های توجه تقریبی از مرتبهٔ تی ضرب در پنجره به‌علاوه تی ضرب در تعداد توکن‌های سراسری‌اند؛ در dense مرتبه تی به توان دو است.

این مرتبه فقط شمار جفت‌ها را تقریب می‌زند؛ توکن global، یال‌های تصادفی، طول پنجره، padding، تعداد لایه‌ها و kernel واقعی را باید در محاسبه گنجاند. اگر هر لایه فقط همسایه‌ها را ببیند، اطلاعات دور ممکن است طی چند لایه منتقل شود، اما این با یک دسترسی مستقیم به هر نقطه برابر نیست. توجه sparseِ دقیق روی الگوی مجاز، نسبت به **همان الگو** دقیق است؛ نسبت به denseِ کامل ممکن است اطلاعاتی را حذف کند. ماسکی که فقط روی ماتریس dense اعمال شود، از دید ریاضی sparsity نشان می‌دهد، اما اگر kernel محاسبهٔ خانه‌های بسته را واقعاً skip نکند، صرفاً با افزودن ماسک صرفه‌جویی سرعتی تضمین نمی‌شود.

## ۹. FlashAttention دقیق است؛ Sparse Attention نیست

**FlashAttention** با tiling و محاسبهٔ نرم‌ماکس به‌صورت مرحله‌ای، attention متراکمِ استاندارد را بدون materialize کردن ماتریس کامل امتیازها محاسبه می‌کند و رفت‌وآمد بین حافظهٔ سریع GPU و HBM را کاهش می‌دهد [۱]. در بیان الگوریتمی، خروجی attention دقیقِ همان رابطهٔ dense است (با اختلاف‌های معمول ممیز شناور)؛ اما شمار ضرب‌های اصلی همچنان مرتبهٔ `O(T²d)` است. **FlashAttention-2** نحوهٔ تقسیم کار و موازی‌سازی را تغییر داد و در پیکربندی‌های مقالهٔ خودش بهبودهایی گزارش کرد [۲].

پس دو محور جدا داریم: «چه جفت‌هایی را می‌خواهیم؟» و «آن جفت‌ها را چطور با کمترین I/O و حافظه اجرا کنیم؟» FlashAttention عمدتاً محور دوم است و به‌تنهایی توجه را پراکنده نمی‌کند؛ Sparse Attention محور اول را هم عوض می‌کند. نسخه‌های block-sparse یا kernelهای تخصصی می‌توانند این ایده‌ها را ترکیب کنند. این ترکیب برای سود واقعی باید روی GPU/نسخهٔ هدف benchmark شود؛ داشتن نام FlashAttention یا mask محلی در کد ساده، نتیجهٔ سرعت را ثابت نمی‌کند.

## ۱۰. Mixture of Experts: انتخاب مسیر محاسبه برای هر توکن

در یک لایهٔ **Mixture of Experts (MoE)**، به‌جای یک شبکهٔ پیش‌خور مشترک، چند expert (اغلب شبکه‌های FFN) و یک **router** داریم. Router برای بازنمایی هر توکن امتیاز می‌سازد، سپس یک یا چند expert را برمی‌گزیند. در یک MoE top-`k` ساده:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="خروجی لایهٔ MoE برابر مجموع خروجی expertهای انتخاب‌شده است که با وزن router ترکیب می‌شوند؛ مجموعهٔ انتخاب‌شده top k expert است"><mrow><mi>p</mi><mo>(</mo><mi>i</mi><mo>|</mo><mi>x</mi><mo>)</mo><mo>=</mo><mi>softmax</mi><mo>(</mo><msub><mi>W</mi><mi>r</mi></msub><mi>x</mi><mo>)</mo><mo>,</mo><mspace width="0.7em"/><mi>y</mi><mo>=</mo><munder><mo>∑</mo><mrow><mi>i</mi><mo>∈</mo><msub><mi>S</mi><mi>k</mi></msub></mrow></munder><msub><mi>g</mi><mi>i</mi></msub><mo>(</mo><mi>x</mi><mo>)</mo><msub><mi>E</mi><mi>i</mi></msub><mo>(</mo><mi>x</mi><mo>)</mo></mrow></math>

**متن جایگزین فرمول:** خروجی لایهٔ MoE برابر مجموع خروجی expertهای انتخاب‌شده است که با وزن router ترکیب می‌شوند؛ مجموعهٔ انتخاب‌شده top k expert است.

ایدهٔ **فعال‌سازی تنک** این است که برای هر توکن فقط بخشی از expertها اجرا شوند؛ در نتیجه ممکن است ظرفیت کل پارامترها از محاسبهٔ فعال هر توکن بزرگ‌تر باشد. این با Sparse Attention فرق دارد: MoE مسیر FFN را انتخاب می‌کند و به‌تنهایی attention یا KV Cache را کوچک نمی‌کند. اگر وزن همهٔ expertها روی چند GPU shard شده باشد، حافظهٔ وزن کل سامانه همچنان باید نگه‌داری/دسترسی شود؛ expert parallelism هم ارتباط شبکه‌ای و all-to-all اضافه می‌کند. عدد «پارامتر فعال» را معادل وزن کل لازم در VRAM نگیرید.

نمونهٔ موردی: گزارش DeepSeek-V3 مدلی با ۶۷۱ میلیارد پارامتر کل و ۳۷ میلیارد پارامتر فعال برای هر توکن را توصیف می‌کند؛ همان گزارش از DeepSeekMoE و Multi-head Latent Attention نیز استفاده می‌کند [۱۰]. این اعداد مشخصات گزارش همان مدل‌اند و به معنی «مدل ۳۷B است» یا تضمین latency/کیفیت برای هر کاربر نیستند. همچنین expertها الزاماً «متخصص انسان‌نام‌گذاری‌شده» نیستند؛ specialization در یک مدل خاص باید با تحلیل و آزمایش بررسی شود.

## ۱۱. Router، توازن بار و هزینهٔ ارتباطی

اگر تقریباً همهٔ توکن‌ها به یک expert بروند، expertهای دیگر کم‌استفاده می‌شوند و همان expertِ پرترافیک bottleneck می‌شود. در routing top-1ِ Switch، `fᵢ` سهم توکن‌هایی است که واقعاً به expert شمارهٔ `i` فرستاده شده‌اند و `Pᵢ` میانگین احتمال router برای همان expert است. یکی از lossهای سادهٔ توازن بار چنین است [۹]:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="در فرمول Switch، زیان کمکی برابر آلفا ضرب در تعداد expertها ضرب در مجموع سهم واقعی توکن‌های هر expert در میانگین احتمال router همان expert است"><mrow><msub><mi>ℒ</mi><mi>aux</mi></msub><mo>=</mo><mi>α</mi><mo>·</mo><mi>E</mi><mo>·</mo><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>E</mi></munderover><msub><mi>f</mi><mi>i</mi></msub><msub><mi>P</mi><mi>i</mi></msub></mrow></math>

**متن جایگزین فرمول:** در فرمول Switch، زیان کمکی برابر آلفا ضرب در تعداد expertها ضرب در مجموع سهم واقعی توکن‌های هر expert در میانگین احتمال router همان expert است.

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

### واژه‌نامهٔ کوتاه

- **پنجرهٔ زمینه (context window):** حداکثر دنباله‌ای که یک فراخوانی مدل پردازش می‌کند.
- **KV Cache:** نگه‌داری Key و Value پیشین برای پرهیز از محاسبهٔ دوباره هنگام تولید.
- **GQA:** اشتراک گروهی Key/Value میان چند Query head.
- **Sparse Attention:** محاسبهٔ توجه روی بخشی از جفت‌موقعیت‌ها، نه همهٔ آن‌ها.
- **MoE:** انتخاب تعدادی expert از میان چند شبکهٔ feed-forward در هر مسیر.

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
