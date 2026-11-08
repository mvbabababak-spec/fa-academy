# فصل ۱۸ — مشتق، انتگرال، قاعده زنجیره‌ای و گرادیان

**هنر و علم ساخت هوش | جلد اول | Babak & Ai**  
**بررسی منابع: ۵ نوامبر ۲۰۲۶**

## ۱. اندازه‌گیری تغییر

یک مدل یادگیری ورودی و پارامترها را به خروجی و زیان تبدیل می‌کند. برای فهم اینکه تغییر کوچک پارامتر چگونه زیان را تغییر می‌دهد، حسابان ابزار اصلی است. **هدف:** تفاوت نرخ متوسط و مشتق، مشتق جزئی، قاعده زنجیره‌ای، بردار گرادیان و انتگرال معین؛ همچنین مقایسه محاسبه تحلیلی و عددی. **پیش‌نیاز:** تابع و نمودار فصل ۱۶، بردار فصل ۱۷.

این فصل مقدمات تغییر را آموزش می‌دهد؛ الگوریتم‌های بهینه‌سازی فصل ۲۰ و پس‌انتشار شبکه فصل ۲۸ هستند. مشتق نشان‌دهنده تغییر محلی است و به‌تنهایی موفقیت یک مدل یا بهینه سراسری را تضمین نمی‌کند.

## ۲. نرخ تغییر و مشتق

نرخ تغییر متوسط f در بازه از x تا `x+h`، برای `h≠0`، برابر `[f(x+h)−f(x)]/h` است. اگر حد این نسبت وقتی h به صفر میل می‌کند وجود داشته باشد، **مشتق** `f′(x)` است [۱]. برای `f(x)=x²` داریم `[(x+h)²−x²]/h=2x+h` و در حد `f′(x)=2x`. در `x=1` شیب مماس ۲ است؛ برای x نزدیک یک، تغییر کوچک خروجی تقریباً دو برابر تغییر x است.

![شکل ۱۸-۱: سهمی x مربع و خط مماس y برابر ۲x منهای ۱ در نقطه ۱،۱ با شیب ۲.](assets/images/babak-ai/ch18-derivative.webp)

**شکل ۱۸-۱ — شیب مماس.** تقریب خطی نزدیک نقطه معتبرتر است، نه لزوماً در فاصله بزرگ. اگر f بر حسب متر و x بر حسب ثانیه باشد، واحد مشتق متر بر ثانیه است.

## ۳. قواعد مشتق و نقاط نامشتق‌پذیر

مشتق ثابت صفر، مشتق `xⁿ` برای توان صحیح مناسب `n xⁿ⁻¹` و مشتق جمع برابر جمع مشتق‌هاست. مثلاً `d(3x²+2x+5)/dx=6x+2`. در ضرب دو تابع `d(uv)/dx=u′v+uv′`؛ مشتق حاصل‌ضرب عموماً حاصل‌ضرب مشتق‌ها نیست.

مشتق همیشه وجود ندارد: برای `|x|` در صفر شیب سمت چپ −۱ و راست +۱ است، پس مشتق معمول وجود ندارد. یک تابع مشتق‌پذیر در نقطه پیوسته است، اما پیوستگی به‌تنهایی مشتق‌پذیری را تضمین نمی‌کند. نزدیک مرز دامنه یا شکستگی، اختلاف محدود ممکن است پاسخ گمراه‌کننده بدهد.

## ۴. قاعده زنجیره‌ای

برای `h(x)=f(g(x))` با مشتق‌پذیری لازم، `h′(x)=f′(g(x))g′(x)` است [۲]. اگر `h(x)=(2x+1)²`، مشتق بیرونی نسبت به ورودی میانی `2(2x+1)` و مشتق درونی ۲ است؛ بنابراین `h′(x)=4(2x+1)`. در x=۱ مقدار مشتق ۱۲ است.

در مدلی که خروجی از چند تبدیل پیاپی می‌گذرد، قاعده زنجیره‌ای تغییر را در مسیرها منتقل می‌کند. این پایه مفهومی پس‌انتشار است، اما پیاده‌سازی کامل و نحوه جمع مسیرها در فصل ۲۸ بررسی می‌شود.

## ۵. مشتق جزئی و گرادیان

برای تابعی از چند ورودی، مشتق جزئی نسبت به یکی از آن‌ها، دیگر ورودی‌ها را ثابت فرض می‌کند. اگر `f(x,y)=x²+3xy+y²`، آنگاه `∂f/∂x=2x+3y` و `∂f/∂y=3x+2y` است. **گرادیان** بردار این مشتق‌هاست: `∇f=[2x+3y, 3x+2y]`؛ در `(1,2)` برابر `[8,7]` است [۳].

