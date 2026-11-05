# فصل ۱۵ — NumPy، Pandas، Matplotlib و Jupyter

**هنر و علم ساخت هوش | جلد اول | Babak & Ai**
**نسخه کاری RC · تاریخ مراجعه به منابع: ۵ نوامبر ۲۰۲۶**

## ۱. از جدول کوچک تا تحلیل داده

داده به‌تنهایی پاسخ نیست: باید منشأ، واحد، خطا، داده گمشده، سؤال و محدودیت آن را بشناسیم. در این فصل آرایه عددی NumPy، جدول Pandas، تصویرسازی Matplotlib و محیط تعاملی Jupyter را می‌آموزیم. **پیش‌نیاز:** Python، تابع، فایل و محیط مجازی. **پروژه:** تحلیل چهار سطر ساختگی مطالعه، با گزارش رکورد ناقص و نمودار WebP.

این داده آموزشی ساختگی است، نه نمونه‌ای نماینده از رفتار انسان‌ها. تحلیل توصیفی آن رابطه علّی یا کیفیت یادگیری را نشان نمی‌دهد. در کار واقعی، رضایت، حریم خصوصی، مجوز داده، واحد اندازه‌گیری و روش نمونه‌گیری اهمیت دارند.

**نسخهٔ پایه — قرارداد پروژه:** قرارداد اصلی `analyze` در `projects/15-data-analysis` سه مقدار `(missing, totals, mean)` برمی‌گرداند. نسخهٔ بازنویسی‌شده در پیوست از قرارداد متفاوت `(clean, totals, missing)` استفاده می‌کند؛ دو فایل هم‌نام را در پوشه‌های مستقل اجرا کنید.

## ۲. NumPy: آرایه و شکل

**NumPy** ابزار محاسبات عددی و `ndarray` ساختار اصلی آن است [۱]. آرایه معمولاً عناصر هم‌نوع با `dtype` مشخص دارد؛ `shape` اندازه هر بُعد است. برخلاف لیست Python، جمع دو آرایه سازگار معمولاً عضو به عضو انجام می‌شود.

```python
import numpy as np
a = np.array([30, 45, 60])
print(a.shape)        # (3,)
print(a + 10)         # [40 55 70]
print(a.mean())       # 45.0
```

اندیس از صفر شروع می‌شود. برش پایه اغلب **view** است، پس تغییرش ممکن است آرایه اصلی را هم تغییر دهد؛ `copy()` نسخه مستقل می‌سازد. **Broadcasting** در شکل‌های سازگار امکان عملیات بین آرایه‌ها با شکل متفاوت می‌دهد؛ سازگاری را بررسی کنید، چون نتیجه‌ای با شکل ناخواسته ممکن است بدون خطا تولید شود. `dtype`، سرریز اعداد صحیح و خطای گردکردن اعشاری در محاسبات بزرگ اهمیت دارند.

## ۳. Pandas: جدول و انتخاب

**DataFrame** جدولی دارای ردیف و ستون و **Series** معمولاً نمایش یک ستون است [۲]. `pd.read_csv` CSV را می‌خواند؛ `head()`, `info()` و `dtypes` برای بازبینی اولیه مفیدند. نام ستون، واحد، نوع، داده‌های تکراری و گمشده را بررسی کنید. CSV نامطمئن ممکن است حجیم باشد؛ داده و خروجی را پیش از اشتراک‌گذاری بازبینی کنید.

```python
import pandas as pd
df = pd.DataFrame({'topic': ['python', 'math'], 'minutes': [30, 60]})
print(df[df['minutes'] >= 45])
```

`groupby('topic')['minutes'].sum()` گروه‌ها را جدا، جمع هر گروه را محاسبه و نتیجه‌ها را ترکیب می‌کند [۳]. `size` تعداد سطرها را می‌شمارد، در حالی که `count` مقادیر غیرگمشده را می‌شمارد. ترتیب و رفتار مقادیر گمشده را با نیاز و نسخه کتابخانه بررسی کنید.

## ۴. داده ناقص و تصمیم تحلیلی

