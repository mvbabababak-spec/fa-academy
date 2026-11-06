# جلد چهارم، فصل ۲ — PEFT، Adapter، LoRA و QLoRA

**نگاشت:** فصل محلی ۲ جلد چهارم = فصل سراسری ۴۸. **تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶.** فصل ۴۷ هدف CPT و SFT و ماسک پاسخ را جدا کرد؛ این فصل می‌پرسد هنگام تطبیق یک مدل پایه، آیا لازم است همهٔ وزن‌های آن تغییر کنند؟ روش‌های PEFT فقط بخش کوچکی از پارامترها را آموزش می‌دهند یا ورودی/نمایش‌های مدل را با پارامترهای افزوده تغییر می‌دهند. فصل بعدی، ۴۹، به دادهٔ ترجیح، reward model و الگوریتم‌های بهینه‌سازی می‌پردازد؛ روش‌های آن فصل در اینجا آموزش داده نمی‌شوند.

**پیش‌نیاز:** لایهٔ خطی، ماتریس وزن، backpropagation، SFT و اندازهٔ دسته؛ مفاهیم dtype و quantization از فصل ۴۵. **خروجی:** بتوانید سه خانوادهٔ adapter bottleneck، LoRA و QLoRA را از نظر پارامتر آموزش‌پذیر، وزن پایه، حافظه و اجرای inference مقایسه کنید؛ تعداد پارامتر LoRA را برای یک ماتریس حساب کنید؛ و پروتکلی طراحی کنید که در آن «کم‌حافظه‌تر» را با «کیفیت برابر» اشتباه نگیرد.

![شکل ۴-۲-۱ — چهار مسیر تطبیق یک لایه: در full fine-tuning همهٔ وزن‌های پایه trainable هستند؛ در adapter و LoRA وزن پایه ثابت می‌ماند و ماژول یا ماتریس کم‌رتبهٔ افزوده آموزش می‌بیند؛ در QLoRA وزن پایهٔ quantized ثابت است و LoRA با دقت محاسباتی جداگانه آموزش می‌بیند. نمودار فقط مسیر پارامترها را نشان می‌دهد و مقایسهٔ کیفیت یا مصرف واقعی حافظه نیست.](book-engineering/diagrams/v4-ch02-peft.svg)

**شکل ۴-۲-۱ —** «فقط پارامترهای جدید را آموزش می‌دهیم» به معنی حذف تمام محاسبات مدل پایه نیست. در LoRA و QLoRA عبور رو به عقب از پایه همچنان برای رسیدن گرادیان به adapter لازم است؛ وزن پایه gradient یا update نمی‌گیرد.

## ۱. PEFT نام یک خانواده است، نه یک الگوریتم

**Parameter-Efficient Fine-Tuning (PEFT)** به روش‌هایی گفته می‌شود که برای تطبیق یک مدل ازپیش‌آموزش‌دیده همهٔ وزن‌هایش را مثل full fine-tuning به‌روزرسانی نمی‌کنند. در بعضی روش‌ها پارامتر جدید به مدل افزوده می‌شود؛ در بعضی دیگر زیرمجموعه‌ای از وزن‌ها، نمایش‌های میانی یا embeddingهای prompt تغییر می‌کنند. هدف معمول می‌تواند کاهش پارامترهای trainable، کاهش حالت optimizer، کوچک‌کردن checkpoint مخصوص task، یا نگهداری چند سازگارساز کنار یک پایهٔ مشترک باشد.

«PEFT» نام یک طبقهٔ روش‌هاست؛ کتابخانهٔ Hugging Face **PEFT** پیاده‌سازی تعدادی از آن‌هاست. این دو را یکی نگیرید. Adapter bottleneck، LoRA، prompt/prefix tuning و IA³ در یک خانوادهٔ کلی قرار می‌گیرند، اما محل و صورت تغییرشان یکسان نیست [۲،۷]. این فصل بر سه مسیر نقشه تمرکز دارد: adapter کلاسیک، LoRA و ترکیب LoRA با quantization که معمولاً QLoRA نامیده می‌شود.

پارامتر کمتر به‌خودی‌خود کیفیت برابر، سرعت بیشتر، مصرف برق کمتر یا هزینهٔ کمتر را ثابت نمی‌کند. آن‌ها نتیجه‌های جداگانه‌اند که با مدل، backend، سخت‌افزار، داده و سنجه باید اندازه‌گیری شوند. PEFT نیز خودبه‌خود داده را مجاز، پاسخ را ایمن یا رفتار مدل را «هم‌تراز» نمی‌کند.

## ۲. سه پرسش جدا: چه چیزی train می‌شود، چه چیزی ذخیره می‌شود، چه چیزی اجرا می‌شود؟

برای مقایسهٔ روش‌ها، دست‌کم این سه ستون را مستقل ثبت کنید:

| پرسش | نمونهٔ پاسخ | چرا مهم است؟ |
|---|---|---|
| کدام پارامترها gradient و optimizer state می‌گیرند؟ | وزن کامل، adapter، یا عوامل A و B | به حافظهٔ آموزش و آزادی تطبیق مربوط است. |
| کدام فایل‌ها برای بازیابی یک task ذخیره می‌شوند؟ | کل checkpoint یا adapter به‌همراه config و شناسهٔ پایه | adapter تنها بدون پایهٔ سازگار مدل کامل نیست. |
| کدام عملیات در inference باقی می‌ماند؟ | لایهٔ افزوده، ماتریس merge‌شده، یا quantized kernel | latency و سازگاری را تعیین می‌کند؛ باید روی backend هدف آزمود. |

«trainable parameters» معمولاً تعداد وزن‌هایی است که `requires_grad=True` دارند؛ این عدد با تعداد پارامتر کل، حجم optimizer، اندازهٔ فایل، حافظهٔ اوج یا latency یکی نیست. برای مثال، freeze کردن وزن پایه gradientهای وزن را حذف می‌کند، اما activationهای لازم برای backprop و اجرای forward پایه باقی‌اند. گزارش خوب هر سه پرسش و محیط سنجش را جواب می‌دهد.

## ۳. Adapter bottleneck: مسیر تازه روی نمایش میانی

