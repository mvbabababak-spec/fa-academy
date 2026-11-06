# جلد سوم، فصل ۸ — پروژهٔ دادهٔ کوچک: از منبع مجاز تا واژگان

**The Art & Science of Building Intelligence | Babak & Ai | فصل سراسری ۴۰ از نقشهٔ پنج‌جلدی**

**تاریخ بازبینی منابع: ۵ نوامبر ۲۰۲۶.** پس از اتصال encoderها در فصل ۳۹، اکنون یک پیکرهٔ کوچک و قابل‌ممیزی آماده می‌کنیم. این فصل پیش از آموزش مدل می‌ایستد: گردآوریِ مجاز، ثبت منشأ، پاک‌سازی، حذف تکرار، تقسیم بدون نشت و ساخت یک tokenizer پایه. حلقهٔ آموزش و ارزیابی مدل در فصل ۴۱ می‌آید.

**پیش‌نیاز:** Tokenizer و واژگان از فصل ۳۳؛ تقسیم داده و نشت از فصل ۲۶؛ توکن‌های Embedding و Attention از فصل‌های ۳۴–۳۸. **هدف:** بتوانید برای هر نمونه پاسخ دهید «از کجا آمده؟ تحت چه شرایطی می‌توانم استفاده‌اش کنم؟ چه تغییری روی آن انجام شده؟ در کدام split قرار گرفته؟ tokenizer با کدام بخش fit شده؟»

![شکل ۳-۸-۱ — مسیر دادهٔ متنی کوچک: منبع دارای شواهد مجوز وارد دروازهٔ provenance و privacy می‌شود؛ manifest و hash ساخته می‌شوند؛ پاک‌سازی و حذف تکرار پیش از split گروهیِ مبتنی بر group_id انجام می‌شود؛ گروه‌ها به train/validation/test جدا می‌شوند؛ فقط train به ساخت واژگان/tokenizer می‌رود و سه split مستند به فصل آموزش تحویل می‌شوند.](assets/images/babak-ai/v3-ch08-data-pipeline.webp)

**شکل ۳-۸-۱ — داده از یک ورودی خامِ مستند، از کنترل منشأ، حریم خصوصی و تکرار می‌گذرد؛ گروه‌ها پیش از ساخت واژگان به train/validation/test جدا می‌شوند.** نمودار، جریان مفهومی است؛ ترتیب مجوز و تقسیم باید با منبع و وظیفهٔ واقعی تطبیق یابد.

## ۱. قبل از مدل، پرسش داده را دقیق کنیم

مدل زبانی از همان ابتدا یک فرض پنهان دارد: متن‌هایی که می‌بیند، نمایندهٔ چیزی‌اند که می‌خواهیم از آن یاد بگیرد. اگر هدف، تکمیل جمله‌های فارسیِ خودساخته است، مجموعه‌ای از پیام‌های انگلیسیِ انجمن عمومی یا خبرهای وب لزوماً دادهٔ مناسب نیست. پیش از کد باید واحد مشاهده، زبان، دامنه، کاربرد موردنظر، کاربرانِ تحت تأثیر، معیار سادهٔ موفقیت و آنچه **قرار نیست** از داده نتیجه بگیریم را بنویسیم.

در این فصل واحد رکورد یک قطعهٔ کوتاه متن است؛ `group_id` چند رکورد هم‌منبع یا هم‌موضوع را کنار هم نگه می‌دارد. پروژه فقط آماده‌سازی داده را می‌آموزد. ۱۶ جملهٔ نمونه در پروژه برای همین درس نوشته شده‌اند؛ آن‌ها benchmark، نمایندهٔ زبان فارسی یا مجوزی برای گردآوری محتوای شخص ثالث نیستند. کد در [پروژهٔ اجرایی فصل ۴۰](book-engineering/projects/40-small-data-project/README.md) و پاسخ تمرین‌ها در [پاسخ‌نامهٔ فصل ۴۰](book-engineering/answers/40-small-data-project-fa.md) آمده است.

## ۲. معیار پذیرش داده را پیش از جمع‌آوری تعیین کنیم

پیش از دانلود یا کپی هر نمونه، فهرست کوتاهی از معیارهای پذیرش بسازید: موضوع و زبان مرتبط‌اند؛ منبع و نسخه معلوم‌اند؛ شرایط استفاده برای **همین استفادهٔ موردنظر** بررسی شده؛ دادهٔ شخصیِ غیرضروری ندارد؛ قالب قابل‌خواندن است؛ و نمونه را می‌توان با گروه‌بندی معنادار تقسیم کرد. اگر یک شرط حیاتی نامعلوم است، رکورد را «حل‌نشده» علامت بزنید و وارد training corpus نکنید.

به‌جای «هرچه بیشتر، بهتر»، سؤال را این‌گونه صورت‌بندی کنید: «با چه کمترین دادهٔ مجازی می‌توان pipeline و آزمون را بررسی کرد؟» در پیکرهٔ کوچک، کیفیت منبع، تناسب دامنه و نبود نشت ممکن است مهم‌تر از افزودن متن‌های نامعلوم باشد. پروژهٔ DataComp نشان می‌دهد در آزمایش‌های تصویر–متنِ همان benchmark، فیلتر و ترکیب داده می‌تواند نتیجهٔ مدل را تغییر دهد؛ این شاهدی بر اهمیت آزمایش طراحی داده در آن setting است، نه قانون اینکه هر فیلتر یا مجموعهٔ کوچک همیشه بهتر است [۸].

## ۳. «قابل‌دسترسی» به معنی «مجاز برای آموزش» نیست

داده می‌تواند در وب قابل مشاهده باشد، اما این موضوع به‌تنهایی نه اجازهٔ کپی، نه اجازهٔ بازتوزیع و نه پاسخ روشن دربارهٔ پردازش برای آموزش می‌دهد. منبع می‌تواند مجوز متن، شرایط استفادهٔ پلتفرم، حق پایگاه داده، حق حریم خصوصی یا محدودیت‌های دیگری داشته باشد. حتی یک مجوز باز هم لزوماً تمام حقوق مربوط به هر شخص/عنصر داخل محتوا را حل نمی‌کند. Creative Commons در توضیح CC BY 4.0 صریحاً یادآوری می‌کند که حقوقی مانند privacy، publicity یا moral rights ممکن است جداگانه مطرح باشند [۲].

CC BY 4.0 امکان اشتراک و اقتباس را در چارچوب شروط مجوز، از جمله attribution و اعلام تغییرات، بیان می‌کند؛ CC0 ابزار dedication به public domain است، اما خود Creative Commons می‌گوید وضعیت حقوقی اثر را راستی‌آزمایی نمی‌کند [۲، ۳]. «Public domain» نیز در هر حوزهٔ قضایی و برای هر نوع حق یکسان تفسیر نمی‌شود. این فصل مشاورهٔ حقوقی نمی‌دهد؛ اگر اجازه، مالکیت یا کاربردی مبهم است، متن را جمع‌آوری نکنید تا بررسی مناسب انجام شود.

