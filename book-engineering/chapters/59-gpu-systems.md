# جلد چهارم، فصل ۱۳ — CUDA، ROCm، Triton و مقیاس‌پذیری

> **جایگاه در نقشه:** فصل محلی ۱۳ از ۱۵ جلد چهارم؛ فصل سراسری ۵۹. فصل ۵۷ چارچوب‌های Python و tensor را مقایسه کرد و فصل ۵۸ زنجیرهٔ داده تا batch و یک گام آموزش را ساخت. این فصل از مرز «کد مدل» عبور می‌کند: درایور، runtime، kernel و ارتباط توزیع‌شده را از هم جدا می‌کنیم. فصل ۶۰ به ردیابی آزمایش و MLOps می‌پردازد؛ فصل ۶۱ به سرو و بهینه‌سازی استنتاج. تخمین حافظه و هزینه در این فصل تکرار نمی‌شود و به‌ترتیب به فصل‌های ۵۴ و ۵۶ واگذار است.

## ۱. پرسش را از «چند GPU؟» به «کدام گلوگاه؟» تغییر دهید

عبارت «مدل را روی GPU اجرا می‌کنیم» چند قرارداد متفاوت را در یک جمله پنهان می‌کند: آیا سیستم‌عامل و درایور دستگاه را می‌بینند؟ آیا build کتابخانه برای همان backend ساخته شده؟ آیا runtime و کتابخانهٔ ارتباطی بار می‌شوند؟ آیا kernel برای همین معماری قابل‌کامپایل است؟ و آیا فرایندهای چندگانه در شبکه و توپولوژی واقعی به یکدیگر می‌رسند؟ پاسخ مثبت به یکی، پاسخ مثبت به همهٔ آن‌ها نیست.

هدف این فصل شناخت مرزهای CUDA، ROCm/HIP و Triton، و انتخاب آگاهانه میان DDP، FSDP، DeepSpeed ZeRO و محورهای موازی‌سازی Megatron-LM/Core است. پیش از تغییر الگوریتم آموزش، باید لایهٔ شکست را پیدا کرد؛ افزودن worker یا تنظیمات بیشتر به خطای سازگاری، ارتباط یا مسیر داده پاسخ نمی‌دهد.

## ۲. نقشهٔ لایه‌ها: مدل، framework، backend و سخت‌افزار

برای عیب‌یابی، هر گزارش را در لایهٔ درست قرار دهید. **CUDA** پشتهٔ NVIDIA برای برنامه‌نویسی و اجرای محاسبات GPU است؛ **ROCm** پشتهٔ نرم‌افزاری AMD است و **HIP** API/مدل برنامه‌نویسی آن است. **PyTorch** می‌تواند با build متفاوت به یکی از این پشته‌ها متصل شود. **NCCL** و **RCCL** کتابخانه‌های collectives برای ارتباط چند GPU هستند؛ آن‌ها نه launcher هستند و نه الگوریتم آموزش. **Triton** زبان و compiler برای نوشتن kernelهای سفارشی است، نه نام دیگری برای کل runtime.

![شکل ۴-۱۳-۱. پشتهٔ اجرایی و نقشهٔ توزیع: PyTorch از build متناسب با CUDA/NCCL یا ROCm/HIP/RCCL به runtime و driver میزبان و سپس GPU می‌رسد؛ Triton مسیر ساخت kernel سفارشی را به این پشته وصل می‌کند. در بخش موازی‌سازی، DP batch را میان replicaها تقسیم می‌کند، TP لایه، PP عمق، CP توالی و EP کارشناس‌های MoE را بخش‌بندی می‌کند. شکل مفهومی است؛ سخت‌افزار یا benchmark اندازه‌گیری‌شده‌ای را نشان نمی‌دهد.](book-engineering/diagrams/v4-ch13-gpu-systems.svg)

این جداسازی یک قاعدهٔ عملی می‌دهد: پیام خطای `import torch`، پیام «device unavailable»، خطای collective و خطای کامپایل Triton را یک مسئله تلقی نکنید. خروجیِ گزارش محیط، نسخهٔ wheel، درایور، backend و فرمان launch را کنار هم ثبت کنید؛ فقط عبارت «CUDA 12» یا «ROCm 10» برای بازتولید کافی نیست.

## ۳. CUDA: toolkit، runtime و driver نقش یکسان ندارند

در مسیر NVIDIA دست‌کم این موارد را از هم جدا کنید:

- **GPU و معماری:** مدل دستگاه و قابلیت‌هایی که واقعاً در آن پیاده‌سازی شده‌اند.
- **Driver میزبان:** مؤلفه‌ای که سیستم‌عامل با GPU و برنامه‌های user-space را به هم وصل می‌کند.
- **CUDA Toolkit:** ابزارهای توسعه مانند `nvcc` و کتابخانه‌های لازم برای ساخت بعضی افزونه‌ها یا برنامه‌ها.
- **Runtime وابسته به برنامه:** نسخه‌ای که build مشخص PyTorch یا افزونهٔ آن انتظار دارد.
- **NCCL:** مسیر collectives چند GPU/چند node، جدا از launch و جدا از خود مدل.

درایورهای NVIDIA سازوکارهای سازگاری مستندشده دارند، اما سازگاری minor-version و forward-compatibility محدودیت و پیش‌شرط دارند؛ وجود یک toolkit تازه، درایور قدیمی را خودبه‌خود مناسب نمی‌کند. از سوی دیگر، wheel پیش‌ساختهٔ PyTorch الزاماً به معنی نیاز به نصب کامل toolkit برای هر اجرای عادی نیست؛ ساخت افزونهٔ CUDA یا kernel ممکن است به ابزار توسعه نیاز داشته باشد. برای ترکیب دقیق، راهنمای نصب PyTorch و مستندات همان نسخهٔ CUDA را بخوانید.

