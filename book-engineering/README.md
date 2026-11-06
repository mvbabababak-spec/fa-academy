# هنر و علم ساخت هوش — Babak & Ai

جلد اول ۲۱ فصل برنامه‌ریزی‌شده دارد. فصل‌های ۱ تا ۲۱ در مخزن انتشار آماده‌اند؛ فصل‌های بعدی هنوز آماده نیستند.

- متن فصل‌ها در `chapters/` و پروژه‌های اجرایی در `projects/` است.
- تصاویر جدید کتاب و جلد آن WebP هستند؛ اسکریپت‌های ساخت تصاویر در فایل‌های `create_ch*.py` قرار دارند.
- بازتولید محتوای فصل‌های ۲۰ تا ۲۱: از ریشه مخزن `python book-engineering/build_chapter.py`؛ نیازمند Python و کتابخانه Mistune 3. قبل از انتشار داده‌های دیگر و خروجی تولیدشده را بررسی کنید.
- پروژه‌های فصل‌های ۸ تا ۱۰ با Python 3.13.16 اجرا شده‌اند. پروژه فصل ۸ شبیه‌سازی CPU است و یک اجرای چند GPU واقعی نیست.
- نقشه کل مجموعه: `../BOOK_ROADMAP_FA.md`

- پروژه‌های فصل‌های ۱۱ تا ۱۳ با Python 3.13.16 آزمایش شدند؛ فصل ۱۳ با Git 2.47.3 فقط محلی و بدون شبکه اجرا شد.

- فصل ۱۴ و ۱۶ با Python 3.13.16 و کتابخانه استاندارد تست شدند؛ فصل ۱۵ با NumPy 2.3.5، Pandas 2.2.3 و Matplotlib 3.11.2 بررسی شد؛ رابط Jupyter آزموده نشده است. نمودار فصل ۱۵ با اجرای پروژه تولید می‌شود.

- پیوست‌های تکمیلی فصل‌های ۱۴ تا ۱۶ و پروژه‌های مستقل در `projects/14-testing-sql/`، `projects/15-data-analysis-supplement/` و `projects/16-algebra-supplement/` قرار دارند. نوت‌بوک فصل ۱۵ با nbclient اجرا شد؛ رابط JupyterLab جداگانه آزموده نشده است.

- فصل‌های ۱۷ تا ۱۹ با Python 3.13.16، فصل ۱۷ با NumPy 2.3.5، روی CPU اجرا شدند.
- قانون تولید: پیش از شروع هر فصل، نسخهٔ مخزن و وجود محتوای فصل بررسی شود؛ فصل تکمیل‌شده دوباره تولید نشود. پیش از نگارش هر فصل، ساختار کل پنج جلد و جایگاه فصل در نقشه بازخوانی شود.

- پروژه‌های فصل ۲۰ و ۲۱ با Python 3.13.16 و کتابخانه استاندارد روی CPU اجرا و هرکدام با چهار آزمون بررسی شدند. تکمیل فصل‌ها به معنای آماده‌بودن PDF یا کل مجموعه نیست.

## ساخت و انتشار جلد دوم

جلد دوم شامل فصل‌های محلی ۱–۱۱ (سراسری ۲۲–۳۲) است. انتشار وب/PWA است؛ PDF و EPUB تولید و آزموده نشده‌اند. فایل قابل دریافت `../volume-2-full-fa.md` است. از ریشه مخزن و پس از نصب Mistune 3.4.0 به ترتیب `python book-engineering/build_volume2.py`، `python book-engineering/append_volume2_04_06.py`، `python book-engineering/append_volume2_07_09.py`، `python book-engineering/append_volume2_10_11.py` را اجرا کنید. این سازنده‌ها فصل موجود ناسازگار را بازنویسی نمی‌کنند؛ برای اصلاح محتوای منتشرشده ابتدا منبع و داده همگام، نسخه SW افزایش و تست‌ها اجرا شوند. `python book-engineering/check_volume2.py` و `python book-engineering/test_volume2.py` کنترل ساختار و مرورگر را انجام می‌دهند؛ دومی Playwright و Chromium می‌خواهد. برای حفظ تاریخچه، توضیحات پیشین این فایل به زمان نگارش خود مربوط‌اند.

**رده‌بندی پروژه‌ها:** ۱۱ پروژه فصل‌های جلد دوم تمرین‌های مستقل اجرایی آن فصل‌ها هستند؛ پروژه تلفیقی پایان بخش، فعالیت ارزیابی جامع است و الزاماً پروژه جدید یا پوشه مستقل نیست؛ ۲۰ پروژه اصلی جدول نقشه مسیرهای سراسری مجموعه‌اند و برخی با پروژه‌های فصلی هم‌پوشانی دارند. این دسته‌ها را نباید با هم جمع زد یا هم‌ارز شمرد.