قانون سادهٔ آزمایشگاه: از متن خودنوشته، دادهٔ صریحاً مجاز، مجوز سازمانیِ ثبت‌شده یا مجموعه‌ای که شروط آن را خوانده‌اید شروع کنید. از دورزدن paywall، ورود با حساب برای scrape، کنارگذاشتن robots/terms یا استخراج پنهانیِ دادهٔ کاربران استفاده نکنید. سیاست مجاز پروژه باید سخت‌تر از «URL باز شد» باشد.

## ۴. منشأ را برای هر رکورد نگه داریم

هر سطر باید مسیر بازگشت به منبع داشته باشد؛ برای مثال: عنوان و صاحب اثر، نشانی نسخهٔ دقیق، تاریخ دریافت/بررسی، روش جمع‌آوری، شناسهٔ منبع اصلی و عبارت مجوز. اگر فایل از آرشیو می‌آید، نسخه/شناسهٔ آرشیو و hash فایل را ثبت کنید؛ اگر نمونه خودنگاشته است، همین را شفاف بنویسید. ثبت «منبع: اینترنت» یا «مجوز: عمومی» برای بازتولید یا ممیزی کافی نیست.

پیشنهاد می‌شود سه لایه را از هم جدا کنید: (۱) `raw/` فقط‌خواندنی با فایل اولیه و شناسهٔ منشأ؛ (۲) `processed/` با کد و نسخهٔ تبدیل؛ (۳) `splits/` شامل خروجی‌های train، validation و test. در این پروژه برای کوچکی مثال، متن‌های خودنوشته مستقیماً در manifest هستند؛ برای دادهٔ واقعی، خام را جدا نگه دارید و روی آن overwrite نکنید. hash محتوا به تشخیص تغییر ناخواسته کمک می‌کند، اما نه هویت نویسنده را ثابت می‌کند و نه حق استفاده می‌دهد.

## ۵. Manifest: مجوز، گروه و متن در یک قرارداد روشن

پروژه از JSONL استفاده می‌کند: هر خط یک شیء JSON مستقل است. فیلدهای لازم عبارت‌اند از `id`، `group_id`، `text`، `source`، `license`، `attribution`، `language`، `acquired_at` و `rights_note`. `group_id` شناسهٔ رابطه‌ای است که در تقسیم باید کنار هم بماند؛ ممکن است نویسنده، مجموعهٔ منبع، داستان، نشست یا رشتهٔ گفتگو باشد. `rights_note` توضیح می‌دهد چه چیزی بررسی شده، نه اینکه خودبه‌خود مجوز را اثبات کند.

| فیلد | پرسش پاسخ‌داده‌شده | نمونهٔ پروژه |
|---|---|---|
| `id` | این رکورد کدام است؟ | `fa-demo-001` |
| `group_id` | چه نمونه‌هایی نباید بین splitها پخش شوند؟ | `garden-notes` |
| `source` و `rights_note` | از کجا آمده و شواهد بررسی چیست؟ | `self-authored-demo` و توضیح متنی |
| `license` و `attribution` | کدام شروط/اعتباردهی باید حفظ شود؟ | `SELF-CREATED`؛ برچسب داخلی پروژه |
| `language` و `acquired_at` | زبان/زمان ثبت کدام است؟ | `fa` و تاریخ ISO |
| `text` | چه محتوایی پردازش می‌شود؟ | یک جملهٔ خودنوشته |

`SELF-CREATED` یک شناسهٔ استاندارد مجوز عمومی نیست؛ در این پروژه صرفاً نشان می‌دهد متن نمونه برای آموزش همین مخزن نوشته شده. برای توزیع مجدد، نباید این مقدار را جایگزین یک مجوز انتشار واقعی یا اجازهٔ نویسنده کنید.

## ۶. حریم خصوصی را پیش از tokenize شدن بررسی کنیم

متن می‌تواند ایمیل، شماره، نشانی، شناسهٔ کاربری، دادهٔ مکانی، اطلاعات سلامت یا جزئیاتی داشته باشد که با کنار هم گذاشتنشان فردی شناسایی شود. حذف نام به‌تنهایی ناشناس‌سازی نیست. اصل کمینه‌سازی را به‌کار ببرید: فقط دادهٔ لازم را جمع کنید؛ شناسه‌ها را جدا و محدود نگه دارید؛ دورهٔ نگهداری و افراد مجاز به دسترسی را مشخص کنید؛ و پیش از انتشار، محتوای حساس و نقل‌قول‌های طولانی را بازبینی کنید.

پروژه چند الگوی سادهٔ ایمیل/تلفن را پیش از ادامه رد می‌کند تا مسیر خطا دیده شود. این regexها **ممیزی حریم خصوصی نیستند**: ممکن است شناسهٔ واقعی را نبینند یا رشتهٔ عادی را اشتباه پرچم بزنند. نبود پیام خطا یعنی فقط این چند الگو پیدا نشده است. برای دادهٔ واقعی، بررسی انسانیِ آگاه به دامنه و فرایند سازمانی لازم است؛ مخصوصاً اگر متن به کودکان، سلامت، مکان دقیق یا دادهٔ محرمانه مربوط باشد.

مجوز حق نسخه‌برداری و حریم خصوصی دو سؤال جدا هستند. در CC0 نیز deed تصریح می‌کند که حقوق privacy/publicity را از بین نمی‌برد [۳]. دادهٔ شخصیِ بدون ضرورت یا مبنای روشن را وارد نمونهٔ آموزشی نکنید.

## ۷. پاک‌سازی بازتولیدپذیر باشد، نه سلیقه‌ای

پاک‌سازی خوب هر تغییر را با هدف قابل‌شرح پیوند می‌دهد. تبدیل newline، حذف فضای تکراری یا رفع یک قالب‌نویسی خراب می‌تواند مناسب باشد؛ اما حذف «متن عجیب»، کوتاه‌کردن همهٔ جمله‌های بلند یا فیلترکردن یک گویش ممکن است همان پدیده‌ای را حذف کند که مدل باید ببیند. پیش از هر فیلتر، تعداد نمونه‌های حذف‌شده، دلیل، مثال قبل/بعد و پیامد احتمالی برای پوشش زبان را ثبت کنید.

کد پروژه فقط دو تبدیل ثابت انجام می‌دهد: Unicode NFC و تبدیل رشته‌های whitespace متوالی به یک فاصله. خروجی پاک‌شده از manifest خام جداست، و `normalized_text_sha256` برای کنترل هویت متنِ پس از همین تبدیل ساخته می‌شود. اگر متنِ خام لازم است، آن را جدا و با دسترسی/مجوز مناسب نگه دارید؛ نیازی نیست برای آموزش، فرادادهٔ حساسِ منبع را داخل فایل مدل‌ورودی کپی کنیم.

تست کنید که اجرای دوباره با ورودی، seed و نسخهٔ کد یکسان همان split، واژگان و hashها را بسازد. اگر رفتار کتابخانه یا نسخهٔ Python عوض شد، محیط و نسخه را ثبت کنید؛ «seed ثابت» به‌تنهایی همهٔ تفاوت‌های محیط را حذف نمی‌کند.

## ۸. متن فارسی را بی‌جهت تخت نکنیم

