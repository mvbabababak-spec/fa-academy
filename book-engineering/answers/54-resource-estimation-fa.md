# پاسخ‌نامهٔ تشریحی فصل ۵۴

این پاسخ‌نامه مستقل است تا امکان بررسی تمرین‌ها بدون جست‌وجو در متن اصلی فراهم باشد. مقادیر محاسبه‌شده همچنان نتیجهٔ فرمول و فرض مسئله‌اند، نه benchmark یا سنجش GPU.

## ۱. وزن BF16 و INT8 برای مدل ۷B

برای BF16، هر وزن را در این حساب ساده دو بایت می‌گیریم:

`7,000,000,000 × 2 = 14,000,000,000 bytes = 14 GB ≈ 13.038 GiB`.

برای INT8:

`7,000,000,000 × 1 = 7,000,000,000 bytes = 7 GB ≈ 6.519 GiB`.

این‌ها footprint ریاضیِ وزن خالص با فرض بایت ثابت‌اند. قالب quantization می‌تواند scaleها، metadata، گروه‌بندی، tensorهای نگه‌داشته‌شده با دقت بالاتر و bufferهای dequantization داشته باشد؛ runtime، cache، activation و حافظهٔ allocator نیز هنوز افزوده نشده‌اند. بنابراین INT8 به‌تنهایی ظرفیت لازم دستگاه را تعیین نمی‌کند.

## ۲. KV cache

رابطه:

`M_KV = 2 × L × B × T × H_KV × d_head × b_KV`.

جایگذاری:

`2 × 32 × 4 × 8192 × 8 × 128 × 2 = 4,294,967,296 bytes = 4 GiB`.

اگر batch از ۴ به ۸ برسد و بقیهٔ فرض‌ها ثابت بمانند، cache دو برابر و برابر ۸ GiB می‌شود. دلیل خطی‌بودن نسبت به batch در این مدل، وجود یک K و یک V برای هر لایه، sequence و KV head است. Cacheهای sliding-window یا quantized و معماری‌های دیگر به این فرض دقیقاً منطبق نیستند.

## ۳. Full fine-tuning با پیکربندی ۱۸ بایت/پارامتر

در این فرض:

`b_w + b_g + b_m + b_o = 2 + 4 + 4 + 8 = 18 bytes/parameter`.

برای `N=N_t=7.035B`:

- وزن کم‌دقت: `7.035B × 2 = 14.07 GB`؛
- gradient: `7.035B × 4 = 28.14 GB`؛
- کپی master: `7.035B × 4 = 28.14 GB`؛
- دو حالت optimizer: `7.035B × 8 = 56.28 GB`.

جمع حالت‌ها `126.63 GB` ده‌دهی است؛ activation، workspace، runtime، fragmentation و حاشیهٔ اطمینان در این جمع نیستند. این یک انتخابِ فرضی از dtype و optimizer است، نه قانون همهٔ آموزش‌ها.

## ۴. Adapter با ۳۵ میلیون پارامتر trainable

وزن همهٔ مدل همچنان در حساب می‌ماند:

`7.035B × 2 = 14.07 GB`.

فقط stateهای trainable بر `35M` ضرب می‌شوند:

- gradient: `35M × 4 = 0.14 GB`؛
- master: `35M × 4 = 0.14 GB`؛
- optimizer: `35M × 8 = 0.28 GB`.

پس subtotal حالت‌ها `14.07 + 0.14 + 0.14 + 0.28 = 14.63 GB` است. در profile ساختگی، مرجع activation با همان فرض‌های قابل‌مشاهده ۴ GiB دیگر می‌افزاید؛ total حسابی `18.924967 GB` می‌شود. این سناریو نشان می‌دهد بخش optimizer/gradient کوچک می‌شود، اما وزن پایه حذف نشده است. مساوی‌گرفتن شمار پارامترهای adapter با سهم کل حافظه نادرست است؛ میزان activation واقعی نیز باید در پیکربندی واقعی اندازه‌گیری شود.

## ۵. ZeRO stage 2 روی چهار rank

در stage 2 ایدئال، وزن‌ها replicate می‌مانند؛ gradient و stateهای optimizer/master بر چهار تقسیم می‌شوند:

- وزن: `14.07 GB`؛
- gradient: `28.14 / 4 = 7.035 GB`؛
- master: `28.14 / 4 = 7.035 GB`؛
- optimizer: `56.28 / 4 = 14.07 GB`.

حالت‌ها جمعاً `42.21 GB` در هر rank هستند، پیش از activation و bufferهای موقت. اگر از profile همان متن ۴ GiB activation reference را هم بیفزاییم، total حسابی به `46.504967 GB` در هر rank می‌رسد. در اجرای واقعی gather/reduce-scatter و بافرها، padding، allocator و ارتباط شبکه نیز اهمیت دارند؛ تقسیم سادهٔ حافظهٔ حالت‌ها اندازه‌گیری جایگزین نیست.

