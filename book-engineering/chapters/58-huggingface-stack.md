# جلد چهارم، فصل ۱۲ — اکوسیستم Hugging Face: از داده تا آموزش

> **جایگاه:** فصل محلی ۱۲ از ۱۵ جلد چهارم؛ فصل سراسری ۵۸. فصل ۵۷ Python و چارچوب‌های پایه را مقایسه کرد؛ اکنون زنجیره‌ای از ابزارهای Hugging Face را از داده تا batch و یک گام آموزش می‌سازیم. فصل ۵۹ به CUDA، ROCm، Triton و آموزش مقیاس‌پذیر می‌پردازد.
>
> **مرز موضوعی:** فصل‌های ۴۷ تا ۴۹ پس‌آموزش، PEFT و بهینه‌سازی ترجیح را پوشش داده‌اند؛ این فصل روش‌های آن‌ها را تکرار نمی‌کند. آموزش اینجا فقط smoke test کوچکی برای اتصال APIهاست. اجرای چند GPU، kernel optimization و benchmark به فصل بعد واگذار می‌شود.
>
> **حد ادعا:** نسخه‌ها snapshot تاریخ‌دارند. پروژه از fixture ساختگی، tokenizer محلی و مدل تصادفی روی CPU استفاده می‌کند؛ هیچ داده یا وزن pretrained از Hub نمی‌گیرد. خروجی آن نه کیفیت زبان فارسی، نه تعمیم، نه سرعت و نه آمادگی محصول را می‌سنجد.
>
> **تاریخ بازبینی منابع و آزمون محیط: ۶ نوامبر ۲۰۲۶.**

## ۱. از چهار کتابخانه، یک زنجیره بسازید

«Hugging Face» نام یک کتابخانهٔ واحد نیست. **Hub** محل میزبانی مخزن‌های مدل، داده و ابزار است؛ **Transformers** APIهای مدل و آموزش/استنتاج را عرضه می‌کند؛ **Datasets** خواندن و تبدیل مجموعه‌داده‌ها را سامان می‌دهد؛ **Tokenizers** موتورهای سریع tokenization می‌سازد و اجرا می‌کند؛ و **Accelerate** اجرای PyTorch را از CPU تا محیط‌های توزیع‌شده هماهنگ می‌کند. این اجزا می‌توانند کنار هم کار کنند، اما یکی جای دیگری را نمی‌گیرد.

مسیر آموزشی این فصل چنین است:

```text
فایل محلی و مجاز
       ↓
Dataset + splitهای ثبت‌شده
       ↓
Tokenizer + input_ids + attention_mask
       ↓
Collator → batchهای هم‌شکل
       ↓
مدل Transformers از config محلی
       ↓
Accelerate → یک smoke test روی CPU
       ↓
manifest نسخه، hash و محدودیت نتیجه
```

![شکل ۴-۱۲-۱ — مسیر آفلاین فصل از فایل و split ساختگی به ابزارهای Hugging Face: Dataset، Tokenizers، batch، مدل تصادفی و smoke test CPU با Accelerate؛ این نمودار benchmark، آموزش مقیاس‌پذیر یا سنجش کیفیت را نشان نمی‌دهد.](book-engineering/diagrams/v4-ch12-huggingface-stack.svg)

شکل ۴-۱۲-۱ — اتصال اجزا و مرز ادعا؛ Hub در مثال اجرایی استفاده نمی‌شود.

هدف این نیست که چهار نام را حفظ کنید. هدف آن است که برای هر مرحله بدانید **چه داده‌ای وارد می‌شود، کدام نسخه آن را تغییر می‌دهد، چه artifactی بیرون می‌آید و چگونه آن را آزمون می‌کنید**. پروژهٔ فصل مسیر فایل JSONL ساختگی → `DatasetDict` → tokenizer BPE → `DataCollatorWithPadding` → BERT بسیار کوچک و تصادفی → `Accelerator(cpu=True)` را اجرا می‌کند.

## ۲. Hub، کتابخانه و cache یکی نیستند

این سه مفهوم را از هم جدا کنید:

- **Hub repository:** مخزنی با شناسه، نوع (مثلاً `model` یا `dataset`)، تاریخچهٔ commit، فایل‌ها و کارت توضیحی. عمومی‌بودن یک مخزن به معنی مناسب‌بودن داده یا وزن آن برای مسئلهٔ شما نیست.
- **کتابخانه:** کدی که قالب یا معماری را می‌خواند و عملیات را اجرا می‌کند. `transformers`، `datasets`، `tokenizers` و `accelerate` بسته‌های Python هستند؛ خودشان به‌تنهایی وزن مدل یا مجوز داده نیستند.
- **Cache محلی:** نسخه‌های دریافت‌شده و فایل‌های پردازش‌شده‌ای که برای کم‌کردن دانلود یا محاسبهٔ دوباره نگهداری می‌شوند. cache یک روش دسترسی است، نه سند منشأ یا مجوز.

توابعی با نام `from_pretrained` می‌توانند فایل را از Hub دریافت کنند یا از فایل‌های محلی/cache بخوانند؛ نام تابع تضمین نمی‌کند که اجرای شما آفلاین باشد. گزینه‌هایی مانند `local_files_only=True` و متغیرهای حالت آفلاین فقط وقتی کار می‌کنند که artifact لازم از پیش موجود و کامل باشد. شناسهٔ repo و commit مورد استفاده را ثبت کنید؛ عبارت «از Hugging Face گرفتم» برای بازتولید نتیجه کافی نیست.

یک model card یا dataset card ممکن است معماری، کاربرد پیشنهادی، دادهٔ آموزش یا مجوز را توضیح دهد؛ اما کارتِ ناقص را با تضمین رسمی یکی نگیرید. خود فایل‌ها، مجوز واقعی، محدودیت دسترسی، سیاست نگهداری داده و سازگاری‌شان با محصول را جداگانه بررسی کنید.

## ۳. نسخه‌ها snapshot‌اند؛ سازگاری را نصب کنید و بیازمایید

نسخه‌های رسمیِ مشاهده‌شده در **۶ نوامبر ۲۰۲۶**:

| بسته | نسخهٔ stable در snapshot | تاریخ انتشار مشاهده‌شده | نکتهٔ سازگاری در metadata |
|---|---:|---|---|
| Transformers | `5.22.2` | ۶ نوامبر ۲۰۲۶، 15:43 UTC | Python `>=3.11`; backend PyTorch به `torch>=2.6` نیاز دارد؛ `tokenizers>=0.23.1,<0.24.0`; Hub `>=1.31,<3` |
| Datasets | `5.1.0` | ۵ اکتبر ۲۰۲۶ | Python `>=3.10`; core به `pyarrow>=24` و Hub `>=1.31,<3` نیاز دارد؛ برخی قابلیت‌های صوت/ویدئو وابستگی جدا دارند |
| Tokenizers | `0.23.3` | ۹ اکتبر ۲۰۲۶ | Python `>=3.10`; این نسخهٔ Python stable است؛ `1.0.0-rc.3` را stable جا نزنید |
| Accelerate | `1.15.0` | ۹ سپتامبر ۲۰۲۶ | Python `>=3.10`; PyTorch `>=2.0` |

