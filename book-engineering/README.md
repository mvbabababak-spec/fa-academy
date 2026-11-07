# هنر و علم ساخت هوش — Babak & Ai

جلد اول ۲۱ فصل برنامه‌ریزی‌شده دارد. فصل‌های ۱ تا ۲۱ در مخزن انتشار آماده‌اند؛ فصل‌های بعدی هنوز آماده نیستند.

- متن فصل‌ها در `chapters/` و پروژه‌های اجرایی در `projects/` است.
- تصاویر جدید کتاب و جلد آن WebP هستند؛ اسکریپت‌های ساخت تصاویر در فایل‌های `create_ch*.py` قرار دارند.
- بازتولید محتوای فصل‌های ۲۰ تا ۲۱: از ریشه مخزن `python book-engineering/build_chapter.py`؛ نیازمند Python و کتابخانه Mistune 3. قبل از انتشار داده‌های دیگر و خروجی تولیدشده را بررسی کنید.
- پروژه‌های فصل‌های ۸ تا ۱۰ با Python 3.13.16 اجرا شده‌اند. پروژه فصل ۸ شبیه‌سازی CPU است و یک اجرای چند GPU واقعی نیست.
- نقشه کل مجموعه: `../BOOK_ROADMAP_FA.md`

- پروژه‌های فصل‌های ۱۱ تا ۱۳ با Python 3.13.16 آزمایش شدند؛ فصل ۱۳ با Git 2.47.3 فقط محلی و بدون شبکه اجرا شد.

- فصل ۱۴ و ۱۶ با Python 3.13.16 و کتابخانه استاندارد تست شدند؛ فصل ۱۵ با NumPy 2.3.5، Pandas 2.2.3 و Matplotlib 3.11.2 بررسی شد؛ رابط Jupyter آزموده نشده است. نمودار فصل ۱۵ با اجرای پروژه تولید می‌شود.

- پیوست‌های تکمیلی فصل‌های ۱۴ تا ۱۶ و پروژه‌های مستقل در `projects/14-testing-sql/`، `projects/15-data-analysis-supplement/` و `projects/16-algebra-supplement/` قرار دارند. نوت‌بوک فصل ۱۵ با nbclient اجرا شد؛ رابط JupyterLab جداگانه آزموده نشده است.

- فصل‌های ۱۷ تا ۱۹ با Python 3.13.16، فصل ۱۷ با NumPy 2.3.5، روی CPU اجرا شدند.
- قانون تولید: پیش از شروع هر فصل، نسخهٔ مخزن و وجود محتوای فصل بررسی شود؛ فصل تکمیل‌شده دوباره تولید نشود. پیش از نگارش هر فصل، ساختار کل پنج جلد و جایگاه فصل در نقشه بازخوانی شود.

- پروژه‌های فصل ۲۰ و ۲۱ با Python 3.13.16 و کتابخانه استاندارد روی CPU اجرا و هرکدام با چهار آزمون بررسی شدند. تکمیل فصل‌ها به معنای آماده‌بودن PDF یا کل مجموعه نیست.

## ساخت و انتشار جلد دوم

جلد دوم شامل فصل‌های محلی ۱–۱۱ (سراسری ۲۲–۳۲) است. انتشار وب/PWA است؛ PDF و EPUB تولید و آزموده نشده‌اند. فایل قابل دریافت `../volume-2-full-fa.md` است. از ریشه مخزن و پس از نصب Mistune 3.4.0 به ترتیب `python book-engineering/build_volume2.py`، `python book-engineering/append_volume2_04_06.py`، `python book-engineering/append_volume2_07_09.py`، `python book-engineering/append_volume2_10_11.py` را اجرا کنید. این سازنده‌ها فصل موجود ناسازگار را بازنویسی نمی‌کنند؛ برای اصلاح محتوای منتشرشده ابتدا منبع و داده همگام، نسخه SW افزایش و تست‌ها اجرا شوند. `python book-engineering/check_volume2.py` و `python book-engineering/test_volume2.py` کنترل ساختار و مرورگر را انجام می‌دهند؛ دومی Playwright و Chromium می‌خواهد. برای حفظ تاریخچه، توضیحات پیشین این فایل به زمان نگارش خود مربوط‌اند.

**رده‌بندی پروژه‌ها:** ۱۱ پروژه فصل‌های جلد دوم تمرین‌های مستقل اجرایی آن فصل‌ها هستند؛ پروژه تلفیقی پایان بخش، فعالیت ارزیابی جامع است و الزاماً پروژه جدید یا پوشه مستقل نیست؛ ۲۰ پروژه اصلی جدول نقشه مسیرهای سراسری مجموعه‌اند و برخی با پروژه‌های فصلی هم‌پوشانی دارند. این دسته‌ها را نباید با هم جمع زد یا هم‌ارز شمرد.

## ساخت و انتشار تدریجی جلد سوم

