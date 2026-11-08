# جلد پنجم، فصل ۶ — سرو مدل در سطح محصول، صف، cache پاسخ و توان عملیاتی

**نگاشت:** فصل محلی ۶ جلد پنجم = فصل سراسری ۶۷. **تاریخ بازبینی منابع: ۷ نوامبر ۲۰۲۶.** پیش از نگارش، نقشهٔ هر پنج جلد و ترتیب فصل‌ها دوباره بررسی شد؛ در جلد پنجم فصل ۶۶ ساخت API و قرارداد محصول را می‌سازد، فصل ۶۷ رفتار صف، cache پاسخ و زمان‌بندی سرویس را می‌سنجد، و فصل ۶۸ به احراز هویت، محدودیت نرخ، ثبت رخداد، پایش، حریم خصوصی و پاسخ به رخداد می‌پردازد. فصل ۶۹ استقرار و CI/CD را دنبال می‌کند. در جلد چهارم، فصل ۶۱ از پیش runtimeهای مدل، زمان‌بندی داخلی موتور، KV/prefix cache، batchهای inference و benchmark سطح موتور را پوشش می‌دهد؛ این فصل آن موضوع‌ها را بازنویسی نمی‌کند و در صورت نیاز به همان فصل ارجاع می‌دهد.

**پیش‌نیاز:** قرارداد درخواست/پاسخ فصل ۶۶، آشنایی مقدماتی با احتمال و آزمون نرم‌افزار، و تمایز سنجه‌های runtime در فصل ۶۱. **خروجی:** بتوانید مسیر خدمت‌رسانی را از cache تا صف و worker ترسیم کنید، ظرفیت و تأخیر را با فرض‌های روشن تحلیل کنید، برای microbatch و cache پاسخ معیار بگذارید، و یک trace ساختگی را بدون ادعای benchmark واقعی بازتولید کنید. پروژهٔ همراه شبیه‌ساز CPU با کتابخانهٔ استاندارد است؛ هیچ مدل، GPU، سرویس بیرونی یا دادهٔ کاربر را اجرا یا فراخوانی نمی‌کند.

![شکل ۵-۶-۱ — درخواست وارد cache پاسخ دقیق می‌شود؛ hit مستقیماً پاسخ می‌گیرد و miss به صف FIFO با سقف ۸ درخواست منتظر می‌رود. زمان‌بند حداکثر ۴ درخواست را با پنجرهٔ انتظار حداکثر ۱۲ ms به یک worker فرضی می‌فرستد؛ پاسخ محاسبه‌شده می‌تواند پس از تکمیل در cache محدود ذخیره شود. پیکان و برچسب‌ها مسیرها را نشان می‌دهند، نه رنگ. همهٔ عددها از fixture آموزشی‌اند و کارایی runtime، GPU یا مدل واقعی و تضمین latency را ثابت نمی‌کنند.](../diagrams/v5-ch06-serving-pipeline.svg)

**شکل ۵-۶-۱ —** نمودار مفهومیِ صف محصول و cache پاسخ دقیق؛ hit صف محاسبه را دور می‌زند، درحالی‌که miss با سقف صف و زمان انتظار محدود به worker می‌رسد.

## ۱. جایگاه فصل و مرز موضوعی

فصل ۶۶ می‌پرسید رابط وب یا موبایل چه قراردادی با backend دارد؛ این فصل از همان مرز محصول می‌پرسد: پس از پذیرفته‌شدن یک درخواست معتبر، چه زمانی پاسخ می‌رسد و درخواست‌های هم‌زمان چگونه منابع محدود را تقسیم می‌کنند؟ تمرکز بر رفتار خدمت‌رسانی در سطح محصول است، نه ساخت endpoint، طراحی فرم، انتخاب موتور GPU یا پیاده‌سازی یک runtime.

واژه‌های «صف»، «batch» و «cache» در چند لایه به‌کار می‌روند. در فصل ۶۱، موضوع اصلی زمان‌بندی داخل موتور inference، KV cache و سنجش runtime است. در این فصل، صفِ جلوی worker محصول، microbatch سطح درخواست و cache پاسخ کامل محورند. برای جزئیات PagedAttention، quantization، prefix reuse، مدل‌های vLLM/llama.cpp یا برآورد KV به فصل ۶۱ برگردید؛ آن مفاهیم را با cache پاسخ این فصل یکی نگیرید.

## ۲. سرویس محصول، API و runtime سه سطح مرتبط‌اند

**API** در فصل ۶۶ معنای درخواست و پاسخ را تثبیت می‌کند. **سرویس محصول** درخواست‌های معتبر را می‌پذیرد، ممکن است cache را بررسی کند، صف را مدیریت کند و کار را به worker بدهد. **runtime مدل** وزن‌ها را اجرا می‌کند و prefill/decode را انجام می‌دهد. پاسخ کاربر ممکن است از cache برگردد یا از ترکیب زمان انتظار سرویس، اجرای runtime و انتقال شبکه ساخته شود.

این تفکیک برای یافتن گلوگاه لازم است. اگر زمان انتظار پیش از worker بالا باشد، تعویض kernel یا کوچک‌کردن وزن شاید علت اصلی را برطرف نکند. اگر صف کوتاه باشد اما decode کند، افزایش ظرفیت جلوی صف همان مدل را سریع‌تر نمی‌کند. زمان‌های هر لایه را جدا اندازه بگیرید؛ نام یک محصول یا یک feature به‌تنهایی تشخیص نیست.

## ۳. مسیر درخواست را به رویدادهای قابل‌اندازه‌گیری بشکنید

یک مسیر ساده این نقاط را دارد: ورود درخواست، بررسی cache، انتظار برای batch، آغاز worker، نخستین خروجی، پایان پاسخ و ثبت نتیجه. hit دقیق cache می‌تواند از صف محاسبه عبور نکند؛ miss باید منتظر worker یا نوبت batch بماند. هر نقطه timestamp و معنای خودش را می‌خواهد.

در نمودار، سقف «۸» فقط تعداد درخواست‌های منتظر را نشان می‌دهد و درخواست‌های در حال اجرا را نمی‌شمارد. این قراردادِ شبیه‌ساز است، نه قاعده‌ای برای هر سامانه. در یک پیاده‌سازی واقعی، ظرفیت صف، workerهای فعال، batchهای runtime و صف شبکه ممکن است چند لایه باشند؛ نام‌گذاری را طوری انتخاب کنید که جمع‌کردن سنجه‌های لایه‌های مختلف یک عدد گمراه‌کننده نسازد.

## ۴. معیار پذیرش را پیش از تنظیم بنویسید

«سریع‌تر باشد» یا «بتواند درخواست بیشتری بگیرد» معیار کامل نیست. برای یک مسیر مشخص بنویسید: چه نسبت درخواست‌هایی باید پیش از deadline پاسخ بگیرند؟ آیا حداقل کیفیت یا صحت لازم است؟ پاسخ cache‌شده باید چقدر تازه باشد؟ در فشار بار چه رفتاری پذیرفته است: انتظار، رد سریع یا پاسخ جایگزین؟ هر شرط باید با سنجه و آزمونی مستقل پیوند بخورد.

زمان پاسخِ پایین‌تر کافی نیست اگر پاسخ اشتباه، قدیمی یا ناسازگار با قرارداد باشد. در این فصل «درست‌بودن خروجی مدل» از روی trace ساختگی نتیجه نمی‌شود؛ ارزیابی کیفیت به معیارهای مستقل فصل‌های ۶۲ و ۶۳ وابسته است. پروژه فقط برابری یک رشتهٔ ثابت با مرجع fixture را کنترل می‌کند.

## ۵. بودجهٔ latency را به اجزا تقسیم کنید

برای miss می‌توان یک تجزیهٔ مفهومی نوشت:

