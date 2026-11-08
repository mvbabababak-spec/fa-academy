# پاسخ‌نامهٔ مستقل — فصل ۵۷: Python، PyTorch، JAX و TensorFlow

این پاسخ‌ها نمونه‌اند، نه انتخاب اجباری. هر تصمیم را با workload، نسخه و سیستم هدف خود مستند کنید. نصب موفق یا smoke test کوچک به معنی benchmark، کیفیت مدل یا آمادگی production نیست.

## ۱. مدل موجود در PyTorch

سه سؤال مفید:

1. آیا همان نسخهٔ checkpoint، tokenizer/ورودی، operatorهای لازم و کتابخانه‌های جانبی واقعاً در PyTorch پشتیبانی می‌شوند؟
2. آیا هدف پژوهش/آموزش/inference است، و deployment به export یا سرو از چه نوع نیاز دارد؟
3. روی سیستم‌عامل، نسخهٔ Python و accelerator مقصد، wheel رسمی و driver/runtime سازگار وجود دارد؟

اگر مدل فقط PyTorch را پشتیبانی کند و سه سؤال با شواهد پاسخ بگیرند، PyTorch گزینهٔ شروع منطقی است؛ اما پیش از تعیین deployment، مقایسهٔ نیازهای محصول و آزمون workload واقعی هنوز لازم است. مثال رسمی یا فرمت checkpoint به‌تنهایی عملکرد یا سازگاری آینده را اثبات نمی‌کند.

## ۲. محاسبات تابعی و JIT

در JAX ابتدا `jax.grad` یا `jax.value_and_grad` برای مشتق، `jax.vmap` برای بردارسازی و `jax.jit` برای trace/کامپایل تابع را روی CPU بررسی کنید. عملیات باید تا حد امکان با JAX array و تابع‌های خالص نوشته شوند؛ آثار جانبی Python یا تبدیل آرایهٔ traced به NumPy در زمان trace ممکن است ناسازگار باشد. سپس ثبت کنید: Python/OS/architecture، device wheel، driver/runtime، شکل‌های ورودی، compile/warm-up و test روی hardware واقعی. مثال آموزشی سرعت یا پشتیبانی همهٔ GPUها را ثابت نمی‌کند.

## ۳. Keras/TensorFlow موجود

پیش از مهاجرت یا تثبیت، دست‌کم دو آزمون لازم است:

- همان مدل و ورودی، معیار correctness/کیفیت و artifact نهایی را روی مسیر موجود و candidate اجرا کنید؛ `eager` تنها نمایندهٔ `tf.function`/Keras deployment نیست.
- مسیر هدف (OS، device، Python، dependencies، export/serving) و ابزارهای نگه‌داری را روی نسخهٔ دقیق بررسی کنید؛ نسخهٔ Python/wheel و GPU باید از جدول رسمی همان سیستم باشد.

یک مثال eager فقط API/گرادیان کوچک را نشان می‌دهد. اگر Keras و TensorFlow زیرساخت فعلی‌اند، هزینهٔ مهاجرت و توان تیم را هم کنار سرعت/دقت اندازه‌گیری کنید.

## ۴. چرا Python 3.15.2 نه؟ چه نسخهٔ مشترکی؟

Python 3.15.2 تازه‌ترین CPython پایدار در snapshot 2026-11-06 است؛ اما TensorFlow 2.21 مستندات Python و wheelهایش را به بازه/پلتفرم محدود می‌کند و همان صفحه در متن عمومی و جدول wheelها کاملاً هم‌خوان نیست. PyTorch 2.15 و JAX نیز به‌تنهایی تضمین نمی‌کنند که TensorFlow، افزونه‌ها و همهٔ deviceها برای همان ABI wheel داشته باشند. برای مطالعهٔ مقایسه‌ای این فصل Python 3.12 انتخاب شده، چون در ماتریس/متن مستند TensorFlow و دیگر گزینه‌ها مشترک است. برای محصول، اول ماتریس هر wheel و هر dependency را کنترل کنید؛ سپس نسخهٔ pinشده را انتخاب کنید.

## ۵. `all` دو skip و یک pass دارد

این اجرا نشان می‌دهد:

- fixture و محاسبهٔ مرجع محلی اجرا شده‌اند؛
- adapter چارچوبی که pass گزارش کرده، در همان interpreter و CPU نتیجه‌ای در tolerance fixture داده است؛
- دو package در آن محیط پیدا نشده‌اند، پس هیچ نتیجه‌ای دربارهٔ API/runtime آن‌ها نداریم.

این اجرا نه ثابت می‌کند سه چارچوب نصب‌اند، نه برابری عملکرد/کیفیت، GPU readiness، قابلیت تعمیم یا سازگاری با مدل بزرگ. برای دو چارچوب skipped، هرکدام باید در venv جدا نصب و adapter همان نسخه اجرا شود؛ سپس workload واقعی و benchmark همسان لازم است.

## ۶. `torch.cuda.is_available()` نادرست/False است

بررسی به ترتیب:

1. چاپ `sys.executable`, `torch.__version__`, `torch.version.cuda` و فرمان/index نصب؛ ممکن است CPU wheel نصب شده یا Python دیگری در حال اجرا باشد.
2. از host با `nvidia-smi` مدل GPU و driver را بخوانید؛ نسخه/driver و compute wheel را با راهنمای همان release تطبیق دهید.
3. visibility دستگاه، container passthrough، driver/runtime/library path و نتیجهٔ یک tensor کوچک روی device را جداگانه بررسی کنید.

`False` به‌تنهایی خرابی GPU را ثابت نمی‌کند؛ می‌تواند محیط، wheel یا driver را نشان دهد. تغییر تصادفی PATH/`LD_LIBRARY_PATH` یا نصب چند CUDA toolkit راه تشخیص معتبر نیست. اگر CPU wheel عمدی است، خروجی False طبیعی است.

## ۷. آیا نتیجهٔ gradient toy قابل تعمیم است؟

خیر. fixture فقط قرارداد سه مقدار و tolerance را روی دو مشاهده آزمایش می‌کند. آن هیچ dataloader، optimizer state، مدل عمیق، dtype کم‌دقت، kernel اختصاصی، multi-GPU، compile warm-up، حافظهٔ اوج، سرعت یا معیار کیفیت ندارد. در workload واقعی باید ورودی مجاز، seed/split، مدل و نسخه، معیار پذیرش، warm-up، synchronization و hardware/driver را ثابت و ثبت کنید.
