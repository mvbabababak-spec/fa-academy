# برآورد منابع مدل‌های هوش مصنوعی: استنتاج، Fine-tuning و آموزش از صفر

> **جایگاه در نقشه:** فصل محلی ۸ از ۱۵ فصل جلد چهارم؛ فصل سراسری ۵۴. جلد چهارم طبق نقشهٔ راه ۱۵ فصل دارد.
>
> **مرز موضوعی:** فصل ۵۳ هزینهٔ محاسباتی تولید تصویر/ویدئو را به اجزا می‌شکست. این فصل روش حساب‌کردن حافظه و FLOPs را برای استنتاج، Fine-tuning و آموزش از صفر می‌آموزد؛ فهرست قطعات و طراحی آزمایشگاه موضوع فصل ۵۵ است و قیمت، بودجه و هزینهٔ مالکیت موضوع فصل ۵۶.
>
> **حد ادعا:** فرمول‌ها برآورد مرتبهٔ اول‌اند. پروژهٔ همراه فقط روی ورودی ساختگی حساب انجام می‌دهد؛ سخت‌افزار یا مدل واقعی را نمی‌سنجد و benchmark نیست. در این فصل هیچ فهرست قطعه، قیمت روز، تضمین جا شدن مدل یا توصیهٔ خریدی ارائه نمی‌شود.

## ۱. چرا پیش از انتخاب دستگاه باید صورت مسئله را بنویسیم؟

«مدل هفت‌میلیاردپارامتری» به‌تنهایی نیاز حافظه را تعیین نمی‌کند. استنتاج تک‌کاربره با دنبالهٔ کوتاه با سرو هم‌زمان چند ده گفتگو تفاوت دارد؛ تنظیم adapter با آموزش همهٔ وزن‌ها یکسان نیست؛ طول توالی، اندازهٔ micro-batch، dtype، روش attention، cache، optimizer و checkpointing همگی حساب را عوض می‌کنند.

هدف این فصل ساختن یک **دفترچهٔ فرض‌ها** است: هر عدد باید به مؤلفه‌ای روشن وصل باشد و معلوم باشد اندازه‌گیری شده، از مشخصات استخراج شده یا صرفاً برای مثال فرض شده است. اندازهٔ وزن‌ها، activationها، gradientها، حالت optimizer، cache، بافر موقت و ذخیره‌سازی را در یک عدد مبهم «حافظهٔ مدل» ادغام نکنید.

![شکل ۴-۸-۱: استنتاج، Fine-tuning و آموزش از صفر هرکدام دفتر حافظه و محاسبهٔ جدا دارند؛ وزن‌ها، KV cache، activation، gradient، optimizer، runtime و مرحلهٔ اجرای کوچک و اندازه‌گیری peak از هم تفکیک شده‌اند.](book-engineering/diagrams/v4-ch08-resource-estimation.svg)

## ۲. پیش از ضرب‌کردن، workload را مشخص کنید

برای هر سناریو ثبت کنید:

- **کار:** استنتاج، تنظیم کامل، adapter/LoRA، ادامهٔ پیش‌آموزش یا آموزش از صفر؛
- **معماری و پارامترها:** تعداد لایه‌ها، عرض پنهان، headهای query و KV، MoE یا dense، و تعداد پارامترهای یکتا؛
- **شکل ورودی:** batch یا تعداد درخواست‌های هم‌زمان، طول prompt، طول خروجی، طول زمینه و رزولوشن/تعداد فریم در کار چندوجهی؛
- **حالت عددی:** وزن، gradient، optimizer و KV cache ممکن است dtypeهای جدا داشته باشند؛
- **روش اجرا:** DDP یا شاردینگ، optimizer، attention backend، quantization، activation checkpointing و offload؛
- **قید هدف:** فقط جا شدن، زمان پاسخ، throughput، اندازهٔ batch یا تعداد کاربر هم‌زمان.

در مدل‌های Mixture-of-Experts، تعداد پارامترهای ذخیره‌شده با تعداد پارامترهای فعال در هر token یکی نیست: ظرفیت حافظه بیشتر به کل وزن‌های مستقر و هزینهٔ محاسبه به routing و expertهای فعال وابسته است. وزن‌های tied را دوبار نشمارید. اگر پیکربندی ناشناخته است، نتیجه را بازه یا چند سناریوی مشروط گزارش کنید، نه یک مقدار ظاهراً دقیق.

## ۳. GB با GiB یکی نیست

سازنده‌ها و ابزارها ممکن است از واحدهای متفاوت استفاده کنند. در این فصل GB ده‌دهی است و GiB دودویی:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="یک گیبی‌بایت برابر دو به توان سی بایت و تقریباً یک ممیز صفر هفتاد و چهار گیگابایت ده‌دهی است">
  <mrow><mn>1</mn><mtext> GiB</mtext><mo>=</mo><msup><mn>2</mn><mn>30</mn></msup><mtext> bytes</mtext><mo>≈</mo><mn>1.073742</mn><mtext> GB</mtext></mrow>
</math>

**متن جایگزین فرمول:** `1 GiB = 1,073,741,824 bytes ≈ 1.073742 GB`؛ پس عدد GB روی برچسب و GiB در گزارش ابزار را بی‌تبدیل مقایسه نکنید.

یک ترابایت ده‌دهی نیز با یک tebibyte برابر نیست. در کد پروژه، تعداد بایت اصل داده است و GB و GiB فقط دو نمایش کمکی‌اند. اگر واحد دقیق روشن نیست، پیش از نتیجه‌گیری آن را از مستندات همان ابزار یا سازنده تأیید کنید.

## ۴. کف حافظهٔ وزن‌ها را از تعداد پارامتر بگیرید

اگر مدل N پارامتر ذخیره کند و هر پارامتر به‌طور متوسط b وزن-بایت داشته باشد، کف نظری فضای وزن‌ها چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="حافظهٔ وزن‌ها تقریباً برابر تعداد پارامترهای ذخیره‌شده ضرب‌در بایت هر پارامتر است">
  <mrow><msub><mi>M</mi><mtext>weights</mtext></msub><mo>≈</mo><mi>N</mi><mo>×</mo><msub><mi>b</mi><mi>w</mi></msub></mrow>
</math>

**متن جایگزین فرمول:** `M_weights ≈ N × b_w` بایت؛ b_w اندازهٔ واقعیِ قالب ذخیره‌شده برای هر پارامتر است.

برای تخمین ابتدایی، FP32 چهار بایت، FP16/BF16 دو بایت، INT8 یک بایت و INT4 به‌صورت اسمی نیم‌بایت به‌ازای هر وزن دارند. در quantization چهار‌بیتی، بسته‌بندی، scale/zero-point، گروه‌بندی، tensorهای باقی‌مانده با دقت بالاتر و kernel مورد استفاده می‌توانند اندازهٔ واقعی را تغییر دهند؛ «چهاربیتی» مساوی تضمینی با `0.5 byte × N` روی دستگاه نیست. فایل checkpoint هم ممکن است نسخه‌ها یا metadataهایی داشته باشد که با footprint زمان اجرا یکی نیستند.

## ۵. آموزش، چهار دفتر متفاوت دارد

در آموزش، وزن‌ها فقط یکی از اجزای پایدارند. جداگانه بنویسید:

