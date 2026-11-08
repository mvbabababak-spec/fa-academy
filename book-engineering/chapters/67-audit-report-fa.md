# گزارش ممیزی فصل سراسری ۶۷ — سرو، صف و cache پاسخ

**نگاشت:** فصل محلی ۶ جلد پنجم = فصل سراسری ۶۷. **تاریخ ممیزی محلی: ۸ نوامبر ۲۰۲۶.** پیش از نگارش، ساختار پنج جلد از `data.json` و نقشهٔ رسمی، فصل ۶۱ جلد چهارم، فصل ۶۶، راهنمای سبک جلد پنجم و گزارش‌های ممیزی فصل‌های ۶۲–۶۵ مرور شدند. در remote `gh-pages` برابر `71e8cb4da94c0f2ddb56bf38868281fb7988ff40` هیچ فایل فصل ۶۷ وجود نداشت؛ فصل ۶۶ پیش‌تر تکمیل و منتشر شده است و این کار آن را تکرار نمی‌کند.

## دامنه و مرز موضوعی

فصل ۶۱ موتورهای inference، batch داخلی runtime، KV/prefix cache و benchmark سطح موتور را پوشش می‌دهد؛ فصل ۶۶ قرارداد API و frontend/backend را می‌سازد؛ فصل ۶۷ روی صف سطح محصول، microbatch، cache پاسخ دقیق و latency/throughput trace تمرکز دارد. احراز هویت، rate limiting، telemetry، privacy و پاسخ رخداد در فصل ۶۸، و deployment/CI/CD در فصل ۶۹ باقی می‌مانند. پروژهٔ همراه یک شبیه‌ساز deterministic CPU است؛ نه مدل یا runtime تولیدی.

## داده و محیط

- Fixture: `book-engineering/projects/67-serving-lab/synthetic_serving_trace.json`، شناسهٔ `v5-ch06-serving-synthetic-v1`، ۲۴ درخواست و ۱۲ کلید دقیق یکتا؛ SHA-256: `2082e82cc4e68ec031715c6429c225cf06e77124fe2c565fe397613fbbbf7e0c`.
- داده، زمان‌ها، tokenها و پاسخ‌ها دستی و ساختگی‌اند؛ دادهٔ شخصی، trace تولیدی، درخواست HTTP بیرونی، GPU و مدل زنده به‌کار نرفته‌اند.
- CPython 3.13.16، Linux x86_64/glibc 2.41، کتابخانهٔ استاندارد و بدون وابستگی ثالث.
- شبیه‌ساز یک worker، صف FIFO محدود، پنجرهٔ batch و cache پاسخ محدود را اجرا می‌کند؛ ضرایب زمان fixture فرضی‌اند، نه اندازه‌گیری.

## نتیجهٔ اجرای پروژه

`python -m unittest -v` در پوشهٔ پروژه **۱۷ از ۱۷ آزمون** را گذراند. آزمون‌ها schema و یکتایی شناسه‌ها، deterministic بودن، کلید نسخه‌دار، Little’s Law، nearest-rank percentile، اعتبارسنجی نوع پیکربندی، سقف صف، batch wait، hit پس از تکمیل، عدم hit پیش از تکمیل، bound حافظه/LRU و آشکارشدن برخورد کلید را بررسی می‌کنند. اجرای CLI روی fixture با `results.json` برابر است.

| سیاست | پاسخ کامل / رد صف | محاسبه / hit | p50 / p95 پاسخ (ms) | دیرکرد | تکمیل بر ثانیه | تطبیق fixture بر ثانیه |
|---|---:|---:|---:|---:|---:|---:|
| `baseline_one_at_a_time` | ۲۰ / ۴ | ۲۰ / ۰ | ۱۷۷٫۰ / ۳۳۳٫۶ | ۱۰ | ۸٫۴۶۲ | ۸٫۴۶۲ |
| `microbatch_only` | ۲۴ / ۰ | ۲۴ / ۰ | ۱۰۱٫۳ / ۱۷۹٫۵ | ۰ | ۱۰٫۸۷۷ | ۱۰٫۸۷۷ |
| `exact_response_cache_only` | ۲۲ / ۲ | ۱۲ / ۱۰ | ۲۸٫۲ / ۳۰۸٫۲ | ۵ | ۱۰٫۴۲۸ | ۱۰٫۴۲۸ |
| `microbatch_plus_exact_cache` | ۲۴ / ۰ | ۱۲ / ۱۲ | ۱٫۵ / ۱۷۶٫۲۵ | ۰ | ۱۱٫۷۹۷ | ۱۱٫۷۹۷ |

