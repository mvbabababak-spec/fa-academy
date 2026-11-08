# آزمایشگاه محلیِ دروازهٔ انتشار — فصل ۶۹

این پروژه دو مرز را با Python استاندارد نشان می‌دهد: (۱) ارزیابی قطعیِ manifest، شواهدِ gate، digest و rollout روی سه سناریوی ساختگی؛ (۲) یک HTTP smoke service واقعی اما موقت و فقط loopback که health/version و یک برچسبِ ثابتِ ساختگی را برمی‌گرداند. هیچ مدل، وزن، cloud account، credential، دادهٔ کاربر یا ترافیک تولیدی استفاده نمی‌شود. «promoted» و «rollback» در خروجی شبیه‌ساز تصمیمِ فرضی‌اند؛ هیچ استقرار واقعی یا نوشتن روی production انجام نمی‌شود.

## نیازمندی و بازتولید

- CPython 3.10 یا جدیدتر؛ پروژه در CPython 3.13.16 آزمایش شده است.
- فقط کتابخانهٔ استاندارد؛ `requirements.txt` عمداً وابستگی خارجی ندارد.
- همهٔ سناریوها و شناسه‌ها ساختگی‌اند. hash bundle در این تمرین، hash از JSON canonical توصیف اجزاست؛ آن را با digest یک image، وزن مدل یا artifact واقعی اشتباه نگیرید.

از همین پوشه اجرا کنید:

```text
python3 -m unittest -v
python3 deployment_gate.py --fixture synthetic_release_scenarios.json --output /tmp/ch69-results.json
cmp /tmp/ch69-results.json results.json
```

CLI سه سناریو را به‌طور قطعی گزارش می‌کند: rollout سالم تا ۱۰۰٪، توقف/rollback ساختگی پس از نقض آستانهٔ p95 در مرحلهٔ ۲۵٪، و مسدودشدن candidate با provenance تأییدنشده. آستانه‌ها و درصدهای ۵/۲۵/۱۰۰ فقط policy همین fixture هستند؛ توصیهٔ عمومی یا SLO محصول نیستند.

## smoke service محلی

در یک ترمینال از همین پوشه:

```text
python3 local_stub.py --host 127.0.0.1 --port 8765 --release-id demo-r4
```

در ترمینال دوم، فقط به `127.0.0.1` درخواست بفرستید:

```text
curl http://127.0.0.1:8765/healthz
curl http://127.0.0.1:8765/version
curl -X POST http://127.0.0.1:8765/predict -H 'Content-Type: application/json' -d '{"sample_id":"synthetic-001"}'
```

سرور عمداً فقط به loopback bind می‌شود؛ ورودی `/predict` باید یک `sample_id` ساختگی داشته باشد و پاسخ صریحاً `model_execution: false` می‌دهد. برای پایان، `Ctrl+C` بزنید. آزمون‌های HTTP خودکار نیز از پورت loopback تصادفی استفاده می‌کنند؛ این درخواست‌ها از sandbox بیرون نمی‌روند.

## قرارداد و خواندن خروجی

- مجموعهٔ اجزا شامل سرویس، مدل، tokenizer، preprocessing و runtime است. هر scenario از یک manifest ساختگی، شناسهٔ build، digest محتوایی، provenance، وضعیت gate و شاهد rollout استفاده می‌کند.
- preflight، completeness و hash manifest را دوباره محاسبه می‌کند؛ provenance باید به همان digest اشاره کند. در production فرضی، approval و سازگاری رو به عقب برای مسیر بازگشت لازم‌اند.
- پس از preflight، مرحله‌های traffic با حداقل نمونه، error rate و p95 مقایسه می‌شوند. کمبود نمونه به `hold` می‌رسد؛ نقض سلامت به `rolled_back` برمی‌گردد؛ تکمیل همهٔ gateها `promoted` می‌دهد.
- `results.json` دارای SHA-256 بایت‌های خام fixture است. ویرایش fixture، hash مورد انتظار را تغییر می‌دهد؛ CLI را دوباره اجرا و مقایسه را آگاهانه به‌روزرسانی کنید.

## محدودیت و ایمنی

این شبیه‌ساز CI runner، registry، signer/verifier واقعی SLSA، scanner زنجیرهٔ تأمین، container، orchestrator، canary controller، database migration یا rollback عملیاتی نیست. hash canonical فقط شکل یک policy gate را تمرین می‌دهد؛ صحت builder، امضا یا اصالت نرم‌افزار را ثابت نمی‌کند. داده‌های health از fixture ثابت می‌آیند؛ هیچ مدل ارزیابی یا inference نشده است. HTTP stub یک سرویس محلی واقعی است، ولی inference را تقلید نمی‌کند و برای شبکه یا production طراحی نشده است. هیچ قیمت ابری یا برآورد TCO در خروجی پروژه وجود ندارد. از secret، prompt واقعی یا دادهٔ شخصی استفاده نکنید.
