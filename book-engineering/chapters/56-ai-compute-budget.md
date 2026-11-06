# جلد چهارم، فصل ۱۰ — بودجه و هزینهٔ مالکیت سامانه‌های محاسباتی

> **جایگاه:** فصل محلی ۱۰ از ۱۵ فصل جلد چهارم؛ فصل سراسری ۵۶ از ۶۱. این فصل بعد از برآورد workload و منابع در فصل ۵۴ و طراحی اجزای آزمایشگاه در فصل ۵۵ می‌آید. کارش تبدیل یک طرح فنیِ مشروط به بودجه، جریان هزینه، مقایسهٔ سناریوها و نقطه‌های تصمیم است؛ انتخاب GPU یا طراحی دوبارهٔ آزمایشگاه نیست.
>
> **مرز قیمت:** هر عددِ بازار باید همراه تاریخ، محل/منطقه، ارز، واحد صورتحساب و اقلام داخل/خارج از قیمت خوانده شود. نمونهٔ ابر این فصل برای Iowa (`us-central1`) است، نه Dallas. نمونهٔ برق، میانگین تجاری کل Texas است، نه تعرفهٔ Dallas یا قبض مشتری. اعداد خرید و اجارهٔ پروژه synthetic هستند، نه قیمت بازار.
>
> **پیش‌نیاز و خروجی:** از فصل ۵۴، دفتر workload و فرض‌های حافظه/زمان را بیاورید؛ از فصل ۵۵، فهرست اجزا، برق، خنک‌کاری، شبکه، فضا و برنامهٔ ارتقا را. در پایان، یک برگهٔ هزینهٔ قابل بازبینی خواهید داشت. انتخاب و راه‌اندازی چارچوب‌های نرم‌افزاری در فصل بعد، ۵۷، می‌آید.

## ۱. چرا «قیمت یک GPU» بودجهٔ محاسبات نیست؟

قیمتِ یک قطعه فقط یک ورودی است، نه پاسخِ «کدام گزینه کم‌هزینه‌تر است؟». ممکن است یک کارت ارزان به میزبان، برق، خنک‌کاری، حافظه، کابل، نصب، قطعهٔ یدکی، نیروی نگهداری یا توقفی نیاز داشته باشد که در برچسب کالا دیده نمی‌شود. در ابر نیز نرخ ساعتی یک ماشین با قبض کامل یکسان نیست: دیسک، خروج داده، سرویس‌های پیرامونی، ظرفیت بیکار، پشتیبانی و مالیات می‌توانند جدا باشند.

سؤال درست این است: **برای ارائهٔ یک خدمت مشخص، در یک بازهٔ زمانی و بازار معین، با چه سطحی از دسترس‌پذیری و ریسک، چه جریان هزینه‌ای می‌پردازیم؟** پاسخ باید از نیاز به خروجی پذیرفته‌شده برسد؛ نه از یک عدد تبلیغاتی به نتیجه‌ای دربارهٔ سرعت یا صرفه.

فصل ۵۴ تخمین منابع را از شکل بار کاری آغاز کرد. فصل ۵۵ آن را به طرح فیزیکی و فهرست سازگاری تبدیل کرد. این فصل هیچ‌کدام را جایگزین نمی‌کند؛ تنها آن‌ها را به فرض‌های بودجه‌ایِ قابل پیگیری پیوند می‌دهد. اگر فرضِ زمان اجرا هنوز اندازه‌گیری نشده، آن را «نامعلوم/فرض» نگه دارید، نه رقم قطعی.

![شکل ۴-۱۰-۱ — جریان هزینه از پرداخت آغازین و دوره‌ای تا TCO/NPV و هزینهٔ خروجی؛ گزینه‌های خرید، اجاره و ابر فقط با مرز بازار و خدمت همسان مقایسه می‌شوند.](assets/images/babak-ai/v4-ch10-tco-timeline.svg)

## ۲. واحد تصمیم و مرز مقایسه را پیش از قیمت‌گیری بنویسید

قبل از درخواست پیش‌فاکتور، یک برگهٔ یک‌صفحه‌ای برای هر سناریو بسازید:

- **خروجی:** چه کاری باید تمام شود؟ مثلاً تعداد آزمایش‌های آموزشیِ پذیرفته‌شده، درخواست استنتاج در بار و سطح کیفیت معین، یا حجم دادهٔ پردازش‌شده. «یک ساعت GPU» به‌تنهایی خروجی نیست.
- **کیفیت و ظرفیت:** معیار پذیرش، حجم هم‌زمانی، زمان پاسخ، حافظه و پایداری موردنیاز چیست؟ خروجی ارزان‌تر که نیاز را برآورده نمی‌کند، گزینهٔ هم‌ارز نیست.
- **افق:** چند ماه یا سال استفاده می‌کنیم؟ عمر مفید فنی را با عمر پشتیبانی، قرارداد، سیاست نگهداری داده و دورهٔ بودجه یکی نگیرید.
- **بازار و تاریخ:** کشور/منطقه، ارز، مالیات یا وضعیت معافیت، تاریخ مشاهدهٔ قیمت، تاریخ اعتبار پیشنهاد و زمان تحویل را ثبت کنید.
- **مرز خدمت:** در قیمت چه چیزی هست و چه چیزی نیست؟ برای خرید، تحویل و راه‌اندازی؛ برای اجاره، تعمیر و بازگشت؛ برای ابر، دیسک، شبکه، پشتیبانی، ظرفیت رزروشده و هزینهٔ خروج داده را جداگانه روشن کنید.
- **سطح خدمت و ریسک:** دسترس‌پذیری، زمان تعمیر/جایگزینی، پشتیبان، تحمل توقف و حداکثر بودجهٔ مجاز را بنویسید.

این مشخصات مقایسه را قابل بازتولید می‌کند. دو قیمت با واحد یا مرز متفاوت، حتی اگر هر دو «ماهانه» باشند، مستقیماً قابل قیاس نیستند.

## ۳. هزینهٔ کل مالکیت را به دفترهای جدا بشکنید

یک مدل مفید هزینه‌ها را دست‌کم به چهار دفتر تقسیم می‌کند:

1. **یک‌باره و آغازین:** خرید یا ودیعه، حمل، بیمهٔ حمل، مالیات/عوارض، رک و کابل، UPS، نصب، راه‌اندازی، آزمون پذیرش و انتقال داده.
2. **ثابت و دوره‌ای:** پشتیبانی، نگهداری، قرارداد، بیمه، فضا، مجوز، نیروی بهره‌برداری و هزینهٔ ثابت اتصال.
3. **متغیر با مصرف:** انرژی، مصرف ساعتی ابر، ذخیره‌سازی، خروج داده، ظرفیت‌افزوده، مصرفی‌ها و هزینهٔ وابسته به تعداد اجرا.
4. **ریسک، خروج و ارزش پایانی:** تأخیر عرضه، خرابی، زمان ازکارافتادگی، تعویض، تمدید اجباری، هزینهٔ مهاجرت/پاک‌سازی، بازگرداندن تجهیز، خرید انتهای اجاره و ارزش فروش/باقیمانده.

