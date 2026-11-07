# گزارش ممیزی فصل سراسری ۶۶ — API، FastAPI و قرارداد محصول

**نگاشت:** فصل محلی ۵ جلد پنجم = فصل سراسری ۶۶. **تاریخ ممیزی محلی: ۷ نوامبر ۲۰۲۶.** این گزارش نتیجهٔ fixture ساختگی، آزمون‌های API/مرورگر و گیت‌های کتاب را از هم جدا می‌کند. هیچ پاسخ مدل واقعی، کیفیت محصول، امنیت یا مجوز انتشار از این نتایج استنتاج نمی‌شود.

## دامنه و محیط پروژه

- پروژه: `book-engineering/projects/66-ai-product-api/`؛ شناسهٔ fixture: `v5-ch05-api-contract-synthetic-v1`؛ SHA-256: `aa333a70cf87376fdde7a919d5b79fc1a97cf4ea8da15c8eab89c551c2070bad`.
- Fixture یک رکورد و دو پاسخ متنی ساختگی دارد؛ دادهٔ شخصی، حساب، مدل زنده یا منبع بیرونی ندارد. دامنهٔ `example.invalid` رزروشده و صرفاً نمایشی است.
- محیط: CPython 3.13.16، FastAPI 0.162.2، Starlette 1.10.0، Pydantic 2.14.2، httpx2 2.16.0، Uvicorn 0.54.0، Playwright 1.64.1 و Chromium 156.0.8078.4؛ جزئیات در `projects/66-ai-product-api/environment.json`.
- API با FastAPI TestClient درون‌فرایندی از مسیر ASGI آزموده شد؛ suite مرورگر HTML را از loopback محلی می‌خواند و پاسخ `/v1/assist` را intercept می‌کند. درخواست بیرونی صفر است و مدل زنده اجرا نشده است.
- `audit.py` هر دو suite را اجرا می‌کند و نتایج قطعی JSON می‌سازد؛ SHA-256 قبل از آزمون با manifest تطبیق داده می‌شود.

## نتایج آزمون پروژه

| دامنه | نتیجه | سناریوهای اصلی |
|---|---:|---|
| API و OpenAPI | ۱۲ از ۱۲ موفق | فهرست/مورد کاتالوگ، `404`, اعتبارسنجی `limit`, پاسخ فارسی/انگلیسی، ورودی خالی/طولانی/فیلد اضافه/locale نامعتبر، Problem Details و schema تولیدشده |
| رابط مرورگر | ۲ از ۲ موفق | حالت‌های آماده/بارگذاری/موفقیت، خطای safe، برچسب/اعلان وضعیت، رفتار متنی برای `<script>` ساختگی و عرض‌های ۳۲۰، ۳۹۰ و ۷۶۸ پیکسل |
| تماس بیرونی / مدل | ۰ / ۰ | تمام دادهٔ API از fixture محلی یا پاسخ browser-intercept است |

`results.json` تعداد caseها، hash fixture و محدودیت دامنه را ثبت می‌کند. آزمون‌ها در پیوست پروژه با دستور `python audit.py --output /tmp/ch66-results.json` بازتولید می‌شوند؛ برای suite مرورگر، وابستگی‌های ریشهٔ repository و Chromium لازم‌اند.

## گیت‌های کتاب و انتشار محلی

