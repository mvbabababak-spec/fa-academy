# جلد چهارم، فصل ۱۱ — Python، PyTorch، JAX و TensorFlow: مقایسه و راه‌اندازی

> **جایگاه:** فصل محلی ۱۱ از ۱۵ جلد چهارم؛ فصل سراسری ۵۷. فصل ۵۶ هزینهٔ مالکیت و بودجه را بررسی کرد؛ اکنون محیط نرم‌افزاری و چارچوب محاسبه را انتخاب و روی CPU راه‌اندازی می‌کنیم.
>
> **مرز موضوعی:** Python زبان و محیط اجرای برنامه است؛ PyTorch، JAX و TensorFlow چارچوب‌ها/اکوسیستم‌های محاسبه و یادگیری‌اند. فصل ۵۸ به ابزارهای Hugging Face می‌پردازد و فصل ۵۹ سراغ CUDA، ROCm، Triton و مقیاس‌پذیری می‌رود. این فصل آن دو را جایگزین نمی‌کند.
>
> **حد ادعا:** نسخه‌ها یک snapshot تاریخ‌دارند. نصب CPU و مقایسهٔ گرادیان روی fixture کوچک، سازگاری هر GPU، سرعت، کیفیت مدل یا آمادگی استقرار را اثبات نمی‌کند. هر نتیجهٔ عملکردی باید روی workload، سخت‌افزار و محدودیت واقعی خودتان اندازه‌گیری شود.
>
> **تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶.**

## ۱. از «کدام چارچوب بهتر است؟» به «کدام قرارداد برای کار من می‌خواند؟»

معمولاً پاسخ یکسانی برای همهٔ تیم‌ها وجود ندارد. چارچوب بخشی از زنجیره‌ای است که زبان، بسته‌ها، سیستم‌عامل، سخت‌افزار، مدل، داده و محیط استقرار را به هم وصل می‌کند. کتابخانه‌ای که همکاران می‌شناسند یا مدل‌های موجودتان از آن پشتیبانی می‌کنند، ممکن است گزینهٔ کم‌ریسک‌تری از گزینه‌ای باشد که در نمودار مقایسه «قابلیت بیشتر» دارد.

هدف این فصل دو خروجی عملی است:

1. با شناخت تفاوت‌های اصلی PyTorch، JAX و TensorFlow، shortlist بسازید و برای هرکدام سؤال‌های سازگاری را بدانید.
2. یک محیط Python جدا بسازید، نسخه/دستگاه نصب را ثبت کنید و یک مسئلهٔ کوچک یکسان را با CPU اجرا کنید.

پیش از انتخاب، بنویسید **چه چیزی باید کار کند**: سیستم‌عامل و معماری CPU، نسخهٔ Python، نوع accelerator، مدل و workload، نیازهای دقت/حافظه، بسته‌های جانبی، مسیر export یا سرو و مهارت تیم. «PyTorch سریع است» یا «JAX مدرن‌تر است» الزام قابل آزمون نیست.

![شکل ۴-۱۱-۱ — نخست workload و محیط را مشخص می‌کنیم، سپس یک مسئلهٔ یکسان را در PyTorch، JAX یا TensorFlow روی CPU می‌سنجیم، ماتریس بسته و سخت‌افزار را بررسی می‌کنیم و فقط بعد از آزمون واقعی تصمیم می‌گیریم؛ شکل benchmark یا رتبه‌بندی کارایی نیست.](book-engineering/diagrams/v4-ch11-framework-selection.svg)

شکل ۴-۱۱-۱ — مسیر انتخاب از قرارداد workload تا smoke test؛ سبک API و پشتیبانی سخت‌افزار را جدا بررسی کنید.

## ۲. Python زبان/مفسر است؛ چارچوب tensor چیز دیگری

Python زبان برنامه‌نویسی و محیط اجرای بسیاری از ابزارهای یادگیری است. PyTorch، JAX و TensorFlow بسته‌هایی هستند که روی Python و وابستگی‌های بومی آن نصب می‌شوند. نصب Python به‌تنهایی هیچ‌یک از آن‌ها را فعال نمی‌کند؛ و نصب یک چارچوب هم تضمین نمی‌کند wheel سازگار با سیستم‌عامل یا شتاب‌دهندهٔ شما پیدا شود.

یک نصب عملی دست‌کم پنج لایه دارد:

1. **مفسر و ABI:** مثلاً CPython 3.12 و نوع build آن؛ نسخهٔ بسته باید برای همین ABI wheel داشته باشد.
2. **محیط مجازی و بسته‌ها:** کدام `python` و `pip` دریافت‌کنندهٔ فرمان‌اند؟ آیا dependencyها با هم سازگارند؟
3. **سیستم و معماری:** Linux/Windows/macOS، نسخهٔ glibc یا حداقل سیستم‌عامل، x86-64 یا ARM64.
4. **شتاب‌دهنده و driver/runtime:** CPU، NVIDIA/CUDA، AMD/ROCm، Apple GPU، Intel یا TPU؛ پشتیبانی بسته و driver باید برای ترکیب دقیق بررسی شود.
5. **کد و داده:** نسخهٔ مدل، کتابخانه‌های همراه، شکل ورودی، dtype، سیاست دسترسی/مجوز و هدف اجرا.

پس هنگام نصب، دستور را با `python -m pip` اجرا کنید؛ این کار احتمال استفاده از `pip` متعلق به Python دیگری را کم می‌کند. هر پروژه را در virtual environment مستقل نگه دارید. «روی لپ‌تاپم import شد» هنوز آزمون مدل، GPU یا production نیست.

## ۳. نسخه‌ها را به‌عنوان snapshot بخوانید، نه فهرست دائمی سازگاری

جدول زیر، نسخه‌ها و نکته‌های منتشرشده در **۶ نوامبر ۲۰۲۶** را ثبت می‌کند. بسته‌های ML سریع عوض می‌شوند؛ پیش از نصب، همان ماتریس رسمی را دوباره باز کنید و نسخهٔ دقیق Python/OS/device را تطبیق دهید.