فرمان `nvcc --version` نسخهٔ compiler/toolkit قابل‌دسترسی در `PATH` را گزارش می‌کند؛ `torch.version.cuda` مشخصهٔ build نصب‌شدهٔ PyTorch است. این دو را برابر فرض نکنید و صرفاً از نام wheel نتیجه نگیرید که driver، افزونهٔ بومی یا NCCL هم درست‌اند. راهنمای رسمی CUDA سازگاری برنامه و toolkit را به driver و محدودیت‌های هر مسیر ارتقا پیوند می‌دهد.

## ۴. ROCm/HIP: API پایتونی ممکن است واژهٔ `cuda` را نشان دهد

در PyTorch مبتنی بر ROCm، namespace عمومی دستگاه در Python همچنان `torch.cuda` و رشتهٔ دستگاه همچنان `cuda:0` است. بنابراین `torch.cuda.is_available()` به‌تنهایی نمی‌گوید GPU از NVIDIA است. build را با `torch.version.hip` و `torch.version.cuda` بخوانید: مقدار HIP و نبودن build CUDA معمولاً نشان می‌دهد wheel به ROCm ساخته شده؛ سپس مدل GPU و نام build را نیز ثبت کنید.

ROCm یک فایل Python تنها نیست. نسخهٔ ROCm، GPU و معماری `gfx`, توزیع و kernel لینوکس، driver/firmware و نسخهٔ framework باید در ماتریس پشتیبانی‌شده کنار هم باشند. PyTorch می‌تواند در یک build از کتابخانه‌های متناظر AMD و RCCL استفاده کند، اما دسترس‌پذیری یک API در PyTorch تضمین نمی‌کند که هر افزونهٔ CUDA، kernel سفارشی یا نسخهٔ DeepSpeed/Megatron روی AMD نیز کار کند. این‌ها را برای هر ابزار و عملیات جداگانه بیازمایید.

**قاعده:** برای تشخیص NVIDIA/AMD فقط نام متدهای Python را نخوانید؛ build، runtime گزارش‌شده، driver و دستگاه را با هم بخوانید. روی ROCm هم `torch.cuda` می‌تواند API درست باشد.

## ۵. ماتریس پشتیبانی را به‌صورت یک tuple بخوانید

پیش از نصب، یک ترکیب کامل را بررسی کنید؛ نه فقط «PyTorch از GPU پشتیبانی می‌کند». حداقل این tuple را بنویسید:

| مؤلفه | پرسش قابل‌آزمون |
| --- | --- |
| OS، نسخه و kernel | آیا همین انتشار برای این توزیع/نسخه مستند شده است؟ |
| GPU و معماری | آیا شناسهٔ دقیق GPU یا معماری آن در جدول آمده است؟ |
| Driver و runtime | آیا driver میزبان با runtime انتخابی سازگار است؟ |
| PyTorch و Python | آیا wheel همان نسخه برای backend، OS و Python موجود است؟ |
| افزونه و ارتباط | آیا Triton، DeepSpeed، FSDP و کتابخانهٔ collective همین ترکیب را پوشش می‌دهند؟ |
| launcher و شبکه | آیا rankها، پورت rendezvous و interfaceهای شبکه در محیط واقعی قابل‌دسترسی‌اند؟ |

**snapshot اسنادی این فصل، بررسی‌شده در ۷ نوامبر ۲۰۲۶:** راهنمای CUDA که در زمان بررسی برچسب Release 620 دارد، مدل‌های minor-version و forward compatibility را شرح می‌دهد؛ ماتریس ROCm 10.1.0 ترکیب‌های GPU/سیستم‌عامل/driver و framework را نسخه‌بندی می‌کند؛ اسناد PyTorch 2.15.0 مسیر `torchrun` و `fully_shard` را توصیف می‌کنند؛ Triton 3.9.0 در ۲۷ اکتبر ۲۰۲۶ منتشر شده؛ اسناد DeepSpeed در زمان بازبینی نسخهٔ 0.19.9 و مستندات Megatron Core نسخهٔ 0.20.0 را نشان می‌دهند. این‌ها snapshotهای مستندات‌اند، نه ادعای آزمون همهٔ نسخه‌ها در یک محیط سازگار.

جدول‌های vendor با انتشارهای تازه تغییر می‌کنند. تاریخ دسترسی را کنار شمارهٔ نسخه بنویسید و روز اجرا همان selector/matrix را دوباره بررسی کنید. دستور نصب یک ماشین یا wheel قدیمی را به دستور عمومی برای همهٔ GPUها تبدیل نکنید.

## ۶. Preflight: ابتدا build را ثبت کنید، سپس یک عملیات واقعی را بیازمایید

در محیط موردنظر، این گزارش پایه را ذخیره کنید:

```bash
python -m torch.utils.collect_env
python -c "import torch; print('torch=', torch.__version__); print('cuda_build=', torch.version.cuda); print('hip_build=', torch.version.hip); print('device_api_available=', torch.cuda.is_available()); print('device_count=', torch.cuda.device_count())"
```

در ROCm هم نام API در خط چهارم `device_api_available` عمداً خنثی است. اگر build و دستگاه در دسترس‌اند، آزمون بعدی باید یک tensor allocation و یک عملیات واقعی روی همان دستگاه انجام دهد، خروجی را با مرجع CPU بسنجد و در پایان synchronize کند. پس از آن، collective دوفرایندی و سپس مدل/عملیات نماینده را با همان launcher اجرا کنید. صرفاً چاپ `True` از `is_available()`، سازگاری تمام operators یا مقیاس‌پذیری را اثبات نمی‌کند.

