# فصل ۶۱: سرو و بهینه‌سازی استنتاج

فصل محلی ۱۵ از ۱۵ جلد چهارم؛ فصل سراسری ۶۱

این فصل موتورهای اجرای مدل، قالب‌های خروجی، زمان‌بندی درخواست‌ها و ارزیابی کارایی استنتاج را بررسی می‌کند. هدف انتخاب بر اساس مدل، سخت‌افزار، workload و شواهد است؛ نه معرفی یک «بهترین» runtime.

## ۱. جایگاه فصل و مرز موضوعی

پس از فصل ۵۸، که آماده‌سازی مدل و قرارداد tokenizer را می‌سازد، فصل ۵۹ سخت‌افزار، driver، backend و موازی‌سازی را بررسی می‌کند و فصل ۶۰ منشأ اجرا، قفل محیط و ثبت سنجه را پی می‌گیرد. این فصل در لایهٔ بعد قرار می‌گیرد: وزن و قالب به کدام runtime می‌رسد، runtime درخواست‌ها و KV cache را چگونه زمان‌بندی می‌کند، و تغییر را با چه سنجه‌ای می‌سنجیم؟

دامنهٔ ما موتور/runtime است؛ نه طراحی محصول یا API، احراز هویت، محدودیت نرخ، معماری وب، فرایند استقرار سازمانی و پاسخ به رخداد. آن موضوع‌ها در بخش «تبدیل مدل به محصول» نقشهٔ مجموعه، فصل‌های ۶۶ تا ۶۹، جای می‌گیرند. فصل ۶۱ نیز جای فصل ۵۴ را نمی‌گیرد: برآورد جامع وزن، FLOPs و هزینه در آن فصل است؛ اینجا فقط KV cache را به‌عنوان محدودیت زندهٔ runtime محاسبه می‌کنیم.

![شکل ۴-۱۵-۱: وزن، پیکربندی و tokenizer از مسیر قالب یا بستهٔ خروجی به runtime می‌روند؛ زمان‌بند prefill و decode، batch و KV cache را مدیریت می‌کند و trace سنجه‌های تأخیر، throughput، خطا، حافظه و ارزیابی کیفیت را ثبت می‌کند. انتخاب قالب به پشتیبانی مدل و سخت‌افزار وابسته است؛ پیکان‌ها و شکل‌ها رابطهٔ فرایند را نشان می‌دهند، نه سازگاری همگانی، بهبود تضمینی یا benchmark واقعی.](book-engineering/diagrams/v4-ch15-inference-serving.svg)

## ۲. Runtime با محصول یکی نیست

Runtime وزن‌ها را بار می‌کند، عملگرها را اجرا می‌کند، صف و حافظهٔ موقت را مدیریت می‌کند و خروجی توکن‌ها را می‌سازد. «سرو» در این فصل یعنی اجرای چند درخواست مدل زیر یک زمان‌بند و مشاهدهٔ رفتار همان موتور. این بحث با ساخت API مشتری‌محور، مدیریت حساب کاربر یا طراحی frontend متفاوت است.

مرزها را در گزارش هم نگه دارید: قابلیت runtime یک واقعیت نسخه‌مند است؛ پشتیبانی از یک مدل، GPU و dtype را برای release دقیق بررسی کنید. کارایی یک اندازه‌گیری وابسته به workload است. کیفیت خروجی یک ارزیابی جداست. وجود یک endpoint، مثال مستندات یا موفقیت در بارگذاری مدل هیچ‌یک به‌تنهایی این سه ادعا را ثابت نمی‌کند.

## ۳. مسیر درخواست از مدل تا خروجی

پیش از مقایسه، زنجیرهٔ واقعی را ترسیم کنید: artifact مدل و پیکربندی، tokenizer و الگوی گفت‌وگو، تبدیل یا export، backend اجرا، صف پذیرش، prefill متن ورودی، ساخت KV cache، decode توکن‌به‌توکن و پایان پاسخ. هر مرحله هم محل شکست است و هم منشأ تأخیر.

اگر tokenizer یا template عوض شده باشد، ورودی توکنی دیگری به مدل می‌رسد؛ بنابراین مقایسهٔ «همان prompt» الزاماً مقایسهٔ «همان توکن‌ها» نیست. شناسهٔ مدل و revision، hash وزن‌ها، tokenizer/template، نسخهٔ runtime، تنظیمات precision، نسخهٔ driver و runtime شتاب‌دهنده، دستگاه، محدودیت طول، پیکربندی صف و fixture درخواست را کنار هر trace ثبت کنید. زنجیرهٔ منشأ فصل ۶۰ برای همین پیوندها مفید است.

## ۴. سنجه‌هایی که رفتار runtime را آشکار می‌کنند

| سنجه | تعریف عملی | پرسشی که پاسخ می‌دهد |
|---|---|---|
| TTFT | زمان ورود درخواست تا نخستین خروجی متنی/توکنی | صف و prefill چه‌قدر منتظر می‌گذارند؟ |
| ITL | فاصلهٔ زمانی میان خروجی‌های متوالی در جریان decode | خروجی برای کاربر چقدر پیوسته است؟ |
| TPOT | میانگین زمان پاسخ به هر توکن خروجی پس از نخستین توکن | هزینهٔ decode در این بار چقدر است؟ |
| End-to-end | ورود تا پایان خروجی | کل درخواست در این اندازه‌گیری چه‌قدر طول کشید؟ |
| Request/s | درخواست موفق تقسیم بر پنجرهٔ اندازه‌گیری | ظرفیت درخواست با همین توزیع طول چقدر است؟ |
| Prompt/output tokens/s | توکن‌های ورودی و خروجی تقسیم بر پنجره | کار prefill و decode را جداگانه می‌سنجیم؟ |
| Queue/KV metrics | انتظار صف، درخواست‌های در حال اجرا و مصرف/اشغال cache | گلوگاه از admission یا حافظه است؟ |