| مؤلفه | تقریب حسابی | نکته |
|---|---:|---|
| وزن‌های مدل | `N × b_w` | همهٔ وزن‌های موردنیاز forward؛ بخش منجمد هم حذف نمی‌شود |
| gradientها | `N_t × b_g` | `N_t` تعداد پارامترهای قابل‌آموزش است؛ dtype و نگه‌داری به پیاده‌سازی وابسته‌اند |
| کپی master | `N_t × b_m` | فقط اگر مسیر optimizer کپی دقت‌بالاتر نگه دارد |
| حالت optimizer | `N_t × b_o` | مثلاً دو moment از نوع FP32 در Adam هشت بایت برای پارامتر قابل‌آموزش می‌خواهند |

در نتیجهٔ ساده‌شده:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="حافظهٔ حالت‌های آموزش برابر وزن‌های همهٔ پارامترها به‌علاوهٔ gradient و master و optimizer برای پارامترهای قابل‌آموزش است">
  <mrow>
    <msub><mi>M</mi><mtext>states</mtext></msub><mo>≈</mo>
    <mi>N</mi><msub><mi>b</mi><mi>w</mi></msub><mo>+</mo>
    <msub><mi>N</mi><mi>t</mi></msub>
    <mo>(</mo><msub><mi>b</mi><mi>g</mi></msub><mo>+</mo><msub><mi>b</mi><mi>m</mi></msub><mo>+</mo><msub><mi>b</mi><mi>o</mi></msub><mo>)</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** `M_states ≈ N·b_w + N_t·(b_g + b_m + b_o)`؛ وزن پایه برای همهٔ پارامترها، اما gradient و optimizer برای پارامترهای قابل‌آموزش حساب می‌شوند.

این فرمول activationها، workspace، bufferهای ارتباطی، allocator و fragmentation را هنوز شامل نمی‌شود. ممکن است برخی tensorها فقط در بخشی از گام وجود داشته باشند؛ جمع مؤلفه‌ها یک accounting محافظه‌کارانه است، نه زمان‌بندی دقیق lifetime آن‌ها.

## ۶. چرا «بایت به‌ازای پارامتر» قانون ثابتی نیست؟

مستند Hugging Face برای یک نمونهٔ mixed-precision AdamW حدود ۱۸ بایت به‌ازای پارامتر، به‌علاوهٔ activationها را تجزیه می‌کند: وزن کم‌دقت به‌همراه کپی FP32، gradient چهار‌بایتی و دو moment هشت‌بایتی. این **پیکربندی نمونه** است، نه ثابت همهٔ مدل‌ها یا همهٔ optimizerها [۳]. در تنظیمی دیگر ممکن است کپی master حذف شود، gradientها دقت متفاوت داشته باشند، optimizer کم‌حافظه‌تر باشد، optimizer state تنبل تخصیص یابد یا پارامترهای زیادی frozen باشند.

برای نمونه، اگر مفروضات خودمان را `b_w=2`, `b_g=4`, `b_m=4`, `b_o=8` بگیریم، مدل کاملاً آموزش‌پذیر ۱۸ بایت حالت به‌ازای هر پارامتر می‌دهد. اگر gradientها دو‌بایتی فرض شوند، همان سطرها ۱۶ بایت می‌شوند. اعداد را از مستندات framework/optimizer و dtype واقعی استخراج کنید؛ از یک headline عددی به workload دیگر تعمیم ندهید. ZeRO نیز به‌جای حذف مؤلفه‌ها، افزونگیِ نگه‌داری آن‌ها میان رتبه‌ها را هدف می‌گیرد [۱].

## ۷. DDP حافظهٔ مدل را تقسیم نمی‌کند؛ شاردینگ می‌تواند

در data parallel معمولی، هر رتبه نسخه‌ای از وزن‌ها و optimizer state را نگه می‌دارد؛ gradientها میان رتبه‌ها همگام می‌شوند، اما اضافه‌کردن GPU به‌تنهایی حافظهٔ مدل روی هر GPU را بر تعداد رتبه‌ها تقسیم نمی‌کند. در خانوادهٔ ZeRO، به‌طور خلاصه، stage 1 optimizer state را، stage 2 علاوه بر آن gradientها را، و stage 3 علاوه بر هر دو پارامترها را shard می‌کند [۱].

برای حساب ایدئالِ هر رتبه، اگر `s_p`, `s_g`, `s_o` ضریب تقسیم وزن، gradient و حالت optimizer باشند، می‌توان نوشت:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="حافظهٔ حالت هر رتبه تقریباً برابر وزن بر ضریب تقسیم پارامتر به‌علاوهٔ gradient بر ضریب تقسیم gradient به‌علاوهٔ master و optimizer بر ضریب تقسیم حالت است">
  <mrow>
    <msub><mi>M</mi><mtext>states,rank</mtext></msub><mo>≈</mo>
    <mfrac><mi>N</mi><msub><mi>s</mi><mi>p</mi></msub></mfrac><msub><mi>b</mi><mi>w</mi></msub><mo>+</mo>
    <mfrac><msub><mi>N</mi><mi>t</mi></msub><msub><mi>b</mi><mi>g</mi></msub><msub><mi>s</mi><mi>g</mi></msub></mfrac><mo>+</mo>
    <mfrac><msub><mi>N</mi><mi>t</mi></msub><mo>(</mo><msub><mi>b</mi><mi>m</mi></msub><mo>+</mo><msub><mi>b</mi><mi>o</mi></msub><mo>)</mo><msub><mi>s</mi><mi>o</mi></msub></mfrac>
  </mrow>
</math>

**متن جایگزین فرمول:** `M_states,rank ≈ N·b_w/s_p + N_t·b_g/s_g + N_t·(b_m+b_o)/s_o`؛ در شاردینگ ایدئال، stage 1/2/3 به‌ترتیب حالت optimizer، سپس gradient و سپس پارامتر را بر تعداد رتبه‌ها تقسیم می‌کنند.

این رابطه فقط مدل حافظهٔ حالت است. all-gather/reduce-scatter، bucket، padding، پارامترهای ناهم‌اندازه، bufferهای موقت، ارتباط شبکه، CPU offload و رفتار نسخهٔ framework در آن نیست. بنابراین خروجی «حافظهٔ کافی برای اجرای واقعی» را اثبات نمی‌کند. Tensor/pipeline parallelism نیز هزینهٔ ارتباط و تقسیم متفاوتی دارد.

## ۸. Activationها: حافظه‌ای که با شکل batch و توالی تغییر می‌کند

برای محاسبهٔ gradient، مسیر backward به بخشی از خروجی‌های forward نیاز دارد. activation memory به micro-batch، طول دنباله، عرض پنهان، عمق، نوع attention و MLP، dtype، عملیات fused و این‌که autograd چه چیزی را نگه می‌دارد وابسته است. در بعضی مسیرهای attention، نگه‌داری ماتریس score کامل می‌تواند با طول دنباله به‌شکل درجه‌دو رشد کند؛ kernel حافظه‌بهینه ممکن است آن ماتریس را materialize نکند. پس یک tensor پنهان را در لایه‌ها ضرب‌کردن، حافظهٔ واقعی را به‌تنهایی پیش‌بینی نمی‌کند.

برای تمرین، پروژهٔ ما یک سناریوی **معادل‌های tensor پنهان** را حساب می‌کند: فرض می‌کنیم در هر لایه S tensor با ابعاد `microbatch × tokens × hidden` و b بایت برای هر عنصر ذخیره می‌شود:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="مرجع ساده‌شدهٔ فعال‌سازی برابر micro-batch ضرب‌در tokenها ضرب‌در عرض پنهان ضرب‌در لایه‌ها ضرب‌در شمار معادل tensorهای ذخیره‌شده ضرب‌در بایت هر عنصر است">
  <mrow>
    <msub><mi>M</mi><mtext>act,ref</mtext></msub><mo>=</mo>
    <mi>B</mi><mo>×</mo><mi>T</mi><mo>×</mo><mi>H</mi><mo>×</mo><mi>L</mi><mo>×</mo><mi>S</mi><mo>×</mo><mi>b</mi>
  </mrow>