طبق نقشهٔ کامل پنج‌جلدی، جلد سوم ۱۴ فصل محلی دارد که با فصل‌های سراسری ۳۳–۴۶ متناظرند؛ هر ۱۴ فصل منتشر و آزموده شده‌اند. محلی‌های ۱–۷ (سراسری ۳۳–۳۹) توکن‌سازی، خانواده‌های Attention/Transformer و چندوجهی را پوشش می‌دهند؛ محلی‌های ۸–۹ (۴۰–۴۱) آماده‌سازی داده و نخستین مدل زبانی کوچک‌اند؛ محلی‌های ۱۰–۱۴ (۴۲–۴۶) طراحی Mini GPT، ممیزی corpus، برنامهٔ پیش‌آموزش و بازیابی، دقت عددی و مقیاس آموزش را می‌پوشانند. فصل ۴۲ آموزش یا کیفیت Mini GPT را ادعا نمی‌کند؛ فصل ۴۳ ابزارش corpus واقعی یا مجوز آموزشی نمی‌سازد؛ فصل ۴۴ smoke exercise روی fixture کوچک است، نه پیش‌آموزش صنعتی یا benchmark؛ فصل ۴۵ cast/quantization را در نمونه‌های کوچک می‌سنجد، نه کیفیت یا سرعت مدل واقعی؛ فصل ۴۶ correctness fixture CPU/Gloo را می‌سنجد، نه GPU/cluster یا benchmark. فصل‌های منتشرشده را بازنویسی نکنید.

منبع هر فصل در `chapters/`، پاسخ‌نامه در `answers/`، و پروژهٔ مستقل در `projects/` قرار دارد. فصل ۴۲: `chapters/42-mini-gpt.md`، `answers/42-mini-gpt-fa.md` و `projects/42-mini-gpt-design/`؛ نمودارش از `diagrams/v3-ch10-mini-gpt-budget.svg` و `create_v3_ch10_image.py` به WebP محلی تبدیل می‌شود. فصل ۴۳: `chapters/43-corpus.md`، `answers/43-corpus-fa.md` و `projects/43-corpus-audit/`؛ نمودارش از `diagrams/v3-ch11-corpus-audit.svg` و `create_v3_ch11_image.py` به WebP محلی تبدیل می‌شود. فصل ۴۴: `chapters/44-pretraining.md`، `answers/44-pretraining-fa.md` و `projects/44-pretraining/`؛ نمودارش از `diagrams/v3-ch12-pretraining.svg` و `create_v3_ch12_image.py` به WebP تبدیل می‌شود. پروژهٔ ۴۴ از history واقعی هر run نمودار `loss_curve.svg` می‌سازد. `volume-3-full-fa.md` نسخهٔ Markdown فصل‌های موجود را جمع می‌کند. پروژهٔ ۴۲ با Python 3.13.16 و PyTorch 2.6.0+cpu یازده آزمون و CLI را پاس می‌کند؛ آموزش، کیفیت یا peak VRAM را ارزیابی نمی‌کند. پروژهٔ ۴۳ با Python 3.13.16 و کتابخانهٔ استاندارد، ۱۲ آزمون و CLI آفلاین را پاس می‌کند؛ متن fixtureها ساختگی است و ابزار حقوق، کیفیت زبانی یا نبود آلودگی را تأیید نمی‌کند. پروژهٔ ۴۴ با Python 3.13.16 و PyTorch 2.6.0+cpu ده آزمون و اجرای کامل/قطع‌و‌ادامه را پاس می‌کند؛ منحنی زیان و test metric فقط خروجی fixture کوچک‌اند و benchmark واقعی نیستند.

برای ارجاع سریعِ دو فصل پایانی: [فصل ۴۵](chapters/45-precision.md)، [پاسخ‌نامهٔ ۴۵](answers/45-precision-fa.md)، [README پروژهٔ ۴۵](projects/45-precision/README.md)؛ [فصل ۴۶](chapters/46-scale-training.md)، [پاسخ‌نامهٔ ۴۶](answers/46-scale-training-fa.md)، [README پروژهٔ ۴۶](projects/46-scale-training/README.md). هر پروژه از متن فصل جداست؛ پیوست اجرایی Markdown باید بایت‌به‌بایت با فایل پروژهٔ آزموده‌شده بماند. [Contact sheet چهارده شکل](../review-volume-3/volume-3-contact-sheet.webp)، [راهنمای سبک جلد سوم](VOLUME3_STYLE_GUIDE_FA.md)، [گزارش نهایی انتشار](VOLUME3_FINAL_RELEASE_FA.md) و [گزارش تایپوگرافی نثر سه جلد](BOOK_TYPOGRAPHY_RELEASE_FA.md) ثبت بصریات، تصمیم‌های قالب و نتایج گیت‌ها را دارند.

### ساخت، آزمون و ممیزی

از ریشهٔ مخزن، ممیزی انتشار با Python 3.13.x و وابستگی‌های دقیق `requirements.txt` انجام می‌شود. نصب و اجرای گیت‌های ساختار:

```bash
python -m pip install -r requirements.txt
python book-engineering/rebuild_volume3_targets.py
python book-engineering/build_volume3.py
python book-engineering/check_volume3.py
```

`rebuild_volume3_targets.py` در حالت پیش‌فرض فقط منبع را با `data.json` تطبیق می‌دهد؛ فقط پس از بازبینی تغییرهای هدف‌دار، `--write` را برای همگام‌سازی HTML فصل‌های جلد سوم به کار ببرید. نسخه‌های مستقیم manifest: NumPy 2.3.5، scikit-learn 1.6.1، pandas 2.2.3، Matplotlib 3.11.2، Pillow 13.0.0، Mistune 3.4.0، Playwright 1.64.1 و PyTorch 2.6.0 از wheel CPU. هر سه workflow جلدها از همین manifest مشترک استفاده می‌کنند؛ نسخهٔ Python ممیزی/CI برابر 3.13 است.

سازنده فقط فصل‌های دارای منبع پیوسته از شمارهٔ ۱ را اضافه می‌کند و شناسه‌های پایدار می‌سازد؛ فصل منتشرشدهٔ ناسازگار را بازنویسی نمی‌کند. گزینهٔ `--refresh-last-draft` فقط برای آخرین draft محلیِ هنوز منتشرنشده است و پس از کنترل remote و حفظ همهٔ IDها مجاز است.

