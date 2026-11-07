# گزارش ممیزی فصل ۶۰ — ردیابی آزمایش و ابزارهای MLOps

## دامنه و تاریخ

این گزارش برای فصل محلی ۱۴ / سراسری ۶۰ جلد چهارم است. منابع زنده و release noteها در ۷ نوامبر ۲۰۲۶ بررسی شدند. این نسخه فقط وب/PWA و Markdown است؛ PDF و EPUB تولید یا آزموده نشده‌اند.

## نسخه‌ها و ورودی

- CPython `3.13.16` روی Linux x86-64
- `mlflow==3.18.0`، `wandb==0.31.0` و `PyYAML==6.0.3`
- قفل کامل `requirements-lock-linux-py313.txt`: ۱۰۱ توزیع، SHA-256 برابر `a759b357a25c46c07256ce9a18bdc3c7c0f4f1276f3c1d374e284d278ba45ced`؛ مخصوص Linux x86-64 و CPython 3.13
- fixture ساختگی چهارردیفی: `v4-ch14-synthetic-linear-v1`، SHA-256 برابر `81989e3ae534cade6f4e77742cb3fae01649247956962559720e75b093f1a260`
- digest مرجع base image از Docker Hub: `python:3.13.16-slim@sha256:cf50a4f6ac4f026458b08d5222023d700ac806410dff5e9ca8728fa44f2b850f`؛ فقط در Dockerfile ثابت شده و image ساخته نشده است.

جزئیات در `projects/60-mlops/environment.json` و `results.json` ثبت شده‌اند.

## نتایج اجرای واقعی محلی

- `python -m pip check`: موفق؛ هیچ نیازمندی شکسته گزارش نشد.
- `python -m unittest -v`: **۱۶/۱۶ آزمون unit موفق**.
- اجرای CLI در حالت `manifest`: fixture و run manifest ساخته شدند؛ MSE آغازین `21.0` و پس از پنج گام `0.09078731868784178` شد.
- اجرای `mlflow`: metadata و سنجه‌ها در SQLite محلی ثبت شدند؛ آزمون `MlflowClient` پارامتر، سنجه و دو artifact (`model.json` و `run.json`) را خواند. tracking server یا همگام‌سازی راه‌اندازی نشد.
- اجرای `wandb-offline`: run و artifact در پوشهٔ محلی W&B ساخته شدند؛ API key لازم نبود، همگام‌سازی یا `wandb sync` اجرا نشد و آزمون وجود فایل `.wandb` را بررسی کرد. آزمون حتی وقتی محیط والد `WANDB_MODE=online` و یک کلید آزمایشیِ جعلی داشت، offline اجباری و بازیابی محیط والد را تأیید کرد.
- `Dockerfile`: آزمون static برای digest، ساخت چندمرحله‌ای، کاربر غیرریشه و نبودن کلید در دستورهای `ARG`/`ENV` موفق شد؛ build، scan یا اجرای image انجام نشد.
- `job.yaml`: parse با PyYAML و آزمون static برای Job، deadline، retry، TTL، منابع، `emptyDir` و security context موفق شد؛ schema کامل Kubernetes یا cluster زنده آزموده نشد.

در یکی از آزمون‌های MLflow، یک `SADeprecationWarning` از زنجیرهٔ SQLAlchemy نمایش داده شد؛ آزمون و عملیات محلی موفق ماندند و هشدار پنهان نشده است.

## ساخت کتاب و آزمون مرورگر

`build_volume4.py` فصل را با شناسهٔ پایدار محلی ۱۴ / سراسری ۶۰ افزود؛ پس از اصلاح متن همان آخرین draft محلی، `--refresh-last-draft` فقط فصل منتشرنشدهٔ ۱۴ را به‌روز کرد و شناسه‌های بخش‌ها را حفظ کرد. اجرای builder دوم «already matches» بود. `check_volume4.py` موفق شد: **۱۴/۱۵ فصل، ۳۱۹ بخش، ۵۸ عبارت MathML دسترس‌پذیر و پیوست‌های اجرایی دقیق**.

`test_volume4.py` موفق شد در ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل؛ ۱۵۱ مسیر لازم را از cache آفلاین خواند و appendix فصل ۶۰ را دقیقاً با فایل پروژه مقایسه کرد. `test_mobile_layout.py` نیز در ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل موفق شد و ۱٬۱۲۴ بخش را وارسی کرد؛ جلد چهارم ۸۹۷ بند نثری، ۵۲۶ بند تورفته، ۵۸ MathML و ۹ کپشن داشت. درخواست‌های 404 در خروجی مرورگر به assetهای قدیمیِ خارج از sparse checkout مربوط بودند؛ فایل‌های ناموجود دست‌نخورده ماندند، هر ۱۵۱ مسیرِ لازم موجود بود و همهٔ مسیرهای فصل ۶۰ پاسخ ۲۰۰ دادند.

## GitHub Actions و نسخهٔ زنده

