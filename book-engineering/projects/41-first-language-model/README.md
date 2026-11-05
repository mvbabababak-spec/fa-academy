# پروژهٔ فصل ۴۱: حلقهٔ آموزش یک مدل زبانی کوچک

این تمرین خروجی‌های پروژهٔ فصل ۴۰ را می‌خواند، واژگان ثابتِ آموخته‌شده فقط از train را نگه می‌دارد و یک مدل پیش‌بینی واژهٔ بعدی را روی CPU آموزش می‌دهد. معماری آن embedding توکن و موقعیت، MLP با زمینهٔ ثابت، logits و cross-entropy است؛ **Transformer، Self-Attention یا LLM تولیدی نیست**. پیش‌فرض هیچ داده‌ای از اینترنت دریافت نمی‌کند.

## نیازمندی و اجرا

- Python 3.11+ و PyTorch 2.6.x؛ GPU لازم نیست و این پروژه از CPU استفاده می‌کند.
- دستور نصب CPU-only که در محیط Linux/Python 3.13 این گزارش اجرا شد:

```bash
python -m pip install torch==2.6.0+cpu --index-url https://download.pytorch.org/whl/cpu
```

برای سیستم‌عامل یا نسخهٔ Python دیگر، دستور رسمی CPU را از [PyTorch Start Locally](https://pytorch.org/get-started/locally/) انتخاب کنید؛ wheelها با سیستم‌عامل و نسخهٔ Python فرق می‌کنند. نخست splitهای فصل ۴۰ را بسازید، سپس آزمایش فصل ۴۱ را اجرا کنید. از ریشهٔ مخزن:

```bash
python book-engineering/projects/40-small-data-project/small_corpus.py \
  --manifest book-engineering/projects/40-small-data-project/sample_corpus.jsonl \
  --output /tmp/ch41-data --seed 40
python book-engineering/projects/41-first-language-model/tiny_lm.py \
  --data-dir /tmp/ch41-data --output-dir /tmp/ch41-run --seed 41
```

یا از همین پوشه:

```bash
python -m unittest discover -v
python tiny_lm.py --data-dir ../40-small-data-project/build --output-dir build --seed 41
```

در بار اول ممکن است نصب PyTorch به اینترنت نیاز داشته باشد. نسخهٔ نصب‌شده را با `python -c 'import torch; print(torch.__version__)'` ثبت کنید. خروجی وزن‌ها را از منبع نامطمئن بارگذاری نکنید؛ ابزار از `torch.load(..., weights_only=True, map_location='cpu')` استفاده می‌کند.

## قرارداد داده و آموزش

`load_dataset` سه JSONL، `vocab.json` و `summary.json` فصل ۴۰ را کنترل می‌کند: شناسهٔ رکورد تکراری نباشد، hash و نرمال‌سازی هر متن درست باشد، `group_id` میان train/validation/test نشت نکند، متن دقیق تکراری بین splitها نیاید، گروه‌های واقعی با summary برابر باشند و واژگان فقط tokenهایی داشته باشد که در train دیده شده‌اند. پرچم `tokenizer_fit_split=train` یک metadata اعلام‌شده است، نه امضای رمزنگاری‌شدهٔ منشأ. هر رکورد جداگانه به دنبالهٔ BOS، توکن‌ها و EOS تبدیل می‌شود؛ پنجره از مرز رکورد عبور نمی‌کند. فقط train گرادیان می‌گیرد. validation در پایان هر epoch گزارش می‌شود.

برای مقایسهٔ hyperparameterها فقط با validation، هر اجرای آزمایشی را با `--skip-test` انجام دهید؛ در metrics، مقدار test برابر `null` می‌ماند. پس از قفل‌کردن تنظیمات یک اجرای نهایی را بدون این flag انجام دهید تا test فقط یک‌بار گزارش شود.

تنظیمات پیش‌فرض آموزشی کوچک و برای CPU هستند: context برابر ۴، embedding برابر ۱۶، لایهٔ پنهان ۳۲، batch برابر ۱۶، ۳۰ epoch، AdamW با weight decay صفر و seed برابر ۴۱. تغییر seed، split، نسخهٔ PyTorch یا تنظیمات می‌تواند نتیجه را عوض کند. این تنظیمات توصیهٔ بهینه برای زبان فارسی یا مدل واقعی نیستند.

## فایل‌های خروجی

- `metrics.json`: تعداد target tokenها، میانگین negative log-likelihood و perplexity برای train، آخرین validation و test نهایی؛ همراه با hash canonical واژگان، summary و سه فایل split، نسخهٔ PyTorch، seed و محدودیت‌ها.
- `history.json`: train/validation در هر epoch؛ فقط validation می‌تواند برای انتخاب تنظیمات استفاده شود.
- `checkpoint.pt`: config، vocabulary، metadata و `state_dict`؛ خود شیء مدل pickle نمی‌شود.

`build/` و checkpointها با `.gitignore` از commit خارج‌اند. `perplexity = exp(mean NLL)` در همین tokenizer و قرارداد target تعریف می‌شود؛ به‌دلیل پیکرهٔ ۱۶رکوردی و holdoutهای بسیار کوچک، آن را با عدد مدل‌های دیگر مقایسه نکنید. خروجی تولیدشده یک نمونهٔ آموزشی است، نه ارزیابی کیفیت فارسی.

## آزمون و محدودیت

۲۲ آزمون قرارداد توکن، shift ورودی/هدف، padding و زمینه، مرزبندی رکورد، hash و split، منشأ تقریبی واژگان، شکل logits، loss، گرادیان، تکرارپذیری seed، checkpoint، تولید با EOS و اجرای CLI را می‌سنجند. آزمون‌ها کیفیت زبانی، تعمیم، بی‌طرفی، مجوز داده یا ایمنی تولید را اثبات نمی‌کنند. واژگان word-level، زمینهٔ کوتاه، دادهٔ خودساختهٔ بسیار کوچک و مدل MLP باعث خروجی‌های شکننده و احتمال حفظ مثال‌ها می‌شوند. برای هر استفادهٔ بیرون از این تمرین، ارزیابی مجزا، دادهٔ مجاز، مجموعهٔ test مستقل و بازبینی انسانی لازم است.