پروژه‌های فصل‌های ۳۳ تا ۴۶ را جداگانه با `python -m unittest discover -v` از پوشهٔ همان پروژه اجرا کنید. پروژهٔ فصل ۴۰ Python 3.11+ و کتابخانهٔ استاندارد می‌خواهد. پروژهٔ فصل ۴۱ به Python 3.11+ و PyTorch 2.6.x CPU نیاز دارد؛ برای مقایسهٔ تنظیمات از `--skip-test` استفاده کنید و فقط اجرای نهایی را بدون آن انجام دهید. ۲۲ آزمون آن، قرارداد داده و hash، واژگان و زمینه، ابعاد/زیان/گرادیان، seed، checkpoint، تولید و CLI را می‌سنجند؛ کیفیت زبان، تعمیم، حقوق داده یا ایمنی محصول را اثبات نمی‌کنند. پروژهٔ فصل ۴۲ با Python 3.11+ و PyTorch 2.6.x CPU نیازمندی دارد؛ یازده آزمون، شمار پارامتر، شکل logits، عدم نشت آینده، رد prefix چپ‌pad/all-pad و برآوردهای tensor را می‌سنجند. `python book-engineering/projects/42-mini-gpt-design/mini_gpt_design.py --context-sweep` خروجی بودجهٔ پیش‌فرض را بازتولید می‌کند؛ peak حافظه، benchmark یا کیفیت تولید را ثابت نمی‌کند. پروژهٔ فصل ۴۳ در `projects/43-corpus-audit/` به Python 3.11+ و کتابخانهٔ استاندارد نیاز دارد؛ ۱۲ آزمون و CLI، manifest ساختگی، فیلترهای پرچمی، near-duplicate و overlap سطحی با ارزیابی جدا را می‌سنجند. خروجی آن فقط report است؛ هیچ متنی را خودکار حذف یا برای آموزش صادر نمی‌کند، و مجوز، privacy، کیفیت زبانی یا پاک‌بودن benchmark را اثبات نمی‌کند. پروژهٔ فصل ۴۴ به Python 3.11+ و PyTorch 2.6.x CPU نیاز دارد؛ ۱۰ آزمون، schedule، microbatch ناقص، accumulation، checkpoint/resume، data/config identity و SVG خروجی را می‌سنجند. CLI از fixture فصل ۴۰ history/metrics/checkpoint/`loss_curve.svg` می‌سازد؛ test فقط پس از run کامل ارزیابی می‌شود. خروجی‌ها معیار کیفیت یا scaling مدل نیستند. پروژهٔ فصل ۴۵ در `projects/45-precision/` به Python 3.11+ و PyTorch 2.6.x CPU نیاز دارد؛ ۱۰ آزمون metadata قالب، cast/underflow/overflow، CPU BF16 autocast، affine int8، scale per-group، saturation و JSON را کنترل می‌کنند. `precision_lab.py` گزارش JSON قطعی می‌سازد؛ cast FP8 روی CPU پشتیبانی accelerator یا GEMM سریع را ثابت نمی‌کند، و کدهای زیر ۸ bit در demo واقعاً bit-pack نمی‌شوند؛ این پروژه latency، دقت مدل، مزیت task یا benchmark را ارزیابی نمی‌کند. پروژهٔ فصل ۴۶ در `projects/46-scale-training/` به Python 3.11+ و PyTorch 2.6.x CPU/Gloo نیاز دارد؛ ده آزمون activation recomputation، بایت saved-tensorهای hook، گرادیان DDP با shardهای نابرابر، fingerprint و JSON را کنترل می‌کنند. اجرای CLI با fixture دوپردازه‌ای correctness را می‌سنجد، نه GPU/cluster، سرعت، peak memory یا کیفیت مدل. دستور نصب و محدودیت‌ها در README هر پروژه است.

آزمون مرورگر جلد سوم: `python book-engineering/test_volume3.py`؛ آزمون layout کل کتاب: `python book-engineering/test_mobile_layout.py`. هر دو به Playwright 1.64.1، Chromium و Pillow 13.0.0 نیاز دارند. تست جلد سوم ناوبری، شناسه‌های پایدار، جست‌وجو، MathML دسترس‌پذیر، overflow، ۱۴ تصویر و ۱۱۵ فایل آفلاین را در عرض‌های ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل بررسی می‌کند؛ آزمون موبایل ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل را می‌سنجد. آزمون موبایل همچنین جهت RTL، تراز نثر، تورفتگی بند، استثنای کپشن/MathML و محدودبودن قاعده به جلدهای سری اصلی را در کل ۱٬۱۲۴ بخش وارسی می‌کند؛ فصل‌های ۴۷–۶۰ به‌ترتیب ۱۹، ۲۱، ۲۳، ۲۴، ۲۳، ۳۰، ۲۷، ۲۲، ۲۱، ۲۱، ۲۰، ۲۲، ۲۲ و ۲۴ بخش دارند. Service Worker کنونی `fa-academy-v95` است؛ فهرست آفلاین جلد چهارم ۱۵۱ دارایی شامل فصل‌های ۵۷–۶۰، پاسخ‌نامه‌ها، گزارش‌ها، نمودارها و پروژه‌ها را دارد. گردش‌کار `.github/workflows/volume3-audit.yml` checkerها، پروژه‌های جلد سوم، idempotence سازنده، آزمون مرورگر جلد دوم/سوم و layout موبایل را اجرا می‌کند.