در داده پروژه، یک سطر math دقیقه ندارد. نبود مقدار به معنای صفر نیست. برای این تمرین **حذف سطرهای ناقص** را انتخاب و تعداد آن‌ها را گزارش می‌کنیم؛ ممکن است در پژوهش واقعی این کار سوگیری ایجاد کند. روش جایگزین مانند تکمیل مقدار یا جمع‌آوری مجدد باید بر اساس زمینه، علت مفقودشدن و مستندسازی انتخاب شود. هرگز فرض نکنید یک روش برای همه داده‌ها صحیح است.

پس از حذف یک سطر، سه مقدار ۳۰، ۴۵، ۶۰ می‌ماند. مجموع ۱۳۵ دقیقه و میانگین ۴۵ دقیقه است؛ جمع python برابر ۷۵ و math برابر ۶۰ است. این میانگین روی **جلسه‌های کامل** محاسبه شده، نه روی همه چهار سطر و نه میانگین روزانه یا فردی.

## ۵. Matplotlib: نمودار مسئولانه

`plt.subplots()` یک **Figure** و ناحیه رسم **Axes** می‌سازد؛ `ax.bar` نمودار ستونی و `set` عنوان و برچسب محور را تنظیم می‌کند [۴]. محور و واحد را روشن بنویسید و نمودار مناسب سؤال انتخاب کنید؛ تفاوت مقیاس، حذف داده و تعداد نمونه می‌تواند خواننده را گمراه کند. نمودار ستونی با محور عمودی از صفر برای مقایسه اندازه‌ها معمولاً خواناتر است.

![شکل ۱۵-۱: مجموع دقیقه‌های معتبر برای python برابر ۷۵ و برای math برابر ۶۰ است.](assets/images/babak-ai/ch15-study-chart.webp)

**شکل ۱۵-۱ — داده ساختگی پروژه.** سطر بدون دقیقه حذف شده؛ شکل توسط کد پروژه تولید شده است. این نمودار اختلاف در مجموع جلسه‌های مشاهده‌شده را نشان می‌دهد، نه تفاوت مهارت یا علت.

## ۶. Jupyter: سلول، kernel و تکرارپذیری

Jupyter Notebook سندی تعاملی با سلول‌های کد و متن است؛ کد در فرایند **kernel** اجرا می‌شود [۵]. مثلاً یک سلول واردکردن کتابخانه‌ها و سلول بعدی تعریف داده را در خود جای می‌دهد. خروجی یک سلول می‌تواند به متغیری وابسته باشد که قبلاً در سلولی دیگر ساخته شده است، حتی اگر ترتیب ظاهری سلول‌ها فرق کند. برای بازتولید، kernel را restart و همه سلول‌ها را از ابتدا به ترتیب اجرا کنید.

نسخه Python، کتابخانه‌ها، ورودی و دستور اجرا را یادداشت کنید. پیش از اشتراک‌گذاری، خروجی‌ها را برای داده شخصی و اسرار بررسی کنید؛ notebook ناشناس می‌تواند کد مخرب داشته باشد و نباید بی‌بررسی اجرا شود. پروژه زیر اسکریپت است؛ اجرای رابط Jupyter در این محیط آزمون نشده است.

## ۷. آماده‌سازی پروژه

در پوشه‌ای تمرینی، محیط مجازی فصل ۱۳ را بسازید و فعال کنید. سپس در همان محیط، از منابع بسته معتبر و با توجه به سازگاری سیستم نصب کنید:

```text
python -m pip install numpy pandas matplotlib
```