در adapter کلاسیک، یک ماژول کوچک به بلوک Transformer افزوده می‌شود. شکل سادهٔ آن hidden vector را از بعد `d` به bottleneck با بعد `m` پایین می‌آورد، activation اعمال می‌کند و دوباره به `d` برمی‌گرداند؛ خروجی با skip connection به نمایش اولیه افزوده می‌شود:

```text
h' = h + W_up · activation(W_down · h + b_down) + b_up
W_down ∈ R^(m×d),   W_up ∈ R^(d×m),   m << d
```

برای یک adapter ساده، تعداد وزن‌های دو projection تقریباً `2dm` است؛ bias، LayerNorm، محل درج، تعداد ماژول‌های هر بلوک و headهای task-specific می‌توانند شمار واقعی را عوض کنند. در طرح Houlsby و همکاران، adapterها در دو نقطه از بلوک‌های BERT قرار گرفتند؛ مقاله روی مجموعهٔ taskها و setup خودش نتیجهٔ پارامتر/عملکرد گزارش می‌کند، نه عددی برای همهٔ مدل‌های امروزی [۱].

ماژول bottleneck معمولاً nonlinear است و در forward جداگانه اجرا می‌شود. در نتیجه نمی‌توان آن را عموماً با جمع‌کردن یک ماتریس خطی در وزن پایه ادغام کرد. این هزینه ممکن است قابل قبول باشد اگر چند task با ماژول‌های کوچک نگهداری شوند؛ اما latency و حافظهٔ واقعی باید در serving سنجیده شوند. واژهٔ «adapter» در گفت‌وگوی روزمره گاهی به LoRA هم گفته می‌شود؛ در این فصل «adapter bottleneck» به ماژول میانی nonlinear و «LoRA» به update ماتریسی کم‌رتبه اشاره می‌کند.

## ۴. LoRA: محدودکردن تغییر وزن به یک زیرفضای کم‌رتبه

فرض کنید وزن یک projection خطی `W₀` با شکل `d_out × d_in` ثابت بماند. Full fine-tuning می‌تواند تمام خانه‌های آن را عوض کند؛ LoRA تغییر را به حاصل‌ضرب دو ماتریس باریک محدود می‌کند:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="وزن مؤثر برابر وزن پایهٔ ثابت به‌علاوهٔ ضریب مقیاس ضربدر حاصل‌ضرب ماتریس B با شکل خروجی در رتبه و ماتریس A با شکل رتبه در ورودی است">
  <mrow>
    <msub><mi>W</mi><mi>eff</mi></msub><mo>=</mo><msub><mi>W</mi><mn>0</mn></msub><mo>+</mo><mi>γ</mi><mi>B</mi><mi>A</mi>
  </mrow>
</math>

**متن جایگزین فرمول:** وزن مؤثر برابر وزن پایهٔ ثابت به‌علاوهٔ ضریب مقیاس ضربدر حاصل‌ضرب ماتریس B با شکل خروجی در رتبه و ماتریس A با شکل رتبه در ورودی است. در LoRA کلاسیک معمولاً `γ = α/r`، `A ∈ R^(r×d_in)`، `B ∈ R^(d_out×r)` و `r` از ابعاد لایه کوچک‌تر است [۳].

در forward، برای ورودی `x` می‌توان نوشت `y = W₀x + γBAx`. `W₀` frozen می‌ماند و `A` و `B` آموزش می‌بینند. پژوهش LoRA انگیزهٔ خود را با فرض تجربیِ کم‌رتبه‌بودن تغییرهای سازگارشده صورت‌بندی کرد و روی چند مدل/task مقایسه‌هایی گزارش داد [۳]. این یک فرض مفید برای طراحی روش است، نه قضیه‌ای که برای هر مدل، دامنه یا task تضمین کند رتبهٔ کوچک کافی باشد.

## ۵. شمار پارامترها را برای هر ماتریس حساب کنید

برای یک ماتریس وزن `d_out × d_in`، full fine-tuning به‌روزرسانی همین ماتریس شامل `d_out × d_in` وزن است. در LoRA، دو عامل `A` و `B` روی هم `r(d_in + d_out)` پارامتر دارند؛ bias، dropout و پارامترهای خارج از این لایه در این شمار ساده نیامده‌اند:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="تعداد پارامترهای آموزش‌پذیر LoRA برای یک ماتریس برابر رتبه ضربدر مجموع بعد ورودی و بعد خروجی است">
  <mrow>
    <msub><mi>N</mi><mi>LoRA</mi></msub><mo>=</mo><mi>r</mi><mo>(</mo><msub><mi>d</mi><mi>in</mi></msub><mo>+</mo><msub><mi>d</mi><mi>out</mi></msub><mo>)</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** تعداد پارامترهای آموزش‌پذیر LoRA برای یک ماتریس برابر رتبه ضربدر مجموع بعد ورودی و بعد خروجی است. نسبت این تعداد به وزن کامل همان ماتریس برابر `r(d_in+d_out)/(d_in d_out)` است.

برای ماتریس فرضی `4096 × 4096` و `r=16`، update شامل `16 × (4096+4096) = 131,072` پارامتر است؛ ماتریس پایه `16,777,216` خانه دارد. نسبتِ این **یک ماتریس** حدود `0.78%` است. این درصد به معماری و انتخاب targetها وابسته است؛ اگر LoRA را روی Q، K، V، O و لایه‌های MLP قرار دهید، تعداد پارامترهای همهٔ ماژول‌ها را جمع کنید. درصد یک ماتریس را به کل مدل تعمیم ندهید.

## ۶. رتبه، مقیاس و initialization سه انتخاب مستقل‌اند

`r` ظرفیت update کم‌رتبه را تعیین می‌کند و شمار پارامتر را خطی بالا می‌برد؛ `α` در روش کلاسیک شدت update را از راه `α/r` مقیاس می‌دهد. مقدارهای r و alpha نسخهٔ واحد و تضمین‌شده ندارند: باید با validation و بودجهٔ واقعی آزموده شوند. در `r` بزرگ‌تر ممکن است کیفیت، پایداری گرادیان، سرعت و حافظه به شکل‌های متفاوت تغییر کنند.

