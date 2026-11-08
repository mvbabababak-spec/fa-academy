# پروژهٔ فصل ۵۷: یک تابع، چهار مسیر اجرا

این پروژه یک مسئلهٔ بسیار کوچک و ساختگی را با محاسبهٔ تحلیلی و در صورت نصب‌بودن با PyTorch، JAX یا TensorFlow روی **CPU** می‌سنجد. هدف، کنترل قرارداد API و گرادیان است؛ نه رتبه‌بندی سرعت یا کیفیت چارچوب‌ها.

- هیچ مدل ازپیش‌آموزش‌دیده، مجموعه‌دادهٔ واقعی یا سرویس شبکه بارگذاری نمی‌شود.
- پروژه training loop، GPU، benchmark، حافظهٔ اوج، استقرار یا کیفیت مدل را نمی‌آزماید.
- فقط چارچوبی وارد می‌شود که کاربر انتخاب کند؛ `--backend all` چارچوب غایب را `not_installed` ثبت می‌کند و چیزی را نصب/دانلود نمی‌کند.
- بخش مرجع و کل آزمون‌های ورودی با کتابخانهٔ استاندارد Python اجرا می‌شوند.

## اجرا

```bash
python framework_compare.py --backend reference
python framework_compare.py --backend all --output /tmp/framework-report.json
python -m unittest -v
```

برای آزمودن یک چارچوب که از قبل در همین محیط نصب است:

```bash
python framework_compare.py --backend torch
python framework_compare.py --backend jax
python framework_compare.py --backend tensorflow
```

در انتخاب صریح، نبودن چارچوب خطای خروجی است؛ در حالت `all` نبودن هر بسته به‌صورت skip گزارش می‌شود. فایل `results.json` snapshot اجرای واقعی یک venv با PyTorch 2.15.0+cpu و Python 3.13.16 است؛ JAX و TensorFlow در همان venv نصب نبودند. adapterهای JAX و TensorFlow جداگانه و در محیط‌های مستقل آزموده شده‌اند؛ جزئیات در گزارش ممیزی فصل است. هیچ‌یک از این خروجی‌ها گواه سازگاری سیستم‌های دیگر نیست.

## محیط پیشنهادی برای مطالعه

نسخه‌ها در زیر یک **snapshot تاریخ‌دار** برای متن فصل‌اند (2026-11-06)، نه توصیهٔ ارتقای هم‌زمان. Python 3.12 را برای این مقایسهٔ مشترک برمی‌گزینیم، چون مستند TensorFlow 2.21 در متن نیازمندی عمومی تا 3.12 را می‌گوید، درحالی‌که جدول wheel همان صفحه برای 3.13 هم artifact نشان می‌دهد. هنگام نصب، جدول دقیق سیستم‌عامل/معماری را دوباره بررسی کنید.

هر چارچوب را در virtual environment جدا نصب کنید. این دستورها نمونهٔ CPU هستند؛ نصب CUDA/ROCm/MPS/XPU/TPU، driver و wheel را از selector و راهنمای رسمی همان نسخه تعیین کنید.

### PyTorch 2.15.0 — CPU

```bash
python3.12 -m venv .venv-torch
source .venv-torch/bin/activate
python -m pip install --upgrade pip
python -m pip install "torch==2.15.0" --index-url https://download.pytorch.org/whl/cpu
```

### JAX 0.12.0.1 — CPU

```bash
python3.12 -m venv .venv-jax
source .venv-jax/bin/activate
python -m pip install --upgrade pip
python -m pip install "jax==0.12.0.1"
```

### TensorFlow 2.21.0 — CPU

```bash
python3.12 -m venv .venv-tensorflow
source .venv-tensorflow/bin/activate
python -m pip install --upgrade pip
python -m pip install "tensorflow==2.21.0"
```

در PowerShell، ساخت محیط با `py -3.12 -m venv .venv-tensorflow` انجام می‌شود و فعال‌سازی آن `\.venv-tensorflow\Scripts\Activate.ps1` است. راه درست نصب GPU را از مستند رسمی نسخه و سیستم هدف بگیرید؛ دستور یک backend را به دیگری تعمیم ندهید.

## قرارداد مسئله

Fixture `sample_problem.json` دو نقطهٔ مصنوعی `x=[0,1]`, `y=[1,3]` و پارامترهای آغازین `w=1`, `b=0` دارد. برای `MSE = mean((w*x+b-y)^2)`، مرجع تحلیلی باید `loss=2.5`, `dw=-2`, `db=-3` بدهد. اختلاف مطلق تا `1e-5` پذیرفته می‌شود تا گردکردن float32، device و backend با برابری بیت‌به‌بیت اشتباه گرفته نشود.

Fixture هم از نظر schema و هم از نظر ادعا محدود است. خروجی SHA-256 آن را گزارش می‌کند و نشان می‌دهد کدام چارچوب واقعاً اجرا شده، کدام نصب نبوده و کدام آزمون شکست خورده است.
