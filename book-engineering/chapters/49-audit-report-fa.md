# گزارش ممیزی فصل ۴۹ — مدل پاداش، RLHF، PPO، DPO، GRPO و RLAIF

**وضعیت:** گزارش انتشار فصل محلی ۳ / سراسری ۴۹. **تاریخ پژوهش و ممیزی: ۶ نوامبر ۲۰۲۶.** این گزارش نتایج اجرای واقعی کد fixture را از ادعاهای پژوهشی و محدودیت‌ها جدا می‌کند. بازبینی منابع، مجوز یا کیفیت هر دادهٔ بیرونی را تأیید نمی‌کند.

## اقلام تحویلی

- منبع فصل: `book-engineering/chapters/49-preference-optimization.md`
- پاسخ‌نامهٔ مستقل: `book-engineering/answers/49-preference-optimization-fa.md`
- نمودار دسترس‌پذیر: `book-engineering/diagrams/v4-ch03-preference.svg`
- پروژهٔ مستقل: `book-engineering/projects/49-preference-lab/`
- گزارش نتایج ماشین‌خوان: `book-engineering/projects/49-preference-lab/results.json`
- پیوست کد فصل با فایل آزموده‌شده بایت‌به‌بایت: `projects/49-preference-lab/preference_lab.py`

## پژوهش מקורות ומحدودهٔ ادعا

ساختار فصل با نقشهٔ پنج‌جلدی و مرز فصل‌های ۴۷–۴۸ تطبیق داده شد. منابع اولیه برای RLHF، PPO، DPO، GRPO، RLAIF، Constitutional AI و RewardBench بررسی شدند؛ مستندات رسمی TRL نیز با نسخهٔ stable v1.17.1 و یادداشت انتشار v1.13.0 مقابله شد. در TRL v1.17.1، DPO/Reward/GRPO مستند شده‌اند و PPOTrainer از v1.13.0 حذف شده است؛ این نکته دربارهٔ API کتابخانه است، نه دربارهٔ الگوریتم PPO یا پیاده‌سازی‌های دیگر.

نتیجه‌های مقالات به prompt، مدل، داده، task، روش ارزیابی و تنظیم‌های گزارش‌شده در همان مقاله محدودند. دادهٔ ترجیح، probability در Bradley–Terry و reward model به‌عنوان proxy توصیف شده‌اند؛ clip PPO به‌عنوان hard bound یا تضمین بهبود معرفی نشده؛ DPO به فرض‌ها و reference وابسته دانسته شده؛ حذف critic در GRPO به معنی حذف reward/reference/rollout نیست؛ RLAIF از Constitutional AI جدا شده و نقش اصول انسانی حفظ شده است. منابع و تاریخ بازبینی در پایان متن فصل آمده‌اند.

## نتایج اجرای واقعی

محیط ثبت‌شده: Python **3.13.16**، PyTorch **2.6.0+cpu**، CPU و `float32`. هیچ checkpoint، tokenizer، dataset یا مدل pretrained دانلود/بارگذاری نشد.

- `python -m unittest -v test_preference_lab.py`: **۲۲/۲۲ آزمون موفق**؛ شامل اعتبارسنجی schema/ID/source، split گروهی قطعی و بدون هم‌پوشانی، loss مقایسه‌ای، loss DPO، advantage گروهی، clipping PPO و smoke test demo.
- CLI audit روی `sample_preferences.jsonl`: **۱۲ ردیف، ۶ گروه**، تمام برچسب‌ها `synthetic_fixture`. split: train **۸ ردیف/۴ گروه**، validation **۲/۱**، test **۲/۱**. وضعیت `validated_only`، `training_performed=false` و `model_downloaded=false`. SHA-256: `629b48e6a9c3f3a8d6c336eadbb1f3833b988348c1b11f1022221db121fc21bb`.
- CLI `toy-dpo` با seed **۴۹** و **۸۰** گام: loss از `0.6931471824645996` به `0.12939360737800598` رسید؛ احتمال انتخاب chosen در policy دسته‌ای از `0.5` به `0.9999496936798096` رسید. اجرا CPU/float32 بود و `model_loaded=false`، `model_downloaded=false`.
- `results.json` خروجی کامل audit و demo، نسخه‌ها و تعداد آزمون را نگه می‌دارد؛ همهٔ اعداد این بخش از همان اجرا ثبت شده‌اند.

