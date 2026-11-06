# جلد سوم، فصل ۱۱ — Corpus، مجوز، کیفیت و جلوگیری از آلودگی ارزیابی

**نگاشت:** فصل محلی ۱۱ جلد سوم = فصل سراسری ۴۳. **تاریخ مرجع و بازبینی منابع: ۶ نوامبر ۲۰۲۶.** فصل ۴۰ یک پیکرهٔ کوچکِ خودنوشته، حذف تکرار دقیق، split گروهی و واژگان train-only ساخت؛ فصل ۴۱ یک baseline زبانی را روی همان نمونه آموزش داد؛ فصل ۴۲ Mini GPT را از نظر شکل و بودجه طراحی کرد. این فصل دروازهٔ «آیا این داده را با شواهد و کیفیت کافی وارد فرایند می‌کنیم؟» را گسترش می‌دهد: زنجیرهٔ منشأ و شروط استفاده، فیلترهای قابل‌دفاع، تکرارهای نزدیک و هم‌پوشانی با ارزیابی. این پروژه نه پیکرهٔ واقعی گردآوری می‌کند، نه داده را برای آموزش صادر می‌کند و نه مجوز صادر می‌کند.

**پیش‌نیاز:** manifest و group split فصل ۴۰؛ تفاوت train، validation و test در فصل ۴۱؛ بودجهٔ Mini GPT و طراحی داده در فصل ۴۲. **خروجی:** بتوانید یک ممیزی بازتولیدپذیر بنویسید که برای هر سند «از کجا آمد؟ چه نسخه‌ای است؟ برای چه استفاده‌ای بررسی شده؟ چه چیزی را پرچم زدیم؟ چه چیزی هنوز نامعلوم است؟» را جدا جواب دهد.

![شکل ۳-۱۱-۱ — دروازهٔ ممیزی پیکره: منشأ هر منبع با نسخه و شواهد حقوق ثبت می‌شود؛ کیفیت و پوشش با هدف وظیفه سنجیده می‌شود؛ نامزدهای تکرار و هم‌پوشانی ارزیابی به بازبینی می‌روند؛ تصمیم انسانی، دلیل و نسخه ثبت می‌شوند. هیچ شناسهٔ مجوز، امتیاز کیفیت یا match سطحی به‌تنهایی مجوز، کیفیت یا نبود آلودگی را ثابت نمی‌کند.](assets/images/babak-ai/v3-ch11-corpus-audit.webp)

**شکل ۳-۱۱-۱ —** مسیر ممیزی از منشأ تا انتشار. فلگ‌ها «سرنخ برای بررسی» هستند، نه دستور حذف یا مجوز خودکار. مقایسهٔ فیلترها باید روی داده و ارزیابی همان وظیفه انجام شود.

## ۱. از «مدل کوچک» به «پیکرهٔ پاسخ‌گو»

در فصل ۴۲ با این سؤال روبه‌رو شدیم که مدل چندپارامتری، با چه context و بودجه‌ای آزمایش شود. اما اگر منشأ داده نامعلوم باشد، تعداد پارامتر دقیق یا mask علّی درست، اعتبار آزمایش را نجات نمی‌دهد. یک corpus صرفاً پوشه‌ای از متن نیست؛ محصول زنجیره‌ای از منبع‌ها، نسخه‌ها، انتخاب‌ها، تبدیل‌ها، مجوزها، تصمیم‌های حذف و تقسیم‌هاست.

فصل ۴۰ عمدتاً یک مثال کوچک و خودنوشته را آماده کرد. آن را دوباره پیاده نمی‌کنیم. این فصل روی دردسرهایی تمرکز دارد که در مقیاس چند منبعی ظاهر می‌شوند: برچسب مجوزی که از صفحهٔ میزبان به اشتباه به متن‌های upstream تعمیم داده شده؛ فیلتر زبانی که گونه‌ای کم‌منبع را بیش از حد حذف می‌کند؛ دو نسخهٔ نزدیک از یک سند که در دو split می‌افتند؛ یا سؤال benchmark که پیش از ارزیابی در corpus آموزشی آمده است.

«آماده برای بررسی» با «آمادهٔ آموزش» یا «مجاز برای هر کاربرد» یکی نیست. برای نمونهٔ این فصل خروجی پروژه فقط ledger ممیزی است؛ نه split تازه، نه vocabulary، نه مدل و نه تأیید حقوق.

## ۲. واحد داده و کاربرد را پیش از انتخاب منبع تعریف کنیم

واحد ممیزی می‌تواند یک صفحه، سند، بند، پیام، جفت پرسش‌وپاسخ یا قطعهٔ پس از chunking باشد. اگر قرار است هم‌پوشانی بندها یا split گروهی را بسنجیم، تنها نگه‌داشتن نام فایل کافی نیست؛ باید بدانیم هر قطعه از کدام سند مادر و نسخه آمده است. «زبان فارسی» نیز هدف کافی نیست: دامنه، گونه، بازهٔ زمانی، سبک، سطح تخصص، کاربرد موردنظر و کاربردهای خارج از دامنه را تعیین کنید.

پیش از گردآوری، مختصر بنویسید: چه نوع تعمیمی را می‌خواهیم؟ کدام موضوع‌ها/گونه‌ها باید حضور داشته باشند؟ کدام خطاها یا داده‌ها برای این وظیفه پذیرفتنی نیستند؟ آیا corpus قرار است فقط به‌صورت محلی استفاده شود، بازتوزیع شود یا برای آموزش مدلی به کار رود که وزن‌هایش منتشر می‌شود؟ شروط مجاز بودن ممکن است به همین کاربرد نهایی وابسته باشد؛ نام dataset به‌تنهایی پاسخ نمی‌دهد.

## ۳. مجوز، منبع و حقوق همهٔ لایه‌ها را جدا کنیم

یک برچسب `license` در کارت یک بسته، لزوماً وضعیت همهٔ اجزای درون آن را نشان نمی‌دهد. بسته می‌تواند چند dataset upstream، اسناد با نویسنده‌های مختلف، metadata تولیدشده، annotation یا متن جمع‌آوری‌شده از پلتفرم را کنار هم بگذارد. مجوزِ فایل بسته با مجوزِ هر اثر منبع، شروط سرویس یا حقوقی مانند privacy/publicity یکی نیست. همچنین «دیدن در وب»، «دانلودشدن» و «اجازهٔ آموزش یا بازتوزیع» سه گزارهٔ متفاوت‌اند.

شناسه‌های SPDX می‌توانند نام استاندارد مجوز را کوتاه و قابل‌پردازش کنند؛ خود شناسه، مالکیت، تطبیق اثر با مجوز یا جواز استفادهٔ خاص را ثابت نمی‌کند [۱]. برای نمونه، deed رسمی CC BY 4.0 شرط credit، پیوند به مجوز و اعلام تغییرات را بیان می‌کند، اما هشدار می‌دهد که ممکن است حقوق دیگری مانند privacy، publicity یا moral rights جداگانه لازم باشند [۲]. این فصل مشاورهٔ حقوقی نیست: اگر upstream، صاحب حق، متن شروط یا دامنهٔ کاربرد روشن نیست، وضعیت را «حل‌نشده» ثبت کنید و پیش از استفاده متوقف شوید.

ممیزی Longpre و همکاران روی بیش از ۱۸۰۰ مجموعهٔ متنیِ پرکاربرد، مشکلات جدیِ انتساب و برچسب‌گذاری را در همان مجموعهٔ بررسی‌شده گزارش کرد؛ از جمله حذف یا طبقه‌بندی نادرست license روی میزبان‌ها [۳]. این یافته به همهٔ مخزن‌ها و همهٔ مجوزها تعمیم مستقیم ندارد؛ اما دلیل خوبی است که metadata پلتفرم را تنها شاهد خود نگیریم.

