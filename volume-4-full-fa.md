# هنر و علم ساخت هوش — جلد چهارم

**The Art & Science of Building Intelligence | Babak & Ai**

وضعیت: ۱۵ فصل در نقشه؛ ۱ فصل از ۱۵ فصل تا این انتشار نگارش، آزموده و منتشر شده‌اند. این فایل Markdown است؛ PDF و EPUB تولید و آزموده نشده‌اند.

## فهرست فصل‌های منتشرشده

- فصل ۱ (سراسری ۴۷) — Continued Pretraining، Instruction Tuning و SFT

---

# جلد چهارم، فصل ۱ — Continued Pretraining، Instruction Tuning و SFT

**نگاشت:** فصل محلی ۱ جلد چهارم = فصل سراسری ۴۷. **تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶.** فصل ۴۳ منشأ، وضعیت حقوقیِ ثبت‌شده، کیفیت داده و نامزدهای آلودگی را ممیزی کرد؛ فصل ۴۴ حلقهٔ پیش‌آموزش، schedule، checkpoint و بازیابی را ساخت؛ فصل‌های ۴۵ و ۴۶ دقت عددی و مقیاس را سنجیدند. این فصل یک مرحلهٔ دیگر از چرخه را جدا می‌کند: «دادهٔ ادامهٔ پیش‌آموزش چه هدفی دارد؟» و «در SFT دقیقاً کدام توکن‌ها پاسخِ تحت نظارت‌اند؟» فصل بعد PEFT، Adapter، LoRA و QLoRA را بررسی می‌کند؛ فصل ۴۹ به ترجیح، پاداش و روش‌های RL می‌پردازد. این فصل آن مباحث را پیشاپیش پیاده نمی‌کند.

**پیش‌نیاز:** تفاوت train، validation و test؛ causal language modeling و ماسک علّی؛ ممیزی corpus و provenance در فصل ۴۳؛ برنامهٔ آموزش و checkpoint در فصل ۴۴. **خروجی:** بتوانید هدف CPT را از SFT تفکیک کنید، رکورد دستور/پاسخ را با گروه‌بندی مناسب بسازید، مرز prompt و target را در token-level بازرسی کنید و پروتکل اعتبارسنجی/آزمون را پیش از دیدن نتایج ثبت کنید.

![شکل ۴-۱-۱ — دو قرارداد آموزشی: در Continued Pretraining متن دامنه‌ای با هدف پیش‌بینی توکن بعدی ادامه می‌یابد؛ در SFT prompt و context به‌عنوان زمینه می‌مانند اما labels آن‌ها −۱۰۰ است و loss روی target پاسخ و پایان آن محاسبه می‌شود. هر دو مسیر به ارزیابی held-out مستقل وصل می‌شوند. نمودار مفهومی است و نتیجهٔ کیفیت یا benchmark مدل را نشان نمی‌دهد.](book-engineering/diagrams/v4-ch01-posttraining.svg)

**شکل ۴-۱-۱ —** CPT و SFT ممکن است معماری و loss علّی مشترک داشته باشند، اما هدف داده و ناحیهٔ تحت نظارتشان فرق می‌کند. مرز loss باید بعد از tokenization دیده شود؛ صرف جداکردن رشته‌های متنی، mask درست را تضمین نمی‌کند.

## ۱. مدل پیش‌آموزش‌دیده لزوماً دستیار آماده نیست

مدل زبانی پایه از روی متن، توزیع توکن بعدی را یاد می‌گیرد. این پیش‌آموزش می‌تواند توانایی‌های زبانی و دانشیِ قابل استفاده برای ادامهٔ آموزش فراهم کند، اما به‌تنهایی تضمین نمی‌کند مدل درخواست را درست تشخیص دهد، قالب پاسخ را رعایت کند، از پاسخ نامطمئن پرهیز کند یا گفت‌وگو را به شکل مطلوب ادامه دهد. «می‌تواند جمله‌ای دربارهٔ X بسازد» با «درخواست کاربر دربارهٔ X را مطابق معیار تعریف‌شده انجام می‌دهد» یکی نیست.

**پس‌آموزش (post-training)** نام چتری برای مرحله‌های پس از پیش‌آموزش است. این اصطلاح یک الگوریتم واحد نیست: ممکن است ادامهٔ پیش‌آموزش دامنه‌ای، نظارت روی نمایش‌های دستور، تنظیم ترجیح، یا روش‌های دیگری را شامل شود. فصل حاضر فقط دو خانوادهٔ نخست را پوشش می‌دهد. نام دقیق مرحله، checkpoint ورودی، داده، هدف، روش ارزیابی و هر محدودیت باید در گزارش run ثبت شود؛ «fine-tuned» به‌تنهایی شرح آزمایش نیست.

## ۲. Continued Pretraining: همان هدف، مرحلهٔ تازه

**Continued pretraining** ادامه‌دادن هدف زبانیِ پیش‌آموزش از یک checkpoint موجود روی دادهٔ انتخاب‌شده است. در **domain-adaptive pretraining (DAPT)** دادهٔ ادامه‌دار از یک دامنه می‌آید؛ در **task-adaptive pretraining (TAPT)** متن‌های نزدیک به وظیفه یا مجموعهٔ مسئله هدف‌اند. اصطلاح‌ها در ادبیات شکل‌های متفاوتی از تطبیق را پوشش می‌دهند؛ در گزارش خود، منبع و انتخاب داده را روشن‌تر از برچسب کوتاه بنویسید.

در causal LM، نمونهٔ ساده همچنان متن پیوسته‌ای است که برای پیش‌بینی توکن بعدی استفاده می‌شود. هدف به‌طور کلی شبیه پیش‌آموزش قبلی است، اما checkpoint آغاز، توزیع متن، تعداد توکن‌ها، ترتیب داده، schedule و مدت مرحله عوض شده‌اند. پس «ادامه» به معنی بی‌اثر بودن تنظیمات قبلی یا سازگار بودن خودکار checkpoint نیست؛ واژگان، tokenizer و معماری نیز باید با مدل ورودی تطبیق داشته باشند.

Gururangan و همکاران DAPT و TAPT را در آزمایش‌هایی بر RoBERTa، چهار دامنه و هشت task بررسی کردند و برای همان تنظیم‌ها سود گزارش کردند [۱]. این شاهد برای فهم ایده و طراحی یک ablation مفید است؛ تضمین نمی‌کند ادامهٔ پیش‌آموزش برای هر مدل decoder، زبان، دامنه یا مقدار داده سودمند باشد. در پروژهٔ این فصل نه corpus دامنه‌ای داریم، نه DAPT انجام می‌دهیم.

## ۳. Instruction Tuning و SFT: دستور را به نمونهٔ نظارت‌شده تبدیل کنیم

