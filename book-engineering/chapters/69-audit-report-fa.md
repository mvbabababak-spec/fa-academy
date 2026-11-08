# گزارش ممیزی فصل ۶۹

**نگاشت:** فصل محلی ۸ جلد پنجم = فصل سراسری ۶۹. **تاریخ ممیزی: ۴ نوامبر ۲۰۲۶.** موضوع این گزارش استقرار ابری/محلی، نسخه‌بندی، CI/CD، rollout، بازگشت نسخه و هزینهٔ نگه‌داری است. فصل ۶۸ منتشر شده و تکرار نشده است؛ فصل ۷۰ تا تأیید انتشار این فصل آغاز نمی‌شود.

## دامنه و روش

ممیزی منبع Markdown، پاسخ‌نامهٔ مستقل، شکل SVG، پروژهٔ بازتولیدپذیر، fixture ساختگی، نتایج و فرادادهٔ محیط را در برابر نقشه و راهنمای سبک جلد پنجم بررسی می‌کند. مرز فصل‌های مجاور حفظ شده است: قرارداد محصول و API در فصل ۶۶، ظرفیت و تأخیر سرو در فصل ۶۷ و کنترل‌های امنیت محصول در فصل ۶۸ باقی می‌مانند. فصل ۷۰ خواندن مقاله و بازتولید پژوهش را پوشش می‌دهد.

شبیه‌ساز gate با ۳۵ آزمون و سرویس HTTP محلی با ۶ آزمون واحد/loopback، در مجموع ۴۱ آزمون، بررسی شده‌اند. سرویس آزمایشی فقط روی loopback گوش می‌دهد؛ آزمون‌ها health، version، پاسخ پیش‌بینیِ ثابت، رد ورودی دارای prompt اضافه و مسیر ناشناخته را پوشش می‌دهند. هیچ درخواست بیرونی، فراخوانی مدل، وزن مدل، credential واقعی، نوشتن production یا deployment ابری انجام نشده است. نتیجه‌ها از فایل `synthetic_release_scenarios.json` می‌آیند و پروژه وابستگی خارجی ندارد.

## نتایج fixture

| سناریو | تصمیم شبیه‌ساز | مشاهده | تفسیر محدود |
|---|---|---|---|
| `healthy_staged_rollout` | `promoted` | ۵٪ ← ۲۵٪ ← ۱۰۰٪ | gateهای تعریف‌شده در fixture سبز شدند؛ شاهد آمادگی محیط واقعی نیست. |
| `latency_regression_rolls_back` | `rolled_back` | در مرحلهٔ ۲۵٪، p95 ساختگی ۹۳۰ms از حد ۸۰۰ms بالاتر رفت؛ active release به `stable-r3` برگشت. | مسیر rollback منطقی در سناریوی مصنوعی آزموده شد؛ دادهٔ production یا تضمین rollback پایگاه‌داده نیست. |
| `missing_provenance_is_blocked` | `blocked` | provenance تأییدنشده بود و rollout آغاز نشد. | رفتار gate در برابر ورودی ناقص آزموده شد؛ این شبیه‌ساز provenance واقعیِ امضاشده تولید یا اعتبارسنجی نمی‌کند. |

خلاصهٔ fixture: یک promotion، یک rollback، یک block و صفر hold. SHA-256 fixture: `4b8824611574ac3ed631bdc81bc78037116afec70acee6942151c59f8ad3a57f`. SHA-256 خروجی ثبت‌شده: `c0efd8a0f9c3aab4d8bb810d43c20ae8c83375b370dfd0a58c50a9fe03596520`.

## آزمون‌های یکپارچه‌سازی و مرورگر

سازندهٔ جلد پنجم ۸ فصل از ۱۲ فصل برنامه‌ریزی‌شده را تولید کرد؛ تعداد بخش‌ها به‌ترتیب ۲۶، ۳۴، ۳۹، ۴۱، ۴۰، ۲۸، ۳۷ و ۲۹ است. `check_volume5.py` موفق شد و ۱۰۴ مسیر آفلاین را بررسی کرد؛ Service Worker به `v110` رسید. اجرای دوبارهٔ سازنده پس از ثبت خروجی‌های مشتق‌شده باید بدون تغییر بماند.

`test_volume5.py` با Playwright 1.64.1 و Chromium 156.0.8078.4 در ۳۲۰، ۳۹۰، ۷۶۸ و ۱۴۴۰ پیکسل گذشت؛ هشت فصل، MathML، SVG، پیوند به پاسخ‌نامه/پروژه/گزارش، تطبیق دقیق پیوست اجرایی و ۱۰۴ asset آفلاین بررسی شدند. `test_mobile_layout.py` نیز در ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل گذشت؛ ۱٬۴۲۳ بخش کتاب‌ها و دوره‌ها، RTL، سرصفحه، جابه‌جایی فصل، قالب‌بندی و دسترسی آفلاین فصل‌های ۵۵ تا ۶۹ سنجیده شد.

در log آزمون سراسری، ۳۶ پاسخ 404 از ۸ مسیر دارایی تصویری قدیمیِ خارج از فصل ۶۹ ثبت شد؛ موارد در محدودهٔ منابع این فصل نیستند و در این تغییر اصلاح نشده‌اند. آزمون‌های browser/mobile با وجود آن پاسخ‌ها موفق بودند و 404 برای دارایی فصل ۶۹ گزارش نشد. خروجی log ممیزی در `.tmp-audit/` است. `book-engineering/reports/browser-mobile.webp` در checkout مبنا وجود نداشت؛ فایل ساخته یا بازنویسی نشد.

## انتشار، CI و Pages