فصل در commit مستقل `83263810ea3b8c0ff024e1ffaf41f7411273183a` با push عادی روی `gh-pages` منتشر شد؛ remote و tree پس از push تأیید شدند.

- [Volume 4 audit — run 42345596107](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42345596107): **موفق**؛ شامل پروژهٔ ۶۰، builder idempotence، آزمون مرورگر/آفلاین و layout.
- [Volume 3 audit — run 42345596099](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42345596099): **موفق**.
- [Volume 2 audit — run 42345596128](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42345596128): **موفق**.
- [Pages build and deployment — run 42345595760](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42345595760): **موفق**.
- [Volume 1 audit روی commit فصل — run 42345596131](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42345596131) و [اجرای دوباره روی commit گزارش — run 42346101802](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42346101802): هر دو در گام «Run each project test suite» با exit code 1 پایان یافتند؛ ساختار کتاب موفق بود. بررسی workflow نشان داد حلقهٔ عمومی Volume 1 فصل ۶۰ را با محیط عمومی اجرا می‌کرد، درحالی‌که `requirements.txt` ریشه MLflow و W&B را نصب نمی‌کند. بازتولید محلی همان اجرای فصل ۶۰ در آن محیط، ۱۴ آزمون را گذراند و دو آزمون tracker با `ModuleNotFoundError` برای `mlflow` و `wandb` شکست خوردند؛ محیط پین‌شدهٔ Volume 4 همان ۱۶ آزمون را موفق اجرا می‌کند. commit گزارش `05838426388c9a3c33a7cf28faf995b5997d313a` نیز همین وضعیت را تکرار کرد: Volume 2، Volume 3، Volume 4 و Pages موفق شدند و Volume 1 دوباره در همان گام شکست خورد. فایل `.github/workflows/volume1-audit.yml` در اصلاح بعدی به‌روز شده تا فصل ۶۰ را به workflow پین‌شدهٔ Volume 4 واگذار کند؛ CI آن اصلاح هنوز در انتظار است.

نسخهٔ زندهٔ [اپ/PWA](https://mvbabababak-spec.github.io/fa-academy/) پس از موفقیت Pages با HTTP 200 بررسی شد. `index.html`، `README.md`، `data.json`، `sw.js`، `volume-4-full-fa.md`، متن و پاسخ‌نامهٔ فصل ۶۰، پروژه و SVG فصل ۱۴ همگی HTTP 200 دادند و بایت‌های منتشرشده با SHA-256 فایل محلی یکسان بودند. هش‌های کلیدی: `data.json` `1b0a8291d446562a1342b3209f21e32dedd5a2f4f0e08029a374508c43364e98`؛ `sw.js` `bb98f6f7420448618125a01ae80ed61535dcc762379c33bfc23b8564f8a1df77`؛ `volume-4-full-fa.md` `65c28b9741c98f313811230fc084b3b9558371d2eccfbf4210574852df30e462`؛ فصل ۶۰ `6ff7741158fde22c7b6c1b2cd5c6bb34a2d491619463d8346a6bff16f728462b`؛ پاسخ‌نامه `3392eadfb750603de3c2e268b6c6ab0c9926b7494ceb0e33babbe8207cd6c09a`.

## محدودیت ادعا

هیچ دادهٔ واقعی، مدل pretrained، آموزش کاربردی، GPU، benchmark، کیفیت تعمیم، Docker build، Kubernetes cluster، tracking server، upload یا W&B sync آنلاین آزموده نشده است. چهار نقطهٔ مصنوعی فقط قرارداد اجرایی و ثبت lineage را بررسی می‌کنند؛ کاهش MSE ادعای کیفیت مدل نیست. `job.yaml` به‌عمد از دامنهٔ رزروشدهٔ `.invalid` و digest صفر استفاده می‌کند و deployable نیست تا با image واقعی و digest بررسی‌شده جایگزین شود.

## منابع اصلی

- [MLflow 3.18.0 release](https://github.com/mlflow/mlflow/releases/tag/v3.18.0)، منتشرشده در ۴ نوامبر ۲۰۲۶؛ [Tracking Quickstart](https://mlflow.org/docs/latest/ml/tracking/quickstart/) و [Tracking Server Architecture](https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/).
- [W&B 0.31.0 release](https://github.com/wandb/wandb/releases/tag/v0.31.0)، منتشرشده در ۱۶ اکتبر ۲۰۲۶؛ [experiments](https://docs.coreweave.com/products/wandb/ref/python/experiments)، [environment variables](https://docs.coreweave.com/products/wandb/track/environment-variables) و [Artifacts](https://docs.coreweave.com/products/wandb/artifacts).
- [Docker Build Best Practices](https://docs.docker.com/build/building/best-practices/) و [Docker Hub Python tag metadata](https://hub.docker.com/v2/repositories/library/python/tags/3.13.16-slim).
- [Kubernetes Workloads](https://kubernetes.io/docs/concepts/workloads/)، [GPU Scheduling](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)، [Git record changes](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository) و [GitHub Actions Secure Use](https://docs.github.com/en/actions/reference/security/secure-use).
