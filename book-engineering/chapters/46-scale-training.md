# جلد سوم، فصل ۱۴ — Gradient Checkpointing، آموزش توزیع‌شده و مقیاس

**نگاشت:** فصل محلی ۱۴ جلد سوم = فصل سراسری ۴۶. **تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶.** فصل ۴۴ یک حلقهٔ تک‌پردازشی را با accumulation و ذخیره/بازیابی وضعیت run آزمایش کرد؛ فصل ۴۵ precision را بررسی کرد. این فصل از همان مسئله شروع می‌کند و می‌پرسد وقتی مدل یا run از یک process فراتر می‌رود، چه چیزی باید بخش‌بندی، دوباره‌محاسبه، همگام، ثبت و بازیابی شود.

**مرزبندی با فصل‌های پیشین:** فصل ۸ مفاهیم پایهٔ چند GPU، شبکه و همگام‌سازی را معرفی می‌کند؛ فصل ۴۲ بودجهٔ tensorها را تخمین می‌زند؛ فصل ۴۳ منشأ و نسخهٔ داده را بررسی می‌کند؛ فصل ۴۴ checkpoint تک‌پردازشی برای ادامهٔ آموزش را می‌سازد. این فصل آن پروژه‌ها را بازنویسی نمی‌کند. تمرکز تازه بر **activation recomputation**، وزن‌دهی صحیح میان rankها، ترکیب راهبردهای موازی، run tracking و بازیابیِ هماهنگ در job چندپردازه‌ای است.

![شکل ۳-۱۴-۱ — طرح شماتیک آموزش توزیع‌شده: sampler داده را میان rankها پخش می‌کند، forward/backward گرادیان می‌سازد، AllReduce آن‌ها را همگام می‌کند و optimizer یک update انجام می‌دهد؛ activation recomputation با sharding وضعیت مدل دو اهرم حافظهٔ جدا هستند؛ snapshot هماهنگ و run record شامل hashها، نسخه‌ها، معیارها و artifactها، restart را به resume معتبر پیوند می‌دهند.](assets/images/babak-ai/v3-ch14-scale-training.webp)

**شکل ۳-۱۴-۱ —** تقسیم داده، پارامتر و activation یک کار نیستند. راهبرد مناسب به اندازهٔ مدل، batch، شکل دنباله، ارتباط، backend و محدودیت حافظه بستگی دارد؛ شکل سرعت یا پشتیبانی سخت‌افزار خاصی را تضمین نمی‌کند.

## ۱. از آزمایش کوچک به run بزرگ‌تر

در یک نمونهٔ کوچک، معمولاً یک process داده می‌خواند، forward و backward انجام می‌دهد، optimizer را یک بار به‌روز می‌کند و تاریخچه می‌نویسد. هنگام scale، ممکن است یک GPU جا کم بیاورد، یک process داده را به‌اندازهٔ کافی سریع نرساند، optimizer state حافظه را بگیرد، یا زمان یک run از پنجرهٔ قابل‌اجرا بیشتر شود. این‌ها گلوگاه‌های متفاوت‌اند؛ افزودن GPU هر کدام را خودکار حل نمی‌کند.

پیش از انتخاب ابزار، نیاز را دقیق کنید: آیا مدل **به‌خودی‌خود** در حافظه جا نمی‌شود؟ activationها پرهزینه‌اند؟ آیا هدف کم‌کردن زمان با همان مقدار کار است یا پردازش دادهٔ بیشتر؟ شکست محتمل چیست و چه stateای برای ادامه نیاز دارید؟ سپس یک baseline قابل‌بازتولید و یک معیار موفقیت—مانند throughput تحت سقف کیفیت و حافظه—تعریف کنید.

## ۲. ابتدا نوع حافظه و محل گلوگاه را جدا کنیم

برای آموزش، وزن‌ها، گرادیان‌ها، حالت optimizer، activationهای لازم برای backward، tensorهای موقت kernel، bufferهای ارتباط و fragmentation همگی در تصویر حافظه سهم دارند. برآورد پارامتر در فصل ۴۲ تنها بخشی از این تصویر بود؛ این‌جا همان تفکیک را برای تصمیم‌گیری به کار می‌بریم، نه برای محاسبهٔ یک «VRAM لازم» خیالی.

سه پرسش راهنما:

1. آیا بخش عمدهٔ فشار از activationها و طول دنباله می‌آید؟ بررسی rematerialization یا انتخاب sequence/context parallelism ممکن است مرتبط باشد.
2. آیا وزن، گرادیان و optimizer state در هر replica جا نمی‌شوند؟ state sharding مانند FSDP/ZeRO را بررسی کنید.
3. آیا حافظه کافی است، اما GPUها منتظر داده یا ارتباط‌اند؟ profiler، sampler، storage و topology را بررسی کنید؛ تغییر الگوریتم حافظه شاید سرعت را بهتر نکند.

یک run می‌تواند هم‌زمان بیش از یک گلوگاه داشته باشد. قبل از تغییر، اندازه‌گیری‌ای متناسب با همان نسخه، shape، batch و دستگاه بگیرید.

## ۳. دو معنای متفاوت «checkpoint»

واژهٔ checkpoint دست‌کم دو سازوکار را نام می‌برد؛ یکی را به‌جای دیگری به‌کار نبرید.

| نام دقیق‌تر | چه چیزی را نگه می‌دارد؟ | چه زمانی به کار می‌آید؟ | چه چیزی را حل نمی‌کند؟ |
|---|---|---|---|
| **Activation checkpoint / recomputation** | ورودی یا مرز تعدادی segment در graph forward | در همان backward، activationهای میانی را دوباره محاسبه می‌کند تا بعضی را ذخیره نکند | run قطع‌شده را بعداً از سر نمی‌گیرد |
| **Training-state checkpoint / snapshot** | وزن، optimizer، گام، sampler، RNG و state لازم دیگر | process متوقف شده یا job به‌خاطر شکست/پیش‌تخصیص باید از state معتبر ادامه یابد | activationهای هر backward جاری را کم نمی‌کند |

در این فصل «بازمحاسبهٔ activation» را برای معنای اول و «snapshot ذخیره‌شده» یا «checkpoint آموزش» را برای معنای دوم به‌کار می‌بریم. فصل ۴۴ برای معنای دوم در یک process نمونه ساخت؛ این فصل بر هماهنگی چند rank تمرکز می‌کند.

