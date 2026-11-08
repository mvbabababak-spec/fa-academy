# پاسخ‌نامهٔ مستقل فصل ۵۹ — CUDA، ROCm، Triton و مقیاس‌پذیری

این پاسخ‌نامه مستقل از متن فصل نوشته شده است. پاسخ‌ها نمونهٔ استدلال‌اند؛ نسخهٔ دقیق PyTorch، backend، مدل و scheduler می‌توانند جزئیات اجرایی را عوض کنند.

## ۱. در یک آموزش دوگرهی با ۸ GPU در هر گره، چرا `LOCAL_RANK=3` را نباید به‌عنوان شناسهٔ سراسری فایل checkpoint به کار برد، و چه متغیری جای آن را می‌گیرد؟

`LOCAL_RANK` فقط شمارهٔ worker در node فعلی است. در هر دو node می‌تواند مقدار ۳ داشته باشد؛ بنابراین اگر فایل‌ها را مثلاً با نام `checkpoint-3.pt` بنویسیم، دو worker می‌توانند مسیر یکسانی را overwrite کنند. شناسهٔ worker در کل process group، `RANK` است؛ در یک اجرای ثابت، مقادیر global rank از ۰ تا `WORLD_SIZE-1` متمایزند. برای نام‌گذاری shardهای checkpoint در یک run ثابت می‌توان از `RANK` استفاده کرد، یا بهتر از آن API/checkpoint format توزیع‌شده‌ای را به‌کار برد که topology و shard metadata را خودش ثبت کند.

یک نکتهٔ مهم: در اجرای elastic، rankها میان restartها تضمین‌شده ثابت نمی‌مانند؛ پس `RANK` نیز شناسهٔ دائمی دستگاه یا کلید پایدارِ بین runها نیست. سیاست نوشتن باید checkpoint را به شناسهٔ run، topology و metadata مناسب متصل کند و معمولاً فقط writerهای تعیین‌شده اجازهٔ نوشتن فایل سراسری دارند. برای log یک‌بار در هر process group معمولاً rank صفر را انتخاب می‌کنند، نه `LOCAL_RANK==0` در هر node.

## ۲. چه شواهدی از `torch` باید کنار `torch.cuda.is_available()` ثبت شوند تا یک buildِ ROCm با CUDA اشتباه نشود؟

حداقل `torch.__version__`, `torch.version.cuda`, `torch.version.hip`, مقدار `torch.cuda.is_available()`, تعداد دستگاه‌ها و نام deviceها را ثبت می‌کنم. در build معمول ROCm، namespace پایتونی `torch.cuda` به‌عمد باقی می‌ماند؛ بنابراین `is_available()` می‌تواند `True` باشد، درحالی‌که `torch.version.hip` مقدار دارد و `torch.version.cuda` برابر `None` است. در build NVIDIA، معمولاً برعکس: مقدار CUDA موجود است و HIP خالی است. این metadata را کنار OS/kernel، PyTorch wheel/index، نسخهٔ driver و خروجی `python -m torch.utils.collect_env` قرار می‌دهم.

بعد از شناسایی build، فقط یک عملیات واقعی روی دستگاه اجرا می‌کنم: allocation و محاسبهٔ tensor، انتقال نتیجه به CPU، مقایسه با مرجع و synchronization. این smoke test دسترسی یک مسیر را نشان می‌دهد، نه پشتیبانی همهٔ operatorها یا کارایی؛ برای Triton، NCCL/RCCL و آموزش چند GPU باید آزمون جدا داشت.

## ۳. اگر مدل روی هر GPU جا می‌شود ولی throughput در دو node افت دارد، چرا اضافه‌کردن ZeRO-3 یا TP بدون تشخیص گلوگاه تصمیم زودهنگام است؟

