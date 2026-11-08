# جلد پنجم، فصل ۸ — استقرار، CI/CD و نگه‌داری سامانهٔ هوش مصنوعی

**نگاشت:** فصل محلی ۸ جلد پنجم = فصل سراسری ۶۹. **تاریخ بازبینی منابع: ۴ نوامبر ۲۰۲۶.** فصل ۶۶ مرز API و محصول را می‌سازد؛ فصل ۶۷ رفتار سرو، صف و cache را می‌سنجد؛ فصل ۶۸ هویت، محدودیت مصرف، رخداد و پایش امنیتی را پوشش می‌دهد. این فصل تغییر کنترل‌شدهٔ نسخه از مخزن تا محیط اجرا، gateهای انتشار، rollback و هزینهٔ نگه‌داری را دنبال می‌کند؛ مبانی امنیت محصول یا تحلیل ظرفیت را دوباره تدریس نمی‌کند و به فصل‌های ۶۷ و ۶۸ ارجاع می‌دهد. فصل ۷۰ به خواندن و بازتولید مقاله می‌پردازد. پروژهٔ فصل یک شبیه‌ساز و smoke service محلیِ ساختگی است؛ نه زیرساخت ابری، نه مدل و نه استقرار production.

**پیش‌نیاز:** Git، آزمون نرم‌افزار، HTTP، قرارداد API فصل ۶۶، ظرفیت فصل ۶۷ و کنترل‌های فصل ۶۸. **خروجی:** بتوانید واحد انتشار هوش مصنوعی را نسخه‌بندی کنید، pipeline را از اعتماد و شواهد جدا بسازید، راهبرد rollout را با هزینه و امکان بازگشت بسنجید و استقرار را روی یک سرویس محلیِ بی‌خطر بازتولید کنید.

![شکل ۵-۸-۱ — نمودار مفهومی جریان انتشار از تغییر نسخه‌بندی‌شده به آزمون و ساخت یک artifact ثابت، سپس staging و canary با gateهای سلامت، و در پایان promotion یا بازگشت به نسخهٔ قبلی. خط توپر مسیر رو به جلو و خط‌چین مسیر rollback را نشان می‌دهد؛ رنگ برای تشخیص مراحل لازم نیست.](../diagrams/v5-ch08-release-pipeline.svg)

## ۱. استقرار یعنی تغییر کنترل‌شدهٔ وضعیت

استقرار (deployment) انتقال یک بستهٔ نسخه‌بندی‌شده به محیطی برای اجراست. انتشار (release) تصمیمی جداست که مشخص می‌کند چه کسی یا چه سهمی از کاربر، قابلیت تازه را می‌بیند. یک artifact می‌تواند در staging مستقر باشد اما هنوز برای کاربر منتشر نشده باشد؛ feature flag یا تغییر مسیر ترافیک ممکن است انتشار را جدا از استقرار کنترل کند.

این تمایز عملی است: اگر یک candidate روی staging آزموده شده ولی traffic production همچنان به نسخهٔ قبلی می‌رود، artifact مستقر شده است اما release کاربر آغاز نشده است. در رخداد، باید بدانیم کدام digest در کدام محیط اجرا می‌شود و کدام مسیر ترافیک به آن رسیده است؛ یک برچسب متنی به‌تنهایی پاسخ این پرسش‌ها نیست.

## ۲. CI، تحویل پیوسته و استقرار پیوسته یکی نیستند

یکپارچه‌سازی پیوسته (CI) تغییرهای کوچک را مرتب به شاخهٔ مشترک می‌آورد و برای آن‌ها build و آزمون تکرارپذیر اجرا می‌کند. هدف، دریافت سریع بازخورد و کوچک نگه‌داشتن فاصلهٔ میان تغییرهاست؛ سبزشدن CI به‌تنهایی مجوز استقرار نیست.

تحویل پیوسته (continuous delivery) یعنی نرم‌افزار در چرخهٔ عمر خود در وضعیت قابل‌استقرار بماند و بتوان آن را در زمان نیاز با ریسک کنترل‌شده منتشر کرد. ممکن است gate انسانی یا پنجرهٔ انتشار لازم باشد. استقرار پیوسته (continuous deployment) مرحله‌ای خودکارتر است: تغییر واجد شرایط، پس از gateهای تعریف‌شده، بدون تصمیم انتشار جداگانه به production می‌رود. هر تیم یا محصول الزاماً نباید استقرار پیوسته را انتخاب کند؛ تحویل پیوسته هم بدون آن ارزش دارد [۱].

## ۳. واحد انتشار برای یک سامانهٔ هوش مصنوعی

در یک محصول مدل‌محور، «نسخهٔ مدل» به‌تنهایی واحد کافی نیست. بستهٔ release ممکن است شامل کد سرو، وزن یا adapter مدل، tokenizer، preprocessing/postprocessing، prompt یا policy version، کتابخانه‌ها و نسخهٔ runtime، قرارداد داده، index بازیابی و گزارش ارزیابی باشد. اگر یکی از این اجزا عوض شود اما شناسهٔ بسته ثابت بماند، بازتولید یا rollback دشوار می‌شود.

برای هر جزء ثبت کنید: شناسهٔ منبع، نسخه یا digest محتوا، روش تولید، وابستگی‌ها، مالک، مجوز، schema ورودی/خروجی و شواهد آزمون. در صورت وجود داده یا index، شناسه و منشأ آن‌ها را ثبت کنید؛ محتوای کاربر را به‌صورت پیش‌فرض در manifest یا log کپی نکنید. نگه‌داری اطلاعات رخداد و دسترسی را مطابق فصل ۶۸ طراحی کنید.

## ۴. نام نسخه با هویت artifact فرق دارد

نامی مانند `release-2026.11` برای انسان خواناست، اما ممکن است tag یا alias در registry به محتوای دیگری اشاره کند. digest رمزنگارانه، در مقابل، هویت محتوا را نشان می‌دهد. برای استقرار دقیق، manifest و رجیستری باید artifact نهایی را به digest پیوند دهند؛ aliasهایی مانند `latest` برای یافتن نسخهٔ جاری مفیدند، اما مرجع یگانهٔ promotion یا rollback نباشند [۲].

Pin کردن digest جلوی تغییر بی‌خبر محتوا پشت tag را می‌گیرد، اما به‌خودی‌خود به‌روزرسانی امنیتی را نصب نمی‌کند. وابستگی pin‌شده را پایش و به‌روزرسانی، آزمون و انتشارش را ثبت کنید. بازسازی image از همان Dockerfile هم لزوماً به‌تنهایی ثابت نمی‌کند همهٔ ورودی‌های زمان build ثابت یا امن بوده‌اند.

