# پاسخ‌نامهٔ تشریحی جلد سوم، فصل ۱۲ — پیش‌آموزش

پاسخ‌های زیر نمونهٔ استدلال‌اند؛ در تحلیل run واقعی، hash داده، تعداد target معتبر، نسخهٔ framework و فرض‌های schedule باید با همان اجرا سازگار باشند.

## ۱. شمار target و exposure

با `B=8` نمونه در هر microbatch، `G=2` microbatch در هر update و `T=64` target معتبر در هر نمونه، حداکثر targetهای update برابر است با `8×2×64=1,024`. برای `U=100` update، سقف exposure برابر `102,400` target است. اگر batch انتهایی ناقص باشد، مقدار واقعی کمتر می‌شود؛ اگر یک token چندبار در چند epoch دیده شود، exposure همچنان چندبار شمرده می‌شود. «دیده‌شده» نه تعداد token یکتا است، نه تضمین یادگیری و نه یکسان با تعداد کل tokenهای فایل.

## ۲. میانگین loss با microbatchهای ناقص

برای targetهای ۴، ۴ و ۲تایی و میانگین‌های هر microbatch به‌ترتیب `L₁`, `L₂`, `L₃`، loss درست این است:

`(4L₁ + 4L₂ + 2L₃) / 10`.

میانگین سادهٔ `(L₁+L₂+L₃)/3` به microbatch ۲تایی همان وزن microbatch ۴تایی را می‌دهد؛ در نتیجه هر target وزن یکسان ندارد. همین منطق هنگام backprop باید اعمال شود: مجموع loss هر پنجره را به تعداد کل targetها تقسیم و سپس گرادیان را accumulate کنید؛ clipping را بعد از پنجره انجام دهید.

## ۳. مقادیر warmup-cosine

`η_peak=0.1`, `ρ=0.1`, `U=10`, `W=2`; پس `η_min=0.01`.

- update ۱: `0.1×1/2 = 0.05`.
- update ۲: پایان warmup، `0.1`.
- update ۶: progress برابر `(6−2)/(10−2)=0.5`; `cos(π/2)=0`, پس `0.01 + 0.5×(0.1−0.01)=0.055`.
- update ۱۰: انتهای decay، `0.01`.

این تابع نمونه updateمحور است؛ اگر step را به‌اشتباه برای هر microbatch زیاد کنیم، منحنی چهار برابر تندتر می‌شود وقتی `G=4`.

## ۴. مقدار schedule اصلی Transformer

در نقطهٔ `t=W=4000` دو عبارت داخل `min` برابر `1/√4000`اند. پس:

`η = 512⁻¹/² × 4000⁻¹/² = 1/√2,048,000 ≈ 0.00069877`.

این نقطهٔ peak فرمول Noam در همان `d_model` و warmup است. cosine در پروژهٔ فصل تابع دیگری است: بعد از warmup، افت با cosine و انتهای run تعریف می‌شود؛ مقادیر دو فرمول را نباید بدون ذکر schedule، واحد و مقیاس مقایسه کرد.

## ۵. state لازم برای resume

برای مثال AdamW: وزن مدل، state momentهای AdamW، optimizer groups و LR، global update/schedule/config، ترتیب و cursor sampler، seed/RNG CPU و hashهای فایل‌های داده. با AMP باید GradScaler هم حفظ شود؛ در data parallel باید وضعیت هر replica/rank و sampler هماهنگ باشد. پروژهٔ فصل روی CPU، یک process و FP32 است، بنابراین GradScaler و rankهای توزیع‌شده ندارد. اگر only weights را بارگذاری و optimizer را تازه بسازیم، آن کار warm-start است، نه resume دقیق.

## ۶. آزمون قطع و ادامه

دادهٔ فصل ۴۰ و config ثابت را نگه دارید؛ run کامل را در مسیر جداگانه اجرا کنید. اجرای دوم را با `--stop-after 6` متوقف کنید؛ `metrics.json` باید `status=partial`, `test_once_after_training=0` و `test_metrics=null` داشته باشد. سپس از `checkpoint-latest.pt` ادامه دهید. در محیط و نسخهٔ یکسان، history و metrics دو run باید دقیقاً برابر شوند؛ checkpoint نهایی نیز باید وزن‌ها و optimizer state سازگار داشته باشد. برابری میان CPU و GPU یا releaseهای مختلف را این آزمون اثبات نمی‌کند.

## ۷. چرا checkpoint تغییر config را رد می‌کند؟

اگر peak LR تغییر کند، schedule و trajectory تغییر می‌کنند؛ اگر data hash عوض شود، sampler روی نمونه‌های دیگری می‌چرخد. ادامه با این تغییرات «همان run» نیست. برای مقایسهٔ آگاهانه، run تازه و fingerprint تازه بسازید. اگر فقط وزن‌های قبلی را شروع کار قرار دهید و optimizer/sampler/schedule را از نو تعریف کنید، آن را warm-start یا continued pretraining با changelog صریح بنویسید.

## ۸. انتخاب فاصلهٔ ذخیره

فرض مثال: checkpoint یک دقیقه زمان می‌برد و job هر ۳۰ دقیقه می‌نویسد؛ نسبت زمان ذخیره حدود ۱/۳۰ یا ۳٫۳٪ و در بدترین حالت نزدیک ۲۹ دقیقه compute از آخرین save از دست می‌رود. اگر هر ۵ دقیقه save شود و هر بار ۱۰ ثانیه طول بکشد، نسبت تقریبی overhead هم ۱۰/۳۰۰ یعنی ۳٫۳٪ است، اما زمان از دست‌رفتهٔ بیشینه نزدیک ۵ دقیقه می‌شود. این فقط محاسبهٔ نمونه است؛ باید اندازهٔ فایل، throughput storage، احتمال interruption، هزینهٔ restart و سقف اتلاف قابل‌قبول خودتان را اندازه بگیرید. «هر ۱۰۰۰ update» نسخهٔ واحد برای همهٔ مدل‌ها نیست.

## معیار پذیرش

تنظیمات و data hashes ثابت‌اند؛ LR برحسب optimizer update ثبت شده؛ valid targetها در gradient accumulation درست وزن گرفته‌اند؛ test در run partial خوانده/ارزیابی نشده؛ checkpoint کامل model+optimizer+progress+sampler/RNG را حفظ کرده؛ و resume از همان نقطه در آزمون ثابت تکرار شده است. خروجی کوچک این fixture هیچ نتیجه‌ای دربارهٔ کیفیت، scaling یا schedule مناسب مدل واقعی نمی‌دهد.