## ۴. منشأ را به‌شکل گرافِ تبدیل‌ها ثبت کنیم

برای هر رکورد باید بتوان از نسخهٔ مصرف‌شده به منبع upstream برگشت و مسیر تبدیل را جلو رفت. یک گراف ساده چنین گره‌هایی دارد: `source`، snapshot یا فایل خام، رکورد، نسخهٔ پردازش‌شده، گروه/خوشهٔ تکرار، split، نسخهٔ corpus و در نهایت اجرای آموزش. یال‌ها مشخص می‌کنند «از این منبع آمده»، «با این کد فیلتر شد» یا «به این نسخه/مدل وارد شد».

برای نگهداری این مسیر، در کنار `source_id` و `record_id`، نسخه یا تاریخ snapshot، URI دقیق در حد مجاز، hash فایل، commit/نسخهٔ pipeline، تنظیمات فیلتر، hash خروجی و فهرست شناسه‌های حذف‌شده را نگه دارید. Hash تغییر بایت را آشکار می‌کند، اما هویت منبع، مجوز یا بی‌خطر بودن را اثبات نمی‌کند؛ همچنین hash یک جملهٔ کوتاه ممکن است با حدس‌زدن متن قابل تطبیق باشد. روی محتوای خام حساس، سیاست دسترسی و نگهداری جدا لازم است.

## ۵. شواهد حقوق و «قصد استفاده» را در manifest ثبت کنیم

manifest یک جدول فهرست منابع نیست؛ باید هم نتیجهٔ فعلی و هم شواهدی را که تصمیم بر آن تکیه دارد نشان دهد. نمونهٔ فیلدها:

| فیلد | چه چیزی را روشن می‌کند؟ |
|---|---|
| `source_id`, `source_uri`, `source_version` | منبع مادر، نشانی/شناسه و snapshot دقیق |
| `license_expression`, `license_url` | عبارت ثبت‌شده و متن/نسخه‌ای که بررسی شده |
| `rights_review_status`, `rights_evidence_ref` | pending، ادعای بازبینی انسانی، یا کنارگذاری؛ مسیر شاهد |
| `intended_use`, `reviewed_at`, `reviewed_by` | کاربردی که بررسی شده و زمان/مسئول تصمیم |
| `language`, `group_id`, `transform_version` | ویژگی‌های ممیزی و رابطهٔ سندهای وابسته |
| `decision`, `reason`, `record_hash` | نگه‌داشتن/hold/کنارگذاری با توضیح و شناسهٔ پایدار |

«بررسی شد» فقط یک ادعای ثبت‌شده است، نه خروجی اثبات‌شدهٔ برنامه. مجوزهای پیچیده، متن‌های چندمنبعی، شروط توزیع مدل، رضایت و قواعد سازمانی باید توسط مسئول مناسب بررسی شوند. فیلد خالی، `NOASSERTION`، URL نامعلوم یا status برابر `pending` باید موجب توقف/صف بررسی شود؛ تبدیل آن‌ها به `unknown-but-allowed` راه‌حل نیست.

## ۶. کیفیت را برداری از هدف‌ها بدانیم، نه نمرهٔ جادویی

«کیفیت» فقط متن بی‌غلط نیست. بسته به وظیفه، ابعاد مهم می‌توانند ارتباط موضوعی، صحت، تازگی، خوانایی، تنوع سبک، پوشش زبان/گونه، توازن منبع، نسبت کد/جدول/متن، ایمنی، privacy، حقوق و تکرار باشند. اگر هدف فهم فارسی محاوره‌ای است، فیلترِ «جملهٔ رسمی‌تر بهتر» ممکن است دادهٔ مهم را حذف کند؛ برای بازیابی اطلاعات حقوقی، منبع و تاریخ ممکن است از سبک مهم‌تر باشند.

گزارش پوشش را فقط با تعداد سند نسنجید. سندهای طولانی‌تر سهم توکنی بیشتری می‌گیرند. اگر منبع `s` در رکوردها مجموعاً `t_s` توکن داشته باشد و کل corpus `T` توکن داشته باشد، سهم آن منبع از budget برابر است با:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="سهم توکنی منبع s برابر مجموع توکن‌های رکوردهای همان منبع تقسیم بر کل توکن‌های corpus است">
  <mrow><msub><mi>p</mi><mi>s</mi></msub><mo>=</mo><mfrac><msub><mi>t</mi><mi>s</mi></msub><mi>T</mi></mfrac><mo>,</mo><mspace width="0.5em"/><mi>T</mi><mo>=</mo><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>N</mi></munderover><msub><mi>t</mi><mi>i</mi></msub></mrow>
</math>

این نسبت هم به tokenizer و روش chunking وابسته است؛ آن را همراه با تعداد رکوردها، گروه‌های مستقل، زبان/موضوع، تاریخ و طول‌ها گزارش کنید. هیچ histogramی به‌تنهایی نمایندگی اجتماعی یا کیفیت واقعی corpus را ثابت نمی‌کند.

## ۷. فیلتر را سیاستی آشکار و برگشت‌پذیر کنیم

فیلتر می‌تواند بر اساس اندازه/قالب، encoding، زبان، تکرار، کلمات ناخواسته، boilerplate یا classifier امتیازدهنده باشد. هر شرط را با چهار مورد ثبت کنید: هدف آن، آستانه، تعداد/سهمی که پرچم می‌گیرد، و نمونه‌های false positive/false negative که انسان بازبینی کرده است. نسخهٔ خامِ مجاز را overwrite نکنید؛ خروجی filtered را با شناسهٔ منبع و دلیل تصمیم بسازید.

در ابتدا بهتر است flag تولید شود، نه حذف قطعی. فیلتر طول ممکن است شعر، عنوان، پاسخ کوتاه یا متن گفتاری را ناعادلانه کنار بگذارد؛ واژه‌نامهٔ مسدود ممکن است نام خاص یا گویش را اشتباه حذف کند؛ language ID می‌تواند روی متن کوتاه یا آمیخته خطا کند. برای هر فیلتر، نرخ نگه‌داشتن را برحسب زبان، دامنه، منبع و ویژگی‌های اخلاقاً/قانوناً مجاز اندازه‌گیری کنید. اگر اثر نامتوازن پیدا شد، بررسی کنید آیا مسئله از threshold، متن‌استخراج، دادهٔ برچسب‌خورده یا هدف نامناسب می‌آید.

## ۸. آستانه را با ablation بسنجیم، نه با سلیقه

یک روش قابل‌دفاع: نمونهٔ کوچکِ انسانی‌برچسب‌خورده بسازید؛ تعریف «قبول/رد» را پیش از دیدن نتیجه بنویسید؛ چند threshold را مقایسه کنید؛ نمونه‌های مرزی را بررسی کنید؛ و نرخ خطا را جداگانه به تفکیک منبع/زبان گزارش دهید. برای classifier، اگر `TP` و `FP` شمار درست/غلط‌های پذیرفته‌شده باشند، precision پاسخ می‌دهد «از آنچه نگه داشتیم چند مورد مناسب‌اند؟»؛ recall پاسخ می‌دهد «از موارد مناسب چندتا را حفظ کردیم؟»:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="precision برابر TP بر TP به‌علاوه FP و recall برابر TP بر TP به‌علاوه FN است">
  <mrow><mi>precision</mi><mo>=</mo><mfrac><mi>TP</mi><mrow><mi>TP</mi><mo>+</mo><mi>FP</mi></mrow></mfrac><mo>,</mo><mspace width="0.7em"/><mi>recall</mi><mo>=</mo><mfrac><mi>TP</mi><mrow><mi>TP</mi><mo>+</mo><mi>FN</mi></mrow></mfrac></mrow>
</math>