شرط‌های بالای بسته، به‌تنهایی **آزمون ترکیب** نیستند. برای پروژهٔ این فصل، همهٔ چهار pin با CPython `3.13.16` و `torch==2.15.0+cpu` در venv مستقل نصب شدند؛ `pip check` موفق بود و آزمون end-to-end اجرا شد. محیط ثبت‌شده همچنین `huggingface_hub==2.4.0`, `pyarrow==26.0.1` و `fsspec==2026.7.0` داشت. این نتیجه فقط دربارهٔ همان Linux x86-64 / CPU و همان snapshot است؛ سازگاری Windows، macOS، CUDA یا ROCm از آن نتیجه نمی‌شود.

یک نکتهٔ مستندسازی: در زمان بازبینی، selector بعضی صفحه‌های Datasets هنوز `4.8.4` را نشان می‌داد، در حالی که release بستهٔ `5.1.0` در PyPI موجود بود. مرجع نسخهٔ نصب‌شده و آزمون پروژه، wheel pinشده و release note است؛ مثال‌های مستندات را برای همین ترکیب حتماً اجرا کنید. منابع و تاریخ مشاهده در بخش ۲۱ آمده‌اند.

## ۴. revision را به یک نقطهٔ ثابت وصل کنید

شاخه‌ای مثل `main` یا برچسبی مثل `latest` می‌تواند بعداً به محتوای دیگری اشاره کند. برای بازتولید، فقط نام repo را ذخیره نکنید؛ **نوع مخزن، شناسه، commit کامل، نام فایل‌ها و hashهای محلی** را ثبت کنید. برای نمونه، پس از دانلودِ مجاز و بازبینی‌شده می‌توان tokenizer محلی را بدون شبکه خواند:

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "organization/model-name",
    revision="<full-commit-sha>",
    local_files_only=True,
)
```

`<full-commit-sha>` جایگزین توضیحی است؛ هنگام اجرا باید با شناسهٔ commit واقعی عوض شود. اگر فایل در cache یا مسیر محلی نیست، حالت آفلاین آن را جادووار ایجاد نمی‌کند. `huggingface_hub` توابعی مثل `hf_hub_download` و `snapshot_download` برای دریافت artifact دارد؛ commit را به‌عنوان `revision` بدهید، سپس فهرست فایل‌ها و hash را نگه دارید [۸].

برای دادهٔ محلی، hash بایت‌های ورودی و schema را ثبت کنید. برای تبدیل‌ها، کد، seed، نام ستون‌ها و نسخهٔ کتابخانه را اضافه کنید. Cache یا fingerprint داخلی Datasets سودمند است، اما جایگزین ثبت فایل مبنا و دستورهای تبدیل نیست؛ ورودی بیرونی، تابع تصادفی یا نسخهٔ عوض‌شده می‌تواند خروجی را تغییر دهد.

## ۵. کد مدل و وزن را با اعتماد یکسان نگیرید

هنگام بارگذاری مدل‌های Auto، `trust_remote_code=True` می‌تواند کد Python موجود در repo مدل را اجرا کند. تنها وقتی آن را بپذیرید که کد را مرور کرده‌اید، نسخه را به commit مشخص مقید کرده‌اید، محیط اجرای جدا و مجوز مناسب دارید و به پیامد اجرای آن آگاهید. اگر معماری رسمی کتابخانه کافی است، مسیر پیش‌فرضِ بدون کد سفارشی را ترجیح دهید.

فایل‌های `safetensors` نسبت به بارگذاری سنتی pickle-based برای وزن tensor طراحی شده‌اند و خطر اجرای کد ناشی از deserialize pickle را کاهش می‌دهند؛ این انتخاب **تضمین بی‌خطری مدل، کد همراه، داده یا رفتار خروجی نیست**. منبع، revision، معماری، مجوز، فایل‌ها و کد را جدا بررسی کنید. توکن Hub را در فایل Python، notebook، log، fixture یا history مخزن ننویسید؛ اگر دریافت نیازمند دسترسی است، secret manager یا متغیر محیطی و دسترسی کمینه به کار ببرید.

برای Datasets نیز به راهنمای قدیمی توجه کنید: در release `4.0.0`، loading scriptها حذف و `trust_remote_code` دیگر پشتیبانی نشد؛ این تغییر در `5.1.0` نیز مهم است. دستورهای قدیمی که برای اجرای کد dataset روی Hub `trust_remote_code=True` می‌خواستند، راه‌حل امروز نیستند. قالب فایل پشتیبانی‌شده و سازوکار loader نسخهٔ خود را بررسی کنید [۴].

## ۶. Datasets داده را به schema قابل‌کار تبدیل می‌کند

`Dataset` یک جدول ستونی با schema و رفتار مناسب پردازش است؛ `DatasetDict` معمولاً چند split مانند `train`, `validation` و `test` را کنار هم نگه می‌دارد. `Features` نوع ستون‌ها را آشکار می‌کند: متن، عدد صحیح، کلاس، تصویر یا نوع‌های دیگر. در دادهٔ کوچک می‌توان از فایل محلی به `Dataset.from_list` رسید؛ در دادهٔ بزرگ‌تر، قالب‌هایی مانند Parquet، بارگذاری تدریجی یا حافظهٔ محدود را با نیاز واقعی بسنجید.

در ابتدای ingest این موارد را کنترل کنید:

- ستون ضروری موجود است؟ نوع آن برای همهٔ ردیف‌ها یکسان است؟
- شناسهٔ نمونه و شناسهٔ گروه/منشأ نگهداری می‌شود؟
- مقدارهای تهی، متن خالی، برچسب خارج از دامنه یا ردیف تکراری داریم؟
- مجوز، تاریخ تهیه و محدودیت استفادهٔ داده ثبت شده است؟
- آیا loader واقعاً فایل محلی می‌خواند، یا نام dataset باعث دانلود ناخواسته از Hub می‌شود؟

در پروژهٔ این فصل، `sample_data.jsonl` مستقیم خوانده و `DatasetDict` با `Features` مشخص ساخته می‌شود. هیچ loader از راه دور یا کد dataset اجرا نمی‌شود. دادهٔ تمرین کوچک است؛ برای میلیون‌ها نمونه، هزینهٔ RAM، cache، I/O و تبدیل را جدا اندازه بگیرید.

## ۷. پیش از tokenize، split را درست تعریف کنید

اگر دو ردیف از یک کاربر، سند، خانوادهٔ نزدیک یا منبع مشترک میان train و validation پخش شوند، مدل ممکن است چیزی بسیار شبیه نمونهٔ ارزیابی را هنگام آموزش دیده باشد. تقسیم تصادفی ردیف‌ها همیشه کافی نیست. نخست واحدِ مستقل تحلیل را تعیین کنید؛ سپس همهٔ موارد وابسته به یک `group_id` را یک‌جا به split بدهید و هم‌پوشانی گروه‌ها را بیازمایید.

`train` برای برازش پارامترها و (در این مثال) ساخت tokenizer محلی به کار می‌رود؛ `validation` برای بازبینی تصمیم‌ها و `test` برای سنجش نهاییِ جدا نگه داشته می‌شود. پس از دیدن نتیجهٔ test و تنظیم دوبارهٔ مدل، همان مجموعه دیگر test دست‌نخورده نیست. پروژهٔ فصل فقط train و validation ساختگی دارد و **test مستقل یا ارزیابی کیفیت ندارد**.

برای جلوگیری از leakage در preprocessing، statisticهایی مانند واژگانِ tokenizer، normalizationهای آموخته‌شده، انتخاب feature یا threshold را از دادهٔ validation/test برآورد نکنید، مگر طراحی آزمایش صریحاً چنین دسترسی را مجاز کرده و گزارش آن را آشکار کند. حتی tokenizer بدون برچسب هم می‌تواند از متن holdout اطلاعات بگیرد؛ برای مثال آموزشی، ساخت آن را به train محدود می‌کنیم.

## ۸. `map`, cache و streaming قراردادهای متفاوت‌اند

`Dataset.map` تابعی را روی ردیف‌ها یا batchها اجرا می‌کند و می‌تواند ستون‌های تازه بسازد یا ستون خام را حذف کند. `batched=True` به تابع چند مقدار هم‌زمان می‌دهد؛ اندازهٔ batch تبدیل را با حافظه و API مقصد هماهنگ کنید. `remove_columns` برای کنارگذاشتن متن خام پس از tokenization مفید است، ولی پیش از آن مطمئن شوید شناسه و منشأ لازم را در جای دیگری ثبت کرده‌اید.

دادهٔ map-style معمولاً index و دسترسی به ردیف دارد و امکان cache/تبدیل محلی را می‌دهد. `IterableDataset` در streaming برای پیمایش ترتیبی مناسب است و به معنای همان دسترسی تصادفیِ Dataset نیست؛ shuffle با buffer نمایندهٔ یک permutation سراسری از کل داده نیست. در streaming باید ترتیب shard، seed، اندازهٔ buffer، تعداد تکرار و سیاست resume را روشن کنید. وجود streaming به معنای «داده در حافظه نیست و همهٔ عملیات رایگان‌اند» نیست؛ شبکه، I/O، decoding و backpressure هم گلوگاه‌اند [۵].

در پروژهٔ فصل هیچ streaming انجام نمی‌شود؛ fixture فقط ۱۲ ردیف دارد. این انتخاب عمداً به ما امکان می‌دهد hash، split و محتوای ورودی را قبل از ساخت Dataset ببینیم. APIهای streaming را برای نسخهٔ دقیق خود از مستند رسمی و آزمون کوچک بررسی کنید.

## ۹. Tokenizer یک قرارداد مدل است، نه فقط تابع جداکنندهٔ واژه

Tokenization متن را به شناسه‌های عددی تبدیل می‌کند؛ مسیر معمول می‌تواند normalization، pre-tokenization، مدل واژگان/تقسیم، افزودن special token و decode را شامل شود. «توکن» الزاماً واژهٔ طبیعی نیست؛ ممکن است بخشی از واژه، بایت/نویسه یا نشانه باشد. مبانی BPE و خانواده‌های دیگر در فصل ۳۳ آمده است؛ اینجا قرارداد اجرایی مهم است.

برای زبان فارسی، normalization و سیاست فاصله، نیم‌فاصله، عربی/فارسی‌بودن کدپوینت حروف و نشانه‌گذاری می‌تواند نتیجه را عوض کند. اگر متن برای جست‌وجو، برچسب span یا نمایش highlight به متن اصلی بازمی‌گردد، offsetها را در همان tokenizer و همان normalization بیازمایید. یک tokenizer کوچک که روی چند سطر fixture آموزش دیده، پوشش یا کیفیت زبان فارسی را اثبات نمی‌کند.

`input_ids` عددهایی‌اند که مدل به‌عنوان index واژگان می‌خواند. بنابراین شناسهٔ tokenizer و `vocab_size` مدل به هم وابسته‌اند. عوض‌کردن tokenizer یک مدل pretrained، فقط «تغییر پیش‌پردازش» نیست: ترتیب شناسه‌ها باید با embeddingهای آموزش‌دیده سازگار باشد. resizeکردن embeddingها نیز به‌تنهایی معنای token تازه را یاد نمی‌دهد.

## ۱۰. `AutoTokenizer` موجود یا tokenizer تازه؟

اگر مدل ازپیش‌آموزش‌دیده‌ای را اجرا می‌کنید، tokenizer متناظر با همان مدل و همان revision را بارگذاری کنید؛ `AutoTokenizer` از config و فایل‌های model repo نوع مناسب را انتخاب می‌کند. بارگذاری و دسترسی cache/شبکه باید صریح باشد و revision کامل را ثبت کنید. ابتدا tokenizer و model را از یک artifact سازگار بگیرید؛ سپس special tokenها، `vocab_size`, padding و طول‌های مجاز را کنترل کنید.

اگر واقعاً باید tokenizer تازه بسازید، API کم‌سطح `tokenizers` اجزایی چون `Tokenizer`, `BPE`, pre-tokenizer و trainer را آشکار می‌کند. آن را فقط با داده‌ای بسازید که مجوز و split اجازه می‌دهد. `PreTrainedTokenizerFast` می‌تواند یک tokenizer object را به APIهای Transformers وصل کند. پروژهٔ ما همین مسیر آموزشی را دارد، ولی fixture آن فقط ۸ ردیف train و متن ساختگی است.

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.trainers import BpeTrainer
from transformers import PreTrainedTokenizerFast

raw = Tokenizer(BPE(unk_token="[UNK]"))
raw.pre_tokenizer = Whitespace()
raw.train_from_iterator(train_texts, trainer=BpeTrainer(special_tokens=["[PAD]", "[UNK]"]))
fast_tokenizer = PreTrainedTokenizerFast(
    tokenizer_object=raw, unk_token="[UNK]", pad_token="[PAD]"
)
```

