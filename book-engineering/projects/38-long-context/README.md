# پروژهٔ فصل ۳۸ — حافظهٔ توجه و بودجهٔ زمینهٔ بلند

این پروژهٔ آموزشی سه ایده را با PyTorch و ورودی‌های کوچک روی CPU قابل مشاهده می‌کند:

1. **GQA/MQA:** چند Query head برای هر KV head و محاسبهٔ توجه با گروه‌بندی روشن.
2. **KV Cache:** افزودن K/V هر گام و مقایسهٔ خروجی decode افزایشی با attention علّیِ یک‌جای کل دنباله.
3. **MoE از نوع Switch top-1:** router هر توکن را به یک expert می‌فرستد؛ زیان سادهٔ توازن بار نیز قابل آزمون است.

تابع mask محلی، الگوی «هر Query فقط پنجرهٔ اخیر را می‌بیند» را می‌سازد. این mask برای آموزش قرارداد و صحت است: تابع attention در این پروژه عمداً scoreهای متراکم را می‌سازد و سپس mask می‌زند؛ بنابراین **کاهش زمان اجرا یا حافظهٔ محاسباتی attention پراکنده را اندازه‌گیری یا فراهم نمی‌کند**. برای کار تولیدی باید از kernel و runtime بهینه‌شده و سازگار با سخت‌افزار استفاده و کیفیت/کارایی آن‌ها جداگانه سنجیده شود.

## پیش‌نیاز و اجرا

- Python 3.13.16
- PyTorch 2.6.0 با build CPU (`torch==2.6.0`)
- هیچ GPU، مدل ازپیش‌آموزش‌دیده، dataset یا شبکه‌ای لازم نیست.

از همین پوشه:

```bash
python -m unittest discover -v
python efficient_attention.py
```

آزمون‌ها shape و dtype، قرارداد ماسک، عدم دسترسی به آینده، هم‌ارزی GQA با مرجع تکرار KV، هم‌ارزی cache افزایشی با causal attention، برآورد حافظه و گرادیان/dispatch سادهٔ MoE را کنترل می‌کنند. اجراهای تصادفی، benchmark سرعت یا ارزیابی کیفیت زبانی نیستند.

## قراردادها و مرزها

- شکل Query: `[batch, Hq, Tq, head_dim]`; شکل Key/Value: `[batch, Hkv, Tk, head_dim]`.
- تعداد Query head باید بر تعداد KV head بخش‌پذیر باشد. در این پروژه، Query headهای هر گروه پشت‌سرهم قرار می‌گیرند.
- در mask این پروژه `True` یعنی **دسترسی مجاز**. این قرارداد را با APIهای دیگری که `True` را «مسدود» تعریف می‌کنند قاطی نکنید.
- `KVCache` از `torch.cat` استفاده می‌کند؛ هر append دادهٔ قبلی را کپی می‌کند. برای سامانهٔ serving، این پیاده‌سازی آموزشی جایگزین حافظهٔ preallocated/paged نیست.
- `estimate_kv_cache_bytes` فقط حافظهٔ K و V خودتوجهی را تخمین می‌زند: `2 × layers × batch × tokens × KV heads × head_dim × bytes/element`. وزن‌ها، bufferها، activationها، metadata، cross-attention و فضای allocator در آن نیست.
- `SwitchTop1MoE` یک expert را به هر توکن می‌فرستد، محدودیت capacity، overflow، distributed all-to-all یا هدف آموزش زبانی ندارد. تابع زیان، نسخهٔ سادهٔ top-1 از فرمول Switch است؛ برای top-k یا روش‌های نوین، loss همان روش را جداگانه پیاده‌سازی کنید.
- معیار RAM/VRAM، latency، throughput، کیفیت مدل، «سرعت GPU» یا مقایسهٔ تولیدی از این demo نتیجه نمی‌شود.

## محتوای پوشه

- `efficient_attention.py` — mask، GQA، cache، تخمین بایت و MoE آموزشی.
- `test_efficient_attention.py` — آزمون‌های واحد کتابخانهٔ استاندارد `unittest`.
- `README.md` — نصب، اجرا، قراردادها و محدودیت‌ها.