برای درخواست با بیش از یک توکن خروجی، برآورد TPOT را می‌توان به‌شکل زیر نوشت:

<math xmlns="http://www.w3.org/1998/Math/MathML" aria-label="TPOT برابر است با زمان پایان منهای زمان نخستین خروجی، تقسیم بر تعداد توکن‌های خروجی منهای یک">
  <mrow><mi>TPOT</mi><mo>=</mo><mfrac><mrow><msub><mi>t</mi><mi>finish</mi></msub><mo>−</mo><msub><mi>t</mi><mi>first</mi></msub></mrow><mrow><msub><mi>N</mi><mi>out</mi></msub><mo>−</mo><mn>1</mn></mrow></mfrac></mrow>
</math>

**متن جایگزین فرمول:** TPOT برابر است با زمان پایان منهای زمان نخستین خروجی، تقسیم بر تعداد توکن‌های خروجی منهای یک؛ این برآورد برای بیش از یک توکن تعریف می‌شود.

در benchmark، میانگین به‌تنهایی کافی نیست؛ p50/p95/p99، نرخ خطا و توزیع طول ورودی/خروجی را نیز ببینید. ITL دقیق به timestamp توکن نیاز دارد؛ timestamp یک chunk شبکه که ممکن است چند توکن را یک‌جا حمل کند، اندازه‌گیری دقیق ITL نیست. سنجهٔ سرویس داخلی و زمان‌سنجی مشتری را جدا نام‌گذاری کنید.

## ۵. پیش از انتخاب نام ابزار، ماتریس سازگاری بسازید

| گزینه | نقش غالب | قالب یا مسیر معمول | مرز تصمیم |
|---|---|---|---|
| vLLM | runtime سرو LLM با زمان‌بندی و مدیریت KV | وزن/معماری پشتیبانی‌شده در release جاری | پشتیبانی مدل، GPU، dtype و kernel را در نسخهٔ منتخب بیازمایید. |
| llama.cpp | موتور inference چند backend با پیاده‌سازی C/C++ | اغلب بستهٔ GGUF و کمّی‌سازی متناظر | CPU، offload به GPU و build/backend واقعی را برای دستگاه خود بسنجید. |
| Ollama | تجربهٔ مدیریت مدل و اجرای سرویس محلی/ابری | بسته‌ها و قالب‌های import پشتیبانی‌شدهٔ همان release | لایهٔ راحتی و مدیریت را با موتور پایین‌دستی و کارایی آن یکی نگیرید. |
| ONNX Runtime GenAI | حلقهٔ تولید روی مدل ONNX و Execution Provider | مدل ONNX و پیکربندی generation | عملگر، provider، دستگاه و وضعیت API/version را کنترل کنید. |
| TensorRT-LLM | build و اجرای بهینه‌شده برای GPUهای NVIDIA | engine و pluginهای پشتیبانی‌شدهٔ همان release | ساخت engine، مدل و سخت‌افزار باید با هم سازگار باشند. |

این جدول ranking نیست. ابتدا پرسش «آیا همین مدل و tokenizer روی این build و دستگاه درست اجرا می‌شود؟» را پاسخ دهید؛ سپس کیفیت، کارایی، حافظه، محدودیت مجوز و هزینهٔ نگهداری را در workload خود مقایسه کنید. یک نام نرم‌افزار، جای ماتریس پشتیبانی نسخه را نمی‌گیرد.

## ۶. vLLM: زمان‌بندی و حافظهٔ چند درخواست

vLLM یک runtime سرو است که مدیریت بلوکی KV cache، batch پیوسته و ابزار مشاهده‌پذیری را در مستندات خود توضیح می‌دهد. در PagedAttention، فضای KV به block تقسیم می‌شود و الزاماً در قطعات فیزیکی پیوسته قرار نمی‌گیرد؛ allocation برحسب نیاز می‌تواند اتلاف ناشی از تکه‌تکه‌شدن را کم کند. مقالهٔ اولیه در workloadهای خودش افزایش ۲ تا ۴ برابری throughput را در latency مشابه گزارش می‌کند؛ آن عدد تضمین یک GPU، مدل یا ورودی دیگر نیست.

Automatic Prefix Caching می‌تواند blockهای KV مربوط به پیشوند مشترک را دوباره به‌کار گیرد. مستند طراحی، block را با محتوای خودش و پیشوند قبلی شناسایی می‌کند؛ وقتی درخواست‌ها واقعاً prefix مشترک دارند، prefill تکراری ممکن است کم شود. hit rate به توکن‌های دقیق، طول و مرز block، عمر cache و eviction وابسته است. prefix cache حافظهٔ وضعیت محاسبه است، نه cache پاسخ نهایی.

مستندات metrics سنجه‌هایی برای TTFT، ITL/TPOT، صف، prefill، KV cache و درخواست‌های فعال/منتظر معرفی می‌کنند؛ CLI `vllm bench serve` نیز ابزار benchmark دارد. نام و schema سنجه‌ها و flagها را در مستندات همان نسخه بخوانید؛ مدل/دستگاه پشتیبانی‌شده را از روی مثال benchmark تعمیم ندهید.

## ۷. llama.cpp: اجرای چندسکویی و GGUF

`llama.cpp` یک runtime C/C++ است که buildهای متناسب با backendهای سخت‌افزاری دارد و ابزار server و quantization را عرضه می‌کند. GGUF قالب بسته‌بندی مدل برای اکوسیستم `ggml` است؛ گردش‌کار معمول می‌تواند تبدیل وزن‌های منبع به GGUF و سپس ساخت نسخهٔ کمّی‌شده باشد. دقت عددی، شکل quantization، backend و مسیر offload روی رفتار واقعی اثر می‌گذارند.