<math xmlns="http://www.w3.org/1998/Math/MathML" aria-label="زمان پاسخ یک درخواست cache miss برابر است با زمان انتظار صف به‌علاوهٔ انتظار جمع‌شدن batch، اجرای prefill، تولید decode و انتقال پاسخ؛ این جمع یک مدل مفهومی است و زمان واقعی هر لایه باید جدا اندازه‌گیری شود."><mrow><msub><mi>T</mi><mi>response</mi></msub><mo>=</mo><msub><mi>T</mi><mi>queue</mi></msub><mo>+</mo><msub><mi>T</mi><mi>batch</mi></msub><mo>+</mo><msub><mi>T</mi><mi>prefill</mi></msub><mo>+</mo><msub><mi>T</mi><mi>decode</mi></msub><mo>+</mo><msub><mi>T</mi><mi>transport</mi></msub></mrow></math>

**متن جایگزین فرمول:** زمان پاسخِ یک miss از انتظار صف، انتظار جمع‌شدن batch، اجرای prefill، تولید decode و انتقال تشکیل می‌شود؛ این جمع فقط چارچوبی مفهومی است و برابری یا مستقل‌بودن زمان‌های واقعی را تضمین نمی‌کند.

برای hit، مسیر معمولاً lookup و بازگرداندن پاسخ را دارد و زمان prefill/decode مدل را ندارد؛ اما اتصال، serialization، شبکه و محل cache همچنان می‌توانند تأخیر بسازند. فصل ۶۱، TTFT و فاصلهٔ توکن‌های خروجی را از end-to-end جدا می‌کند. در سطح محصول نیز TTFT را با latency کامل پاسخ و زمان انتظار صف اشتباه نگیرید.

## ۶. latency تنها میانگین نیست

میانگین پایین می‌تواند با tail کند پنهان همراه باشد. p50 میانهٔ تجربه را توصیف می‌کند؛ p95 و p99 نشان می‌دهند بخش کندتر توزیع چه می‌کند. علاوه بر percentile، نرخ خطا، timeout، رد صف و تفکیک درخواست‌های cache-hit از model-miss را گزارش کنید. اگر خروجی streaming است، زمان نخستین token و زمان پایان پاسخ دو پرسش متفاوت‌اند.

Percentile روی ۲۰ درخواست ساختگی فقط خلاصهٔ همان ۲۰ مورد است؛ برآورد قابل‌اتکای tail در یک جمعیت واقعی نیست. برای نتیجهٔ استنباطی، workload نماینده، حجم نمونه و عدم‌قطعیت لازم است؛ طراحی آزمون و تفسیر آماری در فصل ۶۲ بررسی می‌شود.

## ۷. throughput و goodput را جدا تعریف کنید

Throughput می‌تواند تعداد پاسخ‌های کامل‌شده بر ثانیه یا تعداد tokenهای خروجی بر ثانیه باشد. این سنجه‌ها با طول ورودی/خروجی، نسبت hit، نرخ خطا و پنجرهٔ اندازه‌گیری تغییر می‌کنند. «تعداد درخواست بر ثانیه» بدون گفتن شکل workload و مخرج، برای مقایسه کافی نیست.

در برخی سامانه‌ها goodput تعداد پاسخ‌هایی است که معیار پذیرشِ ازپیش‌تعریف‌شده—برای نمونه، صحت قراردادی و deadline—را می‌گذرانند، تقسیم بر زمان؛ تعریف و مخرج را همراه عدد گزارش کنید. در این پروژه، `completed_responses_per_second` نرخ تکمیل است. `fixture_correct_responses_per_second` فقط پاسخ‌های کامل‌شده‌ای را می‌شمارد که رشتهٔ ساختگی‌شان با مرجع برابر است؛ deadline را در شرط پذیرش وارد نمی‌کند. چون پاسخِ مسیر model-miss از خود fixture می‌آید و برابری‌اش در شبیه‌ساز به‌صورت پیش‌فرض درست است، این عدد نه goodput یک محصول واقعی است و نه سنجهٔ کیفیت مدل.

## ۸. قانون Little برای میانگین تعداد درخواست‌ها

در یک سامانهٔ ایستا با میانگین‌های بلندمدت متناهی و مرز اندازه‌گیری سازگار، رابطهٔ Little میان نرخ ورود، زمان ماندن و تعداد متوسط درخواست‌ها چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" aria-label="L برابر lambda ضرب‌در W است؛ L میانگین تعداد درخواست‌ها در کل سامانه، lambda نرخ ورود بر ثانیه و W میانگین زمان ماندن بر حسب ثانیه است. رابطه برای میانگین‌های پایدار است و p95 را محاسبه نمی‌کند."><mrow><mi>L</mi><mo>=</mo><mi>λ</mi><mo>×</mo><mi>W</mi></mrow></math>

**متن جایگزین فرمول:** L میانگین تعداد درخواست‌ها در کل سامانه است، λ نرخ ورود بر ثانیه و W میانگین زمان ماندن بر حسب ثانیه؛ L برابر λ ضرب‌در W است. این رابطه میانگین را می‌دهد، نه p95.

اگر به‌طور فرضی در بلندمدت ۲۰ درخواست در ثانیه برسد و زمان میانگین حضور در کل سامانه ۰٫۲۵ ثانیه باشد، میانگین تعداد درخواست‌های هم‌زمان برابر ۵ است. این عدد مجموع منتظر و در حال سرویس است، نه سقف صف یا تعداد workerها. قانون از یک trace کوتاه به‌تنهایی، burst، p95 یا علت تأخیر را تعیین نمی‌کند؛ شرایط و حدود مقالهٔ Little را رعایت کنید.

## ۹. ورود پایدارِ بالاتر از ظرفیت صف را پر می‌کند

برای یک worker و تعریف سازگار از «واحد کار»، نسبت تقریبی بار چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" aria-label="نسبت بار rho برابر نرخ ورود lambda تقسیم بر ظرفیت خدمت mu است؛ برای یک worker پایدار، ورودی بلندمدت باید از ظرفیت خدمت کمتر باشد. این نسبتِ آموزشی پیک بار، ناهمگنی درخواست‌ها یا محدودیت حافظه را به‌تنهایی مدل نمی‌کند."><mrow><mi>ρ</mi><mo>=</mo><mfrac><mi>λ</mi><mi>μ</mi></mfrac></mrow></math>

**متن جایگزین فرمول:** ρ برابر λ تقسیم بر μ است؛ λ نرخ ورود و μ ظرفیت خدمت در واحدهای سازگارند. برای یک worker پایدار، نرخ ورودی بلندمدت باید از ظرفیت کمتر باشد؛ نسبت به‌تنهایی burst و تفاوت هزینهٔ درخواست‌ها را مدل نمی‌کند.

اگر λ از μ بیشتر بماند، کارِ منتظر در سامانهٔ بدون محدودیت رشد می‌کند؛ بزرگ‌ترکردن صف، توان محاسبه نمی‌سازد. نزدیک‌شدن به اشباع نیز headroom را برای نوسان و درخواست سنگین کم می‌کند. برای درخواست‌های با هزینهٔ متفاوت، واحد «تعداد درخواست» ممکن است کافی نباشد؛ توکن ورودی/خروجی یا زمان محاسبهٔ واقعی را جدا ببینید.

## ۱۰. صف محدود، backpressure و ردِ زودهنگام

صف بدون حد می‌تواند حافظه مصرف کند و زمان انتظار را زیاد کند، بی‌آنکه ظرفیت خدمت را بالا ببرد. صف محدود یک policy صریح می‌خواهد: وقتی پر شد، درخواست تازه را نپذیرید، پاسخ مناسب قرارداد را برگردانید یا بار را به مسیر دیگری هدایت کنید. رد زودهنگام می‌تواند از انتظار طولانیِ بی‌فایده بهتر باشد، اما آستانه باید با workload و هدف محصول سنجیده شود.