## جلد چهارم — انتشار مرحله‌ای

جلد چهارم طبق نقشه ۱۵ فصل محلی (سراسری ۴۷–۶۱) دارد. چهارده فصل محلی ۱–۱۴ (سراسری ۴۷–۶۰) جداگانه تکمیل، آزموده و منتشر شده‌اند: Continued Pretraining/Instruction Tuning/SFT؛ PEFT/LoRA؛ مدل پاداش، RLHF/PPO، DPO، GRPO، RLAIF و Constitutional AI؛ دادهٔ مصنوعی، تقطیر، Curriculum Learning، محاسبهٔ زمان آزمون و مدل‌های استدلالی؛ رمزگذار تصویر، Vision Transformer و هم‌ترازی متن–تصویر؛ صوت/گفتار، بازشناسی و تولید گفتار، Audio-Language و ارزیابی؛ تولید تصویر/ویدئو و Diffusion؛ برآورد حافظه/FLOPs برای استنتاج، Fine-tuning و آموزش از صفر؛ طراحی آزمایشگاه از شخصی تا سازمانی؛ بودجه/TCO/NPV، خرید/اجاره/ابر، ریسک عرضه و توسعهٔ مرحله‌ای؛ مقایسه و راه‌اندازی Python، PyTorch، JAX و TensorFlow؛ خط لولهٔ Hugging Face با Transformers، Datasets، Tokenizers و Accelerate؛ CUDA/ROCm/Triton و مقیاس‌پذیری DeepSpeed/FSDP/Megatron-LM؛ و ردیابی اجرا با MLflow/W&B، منشأ Git، قفل محیط، Docker و Kubernetes. فصل ۶۱ دربارهٔ سرو و بهینه‌سازی استنتاج هنوز در نقشه است. هر فصل منبع، پاسخ‌نامه، گزارش ممیزی و پروژهٔ جدا دارد. فصل‌های منتشرشده را دوباره تولید یا بازنویسی نکنید. پیش از هر فصل، کل نقشه و شاخه/داده بررسی شود؛ هر فصل به‌صورت مستقل کامل، آزموده و push شود.

فایل‌های فصل ۴۷: `chapters/47-posttraining.md`؛ پاسخ‌نامهٔ مستقل `answers/47-posttraining-fa.md`؛ گزارش اجرا/محدودیت `chapters/47-audit-report-fa.md`؛ پروژهٔ `projects/47-instruction-tuning/`؛ نمودار accessible SVG در `diagrams/v4-ch01-posttraining.svg`. فصل ۴۸: `chapters/48-peft.md`، `answers/48-peft-fa.md`، `chapters/48-audit-report-fa.md`، `projects/48-peft-lab/` و `diagrams/v4-ch02-peft.svg`. فصل ۴۹: `chapters/49-preference-optimization.md`، `answers/49-preference-optimization-fa.md`، `chapters/49-audit-report-fa.md`، `projects/49-preference-lab/` و `diagrams/v4-ch03-preference.svg`. فصل ۵۰: `chapters/50-synthetic-reasoning.md`، `answers/50-synthetic-reasoning-fa.md`، `chapters/50-audit-report-fa.md`، `projects/50-synthetic-reasoning/` و `diagrams/v4-ch04-synthetic-reasoning.svg`. فصل ۵۱: `chapters/51-vision-models.md`، `answers/51-vision-models-fa.md`، `chapters/51-audit-report-fa.md`، `projects/51-vision-lab/` و `diagrams/v4-ch05-vision.svg`. فصل ۵۲: `chapters/52-audio-models.md`، `answers/52-audio-models-fa.md`، `chapters/52-audit-report-fa.md`، `projects/52-audio-lab/` و `diagrams/v4-ch06-audio.svg`. فصل ۵۳: `chapters/53-image-video-generation.md`، `answers/53-image-video-generation-fa.md`، `chapters/53-audit-report-fa.md`، `projects/53-diffusion-lab/` و `diagrams/v4-ch07-diffusion.svg`. فصل ۵۴: `chapters/54-resource-estimation.md`، `answers/54-resource-estimation-fa.md`، `chapters/54-audit-report-fa.md`، `projects/54-resource-estimation/` و `diagrams/v4-ch08-resource-estimation.svg`. فصل ۵۵: `chapters/55-ai-lab-design.md`، `answers/55-ai-lab-design.md`، `chapters/55-audit-report-fa.md`، `projects/55-ai-lab-design/` و `diagrams/v4-ch09-lab-design.svg`. فصل ۵۶: `chapters/56-ai-compute-budget.md`، `answers/56-ai-compute-budget-fa.md`، `chapters/56-audit-report-fa.md`، `projects/56-ai-compute-budget/` و `assets/images/babak-ai/v4-ch10-tco-timeline.svg`. `data.json` جلد چهارم را پس از جلد سوم قرار می‌دهد. فصل ۵۷: `chapters/57-ml-frameworks.md`، `answers/57-ml-frameworks-fa.md`، `chapters/57-audit-report-fa.md`، `projects/57-framework-lab/` و `diagrams/v4-ch11-framework-selection.svg`. فصل ۵۸: `chapters/58-huggingface-stack.md`، `answers/58-huggingface-stack-fa.md`، `chapters/58-audit-report-fa.md`، `projects/58-huggingface-stack/` و `diagrams/v4-ch12-huggingface-stack.svg`. فصل ۵۹: `chapters/59-gpu-systems.md`، `answers/59-gpu-systems-fa.md`، `chapters/59-audit-report-fa.md`، `projects/59-gpu-systems/` و `diagrams/v4-ch13-gpu-systems.svg`. فصل ۶۰: `chapters/60-mlops.md`، `answers/60-mlops-fa.md`، `chapters/60-audit-report-fa.md`، `projects/60-mlops/` و `diagrams/v4-ch14-mlops.svg`. `data.json` جلد چهارم را پس از جلد سوم قرار می‌دهد. `volume-4-full-fa.md` متن Markdown چهارده فصل منتشرشده را جمع می‌کند.