## ۵. Manifest، provenance و SBOM سه نقش مکمل دارند

Manifest release فهرست نسخه‌ها و قرارداد اجزای همان بسته است. فهرست اجزای نرم‌افزار (SBOM) inventory اجزای نرم‌افزاری را توصیف می‌کند. Provenance شواهدی دربارهٔ این است که کدام builder، از چه ورودی‌ها و فرایندی، artifact معین را ساخته است. این اسناد مکمل‌اند؛ یکی جای دیگری را نمی‌گیرد.

SLSA یک مشخصات تدریجی برای شواهد زنجیرهٔ تأمین است. در مشخصهٔ نسخهٔ ۱٫۲، Build Track از L0 تا L3 پیش می‌رود: L1 provenance می‌خواهد، L2 provenance امضاشده از platform می‌خواهد و L3 کنترل‌های سخت‌گیرانه‌تر builder را اضافه می‌کند. نسخهٔ ۱٫۲ Source Track را نیز تعریف می‌کند. سطح SLSA گواه امن‌بودن منطق برنامه، کیفیت مدل، قانونی‌بودن داده یا درستی یک ادعای تولیدی نیست؛ مصرف‌کننده باید provenance و digest را در برابر انتظار خود بررسی کند [۳].

در سامانهٔ هوش مصنوعی، این زنجیره را تا حد امکان به وزن، کد preprocessing، tokenizer، دادهٔ آموزشی یا ارزیابی، pipeline و مشتقات مدل امتداد دهید. NIST SP 800-218A پروفایل تکمیلیِ SSDF برای توسعهٔ GenAI و مدل‌های foundation دوکاربردی است و بر حفاظت و ردیابی اجزای هوش مصنوعی تأکید دارد؛ آن را کنار SP 800-218 بخوانید، نه به‌عنوان جایگزین همهٔ الزامات سازمانی [۴].

## ۶. محل استقرار را با محدودیت‌ها انتخاب کنید

استقرار محلی، ابر یا ترکیبی را فقط بر اساس قیمت فهرستی انتخاب نکنید. جدول زیر چارچوب تصمیم است، نه رتبه‌بندی قطعی:

| گزینه | مزیت محتمل | هزینه یا ریسک اجرایی | پرسش پیش از انتخاب |
|---|---|---|---|
| محلی یا مرکز دادهٔ خودسازمان | کنترل نزدیک‌تر بر محیط، اتصال و سیاست نگه‌داری داده | خرید/نگه‌داری سخت‌افزار، ظرفیت محدود، patch و مسئولیت on-call | چه کسی ظرفیت، برق، شبکه، backup و بازیابی را اداره می‌کند؟ |
| ابر عمومی | قابلیت‌های مدیریت‌شده، ظرفیت قابل تغییر و دسترسی به محیط‌های گوناگون | سهمیه، وابستگی به provider، egress و هزینهٔ مشاهده‌پذیری/ذخیره | اگر region یا سرویس در دسترس نباشد، مسیر جایگزین چیست؟ |
| ترکیبی | تقسیم workload و امکان نگه‌داشتن بعضی داده یا سرویس در محل مناسب | هماهنگی هویت، نسخه، شبکه، failover و هزینهٔ دو محیط | آیا قرارداد و آزمون میان دو محیط واقعاً یکسان‌اند؟ |

تصمیم باید از نیازمندی‌های latency، دسترسی، residency، حساسیت داده، پشتیبانی سخت‌افزار، رشد بار، مهارت تیم، RTO/RPO و هزینهٔ خروج از provider بیاید. تکرار inference روی چند replica یا منطقه نیز هزینه و سطح حمله را بالا می‌برد. تخمین منابع و قیمت بازار موضوع فصل ۵۶ است؛ این فصل قیمت روز برای provider یا GPU معرفی نمی‌کند.

## ۷. تفاوت محیط‌ها را آشکار کنید، نه پنهان

توسعه، آزمون، staging و production باید از نظر قرارداد و تنظیمات قابل‌مقایسه باشند، اما credential و دادهٔ یکسان نداشته باشند. اگر staging همان secret production را بگیرد، یک تست کم‌خطر می‌تواند به‌اشتباه عمل حساس انجام دهد. اگر staging از نسخهٔ dependency، schema یا feature flag متفاوت استفاده کند، smoke test ممکن است خرابی production را پیش‌بینی نکند.

Infrastructure as Code (IaC) تعریف محیط را نسخه‌بندی می‌کند؛ خودش صحت، مجوز یا ظرفیت را تضمین نمی‌کند. تغییر زیرساخت را بازبینی و آزمون کنید، state و secret را از repository جدا نگه دارید و drift بین پیکربندی اعلام‌شده و محیط واقعی را آشکار کنید. drift حل‌نشده باید gate یا هشدارِ مالک‌دار داشته باشد.

## ۸. Pipeline از چه gateهایی تشکیل می‌شود؟

یک pipeline قابل‌ممیزی معمولاً از تغییر کنترل‌شده آغاز می‌شود، سپس lint و unit test، integration contract، scan وابستگی و secret، ارزیابی مدل متناسب با خطر، build artifact، تولید provenance، انتشار artifact به registry، آزمون staging، approval در صورت نیاز، rollout تدریجی و ثبت نتیجه را می‌گذراند. ترتیب و gate دقیق به سطح ریسک بستگی دارد؛ فهرست ابزار، معیار موفقیت نیست.

هر gate باید بگوید چه ورودی را می‌سنجد، چه شاهدی ذخیره می‌کند، چه کسی مالک آن است و شکست چه اثری دارد. «اسکن انجام شد» بدون نگه‌داری گزارش، severity، استثنا و تصمیم دربارهٔ استثنا قابل‌ممیزی نیست. «آزمون گذشت» نیز باید به نسخهٔ کد و artifact مشخص پیوند بخورد.

## ۹. یک‌بار بسازید؛ همان artifact را promote کنید

اگر برای staging و production هر بار از source جداگانه build کنید، دو artifact ممکن است حتی با نام نسخهٔ یکسان محتوا یا وابستگی متفاوت داشته باشند. الگوی امن‌تر آن است که candidate از ورودی نسخه‌بندی‌شده یک‌بار build شود، digest و provenance آن ثبت شود، همان artifact در staging آزموده و سپس با همان digest به محیط بعدی promote شود.

