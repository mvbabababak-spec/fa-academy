# پاسخ‌نامهٔ فصل ۴۶ — مقیاس و بازیابی run

## ۱. وزن‌دهی shardهای نابرابر

اگر rank صفر ۳ نمونه و rank یک ۲ نمونه داشته باشد، میانگین نمونه‌ای کل برابر است با `(3×mean₀ + 2×mean₁)/5`، نه `0.5×(mean₀+mean₁)`. DDP گرادیان rankها را میانگین می‌گیرد؛ اگر `Sᵣ` مجموع loss محلی و `W=2` باشد، هر rank مقدار `Lᵣ=(W/N)Sᵣ` را backpropagate می‌کند. بنابراین میانگین گرادیان rankها به `1/N` ضربدر مجموع گرادیان همهٔ lossها تبدیل می‌شود.

## ۲. Batch و token

`B_global ≈ 4×3×2 = 24` نمونهٔ مؤثر در یک update، با فرض batch کامل و وزن برابر برای هر نمونه. برای valid token باید طول/ماسک هدف هر نمونه و padding را شمرد؛ اگر نمونه‌ها طول متفاوت دارند، `24` را در یک طول میانگین حدسی ضرب نکنید، مجموع targetهای معتبر واقعی را ثبت کنید.

## ۳. دو checkpoint

Activation checkpointing مرز segmentهای forward را نگه می‌دارد و در backward، بخشی از محاسبه را دوباره انجام می‌دهد؛ هدفش کم‌کردن activationهای ذخیره‌شده به بهای compute است. Training-state snapshot برای resume وزن، optimizer، گام/scheduler، sampler/data position و RNGهای لازم را در یک نقطهٔ سازگار نگه می‌دارد. یکی به‌تنهایی جای دیگری نیست.

## ۴. راه‌حل برحسب نوع OOM

- OOM activation یا attention: کوچک‌کردن sequence/microbatch یا سنجش activation recomputation و مسیر attention مناسب؛ زمان و metric نیز باید دوباره اندازه‌گیری شوند.
- OOM وزن/گرادیان/optimizer state: ارزیابی ZeRO/FSDP یا راهبرد مدل‌موازی و هزینهٔ ارتباط.
- گلوگاه data loading: profile کردن reader، decode، storage و data wait، سپس تنظیم pipeline؛ افزودن GPU به تنهایی داده را سریع‌تر نمی‌رساند.

این‌ها پیشنهاد شروع‌اند، نه تضمین اینکه علت تنها همین باشد.

## ۵. Snapshot توزیع‌شده

در گام ۲۰۰ باید snapshot پس از optimizer update و collectiveهای مربوطه، شامل مدل و optimizer state، گام/scheduler، state sampler و offset، RNG هر rank، config/precision، world size و metadata لازم باشد. همهٔ shardهای مورد انتظار باید کامل باشند و manifest نقطهٔ snapshot را شناسایی کند. اگر world size از ۴ به ۸ عوض شد، sampler و تقسیم داده، global batch، rank assignment، optimizer state/shard layout و semantics resume را بررسی کنید؛ DCP می‌تواند برخی stateهای شاردشده را reshard کند، اما هر state یا ناسازگاری نسخه را خودکار حل نمی‌کند.

## ۶. تقریب سربار checkpoint

`C=90 s=1.5 min`, `I=30 min`, `λ=0.02/hour`. سهم زمان نوشتن: `C/I=1.5/30=0.05=5%`. نیمهٔ فاصله `I/2=15 min=0.25 h` است؛ اتلاف مورد انتظار: `λI/2=0.02×0.25=0.005=0.5%`. جمع تقریبی `5.5%` می‌شود. این تقریب زمان restart، شکست‌های هم‌بسته، نوسان هزینهٔ write، رقابت storage و خطای چند منبع را نادیده می‌گیرد.

## ۷. Run record و حریم خصوصی

ثبت کنید: code commit/hash و وضعیت تغییرات، hash داده و split، tokenizer/config، seed، Python/PyTorch/driver، device/topology، world size و strategy، precision، global step و valid tokens، نام/واحد/split معیارها، زمان‌بندی و checkpoint/artifact references. متن خام prompt، اطلاعات شخصی، token دسترسی و secret را ثبت نکنید. اگر تشخیص موردی نیازمند دادهٔ حساس است، سیاست مجوز، حداقل‌سازی و کنترل دسترسی لازم است؛ hash نیز به‌تنهایی محرمانگی را تضمین نمی‌کند.

## ۸. تفسیر پروژه

در محیط ثبت‌شده، hookهای autograd برای fixture کوچک `4,016` بایت saved-tensor در حالت معمول و `688` بایت با recomputation دیدند؛ خروجی و gradientها برابر شدند. DDP واقعی دوپردازه‌ای CPU/Gloo با shardهای ۳ و ۲ نمونه، گرادیان `−33` را با backward تک‌پردازشی تطبیق داد. این نتیجه correctness همین fixture است؛ peak حافظه، سرعت، latency، کیفیت مدل، NCCL/GPU، شبکهٔ چندگره‌ای یا تحمل خرابی واقعی را نمی‌سنجد.