## ۴. Activation recomputation: حافظه را با محاسبه معاوضه کنیم

در forward، autograd بعضی خروجی‌های میانی را نگه می‌دارد تا backward از آن‌ها استفاده کند. با activation checkpointing، به‌جای ذخیرهٔ همهٔ tensorهای داخل یک region، مرز region حفظ می‌شود؛ هنگام backward، تابع forward آن region دوباره اجرا می‌شود تا مقدارهای لازم بازسازی شوند. پس حافظهٔ activation می‌تواند کم شود، اما محاسبه و زمان اضافه می‌شود [۱].

این انتخاب با «یک قانون ثابت به‌اندازهٔ جذر تعداد لایه‌ها» برای هر Transformer یکی نیست. حد نظری و طرح بهینهٔ مقالهٔ ۲۰۱۶ به فرض‌ها و graph آن مربوط است؛ کتابخانه‌ها و مدل‌های جدید ممکن است checkpoint کل block، بخش‌هایی از آن یا عملیات انتخابی را اجرا کنند. حافظهٔ واقعی به activationهای بقیهٔ مدل، طول sequence، batch، kernel، bufferها و allocator هم وابسته می‌ماند.

## ۵. مرزهای recomputation را آگاهانه انتخاب کنیم

Checkpoint کردن هر بخش می‌تواند بیش از حد محاسبهٔ forward را تکرار کند؛ checkpoint کردن بخش بسیار کوچک نیز شاید activation قابل‌توجهی آزاد نکند. روی workload هدف، حافظهٔ peak، زمان step و تعداد tokenهای مفید را همراه هم بسنجید. پژوهش selective recomputation در Transformer نشان داد که در setup همان مقاله می‌توان بخش‌های حافظه‌بر را انتخاب کرد و هزینهٔ اضافه را کاهش داد؛ اعداد آن مقاله پیش‌بینی دستگاه شما نیستند [۱۱].

در PyTorch 2.6، `torch.utils.checkpoint.checkpoint` اجرای forward یک region را در backward بازاجرا می‌کند و مستندات `use_reentrant=False` را توصیه می‌کنند. آرگومان را صریح بدهید. تابع checkpoint‌شده باید در بازاجرای backward همان محاسبهٔ forward را انجام دهد؛ متغیر global تغییریافته یا side effect پنهان می‌تواند گرادیان نادرست بسازد. برای dropout و عملیات تصادفی، نگه‌داری و بازگردانی RNG به‌طور پیش‌فرض فعال است، ولی این کار هزینه دارد و جابه‌جایی tensor به device جدید درون تابع، برابری RNG را تضمین نمی‌کند [۲].

## ۶. Data Parallelism در سطح یک optimizer update

در DDP، هر worker معمولاً کپی کاملی از مدل را دارد و shard متفاوتی از batch می‌بیند. پس از backward، gradientها میان rankها همگام می‌شوند؛ optimizer هر rank باید همان update را روی پارامترهای همسان انجام دهد. `DistributedDataParallel` ورودی را خودکار shard نمی‌کند: انتخاب نمونه‌ها و `DistributedSampler` یا روش تقسیم دیگر مسئولیت برنامه است [۳].

هر process در group یک `rank` دارد؛ `world_size` شمار rankهای همان group است. یک node می‌تواند چند process محلی داشته باشد و چند node در یک worker group شرکت کنند. همهٔ rankها باید با ترتیب parameterهای هم‌سان وارد collectiveهای سازگار شوند؛ اگر rankها در مسیرهای متفاوت بمانند، عملیات همگام‌سازی ممکن است منتظر بماند یا خطا دهد.

## ۷. میانگین گرادیان با shardهای نابرابر

اگر rankها batch هم‌اندازه داشته باشند، میانگین سادهٔ lossهای محلی معمولاً هدف batch کلی را می‌سازد. اما با تعداد نمونهٔ متفاوت در rankها، میانگینِ میانگین‌های محلی به نمونه‌ها وزن برابر نمی‌دهد. این جزئیات برای batch آخر، shard ناقص یا تعداد target معتبر متفاوت مهم است.

فرض کنید rank `r` مجموع lossهای محلی `Sᵣ` و `nᵣ` نمونه دارد؛ `N=Σ nᵣ` و شمار rankها `W` است. چون DDP گرادیان rankها را میانگین می‌گیرد، هر rank باید مجموع loss خود را در `W/N` ضرب کند تا گرادیان نهایی معادل میانگین نمونه‌های global باشد:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="اگر هر rank مجموع loss محلی S r داشته باشد، میانگین گرادیان سراسری برابر یک تقسیم بر N ضربدر مجموع گرادیان مجموع lossهای rankها است؛ برای DDP میانگین‌گیر، loss هر rank در W تقسیم بر N وزن داده می‌شود">
  <mrow><msub><mi>L</mi><mi>r</mi></msub><mo>=</mo><mfrac><mi>W</mi><mi>N</mi></mfrac><msub><mi>S</mi><mi>r</mi></msub><mo>;</mo><mspace width="0.7em"/><mfrac><mn>1</mn><mi>W</mi></mfrac><munderover><mo>∑</mo><mrow><mi>r</mi><mo>=</mo><mn>0</mn></mrow><mrow><mi>W</mi><mo>−</mo><mn>1</mn></mrow></munderover><mo>∇</mo><msub><mi>L</mi><mi>r</mi></msub><mo>=</mo><mfrac><mn>1</mn><mi>N</mi></mfrac><munderover><mo>∑</mo><mrow><mi>r</mi><mo>=</mo><mn>0</mn></mrow><mrow><mi>W</mi><mo>−</mo><mn>1</mn></mrow></munderover><mo>∇</mo><msub><mi>S</mi><mi>r</mi></msub></mrow>
</math>

در پروژهٔ CPU این فصل rankها ۳ و ۲ نمونه دارند. هر worker `local_loss_sum × world_size / global_sample_count` را backpropagate می‌کند. پس از همگام‌سازی، گرادیان DDP باید با backward روی پنج نمونه در یک process برابر باشد؛ در fixture نتیجهٔ هر دو `−33` است. اگر تعداد نمونه‌ها برابر باشد، فرمول به میانگین معمول محلی تبدیل می‌شود. در workflow واقعی برای padding و targetهای نامعتبر، مخرج را بر مبنای targetهای واقعاً داخل loss انتخاب کنید.

