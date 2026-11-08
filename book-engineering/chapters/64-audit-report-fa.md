# گزارش ممیزی فصل سراسری ۶۴ — Red Teaming و امنیت

**نگاشت:** فصل محلی ۳ جلد پنجم = فصل سراسری ۶۴. **تاریخ ممیزی: ۷ نوامبر ۲۰۲۶.** این گزارش نتایج محلی را از انتشار و آزمون‌های remote جدا ثبت می‌کند؛ نتیجهٔ fixture آزمایشگاه red-team واقعیِ مدل یا محصول نیست. تأیید remote فقط به commit و فایل‌های مشخص‌شده در بخش انتشار مربوط است.

## دامنه و محیط

- پروژه: `book-engineering/projects/64-red-team-lab/`؛ CPython 3.13.16؛ کتابخانهٔ استاندارد Python؛ اجرای محلی و deterministic روی CPU.
- Fixture: `synthetic_security_fixture.json`؛ شناسهٔ `v5-ch03-red-team-synthetic-v1`؛ SHA-256: `1f7183e4db3536e12afb9dd07c81042d0e13c2e7fab9312321bc4f2fed84013f`؛ هفت رکوردِ ساختگی و بدون دادهٔ شخصی، credential یا راز واقعی.
- دستورات پروژه: `python -m unittest -v` و `python red_team_lab.py --output results.json`.
- آزمون پروژه: ۲۰ آزمون واحد از ۲۰ گذشت؛ CLI خروجی JSON قطعی ساخت.
- هیچ API، شبکه، مدل، وزن، pipeline، سرویس retrieval، tool واقعی یا دادهٔ کاربر اجرا نشد.

## نتایج fixture

| خروجی | نتیجهٔ محلی | تفسیر مجاز |
|---|---:|---|
| شمار caseها | ۷ | شش هدف شبیه‌سازی‌شده و یک کنترل سالم |
| کنترل‌های منطبق با انتظار fixture | ۷ از ۷ | فقط شاخه‌های قانون‌محور در کد همین آزمایشگاه |
| هدف شبیه‌سازی‌شدهٔ محقق‌شده | ۰ از ۶ | نرخ موفقیت حمله علیه مدل یا محصول نیست |
| درخواست سالمِ مجاز | ۱ از ۱ | خواندن ساختگیِ دادهٔ عمومی در منطق fixture |
| شاخهٔ محدودیت پرس‌وجو | ۱ مورد rate-limited | آستانهٔ محلی؛ نه آزمون استخراج مدل یا privacy |

پنج آزمون mutation با خاموش‌کردن کنترل‌های ساختگیِ canary، مرز محتوای بازیابی‌شده، scope ابزار، منشأ داده یا query budget نشان دادند انتظار همان fixture نقض می‌شود. این آزمون‌ها فقط حساسیت unit test به تغییرِ آن شاخه‌ها را می‌سنجند؛ اثربخشی کنترل در یک سامانهٔ مولد را نمی‌سنجند.

## بازتولیدپذیری و بررسی داده

`fixture_manifest.json` شناسه، تعداد، منشأ و digest را ثبت می‌کند؛ `results.json` digest یکسان را برمی‌گرداند؛ `environment.json` محیط، وابستگی‌ها و نبود شبکه/مدل را مشخص می‌کند. آزمون‌ها schema، یکتایی شناسه‌ها، تصمیم‌های هفت case، پنج حالتِ تضعیف سیاست، ورودی نامعتبر، بودجهٔ پرس‌وجو و ثبت محدودیت‌ها را وارسی می‌کنند. وابستگی بیرونی لازم نیست. تکرار CLI همان JSON مرجع را تولید می‌کند.

## اعتبارسنجی ساختار کتاب و مرورگر

- Builder جلد پنجم، در اجرای عادی، ۳ فصل از ۱۲ و ۹۹ بخش (۲۶ + ۳۴ + ۳۹) ساخت؛ Service Worker نسخهٔ ۱۰۰ شامل ۳۹ مسیر آفلاین جلد پنجم شد. اجرای دوبارهٔ builder بدون تغییر خروجی‌ها بود.
- Checkerهای جلدهای ۱ تا ۵ همگی موفق شدند: جلد اول ۲۱ فصل/۲۳۶ بخش؛ جلد دوم ۱۱/۱۰۱؛ جلد سوم ۱۴/۲۶۵؛ جلد چهارم ۱۵/۳۴۴؛ جلد پنجم ۳/۹۹.
- آزمون واحد پروژه‌های جلد پنجم موفق شد: فصل ۶۲، ۹/۹؛ فصل ۶۳، ۱۵/۱۵؛ فصل ۶۴، ۲۰/۲۰. اجرای CLI فصل‌های ۶۳ و ۶۴ نیز با `results.json` مرجع برابر بود.
- `test_volume5.py` در عرض‌های ۳۲۰، ۳۹۰، ۷۶۸ و ۱۴۴۰ پیکسل موفق شد؛ هر سه فصل، ۹۹ بخش، نمودارها، MathML، پیوست‌های دقیق و ۳۹ مسیر آفلاین بررسی شدند.
- `test_mobile_layout.py` در عرض‌های ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل موفق شد و ۱٬۲۴۸ بخش را پیمود؛ در جلد پنجم ۲۱۵ بند نثر، ۱۱۷ بند تورفته، چهار بلوک MathML و سه کپشن وارسی شدند.
- آزمون مرورگر جلد دوم در ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل موفق شد: ۱۰۱ بخش و ۲۲ فایل آفلاین. آزمون جلد چهارم نیز در همین سه عرض موفق شد و ۱۵ فصل محلی ۱–۱۵/۱۶۲ دارایی آفلاین را وارسی کرد. آزمون آفلاین سراسری ۲۱ پاسخ‌نامه و ۲۷ تصویر جلد را تأیید کرد؛ آزمون PWA نیز manifest، metadata اپل، ابعاد PNG، نصب‌پذیری Chromium و assetهای آفلاین را گذراند. آزمون مرورگر جلد سوم ۲۶۵ بخش، ۶۰ MathML، ۱۴ شکل و ۱۱۵ فایل آفلاین را در ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل تأیید کرد؛ اجرای کاملِ مجدد پس از یک شکست تک‌اجرای assertion بارگذاری تصویر موفق شد و فایل آزمون یا محتوای آن جلد تغییر نکرد.
- آزمون گستردهٔ موبایل چند درخواست 404 برای دارایی‌های تصویری قدیمی و نامرتبط ثبت کرد؛ assertionهای آن موفق ماندند و این مسیرها جزو دارایی‌های فصل ۶۴ نیستند. `git diff --check` و `node --check sw.js` نیز موفق شدند.