| جزء | snapshot رسمیِ مورد بررسی | پیام برای نصب |
|---|---|---|
| CPython | `3.15.2`؛ انتشار ۲۵ اکتبر ۲۰۲۶ | تازه‌ترین CPython پایدار در تاریخ این بازبینی است؛ اما جدیدترین نسخهٔ Python لزوماً نقطهٔ مشترک wheelهای همهٔ چارچوب‌ها نیست. |
| PyTorch | `2.15.0`؛ stable در صفحهٔ نصب و انتشار ۲۸ اکتبر ۲۰۲۶؛ نسخه‌های wheel باینری از Python `3.11` به بالا، تا `3.15` در یادداشت انتشار | wheel/اندیس CPU، CUDA یا ROCm را از selector همان نسخه انتخاب کنید. در این release، PyPI به CUDA 13.2 منتقل شده و wheelهای رسمی cu134 هم جداگانه فهرست شده‌اند؛ دستور قدیمی cu118 یا cu126 را بی‌بررسی کپی نکنید. |
| JAX | `0.12.0.1`؛ در changelog رسمی مورخ ۲۳ اکتبر ۲۰۲۶ | `jax` و `jaxlib` بسته‌های جدا هستند؛ نوع wheel و backend برای CPU/GPU/TPU و سیستم‌عامل مهم است. مستند جاری برای CUDA 13 نمونهٔ `jax[cuda13]` دارد؛ جزئیات driver و پلتفرم را همان‌جا کنترل کنید. |
| TensorFlow | `2.21.0`؛ نسخهٔ مستندشده در صفحهٔ رسمی نصب pip | صفحهٔ جاری در متن نیازمندی عمومی Python `3.9–3.12` می‌گوید، ولی جدول wheelهای 2.21 برای بعضی platformها Python 3.13 را هم نشان می‌دهد و هم‌زمان یادآور می‌شود 3.9 پشتیبانی نمی‌شود. این ناهمخوانی را پنهان نکنید؛ برای آموزش مشترک در این فصل Python 3.12 انتخاب شده و برای 3.13 باید wheel دقیق سیستم هدف بررسی شود. |

**قاعدهٔ انتخاب محیط مشترک:** برای آزمایش کوتاهِ هر سه چارچوب، از نسخه‌ای استفاده کنید که همگی آن را پشتیبانی می‌کنند؛ در snapshot بالا، Python 3.12 انتخاب محافظه‌کارانه‌تری از 3.15 است. برای پروژهٔ تولیدی، نسخه را از روی ماتریس همان بسته‌ها، سیستم‌عامل و سخت‌افزار ثبت کنید؛ نه فقط چون «latest» است.

## ۴. مقایسهٔ کوتاه: چه چیزی واقعاً متفاوت است؟

| بُعد | PyTorch | JAX | TensorFlow |
|---|---|---|---|
| مدل ذهنی رایج | عملیات eager و tensorهای Python؛ autograd برای گرادیان | آرایه/تابع و تبدیل‌های صریح مثل `grad`, `jit`, `vmap`؛ اجرا اغلب با tracing/کامپایل XLA | eager mode برای توسعه؛ `GradientTape`، `tf.function` و API سطح‌بالای Keras |
| کِی راحت شروع می‌شود؟ | وقتی می‌خواهید مرحله‌به‌مرحله tensor را ببینید یا از مدل/ابزارهای PyTorch استفاده کنید | وقتی محاسبهٔ عددی را به تابع‌های خالص و تبدیل‌پذیر می‌نویسید و ترکیب گرادیان/vectorization/JIT مهم است | وقتی Keras و قراردادهای TensorFlow در تیم یا مسیر محصول موجودند و eager/graph هر دو به کار می‌آیند |
| چیزی که باید از پیش بدانید | `torch.compile` گزینهٔ بهینه‌سازی/کامپایل است، نه کلید تضمین سرعت؛ graph break، compile time و ورودی واقعی را بسنجید | tracing، آثار جانبی Python و کلیدهای تصادفی صریح می‌توانند مدل ذهنی را تغییر دهند؛ تابع را تا جای ممکن تابعی نگه دارید | `tf.function` می‌تواند تابع را trace کند؛ ورودی‌های متغیر/آثار جانبی Python ممکن است رفتار retracing را پیچیده کنند |
| ریسک انتخاب | تصور اینکه eager برابر «همیشه ساده‌تر/سریع‌تر» است یا همهٔ افزونه‌ها با هر wheel سازگارند | پنداشتن اینکه هر کد NumPy/Python بدون تغییر JIT می‌شود؛ تفاوت پشتیبانی device را نادیده گرفتن | فرض اینکه نصب `tensorflow` به معنی GPU روی هر سیستم‌عامل است؛ در عمل جدول OS/device مهم است |
| پرسش تصمیم | آیا تیم، کد پایه و کتابخانه‌های شما PyTorch محورند؟ | آیا محاسبات شما تابعی/عددی و transformمحورند؟ | آیا Keras، گراف، ابزارهای TensorFlow یا مسیر خروجی شما از قبل به TensorFlow وابسته است؟ |

این جدول «برنده» معرفی نمی‌کند. واژه‌هایی مثل *dynamic graph*، *compiled graph* و *functional transformation* مسیرهای اجرایی را توضیح می‌دهند، نه کیفیت model یا هزینهٔ محصول. PyTorch هم قابلیت‌های کامپایل دارد؛ TensorFlow هم eager اجرا می‌شود؛ و JAX نیز می‌تواند در CPU اجرا شود. تفاوت‌ها مطلق یا ایستا نیستند.

## ۵. PyTorch: tensorهای آشکار و گرادیان خودکار

در حالت معمول، عملیات PyTorch فوراً روی tensor اجرا می‌شود. اگر پارامتری `requires_grad=True` داشته باشد، چارچوب مسیر محاسبه را دنبال می‌کند؛ با `backward()` گرادیان‌های لازم محاسبه می‌شوند. این سبک برای debugging مرحله‌ای و برای codebaseهای Python رایج راحت است.