**معادله ۱۸-۱** — f تابع و x و y ورودی‌ها هستند؛ هر مؤلفه یک مشتق جزئی است.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" dir="ltr" aria-label="gradient has partial derivatives"><mo>∇</mo><mi>f</mi><mo>=</mo><mo>(</mo><mfrac><mrow><mo>∂</mo><mi>f</mi></mrow><mrow><mo>∂</mo><mi>x</mi></mrow></mfrac><mo>,</mo><mfrac><mrow><mo>∂</mo><mi>f</mi></mrow><mrow><mo>∂</mo><mi>y</mi></mrow></mfrac><mo>)</mo></math>

برای تابع مشتق‌پذیر و جهت واحد u، نرخ تغییر جهت‌دار `∇f·u` است. اگر گرادیان غیرصفر باشد، جهت آن بیشترین نرخ افزایش محلی را در میان جهت‌های واحد دارد؛ گرادیان صفر چنین جهت یکتایی تعیین نمی‌کند. مقیاس و واحد متغیرها در تفسیر جهت اهمیت دارند.

## ۶. انتگرال معین و نامعین

انتگرال معین می‌تواند حد مجموع‌های ریمانی و مساحت علامت‌دار زیر نمودار باشد: نواحی زیر محور x علامت منفی دارند. برای تابع پیوسته `f(x)=x²` و پادمشتق `F(x)=x³/3`، قضیه بنیادی حسابان می‌دهد `∫₀² x² dx=F(2)−F(0)=8/3` [۴]. انتگرال نامعین خانواده پادمشتق‌ها را با ثابت C نمایش می‌دهد: `∫x² dx=x³/3+C`.

با تقسیم بازه به n قسمت و نمونه‌برداری وسط هر قسمت می‌توان مقدار را تقریب زد. نتیجه به تعداد قسمت‌ها و ویژگی تابع بستگی دارد؛ انتگرال علامت‌دار لزوماً مساحت هندسی مثبت نیست و عوض‌کردن حدود علامت آن را تغییر می‌دهد.

## ۷. پروژه: گرادیان تحلیلی و عددی

فایل `calculus.py` را بسازید؛ وابستگی خارجی یا شبکه ندارد. اختلاف مرکزی `(f(x+h)−f(x−h))/(2h)` مشتق را برای h کوچک تقریب می‌زند، اما h بیش‌ازحد کوچک ممکن است به دلیل گردکردن و حذف رقم‌ها خطا را افزایش دهد. این تست برای تابع هموار و نقطه مشخص است، نه تضمین عمومی.

```python
"""Analytic and numerical calculus checks for a smooth polynomial."""
import math


def f(x, y):
    return x*x + 3*x*y + y*y


def gradient(x, y):
    return (2*x + 3*y, 3*x + 2*y)


def numerical_gradient(x, y, h=1e-5):
    if not math.isfinite(h) or h <= 0:
        raise ValueError('h must be finite and positive')
    dx = (f(x+h, y) - f(x-h, y)) / (2*h)
    dy = (f(x, y+h) - f(x, y-h)) / (2*h)
    return dx, dy


def midpoint_integral(func, a, b, n):
    if type(n) is not int or n <= 0:
        raise ValueError('n must be a positive integer')
    width = (b - a) / n
    return sum(func(a + (i + 0.5)*width) for i in range(n)) * width


def main():
    exact = gradient(1, 2)
    numeric = numerical_gradient(1, 2)
    print('analytic_gradient=', exact)
    print('numeric_gradient=', tuple(round(v, 6) for v in numeric))
    print('gradient_matches=', all(math.isclose(a, b, rel_tol=1e-8, abs_tol=1e-8)
                                   for a, b in zip(exact, numeric)))
    area = midpoint_integral(lambda x: x*x, 0, 2, 1000)
    print('integral_x2_0_2=', round(area, 6))
    print('exact_integral=', round(8/3, 6))


if __name__ == '__main__':
    main()
```

خروجی Python 3.13.16: `analytic_gradient= (8, 7)`؛ `numeric_gradient= (8.0, 7.0)`؛ `gradient_matches= True`؛ تقریب انتگرال `2.666666` و مقدار دقیق گرد‌شده `2.666667`. اختلاف حدود `6.67×10⁻⁷` است. اعداد نمایش داده‌شده گرد شده‌اند.

## ۸. آزمون و عیب‌یابی