NFC دنباله‌های کدپوینتِ دارای معادل canonical را هم‌شکل می‌کند، اما آن را با یکسان‌سازی تهاجمیِ حروف یا حذف نشانه‌ها یکی نگیرید. در فارسی، نیم‌فاصله می‌تواند مرز واژه را نشان دهد؛ نگاشت «ي/ی»، «ك/ک»، حذف اعراب، حذف نشانه‌گذاری یا یکسان‌کردن اعداد به تصمیم وظیفه وابسته است. اگر این تبدیل‌ها لازم‌اند، نسخهٔ اصلی را نگه دارید، تبدیل را مستند کنید و اثرش را بر tokenizer و متن‌های هدف بسنجید.

از `NFKC` یا حذف همهٔ کاراکترهای Unicode به‌صورت پیش‌فرض استفاده نمی‌کنیم، چون ممکن است تفاوت‌هایی را که برای نمایش، جست‌وجو یا متن آمیخته مهم‌اند پنهان کند. خطای encoding را هنگام خواندن فایل تشخیص دهید، نه اینکه هر نویسهٔ ناخوانا را بی‌صدا حذف کنید. پروژه whitespace را فشرده می‌کند و نیم‌فاصله را حفظ می‌کند؛ این رفتار ساده است، اما tokenizer واژه‌ای آن تحلیل صرفی یا جداسازی دقیق فارسی انجام نمی‌دهد.

## ۹. تکرار را قبل از split پیدا کنیم

تکرار دقیق می‌تواند معیار را خوش‌بینانه کند اگر نسخهٔ یک متن در train و test ظاهر شود. ابتدا متن را با تبدیل‌های مستند canonical کنید؛ سپس hash بگیرید و متن‌های برابر را در یک گروه محتوایی قرار دهید یا یکی را حذف کنید. گزارش حذف باید شناسهٔ نسخهٔ نگه‌داشته‌شده، شناسهٔ نسخهٔ تکراری، source، گروه، مجوز، attribution و دلیل را حفظ کند؛ در غیر این صورت یکسان‌سازی ممکن است شواهد منشأ یا اختلاف مجوز را پنهان کند.

کد این فصل فقط برابری دقیقِ متنِ NFC/whitespace-normalized را می‌یابد. آن نمی‌تواند paraphrase، نقل‌قول کوتاه، ترجمه، تکرار تصویریِ متفاوت یا محتوای نزدیک را تشخیص دهد. MinHash/SimHash یا embedding-nearest-neighbor می‌تواند برای دادهٔ بزرگ‌تر به audit کمک کند، ولی threshold باید با نمونهٔ مثبت و منفی بررسی شود؛ شباهت بالا لزوماً تخلف یا نشت نیست و شباهت پایین هم پاک‌بودن را ثابت نمی‌کند.

در پروژه، حذف تکرار روی متن نرمال‌شده **پیش از** انتساب به split انجام می‌شود، و `duplicates.json` منبع هر دو ردیف را نگه می‌دارد. اگر تکرارها برچسب یا مجوز ناسازگار دارند، آن‌ها را بی‌سروصدا merge نکنید: مورد را برای بررسی انسانی نگه دارید.

## ۱۰. Train، validation و test سه نقش متفاوت دارند

`train` برای یادگیری وزن‌ها و fit کردن preprocessing استفاده می‌شود؛ `validation` برای انتخاب تنظیمات و تصمیم توقف؛ `test` برای یک ارزیابی نهاییِ نگه‌داشته‌شده پس از تثبیت روش است. اگر بارها بر اساس test تغییر بدهید، این مجموعه هم به‌طور غیرمستقیم وارد تصمیم‌گیری شده است. اصل، جدایی اطلاعاتی است نه صرفاً سه نام پوشه؛ leakage در کاربردهای مختلف می‌تواند از پیش‌پردازش، نمونه‌های مشابه، هدف یا زمان‌بندی بیاید [۵].

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="مجموعه‌های train و validation و test باید دوبه‌دو اشتراک نمونهٔ مستقل نداشته باشند؛ اگر گروهی واحد تقسیم می‌شود باید همهٔ اعضای آن در یک بخش باشند"><mrow><mi>D</mi><mo>=</mo><msub><mi>D</mi><mi>train</mi></msub><mo>∪</mo><msub><mi>D</mi><mi>val</mi></msub><mo>∪</mo><msub><mi>D</mi><mi>test</mi></msub><mo>,</mo><mspace width="0.5em"/><msub><mi>D</mi><mi>a</mi></msub><mo>∩</mo><msub><mi>D</mi><mi>b</mi></msub><mo>=</mo><mi>∅</mi></mrow></math>

**متن جایگزین فرمول:** مجموعه‌های train و validation و test باید دوبه‌دو اشتراک نمونهٔ مستقل نداشته باشند؛ اگر گروهی واحد تقسیم می‌شود باید همهٔ اعضای آن در یک بخش باشند.

در متن، برش تصادفیِ سطرها همیشه امن نیست. اگر چند جمله از یک سند، نسخه‌های نزدیک از یک صفحه یا بخش‌هایی از یک گفتگو باشند، باید آن‌ها را گروه‌بندی و با هم تقسیم کنید. در corpus زمانی می‌توان به‌جای shuffle از زمان آینده برای test استفاده کرد؛ در corpus نویسنده‌محور ممکن است نویسنده‌ها گروه باشند. انتخاب split پرسشی از نوع «چه تعمیمی می‌خواهم اندازه بگیرم؟» است، نه یک نسبت ثابت برای همهٔ مسئله‌ها.

## ۱۱. تقسیم گروهی تکرارپذیر، با نسبت‌های تقریبی

پروژه ابتدا `group_id`های یکتا را برمی‌دارد، مرتب می‌کند، با seed ثابت جابه‌جا می‌کند و سپس گروه‌ها را به train/validation/test تخصیص می‌دهد. الگوریتم برای پیکرهٔ کوچک هر split را حداقل با یک گروه پر می‌کند، اگر دست‌کم سه گروه مستقل وجود داشته باشد. تمام رکوردهای یک گروه در یک split می‌مانند؛ بنابراین تعداد **رکوردها** ممکن است با نسبت هدف تفاوت داشته باشد، مخصوصاً وقتی گروه‌ها اندازه‌های متفاوت دارند.

اگر ۸ گروهِ هم‌اندازه داشته باشیم و هدف ۸۰/۱۰/۱۰ باشد، تقسیم تعداد گروه‌ها می‌تواند ۶/۱/۱ شود. با دو رکورد در هر گروه، خروجی ۱۲/۲/۲ رکورد است؛ سهم train برابر ۷۵٪ است، نه دقیقاً ۸۰٪. این نقص الگوریتم نیست؛ محدودیت واحدهای مستقلِ کوچک است. افزایش تعداد گروه‌های مستقل یا استفاده از split ازپیش‌تعریف‌شده ممکن است مناسب‌تر باشد، اما نباید صرفاً برای رسیدن به درصد دلخواه گروه‌ها را بشکنیم.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="اگر گروه‌ها g باشند و سهم train و validation و test برابر p باشد، تعداد رکوردهای هر split تابع اندازهٔ گروه‌های اختصاص‌یافته است و ضرورتاً برابر سهم ضربدر کل رکوردها نیست"><mrow><msub><mi>n</mi><mi>s</mi></msub><mo>=</mo><msub><mo>∑</mo><mrow><mi>g</mi><mo>∈</mo><msub><mi>G</mi><mi>s</mi></msub></mrow></msub><msub><mi>n</mi><mi>g</mi></msub><mo>,</mo><mspace width="0.5em"/><mfrac><msub><mi>n</mi><mi>s</mi></msub><mi>N</mi></mfrac><mo>≠</mo><msub><mi>p</mi><mi>s</mi></msub><mspace width="0.3em"/><mi>in</mi><mspace width="0.3em"/><mi>general</mi></mrow></math>

