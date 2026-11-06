# پروژهٔ فصل ۴۵ — آزمایشگاه دقت عددی و Quantization

این تمرین روی CPU رفتار عددی چند dtype را اندازه می‌گیرد، نه سرعت را: حدود قالب‌ها را از `torch.finfo` می‌خواند، تبدیل FP32 به FP16/BF16/FP8 و برگشت را برای یک بردار ثابت گزارش می‌کند، BF16 autocast را روی یک Linear کوچک با مرجع FP32 مقایسه می‌کند و quantization صحیح affine را با scaleهای per-tensor و per-group نشان می‌دهد.

## نیازمندی و اجرا

- Python 3.11+ و PyTorch 2.6.x؛ تست‌ها در PyTorch `2.6.0+cpu` اجرا شده‌اند.
- CPU کافی است؛ GPU، دانلود داده یا نصب NumPy لازم نیست.
- از ریشهٔ مخزن:

```bash
python book-engineering/projects/45-precision/precision_lab.py
python book-engineering/projects/45-precision/precision_lab.py --output /tmp/ch45-precision.json
(cd book-engineering/projects/45-precision && python -m unittest discover -v)
```

برنامه JSON قطعی چاپ می‌کند یا در مسیر انتخابی می‌نویسد. هشدار PyTorch دربارهٔ نبود NumPy در بعضی محیط‌های CPU، اگر ظاهر شد، برای این پروژه مسدودکننده نیست؛ کد از NumPy استفاده نمی‌کند.

## آنچه خروجی می‌سنجد

- `formats`: تعداد bit، چیدمان sign/exponent/fraction، `max_finite`، کوچک‌ترین مقدار نرمال، epsilon نزدیک ۱ و هزینهٔ خام یک میلیون مقدار. مقادیر از dtypeهای واقعاً حاضر در runtime می‌آیند.
- `cast_probe`: خروجی‌های رفت‌وبرگشت FP32→dtype→FP32، شمار زیرریز به صفر، Inf و NaN و بیشینهٔ خطای قدر مطلق برای نتایج متناهی. Overflow همان نسخهٔ PyTorch مشاهده می‌شود؛ برنامه یک رفتار overflow واحد را برای همهٔ backendها تجویز نمی‌کند.
- `cpu_bf16_autocast`: dtype ورودی/خروجی و وزن، متناهی‌بودن و اختلاف از خروجی FP32. این اجرا benchmark نیست و سرعت CPU را اندازه نمی‌گیرد.
- `quantization`: quantization متقارن و affine، `round`، clamp، بازسازی، MAE/RMSE، شمار اشباع، calibration shift و مقایسهٔ scale کلی با scale گروهی در برداری با outlier.

## مرزهای مدل آموزشی

این مثال‌ها tensor کوچک و ساختگی‌اند. پروژه accuracy یک مدل، افت loss در آموزش، کیفیت benchmark، latency، توان سخت‌افزار، kernel coverage یا سازگاری checkpoint میان نسخه‌ها را نمی‌سنجد. نتیجهٔ cast FP8 فقط پشتیبانی dtype/cast در همین runtime CPU را نشان می‌دهد، نه اجرای GEMM یا پشتیبانی accelerator. تابع گروهی روی بردار flatten‌شده کار می‌کند، نه layout کانال یک لایهٔ واقعی. کدهای کمتر از ۸ bit برای آموزش فرمول در قالب `torch.int8` نگهداری می‌شوند؛ bit-packing، هزینهٔ scale/zero-point، kernel هدف و اندازهٔ واقعی مدل محاسبه نمی‌شود. آزمون گروه‌بندی تنها همان ورودی مصنوعی را مقایسه می‌کند؛ برای مدل باید validation و معیار task هم سنجیده شود.

۱۰ آزمون واحد، متادیتای dtype، underflow/overflow مشاهده‌شده، BF16 autocast، حدود و qparams، اشباع ناشی از تغییر توزیع، کاهش خطای نمونهٔ per-group، ورودی‌های نامعتبر و JSON قطعی را می‌سنجند. این آزمون‌ها هیچ ادعای کیفیت یا کارایی مدل واقعی ندارند.