برای آزمایش مدل نیز در صورت امکان همه‌چیز جز corpus ثابت بماند: معماری، تعداد توکن آموزش، schedule و معیارها. FineWeb و DCLM-LM نمونه‌هایی از کارهای داده‌محورند که انتخاب فیلتر/تکرار را با آزمایش و مقایسه بررسی می‌کنند، نه با فرض «حذف بیشتر همیشه بهتر است» [۴،۵]. نتایج آن‌ها به setup، منبع و مدل همان مطالعه تعلق دارند؛ threshold انگلیسی یا امتیاز classifier آن‌ها نسخهٔ آماده برای فارسی نیست. پیش‌چاپ ۲۰۲۶ «A Bitter Lesson for Data Filtering» نیز در setup پرمحاسبه/کمبود داده نتایجی به نفع فیلترنکردن گزارش می‌کند؛ چون پیش‌چاپ و وابسته به شرایط خاص است، آن را هشدار علیه نسخهٔ واحد می‌خوانیم، نه توصیهٔ عمومی [۱۰].

## ۹. تکرار دقیق، نسخهٔ تازه و تکرار نزدیک را از هم جدا کنیم

تکرار دقیق ممکن است پس از normalization یکسان شود؛ تکرار نزدیک می‌تواند تفاوت فاصله‌گذاری، قالب، عنوان، چند جمله یا نسخهٔ ترجمه‌شده داشته باشد. همچنین ممکن است یک صفحه در snapshotهای مختلف بازنشر شود، یک پاراگراف از چند سند نقل شده باشد، یا دو متن صرفاً قالب مشترک داشته باشند. این‌ها یک نوع رابطه نیستند و تصمیم حذفشان پیامد یکسان ندارد.

سه سطح را جدا گزارش کنید: URL/منبع تکراری؛ سند یا قطعهٔ دقیق؛ و شباهت متن یا معنا. در هر سطح، شناسهٔ هر دو طرف، snapshot، گروه، hash، license/evidence و دلیل بررسی را نگه دارید. اگر دو متن دقیقاً برابرند اما منشأ یا شروط متفاوت دارند، بی‌سروصدا یکی را حذف نکنید؛ شاید نسخهٔ باقی‌مانده شاهد حقوق/attribution بدتری داشته باشد.

## ۱۰. شباهت n-gram را برای triage به‌کار ببریم

یک baseline نزدیک‌تکرار می‌تواند متن را به کلمات یا قطعه‌های نویسه‌ای تقسیم کند، مجموعهٔ shingleهای `k`تایی بسازد و ضریب Jaccard را حساب کند:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="شباهت ژاکارد دو مجموعهٔ شینگل برابر اندازهٔ اشتراک تقسیم بر اندازهٔ اجتماع است">
  <mrow><mi>J</mi><mo>(</mo><msub><mi>A</mi><mi>k</mi></msub><mo>,</mo><msub><mi>B</mi><mi>k</mi></msub><mo>)</mo><mo>=</mo><mfrac><mrow><mo>|</mo><msub><mi>A</mi><mi>k</mi></msub><mo>∩</mo><msub><mi>B</mi><mi>k</mi></msub><mo>|</mo></mrow><mrow><mo>|</mo><msub><mi>A</mi><mi>k</mi></msub><mo>∪</mo><msub><mi>B</mi><mi>k</mi></msub><mo>|</mo></mrow></mfrac></mrow>
</math>

Jaccard روی کلمات در متن کوتاه یا واژگان پرتکرار حساس است؛ punctuation، ترتیب و paraphrase نیز نتیجه را عوض می‌کنند. MinHash/LSH برای یافتن نامزدها در مجموعه‌های بزرگ‌تر مفید است، اما مرحلهٔ دومِ دقیق و نمونه‌برداری انسانی همچنان لازم‌اند. Embeddingها یا مدل معنایی می‌توانند شباهت معنایی را گسترش دهند، ولی گاهی متن‌های فقط مرتبط را با duplicate اشتباه می‌گیرند و هزینه/محدودیت privacy دارند. threshold را با جفت‌های واقعاً نزدیک و جفت‌های منفی کالیبره کنید؛ یک score خودبه‌خود تصمیم حذف نیست.

## ۱۱. خوشه‌ها را پیش از split و ارزیابی به حساب آوریم

در فصل ۴۰ `group_id` برای آن بود که بندهای یک منبع مستقل از هم به train و test نروند. اکنون همین ایده را به خوشه‌های نزدیک‌تکرار تعمیم می‌دهیم: اگر چند نسخه یا برش از یک سند شناسایی شد، برای split آن‌ها را به‌عنوان یک واحد وابسته در نظر بگیرید یا یک split ازپیش‌تعریف‌شده و توضیح‌پذیر بسازید. در غیر این صورت مدل ممکن است test را به شکل نسخه‌ای در train دیده باشد.

اما «یکسان‌سازی پیش از split» به این معنی نیست که ارزیابی را وارد tokenizer یا فیلترهای انتخابی کنیم. ابتدا سیاست داده و شناسه‌های گروه را تعیین کنید؛ در pipeline آموزشی فقط corpus مجاز و splitهای تعریف‌شده را بسازید؛ سپس نسخهٔ ارزیابی را در غربال جداگانه با corpus مقایسه کنید. دادهٔ benchmark باید از تصمیم‌گیری روی validation/test خود مدل جدا بماند. روند فصل ۴۰ برای گروه‌بندی اولیه مفید است، اما تشخیص near-duplicate یک گام ممیزی اضافه است، نه جایگزین بررسی معنای `group_id`.

## ۱۲. «آلودگی» را به سه ادعای متفاوت بشکنیم

در بحث LLM، «آلودگی ارزیابی» گاهی برای سه وضعیت مختلف به کار می‌رود:

1. **هم‌پوشانی داده‌ای:** متن، پرسش، پاسخ یا بخش‌هایی از benchmark در corpus یا منبعی شناخته‌شده پیدا می‌شود.
2. **مواجههٔ مدل:** اسناد ثبت‌شده نشان می‌دهند نمونه واقعاً در یک نسخهٔ آموزش مدل بوده، با چه تکرار و چه زمانی.
3. **اثر روی امتیاز:** مواجهه باعث افزایش/کاهش نتیجهٔ اندازه‌گیری‌شده در آن مدل/وظیفه شده است.

یافتن یک n-gram در فایل corpus فقط نامزد هم‌پوشانی سطحی است؛ تضمین نمی‌کند همان فایل به مدل خاصی رسیده باشد. برعکس، پیدا نکردن عبارت هم مدل را از تماس با ترجمه، paraphrase یا منبع ناشناخته مبرا نمی‌کند. حتی مواجهه هم به‌تنهایی نمی‌گوید امتیاز چقدر تغییر می‌کند. پژوهش‌ها نرخ‌های بسیار متفاوتی را برای مدل‌ها و benchmarkهای مورد بررسی گزارش کرده‌اند، و اثر بر نمره در همهٔ benchmarkها یکسان نیست [۷]. پس گزارش باید ادعا را دقیق نام‌گذاری کند.

## ۱۳. غربال هم‌پوشانی چه چیزی را می‌بیند و چه چیزی را نه؟

روش سطحی از hash نرمال‌شده، exact match و قطعهٔ بلند n-gram شروع می‌شود. سپس می‌توان MinHash/LSH، جست‌وجوی embedding یا مقایسهٔ انسانی را برای نامزدهای نزدیک افزود. ابزارهای black-box مانند پرسش از مدل یا membership-inference فرض‌های تازه‌ای دارند؛ ممکن است به توزیع داده، رفتار مدل یا دسترسی به logits وابسته باشند. بررسی فرض‌های detector مهم است، چون بعضی روش‌ها زیر جابه‌جایی توزیع یا با متن بازنویسی‌شده کارایی ندارند [۹].