</math>

**متن جایگزین فرمول:** `M_act,ref = B × T × H × L × S × b`؛ S فرض صریح کاربر است و «شمار activation واقعی مدل» محسوب نمی‌شود.

در fixture آموزشی، `B=1`, `T=4096`, `H=4096`, `L=32`, `S=4`, `b=2` به **۴ GiB** مرجع حسابی می‌رسد. این عدد را نه اندازه‌گیری و نه برآورد معتبر activation یک مدل واقعی بنامید؛ S برای همین مثال انتخاب شده است.

## ۹. Checkpointing و gradient accumulation کدام دفتر را کم می‌کنند؟

Activation checkpointing بخشی از activationها را به‌جای نگه‌داشتن، در backward دوباره محاسبه می‌کند؛ عموماً trade-off حافظه در برابر محاسبه و زمان است. PyTorch مستند می‌کند که checkpointed segment در backward دوباره اجرا می‌شود و حفظ RNG state نیز ممکن است سربار داشته باشد [۴]. صرف وجود این گزینه درصد ثابتی از حافظه را آزاد نمی‌کند؛ محل checkpoint، ساختار مدل و پیاده‌سازی را اندازه بگیرید.

Gradient accumulation چند micro-batch را پیش از update جمع می‌کند. این کار می‌تواند batch فیزیکی هر forward را کوچک نگه دارد و در نتیجه قلهٔ activation هر micro-step را پایین بیاورد؛ اما وزن‌ها و optimizer state را خودبه‌خود از هر رتبه حذف نمی‌کند. معادل‌بودن با batch بزرگ هم به scheduler، normalization، رفتار dropout و جزئیات optimizer وابسته است.

## ۱۰. Fine-tuning کامل در برابر LoRA و روش‌های adapter

در full fine-tuning تقریباً همهٔ وزن‌ها trainable هستند؛ بنابراین gradient و optimizer state روی بخش بزرگی از N حساب می‌شود. در LoRA، بخش بزرگی از وزن پایه frozen می‌ماند و `N_t` به تعداد پارامترهای adapter نزدیک می‌شود. در مدل معادله، این کار می‌تواند gradient، کپی master و optimizer state را برای بخش منجمد حذف کند؛ اما **وزن پایه هنوز باید در دسترس forward باشد** و فعالیت‌های لازم برای عبور gradient از لایه‌ها نیز ممکن است همچنان مهم باشند. بنابراین PEFT برابر «یک درصد از حافظهٔ کل» نیست.

QLoRA و quantization می‌توانند footprint وزن پایه را کاهش دهند، اما metadata، dequantization، activationها و kernel/runtime باید جداگانه بررسی شوند. دستورالعمل Hugging Face برای PEFT نیز freezeکردن پایه و کاهش stateهای قابل‌آموزش را توضیح می‌دهد؛ نه حذف مدل پایه از محاسبه [۵]. در این فصل هیچ مدل واقعی یا adapter آموزش داده نمی‌شود.

## ۱۱. استنتاج: وزن‌ها به‌علاوهٔ KV cache و فضای اجرا

در استنتاج، معمولاً optimizer state و gradient آموزشی نداریم؛ اما باید وزن‌ها، cache، tensorهای موقت، runtime و حاشیهٔ اطمینان را جا بدهیم:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="حافظهٔ استنتاج تقریباً برابر وزن‌ها به‌علاوهٔ KV cache به‌علاوهٔ workspace و runtime به‌علاوهٔ حاشیهٔ ایمنی است">
  <mrow>
    <msub><mi>M</mi><mtext>infer</mtext></msub><mo>≈</mo>
    <msub><mi>M</mi><mtext>weights</mtext></msub><mo>+</mo>
    <msub><mi>M</mi><mtext>KV</mtext></msub><mo>+</mo>
    <msub><mi>M</mi><mtext>runtime/temp</mtext></msub><mo>+</mo>
    <msub><mi>M</mi><mtext>margin</mtext></msub>
  </mrow>
</math>

**متن جایگزین فرمول:** `M_infer ≈ M_weights + M_KV + M_runtime/temp + M_margin`؛ اجزای آخر باید با workload و اندازه‌گیری همان محیط تعیین شوند.

KV cache در decode علّی، key و value قبلی را برای استفادهٔ مجدد نگه می‌دارد. برای cache متراکمِ decoder معمولی، تخمین مرتبهٔ اول چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="اندازهٔ KV cache تقریباً دو ضرب‌در لایه‌ها ضرب‌در batch فعال ضرب‌در طول زمینه ضرب‌در تعداد KV head ضرب‌در بُعد head ضرب‌در بایت هر عنصر است">
  <mrow>
    <msub><mi>M</mi><mtext>KV</mtext></msub><mo>≈</mo><mn>2</mn><mo>×</mo><mi>L</mi><mo>×</mo><mi>B</mi><mo>×</mo><mi>T</mi><mo>×</mo><msub><mi>H</mi><mtext>KV</mtext></msub><mo>×</mo><msub><mi>d</mi><mi>head</mi></msub><mo>×</mo><msub><mi>b</mi><mtext>KV</mtext></msub>
  </mrow>
</math>

**متن جایگزین فرمول:** `M_KV ≈ 2 × L × B × T × H_KV × d_head × b_KV` بایت؛ عامل ۲ برای K و V است.

T باید با سقف یا طول واقعی prompt به‌علاوهٔ tokenهای تولیدی سازگار باشد؛ B تعداد sequenceهای هم‌زمان است. در Multi-Query/Grouped-Query attention، `H_KV` از headهای query کمتر است و همین تعداد headهای KV را در فرمول می‌آوریم. Sliding-window، cache کوانتیزه، offload، cacheهای مدل‌های state-space و پیاده‌سازی‌های خاص به اصلاح فرمول نیاز دارند. مستندات Transformers بین cache پویا، ثابت، کوانتیزه و offloaded تفاوت می‌گذارد؛ انتخاب‌ها trade-off حافظه/سرعت دارند [۶].

## ۱۲. مثال استنتاج با ابعاد فرضی

برای شکل ساختگیِ fixture ــ `N=7.035B`, وزن دو‌بایتی، ۳۲ لایه، batch چهار، ۸۱۹۲ token، هشت KV head، بعد head برابر ۱۲۸ و cache دو‌بایتی ــ وزن‌ها **۱۴٫۰۷ GB ده‌دهی** و cache برابر **۴ GiB** می‌شود. جمع همین دو قلم **۱۸٫۳۶۴۹۶۷ GB** یا **۱۷٫۱۰۳۷۰۹ GiB** است.

این جمع عمدیْ فقط وزن‌ها و KV را دارد: fixture برای runtime، workspace و safety reserve صفر گذاشته است. بنابراین ۱۷٫۱۰ GiB را نباید با ظرفیت واقعی دستگاه مقایسه و نتیجه گرفت که «مدل حتماً جا می‌شود». ظرفیت قابل‌استفاده از کل حافظهٔ تبلیغی کمتر می‌تواند باشد؛ cache پویا/ثابت، processهای دیگر و bufferها نیز مؤثرند. افزوده‌شدن درخواست هم‌زمان، context یا طول خروجی، KV را تغییر می‌دهد.