پروژهٔ این فصل `gpu_systems_demo.py --mode preflight` را به همین گزارش حداقلی تبدیل می‌کند؛ آن را روی CPU هم می‌توان اجرا کرد. در این محیط بررسی‌شده، build فقط CPU است، `torch.cuda.is_available()` برابر `False` است و Gloo موجود است. پس هیچ نتیجهٔ CUDA یا ROCm از این پیش‌آزمون استنباط نمی‌شود.

## ۷. Triton: kernel سفارشی بنویسید؛ runtime را با زبان اشتباه نگیرید

Triton زبان/کامپایلری tile-oriented برای نوشتن kernelهای محاسباتی است. کاربردش زمانی معنی دارد که trace و profiler نشان دهند kernelهای موجود یا رفت‌وبرگشت‌های متعدد حافظه/launch گلوگاه‌اند و یک kernel سفارشی می‌تواند محاسبه را fuse کند. این ابزار جای PyTorch، CUDA یا ROCm را نمی‌گیرد و با **Triton Inference Server** یکی نیست؛ آن نام به سامانهٔ سرو مدل مربوط است و خارج از مرز این فصل است.

مخزن رسمی Triton، Linux و backendهای NVIDIA و AMD را فهرست می‌کند، اما شرط‌های backend، معماری و toolchain را نیز باید برای همان release کنترل کرد. «یک منبع Python» به معنی یکسان‌بودن binary، دقت عددی، قابلیت‌های سخت‌افزاری یا کارایی در CUDA و HIP نیست. build باید با PyTorch/ROCm یا CUDA انتخاب‌شده جور باشد؛ نصب دلخواه wheel جدا ممکن است زنجیرهٔ سازگاری را برهم بزند.

پیش از بهینه‌سازی، kernel را در شکل‌های کوچک و مرزی با مرجع ساده مقایسه کنید: اندازه‌های غیرمضرب tile، mask انتهایی، dtype، stride و مقادیر NaN/Inf را فراموش نکنید. سپس نسخهٔ Triton، GPU، driver، shape، warm-up، روش زمان‌گیری و خروجی correctness را ثبت کنید. پروژهٔ حاضر هیچ kernel Triton را اجرا یا benchmark نمی‌کند.

## ۸. `torchrun`: launcher فرایند می‌سازد؛ collective داده جابه‌جا می‌کند

در الگوی رایج، launcher برای هر worker یک فرایند Python راه می‌اندازد و هر فرایند همان برنامه را اجرا می‌کند. `torchrun` متغیرهایی مانند `RANK`, `LOCAL_RANK` و `WORLD_SIZE` را فراهم می‌کند؛ `RANK` شناسهٔ worker در کل گروه است، اما `LOCAL_RANK` فقط در همان node معنا دارد. از `LOCAL_RANK` برای نام‌گذاری یکتای checkpoint یا فایل مشترک استفاده نکنید. در اجراهای elastic، world size و rankها ممکن است پس از restart عوض شوند.

برای یک میزبان، `--standalone --nproc-per-node=2` می‌تواند دو worker بسازد؛ برای چند node باید rendezvous، شناسهٔ job، آدرس/پورت مشترک، node count، firewall، DNS و رابط شبکه را نیز درست تعیین کرد. `torchrun` جایگزین collective library نیست: launcher workerها را هماهنگ می‌کند، ولی `init_process_group` و backend انتخابی ارتباط میان آن‌ها را برقرار می‌کنند.

پروژهٔ پیوست فرمان دو-worker را روی CPU/Gloo واقعاً اجرا می‌کند. چون این محیط GPU ندارد، این آزمون فقط launch، متغیرهای rank و یک collective محلی را می‌آزماید؛ نه NCCL، RCCL، شبکهٔ چند node یا یک آموزش واقعی.

## ۹. NCCL، RCCL و Gloo: مسیر ارتباط با نوع دستگاه و build عوض می‌شود

**NCCL** کتابخانهٔ NVIDIA برای collectives و ارتباط point-to-point چند GPU است و topology و interconnect را در نظر می‌گیرد. **RCCL** متناظر AMD برای ارتباط چند GPU و چند node است. **Gloo** backend دیگری است که در این فصل برای آزمون CPU استفاده می‌شود. این کتابخانه‌ها خودشان model-parallel planner یا launcher نیستند؛ آن‌ها عملیات‌هایی مانند AllReduce، AllGather، ReduceScatter و AlltoAll را اجرا می‌کنند.

در DDP، معمولاً gradientها میان replicaها جمع می‌شوند؛ FSDP و ZeRO نیز all-gather و reduce-scatter بیشتری در مسیر وزن/گرادیان دارند؛ TP و EP می‌توانند برای هر لایه یا توزیع expert ارتباط ایجاد کنند. در نتیجه سرعت به تعداد GPU تنها وابسته نیست: placement processها، PCIe/NVLink یا xGMI، شبکهٔ بین nodeها، اندازهٔ پیام، overlap محاسبه و ارتباط و بارگذاری داده مهم‌اند.

برای بررسی خرابی collective، همهٔ rankها را با یک فرمان و محیط یکسان شروع کنید؛ backend، rank، world size، endpoint، interface و log هر worker را ثبت کنید. یک `barrier` یا متغیر محیطی تصادفی را بی‌هدف اضافه نکنید: اگر rankی پیش از collective خطا داده باشد، rankهای دیگر ممکن است همان‌جا منتظر بمانند.

## ۱۰. DDP: مدل تکرار می‌شود، batch میان replicaها تقسیم می‌شود