**متن جایگزین فرمول:** اگر گروه‌ها g باشند و سهم train و validation و test برابر p باشد، تعداد رکوردهای هر split تابع اندازهٔ گروه‌های اختصاص‌یافته است و ضرورتاً برابر سهم ضربدر کل رکوردها نیست.

`summary.json` شمار رکورد و گروه را جدا ثبت می‌کند. همین فایل، seed و شناسهٔ گروه‌ها را نگه می‌دارد تا بتواتید تقسیم را بازبینی کنید. اگر گروه کم است، برآورد ارزیابی ناپایدار خواهد بود؛ یک درصد ظاهراً دقیق این عدم قطعیت را حل نمی‌کند.

## ۱۲. واژگان را فقط از train بیاموزیم

Tokenizer بخشی از preprocessing است: مرزهای واحد زبانی را می‌سازد و شناسه‌ها را تعیین می‌کند. اگر واژگان با test ساخته شود، اطلاعات test وارد pipeline شده، حتی اگر وزن مدل را با آن آموزش نداده باشیم. برای جلوگیری از این نشت، vocab یا merge ruleهای BPE را فقط روی train fit کنید؛ سپس همان tokenizer منجمد را برای validation و test به‌کار ببرید. راهنمای Tokenizers تفاوت tokenizerها، special tokenها و ذخیرهٔ artifact را نشان می‌دهد [۷].

این پروژه baseline واژه‌ای ساده دارد؛ نشانه‌ها با یک regex Unicode، شامل نیم‌فاصله، پیدا می‌شوند. شمارش هر نشانه در train را `c(w)` بگیریم؛ ترتیب واژگان بر اساس فراوانی نزولی و در تساوی ترتیب Unicode است. چهار شناسهٔ رزروشدهٔ `<pad>`, `<unk>`, `<bos>`, `<eos>` در ابتدای vocabulary می‌آیند. واژهٔ نادیده در validation/test به `<unk>` نگاشت می‌شود.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="واژگان آموخته‌شده از متن‌های train ساخته می‌شود؛ نسبت واژه‌های خارج از واژگان برابر شمار رخدادهای ناشناخته تقسیم بر کل رخدادهای متن ارزیابی است"><mrow><mi>V</mi><mo>=</mo><mrow><mi>Special</mi></mrow><mo>∪</mo><mo>{</mo><mi>w</mi><mo>:</mo><mi>c</mi><mo>(</mo><mi>w</mi><mo>,</mo><msub><mi>D</mi><mi>train</mi></msub><mo>)</mo><mo>≥</mo><mi>f</mi><mo>}</mo><mo>,</mo><mspace width="0.5em"/><mi>OOV</mi><mo>=</mo><mfrac><mrow><mi>unseen</mi><mspace width="0.2em"/><mi>tokens</mi></mrow><mrow><mi>all</mi><mspace width="0.2em"/><mi>eval</mi><mspace width="0.2em"/><mi>tokens</mi></mrow></mfrac></mrow></math>

**متن جایگزین فرمول:** واژگان آموخته‌شده از متن‌های train ساخته می‌شود؛ نسبت واژه‌های خارج از واژگان برابر شمار رخدادهای ناشناخته تقسیم بر کل رخدادهای متن ارزیابی است.

Word-level tokenizer برای آموزش مفاهیم و آزمون OOV روشن است، اما واژهٔ فارسیِ صرف‌شده، نیم‌فاصله، نویسهٔ نو و غلط املایی می‌توانند OOV را بالا ببرند. مدل زیرواژه‌ای/byte-level این ریسک را به شکل دیگری مدیریت می‌کند، ولی حد واژگان، طول توالی و دقت بازسازی را هم تغییر می‌دهد. فصل ۳۳ BPE را از صفر می‌سازد؛ پروژهٔ حاضر به‌جای تکرار آن، مسئلهٔ ساخت vocabulary از train را نشان می‌دهد.

## ۱۳. کارت داده، داده‌برگ و گزارش نسخه

یک README یا کارت داده باید توضیح دهد: هدف و استفادهٔ غیرمجاز؛ منابع و شروط؛ زبان/گونه و دامنه؛ نحوهٔ گردآوری و گزینش؛ برچسب‌گذاری یا transform؛ اندازه و splitها؛ فیلترها و موارد حذف‌شده؛ اطلاعات حساس و فرایند رسیدگی؛ محدودیت پوشش و سوگیری؛ مالک نگهداری، نسخه و تاریخ به‌روزرسانی. «اطلاع نداریم» پاسخ پذیرفتنی است؛ حدس را به‌عنوان واقعیت ثبت نکنید.

Datasheets for Datasets پیشنهاد می‌کند انگیزه، ترکیب، فرایند گردآوری و استفادهٔ توصیه‌شده مستند شوند [۱]. برای متن/زبان، Data Statements نسخهٔ سوم به زمینهٔ زبانی، منبع، preprocessing، محدودیت و مشارکت جامعهٔ زبانی توجه دارد [۴]. Data Cards هم شواهدی مانند upstream source، روش جمع‌آوری، شیوهٔ آموزش/ارزیابی و intended use را در قالبی قابل‌خواندن مطرح می‌کنند [۹]. این چارچوب‌ها چک‌لیست فکرکردن‌اند؛ تکمیل قالب به‌تنهایی داده را بی‌طرف یا قانونی نمی‌کند.

خروجی `data_card.md` پروژه عمداً کوتاه است و محدودیت نمونه را ثبت می‌کند. کارت واقعی باید در کنار فایل داده نسخه‌گذاری شود، تغییرات آن با انتشار نسخه بازبینی شود و لینک به منبع/مجوز را تا حد مجاز نگه دارد. اگر redistribution ممنوع است، کارت می‌تواند مشخصات و فرایند دسترسی را توضیح دهد، بی‌آنکه متن خام را منتشر کند.

## ۱۴. پروژه را مرحله‌به‌مرحله اجرا کنیم

برای اجرای نمونه، از پوشهٔ پروژه `python -m unittest discover -v` و سپس `python small_corpus.py` را بزنید. هر دو به Python و کتابخانهٔ استاندارد نیاز دارند؛ هیچ network request، PyTorch، model checkpoint یا GPU در این فصل لازم نیست. مسیرهای قابل‌تغییر `--manifest`, `--output` و `--seed` هستند.