از PyTorch می‌توانید با CPU شروع کنید و سپس انتخاب wheel/device را بررسی کنید. `torch.compile` می‌تواند بخش‌هایی از کد را کامپایل کند؛ اما compile time، graph break، اندازه/شکل ورودی و سرعت واقعی باید در سناریوی خودتان سنجیده شوند. فقط اجرای دوبارهٔ یک تابع مصنوعی یا اندازه‌گیری یک دور گرم‌نشده مقایسهٔ منصفانه‌ای نیست.

```python
import torch

x = torch.tensor([0.0, 1.0])
y = torch.tensor([1.0, 3.0])
w = torch.tensor(1.0, requires_grad=True)
b = torch.tensor(0.0, requires_grad=True)
loss = ((w * x + b - y) ** 2).mean()
loss.backward()
print(loss.item(), w.grad.item(), b.grad.item())  # 2.5, -2.0, -3.0
```

دستور نصب عمومی ممکن است wheel متفاوتی نسبت به CPU-only یا accelerator داشته باشد. برای کار CPU آموزشی از راهنمای رسمی همان پلتفرم استفاده کنید؛ برای CUDA، ROCm، Intel XPU یا Apple MPS نوع build را صریح انتخاب و بعد از نصب device را وارسی کنید.

## ۶. JAX: تبدیل تابع‌ها به محاسبه‌های قابل ترکیب

JAX آرایه‌های `jax.numpy` و تبدیل‌های تابعی ارائه می‌کند. `jax.grad` یا `jax.value_and_grad` مشتق را می‌گیرد؛ `jax.jit` تابع را برای کامپایل می‌برد؛ `jax.vmap` می‌تواند محاسبه را روی محور batch برداری کند. این تبدیل‌ها را می‌توان ترکیب کرد، اما آن‌ها قواعدی هم دارند: اجرای JIT مرحلهٔ trace دارد، مقدارهای پایتونی/آثار جانبی در زمان trace با اجرا فرق می‌کنند، و تغییر شکل/نوع ورودی ممکن است compilation جدید ایجاد کند.

در JAX معمولاً state تصادفی با PRNG key صریح مدیریت می‌شود. کلید را دوباره مصرف نکنید؛ آن را طبق الگوی `split` تقسیم کنید. این صراحت به بازبینی جریان randomness کمک می‌کند، اما به‌تنهایی reproducibility کامل across-device/version یا یک seed جهانی را تضمین نمی‌کند.

```python
import jax
import jax.numpy as jnp

x = jnp.array([0.0, 1.0])
y = jnp.array([1.0, 3.0])

def loss_fn(params):
    w, b = params
    return jnp.mean((w * x + b - y) ** 2)

loss, (dw, db) = jax.value_and_grad(loss_fn)((jnp.array(1.0), jnp.array(0.0)))
print(float(loss), float(dw), float(db))
```

`jit`، `grad` یا `vmap` را به عنوان قابلیت‌های برنامه‌نویسی ببینید، نه اندازه‌گیری کارایی. نصب CPU با `jax` ساده‌تر است؛ برای NVIDIA GPU، مستند جاری بستهٔ CUDA مناسب و محدودیت‌های driver/OS/معماری را جدا می‌کند. در تاریخ بازبینی، مستند JAX برای Windows x86-64 CPU و Apple GPU وضعیت متفاوتی از Linux NVIDIA GPU نشان می‌دهد؛ یک دستور را به همهٔ سیستم‌ها تعمیم ندهید.

## ۷. TensorFlow: eager برای ساخت، گراف و Keras برای مسیرهای دیگر

TensorFlow از eager اجرا پشتیبانی می‌کند؛ `tf.GradientTape` عملیات لازم برای گرادیان را ثبت می‌کند. Keras API سطح‌بالایی برای تعریف و آموزش مدل است؛ `tf.function` می‌تواند تابع را به مسیر graph ببرد. این ترکیب برای تیم‌هایی که قراردادها یا سامانه‌های TensorFlow دارند مناسب است، اما باید مشخص کنید در توسعه، آموزش و استقرار کدام API/format را واقعاً استفاده می‌کنید.

```python
import tensorflow as tf

x = tf.constant([0.0, 1.0])
y = tf.constant([1.0, 3.0])
w = tf.Variable(1.0)
b = tf.Variable(0.0)
with tf.GradientTape() as tape:
    loss = tf.reduce_mean(tf.square(w * x + b - y))
dw, db = tape.gradient(loss, [w, b])
print(float(loss), float(dw), float(db))
```

برای این فصل لازم نیست شبکهٔ عصبی، Keras model یا optimizer بسازید؛ هدف فقط این است که ببینید همان تابع و گرادیان را چگونه بیان می‌کنیم. TensorFlow نصب CPU را از `tensorflow` می‌گیرد؛ نصب NVIDIA GPU طبق مستند جاری مسیر `tensorflow[and-cuda]` دارد و به OS/driver پشتیبانی‌شده محدود است. مستند TensorFlow GPU را برای macOS رسمی نمی‌داند و Windows native GPU را برای نسخه‌های بالاتر از 2.10 پشتیبانی نمی‌کند؛ از راه قدیمی «نصب CUDA و امید بستن» استفاده نکنید.

## ۸. یک تابع مشترک، یک مرجع ریاضی

برای آنکه مقایسه به API یا نام برند منحرف نشود، همهٔ backendها یک fixture دو‌نقطه‌ای را می‌گیرند:

- ورودی: `x = [0, 1]`
- هدف: `y = [1, 3]`
- پارامتر آغازین: `w = 1`, `b = 0`
- پیش‌بینی: `[0, 1]`؛ باقیماندهٔ `ŷ − y = [-1, -2]`
- معیار: میانگین مربع خطا (Mean Squared Error, MSE)

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="زیان میانگین مربع خطا برای مدل خطی برابر میانگین مربع w x به‌علاوه b منهای y است">
  <mrow><mi>L</mi><mo>=</mo><mfrac><mn>1</mn><mi>n</mi></mfrac><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi></munderover><msup><mrow><mo>(</mo><mi>w</mi><msub><mi>x</mi><mi>i</mi></msub><mo>+</mo><mi>b</mi><mo>−</mo><msub><mi>y</mi><mi>i</mi></msub><mo>)</mo></mrow><mn>2</mn></msup></mrow>
</math>

