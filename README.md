# Fa Academy

اپ وب/PWA فارسی برای مجموعهٔ پنج‌جلدی «هنر و علم ساخت هوش». جلد اول ۲۱ فصل و جلد دوم ۱۱ فصل منتشرشده دارد. جلد سوم ۱۴ فصل محلی (۱–۱۴)، متناظر با فصل‌های سراسری ۳۳–۴۶، منتشر شده است. جلد چهارم ۱۵ فصل محلی (سراسری ۴۷–۶۱) دارد و هر ۱۵ فصل جداگانه منتشر شده‌اند. جلد پنجم در نقشه ۱۲ فصل محلی دارد؛ فصل‌های محلی ۱ تا ۴ (فصل‌های سراسری ۶۲ تا ۶۵) منتشر شده‌اند و فصل محلی ۵/سراسری ۶۶ با commit مستقل منتشر شده است. پس از اصلاح واگذاری یک آزمون در workflow جلد اول، هر پنج workflow جلدها و Pages موفق شدند؛ جزئیات commitها، runها و بررسی زنده در [گزارش ممیزی فصل ۶۶](book-engineering/chapters/66-audit-report-fa.md) آمده است. متن‌های قابل‌دریافت:

- [جلد دوم — Markdown](volume-2-full-fa.md)
- [جلد سوم، فصل‌های ۳۳–۴۶ — Markdown](volume-3-full-fa.md)
- [جلد چهارم، فصل‌های ۴۷–۶۱ — Markdown](volume-4-full-fa.md)
- [جلد پنجم، فصل‌های ۶۲–۶۶ — Markdown](volume-5-full-fa.md)

**قالب انتشار فعلی وب/PWA و Markdown است. PDF و EPUB تولید و آزموده نشده‌اند و به milestone بعدی موکول‌اند.** راهنمای اجرا، محدوده و محدودیت پروژه‌ها در [book-engineering/README.md](book-engineering/README.md) آمده است.

## جلد سوم: منابع و پروژه‌های فصل‌های ۴۵ و ۴۶

- **فصل ۴۵ — دقت عددی و Quantization:** [متن فصل](book-engineering/chapters/45-precision.md) · [پاسخ‌نامه](book-engineering/answers/45-precision-fa.md) · [پروژه](book-engineering/projects/45-precision/README.md) · [گزارش ممیزی فصل](book-engineering/chapters/45-audit-report-fa.md)
- **فصل ۴۶ — مقیاس، checkpointing و بازیابی run:** [متن فصل](book-engineering/chapters/46-scale-training.md) · [پاسخ‌نامه](book-engineering/answers/46-scale-training-fa.md) · [پروژه](book-engineering/projects/46-scale-training/README.md) · [گزارش ممیزی فصل](book-engineering/chapters/46-audit-report-fa.md)

نام‌گذاری ثابت است: منبع فصل در `chapters/{شماره سراسری}-{موضوع}.md`، پاسخ‌نامهٔ همان فصل در `answers/{شماره سراسری}-{موضوع}-fa.md` و پروژهٔ اجرایی در پوشهٔ موضوعی `projects/{شماره سراسری}-{موضوع}/` قرار دارد. پاسخ‌نامه مکمل متن است؛ پروژه نیز تمرین اجرایی مستقل همان فصل است.

برای مرور دیداری، [contact sheet چهارده شکل](review-volume-3/volume-3-contact-sheet.webp) و [راهنمای سبک جلد سوم](book-engineering/VOLUME3_STYLE_GUIDE_FA.md) را ببینید. [گزارش نهایی انتشار و گیت‌ها](book-engineering/VOLUME3_FINAL_RELEASE_FA.md) شمار فصل/بخش/فرمول، نتایج آزمون، وضعیت CI و محدودیت‌های باقی‌مانده را ثبت می‌کند.

## جلد چهارم: فصل‌های محلی ۱–۱۵ / سراسری ۴۷–۶۱