ترتیب قابل‌ردیابی می‌تواند چنین باشد: commit → build/test → artifact + digest + provenance → staging → approval یا policy gate → canary → rollout یا rollback. وقتی لازم است یک artifact دوباره build شود، آن را release تازه با شناسه و شواهد تازه بدانید؛ صرفاً tag را بازنویسی نکنید.

## ۱۰. مرز اعتماد GitHub Actions را محدود کنید

یک workflow فایل پیکربندی است و اختیار اجرا می‌گیرد؛ بنابراین خودش بخشی از سطح حمله است. `GITHUB_TOKEN` را با کمترین permission لازم تعریف کنید، permission نوشتن را فقط به jobی بدهید که به آن نیاز دارد و job آزمون کدِ pull request نامطمئن را از job استقرارِ دارای دسترسی جدا کنید. دادهٔ کنترل‌شده توسط pull request را مستقیم در shell interpolation نگذارید.

برای workflowهای عمومی، به کد fork یا pull request نامطمئن secret deploy ندهید. از `pull_request_target` برای checkout و اجرای کد pull request نامطمئن استفاده نکنید. به‌روزرسانی actionهای شخص ثالث را بازبینی کنید؛ مستندات GitHub پین‌کردن action به SHA کامل را راهی برای ارجاع immutable می‌داند و در صورت پشتیبانی، dependency lockfile را نیز مطرح می‌کند [۵].

## ۱۱. Secret پایدار را تا حد ممکن از pipeline حذف کنید

به‌جای نگه‌داری credential بلندمدت cloud به‌عنوان secret عمومی repository، در صورت پشتیبانی provider از OpenID Connect استفاده کنید: workflow هویت موقت می‌گیرد، cloud claimها را با trust policy از پیش‌تعریف‌شده می‌سنجد و token کوتاه‌عمر با scope محدود برمی‌گرداند. این الگو secret پایدار را کم می‌کند، اما اگر trust policy به repository، branch، environment و workflow درست محدود نشده باشد، مجوز باز باقی می‌ماند [۶].

اجازهٔ `id-token: write` را فقط برای jobی که token می‌خواهد بدهید. Secretهای محیط production را به jobهای غیرضروری ندهید؛ logها و خطاها را بعد از آزمون ورودی نامعتبر نیز بازبینی کنید. در GitHub، required reviewer و قواعد branch/tag برای environment می‌توانند gate ایجاد کنند، ولی availability برخی قابلیت‌ها به plan و عمومی/خصوصی بودن repository بستگی دارد؛ پیش از تکیه بر آن‌ها دسترسی واقعی مخزن را بررسی کنید [۷].

## ۱۲. قرارداد آزمون پیش از جابه‌جایی ترافیک

قبل از deployment، آزمون contract و schema، startup/readiness، smoke test، integration با وابستگی‌های لازم و بررسی configuration را تعریف کنید. برای سرو مدل، آزمون سلامت endpoint به‌تنهایی کافی نیست؛ یک ورودی ساختگی و مجاز باید پاسخ با شکل و نسخهٔ مورد انتظار بگیرد. تست عملیاتی باید با سازگاری فصل ۶۶، latency/throughput فصل ۶۷ و policy امنیت/حریم خصوصی فصل ۶۸ هم‌راستا باشد.

برای artifact مدل، حداقل نسخهٔ مدل، tokenizer، preprocessing، runtime، precision، schema و گزارش ارزیابی را کنار هم ثبت کنید. تغییرِ فقط prompt، quantization، index یا policy نیز ممکن است رفتار را تغییر دهد؛ مسیر release باید این اجزا را به نسخهٔ موثر پیوند دهد، نه فقط وزن مدل را.

## ۱۳. راهبرد rollout را با شکل شکست تطبیق دهید

| راهبرد | روش | مزیت یا هزینهٔ اصلی | شرط مهم بازگشت |
|---|---|---|---|
| بازسازی (recreate) | نسخهٔ قدیمی متوقف و نسخهٔ تازه جایگزین می‌شود | ساده، اما downtime محتمل | توقف پیش از آماده‌شدن نسخهٔ جدید را بپذیرید |
| rolling update | نمونه‌های جدید تدریجی جای نمونه‌های قبلی را می‌گیرند | ظرفیت اضافهٔ گذرا و هم‌زیستی نسخه‌ها لازم است | هر دو نسخه باید در دورهٔ گذار با schema و درخواست سازگار باشند |
| blue/green | محیط دوم آماده و پس از آزمون مسیر ترافیک جابه‌جا می‌شود | تغییر مسیر سریع؛ هزینهٔ محیط موازی | نسخهٔ قبلی تا پایان پنجرهٔ بازگشت باقی بماند |
| canary | سهم کوچکی از بار واقعی به نسخهٔ تازه می‌رسد | اثر شکست محدودتر و شاهد واقعی‌تر | کنترل و candidate با سنجهٔ ازپیش‌تعریف‌شده مقایسه شوند |
| shadow | candidate ورودیِ کپی‌شده را می‌بیند اما پاسخ آن به کاربر برنمی‌گردد | رفتار با ترافیک واقعی دیده می‌شود، با هزینه و ملاحظات privacy | جلوگیری از side effect و رعایت مجوز کپی داده ضروری است |
| feature flag | قابلیت یا مسیر پاسخ برای گروهی فعال می‌شود | خاموش‌کردن سریع رفتار جدید | flag منقضی و مالک و مقدار پیش‌فرضش مشخص باشد |

Rolling و canary واژه‌های جایگزین هم نیستند؛ rolling روش جایگزینی نمونه‌هاست و canary قاعدهٔ ارزیابی و تقسیم مواجهه. Shadow یا A/B نیز فقط با ورودی مجاز و حذف side effect امن‌اند. راهبردهای تدریجی باید مدت مشاهده، گروه کنترل، سیگنال و نقطهٔ توقف داشته باشند [۸، ۹].

## ۱۴. آستانهٔ canary را پیش از مشاهده تعیین کنید

برای هر مرحله، پیشاپیش baseline، حداقل حجم نمونه، مدت مشاهده، شاخص کیفیت و شاخص سرو را ثبت کنید. اگر error rate، p95 یا شکست readiness از آستانه عبور کرد، promotion را متوقف کنید؛ اگر شاهد کم است، rollout را «نامعلوم» یا «hold» بگذارید، نه «موفق». یک نمونهٔ کوچکِ بدون خطا، تضمین نبود خطای نادر نیست.

