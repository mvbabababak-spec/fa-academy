# round-trip چهار float32 در فایل موقت

**هدف:** round-trip چهار float32 در فایل موقت با داده ساختگی.

**پیش‌نیاز:** Python 3.13 و کتابخانه استاندارد. نصب بسته اضافی الزامی نیست.

از همین پوشه: `python storage_demo.py`.

**خروجی ثبت‌شده در محیط آزمایش:**

```text
number_of_values=4
bytes_per_value=4
payload_bytes=16
file_bytes=16
recovered=(1.0, 2.5, -3.0, 4.0)
```

**آزمون:** `python -m unittest discover -v` از همین پوشه.

**محدودیت:** این اندازه payload است و بنچمارک سخت‌افزار نیست.
