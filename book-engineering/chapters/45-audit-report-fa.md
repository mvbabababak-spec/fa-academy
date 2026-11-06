# گزارش ممیزی فصل ۴۵ — دقت عددی و Quantization

**نسخهٔ ممیزی:** پیش‌انتشار محلی، ۶ نوامبر ۲۰۲۶. **دامنه:** منبع فصل ۴۵، پروژهٔ CPU و آزمون‌های آن، تصویر، builder/checker جلد سوم، offline/PWA و پیوندهای فنی. هیچ کدام از این آزمون‌ها benchmark کیفیت یا سرعت یک مدل واقعی نیستند.

## دامنه و جلوگیری از تکرار

پیش از نگارش، `BOOK_ROADMAP_FA.md` به‌طور کامل خوانده و workspace و remote برای `45-precision` بررسی شد. نقشه از قبل فصل ۴۵ را به‌عنوان فصل محلی ۱۳ جلد سوم تعریف می‌کرد. در مرور تازهٔ remote، `HEAD` و `origin/gh-pages` هر دو روی `9282eff7e436e8a47347fc5ffb69cc8ddc585d9a` بودند و نه منبع فصل ۴۵ و نه پروژهٔ آن در remote وجود نداشت. منبع قبلی فصل‌های ۴۲، ۴۳ و ۴۴ و درس‌های گزارش‌های فصل‌های ۱، ۲، ۴۰ و ۴۱ لحاظ شد.

فصل ۴۲ بودجهٔ Mini GPT را طراحی می‌کند و فصل ۴۴ schedule، حلقهٔ FP32 و checkpoint/resume را؛ این فصل آن کارها را دوباره نمی‌سازد. دامنهٔ تازه، range در برابر precision، FP16/BF16/FP8، scaling، affine quantization، PTQ/QAT، پایداری عددی و سازگاری hardware است. پروژه به‌جای آموزش مدل جدید، behavior قابل‌اندازه‌گیری dtype/quantization را در CPU نشان می‌دهد.

## محتوای آموزشی و منابع

فصل ۲۷ بخش دارد و ۶ MathML دسترس‌پذیر برای نمایش عدد شناور، epsilon، loss scaling، FP8 scaling، affine quantization و نسبت saturation. مرزهای FP8 از OCP OFP8 revision 1.1 مورخ ۲۹ ژانویه و مؤثر ۲۲ ژوئن ۲۰۲۶ بررسی شد؛ MX از OCP MX v1.1 مورخ ۹ اکتبر ۲۰۲۶. BF16 با مستندات PyTorch 2.6، Google Cloud و مطالعهٔ arXiv مقایسه شد. PyTorch AMP 2.6، TorchAO QAT/inference v0.17.0 (`main`, unstable در صفحهٔ مورخ ۵ نوامبر ۲۰۲۶)، و راهنمای قابل‌واکشی Transformer Engine 2.20.2 نیز بازبینی شدند. در متن، پشتیبانی dtype، kernel، سخت‌افزار و کیفیت workload به‌عنوان ادعاهای جدا نگه داشته شده‌اند؛ نتیجهٔ paper یا صفحهٔ vendor به همهٔ مدل‌ها تعمیم داده نشده است.