**متن جایگزین فرمول:** `L = (1/n) Σᵢ (w xᵢ + b − yᵢ)²`؛ میانگین مربعات باقیماندهٔ پیش‌بینی است.

در این نقطه، `L = (1 + 4) / 2 = 2.5`. مشتق نسبت به `w` برابر `2/n × Σᵢ (w xᵢ+b−yᵢ)xᵢ = −2` است؛ نسبت به `b` برابر `2/n × Σᵢ (w xᵢ+b−yᵢ) = −3`. بنابراین مرجع پروژه `loss=2.5`, `gradient_weight=-2`, `gradient_bias=-3` دارد.

این fixture عمداً خیلی کوچک و شفاف است. درست‌بودن گرادیان در آن، سازگاری یک مدل زبانی، نرخ یادگیری مطلوب، تعمیم، دقت آماری یا سرعت را اثبات نمی‌کند. روی float32 نیز برابری بیت‌به‌بیت را شرط نکنید؛ پروژه اختلاف مطلق حداکثر `1e-5` را می‌پذیرد.

## ۹. پیش از انتخاب، معیارهای تصمیم را وزن‌دهی کنید

برای هر candidate، یک ردیف در برگهٔ ارزیابی بسازید و وضعیت را «پاسخ مستند»، «آزمون‌شده»، «نامعلوم» یا «رد» علامت بزنید:

| پرسش | شواهدی که جمع می‌کنید |
|---|---|
| مدل/کتابخانهٔ لازم اکنون در کدام چارچوب است؟ | مدل پایه، operatorهای خاص، نسخه و وابستگی‌ها؛ نه فقط یک صفحهٔ معرفی |
| کد را چه کسی نگه می‌دارد؟ | تجربهٔ تیم، debugging، استخدام/آموزش و هزینهٔ مهاجرت |
| محیط اجرا کجاست؟ | سیستم‌عامل، CPU/GPU/TPU، driver، container، سرو یا edge |
| هدف چیست؟ | پژوهش، fine-tuning، inference، batch processing یا محصول پایدار؛ هر workload آزمون خودش را می‌خواهد |
| چه محدودیت‌هایی قابل مذاکره نیستند؟ | مجوز، حفاظت داده، تأخیر، توان عملیاتی، حافظه، قابلیت export یا پشتیبانی vendor/community |
| مقایسه چطور منصفانه می‌شود؟ | همان مدل/وزن، دادهٔ مجاز، split، دقت، batch، سخت‌افزار، warm-up، تعداد اجرا و معیار پذیرش |

اگر مدل مورد نیاز فقط یک چارچوب یا accelerator را پشتیبانی کند، «سلیقهٔ API» ممکن است معیار دوم باشد. برعکس، اگر دو گزینه واقعاً معادل‌اند، هزینهٔ نگه‌داری و مسیر استخدام نیز بخشی از انتخاب است. پیش از benchmark، خروجی صحیح و کیفیت پذیرفته‌شده را تعریف کنید تا سرعتِ خروجی نادرست برنده نشود.

## ۱۰. ساخت محیط مجازی: Python را از پروژه جدا کنید

`venv` محیطی جدا با interpreter و مسیر نصب بسته‌ها می‌سازد. از پوشهٔ پروژه اجرا کنید:

**Linux/macOS:**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -c "import sys; print(sys.executable); print(sys.version)"
```

**Windows PowerShell:**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -c "import sys; print(sys.executable); print(sys.version)"
```

برای پایان جلسه، `deactivate` اجرا کنید. پوشهٔ `.venv` را به Git commit نکنید؛ dependencyها را در manifest نگه دارید. در CI، همان interpreter را صریح تعیین کنید و نصب/آزمون را در clean environment انجام دهید. اگر policy اجرا script در PowerShell فعال نیست، policy سازمان و مستند Python/Windows را دنبال کنید؛ برای دورزدن کنترل امنیتی، execution policy را بی‌فکر تغییر ندهید.

## ۱۱. نصب CPU: یک backend در یک virtual environment

پروژهٔ فصل را بدون چارچوب خارجی می‌توان اجرا کرد. وقتی می‌خواهید adapter واقعی را بیازمایید، یک محیط تازه بسازید؛ **سه دستور نصب را پشت سر هم در یک environment اجرا نکنید.** ترکیب NumPy، compiler، runtimeهای GPU و نسخه‌های وابستگی بین بسته‌ها ممکن است نیازهای متفاوتی داشته باشد.

**PyTorch 2.15.0، نمونهٔ CPU** (بعد از فعال‌سازی `.venv-torch`):

```bash
python -m pip install "torch==2.15.0" --index-url https://download.pytorch.org/whl/cpu
python -m pip check
python framework_compare.py --backend torch
```

**JAX 0.12.0.1، نمونهٔ CPU** (در `.venv-jax`):

```bash
python -m pip install "jax==0.12.0.1"
python -m pip check
python framework_compare.py --backend jax
```

**TensorFlow 2.21.0، نمونهٔ CPU** (در `.venv-tensorflow` و Python 3.12):

```bash
python -m pip install "tensorflow==2.21.0"
python -m pip check
python framework_compare.py --backend tensorflow
```

این دستورها snapshot آموزشی‌اند و محیط کاربر را در این کتاب به‌طور زنده نصب/آزمون نمی‌کنند. اگر سیستم‌عامل یا architecture در ماتریس همان نسخه نیست، wheel در دسترس نیست یا نصب به منبع بومی نیاز دارد، نصب را متوقف کنید و جدول رسمی را بررسی کنید؛ بدون مدرک، نسخه را حدس نزنید.

## ۱۲. GPU: اول ماتریس رسمی، بعد wheel و driver

نصب GPU فقط «یک بستهٔ Python اضافه» نیست. پیش از آن، موارد زیر را کنار هم ثبت کنید:

1. مدل دقیق GPU و معماری آن؛
2. OS، نسخه و architecture؛
3. حداقل driver و نسخه‌های CUDA/ROCm یا SDK مرتبط؛
4. Python ABI و wheel/index دقیق؛
5. container/host و محل libraryهای بومی؛
6. smoke test روی همان device.

