# طبقه‌بندی قاعده‌محور پیام ساختگی

**هدف:** طبقه‌بندی قاعده‌محور پیام ساختگی با داده ساختگی.

**پیش‌نیاز:** Python 3.13 و کتابخانه استاندارد. نصب بسته اضافی الزامی نیست.

از همین پوشه: `python rule_baseline.py`.

**خروجی ثبت‌شده در محیط آزمایش:**

```text
prediction=True, expected=True: شما برنده جایزه شدید
prediction=True, expected=True: رمز عبور خود را ارسال کنید
prediction=False, expected=False: فردا جلسه داریم
prediction=True, expected=False: این درس درباره امنیت رمز عبور است
prediction=False, expected=True: برای دریافت پاداش، اطلاعات بانکی بدهید
accuracy=3/5 = 60%
```

**آزمون:** `python -m unittest discover -v` از همین پوشه.

**محدودیت:** مدل امنیتی واقعی نیست؛ فارسی و کلمات کلیدی محدودند.
