# پاسخ‌نامهٔ تشریحی جلد سوم، فصل ۱۳ (فصل ۴۵)

پاسخ‌ها معیار استدلال‌اند، نه تنها گزینهٔ ممکن. وقتی سؤال به سخت‌افزار یا مدل واقعی می‌رسد، باید نسخه، device، شکل tensor، ورودی و metric را ثبت کرد؛ استنتاج کلی از یک cast CPU یا بردار اسباب‌بازی کافی نیست.

## ۱. چرا BF16 دامنهٔ گسترده‌تر از FP16 دارد؟

FP16 چیدمان `1/5/10` دارد: یک بیت علامت، پنج بیت نما و ده بیت fraction. BF16 چیدمان `1/8/7` دارد. بیت‌های بیشتر نما اجازهٔ توان‌های بزرگ‌تر/کوچک‌تر را می‌دهند؛ برای همین `torch.finfo(torch.bfloat16).max` در PyTorch 2.6.0+cpu حدود `3.3895×10^38` است، در حالی که بیشینهٔ متناهی FP16 برابر `65,504` است. در مقابل، epsilon نزدیک ۱ در BF16 برابر `2^-7 = 0.0078125` و در FP16 برابر `2^-10 ≈ 0.0009766` است؛ پس FP16 در آن ناحیه فاصلهٔ ریزتری دارد. BF16 range را با fraction کوتاه‌تر می‌خرد. هیچ‌یک از این دو عدد به‌تنهایی دقت task یا سرعت را تعیین نمی‌کند؛ overflow، rounding، accumulation و kernel باید آزموده شوند.

## ۲. زیرنورمال، صفر و overflow را چگونه گزارش کنیم؟

بردار پیش‌فرض برنامه `[1e-8, 0.1, 1.001, 1e5, -1e5]` است. در همین PyTorch/CPU، FP16 مقدار `1e-8` را در round-trip به صفر تبدیل می‌کند و `±1e5` را ±Inf می‌دهد. این نشان می‌دهد مقدار کوچک زیر دامنهٔ مؤثر این cast افتاده و مقدار بزرگ از سقف finite عبور کرده است. اگر ورودی را نزدیک حد نرمال ببریم، ممکن است نتیجه subnormal باشد؛ «کوچک‌تر از smallest normal» مساوی «حتماً صفر» نیست، چون subnormalها می‌توانند بخشی از فاصله تا صفر را پوشش دهند. اما برخی backendها آن‌ها را flush-to-zero می‌کنند.

برای یک بردار تازه، `precision_probe(values)` را فراخوانی و شمار `nonzero_to_zero_count`، `infinity_count` و `nan_count` را جداگانه بخوانید. مقدارهای برگشتی cast هم باید گزارش شوند. FP8 E4M3FN طبق default cast همین محیط برای ±100000 NaN نشان داد، در حالی که E5M2 Inf داد؛ این رفتار را برای همهٔ conversion modeها و دستگاه‌ها تعمیم ندهید. `max_abs_error_on_finite_values` فقط روی خروجی‌های متناهی محاسبه می‌شود، پس در کنار آن شمار nonfinite را هم بخوانید.

## ۳. چرا scale per-group در مثال خطای کمتری داد؟

بردار پروژه هشت مقدار دارد و یکی از آن‌ها outlier برابر `10` است. در per-tensor، scale از `amax=10` محاسبه می‌شود؛ بنابراین گام quantization تقریباً `10/127 ≈ 0.07874` است. مقادیر `0.10` و `0.12` همگی با همین گام بزرگ نمایش داده می‌شوند. RMSE گزارش‌شده برای این fixture حدود `0.027528` است.

در گروه‌بندی چهارتایی، گروه نخست هنوز outlier `10` را دارد؛ گروه دوم مقادیر نزدیک `±0.12` دارد و scale کوچک‌تری، حدود `0.0009449`، می‌گیرد. خطای گروه دوم کم می‌شود و RMSE کل به حدود `0.020084` می‌رسد. گروه اول اما از نظر scale از outlier رها نشده، پس خطای هر عنصر آن الزاماً بهتر نمی‌شود. تعداد scaleها از یک به دو می‌رسد و در مدل واقعی metadata، layout، kernel و احتمال نیاز به padding هم هزینه دارند. این یک نتیجهٔ fixture است؛ اگر outlierها در هر گروه پخش شوند یا شکل و group size تغییر کند، رتبه‌بندی می‌تواند عوض شود.

## ۴. Calibration shift و saturation

پروژه scale را از `[-1,-0.5,0,0.5,1]` می‌آموزد؛ برای symmetric int8 در نتیجه `scale=1/127` و `zero_point=0` می‌شود. در evaluation، `-1.5` و `1.4` بیرون بازه‌اند. پیش از clamp، کدهای متناظر از `qmin` یا `qmax` عبور می‌کنند؛ پس دو مقدار از سه مقدار اشباع می‌شوند و `saturation_fraction=2/3` گزارش می‌شود. بعد از dequantize، آن دو تقریباً به `-1` و `1` برمی‌گردند، نه به مقدار اصلی‌شان.

Calibration پویاتر می‌تواند scale را بر اساس ورودی تازه به‌روز کند، ولی هزینهٔ اجرا و تغییر دامنهٔ runtime را می‌آورد. Granularity per-token/per-row یا per-group ممکن است اثر outlierهای دور از هم را کم کند، اما اگر outlier در همان گروه باشد باز هم سقف را تعیین می‌کند. تصمیم را با calibration مجاز و نماینده، validation و metricهای task بگیرید؛ test را برای تنظیم scale مصرف نکنید.

