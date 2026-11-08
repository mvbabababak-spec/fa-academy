# جلد چهارم، فصل ۱۴ — ردیابی آزمایش و ابزارهای MLOps

فصل محلی ۱۴ از ۱۵ جلد چهارم؛ فصل سراسری ۶۰. این فصل عملیاتِ ثبت و بازسازی یک اجرای یادگیری ماشین را بررسی می‌کند: کد، داده، پیکربندی، محیط، سنجه و artifact چگونه با هم به یک سابقهٔ قابل‌ردیابی تبدیل می‌شوند؟ موضوع فصل، اجرای آزمایش و خط لولهٔ دسته‌ای است؛ ساخت API سرو، زمان‌بندی استنتاج، batching و بهینه‌سازی تأخیر به فصل ۶۱ واگذار می‌شوند.

## ۱. جایگاه فصل و مرز موضوعی

فصل ۵۷ به چارچوب‌ها و فصل ۵۸ به زنجیرهٔ داده و مدل پرداخته‌اند؛ فصل ۵۹ دستگاه‌های CUDA و ROCm، Triton و موازی‌سازی آموزش را بررسی کرده است. این فصل نتیجهٔ آن مراحل را به یک اجرای قابل‌شناسایی و قابل‌بازرسی پیوند می‌دهد، اما آموزش توزیع‌شده یا سازگاری GPU را دوباره آموزش نمی‌دهد. فصل ۶۱ روی سرو و بهینه‌سازی استنتاج متمرکز است؛ پس Kubernetes Job و CronJob را در این‌جا فقط برای اجرای کار دسته‌ای توضیح می‌دهیم، نه به‌عنوان راهنمای سرو مدل.

در این متن، «MLOps» به معنی ثبت و ادارهٔ اجرای آزمایش است، نه ادعای خودکار دربارهٔ کیفیت مدل یا «استقرار یک‌کلیکی». Git تاریخچهٔ کد را نگه می‌دارد؛ سامانهٔ ردیابی، پیکربندی و سنجهٔ اجرا را سازمان می‌دهد؛ ذخیره‌ساز artifact فایل‌های بزرگ را نگه می‌دارد؛ کانتینر محیط نرم‌افزار را بسته‌بندی می‌کند؛ و ارکستریتور، مانند Kubernetes، محاسبه را زمان‌بندی می‌کند. هیچ‌یک به‌تنهایی جای سه جزء دیگر را نمی‌گیرد.

## ۲. مسئلهٔ عملیاتی: «این عدد از کدام اجرا آمده است؟»

فرض کنید یک جدول گزارش می‌گوید زیان اعتبارسنجی ۰٫۰۹ بوده است. برای تفسیر آن باید بتوان پرسید: کدام کد؟ کدام نسخهٔ داده؟ کدام پیکربندی؟ کدام نسخهٔ کتابخانه‌ها و image؟ آیا پوشهٔ کار Git پاک بوده است؟ سنجه در کدام گام ثبت شده؟ فایل مدل یا گزارش کجاست؟ آیا اجرا به‌طور کامل تمام شده یا فقط یک آزمون دود بوده است؟

اگر پاسخ هر سؤال گم شده باشد، رقم به‌تنهایی قابل بازسازی نیست. یک دفترچهٔ run باید حداقل شناسهٔ اجرا، شناسه و هش داده، پیکربندی، نسخهٔ کد، وضعیت dirty بودن درخت Git، نسخهٔ محیط، سنجه‌های مرحله‌ای، مسیر و هش artifact و وضعیت پایان را ثبت کند. برای کار GPU باید مدل دستگاه، درایور و چارچوب نیز ثبت شود؛ این پروژه فقط محاسبهٔ مصنوعی روی CPU انجام می‌دهد و برای آن ادعای GPU ندارد.

## ۳. شناسهٔ اجرا و هش محتوا

شناسهٔ قابل‌ردیابی را از ورودی‌های پایدار بسازید: نسخهٔ کد، هش fixture، پیکربندی، قفل وابستگی‌ها و digest کانتینر. زمان اجرا را جداگانه ذخیره کنید؛ اگر زمان وارد اثرانگشت شود، دو اجرای یکسان در دو روز بی‌دلیل شناسهٔ متفاوت می‌گیرند.

<math xmlns="http://www.w3.org/1998/Math/MathML" aria-label="اثر انگشت اجرا برابر است با هش SHA256 از JSON کانونی مجموعهٔ ورودی‌های ثابت">
  <mrow><mi>F</mi><mo>=</mo><mi>SHA256</mi><mo>(</mo><mi>CanonicalJSON</mi><mo>(</mo><mi>S</mi><mo>)</mo><mo>)</mo></mrow>
</math>

**متن جایگزین فرمول:** اثرانگشت اجرا برابر SHA-256ِ JSON کانونیِ مجموعهٔ ورودی‌های ثابت است.

«JSON کانونی» در این مثال یعنی کلیدها مرتب، جداکننده‌ها ثابت، متن با UTF-8 و مقادیر غیرمتناهی ممنوع باشند. هش به شناسایی تغییر بایت‌ها کمک می‌کند؛ کیفیت داده، بی‌طرفی مدل، مجوز استفاده یا صحت علمی را ثابت نمی‌کند. اگر Git dirty باشد، صرفاً درج commit کافی نیست؛ پروژه وضعیت و هش diff را نیز ثبت می‌کند. برای بازسازی کامل، اجرای انتشار را از commit پاک انجام دهید یا patch و فایل‌های ثبت‌نشده را طبق سیاست نگهداری خود نگه دارید.

![شکل ۴-۱۴-۱: کد و وضعیت Git، fixture داده، قفل محیط و پیکربندی با پیکان به یک اجرای دارای اثرانگشت می‌رسند؛ پارامترها و سنجه‌ها به MLflow محلی یا W&B آفلاین پیوند می‌خورند و model.json و run.json خروجی می‌شوند. مثال فقط چهار ردیف ساختگی را ثبت می‌کند؛ tracker، CI و Job به‌تنهایی کیفیت مدل، benchmark یا استقرار واقعی را ثابت نمی‌کنند.](book-engineering/diagrams/v4-ch14-mlops.svg)

## ۴. آزمایش، اجرا، پارامتر، سنجه و artifact

«آزمایش» گروهی از اجراهای مربوط به یک پرسش است؛ «اجرا» یک پیکربندی مشخص است که واقعاً انجام شده است. پارامترهایی مانند نرخ یادگیری و تعداد گام‌ها در آغاز run ثبت می‌شوند. سنجه‌هایی مانند loss می‌توانند با شمارهٔ گام تغییر کنند؛ میانگین نهایی بدون تاریخچه ممکن است روند ناپایدار را پنهان کند. artifact فایل خروجی نسخه‌دار است؛ برای نمونه، گزارش JSON یا وزن‌های مدل. در این فصل، `model.json` فقط دو ضریب یک تمرین مصنوعی را نگه می‌دارد.

