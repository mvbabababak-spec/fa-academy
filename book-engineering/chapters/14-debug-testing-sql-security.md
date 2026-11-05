# فصل ۱۴ — عیب‌یابی، آزمون، طراحی نرم‌افزار، SQL و امنیت

**هنر و علم ساخت هوش | جلد اول | Babak & Ai**
**نسخه ۱.۰ · بررسی منابع: ۵ نوامبر ۲۰۲۶**

## ۱. از «اجرا شد» تا «درست و قابل نگهداری است»

برنامه‌ای که خطا نمی‌دهد الزاماً پاسخ درست نمی‌دهد. هدف این فصل تشخیص خطا، نوشتن آزمون تکرارپذیر، تفکیک مسئولیت‌ها، آشنایی با بانک داده رابطه‌ای و جلوگیری از اشتباهات امنیتی متداول است. **پیش‌نیاز:** توابع، استثنا، فایل و Git از فصل‌های ۱۱ تا ۱۳. **خروجی:** برنامه ثبت زمان مطالعه با SQLite و سه آزمون خودکار.

**نمونه:** اگر جمع ۳۰ و ۴۵ به جای ۷۵ برابر ۷۴ شود، اجرای بدون خطای برنامه نشانه درستی نیست. داده نمونه، خروجی مورد انتظار و آزمونی مستقل از پیاده‌سازی به ما در تشخیص کمک می‌کند. تست هیچ‌گاه همه حالت‌ها و تمام خطرهای امنیتی را ثابت نمی‌کند.

## ۲. عیب‌یابی نظام‌مند

**عیب‌یابی (Debugging)** را از مشاهده شروع کنید: انتظار چه بود، چه رخ داد، با کدام ورودی و نسخه؟ سپس نمونه‌ای کوچک و قابل تکرار بسازید، فرضیه‌ها را یکی‌یکی بررسی کنید و بعد از رفع مشکل آزمونی اضافه کنید که بازگشت همان خطا را آشکار کند. متغیرهای محیط و ورودی را ثبت کنید اما داده خصوصی و رمزها را ثبت نکنید.

**Traceback** مسیر فراخوانی و محل مشاهده خطا را نشان می‌دهد؛ آخرین سطر معمولاً نوع استثنا و پیام آن است، اما علت ریشه‌ای می‌تواند زودتر در مسیر باشد. خطای نحوی مانع تفسیر درست کد است؛ استثنای زمان اجرا مانند `ZeroDivisionError` در هنگام اجرا رخ می‌دهد؛ خطای منطقی ممکن است هیچ استثنایی ندهد [۱]. لاگ و breakpoint در debugger مکمل‌اند. `try/except` را فقط برای خطاهای قابل رسیدگی به‌کار ببرید، نه برای پنهان‌کردن خطا.

## ۳. آزمون خودکار

هر آزمون با چیدمان داده (**Arrange**)، اجرای رفتار (**Act**) و بررسی نتیجه (**Assert**) خوانا می‌شود. آزمون واحد واحدی کوچک را بررسی می‌کند؛ آزمون یکپارچه تعامل اجزا و آزمون سرتاسری جریان گسترده‌تر را می‌سنجد. مرزها، داده خالی، نوع نامعتبر، مسیر خطا و مقدار معمول را بپوشانید. نتایج آزمون‌ها باید مستقل از ترتیب اجرا باشند [۲].

در `unittest`, کلاس از `unittest.TestCase` ارث می‌برد؛ متدهای `test_...` کشف می‌شوند. `assertEqual` خروجی و `assertRaises` خطای مورد انتظار را بررسی می‌کند. هر تست پروژه در `setUp` پایگاه داده مجزا می‌سازد و در `tearDown` اتصال را می‌بندد. گذر آزمون‌ها برای داده‌های منتخب نشانه مفید است، نه اثبات نبود همه خطاها. پوشش خط کد نیز به‌تنهایی کیفیت بررسی نتیجه را نشان نمی‌دهد.

