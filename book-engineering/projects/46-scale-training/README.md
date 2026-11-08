# پروژهٔ فصل ۴۶: activation checkpointing و DDP روی CPU

این آزمایشگاه دو سازوکار را که نام «checkpoint» در آن‌ها گمراه‌کننده است از هم جدا می‌کند: **activation checkpointing** در forward/backward بعضی tensorهای میانی را دوباره محاسبه می‌کند؛ **training-state checkpoint** وزن/optimizer/data/RNG را برای ادامهٔ یک run ثبت می‌کند. پروژهٔ کوچک فقط اولی و همگام‌سازی گرادیان DDP را اجرا می‌کند؛ recovery واقعی را پیاده‌سازی نمی‌کند.

## نیازمندی و اجرا

- Python 3.11+ و PyTorch 2.6.x با پشتیبانی CPU Gloo؛ GPU لازم نیست.
- فقط روی دو process محلی با دادهٔ مصنوعی ثابت اجرا می‌شود؛ هیچ سرویس، dataset یا model از شبکه دریافت نمی‌شود.
- از ریشهٔ repository اجرا کنید:

```bash
python book-engineering/projects/46-scale-training/scaling_lab.py --output /tmp/ch46-scaling.json
(cd book-engineering/projects/46-scale-training && python -m unittest discover -v)
```

CLI یک forward/backward معمولی را با `torch.utils.checkpoint.checkpoint(..., use_reentrant=False)` مقایسه می‌کند، تعداد بایت tensorهایی را که PyTorch از طریق hook برای backward ذخیره می‌کند می‌شمارد، سپس با `torch.distributed` و دو rank از نوع Gloo یک گرادیان DDP را با مرجع تک‌پردازشی می‌سنجد. fixture توزیع‌شده عمداً ۳ و ۲ نمونه دارد و loss محلی را متناسب با تعداد نمونه وزن می‌دهد تا میانگین گرادیان کل داده به‌دست آید. گزارش JSON نسخهٔ Python/PyTorch، config، hash کد و fixture، و محدودیت‌های آزمایش را ثبت می‌کند.

ده آزمون واحد، برابری خروجی و گرادیان، کاهش بایت‌های saved-tensor در همین مدل/نسخه، انتخاب صریح non-reentrant، تطبیق DDP با مرجع، shardهای نابرابر، پایداری fingerprint، قالب گزارش و نوشتن اتمی JSON را کنترل می‌کنند.

## محدودیت‌ها

- `saved_tensor_bytes` از hook گراف autograd می‌آید؛ peak GPU/CPU memory، fragmentation، throughput یا زمان recomputation را اندازه نمی‌گیرد.
- اجرای Gloo دو پردازه روی یک میزبان است؛ NIC، چند node، NCCL، GPU و کارایی scale را آزمایش نمی‌کند.
- گرادیان مصنوعی و شبکهٔ چندلایه، مدل زبانی یا کیفیت task را آموزش نمی‌دهند.
- fingerprint برای هویت‌دادن به fixture است؛ امضای امنیتی، provenance حقوقی یا تضمین بازتولید بین نسخه‌ها نیست.
- فایل JSON گزارش یک run manifest ساده است، نه MLflow server، artifact store یا سامانهٔ تحمل خطا. در production باید checkpoint هماهنگ همهٔ stateها، storage قابل اتکا، سیاست دسترسی و بازیابی واقعی جداگانه طراحی و آزموده شوند.
