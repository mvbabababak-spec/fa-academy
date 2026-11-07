# گزارش ممیزی فصل محلی ۱۳ / سراسری ۵۹ — سامانه‌های GPU و مقیاس‌پذیری

**تاریخ ممیزی:** ۷ نوامبر ۲۰۲۶.

**مسیرها:** فصل `59-gpu-systems.md`؛ پاسخ‌نامهٔ مستقل `../answers/59-gpu-systems-fa.md`؛ پروژهٔ آفلاین `../projects/59-gpu-systems/`؛ شکل دسترس‌پذیر `../diagrams/v4-ch13-gpu-systems.svg`.

## نتایج اجرای واقعی

محیط تمیز Linux x86-64 با CPython `3.13.16` و `torch==2.6.0+cpu` ساخته شد و فایل‌های `requirements-cpu.txt` و `requirements-lock-linux-py313.txt` پروژه در آن نصب شدند. `python -m pip check` موفق بود (`No broken requirements found`). اجرای نهایی `python -m unittest discover -v` برابر **۲۳/۲۳ آزمون unit موفق** بود.

Preflight نشان داد build پایتورچ CPU-only است: CUDA/HIP build و دستگاه شتاب‌دهنده در دسترس نیستند؛ Gloo موجود و NCCL غایب است. validator، fixture ساختگی `v4-ch13-synthetic-dense-layout-v1` را با `DP=2, TP=2, PP=2, CP=2` و حاصل‌ضرب `world_size=16` پذیرفت. SHA-256 fixture: `1edb63d0caa8eedbadf77de3a086c6d61cc1a7dc072601f97046066eb95e7fa0`.

آزمون دوفرایندی `torchrun --standalone --nproc-per-node=2 ... --mode gloo-smoke` در یک میزبان با backendِ Gloo موفق شد؛ `all_reduce_sum` روی ورودی‌های ۱ و ۲ مقدار ۳ را برگرداند. این نتیجه فقط قرارداد فرایند/rank و collective محلی CPU/Gloo را نشان می‌دهد.

## Fixture و مرز ادعا

`sample_layout.json` دادهٔ سخت‌افزار یا پیکربندی اجرای واقعی نیست؛ فقط حاصل‌ضرب چهار محور موازی‌سازی dense را برای یک طرح ساختگی بررسی می‌کند. Expert Parallelism، توپولوژی، مدل، داده و آموزش واقعی در validator مدل نشده‌اند. خروجی `results.json` و `environment.json` اطلاعات محیط و محدودیت ادعا را ثبت می‌کنند.

هیچ CUDA، ROCm، Triton kernel روی GPU، NCCL/RCCL، FSDP، DeepSpeed، Megatron-LM، آموزش، benchmark، throughput، مصرف حافظه یا مدل‌سنجی (ارزیابی کیفیت مدل) آزموده نشده است. نتیجهٔ CPU/Gloo یا fixture ساختگی شاهدی برای سازگاری vendor، scaling، سرعت، کیفیت مدل یا آمادگی محصول نیست. منابع vendor/framework در فصل با نسخه و تاریخ snapshot شده‌اند؛ این نسخه‌های مستندات، یک stack یکپارچهٔ آزموده‌شده را تشکیل نمی‌دهند.

## بررسی جلد چهارم و انتشار

`build_volume4.py` با ۱۳/۱۵ فصل و ۲۹۵ بخش ساخته شد؛ اجرای دوم داده و Markdown را بدون تغییر گذراند. `check_volume4.py` موفق شد: ۵۶ عبارت MathML دسترس‌پذیر، appendix دقیق، برچسب‌های فارسی و انگلیسیِ شکل در سطرهای جدا، و گزارش/پاسخ‌نامه و fixture/hash معتبر.

`test_volume4.py` با Playwright 1.64.1 و Chromium 156.0.8078.4 در ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل موفق شد؛ بررسی ۱۳ فصل، لینک پاسخ‌نامه، شکل، MathML، پیوست دقیق و ۱۳۵ دارایی آفلاین را دربرگرفت. `test_mobile_layout.py` در ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل موفق شد؛ ۱٬۱۰۰ بخش، متن RTL، قفل viewport و دسترسی آفلاین به فصل/پاسخ‌نامه/شکل فصل ۵۹ آزموده شدند. اجرای مرورگر روی sparse-checkout همچنین برای تعدادی تصویر قدیمیِ خارج از فصل/حجم این انتشار 404 ثبت کرد؛ آزمون هدف و دارایی‌های فصل ۵۹ موفق ماندند، و این نتیجه ادعای کامل‌بودن آن دارایی‌های نامرتبط نیست.

Workflow `.github/workflows/volume4-audit.yml` شامل آزمون CPU/Gloo فصل ۵۹ و checkerهای وب/آفلاین است؛ نتیجهٔ GitHub Actions پس از push جداگانه بررسی می‌شود. PDF/EPUB ساخته یا آزموده نشده است؛ خروجی جلد، وب/PWA و Markdown است.
