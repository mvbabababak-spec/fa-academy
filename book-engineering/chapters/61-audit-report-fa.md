# گزارش ممیزی فصل ۶۱ — سرو و بهینه‌سازی استنتاج

- **تاریخ:** ۷ نوامبر ۲۰۲۶
- **شناسه:** فصل محلی ۱۵ جلد چهارم / سراسری ۶۱
- **دامنه:** runtime استنتاج، export و مصالحه‌های اندازه‌گیری؛ نه API محصول یا استقرار سازمانی

## نتایج اجرای واقعی

پروژه در Linux x86-64 با CPython 3.13.16 و کتابخانهٔ استاندارد Python اجرا شد. ۲۴/۲۴ آزمون unit موفق شدند:

```bash
cd book-engineering/projects/61-inference-serving
python3.13 -m unittest -v
python3.13 inference_lab.py --fixture sample_trace.json --output /tmp/ch61-analysis.json
```

اجرای CLI موفق بود و JSON قطعی تولید کرد. برچسب منبع fixture برابر `synthetic_fixture` است؛ SHA-256 فایل `sample_trace.json` برابر `e53d085e8386c0c8d8dcb9b8b0c7ab9508bfef8d3f72341ea6c5f58bb9ffaf7c` است. برای فرض ۳۲ لایه، ۸ سر KV، بُعد ۱۲۸، دقت دو بایت، طول ۴٬۰۹۶ و هشت دنباله، محاسبهٔ ساده ۱۳۱٬۰۷۲ بایت به‌ازای هر token، ۰٫۵ GiB برای یک دنباله و ۴ GiB برای هشت دنباله گزارش کرد.

دو trace با برچسب‌های `illustrative-static` و `illustrative-candidate` ساختگی‌اند. هر کدام ۵ درخواست موفق از ۶ تلاش، پنجرهٔ ۲٬۰۰۰ ms، نرخ ۲٫۵ درخواست موفق بر ثانیه و ۲۳۴ توکن خروجی بر ثانیه دارند. p95 TTFT به‌ترتیب ۳۵۰ و ۲۰۰ ms و p95 end-to-end برابر ۱٬۰۸۰ و ۸۲۰ ms شد. این اعداد از timestampهای قراردادی fixture محاسبه شده‌اند؛ هیچ runtime، مدل، GPU یا scheduler اجرا نشده است و اعداد ادعای برتری batching نیستند.

`results.json`, `environment.json` و `fixture_manifest.json` هویت trace، hash، خروجی محاسبه، نسخهٔ Python، شمار آزمون و scope را ثبت می‌کنند. پروژه وابستگی خارجی ندارد؛ `pip check` برای آن کاربرد ندارد.

## کنترل محتوایی و دسترس‌پذیری

فصل ۲۵ بخش دارد، دو فرمول MathML با `aria-label` و متن جایگزین دارد، نمودار SVG به‌اندازهٔ ۱۶۰۰×۱۰۰۰ و با برچسب‌های دوجهتهٔ جداگانه ساخته شده است و alt آن رابطهٔ artifact، runtime، سنجه و محدودیت را توضیح می‌دهد. هفت صورت تمرین در پاسخ‌نامهٔ مستقل، بدون تغییر متن، تکرار شده‌اند. پیوست اجرایی با `inference_lab.py` بایت‌به‌بایت منطبق است. builder جلد چهارم فصل را فقط به‌عنوان فصل محلی ۱۵ / شناسهٔ پایدار `art-science-v4-ch15` اضافه می‌کند؛ فصل‌های محلی ۱–۱۴ بازنویسی نشده‌اند.

### گیت‌های جلد چهارم، رابط و آفلاین

گیت‌های محلی با Python 3.13.16، Playwright 1.64.1 و Chromium (Chrome for Testing 156.0.8078.4) اجرا شدند:

- `python3.13 -B book-engineering/check_volume4.py` — موفق: ۱۵/۱۵ فصل، ۳۴۴ بخش، ۶۰ عبارت MathML دسترس‌پذیر، پیوست‌های دقیق و حضور گزارش‌ها، پاسخ‌نامه‌ها و fixtureها.
- `python book-engineering/test_volume4.py` — موفق در عرض‌های ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل؛ ۱۵ فصل، ۱۶۲ مسیر یکتای ذخیره‌سازی آفلاین، و آزمون متن، MathML و تطبیق پیوست‌ها.
- `python book-engineering/test_mobile_layout.py` — موفق در عرض‌های ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل؛ ۱٬۱۴۹ بخش، ناوبری RTL و دسترسی آفلاین به متن، پاسخ‌نامه و نمودار فصل‌های ۵۶ تا ۶۱.
- `git diff --check` — موفق.

در لاگ آزمون موبایل چند درخواست HTTP 404 برای تصویرهای بخش‌های دیگر سایت دیده شد؛ از جمله مسیرهای `Mark_I_perceptron_wikipedia`، `Rosenblatt-wikipedia`، یک تصویر DALL·E و `assets/images/ml/p%26amp%3Bp.279f1c49ecd88941.webp`. این نشانی‌ها خارج از فصل ۶۱ و فهرست ۱۶۲ دارایی آفلاین جلد چهارم‌اند؛ آزمون با کد خروج موفق پایان یافت و این دارایی‌های نامرتبط در patch فصل ۶۱ تغییر داده نشده‌اند. این گزارش نتایج محلی را ثبت می‌کند؛ وضعیت GitHub Actions، Pages و hashهای نسخهٔ زنده باید پس از push جداگانه تأیید شوند.

## محدودیت‌های آزمون

مدل واقعی، وزن pretrained، vLLM، llama.cpp، Ollama، ONNX Runtime GenAI، TensorRT-LLM، export، quantization، GPU/driver، benchmark واقعی، کیفیت خروجی، open-loop load، پایداری طولانی‌مدت، API محصول و استقرار Docker/Kubernetes اجرا یا آزموده نشده‌اند. percentile fixture شش‌درخواستی تخمین آماری tail نیست؛ برآورد KV نیز فقط payload dense و ایده‌آل است و fragmentation، workspace، وزن‌ها، activation و تفاوت معماری را دربرنمی‌گیرد. پشتیبانی و API هر runtime باید برای نسخه و دستگاه منتخب از مستندات رسمی همان release بازبینی شود.

PDF و EPUB تولید یا آزموده نشده‌اند؛ خروجی کتاب وب/PWA و Markdown است.