ترتیب کار در `prepare_dataset` چنین است: بایت‌های فایل manifest را hash کن؛ JSONL را بخوان و schema/مجوز/تاریخ/الگوهای حساس را بررسی کن؛ متن را NFC و whitespace را یکسان کن؛ `id` تکراری را رد کن؛ hash متن نرمال‌شده را ثبت کن؛ تکرار دقیق را حذف و گزارش کن؛ `group_id`ها را قبل از tokenizer به سه split تخصیص بده؛ vocabulary را از train بساز؛ و artifactها، شمارش‌ها و کارت داده را ذخیره کن. `summary.json` هش SHA-256 بایت‌های دقیق manifest و هش متن‌های نرمال‌شده را جدا ثبت می‌کند؛ این شناسهٔ ورودی به بازبینی نسخه کمک می‌کند، اما مجوز/منشأ حقوقی را ثابت نمی‌کند. اجرای دوباره با همان manifest، seed و نسخهٔ کد باید artifactهای یکسان بسازد؛ آزمون پروژه این برابری بایتی را بررسی می‌کند. Hugging Face Datasets نیز APIهای `map`, `filter`, split و ذخیره را ارائه می‌کند، اما پروژه برای دیدن قراردادها وابستگی دیگری اضافه نمی‌کند [۶].

## ۱۵. خروجی قابل‌ممیزی چگونه است؟

اجرای پیش‌فرض ۱۶ رکورد در ۸ گروه را می‌پذیرد؛ پس از تقسیم، train شامل ۱۲ رکورد/۶ گروه، validation دو رکورد/یک گروه و test دو رکورد/یک گروه است. هیچ گروهی بین splitها مشترک نیست. در نمونه تکرار دقیقی حذف نمی‌شود. vocabulary شامل چهار special token و ۹۸ نشانهٔ مشاهده‌شده در train است؛ این عدد به متن نمونه، regex، seed، نسخهٔ کد و تنظیمات وابسته است، نه معیار کیفیت tokenizer.

`build/train.jsonl`, `validation.jsonl`, `test.jsonl` برای فصل ۴۱ آماده‌اند. `vocab.json` ترتیب توکن‌ها و قرارداد normalization را نگه می‌دارد؛ `summary.json` گروه‌ها، تعدادها، seed و SHA-256 بایت‌های manifest ورودی را؛ `duplicates.json` تاریخچهٔ dedup را؛ و `data_card.md` هدف/محدودیت‌ها را. برای مثال، اگر test شامل واژه‌ای باشد که در train ندیده‌ایم، encode باید `<unk>` بدهد، نه شناسهٔ تازه. اگر source یا attribution گم شود، manifest باید پیش از آموزش fail کند. یکسانی hash صرفاً هویت فایل را ثبت می‌کند و جای بررسی انسانی حقوق را نمی‌گیرد.

## ۱۶. آزمون‌های پذیرش و آنچه واقعاً اثبات می‌کنند

۲۰ آزمون واحد پروژه، ورودی JSONL خراب، فیلدهای لازم، مجوز خارج از allowlist، شرط attribution در CC BY، تاریخ نادرست، email/phone الگووار، Unicode NFC، حفظ نیم‌فاصله، تکرار دقیق، هم‌پوشانی گروه‌ها، ثبات seed، تقسیم ناممکن، vocabulary train-only، `<unk>`, ذخیره/بازیابی و وجود artifactها را می‌سنجند.

آزمون موفق نمی‌گوید مجوز واقعی یک وب‌سایت درست است؛ تأیید نمی‌کند همهٔ اطلاعات شخصی پاک شده؛ paraphraseها را پیدا نمی‌کند؛ نشان نمی‌دهد گروه‌بندی برای هر سؤال علمی درست بوده؛ یا ثابت نمی‌کند مدل با این corpus مفید می‌شود. به همین دلیل acceptance criteria را جدا بنویسید: (۱) شواهد منبع/مجوز بررسی انسانی شده؛ (۲) هر رکورد schema دارد؛ (۳) duplicate audit انجام شده؛ (۴) group leakage صفر است؛ (۵) tokenizer فقط train را دیده؛ (۶) کارت داده محدودیت‌های باقی‌مانده را ثبت کرده است.

## ۱۷. خطاهای رایج و راه اصلاح

| نشانه | علت محتمل | گام بعدی |
|---|---|---|
| `outside this demo's allowlist` | مجوز ناشناخته یا بیرون از سیاست کد | توقف؛ شروط منبع را بررسی کنید، allowlist را بی‌تأمل گسترش ندهید |
| split validation یا test خالی است | کمتر از سه گروه یا گروه‌بندی نامناسب | داده/گروه مستقل بیشتری جمع کنید؛ گروه را برای درصدسازی نشکنید |
| OOV test بالا است | دامنه/املا متفاوت یا vocab کوچک | خطاها را تحلیل کنید؛ train-only tokenizer را حفظ و vocab/BPE را با validation تنظیم کنید |
| نسبت split متفاوت از ۸۰/۱۰/۱۰ است | تعداد/اندازهٔ گروه‌ها نامتوازن است | شمار گروه و رکورد را جدا گزارش کنید؛ درصد را تضمین فرض نکنید |
| تکرارها پس از split پیدا می‌شوند | dedup بعد از split انجام شده یا معیار فقط hash فایل بوده | متن normalize و dedup را پیش از split اجرا کنید؛ near-duplicate را با نمونه‌های دستی audit کنید |
| پیام privacy scanner ظاهر می‌شود | الگوی ایمیل/شماره یا متن حساس | متن را انسانی بررسی کنید؛ اطلاعات لازم‌نبوده را حذف/ماسک کنید؛ اسکنر را دور نزنید |

هر تغییر پاک‌سازی می‌تواند تنوع و تعداد را عوض کند. قبل/بعد را با شمارش و چند نمونه ثبت کنید؛ اگر خطا برای فارسی یا گونهٔ خاص نامتناسب است، فیلتر را بازطراحی کنید نه اینکه فقط آستانه را کورکورانه بالا ببرید.

## ۱۸. تمرین و چالش مهندسی

۱. برای ده رکورد از سه منبع مجاز، manifestی بسازید و برای هر مجوز پیوند، attribution، زمان بررسی و یادداشت شواهد ثبت کنید. ۲. دو نسخهٔ فاصله‌گذاری متفاوت از یک متن وارد کنید؛ نشان دهید چرا hash فایل به‌تنهایی آن‌ها را یکی نمی‌کند. ۳. دو بند از یک سند را در یک `group_id` بگذارید و ثابت کنید split گروهی آن‌ها را جدا نمی‌کند. ۴. واژهٔ منحصربه‌فردی فقط در test اضافه کنید و نشان دهید vocabulary آن را نمی‌شناسد. ۵. فارسی دارای نیم‌فاصله/اعراب/اعداد را با NFC و یک نرمال‌ساز تهاجمی مقایسه کنید؛ هر تغییری را با نمونه و پیامد توضیح دهید. ۶. کارت داده را با ۵ مورد «نامعلوم» و ۳ محدودیت واقعی تکمیل کنید. ۷. یک روش near-duplicate پیشنهاد دهید؛ روی حداقل ۱۰ جفت مثبت و ۱۰ منفی دستی threshold آن را ارزیابی کنید. ۸. مسئله‌ای طراحی کنید که split زمانی یا نویسنده‌ای از تقسیم تصادفی مناسب‌تر باشد.