هر یافته باید نوع شاهد و نسخهٔ ابزار را ثبت کند: «exact normalized match»، «shared 8-token span»، «Jaccard بالای threshold»، «منبع upstream یکسان» یا «عضویت ثبت‌شده در manifest آموزش». نام‌هایی مانند `contaminated=true` بدون روش/نسخه/مدرک ابهام می‌سازند. rate غربال را می‌توان این‌طور نوشت:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="نرخ نامزدهای غربال برابر تعداد موارد پرچم‌خورده تقسیم بر کل موردهای ارزیابی است؛ این نرخ برآورد قطعی آلودگی مدل نیست">
  <mrow><msub><mi>r</mi><mi>screen</mi></msub><mo>=</mo><mfrac><mrow><msub><mi>n</mi><mi>flagged</mi></msub></mrow><mrow><msub><mi>n</mi><mi>evaluation</mi></msub></mrow></mfrac><mo>;</mo><mspace width="0.4em"/><msub><mi>r</mi><mi>screen</mi></msub><mo>≠</mo><msub><mi>r</mi><mi>model-exposed</mi></msub></mrow>
</math>

یک مثبت کاذب می‌تواند عبارتی رایج باشد؛ منفی کاذب می‌تواند ناشی از املای دیگر، ترجمه، بازنویسی یا متن ناقص باشد. برای ادعای میزان آلودگی، denominator، روش تطبیق، نسخهٔ benchmark، حدود دسترسی به دادهٔ آموزش و uncertainty را صریح بنویسید.

## ۱۴. طراحی ارزیابی مستقل، بدون وعدهٔ «پاک‌بودن کامل»

هنگام ساخت corpus آموزشی، benchmark نهایی را در فایل دسترسی‌محدود و جدا نگه دارید؛ از آن برای fit کردن vocabulary، تنظیم threshold یا انتخاب checkpoint استفاده نکنید. زمان انتشار/نسخهٔ دادهٔ مدل را با تاریخ benchmark مقایسه کنید، اما post-cutoff یا dynamic بودن آزمون را ضمانت ندانید: نمونه ممکن است در منبع دیگری آمده باشد، از راه API به مدل برسد یا در تغییر نسخه‌ها بازنشر شود.

یک مطالعهٔ کنترل‌شده نشان داد مواجههٔ تکراری و اندازه/حجم آموزش بر ماندگاری اثر آلودگی تعامل دارند؛ برخی نمونه‌ها در setup آن مقاله با دادهٔ تازه فراموش شدند [۸]. این یافته دلیل نمی‌شود که نشت را بی‌اهمیت بدانیم: تکرار، زمان‌بندی، هدف و مدل فرق می‌کنند، و در ارزیابی‌های دیگر اثر benchmark گزارش شده است [۷]. بهترین سیاست همچنان پیشگیری، ثبت نسخه و گزارش شفاف محدودیت است. benchmark محرمانه یا دادهٔ شخصی را به سرویس خارجی نفرستید مگر آنکه مجاز و از نظر privacy بررسی شده باشد.

## ۱۵. نسخه‌بندی و تغییرات را بخشی از dataset بدانیم

هر انتشار corpus باید شناسهٔ نسخه، ورودی‌ها/نسخهٔ upstream، commit pipeline، تنظیمات، شمار و hash خروجی‌ها، توزیع منبع/زبان/طول، تغییرات نسبت به نسخهٔ پیشین و فهرست شناسه‌های افزوده/حذف‌شده داشته باشد. «نسخه ۲» بدون changelog کافی نیست. اجرای دوباره با ورودی و کد ثابت باید حداقل manifest و آمار یکسان بسازد؛ اگر ترتیب فایل‌ها یا کتابخانه نتیجه را عوض می‌کند، همان وابستگی ثبت شود.

نسخه‌بندی به معنی نگه‌داشتن اجباری هر متن حساس برای همیشه نیست. سیاست حذف، درخواست صاحب داده، privacy و نگهداری باید با دسترسی و امنیت سازگار باشد؛ گاهی فقط tombstone یا شناسهٔ حذف در گزارش مجاز است. ذخیرهٔ artifact hash جایگزین سیاست دسترسی نیست. این فصل هیچ فایل دادهٔ وب، شخصی یا پنهانی را نمی‌گیرد؛ تمام fixtureها متن آموزشی ساخته‌شده‌اند.

## ۱۶. Data card باید نتیجهٔ فیلتر را هم شرح دهد

کارت دادهٔ فصل ۴۰ پرسش‌های منشأ، زبان، preprocessing، split و محدودیت را معرفی کرد. برای corpus نسخه‌دار، کارت را به خروجی واقعی همان نسخه وصل کنید: چه منبع‌هایی سهم دارند؟ با چه معیارهایی انتخاب یا کنار گذاشته شدند؟ هر فیلتر چند مورد را تغییر داد؟ چه گروه‌هایی کم‌نماینده‌اند؟ چطور near-duplicate و evaluation overlap بررسی شدند؟ چه چیزی هنوز نامعلوم است؟ چه کسی پاسخ‌گو و مالک به‌روزرسانی است؟

کارت خوانا، log فنی را جایگزین نمی‌کند؛ log هم کارت انسانی را. نسخهٔ مشتق‌شده باید روش، شروط و تغییراتی را که از منبع بالادستی دریافت کرده حفظ کند. پروژهٔ این فصل `data_card.md` کوتاهی می‌سازد تا خودِ آمار و محدودیت‌ها در کنار report دیده شوند؛ این کارت fixture را برای corpus واقعی کامل نمی‌کند.

## ۱۷. پروژهٔ ممیزی را اجرا کنیم

فایل‌های [پروژهٔ فصل ۴۳](book-engineering/projects/43-corpus-audit/README.md) یک manifest JSONL ساختگی، فایل ارزیابی جدا و ابزار استاندارد-library فراهم می‌کنند. هر ردیف corpus شناسهٔ منبع و نسخه، status حقوقیِ ادعاشده، کاربرد موردنظر، زبان و متن دارد. فایل `sample_evaluation.jsonl` جدا خوانده می‌شود و هرگز به لیست اسناد corpus افزوده نمی‌شود.

از ریشهٔ مخزن:

```bash
python -m unittest discover -v --start-directory book-engineering/projects/43-corpus-audit
python book-engineering/projects/43-corpus-audit/corpus_audit.py
```

یا از پوشهٔ پروژه، `python -m unittest discover -v` و `python corpus_audit.py` اجرا کنید. CLI به‌طور پیش‌فرض سه artifact را در `build/` می‌نویسد؛ build محلی در `.gitignore` است. آستانهٔ طول، Jaccard، استفادهٔ موردنظر و طول قطعهٔ پیوسته قابل تنظیم‌اند. هیچ URL دریافت نمی‌شود.

## ۱۸. خروجی نمونه را به‌عنوان فهرست کار بخوانیم

اجرای ثبت‌شده در Python 3.13.16، با کتابخانهٔ استاندارد و CPU، ۱۲ سند و ۳ ردیف ارزیابی را خواند. گزارش یک جفت exact normalized، یک نامزد نزدیک با Jaccard روی ۳-gram، و دو نامزد هم‌پوشانی ارزیابی پیدا کرد: یکی تطبیق دقیق و یکی اشتراک قطعهٔ ۸ واژه‌ای. سه رکورد heuristic flag کیفیت داشتند: متن کوتاه، نویسهٔ جایگزین و سطرهای تکراری. این موارد نگه داشته شدند تا بازبین دلیل پرچم را ببیند.

