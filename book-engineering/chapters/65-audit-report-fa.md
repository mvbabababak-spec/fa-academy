# گزارش ممیزی فصل سراسری ۶۵ — هم‌ترازی و حکمرانی

**نگاشت:** فصل محلی ۴ جلد پنجم = فصل سراسری ۶۵. **تاریخ ممیزی: ۷ نوامبر ۲۰۲۶.** این گزارش نتایج fixture ساختگی، آزمون‌های محلی و وضعیت انتشار را از هم جدا می‌کند. `structurally_valid` برای یک بستهٔ آموزشی است و هرگز مجوز استقرار یا ادعای انطباق نیست.

## دامنه و محیط

- پروژه: `book-engineering/projects/65-governance-lab/`؛ CPython 3.13.16؛ فقط کتابخانهٔ استاندارد Python.
- Fixture: `governance_pack.json`؛ شناسهٔ `v5-ch04-governance-pack-synthetic-v1`؛ SHA-256: `9a2fb3e97951f5e06eabf0a6fdb10e982f9ad7e738f4766049eb28fb4714dea6`؛ بستهٔ کاملاً ساختگی با چهار ریسک و پنج شناسهٔ شاهدِ نمونه.
- دستورات: `python -m unittest discover -v` و `python governance_check.py --output results.json`.
- پروژه نه مدل، API، شبکه، دادهٔ شخصی، endpoint، ارزیابی حقوقی، بررسی privacy واقعی یا تصمیم انسانی انتشار اجرا می‌کند.

## نتایج fixture

| خروجی | نتیجهٔ پروژه | تفسیر مجاز |
|---|---:|---|
| آزمون واحد پروژه | ۱۲ از ۱۲ موفق | قرارداد schema و منطق validator برای fixture، از جمله رد typeهای نامناسب بدون crash |
| ریسک‌ها / شاهدها | ۴ / ۵ | شمارش رکوردهای ساختگی، نه inventory محصول |
| اعتبار ساختاری | `true`؛ خطای ساختاری صفر | فیلدها و پیوندهای داخلی با قرارداد همین validator سازگارند |
| دروازه | `hold` | نمونهٔ آموزشی؛ هیچ بررسی واقعی تکمیل نشده است |
| مجوز انتشار | `false` | کد عمداً هیچ‌گاه مجوز انتشار صادر نمی‌کند |

validator حضور فیلدها، قالب مقدارهای کیفی، یکتایی شناسه‌ها، تاریخ‌های ISO و ارجاع داخلی شاهدها را می‌سنجد. وجود شناسهٔ شاهد به‌معنای وجود مدرک نیست؛ خود fixture وضعیت‌های `planned` و `fixture_only` دارد.

## اعتبارسنجی ساختار کتاب و مرورگر

- `python book-engineering/check_volume5.py` موفق شد: جلد پنجم ۴/۱۲ فصل، بخش‌ها `[26, 34, 39, 41]`، SVG و MathML دسترس‌پذیر، صورت‌پرسش‌های عیناً منطبق با پاسخ‌نامه، پیوست کد بایت‌به‌بایت، ۵۱ مسیر آفلاین و Service Worker نسخهٔ ۱۰۳.
- `python book-engineering/test_volume5.py` در عرض‌های ۳۲۰، ۳۹۰، ۷۶۸ و ۱۴۴۰ پیکسل موفق شد؛ چهار فصل و ۱۴۰ بخش، شکل‌ها، فرمول‌ها، پیوندهای همراه، پیوست‌های اجرایی دقیق و cache آفلاینِ ۵۱ مسیر را وارسی کرد.
- `python book-engineering/test_mobile_layout.py` در عرض‌های ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل موفق شد؛ ۱٬۲۸۹ بخشِ مجموعهٔ کتاب/دوره پیموده شد. برای جلد پنجم ۳۱۵ بند نثرِ هم‌تراز، ۱۷۷ بند تورفته، ۵ بلوک MathML و ۴ کپشن بررسی شدند.
- آزمون‌های پروژه: فصل ۶۲، ۹/۹؛ فصل ۶۳، ۱۵/۱۵؛ فصل ۶۴، ۲۰/۲۰؛ فصل ۶۵، ۱۲/۱۲. CLIها و hashهای fixture با نتایج مرجع برابر بودند؛ فصل ۶۵ `structurally_valid: true`, `gate_status: hold`, `release_authorized: false` گزارش کرد.
- اجرای دوبارهٔ `build_volume5.py` idempotent بود؛ `data.json`, `sw.js` و `volume-5-full-fa.md` با نسخهٔ قبل از اجرا byte-for-byte برابر ماندند. `node --check sw.js` و `git diff --check` نیز موفق شدند.
- محیط مرورگر: CPython 3.13.16، Playwright 1.64.1 و Chromium 156.0.8078.4؛ browser dependencies با دستور رسمی `python -m playwright install --with-deps chromium` نصب شدند.

این worktree یک checkout sparse/partial است. هنگام `test_mobile_layout.py`، ۲۵ فایلِ قدیمیِ موردنیاز آزمون آفلاین (کاورهای Microsoft و چند سند/نمودار فصل‌های پیشین) موقتاً از blob همان `HEAD` materialize شدند؛ SHA-1 Git با blob مرجع برابر بود و فایل‌ها پس از آزمون حذف شدند. آزمون همچنان برای تصاویر/سندهای قدیمیِ نامرتبط که در sparse checkout حضور ندارند، ۴٬۲۳۰ لاگ HTTP 404 ثبت کرد؛ این‌ها مسیرهای خارج از assertionهای هدف بودند. assertionهای layout، فصل‌های ۶۲–۶۵، کاورها و پوشش آفلاینِ خواسته‌شده همگی موفق شدند. هیچ تصویر پیوست یا مرجع و هیچ محتوای فصل منتشرشده‌ای ویرایش نشد.