![شکل ۱۴-۱: ورودی اعتبارسنجی‌شده به تابع و پرس‌وجوی پارامتری می‌رود و خروجی با آزمون بررسی می‌شود.](assets/images/babak-ai/ch14-tests.webp)

**شکل ۱۴-۱ — مسیر آموزشی و مرز اعتماد.** پارامتری‌کردن به‌تنهایی مجوز دسترسی یا امنیت کامل را تضمین نمی‌کند.

## ۴. طراحی و بازبینی

وظایف را جدا کنید: یک تابع اعتبارسنجی و درج می‌کند، تابع دیگر پرس‌وجو را انجام می‌دهد، و نمایش خروجی در `main` است. نام روشن، ورودی و خروجی مشخص و توابع کوچک آزمون و تغییر را آسان می‌کنند. از تکرار بی‌دلیل بپرهیزید اما تجرید پیچیده را زودهنگام تحمیل نکنید. بازبینی کد شامل خوانایی، درستی، خطاها، کارایی، امنیت و آزمایش است.

برای تغییرات Git، `git diff` را ببینید، فایل‌های مرتبط را stage کنید و آزمون‌ها را قبل از commit اجرا کنید. در پروژه تیمی بازبینی مستقل و اجرای خودکار آزمون‌ها در CI کمک می‌کند، ولی CI جای تصمیم مهندسی را نمی‌گیرد.

## ۵. داده رابطه‌ای و SQL

**پایگاه داده رابطه‌ای (Relational Database)** داده را در جدول‌هایی از سطر و ستون سازمان می‌دهد. **SQL** زبان تعریف و پرس‌وجوی داده است. SQLite یک موتور تعبیه‌شده است؛ در این پروژه `:memory:` یعنی داده فقط در حافظه اتصال است و پس از بسته‌شدن از بین می‌رود، نه ذخیره دائمی.

در مثال، جدول `sessions` دو ستون `topic` و `minutes` دارد. `CREATE TABLE` ساختار را ایجاد و `INSERT` سطر را درج می‌کند؛ `SELECT`، `WHERE` و `SUM` انتخاب، فیلتر و جمع را انجام می‌دهند. `COALESCE(SUM(minutes), 0)` برای مجموعه بدون سطر صفر می‌دهد. در سیستم واقعی برای موجودیت‌ها و روابط مناسب کلید، محدودیت، نسخه‌بندی schema، پشتیبان‌گیری و سیاست دسترسی تعیین کنید.

## ۶. پارامتر، تراکنش و امنیت اولیه

هرگز مقدار نامطمئن را با الحاق رشته داخل SQL قرار ندهید. در SQLite برای **مقدار داده** از `?` و دنباله پارامترها استفاده کنید؛ موتور مقدار را داده در نظر می‌گیرد، نه بخشی از دستور [۳، ۴]. جای‌نگهدار برای نام جدول یا ستون نیست: ساختار پویا را از گزینه‌های ثابت و مجاز برنامه انتخاب کنید. اعتبارسنجی، کمترین سطح دسترسی و بررسی مجوز کاربر همچنان لازم‌اند [۴].

`with db:` تراکنش را در صورت موفقیت commit و در صورت خطا rollback می‌کند؛ **اتصال را نمی‌بندد**، به همین دلیل برنامه در `finally` آن را می‌بندد [۳]. این مثال فقط درج ساده را آموزش می‌دهد، نه طراحی همزمانی یا امنیت production. رمز و کلید را در کد، Git و log نگذارید؛ از مدیریت امن اسرار، احراز هویت، مجوز و محافظت از داده استفاده کنید. روی ورودی نامطمئن `eval` یا دستور shell نسازید.

## ۷. پروژه: دفتر مطالعه در SQLite

دو فایل زیر را کنار هم ذخیره کنید. این کد فقط از کتابخانه استاندارد استفاده می‌کند و فایل یا شبکه را تغییر نمی‌دهد. ورودی موضوع خالی، عدد منفی، بیش از ۱۴۴۰ و `True` را رد می‌کند. محدودیت ۱۴۴۰ قرارداد آموزشی است، نه ویژگی ذاتی SQLite.