## ساخت و انتشار تدریجی جلد سوم

طبق نقشهٔ کامل پنج‌جلدی، جلد سوم ۱۴ فصل محلی دارد که با فصل‌های سراسری ۳۳–۴۶ متناظرند. فصل‌های محلی ۱–۱۲ (سراسری ۳۳–۴۴) منتشرشده‌اند: توکن‌سازی؛ Attention و Q/K/V؛ Self-Attention؛ positional encoding و اجزای Transformer؛ خانواده‌های Encoder/Decoder؛ زمینهٔ بلند؛ Transformer چندوجهی؛ پیکرهٔ کوچک و آماده‌سازی داده؛ نخستین مدل زبانی feed-forward با آموزش/ارزیابی؛ طراحی/بودجه‌بندی Mini GPT با reuse پروژهٔ Decoder فصل ۳۷؛ ممیزی provenance و مجوز corpus؛ و برنامهٔ پیش‌آموزش برحسب optimizer update، warmup/cosine، accumulation، validation و checkpoint قابل‌بازیابی. فصل ۴۲ آموزش یا کیفیت Mini GPT را ادعا نمی‌کند؛ فصل ۴۳ ابزارش corpus واقعی یا مجوز آموزشی نمی‌سازد؛ فصل ۴۴ نیز smoke exercise روی fixture کوچک است، نه پیش‌آموزش صنعتی یا benchmark. فصل‌های منتشرشده را بازنویسی نکنید.

منبع هر فصل در `chapters/`، پاسخ‌نامه در `answers/`، و پروژهٔ مستقل در `projects/` قرار دارد. فصل ۴۲: `chapters/42-mini-gpt.md`، `answers/42-mini-gpt-fa.md` و `projects/42-mini-gpt-design/`؛ نمودارش از `diagrams/v3-ch10-mini-gpt-budget.svg` و `create_v3_ch10_image.py` به WebP محلی تبدیل می‌شود. فصل ۴۳: `chapters/43-corpus.md`، `answers/43-corpus-fa.md` و `projects/43-corpus-audit/`؛ نمودارش از `diagrams/v3-ch11-corpus-audit.svg` و `create_v3_ch11_image.py` به WebP محلی تبدیل می‌شود. فصل ۴۴: `chapters/44-pretraining.md`، `answers/44-pretraining-fa.md` و `projects/44-pretraining/`؛ نمودارش از `diagrams/v3-ch12-pretraining.svg` و `create_v3_ch12_image.py` به WebP تبدیل می‌شود. پروژهٔ ۴۴ از history واقعی هر run نمودار `loss_curve.svg` می‌سازد. `volume-3-full-fa.md` نسخهٔ Markdown فصل‌های موجود را جمع می‌کند. پروژهٔ ۴۲ با Python 3.13.16 و PyTorch 2.6.0+cpu یازده آزمون و CLI را پاس می‌کند؛ آموزش، کیفیت یا peak VRAM را ارزیابی نمی‌کند. پروژهٔ ۴۳ با Python 3.13.16 و کتابخانهٔ استاندارد، ۱۲ آزمون و CLI آفلاین را پاس می‌کند؛ متن fixtureها ساختگی است و ابزار حقوق، کیفیت زبانی یا نبود آلودگی را تأیید نمی‌کند. پروژهٔ ۴۴ با Python 3.13.16 و PyTorch 2.6.0+cpu ده آزمون و اجرای کامل/قطع‌و‌ادامه را پاس می‌کند؛ منحنی زیان و test metric فقط خروجی fixture کوچک‌اند و benchmark واقعی نیستند.

### ساخت، آزمون و ممیزی

از ریشهٔ مخزن و با Python 3.13.16، پس از نصب `mistune==3.4.0`، اجرا کنید:

```bash
python book-engineering/build_volume3.py
python book-engineering/check_volume3.py
```

سازنده فقط فصل‌های دارای منبع پیوسته از شمارهٔ ۱ را اضافه می‌کند و شناسه‌های پایدار می‌سازد؛ فصل منتشرشدهٔ ناسازگار را بازنویسی نمی‌کند. گزینهٔ `--refresh-last-draft` فقط برای آخرین draft محلیِ هنوز منتشرنشده است و پس از کنترل remote و حفظ همهٔ IDها مجاز است.