## ۸. Batch سراسری، accumulation و تعداد token

با microbatch اندازهٔ `m`, gradient accumulation برابر `G`, و تعداد replicaهای data-parallel برابر `D`, batch مؤثر تقریبی یک update می‌شود `m×G×D`؛ فرض می‌کند همهٔ batchها کامل‌اند و هر نمونه یک وزن دارد. در زبان‌مدل، تعداد token معتبر در update از batch به‌تنهایی دقیق‌تر است: padding، طول‌های متفاوت، packing و آخرین batch می‌توانند شمار token را عوض کنند.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="batch مؤثر تقریبی برابر microbatch در هر rank ضربدر گام‌های accumulation ضربدر تعداد replicaهای data parallel است؛ targetهای معتبر باید جدا شمرده شوند">
  <mrow><msub><mi>B</mi><mi>global</mi></msub><mo>≈</mo><msub><mi>B</mi><mi>micro</mi></msub><mo>×</mo><mi>G</mi><mo>×</mo><mi>D</mi></mrow>
</math>

اگر `D` را زیاد کنید و microbatch و accumulation ثابت بمانند، دادهٔ هر update بزرگ‌تر می‌شود؛ همان LR و همان تعداد update الزاماً همان run نیست. اگر می‌خواهید دو پیکربندی را مقایسه کنید، روشن کنید چه چیزی ثابت است: global valid-token batch، کل tokenهای دیده‌شده، تعداد update، optimizer schedule یا wall-clock budget. همه را هم‌زمان ثابت نگه‌داشتن ممکن نیست.

## ۹. AllReduce، bucketها و زمان انتظار

`AllReduce` جمع یا عمل reduction را میان همهٔ rankها انجام می‌دهد و نتیجه را به همه برمی‌گرداند؛ برای DDP با loss محلی مناسب، نتیجه گرادیان‌های همگام‌شده است. PyTorch DDP گرادیان‌ها را در bucketها گروه‌بندی می‌کند تا کاهش یک bucket در بعضی پیکربندی‌ها با ادامهٔ backward هم‌پوشانی داشته باشد. این هم‌پوشانی به اندازهٔ bucket، ترتیب graph، backend و topology وابسته است [۳].

برای آموزش GPU، مستندات PyTorch NCCL را backend توصیه‌شده می‌دانند؛ برای DDP CPU از Gloo استفاده می‌شود. انتخاب backend فقط نام یک option نیست: درایور، CUDA/NCCL، کارت شبکه، مسیر میان‌گره‌ای، firewall و نسخهٔ سازگار باید بررسی شوند [۴]. نمونهٔ CPU فصل backend شبکهٔ GPU یا NCCL را نمی‌آزماید.

## ۱۰. DDP حافظهٔ مدل را خودبه‌خود جمع نمی‌کند

در data parallel، هر rank معمولاً وزن‌های کامل مدل، گرادیان‌ها و optimizer state لازم را نگه می‌دارد؛ افزودن rankها به‌تنهایی model state بزرگ را در چند GPU پخش نمی‌کند. اگر پارامتر یا optimizer state روی یک device جا نمی‌شود، familyهای state-sharding مانند ZeRO و PyTorch FSDP مسئلهٔ دیگری را هدف می‌گیرند.

| طرح | stateهای partitionشده | معاملهٔ اصلی |
|---|---|---|
| ZeRO stage 1 | optimizer state | کاهش حافظهٔ تکراری optimizer؛ هنوز وزن/گرادیان کپی‌های کامل دارند |
| ZeRO stage 2 | optimizer state و گرادیان | حافظهٔ کمتر؛ نیاز به جمع/تقسیم گرادیان سازگار |
| ZeRO stage 3 | optimizer state، گرادیان و پارامتر | حافظهٔ model-state کمتر؛ پارامترها هنگام محاسبه باید gather شوند |
| FSDP | stateهای ماژول بر پایهٔ راهبرد sharding | gather پارامتر و reduce-scatter گرادیان؛ wrapping، buffer و نسخه مهم‌اند |

این نام‌گذاری مراحل، شرح ZeRO از DeepSpeed و مقالهٔ آن است؛ APIهای DeepSpeed و FSDP را یکسان ندانید [۵، ۶]. State sharding حافظهٔ activation را لزوماً برطرف نمی‌کند، و activation checkpointing جایگزین sharding نیست. پروژهٔ کوچک این فصل هیچ‌کدام را روی GPU اجرا نمی‌کند.

## ۱۱. Tensor، Pipeline و ترکیب موازی‌سازی

فصل ۸ Data Parallelism و تقسیم مدل را معرفی کرد؛ در این‌جا سؤال اصلی **چطور چند محور را با هم ترکیب کنیم** است. در Tensor Parallelism، یک tensor یا محاسبهٔ درون یک لایه بین deviceها شکسته می‌شود و داخل block به ارتباط نیاز دارد. در Pipeline Parallelism، لایه‌ها به stageها واگذار می‌شوند؛ microbatchها stageها را پر می‌کنند، اما pipeline bubble و انتقال activation/gradient می‌ماند. Data Parallelism بین replicaها shard نمونه را پخش می‌کند. Megatron-LM این محورها را در همان cluster، معماری و schedule پژوهش ترکیب کرد؛ نتیجهٔ مقاله benchmark عمومی نیست [۷].

یک راهنمای تصمیم، نه قانون:

- اگر مدل جا می‌شود و داده‌رسانی/throughput گلوگاه است، اول DDP و sampler را اندازه بگیرید.
- اگر وزن/optimizer state جا نمی‌شود، FSDP/ZeRO را ارزیابی کنید.
- اگر یک لایه یا projection بزرگ‌تر از ظرفیت device است، tensor parallel ممکن است لازم شود.
- اگر مدل از چند stage بزرگ‌تر است، pipeline parallel را بررسی کنید و هزینهٔ microbatch و bubble را بسنجید.
- برای ترکیب روش‌ها، topology واقعی و payload ارتباط را پروفایل کنید؛ هر محور موازی‌سازی می‌تواند محدودیت محور دیگر را تشدید کند.

## ۱۲. برنامهٔ عیب‌یابی حافظه و مقیاس

