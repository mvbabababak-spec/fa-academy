# فصل ۱۵ — NumPy، Pandas، Matplotlib و Jupyter

**هنر و علم ساخت هوش | جلد اول | Babak & Ai**
**نسخه ۱.۰ · بررسی منابع: ۵ نوامبر ۲۰۲۶**

## ۱. از جدول کوچک تا تحلیل داده

داده به‌تنهایی پاسخ نیست: باید منشأ، واحد، خطا، داده گمشده، سؤال و محدودیت آن را بشناسیم. در این فصل آرایه عددی NumPy، جدول Pandas، تصویرسازی Matplotlib و محیط تعاملی Jupyter را می‌آموزیم. **پیش‌نیاز:** Python، تابع، فایل و محیط مجازی. **پروژه:** تحلیل چهار سطر ساختگی مطالعه، با گزارش رکورد ناقص و نمودار WebP.

این داده آموزشی ساختگی است، نه نمونه‌ای نماینده از رفتار انسان‌ها. تحلیل توصیفی آن رابطه علّی یا کیفیت یادگیری را نشان نمی‌دهد. در کار واقعی، رضایت، حریم خصوصی، مجوز داده، واحد اندازه‌گیری و روش نمونه‌گیری اهمیت دارند.

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

**تمرین:** یک مقدار ۱۵ به موضوع math اضافه کنید؛ مجموع math برابر ۷۵ و میانگین چهار مقدار کامل ۳۷٫۵ می‌شود. تست خودکار این نتیجه را بنویسید. **مینی‌پروژه:** CSV ساختگی با پنج سطر و یک مقدار گمشده بسازید، حذف‌شده‌ها، مجموع و میانگین را با واحد گزارش کنید و نمودار WebP با عنوان و برچسب رسم کنید. برای داده واقعی درباره سوگیری و مجوز توضیح دهید.

**قبولی:** ۷ پاسخ درست، اجرای دو تست و تولید نمودار با مقادیر صحیح. پاسخ: ۱) اندازه ابعاد؛ ۲) خیر؛ ۳) جدول؛ ۴) `count` بدون مقدار گمشده و `size` تعداد سطر؛ ۵) مقدار ناشناخته است؛ ۶) ۱۳۵ و ۴۵؛ ۷) وضعیت پنهان kernel؛ ۸) خیر.

## ۱۰. منابع و واژه‌نامه

**مرور منابع: ۵ نوامبر ۲۰۲۶.** نتایج فقط بر داده مصنوعی و نسخه‌های اعلام‌شده آزمون شده‌اند؛ رابط تعاملی Jupyter آزمون نشده است. فصل ۱۶ به مبانی ریاضی می‌پردازد.

NumPy، Array، Shape، dtype، View، DataFrame، Series، Missing Value، Aggregation، Figure، Axes، Kernel، Notebook.

**منابع؛ مراجعه ۵ نوامبر ۲۰۲۶:** [۱] NumPy، «Absolute basics for beginners»، [منبع](https://numpy.org/doc/stable/user/absolute_beginners.html). [۲] pandas، «What kind of data does pandas handle?»، [منبع](https://pandas.pydata.org/docs/getting_started/intro_tutorials/01_table_oriented.html). [۳] pandas، «Summary statistics»، [منبع](https://pandas.pydata.org/docs/getting_started/intro_tutorials/06_calculate_statistics.html). [۴] Matplotlib، «Quick start guide»، [منبع](https://matplotlib.org/stable/users/explain/quick_start.html). [۵] Jupyter، «Running Code»، [منبع](https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Running%20Code.html). تاریخ صفحه‌ها متغیر یا نامشخص است.