**معیار قبولی:** تست‌ها سبزند؛ هیچ گروهی از هر دو سوی مرز split عبور نمی‌کند؛ منبع و شروط هر رکورد قابل‌پیگیری است؛ vocabulary از train ساخته شده؛ حداقل یک شکست/محدودیت مستند شده؛ و کارت داده طوری نوشته شده که خواننده بفهمد این مجموعه برای چه استفاده‌ای مناسب **نیست**. پاسخ نمونهٔ تمرین‌ها در فایل پاسخ‌نامه پیوندشده در بخش ۱ قرار دارد.

### واژه‌نامهٔ کوتاه

- **Manifest:** فهرست نسخه‌دار رکوردها و فرادادهٔ منشأ/مجوز آن‌ها.
- **group_id:** شناسهٔ واحد وابستگی که باید در یک split باقی بماند.
- **Split:** بخش train، validation یا test با نقش ارزیابی متفاوت.
- **واژگان (vocabulary):** فهرست توکن‌ها و شناسه‌های tokenizer.
- **Train-only fit:** ساخت واژگان فقط از دادهٔ آموزش برای جلوگیری از نشت.

## ۱۹. منابع و وضعیت دانش تا ۵ نوامبر ۲۰۲۶

منابع اولیه و مستندات رسمی در این فصل برای پشتیبانی از چهار تصمیم استفاده شده‌اند: منشأ و مستندسازی داده [۱، ۴، ۹]؛ مجوز و محدودیت حقوق دیگر [۲، ۳]؛ split/پردازش و tokenizer [۶، ۷]؛ و ریسک leakage [۵]. DataComp در setting تصویر–متن، تمرکز روی ساخت مجموعه و فیلتر را جدا از تغییر کد/بودجهٔ آموزش مطالعه می‌کند [۸]؛ نتیجه‌های benchmark آن را به دادهٔ فارسی یا هر وظیفهٔ زبانی تعمیم نمی‌دهیم.

تا تاریخ بازبینی، راهنمای Data Statements نسخهٔ ۳ دانشگاه واشنگتن برای طراحی و ثبت مجموعه‌های زبانی در دسترس است [۴] و مستندات زندهٔ Datasets و Tokenizers دربارهٔ پردازش splitها و ساخت/ذخیرهٔ tokenizer توضیح می‌دهند [۶، ۷]. اسناد زنده نسخه‌دار نیستند یا تغییر می‌کنند؛ پیش از استفادهٔ صنعتی، نسخهٔ کتابخانه، API و شروط داده را همان زمان کنترل کنید. این فصل روش حقوقی یا privacy جدیدی را تأیید نمی‌کند؛ ناشناخته‌ها با برچسب محدودیت حفظ شده‌اند.