## ۱۳. محاسبهٔ آموزشی: FLOPs بدون ادعای زمان اجرا

برای Transformer متراکم، یک قرارداد مرتبهٔ اول برای آموزش این است که forward حدود `2ND` و backward حدود `4ND` FLOPs داشته باشد؛ پس:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="تقریب FLOPs آموزش برابر شش ضرب‌در تعداد پارامترها ضرب‌در تعداد tokenهای دیده‌شده است">
  <mrow><mi>C</mi><mo>≈</mo><mn>6</mn><mo>×</mo><mi>N</mi><mo>×</mo><mi>D</mi></mrow>
</math>

**متن جایگزین فرمول:** `C_train ≈ 6 × N × D` FLOPs؛ N پارامترها و D تعداد tokenهای پردازش‌شده‌اند.

این تقریب با تحلیل FLOPs پیوست F مقالهٔ Hoffmann و همکاران تطبیق دارد؛ خود مقاله نیز مقایسهٔ محاسبهٔ خود را با قرارداد `6ND` گزارش می‌کند [۲]. attention با دنبالهٔ بلند، padding، embedding، MoE، activation recomputation، optimizer، evaluation، تعداد epochها و کارایی kernel می‌توانند محاسبهٔ واقعی را تغییر دهند. برای نمونه، `7B` پارامتر و `140B` token فقط در این قرارداد برابر **`5.88 × 10²¹` FLOPs** می‌شود؛ نه زمان آموزش، هزینه، کیفیت یا benchmark.

داده/پارامتر بهینه برای یک هدف کیفیت و compute خاص مسئلهٔ تجربی است؛ نتیجهٔ Chinchilla دربارهٔ تخصیص compute-optimal در setup آن مقاله است، نه نسخهٔ عمومی «همیشه فلان تعداد token به‌ازای پارامتر» [۲]. برای Fine-tuning هم D را تعداد tokenهای واقعاً پردازش‌شده ــ نه شمار ردیف‌های dataset ــ تعریف کنید و مشخص کنید padding و تکرار داده چطور شمرده شده‌اند.

## ۱۴. FLOPs استنتاج: prompt و decode را از هم جدا ببینید

برای لایه‌های خطی متراکم، forward روی هر token مرتبهٔ `2N` FLOPs دارد. بنابراین یک جمع‌بندی ساده برای prompt و خروجی چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="FLOPs خطی استنتاج تقریباً دو ضرب‌در پارامترها ضرب‌در batch ضرب‌در مجموع tokenهای prompt و tokenهای تولیدشده است">
  <mrow><msub><mi>C</mi><mtext>linear,infer</mtext></msub><mo>≈</mo><mn>2</mn><mo>×</mo><mi>N</mi><mo>×</mo><mi>B</mi><mo>×</mo><mo>(</mo><msub><mi>T</mi><mtext>prompt</mtext></msub><mo>+</mo><msub><mi>T</mi><mtext>generated</mtext></msub><mo>)</mo></mrow>
</math>

**متن جایگزین فرمول:** `C_linear,infer ≈ 2 × N × B × (T_prompt + T_generated)`؛ این فقط تقریب بخش‌های خطی است.

در prefill، attention روی توالی prompt نیز هزینه دارد و برای attention متراکم می‌تواند با طول توالی به مرتبهٔ درجه‌دو برسد؛ در decode، cache باعث می‌شود کل prompt از نو محاسبه نشود، ولی tokenها همچنان ترتیبی تولید می‌شوند. ضرب FLOPs به peak FLOPs سخت‌افزار تقسیم‌کردن، به‌تنهایی latency را به دست نمی‌دهد.

## ۱۵. Compute bound یا bandwidth bound؟

یک کرنل ممکن است با ظرفیت محاسبات محدود شود یا با سرعت جابه‌جایی داده. مدل roofline ساده، حد پایین زمانی را از بیشینهٔ زمان حساب FLOPs و زمان جابه‌جایی بایت‌ها می‌سازد:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="حد پایین زمان برابر بیشینهٔ FLOPs تقسیم بر نرخ محاسبهٔ مؤثر و بایت‌های جابه‌جاشده تقسیم بر پهنای‌باند مؤثر است">
  <mrow><msub><mi>t</mi><mtext>lower</mtext></msub><mo>=</mo><mi>max</mi><mo>(</mo><mfrac><mi>F</mi><msub><mi>P</mi><mtext>eff</mtext></msub></mfrac><mo>,</mo><mfrac><mi>Q</mi><msub><mi>B</mi><mtext>eff</mtext></msub></mfrac><mo>)</mo></mrow>
</math>

**متن جایگزین فرمول:** `t_lower = max(F / P_eff, Q / B_eff)`؛ F FLOPs، Q بایت ترافیک، P_eff نرخ محاسبه و B_eff پهنای‌باند مؤثر است.

این فقط حد پایینِ یک مدل ساده است. `P_eff` و `B_eff` باید برای workload و kernel نزدیک به اجرای هدف سنجیده شوند؛ نرخ تبلیغی peak را نرخ پایدار واقعی فرض نکنید. تأخیر شبکه، synchronization، launch، tokenizer، dataloader، cache miss، شکل ماتریس، اندازهٔ batch و رقابت با process دیگر در این یک خط ظاهر نمی‌شوند. راهنمای CUDA انویدیا نیز توصیه می‌کند کارایی و پهنای‌باند مؤثر اندازه‌گیری شوند و optimization چرخه‌ای از ارزیابی و سنجش باشد [۷].

## ۱۶. دفترچهٔ کل workload؛ فقط VRAM را جمع نزنید

| دفتر | مثال مؤلفه‌ها | پرسشی که باید پاسخ دهید |
|---|---|---|
| حافظهٔ شتاب‌دهنده | وزن، gradient، optimizer، activation، KV، workspace | کدام tensorها هم‌زمان در peak زنده‌اند؟ |
| RAM میزبان | dataloader، offload، staging، بارگذاری checkpoint | داده از کجا می‌آید و چه چیزی در CPU نگه داشته می‌شود؟ |
| ذخیره‌سازی | checkpoint، dataset، cache، نسخه‌های قبلی | checkpoint شامل optimizer state هست یا فقط وزن؟ |
| compute | forward/backward، تعداد token/step، recomputation | چه تعداد FLOPs و با چه نرخ مؤثری؟ |
| انتقال داده | PCIe/شبکه، all-reduce، gather/scatter | مدل یا optimizer میان کدام دستگاه‌ها جابه‌جا می‌شود؟ |

فصل حاضر اندازهٔ قطعه یا قیمت را انتخاب نمی‌کند. پس از ساختن همین دفترچه، فصل ۵۵ به طراحی آزمایشگاه و فصل ۵۶ به مقایسهٔ بودجه و هزینهٔ مالکیت می‌پردازند.

## ۱۷. روش عملی: از کاغذ تا اجرای آزمایشی