هزینهٔ مالکیت کل (Total Cost of Ownership, **TCO**) به افق مشخص وابسته است؛ یک تعریف سادهٔ اسمی چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="هزینهٔ کل مالکیت اسمی برابر هزینهٔ آغازین به‌علاوهٔ مجموع هزینه‌های هر سال، منهای ارزش باقیمانده در پایان افق است">
  <mrow><msub><mi>TCO</mi><mi>H</mi></msub><mo>=</mo><msub><mi>C</mi><mn>0</mn></msub><mo>+</mo><munderover><mo>∑</mo><mrow><mi>t</mi><mo>=</mo><mn>1</mn></mrow><mi>H</mi></munderover><msub><mi>C</mi><mi>t</mi></msub><mo>−</mo><msub><mi>R</mi><mi>H</mi></msub></mrow>
</math>

**متن جایگزین فرمول:** `TCO_H = C_0 + Σ(t=1..H) C_t − R_H`؛ در این نمایش ساده، `C_0` پرداخت آغازین، `C_t` هزینهٔ سال `t` و `R_H` ارزش باقیمانده در پایان افق است.

این فرمول قرارداد مدل است، نه قاعدهٔ حسابداری. اگر در جریان‌های نقدی، ارزش باقیمانده را از سال پایانی کم کرده‌اید، آن را دوباره از TCO کم نکنید. همچنین استهلاک دفتری را روی خرید نقدی اضافه نکنید، مگر هدف مشخصاً صورت سودوزیان یا مالیات باشد؛ استهلاک با خروج وجه نقد یکسان نیست. برای گزارش مالیاتی/حسابداری از متخصص همان حوزه و همان jurisdiction راهنمایی بگیرید.

## ۴. اسمی یا ارزش فعلی؟ زمان پرداخت را آشکار کنید

جمع اسمی پول در سال‌های مختلف، اثر زمان ارزش پول را نادیده می‌گیرد. برای مقایسهٔ جریان‌ها در یک افق، ارزش فعلی خالص هزینه‌ها (Net Present Value, **NPV**) را می‌توان با نرخ تنزیل سالانهٔ `r` نوشت:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="ارزش فعلی هزینه برابر هزینهٔ سال صفر به‌علاوهٔ مجموع هزینهٔ سال t تقسیم بر یک به‌علاوهٔ نرخ تنزیل به توان t است؛ ارزش باقیمانده در سال H به صورت جریان منفی وارد می‌شود">
  <mrow><mi>NPV</mi><mo>=</mo><msub><mi>C</mi><mn>0</mn></msub><mo>+</mo><munderover><mo>∑</mo><mrow><mi>t</mi><mo>=</mo><mn>1</mn></mrow><mi>H</mi></munderover><mfrac><msub><mi>C</mi><mi>t</mi></msub><msup><mrow><mo>(</mo><mn>1</mn><mo>+</mo><mi>r</mi><mo>)</mo></mrow><mi>t</mi></msup></mfrac></mrow>
</math>

**متن جایگزین فرمول:** `NPV = C_0 + Σ(C_t / (1+r)^t)`؛ اگر ارزش باقیمانده وجود دارد، آن را به‌صورت جریان هزینهٔ منفی در سال `H` وارد کنید. نرخ `r` باید از سیاست مالی/بودجهٔ سازمان یا فرض مستند بیاید؛ آن را از روی نرخ بهرهٔ دلخواه انتخاب نکنید.

در برگهٔ تصمیم، **هر دو** جمع اسمی و NPV را نگه دارید و زمان‌بندی پرداخت را نشان دهید. نرخ اسمی را با جریان اسمی و نرخ واقعی را با جریان ثابت‌قیمت جفت کنید؛ تورم و افزایش قرارداد را دوبار نشمارید. اگر نرخ تنزیل، عمر خدمت یا ارزش پایانی عوض شود، نتیجه را در سناریوی حساسیت دوباره حساب کنید. این مدل جایگزین تحلیل مالی رسمی نیست.

## ۵. خرید: فراتر از قیمت فاکتور

در سناریوی خرید، نقطهٔ شروع پیش‌فاکتور هم‌دامنه است. ردیف‌های جداگانه را بررسی کنید:

- تجهیز، قطعهٔ جایگزین و زمان تحویل؛
- حمل، بسته‌بندی/بیمه، مالیات و هزینهٔ وارداتِ مربوط به بازار واقعی؛
- میزبان و سازگاری مادربرد، شاسی، مسیر PCIe، RAM و firmware؛
- برق ورودی، مدار/UPS، کابل و آزمون بار؛
- خنک‌کاری و ظرفیت اتاق، رک، فضا و نویز؛
- شبکه و ذخیره‌سازیِ لازم برای بار، backup و انتقال داده؛
- نصب، پذیرش، آموزش، زمان نیروی فنی و پشتیبانی؛
- قطعهٔ یدکی، تعمیر، توقف، تمدید ضمانت و پایان عمر؛
- ارزش باقیمانده و هزینهٔ پاک‌سازی/فروش/حذف در پایان افق.

فصل ۵۵ فهرست سازگاری را نگه می‌دارد؛ بودجه نباید با جمعِ قیمت چند قلم ناسازگار ساخته شود. ردیف «احتیاط» را نیز به نام و دلیل مشخص ثبت کنید؛ درصدی بی‌منبع که همهٔ ریسک‌ها را می‌پوشاند، جایگزین برآورد شفاف نیست.

## ۶. برق: واحد اندازه‌گیری و مرز تأسیسات را اعلام کنید

هزینهٔ انرژی برای تخمین ساده از توان ورودیِ اندازه‌گیری‌شده، ساعت کار و نرخ برق به‌دست می‌آید:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="هزینهٔ انرژی برابر توان ورودی بر حسب کیلووات ضربدر ساعت روشن‌بودن ضربدر نرخ دلار به ازای هر کیلووات ساعت است">
  <mrow><msub><mi>C</mi><mtext>energy</mtext></msub><mo>=</mo><msub><mi>P</mi><mtext>site,kW</mtext></msub><mo>×</mo><mi>h</mi><mo>×</mo><msub><mi>p</mi><mtext>USD/kWh</mtext></msub></mrow>
</math>

**متن جایگزین فرمول:** `هزینهٔ انرژی = توان ورودیِ سایت (kW) × ساعت (h) × نرخ ($/kWh)`؛ نمونهٔ قابل‌اندازه‌گیری را از توان اسمی یا TDP به‌جای متر/زیرمتر معتبر نسازید.

برای هزینهٔ تأسیسات روشن کنید آیا مرز کنتور فقط node است یا سرمایش، UPS و شبکه را نیز دربرمی‌گیرد. اگر از PUE استفاده می‌کنید، تعریف و اندازه‌گیری آن را ثبت کنید و بار سرمایش را دوباره به هزینهٔ برقِ کل ساختمان اضافه نکنید. تعرفه ممکن است هزینهٔ تقاضا، پلهٔ مصرف، زمان‌مند، مالیات، حداقل قبض یا تعدیل داشته باشد؛ میانگین انرژی را قبض کامل فرض نکنید.

**نمونهٔ بازار، نه تعرفهٔ Dallas:** جدول رسمی EIA برای بخش تجاری Texas، میانگین **8.96 سنت/kWh** را برای **August 2026** گزارش می‌کند؛ جدول در **2026-10-23** منتشر شده و دادهٔ آن statewide و مقدماتی است [۴]. با این نرخ، `1000 kWh × $0.0896/kWh = $89.60` به‌عنوان ضرب آموزشی به‌دست می‌آید؛ این مبلغ قبض، تعرفهٔ Dallas، هزینهٔ demand یا نرخ یک مشتری واقعی نیست.

## ۷. ابر: نرخ ماشین را از فاکتور کامل جدا کنید

برای ماشین‌های ابری، دست‌کم این ردیف‌ها را جدا نگه دارید:

- زمان صورتحساب ماشین (ساعت، دقیقه یا granularity واقعی ارائه‌دهنده) و حداقل/گردکردن؛
- ماشین فعالِ بیکار، ظرفیت رزروشده، commitment و شرایط تخفیف؛
- دیسک، snapshot، ذخیره‌سازی پایدار، IOPS و انتقال داده؛
- شبکه، egress، load balancer، IP و سرویس‌های پیرامونی؛
- منطقه، پشتیبانی، مجوز نرم‌افزار، مالیات و اعتبار/هزینهٔ خروج؛
- ساخت و حذف منابع، quota، نگهداری داده و نیروی بهره‌برداری.

نمونهٔ مستند و تاریخ‌دار این فصل:

| قلم | مشاهدهٔ منتشرشده | بازار و تاریخ | داخل/خارج از عدد |
|---|---|---|---|
| ماشین `g4-standard-48` | **$4.49993 به‌ازای VM-hour** | Iowa, US، منطقهٔ `us-central1`؛ صفحهٔ قیمت واکشی‌شده در 2026-11-06 | قیمت ماشین کاملِ فهرست‌شده؛ دیسک، شبکه/egress، مالیات و سرویس‌های دیگر جدا هستند. نرخ Dallas نیست. |
| پیکربندی منتشرشدهٔ همین نوع ماشین | 48 vCPU، 180 GB حافظهٔ میزبان، یک NVIDIA RTX PRO 6000 با 96 GB GDDR7 | مستندات رسمی خانوادهٔ G4؛ بازبینی 2026-11-06 | مشخصهٔ فهرست‌شدهٔ ماشین؛ تضمین کارایی بار شما یا قیمت خرید محلی نیست. |
| میانگین برق تجاری | **8.96¢/kWh** | Texas statewide؛ دادهٔ August 2026، انتشار 2026-10-23 | میانگین ایالتی EIA؛ نه Dallas tariff و نه قبض/هزینهٔ نهایی مشتری. |

صفحهٔ قیمت Google Cloud در تاریخ بازبینی، نرخ بالا را برای Iowa (`us-central1`) نشان می‌داد [۲]. مستندات ماشین، مشخصهٔ `g4-standard-48` را ثبت می‌کند [۳]. برای **1000 VM-hour**، ضرب مستقیم برابر **$4,499.93** می‌شود؛ این فقط خط محاسبات ماشین در آن snapshot است. ذخیره‌سازی، شبکه/خروج داده، پشتیبانی، مالیات، ساعات بیکار، شرایط قراردادی و تغییر بعدی قیمت را از آن نتیجه نگیرید.

جدول برق و قیمت ابر دو دادهٔ متفاوت‌اند: اولی میانگین ایالتی برق تجاری است، دومی نرخ یک ماشین در یک منطقهٔ ابری. کنار هم آوردن آن‌ها به معنی مقایسهٔ مستقیم خرید در Dallas با cloud نیست. هر نقل‌قول ابری جدید باید همان بازار، منطقه، تاریخ، ارز، نوع خرید و فهرست اقلام را دوباره ثبت کند.

## ۸. اجاره، مالکیت و مصرف ابری را در افق یکسان بسنجید

- **خرید:** پرداخت سرمایه‌ای و هزینهٔ زیرساخت/نگهداری در برابر دسترسی و اختیار کنترل؛ ارزش باقیمانده، ظرفیت بلااستفاده و مسئولیت تعمیر بر عهدهٔ خریدار است.
- **اجاره/لیزینگ:** پرداخت دوره‌ای، ودیعه، مدت اجباری، SLA، نگهداری، جریمهٔ خروج، خرید انتهای دوره، هزینهٔ بازگشت و مسئولیت خرابی را بخوانید. «ماهانه» بدون مدت قرارداد، واحد مقایسه نیست.
- **ابر:** هزینه با مصرف بالا و پایین می‌رود و راه‌اندازی می‌تواند سریع باشد؛ اما انتقال داده، نگهداری منابع، هزینهٔ idle، وابستگی به منطقه/خدمت، تغییر نرخ، شبکه، quota و کنترل حاکمیتی نیز وارد تصمیم می‌شوند.

این‌ها یک رتبه‌بندی ثابت ندارند. خرید می‌تواند برای بار پایدار و ظرفیت واقعاً مصرف‌شده مناسب باشد؛ ابر می‌تواند برای آزمایش کوتاه یا تقاضای ناپایدار ارزش داشته باشد؛ اجاره ممکن است انعطاف قرارداد یا پشتیبانی‌ای بدهد که در خرید جداست. پاسخ را بار کاری، نیاز خدمت، موجودی ظرفیت، قرارداد و مقایسهٔ خروجی می‌سازند، نه برچسب «محلی» یا «ابر».

برای هر گزینه افق زمانی را یکسان کنید. اگر خرید سه ساله را با یک ماه ابر بسنجید، دو مسئلهٔ متفاوت را پاسخ داده‌اید. نرخ مصرف، رشد/کاهش workload، برنامهٔ ارتقا، زمان تحویل، مهاجرت و هزینهٔ پایان قرارداد را همسان‌سازی کنید.

## ۹. نقطهٔ سربه‌سر فقط با واحد و افق مشخص معنا دارد

برای یک مثال خطیِ ساده در افق ثابت، فرض کنید هزینهٔ ثابت مالکیت `F_own`، هزینهٔ متغیر مالکیت به‌ازای ساعت مصرف `v_own`، هزینهٔ ثابت گزینهٔ دوم `F_alt` و هزینهٔ هر ساعت گزینهٔ دوم `r_alt` باشد. آنگاه ساعت مصرفِ سربه‌سرِ فرضی چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="ساعت سربه‌سر برابر اختلاف هزینهٔ ثابت مالکیت و گزینهٔ دیگر تقسیم بر اختلاف نرخ متغیر گزینهٔ دیگر و مالکیت است، به شرط مثبت بودن مخرج و یکسان بودن خدمت">
  <mrow><msub><mi>h</mi><mo>*</mo></msub><mo>=</mo><mfrac><mrow><msub><mi>F</mi><mtext>own</mtext></msub><mo>−</mo><msub><mi>F</mi><mtext>alt</mtext></msub></mrow><mrow><msub><mi>r</mi><mtext>alt</mtext></msub><mo>−</mo><msub><mi>v</mi><mtext>own</mtext></msub></mrow></mfrac></mrow>
</math>

**متن جایگزین فرمول:** `h* = (F_own − F_alt) / (r_alt − v_own)`؛ فقط اگر مخرج مثبت و خدمت/خروجی، ظرفیت و افق یکسان باشد. اگر مخرج صفر یا منفی است یا هزینه‌ها غیرخطی/قراردادی‌اند، این رابطه نقطهٔ سربه‌سر قابل استفاده نمی‌دهد.

در خرید چندساله، `F_own` باید هزینهٔ ثابت همان افق، ارزش باقیمانده و زمان پرداخت را مطابق تعریف مدل داشته باشد؛ نرخِ متغیر را با هزینهٔ انرژی/نگهداری واقعی تعریف کنید. برای بار کاری متفاوت، به‌جای «ساعت» از خروجی پذیرفته‌شده یا بار benchmark همسان‌شده استفاده کنید. این تقریب دسترس‌پذیری، خرابی و تأخیر عرضه را مدل نمی‌کند.

## ۱۰. هزینه بر واحد خروجی: نخست، هم‌ارزی را ثابت کنید

