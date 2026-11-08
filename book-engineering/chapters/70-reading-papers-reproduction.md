# جلد پنجم، فصل ۹ — خواندن مقاله و بازتولید نتیجه

**نگاشت:** فصل محلی ۹ جلد پنجم = فصل سراسری ۷۰. **تاریخ بازبینی منابع: ۴ نوامبر ۲۰۲۶.** فصل ۶۹ مسیر استقرار را تا artifact و محیط اجرا دنبال کرد؛ این فصل از یک ادعای پژوهشی به زنجیرهٔ شاهد، روش، داده، کد و نتیجه برمی‌گردد. در نقشهٔ جلد، فصل ۷۰ خواندن و بازتولید مطالعه را پوشش می‌دهد و فصل ۷۱ پس از آن به طراحی آزمایش، فرضیه، معیار، ساخت دیتاست، مقایسهٔ مدل‌ها و تحلیل آماری می‌پردازد؛ این فصل روش و شاهدِ پژوهش موجود را می‌سنجد و آن موضوع‌ها را جایگزین نمی‌کند. فصل ۶۲ طراحی ارزیابی و benchmark را می‌سازد؛ مبانی آن دوباره تدریس نمی‌شوند، بلکه به خواندن و آزمودن یک مقاله پیوند می‌خورند. پروژهٔ فصل یک بستهٔ آموزشیِ کاملاً ساختگی است، نه بازتولید یک پژوهش واقعی.

**پیش‌نیاز:** خواندن جدول و نمودار، مفاهیم ارزیابی فصل ۶۲ و آشنایی مقدماتی با Git و پایتون. **خروجی:** بتوانید ادعای مشخص را از دامنه و شواهدش جدا کنید، روش و معماری گزارش‌شده را بازسازی کنید، artifact و دستور لازم را ممیزی کنید و نتیجهٔ بازتولید را با مرز ادعا و عدم‌قطعیت گزارش دهید.

![شکل ۵-۹-۱ — نمودار مفهومی خواندن پژوهش از ادعای مقاله به روش، داده، کد و محیطِ نسخه‌دار؛ سپس اجرای مستقل و مقایسه با معیار ازپیش‌اعلام‌شده. خروجی‌ها جدا هستند: سازگار در تلورانس، متوقف به‌علت artifact گمشده، ارزیابی‌نشده برای دامنهٔ تازه، یا ناسازگار با معیار. برچسب و مسیر هر حالت در متن آمده است و معنا به رنگ وابسته نیست.](../diagrams/v5-ch09-paper-evidence.svg)

## ۱. مقاله را مانند زنجیرهٔ ادعا تا شاهد بخوانید

مقاله فقط چکیده، عدد بزرگ جدول آخر یا مخزن کد آن نیست. یک نتیجه از پرسش و تعریف دامنه آغاز می‌شود، از داده و روش عبور می‌کند، به metric و نمودار می‌رسد و در متن به ادعایی دربارهٔ یک جمعیت، مدل یا شرایط تبدیل می‌شود. خواندن نقادانه یعنی بازسازی این زنجیره، نه جست‌وجوی یک عدد برای تأیید باور قبلی.

در جلد پنجم، فصل ۶۸ امنیت سامانهٔ محصول و فصل ۶۹ انتشار آن را پوشش می‌دهند؛ فصل حاضر پژوهش را نه با عملیات production یکی می‌کند و نه با آزمون محصول. همچنین فصل ۵۶ برای قیمت و TCO بازار و تاریخ مشخص دارد؛ برآورد هزینهٔ محاسبهٔ مقاله باید از منابع و دامنهٔ همان پژوهش خوانده شود، نه از قیمت‌گذاری این فصل.

## ۲. واژگان یکسان نیستند؛ تعریف انتخاب‌شده را اعلام کنید

رشته‌ها و نهادهای مختلف دو واژهٔ کلیدی را گاه به‌صورت متفاوت به‌کار می‌برند. آکادمی‌های ملی آمریکا هم صریحاً دربارهٔ این ناسازگاری هشدار می‌دهند؛ بنابراین عنوان یک badge یا واژهٔ «بازتولید» بدون تعریف عملیاتی کافی نیست [۱].

در این کتاب، برای گزارش علمی از تعریف NASEM استفاده می‌کنیم. اصطلاح محاسباتی به انگلیسی:

`Reproducibility`

یعنی گروهی مستقل، با همان داده‌ها و مراحل، روش‌ها، کد و شرایط محاسباتیِ گزارش‌شده، نتیجهٔ محاسباتی را دوباره به‌دست آورد. برای تکرار یک پرسش علمی با داده‌های تازه، اصطلاح انتخاب‌شده این است:

`Replicability`

در ACM نسخهٔ ۱٫۱، برچسب‌های نتایج در محاسبات تعریف عملیاتی دیگری هم دارند: «نتیجهٔ بازتولیدشده» از artifactهای عرضه‌شدهٔ نویسنده بهره می‌گیرد و «نتیجهٔ تکرارشده» با artifactهایی که مستقل ساخته شده‌اند به دست می‌آید [۲]. این واژگان را به تعریف NASEM فرو نمی‌کاهیم؛ اگر مجله یا کنفرانس دیگری اصطلاح متفاوتی دارد، همان تعریف و دامنهٔ آن را کنار نتیجه ثبت کنید.

## ۳. سه گذر برای خواندن مقاله

در گذر نخست، چکیده، پرسش، شکل‌های اصلی، نتیجه‌گیری و محدودیت‌ها را بخوانید و بپرسید مقاله دقیقاً چه ادعایی دارد و برای چه دامنه‌ای. در گذر دوم، روش، داده، پیوست، جدول‌ها، منابع کد و توضیح metric را دنبال کنید؛ ادعای اصلی را به شاهد معین وصل کنید. در گذر سوم، یک ادعای قابل‌سنجش را انتخاب کنید، پیش‌نیازهای اجرا و معیار مقایسه را بنویسید و فقط سپس artifact را راه‌اندازی کنید.

