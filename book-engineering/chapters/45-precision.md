# جلد سوم، فصل ۱۳ — دقت عددی، BF16، FP16، FP8 و Quantization

**نگاشت:** فصل محلی ۱۳ جلد سوم = فصل سراسری ۴۵. **تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶.** فصل ۴۲ شمار پارامترها و بودجهٔ مدل را برآورد کرد؛ فصل ۴۴ یک حلقهٔ پیش‌آموزش FP32 و checkpoint/resume آزمود. این فصل آن‌ها را دوباره پیاده نمی‌کند: می‌پرسد چه وقت و با چه شواهدی می‌توان نمایش عددها و اجرای محاسبات را کم‌دقت‌تر کرد، و کدام وضعیت precision باید همراه یک run بماند. خروجی، انتخاب آگاهانه میان FP32، FP16، BF16، FP8 و quantization بر پایهٔ workload و سخت‌افزار است؛ نه دستور «همیشه ۸ بیت».

**پیش‌نیاز:** tensor، loss و optimizer از فصل‌های ۴۱–۴۴؛ مفهوم ظرفیت خام از فصل ۴۲؛ جداسازی train/validation/test از فصل ۴۳. **پروژه:** یک آزمایشگاه CPU قطعی که حدود dtypeها را در runtime می‌خواند، underflow/overflow را مشاهده می‌کند، BF16 autocast را با مرجع FP32 می‌سنجد و quantization صحیح را با خطای بازسازی و اشباع مقایسه می‌کند. این پروژه هیچ benchmark مدل یا GPU اجرا نمی‌کند.

![شکل ۳-۱۳-۱ — مقایسهٔ FP32، FP16، BF16 و FP8 E4M3/E5M2 برحسب بیت‌های sign/exponent/fraction؛ مسیر AMP per-op و مسیر Quantization از calibration و scale/zero-point تا rounding و clamp و سپس validation روی سخت‌افزار مقصد.](assets/images/babak-ai/v3-ch13-precision.webp)

**شکل ۳-۱۳-۱ —** تعداد bit کمتر، به‌تنهایی به معنی دقت task بهتر یا اجرای سریع‌تر نیست. قالب، scale، سیاست عملگرها، kernel و معیار کیفیت باید با هم سنجیده شوند. شکل شماتیک است و پشتیبانی هیچ GPU خاصی را تضمین نمی‌کند.

## ۱. پرسش فصل: کدام محاسبه را می‌توان کم‌دقت‌تر کرد؟

هر عدد ذخیره‌شده در یک tensor از یک قرارداد نمایش پیروی می‌کند. انتخاب آن قرارداد بر مقدارهای قابل نمایش، فاصلهٔ بین عددها، حافظهٔ خام و گاهی مسیر محاسبهٔ سخت‌افزار اثر می‌گذارد. در آموزش، برای وزن، activation، gradient، accumulator و state بهینه‌ساز ممکن است قراردادهای متفاوتی به‌کار رود؛ در inference، مدل ممکن است وزن‌های quantized و activationهای پویا داشته باشد. عبارت «مدل BF16 است» این جزئیات را پنهان می‌کند.

هدف مهندسی این نیست که همه‌جا کوچک‌ترین dtype را به‌کار ببریم. ابتدا FP32 یا یک baseline معتبر داریم؛ سپس کاهش دقت را روی همان داده، ورودی‌ها، metricها و backend آزمایش می‌کنیم. می‌پرسیم: آیا خروجی‌ها و گرادیان‌ها متناهی‌اند؟ آیا خطای عددی در حد بودجه است؟ آیا کیفیت validation پذیرفتنی است؟ آیا kernel مقصد واقعاً از آن قالب پشتیبانی می‌کند و latency/حافظه بهتر شده است؟ اگر یکی از این پاسخ‌ها نامعلوم باشد، صرف وجود dtype در کتابخانه مدرک کافی نیست.

## ۲. بیت‌های یک عدد شناور

قالب دودویی شناور معمولاً یک بیت علامت `s`، فیلد نما `e` و فیلد fraction یا significand دارد. برای عدد نرمال دودویی، ارزش تقریبی را می‌توان چنین نوشت:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="عدد شناور نرمال دودویی برابر منفی یک به توان بیت علامت ضربدر یک ممیز fraction در مبنای دو ضربدر دو به توان نمای ذخیره‌شده منهای bias است">
  <mrow><mi>x</mi><mo>=</mo><msup><mrow><mo>(</mo><mo>−</mo><mn>1</mn><mo>)</mo></mrow><mi>s</mi></msup><mo>×</mo><msub><mrow><mo>(</mo><mn>1</mn><mo>.</mo><mi>f</mi><mo>)</mo></mrow><mn>2</mn></msub><mo>×</mo><msup><mn>2</mn><mrow><mi>e</mi><mo>−</mo><mi>bias</mi></mrow></msup></mrow>
</math>

**متن جایگزین فرمول:** عدد شناور نرمال دودویی برابر منفی یک به توان بیت علامت ضربدر یک ممیز fraction در مبنای دو ضربدر دو به توان نمای ذخیره‌شده منهای bias است.

در عددهای نرمال، یک بیت پیشروِ significand معمولاً ضمنی است. عددهای subnormal نزدیک صفر را با معنادهی متفاوت به نما و fraction نمایش می‌دهند؛ این‌ها می‌توانند فاصلهٔ میان صفر و کوچک‌ترین عدد نرمال را پُر کنند، اما همهٔ سخت‌افزارها یا مسیرهای محاسبه رفتار یکسانی با آن‌ها ندارند. الگوهای بیت هم ممکن است برای ±Inf، NaN و صفر علامت‌دار رزرو شوند. جزئیات به استاندارد همان قالب بستگی دارد؛ برای FP8 نباید قواعد FP16 را خودکار تعمیم داد.

این نمایش یک **تقریب محدود** است. بیشتر اعداد ده‌دهی مثل `0.1` در نمایش دودویی finite دقیق نیستند؛ چند عمل پشت‌سرهم گرد می‌شوند. حتی FP32 هم «حساب حقیقی دقیق» نیست، بلکه یک baseline عملی رایج با دامنه و fraction بزرگ‌تر از قالب‌های کم‌بیت است.

## ۳. دامنه و تفکیک‌پذیری یک چیز نیستند

تعداد بیت‌های نما عمدتاً روی dynamic range، یعنی بازهٔ توان‌های قابل نمایش، اثر دارد. تعداد بیت‌های fraction روی دقت نسبی و فاصلهٔ عددهای متوالی در یک بازه اثر می‌گذارد. بنابراین ممکن است قالبی عددهای خیلی بزرگ و خیلی کوچک را بپذیرد اما بین دو مقدار نزدیک، فاصلهٔ درشت‌تری داشته باشد.

برای یک قالب binary با `m` بیت fraction ذخیره‌شده، فاصلهٔ نسبی نزدیک ۱ در حالت نرمال تقریباً چنین است؛ این epsilon ویژگی local است، نه خطای مطلق همهٔ عمل‌ها:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="فاصلهٔ ماشین نزدیک یک برای m بیت fraction تقریباً دو به توان منفی m است">
  <mrow><mi>ε</mi><mo>≈</mo><msup><mn>2</mn><mrow><mo>−</mo><mi>m</mi></mrow></msup></mrow>
</math>

**متن جایگزین فرمول:** فاصلهٔ ماشین نزدیک یک برای m بیت fraction تقریباً دو به توان منفی m است.

برای نمونه، FP16 با ۱۰ بیت fraction نزدیک ۱ گام ریزتری از BF16 با ۷ بیت fraction دارد؛ BF16 در عوض تعداد بیت نمای بیشتری دارد. این مقایسه نمی‌گوید یکی برای همهٔ مدل‌ها بهتر است. اگر activation از range بیرون بزند، fraction دقیق‌تر نجاتش نمی‌دهد؛ اگر به‌روزرسانی وزن از گام‌های قالب کوچک‌تر باشد، range بزرگ به‌تنهایی تغییر وزن را حفظ نمی‌کند.