فصل ۴۷ دربارهٔ **Continued Pretraining، Instruction Tuning و SFT** است: مرز هدف CPT/SFT، label masking، قالب داده، split گروهی و پروتکل validation/test. فصل ۴۸، **PEFT، Adapter، LoRA و QLoRA** را بررسی می‌کند؛ فصل ۴۹ به **مدل پاداش، RLHF/PPO، DPO، GRPO، RLAIF و Constitutional AI** می‌پردازد؛ فصل ۵۰ **دادهٔ مصنوعی، تقطیر، Curriculum Learning، محاسبهٔ زمان آزمون و مدل‌های استدلالی** را پوشش می‌دهد؛ فصل ۵۱ **رمزگذار تصویر، Vision Transformer، ویژگی‌های وصله‌ای و هم‌ترازی متن–تصویر** را بررسی می‌کند؛ فصل ۵۲ **صوت و گفتار، قرارداد waveform، ASR، TTS، مدل‌های Audio-Language و ارزیابی WER/CER و کیفیت تولید** را پوشش می‌دهد؛ فصل ۵۳ **تولید تصویر و ویدئو، diffusion، sampling، latent، شرط‌دهی چندوجهی، ارزیابی، حقوق و ایمنی محتوا** را با آزمایشگاه CPU صرفاً مصنوعی بررسی می‌کند؛ فصل ۵۴ **برآورد منابع استنتاج، Fine-tuning و آموزش از صفر** را با تفکیک وزن‌ها، activationها، gradientها و optimizer بررسی می‌کند؛ فصل ۵۵ این نیازها را به طراحی اجزای آزمایشگاه شخصی، workstation حرفه‌ای و کلاستر سازمانی، همراه با بررسی برق، خنک‌کاری، شبکه، ذخیره‌سازی و نگه‌داری پیوند می‌دهد. فصل ۵۵ از fixture ساختگی استفاده می‌کند، نه از فهرست قیمت یا benchmark؛ فصل ۵۶ بودجه و TCO/NPV، خرید/اجاره/ابر و ریسک عرضه را پوشش می‌دهد. قیمت ابرِ Iowa (`us-central1`) و میانگین برق statewide در Texas در فصل ۵۶ با تاریخ و بازار مشخص شده‌اند و به‌عنوان Dallas quotes معرفی نشده‌اند. فصل ۵۷ چارچوب‌های Python/PyTorch/JAX/TensorFlow را مقایسه می‌کند؛ فصل ۵۸ خط لولهٔ Transformers/Datasets/Tokenizers/Accelerate را از داده تا یک smoke test CPU می‌سازد؛ فصل ۵۹ CUDA/ROCm/Triton و مقیاس‌پذیری DeepSpeed/FSDP/Megatron را با آزمون CPU/Gloo محدود می‌کند؛ فصل ۶۰ MLflow/W&B، Git، Linux، Docker و Kubernetes را برای ثبت اجرای قابل‌بازرسی آموزش می‌دهد؛ فصل ۶۱ موتورهای runtime، export، KV cache، زمان‌بندی و trade-offهای benchmark را بررسی می‌کند. هر فصل منبع، پاسخ‌نامه، گزارش ممیزی و پروژهٔ جدا دارد.

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
- [فصل ۵۷: متن](book-engineering/chapters/57-ml-frameworks.md) · [پاسخ‌نامه](book-engineering/answers/57-ml-frameworks-fa.md) · [پروژه](book-engineering/projects/57-framework-lab/README.md) · [گزارش](book-engineering/chapters/57-audit-report-fa.md)
- [فصل ۵۸: متن](book-engineering/chapters/58-huggingface-stack.md) · [پاسخ‌نامه](book-engineering/answers/58-huggingface-stack-fa.md) · [پروژه](book-engineering/projects/58-huggingface-stack/README.md) · [گزارش](book-engineering/chapters/58-audit-report-fa.md)
- [فصل ۵۹: متن](book-engineering/chapters/59-gpu-systems.md) · [پاسخ‌نامه](book-engineering/answers/59-gpu-systems-fa.md) · [پروژه](book-engineering/projects/59-gpu-systems/README.md) · [گزارش](book-engineering/chapters/59-audit-report-fa.md)
- [فصل ۶۰: متن](book-engineering/chapters/60-mlops.md) · [پاسخ‌نامه](book-engineering/answers/60-mlops-fa.md) · [پروژه](book-engineering/projects/60-mlops/README.md) · [گزارش](book-engineering/chapters/60-audit-report-fa.md)
- [فصل ۶۱: متن](book-engineering/chapters/61-inference-serving.md) · [پاسخ‌نامه](book-engineering/answers/61-inference-serving-fa.md) · [پروژه](book-engineering/projects/61-inference-serving/README.md) · [گزارش](book-engineering/chapters/61-audit-report-fa.md)
- سازندهٔ append-safe: `book-engineering/build_volume4.py`؛ checker: `book-engineering/check_volume4.py`؛ خروجی Markdown: `volume-4-full-fa.md`.

## جلد پنجم: فصل‌های محلی ۱–۱۲ / سراسری ۶۲–۷۳

فصل‌های محلی ۱–۴ (سراسری ۶۲–۶۵) جداگانه منتشر شده‌اند؛ فصل محلی ۵/سراسری ۶۶ با commit مستقل و push عادی منتشر شد. اجرای نخستِ جلد اول آشکار کرد که حلقهٔ عمومی آزمون پروژه‌ها باید فصل ۶۶ را به محیط پین‌شدهٔ جلد پنجم واگذارد؛ اصلاح این گیت و تأیید موفق هر پنج workflow و Pages در گزارش ممیزی ثبت شده‌اند. این جلد benchmark و رفتار مدل (۶۲–۶۳)، Red Teaming و امنیت (۶۴)، حکمرانی و ریسک (۶۵)، سپس محصول/API و قراردادهای backend/frontend (۶۶) را به هم پیوند می‌دهد. مرزهای بعدی حفظ شده‌اند: runtime و بهینه‌سازی در ۶۷، احراز هویت/پایش/پاسخ به رخداد در ۶۸، و استقرار/CI/CD در ۶۹ است؛ پژوهش مستقل در فصل‌های ۷۰–۷۳ می‌آید.