این ترتیب جلوی دو خطای پرهزینه را می‌گیرد: اجرای مخزن بدون فهمیدن اینکه کدام ادعا را می‌آزماید، و برداشت کلی از نتیجه‌گیری بدون بررسی داده و روش. برای هر گذر، پرسش و ابهام باقی‌مانده را یادداشت کنید؛ آن‌ها را پس از اجرای کد از حافظه بازسازی نکنید [۴].

## ۴. نخست ادعاها را از هم جدا کنید

یک مقاله معمولاً چند ادعا دارد: یک روش روی benchmark معین بهتر بوده، سرعت یا حافظه کمتر مصرف کرده، یک جزء معماری علت بهبود بوده، یا نتیجه به محیط تازه تعمیم می‌یابد. این‌ها یک گزارهٔ واحد نیستند. برای هر ادعا شناسه‌ای مانند `C1` بدهید و فعل، جمعیت یا مجموعهٔ داده، مقایسه‌گر، پیامد و شرایط را صریح کنید.

واژه‌هایی مانند «بهتر»، «قوی»، «کارآمد» و «عمومی» را به معیار و دامنه تبدیل کنید. «بهتر» یعنی کدام metric و در کدام split؟ «کارآمد» یعنی latency، زمان آموزش، انرژی یا هزینه؟ «عمومی» یعنی کدام زبان، گروه یا محیطِ دیده‌نشده؟ اگر متن مقاله پاسخ نمی‌دهد، ابهام را ثبت کنید؛ به‌جای نویسنده جواب نسازید.

## ۵. دامنه و نردبان استنتاج را علامت بزنید

از مشاهدهٔ یک benchmark تا ادعای کلی چند گام است. نتیجهٔ روی مجموعهٔ آزمون، شاهد عملکرد همان روش در همان پروتکل و داده است؛ به‌تنهایی کیفیت در همهٔ کاربران، زبان‌ها، محیط‌ها یا کاربردهای آینده را ثابت نمی‌کند. ادعای علّی نیز به مقایسه و طراحی‌ای نیاز دارد که اثر عامل موردنظر را از گزینه‌های دیگر جدا کند.

هر بار که متن از «در این مجموعه» به «در کاربرد واقعی» یا از «همراهی» به «علت» می‌رسد، بنویسید کدام فرض یا دادهٔ تازه لازم است. اگر مقاله آن را نمی‌آزماید، نتیجه را با مرز خودش نقل کنید؛ نه آن را به توصیهٔ محصولی تبدیل کنید و نه به‌علت نقص گزارش فوراً به تقلب یا بی‌اعتباری متهم کنید.

## ۶. دفتر ادعا–شاهد بسازید

یک ردیف برای هر ادعای مهم بسازید. حداقل ستون‌ها: شناسه و متن آزمون‌پذیر ادعا، شکل/جدول/بخش روش که شاهد را می‌دهد، داده و split، metric و مقایسه‌گر، نتیجهٔ گزارش‌شده، فرض‌های باز، و محدودیت دامنه. شناسهٔ شکل یا صفحه را بیاورید تا خواننده بتواند ادعا را به منشأ آن دنبال کند.

این دفترچه، فهرست چک‌باکس‌های «مقاله را خواندم» نیست؛ ابزاری است برای اینکه هر عدد و نتیجه‌گیری به شاهد قابل‌بررسی وصل بماند. اگر یک عدد در شکل از جدولی بیرون می‌آید یا چند مرحلهٔ preprocessing دارد، مسیر هر دو را ثبت کنید [۴].

| شناسه | گزارهٔ آزمون‌پذیر | شاهد اولیه | داده و روش | ابهام یا مرز |
|---|---|---|---|---|
| `C1` | روش روی split ثابت، از baseline بهبود دارد | جدول و پیوست ارزیابی | split، metric، نسخهٔ کد | seed و پراکندگی نتیجه |
| `C2` | هزینهٔ inference کمتر است | جدول latency و تنظیم سخت‌افزار | batch، دقت، طول ورودی | زمان warm-up و نرخ بار |
| `C3` | نتیجه به دامنهٔ تازه تعمیم می‌یابد | آزمون بیرونی یا گروهِ نگه‌داشته‌شده | منشأ، جداسازی و ترکیب گروه | نمایندگی داده و تغییر دامنه |

## ۷. معماری و مسیر داده را از شکل و متن بازسازی کنید

برای مقالهٔ یادگیری ماشین، جعبه‌های معماری را به مسیر اجرایی تبدیل کنید: ورودی خام، پاک‌سازی و tokenization، split، آموزش، انتخاب checkpoint، inference، پس‌پردازش و محاسبهٔ metric. برای روش‌های دیگر، همان نقش‌ها را با اجزای واقعی جایگزین کنید. روی هر یال بنویسید چه داده‌ای جابه‌جا می‌شود و روی هر جزء نسخه یا تنظیم مؤثر را ثبت کنید.

شکل معماری می‌تواند ساده‌سازی یا نام‌گذاری مبهم داشته باشد؛ متن روش و پیوست را نیز بررسی کنید. اگر مقاله در شکل از دو مرحله می‌گوید اما کد فقط یک مسیر دارد، اختلاف را با file/line یا نسخه ثبت کنید. شکل، خودِ پیاده‌سازی نیست و README، خودِ نتیجهٔ مقاله نیست.

## ۸. داده و split را با واحد آزمایش بخوانید

نام dataset برای شناسایی نسخه کافی نیست. نسخه یا snapshot، مجوز و منشأ، معیار ورود/خروج، preprocessing، deduplication و نحوهٔ برچسب‌گذاری را بخوانید. واحد جداسازی را پیدا کنید: ردیف، فرد، سند، ویدئو، زمان، سازمان یا منبع. اگر واحدهای مرتبط میان train و test پخش شده باشند، نشت داده می‌تواند ارزیابی را خوش‌بینانه کند.

ثبت کنید split تصادفی، زمانی یا گروهی است؛ validation برای انتخاب مدل استفاده شده یا نه؛ test چندبار و با چه قاعده‌ای دیده شده؛ و آیا دادهٔ بیرونی همان توزیع هدف را می‌نمایاند. جایگزین کردن dataset غیرقابل‌دسترسی با dataset مشابه، همان آزمایش نیست؛ چنین کاری را به‌عنوان تغییر پروتکل و تحلیل جداگانه گزارش کنید.

