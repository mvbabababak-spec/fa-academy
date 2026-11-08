# پروژهٔ فصل ۵۶ — مدل شفاف TCO برای بودجهٔ محاسبات

این پروژه فقط یک fixture مصنوعی را حساب می‌کند: خرید، اجاره و یک snapshot محاسبهٔ ابری. هیچ قیمت خرید یا اجاره‌ای نقل‌قول فروشنده نیست؛ کد به شبکه وصل نمی‌شود، سخت‌افزار را اندازه‌گیری نمی‌کند و برابری عملکرد سه گزینه را ادعا نمی‌کند.

## اجرا

از پوشهٔ پروژه:

```bash
python -m unittest -v
python budget_model.py --fixture sample_budget.json --output results.json
```

یا از ریشهٔ مخزن:

```bash
python -m unittest discover -s book-engineering/projects/56-ai-compute-budget -v
python book-engineering/projects/56-ai-compute-budget/budget_model.py \
  --fixture book-engineering/projects/56-ai-compute-budget/sample_budget.json \
  --output book-engineering/projects/56-ai-compute-budget/results.json
```

۱۳ آزمون unit، arithmetic انرژی/ابر/NPV، رد ورودی نامعتبر، برچسب synthetic، مرز بازار، نرخ تاریخ‌دار و محدودیت ادعای عملکرد را بررسی می‌کنند. `results.json` کنار fixture، ورودی‌های خام، دورهٔ سه‌ساله، نرخ تنزیل، جریان‌های سال صفر تا افق، TCO اسمی، NPV، نرخ هزینهٔ هر «تحویل مصنوعی» و محدودیت‌ها را نگه می‌دارد. مقدار SHA-256 ورودی هم برای امکان بازبینی ثبت می‌شود. محاسبات مالی با `Decimal` انجام می‌شوند؛ جریان هر سال برای نمایش به سنت آمریکا گرد می‌شود. شیوهٔ گردکردن فاکتور واقعی ممکن است متفاوت باشد.

## مرز بازار و داده

- قیمت ابری **`$4.49993/instance-hour`** برای `g4-standard-48`، در **Iowa, US (`us-central1`)**، snapshot رسمیِ واکشی‌شده در **2026-11-06** است. مشخصات ثبت‌شده در fixture: 48 vCPU، 180 GB حافظهٔ میزبان و یک RTX PRO 6000 با 96 GB GDDR7. دیسک، شبکه/خروج داده، مالیات و سرویس‌های دیگر در این عدد نیستند. این نرخ Dallas نیست.
- **`8.96¢/kWh`** میانگین تجاری statewide تگزاس برای **August 2026** در جدول EIA است که **2026-10-23** منتشر شد؛ مقدار مقدماتی/میانگین است، نه تعرفهٔ Dallas، قبض یک مشتری یا هزینهٔ نهایی برق.
- مبالغ خرید، اجاره، نگهداری، هزینه‌های جانبی، ساعت کار، ارزش باقیمانده و تعداد تحویل‌ها در fixture همگی **فرض آموزشی مصنوعی**‌اند، نه قیمت بازار و نه پیشنهاد خرید.
- یک denominator مشترک در fixture برابری زمان اجرا، کیفیت، دسترس‌پذیری، throughput یا تناسب بار را اثبات نمی‌کند. هیچ رتبه‌بندی خودکاری برای تصمیم خرید گزارش نمی‌شود.

منابع قیمت: [Google Cloud accelerator-optimized pricing](https://cloud.google.com/products/compute/pricing/accelerator-optimized), [Google Cloud accelerator-optimized machine documentation](https://docs.cloud.google.com/compute/docs/accelerator-optimized-machines), [EIA Table 5.6.A](https://www.eia.gov/electricity/monthly/xls/table_5_06_a.xlsx). همهٔ URLها و تاریخ‌ها نیز در fixture آمده‌اند.

## محدودیت‌ها

مدل آموزشی مالیات، تأمین مالی، تورم، افزایش آتی قیمت، هزینهٔ تقاضای برق، خاموشی، نیروی انسانی، ریسک خرابی/تأخیر، جایگزینی، ارزش زمان کارکنان و اقلامی را که صریحاً در fixture نیستند وارد محاسبه نمی‌کند. حتی «سایر هزینه‌ها» فقط فرض synthetic سالانه‌اند. برای تصمیم واقعی باید محدودهٔ خدمت و خروجی همسان، پیش‌فاکتور معتبر همان بازار/تاریخ، قرارداد و دورهٔ صورتحساب، اندازه‌گیری برق در مرز مشخص، هزینه‌های تأسیسات/شبکه و ریسک‌ها جداگانه راستی‌آزمایی شوند.
