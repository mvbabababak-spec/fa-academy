# گزارش ممیزی فصل ۴۶ — مقیاس، activation checkpointing و بازیابی run

**تاریخ:** ۶ نوامبر ۲۰۲۶ · **وضعیت:** commit مستقل فصل `c2e210e84fe591ee3fb866eef922553d0382e055` روی `gh-pages` منتشر شد؛ remote، CI جلدهای ۱ تا ۳ و Pages بررسی و موفق شدند. **دامنه:** منبع فصل، پروژهٔ دوپردازهٔ CPU، شکل و یکپارچه‌سازی جلد سوم. این گزارش هیچ ادعای benchmark مدل/سخت‌افزار یا اجرای چند GPU واقعی ندارد.

## پیش‌بررسی و جلوگیری از تکرار

پیش از نگارش، تمام `BOOK_ROADMAP_FA.md` خوانده شد. فصل ۴۶ «Gradient Checkpointing، آموزش توزیع‌شده، ردیابی آزمایش و مدیریت خطا» است و حرکت از نمونهٔ کوچک به بزرگ را هدف می‌گیرد. پس از انتشار و CI موفق فصل ۴۵، workspace و `origin/gh-pages` در commit `6fdf5322f7f5ecc216217cc9526f6ed4d73432f0` بررسی شدند؛ فایل فصل/پاسخ/پروژهٔ ۴۶ در هر دو غایب بود. فصل‌های ۸، ۴۲ تا ۴۵ و گزارش‌های ممیزی فصل‌های ۱، ۲، ۴۰ و ۴۱ برای مرزبندی و درس‌های ویراستاری مرور شدند.

فصل ۸ مفاهیم پایهٔ توپولوژی و Data/Model Parallelism و یک شبیه‌ساز ترتیبی میانگین گرادیان دارد؛ پروژهٔ این فصل از آن کد تکرار نمی‌سازد. فصل ۴۲ برآورد tensor/حافظه را می‌دهد؛ فصل ۴۳ نسخه و provenance داده را ممیزی می‌کند؛ فصل ۴۴ برنامهٔ optimizer، accumulation و checkpoint/resume تک‌پردازشی را می‌آزماید؛ فصل ۴۵ precision و ثبت state وابسته به recipe را پوشش می‌دهد. فصل ۴۶ این پایه‌ها را برای ترکیب روش‌های موازی، activation recomputation و بازیابی هماهنگ در jobهای بزرگ‌تر به کار می‌گیرد.

## منابع، پیاده‌سازی و دامنه

مستندات PyTorch 2.6 برای `torch.utils.checkpoint`, DDP، FSDP، Distributed Checkpoint و `torchrun` با همین نسخه بازبینی شدند. هشدارهای non-reentrant، RNG، هم‌ترازی کاهش گرادیان، تغییر rank/world size، چندفایلی‌بودن DCP و نبود تضمین backward compatibility در فصل به محدودیت تبدیل شده‌اند. مقاله‌های Chen et al. (2016)، ZeRO (2019/2020)، Megatron-LM (2019) و selective recomputation (2022) به‌عنوان نتایج همان setupها معرفی شده‌اند، نه وعده برای هر مدل. مستندات جاری MLflow در ۶ نوامبر ۲۰۲۶ برای مفاهیم run/experiment/metrics/artifacts بررسی شد؛ پروژهٔ درس به آن وابسته نیست.

پروژه، یک مدل feed-forward بسیار کوچک را با و بدون `use_reentrant=False` مقایسه می‌کند و از hookهای autograd فقط تعداد بایت tensorهای ذخیره‌شده را می‌شمارد. بخش دیگر دو rank واقعی CPU/Gloo ایجاد می‌کند؛ هر rank shardی از پنج نمونه می‌گیرد و گرادیان میانگین DDP را با backward تک‌پردازشی می‌سنجد. JSON محلی config، نسخه‌ها و hashهای کد/fixture را ثبت می‌کند.

## نتایج نهایی محلی