## ۹. baseline، ablation و انتخاب مدل را ممیزی کنید

مقایسه فقط وقتی معنا دارد که baseline روشن و اجرای آن منصفانه باشد. بودجهٔ جست‌وجوی hyperparameter، تعداد آموزش‌ها، دادهٔ مجاز، دقت عددی، اندازهٔ مدل، زمان/سخت‌افزار و قاعدهٔ انتخاب checkpoint را کنار هم بگذارید. اگر روش تازه چند برابر فرصت تنظیم داشته، عدد برتر را بی‌قید به خود معماری نسبت ندهید.

Ablation باید عامل مورد ادعا را تا حد ممکن جدا کند: حذف جزء باید با بقیهٔ تنظیمات مقایسه‌پذیر بماند. از یک ablation به‌تنهایی سازوکار علّی قطعی نتیجه نگیرید؛ ممکن است چند جزء یا تعامل آن‌ها دخیل باشند. جزئیات کامل طرح و انتخاب baseline را در دفتر ادعا–شاهد نگه دارید.

## ۱۰. metric و جدول را با مخرج و واحد بخوانید

برای هر metric، تعریف، جهت بهترشدن، واحد، مقدار مرجع، مجموعهٔ محاسبه و تجمیع را پیدا کنید. میانگین macro با micro یکی نیست؛ average ممکن است روی ردیف، کاربر، زبان یا task گرفته شده باشد. در classification، معیار per-class و آستانه را ببینید؛ در generation، پروتکل داوری و نسخهٔ judge را؛ در زمان‌سنجی، batch size، warm-up و سخت‌افزار را.

از جدول عددها را تنها رونویسی نکنید. تعداد نمونه یا task، denominator، metricهای جاافتاده، علامت ± و توضیح پانویس را هم بخوانید. اگر مبنای normalization یا درصد بهبود مبهم است، عبارت دقیق را نقل کنید و ابهام را ثبت کنید. تعریف پیشرفتهٔ آماری و طراحی benchmark در فصل ۶۲ آمده‌اند؛ اینجا فقط از آن‌ها برای تفسیر ادعای مشخص استفاده می‌کنیم.

## ۱۱. تغییرپذیری و عدم‌قطعیت را پنهان نکنید

در روش تصادفی، یک seed یا یک split لزوماً تصویر پایداری را نشان نمی‌دهد. تعداد اجراها، seedها، splitها و قاعدهٔ خلاصه‌سازی را بیابید. اگر error bar وجود دارد، مشخص کنید انحراف معیار، خطای معیار یا فاصلهٔ اطمینان است و تغییرپذیریِ کدام عامل را نشان می‌دهد. NeurIPS نیز می‌خواهد روش محاسبه و فرض‌های error bar برای نتیجهٔ پشتیبان ادعا روشن باشد [۳].

«میانگین بالاتر» به‌تنهایی آزمون تفاوت معنی‌دار نیست؛ هم‌پوشانی error bar هم به‌تنهایی حکم عمومی نمی‌دهد. به‌جای استنتاج آماری از شکل کم‌جزئیات، uncertainty گزارش‌شده و محدودیت توان آزمون را بنویسید. اگر مقاله پراکندگی را ندارد، آن را از حدس خود پر نکنید.

## ۱۲. منابع محاسباتی و هزینهٔ بازتولید را ثبت کنید

برای اجرای محاسباتی، نوع CPU/GPU/شتاب‌دهنده، حافظه، تعداد worker، نسخهٔ runtime و کتابخانه‌ها، زمان اجرا و ذخیره‌سازی لازم را جست‌وجو کنید. اگر بخش بزرگی از هزینه مربوط به پیش‌آموزش، جست‌وجوی مدل یا اجراهای ناموفق است، هزینهٔ نهاییِ همان یک آزمایش را معادل هزینهٔ کل پژوهش نگیرید. چک‌لیست NeurIPS دربارهٔ compute worker، حافظه، زمان و هزینهٔ کل سؤال می‌کند [۳].

برآورد هزینه برای تصمیم‌گیری به دامنهٔ زمانی و بازار نیاز دارد. اگر مقاله سخت‌افزار و تعداد اجرا را نمی‌گوید، نیازمندی را «نامعلوم» علامت بزنید؛ قیمت روزی را از یک provider وارد نتیجهٔ علمی نکنید. هر تخمین تازه باید از اجرای اندازه‌گیری‌شده، نرخ بازار تاریخ‌دار و فرض‌های روشن ساخته شود.

## ۱۳. زنجیرهٔ artifact را نسخه‌بندی کنید

برای ادعای محاسباتی، فهرست artifact لازم ممکن است شامل نسخهٔ مقاله و supplement، کد، داده و snapshot، تنظیمات، seed، محیط، checkpoint یا وزن‌ها، tokenizer، scriptهای ساخت شکل و خروجی خام باشد. شناسهٔ branch یا tag متحرک کافی نیست؛ commit یا digest ثابت و مسیر ذخیره‌شده را ثبت کنید. به هر خروجی اصلی پیوند دهید که از کدام ورودی و script تولید شده است [۴].

وجود کد بدون داده، یا داده بدون مجوز بازتوزیع، زنجیره را کامل نمی‌کند. hash، منشأ و مجوز را نگه‌دارید؛ محتوای حساس یا credential را در notebook و log عمومی کپی نکنید. artifact ناشناس یا قدیمی را از mirror دلخواه دریافت و بی‌بررسی اجرا نکنید.

## ۱۴. «در دسترس»، «ارزیابی‌شده» و «نتیجه‌سازگار» یکی نیستند

یک پیوند عمومی ممکن است فقط بگوید artifact در دسترس است. اجرای آن و بررسی عملکرد، ارزیابی جداگانه است؛ آزمودن نتیجهٔ اصلی با یک تیم دیگر نیز ادعای مستقل دیگری است. در سیاست ACM، این‌ها badgeهای متمایزند: در دسترس بودن artifact، بررسی ویژگی‌های آن، و اعتبارسنجی نتیجه را یکی نگیرید [۲].

