# پروژهٔ فصل ۵۳ — زنجیرهٔ Diffusion روی یک مخلوط ساختگی دوبعدی

این پروژه با کتابخانهٔ استاندارد Python یک برنامهٔ آموزشی کوچک برای زنجیرهٔ forward و یک sampler معکوس DDPM می‌سازد. fixture چهار مؤلفهٔ Gaussian دوبعدی دارد؛ score هر گام از چگالی تحلیلی همین مخلوط به‌دست می‌آید. **شبکهٔ عصبی، مدل تصویر/ویدئو، دادهٔ واقعی، فایل رسانه‌ای، وزن آموزش‌دیده یا benchmark وجود ندارد.** score «oracle» این مثال عمداً معلوم است تا سازوکار فرمول‌ها آزمون‌پذیر باشد؛ چیزی یاد گرفته نمی‌شود.

## اجرا

از ریشهٔ مخزن:

```bash
(cd book-engineering/projects/53-diffusion-lab && python -m unittest discover -v)
python book-engineering/projects/53-diffusion-lab/diffusion_lab.py \
  --mode audit --fixture book-engineering/projects/53-diffusion-lab/sample_mixture.json \
  --output /tmp/ch53-audit
python book-engineering/projects/53-diffusion-lab/diffusion_lab.py \
  --mode demo --fixture book-engineering/projects/53-diffusion-lab/sample_mixture.json \
  --output /tmp/ch53-demo --steps 200 --samples 64 --seed 53
```

وابستگی خارجی یا دسترسی شبکه لازم نیست. `audit` schema و SHA-256 fixture را ثبت می‌کند. `demo` از prior استاندارد نرمال در انتهای زنجیره شروع می‌کند و با score تحلیلی، به‌روزرسانی معکوس DDPM را اجرا می‌کند؛ فایل `run.json` نقاط دوبعدی و خلاصهٔ آن‌ها را ذخیره می‌کند. به‌دلیل ثابت‌بودن seed، همین نسخهٔ Python و fixture باید همان نقاط را بازتولید کند.

## مرز نتیجه

این آزمایش فقط منطق schedule، noising، رابطهٔ score/epsilon، posterior variance و یک زنجیرهٔ نمونه‌گیری دوبعدیِ بسیار کوچک را نشان می‌دهد. score به‌طور تحلیلی از توزیعی معلوم محاسبه می‌شود؛ بنابراین پروژه نه هدف آموزش یک مدل واقعی را دارد و نه کیفیت نمونه‌سازی آموخته‌شده را می‌سنجد. نقاط دوبعدی «تصویر» یا «ویدئو» نیستند. خروجی را به کیفیت مدل، وفاداری به prompt، کیفیت فارسی، سخت‌افزار، سرعت، benchmark، ایمنی، حریم خصوصی، مجوز یا نتیجهٔ حقوقی تعمیم ندهید. کد آموزشی، روش تولید ایمن یا مجوز انتشار محتوا نیست.

اعداد دقیق اجرای audit/demo، hash و تعداد آزمون‌ها در `results.json` ثبت می‌شوند؛ محدودیت‌های بازبینی نیز در `../../chapters/53-audit-report-fa.md` آمده است.