در DistributedDataParallel معمولی، هر worker یک نسخهٔ کامل از مدل دارد و بخشی از داده را پردازش می‌کند. در مسیر backward، gradientها میان replicaها هماهنگ می‌شوند. بنابراین DDP ابتدا «یک مدل بزرگ را به چند تکه تقسیم» نمی‌کند؛ آن مسئله را باید با sharding یا موازی‌سازی مدل بررسی کرد.

اگر batch محلی، تعداد worker و gradient accumulation را تغییر دهید، batch مؤثر و schedule آموزش هم تغییر می‌کنند. داده را با sampler توزیع‌شده طوری بخش کنید که هر rank سهم معنادار داشته باشد؛ seed، padding/drop-last و تعداد گام‌ها را در همهٔ workerها سازگار کنید. rank صفر می‌تواند مسئول log یا نوشتن فایل یکتا باشد، اما همهٔ rankها باید در ترتیب collectiveها و checkpointهای هماهنگ توافق داشته باشند.

از DDP شروع کنید اگر مدل و حالت‌های آن روی هر device جا می‌شوند و هدف، تقسیم batch است. آن را با `DataParallel` درون یک process یا با FSDP یکی نگیرید. مفهوم batch و تفکیک داده در فصل ۵۸ معرفی شد؛ اینجا مسئله، هماهنگی فرایندها و هزینهٔ ارتباط است.

## ۱۱. FSDP2: state مدل را در گروه داده shard کنید

PyTorch FSDP2 با `fully_shard` از پارامترهای shardشده استفاده می‌کند: وزن‌های لازم پیش از forward/backward جمع می‌شوند، سپس stateها دوباره shard/آزاد می‌شوند و gradientها reduce-scatter می‌شوند. API سطح بالا از `DeviceMesh` و گروه‌های ارتباطی استفاده می‌کند. اندازه و مرز هر گروه مهم است؛ در مدل transformer معمولاً ابتدا blockها و سپس root را به‌شکل bottom-up shard می‌کنند تا گروه‌ها و فرصت overlap روشن باشند.

این رفتار با DDP فرق دارد: FSDP برای کاهش نسخه‌های تکراریِ model state ارتباط بیشتری وارد مسیر اجرا می‌کند. `reshard_after_forward`, مرز moduleها، dtype، optimizer و checkpoint format روی حافظه، تعداد collectiveها و portability اثر می‌گذارند. عبارت «FSDP روشن شد» برای بازتولید کافی نیست؛ نسخهٔ PyTorch، mesh، مرزهای shard، precision policy و روش ذخیره/بارگذاری را ثبت کنید.

اسناد PyTorch در نسخهٔ 2.15.0 API FSDP2 را مستند می‌کنند؛ قطعه‌کدهای FSDP1 و FSDP2 را بی‌بررسی در یک پروژه مخلوط نکنید. این chapter محیط GPU در اختیار ندارد، بنابراین API را توضیح می‌دهد اما اجرای `fully_shard`، آموزش، load/save checkpoint یا سازگاری model-specific را ادعا نمی‌کند.

## ۱۲. DeepSpeed ZeRO: مرحله‌ها دقیقاً چه چیزی را partition می‌کنند؟

DeepSpeed ZeRO افزونگی state در data-parallel workers را مرحله‌به‌مرحله کم می‌کند:

| مرحله | stateهای shardشده | پیامد عملی |
| --- | --- | --- |
| ZeRO-1 | optimizer state | وزن و گرادیان هنوز مانند مرحلهٔ بدون shard تکثیر می‌شوند. |
| ZeRO-2 | optimizer state و gradient | انتقال gradient و مدیریت optimizer باید با stage سازگار باشد. |
| ZeRO-3 | optimizer state، gradient و parameter | پارامترهای موردنیاز باید هنگام forward/backward جمع و دوباره partition شوند. |

DeepSpeed می‌تواند در پیکربندی‌های مشخص state یا محاسبه را به CPU و در بعضی مسیرها به NVMe offload کند. این کار حافظهٔ GPU را با هزینهٔ انتقال داده، CPU، storage و تنظیمات بیشتر معاوضه می‌کند؛ «offload» راه‌حل رایگان یا تضمین سرعت نیست. نصب بعضی operatorها به build/JIT و compiler مناسب نیاز دارد. از راهنمای accelerator setup و مستندات نسخهٔ خود استفاده کنید و سازگاری operatorها را جدا بیازمایید؛ پشتیبانی عمومی accelerator abstraction دلیل کافی برای سازگار فرض‌کردن همهٔ kernelها نیست.

## ۱۳. FSDP یا ZeRO؟ «بهترین» را از نیاز و عملیات استخراج کنید

FSDP2 یک API بومی PyTorch برای شاردینگ ماژول و state است؛ DeepSpeed یک engine و پیکربندی ZeRO/offload فراهم می‌کند. FSDP2 با full sharding و ZeRO-3 از نظر هدف شبیه‌اند، اما پیاده‌سازی، API، optimizer lifecycle، checkpoint و افزونه‌های قابل‌استفاده‌شان یکسان نیست. انتخاب باید به قرارداد مدل، نوع optimizer، نیاز checkpoint/reshard، support matrix، topology، کدهای فعلی و تجربهٔ تیم وابسته باشد.

| نیاز غالب | گزینهٔ آغازین برای بررسی | هزینه‌ای که باید دوباره بسنجید |
| --- | --- | --- |
| مدل در هر GPU جا می‌شود و batch را می‌خواهید توزیع کنید | DDP | حافظهٔ مدل تکثیر است؛ ارتباط gradient را اندازه بگیرید. |
| PyTorch-native sharding و کنترل گروه‌های module لازم است | FSDP2 | API/mesh/checkpoint را در نسخهٔ ثابت و مدل واقعی بیازمایید. |
| ZeRO stageها، engine یا offload موجود در recipe مهم‌اند | DeepSpeed | build operator، driver، offload و checkpoint conversion را بسنجید. |
| لایه یا sequence خودش نیازمند تقسیم مدل است | Megatron TP/PP/CP | topology، schedule و communication گروه‌ها را مشخص کنید. |