هنگام OOM، از راه‌حل‌های کوچک و تفکیک‌شده شروع کنید: (۱) ثبت کنید چه tensor یا state در peak حضور دارد؛ (۲) microbatch و sequence length را جدا کنترل کنید؛ (۳) اگر activation عامل است، checkpoint یا attention path را ارزیابی کنید؛ (۴) اگر state مدل غالب است، sharding یا offload را در محیط مجاز بسنجید؛ (۵) پس از هر تغییر، throughput و metric را دوباره اندازه بگیرید.

«مدل جا شد» قبولی کامل نیست: آیا optimizer update برقرار است؟ آیا همهٔ rankها همان تعداد collective را اجرا کردند؟ آیا حافظهٔ communication buffer و checkpoint هم حساب شد؟ آیا معیار validation تحت همان budget می‌ماند؟ یک عامل را در هر آزمایش تغییر دهید تا معلوم باشد نتیجه از کجا آمده است. تغییر precision را به‌جای این فصل از پروتکل فصل ۴۵ کنترل کنید.

## ۱۳. Scaling efficiency را از کیفیت جدا نکنیم

فصل ۸ شتاب، بهره‌وری نسبت به ایده‌آل و هزینهٔ ارتباط را معرفی کرد. برای LLM، یک عدد tokens/second هم به‌تنهایی کافی نیست: دنبالهٔ کوتاه/بلند، padding، precision، throughput مفید، update batch و مقدار کار تا metric هدف را ثبت کنید. زمان setup، data loading، checkpoint I/O و synchronization را از زمان kernel جدا کنید، و end-to-end عدد نهایی را هم گزارش دهید.

در strong scaling، حجم کار تقریباً ثابت و worker بیشتر می‌شود؛ در weak scaling، بار هر worker ثابت می‌ماند و حجم کل بالا می‌رود. اگر با افزایش `D` global batch یا token budget عوض شود، training dynamics و validation می‌تواند تغییر کند. به همین دلیل «۴ GPU سریع‌تر از ۱ GPU است» باید همراه config، کیفیت، سخت‌افزار و خطای اندازه‌گیری بیان شود، نه به‌عنوان نتیجه‌ای از تعداد کارت‌ها.

## ۱۴. داده‌رسانی، ارتباط و گلوگاه rank کند

یک collective تا وقتی کندترین یا دیرترین rank وارد آن نشود کامل نمی‌شود. یک rank ممکن است به‌علت decode، شبکهٔ storage، CPU oversubscription یا batch متفاوت عقب بیفتد؛ GPUهای دیگر در انتظار بمانند. پیش از افزودن worker، زمان data wait، forward/backward، all-reduce، optimizer و checkpoint write را جدا log کنید.

داده‌خوان‌ها و prefetch می‌توانند گلوگاه را جابه‌جا کنند؛ افزایش workerها هم ممکن است رقابت CPU یا IO بسازد. pinned memory و asynchronous transfer فقط وقتی مفید است که مسیر دستگاه/نرم‌افزار آن را پشتیبانی کند و اندازه‌گیری نشان دهد. در multi-node، ترتیب cardها، نوع link، تعداد message، bandwidth و latency اهمیت دارند؛ مشخصات اسمی کارت یا شبکه جای profiler را نمی‌گیرد.

## ۱۵. Experiment Tracking: هر اجرا شناسه و زمینهٔ خودش را دارد

یک run را با `model=large` یا `lr=...` کامل توصیف نمی‌کنیم. حداقل run record باید این‌ها را پیوند دهد: شناسهٔ کد/commit و وضعیت تغییرات؛ hash نسخهٔ داده و split؛ tokenizer؛ config کامل؛ seed و RNG policy؛ نسخهٔ Python/framework/driver؛ precision؛ rank/world size و parallel axes؛ device/topology؛ زمان شروع/پایان؛ و artifactهای checkpoint، config، log و نمودار.

معیارهای مفید در طول آموزش می‌توانند train/validation loss، global step، valid tokens، گرادیان، tokens/sec، زمان صرف‌شده در communication/data/checkpoint، حافظهٔ peak، retry count و خطای آخر باشند. هر metric را با `step`، واحد و data split ثبت کنید. MLflow Tracking، برای نمونه، مفهوم run/experiment، پارامتر، metric و artifact دارد؛ مستندات جاری‌اش ذخیرهٔ محلی `mlruns` را در حالت پیش‌فرض شرح می‌دهد [۱۰]. ابزارهای دیگر هم ممکن‌اند؛ سرویس خارجی برای داده یا log حساس باید از نظر privacy، credential و دسترسی بررسی شود.

## ۱۶. مقایسهٔ runها را قابل‌تفسیر طراحی کنیم

برای فهم اثر sharding، batch یا recomputation یک سؤال ابطال‌پذیر بنویسید و baseline را حفظ کنید. اگر سه پیکربندی را مقایسه می‌کنید، یک جدول از config، seedها، نسخه‌ها، tokenهای مصرف‌شده، updateها، validation metric، throughput و checkpoint duration بسازید. مقایسهٔ «همان ۱۰۰۰ update» اگر هر update token متفاوتی دیده باشد، هم‌بودجه نیست.

از test نهایی برای انتخاب topology، checkpoint interval یا hyperparameter استفاده نکنید؛ مرز validation/test فصل ۴۳ و ۴۴ هنوز برقرار است. در اجراهای تصادفی چند seed می‌تواند پایداری را بهتر بسنجد؛ یک run خوب یا یک run شکست‌خورده به‌تنهایی توزیع نتیجه را نشان نمی‌دهد. تکرار کد با hash یکسان هم deterministic بودن GPU، collective و library را تضمین نمی‌کند.

## ۱۷. Snapshot هماهنگ در آموزش چندپردازه‌ای

برای resume توزیع‌شده، فقط `model.state_dict()` ممکن است کافی نباشد. state optimizer، scheduler/update، sampler و offset، RNG هر rank، scaler در صورت استفاده، config/precision، معیارهای ثبت‌شده و snapshot شاردشده باید با هم سازگار باشند. ساده‌ترین نقطهٔ امن اغلب پس از optimizer update و collectiveهای همان update است؛ ذخیره در میانهٔ accumulation یعنی گرادیان‌های جمع‌شده را هم باید ثبت یا آن window را آگاهانه کنار گذاشت.