این snippet فقط شکل API را نشان می‌دهد؛ پروژهٔ آزموده‌شده special tokenهای بیشتری دارد و template پردازش `[CLS]`/`[SEP]` را تعریف می‌کند. برای نمونهٔ آموزشی کوچک، کد پیوست همان مرجع اجرایی است.

## ۱۱. truncation، padding و mask را قابل مشاهده کنید

طول دنباله باید با محدودیت معماری و حافظه سازگار باشد. `truncation=True` متن بلندتر از حد را کوتاه می‌کند؛ چه بخشی حذف می‌شود، ممکن است برای مسئله مهم باشد و باید آزموده شود. padding ردیف‌های کوتاه‌تر را هم‌اندازه می‌کند تا به tensor batch تبدیل شوند. `attention_mask` معمولاً token واقعی را از pad جدا می‌کند؛ mask به معنی حذف خودکار همهٔ اثرهای طول یا padding از کد شما نیست.

Padding ثابت تا بیشینهٔ طول ساده است اما برای batch کوتاه می‌تواند محاسبهٔ اضافی ایجاد کند. `DataCollatorWithPadding` معمولاً بر اساس بلندترین عضو هر batch pad می‌کند. برای تولید batch، ستون متنی خام را پس از encode کنار بگذارید یا collator مخصوصی بنویسید؛ اگر رشته‌های متفاوت وارد تبدیل مستقیم به tensor شوند، خطاهای «cannot create tensor» یا شکل نامنظم می‌بینید.