در initialization رایج LoRA، `B` صفر و `A` غیرصفر مقداردهی می‌شود؛ در نتیجه `BA=0` در آغاز و خروجی اولیه با پایه برابر می‌ماند. پیاده‌سازی‌ها ممکن است جزئیات initializer را تغییر دهند؛ مستندات PEFT در تاریخ بازبینی initialization پیش‌فرض و `LoraConfig` را توضیح می‌دهد [۷]. تست کردن یک batch و شمار پارامترهای trainable پیش از run واقعی مفید است.

**Rank-Stabilized LoRA (rsLoRA)** ضریب `α/√r` را به‌جای `α/r` به‌کار می‌گیرد. مقالهٔ rsLoRA استدلال و آزمایش‌های خودش را برای پایداری rank مطرح می‌کند؛ در PEFT گزینهٔ `use_rslora` این انتخاب را فعال می‌کند [۵،۷]. این گزینه قانون همگانی یا وعدهٔ کیفیت نیست؛ اگر آن را روشن می‌کنید، در config، checkpoint و مقایسه ثبت کنید. این فصل وارد جزئیات AdaLoRA، DoRA، LoftQ و دیگر شاخه‌ها نمی‌شود؛ نام آن‌ها را با LoRA پایه یکی نگیرید.

## ۷. کدام ماژول‌ها را هدف می‌گیریم؟

مدل‌ها نام‌گذاری و بسته‌بندی لایه‌های متفاوتی دارند. در بعضی معماری‌ها projectionها جداگانه `q_proj`، `k_proj`، `v_proj` و `o_proj` هستند؛ در برخی دیگر چند projection در یک لایهٔ fused یا نام متفاوت قرار دارند. فهرست `target_modules` که برای یک معماری کار می‌کند، ممکن است در معماری دیگر هیچ لایه‌ای را پیدا نکند یا بیش از آنچه می‌خواهید انتخاب کند.

روند امن این است: نام و شکل ماژول‌های واقعی مدل را چاپ/ممیزی کنید؛ انتخاب target را با معماری و نسخهٔ کتابخانه تطبیق دهید؛ سپس تعداد لایه‌ها و پارامترهای LoRA را پس از wrap شدن بررسی کنید. انتخاب فقط Q/V، همهٔ projectionهای attention یا همهٔ linears مصالحه‌های متفاوت‌اند. `all-linear` در APIهای جاری PEFT یک shorthand است، اما coverage و سازگاری را برای مدل شما خودتان بررسی کنید [۷،۸].

قرار دادن LoRA روی لایه‌های بیشتری ظرفیت و پارامتر را بالا می‌برد. هدف‌گرفتن لایهٔ نادرست، head تصادفی، embedding یا لایهٔ خارج از مسیر آموزش می‌تواند adapter بی‌اثر یا فایل ناقص بسازد. ماژول task-specificِ تصادفی‌مقداردهی‌شده گاهی باید با گزینه‌ای مانند `modules_to_save` همراه checkpoint شود؛ انتخاب آن هم معماری‌محور است و باید بازخوانی‌پذیر باشد.

## ۸. وزن پایه frozen است، اما محاسبهٔ پایه حذف نمی‌شود

وقتی وزن پایه `requires_grad=False` است، optimizer برای آن weight gradient/حالت به‌روزرسانی نگه نمی‌دارد؛ اما forward پایه باید اجرا شود. در backprop نیز گرادیان نسبت به ورودی‌ها از محاسبهٔ لایه‌های frozen عبور می‌کند تا به adapterهای لایه‌های قبلی برسد. به همین دلیل PEFT می‌تواند حافظهٔ gradient و optimizer state را کاهش دهد، ولی activationها، attention، sequence length، batch و workspace هنوز می‌توانند غالب باشند.

این تفاوت را در مقایسه با full fine-tuning روشن کنید: «پارامتر trainable کمتر» لزوماً به معنی «زمان آموزش به همان نسبت کمتر» نیست. حافظهٔ بارگذاری مدل پایه نیز باقی است؛ QLoRA این قسمت را با quantization هدف می‌گیرد، اما metadata، activation و اجرای backward همچنان هزینه دارند. Gradient checkpointing، accumulation و batching روش‌های جداگانه‌اند و باید در هر run ثبت شوند؛ آن‌ها ویژگی خود LoRA نیستند.

## ۹. Adapter و LoRA را چطور ذخیره و سرو می‌کنیم؟

در بسیاری از کتابخانه‌ها می‌توان وزن adapter را جدا از وزن پایه ذخیره کرد. فایل جداگانه، اگر به‌تنهایی منتشر شود، معمولاً باید همراه شناسه/نسخه یا hash مدل پایه، tokenizer، config، target moduleها، rank، alpha، dtype و هر head لازم توصیف شود. بارگذاری adapter روی checkpoint نامتجانس ممکن است از نظر شکل رد شود، یا بدتر، با شکل مشابه ولی معنای متفاوت بارگذاری شود؛ شناسهٔ نام متحرک `main` برای بازتولید دقیق کافی نیست.

در LoRA خطیِ معمول، اگر adapter با همان precision و semantics merge شود، حاصل‌ضرب `γBA` را می‌توان به وزن پایه افزود: `W_eff = W₀ + γBA`. این کار ممکن است ماژول افزوده را از مسیر inference بردارد. اگر چند adapter هم‌زمان یا swapپذیر لازم باشد، نگه‌داشتن آن‌ها جدا انعطاف می‌دهد اما عملیات افزوده دارد. برای لایهٔ nonlinear bottleneck چنین ادغام ساده‌ای عموماً برقرار نیست.

در مدل quantized، merge/unmerge، پشتیبانی kernel و تبدیل dtype/quantization وابسته به نسخه و backend است؛ dequantize/merge/requantize ممکن است گردکردن جدید و هزینهٔ حافظه داشته باشد. پیش از انتشار، هم برابری عددی تقریبی و هم خروجی/latency روی همان سیستم serving را بسنجید. مستندات PEFT توابع merge/unload را دارد، اما وجود API تضمین سازگاری با هر لایه و quantization نیست [۷،۸].

## ۱۰. QLoRA: LoRA روی پایهٔ quantized، نه آموزش همه‌چیز در ۴ بیت