مبنای انتشار، شاخهٔ `gh-pages` با SHA پیشین `a5b892f8f2849b894be2b51776fff9c3b7586029` بود. commit محتوای فصل ۶۹ `23cccad26d46f072c46c70c0e6832daa133625d3` با push عادی منتشر شد؛ شاخهٔ remote همان SHA را گزارش کرد. [اجرای GitHub Actions، Volume 5 audit #15](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42450263887) برای این commit موفق شد (۲ دقیقه و ۴۴ ثانیه).

Pages پس از انتشار پاسخ ۲۰۰ داد: فایل فصل، `data.json` و Service Worker در دسترس بودند؛ `sw.js` نشانگر `v110` داشت و دادهٔ زنده ۸ فصل جلد پنجم، ۲۹ بخش فصل ۶۹ و ۱٬۴۲۳ بخش در کل کتاب‌ها/دوره‌ها را گزارش کرد. آزمون Playwright روی خود Pages نیز در حالت آنلاین جلد پنجم را با ۸ فصل دید؛ پس از cache شدن، صفحه و پنج فایل فصل ۶۹ در حالت offline هم با پاسخ ۲۰۰ بارگذاری شدند.

اجرای CI شمارهٔ ۱۵ یک هشدار Node 20 برای `actions/checkout` و یک اطلاع‌رسانی مهاجرت label `ubuntu-latest` نشان داد. این دو مورد شکست آزمون نبودند؛ برای جلوگیری از drift، workflow در این اصلاح با SHA کامل `actions/checkout` نسخهٔ ۵٫۱٫۰ و runner صریح `ubuntu-24.04` pin شده است. اجرای CI که با commit اصلاح گزارش آغاز می‌شود باید همین تغییر workflow را نیز تأیید کند.

## منابع اولیه و تاریخ بازبینی

منابع زیر در ۴ نوامبر ۲۰۲۶ بازبینی شده‌اند؛ نسخه و دامنهٔ ادعا در متن فصل مشخص شده است.

- NIST، [Secure Software Development Framework (SSDF) Version 1.1، SP 800-218](https://csrc.nist.gov/pubs/sp/800/218/final)، فوریهٔ ۲۰۲۲.
- NIST، [Secure Software Development Practices for Generative AI and Dual-Use Foundation Models، SP 800-218A](https://csrc.nist.gov/pubs/sp/800/218/a/final)، ژوئیهٔ ۲۰۲۴؛ مکمل SSDF است، نه جایگزین آن.
- OpenSSF، [SLSA specification v1.2](https://slsa.dev/spec/v1.2/)، به‌ویژه [Build Track Basics](https://slsa.dev/spec/v1.2/build-track-basics) و [Build Provenance](https://slsa.dev/spec/v1.2/build-provenance). سطح SLSA فقط با شواهد انطباق ادعا می‌شود؛ پروژهٔ این فصل ادعای انطباق سطحی ندارد.
- DORA، [Continuous delivery](https://dora.dev/capabilities/continuous-delivery/)؛ تحویل پیوسته از استقرار پیوسته متمایز شده است.
- GitHub Docs، [Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)، [Managing environments for deployment](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments) و [OpenID Connect](https://docs.github.com/en/actions/concepts/security/openid-connect). قابلیت‌های environment ممکن است به plan وابسته باشند؛ trust policy و subject claim باید با وضعیت جاری مخزن تطبیق داده شوند.
- Google SRE Workbook، [Canarying Releases](https://sre.google/workbook/canarying-releases/)، برای canary زمان‌مند و ارزیابی در برابر کنترل؛ Kubernetes، [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)؛ Docker، [Building best practices](https://docs.docker.com/build/building/best-practices/) برای digestهای ثابت و به‌روزرسانی آگاهانهٔ image.
- Google Cloud، [AI and ML perspective: Reliability](https://docs.cloud.google.com/architecture/framework/perspectives/ai-ml/reliability)، صفحه با برچسب «Last reviewed 2026-10-29»؛ بخش‌های MLOps رفتار مدل را اعتبارسنجی می‌کنند و برای deployment کنترل ترافیک، canary، سنجه‌ها، rollback خودکار و آزمون latency/throughput پیش از جابه‌جایی ترافیک را صریحاً توصیه می‌کنند. این توصیه‌ها vendor-specific هستند و در فصل به الزام عمومی تعمیم داده نشده‌اند.

## محدودیت‌ها

نتایج پروژه آزمون ساختگی‌اند و به‌تنهایی CI/CD واقعی، دسترس‌پذیری، هزینه، مقیاس‌پذیری، کیفیت مدل، امنیت کامل، آمادگی تولید، artifact قابل‌اعتماد، provenance امضاشده یا انطباق SLSA را اثبات نمی‌کنند. رقم ۹۳۰ms نمونهٔ ثابت در fixture است و برآورد latency واقعی نیست. rollback آزمایشی تنها شناسهٔ نسخهٔ فعال را عوض می‌کند؛ مهاجرت داده، schema پایگاه‌داده و سازگاری نسخه‌ها باید جداگانه طراحی و آزموده شوند. هزینهٔ این فصل به‌صورت چارچوب تصمیم‌گیری مطرح می‌شود و قیمت‌نامه یا TCO زنده ارائه نمی‌دهد.

**خروجی ممیزی:** منبع Markdown، پاسخ‌نامه، پروژه و نتیجهٔ fixture مستقل از هم هستند؛ پیوست اجرایی فصل عیناً از فایل gate آزموده‌شده درج شده است. محصول این مخزن وب/PWA و Markdown است؛ PDF و EPUB تولید و آزموده نشده‌اند.