از ترکیب چند روش تنها وقتی استفاده کنید که مشخص باشد هرکدام چه state یا بُعدی را مدیریت می‌کند. فعال‌کردن DDP، FSDP و ZeRO با هم بدون تعریف ownership گروه‌ها و checkpoint می‌تواند هزینه و پیچیدگی بسازد، نه ظرفیت رایگان.

## ۱۴. Megatron-LM/Core: موازی‌سازی را روی بُعد درست قرار دهید

Megatron-LM نمونه‌ها و loopهای آموزش مقیاس‌پذیر دارد؛ Megatron Core building blockهای composable و مسیرهای موازی‌سازی را ارائه می‌کند. مستندات جاری Megatron Core محورهایی چون DP، TP، PP، CP، EP و Megatron-FSDP را تفکیک می‌کنند. هر محور مسئلهٔ متفاوتی را تقسیم می‌کند:

| محور | چه چیزی تقسیم می‌شود؟ | معمولاً چه وقت بررسی می‌شود؟ |
| --- | --- | --- |
| Data Parallelism (DP) | نمونه‌ها/batch میان replicaها | مدل در هر worker جا می‌شود و می‌خواهید داده را موازی کنید. |
| Tensor Parallelism (TP) | محاسبه و وزن درون لایه | لایهٔ بزرگ به چند device نیاز دارد؛ ارتباط نزدیک و پرسرعت اهمیت دارد. |
| Pipeline Parallelism (PP) | عمق مدل میان stageها | مدل عمیق است؛ تعداد microbatch و pipeline bubble باید بررسی شود. |
| Context Parallelism (CP) | بخش‌های توالی/context | activationهای sequence بلند گلوگاه‌اند؛ ارتباط KV نیز اضافه می‌شود. |
| Expert Parallelism (EP) | expertهای مدل MoE | واقعاً از MoE استفاده می‌کنید؛ token dispatch و load balance مهم‌اند. |

این نام‌ها گزینه‌های independent برای checkbox زدن نیستند. TP و PP می‌توانند در یک mesh ترکیب شوند؛ CP برای هر معماری یکسان قابل‌فعال‌سازی نیست؛ EP فقط وقتی معنا دارد که لایهٔ MoE وجود داشته باشد. مستندات Megatron Core نسخه، معماری، operator و ترکیب‌های پشتیبانی‌شده را بررسی کنید. از آنجا که این پشته NVIDIA-focused است، پشتیبانی CUDA آن را به ROCm تعمیم ندهید؛ برای AMD ماتریس و backend مشخص همان branch را مطالبه کنید.

## ۱۵. حسابِ workerها و topology را از روی فرض بنویسید

برای یک layout سادهٔ dense با گروه‌های مستقل و یک worker در هر مختصات، رابطهٔ تعداد workerها چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" aria-label="در layout سادهٔ dense، world size برابر حاصل‌ضرب اندازه‌های DP، TP، PP و CP است">
  <mrow>
    <mi>world_size</mi><mo>=</mo><mi>DP</mi><mo>×</mo><mi>TP</mi><mo>×</mo><mi>PP</mi><mo>×</mo><mi>CP</mi>
  </mrow>
</math>

**متن جایگزین فرمول:** برای این layout سادهٔ dense، تعداد workerها برابر حاصل‌ضرب اندازه‌های DP، TP، PP و CP است؛ این رابطه EP و meshهای hybrid را مدل نمی‌کند.

فایل `sample_layout.json` فقط قرارداد همین حساب را برای fixture ساختگی کنترل می‌کند: `2 × 2 × 2 × 2 = 16`. این عدد GPU شمارش‌شده یا config اجرایی Megatron نیست. در MoE، EP/ETP، HSDP، multi-node و layoutهای واقعی گروه‌ها ممکن است در هم تنیده شوند و باید از config/version همان framework پیروی کرد.

علاوه بر حاصل‌ضرب، جای هر گروه را روی ماشین‌ها بنویسید. اگر TP درون یک node ارتباط پرتکرار دارد، آن را بی‌دلیل از fabric کند عبور ندهید؛ اگر PP میان nodeهاست، انتقال activation و pipeline bubble را در recipe لحاظ کنید. چند node با یک نام `WORLD_SIZE` یک توپولوژی یکتا نمی‌سازند.

## ۱۶. انتخاب را از گلوگاه شروع کنید؛ تعداد GPU را به‌تنهایی بهینه نکنید

ترتیب تشخیص زیر از افزودن هم‌زمان featureها قابل‌بازتولیدتر است:

۱. مدل کوچک و batch کوچک را روی یک device اجرا و صحت dtype، خروجی و loss را بسنجید.
۲. اگر مدل و optimizer روی هر device جا می‌شوند، DDP را به‌عنوان خط مبنای تقسیم داده بررسی کنید.
۳. اگر model state حافظه را محدود می‌کند، FSDP2 و ZeRO را با model/optimizer/checkpoint واقعی، نه فقط جدول مرحله‌ها، مقایسه کنید.
۴. اگر محدودیت در لایه، عمق، sequence یا MoE است، به‌ترتیب TP، PP، CP یا EP را با topology و schedule متناسب بسنجید.
۵. فقط بعد از smoke correctness، اندازه‌گیری همگام و warm-up را روی workload نماینده انجام دهید؛ وضعیت و محدودیت هر run را ثبت کنید.

