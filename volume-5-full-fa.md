# هنر و علم ساخت هوش — جلد پنجم

**The Art & Science of Building Intelligence | Babak & Ai**

وضعیت: ۱۲ فصل در نقشه؛ ۱ فصل تا این انتشار نگارش و آزموده شده‌اند. این فایل Markdown است؛ PDF و EPUB تولید و آزموده نشده‌اند.

## فهرست فصل‌های منتشرشده

- فصل ۱ (سراسری ۶۲) — Benchmarking، طراحی آزمون، معیارها، ارزیابی انسانی، عدم‌قطعیت و آلودگی بنچمارک

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
