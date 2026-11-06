# گزارش ممیزی فصل ۵۷ — Python، PyTorch، JAX و TensorFlow

**تاریخ بازبینی محتوایی/نسخه‌ها: 2026-11-06.** این گزارش شواهد همین build، آزمون CPU و fixture کوچک را ثبت می‌کند؛ تأیید سازگاری همهٔ سیستم‌ها، benchmark، کیفیت محصول یا پشتیبانی آینده نیست.

## جایگاه و مرز فصل

فصل محلی ۱۱ / سراسری ۵۷ بعد از فصل ۵۶ (بودجه و هزینهٔ مالکیت) قرار گرفته است. موضوعش انتخاب چارچوب و ساخت محیط Python برای PyTorch، JAX و TensorFlow است؛ فصل ۵۸ اکوسیستم Hugging Face و فصل ۵۹ CUDA، ROCm، Triton و مقیاس‌پذیری را جداگانه پوشش می‌دهند. این فصل قیمت، TCO، benchmark خرید/اجاره، عملیات MLOps، دانلود مدل یا آموزش واقعی ندارد.

نسخه‌های درج‌شده در متن به‌صورت snapshot تاریخ‌دارند: CPython 3.15.2، PyTorch 2.15.0، JAX 0.12.0.1 و TensorFlow 2.21.0. مستند جاری TensorFlow در متن عمومی Python 3.9–3.12 و در جدول wheelها Python 3.13 را نیز نشان می‌دهد؛ فصل این ناهمخوانی را آشکار می‌کند و برای شروع مشترک Python 3.12 را انتخاب می‌کند. آزمون‌های جداگانهٔ ممیزی در Linux x86_64 با Python 3.13.16 اجرا شدند؛ این شاهد فقط همان platform و wheel است.

## شواهد پروژه و fixture

پوشهٔ `book-engineering/projects/57-framework-lab/` شامل `framework_compare.py`, `test_framework_compare.py`, `sample_problem.json`, `README.md` و `results.json` است. fixture با `label_source=synthetic_fixture` علامت‌گذاری شده است. بخش مرجع، MSE و گرادیان خطی را با کتابخانهٔ استاندارد Python محاسبه می‌کند؛ adapterهای اختیاری فقط framework انتخاب‌شده را import می‌کنند و `--backend all` بستهٔ غایب را skip می‌کند. هیچ network call، مجموعه‌دادهٔ واقعی، مدل ازپیش‌آموزش‌دیده یا دادهٔ بیرونی ندارد.

SHA-256 فایل `sample_problem.json`:

```text
b9c134951bbf77a0bee3ec3c498e332bb63810a95638fa1efb7b256a1cc69771
```

مرجع تحلیلی و هر adapter آزموده‌شده مقدارهای زیر را در tolerance مطلق `1e-5` بازگرداند:

```text
loss = 2.5
gradient_weight = -2.0
gradient_bias = -3.0
```

`results.json` خروجی ثبت‌شده از یک venv مجزای PyTorch 2.15.0+cpu / NumPy 2.3.5 است. در آن محیط، JAX و TensorFlow نصب نبودند و به‌درستی `not_installed` ثبت شده‌اند؛ آن‌ها به‌طور جداگانه در venvهای مستقل آزموده شدند، نه اینکه هر سه چارچوب را در یک محیط ترکیب کنیم.

## نتایج اجرای واقعی آزمون‌ها

آزمون‌ها با CPython 3.13.16 در Linux x86_64، CPU و fixture ساختگی اجرا شدند. در هر venv فقط یک framework نصب بود:

| محیط | چارچوب نصب‌شده | آزمون unit | آزمون adapter/CLI |
|---|---|---:|---|
| Python پایه، بدون framework | هیچ‌کدام | ۱۵ مورد؛ ۱۲ موفق، ۳ skip اختیاری | `--backend reference` و `--backend all`؛ مرجع درست، سه بسته `not_installed`، بدون شکست |
| venv مستقل، NumPy 2.3.5 | PyTorch 2.15.0+cpu | ۱۵ مورد؛ ۱۳ موفق، ۲ skip | `test_torch_cpu_adapter_when_installed` موفق؛ `--backend all`: PyTorch `passed`، JAX/TensorFlow نصب نبودند |
| venv مستقل | JAX 0.12.0.1، `jaxlib` 0.12.0.1 | ۱۵ مورد؛ ۱۳ موفق، ۲ skip | `test_jax_cpu_adapter_when_installed` و `--backend jax` موفق |
| venv مستقل | TensorFlow 2.21.0 | ۱۵ مورد؛ ۱۳ موفق، ۲ skip | `test_tensorflow_cpu_adapter_when_installed` و `--backend tensorflow` موفق؛ device صریح CPU |
| venv هم‌راستا با manifest مخزن | PyTorch 2.6.0+cpu، NumPy 2.3.5 | ۱۵ مورد؛ ۱۳ موفق، ۲ skip | `--backend all` موفق با PyTorch؛ این همان نسخهٔ PyTorch پین‌شده در `requirements.txt` است |

