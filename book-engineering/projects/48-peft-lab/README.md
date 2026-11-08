# پروژهٔ فصل ۴۸ — آزمایشگاه PEFT و LoRA

## هدف و مرز ادعا

این پروژه با PyTorch و CPU، قراردادهای ریاضیِ Adapter و LoRA را روی لایه‌های خطی کوچک می‌آزماید: انجماد وزن پایه، شمار پارامترهای LoRA، برابری merge در حالت eval و اجرای یک نگاشت خطی مصنوعی. حالت audit یک fixture صرفاً شکلِ لایه‌ها را اعتبارسنجی می‌کند و کران پایینِ payload وزن فشرده را حساب می‌کند. هیچ مدل pretrained بارگیری یا quantize نمی‌شود؛ QLoRA واقعی، GPU، memory peak، سرعت، کیفیت زبانی/فارسی، benchmark، privacy یا deployment آزموده نمی‌شوند.

اعداد audit فقط از ابعاد ساختگی می‌آیند. `packed_weight_payload_lower_bound_bytes` اندازهٔ نظری دادهٔ وزن packed است؛ نه VRAM موردنیاز و نه اندازهٔ checkpoint واقعی. برای یک مدل واقعی باید metadata و scaleهای quantization، لایه‌های خارج از quantization، activations، gradients، optimizer state، طول توالی، batch، workspace و backend را جداگانه اندازه گرفت.

## اجرا

از پوشهٔ پروژه و محیط اصلی مخزن که PyTorch 2.6.0+cpu دارد:

```bash
python -m unittest discover -v
python peft_lab.py --mode audit --fixture sample_layers.json --output /tmp/ch48-peft-audit
python peft_lab.py --mode toy-lora --output /tmp/ch48-peft-toy
```

هیچ شبکه، وزن، دادهٔ کاربر یا فایل محرمانه‌ای لازم نیست. هر دو CLI، نتیجهٔ JSON را در `run.json` می‌نویسند. fixture مصنوعی است و شناسه‌های آن معماری مدل واقعی را بازنمایی نمی‌کنند.

## فایل‌ها

- `peft_lab.py`: `LoRALinear`، adapter bottleneck، حسابگر پارامترها و کران پایین payload چهار بیتی؛ CLI آفلاین.
- `test_peft_lab.py`: آزمون واحد برای انجماد پایه، initialization صفرِ update، gradient، merge، adapter residual، حسابگر و قرارداد fixture.
- `sample_layers.json`: سه ردیف ساختگیِ شکل لایه.

کد این پوشه برای آموزش رابطه‌های جبری است؛ پیاده‌سازی کامل PEFT، bitsandbytes، QLoRA یا loop صنعتی نیست. راهنمای API کتابخانه‌ها در متن فصل فقط illustrative است و در این پروژه اجرا نشده؛ به نسخه و معماری مدل وابسته است.