**`study_db.py`:**
```python
"""Small in-memory SQLite study log; no external services or files."""
import sqlite3


def create_database():
    db = sqlite3.connect(':memory:')
    db.execute('CREATE TABLE sessions (topic TEXT NOT NULL, minutes INTEGER NOT NULL CHECK(minutes >= 0))')
    return db


def add_session(db, topic, minutes):
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError('topic must be non-empty')
    if type(minutes) is not int or not 0 <= minutes <= 1440:
        raise ValueError('minutes must be an integer from 0 to 1440')
    with db:
        db.execute('INSERT INTO sessions (topic, minutes) VALUES (?, ?)', (topic.strip(), minutes))


def minutes_for(db, topic):
    row = db.execute('SELECT COALESCE(SUM(minutes), 0) FROM sessions WHERE topic = ?', (topic,)).fetchone()
    return row[0]


def main():
    db = create_database()
    try:
        add_session(db, 'python', 30)
        add_session(db, 'python', 45)
        add_session(db, 'math', 60)
        print('python_minutes=', minutes_for(db, 'python'))
        print('missing_minutes=', minutes_for(db, 'missing'))
    finally:
        db.close()


if __name__ == '__main__':
    main()
```

اتصال حافظه‌ای در هر اجرا تازه است. `topic.strip()` فضاهای ابتدا و انتهای متن را در درج حذف می‌کند؛ جست‌وجو در این نمونه مقدار را بدون پاک‌سازی اضافی استفاده می‌کند. در سامانه واقعی این قرارداد باید برای هر دو مسیر دقیق طراحی شود. SQLite بررسی `CHECK` منفی را هم انجام می‌دهد اما سایر اعتبارسنجی‌های برنامه را جایگزین نمی‌کند.

## ۸. آزمون و اجرای پروژه

**`test_study_db.py`:**
```python
import unittest
from study_db import create_database, add_session, minutes_for


class StudyTests(unittest.TestCase):
    def setUp(self):
        self.db = create_database()

    def tearDown(self):
        self.db.close()

    def test_sum_and_missing(self):
        add_session(self.db, 'python', 30)
        add_session(self.db, 'python', 45)
        self.assertEqual(minutes_for(self.db, 'python'), 75)
        self.assertEqual(minutes_for(self.db, 'math'), 0)

    def test_invalid_values(self):
        for topic, minutes in [('', 1), ('x', -1), ('x', True), ('x', 1441)]:
            with self.subTest(topic=topic, minutes=minutes):
                with self.assertRaises(ValueError):
                    add_session(self.db, topic, minutes)

    def test_untrusted_value_is_literal(self):
        add_session(self.db, 'python', 30)
        self.assertEqual(minutes_for(self.db, "python' OR 1=1 --"), 0)
        self.assertEqual(minutes_for(self.db, 'python'), 30)


if __name__ == '__main__':
    unittest.main()
```

در پوشه پروژه `python study_db.py` و `python -m unittest -v` را اجرا کنید. در محیط آزمون Python 3.13.16 خروجی برنامه `python_minutes= 75` و `missing_minutes= 0` و گزارش آزمون شامل `Ran 3 tests` و `OK` بود. آزمون ورودی ظاهراً SQL را **به‌صورت مقدار واقعی** به تابع می‌دهد و انتظار صفر دارد؛ این یک بررسی محدود است و جای ممیزی امنیتی را نمی‌گیرد.

**عیب‌یابی:** `ModuleNotFoundError` برای `study_db` معمولاً یعنی آزمون را بیرون پوشه فایل‌ها اجرا کرده‌اید؛ وارد همان پوشه شوید یا از دستور discover مناسب استفاده کنید. `sqlite3` بخشی از کتابخانه استاندارد Python است، اما در برخی توزیع‌های سفارشی ممکن است ماژول ساخته نشده باشد. خطای تست را با مقدار مورد انتظار و traceback مقایسه کنید، نه اینکه آزمون را برای سبزشدن بی‌دلیل ضعیف کنید.

## ۹. تمرین، ارزیابی و توسعه