۱. با نسخه و پیکربندی ثابت، N، dtypeها، optimizer، trainable params، طول توالی، batch/هم‌زمانی و روش شاردینگ را ثبت کنید.
۲. مؤلفه‌های پایدار را جدا حساب کنید: وزن، gradient، master، optimizer و KV cache.
۳. activation و temporary را به‌صورت سناریوی شفاف اضافه کنید؛ اگر ضریب معلوم نیست، بازه یا unknown بنویسید.
۴. تعداد tokenها و قرارداد FLOPs را ثبت کنید؛ تبدیل FLOPs به زمان را فقط با نرخ مؤثر سنجیده‌شده انجام دهید.
۵. پیش از workload کامل، روی همان مدل و software stack یک forward/backward/optimizer step یا درخواست inference با بدترین ورودی مورد انتظار اجرا کنید.
۶. قله را در مرزهای یکسان اندازه بگیرید؛ warm-up، synchronization و reset peak counter را مستند کنید. PyTorch بین حافظهٔ tensorهای تخصیص‌یافته و حافظهٔ نگه‌داشته‌شده توسط caching allocator تمایز می‌گذارد؛ `memory_allocated`, `max_memory_allocated`, `memory_reserved` و سطح دستگاه پاسخ‌های یکسانی نمی‌دهند [۸].
۷. نسخهٔ framework/driver، GPU، dtype، batch، طول prompt/output، attention backend، checkpointing، optimizer و concurrency را کنار هر اندازه‌گیری ذخیره کنید. یک سناریوی موفق را به شکل‌های ورودی دیگر تعمیم ندهید.

در تخمین اولیه، فضای باقی‌مانده‌ای برای بافرها، تغییر طول ورودی، processهای دیگر و خطای برآورد در نظر بگیرید. حاشیه را به‌عنوان ورودی صریح ثبت کنید؛ یک درصد ثابت برای همهٔ مدل‌ها و runtimeها وجود ندارد. خطای OOM یا افت throughput را هم به مشاهدهٔ همان نسخه و workload وصل کنید، نه نتیجه‌ای عمومی.

## ۱۸. خروجی پروژه و مرز نتیجهٔ آن

`projects/54-resource-estimation/` یک برنامهٔ Python استاندارد دارد که fixture را با schema محدود اعتبارسنجی می‌کند، SHA-256 می‌سازد، اجزای حافظه را جدا چاپ می‌کند، محاسبهٔ ایدئال stageهای ZeRO را نشان می‌دهد، FLOPs مرتبهٔ اول را می‌شمارد و GB/GiB را جدا گزارش می‌کند. چهار profile آن فرضی‌اند: GQA برای cache، آموزش همهٔ پارامترها، adapter با تعداد trainable کمتر، و شاردینگ ایدئال stage 3 روی چهار رتبه.

اجرای ثبت‌شده روی Python 3.13.16، fixture با SHA-256 برابر `9648418ea1cd039a5554d489d79e5d688314240f7c254d2d5215d03e372a4a57` و **۴۵/۴۵ آزمون unit موفق** داشت. از خروجی‌های سناریوی آموزشی: inference با وزن و KV برابر `18.364967 GB` (runtime و margin صفر در fixture)، full training با مرجع activation برابر `130.924967 GB` در هر رتبه، adapter برابر `18.924967 GB` و stage 3 چهاررتبه‌ای برابر `35.952467 GB` در هر رتبه. مقادیر آموزش شامل مرجع activation ساختگی‌اند؛ نه اجرا، نه benchmark و نه اندازه‌گیری حافظه نیستند. فایل‌های کامل خروجی در `projects/54-resource-estimation/results.json` و فرمان/محدودیت‌ها در README پروژه ثبت شده‌اند.

آزمون‌ها حساب بایت، واحدها، KV cache، activation reference، trainable subset، sharding، FLOPs، roofline، اعتبار fixture، CLI و ثبات خروجی را بررسی می‌کنند. آن‌ها کیفیت مدل واقعی، فارسی، سرعت، سخت‌افزار، مصرف برق، هزینه یا امکان اجرای workload روی GPU مشخص را نمی‌آزمایند.

## ۱۹. تمرین‌ها

۱. مدلی با ۷ میلیارد پارامتر را با وزن BF16 و سپس INT8 حساب کنید. وزن‌ها چند GB ده‌دهی و چند GiB دودویی می‌شوند؟ چرا مقدار INT8 را footprint قطعی روی GPU نمی‌دانید؟

۲. برای `L=32`, `B=4`, `T=8192`, `H_KV=8`, `d_head=128`, `b_KV=2` حافظهٔ cache را محاسبه کنید. اگر batch دوبرابر شود، با ثابت‌ماندن بقیه چه تغییری رخ می‌دهد؟

۳. در مثال `N=7.035B` و مفروضات `b_w=2`, `b_g=4`, `b_m=4`, `b_o=8`, حافظهٔ حالت‌ها را برای full fine-tuning حساب کنید. activation و runtime را فعلاً جدا نگه دارید.

۴. همان N را نگه دارید، اما فقط ۳۵ میلیون پارامتر را trainable فرض کنید. کدام اجزا کم می‌شوند و کدام‌ها در حساب باقی می‌مانند؟ این پاسخ چرا «حافظه یک‌دویستم شد» را ثابت نمی‌کند؟

۵. با فرض‌های پرسش ۳، مدل کاملاً trainable و چهار rank را در ZeRO stage 2 حساب کنید. وزن‌ها چه‌طور تقسیم می‌شوند؟ کدام stateها بر چهار تقسیم می‌شوند؟ بافرهای ارتباطی را کجا ثبت می‌کنید؟

۶. با قرارداد `C≈6ND`, برای `N=7B` و `D=140B` تعداد FLOPs را بیابید. فهرست کنید دست‌کم چهار چیز را که از این عدد به‌تنهایی نمی‌دانید.

۷. برای استنتاج batch چهار، prompt با ۴۰۹۶ token و خروجی ۱۰۲۴ token و N=7B، FLOPs خطی تقریبی را حساب کنید. بگویید چرا این مقدار latency واقعی نیست و کدام بخش attention در آن ساده‌سازی شده است.

۸. برای کاهش peak activation، دو روش پیشنهاد کنید و توضیح دهید هرکدام کدام دفتر را کم می‌کند و چه trade-off یا شرطی دارد.

۹. یک پروتکل کوتاه برای سنجش واقعی peak حافظه بنویسید که تفاوت allocated و reserved را رعایت کند. چه metadataهایی باید کنار نتیجه بماند؟

۱۰. یک گزارش می‌گوید «مدل 8B با چهار GPU حتماً جا می‌شود، چون هر GPU یک‌چهارم دارد». با توجه به DDP، ZeRO، KV cache و workspace، این ادعا چه اطلاعاتی کم دارد؟

پاسخ‌های تشریحی مستقل در [`پاسخ‌نامهٔ فصل ۵۴`](book-engineering/answers/54-resource-estimation-fa.md) آمده‌اند.

## ۲۰. جمع‌بندی

برآورد مفید از نام مدل یا یک قاعدهٔ ثابتِ byte/parameter شروع نمی‌شود؛ از workload و فرض‌های ثبت‌شده شروع می‌شود. وزن‌ها، gradient، master، optimizer، activation، KV، workspace و حاشیهٔ اطمینان را جدا حساب کنید. Fine-tuning منجمد ممکن است optimizer state را کم کند، اما وزن پایه و بخش‌هایی از forward/activation باقی می‌مانند. Data parallel مدل را خودبه‌خود shard نمی‌کند؛ ZeRO stageها اجزای متفاوتی از state را تقسیم می‌کنند و هزینهٔ ارتباطی/موقت دارند.

`6ND`, `2N` به‌ازای token و رابطهٔ roofline ابزارهای تقریب‌اند، نه benchmark یا زمان اجرای قطعی. پس از برآورد، workload واقعی را در محیط هدف با همان ورودی و نسخه اندازه بگیرید. فصل بعد از حساب اجزا به طراحی آزمایشگاه، حافظه و زیرساخت می‌رود؛ قیمت و هزینهٔ مالکیت در فصل ۵۶ بررسی خواهد شد.

