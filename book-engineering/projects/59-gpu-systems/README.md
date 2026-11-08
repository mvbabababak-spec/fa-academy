# پروژهٔ فصل ۵۹ — preflight و جمعِ توزیع‌شدهٔ CPU

این پروژه چهار کار کوچک و محدود دارد: گزارش‌کردن metadata محیط PyTorch، اعتبارسنجی یک طرح موازی‌سازی **ساختگی و dense-only**، بررسی قرارداد rankهای `torchrun` و اجرای یک `all_reduce` روی دو فرایند CPU با backendِ Gloo. پروژه نمونهٔ نصب درایور، اجرای GPU یا راه‌اندازی آموزش مدل نیست.

## نصب snapshot آزموده‌شده

در Linux x86-64 و CPython 3.13 یک محیط جدا بسازید. این وابستگی فقط wheelِ CPU را نصب می‌کند:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-cpu.txt
python -m pip install -r requirements-lock-linux-py313.txt
python -m pip check
```

برای نصب CUDA یا ROCm از این فایل استفاده نکنید. نسخهٔ wheel باید با ماتریس رسمی GPU، سیستم‌عامل، driver و PyTorch همان میزبان جور باشد.

## آزمون و اجرا

```bash
python -m unittest discover -v
python gpu_systems_demo.py --mode preflight
python gpu_systems_demo.py --mode layout

torchrun --standalone --nproc-per-node=2 gpu_systems_demo.py \
  --mode gloo-smoke --output /tmp/ch59-gloo-smoke.json
```

`preflight` فقط build/runtime ثبت‌شده در PyTorch را گزارش می‌کند. در ROCm نیز API پایتونی PyTorch از namespaceِ `torch.cuda` استفاده می‌کند؛ پس نتیجه را کنار `torch.version.hip` و `torch.version.cuda` تفسیر کنید. `layout` فایل ساختگی را با `fixture_manifest.json` می‌سنجد. اجرای `gloo-smoke` مقدارهای ۱ و ۲ را از دو rank جمع می‌کند و باید ۳ برگرداند؛ فایل خروجی فقط از rank صفر نوشته می‌شود.

## Fixture و قرارداد

`sample_layout.json` دادهٔ سخت‌افزاری نیست؛ رابطهٔ سادهٔ `DP × TP × PP × CP = world_size` را برای یک layout فرضیِ dense بررسی می‌کند. Expert Parallelism، hybrid meshها، پیاده‌سازی Megatron، FSDP، DeepSpeed، وزن/مدل، دادهٔ آموزش و اندازه‌گیری performance در این validator مدل نشده‌اند. `fixture_manifest.json` شناسه، منبع و SHA-256 ورودی را تثبیت می‌کند.

## نتیجه و مرز ادعا

خروجی ثبت‌شده در `results.json` از CPython `3.13.16`، `torch==2.6.0+cpu`, Linux x86-64 و CPU با Gloo به‌دست آمده است. آزمون فرایند و collective در یک میزبان موفق است؛ این نتیجه کارکرد CUDA، ROCm، Triton، NCCL/RCCL، چند GPU، چند node، شاردینگ مدل، سرعت، مقیاس‌پذیری یا کیفیت مدل را ثابت نمی‌کند. برای هر شتاب‌دهنده باید ماتریس دقیق سازنده و smoke test روی همان سخت‌افزار را جداگانه اجرا کرد.