**Instruction tuning** آموزش مدل روی نمونه‌هایی است که وظیفه را به‌شکل دستور، سؤال یا درخواست طبیعی بیان می‌کنند. نمونه می‌تواند شامل دستور، زمینه، ورودی و پاسخ مطلوب باشد. در **supervised fine-tuning (SFT)**، الگوریتم با demonstrationهای هدف آموزش داده می‌شود: به مدل رشتهٔ زمینه داده می‌شود و برای پاسخ/ادامهٔ موردنظر loss محاسبه می‌شود. در عمل این اصطلاح‌ها گاهی به‌جای یکدیگر به کار می‌روند؛ «instruction tuning» معمولاً شکل و ترکیب taskها را برجسته می‌کند، درحالی‌که «SFT» شیوهٔ نظارت را توصیف می‌کند. هیچ مرز واژگانیِ جهانی و رسمی میان همهٔ کاربردهای این دو نام وجود ندارد.

کار FLAN نشان داد که نمایش‌دادن taskها به زبان دستور و آموزش روی مجموعه‌ای از taskها می‌تواند رفتار zero-shot را در برخی مدل‌ها و پروتکل‌های همان پژوهش تغییر دهد [۲]. مجموعهٔ Flan در ادامه ترکیب taskها و صورت‌بندی promptهای zero-shot، few-shot و chain-of-thought را مطالعه کرد [۳]. نتیجه‌های آن مقاله‌ها به مدل، داده، prompt و سنجه‌های همان کار وابسته‌اند؛ از آن‌ها نمی‌توان نتیجه گرفت «هر دستور بیشتر، هر مدلی را بهتر می‌کند».

در SFT، پاسخ هدف معمولاً از انسان، سیاست داده یا منبع بازبینی‌شده می‌آید. مدل پیش‌بینی ادامهٔ ارائه‌شده را یاد می‌گیرد، نه اینکه به‌طور خودکار درست‌بودن پاسخ یا رضایت کاربر را بفهمد. کیفیت demonstration، پوشش وظایف، توافق annotatorها، نحوهٔ نمایش زمینه و سیاست انتخاب پاسخ، همگی بخشی از تعریف آزمایش‌اند.

## ۴. هدف آموزش: فقط target باید loss بسازد

در prompt-completion ساده، `x` متن زمینه و `y` دنبالهٔ پاسخ هدف است. برای causal language model، نسخهٔ سادهٔ objective روی tokenهای پاسخ چنین نوشته می‌شود:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="زیان SFT برابر منفی میانگین لگاریتم احتمال هر توکن هدف پاسخ، با شرط بر توکن‌های پیشین و زمینه، است">
  <mrow><msub><mi>L</mi><mi>SFT</mi></msub><mo>=</mo><mo>−</mo><mfrac><mn>1</mn><mrow><mo>|</mo><mi>T</mi><mo>|</mo></mrow></mfrac><munder><mo>∑</mo><mrow><mi>t</mi><mo>∈</mo><mi>T</mi></mrow></munder><mi>log</mi><msub><mi>p</mi><mi>θ</mi></msub><mo>(</mo><msub><mi>y</mi><mi>t</mi></msub><mo>|</mo><msub><mi>x</mi><mrow><mo>&lt;</mo><mi>t</mi></mrow></msub><mo>)</mo></mrow>
</math>

**متن جایگزین فرمول:** زیان SFT برابر منفی میانگین لگاریتم احتمال هر توکن هدف پاسخ، با شرط بر توکن‌های پیشین و زمینه، است. `T` فقط جایگاه‌های تحت نظارت را در بر می‌گیرد.

در یک پیاده‌سازی متداول، آرایهٔ `labels` برای prompt با `-100` پر می‌شود و مقدار متناظر با پاسخ در جایگاه‌های هدف می‌ماند. در causal LM، logits هر موقعیت برای پیش‌بینی token بعدی به‌کار می‌روند؛ بنابراین باید شیفت هدفی را که مدل و trainer اعمال می‌کنند در نظر گرفت. `CrossEntropyLoss` در PyTorch 2.6 مقدار پیش‌فرض `ignore_index=-100` دارد و جایگاه‌های چنین برچسبی را از loss حذف می‌کند [۸]. این رفتار دربارهٔ آرایهٔ labels است؛ `attention_mask` جایگزین label masking نیست.

```text
input_ids = [BOS, ...prompt tokens..., ...answer tokens..., EOS]
labels    = [-100, ...-100..........., ...answer token IDs..., EOS]
```

مدل همچنان context prompt را می‌بیند و از آن برای پیش‌بینی پاسخ استفاده می‌کند؛ فقط prompt مستقیماً target loss نیست. اگر همهٔ labels برابر `-100` باشند یا مرز به‌اندازهٔ یک token جابه‌جا شده باشد، loss یا معنی آزمایش عوض می‌شود. پس چند batch واقعی را به‌شکل token ID، mask، طول و شمار target بازرسی کنید.

## ۵. قالب مکالمه و ماسک پاسخ دو قرارداد جدا هستند

در دادهٔ چتی، متن ممکن است با markerهای نقش، جداکنندهٔ پیام، کانال، یا token پایان turn سریال‌سازی شود. **Chat template** می‌گوید رشتهٔ مکالمه چگونه به دنبالهٔ tokenها تبدیل شود؛ **loss mask** می‌گوید کدام جایگاه‌ها برچسب آموزشی می‌گیرند. استفاده از template درست بدون mask درست کافی نیست؛ mask روی رشتهٔ ساده پیش از tokenization نیز ممکن است مرز را اشتباه بزند.

مستندات Transformers تأکید می‌کنند template را با همان tokenizer مدل و قرارداد پیام استفاده کنید [۹]. در دادهٔ چندنوبتی، ممکن است فقط پاسخ assistant یا بخشی از آن هدف باشد؛ پیام‌های system/user و بعضی markerهای مرزی باید بر اساس هدف آموزش تعیین شوند. گزینه‌های تولید assistant-mask و قالب داده بین نسخه‌های کتابخانه و templateها تفاوت دارند؛ نام آرگومان را از مستندات نسخهٔ pin‌شده بردارید و خروجی mask را تست کنید. در صورت استفاده از TRL، فرمت prompt-completion یا conversational و قرارداد loss همان نسخه را بررسی کنید [۱۰].

پروژهٔ این فصل عمداً chat template نمی‌سازد. Pythia-14m یک مدل پایهٔ انگلیسی است، نه مدل گفتگو؛ fixture نیز prompt-completion ساده است. این انتخاب جلوی ادعای نادرست دربارهٔ قالب چت یک مدل را می‌گیرد و امکان می‌دهد مرز دو رشته و label mask را آشکار ببینیم.

## ۶. Padding، طول و شمار واقعی token هدف

Batchهای هم‌طول برای محاسبهٔ دسته‌ای padding می‌گیرند. ورودی padding می‌تواند `pad_token_id` داشته باشد و `attention_mask` موقعیت‌های padding را برای attention مشخص کند؛ برچسب padding نیز باید از loss حذف شود. در پروژه، هر دو مورد برچسب prompt و padding برابر `-100` می‌گیرند. تعداد targetها را از labels معتبر پس از شیفت causal بشمارید؛ تعداد کل `input_ids` معیار اندازهٔ supervision نیست.