## ۲۱. منابع و تاریخ بازبینی

**لینک‌ها و نسخه‌های مستندات در ۶ نوامبر ۲۰۲۶ بازبینی شدند.** ضرایب تقریبی در متن به مؤلفه‌های همان منبع و محدودهٔ آزمایش آن مقیدند.

۱. Rajbhandari, S., Rasley, J., Ruwase, O., و He, Y. “ZeRO: Memory Optimizations Toward Training Trillion Parameter Models.” arXiv:1910.02054, نسخهٔ ۳ مورخ ۱۳ مهٔ ۲۰۲۰؛ مقاله دربارهٔ partitioning optimizer state، gradient و parameter. <https://arxiv.org/abs/1910.02054>

۲. Hoffmann, J. و همکاران. “Training Compute-Optimal Large Language Models.” NeurIPS 2022, arXiv:2203.15556, ۲۹ مارس ۲۰۲۲؛ Appendix F دربارهٔ تقریب FLOPs و مقایسه با `6ND`. <https://arxiv.org/abs/2203.15556>

۳. Hugging Face Transformers. “Model training anatomy.” مستند نسخهٔ 4.47.1؛ نمونهٔ accounting mixed-precision AdamW و جداسازی وزن/optimizer/gradient/activation/temporary. <https://huggingface.co/docs/transformers/v4.47.1/en/model_memory_anatomy>

۴. PyTorch. “torch.utils.checkpoint.” مستند نسخهٔ 2.15.0؛ آخرین به‌روزرسانی صفحه ۲۷ ژوئیهٔ ۲۰۲۶. <https://docs.pytorch.org/docs/2.15/checkpoint.html>

۵. Hugging Face Transformers. “Methods and tools for efficient training on a single GPU.” نسخهٔ 4.42.0؛ بخش PEFT/LoRA و اجزای باقی‌ماندهٔ حافظه. <https://huggingface.co/docs/transformers/v4.42.0/perf_train_gpu_one>

۶. Hugging Face Transformers. “Cache strategies.” نسخهٔ 5.22.1؛ cache پویا، ثابت، quantized و offload، و محدودیت معماری‌های خاص. <https://huggingface.co/docs/transformers/v5.22.1/en/kv_cache>

۷. NVIDIA. “CUDA C++ Best Practices Guide.” نسخهٔ جاری مستند آنلاین 13.5 هنگام بازبینی؛ bandwidth مؤثر و چرخهٔ assess/profile/optimize. <https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/>

۸. PyTorch. “CUDA semantics.” مستند نسخهٔ 2.15.0؛ آخرین به‌روزرسانی صفحه ۵ سپتامبر ۲۰۲۶، بخش caching allocator و سنجه‌های allocated/reserved. <https://docs.pytorch.org/docs/2.15/notes/cuda.html>

۹. Pope, R. و همکاران. “Efficiently Scaling Transformer Inference.” arXiv:2211.05102, ۹ نوامبر ۲۰۲۲؛ تحلیل وزن‌ها، KV cache، context، batch و محدودیت‌های استنتاج. <https://arxiv.org/abs/2211.05102>

## ۲۲. پیوست اجرایی: کد آزموده‌شدهٔ پروژه

این پیوست با `projects/54-resource-estimation/resource_estimator.py` یکسان است؛ برنامه فقط با کتابخانهٔ استاندارد Python کار می‌کند و هیچ GPU یا مدل واقعی را بارگذاری نمی‌کند.

