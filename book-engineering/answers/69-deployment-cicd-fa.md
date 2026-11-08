# پاسخ‌نامهٔ مستقل فصل ۶۹ — استقرار و CI/CD

این پاسخ‌ها نمونهٔ استدلال‌اند؛ انتخاب نهایی به threat model، بار، قرارداد داده، تعهد دسترس‌پذیری، حوزهٔ قضایی و مهارت تیم وابسته است. آستانه‌های fixture فصل را به‌عنوان policy تولیدی به‌کار نبرید.

## پرسش ۱

**صورت پرسش:** برای یک سرو داخلی با دادهٔ حساس و burst فصلی، بین استقرار محلی، ابر و ترکیبی تصمیم بگیرید. دو محدودیت غیرقابل‌مذاکره، سه هزینهٔ جاری و یک مسیر بازیابی را مشخص کنید؛ قیمت بدون تاریخ و بازار ننویسید.

**پاسخ:** یک انتخاب محتمل، محیط محلی برای داده‌ای است که باید در مرز سازمان بماند و capacity ابریِ ازپیش‌تأییدشده برای burst محدود است؛ اما این انتخاب تنها وقتی منطقی است که مسیر شبکه و identity دو محیط یکسان آزموده و failover امن باشد. دو محدودیت می‌توانند residency داده و حداکثر latency endpoint باشند. سه هزینهٔ جاری را به‌ترتیب محاسبه/ظرفیت، storage و network/egress می‌نویسم؛ سپس زمان patch و on-call را هم در برآورد مالکیت می‌آورم. مسیر بازیابی: traffic را به آخرین bundle پایدار با schema سازگار برگردانم، صفِ مجاز را drain کنم و readiness و latency را دوباره تأیید کنم. بدون منطقه، تاریخ، واحد یا منبع قیمت ابری نمی‌نویسم؛ هزینهٔ بازار باید جداگانه با فرض‌هایش ثبت شود.

## پرسش ۲

**صورت پرسش:** manifest یک release فرضی را با پنج جزء بسازید: serving، مدل، tokenizer، preprocessing و runtime. بگویید برای هر جزء کدام شناسه immutable است و کدام evidence باید به digest بسته پیوند بخورد.

**پاسخ:** manifest شامل `service_image_digest`، `model_artifact_digest`، `tokenizer_version_or_digest`، `preprocessing_code_digest` و `runtime_dependency_lock_digest` است؛ کنارشان schema ورودی/خروجی، منبع هر جزء، مجوز، owner، policy version و شاخص ارزیابی نگه می‌دارم. digest نهایی bundle به manifest canonical یا بستهٔ release واقعی وصل می‌شود، نه به tag متحرک. provenance باید همان digest را در subject معرفی کند و به source revision، builder، build type و ورودی‌های resolved پیوند داشته باشد. SBOM برای inventory dependency و گزارش آزمون برای gateهای release جداگانه ثبت می‌شوند. در پروژهٔ فصل، این hashها فقط hash توصیف‌های JSON ساختگی‌اند؛ artifact واقعی نیستند.

## پرسش ۳

**صورت پرسش:** در canary فرضی، ۲۷ خطا از ۱٬۰۰۰ درخواست و p95 برابر ۷۵۰ ms ثبت شده است. اگر policy آزمایشگاه به‌ترتیب حداکثر ۲٪ خطا و ۸۰۰ ms باشد، تصمیم این مرحله چیست؟ کدام نکته باعث می‌شود این تصمیم را مستقیماً به production تعمیم ندهید؟

**پاسخ:** نرخ خطا ۲۷ ÷ ۱٬۰۰۰ = ۰٫۰۲۷ = ۲٫۷٪ است؛ از حد fixture یعنی ۲٪ بیشتر می‌شود. p95 برابر ۷۵۰ ms در حد ۸۰۰ ms می‌ماند، اما کافی نیست تا نتیجهٔ نرخ خطا را نادیده بگیریم؛ gate این مرحله fail می‌شود و promotion متوقف یا rollback می‌شود. این تصمیم فقط با همان policy و دادهٔ تمرینی سازگار است. حداقل حجم نمونه، مدت مشاهده، baseline، SLO واقعی، تعریف خطا، طبقهٔ درخواست و خطر محصول باید پیش از canary واقعی مشخص شوند؛ آستانهٔ fixture آستانهٔ production نیست.

## پرسش ۴

**صورت پرسش:** pipeline شما برای candidate جدید به migration پایگاه داده نیاز دارد. یک ترتیب expand/contract طراحی کنید که نسخهٔ قدیم و جدید در پنجرهٔ بازگشت دادهٔ قابل‌خواندن داشته باشند؛ اگر migration برگشت‌ناپذیر است، چه recovery جایگزینی می‌گذارید؟

**پاسخ:** ابتدا ستون یا schema تازه را به‌شکل nullable/سازگار اضافه می‌کنم و نسخهٔ قدیم را دست‌نخورده نگه می‌دارم. سپس کدی می‌گذارم که هر دو نمایش را بخواند و فقط پس از آزمون، نوشتن یا dual-write کنترل‌شده را آغاز می‌کند. پس از backfill و مقایسهٔ consistency، traffic را به candidate می‌برم و تا پایان پنجرهٔ rollback، consumer نسخهٔ قبلی را پشتیبانی می‌کنم. حذف فیلد قدیمی مرحله‌ای مستقل و دیرتر است. اگر عملیات داده برگشت‌پذیر نیست، قبل از اجرا backup/restore و forward-fix آزموده، نقطهٔ توقف، هماهنگی مالک داده و روش reconcile تعریف می‌کنم؛ فرمان rollback برنامه به‌تنهایی داده را به عقب نمی‌برد.