مدل‌رجیستری، مخزن داده و سامانهٔ ردیابی مفاهیم جدا هستند. artifact ثبت‌شده به‌خودی‌خود تأییدشده، قابل‌استقرار یا دارای چرخهٔ انتشار نیست. فرایند پذیرش و مصرف مدل در سرو، موضوع فصل ۶۱ و سیاست سازمان شماست. برای فایل بزرگ، Git commit را به مخزن وزن تبدیل نکنید؛ از ذخیره‌ساز مناسب، مجوز دسترسی، نسخه و هش استفاده کنید.

## ۵. قرارداد داده و fixture کوچک

پروژهٔ فصل از چهار زوج عددی ساختگی استفاده می‌کند. `sample_experiment.json` شناسهٔ fixture، برچسب صریح `synthetic_fixture`، پیکربندی و محدودیت ادعا را دارد. `fixture_manifest.json` تعداد ردیف‌ها و SHA-256 بایت‌های همان فایل را ثبت می‌کند. کد پیش از اجرا هش را دوباره محاسبه می‌کند و اگر fixture تغییر کرده باشد، اجرا را رد می‌کند.

در دادهٔ واقعی، تنها هش معمولاً برای بازتولید کافی نیست؛ نسخهٔ snapshot، محل مجاز بازیابی، تقسیم train/validation، فیلترها، مجوز، نگهدارنده و سیاست حذف را نیز مستند کنید. هش را جایگزین رضایت، مجوز یا ناشناس‌سازی نکنید و دادهٔ حساس را فقط برای راحتی در tracker کپی نکنید. پروژهٔ این فصل دادهٔ واقعی نمی‌خواند و به دادهٔ شخصی نیاز ندارد.

برای معیار خطای نمونه، رگرسیون خطی کوچک از میانگین مربعات استفاده می‌کند:

<math xmlns="http://www.w3.org/1998/Math/MathML" aria-label="میانگین مربعات خطا برابر است با مجموع مربع اختلاف پیش‌بینی و مقدار هدف تقسیم بر تعداد نمونه‌ها">
  <mrow><mi>MSE</mi><mo>=</mo><mfrac><mn>1</mn><mi>n</mi></mfrac><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi></munderover><msup><mrow><mo>(</mo><msub><mover><mi>y</mi><mo>^</mo></mover><mi>i</mi></msub><mo>−</mo><msub><mi>y</mi><mi>i</mi></msub><mo>)</mo></mrow><mn>2</mn></msup></mrow>
</math>

**متن جایگزین فرمول:** میانگین مربعات خطا، مجموع مربع اختلاف پیش‌بینی و مقدار هدف را بر تعداد نمونه‌ها تقسیم می‌کند.

این معیار فقط قرارداد ریاضی همان fixture است؛ split مستقل، baseline، آزمون تعمیم یا سنجش کیفیت محصول نداریم. بنابراین کاهش loss در چهار نمونهٔ ساختگی شاهد کیفیت مدل نیست.

## ۶. Git و منشأ کد

Git commit برای شناسهٔ کد نقطهٔ آغاز است، نه تمام داستان. پیش از انتشار، `git rev-parse HEAD` را ثبت کنید و با `git status --porcelain` پاک بودن درخت را بررسی کنید. اگر اجرا ناچاراً از وضعیت dirty انجام شده، هش diff، تعداد فایل‌های ثبت‌نشده و وضعیت را ثبت و آن اجرا را «کاملاً بازتولیدپذیر از commit» معرفی نکنید. این پروژه نام فایل‌ها یا محتوای diff را به tracker نمی‌فرستد؛ فقط هش وضعیت را ثبت می‌کند.

Git برای تغییرات متنی کوچک و review مناسب است. وزن‌های مدل، cache، log و دادهٔ حجیم معمولاً در Git عادی جای نمی‌گیرند. Git LFS نیز به‌تنهایی lineage داده یا کنترل دسترسی کامل نمی‌سازد. پس commit، هش داده و نسخهٔ artifact را در manifest به هم وصل کنید. اگر کد داخل container اجرا می‌شود و پوشهٔ `.git` به‌عمد در image نیست، commit و وضعیت پاک را از pipeline ساخت به‌عنوان metadata غیرمحرمانه تزریق کنید؛ Dockerfile نمونه متغیرهای `SOURCE_*` را برای همین حالت می‌پذیرد.

## ۷. محیط اجرا و قفل وابستگی‌ها

نسخهٔ مستقیم دو tracker کافی نیست: resolver می‌تواند وابستگی‌های انتقالی را در روز دیگری متفاوت انتخاب کند. پروژه هم `requirements.txt` با وابستگی‌های مستقیم دارد و هم `requirements-lock-linux-py313.txt` با نسخه‌های نصب‌شدهٔ محیط آزموده‌شده. این قفل برای CPython 3.13 روی Linux x86-64 است؛ برای معماری یا نسخهٔ پایتون دیگری قفل جدا بسازید و آزمایش کنید. `pip check` سازگاری اعلام‌شدهٔ وابستگی‌ها را بررسی می‌کند، نه صحت همهٔ رفتارها.

اثر انگشت پروژه هش خود قفل را هم ثبت می‌کند. برای اجرای واقعی، زمان، فرمان، locale و timezone، نسخهٔ سیستم‌عامل، image digest، دستگاه و درایور، مقدار seed و تنظیمات precision را نیز متناسب با محاسبه نگه دارید. حتی با lockfile، نتیجهٔ عددی روی سخت‌افزارها یا کرنل‌های متفاوت ممکن است بیت‌به‌بیت یکسان نباشد؛ بازتولیدپذیری باید با دامنهٔ مشخص تعریف شود.

## ۸. انتخاب tracker: چه چیزی را واقعاً می‌خواهیم؟

| نیاز | MLflow | Weights & Biases |
|---|---|---|
| واحد اصلی | آزمایش و run؛ پارامتر، سنجه، tag و artifact | run؛ پیکربندی و تاریخچهٔ سنجه، با Artifact و lineage |
| شروع محلی این پروژه | SQLite و artifact محلی؛ بدون سرور شبکه‌ای | حالت `offline`؛ فایل run در مسیر خروجی |
| چندکاربره یا تیمی | tracking server، backend store و artifact store با پشتیبان‌گیری و دسترسی درست | فضای تیم/سازمان و میزبان پشتیبانی‌شده؛ بررسی محل داده و سیاست دسترسی |
| وابستگی به شبکه در smoke test | ندارد، چون URI محلی است | ندارد، چون SDK صریحاً در حالت `offline` اجرا می‌شود |
| چه چیزی حل نمی‌شود؟ | کیفیت مدل، مدیریت اسرار، نگهداری داده و مجوز | همان؛ به‌علاوه همگام‌سازی آفلاین تا وقتی اپراتور صریحاً آن را انجام ندهد |