در Python، `asyncio.Queue(maxsize=N)` برای `N` مثبت رفتار صفِ محدود را دارد؛ `put()` در صف پُر منتظر می‌ماند و `put_nowait()` می‌تواند `QueueFull` بدهد. نکتهٔ ظریف: `maxsize=0` یعنی صف نامحدود، نه «هیچ‌درخواستی پذیرفته نشود». API و status پاسخ واقعی را طبق قرارداد فصل ۶۶ تعریف کنید؛ rate limit، سهمیه و هویت کاربر فصل ۶۸ هستند، نه این پروژه.

## ۱۱. deadline از انتظارِ بی‌پایان بهتر است

هر درخواست ممکن است deadline کلاینت داشته باشد. اگر زمان باقی‌مانده از زمان تخمینی انتظار و سرویس کمتر باشد، نگه‌داشتن درخواست در صف می‌تواند حافظه و ظرفیت را مصرف کند درحالی‌که کلاینت دیگر پاسخ را نمی‌پذیرد. timeout صف، deadline پاسخ و timeout شبکه سه مفهوم جدا هستند؛ یکی را جای دیگری ننشانید.

سرویس واقعی باید تصمیم بگیرد آیا درخواستِ دیرشده لغو می‌شود، آیا لغو به runtime می‌رسد و آیا کارِ در جریان منابع را آزاد می‌کند. شبیه‌ساز فصل deadline miss را فقط می‌شمارد و cancellation اجرا نمی‌کند. retry کور نیز بار اضافه می‌سازد؛ policy تکرار، بودجهٔ retry و امنیت درخواست در این پروژه پیاده‌سازی نمی‌شوند.

## ۱۲. microbatch زمان را با ظرفیت معامله می‌کند

در microbatch، scheduler تا رسیدن batch به اندازهٔ حداکثر یا گذشتن پنجرهٔ انتظار، درخواست‌های سازگار را جمع می‌کند. انتظار کوتاه ممکن است هزینهٔ ثابت اجرای هر گروه را میان چند درخواست تقسیم کند؛ همان انتظار به latency درخواست نخست اضافه می‌شود. batch بزرگ‌تر هم همیشه بهتر نیست: زمان گام می‌تواند با اندازه بالا برود، خروجی‌های کوتاه در گروه بلند منتظر بمانند و حافظه مصرف شود.

این سیاست سطح درخواست را از continuous/in-flight batching داخل runtime جدا می‌کند. فصل ۶۱ الگوریتم‌های runtime را توضیح می‌دهد؛ پروژهٔ اینجا فقط یک batch ایستا و یک worker فرضی دارد. مدل، revision، تنظیم generation، شکل ورودی و محدودیت منابع باید برای اعضای یک batch سازگار باشند؛ جزئیات هر engine نسخه‌مندند.

## ۱۳. FIFO ساده است، اما همهٔ هزینه‌ها برابر نیستند

FIFO ترتیب ورود را حفظ می‌کند و فهم رفتار را آسان می‌سازد. در workload ناهمگون، یک prompt بلند ممکن است کار کوتاه را عقب بیندازد؛ در batch، خروجی بلند می‌تواند worker را تا پایان نگه دارد. مرتب‌سازی بر اساس تخمین کار شاید tail را برای گروهی کم کند، اما fairness و starvation را بدتر کند.

اول از همه، توزیع طول prompt و completion و هدف latency را اندازه بگیرید. سیاست‌های priority یا انتخاب tenant می‌توانند اثرهای دسترسی و انصاف داشته باشند و در فصل‌های مربوط بررسی می‌شوند. هیچ سیاستی را فقط از روی میانگین throughput انتخاب نکنید؛ p95 و سهم درخواست‌های دیرشده را کنار آن ببینید.

## ۱۴. سه cache را با هم اشتباه نگیرید

| نوع | چه چیزی را بازاستفاده می‌کند؟ | کدام مسئله را پاسخ می‌دهد؟ |
|---|---|---|
| cache پاسخ محصول | بدنهٔ کامل پاسخ برای یک کلید درخواست | آیا همین درخواستِ هم‌ارز پیش‌تر پاسخ داشته است؟ |
| KV/prefix cache موتور | وضعیت میانی K/V برای پیشوند توکنی | آیا بخشی از محاسبهٔ مدل برای prompt مشترک قابل‌بازاستفاده است؟ |
| cache آفلاین/PWA | فایل ثابت کتاب، شکل، پاسخ‌نامه یا کد | آیا asset وب بدون شبکه در دسترس است؟ |

این فصل فقط cache پاسخ محصول را در fixture شبیه‌سازی می‌کند. Prefix/KV cache متن پاسخ را ذخیره نمی‌کند و موضوع فصل ۶۱ است؛ cache آفلاین کتاب نیز به فایل‌های ثابت مربوط است، نه پاسخ تولیدی. وجود یکی از این cacheها به معنی hit در دیگری نیست.

## ۱۵. کلید cache باید تمام عوامل پاسخ را بازتاب دهد

یک کلید نمونه می‌تواند شامل revision مدل، شناسه یا hash prompt دقیق و قالب system prompt، تنظیم decoding، locale، revision شاخص بازیابی و نسخهٔ زمینهٔ ابزار باشد. تغییر مؤثر بر پاسخ باید کلید تازه بسازد یا ورودی قبلی را invalidate کند. کلید ناقص می‌تواند پاسخ مدل یا زبان قبلی را به درخواست تازه نسبت دهد.

RFC 9111 برای cacheهای HTTP از هویت representation، freshness و انتخاب headerها مانند `Vary` حرف می‌زند؛ این مفاهیم برای طراحی مفیدند، اما قرارداد cache پاسخ LLM را خودکار تعریف نمی‌کنند. در خروجی تصادفی، cache می‌تواند با برگرداندن یک پاسخ ثابت، semantics نمونه‌گیری را عوض کند؛ seed و sampling parameters را در policy لحاظ کنید و پیشاپیش تصمیم بگیرید تکرار باید پاسخ قبلی را بدهد یا تولید تازه انجام دهد.

## ۱۶. freshness و invalidation بخشی از correctness هستند

پاسخ cache می‌تواند با عوض‌شدن مدل، template، policy، سند بازیابی یا tool result قدیمی شود. زمان انقضای ثابت برای همهٔ جواب‌ها الزاماً درست نیست؛ برای برخی پاسخ‌ها باید freshness بر اساس منبع یا وضعیت داده تعریف شود، و برای بعضی اصلاً cache پاسخ مناسب نباشد. invalidation باید در release و تغییر محتوا آزموده شود، نه فقط در کد cache.

HTTP cache از freshness و validation طبق headerهای استاندارد پیروی می‌کند؛ cache داخلی پاسخ مدل باید policy محصول خودش را داشته باشد. اگر cache یک پاسخ stale را می‌دهد، آن را با یک hit «درست» گزارش نکنید. این فصل TTL، stale-while-revalidate، دسترسی شخصی یا حذف داده را پیاده‌سازی نمی‌کند؛ حریم خصوصی و مجوزها به فصل ۶۸ مربوط‌اند.

## ۱۷. اندازهٔ cache، eviction و حافظه

یک cache محدود می‌تواند سقف تعداد ورودی، سقف بایت، TTL و policy eviction داشته باشد. LRU هنگام ورود مورد تازه، مورد کم‌استفاده‌تر را بیرون می‌گذارد؛ این انتخاب فقط وقتی مناسب است که الگوی مراجعه با تازگی استفاده هم‌خوانی داشته باشد. اگر یک کلید پرهزینه مدام بیرون می‌رود یا hit rate پایین می‌ماند، افزایش کور ظرفیت لزوماً سودمند نیست.