«روی CPU اجرا شد» یا «در منوی quantization وجود دارد» دربارهٔ سرعت یا کیفیت چیزی را تضمین نمی‌کند. تبدیل را روی یک نسخهٔ ثابت انجام دهید، hash خروجی را نگه دارید و مدل کمّی را در همان سنجهٔ کیفیت و workload پیش/پس از تغییر بسنجید. server در مخزن رسمی چنددرخواستی و endpointهای سازگار با قالب‌های رایج را فهرست می‌کند؛ جزئیات پروتکل این فصل موضوع اصلی نیست.

## ۸. Ollama: تجربهٔ اجرا و چرخهٔ مدل

Ollama دسترسی و مدیریت مدل و اجرای محلی را ساده می‌کند و مستندات کنونی آن مسیرهای محلی و cloud را پوشش می‌دهد. این سطح برای آزمایش و اجرای محلی مفید است، اما مقایسهٔ runtime را خودکار نمی‌کند: بستهٔ مدل، نسخه، backend، GPU، تعداد درخواست هم‌زمان و تنظیمات cache همچنان باید ثبت شوند.

برای یک benchmark قابل‌تفسیر، بنویسید مدل از کجا آمده، چه قالبی اجرا شده، آیا backend شتاب‌دهنده واقعاً فعال بوده و خروجی چگونه timestamp یا شمارش شده است. یک فرمان کوتاه که «مدل را اجرا کرد» مدرک throughput، پایداری یا معادل‌بودن خروجی با build دیگری نیست.

## ۹. ONNX Runtime GenAI: گراف و Execution Provider

ONNX یک قالب تبادل گراف محاسبات است؛ ONNX Runtime GenAI لایهٔ generation را کنار آن قرار می‌دهد، از جمله tokenizer و تنظیم generation و مدیریت KV cache در مسیر مستندشده. اجرای واقعی به operatorهای مدل، شکل‌های پویا، provider، دستگاه و build وابسته است. Export موفق به ONNX مساوی با اجرای سریع یا حتی اجرای کامل در provider مقصد نیست.

مستندات GenAI در تاریخ بازبینی این فصل API را preview معرفی می‌کردند. بنابراین نسخهٔ بسته، تغییرات API، provider پشتیبانی‌شده و مسیر تبدیل مدل را pin و آزمون کنید؛ از مثال preview نتیجهٔ تضمین سازگاری نسخه‌های آینده نگیرید. مدل‌هایی که custom op دارند یا پیکربندی‌شان در مسیر export پشتیبانی نشده، نیازمند بررسی جدا هستند.

## ۱۰. TensorRT-LLM: engine build و وابستگی سخت‌افزاری

TensorRT-LLM ابزارها و runtimeهای inference برای GPUهای NVIDIA را ارائه می‌کند. مستندات آن قابلیت‌هایی مانند quantization، in-flight batching، chunked context، استفادهٔ مجدد از KV cache و speculative sampling را نسخه‌مند فهرست می‌کنند. بسته به مسیر، لازم است engine با مدل، precision، plugin و دستگاه سازگار ساخته شود؛ artifact به‌دست‌آمده را یک فایل عمومی و قابل‌انتقال میان هر GPU و نسخه فرض نکنید.

این انتخاب وقتی معنا پیدا می‌کند که سود احتمالی بهینه‌سازی از هزینهٔ build، نگهداری نسخه، تغییر سخت‌افزار، پوشش مدل و debugging بیشتر باشد. در هر گزارش، نسخهٔ TensorRT-LLM/CUDA/driver، مدل و digest engine را نگه دارید و release notes را برای همان ترکیب بررسی کنید. فصل ۵۹ مبانی backend و device را پوشش می‌دهد؛ اینجا نتیجهٔ GPU واقعی ادعا نمی‌شود.

## ۱۱. Export و قالب: چه چیزی واقعاً قابل‌انتقال است؟

| Artifact | چه چیزی را نگه می‌دارد؟ | پرسش انتقال |
|---|---|---|
| فایل وزن مانند Safetensors | آرایه‌های وزن؛ نه لزوماً runtime یا graph کامل | آیا معماری و config در runtime مقصد پیاده‌سازی شده‌اند؟ |
| GGUF | ساختار و وزن‌ها با metadata مورد استفادهٔ اکوسیستم مرتبط | آیا نوع quantization، tokenizer و backend موردنیاز در build هست؟ |
| ONNX | گراف و tensorهای مدل در قالب تبادل | آیا عملگرها، dynamic shape و provider مقصد را پشتیبانی می‌کنند؟ |
| engine کامپایل‌شده | برنامهٔ runtime بهینه‌شده برای مسیر build مشخص | برای کدام نسخه، GPU، plugin و precision ساخته شده است؟ |

Tokenizer، special token، chat template، generation config و فایل مجوز ممکن است در artifact واحد جمع نشده باشند. قبل از export manifest بسازید: فایل‌ها و hash، revision کامل منبع، ابزار و نسخهٔ تبدیل، config، tokenizer، dtype، calibration data مجاز، دستگاه مقصد و آزمون صحت. اگر خروجی خام تغییر کرد، rollback باید به artifact شناسه‌دار قبلی بازگردد.

## ۱۲. Quantization: وزن، activation و KV یک متغیر نیستند

کمّی‌سازی وزن، دقت نمایش وزن‌ها را عوض می‌کند؛ کمّی‌سازی KV cache نمایش وضعیت K/V را؛ و mixed precision/activation مسیر محاسبه را. این‌ها اثرهای یکسان ندارند. کوچک‌ترشدن فایل وزن به‌تنهایی مصرف KV، workspace یا زمان اجرا را اندازه نمی‌گیرد. حتی اگر تعداد بایت کمتر شود، سرعت به kernel، پشتیبانی dtype، bandwidth، batch و شکل لایه‌ها وابسته است.

کیفیت را با ارزیابی ثابت و مرتبط با کاربرد بسنجید: نسخهٔ مدل و tokenizer، prompt، decoding، نمونهٔ جدا و معیار ازپیش‌تعریف‌شده را نگه دارید. برای زبان‌های مختلف، طول context و خروجی‌های حساس به عدد/نام خاص، یک average کلی می‌تواند افت موضعی را پنهان کند. اگر quantization نیاز به calibration دارد، منشأ، مجوز و split آن داده را ثبت کنید؛ آن را با test set مخلوط نکنید.