`completed_responses_per_second` تکمیل‌های دیرشده را هم می‌شمارد؛ `fixture_correct_responses_per_second` تطبیق رشتهٔ مرجع را می‌شمارد، اما deadline را شرط نمی‌کند. در مسیر model-miss، شبیه‌ساز رشتهٔ مرجع را از خود fixture برمی‌گرداند؛ بنابراین برابری قراردادی است و هیچ‌یک goodput یا کیفیت مدل واقعی نیست. `output_integrity_rate=1.0` سهم پاسخ‌های کامل‌شدهٔ منطبق را نشان می‌دهد و درخواست‌های ردشده را شامل نمی‌کند. آزمون برخورد کلید پاسخ cacheشدهٔ ناسازگار را علامت می‌زند. هیچ مدل زبانی اجرا نشده است. خروجی کامل و محدودیت‌ها در `projects/67-serving-lab/results.json` ثبت شده‌اند.

## ساختار کتاب و آزمون‌های وب

گیت‌های محلی نهایی موفق شدند:

- `build_volume5.py` و `check_volume5.py`: شش فصل فعال از دوازده فصل برنامه‌ریزی‌شده، با شمار بخش‌های `[26, 34, 39, 41, 40, 28]`؛ خروجی Markdown و `data.json` با منابع همگام، ۷۸ مسیر آفلاین برای فصل‌های جلد پنجم و Service Worker نهایی نسخهٔ `v107`.
- Checkerهای جلدهای ۱ تا ۵ و `node --check sw.js`: همگی موفق؛ `pip check` نیز موفق.
- پروژه‌های ۶۲ تا ۶۷: به‌ترتیب ۹/۹، ۱۵/۱۵، ۲۰/۲۰، ۱۲/۱۲، API فصل ۶۶ برابر ۱۲/۱۲ به‌علاوهٔ ۲ آزمون مرورگر، و پروژهٔ ۶۷ برابر ۱۷/۱۷. خروجی CLI هر شش پروژه با `results.json` متناظر برابر شد.
- `test_volume5.py`: PASS در عرض‌های ۳۲۰، ۳۹۰، ۷۶۸ و ۱۴۴۰ پیکسل؛ شش فصل، ۷۸ مسیر آفلاین، MathML/SVG دسترس‌پذیر و پیوست‌های کد دقیق.
- `test_mobile_layout.py`: PASS در ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل؛ ۱۳۵۷ بخش، ناوبری RTL، نمایش متن، پوشش فایل‌های فصل‌های ۵۵–۶۷ و مسیرهای آفلاین. لاگ وب‌سرور در همین آزمون ۳۷ درخواست 404 برای ۸ مسیر تصویریِ قدیمی و نامرتبط با فصل‌های ۶۲–۶۷ (از جمله تصاویر legacy فصل ۳۵ و گزارش فصل ۶۱) ثبت کرد؛ این assetها دست‌نخورده ماندند و آزمون سبز است.
- `test_volume2.py`, `test_volume3.py`, `test_volume4.py`: همگی PASS؛ به‌ترتیب ۱۰۱ بخش/۲۲ asset آفلاین، ۲۶۵ بخش/۶۰ MathML/۱۱۵ فایل آفلاین، و ۱۵ فصل با پیوست‌ها و ۱۶۲ asset آفلاین.
- `test_offline_volume.py`: PASS، شامل ۲۱ پاسخ‌نامه و ۲۷ تصویر جلد؛ `test_pwa_icon.py`: PASS، شامل manifest، ابعاد PNG، قابلیت نصب Chromium و assetهای آفلاین.
- رندر دیداری فصل ۶۷ در ۳۹۰ و ۱۴۴۰ پیکسل در `.tmp-audit/ch67-mobile-390.png` و `.tmp-audit/ch67-desktop-1440.png` ذخیره و بازبینی شد؛ این‌ها artifactهای محلی ممیزی‌اند و در انتشار محصول وارد نمی‌شوند. فایل محافظت‌شدهٔ `book-engineering/reports/browser-mobile.webp` دست‌نخورده ماند.