- **PyTorch:** صفحهٔ «Start Locally» را با OS، installer، زبان و compute platform انتخاب کنید. CPU، CUDA و ROCm build جدا هستند. wheelهای 2.15 snapshot متفاوتی از releaseهای پیشین دارند؛ کپی‌کردن URL نسخهٔ قدیمی می‌تواند wheel ناسازگار نصب کند.
- **JAX:** مستند جاری CPU، NVIDIA CUDA، AMD ROCm، Intel، Apple و TPU را جداگانه فهرست می‌کند. برای NVIDIA در نسخهٔ مستندشده، wheel CUDA با pip نمونهٔ `jax[cuda13]` دارد؛ سیستم‌عامل/معماری و driver حداقل را پیش از نصب کنترل کنید.
- **TensorFlow:** برای Linux/WSL2 مبتنی بر NVIDIA، مستند pip مسیر `tensorflow[and-cuda]` را می‌آورد؛ Windows native GPU برای نسخه‌های بالاتر از 2.10 پشتیبانی نمی‌شود و در macOS GPU رسمی ندارد. نصب شدن بسته به معنی دیده‌شدن GPU نیست.

در همهٔ چارچوب‌ها، `is_available` یا فهرست deviceها فقط کشف اولیه است؛ اجرای یک tensor هم مدل واقعی را benchmark نمی‌کند. اگر toolkit جداگانه دارید، library path و runtime را با مستند همان wheel تطبیق دهید؛ ترکیب چند نسخهٔ CUDA/ROCm در یک process می‌تواند import یا kernel loading را خراب کند. محاسبهٔ هزینهٔ GPU، انتخاب خرید/اجاره و نرخ بازار در فصل ۵۶ است و در اینجا تکرار نمی‌شود.

## ۱۳. آزمون نصب را مرحله‌ای انجام دهید

ترتیب کم‌ریسک این است:

1. چاپ `sys.executable`, `sys.version` و مسیر `pip`؛ مطمئن شوید virtual environment فعال است.
2. چاپ نسخهٔ بسته و `pip check`؛ این‌ها ناسازگاری dependency را می‌جویند، نه correctness مدل را.
3. یک CPU smoke test کوچک با یک input معلوم؛ مقدار، شکل tensor و finite بودن خروجی را کنترل کنید.
4. اگر GPU لازم است، ابتدا device enumeration و سپس forward/backward خیلی کوچک روی device صریح را اجرا کنید.
5. تنها پس از آن workload واقعی و testهای کیفیت/کارایی را با دادهٔ مجاز اجرا کنید.

پروژهٔ پیوست، همین قاعده را در مقیاس toy نشان می‌دهد. `python framework_compare.py --backend all` فقط adapterهای نصب‌شده را import می‌کند و بسته‌های غایب را skip می‌کند؛ هیچ دانلود مدل/داده یا نصب انجام نمی‌شود. اگر یک adapter عددی با مرجع تفاوت بیش از tolerance داشته باشد، گزارش آن را failure می‌زند.

## ۱۴. نسخه‌گذاری و بازتولیدپذیری: `pip freeze` به‌تنهایی کافی نیست

برای هر محیطی که باید دوباره ساخته شود، حداقل این‌ها را ثبت کنید:

- نسخهٔ دقیق CPython، OS/architecture و manager مورد استفاده؛
- package version و همهٔ direct/transitive dependencies؛
- PyPI یا index سفارشی/wheel channel، hash فایل‌ها یا lockfile با hash؛
- accelerator، driver و runtime/SDK؛
- دستور نصب، commit کد، fixture hash و دستور آزمون؛
- اینکه آزمون CPU یا GPU بوده و آیا download/benchmark واقعی رخ داده است.

`pip freeze` snapshot خوبی برای اشکال‌زدایی است، ولی به‌تنهایی فایل lock قابل بازسازی نیست: index، wheel platform، hash، driver و سخت‌افزار را کامل نمی‌کند. برای محیط محصول، از lock manager مورد تأیید تیم یا container pinشده استفاده کنید و به‌روزرسانی امنیتی را به‌صورت کنترل‌شده بازبینی کنید. secrets و tokenها را در requirements، output و notebook commit نکنید. wheel را فقط از index معتبر بگیرید و provenance/hash را برای pipeline حساس نگه دارید.

## ۱۵. اعداد تصادفی، dtype و رفتار eager/compiled را یکی فرض نکنید

Seed لازم است، اما reproducibility ممکن است به CUDA kernel nondeterministic، ترتیب داده، worker، نسخه، compiler، device و deterministic flag وابسته باشد. JAX key صریح را مصرف/تقسیم می‌کند؛ در PyTorch و TensorFlow نیز generator/seed همان نسخهٔ API را بررسی کنید. ثبت seed، نتیجهٔ دقیق across-device را تضمین نمی‌کند.

همچنین `float32`, `bfloat16`, `float16` یا precision پایین‌تر ممکن است روی deviceهای مختلف kernel، rounding، underflow/overflow و کیفیت متفاوت داشته باشند. در این فصل مقایسه همه در CPU/float32 است. برای انتخاب precision واقعی، فصل ۴۵ را به‌عنوان پیش‌نیاز مفهومی مرور کنید و روی مدل/workload خود معیار کیفیت و خطای عددی بگذارید.

وقتی JIT/compile یا graph را فعال می‌کنید، زمان اجرای نخستین تابع ممکن است شامل tracing/compile باشد؛ warm-up را از اندازه‌گیری جدا کنید. تغییر shape و control flow می‌تواند compile/retrace داشته باشد. اگر عملکرد می‌سنجید، تعداد تکرار، synchronization، warm-up، دمای دستگاه و هزینهٔ انتقال داده را ثبت کنید. پروژهٔ این فصل هیچ‌یک را اندازه نمی‌گیرد.

## ۱۶. خطاهای رایج و مسیر تشخیص