## ۱۳. KV cache: محدودیت زندهٔ طول و هم‌زمانی

در یک decoder با توجه کامل، اگر هر لایه برای هر token یک بردار K و V نگه دارد، تخمین payload ساده چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" aria-label="بایت‌های KV برابر است با دو ضرب‌در تعداد لایه‌ها، تعداد سرهای KV، بُعد سر، بایت هر عنصر، تعداد توکن‌ها و تعداد دنباله‌های هم‌زمان">
  <mrow><msub><mi>M</mi><mi>KV</mi></msub><mo>=</mo><mn>2</mn><mo>×</mo><mi>L</mi><mo>×</mo><msub><mi>H</mi><mi>KV</mi></msub><mo>×</mo><msub><mi>d</mi><mi>head</mi></msub><mo>×</mo><mi>b</mi><mo>×</mo><mi>T</mi><mo>×</mo><mi>S</mi></mrow>
</math>

**متن جایگزین فرمول:** بایت‌های KV برابر است با دو ضرب‌در تعداد لایه‌ها، تعداد سرهای KV، بُعد هر سر، بایت هر عنصر، تعداد tokenهای نگه‌داری‌شده و تعداد دنباله‌های هم‌زمان.

مثال فرضی: ۳۲ لایه، ۸ سر KV، بُعد ۱۲۸ و دو بایت برای هر عنصر، به ازای هر token برابر ۱۳۱٬۰۷۲ بایت می‌دهد. با طول ۴٬۰۹۶، payload یک دنباله ۵۳۶٬۸۷۰٬۹۱۲ بایت یا ۰٫۵ GiB است؛ برای ۸ دنبالهٔ هم‌زمان، ۴ GiB می‌شود. این حاصل fixture فرضی است، نه نیاز یا اندازه‌گیری دستگاه.

فرمول ساده، allocator، blockها، fragmentation، workspace، وزن مدل، activation و معماری‌هایی با sliding window یا cache غیرمعمول را پوشش نمی‌دهد. `H_KV` را با تعداد سرهای query اشتباه نگیرید. برای ظرفیت دستگاه، workload کامل و حاشیهٔ ایمنی، به فصل ۵۴ برگردید و اجرای واقعی را اندازه بگیرید.

## ۱۴. Batching و صف: throughput در برابر زمان انتظار

در static batching، گروهی ثابت از درخواست‌ها با هم جلو می‌روند و دنبالهٔ کوتاه ممکن است تا پایان دنبالهٔ بلند منتظر بماند. continuous/in-flight batching اجازه می‌دهد درخواست جدید پس از آزادشدن slot وارد شود. این سیاست می‌تواند استفاده از GPU را بالا ببرد، اما نتیجه به توزیع طول، prefill/decode، اندازهٔ batch، fairness و حد حافظه وابسته است؛ زمان‌بندی تهاجمی هم ممکن است صف یا tail latency را بدتر کند.

حد فعال‌بودن هم‌زمان را فقط با «چند درخواست می‌رسد؟» تعیین نکنید. طول context، توکن خروجی، KV cache، حافظهٔ وزن‌ها و فضای موقت را لحاظ کنید. prefill طولانی می‌تواند decode درخواست‌های موجود را عقب بیندازد؛ chunked prefill بعضی زمان‌بندها را منصفانه‌تر می‌کند، اما باید در نسخه و workload انتخابی آزموده شود.

## ۱۵. Prefix cache: reuse محاسبه، نه متن پاسخ

اگر دو prompt prefix توکنی یکسان داشته باشند، cache ممکن است K/V محاسبه‌شده برای آن قسمت را دوباره استفاده کند و prefill تکراری را کم کند. این سود وقتی وجود دارد که prefix واقعاً مشترک، هنوز resident و قابل‌اشتراک در همان دامنهٔ مدل/adapter و سیاست cache باشد. تفاوت کوچک در tokenization، قالب، اطلاعات dynamic یا مرز block می‌تواند hit را از بین ببرد.

Hit rate را کنار TTFT، مصرف cache و eviction بخوانید. در یک آزمون cold، warm و mixed را جدا کنید؛ مقایسهٔ warm-cache یک runtime با cold-cache دیگری نامنصفانه است. reuse وضعیت داخلی مدل با پاسخ ذخیره‌شده یکی نیست و سازوکار نگهداری پاسخ محصولی هم موضوع این فصل نیست.

## ۱۶. Speculative decoding: پیشنهاد و وارسی

روش speculative decoding از یک draft برای پیشنهاد چند token استفاده می‌کند و مدل هدف آن‌ها را وارسی می‌کند. اگر پذیرش کافی باشد، می‌توان بخشی از decode را با کار کمتر جلو برد؛ اگر draft ضعیف یا وارسی پرهزینه باشد، overhead سود را می‌خورد. اندازهٔ پیشنهاد، نسبت پذیرش، batch و نسبت اندازهٔ draft به target با workload تغییر می‌کنند.

الگوریتم‌های پذیرش/اصلاح دقیق می‌توانند توزیع خروجی مدل هدف را حفظ کنند؛ این ویژگی را به هر پیاده‌سازی با نام speculative تعمیم ندهید. مقالهٔ اولیه نتیجهٔ ۲ تا ۳ برابری را برای آزمایش‌های خودش با T5-XXL/T5X گزارش می‌کند، نه برای هر مدل و GPU. اجرای خود را با مدل، seed/decoding، کیفیت، TTFT، TPOT و throughput پیش/پس از تغییر بسنجید.

## ۱۷. قاعدهٔ بهینه‌سازی: یک متغیر، یک فرضیه، یک rollback