اگر افق هزینه `H` سال و تعداد خروجی‌های پذیرفته‌شده `Q` باشد، می‌توان نرخ هزینه را چنین گزارش کرد:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="هزینهٔ هر خروجی پذیرفته‌شده برابر ارزش فعلی کل هزینه تقسیم بر تعداد خروجی‌های هم‌ارز و پذیرفته‌شده در همان افق است">
  <mrow><msub><mi>C</mi><mtext>per accepted unit</mtext></msub><mo>=</mo><mfrac><mi>NPV</mi><mi>Q</mi></mfrac></mrow>
</math>

**متن جایگزین فرمول:** `هزینهٔ هر واحد پذیرفته‌شده = NPV / Q`؛ `Q` باید تعداد خروجی‌هایی باشد که کیفیت و معیار پذیرش مشترک را گذرانده‌اند، نه تعداد batch فرضی.

برای معتبر بودن این تقسیم، workload، کیفیت، سطح خدمت و معیار پذیرش باید همسان باشد و `Q` از benchmark یا دادهٔ عملیاتیِ قابل تکرار بیاید. هزینهٔ به ازای token، image یا training step بدون مشخصات کیفیت، توالی، batch، وقت‌بیکاری، نرخ شکست و هزینه‌های اطراف می‌تواند گمراه‌کننده باشد. اگر یکی از فرض‌های هم‌ارزی اندازه‌گیری نشده، مقدار را صرفاً یک **سناریوی محاسباتی** و نه ranking گزینه‌ها گزارش کنید.

## ۱۱. عدم‌قطعیت را به یک عددِ ظاهراً دقیق پنهان نکنید

برای هریک از ورودی‌های حساس، بازهٔ معقول و منبع آن را ثبت کنید:

- ساعت مصرف و درصد بیکاری؛
- قیمت معتبر خرید، هزینهٔ تحویل و موعد دسترسی؛
- نرخ انرژی و مرز اندازه‌گیری؛
- عمر خدمت، ارزش باقیمانده و هزینهٔ تعویض؛
- مدت اجاره، جریمهٔ فسخ و شرایط تمدید؛
- نرخ cloud، زمان billed، storage/egress و رشد داده؛
- زمان نیروی نگهداری، توقف و هدف بازیابی.

سه سناریوی **کم/پایه/زیاد** را با فرض‌های مشخص نگه دارید؛ سپس حساسیت یک‌به‌یک را نشان دهید. نمودار tornado یا جدول حساسیت زمانی مفید است که ورودی‌های پرتأثیر و منشأ بازه روشن باشند. اگر احتمال خرابی/تأخیر را به‌کار می‌برید، احتمال و پیامد باید مستند و متعلق به زمینهٔ شما باشد؛ ضرب `احتمال × پیامد` فقط خلاصهٔ مورد انتظارِ همان مفروضات است، نه پیش‌بینی قطعی.

GAO-20-195G بر تعریف هدف و دامنه، مستندسازی فرض‌ها و داده، تحلیل ریسک/عدم قطعیت، بازبینی برآورد و به‌روزرسانی با هزینهٔ واقعی تأکید دارد [۱]. آن را چرخهٔ مدیریت برآورد بخوانید، نه قالبی که به‌تنهایی دقت رقم را تضمین کند. نسخهٔ تاریخ‌دارِ ورودی و دلیل هر تغییر را نگه دارید.

## ۱۲. زمان تحویل و ظرفیت: هزینهٔ توقف هم بخشی از تصمیم است

برای سخت‌افزاری که باید خریداری شود، زمان تحویل و احتمال نبود کالا می‌تواند هزینهٔ واقعی ایجاد کند: تأخیر پژوهش، رزرو نیروی کار، تمدید اجارهٔ موقت، جابه‌جایی برنامهٔ پروژه یا ازدست‌رفتن ظرفیت. این اثرها را با منبع و واحد روشن کنید؛ آن‌ها را بی‌دلیل به مبلغ فاکتور اضافه نکنید.

در برگهٔ خرید، حداقل این ستون‌ها را داشته باشید: تاریخ استعلام، انقضا، فروشنده/کانال مجاز، شمارهٔ دقیق مدل و revision، تحویل، ارز، مالیات/حمل، موجودی، ضمانت، تعمیر/RMA، جایگزین مجاز، شرط فسخ و زمان پرداخت. اگر نرخ یا موجودی فقط شفاهی است، آن را «تأییدنشده» علامت بزنید.

گزینهٔ جایگزین را فقط به‌دلیل قیمت کمتر قبول نکنید. فصل ۵۵ ماتریس سازگاری را حفظ می‌کند؛ تغییری در GPU، PSU، شاسی، firmware، driver یا مسیر داده نیازمند آزمون سازگاری و پذیرشِ دوبارهٔ معماری است.

## ۱۳. ریسک عرضه و بررسی موشکافانهٔ تأمین‌کننده

هزینهٔ پایین روی کاغذ می‌تواند با نبود قطعه، منبع نامعتبر، پشتیبانی ضعیف یا وابستگیِ تک‌تأمین‌کننده دوام نیاورد. بررسی را متناسب با اهمیت سامانه و توان سازمان انجام دهید: مالکیت و کنترل تأمین‌کننده، اصالت و منشأ قطعه، مسیر توزیع، سابقهٔ جایگزینی، تاب‌آوری، امنیت پایه، نگهداری firmware/driver، دسترسی به اصلاحیه، تعمیر، قطعات یدکی، انقضای پشتیبانی، وابستگی‌های زیرتأمین‌کننده و برنامهٔ خروج.

NIST SP 1326، نسخهٔ نهایی منتشرشده در **2026-07-08**، یک راهنمای شروع برای بررسی موشکافانهٔ زنجیرهٔ تأمین سایبریِ ICT در چارچوب SP 800-161 Rev. 1 است [۵][۶]. پنج محور آن عبارت‌اند از: **FOCI** (مالکیت/کنترل/نفوذ خارجی)، **Provenance** (منشأ و زنجیرهٔ نگهداری)، **Resilience** (تاب‌آوری)، **Foundational Cyber Practices** (رویه‌های پایهٔ امنیت سایبری) و **Supply Chain Tiers** (لایه‌های زنجیرهٔ تأمین). این‌ها محورهای بررسی‌اند؛ SP 1326 گواهیِ محصول یا فروشنده نیست، فهرست تضمین خرید نیست و به‌خودی‌خود الزام قانونی برای همهٔ خریداران ایجاد نمی‌کند.

برای پروژهٔ کوچک، می‌توان همین سؤال‌ها را متناسب و مستند کرد؛ برای سامانهٔ حساس، باید مسئولیت، شواهد، سطح دسترسی و مسیر اصلاح/قطع همکاری تعریف شود. هیچ checkbox منفردی ریسک را صفر نمی‌کند. قیمت، مالکیت، کشور ساخت یا برچسب انطباق به‌تنهایی برای نتیجه‌گیری کافی نیست.

## ۱۴. بودجه را مرحله‌ای آزاد کنید، نه با یک تصمیم برگشت‌ناپذیر

یک برنامهٔ نمونهٔ چهاردروازه‌ای:

1. **دروازهٔ تعریف:** خروجی/سطح خدمت، مرز فنی فصل ۵۵، برآورد فصل ۵۴، بازار و تاریخ قیمت، سناریوهای هزینه، ریسک و سقف بودجه را بازبینی کنید. ابهام‌های گران را فهرست کنید.
2. **دروازهٔ آزمون محدود:** پیش از خرید بزرگ، از ظرفیت موجود، اجاره یا سرویس کوتاه‌مدت استفاده کنید تا throughput، کیفیت، انرژی، bottleneck و زمان کار واقعی سنجیده شود. قرارداد و سقف مصرف را محدود کنید.
3. **دروازهٔ توسعه:** فقط اگر آزمون نیاز را برآورده کرد، سازگاری/پشتیبانی/عرضه تأیید شد و هزینه بر خروجی قابل‌قبول بود، ظرفیت را مرحله‌ای اضافه کنید. نقطهٔ توقف و شخص تأییدکننده را تعیین کنید.
4. **دروازهٔ تمدید یا خروج:** پیش از پایان عمر/قرارداد، داده را مهاجرت/پاک‌سازی، رسانه و تجهیز را امن بازگردان/حذف، هزینهٔ باقی‌مانده و ارزش پایانی را بازبینی و تصمیم تمدید، فروش یا بازنشستگی را مستند کنید.

پایلوت، benchmark یا پیش‌فاکتور نتیجهٔ قطعی آینده نیست. هدف مرحله‌بندی این است که ورودی‌های مهم با واقعیت به‌روز شوند و تصمیم بزرگ بعد از یادگیری قابل لغو باشد.

## ۱۵. گردش‌کار برآوردی که بتوان بعداً بازبینی کرد

1. نسخهٔ نیاز و خروجی را قفل کنید؛ تغییر نیاز، تغییر برآورد را ثبت کند.
2. برای هر سناریو، بازار/منطقه، تاریخ، ارز، واحد مصرف و شمول قیمت را مشخص کنید.
3. درخواست‌های خرید/اجاره را با یک فهرست اجزا و سطح خدمت یکسان ارسال کنید.
4. قیمت را به جریان‌های یک‌باره، دوره‌ای، متغیر، خروج/ریسک و باقیمانده تفکیک کنید.
5. زمان تحویل، تعهد، تمدید، قطعات و پشتیبانی را با شاهد قرارداد/فروشنده بررسی کنید.
6. برق و استفاده را در مرز اعلام‌شده اندازه بگیرید؛ تخمین فصل ۵۴ را با آزمون واقعی جایگزین یا اصلاح کنید.
7. TCO اسمی و NPV را در افق یکسان بسازید؛ نرخ تنزیل، تورم، گردکردن و زمان‌بندی را اعلام کنید.
8. بد/پایه/خوب، حساسیت، محدودیت داده و ریسک زنجیره را ثبت کنید.
9. تأییدهای فنی، امنیتی، مالی و عملیاتی را از مسئولان مربوط بگیرید.
10. بعد از خرید یا اجرا، برآورد را با قبض، زمان تعمیر، مصرف، ساعت billed و خروجی پذیرفته‌شده مقایسه و به‌روزرسانی کنید.

راهنمای پروژه یک نسخهٔ محلی و آفلاین از همین حساب‌هاست؛ در بخش بعد، مرز محاسبات آن صریح می‌شود.

## ۱۶. پروژهٔ فصل: مدل آفلاین و fixture تاریخ‌دار

پروژهٔ `56-ai-compute-budget` با `Decimal`، یک fixture JSON را می‌خواند و جریان هزینهٔ سه سناریوی آموزشی را حساب می‌کند: خرید مصنوعی، اجارهٔ مصنوعی و مثال محاسباتی ابر. کد هیچ درخواست شبکه‌ای نمی‌زند و هیچ سخت‌افزاری را اندازه نمی‌گیرد.

در fixture، قیمت ابری `4.49993 USD/VM-hour` با بازار Iowa (`us-central1`) و تاریخ مشاهدهٔ 2026-11-06 ثبت شده است. نرخ `0.0896 USD/kWh`، میانگین تجاری کل Texas برای August 2026 است که 2026-10-23 منتشر شد؛ این ورودی فقط برای ردیف‌های فرضی برق خرید/اجاره استفاده شده و تعرفهٔ Dallas نیست. مبالغ acquisition، اجاره، نگهداری، ساعات مصرف، سایر هزینه‌ها، ارزش باقیمانده و تعداد «تحویل»‌ها همگی `synthetic_fixture` هستند؛ هیچ‌کدام نقل‌قول فروشنده یا اندازه‌گیری واقعی نیستند.

**اجرا از ریشهٔ مخزن:**

```bash
python -m unittest discover -s book-engineering/projects/56-ai-compute-budget -v
python book-engineering/projects/56-ai-compute-budget/budget_model.py \
  --fixture book-engineering/projects/56-ai-compute-budget/sample_budget.json \
  --output book-engineering/projects/56-ai-compute-budget/results.json
```

مدل با نرخ سالانهٔ تنزیل ۵٪ و افق مصنوعی سه‌ساله، جریان اولیه را در سال صفر، هزینه‌های تکرارشونده را در پایان سال و ارزش باقیمانده/خرید پایانی را در افق منظور می‌کند. هزینه‌های هر سال برای گزارش به سنت گرد می‌شوند. صورتحساب واقعی ممکن است granularity و شیوهٔ گردکردن دیگری داشته باشد.

## ۱۷. خروجی نمونه و آنچه از آن **نمی‌توان** نتیجه گرفت

اجرای fixture، این مقادیر را می‌دهد:

| سناریوی مصنوعی | TCO اسمی (USD) | NPV با فرض ۵٪ (USD) | NPV بر «تحویل فرضی» (USD) |
|---|---:|---:|---:|
| خرید synthetic | 8,595.14 | 8,577.77 | 23.83 |
| اجاره synthetic | 14,005.14 | 12,726.99 | 35.35 |
| cloud snapshot illustration | 12,149.82 | 11,028.99 | 30.64 |

این جدول **رتبه‌بندی خرید واقعی نیست**. هزینهٔ خرید/اجاره مصنوعی است، تعداد سالانهٔ تحویل‌ها فرض شده، هم‌ارزی throughput/کیفیت سنجیده نشده، و فقط خط ماشین ابر از snapshot منتشرشده آمده است. مدل نیز مالیات، تامین مالی، تورم/افزایش قیمت، هزینهٔ demand، نیروی کار، downtime، تمدید پشتیبانی، هزینهٔ کامل cloud، outage و هزینهٔ تغییر/خروج را وارد نمی‌کند. قیمت Iowa را برای Dallas به‌کار نبرید و میانگین برق Texas را تعرفهٔ محلی نخوانید.

`results.json` علاوه بر خروجی، SHA-256 fixture، بازار/تاریخ ورودی، تعداد فرضی، جریان‌های سالانه و محدودیت‌ها را نگه می‌دارد. آزمون‌ها هم قیمت/بازار، برچسب synthetic، نرخ تبدیل انرژی، NPV، ورودی‌های منفی/نامتناهی و برابری کد/fixture را بررسی می‌کنند؛ این‌ها آزمون حسابداری کدند، نه آزمون کارایی دستگاه یا پیش‌بینی قیمت.

## ۱۸. تمرین‌ها

۱. برای یک طرح آزمایشگاهی از فصل ۵۵، واحد تصمیم را در یک جمله بنویسید. حداقل سه معیار خروجی یا سطح خدمت را مشخص کنید که باید در خرید، اجاره و ابر برابر باشند.

۲. از نمونهٔ فصل، محاسبهٔ `1000 VM-hour × $4.49993` را بازتولید کنید. دست‌کم پنج قلمی را نام ببرید که از این خط هزینه نمی‌توان درباره‌شان نتیجه گرفت. منطقه و تاریخ مشاهده را نیز ذکر کنید.