برای هر adapter موفق، زیان، هر دو گرادیان و اختلاف از مرجع برابر مقادیر جدول بالا/صفر بود. TensorFlow هنگام import پیام می‌دهد driver CUDA در این میزبان نیست؛ کد adapter در `/CPU:0` اجرا شد. این پیام به معنی آزمون GPU نیست. سه skip در محیط بدون framework و دو skip در هر venv تک-framework، skipهای آگاهانه‌اند؛ هیچ‌یک به‌عنوان pass چارچوب غایب شمرده نشده‌اند.

## کنترل ساخت و فایل‌ها

- [فصل](57-ml-frameworks.md) شامل مقایسهٔ API، انتخاب، نصب CPU و هشدار platform-specific است؛ نسخه‌ها تاریخ دارند.
- [پاسخ‌نامهٔ مستقل](../answers/57-ml-frameworks-fa.md) تمرین‌ها را جدا پاسخ می‌دهد.
- نمودار [مسیر انتخاب و سازگاری](../diagrams/v4-ch11-framework-selection.svg) SVG محلی و دارای title/description دسترس‌پذیر است.
- کد انتهای فصل و `framework_compare.py` بایت‌به‌بایت برابرند؛ `sample_problem.json` در خروجی SHA-256 دارد.
- builder از حالت معمول استفاده شد و فصل جدید را بعد از فصل منتشرشدهٔ ۵۶ append کرد؛ هیچ `--refresh-last-draft` برای فصل منتشرشده به کار نرفت.
- checker جلد چهارم برای ۱۱ فصل، ۲۵۱ بخش، ۵۴ عبارت MathML، fixture، پاسخ‌نامه و مسیر offline اجرا شد.
- `book-engineering/test_volume4.py` در ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل، شناسه‌ها، MathML، لینک پاسخ‌نامه، نمودار، کد دقیق پیوست و cache offline را بررسی کرد؛ ۱۰۷ دارایی precache شدند.
- `book-engineering/test_mobile_layout.py` در ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل اجرا شد؛ محتوای جلد چهارم ۱٬۰۵۶ بخش داشت و فایل فصل، پاسخ‌نامه و نمودار این فصل در offline قابل دریافت بود.

چند asset قدیمی نامرتبط خارج از فصل در sparse checkout همچنان درخواست 404 می‌دهند؛ فایل‌ها تغییر داده نشدند و دارایی‌های فصل ۵۷ در cache موجودند. این نسخه وب/PWA و Markdown است؛ PDF یا EPUB در این ممیزی تولید یا آزموده نشده‌اند.

## محدودیت‌ها

- هیچ سخت‌افزار واقعی برای سنجش بار/کارایی، GPU واقعی، CUDA/ROCm/MPS/TPU، مدل بزرگ، dataset واقعی، training loop یا workload محصول اجرا نشد.
- هیچ latency، throughput، peak memory، کیفیت یا قابلیت تعمیم benchmark نشد.
- نصب‌های CPU با نسخه‌های نام‌برده در محیط Linux x86_64 انجام شدند؛ نتیجه را به macOS، Windows، ARM، container یا GPU دیگر تعمیم ندهید.
- برای TensorFlow، ماتریس wheel مستندات همان نسخه/OS را پیش از نصب دوباره بررسی کنید؛ متن عمومی Python و جدول wheel صفحه در snapshot بازبینی هم‌راستا نبودند.
- خروجی PyTorch/JAX/TensorFlow سه تست کوچک مستقل است؛ یکسانی این toy gradient هم‌ارزی API، سرعت یا رفتار model-level را ثابت نمی‌کند.

## منابع

ارجاع‌های نسخه‌ای و نصب در [منابع و تاریخ بازبینی فصل ۵۷](57-ml-frameworks.md) آمده‌اند؛ منابع اصلی Python.org، PyTorch.org / GitHub releases، docs.jax.dev و tensorflow.org هستند. آخرین بررسی آن صفحات: 2026-11-06.