نصب به شبکه نیاز دارد؛ دستور فوق برای نسخه‌ها محدودیت قرار نمی‌دهد. برای بازتولید، نسخه‌های آزمایش‌شده را ثبت و سازگاری را در سیستم خود بررسی کنید: Python 3.13.16، NumPy 2.3.5، Pandas 2.2.3 و Matplotlib 3.11.2. نصب Jupyter برای اجرای اسکریپت لازم نیست. برای notebook می‌توانید طبق [راهنمای رسمی Jupyter](https://jupyter.org/install) آن را نصب کنید؛ در سرور عمومی بدون احراز هویت راه‌اندازی نکنید.

## ۸. پروژه: تحلیل داده ساختگی

فایل `analyze.py` را بسازید و در پوشه‌ای که اجازه نوشتن دارید با `python analyze.py` اجرا کنید. فایل `study_summary.webp` در **پوشه جاری بازنویسی می‌شود**؛ پیش از اجرا از نبود فایل مهم با همین نام مطمئن شوید. `Agg` برای محیط بدون نمایشگر است؛ داده داخل برنامه است و شبکه یا داده شخصی ندارد.

```python
"""Analyze a tiny synthetic study log; no network or real personal data."""
from io import StringIO
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for script/headless use.
import matplotlib.pyplot as plt

DATA = '''topic,minutes
python,30
python,45
math,60
math,
'''


def analyze(csv_text):
    df = pd.read_csv(StringIO(csv_text))
    if not {'topic', 'minutes'}.issubset(df.columns):
        raise ValueError('required columns: topic, minutes')
    df['minutes'] = pd.to_numeric(df['minutes'], errors='raise')
    if (df['minutes'].dropna() < 0).any():
        raise ValueError('minutes cannot be negative')
    missing = int(df[['topic', 'minutes']].isna().any(axis=1).sum())
    clean = df.dropna(subset=['topic', 'minutes'])
    if clean.empty:
        raise ValueError('no complete rows')
    totals = clean.groupby('topic', sort=True)['minutes'].sum()
    mean = float(np.mean(clean['minutes'].to_numpy()))
    return missing, totals, mean


def main():
    missing, totals, mean = analyze(DATA)
    print('omitted_rows=', missing)
    print('total_minutes=', int(totals.sum()))
    print('mean_minutes=', f'{mean:.1f}')
    print('by_topic=', totals.to_dict())
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(totals.index, totals.values, color='#536fd1')
    ax.set(title='Study time by topic', xlabel='Topic', ylabel='Minutes')
    fig.tight_layout()
    path = Path('study_summary.webp')
    fig.savefig(path, format='webp', dpi=120)
    plt.close(fig)
    print('chart=', path)


if __name__ == '__main__':
    main()
```

در اجرای آزمایشی خروجی `omitted_rows= 1`, `total_minutes= 135`, `mean_minutes= 45.0` و `by_topic= {'math': 60.0, 'python': 75.0}` بود و WebP ۷۲۰×۴۸۰ تولید شد. `to_numeric(errors='raise')` مقدار غیرعددی را رد می‌کند. این نمونه کنترل جامعی برای مقدارهای نامتناهی، زمان غیرواقعی، برچسب خالی یا فایل بسیار بزرگ ندارد و برای داده واقعی به اعتبارسنجی بیشتر نیاز دارد.

## ۹. آزمون، تمرین و ارزیابی

**آزمون همراه پروژه (`test_analyze.py`):**
```python
import unittest
from analyze import DATA, analyze

class AnalysisTests(unittest.TestCase):
    def test_summary(self):
        missing, totals, mean = analyze(DATA)
        self.assertEqual(missing, 1)
        self.assertEqual(totals.to_dict(), {'math': 60.0, 'python': 75.0})
        self.assertEqual(mean, 45.0)

    def test_invalid_data(self):
        for data in ['topic,minutes\na,-1\n', 'topic,minutes\na,\n', 'wrong,minutes\na,2\n']:
            with self.subTest(data=data), self.assertRaises(ValueError):
                analyze(data)

if __name__ == '__main__':
    unittest.main()
```

از پوشه پروژه `python -m unittest -v` را اجرا کنید؛ دو تست روی نسخه‌های بالا موفق بودند. اگر import خطا داد، محیط فعال و `python -m pip --version` را بررسی کنید. اگر نوشتن تصویر خطا داد، مسیر و پشتیبانی فرمت WebP/Pillow را در نصب خود بررسی کنید. در صورت تفاوت خروجی، نسخه کتابخانه‌ها را مقایسه کنید.

**پرسش:** ۱) shape چیست؟ ۲) آیا برش پایه NumPy همیشه مستقل است؟ ۳) DataFrame چیست؟ ۴) `count` و `size` چه تفاوتی در داده ناقص دارند؟ ۵) چرا مقدار گمشده لزوماً صفر نیست؟ ۶) مجموع سطرهای کامل و میانگین آن‌ها چقدر است؟ ۷) چرا اجرای نامرتب سلول‌ها خطر دارد؟ ۸) آیا نمودار پروژه نشان‌دهنده رابطه علّی است؟