از ریشهٔ مخزن برای build و checker استفاده کنید:

```bash
python book-engineering/build_volume4.py
python book-engineering/check_volume4.py
(cd book-engineering/projects/47-instruction-tuning && python -m unittest discover -v)
python book-engineering/projects/47-instruction-tuning/sft_experiment.py \
  --mode audit --data book-engineering/projects/47-instruction-tuning/sample_sft.jsonl \
  --output /tmp/ch47-audit
(cd book-engineering/projects/48-peft-lab && python -m unittest discover -v)
python book-engineering/projects/48-peft-lab/peft_lab.py \
  --mode audit --fixture book-engineering/projects/48-peft-lab/sample_layers.json \
  --output /tmp/ch48-audit
python book-engineering/projects/48-peft-lab/peft_lab.py --mode toy-lora --output /tmp/ch48-toy
(cd book-engineering/projects/49-preference-lab && python -m unittest discover -v)
python book-engineering/projects/49-preference-lab/preference_lab.py \
  --mode audit --fixture book-engineering/projects/49-preference-lab/sample_preferences.jsonl \
  --output /tmp/ch49-audit
python book-engineering/projects/49-preference-lab/preference_lab.py \
  --mode toy-dpo --output /tmp/ch49-demo --steps 80 --seed 49
(cd book-engineering/projects/50-synthetic-reasoning && python -m unittest discover -v)
python book-engineering/projects/50-synthetic-reasoning/reasoning_lab.py \
  --mode audit --fixture book-engineering/projects/50-synthetic-reasoning/sample_traces.jsonl \
  --output /tmp/ch50-audit
python book-engineering/projects/50-synthetic-reasoning/reasoning_lab.py \
  --mode demo --fixture book-engineering/projects/50-synthetic-reasoning/sample_traces.jsonl \
  --output /tmp/ch50-demo
(cd book-engineering/projects/51-vision-lab && python -m unittest discover -v)
python book-engineering/projects/51-vision-lab/vision_lab.py \
  --mode audit --fixture book-engineering/projects/51-vision-lab/sample_embeddings.json \
  --output /tmp/ch51-audit
python book-engineering/projects/51-vision-lab/vision_lab.py \
  --mode demo --fixture book-engineering/projects/51-vision-lab/sample_embeddings.json \
  --output /tmp/ch51-demo
(cd book-engineering/projects/52-audio-lab && python -m unittest discover -v)
python book-engineering/projects/52-audio-lab/audio_lab.py \
  --mode audit --fixture book-engineering/projects/52-audio-lab/sample_transcripts.json \
  --output /tmp/ch52-audit
python book-engineering/projects/52-audio-lab/audio_lab.py \
  --mode demo --fixture book-engineering/projects/52-audio-lab/sample_transcripts.json \
  --output /tmp/ch52-demo
(cd book-engineering/projects/53-diffusion-lab && python -m unittest discover -v)
python book-engineering/projects/53-diffusion-lab/diffusion_lab.py \
  --mode audit --fixture book-engineering/projects/53-diffusion-lab/sample_mixture.json \
  --output /tmp/ch53-audit
python book-engineering/projects/53-diffusion-lab/diffusion_lab.py \
  --mode demo --fixture book-engineering/projects/53-diffusion-lab/sample_mixture.json \
  --output /tmp/ch53-demo --steps 200 --samples 64 --seed 53
(cd book-engineering/projects/55-ai-lab-design && python -m unittest discover -v)
python book-engineering/projects/55-ai-lab-design/lab_design_planner.py \
  --output /tmp/ch55-demo.json
(cd book-engineering/projects/56-ai-compute-budget && python -m unittest discover -v)
python book-engineering/projects/56-ai-compute-budget/budget_model.py \
  --fixture book-engineering/projects/56-ai-compute-budget/sample_budget.json \
  --output /tmp/ch56-results.json
(cd book-engineering/projects/57-framework-lab && python -m unittest discover -v)
python book-engineering/projects/57-framework-lab/framework_compare.py \
  --backend all --output /tmp/ch57-results.json
python -m venv /tmp/ch58-venv
/tmp/ch58-venv/bin/python -m pip install -r book-engineering/projects/58-huggingface-stack/requirements-cpu.txt
/tmp/ch58-venv/bin/python -m pip install -r book-engineering/projects/58-huggingface-stack/requirements-lock-linux-py313.txt
/tmp/ch58-venv/bin/python -m pip check
(cd book-engineering/projects/58-huggingface-stack && /tmp/ch58-venv/bin/python -m unittest discover -v)
/tmp/ch58-venv/bin/python book-engineering/projects/58-huggingface-stack/pipeline_demo.py --max-steps 2 --seed 58 --output /tmp/ch58-results.json
HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 /tmp/ch58-venv/bin/accelerate launch --cpu --num_processes 1 --num_machines 1 --mixed_precision no --dynamo_backend no book-engineering/projects/58-huggingface-stack/pipeline_demo.py --max-steps 2 --seed 58 --output /tmp/ch58-accelerate-results.json
python -m venv book-engineering/projects/60-mlops/.venv
book-engineering/projects/60-mlops/.venv/bin/python -m pip install -r book-engineering/projects/60-mlops/requirements-cpu.txt
book-engineering/projects/60-mlops/.venv/bin/python -m pip install -r book-engineering/projects/60-mlops/requirements-lock-linux-py313.txt
book-engineering/projects/60-mlops/.venv/bin/python -m pip check
(cd book-engineering/projects/60-mlops && .venv/bin/python -m unittest -v)
book-engineering/projects/60-mlops/.venv/bin/python book-engineering/projects/60-mlops/experiment_ops.py --backend manifest --output /tmp/ch60-manifest
book-engineering/projects/60-mlops/.venv/bin/python book-engineering/projects/60-mlops/experiment_ops.py --backend mlflow --output /tmp/ch60-mlflow
book-engineering/projects/60-mlops/.venv/bin/python book-engineering/projects/60-mlops/experiment_ops.py --backend wandb-offline --output /tmp/ch60-wandb
python book-engineering/test_volume4.py
python book-engineering/test_mobile_layout.py
```