- `build_volume5.py` را اجرا کردیم: جلد پنجم ۵/۱۲ فصل دارد و ۴۰ بخش فصل ۶۶ را اضافه کرد؛ Service Worker از `fa-academy-v103` به `fa-academy-v104` رفت. اجرای دوباره تغییری نداد. مقایسهٔ پیش/پسِ `data.json`، `sw.js` و `volume-5-full-fa.md` برای idempotence موفق بود.
- `check_volume5.py` موفق شد: شمار بخش‌ها `[۲۶، ۳۴، ۳۹، ۴۱، ۴۰]`، شکل SVG و MathML دسترس‌پذیر، هشت پرسش و پاسخ‌نامهٔ دقیق، پیوست اجرایی همسان، Markdown، جلدها و ۶۶ مسیر آفلاین.
- پنج checker سراسری موفق شدند: جلد اول ۲۱ فصل/۲۳۶ بخش/۲۷ تصویر WebP؛ جلد دوم ۱۱/۱۰۱/۱۱؛ جلد سوم ۱۴/۱۴ فصل و ۲۶۵ بخش؛ جلد چهارم ۱۵/۱۵ و ۳۴۴ بخش؛ جلد پنجم ۵/۱۲ فصل. `pip check` نیز بدون وابستگی شکسته بود.
- پروژه‌های فصل‌های ۶۲، ۶۳، ۶۴، ۶۵ و ۶۶ به‌ترتیب ۹/۹، ۱۵/۱۵، ۲۰/۲۰، ۱۲/۱۲ آزمون unit، و ۱۲/۱۲ آزمون API به‌علاوهٔ ۲/۲ آزمون مرورگر را گذراندند؛ CLIها و hashهای fixture با فایل‌های نتیجه تطبیق داشتند.
- `test_volume5.py` در ۳۲۰، ۳۹۰، ۷۶۸ و ۱۴۴۰ پیکسل موفق شد: پنج فصل ۶۲–۶۶، ۶۶ مسیر آفلاین، MathML/SVG و پیوست اجرایی دقیق. لینک‌های منبع Markdown برای خواندن مستقل نسبی مانده‌اند؛ سازنده آن‌ها را فقط در HTML تزریق‌شده به ریشهٔ وب‌اپ به مسیر site-root تبدیل می‌کند.
- بررسی لینک‌های محلی READMEها، متن فصل، پاسخ‌نامه و گزارش موفق شد: به‌ترتیب ۲۱، ۲۱، ۱۸، ۴ و ۵ مقصد معتبر.
- پس از افزودن نتیجهٔ CI به همین گزارش، Service Worker برای تازه‌کردن نسخهٔ آفلاین به v105 رفت. `build_volume5.py` همچنان idempotent ماند، `check_volume5.py` موفق شد و `test_volume5.py` در ۳۲۰، ۳۹۰، ۷۶۸ و ۱۴۴۰ پیکسل، با ۶۶ مسیر آفلاین، دوباره گذشت.
- `test_mobile_layout.py` در ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل موفق شد و ۱٬۳۲۹ بخش پنج جلد را سنجید؛ پوشش شامل جلدها در حالت آنلاین/آفلاین، مسیرهای ۵۵–۶۶ آفلاین، ناوبری RTL، viewport قفل‌شده و تراز نثر بود. برای جلد پنجم، ۳۹۴ بند نثر، ۲۱۶ بند تورفته، ۶ MathML و ۵ کپشن بررسی شدند.
- این clone برای صرفه‌جویی در فایل‌ها sparse بود. پیش از checkerهای میان‌جلدی، ۵۳ تصویر ردیابی‌شده را فقط برای آزمون از C3 با hash یکسان موقتاً materialize کردیم و پس از آن پاک کردیم؛ هیچ تصویر مرجع یا فایل منتشرشده‌ای تغییر نکرد. چند 404 قدیمی و نامرتبط در log موبایل باقی ماند، اما assertionهای آزمون موفق بودند.

## انتشار، CI و بررسی Pages

