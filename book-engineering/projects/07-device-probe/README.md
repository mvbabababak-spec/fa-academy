# شناسایی اختیاری دستگاه PyTorch

**هدف:** شناسایی اختیاری دستگاه PyTorch با داده ساختگی.

**پیش‌نیاز:** Python 3.13 و کتابخانه استاندارد. PyTorch اختیاری است؛ بدون آن شاخه unavailable نمایش داده می‌شود. نصب بسته اضافی الزامی نیست.

از همین پوشه: `python device_probe.py`.

**خروجی ثبت‌شده در محیط آزمایش:**

```text
python= 3.13.16
torch= not installed
device= unavailable
reason= PyTorch is not installed
tpu=not checked
```

**آزمون:** `python -m unittest discover -v` از همین پوشه.

**محدودیت:** تست‌های سخت‌افزار صرفاً mock هستند؛ GPU و TPU واقعی اجرا نشدند.
