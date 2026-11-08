# پروژهٔ فصل ۶۱: تحلیل trace استنتاج و بودجهٔ KV cache

این پروژه یک trace نرمال‌شده را تحلیل می‌کند و payload نظری KV cache را با فرض‌های آشکار حساب می‌کند. کد فقط از کتابخانهٔ استاندارد Python استفاده می‌کند؛ مدل، tokenizer، runtime، GPU یا شبکه را بار نمی‌کند و زمان‌سنجی واقعی انجام نمی‌دهد.

## محیط و اجرا

- CPython 3.13؛ وابستگی خارجی ندارد.
- ورودی ثابت `sample_trace.json` صرفاً ساختگی است و دو پیکربندی خیالی را نشان می‌دهد.
- همهٔ زمان‌ها، شمار توکن‌ها و خطای نمونه قراردادی‌اند؛ خروجی، نتیجهٔ benchmark نیست.

از پوشهٔ پروژه:

```bash
python -m unittest -v
python inference_lab.py --fixture sample_trace.json --output /tmp/ch61-analysis.json
```

یا برای چاپ JSON در ترمینال:

```bash
python inference_lab.py --fixture sample_trace.json --output -
```

## قرارداد trace

هر درخواست زمان‌های `arrival_ms`, `first_output_ms` و `finish_ms` را نسبت به آغاز پنجره دارد؛ `prompt_tokens` و `completion_tokens` باید از runtime/trace معتبر بیایند. `status` یکی از `ok`, `error`, `timeout` است. برای درخواست موفق، زمان اولین خروجی و شمار مثبت توکن خروجی الزامی‌اند. زمان‌های percentile فقط درخواست‌های موفق را می‌گیرند؛ نرخ خطا درخواست‌های ناموفق را در مخرج نگه می‌دارد.

برای سنجش واقعی، ابتدا مستندات و ابزار benchmark همان runtime را به‌کار ببرید، workload و warm-up را ثابت کنید، خروجی‌های معتبر را به schema تبدیل کنید و نام/نسخهٔ مدل، hash یا revision artifact، tokenizer/template، runtime، driver، GPU، precision، تنظیمات صف و پنجرهٔ اندازه‌گیری را کنار trace ثبت کنید. این analyzer قراردادهای خام ابزارهای مختلف را خودکار تبدیل نمی‌کند و اگر runtime شمار توکن یا timestamp را ندهد، نباید آن را از تعداد chunkهای شبکه حدس زد.

در این پروژه درخواست‌ها از یک پنجرهٔ مصنوعی می‌آیند؛ بنابراین open-loop load generation، warm-up، نرخ ورودی کنترل‌شده، confidence interval، ارزیابی کیفیت، پایداری چندساعته، مصرف peak حافظهٔ دستگاه و صحت runtime آزموده نمی‌شوند. Percentile نزدیک‌ترین رتبه برای شرح همین fixture است، نه برآورد آماری قابل‌اتکا از جمعیت.

## برآورد KV cache

فرض dense full-attention در `inference_lab.py` چنین است:

```text
bytes = 2 × layers × KV_heads × head_dim × bytes_per_element × tokens × sequences
```

این حساب فقط payload سادهٔ K و V را پوشش می‌دهد. padding/block metadata، fragmentation، workspaces، وزن مدل، activationها و مزیت احتمالی sliding-window یا معماری‌های غیرمعمول را شامل نمی‌شود؛ از آن ظرفیت قطعی GPU نتیجه نگیرید. برای برآورد کلی وزن‌ها، FLOPs و حافظه به فصل ۵۴ مراجعه کنید.

## محدودیت ادعا

`results.json` hash fixture و خلاصهٔ محاسبهٔ قطعی را نگه می‌دارد. هیچ model serving، vLLM، llama.cpp، Ollama، ONNX Runtime GenAI، TensorRT-LLM، kernel، GPU، quantization یا performance benchmark در این پروژه اجرا نشده است. نام‌های `illustrative-static` و `illustrative-candidate` فقط برچسب دو trace ساختگی‌اند و برتری batching یا runtime را اثبات نمی‌کنند.
