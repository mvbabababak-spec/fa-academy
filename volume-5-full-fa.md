# هنر و علم ساخت هوش — جلد پنجم

**The Art & Science of Building Intelligence | Babak & Ai**

وضعیت: ۱۲ فصل در نقشه؛ ۵ فصل تا این انتشار نگارش و آزموده شده‌اند. این فایل Markdown است؛ PDF و EPUB تولید و آزموده نشده‌اند.

## فهرست فصل‌های منتشرشده

- فصل ۱ (سراسری ۶۲) — Benchmarking، طراحی آزمون، معیارها، ارزیابی انسانی، عدم‌قطعیت و آلودگی بنچمارک
- فصل ۲ (سراسری ۶۳) — توهم، سوگیری، استحکام، تبیین‌پذیری و تفسیرپذیری
- فصل ۳ (سراسری ۶۴) — Red Teaming، حملات خصمانه، Prompt Injection، مسموم‌سازی داده، استخراج مدل و حریم خصوصی
- فصل ۴ (سراسری ۶۵) — هم‌ترازی، حاکمیت، مستندسازی، مدل‌کارت، داده‌کارت و مدیریت ریسک
- فصل ۵ (سراسری ۶۶) — API و FastAPI، Backend، Frontend، برنامهٔ وب و موبایل؛ قرارداد داده و آزمایش

---

# جلد پنجم، فصل ۱ — Benchmarking، طراحی آزمون و ارزیابی

**نگاشت:** فصل محلی ۱ جلد پنجم = فصل سراسری ۶۲. **تاریخ بازبینی منابع: ۷ نوامبر ۲۰۲۶.** فصل ۶۱ کارایی runtime، مسیر استنتاج و اندازه‌گیری‌های وابسته به workload را پوشش داد؛ این فصل روی کیفیت کارِ تعریف‌شده، طراحی آزمون، سنجه، ارزیابی انسانی، عدم‌قطعیت و خطر آلودگی بنچمارک تمرکز می‌کند. فصل ۶۳ به توهم، سوگیری، استحکام و تبیین‌پذیری می‌پردازد؛ فصل ۶۴ آزمون خصمانه و امنیت را ادامه می‌دهد و فصل ۶۵ حکمرانی و مدیریت ریسک را جمع‌بندی می‌کند. این فصل نه ممیزی جامع ایمنی است، نه معیار نهایی برای انتخاب محصول و نه جایگزین طرح پژوهشی فصل‌های ۷۰ و ۷۱.

**پیش‌نیاز:** تمایز دادهٔ آموزش، اعتبارسنجی و آزمون؛ آشنایی مقدماتی با دسته‌بندی، احتمال، prompt و نسخه‌بندی آزمایش. **خروجی:** بتوانید ادعای قابل‌آزمون را به سناریو و مجموعه‌داده تبدیل کنید، سنجه و مقایسهٔ منصفانه برگزینید، عدم‌قطعیت و توافق ارزیابان را با محدودیت مناسب گزارش کنید، و دربارهٔ آلودگی بنچمارک ادعایی متناسب با شواهد بنویسید.

![شکل ۵-۱-۱ — زنجیرهٔ ارزیابی از ادعای محدود و جمعیتِ هدف، به سناریو و نمونه‌گیری، اجرای نسخه‌مند، سنجش و گزارش می‌رسد؛ هر پیکان یک وابستگی است و شکست در تعریف سناریو، نمونه‌گیری یا scorer می‌تواند تفسیر امتیاز نهایی را تغییر دهد. خروجی مسیر، شواهدی برای همان پروتکل است، نه تضمین کیفیت کلی، نبود آلودگی یا ایمنی محصول. نمودار مفهومی است و معنا به رنگ وابسته نیست.](book-engineering/diagrams/v5-ch01-evaluation-protocol.svg)

**شکل ۵-۱-۱ —** عدد پایانی جدا از قراردادهای پیش از آن معنا ندارد: باید دانست چه کسی، روی چه کار و نمونه‌ای، با کدام نسخه و روش امتیازدهی سنجیده شده است.

## ۱. یک امتیاز دقیقاً از چه ادعایی پشتیبانی می‌کند؟

گزارش «مدل الف ۸۷ امتیاز گرفت» هنوز نمی‌گوید ۸۷ از چه چیزی، روی کدام نمونه، در چه شرایطی، با چه خطایی و برای کدام تصمیم به‌دست آمده است. امتیاز نتیجهٔ یک زنجیره است: تعریف کار، جمعیت و سناریو؛ انتخاب و برچسب‌گذاری نمونه؛ آماده‌سازی ورودی؛ نسخهٔ مدل و تنظیمات اجرا؛ تعریف سنجه و scorer؛ تحلیل آماری؛ و تفسیر محدود نتیجه. هر جزء می‌تواند مقایسه را عوض کند.

پرسش درست معمولاً «کدام مدل بهتر است؟» نیست؛ «برای این جمعیت و این کاربرد، روی این رفتارِ ازپیش‌تعریف‌شده، در شرایط X و با معیار Y، آیا گزینهٔ الف از baseline به‌اندازهٔ معناداری بهتر است؟» است. بهتر است پیش از اجرا یک جملهٔ ادعا، پیامد تصمیم اشتباه و شرطی را که نتیجه را باطل می‌کند بنویسید.

## ۲. Benchmark، metric و پروتکل را یکی نگیرید

**بنچمارک (benchmark)** بسته‌ای نسخه‌مند از taskها، داده یا سناریوها، قرارداد اجرا، روش امتیازدهی و مستندات است. **سنجه (metric)** قاعده‌ای است که خروجی‌ها را به کمیت قابل‌گزارش تبدیل می‌کند. **پروتکل ارزیابی** می‌گوید چه نمونه‌هایی، با کدام مدل و ورودی، چه تنظیمات، چه ارزیاب، چه تصادفی‌سازی و چه تحلیل آماری استفاده می‌شوند. **نتیجه** یک مشاهده تحت همان ترکیب است؛ نتیجه به‌تنهایی ویژگی ثابت و عمومی مدل نیست.

دو تیم ممکن است نام یک سنجه را یکسان به‌کار ببرند، اما prompt، نسخهٔ test set، نحوهٔ شکست خروجی، parsing یا روش تجمیع آن‌ها فرق کند. در این حالت، مقایسهٔ عددها الزاماً مقایسهٔ هم‌شرط نیست. بنابراین نسخهٔ داده، کد scorer، prompt، تنظیم تولید و تصمیم‌های حذف/اصلاح باید شناسه‌دار و قابل‌ردیابی باشند.

## ۳. تصمیم را پیش از ساختن آزمون تعریف کنید

ابتدا مشخص کنید نتیجه قرار است از کدام تصمیم پشتیبانی کند: انتخاب میان دو checkpoint، پذیرش تغییر یک سامانه، شناسایی یک شکاف زبانی یا بررسی یک ادعای علمی. جمعیتِ کاربر، محیط، خطر خطا، زبان و پیامد false positive و false negative را بنویسید. یک بنچمارک عمومی نمی‌تواند همهٔ این تصمیم‌ها را هم‌زمان نمایندگی کند.

پروتکل خوب ادعا را محدود می‌کند. اگر نمونه‌ها پرسش‌های کوتاه و ساختگی‌اند، نتیجه دربارهٔ همان پرسش‌هاست؛ اگر فقط زبان انگلیسی آزموده شده، از آن نمی‌توان کیفیت فارسی را نتیجه گرفت. اگر خروجی یک endpoint بیرونی است، نسخهٔ دقیق سرویس و زمان درخواست ثبت شود، چون نسخهٔ مدل ممکن است بدون هشدار تغییر کند. سنجهٔ کارایی سرو و تأخیر را با کیفیت task مخلوط نکنید؛ فصل ۶۱ آن شاخهٔ اندازه‌گیری را جداگانه بررسی کرد.

## ۴. سازهٔ موردنظر را عملیاتی کنید

گاهی چیزی که می‌خواهیم بسنجیم مستقیماً مشاهده‌پذیر نیست: «مفیدبودن»، «استدلال»، «درستی»، «بی‌طرفی» یا «کیفیت پاسخ» سازه‌اند. باید آن‌ها را به رفتارها و برچسب‌های قابل‌بررسی تبدیل کرد. برای نمونه، «درستی پاسخ» ممکن است در پرسش حسابی با جواب مرجع سنجیده شود؛ در پاسخ باز، به rubric، منابع و داوری انسانی نیاز داشته باشد. exact match برای پارافرایز درست ممکن است ناعادلانه باشد، و شباهت متنی برای پاسخِ روان اما نادرست امتیاز بسازد.