برای هر نشان، تعریف venue، هویت ارزیاب، دامنهٔ آزمون و زمان را بخوانید. badge به‌تنهایی همهٔ جدول‌های مقاله را تأیید نمی‌کند؛ ممکن است فقط یک نتیجه یا بخشی از artifact سنجیده شده باشد. نبود badge نیز به‌تنهایی نشان نمی‌دهد مقاله نادرست است.

## ۱۵. دقیقاً چه چیزی را بازتولید یا تکرار می‌کنید؟

پیش از اجرا، در گزارش خود بگویید کدام تعریف را به‌کار می‌برید. طبق انتخاب این فصل از NASEM، بازتولید محاسباتی یعنی اجرای مستقلِ همان داده، روش و کد/مراحل با شرایط مستند؛ پرسش واحد با دادهٔ جدید در این واژگان تکرار مطالعه است [۱]. این واژگان، بازتولیدپذیری کامل علم یا تعمیم به همهٔ دامنه‌ها را ادعا نمی‌کند.

با تعریف ACM برای برچسب‌های محاسباتی، اجرای مستقل با artifact نویسنده و اجرای مستقل با artifactهای تازه دو برچسب متفاوت‌اند [۲]. برای جلوگیری از سوءتفاهم، در گزارش هر دو را با فعل روشن توصیف کنید: «همان داده و کد»، «پیاده‌سازی مستقل»، «دادهٔ جدید» یا «آزمون دامنهٔ تازه». یک واژهٔ کوتاه جای این توضیح را نمی‌گیرد.

## ۱۶. پیش از اجرا، run card بنویسید

run card یک صفحهٔ کوتاه برای اجرای قابل‌ممیزی است. در آن شناسهٔ ادعا، محدودهٔ نتیجه، commit و digest، داده و مجوز، فرمان، محیط، seed، منابع، metric، معیار پذیرش، انحراف‌های مجاز و شرط توقف را پیشاپیش ثبت کنید. قاعدهٔ مقایسه را بعد از دیدن خروجی تغییر ندهید؛ اگر تغییر کرد، نسخه و دلیل تازه ثبت کنید.

یک اجرای کم‌خطر و محدود ابتدا مسیر داده و کد را می‌آزماید، نه اینکه با خروجی کوچک‌تر به‌جای عدد مقاله بنشیند. در اجرای پرهزینه، سقف زمان/هزینه، محدودیت credential و حذف داده را قبل از شروع تعیین کنید. اگر مجوز داده یا مدل اجازهٔ اجرا نمی‌دهد، محدودیت را ثبت کنید؛ با دور زدن آن «بازآفرینی» نکنید.

## ۱۷. فرمان، محیط و شواهد اجرا را نگه دارید

فرمان دقیق، working directory، نسخهٔ interpreter و package، قفل وابستگی، سخت‌افزار، seed، ورودی‌ها و آرگومان‌ها را ثبت کنید. اگر container یا environment lock دارید، digest یا lockfile را نگه دارید. نسخه‌های متحرک، dependencyهایی که هنگام اجرا خودکار دانلود می‌شوند یا secretهای تعریف‌نشده، اجرای دوم را مبهم می‌کنند.

خروجی خام و log را با run ID و timestamp به نسخهٔ ورودی پیوند دهید. فرمان نهایی را از workflow اجرا کنید، نه از یادداشت دست‌نویس جداگانه؛ این کار احتمال ناهمخوانی مستندات و اجرا را کم می‌کند [۴]. دادهٔ شخصی یا prompt خصوصی را در log نگه ندارید، مگر با مبنای مجاز و کنترل دسترسی روشن.

## ۱۸. بازتولید با تکرار و توسعه فرق دارد

در بازتولید محاسباتی، هدف سنجش این است که گزارش و artifactهای یک تحلیل با همان داده و شرایط چه نتیجه‌ای می‌دهند. در تکرار مطالعه، دادهٔ تازه برای همان پرسش گردآوری یا آزموده می‌شود؛ نتیجهٔ آن دربارهٔ پایداری شاهد است، نه فقط اجرای کد. در توسعه، پرسش، روش، جمعیت یا metric عوض می‌شود؛ آن را به‌عنوان نتیجهٔ تازه گزارش کنید.

یک اجرای مستقل می‌تواند روش را تأیید، رد یا محدود کند؛ اما سه کار را در یک عبارت مبهم ادغام نکنید. برنامه‌های reproducibility در یادگیری ماشین نشان داده‌اند که checklist، artifact policy و اجرای مستقل هرکدام سهم جداگانه‌ای در فهم نتایج دارند [۵].

## ۱۹. خطاهای متداولِ بازتولید

دلایل شکست رایج‌اند: URL داده منقضی، license ناسازگار، dependency حذف‌شده، API تغییرکرده، GPU یا حافظهٔ ناکافی، seed ناقص، نسخهٔ tokenizer متفاوت، split نامشخص، مسیر نسبی اشتباه یا preprocessing گزارش‌نشده. هر کدام را با شاهد ثبت کنید؛ پیام خطا را به یک نتیجهٔ روش‌شناختی تبدیل نکنید.

اگر می‌خواهید به‌جای آن dependency تازه، mirror، مدل کوچک‌تر یا دادهٔ جانشین بگذارید، این کار را در اجرای جداگانه و با diff تنظیمات انجام دهید. اجرای سازگار با نسخهٔ جدید ممکن است یک تحلیل مفید باشد، ولی دیگر بازتولید دقیق همان شرایط نیست. از مقاله و نسخهٔ artifact snapshot نگه دارید تا بررسی بعدی با نسخهٔ تازهٔ repository اشتباه نشود.

## ۲۰. اختلاف نتیجه را تشخیص دهید؛ علت را حدس نزنید

اگر نتیجه فرق دارد، نخست پروتکل را خط‌به‌خط مقایسه کنید: نسخهٔ داده، deduplication، split، preprocessing، metric و aggregation، seed، checkpoint selection، dependency، سخت‌افزار و rounding. اختلاف را به چند اندازهٔ قابل‌آزمون بشکنید و هر تغییر را جداگانه ثبت کنید. «نسخهٔ من بهتر شد» توضیح علت نیست.