## ساخت، browser، PWA و خروجی

- `build_volume4.py`: سه منبع پیوسته را ساخت/تطبیق داد؛ idempotence با snapshot قبل/بعد موفق بود. `check_volume4.py`: موفق؛ ۳ فصل از ۱۵، ۶۳ بخش، ۹ عبارت MathML دسترس‌پذیر، پیوست‌های کد دقیق و فایل‌های پاسخ‌نامه/گزارش/fixture تأیید شدند.
- `test_volume4.py`: در عرض‌های ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل موفق؛ فصل‌های ۴۷/۴۸/۴۹ دارای ۱۹/۲۱/۲۳ بخش‌اند. آزمون شکل‌های ۱۶۰۰×۱۰۰۰، MathML و `aria-label` نمونه‌ای از هر فصل، لینک پاسخ‌نامه، تطبیق بایت‌به‌بایت هر سه پیوست اجرایی، و ۲۷ دارایی precache/offline را وارسی کرد.
- `test_mobile_layout.py`: در ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل موفق؛ ۸۶۸ بخش، overflow، RTL و قواعد صفحه‌آرایی نثر را بررسی کرد. جلد چهارم ۱۶۶ بند نثری (۹۷ بند تورفته)، ۹ MathML و ۳ کپشن داشت. تراز/تورفتگی فقط در CSS است؛ فرمول، `aria-label`، متن جایگزین و کپشن دست‌کاری نشدند.
- `test_volume3.py` پس از ارتقای Service Worker به v79 نیز در ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل موفق بود: ۲۶۵ بخش، ۶۰ MathML، ۱۴ تصویر و ۱۱۵ فایل آفلاین.
- Regressionهای `check_volume.py`, `check_volume2.py`, `rebuild_volume3_targets.py`, `check_volume3.py`، `test_volume2.py`، `test_browser_audit.py`، `test_offline_volume.py` و `test_pwa_icon.py` موفق شدند. مجموعه‌آزمون پروژه‌ها در ۵۲ پوشه، در مجموع **۳۸۷/۳۸۷ آزمون** موفق داشت.
- مقایسه با `origin/gh-pages` نشان داد فایل‌های محتوایی جلدهای ۱–۳ و فصل‌های منتشرشدهٔ ۴۷–۴۸/پروژه‌هایشان byte-identical مانده‌اند؛ در `data.json` فصل‌های ۴۷–۴۸ بدون تغییرند و فقط فصل ۴۹ افزوده شده است. Builder و Markdown جلد چهارم نیز idempotent بودند.

این کتاب در این milestone به صورت وب/PWA و Markdown ساخته می‌شود؛ **PDF یا EPUB ساخته و آزموده نشده‌اند**، پس این گزارش تأیید خروجی چاپی نیست.

## محدوده و محدودیت‌ها

Fixtureها ساختگی و کوچک‌اند و برچسب‌های انسانی یا AI نیستند. آزمایشگاه تابع‌های ریاضی را روی tensorهای محدود smoke-test می‌کند؛ اجرای PPO، GRPO یا RLHF روی policy زبانی و آموزش reward model انجام نمی‌دهد. اعداد demo کیفیت زبان فارسی/دیگر زبان‌ها، مدل واقعی، ترجیح کاربران، safety، fairness، حقوق داده، privacy، GPU/NCCL، benchmark سخت‌افزار، latency یا هزینه را اندازه نمی‌گیرند. Split فقط گروه‌های موجود را جدا می‌کند؛ تعریف درست group، representativeness و leakageهای ثبت‌نشده را اثبات نمی‌کند. خروجی reward مصنوعی هم اعتبار یک ارزیاب یا metric بیرونی را نشان نمی‌دهد.

نتیجهٔ آزمون مرورگر فقط رفتار مسیرهای آزموده‌شدهٔ Chromium و عرض‌های گزارش‌شده را پوشش می‌دهد؛ تمام مرورگرها، دستگاه‌ها و دسترس‌پذیری واقعی برای همهٔ کاربران را تضمین نمی‌کند. هر ادعای فراتر از محدوده‌های بالا به آزمایش و منبع مستقل نیاز دارد.
