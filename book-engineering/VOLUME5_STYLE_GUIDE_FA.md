# راهنمای نگارش و انتشار تدریجی جلد پنجم

## نقشه و مرز موضوعی

جلد پنجم ۱۲ فصل محلی دارد که با فصل‌های سراسری ۶۲–۷۳ متناظرند. فصل‌های ۶۲–۶۵ کیفیت، امنیت و مسئولیت؛ فصل‌های ۶۶–۶۹ تبدیل مدل به محصول؛ و فصل‌های ۷۰–۷۳ پژوهشگر و معمار مستقل را پوشش می‌دهند. ساختار جلدهای ۱–۴ و شناسه‌های آن‌ها باید بدون تغییر بمانند.

- فصل ۶۲: طراحی benchmark و آزمون، metric، ارزیابی انسانی، عدم‌قطعیت و آلودگی. کارایی runtime و benchmark استنتاج در فصل ۶۱ است؛ تحلیل تفصیلی توهم/سوگیری در ۶۳ و آزمون خصمانه در ۶۴ است.
- فصل ۶۳: توهم، سوگیری، استحکام، توضیح‌پذیری و تفسیرپذیری؛ روش و مرز اندازه‌گیری.
- فصل ۶۴: Red Teaming، حمله، Prompt Injection، مسموم‌سازی، استخراج مدل و حریم خصوصی.
- فصل ۶۵: هم‌ترازیِ سازمانی، حکمرانی، مدل‌کارت/داده‌کارت و مدیریت ریسک؛ جزئیات حمله در ۶۴ می‌ماند و ساخت API در ۶۶ آغاز می‌شود.
- فصل ۶۶: API و ساخت محصول، قرارداد داده، backend/frontend و آزمایش رابط؛ نه بهینه‌سازی runtime فصل ۶۷.
- فصل ۶۷: سرو، صف، cache، تأخیر و توان عملیاتی؛ نه حاکمیت/کارت‌های فصل ۶۵ یا امنیت محصول/پایش فصل ۶۸.
- فصل ۶۸: احراز هویت، محدودیت نرخ، ثبت رخداد، حریم خصوصی، پایش و پاسخ به رخداد؛ فصل ۶۹ به استقرار و CI/CD اختصاص دارد.
- فصل ۶۹: استقرار ابری/محلی، نسخه‌بندی، CI/CD، بازگشت نسخه و نگه‌داری؛ مرز محصول فصل‌های ۶۶–۶۸ حفظ شود.

پیش از هر فصل، وضعیت شاخهٔ محلی و remote، فایل‌های هم‌نام و نسخهٔ roadmap بررسی شود؛ سپس ساختار هر پنج جلد و مرز دو فصل مجاور دوباره خوانده شود. فصل تکمیل‌شده دوباره نوشته نشود. فصل‌ها به ترتیب محلی ۱ تا ۱۲، هرکدام با یک commit مستقل و push عادی منتشر می‌شوند؛ آغاز فصل بعد تنها پس از تأیید remote فصل قبل مجاز است. Force push ممنوع است.

## قالب هر فصل

هر فصل باید منبع مستقل Markdown، پاسخ‌نامهٔ مستقل که متن سؤال‌ها را عیناً حفظ می‌کند، پروژهٔ کوچک قابل‌بازتولید، fixture یا دادهٔ نمونه با منشأ روشن، آزمون، `results.json`/`environment.json` متناسب با دامنه، شکل دسترس‌پذیر و گزارش ممیزی داشته باشد. کد پیوست‌شده در انتهای فصل باید بایت‌به‌بایت با فایل اجرایی آزموده‌شده برابر باشد. شناسه‌های موجود در جلدهای دیگر ثابت می‌مانند.

گزارش نتیجه باید تنها چیزی را ادعا کند که واقعاً آزموده شده است. Fixture ساختگی، اجرای CPU یا آزمون واحد به‌تنهایی benchmark واقعی، کیفیت زبان، تأیید انسانی، نبود آلودگی، ایمنی، حریم خصوصی کامل، استقرار یا عملکرد سخت‌افزار را ثابت نمی‌کند. منابع اولیه/معتبر و تاریخ بازبینی آن‌ها ثبت شوند؛ نتیجهٔ پژوهش به شرایط همان منبع محدود بماند.

## فارسی، شکل و دسترس‌پذیری