اگر شاهد کافی برای علت ندارید، بنویسید «علت اختلاف تعیین نشد». اجرای ناموفق می‌تواند از نقص بسته، تغییر محیط، خطای پیاده‌سازی یا نوسان تصادفی ناشی شود؛ به‌تنهایی نادرستی یا سوءرفتار نویسنده را ثابت نمی‌کند. بازتولید موفق نیز به‌تنهایی درستی فرض، اعتبار اندازه‌گیری یا تعمیم‌پذیری را تضمین نمی‌کند [۱].

## ۲۱. دفتر ادعای نمونه: یک نتیجهٔ محدود، دو شکاف روشن

fixture آموزشی فصل هشت ردیف ساختگی دارد. برای ادعای `C1`، MAE baseline برابر ۰٫۵۰، مقدار گزارش‌شدهٔ روش برابر ۰٫۴۰ و مقدار اجرای دوباره برابر ۰٫۴۲ است. اختلافِ مقدار دوباره با عدد منتشرشدهٔ داخل fixture برابر ۰٫۰۲ و تلورانس ازپیش‌ثبت‌شده ۰٫۰۳ است؛ بهبود نسبی نسبت به baseline برابر ۱۶ درصد و حداقل مقرر ۱۵ درصد است. پس وضعیت `C1` در همین مثال `reproduced_within_tolerance` است.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="MAE برابر مجموع قدرمطلق اختلاف y زیرنویس i و y کلاه زیرنویس i برای i از یک تا n، تقسیم بر n است.">
  <mrow><mi>MAE</mi><mo>=</mo><mfrac><mn>1</mn><mi>n</mi><mrow><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi></munderover><mrow><mo>|</mo><msub><mi>y</mi><mi>i</mi></msub><mo>−</mo><msub><mi>ŷ</mi><mi>i</mi></msub><mo>|</mo></mrow></mrow></mfrac></mrow>
</math>

**متن جایگزین فرمول:** MAE برابر مجموع قدرمطلق اختلاف مقدار واقعی و پیش‌بینی‌شده در n ردیف، تقسیم بر n است.

`C2` به checkpoint و tokenizer نیاز دارد که در بسته موجود نیستند؛ پروژه آن را `blocked` می‌گذارد. `C3` برای دامنهٔ تازه به گروه دادهٔ مستقل نیاز دارد که ثبت نشده؛ نتیجه `not_assessed` است. نتیجهٔ کلی `partial_or_unassessed` می‌ماند. هیچ‌یک از این خروجی‌ها نتیجهٔ پژوهش واقعی یا آزمون مدل بیرونی نیستند.

## ۲۲. پروژهٔ عملی و اجرای آفلاین

فایل‌های پروژه در [پوشهٔ آزمایش فصل ۷۰](../projects/70-reading-papers-lab/README.md) هستند؛ بستهٔ داده در `synthetic_paper_packet.json`، گزارش محیط در `environment.json` و digest و مرز fixture در `fixture_manifest.json` ثبت شده است. پایتون کتابخانهٔ استاندارد را به‌کار می‌گیرد؛ شبکه، GPU، credential، دادهٔ شخصی یا مدل زنده لازم نیست.

از پوشهٔ پروژه اجرا کنید:

```sh
python3.13 -m unittest -v test_paper_reproduction.py
python3.13 paper_reproduction.py --packet synthetic_paper_packet.json --output /tmp/paper-results.json
cmp results.json /tmp/paper-results.json
```

اجرای پیش‌فرض نتیجهٔ `C1` را از داده‌های ردیفی دوباره محاسبه می‌کند، کمبود artifact و دامنه را برای `C2` و `C3` جداگانه ثبت می‌کند و hash ورودی را کنار خروجی می‌گذارد. `cmp` باید بدون پیام و با exit code صفر تمام شود؛ این فقط پایداری اجرای محلی همین fixture را می‌سنجد.

## ۲۳. خروجی پروژه، حکم مقاله نیست

`results.json` در اجرای مرجع یک claim را در تلورانس، یک claim را blocked و یک claim را ارزیابی‌نشده گزارش می‌کند. این همان چیزی است که آزمون می‌سنجد: پایداری parser و قواعد محدودِ fixture، نه صحت مقاله، کیفیت روش علمی یا تعمیم‌پذیری مدل.

اگر عددها را تغییر دهید و دوباره اجرا کنید، اجرای برنامه پیش از تولید نتیجه hash و تعداد ردیف را با `fixture_manifest.json` می‌سنجد؛ تغییر bytes به‌طور پیش‌فرض رد می‌شود تا نتیجهٔ ورودی تازه با مرجع مخلوط نشود. برای تغییر عمدی، manifest تازه را جداگانه بسازید، نسخهٔ fixture را افزایش دهید و هر دو digest را ثبت کنید. برای ادعای C2 به‌جای پرکردن مصنوعی checkpoint، دامنهٔ آزمون را «اجرا نشد» گزارش کنید. برای C3 باید داده و طرح بیرونیِ موجه طراحی شود؛ افزودن نام یک گروه در JSON، شاهدی از تعمیم نیست.

## ۲۴. مرزهای استنتاج و ملاحظات اخلاقی

دادهٔ دسترس‌پذیر الزاماً دادهٔ قابل‌بازنشر نیست؛ کد آزاد الزاماً checkpoint یا مجوز استفاده را آزاد نمی‌کند. به privacy، رضایت، مجوز، خطر بازشناسایی، شروط استفاده از مدل و داده و سیاست امنیتی دقت کنید. یک reproduction مسئولانه می‌تواند از اجرای بخشی از artifact صرف‌نظر کند و دلیل را روشن بنویسد.

نتیجهٔ ناموافق را فقط در حد روش و شواهدی که اجرا شد تفسیر کنید. آن را به برچسب «مقاله نادرست است» تبدیل نکنید مگر ادعای مشخص، طراحی مقایسه و شاهد کافی دارید. نتیجهٔ سازگار هم محدود به شرایط آزموده‌شده است؛ مستقل‌بودن تیم یا یک عدد برابر، همهٔ فرض‌ها را بررسی نمی‌کند.