`build_volume4.py` فصل‌های دارای منبع پیوسته را append می‌کند و فصل منتشرشدهٔ ناسازگار را رد می‌کند. گزینهٔ `--refresh-last-draft` فقط برای آخرین پیش‌نویس محلیِ هنوز منتشرنشده، پس از بررسی مستقل نبودن آن در remote و با حفظ تمام شناسه‌ها، مجاز است؛ پس از push نباید برای فصل منتشرشده به‌کار رود. CI جلد چهارم در `.github/workflows/volume4-audit.yml` checker، پروژهٔ آفلاین، idempotence، مرورگر و layout موبایل را اجرا می‌کند؛ وزن مدل را دانلود نمی‌کند.

پروژهٔ ۴۷ ۹ آزمون unit دارد؛ fixture آن ۱۵ رکورد ساختگی و ۱۴ گروه است. run اختیاری روی Pythia با revision ثابت و وابستگی‌های `requirements-model-demo.txt` انجام شد: Python 3.13.16، PyTorch 2.6.0+cpu، Transformers 4.57.6، Hub 0.36.0، Tokenizers 0.22.1 و Safetensors 0.7.0؛ CPU/FP32، یک epoch و شش update. Validation NLL در همین run از 7.1542 به 5.2552 رسید؛ test عمومی یک‌بار 6.4489 بود. این اعداد فقط smoke-test یک fixture بسیار کوچک‌اند؛ benchmark، کیفیت مدل واقعی/فارسی، پاسخ‌گویی محصولی، GPU/NCCL یا deployment را نشان نمی‌دهند. کارت Pythia آن را English و پژوهشی، نه مناسب deployment یا زبان‌های دیگر، معرفی می‌کرد؛ metadata مجوز مدل، مجوز corpus را اثبات نمی‌کند. وزن‌ها در repository نیستند.

پروژهٔ ۴۸ در `projects/48-peft-lab/` یک آزمایشگاه CPU/float32 برای LoRA و adapter مصنوعی است؛ ۱۴ آزمون unit موفق دارد. Fixture سه شکل لایه‌ای دارد و CLI audit روی همین fixture ۵٬۱۲۰ پارامتر پایه، ۸۳۲ پارامتر LoRA و کران پایین payload برابر ۲٬۵۶۰ بایت گزارش می‌کند. Demo خطی مصنوعیِ seed=48 در ۵۰۰ گام، MSE را از `0.001954437233507633` به `1.0780806292132183e-07` رساند؛ اختلاف merge `2.086162567138672e-07` بود. هیچ مدل pretrained، QLoRA واقعی، GPU، VRAM، کیفیت زبانی/فارسی یا benchmark اجرا/اندازه‌گیری نشد. جزئیات و محدودیت‌ها در `chapters/48-audit-report-fa.md` ثبت‌اند.

پروژهٔ ۴۹ در `projects/49-preference-lab/` loss مقایسه‌ای Bradley–Terry، DPO، surrogate clipped PPO و advantage گروهی GRPO را روی tensorهای کوچک CPU می‌آزماید؛ ۲۲ آزمون موفق دارد. Fixture ساختگی آن ۱۲ جفت در ۶ گروه دارد و audit فقط schema/split را بررسی می‌کند. Demo دسته‌ایِ seed=49 در ۸۰ گام loss را از `0.6931471824645996` به `0.12939360737800598` رساند و احتمال گزینهٔ chosen را از `0.5` به `0.9999496936798096` تغییر داد. هیچ model/reward انسانی یا AI، policy زبانی، RLHF/PPO/GRPO کامل، فارسی، GPU/NCCL، benchmark، privacy یا حقوق داده آزموده نشده است. مستندات و نتایج در `chapters/49-audit-report-fa.md` و `projects/49-preference-lab/results.json` ثبت‌اند.

پروژهٔ ۵۰ در `projects/50-synthetic-reasoning/` ممیزی trace جمع صحیح، split گروهی، ترتیب نمایشی curriculum، loss نرم KL و رأی‌گیری روی candidateهای ثابت را آزمود؛ ۲۶ آزمون موفق دارد. Fixture ساختگی ۱۲ ردیف/۶ گروه با seed=50 به splitهای train/validation/test برابر ۸/۲/۲ ردیف و ۴/۱/۱ گروه رفت؛ SHA-256 آن `1654621020c9dd2175cf0d7f66cb14ed78a3d192667c7e79ce7571219f47a075` است. loss روی logits مصنوعی `0.2875792384147644` بود و پنج رشتهٔ ثابت با رأی سه‌تایی `125` را برگزید. هیچ مدل زبانی، teacher/student آموزش‌دیده، benchmark، کیفیت فارسی، GPU، latency محصول، privacy یا حقوق داده آزموده نشد؛ جزئیات در `chapters/50-audit-report-fa.md` و `projects/50-synthetic-reasoning/results.json` ثبت‌اند.