۳. با میانگین EIA ثبت‌شده، هزینهٔ ضربی `540 kWh` را محاسبه کنید. توضیح دهید چرا این عدد به‌تنهایی قبض یک مشتری در Dallas نیست و برای تبدیل توان به kWh چه مرز/مدت اندازه‌گیری لازم است.

۴. در یک افق سه‌ساله، هزینهٔ خرید در آغاز `F_own=$10,000` و هزینهٔ متغیر مالکیت `$8/hour` فرض کنید؛ گزینهٔ دیگر `F_alt=$1,000` و نرخ `$20/hour` است. ساعت سربه‌سر را در مدل خطی حساب کنید. دو فرضی را بنویسید که اگر برقرار نباشند، نتیجه معتبر نیست.

۵. چرا استهلاک را نباید بی‌دلیل به پرداخت نقدی خرید اضافه کرد؟ تفاوت TCO نقدی با گزارش مالیاتی را در دو یا سه جمله توضیح دهید.

۶. برای فهرست خرید یک ردیفِ GPU با «قیمت بهتر» پیشنهاد شده، اما مدل دقیق یا revision آن فرق دارد. پیش از پذیرش جایگزین چه موارد فنی/تأمینی را بازبینی می‌کنید؟ چهار مورد کافی نیست؛ حداقل شش مورد بنویسید.

۷. پنج محور NIST SP 1326 را نام ببرید و یک جمله بگویید چرا این راهنما نه گواهی محصول است و نه منبع قیمت.

۸. یک برنامهٔ مرحله‌ای برای خرید یا تمدید خودتان بنویسید: آزمون اول، شرط توسعه، سقف هزینه و شرط توقف/خروج. تفاوت «قیمت» و «هزینه بر خروجی پذیرفته‌شده» را نیز در تصمیم ذکر کنید.

پاسخ‌نامهٔ مستقل و تشریحی تمرین‌ها در [پاسخ‌نامهٔ فصل ۵۶](book-engineering/answers/56-ai-compute-budget-fa.md) آمده است.

## ۱۹. جمع‌بندی

- هزینه را بر یک خدمت، خروجی، کیفیت، سطح دسترس‌پذیری و افق زمانی مشخص بسنجید؛ قیمت قطعه یا نرخ یک ساعت به‌تنهایی TCO نیست.
- جریان یک‌باره، ثابت، متغیر، ریسک/خروج و ارزش پایانی را جدا کنید؛ اسمی و NPV را با نرخ/زمان‌بندی مستند گزارش کنید.
- توان ورودی را در مرز مشخص بسنجید؛ تعرفهٔ برق، انرژی، هزینهٔ تقاضا و سرمایش را با هم خلط نکنید.
- بازار/منطقه/تاریخ و اقلام داخل/خارج از قیمت را روی هر snapshot ثبت کنید. نمونهٔ این فصل: قیمت G4 در Iowa (`us-central1`)، نه Dallas؛ میانگین برق statewide در Texas، نه تعرفهٔ محلی.
- فرض‌های synthetic و نقاط نامعلوم را صریح نگه دارید. بدون benchmark و هم‌ارزی خروجی، جدول هزینه حکم رتبه‌بندی عملکرد یا پیشنهاد خرید ندارد.
- استعلام، عرضه، منشأ، تاب‌آوری، پشتیبانی و برنامهٔ خروج را در کنار رقم بررسی کنید؛ سرمایه را مرحله‌ای آزاد و برآورد را با هزینهٔ واقعی به‌روز کنید.

در فصل ۵۷ وارد Python، PyTorch، JAX و TensorFlow می‌شویم. هزینهٔ فصل حاضر سقفِ خودکارِ انتخاب framework نیست؛ نیازهای اجرا، سازگاری و آزمون‌های workload باید به تصمیم نرم‌افزار پیوند بخورند.

## ۲۰. منابع و تاریخ بازبینی

**تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶ (2026-11-06).** تاریخ snapshotهای بازار نیز جداگانه در متن و fixture ثبت شده است. قیمت cloud یک مشاهده از صفحهٔ رسمی در همان تاریخ است، نه quote یا ضمانت نرخ آینده. دادهٔ EIA مربوط به ماه August 2026 و انتشار 2026-10-23 است.