## ۲۵. چک‌لیست خواندن مقاله

پیش از ارجاع به نتیجه یا اجرای artifact، این پرسش‌ها را پاسخ دهید. چک‌لیست راهنمای مشاهده است، نه امتیاز کیفیت قطعی؛ با موضوع پژوهش تطبیقش دهید [۳].

- آیا ادعای اصلی و دامنهٔ آن را می‌توان در یک جملهٔ قابل‌سنجش نوشت؟
- آیا هر ادعا به شکل، جدول، بخش روش یا دادهٔ معینی پیوند دارد؟
- آیا نسخه و منشأ داده، split و واحد استقلال روشن است؟
- آیا metric، مقایسه‌گر، denominator و قاعدهٔ انتخاب مدل مشخص‌اند؟
- آیا seed، تعداد اجرا، عدم‌قطعیت و روش error bar گزارش شده‌اند؟
- آیا محیط، dependency، سخت‌افزار، زمان و حافظه برای اجرا روشن‌اند؟
- آیا کد، داده، checkpoint، تنظیمات و مجوزهای لازم در دسترس و نسخه‌دارند؟
- آیا دستور اجرا دقیق است و به همان ورودی و نتیجه وصل می‌شود؟
- آیا معلوم است artifact فقط موجود است، ارزیابی شده یا نتیجه‌ای مستقلاً اعتبارسنجی شده است؟
- آیا محدودیت، هزینه، حریم خصوصی و خطر کاربردهای منفی در دامنهٔ مقاله بررسی شده‌اند؟

## ۲۶. جمع‌بندی

مقاله را از ادعا به شاهد بخوانید: دامنه را محدود کنید، روش و معماری را بازسازی کنید، داده و metric را بررسی کنید و زنجیرهٔ artifact را نسخه‌دار نگه دارید. پیش از اجرا، تعریف reproducibility یا replicability، معیار پذیرش، فرمان، محیط و تلورانس را روشن کنید.

هر نتیجه را با همان دامنه‌ای گزارش کنید که واقعاً آزموده‌اید. artifact گمشده یعنی اجرای محدودشده، نه ادعای ردشده؛ نتیجهٔ متفاوت یعنی مسئله‌ای برای بررسی، نه اتهام خودکار؛ و نتیجهٔ سازگار هم تضمین صحت یا تعمیم نیست. فایل‌های اجرای آفلاین در [پروژهٔ فصل ۷۰](../projects/70-reading-papers-lab/README.md)، پاسخ‌ها در [فایل پاسخ‌نامهٔ مستقل فصل ۷۰](../answers/70-reading-papers-reproduction-fa.md) و آزمون‌ها و محدودیت‌ها در [گزارش ممیزی فصل ۷۰](70-audit-report-fa.md) آمده‌اند.

## ۲۷. منابع و تاریخ بازبینی

منابع زیر در ۴ نوامبر ۲۰۲۶ بازبینی شدند. تعریف واژه‌ها، دامنهٔ چک‌لیست و تفاوت میان badgeها در متن صریح شده‌اند؛ پیوند رسمی و مشخصات هر منبع کنار همان مدخل آمده است.

۱. آکادمی‌های ملی علوم، مهندسی و پزشکی آمریکا. ۲۰۱۹. فصل سوم، «درک بازتولیدپذیری و تکرارپذیری».

*Reproducibility and Replicability in Science.* National Academies Press. DOI: 10.17226/25303.

https://nap.nationalacademies.org/read/25303/chapter/6

۲. انجمن ماشین‌های محاسباتی. سیاست مرور artifact و نشان‌گذاری، نسخهٔ ۱٫۱؛ منتشرشده در ۲۴ اوت ۲۰۲۰. تعریف badgeهای artifact و نتایجِ بازتولیدشده/تکرارشده در محاسبات.

*Artifact Review and Badging.*

https://www.acm.org/publications/policies/artifact-review-and-badging-current

۳. NeurIPS. راهنمای جاری چک‌لیست مقاله، شامل دامنهٔ ادعا، artifact و دستور اجرا، جزئیات آزمایش، عدم‌قطعیت و منابع محاسباتی؛ صفحهٔ جاری در زمان بازبینی به قالب ۲۰۲۶ پیوند می‌دهد.

*Paper Checklist Guidelines.*

https://neurips.cc/public/guides/PaperChecklist

۴. Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. 2013. «ده قاعدهٔ ساده برای پژوهش محاسباتیِ بازتولیدپذیر». *PLOS Computational Biology*, 9(10), e1003285. DOI: 10.1371/journal.pcbi.1003285.

https://doi.org/10.1371/journal.pcbi.1003285

۵. Pineau, J. و همکاران. ۲۰۲۱. «بهبود بازتولیدپذیری در پژوهش یادگیری ماشین: گزارش برنامهٔ بازتولیدپذیری NeurIPS 2019». *Journal of Machine Learning Research*, 22(164):1–20.

*Improving Reproducibility in Machine Learning Research.*

https://jmlr.org/papers/v22/20-303.html

## ۲۸. تمرین‌ها

۱. یک ادعای نتیجه‌گیری از مقاله‌ای که می‌شناسید انتخاب کنید. آن را به گزاره‌ای شامل دامنه، داده یا جمعیت، مقایسه‌گر و metric تبدیل کنید؛ هر بخشی را که مقاله روشن نکرده، جداگانه علامت بزنید.

۲. برای NASEM و ACM نسخهٔ ۱٫۱، یک جمله بنویسید که در آن معنای عملیاتی reproducibility و replicability در هر چارچوب از هم جدا باشد. سپس بگویید در گزارش خود کدام تعریف را انتخاب می‌کنید.

۳. از یک نمودار روش، مسیر داده تا نتیجه را در پنج گام بازسازی کنید. برای هر گام یک artifact و یک نسخه یا شناسهٔ لازم بنویسید.

۴. در یک جدول مقاله، جهت بهترشدن metric، واحد، denominator، دادهٔ ارزیابی و روش تجمیع را پیدا کنید. اگر هرکدام گزارش نشده، دقیقاً همان خلأ را بنویسید.