- محتوای فصل ۶۶ با commit مستقل [`5dc36725c962ce05790cac1728df744d4c640e42`](https://github.com/mvbabababak-spec/fa-academy/commit/5dc36725c962ce05790cac1728df744d4c640e42) منتشر شد؛ اصلاح workflow نیز با commit [`9ed607a862b5b11042ad640394606e00fab28851`](https://github.com/mvbabababak-spec/fa-academy/commit/9ed607a862b5b11042ad640394606e00fab28851) و push عادی روی `gh-pages` رفت. پس از هر push، نوک `origin/gh-pages` با SHA محلی تطبیق داده شد؛ پس از commit اصلاحی، remote روی `9ed607a862b5b11042ad640394606e00fab28851` و worktree پاک بود.
- در اجرای نخست روی commit فصل، workflow جلد اول، [اجرا #۷۸](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42397848021)، در گام اجرای suiteهای پروژه شکست خورد: حلقهٔ عمومی آن پوشهٔ فصل ۶۶ را هم اجرا می‌کرد، اما وابستگی‌های پین‌شدهٔ FastAPI در manifest ریشه نیستند و suite فصل ۶۶ در محیط اختصاصی workflow جلد پنجم اجرا می‌شود. این ایرادِ واگذاری در CI بود، نه شکست آزمون‌های فصل. workflow جلد اول در commit اصلاحی [`9ed607a862b5b11042ad640394606e00fab28851`](https://github.com/mvbabababak-spec/fa-academy/commit/9ed607a862b5b11042ad640394606e00fab28851) اصلاح شد تا فصل ۶۶ را به workflow جلد پنجم واگذارد.
- نتیجهٔ هر دو commit به‌صورت مستقیم در GitHub Actions بررسی شد:

| گیت | commit محتوای فصل `5dc3672` | commit اصلاح واگذاری `9ed607a` |
|---|---|---|
| جلد اول | [اجرا #۷۸](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42397848021) ناموفق؛ اشکال واگذاری بالا | [اجرا #۷۹](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42398334975) موفق |
| جلد دوم | [اجرا #۶۱](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42397847999) موفق | [اجرا #۶۲](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42398334874) موفق |
| جلد سوم | [اجرا #۶۰](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42397847909) موفق | [اجرا #۶۱](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42398334910) موفق |
| جلد چهارم | [اجرا #۴۰](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42397848032) موفق | [اجرا #۴۱](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42398334936) موفق |
| جلد پنجم | [اجرا #۸](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42397848081) موفق | [اجرا #۹](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42398334882) موفق |
| Pages | [اجرا #۱۴۶](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42397847839) موفق | [اجرا #۱۴۷](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42398334965) موفق؛ artifact برابر ۱۳۳ مگابایت |

- Pages زنده در [نشانی انتشار](https://mvbabababak-spec.github.io/fa-academy/) بازبینی شد: فهرست زنده جلد پنجم ۵/۱۲ فصل و ۱۸۰ بخش دارد؛ فایل Markdown فصل ۶۶ و `results.json` از همان انتشار قابل دریافت‌اند. نتیجهٔ زندهٔ پروژه ۱۲/۱۲ آزمون API و ۲/۲ آزمون رابط را ثبت می‌کند؛ هیچ درخواست بیرونی یا اجرای مدل زنده‌ای گزارش نشده است. در commit اصلاح واگذاری، Service Worker نسخهٔ v104 و ۶۶ مسیر آفلاین تأیید شد.
- هشدارهای workflowها غیربلوکه‌کننده بودند: اقدام‌های `actions/checkout@v4`، `actions/setup-python@v5` و `actions/upload-artifact@v4` با زمان‌اجرای Node.js 24 اجرا شدند، و GitHub دربارهٔ مهاجرت برچسب `ubuntu-latest` به Ubuntu 26 اطلاع داد؛ همهٔ گیت‌های نهایی روی commit اصلاحی موفق شدند. این هشدارها به نتیجهٔ آزمون فصل مربوط نیستند.
- چون این گزارش در Service Worker پیش‌ذخیره می‌شود، در انتشار همین اصلاح گزارش نسخهٔ Service Worker از v104 به v105 افزایش می‌یابد تا نسخهٔ آفلاین گزارش هم تازه شود؛ فهرست ۶۶ مسیر آفلاین حفظ می‌شود.

## محدودیت‌ها

۱. fixture و همهٔ پاسخ‌ها اختراعی‌اند؛ هیچ کاربر، نهاد، منبع واقعی، مدل یا API بیرونی نمایندگی نمی‌شود.
۲. TestClient تعامل ASGI را درون‌فرایندی می‌سنجد، نه شبکه، TLS، latency، ظرفیت، proxy، استقرار یا رفتار native mobile.
۳. آزمون مرورگر پاسخ API را intercept می‌کند؛ E2E زنده نیست و تنها چند state، viewport و یک ورودی sentinel را می‌سنجد.
۴. تطبیق schema یا موفقیت آزمون، factuality، کیفیت، ایمنی، دسترس‌پذیریِ منطبق، privacy، امنیت یا انطباق حقوقی را اثبات نمی‌کند.
۵. احراز هویت/مجوز، محدودیت نرخ، telemetry، پاسخ به رخداد، پایش، runtime و CI/CD در این پروژه پیاده‌سازی نشده‌اند؛ مرز آن‌ها در فصل‌های ۶۷–۶۹ است.

برای تفسیر کامل، [فصل ۶۶](66-ai-product-api.md)، [پاسخ‌نامهٔ مستقل](../answers/66-ai-product-api-fa.md)، [README پروژه](../projects/66-ai-product-api/README.md)، [fixture](../projects/66-ai-product-api/synthetic_fixture.json) و [نتایج](../projects/66-ai-product-api/results.json) را ببینید. PDF و EPUB تولید یا آزموده نشده‌اند؛ محصول این milestone وب/PWA و Markdown است.
