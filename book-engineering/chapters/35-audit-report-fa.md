# گزارش ممیزی فصل ۳۵ — نسخهٔ محلی

**تاریخ اجرا:** ۵ نوامبر ۲۰۲۶ · **دامنه:** فصل ۳ جلد سوم (فصل سراسری ۳۵)، ماژول Multi-Head Self-Attention، پاسخ‌نامه، تصویر و آزمون نشت علّی.

## محیط ثبت‌شده

- Python 3.13.16 روی Linux؛ اجرای پروژه روی CPU.
- PyTorch `2.6.0+cpu`؛ آزمون CUDA/GPU اجرا نشد.
- Pillow 13.0.0 و Mistune 3.4.0؛ تصویر اختصاصی از اسکریپت Python ساخته شد.

## آزمون پروژه

- `cd book-engineering/projects/35-self-attention && python -m unittest -v` — **۱۰ آزمون موفق**: شکل‌های batch و هر سر، مجموع وزن‌ها، صفر بودن توجه آینده، مداخلهٔ تغییر آینده/ثبات خروجی و وزن گذشته، اثر ورودی جاری، سازگاری با SDPA علّی، معنای ماسک بولی SDPA، گرادیان و ورودی‌های نامعتبر.
- `python causal_multihead.py` — CPU؛ ورودی و خروجی `(1, 5, 8)`، وزن‌های هر سر `(1, 2, 5, 5)`، بیشینهٔ وزنِ خانه‌های آینده `0.0`.
- نمونه‌های کوتاه `nn.MultiheadAttention` و `F.scaled_dot_product_attention` در فصل جداگانه روی PyTorch 2.6 CPU اجرا شدند؛ به‌ترتیب شکل خروجی `(2,5,8)` و `(2,3,5,4)` بود.

## ساختار، مرورگر و آفلاین

- `python book-engineering/check_volume3.py` — موفق: ۳/۱۴ فصل، ۳۷ بخش، ۳ تصویر محلی WebP با متن جایگزین معنایی، ۳ جواب‌نامه و ۱۰ قطعهٔ MathML دسترس‌پذیر.
- `python book-engineering/build_volume3.py` دوبار اجرا شد؛ بار دوم اعلام کرد «already matches». SHA-256 فایل‌های `data.json` و `volume-3-full-fa.md` پیش و پس از اجرای دوم برابر بود (idempotent).
- آزمون Chromium `python book-engineering/test_volume3.py` — موفق در عرض‌های ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل: ۳۷ بخش، MathML، هر سه تصویر، مرزهای ناوبری، پیوند جواب‌نامه، جست‌وجو و ۲۳ فایل صریحاً فهرست‌شده در cache آفلاین.
- آزمون‌های regression: جلد اول — ۲۱ فصل/۲۳۶ بخش و ۲۷ تصویر محلی؛ جلد دوم — ۱۱ فصل/۱۰۱ بخش و ۱۱ تصویر. هر دو کنترل ساختار موفق.
- `python book-engineering/test_volume2.py` — موفق در ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل: ناوبری، جست‌وجو، MathML و ۲۲ فایل آفلاین.
- `python book-engineering/test_mobile_layout.py` — موفق در ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل؛ ۵۷۷ بخش، قفل افقی و متن/ناوبری آفلاین بررسی شدند.
- مرورگرها چند 404 برای تصویرهای قدیمی و نامرتبط ثبت کردند: `assets/images/genai/repo-thumbnailv4-fixed.11f1ce6a85d01461.webp`، `translated_images/fa/Rosenblatt-wikipedia.294821b285ac796d.webp` و `translated_images/fa/Mark_I_perceptron_wikipedia.1f84eaa2d4b76ec9.webp`. هر سه ارجاع در دادهٔ مبنای تأییدشدهٔ فصل ۳۴ نیز وجود دارد و فایل‌ها آنجا هم غایب‌اند؛ فایل‌های فصل ۳۵ و مسیرهای آفلاین PWA همگی دریافت شدند و آزمون‌های صفحه خطای JavaScript گزارش نکردند.

## محدودیت و وضعیت انتشار

این ممیزی Chromium desktop را در سه عرض شبیه‌سازی‌شده پوشش می‌دهد؛ Safari/iOS، دستگاه فیزیکی، همهٔ مرورگرها و نتیجهٔ GitHub Actions بررسی نشده‌اند. پروژه یک ماژول تک‌بلوک علّی با طول ثابت است؛ positional encoding، padding mask، dropout، residual و FFN را ندارد. آزمون‌ها آن را به GPT یا کل pipeline داده تعمیم نمی‌دهند؛ اجرای CPU، کیفیت مدل کامل یا سرعت GPU را ثابت نمی‌کند. PDF و EPUB تولید نشده‌اند.

## محدودیت و وضعیت انتشار

پروژه یک ماژول تک‌بلوکِ علّی با طول ثابت، بدون positional encoding، padding mask، dropout، residual یا FFN است؛ آزمون‌ها آن را به GPT یا کل pipeline تعمیم نمی‌دهند. نتیجهٔ GitHub Actions و نسخهٔ زندهٔ Pages تنها پس از مشاهدهٔ واقعی ثبت می‌شود. PDF و EPUB تولید نشده‌اند.