این جدول رتبه‌بندی محصول نیست. برای انتخاب، مالکیت داده، دسترسی، محل ذخیره، هزینه، قابلیت پشتیبان‌گیری، احراز هویت، نگهداری نسخه و توان عملیات را ارزیابی کنید. یک SQLite محلی برای تمرین تک‌نفره مناسب است، نه الزاماً پایگاه چندکاربرهٔ تولیدی.

## ۹. MLflow: run و artifact در ذخیرهٔ محلی

MLflow Tracking، پیکربندی و پارامترها، سنجه‌های مرحله‌ای، tagها و فایل‌های artifact را به run مرتبط می‌کند. کد پروژه `mlflow==3.18.0` را در یک virtualenv مستقل نصب می‌کند؛ URI از نوع SQLite به فایل داخل پوشهٔ خروجی اشاره دارد و فایل `model.json` و manifest را در artifact محلی ثبت می‌کند. هیچ tracking server یا سرو عمومی آغاز نمی‌شود. آزمون با `MlflowClient` پارامتر، آخرین سنجه و دو مسیر artifact را از run ذخیره‌شده می‌خواند.

برای تیم، معماری ذخیره‌سازی را جدا طراحی کنید: backend store برای metadata و artifact store برای فایل‌ها، با احراز هویت، TLS، backup، restore، retention و حداقل مجوز. SQLite محلیِ تمرین، سرور مشترک نیست. نشانی endpoint و credential را در سورس یا log چاپ نکنید؛ آن‌ها را از سازوکار اسرار محیط اجرا تزریق کنید.

## ۱۰. W&B: run آفلاین و همگام‌سازی آگاهانه

در API پایتون، `wandb.init` یک run می‌سازد؛ `config` برای پیکربندی و `run.log` برای تاریخچهٔ سنجه است. Artifact خروجی می‌تواند به همان run پیوند بخورد. نمونهٔ پروژه صریحاً `mode="offline"` را تحمیل می‌کند، API key ارث‌رسیده را فقط برای مدت فراخوانی از محیط حذف می‌کند، دریافت خودکار کد و Git را خاموش می‌کند و فقط اطلاعات مصنوعیِ اعلام‌شده را log می‌کند. تست حتی وقتی متغیر محیطی والد روی `online` و یک کلید آزمایشیِ جعلی تنظیم شده باشد، ذخیرهٔ محلی را بررسی می‌کند؛ کلید واقعی لازم نیست.

اجرای آفلاین هنوز فایل محلی می‌سازد. آن پوشه ممکن است سنجه، پیکربندی و artifact را شامل شود؛ محل، دسترسی و زمان حذفش را مدیریت کنید. SDK به‌تنهایی `wandb sync` را از این پروژه اجرا نمی‌کند. همگام‌سازی بعدی تصمیم اپراتور است: پیش از آن بررسی کنید چه چیزی ارسال می‌شود، به کدام میزبان و سازمان می‌رود و سیاست داده اجازه می‌دهد یا نه. نسخهٔ `wandb==0.31.0` در release note اکتبر ۲۰۲۶ تغییر میزبان پیش‌فرض و مسیر پیوند run را گزارش می‌کند؛ پیش از اتصال آنلاین میزبان و credential را با مستندات همان استقرار دوباره بررسی کنید.

## ۱۱. پروژهٔ اجرایی: از fixture تا run