۵. مقاله‌ای با یک عدد میانگین و بدون error bar تصور کنید. فهرست کنید چه چیزهایی دربارهٔ seed، split، تعداد اجرا و تغییرپذیری نمی‌توان از آن عدد نتیجه گرفت.

۶. در fixture پروژه، چرا وضعیت C2 برابر «ردشده» نیست؟ چه artifactهایی کم‌اند و برای آزمودن ادعای آن چه شواهد دیگری لازم است؟

۷. یک برنامهٔ run card برای اجرای مستقل C1 بنویسید: commit، داده، محیط، فرمان، metric، معیار پذیرش و قاعدهٔ ثبت انحراف را مشخص کنید؛ سپس بگویید کدام بخش هنوز فقط آموزشی است.

۸. تفاوت میان نتیجهٔ سازگار در تلورانس، بازتولید ناموفق، artifact گمشده و تعمیمِ ارزیابی‌نشده را با یک مثال برای هرکدام توضیح دهید و برای هیچ‌کدام ادعای فراتر از شاهد ننویسید.

## پیوست اجرایی — کد تحلیل fixture

کد زیر عیناً از `paper_reproduction.py` پروژهٔ آزموده‌شده درج شده است؛ این پیوست برای همان بستهٔ ساختگی نوشته شده و ابزار عمومی داوری مقاله نیست.