وقتی طول پاسخ‌ها متفاوت است، میانگین‌گیری را دقیق تعریف کنید. اگر trainer loss را بر تعداد targetهای معتبر هر batch میانگین می‌گیرد، برای تجمیع چند batch باید آن را با تعداد targetها وزن‌دهی کنید؛ میانگین سادهٔ lossهای batchهای کوچک و بزرگ می‌تواند به هر batch وزن برابر بدهد، نه به هر token. جزئیات reduction و accumulation به پیاده‌سازی وابسته است؛ برای run واقعی رفتار loss را با یک مثال کوچک و reference دستی تطبیق دهید.

**Truncation** نیز باید هدف‌مند باشد. بریدن انتهای پاسخ می‌تواند target را ناقص کند؛ بریدن ابتدای زمینه ممکن است دستور یا قید اصلی را حذف کند. سیاست‌ها می‌توانند طول حداکثری، اولویت حفظ دستور، انتخاب پنجره، یا کنارگذاشتن نمونهٔ بلند باشند. نمونهٔ پروژه prompt را از سمت چپ کوتاه می‌کند تا پاسخ کامل بماند؛ این انتخاب فقط برای fixture آموزشی است و قانون عمومی برای گفتگو یا اسناد بلند نیست. مرز سند و token پایان را با template و هدف همان مدل کنترل کنید.

## ۷. رکورد آموزشی باید هدف را قابل‌ردیابی کند

یک ساختار ساده می‌تواند `id`، `source_id`، `group_id`، `prompt` و `completion` داشته باشد. در corpus واقعی معمولاً فیلدهایی برای نسخه، منشأ، روش تولید، بازبینی، زبان، دامنه، برچسب، مجوز و دلیل نگه‌داری/کنارگذاری نیز نیاز است. فصل ۴۳ برای provenance، حقوق و audit طراحی شده؛ این فصل آن سامانه را دوباره نمی‌سازد. وجود فیلد در JSONL هم صحت یا مجازبودن مقدار را اثبات نمی‌کند.

برای هر نمونه بپرسید: آیا دستور واضح است؟ زمینهٔ لازم دارد؟ پاسخ با معیار تعریف‌شده منطبق است؟ پاسخ کوتاه یا بلندتر از مطلوب است؟ آیا چند پاسخ جایگزین پذیرفتنی‌اند؟ چه کسی قضاوت کرده و اختلاف چگونه ثبت شده؟ آیا prompt الگوی نشت target یا پاسخ ساختگی دارد؟ آیا داده نمونه‌های رد، عدم‌قطعیت یا درخواست clarification را پوشش می‌دهد؟ یک پاسخ نمونه فقط یکی از پاسخ‌های پذیرفتنی را نشان می‌دهد؛ آن را تعریف حقیقت مطلق نکنید.

Data card باید جمعیت و هدف مجموعه، نحوهٔ ساخت/انتخاب، توزیع source/task/طول، splitها، ناشناخته‌ها و کاربردهای خارج از دامنه را توضیح دهد [۱۲]. دادهٔ آموزشی، دادهٔ validation و test باید از نظر تصمیم‌های انتخاب و نسخه جدا بمانند. اگر نمونه‌های مرتبط از یک سند، template، کاربر یا خانوادهٔ تولید آمده‌اند، رابطه را با `group_id` یا شناسهٔ مناسب نگه دارید تا split میان آن‌ها نشت نکند.

## ۸. آمیختن taskها: تعداد نمونه تنها وزن نیست

مجموعهٔ instruction می‌تواند taskها، زبان‌ها، طول پاسخ‌ها، سبک prompt، منبع و دشواری متفاوت داشته باشد. اگر یک نوع task صد برابر نمونه دارد، شاید سهم token آن از batch و گرادیان هم بیشتر شود؛ ولی کم‌شمردن آن به‌خاطر «توازن تعداد ردیف» هم ممکن است الگوی مهمی را کم‌وزن کند. نسبت رکورد، نسبت token، احتمال نمونه‌گیری، وزن loss و ترتیب curriculum تصمیم‌های متفاوتی‌اند.

طرح آزمایش را بر اساس خروجی‌های مورد انتظار و خطاهای مهم بنویسید. سهم taskها را جدا log کنید؛ منبع، group و طول را ثبت کنید؛ و تغییرات mixture را روی validationِ تعریف‌شده بسنجید. اگر چند نسخه از یک task یا ترجمهٔ یک prompt در داده است، آن‌ها را مستقل فرض نکنید. تغییر هم‌زمان mixture، مدل، schedule و prompt ارزیابی تفسیر علت را دشوار می‌کند؛ مقایسه را تا حد امکان کنترل کنید.

Flan Collection اثر طراحی taskها و prompt-formatها را در آزمایش‌های نویسندگان گزارش می‌کند [۳]. این نتایج به ترکیب و ارزیابی همان مقاله تعلق دارد؛ وزن‌های آن را بدون توجه به هدف، زبان، منبع یا مقیاس به مجموعه‌ای دیگر منتقل نکنید. «توازن بهتر» باید با تعریف معیار و جمعیت موردنظر سنجیده شود، نه با فرض یک توزیع ایده‌آل ثابت.

## ۹. «کمتر ولی بهتر» قانون عددی جهان‌شمول نیست

LIMA روی LLaMA با ۶۵ میلیارد پارامتر و ۱٬۰۰۰ نمونهٔ curated شده، در همان setup نتیجه‌هایی دربارهٔ کیفیت SFT و اهمیت مدل پایه/داده گزارش کرد [۵]. AlpaGasus زیرمجموعه‌ای حدود ۹٬۰۰۰تایی از ۵۲٬۰۰۰ نمونهٔ Alpaca را با روش امتیازدهی خود انتخاب کرد و آزمایش‌های مربوط به مدل‌ها و سنجه‌های خود را گزارش داد [۶]. این‌ها پرسش خوبی برای طراحی ablation می‌سازند: کدام نمونه‌ها مفیدند؟ چه هزینه‌ای دارد؟ معیار انتخاب چقدر با هدف منطبق است؟ اما هیچ‌کدام ثابت نمی‌کنند «۱٬۰۰۰ نمونه برای هر مدل کافی است» یا «حذف داده همیشه کیفیت را بالا می‌برد».

دادهٔ کم ممکن است پوشش را کم کند؛ دادهٔ بیشتر می‌تواند تنوع را بالا ببرد یا نویز و پاسخ‌های ناسازگار اضافه کند. امتیازدهی خودکار یا LLM-as-a-judge نیز نیازمند تعریف معیار، calibration، بررسی خطا و تحلیل اختلاف است. گزارش نتیجه باید مدل پایه، نسخه/حجم داده، انتخاب‌ها، تعداد token، تعداد update، پروتکل validation/test و محدودیت ارزیاب را ثبت کند؛ یک نسبت نمونه به‌تنهایی کیفیت را پیش‌بینی نمی‌کند.