از نظر status، ۱۰ رکورد `demo-only` و یک مورد `pending` به بررسی/رفع ابهام نیاز دارند؛ یک مورد نیز در نمونه صریحاً `excluded` است. هیچ‌یک به مجوز واقعی یا تأیید آموزش تبدیل نمی‌شود. گزارش فقط ID، hash و پرچم را می‌نویسد، متن خام را به report کپی نمی‌کند و در summary می‌گوید `training_rows_exported=0`. این به‌تنهایی محرمانگی تضمین نمی‌کند: hash می‌تواند تطبیق‌پذیر باشد و فایل ورودی هنوز متن دارد.

۱۲ آزمون پروژه schema و خطاهای ورودی، status حقوق، رفتار non-destructive پرچم‌ها، جفت‌های دقیق/نزدیک، هم‌پوشانی ارزیابی، جدایی دو فایل، hash بدون متن خام، اعتبارسنجی threshold و تکرارپذیری خروجی را می‌سنجند. این آزمون‌ها صحت کامل مجوز، جامع‌بودن PII، کیفیت زبان، نبود paraphrase یا اثر benchmark بر عملکرد مدل را نمی‌سنجند.

## ۱۹. منابع و وضعیت دانش تا ۶ نوامبر ۲۰۲۶

- SPDX License List نسخهٔ 3.29.0 در ۱۶ سپتامبر ۲۰۲۶ فهرست شناسه‌ها و متن‌های مرجع خود را منتشر می‌کرد [۱]. شناسهٔ استاندارد، تصمیم حقوقی برای هر اثر و کاربرد نیست.
- Creative Commons توضیح رسمی CC BY 4.0 و متن حقوقی را جدا عرضه می‌کند؛ deed فقط خلاصهٔ ویژگی‌هاست و حقوق دیگر ممکن است باقی باشند [۲].
- Longpre و همکاران در ممیزی انتخاب‌شدهٔ مجموعه‌های instruction/alignment از ۱۸۰۰+ dataset، اهمیت provenance و خطای metadata میزبان را مستند کردند [۳]. نتیجه را به تمام corpusهای وب تعمیم ندهید.
- FineWeb (NeurIPS 2024) و DataComp-LM (NeurIPS 2024) با ablation و کنترل بهتر مقایسه نشان می‌دهند طراحی داده یک متغیر تجربی مهم است [۴،۵]. هر دو روی منابع، مدل‌ها و budget همان مقاله تمرکز دارند.
- Lee و همکاران (ACL 2022) سودهای حذف تکرار را در datasetها و مدل‌های مورد مطالعه گزارش کردند [۶]؛ اثر و threshold هنوز به وظیفه و سطح dedup وابسته است.
- Li و همکاران (Findings EMNLP 2024) در بررسی ۱۵+ مدل و شش benchmark، میزان overlap و تغییرات عملکرد متفاوتی گزارش کردند؛ وجود overlap الزاماً برای هر معیار اثر یکسان نداشت [۷]. Bordt و همکاران (ICML 2025) نیز در آزمایش کنترل‌شده نشان دادند اثر برخی مواجهه‌ها با حجم/تکرار/دادهٔ بعدی تعامل دارد [۸].
- Fu و همکاران (arXiv v3، مه ۲۰۲۵) فرض‌های detectorهای آلودگی را مرور و شکنندگی برخی رویکردهای membership inference را در شرایط بررسی‌شده مطرح کردند [۹]. Mohri، Duchi و Hashimoto (arXiv v1، مه ۲۰۲۶) در یک پیش‌چاپ دربارهٔ رژیم پرمحاسبه/کمبود داده، نتیجه‌ای مخالف فرض «همیشه بیشتر فیلتر کن» گزارش کردند [۱۰]. هر دو را در حد setup و وضعیت انتشارشان تفسیر کنید.

تاریخ مراجعه به پیوندها: ۶ نوامبر ۲۰۲۶. بازشدن پیوند یا وجود مقاله، صحت همهٔ کاربردهای آن یا تازه‌ترین‌بودن هر گزاره را به‌تنهایی ثابت نمی‌کند.