در منبع Transformer Engine، به‌جای URL قدیمی و ازکارافتادهٔ صفحهٔ scaling، راهنمای فعلی [Using FP8 and FP4](https://docs.nvidia.com/deeplearning/transformer-engine/examples/fp8_primer.html) استفاده شد. این منبع current-iteration `amax` و delayed scaling بر مبنای history را در context همان library شرح می‌دهد. تاریخ مراجعه به مراجع فصل: ۶ نوامبر ۲۰۲۶.

## پروژه و نتایج محلی

نیازمندی پروژه Python 3.11+ و PyTorch 2.6.x CPU است. کد `precision_lab.py` از `torch.finfo`، cast رفت‌وبرگشت، CPU BF16 autocast و یک پیاده‌سازی آموزشی symmetric/affine quantization استفاده می‌کند. `test_precision_lab.py` ده آزمون دارد.

در `.venv/bin/python` با PyTorch `2.6.0+cpu`، **۱۸۰ آزمون واحد پروژه‌های فصل‌های ۳۳ تا ۴۵** موفق شدند. CLI فصل ۴۵ هم JSON ساخت و checkهای version، finite output، saturation `2/3` و RMSE پایین‌تر per-group را گذراند. در بردار مصنوعی، RMSE per-tensor `0.02752798` و per-group `0.02008443` بود. CPU BF16 autocast خروجی متناهی داد و بیشینهٔ اختلاف Linear کوچک از FP32 `0.00229204` شد؛ این دو اندازه‌گیری benchmark نیستند. PyTorch در محیط محلی یک هشدار غیرمسدودکننده دربارهٔ نبود NumPy داد؛ پروژه به NumPy وابستگی ندارد و تمام آزمون‌ها موفق بودند.

مشاهدهٔ FP8 محدود است: PyTorch همین runtime dtypeهای `float8_e4m3fn` و `float8_e5m2`، `torch.finfo` و cast را روی CPU اجرا کرد. هیچ FP8 GEMM، CUDA/ROCm/XPU، سخت‌افزار خاص، throughput، training یا مدل واقعی آزمایش نشد. پروژهٔ quantization هم فقط بردارهای کوچک را می‌سنجد؛ bit-packing زیر ۸ bit و هزینهٔ واقعی metadata/kernel را پیاده نمی‌کند.

## شکل، ساخت کتاب و یکپارچه‌سازی

شکل ۳-۱۳-۱ از SVG محلی و Chromium ساخته شد: WebP lossless با ابعاد `1600×1000` و اندازهٔ ثبت‌شدهٔ `149,996` بایت. شکل محدودهٔ FP32/FP16/BF16/E4M3/E5M2 را با مسیرهای mixed precision و quantization تفکیک می‌کند؛ alt فارسی محتوا، کلمات کلیدی و مقصد hardware را توصیف می‌کند.

`build_volume3.py` فصل را ۱۳/۱۴ ساخت و شمار بخش‌ها به ۲۳۸ رسید. refresh فقط پس از بررسی تازهٔ remote و بررسی ۲۷ شناسهٔ پایدار محلی انجام شد. اجرای دوبارهٔ builder بدون گزینهٔ refresh idempotent بود: `data.json` و `volume-3-full-fa.md` هیچ diffی نداشتند. `check_volume3.py` برای فصل ۴۵ هم هم‌ترازی byte-for-byte پیوست اجرایی با فایل تست‌شده، پروژه، شکل و این گزارش را بررسی می‌کند.

سه checker محتوایی موفق شدند: جلد اول ۲۱ فصل/۲۳۶ بخش/۲۷ تصویر/۶ MathML؛ جلد دوم ۱۱ فصل/۱۰۱ بخش/۱۱ تصویر/۱۱ پاسخ‌نامه/۱۵ MathML؛ جلد سوم ۱۳ فصل/۲۳۸ بخش/۱۳ تصویر/۱۳ پاسخ‌نامه/۵۷ MathML. Service Worker از v70 به v71 ارتقا یافت؛ فهرست offline به ۱۰۶ فایل با شکل، chapter، answer، گزارش و پروژهٔ فصل ۴۵ گسترش پیدا کرد. Chromium در viewportهای ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل موفق شد: ۲۳۸ بخش، ۵۷ MathML، ۱۳ تصویر، search، شناسه‌های پایدار، ناوبری، overflow و دسترسی offline بررسی شدند؛ page error وجود نداشت. در لاگ یک GET 404 برای thumbnail قدیمی `assets/images/genai/repo-thumbnailv4-fixed.11f1ce6a85d01461.webp` از کارت خارج از فصل ۴۵ دیده شد؛ فایل جزو دارایی‌های فصل ۴۵/جلد سوم نیست و آزمون مرورگر با وجود آن موفق بود. Browser test جلد دوم نیز در عرض‌های ۳۲۰/۳۹۰/۱۴۴۰ و آزمون mobile در ۳۲۰/۳۹۰/۴۱۴/۷۶۸/۱۴۴۰ موفق شد؛ هر بار به‌ترتیب ۱۰۱ و ۷۷۸ بخش بررسی شد. لاگ legacy چند 404 برای assetهای قدیمی Rosenblatt/Mark-I و یک فایل تصویری DALL·E داشت که خارج از دارایی‌های فصل ۴۵ بود. `.github/workflows/volume3-audit.yml` ده آزمون و اجرای CLI فصل ۴۵ را به jobهای قبلی اضافه می‌کند.

## محدودیت‌ها و تصمیم انتشار

این ممیزی موارد زیر را اثبات نمی‌کند: صحت آموزش یا کیفیت benchmark یک مدل واقعی؛ سرعت FP16/BF16/FP8؛ سازگاری تمام operatorها/deviceها؛ برابری عددی بین نسخه‌ها یا backendها؛ اجرای MX hardware؛ صحت calibration بر دادهٔ deployment؛ یا افزایش accuracy ناشی از QAT. برای هر deployment باید framework/driver/device/shape، recipe، calibration، test metric و latency واقعی ثبت شود. فصل برای انتشار به یک commit مستقل نیاز دارد؛ پس از push remote و GitHub Actions باید جداگانه بررسی شوند.