## ۱۰. CPT و SFT را می‌توان مرحله‌بندی کرد، اما نباید در گزارش مخلوط کرد

ممکن است run ابتدا روی متن دامنه‌ای ادامهٔ پیش‌آموزش بگیرد و سپس روی demonstrationهای دستور SFT شود؛ این دو مرحله هدف داده‌ای متفاوت دارند. همچنین می‌توان در یک برنامهٔ چندبخشی متن‌های مختلف را با weighting یا sampling ترکیب کرد. هر انتخاب در checkpoint، نسخهٔ tokenizer، مقدار و ترتیب داده، schedule و معیارها بازتاب دارد. «یک مدل را fine-tune کردیم» نمی‌گوید کدام مرحله و کدام هدف اجرا شده است.

تغییر توزیع داده یا هدف می‌تواند رفتارها را تغییر دهد؛ حفظ، فراموشی یا افت در taskهای پیشین باید با ارزیابی مناسب سنجیده شود. این فصل claim نمی‌کند CPT یا SFT الزاماً موجب catastrophic forgetting می‌شوند یا آن را برطرف می‌کنند. اگر ادامهٔ آموزش، task تازه یا data mixture را می‌آزمایید، خط پایه و چند task نماینده را پیش از run تعریف کنید و نتیجه را در همان دامنه گزارش دهید.

SFT نیز به‌تنهایی ترجیح یا پاداش انسانی را مدل نمی‌کند. در مقالهٔ InstructGPT، SFT روی demonstration مرحلهٔ جداگانه‌ای از preference comparisons، reward modeling و PPO بود [۴]. فصل ۴۹ همان تفاوت‌ها را دقیق‌تر بررسی می‌کند؛ اینجا از مخلوط‌کردن نام «SFT» با «RLHF» پرهیز می‌کنیم.

## ۱۱. ارزیابی را قبل از انتخاب checkpoint تعریف کنیم

پروتکل ساده شامل سه split است: train برای گرادیان؛ validation برای مشاهده/انتخاب‌های مجاز؛ test برای گزارش نهایی پس از تثبیت روش. اگر validation چندباره برای انتخاب mixture یا checkpoint استفاده شد، آن تصمیم را ثبت کنید. Test را پس از هر update یا هر انتخاب threshold نخوانید؛ در غیر این صورت دیگر شاهد مستقل نهایی نیست. در پروژهٔ فصل، NLL اعتبارسنجی پیش و پس از آموزش مقایسه می‌شود و test عمومی فقط یک بار پس از آموزش محاسبه می‌شود.

Metric را به مسئله وصل کنید. NLL یا cross-entropy برای توزیع tokenها است؛ exact match برای خروجی‌های دقیق؛ معیارهای طبقه‌بندی برای برچسب‌های تعریف‌شده؛ و rubric انسانی برای ویژگی‌هایی که خودکار سنجش نمی‌شوند. هیچ‌کدام به‌تنهایی «مفید»، «ایمن» یا «مطابق دستور» بودن کلی مدل را ثابت نمی‌کنند. اگر از ارزیاب انسانی/مدلی استفاده می‌کنید، rubric، نمونه‌گیری، توافق، ترجیح position، دسترسی به مرجع و موارد مبهم را بنویسید.

ممیزی فصل ۴۳ هشدار می‌دهد که match سطحی نه اثبات مواجههٔ مدل است و نه نبودن match اثبات پاک‌بودن داده. پژوهش Sainz و همکاران نشان می‌دهد سنجش آلودگی باید برای benchmark مشخص انجام شود [۷]. منابع، نسخهٔ benchmark، تاریخ cutoff، groupها و روش بررسی را ثبت کنید؛ ارزیابی عمومی را محرمانه فرض نکنید.

## ۱۲. حقوق داده، privacy و مجوز مدل سه پرسش جدا هستند

دادهٔ عمومی یا نمونهٔ قابل‌دسترسی خودبه‌خود اجازهٔ آموزش، انتشار یا استفادهٔ محصولی نمی‌دهد. پیش از مصرف corpus واقعی، provenance، مجوز upstream، شرایط کاربرد، privacy و هر الزام انتساب را طبق فرایند فصل ۴۳ و نظر مسئول مناسب بررسی کنید. ابزارهای این فصل هیچ مجوزی صادر نمی‌کنند و تضمین حقوقی یا privacy نمی‌دهند.

مجوز metadata یک checkpoint نیز با مجوز مواد آموزشی آن یکی نیست. کارت مدل `EleutherAI/pythia-14m` در بازبینی ۶ نوامبر ۲۰۲۶ metadata مجوز را `apache-2.0` نشان می‌داد؛ کارت همین مدل را English و برای پژوهش معرفی می‌کرد، نه deployment یا زبان‌های دیگر [۱۱]. کارت همچنین به تغییر مقصد مدل میزبانی‌شده از نسخهٔ `deduped` به Pile استاندارد در فوریهٔ ۲۰۲۶ اشاره می‌کند. پروژه revision را به SHA ثابت pin می‌کند تا شناسهٔ متحرک `main` در بازتولیدپذیری دخیل نباشد [۱۳].

این metadata نه جواز همهٔ داده‌های Pile را ثابت می‌کند، نه حقوق دادهٔ fixtureهای دیگر را تعیین می‌کند، نه کیفیت فارسی یا تناسب محصول را نشان می‌دهد. در این پروژه فقط fixtureهای ساختگی انگلیسی به کار می‌روند؛ فایل دادهٔ بیرونی یا benchmark محرمانه‌ای دریافت یا ارسال نمی‌شود. مدل‌کارت و مجوزش را برای هر کاربرد و نسخه دوباره بررسی کنید.

## ۱۳. پروژهٔ قابل‌بازتولید: از audit تا run اختیاری

پروژهٔ [قرارداد داده و SFT فصل ۴۷](book-engineering/projects/47-instruction-tuning/README.md) سه بخش دارد: fixture JSONL، split پایدار بر اساس `group_id`، و کد tokenization/collation که prompt و padding را از loss کنار می‌گذارد. تست‌ها با tokenizer ساختگی اجرا می‌شوند؛ بنابراین هیچ وزن، tokenization Pythia یا کیفیت مدل را ادعا نمی‌کنند. حالت `audit` نیز فقط ساختار و شمارها را بررسی می‌کند.

برای آموزش واقعیِ نمایشی، وابستگی‌های optional دقیق pin شده‌اند؛ `--allow-download` باید آگاهانه داده شود و کد revision مدل را ثابت می‌کند. CPU و یک fixture عمومی کوچک انتخاب شده‌اند تا مسیر قابل اجرا بماند. در گزارش run، نسخهٔ Python/PyTorch/Transformers، hash داده، config، شمار update، NLL validation پیش/پس، test نهایی و محدودیت‌ها ثبت می‌شوند. به علت محدودیت کارت، این مثال انگلیسی است؛ از آن هیچ ادعای کیفیت فارسی، GPU/NCCL، سرعت/benchmark سخت‌افزار یا deployment نتیجه نگیرید.