Special tokenهای `[PAD]`, `[UNK]`, `[CLS]`, `[SEP]` یا tokenهای اختصاصی مدل، شناسهٔ ثابت و وظیفهٔ مشخص دارند. مقدار آن‌ها را حدس نزنید: از tokenizer بپرسید و در manifest ثبت کنید. پروژه برای آزمون خود شناسه‌ها را چاپ/ثبت می‌کند؛ عددهای همان fixture قرارداد عمومی همهٔ tokenizerها نیستند.

## ۱۲. از Dataset به مدل: ستون‌ها و اندازه‌ها را تطبیق دهید

الگوی مفهومی تبدیل batch چنین است:

```python
encoded = dataset.map(
    tokenize_batch,
    batched=True,
    remove_columns=["example_id", "group_id", "split", "text"],
)
collator = DataCollatorWithPadding(tokenizer=tokenizer, return_tensors="pt")
```

پیش از آموزش، یک batch واقعی را inspect کنید:

- `input_ids` باید tensor صحیح با shape `[batch, sequence]` و شناسه‌های در دامنهٔ `vocab_size` باشد.
- `attention_mask` باید هم‌شکل باشد و مقادیر قابل‌انتظار برای token/padding داشته باشد.
- برچسب باید dtype و shape مناسب loss داشته باشد؛ collator ممکن است `label` را به کلید `labels` تبدیل کند.
- `max_length` tokenizer باید با `max_position_embeddings` مدل سازگار باشد.
- همهٔ ستون‌های metadata را به مدل پاس ندهید؛ مدل فقط ورودی‌های مورد انتظارش را می‌پذیرد.

عبور موفق `map` یا ساخت DataLoader هنوز نشان نمی‌دهد برچسب‌ها معنا دارند یا split مستقل است. به همین دلیل پروژه پیش از training، schema، تعداد ردیف، هم‌پوشانی گروه و hash را کنترل می‌کند و بعد از map فقط ستون `label`, `input_ids` و `attention_mask` را نگه می‌دارد.

## ۱۳. `Trainer` و `Accelerator` دو سطح API هستند

**`Trainer`** از Transformers API سطح‌بالاست: برای supervised fine-tuning متعارف، تنظیم argumentها، logging، evaluation و checkpointها از حلقهٔ دست‌نویس کوتاه‌تر است. این سطح مسئولیت شما را حذف نمی‌کند؛ split، معیار، callback، سیاست save، بارگذاری امن و نسخه‌ها همچنان باید روشن باشند.

**`Accelerator`** از Accelerate برای ساخت حلقهٔ PyTorch سفارشی مناسب‌تر است: model، optimizer و dataloader را با `prepare` آماده می‌کنید و loss را از مسیر `accelerator.backward` پس‌انتشار می‌دهید. `accelerate launch` راه اجرای همان برنامه با تنظیمات اجراست. در پروژهٔ این فصل یک مسیر سادهٔ Accelerator را استفاده می‌کنیم تا حرکت batch، gradient و optimizer آشکار بماند.

از wrapperهای هر دو سطح بی‌برنامه استفاده نکنید. `Trainer` خودش از زیرساخت Accelerate بهره می‌گیرد؛ معمولاً نباید Trainer را بسازید، اجزای داخلی‌اش را دوباره با `Accelerator.prepare` بپیچید و انتظار رفتار عادی داشته باشید. برای یک حلقهٔ سفارشی، Accelerator را مستقیم برگزینید؛ برای قرارداد استاندارد، Trainer و API مستند همان نسخه را به کار ببرید.

## ۱۴. `Accelerator` به‌تنهایی سرعت یا چند GPU نمی‌سازد

در مثال پروژه، `Accelerator(cpu=True)` دستگاه را صریحاً CPU می‌کند. سپس مدل، optimizer و DataLoader آماده و loss از `accelerator.backward` عبور داده می‌شود. این smoke test ثابت می‌کند مسیر API در محیط ثبت‌شده اجرا شده؛ این نشان نمی‌دهد GPU پیدا شده، چند GPU فعال است یا کد بهینه شده است.

برای اجرا، یک venv با وابستگی‌های pin‌شده لازم است. `accelerate launch` فرایند را با تنظیمات انتخابی اجرا می‌کند؛ برای CPU می‌توان `--cpu --num_processes 1` را آشکار نوشت. config launcher، distributed backend، mixed precision و driver باید با محیط هدف جور باشند. فصل ۵۹ به سخت‌افزار و مقیاس می‌پردازد؛ اینجا از benchmark یا آزمایش شتاب‌دهنده صرف‌نظر می‌کنیم.

## ۱۵. loss عددی است؛ کیفیت نیست

برای طبقه‌بندی چندکلاسه، cross-entropy معمولاً از احتمال مدل به برچسب هدف محاسبه می‌شود. اگر `y[i,c]` نشانگر کلاس درست و `p[i,c]` احتمال پیش‌بینی‌شده باشد، شکل میانگین آن چنین است:

**متن جایگزین فرمول:** میانگین cross-entropy برابر است با منفیِ میانگین روی نمونه‌ها و کلاس‌ها از نشانگر برچسب ضرب‌در لگاریتم احتمال پیش‌بینی‌شده.

<math display="block" aria-label="L equals negative one over N times sum over i and c of y i c times natural logarithm of p i c">
  <mrow>
    <mi mathvariant="script">L</mi><mo>=</mo><mo>−</mo><mfrac><mn>1</mn><mi>N</mi></mfrac>
    <munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>N</mi></munderover>
    <munderover><mo>∑</mo><mrow><mi>c</mi><mo>=</mo><mn>1</mn></mrow><mi>C</mi></munderover>
    <msub><mi>y</mi><mrow><mi>i</mi><mo>,</mo><mi>c</mi></mrow></msub>
    <mi>log</mi><mo>⁡</mo><msub><mi>p</mi><mrow><mi>i</mi><mo>,</mo><mi>c</mi></mrow></msub>
  </mrow>