- هر ۱۴ پروژهٔ جلد سوم اجرا شدند: **۱۹۰/۱۹۰ آزمون واحد موفق**؛ پروژهٔ فصل ۴۶ به‌تنهایی ۱۰/۱۰. در اجرای PyTorch 2.6.0+cpu/Python 3.13، warning محیطیِ نبود NumPy در virtualenv دیده شد، اما هیچ آزمونی به آن وابسته نبود و همه موفق شدند.
- CLI فصل ۴۶ saved-tensorهای hook را در fixture از **۴٬۰۱۶ به ۶۸۸ بایت** رساند؛ اختلاف خروجی، گرادیان ورودی و گرادیان پارامترها صفر بود. دو rank در Gloo با shardهای `[3, 2]` گرادیان `−33.0` را با مرجع تک‌پردازشی تطبیق دادند. این نتیجه فقط correctness همین fixture است.
- checkerهای جلدهای ۱، ۲ و ۳ موفق شدند. جلد سوم: **۱۴ فصل، ۲۶۵ بخش، ۱۴ تصویر، ۱۴ پاسخ‌نامه و ۶۰ بلوک MathML دسترس‌پذیر**. builder پس از اجرا، `data.json` و `volume-3-full-fa.md` را عیناً ثابت گذاشت.
- آزمون Chromium جلد سوم در ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل موفق شد: بخش‌ها، فرمول‌ها، تصویرها، overflow، search، navigation و **۱۱۵ فایل آفلاین** بررسی شدند. آزمون جلد دوم در همان سه عرض و آزمون layout موبایل در ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل نیز موفق شدند.
- smoke testهای CLI فصل‌های ۴۲، ۴۳، ۴۴ (آموزش کامل و resume با history/metrics یکسان) و ۴۵ موفق شدند. WebP شکل **۱۶۰۰×۱۰۰۰** است؛ SHA-256: `4e060a7d0c9d069f67cfd7e8ce7f2a935701fa79218115eb77cb08981bedd1fe`.
- commit انتشار فصل `c2e210e84fe591ee3fb866eef922553d0382e055` پس از push با `origin/gh-pages` تطبیق داده شد. CIهای push برای جلد ۱ ([run 42171983701](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42171983701))، جلد ۲ ([run 42171983694](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42171983694)) و جلد ۳ ([run 42171983562](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42171983562)) همگی `success` شدند. GitHub Pages وضعیت `built` گزارش کرد؛ سایت زنده در [mvbabababak-spec.github.io/fa-academy](https://mvbabababak-spec.github.io/fa-academy/) با ۱۴ فصل جلد سوم، ۲۷ بخش فصل ۱۴، Service Worker v72 و همان hash شکل پاسخ داد.
- annotations غیرمسدودکنندهٔ runner به deprecation مربوط به Node 20 در `actions/checkout@v4` و `actions/setup-python@v5` و مهاجرت آیندهٔ `ubuntu-latest` به Ubuntu 26 اشاره داشتند؛ هیچ jobی شکست نخورد.
- در لاگ Chromium یک درخواست 404 برای thumbnail قدیمیِ بیرون از فصل/جلد سوم دیده شد؛ مطابق گزارش فصل ۴۵، دارایی از قبل در کارت عمومی وجود ندارد و مانع آزمون یا نمایش محتوای فصل نشد. خطای JavaScript صفحه ثبت نشد.

## محدودیت‌ها و گیت انتشار

شمار saved-tensorها peak memory یا fragmentation نیست؛ Gloo دوپردازه روی یک میزبان، آموزش چند GPU/node، NCCL، latency، throughput، کیفیت زبان، recovery پس از خرابی واقعی یا تغییر topology را نمی‌آزماید. run fingerprint امضای امنیتی یا تضمین بازتولید بین سخت‌افزار/نسخه‌ها نیست. checkerها، ۱۹۰ آزمون پروژه، idempotence builder، browser جلد دوم/سوم، آزمون mobile و `git diff --check` برای انتشار commit بالا موفق شدند. commit به‌صورت معمولی push شد، با remote تطبیق یافت و workflowهای سه جلد و Pages موفق شدند؛ force push انجام نشد.