## پرسش ۵

**صورت پرسش:** برای blue/green و canary، هزینه‌هایی را فهرست کنید که در compute خام دیده نمی‌شوند. یک برآورد ماهانه بسازید که resource، کار انسانی و بازیابی را جدا کند؛ اگر نرخ بازار ندارید، کدام اعداد را باید خالی بگذارید؟

**پاسخ:** Blue/green ممکن است storage دو محیط، load balancer، شبکه، egress، logging/metrics موازی و زمان آزادنگه‌داشتن نسخهٔ قبلی را اضافه کند. Canary ممکن است inference دوباره، جمع‌آوری و بررسی سنجه، دادهٔ کنترل، زمان on-call و بازآزمایی کیفیت را بخواهد. در برآورد ماهانه، resourceهای ثابت و مصرفی، ساعت نیروی انسانی، storage/retention و exerciseهای recovery را ردیف‌های جدا می‌کنم؛ هزینهٔ مورد انتظار رخداد را نیز با فرض و دادهٔ تاریخی مستقل نشان می‌دهم. اگر نرخ واقعی بازار/منطقه یا ساعات تیم را ندارم، مقدار قیمت/ساعت را خالی یا «تأییدنشده» می‌گذارم و واحد و روش جمع‌آوری را مشخص می‌کنم؛ عدد ساختگی را به دلار تبدیل نمی‌کنم.

## پرسش ۶

**صورت پرسش:** یک workflow روی pull request fork، کد آزمون را اجرا می‌کند و job دیگری به cloud deploy دسترسی دارد. مرز jobها، permissionهای token، secretها، OIDC trust و نقطهٔ approval را طوری بازطراحی کنید که اجرای کد نامطمئن اختیار استقرار نگیرد.

**پاسخ:** Job آزمون pull request را با permission حداقلی و بدون secret deploy اجرا می‌کنم؛ artifact آن را از نظر منبع و digest بررسی می‌کنم و هیچ artifact نامطمئنی را مستقیم در job privileged اجرا نمی‌کنم. Job deploy فقط پس از branch protection و CI سبز روی commit مورد اعتماد آغاز می‌شود. `GITHUB_TOKEN` را به `contents: read` محدود می‌کنم و permissionهای دیگر را در job لازم جداگانه می‌دهم. `id-token: write` فقط به job deploy نیاز دارد؛ trust policy در cloud به repository، ref/workflow و environment درست مقید می‌شود و token کوتاه‌عمر با scope لازم می‌گیرد. دسترسی production secret بعد از environment gate و approval مالک مستقل داده می‌شود. از اجرای fork با `pull_request_target` و checkout کد آن در زمینهٔ privileged دوری می‌کنم.

## پرسش ۷

**صورت پرسش:** مدل و وزن ثابت‌اند اما tokenizer و preprocessing عوض می‌شوند. توضیح دهید چرا release تازه لازم است و چه gateهای offline، API، کیفیت و latency را پیش از جابه‌جایی ترافیک اجرا می‌کنید.

**پاسخ:** رفتار مؤثر تابع وزن به‌تنهایی نیست؛ tokenizer تعداد/مرز token، truncation، ترتیب ویژگی و ورودی مدل را تغییر می‌دهد، و preprocessing نیز ممکن است توزیع یا schema را جابه‌جا کند. بنابراین release تازه با manifest و digest جدید لازم است، حتی اگر وزن‌ها ثابت باشند. ابتدا schema و unit/integration tests، fixtureهای ورودی مرزی و smoke endpoint را اجرا می‌کنم؛ سپس protocol ارزیابی offline با holdout و metricهای ازپیش‌ثبت‌شده را می‌سنجیم، و latency/p95/throughput و حافظه را برای همان runtime و precision اندازه می‌گیریم. در canary فقط پس از gateها، با privacy و approval مناسب، به سهم کوچک می‌روم و معیار توقف ازپیش‌تعیین‌شده می‌گذارم.

## پرسش ۸

**صورت پرسش:** پروژه را گسترش دهید تا در صورت نبود artifact پایدار، مفقودبودن provenance یا نقض p95، هیچ promotion انجام نشود. یک آزمون خطا و یک آزمون بازیابی اضافه کنید و دقیقاً بنویسید کدام بخش هنوز فقط شبیه‌سازی است.

**پاسخ:** در preflight شرط می‌گذارم current release digest معتبر و در registry قابل‌بازیابی باشد، و provenance هم به digest candidate وصل و verify شده باشد؛ در غیر این صورت decision `blocked` می‌شود. برای p95، یک آزمون fixture با latency بیش از policy می‌سازم و assert می‌کنم stage بعدی promotion نمی‌شود و active release همان نسخهٔ پایدار قبلی است. آزمون بازیابی می‌تواند پس از fail شدن canary، route را به نسخهٔ قبلی برگرداند و `/healthz` و `/version` را در local stub دوباره کنترل کند. در محیط این پروژه، registry، امضا، health metrics، routing و rollback production واقعی نیستند؛ کد تصمیم را روی fixture و سرویس loopback ساختگی می‌سنجد.