پروژهٔ ۵۱ در `projects/51-vision-lab/` قرارداد patchify/unpatchify، loss contrastive و سنجهٔ retrieval را روی CPU و fixtureهای ساختگی می‌آزماید؛ ۲۶ آزمون موفق دارد. Fixture شامل ۴ بردار تصویر، ۴ بردار متن و ۴ گروه است؛ SHA-256 آن `aba309bb1b3e69443802190b988a21e0432109c01b777f4f58fe11f992936522` است. Demo loss مصنوعی `0.00024217297323048115` و Recall@1/MRR برابر ۱ را روی همین جفت‌های ساختگی گزارش کرد؛ ratio جفت‌های توجه برای token budget از ۲۲۴ تا ۴۴۸ برابر `15.878404493802984` بود. هیچ تصویر واقعی، مدل/ViT، training، benchmark، کیفیت فارسی، GPU، privacy، مجوز یا هزینهٔ محصول آزموده نشد؛ جزئیات در `chapters/51-audit-report-fa.md` و `projects/51-vision-lab/results.json` است.
پروژهٔ ۵۲ در `projects/52-audio-lab/` نمونهٔ سینوسی و WER/CER را بدون مدل یا فایل صوتی روی CPU بررسی می‌کند؛ ۳۹ آزمون موفق دارد. fixture ساختگی سه جفت transcript دارد و SHA-256 آن `46abd6b35e1481e0b3796522056d25168f7cc1823e0059fafc9a544dd5fdf347` است. Demo ۱۶۰۰ sample و ۸ frame کامل ساخت و در bin ۱۱ قلهٔ ۴۴۰ Hz یافت؛ WER ساختگی `3/11 = 0.2727272727272727` و CER ساختگی `15/43 = 0.3488372093023256` بود. هیچ گفتار، ASR/TTS، کیفیت فارسی، benchmark، inference، آموزش یا hardware performance سنجیده نشد؛ جزئیات در `chapters/52-audit-report-fa.md` و `projects/52-audio-lab/results.json` ثبت است.

پروژهٔ ۵۳ در `projects/53-diffusion-lab/` روی CPU و فقط کتابخانهٔ استاندارد، diffusion پیش‌رو/معکوس را روی یک مخلوط Gaussian دوبعدی ساختگی می‌آزماید؛ ۴۰ آزمون unit موفق دارد. SHA-256 fixture برابر `7646ab0c0d8cee8fdbf3e29ac88ce9e37b181859e0ff34935f6af7bbe28b208b` است. Demo با ۲۰۰ گام، ۶۴ نقطه و seed=53 مقدار `ᾱ_T=0.002080618226191632` و نزدیک‌ترین مرکزهای ساختگی `[19,17,16,12]` را گزارش کرد. شبکه، checkpoint، تصویر/ویدئو، benchmark، کیفیت فارسی یا سخت‌افزار واقعی آزموده نشد؛ جزئیات آزمون مرورگر، نتایج و مرز ادعاها در `chapters/53-audit-report-fa.md` و `projects/53-diffusion-lab/results.json` ثبت‌اند.

پروژهٔ ۵۴ در `projects/54-resource-estimation/` چهار profile ساختگیِ inference، full training، adapter و تقسیم ایدئال ZeRO را فقط با arithmetic و کتابخانهٔ استاندارد حساب می‌کند؛ ۴۵ آزمون موفق دارد. SHA-256 fixture برابر `9648418ea1cd039a5554d489d79e5d688314240f7c254d2d5215d03e372a4a57` است. نمونه‌ها وزن/KV را `18.364967 GB`، full training را همراه مرجع activation `130.924967 GB` در هر rank، adapter را `18.924967 GB` و ZeRO stage 3 چهاررتبه‌ای را `35.952467 GB` در هر rank گزارش می‌کنند. هیچ مدل یا سخت‌افزار واقعی، آموزش، peak memory، latency، benchmark، کیفیت فارسی یا هزینه سنجیده نشد؛ نتایج و مرز ادعاها در `chapters/54-audit-report-fa.md` و `projects/54-resource-estimation/results.json` ثبت‌اند.

**برش تاریخیِ آزمون فصل ۵۸، پیش از نگارش فصل‌های ۵۹ و ۶۰:** جلد چهارم در آن زمان ۱۲/۱۵ فصل و ۲۷۳ بخش داشت؛ فصل ۵۷ دارای ۲۰ و فصل ۵۸ دارای ۲۲ بخش است. `check_volume4.py` موفق شد: ۵۵ عبارت MathML دسترس‌پذیر و پیوست‌های دقیق. اجرای عادی builder idempotent بود. `test_volume4.py` در ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل موفق شد و ۱۲۱ دارایی آفلاین را بررسی کرد. `test_mobile_layout.py` در پنج عرض ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل کل ۱٬۰۷۸ بخش را گذراند؛ جلد چهارم ۷۸۷ بند نثری، ۴۶۲ بند تورفته، ۵۵ MathML و ۹ کپشن داشت. 404های ثبت‌شده مربوط به assetهای قدیمی و نامرتبط خارج از sparse checkout بودند؛ فایل‌های آن‌ها تغییر نکردند و تمام ۱۲۱ مسیر آفلاینِ لازم موجود بود.

