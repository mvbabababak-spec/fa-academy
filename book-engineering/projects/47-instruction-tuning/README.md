# پروژهٔ فصل ۴۷: قرارداد داده و یک آزمایش کوچک SFT

این پروژه ادامهٔ پروژه‌های جلد سوم را تکرار نمی‌کند. فصل ۴۳ provenance، وضعیت‌های حقوقیِ ثبت‌شده، پرچم‌های کیفیت و نامزدهای تکرار را ممیزی می‌کند؛ فصل ۴۴ حلقهٔ پیش‌آموزش، schedule و checkpoint را می‌سازد. اینجا هدف پس‌آموزش است: رکورد `prompt`/`completion`، جداسازی group-aware، ماسک‌کردن prompt در loss علّی و یک مسیر اختیاریِ full-parameter SFT. PEFT و LoRA به فصل ۴۸ واگذار می‌شوند؛ preference optimization و RL به فصل ۴۹.

## اجرای آفلاین و آزمون‌های قراردادی

Python 3.13.x پشتیبانی‌شدهٔ مخزن است؛ توابع داده و تمام آزمون‌های unit با کتابخانهٔ استاندارد Python اجرا می‌شوند. حالت پیش‌فرض مدل یا tokenizer را بار نمی‌کند و شبکه نمی‌خواهد:

```bash
python -m unittest discover -v
python sft_experiment.py --mode audit --data sample_sft.jsonl --output /tmp/ch47-audit
```

`run.json` در حالت audit فقط hash و شمار رکوردها/گروه‌ها در splitها را می‌نویسد؛ متن خام را کپی نمی‌کند، loss نمی‌سنجد و ادعای مجوز، کیفیت یا آمادگی آموزشی ندارد. fixture دارای ۱۵ رکورد و ۱۴ گروه خودنوشته و عمومی است؛ دو ردیف خانوادهٔ مشابه در یک group قرار می‌گیرند تا آزمون split گروهی قابل مشاهده باشد. test این fixture محرمانه یا benchmark نیست.

## آزمایش اختیاری مدل

نسخهٔ پایهٔ مخزن PyTorch 2.6.0 CPU را pin می‌کند. برای مرحلهٔ اختیاری مدل، در صورت پذیرش دانلود وزن‌ها، وابستگی‌های جدا و pin‌شده را نصب کنید:

```bash
python -m pip install -r ../../../requirements.txt -r requirements-model-demo.txt
python sft_experiment.py --mode train --data sample_sft.jsonl \
  --output /tmp/ch47-pythia-run --allow-download --epochs 1 --batch-size 2
```

بدون `--allow-download`، بارگیری فقط از cache محلی انجام می‌شود. مدل `EleutherAI/pythia-14m` در revision ثابت `cf967c0a9a04383db6f7b1108d86b2962634b4ac` استفاده می‌شود؛ مدل‌کارت در ۶ نوامبر ۲۰۲۶ زبان را English، کاربرد را پژوهشی و نه deployment معرفی می‌کرد و metadata مجوز را Apache-2.0 نشان می‌داد. metadata مدل، مجوز دادهٔ pretraining، حقوق رکوردهای دیگر یا جواز یک کاربرد خاص را تعیین نمی‌کند؛ کد هیچ‌یک را بررسی حقوقی نمی‌کند. وزن‌ها به مخزن افزوده نمی‌شوند.

پروژه full fine-tuning کوچک را روی CPU و متن‌های مصنوعی انگلیسی اجرا می‌کند. NLL اعتبارسنجی پیش و پس از آموزش گزارش می‌شود؛ test عمومی فقط یک‌بار پس از آموزش ارزیابی می‌شود. خروجی وزن، tokenizer و `run.json` در مسیر `/tmp` می‌مانند. دستور برای نمایش سازوکار است، نه توصیهٔ ابرپارامتر، ادعای پیروی از دستور، کیفیت فارسی، کیفیت محصول، benchmark، privacy guarantee، سرعت یا اجرای GPU/NCCL. اگر مقدار اعتبارسنجی تغییر کند، فقط نتیجهٔ همین fixture/run است؛ از آن کیفیت مدل واقعی را نتیجه نگیرید.

## قرارداد ورودی و کد

هر خط JSONL دست‌کم `id`, `source_id`, `group_id`, `prompt`, `completion` دارد. `group_id` باید وابستگی رکوردهای مرتبط را نگه دارد؛ split بر پایهٔ گروه و seed پایدار ساخته می‌شود. برنامه fuzzy dedup، provenance audit، فیلتر حقوق/PII، ساخت chat template یا تشخیص آلودگی انجام نمی‌دهد؛ در دادهٔ واقعی این گام‌ها و شواهد را جدا طراحی کنید.

توکن‌های prompt و completion جدا tokenization می‌شوند؛ `labels` متناظر با prompt و padding برابر `-100` است. completion و EOS هدف آموزش‌اند؛ اگر target از `max_length` بلندتر باشد، نمونه رد می‌شود و بریده نمی‌شود. اگر ورودی واقعاً chat-based است، قالب گفتگو و assistant mask همان tokenizer/model را باید با batch واقعی بررسی کرد؛ این fixture عمداً قالب چت اختصاصی جعل نمی‌کند.

## وابستگی‌های optional pin‌شده

`requirements-model-demo.txt` نسخه‌های Transformers 4.57.6، Hugging Face Hub 0.36.0، Tokenizers 0.22.1 و Safetensors 0.7.0 را برای آزمایش مدل مشخص می‌کند. PyTorch از manifest اصلی مخزن نصب می‌شود. CI فصل، آزمون‌های unit و audit آفلاین را اجرا می‌کند؛ CI وزن مدل را دانلود یا fine-tune نمی‌کند.