**تمرین:** یک مقدار ۱۵ به موضوع math اضافه کنید؛ مجموع math و میانگین چهار مقدار کامل را محاسبه و تست خودکار نتیجه را بنویسید. **مینی‌پروژه:** CSV ساختگی با پنج سطر و یک مقدار گمشده بسازید، حذف‌شده‌ها، مجموع و میانگین را با واحد گزارش کنید و نمودار WebP با عنوان و برچسب رسم کنید. برای داده واقعی درباره سوگیری و مجوز توضیح دهید.

**قبولی:** ۷ پاسخ درست، اجرای دو تست و تولید نمودار با مقادیر صحیح. [پاسخ‌نامه جداگانه فصل 15](book-engineering/answers/15-data-analysis-answers-fa.md).

## ۱۰. منابع و واژه‌نامه

**مرور منابع: ۵ نوامبر ۲۰۲۶.** نتایج فقط بر داده مصنوعی و نسخه‌های اعلام‌شده آزمون شده‌اند؛ رابط تعاملی Jupyter آزمون نشده است. فصل ۱۶ به مبانی ریاضی می‌پردازد.

NumPy، Array، Shape، dtype، View، DataFrame، Series، Missing Value، Aggregation، Figure، Axes، Kernel، Notebook.

**منابع؛ مراجعه ۵ نوامبر ۲۰۲۶:** [۱] NumPy، «Absolute basics for beginners»، [منبع](https://numpy.org/doc/stable/user/absolute_beginners.html). [۲] pandas، «What kind of data does pandas handle?»، [منبع](https://pandas.pydata.org/docs/getting_started/intro_tutorials/01_table_oriented.html). [۳] pandas، «Summary statistics»، [منبع](https://pandas.pydata.org/docs/getting_started/intro_tutorials/06_calculate_statistics.html). [۴] Matplotlib، «Quick start guide»، [منبع](https://matplotlib.org/stable/users/explain/quick_start.html). [۵] Jupyter، «Running Code»، [منبع](https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Running%20Code.html). تاریخ صفحه‌ها متغیر یا نامشخص است.

## پیوست: نسخهٔ بازنویسی‌شده و آزمون‌شده

**مرز دو نسخه:** نسخهٔ بازنویسی‌شده و آزمون‌شده در `projects/15-data-analysis-supplement` است و خروجی `(clean, totals, missing)` دارد، برخلاف نسخهٔ پایه که `(missing, totals, mean)` می‌دهد.


### فصل ۱۵ — NumPy، Pandas، Matplotlib و Jupyter

**هنر و علم ساخت هوش | جلد اول | Babak & Ai**  
**بررسی منابع: ۵ نوامبر ۲۰۲۶**

### ۱. تبدیل داده خام به پرسش پاسخ‌پذیر

تحلیل داده صرفاً کشیدن نمودار نیست. ابتدا پرسش را روشن کنید: «در داده ساختگی تمرین، مجموع زمان مطالعه هر موضوع چقدر است؟» سپس منشأ داده، تعریف ستون‌ها، خطا و مقادیر گمشده را بررسی، محاسبه را بازتولید و محدودیت نتیجه را بیان کنید. این نمونه آموزشی یک مشاهده کوچک ساختگی است و درباره رفتار جمعیت، علت موفقیت یا دقت یک مدل نتیجه‌گیری نمی‌کند.

**پیش‌نیاز:** توابع، فایل، محیط مجازی و آزمون. **هدف:** فهم آرایه، شکل و محور در NumPy؛ جدول و گروه‌بندی در Pandas؛ نمودار در Matplotlib؛ و اجرای منظم نوت‌بوک Jupyter.

### ۲. نصب و محیط قابل بازتولید

در محیط مجازی اختصاصی، با توجه به سیستم و منبع رسمی بسته‌ها را نصب کنید: `python -m pip install numpy pandas matplotlib pillow jupyterlab`. این فرمان نیازمند شبکه است؛ قبل از نصب، مجوز، منبع و نسخه‌های سازگار را بررسی کنید. `python -m pip --version` کمک می‌کند pip همان مفسر را صدا بزنید.

**محیط آزمایش واقعی این فصل:** Python 3.13.16، NumPy 2.3.5، Pandas 2.2.3، Matplotlib 3.11.2 و Pillow 13.0.0. نسخه‌ها را برای بازتولید ثبت کنید؛ این فهرست به‌تنهایی قفل کامل زنجیره وابستگی یا تضمین سازگاری همه سیستم‌ها نیست. نوت‌بوک با nbformat 5.11.1 و nbclient اجرا شد؛ آزمون رابط گرافیکی JupyterLab انجام نشده است.

### ۳. NumPy: آرایه، نوع و شکل

NumPy آرایه چندبعدی `ndarray` و عملیات عددی را فراهم می‌کند [۱]. در مثال `a = np.array([[1, 2, 3], [4, 5, 6]])` شکل `a.shape` برابر `(2, 3)` است: دو سطر و سه ستون؛ `a.ndim` برابر ۲ و `a.size` برابر ۶ است. `dtype` نوع داده عناصر را مشخص می‌کند و انتخاب آن بر دقت و حافظه اثر دارد.

`a.sum(axis=0)` سطرها را در امتداد محور صفر کاهش می‌دهد و خروجی `[5, 7, 9]` است؛ `a.sum(axis=1)` برای هر سطر `[6, 15]` می‌دهد. عملیات `a * 2` عنصر به عنصر است؛ برای ضرب ماتریسی از `@` با شکل سازگار استفاده می‌شود. broadcasting قواعد خاص سازگاری ابعاد دارد؛ همیشه شکل ورودی و خروجی را بررسی کنید.

### ۴. Pandas: جدول و پرس‌وجو

`Series` یک ساختار یک‌بعدی دارای برچسب و `DataFrame` جدول دارای ستون‌های نام‌دار است. `pd.read_csv` CSV را می‌خواند؛ `head()`، `dtypes` و `isna().sum()` برای بازرسی اولیه مفیدند. نوع و معنای هر ستون را تأیید کنید: «دقیقه» باید عدد معتبر و یکای اندازه‌گیری مشخص باشد.

در `df.groupby('topic')['minutes'].sum()` داده بر اساس موضوع گروه‌بندی و مجموع هر گروه محاسبه می‌شود [۲]. گروه‌بندی نتیجه را خلاصه می‌کند و ترتیب، مقدارهای گمشده و داده‌های تکراری ممکن است بر پاسخ اثر بگذارند. مقادیر گمشده برابر صفر نیستند: در پروژه یک ردیف بدون دقیقه را **گزارش و فقط برای محاسبه حذف** می‌کنیم؛ این تصمیم به مسئله وابسته است و ممکن است سوگیری ایجاد کند [۳].

### ۵. Matplotlib: نمودار و تفسیر

برای مقایسه مجموع گروه‌های گسسته از نمودار میله‌ای استفاده می‌کنیم. عنوان، نام محور و واحد لازم‌اند. شکل ۱۵-۲ داده ساختگی ما را نشان می‌دهد: Python برابر ۷۵ دقیقه و math برابر ۶۰ دقیقه؛ یک ردیف با دقیقه ناموجود کنار گذاشته شده است. نسبت ۷۵ به ۶۰ برابر ۱٫۲۵ است، اما از آن درباره جامعه یا رابطه علّی نتیجه نمی‌گیریم.

![شکل ۱۵-۲: مجموع دقیقه‌های معتبر برای دو موضوع مصنوعی، Python برابر ۷۵ و math برابر ۶۰.](assets/images/babak-ai/ch15-study.webp)

**شکل ۱۵-۲ — خلاصه داده ساختگی.** نمودار با Matplotlib ساخته و WebP ذخیره شده است. محور عمودی از صفر آغاز می‌شود؛ واحد دقیقه است. ساخت `Figure` بدون رابط گرافیکی برای خروجی فایل مناسب است [۴].

### ۶. Jupyter و خطر وضعیت پنهان

نوت‌بوک `.ipynb` سلول‌های کد، متن و خروجی را ذخیره می‌کند؛ **kernel** برنامه اجراکننده را نگه می‌دارد و متغیرها بین اجرای سلول‌ها باقی می‌مانند [۵]. اگر سلول‌ها را نامرتب اجرا کنید، خروجی ممکن است به متغیر قدیمی وابسته باشد. پیش از تحویل، kernel را restart و همه سلول‌ها را از بالا اجرا و خروجی‌ها را بررسی کنید.

فقط نوت‌بوک قابل اعتماد را اجرا کنید؛ کد نوت‌بوک مانند هر برنامه Python می‌تواند به فایل‌ها یا شبکه دسترسی پیدا کند. نوت‌بوک و خروجی‌ها ممکن است حاوی داده حساس باشند. در پروژه ما `study.ipynb` کنار `analyze.py` قرار دارد؛ از همان پوشه با `jupyter lab` باز کنید و سلول‌ها را به‌ترتیب اجرا کنید. اجرای نوت‌بوک با nbclient آزمایش شده، نه رابط JupyterLab.

### ۷. پروژه تحلیل داده ساختگی

فایل `analyze.py` را بسازید. داده داخلی چهار ردیف دارد: سه دقیقه معتبر ۳۰، ۴۵، ۶۰ و یک مقدار ناموجود. تحلیل دقیقه ناموجود را صفر فرض نمی‌کند. توابع از رشته CSV دریافت می‌کنند و نمودار در پوشه موقت ذخیره و پس از اجرا پاک می‌شود؛ برای نگهداری نمودار، با آگاهی مسیر خروجی دیگری به `make_plot` بدهید.

```python
"""Analyze synthetic study sessions, with explicit missing-data policy."""
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

DATA = '''topic,minutes
python,30
python,45
math,60
math,
'''


def analyze(csv_text):
    frame = pd.read_csv(StringIO(csv_text))
    if not {'topic', 'minutes'}.issubset(frame.columns):
        raise ValueError('missing required columns')
    frame['minutes'] = pd.to_numeric(frame['minutes'], errors='raise')
    if frame['topic'].isna().any() or frame['topic'].str.strip().eq('').any():
        raise ValueError('topic missing')
    present = frame['minutes'].dropna().to_numpy()
    if not np.isfinite(present).all() or (present < 0).any():
        raise ValueError('minutes must be finite and nonnegative')
    clean = frame.dropna(subset=['minutes']).copy()
    if clean.empty:
        raise ValueError('no measured minutes')
    totals = clean.groupby('topic')['minutes'].sum().sort_index()
    return clean, totals, int(frame['minutes'].isna().sum())


def make_plot(totals, filename):
    fig = Figure(figsize=(7, 4), layout='constrained')
    ax = fig.subplots()
    ax.bar(totals.index, totals.values, color='#627bd2')
    ax.set(title='Study minutes by topic', ylabel='Minutes', xlabel='Topic')
    fig.savefig(filename, format='webp', dpi=140)


def main():
    clean, totals, missing = analyze(DATA)
    print('valid_rows=', len(clean), 'missing_rows=', missing)
    print('mean_minutes=', float(np.mean(clean['minutes'].to_numpy())))
    print('totals=', {key: float(value) for key, value in totals.items()})
    with TemporaryDirectory() as directory:
        output = Path(directory) / 'study.webp'
        make_plot(totals, output)
        print('webp_created=', output.is_file())


if __name__ == '__main__':
    main()
```

اجرا: `python analyze.py`. خروجی آزمایش‌شده:

```text
valid_rows= 3 missing_rows= 1
mean_minutes= 45.0
totals= {'math': 60.0, 'python': 75.0}
webp_created= True
```

`np.isfinite` مقدار بی‌نهایت را رد می‌کند. ورودی منفی، موضوع ناموجود و نبود همه دقیقه‌ها رد می‌شوند. این مثال همه مشکلات داده مثل نام‌های تکراری با فاصله یا اختلاف واحد را حل نمی‌کند؛ برای داده واقعی طرح اعتبارسنجی باید کامل‌تر باشد.

### ۸. آزمون و بازبینی

فایل زیر را کنار برنامه ذخیره و از همان پوشه `python -m unittest -v test_analyze` اجرا کنید. فایل آزمون به Pillow نیاز دارد و محتوا و فرمت WebP را بررسی می‌کند:

```python
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image
from analyze import DATA, analyze, make_plot


class AnalysisTests(unittest.TestCase):
    def test_summary(self):
        clean, totals, missing = analyze(DATA)
        self.assertEqual((len(clean), missing), (3, 1))
        self.assertEqual(totals.to_dict(), {'math': 60.0, 'python': 75.0})
        self.assertEqual(clean['minutes'].mean(), 45.0)

    def test_invalid(self):
        for data in ('topic,minutes\nx,-1\n', 'topic,minutes\nx,inf\n',
                     'topic,minutes\nx,\n', 'topic,minutes\n,5\n'):
            with self.subTest(data=data), self.assertRaises(ValueError):
                analyze(data)

    def test_webp(self):
        _, totals, _ = analyze(DATA)
        with TemporaryDirectory() as folder:
            p = Path(folder) / 'chart.webp'
            make_plot(totals, p)
            with Image.open(p) as image:
                self.assertEqual(image.format, 'WEBP')
                image.verify()


if __name__ == '__main__':
    unittest.main()
```

سه تست اجرا شده‌اند: خلاصه، چهار ورودی نامعتبر و تولید تصویر. نتیجه سه آزمون `OK` است؛ این آزمون‌ها کیفیت علمی تمام داده‌ها یا کارکرد همه نسخه‌ها را تضمین نمی‌کنند. خطای `ModuleNotFoundError` معمولاً نشان‌دهنده نصب نبودن بسته در مفسر فعال است؛ مسیر Python و محیط را بررسی کنید. اگر خروجی WebP ساخته نشد، پشتیبانی WebP در Pillow و مجوز پوشه موقت را بررسی کنید.

### ۹. تمرین و ارزیابی

**پرسش:** ۱) shape آرایه ۲×۳ چیست؟ ۲) `axis=0` در جمع این آرایه چه می‌کند؟ ۳) آیا مقدار گمشده همان صفر است؟ ۴) groupby چه می‌کند؟ ۵) میانگین ۳۰، ۴۵، ۶۰ چیست؟ ۶) چرا اجرای نامرتب نوت‌بوک خطرناک است؟ ۷) آیا نمودار فوق علّیت ثابت می‌کند؟ ۸) چرا نسخه محیط را ثبت می‌کنیم؟