PyTorch Distributed Checkpoint می‌تواند state را از چند rank به‌صورت چندفایلی ذخیره کند و در load، shardها را برای topology تازه reshard کند. این با یک `torch.save` روی rank 0 یکی نیست؛ همهٔ rankها و process group باید مطابق API مشارکت کنند. مستندات PyTorch 2.6 هشدار می‌دهد که برای state_dict ذخیره‌شده، backward compatibility میان نسخه‌های PyTorch تضمین نشده است [۸]. حتی اگر API reshard می‌کند، لازم نیست sampler، RNG یا semantics optimizer شما را خودکار به run جدید تبدیل کند.

## ۱۸. چه خطایی واقعاً قابل retry است؟

OOM ناشی از batch بزرگ، NaN ناشی از مسیر عددی، `rank` گم‌شده، timeout ارتباط، storage پر، host restart و ورودی خراب یک کلاس شکست نیستند. retry بی‌نهایت ممکن است همان خطا را تکرار و هزینه را افزایش دهد. error policy باید سقف retry، timeout، مسیر ذخیره، alert، رفتار بعد از شکست و تصمیم انسان را روشن کند.

`torchrun` می‌تواند پس از شکست workerها کل worker group را تا سقف `--max-restarts` دوباره راه‌اندازی کند و rank/world size را از محیط در اختیار script قرار دهد. اما راه‌اندازی processها خودش model/optimizer/data position را بازسازی نمی‌کند؛ برنامه باید checkpoint معتبر را load کند. در membership change، rank و `WORLD_SIZE` می‌توانند عوض شوند؛ sampler، global batch و برنامهٔ آموزش را دوباره بررسی کنید [۹].

## ۱۹. الگوی restart که run را خاموش و روشن نکند

یک workflow محتاطانه:

1. در شروع، run ID، config، کد/داده، نسخه‌ها و topology را ثبت کنید.
2. در مرزهای optimizer update، snapshot هماهنگ بنویسید؛ شناسهٔ update و world size را در metadata بگذارید.
3. هنگام signal یا خطای worker، run را `interrupted/failed` علامت بزنید؛ خروجی ناقص را `completed` ننامید.
4. پس از restart، checkpoint و hashها را validate کنید، سپس sampler/RNG و optimizer state را restore کنید.
5. اگر world size، داده، tokenizer، dtype یا config عوض شده، run تازه یا warm-start صریح بسازید؛ سکوتاً همان run ID را ادامه ندهید.
6. یک آزمایش قطع/ادامه روی fixture کوچک انجام دهید؛ پس از آن هم GPU/backend و storage هدف را جداگانه آزمایش کنید.

در صورت استفاده از snapshotهای چندبخشی، manifestی لازم است که همهٔ shardهای مورد انتظار، گام، hash و کامل‌شدن write را مشخص کند. فایل‌های ناقص را «latest» حساب نکنید. حفاظت داده، عمر نگهداری، رمزنگاری و مجوز دسترسی نیز بخش recovery هستند.

## ۲۰. فاصلهٔ ذخیره را با failure rate و هزینه بسنجیم

ذخیرهٔ هر update می‌تواند IO را زیاد کند؛ ذخیرهٔ خیلی کم‌تعداد، در خرابی کار بیشتری را از آخرین snapshot از دست می‌دهد. یک تقریب آموزشی، اگر زمان نوشتن snapshot برابر `C`، فاصلهٔ زمانی میان snapshotها `I` و نرخ شکست مستقل `λ` در واحد زمان باشد، سهم overhead را این‌گونه می‌نویسد:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="تقریب سهم سربار برابر زمان نوشتن checkpoint تقسیم بر فاصلهٔ checkpointها به‌علاوهٔ نرخ شکست ضربدر نصف فاصله است؛ این تقریب restart، هزینهٔ بازیابی و شکست‌های هم‌بسته را نادیده می‌گیرد">
  <mrow><mi>overhead</mi><mo>≈</mo><mfrac><mi>C</mi><mi>I</mi></mfrac><mo>+</mo><mfrac><mrow><mi>λ</mi><mi>I</mi></mrow><mn>2</mn></mfrac></mrow>
</math>

این تقریب فرض می‌کند شکست‌ها کم‌تعداد و مستقل‌اند، زمان write ثابت است، و شکست به‌طور میانگین نیمهٔ interval را از دست می‌دهد؛ زمان restart، contention ذخیره‌سازی و خرابی‌های correlated داخل آن نیست. برای نمونهٔ فرضی، `C=2 min`, `I=1 h`, `λ=0.01 /h`: سهم نوشتن حدود ۳٫۳٪ و اتلاف مورد انتظار حدود ۰٫۵٪ است. مقدار failure rate را از سابقهٔ job/storage خود بگیرید؛ این اعداد نسخهٔ همگانی برای هر cluster نیستند. در run واقعی checkpoint duration و bytes را هم به experiment tracker بفرستید.

## ۲۱. مشاهده‌پذیری: چه چیزی را در log جدا کنیم؟

لاگ کافی باید دست‌کم `run_id`, `rank`, `world_size`, `global_step`, `valid_tokens`, LR واقعی، loss/NLL با نام split، gradient norm، زمان هر جزء، checkpoint ID و restart count را همراه داشته باشد. هنگام profiling، latency و throughput را پس از warm-up و با synchronization مناسب accelerator اندازه بگیرید. برای تصمیم کیفیت، validation metric؛ برای ادعای نهایی، test فقط در پایان و طبق پروتکل.

در multi-rank logها را per-rank یا به‌صورت aggregate قابل‌ردیابی ذخیره کنید؛ فقط rank 0 را نوشتن به یک فایل مشترک بگذارید، مگر اینکه sink همگام و thread-safe داشته باشید. هشدار non-finite، نرخ رشد حافظه، rank lag و شکست write را alert کنید. log متن خام prompt، دادهٔ شخصی، token یا credential را بی‌دلیل ثبت نکند؛ run record مفید باید حداقل‌گرایانه و تحت کنترل دسترسی باشد.

## ۲۲. پروژهٔ CPU فصل را اجرا کنیم

پروژه در [`projects/46-scale-training/`](book-engineering/projects/46-scale-training/README.md) دو سازوکار قابل‌آزمون فراهم می‌کند و به GPU یا سرویس tracking احتیاج ندارد:

```bash
python book-engineering/projects/46-scale-training/scaling_lab.py \
  --output /tmp/ch46-scaling.json

(cd book-engineering/projects/46-scale-training && python -m unittest discover -v)
```

