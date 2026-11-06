# گزارش ممیزی فصل محلی ۱۲ / سراسری ۵۸ — اکوسیستم Hugging Face

**وضعیت:** ممیزی محلی تکمیل؛ آزمون پروژه، checker، build idempotent و آزمون مرورگر/آفلاین جلد موفق شدند. اجرای workflow راه دور پس از push معمولی بررسی می‌شود.

**تاریخ:** ۶ نوامبر ۲۰۲۶.

**مسیرها:** فصل `58-huggingface-stack.md`؛ پاسخ‌نامهٔ مستقل `../answers/58-huggingface-stack-fa.md`؛ پروژه `../projects/58-huggingface-stack/`؛ نمودار آفلاین `../diagrams/v4-ch12-huggingface-stack.svg`.

## نتایج اجرای واقعی

ترکیب نسخه‌ها در venv تازه روی Linux x86-64 / CPU نصب و آزمایش شد: CPython `3.13.16`, PyTorch `2.15.0+cpu`, Transformers `5.22.2`, Datasets `5.1.0`, Tokenizers `0.23.3`, Accelerate `1.15.0`, `huggingface_hub==2.4.0`, `pyarrow==26.0.1` و `fsspec==2026.7.0`. `python -m pip check` گزارش داد: `No broken requirements found`.

دستور `(cd book-engineering/projects/58-huggingface-stack && python -m unittest discover -v)` در همین venv **۱۲/۱۲ آزمون unit موفق** داشت. پوشش شامل hash و manifest fixture، schema و تعداد splitها، گروه‌های بدون overlap، رد label بولی/نامعتبر، آزمون `Dataset` و `Features`, ساخت BPE فقط از train، special tokenها، حذف ستون خام، padding/mask، اجرای CPU با گرادیان متناهی، ثبات trace برای seed ثابت، خطاهای `max_steps` و CLI آفلاین است.

اجرای `pipeline_demo.py --max-steps 2 --seed 58` با `Accelerator(cpu=True)` موفق شد؛ `accelerate launch --cpu --num_processes 1 --num_machines 1 --mixed_precision no --dynamo_backend no` نیز همان مسیر را جداگانه اجرا کرد. هر دو اجرای launcher و مستقیم CPU را گزارش کردند. build اولیهٔ جلد چهارم هم موفق بود: **۱۲/۱۵ فصل، ۲۵۱+۲۲=۲۷۳ بخش**؛ پیوست اجرایی دقیقاً با `pipeline_demo.py` تطبیق داشت.

## Fixture و خروجی

fixture `sample_data.jsonl` با `label_source=synthetic_fixture` ساختگی است، ۱۲ ردیف دارد و SHA-256 آن `eb21fe6a41dcd4dc828c00a7dc0293370087bb77fc6df022078fc16a20d750a2` است. Train شامل ۸ ردیف/۴ گروه و validation شامل ۴ ردیف/۲ گروه است؛ overlap گروهی صفر است. برچسب‌ها معنای زبانی یا کاربرد واقعی ندارند. Tokenizer روی train ساخته شد و هیچ متن validation وارد corpus ساخت آن نشد.

مدل `BertForSequenceClassification` از config محلی و وزن تصادفی ساخته شد: ۴٬۶۴۲ پارامتر trainable، batch size برابر ۲ و دو گام AdamW روی CPU. Lossهای trace‌شده `0.6931532621` و `0.6891556978` بودند؛ validation loss در `results.json` فقط `validation_loss_smoke_only` است. هیچ دادهٔ عمومی یا کاربر، pretrained model، token/اتصال Hub، GPU، benchmark یا سنجش تعمیم/کیفیت استفاده نشد.

## محدودیت‌ها و مرز ادعا

این آزمون فقط نشان می‌دهد APIهای pinشده در همین محیط، روی fixture آفلاین، از ingest تا batch و دو گام CPU اجرا شدند و loss/gradient متناهی بود. آزمون، سازگاری همهٔ OSها یا acceleratorها، ایمنی model repo، مجوز corpus، کیفیت زبان فارسی (model quality)، اعتبار splitهای مسئلهٔ واقعی، کارایی/VRAM، آموزش توزیع‌شده یا آمادگی محصول را ثابت نمی‌کند. صفحهٔ selector برخی مستندات Datasets در زمان بررسی هنوز `4.8.4` نشان می‌داد؛ APIهای پروژه با wheel واقعی `5.1.0` آزموده شدند و نباید اختلاف مستندات را پنهان کرد.

## بررسی نهایی جلد و انتشار

- `build_volume4.py` اجرای دوم را بدون تغییر `data.json` یا `volume-4-full-fa.md` گذراند؛ ۱۲/۱۵ فصل و ۲۷۳ بخش ثبت شد. `check_volume4.py` موفق بود: ۵۵ عبارت MathML دسترس‌پذیر، پیوست دقیق، fixture/hash، پاسخ‌نامه و گزارش.
- `test_volume4.py` در ۳۲۰، ۳۹۰ و ۱۴۴۰ پیکسل موفق شد؛ ناوبری، فرمول، diagram، پاسخ‌نامه، تطبیق appendix و ۱۲۱ دارایی آفلاین را بررسی کرد.
- `test_mobile_layout.py` در ۳۲۰، ۳۹۰، ۴۱۴، ۷۶۸ و ۱۴۴۰ پیکسل موفق شد؛ ۱٬۰۷۸ بخش، متن RTL، قفل viewport، و دسترسی آفلاین به فصل/پاسخ‌نامه/نمودار فصل ۵۸ بررسی شدند.
- workflow `.github/workflows/volume4-audit.yml` یک venv جدا برای snapshot فصل می‌سازد و `pip check`, دوازده آزمون، اجرای مستقیم و `accelerate launch` را آزمون می‌کند؛ نتیجهٔ راه دور پس از push عادی پایش خواهد شد.

PDF/EPUB تولید یا آزموده نمی‌شوند؛ خروجی وب/PWA و Markdown است. انتشار فقط در commit مستقل فصل محلی ۱۲/سراسری ۵۸، با push عادی و بدون force انجام می‌شود.
