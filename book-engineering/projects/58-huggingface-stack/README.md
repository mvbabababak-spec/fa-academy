# پروژهٔ فصل ۵۸ — خط لولهٔ آفلاین Hugging Face

این پروژه فقط برای تمرین اتصال چهار کتابخانه است: fixture ساختگی → `datasets.DatasetDict` → tokenizer محلی `tokenizers` → batch با Transformers → دو گام مدل BERT کوچک با `accelerate` روی CPU.

## نصبِ snapshot آزموده‌شده

در Linux x86-64 و CPython 3.13، محیطی جدا بسازید. برای جلوگیری از انتخاب wheel اشتباه، PyTorch CPU را از فهرست رسمی خودش و بسته‌های دیگر را جداگانه نصب کنید:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-cpu.txt
python -m pip install -r requirements-lock-linux-py313.txt
python -m pip check
```

`requirements-lock-linux-py313.txt` snapshot کامل resolveشده برای Linux/CPython 3.13 است و `torch` را عمداً دوباره نصب نمی‌کند. برای سیستم‌عامل یا accelerator دیگر، wheel و driver را از ماتریس رسمی همان PyTorch انتخاب کنید؛ lock این پروژه را سازگاری عمومی تلقی نکنید. `requirements.txt` چهار pin مستقیم Hugging Face را نشان می‌دهد.

## آزمون و اجرا

```bash
python -m unittest discover -v
HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 \
  python pipeline_demo.py --max-steps 2 --seed 58 --output results.json

# معادل یک‌پردازه‌ای با launcher؛ همچنان CPU و smoke test است
HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 \
  accelerate launch --cpu --num_processes 1 --num_machines 1 \
  --mixed_precision no --dynamo_backend no pipeline_demo.py \
  --max-steps 2 --seed 58 --output /tmp/ch58-accelerate-results.json
```

`fixture_manifest.json`، شمار splitها و SHA-256 فایل `sample_data.jsonl` را کنترل می‌کند. tokenizer فقط از ۸ ردیف `train` ساخته می‌شود؛ ۴ ردیف validation و دو `group_id` آن در آموزش tokenizer/مدل وارد نمی‌شوند. آزمون‌ها leakage گروهی، hash، ویژگی‌های Dataset، special tokenها، padding، خروجی CPU، گرادیان متناهی، seed ثابت و اجرای CLI آفلاین را بررسی می‌کنند.

## نسخه و نتیجهٔ ثبت‌شده

snapshot بررسی‌شده در ۶ نوامبر ۲۰۲۶: Python 3.13.16، `torch==2.15.0+cpu`, `transformers==5.22.2`, `datasets==5.1.0`, `tokenizers==0.23.3`, `accelerate==1.15.0`; وابستگی‌های مهم resolveشده و خروجی `pip check` در `environment.json` آمده‌اند. `results.json` از اجرای واقعی همین محیط بازتولید شده است؛ مدل از config با وزن تصادفی ساخته شده و lossهای آن فقط trace آزمون اجرا هستند.

## مرز ادعا

- تمام ۱۲ ردیف و برچسب‌ها ساختگی‌اند؛ این fixture معیار یا نمونهٔ نمایندهٔ زبان فارسی نیست.
- هیچ مدل/داده‌ای از Hub دریافت یا منتشر نمی‌شود؛ هیچ token لازم نیست.
- مدل از config محلی با ۴٬۶۴۲ پارامتر trainable و وزن تصادفی آغاز می‌شود؛ pretrained fine-tuning انجام نشده است.
- دو گام CPU، آزمون سازگاری API و finite بودن loss/gradient هستند؛ کیفیت، تعمیم، benchmark، کارایی GPU، آموزش توزیع‌شده یا آمادگی محصول را اثبات نمی‌کنند.
- `validation_loss_smoke_only` در `results.json` برای نشان‌دادن مسیر محاسبه ذخیره شده است، نه نتیجهٔ ارزیابی قابل تعمیم.