در QLoRA، وزن‌های پایه پیش از آموزش به قالب کم‌دقت (در مقاله ۴-bit) ذخیره می‌شوند و ثابت می‌مانند؛ LoRA factors آموزش‌پذیرند و گرادیان از محاسبات پایه به آن‌ها می‌رسد. پس عبارت «QLoRA مدل را در ۴ بیت fine-tune می‌کند» اگر منظورش update همهٔ وزن‌های پایه باشد گمراه‌کننده است. تمرین QLoRA عموماً وزن‌های LoRA را با dtype محاسباتی دیگری نگه می‌دارد و optimizer را روی بخش آموزش‌پذیر اجرا می‌کند [۴،۹].

QLoRA مقالهٔ Dettmers و همکاران سه جزئیات را برجسته کرد: NF4، double quantization و paged optimizers. در همان setup مقاله، نویسندگان امکان تطبیق مدل ۶۵B را روی یک GPU 48GB گزارش کردند [۴]. این عدد نتیجهٔ پیکربندی و نرم‌افزار همان آزمایش است، نه حداقل VRAM عمومی یا تضمین اینکه هر مدل 65B با هر طول و batch روی هر کارت جا شود.

QLoRA memory optimization است، نه ارزیابیِ خودکارِ کیفیت؛ می‌تواند بر کیفیت اثر بگذارد یا run را از نظر سخت‌افزار ممکن کند، اما آیا خروجی بهتر، هم‌ارز یا بدتر است باید با baseline همسان سنجیده شود. مقالهٔ اصلی نتایج تجربی خودش را روی مدل‌ها، داده‌ها و benchmarkهای خودش گزارش می‌دهد؛ انتقال آن‌ها به زبان، task یا checkpoint دیگر نیازمند آزمایش تازه است.

## ۱۱. NF4، nested quantization و precision محاسبه

در مستندات Transformers، `load_in_4bit=True` قالب ذخیرهٔ پایه را فعال می‌کند؛ `bnb_4bit_quant_type="nf4"` نوع quantization است؛ `bnb_4bit_use_double_quant=True` nested quantization را برای scaleها به کار می‌گیرد؛ و `bnb_4bit_compute_dtype` dtype محاسبهٔ ماتریسی را مشخص می‌کند [۹]. این گزینه‌ها مفهوم‌های جدا هستند. ۴-bit storage به این معنا نیست که تمام ضرب ماتریسی یا adapter هم با ۴-bit انجام شود.

NF4 در QLoRA برای توزیع وزن‌های فرض‌شده نرمال طراحی شد؛ «بهینه برای نرمال» حکم نمی‌کند بهترین انتخاب برای هر activation، embedding، نوع وزن یا مدل باشد. Double quantization، بنا بر مقاله و راهنمای Transformers، اندازهٔ میانگین برخی ثابت‌های quantization را کم می‌کند؛ مقدار گزارش‌شده به block format و implementation مربوط است [۴،۹]. در notebook خود از مقدار پیش‌فرض کتابخانه کورکورانه پیروی نکنید؛ config واقعی را ذخیره کنید.

Paged optimizer در مقالهٔ QLoRA برای مدیریت memory spike با unified memoryِ NVIDIA توصیف شده است [۴]. نام مشابه در کتابخانه‌های دیگر لزوماً رفتار یا سخت‌افزار یکسان ندارد. قبل از انتخاب، backend، نسخهٔ CUDA/کتابخانه، سازگاری کارت، dtype قابل پشتیبانی و محدودیت‌های install را از جدول همان نسخه بخوانید. مستندات جاری Transformers هنگام بازبینی، backendهای پشتیبانی‌شدهٔ bitsandbytes را جداگانه فهرست می‌کرد [۹].

## ۱۲. حافظه را از اجزایش برآورد کنید، نه از «چهار بیت» به‌تنهایی

برای یک پایهٔ فرضی با `N` وزن، payload خام ۴-bit حد نظریِ حدود `N/2` بایت دارد، چون هر بایت دو مقدار ۴-bit نگه می‌دارد. این **کران پایین وزن packed** است، نه VRAM کل. اندازهٔ واقعی وزن می‌تواند به group scale و metadata، alignment، لایه‌های quantizeنشده، tableها، padding و serialization بستگی داشته باشد.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="حافظهٔ آموزش حاصل جمع حافظهٔ وزن پایهٔ quantized، پارامتر و optimizer adapter، activationها و workspace موقت است">
  <mrow><msub><mi>M</mi><mi>train</mi></msub><mo>≈</mo><msub><mi>M</mi><mi>base</mi></msub><mo>+</mo><msub><mi>M</mi><mi>adapter</mi></msub><mo>+</mo><msub><mi>M</mi><mi>optimizer</mi></msub><mo>+</mo><msub><mi>M</mi><mi>activations</mi></msub><mo>+</mo><msub><mi>M</mi><mi>workspace</mi></msub></mrow>
</math>

**متن جایگزین فرمول:** حافظهٔ آموزش تقریباً مجموع وزن پایهٔ quantized، پارامتر و حالت optimizer adapter، activationها و workspace موقت است. این رابطه فقط تفکیک مؤلفه‌ها را نشان می‌دهد و مقدار اندازه‌گیری‌شده نیست.

حافظهٔ full fine-tuning به dtype وزن و gradient، optimizer، sharding، offload، activation و checkpointing بستگی دارد؛ عدد ثابت «چند بایت به‌ازای پارامتر» را بدون مفروضات به همهٔ runها نسبت ندهید. برای مقایسهٔ منصفانه، موارد زیر را کنار هم ثبت کنید:

| مورد ثبت | خط پایهٔ مناسب |
|---|---|
| مدل و revision، tokenizer، tokenizer template | یکسان در همهٔ پیکربندی‌های مقایسه |
| داده، split و تعداد supervised token | یکسان و hash‌شده |
| context، batch مؤثر، updateها و optimizer | هم‌بودجه یا تفاوت صریح و توجیه‌شده |
| rank، alpha، target modules، precision و quantization | config کامل و نسخه‌دار |
| peak allocated/reserved، throughput و latency | اندازه‌گیری روی دستگاه/نسخهٔ مشخص، با warm-up و روش ثابت |
| معیار task و test نهایی | تعریف‌شده پیش از run؛ test پس از انتخاب نهایی فقط یک‌بار |