یک زنجیرهٔ اعتبار بسازید: تعریف سازه ← نشانهٔ مشاهده‌پذیر ← روش ثبت/برچسب‌گذاری ← سنجه ← تصمیم. سپس نمونه‌هایی را بررسی کنید که سنجه در آن‌ها موفق یا شکست می‌خورد. وجود کد، عدد اعشاری و نمودار اعتبار سازه را تضمین نمی‌کند. [HELM](https://arxiv.org/abs/2211.09110) نشان می‌دهد که سناریوها و مطلوبیت‌ها متعددند و سنجش چندمعیاره trade-offهایی را آشکار می‌کند که یک accuracy تنها پنهان می‌سازد.

## ۵. پوشش سناریو را به‌صورت ماتریس طراحی کنید

پیش از گردآوری، محورهای مرتبط را فهرست کنید: نوع task، دشواری، دامنهٔ موضوعی، زبان و گونهٔ زبانی، طول ورودی، منبع و زمان داده، شکل تعامل، گروه کاربر، نوع خطا و حساسیت پیامد. لازم نیست همهٔ خانه‌های ماتریس هم‌اندازه باشند؛ لازم است پوشش واقعی و جاهای خالی آشکار بمانند. اگر سهم داده از هر خانه نامتوازن است، وزن‌دهی یا گزارش تفکیکی را پیشاپیش تعریف کنید.

| محور | پرسش طراحی | آنچه باید گزارش شود |
|---|---|---|
| کار و دامنه | آیا نمونه‌ها همان تصمیم واقعی را بازنمایی می‌کنند؟ | تعریف inclusion/exclusion و موارد خارج از دامنه |
| زبان و جمعیت | کدام زبان، گویش یا گروه کم‌نماینده است؟ | شمار نمونه، روش جذب و محدودیت پوشش |
| دشواری و پیامد | آیا خطاها هزینهٔ یکسان دارند؟ | strata دشواری و وزن/هزینهٔ ازپیش‌تعریف‌شده |
| زمان و منبع | آیا نمونه پس از تاریخ آموزش منتشر شده است؟ | تاریخ، منبع، مجوز و عدم‌قطعیت provenance |
| تعامل | تک‌نوبتی است یا گفت‌وگوی چندمرحله‌ای؟ | تاریخچه، حافظه، ابزار و قواعد توقف |

همهٔ میانگین‌ها را کنار گروه‌های کوچک‌تر بخوانید؛ یک میانگین کل می‌تواند افت شدید در یک زبان یا نوع خطا را پنهان کند. نمایش یک رادارچارت یا leader board به‌تنهایی پوشش را اثبات نمی‌کند. هر نتیجه را با تعداد نمونه و پراکندگی آن همراه کنید.

## ۶. مجموعه‌داده و split را طوری بسازید که آزمون واقعاً تازه بماند

رکوردها را تنها بر اساس ردیف تصادفی تقسیم نکنید، اگر چند سؤال از یک سند، کاربر، مکالمه، قالب، منبع یا خانوادهٔ پارافرایز آمده‌اند. ابتدا **گروه وابستگی** را تعریف کنید؛ سپس گروه‌ها را میان train، validation و test جدا کنید. در غیر این صورت، یک نمونه می‌تواند در train و نسخه‌ای تقریباً یکسان در test باشد و عملکرد تعمیمی را بیش‌برآورد کند.

Validation برای انتخاب prompt، threshold و checkpoint مصرف می‌شود؛ test نهایی را برای همان انتخاب‌ها به‌کار نبرید. اگر test را بارها می‌خوانید و بر اساس آن تغییر می‌دهید، به‌تدریج بخشی از فرایند توسعه شده است؛ این استفاده را ثبت کنید و برای تصمیم نهایی دادهٔ تازه یا ارزیابی تأییدی کنار بگذارید. دادهٔ کلیددار هم خطر را صفر نمی‌کند، اما دامنهٔ دسترسی را محدود می‌سازد.

برای هر ردیف، شناسهٔ پایدار، منبع یا توضیح منشأ، گروه وابستگی، split، برچسب، شیوهٔ برچسب‌گذاری و نسخهٔ schema ثبت کنید. مجوز، رضایت، دادهٔ شخصی و سیاست نگهداری را در طراحی وارد کنید؛ این‌ها بعداً با یک hash جایگزین نمی‌شوند.

## ۷. Baseline و مقایسهٔ منصفانه بسازید

Baseline باید پیش از دیدن test انتخاب شود و برای تصمیم شما معنا داشته باشد: روش ساده، مدل مرجع، نسخهٔ پیشین یا یک قاعدهٔ انسانی. اگر مقایسهٔ انسان و مدل می‌کنید، ابزار، زمان، منابع در دسترس، دستورالعمل و آشنایی با task را هم‌تراز کنید. baseline انسانی «سقف ممکن» نیست و اختلاف با آن به‌تنهایی نمی‌گوید مدل برای مصرف واقعی مناسب است.

گزینه‌ها را روی همان نمونه‌ها و شرایط اجرا کنید؛ تفاوت prompt یا بودجهٔ محاسبه را ثبت کنید. اجرای تکراری با seedهای متعدد مفید است اگر تصادفی‌بودن تولید بخشی از رفتار باشد؛ اما انتخاب بهترین run از میان تعداد زیادی تلاش، برآورد را خوش‌بینانه می‌کند. همهٔ runهای برنامه‌ریزی‌شده و قواعد انتخاب را گزارش کنید.

## ۸. سنجه را از نوع کار و خطا انتخاب کنید

برای دسته‌بندی نامتوازن، accuracy به‌تنهایی ممکن است مدلِ همیشه‌مثبت را موفق نشان دهد. precision می‌پرسد از پیش‌بینی‌های مثبت چند مورد درست بوده‌اند؛ recall می‌پرسد از موارد مثبت چند مورد پیدا شده‌اند؛ F1 میان precision و recall مصالحه می‌کند. macro-F1 به هر کلاس وزن برابر می‌دهد، درحالی‌که micro و weighted رفتار دیگری دارند. پیش از گزارش، تعریف هرکدام و برچسب‌های حاضر را ذکر کنید.

برای تولید آزاد، exact match، معیارهای هم‌پوشانی واژگانی، شباهت معنایی، داوری انسانی یا آزمونِ اجرای کد هرکدام خطاهای متفاوتی دارند. در ترجمه، خلاصه‌سازی، پاسخ factual و تکمیل کد یک scorer واحد را بی‌دلیل به همه تعمیم ندهید. برای امتناع یا abstention، هم **coverage** و هم خطر خطا در میان پاسخ‌های پذیرفته‌شده را بسنجید؛ سامانه‌ای که به همهٔ درخواست‌ها «نمی‌دانم» می‌گوید شاید خطای کمتری داشته باشد، اما کار را هم انجام نداده است.

Calibration، Brier score یا expected calibration error می‌توانند دربارهٔ رابطهٔ confidence و درستی اطلاعات بدهند، اما به bucket، تعداد نمونه و تعریف confidence حساس‌اند. برای چند سنجه یک امتیاز ترکیبی نسازید مگر وزن‌ها، هدف تصمیم و تحلیل حساسیت آن‌ها را صریح اعلام کنید. مدلِ بهتر بر حسب یک معیار لزوماً در معیار یا زیرگروه دیگر بهتر نیست.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="دقت برابر است با تعداد پیش‌بینی‌های درست تقسیم بر تعداد کل نمونه‌های سنجیده‌شده">
  <mrow><mi>Accuracy</mi><mo>=</mo><mfrac><mrow><mi>تعداد پیش‌بینی‌های درست</mi></mrow><mrow><mi>تعداد کل نمونه‌ها</mi></mrow></mfrac></mrow>
</math>

**متن جایگزین فرمول:** دقت، تعداد پیش‌بینی‌های درست تقسیم بر تعداد کل نمونه‌های سنجیده‌شده است.

## ۹. سنجه نیز می‌تواند خطا کند

در دادهٔ نامتوازن، metric کلی وزن کلاس‌ها را طبق فرمول خودش می‌دهد؛ این الزاماً با هزینهٔ واقعی تصمیم یکی نیست. threshold را با نگاه به test تعیین نکنید. اگر scorer پاسخ ناقص، قالب متفاوت یا خطای parsing را حذف می‌کند، دقیقاً همان رفتار را مستند کنید و تعداد نمونه‌های حذف‌شده را گزارش دهید.

سنجه را در چند نمونه به‌صورت دستی ممیزی کنید: بهترین امتیاز اما پاسخ غلط؛ امتیاز کم اما پاسخ قابل‌قبول؛ و مواردی که rubric در آن‌ها مبهم است. وقتی مدل یا تیم scorer را بهینه می‌کند، رفتار می‌تواند به‌سمت آنچه metric پاداش می‌دهد تغییر کند، نه لزوماً هدف واقعی. یک معیار اولیهٔ ازپیش‌ثبت‌شده و چند سنجهٔ مکمل، همراه با تحلیل خطا، این خطر را کاهش می‌دهد؛ حذف نمی‌کند.

## ۱۰. عدم‌قطعیت را به منبع آن تفکیک کنید

فاصلهٔ اطمینان فقط یک نوع عدم‌قطعیت را خلاصه می‌کند. نوسان ناشی از نمونه‌گیری با تغییر prompt، seed، ارزیاب، روز اجرا، نسخهٔ API یا scorer یکی نیست. اگر داده خوشه‌ای است، چند ردیف یک سند یا یک کاربر را نمونه‌های مستقل فرض نکنید. اگر benchmark تنها یک بار اجرا شده، از عدد دقیق اعشار برای القای قطعیت استفاده نکنید.

برای نسبت دودویی می‌توان فاصلهٔ Wilson را به‌جای تقریب نرمال ساده گزارش کرد؛ آن هم فقط با ذکر اندازهٔ نمونه و فرض نمونه‌گیری. برای اختلاف دو مدل روی ورودی‌های متناظر، resampling یا آزمون باید جفت‌بودن را حفظ کند؛ اگر چند پرسش از یک گروه آمده، گروه را واحد نمونه‌گیری قرار دهید. فاصلهٔ باریک به‌تنهایی bias یا خطای برچسب را پوشش نمی‌دهد.

در پژوهش NLP، آزمون آماری باید با نوع metric، واحد نمونه‌گیری و طراحی جفت‌شده سازگار باشد؛ مرور [Dror و همکاران](https://aclanthology.org/P18-1128/) به همین انتخاب وابسته به ساختار task می‌پردازد. مقدار `p` نه اندازهٔ اثر است، نه احتمال درست‌بودن مدل و نه گواه اهمیت عملی. نتیجه را با اندازهٔ اثر، فاصلهٔ عدم‌قطعیت و هزینهٔ خطا بخوانید.

## ۱۱. مقایسهٔ جفت‌شده، اندازهٔ اثر و چندین آزمون

اگر دو مدل روی همان test اجرا شده‌اند، اختلاف موردی را نگه دارید: کدام ورودی را مدل الف درست کرد و مدل ب نه، و برعکس؟ برای اختلاف accuracy می‌توان bootstrap جفت‌شده یا permutation test به‌کار برد؛ واحد resampling باید متناسب با استقلال داده باشد. آزمون مستقل روی دو فهرست که در واقع همان ورودی‌ها را دارند ساختار مقایسه را دور می‌ریزد.

پیش از اجرا، metric اصلی، جهت مطلوب، زیرگروه‌های تأییدی و اثرِ کمینهٔ مهم را تعیین کنید. آزمودن ده‌ها معیار و انتخاب تنها نتیجهٔ مطلوب خطر false discovery دارد؛ اصلاح چندمقایسه‌ای یا اعلام اکتشافی‌بودن تحلیل را در نظر بگیرید. «معنادار آماری» با «به‌اندازهٔ کافی مفید برای انتشار» یکی نیست.

## ۱۲. توان آماری و اندازهٔ نمونه را پیشاپیش بسنجید

نمونهٔ کافی به نرخ پایه، اندازهٔ اثر مورد انتظار، پراکندگی بین گروه‌ها، وابستگی نمونه‌ها و هزینهٔ خطای نوع اول و دوم بستگی دارد. چند نمونهٔ pilot برای برآورد و طراحی مفیدند، اما اگر با همان داده نتیجهٔ نهایی را انتخاب و گزارش کنید، آن‌ها دیگر آزمون مستقل نیستند. اگر توان مناسب شدنی نیست، مطالعه را اکتشافی بنامید و فاصله‌ها را صادقانه نشان دهید.

در آزمون انسانی، تعداد رأی‌ها با تعداد نمونهٔ مستقل یکی نیست: سه ارزیاب برای یک پاسخ، سه مشاهدهٔ مستقل از جمعیت کاربردی نمی‌سازند. باید هم شمار نمونه‌ها، هم شمار ارزیابان، هم خوشه‌بندی و هم روش جذب را گزارش کرد.

## ۱۳. ارزیابی انسانی را به پروتکل تبدیل کنید

برای هر rubic یا مقیاس، معیارهای «قبول»، «مرزی» و «رد» را با مثال و مرز تصمیم تعریف کنید. ارزیابان را با نمونهٔ آموزشی آشنا کنید؛ ترتیب پاسخ‌ها را تصادفی کنید؛ در مقایسهٔ A/B نام مدل را پنهان کنید؛ تعداد نوبت‌ها و امکان استفاده از ابزار را ثابت نگه دارید؛ و اختلاف نظر را حذف نکنید. پاسخ‌های نادرستِ قانع‌کننده یا زیان‌بار را جداگانه تحلیل کنید.

طراحی نمونه و ارزیاب باید با جمعیتِ مورد ادعا سازگار باشد. اگر کیفیت فارسی یا تجربهٔ یک گروه خاص مهم است، ارزیابی را تنها به ارزیابان مسلط به زبانی دیگر یا یک گروه جمعیتی محدود نکنید. دستورالعمل، معیار جذب، آموزش، جبران خدمت، رضایت آگاهانه، محافظت از دادهٔ حساس، بار کاری و روش حل اختلاف را از ابتدا برنامه‌ریزی کنید.

گزارش کنید چه تعداد ارزیاب و نمونه داشتید، چند برچسب گم شد، نمونه‌های اختلافی چگونه رسیدگی شدند، و rubric چه revisionی داشت. توافق بالا ثابت نمی‌کند برچسب درست یا سازه معتبر است؛ اختلاف پایین نیز ممکن است از دستورالعمل روشن یا از برچسب‌گذاری سطحی ناشی شود. مقالهٔ [James (LREC 2026)](https://aclanthology.org/2026.lrec-1.347/) انتخاب سنجهٔ توافق را وابسته به نوع وظیفه می‌داند و بر عدم‌توازن، دادهٔ گمشده، فاصلهٔ اطمینان و تحلیل الگوی اختلاف تأکید می‌کند.

## ۱۴. ضریب توافق را بی‌توضیح به کار نبرید

درصد توافق خام، Cohen’s kappa، Krippendorff’s alpha و ICC فرض‌ها و نوع دادهٔ متفاوتی دارند. انتخاب به تعداد ارزیاب، اسمی/ترتیبی/پیوسته بودن نمره، دادهٔ گمشده، طرح نمونه و نامتوازن‌بودن برچسب‌ها بستگی دارد. برای مثال، یک درصد توافق بالا ممکن است در داده‌ای که تقریباً همه برچسب‌ها «قبول» است، بدون دیدن توزیع گمراه‌کننده باشد.

هم مقدار و فاصلهٔ عدم‌قطعیت، هم شمار برچسب هر کلاس، هم توزیع اختلاف را گزارش کنید. اگر توافق را برای پالایش rubric استفاده می‌کنید، نسخهٔ دستورالعمل را ثبت کنید و نتیجهٔ پیش و پس از بازآموزی را جدا نگه دارید. ضریب واحد را به «کیفیت داوری» یا «درستی حقیقت» تبدیل نکنید.

## ۱۵. LLM-as-a-judge یک ابزار اندازه‌گیریِ نیازمند کالیبراسیون است

مدل داور می‌تواند حجم زیادی از خروجی را غربال کند، اما خود یک مدل و یک پروتکل دیگر است. نام و revision مدل داور، prompt، ترتیب گزینه‌ها، decoding، rubric، زبان، قالب خروجی و قواعد retry را نسخه‌مند کنید. روی زیرمجموعه‌ای با داوری انسانیِ کور، توافق و نمونه‌های اختلاف را بسنجید.

مطالعهٔ [MT-Bench و Chatbot Arena](https://arxiv.org/abs/2306.05685) در تنظیم‌های خودش سوگیری جایگاه، طول پاسخ و ترجیح پاسخ هم‌خانواده را بررسی می‌کند. این مطالعه مجوزی برای فرض توافق عمومی یا جایگزینی ارزیاب انسانی نیست. گزینه‌ها را جابه‌جا کنید، پاسخ کوتاه و بلند را با معیار یکسان بسنجید، نام مدل را از داور پنهان کنید و پاسخ‌های مرجعِ مصنوعی را از داوریِ ادعای factual جدا کنید.

اگر داور مدل به شواهد بیرونی نیاز دارد، منبع و زمان دسترسی را ثبت کنید. خروجی‌های مبهم، امتناع یا format error را silent drop نکنید. برآورد توافق روی زیرمجموعهٔ انتخاب‌شده را به کل توزیع تعمیم ندهید مگر طرح نمونه‌گیری این تعمیم را پشتیبانی کند.

## ۱۶. آلودگی بنچمارک فقط «پیداشدن رشتهٔ برابر» نیست

**آلودگی (contamination)** وقتی نگران‌کننده است که اطلاعاتی از ارزیابی در دادهٔ آموزش، تنظیم، انتخاب مدل، prompt engineering یا فرایندی که ادعای test نهایی به آن متکی است، وارد شود و برآورد را خوش‌بینانه کند. شکل‌های احتمالی شامل متن دقیق، پارافرایز، پاسخ یا تست عمومی، نسخهٔ مشتق‌شده، و انتخاب مکرر روی test است. دسترسی به سؤال عمومی با اثباتِ استفادهٔ آن در وزن‌های یک checkpoint برابر نیست؛ برعکس، نبود تطابق دقیق هم نبود هرگونه مواجهه را ثابت نمی‌کند.

ثبت منشأ داده، تاریخ انتشار، snapshot مجموعه، cutoff اعلام‌شدهٔ آموزش و نسخهٔ checkpoint شواهد مهم‌اند، اما metadata ممکن است ناقص باشد. بررسی n-gram، شباهت معنایی، جست‌وجوی retrieval، آزمون عضویت یا سؤال‌های تازه هرکدام فرض‌هایی دارند. [Fu و همکاران](https://arxiv.org/abs/2410.18966) نشان می‌دهند روش‌های تشخیص بر فرض‌هایی متکی‌اند که در همهٔ وضعیت‌ها برقرار نیستند؛ در مطالعهٔ آن‌ها بعضی روش‌های membership inference به عملکرد نزدیک حد تصادفی رسیدند. پس یک ابزار overlap را گواه «پاک‌بودن» یا «آلودگی قطعی» نخوانید.

گزارش شواهد را درجه‌بندی کنید: «موردِ هم‌پوشانی در منبع قابل‌دسترسی پیدا شد»؛ «این روش جست‌وجو پرچمی نداد»؛ «provenance کافی برای نتیجه‌گیری نداریم». روش جست‌وجو، threshold، corpus قابل‌دسترسی و محدودهٔ ناشناخته را شرح دهید. [Chunyuan Deng و همکاران، «Investigating Data Contamination in Modern Benchmarks for Large Language Models»](https://aclanthology.org/2024.naacl-long.482/) retrieval و probeهای test-set را به‌عنوان راه بررسی احتمالی مطرح می‌کنند، نه اثبات قطعی منشأ. مرور [Chen و همکاران، EMNLP 2025](https://aclanthology.org/2025.emnlp-main.511/) مصالحهٔ بنچمارک ایستا و پویا را بررسی می‌کند و خلأ معیارهای استاندارد برای آزمون‌های پویا را نیز برجسته می‌سازد.

## ۱۷. آزمون ایستا، آزمون زمان‌مند و هزینهٔ مقایسه‌پذیری

بنچمارک ایستا تکرارپذیری و مقایسهٔ تاریخی را ساده می‌کند، اما عمومی‌شدن آن احتمال مواجهه، بهینه‌سازی مستقیم روی leaderboard یا حفظ پاسخ‌ها در گردش کار را بالا می‌برد. آزمون پویا سؤال‌های تازه یا بازه‌های انتشار زمانی را وارد می‌کند؛ اما بدون snapshot، نسخه و پروتکل ثابت، مقایسهٔ مدل‌ها می‌تواند مخدوش شود.

[LiveCodeBench](https://livecodebench.github.io/) نمونه‌ای از ثبت تاریخ انتشار مسئله و ارزیابی پیوسته در وظایف کدنویسی است. تازه‌بودنِ زمان‌مند می‌تواند ریسک مواجههٔ پیشین را کاهش دهد؛ تضمینِ نبود آن نیست. برای هر snapshot پویا، شناسهٔ task، تاریخ قطع، scorer، تغییرات و قاعدهٔ بازتولید نتیجه را منتشر کنید، مگر محدودیت حقوقی یا خطر سوءاستفاده انتشار را نامناسب کند.

## ۱۸. گزارش بازتولیدپذیر چه چیزهایی را ثبت می‌کند؟

| جزء | حداقل اطلاعات لازم |
|---|---|
| ادعا و جمعیت | تصمیم، کار، دامنه و موارد خارج از ادعا |
| داده | نسخه، منبع، split، گروه وابستگی، برچسب و hash |
| مدل و اجرا | شناسهٔ checkpoint/API، تاریخ، prompt، ابزار و decoding |
| scorer | کد و نسخه، قواعد parse، metric و موارد حذف‌شده |
| ارزیابی انسانی | rubric، تعداد، جذب، کورسازی، توافق و اختلاف |
| تحلیل | metric اصلی، واحد نمونه‌گیری، فاصله/آزمون و چندمقایسه‌ای |
| محدودیت | پوشش جاافتاده، آلودگی احتمالی و عدم‌قطعیت provenance |

Hash به بازشناسی بایت‌های همان فایل کمک می‌کند؛ درستی، مجوز، بی‌خطر بودن یا نبود دادهٔ شخصی را اثبات نمی‌کند. نسخهٔ داده را بدون افشای محتوای محدود یا حساس شناسه‌دار کنید. اگر نتایج را بازتولیدناپذیر می‌کند، دلیل و artefact جایگزین را ثبت کنید.

## ۱۹. مثال عددیِ ساختگی: چرا «۸۳٫۳٪» کافی نیست؟

آزمایشگاه همراه فصل شش مورد test در سه گروه ساختگی دارد. در همین fixture، baseline چهار مورد از شش مورد را درست می‌کند و گزینهٔ دوم پنج مورد را: اختلاف مشاهده‌شده یک ششم، حدود ۱۶٫۷ واحد درصد است. فاصلهٔ Wilsonِ محاسبه‌شده برای baseline حدود ۰٫۳۰ تا ۰٫۹۰ و برای گزینهٔ دوم حدود ۰٫۴۴ تا ۰٫۹۷ است؛ این فاصله‌ها استقلال نمونه‌ها را فرض می‌کنند و اثر خوشه‌بندی را لحاظ نمی‌کنند. bootstrap خوشه‌ای با تنها سه گروه، در اجرای seed=۶۲ بازهٔ صدکی ۹۵٪ از −۰٫۵ تا ۰٫۵ و سهم اختلاف مثبت ۷۴٫۶۵٪ را داد. این تعداد و بازه برای نتیجه‌گیری دربارهٔ برتری پایدار یا توان کافی نیست.

فایل رأی‌گیری شامل رأی‌های فرضی و دست‌ساز است: ۱۲ توافق جفتی از ۱۸ مقایسه، یعنی ۶۶٫۷٪ توافق خام. هیچ انسانی آن را برچسب نزده است؛ این عدد فقط کنترل محاسبه است. یک prompt با corpus ساختگی هم‌پوشانی دقیق دارد و به‌عنوان سرنخ بازبینی علامت می‌خورد؛ نه آنکه آموزش مدل بر آن ثابت شود. هش‌ها، محیط و محدودیت‌ها در `results.json` ثبت شده‌اند.

این مثال به‌عمد کوچک است تا مسیر محاسبه خوانا بماند، نه برای نمایش روش مطالعهٔ واقعی. برای ادعای تجربی باید نمونهٔ نماینده، طراحی توان‌مند، برچسب معتبر، دادهٔ مستقل و روش آماری سازگار داشت.

## ۲۰. پروژهٔ فصل: ممیزی یک پروتکل کوچک

در `book-engineering/projects/62-evaluation-lab/` برنامه‌ای کتابخانه‌استاندارد schema را بررسی می‌کند، نشت group میان splitها را رد می‌کند، metricهای دوکلاسه و فاصلهٔ Wilson را می‌سازد، اختلاف جفت‌شده را با resampling گروهی خلاصه می‌کند، توافق خام را با مخرج گزارش می‌دهد و هم‌پوشانی را فقط برای بازبینی پرچم می‌زند. پیش از اجرا، سطرهای JSONL و سه فایل fixture را بخوانید و مطمئن شوید همه ساختگی‌اند.

آزمون‌ها را با `python -m unittest -v` و گزارش مرجع را با `python evaluation_lab.py --output results.json` بازتولید کنید. برنامهٔ اصلی خود را حفظ می‌کند؛ برای آزمایش تغییر، مسیر خروجی موقت بدهید. نتیجهٔ CLI را کنار hash ورودی، نسخهٔ Python و محدودیت‌ها نگه دارید.

## ۲۱. خطاهای رایج در گزارش بنچمارک

- اعلام «بهترین مدل» از یک میانگین بدون جمعیت، نسخه، تعداد نمونه و فاصلهٔ عدم‌قطعیت.
- گزینش metric، prompt یا threshold پس از دیدن test و سپس معرفی همان test به‌عنوان ارزیابی مستقل.
- مخلوط‌کردن داده‌های وابسته در splitهای مختلف یا فرض استقلال چند پرسش از یک سند.
- گزارش accuracy در کلاس نامتوازن، بدون precision/recall و ماتریس خطا.
- انتخاب آزمون آماری صرفاً بر اساس این‌که نتیجهٔ مطلوب بدهد، نه ساختار جفت‌شده و خوشه‌ای.
- معرفی توافق LLM-as-a-judge یا ارزیاب انسانی به‌عنوان حقیقتِ بی‌خطا.
- ادعای «آلودگی ندارد» به‌دلیل نبود تطابق دقیق یا «آلوده است» به‌دلیل یک شباهت سطحی.
- تبدیل آزمون شش نمونهٔ ساختگی به ادعای کیفیت زبان، کاربرد، کارایی یا ایمنی.

برای هر یک بپرسید: کدام داده یا تصمیم این ادعا را پشتیبانی می‌کند؟ کدام توضیح بدیل باقی است؟ اگر پاسخ روشن نیست، دامنهٔ جملهٔ گزارش را کوچک کنید.

## ۲۲. چک‌لیست پیش از اعلام نتیجه

1. ادعا، جمعیت، سناریو و تصمیمِ وابسته را پیش از اجرا ثبت کرده‌ام.
2. نسخهٔ داده، منبع، split و گروه وابستگی معلوم است و test در تنظیم مدل مصرف نشده است.
3. baseline، metric اصلی، زیرگروه‌ها و قواعد حذف یا parse مشخص شده‌اند.
4. دو گزینه روی شرایط و نمونه‌های هم‌تراز سنجیده شده‌اند؛ seed و تغییر تنظیم ثبت است.
5. عدم‌قطعیت و واحد resampling با استقلال/خوشه‌بندی داده سازگارند.
6. ارزیابی انسانی rubric، جذب، کورسازی، توافق، اختلاف و محافظت از داده را ثبت کرده است.
7. داور ماشینی روی زیرمجموعهٔ انسانی کالیبره شده و سوگیری‌های محتمل بررسی شده‌اند.
8. آلودگی به‌صورت شواهد محدود، روش بررسی و ناحیهٔ ناشناخته گزارش شده، نه حکم مطلق.
9. محدودیت پوشش، هزینهٔ خطا و مواردی که اصلاً آزموده نشدند در کنار عدد آمده‌اند.

## ۲۳. تمرین‌ها

۱. جملهٔ «مدل الف از مدل ب بهتر است چون امتیازش بیشتر است» را به ادعایی محدود و قابل‌آزمون برای یک تصمیم مشخص بازنویسی کنید.

۲. یک دادهٔ گفت‌وگوی چندنوبتی بسازید که split تصادفی ردیفی در آن نشت ایجاد کند. گروه وابستگی مناسب را تعریف و روش تقسیم را توضیح دهید.

۳. برای داده‌ای با ۹۵٪ برچسب منفی و یک هزینهٔ بالا برای false negative، دو metric مکمل پیشنهاد دهید و بگویید چرا accuracy تنها کافی نیست.

۴. دو checkpoint روی همان ۲۰۰ مکالمه سنجیده شده‌اند؛ شش مکالمه از هر مشتری و چندین مشتری وجود دارد. واحد resampling و شکل گزارش اختلاف را تعیین کنید.

۵. سه ارزیاب روی یک prompt امتیازهای ترتیبی ۱ تا ۵ داده‌اند و برخی رأی‌ها گم‌اند. پیش از نام‌بردن از ضریب توافق، چه ویژگی‌هایی از طرح باید روشن شود؟

۶. یک داور LLM معمولاً پاسخ طولانی‌تر را برمی‌گزیند. طرحی برای آزمون این سوگیری و مقایسه با داور انسانی پیشنهاد کنید.

۷. ابزار جست‌وجو روی test set تطابقی نیافته است. یک جملهٔ دقیق دربارهٔ آلودگی بنویسید و دست‌کم دو محدودیت آزمون را ذکر کنید.

۸. در fixture فصل، اختلاف accuracy برابر ۱/۶ است، اما فقط سه گروه مستقل وجود دارد. کدام نتیجه را می‌توان گزارش کرد و کدام نتیجه را نمی‌توان ادعا کرد؟

## ۲۴. جمع‌بندی و پیوند فصل‌ها

Benchmark یک عدد نیست؛ قرارداد نسخه‌مند میان ادعا، سناریو، نمونه، مدل، scorer و تحلیل است. کیفیت سنجه به اعتبار سازه، پوشش، split، baseline، مدیریت وابستگی، عدم‌قطعیت و روش ارزیابی انسانی وابسته است. توافق، significance، hash و آزمون overlap هرکدام پاسخ محدود خود را دارند؛ هیچ‌کدام به‌تنهایی حقیقت، کاربردپذیری یا پاکی داده را ثابت نمی‌کنند.

فصل ۶۱ روش سنجش workload استنتاج را از این پرسش‌ها جدا می‌کند. فصل ۶۳ الگوهای خطا، سوگیری و استحکام را به موضوع اصلی بدل می‌سازد؛ فصل ۶۴ حمله و حریم خصوصی را می‌آزماید؛ فصل ۶۵ مدیریت و مستندسازی ریسک را ادامه می‌دهد. تمرین‌ها پاسخ یگانه ندارند؛ [پاسخ‌نامهٔ مستقل فصل ۶۲](book-engineering/answers/62-benchmarking-evaluation-fa.md) فرض‌ها و مرز شواهد را شرح می‌دهد. [پروژهٔ فصل](book-engineering/projects/62-evaluation-lab/README.md) و [گزارش ممیزی](book-engineering/chapters/62-audit-report-fa.md) همراه این متن‌اند.

## ۲۵. منابع و تاریخ بازبینی

منابع زیر در ۷ نوامبر ۲۰۲۶ بازبینی شدند. این فهرست برای پیگیری روش‌هاست، نه تأییدِ مستقل همهٔ نتیجه‌های هر مقاله.

- [Percy Liang و همکاران، “Holistic Evaluation of Language Models (HELM),” TMLR 2023 / arXiv:2211.09110](https://arxiv.org/abs/2211.09110) — پوشش چند سناریو و چند مطلوبیت و شفاف‌کردن جاهای خالی.
- [Rotem Dror، Gili Baumer، Segev Shlomov و Roi Reichart، “The Hitchhiker’s Guide to Testing Statistical Significance in Natural Language Processing,” ACL 2018](https://aclanthology.org/P18-1128/) — انتخاب آزمون متناسب با نوع task، metric و طراحی.
- [Joseph H. F. James، “Counting on Consensus: Selecting the Right Inter-Annotator Agreement Metric for NLP Annotation and Evaluation,” LREC 2026](https://aclanthology.org/2026.lrec-1.347/) — فرض‌ها و محدودیت‌های سنجهٔ توافق برحسب وظیفه، عدم‌توازن، دادهٔ گمشده و گزارش فاصله/اختلاف.
- [Lianmin Zheng و همکاران، “Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena,” NeurIPS 2023 Datasets and Benchmarks / arXiv:2306.05685](https://arxiv.org/abs/2306.05685) — مطالعهٔ داور LLM و سوگیری‌های جایگاه، verbosity و self-enhancement در تنظیم‌های بررسی‌شده.
- [Yujuan Fu و همکاران، “Does Data Contamination Detection Work (Well) for LLMs?,” NAACL Findings 2025 / arXiv:2410.18966](https://arxiv.org/abs/2410.18966) — فرض‌های روش‌های تشخیص و محدودیت تعمیم.
- [Simin Chen و همکاران، “Benchmarking Large Language Models Under Data Contamination: A Survey from Static to Dynamic Evaluation,” EMNLP 2025](https://aclanthology.org/2025.emnlp-main.511/) — مقایسهٔ بنچمارک ایستا/پویا و چالش معیارهای استاندارد.
- [Yue Deng و همکاران، مقالهٔ بررسی آلودگی و probeهای بنچمارک، NAACL 2024](https://aclanthology.org/2024.naacl-long.482/) — retrieval و probe به‌عنوان نشانهٔ بررسی، نه اثبات منشأ.
- [NIST AI 600-1, Generative AI Profile (July 2024)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) — ارزیابی پیش از استقرار، شفافیت دربارهٔ روش و محدودیت، و توجه به زمینهٔ کاربرد.
- [LiveCodeBench](https://livecodebench.github.io/) و [Jain و همکاران، arXiv:2403.07974](https://arxiv.org/abs/2403.07974) — نمونهٔ ارزیابی زمان‌مند؛ تاریخ تازه خطر مواجهه را کاهش می‌دهد، نه آنکه نبود آلودگی را تضمین کند.

## پیوست اجرایی: کد دقیق پروژهٔ آزموده‌شده

کد زیر بایت‌به‌بایت با `evaluation_lab.py` پروژهٔ پیوندشده در بالا تطبیق داده می‌شود. نتیجه‌های آن فقط fixture کوچک ساختگی را توصیف می‌کنند.

```python
"""Small, deterministic audit helpers for an explicitly synthetic benchmark fixture.

This module is teaching code, not a production evaluator. It uses only the Python
standard library and deliberately labels overlap results as review flags, not proof
of training-data contamination.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import re
import sys
import unicodedata
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parent
VALID_SPLITS = {"train", "validation", "test"}
LABELS = (0, 1)
REQUIRED_FIELDS = {"case_id", "group_id", "split", "prompt", "reference", "baseline", "candidate"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_number}: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"line {line_number} must be a JSON object")
            rows.append(value)
    return rows


def validate_rows(rows: Sequence[dict[str, Any]]) -> dict[str, int]:
    """Validate schema, unique cases, labels, and group-disjoint data splits."""
    if not rows:
        raise ValueError("benchmark fixture must contain at least one case")
    seen: set[str] = set()
    group_split: dict[str, str] = {}
    counts = {split: 0 for split in sorted(VALID_SPLITS)}
    for index, row in enumerate(rows):
        missing = REQUIRED_FIELDS - row.keys()
        if missing:
            raise ValueError(f"row {index} is missing fields: {sorted(missing)}")
        case_id = row["case_id"]
        group_id = row["group_id"]
        split = row["split"]
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"row {index} has an empty or non-string case_id")
        if not isinstance(group_id, str) or not group_id.strip():
            raise ValueError(f"row {index} has an empty or non-string group_id")
        if case_id in seen:
            raise ValueError(f"duplicate case_id: {case_id}")
        seen.add(case_id)
        if split not in VALID_SPLITS:
            raise ValueError(f"unknown split {split!r} for case {case_id}")
        previous = group_split.setdefault(group_id, split)
        if previous != split:
            raise ValueError(f"group {group_id!r} crosses splits {previous!r} and {split!r}")
        counts[split] += 1
        if not isinstance(row["prompt"], str) or not row["prompt"].strip():
            raise ValueError(f"case {case_id} has an empty prompt")
        for field in ("reference", "baseline", "candidate"):
            value = row[field]
            if isinstance(value, bool) or value not in LABELS:
                raise ValueError(f"case {case_id} has invalid binary label in {field}: {value!r}")
    return counts


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion; not cluster-adjusted."""
    if total <= 0 or successes < 0 or successes > total:
        raise ValueError("require 0 <= successes <= total and total > 0")
    p = successes / total
    z2 = z * z
    denominator = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denominator
    margin = z * math.sqrt((p * (1.0 - p) / total) + (z2 / (4.0 * total * total))) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def classification_metrics(truth: Sequence[int], predictions: Sequence[int]) -> dict[str, Any]:
    """Return accuracy, macro-F1, per-class scores, and a Wilson interval."""
    if len(truth) != len(predictions) or not truth:
        raise ValueError("truth and predictions must have equal, nonzero length")
    if any(isinstance(value, bool) or not isinstance(value, int) or value not in LABELS for value in (*truth, *predictions)):
        raise ValueError("labels must be integer 0 or 1")
    per_class: dict[str, dict[str, float | int]] = {}
    f1_values: list[float] = []
    for label in LABELS:
        tp = sum(actual == label and predicted == label for actual, predicted in zip(truth, predictions))
        fp = sum(actual != label and predicted == label for actual, predicted in zip(truth, predictions))
        fn = sum(actual == label and predicted != label for actual, predicted in zip(truth, predictions))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        support = sum(actual == label for actual in truth)
        per_class[str(label)] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }
        f1_values.append(f1)
    correct = sum(actual == predicted for actual, predicted in zip(truth, predictions))
    low, high = wilson_interval(correct, len(truth))
    return {
        "n": len(truth),
        "correct": correct,
        "accuracy": correct / len(truth),
        "accuracy_wilson_95": [low, high],
        "macro_f1": sum(f1_values) / len(f1_values),
        "per_class": per_class,
    }


def paired_group_bootstrap(
    rows: Sequence[dict[str, Any]], *, repetitions: int = 2000, seed: int = 62
) -> dict[str, Any]:
    """Bootstrap paired accuracy difference by resampling whole group clusters."""
    if repetitions < 100:
        raise ValueError("use at least 100 bootstrap repetitions")
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["group_id"]].append(row)
    group_ids = sorted(groups)
    if len(group_ids) < 2:
        raise ValueError("group bootstrap requires at least two groups")
    observed = sum(r["candidate"] == r["reference"] for r in rows) / len(rows) - sum(
        r["baseline"] == r["reference"] for r in rows
    ) / len(rows)
    rng = random.Random(seed)
    deltas: list[float] = []
    for _ in range(repetitions):
        sampled_ids = [rng.choice(group_ids) for _ in group_ids]
        sample = [row for group_id in sampled_ids for row in groups[group_id]]
        base = sum(r["baseline"] == r["reference"] for r in sample) / len(sample)
        candidate = sum(r["candidate"] == r["reference"] for r in sample) / len(sample)
        deltas.append(candidate - base)
    deltas.sort()

    def percentile(q: float) -> float:
        position = (len(deltas) - 1) * q
        lo = math.floor(position)
        hi = math.ceil(position)
        if lo == hi:
            return deltas[lo]
        return deltas[lo] * (hi - position) + deltas[hi] * (position - lo)

    return {
        "groups": len(group_ids),
        "repetitions": repetitions,
        "seed": seed,
        "observed_candidate_minus_baseline_accuracy": observed,
        "percentile_95_interval": [percentile(0.025), percentile(0.975)],
        "bootstrap_fraction_delta_positive": sum(value > 0 for value in deltas) / repetitions,
        "warning": "Fixture-sized descriptive bootstrap; not a significance claim or a substitute for a prespecified study.",
    }


def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def _token_jaccard(left: str, right: str) -> float:
    a = set(_normalize_text(left).split())
    b = set(_normalize_text(right).split())
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def screen_for_overlap(
    evaluation_texts: Sequence[str], training_texts: Sequence[str], *, threshold: float = 0.8
) -> list[dict[str, Any]]:
    """Flag exact/near overlaps for manual review; never infer training provenance."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")
    normalized_training: dict[str, list[int]] = defaultdict(list)
    for index, text in enumerate(training_texts):
        normalized_training[_normalize_text(text)].append(index)
    output: list[dict[str, Any]] = []
    for eval_index, text in enumerate(evaluation_texts):
        normalized = _normalize_text(text)
        exact = normalized_training.get(normalized, []) if normalized else []
        best_score = 0.0
        best_training_index: int | None = None
        for train_index, train_text in enumerate(training_texts):
            score = _token_jaccard(text, train_text)
            if score > best_score:
                best_score, best_training_index = score, train_index
        flagged = bool(exact) or best_score >= threshold
        reason = "normalized_exact_match" if exact else ("high_token_jaccard_review" if flagged else "no_flag")
        output.append({
            "evaluation_index": eval_index,
            "flagged_for_review": flagged,
            "reason": reason,
            "exact_training_indices": exact,
            "best_token_jaccard": best_score,
            "best_training_index": best_training_index,
            "interpretation": "Overlap is a review lead only; it does not establish whether a model trained on this text.",
        })
    return output


def pairwise_percent_agreement(votes_by_case: dict[str, Sequence[int]]) -> dict[str, Any]:
    """Uncorrected pairwise agreement; report counts and disagreements, not only a score."""
    agreements = 0
    comparisons = 0
    items_with_votes = 0
    for votes in votes_by_case.values():
        if len(votes) < 2:
            continue
        items_with_votes += 1
        for left, right in combinations(votes, 2):
            comparisons += 1
            agreements += left == right
    return {
        "items_with_at_least_two_votes": items_with_votes,
        "pair_comparisons": comparisons,
        "pair_agreements": agreements,
        "percent_agreement": agreements / comparisons if comparisons else None,
        "warning": "Raw pairwise agreement is not chance-corrected and is not a measure of label validity.",
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_fixture() -> dict[str, Any]:
    data_path = ROOT / "sample_evaluation.jsonl"
    rows = load_jsonl(data_path)
    split_counts = validate_rows(rows)
    test_rows = [row for row in rows if row["split"] == "test"]
    corpus_path = ROOT / "training_corpus_fixture.txt"
    training_texts = [line.strip() for line in corpus_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    vote_path = ROOT / "human_votes_fixture.json"
    votes = json.loads(vote_path.read_text(encoding="utf-8"))
    return {
        "scope": "Synthetic, hand-authored teaching fixture only; no external benchmark or model was used.",
        "fixture_sha256": {
            data_path.name: sha256_file(data_path),
            corpus_path.name: sha256_file(corpus_path),
            vote_path.name: sha256_file(vote_path),
        },
        "split_counts": split_counts,
        "test_case_count": len(test_rows),
        "baseline": classification_metrics(
            [row["reference"] for row in test_rows], [row["baseline"] for row in test_rows]
        ),
        "candidate": classification_metrics(
            [row["reference"] for row in test_rows], [row["candidate"] for row in test_rows]
        ),
        "paired_group_bootstrap": paired_group_bootstrap(test_rows),
        "human_vote_fixture": pairwise_percent_agreement(votes),
        "overlap_screen": screen_for_overlap([row["prompt"] for row in test_rows], training_texts),
        "limitations": [
            "The labels, predictions, annotator votes, and corpus lines are fabricated for teaching.",
            "The test contains six cases in three groups; intervals and bootstrap output are unstable and illustrative.",
            "Wilson intervals assume independent Bernoulli trials; this code does not make that assumption valid for clustered or distribution-shifted data.",
            "Overlap flags are heuristics and cannot prove contamination or prove its absence.",
            "No human annotators, language model, benchmark, deployment workload, or sensitive data were used.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results.json")
    args = parser.parse_args()
    result = run_fixture()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "test_cases": result["test_case_count"],
        "baseline_accuracy": result["baseline"]["accuracy"],
        "candidate_accuracy": result["candidate"]["accuracy"],
        "limitations": "synthetic fixture only; see results.json",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

---

# جلد پنجم، فصل ۲ — توهم، سوگیری، استحکام، تبیین‌پذیری و تفسیرپذیری

**نگاشت:** فصل محلی ۲ جلد پنجم = فصل سراسری ۶۳. **تاریخ بازبینی منابع: ۷ نوامبر ۲۰۲۶.** فصل ۶۲ طراحی ارزیابی، معیارها، ارزیابان انسانی و عدم‌قطعیت اندازه‌گیری را صورت‌بندی کرد؛ این فصل آن ابزارها را برای ممیزی رفتار مدل در چهار محورِ حقیقت و شواهد، سوگیری، استحکام و توضیح‌پذیری به‌کار می‌گیرد. فصل ۶۴ حمله‌های خصمانه، Prompt Injection، مسموم‌سازی و حریم خصوصی را بررسی می‌کند؛ فصل ۶۵ حکمرانی و مدیریت ریسک را پوشش می‌دهد. این فصل نه گواهی ایمنی محصول است، نه آزمون امنیتی و نه حکم کلی دربارهٔ «خوب» یا «منصفانه» بودن یک مدل.

**پیش‌نیاز:** تفکیک دادهٔ آزمون از آموزش، آشنایی مقدماتی با احتمال و معیارهای طبقه‌بندی، توانایی خواندن یک گزارش ارزیابی. **خروجی:** بتوانید پشتیبانی شواهد را از حقیقت و وفاداری جدا کنید، شکاف گروهی را بدون تبدیل آن به حکم ارزشی تفسیر کنید، تغییر توزیع را با جفت‌های معناییِ معتبر بیازمایید، و برای یک توضیح post-hoc آزمون وفاداری و کاربری طراحی کنید.

![شکل ۵-۲-۱ — یک ورودی نسخه‌مند و محدود به زمینه به چهار آزمون موازی منشعب می‌شود: حقیقت و شواهد، برش‌های گروهی و معیارهای سوگیری، استحکام در برابر تغییرهای تعریف‌شده، و وفاداری و کاربری توضیح. نتایج همراه با مخرج، نمونه، عدم‌قطعیت و محدودیت‌ها در گزارش ممیزی جمع می‌شوند و به اقدام و آزمون دوباره می‌رسند. نمودار امتیاز واحد یا تضمین کلی نمی‌دهد و معنا به رنگ وابسته نیست.](book-engineering/diagrams/v5-ch02-behavior-audit.svg)

**شکل ۵-۲-۱ —** چهار پرسش به‌هم‌مرتبط‌اند، اما یک معیار مشترک ندارند؛ گزارش باید زمینه، مخرج، روش و محدودیت هر آزمون را جدا نگه دارد.

## ۱. جایگاه فصل و مرزهای ممیزی رفتار

«ممیزی رفتار» در این فصل یعنی آزمون مستندِ ادعاهای محدود دربارهٔ خروجی و شرایط آن؛ نه وارسی کامل وزن‌ها و نه تضمین رفتار همهٔ کاربران. ممکن است سامانه‌ای پاسخ factual نادرست بدهد، برای دو گروه با ورودی‌های هم‌معنا رفتار متفاوتی داشته باشد، با تغییر بی‌ضرر ورودی ناپایدار شود، یا توضیحی بسازد که از تصمیم واقعی پشتیبانی نکند. هر مورد پرسش، داده، معیار و مرز تعمیم خودش را دارد.

فصل ۶۲ می‌پرسد «آزمون را چگونه طراحی و اندازه‌گیری کنیم؟»؛ این فصل می‌پرسد «کدام نوع رفتار را چگونه ممیزی کنیم؟»؛ فصل ۶۴ سراغ مهاجم و قابلیت سوءاستفاده می‌رود. یک prompt نامعمول می‌تواند آزمون تغییر توزیعِ بی‌خطر باشد؛ اگر هدفش دورزدن کنترل یا استخراج داده است، مسئلهٔ امنیتی است و باید با پروتکل فصل ۶۴ بررسی شود. این مرزبندی مانع از آن می‌شود که یک score عادی را به آزمون red-team تعبیر کنیم.

## ۲. حقیقت، پشتیبانی از منبع و وفاداری یکی نیستند

در متن مولد سه پرسش جداگانه داریم. **درستی factual** می‌پرسد آیا ادعا با واقعیتِ قابل‌راستی‌آزمایی در زمان و زمینهٔ مشخص سازگار است. **پشتیبانی از منبع** می‌پرسد آیا سندِ ارجاع‌شده واقعاً همان ادعا را پشتیبانی می‌کند. **وفاداری به زمینه** می‌پرسد آیا پاسخ با متن فراهم‌شده، دستور معتبر یا دادهٔ ورودی تناقض دارد و آیا چیزی بیرون از آن را به‌عنوان شاهدِ همان زمینه جا می‌زند.

ادعایی می‌تواند در جهان درست ولی در سندِ داده‌شده بی‌پشتوانه باشد؛ می‌تواند از سند پشتیبانی شود ولی سند قدیمی یا نادرست باشد؛ و می‌تواند بدون منبع آشکار درست از آب درآید. پس citation، بازیابی سند یا توافق دو مدل، به‌تنهایی truth oracle نیست. ثبت تاریخ، نسخه و دامنهٔ منبع بخشی از تعریف آزمون است.

## ۳. خطاهای factual را ریز و قابل‌بررسی نام‌گذاری کنید

واژهٔ رایج «توهم» چند پدیده را در یک برچسب مبهم جمع می‌کند. برای گزارش دقیق‌تر دست‌کم این موارد را جدا کنید: ادعای ناسازگار با شواهد معتبر؛ ادعای بی‌پشتوانه؛ منبع یا نقل‌قول نادرست؛ نسبت‌دادن گفته به شخص یا سند اشتباه؛ نتیجه‌گیری فراتر از داده؛ تناقض درون پاسخ؛ و موردی که با شواهد موجود قابل‌تأیید نیست. «تأییدناپذیر» را بی‌دلیل «نادرست» ننامید و «روان بودن» را شاهد درستی نگیرید.

NIST در پروفایل GenAI از اصطلاح *confabulation* برای محتوای ظاهراً روان اما نادرست یا ساختگی استفاده می‌کند. اصطلاح «توهم» در این فصل نام کوتاه و رایج حوزه است، نه ادعایی دربارهٔ تجربه یا باور انسانیِ مدل. هر پروژه باید rubric خود را بنویسد و «نامعلوم»، «متناقض» و «تأییدشده» را از هم تفکیک کند.

## ۴. از پاسخِ بلند به ادعاهای اتمی برسید

پاسخ ترکیبی را به گزاره‌های کوچک‌تر بشکنید تا هر جزء با مدرک متناظر سنجیده شود. برای نمونه، پاسخ «این درمان در سال ۲۰۲۱ تأیید شد و نرخ موفقیتش ۸۰ درصد است» دو ادعا دارد: تاریخ تأیید و مقدار نرخ. ممکن است یکی درست و دیگری بی‌پشتوانه باشد. برش ادعا باید معنای اصلی، قید زمانی، نفی و نسبت‌دهی را حفظ کند؛ تجزیهٔ نادرست خودش منبع خطاست.

FActScore به ارزیابی factual بر پایهٔ ادعاهای اتمی و شواهد منبع‌دار می‌پردازد؛ FactReasoner رابطهٔ شواهد و گزاره را با تفکیک entailment و contradiction بررسی می‌کند. هر دو وابسته به کیفیت atomization، بازیابی، منبع و تصمیم برچسب‌زن‌اند. یک گزارهٔ خردتر لزوماً «حقیقت ساده» یا شاهد قطعی ندارد.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="کسر پشتیبانی برابر است با شمار ادعاهای پشتیبانی‌شده تقسیم بر مجموع ادعاهای پشتیبانی‌شده و متناقض؛ ادعاهای نامعلوم در مخرج نیستند">
  <mrow><mi>SupportFraction</mi><mo>=</mo><mfrac><mrow><mi>Supported</mi></mrow><mrow><mi>Supported</mi><mo>+</mo><mi>Contradicted</mi></mrow></mfrac></mrow>
</math>

**متن جایگزین فرمول:** کسر پشتیبانی روی ادعاهای حل‌شده حساب می‌شود؛ مورد نامعلوم در مخرج قرار نمی‌گیرد و نتیجه فقط به همان rubric و شواهد مربوط است.

## ۵. قرارداد شواهد و منشأ را پیش از امتیازدهی ثبت کنید

برای هر ادعا ثبت کنید: متن دقیق ادعا، برچسب و تعریف برچسب، سند یا قطعهٔ شاهد، تاریخ و نسخهٔ سند، حوزهٔ اعتبار، روش جست‌وجو، ارزیاب و درجهٔ اطمینان. سندِ بی‌تاریخ دربارهٔ موضوع متغیر، شاهد کافی برای وضعیت فعلی نیست. در پاسخ‌های حوزهٔ علمی، قانونی یا سلامت، اختلافِ نسخه، جمعیت هدف و قیدهای کاربرد را در rubric نگه دارید.

نمونهٔ «نامعلوم» باید مسیر مستقلی داشته باشد: آیا سند در دسترس نبود؟ شواهد ناسازگار بودند؟ پرسش مبهم بود؟ یا ارزیاب تخصص کافی نداشت؟ ادغام این وضعیت‌ها، نرخ خطا را به تعریف انتخابی وابسته و تفسیر را دشوار می‌کند. اگر برچسب‌ها با نظر متخصص حل می‌شوند، شمار ارزیابان، دستورالعمل، اختلاف‌ها و روش adjudication را گزارش کنید.

## ۶. بازیابی و citation کمک‌اند، نه تضمین

سامانهٔ RAG می‌تواند پاسخ را به سند متصل کند، اما سند نامرتبط، تاریخ‌گذشته یا ناقص را هم بازیابی می‌کند؛ مدل نیز ممکن است از سند فراتر برود یا citation ظاهراً معتبر بسازد. retrieval recall، پشتیبانی گزاره، درستی factual و کیفیت citation معیارهای متفاوتی هستند. در آزمون RAG، سندهای زمینه را همراه پاسخ ارزیابی کنید و ببینید کدام گزاره از کدام قطعه پشتیبانی می‌شود.

TRIVIA+ در ACL 2026 بر سنجشِ تشخیص hallucination در زمینهٔ RAG بلند و نویز برچسب تمرکز دارد؛ SciFactCheck در EMNLP 2026 انواعی چون ادعای تأییدناپذیر، overclaim و attribution را در promptهای علمی جدا می‌کند. این‌ها نمونه‌هایی از مسئله‌های پژوهشی و benchmarkهای پیشنهادی‌اند، نه استاندارد نهایی یا اثبات اینکه یک ابزار fact-checking برای همهٔ حوزه‌ها معتبر است.

## ۷. سنجهٔ factuality را همراه مخرج و خطای برچسب گزارش کنید

اگر نمرهٔ واحد می‌سازید، روشن کنید چه چیزی واحد شمارش است: پاسخ، جمله، ادعای اتمی یا منبع. نرخ ادعای پشتیبانی‌شده را از روی تعداد ادعاهای برچسب‌خورده حساب کنید؛ سپس موارد متناقض و نامعلوم را جداگانه گزارش دهید. اگر سامانه پاسخ را کوتاه‌تر می‌کند، می‌تواند با حذف ادعاها نرخ پشتیبانی را بهتر جلوه دهد؛ بنابراین coverage، شمار ادعا، abstention و طول پاسخ را هم بسنجید.

FActScore و سنجه‌های مشابه در تشخیص ادعا و ارزیابی مدرک به مدل یا ارزیاب کمکی وابسته‌اند. نتایج را روی نمونهٔ انسانیِ کور ممیزی کنید، نمونه‌های اختلاف را بخوانید و حساسیت به تغییر rubric را نشان دهید. اختلاف scorer خودکار و ارزیاب را به‌عنوان خطای ابزار اندازه‌گیری ببینید، نه چیزی که با میانگین‌گیری ناپدید می‌شود.

## ۸. Calibration و اطمینان، فقط با تعریف دقیق معنا دارند

Calibration می‌پرسد وقتی مدل یا classifier روی مجموعه‌ای از پیش‌بینی‌ها اطمینان مشخصی اعلام می‌کند، چه نسبتی از آن‌ها درست از آب درمی‌آید؛ این ویژگی گروهی/توزیعی است، نه گواه درست بودن تک‌پیش‌بینی. در متن مولد، «اعتماد به نفس» نمرهٔ توکنی، احتمال دنباله، خوداظهاری زبانی، نمرهٔ retrieval یا داوری مدل دیگر می‌تواند باشد؛ آن‌ها را با هم یکی نگیرید.

برای classifier، Brier score و expected calibration error از خانوادهٔ ابزارهای رایج‌اند. ECE، برای مثال، اختلاف میان accuracy و confidence را در بازه‌های bucketشده تجمیع می‌کند؛ تعداد و مرز bucketها نتیجه را عوض می‌کنند. نمرهٔ پایین روی نمونهٔ کوچک یا binning نامناسب، calibration عمومی یا اطمینان یک پاسخ مولد را ثابت نمی‌کند. Guo و همکاران calibration شبکه‌های عصبیِ طبقه‌بند را بررسی کردند؛ انتقال مستقیم آن نتیجه به ادعاهای متن آزاد نیازمند اعتبارسنجی جداست.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="ECE برابر است با مجموع وزن هر بازهٔ اطمینان در نمونه، ضرب در قدر مطلق اختلاف دقت همان بازه و میانگین confidence آن">
  <mrow><mi>ECE</mi><mo>=</mo><munderover><mo>∑</mo><mrow><mi>m</mi><mo>=</mo><mn>1</mn></mrow><mi>M</mi></munderover><mfrac><mrow><mo>|</mo><msub><mi>B</mi><mi>m</mi></msub><mo>|</mo></mrow><mi>n</mi></mfrac><mo>|</mo><mi>accuracy</mi><mo>(</mo><msub><mi>B</mi><mi>m</mi></msub><mo>)</mo><mo>−</mo><mi>confidence</mi><mo>(</mo><msub><mi>B</mi><mi>m</mi></msub><mo>)</mo><mo>|</mo></mrow>
</math>

**متن جایگزین فرمول:** ECE میانگین وزنیِ فاصلهٔ دقت و میانگین اطمینان در bucketهاست؛ تعریف confidence، تعداد نمونه و انتخاب مرز bucketها باید گزارش شود.

## ۹. سوگیری را در یک تصمیم و جمعیت مشخص تعریف کنید

«مدل biased است» بدون تعریف گروه، تصمیم، دادهٔ مرجع و پیامد، گزارهٔ آزمون‌پذیر نیست. سوگیری ممکن است از نمونه‌گیری کم‌نماینده، برچسب‌های تاریخی، نماینده‌های نامناسب، زبان و dialect، طراحی prompt، خطای اندازه‌گیری، threshold، یا کاربرد خروجی در تصمیمی متفاوت ناشی شود. «دادهٔ متوازن» به‌تنهایی همهٔ این علت‌ها را رفع نمی‌کند.

تعریف عملیاتی را با ذی‌نفعان و افراد متأثر بنویسید: چه زیانی مهم است، در کدام زیرگروه، برای کدام عمل و در چه افق زمانی؟ دسته‌های جمعیتی در هر جامعه و سامانه یکسان یا بی‌مسئله نیستند. با دادهٔ حساس فقط بر مبنای ضرورت، مجوز، امنیت و روش مستند کار کنید؛ نبود فیلد حساس در dataset، به‌معنای نبودِ اثر نامتوازن نیست.

## ۱۰. شکاف گروهی را با مخرج، نمونه و پیامد نشان دهید

بسته به کار، برش‌ها می‌توانند accuracy، recall/TPR، false-positive rate، precision، نرخ امتناع، نرخ خطای factual، یا کیفیت پاسخ بر حسب زبان، لهجه، سناریو یا روش ورودی را مقایسه کنند. تفاوت نرخ پیش‌بینی مثبت را با تفاوت خطای واقعی یکی نگیرید. یک جدول مفید، تعداد واقعی هر کلاس، شمار پیش‌بینی‌ها، نرخ و بازهٔ عدم‌قطعیت را کنار هر گروه می‌آورد.

گروه‌های تقاطعی را بی‌دلیل در میانگین بزرگ‌تر محو نکنید؛ اما از چند نمونهٔ کم هم نتیجهٔ پرقدرت نسازید. گروه‌های ناموجود، label noise نامتقارن و کاربران بیرون از دسته‌بندی را ثبت کنید. اگر یک گروه به‌اندازهٔ کافی نمونه ندارد، عبارت «داده کافی نیست» دقیق‌تر از «برای این گروه منصفانه است» خواهد بود.

## ۱۱. معیارهای عدالت می‌توانند با هم تعارض داشته باشند

Demographic parity برابری نرخ تصمیم مثبت را می‌سنجد؛ equal opportunity برابری TPR را هدف می‌گیرد؛ equalized odds به هم‌ترازی TPR و FPR مربوط است؛ calibration هم یک خاصیت دیگر می‌سنجد. این معیارها پرسش ارزشی و آماری متفاوتی دارند. انتخاب یکی باید با هزینهٔ خطا، base rate، قواعد تصمیم، قانون و نظر افراد متأثر توجیه شود، نه با اینکه کدام نمودار مطلوب‌تر به نظر می‌رسد.

Chouldechova نشان می‌دهد در مطالعهٔ خاص ارزیابی ریسک، وقتی نرخ پایهٔ رخداد میان گروه‌ها فرق دارد و پیش‌بینی بی‌خطا نیست، برخی خواسته‌های معیارمحور را نمی‌توان هم‌زمان برآورده کرد. این نتیجه را به «عدالت غیرممکن است» یا هر مدل مولد تعمیم ندهید؛ پیام کاربردی آن این است که پیش از optimization، معیارِ انتخاب‌شده و trade-off آن را شفاف کنید.

FairFund-Bench در Findings of EMNLP 2026 توزیع منابع را روی ۶۰۰ درخواست انگلیسی و ۱۴ مدل بررسی می‌کند و اثر قالب ممیزی بر اندازه و جهت تفاوت‌های مطالعهٔ خود را گزارش می‌دهد. این نتیجه اهمیتِ پروتکل را نشان می‌دهد، اما از آن نمی‌توان حکم کلی دربارهٔ همهٔ گروه‌ها، زبان‌ها یا تصمیم‌های تخصیص منابع گرفت.

## ۱۲. پوشش داده، برچسب مرجع و زبان را ممیزی کنید

برای هر برش، بدانید چه کسی و چگونه نمونه‌ها را ساخته یا انتخاب کرده؛ برچسب «حقیقت» از کدام منبع یا فرایند آمده؛ و آیا گروه‌های کم‌نماینده خطای برچسب بیشتری دارند. نمونهٔ تکراری، templateهای آشنا یا source leakage می‌تواند عملکرد را بالا ببرد. یک بنچمارک فقط سازه و جمعیتی را می‌سنجد که واقعاً در آن نماینده دارند.

در آزمون متن چندزبانه، ترجمهٔ ماشینی از یک مجموعهٔ انگلیسی لزوماً هم‌ارزی معنایی، رسم‌الخط، dialect و پیچیدگی فرهنگی را حفظ نمی‌کند. از ارزیابان مناسب و بومیِ زمینه بهره بگیرید؛ اما یک ارزیاب را نمایندهٔ تمام جامعه نگیرید. تعداد، روش جذب، قرارداد اصطلاحات و اختلاف نظر را گزارش کنید. مواردی که برچسب هویتی مبهم یا داوطلبانه است، با احترام و حفاظت داده مدیریت شود.

## ۱۳. از مشاهدهٔ شکاف تا مداخله، یک زنجیرهٔ استدلال بسازید

شکاف مشاهده‌شده علت را مشخص نمی‌کند. آن را به لایه‌ها بشکنید: نمونه‌گیری و پوشش؛ کیفیت/معنای label؛ پردازش متن و tokenization؛ مدل و fine-tuning؛ threshold یا prompt؛ ابزار retrieval؛ تجربهٔ کاربر؛ و قاعدهٔ تصمیم نهایی. مداخلهٔ درست به تشخیص بستگی دارد. افزودن نمونه ممکن است به کیفیت برچسب یا تعریف هدف بد پاسخ دهد؛ حذف ویژگی حساس هم proxyها را حذف نمی‌کند.

پس از تغییر داده، مدل، prompt یا threshold، همان آزمون قبلی را با نسخهٔ تازه اجرا کنید و معیارهای کل و گروهی را همراه با ناحیه‌های تازهٔ آسیب بررسی کنید. نتایج را قبل و بعد از مداخله و روی دادهٔ نگه‌داشته‌شده ثبت کنید. هیچ post-processing یا برابرسازی عددی را «رفع کامل سوگیری» ننامید؛ تصمیم عملی به خطر و الزام کاربرد وابسته است.

## ۱۴. استحکام را از امنیت خصمانه جدا کنید

در این فصل، استحکام یعنی رفتار قابل‌قبول تحت تغییرهایی که برای ارزیابی تعریف شده‌اند: تغییر زمان، دامنه، قالب، زبان یا شکل ورودی؛ یا تغییر بی‌خطری که انتظار می‌رود معنای task را حفظ کند. این با پاسخ‌گویی در برابر مهاجم سازگار، prompt injection، jailbreak، poisoning یا استخراج وزن یکی نیست. آزمون آن‌ها و کنترل دسترسی/حریم خصوصی موضوع فصل ۶۴ است.

پیش از آزمون invariant بودن، مشخص کنید کدام تغییر باید خروجی را ثابت نگه دارد و کدام تغییر باید رفتار را عوض کند. تغییر نام، punctuation، واحد، negation یا ترتیب عبارت می‌تواند معنای واقعی را تغییر دهد. robustness را با تعریف تغییر و مرجع معنایی گزارش کنید، نه با نام کلی «adversarially robust».

## ۱۵. تغییر توزیع را در چند بُعد اندازه بگیرید

توزیع کاربرد می‌تواند در زمان، جغرافیا، زبان، جمعیت، موضوع، طول prompt، دستگاه، منبع retrieval، رفتار کاربر و قالب عوض شود. WILDS برای تغییرهای توزیع در داده‌ها و محیط‌های کاربردی benchmarkهایی گرد آورده است؛ LENS در ACL 2026 تغییر توزیع prompt کاربران را در ۱۹۲ تنظیم زمانی، جمعیتی و جغرافیایی بررسی می‌کند و در طرح خود افت میانگین ۷۳٪ گزارش می‌دهد. این عدد به promptها، مدل‌ها و تعریف همان آزمایش وابسته است؛ نه پیش‌بینی افت همهٔ محصولات و نه برآوردی برای مدل‌های دیگر.

SciFactCheck در EMNLP 2026، برای نمونه، ۲٬۵۰۰ prompt در پنج حوزهٔ علمی و ۱۸ مدل را با برچسب‌های چندنوعی بررسی می‌کند؛ نویسندگان توافق ابزار بررسی factual با متخصصان را در pilot متوسط گزارش می‌کنند. این نتیجه به‌خودی‌خود نشان نمی‌دهد کدام مدل علمیِ «بهترین» است؛ بر اهمیت تعریف نوع خطا و محدودیت labeler تأکید می‌کند.

برای هر محور shift، دادهٔ آزمون، provenance، جمعیت مرجع و تصمیمِ پشتیبانی‌شده را مشخص کنید. افت میانگین را کنار بدترین برش و نمونه‌های خطا بگذارید. اگر اندازه‌گیری از کاربران واقعی است، رضایت، حداقل‌سازی داده و الزامات حریم خصوصی را رعایت کنید؛ اثر drift را از تغییر نسخهٔ سرویس، سنجه یا ترکیب کاربران جدا کنید.

## ۱۶. آزمون جفتی فقط وقتی معتبر است که معنا حفظ شود

برای یک ورودی، یک یا چند variant بسازید: تفاوت فاصله و normalization؛ paraphrase دستی؛ جابه‌جایی نام‌های بی‌اثر در یک task؛ یا قالبی متفاوت. هر جفت را به‌صورت مستقل بررسی کنید که label و intended meaning حفظ شده است. اگر تبدیلْ پاسخ درست را عوض می‌کند، آن جفت آزمون invariance نیست و باید با برچسب جداگانه ارزیابی شود.

می‌توانید consistency، accuracy روی variant، و نرخ تغییر خروجی را محاسبه کنید. برای پاسخ مولد، exact string match معمولاً سخت‌گیرانه‌تر از نیاز است؛ به‌جای آن، ویژگی معنایی یا ادعای factual را با rubric سنجش کنید. هم نمونه‌های ثابت ولی غلط و هم نمونه‌های تغییرکرده اما درست را بخوانید. قاعدهٔ scorer را پیشاپیش اعلام کنید.

## ۱۷. میانگین را با بدترین برش و نوع خطا کامل کنید

گزارش استحکام شامل baseline و variant در هر زیرگروه، اختلاف مطلق و نسبی، تعداد نمونه و برش کم‌عملکرد باشد. «robust accuracy» می‌تواند سهم ورودی‌هایی باشد که در همهٔ تغییرهای ازپیش‌تعریف‌شده درست مانده‌اند؛ ولی مقدار آن فقط برای همان مجموعه و تعریفِ حفظ‌معناست. اگر یک زیرگروه بسیار کوچک است، اندازهٔ آن را پنهان نکنید و با وزن‌دهی بی‌توضیح، میانگین را دست‌کاری نکنید.

برای مدل مولد، شکست را بر حسب نوع ادعا، citation، امتناع، تناقض یا زیان محتمل دسته‌بندی کنید. یک افت کوچک در معیار کلی ممکن است روی یک کاربرد حساس مهم باشد؛ یک افت بزرگ روی variant نامعتبر نیز شاهد خوبی نیست. همراه عدد، چند مورد نماینده و چند مورد مرزی را با حداقل دادهٔ لازم منتشر کنید.

## ۱۸. امتناع و کالیبراسیون را در برابر هم نسنجید

سامانه ممکن است برای عدم‌قطعیت بالا abstain کند. این کار فقط هنگامی مفید است که آستانه روی validation تنظیم شده باشد، coverage و risk هر دو گزارش شوند، و مسیر بعدیِ کاربر روشن باشد. اگر مدل روی یک گروه بیشتر امتناع می‌کند یا fallback دسترس‌پذیر نیست، خطای کم‌تر به‌تنهایی نتیجهٔ مطلوب نیست.

مقایسهٔ «مدل پاسخ داد» با «مدل پاسخ نداد» باید شرایط و هزینهٔ رد را در بر بگیرد. برای تصمیم حساس، confidence خوداظهاری مدل را به‌عنوان تنها trigger انسانی به کار نبرید. در دسترس‌بودن سند، کیفیت retrieval، پیامد پاسخ غلط و دسترسی کاربر به بازبینی مستقل باید در policy کاربرد لحاظ شوند.

## ۱۹. تفسیرپذیری و تبیین‌پذیری را عملیاتی تعریف کنید

واژه‌ها در پژوهش یکدست نیستند؛ در این فصل **تفسیرپذیری** را میزان قابل‌فهم بودن سازوکار/نمایش مدل برای مخاطب و task معین، و **تبیین** را توضیحی دربارهٔ یک پیش‌بینی یا رفتار می‌نامیم. توضیح درونیِ مدل، attribution ویژگی، مثال مشابه، counterfactual و متن تولیدشدهٔ مدل چیزهای یکسانی نیستند. از ابتدا بگویید توضیح برای چه کسی و برای کدام تصمیم است.

این پرسش‌ها را از هم جدا کنید: آیا توضیح با رفتار مدل وفادار است؟ آیا برای کاربر قابل‌فهم است؟ آیا کاربر را بهتر قادر به پیش‌بینی خطا می‌کند؟ آیا می‌فهماند مدل چرا در جهان واقعی این رخداد را پیش‌بینی کرده؟ پاسخ مثبت به یکی، پاسخ مثبت به بقیه نیست. بیشتر ابزارهای XAI به توضیح رفتارِ محاسباتی مدل نزدیک‌اند، نه کشف علت واقعی در جهان.

## ۲۰. مدل ذاتاً تفسیرپذیر را با توضیح post-hoc عوض نکنید

قاعدهٔ ساده، درخت کوچک یا مدل خطی می‌تواند به‌طور مستقیم خوانده و ممیزی شود؛ توضیح LIME یا SHAP معمولاً پس از آموزش یک مدل پیچیده تولید می‌شود. اگر تصمیم پرپیامد است، گاهی بهتر است مدل قابل‌فهم و آزموده انتخاب شود تا به یک لایهٔ توضیح پسینی تکیه کنیم. Rudin این تمایز را در بحث تصمیم‌های high-stakes برجسته می‌کند؛ این پیشنهاد هم به سازه، کاربرد و قیود عملکرد وابسته است.

مدل ساده هم خودبه‌خود عادلانه یا صحیح نیست؛ می‌تواند روی دادهٔ نامناسب ساخته شود و خطاهای مشابه تولید کند. اگر تبیین post-hoc انتخاب شد، نام روش، ورودی، پس‌زمینه، نسخه، target خروجی و روش تولید را ثبت کنید. توضیح را با آزمون‌های وفاداری و آزمون کاربر بسنجید، نه با جذابیت بصری.

## ۲۱. Attribution، surrogate و counterfactual را چگونه بخوانیم؟

LIME یک surrogate محلی را روی نمونه‌های perturbشده پیرامون ورودی می‌آموزد؛ SHAP سهم‌های ویژگی را نسبت به تعریف بازی/پس‌زمینهٔ انتخابی محاسبه می‌کند. هر دو می‌توانند وابسته به انتخاب feature، روش mask، نمونه‌گیری، توزیع زمینه و خروجی مورد توضیح باشند. «ویژگیِ مهم» را به‌تنهایی علت نمی‌خوانیم و سهم‌ها را با تغییر پیاده‌سازی یا زمینه مقایسه می‌کنیم.

Counterfactual می‌گوید اگر ویژگی‌ای تغییر کند، پیش‌بینی طبق مدل چگونه عوض می‌شود؛ تغییر باید ممکن و سازگار با قیود task باشد. مثال «اگر جنسیت یا قومیتت فرق می‌کرد، تصمیم عوض می‌شد» شاید از نظر اجتماعی و علّی نامعتبر یا زیان‌بار باشد. counterfactualهای ناممکن یا خارج از اختیار کاربر را به‌عنوان توصیهٔ عملی ارائه نکنید.

مهم‌تر از واژه، پرسش قابل‌آزمون است: آیا حذف ویژگیِ معرفی‌شده خروجی را مطابق توضیح جابه‌جا می‌کند؟ آیا perturbation معنادار نتیجهٔ متفاوتی می‌دهد؟ آیا توضیح روی ورودی نزدیک بی‌دلیل واژگون می‌شود؟ هر آزمون فقط تعریف مشخصی از fidelity را می‌سنجد.

## ۲۲. متن توضیحی و attention، گزارش مستقیم «فرایند فکر» نیستند

نقشهٔ attention یا saliency را تنها به‌دلیل رنگ یا هم‌راستایی با متن، توضیح faithful ننامید. مطالعهٔ Jain و Wallace نشان داد attention weights در تنظیمات بررسی‌شده همیشه توضیح یکتای خروجی نیستند؛ کارهای بعدی هم دربارهٔ تعریف و استفادهٔ آن بحث کرده‌اند. نتیجهٔ محتاطانه این است که اگر attention را به‌عنوان توضیح عرضه می‌کنید، آزمون مداخله، حساسیت و کاربر را هم ارائه کنید.

متن استدلالیِ تولیدشده پس از پاسخ نیز تضمین نمی‌کند سازوکار واقعی درونی را آشکار کند. FaithLM در EACL 2026 روش‌هایی برای ارزیابی و بهبود fidelity توضیح‌های LLM با مداخله بررسی می‌کند؛ این benchmark و تعریف عملیاتیِ مقاله است، نه اثبات دسترسی به «زنجیرهٔ فکر» پنهان. عبارت «مدل به‌خاطر X چنین تصمیمی گرفت» را تنها هنگامی بنویسید که آزمایشِ معتبر همان ادعا را پشتیبانی کند.

## ۲۳. آزمون وفاداری و sanity check طراحی کنید

چند خانوادهٔ آزمون را ترکیب کنید: **completeness**، آیا سهم‌ها با خروجی تعریف‌شده سازگارند؟ **sensitivity**، آیا تغییر ویژگیِ مهم پاسخ را آن‌طور که پیش‌بینی شده جابه‌جا می‌کند؟ **stability**، آیا ورودی نزدیک توضیح بی‌دلیل متفاوت می‌سازد؟ **randomization/sanity**، آیا توضیح وقتی وزن‌ها یا labelها تصادفی می‌شوند، به مدل حساس است؟ **counterfactual validation**، آیا تغییرات پیشنهادی واقع‌بینانه‌اند؟ نتیجه را با baselineهای ساده و روش‌های جایگزین مقایسه کنید.

هر sanity check وابسته به روش است. اگر مدل ثابت بماند ولی explainer هر بار خروجی متفاوت بدهد، مشکل می‌تواند از explainer باشد؛ اگر خروجی مدل تغییر کند ولی attribution ثابت بماند، توضیح ممکن است اطلاعات لازم را ندهد. «جمع سهم‌ها دقیقاً برابر score است» تنها برای قراردادهایی با خاصیت completeness معنا دارد؛ fidelity همهٔ رفتارها یا causal validity را اثبات نمی‌کند.

## ۲۴. فهم‌پذیری کاربر را جداگانه بسنجید

برای مخاطب واقعی، آزمون کنید آیا توضیح به فرد کمک می‌کند پاسخ مدل را پیش‌بینی، خطا را پیدا، میزان اعتماد خود را تنظیم یا تصمیم مناسب را بگیرد. وضوح ظاهری و رضایت پرسش‌نامه کافی نیست؛ یک توضیح قانع‌کننده ممکن است اعتماد بی‌جا بسازد. آزمایش کاربر باید task، اطلاعات در دسترس، زمان، تصادفی‌سازی و متغیر سنجیده را گزارش کند.

مخاطب را مشخص کنید: توسعه‌دهنده، متخصص دامنه، ارزیاب یا کاربر نهایی نیاز متفاوت دارد. برچسب feature فنی می‌تواند برای کاربر بی‌معنا باشد؛ توضیح ساده‌شده می‌تواند محدودیت مدل را پنهان کند. اگر توضیح برای تصمیم پرپیامد است، بررسی مستقل، امکان اعتراض، منبع قابل‌بررسی و مسئول انسانی را از رابط جداگانه فراهم کنید.

## ۲۵. پروتکل ممیزی از سؤال تا گزارش

پروتکل را پیش از دیدن خروجی به این زنجیره تبدیل کنید: ادعا و کاربرد؛ جمعیت و خطر؛ داده و منشأ؛ rubric و گروه‌ها؛ مدل و نسخه؛ run و تنظیمات؛ معیار اصلی و مکمل؛ بازه و تحلیل خطا؛ محدودیت تعمیم؛ و قاعدهٔ توقف یا اقدام. شناسهٔ دقیق داده، hash فایل‌ها، کد scorer، prompt و تاریخ اجرا را ثبت کنید. این روش کمک می‌کند ممیز دیگری همان آزمایش را بازسازی و نقاط تصمیم‌گیری را ببیند.

| محور | پرسش ممیزی | شاهد قابل‌گزارش | نتیجه‌ای که نباید تعمیم داد |
|---|---|---|---|
| حقیقت و وفاداری | ادعا از کدام منبع و زمینه پشتیبانی می‌شود؟ | ادعای اتمی، منبع، تاریخ و status | حقیقت همهٔ پاسخ‌ها یا نبود hallucination |
| سوگیری | چه تصمیم و گروهی مقایسه شده است؟ | مخرج، خطا، معیار، گروه و عدم‌قطعیت | «منصفانه برای همه» از یک نرخ |
| استحکام | کدام تغییر باید معنا را حفظ کند؟ | جفت معتبر، افت و برش بدترین | امنیت در برابر مهاجم از آزمون عادی |
| تبیین | آیا توضیح از نظر روش faithful است و به چه کسی کمک می‌کند؟ | آزمون مداخله، پایداری و کاربر | دسترسی مستقیم به علت درونی یا جهان |

نتیجهٔ «آزموده نشد» را با «قبول شد» یکی نکنید. اگر داده، ارزیاب، زبان یا دستگاهی در دسترس نیست، آن را صریحاً به‌عنوان پوشش‌نداده ثبت کنید. برای انتشار، آزمون اکتشافی را از تأییدی جدا کنید و نتیجهٔ منفی را نیز نگه دارید.

## ۲۶. مداخله را به علت و خطر پیوند دهید

برای factuality، منبع تاریخ‌دار، نمایش دقیق citation، پاسخ محدود به evidence، abstention و اعتبارسنجی مستقل را آزمایش کنید؛ retrieval بهتر تضمین truth نیست. برای شکاف گروهی، پوشش و کیفیت برچسب را اصلاح کنید، معیارهای ناسازگار را آشکار سازید و اثر تغییر threshold یا policy را برای هر گروه بسنجید. برای shift، مجموعهٔ نماینده و آزمون drift را به‌روزرسانی کنید؛ تغییر مصنوعی را با بازبینی معنایی همراه کنید. برای تبیین، مدل ساده‌تر یا توضیحِ آزموده‌شده را با سنجش وفاداری و استفاده مقایسه کنید.

بعد از هر مداخله، side effectها را بسنجید: آیا کم‌شدن خطای یک گروه، coverage گروه دیگر را کم کرد؟ آیا توضیح ساده‌شده اعتماد بیش‌ازحد ساخت؟ آیا نسخهٔ تازه روی زبان یا task دیگری افت کرد؟ مداخله فقط وقتی گزارش‌پذیر است که داده و معیار پس از تغییر روشن باشند. از تغییر score به‌تنهایی ادعای حل ریشه‌ای نکنید.

## ۲۷. پروژهٔ فصل: آزمایشگاه رفتار با fixture ساختگی

پروژهٔ [آزمایشگاه رفتار مدل فصل ۶۳](book-engineering/projects/63-model-behavior-lab/README.md) با کتابخانهٔ استاندارد Python چهار محاسبهٔ محدود انجام می‌دهد: شمارش status شواهد؛ accuracy، Brier، ECE و برش‌های ساختگی؛ consistency روی جفت‌هایی که در fixture «حفظ‌معنا» علامت خورده‌اند؛ و کنترل جمع‌پذیری یک تابع خطیِ معلوم. پروژه مدل زبانی بارگیری نمی‌کند، شبکه نمی‌زند و حقیقت هیچ ادعای بیرونی را راستی‌آزمایی نمی‌کند.

در پوشهٔ پروژه fixture، manifest، محیط اجرا، خروجی مرجع و ۱۵ آزمون واحد قرار دارد. اجرا:

```text
cd book-engineering/projects/63-model-behavior-lab
python -m unittest -v
python model_behavior_lab.py --output results.json
```

## ۲۸. نتیجهٔ پروژه را درست بخوانید

در fixture، ۴ ادعا «پشتیبانی‌شده»، ۲ «متناقض» و ۲ «نامعلوم» هستند؛ کسر پشتیبانی روی ۶ مورد resolved برابر ۴/۶ است. این عدد تنها حساب همان statusهای ساختگی با rubric پروژه است؛ نرخ توهم هیچ مدل واقعی نیست. `unverified` را از مخرجِ نسبتِ حل‌شده کنار می‌گذاریم، نه اینکه وانمود کنیم درست یا نادرست است.

طبقه‌بند ساختگی ۱۲ ردیف دارد: accuracy برابر ۸/۱۲، Brier حدود ۰٫۱۶۹۸ و ECE پنج‌بازه‌ای حدود ۰٫۱۳۴۲ است. دقت دو cohort ساختگی به‌ترتیب ۵/۶ و ۳/۶ می‌شود و اختلاف توصیفی ۱/۳ است. هر گروه فقط شش ردیف دارد؛ نه فاصلهٔ اطمینان داریم، نه توان استنباط دربارهٔ جمعیت یا ادعای تبعیض.

در شش جفت مصنوعی، prediction consistency برابر ۴/۶، دقت baseline برابر ۵/۶ و دقت variant برابر ۳/۶ است. برچسب «حفظ‌معنا» در دادهٔ آموزشی ساخته شده و اعتبارسنجی انسانی ندارد؛ اعداد فقط نشان می‌دهند برنامه همان داده را چگونه حساب می‌کند. توضیح چهار تابع خطی با جمع‌پذیری دقیق و خطای حذف ویژگی در حد خطای ممیز شناور سازگار است؛ این آزمون ریاضی، faithfulness هیچ توضیح post-hoc را ثابت نمی‌کند.

## ۲۹. محدودیت‌ها و مواردی که این پروژه نمی‌آزماید

هیچ مدل، API، وزن یا پاسخ انسانی به پروژه داده نشده است؛ fixture کوچک، ساختگی و بدون نویز واقعی است. گروه‌های `synthetic_cohort_a` و `synthetic_cohort_b` انسان یا ویژگی حساس را نمایندگی نمی‌کنند. شش جفت تغییریافته داوری معنایی نشده‌اند. ECE به bucket و اندازهٔ نمونه وابسته است؛ این پروژه فاصله، bootstrap، آزمون معناداری یا برآورد توان ندارد.

آزمایش factuality با برچسب fixture، بازیابی منبع، حقیقت بیرونی، سلامت یا حقوقی را بررسی نمی‌کند. آزمون consistency معادل shift واقعی، حمله یا prompt injection نیست. توضیح‌ها متعلق به تابع خطی شناخته‌شده‌اند، نه مدل جعبه‌سیاه؛ کاربر، utility، causal explanation و اعتماد انسانی سنجیده نشده‌اند. مشاهده یا نتیجه را تنها به دامنهٔ آزموده‌شده محدود کنید؛ خروجی CLI گزارش ممیزی محصول نیست.

## ۳۰. چک‌لیست گزارش‌نویسی فصل

- کاربرد، جمعیت هدف، نسخهٔ مدل/داده و ادعای قابل‌ابطال را ثبت کنید.
- برچسب‌های supported، contradicted و unverified و قواعد حل اختلاف را تعریف کنید.
- مخرج، نمونه، گروه، معیار، بازهٔ عدم‌قطعیت و نوع تحلیل را کنار عدد بیاورید.
- برای fairness، معیار انتخابی، معیارهای متعارض، نرخ پایه و پیامد خطا را توضیح دهید.
- برای robustness، معتبر بودن حفظ‌معنا و محور shift را مستند کنید؛ امنیت را از فصل ۶۴ و آزمون عادی جدا نگه دارید.
- برای explanation، روش، مدل مبنا، آزمون وفاداری، مخاطب و utility را از هم گزارش کنید.
- نتیجهٔ نامعلوم، دادهٔ کم، پوشش‌نداده و شکست ابزار را به‌عنوان محدودیت ثبت کنید.
- از نتیجهٔ یک benchmark، میانگین، citation، score توضیح یا آزمون کوچک، گواه کلی نسازید.

## ۳۱. تمرین‌ها

۱. اگر ۴ ادعا supported، ۲ ادعا contradicted و ۲ ادعا unverified باشند، نسبت پشتیبانیِ resolved چند است و چرا نباید آن را ۴/۸ گزارش کرد؟
۲. در fixture فصل، دقت دو cohort برابر ۵/۶ و ۳/۶ است. دقیقاً چه چیزی از این اختلاف می‌توان گفت و چه چیزی دربارهٔ عدالت نمی‌توان نتیجه گرفت؟
۳. ECE پنج‌بازه‌ای چه رابطه‌ای را اندازه می‌گیرد و چرا مقدار آن روی ۱۲ ردیف گواه calibration عمومی نیست؟
۴. consistency جفت‌های مصنوعی ۴/۶ و اختلاف accuracy روی variant برابر منفی ۱/۳ است. دو محدودیت این نتیجه را توضیح دهید.
۵. چرا attention map یا متن استدلالی مدل به‌تنهایی توضیح faithful نیست؟ دو آزمون مناسب پیشنهاد کنید.
۶. در یک مثال RAG، فرق factual truth، پشتیبانی منبع و وفاداری به زمینه را شرح دهید.
۷. برای تصمیمی که نرخ پایهٔ گروه‌ها متفاوت است، دو معیار fairness را مقایسه کنید و بگویید چه اطلاعاتی پیش از انتخاب لازم است.
۸. برای دستیار پاسخ‌گوی پرسش‌های علمی فارسی، طرح ممیزی کوچکی شامل ادعاها، منبع، زیرگروه، تغییر توزیع، معیار uncertainty، کاربر ارزیاب و محدودیت تعمیم بنویسید.

## ۳۲. جمع‌بندی

توهم، سوگیری، استحکام و تبیین‌پذیری چهار نوع پرسش‌اند، نه چهار نام برای یک score. حقیقت را از پشتیبانی و وفاداری جدا کنید؛ برچسب نامعلوم را حفظ کنید؛ مخرج، گروه، منبع و نسخه را ثبت کنید؛ و معیار fairness را با پیامد و trade-off انتخاب کنید. آزمون استحکام به تغییرهای معتبر و حفظ معنا نیاز دارد؛ توضیح هم باید از نظر fidelity و utility آزموده شود.

پروژهٔ فصل، فقط محاسبات fixture کوچک و ساختگی را تأیید می‌کند. نتیجهٔ آن دربارهٔ مدل واقعی، مردم یا محصول نیست. حملهٔ هدفمند و حریم خصوصی در فصل ۶۴، و حاکمیت و مستندسازی در فصل ۶۵ دنبال می‌شوند؛ برای طراحی آزمون و تحلیل عدم‌قطعیت به [فصل ۶۲](62-benchmarking-evaluation.md) بازگردید. [پاسخ‌نامهٔ مستقل فصل ۶۳](book-engineering/answers/63-hallucination-bias-robustness-fa.md)، [گزارش ممیزی](book-engineering/chapters/63-audit-report-fa.md) و [پروژهٔ فصل](book-engineering/projects/63-model-behavior-lab/README.md) تکمیل‌کنندهٔ این فصل‌اند.

## ۳۳. منابع و تاریخ بازبینی

تاریخ بررسی منابع و پیوندهای رسمی: ۷ نوامبر ۲۰۲۶. منابع زیر پشتیبان تعریف‌ها و نمونه‌های پژوهشی‌اند؛ benchmarkهای تازه را استاندارد قطعی یا نتیجهٔ جهان‌شمول تلقی نکنید.

- NIST. *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile* (AI 600-1), 2024. [گزارش رسمی](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
- Zhang et al. “Siren’s Song in the AI Ocean: A Survey on Hallucination in Large Language Models.” *Computational Linguistics*, 2025. [ACL Anthology](https://aclanthology.org/2025.cl-4.9/)
- Min et al. “FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation.” EMNLP, 2023. [ACL Anthology](https://aclanthology.org/2023.emnlp-main.741/)
- Marinescu et al. “FactReasoner.” Findings of EMNLP, 2025. [ACL Anthology](https://aclanthology.org/2025.findings-emnlp.785/)
- Chen et al. “TRIVIA+.” ACL, 2026. [ACL Anthology](https://aclanthology.org/2026.acl-long.680/)
- Abu Ahmad et al. “Does Finetuning with Scientific Data Increase Hallucinations? (SciFactCheck).” EMNLP, 2026. [ACL Anthology](https://aclanthology.org/2026.emnlp-main.610/)
- Seegmiller & Preum. “Measuring Distribution Shift in User Prompts and Its Effects on LLM Performance (LENS).” ACL, 2026. [ACL Anthology](https://aclanthology.org/2026.acl-long.1508/)
- Lukk. “FairFund-Bench: Evaluating Distributive Bias in LLM Resource Allocation.” Findings of EMNLP, 2026. [ACL Anthology](https://aclanthology.org/2026.findings-emnlp.1340/)
- Parrish et al. “BBQ: A hand-built bias benchmark for question answering.” Findings of ACL, 2022. [ACL Anthology](https://aclanthology.org/2022.findings-acl.165/)
- Koh et al. “WILDS: A Benchmark of in-the-Wild Distribution Shifts.” ICML/PMLR, 2021. [PMLR](https://proceedings.mlr.press/v139/koh21a.html)
- Guo et al. “On Calibration of Modern Neural Networks.” ICML/PMLR, 2017. [PMLR](https://proceedings.mlr.press/v70/guo17a.html)
- Chouldechova. “Fair Prediction with Disparate Impact: A Study of Bias in Recidivism Prediction Instruments.” *Big Data*, 2017. [SAGE](https://journals.sagepub.com/doi/abs/10.1089/big.2016.0047)
- Ribeiro et al. “Why Should I Trust You? Explaining the Predictions of Any Classifier.” NAACL, 2016. [ACL Anthology](https://aclanthology.org/N16-3020/)
- Lundberg & Lee. “A Unified Approach to Interpreting Model Predictions.” NeurIPS, 2017. [NeurIPS proceedings](https://proceedings.neurips.cc/paper_files/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html)
- Jain & Wallace. “Attention is not Explanation.” NAACL, 2019. [ACL Anthology](https://aclanthology.org/N19-1357/)
- Adebayo et al. “Sanity Checks for Saliency Maps.” NeurIPS, 2018. [Google Research](https://www.research.google/pubs/sanity-checks-for-saliency-maps/)
- Rudin. “Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead.” *Nature Machine Intelligence*, 2019. [Nature](https://www.nature.com/articles/s42256-019-0048-x)
- Choudhury et al. “FaithLM: Towards Faithful Explanations for Large Language Models.” EACL, 2026. [ACL Anthology](https://aclanthology.org/2026.eacl-long.177/)

## ۳۴. پیوست اجرایی: کد کامل آزمایشگاه

کد زیر بایت‌به‌بایت با فایل آزموده‌شدهٔ پروژه تطبیق داده می‌شود. کد یک fixture محلی می‌خواند؛ مدل یا شبکهٔ بیرونی را فراخوانی نمی‌کند.

```python
"""Audit a deliberately synthetic model-behavior fixture.

This teaching utility computes descriptive claim-evidence, group-slice,
calibration, paired-perturbation, and toy-linear-explanation summaries. It does
not load a model, retrieve real evidence, infer social fairness, or certify safety.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_FIXTURE = ROOT / "synthetic_behavior_fixture.json"
CLAIM_STATUSES = {"supported", "contradicted", "unverified"}


def _finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def _binary(value: Any, name: str) -> int:
    if type(value) is not int or value not in (0, 1):
        raise ValueError(f"{name} must be integer 0 or 1")
    return value


def _unique_ids(rows: list[dict[str, Any]], name: str) -> None:
    ids = [row.get("id") for row in rows]
    if any(not isinstance(item, str) or not item.strip() for item in ids):
        raise ValueError(f"{name} rows need non-empty string IDs")
    if len(ids) != len(set(ids)):
        raise ValueError(f"{name} IDs must be unique")


def validate_fixture(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict) or data.get("synthetic") is not True:
        raise ValueError("fixture must explicitly identify itself as synthetic")
    if data.get("fixture_id") != "v5-ch02-synthetic-behavior-v1":
        raise ValueError("unexpected fixture_id")
    required = ("claims", "classification_cases", "robustness_pairs", "explanation_cases")
    for key in required:
        if not isinstance(data.get(key), list) or not data[key]:
            raise ValueError(f"{key} must be a non-empty list")
        _unique_ids(data[key], key)

    for row in data["claims"]:
        if row.get("status") not in CLAIM_STATUSES:
            raise ValueError(f"claim {row.get('id')} has an unsupported evidence status")
        if not isinstance(row.get("evidence_id"), str) or not row["evidence_id"].strip():
            raise ValueError(f"claim {row.get('id')} needs a fixture evidence_id")

    for row in data["classification_cases"]:
        _binary(row.get("label"), f"{row.get('id')}.label")
        probability = _finite_number(row.get("probability_positive"), f"{row.get('id')}.probability_positive")
        if not 0.0 <= probability <= 1.0:
            raise ValueError(f"{row.get('id')}.probability_positive must be in [0, 1]")
        group = row.get("group")
        if not isinstance(group, str) or not group.strip():
            raise ValueError(f"{row.get('id')} needs a non-empty synthetic group label")

    for row in data["robustness_pairs"]:
        _binary(row.get("true_label"), f"{row.get('id')}.true_label")
        _binary(row.get("baseline_prediction"), f"{row.get('id')}.baseline_prediction")
        _binary(row.get("variant_prediction"), f"{row.get('id')}.variant_prediction")
        if row.get("label_preserving") is not True:
            raise ValueError(f"{row.get('id')} is not declared label-preserving in the synthetic fixture")
        if not isinstance(row.get("transformation"), str) or not row["transformation"].strip():
            raise ValueError(f"{row.get('id')} needs a transformation label")

    for row in data["explanation_cases"]:
        _finite_number(row.get("intercept"), f"{row.get('id')}.intercept")
        weights, features = row.get("weights"), row.get("features")
        if not isinstance(weights, dict) or not isinstance(features, dict) or not weights:
            raise ValueError(f"{row.get('id')} needs non-empty weights and features")
        if set(weights) != set(features):
            raise ValueError(f"{row.get('id')} weight and feature names must match")
        for name in weights:
            _finite_number(weights[name], f"{row.get('id')}.weights.{name}")
            _finite_number(features[name], f"{row.get('id')}.features.{name}")
    return data


def audit_claim_evidence(claims: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {status: 0 for status in sorted(CLAIM_STATUSES)}
    for row in claims:
        counts[row["status"]] += 1
    resolved = counts["supported"] + counts["contradicted"]
    return {
        "claim_count": len(claims),
        "counts_by_fixture_status": counts,
        "resolved_count": resolved,
        "support_fraction_among_resolved": counts["supported"] / resolved if resolved else None,
        "unverified_count_excluded_from_denominator": counts["unverified"],
        "interpretation": "fixture evidence labels only; not a measured hallucination rate or a truth oracle",
    }


def _classification_metrics(rows: list[dict[str, Any]], bins: int = 5) -> dict[str, Any]:
    tp = tn = fp = fn = 0
    brier_total = 0.0
    confidence_rows: list[tuple[float, int]] = []
    for row in rows:
        label = row["label"]
        probability = float(row["probability_positive"])
        prediction = int(probability >= 0.5)
        if prediction == 1 and label == 1:
            tp += 1
        elif prediction == 0 and label == 0:
            tn += 1
        elif prediction == 1 and label == 0:
            fp += 1
        else:
            fn += 1
        brier_total += (probability - label) ** 2
        confidence = probability if prediction == 1 else 1.0 - probability
        confidence_rows.append((confidence, int(prediction == label)))

    total = len(rows)
    accuracy = (tp + tn) / total if total else None
    calibration_bins: list[dict[str, Any]] = []
    ece = 0.0
    for index in range(bins):
        lower = 0.5 + 0.5 * index / bins
        upper = 0.5 + 0.5 * (index + 1) / bins
        members = [
            (confidence, correct)
            for confidence, correct in confidence_rows
            if (
                lower <= confidence <= upper
                if index == bins - 1
                else lower <= confidence < upper
            )
        ]
        mean_confidence = sum(item[0] for item in members) / len(members) if members else None
        bin_accuracy = sum(item[1] for item in members) / len(members) if members else None
        gap = abs(mean_confidence - bin_accuracy) if members else None
        if members:
            ece += len(members) / total * float(gap)
        calibration_bins.append({
            "lower_inclusive": round(lower, 6),
            "upper_inclusive": index == bins - 1,
            "upper": round(upper, 6),
            "count": len(members),
            "mean_confidence": mean_confidence,
            "accuracy": bin_accuracy,
            "absolute_gap": gap,
        })

    return {
        "count": total,
        "threshold": 0.5,
        "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
        "accuracy": accuracy,
        "true_positive_rate": tp / (tp + fn) if tp + fn else None,
        "false_positive_rate": fp / (fp + tn) if fp + tn else None,
        "brier_score": brier_total / total if total else None,
        "top_label_ece_equal_width_5_bins": ece if total else None,
        "calibration_bins": calibration_bins,
        "calibration_note": "top-label ECE depends on binning and sample size; it is not a complete calibration certificate",
    }


def audit_classification(cases: list[dict[str, Any]]) -> dict[str, Any]:
    overall = _classification_metrics(cases)
    groups = sorted({row["group"] for row in cases})
    by_group = {
        group: _classification_metrics([row for row in cases if row["group"] == group])
        for group in groups
    }

    def gap(metric: str) -> float | None:
        values = [item[metric] for item in by_group.values() if item[metric] is not None]
        return max(values) - min(values) if len(values) >= 2 else None

    return {
        "overall": overall,
        "synthetic_group_slices": by_group,
        "max_absolute_group_gap": {
            "accuracy": gap("accuracy"),
            "true_positive_rate": gap("true_positive_rate"),
            "false_positive_rate": gap("false_positive_rate"),
        },
        "scope": "descriptive fixture slices; no real population, protected group, or fairness criterion is represented",
    }


def audit_robustness_pairs(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(pairs)
    unchanged = sum(row["baseline_prediction"] == row["variant_prediction"] for row in pairs)
    baseline_correct = sum(row["baseline_prediction"] == row["true_label"] for row in pairs)
    variant_correct = sum(row["variant_prediction"] == row["true_label"] for row in pairs)
    return {
        "label_preserving_pair_count": count,
        "prediction_consistency": unchanged / count if count else None,
        "prediction_changed_count": count - unchanged,
        "baseline_accuracy_on_pairs": baseline_correct / count if count else None,
        "variant_accuracy_on_pairs": variant_correct / count if count else None,
        "accuracy_difference_variant_minus_baseline": (variant_correct - baseline_correct) / count if count else None,
        "interpretation": "synthetic paired stress cases only; transformations are not human-validated and this is not an adversarial-security test",
    }


def audit_toy_explanations(rows: list[dict[str, Any]]) -> dict[str, Any]:
    case_results = []
    max_additivity_error = 0.0
    max_ablation_error = 0.0
    for row in rows:
        contributions = {
            name: float(row["weights"][name]) * float(row["features"][name])
            for name in sorted(row["weights"])
        }
        score = float(row["intercept"]) + sum(contributions.values())
        reconstructed = float(row["intercept"]) + sum(contributions.values())
        additivity_error = abs(score - reconstructed)
        max_additivity_error = max(max_additivity_error, additivity_error)
        ablation_errors = {}
        for name in contributions:
            ablated_score = float(row["intercept"]) + sum(
                contribution for other, contribution in contributions.items() if other != name
            )
            ablation_delta = score - ablated_score
            ablation_errors[name] = abs(ablation_delta - contributions[name])
            max_ablation_error = max(max_ablation_error, ablation_errors[name])
        top_feature = max(contributions, key=lambda name: abs(contributions[name]))
        case_results.append({
            "id": row["id"],
            "toy_score": score,
            "contributions": contributions,
            "largest_absolute_contribution": top_feature,
            "additivity_error": additivity_error,
            "ablation_errors": ablation_errors,
        })
    return {
        "case_count": len(rows),
        "max_additivity_error": max_additivity_error,
        "max_ablation_error": max_ablation_error,
        "cases": case_results,
        "interpretation": "arithmetic checks for a known toy linear function only; not evidence of causal or human-faithful explanations for a black-box model",
    }


def analyze(data: dict[str, Any], fixture_bytes: bytes) -> dict[str, Any]:
    validate_fixture(data)
    return {
        "fixture_id": data["fixture_id"],
        "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "claim_evidence_audit": audit_claim_evidence(data["claims"]),
        "classification_audit": audit_classification(data["classification_cases"]),
        "paired_robustness_audit": audit_robustness_pairs(data["robustness_pairs"]),
        "toy_explanation_audit": audit_toy_explanations(data["explanation_cases"]),
        "limitations": [
            "All records, labels, evidence statuses, groups, probabilities, transformations, and model scores are synthetic.",
            "No real language model, external source, human annotation, or deployment was queried.",
            "Small group slices and calibration bins are descriptive; no confidence interval or significance test is estimated.",
            "Fixture evidence support is not a truth oracle; unresolved claims are excluded from the support fraction.",
            "The perturbation pairs are not human-validated, and robustness to these pairs does not imply robustness to distribution shift or attack.",
            "Toy linear additivity does not establish the faithfulness, causality, or usefulness of post-hoc explanations for a black-box model.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, help="write deterministic JSON to this path")
    args = parser.parse_args()
    raw = args.fixture.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    result = analyze(data, raw)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote synthetic behavior audit: {args.output}")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
```

---

# جلد پنجم، فصل ۳ — Red Teaming، حملات خصمانه، Prompt Injection، مسموم‌سازی داده، استخراج مدل و حریم خصوصی

**نگاشت:** فصل محلی ۳ جلد پنجم = فصل سراسری ۶۴. **تاریخ بازبینی منابع: ۷ نوامبر ۲۰۲۶.** فصل ۶۳ کیفیت رفتاری، حقیقت، سوگیری، تغییر توزیع و توضیح را در قالب ارزیابی محدود بررسی کرد؛ این فصل همان سامانه را از دید مهاجمی می‌سنجد که می‌خواهد محرمانگی، یکپارچگی یا دسترس‌پذیری را نقض کند یا اختیار سامانه را به کار بگیرد. فصل ۶۵ حاکمیت، هم‌ترازی، مستندسازی و مدیریت ریسک را می‌پوشاند. Red Teaming جایگزین آزمون نرم‌افزار، threat modeling یا کنترل‌های امنیتی نیست و موفقیت در چند آزمون به‌معنای امنیت محصول نیست.

**پیش‌نیاز:** شناخت چرخهٔ عمر مدل و داده، API و مجوزهای نرم‌افزاری، تقسیم داده، اجرای آزمون و تفاوت مدل با محصول متصل به ابزار. **خروجی:** بتوانید دامنه و مجوز یک آزمون خصمانه را دقیق کنید، مدل تهدید و سناریوهای قابل‌تکرار بسازید، Prompt Injection را از آسیب‌پذیریِ سطح ابزار و داده جدا کنید، خطرهای poisoning، استخراج مدل و حریم خصوصی را با کنترل‌های متناسب بررسی کنید، و شواهد و محدودیت را بدون ادعای کلی گزارش دهید.

![شکل ۵-۳-۱ — چرخه از تعیین دامنه و مجوز به مدل تهدید و آزمون، سپس اجرای کنترل‌های مستقل و ثبت شواهد می‌رسد؛ نتیجه برای اصلاح و آزمون دوباره بازمی‌گردد. چهار سطح آزمون ورودی مستقیم، محتوای بازیابی و ابزار، داده و زنجیرهٔ تأمین، و حریم خصوصی و پرس‌وجو را جدا می‌کنند. خروجی فقط دربارهٔ هدف، سناریو و نسخهٔ آزموده‌شده معتبر است و نمودار تضمین امنیت کلی نمی‌دهد.](book-engineering/diagrams/v5-ch03-red-team-pipeline.svg)

**شکل ۵-۳-۱ —** آزمون خصمانه یک چرخهٔ مجاز، نسخه‌مند و تکرارشونده است؛ کنترل‌های مستقل باید اثر حمله را محدود و شواهد را برای اصلاح قابل‌بررسی کنند.

## ۱. از ارزیابی رفتار به آزمون امنیتی

آزمون فصل ۶۳ می‌پرسد مدل در یک جمعیت یا مجموعهٔ ورودی چه رفتاری دارد؛ Red Teaming می‌پرسد آیا کنشگرِ دارای هدف و دسترسی مشخص می‌تواند مرز امنیتی سامانه را نقض کند. این دو روش هم‌پوشانی دارند، اما مترادف نیستند. ورودیِ غیرمعمول می‌تواند آزمون استحکام باشد؛ اگر هدفش افشای داده، اجرای عمل غیرمجاز یا دورزدن کنترل است، یک سناریوی خصمانه است. نتیجه باید به همان هدف و پیکربندی محدود بماند.

داراییِ مورد آزمون فقط وزن مدل نیست. برنامهٔ کاربردی، promptها، حافظه، منابع RAG، ابزارها، حساب‌های کاربری، پایپ‌لاین آموزش، مدل‌های پایه و adapterها، لاگ‌ها و سرویس inference هم مرزهای امنیتی دارند. آسیب‌پذیری ممکن است در مدل، اتصال‌های نرم‌افزاری، سیاست مجوز یا گردش کار انسانی باشد؛ بنابراین گزارش «مدل امن/ناامن است» معمولاً بیش از شواهد نتیجه می‌گیرد.

## ۲. هدف امنیتی را به ناوردای قابل‌آزمون تبدیل کنید

پیش از ساخت سناریو بگویید کدام خاصیت نباید نقض شود: پاسخ‌دهی نباید رازِ متعلق به کاربر دیگری را افشا کند؛ محتوای بازیابی‌شده نباید به‌تنهایی مجوز اجرای ابزار بسازد؛ درخواست یک هویت کم‌دسترسی نباید با هویت سرویسِ پُرامتیاز اجرا شود؛ یا دادهٔ بی‌منشأ نباید بی‌بررسی وارد آموزش شود. جملهٔ «مدل نباید بد باشد» آزمون‌پذیر نیست؛ «این درخواست با این هویت و در این نسخه نباید عملیات نوشتن را انجام دهد» قابل‌بررسی است.

برای هر ناوردا دارایی، مرز اعتماد، عامل مجاز، پیامد نقض و شاهد موفقیت یا شکست را تعریف کنید. محرمانگی، یکپارچگی و دسترس‌پذیری محورهای مفیدی‌اند، اما در سیستم‌های AI باید اثر بر فرد، تصمیم یا عملیات پایین‌دستی را نیز بنویسید. یک پاسخ متنیِ بی‌ضرر می‌تواند در یک محصولِ متصل به پرداخت یا پروندهٔ پزشکی، آغازگر پیامد جدی‌تری شود.

## ۳. مجوز و قواعد توقف، بخشی از طراحی آزمون‌اند

آزمون خصمانه فقط در دامنه‌ای انجام می‌شود که مالک سیستم کتبی و روشن مجاز کرده است. پیش از اجرا، هدف، محیط، URL یا سرویس، حساب‌ها و نقش‌ها، بازهٔ زمانی، نوع داده، حجم درخواست، عملیات مجاز و ممنوع، افراد تماس و شیوهٔ نگهداری شواهد را ثبت کنید. آزمون را از داده و حساب واقعیِ خارج از مجوز جدا نگه دارید؛ برای سناریوی افشا از canary ساختگی استفاده کنید، نه راز واقعی.

قواعد توقف را از پیش بنویسید: مشاهدهٔ دادهٔ واقعیِ خارج از scope، اثر روی کاربر ثالث، افزایش غیرمنتظرهٔ هزینه یا بار، انجام عملیات برگشت‌ناپذیر، یا از دست‌رفتن کنترل محیط. در این حالت آزمون متوقف، شواهد لازم حداقلی نگهداری و مالک سیستم مطلع می‌شود. مجوزِ نوشتن روی یک محیط آزمایشی، مجوزِ استخراج داده از کاربر یا سرویس دیگری نیست.

## ۴. مدل تهدید را برای سامانهٔ کامل بسازید

یک threat model کوتاه باید عامل، هدف، دانسته‌ها، دسترسی، سطح ورود، دارایی هدف، پیامد، کنترل موجود و نقطهٔ تشخیص را کنار هم بیاورد. مهاجم ممکن است کاربر عادی، شریک زنجیرهٔ تأمین، صاحب دادهٔ آلوده، یا فردی با دسترسی query-only باشد؛ فرض‌ها را به «مهاجم همه‌چیز می‌داند» یا «مهاجم هیچ نمی‌داند» تقلیل ندهید. سامانهٔ سادهٔ گفتگو، RAG و agent دارای ابزار، سطح حملهٔ یکسان ندارند.

| پرسش | نمونهٔ تصمیمی که باید ثبت شود |
|---|---|
| چه چیزی ارزش حفاظت دارد؟ | سند خصوصی، وزن مدل، دادهٔ آموزش، credential، اعتبار تصمیم یا دسترس‌پذیری |
| مهاجم از کجا وارد می‌شود؟ | UI، API، محتوای بازیابی، فایل، tool response، dataset یا artifact ثالث |
| چه توان و دانشی دارد؟ | query-only، نقش داخلی محدود، دسترسی به artifact یا شناخت کنترل‌های دفاعی |
| چه کاری نباید رخ دهد؟ | افشا، تغییر داده، اجرای ابزار، استخراج مدل، تخریب یا مصرف غیرمجاز منابع |
| چه شاهدی کافی است؟ | شناسهٔ نسخه، request ID، تصمیم policy، اثر ابزار، دادهٔ ساختگی و زمان ثبت |

## ۵. دسترسی سیاه‌جعبه‌ای، خاکستری و سفید را قاطی نکنید

در مدل تهدید **black-box** ممکن است مهاجم فقط به رابط عادی و خروجی دسترسی داشته باشد؛ **gray-box** می‌تواند معماری، بخشی از پیکربندی یا نمونه‌ای از توزیع داده را بداند؛ **white-box** فرض می‌کند اطلاعاتی مانند معماری و پارامترها در دسترس است. این دسته‌ها درجهٔ واقع‌گرایی یا اخلاقی‌بودن آزمون نیستند؛ فرض‌های آزمون‌اند. آزمون white-box برای بررسی بدترین حالت یا ارزیابی دفاع می‌تواند مفید باشد، هرچند با دسترسی مهاجم معمولی برابر نیست.

برای هر سناریو مشخص کنید پاسخ شامل label، score، token log-probability، متن آزاد، tool call یا artifact است. میزان اطلاعات خروجی، تعداد queryهای مجاز و امکان تکرار را هم ثبت کنید. تفاوت دو آزمایش را به «مدل بهتر دفاع کرد» نسبت ندهید اگر یکی به logits و دیگری فقط به پاسخ نهایی دسترسی داشته است.

## ۶. خانواده‌های حمله را با هدف و مرحله دسته‌بندی کنید

NIST در گزارش AI 100-2e2025 حمله‌های adversarial machine learning را با واژگان و مفروضات مربوط به هدف، مرحلهٔ چرخهٔ عمر، دانش و دسترسی دسته‌بندی می‌کند؛ از جمله evasion، poisoning و privacy attacks، با ملاحظات ویژهٔ سامانه‌های مولد. در این فصل این طبقه‌بندی را نقشهٔ طراحی آزمون می‌گیریم، نه فهرست جامع یا استانداردِ قبولی.

| خانواده | مرحله یا نقطهٔ ورود | پرسش امنیتی نمونه |
|---|---|---|
| Evasion و ورودی خصمانه | زمان استنتاج | آیا تغییر ورودیِ تعریف‌شده تصمیم را به‌نحوی زیان‌بار عوض می‌کند؟ |
| Prompt Injection و jailbreak | ورودی یا زمینهٔ مدل | آیا ورودی نامطمئن، دستور مجاز یا کنترل را دور می‌زند؟ |
| Poisoning و backdoor | داده، آموزش، fine-tuning یا حافظه | آیا نمونه یا trigger کنترل‌نشده رفتار هدف‌دار می‌سازد؟ |
| Privacy و استخراج | API، خروجی یا دادهٔ آموزش | آیا queryها اطلاعات عضویت، نمونه‌ها یا رفتار/مدل را آشکار می‌کنند؟ |
| سوءاستفاده از اختیار عامل | ابزار و سرویس پایین‌دستی | آیا خروجی مدل به عملِ خارج از اختیار تبدیل می‌شود؟ |
| مصرف بی‌مهار | درخواست، مدل یا ابزار | آیا ورودی/حلقهٔ پرهزینه منابع یا ظرفیت را بی‌تناسب مصرف می‌کند؟ |

در محصول واقعی خانواده‌ها به‌هم متصل‌اند: تزریق در سند می‌تواند به tool call برسد، و دسترسی ابزار به داده ممکن است افشا را ممکن کند. ثبت زنجیرهٔ رخداد از انتخاب یک برچسب حملهٔ واحد دقیق‌تر است.

## ۷. حمله را در سراسر چرخهٔ عمر ردیابی کنید

سطح حمله از گردآوری داده آغاز می‌شود، از label کردن، پیش‌آموزش، fine-tuning و تبدیل مدل می‌گذرد و به retrieval، inference، ابزارها، telemetry و بازنشستگی می‌رسد. تیم‌ها گاهی تنها ورودی endpoint را red-team می‌کنند، درحالی‌که مهاجم می‌تواند data pipeline یا artifactی را دست‌کاری کند که بعداً «ورودی معتبر» به نظر می‌رسد. inventory و provenance باید شامل کد، مدل، adapter، tokenizer، dataset، prompt و اتصال پایین‌دستی باشد.

تغییر provider، revision مدل، index، prompt، ابزار، نقش، policy یا محیط می‌تواند فرض آزمون را باطل کند. ثبت شناسهٔ نسخه و hash کمک می‌کند بدانیم دقیقاً چه چیزی آزموده شده است؛ اما hash به‌تنهایی کیفیت یا بی‌خطری محتوا را تضمین نمی‌کند. تغییر مؤثر باید trigger بازبینی ریسک و آزمون متناسب باشد.

## ۸. Prompt Injection و jailbreak را هم‌معنا نگیرید

**Prompt Injection** حمله‌ای است که با دست‌کاری ورودی یا محتوای دیده‌شده به‌وسیلهٔ مدل، آن را به رفتار ناخواسته می‌کشاند؛ **jailbreak** معمولاً تلاش برای دورزدن محدودیت‌های رفتاری یا محتوایی مدل را توصیف می‌کند. این دو می‌توانند هم‌زمان باشند، اما هر jailbreak به ابزار یا دادهٔ بیرونی نیاز ندارد و هر prompt injection الزاماً به تولید محتوای ممنوع ختم نمی‌شود. معیار امنیتی باید پیامد تعریف‌شده باشد، نه صرفاً اینکه مدل عبارتی نامعمول گفته است.

MITRE ATLAS برای Prompt Injection شناسهٔ AML.T0051 را نگه می‌دارد و زیرنوع‌های direct، indirect و triggered را جدا می‌کند. OWASP Top 10 for LLM Applications 2026 نیز Prompt Injection را LLM01 و ریسک‌هایی مانند افشای اطلاعات حساس، اختیار بیش‌ازحد و مسموم‌سازی داده/مدل را در ورودی‌های جداگانه فهرست می‌کند. این دسته‌بندی‌ها برای سازمان‌دهی آزمون مفیدند؛ رتبه یا شمارهٔ یک فهرست، احتمال رخداد برای محصول خاص را اندازه نمی‌گیرد.

## ۹. تزریق مستقیم، غیرمستقیم و وابسته به رویداد

در تزریق مستقیم، ورودیِ خصمانه از همان رابطی می‌آید که کاربر با آن تعامل می‌کند. در تزریق غیرمستقیم، دستور در داده‌ای قرار می‌گیرد که مدل بنا بر وظیفه‌اش می‌خواند: صفحهٔ وب، ایمیل، فایل، سند بازیابی‌شده، پاسخ ابزار یا حافظه. در حالت triggered، دستور تنها پس از رخدادی مانند خواندن منبع، رسیدن به وضعیت معین یا فراخوانی مرحلهٔ بعدی فعال می‌شود. بنابراین آزمونِ فقط روی کادر prompt می‌تواند سطح‌های ورود واقعی را از قلم بیندازد.

NIST AI 600-1 در بخش Information Security، prompt injection مستقیم و غیرمستقیم را در زمرهٔ ریسک‌های امنیتی GenAI می‌آورد. اقدام پیشنهادی MS-2.7-007 صریحاً Red Teaming را برای سنجش تاب‌آوری در برابر سوءاستفادهٔ تسهیل‌شده با AI، prompt injection و حمله‌هایی مانند adversarial example/prompt، data poisoning، membership inference و model extraction مطرح می‌کند. این «اقدام پیشنهادی» در یک پروفایل داوطلبانه است، نه گواهی اجباری یا تضمین فنی.

## ۱۰. دادهٔ نامطمئن را با دستور معتبر یکی نکنید

مدل‌های زبانی متن دستورگونه را در همان کانال زبانی می‌خوانند که متن عادی را؛ برچسب «محتوای نامطمئن» در prompt کمک می‌کند، اما مرز امنیتی قطعی نیست. دادهٔ بیرونی را منشأدار، محدود و جداگانه نمایش دهید؛ متن بازیابی‌شده را از مجوز برنامه جدا نگه دارید؛ و هر اقدام پایین‌دستی را پیش از اجرا با policy قطعیِ خارج از مدل بررسی کنید. درخواست از مدل برای «نادیده‌گرفتن دستور مخرب» به‌تنهایی کنترل دسترسی نیست.

آزمون باید هم دو پرسش را بپرسد: آیا مدل محتوای نامطمئن را به‌عنوان داده تفسیر کرده است؟ و اگر نه، آیا کنترل مستقل جلوی افشا یا عمل را گرفت؟ آزمون اول دربارهٔ رفتار احتمالاتی مدل است؛ آزمون دوم دربارهٔ مرز امنیتی سامانه. محصولی که در پرسش اول شکست می‌خورد اما عمل غیرمجاز را با مجوز مستقل مسدود می‌کند، هنوز نیازمند کاهش ریسک است، ولی اثرش با اجرای واقعی عمل برابر نیست.

## ۱۱. RAG، پایگاه برداری و حافظه را سطح حمله بدانید

در Retrieval-Augmented Generation، سند و metadata از ورودیِ قابل‌اعتمادترِ برنامه نیستند مگر منشأ و مجوزشان اثبات شده باشد. دسترسی کاربر را پیش از retrieval اعمال کنید تا chunk متعلق به tenant دیگر وارد زمینه نشود؛ منشأ، نسخه و سطح محرمانگی chunk را تا پاسخ نگه دارید؛ و index، cache و حافظهٔ پایدار را در آزمون‌های حذف و تغییر دسترسی بگنجانید. کنترل دسترسی بعد از تولید پاسخ، اگر داده از مرز گذشته باشد، کافی نیست.

برای هر منبع، آزمون‌های جداگانه بسازید: سند سالم و مرتبط؛ سند سالم اما دسترسی‌ندار؛ سند با دستور نامطمئن؛ دادهٔ تاریخ‌گذشته؛ metadata ناسازگار؛ و نتیجهٔ خالی یا مبهم. در خروجی بررسی کنید آیا سند غیرمجاز بازیابی، خلاصه، نقل یا به کاربر دیگری نسبت داده شده است. prompt injection داخل متن بازیابی‌شده را با fixture بی‌خطر و سند ساختگی بسنجید؛ هیچ سند واقعیِ محرمانه‌ای را به‌عنوان «طعمه» منتشر نکنید.

## ۱۲. اختیار ابزار را به مجوز کاربر و برنامه گره بزنید

ریسک عامل زمانی بیشتر می‌شود که مدل بتواند ابزار، پایگاه داده، ایمیل، فایل یا گردش کار را صدا بزند. طراحی امن تعداد ابزارها و هر ابزار را به حداقل لازم می‌رساند، schema ورودی را در کد اعتبارسنجی می‌کند، مجوز را برای هر عمل در سامانهٔ پایین‌دستی دوباره می‌سنجد و حساب کاربریِ جاری را به فراخوانی منتقل می‌کند. مدل ممکن است پیشنهاد دهد؛ policy مستقل باید تصمیم بگیرد که آیا عملیات مجاز است.

برای عمل حساس، reversible بودن، مبلغ، دامنهٔ اثر، مقصد و وضعیت حساب را پیش از اجرا کنترل کنید. عمل پرپیامد یا برگشت‌ناپذیر را برای تأیید انسانی متوقف کنید؛ برای عملِ محدود و قابل‌بازگشت می‌توان policy مرحله‌ای داشت. لاگِ tool call و نتیجهٔ واقعی را به همان شناسهٔ درخواست متصل کنید. پاسخ متنیِ «من این کار را انجام دادم» شاهد اجرای ابزار نیست؛ و نبود چنین جمله‌ای نیز اثبات نمی‌کند عمل رخ نداده است.

## ۱۳. ورودی چندوجهی و تبدیل‌های میانی را بگنجانید

مدل ممکن است از تصویر، OCR، PDF، صوت، زیرنویس، ویدئو، metadata یا خروجی transcriber دستور بگیرد. محتوای نامطمئن می‌تواند در یک modality وارد شود، در مرحلهٔ دیگری به متن تبدیل شود و سپس مانند زمینهٔ عادی به مدل برسد. فیلتر متنیِ پیش از OCR ممکن است چیزی را نبیند که بعداً وارد prompt می‌شود؛ فیلتر پس از OCR نیز همهٔ ابهام‌های بصری یا زبانی را حل نمی‌کند.

آزمون چندوجهی باید مسیر تبدیل را ثبت کند: فایل خام، ابزار استخراج، متن نهایی و provenance. نسخه‌های مجاز و ساختگی برای بررسی OCR، caption، metadata و ترکیب چندورودی استفاده کنید. نتیجه را به همان preprocessing، مدل و مسیر محدود کنید؛ عبور از یک نمونهٔ تصویر یا صوتی، مقاومت عمومی چندوجهی را ثابت نمی‌کند.

## ۱۴. پروندهٔ آزمون خصمانه را قابل‌بازتولید تعریف کنید

هر test case باید شناسه، هدف امنیتی، دارایی، نقطهٔ ورود، توان مهاجم، پیش‌شرط، نسخهٔ سامانه، اقدام مجاز، ناوردای موردانتظار، شاهد، معیار شدت، روش توقف و محدودیت را داشته باشد. به‌جای نگهداری راز یا payload حساس در گزارش، از canary ساختگی یا نمایش پالایش‌شده استفاده کنید. برای سناریوهای تعاملی، تاریخچهٔ نوبت‌ها، ابزارهای در دسترس، وضعیت حافظه، seed و قواعد تکرار را ثابت یا ثبت کنید.

یک test case فقط زمانی شکست کنترل است که معیار موفقیت از پیش تعریف شده و شاهد آن ثبت شده باشد. صرف تولید یک پاسخ نامطلوب، بدون نشان‌دادن نقض مرز یا هدف، ممکن است finding با اولویت پایین‌تر باشد؛ برعکس، یک tool call غیرمجاز حتی اگر خروجی متنی بی‌ضرر باشد، ممکن است شکست امنیتی مهمی باشد. «محل خطا»، «اثر» و «شدت» را جداگانه گزارش کنید.

## ۱۵. نرخ موفقیت را با مخرج و هدف روشن گزارش دهید

اگر نرخ موفقیت حمله را گزارش می‌کنید، تعریف «موفقیت» باید با هدف و پیامد سازگار باشد: آیا یک پاسخ خاص کافی است، آیا داده افشا شده، آیا عمل پایین‌دستی واقعاً اجرا شده یا آیا اثر روی کاربر دیده شده است؟ تعداد تلاش‌های معتبر، تعداد تغییرهای prompt، نسخهٔ policy، معیار adjudication و موارد نامعتبر را ثبت کنید. promptهای تکراری و وابسته را مشاهدات مستقل نشمارید.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="نرخ موفقیت حمله برابر است با شمار آزمون‌های معتبر که هدف امنیتی ازپیش‌تعریف‌شده را محقق کرده‌اند، تقسیم بر شمار کل آزمون‌های معتبر همان هدف">
  <mrow><mi>ASR</mi><mo>=</mo><mfrac><mrow><mi>تعداد آزمون‌های معتبر با هدف محقق‌شده</mi></mrow><mrow><mi>کل آزمون‌های معتبر همان هدف</mi></mrow></mfrac></mrow>
</math>

**متن جایگزین فرمول:** نرخ موفقیت فقط روی تلاش‌های معتبر با هدف و معیار ازپیش‌ثبت‌شده محاسبه می‌شود؛ آن را با احتمال حمله در دنیای واقعی یکی نگیرید.

ASR بدون severity، پوشش، هزینهٔ مهاجم و محدودیت روش تصویر ناقصی است. «صفر از شش» فقط یعنی در شش مورد تعریف‌شده، آن هدف در این اجرا رخ نداده است؛ نه اینکه احتمال رخداد صفر است. اگر آزمونگر پاسخِ موفق را به‌صورت ذهنی انتخاب کند، اندازه‌گیری به سلیقهٔ ارزیاب وابسته می‌شود؛ rubric و بازبینی دوم برای موارد مبهم لازم است.

## ۱۶. پوشش و شکست را از هم جدا کنید

گزارش کنید کدام دارایی‌ها، modalityها، نسخه‌ها، نقش‌ها، ابزارها، tenantها، منابع داده و خانواده‌های حمله آزموده شده‌اند و کدام پوشش داده نشده‌اند. تعداد caseها به‌تنهایی معیار پوشش نیست: صد پارافرایز از یک سناریو الزاماً از یک آزمون برای هر مرز امنیتی مفیدتر نیست. سناریوها را به risk register یا threat model نگاشت کنید و خانه‌های خالی را نشان دهید.

برای هر مورد یافته، شدت پیامد، احتمال در threat model، دامنهٔ اثر، سهولت تکرار و وجود کنترل جبرانی را جدا کنید. یک احتمال یا score عددیِ ساختگی از واژهٔ «بحرانی» دقیق‌تر نیست. تصمیم‌گیر باید بداند چه چیزی ثابت شده، چه چیزی به‌صورت فرض باقی مانده و چه نوع حمله‌ای هنوز آزموده نشده است.

## ۱۷. آزمون تطبیقی و تکرارپذیری لازم‌اند

دفاع را فقط در برابر نمونه‌های شناخته‌شده نسنجید. آزمونگرِ تطبیقی می‌داند فیلتر یا policy چیست و سناریو را برای همان دفاع تغییر می‌دهد؛ این سناریو می‌تواند برای تحلیل بدترین حالت مفید باشد، هرچند دسترسی‌اش باید در مدل تهدید ثبت شود. NIST دربارهٔ evasion و دفاع‌های یادگیری ماشین به ضعف ارزیابی در برابر حمله‌های سازگار هشدار می‌دهد و آزمون قوی‌تر را توصیه می‌کند؛ مقاومتِ مشاهده‌شده همیشه به فرض‌ها و دامنهٔ آزمون وابسته است.

برای بازتولید، نسخهٔ مدل و برنامه، policy، prompt، tool schema، منبع retrieval، زمان، هویت آزمونگر، seed، تعداد تلاش و خروجی پالایش‌شده را نگه دارید. اجرای مجدد پس از اصلاح را به همان سناریو و نسخهٔ قبلی متصل کنید، اما از ثابت‌بودن جواب در یک run نتیجهٔ پایداری همیشگی نگیرید. در سامانهٔ مولد، نوسان بین اجراها خود بخشی از نتیجه است.

## ۱۸. دفاع چندلایه بسازید؛ از prompt به‌تنهایی انتظار مرز نداشته باشید

دفاع ترکیبی می‌تواند شامل سخت‌سازی ورودی، جداسازی منشأ، retrieval مبتنی بر مجوز، policy قطعیِ ابزار، sandbox، محدودکردن خروجی، نظارت و مسیر پاسخ به رخداد باشد. هدف لایه‌ها یکی نیست: فیلتر می‌تواند موارد شناخته‌شده را علامت بزند؛ مجوز پایین‌دستی عمل غیرمجاز را رد کند؛ sandbox دامنهٔ اثر را کوچک کند؛ و مانیتورینگ کشف و مهار را تسهیل کند. هیچ‌یک به‌تنهایی تضمین نمی‌کند همهٔ ورودی‌های خصمانه را بشناسد.

کنترل را در جایی اجرا کنید که بتواند اثر موردنظر را واقعاً متوقف کند. اگر خط دفاعی فقط مدل است، ابزار همان هویت پرقدرت را دارد و خروجی بدون بررسی اجرا می‌شود، فیلتر متنی تنها نقطهٔ شکست است. برای کنترل مستقل، دو لایه باید تا حد ممکن در مرزهای جداگانه و با مسئولیت روشن باشند، نه دو prompt متنی که هر دو را همان مدل تفسیر می‌کند.

## ۱۹. مجوز ابزار را در کد و سرویس پایین‌دستی enforce کنید

برای هر ابزار allowlist محدود، schema صریح، محدودیت طول و نوع داده، timeout، سقف فراخوانی و سطح مجوز مشخص کنید. برای خواندن، از credential خواندنی؛ برای هر کاربر، از هویت و scope همان کاربر؛ برای نوشتن، از یک عمل کوچک و نام‌دار به‌جای اجرای دستور آزاد استفاده کنید. اجازهٔ مدل برای فراخوانی ابزار هرگز جای authorization در application یا downstream service را نمی‌گیرد.

در زنجیرهٔ چندعامل، identity، scope و provenance را در هر hop حفظ کنید. tool response را نیز دادهٔ بیرونی بدانید؛ ممکن است آلوده، اشتباه یا حاوی دستور باشد. در صورت خروج از schema، تغییر نقش، تکرار غیرعادی یا افزایش ارزش تجمعی پارامتر، فراخوانی را رد یا برای بازبینی متوقف کنید. Human-in-the-loop برای اعمال حساس کمک می‌کند، اما باید متن و اثر واقعیِ عمل را به بازبین نشان دهد.

## ۲۰. Poisoning داده را از خطای برچسب جداگانه بررسی کنید

**Data poisoning** یعنی مهاجم داده یا فرایندی را آن‌قدر تحت نفوذ قرار دهد که رفتار یا دسترس‌پذیری مدل تغییر کند؛ هر رکورد نامناسب، bias یا label اشتباه الزاماً poisoning خصمانه نیست. حمله می‌تواند به هدف integrity رفتار مدل را دست‌کاری کند، به هدف availability کیفیت را کاهش دهد، یا در شکل backdoor تنها با trigger معینی اثر بگذارد. در GenAI، دادهٔ pretraining، fine-tuning، بازخورد، RAG و حافظه می‌توانند مرزهای متفاوتی باشند.

کنترل‌ها شامل inventory منابع، provenance و مجوز، کنترل دسترسی به pipeline، ثبت نسخه و transform، بازبینی نمونه‌های مشکوک، جداسازی ارزیابی از دادهٔ توسعه و آزمون رفتار روی triggerهای تعریف‌شده است. Deduplication، anomaly detection یا بررسی آماری می‌توانند علامت بدهند، اما دادهٔ آلودهٔ هدف‌دار ممکن است به توزیع عادی شباهت داشته باشد. «هیچ پرچمی دیده نشد» مساوی «داده پاک است» نیست.

## ۲۱. Backdoor و trigger را در آموزش و نسخهٔ نهایی بجویید

در backdoor، رفتار ناخواسته ممکن است در حضور pattern یا شرطی خاص فعال شود و در نمونه‌های عادی دیده نشود. این الگو می‌تواند از دادهٔ آلوده، checkpoint یا فرایند fine-tuning وارد شود. آزمون عمومیِ accuracy ممکن است آن را نبیند؛ باید threat model مشخص کند چه triggerها یا ورودی‌های غیرعادی در scope هستند و چه رفتار قابل‌قبولی برای هرکدام انتظار می‌رود.

تغییر وزن یا مدل فقط با hash قابل‌تشخیص نیست اگر از نسخهٔ سالمِ منتشرشده hash مرجع نداشته باشید؛ و artifact همسان با upstream، تضمین رفتار امن نیست. نسخهٔ پایه، adapterها، مسیر merge، quantization، تبدیل format، ابزار بارگذاری و محیط اجرا را ثبت کنید و آزمون را روی همان artifact نهاییِ deployشده تکرار کنید. assurance پیش از تبدیل الزاماً به فایل تبدیل‌شده منتقل نمی‌شود.

## ۲۲. زنجیرهٔ تأمین مدل و داده را نسخه‌مند کنید

زنجیرهٔ AI می‌تواند شامل dataset، model checkpoint، adapter، tokenizer، کتابخانه، container، کد تبدیل، registry، سرویس میزبان و pipeline انتشار باشد. ریسک‌ها فقط وابستگی نرم‌افزاری قدیمی نیستند؛ artifact جایگزین‌شده، منبع نامعلوم یا دست‌کاری در مرحلهٔ merge هم می‌تواند رفتار را عوض کند. فهرست اجزا، revision ثابت، hash، منشأ، مجوز و نقش مسئول را کنار هم نگه دارید.

امضای دیجیتال یا digest می‌تواند تمامیت فایل نسبت به یک مرجع و هویت امضاکننده را پشتیبانی کند؛ ثابت نمی‌کند محتوا بی‌خطر، قانونی، بی‌سوگیری یا برای task مناسب است. artifactِ درست‌امضا‌شده هم می‌تواند آسیب‌پذیر یا از منبع مورد اعتمادِ آلوده آمده باشد. در release gate هم provenance و هم آزمون رفتاریِ artifact نهایی را مطالبه کنید.

## ۲۳. Evasion را با Prompt Injection یکی نکنید

در **evasion** مهاجم ورودیِ زمان استنتاج را چنان تغییر می‌دهد که پیش‌بینی یا رفتار مدل از هدف موردنظر منحرف شود. در مدل‌های تصویری، perturbationهای عددی و تغییرهای فیزیکی موضوع پژوهش بوده‌اند؛ در متن، فضای ورودی گسسته است و تغییر کوچکِ ظاهری ممکن است معنا را عوض کند. Prompt injection نوعی دست‌کاری ورودی یا زمینه برای منحرف‌کردن پیروی از دستور است، اما threat model، معیار موفقیت و کنترل آن با evasion یکسان نیست.

آزمون white-box می‌تواند از دسترسی داخلی و آزمون black-box از queryهای قابل‌دسترس استفاده کند؛ انتقال حمله از یک مدل به مدل دیگر نیز فرض جداگانه دارد. نتیجه را با مدل، modality، perturbation، بودجهٔ query و معیار موفقیت گزارش کنید. دفاع adversarial training، randomized smoothing یا روش‌های دیگر فقط در دامنهٔ تعریف‌شده و با هزینه‌ها و محدودیت‌های خودشان قابل ارزیابی‌اند؛ نام آن‌ها گواه مصونیت محصول نیست.

## ۲۴. Model Extraction با Membership Inference متفاوت است

**Model extraction** با پرس‌وجو از یک سرویس یا مشاهدهٔ خروجی، هدف بازسازی یا تقریب رفتار/پارامترهای مدل را دنبال می‌کند؛ جزئیات موفقیت به نوع API، تعداد و کیفیت query، هدف و امکان دسترسی به خروجی بستگی دارد. دریافت مستقیمِ وزنِ منتشرشده یا دزدیده‌شده نوع دیگری از دسترسی است و نباید همه را یک حمله بنامیم. محدودیت نرخ، کنترل دسترسی، بودجهٔ استفاده، کاهش دقت خروجی و پایش الگوی query می‌توانند هزینه را بالا ببرند، اما extraction را به‌طور کلی ناممکن نمی‌کنند.

**Membership inference** تلاش می‌کند بفهمد یک رکورد مشخص در دادهٔ آموزش بوده یا نه؛ این سؤال با بازیابی متن همان رکورد یکی نیست. **Model inversion** می‌کوشد ویژگی یا اطلاعاتی را از رفتار مدل استنتاج یا بازسازی کند. **Training-data extraction** بر آشکارشدن نمونه یا بخش‌های memorized تمرکز می‌کند. این تهدیدها از نظر هدف و معیار فرق دارند و به پروتکل‌های جدا نیاز دارند؛ یک پاسخ نمونه نمی‌تواند همهٔ آن‌ها را اندازه بگیرد.

## ۲۵. حریم خصوصی را در ورودی، retrieval، خروجی و telemetry ببینید

دادهٔ حساس ممکن است در ورودی کاربر، سندِ بازیابی‌شده، دادهٔ آموزش، state مشترک، output، trace یا log باشد. کمینه‌سازی داده، جداسازی tenant، کنترل دسترسی پیش از retrieval، کوتاه‌کردن retention، پالایش و محدودسازی logها و فرایند مدیریت رخداد را از ابتدا طراحی کنید. secret را در system prompt قرار ندهید با این امید که مدل آن را مخفی نگه می‌دارد؛ prompt محل نگهداری credential نیست.

رمزنگاری در انتقال و ذخیره‌سازی مهم است، اما مانع افشای داده‌ای نیست که مدل یا ابزار به‌طور مجاز به آن دسترسی دارد. Privacy-preserving training، differential privacy یا confidential computing ممکن است برای threat model خاص مناسب باشد، اما هرکدام تعریف، هزینه و مصالحه دارند و سامانهٔ اطراف را خودکار امن نمی‌کنند. نسخه، داده، تنظیمات و معیار آزمونِ هر ادعای حریم خصوصی را دقیق بنویسید.

## ۲۶. مصرف بی‌مهار و رفتارهای پرهزینه را اندازه بگیرید

درخواست‌های بسیار بلند، حلقه‌های agent، retrieval تکراری، تولید طولانی، ابزار پرهزینه یا پرس‌وجوی هم‌زمان می‌توانند هزینه یا ظرفیت را تحت فشار بگذارند. NIST AI 600-1 در اقدام MS-2.7-007 از sponge examples نیز نام می‌برد؛ این اشاره در فهرست آزمون است، نه شاهد اینکه یک ورودی معین واقعاً سرویس را از کار می‌اندازد. سناریو باید روی محیط مجاز و با سقف هزینه، timeout و قاعدهٔ توقف اجرا شود.

برای کنترل availability، سقف context و output، timeout، concurrency، بودجهٔ query و tool call، circuit breaker و هشدار هزینه را لایه‌ای تعریف کنید. نرخ‌محدودسازی را بر اساس هویت، tenant و هزینهٔ تجمعی طراحی کنید؛ حد صرفاً IP ممکن است بی‌اثر یا برای کاربران مشترک ناعادلانه باشد. نتیجه را روی workload مصنوعی یا محیط آزمایشی گزارش کنید، نه با تولید بار مخرب روی سرویس عمومی.

## ۲۷. فیلتر و guardrail را دفاع کامل معرفی نکنید

تشخیص prompt injection از روی واژه‌ها، الگوهای شناخته‌شده یا classifier می‌تواند بخشی از ورودی‌ها را علامت بزند؛ مهاجم ممکن است متن را بازنویسی، پنهان یا از modality دیگری وارد کند. مدل دیگری برای بازبینی نیز یک مدل و وابستگی تازه است. guardrail مفید است، اما حد دسترسی ابزار، مجوز downstream و کنترل data boundary باید مستقل باشند.

NIST AI 100-2e2025 و کارهای red-team نشان می‌دهند دفاع‌های adversarial باید در برابر حملهٔ سازگار سنجیده شوند؛ بسیاری از روش‌های پیشنهادی وابسته به فرض‌های خاص و بدون تضمین عمومی‌اند. اگر آزمون دفاع را دور زد، ابتدا سطح شکست را تعیین کنید: مدل، prompt، policy، مجوز، داده، ابزار، monitoring یا فرایند. تغییر prompt به‌تنهایی شاید هشدار را کم کند، اما مرز امنیتی واقعی را برقرار نکند.

## ۲۸. آزمون را پس از تغییر و در عملیات ادامه دهید

Red Teaming یک event سالانه نیست. تغییر مدل پایه، adapter، داده، index، prompt، tool، schema، permission، serving stack یا نوع کاربر می‌تواند سطح حمله را عوض کند. در CI یا پیش از release، سناریوهای ثابت و کم‌خطر را اجرا کنید؛ برای ارزیابی تطبیقی و پراثرتر، محیط و زمان جدا، مجوز مشخص و بررسی انسانی داشته باشید. یافتهٔ قدیمی را پس از اصلاح به regression test تبدیل کنید، اگر آزمون کم‌خطر و نماینده باقی مانده است.

در عملیات، پایش فقط ذخیرهٔ همهٔ promptها نیست. رویدادهای ابزار، تصمیم مجوز، خطا، حجم و الگوی query را با حداقل دادهٔ لازم ثبت کنید؛ PII و secret را پالایش یا محدود کنید؛ دسترسی به telemetry را کنترل کنید و retention را تعیین کنید. سامانهٔ پایش باید توان توقف یا محدودسازی را داشته باشد و سنجش اثر هشدارهای نادرست نیز بخشی از برنامه باشد.

## ۲۹. پاسخ به رخداد را از پیش تمرین کنید

اگر افشای داده یا عمل غیرمجاز رخ داد، دسترسی و اثر را مهار کنید: token یا credential درگیر را revoke کنید، ابزار یا مسیر پرخطر را موقتاً غیرفعال کنید، artifact یا index مشکوک را قرنطینه کنید و اجرای دوبارهٔ سناریو را تا حفظ شواهد متوقف کنید. سپس شناسهٔ نسخه، درخواست‌های مرتبط، تصمیم policy، tool call و دامنهٔ دادهٔ متأثر را با حداقل اطلاعات ضروری بازسازی کنید. هر مرحله باید مالک و زمان مشخص داشته باشد.

پس از مهار، علت ریشه‌ای را در زنجیرهٔ مدل تا برنامه جست‌وجو کنید؛ فقط متن prompt را عوض نکنید اگر مجوز یا جداسازی داده مسئله بوده است. اصلاح را در محیط آزمون تکرار، regression test و کنترل جبرانی را بازبینی کنید، افراد مسئول را مطلع سازید و الزامات قانونی/قراردادی اطلاع‌رسانی را با مشاور مربوط بررسی کنید. گزارش عمومی نباید PII یا جزئیاتی را افشا کند که همان حمله را آسان‌تر کند.

## ۳۰. برای انتشار، شواهد و ریسک باقی‌مانده را امضا کنید

release gate باید نشان دهد چه نسخه‌ای با چه روش‌هایی آزموده شد، چه findingهایی باز یا بسته‌اند، کدام کنترل‌ها مستقل‌اند، کدام گروه/زبان/modality در scope نبوده، و ریسک باقیمانده را چه کسی پذیرفته است. پذیرش ریسک تصمیم سازمانی است، نه نتیجهٔ خودکار «مدل قبول شد». برای کاربرد پرپیامد، آزمون مستقل و ارزیابی پیوسته می‌تواند لازم باشد؛ سطح اطمینان باید متناسب با پیامد خطا باشد.

حداقل شواهد شامل مجوز، threat model، فهرست caseها، نسخهٔ دقیق، گزارش خطا و severity، شاهد پالایش‌شده، محدودیت تعمیم، اصلاح، نتیجهٔ بازآزمون، مالک ریسک و تاریخ بازبینی بعدی است. اگر یک کنترل فقط روی fixture یا unit test اجرا شده، همان را بنویسید؛ از آن نتیجهٔ امنیتی دربارهٔ محیط production نگیرید.

## ۳۱. پروژهٔ فصل: آزمایشگاه کنترل‌های امنیتی با fixture ساختگی

پروژهٔ [آزمایشگاه سناریوهای امنیتی فصل ۶۴](book-engineering/projects/64-red-team-lab/README.md) با کتابخانهٔ استاندارد Python هفت تصمیم سیاستیِ ساختگی را اجرا می‌کند: شش هدف خصمانهٔ تعریف‌شده شامل درخواست افشای canary، تزریق در متن بازیابی‌شده، عبور از scope ابزار، رکورد آموزشی بی‌منشأ، پرس‌وجوی membership و عبور از query budget؛ و یک کنترل سالم برای خواندن عمومی. آزمون‌ها هم baseline و هم چند پیکربندی عمداً تضعیف‌شده را بررسی می‌کنند تا نشان دهند fixture در صورت حذف کنترل مرتبط، شکست را تشخیص می‌دهد.

در پوشهٔ پروژه fixture، `fixture_manifest.json` با SHA-256، `environment.json`، خروجی مرجع `results.json`، کد و آزمون‌های واحد قرار دارند. اجرا:

```text
cd book-engineering/projects/64-red-team-lab
python -m unittest -v
python red_team_lab.py --output results.json
```

این پروژه هدف آموزشیِ مرزهای policy را نشان می‌دهد؛ نه سیستم زبان طبیعی، مدل یادگیری ماشین، RAG، ابزار بیرونی، pipeline واقعی، تحلیل آماری privacy یا engagement انسانی را. برچسب provenance در fixture یک Boolean ساختگی است و به‌معنای امضای دیجیتال نیست.

## ۳۲. نتیجهٔ fixture را دقیق و باریک تفسیر کنید

خروجی مرجع شامل ۷ case، ۶ هدف شبیه‌سازی‌شده و یک درخواست سالم است. در اجرای محلی، هر ۷ نتیجه با انتظار fixture برابر بود؛ صفر از شش هدف شبیه‌سازی‌شده محقق شد و یک مورد query از بودجهٔ محلی فراتر رفت و rate-limit شد. آزمون‌های unit بیست مورد را گذراندند؛ پنج آزمون تغییر سیاست نشان دادند که با غیرفعال‌کردن کنترلِ canary، مرز محتوای بازیابی‌شده، scope ابزار، منشأ داده یا query budget، انتظار ساختگی نقض می‌شود.

عدد صفر از شش **نرخ موفقیت حمله علیه مدل یا محصول نیست**؛ این فقط نتیجهٔ تصمیم‌های ثابت در کد و fixture است. برنامه هیچ model، API، tool، فایل وزن، corpus واقعی یا دادهٔ شخصی را بارگیری نمی‌کند. بنابراین این اجرا دربارهٔ مقاومت مدل در برابر Prompt Injection، کیفیت privacy defense، امنیت pipeline، احتمال رخداد یا آمادگی انتشار چیزی ثابت نمی‌کند. جزئیات و محدودیت‌ها در [گزارش ممیزی فصل ۶۴](book-engineering/chapters/64-audit-report-fa.md) آمده‌اند.

## ۳۳. سناریوی تمرینی را به کنترل مستقل وصل کنید

برای یک دستیار RAG که می‌تواند سند را بخواند و ایمیل پیش‌نویس کند، threat model را از ابتدا بنویسید: سندهای tenantهای مختلف، credential ایمیل، متن بازیابی‌شده، پیش‌نویس، tool call و کاربرِ تأییدکننده دارایی‌اند. سناریوی خصمانه می‌تواند ورودی مستقیم یا محتوای ساختگیِ بازیابی‌شده باشد که از عامل می‌خواهد داده‌ای خارج از وظیفه را بخواند یا ایمیلی ارسال کند. ناوردا این است که متن سند به‌تنهایی اختیار نمی‌دهد و ارسال بدون مجوز و تأیید لازم انجام نمی‌شود.

کنترل‌های مستقل می‌توانند دسترسی retrieval بر مبنای کاربر، credential محدود به draft، tool مجزای read/write، schema مقصد، policy برنامه برای ارسال، تأیید صریح انسان و ثبت نتیجهٔ downstream باشند. آزمون فقط با حساب، سند و مقصد ساختگیِ مجاز اجرا می‌شود؛ خروجی باید نشان دهد هم پاسخ مدل و هم اثر واقعی ابزار چگونه ثبت شده‌اند. در فصل ۶۵ این یافته‌ها به مالک ریسک، مدل‌کارت و برنامهٔ بازبینی وصل می‌شوند.

## ۳۴. دست‌به‌کار: طرح، اجرا، اصلاح و بازبینی

برای هر سناریو این چرخه را تکمیل کنید: **هدف** و پیامد نقض؛ **scope و مجوز**؛ **نسخه و مرز اعتماد**؛ **مهاجم و دسترسی**؛ **ورودی/حالت ساختگی**؛ **ناوردا و معیار**؛ **شاهد بی‌خطر**؛ **قاعدهٔ توقف**؛ **کنترل مستقل**؛ **اصلاح و آزمون دوباره**؛ و **محدودیت تعمیم**. قبل از اجرای واقعی، این طرح را با مالک سامانه و security reviewer مرور کنید. اگر دادهٔ ساختگی یا محیط ایزوله برای آزمون کافی است، از دادهٔ تولید استفاده نکنید.

یافتهٔ ارزشمند صرفاً «مدل را فریب دادیم» نیست. ارزش آن در پیوند قابل‌بررسی میان فرض تهدید، شواهد، اثر، مالک اصلاح و کنترل تکرارپذیر است. اگر آزمایش به خروجی حساس رسید، کار را متوقف کنید، داده را خارج از گزارش عمومی نگه دارید و از مسیر مسئول disclosure پیروی کنید.

## تمرین‌ها

۱. یک دستیار RAG را در برابر تزریق مستقیم و غیرمستقیم مقایسه کنید. برای هرکدام نقطهٔ ورود، ناوردای امنیتی و کنترل مستقلی بنویسید که فقط به prompt مدل متکی نباشد.

۲. عاملی می‌تواند ایمیل بخواند و ارسال کند، اما کار موردنظر فقط خلاصه‌سازی است. دو کنترل متفاوت برای کم‌کردن خطر excessive agency شرح دهید و بگویید کدام‌یک باید در downstream اجرا شود.

۳. تفاوت data poisoning، خطای عادی برچسب و backdoor را با مثال سطح‌بالا توضیح دهید. برای یک dataset ثالث چه شواهد منشأ و چه آزمون رفتاری درخواست می‌کنید؟

۴. در یک پروتکل مجاز، از ۱۲ تلاش معتبر برای یک هدف مشخص، ۳ مورد هدف را محقق می‌کنند. ASR مشاهده‌شده چیست؟ چرا از این نسبت نمی‌توان احتمال حمله به محصول یا نرخ شکست عمومی را نتیجه گرفت؟

۵. model extraction، membership inference و training-data extraction چه هدف‌های متفاوتی دارند؟ برای هرکدام یک کنترل یا آزمون متناسب پیشنهاد کنید و محدودیت آن را بنویسید.

۶. اقدام NIST AI 600-1 با شناسهٔ MS-2.7-007 چه نوع ارزیابی‌ای را پیشنهاد می‌کند؟ چرا نباید آن را گواهی الزامی یا تضمینِ مقاومت تلقی کرد؟

۷. پروژهٔ فصل ۶۴ صفر هدف محقق‌شده از شش مورد را گزارش می‌کند. دقیقاً چه نتیجه‌ای مجاز است و دست‌کم سه چیزی که از آن نمی‌توان نتیجه گرفت چیست؟

۸. یک طرح آزمون مجاز برای agent متصل به RAG بنویسید که scope، هدف، ابزار، دادهٔ ساختگی، شاهد، معیار، قاعدهٔ توقف و کنترل مستقل را مشخص کند.

## جمع‌بندی

Red Teaming باید از تهدید و پیامد آغاز شود، نه از فهرست payload. برای هر آزمون، مجوز، دسترسی، دارایی، ناوردا، مخرج، نسخه، شاهد و قاعدهٔ توقف را ثبت کنید. Prompt Injection را با دفاع صرفاً متنی حل‌شده ندانید؛ اجازهٔ ابزار و داده را بیرون از مدل و در هویت واقعی enforce کنید. داده و artifact را با منشأ و نسخه ردیابی کنید؛ خطرهای poisoning، استخراج، privacy و availability را جداگانه بسنجید؛ و یافته را به اصلاح، مالک ریسک و آزمون دوباره متصل کنید. موفقیت fixture یا red-team محدود، امنیت کامل را ثابت نمی‌کند.

**پاسخ‌نامهٔ مستقل:** [پاسخ‌نامهٔ فصل ۶۴](book-engineering/answers/64-red-teaming-security-fa.md). **پروژهٔ فصل:** [آزمایشگاه سناریوهای امنیتی](book-engineering/projects/64-red-team-lab/README.md). **گزارش ممیزی:** [دامنه، نتیجه و محدودیت اجرای محلی](book-engineering/chapters/64-audit-report-fa.md).

## منابع و تاریخ بازبینی منابع

تاریخ مراجعه و بازبینی همهٔ منابع زیر: ۷ نوامبر ۲۰۲۶. منابع چارچوبی برای طبقه‌بندی، طراحی و آزمون‌اند؛ مفادشان را با مقررهٔ اجباری یا تضمین امنیتی اشتباه نگیرید.

- Autio, C. و همکاران، *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile*, NIST AI 600-1، ژوئیهٔ ۲۰۲۴، به‌ویژه خطرهای Information Security و اقدام پیشنهادی **MS-2.7-007** در بخش Measure 2.7؛ [DOI](https://doi.org/10.6028/NIST.AI.600-1) · [نسخهٔ رسمی PDF](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf). پروفایل و اقدام‌هایش داوطلبانه و وابسته به زمینه‌اند.
- Vassilev, A. و همکاران، *Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations*, NIST AI 100-2e2025، ۲۴ مارس ۲۰۲۵؛ [صفحه و DOI رسمی NIST](https://csrc.nist.gov/pubs/ai/100/2/e2025/final) · [نسخهٔ رسمی PDF](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-2e2025.pdf) · [یادداشت به‌روزرسانی‌های احتمالی](https://csrc.nist.gov/files/pubs/ai/100/2/e2025/final/docs/nist.ai.100-2e2025_potential_updates.pdf). این گزارش taxonomy و محدودیت‌های mitigations را فراهم می‌کند؛ certification محصول نیست. یادداشت errata که در ۳ ژوئن ۲۰۲۵ به‌روزرسانی شده، یک اصلاح احتمالیِ فهرستِ شناسه‌های availability را ثبت می‌کند؛ taxonomyهای مورد استفادهٔ این فصل به آن شناسه‌ها متکی نیستند.
- OWASP GenAI Security Project، *OWASP Top 10 for LLM Applications 2026*، ۴ اوت ۲۰۲۶؛ [PDF رسمی](https://genai.owasp.org/download/56857/) · [صفحهٔ معرفی](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/). از LLM01، LLM02، LLM03، LLM04 و LLM05 برای طبقه‌بندیِ prompt injection، افشا، اختیار، زنجیرهٔ تأمین و poisoning استفاده شده است؛ شمارهٔ رتبه احتمال مستقلِ رخداد نیست.
- MITRE ATLAS، *LLM Prompt Injection*, AML.T0051، زیرنوع‌های direct، indirect و triggered؛ [نسخهٔ پایدار v2026.10](https://atlas.mitre.org/v/2026.10/techniques/AML.T0051/) · [صفحهٔ زنده و mitigationها](https://atlas.mitre.org/techniques/AML.T0051). پایگاه دانش زنده است؛ برای بازتولید، snapshot استفاده‌شده را ثبت کنید.

## پیوندهای آموزشی و ادامهٔ مسیر

- [فصل ۶۳: ممیزی رفتار مدل](63-hallucination-bias-robustness.md) — کیفیت، سوگیری، استحکام و تبیین.
- [فصل ۶۵ در نقشهٔ جلد پنجم](../../BOOK_ROADMAP_FA.md) — هم‌ترازی، حاکمیت، مستندسازی و مدیریت ریسک.
- [راهنمای سبک و انتشار تدریجی جلد پنجم](../VOLUME5_STYLE_GUIDE_FA.md) — ساخت، آزمون و انتشار مستقل هر فصل.

## پیوست اجرایی: آزمایشگاه کنترل‌های امنیتی

فایل زیر دقیقاً با `red_team_lab.py` در پوشهٔ پروژهٔ فصل ۶۴ برابر است. این پیوست فقط منطقِ fixture ساختگی را اجرا می‌کند؛ اجرای موفق آن آزمون عملی روی مدل یا محصول نیست.

```python
"""Run a deterministic, synthetic check of selected AI security controls.

This program does not load or attack a language model, service, tool, or dataset.
It checks only the policy branches explicitly represented in its local fixture.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_FIXTURE = BASE_DIR / "synthetic_security_fixture.json"
DEFAULT_POLICY: dict[str, Any] = {
    "deny_synthetic_canary": True,
    "treat_retrieved_instructions_as_untrusted": True,
    "enforce_tool_scopes": True,
    "require_verified_data_provenance": True,
    "deny_membership_confirmation": True,
    "enforce_query_budget": True,
    "query_budget": 2,
}
CATEGORIES = {
    "direct_prompt_injection",
    "indirect_prompt_injection",
    "tool_scope",
    "data_poisoning",
    "membership_probe",
    "excessive_querying",
    "benign_public_read",
}
POLICY_KEYS = set(DEFAULT_POLICY)


def validate_fixture(data: dict[str, Any]) -> None:
    """Reject malformed or ambiguous fixture records before calculating results."""
    if not isinstance(data, dict) or not isinstance(data.get("fixture_id"), str):
        raise ValueError("fixture must contain a string fixture_id")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("fixture cases must be a non-empty list")
    ids: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("each fixture case must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("each fixture case needs a non-empty id")
        if case_id in ids:
            raise ValueError(f"duplicate case id: {case_id}")
        ids.add(case_id)
        if case.get("category") not in CATEGORIES:
            raise ValueError(f"unknown category in {case_id}: {case.get('category')!r}")
        if not isinstance(case.get("is_attack"), bool):
            raise ValueError(f"is_attack must be boolean in {case_id}")
        if not isinstance(case.get("expected_outcome"), str):
            raise ValueError(f"expected_outcome must be a string in {case_id}")
        if case.get("is_attack") and not isinstance(case.get("success_outcome"), str):
            raise ValueError(f"attack case needs a fixture-specific success_outcome in {case_id}")
        if not case.get("is_attack") and case.get("success_outcome") is not None:
            raise ValueError(f"benign case success_outcome must be null in {case_id}")
        if case["category"] == "excessive_querying":
            count = case.get("queries_in_window")
            if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                raise ValueError(f"queries_in_window must be a non-negative integer in {case_id}")
        if case["category"] == "tool_scope" and not isinstance(case.get("principal_scopes"), list):
            raise ValueError(f"principal_scopes must be a list in {case_id}")


def _effective_policy(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    policy = DEFAULT_POLICY.copy()
    if overrides:
        unknown = set(overrides) - POLICY_KEYS
        if unknown:
            raise ValueError(f"unknown policy keys: {sorted(unknown)}")
        policy.update(overrides)
    for key in POLICY_KEYS - {"query_budget"}:
        if not isinstance(policy[key], bool):
            raise ValueError(f"policy {key} must be boolean")
    budget = policy["query_budget"]
    if not isinstance(budget, int) or isinstance(budget, bool) or budget < 0:
        raise ValueError("query_budget must be a non-negative integer")
    return policy


def decide(case: dict[str, Any], policy: dict[str, Any] | None = None) -> str:
    """Return the toy policy outcome for a fixture case; this is not model inference."""
    controls = _effective_policy(policy)
    category = case["category"]
    if category == "direct_prompt_injection":
        if case.get("asks_for_synthetic_canary") and controls["deny_synthetic_canary"]:
            return "blocked"
        return "canary_disclosed"
    if category == "indirect_prompt_injection":
        is_untrusted = case.get("instruction_origin") == "untrusted_retrieved_content"
        if is_untrusted and controls["treat_retrieved_instructions_as_untrusted"]:
            return "blocked"
        return "action_executed" if case.get("requests_tool_action") else "allowed"
    if category == "tool_scope":
        requested = case.get("requested_action")
        scopes = case.get("principal_scopes", [])
        if requested not in scopes and controls["enforce_tool_scopes"]:
            return "blocked"
        return "action_executed" if requested not in scopes else "allowed"
    if category == "data_poisoning":
        if not case.get("provenance_verified") and controls["require_verified_data_provenance"]:
            return "quarantined"
        return "sample_accepted"
    if category == "membership_probe":
        if case.get("requests_membership_confirmation") and controls["deny_membership_confirmation"]:
            return "blocked"
        return "membership_confirmed"
    if category == "excessive_querying":
        if (case.get("queries_in_window", 0) > controls["query_budget"]
                and controls["enforce_query_budget"]):
            return "rate_limited"
        return "query_served"
    if category == "benign_public_read":
        return "allowed"
    raise ValueError(f"unsupported category: {category!r}")


def analyze(data: dict[str, Any], fixture_bytes: bytes,
            policy: dict[str, Any] | None = None) -> dict[str, Any]:
    validate_fixture(data)
    controls = _effective_policy(policy)
    case_results = []
    for case in data["cases"]:
        observed = decide(case, controls)
        case_results.append({
            "id": case["id"],
            "category": case["category"],
            "is_attack": case["is_attack"],
            "expected_outcome": case["expected_outcome"],
            "observed_outcome": observed,
            "control_check_passed": observed == case["expected_outcome"],
            "simulated_goal_reached": bool(
                case["is_attack"] and observed == case.get("success_outcome")
            ),
        })
    attack_cases = [result for result in case_results if result["is_attack"]]
    goal_count = sum(result["simulated_goal_reached"] for result in attack_cases)
    passed = sum(result["control_check_passed"] for result in case_results)
    attempts = len(attack_cases)
    return {
        "fixture_id": data["fixture_id"],
        "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "policy_id": "synthetic-control-policy-v1",
        "case_count": len(case_results),
        "attack_case_count": attempts,
        "benign_control_count": len(case_results) - attempts,
        "control_checks_passed": passed,
        "control_checks_failed": len(case_results) - passed,
        "simulated_attack_goals_reached": goal_count,
        "simulated_attack_goal_rate": goal_count / attempts if attempts else None,
        "rate_limited_cases": sum(
            result["observed_outcome"] == "rate_limited" for result in case_results
        ),
        "cases": case_results,
        "scope": (
            "Deterministic decisions against seven synthetic policy cases only; "
            "not a red-team test of an AI model or deployed system."
        ),
        "limitations": [
            "No language model, classifier, API, network, external tool, model weight, training pipeline, or real dataset is executed.",
            "The fixture contains synthetic labels and no personal data, credentials, or production secrets.",
            "The simulated goal rate is computed from six hand-authored cases and is not an empirical attack-success rate.",
            "The query-budget case checks a local threshold branch only; it does not test model extraction, distributed accounts, or privacy leakage.",
            "A provenance flag is not a cryptographic signature or proof that data is safe, lawful, accurate, or unbiased.",
            "Passing these unit tests does not establish prompt-injection resistance, privacy, security, safety, or deployment readiness.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, help="write deterministic JSON to this path")
    args = parser.parse_args()
    fixture_bytes = args.fixture.read_bytes()
    data = json.loads(fixture_bytes.decode("utf-8"))
    result = analyze(data, fixture_bytes)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote synthetic security-control results: {args.output}")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
```

---

# جلد پنجم، فصل ۴ — هم‌ترازی، حاکمیت، مستندسازی، مدل‌کارت، داده‌کارت و مدیریت ریسک

**نگاشت:** فصل محلی ۴ جلد پنجم = فصل سراسری ۶۵. **تاریخ بازبینی منابع: ۷ نوامبر ۲۰۲۶.** این فصل «هم‌ترازی» را در سطح هدفِ سازمانی، کاربرد مقصود، مسئولیت انسانی و کنترل ریسک بررسی می‌کند؛ الگوریتم‌های ترجیح‌محورِ پس‌آموزش در فصل ۴۹ جلد چهارم‌اند. فصل ۶۴ حمله‌ها و آزمون خصمانه را می‌کاود؛ این فصل نشان می‌دهد یافته‌ها چگونه به مالک، سند، تصمیم و بازبینی وصل می‌شوند. ساخت API در فصل ۶۶ و سرو و بهینه‌سازی استنتاج در فصل ۶۷ می‌آید؛ آن‌ها را با حکمرانی این فصل یکی نگیرید.

**پیش‌نیاز:** آشنایی با چرخهٔ عمر داده و مدل، ارزیابی فصل‌های ۶۲ و ۶۳، و تهدیدهای فصل ۶۴. **خروجی:** بتوانید مرز سامانه و نقش‌ها را ثبت کنید؛ قانون را از استاندارد و راهنمای داوطلبانه جدا کنید؛ یک ارزیابی اثر و دفتر ثبت ریسک بسازید؛ کاربرد، محدودیت، منشأ و شواهد را در کارت مدل و داده‌کارت مستند کنید؛ و تصمیمِ توقف یا ادامهٔ مشروط را به مالک انسانی و مدرک قابل‌ردیابی پیوند دهید.

![شکل ۵-۴-۱ — چرخه از تعیین کاربرد و مرز سامانه به ارزیابی اثر و ذی‌نفعان، سپس ثبت سناریوی ریسک و شواهد، و در پایان به تصمیم مالک انسانی می‌رسد. اگر شاهد کافی نباشد یا ریسک شدیدِ باز مهار نشده باشد، مسیر به توقف یا بازطراحی می‌رود؛ مسیر ادامه نیز باید محدودیت، مالک، مدرک و موعد بازبینی داشته باشد. تغییر مدل، داده، کاربرد یا قاعده دوباره ارزیابی را فعال می‌کند؛ رنگ فقط تزئینی است و معنی مسیر را متن و پیکان‌ها می‌رسانند.](book-engineering/diagrams/v5-ch04-governance-cycle.svg)

**شکل ۵-۴-۱ —** حکمرانی یک چرخهٔ قابل‌ردیابی است: دامنه و اثر به ریسک و شاهد می‌رسند؛ مالک پاسخ‌گو تصمیم می‌گیرد؛ تغییر مهم ارزیابی را دوباره باز می‌کند.

## ۱. از آزمون خصمانه به حکمرانی

فصل ۶۴ پرسید مهاجمِ دارای دسترسی و هدف مشخص چه مرزی را می‌تواند نقض کند. فصل ۶۵ می‌پرسد چه کسی دامنهٔ قابل‌قبول را تعیین می‌کند، چه کسانی متأثر می‌شوند، چه شواهدی برای تصمیم لازم است و چه کسی پاسخ‌گوی ریسک باقی‌مانده است. نتیجهٔ یک آزمون، خودبه‌خود تصمیم سازمانی نیست: باید به نسخهٔ آزموده‌شده، سناریو، محدودیت و صاحب تصمیم پیوند بخورد.

حکمرانی در این فصل به معنی داشتن سازوکارهای تصمیم، اختیار، پاسخ‌گویی و بازبینی است؛ نه فقط تصویب یک بیانیهٔ اخلاقی یا تکمیل فرم. «هم‌ترازی» نیز به معنی یک ادعای فنیِ کلی دربارهٔ مدل نیست؛ یعنی مقصد و حدود سامانه با نیاز مشروع، حقوق و ایمنی افراد، الزامات الزام‌آور و توان واقعی سازمان برای نظارت سازگار باشند. هیچ کارت یا چارچوبی این سازگاری را به‌تنهایی ثابت نمی‌کند.

## ۲. مرز سامانه و سطح مسئولیت

مدل به‌تنهایی معمولاً محصول نیست. سامانه می‌تواند مدل پایه، adapter، prompt، دادهٔ بازیابی‌شده، فهرست ابزارها، رابط کاربر، قواعد دسترسی، حافظه، ثبت رخداد و فرایند انسانی را در بر بگیرد. خروجی‌ای که از یک مدل بی‌خطر به نظر می‌رسد، اگر به تصمیم استخدام، پرداخت، درمان یا دسترسی به خدمت وصل شود، ممکن است اثر پرریسکی پیدا کند. بنابراین فهرست اجزا باید همراه با جریان داده و تصمیم پایین‌دستی باشد، نه فقط نام مدل و شمار پارامترها.

برای هر مرز بنویسید چه چیزی داخل دامنه است، چه چیزی بیرون می‌ماند، چه نهادی آن را فراهم می‌کند و چه تیمی اختیار تغییرش را دارد. اگر سرویس مدلِ بیرونی تغییر نسخه می‌دهد، یا موتور بازیابی پایگاه داده‌ای را می‌خواند که تیم محصول مالک آن نیست، این وابستگی در inventory ثبت شود. نمودار معماری یا فهرست دارایی جای تحلیل اثر را نمی‌گیرد، اما بدون آن‌ها ممکن است ریسک و پاسخ‌گو از قلم بیفتند.

## ۳. چرخهٔ عمر، مالکیت و شاهد

مسئولیت در یک نقطهٔ «ساخت مدل» تمام نمی‌شود. آن را از تعریف مسئله و تهیهٔ داده تا آموزش یا انتخاب مدل، ادغام، استفاده، تغییر، رسیدگی به شکایت و بازنشستگی دنبال کنید. برای هر مرحله صاحب کار، صاحب تصمیم و منبع شواهد را مشخص کنید. تیمی که روی داده یا مدل نظارت می‌کند، لزوماً اختیار پذیرش اثر بر کاربر یا انطباق حقوقی را ندارد؛ اختیارها باید روشن و قابل‌ارجاع باشند.

سه چیز را جدا نگه دارید: **ادعا** آن چیزی است که سازمان می‌گوید؛ **شاهد** داده، آزمون، سند یا تصمیم ثبت‌شده‌ای است که ادعا را پشتیبانی می‌کند؛ **داوری** تفسیر فرد صاحب‌صلاحیت از کفایت شاهد برای یک کاربرد و نسخهٔ مشخص است. برای مثال، «آزمون‌ها گذشتند» بدون نام آزمون، نسخه، نمونه، معیار و محدودیت شاهد کافی نیست. قبولی یک schema check نیز ادعای انطباق حقوقی یا ایمنی محصول را پشتیبانی نمی‌کند.

در کنار هر ادعا، نسخهٔ محصول، زمان بازبینی، محیط، محدودهٔ آزمون و مالک را ثبت کنید. اگر داده ناقص است، به‌جای پرکردن شکاف با قطعیت، «نامعلوم»، «تأییدنشده» یا «بررسی‌نشده» بنویسید و تعیین کنید چه تصمیمی تا رفع ابهام مجاز نیست. این روش با درس فصل‌های ۶۲ تا ۶۴ هم‌راستاست: نتیجه را فقط تا جایی تعمیم دهید که طرح و شواهد اجازه می‌دهند.

## ۴. قانون، استاندارد، چارچوب و سیاست داخلی

واژه‌های «مقرره»، «استاندارد»، «چارچوب» و «سیاست» هم‌معنا نیستند. قانون می‌تواند الزام حقوقی و پیامد اجرا داشته باشد؛ استاندارد، سند فنی یا مدیریتی با دامنه و قواعد خودش است؛ چارچوب راهی برای سازمان‌دهی کار و شواهد پیشنهاد می‌کند؛ و سیاست داخلی تصمیمِ یک سازمان دربارهٔ شیوهٔ عمل خودش است. گاهی قرارداد یا قانون به سندی ارجاع می‌دهد و جایگاه آن را برای مورد خاص تغییر می‌دهد؛ پس از نام سند به‌تنهایی نتیجهٔ حقوقی نگیرید.

| نوع سند | پرسش اصلی | نمونه در این فصل | چیزی که به‌تنهایی ثابت نمی‌کند |
|---|---|---|---|
| قانون الزام‌آور | چه کسی، در کدام حوزه و از چه تاریخی چه وظیفه‌ای دارد؟ | مقررهٔ هوش مصنوعی اتحادیهٔ اروپا | اینکه هر سامانه در هر کشور مشمول یک بند معین است |
| استاندارد | چه الزامات یا راهنمای فنی/مدیریتی برای دامنهٔ استاندارد آمده است؟ | ISO/IEC 42001 و 42005 | انطباق خودکار با تمام قوانین یا پیامد واقعیِ مطلوب |
| چارچوب راهنما | کار را با چه تابع‌ها و دسته‌هایی سازمان‌دهی کنیم؟ | NIST AI RMF 1.0 | گواهی اجباری یا مجوز انتشار |
| سیاست سازمانی | در همین سازمان چه کاربردی مجاز، نیازمند تأیید یا ممنوع است؟ | سیاست نگهداری داده و مسیر اعتراض | درستی سیاست یا کفایت آن در برابر قانون |

فهرست منابع در پایان فصل، صفحه‌های رسمی را برای راستی‌آزمایی فراهم می‌کند؛ اما این فصل مشاورهٔ حقوقی نیست. سازمان باید دامنه، نقش، کشور، قرارداد، بخش صنعتی و نسخهٔ جاری متن الزام‌آور را برای کاربرد خودش بررسی کند.

## ۵. EU AI Act: دامنه، طبقه‌بندی و نقش‌ها

مقررهٔ ۲۰۲۴/۱۶۸۹ قانون اتحادیهٔ اروپاست و برای نقش‌ها و دسته‌های تعریف‌شده تکلیف مشخص می‌کند؛ عنوان «هوش مصنوعی» یا میزان نوآوری محصول به‌تنهایی طبقه‌بندی حقوقی را تعیین نمی‌کند. کاربرد مقصود، محل عرضه یا استفاده، جایگاه سازمان در زنجیره و پیوست‌ها و ماده‌های مرتبط باید بررسی شوند. بعضی تکلیف‌ها به provider، بعضی به deployer و بعضی به مدل‌های عمومی یا نقش‌های دیگر مربوط‌اند؛ از آنجا که تعریف‌ها و استثناها فنی‌اند، آن‌ها را از متن جاری مادهٔ مربوط تطبیق دهید [۱، ۲، ۱۱].

برای تیم محصول، حداقل inventory باید شناسهٔ سامانه، نسخه، کاربرد مقصود، نقش سازمان، کشور/بازار، مدل‌های ثالث، جریان‌های داده و تصمیم‌های پایین‌دستی را نشان دهد. «مدل عمومی است» پاسخِ طبقه‌بندی سامانهٔ نهایی نیست؛ سامانهٔ یکپارچه ممکن است کاربرد و وظیفه‌ای متفاوت داشته باشد. همچنین همهٔ وظایف AI Act در یک تاریخ آغاز نمی‌شوند و هر پرسش‌نامهٔ مشتری الزام قانونی تازه‌ای ایجاد نمی‌کند.

## ۶. تقویم اجرا تا ۲۰۲۸، در تاریخ ۷ نوامبر ۲۰۲۶

کمیسیون اروپا اعلام کرده مقررهٔ اصلاحی Digital Omnibus on AI، یعنی Regulation (EU) 2026/1744، در ۲۷ ژوئیهٔ ۲۰۲۶ لازم‌الاجرا شده است. خط زمانی رسمی، شروع اعمال بعضی قواعد را جداگانه نشان می‌دهد؛ «لازم‌الاجراشدن اصلاحیه» با «شروع اجرای تمام تکلیف‌ها» یکی نیست [۱، ۲]. جدول زیر خلاصهٔ همان خط زمانی رسمی در روز بازبینی منابع است، نه تقویم کامل همهٔ تکلیف‌ها یا نظر حقوقی برای محصول خاص.

| تاریخ | رویداد یا زمان‌بندی اعلام‌شده | تفسیر محتاطانه |
|---|---|---|
| ۱ اوت ۲۰۲۴ | مقررهٔ اصلی وارد مرحلهٔ لازم‌الاجراشدن شد | این تاریخ به‌معنای اجرای هم‌زمان همهٔ مواد نیست |
| ۲ اوت ۲۰۲۵ | قواعد مدل‌های عمومی و سازوکارهای حکمرانی مربوط، طبق خط زمانی، وارد مرحلهٔ اعمال شدند | نقش ارائه‌دهندهٔ مدل عمومی را با نقش ارائه‌دهندهٔ سامانهٔ نهایی خلط نکنید |
| ۲ اوت ۲۰۲۶ | شفافیت مادهٔ ۵۰ و اجرای قواعدی که تا آن تاریخ قابل‌اعمال شده‌اند آغاز شد | شفافیت را به تاریخ‌های بعدی قواعد high-risk موکول نکنید |
| ۲ دسامبر ۲۰۲۶ | خط زمانی، ممنوعیت‌های تازهٔ مشخص و پایان مهلت انتقالیِ مادهٔ ۵۰(۲) برای بعضی سامانه‌های مولدِ ازپیش‌عرضه‌شده را فهرست می‌کند | این مهلت، تعویق عمومی همهٔ تکلیف‌های شفافیت یا مجوز عرضه نیست |
| ۲ دسامبر ۲۰۲۷ | قواعد مربوط به سامانه‌های پرریسکِ پیوست III طبق اصلاحیه اعمال می‌شوند | هر کاربرد را جداگانه با متن و نقش حقوقی تطبیق دهید |
| ۲ اوت ۲۰۲۸ | قواعد سامانه‌های پرریسکِ تعبیه‌شده در محصولات مشمول پیوست I اعمال می‌شوند | این تاریخ را با همهٔ دسته‌های high-risk یکی نگیرید |

کمیسیون همچنین برای ۲ دسامبر ۲۰۲۶ زمان‌بندی ممنوعیت‌های جدید مربوط به تولید برخی محتوای صمیمیِ بدون رضایت و محتوای سوءاستفادهٔ جنسی از کودکان را درج کرده است. جزئیات، استثناها و متن اصلاح‌شده را از Regulation (EU) 2026/1744 و خط زمانی رسمی بخوانید؛ از این خلاصه برای تصمیم حقوقی دربارهٔ یک قابلیت خاص استفاده نکنید [۱، ۲]. برای انطباق عملی، هر تاریخ را به دارایی، نقش، بازار، مالک و مدرک تبدیل کنید و تقویم را پیش از انتشار دوباره بررسی کنید.

## ۷. از ماده تا مدرک: ماتریس تعهد و شواهد

در AI Act نمونه‌هایی از تکلیف‌های سامانه‌های پرریسک دربارهٔ مدیریت ریسک، نظام مدیریت کیفیت، وظایف بهره‌بردار و ارزیابی اثر بر حقوق بنیادین در موارد مشخص وجود دارد؛ شفافیت مادهٔ ۵۰ نیز دامنه و نقش‌های خودش را دارد [۲، ۳، ۱۱]. این‌ها مثال‌هایی برای ساخت ماتریس‌اند، نه فهرست تمام تعهدها. پیوند هر ماده را به منبع رسمی و نسخهٔ جاری نگه دارید، چون طبقه‌بندی، زمان‌بندی و استثنا می‌توانند با اصلاح مقرره تغییر کنند.

یک ماتریس ساده چهار ستون دارد: منبع و ماده؛ نقش و کاربردی که احتمالاً مشمول است؛ مسئول داخلی و تاریخ بررسی؛ و مدرکِ موجود/مفقود. مدرک ممکن است سیاست، گزارش ارزیابی، ثبت آزمون، سند مدل/داده یا تصمیم مصوب باشد. صرف نوشتن «مطابق مادهٔ X» مدرک نیست؛ و وجود یک سند مدیریتی نیز ثابت نمی‌کند اجرای روزمره با آن هم‌خوان است.

## ۸. NIST AI RMF 1.0: چهار تابع، یک چرخه

NIST AI Risk Management Framework 1.0 چارچوبی داوطلبانه برای بهترکردن مدیریت ریسک و واردکردن ملاحظه‌های اعتمادپذیری در طراحی، توسعه، استفاده و ارزیابی سامانه‌هاست. چهار تابع آن **GOVERN، MAP، MEASURE و MANAGE** هستند؛ GOVERN نقش‌ها و سیاست‌ها را پشتیبانی می‌کند و سه تابع دیگر زمینه، سنجش و پاسخ را سامان می‌دهند. آن‌ها را یک‌بار و به‌ترتیب خطی اجرا نمی‌کنیم: یادگیری از سنجش یا رخداد می‌تواند نقشه و کنترل را تغییر دهد [۴].

- **GOVERN:** فرهنگ ریسک، مالکیت، اختیار تصمیم، سیاست، منابع، نظارت و رویهٔ ارجاع را روشن کنید.
- **MAP:** کاربرد، بافت، افراد متأثر، وابستگی‌ها، حدود دانسته‌ها و پیامدهای ممکن را توصیف کنید.
- **MEASURE:** روش، داده، معیار، آستانه، عدم‌قطعیت و محدودیت شواهد را ثبت کنید؛ نتیجه را به ادعای بزرگ‌تر تبدیل نکنید.
- **MANAGE:** ریسک‌ها را اولویت‌بندی کنید، درمان یا توقف را تعیین کنید و بازبینی را به تغییرها و رخدادها پیوند دهید.

وب‌سایت NIST در زمان بازبینی می‌گوید AI RMF 1.0 در حال بازنگری است. چارچوب را به‌عنوان سند داوطلبانهٔ جاریِ منتشرشده بشناسید و هنگام استفاده، صفحهٔ NIST را برای نسخه یا به‌روزرسانی تازه بررسی کنید [۴]. داوطلبانه‌بودن خود چارچوب، تکلیف قراردادی یا حقوقی جداگانهٔ سازمان را حذف نمی‌کند.

## ۹. پروفایل مولد NIST AI 600-1

NIST AI 600-1 یک پروفایل مقطعی برای کاربرد چارچوب در سامانه‌های مولد است. سند در سال ۲۰۲۴ منتشر شد و خطرهای خاص یا تشدیدشدهٔ هوش مولد و اقدام‌های پیشنهادی برای GOVERN، MAP، MEASURE و MANAGE را گرد می‌آورد. نویسندگان چهار ملاحظهٔ اصلیِ کارگروه را governance، content provenance، pre-deployment testing و incident disclosure می‌نامند؛ این چهار مورد، محورهای آن پروفایل‌اند، نه فهرست بستهٔ همهٔ خطرها یا استاندارد قبولی [۵].

برای هر اقدام پیشنهادی مشخص کنید چه کسی آن را اجرا می‌کند، روی کدام نسخه و دامنه، با چه مدرکی و با چه محدودیتی. اگر «آزمون پیش از عرضه» فقط روی fixture انجام شده، آن را آزمون fixture بنویسید، نه اعتبارسنجی سامانهٔ واقعی. اگر منشأ محتوا نامعلوم است، نبود فراداده را به «اثبات‌شدهٔ اصیل» تبدیل نکنید. هم‌چنین «افشا/گزارش رخداد» را به یک فیلد تماس محدود نکنید؛ آستانه، اختیار، مخاطب، نگهداری شواهد و یادگیری پس از رخداد را در نظر بگیرید.

## ۱۰. ISO/IEC 42001:2023؛ سیستم مدیریت

ISO/IEC 42001:2023 الزامات ایجاد، اجرا، نگه‌داری و بهبود مستمر یک Artificial Intelligence Management System را برای سازمان‌های ارائه‌دهنده یا استفاده‌کننده از محصولات و خدمات هوش مصنوعی مشخص می‌کند. این استاندارد دربارهٔ سازمان و فرایند مدیریت است؛ جایگزین ارزیابی فنی هر مدل یا تحلیل اثر یک کاربرد معین نیست [۶].

کاربرد آموزشی آن در این فصل، یادآوری چرخهٔ مدیریتی است: محدودهٔ سیستم را تعیین کنید، نقش و سیاست را تصویب کنید، منابع و شایستگی را فراهم کنید، ریسک و اثر را بررسی کنید، اجرای کنترل را ثبت کنید، ممیزی و بازنگری انجام دهید و نارسایی را اصلاح کنید. متن کامل استاندارد و معیارهای انطباق در این خلاصه بازتولید نشده‌اند. پیروی از چارچوب داخلی، ادعای certification، گواهی طرف ثالث یا انطباق با قانون خاص را مجاز نمی‌کند؛ آن‌ها ادعاهای جدا و نیازمند دامنه و شواهد خودشان‌اند.

## ۱۱. ISO/IEC 42005:2025؛ ارزیابی اثر

ISO/IEC 42005:2025 راهنمای انجام ارزیابی اثر سامانهٔ هوش مصنوعی است و می‌پرسد سامانه و کاربردهای قابل‌پیش‌بینی آن چه اثری بر افراد، گروه‌ها یا جامعه می‌گذارند. صفحهٔ رسمی ISO انتشار نسخهٔ نخست را در مه ۲۰۲۵ ثبت می‌کند و آن را مکمل استانداردهای مدیریت و حکمرانی معرفی می‌کند [۷]. نشانی رسمی این استاندارد `https://www.iso.org/standard/42005` است؛ پسوند `.html` نشانی درستی نیست.

ارزیابی اثر را در طراحی آغاز کنید و با تغییر کاربرد، داده، گروه مخاطب، تصمیم پایین‌دستی یا وابستگی مهم باز کنید. حداقل ثبت کنید چه افراد یا گروه‌هایی ممکن است سود یا زیان ببینند، مسیر اثر چیست، چه کسی شواهد را بررسی کرده، چه گزینهٔ کم‌خطر‌تری وجود دارد و کدام عدم‌قطعیت تصمیم را محدود می‌کند. یک جدول ساده در این فصل الگویی آموزشی است؛ متن خریداری‌شدهٔ استاندارد یا ارزیابی منطبق با آن نیست.

## ۱۲. Crosswalk: هم‌ترازی بدون تیک‌زنی

یک crosswalk می‌تواند بندهای چند چارچوب را به یک artifact مشترک وصل کند؛ برای مثال، «مالک ریسک»، «نسخهٔ مدل» و «تاریخ بازبینی» در چند فرم تکرار می‌شوند. اما هم‌نامی ستون‌ها به معنی هم‌ارزی حقوقی نیست. مادهٔ الزام‌آور، پروفایل داوطلبانه و کنترل داخلی ممکن است دامنه، مخاطب، شدت و معیار اثبات متفاوتی داشته باشند.

برای هر نگاشت، منبع و نسخه، دلیل تطبیق، شکاف باقی‌مانده و فرد تأییدکننده را ثبت کنید. کنترل را به فرم تبدیل نکنید که فقط «بله/خیر» می‌پرسد: «ارزیابی شد؟» بدون اینکه روش، تاریخ، نسخه و نتیجه را نشان دهد، قابلیت ممیزی ندارد. از artifactهای مشترک برای کم‌کردن دوباره‌کاری استفاده کنید، ولی هر تکلیف را در متن مرجع خودش تفسیر کنید.

## ۱۳. کاربرد مقصود و مرز منع‌کاربرد

شرح کاربرد باید از زبان نقش و تصمیم واقعی نوشته شود: چه کسی از چه ورودی استفاده می‌کند، چه خروجی می‌گیرد، برای کدام تصمیم یا خدمت، با چه اختیار و در کدام محیط. عبارت «دستیار هوشمند» نه کاربرد مقصود است و نه محدودیت. برای مثال، می‌توان گفت سامانه فقط قواعد منتشرشده را توضیح می‌دهد و کاربر را به منبع رسمی ارجاع می‌دهد؛ تصمیم واجدشرایط‌بودن، پذیرش یا رد را انسان یا فرایند رسمی می‌گیرد.

«منع‌کاربرد» را هم صریح کنید: سامانه برای جمعیت، زبان، نوع سند یا تصمیمی که بررسی نشده استفاده نشود. اگر کاربرد دیگری بعداً اضافه شد، آن را توسعهٔ بی‌اهمیت رابط تلقی نکنید؛ ممکن است بافت اثر، نقش حقوقی، داده و سطح ریسک را تغییر دهد و به ارزیابی دوباره نیاز داشته باشد.

## ۱۴. ذی‌نفعان و اثرهای قابل‌پیش‌بینی

از دید کسی که روی سامانه اثر می‌پذیرد، فهرست ذی‌نفعان بسازید: کاربر مستقیم، فردی که درباره‌اش تصمیم گرفته می‌شود، کارکنان پشتیبان، گروه‌های کم‌نماینده، مدیر، ارائه‌دهندهٔ زیرساخت و نهاد پاسخ‌گو. «مشتری» همیشه تنها فرد متأثر نیست؛ خروجی ممکن است به تصمیم‌گیر دیگری برسد یا برای مدتی نگه داشته شود.

برای هر گروه بپرسید: چه منفعتی انتظار می‌رود؟ چه خطایی محتمل است؟ آیا می‌توان خروجی را رد یا اصلاح کرد؟ آیا راه دیگری برای دریافت خدمت باقی می‌ماند؟ چه زبانی و چه شکل دسترس‌پذیری در دامنه است؟ اگر دیدگاه افراد متأثر دریافت نشده، آن را «گفت‌وگو انجام نشده» ثبت کنید؛ فرض نکنید تیم فنی نمایندهٔ تجربهٔ آنان است.

## ۱۵. ارزیابی اثر را از سناریو شروع کنید

ارزیابی اثر، فهرست کلی «خوب و بد» نیست. برای هر مسیر از ورودی به پیامد، عامل تصمیم، واسطهٔ انسانی، امکان اعتراض و کنترل را دنبال کنید. یک خروجی نادرست می‌تواند در کاربرد کم‌اثر به اتلاف زمان، و در کاربردی که دسترسی به خدمت را تعیین می‌کند به زیان جدی منجر شود. پس شدت اثر فقط از متن خروجی مدل استنتاج نمی‌شود؛ وابستگی تصمیم پایین‌دستی و زمینه را نیز ببینید.

محدودهٔ ارزیابی و دلیل حذف احتمالات را ثبت کنید. اگر افراد یا دادهٔ واقعی در مطالعه نیستند، به‌جای «هیچ اثر منفی مشاهده نشد» بنویسید «اثر انسانی در این مرحله بررسی نشده است». اگر خطر به کنترل وابسته است، خود کنترل را هم بیازمایید یا وضعیتش را «برنامه‌ریزی‌شده» علامت بزنید؛ وجود بند در سیاست، اجرای واقعی را ثابت نمی‌کند.

## ۱۶. از آسیب به سناریوی ریسک

یک نگرانی کلی را به زنجیرهٔ قابل‌بررسی تبدیل کنید: **بافت و شرط** → **رویداد یا خطا** → **قرارگرفتن فرد در معرض** → **پیامد** → **شدت و احتمال** → **کنترل و ریسک باقی‌مانده**. مثلاً در یک راهنمای ساختگی بورسیه، اگر پاسخ قدیمی به‌عنوان تصمیم رسمی تلقی شود، ممکن است فرد مهلت یا حق درخواست را از دست بدهد؛ مسیر کم‌کردن اثر می‌تواند ارجاع به متن رسمی و منع تصمیم نهایی باشد.

سناریو را از نتیجهٔ آزمون جدا کنید. «ممکن است اطلاعات منقضی باشد» خطر فرضی است؛ «نسخهٔ تاریخ‌دار X در محیط Y پاسخ Z داد» مشاهدهٔ مشخص است. هر دو مهم‌اند، اما یکی را به‌جای دیگری گزارش نکنید. برای خطرهای فصل ۶۴، به گزارش همان آزمون، scope و نسخه وصل شوید؛ شرح دوبارهٔ payload یا روش حمله در این فصل لازم نیست.

## ۱۷. ثبت ریسک: مالک و شاهد

دفتر ثبت ریسک، فهرست زندهٔ تصمیم‌هاست؛ یک قالب مناسب دست‌کم این فیلدها را دارد:

| فیلد | چه چیزی ثبت می‌شود؟ |
|---|---|
| شناسه و نسخه | ریسک و نسخهٔ سامانه‌ای که درباره‌اش تصمیم می‌گیرید |
| سناریو و افراد متأثر | شرط وقوع، مسیر اثر و کسی که ممکن است زیان ببیند |
| شدت و احتمال ذاتی | ارزیابی پیش از کنترل، همراه با تعریف مقیاس |
| مالک و درمان | فرد پاسخ‌گو و اقدام: پرهیز، کاهش، انتقال یا پذیرش |
| کنترل و مدرک | کنترل مشخص، آزمون/سند، وضعیت و محدودهٔ شاهد |
| ریسک باقی‌مانده | آنچه پس از کنترل هنوز می‌تواند رخ دهد |
| تصمیم و بازبینی | قبول/توقف، دلیل، تاریخ انقضا و محرک بازنگری |

هر ریسک باید یک مالک انسانیِ قابل‌تماس و اختیار روشن داشته باشد. عنوان کلی «تیم هوش مصنوعی» مالک نیست؛ و ثبت یک شاهد placeholder، تأیید آن شاهد محسوب نمی‌شود. وضعیت‌ها را از هم تفکیک کنید: طراحی‌شده، اجراشده، بازبینی‌شده، ناکام، پذیرفته‌شده یا منقضی‌شده.

## ۱۸. رتبه‌بندی کیفی، بدون نمرهٔ جعلی

شدت، احتمال، میزان مواجهه و برگشت‌پذیری می‌توانند برای مرتب‌سازی کیفی به‌کار روند؛ اما رتبه‌های ترتیبی را بی‌توضیح ضرب یا جمع نکنید و حاصل را «احتمال واقعی» ننامید. تعریف «بالا» باید برای سازمان و بافت روشن باشد؛ دو ارزیاب ممکن است با شواهد متفاوت به رتبه‌های متفاوت برسند. اختلاف دیدگاه را ثبت کنید، نه اینکه آن را با میانگین‌گیری ناپدید سازید.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="نمای کیفی ریسک با چهار مؤلفه: شدت، احتمال، میزان مواجهه و برگشت‌پذیری؛ این بردار عدد جمع‌پذیر یا احتمال آماری نیست."><mrow><mi>R</mi><mo>=</mo><mo>(</mo><mi>S</mi><mo>,</mo><mi>L</mi><mo>,</mo><mi>E</mi><mo>,</mo><mi>V</mi><mo>)</mo></mrow></math>

**متن جایگزین فرمول:** `R` یک بردار کیفی از شدت اثر `S`، احتمال `L`، میزان مواجهه `E` و امکان جبران `V` است؛ این نمایش، امتیاز عددی یا احتمال آماری تولید نمی‌کند.

از آستانه برای پرسیدن «چه چیزی نیازمند بازبینی بیشتر است؟» استفاده کنید، نه برای حذف نظر متخصص یا حق فرد متأثر. حتی اگر دو سناریو برچسب یکسان داشته باشند، ممکن است برگشت‌پذیری، دامنهٔ آسیب یا امکان اعتراضشان متفاوت باشد. قاعدهٔ توقف و ریسک‌های غیرقابل‌پذیرش را پیشاپیش تعیین کنید.

## ۱۹. درمان ریسک و باقی‌مانده

چهار انتخاب رایج عبارت‌اند از پرهیز از کاربرد، کاهش احتمال یا اثر، انتقال قراردادی بخشی از مسئولیت، و پذیرش آگاهانهٔ ریسک باقی‌مانده. انتقال به تأمین‌کننده یا بیمه، مسئولیت قانونی و اخلاقی سازمان را خودکار حذف نمی‌کند. برای هر اقدام، مالک، موعد، شاخص تکمیل و شاهد را ثبت کنید؛ «آموزش کاربر» اگر اختیار، زمان و مسیر اعتراض در کار واقعی وجود نداشته باشد کنترل کافی نیست.

پس از کنترل دوباره ارزیابی کنید و بنویسید کدام فرض تغییر کرده است. اگر ریسک هنوز بالاست، نام «ریسک باقی‌مانده» را صادقانه حفظ کنید؛ با تغییر برچسب یا انتقال کار به کاربر آن را ناپدید نکنید. پذیرش فقط در صورتی معنا دارد که اختیار پذیرش، دلیل، دامنه، محدودیت، تاریخ بازبینی و مسیر توقف مشخص باشند؛ ریسک ممنوع یا الزام‌آور را نمی‌توان با یک امضای داخلی مجاز کرد.

## ۲۰. دروازهٔ تصمیم، معیار توقف و بازگشایی

دروازهٔ انتشار یا ادامهٔ پایلوت باید معیار داشته باشد: آیا کاربرد و نسخه مشخص است؟ آیا مالک و کارشناس مستقل در دسترس‌اند؟ آیا شواهد مربوط به مهم‌ترین مسیرهای اثر وجود دارد؟ آیا ابهام بحرانی، ریسک بازِ غیرقابل‌قبول یا راه اعتراضِ ناموجود باقی مانده است؟ آیا تصمیم را می‌توان در بازهٔ محدود و با توقف سریع بازبینی کرد؟ اگر نه، گزینه‌ها «توقف»، «کاهش دامنه»، «طراحی کنترل تازه» یا «درخواست شواهد بیشتر» هستند.

تصمیم را زمان‌دار کنید و محرک بازگشایی بگذارید: تغییر مدل یا provider، داده، مخاطب، کاربرد، بازار، ابزار، policy، قانون، رخداد یا شواهدِ تازه. «تأیید شد» نباید به مجوز دائمی برای هر نسخه و گروه کاربری تبدیل شود. تأیید یک بستهٔ مستندات، رأی انسانی دربارهٔ کاربرد معین است، نه خاصیت ذاتی مدل.

## ۲۱. نقش‌ها، RACI و استقلال

RACI می‌تواند مسئول اجرا (Responsible)، پاسخ‌گوی نهایی (Accountable)، مشورت‌شونده (Consulted) و مطلع (Informed) را برای هر فعالیت جدا کند. برای یک تصمیم مهم، یک پاسخ‌گوی نهایی نام‌دار لازم است؛ اگر چند نفر یا کمیته حضور دارند، مرجع نهایی و شیوهٔ ثبت رأی را مشخص کنید. نقش‌ها را بر اساس وظیفه تعیین کنید، نه فقط عنوان شغلی.

توسعه‌دهنده نباید تنها داور کنترل خودش باشد؛ بازبینی متناسب با ریسک می‌تواند شامل متخصص داده، امنیت، privacy، حقوق، accessibility، کارکنان پشتیبانی یا نمایندهٔ افراد متأثر باشد. استقلال کامل همیشه ممکن نیست، اما تضاد منافع، دامنهٔ بازبینی و محدودیت منابع باید ثبت شود. این جدول نقش‌ها، جایگزین مسئولیت قانونی هیچ طرفی نیست.

## ۲۲. Model card: سندِ تصمیم

Model card روشی پیشنهادی برای همراه‌کردن مدل آموزش‌دیده با توضیح کاربرد مقصود، زمینه، روش‌های ارزیابی و ویژگی‌های عملکرد است. مقالهٔ Mitchell و همکاران بر گزارش شرایط ارزیابی و گروه‌های مرتبط با کاربرد تأکید می‌کند [۸]. هدف، کمک به سازنده و استفاده‌کننده برای دیدن محدودهٔ دانسته‌هاست؛ کارت نه تضمین کیفیت است، نه برچسب رسمی انطباق و نه گواهی «ایمن»بودن.

کارت را برای مخاطب واقعی بنویسید: تیم ادغام، خریدار، کارشناس ریسک، کاربر حرفه‌ای یا ناظر ممکن است به جزئیات متفاوت نیاز داشته باشند. عنوان دقیق مدل، شناسهٔ نسخه و وضعیت ناشر را بیاورید؛ اگر اطلاعات را از تأمین‌کننده نگرفته‌اید، فیلد را «نامعلوم» بگذارید. برداشت از یک کارت قدیمی را به نسخهٔ فعلی مدل تعمیم ندهید.

## ۲۳. اجزای مدل‌کارت

قالب سازمانی می‌تواند این موارد را پوشش دهد: شناسه و نسخه؛ سازنده و راه توزیع؛ مقصود و کاربردهای بیرون‌ازدامنه؛ زبان‌ها و جمعیت‌هایی که بررسی شده‌اند؛ داده‌ها یا منشأهای شناخته‌شده؛ روش ارزیابی و معیارها؛ شرایط هر آزمون؛ محدودیت‌ها و شکست‌های شناخته‌شده؛ نیاز به نظارت انسانی؛ تاریخ و مالک بازبینی؛ و پیوند به شواهد. اگر model card معیارهایی مانند accuracy یا نرخ خطا دارد، مخرج، مجموعه، نسخه، شرایط و عدم‌قطعیت را نیز ثبت کنید؛ فصل ۶۲ دربارهٔ طراحی خود معیار و فصل ۶۳ دربارهٔ تحلیل رفتار تفصیلی‌تر است.

فقط شاخص‌هایی را بیاورید که به کاربرد مربوط‌اند و پشتوانه دارند. عددِ میانگین ممکن است تفاوت زیرگروه‌ها، تفاوت زبان یا هزینهٔ خطا را پنهان کند. اگر دادهٔ لازم برای ارزیابی یک گروه موجود نیست، آن را اعلام کنید؛ جای خالی را با ادعای «عملکرد برابر» پر نکنید.

## ۲۴. کارت مدل و کارت سامانه یکی نیستند

| سند | واحد توصیف | سؤال محوری |
|---|---|---|
| Model card | مدل یا نسخهٔ مدل | این مدل با چه کاربرد و شرایطی ارزیابی یا عرضه شده است؟ |
| Data card / datasheet | مجموعه‌داده یا منبع داده | داده از کجا آمده، چگونه ساخته شده و چه خلأیی دارد؟ |
| System card | سامانهٔ ادغام‌شده | مدل، prompt، retrieval، ابزار، رابط و انسان چگونه با هم عمل می‌کنند؟ |
| Risk register | سناریوی ریسک | چه کسی ریسک را پیگیری می‌کند و تصمیم درمان چیست؟ |
| ارزیابی اثر | کاربرد در بافت مشخص | چه افرادی و با چه مسیرهایی ممکن است متأثر شوند؟ |

نام این سندها در صنعت یکدست نیست؛ پس دامنه را در سربرگ تعریف کنید. ممکن است یک سازمان «AI system card» بسازد که چند بخش را در خود دارد، اما نگه‌داشتن پیوندهای جدا به مدل، داده، کاربرد و شاهد هنوز ارزشمند است. کارت مدل یک جزء را توصیف می‌کند؛ نمی‌تواند همهٔ رفتارهایی را پیش‌بینی کند که از اتصال چند جزء به وجود می‌آیند.

## ۲۵. حدود ادعا در کارت مدل

کارت، آنچه گزارش نشده را آشکار می‌کند؛ اما نمی‌تواند خوداظهاری را به تأیید مستقل تبدیل کند. «مناسب همهٔ کاربران» به نمونه‌گیری و آزمون گسترده نیاز دارد؛ «داده ناشناس است» به تعریف تهدید و روش ارزیابی؛ «کم‌سوگیری است» به هدف، گروه، معیار و زمینه. از عبارت‌های فراگیر مثل «منصفانه»، «ایمن» یا «بی‌طرف» بدون دامنه و سنجه پرهیز کنید.

اگر مدل از تأمین‌کننده آمده، اطلاعات عمومی، مستند قراردادی و آزمون سازمان را از هم برچسب بزنید. کارت تجاری یا یک صفحهٔ بازاریابی می‌تواند سرنخ باشد، اما شاهدِ آزمون سازمان شما نیست. حریم محرمانهٔ تجاری را هم محترم بشمارید؛ برای بازبینی به‌جای افشای اطلاعات حساس در کارت عمومی، پیوند کنترل‌شده و دسترسی‌محدود نگه دارید.

## ۲۶. مستندسازی مجموعه‌داده

مدل‌کارت را با مستند داده کامل کنید. برای هر منبع بنویسید سازنده چه هدفی داشته، داده چگونه گردآوری یا تولید شده، چه پردازش و برچسب‌گذاری‌ای انجام شده، چه نسخه‌ای استفاده می‌شود، چه گروهی نمایندگی نمی‌شود و چه کاربردی مجاز یا نامناسب است. یک پروژه ممکن است چند منبع با مجوز و کیفیت متفاوت داشته باشد؛ نام پوشهٔ «training data» منشأ یا مجوز هیچ‌کدام را ثابت نمی‌کند.

اگر دادهٔ حساس، شخصی یا قراردادی در کار است، مستند را به محل نگهداری هر فیلد حساس تبدیل نکنید. شناسه، مسیر دسترسی امن و نقش مجاز کافی است؛ از انتشار نمونهٔ واقعی برای «شفافیت» پرهیز کنید. مستندسازی به معنی جمع‌آوری اطلاعات بیشتر نیست؛ اصل کمینه‌سازی داده همچنان برقرار است.

## ۲۷. Datasheets و Data Cards

Gebru و همکاران پیشنهاد کردند datasheet همراه مجموعه‌داده، انگیزه، ترکیب، فرایند گردآوری و کاربردهای توصیه‌شده را توضیح دهد تا سازنده و مصرف‌کننده دربارهٔ داده گفت‌وگوی دقیق‌تری داشته باشند [۹]. Pushkarna و همکاران Data Cards را به‌صورت خلاصه‌های ساختاریافته و انسان‌محور معرفی می‌کنند که منشأ، توسعه، هدف، ملاحظه‌های اخلاقی و روش جمع‌آوری/برچسب‌گذاری را در چرخهٔ عمر داده به مخاطبان مختلف منتقل کند [۱۰]. این‌ها الگوهای مستندسازی پژوهشی‌اند، نه قانون یا قالب اجباری واحد.

نام ابزار مهم‌تر از پوشش سؤال‌ها نیست. «datasheet»، «data card» و «dataset statement» می‌توانند ساختارهای متفاوتی داشته باشند؛ هدف مشترک، کاهش فاصلهٔ میان کسی است که داده را ساخته و کسی که آن را دوباره به‌کار می‌گیرد. قالب باید قابل‌مقایسه، قابل‌به‌روزرسانی و متناسب با حساسیت داده باشد.

## ۲۸. فیلدهای داده‌کارت

برای یک مجموعه‌داده، این پرسش‌ها را پاسخ دهید: چه کسی و چرا آن را ایجاد کرد؟ منبع و بازهٔ گردآوری چیست؟ چه فرایندی برای پاک‌سازی، انتخاب، برچسب‌گذاری یا تولید به‌کار رفت؟ واحد نمونه‌گیری و معیار حذف چه بود؟ مجوز و حقوق استفاده از کجا معلوم می‌شود؟ چه زبان، جمعیت، زمان یا شرایطی کم‌نمایی شده‌اند؟ کاربردهای موردانتظار و خارج از دامنه کدام‌اند؟ چگونه خطا یا درخواست اصلاح ثبت می‌شود؟

برای مصرف‌کننده، «کیفیت داده» را به یک امتیاز کلی فرو نکاهید. کیفیت باید نسبت به هدف، پوشش، تازه‌بودن، برچسب، خطا و هزینهٔ اشتباه توضیح داده شود. اگر روش نمونه‌گیری معلوم نیست، آن را مجهول نگه دارید؛ و اگر فهرست فیلدها از vendor آمده، منبع و تاریخ دریافت را کنار آن ثبت کنید.

## ۲۹. منشأ، حقوق، privacy و نگهداری

برای هر منبع، زنجیرهٔ گردآوری، انتقال، تبدیل و نسخه را ثبت کنید؛ در کنار آن، مبنای مجاز استفاده، محدودیت قرارداد، دادهٔ شخصی احتمالی، دورهٔ نگهداری و مسیر حذف را جداگانه بررسی کنید. علامت «public» به معنای مجاز برای هر آموزش یا کاربرد ثانویه نیست. مجوزِ repository یا مدل نیز مجوزِ دادهٔ آموزشی را ثابت نمی‌کند.

اگر نمونه‌ای برای ممیزی لازم است، دسترسی محدود و کمینه را انتخاب کنید و مالک، مقصد، مدت نگهداری و روش پاک‌سازی را ثبت کنید. فیلد `personal_data: false` در fixture این پروژه فقط یک مقدار ساختگی است؛ در دادهٔ واقعی، تشخیص و تفسیر آن نیاز به بررسی مسئول privacy و تعریف‌های قانونی مربوط دارد. Hash می‌تواند تغییر بایت را آشکار کند، نه رضایت، مالکیت، صحت یا بی‌طرفی را.

## ۳۰. تبار، شواهد و پیوند نسخه‌ها

برای هر artifact شناسهٔ پایدار و نسخهٔ قابل‌ردیابی نگه دارید: مدل، داده، prompt، مجموعهٔ ارزیابی، کد، پیکربندی، گزارش و تصمیم. پیوندها باید نشان دهند کدام شاهد به کدام کاربرد و نسخه مربوط است؛ لینک شکسته یا نام فایلِ مبهم زنجیرهٔ بررسی را قطع می‌کند. اگر داده محرمانه است، شناسه و مسیر کنترل‌شده را ثبت کنید، نه لزوماً خود داده را در گزارش عمومی.

Hash برای تمامیت فایل مفید است، اما «hash ثبت شد» به‌معنای provenance کامل نیست؛ باید روشن باشد چه کسی فایل را از کجا گرفته و قبل از hash چه تبدیلی انجام شده است. ثبت زمان، ابزار، نسخه و صاحب خروجی به بازتولید کمک می‌کند؛ امضای دیجیتال در صورت استفاده، هویت امضاکننده و مدیریت کلید می‌خواهد و باز هم کیفیت محتوا را ثابت نمی‌کند.

## ۳۱. تأمین‌کننده و اجزای ثالث

در خرید یا اتصال مدل و دادهٔ بیرونی، اطلاعاتی را که فروشنده می‌دهد به‌عنوان ورودی بازبینی ثبت کنید: revision، کاربرد اعلام‌شده، محدودیت، سطح سرویس، رخدادهای قابل‌گزارش، نگهداری داده، تغییر نسخه، مسیر حذف و حقوق استفاده. قرارداد می‌تواند مسئولیت‌ها را تقسیم کند، اما سازمان باید همچنان بداند خودش چه استفاده‌ای می‌کند و چه گروهی متأثر است.

اگر vendor پاسخ نمی‌دهد، سؤال را به ریسک با مالک و تصمیم تبدیل کنید؛ ناتوانی در دریافت شواهد را «نبود ریسک» تعبیر نکنید. بستهٔ مستندات تأمین‌کننده ممکن است به مدل دیگری، نسخهٔ قدیمی یا کاربرد عمومی مربوط باشد؛ hash، تاریخ و دامنهٔ آن را مقایسه کنید. پیش از انتخاب، امکان تعویض یا توقف سرویس را نیز به‌عنوان تصمیم حکمرانی ثبت کنید.

## ۳۲. شفافیت و منشأ محتوای تولیدشده

NIST AI 600-1 منشأ محتوا را یکی از ملاحظه‌های اصلی خود می‌گیرد و بر ضرورت اطلاعاتی تأکید دارد که برای فهم منشأ و تاریخچهٔ محتوای تولیدی به‌کار می‌آید [۵]. در سطح محصول، سازمان باید روشن کند چه کسی به چه اطلاعاتی برای اعتماد یا بازبینی نیاز دارد، چه محتوایی مصنوعی است و چه داده‌ای باید همراه خروجی بماند. این موضوع با صدق پاسخ فرق دارد: برچسب «ساخت AI» حقیقت یا مجوز را اثبات نمی‌کند.

مادهٔ ۵۰ AI Act تکلیف‌های شفافیت مشخصی برای بعضی سامانه‌ها و نقش‌ها دارد و طبق خط زمانی کمیسیون از ۲ اوت ۲۰۲۶ شروع به اعمال کرده است؛ دامنهٔ دقیق هر بند را از متن جاری بررسی کنید [۲، ۳، ۱۱]. انتقال مسئولیت به یک واترمارک یا برچسب واحد کافی نیست؛ روش فنی باید با مسیر انتشار، حذف metadata، مصرف‌کننده و الزامات قانونیِ همان مورد سازگار باشد.

## ۳۳. رخداد، شکایت و افشا

پیش از استفاده، مشخص کنید چه چیزی «رخداد» محسوب می‌شود، چه کسی می‌تواند آن را گزارش کند، چه کسی شدت را ارزیابی می‌کند و چه زمانی موضوع به مدیر، حقوقی، privacy، مشتری یا نهاد مربوط ارجاع می‌شود. آستانهٔ داخلی نباید باعث شود سازمان گزارش الزام‌آور قانونی را از دست بدهد؛ متن و زمان‌بندی مربوط را جداگانه بررسی کنید.

مستند رخداد را به کمینهٔ لازم محدود کنید: شناسهٔ نسخه و زمان، شرح اثر، افراد/سامانه‌های متأثر، کنترل فعال، تصمیم گرفته‌شده و اقدام اصلاحی. اطلاعات شخصی یا راز را بی‌دلیل در ticket و گزارش تکثیر نکنید. پس از رسیدگی، تحلیل علت، تغییر کنترل، به‌روزرسانی اسناد و اطلاع‌رسانی لازم را ثبت کنید؛ یک گزارش بسته‌شده بدون یادگیری، چرخهٔ حکمرانی را کامل نمی‌کند.

## ۳۴. بازبینی دوره‌ای و تغییرهای محرک

تاریخ بازبینی را برای هر سند و تصمیم تعیین کنید؛ «آخرین ویرایش» بدون موعد بعدی تضمین نمی‌کند اطلاعات هنوز درست است. بازبینی زودتر از موعد را در صورت تغییر هدف، مدل، prompt، داده، vendor، زبان، گروه مخاطب، ابزار، سطح دسترسی، کشور/بازار، قانون یا رخداد فعال کنید. تغییر کوچکِ UI ممکن است مسیر استفاده را عوض کند و تغییر ظاهراً بزرگِ وزن‌ها ممکن است برای یک کاربرد هیچ اثری نداشته باشد؛ دامنهٔ بازبینی را با اثر واقعی تنظیم کنید.

سندهای قدیمی را بی‌علامت جایگزین نکنید: نسخهٔ پیشین، تاریخ اثرگذاری، دلیل تغییر و تصویب را نگه دارید. اگر تصمیم قبلی دیگر معتبر نیست، آن را «منقضی» یا «جایگزین‌شده» نشان دهید و بگویید چه استفاده‌ای تا بازبینی مجدد متوقف می‌شود. این کار از تفسیر یک کارت قدیمی به‌عنوان گواه نسخهٔ جاری جلوگیری می‌کند.

## ۳۵. مطالعهٔ موردی: CampusGuide

فرض کنید یک کالج خیالی دستیار متنی برای توضیح قواعد منتشرشدهٔ انتخاب واحد و بورسیه می‌سازد. هدف، یافتن صفحهٔ مرتبط و توضیح زبان ساده است؛ سامانه نباید دربارهٔ پذیرش یا واجدشرایط‌بودن تصمیم بگیرد. مخاطب اصلی دانشجوست، اما مشاور آموزشی نیز ممکن است خروجی را ببیند. این کاربرد می‌تواند کار جست‌وجو را آسان کند، اما پاسخ منقضی، افشای رکورد شخصی یا پوشش زبانی نابرابر پیامد دارد.

| مسیر | کنترل مدیریتی یا محصولی | شاهدی که باید پیش از ادعای تکمیل بررسی شود |
|---|---|---|
| پاسخ قدیمی دربارهٔ مهلت بورسیه | تاریخ و مالک محتوا؛ لینک مستقیم به منبع رسمی؛ منع تصمیم نهایی | بررسی منبع و نسخهٔ قواعد؛ آزمون مسیر ارجاع در نسخهٔ معین |
| ورود رکورد دانشجو | جلوگیری از ورود دادهٔ شخصی تا پایان بازبینی مجاز | طراحی جریان داده و تصمیم privacy؛ نه فقط جملهٔ «داده ذخیره نمی‌شود» |
| کاربر فارسی‌زبان با پاسخ ناقص | اعلام دامنهٔ زبانِ بررسی‌نشده و دسترسی به مشاور | آزمون متناسب با جمعیت و کاربرد؛ اگر انجام نشده، ثبت شکاف |
| تغییر ارائه‌دهنده یا پایگاه قواعد | بازشدن دوبارهٔ مرور نسخه و ریسک | ثبت وابستگی، تاریخ تغییر و تصمیمِ نسخهٔ جدید |

در مثال آموزشی این فصل، تصمیم «hold» است: هیچ مطالعهٔ حقوقی، privacy، ارزیابی کاربر یا آزمون مدل واقعی انجام نشده است. کنترل‌های پیشنهادی، برنامه‌اند و شواهدِ کارکردشان باید پیش از هر کاربرد واقعی جداگانه فراهم شوند.

## ۳۶. بستهٔ حاکمیت نمونه و آزمایشگاه

بستهٔ نمونه در [پروژهٔ فصل](book-engineering/projects/65-governance-lab/README.md) یک فایل JSON، model card، data card، چهار سناریوی ریسک، پنج شناسهٔ شاهد و تصمیم `hold` دارد. همهٔ داده ساختگی است. `governance_check.py` فقط وجود فیلدهای لازم، مقادیر کیفی مجاز، یکتایی شناسه‌ها و پیوندهای داخلی را کنترل می‌کند؛ `structurally_valid: true` نمی‌گوید شاهد واقعی کافی است، پرونده مطابق قانون است یا انتشار مجاز است. خروجی `release_authorized` همیشه `false` باقی می‌ماند.

از پوشهٔ پروژه، این دو فرمان را اجرا کنید: `python -m unittest discover -v` و `python governance_check.py --output results.json`. دوازده آزمون واحد، از جمله ورودی‌های بدساخت با نوع نامناسب، نبود مالک، شناسهٔ تکراری، رتبهٔ نامعتبر، شاهدِ پیوندنشده و تأیید انسانیِ ناقص را پوشش می‌دهند. `fixture_manifest.json` hash همان ورودی را ثبت می‌کند؛ `environment.json` محیط و نبود شبکه/مدل را مشخص می‌کند؛ `results.json` خروجی CLI است. این آزمایشگاه روش مستندسازی را تمرین می‌دهد، نه ممیزی واقعی یا گواهی انطباق را.

## ۳۷. ضدالگوها و چک‌لیست ۳۰روزه

**تیک‌زنی بی‌شاهد:** «تست شد» بدون نسخه و خروجی؛ **مالکیت مبهم:** نام تیم به‌جای تصمیم‌گیر پاسخ‌گو؛ **عددسازی:** ضرب چند رتبهٔ ترتیبی و نامیدن آن به‌عنوان احتمال؛ **سند تبلیغاتی:** فقط موفقیت‌ها، بدون شکست و جمعیت بررسی‌نشده؛ **کپی کورکورانه:** استفاده از کارت مدل برای سامانهٔ ادغام‌شده؛ **انتقال مسئولیت:** فرض اینکه تأمین‌کننده یا کاربر همهٔ پاسخ‌گویی را برعهده دارد؛ و **کهنه‌ماندن:** سندی بدون تاریخ بازبینی یا محرک تغییر.

برای شروع محدود: هفتهٔ اول inventory، کاربرد، نقش‌ها و بازار را ثبت کنید؛ هفتهٔ دوم افراد متأثر، مسیر اثر و ریسک‌های اولویت‌دار را با مالک مرور کنید؛ هفتهٔ سوم کارت مدل/داده، crosswalk تعهدها و پیوند شواهد را کامل کنید؛ هفتهٔ چهارم شکاف‌ها، معیار توقف، تصمیم‌گیر نهایی و تاریخ بازبینی را تعیین کنید. این برنامه به‌تنهایی «انطباق در ۳۰ روز» نمی‌دهد؛ خروجی آن فهرست کار و ابهام‌های باز است.

## ۳۸. تمرین‌ها

۱. برای دستیار خیالیِ پاسخ‌گویی به کارکنان، یک مثال از قانون، استاندارد، چارچوب و سیاست داخلی بنویسید و توضیح دهید چرا عنوان سند به‌تنهایی دامنهٔ الزام را تعیین نمی‌کند.

۲. در جدول زمان‌بندی فصل، تفاوت ۲۷ ژوئیهٔ ۲۰۲۶، ۲ اوت ۲۰۲۶، ۲ دسامبر ۲۰۲۶، ۲ دسامبر ۲۰۲۷ و ۲ اوت ۲۰۲۸ را توضیح دهید. کدام نتیجه‌ها را بدون بررسی نقش و دامنه نمی‌توان گرفت؟

۳. برای CampusGuide یک خروجی نمونه از هر چهار تابع NIST AI RMF بنویسید و مشخص کنید چرا «چارچوب داوطلبانه» به‌تنهایی جای بررسی قانون یا قرارداد را نمی‌گیرد.

۴. Model card، data card، system card، risk register و ارزیابی اثر را از نظر واحد توصیف و پرسش اصلی با هم مقایسه کنید.

۵. برای یک خطرِ پاسخ منقضی در CampusGuide، چهار مؤلفهٔ بردار کیفی ریسک را جدا بنویسید. چرا نباید رتبه‌های ترتیبی را بی‌توضیح در هم ضرب کنید؟

۶. اگر یک ریسک باقی‌مانده «شدید» است، شاهد فقط fixture ساختگی است و مالک انسانی نام‌گذاری نشده، چه تصمیمی برای دروازهٔ انتشار می‌گیرید و کدام شکاف‌ها را اول می‌بندید؟

۷. خروجی پروژهٔ فصل می‌گوید `structurally_valid: true` و `release_authorized: false`. دقیقاً چه چیزی بررسی شده است و دست‌کم سه چیزی که نمی‌توان از آن نتیجه گرفت چیست؟

۸. سه تغییر را که باید بازبینی را دوباره فعال کنند نام ببرید و برای یکی از آن‌ها پیوند نسخه، مالک، مدرک و تصمیم موردنیاز را شرح دهید.

## ۳۹. جمع‌بندی

حکمرانی کارِ اتصالِ کاربرد، فرد متأثر، نقش، قانون یا چارچوب، سند، شاهد، مالک و تصمیم است. AI Act قانون الزام‌آور با زمان‌بندی و نقش‌های خاص است؛ NIST AI RMF و استانداردهای ISO ابزارهای متفاوتی برای سازمان‌دهی کارند؛ و کارت مدل و داده راهی برای مستندسازی زمینه و محدودیت‌اند، نه مهر تأیید. ریسک باقی‌مانده را با تعریف روشن ثبت کنید؛ مقدار نامعلوم را پنهان نکنید؛ و با تغییر نسخه یا کاربرد، ارزیابی را باز کنید.

برای مرور سؤال‌ها از [پاسخ‌نامهٔ مستقل فصل ۶۵](book-engineering/answers/65-alignment-governance-fa.md)، برای اجرای schema checker از [README آزمایشگاه](book-engineering/projects/65-governance-lab/README.md) و برای دامنه و نتیجهٔ آزمون‌ها از [گزارش ممیزی فصل ۶۵](book-engineering/chapters/65-audit-report-fa.md) استفاده کنید. خروجی این milestone وب/PWA و Markdown است؛ PDF و EPUB تولید یا آزموده نشده‌اند.

## ۴۰. منابع و تاریخ بازبینی منابع

منابع زیر برای ادعاهای مقرراتی، چارچوبی و مستندسازی استفاده شده‌اند. صفحه‌های وب و متن‌های رسمی در ۷ نوامبر ۲۰۲۶ بازبینی شدند؛ زمان‌بندی حقوقی باید پیش از استفادهٔ واقعی دوباره از منبع جاری کنترل شود.

- ۱ — European Commission. AI Omnibus enters into force. Published 27 July 2026.
   <https://digital-strategy.ec.europa.eu/en/news/ai-omnibus-enters-force>

- ۲ — European Commission AI Act Service Desk. Timeline for the Implementation of the EU AI Act.
   <https://ai-act-service-desk.ec.europa.eu/en/ai-act/timeline/timeline-implementation-eu-ai-act>

- ۳ — European Union. Regulation (EU) 2026/1744, Digital Omnibus on AI; EUR-Lex, in force.
   <https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng>

- ۴ — National Institute of Standards and Technology. Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1; official status page.
   <https://www.nist.gov/itl/ai-risk-management-framework>
   <https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf>

- ۵ — National Institute of Standards and Technology. Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile, NIST AI 600-1, July 2024.
   <https://doi.org/10.6028/NIST.AI.600-1>
   <https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf>

- ۶ — International Organization for Standardization and International Electrotechnical Commission. ISO/IEC 42001:2023, Artificial intelligence — Management system.
   <https://www.iso.org/standard/42001>

- ۷ — International Organization for Standardization and International Electrotechnical Commission. ISO/IEC 42005:2025, AI system impact assessment.
   <https://www.iso.org/standard/42005>

- ۸ — Mitchell, M., et al. Model Cards for Model Reporting. FAT* 2019. DOI: 10.1145/3287560.3287596.
   <https://doi.org/10.1145/3287560.3287596>
   <https://arxiv.org/abs/1810.03993>

- ۹ — Gebru, T., et al. Datasheets for Datasets. Communications of the ACM, 64(12), 2021. DOI: 10.1145/3458723.
   <https://doi.org/10.1145/3458723>
   <https://arxiv.org/abs/1803.09010>

- ۱۰ — Pushkarna, M., Zaldivar, A., and Kjartansson, O. Data Cards: Purposeful and Transparent Dataset Documentation for Responsible AI. ACM FAccT 2022. DOI: 10.48550/arXiv.2204.01075.
   <https://doi.org/10.48550/arXiv.2204.01075>
   <https://arxiv.org/abs/2204.01075>

- ۱۱ — European Union. Regulation (EU) 2024/1689, consolidated text as of 27 July 2026; read with the amendments and application dates in Regulation (EU) 2026/1744.
   <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02024R1689-20260727>

## پیوست اجرایی

فایل زیر همان برنامهٔ آزموده‌شدهٔ پروژه است؛ برای کار با بستهٔ نمونه، به‌جای تغییر کد، یک کپی از JSON بسازید و تغییرهایش را جداگانه ممیزی کنید.

```python
"""Validate the structure of a synthetic AI-governance evidence pack."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_FIXTURE = ROOT / "governance_pack.json"
SCHEMA_VERSION = "1.0"
SEVERITY_LEVELS = {"low", "moderate", "high", "critical"}
LIKELIHOOD_LEVELS = {"rare", "possible", "likely"}
TREATMENTS = {"avoid", "mitigate", "transfer", "accept"}
EVIDENCE_STATES = {"planned", "fixture_only", "reviewed"}
RISK_STATES = {"planned", "in_progress", "mitigated", "accepted"}


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _has_text_items(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_has_text(item) for item in value)


def _is_allowed(value: Any, allowed: set[str]) -> bool:
    return isinstance(value, str) and value in allowed


def _require_fields(value: Any, fields: tuple[str, ...], path: str,
                    errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return
    for field in fields:
        if not _has_text(value.get(field)):
            errors.append(f"{path}.{field} must be a non-empty string")


def validate_pack(pack: Any) -> list[str]:
    """Return schema/completeness errors; this function is not a compliance audit."""
    errors: list[str] = []
    if not isinstance(pack, dict):
        return ["pack must be a JSON object"]

    if pack.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION!r}")
    if not _has_text(pack.get("pack_id")):
        errors.append("pack_id must be a non-empty string")
    if not _has_text(pack.get("fixture_id")):
        errors.append("fixture_id must be a non-empty string")

    system = pack.get("system")
    _require_fields(
        system,
        ("system_id", "name", "provider", "deployer", "version", "intended_use", "review_by"),
        "system",
        errors,
    )
    if isinstance(system, dict):
        if not _has_text_items(system.get("out_of_scope_uses")):
            errors.append("system.out_of_scope_uses must be a non-empty list of non-empty strings")
        try:
            date.fromisoformat(system.get("review_by", ""))
        except (TypeError, ValueError):
            errors.append("system.review_by must be an ISO date")

    model_card = pack.get("model_card")
    _require_fields(
        model_card,
        ("model_id", "provider", "revision", "intended_use", "evaluation_status"),
        "model_card",
        errors,
    )
    if isinstance(model_card, dict) and not _has_text_items(model_card.get("limitations")):
        errors.append("model_card.limitations must be a non-empty list of non-empty strings")

    evidence = pack.get("evidence")
    evidence_ids: set[str] = set()
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a non-empty list")
        evidence = []
    for index, item in enumerate(evidence):
        path = f"evidence[{index}]"
        _require_fields(item, ("id", "kind", "scope"), path, errors)
        if not isinstance(item, dict):
            continue
        evidence_id = item.get("id")
        if _has_text(evidence_id):
            if evidence_id in evidence_ids:
                errors.append(f"{path}.id is duplicated: {evidence_id}")
            evidence_ids.add(evidence_id)
        if not _is_allowed(item.get("status"), EVIDENCE_STATES):
            errors.append(f"{path}.status must be one of {sorted(EVIDENCE_STATES)}")

    data_cards = pack.get("dataset_cards")
    if not isinstance(data_cards, list) or not data_cards:
        errors.append("dataset_cards must be a non-empty list")
        data_cards = []
    dataset_ids: set[str] = set()
    for index, card in enumerate(data_cards):
        path = f"dataset_cards[{index}]"
        _require_fields(
            card,
            ("dataset_id", "name", "source", "collection_method", "license_status", "intended_use", "review_by"),
            path,
            errors,
        )
        if not isinstance(card, dict):
            continue
        dataset_id = card.get("dataset_id")
        if _has_text(dataset_id):
            if dataset_id in dataset_ids:
                errors.append(f"{path}.dataset_id is duplicated: {dataset_id}")
            dataset_ids.add(dataset_id)
        if not _has_text_items(card.get("known_gaps")):
            errors.append(f"{path}.known_gaps must be a non-empty list of non-empty strings, including known unknowns")
        if not isinstance(card.get("personal_data"), bool):
            errors.append(f"{path}.personal_data must be an explicit boolean")
        try:
            date.fromisoformat(card.get("review_by", ""))
        except (TypeError, ValueError):
            errors.append(f"{path}.review_by must be an ISO date")

    risks = pack.get("risk_register")
    if not isinstance(risks, list) or not risks:
        errors.append("risk_register must be a non-empty list")
        risks = []
    risk_ids: set[str] = set()
    high_residual_open = []
    for index, risk in enumerate(risks):
        path = f"risk_register[{index}]"
        if not isinstance(risk, dict):
            errors.append(f"{path} must be an object")
            continue
        for field in ("id", "scenario", "control_owner"):
            if not _has_text(risk.get(field)):
                errors.append(f"{path}.{field} must be a non-empty string")
        risk_id = risk.get("id")
        if _has_text(risk_id):
            if risk_id in risk_ids:
                errors.append(f"{path}.id is duplicated: {risk_id}")
            risk_ids.add(risk_id)
        if not _has_text_items(risk.get("affected_parties")):
            errors.append(f"{path}.affected_parties must be a non-empty list of non-empty strings")
        if not _is_allowed(risk.get("inherent_severity"), SEVERITY_LEVELS):
            errors.append(f"{path}.inherent_severity is not a defined qualitative level")
        if not _is_allowed(risk.get("residual_severity"), SEVERITY_LEVELS):
            errors.append(f"{path}.residual_severity is not a defined qualitative level")
        if not _is_allowed(risk.get("inherent_likelihood"), LIKELIHOOD_LEVELS):
            errors.append(f"{path}.inherent_likelihood is not a defined qualitative level")
        if not _is_allowed(risk.get("treatment"), TREATMENTS):
            errors.append(f"{path}.treatment must be one of {sorted(TREATMENTS)}")
        if not _is_allowed(risk.get("status"), RISK_STATES):
            errors.append(f"{path}.status must be one of {sorted(RISK_STATES)}")
        if not _has_text_items(risk.get("controls")):
            errors.append(f"{path}.controls must be a non-empty list of non-empty strings")
        refs = risk.get("evidence_refs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"{path}.evidence_refs must be a non-empty list")
        elif any(not _has_text(ref) for ref in refs):
            errors.append(f"{path}.evidence_refs must contain non-empty string ids")
        elif any(ref not in evidence_ids for ref in refs):
            errors.append(f"{path}.evidence_refs contains an unknown evidence id")
        if _is_allowed(risk.get("residual_severity"), {"high", "critical"}) and risk.get("status") != "accepted":
            high_residual_open.append(risk_id or f"risk-{index}")

    decision = pack.get("decision")
    if not isinstance(decision, dict):
        errors.append("decision must be an object")
        decision = {}
    if not _is_allowed(decision.get("gate_status"), {"hold", "approved", "rejected"}):
        errors.append("decision.gate_status must be hold, approved, or rejected")
    if not _has_text(decision.get("rationale")):
        errors.append("decision.rationale must be a non-empty string")
    if decision.get("gate_status") == "approved":
        if not _has_text(decision.get("approved_by")) or not _has_text(decision.get("approved_at")):
            errors.append("an approved gate needs a named human approver and approval date")
        if high_residual_open:
            errors.append("an approved gate cannot leave high or critical residual risks without explicit acceptance")

    return errors


def analyze(pack: Any, fixture_bytes: bytes) -> dict[str, Any]:
    """Produce a deterministic schema-check report without authorizing deployment."""
    errors = validate_pack(pack)
    risks = pack.get("risk_register", []) if isinstance(pack, dict) else []
    evidence = pack.get("evidence", []) if isinstance(pack, dict) else []
    decision = pack.get("decision", {}) if isinstance(pack, dict) else {}
    if not isinstance(risks, list):
        risks = []
    if not isinstance(evidence, list):
        evidence = []
    if not isinstance(decision, dict):
        decision = {}
    return {
        "fixture_id": pack.get("fixture_id") if isinstance(pack, dict) else None,
        "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "risk_count": len(risks),
        "evidence_count": len(evidence),
        "structurally_valid": not errors,
        "validation_errors": errors,
        "gate_status": decision.get("gate_status"),
        "release_authorized": False,
        "scope": (
            "Structural validation of one synthetic governance pack only; "
            "not a compliance audit, certification, legal opinion, or release authorization."
        ),
        "limitations": [
            "The fixture is synthetic and contains no personal data, actual model, or production evidence.",
            "The validator checks field presence and internal references, not the truth, quality, or sufficiency of evidence.",
            "Qualitative severity and likelihood labels are not probabilities and are not aggregated into a numeric score.",
            "A valid schema does not establish legal applicability, conformity, safety, fairness, privacy, or fitness for use.",
            "The release_authorized field is always false; approval belongs to an accountable human process.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, help="write deterministic JSON to this path")
    args = parser.parse_args()
    fixture_bytes = args.fixture.read_bytes()
    pack = json.loads(fixture_bytes.decode("utf-8"))
    result = analyze(pack, fixture_bytes)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote synthetic governance-pack validation: {args.output}")
    else:
        print(rendered, end="")
    return 0 if result["structurally_valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
```

---

# جلد پنجم، فصل ۵ — API و FastAPI، Backend، Frontend، برنامهٔ وب و موبایل؛ قرارداد داده و آزمایش

**نگاشت:** فصل محلی ۵ جلد پنجم = فصل سراسری ۶۶. **تاریخ بازبینی منابع: ۷ نوامبر ۲۰۲۶.** فصل ۶۵ دربارهٔ حکمرانی، مالکیت تصمیم و ریسک بود؛ این فصل آن مرزها را به یک رابط محصولِ قابل‌آزمون تبدیل می‌کند. تمرکز بر API، قرارداد داده، backend، frontend و آزمون رابط است؛ بهینه‌سازی runtime، Cache، صف، تأخیر و توان عملیاتی برای فصل ۶۷ می‌ماند. احراز هویت، مجوز، محدودیت نرخ، ثبت رخداد، پایش و پاسخ به رخداد موضوع فصل ۶۸ است؛ انتشار، CI/CD و بازگشت نسخه در فصل ۶۹ می‌آید. نمونهٔ این فصل یک fixture ساختگی دارد و هیچ مدل زنده‌ای را اجرا نمی‌کند.

**پیش‌نیاز:** آشنایی با JSON، HTTP، آزمون نرم‌افزار، فصل‌های ۶۲ تا ۶۵ و چرخهٔ داده/مدل. **خروجی:** بتوانید نیاز کاربر را به قرارداد نسخه‌دار تبدیل کنید، endpoint و پاسخ/خطا را با FastAPI پیاده‌سازی کنید، یک رابط وب راست‌به‌چپ را به همان قرارداد وصل کنید، و با fixture ثابت، آزمون API و آزمون مرورگر بنویسید؛ بدون آنکه موفقیت ساختاری را با کیفیت مدل، امنیت یا آمادگی انتشار یکی بگیرید.

![شکل ۵-۵-۱ — دو مصرف‌کنندهٔ وب و موبایل از قرارداد نسخهٔ ۱٫۰ برای فرستادن پرسش ساختگی به endpoint `POST /v1/assist` استفاده می‌کنند؛ قرارداد ورودی را به پرسشِ حداکثر ۳۰۰ نویسه محدود می‌کند و پاسخ موفق را با وضعیت ۲۰۰ یا خطای ساختاری را با وضعیت ۴۲۲ به رابط برمی‌گرداند. backend ورودی را اعتبارسنجی و از fixture محلی پاسخ نمایشی می‌سازد؛ رابط حالت بارگذاری، موفقیت یا خطا را نشان می‌دهد. آزمون‌های schema، API و رابط هر دو مسیر را می‌سنجند. رنگ‌ها تزئینی‌اند و نمودار کیفیت مدل، امنیت، تأخیر یا آمادگی استقرار را نمی‌سنجد.](../diagrams/v5-ch05-api-contract.svg)

**شکل ۵-۵-۱ —** یک قرارداد ماشین‌خوان، ورودی و خروجی مشترک وب و موبایل را مشخص می‌کند؛ اعتبارسنجی backend، پاسخ ساختگی و حالت‌های UI جداگانه اما به‌هم‌پیوسته آزموده می‌شوند.

## ۱. از تصمیم حکمرانی تا محصول قابل‌استفاده

در فصل ۶۵ برای کاربرد، افراد متأثر، مالک تصمیم و محدودیت‌ها مرز گذاشتیم. API جایی است که بخشی از آن تصمیم‌ها به پیام‌های دقیقِ ماشینی تبدیل می‌شوند: کدام ورودی پذیرفته است، چه خروجی‌ای تضمین می‌شود، خطا چگونه اعلام می‌شود و کلاینت با کدام نسخه گفت‌وگو می‌کند. قرارداد خوب جای حکمرانی را نمی‌گیرد؛ اما بدون قرارداد، تصمیم‌های فصل قبل در چند کلاینت، چند تیم و چند تفسیر ناسازگار پخش می‌شوند.

در این فصل «محصول» را نه خود مدل، بلکه تجربه‌ای می‌گیریم که کاربر می‌تواند در بافت معین استفاده کند: رابط، API، backend، منبع داده یا مدلِ پشت آن، و مرزهای اعتماد. آزمایشگاه پیوست عمداً فقط fixture می‌خواند. این انتخاب امکان آزمودن قرارداد را می‌دهد، اما هیچ شاهدی دربارهٔ سودمندی یا درستی پاسخ یک مدل واقعی فراهم نمی‌کند.

## ۲. از کاربر و تصمیم به نیازمندی آزمون‌پذیر

«یک دستیار هوش مصنوعی بسازیم» نیازمندی محصول نیست؛ معلوم نمی‌کند چه کسی چه کاری می‌کند، پاسخ چه اثری دارد، کدام ورودی مجاز است یا چه خطایی قابل‌قبول نیست. نیازمندی را از مسیر کاربر بنویسید: «کاربرِ فارسی‌زبان پرسش کوتاهی دربارهٔ راهنمای منتشرشده می‌فرستد؛ محصول یا منبع ساختگی را نشان می‌دهد یا خطای قابل‌فهم می‌دهد؛ هیچ پاسخ ماشینی به‌تنهایی تصمیم واجدشرایط‌بودن نمی‌سازد.» همین جمله scope، قرارداد و آزمون را محدود می‌کند.

برای هر نیازمندی، ورودی، پیش‌شرط، پاسخ قابل‌مشاهده و شکست موردانتظار را تعیین کنید. عباراتی مثل «سریع»، «دقیق» و «امن» باید به سنجه و برنامهٔ جداگانه تبدیل شوند؛ این فصل فقط قرارداد و چند مسیر رابط را می‌آزماید. هدف کیفیت پاسخ، ریسک و معیار پذیرش باید در فصل‌های مربوط به خود تعریف شوند، نه با نام endpoint پوشانده شوند.

## ۳. برش کوچک محصول و معیار پذیرش

پیش از انتخاب framework، کوچک‌ترین برشی را انتخاب کنید که یک کاربر بتواند از ابتدا تا انتها انجام دهد. برای نمونه: صفحه پرسش را نشان دهد؛ درخواستِ معتبر ارسال شود؛ backend فیلدها را بررسی کند؛ پاسخ ثابت همراه شناسهٔ منبع برگردد؛ رابط آن را به‌صورت متن نمایش دهد؛ و کاربر در خطا پیام قابل‌فهم ببیند. این برش یک رفتار قابل‌آزمون است، نه «پروژهٔ کامل هوش مصنوعی».

معیار پذیرش باید از بیرون سیستم قابل‌مشاهده باشد: درخواست ۳۰۱ نویسه رد می‌شود؛ فیلد ناشناخته پذیرفته نمی‌شود؛ status و media type خطا مشخص‌اند؛ رابط در ۳۲۰ پیکسل پیمایش افقی ناخواسته ندارد؛ متن پاسخ به‌عنوان HTML اجرا نمی‌شود. ثبت معیار پیش از کدنویسی مانع آن می‌شود که بعداً آزمون‌ها فقط پیاده‌سازی موجود را توجیه کنند.

## ۴. مرز سامانه و جریان داده

یک نمودار زمینه دست‌کم کاربر، برنامهٔ وب/موبایل، API، backend، منبع داده یا مدل، و سرویس‌های بیرونی را از هم جدا می‌کند. پیکان‌ها را با نوع داده و مالک مشخص کنید: آیا متن خام، شناسه، فایل، embedding یا خروجی مدل جابه‌جا می‌شود؟ کدام بخش آن را اعتبارسنجی می‌کند؟ کدام مرز ممکن است داده را نگه دارد؟ اگر نمی‌دانید، آن را «نامعلوم» بنویسید، نه اینکه در نمودار حذفش کنید.

فصل ۶۶ معماری واقعیِ سرویس بیرونی یا سیاست نگه‌داری را طراحی نمی‌کند. شکل آزمایشگاه فقط درخواست کلاینت، backend و fixture محلی را نشان می‌دهد؛ بنابراین نمودار شاهدی برای امنیت، معماری تولیدی یا کیفیت مدل نیست. کنترل‌های عملیاتی، حریم خصوصی و زنجیرهٔ تأمین در فصل‌های ۶۸ و ۶۹ بررسی می‌شوند.

## ۵. سهم backend، frontend و قرارداد

**Frontend** ورودی را گردآوری، حالت کار را نمایش و دادهٔ پاسخ را برای کاربر قابل‌فهم می‌کند. **Backend** قرارداد را سمت سرویس اعتبارسنجی می‌کند، منطق کاربرد را صدا می‌زند و پاسخ پایدار می‌سازد. رابط کاربری هرگز مرجع نهایی برای مجازبودن ورودی، دسترسی یا تصمیم پرپیامد نیست؛ کاربر می‌تواند نسخهٔ قدیمی کلاینت داشته باشد یا درخواست را بیرون از رابط بسازد.

قرارداد میان این دو است: به کلاینت می‌گوید چه چیزی باید بفرستد و چه چیزی می‌تواند انتظار داشته باشد. این قرارداد اجازه نمی‌دهد backend جزئیات داخلی یا secret را به پاسخ تبدیل کند؛ همچنین UI را از بررسی status code بی‌نیاز نمی‌کند. هر لایه مسئولیت خودش را دارد و هر سه باید با هم آزموده شوند.

## ۶. وب و موبایل مصرف‌کنندگان مستقل‌اند

وب و موبایل ممکن است اندازهٔ صفحه، روش ورودی، اتصال، قابلیت دسترس‌پذیری و چرخهٔ به‌روزرسانی متفاوت داشته باشند؛ اما اگر یک کار واحد انجام می‌دهند، بهتر است معنای قرارداد API مشترک باشد. ساخت دو endpoint با دو نام برای یک عملیات می‌تواند به تفاوت‌های ناخواستهٔ اعتبارسنجی، خطا و حریم داده منجر شود. تفاوت رابط را با منطق presentation حل کنید، نه با تکثیر بی‌دلیل مدل داده.

موبایل می‌تواند مدت بیشتری نسخهٔ قدیمی را نگه دارد و گاه شبکهٔ ناپایدار داشته باشد؛ این واقعیت روی سازگاری قرارداد اثر می‌گذارد، اما پیاده‌سازی صف و بهینه‌سازی آفلاین در این فصل نیست. credential را در کد برنامه hard-code نکنید؛ سازوکار احراز هویت و نگه‌داری امن آن در فصل ۶۸ است. آزمایشگاه ما UI وب را در viewportهای باریک می‌سنجد و ادعای ساخت برنامهٔ native موبایل ندارد.

## ۷. قرارداد را قبل از route روشن کنید

قرارداد را می‌توان به‌صورت چهارتایی درخواست و پاسخ دید: روش و مسیر، سرآیندها، بدنهٔ داده، و نتیجهٔ قابل‌مشاهده. هر جزء باید با دیگری سازگار باشد: مثلاً `POST /v1/assist` یک JSON با `question` می‌گیرد؛ پاسخ موفق `200` شامل `answer` و `sources` است؛ و ورودی ناسازگار status `422` و بدنهٔ خطای ماشین‌خوان دارد. روش، body و status نامرتبط به هم اضافه نکنید.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="درخواست HTTP از روش، مسیر، سرآیند و بدنه ساخته می‌شود؛ پاسخ از وضعیت، سرآیند و بدنه ساخته می‌شود. این یک مدل مفهومی قرارداد است، نه سنجهٔ کیفیت یا تضمین امنیت."><mrow><mi>Request</mi><mo>=</mo><mo>(</mo><mi>Method</mi><mo>,</mo><mi>Path</mi><mo>,</mo><mi>Headers</mi><mo>,</mo><mi>Body</mi><mo>)</mo><mo>;</mo><mspace width="0.5em"/><mi>Response</mi><mo>=</mo><mo>(</mo><mi>Status</mi><mo>,</mo><mi>Headers</mi><mo>,</mo><mi>Body</mi><mo>)</mo></mrow></math>

**متن جایگزین فرمول:** درخواست شامل روش، مسیر، سرآیند و بدنه است؛ پاسخ شامل وضعیت HTTP، سرآیند و بدنه. این نمایش فقط اجزای ارتباط را یادآوری می‌کند.

## ۸. منبع، مجموعه و عملیات را از هم جدا کنید

اگر API از یک مجموعه منبع می‌خواند، مسیر را حول منبع نام‌گذاری کنید: `GET /v1/catalog` فهرست، `GET /v1/catalog/items/guide-001` یک مورد، و `POST /v1/assist` عملیاتی با ورودی و پاسخ مستقل. نام مسیر باید به مصرف‌کننده کمک کند بفهمد چه عملی رخ می‌دهد؛ endpoint را به نام تابع داخلی یا مدل پشت سرویس گره نزنید.

انتخاب REST، RPC یا GraphQL به نیاز دامنه، کلاینت، ابزار و محدودیت‌ها وابسته است. «REST همیشه بهتر است» یا «GraphQL همیشه کارآمدتر است» حکم عمومی نیست. برای پروژهٔ کوچک این فصل، endpointهای HTTP/JSON ساده و قابل‌آزمون‌اند؛ اگر چند تیم مصرف‌کننده، پیچیدگی query یا جریان داده متفاوت دارند، گزینه‌ها را با نیاز واقعی مقایسه کنید.

## ۹. مسیر و نسخه را در سطح قرارداد معنا کنید

مسیر `/v1/` در پروژه نسخهٔ سطح API را نشان می‌دهد، نه نسخهٔ FastAPI، مدل یا build نرم‌افزار. مسیر نسخه‌دار ساده است که دو کلاینت نسخه‌های متفاوت را از هم جدا کنند، اما به‌تنهایی سازگاری یا زمان پشتیبانی را تعیین نمی‌کند. قرارداد باید روشن کند هر نسخه چه فیلد، رفتار و دورهٔ پشتیبانی دارد؛ اجرا و زمان بازنشستگی، موضوع release management است.

تغییر نام یک فیلد، تغییر نوع از string به object، اجباری‌کردن مقدار اختیاری، عوض‌کردن معنی status یا تغییر enum می‌تواند کلاینت قدیمی را بشکند، حتی اگر URL ثابت بماند. تغییر افزایشی نیز همیشه بی‌خطر نیست: مصرف‌کننده‌ای که فیلدهای ناشناخته را رد می‌کند ممکن است با فیلد تازه شکست بخورد. سازگاری را با قرارداد واقعی مشتریان و آزمون مصرف‌کننده بررسی کنید.

## ۱۰. معنای روش HTTP را حفظ کنید

RFC 9110 معنای روش‌ها را تعریف می‌کند. `GET` برای دریافت representation است و نباید تغییر عمدیِ حالت سرور را انجام دهد؛ `PUT` و `DELETE` از دید معنای HTTP idempotent هستند، یعنی تکرار همان درخواست باید همان اثر موردنظر را داشته باشد؛ `POST` برای پردازش یا ایجاد منبع به‌کار می‌رود و صرفاً به‌خاطر نامش idempotent نیست. پیاده‌سازی باید این واژه‌ها را با رفتار واقعی هماهنگ کند.

این تفاوت بر طراحی کلاینت اثر دارد: اگر پاسخ POST گم شد، کلاینت نمی‌داند درخواست انجام شده یا نه و تکرار کورکورانه ممکن است کار را دوباره انجام دهد. سازوکار deduplication یا retry را باید با دامنه، ذخیره‌سازی و تهدیدها طراحی کرد؛ این فصل فقط قرارداد را مشخص می‌کند و پیاده‌سازی صف/تکرار را به فصل ۶۷ و کنترل سوءاستفاده را به فصل ۶۸ واگذار می‌کند.

## ۱۱. status code بخشی از پاسخ است

status code را به پیام رابط یا JSON پنهان نکنید؛ کتابخانه‌ها و کلاینت‌های HTTP از آن برای فهم نتیجه استفاده می‌کنند. الگوی رایج: `200` برای پاسخ موفق، `201` برای ایجاد موفق، `202` برای پذیرش پردازش ناتمام، `204` برای موفقیت بدون body، `400` برای درخواست بدساخت، `404` برای منبع پیدا نشد، `409` برای تعارض وضعیت، `413` برای محتوای بیش‌ازحد، `415` برای media type پشتیبانی‌نشده، `422` برای محتوای قابل‌خواندن اما ناسازگار با قرارداد، و `5xx` برای شکست سمت سرویس.

برای `401` و `403`، معنای HTTP را با ورود و مجوز واقعی پیاده کنید؛ جزئیات کنترل در فصل ۶۸ می‌آید. `429` نیز به سیاست محدودیت نرخ وابسته است و در فصل ۶۸ بررسی می‌شود؛ این فصل فقط آن را به‌عنوان status قابل‌مشاهده می‌شناسد. `202` را برای درخواست synchronous که همین حالا تمام شده استفاده نکنید، و `200` را به پاسخ خطایی تبدیل نکنید که کلاینت باید حدس بزند.

## ۱۲. media type و JSON باید روشن باشند

درخواست و پاسخ باید نوع رسانه را نشان دهند. برای JSON، معمولاً `Content-Type: application/json` در درخواست و پاسخ می‌آید؛ درخواست با `Accept` می‌تواند نوع پاسخ مطلوب را مشخص کند. پاسخ Problem Details از `application/problem+json` استفاده می‌کند. صرف اینکه بدنه شبیه JSON است، قرارداد media type را جایگزین نمی‌کند؛ و parser کلاینت نباید هر پاسخ را بدون بررسی به JSON تبدیل کند.

ساختار را یک‌بار برای همان عملیات تعریف کنید. برای نمونه، پاسخ `POST /v1/assist` دارای `contract_version`, `request_id`, `status`, `answer` و `sources` است. اگر نسخهٔ ساختار یا language tag اهمیت دارد، آن را در فیلد یا media type مستند کنید؛ از اضافه‌کردن چند envelope تو در تو که هیچ مصرف‌کننده‌ای به آن نیاز ندارد خودداری کنید.

## ۱۳. null، نبودن فیلد و مقدار خالی یکی نیستند

این سه وضعیت را از هم جدا کنید: فیلد اصلاً ارسال نشده، فیلد با مقدار `null` ارسال شده، یا رشتهٔ خالی فرستاده شده. در JSON این‌ها معنای متفاوت دارند؛ در Pydantic هم «اختیاری‌بودن» به‌تنهایی الزاماً به معنی پذیرفتن `null` نیست. برای هر فیلد بنویسید اجباری است یا نه، `null` مجاز است یا نه، مقدار پیش‌فرض چیست، و حذف فیلد در پاسخ چه معنایی دارد.

مقدار پیش‌فرض را به‌عنوان رفتار پنهان API اضافه نکنید. اگر locale پیش‌فرض فارسی است، قرارداد و OpenAPI باید آن را نشان دهند؛ اگر backend به نبودن `locale` و `locale: null` پاسخ یکسان نمی‌دهد، آزمون بنویسید. تغییر از فیلد optional به required در یک نسخهٔ زنده می‌تواند client قدیمی را بشکند.

## ۱۴. ورودی را نزدیک مرز و با schema اعتبارسنجی کنید

اعتبارسنجی سمت کلاینت تجربهٔ بهتر می‌دهد، ولی کنترل اصلی سمت سرور است؛ درخواست مستقیم می‌تواند UI را دور بزند. schema را با type، طول، enum، محدودهٔ عددی و فیلدهای مجاز تعریف کنید. در آزمایشگاه `question` رشته‌ای با طول ۱ تا ۳۰۰ نویسه و `locale` برابر `fa` یا `en` است؛ فیلد اضافه رد می‌شود. «اعتبارسنجی شد» را به تعداد فیلدهای بررسی‌شده یا سناریوی آزموده‌شده محدود کنید.

FastAPI از type annotation و Pydantic برای تبدیل و اعتبارسنجی داده استفاده می‌کند. مدل ورودی DTO مرز شبکه است، نه الزاماً مدل پایگاه داده یا کلاس دامنه. در صورت نیاز، normalization را آشکار بنویسید: trim فاصلهٔ ابتدا/انتها، canonicalize کد زبان یا اعتبارسنجی شناسه. هر normalization می‌تواند ورودی‌های متفاوت را یکی کند؛ آن را پنهانی انجام ندهید.

## ۱۵. پاسخ را به مدل خروجی محدود کنید

API نباید هر داده‌ای را که backend یا مدل برگردانده بدون پالایش به کلاینت بفرستد. مدل خروجی، فیلدهای قابل‌مشاهده را صریح می‌کند؛ دادهٔ داخلی، prompt، stack trace، metadata محرمانه یا شناسهٔ منبع غیرمجاز نباید صرفاً به‌دلیل حضور در شیء پایتون بیرون برود. DTO پاسخ را از ساختار داخلی جدا کنید و آزمون کنید که فیلدهای خصوصی در JSON وجود ندارند.

در پروژه، رکورد fixture هم `answer_fa` و هم `answer_en` دارد، ولی endpoint کاتالوگ فقط `id`, `title`, `url` را برمی‌گرداند. این یک مرز پاسخ است و آزمون دقیقاً نبودن دو فیلد پاسخ را بررسی می‌کند. از آن نمی‌توان نتیجه گرفت که دادهٔ واقعی امن یا کمینه شده است؛ برای همان ادعا به schema، منبع داده و سیاست دسترسیِ محیط واقعی نیاز است.

## ۱۶. خطا را برای ماشین و انسان قابل‌فهم کنید

RFC 9457 قالب استاندارد Problem Details را برای جزئیات ماشین‌خوانِ خطای HTTP تعریف می‌کند. `type` نوع خطا را مشخص می‌کند؛ `title` خلاصهٔ پایدارتر است؛ `detail` شرح همین رخداد است؛ `instance` و extension memberها اختیاری‌اند. status واقعی HTTP مرجع معناست؛ اگر body فیلد `status` دارد، آن را با پاسخ واقعی هماهنگ کنید. در کلاینت بر اساس `type` یا کد پایدار تصمیم بگیرید، نه متن محلی‌سازی‌شدهٔ `title` و `detail`.

خطا باید اطلاعات کافی برای اقدام مصرف‌کننده بدهد و در عین حال ورودی ردشده یا جزئیات داخلی را فاش نکند. در نمونه، بدنه با `application/problem+json` بازمی‌گردد و رشتهٔ ورودی نامعتبر را echo نمی‌کند. UI خطای فنی را عیناً نمایش نمی‌دهد و پیام عمومی می‌دهد. برای زبان‌ها و مسیرهای پشتیبانیِ واقعی، قرارداد و privacy را جداگانه بازبینی کنید.

## ۱۷. فهرست، صفحه‌بندی و ترتیب را قرارداد کنید

اگر endpoint فهرست بزرگ می‌شود، `limit`, `cursor`, فیلتر و ترتیب باید معنی دقیق داشته باشند. `limit=0` یا مقدار منفی را چگونه پاسخ می‌دهید؟ آیا ترتیب پایدار است؟ اگر موردی در میانهٔ پیمایش افزوده شود، کلاینت چه می‌بیند؟ cursor را به جای offset، شناسهٔ داخلی یا state حساس افشا نکنید مگر طراحی آگاهانه باشد. این‌ها بخش قراردادند، حتی اگر پیاده‌سازی کارایی به فصل ۶۷ تعلق داشته باشد.

در نمونه فقط یک رکورد ساختگی وجود دارد و `next_cursor` همیشه `null` است؛ `limit` در بازهٔ ۱ تا ۱۰ اعتبارسنجی می‌شود. این آزمایش ادعای پشتیبانی از pagination در مقیاس ندارد. اگر پروژهٔ واقعی چند هزار منبع دارد، شکل pagination و رفتار تغییر هم‌زمان را با مشتریان واقعی و دادهٔ آزمون جدا بسنجید.

## ۱۸. OpenAPI: توصیف ماشین‌خوان، نه جایگزین توافق

OpenAPI Specification یک توصیف زبان‌مستقل از رابط HTTP است که انسان و ابزار می‌توانند از آن برای کشف عملیات، ورودی، پاسخ و schema استفاده کنند. در تاریخ بازبینی این فصل، نسخهٔ منتشرشدهٔ جاری OAS 3.2.1 است. نسخهٔ generator باید با ابزارهای تولید client، validator و سرور شما آزموده شود؛ عوض‌کردن فیلد `openapi` به‌تنهایی پشتیبانی از قابلیت‌های نسخهٔ جدید را ایجاد نمی‌کند.

نسخهٔ فعلی FastAPI در این محیط سند OpenAPI 3.1.0 تولید می‌کند و آزمایشگاه نیز همین خروجی واقعی را assert می‌کند. این تصمیم نمونه‌ای است از تفاوت «آخرین نسخهٔ مشخصه» و «نسخه‌ای که toolchain شما واقعاً تولید و مصرف می‌کند». schema را در CI بررسی کنید، ولی قرارداد محصول باید تصمیم‌های مهمی مثل سازگاری، دادهٔ مجاز، error semantics و پشتیبانی را نیز مستند کند.

## ۱۹. FastAPI route را به مدل ورودی و خروجی وصل کنید

FastAPI decoratorهایی مانند `@app.get` و `@app.post` را به تابع route وصل می‌کند. annotation برای query/path/body و مدل‌های Pydantic به framework کمک می‌کند درخواست را parse و validate کند و سند OpenAPI بسازد. route باید کوتاه بماند: ورودی را بگیرد، use-case را فراخوانی کند و نتیجه یا خطای قراردادی را بازگرداند. قرار دادن کل منطق محصول، SQL، prompt و فراخوانی provider در یک تابع بزرگ نگه‌داری و آزمون را سخت می‌کند.

در پروژه `POST /v1/assist` ورودی `AssistRequest`، پاسخ `AssistResponse` و خطای `Problem` دارد. `operation_id` پایدار برای ابزار تولید client کمک می‌کند؛ تغییر آن نیز می‌تواند خروجی SDK را عوض کند. برای محصول واقعی مسیر، اسم عملیات، نام schema و رفتار را با مصرف‌کنندگان بررسی کنید؛ نام‌گذاری تصادفیِ generator را بی‌بازبینی منتشر نکنید.

## ۲۰. dependency injection را برای وابستگی‌های قابل‌تعویض به‌کار ببرید

FastAPI وابستگی‌های قابل تزریق دارد؛ برای نمونه، تنظیمات، repository، سرویس دامنه یا هویت درخواست از dependency بیاید تا در آزمون بتوان جایگزین ساختگی تزریق کرد. این الگو از سراسری‌بودن state و اتصال سخت route به پایگاه داده یا provider جلوگیری می‌کند. استفاده از dependency فقط برای پنهان‌کردن فراخوانی عادی یا ساخت زنجیره‌ای غیرقابل‌فهم ارزش ندارد.

در fixture lab، داده از فایل محلی خوانده می‌شود تا رفتار deterministic بماند. در پروژهٔ واقعی، dependency graph باید محدود و قابل‌ردیابی باشد؛ dependency injection امنیت دسترسی را خودکار حل نمی‌کند، و fake provider نیز صحت provider واقعی را ثابت نمی‌کند. قراردادهای فصل ۶۸ برای هویت و مجوز و فصل ۶۹ برای configuration/deployment لازم‌اند.

## ۲۱. لایه‌ها را در حد نیاز جدا کنید

یک جداسازی ساده می‌تواند این باشد: route/adapter شبکه؛ schema ورودی و خروجی؛ use-case یا سرویس دامنه؛ adapter برای داده، مدل یا سرویس بیرونی؛ و لایهٔ ذخیره‌سازی. این تقسیم‌بندی مرز تغییر را روشن می‌کند: FastAPI یک انتخاب transport است، ولی منطق «ساخت پاسخ نمایشی از fixture» می‌تواند بدون framework هم آزموده شود. معماری را متناسب با اندازهٔ محصول انتخاب کنید؛ برای یک نمونهٔ کوچک، ده‌ها abstraction فقط هزینه می‌سازند.

هر adapter بیرونی زمان، خطا، مجوز، retry و version خاص خود را دارد. آن‌ها را در قرارداد محصول پنهان نکنید؛ خطای upstream ممکن است به status متفاوت و پیام امن نیاز داشته باشد. ما در این نمونه از adapter بیرونی استفاده نمی‌کنیم، بنابراین موفقیت fixture فقط شاهد همان کد محلی است.

## ۲۲. کلاینت وب: پاسخ HTTP را درست مصرف کنید

`fetch()` یک Promise برمی‌گرداند؛ پاسخ `404` یا `422` لزوماً Promise را reject نمی‌کند. کلاینت باید `response.ok` یا `status` را بررسی کند، media type و schema را در محدودهٔ نیاز parse کند، و خطای شبکه را از پاسخ خطای سرور جدا کند. سپس فقط فیلدهای قراردادی را به view model تبدیل کند؛ نه اینکه همهٔ JSON را بی‌بررسی در DOM جا دهد.

اگر body خالی، HTML یا JSON ناسازگار آمد، رابط نباید crash کند. پیام کاربر را از `detail` خام نسازید و دادهٔ سرور را با `innerHTML` وارد صفحه نکنید. در نمونهٔ `demo.html` از `textContent` استفاده شده؛ آزمون مرورگر پاسخ دارای `<script>` را متن عادی می‌بیند و هیچ عنصر اجرایی جدیدی نمی‌سازد. این آزمون محدود، ممیزی امنیتی کامل نیست.

## ۲۳. کلاینت موبایل: قرارداد مشترک، تجربهٔ متناسب

برنامهٔ موبایل همان schema را consume می‌کند، ولی باید فضای کم، صفحه‌کلید مجازی، چرخش صفحه، اتصال ناپایدار و به‌روزرسانی دیرهنگام را در طراحی رابط در نظر بگیرد. تاریخ، زبان، حالت خالی و خطای شبکه نباید فقط برای صفحهٔ دسکتاپ تعریف شوند. شناسه و مقدار enum را به نمایش انسانیِ محلی‌شده تبدیل کنید؛ متن فارسی را با شکستن دستی فاصله‌ها برای یک صفحهٔ خاص قالب ندهید.

کلید سرویس یا secret را در bundle کلاینت قرار ندهید؛ هر چیزی که به دستگاه کاربر می‌رسد قابل استخراج است. احراز هویت، secure storage، محدودیت نرخ و مدیریت رخداد در فصل ۶۸ است. این بخش فقط می‌گوید قرارداد را برای پلتفرم‌های مصرف‌کننده طراحی کنید؛ پروژهٔ پیوست برنامهٔ native یا Android/iOS را نمی‌سازد.

## ۲۴. حالت UI را آشکار و کامل مدل کنید

یک فرم واقعی دست‌کم این حالت‌ها را دارد: آمادهٔ ورود، در حال ارسال، پاسخ موفق، نتیجهٔ خالی، خطای اعتبارسنجی، خطای سرویس و خطای شبکه. اگر فقط «موفق/ناموفق» دارید، کاربر نمی‌فهمد چه باید بکند؛ و اگر دو درخواست پشت‌سرهم اجرا شوند، پاسخ قدیمی ممکن است وضعیت تازه را بازنویسی کند. در این فصل concurrency یا cancellation را پیاده‌سازی نمی‌کنیم، اما حالت و آزمونش را از قبل در نظر می‌گیریم.

در هنگام ارسال، وضعیت را به فناوری کمکی اعلام کنید و دکمه را موقتاً غیرفعال کنید؛ در پایان، آن را دوباره فعال کنید. در خطا دادهٔ موفقیت قبلی را به‌اشتباه تازه نشان ندهید. پاسخ خالی باید حالت خالی باشد، نه صفحهٔ سفید. هر transition از یک رویداد قابل‌آزمون بیاید، نه از رنگ یا انیمیشن به‌تنهایی.

## ۲۵. دسترس‌پذیری جزئی از قرارداد تجربه است

هر ورودی برچسب مرتبط و قابل‌فوکوس صفحه‌کلید داشته باشد؛ خطا را به فیلد مربوط وصل کنید؛ تغییر وضعیت را با `role="status"` یا الگوی مناسب به فناوری کمکی اعلام کنید؛ ترتیب headingها منطقی باشد؛ و focus پس از خطا یا dialog گم نشود. رنگ تنها راه تمایز موفقیت و خطا نباشد. در صفحهٔ کوچک، هدف لمسی، بزرگ‌نمایی و پنهان‌نشدن focus را بررسی کنید.

WCAG 2.2 معیارهای آزمون‌پذیر و فناوری‌مستقل دارد، اما چند assertion در Playwright مساوی conformance نیست. پروژه برچسب، اعلان وضعیت و overflow در سه viewport را بررسی می‌کند؛ آزمون screen reader، کنتراست کامل، کاربر واقعی یا ممیزی رسمی انجام نمی‌دهد. دامنهٔ آزمون و محدودیت آن را همین‌قدر دقیق گزارش کنید.

## ۲۶. فارسی، راست‌به‌چپ و دادهٔ محلی‌شده

جهت سند را با `dir="rtl"` و زبان را با `lang="fa"` مشخص کنید؛ برای شناسه، URL، کد، تاریخ و متن انگلیسی از جداسازی جهت‌دار مناسب استفاده کنید، نه فاصله یا شکست دستی. از «ترجمه‌کردن» مقدار قراردادی مانند `status` یا `id` در JSON بپرهیزید؛ مقدار ماشین‌خوان پایدار است و UI آن را به برچسب فارسی نمایش می‌دهد. رقم‌های محلی در رابط با شناسهٔ قابل‌ارسال یکسان نیستند مگر قرارداد این را صریح کند.

تاریخ باید منطقهٔ زمانی و قالب مشخص داشته باشد، اگر برای تصمیم کاربردی است؛ timestamp را بدون معنای UTC یا offset به کلاینت نسپارید. در پروژه اصلاً زمان واقعی یا PII نداریم. حروف فارسی، نیم‌فاصله، Unicode normalization و نام‌های راست‌به‌چپ را در fixtureها و آزمون‌ها به‌عنوان دادهٔ متنی واقعی بگذارید؛ فونت محلی فقط ظاهر را عوض می‌کند و وجود نویسه را تعیین نمی‌کند.

## ۲۷. CORS را با مجوز اشتباه نگیرید

مرورگر برای درخواست cross-origin سیاست CORS را اعمال می‌کند تا origin وب‌سایت به پاسخ دسترسی داشته باشد. CORS یک سازوکار authorization سمت backend نیست و درخواست‌های غیرمرورگری را متوقف نمی‌کند. در محصول واقعی originهای لازم، روش‌ها و headerها را محدود و با flowهای احراز هویت هماهنگ کنید؛ فعال‌کردن wildcard به‌عنوان راه‌حل همیشگی را از روی نمونه‌کد کپی نکنید.

پروژهٔ آزمایشگاهی از همان origin سرو می‌شود و اصلاً middleware CORS ندارد. به همین دلیل آزمون آن شاهد درست‌بودن CORS در deployment نیست. تصمیم دربارهٔ credential، cross-origin، CSRF و policy امنیتی در فصل ۶۸ بررسی می‌شود؛ مسئلهٔ deployment و proxy در فصل ۶۹ است.

## ۲۸. قرارداد داده و کمینه‌سازی

هر فیلد ورودی را از دید کاربرد توجیه کنید: آیا برای کار لازم است؟ کجا پردازش می‌شود؟ آیا در پاسخ برمی‌گردد؟ آیا ذخیره می‌شود؟ اگر endpoint فقط پرسش کوتاه می‌خواهد، افزودن نام، ایمیل، محل زندگی یا تاریخچهٔ کامل گفتگو را «شاید لازم شود» توجیه نکنید. schema کوچک‌تر هم سطح خطا و هم مسئولیت داده را کاهش می‌دهد؛ حذف فیلد بی‌مصرف از قرارداد اغلب از توضیح اضافه‌اش بهتر است.

حذف یک فیلد از response نیز ممکن است سازگاری client را بشکند، پس کاهش داده را با نسخه و آزمون مدیریت کنید. آزمون fixture در این پروژه هیچ اطلاعات شخصی ندارد؛ این به معنی privacy-preserving بودن API واقعی نیست. مبانی حریم خصوصی و نگه‌داری داده در فصل ۶۸ و ارزیابی اثر/مسئولیت در فصل ۶۵ می‌ماند.

## ۲۹. آزمون قرارداد و schema

آزمون قرارداد باید ورودی معتبر، مرز طول، فیلد ناشناخته، مقدار enum نامعتبر، status، media type و شکل خروجی را بسنجد. سند OpenAPI را از اجرای واقعی API بگیرید و بررسی کنید که محدودیت `maxLength`, `additionalProperties` و error response در آن وجود دارد. در آزمون regression، تغییر ناخواستهٔ schema باید شکست روشن بدهد؛ مقایسهٔ کل JSON خام ممکن است ترتیب یا metadata بی‌اهمیت را ناپایدار کند، پس assertionهای معنایی بسازید.

`test_api.py` سند `/openapi.json` را می‌خواند و `POST /v1/assist` را با status و `application/problem+json` می‌سنجد. این رفتار درون‌فرایندی است، نه آزمون proxy، TLS، DNS، packet، latency یا سرو واقعی. «قرارداد سازگار است» را به نسخهٔ schema، مصرف‌کننده و سناریوی مشخص نسبت دهید.

## ۳۰. آزمون route و منطق دامنه

آزمون کوچک باید علت شکست را روشن کند: مدل ورودی حد ۳۰۰ را enforce می‌کند؛ route برای whitespace-only خطای دامنه می‌دهد؛ فهرست کاتالوگ فقط دادهٔ عمومی را می‌فرستد؛ و locale انگلیسی همان ساختار خروجی را نگه می‌دارد. آزمون واحد use-case را می‌توان جدا از FastAPI نوشت، اما برای نمونهٔ کوچک TestClient راه مستقیمی است برای آزمودن قرارداد HTTP در ASGI.

TestClient در این پروژه به برنامهٔ FastAPI وصل است و با `httpx2` کار می‌کند؛ درخواست به شبکهٔ بیرونی نمی‌رود. fixture hash و تعداد آزمون در `results.json` ثبت می‌شوند. اگر آزمون به provider یا مدل زنده وصل شود، نتیجه به نسخه، دسترسی، هزینه و تغییر سرویس وابسته می‌شود؛ برای آزمون قرارداد از fakeِ صریح و دادهٔ ثابت استفاده کنید.

## ۳۱. آزمون رابط با پاسخ کنترل‌شده

آزمون frontend باید stateهای قابل‌مشاهده را بسنجد: برچسب فرم، اعلان بارگذاری، غیرفعال‌شدن موقت دکمه، نمایش پاسخ، خطای عمومی، و بازگشت دکمه به حالت فعال. پاسخ را با route interception کنترل کنید تا آزمون تصادفی به اینترنت یا مدل وابسته نباشد. برای آزمون success، fixture پاسخ را بدهید؛ برای خطا، Problem Details دارای یک sentinel خصوصی بسازید و assert کنید رابط آن را نشان نمی‌دهد.

در `test_frontend.py` همین دو مسیر در viewportهای ۳۲۰، ۳۹۰ و ۷۶۸ پیکسل آزموده می‌شوند؛ یکی از متن‌ها عمداً `<script>` دارد تا نشان دهد UI آن را به‌صورت متن درج می‌کند. این آزمون ثابت نمی‌کند همهٔ مرورگرها، زبان‌ها یا screen readerها رفتار یکسان دارند. آزمون رابط باید علاوه بر کلاس CSS، آنچه کاربر با role/label می‌بیند را assert کند.

## ۳۲. آزمون یکپارچه و end-to-end را مرزبندی کنید

آزمون واحد یک تابع یا schema کوچک را می‌سنجد؛ آزمون API با TestClient چند route و middleware درون فرایند را می‌سنجد؛ آزمون integration دو adapter یا datastore واقعی را به هم وصل می‌کند؛ و end-to-end از رابط واقعی تا سرویس و وابستگی‌های واقعی می‌رود. هرچه آزمون بزرگ‌تر است، failureهای بیشتری را پوشش می‌دهد اما تشخیص علت و بازتولید دقیق سخت‌تر می‌شود. suite کم‌هزینه را زیاد و چند آزمون end-to-end هدفمند را جدا نگه دارید.

پروژهٔ این فصل E2E با API زنده یا مدل را اجرا نمی‌کند؛ آزمون مرورگر شبکهٔ API را intercept می‌کند و TestClient سرویس را جدا می‌سنجد. بنابراین نتیجهٔ دو suite را «کل مسیر در production تأیید شد» ننامید. اگر در آینده backend و frontend کنار هم اجرا شوند، آن مسیر را با environment و fixture همان deployment و بدون دسترسی به دادهٔ واقعی به‌طور مجزا بیازمایید.

## ۳۳. Fixture، محیط و نتیجهٔ قابل‌بازتولید

Fixture باید شناسه، منشأ، نسخه، نوع داده، hash و محدودیت داشته باشد. آن را با دادهٔ ساختگی بسازید، نه از یک کاربر واقعی یا خروجی زندهٔ یک provider. محیط را شامل نسخهٔ Python، FastAPI، Starlette، Pydantic، TestClient، مرورگر و دستور اجرا ثبت کنید؛ اگر نتیجه از همان fixture hash متفاوت است، مقایسه دیگر بازتولید همان اجرا نیست.

پروژهٔ پیوست `synthetic_fixture.json` را با SHA-256 در `fixture_manifest.json` پیوند می‌دهد و `audit.py` هر دو suite را دوباره اجرا می‌کند. `results.json` فقط ۱۲ آزمون API و ۲ آزمون browser در environment ثبت‌شده را گزارش می‌کند. آن عدد نه اندازهٔ کیفیت محصول است و نه نرخ خطای آماری؛ تنها نتیجهٔ اجرای همین آزمون‌هاست.

## ۳۴. سازگاری قرارداد و تغییر تدریجی

مصرف‌کننده را از ابتدا شریک قرارداد بدانید. برای هر تغییر سؤال کنید: آیا ورودی اجباری تازه شده؟ آیا خروجی حذف یا تغییرنوع یافته؟ آیا enum جدید برای client قدیمی قابل‌تحمل است؟ آیا status/error type عوض شده؟ آیا SDK تولیدشده تغییر ناخواسته دارد؟ تغییر شکستن‌ناپذیر را نیز با کلاینتی که فیلد ناشناخته را نمی‌پذیرد بررسی کنید؛ قانون سازگاری فقط به نظریهٔ schema وابسته نیست.

در rollout محصول، روش اعلام، پشتیبانی هم‌زمان، انتقال مشتری و توقف نسخه مهم‌اند؛ آن برنامه در فصل ۶۹ است. اینجا صرفاً قرارداد را از لحاظ معنایی نسخه‌گذاری و با آزمون backward compatibility می‌سنجیم. مهاجرت schema را بدون فهرست مصرف‌کننده و شواهد استفاده واقعی، «سازگار» اعلام نکنید.

## ۳۵. خطا، timeout و تجربهٔ بازیابی

کلاینت باید تفاوت پاسخ خطای HTTP، قطع اتصال، timeout و پاسخ خراب را بداند. یک timeout به‌تنهایی نمی‌گوید سرور کار را انجام نداده؛ برای عملیات نوشتنی retry کور می‌تواند عارضه داشته باشد. متن کاربر باید بگوید چه کاری می‌تواند انجام دهد، اما تکرار را تنها وقتی پیشنهاد دهید که semantics و قرارداد درخواست اجازه دهد. retry policy، صف و circuit breaker موضوع runtime/امنیت عملیاتی‌اند و در این فصل پیاده‌سازی نمی‌شوند.

برای پاسخ مدلِ در حال تولید، streaming یا job asynchronous قرارداد متفاوت می‌خواهد: status `202`، شناسهٔ job، مسیر پیگیری یا channel جریان باید صریح باشد. از `202` به‌عنوان «پاسخ موفقِ معمولی» استفاده نکنید. چون فصل ۶۷ دربارهٔ serving و جریان اجراست، پروژهٔ این فصل synchronous، کوتاه و fixture-backed می‌ماند.

## ۳۶. خطاهای طراحی و بازبینی پیش از تحویل

چند خطای رایج را با چک‌لیست کوتاه پیدا کنید: استفاده از `200` برای همهٔ اتفاق‌ها؛ بدنهٔ خطای مخصوص هر route؛ واژه‌های ثابت در انگلیسی به‌جای type پایدار؛ درخواست بدون محدودیت طول؛ خروجی‌ای که فیلد داخلی را هم می‌فرستد؛ UI که status را نمی‌خواند؛ client که متن خطای سرور را بدون پالایش نمایش می‌دهد؛ CORS باز برای رفع سریع مشکل؛ و schemaای که فقط از روی کد route حدس زده شده است.

پیش از تحویل فصل، endpoint، method، request schema، response schema، خطاها و OpenAPI را روبه‌روی هم بگذارید. سپس fixture را با hash وارسی کنید، suite API و UI را اجرا کنید، محدودیت آزمون را ثبت کنید و پیوند فصل/پاسخ‌نامه/پروژه/گزارش را کنترل کنید. این چک‌لیست release pipeline یا تأیید امنیتی نیست؛ مرزهای آن در فصل‌های ۶۷ تا ۶۹ حفظ می‌شود.

## ۳۷. منابع و تاریخ بازبینی

منابع زیر در ۷ نوامبر ۲۰۲۶ بازبینی شدند. نسخهٔ FastAPI در محیط مثال `0.162.2` و نسخه‌های وابستگی مستقیم در `book-engineering/projects/66-ai-product-api/requirements.txt` ثبت شده‌اند؛ نسخهٔ واقعی نصب‌شده را هنگام بازتولید با `environment.json` تطبیق دهید.

- [۱] FastAPI، [First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)، [Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)، [Testing](https://fastapi.tiangolo.com/tutorial/testing/) و [Release Notes](https://fastapi.tiangolo.com/release-notes/). راهنمای چارچوب، نه استاندارد HTTP.
- [۲] OpenAPI Initiative، [OpenAPI Specification 3.2.1](https://spec.openapis.org/oas/v3.2.1.html)، منتشرشده در ۱۰ سپتامبر ۲۰۲۶. پروژه عمداً خروجی تولیدشدهٔ 3.1.0 را assert می‌کند.
- [۳] IETF، [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)، ژوئن ۲۰۲۲.
- [۴] IETF، [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457)، ژوئیهٔ ۲۰۲۳؛ جایگزین RFC 7807.
- [۵] Pydantic، [Models](https://docs.pydantic.dev/latest/concepts/models/) و [Fields](https://docs.pydantic.dev/latest/concepts/fields/)، برای مدل‌سازی و اعتبارسنجی داده در نسخهٔ نصب‌شده.
- [۶] W3C، [Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)، Recommendation مورخ ۱۲ دسامبر ۲۰۲۴.
- [۷] WHATWG، [Fetch Standard](https://fetch.spec.whatwg.org/)، معنای درخواست/پاسخ Fetch در مرورگر.
- [۸] JSON Schema، [Draft 2020-12](https://json-schema.org/draft/2020-12)، برای مفاهیم schema و validation؛ OpenAPI و ابزارهای آن dialectهای موردپشتیبانی خود را نیز دارند.

خلاصهٔ این فصل جای متن استاندارد، راهنمای جاری کتابخانه، ارزیابی حقوقی، آزمون با کاربر واقعی یا بررسی دسترس‌پذیری متخصص را نمی‌گیرد. در صورت تغییر نسخهٔ toolchain، OpenAPI یا استانداردها، منابع و نتایج را دوباره بررسی کنید.

## ۳۸. تمرین‌ها

۱. قرارداد `POST /v1/assist` برای پرسشی با طول ۳۰۱ نویسه چه status و media type خطایی می‌دهد، و کدام آزمون آن را تأیید می‌کند؟
۲. تفاوت نبودن `locale`، مقدار `null` و رشتهٔ خالی چیست؟ برای هر وضعیت، رفتار موردانتظار را در schema و آزمون بنویسید.
۳. چرا `GET /v1/catalog` نباید تغییری در state سرور ایجاد کند، و این قاعده چه اثری بر retry کلاینت دارد؟
۴. در OpenAPI خروجی پروژه، `question` چه محدودیت طولی دارد و فیلدهای ناشناخته چگونه رفتار می‌کنند؟
۵. پاسخ fixture دارای `<script>` را رابط چگونه نمایش می‌دهد، و آزمون browser چه چیزی را ثابت نمی‌کند؟
۶. چرا status `202` برای endpoint synchronous این آزمایشگاه نامناسب است؟ یک قرارداد مناسب برای job asynchronous چه شناسه یا مسیر تازه‌ای می‌خواهد؟
۷. کدام بخش‌های احراز هویت، محدودیت نرخ، ثبت رخداد و استقرار عمداً از پیوست حذف شده‌اند، و در کدام فصل ادامه می‌یابند؟
۸. نتایج ۱۲ آزمون API و ۲ آزمون مرورگر تا چه اندازه به ادعای کیفیت یک مدل واقعی اجازه می‌دهند؟ دو محدودیت آزمون را ذکر کنید.

## ۳۹. جمع‌بندی

قرارداد API یک توافق صریح دربارهٔ ورودی، خروجی، status، media type، schema و نسخه است. FastAPI و Pydantic ابزار پیاده‌سازی‌اند؛ OpenAPI توصیف ماشین‌خوان می‌سازد؛ و تست API و رابط باید با هم اما در دامنهٔ درست اجرا شوند. frontend وب و موبایل مصرف‌کنندگان مستقل همان قراردادند، نه مرجع امنیت یا حقیقت مدل.

پروژهٔ همراه با fixture ساختگی، ۱۲ آزمون API و ۲ آزمون مرورگر در سه viewport اجرا می‌شود؛ خروجی فقط دربارهٔ همان قرارداد و همان fixture است. **پاسخ‌نامهٔ مستقل** در [فایل پاسخ‌ها](../answers/66-ai-product-api-fa.md)، **پروژهٔ فصل** در [آزمایشگاه API](../projects/66-ai-product-api/README.md)، و **گزارش ممیزی** در [گزارش فصل ۶۶](66-audit-report-fa.md) است. برای مرور دامنهٔ قبلی به [فصل ۶۵](65-alignment-governance.md) بازگردید؛ ادامهٔ runtime، امنیت محصول و استقرار به‌ترتیب در فصل‌های ۶۷، ۶۸ و ۶۹ است.

## ۴۰. پیوست اجرایی — سرویس FastAPI و قرارداد

فایل کاملِ آزموده‌شدهٔ `app.py` در زیر آمده است؛ نسخهٔ اجرایی و fixture، آزمون‌ها، محیط و نتیجه در [پوشهٔ پروژه](../projects/66-ai-product-api/README.md) هستند.

```python
"""Synthetic FastAPI contract demo for Volume 5, Chapter 5 / global Chapter 66."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parent
FIXTURE = json.loads((ROOT / "synthetic_fixture.json").read_text(encoding="utf-8"))
RECORDS = {record["id"]: record for record in FIXTURE["records"]}


class Problem(BaseModel):
    """Small RFC 9457-style error representation for this teaching API."""

    type: str
    title: str
    status: int
    detail: str


class CatalogItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9-]+$", description="Stable identifier for this synthetic source.")
    title: str = Field(min_length=1, max_length=120)
    url: str = Field(description="Reserved example.invalid URL; it is not a live source.")


class CatalogResponse(BaseModel):
    contract_version: Literal["1.0"] = "1.0"
    items: list[CatalogItem]
    next_cursor: str | None = None


class AssistRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=300, description="Synthetic demo input; do not send personal data.")
    locale: Literal["fa", "en"] = "fa"


class SourceRef(BaseModel):
    id: str
    title: str


class AssistResponse(BaseModel):
    contract_version: Literal["1.0"] = "1.0"
    request_id: str
    status: Literal["completed"]
    answer: str
    sources: list[SourceRef]


PROBLEM_SCHEMA = Problem.model_json_schema()
PROBLEM_404 = {
    "description": "The requested synthetic catalog item does not exist.",
    "content": {"application/problem+json": {"schema": PROBLEM_SCHEMA}},
}
PROBLEM_422 = {
    "description": "The request does not satisfy the published input contract.",
    "content": {"application/problem+json": {"schema": PROBLEM_SCHEMA}},
}

app = FastAPI(
    title="CampusGuide synthetic product API",
    description="A deterministic, fixture-backed teaching example; it does not call an AI model.",
    version="1.0.0",
)


def problem_response(status: int, title: str, detail: str, slug: str) -> JSONResponse:
    body = {
        "type": f"https://example.invalid/problems/{slug}",
        "title": title,
        "status": status,
        "detail": detail,
    }
    return JSONResponse(status_code=status, content=body, media_type="application/problem+json")


@app.exception_handler(RequestValidationError)
async def request_validation_problem(_request: Request, _exc: RequestValidationError) -> JSONResponse:
    # The response intentionally does not echo rejected values or internal validator details.
    return problem_response(
        422,
        "درخواست با قرارداد سازگار نیست",
        "ساختار یا مقدار یکی از فیلدهای ورودی پذیرفته نشد.",
        "invalid-request",
    )


@app.get("/v1/catalog", response_model=CatalogResponse, operation_id="listCatalog")
def list_catalog(limit: int = Query(default=10, ge=1, le=10, description="Maximum items in this synthetic fixture.")) -> CatalogResponse:
    records = [CatalogItem.model_validate({key: row[key] for key in ("id", "title", "url")}) for row in FIXTURE["records"][:limit]]
    return CatalogResponse(items=records, next_cursor=None)


@app.get(
    "/v1/catalog/items/{item_id}",
    response_model=CatalogItem,
    responses={404: PROBLEM_404},
    operation_id="getCatalogItem",
)
def get_catalog_item(item_id: str) -> CatalogItem | JSONResponse:
    record = RECORDS.get(item_id)
    if record is None:
        return problem_response(404, "منبع پیدا نشد", "شناسه در fixture ساختگی وجود ندارد.", "not-found")
    return CatalogItem.model_validate({key: record[key] for key in ("id", "title", "url")})


@app.post(
    "/v1/assist",
    response_model=AssistResponse,
    responses={422: PROBLEM_422},
    operation_id="createAssistResponse",
)
def create_assist_response(payload: AssistRequest) -> AssistResponse | JSONResponse:
    question = payload.question.strip()
    if not question:
        return problem_response(
            422,
            "پرسش خالی است",
            "یک پرسش کوتاه و غیرشخصی وارد کنید.",
            "empty-question",
        )

    record = FIXTURE["records"][0]
    answer = record["answer_fa"] if payload.locale == "fa" else record["answer_en"]
    return AssistResponse(
        request_id="req-demo-001",
        status="completed",
        answer=answer,
        sources=[SourceRef(id=record["id"], title=record["title"])],
    )


@app.get("/demo", include_in_schema=False)
def demo() -> FileResponse:
    return FileResponse(ROOT / "demo.html", media_type="text/html; charset=utf-8")
```