نتایج محلیِ بالا فقط همان fixture و آزمون‌های توصیف‌شده را پوشش می‌دهند؛ وضعیت GitHub Actions و فایل‌های زنده در بخش remote جداگانه ثبت شده است.

## انتشار و تأیید remote

فصل محلی ۳/سراسری ۶۴ در commit مستقل `7c6074dbf899397f4a904a0d12805109f6c48b13` با push عادی به `origin/gh-pages` منتشر شد؛ هنگام انتشار، `git ls-remote` همان SHA را برای نوک شاخه برگرداند. هر شش workflow برای همین commit موفق شدند:

- [Volume 1](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42380667136)
- [Volume 2](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42380667095)
- [Volume 3](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42380667099)
- [Volume 4](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42380667097)
- [Volume 5](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42380667089)
- [GitHub Pages](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42380666893)

نسخهٔ زنده در [Fa Academy](https://mvbabababak-spec.github.io/fa-academy/) پاسخ HTTP 200 داد. برای فایل‌های جدول، SHA-256 دریافت زنده با فایل محلی در commit فصل برابر بود؛ صفحهٔ اصلی و گزارش ممیزی نیز HTTP 200 داشتند. hash گزارش ممیزیِ ثبت‌شده در این نسخه به‌روزرسانی release است و خودش در جدول hash نشده است.

| فایل زنده | SHA-256 محلی = زنده |
|---|---|
| `data.json` | `ae30bdee93eb41020cacc6a9d017762acd22260878d037c3d36cd5e7de00380d` |
| `sw.js` | `02b5fe8343e9f1cae8bc41b447bde9d2a69d085542558695f94f6bfad6d5f53c` |
| `volume-5-full-fa.md` | `da2ea1cf7b0faaf7aa6e520bd20ddebf9f09d32023cedf41a71b9bc253499a64` |
| `book-engineering/chapters/64-red-teaming-security.md` | `81b4be0a00444631d9bb5e302331b18ae6714c1ef3deab2c0dcb2fe4d6c9d99a` |
| `book-engineering/answers/64-red-teaming-security-fa.md` | `28f274f4a76e31222fcef36baaa9c4460b7a114ea7554d3fdc43f1aa67031100` |
| `book-engineering/diagrams/v5-ch03-red-team-pipeline.svg` | `9f03adf59b2eafa5d62f29b1fbe9983b97b1e3faee8e98449f5a58d8af047745` |
| `book-engineering/projects/64-red-team-lab/results.json` | `2bd1ac90a1a1229fd3a9a38e015641044b4629fb9b7ed879ebe1df8afe61a8e5` |

## محدودیت‌ها

۱. Fixture هفت مورد دست‌نویس دارد؛ نمونه‌گیری یا تنوع آن برآوردکنندهٔ حمله‌های واقعی نیست و هیچ عدم‌قطعیت آماری محاسبه نشده است.
۲. هیچ مدل زبانی، classifier، agent، ابزار، retrieval، API، زیرساخت، artifact آموزشی یا pipeline واقعی آزموده نشده است.
۳. نرخ «هدف شبیه‌سازی‌شده» فقط مقایسهٔ outcome تابع‌های قطعی با برچسب‌های fixture است؛ احتمال حمله، ASR تجربی یا تضمین صفرِ نقض نیست.
۴. membership case یک endpoint فرضیِ قانون‌محور را بررسی می‌کند؛ حملهٔ آماری membership inference، inversion یا استخراج متن آموزش اجرا نشده است.
۵. provenance در این fixture Boolean است؛ signature، مجوز، کیفیت، صحت یا بی‌طرفی داده را تأیید نمی‌کند. rate limit نیز فقط یک شمارندهٔ محلی است و حساب‌های متعدد، توزیع زمانی یا مصرف واقعی را پوشش نمی‌دهد.
۶. مطالعهٔ انسانی، ارزیابی حقوق/حریم خصوصی، آزمون چندوجهی، تأیید safety، تست نفوذِ مجاز یا آماده‌بودن deployment در این پروژه انجام نشده است.

برای تفسیر کامل، فصل ۶۴ را همراه با [پاسخ‌نامهٔ مستقل](../answers/64-red-teaming-security-fa.md)، [README پروژه](../projects/64-red-team-lab/README.md)، [fixture](../projects/64-red-team-lab/synthetic_security_fixture.json) و [خروجی مرجع](../projects/64-red-team-lab/results.json) بخوانید. PDF/EPUB تولید یا آزموده نشده‌اند؛ محصول این milestone وب/PWA و Markdown است.