بخش activation، مدل feed-forward دو-block را با و بدون `checkpoint(..., use_reentrant=False)` اجرا می‌کند؛ خروجی، gradient ورودی و gradient پارامترها را تطبیق می‌دهد و با `saved_tensors_hooks` تعداد بایت tensorهای ثبت‌شده برای backward را می‌شمارد. بخش distributed دو process واقعی محلی با backend `gloo` می‌سازد؛ shardها ۳ و ۲ نمونه‌اند و گرادیان DDP با نسخهٔ تک‌پردازشی مقایسه می‌شود. CLI فایل JSON اختیاری می‌نویسد و fingerprint محتواییِ config، hash کد/fixture و نسخهٔ runtime را همراه گزارش می‌آورد.

ده آزمون قرارداد خروجی/گرادیان، بایت saved-tensor، `use_reentrant=False`, گرادیان DDP، وزن‌دهی shardهای نابرابر، hash و نوشتن JSON را بررسی می‌کنند. تست مرورگر و builder نیز کد پیوست را با فایل پروژه به‌صورت بایتی تطبیق می‌دهند.

## ۲۳. نتیجهٔ fixture و حد استنتاج

در Python 3.13 و PyTorch `2.6.0+cpu` محلی، ده آزمون پروژه موفق شدند. در شبکهٔ مصنوعی، بایت tensorهای نگه‌داری‌شده در hook از `4,016` به `688` رسید؛ بیشینهٔ اختلاف خروجی، gradient ورودی و gradient پارامترها `0` بود. این شمار فقط stateهای مشاهده‌شده توسط hook autograd همان fixture است؛ peak حافظه یا درصد صرفه‌جویی GPU نیست.

در probe دوپردازه‌ای، rankها به‌ترتیب ۳ و ۲ نمونه داشتند؛ DDP گرادیان `−33.0` داد و backward تک‌پردازشی نیز `−33.0` شد. این اجرای Gloo محلی نه benchmark شبکه است، نه آزمایش NCCL، و نه آموزش مدل زبان. fingerprint فقط برای تشخیص همان config/code/data در fixture است، نه امضای رمزنگاری‌شده یا اثبات provenance.

## ۲۴. برداشت‌های رایجی که باید اصلاح شوند

| برداشت | اصلاح |
|---|---|
| «Gradient checkpoint همان فایل resume است.» | activation recomputation و training-state snapshot زمان و هدف متفاوت دارند. |
| «DDP داده را بین rankها تقسیم می‌کند.» | DDP گرادیان را همگام می‌کند؛ sampler/input pipeline باید shard را بسازد. |
| «میانگین meanهای محلی همیشه mean global است.» | اگر شمار نمونه/token برابر نباشد، loss را متناسب با مخرج global وزن دهید. |
| «اضافه‌کردن GPU حافظهٔ یک مدل را جمع می‌کند.» | DDP معمولاً model state را replicate می‌کند؛ sharding راهبرد دیگری است. |
| «torchrun پس از restart از state درست ادامه می‌دهد.» | launcher workerها را restart می‌کند؛ script و checkpoint باید state معتبر را بازیابی کنند. |
| «یک fingerprint یعنی run دقیقاً تکرار می‌شود.» | hash هویت ورودی را کمک می‌کند؛ backend، نسخه و ترتیب floating point هنوز تفاوت دارند. |
| «tokens/s بیشتر یعنی مدل بهتر یا ارزان‌تر است.» | کیفیت، token budget، دقت، هزینه، setup و شرایط اندازه‌گیری را نیز گزارش کنید. |

## ۲۵. تمرین‌ها و معیار عبور

۱. دو rank به‌ترتیب ۳ و ۲ نمونه دارند. نشان دهید چرا `0.5 × (mean₀ + mean₁)` به‌طور کلی mean پنج نمونه نیست و ضریب loss محلی را برای DDP بنویسید.

۲. اگر microbatch برابر ۴، accumulation برابر ۳ و data-parallel replica برابر ۲ باشد، batch مؤثر تقریبی چند است؟ چه اطلاعاتی برای تبدیل آن به شمار valid token لازم است؟

۳. با یک مثال توضیح دهید activation checkpointing چه tensorی را بازسازی می‌کند و چه چیزی را برای resume باید در training-state checkpoint نگه داشت.

۴. از جدول فصل ۴۶ یک انتخاب برای OOM پارامتر، OOM activation و گلوگاه data loading بنویسید؛ برای هر کدام یک metric قابل‌اندازه‌گیری پیشنهاد دهید.

۵. snapshot چندپردازه‌ای را در گام ۲۰۰ بنویسید. چه تضمینی لازم است تا مدل، optimizer، sampler و RNG از یک نقطهٔ منطقی باشند؟ اگر world size از ۴ به ۸ تغییر کرد چه چیزهایی را بازبینی می‌کنید؟

۶. برای `C=90 s`, `I=30 min`, `λ=0.02/h`, دو جملهٔ محاسبهٔ تقریبی overhead را بسازید. فرض‌های این مدل ساده چیست و کدام هزینه‌ها جا افتاده‌اند؟

۷. برای run پنج‌گانه‌ای که فقط parallel strategy عوض می‌شود، config و metrics را فهرست کنید. کدام داده باید در run record باشد اما نباید raw text/prompt در آن ذخیره شود؟

۸. پروژه را اجرا کنید و بگویید چه چیزی را واقعاً می‌سنجد و چه ادعایی از آن نمی‌شود کرد. [پاسخ‌نامهٔ فصل ۴۶](book-engineering/answers/46-scale-training-fa.md).

**معیار عبور:** دست‌کم ۶ تمرین از ۸ با فرض و واحد درست؛ تشخیص تفاوت دو checkpoint؛ loss weighting صحیح برای shardهای نابرابر؛ run record با کد/داده/نسخه/config؛ و صریح‌بودن مرز بین fixture CPU و آموزش/benchmark چند GPU واقعی.

## ۲۶. منابع فنی و تاریخ بازبینی

مستندات اجرایی با PyTorch 2.6 pin شدند تا با پروژهٔ CPU کتاب قابل‌مقایسه باشند. API و رفتار نسخه‌های تازه ممکن است فرق کند؛ پیش از اجرا، نسخه و backend خود را دوباره بررسی کنید. عددهای مقاله فقط نتیجهٔ setup گزارش‌شده‌اند.