## ۵. BF16 autocast روی CPU را چطور تفسیر کنیم؟

در پروژه `nn.Linear(8,4)` با وزن‌های FP32 ساخته می‌شود. مرجع خارج از autocast اجرا می‌شود؛ سپس forward در `torch.amp.autocast("cpu", dtype=torch.bfloat16)` قرار می‌گیرد. در محیط آزموده‌شده، خروجی BF16 و متناهی بود، پارامترهای مدل همچنان FP32 ماندند و max absolute difference از مرجع حدود `0.002292` شد. این نتیجه نشان می‌دهد context autocast می‌تواند dtype خروجی را تغییر دهد، بدون آن‌که لازم باشد model را دستی `bfloat16()` کنیم.

این اختلاف یک معیار پذیرش عمومی نیست. داده ۸×۸ و یک Linear کوچک است، نه مدل زبانی، نه benchmark و نه ارزیابی latency. برای model واقعی باید همان ورودی‌ها، checkpoint، معیار task، backend و version را مقایسه کرد؛ اندازه‌گیری زمان CPU نیز به warmup و تکرار نیاز دارد. `finite_output=True` مفید است، ولی به‌تنهایی اثبات حفظ کیفیت نیست.

## ۶. انتخاب E4M3 یا E5M2

اگر tensor دامنهٔ نسبتاً کنترل‌شده‌ای دارد و تفکیک‌پذیری آن برای metric مهم است، E4M3 به علت سه بیت fraction (در برابر دو بیت E5M2) می‌تواند انتخاب کاندید باشد؛ بیشینهٔ finite آن ±448 است. اگر gradient یا مقدارهای میانی دامنهٔ وسیع‌تری دارند، E5M2 تا ±57,344 finite را نمایش می‌دهد و Inf/NaN را هم طبق قالب دارد، اما fraction کوتاه‌تر می‌شود. در هر دو حالت scale می‌تواند دامنهٔ tensor را به محدودهٔ format نگاشت کند؛ پس نقش weight، activation و gradient، outlierها، current/delayed history و پشتیبانی kernel مهم‌اند. نمی‌توان گفت «همیشه وزن E4M3 و gradient E5M2» یا «FP8 همیشه دقیق‌تر/سریع‌تر»؛ recipe مقالهٔ FP8 و TorchAO فقط در setup و version گزارش‌شده شاهدند.

## ۷. طرح QAT قابل ارزیابی

یک طرح قابل‌دفاع ابتدا وزن‌ها و activationهای لایه‌های هدف و granularity را مشخص می‌کند. دادهٔ train یا کالیبراسیونِ مجاز و نماینده برای انتخاب range استفاده می‌شود، نه test نهایی. در `prepare` fake-quantization حدود scale/zero-point را در forward شبیه‌سازی می‌کند؛ training/fine-tune با validation monitoring انجام می‌شود. در مرحلهٔ convert، artifact کم‌بیت به kernel هدف تبدیل می‌شود؛ سپس هم کیفیت task و هم latency/memory روی همان device سنجیده می‌شود.

run card باید framework/TorchAO version (stable یا unstable)، hardware/driver، format، granularity، calibration data identity، clipping/saturation، seed، معیار پذیرش و checkpoint state را ثبت کند. Fake quant یک محاسبهٔ نرم‌افزاری float است و لزوماً به معنی اجرای integer GEMM همان‌جا نیست. اگر کیفیت یا سرعت شرط pass/fail را نگرفت، recipe را رد یا دوباره مطالعه می‌کنیم؛ QAT تضمین‌کنندهٔ حفظ metric نیست.

## ۸. چه چیزی به checkpoint افزوده می‌شود؟

برای run FP16، علاوه بر model/optimizer و update/data state که فصل ۴۴ توضیح داد، باید `GradScaler` و مقیاس فعلی/تاریخچهٔ رشد و backoff را ذخیره کنیم؛ وگرنه run ادامه‌یافته ممکن است در updateهای بعدی با رفتار scale دیگری روبه‌رو شود. برای FP8 باید format policy، scaling recipe و current/delayed `amax` history/scaleهایی را که در آموزش استفاده شده‌اند نیز نگه داشت. اگر optimizer state جداگانه نگهداری می‌شود، آن هم لازم است.

برای inference quantized، artifact باید وزن‌های quantized، scale و zero-point، granularity/shape، model config و محدودیت نسخه/kernel/device را همراه داشته باشد. وزن تنها معمولاً برای بازسازی دقیق همان محاسبه کافی نیست. Checkpoint آموزش قابل resume و بستهٔ inference قابل deployment ممکن است متفاوت باشند؛ هر دو را با شناسهٔ مدل و منشأ داده به هم مرتبط می‌کنیم، اما هدف ذخیره‌سازی‌شان یکی نیست.

## معیار تصحیح

پاسخ خوب دست‌کم شش تمرین را با فرض، واحد و شواهد توضیح می‌دهد؛ بین range و precision، overflow و underflow، AMP و quantization، و مشاهدهٔ CPU و پشتیبانی accelerator تمایز می‌گذارد؛ و هیچ عدد toy را نتیجهٔ benchmark یا کیفیت مدل واقعی جا نمی‌زند. تعداد آزمون‌های پروژه ۱۰ است. اجرای موفق تست فقط درستی قراردادهای همین آزمایشگاه را می‌سنجد.