در `experiment_ops.py` چهار کار از هم جدا شده‌اند: اعتبارسنجی قرارداد و هش fixture؛ اجرای رگرسیون خطی ساختگی؛ ساخت `model.json` و `run.json` با اثرانگشت، محیط و منشأ؛ و ارسال metadata به backend انتخابی. حالت پیش‌فرض `manifest` فقط فایل محلی می‌سازد؛ `mlflow` از SQLite محلی استفاده می‌کند؛ `wandb-offline` از SDK رسمی در حالت محلی استفاده می‌کند.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-lock-linux-py313.txt
python -m pip check
python experiment_ops.py --backend manifest --output /tmp/ch60-manifest
python experiment_ops.py --backend mlflow --output /tmp/ch60-mlflow
python experiment_ops.py --backend wandb-offline --output /tmp/ch60-wandb
python -m unittest -v
```

در خروجی هر اجرا، `run.json` هش fixture و مدل، پارامترها، سنجهٔ اولیه و نهایی، تاریخچهٔ گام‌ها، قفل وابستگی، commit و وضعیت Git را دارد. زمان تولید ثبت می‌شود اما در اثرانگشت پایدار وارد نمی‌شود. در image بدون `.git`، متغیرهای `SOURCE_COMMIT` و `SOURCE_WORKTREE_CLEAN` و هش‌های وضعیت را از CI تزریق کنید؛ اگر منبع در دسترس نباشد، مقدار نامعلوم صریح می‌ماند و به‌جای دادهٔ ساختگی، `null` ثبت می‌شود.

## ۱۲. خواندن نتایج و مرز شواهد

روی fixture فعلی، MSE آغازین ۲۱ و MSE پس از ۵ گام ۰٫۰۹۰۷۸۷۳۱۸۶۸۷۸۴۱۷۸ است. این مقدار با اجرای خالص پایتون، چهار نقطه و نرخ یادگیری ۰٫۰۵ به دست می‌آید. ۱۶ آزمون unit قرارداد fixture و هش، کانونی‌سازی fingerprint، تشخیص درخت Git پاک/dirty، ذخیرهٔ SQLite محلی، run آفلاین W&B و ساختار ایستای Dockerfile و YAML را بررسی می‌کنند. `results.json` و `environment.json` خلاصهٔ همین اجرا هستند.

این نتایج اثبات نمی‌کنند که Docker image ساخته شده یا Kubernetes Job در cluster اجرا شده است. در محیط نویسندگی Docker، Podman و kubectl در دسترس نبودند؛ YAML فقط با PyYAML parse و قراردادهای منتخب بررسی شد، نه با API server یا schema validator کامل. هیچ dataset واقعی، model checkpoint، GPU، benchmark، upload یا sync آنلاین به‌کار نرفته است. بخش گزارش ممیزی این محدودیت‌ها را جداگانه ثبت می‌کند.

## ۱۳. کانتینر: مرز محیط، نه تضمین بازتولید

`Dockerfile` نمونه، Python `3.13.16-slim` را با digest چندمعماری ثبت‌شده در ۲۱ اکتبر ۲۰۲۶ pin می‌کند، وابستگی‌ها را در stage ساخت نصب می‌کند و فقط لایهٔ محیط و فایل‌های لازم را به runtime می‌برد. کاربر غیرریشه، مسیر خروجی writable و `.dockerignore` مانع ورود اتفاقی `.git`، محیط مجازی، پایگاه tracker، log و فایل `.env` به build context می‌شوند. چون lock این پروژه Linux x86-64 است، نمونهٔ Dockerfile نیز `linux/amd64` را مشخص می‌کند؛ برای ARM64 باید lock و build جداگانه تولید و آزموده شود.

Pin کردن digest، تغییرپذیری tag را کم می‌کند، اما به‌معنای وصلهٔ امنیتی دائمی نیست. برای به‌روزرسانی، image پایه را آگاهانه بررسی و rebuild کنید؛ از `--pull` برای گرفتن مرجع تازه استفاده کنید، ولی تأثیر `--no-cache` را از آن جدا بدانید. Dockerfile را فقط static بررسی کرده‌ایم؛ build و scan image انجام نشده است. `SOURCE_*` در نمونه metadata غیرمحرمانه است؛ هرگز API key را با `ARG`, `ENV`, build log یا لایهٔ image وارد نکنید.

## ۱۴. Kubernetes: Job برای کار تمام‌شونده

`Deployment` برای پردازهٔ پایدار، `Job` برای کار پایان‌پذیر و `CronJob` برای ساخت دوره‌ای Job است. نمونهٔ `job.yaml` یک `batch/v1 Job` با deadline، retry محدود، TTL، resource request/limit، اجرای غیرریشه، filesystem ریشه فقط‌خواندنی و `emptyDir` محدودشده دارد. image با digest نوشته شده، اما دامنهٔ `.invalid` و digest صفر عمداً placeholder غیرقابل‌دریافت است؛ تا زمان جایگزینی با image واقعی، manifest deployable نیست.

این Job فقط demo مصنوعی CPU را می‌نویسد. برای GPU باید device plugin و resource نام‌گذاری‌شدهٔ cluster و محدودیت‌های همان سخت‌افزار را پیکربندی کنید؛ شرح دستگاه‌ها در فصل ۵۹ است. برای اجرای W&B آنلاین یا MLflow تیمی، endpoint، egress، credential و artifact store را جدا طراحی کنید؛ secret را در Git/YAML آشکار وارد نکنید. YAML با یک parser خوانده شده، اما در cluster اجرا نشده است.

## ۱۵. ماندگاری خروجی و عمر artifact

`emptyDir` با حذف Pod از بین می‌رود؛ TTL نیز Job را پس از زمان تعیین‌شده پاک می‌کند. این رفتار برای demo کوتاه مناسب است، نه نگهداری نتیجهٔ باارزش. پیش از حذف، log و artifact را به PVC یا object store مجاز منتقل کنید، نسخه و هش آن را ثبت کنید، و آزمایش restore را هم انجام دهید. اگر data residency یا درخواست حذف مطرح است، cache، نسخه‌های artifact، پشتیبان و runهای آفلاین را هم در محدودهٔ حذف حساب کنید.

مسئولیت tracker این نیست که retention شما را حدس بزند. برای هر artifact، مالک، محل، مدت نگهداری، مجوز خواندن/نوشتن، نسخه، فرایند حذف و هزینهٔ ذخیره‌سازی را تعیین کنید. یک path یا run ID بدون سیاست نگهداری به‌معنای در دسترس بودن همیشگی نیست.

## ۱۶. CI و انتشار امن

CI باید دست‌کم قفل نصب‌شده را با `pip check` بررسی کند؛ آزمون‌های قرارداد را اجرا کند؛ hash fixture و manifest را تطبیق دهد؛ smoke test آفلاین MLflow و W&B را انجام دهد؛ و Dockerfile/YAML را با ادعاهای ثبت‌شده مقایسه کند. اگر image واقعاً build و publish می‌شود، خروجی را با digest تغییرناپذیر و commit منبع پیوند دهید. در این انتشار فقط آزمون‌های پایتون و parse ایستای manifest اجرا می‌شوند؛ build/push image و cluster test در scope نیستند.

برای GitHub Actions، دسترسی `GITHUB_TOKEN` را حداقلی کنید، actionهای شخص ثالث را به commit کامل pin کنید، credential را فقط در job نیازمند آن بدهید و log را از secret پاک نگه دارید. تست offline نباید برای موفقیت به credential یا شبکهٔ tracking نیاز پیدا کند. CI نیز مجوز تولید یا نشر مدل صادر نمی‌کند؛ gateهای validation و approval را جدا تعریف کنید.

## ۱۷. مشاهده‌پذیری و عیب‌یابی در Linux

پیش از تکرار اجرا، فرمان و خروجی خطا را بخوانید، وضعیت دیسک را بررسی کنید، سپس tracker و artifact را جدا ارزیابی کنید. برای پروژهٔ نمونه این فرمان‌ها فقط وضعیت محلی را نشان می‌دهند:

```bash
python -VV
python -m pip check
git rev-parse HEAD
git status --porcelain
find /tmp/ch60-mlflow -maxdepth 3 -type f -printf '%p %s bytes\n'
df -h /tmp
```

در محیط واقعی، log را با شناسهٔ run، زمان UTC و سطح severity پیوند دهید؛ اما token، دادهٔ خام و URI دارای password را چاپ نکنید. از stdout/stderr و exit code برای خطای job استفاده کنید؛ برای GPU، وضعیت driver را مطابق فصل ۵۹ بررسی کنید. «process زنده است» و «Job موفق است» یکسان نیستند؛ exit code، پایان artifact و ثبت سنجه باید با هم تفسیر شوند.

## ۱۸. امنیت، حریم خصوصی و مرز اعتماد

tracking server و artifact store دو محل افشای متفاوت‌اند. فهرست مجازهای جدا برای metadata و فایل‌ها تنظیم کنید؛ رمزگذاری مسیر انتقال و ذخیره را طبق زیرساخت اعمال کنید؛ credential چرخشی و کوتاه‌عمر به کار ببرید؛ و دسترسی CI، کاربر، سرویس و پژوهشگر را از هم تفکیک کنید. W&B offline هم روی دیسک محلی داده می‌نویسد، پس «آفلاین» به معنی «بی‌خطر» یا «بدون نگهداری» نیست.

ثبت کد یا dataset در run باید انتخاب آگاهانه باشد. پیش از logging، log و artifact را از PII، token، مسیر داخلی، دادهٔ دارای مجوز محدود و اطلاعات مشتری پاک کنید. هیچ secret را در پارامتر run، tag، Docker layer یا فایل fixture ثبت نکنید. برای incident، ابتدا دسترسی را مسدود و credential را rotate کنید، سپس دامنهٔ runها و نسخه‌های artifact را پیدا و طبق سیاست پاسخ‌گویی حذف/گزارش کنید.

## ۱۹. خطاهای رایج و پاسخ عملی

| نشانه | علت محتمل | بررسی کم‌خطر | اقدام بعدی |
|---|---|---|---|
| دو run با config یکسان، نتیجهٔ متفاوت | lock، commit، seed، hardware یا nondeterminism فرق دارد | fingerprint و environment دو run را مقایسه کنید | تفاوت‌ها را ثبت کنید؛ صرفاً seed را برای پنهان‌کردن تفاوت عوض نکنید |
| fixture mismatch | فایل بعد از manifest تغییر کرده یا مسیر اشتباه است | SHA-256 فایل و نام fixture را بخوانید | manifest را فقط بعد از review داده به‌روز کنید |
| MLflow run ساخته نشد | مسیر SQLite، مجوز نوشتن یا وابستگی ناقص | `pip check`، مسیر output و traceback | مسیر مجاز محلی بدهید؛ در محیط تیمی از معماری server/store پشتیبانی‌شده استفاده کنید |
| W&B می‌خواهد login شود | حالت offline به adapter نرسیده یا نسخه/تنظیمات متفاوت است | `run.json` و نسخهٔ SDK را بررسی کنید | حالت offline را صریح کنید؛ API key را چاپ نکنید و sync را جداگانه تأیید کنید |
| W&B run بعد از container ناپدید شد | پوشهٔ محلی ephemeral بود | mount و TTL را بررسی کنید | PVC/object store یا انتقال کنترل‌شده را پیاده کنید |
| Job در `ImagePullBackOff` است | placeholder، tag/digest یا مجوز registry نادرست است | image reference و pull permission | image واقعی و digest reviewشده را در pipeline تنظیم کنید |
| run تکرار شده و هزینه بالا رفته | retry یا cron بدون idempotency/حد بودجه | Job history، schedule و نرخ retry | deadline، سقف retry، quota و کلید idempotency اضافه کنید |
| log ناخواسته حاوی secret است | capture خودکار console یا کد روشن است | محل‌های log/artifact و دسترسی‌ها را محدود بررسی کنید | credential را rotate کنید و حذف/گزارش incident را طبق سیاست انجام دهید |

## ۲۰. چک‌لیست یک اجرای قابل‌حسابرسی

پیش از اجرا بپرسید: آیا داده مجاز و نسخه‌دار است؟ آیا fixture/config اعتبارسنجی می‌شود؟ آیا commit پاک یا diff بایگانی شده است؟ آیا lock و image digest ثبت شده‌اند؟ آیا سنجه و گام آن تعریف روشن دارند؟ آیا artifact مسیر، هش، مالک و retention دارد؟ آیا کلیدها و دادهٔ خام از log بیرون مانده‌اند؟ آیا retry و deadline کنترل شده‌اند؟ آیا نتیجه صرفاً smoke test است یا واقعاً evaluation مستقل؟

پس از اجرا، manifest و exit code را با هم بررسی کنید، artifact را با هش verify کنید، گزارش را با محدودیت‌های واقعی بنویسید و فقط سپس نتیجه را به مرحلهٔ بعد بسپارید. اجرای موفق pipeline نشان می‌دهد قراردادهای همان pipeline رد نشده‌اند؛ به‌تنهایی نتیجهٔ علمی یا اجازهٔ استقرار نیست.

## ۲۱. تمرین‌ها

۱. یک آزمایش دو بار با `learning_rate` یکسان اجرا شده، اما lockfile در اجرای دوم فرق دارد. برای مقایسهٔ معتبر چه metadataهایی را ثبت و کدام تفاوت را نمی‌توان با هش fixture توضیح داد؟

۲. دادهٔ مشتری اجازهٔ بارگذاری به tracker را ندارد. چه اطلاعاتی می‌توان ثبت کرد تا lineage حفظ شود، و چه چیزی نباید در log یا artifact کپی شود؟

۳. برای یک پژوهشگر منفرد بدون شبکه و یک تیم چندکاربره، کدام ویژگی‌های اجرای محلی SQLite و W&B آفلاین مفیدند و چه مسئله‌هایی را باید جداگانه حل کرد؟

۴. Dockerfile از `python:3.13-slim` با tag متحرک استفاده می‌کند. برای بازسازی image چه چیزی را pin می‌کنید، و چرا pin کردن digest نیاز به وصلهٔ امنیتی آینده را حذف نمی‌کند؟

۵. Kubernetes Job موفق شده، اما `run.json` پس از TTL دیگر وجود ندارد. علت چیست و چه معماری ذخیره‌سازی/نگهداری باید پیش از اجرای مهم اضافه شود؟

۶. در یک log، API key آشکار شده است. قدم‌های فوری شما برای محدودسازی دسترسی، چرخش credential، تعیین دامنهٔ افشا و رسیدگی به نسخه‌های artifact چیست؟

پاسخ‌نامهٔ مستقل و تشریحی: [پاسخ‌نامهٔ فصل ۶۰](book-engineering/answers/60-mlops-fa.md).

## ۲۲. جمع‌بندی و مرز فصل بعد

یک run قابل‌پیگیری، زنجیره‌ای از شناسه‌هاست: commit و وضعیت کد، نسخه و هش داده، config، lock و digest محیط، سنجهٔ مرحله‌ای و artifact. MLflow و W&B این زنجیره را سازمان می‌دهند؛ Docker محیط نرم‌افزار را بسته‌بندی می‌کند؛ Kubernetes کار را زمان‌بندی می‌کند؛ Git و object store و کنترل دسترسی مسئولیت‌های مکمل دارند. هیچ ابزار منفردی به‌تنهایی بازتولیدپذیری یا کیفیت مدل را تضمین نمی‌کند.

پروژهٔ این فصل تنها چهار نقطهٔ ساختگی را در CPU اجرا کرده و ردیابی محلی و W&B آفلاین را آزموده است. ساخت image و اجرای Kubernetes آزموده نشده‌اند. فصل ۶۱ از مرز اجرا و ثبت عبور می‌کند و به سرو مدل و بهینه‌سازی استنتاج می‌پردازد.

## منابع و تاریخ بازبینی

تاریخ بازبینی منابع: ۷ نوامبر ۲۰۲۶. نسخه‌های نرم‌افزار در این فصل snapshot تاریخ‌دارند؛ پیش از استفادهٔ عملی، release note و مستندات سازگار با محیط خود را دوباره بررسی کنید.

- MLflow 3.18.0، release note: <https://github.com/mlflow/mlflow/releases/tag/v3.18.0>
- MLflow Tracking Quickstart: <https://mlflow.org/docs/latest/ml/tracking/quickstart/>
- MLflow Tracking Server Architecture: <https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/>
- Weights & Biases 0.31.0، release note: <https://github.com/wandb/wandb/releases/tag/v0.31.0>
- W&B Experiments: <https://docs.coreweave.com/products/wandb/ref/python/experiments>
- W&B Environment Variables: <https://docs.coreweave.com/products/wandb/track/environment-variables>
- W&B Artifacts: <https://docs.coreweave.com/products/wandb/artifacts>
- Docker Build Best Practices: <https://docs.docker.com/build/building/best-practices/>
- Python 3.13.16 image tag/digest: <https://hub.docker.com/v2/repositories/library/python/tags/3.13.16-slim>
- Kubernetes Workloads: <https://kubernetes.io/docs/concepts/workloads/>
- Kubernetes GPU Scheduling: <https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/>
- Git Book، Recording Changes و Branches: <https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository> و <https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell>
- GitHub Actions Secure Use: <https://docs.github.com/en/actions/reference/security/secure-use>

## ۲۳. پیوست اجرایی

کد زیر همان فایل آزموده‌شدهٔ `book-engineering/projects/60-mlops/experiment_ops.py` است و باید بایت‌به‌بایت با آن یکسان بماند.

```python
#!/usr/bin/env python3
"""Small, offline-first experiment-tracking example for Volume 4, Chapter 14.

The fixture and model are synthetic and intentionally tiny. No network tracking,
model-quality claim, GPU training, or production deployment is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import re
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_FIXTURE = PROJECT_DIR / "sample_experiment.json"
DEFAULT_FIXTURE_MANIFEST = PROJECT_DIR / "fixture_manifest.json"
LOCKFILE = PROJECT_DIR / "requirements-lock-linux-py313.txt"
EXPERIMENT_NAME = "fa-academy-v4-ch14-synthetic-ops"


class ContractError(ValueError):
    """Raised when the fixture or run configuration violates the project contract."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(value: Any) -> bytes:
    """Stable UTF-8 encoding used only for deterministic run fingerprints."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def validate_fixture(data: dict[str, Any]) -> None:
    if data.get("schema_version") != 1:
        raise ContractError("fixture schema_version must be 1")
    if data.get("label_source") != "synthetic_fixture":
        raise ContractError("only the explicitly synthetic fixture is accepted")
    if not isinstance(data.get("fixture_id"), str) or not data["fixture_id"]:
        raise ContractError("fixture_id must be a non-empty string")

    records = data.get("records")
    if not isinstance(records, list) or len(records) < 2:
        raise ContractError("records must contain at least two synthetic rows")
    sample_ids: set[str] = set()
    for row in records:
        if not isinstance(row, dict):
            raise ContractError("every record must be an object")
        sample_id = row.get("sample_id")
        if not isinstance(sample_id, str) or not sample_id or sample_id in sample_ids:
            raise ContractError("sample_id values must be non-empty and unique")
        sample_ids.add(sample_id)
        for key in ("x", "y"):
            value = row.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ContractError(f"record field {key!r} must be a finite number")

    scope = data.get("scope")
    if not isinstance(scope, dict):
        raise ContractError("fixture scope must be an object")
    required_false = (
        "real_data_used",
        "pretrained_model_used",
        "gpu_used",
        "benchmark_claim",
        "model_quality_claim",
        "production_claim",
    )
    if scope.get("synthetic_only") is not True:
        raise ContractError("scope.synthetic_only must be true")
    if any(scope.get(key) is not False for key in required_false):
        raise ContractError("the project fixture must make no real-data or production claims")


def load_fixture(
    fixture_path: Path = DEFAULT_FIXTURE,
    manifest_path: Path = DEFAULT_FIXTURE_MANIFEST,
) -> tuple[dict[str, Any], str]:
    raw = fixture_path.read_bytes()
    digest = sha256_bytes(raw)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"fixture manifest is missing: {manifest_path}") from exc
    if manifest.get("fixture_id") is None:
        raise ContractError("fixture manifest must identify the fixture")
    if manifest.get("fixture_file") != fixture_path.name:
        raise ContractError("fixture manifest filename does not match the selected fixture")
    if manifest.get("sha256") != digest:
        raise ContractError("fixture SHA-256 does not match fixture_manifest.json")
    if manifest.get("record_count") is not None:
        data = json.loads(raw)
        if manifest["record_count"] != len(data.get("records", [])):
            raise ContractError("fixture record count does not match fixture_manifest.json")
    else:
        data = json.loads(raw)
    validate_fixture(data)
    if manifest["fixture_id"] != data["fixture_id"]:
        raise ContractError("fixture ID does not match fixture_manifest.json")
    return data, digest


def fit_toy_linear(
    records: list[dict[str, Any]],
    *,
    steps: int,
    learning_rate: float,
) -> dict[str, Any]:
    """Full-batch gradient descent on a four-row synthetic linear fixture."""
    if isinstance(steps, bool) or not isinstance(steps, int) or not 1 <= steps <= 100:
        raise ContractError("steps must be an integer from 1 through 100")
    if isinstance(learning_rate, bool) or not isinstance(learning_rate, (int, float)):
        raise ContractError("learning_rate must be numeric")
    learning_rate = float(learning_rate)
    if not math.isfinite(learning_rate) or not 0.0 < learning_rate <= 0.1:
        raise ContractError("learning_rate must be finite and in (0, 0.1]")

    xs = [float(row["x"]) for row in records]
    ys = [float(row["y"]) for row in records]
    count = len(records)
    weight = 0.0
    bias = 0.0

    def mse() -> float:
        return sum((weight * x + bias - y) ** 2 for x, y in zip(xs, ys)) / count

    history: list[dict[str, float | int]] = [{"step": 0, "mse": mse()}]
    for step in range(1, steps + 1):
        residuals = [weight * x + bias - y for x, y in zip(xs, ys)]
        grad_weight = (2.0 / count) * sum(error * x for error, x in zip(residuals, xs))
        grad_bias = (2.0 / count) * sum(residuals)
        weight -= learning_rate * grad_weight
        bias -= learning_rate * grad_bias
        loss = mse()
        if not math.isfinite(loss):
            raise ContractError("toy optimizer produced a non-finite metric")
        history.append({"step": step, "mse": loss})

    return {
        "weight": weight,
        "bias": bias,
        "initial_mse": history[0]["mse"],
        "final_mse": history[-1]["mse"],
        "history": history,
    }


def capture_git_provenance(start: Path = PROJECT_DIR) -> dict[str, Any]:
    """Capture commit and cleanliness digests without exporting diffs or file contents."""
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=top,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=top,
            check=True,
            capture_output=True,
        ).stdout
        diff = subprocess.run(
            ["git", "diff", "--binary", "HEAD"],
            cwd=top,
            check=True,
            capture_output=True,
        ).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        declared_commit = os.environ.get("SOURCE_COMMIT")
        if declared_commit in (None, "", "unknown") or not re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", declared_commit):
            declared_commit = None
        clean_text = os.environ.get("SOURCE_WORKTREE_CLEAN", "unknown").lower()
        declared_clean = True if clean_text == "true" else False if clean_text == "false" else None
        status_hash = os.environ.get("SOURCE_STATUS_SHA256")
        diff_hash = os.environ.get("SOURCE_TRACKED_DIFF_SHA256")
        if status_hash is not None and not re.fullmatch(r"[0-9a-f]{64}", status_hash):
            status_hash = None
        if diff_hash is not None and not re.fullmatch(r"[0-9a-f]{64}", diff_hash):
            diff_hash = None
        untracked_text = os.environ.get("SOURCE_UNTRACKED_PATH_COUNT")
        try:
            untracked_count = int(untracked_text) if untracked_text is not None else None
            if untracked_count is not None and untracked_count < 0:
                untracked_count = None
        except ValueError:
            untracked_count = None
        declared = any((declared_commit, declared_clean is not None, status_hash, diff_hash, untracked_count is not None))
        return {
            "available": False,
            "capture_method": "environment" if declared else "unavailable",
            "commit": declared_commit,
            "worktree_clean": declared_clean,
            "status_sha256": status_hash,
            "tracked_diff_sha256": diff_hash,
            "untracked_path_count": untracked_count,
        }

    return {
        "available": True,
        "capture_method": "git",
        "commit": commit,
        "worktree_clean": len(status) == 0,
        "status_sha256": sha256_bytes(status),
        "tracked_diff_sha256": sha256_bytes(diff),
        "untracked_path_count": sum(line.startswith(b"??") for line in status.splitlines()),
    }


def package_version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def environment_snapshot() -> dict[str, Any]:
    lock_hash = sha256_file(LOCKFILE) if LOCKFILE.exists() else None
    digest = os.environ.get("CONTAINER_IMAGE_DIGEST")
    if digest is not None and not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        digest = None
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.system(),
        "machine": platform.machine(),
        "mlflow": package_version("mlflow"),
        "wandb": package_version("wandb"),
        "pyyaml": package_version("PyYAML"),
        "dependency_lock_sha256": lock_hash,
        "container_image_digest": digest,
        "accelerator": "none; pure-Python CPU arithmetic",
    }


def run_fingerprint(
    *,
    fixture_sha256: str,
    config: dict[str, Any],
    environment: dict[str, Any],
    source: dict[str, Any],
) -> str:
    stable_git = {
        key: source.get(key)
        for key in (
            "available",
            "capture_method",
            "commit",
            "worktree_clean",
            "status_sha256",
            "tracked_diff_sha256",
            "untracked_path_count",
        )
    }
    identity = {
        "schema_version": 1,
        "fixture_sha256": fixture_sha256,
        "config": config,
        "environment": environment,
        "source": stable_git,
    }
    return sha256_bytes(canonical_json_bytes(identity))


def create_run(
    *,
    fixture_path: Path,
    fixture_manifest_path: Path,
    output_dir: Path,
    steps: int | None = None,
    learning_rate: float | None = None,
    capture_git: bool = True,
) -> tuple[dict[str, Any], Path, Path]:
    fixture, fixture_hash = load_fixture(fixture_path, fixture_manifest_path)
    config = dict(fixture["config"])
    if steps is not None:
        config["steps"] = steps
    if learning_rate is not None:
        config["learning_rate"] = learning_rate
    result = fit_toy_linear(
        fixture["records"],
        steps=config["steps"],
        learning_rate=config["learning_rate"],
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "model.json"
    run_path = output_dir / "run.json"
    model_record = {
        "schema_version": 1,
        "artifact_type": "synthetic-toy-linear-output",
        "fixture_id": fixture["fixture_id"],
        "fixture_sha256": fixture_hash,
        "weights": {"weight": result["weight"], "bias": result["bias"]},
        "training_points": len(fixture["records"]),
        "history": result["history"],
        "scope": {
            "synthetic_only": True,
            "model_quality_claim": False,
            "benchmark_claim": False,
            "production_claim": False,
        },
    }
    write_json(model_path, model_record)

    source = capture_git_provenance(PROJECT_DIR) if capture_git else {
        "available": False,
        "commit": None,
        "worktree_clean": None,
        "status_sha256": None,
        "tracked_diff_sha256": None,
        "untracked_path_count": None,
        "capture_requested": False,
    }
    environment = environment_snapshot()
    fingerprint = run_fingerprint(
        fixture_sha256=fixture_hash,
        config=config,
        environment=environment,
        source=source,
    )
    record: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": fixture["fixture_id"],
        "run_fingerprint_sha256": fingerprint,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "fixture": {
            "fixture_id": fixture["fixture_id"],
            "fixture_file": fixture_path.name,
            "sha256": fixture_hash,
            "record_count": len(fixture["records"]),
            "label_source": fixture["label_source"],
        },
        "config": config,
        "source": source,
        "environment": environment,
        "metrics": {
            "initial_mse": result["initial_mse"],
            "final_mse": result["final_mse"],
            "history": result["history"],
            "training_points": len(fixture["records"]),
        },
        "artifact": {
            "file": model_path.name,
            "sha256": sha256_file(model_path),
            "bytes": model_path.stat().st_size,
        },
        "scope": fixture["scope"],
        "tracking": {
            "backend": "manifest",
            "status": "manifest-only",
            "external_sync_requested": False,
            "api_key_required": False,
        },
    }
    write_json(run_path, record)
    return record, model_path, run_path


@contextmanager
def temporary_environment(values: dict[str, str | None]) -> Iterator[None]:
    old = {key: os.environ.get(key) for key in values}
    try:
        for key, value in values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def track_with_mlflow(
    record: dict[str, Any], model_path: Path, run_path: Path, output_dir: Path
) -> dict[str, Any]:
    import mlflow

    tracking_dir = output_dir / "mlflow"
    tracking_dir.mkdir(parents=True, exist_ok=True)
    database = tracking_dir / "tracking.db"
    tracking_uri = f"sqlite:///{database.resolve()}"
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run(run_name=f"ch60-{record['run_fingerprint_sha256'][:12]}") as run:
        mlflow.log_params(
            {
                "fixture_id": record["fixture"]["fixture_id"],
                "fixture_sha256": record["fixture"]["sha256"],
                "learning_rate": record["config"]["learning_rate"],
                "steps": record["config"]["steps"],
                "run_fingerprint_sha256": record["run_fingerprint_sha256"],
            }
        )
        mlflow.set_tags(
            {
                "git_commit": record["source"].get("commit") or "unavailable",
                "git_worktree_clean": str(record["source"].get("worktree_clean")),
                "synthetic_only": "true",
                "external_sync_requested": "false",
            }
        )
        for point in record["metrics"]["history"]:
            mlflow.log_metric("toy/mse", point["mse"], step=point["step"])
        run_id = run.info.run_id
        record["tracking"] = {
            "backend": "mlflow",
            "status": "logged-local-sqlite",
            "experiment_name": EXPERIMENT_NAME,
            "run_id": run_id,
            "storage": "local SQLite plus local artifact directory",
            "external_sync_requested": False,
            "api_key_required": False,
        }
        write_json(run_path, record)
        mlflow.log_artifact(str(model_path), artifact_path="outputs")
        mlflow.log_artifact(str(run_path), artifact_path="provenance")

    return record["tracking"]


def track_with_wandb_offline(
    record: dict[str, Any], model_path: Path, run_path: Path, output_dir: Path
) -> dict[str, Any]:
    # Force local-only mode and remove any inherited API key for this call.
    # No `wandb sync` or login operation is performed by this project.
    env = {
        "WANDB_MODE": "offline",
        "WANDB_CONSOLE": "off",
        "WANDB_DISABLE_GIT": "true",
        "WANDB_SILENT": "true",
        "WANDB_API_KEY": None,
    }
    with temporary_environment(env):
        import wandb

        output_dir.mkdir(parents=True, exist_ok=True)
        settings = wandb.Settings(
            mode="offline",
            save_code=False,
            disable_git=True,
            console="off",
            x_disable_stats=True,
            x_disable_meta=True,
            x_disable_machine_info=True,
        )
        with wandb.init(
            project="fa-academy-v4-ch14-synthetic-ops",
            name=f"ch60-{record['run_fingerprint_sha256'][:12]}",
            mode="offline",
            dir=str(output_dir),
            config={
                "fixture_id": record["fixture"]["fixture_id"],
                "fixture_sha256": record["fixture"]["sha256"],
                "learning_rate": record["config"]["learning_rate"],
                "steps": record["config"]["steps"],
                "run_fingerprint_sha256": record["run_fingerprint_sha256"],
                "synthetic_only": True,
            },
            settings=settings,
        ) as run:
            run.define_metric("step")
            run.define_metric("toy/mse", step_metric="step")
            for point in record["metrics"]["history"]:
                run.log({"step": point["step"], "toy/mse": point["mse"]})
            run.summary["fixture_sha256"] = record["fixture"]["sha256"]
            run.summary["synthetic_only"] = True
            run_id = run.id
            offline_run_dir = Path(run.dir).resolve().parent
            relative_run_dir = offline_run_dir.relative_to(output_dir.resolve()).as_posix()
            record["tracking"] = {
                "backend": "wandb",
                "mode": "offline",
                "status": "saved-locally-not-synced",
                "project": "fa-academy-v4-ch14-synthetic-ops",
                "run_id": run_id,
                "offline_run_directory": relative_run_dir,
                "external_sync_requested": False,
                "api_key_required": False,
                "automatic_code_capture": False,
                "automatic_git_capture": False,
                "system_metrics_capture": False,
            }
            write_json(run_path, record)
            artifact = wandb.Artifact(
                name=f"ch60-output-{record['run_fingerprint_sha256'][:12]}",
                type="synthetic-run-output",
                metadata={
                    "fixture_id": record["fixture"]["fixture_id"],
                    "fixture_sha256": record["fixture"]["sha256"],
                    "run_fingerprint_sha256": record["run_fingerprint_sha256"],
                    "synthetic_only": True,
                },
            )
            artifact.add_file(str(model_path), name="model.json")
            artifact.add_file(str(run_path), name="run.json")
            run.log_artifact(artifact)

    return record["tracking"]


def run_experiment(
    *,
    backend: str,
    output_dir: Path,
    fixture_path: Path = DEFAULT_FIXTURE,
    fixture_manifest_path: Path = DEFAULT_FIXTURE_MANIFEST,
    steps: int | None = None,
    learning_rate: float | None = None,
    capture_git: bool = True,
) -> dict[str, Any]:
    if backend not in {"manifest", "mlflow", "wandb-offline"}:
        raise ContractError(f"unsupported backend: {backend}")
    record, model_path, run_path = create_run(
        fixture_path=fixture_path,
        fixture_manifest_path=fixture_manifest_path,
        output_dir=output_dir,
        steps=steps,
        learning_rate=learning_rate,
        capture_git=capture_git,
    )
    if backend == "mlflow":
        track_with_mlflow(record, model_path, run_path, output_dir)
    elif backend == "wandb-offline":
        track_with_wandb_offline(record, model_path, run_path, output_dir)
    write_json(run_path, record)
    return record


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backend",
        choices=("manifest", "mlflow", "wandb-offline"),
        default="manifest",
        help="manifest-only, local SQLite MLflow, or explicitly offline W&B",
    )
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--fixture-manifest", type=Path, default=DEFAULT_FIXTURE_MANIFEST)
    parser.add_argument("--output", type=Path, default=Path("/tmp/fa-academy-ch60-run"))
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--learning-rate", type=float, default=None)
    parser.add_argument(
        "--no-git-provenance",
        action="store_true",
        help="omit local Git state from this demo run; not recommended for real experiments",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        record = run_experiment(
            backend=args.backend,
            output_dir=args.output,
            fixture_path=args.fixture,
            fixture_manifest_path=args.fixture_manifest,
            steps=args.steps,
            learning_rate=args.learning_rate,
            capture_git=not args.no_git_provenance,
        )
    except (ContractError, OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    summary = {
        "run_fingerprint_sha256": record["run_fingerprint_sha256"],
        "fixture_sha256": record["fixture"]["sha256"],
        "initial_mse": record["metrics"]["initial_mse"],
        "final_mse": record["metrics"]["final_mse"],
        "git_worktree_clean": record["source"].get("worktree_clean"),
        "tracking": record["tracking"],
        "output": str(args.output.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
