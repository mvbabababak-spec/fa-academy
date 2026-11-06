# گزارش ممیزی فصل ۴۴ — پیش‌آموزش، برنامهٔ نرخ یادگیری و بازیابی

## دامنه و تغییرات

فصل محلی ۱۲ جلد سوم (فصل سراسری ۴۴) با ۲۱ بخش، پاسخ‌نامهٔ ۸ تمرینی، پیوست کامل کد و یک نمودار مفهومی منتشر می‌شود. پروژه، حلقهٔ پیش‌آموزش، warmup و cosine برحسب optimizer update، gradient accumulation، پایش و checkpoint/resume را روی CPU تمرین می‌کند؛ مدل `TinyFeedForwardLM` و ارزیابی فصل ۴۱ را reuse می‌کند و دادهٔ خودنوشتهٔ فصل ۴۰ را می‌گیرد. این فصل Transformer تازه، corpus واقعی، پیش‌آموزش صنعتی یا benchmark نمی‌سازد.

خروجی تازهٔ پروژه `loss_curve.svg` است؛ SVG از `history.json` همان run رسم می‌شود، train batch-mean NLL و نقاط validation دوره‌ای را جدا نشان می‌دهد و به کتابخانهٔ plotting اضافه نیاز ندارد. Test در نمودار انتخابی نیست و فقط پس از run کامل، یک بار ارزیابی می‌شود.

## محیط

- Python 3.13.16، PyTorch 2.6.0+cpu، Mistune 3.4.0، Pillow 13.0.0، Playwright 1.64.1 و Chromium 156.0.8078.4.
- fixture دادهٔ ۱۶ رکورد خودساخته و برچسب `SELF-CREATED` دارد؛ train/validation/test از pipeline فصل ۴۰ ساخته می‌شوند.
- PyTorch در محیط بدون NumPy یک هشدار اختیاری صادر کرد؛ پروژهٔ ۴۴ NumPy را import یا مصرف نمی‌کند و فرمان‌ها/آزمون‌ها موفق بودند.

## آزمون پروژه و اجرای CLI

در `projects/44-pretraining/`:

```text
python -m py_compile pretraining_run.py test_pretraining_run.py — موفق
python -m unittest discover -v — ۱۰ از ۱۰ موفق
```

پوشش آزمون شامل مرزهای warmup/cosine، ورودی‌های نامعتبر، sampler permutation/cursor/RNG، microbatch نهایی ناقص، برابری accumulation با batch ترکیبی، checkpoint/resume در CPU ثابت، رد config/hash متفاوت، test فقط پس از تکمیل، خروجی SVG ساخته‌شده از ردیف‌های history و رد checkpoint با نسخهٔ ناشناخته است.

CLI بر دادهٔ فصل ۴۰ اجرا شد: ۱۵۱ train example، ۱۲ optimizer update و ۱۹۱ target exposure. Validation نهایی: ۲۳ target، NLL `4.8459761246` nat/target و perplexity `127.2274`. Test نهایی: ۲۸ target، NLL `4.9295075962` و perplexity `138.3114`. این تعداد کوچک فقط fixture smoke test است و برای نتیجهٔ آماری/کیفیت کافی نیست.

اجرای uninterrupted با اجرای متوقف در update ۶ و ادامه از checkpoint مقایسه شد: `metrics.json` و بایت‌های `history.json` برابر بودند. اجرای partial وضعیت `test_once_after_training=0` و `test_metrics=null` داشت؛ run کامل test را یک بار اجرا کرد. `loss_curve.svg` برای run کامل، partial و resumed تولید و به‌عنوان XML معتبر parse شد؛ پروژه از اجراهای یادشده curve را مستقیماً از history ذخیره‌شده می‌سازد.

## یکپارچه‌سازی جلد سوم

- سازنده `build_volume3.py` فصل ۱۲ محلی را به data و Markdown کامل افزود؛ اجرای دوم idempotent بود و `data.json` و `volume-3-full-fa.md` را تغییر نداد. ۱۲ فصل، ۲۱۱ بخش و ۵۱ MathML دسترس‌پذیر ثبت شد.
- `check_volume.py`, `check_volume2.py`, `check_volume3.py`: به‌ترتیب جلد اول ۲۱/۲۳۶، جلد دوم ۱۱/۱۰۱ و جلد سوم ۱۲/۲۱۱ فصل/بخش؛ همه پاس شدند. Checker جلد سوم ۱۲ تصویر WebP محلی با alt معنایی و ۱۲ پاسخ‌نامهٔ بیش از ۳۰۰ واژه را یافت و برابری پیوست کد فصل با پروژه را تأیید کرد.
- آزمون Chromium جلد سوم در ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل موفق شد: ۲۱۱ بخش، ۵۱ MathML، ۱۲ تصویر WebP و ۹۷ فایل آفلاین؛ ناوبری، جست‌وجو، ID پایدار، overflow و دسترسی offline بررسی شدند. Service Worker به v70 ارتقا یافت.
- آزمون مرورگر جلد دوم در ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل و آزمون layout کل کتاب در ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل موفق شدند؛ آزمون layout، ۷۵۱ بخش را بررسی کرد.
- ۱۷۰ آزمون پروژه‌های فصل‌های ۳۳–۴۴ در مجموع موفق شدند؛ CLIهای نمونهٔ فصل‌های ۴۲ و ۴۳ نیز اجرا شدند.

در لاگ مرورگر یک 404 برای thumbnail قدیمی خارج از assets فصل‌های جلد سوم دیده شد؛ این خطای غیرمسدودکننده در snapshotهای پیشین هم وجود داشت. آزمون‌های کتاب، ۹۸ منبع آفلاین فهرست‌شده و تمام شکل‌های فصل ۳۳–۴۴ موفق بودند؛ 404 را به‌عنوان سلامت همهٔ assetهای قدیمی ادعا نمی‌کنیم.

## محدودیت ممیزی

این آزمایش‌ها GPU، چند‌پردازنده‌ای، precision کم، checkpoint storage روی شبکه/برق، corpus واقعی فارسی، کیفیت زبان، حقوق تمام داده‌های بیرونی، performance در مقیاس بزرگ، یا بازتولید میان releaseها/سخت‌افزارهای متفاوت را تأیید نمی‌کنند. `weights_only=True` بررسی امن‌بودن منبع checkpoint را جایگزین نمی‌کند. برابری resume فقط در config، داده، نسخهٔ Python/PyTorch و CPU ثابت سنجیده شد.