برای payload متنی می‌توان طول UTF-8 کلید و پاسخ را جمع کرد، ولی این فقط کران payload همان دو رشته است. overhead شیء، hash table، allocator، metadata، هم‌زمانی و حافظهٔ process را نمی‌سنجد. این محاسبه KV cache یا VRAM نیست؛ فصل ۶۱ آن تخمین را جدا توضیح می‌دهد.

## ۱۸. cache، batch و صف با یکدیگر اثر متقابل دارند

Hit پاسخ، اگر policy اجازه دهد، معمولاً worker مدل را مصرف نمی‌کند؛ اما missها هنوز از سقف صف عبور می‌کنند. اگر چند درخواست هم‌کلید پیش از پایان اولین پاسخ برسند، ممکن است همگی miss شوند و محاسبهٔ تکراری بسازند؛ جلوگیری از این وضعیت به سازوکارهایی مانند single-flight نیاز دارد. پروژه عمداً in-flight deduplication را ندارد تا این محدودیت پنهان نشود.

Cache hit می‌تواند میانگین latency را پایین بیاورد و هم‌زمان حافظه یا freshness را بدتر کند. Microbatch می‌تواند batchهای کم‌تعداد یا انتظار اضافه بسازد، به‌ویژه وقتی بخش زیادی از درخواست‌ها hit می‌شوند. بنابراین hit rate، compute work، صف، latency miss و latency hit را جدا گزارش کنید؛ یک سنجهٔ تجمیعی علت تغییر را نشان نمی‌دهد.

## ۱۹. پروتکل پیش/پس از تغییر

- نسخهٔ API، مدل و template، decoding، fixture، سخت‌افزار، runtime و زمان اندازه‌گیری را ثبت کنید؛ اگر runtime/دستگاه را اجرا نمی‌کنید، صریح بنویسید.
- workload را با توزیع prompt/output، burst، concurrency و نسبت تکرار طراحی کنید؛ trace ساختگی را به بار واقعی تعمیم ندهید.
- baseline و candidate را با یک فرض ثابت مقایسه کنید؛ در هر مرحله یک متغیر مانند batch wait، queue cap یا cache را تغییر دهید.
- warm/cold، p50/p95/p99، TTFT، پاسخ کامل، queue depth/wait، cache hit/eviction، رد و deadline miss را جدا بسنجید.
- correctness و کیفیت را مستقل و پیش‌تعریف‌شده ارزیابی کنید؛ تغییر latency به‌تنهایی اجازهٔ افت کیفیت را نمی‌دهد.
- اندازهٔ نمونه، تکرارها، عدم‌قطعیت، بار آزمایش‌شده و محدودیت‌ها را ثبت کنید؛ trace کوتاه پایداری تولیدی را ثابت نمی‌کند.

اگر نرخ ورود یا طول‌ها با اجرا عوض شود، مقایسه قابل‌تفسیر نیست. در workload open-loop، درخواست‌ها طبق زمان‌بندی ورود می‌رسند؛ در load بسته، client بعد از هر پاسخ دوباره می‌فرستد و ازدحام را می‌تواند پنهان کند. نوع بار را گزارش کنید. اجرای واقعی runtime و ابزار benchmark آن به فصل ۶۱ و طراحی آزمون/تحلیل عدم‌قطعیت به فصل ۶۲ مربوط است.

## ۲۰. پروژهٔ فصل: یک trace، چهار policy

پروژه در [پوشهٔ `67-serving-lab`](../projects/67-serving-lab/README.md) است. `serving_lab.py` صف FIFO با سقف، batch wait و اندازهٔ حداکثر، مدل زمان فرضی، cache پاسخ دقیق با LRU و بایت محدود، و شاخص‌های latency/throughput را در زمان گسسته شبیه‌سازی می‌کند. fixture شامل ۱۲ کلید تکراری در دو burst است؛ رشتهٔ پاسخ ثابت از fixture می‌آید، نه از مدل.

از ریشهٔ مخزن اجرا کنید:

```bash
(cd book-engineering/projects/67-serving-lab && python -m unittest -v)
python book-engineering/projects/67-serving-lab/serving_lab.py \
  --fixture book-engineering/projects/67-serving-lab/synthetic_serving_trace.json \
  --output /tmp/ch67-results.json
cmp /tmp/ch67-results.json book-engineering/projects/67-serving-lab/results.json
```

مدل زمانی ساده برای هر batch چنین فرض می‌کند: سربار آغاز ثابت ۵ ms، prefill برابر ۰٫۴ ms ضرب‌در بیشترین prompt در گروه، و زمان هر گام decode برابر ۴ ms به‌علاوهٔ ۰٫۷۵ ms برای هر عضو افزوده. worker تا پایان خروجی طولانی‌ترین درخواست درگیر فرض می‌شود. این ضرایب فقط برای نشان‌دادن اثر سیاست‌ها هستند؛ از آن‌ها سرعت یک GPU، runtime یا محصول واقعی استنتاج نکنید.

## ۲۱. خواندن نتیجهٔ fixture

`results.json` از همان trace چهار run قطعی دارد. baseline صف را تا سقف ۸ پر کرد و ۴ درخواست را رد کرد. microbatch با batch حداکثر ۴ و انتظار ۱۲ ms در این trace ۲۴ پاسخ را کامل کرد؛ exact cacheِ تنها ۱۰ hit داشت، چون بخشی از درخواست‌های burst اول پیش از ذخیرهٔ پاسخ رد شده بودند؛ ترکیب microbatch و cache، ۱۲ miss را محاسبه و ۱۲ تکرار را از cache پاسخ داد.

| سیاست | پاسخ کامل / رد صف | محاسبهٔ ساختگی / hit دقیق | batchهای مدل | p50 / p95 latency پاسخ (ms) | p95 انتظار صف (ms) | deadline miss | پاسخ بر ثانیه در trace |
|---|---:|---:|---:|---:|---:|---:|---:|
| تک‌درخواست، بدون cache | ۲۰ / ۴ | ۲۰ / ۰ | ۲۰ | ۱۷۷٫۰ / ۳۳۳٫۶ | ۳۰۲٫۲ | ۱۰ | ۸٫۴۶۲ |
| microbatch، بدون cache | ۲۴ / ۰ | ۲۴ / ۰ | ۶ | ۱۰۱٫۳ / ۱۷۹٫۵ | ۱۱۴٫۰۵ | ۰ | ۱۰٫۸۷۷ |
| cache دقیق، بدون batch | ۲۲ / ۲ | ۱۲ / ۱۰ | ۱۲ | ۲۸٫۲ / ۳۰۸٫۲ | ۳۰۲٫۲ | ۵ | ۱۰٫۴۲۸ |
| microbatch و cache دقیق | ۲۴ / ۰ | ۱۲ / ۱۲ | ۳ | ۱٫۵ / ۱۷۶٫۲۵ | ۱۱۴٫۰۵ | ۰ | ۱۱٫۷۹۷ |

در این خروجی، p95 انتظار صف و p95 زمان TTFT فقط پاسخ‌های model-miss را می‌گیرند؛ p95 latency پاسخ شامل miss و hit است. نرخ `completed_responses_per_second` تکمیل‌های دیرشده را نیز می‌شمارد. `fixture_correct_responses_per_second` نیز deadline را شرط نمی‌کند؛ در مسیر model-miss، شبیه‌ساز رشتهٔ مرجع را از fixture می‌گیرد، پس تطبیق آن به‌صورت پیش‌فرض برقرار است و آزمون مستقلِ انتقال یا کیفیت نیست. نسبت hit در این fixture به‌تنهایی سود cache در دادهٔ واقعی را نشان نمی‌دهد. بیشینهٔ payload cache ترکیبی ۲٬۴۶۰ بایت است، نه peak حافظهٔ پردازه یا GPU. خروجی مرجع، hash fixture و هر چهار run در [نتایج](../projects/67-serving-lab/results.json) ثبت شده‌اند.

