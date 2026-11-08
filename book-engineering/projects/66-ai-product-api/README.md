# آزمایشگاه قرارداد API و رابط ساختگی — فصل ۶۶

این پروژه یک API نمونه با FastAPI می‌سازد تا قرارداد داده، اعتبارسنجی، status code، OpenAPI و رفتار رابط از یک fixture بازتولیدپذیر آزموده شوند. هیچ مدل زنده، حساب کاربری، دادهٔ شخصی، پایگاه داده، شبکهٔ بیرونی یا سامانهٔ حقیقی در کار نیست؛ `example.invalid` عمداً دامنهٔ رزروشده و غیرقابل‌استفاده به‌عنوان منبع واقعی است.

## ساختار

- `app.py`: سرویس FastAPI با `GET /v1/catalog`، `GET /v1/catalog/items/{item_id}`، `POST /v1/assist` و رابط `GET /demo`.
- `demo.html`: رابط فارسی و راست‌به‌چپ با حالت‌های اولیه، بارگذاری، پاسخ و خطا؛ دادهٔ پاسخ با `textContent` درج می‌شود، نه HTML اجرایی.
- `synthetic_fixture.json`: یک رکورد ساختگی و پاسخ‌های ثابت فارسی/انگلیسی.
- `fixture_manifest.json`: شناسه، منشأ و SHA-256 بایت‌های fixture.
- `test_api.py`: آزمون‌های قراردادی با TestClient درون‌فرایندی.
- `test_frontend.py`: آزمون مرورگر روی viewportهای کوچک؛ پاسخ API به‌طور صریح intercept می‌شود.
- `audit.py`: اجرای دو suite و ساخت خروجی JSON قطعی.
- `results.json`, `environment.json`: نتیجهٔ ثبت‌شده و محیط اجرای ممیزی.

## محیط و اجرا

محیط مرجع: CPython 3.13.16 روی Linux؛ نسخه‌های مستقیم FastAPI، Starlette، Pydantic، `httpx2` و Uvicorn در `requirements.txt` pin شده‌اند. `httpx2` backend ترجیحی TestClient در نسخهٔ آزموده‌شدهٔ Starlette است. Playwright از `requirements.txt` ریشهٔ repository می‌آید و Chromium در ممیزی مرورگر نصب می‌شود.

از ریشهٔ repository:

```bash
python -m pip install -r requirements.txt
python -m pip install -r book-engineering/projects/66-ai-product-api/requirements.txt
cd book-engineering/projects/66-ai-product-api
python audit.py --output /tmp/ch66-results.json
cmp /tmp/ch66-results.json results.json
uvicorn app:app --host 127.0.0.1 --port 8000
```

پس از اجرای Uvicorn، رابط در `http://127.0.0.1:8000/demo` و قرارداد ماشین‌خوان در `/openapi.json` دیده می‌شود. سرویس را فقط برای دموی محلی اجرا کنید؛ این کد مجوز یا تنظیمات آمادهٔ انتشار ندارد. برای ساخت محیط مجازی، پیش از نصب `python -m venv .venv` را اجرا و محیط را فعال کنید؛ در Windows فرمان فعال‌سازی متفاوت است.

## قرارداد کوتاه

درخواست `POST /v1/assist` یک شیء JSON با `question` غیرخالی و حداکثر ۳۰۰ نویسه و `locale` برابر `fa` یا `en` می‌پذیرد. فیلد ناشناخته رد می‌شود. پاسخ موفق status `200` و فیلدهای `contract_version`, `request_id`, `status`, `answer` و `sources` دارد. خطاها با status مناسب و media type `application/problem+json` برمی‌گردند؛ ورودی ردشده یا جزئیات داخلی به رابط echo نمی‌شود.

## نتایج و محدودیت

`results.json` از اجرای واقعی `audit.py` ساخته می‌شود و هم آزمون API و هم آزمون مرورگر را گزارش می‌کند. suite مرورگر پاسخ API را intercept می‌کند: UI و حالت‌های بارگذاری/موفقیت/خطا را می‌سنجد، نه یک استقرار end-to-end یا برنامهٔ native موبایل را. نسخه‌های مستقیم pin شده‌اند؛ برای انتشار واقعی باید کل dependency graph، lockfile، تنظیمات محیط، پایگاه داده و threat model جداگانه بازبینی شوند.

این آزمایشگاه قرارداد و چند حالت رابط را می‌سنجد، نه کیفیت یا حقیقت پاسخ، عملکرد مدل، امنیت محصول، latency، conformance دسترس‌پذیری، انطباق حقوقی، استقرار یا تجربهٔ کاربر واقعی. احراز هویت و مجوز، محدودیت نرخ، privacy، ثبت رخداد و پایش در فصل ۶۸؛ runtime در فصل ۶۷؛ و CI/CD و استقرار در فصل ۶۹ بررسی می‌شوند.