خروجی‌های اجرای پروژه در مسیر `/tmp` نگه داشته می‌شوند و وزن‌ها به Git اضافه نمی‌شوند. CI آزمون‌های unit و audit آفلاین را اجرا می‌کند، نه دانلود مدل. اگر آزمایش اختیاری اجرا نشود یا دانلود در دسترس نباشد، گزارش باید همین را صریح بگوید؛ صرف وجود دستور اجرا نتیجهٔ آموزش محسوب نمی‌شود.

## ۱۴. خطاهای رایج در داده و labelها

- اگر برچسب‌های prompt را به‌اشتباه فعال کنید، مدل بخشی از ورودی را نیز بازتولید می‌کند؛ ممکن است هدف task عوض شود، حتی اگر loss عددی باشد.
- اگر همهٔ پاسخ‌ها به یک separator یا template وابسته‌اند و آن در inference وجود ندارد، ارزیابی آموزش نمایندهٔ مصرف واقعی نیست.
- اگر پاسخ طولانی در انتها truncate شود، EOS یا بخش تعیین‌کنندهٔ جواب از target حذف می‌شود؛ این خطا را با تغییر طول و شمار tokenها پیدا کنید.
- اگر padding labels نادیده گرفته نشود، مدل ممکن است token padding را هدف بگیرد؛ `attention_mask` به‌تنهایی این مشکل را رفع نمی‌کند.
- اگر نمونه‌های یک group یا near-duplicate در train و test پخش شوند، score می‌تواند بیش از حد خوش‌بینانه شود؛ از group-aware split و audit فصل ۴۳ بهره ببرید.
- اگر validation را بارها برای انتخاب prompt و mixture مصرف کنید، دیگر آن را test مستقل ننامید؛ روند انتخاب را ثبت کنید.
- اگر metadata مدل را با حقوق corpus یا تضمین محصول یکی بگیرید، از مرز شواهد فراتر رفته‌اید؛ مدل‌کارت، داده‌کارت و بررسی کاربردی را جدا نگه دارید.

## ۱۵. چک‌لیست پیش از اجرای SFT

۱. هدف، کاربرد موردنظر، خروجی پذیرفتنی و baseline را تعریف کرده‌ام. ۲. checkpoint، tokenizer، revision و وابستگی‌ها pin شده‌اند. ۳. provenance و کاربرد داده از فرایند فصل ۴۳ عبور کرده‌اند؛ fixture با دادهٔ واقعی اشتباه نمی‌شود. ۴. رکوردها ID و `group_id` پایدار دارند و train/validation/test پیش از آموزش جدا شده‌اند. ۵. serialization، chat template، پایان پیام و پاسخ هدف تعریف شده‌اند. ۶. چند batch واقعی را پس از tokenization بررسی کرده‌ام: ورودی، attention mask، labels، `-100`، طول target و شمار supervised tokens. ۷. سیاست truncation، padding، loss reduction و gradient accumulation معلوم است. ۸. task mixture و معیارهای validation پیش از اجرا ثبت شده‌اند. ۹. آلودگی benchmark و محدودیت‌های data/model card بررسی شده‌اند. ۱۰. test فقط پس از تثبیت تصمیم‌ها برای گزارش نهایی استفاده می‌شود. ۱۱. run، وابستگی، hash و محدودیت‌ها ثبت می‌شوند؛ outputهای مصنوعی یا smoke-test را benchmark معرفی نمی‌کنم.

## ۱۶. تمرین و پاسخ‌نامه

**تمرین ۱.** برای دو هدف «ادامهٔ پیش‌آموزش روی متن پزشکی» و «پاسخ‌دادن به پرسش با demonstration» نوع داده، هدف token-level و خطر ارزیابی متفاوت را بنویسید. چرا عنوان «fine-tuning» برای بازتولید run کافی نیست؟

**تمرین ۲.** ورودی `BOS + prompt(4 tokens) + answer(3 tokens) + EOS` را در آرایهٔ `labels` مشخص کنید. اگر labelهای prompt به‌جای `-100` همان token ID بمانند، چه چیزی تغییر می‌کند؟

**تمرین ۳.** دوازده رکورد از چهار سند مادر آمده‌اند؛ هر سند سه قطعه دارد. چرا split تصادفی هر رکورد ممکن است نشت بسازد؟ چه کلیدی را برای split نگه می‌دارید و چه چیزی را جداگانه در validation/test می‌سنجید؟

**تمرین ۴.** یک مقاله روی ۱٬۰۰۰ نمونهٔ curated نتیجهٔ خوبی گزارش می‌کند. دو دلیل بیاورید که چرا این عدد، قانون حجم داده برای مدل شما نیست؛ یک ablation قابل‌دفاع پیشنهاد دهید.

**تمرین ۵.** تفاوت مجوز metadata مدل و مجوز corpus آموزشی چیست؟ در پروژهٔ Pythia چه چیزی pin شده و چه چیزی از کارت مدل استنتاج نمی‌شود؟

**پاسخ‌نامهٔ مستقل:** [پاسخ‌نامهٔ تشریحی فصل ۴۷](book-engineering/answers/47-posttraining-fa.md). **پروژه:** [README و دستورهای اجرا](book-engineering/projects/47-instruction-tuning/README.md)؛ [گزارش ممیزی و نتیجه](book-engineering/chapters/47-audit-report-fa.md).

## ۱۷. جمع‌بندی و مسیر بعد

CPT دادهٔ متنی را با هدف پیش‌بینی token بعدی روی مرحلهٔ تازه ادامه می‌دهد؛ SFT demonstrationهای مطلوب را به targetهای supervised تبدیل می‌کند. اگر prompt قرار است فقط context باشد، label mask باید واقعاً آن را از loss کنار بگذارد. Chat template، attention mask، padding mask و assistant-target mask مفهوم‌های مرتبط اما قابل‌جایگزین نیستند. Split گروهی، validation مستقل، testِ دیرهنگام، منشأ داده و محدودیت‌های مدل هم بخشی از پروتکل‌اند، نه کارهای جانبی.

فصل ۴۸ بعدی می‌پرسد آیا باید همهٔ وزن‌ها را به‌روزرسانی کرد یا با PEFT/Adapter/LoRA/QLoRA بخشی از هزینه را عوض کرد؛ مقایسهٔ کیفیت و حافظه را باید روی task، مدل و سخت‌افزار مشخص انجام داد. فصل ۴۹ سپس preference data و روش‌های پاداش/RL را از SFT جدا می‌کند. هیچ‌یک از این فصل‌های آینده با نتیجهٔ fixture این فصل از پیش حل نمی‌شوند.

## منابع و تاریخ بازبینی

