# گزارش ممیزی فصل ۴۱ — نخستین مدل زبانی کوچک

**تاریخ ممیزی:** ۵ نوامبر ۲۰۲۶ · **هدف:** فصل محلی ۹، فصل سراسری ۴۱ · **پایهٔ بازبینی:** `7bb893b60e6a71cb2030d9a7fc309a0db3e248a4`، انتشار فصل ۴۰. فصل‌های منتشرشدهٔ پیشین بازنویسی نشده‌اند.

## دامنه و روش

فصل ۲۰ بخش آموزشی، کد کامل پروژه، پاسخ‌نامه، README پروژه، شکل جریان آموزش، دادهٔ تولیدشده از manifest فصل ۴۰، و اتصال به سازندهٔ جلد سوم را پوشش می‌دهد. پروژه یک مدل زبانی feed-forward با زمینهٔ ثابت است؛ Transformer یا self-attention نیست. تقسیم داده در سطح گروه انجام شده و vocabulary فقط از train ساخته می‌شود. برای انتخاب تنظیمات، `--skip-test` واقعاً test را اجرا نمی‌کند؛ خروجی آن `test_once_after_training: null` است. ارزیابی نهایی ثبت‌شده، test را فقط پس از ثابت‌کردن تنظیمات یک‌بار اجرا می‌کند.

**محیط:** Python 3.13.16؛ PyTorch 2.6.0+cpu؛ Mistune 3.4.0؛ Pillow 13.0.0؛ Playwright 1.64.1؛ Chromium 156.0.8078.4.

## بازتولید و خروجی ثبت‌شده

دادهٔ نمونهٔ فصل ۴۰ با seed 40 شامل ۱۶ رکورد و ۸ گروه است: train/validation/test به‌ترتیب ۱۲/۲/۲ رکورد و ۶/۱/۱ گروه. vocabulary برابر ۱۰۲ توکن است. `chapter40_summary_sha256=8dea00dc131f9ffd821b8e1b638470b41563edb1296ff4eabc0ac07f049ebe0` و `vocabulary_sha256=43db15f1c5032c4f96ffda5568f942bac355806e5807a662e450716e72e82946`.

برای بازتولید داده، از پوشهٔ پروژهٔ فصل ۴۰ اجرا شد: `python small_corpus.py --manifest sample_corpus.jsonl --output /tmp/ch41-data-rebuilt --seed 40`. سپس در پروژهٔ فصل ۴۱: `python tiny_lm.py --data-dir /tmp/ch41-data-rebuilt --output-dir /tmp/ch41-run-reprod --seed 41`. اجرای بازتولید، هر دو hash و همهٔ اعداد زیر را عیناً تکرار کرد. با PyTorch 2.6.0+cpu، seed 41 و ۳۰ epoch، مدل ۷٬۱۴۲ پارامتری ساخته شد. میانگین NLL برحسب nat/token و perplexity:

| بخش | هدف‌های token | NLL | Perplexity |
|---|---:|---:|---:|
| train | 151 | 0.2253182853 | 1.2527213756 |
| validation | 23 | 6.3173831442 | 554.1210386563 |
| test (یک‌بار، در پایان) | 28 | 6.2404997689 | 513.1148857551 |

نمونهٔ خام تولید، با سقف ۱۰ token: `<unk> <unk> ، پرچم دیوار پس از باران برق می‌زدند .`. فاصلهٔ train و holdout و perplexity بزرگ، هشدار اندازه و ماهیت corpus کوچک‌اند؛ این خروجی benchmark یا شاهد تعمیم نیست. اجرای validation-only با `python tiny_lm.py --data-dir /tmp/ch41-data-rebuilt --output-dir /tmp/ch41-run-reprod-validation --seed 41 --epochs 1 --skip-test` نیز بررسی شد؛ `test_once_after_training` برابر `null` و سیاست اجرا `not evaluated; validation-only run (--skip-test)` بود.

## آزمون‌ها و یکپارچه‌سازی