- [فصل ۶۲: متن](book-engineering/chapters/62-benchmarking-evaluation.md) · [پاسخ‌نامه](book-engineering/answers/62-benchmarking-evaluation-fa.md) · [پروژه](book-engineering/projects/62-evaluation-lab/README.md) · [گزارش ممیزی](book-engineering/chapters/62-audit-report-fa.md)
- [فصل ۶۳: متن](book-engineering/chapters/63-hallucination-bias-robustness.md) · [پاسخ‌نامه](book-engineering/answers/63-hallucination-bias-robustness-fa.md) · [پروژه](book-engineering/projects/63-model-behavior-lab/README.md) · [گزارش ممیزی](book-engineering/chapters/63-audit-report-fa.md)
- [فصل ۶۴: متن](book-engineering/chapters/64-red-teaming-security.md) · [پاسخ‌نامه](book-engineering/answers/64-red-teaming-security-fa.md) · [پروژه](book-engineering/projects/64-red-team-lab/README.md) · [گزارش ممیزی](book-engineering/chapters/64-audit-report-fa.md)
- [فصل ۶۵: متن](book-engineering/chapters/65-alignment-governance.md) · [پاسخ‌نامه](book-engineering/answers/65-alignment-governance-fa.md) · [پروژه](book-engineering/projects/65-governance-lab/README.md) · [گزارش ممیزی](book-engineering/chapters/65-audit-report-fa.md)
- [فصل ۶۶: متن](book-engineering/chapters/66-ai-product-api.md) · [پاسخ‌نامه](book-engineering/answers/66-ai-product-api-fa.md) · [پروژه](book-engineering/projects/66-ai-product-api/README.md) · [گزارش ممیزی](book-engineering/chapters/66-audit-report-fa.md)

فصل ۶۶ روی fixture ساختگی و بدون شبکه یا مدل زنده، ۱۲ آزمون API و دو آزمون مرورگر دارد؛ نسخه‌ها، محدودیت‌ها و نتایج در [گزارش ممیزی](book-engineering/chapters/66-audit-report-fa.md) و `projects/66-ai-product-api/results.json` ثبت شده‌اند. برای بازتولید، از ریشهٔ مخزن اجرا کنید:

```bash
python -m pip install -r requirements.txt
python -m pip install -r book-engineering/projects/66-ai-product-api/requirements.txt
python -m playwright install --with-deps chromium
python book-engineering/build_volume5.py
python book-engineering/check_volume5.py
python book-engineering/projects/66-ai-product-api/audit.py --output /tmp/ch66-results.json
python book-engineering/test_volume5.py
python book-engineering/test_mobile_layout.py
```

در این snapshot جلد پنجم ۵/۱۲ فصل و ۴۰ بخش تازه دارد؛ Service Worker `fa-academy-v105` با ۶۶ مسیر آفلاین، از جمله گزارش به‌روزشدهٔ فصل ۶۶، منتشر می‌شود. پنج checker جلدها، پروژه‌های ۶۲–۶۶، آزمون idempotence سازنده و browser/mobile در گیت محلی موفق شدند. commit محتوای فصل [`5dc3672`](https://github.com/mvbabababak-spec/fa-academy/commit/5dc36725c962ce05790cac1728df744d4c640e42) و commit اصلاح واگذاری CI [`9ed607a`](https://github.com/mvbabababak-spec/fa-academy/commit/9ed607a862b5b11042ad640394606e00fab28851) روی `gh-pages` منتشر شدند؛ پس از اصلاح، هر پنج workflow و Pages با وضعیت موفق تأیید شدند. شناسهٔ runها، شکست اولیهٔ جلد اول و علت اصلاح در [گزارش ممیزی فصل ۶۶](book-engineering/chapters/66-audit-report-fa.md) ثبت است. تصویر مرجع `book-engineering/reports/browser-mobile.webp` و تغییرهای responsive قبلی حفظ شده‌اند.

قالب انتشار وب/PWA و Markdown است؛ PDF و EPUB تولید یا آزموده نشده‌اند. فصل ۶۵ تکرار نمی‌شود. فصل ۶۷ را تا ثبت SHA انتشار فصل ۶۶، تأیید remote، workflowهای جلدهای ۱–۵ و Pages آغاز نکنید.