```python
"""First-order, configuration-driven estimates for model memory and FLOPs.

The module performs arithmetic on an explicitly synthetic fixture. It does not
load a model, inspect a GPU, train, benchmark, or predict real-world quality.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_FIXTURE = Path(__file__).with_name("sample_profiles.json")
BYTES_PER_GB = 1_000_000_000
BYTES_PER_GIB = 1024**3
SCHEMA_VERSION = 1


class EstimationInputError(ValueError):
    """Raised when a workload profile is malformed or outside the model."""


def _integer(name: str, value: Any, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise EstimationInputError(f"{name} must be an integer >= {minimum}")
    return value


def _number(name: str, value: Any, *, minimum: float = 0.0) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EstimationInputError(f"{name} must be a finite number >= {minimum}")
    if isinstance(value, float) and not math.isfinite(value):
        raise EstimationInputError(f"{name} must be a finite number >= {minimum}")
    if value < minimum:
        raise EstimationInputError(f"{name} must be a finite number >= {minimum}")
    return value


def _normalize(value: int | float) -> int | float:
    if isinstance(value, float) and math.isfinite(value) and value.is_integer():
        return int(value)
    return value


def _scaled(count: int, bytes_per_item: int | float) -> int | float:
    return _normalize(count * bytes_per_item)


def _divided(value: int | float, divisor: int) -> int | float:
    return _normalize(value / divisor)


def byte_units(byte_count: int | float) -> dict[str, int | float]:
    """Return bytes plus decimal GB and binary GiB; GB and GiB are not equal."""
    count = _number("byte_count", byte_count)
    return {
        "bytes": _normalize(count),
        "decimal_GB": round(count / BYTES_PER_GB, 6),
        "binary_GiB": round(count / BYTES_PER_GIB, 6),
    }


def _require_mapping(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EstimationInputError(f"{name} must be an object")
    return value


def estimate_kv_cache(
    *,
    layers: int,
    active_sequences: int,
    context_tokens: int,
    kv_heads: int,
    head_dim: int,
    bytes_per_element: int | float,
) -> int | float:
    """Estimate uncompressed K and V storage for a decoder KV cache.

    The estimate is 2 * layers * batch * tokens * KV-heads * head-dimension
    * bytes-per-element. It is not applicable unchanged to every architecture.
    """
    layer_count = _integer("layers", layers, minimum=1)
    batch = _integer("active_sequences", active_sequences)
    tokens = _integer("context_tokens", context_tokens)
    key_value_heads = _integer("kv_heads", kv_heads, minimum=1)
    dimension = _integer("head_dim", head_dim, minimum=1)
    element_bytes = _number("bytes_per_element", bytes_per_element, minimum=0.000001)
    return _normalize(
        2 * layer_count * batch * tokens * key_value_heads * dimension * element_bytes
    )


def estimate_activation_reference(
    *,
    microbatch: int,
    sequence_tokens: int,
    hidden_size: int,
    layers: int,
    saved_tensors_per_layer: int,
    bytes_per_element: int | float,
) -> int | float:
    """Count a declared number of hidden-state-sized activation equivalents.

    This deliberately transparent scenario is not a framework-level prediction
    of actual activation memory. Attention, MLP intermediates, rematerialization,
    fusion, tensor layouts, and implementation details can change the peak.
    """
    batch = _integer("microbatch", microbatch, minimum=1)
    tokens = _integer("sequence_tokens", sequence_tokens, minimum=1)
    width = _integer("hidden_size", hidden_size, minimum=1)
    layer_count = _integer("layers", layers, minimum=1)
    saved_count = _integer("saved_tensors_per_layer", saved_tensors_per_layer)
    element_bytes = _number("bytes_per_element", bytes_per_element, minimum=0.000001)
    return _normalize(batch * tokens * width * layer_count * saved_count * element_bytes)


def estimate_inference(
    *,
    model_parameters: int,
    weight_bytes_per_parameter: int | float,
    kv_cache_bytes: int | float = 0,
    runtime_and_temporary_bytes: int | float = 0,
    safety_bytes: int | float = 0,
) -> dict[str, Any]:
    """Add explicitly supplied inference memory components for one device."""
    parameters = _integer("model_parameters", model_parameters, minimum=1)
    weight_size = _number("weight_bytes_per_parameter", weight_bytes_per_parameter)
    kv_size = _number("kv_cache_bytes", kv_cache_bytes)
    runtime_size = _number("runtime_and_temporary_bytes", runtime_and_temporary_bytes)
    margin = _number("safety_bytes", safety_bytes)

    weights = _scaled(parameters, weight_size)
    total = weights + kv_size + runtime_size + margin
    return {
        "kind": "inference_memory",
        "model_weights": byte_units(weights),
        "kv_cache": byte_units(kv_size),
        "runtime_and_temporary": byte_units(runtime_size),
        "safety_reserve": byte_units(margin),
        "total_estimate": byte_units(total),
        "scope": "configured arithmetic; not a device-fit guarantee",
    }


def estimate_training(
    *,
    model_parameters: int,
    trainable_parameters: int,
    weight_bytes_per_parameter: int | float,
    gradient_bytes_per_trainable_parameter: int | float,
    master_weight_bytes_per_trainable_parameter: int | float,
    optimizer_state_bytes_per_trainable_parameter: int | float,
    world_size: int = 1,
    zero_stage: int = 0,
    activation_model: dict[str, Any] | None = None,
    activation_bytes_override: int | float | None = None,
    temporary_bytes: int | float = 0,
    safety_bytes: int | float = 0,
) -> dict[str, Any]:
    """Estimate per-rank model-state and declared non-state memory.

    ``zero_stage`` uses idealized ZeRO divisors: stage 1 partitions optimizer
    state/master copies, stage 2 additionally partitions gradients, and stage 3
    additionally partitions parameters. Communication/all-gather buffers,
    padding, fragmentation, and framework-specific behavior are not modelled.
    """
    parameters = _integer("model_parameters", model_parameters, minimum=1)
    trainable = _integer("trainable_parameters", trainable_parameters)
    if trainable > parameters:
        raise EstimationInputError("trainable_parameters cannot exceed model_parameters")
    ranks = _integer("world_size", world_size, minimum=1)
    stage = _integer("zero_stage", zero_stage)
    if stage > 3:
        raise EstimationInputError("zero_stage must be an integer in [0, 3]")

    weight_b = _number("weight_bytes_per_parameter", weight_bytes_per_parameter)
    gradient_b = _number(
        "gradient_bytes_per_trainable_parameter", gradient_bytes_per_trainable_parameter
    )
    master_b = _number(
        "master_weight_bytes_per_trainable_parameter",
        master_weight_bytes_per_trainable_parameter,
    )
    optimizer_b = _number(
        "optimizer_state_bytes_per_trainable_parameter",
        optimizer_state_bytes_per_trainable_parameter,
    )
    temporary = _number("temporary_bytes", temporary_bytes)
    margin = _number("safety_bytes", safety_bytes)

    if activation_model is not None and activation_bytes_override is not None:
        raise EstimationInputError(
            "supply activation_model or activation_bytes_override, not both"
        )
    if activation_model is not None:
        activation_inputs = _require_mapping("activation_model", activation_model)
        activation_bytes = estimate_activation_reference(**activation_inputs)
        activation_basis = {
            "kind": "hidden_state_equivalents",
            "inputs": activation_inputs,
            "interpretation": "user-configured reference scenario, not a measured peak",
        }
    elif activation_bytes_override is not None:
        activation_bytes = _number("activation_bytes_override", activation_bytes_override)
        activation_basis = {
            "kind": "externally_supplied_bytes",
            "interpretation": "user-supplied value; no measurement performed by this program",
        }
    else:
        activation_bytes = 0
        activation_basis = {
            "kind": "not_estimated",
            "interpretation": "zero is a placeholder; actual activations must be measured or supplied",
        }

    parameter_divisor = ranks if stage == 3 else 1
    gradient_divisor = ranks if stage >= 2 else 1
    optimizer_divisor = ranks if stage >= 1 else 1

    weights = _divided(_scaled(parameters, weight_b), parameter_divisor)
    gradients = _divided(_scaled(trainable, gradient_b), gradient_divisor)
    master_weights = _divided(_scaled(trainable, master_b), optimizer_divisor)
    optimizer_states = _divided(_scaled(trainable, optimizer_b), optimizer_divisor)
    state_total = weights + gradients + master_weights + optimizer_states
    total = state_total + activation_bytes + temporary + margin

    return {
        "kind": "training_memory_per_rank",
        "assumptions": {
            "model_parameters": parameters,
            "trainable_parameters": trainable,
            "world_size": ranks,
            "zero_stage": stage,
            "weight_bytes_per_parameter": weight_b,
            "gradient_bytes_per_trainable_parameter": gradient_b,
            "master_weight_bytes_per_trainable_parameter": master_b,
            "optimizer_state_bytes_per_trainable_parameter": optimizer_b,
        },
        "idealized_sharding_divisors": {
            "parameters": parameter_divisor,
            "gradients": gradient_divisor,
            "master_and_optimizer_states": optimizer_divisor,
        },
        "model_states_per_rank": {
            "model_weights": byte_units(weights),
            "trainable_gradients": byte_units(gradients),
            "trainable_master_weights": byte_units(master_weights),
            "trainable_optimizer_states": byte_units(optimizer_states),
            "subtotal": byte_units(state_total),
        },
        "non_state_memory_per_rank": {
            "activation_reference": byte_units(activation_bytes),
            "activation_basis": activation_basis,
            "temporary_workspaces": byte_units(temporary),
            "safety_reserve": byte_units(margin),
        },
        "total_estimate_per_rank": byte_units(total),
        "scope": (
            "first-order per-rank accounting; excludes unmodelled communication buffers, "
            "allocator effects, offload copies, and other implementation-specific memory"
        ),
    }


def estimate_training_flops(
    *, model_parameters: int, training_tokens: int, flops_per_parameter_token: int = 6
) -> int:
    """Return C ≈ k*N*D; k=6 is a dense-transformer first-order convention."""
    parameters = _integer("model_parameters", model_parameters, minimum=1)
    tokens = _integer("training_tokens", training_tokens)
    factor = _integer("flops_per_parameter_token", flops_per_parameter_token, minimum=1)
    return factor * parameters * tokens


def estimate_inference_flops(
    *,
    model_parameters: int,
    prompt_tokens: int,
    generated_tokens: int,
    batch_size: int = 1,
    flops_per_parameter_token: int = 2,
) -> int:
    """Approximate dense linear-layer FLOPs over prompt and generated tokens.

    This omits the sequence-quadratic attention term in prefill and many
    architecture/runtime costs; it is not a latency prediction.
    """
    parameters = _integer("model_parameters", model_parameters, minimum=1)
    prompt = _integer("prompt_tokens", prompt_tokens)
    generated = _integer("generated_tokens", generated_tokens)
    batch = _integer("batch_size", batch_size, minimum=1)
    factor = _integer("flops_per_parameter_token", flops_per_parameter_token, minimum=1)
    return factor * parameters * batch * (prompt + generated)


def roofline_lower_bound_seconds(
    *,
    floating_point_operations: int,
    bytes_moved: int,
    effective_flops_per_second: int | float,
    effective_bytes_per_second: int | float,
) -> dict[str, float]:
    """Compute a roofline-style lower bound from user-supplied effective rates."""
    operations = _integer("floating_point_operations", floating_point_operations)
    traffic = _integer("bytes_moved", bytes_moved)
    compute_rate = _number("effective_flops_per_second", effective_flops_per_second, minimum=0.000001)
    bandwidth = _number("effective_bytes_per_second", effective_bytes_per_second, minimum=0.000001)
    compute_bound = operations / compute_rate
    bandwidth_bound = traffic / bandwidth
    return {
        "compute_bound_seconds": compute_bound,
        "bandwidth_bound_seconds": bandwidth_bound,
        "lower_bound_seconds": max(compute_bound, bandwidth_bound),
        "warning": "a lower bound only; rates are user inputs, not measured by this project",
    }


def validate_fixture(fixture: Any) -> None:
    """Validate the synthetic fixture and every profile before calculating."""
    if not isinstance(fixture, dict):
        raise EstimationInputError("fixture must be a JSON object")
    if fixture.get("schema_version") != SCHEMA_VERSION:
        raise EstimationInputError("unsupported fixture schema_version")
    if fixture.get("label_source") != "synthetic_fixture":
        raise EstimationInputError("fixture label_source must be synthetic_fixture")
    metadata = _require_mapping("metadata", fixture.get("metadata"))
    for field in (
        "real_model_weights_included",
        "real_hardware_measurements_performed",
        "training_performed",
        "benchmark_performed",
    ):
        if metadata.get(field) is not False:
            raise EstimationInputError(f"fixture metadata must explicitly set {field}=false")

    profiles = fixture.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise EstimationInputError("fixture profiles must be a non-empty array")
    identifiers: set[str] = set()
    for profile in profiles:
        profile = _require_mapping("profile", profile)
        identifier = profile.get("profile_id")
        if not isinstance(identifier, str) or not identifier.strip():
            raise EstimationInputError("each profile needs a non-empty profile_id")
        if identifier in identifiers:
            raise EstimationInputError("profile_id values must be unique")
        identifiers.add(identifier)
        kind = profile.get("kind")
        if kind == "inference":
            _integer("model_parameters", profile.get("model_parameters"), minimum=1)
            _number("weight_bytes_per_parameter", profile.get("weight_bytes_per_parameter"))
            cache = _require_mapping("kv_cache", profile.get("kv_cache"))
            required = ("layers", "active_sequences", "context_tokens", "kv_heads", "head_dim", "bytes_per_element")
            if any(field not in cache for field in required):
                raise EstimationInputError(f"{identifier}: kv_cache is missing a required field")
            estimate_kv_cache(**{field: cache[field] for field in required})
            _number("runtime_and_temporary_bytes", profile.get("runtime_and_temporary_bytes", 0))
            _number("safety_bytes", profile.get("safety_bytes", 0))
        elif kind == "training":
            parameters = _integer("model_parameters", profile.get("model_parameters"), minimum=1)
            trainable = _integer("trainable_parameters", profile.get("trainable_parameters"))
            if trainable > parameters:
                raise EstimationInputError("trainable_parameters cannot exceed model_parameters")
            for field in (
                "weight_bytes_per_parameter",
                "gradient_bytes_per_trainable_parameter",
                "master_weight_bytes_per_trainable_parameter",
                "optimizer_state_bytes_per_trainable_parameter",
            ):
                _number(field, profile.get(field))
            _integer("world_size", profile.get("world_size", 1), minimum=1)
            stage = _integer("zero_stage", profile.get("zero_stage", 0))
            if stage > 3:
                raise EstimationInputError("zero_stage must be an integer in [0, 3]")
            if "activation_model" in profile:
                activation_model = _require_mapping("activation_model", profile["activation_model"])
                estimate_activation_reference(**activation_model)
            _number("temporary_bytes", profile.get("temporary_bytes", 0))
            _number("safety_bytes", profile.get("safety_bytes", 0))
            if "training_tokens" in profile:
                _integer("training_tokens", profile["training_tokens"])
        else:
            raise EstimationInputError(f"{identifier}: kind must be inference or training")


def load_fixture(path: str | Path = DEFAULT_FIXTURE) -> tuple[dict[str, Any], str]:
    fixture_path = Path(path)
    raw = fixture_path.read_bytes()
    try:
        fixture = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EstimationInputError(f"fixture is not valid UTF-8 JSON: {fixture_path.name}") from exc
    validate_fixture(fixture)
    return fixture, hashlib.sha256(raw).hexdigest()


def analyze_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one validated profile, preserving its declared assumptions."""
    common = {"profile_id": profile["profile_id"], "label": profile.get("label", "")}
    if profile["kind"] == "inference":
        cache_inputs = profile["kv_cache"]
        cache_bytes = estimate_kv_cache(**cache_inputs)
        estimate = estimate_inference(
            model_parameters=profile["model_parameters"],
            weight_bytes_per_parameter=profile["weight_bytes_per_parameter"],
            kv_cache_bytes=cache_bytes,
            runtime_and_temporary_bytes=profile.get("runtime_and_temporary_bytes", 0),
            safety_bytes=profile.get("safety_bytes", 0),
        )
        output = {**common, "kind": "inference", "kv_cache_inputs": cache_inputs, "estimate": estimate}
        if "prompt_tokens" in profile or "generated_tokens" in profile:
            output["linear_layer_flops"] = estimate_inference_flops(
                model_parameters=profile["model_parameters"],
                prompt_tokens=profile.get("prompt_tokens", 0),
                generated_tokens=profile.get("generated_tokens", 0),
                batch_size=cache_inputs["active_sequences"],
            )
        return output

    activation_model = profile.get("activation_model")
    estimate = estimate_training(
        model_parameters=profile["model_parameters"],
        trainable_parameters=profile["trainable_parameters"],
        weight_bytes_per_parameter=profile["weight_bytes_per_parameter"],
        gradient_bytes_per_trainable_parameter=profile["gradient_bytes_per_trainable_parameter"],
        master_weight_bytes_per_trainable_parameter=profile["master_weight_bytes_per_trainable_parameter"],
        optimizer_state_bytes_per_trainable_parameter=profile["optimizer_state_bytes_per_trainable_parameter"],
        world_size=profile.get("world_size", 1),
        zero_stage=profile.get("zero_stage", 0),
        activation_model=activation_model,
        temporary_bytes=profile.get("temporary_bytes", 0),
        safety_bytes=profile.get("safety_bytes", 0),
    )
    output = {**common, "kind": "training", "estimate": estimate}
    if "training_tokens" in profile:
        output["training_flops_approximation"] = estimate_training_flops(
            model_parameters=profile["model_parameters"],
            training_tokens=profile["training_tokens"],
        )
    return output


def run_demo(fixture_path: str | Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    """Return deterministic arithmetic results for all fixture profiles."""
    fixture, digest = load_fixture(fixture_path)
    return {
        "schema_version": SCHEMA_VERSION,
        "fixture": {
            "fixture_id": fixture.get("fixture_id", "unnamed"),
            "sha256": digest,
            "label_source": fixture["label_source"],
        },
        "scope": {
            "real_model_loaded": False,
            "real_hardware_measured": False,
            "training_performed": False,
            "benchmark_performed": False,
            "claim": "configured arithmetic and synthetic profiles only",
        },
        "scenarios": [analyze_profile(profile) for profile in fixture["profiles"]],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="First-order model memory/FLOPs estimator")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, help="write JSON to this path (default: stdout)")
    args = parser.parse_args(argv)
    result = run_demo(args.fixture)
    serialized = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
        print(f"Wrote arithmetic-only report: {args.output}")
    else:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