</math>

`loss` فقط عددی برای تابع هدف است. در پروژه، fixture بسیار کوچک و برچسب‌های آن قراردادی‌اند؛ دو گام با وزن تصادفی نه مدل مفیدی می‌سازند و نه دلیل خوبی برای مقایسهٔ روش‌ها می‌دهند. `validation_loss_smoke_only` در `results.json` صرفاً اثبات می‌کند محاسبهٔ forward روی split کنارگذاشته‌شده اجرا شده؛ آن را امتیاز کیفیت یا نتیجهٔ پژوهشی گزارش نکنید.

## ۱۶. نسخه، داده و اجرا را یک‌جا ثبت کنید

`pip freeze` به‌تنهایی بازتولیدپذیری را تضمین نمی‌کند. حداقل این موارد را ثبت کنید:

1. Python، سیستم‌عامل/معماری، device، driver/runtime و نسخهٔ چارچوب‌ها.
2. فایل ورودی، hash، مجوز، schema، ID گروه‌ها و سیاست split.
3. tokenizer/model repo، نوع artifact، revision commit کامل، hash و فایل‌های مورد استفاده.
4. دستورهای preprocessing، طول حداکثر، truncation/padding، collator و seed.
5. config معماری، optimizer، batch size، تعداد step، دقت محاسبه و هر ارزیابی.
6. آنچه **انجام نشده**: وزن pretrained، GPU، benchmark، دادهٔ واقعی یا معیار تعمیم.

پروژهٔ فصل `requirements.txt` را برای pinهای مستقیم، `requirements-cpu.txt` را برای wheel CPU و `requirements-lock-linux-py313.txt` را برای dependencyهای resolveشدهٔ همان محیط دارد. lock سوم برای Linux/CPython 3.13 نوشته شده و نباید به سیستم‌عامل یا نسخهٔ دیگر تعمیم داده شود. `environment.json` نسخه‌های مهم، `fixture_manifest.json` hash و splitها و `results.json` خروجی اجرای ثبت‌شده را نگه می‌دارند.

## ۱۷. اجرای پروژه و خواندن نتیجه

در Linux x86-64 با CPython 3.13، راه‌اندازی جداگانهٔ PyTorch CPU از index رسمی و سپس نصب lock، بعد از آن `pip check` و آزمون‌های واحد انجام می‌شود. دستورهای کامل در README پروژه آمده‌اند. پس از نصب، اجرای زیر باید بدون تماس با Hub کار کند:

```bash
HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 \
  python pipeline_demo.py --max-steps 2 --seed 58 --output results.json
```

در snapshot آزموده‌شده، hash fixture برابر `eb21fe6a41dcd4dc828c00a7dc0293370087bb77fc6df022078fc16a20d750a2` بود؛ train شامل ۸ ردیف و ۴ گروه و validation شامل ۴ ردیف و ۲ گروه بود. tokenizer روی ۸ ردیف train آموزش دید و واژگان fixture آن ۹۶ شناسه داشت. مدل BERT کوچک با ۴٬۶۴۲ پارامتر trainable از config تصادفی ساخته شد و دو گام CPU، lossهای `0.6931533` و `0.6891557` و gradientهای متناهی تولید کرد.

این اعداد **trace اجرای همان smoke test** هستند، نه هدف یا benchmark. اختلاف نسخهٔ CPU، کتابخانهٔ عددی یا محیط ممکن است مقدار اعشاری را تغییر دهد؛ نتیجهٔ قابل‌توجه، پایان موفق، finite بودن gradientها، hash و device ثبت‌شده است. هیچ ادعایی دربارهٔ دقت/کارایی مدل از این اعداد استخراج نمی‌شود.

## ۱۸. خطاهای رایج و عیب‌یابی مرحله‌ای

| نشانه | پرسش اول | اقدام امن |
|---|---|---|
| خطای دانلود در حالت آفلاین | آیا همهٔ فایل‌های دقیق همان revision از پیش در cache/مسیر محلی‌اند؟ | manifest و cache را بازبینی کنید؛ offline mode فایل گمشده را تهیه نمی‌کند. |
| خطای `trust_remote_code` یا مدل ناشناخته | آیا repo به معماری یا کد سفارشی نیاز دارد؟ | کد و commit را بررسی و در sandbox جدا اجرا کنید؛ Datasets جدید scriptهای قدیمی را اجرا نمی‌کند. |
| خطای `vocab_size`, index یا embedding | آیا tokenizer و وزن/config از همان revision/واژگان‌اند؟ | `len(tokenizer)`, `config.vocab_size`, شناسهٔ tokenها و حد ورودی را تطبیق دهید؛ IDها را تصادفی remap نکنید. |
| خطای تبدیل tensor به‌خاطر string یا طول‌های متفاوت | آیا متن/metadata در dataset خروجی مانده یا padding فعال است؟ | ستون خام را آگاهانه حذف کنید و `DataCollatorWithPadding` را روی چند ردیف inspect کنید. |
| train خوب به نظر می‌رسد، validation عجیب است | آیا گروه/منبع مشترک، near-duplicate یا preprocessing آموخته‌شده میان splitها نشت کرده؟ | split را بر اساس گروه بازسازی و hash/IDها را آزمون کنید؛ پس از دیدن test آن را برای تنظیم دوباره مصرف نکنید. |
| Accelerate دستگاه یا process متفاوت می‌سازد | آیا launcher config، `--cpu`, تعداد process و device با هدف یکی‌اند؟ | اول تک‌پردازه و CPU را بازتولید کنید؛ بعد distributed را جدا اضافه کنید و ثبت کنید. |

## ۱۹. تمرین‌ها

۱. برای مجموعه‌ای فرضی که چند جمله از یک سند دارد، `group_id` مناسب تعریف کنید. توضیح دهید چرا تقسیم تصادفی جمله‌ها ممکن است نتیجه را خوش‌بینانه کند.

۲. دو سطر validation به fixture اضافه کنید که یک گروه تازه دارند. manifest، hash و آزمون‌ها را به‌روز کنید؛ هیچ متن validation را وارد آموزش tokenizer نکنید.

۳. با بررسی model card و commit یک مدل مجاز، فهرست فایل‌های لازم را بنویسید. مشخص کنید برای اجرای کامل کدام موارد باید محلی cache شوند تا `local_files_only=True` کار کند.

۴. چه زمانی `Dataset` map-style و چه زمانی `IterableDataset` می‌خواهید؟ برای streaming توضیح دهید چرا buffer shuffle همان shuffle سراسری و چرا iteration همان دسترسی تصادفی نیست.