`test_browser_audit.py` در clone محلی عمداً اجرا نشد، چون آن اسکریپت تصویر محافظت‌شدهٔ `book-engineering/reports/browser-mobile.webp` را می‌نویسد. اجرای همان step در workflow جلد اول روی runner موقت، جداگانه در بخش انتشار ثبت شده است. آزمون‌های responsive محلی جایگزین آن معرفی نمی‌شوند و برای آن‌ها ادعای موفقیت ثبت نشده است.

## وضعیت انتشار

- فصل و پروژه در commit مستقل `2c1e8b3ea7f14e46ee509b87c29832a7381991a0` با parent برابر baseline `71e8cb4da94c0f2ddb56bf38868281fb7988ff40` روی `gh-pages` با push عادی منتشر شدند؛ `ls-remote` شاخه را روی همان SHA تأیید کرد.
- GitHub Actions برای همان commit موفق شد: جلد ۱ [run #81](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42426865567)، جلد ۲ [#64](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42426865564)، جلد ۳ [#63](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42426865555)، جلد ۴ [#43](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42426865546) و جلد ۵ [#11](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42426865554). هر پنج workflow نتیجهٔ `success` داشتند.
- Pages [run #149](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42426865245) موفق شد؛ deployment شناسهٔ `7628756524` به SHA بالا اشاره دارد و URL آن [mvbabababak-spec.github.io/fa-academy](https://mvbabababak-spec.github.io/fa-academy/) است. دریافت زندهٔ `data.json`، فایل Markdown جلد پنجم، سورس و گزارش فصل ۶۷ همگی HTTP 200 دادند؛ دادهٔ منتشرشده ۶ فصل فعال از ۱۲ فصل برنامه‌ریزی‌شده، ۲۰۸ بخش در جلد پنجم و ۲۸ بخش در فصل ۶۷ نشان می‌دهد. انتشار اولیه Service Worker نسخهٔ `v106` داشت؛ در تغییر پیگیری این گزارش، نسخه به `v107` ارتقا داده شد تا گزارش تازه در cache-first آفلاین نیز به‌روز شود.
- فایل `book-engineering/reports/browser-mobile.webp` در شاخهٔ منتشرشده وجود ندارد (درخواست خام آن 404 می‌دهد) و در clone محلی نیز ساخته یا تغییر داده نشد. نکتهٔ مهم: `test_browser_audit.py` عمداً در clone محلی اجرا نشد؛ بااین‌حال workflow موجود جلد اول در run #81 همین آزمون را خودکار روی runner موقت GitHub اجرا کرد و موفق شد. run هیچ artifact تصویری منتشر نکرد و فایل موقتی runner به شاخه یا Pages منتقل نشد.

پیوندهای CI و Pages در این بخش وضعیت انتشار محتوای فصل را برای commit `2c1e8b3ea7f14e46ee509b87c29832a7381991a0` مستند می‌کنند.

## محدودیت نتیجه

شبیه‌ساز رشتهٔ مرجع fixture را برای model-miss به‌طور قراردادی بازمی‌گرداند؛ مقدار تطبیق ۱۰۰٪ در آن مسیر از فرض مدل می‌آید، نه آزمون مستقل انتقال. این مقدار quality، factuality، safety، latency یا throughput یک مدل واقعی را نمی‌سنجد. trace کوچک، نمونه‌گیری یا confidence interval ندارد. token/KV واقعی، حافظهٔ process/GPU، runtime، network، endpoint، streaming، چند worker، autoscaling، cancellation، authentication، مجوز و privacy بررسی نشده‌اند. محصول این milestone وب/PWA و Markdown است؛ PDF و EPUB تولید یا آزموده نشده‌اند.