آستانه‌ها وابسته به سرویس‌اند. اعداد ۲٪ خطا و ۸۰۰ میلی‌ثانیه در پروژهٔ این فصل فقط policy یک fixture است؛ نباید بدون baseline، حجم واقعی، هزینهٔ خطا و SLO به production منتقل شوند. معیارهای canary نیز در فصل ۶۸ باید privacy-preserving و قابل‌اقدام بمانند.

## ۱۵. کیفیت مدل را کنار سلامت زیرساخت بسنجید

پاسخ ۲۰۰، latency مناسب یا memory پایین کیفیت model behavior را ثابت نمی‌کند. در صورت تغییر مدل یا ورودی‌هایش، gateهای offline و holdout مناسب، محدودیت گروه‌ها، schema، latency و failure mode را با پروتکل فصل ۶۲ و موضوعات فصل ۶۳ بسنجید؛ ارزیابی حمله و حریم خصوصی نیز به فصل ۶۴ و ۶۸ مربوط است. پس از تغییر مدل، صرفاً موفق‌شدن health check برای promotion کافی نیست.

آزمون آنلاین با دادهٔ واقعی ممکن است اثرات دیگری ببیند، اما نیازمند مجوز، کمینه‌سازی، نگه‌داری روشن و تحلیل آسیب است. در fixture ساختگی یا canary کوتاه، نتیجه را به کیفیت عمومی، ایمنی یا fairness مدل تعمیم ندهید. راهنمای reliability هوش مصنوعی Google Cloud نیز نسخه‌بندی، آزمون پیش از تغییر ترافیک، canary و پایش/rollback را کنار هم می‌گذارد؛ این راهنما توصیهٔ عملیاتی است، نه الزام عمومی یا اثبات نتیجه [۱۰].

## ۱۶. مقیاس‌پذیری deployment را با ظرفیت سرو اشتباه نگیرید

Deployment چگونگی انتقال نسخه است؛ scaling چگونگی تغییر ظرفیت در برابر بار. Rollout ممکن است موقتاً دو نسخه را هم‌زمان اجرا کند، وزن‌ها را دوباره بارگیری کند یا درخواست‌های warm-up بسازد؛ این تغییر می‌تواند ظرفیت و هزینه را بالا ببرد. قواعد replica، صف، batch، cache و goodput را با سنجه‌های فصل ۶۷ هماهنگ کنید، ولی این فصل الگوریتم runtime را بازنویسی نمی‌کند.

برای سرو مدل، readiness واقعی، زمان بارگیری وزن، سقف حافظه، warmup، حد replica، سهمیهٔ GPU و رفتار هنگام scale-in را قبل از rollout بسنجید. autoscaling جای ظرفیت‌بندی یا آزمون overload نیست؛ اگر candidate فقط با replica اضافی latency هدف را می‌گیرد، هزینه و ظرفیت وابستگی‌ها را هم ثبت کنید.

## ۱۷. Rollback فقط بازگرداندن image نیست

Rollback باید کل bundle سازگار را به نسخه‌ای شناخته‌شده برگرداند: کد، مدل، tokenizer، preprocessing، تنظیمات، policy و هر artifact مرتبط. مشخص کنید مسیر traffic، feature flag و alias registry چگونه برمی‌گردند و آیا دادهٔ درحال‌نوشتن با نسخهٔ قبلی قابل‌خواندن است. ارجاع به revision قبلی Kubernetes، برای مثال، فقط اجزایی را بازمی‌گرداند که در revision مدیریت می‌کند؛ این کار database یا دادهٔ بیرونی را خودکار به عقب نمی‌برد [۱۱].

برای schema، راهبرد expand/contract خطر را کم می‌کند: ابتدا تغییر سازگار با نسخهٔ جاری را اضافه کنید؛ سپس کدی deploy کنید که schema قدیم و جدید را می‌فهمد؛ بعد مهاجرت یا dual-write را تأیید کنید؛ و حذف ستون یا رفتار قدیمی را تا پایان پنجرهٔ rollback عقب بیندازید. برای مهاجرت برگشت‌ناپذیر، forward-fix یا بازیابی از backup ممکن است امن‌تر از rollback فوری باشد.

## ۱۸. Rollback را واقعاً تمرین کنید

در staging یا محیط آزمایشی، failure gate، نسخهٔ قبلی، بازگشت ترافیک، readiness و صحت endpoint را تمرین کنید؛ فقط فرمان rollback را از روی wiki نخوانید. زمان تشخیص، زمان تصمیم، زمان بازگشت، مالک، دادهٔ باقی‌مانده و معیار پایان را ثبت کنید. برای roll-forward نیز مرز تصمیم و مسیر دستی در صورت خرابی خود pipeline داشته باشید.

پس از هر شکست، artifact و log مجاز را حفظ کنید، علت را از هم‌بستگی صرف جدا کنید و action item را به owner و موعد وصل کنید. کنترل rollback بدون artifact قبلی، migration سازگار، دسترسی اضطراری و health check قابل‌اعتماد، بیشتر شبیه وعده است تا قابلیت بازیابی.

## ۱۹. هزینهٔ نگه‌داری را در کل چرخه ببینید

هزینهٔ یک release تنها هزینهٔ GPU یا درخواست inference نیست. محاسبه و ظرفیت مازاد canary/blue-green، storage وزن و index، شبکه و egress، registry، log و metric، test environment، پشتیبانی، patch dependency، بازآموزی یا ارزیابی، on-call، drill بازیابی و زمان مهندسی را جداگانه ثبت کنید. محیط دوم ممکن است rollback را سریع کند ولی تا زمان حذف، هزینهٔ دوگانه بسازد.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="هزینهٔ ماهانهٔ نگه‌داری برابر مجموع محاسبه، ذخیره‌سازی، شبکه، پایش، نیروی انسانی و بازیابی است.">
  <mtable columnalign="left">
    <mtr><mtd><mrow><msub><mi>C</mi><mi>monthly</mi></msub><mo>=</mo><msub><mi>C</mi><mi>compute</mi></msub><mo>+</mo><msub><mi>C</mi><mi>storage</mi></msub><mo>+</mo><msub><mi>C</mi><mi>network</mi></msub></mrow></mtd></mtr>
    <mtr><mtd><mrow><mo>+</mo><msub><mi>C</mi><mi>observability</mi></msub><mo>+</mo><msub><mi>C</mi><mi>staff</mi></msub><mo>+</mo><msub><mi>C</mi><mi>recovery</mi></msub></mrow></mtd></mtr>
  </mtable>
</math>

