# Fa Academy

اپ وب/PWA فارسی برای مجموعهٔ پنج‌جلدی «هنر و علم ساخت هوش». جلد اول ۲۱ فصل و جلد دوم ۱۱ فصل منتشرشده دارد. جلد سوم ۱۴ فصل محلی (۱–۱۴)، متناظر با فصل‌های سراسری ۳۳–۴۶، منتشر شده است. جلد چهارم در نقشه ۱۵ فصل محلی (سراسری ۴۷–۶۱) دارد؛ ده فصل محلی ۱–۱۰/سراسری ۴۷–۵۶ منتشر شده‌اند و پنج فصل دیگر در نقشه‌اند. متن‌های قابل‌دریافت:

- [جلد دوم — Markdown](volume-2-full-fa.md)
- [جلد سوم، فصل‌های ۳۳–۴۶ — Markdown](volume-3-full-fa.md)
- [جلد چهارم، فصل‌های ۴۷–۵۶ — Markdown](volume-4-full-fa.md)

**قالب انتشار فعلی وب/PWA و Markdown است. PDF و EPUB تولید و آزموده نشده‌اند و به milestone بعدی موکول‌اند.** راهنمای اجرا، محدوده و محدودیت پروژه‌ها در [book-engineering/README.md](book-engineering/README.md) آمده است.

## جلد سوم: منابع و پروژه‌های فصل‌های ۴۵ و ۴۶

- **فصل ۴۵ — دقت عددی و Quantization:** [متن فصل](book-engineering/chapters/45-precision.md) · [پاسخ‌نامه](book-engineering/answers/45-precision-fa.md) · [پروژه](book-engineering/projects/45-precision/README.md) · [گزارش ممیزی فصل](book-engineering/chapters/45-audit-report-fa.md)
- **فصل ۴۶ — مقیاس، checkpointing و بازیابی run:** [متن فصل](book-engineering/chapters/46-scale-training.md) · [پاسخ‌نامه](book-engineering/answers/46-scale-training-fa.md) · [پروژه](book-engineering/projects/46-scale-training/README.md) · [گزارش ممیزی فصل](book-engineering/chapters/46-audit-report-fa.md)

نام‌گذاری ثابت است: منبع فصل در `chapters/{شماره سراسری}-{موضوع}.md`، پاسخ‌نامهٔ همان فصل در `answers/{شماره سراسری}-{موضوع}-fa.md` و پروژهٔ اجرایی در پوشهٔ موضوعی `projects/{شماره سراسری}-{موضوع}/` قرار دارد. پاسخ‌نامه مکمل متن است؛ پروژه نیز تمرین اجرایی مستقل همان فصل است.

برای مرور دیداری، [contact sheet چهارده شکل](review-volume-3/volume-3-contact-sheet.webp) و [راهنمای سبک جلد سوم](book-engineering/VOLUME3_STYLE_GUIDE_FA.md) را ببینید. [گزارش نهایی انتشار و گیت‌ها](book-engineering/VOLUME3_FINAL_RELEASE_FA.md) شمار فصل/بخش/فرمول، نتایج آزمون، وضعیت CI و محدودیت‌های باقی‌مانده را ثبت می‌کند.

## جلد چهارم: فصل‌های محلی ۱–۱۰ / سراسری ۴۷–۵۶

فصل ۴۷ دربارهٔ **Continued Pretraining، Instruction Tuning و SFT** است: مرز هدف CPT/SFT، label masking، قالب داده، split گروهی و پروتکل validation/test. فصل ۴۸، **PEFT، Adapter، LoRA و QLoRA** را بررسی می‌کند؛ فصل ۴۹ به **مدل پاداش، RLHF/PPO، DPO، GRPO، RLAIF و Constitutional AI** می‌پردازد؛ فصل ۵۰ **دادهٔ مصنوعی، تقطیر، Curriculum Learning، محاسبهٔ زمان آزمون و مدل‌های استدلالی** را پوشش می‌دهد؛ فصل ۵۱ **رمزگذار تصویر، Vision Transformer، ویژگی‌های وصله‌ای و هم‌ترازی متن–تصویر** را بررسی می‌کند؛ فصل ۵۲ **صوت و گفتار، قرارداد waveform، ASR، TTS، مدل‌های Audio-Language و ارزیابی WER/CER و کیفیت تولید** را پوشش می‌دهد؛ فصل ۵۳ **تولید تصویر و ویدئو، diffusion، sampling، latent، شرط‌دهی چندوجهی، ارزیابی، حقوق و ایمنی محتوا** را با آزمایشگاه CPU صرفاً مصنوعی بررسی می‌کند؛ فصل ۵۴ **برآورد منابع استنتاج، Fine-tuning و آموزش از صفر** را با تفکیک وزن‌ها، activationها، gradientها و optimizer بررسی می‌کند؛ فصل ۵۵ این نیازها را به طراحی اجزای آزمایشگاه شخصی، workstation حرفه‌ای و کلاستر سازمانی، همراه با بررسی برق، خنک‌کاری، شبکه، ذخیره‌سازی و نگه‌داری پیوند می‌دهد. فصل ۵۵ از fixture ساختگی استفاده می‌کند، نه از فهرست قیمت یا benchmark؛ فصل ۵۶ بودجه و TCO/NPV، خرید/اجاره/ابر و ریسک عرضه را پوشش می‌دهد. قیمت ابرِ Iowa (`us-central1`) و میانگین برق statewide در Texas در فصل ۵۶ با تاریخ و بازار مشخص شده‌اند و به‌عنوان Dallas quotes معرفی نشده‌اند. هر فصل منبع، پاسخ‌نامه، گزارش ممیزی و پروژهٔ جدا دارد.