1. SPDX Project، «SPDX License List»، نسخهٔ 3.29.0، ۱۶ سپتامبر ۲۰۲۶؛ [فهرست رسمی](https://spdx.org/licenses/).
2. Creative Commons، «Attribution 4.0 International — Deed و Legal Code»، صفحهٔ رسمیِ زنده؛ [متن](https://creativecommons.org/licenses/by/4.0/).
3. Longpre, S. و همکاران، «A large-scale audit of dataset licensing and attribution in AI»، *Nature Machine Intelligence* 6, 975–987 (2024), DOI: [10.1038/s42256-024-00878-8](https://doi.org/10.1038/s42256-024-00878-8).
4. Penedo, G. و همکاران، «The FineWeb Datasets: Decanting the Web for the Finest Text Data at Scale»، *NeurIPS 2024, Datasets and Benchmarks*؛ [مقاله و چکیده](https://proceedings.neurips.cc/paper_files/paper/2024/hash/370df50ccfdf8bde18f8f9c2d9151bda-Abstract-Datasets_and_Benchmarks_Track.html), arXiv: [2406.17557](https://arxiv.org/abs/2406.17557).
5. Li, J. و همکاران، «DataComp-LM: In search of the next generation of training sets for language models»، *NeurIPS 2024, Datasets and Benchmarks*؛ [مقاله](https://proceedings.neurips.cc/paper_files/paper/2024/hash/19e4ea30dded58259665db375885e412-Abstract-Datasets_and_Benchmarks_Track.html), arXiv: [2406.11794](https://arxiv.org/abs/2406.11794).
6. Lee, K. و همکاران، «Deduplicating Training Data Makes Language Models Better»، *ACL 2022*, pp. 8424–8445, DOI: [10.18653/v1/2022.acl-long.577](https://doi.org/10.18653/v1/2022.acl-long.577).
7. Li, Y. و همکاران، «An Open-Source Data Contamination Report for Large Language Models»، *Findings of EMNLP 2024*, pp. 528–541, DOI: [10.18653/v1/2024.findings-emnlp.30](https://doi.org/10.18653/v1/2024.findings-emnlp.30).
8. Bordt, S. و همکاران، «How much can we Forget about Data Contamination?»، *ICML 2025*؛ [نسخهٔ پذیرفته‌شده و کد](https://openreview.net/forum?id=Pf0PaYS9KG).
9. Fu, Y. و همکاران، «Does Data Contamination Detection Work (Well) for LLMs? A Survey and Evaluation on Detection Assumptions»، arXiv:2410.18966v3، ۲۰۲۵؛ [متن](https://arxiv.org/abs/2410.18966).
10. Mohri, C., Duchi, J. & Hashimoto, T., «A Bitter Lesson for Data Filtering», arXiv:2605.19407v1, submitted 19 May 2026; [پیش‌چاپ](https://arxiv.org/abs/2605.19407).

## ۲۰. تمرین، معیار پذیرش و پیوند به فصل بعد

۱. برای ۲۰ سند فرضی manifestی طراحی کنید که برای هر upstream نسخه، URL مجوز، شواهد، کاربرد هدف، زمان بازبینی و status داشته باشد. پنج خانهٔ نامعلوم را به‌جای حدس، `pending` کنید. ۲. یک منبع با ۸ سند کوتاه و یک منبع با دو سند طولانی بسازید؛ سهم سندی و سهم توکنی را مقایسه کنید. ۳. دست‌کم ۲۰ جفت نزدیک و ۲۰ جفت منفی تهیه و برای دو threshold، precision/recall را گزارش کنید؛ نمونه‌های ارزیابی اصلی را برای انتخاب threshold مصرف نکنید. ۴. دو نسخهٔ یک سند با attribution یا license متفاوت اضافه کنید و نشان دهید چرا حذف «اولین نسخه» کافی نیست. ۵. یک cluster تکرار بسازید و splitی تعریف کنید که هیچ عضو آن بین train و test پخش نشود. ۶. benchmark ساختگی جدا بسازید و exact، قطعهٔ پیوسته و paraphrase را تفکیک کنید؛ توضیح دهید کدام detector paraphrase را نمی‌بیند. ۷. یک فیلتر کیفیت با دو threshold ablate کنید و تغییر شمار، منبع، زبان و مثال‌های false-positive را ثبت کنید. ۸. برای corpus نسخه‌دار یک data card بنویسید که هم تصمیم‌ها و هم ناشناخته‌ها را نشان دهد.

**معیار قبولی:** هر رکورد در حد مجاز به منبع/نسخه وصل است؛ status نامعلوم به مجوز تبدیل نشده؛ فیلترها و آستانه‌ها قابل‌بازتولیدند؛ تکرارهای وابسته بین splitها نمی‌افتند؛ benchmark از انتخاب preprocessing جداست؛ یک مورد خطا/false positive بررسی شده؛ کارت داده کاربرد، دامنه و محدودیت را به روشنی می‌گوید؛ و هیچ آزمون خودکاری به‌عنوان نظر حقوقی، تضمین privacy یا اثبات نبود آلودگی معرفی نشده است. پاسخ نمونهٔ تمرین‌ها در [پاسخ‌نامهٔ فصل ۴۳](book-engineering/answers/43-corpus-fa.md) آمده است.

**پیوند به فصل بعد:** فصل ۴۴ چرخهٔ پیش‌آموزش، نرخ یادگیری، warmup، اندازهٔ batch، پایش و checkpoint را روی دادهٔ دارای نسخه و سیاست روشن می‌آموزد. گزارش این فصل مجوز استفاده از corpus واقعی نیست.

## ۲۱. پیوست: کد کامل ممیزی آفلاین

فایل زیر همان ابزار آزموده‌شدهٔ پروژه است. این برنامه از کتابخانهٔ استاندارد Python استفاده می‌کند، URLها را واکشی نمی‌کند و هیچ داده‌ای را برای آموزش نمی‌سازد.

```python
"""Offline corpus release-screen demo for chapter 43.

This program writes a review ledger only. It does not decide whether data may
legally or ethically be used, does not delete records, and does not train a model.
It uses only Python's standard library and never fetches source URLs.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata
from typing import Sequence


REPORT_VERSION = 1
RIGHTS_STATUSES = frozenset({"demo-only", "pending", "reviewed", "excluded"})
REQUIRED_STRING_FIELDS = (
    "id", "source_id", "source_version", "captured_at", "license_expression",
    "rights_review_status", "intended_use", "language",
)
OPTIONAL_STRING_FIELDS = ("source_uri", "license_url", "rights_evidence_ref")
TOKEN_PATTERN = re.compile(r"[\w\u200c]+", flags=re.UNICODE)


def normalize_text(text: str) -> str:
    """Conservative comparison cleanup: NFC and whitespace collapse only."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return " ".join(unicodedata.normalize("NFC", text).split())


def comparison_key(text: str) -> str:
    """Case-insensitive exact-match key; punctuation and Persian letter forms stay."""
    return normalize_text(text).casefold()


def word_tokens(text: str) -> list[str]:
    """A tiny Unicode word splitter for audit examples, not a Persian tokenizer."""
    return TOKEN_PATTERN.findall(normalize_text(text).casefold())


def _require_string(row: dict, key: str, line_number: int, allow_empty: bool = False) -> str:
    value = row.get(key)
    if not isinstance(value, str):
        raise ValueError(f"line {line_number}: field {key!r} must be a string")
    value = value.strip()
    if not value and not allow_empty:
        raise ValueError(f"line {line_number}: field {key!r} must be non-empty")
    return value


def validate_corpus_record(value: object, line_number: int) -> dict:
    """Check the sample schema while retaining unresolved rights as review flags."""
    if not isinstance(value, dict):
        raise ValueError(f"line {line_number}: each corpus JSONL row must be an object")
    row = dict(value)
    for key in REQUIRED_STRING_FIELDS:
        row[key] = _require_string(row, key, line_number)
    for key in OPTIONAL_STRING_FIELDS:
        row[key] = _require_string(row, key, line_number, allow_empty=True)
    row["text"] = _require_string(row, "text", line_number, allow_empty=True)
    if row["rights_review_status"] not in RIGHTS_STATUSES:
        allowed = ", ".join(sorted(RIGHTS_STATUSES))
        raise ValueError(f"line {line_number}: rights_review_status must be one of: {allowed}")
    try:
        date.fromisoformat(row["captured_at"][:10])
    except (TypeError, ValueError):
        raise ValueError(f"line {line_number}: captured_at must begin with an ISO date, e.g. 2026-11-06") from None
    return row


def validate_evaluation_record(value: object, line_number: int) -> dict:
    """Read a separate evaluation fixture; it is never merged into the corpus."""
    if not isinstance(value, dict):
        raise ValueError(f"evaluation line {line_number}: each JSONL row must be an object")
    row = dict(value)
    row["id"] = _require_string(row, "id", line_number)
    row["text"] = _require_string(row, "text", line_number)
    return row


def _load_jsonl(path: str | Path, validator) -> list[dict]:
    path = Path(path)
    records: list[dict] = []
    seen_ids: set[str] = set()
    try:
        stream = path.open("r", encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot open {path}: {exc}") from exc
    with stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON in {path.name} line {line_number}: {exc.msg}") from exc
            record = validator(value, line_number)
            if record["id"] in seen_ids:
                raise ValueError(f"duplicate id {record['id']!r} in {path.name} line {line_number}")
            seen_ids.add(record["id"])
            records.append(record)
    if not records:
        raise ValueError(f"{path.name} contains no records")
    return records


def load_corpus(path: str | Path) -> list[dict]:
    return _load_jsonl(path, validate_corpus_record)


def load_evaluation(path: str | Path) -> list[dict]:
    return _load_jsonl(path, validate_evaluation_record)


def quality_flags(text: str, min_characters: int = 64) -> list[str]:
    """Return review signals only; no flag automatically removes a record."""
    if min_characters < 0:
        raise ValueError("min_characters must be non-negative")
    flags: list[str] = []
    cleaned = normalize_text(text)
    if not cleaned:
        flags.append("empty_after_normalization")
    if len(cleaned) < min_characters:
        flags.append("below_min_characters")
    if "\ufffd" in text:
        flags.append("replacement_character_present")

    controls = [
        character for character in text
        if unicodedata.category(character) == "Cc" and character not in "\r\n\t"
    ]
    if controls and len(controls) / max(len(text), 1) > 0.01:
        flags.append("control_character_ratio_over_1pct")

    lines = [comparison_key(line) for line in text.splitlines() if line.strip()]
    if len(lines) >= 3:
        duplicate_count = len(lines) - len(set(lines))
        if duplicate_count / len(lines) >= 0.5:
            flags.append("repeated_lines_candidate")
    return flags


def _shingles(tokens: Sequence[str], size: int = 3) -> set[tuple[str, ...]]:
    if size < 1:
        raise ValueError("shingle size must be positive")
    return {tuple(tokens[index:index + size]) for index in range(max(0, len(tokens) - size + 1))}


def jaccard_similarity(left: set[tuple[str, ...]], right: set[tuple[str, ...]]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _validate_threshold(name: str, value: float) -> float:
    if not isinstance(value, (int, float)) or not math.isfinite(value) or not 0.0 < value <= 1.0:
        raise ValueError(f"{name} must be finite and in (0, 1]")
    return float(value)


def exact_duplicate_pairs(records: Sequence[dict]) -> list[dict]:
    by_key: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        key = comparison_key(record["text"])
        if key:
            by_key[key].append(record)
    pairs = []
    for key, group in by_key.items():
        if len(group) < 2:
            continue
        ordered = sorted(group, key=lambda item: item["id"])
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        for left_index in range(len(ordered)):
            for right_index in range(left_index + 1, len(ordered)):
                pairs.append({
                    "left_id": ordered[left_index]["id"],
                    "right_id": ordered[right_index]["id"],
                    "match_type": "exact_normalized_candidate",
                    "content_sha256": digest,
                })
    return sorted(pairs, key=lambda item: (item["left_id"], item["right_id"]))


def near_duplicate_pairs(
    records: Sequence[dict], threshold: float = 0.70, min_tokens: int = 6, shingle_size: int = 3
) -> list[dict]:
    """Pairwise shingle-Jaccard candidate search for small offline examples only."""
    threshold = _validate_threshold("near-duplicate threshold", threshold)
    if min_tokens < shingle_size or shingle_size < 1:
        raise ValueError("min_tokens must be at least a positive shingle_size")
    cached = []
    for record in records:
        text_key = comparison_key(record["text"])
        tokens = word_tokens(record["text"])
        cached.append((record["id"], text_key, tokens, _shingles(tokens, shingle_size)))
    pairs = []
    for index, (left_id, left_key, left_tokens, left_shingles) in enumerate(cached):
        if len(left_tokens) < min_tokens or not left_shingles:
            continue
        for right_id, right_key, right_tokens, right_shingles in cached[index + 1:]:
            if left_key == right_key or len(right_tokens) < min_tokens or not right_shingles:
                continue
            score = jaccard_similarity(left_shingles, right_shingles)
            if score >= threshold:
                first, second = sorted((left_id, right_id))
                pairs.append({
                    "left_id": first,
                    "right_id": second,
                    "match_type": "near_duplicate_review_candidate",
                    "shingle_size": shingle_size,
                    "jaccard": round(score, 6),
                })
    return sorted(pairs, key=lambda item: (item["left_id"], item["right_id"]))


def _has_common_contiguous_window(left: Sequence[str], right: Sequence[str], window_size: int) -> bool:
    if window_size < 1 or min(len(left), len(right)) < window_size:
        return False
    right_windows = {tuple(right[index:index + window_size]) for index in range(len(right) - window_size + 1)}
    return any(
        tuple(left[index:index + window_size]) in right_windows
        for index in range(len(left) - window_size + 1)
    )


def evaluation_overlap_candidates(
    corpus: Sequence[dict],
    evaluation: Sequence[dict],
    near_threshold: float = 0.65,
    min_contiguous_tokens: int = 8,
    shingle_size: int = 3,
    min_tokens: int = 6,
) -> list[dict]:
    """Find exact, long-substring, or shingle-similarity candidates, not proof of exposure."""
    near_threshold = _validate_threshold("evaluation near-overlap threshold", near_threshold)
    if min_contiguous_tokens < 1 or shingle_size < 1 or min_tokens < shingle_size:
        raise ValueError("overlap sizes must be positive and min_tokens >= shingle_size")
    matches = []
    for benchmark in evaluation:
        benchmark_key = comparison_key(benchmark["text"])
        benchmark_tokens = word_tokens(benchmark["text"])
        benchmark_shingles = _shingles(benchmark_tokens, shingle_size)
        for document in corpus:
            document_key = comparison_key(document["text"])
            document_tokens = word_tokens(document["text"])
            match_type = None
            score = None
            if benchmark_key and benchmark_key == document_key:
                match_type = "exact_surface_overlap_candidate"
                score = 1.0
            elif _has_common_contiguous_window(benchmark_tokens, document_tokens, min_contiguous_tokens):
                match_type = "long_contiguous_overlap_candidate"
            elif (
                len(benchmark_tokens) >= min_tokens
                and len(document_tokens) >= min_tokens
                and benchmark_shingles
            ):
                similarity = jaccard_similarity(benchmark_shingles, _shingles(document_tokens, shingle_size))
                if similarity >= near_threshold:
                    match_type = "near_overlap_review_candidate"
                    score = round(similarity, 6)
            if match_type:
                matches.append({
                    "evaluation_id": benchmark["id"],
                    "corpus_id": document["id"],
                    "match_type": match_type,
                    **({"jaccard": score} if score is not None else {}),
                })
    return sorted(matches, key=lambda item: (item["evaluation_id"], item["corpus_id"], item["match_type"]))


def _rights_review(record: dict, target_use: str) -> tuple[str, list[str]]:
    status = record["rights_review_status"]
    flags: list[str] = []
    if status == "demo-only":
        flags.append("synthetic_demo_not_a_permission")
    elif status == "pending":
        flags.append("human_rights_review_pending")
    elif status == "excluded":
        flags.append("excluded_by_declared_policy")
    else:
        flags.append("human_review_claim_not_machine_verified")

    if record["license_expression"].casefold() in {"noassertion", "none", "unknown"}:
        flags.append("license_expression_unresolved")
    if not record["source_uri"]:
        flags.append("source_uri_missing")
    if not record["license_url"]:
        flags.append("license_url_missing")
    if not record["rights_evidence_ref"]:
        flags.append("rights_evidence_reference_missing")
    if record["intended_use"] != target_use:
        flags.append("intended_use_mismatch")

    if status == "excluded":
        disposition = "excluded_by_declared_policy"
    elif status == "reviewed" and len(flags) == 1:
        disposition = "review_claim_complete_but_unverified"
    elif status == "demo-only":
        disposition = "fixture_only_not_cleared"
    else:
        disposition = "hold_for_human_review"
    return disposition, sorted(flags)


def audit_records(
    corpus: Sequence[dict],
    evaluation: Sequence[dict],
    *,
    target_use: str = "pretraining",
    min_characters: int = 64,
    near_threshold: float = 0.70,
    evaluation_threshold: float = 0.65,
    min_contiguous_tokens: int = 8,
) -> tuple[dict, dict]:
    if not isinstance(target_use, str) or not target_use.strip():
        raise ValueError("target_use must be a non-empty string")
    _validate_threshold("near-duplicate threshold", near_threshold)
    _validate_threshold("evaluation near-overlap threshold", evaluation_threshold)
    if min_characters < 0 or min_contiguous_tokens < 1:
        raise ValueError("minimum lengths must be non-negative (contiguous token count must be positive)")

    rows = sorted(corpus, key=lambda record: record["id"])
    eval_rows = sorted(evaluation, key=lambda record: record["id"])
    exact_pairs = exact_duplicate_pairs(rows)
    near_pairs = near_duplicate_pairs(rows, threshold=near_threshold)
    overlap_pairs = evaluation_overlap_candidates(
        rows,
        eval_rows,
        near_threshold=evaluation_threshold,
        min_contiguous_tokens=min_contiguous_tokens,
    )

    record_rows = []
    statuses: Counter[str] = Counter()
    languages: Counter[str] = Counter()
    sources: Counter[str] = Counter()
    quality_counts: Counter[str] = Counter()
    review_required = 0
    excluded_count = 0
    for record in rows:
        disposition, rights_flags = _rights_review(record, target_use)
        flags = quality_flags(record["text"], min_characters=min_characters)
        quality_counts.update(flags)
        statuses[record["rights_review_status"]] += 1
        languages[record["language"]] += 1
        sources[record["source_id"]] += 1
        if disposition == "hold_for_human_review" or disposition == "fixture_only_not_cleared":
            review_required += 1
        if disposition == "excluded_by_declared_policy":
            excluded_count += 1
        canonical = normalize_text(record["text"])
        record_rows.append({
            "id": record["id"],
            "source_id": record["source_id"],
            "content_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            "character_count": len(canonical),
            "word_count_proxy": len(word_tokens(record["text"])),
            "rights_review_status": record["rights_review_status"],
            "rights_disposition": disposition,
            "rights_flags": rights_flags,
            "quality_flags": flags,
        })

    summary = {
        "report_version": REPORT_VERSION,
        "corpus_documents": len(rows),
        "evaluation_items": len(eval_rows),
        "rights_status_counts": dict(sorted(statuses.items())),
        "manual_rights_review_required": review_required,
        "explicitly_excluded_records": excluded_count,
        "quality_flagged_records": sum(bool(row["quality_flags"]) for row in record_rows),
        "quality_flag_counts": dict(sorted(quality_counts.items())),
        "source_counts": dict(sorted(sources.items())),
        "language_counts": dict(sorted(languages.items())),
        "exact_duplicate_pairs": len(exact_pairs),
        "near_duplicate_review_candidates": len(near_pairs),
        "evaluation_overlap_candidates": len(overlap_pairs),
        "training_rows_exported": 0,
        "automatic_training_approval": False,
        "raw_text_in_report": False,
        "thresholds": {
            "min_characters_review_flag": min_characters,
            "near_duplicate_shingle_jaccard": near_threshold,
            "evaluation_shingle_jaccard": evaluation_threshold,
            "minimum_contiguous_evaluation_tokens": min_contiguous_tokens,
        },
    }
    report = {
        "report_version": REPORT_VERSION,
        "purpose": "offline review ledger; not legal approval, not a training export",
        "comparison_normalization": "Unicode NFC and whitespace collapse; exact key casefolds; punctuation retained",
        "target_use_claimed_by_policy": target_use,
        "automatic_training_approval": False,
        "raw_text_in_report": False,
        "records": record_rows,
        "exact_duplicate_candidates": exact_pairs,
        "near_duplicate_candidates": near_pairs,
        "evaluation_overlap_candidates": overlap_pairs,
        "summary": summary,
    }
    return report, summary


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def build_data_card(summary: dict) -> str:
    thresholds = summary["thresholds"]
    status_lines = [f"- `{name}`: {count}" for name, count in summary["rights_status_counts"].items()]
    quality_lines = [f"- `{name}`: {count}" for name, count in summary["quality_flag_counts"].items()] or ["- هیچ پرچم کیفیتی در این اجرای نمونه ثبت نشد."]
    return "\n".join([
        "# کارت ممیزی نمونهٔ فصل ۴۳",
        "",
        "> این سند فقط گزارش یک fixture آموزشی است؛ مجوز واقعی، رضایت، ناشناس‌سازی، کیفیت زبانی یا آماده‌بودن برای آموزش را تأیید نمی‌کند.",
        "",
        "## هدف و دامنه",
        "",
        f"- ردیف‌های پیکره: {summary['corpus_documents']}؛ موارد ارزیابی جدا: {summary['evaluation_items']}",
        "- دامنهٔ ادعاشده در سیاست نمونه: پیش‌آموزش؛ هیچ ردیفی از این fixture به مدل صادر نمی‌شود.",
        "- همهٔ جمله‌ها برای نمایش کد ساخته شده‌اند؛ `demo-only` مجوز نشر یا آموزش نیست.",
        "",
        "## منشأ و بررسی حقوق",
        "",
        *status_lines,
        f"- نیازمند بررسی انسانی طبق status/metadata نمونه: {summary['manual_rights_review_required']}",
        f"- صریحاً کنارگذاشته‌شده در نمونه: {summary['explicitly_excluded_records']}",
        "- برنامه متن مجوز را تفسیر یا URL را دریافت نمی‌کند و هیچ حق استفاده‌ای اعطا نمی‌کند.",
        "",
        "## کیفیت و تکرار",
        "",
        f"- ردیف‌های دارای دست‌کم یک heuristic flag: {summary['quality_flagged_records']}",
        *quality_lines,
        f"- پرچم کوتاهی متن از {thresholds['min_characters_review_flag']} نویسه کمتر؛ این فقط آستانهٔ تمرین است.",
        f"- exact duplicate candidate pairs: {summary['exact_duplicate_pairs']}",
        f"- near-duplicate review candidates (Jaccard روی {3}-gramها، threshold={thresholds['near_duplicate_shingle_jaccard']:.2f}): {summary['near_duplicate_review_candidates']}",
        "- هیچ رکوردی خودکار حذف یا ادغام نشده است.",
        "",
        "## آلودگی ارزیابی",
        "",
        f"- هم‌پوشانی‌های سطحیِ candidate: {summary['evaluation_overlap_candidates']}",
        f"- هم‌پوشانی پیوسته: حداقل {thresholds['minimum_contiguous_evaluation_tokens']} واژه؛ بررسی نزدیک: Jaccard روی 3-gramها.",
        "- candidate نه اثبات ورود به آموزش است و نه برآورد سوگیری نمره؛ شباهت معنایی/پارافریزها پوشش داده نمی‌شوند.",
        "",
        "## پردازش، نسخه و محدودیت",
        "",
        "- مقایسه: Unicode NFC و فشرده‌سازی فاصله‌ها؛ متن اصلی بازنویسی یا صادر نمی‌شود.",
        "- گزارش فقط شناسه، شمارش، پرچم و hash دارد؛ hash ناشناس‌سازی نیست و ممکن است امکان تطبیق متن را بدهد.",
        "- جست‌وجوی near-duplicate زوج‌به‌زوج و مناسب fixture کوچک است؛ برای وب‌مقیاس طراحی نشده.",
        "- زبان از فیلد manifest خوانده می‌شود؛ کد زبان را تشخیص یا کیفیت را رتبه‌بندی نمی‌کند.",
        "- وضعیت حقوقی، مجوز پلتفرم، حریم خصوصی، bias، پوشش، کیفیت موضوعی و حذف تکرار معنایی باید جداگانه و انسانی بررسی شوند.",
        "",
    ])


def audit_files(
    manifest_path: str | Path,
    evaluation_path: str | Path,
    output_dir: str | Path,
    *,
    target_use: str = "pretraining",
    min_characters: int = 64,
    near_threshold: float = 0.70,
    evaluation_threshold: float = 0.65,
    min_contiguous_tokens: int = 8,
) -> tuple[dict, dict]:
    corpus = load_corpus(manifest_path)
    evaluation = load_evaluation(evaluation_path)
    report, summary = audit_records(
        corpus,
        evaluation,
        target_use=target_use,
        min_characters=min_characters,
        near_threshold=near_threshold,
        evaluation_threshold=evaluation_threshold,
        min_contiguous_tokens=min_contiguous_tokens,
    )
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    _write_json(output / "audit.json", report)
    _write_json(output / "summary.json", summary)
    (output / "data_card.md").write_text(build_data_card(summary), encoding="utf-8")
    return report, summary


def main(argv: Sequence[str] | None = None) -> int:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Create an offline corpus audit ledger; no training export")
    parser.add_argument("--manifest", type=Path, default=root / "sample_corpus.jsonl")
    parser.add_argument("--evaluation", type=Path, default=root / "sample_evaluation.jsonl")
    parser.add_argument("--output", type=Path, default=root / "build")
    parser.add_argument("--target-use", default="pretraining")
    parser.add_argument("--min-characters", type=int, default=64)
    parser.add_argument("--near-threshold", type=float, default=0.70)
    parser.add_argument("--evaluation-threshold", type=float, default=0.65)
    parser.add_argument("--min-contiguous-tokens", type=int, default=8)
    args = parser.parse_args(argv)
    _, summary = audit_files(
        args.manifest,
        args.evaluation,
        args.output,
        target_use=args.target_use,
        min_characters=args.min_characters,
        near_threshold=args.near_threshold,
        evaluation_threshold=args.evaluation_threshold,
        min_contiguous_tokens=args.min_contiguous_tokens,
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2))
    print("Audit only: no data was approved, deleted, downloaded, or exported for training.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