۱. U.S. Government Accountability Office, *Cost Estimating and Assessment Guide: Best Practices for Developing and Managing Program Costs*, GAO-20-195G, 2020-03-12. راهنمای برآورد، دامنه/فرض‌ها، داده، تحلیل ریسک و به‌روزرسانی: [gao.gov/products/gao-20-195g](https://www.gao.gov/products/gao-20-195g).

۲. Google Cloud, *Accelerator-optimized machine family pricing*. جدول قیمت رسمی؛ snapshot مورد استفاده برای `g4-standard-48` در `us-central1` / Iowa، بازبینی 2026-11-06: [cloud.google.com/products/compute/pricing/accelerator-optimized](https://cloud.google.com/products/compute/pricing/accelerator-optimized). نرخ نمایش‌داده‌شدهٔ مورد استفاده `$4.49993/VM-hour` است؛ ردیف‌های دیگر و نرخ مناطق دیگر ممکن است فرق کنند.

۳. Google Cloud, *Accelerator-optimized machines*. مشخصهٔ خانوادهٔ G4 و ماشین‌ها؛ بازبینی 2026-11-06: [docs.cloud.google.com/compute/docs/accelerator-optimized-machines](https://docs.cloud.google.com/compute/docs/accelerator-optimized-machines). مستندات و محل عرضه را برای پیکربندی/زمان خرید خود دوباره بررسی کنید.

۴. U.S. Energy Information Administration, *Electric Power Monthly, Table 5.6.A: Average Price of Electricity to Ultimate Customers by End-Use Sector*. جدول رسمی XLSX: [eia.gov/electricity/monthly/xls/table_5_06_a.xlsx](https://www.eia.gov/electricity/monthly/xls/table_5_06_a.xlsx); صفحهٔ جدول: [eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a). مقدار نمونه برای Texas commercial، August 2026: `8.96¢/kWh`; statewide average مقدماتی، نه تعرفهٔ Dallas.

۵. National Institute of Standards and Technology, *NIST Cybersecurity Supply Chain Risk Management: Due Diligence Assessment Quick-Start Guide*, NIST SP 1326, نسخهٔ نهایی منتشرشده در 2026-07-08: [csrc.nist.gov/pubs/sp/1326/final](https://csrc.nist.gov/pubs/sp/1326/final). دامنهٔ این راهنما، بررسی موشکافانهٔ ICT در چارچوب مدیریت ریسک زنجیرهٔ تأمین سایبری است.

۶. NIST, *Cybersecurity Supply Chain Risk Management Practices for Systems and Organizations*, SP 800-161 Rev. 1, Update 1: [csrc.nist.gov/pubs/sp/800/161/r1/upd1/final](https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final). چارچوب مرجع C-SCRM؛ نیازهای هر سازمان و قرارداد جداگانه بررسی شود.

## ۲۱. پیوست اجرایی: کد آزموده‌شدهٔ پروژه

فایل `budget_model.py` در پروژهٔ فصل، بدون اتصال شبکه، بر fixture محلی اجرا می‌شود. نسخهٔ زیر باید بایت‌به‌بایت با فایل پروژه برابر بماند؛ برای تغییر، ابتدا آزمون‌ها و manifest نتایج را به‌روز کنید.

```python
"""Transparent lifecycle-cost arithmetic for an explicitly synthetic fixture.

This module does not fetch prices, inspect hardware, offer tax/accounting advice,
or establish that different compute services deliver equivalent work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CENT = Decimal("0.01")
ZERO = Decimal("0")


class BudgetInputError(ValueError):
    """Raised when the fixture is incomplete, inconsistent, or non-finite."""


def decimal_value(value: Any, field: str) -> Decimal:
    if isinstance(value, bool):
        raise BudgetInputError(f"{field} must be a finite decimal, not a boolean")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as error:
        raise BudgetInputError(f"{field} must be a finite decimal") from error
    if not result.is_finite():
        raise BudgetInputError(f"{field} must be finite")
    return result


def nonnegative(value: Any, field: str) -> Decimal:
    result = decimal_value(value, field)
    if result < ZERO:
        raise BudgetInputError(f"{field} must be nonnegative")
    return result


def integer(value: Any, field: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise BudgetInputError(f"{field} must be an integer >= {minimum}")
    return value


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def energy_cost_usd(site_input_kw: Any, powered_hours: Any, rate_usd_per_kwh: Any) -> Decimal:
    """Compute meter-boundary kWh times a user-supplied USD/kWh rate."""
    kw = nonnegative(site_input_kw, "site_input_kw")
    hours = nonnegative(powered_hours, "powered_hours")
    rate = nonnegative(rate_usd_per_kwh, "rate_usd_per_kwh")
    return kw * hours * rate


def cloud_compute_cost_usd(hourly_rate_usd: Any, billed_hours: Any) -> Decimal:
    rate = nonnegative(hourly_rate_usd, "hourly_rate_usd")
    hours = nonnegative(billed_hours, "billed_hours")
    return rate * hours


def net_present_value(cashflows: list[Decimal], annual_discount_rate: Any) -> Decimal:
    """Discount costs at year-end; index 0 is the initial cash flow."""
    if not isinstance(cashflows, list) or not cashflows:
        raise BudgetInputError("cashflows must be a non-empty list")
    rate = nonnegative(annual_discount_rate, "annual_discount_rate")
    if rate >= Decimal("1"):
        raise BudgetInputError("annual_discount_rate must be less than 1 for this teaching model")
    total = ZERO
    factor = Decimal("1") + rate
    for year, amount in enumerate(cashflows):
        cash = decimal_value(amount, f"cashflows[{year}]")
        total += cash / (factor ** year)
    return total


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BudgetInputError(f"{field} must be an object")
    return value


def validate_fixture(fixture: Any) -> dict[str, Any]:
    data = _require_mapping(fixture, "fixture")
    if data.get("schema_version") != 1:
        raise BudgetInputError("unsupported schema_version")
    if data.get("fixture_id") != "v4-ch10-synthetic-budget-v1":
        raise BudgetInputError("fixture_id does not match this chapter")
    if data.get("label_source") != "synthetic_fixture":
        raise BudgetInputError("the worked case must stay labeled synthetic_fixture")

    market = _require_mapping(data.get("market_snapshot"), "market_snapshot")
    cloud = _require_mapping(market.get("cloud_compute"), "market_snapshot.cloud_compute")
    energy = _require_mapping(market.get("electricity"), "market_snapshot.electricity")
    for record, field in ((cloud, "cloud_compute"), (energy, "electricity")):
        for required in ("as_of", "market", "currency", "source_url"):
            if not isinstance(record.get(required), str) or not record[required].strip():
                raise BudgetInputError(f"market_snapshot.{field}.{required} is required")
        if not record["source_url"].startswith("https://"):
            raise BudgetInputError(f"market_snapshot.{field}.source_url must use HTTPS")
    if cloud.get("currency") != "USD" or energy.get("currency") != "USD":
        raise BudgetInputError("the chapter fixture uses USD throughout")
    nonnegative(cloud.get("price_usd_per_instance_hour"), "cloud price")
    nonnegative(energy.get("price_usd_per_kwh"), "electricity price")
    if cloud.get("region") != "us-central1 (Iowa, US)":
        raise BudgetInputError("cloud snapshot region must remain explicit")
    if energy.get("market") != "Texas, US statewide commercial average":
        raise BudgetInputError("electricity snapshot must not be presented as a Dallas tariff")

    assumptions = _require_mapping(data.get("assumptions"), "assumptions")
    horizon = integer(assumptions.get("horizon_years"), "horizon_years", minimum=1)
    discount = nonnegative(assumptions.get("annual_discount_rate"), "annual_discount_rate")
    if discount >= Decimal("1"):
        raise BudgetInputError("annual_discount_rate must be less than 1")
    if assumptions.get("price_escalation_mode") != "held_constant_for_synthetic_demo":
        raise BudgetInputError("price_escalation_mode must disclose the fixture assumption")
    if assumptions.get("performance_parity_measured") is not False:
        raise BudgetInputError("the fixture must not claim measured performance parity")

    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != 3:
        raise BudgetInputError("exactly three teaching scenarios are required")
    seen: set[str] = set()
    for index, raw in enumerate(scenarios):
        scenario = _require_mapping(raw, f"scenarios[{index}]")
        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str) or not scenario_id or scenario_id in seen:
            raise BudgetInputError(f"scenarios[{index}].id must be unique and non-empty")
        seen.add(scenario_id)
        if scenario.get("quote_status") != "synthetic_not_a_vendor_quote":
            raise BudgetInputError(f"{scenario_id} must disclose synthetic quote status")
        if scenario.get("strategy") not in {"buy", "lease", "cloud"}:
            raise BudgetInputError(f"{scenario_id}.strategy must be buy, lease, or cloud")
        integer(scenario.get("annual_deliverables"), f"{scenario_id}.annual_deliverables", minimum=1)
        nonnegative(scenario.get("annual_other_cost_usd"), f"{scenario_id}.annual_other_cost_usd")
        nonnegative(scenario.get("upfront_cost_usd"), f"{scenario_id}.upfront_cost_usd")
        if scenario["strategy"] in {"buy", "lease"}:
            nonnegative(scenario.get("site_input_kw"), f"{scenario_id}.site_input_kw")
            integer(scenario.get("annual_powered_hours"), f"{scenario_id}.annual_powered_hours")
            nonnegative(scenario.get("annual_maintenance_usd"), f"{scenario_id}.annual_maintenance_usd")
            if scenario.get("energy_price_source") != "market_snapshot.electricity":
                raise BudgetInputError(f"{scenario_id} must identify its electricity input source")
        if scenario["strategy"] == "buy":
            for key in ("acquisition_cost_usd", "residual_value_usd"):
                nonnegative(scenario.get(key), f"{scenario_id}.{key}")
        elif scenario["strategy"] == "lease":
            for key in ("monthly_lease_payment_usd", "end_of_term_buyout_usd", "residual_value_usd"):
                nonnegative(scenario.get(key), f"{scenario_id}.{key}")
        else:
            if scenario.get("price_source") != "market_snapshot.cloud_compute":
                raise BudgetInputError(f"{scenario_id} must identify the dated cloud price source")
            if decimal_value(scenario.get("instance_hourly_price_usd"), f"{scenario_id}.instance_hourly_price_usd") != decimal_value(
                cloud["price_usd_per_instance_hour"], "market cloud price"
            ):
                raise BudgetInputError("cloud scenario price differs from its dated market snapshot")
            integer(scenario.get("annual_billed_instance_hours"), f"{scenario_id}.annual_billed_instance_hours")
    return data


def _scenario_cashflows(scenario: dict[str, Any], years: int, energy_rate: Decimal, cloud_rate: Decimal) -> tuple[list[Decimal], dict[str, Any]]:
    strategy = scenario["strategy"]
    annual_deliverables = int(scenario["annual_deliverables"])
    annual_other = nonnegative(scenario["annual_other_cost_usd"], "annual_other_cost_usd")
    upfront = nonnegative(scenario["upfront_cost_usd"], "upfront_cost_usd")
    rows: list[dict[str, str]] = []

    if strategy == "buy":
        acquisition = nonnegative(scenario["acquisition_cost_usd"], "acquisition_cost_usd")
        annual_maintenance = nonnegative(scenario["annual_maintenance_usd"], "annual_maintenance_usd")
        annual_energy = energy_cost_usd(
            scenario["site_input_kw"], scenario["annual_powered_hours"], energy_rate
        )
        initial = cents(acquisition + upfront)
        recurring = cents(annual_maintenance + annual_other + annual_energy)
        residual = nonnegative(scenario["residual_value_usd"], "residual_value_usd")
        components = {
            "acquisition_usd": str(cents(acquisition)),
            "upfront_usd": str(cents(upfront)),
            "annual_energy_kwh": str(nonnegative(scenario["site_input_kw"], "site_input_kw") * Decimal(int(scenario["annual_powered_hours"]))),
            "annual_energy_cost_usd": str(cents(annual_energy)),
            "annual_maintenance_usd": str(cents(annual_maintenance)),
            "annual_other_cost_usd": str(cents(annual_other)),
            "terminal_residual_credit_usd": str(cents(residual)),
        }
        cashflows = [initial] + [recurring for _ in range(years)]
        cashflows[-1] -= cents(residual)
    elif strategy == "lease":
        monthly = nonnegative(scenario["monthly_lease_payment_usd"], "monthly_lease_payment_usd")
        annual_lease = cents(monthly * Decimal(12))
        annual_maintenance = nonnegative(scenario["annual_maintenance_usd"], "annual_maintenance_usd")
        annual_energy = energy_cost_usd(
            scenario["site_input_kw"], scenario["annual_powered_hours"], energy_rate
        )
        initial = cents(upfront)
        recurring = cents(annual_lease + annual_maintenance + annual_other + annual_energy)
        buyout = nonnegative(scenario["end_of_term_buyout_usd"], "end_of_term_buyout_usd")
        residual = nonnegative(scenario["residual_value_usd"], "residual_value_usd")
        components = {
            "upfront_usd": str(cents(upfront)),
            "annual_lease_payment_usd": str(annual_lease),
            "annual_energy_kwh": str(nonnegative(scenario["site_input_kw"], "site_input_kw") * Decimal(int(scenario["annual_powered_hours"]))),
            "annual_energy_cost_usd": str(cents(annual_energy)),
            "annual_maintenance_usd": str(cents(annual_maintenance)),
            "annual_other_cost_usd": str(cents(annual_other)),
            "terminal_buyout_usd": str(cents(buyout)),
            "terminal_residual_credit_usd": str(cents(residual)),
        }
        cashflows = [initial] + [recurring for _ in range(years)]
        cashflows[-1] += cents(buyout) - cents(residual)
    else:
        billed_hours = integer(scenario["annual_billed_instance_hours"], "annual_billed_instance_hours")
        compute = cloud_compute_cost_usd(cloud_rate, billed_hours)
        initial = cents(upfront)
        recurring = cents(compute + annual_other)
        components = {
            "upfront_usd": str(cents(upfront)),
            "annual_billed_instance_hours": billed_hours,
            "market_instance_price_usd_per_hour": str(cloud_rate),
            "annual_compute_cost_usd": str(cents(compute)),
            "annual_other_cost_usd": str(cents(annual_other)),
            "annual_energy_cost_usd": None,
            "terminal_residual_credit_usd": "0.00",
        }
        cashflows = [initial] + [recurring for _ in range(years)]

    return cashflows, {
        "id": scenario["id"],
        "strategy": strategy,
        "market": scenario.get("market", "synthetic classroom case"),
        "quote_status": scenario["quote_status"],
        "annual_deliverables_assumed": annual_deliverables,
        "total_deliverables_assumed": annual_deliverables * years,
        "components": components,
        "cashflows_year_0_to_horizon_usd": [str(cents(value)) for value in cashflows],
    }


def build_results(fixture: Any, fixture_bytes: bytes) -> dict[str, Any]:
    data = validate_fixture(fixture)
    assumptions = data["assumptions"]
    horizon = int(assumptions["horizon_years"])
    discount = nonnegative(assumptions["annual_discount_rate"], "annual_discount_rate")
    energy_rate = nonnegative(data["market_snapshot"]["electricity"]["price_usd_per_kwh"], "electricity price")
    cloud_rate = nonnegative(data["market_snapshot"]["cloud_compute"]["price_usd_per_instance_hour"], "cloud price")
    scenarios_out = []
    for scenario in data["scenarios"]:
        flows, details = _scenario_cashflows(scenario, horizon, energy_rate, cloud_rate)
        nominal = sum(flows, ZERO)
        npv_value = net_present_value(flows, discount)
        outputs = details["total_deliverables_assumed"]
        details.update({
            "nominal_tco_usd": str(cents(nominal)),
            "npv_tco_usd": str(cents(npv_value)),
            "npv_cost_per_synthetic_deliverable_usd": str(cents(npv_value / Decimal(outputs))),
        })
        scenarios_out.append(details)
    return {
        "result_schema_version": 1,
        "fixture_id": data["fixture_id"],
        "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "python_version": ".".join(map(str, sys.version_info[:3])),
        "currency": "USD",
        "horizon_years": horizon,
        "annual_discount_rate": str(discount),
        "cashflow_timing": "initial cost at year 0; recurring costs at year end; residual/buyout at horizon; yearly cashflows rounded to cents",
        "market_snapshot": data["market_snapshot"],
        "scenarios": scenarios_out,
        "comparison_status": {
            "performance_parity_measured": False,
            "synthetic_deliverables_are_not_benchmarks": True,
            "purchase_and_lease_amounts_are_vendor_quotes": False,
            "prices_escalated": False,
            "taxes_and_financing_costs_included": False,
            "complete_invoice_or_cost_estimate": False,
        },
        "limitations": [
            "Purchase and lease amounts and annual usage are synthetic assumptions, not offers or market quotes.",
            "The dated cloud list price is one US region snapshot; it is not an all-in invoice or future price guarantee.",
            "The Texas commercial electricity value is a statewide average, not a Dallas customer tariff or marginal bill rate.",
            "Equal synthetic deliverables do not demonstrate equal throughput, quality, availability, or workload suitability.",
            "Taxes, financing, inflation, escalation, demand charges, depreciation rules, downtime, labor, replacement, and all charges not explicit in the fixture are excluded.",
        ],
    }


def load_and_run(fixture_path: Path) -> dict[str, Any]:
    raw = fixture_path.read_bytes()
    try:
        fixture = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise BudgetInputError(f"cannot parse fixture: {error}") from error
    return build_results(fixture, raw)


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate a synthetic three-way compute TCO illustration")
    parser.add_argument("--fixture", type=Path, default=ROOT / "sample_budget.json")
    parser.add_argument("--output", type=Path, help="write deterministic JSON results instead of stdout")
    args = parser.parse_args()
    try:
        result = load_and_run(args.fixture)
    except (OSError, BudgetInputError) as error:
        parser.error(str(error))
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
```