برای تخمین حافظه به فصل ۵۴، برای طراحی آزمایشگاه به فصل ۵۵ و برای قیمت/TCO به فصل ۵۶ برگردید. این فصل قیمت سخت‌افزار نمی‌دهد و تعداد workerهای یک fixture ساختگی را پیش‌بینی ظرفیت یا هزینه تلقی نمی‌کند.

## ۱۷. خطاهای رایج را از روی مرز لایه عیب‌یابی کنید

| نشانه | بررسی نخست | از چه نتیجه‌ای پرهیز کنیم؟ |
| --- | --- | --- |
| `torch.cuda.is_available()` نادرست است | نسخهٔ wheel، driver، دسترسی device، متغیرهای visibility و `collect_env` | از اینکه «Python نصب شد» نتیجه نگیرید driver هم درست است. |
| API در دسترس است اما kernel شکست می‌خورد | build CUDA/HIP، معماری GPU، operator، dtype و compiler | `is_available()` را گواه همهٔ operatorها ندانید. |
| `torchrun` منتظر می‌ماند | همهٔ rankها، rank/world size، rendezvous، پورت و log اولین خطای worker | timeout را بی‌تشخیص زیاد نکنید؛ worker مفقود را پیدا کنید. |
| collective در یک node کار می‌کند و چند node نه | DNS، firewall، interface، routing و پیکربندی launcher/backend | نتیجهٔ Gloo محلی را گواه شبکهٔ NCCL/RCCL ندانید. |
| Triton در اجرا JIT نمی‌شود | نسخهٔ package، target معماری، runtime/compiler و کمینه‌ترین kernel | نصب PyPI جدا را خودکار با wheel framework سازگار فرض نکنید. |
| سرعت با worker بیشتر کم می‌شود | زمان محاسبه/ارتباط/داده، batch مؤثر، placement و load balance | از «GPU بیشتر» نتیجه نگیرید throughput بیشتر است. |

در logها token، مسیر خصوصی یا متغیر محرمانه را پاک کنید. برای هر خطا نسخه‌های `torch`, driver/runtime، backend و command line را به‌صورت یک snapshot قابل‌بازبینی کنار گزارش بگذارید.

## ۱۸. چه چیزی را اندازه بگیریم و چه چیزی را ادعا نکنیم؟

Smoke test پاسخ می‌دهد «آیا این مسیر حداقلی کار کرد؟»؛ benchmark پاسخ می‌دهد «این workload تحت پروتکل زمان‌گیری مشخص با چه هزینه/کارایی اجرا شد؟». برای دومی warm-up، همگام‌سازی device، چند تکرار، batch/sequence واقعی، precision، throughput و latency، مصرف/peak memory، تعداد worker، topology و نسخه‌ها را ثبت کنید. overhead راه‌اندازی، جمع‌آوری checkpoint و خواندن داده را با زمان kernel یکی نکنید.

در این پروژه نه GPU در دسترس است، نه CUDA/ROCm اجرا شده، نه kernel Triton و نه DeepSpeed/FSDP/Megatron. دو worker CPU فقط یک `all_reduce` صحیح در Gloo را نشان می‌دهند. نه fixture layout و نه این collective شواهدی برای scaling، سرعت، مصرف حافظه، کیفیت مدل یا برتری AMD/NVIDIA هستند.

## ۱۹. تمرین‌ها

۱. در یک آموزش دوگرهی با ۸ GPU در هر گره، چرا `LOCAL_RANK=3` را نباید به‌عنوان شناسهٔ سراسری فایل checkpoint به کار برد، و چه متغیری جای آن را می‌گیرد؟

۲. چه شواهدی از `torch` باید کنار `torch.cuda.is_available()` ثبت شوند تا یک buildِ ROCm با CUDA اشتباه نشود؟

۳. اگر مدل روی هر GPU جا می‌شود ولی throughput در دو node افت دارد، چرا اضافه‌کردن ZeRO-3 یا TP بدون تشخیص گلوگاه تصمیم زودهنگام است؟

۴. یک تیم می‌خواهد kernelِ Triton را هم روی NVIDIA و هم AMD اجرا کند. چه چیزهایی باید روی هر backend دوباره آزموده شوند، حتی اگر منبع kernel مشترک باشد؟

۵. در layout فرضی `DP=2, TP=2, PP=2, CP=1` چند worker لازم است، و چرا این محاسبه را نمی‌توان بی‌قید به MoE/EP تعمیم داد؟

پاسخ‌های استدلالی در [پاسخ‌نامهٔ مستقل فصل ۵۹](book-engineering/answers/59-gpu-systems-fa.md) آمده‌اند؛ صورت سؤال در آن فایل حفظ شده است. فرمان‌ها، fixture و محدودیت‌های واقعی پروژه در [README پروژه](book-engineering/projects/59-gpu-systems/README.md) و [گزارش ممیزی](book-engineering/chapters/59-audit-report-fa.md) ثبت شده‌اند.

## ۲۰. جمع‌بندی و مسیر ادامه

CUDA، ROCm/HIP، Triton، collective library و launcher لایه‌های متفاوت‌اند؛ نسخه و سازگاری را برای tuple کامل دستگاه/OS/driver/framework بسنجید. `torchrun` فرایند می‌سازد، NCCL/RCCL/Gloo عملیات ارتباطی را اجرا می‌کنند، و DDP/FSDP/ZeRO/Megatron هرکدام state یا بُعد متفاوتی را موازی می‌کنند. استراتژی را از محدودیت واقعی مدل و topology انتخاب کنید، نه از تعداد GPU یا نام framework.