منابع زیر تا **۶ نوامبر ۲۰۲۶** بازبینی شده‌اند. مقاله‌ها نتیجه‌های همان setup نویسندگان را پشتیبانی می‌کنند؛ صفحات مستندات زنده نسخه‌محورند و باید هنگام اجرای کد دوباره کنترل شوند.

1. Gururangan, S. و همکاران، “Don’t Stop Pretraining: Adapt Language Models to Domains and Tasks”، ACL 2020، [متن مقاله](https://aclanthology.org/2020.acl-main.740/). مطالعهٔ DAPT/TAPT بر setup گزارش‌شدهٔ مقاله.
2. Wei, J. و همکاران، “Finetuned Language Models Are Zero-Shot Learners”، 2021، [arXiv:2109.01652](https://arxiv.org/abs/2109.01652). نتیجه‌های FLAN به مدل و پروتکل مقاله وابسته‌اند.
3. Longpre, S. و همکاران، “The Flan Collection: Designing Data and Methods for Effective Instruction Tuning”، 2023، [arXiv:2301.13688](https://arxiv.org/abs/2301.13688). طراحی mixture و صورت‌بندی taskها در آزمایش‌های نویسندگان.
4. Ouyang, L. و همکاران، “Training language models to follow instructions with human feedback”، 2022، [arXiv:2203.02155](https://arxiv.org/abs/2203.02155). تفکیک مراحل SFT، reward model و PPO در مطالعهٔ InstructGPT.
5. Zhou, C. و همکاران، “LIMA: Less Is More for Alignment”، 2023، [arXiv:2305.11206](https://arxiv.org/abs/2305.11206). setup مدل LLaMA 65B و 1,000 نمونهٔ curated.
6. Chen, L. و همکاران، “AlpaGasus: Training A Better Alpaca with Fewer Data”، 2023، [arXiv:2307.08701](https://arxiv.org/abs/2307.08701). انتخاب 9k از 52k در آزمایش مقاله؛ نه قاعدهٔ کمیت.
7. Sainz, O. و همکاران، “NLP Evaluation in trouble: On the Need to Measure LLM Data Contamination for each Benchmark”، Findings of EMNLP 2023، [ACL Anthology](https://aclanthology.org/2023.findings-emnlp.722/).
8. PyTorch 2.6، `torch.nn.CrossEntropyLoss`، [مستندات نسخه‌دار](https://docs.pytorch.org/docs/2.6/generated/torch.nn.CrossEntropyLoss.html). مستندات مرجع `ignore_index`.
9. Hugging Face Transformers، “Chat templates”، مستندات جاری؛ صفحه هنگام بازبینی نسخهٔ main را 5.22.1 نشان می‌داد، [راهنما](https://huggingface.co/docs/transformers/en/chat_templating). پروژهٔ این فصل از template چت استفاده نمی‌کند.
10. Hugging Face TRL، “SFT Trainer”، مستندات جاری؛ صفحه هنگام بازبینی v1.17.1 را نشان می‌داد، [راهنما](https://huggingface.co/docs/trl/en/sft_trainer). قرارداد dataset و masking باید با نسخهٔ مورد استفاده تطبیق یابد.
11. EleutherAI، [کارت مدل Pythia-14m](https://huggingface.co/EleutherAI/pythia-14m). زبان، کاربرد پژوهشی، محدودیت زبان و metadata مجوز؛ بازبینی ۶ نوامبر ۲۰۲۶.
12. Hugging Face Datasets، “Create a dataset card”، [مستندات](https://huggingface.co/docs/datasets/dataset_card). هدف کارت داده و ثبت محدودیت‌ها؛ تاریخ انتشار صفحه نامشخص.
13. Hugging Face Hub، [API مدل Pythia-14m](https://huggingface.co/api/models/EleutherAI/pythia-14m). SHA مشاهده‌شده در ۶ نوامبر ۲۰۲۶: `cf967c0a9a04383db6f7b1108d86b2962634b4ac`.

## پیوست اجرایی: فایل پروژهٔ آزموده‌شده

کد زیر باید با بایت‌های `book-engineering/projects/47-instruction-tuning/sft_experiment.py` یکسان بماند. CI و سازندهٔ جلد چهارم تطبیق را بررسی می‌کنند. حالت آفلاین فقط audit می‌کند؛ مسیر آموزش اختیاری است و نیازمند مدل/وابستگی‌های pin‌شده است.

```python
"""Small, offline-first SFT data-contract and CPU fine-tuning demonstration.

The default audit mode never imports Transformers, loads a model, or accesses the
network. The optional training mode is a research smoke test on synthetic English
data and a revision-pinned Pythia checkpoint; it is not a quality benchmark.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import sys
from typing import Any, Mapping, Sequence

MODEL_ID = "EleutherAI/pythia-14m"
MODEL_REVISION = "cf967c0a9a04383db6f7b1108d86b2962634b4ac"
MODEL_CARD_LICENSE = "apache-2.0"
MODEL_CARD_URL = "https://huggingface.co/EleutherAI/pythia-14m"
MODEL_CARD_REVIEWED = "2026-11-06"
REQUIRED_FIELDS = ("id", "source_id", "group_id", "prompt", "completion")
SPLIT_NAMES = ("train", "validation", "test")


def _require_positive_int(name: str, value: object, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def _require_fraction(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number in (0, 1)")
    result = float(value)
    if not math.isfinite(result) or not 0.0 < result < 1.0:
        raise ValueError(f"{name} must be a finite number in (0, 1)")
    return result


def load_jsonl(path: str | Path) -> list[dict[str, str]]:
    """Load the minimal prompt/completion schema; never infer rights or quality."""
    path = Path(path)
    rows: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    try:
        stream = path.open("r", encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot open dataset {path}: {exc}") from exc
    with stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_number}: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"line {line_number}: each row must be a JSON object")
            row = dict(value)
            for field in REQUIRED_FIELDS:
                item = row.get(field)
                if not isinstance(item, str) or not item.strip():
                    raise ValueError(f"line {line_number}: {field!r} must be a non-empty string")
                row[field] = item.strip()
            if row["id"] in seen_ids:
                raise ValueError(f"line {line_number}: duplicate id {row['id']!r}")
            seen_ids.add(row["id"])
            rows.append(row)
    if not rows:
        raise ValueError(f"dataset {path} contains no records")
    return rows


def split_by_group(
    records: Sequence[Mapping[str, str]],
    *,
    seed: int = 47,
    train_fraction: float = 0.8,
    validation_fraction: float = 0.1,
) -> dict[str, list[Mapping[str, str]]]:
    """Deterministically split group IDs so related records cannot cross splits."""
    _require_positive_int("seed", seed, minimum=0)
    train_fraction = _require_fraction("train_fraction", train_fraction)
    validation_fraction = _require_fraction("validation_fraction", validation_fraction)
    if train_fraction + validation_fraction >= 1.0:
        raise ValueError("train_fraction + validation_fraction must be less than 1")
    if not records:
        raise ValueError("records must not be empty")
    group_ids = sorted({str(record["group_id"]) for record in records})
    if len(group_ids) < 3:
        raise ValueError("at least three independent group_id values are required for train/validation/test")

    ordered_groups = sorted(
        group_ids,
        key=lambda group: (
            hashlib.sha256(f"{seed}\0{group}".encode("utf-8")).hexdigest(),
            group,
        ),
    )
    train_count = min(max(1, round(len(ordered_groups) * train_fraction)), len(ordered_groups) - 2)
    validation_count = min(
        max(1, round(len(ordered_groups) * validation_fraction)),
        len(ordered_groups) - train_count - 1,
    )
    train_groups = set(ordered_groups[:train_count])
    validation_groups = set(ordered_groups[train_count:train_count + validation_count])
    test_groups = set(ordered_groups[train_count + validation_count:])
    group_to_split = {
        **{group: "train" for group in train_groups},
        **{group: "validation" for group in validation_groups},
        **{group: "test" for group in test_groups},
    }
    result: dict[str, list[Mapping[str, str]]] = {name: [] for name in SPLIT_NAMES}
    for record in records:
        result[group_to_split[str(record["group_id"])]].append(record)
    if any(not result[name] for name in SPLIT_NAMES):
        raise ValueError("each split must contain at least one record")
    return result


def encode_prompt_completion(
    prompt: str,
    completion: str,
    tokenizer: Any,
    *,
    max_length: int = 128,
) -> dict[str, list[int]]:
    """Tokenize separately and mask prompt labels; never silently cut a target."""
    max_length = _require_positive_int("max_length", max_length, minimum=2)
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt must be a non-empty string")
    if not isinstance(completion, str) or not completion.strip():
        raise ValueError("completion must be a non-empty string")
    eos_token_id = getattr(tokenizer, "eos_token_id", None)
    if eos_token_id is None:
        raise ValueError("tokenizer must define eos_token_id")

    prompt_ids = list(tokenizer.encode(prompt, add_special_tokens=False))
    completion_ids = list(tokenizer.encode(completion, add_special_tokens=False))
    bos_token_id = getattr(tokenizer, "bos_token_id", None)
    if bos_token_id is not None:
        prompt_ids.insert(0, int(bos_token_id))
    if not prompt_ids:
        raise ValueError("prompt produced no tokens")
    if not completion_ids:
        raise ValueError("completion produced no tokens")
    if completion_ids[-1] != int(eos_token_id):
        completion_ids.append(int(eos_token_id))

    prompt_budget = max_length - len(completion_ids)
    if prompt_budget < 1:
        raise ValueError("completion plus EOS leaves no room for a prompt token; increase max_length")
    if len(prompt_ids) > prompt_budget:
        # Keep the most recent context tokens; the completion is never truncated.
        prompt_ids = prompt_ids[-prompt_budget:]
    input_ids = [int(token) for token in prompt_ids + completion_ids]
    labels = [-100] * len(prompt_ids) + [int(token) for token in completion_ids]
    if len(input_ids) > max_length or not any(label != -100 for label in labels[1:]):
        raise ValueError("encoded example has no valid shifted completion targets")
    return {"input_ids": input_ids, "labels": labels}


def collate_features(features: Sequence[Mapping[str, Sequence[int]]], *, pad_token_id: int) -> dict[str, list[list[int]]]:
    """Right-pad IDs/masks; pad labels with -100 so padding adds no loss."""
    _require_positive_int("batch size", len(features))
    if isinstance(pad_token_id, bool) or not isinstance(pad_token_id, int):
        raise ValueError("pad_token_id must be an integer")
    max_length = max(len(feature["input_ids"]) for feature in features)
    batch_ids: list[list[int]] = []
    batch_masks: list[list[int]] = []
    batch_labels: list[list[int]] = []
    for feature in features:
        input_ids = [int(value) for value in feature["input_ids"]]
        labels = [int(value) for value in feature["labels"]]
        if not input_ids or len(input_ids) != len(labels):
            raise ValueError("each feature must have equally sized, non-empty input_ids and labels")
        padding = max_length - len(input_ids)
        batch_ids.append(input_ids + [pad_token_id] * padding)
        batch_masks.append([1] * len(input_ids) + [0] * padding)
        batch_labels.append(labels + [-100] * padding)
    return {"input_ids": batch_ids, "attention_mask": batch_masks, "labels": batch_labels}


def _dataset_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _split_counts(splits: Mapping[str, Sequence[Mapping[str, str]]]) -> dict[str, dict[str, int]]:
    return {
        name: {
            "records": len(splits[name]),
            "groups": len({str(record["group_id"]) for record in splits[name]}),
        }
        for name in SPLIT_NAMES
    }


def audit_dataset(dataset_path: str | Path, output_dir: str | Path, *, seed: int = 47) -> dict[str, Any]:
    """Validate JSONL and save counts only. Does not tokenize or train."""
    dataset_path = Path(dataset_path)
    rows = load_jsonl(dataset_path)
    splits = split_by_group(rows, seed=seed)
    report: dict[str, Any] = {
        "schema_version": 1,
        "status": "validated_only",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data": {
            "file_name": dataset_path.name,
            "sha256": _dataset_digest(dataset_path),
            "records": len(rows),
            "groups": len({row["group_id"] for row in rows}),
            "split_counts": _split_counts(splits),
            "contains_only_synthetic_demo_data": True,
        },
        "training_performed": False,
        "model_downloaded_or_loaded": False,
        "test_evaluations": 0,
        "interpretation": "Counts validate this public synthetic fixture only; they are not a model or data-quality result.",
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "run.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _encode_split(
    records: Sequence[Mapping[str, str]], tokenizer: Any, *, max_length: int
) -> list[dict[str, list[int]]]:
    return [
        encode_prompt_completion(record["prompt"], record["completion"], tokenizer, max_length=max_length)
        for record in records
    ]


def _torch_batch(features: Sequence[Mapping[str, Sequence[int]]], *, pad_token_id: int, torch: Any) -> dict[str, Any]:
    padded = collate_features(features, pad_token_id=pad_token_id)
    return {
        name: torch.tensor(values, dtype=torch.long, device="cpu")
        for name, values in padded.items()
    }


def _evaluate_nll(model: Any, features: Sequence[Mapping[str, Sequence[int]]], *, batch_size: int, pad_token_id: int, torch: Any) -> float:
    model.eval()
    weighted_loss = 0.0
    target_count = 0
    with torch.no_grad():
        for start in range(0, len(features), batch_size):
            batch = _torch_batch(features[start:start + batch_size], pad_token_id=pad_token_id, torch=torch)
            valid_targets = int((batch["labels"][:, 1:] != -100).sum().item())
            if valid_targets < 1:
                raise ValueError("evaluation batch has no shifted completion targets")
            output = model(**batch)
            loss = float(output.loss.detach().cpu().item())
            if not math.isfinite(loss):
                raise ValueError("non-finite evaluation loss")
            weighted_loss += loss * valid_targets
            target_count += valid_targets
    if target_count == 0:
        raise ValueError("evaluation split is empty")
    return weighted_loss / target_count


def train_pythia_demo(
    dataset_path: str | Path,
    output_dir: str | Path,
    *,
    seed: int = 47,
    epochs: int = 1,
    batch_size: int = 2,
    max_length: int = 128,
    learning_rate: float = 5e-5,
    cpu_threads: int = 1,
    allow_download: bool = False,
) -> dict[str, Any]:
    """Full-parameter CPU SFT smoke run; test is evaluated once, after training."""
    _require_positive_int("seed", seed, minimum=0)
    epochs = _require_positive_int("epochs", epochs)
    batch_size = _require_positive_int("batch_size", batch_size)
    max_length = _require_positive_int("max_length", max_length, minimum=2)
    cpu_threads = _require_positive_int("cpu_threads", cpu_threads)
    if isinstance(learning_rate, bool) or not isinstance(learning_rate, (int, float)) or not math.isfinite(float(learning_rate)) or learning_rate <= 0:
        raise ValueError("learning_rate must be finite and positive")

    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    try:
        import torch
        import transformers
        import huggingface_hub
        import tokenizers
        import safetensors
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError(
            "training requires the pinned model-demo dependencies; install requirements.txt "
            "and this folder's requirements-model-demo.txt"
        ) from exc

    dataset_path = Path(dataset_path)
    rows = load_jsonl(dataset_path)
    splits = split_by_group(rows, seed=seed)
    torch.manual_seed(seed)
    torch.set_num_threads(cpu_threads)
    local_files_only = not allow_download
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        local_files_only=local_files_only,
        trust_remote_code=False,
        use_fast=True,
    )
    if tokenizer.eos_token_id is None:
        raise RuntimeError("the pinned tokenizer has no EOS token")
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        local_files_only=local_files_only,
        trust_remote_code=False,
        use_safetensors=True,
        dtype=torch.float32,
    )
    model.config.pad_token_id = tokenizer.pad_token_id
    model.to("cpu")

    encoded = {name: _encode_split(splits[name], tokenizer, max_length=max_length) for name in SPLIT_NAMES}
    validation_before = _evaluate_nll(
        model, encoded["validation"], batch_size=batch_size,
        pad_token_id=int(tokenizer.pad_token_id), torch=torch,
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(learning_rate), weight_decay=0.0)
    update_count = 0
    for epoch in range(epochs):
        order = list(range(len(encoded["train"])))
        random.Random(seed + epoch).shuffle(order)
        model.train()
        for start in range(0, len(order), batch_size):
            selected = [encoded["train"][index] for index in order[start:start + batch_size]]
            batch = _torch_batch(selected, pad_token_id=int(tokenizer.pad_token_id), torch=torch)
            optimizer.zero_grad(set_to_none=True)
            output = model(**batch)
            loss = output.loss
            if not bool(torch.isfinite(loss).item()):
                raise ValueError(f"non-finite training loss at update {update_count + 1}")
            loss.backward()
            optimizer.step()
            update_count += 1

    validation_after = _evaluate_nll(
        model, encoded["validation"], batch_size=batch_size,
        pad_token_id=int(tokenizer.pad_token_id), torch=torch,
    )
    # The held-out public fixture split is inspected once, after all training choices.
    test_after = _evaluate_nll(
        model, encoded["test"], batch_size=batch_size,
        pad_token_id=int(tokenizer.pad_token_id), torch=torch,
    )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_dir = output_dir / "model"
    tokenizer_dir = output_dir / "tokenizer"
    model.save_pretrained(model_dir, safe_serialization=True)
    tokenizer.save_pretrained(tokenizer_dir)

    split_counts = _split_counts(splits)
    report: dict[str, Any] = {
        "schema_version": 1,
        "status": "completed_smoke_run",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": {
            "id": MODEL_ID,
            "revision": MODEL_REVISION,
            "card_license_metadata": MODEL_CARD_LICENSE,
            "model_card": MODEL_CARD_URL,
            "card_reviewed": MODEL_CARD_REVIEWED,
            "license_and_training_data_terms_independently_verified": False,
            "human_facing_or_product_deployment_claim": False,
        },
        "runtime": {
            "python": sys.version.split()[0],
            "torch": str(torch.__version__),
            "transformers": str(transformers.__version__),
            "huggingface_hub": str(huggingface_hub.__version__),
            "tokenizers": str(tokenizers.__version__),
            "safetensors": str(safetensors.__version__),
            "device": "cpu",
            "cpu_threads": cpu_threads,
            "dtype": "float32",
        },
        "data": {
            "file_name": dataset_path.name,
            "sha256": _dataset_digest(dataset_path),
            "records": len(rows),
            "groups": len({row["group_id"] for row in rows}),
            "split_counts": split_counts,
            "contains_only_synthetic_demo_data": True,
            "dataset_upload_implemented_by_this_script": False,
        },
        "method": {
            "objective": "causal next-token loss on completion tokens only",
            "prompt_labels": -100,
            "padding_labels": -100,
            "training": "full-parameter supervised fine-tuning",
            "chat_template_used": False,
            "evaluation_policy": "validation before and after; public test split once after training",
        },
        "config": {
            "seed": seed,
            "epochs": epochs,
            "batch_size": batch_size,
            "max_length": max_length,
            "learning_rate": float(learning_rate),
            "optimizer": "AdamW",
            "weight_decay": 0.0,
            "network_download_allowed_for_this_run": bool(allow_download),
        },
        "metrics": {
            "optimizer_updates": update_count,
            "validation_nll_before": validation_before,
            "validation_nll_after": validation_after,
            "test_nll_after": test_after,
            "test_evaluations": 1,
        },
        "interpretation": (
            "A CPU pipeline smoke test on a tiny public synthetic English fixture. "
            "Loss values are not a benchmark, quality claim, Persian result, or deployment recommendation."
        ),
    }
    (output_dir / "run.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit a prompt/completion fixture or run a small pinned SFT demo")
    parser.add_argument("--mode", choices=("audit", "train"), default="audit")
    parser.add_argument("--data", type=Path, default=Path(__file__).with_name("sample_sft.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("/tmp/ch47-sft-demo"))
    parser.add_argument("--seed", type=int, default=47)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=5e-5)
    parser.add_argument("--cpu-threads", type=int, default=1)
    parser.add_argument(
        "--allow-download", action="store_true",
        help="explicitly allow downloading the revision-pinned model/tokenizer; default mode is cache-only",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.mode == "audit":
        report = audit_dataset(args.data, args.output, seed=args.seed)
    else:
        report = train_pythia_demo(
            args.data,
            args.output,
            seed=args.seed,
            epochs=args.epochs,
            batch_size=args.batch_size,
            max_length=args.max_length,
            learning_rate=args.learning_rate,
            cpu_threads=args.cpu_threads,
            allow_download=args.allow_download,
        )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