- نثر فارسی روان با نیم‌فاصله و جهت RTL باشد؛ شکست خط دستی و فاصله‌گذاری مصنوعی انجام نشود. اصطلاح فنی در صورت نیاز با صورت استاندارد بیاید؛ متن مستقل انگلیسی در سطر جدا قرار گیرد.
- متن جایگزین شکل باید رابطه یا مسیر، مقدار/محدودیت مهم و مفهومی/داده‌ای بودن نمودار را توضیح دهد؛ معنا به رنگ وابسته نباشد. ریشهٔ SVG شامل `role="img"`، `aria-labelledby`، `<title>` و `<desc>` یکتا باشد؛ گره‌های فارسی `xml:lang="fa"` بگیرند.
- MathML باید برچسب دسترس‌پذیر داشته باشد. کد، جدول، عنوان و کپشن استثنای قاعدهٔ تورفتگی نثرند؛ نثر پاسخ‌نامه هم‌راستا و فارسی‌رقم باشد، مگر متن سؤال/شناسهٔ فنی عیناً حفظ شود.
- رندرها و screenshotهای audit در `.tmp-audit/` قرار بگیرند. فایل‌های مرجع، پوشهٔ `uploads/` و دارایی‌های جلدهای دیگر تغییر نکنند. وجود نویسهٔ CJK فقط با scan codepoint متن واقعی سنجیده شود، نه با فهرست فونت‌های نصب‌شده.

## ساخت، بررسی و انتشار

از ریشهٔ repository:

```bash
python book-engineering/build_volume5.py
python book-engineering/check_volume5.py
(cd book-engineering/projects/62-evaluation-lab && python -m unittest -v)
python book-engineering/projects/62-evaluation-lab/evaluation_lab.py --output /tmp/ch62-results.json
(cd book-engineering/projects/63-model-behavior-lab && python -m unittest -v)
python book-engineering/projects/63-model-behavior-lab/model_behavior_lab.py --output /tmp/ch63-results.json
(cd book-engineering/projects/64-red-team-lab && python -m unittest -v)
python book-engineering/projects/64-red-team-lab/red_team_lab.py --output /tmp/ch64-results.json
(cd book-engineering/projects/65-governance-lab && python -m unittest discover -v)
python book-engineering/projects/65-governance-lab/governance_check.py --output /tmp/ch65-results.json
python -m pip install -r book-engineering/projects/66-ai-product-api/requirements.txt
python book-engineering/projects/66-ai-product-api/audit.py --output /tmp/ch66-results.json
cmp /tmp/ch66-results.json book-engineering/projects/66-ai-product-api/results.json
(cd book-engineering/projects/67-serving-lab && python -m unittest -v)
python book-engineering/projects/67-serving-lab/serving_lab.py \
  --fixture book-engineering/projects/67-serving-lab/synthetic_serving_trace.json \
  --output /tmp/ch67-results.json
cmp /tmp/ch67-results.json book-engineering/projects/67-serving-lab/results.json
(cd book-engineering/projects/68-product-security-lab && python -m unittest -v)
python book-engineering/projects/68-product-security-lab/security_ops.py \
  --fixture book-engineering/projects/68-product-security-lab/synthetic_security_events.json \
  --output /tmp/ch68-results.json
cmp /tmp/ch68-results.json book-engineering/projects/68-product-security-lab/results.json
python book-engineering/test_volume5.py
python book-engineering/test_mobile_layout.py
```

`build_volume5.py` منبع‌های پیوسته را به `data.json`، `volume-5-full-fa.md` و cache آفلاین Service Worker می‌افزاید؛ هیچ فصل ثبت‌شده یا شناسهٔ جلدهای ۱–۴ را بازنویسی نمی‌کند. پیوندهای محلی در فایل Markdown نسبت به پوشهٔ خود منبع باشند؛ سازنده فقط هنگام درج HTML در ریشهٔ reader آن‌ها را به مسیر site-root تبدیل می‌کند تا هم فایل Markdown مستقل بماند و هم لینک‌های وب درست باز شوند. مسیر پروژه، پاسخ‌نامه و شکل برای فصل‌های موجود صریح و داده‌محور نگاشت شده است. `check_volume5.py` ساختار، ID، پیوند، MathML/SVG، تطبیق عینِ پرسش و پاسخ، پیوست دقیق، خروجی Markdown و cache را بررسی می‌کند. `test_volume5.py` هر فصل موجود را در ۳۲۰، ۳۹۰، ۷۶۸ و ۱۴۴۰ پیکسل، و `test_mobile_layout.py` پوشش سراسری را در ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل می‌آزماید. پس از انتشار، SHA remote، workflowها و دسترسی فایل‌های وب/PWA در گزارش نهایی ثبت شوند.

خروجی این milestone وب/PWA و Markdown است. PDF یا EPUB فقط در صورت تولید و آزمون واقعی در گزارش ذکر می‌شود.