بهینه‌سازی را از سنجهٔ بد آغاز کنید، نه از feature list. TTFT بالا با TPOT خوب می‌تواند به صف یا prefill اشاره کند؛ TPOT بالا با TTFT قابل‌قبول می‌تواند decode یا bandwidth را مطرح کند؛ OOM با درخواست بلند شاید از KV یا workspace باشد. این نشانه‌ها فرضیه‌اند، نه تشخیص قطعی؛ سنجهٔ داخلی runtime، حافظهٔ واقعی و trace را بررسی کنید.

سپس یک تغییر قابل‌بازگشت انتخاب کنید: precision وزن، precision KV، سقف batch، prefix cache، chunked prefill یا speculative decoding. نسخهٔ baseline، کیفیت و خطای آن را ثبت کنید؛ یک گزینه را عوض کنید؛ warm-up و workload ثابت را اجرا کنید؛ نتیجه را در چند بار اندازه‌گیری مقایسه کنید؛ در صورت افت کیفیت یا نقض SLO برگردید. تغییر هم‌زمان runtime، export، quant و scheduler علت را غیرقابل‌تشخیص می‌کند.

## ۱۸. پروتکل benchmark پیش و پس از تغییر

1. مدل، tokenizer، template، revision/hash، runtime/build، driver، GPU، dtype، flags و fixture را ثبت کنید.
2. ورودی/خروجی را در چند bucket طولی بسازید؛ warm-up را از پنجرهٔ سنجش جدا کنید و cold/warm cache را مشخص کنید.
3. نرخ ورود و concurrency را تعریف کنید. بار بسته‌بسته (closed-loop) و بار با نرخ ثابت (open-loop) پدیده‌های صف متفاوتی دارند؛ اگر فقط یکی را اجرا می‌کنید، همان را بنویسید.
4. حداقل TTFT، end-to-end، TPOT یا ITL معتبر، request/s، prompt/output tokens/s، p50/p95/p99، خطا/timeout، peak memory و cache hit/eviction را ثبت کنید.
5. خروجی‌ها را با پروتکل کیفیت مستقل مقایسه کنید. سنجش latency بدون کیفیت ممکن است «سریع‌تر» اما نامعتبر باشد؛ سنجش کیفیت بدون ثابت‌بودن نسخه و prompt نیز مقایسه‌پذیر نیست.
6. تکرارها و تعداد درخواست کافی برای workload هدف داشته باشید. p95 یک fixture شش‌درخواستی، برآورد دقیق tail سازمانی نیست؛ عدم‌قطعیت و تفاوت بین اجرای cold/warm را پنهان نکنید.

نسخهٔ benchmark CLI خود runtime را به‌کار ببرید و schema خروجی را نگه دارید؛ نام flagها و سنجه‌ها نسخه‌مندند. مقایسهٔ throughput فقط با طول خروجی، نرخ ورود، concurrency، سخت‌افزار و تعریف پنجرهٔ یکسان معنا پیدا می‌کند.

## ۱۹. پروژهٔ فصل: تحلیل trace و محاسبهٔ payload KV

پروژهٔ استانداردکتابی `inference_lab.py` ورودی نرمال‌شده را اعتبارسنجی می‌کند، TTFT و end-to-end را می‌سازد، TPOT را از زمان‌های trace برآورد می‌کند و نرخ درخواست/توکن و نرخ خطا را حساب می‌کند. تابع دوم، payload dense KV را بر اساس فرض‌های آشکار برآورد می‌کند. پروژه به runtime وصل نمی‌شود و دو run داخل `sample_trace.json` عمداً ساختگی‌اند.

از پوشهٔ پروژه اجرا کنید:

```bash
python -m unittest -v
python inference_lab.py --fixture sample_trace.json --output /tmp/ch61-analysis.json
```

Trace نرمال‌شده باید timestampهای ورود، نخستین خروجی و پایان، شمار توکن‌های prompt/completion، status و پنجرهٔ اندازه‌گیری را داشته باشد. اگر ابزار اصلی timestamp توکن یا شمار توکن را در اختیار نمی‌گذارد، از تعداد chunkهای شبکه آن‌ها را حدس نزنید؛ محدودیت را در نتیجه ثبت کنید. ساخت fixture واقعی، تبدیل خودکار schema، warm-up، load generation و اتصال به vLLM یا runtime دیگر خارج از این تمرین است.

## ۲۰. خواندن خروجی fixture بدون ادعای کارایی

روی fixture ثابت با hash `e53d085e8386c0c8d8dcb9b8b0c7ab9508bfef8d3f72341ea6c5f58bb9ffaf7c`، هر برچسب پیکربندی ۵ درخواست موفق از ۶ تلاش داشت. هر دو پنجره ۲ ثانیه‌ای‌اند و بنابراین ۲٫۵ درخواست موفق بر ثانیه و ۲۳۴ توکن خروجی بر ثانیه برای هر دو محاسبه می‌شود. p95 TTFT در fixture برچسب `illustrative-static` برابر ۳۵۰ ms و در برچسب `illustrative-candidate` برابر ۲۰۰ ms است؛ p95 end-to-end آن‌ها ۱٬۰۸۰ و ۸۲۰ ms است.

این اختلاف در فایل JSON ساخته شده است؛ runtimeی اجرا نشده تا batching پیوسته را تأیید کند. مصرف محاسبه‌شدهٔ KV نیز همان ۴ GiB فرضی برای ۸ × ۴٬۰۹۶ token است و به دستگاه/مدل واقعی تعلق ندارد. `results.json` و `environment.json` این مرز را حفظ می‌کنند؛ بخش گزارش ممیزی نیز محدودیت آزمون را جداگانه ثبت می‌کند.

## ۲۱. عیب‌یابی و خط مرز عملیاتی