حالت audit این فصل فقط کران پایین payload را از fixture شکل‌ها حساب می‌کند؛ هیچ VRAM، RAM، throughput یا latency را اندازه‌گیری نمی‌کند. به عدد آن برای خرید GPU یا وعدهٔ اجرای مدل بزرگ تکیه نکنید.

## ۱۳. PEFT انتخابی برای هر task با پروتکل ارزیابی یکی نیست

پیش از آموزش، full fine-tuning یا baseline موجود را در صورت امکان مشخص کنید؛ نسخهٔ LoRA و QLoRA را روی همان مدل، داده، split، prompt/template، تعداد update و معیار مقایسه کنید. اگر full fine-tuning در بودجهٔ سخت‌افزار ممکن نیست، محدودیت baseline را ثبت کنید و صرفاً ادعای «بهتر از full fine-tune» ننویسید. بودجهٔ بهینه‌سازی متفاوت، مقایسهٔ کیفیت را مخدوش می‌کند.

برای task، معیار مرتبط انتخاب کنید: NLL، accuracy، exact match، rubric انسانی یا مجموعه‌ای از معیارها. پارامترهای trainable و اندازهٔ adapter را در کنار نتیجه گزارش کنید؛ افزایش ظرفیت rank و target moduleها را با validation تنظیم کنید؛ test را در طول sweeps انتخاب نکنید. اگر ارزیاب انسانی یا مدل دیگری به کار می‌رود، rubric، نمونه‌گیری، ترتیب نمایش، اختلاف ارزیاب و محدودیت‌های آن را بنویسید.

«برابر بودن» باید operational تعریف شود: حاشیهٔ قابل‌قبول، عدم قطعیت و جمعیت ارزیابی را پیشاپیش مشخص کنید. یک run یا یک benchmark محبوب برتری یا برابری کلی را ثابت نمی‌کند. برای فارسی یا task تخصصی نیز داده، ارزیاب و benchmark همان زبان/کاربرد لازم است؛ این پروژهٔ انگلیسی‌محور یا fixture ریاضی چنین شواهدی نمی‌سازد.

## ۱۴. شکست‌های رایج در PEFT و QLoRA

- هیچ پارامتری trainable نیست چون همهٔ ماژول‌ها freeze شده‌اند؛ یا بیش از قصد trainable است چون `bias`, LayerNorm یا head از تنظیم بیرون مانده است. شمار parameters و optimizer groups را log کنید.
- `target_modules` خالی است، نام آن با architecture یکی نیست، یا fused layer را به شکل اشتباه هدف گرفته است. پیش از آموزش، نام و شکل لایه‌های wrap‌شده را inspect کنید.
- adapter ذخیره می‌شود اما base model، revision، tokenizer، config یا head مخصوص task ثبت نمی‌شود؛ فایل برای بازتولید کافی نیست.
- `r`, `alpha`, `use_rslora`, dropout، initializer یا dtype در checkpoint یا گزارش نیست؛ نتیجه قابل نسبت‌دادن به تنظیمات نیست.
- مدل ۴-bit بارگیری شده اما `prepare_model_for_kbit_training`, gradient-checkpointing، dtype، device placement یا backend با نسخهٔ مورد استفاده سازگار نیست. دستور جاری را از مستندات همان نسخه بگیرید، نه یک notebook قدیمی.
- کاربر انتظار دارد quantization خودبه‌خود VRAM را به نصف دقیق کم کند؛ scaleها، activations، optimizer، fragmentation و لایه‌های غیرquantized حذف نشده‌اند.
- adapter در train merge شده یا dropout در inference اشتباهاً فعال می‌ماند؛ یا merge روی quantized weights به‌عنوان برابری دقیق فرض می‌شود.
- PEFT به‌عنوان ضمانت حفظ دانش، ایمنی، privacy، حقوق داده یا کیفیت محصول تفسیر می‌شود؛ هیچ‌کدام از تعداد پارامترها نتیجه نمی‌شود.

## ۱۵. نمونهٔ API کتابخانه‌ها: نسخه را با مدل واقعی تطبیق دهید

در مستندات رسمی PEFT که ۶ نوامبر ۲۰۲۶ بازبینی شد، راه معمول شامل ساخت `LoraConfig`، تعیین rank/target modules، wrap کردن پایه با `get_peft_model` و سپس آموزش بود. نمونهٔ زیر **توضیح API** است و در پروژهٔ همین فصل اجرا نشده؛ نام لایه‌ها برای مدل واقعی باید بررسی شود. مستندات زنده‌ای که بازبینی شد PEFT main و stable v0.21.0 و مستندات Transformers v5.22.1 را نشان می‌داد [۷–۹].

```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    target_modules=["q_proj", "v_proj"],
    task_type="CAUSAL_LM",
)
peft_model = get_peft_model(base_model, config)
peft_model.print_trainable_parameters()
```

QLoRA-style load در Transformers نیز با `BitsAndBytesConfig` تعریف می‌شود؛ کد کوتاه زیر فقط قالب تنظیم را نشان می‌دهد و device, model revision, placement, version compatibility, training arguments یا اجرای CUDA را کامل نمی‌کند:

```python
import torch
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)
```

در run واقعی، نسخهٔ `torch`, `transformers`, `peft`, `bitsandbytes`, `accelerate`، backend، CUDA/driver و مدل را دقیقاً pin/ثبت کنید؛ API و پشتیبانی پلتفرم تغییر می‌کند. این فایل‌ها را با project toy این فصل اشتباه نگیرید: آن پروژه عمدی dependency شبکه و مدل ندارد.

## ۱۶. پروژهٔ اجرایی: ماتریس کوچک، رفتار قابل‌آزمون

[پروژهٔ PEFT/LoRA فصل ۴۸](book-engineering/projects/48-peft-lab/README.md) یک `nn.Linear` کوچک را با `W₀` frozen و دو عامل trainable پیاده‌سازی می‌کند؛ یک bottleneck residual adapter هم برای مقایسه دارد. تست‌ها initialization همانیِ update صفر، freeze پایه، تعداد عوامل، gradient، merge در eval، ابعاد fixture و audit آفلاین را می‌سنجند. اجرای `toy-lora` روی نگاشت خطی مصنوعی انجام می‌شود؛ loss صرفاً خطای همان مثال ساختگی است.