۵. تیمی می‌خواهد `trust_remote_code=True` را روی محیطی با کلیدهای cloud اجرا کند. threat model کوتاهی بنویسید و دست‌کم سه کنترل کم‌هزینه پیشنهاد دهید.

۶. `max_steps` را از ۲ به ۳ تغییر دهید، seed و hash را ثابت نگه دارید و دو خروجی را مقایسه کنید. کدام بخش‌ها باید ثابت باشند و چرا اختلاف lossها اثبات بهترشدن مدل نیست؟

۷. برای آموزش استاندارد یک classifier در برابر حلقهٔ سفارشی با چند منطق loss، بین `Trainer` و `Accelerator` انتخاب کنید. قراردادهای مسئولیت و آزمایش موردنیاز هر انتخاب را بنویسید.

## ۲۰. جمع‌بندی و مسیر بعد

در این فصل دیدیم که مخزن Hub، کتابخانه، cache، Dataset، tokenizer و حلقهٔ آموزش نقش‌های جدا دارند. نسخهٔ دقیق، revision ثابت، fixture hash، split گروهی، tokenizer منطبق با مدل و batchهای inspect‌شده، خط لوله را قابل بازبینی‌تر می‌کنند. اما هیچ‌یک از آن‌ها مجوز داده، ایمنی مدل، کیفیت نتیجه یا کارایی سخت‌افزار را خودکار تضمین نمی‌کند.

تمرین‌ها پاسخ یگانه ندارند؛ پاسخ نمونه با معیار و فرض‌ها در [پاسخ‌نامهٔ مستقل فصل ۵۸](book-engineering/answers/58-huggingface-stack-fa.md) آمده است. پروژه و محدودیت‌های نتیجه در [گزارش ممیزی](book-engineering/chapters/58-audit-report-fa.md) ثبت می‌شوند. فصل ۵۹ از همین مرز عبور می‌کند و به سخت‌افزار، driver، CUDA/ROCm، Triton و مقیاس می‌پردازد؛ این فصل benchmark آن موضوع‌ها نیست.

## ۲۱. منابع و تاریخ بازبینی

صفحه‌های زیر در ۶ نوامبر ۲۰۲۶ بازبینی شده‌اند؛ تاریخ انتشار artifactها در جدول بخش ۳ آمده است. مستندات زنده ممکن است selector نسخه‌شان با wheel مورد استفاده فرق کند؛ نسخه و اجرای واقعی پروژه را معیار سازگاری این مثال بگیرید.