## ۴. جدول مقایسهٔ قالب‌ها

جدول زیر مشخصات رایج دودویی را نشان می‌دهد. ستون `max finite` بیشینهٔ عدد متناهیِ مثبت است، نه تضمین دامنهٔ GEMM یا رفتار overflow در هر backend. `smallest normal` زیرنورمال‌ها را فهرست نمی‌کند. `epsilon` فاصلهٔ تقریبی نزدیک ۱ است. ارقام FP8 مطابق OCP OFP8 revision 1.1 و مقادیر `torch.finfo` در محیط پروژه‌اند [۱، ۲].

| قالب | sign / exponent / fraction | بیشینهٔ متناهی | کوچک‌ترین نرمال | epsilon نزدیک ۱ | بایت هر مقدار |
|---|---:|---:|---:|---:|---:|
| FP32 | 1 / 8 / 23 | حدود `3.403×10^38` | حدود `1.175×10^-38` | `1.192×10^-7` | 4 |
| FP16 (binary16) | 1 / 5 / 10 | `65,504` | `2^-14 ≈ 6.104×10^-5` | `2^-10 ≈ 9.766×10^-4` | 2 |
| BF16 | 1 / 8 / 7 | حدود `3.390×10^38` | حدود `1.175×10^-38` | `2^-7 = 0.0078125` | 2 |
| FP8 E4M3 | 1 / 4 / 3 | `448` | `2^-6 = 0.015625` | `0.125` | 1 |
| FP8 E5M2 | 1 / 5 / 2 | `57,344` | `2^-14 ≈ 6.104×10^-5` | `0.25` | 1 |

ذخیرهٔ خامِ یک میلیون مقدار، بدون scale، alignment، padding، optimizer state یا activationها، تقریباً 4 MB برای FP32، 2 MB برای هر دو قالب ۱۶بیتی، و 1 MB برای FP8 است؛ MB ده‌دهی است. این **محاسبهٔ کل حافظهٔ run نیست** و جای بودجهٔ tensorها در فصل ۴۲ را نمی‌گیرد. بعضی زیرنورمال‌ها پایین‌تر از ستون `smallest normal` هستند؛ سخت‌افزار می‌تواند آن‌ها را با کارایی یا حتی رفتار متفاوت اجرا کند.

## ۵. FP32: مرجع مقایسه، نه حقیقت بی‌خطا

FP32 معمولاً انتخاب مفیدی برای مرجع، حساسیت‌سنجی و بخش‌هایی از optimizer است؛ بسیاری از چارچوب‌ها برای وزن‌های پارامتری FP32 می‌مانند و محاسباتی را در dtype کوچک‌تر انجام می‌دهند. اما FP32 نیز گردکردن دارد، جمع متوالی‌اش جابجاپذیرِ عددی نیست، و نتیجه به ترتیب reduction و kernel وابسته می‌تواند باشد.

پس «مقایسه با FP32» یعنی مقایسه با یک اجرای تعریف‌شده: همان مدل، داده، seed، mask، ترتیب operationها، نسخهٔ نرم‌افزار و مسیر سخت‌افزار تا حد ممکن. اگر خود baseline ناپایدار یا متفاوت باشد، مشاهدهٔ اختلاف BF16/FP8 به‌تنهایی نمی‌گوید خطا از کجاست. برای تصمیم، هم metricهای عددی مانند max absolute error و finite بودن و هم metric اصلی task لازم است.

## ۶. Mixed precision با Quantization چه تفاوتی دارد؟

**Mixed-precision training** معمولاً بخشی از محاسبات forward/backward را با dtype شناور کوچک‌تر انجام می‌دهد و بخشی را با dtype مناسب‌تر نگه می‌دارد؛ چارچوب ممکن است برای هر عملگر policy جدا داشته باشد. وزن مرجع یا state بهینه‌ساز می‌تواند FP32 بماند. این یعنی انتخاب dtype هنگام اجرای عملیات، نه الزاماً تبدیل دائمی تمام وزن‌های مدل.

**Quantization** نگاشت مقدارهای شناور به کدهای محدودتر، به‌همراه scale، zero-point یا metadata لازم است؛ سپس kernel ممکن است روی کدهای صحیح/شناور کم‌بیت کار کند یا در بعضی workflowها فقط وزن quantized را ذخیره کند و محاسبه را در dtype دیگری انجام دهد. FP8 هرچند قالب شناور است، در recipeهای FP8 برای دامنهٔ کوچک معمولاً با scaling و انتخاب دانه‌بندی همراه می‌شود؛ پس «FP8» می‌تواند هم dtype و هم بخشی از یک طرح quantization باشد.

سه سؤال را جدا نگه دارید: **چه قالبی ذخیره می‌شود؟ چه دقتی در ضرب/جمع واقعی استفاده می‌شود؟ کدام الگوریتم scale و کدام kernel اجرا می‌شود؟** به‌ویژه، checkpoint شامل وزن BF16، مدل quantized برای inference و آموزش با FP8 سه artifact یا workflow یکسان نیستند.

## ۷. AMP: سیاست per-op به‌جای `model.half()`

در PyTorch 2.6، `torch.autocast` ناحیه‌ای از برنامه را پوشش می‌دهد و بر حسب device، dtype درخواستی و فهرست عملگرهای واجد شرایط، dtype مناسب را انتخاب می‌کند. مستندات پیشنهاد می‌کند forward و محاسبهٔ loss را در autocast بگذاریم، backward را بیرون آن اجرا کنیم و هنگام autocast مدل/ورودی‌ها را دستی به `half()` تبدیل نکنیم [۲]. عملگرهای reduction یا حساس ممکن است به dtype دقیق‌تری نیاز داشته باشند.

نمونهٔ کلی CUDA با FP16؛ مدل و optimizer در این مثال به‌طور پیش‌فرض وزن FP32 دارند:

```python
import torch

model = model.to("cuda")
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
scaler = torch.amp.GradScaler("cuda")

for inputs, targets in loader:
    optimizer.zero_grad(set_to_none=True)
    with torch.autocast(device_type="cuda", dtype=torch.float16):
        logits = model(inputs)
        loss = loss_fn(logits, targets)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

این API نمونه است، نه تضمین این‌که هر operator، شکل tensor یا کارت، FP16 سریع را اجرا کند. CPU BF16 در PyTorch 2.6 با همان ایده قابل آزمایش است؛ در پروژه فقط `nn.Linear` کوچک را اجرا می‌کنیم. اجرای CPU autocast به معنی شتاب در هر CPU نیست. policy و API را با نسخهٔ نصب‌شدهٔ PyTorch تطبیق دهید؛ APIهای قدیمی `torch.cuda.amp.autocast` در این نسخه deprecated اعلام شده‌اند [۲].

## ۸. FP16 و loss scaling: راهی برای underflow، نه داروی هر خطا

FP16 بیشینهٔ متناهی `65,504` دارد و gradientهای خیلی کوچک ممکن است هنگام cast به صفر گرد شوند. اگر gradient صفر شود، update متناظر وزن عملاً از دست می‌رود. **Loss scaling** loss را پیش از backward در `S` ضرب می‌کند؛ گرادیان scale‌شده بزرگ‌تر است و پس از backward باید پیش از optimizer به اندازهٔ `S` unscale شود:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="اگر loss در S ضرب شود، gradient آن هم در S ضرب می‌شود و پیش از optimizer باید بر S تقسیم شود">
  <mrow><mi>L</mi><mo>′</mo><mo>=</mo><mi>S</mi><mi>L</mi><mo>,</mo><mspace width="0.5em"/><mfrac><mrow><mi>∂</mi><mi>L</mi><mo>′</mo></mrow><mrow><mi>∂</mi><mi>θ</mi></mrow></mfrac><mo>=</mo><mi>S</mi><mfrac><mrow><mi>∂</mi><mi>L</mi></mrow><mrow><mi>∂</mi><mi>θ</mi></mrow></mfrac></mrow>
</math>

**متن جایگزین فرمول:** اگر loss در S ضرب شود، gradient آن هم در S ضرب می‌شود و پیش از optimizer باید بر S تقسیم شود.

`GradScaler` می‌تواند وقتی Inf/NaN می‌بیند optimizer step را رد و scale را کاهش دهد؛ پس scale و تعداد stepهای ردشده بخشی از وضعیت قابل‌مشاهده‌اند. Scaling جلو overflow در activation/forward را نمی‌گیرد و هر خطای quantization را هم اصلاح نمی‌کند. PyTorch 2.6 صریحاً هشدار می‌دهد AMP/FP16 برای همهٔ مدل‌ها مناسب نیست: مثلاً مدل‌هایی که در BF16 با دامنهٔ بزرگ آموزش دیده‌اند ممکن است در FP16 overflow کنند؛ scale حتی می‌تواند به زیر ۱ برسد و افزایش همیشگی را تضمین نمی‌کند [۲].

در probe پروژه، `1e-8` با `torch.float16` روی CPU به صفر رفت و `±100000` به ±Inf تبدیل شد. این مشاهده با حدود جدول سازگار است، اما تست cast روی CPU، رفتار تمام kernelها یا training واقعی را ثابت نمی‌کند. اگر loss یا grad غیرمتناهی است، ابتدا ریشه‌یابی کنید؛ scale بزرگ‌تر را بی‌دلیل افزایش ندهید.

## ۹. BF16: دامنهٔ گسترده‌تر، significand کوتاه‌تر

BF16 تعداد بیت نمایی برابر FP32 دارد و تنها ۷ بیت fraction ذخیره می‌کند. بنابراین سقف و کف نرمال آن به‌طور کلی به FP32 نزدیک است، اما فاصلهٔ مقدارهای نزدیک بیشتر است. در قیاس با FP16، خطر overflow ناشی از دامنه برای خیلی از activationها کمتر می‌شود؛ در عوض خطای گردکردن، از دست‌رفتن تغییرهای کوچک و accumulation همچنان باید بررسی شود. BF16 نه «FP32 دو بایتی» است و نه معادل عددی FP16.

در تجربهٔ Google روی TPUهای نسل دوم/سوم، ضرب ماتریسی BF16 با accumulation در FP32 توصیف شده است؛ این یک پیاده‌سازی سخت‌افزاری مشخص است، نه تضمین PyTorch برای تمام دستگاه‌ها [۳]. پژوهش BF16 هم workloadها و رفتار قالب را می‌سنجد، نه ثبات بی‌قیدوشرط هر مدل [۴]. BF16 معمولاً به loss scaling مانند FP16 نیاز کمتری دارد چون range وسیع‌تر است، اما range به‌تنهایی پایداری را تضمین نمی‌کند.

در پروژهٔ این فصل، PyTorch 2.6.0+cpu، خروجی Linear زیر CPU autocast را BF16 و متناهی گزارش کرد؛ وزن Linear پس از آن FP32 ماند. اختلاف بیشینهٔ خروجی این fixture کوچک با مرجع FP32 حدود `0.002292` بود. این عدد فقط نمونهٔ قابل‌بازتولید همین seed، شکل و runtime است؛ threshold کیفیت برای مدل دیگری نیست.

## ۱۰. ضرب، accumulation، وزن مرجع و state optimizer

واحدهایی که روی آن‌ها دقت را انتخاب می‌کنیم جدا هستند: ورودی، وزن ذخیره‌شده، operand ضرب، accumulator جمع حاصل‌ضرب‌ها، gradient، وزن پس از update و momentهای optimizer. ممکن است عملگر ضرب با BF16 انجام شود و حاصل‌جمع با FP32؛ ممکن است backend برای یک شکل دیگر مسیر متفاوتی برگزیند. این جزئیات را از API یا سند سخت‌افزار همان runtime بگیرید، نه از نام dtype ورودی.

در بعضی recipeهای mixed precision، وزن master و state بهینه‌ساز FP32 می‌مانند تا update کوچک گم نشود؛ هزینهٔ حافظه هم در آن صورت صرفاً `N×2` بایتِ BF16 نیست. راه دیگر، optimizer کم‌دقت یا ذخیرهٔ state فشرده است که tradeoff دیگری دارد. مثال‌های آموزشی یا مستندات paper را نسخهٔ عمومی همهٔ فریم‌ورک‌ها فرض نکنید. از `torch.finfo` برای حدود dtype و از profiler / kernel documentation برای رفتار محاسبه استفاده کنید.

اگر وزن هر قدم به BF16 گرد شود، updateی که از نصف گام محلی کوچک‌تر است ممکن است در وزن گرد‌شده تغییر ندهد؛ ولی optimizer state می‌تواند آن را انباشته کند و بعد تغییر قابل‌نمایش ایجاد شود. نتیجۀ کار به ترتیب update، rounding و optimizer وابسته است. آزمون حداقلی: log کردن norm گرادیان و update، شمار وزن‌های بی‌تغییر و loss/metric روی run مرجع و run کم‌دقت.

## ۱۱. FP8: دو مصالحهٔ متفاوت، نه یک قالب واحد

مشخصات OCP OFP8 revision 1.1 دو binary interchange format تعریف می‌کند [۱]:

- **E4M3**: یک بیت sign، چهار بیت exponent، سه بیت fraction؛ بیشینهٔ متناهی `448`. این قالب infinity را نمایش نمی‌دهد و برای دامنهٔ بیشتر، تعداد الگوهای NaN محدودی دارد.
- **E5M2**: یک بیت sign، پنج بیت exponent، دو بیت fraction؛ بیشینهٔ متناهی `57,344` و الگوهای infinity/NaN دارد. دامنهٔ بزرگ‌تر را با fraction کوتاه‌تر می‌خرد.

هر دو ۸بیتی‌اند، اما E4M3 در بخش متناهی تفکیک‌پذیری بیشتری و E5M2 دامنهٔ بیشتری دارد. مقالهٔ FP8 این قالب‌ها را در طرح‌های آموزش و post-training بررسی می‌کند و نشان می‌دهد انتخاب format، scale و tensor/workload اهمیت دارد؛ نتایج paper تضمین دقت همهٔ شبکه‌ها نیست [۵]. OCP v1.1 هم conversion از قالب‌های عریض‌تر، rounding ties-to-even و گزینه‌های overflow/saturation را دقیق می‌کند؛ اگر تبدیل از سقف خارج شود، نتیجه به حالت conversion بستگی دارد [۱].

نام‌های PyTorch شامل `torch.float8_e4m3fn` و `torch.float8_e5m2` هستند. در PyTorch 2.6 CPU probe می‌تواند آن‌ها را به کار گیرد و cast را گزارش کند، اما این **به معنی پشتیبانی همهٔ عملیات tensor، GEMM سریع یا hardware FP8 نیست**. حتی اگر نوع داده قابل ساخت باشد، عملگر، شکل، scaling recipe و kernel باید جدا بررسی شوند.

## ۱۲. Scaling در FP8: amax، دانه‌بندی و تاریخچه

اگر مقدارهای یک tensor خارج از دامنهٔ FP8 باشند، پیش از cast آن‌ها را با scale نرمال می‌کنیم و پس از محاسبه بازمی‌گردانیم. با قرارداد «scale در واحد مقدار اصلی»، برای بیشینهٔ قدر مطلق مشاهده‌شده `amax` و حد مثبت قابل نمایش `qmax`:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="برای scale ذخیره‌شده به‌صورت مقدار اصلی بر کد کم‌بیت، scale برابر amax تقسیم بر qmax است؛ کد با گردکردن x تقسیم بر scale ساخته می‌شود و بازسازی در scale ضرب می‌شود">
  <mrow><mi>s</mi><mo>=</mo><mfrac><mi>amax</mi><msub><mi>q</mi><mi>max</mi></msub></mfrac><mo>,</mo><mspace width="0.5em"/><mi>q</mi><mo>=</mo><mi>round</mi><mo>(</mo><mfrac><mi>x</mi><mi>s</mi></mfrac><mo>)</mo><mo>,</mo><mspace width="0.5em"/><mover><mi>x</mi><mo>^</mo></mover><mo>=</mo><mi>s</mi><mi>q</mi></mrow>
</math>

**متن جایگزین فرمول:** برای scale ذخیره‌شده به‌صورت مقدار اصلی بر کد کم‌بیت، scale برابر amax تقسیم بر qmax است؛ کد با گردکردن x تقسیم بر scale ساخته می‌شود و بازسازی در scale ضرب می‌شود.

بعضی کتابخانه‌ها reciprocal scale را ذخیره می‌کنند؛ پیش از مقایسهٔ عددها قرارداد را بخوانید. `amax` جاری، سابقهٔ چند گام، scale هر tensor یا scale هر row/block از recipeهای ممکن‌اند. scale تانسری سربار کم دارد اما یک outlier می‌تواند دقت بیشتر عناصر را کم کند؛ scale ریزدانه این اثر را محدود می‌کند ولی metadata و kernel پیچیده‌تر می‌شوند. راهنمای NVIDIA Transformer Engine current-iteration amax و delayed scaling بر پایهٔ تاریخچه را به‌عنوان recipeهای متفاوت توضیح می‌دهد؛ آن‌ها API عمومی برای همهٔ سخت‌افزارها نیستند [۶].

جای داده هم مهم است: weights، activations و gradientها شکل توزیع و دامنهٔ متفاوتی دارند؛ برای همهٔ آن‌ها یک scale ثابت یا یک قالب واحد را مفروض نگیرید. در آموزش recipe ممکن است برای backward نیز state یا history مربوط به amax نگه دارد. اگر run قابل resume می‌خواهیم، این state، dtype policy و config باید در checkpoint ثبت شوند؛ فصل ۴۴ چنین AMP/FP8 stateای را در پروژهٔ FP32 خود پیاده نکرده بود.

## ۱۳. MXFP8 و مقیاس بلوکی در OCP MX

«FP8 E4M3/E5M2» قالب عنصر را می‌گوید؛ «MXFP8» یک بستهٔ داده و scale بلوکی را تعریف می‌کند. در OCP MicroXcaling v1.1، بلوک MXFP8 شامل ۳۲ عنصر FP8 است و scale مشترک ۸بیتی `UE8M0` دارد؛ نسخهٔ اکتبر ۲۰۲۶ نام قدیمی `E8M0` را به `UE8M0` تغییر داده و rounding و edge caseهای تبدیل را روشن‌تر می‌کند [۷]. مشخصات MX، باینری FP8 پایه را از مشخصات OFP8 می‌گیرد؛ این یک format package است، نه اثبات این‌که هر دستگاه آن را اجرا می‌کند.

برای بلوک `b` می‌توان scale مفهومی `s_b` را از `amax_b` برآورد کرد؛ در MX جزئیات scale به encoding و الگوریتم استاندارد وابسته است و الزاماً همان float scale پیوستهٔ مثال قبلی نیست. اندازهٔ بلوک، outlierهای داخل بلوک و امکان استفاده از native kernel بر کیفیت و performance اثر دارند. پیاده‌سازی مجاز است تنها زیرمجموعه‌ای از قالب‌های MX را پشتیبانی کند؛ بنابراین MXFP8 را از روی نام روی هر GPU فرض نکنید [۷].

## ۱۴. Quantization صحیح با scale و zero-point

در quantization affine، مقدار شناور `x` به کد صحیح محدودشده تبدیل می‌شود و پس از inference می‌توان تقریب شناور آن را بازسازی کرد. `s>0` scale و `z` zero-point است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="کد صحیح q برابر clamp گرد کردن x تقسیم بر scale به‌علاوهٔ zero point میان q کمینه و q بیشینه است و مقدار بازسازی‌شده scale ضربدر q منهای zero point است">
  <mrow><mi>q</mi><mo>=</mo><mi>clamp</mi><mo>(</mo><mi>round</mi><mo>(</mo><mfrac><mi>x</mi><mi>s</mi></mfrac><mo>+</mo><mi>z</mi><mo>)</mo><mo>,</mo><msub><mi>q</mi><mi>min</mi></msub><mo>,</mo><msub><mi>q</mi><mi>max</mi></msub><mo>)</mo><mo>,</mo><mspace width="0.5em"/><mover><mi>x</mi><mo>^</mo></mover><mo>=</mo><mi>s</mi><mo>(</mo><mi>q</mi><mo>−</mo><mi>z</mi><mo>)</mo></mrow>
</math>

**متن جایگزین فرمول:** کد صحیح q برابر clamp گرد کردن x تقسیم بر scale به‌علاوهٔ zero point میان q کمینه و q بیشینه است و مقدار بازسازی‌شده scale ضربدر q منهای zero point است.

برای symmetric signed INT8 اغلب `z=0` و بازهٔ متقارن انتخاب می‌شود؛ در پروژه `[-127,127]` به‌کار رفته تا صفر دقیقاً در مرکز باشد. affine INT8 می‌تواند کل بازهٔ `[-128,127]` را به min/max کالیبراسیون نگاشت کند. `round` و clamp باعث می‌شود دو خطا را جدا ببینیم: **rounding error** برای مقدار داخل دامنه، و **saturation/clipping** برای مقدار بیرون دامنه. PyTorch `torch.round` در این مثال round-to-nearest, ties-to-even انجام می‌دهد؛ فرمت یا kernel دیگری ممکن است سیاست متفاوت مستندشده داشته باشد.

## ۱۵. Per-tensor در برابر per-channel، per-row و per-group

Scale می‌تواند برای کل tensor مشترک باشد، برای هر کانال وزن جدا باشد، برای هر row/token activation تغییر کند یا برای بلوک‌های کوچک‌تر نگهداری شود. هرچه granularity محلی‌تر باشد، یک outlier کمتر عناصر دور از خود را می‌کشد؛ در عوض scaleهای بیشتری ذخیره و بارگذاری می‌شوند و layout/kernel باید آن را پشتیبانی کند. «دانه‌بندی دقیق‌تر» به‌تنهایی تضمین کیفیت یا کارایی نیست.

اگر calibration فقط مقادیر بین `−1` و `1` را دیده باشد و inference مقدار `1.4` یا `−1.5` تولید کند، scale ثابت می‌تواند آن‌ها را به سقف/کف ببرد. سهم مقدارهای clamp‌شده را گزارش کنید:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="نسبت اشباع تعداد مقدارهای خارج از qmin و qmax پیش از clamp تقسیم بر کل مقدارها است">
  <mrow><mi>r</mi><mo>_</mo><mi>sat</mi><mo>=</mo><mfrac><mrow><mi>count</mi><mo>(</mo><mi>q</mi><mo>&lt;</mo><msub><mi>q</mi><mi>min</mi></msub><mo>∨</mo><mi>q</mi><mo>&gt;</mo><msub><mi>q</mi><mi>max</mi></msub><mo>)</mo></mrow><mi>N</mi></mfrac></mrow>
</math>

**متن جایگزین فرمول:** نسبت اشباع تعداد مقدارهای خارج از qmin و qmax پیش از clamp تقسیم بر کل مقدارها است.

این شمارش قبل از clamp است؛ اگر فقط کدهای نهایی را ببینید، نمی‌فهمید چند مقدار به یک endpoint فرو ریخته‌اند. کالیبراسیون باید نمایندهٔ ورودی deployment باشد؛ test نهایی را برای تنظیم scale یا انتخاب recipe مصرف نکنید. در پروژه، per-group فقط روی بردار flatten‌شده و گروه‌های چهارتایی تمرین می‌شود؛ این معادل layout کانال‌های یک لایه یا MXFP8 ۳۲تایی نیست.

## ۱۶. PTQ، dynamic و weight-only: زمان محاسبهٔ scale

**Post-training quantization (PTQ)** بعد از آموزش، وزن‌ها و گاهی activation را تبدیل می‌کند. در static PTQ، دادهٔ calibration برای بازه یا پارامترهای activation به‌کار می‌رود؛ اگر توزیع deployment فرق کند، clipping/error تغییر می‌کند. در dynamic quantization، بازهٔ activation در زمان اجرا از ورودی تازه برآورد می‌شود؛ این انعطاف می‌تواند محاسبهٔ اضافه بخواهد. در weight-only، وزن فشرده است اما activation یا matmul ممکن است با دقت دیگری انجام شود.

این‌ها tradeoffهای روش‌اند، نه سه اسم برای یک عملگر. هنگام ذخیره، همراه weightهای quantized، نوع قالب، scale/zero-point، granularity، نسخهٔ تبدیل و محدودیت kernel را هم نگه دارید. PyTorch/TorchAO فهرست workflowهای متفاوت برای FP8، INT8، INT4 و weight-only دارد؛ API و پشتیبانی hardware در نسخه‌ها تغییر می‌کند [۸].

## ۱۷. QAT: شبیه‌سازی خطا پیش از تبدیل نهایی

در **Quantization-Aware Training (QAT)** forward هنگام آموزش، rounding و clamp را با fake-quantization شبیه‌سازی می‌کند؛ tensor در مرحلهٔ آموزش می‌تواند همچنان float باشد و `x̂` را به محاسبه می‌دهد. گرادیان از عملگر گردکردن مشتق معمولی ندارد، پس بعضی پیاده‌سازی‌ها از straight-through estimator یا تخمین گرادیان تعریف‌شده استفاده می‌کنند. در پایان، convert وزن‌ها و kernel مناسب را می‌سازد؛ `prepare → train/fine-tune → convert → evaluate` یک workflow معمول است [۹].

QAT ممکن است مدل را با خطای هدف سازگارتر از PTQ کند، اما هزینهٔ آموزش دارد و نتیجه‌اش تضمین نشده است. fake-quant forward به‌تنهایی ثابت نمی‌کند deployment دقیقاً همان مسیر int8 یا fp8 را اجرا می‌کند؛ post-convert benchmark و task metric همچنان لازم‌اند. نسخهٔ API را pin کنید، چون صفحهٔ TorchAO که در این پژوهش دیده شد `v0.17.0 (unstable)` را کنار `v0.16.0 (stable)` نشان می‌داد [۸، ۹].

## ۱۸. پایداری عددی: کجا اختلاف کوچک بزرگ می‌شود؟

خطای گردکردن در زنجیرهٔ operationها جمع می‌شود؛ تفریق دو عدد نزدیک می‌تواند رقم‌های معنادار را حذف کند (cancellation)؛ جمع شناور associative نیست؛ reduction با ترتیب دیگری می‌تواند خروجی کم‌وبیش متفاوتی بسازد. در مدل عمیق، activation یا gradient می‌تواند از دامنهٔ قالب بیرون رود یا آن‌قدر کوچک شود که به صفر round شود. این‌ها رخدادهای متفاوت‌اند و راه‌حل‌شان یکی نیست.

برای هر run کم‌دقت ثبت کنید: `isfinite` روی loss/gradient/output، norm گرادیان، شمار overflow/step ردشده، max activation یا amax، نرخ اشباع quantization، خطای خروجی نسبت به baseline و metric task روی validation. اگر training منحرف شد، یک عامل را تغییر دهید: dtype یک بخش، loss scaling، granularity، calibration یا accumulation policy. با هم تغییر دادن precision و LR و batch امکان عیب‌یابی را از بین می‌برد.

هیچ epsilon واحدی تضمین نمی‌کند «تغییر بی‌اهمیت» است. برای خروجی‌های نزدیک صفر، relative error می‌تواند گمراه‌کننده شود؛ absolute error، cosine similarity یا KL روی logits هم ممکن است برای هدف شما مناسب‌تر باشد. بودجهٔ خطا باید به خروجی و task مربوط باشد. پاسخ خوب فقط «loss پایین ماند» نیست: واحد داده، معیار، تعداد نمونه، reference و حالت اشباع را مشخص می‌کند.

## ۱۹. سازگاری سخت‌افزار: dtype حاضر ≠ kernel حاضر

حداقل چهار لایهٔ سازگاری را تفکیک کنید:

1. آیا نسخهٔ framework نوع داده را می‌شناسد و می‌تواند tensor بسازد/تبدیل کند؟
2. آیا همان device و backend عملگرهای مدل را روی آن dtype اجرا می‌کند؟
3. آیا kernel واقعاً کم‌دقت است، accumulation را چگونه انجام می‌دهد و برای ابعاد شما بهینه است؟
4. آیا end-to-end latency/حافظه و کیفیت مدل بهتر شده‌اند؟

PyTorch AMP 2.6 برای CUDA به‌طور پیش‌فرض FP16 و برای CPU BF16 را به‌عنوان autocast dtype پیش‌فرض معرفی می‌کند، اما هر operator از همان مسیر استفاده نمی‌کند [۲]. در صفحهٔ TorchAO main که ۵ نوامبر ۲۰۲۶ به‌روزرسانی شده، یک workflow مشخصِ dynamic FP8 inference برای CUDA با compute capability `≥8.9`، AMD MI350+ یا Intel XPU فهرست می‌شود؛ workflowهای دیگر شرط‌های دیگری دارند [۸]. این محدودیت‌ها را به همهٔ FP8ها تعمیم ندهید و از آن صفحهٔ `main` API ناپایدار را بدون نسخه‌بندی کپی نکنید.

آزمایش محلی این فصل روی CPU است و فقط `torch.finfo`، cast FP8 و CPU BF16 autocast را می‌سنجد. CUDA، ROCm، XPU، MPS، GPU GEMM، OCP MX hardware یا latency در این workspace آزموده نشده‌اند؛ جدول قابلیت‌های پروژه عمداً ادعای آن‌ها را نمی‌کند.

## ۲۰. پروتکل مقایسه: کیفیت، پایداری و throughput

برای مقایسهٔ معتبر، ابتدا ثبت کنید: مدل/checkpoint، data/config hash، tokenizer و split، framework/driver/device، dtype و operation policy، quantization recipe، seed، batch/shape و metric. یک FP32 یا BF16 baseline تعریف کنید؛ بعد همان ورودی و مسیر ارزیابی را به‌کار ببرید. کیفیت را با task metric روی validation بسنجید؛ فقط average loss روی چند batch کوچک کافی نیست.

برای performance، shapeهای واقعی، warm-up، synchronization درست accelerator، تعداد تکرار و توزیع latency را گزارش کنید؛ هزینهٔ scale/cast/packing و memory transfer را هم در زمان end-to-end بگذارید. ماتریس کوچک می‌تواند به‌علت overhead از dtype کم‌دقت سود نبرد. عددهای vendor، paper یا TorchAO متعلق به دستگاه، مدل، نسخه و shape گزارش‌شده‌اند، نه پیش‌بینی latency شما [۵، ۸].

پیش از پذیرش یک recipe، معیار pass/fail را بنویسید: حد مجاز افت task metric، عدم NaN/Inf، سقف saturation و حداقل بهبود latency یا memory روی سخت‌افزار مقصد. Test نهایی را فقط پس از انتخاب recipe اجرا کنید؛ انتخاب براساس test خودش بخشی از data leakage است، همان مرزی که فصل ۴۳ برای ارزیابی نگه داشت.

## ۲۱. Checkpoint precision چه چیز تازه‌ای می‌خواهد؟

پروژهٔ فصل ۴۴ در FP32 وضعیت optimizer، update، ترتیب داده و RNG را برای resume نگه می‌داشت؛ این فصل checkpoint آن پروژه را به‌طور پنهانی به AMP تبدیل نمی‌کند. اگر آن run را با FP16 ادامه می‌دهید، scaler و وضعیت آن را هم ذخیره کنید؛ اگر recipe FP8 به amax history یا scaleهای در حال تغییر متکی است، آن state، dtype policy و نسخهٔ recipe را نیز ثبت کنید. Quantization نهایی inference به calibration qparams، scale، zero-point، format و محدودیت backend نیاز دارد.

نام config را ثبت کنید، نه فقط اسم dtype. برای resume، یکسان بودن وزن‌ها کافی نیست اگر scaler/history/optimizer یا مسیر داده فرق کرده است. برای inference artifact، مدل quantized و metadata لازم را به همراه قرارداد ورودی، framework/kernel موردنیاز و تست سازگاری منتشر کنید. این‌ها ادامهٔ مهندسی checkpoint فصل ۴۴ هستند؛ در آن پروژهٔ کوچک فقط stateهای واقعاً استفاده‌شده ذخیره شده بودند.

## ۲۲. اجرای پروژهٔ CPU

پوشهٔ [`projects/45-precision/`](book-engineering/projects/45-precision/README.md) به داده یا checkpoint بیرونی احتیاج ندارد. در محیطی با Python 3.11+ و PyTorch 2.6.x:

```bash
python book-engineering/projects/45-precision/precision_lab.py
python book-engineering/projects/45-precision/precision_lab.py --output /tmp/ch45-precision.json
(cd book-engineering/projects/45-precision && python -m unittest discover -v)
```

CLI یک گزارش JSON قطعی می‌سازد: `formats` از runtime، `cast_probe` از تبدیل‌های محدود، `cpu_bf16_autocast` از Linear کوچک و `quantization` از یک outlier و یک shift کالیبراسیون. `calculate_qparams` روش متقارن/affine با granularity کلی یا group را پیاده می‌کند؛ `quantize_with_qparams` کد قبل از clamp، reconstruction، MAE/RMSE و saturation را برمی‌گرداند. چیدمان گروهی flatten شده است تا الگوریتم روشن بماند، نه این‌که جای API مدل‌محور را بگیرد.

ده آزمون واحد metadata قالب، underflow/overflow مشاهده‌شده، BF16 autocast، zero-point و حدود int8، خطای per-group در fixture، calibration drift، ورودی نامعتبر و JSON را کنترل می‌کنند. مثال ساده است و نه training loop دارد، نه optimizer، نه benchmark inference واقعی.

## ۲۳. نتایج مشاهده‌شده و مرز استنتاج

در همین clone و PyTorch `2.6.0+cpu`:

- dtypeهای `float8_e4m3fn` و `float8_e5m2` حاضرند و `torch.finfo` بیشینه‌های `448` و `57,344` را می‌دهد؛ این آزمایش فقط cast/storage را ثابت می‌کند.
- در cast آزمایشی، FP16 مقدار `1e-8` را صفر و `±1e5` را ±Inf کرد؛ BF16 این دو مقدار بزرگ را متناهی و گرد‌شده به `±99840` نگه داشت؛ E4M3FN مقدارهای `±1e5` را NaN و E5M2 آن‌ها را Inf گزارش کرد. این مشاهده رفتار cast همین نسخه/CPU است، نه نسخهٔ اجباری تبدیل همهٔ دستگاه‌ها.
- CPU BF16 autocast خروجی متناهی داد؛ بیشینهٔ اختلاف fixture با FP32 `0.002292` بود، نه اندازه‌گیری throughput یا کیفیت مدل.
- در بردار هشت‌تایی با outlier `10`، RMSE per-tensor حدود `0.02753` و per-group حدود `0.02008` شد؛ در آزمایش shift کالیبراسیون ۲ مقدار از ۳ مقدار evaluation اشباع شدند. این دو نتیجه خاص داده‌های مصنوعی همین مثال‌اند.

عددهای بالا برای نشان‌دادن mechanism و regression test کاربرد دارند. هیچ‌یک نتیجهٔ آموزش، دقت benchmark، مزیت کاربردی FP8، latency GPU یا توصیهٔ threshold برای مدل واقعی نیست.

## ۲۴. خطاهای رایج در انتخاب precision

| برداشت نادرست | اصلاح |
|---|---|
| «BF16 چون rangeش بزرگ است، از FP32 دقیق‌تر است.» | BF16 fraction کوتاه‌تری دارد؛ range و resolution جدا هستند. |
| «FP16 فقط نیاز به GradScaler دارد.» | scaler فقط underflow گرادیان را هدف می‌گیرد؛ forward overflow و mismatch مدل ممکن است بماند. |
| «`torch.float8` وجود دارد، پس matmul FP8 سریع است.» | dtype/cast، operator support، kernel واقعی و benchmark شکل هدف چهار ادعای متفاوت‌اند. |
| «یک scale برای tensor کافی است.» | outlier و shift توزیع می‌تواند دقت یا اشباع را تغییر دهد؛ granularity و calibration را اندازه بگیرید. |
| «QAT یعنی inference هم دقیقاً مثل training محاسبه می‌کند.» | fake-quant، convert و kernel deployment را جداگانه validate کنید. |
| «وزن یک‌میلیون‌تایی ۱ MB شد، پس کل run ۱ MB است.» | optimizer، gradient، master copy، activation، scale و overhead لحاظ نشده‌اند. |
| «چون loss finite است، کیفیت حفظ شده.» | task metric، خطا نسبت به مرجع، saturation و validation لازم‌اند. |
| «فرمت OCP روی همهٔ سخت‌افزارها یکسان سریع است.» | interchange format با وجود kernel سخت‌افزاری یا performance مساوی نیست. |

## ۲۵. تمرین‌ها و معیار قبولی

1. از `torch.finfo` جدول FP16/BF16 را در runtime خود بازسازی و توضیح دهید چرا BF16 با وجود ۱۶ bit، range بزرگ‌تری از FP16 دارد.
2. بردار cast را تغییر دهید تا یک مقدار متناهی نزدیک سقف FP16 و یک مقدار کوچک‌تر از کوچک‌ترین مقدار نرمال داشته باشد؛ رفتار صفر، subnormal، Inf و NaN را جدا ثبت کنید.
3. یک activation با outlier بسازید و per-tensor را با گروه‌های ۲، ۴ و ۸ مقایسه کنید. MAE، RMSE، max error و metadata scale را گزارش کنید؛ توضیح دهید چرا نتیجه با گروه‌بندی دیگر ممکن است عوض شود.
4. calibration را حول صفر نگه دارید و evaluation را جابه‌جا کنید. سهم اشباع را به‌دست آورید؛ سپس توضیح دهید calibration پویا یا scale ریزدانه کدام tradeoff را عوض می‌کند.
5. با PyTorch autocast یک Linear FP32 و BF16 بسازید؛ پارامتر و خروجی را از نظر dtype و `isfinite` بررسی کنید. هیچ نتیجهٔ سرعتی بدون benchmark معتبر ادعا نکنید.
6. دربارهٔ FP8 دو سطر بنویسید: در کدام کاربرد دامنهٔ E5M2 ارزشمند است، و چه وقت fraction بیشتر E4M3 مفیدتر می‌شود؟ پاسخ را به amax/scale و role وزن/activation/gradient گره بزنید، نه به یک قانون همیشگی.
7. یک طرح QAT پیشنهاد کنید: calibration/train data، fake-quant range، معیار validation، مدل deployment و نسخه/kernel را مشخص کنید. Test را در انتخاب recipe مصرف نکنید.
8. چک‌لیست checkpoint را برای یک run FP16 و یک recipe FP8 جدا بنویسید: علاوه بر وزن، چه scaler، optimizer، scale/amax history، config و data identity لازم است؟

**معیار قبولی:** دست‌کم ۶ پاسخ از ۸ با واحد، فرض و شواهد؛ ۱۰ آزمون پروژه موفق؛ تفاوت range/precision و AMP/quantization درست توضیح داده شده؛ یک گزارش finite/overflow/saturation و خطای بازسازی ارائه شده؛ هیچ toy output به‌عنوان benchmark معرفی نشده؛ و سازگاری kernel/device جدا از dtype بررسی شده است. پاسخ‌های نمونه در [پاسخ‌نامهٔ تشریحی فصل ۴۵](book-engineering/answers/45-precision-fa.md) آمده‌اند.

### واژه‌نامهٔ کوتاه

- **dtype:** قرارداد قالب و دامنهٔ نمایش هر مقدار عددی.
- **Range:** کمینه/بیشینهٔ قابل‌نمایش؛ با دقت نسبی یکی نیست.
- **BF16/FP16:** قالب‌های شناور ۱۶بیتی با مصالحه‌های متفاوت exponent/fraction.
- **Quantization:** نگاشت عددهای شناور به نمایش کم‌بیت با scale و گاه zero-point.
- **Calibration:** داده/روش تعیین پارامترهای quantization؛ نه تضمین کیفیت task.

## ۲۶. منابع، نسخه‌ها و تاریخ دسترسی

1. Open Compute Project, [OCP 8-bit Floating Point Specification (OFP8), Revision 1.1](https://www.opencompute.org/documents/ocp-8-bit-floating-point-specification-ofp8-revision-1-1-final-pdf/), مؤثر از ۲۲ ژوئن ۲۰۲۶؛ قالب‌ها و تبدیل FP8.
2. PyTorch, [Automatic Mixed Precision package — torch.amp, v2.6](https://docs.pytorch.org/docs/2.6/amp.html) و [Type Info — `torch.finfo`, v2.6](https://docs.pytorch.org/docs/2.6/type_info.html)؛ رفتار AMP و حدود عددی قابل پرس‌وجو.
3. Google Cloud, Wang & Kanwar, [“BFloat16: The secret to high performance on Cloud TPUs”](https://cloud.google.com/blog/products/ai-machine-learning/bfloat16-the-secret-to-high-performance-on-cloud-tpus), ۲۳ اوت ۲۰۱۹؛ BFloat16 semantics و مثال accumulation در TPUهای توصیف‌شده.
4. Kalamkar et al., [“A Study of BFLOAT16 for Deep Learning Training”](https://arxiv.org/abs/1905.12322), ۲۰۱۹؛ بررسی workloadهای مقاله، نه تضمین عمومی.
5. Micikevicius et al., [“FP8 Formats for Deep Learning”](https://arxiv.org/abs/2209.05433), ۲۰۲۲؛ مقایسهٔ formatها و طرح‌های آموزش/PTQ در setupهای مطالعه.
6. NVIDIA Transformer Engine 2.20.2, [Using FP8 and FP4 with Transformer Engine](https://docs.nvidia.com/deeplearning/transformer-engine/examples/fp8_primer.html); توضیح current-iteration `amax`، delayed scaling مبتنی بر تاریخچه و MXFP8 در همین library، نه استاندارد API بین vendorها.
7. Open Compute Project, [OCP MicroXcaling (MX) Specification, v1.1](https://www.opencompute.org/wp-content/uploads/2026/10/OCP_MicroXcaling_Spec_v1.1.0.pdf), ۹ اکتبر ۲۰۲۶؛ بلوک ۳۲تایی MXFP8، UE8M0 و conversion edge cases.
8. PyTorch/TorchAO, [Quantized Inference — `main`, v0.17.0 (unstable)](https://docs.pytorch.org/ao/main/workflows/inference.html), به‌روزرسانی ۵ نوامبر ۲۰۲۶؛ workflowها و شرط‌های سخت‌افزاری در همان نسخه.
9. PyTorch/TorchAO, [Quantization-Aware Training — `main`, v0.17.0 (unstable)](https://docs.pytorch.org/ao/main/workflows/qat.html); fake quantization و APIهای QAT. نسخهٔ stable/unstable را پیش از استفاده بررسی کنید.

پیوندها در ۶ نوامبر ۲۰۲۶ بازبینی شدند. مستندات نسخه‌ای ممکن است تغییر کند؛ برای اجرای واقعی شمارهٔ PyTorch/TorchAO، driver، device و API را در run card pin کنید.

## ۲۷. پیوست اجرایی: پیاده‌سازی کامل آزمایشگاه

فایل زیر همان کدی است که پروژه و آزمون‌های واحد اجرا می‌کنند؛ آن را از پروژه import می‌کنیم و در این پیوست نسخهٔ دومی نمی‌سازیم.

```python
"""A deterministic CPU lab for floating-point formats, AMP and affine quantization.

The program measures storage dtypes and tensor-level quantization error. It does
not benchmark accelerators or claim that a dtype has a fast hardware kernel.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import torch
from torch import nn


FORMAT_SPECS = (
    ("FP32", "float32", 32, "1/8/23"),
    ("FP16", "float16", 16, "1/5/10"),
    ("BF16", "bfloat16", 16, "1/8/7"),
    ("FP8 E4M3FN", "float8_e4m3fn", 8, "1/4/3"),
    ("FP8 E5M2", "float8_e5m2", 8, "1/5/2"),
)


def _json_scalar(value: float) -> float | str:
    """Return a JSON-safe scalar while preserving NaN and infinity labels."""
    number = float(value)
    if math.isnan(number):
        return "nan"
    if math.isinf(number):
        return "inf" if number > 0 else "-inf"
    return number


def format_table() -> list[dict[str, Any]]:
    """Inspect the available PyTorch dtypes instead of assuming their limits."""
    rows: list[dict[str, Any]] = []
    for name, attr, bits, fields in FORMAT_SPECS:
        dtype = getattr(torch, attr, None)
        if dtype is None:
            rows.append({"name": name, "dtype": f"torch.{attr}", "available": False})
            continue
        info = torch.finfo(dtype)
        bytes_per_element = torch.empty((), dtype=dtype).element_size()
        bytes_for_million = bytes_per_element * 1_000_000
        rows.append({
            "name": name,
            "dtype": str(dtype),
            "available": True,
            "bits": bits,
            "sign_exponent_fraction_bits": fields,
            "bytes_per_element": bytes_per_element,
            "max_finite": float(info.max),
            "smallest_normal": float(info.tiny),
            "epsilon_at_one": float(info.eps),
            "million_values_decimal_MB": bytes_for_million / 1_000_000,
            "million_values_MiB": bytes_for_million / (1024 * 1024),
        })
    return rows


def precision_probe(values: list[float] | None = None) -> dict[str, Any]:
    """Cast a fixed FP32 vector down and back, counting under/overflow outcomes."""
    if values is None:
        values = [1e-8, 0.1, 1.001, 1e5, -1e5]
    source = torch.tensor(values, dtype=torch.float32)
    rows: list[dict[str, Any]] = []
    for name, attr, _bits, _fields in FORMAT_SPECS:
        dtype = getattr(torch, attr, None)
        if dtype is None:
            rows.append({"name": name, "available": False})
            continue
        rounded = source.to(dtype).to(torch.float32)
        finite = torch.isfinite(rounded)
        error = (rounded[finite] - source[finite]).abs()
        rows.append({
            "name": name,
            "available": True,
            "roundtrip_values": [_json_scalar(x) for x in rounded.tolist()],
            "nonzero_to_zero_count": int(((source != 0) & (rounded == 0)).sum().item()),
            "infinity_count": int(torch.isinf(rounded).sum().item()),
            "nan_count": int(torch.isnan(rounded).sum().item()),
            "max_abs_error_on_finite_values": float(error.max().item()) if error.numel() else None,
        })
    return {"source_fp32": values, "casts": rows}


def cpu_autocast_probe() -> dict[str, Any]:
    """Compare FP32 Linear with CPU BF16 autocast; this is not a speed benchmark."""
    torch.manual_seed(451)
    model = nn.Linear(8, 4, bias=True).eval()
    inputs = torch.linspace(-1.25, 1.25, 64, dtype=torch.float32).reshape(8, 8)
    with torch.inference_mode():
        reference = model(inputs)
        with torch.amp.autocast(device_type="cpu", dtype=torch.bfloat16):
            mixed = model(inputs)
    difference = (mixed.float() - reference).abs()
    return {
        "device": "cpu",
        "autocast_dtype": "torch.bfloat16",
        "parameter_dtype_after_autocast": str(next(model.parameters()).dtype),
        "input_dtype": str(inputs.dtype),
        "output_dtype": str(mixed.dtype),
        "finite_output": bool(torch.isfinite(mixed).all().item()),
        "max_abs_difference_from_fp32": float(difference.max().item()),
        "benchmark_performed": False,
    }


def _as_cpu_float(values: Any) -> torch.Tensor:
    tensor = torch.as_tensor(values, dtype=torch.float32, device="cpu")
    if tensor.numel() == 0:
        raise ValueError("values must not be empty")
    if not bool(torch.isfinite(tensor).all().item()):
        raise ValueError("values must all be finite")
    return tensor


def _chunks(flat: torch.Tensor, granularity: str, group_size: int | None) -> list[torch.Tensor]:
    if granularity == "tensor":
        if group_size is not None:
            raise ValueError("group_size is only valid for granularity='group'")
        return [flat]
    if granularity != "group":
        raise ValueError("granularity must be 'tensor' or 'group'")
    if not isinstance(group_size, int) or isinstance(group_size, bool) or group_size <= 0:
        raise ValueError("group granularity requires a positive integer group_size")
    return [flat[start : start + group_size] for start in range(0, flat.numel(), group_size)]


def calculate_qparams(
    calibration_values: Any,
    *,
    bits: int = 8,
    symmetric: bool = True,
    granularity: str = "tensor",
    group_size: int | None = None,
) -> dict[str, Any]:
    """Derive signed integer quantization parameters from calibration values.

    For a symmetric signed range the negative endpoint is restricted to -qmax
    (for int8: -127..127), making zero exactly representable. Group mode flattens
    the input and gives each consecutive group its own scale/zero point.
    """
    if not isinstance(bits, int) or isinstance(bits, bool) or not 2 <= bits <= 8:
        raise ValueError("bits must be an integer from 2 through 8")
    if not isinstance(symmetric, bool):
        raise ValueError("symmetric must be a bool")
    values = _as_cpu_float(calibration_values)
    flat = values.reshape(-1)
    qmax = 2 ** (bits - 1) - 1
    qmin = -qmax if symmetric else -(2 ** (bits - 1))
    pieces = _chunks(flat, granularity, group_size)
    scales: list[float] = []
    zero_points: list[int] = []

    for piece in pieces:
        low = float(piece.min().item())
        high = float(piece.max().item())
        if symmetric:
            scale = max(abs(low), abs(high)) / qmax
            zero_point = 0
        elif high == low:
            # A constant range needs a non-zero step. This choice preserves a
            # non-zero constant when possible and maps an all-zero group to 0.
            magnitude = abs(low)
            scale = magnitude / qmax if magnitude else 1.0
            zero_point = 0
        else:
            scale = (high - low) / (qmax - qmin)
            zero_point = int(torch.round(torch.tensor(qmin - low / scale)).item())
            zero_point = max(qmin, min(qmax, zero_point))
        if not math.isfinite(scale) or scale <= 0:
            scale = 1.0
        scales.append(float(scale))
        zero_points.append(int(zero_point))

    return {
        "bits": bits,
        "symmetric": symmetric,
        "granularity": granularity,
        "group_size": group_size,
        "qmin": qmin,
        "qmax": qmax,
        "scales": scales,
        "zero_points": zero_points,
        "calibration_numel": flat.numel(),
    }


def quantize_with_qparams(values: Any, qparams: dict[str, Any]) -> dict[str, Any]:
    """Round, clamp and dequantize with precomputed qparams; report saturation."""
    tensor = _as_cpu_float(values)
    flat = tensor.reshape(-1)
    granularity = qparams.get("granularity")
    group_size = qparams.get("group_size")
    pieces = _chunks(flat, granularity, group_size)
    scales = qparams.get("scales")
    zero_points = qparams.get("zero_points")
    if not isinstance(scales, list) or not isinstance(zero_points, list):
        raise ValueError("qparams must contain scale and zero_point lists")
    if len(pieces) != len(scales) or len(pieces) != len(zero_points):
        raise ValueError("qparams count does not match the tensor groups")
    if granularity == "group" and flat.numel() != qparams.get("calibration_numel"):
        raise ValueError("group qparams require the same flattened length as calibration")
    qmin = int(qparams["qmin"])
    qmax = int(qparams["qmax"])

    code_pieces: list[torch.Tensor] = []
    dequant_pieces: list[torch.Tensor] = []
    saturation_count = 0
    for piece, scale, zero_point in zip(pieces, scales, zero_points):
        scale = float(scale)
        zero_point = int(zero_point)
        if not math.isfinite(scale) or scale <= 0:
            raise ValueError("all scales must be positive and finite")
        rounded = torch.round(piece / scale + zero_point)
        saturation_count += int(((rounded < qmin) | (rounded > qmax)).sum().item())
        codes = rounded.clamp(qmin, qmax).to(torch.int8)
        reconstructed = (codes.to(torch.float32) - zero_point) * scale
        code_pieces.append(codes)
        dequant_pieces.append(reconstructed)

    codes_flat = torch.cat(code_pieces)
    dequant_flat = torch.cat(dequant_pieces)
    dequantized = dequant_flat.reshape(tensor.shape)
    error = (dequantized - tensor).abs()
    return {
        "codes": codes_flat.reshape(tensor.shape),
        "dequantized": dequantized,
        "scales": [float(x) for x in scales],
        "zero_points": [int(x) for x in zero_points],
        "qmin": qmin,
        "qmax": qmax,
        "saturation_count": saturation_count,
        "saturation_fraction": saturation_count / flat.numel(),
        "mae": float(error.mean().item()),
        "rmse": float(torch.sqrt(torch.mean((dequantized - tensor) ** 2)).item()),
        "max_abs_error": float(error.max().item()),
    }


def _result_for_json(result: dict[str, Any]) -> dict[str, Any]:
    return {
        key: (value.tolist() if isinstance(value, torch.Tensor) else value)
        for key, value in result.items()
    }


def quantization_demo() -> dict[str, Any]:
    """Compare per-tensor/group int8 and a calibration-distribution shift."""
    values = torch.tensor([0.04, -0.05, 0.03, 10.0, 0.10, 0.12, -0.08, 0.11])
    per_tensor_qparams = calculate_qparams(values, symmetric=True, granularity="tensor")
    per_group_qparams = calculate_qparams(
        values, symmetric=True, granularity="group", group_size=4
    )
    per_tensor = quantize_with_qparams(values, per_tensor_qparams)
    per_group = quantize_with_qparams(values, per_group_qparams)

    calibration = torch.tensor([-1.0, -0.5, 0.0, 0.5, 1.0])
    evaluation = torch.tensor([-1.5, -0.2, 1.4])
    calibrated_qparams = calculate_qparams(calibration, symmetric=True, granularity="tensor")
    shifted = quantize_with_qparams(evaluation, calibrated_qparams)
    return {
        "int8_per_tensor": {
            "source": values.tolist(),
            "qparams": per_tensor_qparams,
            "result": _result_for_json(per_tensor),
        },
        "int8_per_group": {
            "source": values.tolist(),
            "qparams": per_group_qparams,
            "result": _result_for_json(per_group),
        },
        "calibration_shift": {
            "calibration_values": calibration.tolist(),
            "evaluation_values": evaluation.tolist(),
            "qparams": calibrated_qparams,
            "result": _result_for_json(shifted),
        },
        "storage_note": (
            "The code tensor uses torch.int8 for clarity. This demonstration does not pack sub-8-bit codes or include scale metadata in a model-size estimate."
        ),
    }


def run_lab() -> dict[str, Any]:
    """Return the complete deterministic report used by the CLI and tests."""
    return {
        "runtime": {
            "torch_version": torch.__version__,
            "device": "cpu",
            "purpose": "numeric behavior demonstration; not a performance benchmark",
        },
        "formats": format_table(),
        "cast_probe": precision_probe(),
        "cpu_bf16_autocast": cpu_autocast_probe(),
        "quantization": quantization_demo(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="optional path for the JSON report")
    args = parser.parse_args()
    report = json.dumps(run_lab(), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
```
