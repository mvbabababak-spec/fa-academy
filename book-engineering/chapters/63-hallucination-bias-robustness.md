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
