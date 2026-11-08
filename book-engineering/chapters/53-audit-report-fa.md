# گزارش ممیزی فصل ۵۳ — تولید تصویر و ویدئو و Diffusion

**وضعیت:** جلد چهارم، فصل محلی ۷ از ۱۵ / فصل سراسری ۵۳. **تاریخ بازبینی منابع و ممیزی محلی: ۶ نوامبر ۲۰۲۶.** این گزارش نتیجهٔ fixture مصنوعی را از ادعاهای پژوهشی و توان مدل واقعی جدا می‌کند.

## دامنه و مرز فصل

فهرست کامل پنج جلد و جایگاه این فصل با `BOOK_ROADMAP_FA.md` تطبیق داده شد. فصل ۵۱ فهم تصویر، Vision Transformer و هم‌ترازی متن–تصویر را پوشش می‌دهد؛ فصل ۵۲ به waveform، بازشناسی و تولید گفتار اختصاص دارد. فصل ۵۳ از آن دو مرز عبور می‌کند و بر ساخت تصویر/ویدئو، فرایند و samplerهای diffusion، latent، شرط‌دهی متنی، زمان‌مندی و ارزیابی/حقوق/ایمنی محتوا تمرکز دارد. فصل بعدی، سراسری ۵۴، برآورد منابع برای workload را جداگانه بررسی می‌کند؛ محاسبهٔ هزینهٔ سخت‌افزار در این فصل ادعای اجرایی ندارد.

منابع اولیهٔ DDPM، DDIM، classifier-free guidance و latent diffusion، مقالهٔ DiT، کارهای flow matching/rectified flow، گزارش‌های Sora/HunyuanVideo/Wan، benchmarkهای VBench، مستندات رسمی U.S. Copyright Office و C2PA 2.5 تا تاریخ بالا بازبینی شدند. مقاله‌ها و preprintها برای setup، داده و نسخهٔ گزارش‌شدهٔ همان نویسندگان نقل شده‌اند؛ هیچ‌یک در پروژهٔ محلی بازتولید نشده‌اند. وضعیت Part 3 ادارهٔ کپی‌رایت آمریکا در صفحهٔ بازبینی‌شده، pre-publication اعلام شده است و این گزارش آن را نظر حقوقی برای مورد خاص تلقی نمی‌کند.

## اقلام تحویلی

- متن فصل: `book-engineering/chapters/53-image-video-generation.md`
- پاسخ‌نامهٔ مستقل: `book-engineering/answers/53-image-video-generation-fa.md`
- گزارش ممیزی: همین فایل
- دیاگرام SVG دسترس‌پذیر: `book-engineering/diagrams/v4-ch07-diffusion.svg`
- پروژهٔ CPU و fixture ساختگی: `book-engineering/projects/53-diffusion-lab/`
- پیوست اجرایی: نسخهٔ انتهایی کد فصل باید بایت‌به‌بایت با `projects/53-diffusion-lab/diffusion_lab.py` برابر باشد.
- خروجی گردآوری جلد: `volume-4-full-fa.md`، Markdown وب/PWA؛ PDF و EPUB تولید و آزموده نشده‌اند.

## نتایج اجرای واقعی و روش آزمایش

محیط اجرای ثبت‌شده: **Python 3.13.16**، CPU و فقط کتابخانهٔ استاندارد Python.

- در پوشهٔ پروژه، `python -m unittest discover -v`: **۴۰/۴۰ آزمون موفق**. آزمون‌ها schema و hash fixture، schedule، noising بسته‌بسته، وارون‌سازی با noise معلوم، رابطهٔ score و epsilon، واریانس posterior، گام reverse، seed تکرارپذیر و CLI را بررسی کردند.
- SHA-256 fixture برابر `7646ab0c0d8cee8fdbf3e29ac88ce9e37b181859e0ff34935f6af7bbe28b208b` است. fixture چهار مرکز Gaussian دوبعدی با وزن مساوی دارد و صریحاً تصویر، ویدئو، مشاهدهٔ واقعی یا وزن آموزش‌دیده دربر ندارد.
- `audit` با وضعیت `synthetic_diffusion_fixture_audit_complete` خاتمه یافت؛ نه آموزش، نه بارگیری مدل و نه خواندن رسانه انجام شد.
- اجرای demo با schedule خطی، `β_start=0.0005`، `β_end=0.06`، ۲۰۰ گام، ۶۴ نمونه و seed برابر ۵۳ مقدار `ᾱ_T=0.002080618226191632` داد. شمار نزدیک‌ترین **مرکزهای ساختگی** `[southwest=19, northwest=17, southeast=16, northeast=12]` و میانگین نمونه‌ها `[-0.2332439537277366, -0.14123519607642687]` بود. این شمارش/میانگین فقط خلاصهٔ اجرای همان sampler و fixture است، نه معیار کیفیت.
- `results.json` خروجی‌های audit/demo، hash و نسخهٔ Python را نگه می‌دارد. جزئیات fixture و seed باید هنگام بازتولید ثابت بمانند.

