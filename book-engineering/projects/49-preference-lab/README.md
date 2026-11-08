# پروژهٔ فصل ۴۹ — آزمایشگاه ترجیح، DPO، PPO و GRPO

این پروژهٔ آموزشیِ CPU-only چهار محاسبهٔ کوچک را می‌آزماید: loss مقایسه‌ای Bradley–Terry برای امتیازهای scalar، loss جفتی DPO با log-probabilityهای policy/reference، نسبت clipped در surrogate سادهٔ PPO، و نرمال‌سازی reward درون گروه برای GRPO. audit قرارداد JSONL و split گروهی را کنترل می‌کند. demo به‌صورت تصریح‌شده فقط یک policy دسته‌ای دوگزینه‌ای مصنوعی را با DPO به‌روزرسانی می‌کند.

## محیط و اجرا

از ریشهٔ مخزن، وابستگی PyTorch نسخهٔ 2.6.0+cpu مطابق `requirements.txt` را نصب کنید؛ فایل requirements سراسری کل کتاب را مرجع نسخه‌ها قرار می‌دهد. پروژه وزن، tokenizer یا dataset بیرونی دریافت نمی‌کند.

```bash
cd book-engineering/projects/49-preference-lab
python -m unittest discover -v
python preference_lab.py --mode audit --fixture sample_preferences.jsonl --output /tmp/ch49-audit
python preference_lab.py --mode toy-dpo --output /tmp/ch49-demo --steps 80 --seed 49
```

هر اجرا `run.json` را در مسیر `--output` می‌نویسد؛ مسیر بیرون مخزن است تا خروجی تصادفی/محلی با منبع پروژه مخلوط نشود. دادهٔ audit در `sample_preferences.jsonl`، گزارش دو run ثبت‌شده در `results.json` و آزمون‌ها در `test_preference_lab.py` هستند.

## نتایج ثبت‌شده

روی Python 3.13.16 و PyTorch 2.6.0+cpu، **۲۲/۲۲ آزمون** موفق شدند. audit fixture، ۱۲ ردیف از ۶ گروه را فقط اعتبارسنجی کرد: train برابر ۸/۴ گروه، validation برابر ۲/۱ و test برابر ۲/۱. SHA-256 همان فایل در `results.json` آمده است. audit، آموزش یا بارگیری مدل انجام نمی‌دهد.

دموی مصنوعی با seed=49 و ۸۰ گام، loss را از `0.6931471824645996` به `0.12939360737800598` رساند؛ احتمال یکی از دو انتخاب در policy دسته‌ای از `0.5` به `0.9999496936798096` رسید. این تغییر عمدی روی یک جفت synthetic است و سنجهٔ کیفیت زبان، مقایسهٔ انسانی یا عملکرد مدل نیست.

## محدوده و محدودیت‌ها

- تمام دوازده preference در fixture ساختگی‌اند و `label_source` آن‌ها `synthetic_fixture` است؛ هیچ برچسب انسان/AI جمع‌آوری نشده.
- policy دوگزینه‌ای یک مدل زبان یا trainer کامل نیست؛ پروژه مدل pretrained بارگیری نمی‌کند و RLHF/PPO/GRPO را روی مدل اجرا نمی‌کند.
- تابع PPO فقط clipped surrogate ساده را محاسبه می‌کند؛ reward/value estimation، rollout، optimizer loop و penaltyهای دیگر را پوشش نمی‌دهد.
- تابع GRPO فقط advantage نرمال‌شدهٔ گروهی را می‌سازد؛ objective/trainer کامل، multi-reward یا sampling سیستم را پیاده‌سازی نمی‌کند.
- split گروهی leakageهای ثبت‌شده در `group_id` را کم می‌کند، اما صحت/کفایت گروه‌بندی و نمایندگی آماری را اثبات نمی‌کند.
- نتایج هیچ ادعایی دربارهٔ کیفیت واقعی، فارسی، GPU/NCCL، benchmark سخت‌افزار، safety، مجوز/حقوق یا privacy ایجاد نمی‌کنند.
- این پروژه فقط فایل‌های Python/JSONL و Markdown دارد؛ PDF/EPUB ساخته یا آزموده نشده است.
