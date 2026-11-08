# پروژهٔ فصل ۵۰ — ممیزی دادهٔ مصنوعی و ابزارهای استدلال

این پروژه چند قطعهٔ کوچک آموزشی برای بررسی traceهای حسابی ساختگی، تقسیم گروهی داده، مرتب‌سازی curriculum نمایشی، محاسبهٔ KL روی tensorهای ساختگی و رأی‌گیری میان پاسخ‌های ثابت فراهم می‌کند. هدف، تمرین قرارداد داده و مرز ادعاست؛ این پروژه یک مدل زبانی یا pipeline آموزش reasoning نیست.

## اجرا

از ریشهٔ مخزن:

```bash
(cd book-engineering/projects/50-synthetic-reasoning && python -m unittest discover -v)
python book-engineering/projects/50-synthetic-reasoning/reasoning_lab.py \
  --mode audit \
  --fixture book-engineering/projects/50-synthetic-reasoning/sample_traces.jsonl \
  --output /tmp/ch50-audit
python book-engineering/projects/50-synthetic-reasoning/reasoning_lab.py \
  --mode demo \
  --fixture book-engineering/projects/50-synthetic-reasoning/sample_traces.jsonl \
  --output /tmp/ch50-demo
```

به Python 3.13 و PyTorch CPU نیاز است؛ وابستگی‌های مخزن در `requirements.txt` ثبت شده‌اند. دستورات audit و demo وزن یا مدل دانلود نمی‌کنند و آموزش انجام نمی‌دهند.

## قرارداد fixture و نتیجهٔ ثبت‌شده

`sample_traces.jsonl` شامل ۱۲ رکورد و ۶ گروه است؛ همهٔ برچسب‌ها `synthetic_fixture` هستند. split گروهی با seed برابر ۵۰، ۸ رکورد/۴ گروه را به train، دو رکورد/یک گروه را به validation و دو رکورد/یک گروه را به test می‌فرستد. SHA-256 فایل fixture:

```text
1654621020c9dd2175cf0d7f66cb14ed78a3d192667c7e79ce7571219f47a075
```

در اجرای ثبت‌شده، ۲۶ آزمون از ۲۶ موفق بود. demo روی logits ساختگی با دمای ۲ مقدار KL برابر `0.2875792384147644` و گرادیان finite گزارش کرد. رأی‌گیری روی پنج رشتهٔ ثابت `125, 124, 125, 125, 126` مقدار `125` را با سه رأی برگزید. این‌ها فقط آزمون helperها و fixture هستند؛ نمونه‌گیری از مدل، یادگیری، pass@k یا دقت روی مسئلهٔ واقعی نیستند.

جزئیات محیط، split، خروجی‌ها و مرز محدودیت‌ها در `results.json` و `../../chapters/50-audit-report-fa.md` ثبت شده‌اند.

## محدودیت ادعا

از خروجی این fixture نمی‌توان کیفیت یا توانایی مدل واقعی/فارسی، مزیت تقطیر یا curriculum، عملکرد روی benchmark، زمان پاسخ محصول، نیاز سخت‌افزاری یا اثر آموزش صنعتی را نتیجه گرفت. هیچ دادهٔ انسانی یا کاربرمحور، GPU، ارزیابی حریم خصوصی، مجوز داده یا تضمین حقوقی آزموده نشده است. تقسیم گروهی فقط در همین fixture بررسی شده؛ به معنای ناشناس‌سازی یا رفع نشت در دادهٔ واقعی نیست.