| نشانه | نخست چه چیزی را جدا کنید؟ | گام بعد |
|---|---|---|
| TTFT بالا، TPOT مناسب | queue delay، طول prompt، prefill و warm/cold cache | سنجهٔ queue و prefill را از trace درخواست جدا کنید. |
| TTFT مناسب، TPOT بالا | decode، اندازهٔ batch، bandwidth و precision | workload خروجی و پشتیبانی kernel/device را ثابت نگه دارید. |
| OOM با هم‌زمانی یا context بلند | KV cache، workspace، وزن‌ها و fragmentation | سقف context/concurrency را با دادهٔ واقعی اندازه بگیرید؛ فقط وزن را کمّی نکنید. |
| export اجرا نمی‌شود | op، dtype، shape، tokenizer و provider | نخست یک ورودی ثابت و نسخهٔ دقیق export/runtime را بررسی کنید. |
| throughput بهتر اما کیفیت بدتر | وزن/KV quant، decoding یا تفاوت artifact | baseline کیفی، نمونهٔ جدا و rollback را اجرا کنید. |
| warm-cache نتیجهٔ ناپایدار می‌دهد | hit، eviction، prefix دقیق و cache state | warm-up و cache policy را ثبت و cold/warm را جدا گزارش کنید. |

برای هر تغییر، artifact و config شناسه‌دار و مسیر بازگشت داشته باشید. اما API عمومی، احراز هویت، rate limiting، ثبت رخداد سازمانی، حریم خصوصی محصول و استقرار cloud/on-prem را اینجا طراحی نمی‌کنیم؛ فصل‌های ۶۶ تا ۶۹ مرز محصول و عملیات را ادامه می‌دهند. هزینهٔ دستگاه یا ابر را نیز به فصل ۵۶ ارجاع دهید.

## ۲۲. تمرین‌ها

۱. تیمی یک checkpoint موجود و دو گزینهٔ runtime، vLLM روی GPU سازمانی و llama.cpp در build فعلی، دارد. ماتریس مدل/قالب/دستگاه و آزمون صحتی پیشنهاد دهید که پیش از benchmark انجام می‌دهید.

۲. در trace فرضی، TTFT p95 زیاد است ولی TPOT p95 تغییر نکرده. سه علت محتمل و سه سنجه یا برش workload برای تمایز آن‌ها بنویسید.

۳. کمّی‌سازی وزن، حافظهٔ فایل را کم کرده اما چند گروه ارزیابی کیفیت افت کرده‌اند. پروتکل تصمیم rollback/پذیرش و داده‌هایی را که باید جدا نگه دارید شرح دهید.

۴. با ۳۲ لایه، ۸ سر KV، بُعد ۱۲۸، دو بایت برای هر عنصر، ۴٬۰۹۶ token و ۸ دنباله، payload ایده‌آل KV را محاسبه کنید. حداقل چهار مؤلفهٔ خارج از این حساب را نام ببرید.

۵. prefix-cache hit پایین است. چه تفاوت‌هایی در prompt، tokenization، block، adapter یا عمر cache را بررسی می‌کنید، و چرا این نتیجه به‌تنهایی ثابت نمی‌کند prefix caching بی‌فایده است؟

۶. speculative decoding در یک مجموعهٔ prompt سریع‌تر و در مجموعه‌ای دیگر کندتر شده است. نقش پذیرش draft، طول پیشنهاد، هزینهٔ وارسی، batch و کیفیت را در یک آزمایش جداشدنی توضیح دهید.

۷. benchmark پیش/پس از تغییر runtime طراحی کنید: workload، warm-up، cache state، نرخ ورود، concurrency، سنجه‌های latency/throughput/memory، ارزیابی کیفیت و محدودیت آماری را مشخص کنید.

## ۲۳. جمع‌بندی و پیوند فصل‌ها

vLLM، llama.cpp، Ollama، ONNX Runtime GenAI و TensorRT-LLM نقش و مرز یکسان ندارند؛ تفاوت قالب، export، backend، GPU و نسخه را پیش از مقایسه ثبت کنید. prefill، decode، batch و KV cache اجزای اصلی رفتار runtime هستند. quantization، prefix cache و speculative decoding اهرم‌های وابسته به workload‌اند، نه وعدهٔ speedup.

فصل ۵۴ محاسبهٔ جامع منابع را می‌دهد؛ فصل ۵۸ قرارداد tokenizer و مدل را؛ فصل ۵۹ دستگاه و backend را؛ و فصل ۶۰ ثبت منشأ و اجرای قابل‌ردیابی را. فصل‌های ۶۶ تا ۶۹ در بخش محصول، API، عملیات و استقرار را ادامه خواهند داد. تمرین‌ها پاسخ یگانه ندارند؛ [پاسخ‌نامهٔ مستقل فصل ۶۱](book-engineering/answers/61-inference-serving-fa.md) فرض‌ها و مرز شواهد را شرح می‌دهد. [پروژه](book-engineering/projects/61-inference-serving/README.md) و [گزارش ممیزی](book-engineering/chapters/61-audit-report-fa.md) همراه فصل‌اند.

این فصل و جلد در وب/PWA و Markdown منتشر می‌شوند؛ PDF و EPUB در این کار تولید و آزموده نشده‌اند.

## ۲۴. منابع و تاریخ بازبینی

تاریخ بازبینی منابع: ۷ نوامبر ۲۰۲۶. صفحات زنده و پشتیبانی runtimeها تغییر می‌کنند؛ قبل از استفاده، نسخه و سخت‌افزار خود را با release notes و ماتریس رسمی همان پروژه تطبیق دهید.