- مجموعهٔ آزمون پروژه‌های محلی ۱ تا ۹ جلد سوم: **۱۳۷/۱۳۷ موفق**؛ فصل ۴۰: ۲۰/۲۰ و فصل ۴۱: ۲۲/۲۲.
- `check_volume.py`: موفق، ۲۱ فصل/۲۳۶ بخش. `check_volume2.py`: موفق، ۱۱ فصل/۱۰۱ بخش.
- `test_volume2.py`: موفق در ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل؛ ۲۲ مسیر آفلاین. آزمون قدیمی تصویر `loading=lazy` را بدون انتظار برای بارگذاری بررسی می‌کرد؛ آزمون اکنون تصویر را به viewport می‌آورد و بارگذاری موفق را صریحاً انتظار می‌کشد. این اصلاح فقط تست است و به محتوای فصل‌های قدیمی دست نزده است.
- `test_mobile_layout.py`: **موفق** در ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل؛ ۶۸۹ بخش.
- ساخت جلد سوم یک‌بار ۹/۱۴ فصل و ۱۴۹ بخش را تولید کرد؛ اجرای دوم idempotent بود و اعلام کرد داده با منابع منطبق است. `git diff --check` نیز موفق شد.
- `check_volume3.py`: موفق، ۹/۱۴ فصل، ۱۴۹ بخش، ۹ تصویر WebP محلی با متن جایگزین معنایی، ۹ پاسخ‌نامه و ۳۸ MathML دسترس‌پذیر.
- `test_volume3.py`: موفق در ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل؛ در هر سه عرض، ناوبری، جست‌وجو، ۱۴۹ بخش، ۳۸ MathML، ۹ شکل و ۶۸ فایل لازم آفلاین بررسی شدند.

شکل `assets/images/babak-ai/v3-ch09-training-loop.webp` با Chromium بازبینی و از SVG محلی بازتولید شد: ۱۶۰۰×۱۰۰۰، ۸۰٬۴۷۴ بایت، SHA-256 `3455633303ddf09515237d91e7542114f14bff56b839c7cd7d0a79b592c87401`.

در آزمون‌های سراسری چند تصویر قدیمی خارج از این فصل ۴۰۴ دادند؛ از جمله `assets/images/genai/repo-thumbnailv4-fixed.11f1ce6a85d01461.webp` و دو ارجاع `translated_images/fa/` در کتاب‌های قبلی. این مورد در ممیزی‌های پیشین هم ثبت شده است؛ دارایی‌های تازهٔ فصل ۴۱ و مسیرهای لازم آن در آزمون‌های آفلاین جداگانه سنجیده می‌شوند. این گزارش ادعای پوشش Safari/iOS واقعی، GPU، حقوق همهٔ داده‌ها یا کیفیت آماری مدل ندارد.

## منابع فنی بازبینی‌شده

صفحه‌های زیر در ۵ نوامبر ۲۰۲۶ دریافت و برای همان ادعاهای فصل بازبینی شدند:

1. Bengio et al., “A Neural Probabilistic Language Model” (2003), [JMLR](https://www.jmlr.org/papers/v3/bengio03a.html).
2. [PyTorch 2.6 — `torch.nn.Embedding`](https://docs.pytorch.org/docs/2.6/generated/torch.nn.Embedding.html) و [CrossEntropyLoss](https://docs.pytorch.org/docs/2.6/generated/torch.nn.CrossEntropyLoss.html): نگاشت شناسه به embedding، رفتار `padding_idx`، logits نرمال‌نشده و هدف‌های شناسهٔ کلاس.
3. [PyTorch optimization tutorial](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html)، [randomness](https://docs.pytorch.org/docs/2.6/notes/randomness.html)، [`torch.multinomial`](https://docs.pytorch.org/docs/2.6/generated/torch.multinomial.html) و [serialization](https://docs.pytorch.org/docs/2.6/notes/serialization.html): حلقهٔ گرادیان، محدودیت بازتولیدپذیری میان نسخه/سخت‌افزار، شروط نمونه‌گیری و بارگذاری محدود `weights_only`.
4. Jurafsky & Martin, *Speech and Language Processing*, فصل n-gram، [نسخهٔ سوم](https://web.stanford.edu/~jurafsky/slp3/3.pdf): پیش‌بینی توکن بعدی، splitهای داده و perplexity.

## وضعیت انتشار

این سند، آزمون محلی را ثبت می‌کند. baseline راه دور در آغاز `7bb893b60e6a71cb2030d9a7fc309a0db3e248a4` بود و فصل ۴۱ در آن وجود نداشت. در انتشار قبلی، CI جلد سوم، Pages و جلد اول موفق بودند؛ audit جلد دوم در Browser/offline شکست خورده بود. نتیجهٔ workflowهای مربوط به این انتشار فقط پس از push قابل ثبت و تأیید است؛ این گزارش به‌تنهایی ادعای موفقیت CI راه دور نمی‌کند.