فایل زیر را کنار پروژه قرار دهید و `python -m unittest -v test_calculus` اجرا کنید. چهار تست گرادیان، نقطه صفر، انتگرال با خطای مجاز `10⁻⁶` و ورودی نامعتبر را می‌سنجند.

```python
import math
import unittest
from calculus import f, gradient, numerical_gradient, midpoint_integral


class CalculusTests(unittest.TestCase):
    def test_gradient(self):
        self.assertEqual(gradient(1, 2), (8, 7))
        for a, b in zip(gradient(1, 2), numerical_gradient(1, 2)):
            self.assertTrue(math.isclose(a, b, rel_tol=1e-8, abs_tol=1e-8))

    def test_other_point(self):
        self.assertEqual(gradient(0, 0), (0, 0))
        self.assertEqual(numerical_gradient(0, 0), (0, 0))

    def test_integral(self):
        self.assertAlmostEqual(midpoint_integral(lambda x: x*x, 0, 2, 1000), 8/3, delta=1e-6)
        self.assertAlmostEqual(midpoint_integral(lambda x: x, 2, 0, 100), -2)

    def test_invalid(self):
        for h in (0, -1, float('nan')):
            with self.assertRaises(ValueError): numerical_gradient(1, 2, h)
        for n in (0, -1, True, 2.5):
            with self.assertRaises(ValueError): midpoint_integral(f, 0, 1, n)


if __name__ == '__main__':
    unittest.main()
```

`h` باید مثبت و متناهی و n یک عدد صحیح مثبت باشد. آزمون انتگرال از خطای مطلق متناسب با تقریب استفاده می‌کند؛ برابری دقیق عدد شناور انتظار نمی‌رود. نتیجه نزدیک در چند نقطه ثابت نمی‌کند مشتق تحلیلی برای همه نقاط یا توابع درست است.

## ۹. تمرین و ارزیابی

**پرسش:** ۱) مشتق `x²`؟ ۲) مشتق ثابت؟ ۳) مشتق `(2x+1)²` در x=۱؟ ۴) مشتق جزئی `x²+y²` نسبت به x؟ ۵) گرادیان آن در `(1,2)`؟ ۶) `∫₀² x dx`؟ ۷) آیا `|x|` در صفر مشتق‌پذیر است؟ ۸) چرا h بسیار کوچک همیشه بهتر نیست؟ ۹) آیا انتگرال معین همیشه مثبت است؟ ۱۰) آیا گرادیان صفر جهت بیشترین افزایش یکتایی دارد؟

**تمرین:** برای `g(x,y)=x²+y²` گرادیان تحلیلی و عددی را در دو نقطه مقایسه کنید. **مینی‌پروژه:** نمودار تابع و مماس در یک نقطه و جدول خطای اختلاف مرکزی برای سه h بسازید؛ نتایج و محدودیت دقت را توضیح دهید. **چالش:** تفاوت مشتق تحلیلی و عددی را مقایسه کنید و علت شکست احتمالی هر روش را بنویسید. **قبولی:** حداقل ۸ پاسخ صحیح از ۱۰ و چهار آزمون موفق.

[پاسخ‌نامه جداگانه فصل 18](book-engineering/answers/18-calculus-answers-fa.md).

## ۱۰. منابع و ادامه

Derivative مشتق؛ Partial Derivative مشتق جزئی؛ Gradient گرادیان؛ Chain Rule قاعده زنجیره‌ای؛ Integral انتگرال؛ Finite Difference اختلاف محدود. **بررسی ۵ نوامبر ۲۰۲۶:** مبانی پایدارند؛ تقریب عددی وابسته به گام و دقت ماشین است. فصل ۱۹ احتمال و آمار را می‌آموزد.

**منابع؛ مراجعه ۵ نوامبر ۲۰۲۶:** [۱] OpenStax، «Key Concepts: Derivatives»، Calculus Volume 1، ۲۰۱۶، [منبع](https://openstax.org/books/calculus-volume-1/pages/3-key-concepts). [۲] OpenStax، «The Chain Rule»، ۲۰۱۶، [منبع](https://openstax.org/books/calculus-volume-1/pages/3-6-the-chain-rule). [۳] OpenStax، «Directional Derivatives and the Gradient»، Calculus Volume 3، ۲۰۱۶، [منبع](https://openstax.org/books/calculus-volume-3/pages/4-6-directional-derivatives-and-the-gradient). [۴] OpenStax، «The Fundamental Theorem of Calculus»، Calculus Volume 1، تاریخ انتشار نامشخص، [منبع](https://openstax.org/books/calculus-volume-1/pages/5-3-the-fundamental-theorem-of-calculus).