**پرسش:** ۱) تفاوت خطای منطقی و استثنا چیست؟ ۲) سه گام Arrange/Act/Assert کدام‌اند؟ ۳) آیا test pass اثبات امنیت است؟ ۴) `WHERE` چه می‌کند؟ ۵) پارامتر `?` برای چه استفاده می‌شود؟ ۶) آیا پارامتر جای نام جدول را می‌گیرد؟ ۷) آیا `with db` اتصال SQLite را می‌بندد؟ ۸) چرا رمز را نباید log کرد؟

**تمرین:** جمع ۳۰، ۴۵ و ۶۰ برابر ۱۳۵ است؛ مجموع موضوع python در برنامه ۷۵ است، نه ۱۳۵. تست ورودی مرزی صفر و ۱۴۴۰ را اضافه کنید و نتایج را بررسی کنید. تست درج موضوع فارسی بنویسید. **مینی‌پروژه:** تعداد جلسه‌ها را با پرس‌وجوی پارامتری به‌دست آورید و آزمون صفر و چند سطر بنویسید؛ پیش از تغییر کد خروجی مورد انتظار را مشخص کنید.

**قبولی:** دست‌کم ۷ پاسخ صحیح، اجرای سه آزمون موجود و دو آزمون جدید. پاسخ: ۱) خروجی غلط بدون الزام استثنا/خطای گزارش‌شده در اجرا؛ ۲) آماده‌سازی، اجرا، بررسی؛ ۳) خیر؛ ۴) فیلتر؛ ۵) اتصال مقدار؛ ۶) خیر؛ ۷) خیر؛ ۸) خطر افشا.

## ۱۰. منابع و واژه‌نامه

**مرور: ۵ نوامبر ۲۰۲۶.** پروژه در Python 3.13.16 با SQLite حافظه‌ای آزموده شد؛ اتصال شبکه، امنیت production و پایگاه داده چندکاربره آزموده نشدند. فصل ۱۵ ابزارهای تحلیل داده و نمودار را معرفی می‌کند.

Debugging، Traceback، Unit Test، Integration Test، Regression، SQL، Database، Transaction، Parameterized Query، Least Privilege.