1. Hugging Face, [Transformers releases](https://github.com/huggingface/transformers/releases) و [release `v5.22.2`](https://github.com/huggingface/transformers/releases/tag/v5.22.2), 2026-11-06.
2. Hugging Face, [Transformers installation](https://huggingface.co/docs/transformers/en/installation) و [model loading](https://huggingface.co/docs/transformers/en/models), مشاهده در 2026-11-06.
3. Hugging Face, [Datasets release `5.1.0`](https://github.com/huggingface/datasets/releases/tag/5.1.0), 2026-10-05.
4. Hugging Face, [Datasets release `4.0.0`](https://github.com/huggingface/datasets/releases/tag/4.0.0), 2025-07-09؛ حذف loading scriptها و توقف پشتیبانی `trust_remote_code`.
5. Hugging Face, [Datasets loading](https://huggingface.co/docs/datasets/en/loading) و [stream](https://huggingface.co/docs/datasets/en/stream), مشاهده در 2026-11-06؛ در بازبینی، selector یکی از صفحات هنوز `4.8.4` بود.
6. Hugging Face, [Tokenizers release `0.23.3`](https://github.com/huggingface/tokenizers/releases/tag/v0.23.3), 2026-10-09 و [Quicktour](https://huggingface.co/docs/tokenizers/en/quicktour), مشاهده در 2026-11-06.
7. Hugging Face, [Accelerate release `1.15.0`](https://github.com/huggingface/accelerate/releases/tag/v1.15.0), 2026-09-09 و [Quicktour](https://huggingface.co/docs/accelerate/en/quicktour), مشاهده در 2026-11-06.
8. Hugging Face Hub, [download guide](https://huggingface.co/docs/huggingface_hub/en/guides/download), مشاهده در 2026-11-06؛ cache و pinکردن `revision` روی commit.
9. PyPI JSON metadata برای [`transformers`](https://pypi.org/pypi/transformers/json)، [`datasets`](https://pypi.org/pypi/datasets/json)، [`tokenizers`](https://pypi.org/pypi/tokenizers/json) و [`accelerate`](https://pypi.org/pypi/accelerate/json), استعلام 2026-11-06؛ منبع شرط‌های Python و وابستگی‌ها، نه تضمین سازگاری انتهابه‌انتها.
10. پروژهٔ آزموده‌شده: [README و manifest محیط](book-engineering/projects/58-huggingface-stack/README.md), [fixture و hash](book-engineering/projects/58-huggingface-stack/fixture_manifest.json), [نتایج ثبت‌شده](book-engineering/projects/58-huggingface-stack/results.json); snapshot محلی CPU در 2026-11-06.

## ۲۲. پیوست اجرایی: فایل آزموده‌شدهٔ پروژه

کد زیر همان `book-engineering/projects/58-huggingface-stack/pipeline_demo.py` است. آزمون‌ها در Python 3.13.16/Linux x86-64 با نسخه‌های ثبت‌شده در `environment.json` اجرا شدند. اجرای آن به Hub یا وزن pretrained نیاز ندارد.

```python
"""Run a tiny, offline Hugging Face data-to-CPU-training smoke test.

The project reads only its checked-in synthetic JSONL fixture. It trains a
byte-pair tokenizer on the train split, maps both splits to token IDs, pads
batches, initializes a small random BERT from config, and takes fixed CPU steps
through Accelerate. It never contacts the Hub or loads pretrained weights.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["HF_DATASETS_DISABLE_PROGRESS_BARS"] = "1"

import accelerate
import datasets
import tokenizers
import torch
import transformers
from accelerate import Accelerator
from datasets import Dataset, DatasetDict, Features, Value, disable_progress_bar
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.processors import TemplateProcessing
from tokenizers.trainers import BpeTrainer
from torch.utils.data import DataLoader
from transformers import (
    BertConfig,
    BertForSequenceClassification,
    DataCollatorWithPadding,
    PreTrainedTokenizerFast,
)

ROOT = Path(__file__).resolve().parent
DEFAULT_FIXTURE = ROOT / "sample_data.jsonl"
DEFAULT_MANIFEST = ROOT / "fixture_manifest.json"
DEFAULT_OUTPUT = ROOT / "results.json"
FIXTURE_ID = "v4-ch12-synthetic-text-pipeline-v1"
MAX_LENGTH = 24
BATCH_SIZE = 2
VOCAB_SIZE = 96
SPECIAL_TOKENS = ("[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]")
FEATURES = Features(
    {
        "example_id": Value("string"),
        "group_id": Value("string"),
        "split": Value("string"),
        "text": Value("string"),
        "label": Value("int64"),
    }
)


class PipelineInputError(ValueError):
    """Raised when the synthetic fixture or its manifest is invalid."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PipelineInputError(f"cannot read fixture manifest: {error}") from error
    if not isinstance(manifest, dict):
        raise PipelineInputError("fixture manifest must be a JSON object")
    if manifest.get("schema_version") != 1 or manifest.get("fixture_id") != FIXTURE_ID:
        raise PipelineInputError("unsupported fixture manifest identity")
    if manifest.get("label_source") != "synthetic_fixture":
        raise PipelineInputError("fixture manifest must identify labels as synthetic_fixture")
    digest = manifest.get("sha256")
    if not isinstance(digest, str) or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise PipelineInputError("fixture manifest sha256 must be 64 lowercase hexadecimal characters")
    return manifest


def _validate_records(records: Any, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(records, list) or not records:
        raise PipelineInputError("fixture must contain at least one JSONL record")
    required = {"example_id", "group_id", "split", "text", "label"}
    seen_ids: set[str] = set()
    groups_to_splits: dict[str, set[str]] = defaultdict(set)
    split_counts: Counter[str] = Counter()
    split_groups: dict[str, set[str]] = defaultdict(set)
    label_counts: dict[str, Counter[str]] = defaultdict(Counter)
    cleaned: list[dict[str, Any]] = []
    for row_no, row in enumerate(records, start=1):
        if not isinstance(row, dict) or set(row) != required:
            raise PipelineInputError(f"record {row_no} must contain exactly {sorted(required)}")
        for field in ("example_id", "group_id", "split", "text"):
            if not isinstance(row[field], str) or not row[field].strip():
                raise PipelineInputError(f"record {row_no} field {field} must be a non-empty string")
        if row["split"] not in {"train", "validation"}:
            raise PipelineInputError(f"record {row_no} has unsupported split {row['split']!r}")
        label = row["label"]
        if isinstance(label, bool) or not isinstance(label, int) or label not in (0, 1):
            raise PipelineInputError(f"record {row_no} label must be integer 0 or 1")
        if row["example_id"] in seen_ids:
            raise PipelineInputError(f"duplicate example_id {row['example_id']!r}")
        seen_ids.add(row["example_id"])
        groups_to_splits[row["group_id"]].add(row["split"])
        split_counts[row["split"]] += 1
        split_groups[row["split"]].add(row["group_id"])
        label_counts[row["split"]][str(label)] += 1
        cleaned.append(dict(row))
    leaking_groups = sorted(group for group, splits in groups_to_splits.items() if len(splits) != 1)
    if leaking_groups:
        raise PipelineInputError(f"group_id values cross splits: {leaking_groups}")

    expected_rows = manifest.get("record_count")
    expected_splits = manifest.get("split_record_counts")
    expected_groups = manifest.get("split_group_counts")
    expected_labels = manifest.get("label_counts")
    if len(cleaned) != expected_rows:
        raise PipelineInputError(f"record count {len(cleaned)} does not match manifest {expected_rows}")
    actual_splits = {name: split_counts[name] for name in ("train", "validation")}
    actual_groups = {name: len(split_groups[name]) for name in ("train", "validation")}
    actual_labels = {
        name: {label: label_counts[name][label] for label in ("0", "1")}
        for name in ("train", "validation")
    }
    if actual_splits != expected_splits:
        raise PipelineInputError("split record counts do not match fixture manifest")
    if actual_groups != expected_groups:
        raise PipelineInputError("split group counts do not match fixture manifest")
    if actual_labels != expected_labels:
        raise PipelineInputError("split label counts do not match fixture manifest")
    return cleaned


def load_fixture(
    fixture_path: Path = DEFAULT_FIXTURE,
    manifest_path: Path = DEFAULT_MANIFEST,
) -> tuple[list[dict[str, Any]], dict[str, Any], str]:
    try:
        raw_bytes = fixture_path.read_bytes()
    except OSError as error:
        raise PipelineInputError(f"cannot read fixture: {error}") from error
    manifest = _read_manifest(manifest_path)
    digest = _sha256(raw_bytes)
    if digest != manifest["sha256"]:
        raise PipelineInputError("fixture sha256 does not match fixture manifest")
    records: list[dict[str, Any]] = []
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise PipelineInputError("fixture must be UTF-8 encoded") from error
    for line_no, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            raise PipelineInputError(f"blank JSONL line at {line_no}; keep one record per line")
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise PipelineInputError(f"invalid JSON on line {line_no}: {error.msg}") from error
    return _validate_records(records, manifest), manifest, digest


def split_records(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return {
        name: [row for row in records if row["split"] == name]
        for name in ("train", "validation")
    }


def build_datasets(records: list[dict[str, Any]]) -> DatasetDict:
    splits = split_records(records)
    if not splits["train"] or not splits["validation"]:
        raise PipelineInputError("both train and validation splits must be non-empty")
    return DatasetDict(
        {
            name: Dataset.from_list(rows, features=FEATURES)
            for name, rows in splits.items()
        }
    )


def train_fast_tokenizer(train_rows: list[dict[str, Any]]) -> PreTrainedTokenizerFast:
    if not train_rows:
        raise PipelineInputError("tokenizer training requires at least one train row")
    tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
    tokenizer.pre_tokenizer = Whitespace()
    trainer = BpeTrainer(
        vocab_size=VOCAB_SIZE,
        min_frequency=1,
        special_tokens=list(SPECIAL_TOKENS),
    )
    tokenizer.train_from_iterator((row["text"] for row in train_rows), trainer=trainer)
    cls_id = tokenizer.token_to_id("[CLS]")
    sep_id = tokenizer.token_to_id("[SEP]")
    if cls_id is None or sep_id is None:
        raise RuntimeError("tokenizer training did not retain the required special tokens")
    tokenizer.post_processor = TemplateProcessing(
        single="[CLS] $A [SEP]",
        pair="[CLS] $A [SEP] $B:1 [SEP]:1",
        special_tokens=[("[CLS]", cls_id), ("[SEP]", sep_id)],
    )
    fast = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer,
        unk_token="[UNK]",
        pad_token="[PAD]",
        cls_token="[CLS]",
        sep_token="[SEP]",
        mask_token="[MASK]",
    )
    fast.model_max_length = MAX_LENGTH
    return fast


def tokenize_splits(
    raw_datasets: DatasetDict,
    tokenizer: PreTrainedTokenizerFast,
) -> DatasetDict:
    disable_progress_bar()

    def encode_batch(batch: dict[str, list[Any]]) -> dict[str, Any]:
        return tokenizer(batch["text"], truncation=True, max_length=MAX_LENGTH)

    remove_columns = ["example_id", "group_id", "split", "text"]
    return raw_datasets.map(
        encode_batch,
        batched=True,
        remove_columns=remove_columns,
        load_from_cache_file=False,
        desc="Tokenize the fixed synthetic fixture",
    )


def _split_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels = Counter(str(row["label"]) for row in rows)
    return {
        "records": len(rows),
        "groups": len({row["group_id"] for row in rows}),
        "group_ids": sorted({row["group_id"] for row in rows}),
        "label_counts": {label: labels[label] for label in ("0", "1")},
    }


def _package_versions() -> dict[str, str]:
    return {
        "torch": str(torch.__version__),
        "transformers": str(transformers.__version__),
        "datasets": str(datasets.__version__),
        "tokenizers": str(tokenizers.__version__),
        "accelerate": str(accelerate.__version__),
    }


def run_pipeline(
    fixture_path: Path = DEFAULT_FIXTURE,
    manifest_path: Path = DEFAULT_MANIFEST,
    *,
    seed: int = 58,
    max_steps: int = 2,
) -> dict[str, Any]:
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise PipelineInputError("seed must be a non-negative integer")
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps < 1:
        raise PipelineInputError("max_steps must be a positive integer")

    records, manifest, fixture_sha256 = load_fixture(fixture_path, manifest_path)
    splits = split_records(records)
    if max_steps > (len(splits["train"]) + BATCH_SIZE - 1) // BATCH_SIZE:
        raise PipelineInputError("max_steps exceeds the number of train batches in this one-epoch smoke test")
    raw_datasets = build_datasets(records)
    tokenizer = train_fast_tokenizer(splits["train"])
    tokenized = tokenize_splits(raw_datasets, tokenizer)
    collator = DataCollatorWithPadding(tokenizer=tokenizer, return_tensors="pt")

    torch.manual_seed(seed)
    torch.set_num_threads(1)
    generator = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(
        tokenized["train"],
        batch_size=BATCH_SIZE,
        shuffle=True,
        generator=generator,
        collate_fn=collator,
    )
    validation_loader = DataLoader(
        tokenized["validation"],
        batch_size=BATCH_SIZE,
        shuffle=False,
        collate_fn=collator,
    )

    config = BertConfig(
        vocab_size=len(tokenizer),
        hidden_size=16,
        num_hidden_layers=1,
        num_attention_heads=2,
        intermediate_size=32,
        max_position_embeddings=MAX_LENGTH + 8,
        num_labels=2,
        pad_token_id=tokenizer.pad_token_id,
        hidden_dropout_prob=0.0,
        attention_probs_dropout_prob=0.0,
        classifier_dropout=0.0,
    )
    model = BertForSequenceClassification(config)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    accelerator = Accelerator(cpu=True)
    if accelerator.device.type != "cpu":
        raise RuntimeError(f"CPU-only smoke test received unexpected device {accelerator.device}")
    model, optimizer, train_loader = accelerator.prepare(model, optimizer, train_loader)

    training_losses: list[float] = []
    finite_gradients = True
    model.train()
    for step, batch in enumerate(train_loader):
        if step >= max_steps:
            break
        optimizer.zero_grad(set_to_none=True)
        output = model(**batch)
        loss = output.loss
        if loss is None or not torch.isfinite(loss).item():
            raise RuntimeError("training returned a non-finite loss")
        accelerator.backward(loss)
        finite_gradients = finite_gradients and all(
            parameter.grad is None or torch.isfinite(parameter.grad).all().item()
            for parameter in model.parameters()
        )
        if not finite_gradients:
            raise RuntimeError("training returned a non-finite gradient")
        training_losses.append(float(loss.detach().cpu().item()))
        optimizer.step()
    if len(training_losses) != max_steps:
        raise RuntimeError(f"completed {len(training_losses)} training steps, expected {max_steps}")

    model.eval()
    evaluation_losses: list[float] = []
    validation_loader = accelerator.prepare(validation_loader)
    with torch.no_grad():
        for batch in validation_loader:
            output = model(**batch)
            if output.loss is None or not torch.isfinite(output.loss).item():
                raise RuntimeError("validation smoke loss is non-finite")
            evaluation_losses.append(float(output.loss.detach().cpu().item()))

    return {
        "schema_version": 1,
        "fixture_id": manifest["fixture_id"],
        "fixture_sha256": fixture_sha256,
        "label_source": manifest["label_source"],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "packages": _package_versions(),
            "accelerator_device": str(accelerator.device),
            "distributed_type": str(accelerator.distributed_type),
        },
        "data": {
            "splits": {
                name: _split_summary(rows)
                for name, rows in splits.items()
            },
            "group_overlap": sorted(
                set(row["group_id"] for row in splits["train"])
                & set(row["group_id"] for row in splits["validation"])
            ),
            "dataset_columns_after_tokenization": {
                name: list(tokenized[name].column_names)
                for name in ("train", "validation")
            },
        },
        "tokenizer": {
            "implementation": "tokenizers BPE wrapped by PreTrainedTokenizerFast",
            "trained_on_split": "train",
            "training_example_ids": [row["example_id"] for row in splits["train"]],
            "training_text_sha256": _sha256(
                "\n".join(row["text"] for row in splits["train"]).encode("utf-8")
            ),
            "vocab_size": len(tokenizer),
            "special_token_ids": {
                name: tokenizer.convert_tokens_to_ids(name)
                for name in SPECIAL_TOKENS
            },
            "max_length": MAX_LENGTH,
        },
        "model": {
            "class": "BertForSequenceClassification",
            "weights": "randomly_initialized_from_config",
            "pretrained_weights_loaded": False,
            "trainable_parameters": sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad),
            "hidden_size": config.hidden_size,
            "layers": config.num_hidden_layers,
            "num_labels": config.num_labels,
        },
        "training": {
            "performed": True,
            "seed": seed,
            "optimizer": "torch.optim.AdamW",
            "learning_rate": 1e-3,
            "batch_size": BATCH_SIZE,
            "steps": len(training_losses),
            "training_losses": training_losses,
            "all_gradients_finite": finite_gradients,
            "validation_loss_smoke_only": evaluation_losses,
            "validation_used_for_optimization": False,
            "device": str(accelerator.device),
        },
        "scope": {
            "real_user_or_public_data_used": False,
            "hub_access_or_download": False,
            "pretrained_weights_used": False,
            "validation_used_for_optimization": False,
            "gpu_used": False,
            "benchmark_performed": False,
            "model_quality_claim": False,
            "generalization_established": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the offline synthetic Hugging Face CPU pipeline")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=58)
    parser.add_argument("--max-steps", type=int, default=2)
    args = parser.parse_args(argv)
    try:
        result = run_pipeline(
            args.fixture,
            args.manifest,
            seed=args.seed,
            max_steps=args.max_steps,
        )
    except (PipelineInputError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