1. vLLM, [Automatic Prefix Caching](https://docs.vllm.ai/en/latest/design/automatic_prefix_caching.html)؛ سازوکار blockهای KV و پیشوند مشترک.
2. vLLM, [Production Metrics](https://docs.vllm.ai/en/latest/usage/metrics/) و [Benchmark CLI](https://docs.vllm.ai/en/latest/benchmarking/cli/)؛ سنجه‌ها و ابزارهای نسخه‌مند.
3. Kwon et al., [Efficient Memory Management for Large Language Model Serving with PagedAttention](https://arxiv.org/abs/2309.06180), 2023؛ اعداد مقاله محدود به workloadهای ارزیابی همان پژوهش‌اند.
4. llama.cpp, [HTTP Server README](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) و [Quantization README](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md)؛ سرور و گردش‌کار GGUF/quantization.
5. Ollama, [API Introduction](https://docs.ollama.com/api/introduction)؛ دامنهٔ مستندات اجرای محلی و cloud.
6. ONNX Runtime, [GenAI documentation](https://onnxruntime.ai/docs/genai/) و [Configuration reference](https://onnxruntime.ai/docs/genai/reference/config.html)؛ اجزای generation و وضعیت API در زمان بازبینی.
7. NVIDIA, [TensorRT-LLM Key Features](https://nvidia.github.io/TensorRT-LLM/key-features.html) و [Release Notes](https://nvidia.github.io/TensorRT-LLM/latest/release-notes.html)؛ قابلیت‌ها و وابستگی به نسخه.
8. Leviathan et al., [Fast Inference from Transformers via Speculative Decoding](https://arxiv.org/abs/2211.17192), 2023؛ وارسی speculative و نتیجهٔ آزمایش‌های خود مقاله.
9. پروژهٔ این فصل: [README](book-engineering/projects/61-inference-serving/README.md)، [trace ساختگی](book-engineering/projects/61-inference-serving/sample_trace.json)، [manifest fixture](book-engineering/projects/61-inference-serving/fixture_manifest.json) و [نتایج/محیط آزموده‌شده](book-engineering/projects/61-inference-serving/results.json).

## ۲۵. پیوست اجرایی: فایل آزموده‌شدهٔ پروژه

کد زیر دقیقاً همان `book-engineering/projects/61-inference-serving/inference_lab.py` است. آزمون‌ها با CPython 3.13.16 و کتابخانهٔ استاندارد اجرا شده‌اند؛ این کد runtime مدل یا GPU را اجرا نمی‌کند.

```python
"""Analyze normalized, per-request inference traces and estimate dense KV-cache bytes.

This tool performs deterministic arithmetic on its input trace. It does not load
or serve a model, connect to an inference engine, or benchmark hardware.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
VALID_STATUSES = {"ok", "error", "timeout"}


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _nonnegative_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def _finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def estimate_kv_cache_bytes(
    *,
    layers: int,
    kv_heads: int,
    head_dim: int,
    bytes_per_element: int,
    tokens: int,
    sequences: int = 1,
) -> int:
    """Estimate dense full-attention K/V payload bytes, excluding runtime overhead."""
    values = {
        "layers": layers,
        "kv_heads": kv_heads,
        "head_dim": head_dim,
        "bytes_per_element": bytes_per_element,
        "tokens": tokens,
        "sequences": sequences,
    }
    for name, value in values.items():
        _positive_int(value, name)
    return 2 * layers * kv_heads * head_dim * bytes_per_element * tokens * sequences


def nearest_rank_percentile(values: list[float], percentile: float) -> float:
    """Return the nearest-rank percentile; this is descriptive, not an interval."""
    if not values:
        raise ValueError("percentile requires at least one value")
    percentile = _finite_number(percentile, "percentile")
    if not 0 <= percentile <= 100:
        raise ValueError("percentile must be between 0 and 100")
    ordered = sorted(_finite_number(value, "sample value") for value in values)
    rank = max(1, math.ceil(percentile * len(ordered) / 100))
    return ordered[rank - 1]


def validate_fixture(fixture: dict[str, Any]) -> None:
    """Validate the small, normalized trace schema used by the project."""
    if not isinstance(fixture, dict):
        raise ValueError("fixture root must be an object")
    if fixture.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if not isinstance(fixture.get("fixture_id"), str) or not fixture["fixture_id"].strip():
        raise ValueError("fixture_id must be a non-empty string")
    if not isinstance(fixture.get("label_source"), str) or not fixture["label_source"].strip():
        raise ValueError("label_source must be a non-empty string")

    profile = fixture.get("kv_profile")
    if not isinstance(profile, dict):
        raise ValueError("kv_profile must be an object")
    for key in ("layers", "kv_heads", "head_dim", "bytes_per_element", "context_tokens", "concurrent_sequences"):
        _positive_int(profile.get(key), f"kv_profile.{key}")

    runs = fixture.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("runs must be a non-empty list")
    run_ids: set[str] = set()
    for run_index, run in enumerate(runs, 1):
        prefix = f"runs[{run_index}]"
        if not isinstance(run, dict):
            raise ValueError(f"{prefix} must be an object")
        run_id = run.get("run_id")
        if not isinstance(run_id, str) or not run_id.strip() or run_id in run_ids:
            raise ValueError(f"{prefix}.run_id must be unique and non-empty")
        run_ids.add(run_id)
        if not isinstance(run.get("runtime"), str) or not run["runtime"].strip():
            raise ValueError(f"{prefix}.runtime must be a non-empty string")
        if not isinstance(run.get("configuration"), dict):
            raise ValueError(f"{prefix}.configuration must be an object")
        window_ms = _finite_number(run.get("window_ms"), f"{prefix}.window_ms")
        if window_ms <= 0:
            raise ValueError(f"{prefix}.window_ms must be positive")
        requests = run.get("requests")
        if not isinstance(requests, list) or not requests:
            raise ValueError(f"{prefix}.requests must be a non-empty list")

        request_ids: set[str] = set()
        for request_index, request in enumerate(requests, 1):
            request_prefix = f"{prefix}.requests[{request_index}]"
            if not isinstance(request, dict):
                raise ValueError(f"{request_prefix} must be an object")
            request_id = request.get("request_id")
            if not isinstance(request_id, str) or not request_id.strip() or request_id in request_ids:
                raise ValueError(f"{request_prefix}.request_id must be unique and non-empty")
            request_ids.add(request_id)
            status = request.get("status")
            if not isinstance(status, str) or status not in VALID_STATUSES:
                raise ValueError(f"{request_prefix}.status must be one of {sorted(VALID_STATUSES)}")
            arrival_ms = _finite_number(request.get("arrival_ms"), f"{request_prefix}.arrival_ms")
            finish_ms = _finite_number(request.get("finish_ms"), f"{request_prefix}.finish_ms")
            prompt_tokens = _nonnegative_int(request.get("prompt_tokens"), f"{request_prefix}.prompt_tokens")
            if not 0 <= arrival_ms <= finish_ms <= window_ms:
                raise ValueError(f"{request_prefix} timestamps must satisfy 0 <= arrival <= finish <= window")

            first_output_ms = request.get("first_output_ms")
            completion_tokens = request.get("completion_tokens")
            if status == "ok":
                first_output_ms = _finite_number(first_output_ms, f"{request_prefix}.first_output_ms")
                completion_tokens = _positive_int(completion_tokens, f"{request_prefix}.completion_tokens")
                if not arrival_ms <= first_output_ms <= finish_ms:
                    raise ValueError(f"{request_prefix} timestamps must satisfy arrival <= first output <= finish")
            else:
                if first_output_ms is not None:
                    first_output_ms = _finite_number(first_output_ms, f"{request_prefix}.first_output_ms")
                    if not arrival_ms <= first_output_ms <= finish_ms:
                        raise ValueError(f"{request_prefix}.first_output_ms must be null or within the request")
                if completion_tokens is not None:
                    _nonnegative_int(completion_tokens, f"{request_prefix}.completion_tokens")


def _metric_summary(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "p50_ms": None, "p95_ms": None}
    return {
        "count": len(values),
        "p50_ms": nearest_rank_percentile(values, 50),
        "p95_ms": nearest_rank_percentile(values, 95),
    }


def summarize_run(run: dict[str, Any]) -> dict[str, Any]:
    """Summarize one validated run; latency percentiles include successful requests only."""
    requests = run["requests"]
    successful = [request for request in requests if request["status"] == "ok"]
    failed = len(requests) - len(successful)
    ttft_ms = [request["first_output_ms"] - request["arrival_ms"] for request in successful]
    e2e_ms = [request["finish_ms"] - request["arrival_ms"] for request in successful]
    tpot_ms = [
        (request["finish_ms"] - request["first_output_ms"]) / (request["completion_tokens"] - 1)
        for request in successful
        if request["completion_tokens"] > 1
    ]
    window_s = run["window_ms"] / 1000
    completion_tokens = sum(request["completion_tokens"] for request in successful)
    prompt_tokens = sum(request["prompt_tokens"] for request in successful)
    return {
        "run_id": run["run_id"],
        "runtime": run["runtime"],
        "configuration": run["configuration"],
        "measurement_window_ms": run["window_ms"],
        "requests": {
            "attempted": len(requests),
            "successful": len(successful),
            "failed_or_timed_out": failed,
            "error_rate": failed / len(requests),
            "successful_requests_per_s": len(successful) / window_s,
        },
        "tokens_per_s": {
            "prompt": prompt_tokens / window_s,
            "completion": completion_tokens / window_s,
        },
        "latency": {
            "ttft": _metric_summary(ttft_ms),
            "end_to_end": _metric_summary(e2e_ms),
            "estimated_tpot": _metric_summary(tpot_ms),
        },
        "tpot_definition": "(finish_ms - first_output_ms) / (completion_tokens - 1); client/trace estimate",
        "percentile_method": "nearest rank; descriptive only, not a confidence interval",
    }


def analyze_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    validate_fixture(fixture)
    profile = fixture["kv_profile"]
    per_sequence_bytes = estimate_kv_cache_bytes(
        layers=profile["layers"],
        kv_heads=profile["kv_heads"],
        head_dim=profile["head_dim"],
        bytes_per_element=profile["bytes_per_element"],
        tokens=profile["context_tokens"],
    )
    total_cache_bytes = estimate_kv_cache_bytes(
        layers=profile["layers"],
        kv_heads=profile["kv_heads"],
        head_dim=profile["head_dim"],
        bytes_per_element=profile["bytes_per_element"],
        tokens=profile["context_tokens"],
        sequences=profile["concurrent_sequences"],
    )
    return {
        "schema_version": 1,
        "fixture_id": fixture["fixture_id"],
        "label_source": fixture["label_source"],
        "scope": fixture.get("scope", {}),
        "kv_cache_estimate": {
            "bytes_per_token": estimate_kv_cache_bytes(
                layers=profile["layers"],
                kv_heads=profile["kv_heads"],
                head_dim=profile["head_dim"],
                bytes_per_element=profile["bytes_per_element"],
                tokens=1,
            ),
            "tokens_per_sequence": profile["context_tokens"],
            "concurrent_sequences": profile["concurrent_sequences"],
            "bytes_per_sequence": per_sequence_bytes,
            "bytes_for_concurrency": total_cache_bytes,
            "GiB_for_concurrency": total_cache_bytes / (1024**3),
            "excludes": [
                "model weights and non-KV activations",
                "allocator fragmentation and block metadata",
                "runtime workspaces, graph capture and temporary buffers",
                "sliding-window or architecture-specific cache savings",
            ],
        },
        "runs": [summarize_run(run) for run in fixture["runs"]],
    }


def run(fixture_path: Path) -> dict[str, Any]:
    raw = fixture_path.read_bytes()
    fixture = json.loads(raw)
    result = analyze_fixture(fixture)
    result["fixture_sha256"] = hashlib.sha256(raw).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a normalized inference trace and dense KV-cache estimate")
    parser.add_argument("--fixture", type=Path, default=ROOT / "sample_trace.json")
    parser.add_argument("--output", type=Path, default=Path("-"), help="JSON output path, or - for stdout")
    args = parser.parse_args()
    try:
        result = run(args.fixture)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if str(args.output) == "-":
        print(text, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"Wrote deterministic analysis to {args.output}")


if __name__ == "__main__":
    main()
```