**تمرین:** آرایه دو سطری مثال را بسازید و جمع محورهای ۰ و ۱ را بررسی کنید. سپس مقدار ناموجود را گزارش کرده، سیاست جایگزین مانند حذف یا تکمیل را با دلیل و محدودیت مقایسه کنید؛ به‌صورت خودکار صفرگذاری نکنید. **مینی‌پروژه:** داده ساختگی دیگری با دست‌کم دو گروه، یک داده گمشده، گزارش تعداد، آزمون مجموع و نمودار WebP همراه واحد تهیه کنید. برای قبولی ۷ پاسخ درست و سه آزمون موفق لازم است.

[پاسخ‌نامه جداگانه فصل 15](book-engineering/answers/15-data-analysis-answers-fa.md).

### ۱۰. منابع و ادامه

واژه‌ها: ndarray، shape، axis، dtype، DataFrame، missing data، groupby، visualization، kernel و notebook. فصل ۱۶ ورود به جبر، توابع و لگاریتم است.

**منابع؛ بررسی ۵ نوامبر ۲۰۲۶:** [۱] NumPy، [Quickstart](https://numpy.org/doc/stable/user/quickstart.html). [۲] Pandas، [10 minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html). [۳] Pandas، [Missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html). [۴] Matplotlib، [FAQ](https://matplotlib.org/stable/users/faq.html). [۵] Project Jupyter، [What is Jupyter?](https://docs.jupyter.org/en/latest/what_is_jupyter.html). تاریخ صفحات متغیر است؛ نسخه آزمایش‌شده بالا مشخص شده است.

