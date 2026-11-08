# فصل ۶۰: ردیابی آزمایش و ابزارهای MLOps

این پروژه یک تمرین آفلاین و کاملاً ساختگی برای ثبت پیکربندی، سنجه‌ها، منشأ Git و artifact است. چهار نقطهٔ مصنوعی با یک رگرسیون خطی کوچک اجرا می‌شوند؛ دادهٔ واقعی، مدل ازپیش‌آموزش‌دیده، GPU و benchmark وجود ندارد.

## محیط آزموده‌شده

- CPython 3.13.16 روی Linux x86-64
- `mlflow==3.18.0` با backend محلی SQLite
- `wandb==0.31.0` در حالت `offline`، بدون ورود یا همگام‌سازی
- `PyYAML==6.0.3` فقط برای آزمون ایستای manifest نمونه

`requirements.txt` وابستگی مستقیم و `requirements-lock-linux-py313.txt` قفل کامل محیط آزموده‌شده است. قفل برای Linux x86-64 و CPython 3.13 ساخته شده و به‌جای قفل چندسکویی معرفی نمی‌شود. `environment.json` نسخه‌ها و محدودیت‌های ابزار را ثبت می‌کند؛ `results.json` خلاصهٔ اعتبارسنجی انتشار است، نه یک run database قابل‌واردکردن.

## اجرا

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-lock-linux-py313.txt
python -m pip check

python experiment_ops.py --backend manifest --output /tmp/ch60-manifest
python experiment_ops.py --backend mlflow --output /tmp/ch60-mlflow
python experiment_ops.py --backend wandb-offline --output /tmp/ch60-wandb
python -m unittest -v
```

برای هر اجرا `run.json` و `model.json` نوشته می‌شود. اجرای `mlflow` پایگاه SQLite و artifact را فقط در همان پوشهٔ خروجی می‌سازد. اجرای `wandb-offline` دادهٔ run و artifact را محلی نگه می‌دارد؛ برنامه `wandb sync` را اجرا نمی‌کند و API key نمی‌خواهد. adapter حتی اگر محیط والد روی online باشد، برای همین نمونه offline را تحمیل می‌کند؛ خروجی را پس از بررسی و بر اساس سیاست نگهداری پاک کنید.

کد در checkout، commit و وضعیت dirty بودن Git را ثبت می‌کند. چون image نمونه `.git` را کپی نمی‌کند، pipeline ساخت می‌تواند metadata غیرمحرمانه را با `SOURCE_COMMIT`, `SOURCE_WORKTREE_CLEAN`, `SOURCE_STATUS_SHA256` و `SOURCE_TRACKED_DIFF_SHA256` به build args بدهد. این مقادیر باید از وضعیت واقعی همان build به‌دست آیند؛ مقدار پیش‌فرض `unknown` عمداً ادعای منشأ نمی‌کند. هرگز secret را در build arg یا image وارد نکنید.

## مرز ادعا

کاهش MSE روی همین چهار نمونهٔ مصنوعی فقط آزمون قرارداد اجرایی است؛ کیفیت تعمیم، آموزش یک مدل کاربردی، کارایی، استقرار تولیدی یا صحت ذخیره‌سازی توزیع‌شده را نشان نمی‌دهد. `job.yaml` و `Dockerfile` نمونه‌های ایستا هستند: در محیط آزمون Docker، Podman یا Kubernetes اجرا نشده‌اند. image در `job.yaml` عمداً از دامنهٔ رزروشدهٔ `.invalid` و digest صفر استفاده می‌کند تا اشتباهاً قابل‌استقرار نباشد؛ باید پیش از کاربرد واقعی با image واقعی و digest بررسی‌شده جایگزین شود.

`emptyDir` در Job موقت است. برای خروجی ماندگار، PVC یا object store و رویهٔ مجاز انتقال/حذف داده را جداگانه طراحی کنید. هرگز API key یا اطلاعات حساس را در کد، image، log، fixture، artifact یا Git commit قرار ندهید.
