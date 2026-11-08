# گزارش ممیزی فصل ۵۱ — مدل‌های تصویر و هم‌ترازی متن–تصویر

**وضعیت:** گزارش ممیزی فصل محلی ۵ / سراسری ۵۱. **تاریخ پژوهش و ممیزی: ۶ نوامبر ۲۰۲۶.** نتایج fixture از ادعاهای مقاله‌ها و محدودیت‌های واقعی جدا می‌شوند. این گزارش تأیید حقوقیِ داده یا مدل نیست.

## اقلام تحویلی

- فصل: `book-engineering/chapters/51-vision-models.md`
- پاسخ‌نامهٔ مستقل: `book-engineering/answers/51-vision-models-fa.md`
- نمودار SVG دسترس‌پذیر: `book-engineering/diagrams/v4-ch05-vision.svg`
- پروژهٔ آزمایشگاهی: `book-engineering/projects/51-vision-lab/`
- manifest خروجی: `book-engineering/projects/51-vision-lab/results.json`
- پیوست اجرایی بایت‌به‌بایت: `projects/51-vision-lab/vision_lab.py`

## پژوهش، مرز موضوعی و روش

ساختار کامل پنج جلد و جایگاه فصل‌های ۵۰–۵۲ با `BOOK_ROADMAP_FA.md` تطبیق داده شد؛ فصل ۳۹ برای جلوگیری از تکرار مبانی چندوجهی، فصل ۵۰ برای قرارداد داده/مرز ادعا و فصل‌های ۴۷–۴۹ برای سبک پروژه بازبینی شدند. فصل ۵۱ بر وصله و Vision Transformer، تفاوت نمایش سراسری و مکانی، encoderهای تصویر، dual-encoder متن–تصویر، هدف‌های contrastive، provenance، retrieval و ارزیابی متمرکز است. آموزش صوت و ادغام عمومی چندمدالیته تکرار نشده‌اند؛ فصل ۵۲ برای صوت باقی می‌ماند.

منابع اولیه شامل ViT، CLIP، MAE، SigLIP، DataComp، DINOv2/DINOv3 و کارهای تازه‌تر دربارهٔ SigLIP 2، Perception Encoder، FineViT، CFM و VIRTUE تا تاریخ بازبینی ثبت شدند. نتیجه‌های مقاله‌ها فقط به مدل، داده، task و پروتکل گزارش‌شده در همان کار محدودند؛ پروژهٔ محلی هیچ‌یک را بازتولید نمی‌کند.

## نتایج اجرای واقعی پروژه

محیط ثبت‌شده: Python **3.13.16**، PyTorch **2.6.0+cpu**، CPU و `float32`.

- `python -m unittest discover -v` در `51-vision-lab`: **۲۶/۲۶ آزمون موفق**. آزمون‌ها grid و token budget، patchify/unpatchify، ترتیب وصله، validation ورودی، loss contrastive ساختگی، گرادیان، معیار retrieval دوطرفه، چند مثبت گروهی، fixture، hash و مرز گزارش را بررسی کردند.
- `audit`: چهار رکورد تصویر + چهار رکورد متن، چهار گروه و embedding dimension برابر ۴؛ SHA-256 fixture: `aba309bb1b3e69443802190b988a21e0432109c01b777f4f58fe11f992936522`. `training_performed=false`, `image_files_loaded=false`, `pretrained_model_loaded=false`, `model_downloaded=false`.
- `demo`: tensor ثابت `3×8×8` به چهار patch با عرض ۴۸ تبدیل و دقیق بازسازی شد. بودجهٔ نظری با patch16 شامل ۱۹۷ token و ۳۸٬۸۰۹ جفت توجه در هر head برای ۲۲۴×۲۲۴ و ۷۸۵ token و ۶۱۶٬۲۲۵ جفت برای ۴۴۸×۴۴۸ بود؛ نسبت `15.878404493802984`. loss ساختگی `0.00024217297323048115` شد؛ Recall@1 و MRR در دو جهت `1.0` و گرادیان متناهی بود. بردارهای fixture عمداً جفت درست را نزدیک می‌گذارند؛ این امتیازها نتیجهٔ مدل یا retrieval واقعی نیستند.
- هیچ فایل تصویر، caption واقعی، tokenizer، ViT forward pass، image encoder pretrained، checkpoint دانلودشده، آموزش، پاسخ فارسی، benchmark، GPU یا ارزیابی انسانی اجرا نشد.

این نتایج فقط قرارداد helperها و fixtureهای مصنوعی را می‌سنجند. کیفیت مدل واقعی، کیفیت فارسی، image understanding، zero-shot، localization، fairness، robustness، مجوز/حقوق، privacy، latency، انرژی یا هزینهٔ محصول از آن‌ها استنباط نمی‌شود.

## نتایج ساخت، مرورگر، آفلاین و تایپوگرافی

- `build_volume4.py` پنج فصل از ۱۵ فصل نقشه را با شناسه‌های پایدار ساخت؛ تعداد بخش‌های فصل‌های ۴۷–۵۱ به‌ترتیب **۱۹، ۲۱، ۲۳، ۲۴ و ۲۳** (در مجموع **۱۱۰**) است. `check_volume4.py` حضور پاسخ‌نامه، گزارش، fixture، دسترس‌پذیری MathML، ابعاد SVG و برابری دقیق کد پیوست/پروژه را بررسی می‌کند.
- `test_volume4.py` در **۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل** موفق شد: پنج شناسهٔ فصل پایدار، شکل SVG با ابعاد ۱۶۰۰×۱۰۰۰ و alt text، MathML/aria-label، لینک پاسخ‌نامه، پیوست اجرایی بایت‌به‌بایت و **۴۵ دارایی آفلاین** کنترل شدند.
- `test_mobile_layout.py` در **۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل** موفق شد؛ ناوبری RTL، overflow، cache/پوشش آفلاین، قالب نثر و تمام **۹۱۵ بخش** کتاب/دوره بررسی شدند. در جلد چهارم، ۳۰۶ بند نثری (۱۸۳ بند تورفته)، ۱۸ MathML و ۵ کپشن ثبت شد؛ فرمول، `aria-label`، alt text و کپشن برای تایپوگرافی دست‌کاری نشدند.
- هنگام مرور درخواست‌های محلی، یک 404 ازپیش‌موجود و نامرتبط با فصل برای `assets/images/genai/repo-thumbnailv4-fixed.11f1ce6a85d01461.webp` دیده شد؛ محتوای جلدهای قبلی تغییر نکرد.

این milestone وب/PWA و Markdown است. PDF و EPUB تولید یا آزموده نشده‌اند؛ بنابراین این گزارش گواه خروجی چاپی نیست. این آزمون‌ها همهٔ مرورگرها/دستگاه‌ها، اجرای GPU، مجوز هر تصویر واقعی یا کیفیت مدل را تأیید نمی‌کنند.