## ۲۲. آنچه fixture ثابت نمی‌کند

۱۷ آزمون واحد، schema، صف محدود، batch، زمان‌بندی ساختگی، کلید، hit پس از تکمیل، LRU و آشکارشدنِ یک پاسخ cacheشدهٔ ناسازگار با مرجع را وارسی می‌کنند. برای پاسخ‌های model-miss، `output_integrity_rate` در شبیه‌ساز از این فرض می‌آید که رشتهٔ مرجع fixture بازگردانده می‌شود؛ پس مقدار ۱٫۰ مشاهدهٔ کیفیت یا آزمون مستقل انتقال نیست. این تعداد، آزمون کیفیت مدل نیست. پروژه هیچ prompt واقعی، endpoint، شبکه، مدل، GPU، runtime، cache توزیع‌شده یا load generator را اجرا نمی‌کند.

زمان throughput از کل پنجرهٔ trace، شامل فاصلهٔ ساختگی بین burstها، حساب شده است. sample کوچک است و فاصلهٔ اطمینان، توزیع تولیدی، چند worker، fairness آماری، مصرف واقعی حافظه، هزینه، امنیت، حریم خصوصی و دسترس‌پذیری را نمی‌سنجد. پاسخ‌های fixture عمداً ثابت‌اند؛ ۱۰۰٪ تطبیق رشته در نتایج فقط صحت مسیر قراردادی همین fixture است، نه امتیاز یک مدل.

## ۲۳. تحولات و اسنادِ بررسی‌شده تا نوامبر ۲۰۲۶

مستندات پایدار CLI رسمی `vLLM` در ۷ نوامبر ۲۰۲۶، گزینهٔ `--max-num-queued-tokens` را برای سقف tokenهای prompt منتظر در prefill توضیح می‌دهند و رد درخواست تازه با HTTP 503 را هنگام رسیدن به حد، به‌عنوان سازوکاری برای هدف TTFT توصیف می‌کنند. این مثال به یک runtime و نسخهٔ مستندات وابسته است؛ آن را به محصول دیگر تعمیم ندهید یا با احراز هویت/محدودیت نرخ محصول یکی نگیرید. راهنمای نسخهٔ دقیق مورد استفاده را پیش از تنظیم بررسی کنید.

در همان تاریخ، RFC 9111 برای HTTP cache استاندارد، freshness و validation را تعریف می‌کرد و مستندات رسمی Python 3.15 رفتار صفِ محدود `asyncio.Queue` را توضیح می‌دادند. استاندارد HTTP، API کتابخانه و مستند runtime سه منبع متفاوت‌اند؛ یک اصطلاح مشابه تضمین رفتار مشترک نمی‌دهد. منابع و تاریخ دسترسی در بخش بعد فهرست شده‌اند.

## ۲۴. عیب‌یابی بر اساس شواهد

| نشانه | ابتدا چه چیزی را جدا کنید؟ | پرسش بعدی |
|---|---|---|
| TTFT بالا و پاسخ نهایی کند | انتظار صف، پنجرهٔ batch، prefill و مسیر انتقال | افزایش تأخیر در کدام timestamp آغاز می‌شود؟ |
| queue depth پیوسته بالا می‌رود | نرخ ورود و خدمت، طول‌ها، cache miss و سقف منابع | آیا ورودی بلندمدت از ظرفیت می‌گذرد، یا burst محدود است؟ |
| hit کم است | کلید، revision، تفاوت prompt، eviction و freshness | آیا درخواست‌ها واقعاً از نظر semantics هم‌ارزند؟ |
| latency متوسط خوب و p95 بد است | صف و طول‌های سنگین، outputهای بلند، batchهای دیر | کدام برش workload دنبالهٔ کند را می‌سازد؟ |
| پاسخ cache قدیمی یا نامربوط است | نسخهٔ مدل، زمینه، locale، sampling و invalidation | کدام بُعد در کلید یا policy جا افتاده است؟ |
| بایت cache کم است ولی process سنگین است | overhead، index، objectها و bufferهای دیگر | آیا payload estimate را با RSS یا VRAM اشتباه گرفته‌اید؟ |

جدول فرضیه می‌سازد، تشخیص قطعی نمی‌دهد. برای رخداد، telemetry، privacy، محدودیت درخواست و پیگیری عملیاتی به فصل ۶۸؛ برای deployment و rollback به فصل ۶۹؛ و برای benchmark موتور به فصل ۶۱ بازگردید.

## ۲۵. منابع و تاریخ بازبینی

منابع زیر در **۷ نوامبر ۲۰۲۶** بازبینی شدند. صفحه‌های مستندات زنده ممکن است بدون نسخهٔ ثابت تغییر کنند؛ نتیجهٔ این فصل فقط به متن و تاریخ بررسی‌شده محدود است.