## محدودیت‌ها و gateهای ادغام

Score پروژه به‌صورت تحلیلی از چگالی معلوم همان مخلوط Gaussian محاسبه می‌شود؛ شبکه‌ای آموزش داده نشده است. هیچ تصویر یا ویدئویی تولید یا بارگیری نشده؛ هیچ checkpoint، tokenizer، VAE، GPU، benchmark، latency، کیفیت prompt، تداوم زمانی، کیفیت فارسی، ارزیابی انسانی، مجوز، نتیجهٔ حقوقی، privacy یا ایمنی محصول آزموده نشده است. بنابراین نتیجه را به مولد واقعی یا سخت‌افزار تعمیم ندهید.

آزمون‌های محلی پس از ادغام پیش‌نویس: `check_volume4.py` با نتیجهٔ ۷/۱۵ فصل، ۱۶۷ بخش و ۳۳ MathML موفق شد؛ `test_volume4.py` فصل‌های ۴۷–۵۳ را در عرض‌های ۳۲۰، ۳۹۰ و ۱۴۴۰، پیوست‌های بایت‌به‌بایت و ۷۱ دارایی آفلاین آزمود و موفق بود. `test_mobile_layout.py` نیز در ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل، همهٔ ۹۷۲ بخش را پیمود؛ برای جلد چهارم ۴۶۷ بند نثرِ هم‌تراز، ۲۷۵ بند تورفته، ۳۳ MathML و ۶ کپشن ثبت کرد و موفق شد. چهار جلد مایکروسافت نیز در همین آزمون به‌صورت portrait و آفلاین با اندازهٔ ۸۴۸×۱۲۶۴ بار شدند. آزمون‌های مرورگر با Playwright 1.64.1 و Chromium در محیط محلی اجرا شدند.

**CI نهایی commit فصل ۵۳ `3e60393873002c87d13b5bb81852ce2ed296dced`: موفق.** هر پنج run برای همان SHA سبز شدند: [Volume 1](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42236024938)، [Volume 2](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42236025674)، [Volume 3](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42236024930)، [Volume 4](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42236024967) و [Pages deployment](https://github.com/mvbabababak-spec/fa-academy/actions/runs/42236024385). در workflow جلد چهارم، stepهای فصل ۵۳، idempotence، مرورگر، responsive، پیوست دقیق و offline همگی success شدند.

پس از deployment، `data.json` عمومی جلد چهارم را با ۷ فصل و فصل ۵۳ با ۲۷ بخش نشان داد. متن فصل، پاسخ‌نامه، گزارش، SVG، پروژه و خروجی Markdown همگی از [سایت](https://mvbabababak-spec.github.io/fa-academy/) با HTTP 200 دریافت شدند؛ service worker در commit فصل v86 بود و مسیرهای cache شامل هر ۹ دارایی فصل ۵۳ و هر چهار جلد مایکروسافت بود. چون گزارش ممیزی پس از ثبت CI به‌روزرسانی شد، در commit پیگیریِ گزارش، cache به v87 افزایش داده شد تا نسخهٔ تازهٔ گزارش نیز آفلاین به‌روز شود. چهار جلد مایکروسافت نیز HTTP 200، WebP و ۸۴۸×۱۲۶۴ باقی ماندند. فصل‌های منتشرشدهٔ جلد چهارم بازنویسی نمی‌شوند و فصل ۵۳ باید جدا از فصل بعدی منتشر شود.