## انتشار و remote/CI

فصل محلی ۴ جلد پنجم / فصل سراسری ۶۵ در commit مستقل `546b4c000278de40fec43b4809d677d61e63f2cc` با push عادی روی `gh-pages` منتشر شد؛ در لحظهٔ انتشار، `git ls-remote origin refs/heads/gh-pages` همین SHA را برگرداند. هر شش workflow روی همان commit موفق شدند:

- [Volume 1 — run 42387303368](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42387303368)
- [Volume 2 — run 42387303556](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42387303556)
- [Volume 3 — run 42387303480](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42387303480)
- [Volume 4 — run 42387303420](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42387303420)
- [Volume 5 — run 42387303359](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42387303359)
- [ساخت و استقرار GitHub Pages — run 42387303623](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42387303623)

در workflow جلد پنجم، آزمون‌های پروژه‌های ۶۲–۶۵، idempotence سازنده و آزمون‌های browser/responsive/offline موفق شدند؛ پروژهٔ فصل ۶۵ دوازده آزمون واحد را گذراند. workflow صفحات نیز artifact با اندازهٔ ۱۳۳ MB و digest `sha256:43d24c16d441a86d29abb75f4ae9dbfa375f342d9fd2bbede47bf412de4717d5` ساخت و deploy کرد. هشدارهای runner دربارهٔ مهاجرت Node.js و Ubuntu اطلاعیه‌های غیرمسدودکننده بودند؛ گام شکست‌خورده‌ای وجود نداشت.

پس از deploy، [نسخهٔ زندهٔ وب/PWA](https://mvbabababak-spec.github.io/fa-academy/) و فایل‌های اصلی با HTTP 200 پاسخ دادند. `data.json` زنده چهار فصل منتشرشدهٔ جلد پنجم را نشان داد و فصل محلی ۴ را با ۴۱ بخش فهرست کرد. ده فایل منتخب از صفحهٔ زنده byte-for-byte با فایل‌های محلیِ commit فصل برابر بودند. جدول زیر hashهای دریافت زنده در همان انتشار فصل را ثبت می‌کند؛ گزارش ممیزی نیز HTTP 200 داد، اما hash خودش در جدول نیست چون همین گزارش در commit پیگیری به‌روزرسانی می‌شود.

| فایل زنده در انتشار فصل | SHA-256 دریافت‌شده |
|---|---|
| `data.json` | `2fc0722493ea182f67e054751a7251d2bf5881477a3608bc349c6d5a7e37c1dc` |
| `sw.js` (نسخهٔ ۱۰۱) | `0352f6f7a54e763165d5c4943f7ac0857540f6128a969711d658fc3964df311a` |
| `volume-5-full-fa.md` | `f86358f47e662222e612fa53cd5822a03bbb5a20cc3b41e0224d00cbeb2a9cac` |
| `book-engineering/chapters/65-alignment-governance.md` | `e470ef7e08fe18a7fb20f7fe6354895ae6fbf61b00e8257f50af68d581404461` |
| `book-engineering/answers/65-alignment-governance-fa.md` | `6079543c1a52d119468309c39176ff4019e2429102d72b5e4e5b26d3a002df94` |
| `book-engineering/diagrams/v5-ch04-governance-cycle.svg` | `c4869b69e9baa447fffd62a2867445e88042790e8ffadc6dfd82c862dff479e6` |
| `book-engineering/projects/65-governance-lab/results.json` | `739057069b4c913f7fc94963941d59d725eed95b9da4e81895f41392e7696206` |

گزارش در cache آفلاین قرار دارد. commit پیگیری `1a7b789ad2bf3573e6449690ce03a79ed8c0bddf` Service Worker را از نسخهٔ ۱۰۱ به ۱۰۲ ارتقا داد؛ در اصلاح حاضر، Service Worker به نسخهٔ ۱۰۳ رسید تا گزارش تازه در cache جایگزین شود.

## محدودیت‌ها

۱. داده‌ها، سامانه، نقش‌ها، ریسک‌ها و شناسه‌های شاهد ساختگی‌اند؛ هیچ فرد، سازمان، مدل یا سند حقیقی ارزیابی نشده است.
۲. validator ساختار JSON و پیوند داخلی را می‌سنجد، نه حقیقت، کیفیت، کفایت یا مستقل‌بودن شواهد را.
۳. برچسب‌های شدت و احتمال کیفی‌اند؛ احتمال آماری یا score تجمعی محاسبه نمی‌شود.
۴. نتیجهٔ ساختاری به معنی طبقه‌بندی حقوقی، انطباق، ایمنی، انصاف، privacy، تناسب کاربرد یا آمادگی انتشار نیست.
۵. `release_authorized` همیشه `false` است؛ تصمیم دربارهٔ یک کاربرد واقعی باید از فرایند انسانیِ پاسخ‌گو و شواهد همان نسخه بیاید.

برای تفسیر کامل، [فصل ۶۵](65-alignment-governance.md) را با [پاسخ‌نامهٔ مستقل](../answers/65-alignment-governance-fa.md)، [README آزمایشگاه](../projects/65-governance-lab/README.md)، [fixture](../projects/65-governance-lab/governance_pack.json) و [خروجی مرجع](../projects/65-governance-lab/results.json) بخوانید. PDF/EPUB تولید یا آزموده نشده‌اند؛ محصول این milestone وب/PWA و Markdown است.
