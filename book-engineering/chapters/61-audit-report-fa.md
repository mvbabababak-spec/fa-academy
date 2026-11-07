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

در لاگ آزمون موبایل چند درخواست HTTP 404 برای تصویرهای بخش‌های دیگر سایت دیده شد؛ از جمله مسیرهای `Mark_I_perceptron_wikipedia`، `Rosenblatt-wikipedia`، یک تصویر DALL·E و `assets/images/ml/p%26amp%3Bp.279f1c49ecd88941.webp`. این نشانی‌ها خارج از فصل ۶۱ و فهرست ۱۶۲ دارایی آفلاین جلد چهارم‌اند؛ آزمون با کد خروج موفق پایان یافت و این دارایی‌های نامرتبط در patch فصل ۶۱ تغییر داده نشده‌اند.

## GitHub Actions و نسخهٔ زنده

فصل در commit مستقل `1f5ff067c2343f0b07823873dbcb0e3a301105fb` با push معمولی روی `gh-pages` منتشر شد و remote tip با همان SHA تأیید شد. روی همین commit، هر چهار audit و Pages موفق شدند: [Volume 1 — run 42353970424](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42353970424)، [Volume 2 — run 42353970391](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42353970391)، [Volume 3 — run 42353970378](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42353970378)، [Volume 4 — run 42353970415](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42353970415) و [Pages — run 42353970100](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42353970100). artifact مربوط به `github-pages` با اندازهٔ ۱۳۰ MB و digest `sha256:60484bcf35a3154d0787940e6cd65556b8552e9b415249c3b8cdc85aac22e255` ساخته و deploy شد.

صفحهٔ زندهٔ [اپ/PWA](https://mvbabababak-spec.github.io/fa-academy/) پس از deploy با HTTP 200 باز شد؛ شمار جلد چهارم ۱۵ فصل و ۳۴۴ بخش را نشان می‌دهد. دوازده فایل شامل `index.html`، README و نقشه، `data.json`، `sw.js`، Markdown جلد چهارم، فصل/گزارش/پاسخ‌نامه، SVG و دو فایل پروژه نیز HTTP 200 دادند و hash محلی/زنده‌شان برابر بود. SHA-256 فایل‌های اصلی:

| فایل | SHA-256 محلی = زنده |
| --- | --- |
| `index.html` | `f998310cbcf762dd800dd0060ac582545a0560ca0c9b9ff9cb02f4fa91b6fea4` |
| `data.json` | `5c9f1a0defbe7cb9f60340d501c5197c8637479ce130adc0574d79cd29dfe2dd` |
| `sw.js` | `22645bc5b11d02b13b44eab7b574083c3be53d4b6ed41d3b943959692975f689` |
| `volume-4-full-fa.md` | `9b87b1179cef647631db62eaf030779ab03bc7e7ac3510df317cbc7c9b4c2639` |
| `book-engineering/chapters/61-inference-serving.md` | `153351780cb17a6269b025e7e759ad4444c33a4c06170eb4cdc2918c66a80c74` |
| `book-engineering/answers/61-inference-serving-fa.md` | `c8328752984c1e06145604ba18823042327fd575936e8e97b509b6bb9b75fb6a` |
| `book-engineering/diagrams/v4-ch15-inference-serving.svg` | `d2b3d82a32131b3cd94895e528df88379d7a75bd3b1b365cec91ef3352960341` |
| `book-engineering/projects/61-inference-serving/inference_lab.py` | `6711898bdf18f05a8f7ba9edda080a79a5e20201bfc20fe590413a2872156a1f` |
| `book-engineering/projects/61-inference-serving/sample_trace.json` | `e53d085e8386c0c8d8dcb9b8b0c7ab9508bfef8d3f72341ea6c5f58bb9ffaf7c` |

## محدودیت‌های آزمون

مدل واقعی، وزن pretrained، vLLM، llama.cpp، Ollama، ONNX Runtime GenAI، TensorRT-LLM، export، quantization، GPU/driver، benchmark واقعی، کیفیت خروجی، open-loop load، پایداری طولانی‌مدت، API محصول و استقرار Docker/Kubernetes اجرا یا آزموده نشده‌اند. percentile fixture شش‌درخواستی تخمین آماری tail نیست؛ برآورد KV نیز فقط payload dense و ایده‌آل است و fragmentation، workspace، وزن‌ها، activation و تفاوت معماری را دربرنمی‌گیرد. پشتیبانی و API هر runtime باید برای نسخه و دستگاه منتخب از مستندات رسمی همان release بازبینی شود.

PDF و EPUB تولید یا آزموده نشده‌اند؛ خروجی کتاب وب/PWA و Markdown است.