حالت `audit` از سه ردیف fixtureِ نام‌گذاری‌شده به‌عنوان `fixture.*`، تعداد پارامترهای پایه و LoRA را حساب می‌کند و برای وزن فشرده کران پایین می‌دهد؛ رکوردها معماری مدل واقعی نیستند. حالت demo یک ماتریس هدف rank-2 را با seed=48 و ۵۰۰ گام CPU بازسازی می‌کند. در گزارش ممیزی، نتیجهٔ دقیق اجرای واقعی و محدودیتش ثبت می‌شود. این اجرا PEFT library یا مدل زبانی را آزمایش نمی‌کند.

## ۱۷. چک‌لیست پیش از انتخاب روش

۱. هدف task، مدل پایه، revision، tokenizer و قالب prompt ثبت شده‌اند. ۲. full fine-tuning، adapter bottleneck، LoRA یا QLoRA را بر اساس محدودیت مشخص انتخاب کرده‌ام، نه صرفاً نام رایج. ۳. `target_modules` واقعاً در معماری موجودند و شمارش ماژول‌ها/پارامترهای trainable بازبینی شده است. ۴. rank، alpha یا scaling variant، dropout، initializer، bias، head و `modules_to_save` مستندند. ۵. برای QLoRA، quantization type، double quantization، compute dtype، backend و placement ثبت شده‌اند. ۶. base، adapter، tokenizer و config به شکل سازگار ذخیره می‌شوند. ۷. حافظهٔ اوج، زمان/throughput و latency روی دستگاه هدف با روش ثابت اندازه‌گیری می‌شوند؛ برآورد payload را با peak حافظه اشتباه نمی‌گیرم. ۸. معیار، baseline، split و بودجهٔ مقایسه پیش از آموزش تعیین شده‌اند؛ test دیرهنگام استفاده می‌شود. ۹. ادعای کیفیت به داده و setup واقعی محدود می‌ماند و از شمار پارامتر یا fixture toy نتیجه‌گیری نمی‌کنم.

## ۱۸. تمرین‌ها و پاسخ‌نامهٔ مستقل

**تمرین ۱.** برای projection فرضی `d_in=2048`, `d_out=8192`, `r=8`، تعداد پارامترهای A و B را جداگانه و جمع را حساب کنید. نسبت آن به ماتریس کامل چند درصد است؟ کدام موارد در این نسبت شمرده نشده‌اند؟

**تمرین ۲.** برای یک adapter bottleneck با `d=1024` و `m=32`، فقط تعداد وزن‌های دو projection را برآورد کنید. دو دلیل بیاورید که چرا این عدد با کل پارامترهای روش مقاله یا اندازهٔ inference برابر نیست.

**تمرین ۳.** یک مدل با ۴ میلیارد وزن را در ۴-bit packed ذخیره می‌کنید. payload خام حد پایین چند بایت است؟ حداقل چهار مؤلفهٔ حافظهٔ دیگر را نام ببرید و توضیح دهید چرا عدد شما VRAM تخمینی کامل نیست.

**تمرین ۴.** در یک معماری `qkv_proj` لایهٔ fused است و `q_proj` مجزا وجود ندارد. اگر پیکربندی LoRA هیچ targetی پیدا نکرد، چه چیزهایی را inspect و ثبت می‌کنید؟ چرا کپی‌کردن target modules از مدل دیگری راه‌حل قابل‌اعتماد نیست؟

**تمرین ۵.** دو checkpoint را مقایسه می‌کنید: LoRA full precision و QLoRA NF4. برای ادعای کیفیت/حافظهٔ بهتر، چه چیزهایی باید ثابت، چه چیزهایی باید اندازه‌گیری و test چه زمانی مصرف شود؟

**پاسخ‌نامهٔ مستقل:** [پاسخ‌نامهٔ تشریحی فصل ۴۸](book-engineering/answers/48-peft-fa.md). **پروژه:** [README آزمایشگاه](book-engineering/projects/48-peft-lab/README.md)؛ **گزارش اجرا و محدودیت:** [گزارش ممیزی فصل ۴۸](book-engineering/chapters/48-audit-report-fa.md).

## ۱۹. جمع‌بندی و مرز فصل بعد

PEFT مجموعه‌ای از راه‌هاست تا وزن پایه را کامل fine-tune نکنیم. Adapter bottleneck تغییر را به ماژول‌های کم‌بعد/nonlinear در نمایش‌ها می‌سپارد؛ LoRA update وزن را به `BA` کم‌رتبه با scaling مشخص بازپارامتردهی می‌کند؛ QLoRA LoRA را با پایهٔ کم‌حافظهٔ quantized ترکیب می‌کند. هزینه‌ای که واقعاً کم می‌شود باید با تعداد پارامتر، حافظهٔ اوج، زمان، checkpoint و inference جدا سنجیده شود. در quantization، storage precision و compute precision را با یکدیگر اشتباه نگیرید.

فصل ۴۹ پس از این روش‌های supervised/parameter-efficient، دادهٔ ترجیح، reward model، RLHF/PPO، DPO، GRPO، RLAIF و Constitutional AI را بررسی می‌کند. خروجی toy این فصل نه ترجیح انسانی دارد، نه پاداش، نه policy evaluation؛ برای آن مفاهیم شاهد محسوب نمی‌شود.

## ۲۰. منابع و تاریخ بازبینی

منابع و صفحات رسمی زیر در **۶ نوامبر ۲۰۲۶** بازبینی شدند. عددهای تجربی به setup نویسندگان محدودند؛ مستندات API زنده‌اند و نسخهٔ مشاهده‌شده در همان روز ثبت شده است.