1. Gebru, T. و همکاران، «Datasheets for Datasets»، CACM، 2021؛ نسخهٔ مقاله: arXiv:1803.09010، آخرین بازبینی نسخهٔ arXiv: 1 دسامبر 2021. [arXiv](https://arxiv.org/abs/1803.09010)، مراجعه ۵ نوامبر ۲۰۲۶.
2. Creative Commons، «Attribution 4.0 International (CC BY 4.0) — Deed و Legal Code»، صفحهٔ رسمیِ زنده؛ [متن رسمی](https://creativecommons.org/licenses/by/4.0/)، مراجعه ۵ نوامبر ۲۰۲۶.
3. Creative Commons، «CC0 1.0 Universal — Deed و Legal Code»، صفحهٔ رسمیِ زنده؛ [متن رسمی](https://creativecommons.org/publicdomain/zero/1.0/)، مراجعه ۵ نوامبر ۲۰۲۶.
4. McMillan-Major, A. & Bender, E. M.، «A Guide for Creating and Documenting Language Datasets with Data Statements, Schema Version 3»، University of Washington Tech Policy Lab، 2024؛ [راهنما و قالب‌ها](https://techpolicylab.uw.edu/data-statements/)، مراجعه ۵ نوامبر ۲۰۲۶.
5. Kapoor, S. & Narayanan, A.، «Leakage and the reproducibility crisis in machine-learning-based science»، *Patterns* 4(9), 100804, 2023، DOI: [10.1016/j.patter.2023.100804](https://doi.org/10.1016/j.patter.2023.100804).
6. Hugging Face، «Process — Datasets documentation»، مستندات رسمی زنده، نسخهٔ پایدار 4.8.4 در زمان بررسی؛ [راهنمای پردازش](https://huggingface.co/docs/datasets/v4.8.4/process)، مراجعه ۵ نوامبر ۲۰۲۶.
7. Hugging Face، «Quicktour — Tokenizers documentation»، مستندات رسمی زنده؛ [راهنما](https://huggingface.co/docs/tokenizers/quicktour)، مراجعه ۵ نوامبر ۲۰۲۶.
8. Gadre, S. Y. و همکاران، «DataComp: In search of the next generation of multimodal datasets»، NeurIPS Datasets and Benchmarks Track 2023؛ [arXiv:2304.14108](https://arxiv.org/abs/2304.14108).
9. Pushkarna, M., Zaldivar, A. & Kjartansson, O.، «The Data Cards Playbook: A Toolkit for Transparency in Dataset Documentation»، 2022؛ [راهنمای رسمی Google Research](https://sites.research.google/datacardsplaybook/).

## ۲۰. پیوست: کد کامل پروژه

کد زیر همان `small_corpus.py` است که در پروژه اجرا و با آزمون‌های واحد سنجیده شده؛ فایل نمونه و تست‌ها در پوشهٔ همان پروژه‌اند. پیوست عمداً از نسخهٔ آزمایش‌شدهٔ فایل تولید می‌شود تا دو نسخه از کد از هم منحرف نشوند.

```python
"""A rights-aware, deterministic tiny-text corpus pipeline for chapter 40.

Standard-library only. The sample pipeline is educational, not a legal review,
privacy guarantee, or production-quality near-duplicate detector.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import random
import re
import unicodedata
from typing import Iterable, Sequence


ALLOWED_LICENSES = frozenset({"CC0-1.0", "CC-BY-4.0", "PUBLIC-DOMAIN", "SELF-CREATED"})
REQUIRED_FIELDS = frozenset({
    "id", "group_id", "text", "source", "license", "attribution",
    "language", "acquired_at", "rights_note",
})
SPECIAL_TOKENS = ("<pad>", "<unk>", "<bos>", "<eos>")
TOKEN_PATTERN = re.compile(r"[\w\u200c]+|[^\w\s]", flags=re.UNICODE)
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(?<!\w)\+?\d[\d ().-]{7,}\d(?!\w)")
SPLIT_NAMES = ("train", "validation", "test")
NORMALIZATION_NOTE = "Unicode NFC and whitespace collapse; Persian ZWNJ retained"


def normalize_text(text: str) -> str:
    """Normalize canonical Unicode composition and whitespace conservatively."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return " ".join(unicodedata.normalize("NFC", text).split())


def sensitive_pattern_matches(text: str) -> list[str]:
    """Return heuristic flags only; absence of flags does not prove text is safe."""
    matches = []
    if EMAIL_PATTERN.search(text):
        matches.append("email-like")
    if PHONE_PATTERN.search(text):
        matches.append("phone-like")
    return matches


def _nonempty_string(record: dict, key: str, line_number: int | None) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        where = f" on line {line_number}" if line_number is not None else ""
        raise ValueError(f"field {key!r} must be a non-empty string{where}")
    return value.strip()


def validate_record(record: object, line_number: int | None = None) -> dict:
    """Validate required provenance fields and return a normalized copy."""
    where = f"line {line_number}: " if line_number is not None else ""
    if not isinstance(record, dict):
        raise ValueError(f"{where}each JSONL row must be an object")
    missing = sorted(REQUIRED_FIELDS - record.keys())
    if missing:
        raise ValueError(f"{where}missing required fields: {', '.join(missing)}")

    checked = dict(record)
    for key in REQUIRED_FIELDS - {"text"}:
        checked[key] = _nonempty_string(checked, key, line_number)

    if checked["license"] not in ALLOWED_LICENSES:
        raise ValueError(
            f"{where}license {checked['license']!r} is outside this demo's allowlist; "
            "review rights and update policy deliberately"
        )
    if checked["license"] == "CC-BY-4.0":
        if not checked["attribution"] or not checked["source"].startswith(("https://", "http://")):
            raise ValueError(f"{where}CC-BY-4.0 rows require an attribution and source URL")
    if checked["license"] == "SELF-CREATED" and not checked["rights_note"]:
        raise ValueError(f"{where}self-created rows need a rights_note")

    try:
        date.fromisoformat(checked["acquired_at"][:10])
    except (TypeError, ValueError):
        raise ValueError(f"{where}acquired_at must begin with an ISO date such as 2026-11-05") from None

    normalized = normalize_text(checked["text"])
    if not normalized:
        raise ValueError(f"{where}text is empty after normalization")
    matches = sensitive_pattern_matches(normalized)
    if matches:
        raise ValueError(
            f"{where}possible sensitive pattern {', '.join(matches)}; review and redact "
            "before adding text (the heuristic is not exhaustive)"
        )
    checked["text"] = normalized
    checked["normalized_text_sha256"] = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return checked


def load_manifest(path: str | Path) -> list[dict]:
    """Read UTF-8 JSONL and validate it without fetching external resources."""
    path = Path(path)
    rows: list[dict] = []
    seen_ids: set[str] = set()
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_number}: {exc.msg}") from exc
            row = validate_record(raw, line_number)
            if row["id"] in seen_ids:
                raise ValueError(f"duplicate record id {row['id']!r} on line {line_number}")
            seen_ids.add(row["id"])
            rows.append(row)
    if not rows:
        raise ValueError(f"manifest {path} contains no records")
    return rows


def deduplicate_records(records: Sequence[dict]) -> tuple[list[dict], list[dict]]:
    """Remove exact normalized-text duplicates while preserving an audit trail."""
    unique: list[dict] = []
    first_by_hash: dict[str, dict] = {}
    duplicates: list[dict] = []
    for record in records:
        normalized = normalize_text(record["text"])
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        first = first_by_hash.get(digest)
        if first is None:
            copy = dict(record)
            copy["text"] = normalized
            copy["normalized_text_sha256"] = digest
            first_by_hash[digest] = copy
            unique.append(copy)
        else:
            duplicates.append({
                "duplicate_id": record["id"],
                "kept_id": first["id"],
                "reason": "exact normalized text hash matched",
                "duplicate_source": record["source"],
                "kept_source": first["source"],
                "duplicate_group_id": record["group_id"],
                "kept_group_id": first["group_id"],
                "duplicate_license": record["license"],
                "kept_license": first["license"],
                "duplicate_attribution": record["attribution"],
                "kept_attribution": first["attribution"],
                "duplicate_record_metadata": {key: value for key, value in record.items() if key != "text"},
                "kept_record_metadata": {key: value for key, value in first.items() if key != "text"},
                "normalized_text_sha256": digest,
            })
    return unique, duplicates


def _group_counts(group_count: int, fractions: Sequence[float]) -> list[int]:
    if len(fractions) != 3 or any(not isinstance(x, (int, float)) for x in fractions):
        raise ValueError("fractions must contain train, validation, test values")
    values = [float(x) for x in fractions]
    if any(not math.isfinite(x) or x <= 0 for x in values) or not math.isclose(sum(values), 1.0, abs_tol=1e-9):
        raise ValueError("split fractions must be positive and sum to 1")
    raw = [group_count * x for x in values]
    counts = [math.floor(x) for x in raw]
    remainder_order = sorted(range(3), key=lambda i: (raw[i] - counts[i], -i), reverse=True)
    for i in remainder_order[: group_count - sum(counts)]:
        counts[i] += 1
    # A tiny corpus must still reserve at least one independent group per split.
    for i in range(3):
        if counts[i] == 0:
            donors = [j for j in range(3) if counts[j] > 1]
            if not donors:
                raise ValueError("at least three distinct groups are required for train/validation/test")
            donor = max(donors, key=lambda j: counts[j])
            counts[donor] -= 1
            counts[i] += 1
    return counts


def split_by_group(
    records: Sequence[dict],
    fractions: Sequence[float] = (0.8, 0.1, 0.1),
    seed: int = 40,
) -> tuple[dict[str, list[dict]], dict[str, list[str]]]:
    """Split by source/story group so related records never cross partitions."""
    groups = sorted({record["group_id"] for record in records})
    if len(groups) < 3:
        raise ValueError("at least three distinct groups are required for train/validation/test")
    counts = _group_counts(len(groups), fractions)
    shuffled = list(groups)
    random.Random(seed).shuffle(shuffled)
    assignment: dict[str, str] = {}
    offset = 0
    group_membership: dict[str, list[str]] = {}
    for name, count in zip(SPLIT_NAMES, counts):
        current = shuffled[offset: offset + count]
        offset += count
        group_membership[name] = sorted(current)
        assignment.update({group_id: name for group_id in current})
    splits = {name: [] for name in SPLIT_NAMES}
    for record in records:
        splits[assignment[record["group_id"]]].append(record)
    return splits, group_membership


def tokenize_words(text: str) -> list[str]:
    """A deliberately simple Unicode word/punctuation tokenizer; keeps ZWNJ."""
    return TOKEN_PATTERN.findall(normalize_text(text))


def train_word_vocabulary(
    training_texts: Iterable[str],
    min_frequency: int = 1,
    max_vocab_size: int = 10_000,
) -> list[str]:
    """Learn a deterministic word-level vocabulary from training texts only."""
    if min_frequency < 1:
        raise ValueError("min_frequency must be at least 1")
    if max_vocab_size < len(SPECIAL_TOKENS):
        raise ValueError(f"max_vocab_size must be at least {len(SPECIAL_TOKENS)}")
    counts: Counter[str] = Counter()
    for text in training_texts:
        counts.update(tokenize_words(text))
    candidates = [
        (token, frequency)
        for token, frequency in counts.items()
        if token not in SPECIAL_TOKENS and frequency >= min_frequency
    ]
    candidates.sort(key=lambda item: (-item[1], item[0]))
    room = max_vocab_size - len(SPECIAL_TOKENS)
    return list(SPECIAL_TOKENS) + [token for token, _ in candidates[:room]]


class SimpleWordTokenizer:
    """Small educational tokenizer; decoding joins tokens, not original spacing."""

    def __init__(self, vocabulary: Sequence[str]):
        self.vocabulary = list(vocabulary)
        if self.vocabulary[:len(SPECIAL_TOKENS)] != list(SPECIAL_TOKENS):
            raise ValueError("vocabulary must start with the four declared special tokens")
        if len(self.vocabulary) != len(set(self.vocabulary)):
            raise ValueError("vocabulary tokens must be unique")
        self.token_to_id = {token: index for index, token in enumerate(self.vocabulary)}

    @classmethod
    def train(
        cls,
        training_texts: Iterable[str],
        min_frequency: int = 1,
        max_vocab_size: int = 10_000,
    ) -> "SimpleWordTokenizer":
        return cls(train_word_vocabulary(training_texts, min_frequency, max_vocab_size))

    def encode(self, text: str, add_bos: bool = True, add_eos: bool = True) -> list[int]:
        ids = [self.token_to_id["<bos>"]] if add_bos else []
        ids.extend(self.token_to_id.get(token, self.token_to_id["<unk>"]) for token in tokenize_words(text))
        if add_eos:
            ids.append(self.token_to_id["<eos>"])
        return ids

    def decode(self, ids: Iterable[int], skip_special: bool = True) -> str:
        tokens = []
        for token_id in ids:
            if not isinstance(token_id, int) or token_id < 0 or token_id >= len(self.vocabulary):
                raise ValueError(f"token id {token_id!r} is outside this vocabulary")
            token = self.vocabulary[token_id]
            if skip_special and token in {"<pad>", "<bos>", "<eos>"}:
                continue
            tokens.append(token)
        return " ".join(tokens)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "format_version": 1,
            "kind": "educational-word-level-tokenizer",
            "normalization": NORMALIZATION_NOTE,
            "special_tokens": list(SPECIAL_TOKENS),
            "vocabulary": self.vocabulary,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "SimpleWordTokenizer":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("format_version") != 1 or payload.get("kind") != "educational-word-level-tokenizer":
            raise ValueError("unsupported tokenizer file format")
        if payload.get("special_tokens") != list(SPECIAL_TOKENS):
            raise ValueError("special token contract does not match this implementation")
        return cls(payload["vocabulary"])


def _write_jsonl(path: Path, rows: Sequence[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _write_data_card(path: Path, summary: dict) -> None:
    licenses = ", ".join(f"`{name}`: {count}" for name, count in sorted(summary["license_counts"].items()))
    lines = [
        "# کارت دادهٔ نمونهٔ فصل ۴۰",
        "",
        "- **هدف:** ساخت ورودی کوچک و قابل‌بازتولید برای آموزش آزمایشی فصل ۴۱؛ نه benchmark و نه دادهٔ مناسب محصول.",
        "- **ترکیب:** متن‌های فارسی خودنگاشتهٔ نمونه؛ هیچ فایل یا صفحهٔ وبی در اجرای پیش‌فرض دریافت نمی‌شود.",
        f"- **نسخهٔ pipeline:** 1؛ تعداد رکوردهای پذیرفته‌شده پس از حذف تکرار: {summary['retained_records']}.",
        f"- **هش دقیق فایل manifest (SHA-256):** `{summary['input_manifest_sha256']}`؛ این هش هویت بایت‌های ورودی را ثبت می‌کند و مجوز یا منشأ حقوقی را اثبات نمی‌کند.",
        f"- **مجوزهای ثبت‌شده در manifest:** {licenses or 'هیچ'}.",
        "- **پاک‌سازی:** Unicode NFC و فشرده‌سازی whitespace؛ نیم‌فاصله حفظ می‌شود؛ متن خام این نمونه در `sample_corpus.jsonl` می‌ماند.",
        f"- **تقسیم:** گروه منبعی با seed={summary['seed']}؛ نسبت‌ها برای نمونهٔ کوچک تقریبی‌اند؛ گروه‌ها بین splitها مشترک نیستند.",
        "- **واژگان:** فقط از متن train ساخته شده؛ validation/test برای fit کردن tokenizer استفاده نشده‌اند.",
        "- **حریم خصوصی:** آشکارساز ایمیل/تلفن چند الگوی ساده را رد می‌کند، اما جامع نیست؛ بررسی انسانی پیش از هر استفاده لازم است.",
        "- **محدودیت‌ها:** نمونه کوچک و خودساخته است؛ اندازه/پوشش زبان را نمایندگی نمی‌کند؛ حذف تکرار نزدیک و بررسی مجوز خودکار نیست.",
        "- **کاربرد مجاز پروژه:** تمرین pipeline محلی. برای توزیع یا استفادهٔ دیگر، حقوق، attribution، حریم خصوصی و شرایط منبع را جداگانه بررسی کنید.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def prepare_dataset(
    manifest_path: str | Path,
    output_dir: str | Path,
    seed: int = 40,
    fractions: Sequence[float] = (0.8, 0.1, 0.1),
    min_frequency: int = 1,
    max_vocab_size: int = 10_000,
) -> dict:
    """Run validation, exact deduplication, group splitting, and train-only vocab fit."""
    manifest_path = Path(manifest_path)
    manifest_sha256 = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    records = load_manifest(manifest_path)
    unique, duplicates = deduplicate_records(records)
    splits, group_membership = split_by_group(unique, fractions=fractions, seed=seed)
    tokenizer = SimpleWordTokenizer.train(
        (record["text"] for record in splits["train"]),
        min_frequency=min_frequency,
        max_vocab_size=max_vocab_size,
    )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in splits.items():
        _write_jsonl(output_dir / f"{name}.jsonl", rows)
    tokenizer.save(output_dir / "vocab.json")
    (output_dir / "duplicates.json").write_text(
        json.dumps(duplicates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    license_counts = dict(sorted(Counter(row["license"] for row in unique).items()))
    summary = {
        "pipeline_version": 1,
        "seed": seed,
        "normalization": NORMALIZATION_NOTE,
        "input_manifest_sha256": manifest_sha256,
        "input_records": len(records),
        "retained_records": len(unique),
        "exact_duplicates_removed": len(duplicates),
        "split_counts": {name: len(rows) for name, rows in splits.items()},
        "split_group_counts": {name: len(group_membership[name]) for name in SPLIT_NAMES},
        "split_groups": group_membership,
        "license_counts": license_counts,
        "tokenizer_vocabulary_size": len(tokenizer.vocabulary),
        "tokenizer_fit_split": "train",
        "sensitive_pattern_scan": "heuristic email/phone patterns only; manual review still required",
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_data_card(output_dir / "data_card.md", summary)
    return summary


def main() -> None:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Prepare a tiny rights-documented text corpus")
    parser.add_argument("--manifest", type=Path, default=root / "sample_corpus.jsonl")
    parser.add_argument("--output", type=Path, default=root / "build")
    parser.add_argument("--seed", type=int, default=40)
    args = parser.parse_args()
    summary = prepare_dataset(args.manifest, args.output, seed=args.seed)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```