- [فصل ۴۷: متن](book-engineering/chapters/47-posttraining.md) · [پاسخ‌نامه](book-engineering/answers/47-posttraining-fa.md) · [پروژه](book-engineering/projects/47-instruction-tuning/README.md) · [گزارش](book-engineering/chapters/47-audit-report-fa.md)
- [فصل ۴۸: متن](book-engineering/chapters/48-peft.md) · [پاسخ‌نامه](book-engineering/answers/48-peft-fa.md) · [پروژه](book-engineering/projects/48-peft-lab/README.md) · [گزارش](book-engineering/chapters/48-audit-report-fa.md)
- [فصل ۴۹: متن](book-engineering/chapters/49-preference-optimization.md) · [پاسخ‌نامه](book-engineering/answers/49-preference-optimization-fa.md) · [پروژه](book-engineering/projects/49-preference-lab/README.md) · [گزارش](book-engineering/chapters/49-audit-report-fa.md)
- [فصل ۵۰: متن](book-engineering/chapters/50-synthetic-reasoning.md) · [پاسخ‌نامه](book-engineering/answers/50-synthetic-reasoning-fa.md) · [پروژه](book-engineering/projects/50-synthetic-reasoning/README.md) · [گزارش](book-engineering/chapters/50-audit-report-fa.md)
- [فصل ۵۱: متن](book-engineering/chapters/51-vision-models.md) · [پاسخ‌نامه](book-engineering/answers/51-vision-models-fa.md) · [پروژه](book-engineering/projects/51-vision-lab/README.md) · [گزارش](book-engineering/chapters/51-audit-report-fa.md)
- [فصل ۵۲: متن](book-engineering/chapters/52-audio-models.md) · [پاسخ‌نامه](book-engineering/answers/52-audio-models-fa.md) · [پروژه](book-engineering/projects/52-audio-lab/README.md) · [گزارش](book-engineering/chapters/52-audit-report-fa.md)
- [فصل ۵۳: متن](book-engineering/chapters/53-image-video-generation.md) · [پاسخ‌نامه](book-engineering/answers/53-image-video-generation-fa.md) · [پروژه](book-engineering/projects/53-diffusion-lab/README.md) · [گزارش](book-engineering/chapters/53-audit-report-fa.md)
- [فصل ۵۴: متن](book-engineering/chapters/54-resource-estimation.md) · [پاسخ‌نامه](book-engineering/answers/54-resource-estimation-fa.md) · [پروژه](book-engineering/projects/54-resource-estimation/README.md) · [گزارش](book-engineering/chapters/54-audit-report-fa.md)
- [فصل ۵۵: متن](book-engineering/chapters/55-ai-lab-design.md) · [پاسخ‌نامه](book-engineering/answers/55-ai-lab-design.md) · [پروژه](book-engineering/projects/55-ai-lab-design/README.md) · [گزارش](book-engineering/chapters/55-audit-report-fa.md)
- [فصل ۵۶: متن](book-engineering/chapters/56-ai-compute-budget.md) · [پاسخ‌نامه](book-engineering/answers/56-ai-compute-budget-fa.md) · [پروژه](book-engineering/projects/56-ai-compute-budget/README.md) · [گزارش](book-engineering/chapters/56-audit-report-fa.md)
- سازندهٔ append-safe: `book-engineering/build_volume4.py`؛ checker: `book-engineering/check_volume4.py`؛ خروجی Markdown: `volume-4-full-fa.md`.
- مثال اختیاری فصل ۴۷ از revision ثابت `EleutherAI/pythia-14m` استفاده می‌کند. کارت مدل آن را انگلیسی‌زبان و پژوهشی معرفی می‌کند و برای deployment یا زبان‌های دیگر توصیه نمی‌کند؛ fixture آن ساختگی انگلیسی است و ادعای کیفیت فارسی یا محصولی ندارد. پروژه‌های فصل‌های ۴۸–۵۶ به مدل pretrained نیاز ندارند.

## گزارش‌های ممیزی جلد سوم

[فصل ۳۳](book-engineering/chapters/33-audit-report-fa.md) · [۳۴](book-engineering/chapters/34-audit-report-fa.md) · [۳۵](book-engineering/chapters/35-audit-report-fa.md) · [۳۶](book-engineering/chapters/36-audit-report-fa.md) · [۳۷](book-engineering/chapters/37-audit-report-fa.md) · [۳۸](book-engineering/chapters/38-audit-report-fa.md) · [۳۹](book-engineering/chapters/39-audit-report-fa.md) · [۴۰](book-engineering/chapters/40-audit-report-fa.md) · [۴۱](book-engineering/chapters/41-audit-report-fa.md) · [۴۲](book-engineering/chapters/42-audit-report-fa.md) · [۴۳](book-engineering/chapters/43-audit-report-fa.md) · [۴۴](book-engineering/chapters/44-audit-report-fa.md) · [۴۵](book-engineering/chapters/45-audit-report-fa.md) · [۴۶](book-engineering/chapters/46-audit-report-fa.md) · [ممیزی نهایی جلد سوم](book-engineering/VOLUME3_FINAL_RELEASE_FA.md) · [گزارش ممیزی جلد دوم](book-engineering/VOLUME2_FINAL_RELEASE_FA.md).