1. Houlsby, N. و همکاران، “Parameter-Efficient Transfer Learning for NLP”، ICML 2019, PMLR 97, 2790–2799. [متن و citation](https://proceedings.mlr.press/v97/houlsby19a.html). نتایج adapter مربوط به BERT و setup مقاله‌اند.
2. He, J. و همکاران، “Towards a Unified View of Parameter-Efficient Transfer Learning”، ICLR 2022, [arXiv:2110.04366](https://arxiv.org/abs/2110.04366). چارچوبی برای دیدن محل و صورت update روش‌های PEFT؛ نتایج به taskهای مقاله مربوط‌اند.
3. Hu, E. J. و همکاران، “LoRA: Low-Rank Adaptation of Large Language Models”، ICLR 2022, [arXiv:2106.09685](https://arxiv.org/abs/2106.09685). تعریف low-rank update، scaling و آزمایش‌های همان کار.
4. Dettmers, T. و همکاران، “QLoRA: Efficient Finetuning of Quantized LLMs”، 2023, [arXiv:2305.14314](https://arxiv.org/abs/2305.14314). NF4، double quantization و paged optimizer در setup نویسندگان.
5. Kalajdzievski, D., “A Rank Stabilization Scaling Factor for Fine-Tuning with LoRA”، 2023, [arXiv:2312.03732](https://arxiv.org/abs/2312.03732). rsLoRA و scaling رتبه‌پایدار در تحلیل/آزمایش مقاله.
6. Li, Y. و همکاران، “LoftQ: LoRA-Fine-Tuning-Aware Quantization for Large Language Models”، 2023, [arXiv:2310.08659](https://arxiv.org/abs/2310.08659). initialization آگاه از quantization؛ خارج از پیاده‌سازی پروژهٔ این فصل.
7. Hugging Face PEFT، [راهنمای LoRA](https://huggingface.co/docs/peft/main/en/conceptual_guides/lora) و [API/تنظیمات](https://huggingface.co/docs/peft/main/en/package_reference/lora). نسخهٔ stable روی راهنمای main در تاریخ بازبینی v0.21.0 نشان داده می‌شد؛ API/معماری‌محور است.
8. Hugging Face PEFT، [راهنمای quantization](https://huggingface.co/docs/peft/developer_guides/quantization). پشتیبانی و ترکیب روش‌ها را با نسخهٔ نصب‌شده دوباره تطبیق دهید.
9. Hugging Face Transformers، [راهنمای bitsandbytes و QLoRA](https://huggingface.co/docs/transformers/en/quantization/bitsandbytes). نسخهٔ جاری مشاهده‌شده در ۶ نوامبر ۲۰۲۶ برابر v5.22.1 بود؛ جدول backend سخت‌افزار versioned است.
10. PyTorch 2.6.0، [torch.nn.Linear](https://docs.pytorch.org/docs/2.6/generated/torch.nn.Linear.html) و [torch.nn.Parameter](https://docs.pytorch.org/docs/2.6/generated/torch.nn.parameter.Parameter.html). قرارداد لایهٔ خطی و پارامترها در پروژهٔ toy.
11. PyTorch 2.6.0، [autograd mechanics](https://docs.pytorch.org/docs/2.6/notes/autograd.html). رفتار autograd به گراف و `requires_grad` وابسته است؛ frozen بودن وزن محاسبهٔ forward را حذف نمی‌کند.

## ۲۱. پیوست اجرایی: فایل پروژهٔ آزموده‌شده

کد زیر با بایت‌های `book-engineering/projects/48-peft-lab/peft_lab.py` یکسان است؛ builder و checker این قرارداد را کنترل می‌کنند. این کد یک آزمایشگاه CPU برای لایه‌های مصنوعی است، نه پیاده‌سازی PEFT library یا QLoRA واقعی.

```python
"""CPU-only algebra lab for adapters, LoRA and QLoRA accounting.

This module uses synthetic linear layers only. It does not load a pretrained
model, quantize real weights, benchmark hardware, or claim task quality.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import torch
from torch import nn
from torch.nn import functional as F


def lora_parameter_count(in_features: int, out_features: int, rank: int) -> int:
    """Number of A/B parameters for one bias-free low-rank update."""
    if min(in_features, out_features, rank) <= 0:
        raise ValueError("dimensions and rank must be positive")
    if rank > min(in_features, out_features):
        raise ValueError("rank cannot exceed the smaller matrix dimension in this lab")
    return rank * (in_features + out_features)


def quantized_payload_lower_bound(parameter_count: int, bits: int = 4) -> int:
    """Packed weight payload only; excludes scales, metadata and all other memory."""
    if parameter_count < 0 or bits <= 0:
        raise ValueError("parameter_count must be non-negative and bits positive")
    return math.ceil(parameter_count * bits / 8)


class LoRALinear(nn.Module):
    """Frozen nn.Linear plus a trainable low-rank update."""

    def __init__(
        self,
        in_features: int,
        out_features: int,
        rank: int,
        alpha: float,
        *,
        bias: bool = True,
        dropout: float = 0.0,
        rank_stabilized: bool = False,
    ) -> None:
        super().__init__()
        lora_parameter_count(in_features, out_features, rank)
        if not math.isfinite(alpha) or alpha <= 0:
            raise ValueError("alpha must be finite and positive")
        if not 0.0 <= dropout < 1.0:
            raise ValueError("dropout must be in [0, 1)")
        self.in_features = in_features
        self.out_features = out_features
        self.rank = rank
        self.alpha = float(alpha)
        self.rank_stabilized = bool(rank_stabilized)
        divisor = math.sqrt(rank) if rank_stabilized else rank
        self.scaling = self.alpha / divisor
        self.base = nn.Linear(in_features, out_features, bias=bias)
        self.base.requires_grad_(False)
        self.lora_A = nn.Parameter(torch.empty(rank, in_features))
        self.lora_B = nn.Parameter(torch.zeros(out_features, rank))
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
        self.lora_dropout = nn.Dropout(dropout)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        low_rank = F.linear(F.linear(self.lora_dropout(inputs), self.lora_A), self.lora_B)
        return self.base(inputs) + self.scaling * low_rank

    def merged_layer(self) -> nn.Linear:
        """Return a fresh dense layer with the update folded into its weight."""
        merged = nn.Linear(
            self.in_features,
            self.out_features,
            bias=self.base.bias is not None,
            device=self.base.weight.device,
            dtype=self.base.weight.dtype,
        )
        with torch.no_grad():
            merged.weight.copy_(self.base.weight + self.scaling * (self.lora_B @ self.lora_A))
            if self.base.bias is not None:
                merged.bias.copy_(self.base.bias)
        return merged

    def trainable_parameter_count(self) -> int:
        return sum(parameter.numel() for parameter in self.parameters() if parameter.requires_grad)


class BottleneckAdapter(nn.Module):
    """Simple residual down-activation-up adapter for a hidden vector."""

    def __init__(self, hidden_size: int, bottleneck_size: int) -> None:
        super().__init__()
        if min(hidden_size, bottleneck_size) <= 0 or bottleneck_size > hidden_size:
            raise ValueError("adapter dimensions must be positive and bottleneck <= hidden size")
        self.down = nn.Linear(hidden_size, bottleneck_size, bias=False)
        self.up = nn.Linear(bottleneck_size, hidden_size, bias=False)
        nn.init.zeros_(self.up.weight)

    def forward(self, hidden: torch.Tensor) -> torch.Tensor:
        return hidden + self.up(F.gelu(self.down(hidden)))


def validate_fixture(rows: Any) -> list[dict[str, Any]]:
    if not isinstance(rows, list) or not rows:
        raise ValueError("fixture must be a non-empty JSON list")
    seen: set[str] = set()
    clean: list[dict[str, Any]] = []
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f"row {index} must be an object")
        name = row.get("name")
        if not isinstance(name, str) or not name.strip() or name in seen:
            raise ValueError(f"row {index} needs a unique non-empty name")
        seen.add(name)
        fields = ("in_features", "out_features", "rank", "alpha", "weight_bits")
        if any(field not in row for field in fields):
            raise ValueError(f"row {index} is missing a required field")
        in_features, out_features, rank = (row[k] for k in fields[:3])
        if any(type(value) is not int for value in (in_features, out_features, rank)):
            raise ValueError(f"row {index}: dimensions and rank must be integers")
        lora_parameter_count(in_features, out_features, rank)
        alpha, bits = row["alpha"], row["weight_bits"]
        if isinstance(alpha, bool) or not isinstance(alpha, (int, float)) or not math.isfinite(alpha) or alpha <= 0:
            raise ValueError(f"row {index}: alpha must be finite and positive")
        if type(bits) is not int or bits not in (4, 8, 16, 32):
            raise ValueError(f"row {index}: weight_bits must be one of 4, 8, 16, 32")
        full = in_features * out_features
        trainable = rank * (in_features + out_features)
        clean.append({
            "name": name,
            "in_features": in_features,
            "out_features": out_features,
            "rank": rank,
            "alpha": float(alpha),
            "weight_bits": bits,
            "base_weight_parameters": full,
            "lora_trainable_parameters": trainable,
            "lora_to_base_percent_for_this_matrix": 100.0 * trainable / full,
            "packed_weight_payload_lower_bound_bytes": quantized_payload_lower_bound(full, bits),
        })
    return clean


def audit_fixture(path: Path) -> dict[str, Any]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    layers = validate_fixture(rows)
    return {
        "schema_version": 1,
        "status": "validated_only",
        "training_performed": False,
        "model_loaded": False,
        "model_downloaded": False,
        "fixture": path.name,
        "fixture_kind": "synthetic layer-shape accounting; not a model architecture",
        "layers": layers,
        "totals": {
            "base_weight_parameters_in_fixture": sum(row["base_weight_parameters"] for row in layers),
            "lora_trainable_parameters_in_fixture": sum(row["lora_trainable_parameters"] for row in layers),
            "quantized_weight_payload_lower_bound_bytes": sum(row["packed_weight_payload_lower_bound_bytes"] for row in layers),
        },
        "memory_note": "payload lower bound only; excludes quantization metadata, non-quantized layers, activations, gradients, optimizer, temporary buffers and runtime overhead",
        "claim_boundary": "does not measure GPU/CPU peak memory, quality, throughput, compatibility or a real pretrained model",
    }


def run_toy_demo(steps: int = 500, seed: int = 48) -> dict[str, Any]:
    """Fit an exactly rank-two synthetic matrix change as an algebra smoke test."""
    if steps <= 0:
        raise ValueError("steps must be positive")
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    in_features, out_features, rank, alpha = 16, 12, 2, 2.0
    scale = alpha / rank
    base_weight = torch.randn(out_features, in_features) * 0.12
    target_A = torch.randn(rank, in_features) * 0.10
    target_B = torch.randn(out_features, rank) * 0.10
    target_weight = base_weight + scale * (target_B @ target_A)
    inputs = torch.randn(96, in_features)
    targets = F.linear(inputs, target_weight)

    model = LoRALinear(in_features, out_features, rank, alpha, bias=False)
    with torch.no_grad():
        model.base.weight.copy_(base_weight)
    initial_mse = float(F.mse_loss(model(inputs), targets).item())
    optimizer = torch.optim.Adam((model.lora_A, model.lora_B), lr=0.04)
    model.train()
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)
        loss = F.mse_loss(model(inputs), targets)
        loss.backward()
        optimizer.step()
    model.eval()
    final_mse = float(F.mse_loss(model(inputs), targets).item())
    return {
        "schema_version": 1,
        "status": "synthetic_demo_completed",
        "training_performed": True,
        "model_loaded": False,
        "model_downloaded": False,
        "fixture_kind": "generated synthetic linear mapping",
        "seed": seed,
        "steps": steps,
        "device": "cpu",
        "dtype": "float32",
        "input_shape": list(inputs.shape),
        "base_weight_shape": [out_features, in_features],
        "rank": rank,
        "alpha": alpha,
        "lora_trainable_parameters": model.trainable_parameter_count(),
        "base_parameters_trainable": any(parameter.requires_grad for parameter in model.base.parameters()),
        "initial_mse": initial_mse,
        "final_mse": final_mse,
        "merge_max_abs_error": float((model(inputs) - model.merged_layer()(inputs)).abs().max().item()),
        "claim_boundary": "algebra/implementation smoke test only; not model quality, NLP, Persian, benchmark, hardware or deployment evidence",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline PEFT algebra and synthetic LoRA lab")
    parser.add_argument("--mode", choices=("audit", "toy-lora"), required=True)
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="directory for run.json")
    parser.add_argument("--steps", type=int, default=500)
    args = parser.parse_args()
    if args.mode == "audit":
        if args.fixture is None:
            parser.error("--fixture is required for --mode audit")
        result = audit_fixture(args.fixture)
    else:
        result = run_toy_demo(steps=args.steps)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "run.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```