1. Chen, T., Xu, B., Zhang, C. & Guestrin, C. (2016), “Training Deep Nets with Sublinear Memory Cost,” arXiv:1604.06174v2. [مقاله](https://arxiv.org/abs/1604.06174). مبنای recomputation و معاملهٔ حافظه/محاسبه؛ نتیجه به graph و فرض‌های مطالعه محدود است.
2. PyTorch 2.6, [`torch.utils.checkpoint`](https://docs.pytorch.org/docs/2.6/checkpoint.html). تفاوت non-reentrant/reentrant، RNG state و بازاجرای forward.
3. PyTorch 2.6, [`DistributedDataParallel`](https://docs.pytorch.org/docs/2.6/generated/torch.nn.parallel.DistributedDataParallel.html). همگام‌سازی گرادیان، مسئولیت تقسیم داده، bucket و محدودیت ترکیب checkpoint.
4. PyTorch 2.6, [`torch.distributed`](https://docs.pytorch.org/docs/2.6/distributed.html). backendها، collectiveها و راهنمای Gloo/NCCL.
5. Rajbhandari, S. et al. (2019/2020), “ZeRO: Memory Optimizations Toward Training Trillion Parameter Models,” arXiv:1910.02054v3. [مقاله](https://arxiv.org/abs/1910.02054).
6. PyTorch 2.6, [FullyShardedDataParallel](https://docs.pytorch.org/docs/2.6/fsdp.html); DeepSpeed, [ZeRO tutorial](https://www.deepspeed.ai/tutorials/zero/). APIها و مثال‌های این راهنماها نسخه‌وابسته‌اند.
7. Shoeybi, M. et al. (2019/2020), “Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism,” arXiv:1909.08053v4. [مقاله](https://arxiv.org/abs/1909.08053).
8. PyTorch 2.6, [`torch.distributed.checkpoint`](https://docs.pytorch.org/docs/2.6/distributed.checkpoint.html). ذخیرهٔ چند rank، load-time resharding و نبود تضمین backward compatibility میان نسخه‌ها.
9. PyTorch 2.6, [`torchrun` (Elastic Launch)](https://docs.pytorch.org/docs/2.6/elastic/run.html). restart گروه worker، `--max-restarts` و semantics rank/world size.
10. MLflow, [Tracking documentation](https://mlflow.org/docs/latest/ml/tracking/), صفحهٔ جاری و بدون pin نسخه؛ مراجعهٔ ۶ نوامبر ۲۰۲۶. قابلیت‌های deployment و API ممکن است با نسخه تغییر کنند.
11. Korthikanti, V. et al. (2022), “Reducing Activation Recomputation in Large Transformer Models,” arXiv:2205.05198. [مقاله](https://arxiv.org/abs/2205.05198). نتیجهٔ selective recomputation متعلق به مدل/سخت‌افزار/تنظیمات همان مقاله است.

تاریخ مراجعه به مراجع: ۶ نوامبر ۲۰۲۶. بازشدن یک لینک یا وجود API، سازگاری آن با همهٔ deviceها را ثابت نمی‌کند.

## ۲۷. پیوست اجرایی: کد کامل آزمایشگاه

نسخهٔ زیر عیناً با [`scaling_lab.py`](book-engineering/projects/46-scale-training/scaling_lab.py) هم‌تراز است. اجرای پیوست همان smoke test دوپردازه‌ای CPU است؛ برای runهای GPU/cluster از مستندات نسخه‌دار و پروتکل عملیاتی استفاده کنید.

```python
"""CPU probes for activation rematerialization, DDP gradient reduction, and run identity.

This is a deterministic correctness fixture, not a speed or model-quality benchmark.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import tempfile
from datetime import timedelta
from pathlib import Path
from typing import Any

import torch
import torch.distributed as dist
import torch.multiprocessing as mp
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.checkpoint import checkpoint


SEED = 46
WORLD_SIZE = 2
INPUT_DIM = 8
HIDDEN_DIM = 16
OUTPUT_DIM = 4
BLOCKS = 2
_TIMEOUT = timedelta(seconds=45)


class ResidualBlock(nn.Module):
    """Small block whose intermediate tensors participate in backward."""

    def __init__(self) -> None:
        super().__init__()
        self.up = nn.Linear(INPUT_DIM, HIDDEN_DIM)
        self.down = nn.Linear(HIDDEN_DIM, INPUT_DIM)
        self.activation = nn.GELU()

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        return value + self.down(self.activation(self.up(value))) * 0.5


class ProbeNetwork(nn.Module):
    """A tiny network to compare ordinary and checkpointed autograd graphs."""

    def __init__(self) -> None:
        super().__init__()
        self.blocks = nn.ModuleList(ResidualBlock() for _ in range(BLOCKS))
        self.head = nn.Linear(INPUT_DIM, OUTPUT_DIM)

    def forward(self, value: torch.Tensor, *, rematerialize: bool = False) -> torch.Tensor:
        for block in self.blocks:
            if rematerialize:
                value = checkpoint(block, value, use_reentrant=False)
            else:
                value = block(value)
        return self.head(value)


def _max_abs(left: torch.Tensor, right: torch.Tensor) -> float:
    return float((left - right).abs().max().item())


def activation_checkpoint_probe(seed: int = SEED) -> dict[str, Any]:
    """Compare output/gradients and count tensors saved for backward hooks."""
    if seed < 0:
        raise ValueError("seed must be non-negative")
    torch.manual_seed(seed)
    reference = ProbeNetwork()
    rematerialized = ProbeNetwork()
    rematerialized.load_state_dict(reference.state_dict())
    inputs = torch.linspace(-1.0, 1.0, 5 * INPUT_DIM, dtype=torch.float32).reshape(5, INPUT_DIM)

    def run(model: ProbeNetwork, use_rematerialization: bool) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, int]:
        model.zero_grad(set_to_none=True)
        value = inputs.clone().requires_grad_(True)
        saved_bytes = 0

        def pack(tensor: torch.Tensor) -> torch.Tensor:
            nonlocal saved_bytes
            saved_bytes += tensor.numel() * tensor.element_size()
            return tensor

        with torch.autograd.graph.saved_tensors_hooks(pack, lambda tensor: tensor):
            output = model(value, rematerialize=use_rematerialization)
            output.square().mean().backward()
        parameter_gradients = torch.cat([
            parameter.grad.detach().reshape(-1)
            for parameter in model.parameters()
            if parameter.grad is not None
        ])
        return output.detach(), value.grad.detach(), parameter_gradients, saved_bytes

    base_out, base_input_grad, base_parameter_grad, base_saved = run(reference, False)
    check_out, check_input_grad, check_parameter_grad, check_saved = run(rematerialized, True)
    return {
        "seed": seed,
        "blocks": BLOCKS,
        "use_reentrant": False,
        "saved_tensor_bytes_baseline": base_saved,
        "saved_tensor_bytes_rematerialized": check_saved,
        "saved_tensor_ratio": check_saved / base_saved if base_saved else None,
        "max_abs_output_delta": _max_abs(base_out, check_out),
        "max_abs_input_gradient_delta": _max_abs(base_input_grad, check_input_grad),
        "max_abs_parameter_gradient_delta": _max_abs(base_parameter_grad, check_parameter_grad),
        "measurement_note": "autograd saved-tensor bytes only; not peak process/device memory or runtime",
    }


def _synthetic_data() -> tuple[torch.Tensor, torch.Tensor, tuple[tuple[int, ...], ...]]:
    features = torch.arange(1.0, 6.0, dtype=torch.float32).reshape(-1, 1)
    targets = 2.0 * features
    # Deliberately uneven shards exercise sample-count weighting: 3 + 2 = 5.
    shards = ((0, 1, 2), (3, 4))
    return features, targets, shards


def _ddp_worker(rank: int, world_size: int, rendezvous_file: str, result_file: str) -> None:
    """One Gloo CPU rank; called by multiprocessing spawn."""
    torch.set_num_threads(1)
    dist.init_process_group(
        backend="gloo",
        init_method=f"file://{rendezvous_file}",
        rank=rank,
        world_size=world_size,
        timeout=_TIMEOUT,
    )
    try:
        model = nn.Linear(1, 1, bias=False)
        with torch.no_grad():
            model.weight.fill_(0.5)
        distributed_model = DDP(model)

        features, targets, shards = _synthetic_data()
        indices = list(shards[rank])
        local_features = features[indices]
        local_targets = targets[indices]
        local_loss_sum = F.mse_loss(distributed_model(local_features), local_targets, reduction="sum")
        # DDP averages rank gradients. Scale local sums so the result is the
        # sample-weighted mean gradient, even though shard lengths differ.
        (local_loss_sum * world_size / len(features)).backward()

        if rank == 0:
            single_model = nn.Linear(1, 1, bias=False)
            with torch.no_grad():
                single_model.weight.fill_(0.5)
            global_loss = F.mse_loss(single_model(features), targets, reduction="mean")
            global_loss.backward()
            payload = {
                "backend": "gloo",
                "device": "cpu",
                "world_size": world_size,
                "global_sample_count": len(features),
                "local_sample_counts": [len(shard) for shard in shards],
                "ddp_gradient": float(distributed_model.module.weight.grad.item()),
                "single_process_reference_gradient": float(single_model.weight.grad.item()),
            }
            Path(result_file).write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        dist.barrier()
    finally:
        if dist.is_initialized():
            dist.destroy_process_group()


def distributed_gradient_probe() -> dict[str, Any]:
    """Run a real two-process CPU DDP all-reduce with the Gloo backend."""
    if dist.is_initialized():
        raise RuntimeError("the probe must run before another process group is initialized")
    if not dist.is_available() or not dist.is_gloo_available():
        raise RuntimeError("this PyTorch build does not include the Gloo backend")
    with tempfile.TemporaryDirectory(prefix="ch46-ddp-") as temporary:
        rendezvous_file = str(Path(temporary) / "rendezvous")
        result_file = str(Path(temporary) / "result.json")
        mp.spawn(
            _ddp_worker,
            args=(WORLD_SIZE, rendezvous_file, result_file),
            nprocs=WORLD_SIZE,
            join=True,
        )
        payload = json.loads(Path(result_file).read_text(encoding="utf-8"))
    payload["max_abs_gradient_delta"] = abs(
        payload["ddp_gradient"] - payload["single_process_reference_gradient"]
    )
    payload["measurement_note"] = "one synthetic gradient step; no GPU, network cluster, speed, or quality benchmark"
    return payload


def _data_sha256() -> str:
    features, targets, shards = _synthetic_data()
    content = {
        "features": features.reshape(-1).tolist(),
        "targets": targets.reshape(-1).tolist(),
        "shards": [list(shard) for shard in shards],
    }
    return hashlib.sha256(json.dumps(content, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run_fingerprint(config: dict[str, Any], code_sha256: str, data_sha256: str, runtime: dict[str, str]) -> str:
    """Content identity for this fixture; it is not a security signature."""
    payload = {
        "config": config,
        "code_sha256": code_sha256,
        "data_sha256": data_sha256,
        "runtime": runtime,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_report(seed: int = SEED) -> dict[str, Any]:
    if seed < 0:
        raise ValueError("seed must be non-negative")
    config = {
        "seed": seed,
        "network": {"input_dim": INPUT_DIM, "hidden_dim": HIDDEN_DIM, "output_dim": OUTPUT_DIM, "blocks": BLOCKS},
        "activation_checkpoint": {"enabled_for_probe": True, "use_reentrant": False},
        "distributed": {"backend": "gloo", "world_size": WORLD_SIZE, "device": "cpu"},
    }
    runtime = {
        "python_version": platform.python_version(),
        "torch_version": str(torch.__version__),
        "device": "cpu",
        "distributed_backend": "gloo",
    }
    code_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    data_sha256 = _data_sha256()
    return {
        "schema_version": 1,
        "config_fingerprint": run_fingerprint(config, code_sha256, data_sha256, runtime),
        "code_sha256": code_sha256,
        "data_sha256": data_sha256,
        "config": config,
        "runtime": runtime,
        "activation_checkpoint_probe": activation_checkpoint_probe(seed),
        "distributed_probe": distributed_gradient_probe(),
        "scope_note": "correctness and provenance fixture only; not training, a benchmark, or a production recovery system",
    }


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as handle:
            temporary_name = handle.name
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary_name, path)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--output", type=Path, help="optional JSON report path; no file is written by default")
    args = parser.parse_args(argv)
    report = build_report(args.seed)
    if args.output is not None:
        _atomic_write_json(args.output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