- [۱] Little, J. D. C.، «A Proof for the Queuing Formula: L = λW»، *Operations Research*، جلد ۹، شمارهٔ ۳، صص. ۳۸۳–۳۸۷، ۱۹۶۱، [DOI: 10.1287/opre.9.3.383](https://doi.org/10.1287/opre.9.3.383). فرض‌های پایداری و میانگین‌های متناهی در تفسیر رابطه اهمیت دارند.
- [۲] Google، *Site Reliability Engineering*، فصل‌های [Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/) و [Handling Overload](https://sre.google/sre-book/handling-overload/)، دربارهٔ اشباع منابع، صف، deadline و load shedding.
- [۳] IETF، [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111)، ژوئن ۲۰۲۲؛ استاندارد cache پیام‌های HTTP، نه policy کامل cache پاسخ مدل.
- [۴] IETF، [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)، ژوئن ۲۰۲۲؛ از جمله semantics پاسخ‌های HTTP.
- [۵] Python Software Foundation، [asyncio — Queues](https://docs.python.org/3/library/asyncio-queue.html)، مستندات Python 3.15.2؛ `maxsize` مثبت صف را محدود می‌کند و صفر به‌معنای نامحدود است.
- [۶] vLLM، [vllm serve CLI reference](https://docs.vllm.ai/en/stable/cli/serve/)، مرجع پایدارِ بررسی‌شده در ۷ نوامبر ۲۰۲۶؛ flagها و معنا وابسته به نسخه‌اند.
- [۷] برای runtime، KV/prefix cache و benchmark به [فصل ۶۱](../chapters/61-inference-serving.md)؛ برای قرارداد API به [فصل ۶۶](66-ai-product-api.md)؛ برای quality و طراحی آزمون به فصل‌های ۶۲–۶۳ رجوع کنید.

## ۲۶. تمرین‌ها

۱. در trace فصل، متوسط ۲۰ درخواست بر ثانیه و متوسط زمان ماندگاری ۰٫۲۵ s است؛ با قانون Little میانگین تعداد درخواست‌های سیستم را محاسبه کنید و بگویید چرا از آن p95 به‌دست نمی‌آید.
۲. در یک worker فرضی نرخ ورود پایدار ۲۴ درخواست بر ثانیه و ظرفیت سنجیده‌شده ۲۰ درخواست بر ثانیه است؛ با ρ=λ/μ چه می‌گویید و چرا بزرگ‌کردن صف مشکل را حل نمی‌کند؟
۳. صف FIFO سقف ۸ منتظر دارد و batch حداکثر ۴ با حداکثر ۱۲ ms انتظار؛ توضیح دهید کدام مورد باعث رد صف می‌شود و کدام باعث TTFT اضافه.
۴. سه نوع cache در فصل‌های ۶۷ و ۶۱ و PWA را از نظر محتوای ذخیره‌شده و رفتار hit مقایسه کنید.
۵. کلید پاسخ شامل `model_revision`، `prompt_id`، `decoding`، `locale` و `context_revision` است. کدام تغییرها باید hit را باطل کنند و چه چیزی این کلید را هنوز برای سامانهٔ چندمستأجری کافی نمی‌کند؟
۶. در fixture، چرا نرخ exact cache-only ده hit است نه دوازده؟ microbatch چه trade-offی اضافه می‌کند؟
۷. نتیجهٔ `output_integrity_rate=1.0` در پروژه چه ادعایی را اجازه می‌دهد و کدام ادعا را اجازه نمی‌دهد؟
۸. پروتکل آزمایش روی runtime واقعی طراحی کنید؛ چه چیزی را ثابت، چه سنجه‌هایی را اندازه می‌گیرید و کدام فصل‌ها را برای کیفیت، امنیت و استقرار به‌کار می‌برید؟

## ۲۷. جمع‌بندی

در سطح محصول، صف محدود، پنجرهٔ batch و cache پاسخ می‌توانند زمان انتظار، رد درخواست، مصرف حافظه و کار محاسباتی را تغییر دهند؛ هیچ‌کدام بدون workload و معیار مستقل تضمین سرعت یا کیفیت نیست. قانون Little دربارهٔ میانگین پایدار است، microbatch latency جمع‌شدن را اضافه می‌کند، و cache فقط هنگامی پاسخ را درست بازمی‌گرداند که کلید، freshness و دامنهٔ استفاده درست طراحی شده باشند.

برای ادامه، [پاسخ‌نامهٔ مستقل فصل ۶۷](../answers/67-model-serving-operations-fa.md)، [README و پروژهٔ قابل‌بازتولید](../projects/67-serving-lab/README.md)، [fixture ساختگی](../projects/67-serving-lab/synthetic_serving_trace.json)، [نتایج](../projects/67-serving-lab/results.json) و [گزارش ممیزی](67-audit-report-fa.md) را ببینید. فصل ۶۶ قرارداد و رابط را می‌سازد؛ فصل ۶۸ کنترل‌های امنیت و پایش محصول را ادامه می‌دهد. محصول این milestone وب/PWA و Markdown است؛ PDF و EPUB تولید یا آزموده نشده‌اند.

## ۲۸. پیوست اجرایی — شبیه‌ساز صف و cache پاسخ

فایل کاملِ آزموده‌شدهٔ `serving_lab.py` در زیر آمده است؛ نسخهٔ اجرایی، آزمون‌ها، trace، environment و خروجی مرجع در [پوشهٔ پروژه](../projects/67-serving-lab/README.md) قرار دارند.

```python
"""Synthetic service-level queue, microbatch, and exact-response-cache simulator.

This module is a deterministic discrete-event teaching model. It does not load
an inference runtime, model, GPU, or network client.
"""
from __future__ import annotations

import argparse
from collections import OrderedDict
import hashlib
import json
import math
from pathlib import Path
from typing import Any

FIXTURE_ID = "v5-ch06-serving-synthetic-v1"
DEFAULT_FIXTURE = Path(__file__).with_name("synthetic_serving_trace.json")

SERVICE_MODEL = {
    "launch_overhead_ms": 5.0,
    "prefill_ms_per_prompt_token": 0.4,
    "decode_step_base_ms": 4.0,
    "decode_step_ms_per_extra_sequence": 0.75,
    "cache_lookup_ms": 1.5,
}

CONFIGURATIONS = [
    {
        "name": "baseline_one_at_a_time",
        "batch_size": 1,
        "batch_wait_ms": 0.0,
        "max_queue_size": 8,
        "cache_enabled": False,
        "max_cache_entries": 0,
        "max_cache_bytes": 0,
    },
    {
        "name": "microbatch_only",
        "batch_size": 4,
        "batch_wait_ms": 12.0,
        "max_queue_size": 8,
        "cache_enabled": False,
        "max_cache_entries": 0,
        "max_cache_bytes": 0,
    },
    {
        "name": "exact_response_cache_only",
        "batch_size": 1,
        "batch_wait_ms": 0.0,
        "max_queue_size": 8,
        "cache_enabled": True,
        "max_cache_entries": 16,
        "max_cache_bytes": 4096,
    },
    {
        "name": "microbatch_plus_exact_cache",
        "batch_size": 4,
        "batch_wait_ms": 12.0,
        "max_queue_size": 8,
        "cache_enabled": True,
        "max_cache_entries": 16,
        "max_cache_bytes": 4096,
    },
]


class FixtureError(ValueError):
    """Raised when the synthetic request trace violates its schema."""


def _finite_number(value: Any, name: str, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    result = float(value)
    if not math.isfinite(result) or result < minimum:
        raise ValueError(f"{name} must be finite and >= {minimum}")
    return result


def _positive_integer(value: Any, name: str, minimum: int = 1) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def response_cache_key(request: dict[str, Any]) -> str:
    """Build an exact fixture key from all response-affecting dimensions.

    ``prompt_id`` stands for the exact, versioned tokenized request in this
    synthetic trace. A real product must define its own safe scope and key.
    """
    required = (
        "model_revision", "prompt_id", "decoding", "locale", "context_revision"
    )
    missing = [field for field in required if field not in request]
    if missing:
        raise ValueError(f"request is missing cache-key fields: {', '.join(missing)}")
    payload = {field: request[field] for field in required}
    try:
        return json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as error:
        raise ValueError("cache-key values must be finite JSON data") from error


def little_average_in_system(arrival_rate_per_second: float, mean_time_seconds: float) -> float:
    """Return L = lambda * W for stable long-run averages."""
    rate = _finite_number(arrival_rate_per_second, "arrival_rate_per_second")
    duration = _finite_number(mean_time_seconds, "mean_time_seconds")
    return rate * duration


def nearest_rank_percentile(values: list[float], percentile: float) -> float | None:
    """Nearest-rank percentile; returns None for an empty sample."""
    if not values:
        return None
    p = _finite_number(percentile, "percentile", 0.0)
    if p > 100.0:
        raise ValueError("percentile must be <= 100")
    ordered = sorted(float(value) for value in values)
    rank = max(1, math.ceil((p / 100.0) * len(ordered)))
    return ordered[rank - 1]


def validate_fixture(fixture: dict[str, Any]) -> None:
    if not isinstance(fixture, dict) or fixture.get("fixture_id") != FIXTURE_ID:
        raise FixtureError(f"fixture_id must equal {FIXTURE_ID!r}")
    if fixture.get("synthetic") is not True:
        raise FixtureError("fixture must be explicitly marked synthetic")
    requests = fixture.get("requests")
    if not isinstance(requests, list) or not requests:
        raise FixtureError("requests must be a nonempty list")
    ids: set[str] = set()
    for index, request in enumerate(requests):
        label = f"requests[{index}]"
        if not isinstance(request, dict):
            raise FixtureError(f"{label} must be an object")
        request_id = request.get("request_id")
        if not isinstance(request_id, str) or not request_id:
            raise FixtureError(f"{label}.request_id must be a nonempty string")
        if request_id in ids:
            raise FixtureError(f"duplicate request_id: {request_id}")
        ids.add(request_id)
        try:
            _finite_number(request.get("arrival_ms"), f"{label}.arrival_ms")
            _positive_integer(request.get("prompt_tokens"), f"{label}.prompt_tokens")
            _positive_integer(request.get("output_tokens"), f"{label}.output_tokens")
            _positive_integer(request.get("deadline_ms"), f"{label}.deadline_ms")
        except ValueError as error:
            raise FixtureError(str(error)) from error
        for field in ("model_revision", "prompt_id", "locale", "context_revision"):
            if not isinstance(request.get(field), str) or not request[field]:
                raise FixtureError(f"{label}.{field} must be a nonempty string")
        if not isinstance(request.get("decoding"), dict):
            raise FixtureError(f"{label}.decoding must be an object")
        if not isinstance(request.get("expected_output"), str) or not request["expected_output"]:
            raise FixtureError(f"{label}.expected_output must be a nonempty string")
        try:
            response_cache_key(request)
        except ValueError as error:
            raise FixtureError(f"{label}: {error}") from error


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(config, dict):
        raise ValueError("config must be an object")
    checked = dict(config)
    if not isinstance(checked.get("name"), str) or not checked["name"]:
        raise ValueError("config.name must be a nonempty string")
    checked["batch_size"] = _positive_integer(checked.get("batch_size"), "batch_size")
    checked["max_queue_size"] = _positive_integer(checked.get("max_queue_size"), "max_queue_size")
    checked["batch_wait_ms"] = _finite_number(checked.get("batch_wait_ms"), "batch_wait_ms")
    cache_enabled = checked.get("cache_enabled")
    if not isinstance(cache_enabled, bool):
        raise ValueError("cache_enabled must be a boolean")
    checked["cache_enabled"] = cache_enabled
    checked["max_cache_entries"] = _positive_integer(
        checked.get("max_cache_entries"), "max_cache_entries", minimum=0
    )
    checked["max_cache_bytes"] = _positive_integer(
        checked.get("max_cache_bytes"), "max_cache_bytes", minimum=0
    )
    service_overrides = checked.get("service_model", {})
    if not isinstance(service_overrides, dict):
        raise ValueError("service_model must be an object")
    service = dict(SERVICE_MODEL)
    service.update(service_overrides)
    for field in (
        "launch_overhead_ms", "prefill_ms_per_prompt_token",
        "decode_step_base_ms", "decode_step_ms_per_extra_sequence", "cache_lookup_ms",
    ):
        service[field] = _finite_number(service[field], f"service_model.{field}")
    checked["service_model"] = service
    if not checked["cache_enabled"]:
        checked["max_cache_entries"] = 0
        checked["max_cache_bytes"] = 0
    return checked


class ResponseCache:
    """Small LRU response cache with explicit entry and UTF-8 payload limits."""

    def __init__(self, max_entries: int, max_bytes: int) -> None:
        self.max_entries = max_entries
        self.max_bytes = max_bytes
        self.entries: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self.payload_bytes = 0
        self.peak_payload_bytes = 0

    def get(self, key: str, now_ms: float) -> str | None:
        entry = self.entries.get(key)
        if entry is None or entry["ready_at_ms"] > now_ms:
            return None
        self.entries.move_to_end(key)
        return entry["response"]

    def store(self, key: str, response: str, ready_at_ms: float) -> bool:
        size = len(key.encode("utf-8")) + len(response.encode("utf-8"))
        if self.max_entries == 0 or self.max_bytes == 0 or size > self.max_bytes:
            return False
        old = self.entries.pop(key, None)
        if old is not None:
            self.payload_bytes -= old["payload_bytes"]
        self.entries[key] = {
            "response": response,
            "ready_at_ms": ready_at_ms,
            "payload_bytes": size,
        }
        self.payload_bytes += size
        self.entries.move_to_end(key)
        while len(self.entries) > self.max_entries or self.payload_bytes > self.max_bytes:
            _, evicted = self.entries.popitem(last=False)
            self.payload_bytes -= evicted["payload_bytes"]
        self.peak_payload_bytes = max(self.peak_payload_bytes, self.payload_bytes)
        return key in self.entries


def _round_ms(value: float | None) -> float | None:
    return None if value is None else round(float(value), 3)


def simulate(fixture: dict[str, Any], raw_config: dict[str, Any]) -> dict[str, Any]:
    """Simulate one FIFO service worker, microbatch wait, and optional exact cache."""
    validate_fixture(fixture)
    config = validate_config(raw_config)
    requests = sorted(
        fixture["requests"], key=lambda request: (request["arrival_ms"], request["request_id"])
    )
    waiting: list[dict[str, Any]] = []
    records: dict[str, dict[str, Any]] = {}
    cache = ResponseCache(config["max_cache_entries"], config["max_cache_bytes"])
    queue_peak = 0
    batch_summaries: list[dict[str, Any]] = []
    next_batch_number = 1
    index = 0
    now_ms = 0.0
    active: dict[str, Any] | None = None
    service = config["service_model"]

    def admit(request: dict[str, Any], arrival_ms: float) -> None:
        nonlocal queue_peak
        key = response_cache_key(request)
        if config["cache_enabled"]:
            cached_response = cache.get(key, arrival_ms)
            if cached_response is not None:
                completion_ms = arrival_ms + service["cache_lookup_ms"]
                latency_ms = completion_ms - arrival_ms
                matches = cached_response == request["expected_output"]
                records[request["request_id"]] = {
                    "request_id": request["request_id"],
                    "arrival_ms": _round_ms(arrival_ms),
                    "status": "cache_hit",
                    "cache_hit": True,
                    "model_compute": False,
                    "batch_id": None,
                    "batch_size": 0,
                    "queue_wait_ms": 0.0,
                    "ttft_ms": _round_ms(latency_ms),
                    "response_latency_ms": _round_ms(latency_ms),
                    "completed_at_ms": _round_ms(completion_ms),
                    "deadline_ms": request["deadline_ms"],
                    "deadline_missed": latency_ms > request["deadline_ms"],
                    "output_matches_reference": matches,
                }
                return

        if len(waiting) >= config["max_queue_size"]:
            records[request["request_id"]] = {
                "request_id": request["request_id"],
                "arrival_ms": _round_ms(arrival_ms),
                "status": "rejected_queue_full",
                "cache_hit": False,
                "model_compute": False,
                "batch_id": None,
                "batch_size": 0,
                "queue_wait_ms": None,
                "ttft_ms": None,
                "response_latency_ms": None,
                "completed_at_ms": None,
                "deadline_ms": request["deadline_ms"],
                "deadline_missed": None,
                "output_matches_reference": None,
            }
            return

        waiting.append(request)
        queue_peak = max(queue_peak, len(waiting))

    def start_batch(batch: list[dict[str, Any]], start_ms: float) -> dict[str, Any]:
        nonlocal next_batch_number
        batch_id = f"batch-{next_batch_number:03d}"
        next_batch_number += 1
        batch_size = len(batch)
        max_prompt_tokens = max(request["prompt_tokens"] for request in batch)
        prefill_ms = (
            service["launch_overhead_ms"]
            + max_prompt_tokens * service["prefill_ms_per_prompt_token"]
        )
        decode_step_ms = (
            service["decode_step_base_ms"]
            + max(0, batch_size - 1) * service["decode_step_ms_per_extra_sequence"]
        )
        events = []
        for request in batch:
            first_token_ms = start_ms + prefill_ms
            completion_ms = first_token_ms + request["output_tokens"] * decode_step_ms
            response_latency_ms = completion_ms - request["arrival_ms"]
            queue_wait_ms = start_ms - request["arrival_ms"]
            records[request["request_id"]] = {
                "request_id": request["request_id"],
                "arrival_ms": _round_ms(request["arrival_ms"]),
                "status": "model_response",
                "cache_hit": False,
                "model_compute": True,
                "batch_id": batch_id,
                "batch_size": batch_size,
                "queue_wait_ms": _round_ms(queue_wait_ms),
                "ttft_ms": _round_ms(first_token_ms - request["arrival_ms"]),
                "response_latency_ms": _round_ms(response_latency_ms),
                "completed_at_ms": _round_ms(completion_ms),
                "deadline_ms": request["deadline_ms"],
                "deadline_missed": response_latency_ms > request["deadline_ms"],
                # The mock computation returns the fixed reference string. This
                # is a transport/integrity check, not a model-quality score.
                "output_matches_reference": True,
            }
            events.append((completion_ms, request["request_id"], request, response_cache_key(request)))
        events.sort(key=lambda event: (event[0], event[1]))
        batch_end = max(event[0] for event in events)
        batch_summaries.append({
            "batch_id": batch_id,
            "batch_size": batch_size,
            "start_ms": _round_ms(start_ms),
            "prefill_assumption_ms": _round_ms(prefill_ms),
            "decode_step_assumption_ms": _round_ms(decode_step_ms),
            "engine_release_ms": _round_ms(batch_end),
        })
        return {"events": events, "next_event": 0, "end_ms": batch_end}

    while index < len(requests) or waiting or active is not None:
        if active is None:
            if not waiting:
                if index >= len(requests):
                    break
                now_ms = max(now_ms, float(requests[index]["arrival_ms"]))
                admit(requests[index], now_ms)
                index += 1
                continue

            first_waiter = waiting[0]
            dispatch_deadline = max(
                now_ms, float(first_waiter["arrival_ms"]) + config["batch_wait_ms"]
            )
            while (
                len(waiting) < config["batch_size"]
                and index < len(requests)
                and float(requests[index]["arrival_ms"]) <= dispatch_deadline
            ):
                now_ms = float(requests[index]["arrival_ms"])
                admit(requests[index], now_ms)
                index += 1

            if len(waiting) >= config["batch_size"]:
                start_ms = now_ms
            else:
                start_ms = dispatch_deadline
                now_ms = start_ms
            take = min(config["batch_size"], len(waiting))
            batch = waiting[:take]
            del waiting[:take]
            active = start_batch(batch, start_ms)
            continue

        completion_index = active["next_event"]
        next_completion_ms = active["events"][completion_index][0]
        next_arrival_ms = (
            float(requests[index]["arrival_ms"]) if index < len(requests) else math.inf
        )
        if next_completion_ms <= next_arrival_ms:
            now_ms = next_completion_ms
            _, request_id, request, key = active["events"][completion_index]
            if config["cache_enabled"]:
                cache.store(key, request["expected_output"], now_ms)
            active["next_event"] += 1
            if active["next_event"] >= len(active["events"]):
                active = None
        else:
            now_ms = next_arrival_ms
            admit(requests[index], now_ms)
            index += 1

    if len(records) != len(requests):
        raise RuntimeError("simulation ended before every request received a terminal status")

    successful = [record for record in records.values() if record["status"] in {"model_response", "cache_hit"}]
    model_responses = [record for record in successful if record["model_compute"]]
    correct = [record for record in successful if record["output_matches_reference"] is True]
    rejected = [record for record in records.values() if record["status"] == "rejected_queue_full"]
    latency_values = [record["response_latency_ms"] for record in successful]
    ttft_values = [record["ttft_ms"] for record in model_responses]
    queue_wait_values = [record["queue_wait_ms"] for record in model_responses]
    first_arrival = min(float(request["arrival_ms"]) for request in requests)
    last_completion = max(float(record["completed_at_ms"]) for record in successful)
    elapsed_ms = max(0.0, last_completion - first_arrival)
    elapsed_seconds = elapsed_ms / 1000.0
    successful_tokens = sum(
        request["output_tokens"]
        for request in requests
        if records[request["request_id"]]["status"] in {"model_response", "cache_hit"}
    )
    fixture_match_rate = len(correct) / elapsed_seconds if elapsed_seconds > 0 else None
    response_rate = len(successful) / elapsed_seconds if elapsed_seconds > 0 else None
    token_rate = successful_tokens / elapsed_seconds if elapsed_seconds > 0 else None

    return {
        "name": config["name"],
        "batch_size_limit": config["batch_size"],
        "batch_wait_ms_limit": _round_ms(config["batch_wait_ms"]),
        "max_queue_size": config["max_queue_size"],
        "response_cache_enabled": config["cache_enabled"],
        "max_cache_entries": config["max_cache_entries"],
        "max_cache_payload_bytes": config["max_cache_bytes"],
        "request_count": len(requests),
        "successful_responses": len(successful),
        "queue_rejections": len(rejected),
        "model_compute_requests": len(model_responses),
        "response_cache_hits": sum(record["cache_hit"] for record in successful),
        "output_integrity_matches": len(correct),
        "output_integrity_rate": _round_ms(len(correct) / len(successful) if successful else 0.0),
        "deadline_misses": sum(record["deadline_missed"] is True for record in successful),
        "max_waiting_queue_depth": queue_peak,
        "model_batches": len(batch_summaries),
        "max_batch_observed": max((batch["batch_size"] for batch in batch_summaries), default=0),
        "response_latency_p50_ms": _round_ms(nearest_rank_percentile(latency_values, 50)),
        "response_latency_p95_ms": _round_ms(nearest_rank_percentile(latency_values, 95)),
        "model_ttft_p95_ms": _round_ms(nearest_rank_percentile(ttft_values, 95)),
        "queue_wait_p95_ms": _round_ms(nearest_rank_percentile(queue_wait_values, 95)),
        "trace_elapsed_ms": _round_ms(elapsed_ms),
        "completed_responses_per_second": _round_ms(response_rate),
        "fixture_correct_responses_per_second": _round_ms(fixture_match_rate),
        "fixture_output_tokens_per_second": _round_ms(token_rate),
        "response_cache_payload_bytes_final": cache.payload_bytes,
        "response_cache_payload_bytes_peak": cache.peak_payload_bytes,
        "batch_schedule": batch_summaries,
        "per_request": [records[request["request_id"]] for request in requests],
    }


def analyze_fixture(fixture: dict[str, Any], fixture_sha256: str) -> dict[str, Any]:
    validate_fixture(fixture)
    keys = {response_cache_key(request) for request in fixture["requests"]}
    runs = [simulate(fixture, config) for config in CONFIGURATIONS]
    return {
        "project_id": FIXTURE_ID,
        "fixture_id": FIXTURE_ID,
        "fixture_sha256": fixture_sha256,
        "synthetic": True,
        "request_count": len(fixture["requests"]),
        "unique_exact_cache_keys": len(keys),
        "run_count": len(runs),
        "runs": runs,
        "external_http_requests": 0,
        "live_model_calls": 0,
        "gpu_used": False,
        "production_trace_used": False,
        "personal_records": 0,
        "model_quality_evaluated": False,
        "scope": (
            "Deterministic discrete-event illustration of one synthetic service worker, "
            "bounded FIFO waiting queue, optional microbatching, and bounded exact-response cache. "
            "The model response is a fixed fixture string; no inference runtime is executed."
        ),
        "limitations": [
            "All arrivals, token counts, reference strings, capacities, and service-time coefficients are invented; no production trace is represented.",
            "The single-worker service-time formula is a teaching assumption, not a GPU, model, vLLM, or hardware benchmark.",
            "The mock returns fixture reference strings, so output-integrity equality is not model quality, factuality, safety, or human evaluation.",
            "The response-cache payload estimate counts UTF-8 key and body bytes only; it omits Python object, allocator, index, and process overhead.",
            "Cache freshness, personalized or tenant isolation, authorization, rate limiting, telemetry, cancellation, retry policy, deployment, and autoscaling are not implemented.",
            "The simulator has one worker, FIFO queueing, no in-flight duplicate coalescing, and no stochastic variation or confidence interval."
        ],
    }


def analyze_file(fixture_path: Path) -> dict[str, Any]:
    raw = fixture_path.read_bytes()
    fixture = json.loads(raw.decode("utf-8"))
    return analyze_fixture(fixture, hashlib.sha256(raw).hexdigest())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simulate a synthetic service queue, microbatch policy, and exact response cache"
    )
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, default=Path("-"))
    args = parser.parse_args()
    result = analyze_file(args.fixture)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if str(args.output) == "-":
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
```