```python
#!/usr/bin/env python3
"""Audit a deliberately synthetic teaching packet; never contacts a network."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

FIXTURE_ID = "v5-ch09-paper-reproduction-synthetic-v1"
REQUIRED_CLAIMS = {"C1", "C2", "C3"}
ROW_FIELDS = ("row_id", "target", "baseline_prediction", "reported_prediction", "rerun_prediction")


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


def validate_packet(packet: dict[str, Any]) -> None:
    if not isinstance(packet, dict) or packet.get("schema_version") != 1:
        raise ValueError("packet must be a version-1 JSON object")
    if packet.get("fixture_id") != FIXTURE_ID or packet.get("synthetic") is not True:
        raise ValueError("only the declared synthetic teaching fixture is accepted")
    paper = packet.get("paper")
    if not isinstance(paper, dict) or not paper.get("title") or not paper.get("paper_version"):
        raise ValueError("paper title and version are required")
    if paper.get("status") != "fictional teaching packet; not a published study":
        raise ValueError("the teaching packet must remain explicitly fictional")

    protocol = packet.get("protocol")
    if not isinstance(protocol, dict) or protocol.get("metric") != "mae":
        raise ValueError("this lab supports only the declared MAE protocol")
    rows = protocol.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("at least one fixed synthetic observation is required")
    seen_rows: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or any(field not in row for field in ROW_FIELDS):
            raise ValueError(f"row {index} is missing a required field")
        row_id = row["row_id"]
        if not isinstance(row_id, str) or not row_id or row_id in seen_rows:
            raise ValueError(f"row {index} has an empty or duplicate row_id")
        seen_rows.add(row_id)
        for field in ROW_FIELDS[1:]:
            _finite_number(row[field], f"row {row_id} {field}")

    published = protocol.get("published")
    if not isinstance(published, dict):
        raise ValueError("published metric values are required")
    for field in ("baseline_mae", "candidate_mae", "minimum_relative_improvement", "max_absolute_metric_difference"):
        value = _finite_number(published.get(field), f"published.{field}")
        if value < 0:
            raise ValueError(f"published.{field} cannot be negative")

    claims = packet.get("claims")
    if not isinstance(claims, list):
        raise ValueError("claims must be a list")
    claim_ids = [claim.get("id") for claim in claims if isinstance(claim, dict)]
    if len(claim_ids) != len(claims) or set(claim_ids) != REQUIRED_CLAIMS or len(claim_ids) != len(REQUIRED_CLAIMS):
        raise ValueError("the fixture must contain exactly the distinct claims C1, C2, and C3")
    by_id = {claim["id"]: claim for claim in claims}

    c1 = by_id["C1"]
    artifacts = c1.get("artifacts_available")
    required_artifacts = c1.get("required_artifacts")
    if not isinstance(required_artifacts, list) or not required_artifacts or not isinstance(artifacts, dict):
        raise ValueError("C1 must declare required artifacts and their availability")
    if any(not isinstance(name, str) or not name for name in required_artifacts):
        raise ValueError("C1 artifact names must be non-empty strings")
    if any(not isinstance(artifacts.get(name), bool) for name in required_artifacts):
        raise ValueError("C1 artifact availability must be explicit booleans")

    c2 = by_id["C2"]
    c2_required = c2.get("required_artifacts")
    c2_available = c2.get("artifacts_available")
    if not isinstance(c2_required, list) or not c2_required or not isinstance(c2_available, dict):
        raise ValueError("C2 must declare required artifacts and their availability")
    if any(not isinstance(name, str) or not name for name in c2_required):
        raise ValueError("C2 artifact names must be non-empty strings")
    if any(not isinstance(c2_available.get(name), bool) for name in c2_required):
        raise ValueError("C2 artifact availability must be explicit booleans")

    c3 = by_id["C3"]
    required_groups = c3.get("required_groups")
    observed_groups = c3.get("observed_groups")
    if (not isinstance(required_groups, list) or not required_groups
            or not isinstance(observed_groups, list)
            or any(not isinstance(group, str) or not group for group in required_groups + observed_groups)):
        raise ValueError("C3 must declare non-empty group names for required and observed coverage")


def _mae(rows: list[dict[str, Any]], prediction_field: str) -> float:
    return sum(abs(float(row["target"]) - float(row[prediction_field])) for row in rows) / len(rows)


def evaluate(packet: dict[str, Any]) -> dict[str, Any]:
    """Return claim-level results without treating missing evidence as a negative result."""
    validate_packet(packet)
    protocol = packet["protocol"]
    rows = protocol["rows"]
    published = protocol["published"]
    claims = {claim["id"]: claim for claim in packet["claims"]}

    missing_c1 = [name for name in claims["C1"]["required_artifacts"]
                  if not claims["C1"]["artifacts_available"][name]]
    c1_result: dict[str, Any] = {"claim_id": "C1", "scope": claims["C1"]["scope"]}
    if missing_c1:
        c1_result.update({"status": "blocked", "missing_artifacts": missing_c1,
                          "interpretation": "اجرای ادعای محدود C1 به‌علت artifact ناقص آغاز نشد."})
    else:
        baseline_mae = _mae(rows, "baseline_prediction")
        reported_candidate_mae = _mae(rows, "reported_prediction")
        rerun_candidate_mae = _mae(rows, "rerun_prediction")
        candidate_gap = abs(rerun_candidate_mae - float(published["candidate_mae"]))
        reported_gap = abs(reported_candidate_mae - float(published["candidate_mae"]))
        baseline_gap = abs(baseline_mae - float(published["baseline_mae"]))
        relative_improvement = (baseline_mae - rerun_candidate_mae) / baseline_mae if baseline_mae > 0 else None
        within_tolerance = (
            candidate_gap <= float(published["max_absolute_metric_difference"])
            and reported_gap <= float(published["max_absolute_metric_difference"])
            and baseline_gap <= float(published["max_absolute_metric_difference"])
            and relative_improvement is not None
            and relative_improvement >= float(published["minimum_relative_improvement"])
        )
        c1_result.update({
            "status": "reproduced_within_tolerance" if within_tolerance else "not_reproduced",
            "metrics": {
                "baseline_mae": round(baseline_mae, 6),
                "reported_candidate_mae_from_rows": round(reported_candidate_mae, 6),
                "published_candidate_mae": round(float(published["candidate_mae"]), 6),
                "rerun_candidate_mae": round(rerun_candidate_mae, 6),
                "absolute_difference_from_published_candidate": round(candidate_gap, 6),
                "reported_rows_difference_from_published_candidate": round(reported_gap, 6),
                "baseline_difference_from_published": round(baseline_gap, 6),
                "relative_improvement_vs_baseline": (round(relative_improvement, 6)
                                                       if relative_improvement is not None else None),
                "max_absolute_metric_difference": float(published["max_absolute_metric_difference"]),
                "minimum_relative_improvement": float(published["minimum_relative_improvement"]),
            },
            "interpretation": (
                "روی داده و پروتکل ساختگیِ ثابت، نتیجه در تلورانس اعلام‌شده به‌دست آمد؛ این فقط یک بازتولید آموزشی است."
                if within_tolerance else
                "با artifactهای موجود، معیار پذیرش عددی برآورده نشد؛ اختلاف به‌تنهایی علت علمی یا خطای مقاله را تعیین نمی‌کند."
            ),
        })

    missing_c2 = [name for name in claims["C2"]["required_artifacts"]
                  if not claims["C2"]["artifacts_available"][name]]
    c2_result = {
        "claim_id": "C2",
        "scope": claims["C2"]["scope"],
        "status": "blocked" if missing_c2 else "not_assessed",
        "missing_artifacts": missing_c2,
        "interpretation": (
            "ادعای وابسته به checkpoint اجرا نشد؛ نبود artifact شاهدی علیه درستی ادعا نیست."
            if missing_c2 else
            "وجود artifact به‌تنهایی بازتولید ادعا را انجام نمی‌دهد؛ اجرای مستقل هنوز ارزیابی نشده است."
        ),
    }

    c3 = claims["C3"]
    missing_groups = sorted(set(c3["required_groups"]) - set(c3["observed_groups"]))
    c3_result = {
        "claim_id": "C3",
        "scope": c3["scope"],
        "status": "not_assessed",
        "missing_required_groups": missing_groups,
        "interpretation": (
            "برای تعمیم به دامنهٔ جدید، گروه/دادهٔ مستقلِ لازم در این بسته نیست؛ ادعا آزموده نشده است."
            if missing_groups else
            "دادهٔ گروه‌های لازم فهرست شده، اما تحلیل تعمیم در این پروژه پیاده‌سازی نشده است."
        ),
    }

    claim_results = [c1_result, c2_result, c3_result]
    counts: dict[str, int] = {}
    for result in claim_results:
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    overall = "complete_for_declared_claims" if all(
        result["status"] == "reproduced_within_tolerance" for result in claim_results
    ) else "partial_or_unassessed"
    return {
        "project_id": FIXTURE_ID,
        "paper_id": packet["paper"]["paper_id"],
        "paper_status": packet["paper"]["status"],
        "synthetic": True,
        "claim_results": claim_results,
        "status_counts": counts,
        "overall_status": overall,
        "scope_note": "این خروجی فقط کنترل fixture ساختگی را گزارش می‌کند؛ داوری دربارهٔ مقاله یا مدل واقعی نیست.",
    }


def run(packet_path: Path, output_path: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    packet_bytes = packet_path.read_bytes()
    packet = json.loads(packet_bytes.decode("utf-8"))
    validate_packet(packet)
    fixture_hash = hashlib.sha256(packet_bytes).hexdigest()
    manifest_path = manifest_path or packet_path.with_name("fixture_manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (manifest.get("fixture_id") != FIXTURE_ID
            or manifest.get("sha256") != fixture_hash
            or manifest.get("synthetic") is not True
            or manifest.get("observation_count") != len(packet["protocol"]["rows"])):
        raise ValueError("fixture bytes do not match the declared manifest")
    if manifest.get("claim_ids") != ["C1", "C2", "C3"]:
        raise ValueError("fixture claim IDs do not match the declared manifest")
    result = evaluate(packet)
    result["fixture_sha256"] = fixture_hash
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=here / "synthetic_paper_packet.json")
    parser.add_argument("--manifest", type=Path, default=here / "fixture_manifest.json")
    parser.add_argument("--output", type=Path, default=here / "results.json")
    args = parser.parse_args()
    result = run(args.packet, args.output, args.manifest)
    counts = ", ".join(f"{key}={value}" for key, value in sorted(result["status_counts"].items()))
    print(f"{result['overall_status']}: {counts}; synthetic={result['synthetic']}; sha256={result['fixture_sha256']}")


if __name__ == "__main__":
    main()
```