فصل بعدی (محلی ۱۴ / سراسری ۶۰) ثبت و مقایسهٔ آزمایش‌ها و ابزارهای MLOps را جداگانه می‌سازد؛ فصل ۶۱ سپس به serving و بهینه‌سازی استنتاج می‌پردازد. خودِ این فصل PDF/EPUB تولید نمی‌کند؛ جلد وب/PWA و Markdown است.

## ۲۱. منابع و تاریخ بازبینی

**تاریخ بازبینی منابع:** ۷ نوامبر ۲۰۲۶. شماره‌های زیر snapshot مستندات مشاهده‌شده‌اند؛ سازگاری پیکربندی کامل، مگر برای پروژهٔ CPU/Gloo که صریحاً آزموده شد، جداگانه باید بررسی شود.

- NVIDIA, [CUDA Compatibility Guide, Release 620](https://docs.nvidia.com/deploy/cuda-compatibility/latest/)؛ توضیح minor-version compatibility و forward compatibility.
- NVIDIA, [CUDA Toolkit Release Notes](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html)؛ بررسی الزامات هر release/driver.
- AMD, [ROCm 10.1.0 compatibility matrix](https://rocm.docs.amd.com/en/latest/compatibility/compatibility-matrix.html) و [release notes](https://rocm.docs.amd.com/en/latest/about/release-notes.html)؛ GPU، OS، driver و framework.
- PyTorch, [HIP semantics](https://docs.pytorch.org/docs/2.15/notes/hip.html), [torchrun 2.15](https://docs.pytorch.org/docs/2.15/elastic/run.html), [distributed package](https://docs.pytorch.org/docs/2.15/distributed.html) و [FSDP2 `fully_shard`](https://docs.pytorch.org/docs/2.15/distributed.fsdp.fully_shard.html).
- OpenAI Triton, [release 3.9.0 (۲۷ اکتبر ۲۰۲۶)](https://github.com/triton-lang/triton/releases/tag/v3.9.0) و [مخزن رسمی و ماتریس سازگاری](https://github.com/triton-lang/triton).
- Microsoft DeepSpeed, [ZeRO 0.19.9](https://deepspeed.readthedocs.io/en/stable/zero3.html), [getting started](https://www.deepspeed.ai/getting-started/) و [accelerator setup guides](https://www.deepspeed.ai/tutorials/accelerator-setup-guide/).
- NVIDIA Megatron Core, [parallelism strategies, documentation 0.20.0](https://docs.nvidia.com/megatron-core/developer-guide/latest/user-guide/parallelism-guide.html).
- NVIDIA [NCCL overview](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/overview.html) و AMD [RCCL documentation](https://rocm.docs.amd.com/projects/rccl/en/latest/index.html).
- پروژهٔ آزموده‌شده: `book-engineering/projects/59-gpu-systems/`; fixture آن فقط layout ساختگی است و نتیجهٔ اجرا در `results.json` آمده است.

## ۲۲. پیوست اجرایی: preflight و آزمون CPU/Gloo

این فایل عیناً با پروژهٔ آزموده‌شده در `book-engineering/projects/59-gpu-systems/gpu_systems_demo.py` برابر است. فرمان و محدودیت‌های snapshot در README پروژه آمده‌اند.

```python
#!/usr/bin/env python3
"""Offline-safe GPU-stack preflight and a CPU/Gloo torchrun smoke test.

The project deliberately does not install vendor drivers or run GPU kernels.
It validates a synthetic dense-parallel layout, reports the active PyTorch
build, and tests process/rank/collective wiring on CPU with Gloo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any, Mapping

import torch
import torch.distributed as dist

PROJECT_DIR = Path(__file__).resolve().parent
FIXTURE_PATH = PROJECT_DIR / "sample_layout.json"
MANIFEST_PATH = PROJECT_DIR / "fixture_manifest.json"


class ContractError(ValueError):
    """Raised when a fixture or worker environment violates its contract."""


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ContractError(f"{name} must be a positive integer")
    return value


def validate_dense_layout(layout: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a simplified dense TP×PP×CP×DP layout; EP is out of scope."""
    if layout.get("schema_version") != "v4-ch13-layout-v1":
        raise ContractError("unsupported layout schema_version")
    if layout.get("label_source") != "synthetic_fixture":
        raise ContractError("layout must be labeled synthetic_fixture")
    metadata = layout.get("metadata")
    required_false = (
        "real_hardware_observed",
        "training_run_performed",
        "benchmark_performed",
        "expert_parallelism_modeled",
    )
    if not isinstance(metadata, dict) or any(metadata.get(key) is not False for key in required_false):
        raise ContractError("fixture metadata must explicitly exclude hardware, training, benchmark, and EP claims")

    world_size = _positive_int(layout.get("world_size"), "world_size")
    dense = layout.get("dense_parallelism")
    if not isinstance(dense, dict):
        raise ContractError("dense_parallelism must be an object")
    dimensions = {name: _positive_int(dense.get(name), name) for name in ("dp", "tp", "pp", "cp")}
    product = dimensions["dp"] * dimensions["tp"] * dimensions["pp"] * dimensions["cp"]
    if product != world_size:
        raise ContractError(
            f"dense parallelism product {product} does not equal world_size {world_size}"
        )
    return {
        "fixture_id": layout.get("fixture_id"),
        "label_source": "synthetic_fixture",
        "world_size": world_size,
        "dense_parallelism": dimensions,
        "dimension_product": product,
        "valid": True,
        "scope": {
            "expert_parallelism_included": False,
            "real_hardware_observed": False,
            "training_run_performed": False,
            "benchmark_performed": False,
        },
    }


def load_fixture(path: Path = FIXTURE_PATH, manifest_path: Path = MANIFEST_PATH) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("fixture_id") != "v4-ch13-synthetic-dense-layout-v1":
        raise ContractError("fixture manifest id mismatch")
    if manifest.get("sha256") != digest:
        raise ContractError("fixture SHA-256 does not match the manifest")
    if manifest.get("label_source") != "synthetic_fixture":
        raise ContractError("fixture manifest must identify synthetic data")
    layout = json.loads(raw.decode("utf-8"))
    validated = validate_dense_layout(layout)
    if validated["fixture_id"] != manifest["fixture_id"]:
        raise ContractError("fixture and manifest ids differ")
    return layout, digest


def classify_backend(cuda_build: str | None, hip_build: str | None, available: bool) -> str:
    """Distinguish builds using metadata; torch.cuda is also PyTorch's HIP API."""
    if hip_build:
        return "rocm-hip" if available else "rocm-build-no-visible-device"
    if cuda_build:
        return "cuda" if available else "cuda-build-no-visible-device"
    return "cpu-or-no-accelerator-build"


def runtime_snapshot() -> dict[str, Any]:
    available = bool(torch.cuda.is_available())
    backend = classify_backend(torch.version.cuda, torch.version.hip, available)
    count = int(torch.cuda.device_count()) if available else 0
    devices = [torch.cuda.get_device_name(index) for index in range(count)] if available else []
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "torch": str(torch.__version__),
        "torch_cuda_build": torch.version.cuda,
        "torch_hip_build": torch.version.hip,
        "torch_cuda_api_available": available,
        "accelerator_backend_classification": backend,
        "visible_device_count": count,
        "visible_device_names": devices,
        "distributed_available": bool(dist.is_available()),
        "gloo_available": bool(dist.is_available() and dist.is_gloo_available()),
        "nccl_available": bool(dist.is_available() and dist.is_nccl_available()),
    }


def worker_identity(env: Mapping[str, str] | None = None) -> dict[str, int]:
    values = os.environ if env is None else env
    required = ("RANK", "LOCAL_RANK", "WORLD_SIZE")
    missing = [key for key in required if key not in values]
    if missing:
        raise ContractError(f"launch with torchrun; missing environment variables: {', '.join(missing)}")
    try:
        rank, local_rank, world_size = (int(values[key]) for key in required)
    except (TypeError, ValueError) as exc:
        raise ContractError("RANK, LOCAL_RANK, and WORLD_SIZE must be integers") from exc
    if world_size < 2:
        raise ContractError("the Gloo smoke test requires at least two workers")
    if rank < 0 or rank >= world_size:
        raise ContractError("RANK must be in [0, WORLD_SIZE)")
    if local_rank < 0:
        raise ContractError("LOCAL_RANK must be non-negative")
    return {"rank": rank, "local_rank": local_rank, "world_size": world_size}


def _scope_limits() -> dict[str, bool]:
    return {
        "cuda_runtime_tested": False,
        "rocm_runtime_tested": False,
        "triton_kernel_executed": False,
        "deepspeed_training_executed": False,
        "fsdp_training_executed": False,
        "megatron_training_executed": False,
        "gpu_benchmark_performed": False,
        "model_quality_claim": False,
    }


def run_gloo_smoke(output_path: Path) -> dict[str, Any]:
    identity = worker_identity()
    if not dist.is_available() or not dist.is_gloo_available():
        raise RuntimeError("this CPU smoke test requires PyTorch distributed with Gloo support")
    fixture, fixture_hash = load_fixture()
    dist.init_process_group(backend="gloo", timeout=timedelta(seconds=60))
    try:
        if dist.get_rank() != identity["rank"] or dist.get_world_size() != identity["world_size"]:
            raise RuntimeError("torchrun environment and initialized process group disagree")
        rank = dist.get_rank()
        world_size = dist.get_world_size()
        value = torch.tensor([rank + 1], dtype=torch.int64, device="cpu")
        dist.all_reduce(value, op=dist.ReduceOp.SUM)
        observed = int(value.item())
        expected = world_size * (world_size + 1) // 2
        if observed != expected:
            raise RuntimeError(f"all_reduce returned {observed}; expected {expected}")
        result = {
            "schema_version": "v4-ch13-gloo-smoke-v1",
            "fixture_id": fixture["fixture_id"],
            "fixture_sha256": fixture_hash,
            "validated_synthetic_layout": validate_dense_layout(fixture),
            "environment": runtime_snapshot(),
            "process_group": {
                "backend": "gloo",
                "rank": rank,
                "local_rank": identity["local_rank"],
                "world_size": world_size,
                "rank_inputs": list(range(1, world_size + 1)),
            },
            "collective": {
                "operation": "all_reduce_sum",
                "observed": observed,
                "expected": expected,
                "passed": observed == expected,
            },
            "scope": _scope_limits(),
        }
        if rank == 0:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = output_path.with_name(output_path.name + f".{os.getpid()}.tmp")
            temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            temporary.replace(output_path)
        dist.barrier()
        return result
    finally:
        if dist.is_initialized():
            dist.destroy_process_group()


def _json_stdout(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("preflight", "layout", "gloo-smoke"), default="preflight")
    parser.add_argument("--fixture", type=Path, default=FIXTURE_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--output", type=Path, default=Path("/tmp/ch59-gloo-smoke.json"))
    parser.add_argument("--local-rank", "--local_rank", type=int, default=None,
                        help="accepted for compatibility; torchrun environment variables are authoritative")
    args = parser.parse_args(argv)
    try:
        if args.mode == "preflight":
            _json_stdout(runtime_snapshot())
        elif args.mode == "layout":
            fixture, digest = load_fixture(args.fixture, args.manifest)
            _json_stdout({"fixture_sha256": digest, "layout": validate_dense_layout(fixture)})
        else:
            _json_stdout(run_gloo_smoke(args.output))
    except (ContractError, OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