**منابع؛ مراجعه ۵ نوامبر ۲۰۲۶:** [۱] Python Software Foundation، «Errors and Exceptions»، مستندات Python 3.13، [منبع](https://docs.python.org/3.13/tutorial/errors.html). [۲] Python Software Foundation، «unittest»، مستندات 3.13، [منبع](https://docs.python.org/3.13/library/unittest.html). [۳] Python Software Foundation، «sqlite3»، مستندات 3.13، [منبع](https://docs.python.org/3.13/library/sqlite3.html). [۴] OWASP، «SQL Injection Prevention Cheat Sheet»، تاریخ صفحه نامشخص، [منبع](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html).

## پیوست تکمیلی: آموزش، پروژه و آزمون‌های بیشتر

### فصل ۱۴ — عیب‌یابی، آزمون، طراحی نرم‌افزار، SQL و امنیت پایه

**هنر و علم ساخت هوش | جلد اول | Babak & Ai**  
**بررسی منابع: ۵ نوامبر ۲۰۲۶**

### ۱. از «کار می‌کند» تا «می‌توان به آن اعتماد کرد»

یک برنامه ممکن است روی داده معمولی کار کند اما برای ورودی خالی، خطای فایل یا داده‌ای نامعمول شکست بخورد. مهندسی نرم‌افزار یعنی مشخص‌کردن انتظار، آزمایش منظم و محدودکردن پیامد خطا؛ نه صرفاً نوشتن خروجی نمونه. در این فصل یک سامانه کوچک ثبت مطالعه می‌سازیم، آن را با SQLite می‌آزماییم و با اصول امنیتی آشنا می‌شویم.

**پیش‌نیاز:** توابع، استثنا و محیط فصل‌های ۱۱ تا ۱۳. **هدف:** خواندن traceback، طراحی تست و مرزهای ورودی، نوشتن SQL پارامتری و درک محدودیت امنیت. نمونه از کتابخانه استاندارد Python استفاده می‌کند.

### ۲. عیب‌یابی گام‌به‌گام

**عیب‌یابی (Debugging)** روند پیدا کردن علت رفتار غیرمنتظره است. ابتدا رفتار مورد انتظار و رفتار واقعی را دقیق بنویسید؛ سپس کوچک‌ترین ورودی بازتولیدکننده را بیابید، نسخه و محیط را ثبت کنید، و فرضیه‌ها را یکی‌یکی بیازمایید. تفاوت بین نشانه و علت مهم است: پیام نبود فایل ممکن است ناشی از پوشه کاری اشتباه باشد، نه محتوای فایل.

Traceback معمولاً زنجیره فراخوانی‌ها و در پایان نوع و پیام استثنا را نشان می‌دهد. از آخر به نوع خطا نگاه کنید، سپس سطرهای برنامه خود را دنبال کنید. `ValueError` معمولاً نشان‌دهنده مقدار نامناسب و `TypeError` ناسازگاری نوع عملیات است؛ همیشه زمینه را بخوانید. قبل از تغییر کد، ورودی‌ها را مشاهده کنید و بعد از اصلاح، آزمون بازگشتی برای جلوگیری از تکرار اضافه کنید.

`logging` برای ثبت رویداد با سطح‌هایی مثل INFO و ERROR مناسب است [۱]. گزارش نباید token، رمز، داده شخصی یا کل payload حساس را در خود داشته باشد. چاپ موقت کمک می‌کند اما لاگ کنترل‌شده با دسترسی و نگهداری مناسب برای پروژه واقعی بهتر است.

### ۳. طراحی و جداسازی مسئولیت

تابعی که ورودی را بررسی، SQL را اجرا، HTML را تولید و شبکه را مدیریت می‌کند دشوارتر آزموده می‌شود. کارها را با رابط مشخص جدا کنید: اعتبارسنجی، عملیات داده و نمایش. جداسازی زیاد هم پیچیدگی می‌آورد؛ بر اساس نیاز، سادگی و خوانایی تصمیم بگیرید.

**قرارداد** مشخص می‌کند چه ورودی‌هایی پذیرفته و چه خروجی یا خطایی انتظار می‌رود. در پروژه، `minutes` عدد صحیح ۰ تا ۱۴۴۰ و موضوع رشته غیرخالی است؛ `True` عمداً رد می‌شود. این دامنه یک انتخاب آموزشی است، نه تعریف همگانی جلسه مطالعه. ورودی نامعتبر با `ValueError` رد می‌شود.

![شکل ۱۴-۱: چرخه طراحی، آزمون، مشاهده و اصلاح.](assets/images/babak-ai/ch14-testing.webp)

**شکل ۱۴-۱ — چرخه بهبود.** عبور از آزمون فقط آنچه آزموده شده را پوشش می‌دهد، نه همه رفتارهای ممکن.

### ۴. آزمون واحد و یکپارچگی

**آزمون واحد (Unit Test)** رفتاری کوچک را جداگانه بررسی می‌کند. **آزمون یکپارچگی (Integration Test)** همکاری اجزا را می‌سنجد؛ تست پایگاه‌داده واقعی در حافظه در پروژه ما نیز جنبه یکپارچگی دارد. آزمون سر تا سر مسیر گسترده‌تری از کاربر تا نتیجه را بررسی می‌کند. مرزها بسته به پروژه تغییر می‌کنند.

هر آزمون با آماده‌سازی، اجرا و مقایسه نتیجه مورد انتظار ساخته می‌شود. `unittest.TestCase`، `setUp` و `tearDown` به ساخت آزمون‌های مستقل کمک می‌کنند [۲]. افزون بر حالت عادی، خالی، صفر، مرز بالا، خارج محدوده، نوع اشتباه و متن غیرمعمول را بررسی کنید. آزمون موفق اثبات نبود همه باگ‌ها یا امنیت کامل نیست.

### ۵. SQL و داده رابطه‌ای

در یک پایگاه رابطه‌ای داده‌ها به شکل جدول، ستون و سطر سازمان می‌یابند. **SQL** زبان رایج تعریف و پرس‌وجوی داده است؛ جزئیات میان موتورهای مختلف تفاوت دارند. SQLite کتابخانه‌ای سبک است که برای استفاده معمول به فرایند سرور جداگانه نیاز ندارد [۳]. `:memory:` یک پایگاه موقت در حافظه همان اتصال می‌سازد؛ با بستن آن داده از دست می‌رود.

`CREATE TABLE` جدول می‌سازد؛ `INSERT` سطر اضافه می‌کند؛ `SELECT` اطلاعات می‌خواند و `WHERE` فیلتر می‌کند. `SUM` مجموع را برمی‌گرداند؛ در نبود سطر ممکن است NULL باشد، پس در مثال `COALESCE(..., 0)` صفر می‌دهد. `commit` تراکنش تغییرات را ثبت می‌کند؛ برای داده واقعی باید تراکنش، خطا و بازیابی را متناسب با محیط طراحی کرد.

### ۶. تزریق و پارامترگذاری

داده کاربر را با چسباندن رشته داخل SQL قرار ندهید. در SQLite از placeholder `?` و پارامتر جداگانه استفاده کنید: `execute('SELECT ... WHERE topic = ?', (topic,))`. متن ورودی به‌عنوان داده به موتور داده می‌شود، نه بخشی از دستور SQL [۳، ۴]. این حفاظت برای مقدارهاست؛ نام جدول/ستون را نمی‌توان با همین placeholder دلخواه کرد و اگر واقعاً پویا باشند باید از فهرست مجاز دقیق انتخاب شوند.

اعتبارسنجی نوع و محدوده مفید است، اما جایگزین پارامترگذاری نیست. امنیت نیازمند لایه‌های دیگر از جمله کنترل دسترسی، حداقل سطح مجوز، مدیریت امن کلیدها، به‌روزرسانی و بررسی وابستگی‌هاست. مثال حافظه‌ای ما احراز هویت، مجوز، چندکاربری، پشتیبان یا محصول آماده تولید نیست.

### ۷. پروژه: ثبت جلسه و پرس‌وجوی امن

`study_db.py` را بسازید و اجرا کنید. داده‌ها ساختگی و پایگاه موقتی‌اند. خروجی مورد انتظار `python_minutes= 75` و `unknown_minutes= 0` است.

```python
"""A small in-memory study tracker; no network or persistent files."""
import sqlite3


def setup(connection):
    connection.execute('CREATE TABLE sessions (topic TEXT NOT NULL, minutes INTEGER NOT NULL)')


def add_session(connection, topic, minutes):
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError('topic must be a non-empty string')
    if type(minutes) is not int or not 0 <= minutes <= 1440:
        raise ValueError('minutes must be an integer between 0 and 1440')
    connection.execute('INSERT INTO sessions (topic, minutes) VALUES (?, ?)',
                       (topic.strip(), minutes))
    connection.commit()


def total_for(connection, topic):
    row = connection.execute('SELECT COALESCE(SUM(minutes), 0) FROM sessions WHERE topic = ?',
                             (topic,)).fetchone()
    return row[0]


def main():
    connection = sqlite3.connect(':memory:')
    try:
        setup(connection)
        add_session(connection, 'python', 30)
        add_session(connection, 'python', 45)
        add_session(connection, 'math', 20)
        print('python_minutes=', total_for(connection, 'python'))
        print('unknown_minutes=', total_for(connection, 'unknown'))
    finally:
        connection.close()


if __name__ == '__main__':
    main()
```

دو جلسه Python برابر ۳۰ و ۴۵ دقیقه و جلسه math برابر ۲۰ دقیقه درج می‌شوند. `total_for` فقط موضوع مشخص را جمع می‌کند. اتصال در `finally` بسته می‌شود. هر insert در این مثال جداگانه commit می‌شود؛ برای چند عملیات وابسته در محصول واقعی باید مرز تراکنش و rollback را طراحی کنید.

### ۸. پروژه: مجموعه آزمون

فایل `test_study_db.py` را کنار فایل قبلی ذخیره کنید. دستور: `python -m unittest -v test_study_db` از داخل پوشه؛ یا `python -m unittest discover -s book-engineering/projects/14-testing-sql -v` از ریشه مخزن. سه تست مستقل اجرا می‌شود:

```python
import sqlite3
import unittest
from study_db import setup, add_session, total_for


class StudyDBTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        setup(self.db)

    def tearDown(self):
        self.db.close()

    def test_sum_and_empty(self):
        add_session(self.db, 'python', 30)
        add_session(self.db, 'python', 45)
        self.assertEqual(total_for(self.db, 'python'), 75)
        self.assertEqual(total_for(self.db, 'math'), 0)

    def test_boundaries_and_invalid(self):
        for value in (0, 1440):
            add_session(self.db, 'x', value)
        for value in (-1, 1441, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                add_session(self.db, 'x', value)
        with self.assertRaises(ValueError):
            add_session(self.db, ' ', 10)

    def test_parameter_is_data(self):
        add_session(self.db, 'python', 30)
        self.assertEqual(total_for(self.db, "python' OR 1=1 --"), 0)
        self.assertEqual(total_for(self.db, 'python'), 30)


if __name__ == '__main__':
    unittest.main()
```

تست اول جمع و حالت بدون سطر، دوم مرزها و داده نامعتبر و سوم رفتار متن شبیه تزریق را می‌سنجد. تست سوم یک مثال محدود است، نه ممیزی امنیت جامع. اجرا در Python 3.13.16: `Ran 3 tests ... OK`. اگر import خطا داد، پوشه و دستور اجرا را بررسی کنید.

### ۹. تمرین و ارزیابی

**پرسش‌ها:** ۱) تفاوت نشانه و علت چیست؟ ۲) چرا نمونه حداقلی مفید است؟ ۳) unit و integration چه تفاوتی دارند؟ ۴) چرا تست صفر و حد بالا مهم است؟ ۵) SQL پارامتری چه چیزی را جدا می‌کند؟ ۶) آیا placeholder نام جدول را انتخاب می‌کند؟ ۷) `:memory:` چقدر پایدار است؟ ۸) آیا آزمون موفق امنیت کامل را ثابت می‌کند؟