چون مشاهدهٔ «کندشدن با دو node» به‌تنهایی نشان نمی‌دهد کمبود حافظه عامل محدودکننده است. ZeRO-3 پارامترها را هم shard می‌کند، اما برای forward/backward آن‌ها را gather می‌کند و reduce-scatter/ارتباط بیشتری دارد. اگر network یا collectiveها کند باشند، ممکن است همان bottleneck را تشدید کند. TP لایه را میان deviceها تقسیم می‌کند و برای بسیاری از معماری‌ها در هر لایه رفت‌وبرگشت پرتکرار می‌سازد؛ عبور بی‌نیاز آن از inter-node fabric می‌تواند هزینه را بالا ببرد. اگر مدل از پیش در هر GPU جا می‌شود، این هزینه ممکن است بدون فایدهٔ حافظه‌ای اضافه شود.

ابتدا warm-up و زمان‌گیری همگام‌شده انجام می‌دهم و زمان compute، collective، بارگیری داده، checkpoint و انتظار workerها را جدا می‌بینم. سپس network/interface، تعداد microbatch، batch مؤثر، sampler، placement و اختلاف سرعت میان rankها را بررسی می‌کنم. ZeRO-3 یا TP را فقط وقتی آزمایش می‌کنم که محدودیت state/layer و مسیر ارتباط مشخص باشد؛ برای خط مبنا DDP را نیز نگه می‌دارم. هر نتیجه فقط برای workload، نسخه، topology و تعداد تکرار ثبت‌شده معتبر است.

## ۴. یک تیم می‌خواهد kernelِ Triton را هم روی NVIDIA و هم AMD اجرا کند. چه چیزهایی باید روی هر backend دوباره آزموده شوند، حتی اگر منبع kernel مشترک باشد؟

روی هر backend باید buildهای PyTorch و Triton، driver/runtime، معماری device و toolchain دقیق ثبت شوند. سپس correctness را در shapeهای معمول و مرزی می‌سنجم: اندازه‌های ناتراز با tile، mask انتهایی، stride/layout، dtype و precision، مقادیر NaN/Inf و رفتار synchronization. خروجی kernel را با مرجع PyTorch یا CPU مقایسه می‌کنم و آزمون concurrency/race و خطاهای JIT را هم جدا می‌گیرم. نسخهٔ binary/کامپایل‌شده یا cache یک backend را دلیل اجرای درست backend دیگر فرض نمی‌کنم.

حتی با correctness یکسان، performance را باید جدا و روی GPU واقعی اندازه گرفت: warm-up، synchronization، چند تکرار، shape نماینده و گزارش ابزار profiler. یک kernel مشترک ممکن است برای backend دیگر مسیر lowering، instruction، memory layout یا throughput متفاوت داشته باشد. «منبع مشترک» ادعای portability است، نه اثبات دقت، سازگاری همهٔ معماری‌ها یا برابری سرعت.

## ۵. در layout فرضی `DP=2, TP=2, PP=2, CP=1` چند worker لازم است، و چرا این محاسبه را نمی‌توان بی‌قید به MoE/EP تعمیم داد؟

برای layout سادهٔ dense که اندازهٔ هر محور گروه مستقل است، تعداد workerها برابر است با `2 × 2 × 2 × 1 = 8`. این فقط حساب یک mesh فرضی است؛ نه نتیجهٔ تشخیص GPU موجود و نه config اجرایی یک model خاص.

در MoE، EP واحدهای expert را تقسیم می‌کند و برای توزیع توکن‌ها به token dispatch و گروه‌های ارتباطی دیگری نیاز است. گاهی parallelismهای expert، tensor، data و pipeline با قیدهای معماری/نسخه در هم ترکیب می‌شوند؛ بعضی ابزارها axisهای مدل را جداگانه تعریف یا گروه‌های hierarchical ایجاد می‌کنند. پس نمی‌توان بدون قرارداد دقیق framework، اندازهٔ EP را به حاصل‌ضرب dense اضافه کرد یا فرض کرد همهٔ ابعاد مستقل‌اند. باید config و مستندات نسخهٔ Megatron/DeepSpeed/FSDP و topology واقعی را بررسی کرد.