**متن جایگزین فرمول:** هزینهٔ ماهانهٔ کل، هزینهٔ محاسبه، ذخیره‌سازی، شبکه، مشاهده‌پذیری، نیروی انسانی و بازیابی را با هم جمع می‌کند.

برای مقایسه، افق زمانی، بار موفق، سطح دسترس‌پذیری، مدت نگه‌داری، منطقه و روش اندازه‌گیری را ثابت کنید. اگر دلار یا قیمت provider را وارد می‌کنید، تاریخ، بازار/منطقه، واحد و منبع رسمی را کنار عدد بنویسید؛ برآورد بازار و TCO فصل ۵۶ است. پروژهٔ این فصل عمداً قیمت یا برآورد دلاری تولید نمی‌کند.

## ۲۰. هزینهٔ پنهانِ release ناموفق را هم اندازه بگیرید

میانگین هزینهٔ ماهانه می‌تواند تغییرهای کوچک اما مکرر را پنهان کند. برای تیم، زمان انتظار برای approval، نرخ gateهای flaky، تعداد rollback، زمان بازیابی و درصد تغییرهایی که نیاز به کار اضطراری دارند را ثبت کنید؛ این سنجه‌ها باید برای تصمیم بهتر باشند، نه برای رتبه‌بندی فردی.

برای deployment، هزینهٔ مورد انتظار را می‌توان به‌صورت احتمال شکست ضرب‌در اثر، در کنار هزینهٔ اجرای معمول سنجید؛ این برآورد یک مدل تصمیم است، نه احتمال واقعی مگر دادهٔ تاریخی معتبر داشته باشید. هزینهٔ ناشناخته را «صفر» ثبت نکنید؛ آن را به‌عنوان شکاف اندازه‌گیری به owner بسپارید.

## ۲۱. پروژهٔ فصل: gate و rollout در sandbox محلی

پروژه در `book-engineering/projects/69-deployment-cicd-lab/` یک manifest JSON ساختگی را با قواعد نسخه، componentهای bundle، provenance، gateهای آزمون، approval، سازگاری نسخه و سنجه‌های rollout بررسی می‌کند. سپس یک smoke service واقعی روی loopback بالا می‌آورد که health/version را پاسخ می‌دهد و برای شناسهٔ نمونهٔ ساختگی فقط یک label ثابت برمی‌گرداند.

سناریوی سالم در fixture تا ۱۰۰٪ promotion می‌شود؛ سناریوی latency در مرحلهٔ ۲۵٪ rollback شبیه‌سازی می‌کند؛ سناریوی provenance تأییدنشده پیش از rollout مسدود می‌شود. شاخص‌های ۵/۲۵/۱۰۰ درصد، ۲٪ خطا، p95 برابر ۸۰۰ ms و حداقل ۱۰۰ درخواست فقط ورودی آزمون‌اند، نه نسخهٔ عمومی policy. `results.json` هش بایت‌های خام fixture را ثبت می‌کند. هیچ artifact واقعی یا درخواست production وجود ندارد.

## ۲۲. اجرا و تفسیر نتیجه

از پوشهٔ پروژه، `python3 -m unittest -v` **۴۱ از ۴۱ آزمون** را گذراند: ۳۵ آزمون دروازهٔ انتشار و ۶ آزمون HTTP loopback. اجرای `deployment_gate.py` روی fixture سه تصمیم قطعی داد: یک promotion ساختگی، یک rollback ساختگی و یک block پیش از rollout. پنج درخواست HTTP محلی، health، version، prediction ثابت، رد ورودی دارای prompt اضافه و route ناشناخته را آزمودند؛ سرور از loopback خارج نمی‌شود.

این آزمون‌ها قواعد همان تابع و endpoint نمونه را می‌سنجند. عبور تست واحد، signature معتبر SLSA، scan امنیتی واقعی، quality evaluation مدل، تأیید انسانی، load production یا موفقیت deployment ابری را اثبات نمی‌کند. به‌ویژه مقدار `model_evaluation_record: passed` در fixture فقط یک ورودی ساختگی به policy gate است، نه ارزیابی مدل.

## ۲۳. عیب‌یابی gate و rollout

اگر manifest با digest ثبت‌شده جور نیست، اول بررسی کنید artifact بعد از تولید provenance دوباره بسته‌بندی نشده باشد؛ در production digest artifact نهایی را با subject attestation تطبیق دهید. اگر gate به‌دلیل evidence ناقص block شد، مرحله‌ای را که مدرک ندارد پرچم «تأییدشده» نکنید؛ شاهد معتبر را بسازید یا release را متوقف نگه دارید.

اگر rollout روی `hold` است، حجم نمونه یا duration را در برابر policy ازپیش‌ثبت‌شده بررسی کنید؛ دادهٔ کم به معنی سلامت نیست. اگر p95 یا نرخ خطا خراب است، promotion را متوقف، اثر را محدود و مسیر recovery آزموده را اجرا کنید. اگر rollback روی schema یا index شکست می‌خورد، تغییر را با backup، migration و سازگاری مصرف‌کننده تحلیل کنید؛ کپی‌کردن alias قدیمی لزوماً state بیرونی را برنمی‌گرداند.

## ۲۴. دامنهٔ نتیجه و ضدالگوها

این پروژه یک pipeline واقعی CI/CD، cloud deploy، container build، SLSA signer، model registry، deployment controller یا rollback عملیاتی را اجرا نمی‌کند. مقادیر fixture و hashهای bundle فقط از توصیف‌های JSON ساختگی مشتق شده‌اند؛ نتیجه دربارهٔ کیفیت، امنیت یا هزینهٔ مدل واقعی نیست. سرور loopback نیز endpoint production یا inference engine نیست.

از این ضدالگوها دوری کنید: ساخت artifact مجزا برای هر محیط؛ tag متحرک به‌عنوان تنها هویت release؛ اجرای کد pull request نامطمئن با secret deploy؛ اعتماد به provenance بدون verify؛ approval بی‌مالک؛ rollout بی‌آستانه؛ rollback بدون نسخهٔ قبلی و سازگاری داده؛ نگه‌داری نامحدود staging و وزن؛ و هزینه‌ای که فقط compute را می‌شمارد.

## ۲۵. آخرین تحولات و اسنادِ بررسی‌شده تا نوامبر ۲۰۲۶