| نشانه | علت‌های محتمل | قدم بعد |
|---|---|---|
| `No matching distribution found` | Python ABI، OS، architecture یا index انتخابی wheel ندارد؛ `pip` قدیمی است | `python -m pip --version`, `python -m pip debug --verbose` و ماتریس رسمی همان release را بررسی کنید؛ نسخه را تصادفی downgrade نکنید. |
| `ModuleNotFoundError` بعد از نصب | `pip` به interpreter دیگری نصب کرده، environment فعال نیست، یا محیط IDE متفاوت است | `python -c "import sys; print(sys.executable)"` را در terminal و IDE مقایسه و با همان interpreter نصب کنید. |
| نصب شد، اما GPU پیدا نشد | CPU wheel، driver ناسازگار، platform خارج از ماتریس، device visibility یا library path | فرمان نصب، driver و device را از مستند framework/version دوباره وارسی کنید؛ یک CPU test را با GPU test اشتباه نگیرید. |
| `pip check` خطا می‌دهد | dependencyهای مشترک در یک محیط به pinهای ناسازگار نیاز دارند | محیط را بازسازی کنید؛ backendها را در venvهای جدا نگه دارید و dependency resolver را با lock بررسی کنید. |
| JAX `Tracer`/آرایهٔ traced را به NumPy/Python تبدیل نمی‌کند | اجرای trace-time با اجرای عادی یکسان فرض شده یا تابع اثر جانبی/host callback دارد | تابع را با عملیات JAX بنویسید؛ ورودی static و dynamic را جدا کنید و مستند tracing را بخوانید. |
| `tf.function` بارها trace می‌شود | شکل/ساختار ورودی یا object پایتونی ناپایدار است | امضای ورودی/shape را تعریف کنید و با profiler/trace count علت را بسنجید؛ فقط برای پنهان‌کردن هشدار decorator اضافه نکنید. |
| PyTorch compile کندتر از eager دیده می‌شود | هزینهٔ compile/warm-up، graph break، ورودی کوچک یا اجراهای بسیار کم | warm-up را جدا کنید، چند اندازه‌گیری همسان انجام دهید و eager را baseline نگه دارید. |

خطا را از stderr کامل، نسخه‌ها و فرمان نصب بازتولید کنید. پیام «device unavailable» را با تغییر دستی library path یا نصب تصادفی چند toolkit پنهان نکنید؛ اول علت ناسازگاری را پیدا کنید.

## ۱۷. تمرین‌ها: از نیاز به تصمیم بازبینی‌پذیر

۱. برای تیمی که یک مدل موجود فقط checkpoint و مثال رسمی PyTorch دارد، ولی deployment نهایی هنوز مشخص نیست، سه سؤال برای shortlisting بنویسید. چرا «PyTorch حتماً برنده است» نتیجهٔ زودهنگام است؟

۲. تیمی محاسبات تابعی، برداری‌سازی batch و JIT را در CPU/GPU پژوهشی می‌خواهد. کدام ویژگی JAX را اول بررسی می‌کنید؟ چه محدودیتی دربارهٔ tracing و hardware wheel باید ثبت شود؟

۳. یک محصول داخلی از Keras/TF استفاده می‌کند، اما توسعه‌دهندهٔ جدید می‌خواهد همه‌چیز را با یک مثال eager ارزیابی کند. چه دو آزمونی پیش از مهاجرت لازم است؟

۴. چرا Python 3.15.2 را نباید تنها به‌خاطر «جدیدترین نسخه» در محیط مشترک TensorFlow 2.21 انتخاب کرد؟ نسخهٔ مشترک محافظه‌کارانهٔ این فصل چیست و چرا؟

۵. اجرای `framework_compare.py --backend all` دو چارچوب را skip می‌کند و PyTorch را پاس می‌کند. چه چیزی واقعاً نشان داده شده و چه چیزی هنوز نامعلوم است؟

۶. `torch.cuda.is_available()` در سیستم NVIDIA مقدار `False` می‌دهد، ولی `import torch` موفق است. سه بررسی را به ترتیب پیشنهاد دهید؛ آیا این خطا ثابت می‌کند GPU خراب است؟

## ۱۸. پاسخ نمونه و مسیر ادامه

پاسخ‌های تشریحی در [پاسخ‌نامهٔ مستقل فصل ۵۷](book-engineering/answers/57-ml-frameworks-fa.md) قرار دارند. پاسخ مناسب ممکن است با نیاز پروژه فرق کند، اما باید فرض و شاهد خود را آشکار کند.

جمع‌بندی اجرایی: **یک interpreter مشخص، یک venv برای هر چارچوب، نسخهٔ snapshot ثبت‌شده، CPU smoke test، سپس ماتریس platform/device و آزمون workload واقعی.** انتخاب framework را با cost/market فصل ۵۶، Hugging Face در فصل ۵۸ یا accelerator programming فصل ۵۹ خلط نکنید.

## ۱۹. منابع و تاریخ بازبینی

منابع رسمی بررسی‌شده در 2026-11-06؛ نسخهٔ آنلاین بعداً ممکن است تغییر کند:

1. Python Software Foundation, [Python 3.15.2 release](https://www.python.org/downloads/release/python-3152/), منتشرشده 2026-10-25؛ مرجع نسخهٔ CPython و artifactهای release.
2. PyTorch Foundation, [PyTorch 2.15 Release Blog](https://pytorch.org/blog/pytorch-2-15-release-blog/), 2026-10-28؛ و [PyTorch 2.15.0 release notes](https://github.com/pytorch/pytorch/releases/tag/v2.15.0), شامل Python/wheel و تغییر release.
3. PyTorch, [Start Locally](https://pytorch.org/get-started/locally/), selector نسخه/OS/installer/compute platform؛ [Autograd mechanics](https://pytorch.org/docs/stable/notes/autograd.html) و [torch.compile tutorial](https://pytorch.org/tutorials/intermediate/torch_compile_tutorial.html).
4. JAX, [Change log](https://docs.jax.dev/en/latest/changelog.html), شامل JAX 0.12.0.1 در 2026-10-23؛ [Installation](https://docs.jax.dev/en/latest/installation.html), ماتریس CPU/GPU و دستورهای backend؛ [JAX versioning](https://docs.jax.dev/en/latest/jep/9419-jax-versioning.html), رابطهٔ `jax` و `jaxlib`.
5. TensorFlow, [Install TensorFlow with pip](https://www.tensorflow.org/install/pip), نسخهٔ stable، Python/wheel matrix و تفاوت CPU/GPU/OS؛ صفحهٔ منبع را دوباره تطبیق دهید، چون متن عمومی Python و جدول wheelهای آن snapshot یکسان نیستند.
6. Python documentation, [`venv`](https://docs.python.org/3/library/venv.html), محیط‌های مجازی و دستورهای platform.
7. PyPA, [Installing Packages](https://packaging.python.org/en/latest/tutorials/installing-packages/) و [Requirements for a packaging tool](https://packaging.python.org/en/latest/specifications/requirements-file-format/), برای نصب و قرارداد فایل requirements.
8. PyTorch, [Get Started](https://pytorch.org/get-started/locally/), JAX, [Installation](https://docs.jax.dev/en/latest/installation.html), و TensorFlow, [pip installation](https://www.tensorflow.org/install/pip), برای ماتریس wheelهای وابسته به سیستم.

این فهرست توصیهٔ خرید، benchmark، endorsement یا تضمین سازگاری نیست. نسخهٔ ثبت‌شده فقط snapshot است؛ پیش از اجرای واقعی، صفحهٔ رسمی را در تاریخ کار خود بررسی کنید.

## ۲۰. پیوست اجرایی: کد آزموده‌شدهٔ پروژه

کد زیر بایت‌به‌بایت با `book-engineering/projects/57-framework-lab/framework_compare.py` نگه داشته می‌شود. اجرای مرجع فقط به کتابخانهٔ استاندارد Python نیاز دارد؛ adapterهای اختیاری فقط چارچوب‌های ازپیش‌نصب‌شده را import می‌کنند.

```python
"""Compare automatic gradients on one tiny, explicitly synthetic CPU fixture.

Only the selected optional framework is imported. No model, dataset, GPU, network,
training loop, or performance benchmark is used by this teaching smoke test.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import platform
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_FIXTURE = ROOT / "sample_problem.json"
BACKENDS = ("torch", "jax", "tensorflow")
METADATA_KEYS = (
    "real_dataset_loaded",
    "pretrained_model_loaded",
    "training_performed",
    "gpu_used",
    "benchmark_performed",
)


class ComparisonInputError(ValueError):
    """Raised when the synthetic comparison fixture is invalid."""


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ComparisonInputError(f"{field} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ComparisonInputError(f"{field} must be a finite number")
    return result


def validate_fixture(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ComparisonInputError("fixture must be a JSON object")
    if raw.get("schema_version") != 1:
        raise ComparisonInputError("unsupported schema_version")
    if raw.get("fixture_id") != "v4-ch11-synthetic-gradient-v1":
        raise ComparisonInputError("fixture_id does not match this chapter")
    if raw.get("label_source") != "synthetic_fixture":
        raise ComparisonInputError("fixture must remain labeled synthetic_fixture")

    x = raw.get("x")
    y = raw.get("y")
    if not isinstance(x, list) or not isinstance(y, list) or len(x) != len(y) or len(x) < 2:
        raise ComparisonInputError("x and y must be equal-length lists with at least two values")
    for index, value in enumerate(x):
        _finite_number(value, f"x[{index}]")
    for index, value in enumerate(y):
        _finite_number(value, f"y[{index}]")

    parameters = raw.get("initial_parameters")
    if not isinstance(parameters, dict):
        raise ComparisonInputError("initial_parameters must be an object")
    for name in ("weight", "bias"):
        _finite_number(parameters.get(name), f"initial_parameters.{name}")

    tolerance = _finite_number(raw.get("absolute_tolerance"), "absolute_tolerance")
    if not 0 < tolerance <= 0.01:
        raise ComparisonInputError("absolute_tolerance must be greater than 0 and at most 0.01")

    metadata = raw.get("metadata")
    if not isinstance(metadata, dict) or any(metadata.get(key) is not False for key in METADATA_KEYS):
        raise ComparisonInputError("fixture metadata must explicitly disclaim real data, models, training, GPU and benchmarks")
    return raw


def load_fixture(path: Path = DEFAULT_FIXTURE) -> tuple[dict[str, Any], bytes]:
    try:
        fixture_bytes = path.read_bytes()
    except OSError as error:
        raise ComparisonInputError(f"cannot read fixture: {error}") from error
    try:
        fixture = json.loads(fixture_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ComparisonInputError(f"cannot parse fixture JSON: {error}") from error
    return validate_fixture(fixture), fixture_bytes


def reference_result(fixture: dict[str, Any]) -> dict[str, float]:
    """Evaluate MSE and its closed-form gradients without a tensor library."""
    validate_fixture(fixture)
    x = [float(value) for value in fixture["x"]]
    y = [float(value) for value in fixture["y"]]
    weight = float(fixture["initial_parameters"]["weight"])
    bias = float(fixture["initial_parameters"]["bias"])
    residuals = [weight * xv + bias - yv for xv, yv in zip(x, y)]
    count = len(x)
    loss = sum(error * error for error in residuals) / count
    gradient_weight = 2.0 * sum(error * xv for error, xv in zip(residuals, x)) / count
    gradient_bias = 2.0 * sum(residuals) / count
    return {
        "loss": loss,
        "gradient_weight": gradient_weight,
        "gradient_bias": gradient_bias,
    }


def _as_float(value: Any) -> float:
    if hasattr(value, "item"):
        value = value.item()
    result = float(value)
    if not math.isfinite(result):
        raise RuntimeError("framework returned a non-finite scalar")
    return result


def _torch_result(fixture: dict[str, Any]) -> tuple[dict[str, float], str]:
    torch = importlib.import_module("torch")
    device = torch.device("cpu")
    x = torch.tensor(fixture["x"], dtype=torch.float32, device=device)
    y = torch.tensor(fixture["y"], dtype=torch.float32, device=device)
    weight = torch.tensor(float(fixture["initial_parameters"]["weight"]), dtype=torch.float32, device=device, requires_grad=True)
    bias = torch.tensor(float(fixture["initial_parameters"]["bias"]), dtype=torch.float32, device=device, requires_grad=True)
    loss = torch.mean((weight * x + bias - y) ** 2)
    loss.backward()
    return (
        {
            "loss": _as_float(loss),
            "gradient_weight": _as_float(weight.grad),
            "gradient_bias": _as_float(bias.grad),
        },
        str(getattr(torch, "__version__", "unknown")),
    )


def _jax_result(fixture: dict[str, Any]) -> tuple[dict[str, float], str]:
    jax = importlib.import_module("jax")
    jnp = importlib.import_module("jax.numpy")
    cpu_devices = jax.devices("cpu")
    if not cpu_devices:
        raise RuntimeError("JAX reports no CPU device")
    device = cpu_devices[0]
    x = jax.device_put(jnp.asarray(fixture["x"], dtype=jnp.float32), device)
    y = jax.device_put(jnp.asarray(fixture["y"], dtype=jnp.float32), device)
    initial = fixture["initial_parameters"]

    def objective(parameters: tuple[Any, Any]) -> Any:
        weight, bias = parameters
        return jnp.mean((weight * x + bias - y) ** 2)

    parameters = (
        jax.device_put(jnp.asarray(float(initial["weight"]), dtype=jnp.float32), device),
        jax.device_put(jnp.asarray(float(initial["bias"]), dtype=jnp.float32), device),
    )
    loss, gradients = jax.value_and_grad(objective)(parameters)
    return (
        {
            "loss": _as_float(loss),
            "gradient_weight": _as_float(gradients[0]),
            "gradient_bias": _as_float(gradients[1]),
        },
        str(getattr(jax, "__version__", "unknown")),
    )


def _tensorflow_result(fixture: dict[str, Any]) -> tuple[dict[str, float], str]:
    tf = importlib.import_module("tensorflow")
    initial = fixture["initial_parameters"]
    with tf.device("/CPU:0"):
        x = tf.constant(fixture["x"], dtype=tf.float32)
        y = tf.constant(fixture["y"], dtype=tf.float32)
        weight = tf.Variable(float(initial["weight"]), dtype=tf.float32)
        bias = tf.Variable(float(initial["bias"]), dtype=tf.float32)
        with tf.GradientTape() as tape:
            loss = tf.reduce_mean(tf.square(weight * x + bias - y))
        gradient_weight, gradient_bias = tape.gradient(loss, [weight, bias])
    if gradient_weight is None or gradient_bias is None:
        raise RuntimeError("GradientTape did not return both gradients")
    return (
        {
            "loss": _as_float(loss),
            "gradient_weight": _as_float(gradient_weight),
            "gradient_bias": _as_float(gradient_bias),
        },
        str(getattr(tf, "__version__", "unknown")),
    )


_RUNNERS = {
    "torch": _torch_result,
    "jax": _jax_result,
    "tensorflow": _tensorflow_result,
}


def run_backend(name: str, fixture: dict[str, Any]) -> dict[str, Any]:
    if name not in _RUNNERS:
        raise ComparisonInputError(f"unknown backend: {name}")
    try:
        observed, version = _RUNNERS[name](fixture)
    except ModuleNotFoundError as error:
        missing_root = (error.name or "").split(".", maxsplit=1)[0]
        if missing_root == name:
            return {"backend": name, "status": "not_installed"}
        return {"backend": name, "status": "import_error", "error_type": type(error).__name__}
    except Exception as error:
        return {"backend": name, "status": "import_error", "error_type": type(error).__name__}

    expected = reference_result(fixture)
    tolerance = float(fixture["absolute_tolerance"])
    differences = {
        key: abs(observed[key] - expected[key])
        for key in expected
    }
    passed = all(math.isfinite(observed[key]) and differences[key] <= tolerance for key in expected)
    return {
        "backend": name,
        "status": "passed" if passed else "mismatch",
        "version": version,
        "device": "cpu",
        "observed": observed,
        "absolute_difference_from_reference": differences,
        "tolerance": tolerance,
    }


def build_report(fixture: dict[str, Any], fixture_bytes: bytes, requested_backend: str = "all") -> dict[str, Any]:
    validate_fixture(fixture)
    if requested_backend not in ("reference", "all", *BACKENDS):
        raise ComparisonInputError(f"unknown backend: {requested_backend}")
    expected = reference_result(fixture)
    selected = BACKENDS if requested_backend == "all" else (() if requested_backend == "reference" else (requested_backend,))
    backend_results = {name: run_backend(name, fixture) for name in selected}
    passed = [name for name, row in backend_results.items() if row["status"] == "passed"]
    skipped = [name for name, row in backend_results.items() if row["status"] == "not_installed"]
    failed = [name for name, row in backend_results.items() if row["status"] not in {"passed", "not_installed"}]
    if failed:
        status = "failed"
    elif skipped and passed:
        status = "passed_with_skips"
    elif skipped or requested_backend == "reference":
        status = "reference_only"
    else:
        status = "passed"
    return {
        "schema_version": 1,
        "fixture_id": fixture["fixture_id"],
        "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "requested_backend": requested_backend,
        "python_version": ".".join(map(str, sys.version_info[:3])),
        "platform": f"{platform.system()} {platform.machine()}",
        "reference": expected,
        "framework_results": backend_results,
        "summary": {
            "status": status,
            "passed": passed,
            "skipped_not_installed": skipped,
            "failed": failed,
        },
        "scope": {
            "real_dataset_loaded": False,
            "pretrained_model_loaded": False,
            "training_performed": False,
            "gpu_used": False,
            "benchmark_performed": False,
            "network_access_performed": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare MSE gradients using optional CPU framework adapters")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--backend", choices=("reference", "all", *BACKENDS), default="all")
    parser.add_argument("--output", type=Path, help="write JSON to a file instead of stdout")
    args = parser.parse_args(argv)
    try:
        fixture, fixture_bytes = load_fixture(args.fixture)
        report = build_report(fixture, fixture_bytes, args.backend)
    except ComparisonInputError as error:
        print(f"input error: {error}", file=sys.stderr)
        return 2

    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote comparison report: {args.output}")
    else:
        sys.stdout.write(rendered)

    if report["summary"]["failed"]:
        return 1
    if args.backend not in {"all", "reference"} and report["framework_results"][args.backend]["status"] == "not_installed":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