**تمرین:** تابعی برای شمارش تعداد جلسات یک موضوع با پارامتر SQL بنویسید و برای موضوع نبودنی و موجود تست اضافه کنید. **محاسبه:** سه جلسه ۳۰، ۴۵ و ۲۰ دقیقه مجموعاً ۹۵ دقیقه‌اند؛ مجموع Python در مثال ۷۵ دقیقه است. **مینی‌پروژه:** قرارداد، دو تست مرزی، آزمون موضوع ناموجود، لاگ بدون اطلاعات شخصی و مستندات اجرا تهیه کنید. برای قبولی دست‌کم ۷ پاسخ صحیح و اجرای موفق آزمون‌ها لازم است.

پاسخ‌ها: ۱) مشاهده/منشأ؛ ۲) کاهش عوامل؛ ۳) جزء/همکاری اجزا؛ ۴) کشف خطای مرزی؛ ۵) ساختار و داده؛ ۶) خیر؛ ۷) عمر اتصال؛ ۸) خیر.

### ۱۰. منابع و ادامه مسیر

**واژه‌ها:** Debugging، Traceback، Logging، Unit Test، Integration Test، Contract، SQL، Table، Query، Transaction، Parameterized Query، Injection. فصل ۱۵ ابزارهای داده NumPy، Pandas، Matplotlib و Jupyter را آموزش می‌دهد.

**منابع اولیه؛ بررسی ۵ نوامبر ۲۰۲۶:** [۱] Python Software Foundation، [logging](https://docs.python.org/3.13/library/logging.html)، مستندات Python 3.13. [۲] Python Software Foundation، [unittest](https://docs.python.org/3.13/library/unittest.html). [۳] Python Software Foundation، [sqlite3](https://docs.python.org/3.13/library/sqlite3.html). [۴] OWASP، [Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html)، تاریخ صفحه متغیر.