پروژهٔ فصل ۵۷ با Python 3.13.16 و fixture ساختگی آزموده شد: ۱۵ آزمون در هر محیط مستقل، با ۱۳ موفق و ۲ skip اختیاری در هر venv تک‌چارچوب؛ در محیط پایهٔ بدون چارچوب ۱۲ موفق و ۳ skip بود. adapterهای CPU به‌طور مستقل با PyTorch 2.15.0، JAX 0.12.0.1 و TensorFlow 2.21.0 موفق شدند؛ آزمون workflow با PyTorch 2.6.0+cpu نیز گذشت. این‌ها فقط قرارداد زیان/گرادیان fixture را می‌سنجند، نه benchmark یا سخت‌افزار واقعی. پروژهٔ فصل ۵۶ با Python 3.13.16، fixture ساختگی و ۱۳ آزمون اجرا شد؛ نرخ ابری فقط snapshot Iowa/us-central1 است، برق فقط میانگین statewide Texas است و هیچ دستگاه، workload، تعرفهٔ Dallas، quote خرید/اجاره، benchmark یا نصب واقعی ارزیابی نشد. فصل ۵۷ پیش‌تر با commit مستقل `ff711011d47862fdb66368894493dc9f91d74175` منتشر شده است. شروع فصل ۵۸ روی همان remote، با worktree پاک و بدون فایل هم‌نام انجام شد؛ پروژهٔ آن با CPython 3.13.16, PyTorch `2.15.0+cpu`, Transformers `5.22.2`, Datasets `5.1.0`, Tokenizers `0.23.3` و Accelerate `1.15.0` در venv مستقل آزموده شد: `pip check` پاک، ۱۲/۱۲ آزمون unit موفق، دو گام CPU با گرادیان متناهی و اجرای `accelerate launch` موفق. Fixture دارای ۱۲ ردیف ساختگی/۶ گروه و hash `eb21fe6a41dcd4dc828c00a7dc0293370087bb77fc6df022078fc16a20d750a2` است؛ هیچ Hub download/token، pretrained weights، GPU یا benchmark استفاده نشد. فصل ۵۸ در انتشار پیشین با commit مستقل و push معمولی منتشر شد؛ این بند، وضعیت پروژهٔ آن فصل را ثبت می‌کند. این نسخه وب/PWA و Markdown است؛ PDF/EPUB تولید یا آزموده نشده‌اند.

پروژهٔ فصل ۶۰ در `projects/60-mlops/` با CPython 3.13.16، MLflow 3.18.0، W&B 0.31.0 و PyYAML 6.0.3 اجرا شد؛ ۱۶/۱۶ آزمون unit موفق، `pip check` پاک و `pip freeze` دقیقاً برابر lock بود. Manifest، MLflow محلی با SQLite و W&B آفلاین همگی روی fixture ساختگی hashدار موفق شدند؛ MSE همان fixture از 21.0 به `0.09078731868784178` رسید، بدون ادعای کیفیت مدل یا sync بیرونی. `test_volume4.py` در سه عرض، ۱۵۱ مسیر آفلاین و appendix دقیق فصل ۶۰ را گذراند؛ `test_mobile_layout.py` در پنج عرض ۱٬۱۲۴ بخش کل کتاب را وارسی کرد. checker جلد چهارم ۱۴/۱۵ فصل، ۳۱۹ بخش و ۵۸ MathML را تأیید کرد و builder idempotent بود. فصل در commit `83263810ea3b8c0ff024e1ffaf41f7411273183a` با push عادی منتشر شد؛ Volume 4، Volume 3، Volume 2 و Pages موفق شدند. Volume 1 در دو اجرای نخست (روی commit فصل و commit گزارش) در گام آزمون پروژه‌ها شکست خورد، چون حلقهٔ عمومی آن فصل ۶۰ را بدون MLflow/W&B اجرا می‌کرد؛ بازتولید محلی ۱۴/۱۶ موفق و دو خطای import متناظر را نشان داد. `.github/workflows/volume1-audit.yml` اصلاح شد تا فصل ۶۰ را به محیط پین‌شدهٔ Volume 4 واگذار کند؛ روی commit اصلاح `73c496a4048cd9e38377d804c84d70146595e1ef` پنج workflow (جلدهای ۱ تا ۴ و Pages) همگی موفق شدند. آزمون پروژهٔ فصل ۶۰ در محیط پین‌شده ۱۶/۱۶ موفق است. نسخهٔ زندهٔ Pages و SHA-256 فایل‌های کلیدی در گزارش `chapters/60-audit-report-fa.md` ثبت شده‌اند. Docker image، schema/cluster Kubernetes، GPU و PDF/EPUB در این اعتبارسنجی اجرا/تولید نشدند.

**مرز آزمون‌ها:** این تست‌ها مرورگرهای دیگر، Safari/iOS واقعی، GPU واقعی، همهٔ دستگاه‌ها، مجوز واقعی هر corpus، حذف کامل PII یا کیفیت آماری مدل را تأیید نمی‌کنند. پیش از هر فصل، remote، فایل‌های موجود و کل `BOOK_ROADMAP_FA.md` را بررسی کنید؛ هر فصل commit مستقل داشته باشد، push معمولی انجام شود، remote و CI بررسی شوند و سپس فصل بعد آغاز شود. Force push نکنید.
