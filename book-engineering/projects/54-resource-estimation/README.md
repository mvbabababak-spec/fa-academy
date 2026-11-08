# پروژهٔ فصل ۵۴: برآورد حسابی حافظه و FLOPs

این پروژه، ورودی‌های صریح و fixtureهای ساختگی را با Python standard library به حساب اجزای حافظه و محاسبه تبدیل می‌کند. **مدل واقعی بارگذاری نمی‌شود؛ GPU خوانده نمی‌شود؛ آموزش، benchmark یا اندازه‌گیری انجام نمی‌شود.** نتیجه را فقط به‌عنوان حسابِ فرض‌ها بخوانید، نه توصیهٔ خرید، تضمین جا شدن مدل یا پیش‌بینی زمان اجرا.

## اجرا

```bash
python resource_estimator.py --output results.json
python -m unittest -v
```

برای دادهٔ دیگر، fixture JSON را با schema پروژه بسازید:

```bash
python resource_estimator.py --fixture path/to/profile.json --output path/to/report.json
```

یا بدون نوشتن فایل، JSON را به stdout بفرستید:

```bash
python resource_estimator.py
```

## آنچه حساب می‌شود

- وزن‌ها، گرادیان‌ها، کپی master و حالت optimizer را با بایتِ ورودی‌شده برای هر پارامتر؛
- تقسیم ایدئال حالت‌ها در stageهای ZeRO، نه بافرهای ارتباطی یا رفتار واقعی framework؛
- یک «مرجع فعال‌سازی» شفاف از تعداد معادل‌های hidden-state که خود کاربر تعیین می‌کند؛
- KV cache با تعداد لایه، batch فعال، token، KV head، بُعد head و بایت هر عنصر؛
- تقریب‌های FLOPs برای آموزش متراکم و بخش‌های خطی استنتاج؛
- تبدیل بایت به GB ده‌دهی و GiB دودویی به‌صورت جدا.

`sample_profiles.json` چهار سناریوی فرضی دارد: استنتاج GQA، آموزش همهٔ پارامترها، تنظیم adapter با ۳۵ میلیون پارامتر آموزش‌پذیر، و تقسیم ایدئال stage 3 روی چهار رتبه. هیچ سناریویی یک مدل منتشرشده یا اندازه‌گیری دستگاه نیست.

## مرزهای مدل

فرمول فعال‌سازی فقط شمار معادل‌های اعلام‌شده را ضرب می‌کند؛ حافظهٔ واقعی به معماری، طول دنباله، attention kernel، autograd، checkpointing/rematerialization، batch و نسخهٔ نرم‌افزار وابسته است. محاسبهٔ stageهای ZeRO، padding، gather/reduce buffer، fragmentation، allocator، offload و runtime را مدل نمی‌کند. فرمول `6ND` تقریب dense-transformer است؛ هزینهٔ attention در دنباله‌های بلند، recomputation و جزئیات اجرای واقعی می‌توانند آن را تغییر دهند. تخمین FLOPs زمان دیواری یا throughput نیست.

برای تصمیم اجرایی، پس از برآورد کاغذی یک اجرای کوچک روی **همان** مدل، dtype، framework، optimizer، attention backend، sequence/batch و روش checkpointing انجام دهید؛ اوج allocation در forward/backward/optimizer و مصرف سطح دستگاه را با ابزار همان محیط ثبت کنید. این پروژه چنین آزمایشی انجام نمی‌دهد.