در بازبینی ۴ نوامبر ۲۰۲۶، صفحهٔ رسمی SLSA نسخهٔ ۱٫۲ را نشان می‌داد؛ متن فصل Build و Source Track را از هم تفکیک می‌کند. NIST SP 800-218 نسخهٔ نهایی SSDF 1.1 است و SP 800-218A پروفایل تکمیلیِ توسعهٔ GenAI/مدل‌های foundation است. راهنمای جاری GitHub برای Actions، Environments و OIDC زنده است؛ permission، plan، claim و قابلیت‌های آن را هنگام هر تغییر دوباره از مرجع رسمی بسنجید.

مستند Kubernetes دربارهٔ Deployment و rollback، Google SRE دربارهٔ canary و راهنمای Docker دربارهٔ build و digest نیز بازبینی شدند. یک pattern یا عدد در مستندات محصول، الزام برای همهٔ orchestratorها نیست. توسعهٔ actionها، runner، cloud service و specها ادامه دارد؛ نسخهٔ ابزار، runner image و نتیجهٔ CI باید در هر انتشار ثبت شود، نه این‌که از روی اجرای قدیمی فرض گرفته شود.

## ۲۶. منابع و تاریخ بازبینی

۱. DORA، [Continuous delivery](https://dora.dev/capabilities/continuous-delivery/)، مستند جاری؛ تاریخ انتشار صفحه مشخص نیست، دسترسی ۴ نوامبر ۲۰۲۶. تعریف تحویل پیوسته را از استقرار پیوسته جدا می‌کند.

۲. Docker Docs، [Building best practices](https://docs.docker.com/build/building/best-practices/)، مستند زنده؛ تاریخ انتشار صفحه مشخص نیست، دسترسی ۴ نوامبر ۲۰۲۶. دربارهٔ pin کردن ورودی‌ها، mutable بودن tagها و rebuild امن توضیح می‌دهد.

۳. SLSA، [Specification v1.2](https://slsa.dev/spec/v1.2/)، [Build Track basics](https://slsa.dev/spec/v1.2/build-track-basics) و [Build Provenance](https://slsa.dev/spec/v1.2/build-provenance)، مشخصهٔ رسمی نسخهٔ ۱٫۲؛ دسترسی ۴ نوامبر ۲۰۲۶.

۴. NIST، [SP 800-218، SSDF 1.1](https://doi.org/10.6028/NIST.SP.800-218)، نهایی فوریهٔ ۲۰۲۲؛ و [SP 800-218A، Secure Software Development Practices for Generative AI and Dual-Use Foundation Models](https://doi.org/10.6028/NIST.SP.800-218A)، نهایی ژوئیهٔ ۲۰۲۴؛ دسترسی صفحات رسمی ۴ نوامبر ۲۰۲۶.

۵. GitHub Docs، [Secure use reference for GitHub Actions](https://docs.github.com/en/actions/reference/security/secure-use)، مستند جاری؛ تاریخ انتشار صفحه مشخص نیست، دسترسی ۴ نوامبر ۲۰۲۶. حداقل‌سازی permission، خطر اجرای کد نامطمئن و مدیریت وابستگی action را شرح می‌دهد.

۶. GitHub Docs، [OpenID Connect](https://docs.github.com/en/actions/concepts/security/openid-connect)، مستند جاری؛ دسترسی ۴ نوامبر ۲۰۲۶. token کوتاه‌عمر و trust claimهای workflow را توضیح می‌دهد.

۷. GitHub Docs، [Managing environments for deployment](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)، مستند جاری؛ دسترسی ۴ نوامبر ۲۰۲۶. reviewer، secret و محدودیت دسترس‌پذیری environment را شرح می‌دهد.

۸. Google SRE Workbook، [Canarying Releases](https://sre.google/workbook/canarying-releases/)، متن آموزشی جاری؛ تاریخ انتشار صفحه مشخص نیست، دسترسی ۴ نوامبر ۲۰۲۶. canary را rollout جزئی و زمان‌دار با ارزیابی تعریف می‌کند.

۹. Kubernetes، [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)، مستند جاری؛ دسترسی ۴ نوامبر ۲۰۲۶. rolling update، rollout status و محدودهٔ rollback را شرح می‌دهد.

۱۰. Google Cloud Architecture Center، [AI and ML perspective: Reliability](https://docs.cloud.google.com/architecture/framework/perspectives/ai-ml/reliability)، راهنمای vendor-specific؛ دسترسی ۴ نوامبر ۲۰۲۶. version، آزمون پیش از جابه‌جایی ترافیک و rollback را در زمینهٔ AI/ML مطرح می‌کند.

۱۱. Kubernetes، همان [راهنمای Deployment و revision](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#rolling-back-a-deployment)، دسترسی ۴ نوامبر ۲۰۲۶؛ history مربوط به Pod template را توضیح می‌دهد و rollback پایگاه دادهٔ بیرونی را تضمین نمی‌کند.

## ۲۷. تمرین‌ها

۱. برای یک سرو داخلی با دادهٔ حساس و burst فصلی، بین استقرار محلی، ابر و ترکیبی تصمیم بگیرید. دو محدودیت غیرقابل‌مذاکره، سه هزینهٔ جاری و یک مسیر بازیابی را مشخص کنید؛ قیمت بدون تاریخ و بازار ننویسید.

۲. manifest یک release فرضی را با پنج جزء بسازید: serving، مدل، tokenizer، preprocessing و runtime. بگویید برای هر جزء کدام شناسه immutable است و کدام evidence باید به digest بسته پیوند بخورد.

۳. در canary فرضی، ۲۷ خطا از ۱٬۰۰۰ درخواست و p95 برابر ۷۵۰ ms ثبت شده است. اگر policy آزمایشگاه به‌ترتیب حداکثر ۲٪ خطا و ۸۰۰ ms باشد، تصمیم این مرحله چیست؟ کدام نکته باعث می‌شود این تصمیم را مستقیماً به production تعمیم ندهید؟

۴. pipeline شما برای candidate جدید به migration پایگاه داده نیاز دارد. یک ترتیب expand/contract طراحی کنید که نسخهٔ قدیم و جدید در پنجرهٔ بازگشت دادهٔ قابل‌خواندن داشته باشند؛ اگر migration برگشت‌ناپذیر است، چه recovery جایگزینی می‌گذارید؟

۵. برای blue/green و canary، هزینه‌هایی را فهرست کنید که در compute خام دیده نمی‌شوند. یک برآورد ماهانه بسازید که resource، کار انسانی و بازیابی را جدا کند؛ اگر نرخ بازار ندارید، کدام اعداد را باید خالی بگذارید؟

۶. یک workflow روی pull request fork، کد آزمون را اجرا می‌کند و job دیگری به cloud deploy دسترسی دارد. مرز jobها، permissionهای token، secretها، OIDC trust و نقطهٔ approval را طوری بازطراحی کنید که اجرای کد نامطمئن اختیار استقرار نگیرد.

۷. مدل و وزن ثابت‌اند اما tokenizer و preprocessing عوض می‌شوند. توضیح دهید چرا release تازه لازم است و چه gateهای offline، API، کیفیت و latency را پیش از جابه‌جایی ترافیک اجرا می‌کنید.

۸. پروژه را گسترش دهید تا در صورت نبود artifact پایدار، مفقودبودن provenance یا نقض p95، هیچ promotion انجام نشود. یک آزمون خطا و یک آزمون بازیابی اضافه کنید و دقیقاً بنویسید کدام بخش هنوز فقط شبیه‌سازی است.

## ۲۸. جمع‌بندی

CI/CD فقط اجرای خودکار یک فایل نیست؛ زنجیره‌ای از تغییر کنترل‌شده، artifact قابل‌شناسایی، gate قابل‌ممیزی، دسترسی کمینه و مسیر بازیابی آزموده است. برای مدل، release به مدل و runtime محدود نیست و باید preprocessing، tokenizer، schema و ارزیابی را هم به نسخهٔ سرو وصل کند. rollout تدریجی ریسک را حذف نمی‌کند؛ فقط فرصت مشاهده و توقف می‌دهد. اگر هزینه، داده، migration یا بازگشت روشن نیست، انتخاب درست می‌تواند نگه‌داشتن release در staging باشد.

برای ادامه، [پاسخ‌نامهٔ مستقل فصل ۶۹](../answers/69-deployment-cicd-fa.md)، [README پروژه و دستور بازتولید](../projects/69-deployment-cicd-lab/README.md)، [fixture ساختگی](../projects/69-deployment-cicd-lab/synthetic_release_scenarios.json)، [نتایج](../projects/69-deployment-cicd-lab/results.json) و [گزارش ممیزی](69-audit-report-fa.md) را ببینید. فصل ۷۰ به خواندن و بازتولید مقاله می‌پردازد. خروجی این milestone وب/PWA و Markdown است؛ PDF و EPUB تولید یا آزموده نشده‌اند.

## پیوست اجرایی — شبیه‌ساز دروازهٔ انتشار

```python
#!/usr/bin/env python3
"""Deterministic release-gate simulator for synthetic AI deployment evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

DIGEST_PATTERN = re.compile(r"sha256:[0-9a-f]{64}\Z")
REQUIRED_COMPONENTS = ("service", "model", "tokenizer", "preprocessing", "runtime")
DEFAULT_FIXTURE = Path(__file__).with_name("synthetic_release_scenarios.json")


def canonical_bytes(value: Any) -> bytes:
    """Return stable JSON bytes for this exercise's synthetic manifest."""
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_digest(value: Any) -> str:
    """Hash a JSON value using the exercise's canonical serialization."""
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def is_digest(value: Any) -> bool:
    return isinstance(value, str) and DIGEST_PATTERN.fullmatch(value) is not None


def _current_release_errors(current: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(current, dict):
        return ["current_release_missing"]
    if not isinstance(current.get("release_id"), str) or not current["release_id"].strip():
        errors.append("current_release_id_missing")
    components = current.get("components")
    if not isinstance(components, dict) or not all(key in components for key in REQUIRED_COMPONENTS):
        errors.append("current_release_components_incomplete")
    elif current.get("bundle_digest") != sha256_digest(components):
        errors.append("current_release_digest_mismatch")
    if not is_digest(current.get("bundle_digest")):
        errors.append("current_release_digest_invalid")
    return errors


def _preflight_errors(
    scenario: Any, current: Any, policy: Any
) -> list[str]:
    errors: list[str] = []
    if not isinstance(scenario, dict):
        return ["scenario_not_object"]
    if not isinstance(policy, dict):
        return ["policy_not_object"]
    errors.extend(_current_release_errors(current))

    name = scenario.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("scenario_name_missing")
    if scenario.get("target") not in {"staging", "production"}:
        errors.append("target_not_supported")

    candidate = scenario.get("candidate")
    if not isinstance(candidate, dict):
        return errors + ["candidate_not_object"]
    release_id = candidate.get("release_id")
    if not isinstance(release_id, str) or not release_id.strip():
        errors.append("candidate_release_id_missing")
    elif isinstance(current, dict) and release_id == current.get("release_id"):
        errors.append("candidate_release_id_not_new")

    components = candidate.get("components")
    if not isinstance(components, dict) or not all(key in components for key in REQUIRED_COMPONENTS):
        errors.append("candidate_components_incomplete")
    else:
        computed_digest = sha256_digest(components)
        if not is_digest(candidate.get("bundle_digest")):
            errors.append("candidate_digest_invalid")
        elif candidate.get("bundle_digest") != computed_digest:
            errors.append("candidate_digest_mismatch")

    provenance = candidate.get("provenance")
    if not isinstance(provenance, dict) or provenance.get("verified") is not True:
        errors.append("provenance_not_verified")
    elif candidate.get("bundle_digest") != provenance.get("subject_digest"):
        errors.append("provenance_subject_mismatch")

    required_gates = policy.get("required_gates")
    gates = candidate.get("gates")
    if not isinstance(required_gates, list) or not required_gates:
        errors.append("required_gates_policy_missing")
    elif not isinstance(gates, dict):
        errors.append("candidate_gates_missing")
    else:
        errors.extend(
            f"gate_not_passed:{gate}"
            for gate in required_gates
            if gates.get(gate) != "passed"
        )

    if policy.get("require_backward_compatibility", True) and candidate.get("backward_compatible") is not True:
        errors.append("rollback_compatibility_not_confirmed")
    if scenario.get("target") == "production" and policy.get("require_production_approval", True):
        if scenario.get("approval_status") != "approved":
            errors.append("production_approval_missing")

    stages = policy.get("rollout_stages_percent")
    if (
        not isinstance(stages, list)
        or not stages
        or any(not isinstance(value, int) or isinstance(value, bool) for value in stages)
        or stages != sorted(set(stages))
        or stages[-1] != 100
        or stages[0] <= 0
    ):
        errors.append("rollout_policy_invalid")

    if isinstance(current, dict) and candidate.get("bundle_digest") == current.get("bundle_digest"):
        errors.append("candidate_matches_current_release")
    return errors


def _observation_error(observation: Any) -> str | None:
    if not isinstance(observation, dict):
        return "observation_not_object"
    requests = observation.get("requests")
    errors = observation.get("errors")
    p95_ms = observation.get("p95_ms")
    traffic_percent = observation.get("traffic_percent")
    if not isinstance(traffic_percent, int) or isinstance(traffic_percent, bool):
        return "traffic_percent_invalid"
    if not isinstance(requests, int) or isinstance(requests, bool) or requests <= 0:
        return "request_count_invalid"
    if not isinstance(errors, int) or isinstance(errors, bool) or errors < 0 or errors > requests:
        return "error_count_invalid"
    if not isinstance(p95_ms, (int, float)) or isinstance(p95_ms, bool) or not math.isfinite(p95_ms) or p95_ms < 0:
        return "p95_latency_invalid"
    return None


def evaluate_scenario(scenario: dict[str, Any], current: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a fixture scenario without making any external deployment call."""
    errors = _preflight_errors(scenario, current, policy)
    current_id = current.get("release_id") if isinstance(current, dict) else None
    if errors:
        return {
            "scenario": scenario.get("name") if isinstance(scenario, dict) else None,
            "decision": "blocked",
            "preflight_passed": False,
            "blocked_reasons": errors,
            "active_release_id": current_id,
            "promoted_stages_percent": [],
            "rollback_performed": False,
            "simulated_only": True,
        }

    candidate = scenario["candidate"]
    expected_stages = policy["rollout_stages_percent"]
    observations = scenario.get("observations")
    if not isinstance(observations, list):
        observations = []
    observed_stages = [item.get("traffic_percent") if isinstance(item, dict) else None for item in observations]
    if observed_stages != expected_stages:
        return {
            "scenario": scenario["name"],
            "decision": "blocked",
            "preflight_passed": True,
            "blocked_reasons": ["rollout_observations_do_not_match_policy"],
            "active_release_id": current_id,
            "promoted_stages_percent": [],
            "rollback_performed": False,
            "simulated_only": True,
        }

    promoted: list[int] = []
    minimum_requests = policy.get("minimum_requests_per_stage")
    max_error_rate = policy.get("max_error_rate")
    max_p95_ms = policy.get("max_p95_ms")
    if (
        not isinstance(minimum_requests, int) or isinstance(minimum_requests, bool) or minimum_requests <= 0
        or not isinstance(max_error_rate, (int, float)) or isinstance(max_error_rate, bool)
        or not 0 <= max_error_rate <= 1
        or not isinstance(max_p95_ms, (int, float)) or isinstance(max_p95_ms, bool) or max_p95_ms <= 0
    ):
        return {
            "scenario": scenario["name"],
            "decision": "blocked",
            "preflight_passed": True,
            "blocked_reasons": ["health_policy_invalid"],
            "active_release_id": current_id,
            "promoted_stages_percent": [],
            "rollback_performed": False,
            "simulated_only": True,
        }

    for observation in observations:
        invalid = _observation_error(observation)
        if invalid:
            return {
                "scenario": scenario["name"],
                "decision": "blocked",
                "preflight_passed": True,
                "blocked_reasons": [invalid],
                "active_release_id": current_id,
                "promoted_stages_percent": promoted,
                "rollback_performed": False,
                "simulated_only": True,
            }
        stage = observation["traffic_percent"]
        if observation["requests"] < minimum_requests:
            return {
                "scenario": scenario["name"],
                "decision": "hold",
                "preflight_passed": True,
                "blocked_reasons": ["insufficient_canary_sample"],
                "active_release_id": current_id,
                "promoted_stages_percent": promoted,
                "held_at_percent": stage,
                "rollback_performed": False,
                "simulated_only": True,
            }
        error_rate = observation["errors"] / observation["requests"]
        if error_rate > max_error_rate:
            return {
                "scenario": scenario["name"],
                "decision": "rolled_back",
                "preflight_passed": True,
                "blocked_reasons": ["canary_error_rate_over_limit"],
                "active_release_id": current_id,
                "candidate_release_id": candidate["release_id"],
                "promoted_stages_percent": promoted,
                "failed_at_percent": stage,
                "observed_error_rate": round(error_rate, 6),
                "rollback_performed": True,
                "simulated_only": True,
            }
        if observation["p95_ms"] > max_p95_ms:
            return {
                "scenario": scenario["name"],
                "decision": "rolled_back",
                "preflight_passed": True,
                "blocked_reasons": ["canary_p95_over_limit"],
                "active_release_id": current_id,
                "candidate_release_id": candidate["release_id"],
                "promoted_stages_percent": promoted,
                "failed_at_percent": stage,
                "observed_p95_ms": observation["p95_ms"],
                "rollback_performed": True,
                "simulated_only": True,
            }
        promoted.append(stage)

    return {
        "scenario": scenario["name"],
        "decision": "promoted",
        "preflight_passed": True,
        "blocked_reasons": [],
        "active_release_id": candidate["release_id"],
        "candidate_release_id": candidate["release_id"],
        "previous_release_id": current_id,
        "promoted_stages_percent": promoted,
        "rollback_performed": False,
        "simulated_only": True,
    }


def run_fixture(payload: dict[str, Any], fixture_sha256: str) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("synthetic") is not True:
        raise ValueError("fixture must be a synthetic JSON object")
    fixture_id = payload.get("fixture_id")
    if not isinstance(fixture_id, str) or not fixture_id.strip():
        raise ValueError("fixture_id is required")
    current = payload.get("current_release")
    policy = payload.get("policy")
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("fixture must contain at least one scenario")
    names = [item.get("name") if isinstance(item, dict) else None for item in scenarios]
    if any(not isinstance(name, str) or not name.strip() for name in names) or len(names) != len(set(names)):
        raise ValueError("scenario names must be non-empty and unique")
    results = [evaluate_scenario(scenario, current, policy) for scenario in scenarios]
    decision_counts = {name: sum(result["decision"] == name for result in results) for name in ("blocked", "hold", "rolled_back", "promoted")}
    return {
        "project_id": fixture_id,
        "fixture_id": fixture_id,
        "fixture_sha256": fixture_sha256,
        "synthetic": True,
        "scenario_count": len(results),
        "decision_counts": decision_counts,
        "results": results,
        "external_network_requests": 0,
        "cloud_deployments": 0,
        "production_writes": 0,
        "model_inference_calls": 0,
        "gpu_used": False,
        "personal_records": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, help="write deterministic JSON to this path")
    args = parser.parse_args()
    try:
        raw = args.fixture.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
        result = run_fixture(payload, hashlib.sha256(raw).hexdigest())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