پروژه‌های فصل‌های ۳۳ تا ۴۶ را جداگانه با `python -m unittest discover -v` از پوشهٔ همان پروژه اجرا کنید. پروژهٔ فصل ۴۰ Python 3.11+ و کتابخانهٔ استاندارد می‌خواهد. پروژهٔ فصل ۴۱ به Python 3.11+ و PyTorch 2.6.x CPU نیاز دارد؛ برای مقایسهٔ تنظیمات از `--skip-test` استفاده کنید و فقط اجرای نهایی را بدون آن انجام دهید. ۲۲ آزمون آن، قرارداد داده و hash، واژگان و زمینه، ابعاد/زیان/گرادیان، seed، checkpoint، تولید و CLI را می‌سنجند؛ کیفیت زبان، تعمیم، حقوق داده یا ایمنی محصول را اثبات نمی‌کنند. پروژهٔ فصل ۴۲ با Python 3.11+ و PyTorch 2.6.x CPU نیازمندی دارد؛ یازده آزمون، شمار پارامتر، شکل logits، عدم نشت آینده، رد prefix چپ‌pad/all-pad و برآوردهای tensor را می‌سنجند. `python book-engineering/projects/42-mini-gpt-design/mini_gpt_design.py --context-sweep` خروجی بودجهٔ پیش‌فرض را بازتولید می‌کند؛ peak حافظه، benchmark یا کیفیت تولید را ثابت نمی‌کند. پروژهٔ فصل ۴۳ در `projects/43-corpus-audit/` به Python 3.11+ و کتابخانهٔ استاندارد نیاز دارد؛ ۱۲ آزمون و CLI، manifest ساختگی، فیلترهای پرچمی، near-duplicate و overlap سطحی با ارزیابی جدا را می‌سنجند. خروجی آن فقط report است؛ هیچ متنی را خودکار حذف یا برای آموزش صادر نمی‌کند، و مجوز، privacy، کیفیت زبانی یا پاک‌بودن benchmark را اثبات نمی‌کند. پروژهٔ فصل ۴۴ به Python 3.11+ و PyTorch 2.6.x CPU نیاز دارد؛ ۱۰ آزمون، schedule، microbatch ناقص، accumulation، checkpoint/resume، data/config identity و SVG خروجی را می‌سنجند. CLI از fixture فصل ۴۰ history/metrics/checkpoint/`loss_curve.svg` می‌سازد؛ test فقط پس از run کامل ارزیابی می‌شود. خروجی‌ها معیار کیفیت یا scaling مدل نیستند. پروژهٔ فصل ۴۵ در `projects/45-precision/` به Python 3.11+ و PyTorch 2.6.x CPU نیاز دارد؛ ۱۰ آزمون metadata قالب، cast/underflow/overflow، CPU BF16 autocast، affine int8، scale per-group، saturation و JSON را کنترل می‌کنند. `precision_lab.py` گزارش JSON قطعی می‌سازد؛ cast FP8 روی CPU پشتیبانی accelerator یا GEMM سریع را ثابت نمی‌کند، و کدهای زیر ۸ bit در demo واقعاً bit-pack نمی‌شوند؛ این پروژه latency، دقت مدل، مزیت task یا benchmark را ارزیابی نمی‌کند. پروژهٔ فصل ۴۶ در `projects/46-scale-training/` به Python 3.11+ و PyTorch 2.6.x CPU/Gloo نیاز دارد؛ ده آزمون activation recomputation، بایت saved-tensorهای hook، گرادیان DDP با shardهای نابرابر، fingerprint و JSON را کنترل می‌کنند. اجرای CLI با fixture دوپردازه‌ای correctness را می‌سنجد، نه GPU/cluster، سرعت، peak memory یا کیفیت مدل. دستور نصب و محدودیت‌ها در README هر پروژه است.

آزمون مرورگر جلد سوم: `python book-engineering/test_volume3.py`؛ آزمون layout کل کتاب: `python book-engineering/test_mobile_layout.py`. هر دو به Playwright 1.64.1، Chromium و Pillow 13.0.0 نیاز دارند. تست جلد سوم ناوبری، شناسه‌های پایدار، search، MathML دسترس‌پذیر، overflow، ۱۴ تصویر و ۱۱۵ فایل آفلاین را در عرض‌های ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل بررسی می‌کند؛ آزمون موبایل ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل را می‌سنجد. برای آزمون آفلاین، Service Worker روی v73 است. گردش‌کار `.github/workflows/volume3-audit.yml` checkerها، پروژه‌های جلد سوم، idempotence سازنده، آزمون مرورگر جلد دوم/سوم و layout موبایل را اجرا می‌کند.

**مرز آزمون‌ها:** این تست‌ها مرورگرهای دیگر، Safari/iOS واقعی، GPU واقعی، همهٔ دستگاه‌ها، مجوز واقعی هر corpus، حذف کامل PII یا کیفیت آماری مدل را تأیید نمی‌کنند. انتشار وب/PWA و فایل Markdown است؛ PDF و EPUB تولید و آزموده نشده‌اند. پیش از هر فصل، remote، فایل‌های موجود و کل `BOOK_ROADMAP_FA.md` را بررسی کنید؛ هر فصل commit مستقل داشته باشد، push معمولی انجام شود، remote و CI بررسی شوند و سپس فصل بعد آغاز شود. Force push نکنید.