## ۶. آموزش متراکم با `6ND`

`C ≈ 6 × 7,000,000,000 × 140,000,000,000 = 5.88 × 10²¹ FLOPs`.

از این مقدار به‌تنهایی نمی‌دانیم، برای نمونه:

1. چند روز/ساعت اجرا لازم است؛
2. نرخ مؤثر FLOPs دستگاه یا cluster چقدر است؛
3. attention، padding، MoE، checkpointing و optimizer چه سرباری دارند؛
4. batch، طول توالی، تعداد epoch و کیفیت/تکرار داده چیست؛
5. ارتباط بین دستگاه‌ها یا خواندن داده bottleneck می‌شود یا نه؛
6. نتیجهٔ کیفیت مدل یا سطح benchmark چه خواهد بود.

`6ND` یک تقریب محاسبهٔ مرتبهٔ اول است، نه تبدیل خودکار FLOPs به runtime.

## ۷. FLOPs خطی برای استنتاج

با `N=7B`, `B=4`, `T_prompt=4096`, `T_generated=1024`:

`C_linear ≈ 2 × 7B × 4 × (4096 + 1024) = 286,720,000,000,000 FLOPs`.

این فقط بخش‌های خطیِ متراکم را با قرارداد دو FLOP برای هر multiply-add می‌شمارد. توجهِ prefill، به‌ویژه برای sequence بلند، term جدا می‌خواهد؛ cache، زمان‌بندی decode، ارتباط و اندازه‌گیری latency هم در فرمول نیستند. پس تقسیم این عدد بر peak FLOPs روی بروشور runtime قطعی نمی‌دهد.

## ۸. کاهش قلهٔ activation

نمونه‌ها:

- **کوچک‌کردن micro-batch:** معمولاً activation هم‌زمان را کم می‌کند؛ برای حفظ global batch می‌توان gradient accumulation را بررسی کرد. وزن‌ها و optimizer state حذف نمی‌شوند و نتیجه به normalization/scheduler/optimizer وابسته است.
- **Activation checkpointing:** بخشی از activationها در backward دوباره محاسبه می‌شود تا حافظهٔ نگه‌داری‌شده کمتر شود؛ محاسبه/زمان بیشتر می‌طلبد و سود آن به نقاط checkpoint بستگی دارد.
- **کاهش طول توالی:** معمولاً حافظهٔ activation و KV را کم می‌کند؛ اما اگر workload به context بلند نیاز دارد، این تغییر معنای مسئله را عوض می‌کند.

هیچ درصد صرفه‌جویی واحدی از خود نام گزینه‌ها به دست نمی‌آید؛ باید همان پیکربندی را اندازه گرفت.

## ۹. پروتکل سنجش peak واقعی

یک پروتکل معقول: ثبت نسخهٔ Python/framework/driver و مشخصات workload؛ آزادکردن processهای دیگر؛ اجرای warm-up؛ resetکردن peak counter؛ synchronizeکردن دستگاه در مرزهای سنجش؛ اجرای forward، loss، backward و optimizer step با طول/batch بدترین حالت مورد انتظار؛ ثبت `max_memory_allocated`, `memory_allocated`, `memory_reserved` و مصرف/آزادِ سطح دستگاه؛ اجرای چند تکرار؛ ذخیرهٔ روش attention، dtype، optimizer، checkpointing، concurrency و خروجی خام.

`memory_allocated` مقدار tensorهای فعال PyTorch را نشان می‌دهد؛ `max_memory_allocated` اوج این نوع allocation از reset/شروع را می‌دهد؛ `memory_reserved` مقدار مدیریت‌شده توسط caching allocator است و allocated را در خود دارد، پس این دو را با هم جمع نکنید. گزارش سطح دستگاه ممکن است processها یا بخش‌هایی بیرون از allocator PyTorch را هم ببیند. این‌ها **سه پرسش متفاوت**اند؛ به جای یک عدد، نام سنجه و مرز اندازه‌گیری را بنویسید.

## ۱۰. چرا «چهار GPU یعنی یک‌چهارم حافظه» کافی نیست؟

DDP معمولی وزن‌ها و optimizer state را روی هر rank replicate می‌کند و فقط gradientها را همگام می‌سازد؛ بنابراین اضافه‌کردن چهار GPU به‌تنهایی همهٔ حافظه را چهارقسمتی نمی‌کند. تقسیم واقعی به راهبرد بستگی دارد: ZeRO stageها stateهای متفاوتی را shard می‌کنند، و هرکدام همچنان activation، KV، buffer ارتباطی و workspace دارد. افزون بر آن، باید طول توالی، micro-batch، dtype، بخش trainable، در دسترس‌بودن حافظه، processهای دیگر، حاشیهٔ safety و هزینهٔ شبکه را بدانیم. پس عبارت «حتماً جا می‌شود» بدون پیکربندی و اجرای آزمایشی قابل دفاع نیست.
