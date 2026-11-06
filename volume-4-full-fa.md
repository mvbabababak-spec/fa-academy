# هنر و علم ساخت هوش — جلد چهارم

**The Art & Science of Building Intelligence | Babak & Ai**

وضعیت: ۱۵ فصل در نقشه؛ ۶ فصل از ۱۵ فصل تا این انتشار نگارش، آزموده و منتشر شده‌اند. این فایل Markdown است؛ PDF و EPUB تولید و آزموده نشده‌اند.

## فهرست فصل‌های منتشرشده

- فصل ۱ (سراسری ۴۷) — Continued Pretraining، Instruction Tuning و SFT
- فصل ۲ (سراسری ۴۸) — PEFT، Adapter، LoRA و QLoRA
- فصل ۳ (سراسری ۴۹) — مدل پاداش، RLHF، PPO، DPO، GRPO و RLAIF
- فصل ۴ (سراسری ۵۰) — دادهٔ مصنوعی، تقطیر و محاسبهٔ زمان آزمون
- فصل ۵ (سراسری ۵۱) — مدل‌های تصویر و هم‌ترازی متن–تصویر
- فصل ۶ (سراسری ۵۲) — مدل‌های صوت و گفتار

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

---

# جلد چهارم، فصل ۲ — PEFT، Adapter، LoRA و QLoRA

**نگاشت:** فصل محلی ۲ جلد چهارم = فصل سراسری ۴۸. **تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶.** فصل ۴۷ هدف CPT و SFT و ماسک پاسخ را جدا کرد؛ این فصل می‌پرسد هنگام تطبیق یک مدل پایه، آیا لازم است همهٔ وزن‌های آن تغییر کنند؟ روش‌های PEFT فقط بخش کوچکی از پارامترها را آموزش می‌دهند یا ورودی/نمایش‌های مدل را با پارامترهای افزوده تغییر می‌دهند. فصل بعدی، ۴۹، به دادهٔ ترجیح، reward model و الگوریتم‌های بهینه‌سازی می‌پردازد؛ روش‌های آن فصل در اینجا آموزش داده نمی‌شوند.

**پیش‌نیاز:** لایهٔ خطی، ماتریس وزن، backpropagation، SFT و اندازهٔ دسته؛ مفاهیم dtype و quantization از فصل ۴۵. **خروجی:** بتوانید سه خانوادهٔ adapter bottleneck، LoRA و QLoRA را از نظر پارامتر آموزش‌پذیر، وزن پایه، حافظه و اجرای inference مقایسه کنید؛ تعداد پارامتر LoRA را برای یک ماتریس حساب کنید؛ و پروتکلی طراحی کنید که در آن «کم‌حافظه‌تر» را با «کیفیت برابر» اشتباه نگیرد.

![شکل ۴-۲-۱ — چهار مسیر تطبیق یک لایه: در full fine-tuning همهٔ وزن‌های پایه trainable هستند؛ در adapter و LoRA وزن پایه ثابت می‌ماند و ماژول یا ماتریس کم‌رتبهٔ افزوده آموزش می‌بیند؛ در QLoRA وزن پایهٔ quantized ثابت است و LoRA با دقت محاسباتی جداگانه آموزش می‌بیند. نمودار فقط مسیر پارامترها را نشان می‌دهد و مقایسهٔ کیفیت یا مصرف واقعی حافظه نیست.](book-engineering/diagrams/v4-ch02-peft.svg)

**شکل ۴-۲-۱ —** «فقط پارامترهای جدید را آموزش می‌دهیم» به معنی حذف تمام محاسبات مدل پایه نیست. در LoRA و QLoRA عبور رو به عقب از پایه همچنان برای رسیدن گرادیان به adapter لازم است؛ وزن پایه gradient یا update نمی‌گیرد.

## ۱. PEFT نام یک خانواده است، نه یک الگوریتم

**Parameter-Efficient Fine-Tuning (PEFT)** به روش‌هایی گفته می‌شود که برای تطبیق یک مدل ازپیش‌آموزش‌دیده همهٔ وزن‌هایش را مثل full fine-tuning به‌روزرسانی نمی‌کنند. در بعضی روش‌ها پارامتر جدید به مدل افزوده می‌شود؛ در بعضی دیگر زیرمجموعه‌ای از وزن‌ها، نمایش‌های میانی یا embeddingهای prompt تغییر می‌کنند. هدف معمول می‌تواند کاهش پارامترهای trainable، کاهش حالت optimizer، کوچک‌کردن checkpoint مخصوص task، یا نگهداری چند سازگارساز کنار یک پایهٔ مشترک باشد.

«PEFT» نام یک طبقهٔ روش‌هاست؛ کتابخانهٔ Hugging Face **PEFT** پیاده‌سازی تعدادی از آن‌هاست. این دو را یکی نگیرید. Adapter bottleneck، LoRA، prompt/prefix tuning و IA³ در یک خانوادهٔ کلی قرار می‌گیرند، اما محل و صورت تغییرشان یکسان نیست [۲،۷]. این فصل بر سه مسیر نقشه تمرکز دارد: adapter کلاسیک، LoRA و ترکیب LoRA با quantization که معمولاً QLoRA نامیده می‌شود.

پارامتر کمتر به‌خودی‌خود کیفیت برابر، سرعت بیشتر، مصرف برق کمتر یا هزینهٔ کمتر را ثابت نمی‌کند. آن‌ها نتیجه‌های جداگانه‌اند که با مدل، backend، سخت‌افزار، داده و سنجه باید اندازه‌گیری شوند. PEFT نیز خودبه‌خود داده را مجاز، پاسخ را ایمن یا رفتار مدل را «هم‌تراز» نمی‌کند.

## ۲. سه پرسش جدا: چه چیزی train می‌شود، چه چیزی ذخیره می‌شود، چه چیزی اجرا می‌شود؟

برای مقایسهٔ روش‌ها، دست‌کم این سه ستون را مستقل ثبت کنید:

| پرسش | نمونهٔ پاسخ | چرا مهم است؟ |
|---|---|---|
| کدام پارامترها gradient و optimizer state می‌گیرند؟ | وزن کامل، adapter، یا عوامل A و B | به حافظهٔ آموزش و آزادی تطبیق مربوط است. |
| کدام فایل‌ها برای بازیابی یک task ذخیره می‌شوند؟ | کل checkpoint یا adapter به‌همراه config و شناسهٔ پایه | adapter تنها بدون پایهٔ سازگار مدل کامل نیست. |
| کدام عملیات در inference باقی می‌ماند؟ | لایهٔ افزوده، ماتریس merge‌شده، یا quantized kernel | latency و سازگاری را تعیین می‌کند؛ باید روی backend هدف آزمود. |

«trainable parameters» معمولاً تعداد وزن‌هایی است که `requires_grad=True` دارند؛ این عدد با تعداد پارامتر کل، حجم optimizer، اندازهٔ فایل، حافظهٔ اوج یا latency یکی نیست. برای مثال، freeze کردن وزن پایه gradientهای وزن را حذف می‌کند، اما activationهای لازم برای backprop و اجرای forward پایه باقی‌اند. گزارش خوب هر سه پرسش و محیط سنجش را جواب می‌دهد.

## ۳. Adapter bottleneck: مسیر تازه روی نمایش میانی

در adapter کلاسیک، یک ماژول کوچک به بلوک Transformer افزوده می‌شود. شکل سادهٔ آن hidden vector را از بعد `d` به bottleneck با بعد `m` پایین می‌آورد، activation اعمال می‌کند و دوباره به `d` برمی‌گرداند؛ خروجی با skip connection به نمایش اولیه افزوده می‌شود:

```text
h' = h + W_up · activation(W_down · h + b_down) + b_up
W_down ∈ R^(m×d),   W_up ∈ R^(d×m),   m << d
```

برای یک adapter ساده، تعداد وزن‌های دو projection تقریباً `2dm` است؛ bias، LayerNorm، محل درج، تعداد ماژول‌های هر بلوک و headهای task-specific می‌توانند شمار واقعی را عوض کنند. در طرح Houlsby و همکاران، adapterها در دو نقطه از بلوک‌های BERT قرار گرفتند؛ مقاله روی مجموعهٔ taskها و setup خودش نتیجهٔ پارامتر/عملکرد گزارش می‌کند، نه عددی برای همهٔ مدل‌های امروزی [۱].

ماژول bottleneck معمولاً nonlinear است و در forward جداگانه اجرا می‌شود. در نتیجه نمی‌توان آن را عموماً با جمع‌کردن یک ماتریس خطی در وزن پایه ادغام کرد. این هزینه ممکن است قابل قبول باشد اگر چند task با ماژول‌های کوچک نگهداری شوند؛ اما latency و حافظهٔ واقعی باید در serving سنجیده شوند. واژهٔ «adapter» در گفت‌وگوی روزمره گاهی به LoRA هم گفته می‌شود؛ در این فصل «adapter bottleneck» به ماژول میانی nonlinear و «LoRA» به update ماتریسی کم‌رتبه اشاره می‌کند.

## ۴. LoRA: محدودکردن تغییر وزن به یک زیرفضای کم‌رتبه

فرض کنید وزن یک projection خطی `W₀` با شکل `d_out × d_in` ثابت بماند. Full fine-tuning می‌تواند تمام خانه‌های آن را عوض کند؛ LoRA تغییر را به حاصل‌ضرب دو ماتریس باریک محدود می‌کند:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="وزن مؤثر برابر وزن پایهٔ ثابت به‌علاوهٔ ضریب مقیاس ضربدر حاصل‌ضرب ماتریس B با شکل خروجی در رتبه و ماتریس A با شکل رتبه در ورودی است">
  <mrow>
    <msub><mi>W</mi><mi>eff</mi></msub><mo>=</mo><msub><mi>W</mi><mn>0</mn></msub><mo>+</mo><mi>γ</mi><mi>B</mi><mi>A</mi>
  </mrow>
</math>

**متن جایگزین فرمول:** وزن مؤثر برابر وزن پایهٔ ثابت به‌علاوهٔ ضریب مقیاس ضربدر حاصل‌ضرب ماتریس B با شکل خروجی در رتبه و ماتریس A با شکل رتبه در ورودی است. در LoRA کلاسیک معمولاً `γ = α/r`، `A ∈ R^(r×d_in)`، `B ∈ R^(d_out×r)` و `r` از ابعاد لایه کوچک‌تر است [۳].

در forward، برای ورودی `x` می‌توان نوشت `y = W₀x + γBAx`. `W₀` frozen می‌ماند و `A` و `B` آموزش می‌بینند. پژوهش LoRA انگیزهٔ خود را با فرض تجربیِ کم‌رتبه‌بودن تغییرهای سازگارشده صورت‌بندی کرد و روی چند مدل/task مقایسه‌هایی گزارش داد [۳]. این یک فرض مفید برای طراحی روش است، نه قضیه‌ای که برای هر مدل، دامنه یا task تضمین کند رتبهٔ کوچک کافی باشد.

## ۵. شمار پارامترها را برای هر ماتریس حساب کنید

برای یک ماتریس وزن `d_out × d_in`، full fine-tuning به‌روزرسانی همین ماتریس شامل `d_out × d_in` وزن است. در LoRA، دو عامل `A` و `B` روی هم `r(d_in + d_out)` پارامتر دارند؛ bias، dropout و پارامترهای خارج از این لایه در این شمار ساده نیامده‌اند:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="تعداد پارامترهای آموزش‌پذیر LoRA برای یک ماتریس برابر رتبه ضربدر مجموع بعد ورودی و بعد خروجی است">
  <mrow>
    <msub><mi>N</mi><mi>LoRA</mi></msub><mo>=</mo><mi>r</mi><mo>(</mo><msub><mi>d</mi><mi>in</mi></msub><mo>+</mo><msub><mi>d</mi><mi>out</mi></msub><mo>)</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** تعداد پارامترهای آموزش‌پذیر LoRA برای یک ماتریس برابر رتبه ضربدر مجموع بعد ورودی و بعد خروجی است. نسبت این تعداد به وزن کامل همان ماتریس برابر `r(d_in+d_out)/(d_in d_out)` است.

برای ماتریس فرضی `4096 × 4096` و `r=16`، update شامل `16 × (4096+4096) = 131,072` پارامتر است؛ ماتریس پایه `16,777,216` خانه دارد. نسبتِ این **یک ماتریس** حدود `0.78%` است. این درصد به معماری و انتخاب targetها وابسته است؛ اگر LoRA را روی Q، K، V، O و لایه‌های MLP قرار دهید، تعداد پارامترهای همهٔ ماژول‌ها را جمع کنید. درصد یک ماتریس را به کل مدل تعمیم ندهید.

## ۶. رتبه، مقیاس و initialization سه انتخاب مستقل‌اند

`r` ظرفیت update کم‌رتبه را تعیین می‌کند و شمار پارامتر را خطی بالا می‌برد؛ `α` در روش کلاسیک شدت update را از راه `α/r` مقیاس می‌دهد. مقدارهای r و alpha نسخهٔ واحد و تضمین‌شده ندارند: باید با validation و بودجهٔ واقعی آزموده شوند. در `r` بزرگ‌تر ممکن است کیفیت، پایداری گرادیان، سرعت و حافظه به شکل‌های متفاوت تغییر کنند.

در initialization رایج LoRA، `B` صفر و `A` غیرصفر مقداردهی می‌شود؛ در نتیجه `BA=0` در آغاز و خروجی اولیه با پایه برابر می‌ماند. پیاده‌سازی‌ها ممکن است جزئیات initializer را تغییر دهند؛ مستندات PEFT در تاریخ بازبینی initialization پیش‌فرض و `LoraConfig` را توضیح می‌دهد [۷]. تست کردن یک batch و شمار پارامترهای trainable پیش از run واقعی مفید است.

**Rank-Stabilized LoRA (rsLoRA)** ضریب `α/√r` را به‌جای `α/r` به‌کار می‌گیرد. مقالهٔ rsLoRA استدلال و آزمایش‌های خودش را برای پایداری rank مطرح می‌کند؛ در PEFT گزینهٔ `use_rslora` این انتخاب را فعال می‌کند [۵،۷]. این گزینه قانون همگانی یا وعدهٔ کیفیت نیست؛ اگر آن را روشن می‌کنید، در config، checkpoint و مقایسه ثبت کنید. این فصل وارد جزئیات AdaLoRA، DoRA، LoftQ و دیگر شاخه‌ها نمی‌شود؛ نام آن‌ها را با LoRA پایه یکی نگیرید.

## ۷. کدام ماژول‌ها را هدف می‌گیریم؟

مدل‌ها نام‌گذاری و بسته‌بندی لایه‌های متفاوتی دارند. در بعضی معماری‌ها projectionها جداگانه `q_proj`، `k_proj`، `v_proj` و `o_proj` هستند؛ در برخی دیگر چند projection در یک لایهٔ fused یا نام متفاوت قرار دارند. فهرست `target_modules` که برای یک معماری کار می‌کند، ممکن است در معماری دیگر هیچ لایه‌ای را پیدا نکند یا بیش از آنچه می‌خواهید انتخاب کند.

روند امن این است: نام و شکل ماژول‌های واقعی مدل را چاپ/ممیزی کنید؛ انتخاب target را با معماری و نسخهٔ کتابخانه تطبیق دهید؛ سپس تعداد لایه‌ها و پارامترهای LoRA را پس از wrap شدن بررسی کنید. انتخاب فقط Q/V، همهٔ projectionهای attention یا همهٔ linears مصالحه‌های متفاوت‌اند. `all-linear` در APIهای جاری PEFT یک shorthand است، اما coverage و سازگاری را برای مدل شما خودتان بررسی کنید [۷،۸].

قرار دادن LoRA روی لایه‌های بیشتری ظرفیت و پارامتر را بالا می‌برد. هدف‌گرفتن لایهٔ نادرست، head تصادفی، embedding یا لایهٔ خارج از مسیر آموزش می‌تواند adapter بی‌اثر یا فایل ناقص بسازد. ماژول task-specificِ تصادفی‌مقداردهی‌شده گاهی باید با گزینه‌ای مانند `modules_to_save` همراه checkpoint شود؛ انتخاب آن هم معماری‌محور است و باید بازخوانی‌پذیر باشد.

## ۸. وزن پایه frozen است، اما محاسبهٔ پایه حذف نمی‌شود

وقتی وزن پایه `requires_grad=False` است، optimizer برای آن weight gradient/حالت به‌روزرسانی نگه نمی‌دارد؛ اما forward پایه باید اجرا شود. در backprop نیز گرادیان نسبت به ورودی‌ها از محاسبهٔ لایه‌های frozen عبور می‌کند تا به adapterهای لایه‌های قبلی برسد. به همین دلیل PEFT می‌تواند حافظهٔ gradient و optimizer state را کاهش دهد، ولی activationها، attention، sequence length، batch و workspace هنوز می‌توانند غالب باشند.

این تفاوت را در مقایسه با full fine-tuning روشن کنید: «پارامتر trainable کمتر» لزوماً به معنی «زمان آموزش به همان نسبت کمتر» نیست. حافظهٔ بارگذاری مدل پایه نیز باقی است؛ QLoRA این قسمت را با quantization هدف می‌گیرد، اما metadata، activation و اجرای backward همچنان هزینه دارند. Gradient checkpointing، accumulation و batching روش‌های جداگانه‌اند و باید در هر run ثبت شوند؛ آن‌ها ویژگی خود LoRA نیستند.

## ۹. Adapter و LoRA را چطور ذخیره و سرو می‌کنیم؟

در بسیاری از کتابخانه‌ها می‌توان وزن adapter را جدا از وزن پایه ذخیره کرد. فایل جداگانه، اگر به‌تنهایی منتشر شود، معمولاً باید همراه شناسه/نسخه یا hash مدل پایه، tokenizer، config، target moduleها، rank، alpha، dtype و هر head لازم توصیف شود. بارگذاری adapter روی checkpoint نامتجانس ممکن است از نظر شکل رد شود، یا بدتر، با شکل مشابه ولی معنای متفاوت بارگذاری شود؛ شناسهٔ نام متحرک `main` برای بازتولید دقیق کافی نیست.

در LoRA خطیِ معمول، اگر adapter با همان precision و semantics merge شود، حاصل‌ضرب `γBA` را می‌توان به وزن پایه افزود: `W_eff = W₀ + γBA`. این کار ممکن است ماژول افزوده را از مسیر inference بردارد. اگر چند adapter هم‌زمان یا swapپذیر لازم باشد، نگه‌داشتن آن‌ها جدا انعطاف می‌دهد اما عملیات افزوده دارد. برای لایهٔ nonlinear bottleneck چنین ادغام ساده‌ای عموماً برقرار نیست.

در مدل quantized، merge/unmerge، پشتیبانی kernel و تبدیل dtype/quantization وابسته به نسخه و backend است؛ dequantize/merge/requantize ممکن است گردکردن جدید و هزینهٔ حافظه داشته باشد. پیش از انتشار، هم برابری عددی تقریبی و هم خروجی/latency روی همان سیستم serving را بسنجید. مستندات PEFT توابع merge/unload را دارد، اما وجود API تضمین سازگاری با هر لایه و quantization نیست [۷،۸].

## ۱۰. QLoRA: LoRA روی پایهٔ quantized، نه آموزش همه‌چیز در ۴ بیت

در QLoRA، وزن‌های پایه پیش از آموزش به قالب کم‌دقت (در مقاله ۴-bit) ذخیره می‌شوند و ثابت می‌مانند؛ LoRA factors آموزش‌پذیرند و گرادیان از محاسبات پایه به آن‌ها می‌رسد. پس عبارت «QLoRA مدل را در ۴ بیت fine-tune می‌کند» اگر منظورش update همهٔ وزن‌های پایه باشد گمراه‌کننده است. تمرین QLoRA عموماً وزن‌های LoRA را با dtype محاسباتی دیگری نگه می‌دارد و optimizer را روی بخش آموزش‌پذیر اجرا می‌کند [۴،۹].

QLoRA مقالهٔ Dettmers و همکاران سه جزئیات را برجسته کرد: NF4، double quantization و paged optimizers. در همان setup مقاله، نویسندگان امکان تطبیق مدل ۶۵B را روی یک GPU 48GB گزارش کردند [۴]. این عدد نتیجهٔ پیکربندی و نرم‌افزار همان آزمایش است، نه حداقل VRAM عمومی یا تضمین اینکه هر مدل 65B با هر طول و batch روی هر کارت جا شود.

QLoRA memory optimization است، نه ارزیابیِ خودکارِ کیفیت؛ می‌تواند بر کیفیت اثر بگذارد یا run را از نظر سخت‌افزار ممکن کند، اما آیا خروجی بهتر، هم‌ارز یا بدتر است باید با baseline همسان سنجیده شود. مقالهٔ اصلی نتایج تجربی خودش را روی مدل‌ها، داده‌ها و benchmarkهای خودش گزارش می‌دهد؛ انتقال آن‌ها به زبان، task یا checkpoint دیگر نیازمند آزمایش تازه است.

## ۱۱. NF4، nested quantization و precision محاسبه

در مستندات Transformers، `load_in_4bit=True` قالب ذخیرهٔ پایه را فعال می‌کند؛ `bnb_4bit_quant_type="nf4"` نوع quantization است؛ `bnb_4bit_use_double_quant=True` nested quantization را برای scaleها به کار می‌گیرد؛ و `bnb_4bit_compute_dtype` dtype محاسبهٔ ماتریسی را مشخص می‌کند [۹]. این گزینه‌ها مفهوم‌های جدا هستند. ۴-bit storage به این معنا نیست که تمام ضرب ماتریسی یا adapter هم با ۴-bit انجام شود.

NF4 در QLoRA برای توزیع وزن‌های فرض‌شده نرمال طراحی شد؛ «بهینه برای نرمال» حکم نمی‌کند بهترین انتخاب برای هر activation، embedding، نوع وزن یا مدل باشد. Double quantization، بنا بر مقاله و راهنمای Transformers، اندازهٔ میانگین برخی ثابت‌های quantization را کم می‌کند؛ مقدار گزارش‌شده به block format و implementation مربوط است [۴،۹]. در notebook خود از مقدار پیش‌فرض کتابخانه کورکورانه پیروی نکنید؛ config واقعی را ذخیره کنید.

Paged optimizer در مقالهٔ QLoRA برای مدیریت memory spike با unified memoryِ NVIDIA توصیف شده است [۴]. نام مشابه در کتابخانه‌های دیگر لزوماً رفتار یا سخت‌افزار یکسان ندارد. قبل از انتخاب، backend، نسخهٔ CUDA/کتابخانه، سازگاری کارت، dtype قابل پشتیبانی و محدودیت‌های install را از جدول همان نسخه بخوانید. مستندات جاری Transformers هنگام بازبینی، backendهای پشتیبانی‌شدهٔ bitsandbytes را جداگانه فهرست می‌کرد [۹].

## ۱۲. حافظه را از اجزایش برآورد کنید، نه از «چهار بیت» به‌تنهایی

برای یک پایهٔ فرضی با `N` وزن، payload خام ۴-bit حد نظریِ حدود `N/2` بایت دارد، چون هر بایت دو مقدار ۴-bit نگه می‌دارد. این **کران پایین وزن packed** است، نه VRAM کل. اندازهٔ واقعی وزن می‌تواند به group scale و metadata، alignment، لایه‌های quantizeنشده، tableها، padding و serialization بستگی داشته باشد.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="حافظهٔ آموزش حاصل جمع حافظهٔ وزن پایهٔ quantized، پارامتر و optimizer adapter، activationها و workspace موقت است">
  <mrow><msub><mi>M</mi><mi>train</mi></msub><mo>≈</mo><msub><mi>M</mi><mi>base</mi></msub><mo>+</mo><msub><mi>M</mi><mi>adapter</mi></msub><mo>+</mo><msub><mi>M</mi><mi>optimizer</mi></msub><mo>+</mo><msub><mi>M</mi><mi>activations</mi></msub><mo>+</mo><msub><mi>M</mi><mi>workspace</mi></msub></mrow>
</math>

**متن جایگزین فرمول:** حافظهٔ آموزش تقریباً مجموع وزن پایهٔ quantized، پارامتر و حالت optimizer adapter، activationها و workspace موقت است. این رابطه فقط تفکیک مؤلفه‌ها را نشان می‌دهد و مقدار اندازه‌گیری‌شده نیست.

حافظهٔ full fine-tuning به dtype وزن و gradient، optimizer، sharding، offload، activation و checkpointing بستگی دارد؛ عدد ثابت «چند بایت به‌ازای پارامتر» را بدون مفروضات به همهٔ runها نسبت ندهید. برای مقایسهٔ منصفانه، موارد زیر را کنار هم ثبت کنید:

| مورد ثبت | خط پایهٔ مناسب |
|---|---|
| مدل و revision، tokenizer، tokenizer template | یکسان در همهٔ پیکربندی‌های مقایسه |
| داده، split و تعداد supervised token | یکسان و hash‌شده |
| context، batch مؤثر، updateها و optimizer | هم‌بودجه یا تفاوت صریح و توجیه‌شده |
| rank، alpha، target modules، precision و quantization | config کامل و نسخه‌دار |
| peak allocated/reserved، throughput و latency | اندازه‌گیری روی دستگاه/نسخهٔ مشخص، با warm-up و روش ثابت |
| معیار task و test نهایی | تعریف‌شده پیش از run؛ test پس از انتخاب نهایی فقط یک‌بار |

حالت audit این فصل فقط کران پایین payload را از fixture شکل‌ها حساب می‌کند؛ هیچ VRAM، RAM، throughput یا latency را اندازه‌گیری نمی‌کند. به عدد آن برای خرید GPU یا وعدهٔ اجرای مدل بزرگ تکیه نکنید.

## ۱۳. PEFT انتخابی برای هر task با پروتکل ارزیابی یکی نیست

پیش از آموزش، full fine-tuning یا baseline موجود را در صورت امکان مشخص کنید؛ نسخهٔ LoRA و QLoRA را روی همان مدل، داده، split، prompt/template، تعداد update و معیار مقایسه کنید. اگر full fine-tuning در بودجهٔ سخت‌افزار ممکن نیست، محدودیت baseline را ثبت کنید و صرفاً ادعای «بهتر از full fine-tune» ننویسید. بودجهٔ بهینه‌سازی متفاوت، مقایسهٔ کیفیت را مخدوش می‌کند.

برای task، معیار مرتبط انتخاب کنید: NLL، accuracy، exact match، rubric انسانی یا مجموعه‌ای از معیارها. پارامترهای trainable و اندازهٔ adapter را در کنار نتیجه گزارش کنید؛ افزایش ظرفیت rank و target moduleها را با validation تنظیم کنید؛ test را در طول sweeps انتخاب نکنید. اگر ارزیاب انسانی یا مدل دیگری به کار می‌رود، rubric، نمونه‌گیری، ترتیب نمایش، اختلاف ارزیاب و محدودیت‌های آن را بنویسید.

«برابر بودن» باید operational تعریف شود: حاشیهٔ قابل‌قبول، عدم قطعیت و جمعیت ارزیابی را پیشاپیش مشخص کنید. یک run یا یک benchmark محبوب برتری یا برابری کلی را ثابت نمی‌کند. برای فارسی یا task تخصصی نیز داده، ارزیاب و benchmark همان زبان/کاربرد لازم است؛ این پروژهٔ انگلیسی‌محور یا fixture ریاضی چنین شواهدی نمی‌سازد.

## ۱۴. شکست‌های رایج در PEFT و QLoRA

- هیچ پارامتری trainable نیست چون همهٔ ماژول‌ها freeze شده‌اند؛ یا بیش از قصد trainable است چون `bias`, LayerNorm یا head از تنظیم بیرون مانده است. شمار parameters و optimizer groups را log کنید.
- `target_modules` خالی است، نام آن با architecture یکی نیست، یا fused layer را به شکل اشتباه هدف گرفته است. پیش از آموزش، نام و شکل لایه‌های wrap‌شده را inspect کنید.
- adapter ذخیره می‌شود اما base model، revision، tokenizer، config یا head مخصوص task ثبت نمی‌شود؛ فایل برای بازتولید کافی نیست.
- `r`, `alpha`, `use_rslora`, dropout، initializer یا dtype در checkpoint یا گزارش نیست؛ نتیجه قابل نسبت‌دادن به تنظیمات نیست.
- مدل ۴-bit بارگیری شده اما `prepare_model_for_kbit_training`, gradient-checkpointing، dtype، device placement یا backend با نسخهٔ مورد استفاده سازگار نیست. دستور جاری را از مستندات همان نسخه بگیرید، نه یک notebook قدیمی.
- کاربر انتظار دارد quantization خودبه‌خود VRAM را به نصف دقیق کم کند؛ scaleها، activations، optimizer، fragmentation و لایه‌های غیرquantized حذف نشده‌اند.
- adapter در train merge شده یا dropout در inference اشتباهاً فعال می‌ماند؛ یا merge روی quantized weights به‌عنوان برابری دقیق فرض می‌شود.
- PEFT به‌عنوان ضمانت حفظ دانش، ایمنی، privacy، حقوق داده یا کیفیت محصول تفسیر می‌شود؛ هیچ‌کدام از تعداد پارامترها نتیجه نمی‌شود.

## ۱۵. نمونهٔ API کتابخانه‌ها: نسخه را با مدل واقعی تطبیق دهید

در مستندات رسمی PEFT که ۶ نوامبر ۲۰۲۶ بازبینی شد، راه معمول شامل ساخت `LoraConfig`، تعیین rank/target modules، wrap کردن پایه با `get_peft_model` و سپس آموزش بود. نمونهٔ زیر **توضیح API** است و در پروژهٔ همین فصل اجرا نشده؛ نام لایه‌ها برای مدل واقعی باید بررسی شود. مستندات زنده‌ای که بازبینی شد PEFT main و stable v0.21.0 و مستندات Transformers v5.22.1 را نشان می‌داد [۷–۹].

```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    target_modules=["q_proj", "v_proj"],
    task_type="CAUSAL_LM",
)
peft_model = get_peft_model(base_model, config)
peft_model.print_trainable_parameters()
```

QLoRA-style load در Transformers نیز با `BitsAndBytesConfig` تعریف می‌شود؛ کد کوتاه زیر فقط قالب تنظیم را نشان می‌دهد و device, model revision, placement, version compatibility, training arguments یا اجرای CUDA را کامل نمی‌کند:

```python
import torch
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)
```

در run واقعی، نسخهٔ `torch`, `transformers`, `peft`, `bitsandbytes`, `accelerate`، backend، CUDA/driver و مدل را دقیقاً pin/ثبت کنید؛ API و پشتیبانی پلتفرم تغییر می‌کند. این فایل‌ها را با project toy این فصل اشتباه نگیرید: آن پروژه عمدی dependency شبکه و مدل ندارد.

## ۱۶. پروژهٔ اجرایی: ماتریس کوچک، رفتار قابل‌آزمون

[پروژهٔ PEFT/LoRA فصل ۴۸](book-engineering/projects/48-peft-lab/README.md) یک `nn.Linear` کوچک را با `W₀` frozen و دو عامل trainable پیاده‌سازی می‌کند؛ یک bottleneck residual adapter هم برای مقایسه دارد. تست‌ها initialization همانیِ update صفر، freeze پایه، تعداد عوامل، gradient، merge در eval، ابعاد fixture و audit آفلاین را می‌سنجند. اجرای `toy-lora` روی نگاشت خطی مصنوعی انجام می‌شود؛ loss صرفاً خطای همان مثال ساختگی است.

حالت `audit` از سه ردیف fixtureِ نام‌گذاری‌شده به‌عنوان `fixture.*`، تعداد پارامترهای پایه و LoRA را حساب می‌کند و برای وزن فشرده کران پایین می‌دهد؛ رکوردها معماری مدل واقعی نیستند. حالت demo یک ماتریس هدف rank-2 را با seed=48 و ۵۰۰ گام CPU بازسازی می‌کند. در گزارش ممیزی، نتیجهٔ دقیق اجرای واقعی و محدودیتش ثبت می‌شود. این اجرا PEFT library یا مدل زبانی را آزمایش نمی‌کند.

## ۱۷. چک‌لیست پیش از انتخاب روش

۱. هدف task، مدل پایه، revision، tokenizer و قالب prompt ثبت شده‌اند. ۲. full fine-tuning، adapter bottleneck، LoRA یا QLoRA را بر اساس محدودیت مشخص انتخاب کرده‌ام، نه صرفاً نام رایج. ۳. `target_modules` واقعاً در معماری موجودند و شمارش ماژول‌ها/پارامترهای trainable بازبینی شده است. ۴. rank، alpha یا scaling variant، dropout، initializer، bias، head و `modules_to_save` مستندند. ۵. برای QLoRA، quantization type، double quantization، compute dtype، backend و placement ثبت شده‌اند. ۶. base، adapter، tokenizer و config به شکل سازگار ذخیره می‌شوند. ۷. حافظهٔ اوج، زمان/throughput و latency روی دستگاه هدف با روش ثابت اندازه‌گیری می‌شوند؛ برآورد payload را با peak حافظه اشتباه نمی‌گیرم. ۸. معیار، baseline، split و بودجهٔ مقایسه پیش از آموزش تعیین شده‌اند؛ test دیرهنگام استفاده می‌شود. ۹. ادعای کیفیت به داده و setup واقعی محدود می‌ماند و از شمار پارامتر یا fixture toy نتیجه‌گیری نمی‌کنم.

## ۱۸. تمرین‌ها و پاسخ‌نامهٔ مستقل

**تمرین ۱.** برای projection فرضی `d_in=2048`, `d_out=8192`, `r=8`، تعداد پارامترهای A و B را جداگانه و جمع را حساب کنید. نسبت آن به ماتریس کامل چند درصد است؟ کدام موارد در این نسبت شمرده نشده‌اند؟

**تمرین ۲.** برای یک adapter bottleneck با `d=1024` و `m=32`، فقط تعداد وزن‌های دو projection را برآورد کنید. دو دلیل بیاورید که چرا این عدد با کل پارامترهای روش مقاله یا اندازهٔ inference برابر نیست.

**تمرین ۳.** یک مدل با ۴ میلیارد وزن را در ۴-bit packed ذخیره می‌کنید. payload خام حد پایین چند بایت است؟ حداقل چهار مؤلفهٔ حافظهٔ دیگر را نام ببرید و توضیح دهید چرا عدد شما VRAM تخمینی کامل نیست.

**تمرین ۴.** در یک معماری `qkv_proj` لایهٔ fused است و `q_proj` مجزا وجود ندارد. اگر پیکربندی LoRA هیچ targetی پیدا نکرد، چه چیزهایی را inspect و ثبت می‌کنید؟ چرا کپی‌کردن target modules از مدل دیگری راه‌حل قابل‌اعتماد نیست؟

**تمرین ۵.** دو checkpoint را مقایسه می‌کنید: LoRA full precision و QLoRA NF4. برای ادعای کیفیت/حافظهٔ بهتر، چه چیزهایی باید ثابت، چه چیزهایی باید اندازه‌گیری و test چه زمانی مصرف شود؟

**پاسخ‌نامهٔ مستقل:** [پاسخ‌نامهٔ تشریحی فصل ۴۸](book-engineering/answers/48-peft-fa.md). **پروژه:** [README آزمایشگاه](book-engineering/projects/48-peft-lab/README.md)؛ **گزارش اجرا و محدودیت:** [گزارش ممیزی فصل ۴۸](book-engineering/chapters/48-audit-report-fa.md).

## ۱۹. جمع‌بندی و مرز فصل بعد

PEFT مجموعه‌ای از راه‌هاست تا وزن پایه را کامل fine-tune نکنیم. Adapter bottleneck تغییر را به ماژول‌های کم‌بعد/nonlinear در نمایش‌ها می‌سپارد؛ LoRA update وزن را به `BA` کم‌رتبه با scaling مشخص بازپارامتردهی می‌کند؛ QLoRA LoRA را با پایهٔ کم‌حافظهٔ quantized ترکیب می‌کند. هزینه‌ای که واقعاً کم می‌شود باید با تعداد پارامتر، حافظهٔ اوج، زمان، checkpoint و inference جدا سنجیده شود. در quantization، storage precision و compute precision را با یکدیگر اشتباه نگیرید.

فصل ۴۹ پس از این روش‌های supervised/parameter-efficient، دادهٔ ترجیح، reward model، RLHF/PPO، DPO، GRPO، RLAIF و Constitutional AI را بررسی می‌کند. خروجی toy این فصل نه ترجیح انسانی دارد، نه پاداش، نه policy evaluation؛ برای آن مفاهیم شاهد محسوب نمی‌شود.

## ۲۰. منابع و تاریخ بازبینی

منابع و صفحات رسمی زیر در **۶ نوامبر ۲۰۲۶** بازبینی شدند. عددهای تجربی به setup نویسندگان محدودند؛ مستندات API زنده‌اند و نسخهٔ مشاهده‌شده در همان روز ثبت شده است.

1. Houlsby, N. و همکاران، “Parameter-Efficient Transfer Learning for NLP”، ICML 2019, PMLR 97, 2790–2799. [متن و citation](https://proceedings.mlr.press/v97/houlsby19a.html). نتایج adapter مربوط به BERT و setup مقاله‌اند.
2. He, J. و همکاران، “Towards a Unified View of Parameter-Efficient Transfer Learning”، ICLR 2022, [arXiv:2110.04366](https://arxiv.org/abs/2110.04366). چارچوبی برای دیدن محل و صورت update روش‌های PEFT؛ نتایج به taskهای مقاله مربوط‌اند.
3. Hu, E. J. و همکاران، “LoRA: Low-Rank Adaptation of Large Language Models”، ICLR 2022, [arXiv:2106.09685](https://arxiv.org/abs/2106.09685). تعریف low-rank update، scaling و آزمایش‌های همان کار.
4. Dettmers, T. و همکاران، “QLoRA: Efficient Finetuning of Quantized LLMs”، 2023, [arXiv:2305.14314](https://arxiv.org/abs/2305.14314). NF4، double quantization و paged optimizer در setup نویسندگان.
5. Kalajdzievski, D., “A Rank Stabilization Scaling Factor for Fine-Tuning with LoRA”، 2023, [arXiv:2312.03732](https://arxiv.org/abs/2312.03732). rsLoRA و scaling رتبه‌پایدار در تحلیل/آزمایش مقاله.
6. Li, Y. و همکاران، “LoftQ: LoRA-Fine-Tuning-Aware Quantization for Large Language Models”، 2023, [arXiv:2310.08659](https://arxiv.org/abs/2310.08659). initialization آگاه از quantization؛ خارج از پیاده‌سازی پروژهٔ این فصل.
7. Hugging Face PEFT، [راهنمای LoRA](https://huggingface.co/docs/peft/main/en/conceptual_guides/lora) و [API/تنظیمات](https://huggingface.co/docs/peft/main/en/package_reference/lora). نسخهٔ stable روی راهنمای main در تاریخ بازبینی v0.21.0 نشان داده می‌شد؛ API/معماری‌محور است.
8. Hugging Face PEFT، [راهنمای quantization](https://huggingface.co/docs/peft/developer_guides/quantization). پشتیبانی و ترکیب روش‌ها را با نسخهٔ نصب‌شده دوباره تطبیق دهید.
9. Hugging Face Transformers، [راهنمای bitsandbytes و QLoRA](https://huggingface.co/docs/transformers/en/quantization/bitsandbytes). نسخهٔ جاری مشاهده‌شده در ۶ نوامبر ۲۰۲۶ برابر v5.22.1 بود؛ جدول backend سخت‌افزار versioned است.
10. PyTorch 2.6.0، [torch.nn.Linear](https://docs.pytorch.org/docs/2.6/generated/torch.nn.Linear.html) و [torch.nn.Parameter](https://docs.pytorch.org/docs/2.6/generated/torch.nn.parameter.Parameter.html). قرارداد لایهٔ خطی و پارامترها در پروژهٔ toy.
11. PyTorch 2.6.0، [autograd mechanics](https://docs.pytorch.org/docs/2.6/notes/autograd.html). رفتار autograd به گراف و `requires_grad` وابسته است؛ frozen بودن وزن محاسبهٔ forward را حذف نمی‌کند.

## ۲۱. پیوست اجرایی: فایل پروژهٔ آزموده‌شده

کد زیر با بایت‌های `book-engineering/projects/48-peft-lab/peft_lab.py` یکسان است؛ builder و checker این قرارداد را کنترل می‌کنند. این کد یک آزمایشگاه CPU برای لایه‌های مصنوعی است، نه پیاده‌سازی PEFT library یا QLoRA واقعی.

```python
"""CPU-only algebra lab for adapters, LoRA and QLoRA accounting.

This module uses synthetic linear layers only. It does not load a pretrained
model, quantize real weights, benchmark hardware, or claim task quality.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import torch
from torch import nn
from torch.nn import functional as F


def lora_parameter_count(in_features: int, out_features: int, rank: int) -> int:
    """Number of A/B parameters for one bias-free low-rank update."""
    if min(in_features, out_features, rank) <= 0:
        raise ValueError("dimensions and rank must be positive")
    if rank > min(in_features, out_features):
        raise ValueError("rank cannot exceed the smaller matrix dimension in this lab")
    return rank * (in_features + out_features)


def quantized_payload_lower_bound(parameter_count: int, bits: int = 4) -> int:
    """Packed weight payload only; excludes scales, metadata and all other memory."""
    if parameter_count < 0 or bits <= 0:
        raise ValueError("parameter_count must be non-negative and bits positive")
    return math.ceil(parameter_count * bits / 8)


class LoRALinear(nn.Module):
    """Frozen nn.Linear plus a trainable low-rank update."""

    def __init__(
        self,
        in_features: int,
        out_features: int,
        rank: int,
        alpha: float,
        *,
        bias: bool = True,
        dropout: float = 0.0,
        rank_stabilized: bool = False,
    ) -> None:
        super().__init__()
        lora_parameter_count(in_features, out_features, rank)
        if not math.isfinite(alpha) or alpha <= 0:
            raise ValueError("alpha must be finite and positive")
        if not 0.0 <= dropout < 1.0:
            raise ValueError("dropout must be in [0, 1)")
        self.in_features = in_features
        self.out_features = out_features
        self.rank = rank
        self.alpha = float(alpha)
        self.rank_stabilized = bool(rank_stabilized)
        divisor = math.sqrt(rank) if rank_stabilized else rank
        self.scaling = self.alpha / divisor
        self.base = nn.Linear(in_features, out_features, bias=bias)
        self.base.requires_grad_(False)
        self.lora_A = nn.Parameter(torch.empty(rank, in_features))
        self.lora_B = nn.Parameter(torch.zeros(out_features, rank))
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
        self.lora_dropout = nn.Dropout(dropout)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        low_rank = F.linear(F.linear(self.lora_dropout(inputs), self.lora_A), self.lora_B)
        return self.base(inputs) + self.scaling * low_rank

    def merged_layer(self) -> nn.Linear:
        """Return a fresh dense layer with the update folded into its weight."""
        merged = nn.Linear(
            self.in_features,
            self.out_features,
            bias=self.base.bias is not None,
            device=self.base.weight.device,
            dtype=self.base.weight.dtype,
        )
        with torch.no_grad():
            merged.weight.copy_(self.base.weight + self.scaling * (self.lora_B @ self.lora_A))
            if self.base.bias is not None:
                merged.bias.copy_(self.base.bias)
        return merged

    def trainable_parameter_count(self) -> int:
        return sum(parameter.numel() for parameter in self.parameters() if parameter.requires_grad)


class BottleneckAdapter(nn.Module):
    """Simple residual down-activation-up adapter for a hidden vector."""

    def __init__(self, hidden_size: int, bottleneck_size: int) -> None:
        super().__init__()
        if min(hidden_size, bottleneck_size) <= 0 or bottleneck_size > hidden_size:
            raise ValueError("adapter dimensions must be positive and bottleneck <= hidden size")
        self.down = nn.Linear(hidden_size, bottleneck_size, bias=False)
        self.up = nn.Linear(bottleneck_size, hidden_size, bias=False)
        nn.init.zeros_(self.up.weight)

    def forward(self, hidden: torch.Tensor) -> torch.Tensor:
        return hidden + self.up(F.gelu(self.down(hidden)))


def validate_fixture(rows: Any) -> list[dict[str, Any]]:
    if not isinstance(rows, list) or not rows:
        raise ValueError("fixture must be a non-empty JSON list")
    seen: set[str] = set()
    clean: list[dict[str, Any]] = []
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f"row {index} must be an object")
        name = row.get("name")
        if not isinstance(name, str) or not name.strip() or name in seen:
            raise ValueError(f"row {index} needs a unique non-empty name")
        seen.add(name)
        fields = ("in_features", "out_features", "rank", "alpha", "weight_bits")
        if any(field not in row for field in fields):
            raise ValueError(f"row {index} is missing a required field")
        in_features, out_features, rank = (row[k] for k in fields[:3])
        if any(type(value) is not int for value in (in_features, out_features, rank)):
            raise ValueError(f"row {index}: dimensions and rank must be integers")
        lora_parameter_count(in_features, out_features, rank)
        alpha, bits = row["alpha"], row["weight_bits"]
        if isinstance(alpha, bool) or not isinstance(alpha, (int, float)) or not math.isfinite(alpha) or alpha <= 0:
            raise ValueError(f"row {index}: alpha must be finite and positive")
        if type(bits) is not int or bits not in (4, 8, 16, 32):
            raise ValueError(f"row {index}: weight_bits must be one of 4, 8, 16, 32")
        full = in_features * out_features
        trainable = rank * (in_features + out_features)
        clean.append({
            "name": name,
            "in_features": in_features,
            "out_features": out_features,
            "rank": rank,
            "alpha": float(alpha),
            "weight_bits": bits,
            "base_weight_parameters": full,
            "lora_trainable_parameters": trainable,
            "lora_to_base_percent_for_this_matrix": 100.0 * trainable / full,
            "packed_weight_payload_lower_bound_bytes": quantized_payload_lower_bound(full, bits),
        })
    return clean


def audit_fixture(path: Path) -> dict[str, Any]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    layers = validate_fixture(rows)
    return {
        "schema_version": 1,
        "status": "validated_only",
        "training_performed": False,
        "model_loaded": False,
        "model_downloaded": False,
        "fixture": path.name,
        "fixture_kind": "synthetic layer-shape accounting; not a model architecture",
        "layers": layers,
        "totals": {
            "base_weight_parameters_in_fixture": sum(row["base_weight_parameters"] for row in layers),
            "lora_trainable_parameters_in_fixture": sum(row["lora_trainable_parameters"] for row in layers),
            "quantized_weight_payload_lower_bound_bytes": sum(row["packed_weight_payload_lower_bound_bytes"] for row in layers),
        },
        "memory_note": "payload lower bound only; excludes quantization metadata, non-quantized layers, activations, gradients, optimizer, temporary buffers and runtime overhead",
        "claim_boundary": "does not measure GPU/CPU peak memory, quality, throughput, compatibility or a real pretrained model",
    }


def run_toy_demo(steps: int = 500, seed: int = 48) -> dict[str, Any]:
    """Fit an exactly rank-two synthetic matrix change as an algebra smoke test."""
    if steps <= 0:
        raise ValueError("steps must be positive")
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    in_features, out_features, rank, alpha = 16, 12, 2, 2.0
    scale = alpha / rank
    base_weight = torch.randn(out_features, in_features) * 0.12
    target_A = torch.randn(rank, in_features) * 0.10
    target_B = torch.randn(out_features, rank) * 0.10
    target_weight = base_weight + scale * (target_B @ target_A)
    inputs = torch.randn(96, in_features)
    targets = F.linear(inputs, target_weight)

    model = LoRALinear(in_features, out_features, rank, alpha, bias=False)
    with torch.no_grad():
        model.base.weight.copy_(base_weight)
    initial_mse = float(F.mse_loss(model(inputs), targets).item())
    optimizer = torch.optim.Adam((model.lora_A, model.lora_B), lr=0.04)
    model.train()
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)
        loss = F.mse_loss(model(inputs), targets)
        loss.backward()
        optimizer.step()
    model.eval()
    final_mse = float(F.mse_loss(model(inputs), targets).item())
    return {
        "schema_version": 1,
        "status": "synthetic_demo_completed",
        "training_performed": True,
        "model_loaded": False,
        "model_downloaded": False,
        "fixture_kind": "generated synthetic linear mapping",
        "seed": seed,
        "steps": steps,
        "device": "cpu",
        "dtype": "float32",
        "input_shape": list(inputs.shape),
        "base_weight_shape": [out_features, in_features],
        "rank": rank,
        "alpha": alpha,
        "lora_trainable_parameters": model.trainable_parameter_count(),
        "base_parameters_trainable": any(parameter.requires_grad for parameter in model.base.parameters()),
        "initial_mse": initial_mse,
        "final_mse": final_mse,
        "merge_max_abs_error": float((model(inputs) - model.merged_layer()(inputs)).abs().max().item()),
        "claim_boundary": "algebra/implementation smoke test only; not model quality, NLP, Persian, benchmark, hardware or deployment evidence",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline PEFT algebra and synthetic LoRA lab")
    parser.add_argument("--mode", choices=("audit", "toy-lora"), required=True)
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="directory for run.json")
    parser.add_argument("--steps", type=int, default=500)
    args = parser.parse_args()
    if args.mode == "audit":
        if args.fixture is None:
            parser.error("--fixture is required for --mode audit")
        result = audit_fixture(args.fixture)
    else:
        result = run_toy_demo(steps=args.steps)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "run.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

---

# جلد چهارم، فصل ۳ — مدل پاداش، RLHF، PPO، DPO، GRPO و RLAIF

**نگاشت:** فصل محلی ۳ جلد چهارم = فصل سراسری ۴۹. **تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶.** فصل ۴۷ هدف‌های Continued Pretraining و SFT را از هم جدا کرد و فصل ۴۸ راه‌های کم‌پارامتر برای تطبیق مدل را بررسی کرد. این فصل یک پرسش دیگر دارد: وقتی چند پاسخ برای یک درخواست داریم و یکی را ترجیح می‌دهیم، این ترجیح چگونه به سیگنال آموزش تبدیل می‌شود؟ مسیرهای RLHF/PPO، DPO و GRPO پاسخ‌های متفاوتی‌اند؛ RLAIF نامی برای استفاده از بازخورد هوش مصنوعی است، نه یک الگوریتم واحد. فصل بعد به دادهٔ مصنوعی و تقطیر می‌پردازد؛ آن موضوع‌ها در اینجا آموزش داده نمی‌شوند.

**پیش‌نیاز:** احتمال و لگاریتم احتمال، مدل سیاست، گرادیان، SFT و مفهوم ارزیابی مستقل. **خروجی:** بتوانید دادهٔ chosen/rejected را با منشأ و split گروهی تعریف کنید؛ مدل Bradley–Terry و reward model را توضیح دهید؛ نقش PPO، DPO و GRPO را از هم جدا کنید؛ RLAIF را با Constitutional AI یکی نگیرید؛ و ارزیابی مستقل را از امتیاز reward model تفکیک کنید.

![شکل ۴-۳-۱ — چهار مسیر مفهومیِ استفاده از ترجیح: در RLHF مسیر SFT، مقایسهٔ پاسخ‌ها، reward model و بهینه‌سازی سیاست با PPO دیده می‌شود؛ در DPO جفت‌های ترجیحی و سیاست مرجع مستقیماً وارد loss می‌شوند؛ در GRPO چند پاسخ برای هر prompt با reward گروهی و advantage نسبی مقایسه می‌شوند؛ در RLAIF/Constitutional AI بازخورد هوش مصنوعی بر پایهٔ اصول وارد فرایند می‌شود. نمودار مسیرهای آموزشی را نشان می‌دهد، نه کیفیت، هم‌ترازی یا تضمین ایمنی.](book-engineering/diagrams/v4-ch03-preference.svg)

**شکل ۴-۳-۱ —** این خانواده‌ها بخش‌های مشترک و متفاوت دارند. منبع ترجیح، الگوریتم بهینه‌سازی، مدل پاداش و پروتکل ارزیابی را جداگانه نام ببرید؛ شباهت نمودارها به معنی برابری فرض‌ها یا نتایج نیست.

## ۱. ترجیح، پاداش و «هم‌ترازی» یک چیز نیستند

پس از SFT ممکن است چند پاسخ به یک prompt داشته باشیم و از یک ارزیاب بپرسیم کدام پاسخ را ترجیح می‌دهد. چنین برچسبی یک **مقایسه در زمینه و تحت معیار مشخص** است؛ لزوماً نشان نمی‌دهد پاسخ برگزیده حقیقت مطلق، پاسخ بی‌نقص یا بهترین پاسخ برای همهٔ کاربران است. حتی دو پاسخِ بد ممکن است یکی را بر دیگری ترجیح دهند.

در این فصل «ترجیح» را دادهٔ مقایسه‌ای، «پاداش» را یک عدد یا تابع امتیاز، و «سیاست» را توزیع احتمالی مدل روی توکن‌های بعدی می‌نامیم. **RLHF** معمولاً به فرایندی اشاره می‌کند که بازخورد انسانی را برای ساخت هدف یا مدل پاداش و سپس بهینه‌سازی سیاست به کار می‌گیرد. «هم‌ترازی» واژه‌ای گسترده‌تر است و به‌تنهایی نه الگوریتم خاصی را مشخص می‌کند، نه تضمین رفتار مطلوب می‌دهد. نتایج تجربی هر مقاله به مدل، داده، معیار، نمونه‌گیری و ارزیابی همان مطالعه محدود است [۱،۲].

## ۲. جفت ترجیحی دقیقاً چه چیزی ثبت می‌کند؟

برای prompt برابر `x`، دو completion را `y_A` و `y_B` بنامیم. یک رکورد معمول می‌تواند prompt، پاسخ ترجیح‌داده‌شده، پاسخ کم‌تر ترجیح‌داده‌شده، شناسهٔ گروه و منشأ برچسب را نگه دارد:

```json
{"prompt":"...", "chosen":"...", "rejected":"...", "group_id":"...", "label_source":"..."}
```

`chosen` و `rejected` نام فیلدهای قراردادی‌اند، نه داوری دربارهٔ درستی. ثبت معیار مقایسه—برای نمونه، سودمندی، درستی، اختصار یا رعایت سیاست—مهم است؛ دو annotator ممکن است با معیارهای متفاوت انتخاب‌های متفاوتی داشته باشند. در دادهٔ واقعی، شناسهٔ دور/نمونه، ترتیب نمایش گزینه‌ها، منبع پاسخ، نسخهٔ دستور ارزیابی، زبان، گروه، وضعیت tie/abstain و در صورت لزوم اطمینان یا توضیح ارزیاب را نیز نگه دارید.

اگر دو پاسخ هم‌ارزند یا داوری ممکن نیست، آن را بی‌صدا به chosen/rejected قطعی تبدیل نکنید. می‌توان tie را با طرح برچسب جدا، نمونه‌گیری دوباره یا روش آماریِ متناسب مدیریت کرد؛ انتخاب باید پیش از دیدن test ثبت شود. fixture فصل tie ندارد؛ بنابراین کد آن فقط قرارداد دوگزینه‌ای را می‌آزماید و دربارهٔ سیاست tie نتیجه‌ای نمی‌دهد.

## ۳. جمع‌آوری ترجیح، بخشی از تعریف آزمایش است

یک مقایسهٔ قابل تفسیر باید دو پاسخ را برای همان prompt و زمینه بسنجد. ترتیب نمایش را تصادفی یا متوازن کنید تا سوگیریِ گزینهٔ اول/دوم اندازه‌گیری شود؛ معیار و دستور را به annotator روشن بگویید؛ پاسخ‌های ناقص، refusal، tool-call و چند turn را مطابق کاربرد هدف نگه دارید؛ و نرخ tie، اختلاف ارزیاب و موارد نامعتبر را گزارش کنید. برچسب «انسانی» به‌تنهایی کیفیت، نمایندگی یا توافق را اثبات نمی‌کند.

منشأ را از محتوا جدا کنید: داوری انسانی، داوری یک مدل، rule programmatic و fixture ساختگی، چهار نوع evidence متفاوت‌اند. اگر AI judge به کار می‌رود، نام و revision مدل، system prompt، temperature، ترتیب گزینه‌ها و معیار داوری را ثبت کنید. داده‌های حساس و مکالمه‌های واقعی نیز به رضایت، کمینه‌سازی، کنترل دسترسی و قواعد نگه‌داری نیاز دارند؛ مدل‌کردن ترجیح این مسئولیت‌ها را حذف نمی‌کند.

تقسیم تصادفیِ ردیف‌ها می‌تواند prompt یکسان یا variantهای بسیار نزدیک را میان train و test پخش کند. group را بر پایهٔ واحد وابستگی واقعی—مانند prompt اصلی، سند، مکالمه، کاربر یا template—تعریف و split را در سطح آن انجام دهید. انتخاب این گروه‌بندی باید با هدف تعمیم هم‌خوان باشد؛ یک `group_id` صوری نشت را رفع نمی‌کند. در داده‌های چندمنبعی، سهم هر منبع و معیار را در هر split جدا گزارش کنید.

## ۴. مدل Bradley–Terry: تفاوت امتیاز، احتمال مقایسه

یک مدل متداول برای مقایسهٔ دوتایی می‌گوید احتمال ترجیح پاسخ `y_w` بر `y_l` در زمینهٔ `x` از اختلاف امتیاز آن‌ها به دست می‌آید:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="احتمال ترجیح پاسخ برنده بر پاسخ بازنده برابر تابع سیگموید اختلاف پاداش دو پاسخ در همان زمینه است">
  <mrow>
    <mi>P</mi><mo>(</mo><msub><mi>y</mi><mi>w</mi></msub><mo>≻</mo><msub><mi>y</mi><mi>l</mi></msub><mo>|</mo><mi>x</mi><mo>)</mo><mo>=</mo><mi>σ</mi><mo>(</mo><mi>r</mi><mo>(</mo><mi>x</mi><mo>,</mo><msub><mi>y</mi><mi>w</mi></msub><mo>)</mo><mo>−</mo><mi>r</mi><mo>(</mo><mi>x</mi><mo>,</mo><msub><mi>y</mi><mi>l</mi></msub><mo>)</mo><mo>)</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** احتمال ترجیح پاسخ برنده بر پاسخ بازنده برابر سیگمویدِ اختلاف پاداش دو پاسخ، با شرط بر همان زمینه، است. این صورت‌بندی به مدل Bradley–Terry و فرض‌های آن وابسته است [۱۱].

اگر اختلاف امتیاز صفر باشد، مدل احتمال `۰٫۵` می‌دهد؛ اگر مثبت باشد احتمال پیش‌بینی‌شده از `۰٫۵` بیشتر است. این احتمال، احتمال «واقعاً درست بودن» پاسخ نیست. مدل به روابط مقایسه‌ایِ داده‌شده fit می‌شود و با تغییر معیار، جمعیت داوری یا توزیع prompt ممکن است رفتار دیگری بیاموزد. فرض استقلال/سازگاری ترجیح‌ها نیز در دادهٔ واقعی می‌تواند نقض شود.

## ۵. Reward model از برچسب مقایسه‌ای چه می‌آموزد؟

یک **reward model** معمولاً تابعی پارامتری `r_φ(x,y)` می‌آموزد که به prompt و پاسخ یک scalar می‌دهد. برای هر جفتِ دارای برچسب، اختلاف `r_φ(x,y_w) − r_φ(x,y_l)` باید با جهت انتخاب سازگار باشد. زیان منفیِ log-likelihood برای Bradley–Terry به شکل زیر است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="زیان reward model برابر میانگین منفی لگاریتم سیگموید اختلاف پاداش پاسخ ترجیح داده شده و پاسخ کم تر ترجیح داده شده است">
  <mrow>
    <msub><mi>L</mi><mi>RM</mi></msub><mo>=</mo><mo>−</mo><msub><mi>𝔼</mi><mrow><mo>(</mo><mi>x</mi><mo>,</mo><msub><mi>y</mi><mi>w</mi></msub><mo>,</mo><msub><mi>y</mi><mi>l</mi></msub><mo>)</mo><mo>∼</mo><mi>D</mi></mrow></msub><mo>[</mo><mi>log</mi><mi>σ</mi><mo>(</mo><mi>r</mi><mo>(</mo><mi>x</mi><mo>,</mo><msub><mi>y</mi><mi>w</mi></msub><mo>)</mo><mo>−</mo><mi>r</mi><mo>(</mo><mi>x</mi><mo>,</mo><msub><mi>y</mi><mi>l</mi></msub><mo>)</mo><mo>)</mo><mo>]</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** زیان reward model برابر میانگین منفیِ لگاریتم سیگموید اختلاف پاداش پاسخ ترجیح‌داده‌شده و پاسخ کم‌تر ترجیح‌داده‌شده است؛ داده از توزیع مقایسه‌های ثبت‌شده می‌آید.

در همین prompt، افزودن یک ثابت مشترک به امتیاز هر دو پاسخ، اختلاف را عوض نمی‌کند؛ بنابراین scalar را نباید بدون کالیبراسیون بین promptهای مختلف، مقیاس مطلق رضایت یا احتمال درستی دانست. مدل می‌تواند به نشانه‌های سطحیِ هم‌بسته با برچسب—مثل طول، لحن یا عبارت‌های قالبی—تکیه کند. عملکرد روی validation تصادفی نیز تعمیم به پاسخ‌های تولیدشده توسط policy بعد از بهینه‌سازی را تضمین نمی‌کند؛ آن‌ها ممکن است خارج از توزیع دادهٔ RM باشند.

## ۶. مسیر کلاسیک RLHF: از SFT تا سیاست بهینه‌شده

یک خط لولهٔ متداول در پژوهش‌های RLHF چنین است: (۱) یک مدل SFT نقطهٔ شروع policy و معمولاً مرجع می‌شود؛ (۲) برای promptهای انتخاب‌شده چند پاسخ تولید می‌شود؛ (۳) انسان‌ها پاسخ‌ها را مقایسه می‌کنند؛ (۴) reward model روی این مقایسه‌ها fit می‌شود؛ (۵) policy با الگوریتم RL طوری به‌روزرسانی می‌شود که reward پیش‌بینی‌شده را بالا ببرد، درحالی‌که معمولاً انحراف از policy مرجع نیز جریمه می‌شود [۱،۲]. جزئیات واقعی مقاله‌ها و سامانه‌ها می‌تواند متفاوت باشد.

PPO یکی از الگوریتم‌های ممکن برای گام پنجم است؛ «RLHF» و «PPO» مترادف نیستند. در پیاده‌سازی متداول، محاسبه‌ها می‌توانند policy فعلی، policy قدیمی برای نسبت احتمال، reward model، value/critic و policy reference داشته باشند. این فهرست معماری ثابت برای هر روش نیست؛ پیاده‌سازی، اندازهٔ مدل و sharing وزن‌ها تغییر می‌کنند. شکل فصل مسیر مفهومی را ساده کرده است و نسبت حافظه یا تعداد مدل‌ها را نشان نمی‌دهد.

## ۷. PPO: به‌روزرسانی سیاست با نسبت احتمال محدودشده

در تولید autoregressive، state در گام `t` را می‌توان prompt به‌همراه prefix تولیدشده دانست و action را token بعدی. PPO نسبت احتمال action تولیدشده تحت policy تازه و policy قدیمی را می‌سازد. advantage تخمینی می‌گوید action، با توجه به baseline، بهتر یا بدتر از انتظار بوده است. این تخمین می‌تواند به reward نهایی پاسخ و برآورد value متکی باشد؛ جزئیات توزیع reward و estimator باید در سامانهٔ مورد استفاده مشخص شود.

فرم clipped surrogate از نسبت `r_t(θ)=π_θ(a_t|s_t)/π_{θ_old}(a_t|s_t)` استفاده می‌کند؛ `π_old` همان سیاستی است که rollout را تولید کرده است. این نسبت سهم همان action را به بازه‌ای پیرامون یک محدود می‌برد:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="تابع هدف کلیپ شده PPO امید ریاضی کمینهٔ حاصل ضرب نسبت احتمال در advantage و نسبت بریده شده در advantage است">
  <mrow>
    <msub><mi>L</mi><mi>clip</mi></msub><mo>(</mo><mi>θ</mi><mo>)</mo><mo>=</mo><msub><mi>𝔼</mi><mi>t</mi></msub><mo>[</mo><mi>min</mi><mo>(</mo><msub><mi>r</mi><mi>t</mi></msub><mo>(</mo><mi>θ</mi><mo>)</mo><msub><mover><mi>A</mi><mo>^</mo></mover><mi>t</mi></msub><mo>,</mo><mi>clip</mi><mo>(</mo><msub><mi>r</mi><mi>t</mi></msub><mo>(</mo><mi>θ</mi><mo>)</mo><mo>,</mo><mn>1</mn><mo>−</mo><mi>ε</mi><mo>,</mo><mn>1</mn><mo>+</mo><mi>ε</mi><mo>)</mo><msub><mover><mi>A</mi><mo>^</mo></mover><mi>t</mi></msub><mo>)</mo><mo>]</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** در surrogate کلیپ‌شدهٔ PPO، برای هر گام کمینهٔ دو حاصل‌ضرب سنجیده می‌شود: نسبت احتمال تازه در advantage، و همان نسبتِ محدودشده به بازهٔ یک منهای اپسیلون تا یک به‌علاوهٔ اپسیلون در advantage [۳].

این clip انگیزهٔ surrogate را برای تغییرهای بزرگ در همان objective کم می‌کند؛ **hard bound** بر همهٔ تغییرات توزیع policy، خروجی‌ها یا KL نیست و بهبود واقعی reward را تضمین نمی‌کند. PPO چند epoch روی rolloutهای جمع‌آوری‌شده نیز می‌تواند در معرض mismatch بین داده و policy تازه باشد؛ مقدار clip، batch، تعداد epoch، advantage، value loss و توقف/regularization همگی مهم‌اند. شکل سادهٔ مقالهٔ PPO را با objective کامل یک trainer خاص یکی نگیرید.

## ۸. KL به policy مرجع: مهار انحراف، نه بیمهٔ کیفیت

در بسیاری از setupهای RLHF، reward پیش‌بینی‌شده تنها هدف نیست. جریمه‌ای مبتنی بر فاصلهٔ policy تازه از policy مرجع—اغلب مدل SFT—به هدف افزوده می‌شود تا policy صرفاً برای بالا بردن امتیاز reward، بیش از حد تغییر نکند. «clip ratio» در PPO و «جریمهٔ KL نسبت به reference» دو ابزار متفاوت‌اند؛ ممکن است هر دو در یک روش باشند و هیچ‌یک دیگری را تعریف نمی‌کند.

اگر ضریب جریمه زیاد باشد policy می‌تواند نزدیک مرجع بماند و بخش کمی از ترجیح‌های جدید را بیاموزد؛ اگر کم باشد امکان drift و بهره‌برداری از خطای reward model بیشتر می‌شود. این توصیف جهت مصالحه است، نه قانون یک‌نواخت برای همهٔ taskها. KL کوچک نیز ایمنی یا درستی را تضمین نمی‌کند؛ مدل مرجع خود محدودیت دارد و reward model ممکن است با تغییر اندک هم خطا داشته باشد.

نمونه‌های reward hacking شامل تولید پاسخ‌های بی‌جهت طولانی، تکرار نشانه‌های پاداش، refusal بیش‌ازحد یا بهینه‌کردن الگوی judge به‌جای هدف کاربر است. پاسخ‌ها را با ارزیاب مستقل و متنوع بررسی کنید و reward، KL، طول و دسته‌های خطا را با هم گزارش دهید. امتیاز بالا روی همان reward model که policy برایش optimize شده، شاهد مستقلی برای کیفیت نیست.

## ۹. DPO: استفادهٔ مستقیم از جفت ترجیحی

**Direct Preference Optimization (DPO)** از یک نتیجهٔ پارامتردهی در مسئلهٔ بهینه‌سازی پاداشِ مقیدشده با KL استفاده می‌کند. در صورت‌بندی مقاله، برای یک reward مطلوب، policy بهینه با log-ratio آن نسبت به policy مرجع مرتبط می‌شود؛ با فرض یک مدل ترجیح pairwise مانند Bradley–Terry، می‌توان loss مقایسه را مستقیماً بر policy نوشت و reward model جداگانه را صریحاً fit نکرد [۴]. این استنتاج به objective و فرض‌های مقاله وابسته است؛ آن را قضیه‌ای دربارهٔ هر preference dataset ندانید.

DPO معمولاً روی جفت‌های prompt/chosen/rejected ثابت و offline به‌روزرسانی می‌شود. در این گام نیازی به rolloutهای تازه برای هر update یا یک reward model مستقل نیست؛ اما همچنان به سیاست مرجع، دادهٔ ترجیح، محاسبهٔ log-probability، آموزش policy و انتخاب داده/هایپرپارامتر نیاز دارد. «بدون reward model جداگانه» به معنی «بدون پیش‌فرض دربارهٔ ترجیح» یا «بدون مدل مرجع» نیست.

## ۱۰. Loss در DPO: اختلاف log-ratio، نه صرفاً cross-entropy معمولی

برای یک جفت، DPO اختلاف log-probability پاسخ‌های chosen و rejected را در policy فعلی و reference مقایسه می‌کند. فرم متداول loss چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="زیان DPO برابر منفی لگاریتم سیگموید بتا ضربدر اختلاف log probability پاسخ chosen و rejected پس از کم کردن همان log probability های policy مرجع است">
  <mrow>
    <msub><mi>L</mi><mi>DPO</mi></msub><mo>=</mo><mo>−</mo><msub><mi>𝔼</mi><mrow><mo>(</mo><mi>x</mi><mo>,</mo><msub><mi>y</mi><mi>w</mi></msub><mo>,</mo><msub><mi>y</mi><mi>l</mi></msub><mo>)</mo><mo>∼</mo><mi>D</mi></mrow></msub><mo>[</mo><mi>log</mi><mi>σ</mi><mo>(</mo><mi>β</mi><mo>(</mo><mo>(</mo><mi>log</mi><msub><mi>π</mi><mi>θ</mi></msub><mo>(</mo><msub><mi>y</mi><mi>w</mi></msub><mo>|</mo><mi>x</mi><mo>)</mo><mo>−</mo><mi>log</mi><msub><mi>π</mi><mi>ref</mi></msub><mo>(</mo><msub><mi>y</mi><mi>w</mi></msub><mo>|</mo><mi>x</mi><mo>)</mo><mo>)</mo><mo>−</mo><mo>(</mo><mi>log</mi><msub><mi>π</mi><mi>θ</mi></msub><mo>(</mo><msub><mi>y</mi><mi>l</mi></msub><mo>|</mo><mi>x</mi><mo>)</mo><mo>−</mo><mi>log</mi><msub><mi>π</mi><mi>ref</mi></msub><mo>(</mo><msub><mi>y</mi><mi>l</mi></msub><mo>|</mo><mi>x</mi><mo>)</mo><mo>)</mo><mo>)</mo><mo>)</mo><mo>]</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** زیان DPO برابر منفی لگاریتم سیگمویدِ بتا ضربدر این مقدار است: log-probability پاسخ chosen نسبت به reference، منهای log-probability پاسخ rejected نسبت به همان reference؛ سپس روی جفت‌ها میانگین گرفته می‌شود.

`β` شیب/مقیاس ترجیح در صورت‌بندی objective را کنترل می‌کند؛ رفتار دقیق آن همراه data, reference و نسخهٔ پیاده‌سازی باید آزموده شود. log-probability یک completion معمولاً مجموع log-probability توکن‌های آن است؛ طول پاسخ و tokenization می‌توانند بر مقدار و گرادیان اثر بگذارند. در مثال واقعی باید قرارداد prompt mask، EOS، truncation، chat template، reference، loss reduction و variantهای DPO را از مستندات نسخهٔ دقیق بررسی کنید [۴،۹].

DPO ممکن است preference train را خوب fit کند ولی روی promptهای تازه، معیارهای دیگر یا subgroupهای کم‌نمونه شکست بخورد. از loss کمتر به‌تنهایی نمی‌توان برتری مفید یا ایمن را نتیجه گرفت. مقایسهٔ pairwise روی held-out، اطمینان/توافق ارزیاب، نرخ tie و سنجه‌های رفتاری مستقل را جدا نگه دارید.

## ۱۱. PPO-RLHF، DPO و GRPO: سه جایگاه متفاوت

| روش/نام | ورودی کلیدی | حلقهٔ آموزش | چه چیزی حذف یا عوض می‌شود؟ | احتیاط اصلی |
|---|---|---|---|---|
| RLHF با PPO | جفت ترجیحی برای آموزش reward model؛ promptهای rollout | تولید پاسخ، امتیازدهی reward، advantage و به‌روزرسانی policy | PPO الگوریتم policy optimization در خط لوله است، نه نام کل خط لوله | reward model proxy است؛ rollout، KL و value/advantage باید ممیزی شوند. |
| DPO | جفت‌های prompt/chosen/rejected و policy مرجع | آموزش offline مستقیم روی log-probability پاسخ‌ها | reward model جداگانه و rolloutهای online لازم نیستند | فرض‌ها و پوشش داده پابرجا هستند؛ reference و طول پاسخ مهم‌اند. |
| GRPO | prompt، چند completion برای هر prompt و reward/group score | نمونه‌گیری گروهی و به‌روزرسانی online با advantage نسبی | در صورت‌بندی معرفی‌شده critic/value model جداگانه حذف می‌شود | generation، reward، reference و نرمال‌سازی گروهی باقی می‌مانند. |
| RLAIF | feedback یا preference تولیدشده/داوری‌شده با AI | می‌تواند به reward-model RL یا الگوریتم مستقیم preference وصل شود | منبع feedback عوض می‌شود؛ یک trainer واحد نیست | judge، معیار، دادهٔ انسانیِ اصول و ارزیابی مستقل را ثبت کنید. |

این جدول «کیفیت»، هزینه یا کارایی را رتبه‌بندی نمی‌کند. DPO هم model update دارد؛ GRPO هم rollout و reward دارد؛ PPO را می‌توان با انواع reward به کار برد. در یک پروژه ممکن است چند روش در مرحله‌های متفاوت استفاده شوند، پس نام مرحله و نسخه را ثبت کنید.

## ۱۲. GRPO: مقایسهٔ چند پاسخ درون گروه prompt

**Group Relative Policy Optimization (GRPO)** در DeepSeekMath به‌عنوان گونه‌ای از PPO معرفی شد: برای یک prompt چند completion از policy تولید می‌شود، هرکدام reward می‌گیرد و advantage با مقایسهٔ پاسخ‌ها در همان گروه ساخته می‌شود. نسخهٔ معرفی‌شده critic جداگانه را حذف می‌کند و از score/advantage گروهی برای به‌روزرسانی policy استفاده می‌کند [۵]. این حذف به معنی حذف reward، rollout یا policy reference نیست.

یک نمایش سادهٔ advantage نرمال‌شده برای پاسخ `i` در گروه prompt برابر `q` چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="advantage نسبی پاسخ i در گروه q برابر پاداش پاسخ منهای میانگین پاداش‌های همان گروه تقسیم بر انحراف معیار همان گروه به‌علاوه اپسیلون است">
  <mrow>
    <msub><mover><mi>A</mi><mo>^</mo></mover><mrow><mi>q</mi><mo>,</mo><mi>i</mi></mrow></msub><mo>=</mo><mfrac><mrow><msub><mi>r</mi><mrow><mi>q</mi><mo>,</mo><mi>i</mi></mrow></msub><mo>−</mo><mi>mean</mi><mo>(</mo><msub><mi>r</mi><mi>q</mi></msub><mo>)</mo></mrow><mrow><mi>std</mi><mo>(</mo><msub><mi>r</mi><mi>q</mi></msub><mo>)</mo><mo>+</mo><mi>ε</mi></mrow></mfrac>
  </mrow>
</math>

**متن جایگزین فرمول:** advantage نسبی هر پاسخ برابر reward آن منهای میانگین rewardهای همان گروه، تقسیم بر انحراف معیار گروه به‌علاوهٔ اپسیلون است. این فرمول شماتیک است؛ estimator و objective دقیق را از پیاده‌سازی/مقالهٔ مورد استفاده بگیرید.

اگر همهٔ پاسخ‌های یک گروه reward برابر بگیرند، reward نسبی سیگنال رتبه‌بندی درون آن گروه ندارد؛ اگر reward ناقص یا قابل‌بازی‌دادن باشد، نرمال‌سازی خطا را برطرف نمی‌کند. objective کامل GRPO می‌تواند نسبت احتمال clipped و KL نسبت به reference داشته باشد و روی tokenها/گروه‌ها تجمیع شود. پیاده‌سازی‌ها در estimator، چند reward، طول، ماسک و ترتیب جمع‌زدن تفاوت دارند؛ شکل آموزشی بالا را به کد production جایگزین نکنید.

## ۱۳. Reward از کجا می‌آید؟ مدل آموخته‌شده یا verifier؟

**Learned reward model** از مقایسه‌های انسانی یا AI امتیاز می‌آموزد. **Rule-based / verifiable reward** یک شرط قابل‌محاسبه را بررسی می‌کند—برای نمونه، برابری پاسخ با جواب مرجع، معتبر بودن قالب یا موفقیت یک تست کد. rule برای آن شرطِ قابل‌مشاهده می‌تواند دقیق باشد، اما سنجه‌های دیگر مانند توضیح درست، کیفیت نگارش یا استفاده‌پذیری را پوشش نمی‌دهد. در بسیاری از مسئله‌ها rewardها ترکیبی‌اند و وزن هر مولفه یک انتخاب هنجاری و عملیاتی است.

هر reward را همراه تعریف، واحد، دامنه، نسخه و رفتار روی ورودی نامعتبر ثبت کنید. چند reward قابل‌جمع‌زدن نیستند مگر وزن و واحدشان معنی‌دار باشد؛ rewardهای نادرست یا ناهم‌مقیاس می‌توانند گرادیان را به جهت ناخواسته ببرند. تست‌های adversarial و نمونه‌های مرزی را پیش از optimize طراحی کنید. نمرهٔ بالا روی verifier تنها می‌گوید مدل شرط برنامه‌نویسی‌شده را پاس کرده است، نه اینکه تمام نیاز کاربر برآورده شده باشد.

## ۱۴. RLAIF: منبع بازخورد AI، نه مترادف DPO یا PPO

**Reinforcement Learning from AI Feedback (RLAIF)** بازخورد مدل یا سامانهٔ هوش مصنوعی را در مرحله‌ای از ساخت preference/reward یا policy به کار می‌گیرد. در RLAIF مبتنی بر reward model، AI می‌تواند پاسخ‌ها را بر اساس معیار رتبه‌بندی کند؛ دادهٔ حاصل reward model را آموزش می‌دهد و سپس یک روش RL آن را optimize می‌کند. در direct-RLAIF، preferenceهای AI می‌توانند مستقیماً وارد روش‌های آموزش جفتی شوند. باید مشخص کنید منظور کدام مسیر است؛ «RLAIF» به‌تنهایی الگوریتم و loss را تعیین نمی‌کند [۷].

مطالعهٔ Lee و همکاران RLAIF و RLHF را در وظایف summarization و دو task گفت‌وگو، با setup و evaluatorهای همان مطالعه مقایسه کرد [۷]. نتیجهٔ یکسان یا تعمیم به همهٔ زبان‌ها، مدل‌ها، خطرها و کاربردهای صنعتی از آن مطالعه به دست نمی‌آید. AI judge هم ممکن است پاسخ طولانی‌تر، لحن خاص، refusal یا محتوای نزدیک به خود را بیش از حد ترجیح دهد؛ بنابراین تنوع ارزیاب و ممیزی انسانی مستقل لازم است.

## ۱۵. Constitutional AI: یک روش مشخص در خانوادهٔ بزرگ‌تر

در مقالهٔ **Constitutional AI**، اصول نوشته‌شده به زبان طبیعی برای critique/revision و ساخت پاسخ‌های ترجیحی به‌کار می‌روند؛ فرایند مقاله مرحلهٔ نظارت‌شده و سپس آموزش از preferenceهای AI را توصیف می‌کند [۶]. طرح کلی شامل تولید پاسخ، نقد/بازنویسی با اشاره به اصل، آموزش روی دادهٔ بازبینی‌شده و سپس preference model/RL در مرحلهٔ دوم است. جزئیات و انتخاب‌های نسخهٔ مقاله را باید از منبع اصلی خواند؛ این نمودار خلاصهٔ کل روش‌های مبتنی بر اصل نیست.

«بدون بازخورد انسانی» توصیف دقیقی نیست: اصول را انسان انتخاب/می‌نویسد، معیارهای کمک‌مندی و فرایند ارزیابی طراحی می‌شوند و نظارت انسانی همچنان می‌تواند لازم باشد. Constitution یک فهرست معیار است، نه تضمین حقوقی یا اثبات پوشش همهٔ فرهنگ‌ها/خطرها. Constitutional AI نیز مترادف کل RLAIF نیست؛ نمونه‌ای مشخص است که از اصول و بازخورد AI در فرایند خود استفاده می‌کند.

## ۱۶. خطاهای preference و judge را پیش از آموزش جست‌وجو کنید

منبع انسانی ممکن است اختلاف، خستگی، دانش ناکافی یا تفاوت معیار داشته باشد؛ AI judge ممکن است position bias، طول‌گرایی، خودترجیحی، حساسیت به لحن یا vulnerability به prompt injection داشته باشد. پاسخ‌های refusals یا ایمن‌سازی می‌توانند به‌طور نامتناسب برچسب بگیرند؛ در صورت استفاده از reward model، policy می‌تواند به نشانه‌های قابل‌تشخیص reward بچسبد. میانگین accuracy روی validation نمی‌گوید کدام subgroup یا نوع درخواست شکست می‌خورد.

پروتکل کاهش خطر می‌تواند شامل نمایش کور/تصادفی گزینه‌ها، تکرار داوری روی بخشی از داده، ثبت tie و دلیل، ارزیاب‌های متنوع، تحلیل اختلاف، holdout مستقل از همان promptها، آزمون adversarial و بازبینی انسان روی نمونه‌های پرخطر باشد. عدم توافق را همیشه «نویز قابل حذف» ندانید؛ گاهی نشان می‌دهد معیار مبهم یا جمعیت ترجیح ناهمگن است. حذف برچسب مخالف بدون سیاست ازپیش‌تعریف‌شده می‌تواند یک دیدگاه را پنهان کند.

## ۱۷. ارزیابی مستقل: reward train خود داور نهایی نیست

ارزیابی نهایی را از reward model و دادهٔ preference آموزش جدا نگه دارید. می‌توان promptهای held-out را با پاسخ‌های مدل‌های مورد مقایسه به ارزیاب انسانیِ ناآگاه از هویت مدل داد، ترتیب پاسخ را تصادفی کرد، tie/abstain ثبت کرد و نرخ ترجیح را همراه بازهٔ عدم‌قطعیت گزارش داد. اگر همان مدل قضاوت‌گر استفاده می‌شود، version، prompt و محدودیت‌های آن را مشخص و روی subset انسانی کالیبره/بازبینی کنید.

برای هر ادعا، جمعیت، زبان، قالب، دامنهٔ prompt، روش نمونه‌گیری، تعداد داوری، معیار و زمان آزمون را روشن کنید. علاوه بر win-rate، correctness یا task success در صورت تعریف‌پذیری، calibration، refusal، hallucination، طول، robustness و subgroupها را جدا بسنجید. پاسخ‌های نادرست اما خوش‌بیان نباید با preference کلی پنهان شوند. RewardBench مجموعه‌ای از مقایسه‌های برگزیده/ردشده در chat، reasoning و safety برای ارزیابی reward modelها ارائه می‌کند؛ استفاده از آن جایگزین آزمون دامنهٔ خودتان یا معیار انسانی نیست [۸].

## ۱۸. نسخهٔ کتابخانه و معنای مثال کد

در تاریخ بازبینی، مستندات stableِ TRL نسخهٔ **v1.17.1**، `DPOTrainer`، `RewardTrainer` و `GRPOTrainer` را در دسته‌های offline/online/reward modeling فهرست می‌کنند؛ `PPOTrainer` در taxonomy همان نسخه نیست [۹]. یادداشت انتشار TRL v1.13.0 حذف `PPOTrainer` و `PPOConfig` را ثبت کرده است [۱۰]. مثال‌های قدیمی‌تر ممکن است به API نسخه‌های قدیمی نیاز داشته باشند؛ شمارهٔ نسخهٔ trainer را پیش از اجرای کد pin کنید و API جاری را از یک snippet بی‌تاریخ حدس نزنید.

کد پروژهٔ این فصل API از TRL یا وزن pretrained را اجرا نمی‌کند. تابع‌ها loss Bradley–Terry، DPO، clipping PPO و نرمال‌سازی advantage گروهی را روی tensorهای کوچک می‌آزمایند؛ demo فقط یک سیاست دسته‌ای دوگزینه‌ای مصنوعی را با DPO به‌روزرسانی می‌کند. این انتخاب برای بررسی قرارداد ریاضی است، نه نسخهٔ اجرایی fine-tuning یک مدل زبانی. هیچ عدد خروجی این پروژه را به GPU، فارسی، مدل واقعی، RLHF کامل یا ایمنی تعمیم ندهید.

## ۱۹. آزمایشگاه CPU فصل: قرارداد داده و چهار تابع کوچک

پروژه در `book-engineering/projects/49-preference-lab/` قرار دارد و از PyTorch 2.6.0+cpu مطابق `requirements.txt` مخزن استفاده می‌کند. fixture شامل ۱۲ جفت ساختگی در ۶ گروه prompt است؛ هر ردیف منشأ `synthetic_fixture` دارد. audit فقط JSONL را اعتبارسنجی و گروه‌ها را به train/validation/test تقسیم می‌کند؛ هیچ trainer یا مدلی بارگذاری نمی‌شود.

```bash
cd book-engineering/projects/49-preference-lab
python -m unittest discover -v
python preference_lab.py --mode audit --fixture sample_preferences.jsonl --output /tmp/ch49-audit
python preference_lab.py --mode toy-dpo --output /tmp/ch49-demo --steps 80 --seed 49
```

در اجرای ثبت‌شده، audit برابر ۱۲ ردیف/۶ گروه گزارش کرد؛ split بر پایهٔ group برابر ۸ ردیف/۴ گروه برای train، ۲/۱ برای validation و ۲/۱ برای test شد. این شمارش فقط رفتار splitter روی همین fixture است و نمایندگی آماری را اثبات نمی‌کند. اجرای مصنوعیِ CPU/float32 با seed=49 و ۸۰ گام، زیان DPO را از `0.6931471824645996` به `0.12939360737800598` رساند و احتمال انتخاب گزینهٔ ترجیحی در سیاست دسته‌ای را از `0.5` به `0.9999496936798096` تغییر داد؛ هیچ مدل زبانی بارگیری نشد. تمام ۲۲ آزمون unit پاس شدند. این‌ها تست پیاده‌سازی و fixture‌اند، نه شواهد کیفیت ترجیح انسانی، زبان فارسی، reward واقعی، RLHF کامل، GPU/NCCL، benchmark یا هم‌ترازی.

## ۲۰. تمرین‌ها: از فرمول تا پروتکل

۱. اگر مدل Bradley–Terry برای دو پاسخ یک prompt امتیازهای `r_w=1.2` و `r_l=0.3` بدهد، احتمال ترجیح مدل‌شده را حساب کنید. آیا این مقدار احتمال درست بودن پاسخ است؟

۲. برای مسئله‌ای که پاسخ‌ها بعد از هر update باید تازه تولید شوند، RLHF با PPO و DPO آفلاین چه تفاوتی در داده و اجزای آموزش دارند؟ دست‌کم دو جزء/هزینهٔ باقی‌مانده را برای هر مسیر نام ببرید.

۳. اگر ضریب KL را زیاد یا کم کنید، چه مصالحه‌هایی ممکن است رخ دهد؟ چرا clip در PPO را نباید همان جریمهٔ KL یا hard bound بر policy دانست؟

۴. در یک گروه GRPO، rewardها `[0, 1, 2]` هستند. با انحراف معیار جمعیتی، advantage نرمال‌شدهٔ هر پاسخ را بدون `ε` حساب کنید. اگر هر سه reward برابر شوند چه می‌شود؟

۵. آیا RLAIF یعنی «هیچ انسانی در حلقه نیست»؟ تفاوت آن را با Constitutional AI در دو جمله توضیح دهید.

۶. یک ارزیابی مستقل برای مقایسهٔ دو policy طراحی کنید: واحد نمونه‌گیری، کورسازی/ترتیب گزینه‌ها، tie، بازهٔ عدم‌قطعیت، subgroup و دست‌کم یک معیار غیر از ترجیح کلی را تعریف کنید.

**پاسخ‌نامهٔ مستقل:** [پاسخ‌نامهٔ تشریحی فصل ۴۹](book-engineering/answers/49-preference-optimization-fa.md). **پروژه:** [README و دستورهای اجرا](book-engineering/projects/49-preference-lab/README.md)؛ **گزارش اجرا و محدودیت:** [گزارش ممیزی فصل ۴۹](book-engineering/chapters/49-audit-report-fa.md).

## ۲۱. جمع‌بندی: زنجیره را به اجزایش بشکنید

دادهٔ chosen/rejected ترجیح وابسته به معیار را ثبت می‌کند؛ Bradley–Terry یک مدل احتمالی رایج برای این ترجیح است؛ reward model اختلاف پاسخ‌ها را با scalar می‌آموزد. RLHF یک خط لولهٔ آموزش از بازخورد است و PPO یکی از راه‌های بهینه‌سازی policy در آن است؛ DPO loss جفتی را با reference مستقیماً روی policy می‌آموزد؛ GRPO advantage را درون گروه پاسخ‌های یک prompt می‌سازد و در صورت‌بندی معرفی‌شده critic را کنار می‌گذارد. RLAIF بازخورد AI را توصیف می‌کند و Constitutional AI یک فرایند مبتنی بر اصول در همین پهنه است.

هیچ روش یا reward یک‌تنهٔ کیفیت، درستی، انصاف، ایمنی یا رعایت حقوق را اثبات نمی‌کند. منشأ برچسب، فرض‌های مدل ترجیح، split، نسخهٔ نرم‌افزار، معیار مستقل و محدودهٔ شواهد باید همراه نتیجه بیایند. فصل بعد سراغ دادهٔ مصنوعی و تقطیر می‌رود؛ تولید دادهٔ بیشتر تنها وقتی مفید است که کیفیت و منشأ آن جدا ممیزی شوند.

## ۲۲. منابع و تاریخ بازبینی

منابع در **۶ نوامبر ۲۰۲۶** بازبینی شدند. نتیجه‌های مقاله‌ها به setup و ارزیابی گزارش‌شده در همان منابع محدودند؛ APIهای نرم‌افزار به نسخه وابسته‌اند.

۱. Ziegler, D. M. و همکاران، “Fine-Tuning Language Models from Human Preferences”، ۲۰۱۹، arXiv:1909.08593. <https://arxiv.org/abs/1909.08593>
۲. Ouyang, L. و همکاران، “Training language models to follow instructions with human feedback”، ۲۰۲۲، arXiv:2203.02155. <https://arxiv.org/abs/2203.02155>
۳. Schulman, J. و همکاران، “Proximal Policy Optimization Algorithms”، ۲۰۱۷، arXiv:1707.06347. <https://arxiv.org/abs/1707.06347>
۴. Rafailov, R. و همکاران، “Direct Preference Optimization: Your Language Model is Secretly a Reward Model”، NeurIPS 2023، arXiv:2305.18290. <https://arxiv.org/abs/2305.18290>
۵. Shao, Z. و همکاران، “DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models”، ۲۰۲۴، arXiv:2402.03300. <https://arxiv.org/abs/2402.03300>
۶. Bai, Y. و همکاران، “Constitutional AI: Harmlessness from AI Feedback”، ۲۰۲۲، arXiv:2212.08073. <https://arxiv.org/abs/2212.08073>
۷. Lee, H. و همکاران، “RLAIF vs. RLHF: Scaling Reinforcement Learning from Human Feedback with AI Feedback”، ICML 2024، PMLR 235، arXiv:2309.00267، نسخهٔ v3 مورخ ۳ سپتامبر ۲۰۲۴. <https://arxiv.org/abs/2309.00267>؛ <https://proceedings.mlr.press/v235/lee24t.html>
۸. Lambert, N. و همکاران، “RewardBench: Evaluating Reward Models for Language Modeling”، ۲۰۲۴، arXiv:2403.13787. <https://arxiv.org/abs/2403.13787>
۹. مستندات رسمی TRL v1.17.1، taxonomy، DPOTrainer، RewardTrainer و GRPOTrainer. <https://huggingface.co/docs/trl/v1.17.1/en/index>؛ <https://huggingface.co/docs/trl/v1.17.1/en/dpo_trainer>؛ <https://huggingface.co/docs/trl/v1.17.1/en/reward_trainer>؛ <https://huggingface.co/docs/trl/v1.17.1/en/grpo_trainer>
۱۰. Hugging Face TRL، یادداشت انتشار v1.13.0، حذف PPOTrainer و PPOConfig. <https://github.com/huggingface/trl/releases/tag/v1.13.0>
۱۱. Bradley, R. A. و Terry, M. E.، “Rank Analysis of Incomplete Block Designs: I. The Method of Paired Comparisons”، Biometrika، ۱۹۵۲، ۳۹(۳–۴)، ۳۲۴–۳۴۵، DOI: 10.1093/biomet/39.3-4.324. <https://doi.org/10.1093/biomet/39.3-4.324>

## ۲۳. پیوست اجرایی: فایل آزموده‌شدهٔ پروژه

بلوک زیر نسخهٔ کامل `book-engineering/projects/49-preference-lab/preference_lab.py` است و باید بایت‌به‌بایت با همان فایل آزموده‌شده بماند. کد به‌جای مدل زبانی، fixture و tensorهای کوچک را بررسی می‌کند؛ توضیح خروجی و مرز ادعا در README و گزارش ممیزی ثبت شده است.

```python
"""CPU-only lab for pairwise reward, DPO, PPO clipping and GRPO advantages.

All inputs are synthetic, tiny and categorical. This module does not load an
LLM, collect human/AI feedback, run RLHF, or measure product alignment.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Sequence

import torch
from torch import nn
from torch.nn import functional as F

SPLIT_NAMES = ("train", "validation", "test")
ALLOWED_LABEL_SOURCES = {"human", "ai", "rule", "synthetic_fixture"}
REQUIRED_FIELDS = ("id", "group_id", "prompt", "chosen", "rejected", "label_source")


def validate_preferences(rows: Any) -> list[dict[str, str]]:
    """Validate explicit prompt/chosen/rejected records; ties are not implicit."""
    if not isinstance(rows, list) or not rows:
        raise ValueError("fixture must be a non-empty JSON list")
    seen: set[str] = set()
    clean: list[dict[str, str]] = []
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f"row {index} must be an object")
        missing = [field for field in REQUIRED_FIELDS if field not in row]
        if missing:
            raise ValueError(f"row {index} is missing fields: {', '.join(missing)}")
        values: dict[str, str] = {}
        for field in REQUIRED_FIELDS:
            value = row[field]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"row {index}: {field} must be a non-empty string")
            values[field] = value.strip()
        if values["id"] in seen:
            raise ValueError(f"row {index}: duplicate id {values['id']!r}")
        seen.add(values["id"])
        if values["chosen"] == values["rejected"]:
            raise ValueError(f"row {index}: chosen and rejected must differ")
        if values["label_source"] not in ALLOWED_LABEL_SOURCES:
            raise ValueError(f"row {index}: unsupported label_source")
        clean.append(values)
    return clean


def split_by_group(
    records: Sequence[dict[str, str]],
    *,
    seed: int = 49,
    train_fraction: float = 0.67,
    validation_fraction: float = 0.17,
) -> dict[str, list[dict[str, str]]]:
    """Assign whole prompt groups to deterministic, non-overlapping splits."""
    if type(seed) is not int or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    if not math.isfinite(train_fraction) or not math.isfinite(validation_fraction):
        raise ValueError("split fractions must be finite")
    if not 0.0 < train_fraction < 1.0 or not 0.0 < validation_fraction < 1.0:
        raise ValueError("split fractions must be between zero and one")
    if train_fraction + validation_fraction >= 1.0:
        raise ValueError("train_fraction + validation_fraction must be less than one")
    if not records:
        raise ValueError("records must not be empty")
    groups = sorted({row["group_id"] for row in records})
    if len(groups) < 3:
        raise ValueError("at least three independent group_id values are required")
    ordered = sorted(groups, key=lambda group: (hashlib.sha256(f"{seed}\0{group}".encode("utf-8")).hexdigest(), group))
    train_count = min(max(1, round(len(ordered) * train_fraction)), len(ordered) - 2)
    validation_count = min(max(1, round(len(ordered) * validation_fraction)), len(ordered) - train_count - 1)
    train_groups = set(ordered[:train_count])
    validation_groups = set(ordered[train_count:train_count + validation_count])
    test_groups = set(ordered[train_count + validation_count:])
    group_to_split = {
        **{group: "train" for group in train_groups},
        **{group: "validation" for group in validation_groups},
        **{group: "test" for group in test_groups},
    }
    result: dict[str, list[dict[str, str]]] = {name: [] for name in SPLIT_NAMES}
    for row in records:
        result[group_to_split[row["group_id"]]].append(row)
    if any(not result[name] for name in SPLIT_NAMES):
        raise ValueError("each split must contain at least one record")
    return result


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on line {line_number}: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"line {line_number} must contain a JSON object")
        rows.append(row)
    return rows


def audit_fixture(path: Path) -> dict[str, Any]:
    """Check only the synthetic dataset contract; do not train or infer."""
    raw = path.read_bytes()
    records = validate_preferences(_read_jsonl(path))
    splits = split_by_group(records)
    split_counts = {
        name: {
            "records": len(part),
            "groups": len({row["group_id"] for row in part}),
        }
        for name, part in splits.items()
    }
    return {
        "schema_version": 1,
        "status": "validated_only",
        "training_performed": False,
        "model_loaded": False,
        "model_downloaded": False,
        "fixture": path.name,
        "fixture_kind": "synthetic prompt and pairwise choice records; not human or model feedback",
        "records": len(records),
        "group_count": len({row["group_id"] for row in records}),
        "label_source_counts": dict(sorted(Counter(row["label_source"] for row in records).items())),
        "split_counts": split_counts,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "claim_boundary": "does not validate preference correctness, annotator agreement, language quality, safety, rights, privacy, or a trained model",
    }


def _finite_vector(value: torch.Tensor, name: str) -> torch.Tensor:
    if not torch.is_tensor(value):
        raise TypeError(f"{name} must be a torch.Tensor")
    if value.ndim != 1 or value.numel() == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional tensor")
    if not value.is_floating_point() or not bool(torch.isfinite(value).all()):
        raise ValueError(f"{name} must contain finite floating-point values")
    return value


def _same_shape(*named_tensors: tuple[str, torch.Tensor]) -> list[torch.Tensor]:
    values = [_finite_vector(value, name) for name, value in named_tensors]
    if any(value.shape != values[0].shape for value in values[1:]):
        raise ValueError("all input tensors must have the same shape")
    return values


def pairwise_reward_loss(chosen_scores: torch.Tensor, rejected_scores: torch.Tensor) -> torch.Tensor:
    """Bradley-Terry negative log-likelihood for scalar response scores."""
    chosen, rejected = _same_shape(("chosen_scores", chosen_scores), ("rejected_scores", rejected_scores))
    return F.softplus(rejected - chosen).mean()


def dpo_loss(
    policy_chosen_logps: torch.Tensor,
    policy_rejected_logps: torch.Tensor,
    reference_chosen_logps: torch.Tensor,
    reference_rejected_logps: torch.Tensor,
    beta: float,
) -> torch.Tensor:
    """DPO pairwise loss for already-summed sequence log-probabilities."""
    if isinstance(beta, bool) or not isinstance(beta, (int, float)) or not math.isfinite(beta) or beta <= 0:
        raise ValueError("beta must be finite and positive")
    chosen_pi, rejected_pi, chosen_ref, rejected_ref = _same_shape(
        ("policy_chosen_logps", policy_chosen_logps),
        ("policy_rejected_logps", policy_rejected_logps),
        ("reference_chosen_logps", reference_chosen_logps),
        ("reference_rejected_logps", reference_rejected_logps),
    )
    preference_margin = (chosen_pi - chosen_ref) - (rejected_pi - rejected_ref)
    return -F.logsigmoid(float(beta) * preference_margin).mean()


def grpo_group_advantages(
    rewards: torch.Tensor,
    group_ids: Sequence[str],
    *,
    eps: float = 1e-8,
) -> torch.Tensor:
    """Normalize rewards within each prompt group; constant groups map to zero."""
    rewards = _finite_vector(rewards, "rewards")
    if len(group_ids) != rewards.numel():
        raise ValueError("group_ids length must match rewards")
    if not math.isfinite(eps) or eps <= 0:
        raise ValueError("eps must be finite and positive")
    if any(not isinstance(group, str) or not group.strip() for group in group_ids):
        raise ValueError("each group id must be a non-empty string")
    result = torch.zeros_like(rewards)
    for group in dict.fromkeys(group_ids):
        indices = [index for index, group_id in enumerate(group_ids) if group_id == group]
        values = rewards[indices]
        scale = values.std(unbiased=False)
        if len(indices) < 2 or float(scale) <= eps:
            result[indices] = 0.0
        else:
            result[indices] = (values - values.mean()) / (scale + eps)
    return result


def ppo_clipped_policy_loss(
    new_logps: torch.Tensor,
    old_logps: torch.Tensor,
    advantages: torch.Tensor,
    *,
    clip_range: float = 0.2,
) -> torch.Tensor:
    """Negative clipped PPO surrogate (an optimizer-ready scalar loss)."""
    if not math.isfinite(clip_range) or not 0.0 < clip_range < 1.0:
        raise ValueError("clip_range must be finite and between zero and one")
    new, old, adv = _same_shape(
        ("new_logps", new_logps),
        ("old_logps", old_logps),
        ("advantages", advantages),
    )
    ratio = torch.exp(new - old)
    clipped_ratio = ratio.clamp(1.0 - clip_range, 1.0 + clip_range)
    surrogate = torch.minimum(ratio * adv, clipped_ratio * adv)
    return -surrogate.mean()


def run_toy_dpo(steps: int = 100, seed: int = 49) -> dict[str, Any]:
    """Optimize a two-choice categorical policy on one generated preference."""
    if type(steps) is not int or steps <= 0:
        raise ValueError("steps must be a positive integer")
    if type(seed) is not int or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    reference_logits = torch.tensor([0.0, 0.0], dtype=torch.float32)
    policy_logits = nn.Parameter(reference_logits.clone())
    reference_logps = F.log_softmax(reference_logits, dim=-1)
    optimizer = torch.optim.Adam((policy_logits,), lr=0.08)
    beta = 0.2

    def loss_now() -> torch.Tensor:
        policy_logps = F.log_softmax(policy_logits, dim=-1)
        return dpo_loss(
            policy_logps[0:1], policy_logps[1:2],
            reference_logps[0:1], reference_logps[1:2], beta,
        )

    initial_loss = float(loss_now().item())
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)
        loss = loss_now()
        loss.backward()
        optimizer.step()
    final_loss = float(loss_now().item())
    final_probabilities = F.softmax(policy_logits.detach(), dim=-1)
    return {
        "schema_version": 1,
        "status": "synthetic_demo_completed",
        "training_performed": True,
        "model_loaded": False,
        "model_downloaded": False,
        "fixture_kind": "generated two-action categorical policy; not a language model",
        "seed": seed,
        "steps": steps,
        "device": "cpu",
        "dtype": "float32",
        "beta": beta,
        "initial_dpo_loss": initial_loss,
        "final_dpo_loss": final_loss,
        "reference_chosen_probability": float(F.softmax(reference_logits, dim=-1)[0].item()),
        "policy_chosen_probability": float(final_probabilities[0].item()),
        "policy_rejected_probability": float(final_probabilities[1].item()),
        "claim_boundary": "implementation smoke test only; not human preference, language quality, safety, RLHF, or model-alignment evidence",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline preference, DPO, PPO and GRPO algebra lab")
    parser.add_argument("--mode", choices=("audit", "toy-dpo"), required=True)
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="directory for run.json")
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--seed", type=int, default=49)
    args = parser.parse_args()
    if args.mode == "audit":
        if args.fixture is None:
            parser.error("--fixture is required for --mode audit")
        result = audit_fixture(args.fixture)
    else:
        result = run_toy_dpo(steps=args.steps, seed=args.seed)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "run.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

---

# جلد چهارم، فصل ۴ — دادهٔ مصنوعی، تقطیر و محاسبهٔ زمان آزمون

**نگاشت:** فصل محلی ۴ جلد چهارم = فصل سراسری ۵۰. **تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶.** فصل ۴۷ آموزش نظارتی و SFT را معرفی کرد؛ فصل ۴۸ تغییر کم‌پارامتر را بررسی کرد؛ فصل ۴۹ ترجیح و روش‌های پس‌آموزش مبتنی بر بازخورد را از هم جدا کرد. اکنون می‌پرسیم: دادهٔ مصنوعی را چگونه می‌سازیم و ممیزی می‌کنیم؟ چه چیزی از معلم به دانش‌آموز منتقل می‌شود؟ آیا ترتیب آموزش و محاسبهٔ بیشتر هنگام پاسخ‌گویی کمک می‌کند؟ این‌ها روش‌های قابل‌آزمایش‌اند، نه تضمین کیفیت.

**پیش‌نیاز:** تقسیم داده و SFT از فصل ۴۷، مدل و پارامتر از فصل‌های ۴۱–۴۴، و مفاهیم ترجیح/RLHF از فصل ۴۹. **خروجی:** بتوانید مسیر منشأ یک نمونهٔ مصنوعی را ثبت کنید؛ split را بر اساس گروه وابستگی انجام دهید؛ تفاوت distillation پاسخ، توزیع و trace را توضیح دهید؛ curriculum را با baseline منصفانه بسنجید؛ و کیفیت، زمان، هزینه و عدم‌قطعیت محاسبهٔ زمان آزمون را کنار هم گزارش کنید.

![شکل ۴-۴-۱ — چرخهٔ دادهٔ مصنوعی، ممیزی، تقطیر و محاسبهٔ زمان آزمون. دادهٔ تولیدشده پیش از استفاده از دروازه‌های راستی‌آزمایی و ثبت منشأ می‌گذرد؛ تقطیر از teacher به student یک انتخاب آموزشی است؛ curriculum فرضیه‌ای دربارهٔ ترتیب نمونه‌هاست؛ و چند پاسخ هنگام استنتاج به هزینه نیاز دارد و تضمین درستی نیست.](book-engineering/diagrams/v4-ch04-synthetic-reasoning.svg)

**شکل ۴-۴-۱ —** نمودار جریان مفهومی را نشان می‌دهد، نه سامانهٔ اجرایی یا ادعای کیفیت. هر مسیر باید با منبع داده، کنترل مستقل و بودجهٔ محاسبه سنجیده شود.

## ۱. یک مدل کوچک‌تر، دادهٔ بیشتر، یا فکرکردن بیشتر؟

سه تصمیم را از هم جدا کنید. **دادهٔ مصنوعی** نمونه‌هایی می‌سازد که ممکن است برای آموزش یا ارزیابی به کار روند. **تقطیر دانش (Knowledge Distillation)** تابع یا هدفی از یک teacher را به student منتقل می‌کند. **محاسبهٔ زمان آزمون (test-time compute)** پس از پایان آموزش، برای پاسخ‌دادن به یک ورودی بیشتر محاسبه می‌کند؛ مانند تولید چند نامزد، بازبینی یا جست‌وجو. هر کدام به منابع متفاوت نیاز دارند و با هم یکی نیستند.

اگر یک سامانه روی تکلیف دشوار شکست می‌خورد، «دادهٔ بیشتر» لزوماً درمان نیست: شاید برچسب‌ها اشتباه‌اند، مثال‌ها تکراری‌اند، معیار نامتناسب است یا مدل از نظر ظرفیت محدود است. «نمونهٔ پاسخ بیشتر» نیز اگر همگی از خطای مشترک آمده باشند اطلاعات تازه‌ای نمی‌آورد. «استدلال طولانی‌تر» هم به‌تنهایی دلیل درستی نیست. تصمیم مهندسی باید از تحلیل خطا، آزمایش کنترل‌شده و هزینهٔ واقعی شروع شود.

## ۲. دادهٔ مصنوعی چیست و چه چیزی نیست؟

در این فصل، **دادهٔ مصنوعی** نمونه‌ای است که بخشی از prompt، ورودی، برچسب، پاسخ یا trace آن به‌وسیلهٔ برنامه، مدل، شبیه‌ساز یا قاعدهٔ خودکار ساخته شده است. این تعریف، منشأ نمونه را توصیف می‌کند؛ دربارهٔ کیفیت، درستی، بی‌طرفی، مالکیت، حریم خصوصی یا مجازبودن استفاده داوری نمی‌کند. خروجی یک مدل، حتی اگر به‌صورت روان نوشته شده باشد، «حقیقت مرجع» نمی‌شود.

دادهٔ مصنوعی برای توسعهٔ نمونه‌های مرزی، گسترش الگوهای کم‌شمار، ایجاد برچسب‌هایی که با برنامه وارسی می‌شوند، یا تولید مثال آموزشی با هزینهٔ کمتر می‌تواند مفید باشد. برای زبان‌های کم‌منبع و حوزه‌های حساس، خطر نیز بیشتر است: مولد ممکن است کلیشه‌ها و خلأهای دادهٔ موجود را بازتولید کند یا نمونه‌هایی بسازد که فقط از نظر قالب متنوع‌اند. مقدار ردیف‌ها را با پوشش مفهومی و استقلال داده برابر نگیرید.

## ۳. سه راه تولید و نقش «معلم»

۱. **تولید برنامه‌ای:** از دستور زبان، شبیه‌ساز یا تابعی با جواب معلوم استفاده می‌کنیم؛ مانند ساخت مسئلهٔ جمع و محاسبهٔ پاسخ با عملگر صحیح. کنترل‌پذیری خوب است، اما دامنهٔ مسائل باریک می‌ماند و قانون تولید ممکن است از test لو برود.

۲. **تولید با مدل:** چند seed انسانی یا مجاز به teacher داده می‌شود تا دستور، ورودی، پاسخ یا توضیح بسازد؛ نمونه‌های نامعتبر/تکراری باید فیلتر شوند. Self-Instruct نمونه‌ای از bootstrapکردن دستور و پاسخ از خروجی مدل و فیلترکردن نمونه‌های مشابه/نامعتبر است [۳]. نتیجهٔ همان مقاله به GPT‑3، مجموعه‌ها، معیارها و پروتکل‌های گزارش‌شده در آن مطالعه محدود است؛ آن را قاعده‌ای برای هر مدل و زبان ندانید.

۳. **تقطیر از خروجی teacher:** teacher می‌تواند وزن‌های قابل‌دسترسی داشته باشد یا فقط یک API متن‌محور باشد. در حالت دوم شاید توزیع logits در دسترس نباشد؛ آنچه منتقل می‌شود معمولاً پاسخ، امتیاز یا trace متنی است، نه کل حالت درونی مدل.

«معلم» برچسب نقش در آزمایش است، نه تضمین دانش یا اختیار. ثبت کنید کدام model/revision، prompt، decoding، ابزار و قواعد پس‌پردازش خروجی را ساخته‌اند. اگر انسان پاسخ را بازبینی کرده، سطح و شیوهٔ بازبینی را جداگانه ثبت کنید؛ بازبینی گزینشی با اعتبارسنجی مستقل روی همهٔ ردیف‌ها یکسان نیست.

## ۴. حلقهٔ بازخورد مصنوعی و خطر کپی‌کردن خطا

وقتی نمونه‌های ساخته‌شده به مجموعهٔ آموزش اضافه می‌شوند، مدل بعدی می‌تواند همان‌ها را دوباره به‌عنوان seed تولید کند. این چرخه ممکن است تنوع موضوعی را کم کند، خطاهای پرتکرار را تقویت کند یا توزیع متن را از دادهٔ هدف دور سازد؛ این پیامدها اجتناب‌ناپذیر نیستند، اما باید به‌عنوان فرضیهٔ شکست آزموده شوند. گزارش «صد هزار نمونه تولید شد» به‌تنهایی میزان پوشش یا سود آموزشی را نشان نمی‌دهد.

یک راه کنترل، حفظ نمونه‌های منشأدار، محدودکردن تکرار هر seed، ثبت خانوادهٔ prompt، سنجش شباهت و ارزیابی روی داده‌ای است که از همان generator یا teacher نیامده باشد. هرچه teacher و ارزیاب مشابه‌تر باشند، امکان توافق روی یک خطای مشترک بیشتر می‌شود. ترکیب منبع انسانی، دادهٔ مجاز، برنامهٔ قابل‌راستی‌آزمایی و چند generator ممکن است تنوع ایجاد کند، اما این ترکیب نیز نیازمند آزمون است.

## ۵. منشأ، مجوز، حریم خصوصی و شناسنامهٔ نمونه

در کنار متن نمونه، metadata نگه دارید: شناسهٔ پایدار، `group_id`، نوع منبع، زمان و نسخهٔ تولید، prompt یا قالب مولد، نسخهٔ مدل/ابزار، روش برچسب‌گذاری، قاعدهٔ فیلتر، hash فایل و وضعیت بازبینی. برای دادهٔ واقعی، مجوز، شرایط استفاده، رضایت یا مبنای پردازش و سیاست نگهداری باید از متن جداگانه بررسی شوند. «خودمان تولیدش کردیم» پاسخ کامل به پرسش منشأ و حقوق نیست؛ ممکن است ورودی یا seed از محتوای بیرونی/حساس آمده باشد.

دادهٔ مصنوعی می‌تواند اطلاعات شخصی یا محتوای به‌یادمانده از آموزش را بازتولید کند. از کمینه‌سازی داده، کنترل دسترسی، حذف موارد حساس، آزمون نشت و مسیر اعتراض/حذف استفاده کنید؛ این‌ها تضمین حذف کامل نیستند. چارچوب NIST برای ریسک GenAI نیز ارزیابی ریسک، حکمرانی و مستندسازی را در چرخهٔ سیستم مطرح می‌کند [۱۰]؛ این استاندارد جای مشاورهٔ حقوقی یا بررسی مقررات محل استفاده نیست.

## ۶. یک قرارداد دادهٔ قابل‌ممیزی

در یک رکورد آموزشی، شناسهٔ نمونه را از شناسهٔ گروه جدا کنید. برای نمونه:

```json
{"id":"ex-001","group_id":"seed-family-12","source":"synthetic_fixture","prompt":"Compute 2 + 3.","teacher_trace":"2 + 3 = 5","answer":"5","difficulty":"easy"}
```

`id` یکتا است؛ `group_id` نمونه‌های وابسته را کنار هم نگه می‌دارد؛ `source` نوع منشأ را نشان می‌دهد؛ `teacher_trace` خروجی تولیدشده و `answer` برچسب قابل‌وارسی است. در دادهٔ چندمرحله‌ای، نسخهٔ prompt، دادهٔ ورودی، پاسخ، نتیجهٔ verifier، زبان، ابزار، تاریخ و هرگونه بازبینی را نیز ذخیره کنید. اگر پاسخ مدل با برنامه تصحیح شده، هم پاسخ خام و هم پاسخ نهایی و قانون اصلاح را نگه دارید تا تغییر پنهان نماند.

شناسهٔ گروه باید از وابستگی واقعی پیروی کند: prompt seed، خانوادهٔ template، سند اصلی، مکالمه، کاربر یا مسئلهٔ مادر. شناسه‌ای تصادفی که به ردیف وابسته نیست، split گروهی را بی‌اثر می‌کند. نمونهٔ پروژه فقط `group_id`های ساختگی دارد؛ هیچ منبع انسانی یا بیرونی را نمایش نمی‌دهد.

## ۷. فیلتر، dedup و راستی‌آزمایی: چه چیزی را می‌توان کنترل کرد؟

در مسألهٔ جمع، validator می‌تواند trace را parse کند و جواب را با حساب صحیح محاسبه کند. در کد، تست واحد یا اجرای sandboxشده ممکن است بخشی از پاسخ را وارسی کند. در مسائل متنی باز، verifier می‌تواند rule، مرجع مستقل، تست موردی، ابزار یا ارزیاب انسانی/مدلی باشد. هر verifier سطحی از coverage دارد: پاس‌شدن assertionهای انتخابی همهٔ استدلال یا تمام رفتارهای ممکن را اثبات نمی‌کند.

Exact dedup را با hash متن نرمال‌شده انجام دهید؛ near-duplicate را با الگوریتم شباهت و آستانه‌ای که روی مثال‌های مرزی آزموده شده، بسنجید. حذف بیش‌ازحد می‌تواند تنوع واقعی را پاک کند و حذف ناکافی leakage ایجاد کند. پیش از حذف، شمار و نمونهٔ ردیف‌های حذف‌شده را ثبت کنید. اگر judge مدل است، ممکن است طول، سبک یا قالب را با درستی اشتباه بگیرد؛ داوری روی نمونهٔ کور، ترتیب جابه‌جا، پاسخ‌های نامعتبر و baseline rule-based را جدا گزارش کنید.

## ۸. split گروهی و آلودگی ارزیابی

تقسیم تصادفی ردیف‌ها هنگامی نشت می‌سازد که variantهای یک seed، یک سند یا نسخه‌های بازنویسی‌شده در train و test پخش شوند. ابتدا واحد استقلال را تعریف کنید؛ سپس همهٔ اعضای گروه را به یک split ببرید. برای دادهٔ تولیدشده، گروه ممکن است seed prompt، generator run، مسئلهٔ پایه یا خانوادهٔ template باشد. حتی split گروهی هم نشتِ گروه‌های ثبت‌نشده، شباهت معنایی یا آلودگی benchmark را کشف خودکار نمی‌کند.

فقط پس از ثابت‌کردن پروتکل، test را یک‌بار برای انتخاب نهایی باز کنید؛ هر بار تنظیم بر اساس test آن را به validation تبدیل می‌کند. اگر benchmark عمومی است، احتمال دیده‌شدنش در دادهٔ پیش‌آموزش یا synthetic teacher را بررسی و محدودیت را ثبت کنید. نسخه و hash ارزیابی را ذخیره کنید. اندازهٔ test کوچک، فاصلهٔ چند درصدی را لزوماً معنادار نمی‌کند؛ تعداد، عدم‌قطعیت و روش مقایسه را گزارش کنید.

## ۹. تقطیر دانش: چه چیزی از teacher منتقل می‌شود؟

در تقطیر، یک teacher بزرگ‌تر یا ensemble هدفی برای آموزش student کوچک‌تر فراهم می‌کند. هدف ممکن است **برچسب سخت** باشد، مثل کلاس نهایی؛ **توزیع نرم/logits** باشد، که نسبت احتمالات کلاس‌ها را منتقل می‌کند؛ یا **توالی پاسخ/trace** باشد که با loss توکنی آموزش داده می‌شود. این هدف‌ها مقدار اطلاعات، هزینهٔ دسترسی و خطرهای متفاوت دارند. تقطیر محدودیت‌های کیفیت student را حذف نمی‌کند و معمولاً نیازمند انتخاب داده و ارزیابی جداست [۱].

تقطیر از مدل API که فقط متن می‌دهد، تقطیر logits نیست. اگر API پاسخ و توضیح برگرداند، از آن‌ها می‌توان هدف sequence-level ساخت؛ اگر logits در دسترس باشند، می‌توان هدف توزیع را در نظر گرفت. «دانش teacher» استعاره‌ای برای رفتار قابل‌مشاهدهٔ هدف است؛ وزن‌های teacher کپی نمی‌شوند، مگر آنکه روش مشخصی واقعاً چنین کند.

## ۱۰. هدف نرم، دما و واگرایی KL

برای logits teacher برابر `zᵀ` و student برابر `zˢ`، softmax با دمای `T>0` تعریف می‌شود. دمای بزرگ‌تر توزیع را نرم‌تر می‌کند و گاهی نسبت خطاهای جایگزین را آشکارتر می‌سازد. loss متداولِ تقطیر، واگرایی `KL` از توزیع teacher به student است؛ ضریب `T²` در صورت‌بندی رایج، مقیاس گرادیان را با تغییر دما تنظیم می‌کند [۱].

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="توزیع نرم کلاس آی در دمای تی برابر نمایی لگیت آن بر تی تقسیم بر مجموع نمایی همه لگیت‌ها بر تی است">
  <mrow>
    <msubsup><mi>q</mi><mi>i</mi><mrow><mo>(</mo><mi>T</mi><mo>)</mo></mrow></msubsup><mo>=</mo><mfrac><mrow><mi>exp</mi><mo>(</mo><msub><mi>z</mi><mi>i</mi></msub><mo>/</mo><mi>T</mi><mo>)</mo></mrow><mrow><msub><mo>∑</mo><mi>j</mi></msub><mi>exp</mi><mo>(</mo><msub><mi>z</mi><mi>j</mi></msub><mo>/</mo><mi>T</mi><mo>)</mo></mrow></mfrac>
  </mrow>
</math>

**متن جایگزین فرمول:** احتمال نرم کلاس i برابر نماییِ logit آن تقسیم بر دما، تقسیم بر مجموع نمایی logits همهٔ کلاس‌ها با همان دما است. با `T=1` softmax معمولی به دست می‌آید؛ `T` باید مثبت باشد.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="زیان تقطیر برابر تی به توان دو ضربدر واگرایی کولبک لایبلر از توزیع teacher در دمای تی به توزیع student در همان دما است">
  <mrow>
    <msub><mi>L</mi><mi>distill</mi></msub><mo>=</mo><msup><mi>T</mi><mn>2</mn></msup><msub><mi>D</mi><mi>KL</mi></msub><mo>(</mo><msubsup><mi>q</mi><mi>teacher</mi><mrow><mo>(</mo><mi>T</mi><mo>)</mo></mrow></msubsup><mo>∥</mo><msubsup><mi>p</mi><mi>student</mi><mrow><mo>(</mo><mi>T</mi><mo>)</mo></mrow></msubsup><mo>)</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** loss تقطیر، واگرایی `KL` از توزیع نرم teacher به توزیع نرم student را در `T²` ضرب می‌کند. در پیاده‌سازی، جهت KL، ابعاد batch، محور کلاس و reduction را روشن ثبت کنید.

در آموزش واقعی ممکن است loss برچسب سخت و loss تقطیر با وزن‌هایی جمع شوند؛ وزن، دما، tokenizer، طول پاسخ و masking باید گزارش شوند. مقدار KL پایین فقط به معنی شباهت این دو توزیع روی همین ورودی‌ها و تعریف loss است، نه برابری توانایی یا درست‌بودن مدل.

## ۱۱. تقطیر پاسخ، trace و گام‌های میانی

**تقطیر پاسخ** پاسخ نهایی را هدف می‌گیرد؛ ارزیابی آسان‌تر است، ولی student ممکن است راهبرد حل را نیاموزد. **تقطیر trace** متن میانی تولیدشده را نیز آموزش می‌دهد؛ این trace ممکن است از teacher خطا داشته باشد یا صرفاً توجیه پسینیِ پاسخ باشد. **نظارت فرایندی** می‌تواند برچسب یا امتیاز هر گام را بیاموزد؛ برچسب‌گذاری پرهزینه است و process reward model هم verifier بی‌خطا نیست.

در مقالهٔ Distilling Step-by-Step، rationales به‌عنوان نظارت کمکی در یک چارچوب چندوظیفه‌ای استفاده شده‌اند؛ نتایج روی چهار benchmark NLP و تنظیم گزارش‌شدهٔ همان مقاله است [۴]. در مقالهٔ PaD، برنامهٔ قابل‌اجرا برای برخی مثال‌های استدلالی به‌عنوان میانجیِ قابل‌وارسی بررسی می‌شود [۵]. هیچ‌کدام نشان نمی‌دهد هر trace زبانی درست است یا هر مسأله را می‌توان به برنامه تبدیل کرد.

متن تولیدشدهٔ مدل را «دسترسی مستقیم به فکر درونی» ننامید. مدل ممکن است خروجیِ قابل‌خواندن اما ناقص، نامنطبق با فرایند واقعی یا اشتباه بسازد. اگر trace برای توضیح کاربر است، آن را از evidenceی که برای تصمیم لازم است جدا کنید و به‌جای اتکا به نثر persuasive، گام‌های قابل‌بررسی را آزمون کنید.

## ۱۲. student را در برابر چه چیزی و روی چه داده‌ای می‌سنجیم؟

student را با چند baseline مقایسه کنید: خود teacher، student با برچسب سخت، student با دادهٔ انسانی/مجازِ مرجع، و در صورت امکان student بدون curriculum. مقدار داده، تعداد update، tokenizer، compute و توقف باید هم‌تراز باشند؛ در غیر این صورت معلوم نیست gain از distillation آمده یا بودجهٔ بیشتر. برای teacher سیاه‌جعبه، هزینه و نسخهٔ API را هم ثبت کنید.

نتیجهٔ reported performance «student از teacher بهتر شد» می‌تواند در benchmark مشخص و با سازوکار متفاوت رخ دهد؛ این حکم کلی نیست. student ممکن است در یک task تخصصی بهتر ولی در توزیع دیگر ضعیف‌تر باشد. ارزیابی باید روی test مستقل، چند گروه/منبع و خطاهای زیرگروهی انجام شود. «مدل کوچک‌تر» به معنی latency، انرژی یا هزینهٔ کمتر در deployment نیست، مگر آن را روی سخت‌افزار و workload هدف اندازه گرفته باشیم.

## ۱۳. Curriculum Learning: ترتیب نمونه‌ها یک پارامتر آزمایشی است

**Curriculum learning** نمونه‌ها را بر اساس یک برنامهٔ دشواری یا معیار انتخاب، در طول آموزش دوباره وزن می‌دهد یا مرتب می‌کند. صورت انتزاعی آن را می‌توان به‌شکل زیر نوشت؛ `P(z)` توزیع مرجع داده، `wₜ(z)` وزن نمونه در گام `t` و `Qₜ(z)` توزیع مؤثر آموزش است [۲]:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="توزیع آموزشی در گام تی متناسب با وزن نمونه در آن گام ضربدر توزیع مرجع داده است">
  <mrow>
    <msub><mi>Q</mi><mi>t</mi></msub><mo>(</mo><mi>z</mi><mo>)</mo><mo>∝</mo><msub><mi>w</mi><mi>t</mi></msub><mo>(</mo><mi>z</mi><mo>)</mo><mi>P</mi><mo>(</mo><mi>z</mi><mo>)</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** در هر گام، احتمال دیده‌شدن نمونه با وزن برنامهٔ آن گام و احتمال آن در توزیع مرجع متناسب است. اگر همهٔ وزن‌ها برابر باشند، به نمونه‌گیری مرجع نزدیک می‌شویم.

نسخهٔ ساده، مثال‌های آسان را زودتر و دشوارترها را بعدتر می‌آورد. در روش‌های دیگر، مدل یا الگوریتم نمونه‌هایی را بر مبنای پیشرفت، عدم‌قطعیت یا competence انتخاب می‌کند. مقالهٔ Bengio و همکاران این ایده را در چند setup یادگیری مطرح کرد و بهبود در آزمایش‌های مشخص گزارش داد [۲]. این نتیجه وعدهٔ بهبود برای هر معماری، داده، معیار دشواری یا seed نیست.

## ۱۴. طراحی معیار دشواری و pacing

معیار دشواری باید به هدف مرتبط باشد، نه فقط با طول مثال. در جمع، انتقال از یک‌رقمی به چندرقمی یا وجود carry ممکن است سختی را تغییر دهد؛ در مکالمه، طول جمله الزاماً دشواری استدلال نیست. معیار را روی نمونه‌های دستی وارسی کنید، اندازهٔ هر bucket و ترکیب موضوع/زبان را گزارش کنید و بررسی کنید که curriculum با کیفیت برچسب یا منبع داده هم‌بسته نشده باشد.

برای تشخیص اثر ترتیب، train/validation/test و تعداد مثال را ثابت نگه دارید و دست‌کم این baselineها را مقایسه کنید: ترتیب curriculum، shuffle تصادفی و ترتیب معکوس یا مخلوط. updateها و بودجهٔ token برابر باشند؛ چند seed اجرا شود؛ معیار نهایی روی همان test جدا محاسبه شود. اگر curriculum ابتدا فقط آسان‌ها را نمایش می‌دهد، ممکن است مدل روی آن‌ها بیش‌برازش کند یا از نمونه‌های سخت کمتر یاد بگیرد. ادعای «مدل مانند انسان یاد می‌گیرد» از این روش نتیجه نمی‌شود.

## ۱۵. محاسبهٔ زمان آزمون: بودجه پس از آموزش

محاسبهٔ زمان آزمون یعنی اختصاص محاسبهٔ بیشتر به یک ورودی پس از آن‌که وزن‌های اصلی برای آن درخواست ثابت‌اند. نمونه‌ها: چند خروجی موازی، بازنویسی پیاپی، جست‌وجوی درختی، استفاده از verifier یا ابزار و توقف زودهنگام. این با fine-tuning در test-time فرق دارد؛ اگر پارامترها به‌روزرسانی شوند باید همان adaptation را صریحاً تعریف و ارزیابی کرد.

یک حساب سادهٔ هزینه برای `N` نامزد چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="هزینهٔ آزمون تقریبی برابر تعداد نامزدها ضربدر هزینهٔ تولید هر پاسخ، به‌علاوهٔ هزینهٔ verifier و ترکیب پاسخ‌ها است">
  <mrow>
    <msub><mi>C</mi><mi>test</mi></msub><mo>≈</mo><mi>N</mi><msub><mi>C</mi><mi>generate</mi></msub><mo>+</mo><msub><mi>C</mi><mi>verify</mi></msub><mo>+</mo><msub><mi>C</mi><mi>aggregate</mi></msub>
  </mrow>
</math>

**متن جایگزین فرمول:** هزینهٔ تقریبی inference برابر تعداد نامزدها ضربدر هزینهٔ تولید یک پاسخ، به‌علاوهٔ هزینهٔ verifier و تجمیع است. این برآورد به طول token، موازی‌سازی، سخت‌افزار، cache و نرخ سرو بستگی دارد.

این فرمول فقط دفترچهٔ حساب مفهومی است. latency برابر تعداد نمونه‌ها ضربدر latency یک نمونه نیست اگر اجرا موازی باشد؛ مصرف GPU یا انرژی نیز ممکن است با batch، KV cache و طول خروجی عوض شود. tokenهای تولیدشده، زمان دیواری، حافظه، هزینهٔ سرویس و نرخ خطا را روی workload واقعی بسنجید. گزینهٔ `N=1` و مسیر abstain را نگه دارید تا افزایش هزینه بی‌دلیل نشود.

## ۱۶. Self-consistency، Best-of-N و جست‌وجو

**Self-consistency** چند مسیر یا پاسخ نمونه می‌کند و پاسخ پرتکرار را انتخاب می‌کند. برای پاسخ‌های نهایی `aᵢ`:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="پاسخ برگزیدهٔ رأی هم‌ساز برابر آرگومان بیشینهٔ تعداد نامزدهایی است که پاسخ نهایی‌شان آ را می‌دهند">
  <mrow>
    <mover><mi>a</mi><mo>^</mo></mover><mo>=</mo><munder><mi>argmax</mi><mi>a</mi></munder><msubsup><mo>∑</mo><mi>i</mi><mi>N</mi></msubsup><mi>𝟙</mi><mo>(</mo><msub><mi>a</mi><mi>i</mi></msub><mo>=</mo><mi>a</mi><mo>)</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** پاسخ برگزیده با argmax شمارش به دست می‌آید: برای هر پاسخ نهایی می‌شماریم چند نامزد همان پاسخ را داده‌اند و بیشترین شمار را برمی‌گزینیم. فرمول رأی‌گیری ساده را نشان می‌دهد، نه همهٔ جزئیات مقاله.

مقالهٔ Self-Consistency مسیرهای متنوع را نمونه‌گیری و پاسخ‌های نهایی را تجمیع کرد؛ روی benchmarkهای گزارش‌شده بهبودهایی دیده شد [۶]. اما اگر نمونه‌ها وابسته باشند، خطای مشترک زیاد باشد یا پاسخ پرتکرار اشتباه باشد، رأی اکثریت شکست می‌خورد. در دمو فصل، پنج رشتهٔ ازپیش‌نوشته‌شده رأی‌گیری می‌شوند؛ آن‌ها خروجی مدل نیستند.

در **Best-of-N** یک verifier یا reward model نامزدها را رتبه‌بندی می‌کند؛ در **search** مدل روی شاخه‌ها گسترش می‌یابد و ارزش ادامه یا گام را برآورد می‌کند؛ در **revision** پاسخ یک یا چندبار بازبینی می‌شود. verifier می‌تواند از خود generator متفاوت باشد، اما استقلال خطا را تضمین نمی‌کند. مقالهٔ Snell و همکاران نشان می‌دهد تخصیص بهینهٔ محاسبه به دشواری prompt و روش مورد بررسی وابسته بود؛ آزمایش همان مقاله روی PaLM 2-S*، MATH و تنظیم‌های خاص انجام شده است، نه همهٔ مدل‌های reasoning امروز [۸].

## ۱۷. outcome، process و reward؛ verifier هم هدف می‌شود

**Outcome supervision** نتیجهٔ نهایی را می‌سنجد؛ مثلاً آیا عدد نهایی درست است؟ **Process supervision** برای گام‌های میانی بازخورد می‌دهد. در مطالعهٔ «Let’s Verify Step by Step»، نویسندگان نظارت گام‌به‌گام را در setup مطالعه‌شدهٔ MATH با نظارت نتیجه‌ای مقایسه و برتری گزارش کردند [۷]. این نتیجه دربارهٔ همان داده، مدل، بخش آزمون و برچسب‌گذاری است؛ هزینهٔ برچسب و انتقال به taskهای دیگر جداگانه بررسی می‌شود.

Verifier یا reward model می‌تواند هدف بهینه‌سازی شود و به نشانه‌های سطحی روی بیاورد. مثال‌ها: reward گرفتن از قالب خاص، تکرار گام‌های قابل‌قبول، انتخاب پاسخ کوتاه با ظاهر درست یا بهره‌برداری از خطای checker. مجموعه‌ای از تست‌های adversarial، آزمون verifier روی جواب‌های غلط اما متقاعدکننده، بازبینی انسان و گزارش abstain لازم است. اگر checker ناقص باشد، «پاس شد» را به «درست است» تعمیم ندهید.

## ۱۸. مدل‌های استدلالی: نام توانایی، نه معماری واحد

«مدل استدلالی» نامی رایج برای مدل یا سامانه‌ای است که روی تکلیف‌های چندمرحله‌ای، تولید راه‌حل، بررسی، بازنگری یا جست‌وجو آموزش/پیکربندی شده است. یک مدل می‌تواند با SFT روی trace، RL با reward قابل‌وارسی، verifier، compute بیشتر هنگام inference یا ترکیبی از این‌ها ساخته شود. این اسم به‌تنهایی معماری متفاوتی را تعریف نمی‌کند و درستی هر پاسخ را تضمین نمی‌کند.

نسخهٔ v2 مقالهٔ DeepSeek-R1، که در ۴ ژانویهٔ ۲۰۲۶ بازنگری شده، DeepSeek-R1-Zero را با RL مبتنی بر GRPO روی DeepSeek-V3-Base و rewardهای قاعده‌ای برای صحت/قالب در taskهای قابل‌وارسی شرح می‌دهد. مقاله همچنین برای DeepSeek-R1 یک فرایند چندمرحله‌ای شامل SFT، نمونه‌گیری/گزینش و RL، و تقطیر خروجی‌ها به مدل‌های کوچک‌تر گزارش می‌کند [۹]. این شرح، ادعای نویسندگان دربارهٔ مدل‌ها و منابع همان پروژه است؛ «بدون trace انسانی» در یک مرحله به معنای «بدون داده، مهندسی، انسان یا هزینه» نیست.

پاسخ طولانی‌تر، عبارت‌های «بررسی» یا تگ‌های reasoning، خودگزارشِ شفاف از محاسبهٔ درونی نیستند. برای محصول، رفتار قابل‌مشاهده را با معیار مستقل، دادهٔ آزمون و هزینهٔ پاسخ بسنجید. اگر استدلال مدل در اختیار کاربر قرار می‌گیرد، بررسی کنید آیا trace واقعاً قابل‌راستی‌آزمایی است و آیا افشای آن برای کاربر مناسب است؛ نمایش متن استدلال به‌تنهایی گواه صحت نیست.

## ۱۹. پروتکل سنجش کیفیت و هزینه

پیش از اجرا، ورودی‌ها، معیار اصلی، baseline، حداکثر بودجه، معیار توقف، verifier و روش آماری را ثبت کنید. برای تکلیف با جواب دقیق، exact match مفید است؛ برای پاسخ آزاد، rubric و ارزیابی انسانی کور یا معیارهای task-specific لازم می‌شود. گزارش کنید چند prompt پاسخ داشتند، چند پاسخ abstain شد و موارد نامعتبر/خارج از قالب چگونه شمرده شدند.

`pass@k` می‌پرسد آیا دست‌کم یک پاسخ از k نمونه درست بوده است؛ غالباً فرض می‌کند بهترین پاسخ را می‌توان تشخیص داد. اگر سامانه در deployment نتواند آن را تشخیص دهد، `pass@k` برابر دقت کاربر-نهایی نیست. `maj@k` یا vote، انتخاب قابل‌اجرا را می‌سنجد اما ممکن است پاسخ پرتکرار غلط باشد. هر دو را جدا بنویسید و دقیقاً مشخص کنید چه کسی/چه چیزی نامزد را انتخاب کرده است.

همراه کیفیت، تعداد token ورودی/خروجی، زمان دیواری، latency صدکی، throughput، تعداد فراخوانی verifier و هزینهٔ هر درخواست را گزارش کنید. اگر پاسخ با نمونه‌گیری تصادفی تولید می‌شود، seed و چند اجرای تکراری بیاورید. برای شکاف‌های کوچک، بازهٔ عدم‌قطعیت یا آزمون جفت‌شده گزارش شود؛ عدد خام روی چند prompt اثبات بهبود عمومی نیست. سنجش زیرگروهی را طوری طراحی کنید که دادهٔ حساس بی‌دلیل جمع یا منتشر نشود.

## ۲۰. آزمایشگاه فصل: ممیزی، KL، curriculum و رأی‌گیری

پروژهٔ `book-engineering/projects/50-synthetic-reasoning/` ورودی ساختگی جمع اعداد را اعتبارسنجی می‌کند. کد trace را با حساب صحیح بازحساب می‌کند، شناسه‌های تکراری را رد می‌کند، رکوردها را بر اساس `group_id` جدا می‌کند، یک ترتیب easy-to-hard می‌سازد، loss `T² KL(teacher || student)` را روی logits کوچک محاسبه می‌کند و رأی پرتکرار را روی پنج رشتهٔ ثابت آزمایش می‌کند.

از ریشهٔ مخزن، پس از نصب وابستگی‌های `requirements.txt` مطابق نسخهٔ پروژه، اجرا کنید:

```bash
cd book-engineering/projects/50-synthetic-reasoning
python -m unittest discover -v
python reasoning_lab.py --mode audit --fixture sample_traces.jsonl --output /tmp/ch50-audit
python reasoning_lab.py --mode demo --fixture sample_traces.jsonl --output /tmp/ch50-demo
```

آزمون واحد به PyTorch CPU و کتابخانهٔ استاندارد نیاز دارد. `audit` هیچ آموزشی انجام نمی‌دهد؛ `demo` فقط دو ماتریس logits و فهرست کاندید ازپیش‌نوشته‌شده را به کار می‌برد. در run ثبت‌شده، ۱۲ ردیف در ۶ گروه به splitهای train/validation/test با ۸/۲/۲ ردیف و ۴/۱/۱ گروه رفتند؛ ۲۶ آزمون موفق شدند. hash دقیق fixture در گزارش ممیزی و `results.json` آمده است. loss مصنوعی logits برابر `0.2875792384147644` شد؛ در vote پنج‌تایی، رشتهٔ `125` سه رأی داشت. این‌ها خروجی smoke-test توابع‌اند، نه نتیجهٔ مدل.

**مرز پروژه:** فقط جمع صحیح، logits ساختگی و candidateهای ثابت؛ هیچ LLM، teacher/student آموزش‌دیده، پاسخ فارسی، benchmark، GPU، هزینهٔ سرویس یا ارزیابی انسانی اجرا نشد. پروژه صحت همهٔ استدلال‌ها، مجوز/حقوق داده، privacy، کیفیت صنعتی یا برتری curriculum را تأیید نمی‌کند. دستورات دقیق‌تر و محدودیت‌ها در [README پروژه](book-engineering/projects/50-synthetic-reasoning/README.md)، و خروجی‌ها در [گزارش ممیزی فصل ۵۰](book-engineering/chapters/50-audit-report-fa.md) ثبت شده‌اند.

## ۲۱. تمرین‌ها: نمونه، split، هدف و بودجه

۱. یک teacher برای مسئلهٔ `12 + 24` trace «۱۲ + ۲۴ = ۳۵» می‌سازد، اما پاسخ نهایی را `36` می‌دهد. چه چیزی را می‌توان خودکار رد کرد؟ چه چیزی دربارهٔ traceهای پیچیده‌تر هنوز معلوم نیست؟

۲. دو رکورد از یک seed prompt با paraphrase متفاوت دارید. چرا split تصادفی ردیفی می‌تواند test را خوش‌بینانه کند؟ یک `group_id` مناسب پیشنهاد کنید.

۳. اگر logits teacher برابر `[2, 0, -1]` و logits student برابر `[0, 0, 0]` باشند، در `T=1` آیا KL صفر است؟ توضیح دهید جهت `KL(teacher || student)` چه توزیع‌هایی را مقایسه می‌کند؛ نیازی به محاسبهٔ اعشاری نیست.

۴. برای سنجش curriculum، سه baseline و دو شرط بودجهٔ ثابت تعریف کنید. دشواری را چگونه تعریف می‌کنید و کدام split را برای انتخاب schedule به کار می‌برید؟

۵. از پنج خروجی، پاسخ‌های نهایی `[A, B, A, A, C]` هستند. رأی self-consistency چه پاسخی انتخاب می‌کند؟ آیا `pass@5` یا اکثریت نشان می‌دهد احتمال پاسخ نهایی درست است؟ چه baselineی لازم است؟

۶. اگر هر نمونه ۸۰ token تولید کند و verifier هر کاندید را جداگانه ۱۲ میلی‌ثانیه پردازش کند، با ۴ کاندید چه مقادیری باید برای برآورد هزینه و latency اندازه‌گیری کنید؟ چرا ضرب سادهٔ ۴ در یک latency منفرد همیشه درست نیست؟

۷. مقالهٔ DeepSeek-R1-Zero چه نقشی برای GRPO و rewardهای قابل‌وارسی توصیف می‌کند؟ دو محدودیت برای تعمیم عددهای benchmark آن به محصول فارسی خود بنویسید.

۸. برای مقایسهٔ teacher، student با hard labels و student با soft targets، یک طرح ارزیابی مستقل با معیار کیفیت، هزینه و گزارش عدم‌قطعیت بنویسید.

**پاسخ‌نامهٔ مستقل:** [پاسخ‌نامهٔ تشریحی فصل ۵۰](book-engineering/answers/50-synthetic-reasoning-fa.md). **پروژه:** [README و دستورهای اجرا](book-engineering/projects/50-synthetic-reasoning/README.md)؛ **گزارش اجرا و محدودیت:** [گزارش ممیزی فصل ۵۰](book-engineering/chapters/50-audit-report-fa.md).

## ۲۲. جمع‌بندی: به‌جای شعار، مسیر شواهد را دنبال کنید

دادهٔ مصنوعی زمانی ارزش دارد که منشأ و هدفش معلوم باشد و نمونه‌ها با verifier متناسب، split گروهی و test مستقل سنجیده شوند. تقطیر ممکن است رفتار teacher را با هدف سخت، توزیع نرم یا trace به student منتقل کند؛ هر هدف اطلاعات و خطای متفاوت دارد. Curriculum ترتیب/وزن نمونه‌ها را تغییر می‌دهد و باید در برابر baseline با بودجه و test یکسان مقایسه شود. محاسبهٔ بیشتر هنگام آزمون می‌تواند کیفیت را در بعضی مسائل بالا ببرد، اما هزینه، انتخاب نامزد، وابستگی خطاها و verifier را نیز وارد سامانه می‌کند.

برای هر عدد چهار پرسش بپرسید: چه fixture یا benchmarkی؟ چه مدل و نسخه‌ای؟ چه معیار و بودجه‌ای؟ چه محدوده‌ای از ادعا؟ پروژهٔ این فصل فقط قراردادهای کوچک را آزمود؛ نتیجهٔ مدل یا زبان را نشان نداد. فصل بعد از دادهٔ مصنوعی و استدلال به نمایش تصویر، Vision Transformer و هم‌ترازی متن–تصویر می‌رود؛ مدل تصویر نیز به داده، split و ارزیابی مستقل نیاز دارد.

## ۲۳. منابع و تاریخ بازبینی

منابع در **۶ نوامبر ۲۰۲۶** بازبینی شدند. یافته‌های مقاله‌ها فقط به مدل، داده، task، بودجه و ارزیابی گزارش‌شده در همان کار محدودند؛ citation به معنی بازتولید نتیجه در این پروژه نیست.

۱. Hinton, G., Vinyals, O., & Dean, J.، “Distilling the Knowledge in a Neural Network”، NIPS 2014 Deep Learning Workshop؛ نسخهٔ arXiv در ۹ مارس ۲۰۱۵، arXiv:1503.02531. <https://arxiv.org/abs/1503.02531>
۲. Bengio, Y., Louradour, J., Collobert, R., & Weston, J.، “Curriculum Learning”، ICML 2009، صص. ۴۱–۴۸، DOI: 10.1145/1553374.1553380. <https://doi.org/10.1145/1553374.1553380>؛ <https://mlanthology.org/icml/2009/bengio2009icml-curriculum/>
۳. Wang, Y. و همکاران، “Self-Instruct: Aligning Language Models with Self-Generated Instructions”، ACL 2023؛ arXiv:2212.10560، نسخهٔ v2 مورخ ۲۵ مه ۲۰۲۳. <https://arxiv.org/abs/2212.10560>
۴. Hsieh, C.-Y. و همکاران، “Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes”، Findings of ACL 2023؛ arXiv:2305.02301، نسخهٔ v2 مورخ ۵ ژوئیهٔ ۲۰۲۳. <https://arxiv.org/abs/2305.02301>
۵. Zhu, X. و همکاران، “PaD: Program-aided Distillation Can Teach Small Models Reasoning Better than Chain-of-thought Fine-tuning”، arXiv:2305.13888، نسخهٔ v2 مورخ ۲۰ مارس ۲۰۲۴. <https://arxiv.org/abs/2305.13888>
۶. Wang, X. و همکاران، “Self-Consistency Improves Chain of Thought Reasoning in Language Models”، ICLR 2023؛ arXiv:2203.11171، نسخهٔ v4 مورخ ۷ مارس ۲۰۲۳. <https://arxiv.org/abs/2203.11171>
۷. Lightman, H. و همکاران، “Let’s Verify Step by Step”، arXiv:2305.20050، ارسال‌شده در ۳۱ مه ۲۰۲۳. <https://arxiv.org/abs/2305.20050>
۸. Snell, C., Lee, J., Xu, K., & Kumar, A.، “Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters”، arXiv:2408.03314، ارسال‌شده در ۶ اوت ۲۰۲۴. <https://arxiv.org/abs/2408.03314>
۹. DeepSeek-AI و همکاران، “DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning”، arXiv:2501.12948؛ نسخهٔ v2 مورخ ۴ ژانویهٔ ۲۰۲۶. <https://arxiv.org/abs/2501.12948>
۱۰. Autio, C. و همکاران، “Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile”، NIST AI 600-1، ۲۶ ژوئیهٔ ۲۰۲۴، DOI: 10.6028/NIST.AI.600-1. <https://doi.org/10.6028/NIST.AI.600-1>

## ۲۴. پیوست اجرایی: فایل آزموده‌شدهٔ پروژه

بلوک زیر باید بایت‌به‌بایت با فایل `book-engineering/projects/50-synthetic-reasoning/reasoning_lab.py` برابر بماند؛ checker و آزمون مرورگر این برابری را کنترل می‌کنند. کد fixture حسابی و logits ساختگی را پردازش می‌کند و مدل زبانی یا مجموعه‌داده‌ای بارگیری نمی‌کند.

```python
"""Offline synthetic-data, curriculum, distillation-loss, and voting lab.

The checked-in fixture is deterministic arithmetic data. This module does not
load an LLM, train a language model, or measure real reasoning quality.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

import torch
import torch.nn.functional as F

DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2}
TRACE_RE = re.compile(r"^\s*(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)\s*$")
REQUIRED_FIELDS = ("id", "group_id", "difficulty", "prompt", "teacher_trace", "answer", "label_source")


def load_jsonl(path: str | Path) -> tuple[list[dict[str, Any]], bytes]:
    """Read UTF-8 JSONL and return parsed rows plus the exact source bytes."""
    source = Path(path).read_bytes()
    try:
        text = source.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("fixture must be valid UTF-8") from exc
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on line {line_no}: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"line {line_no} must contain a JSON object")
        rows.append(row)
    return rows, source


def validate_records(rows: Sequence[dict[str, Any]]) -> list[str]:
    """Validate the deliberately narrow exact-addition fixture contract."""
    errors: list[str] = []
    seen_ids: set[str] = set()
    if not rows:
        return ["fixture has no records"]
    for index, row in enumerate(rows, 1):
        prefix = f"row {index}"
        missing = [field for field in REQUIRED_FIELDS if field not in row]
        if missing:
            errors.append(f"{prefix}: missing fields {missing}")
            continue
        bad_text = [field for field in REQUIRED_FIELDS if not isinstance(row[field], str) or not row[field].strip()]
        if bad_text:
            errors.append(f"{prefix}: fields must be non-empty strings: {bad_text}")
            continue
        record_id = row["id"].strip()
        if record_id in seen_ids:
            errors.append(f"{prefix}: duplicate id {record_id!r}")
        seen_ids.add(record_id)
        if row["difficulty"] not in DIFFICULTY_ORDER:
            errors.append(f"{prefix}: unknown difficulty {row['difficulty']!r}")
        if row["label_source"] != "synthetic_fixture":
            errors.append(f"{prefix}: label_source must be 'synthetic_fixture'")
        match = TRACE_RE.fullmatch(row["teacher_trace"])
        if not match:
            errors.append(f"{prefix}: trace must have the form 'a + b = c'")
            continue
        a, b, stated = map(int, match.groups())
        answer = str(a + b)
        if stated != a + b or row["answer"].strip() != answer:
            errors.append(f"{prefix}: trace/result does not match exact addition")
        expected_difficulty = "easy" if max(a, b) < 10 else "medium" if max(a, b) < 50 else "hard"
        if row["difficulty"] != expected_difficulty:
            errors.append(f"{prefix}: difficulty should be {expected_difficulty!r} under this fixture rule")
    return errors


def split_by_group(rows: Sequence[dict[str, Any]], seed: int = 50) -> dict[str, list[dict[str, Any]]]:
    """Make a deterministic 2/3, 1/6, remainder split by group, not row."""
    groups = sorted({row["group_id"] for row in rows})
    if len(groups) < 3:
        raise ValueError("at least three distinct groups are required for a train/validation/test split")
    random.Random(seed).shuffle(groups)
    n_train = max(1, round(len(groups) * (2 / 3)))
    n_validation = max(1, round(len(groups) * (1 / 6)))
    if n_train + n_validation >= len(groups):
        n_train = len(groups) - 2
        n_validation = 1
    assignment = {
        "train": set(groups[:n_train]),
        "validation": set(groups[n_train:n_train + n_validation]),
        "test": set(groups[n_train + n_validation:]),
    }
    return {
        name: [row for row in rows if row["group_id"] in selected]
        for name, selected in assignment.items()
    }


def curriculum_order(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Order fixture rows easy-to-hard; this does not claim an optimal schedule."""
    unknown = sorted({row.get("difficulty") for row in rows} - DIFFICULTY_ORDER.keys())
    if unknown:
        raise ValueError(f"unknown difficulty labels: {unknown}")
    return sorted(rows, key=lambda row: (DIFFICULTY_ORDER[row["difficulty"]], row["id"]))


def soft_target_kl(
    student_logits: torch.Tensor,
    teacher_logits: torch.Tensor,
    temperature: float = 1.0,
) -> torch.Tensor:
    """T-squared KL(teacher || student) for same-shaped batch logits."""
    if student_logits.shape != teacher_logits.shape or student_logits.ndim < 2:
        raise ValueError("student and teacher logits must have the same batch-by-class shape")
    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("temperature must be finite and greater than zero")
    teacher_probabilities = F.softmax(teacher_logits / temperature, dim=-1)
    student_log_probabilities = F.log_softmax(student_logits / temperature, dim=-1)
    return F.kl_div(
        student_log_probabilities,
        teacher_probabilities,
        reduction="batchmean",
    ) * (temperature ** 2)


def self_consistency_vote(candidates: Sequence[str]) -> tuple[str, dict[str, int]]:
    """Return the most frequent normalized candidate; ties follow first occurrence."""
    cleaned = [candidate.strip() for candidate in candidates]
    if not cleaned or any(not candidate for candidate in cleaned):
        raise ValueError("candidate list must be non-empty and contain no blank answers")
    counts = Counter(cleaned)
    maximum = max(counts.values())
    winner = next(candidate for candidate in cleaned if counts[candidate] == maximum)
    return winner, dict(sorted(counts.items()))


def audit_records(rows: Sequence[dict[str, Any]], source_bytes: bytes, seed: int = 50) -> dict[str, Any]:
    """Report fixture checks and group split; no model training is performed."""
    errors = validate_records(rows)
    if errors:
        raise ValueError("fixture validation failed: " + "; ".join(errors))
    split = split_by_group(rows, seed=seed)
    split_report = {}
    for name, subset in split.items():
        split_report[name] = {
            "records": len(subset),
            "groups": len({row["group_id"] for row in subset}),
            "group_ids": sorted({row["group_id"] for row in subset}),
        }
    return {
        "status": "synthetic_fixture_audit_complete",
        "records": len(rows),
        "groups": len({row["group_id"] for row in rows}),
        "label_sources": dict(sorted(Counter(row["label_source"] for row in rows).items())),
        "difficulty_counts": dict(sorted(Counter(row["difficulty"] for row in rows).items())),
        "split_seed": seed,
        "split": split_report,
        "sha256": hashlib.sha256(source_bytes).hexdigest(),
        "training_performed": False,
        "language_model_loaded": False,
        "model_downloaded": False,
        "device": "cpu",
        "claim_boundary": "synthetic arithmetic fixture only; not evidence of language-model or product quality",
    }


def run_demo(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Run fixed tensor and candidate fixtures to exercise two helper functions."""
    teacher_logits = torch.tensor([[2.0, 0.0, -1.0], [0.0, 1.5, -0.5]], dtype=torch.float32)
    student_logits = torch.tensor([[0.5, 0.0, -0.5], [0.0, 0.2, -0.5]], dtype=torch.float32, requires_grad=True)
    loss = soft_target_kl(student_logits, teacher_logits, temperature=2.0)
    loss.backward()
    candidates = ["125", "124", "125", "125", "126"]
    winner, counts = self_consistency_vote(candidates)
    curriculum = curriculum_order(rows)
    return {
        "status": "synthetic_math_helpers_smoke_test",
        "distillation_temperature": 2.0,
        "synthetic_logits_kl": float(loss.detach().item()),
        "student_gradient_is_finite": bool(torch.isfinite(student_logits.grad).all().item()),
        "candidate_fixture": candidates,
        "vote_winner": winner,
        "vote_counts": counts,
        "candidate_budget": len(candidates),
        "curriculum_first_ids": [row["id"] for row in curriculum[:3]],
        "curriculum_difficulty_order": [row["difficulty"] for row in curriculum],
        "training_performed": False,
        "language_model_loaded": False,
        "model_downloaded": False,
        "device": "cpu",
        "claim_boundary": "fixed tensor and candidate fixtures; not model sampling, training, or accuracy evaluation",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline lab for synthetic reasoning-data checks")
    parser.add_argument("--mode", choices=("audit", "demo"), required=True)
    parser.add_argument("--fixture", type=Path, default=Path(__file__).with_name("sample_traces.jsonl"))
    parser.add_argument("--output", type=Path, required=True, help="write JSON report outside the source tree")
    parser.add_argument("--seed", type=int, default=50)
    args = parser.parse_args(argv)
    try:
        rows, source_bytes = load_jsonl(args.fixture)
        result = audit_records(rows, source_bytes, seed=args.seed) if args.mode == "audit" else run_demo(rows)
        result["python_version"] = sys.version.split()[0]
        result["torch_version"] = torch.__version__
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "run.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

---

# جلد چهارم، فصل ۵ — مدل‌های تصویر، Vision Transformer و هم‌ترازی متن–تصویر

**نگاشت:** فصل محلی ۵ جلد چهارم = فصل سراسری ۵۱. **تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶.** فصل ۳۹ مسیر کلی اتصال مدالیته‌ها را معرفی کرد؛ فصل ۵۰ دربارهٔ دادهٔ مصنوعی، منشأ و ارزیابی بود. اکنون روی رمزگذار تصویر تمرکز می‌کنیم: پیکسل چگونه به وصله و نمایش برداری می‌رسد؟ خروجی global با ویژگی‌های مکانی چه فرقی دارد؟ و هم‌ترازی تصویر–متن دقیقاً چه چیزی را می‌آموزد؟ این فصل آموزش صوت یا ادغام عمومی چندمدالیته را تکرار نمی‌کند؛ فصل ۵۲ به نمایش صوت، بازشناسی و تولید گفتار می‌پردازد.

**پیش‌نیاز:** tensor و embedding از فصل‌های ۳۳–۳۶، نمای کلی Transformer چندوجهی از فصل ۳۹، و split گروهی و مرز ادعا از فصل ۵۰. **خروجی:** بتوانید مسیر تصویر تا token و embedding را توضیح دهید؛ میان classification، retrieval و ویژگی dense فرق بگذارید؛ فرض‌های contrastive loss را تشخیص دهید؛ و برای یک کاربرد تصویر–متن، داده و ارزیابی مستقل طراحی کنید.

![شکل ۴-۵-۱ — مسیر مفهومی رمزگذار تصویر: ورودی تصویری پس از تغییر اندازه و نرمال‌سازی به وصله‌ها تبدیل می‌شود؛ Vision Transformer نمایش‌های وصله‌ای و یک نمایش سراسری می‌سازد؛ projection متن و تصویر به فضای مقایسه می‌رسند؛ جفت‌های آموزشی با زیان contrastive هم‌تراز می‌شوند و ارزیابی retrieval جداگانه انجام می‌شود. تصویر و ماتریس شماتیک‌اند و مدل، داده یا نتیجهٔ بنچمارک واقعی را نشان نمی‌دهند.](book-engineering/diagrams/v4-ch05-vision.svg)

**شکل ۴-۵-۱ —** وصله‌ها فقط یک قرارداد ورودی‌اند؛ نوع pooling، projection و هدف آموزشی جداگانه انتخاب می‌شوند. نزدیکی embedding معیار مقایسهٔ آموخته‌شده است، نه شاهد مستقلِ فهم تصویر.

## ۱. از تصویر به تصمیم: سه خروجی را یکی نگیریم

سامانهٔ بینایی می‌تواند برچسب یک تصویر را پیش‌بینی کند، تصویرهای مرتبط با یک عبارت را بازیابی کند، ناحیه‌ای را مکان‌یابی کند یا ویژگی‌هایی برای مدل دیگری بسازد. «مدل تصویر» نام یک وظیفه یا معماری واحد نیست. یک encoder تصویری (image encoder) تابعی است که تصویر را به نمایش عددی تبدیل می‌کند؛ اینکه آن نمایش برای کدام کاربرد مناسب است، به داده، هدف آموزش، pooling، checkpoint و روش ارزیابی وابسته است.

در این فصل مسیر را به پنج تصمیم می‌شکنیم: قرارداد ورودی و وضوح؛ تبدیل پیکسل به توالی؛ انتخاب نمایش سراسری یا مکانی؛ یادگیری شباهت متن–تصویر؛ و آزمون روی داده‌ای جدا از آموزش. این تفکیک کمک می‌کند «بردارها قابل مقایسه‌اند» را با «مدل همهٔ جزئیات را فهمیده» اشتباه نگیریم.

## ۲. قرارداد ورودی تصویر: شکل tensor، رنگ و تبدیل‌ها

تصویر RGB معمولاً به tensorی با شکل `[B,C,H,W]` می‌رسد؛ `B` تعداد نمونه‌ها، `C` کانال رنگ و `H,W` ارتفاع و عرض‌اند. این فقط قرارداد حافظه است. فایل تصویری ممکن است alpha، پروفایل رنگ، جهت ثبت‌شده در metadata یا ابعاد متفاوت داشته باشد؛ loader باید تصمیم‌های خود را صریح کند. تبدیل ورودی به RGB، ترتیب کانال، دامنهٔ پیکسل و normalization را در کنار checkpoint ثبت کنید.

| تصمیم | نمونهٔ قرارداد | خطرِ پنهان در صورت ثبت‌نکردن |
|---|---|---|
| اندازه و نسبت تصویر | resize ثابت، حفظ نسبت، crop یا tile | شیء بریده یا کشیده می‌شود و test با train فرق می‌کند. |
| رنگ و مقدارها | RGB/کانال‌ها، دامنهٔ `[0,1]` یا آمار normalization | مقیاس و ترتیب کانال ممکن است با پیش‌آموزش ناسازگار شود. |
| برش و چندنما | center/random crop، چند crop یا تصویر کامل | ناحیهٔ شاهد حذف می‌شود یا تعداد viewها هزینه را بالا می‌برد. |
| دادهٔ فایل | فرمت، decoder، EXIF orientation و منبع | دو pipeline می‌توانند از یک فایل پیکسل‌های متفاوت بسازند. |

یک مدل ممکن است resize، crop و آمار کانال مشخصی را در recipe پیش‌آموزش به کار برده باشد؛ به‌کارگیری همان preprocessing نقطهٔ شروع مناسبی برای بازتولید سازگاری است، اما لزوماً بهترین انتخاب برای دامنهٔ هدف نیست. اگر اندازه یا crop را تغییر می‌دهید، مقایسه را روی validation انجام دهید و test نهایی را برای انتخاب بارها باز نکنید.

## ۳. وصله‌سازی تصویر و شمار توکن‌ها

در Vision Transformer ساده، تصویر به مربع‌هایی با ضلع `p` شکسته می‌شود. اگر ارتفاع و عرض بر `p` بخش‌پذیر باشند و padding/crop جداگانه‌ای انجام نشود، شمار وصله‌ها برابر حاصل‌ضرب تعداد ردیف و ستون است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="تعداد وصله‌ها برابر ارتفاع تقسیم بر اندازهٔ وصله ضربدر عرض تقسیم بر اندازهٔ وصله است؛ طول توالی برابر تعداد وصله‌ها به‌علاوهٔ تعداد tokenهای ویژه است">
  <mrow>
    <msub><mi>N</mi><mi>p</mi></msub><mo>=</mo><mfrac><mi>H</mi><mi>p</mi></mfrac><mo>×</mo><mfrac><mi>W</mi><mi>p</mi></mfrac><mo>,</mo><mspace width="1em"/>
    <msub><mi>N</mi><mi>seq</mi></msub><mo>=</mo><msub><mi>N</mi><mi>p</mi></msub><mo>+</mo><msub><mi>n</mi><mi>special</mi></msub>
  </mrow>
</math>

**متن جایگزین فرمول:** تعداد وصله‌ها برابر ارتفاع تقسیم بر اندازهٔ وصله ضربدر عرض تقسیم بر اندازهٔ وصله است؛ طول توالی تعداد وصله‌ها به‌علاوهٔ tokenهای ویژه است. این قرارداد فرض می‌کند اندازه‌ها بر وصله بخش‌پذیرند یا سیاست padding/crop جدا ثبت شده است.

برای تصویر `224×224` و `p=16`، شبکه `14×14` و در نتیجه `196` وصله دارد. بعضی ViTها یک token ویژه مانند `[CLS]` به توالی می‌افزایند؛ آن‌گاه encoder در این مثال `197` token می‌بیند. همهٔ مدل‌ها `[CLS]` ندارند و برخی از میانگین وصله‌ها یا pooling دیگری استفاده می‌کنند. بنابراین شمار patchها را با طول دقیق توالی checkpoint یکی نگیرید.

وصله‌ها در ترتیب مکانی ثابت flatten می‌شوند و معمولاً projection و embedding موقعیت دریافت می‌کنند. برای تصویر خاکستری، رنگی یا اندازهٔ غیرمعمول، قرارداد ورودی عوض می‌شود؛ «هر بلوک پیکسل یک کلمه است» فقط شهودی برای تبدیل ساختاری است، نه معنای زبانی یا برچسب‌گذاری تصویر.

## ۴. Vision Transformer: وصله، موقعیت و encoder

ViT وصلهٔ تصویری را با یک نگاشت آموختنی به بردار `d`-بعدی می‌برد؛ نگاشت را می‌توان به‌شکل لایهٔ خطی روی وصلهٔ تخت‌شده یا convolution با kernel و stride برابر اندازهٔ وصله پیاده کرد. سپس موقعیت به بردارها افزوده می‌شود و توالی از بلوک‌های Transformer encoder می‌گذرد. خروجی‌ها نمایش‌های وابسته به وصله‌اند؛ token ویژه، اگر وجود داشته باشد، می‌تواند خلاصه‌ای سراسری برای head بعدی فراهم کند [۱].

در Attention متراکم، هر token می‌تواند با هر token دیگر تعامل کند. اگر هر دو بُعد تصویر دو برابر شوند و اندازهٔ وصله ثابت بماند، تعداد وصله‌ها چهار برابر می‌شود؛ تعداد جفت‌های score در هر head تقریباً شانزده برابر می‌شود. برای `224×224` و `448×448` با وصلهٔ ۱۶، توالی‌های دارای `[CLS]` به‌ترتیب ۱۹۷ و ۷۸۵ token‌اند؛ جفت‌های توجه `38,809` و `616,225`، یعنی حدود `15.88×` می‌شوند. این شمار، هزینهٔ کل مدل یا latency را پیش‌بینی نمی‌کند: MLP، projection، تعداد لایه‌ها، batch، kernel، حافظه و سخت‌افزار نیز اثر دارند.

ViT نشان داد self-attention می‌تواند روی دنبالهٔ وصله‌های تصویر به کار رود؛ نتایج مقاله به اندازه و ترکیب دادهٔ پیش‌آموزش و پروتکل انتقال همان مطالعه وابسته است [۱]. این گزاره نه می‌گوید هر ViT از CNN بهتر است، نه اینکه یک checkpoint روی هر وضوح و هر دامنه آمادهٔ استفاده است.

## ۵. خروجی image encoder: بردار سراسری یا نقشهٔ ویژگی؟

یک encoder ممکن است توالی‌ای با شکل `[B,N,d]` برگرداند؛ `N` تعداد tokenهای تصویر و `d` عرض نمایش است. برای retrieval سراسری یا classification معمولاً یک pooling rule این توالی را به `[B,d]` تبدیل می‌کند: بردار `[CLS]`، میانگین وصله‌ها یا pooling آموختنی، بسته به مدل. سپس head طبقه‌بندی به فضای برچسب‌ها نگاشت می‌کند؛ projection contrastive بردار را به فضایی می‌برد که با متن قابل مقایسه باشد. این headها را نباید با خود encoder یکی گرفت.

اگر به محل شیء، segmentation یا featureهای مکانی نیاز داریم، میانگین‌گیری سراسری ممکن است اطلاعات مکان را حذف کند. نگه‌داشتن `[B,N,d]` یا لایه‌های میانی می‌تواند جزئیات مکانی بیشتری بدهد، اما patch embedding به‌تنهایی mask پیکسلی یا ناحیهٔ حقیقت‌مرجع نیست. برای خروجی dense، هدف، برچسب و معیار مکانیِ متناسب لازم است.

نام API مانند `get_image_features` یا «embedding» کافی نیست تا بدانیم بردار از کدام لایه، با چه pooling و normalization آمده است. هنگام مقایسهٔ checkpoint، قرارداد preprocessing، لایه، projection، dimension و normalization را هم ثبت کنید؛ دو بردار هم‌اندازه الزاماً در یک فضای معنایی نیستند.

## ۶. CNN، ViT و انتخاب انتقال

CNN با کانولوشن و locality bias ساختار مکانی محلی را در معماری وارد می‌کند؛ ViT self-attention را روی tokenهای وصله‌ای به کار می‌گیرد. این‌ها inductive bias و محاسبهٔ متفاوت دارند، نه جدول رتبه‌بندی همیشگی. دادهٔ موجود، اندازهٔ تصویر، نیاز به جزئیات، checkpointهای مجاز، latency و robustness دامنهٔ هدف بر انتخاب اثر می‌گذارند. معماری‌های hybrid نیز ممکن‌اند؛ نتیجه را با نام معماری تنها حدس نزنید.

پس از انتخاب encoder، سه راه رایج برای تطبیق وجود دارد: freeze و آموزش یک head/projection؛ آموزش adapter یا بخشی از لایه‌ها؛ و fine-tuning گسترده‌تر. Freeze می‌تواند هزینهٔ به‌روزرسانی را کاهش دهد، اما اگر ویژگی ثابت ناحیه یا سبک لازم را نگه ندارد، adaptation محدود می‌ماند. Fine-tuning آزادی بیشتری می‌دهد و هم‌زمان به داده، محاسبه، کنترل overfit و ارزیابی دقیق‌تری نیاز دارد. در مقایسه، split، checkpoint آغازین، تعداد نمونه، update، معیار و بودجه را تا حد ممکن ثابت نگه دارید.

## ۷. سه خانوادهٔ پیش‌آموزش تصویر

**نظارت برچسب‌دار:** تصویر و برچسب رده هدف classification می‌شوند. head ممکن است بعداً حذف و encoder برای وظیفهٔ دیگر استفاده شود. دقت همان رده‌بندی، به‌تنهایی انتقال به retrieval یا segmentation را اثبات نمی‌کند.

**بازسازی وصله‌های پنهان:** در Masked Autoencoder (MAE)، بخش بزرگی از وصله‌ها پنهان می‌شوند و decoder بازسازی آن‌ها را یاد می‌گیرد؛ مقاله encoder/decoder نامتقارن را برای این هدف بررسی کرد [۲]. بازسازی پیکسل/وصله یک هدف خودنظارتی است، نه برچسب معنایی مستقیم برای هر کاربرد پایین‌دستی.

**یادگیری خودنظارتی و self-distillation:** DINOv2 ویژگی‌های عمومی‌تر را از دادهٔ تصویری و هدف‌های self-supervised/distillation می‌آموزد؛ مقاله داده‌سازی و گزینش را نیز بخشی از recipe خود می‌داند [۳]. این واژه‌ها خانوادهٔ روش‌اند: encoder، augmentation، teacher/student، loss و داده میان پیاده‌سازی‌ها فرق دارند. هیچ هدف پیش‌آموزشی به‌تنهایی کیفیت همهٔ کاربردها را تضمین نمی‌کند.

## ۸. از دو encoder تا فضای مشترک تصویر–متن

در معماری dual-encoder، رمزگذار تصویر `fᵢ(x)` و رمزگذار متن `fₜ(c)` جداگانه نمایش می‌سازند. pooling و projection هر مسیر، بردارهایی با بُعد مشترک می‌دهند؛ L2-normalization امکان مقایسه با cosine similarity را فراهم می‌کند. تصویر یا متن را می‌توان یک‌بار encode کرد و برای جست‌وجو، بردارهای gallery را ذخیره کرد. این طراحی برای retrieval مقیاس‌پذیر است، اما تعامل tokenبه‌token یا یافتن شاهد دقیق در یک ناحیه را از یک cosine نتیجه نمی‌دهد.

در CLIP، جفت‌های تصویر–شرح با هدف contrastive آموزش داده شدند و مقاله انتقال صفرنمونه‌ای را روی مجموعه‌ای از taskهای بینایی گزارش کرد [۴]. در یک batch از `B` جفت، ماتریس شباهت `B×B` ساخته می‌شود؛ در صورت یک جفت مثبت برای هر سطر، مقدار قطر هدف است و خانه‌های دیگر در نسخهٔ ساده منفی فرض می‌شوند:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="شباهت زوج آی جی برابر مقیاس ضربدر cosine بردارهای نرمال‌شدهٔ تصویر آی و متن جی است؛ زیان متقارن میانگین cross entropy تصویر به متن و متن به تصویر با هدف قطر ماتریس است">
  <mrow>
    <msub><mi>s</mi><mrow><mi>i</mi><mi>j</mi></mrow></msub><mo>=</mo><mi>τ</mi><mo>·</mo><msubsup><mi>v</mi><mi>i</mi><mo>⊤</mo></msubsup><msub><mi>t</mi><mi>j</mi></msub><mo>,</mo><mspace width="0.8em"/>
    <mi>ℒ</mi><mo>=</mo><mfrac><mn>1</mn><mn>2</mn></mfrac><mo>(</mo><mi>CE</mi><mo>(</mo><mi>S</mi><mo>,</mo><mi>diag</mi><mo>)</mo><mo>+</mo><mi>CE</mi><mo>(</mo><msup><mi>S</mi><mi>⊤</mi></msup><mo>,</mo><mi>diag</mi><mo>)</mo><mo>)</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** شباهت زوجی برابر مقیاس `τ` ضربدر ضرب داخلی embeddingهای واحد تصویر و متن است؛ زیان دوطرفه میان cross-entropy مسیر تصویر‌به‌متن و متن‌به‌تصویر، با جفت‌های قطر به‌عنوان هدف، میانگین می‌گیرد. این صورت‌بندی، batch تک‌مثبتی را ساده می‌کند.

**نکتهٔ قرارداد:** `τ` در این نماد مقیاس logit است؛ برخی مقاله‌ها/کتابخانه‌ها دما را به‌صورت تقسیم بر `T` یا پارامتر آموختنی می‌نویسند. پیش از بازتولید، جهت مقیاس، normalization، محور softmax و reduction را در منبع همان پیاده‌سازی بررسی کنید. similarity خام احتمال کالیبره‌شده نیست.

## ۹. مثبت، منفی و false negative

فرض «هر خانهٔ خارج قطر منفی است» فقط وقتی معقول است که جفت‌های داخل batch واقعاً غیرمرتبط باشند. چند caption ممکن است یک تصویر را درست توصیف کنند؛ دو تصویر ممکن است نمای متفاوتی از یک شیء/مفهوم باشند؛ یا duplicateها وارد batch شوند. آن‌گاه جفتِ معناییِ مثبت به‌اشتباه منفی آموزش داده می‌شود. بزرگ‌ترشدن batch می‌تواند نمونه‌های بیشتری برای مقایسه فراهم کند و هم‌زمان احتمال جفت‌های هم‌معنا را بالا ببرد.

پیش از تغییر loss، ساختار جفت‌ها را بررسی کنید: چند شرح به هر تصویر وصل است؟ duplicate، near-duplicate یا گروه صحنه چگونه شناخته می‌شود؟ آیا query باید عین شیء، مفهوم کلی یا رابطهٔ مکانی را پیدا کند؟ برای چند مثبت می‌توان objective یا maskی طراحی کرد که همهٔ مثبت‌های ثبت‌شده را لحاظ کند؛ اما صحت این برچسب‌ها و مرز «مرتبط» همچنان مسئلهٔ داده و تعریف task است.

## ۱۰. Sigmoid loss در برابر softmax سراسری

SigLIP یک هدف pairwise مبتنی بر sigmoid را برای پیش‌آموزش تصویر–زبان بررسی می‌کند؛ جفت مثبت و جفت منفی با برچسب‌های زوجی وارد loss می‌شوند و objective به نرمال‌سازی softmax سراسری روی هر سطر ماتریس به همان شکل CLIP متکی نیست [۵]. یک نمایش شماتیک آن چنین است؛ `yᵢⱼ` برای جفت مثبت `+1` و برای منفی `−1` است و `b` می‌تواند bias logit باشد:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="زیان sigmoid برای زوج‌های تصویر و متن متناسب با منفی مجموع لگاریتم سیگموید برچسب زوج ضربدر شباهت مقیاس‌شده به‌علاوهٔ bias است">
  <mrow>
    <msub><mi>ℒ</mi><mi>sigmoid</mi></msub><mo>∝</mo><mo>−</mo><munderover><mo>∑</mo><mrow><mi>i</mi><mo>,</mo><mi>j</mi></mrow><mi>B</mi></munderover><mi>log</mi><mi>σ</mi><mo>(</mo><msub><mi>y</mi><mrow><mi>i</mi><mi>j</mi></mrow></msub><mo>(</mo><msub><mi>s</mi><mrow><mi>i</mi><mi>j</mi></mrow></msub><mo>+</mo><mi>b</mi><mo>)</mo><mo>)</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** در صورت‌بندی شماتیک sigmoid، هر زوج برچسب مثبت یا منفی دارد و loss منفیِ لگاریتم احتمال سیگمویدِ امتیاز زوج با همان برچسب است. علامت bias، مقیاس، وزن‌دهی و normalization در پیاده‌سازی باید دقیق خوانده شود؛ فرمول بالا نسخهٔ کامل یک trainer خاص نیست.

تفاوت هدف آموزشی می‌تواند مصالحهٔ محاسباتی/آموزشی را عوض کند؛ از نام loss نتیجهٔ عمومی دربارهٔ کیفیت، کارایی یا نبود false negative نگیرید. Sigmoid هم برای یادگیری به تعریف و کیفیت جفت‌ها نیاز دارد [۵]. پروژهٔ فصل، sigmoid loss را پیاده نمی‌کند؛ تابع contrastive آن softmax دوطرفهٔ ساده‌ای برای آموزش قراردادهاست.

## ۱۱. caption و مجموعه‌داده بخشی از مدل‌اند

caption معمولاً همهٔ محتوای تصویر را ثبت نمی‌کند: ممکن است رنگ، شمار، نفی، رابطهٔ فضایی، جزئیات متن داخل تصویر یا زمینهٔ فرهنگی حذف شود. جفت متن–تصویر از نظر فایل کنار هم بودن، تضمین نمی‌کند که متن به همان تصویر اشاره دارد. کیفیت فیلتر، زبان، تکرار، provenance و توزیع موضوعی می‌توانند به‌اندازهٔ انتخاب encoder مهم باشند.

DataComp مجموعه‌ای از recipeهای فیلتر دادهٔ تصویر–متن را با backbone و پروتکل ارزیابی ثابت برای مقایسهٔ اثر مجموعه‌داده بررسی می‌کند؛ نتیجه‌های آن به benchmark، مدل ثابت و تنظیمات همان مطالعه محدود است [۶]. برای دادهٔ واقعی، منبع/مجوز تصویر، شرایط بازاستفاده، رضایت/حریم خصوصی، retention و مسیر حذف باید جداگانه بررسی شود. تولید caption مصنوعی نیز منبع و مدل مولد تازه‌ای به زنجیره اضافه می‌کند؛ «متن ساخته‌شده» به‌خودی‌خود درست، بی‌طرف یا مجاز نیست.

برای ارزیابی، metadata دست‌کم باید شناسهٔ تصویر، شناسهٔ منبع/گروه، متن یا شناسهٔ caption، split، روش گردآوری، نسخهٔ preprocessing و hash فایل/manifest را نگه دارد. split در سطح منبع/تصویر اصلی و گروه معنایی می‌تواند برخی leakageها را کاهش دهد؛ شباهت معناییِ ثبت‌نشده یا حضور benchmark در دادهٔ پیش‌آموزش را خودکار از بین نمی‌برد.

## ۱۲. دو کاربرد رایج: retrieval و zero-shot classification

در **image-to-text retrieval**، تصویر query است و captionها/جمله‌ها candidate؛ در **text-to-image retrieval**، عبارت query است و gallery از تصویرها تشکیل می‌شود. پس از precompute کردن embeddingهای gallery، جست‌وجو بر اساس similarity مرتب می‌کند. دو جهت باید جدا سنجیده شوند: تعداد، تنوع و دشواری queryها/کاندیدها ممکن است نامتقارن باشد. top-1 نتیجهٔ رتبه‌بندی در همین gallery است، نه احتمال اینکه تصویر در جهان «واقعاً» به پرسش مربوط باشد.

در **zero-shot classification**، هر کلاس می‌تواند با یک یا چند prompt متنی نمایش داده شود؛ تصویر با متن کلاس‌ها مقایسه و بیشترین similarity انتخاب می‌شود. این روش classifier از پیش‌آموزش‌دیدهٔ همان رده‌ها را جایگزین می‌کند، نه لزوماً ناظر انسانی را. prompt، واژگان کلاس، تعداد template، زبان، class imbalance و کالیبراسیون ممکن است بر نتیجه اثر بگذارند. انتخاب کلاس با `argmax` هم confidence معتبر یا حق استفاده از تصویر را نمی‌دهد.

یک کاربرد محصولی ممکن است به reranker یا cross-encoder نیاز داشته باشد، اما آن مرحله خارج از مدل embedding ساده است و باید با هزینه و معیار مستقل سنجیده شود. جزئیات کلی dual-encoder و cross-attention در فصل ۳۹ هستند؛ این فصل بر تصویر، patch feature و ارزیابی هم‌ترازی متمرکز می‌ماند.

## ۱۳. ارزیابی retrieval و split مستقل

پیش از ساخت شاخص، واحد relevance را تعریف کنید: آیا یک تصویر دقیق مثبت است، هر تصویر از همان گروه، هر caption معادل، یا فقط نمونه‌ای که شاهد موردنیاز را دارد؟ برای هر query، رتبهٔ نخستین candidate مرتبط را `rᵢ` بنامید. دو معیار رایج چنین‌اند:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="Recall در k برابر نسبت queryهایی است که دست‌کم یک نتیجهٔ مرتبط را در k رتبهٔ اول دارند؛ میانگین رتبهٔ معکوس برابر میانگین یک تقسیم بر رتبهٔ نخستین نتیجهٔ مرتبط است">
  <mrow>
    <msub><mi>Recall</mi><mi>k</mi></msub><mo>=</mo><mfrac><mn>1</mn><mi>Q</mi></mfrac><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>Q</mi></munderover><mi>𝟙</mi><mo>(</mo><msub><mi>r</mi><mi>i</mi></msub><mo>≤</mo><mi>k</mi><mo>)</mo><mo>,</mo><mspace width="1em"/>
    <mi>MRR</mi><mo>=</mo><mfrac><mn>1</mn><mi>Q</mi></mfrac><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>Q</mi></munderover><mfrac><mn>1</mn><msub><mi>r</mi><mi>i</mi></msub></mfrac>
  </mrow>
</math>

**متن جایگزین فرمول:** Recall@k سهم queryهایی است که یک نتیجهٔ مرتبط را در نخستین k رتبه پیدا می‌کنند. MRR میانگین معکوس رتبهٔ نخستین نتیجهٔ مرتبط است؛ اگر query هیچ مثبت ثبت‌شده‌ای نداشته باشد، باید سیاست امتیازدهی آن جدا تعریف شود.

در عمل، queryهایی که هیچ نتیجهٔ مرتبطی ندارند باید از قبل سیاست‌گذاری شوند: آیا کنار گذاشته می‌شوند، یا task شامل abstain/عدم بازیابی است؟ `Recall@k`/`MRR` فقط با gallery و ground truth تعریف‌شده قابل تفسیرند؛ split، تعداد query، چند مثبت، duplicate، روش نمونه‌گیری و فاصلهٔ اطمینان را ثبت کنید. اگر یک تصویر چند caption دارد، group ID باید مثبت‌ها را درست کنار هم نگه دارد.

برای کاهش leakage، split را در سطح تصویر اصلی، منبع، فیلم/صحنه یا گروهی که نمونه‌ها را وابسته می‌کند بسازید؛ فقط ردیف‌های caption را تصادفی تقسیم نکنید. image→text و text→image، دامنه/زبان‌های هدف و جست‌وجوی دشوار (hard negative) را جدا گزارش کنید. بنچمارک عمومی را ممکن است خود پیش‌آموزش دیده باشد؛ hash/split ثبت می‌شود، اما contamination فقط با ثبت hash رد نمی‌شود.

## ۱۴. وضوح، چندنما و هزینهٔ پردازش

تصویر کوچک‌شده ارزان‌تر است، اما متن ریز، نمودار، شیء کوچک یا جزئیات پزشکی/صنعتی ممکن است از بین بروند. گزینه‌ها شامل حفظ نسبت تصویر با padding، crop ثابت، چند crop، tiling یا encoderی با وضوح ورودی بالاتر است. هر گزینه توزیع پیکسل و تعداد token را عوض می‌کند. اگر positional embedding به grid خاصی وابسته است، تغییر grid به روش interpolation یا سازوکار پشتیبانی‌شدهٔ checkpoint نیاز دارد؛ resize کردن خام تصویر و تغییر positional embedding یکسان نیست.

اگر برای دیدن جزئیات، تصویر را به چند tile ببریم، مجموعهٔ tileها به یک ورودی منطقی تعلق دارند و باید در ارزیابی کنار هم بمانند. embedding سراسری هر crop ممکن است محل هر crop را نادیده بگیرد؛ ذخیرهٔ مختصات و تجمیع باید با task سازگار باشد. گزارش هزینه نیز باید تعداد crop/tile، resolution، batch، طول توالی، زمان encode و حافظه را روی سخت‌افزار هدف جدا اندازه‌گیری کند؛ شمار پارامترها به‌تنهایی هزینهٔ واقعی inference نیست.

## ۱۵. ویژگی‌های مکانی و لایه‌های میانی

خروجی سراسری مناسب است وقتی مسئلهٔ اصلی رتبه‌بندی کلی تصویر–متن باشد؛ برای localization یا segmentation، ویژگی‌های patch-level و اتصال آن‌ها به مختصات اهمیت دارند. DINOv3 حفظ کیفیت ویژگی‌های dense را برای آموزش طولانی‌تر با سازوکاری به نام Gram anchoring بررسی می‌کند [۷]. «dense feature بهتر» ادعای مقاله در تنظیم‌های گزارش‌شده است، نه تضمین اینکه هر مدل یا تصویر مکانیابی دقیق می‌دهد.

مقالهٔ Perception Encoder گزارش می‌کند که برای برخی سنجه‌های embedding، لایه‌های میانی می‌توانند از بردار خروجی نهایی سودمندتر باشند؛ روش آن چند خروجی/layer را بررسی می‌کند [۸]. این نتیجه انگیزه‌ای برای آزمایش لایه و pooling است، نه قانون انتخاب دائمی. checkpointهای مختلف ممکن است featureهای متفاوتی را برای downstream task مناسب کنند. برای ارزیابی dense باید ground truth مکانی، tolerances، سطح جزئیات و معیارهایی مانند IoU یا localization error تعریف شود؛ retrieval کلی جای این آزمون را نمی‌گیرد.

## ۱۶. انتخاب اولیه بر پایهٔ نیاز

| هدف | نمایش/مسیر اولیه برای بررسی | معیار و احتیاط |
|---|---|---|
| جست‌وجوی متن در آرشیو تصویر | dual-encoder و embeddingهای cacheشدنی | Recall@k و MRR در gallery ثابت؛ query و تصویر هم‌دامنه نیستند مگر آزموده شود. |
| دسته‌بندی با برچسب‌های متنی | image–text similarity / zero-shot | macro و per-class معیار؛ prompt و زبان را ثابت و مستند کنید. |
| ناحیه، شیء یا سند با متن ریز | patch/dense feature، crop یا مدل localization | دادهٔ ناحیه‌ای و ارزیابی مکانی لازم است؛ وضوح بیشتر هزینه دارد. |
| سازگاری با دامنهٔ خاص | encoder ازپیش‌آموزش‌دیده + head/adapter یا fine-tune | baseline منجمد و بودجهٔ مقایسهٔ منصفانه؛ حقوق checkpoint و تصویر را بررسی کنید. |
| تصویر حساس یا محلی | pipeline پردازش محلی/کنترل‌شده | محل پردازش به‌تنهایی مجوز، رضایت یا privacy را تضمین نمی‌کند. |

این جدول گزینه‌های شروع برای طرح آزمایش است، نه توصیهٔ مدل/فروشنده یا ضمانت انطباق. ابتدا خطا و نیاز را تعریف کنید؛ سپس فقط متغیری را که آزمون می‌خواهید درباره‌اش نتیجه بگیرید تغییر دهید.

## ۱۷. خطا، سوگیری و حریم خصوصی تصویر

شباهت embedding می‌تواند به watermark، پس‌زمینه، قالب وب‌سایت یا متن همراه متکی شود، نه شیء موردنظر. مدل ممکن است کلاس‌های پرتکرار را بهتر بازیابی کند؛ تصویرهای کم‌نور، زاویه‌های متفاوت، اشیا کوچک، زبان‌های کمترپوشش‌داده‌شده یا ترکیب‌های غیرمعمول می‌توانند نرخ خطای دیگری داشته باشند. میانگین کلی را با breakdownهای مرتبط با task و تحلیل نمونه‌های خطا همراه کنید، بدون اینکه دادهٔ حساس را بی‌دلیل منتشر کنید.

تصویر ممکن است چهره، مکان، سند، پلاک یا دادهٔ زیستی را دربرداشته باشد. پیش از گردآوری/بارگذاری، منشأ، مجوز، مبنای استفاده، رضایت و نگهداری را بررسی کنید؛ از حداقل‌سازی، کنترل دسترسی، حذف امن و روش اعتراض/حذف متناسب استفاده کنید. fixture این فصل فقط بردارهای دستی ساختگی دارد و نه فایل تصویر واقعی؛ بنابراین privacy، حقوق، بی‌طرفی یا امنیت pipeline را نمی‌آزماید.

اگر مدل روی دادهٔ وب پیش‌آموزش دیده باشد، فقط به دلیل در دسترس بودن وزن‌ها، مجوز تصویرهای پایه یا مشتق‌شده روشن نمی‌شود. Model card و dataset card را بخوانید و برای کاربرد/قلمرو حقوقی خود بررسی جدا انجام دهید؛ متن فصل مشاورهٔ حقوقی نیست.

## ۱۸. پژوهش‌های منتخب تا ۶ نوامبر ۲۰۲۶

**SigLIP 2** چندزبانه‌بودن، captioning، خودنظارتی و گزینش داده را در recipe خود ترکیب می‌کند و مقاله ارزیابی‌هایی برای retrieval، localization و ویژگی‌های dense گزارش می‌دهد [۹]. این نتیجه به مجموعهٔ مدل‌ها، داده‌ها، زبان‌ها و پروتکل همان مقاله محدود است؛ «چندزبانه» در عنوان، تضمین عملکرد برابر روی هر زبان نیست.

**DINOv3** Gram anchoring را برای حفظ ویژگی‌های مکانی در پیش‌آموزش طولانی مطرح می‌کند [۷]. **Perception Encoder** امکان مفیدبودن لایه‌های میانی برای embedding را بررسی می‌کند [۸]. هر دو خط پژوهش پرسش متفاوتی دارند: حفظ نمایش مکانی در یادگیری خودنظارتی و انتخاب لایهٔ مناسب برای embedding. این‌ها جایگزین ارزیابی downstream نیستند.

**FineViT** وضوح بومی و captionهای متراکم/محلی را برای ادراک fine-grained بررسی می‌کند؛ **CFM** نمایش مفهوم‌های زبانی و مکانی را هدف می‌گیرد؛ و **VIRTUE** retrieval تعاملی متن–تصویر را با ورودی‌هایی مانند ناحیه/شیء دنبال می‌کند [۱۰–۱۲]. این مقاله‌های تازه ادعاهای نویسندگان دربارهٔ روش و benchmarkهای خود را عرضه می‌کنند؛ نام‌هایی مانند «interpretable» یا «universal» تضمین توضیح‌پذیری، پوشش کامل یا برتری عمومی نیستند.

این مرور چند مسیر منتخب را تا تاریخ بازبینی نشان می‌دهد، نه فهرست کامل ادبیات یا نتیجهٔ رقابتی همهٔ checkpointها. هنگام استفاده، نسخهٔ مقاله، مدل‌کارت، license، preprocessing و عددهای همان benchmark را دوباره بررسی کنید.

## ۱۹. آزمایشگاه CPU فصل: patch contract و retrieval ساختگی

پروژهٔ `book-engineering/projects/51-vision-lab/` چهار کار محدود انجام می‌دهد: grid و token budget را می‌شمارد؛ tensor کوچک `[C,H,W]` را patchify و unpatchify می‌کند؛ loss contrastive دوطرفه را روی embeddingهای ساختگی محاسبه می‌کند؛ و Recall@k/MRR را با relevance تعریف‌شده بر پایهٔ `group_id` گزارش می‌دهد. این کد **ViT کامل یا image encoder آموزش‌دیده نیست**؛ فایل تصویر نمی‌خواند، متن را encode نمی‌کند و checkpoint یا وزن pretrained بارگیری نمی‌کند.

از پوشهٔ پروژه، با Python 3.13 و PyTorch CPU مطابق `requirements.txt` مخزن اجرا کنید:

```bash
cd book-engineering/projects/51-vision-lab
python -m unittest discover -v
python vision_lab.py --mode audit --fixture sample_embeddings.json --output /tmp/ch51-audit
python vision_lab.py --mode demo --fixture sample_embeddings.json --output /tmp/ch51-demo
```

fixture چهار بردار تصویر و چهار بردار متن در بُعد چهار، با چهار `group_id` ساختگی دارد؛ captionها رشته‌های placeholder هستند و فایل تصویر وجود ندارد. در اجرای ثبت‌شده، ۲۶ آزمون موفق شد؛ hash fixture برابر `aba309bb1b3e69443802190b988a21e0432109c01b777f4f58fe11f992936522` بود. audit فقط schema و همسانی گروه‌ها را بررسی کرد.

demo یک tensor ساختگی `3×8×8` را به چهار وصلهٔ ۴۸بعدی تقسیم و دقیق بازسازی کرد. بودجهٔ نظری ViT با patch 16 برای `224×224` برابر ۱۹۶ patch/۱۹۷ token و برای `448×448` برابر ۷۸۴/۷۸۵ بود؛ نسبت جفت‌های توجه در هر head `15.8784` شد. loss مصنوعی `0.00024217297323048115` و Recall@1/MRR هر دو جهت retrieval برابر `1.0` شد؛ fixture عمداً بردارهای جفت‌شدهٔ نزدیک دارد، بنابراین این امتیازها **عملکرد retrieval واقعی نیستند**. هیچ آموزش، مدل، فایل تصویر، دادهٔ واقعی، فارسی، benchmark یا GPU اجرا نشد.

**مرز پروژه:** آزمون‌ها قرارداد helperها و fixture را می‌سنجند، نه کیفیت image encoder، ViT forward pass، image understanding، حقوق/مجوز، privacy، fairness، robustness، latency، انرژی یا تعمیم به دستگاه/زبان واقعی. شرایط، hash، خروجی کامل و محدودیت‌ها در [README پروژه](book-engineering/projects/51-vision-lab/README.md)، `results.json` و [گزارش ممیزی فصل ۵۱](book-engineering/chapters/51-audit-report-fa.md) ثبت می‌شوند.

## ۲۰. تمرین‌ها: از patch تا پروتکل آزمون

۱. تصویر `384×256` با وصلهٔ `16×16` چند patch دارد؟ اگر هر دو بُعد دو برابر شوند، نسبت patchها و جفت‌های attention متراکم—با و بدون token ویژه—چه تغییری می‌کند؟ فرض بخش‌پذیری را روشن بنویسید.

۲. در batch چهار جفت CLIP، چرا سه خانهٔ خارج از قطر هر سطر به‌طور ساده منفی شمرده می‌شوند؟ نمونه‌ای بسازید که این فرض false negative ایجاد کند و یک تغییر داده یا loss پیشنهاد دهید.

۳. یک ViT خروجی `[B,N,d]` دارد. برای retrieval سراسری و segmentation چه اطلاعاتی با pooling میانگین ممکن است از دست برود؟ head طبقه‌بندی و projection متن–تصویر چه نقشی متفاوتی دارند؟

۴. طرح مقایسهٔ encoder منجمد، adapter و fine-tuning را بنویسید. چه چیزهایی را ثابت می‌گیرید؟ از کدام split برای انتخاب روش استفاده می‌کنید و کدام معیارهای هزینه/کیفیت را گزارش می‌دهید؟

۵. سه query داریم: رتبهٔ نخستین نتیجهٔ مرتبط برای query اول ۱، برای دوم ۳، و برای سوم هیچ نتیجهٔ مرتبطی در gallery نیست. اگر سیاست ازپیش‌ثبت‌شده query سوم را برای Recall/MRR از میانگین بیرون بگذارد، Recall@1، Recall@5 و MRR دو query نخست را حساب کنید. چرا باید سیاست نبود مثبت را جدا ثبت کرد؟

۶. برای zero-shot classification با نام کلاس‌های فارسی، چه چیزهایی دربارهٔ prompt، خط و واژه‌های مترادف باید ثابت یا تحلیل شود؟ چرا similarity بالا را احتمال کالیبره‌شدهٔ درست‌بودن نمی‌نامیم؟

۷. یک test تصویر–متن برای جست‌وجوی محصول طراحی کنید که split تصادفی ردیفی نداشته باشد. واحد گروه، منبع تصویر، معیار relevance، queryهای بی‌پاسخ و دو جهت retrieval را مشخص کنید.

۸. DINOv3، SigLIP 2 و Perception Encoder در چه پرسش‌هایی متفاوت‌اند؟ یک نتیجهٔ مقالهٔ تازه را به یک کاربرد محصولی تعمیم ندهید؛ چه شواهد مستقلی لازم دارید؟

**پاسخ‌نامهٔ مستقل:** [پاسخ‌نامهٔ تشریحی فصل ۵۱](book-engineering/answers/51-vision-models-fa.md). **پروژه و مرز اجرا:** [README آزمایشگاه تصویر](book-engineering/projects/51-vision-lab/README.md)؛ **نتایج واقعی و محدودیت‌ها:** [گزارش ممیزی فصل ۵۱](book-engineering/chapters/51-audit-report-fa.md).

## ۲۱. جمع‌بندی: embedding، ناحیه و شاهد

ViT تصویر را به وصله و توالی token تبدیل می‌کند؛ image encoder می‌تواند نمایش وصله‌ای، بردار سراسری یا هر دو را بدهد. وضوح و crop تعداد token و محاسبه را تغییر می‌دهند. در هم‌ترازی contrastive، dual-encoder بردار متن و تصویر را در فضایی مشترک می‌آموزد؛ softmax batch loss یا sigmoid loss فرض‌های متفاوتی دربارهٔ زوج‌ها دارد. caption ناقص، false negative، leakage، provenance و سطحی‌بودن benchmark بر نتیجه اثر می‌گذارند.

برای retrieval، gallery و relevance را تعریف کنید، split گروهی بسازید و هر دو جهت را با Recall@k/MRR و هزینه بسنجید. برای ناحیه یا segmentation، خروجی patch-level و معیار مکانی لازم است؛ score سراسری شاهد موضعی نیست. پروژهٔ فصل فقط tensor کوچک و embeddingهای ساختگی را آزمود. فصل بعد سراغ صوت، نمایش waveform/features، بازشناسی و تولید گفتار می‌رود؛ waveform نیز قرارداد ورودی و ارزیابی مخصوص خود را می‌خواهد.

## ۲۲. منابع و تاریخ بازبینی

منابع در **۶ نوامبر ۲۰۲۶** بازبینی شدند. ادعاهای تجربی فقط به مدل، داده، وظیفه و پروتکل همان مقاله محدودند؛ نقل یک مقاله به معنی بازتولید آن در پروژهٔ این فصل نیست.

۱. Dosovitskiy, A. و همکاران، “An Image is Worth 16×16 Words: Transformers for Image Recognition at Scale,” ICLR 2021, arXiv:2010.11929. <https://arxiv.org/abs/2010.11929>
۲. He, K. و همکاران، “Masked Autoencoders Are Scalable Vision Learners,” CVPR 2022, arXiv:2111.06377. <https://arxiv.org/abs/2111.06377>
۳. Oquab, M. و همکاران، “DINOv2: Learning Robust Visual Features without Supervision,” arXiv:2304.07193، نسخهٔ v2 (۲۰۲۴). <https://arxiv.org/abs/2304.07193>
۴. Radford, A. و همکاران، “Learning Transferable Visual Models From Natural Language Supervision,” ۲۰۲۱, arXiv:2103.00020. <https://arxiv.org/abs/2103.00020>
۵. Zhai, X. و همکاران، “Sigmoid Loss for Language Image Pre-Training,” ICCV 2023, arXiv:2303.15343. <https://arxiv.org/abs/2303.15343>
۶. Gadre, S. Y. و همکاران، “DataComp: In search of the next generation of multimodal datasets,” NeurIPS 2023 Datasets & Benchmarks, arXiv:2304.14108. <https://arxiv.org/abs/2304.14108>
۷. Siméoni, O. و همکاران، “DINOv3,” arXiv:2508.10104، نسخهٔ نخست ۱۳ اوت ۲۰۲۵. <https://arxiv.org/abs/2508.10104>
۸. Bolya, D. و همکاران، “Perception Encoder: The best visual embeddings are not at the output of the network,” arXiv:2504.13181، نسخهٔ v2، ۲۸ آوریل ۲۰۲۵. <https://arxiv.org/abs/2504.13181>
۹. Tschannen, M. و همکاران، “SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features,” arXiv:2502.14786، ۲۰۲۵. <https://arxiv.org/abs/2502.14786>
۱۰. Zhao, H. و همکاران، “FineViT: Progressively Unlocking Fine-Grained Perception with Dense Recaptions,” arXiv:2603.17326، ۱۸ مارس ۲۰۲۶. <https://arxiv.org/abs/2603.17326>
۱۱. Wittenmayer, L. و همکاران، “CFM: Language-aligned Concept Foundation Model for Vision,” arXiv:2601.13798، نسخهٔ v3 مورخ ۲۱ اوت ۲۰۲۶؛ گزارش نویسندگان از پذیرش ECCV 2026 Spotlight. <https://arxiv.org/abs/2601.13798>
۱۲. Wang, Z. و همکاران، “VIRTUE: Visual-Interactive Text-Image Universal Embedder,” arXiv:2510.00523، نسخهٔ v2 مورخ ۲۳ فوریهٔ ۲۰۲۶؛ ICLR 2026. <https://arxiv.org/abs/2510.00523>

## ۲۳. پیوست اجرایی: فایل آزموده‌شدهٔ پروژه

بلوک زیر باید بایت‌به‌بایت با `book-engineering/projects/51-vision-lab/vision_lab.py` برابر بماند؛ سازنده و آزمون مرورگر جلد چهارم همین برابری را کنترل می‌کنند. کد fixture تصویری واقعی یا مدل بارگیری نمی‌کند و خروجی loss/retrieval آن فقط برای آزمودن قراردادهای محاسباتی است.

```python
"""CPU-only vision-patch contracts and synthetic image-text alignment metrics.

This lab does not load pixels from files, a pretrained encoder, or real data.
The vectors and tiny tensor image are fixed educational fixtures only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Sequence

import torch
import torch.nn.functional as F

SOURCE = "synthetic_fixture"


def _positive_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


def _validate_embeddings(embeddings: torch.Tensor, name: str) -> None:
    if not isinstance(embeddings, torch.Tensor) or embeddings.ndim != 2:
        raise ValueError(f"{name} must have shape [items, dimension]")
    if embeddings.shape[0] < 1 or embeddings.shape[1] < 1:
        raise ValueError(f"{name} must have at least one item and one feature")
    if not embeddings.is_floating_point():
        raise ValueError(f"{name} must use a floating-point dtype")
    if not bool(torch.isfinite(embeddings).all()):
        raise ValueError(f"{name} must contain only finite values")
    if bool((torch.linalg.vector_norm(embeddings, dim=-1) <= 1e-12).any()):
        raise ValueError(f"{name} must not contain a zero vector")


def _validate_temperature(temperature: float) -> None:
    if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
        raise ValueError("temperature must be a finite positive number")
    if not math.isfinite(float(temperature)) or float(temperature) <= 0:
        raise ValueError("temperature must be a finite positive number")


def patch_grid(height: int, width: int, patch_size: int) -> tuple[int, int]:
    """Return a non-overlapping patch grid; this helper rejects implicit padding."""
    _positive_int(height, "height")
    _positive_int(width, "width")
    _positive_int(patch_size, "patch_size")
    if height % patch_size or width % patch_size:
        raise ValueError("height and width must be divisible by patch_size; choose and record a padding/crop policy")
    return height // patch_size, width // patch_size


def vit_token_budget(
    height: int,
    width: int,
    patch_size: int,
    *,
    include_class_token: bool = True,
) -> dict[str, int | list[int]]:
    """Count patch/sequence tokens and dense attention score pairs per head."""
    if not isinstance(include_class_token, bool):
        raise ValueError("include_class_token must be bool")
    grid_h, grid_w = patch_grid(height, width, patch_size)
    patch_tokens = grid_h * grid_w
    sequence_tokens = patch_tokens + int(include_class_token)
    return {
        "grid": [grid_h, grid_w],
        "patch_tokens": patch_tokens,
        "sequence_tokens": sequence_tokens,
        "attention_pairs_per_head": sequence_tokens * sequence_tokens,
    }


def patchify(image: torch.Tensor, patch_size: int) -> torch.Tensor:
    """Flatten a [C,H,W] tensor into row-major [patches,C*patch_size**2]."""
    if not isinstance(image, torch.Tensor) or image.ndim != 3:
        raise ValueError("image must have shape [channels,height,width]")
    if not image.is_floating_point() or not bool(torch.isfinite(image).all()):
        raise ValueError("image must be a finite floating-point tensor")
    channels, height, width = image.shape
    if channels < 1:
        raise ValueError("image needs at least one channel")
    grid_h, grid_w = patch_grid(height, width, patch_size)
    patches = image.unfold(1, patch_size, patch_size).unfold(2, patch_size, patch_size)
    return patches.permute(1, 2, 0, 3, 4).reshape(grid_h * grid_w, channels * patch_size * patch_size)


def unpatchify(
    patches: torch.Tensor,
    grid: tuple[int, int],
    channels: int,
    patch_size: int,
) -> torch.Tensor:
    """Invert patchify for a known grid and channel count."""
    if not isinstance(patches, torch.Tensor) or patches.ndim != 2:
        raise ValueError("patches must have shape [patch_count, flattened_patch]")
    if not isinstance(grid, tuple) or len(grid) != 2:
        raise ValueError("grid must be a (rows, columns) tuple")
    grid_h, grid_w = grid
    _positive_int(grid_h, "grid height")
    _positive_int(grid_w, "grid width")
    _positive_int(channels, "channels")
    _positive_int(patch_size, "patch_size")
    if tuple(patches.shape) != (grid_h * grid_w, channels * patch_size * patch_size):
        raise ValueError("patch tensor shape does not match grid, channels, and patch_size")
    return patches.reshape(grid_h, grid_w, channels, patch_size, patch_size).permute(2, 0, 3, 1, 4).reshape(
        channels, grid_h * patch_size, grid_w * patch_size
    )


def normalize_embeddings(embeddings: torch.Tensor) -> torch.Tensor:
    """L2-normalize a batch of nonzero feature vectors."""
    _validate_embeddings(embeddings, "embeddings")
    return F.normalize(embeddings, p=2, dim=-1)


def image_text_logits(
    image_embeddings: torch.Tensor,
    text_embeddings: torch.Tensor,
    temperature: float = 0.07,
) -> torch.Tensor:
    """Return cosine-similarity logits [image_count,text_count] divided by T."""
    _validate_embeddings(image_embeddings, "image_embeddings")
    _validate_embeddings(text_embeddings, "text_embeddings")
    _validate_temperature(temperature)
    if image_embeddings.shape[1] != text_embeddings.shape[1]:
        raise ValueError("image and text embeddings must share the same dimension")
    if image_embeddings.device != text_embeddings.device:
        raise ValueError("image and text embeddings must be on the same device")
    return normalize_embeddings(image_embeddings) @ normalize_embeddings(text_embeddings).transpose(0, 1) / float(temperature)


def symmetric_contrastive_loss(
    image_embeddings: torch.Tensor,
    text_embeddings: torch.Tensor,
    temperature: float = 0.07,
) -> torch.Tensor:
    """Diagonal-positive, symmetric batch-softmax loss for one-to-one pairs."""
    logits = image_text_logits(image_embeddings, text_embeddings, temperature)
    if logits.shape[0] != logits.shape[1]:
        raise ValueError("the diagonal-positive loss requires equal image/text batch sizes")
    if logits.shape[0] < 2:
        raise ValueError("at least two pairs are required; batch size one has no in-batch negative")
    targets = torch.arange(logits.shape[0], device=logits.device)
    return (F.cross_entropy(logits, targets) + F.cross_entropy(logits.transpose(0, 1), targets)) / 2


def retrieval_metrics(
    query_embeddings: torch.Tensor,
    candidate_embeddings: torch.Tensor,
    query_group_ids: Sequence[str],
    candidate_group_ids: Sequence[str],
    ks: Sequence[int] = (1, 5),
) -> dict[str, Any]:
    """Compute cosine retrieval Recall@k and MRR, allowing multiple matches by group."""
    _validate_embeddings(query_embeddings, "query_embeddings")
    _validate_embeddings(candidate_embeddings, "candidate_embeddings")
    if query_embeddings.shape[1] != candidate_embeddings.shape[1]:
        raise ValueError("query and candidate embeddings must share the same dimension")
    if query_embeddings.device != candidate_embeddings.device:
        raise ValueError("query and candidate embeddings must be on the same device")
    if len(query_group_ids) != query_embeddings.shape[0] or len(candidate_group_ids) != candidate_embeddings.shape[0]:
        raise ValueError("group ID counts must match the corresponding embedding counts")
    if not query_group_ids or not candidate_group_ids:
        raise ValueError("query and candidate group IDs must be non-empty")
    if any(not isinstance(group, str) or not group.strip() for group in (*query_group_ids, *candidate_group_ids)):
        raise ValueError("group IDs must be non-empty strings")
    if not ks or any(isinstance(k, bool) or not isinstance(k, int) or k < 1 for k in ks):
        raise ValueError("ks must contain positive integers")

    candidate_indices: dict[str, list[int]] = {}
    for index, group in enumerate(candidate_group_ids):
        candidate_indices.setdefault(group, []).append(index)
    scores = normalize_embeddings(query_embeddings) @ normalize_embeddings(candidate_embeddings).transpose(0, 1)
    ordering = torch.argsort(scores, dim=1, descending=True, stable=True).tolist()
    ranks: list[int] = []
    for query_index, group in enumerate(query_group_ids):
        positives = candidate_indices.get(group)
        if not positives:
            raise ValueError(f"query group {group!r} has no matching candidate")
        position = {candidate_index: rank + 1 for rank, candidate_index in enumerate(ordering[query_index])}
        ranks.append(min(position[candidate_index] for candidate_index in positives))
    return {
        "queries": len(query_group_ids),
        "candidates": len(candidate_group_ids),
        "ranks": ranks,
        "recall_at_k": {str(k): sum(rank <= k for rank in ranks) / len(ranks) for k in sorted(set(ks))},
        "mean_reciprocal_rank": sum(1.0 / rank for rank in ranks) / len(ranks),
    }


def load_fixture(path: str | Path) -> tuple[dict[str, Any], bytes]:
    """Load the tiny JSON fixture and preserve its exact bytes for a checksum."""
    source_bytes = Path(path).read_bytes()
    try:
        payload = json.loads(source_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("fixture must be valid UTF-8 JSON") from exc
    validate_fixture(payload)
    return payload, source_bytes


def validate_fixture(payload: Any) -> tuple[int, int, int]:
    """Check the small synthetic vector-pair contract; this is not image validation."""
    if not isinstance(payload, dict) or payload.get("label_source") != SOURCE:
        raise ValueError("fixture label_source must be 'synthetic_fixture'")
    images, texts = payload.get("images"), payload.get("texts")
    if not isinstance(images, list) or not images or not isinstance(texts, list) or not texts:
        raise ValueError("fixture must contain non-empty image and text lists")
    image_ids: set[str] = set()
    text_ids: set[str] = set()
    image_groups: set[str] = set()
    text_groups: set[str] = set()
    dimension: int | None = None
    for kind, rows, seen_ids, seen_groups in (
        ("image", images, image_ids, image_groups),
        ("text", texts, text_ids, text_groups),
    ):
        for index, row in enumerate(rows, 1):
            if not isinstance(row, dict):
                raise ValueError(f"{kind} row {index} must be an object")
            record_id, group_id, vector = row.get("id"), row.get("group_id"), row.get("embedding")
            if not isinstance(record_id, str) or not record_id.strip() or record_id in seen_ids:
                raise ValueError(f"{kind} row {index} needs a unique non-empty id")
            if not isinstance(group_id, str) or not group_id.strip():
                raise ValueError(f"{kind} row {index} needs a non-empty group_id")
            if row.get("label_source") != SOURCE:
                raise ValueError(f"{kind} row {index} must use the synthetic fixture label")
            if not isinstance(vector, list) or not vector:
                raise ValueError(f"{kind} row {index} needs a non-empty embedding list")
            if dimension is None:
                dimension = len(vector)
            if len(vector) != dimension:
                raise ValueError("all fixture embeddings must have the same dimension")
            try:
                values = [float(value) for value in vector]
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{kind} row {index} has a non-numeric embedding") from exc
            if not all(math.isfinite(value) for value in values) or sum(value * value for value in values) <= 1e-24:
                raise ValueError(f"{kind} row {index} needs finite, nonzero embedding values")
            seen_ids.add(record_id)
            seen_groups.add(group_id)
    if image_groups != text_groups:
        raise ValueError("image and text fixture group IDs must match exactly")
    return len(image_groups), dimension or 0, len(images) + len(texts)


def audit_fixture(payload: dict[str, Any], source_bytes: bytes) -> dict[str, Any]:
    """Summarize the synthetic vector-pair contract without training a model."""
    groups, dimension, rows = validate_fixture(payload)
    return {
        "status": "synthetic_image_text_fixture_audit_complete",
        "image_records": len(payload["images"]),
        "text_records": len(payload["texts"]),
        "groups": groups,
        "embedding_dimension": dimension,
        "label_source": SOURCE,
        "sha256": hashlib.sha256(source_bytes).hexdigest(),
        "training_performed": False,
        "image_files_loaded": False,
        "pretrained_model_loaded": False,
        "model_downloaded": False,
        "device": "cpu",
        "claim_boundary": f"{rows} synthetic vectors only; not image understanding, model quality, or retrieval performance",
    }


def run_demo(payload: dict[str, Any]) -> dict[str, Any]:
    """Exercise patch ordering, token budgets, contrastive loss and retrieval on fixed fixtures."""
    image = torch.arange(3 * 8 * 8, dtype=torch.float32).reshape(3, 8, 8) / 191.0
    patches = patchify(image, patch_size=4)
    reconstructed = unpatchify(patches, (2, 2), channels=3, patch_size=4)
    image_vectors = torch.tensor([row["embedding"] for row in payload["images"]], dtype=torch.float32, requires_grad=True)
    text_vectors = torch.tensor([row["embedding"] for row in payload["texts"]], dtype=torch.float32)
    loss = symmetric_contrastive_loss(image_vectors, text_vectors, temperature=0.1)
    loss.backward()
    i2t = retrieval_metrics(
        image_vectors.detach(), text_vectors,
        [row["group_id"] for row in payload["images"]],
        [row["group_id"] for row in payload["texts"]],
    )
    t2i = retrieval_metrics(
        text_vectors, image_vectors.detach(),
        [row["group_id"] for row in payload["texts"]],
        [row["group_id"] for row in payload["images"]],
    )
    budget_224 = vit_token_budget(224, 224, 16)
    budget_448 = vit_token_budget(448, 448, 16)
    return {
        "status": "synthetic_patch_and_embedding_smoke_test",
        "patch_fixture": {
            "input_shape": list(image.shape),
            "patch_shape": list(patches.shape),
            "reconstruction_exact": bool(torch.equal(image, reconstructed)),
        },
        "vit_token_budget": {"224x224_patch16": budget_224, "448x448_patch16": budget_448},
        "attention_pair_ratio_448_to_224": budget_448["attention_pairs_per_head"] / budget_224["attention_pairs_per_head"],
        "synthetic_symmetric_contrastive_loss": float(loss.detach().item()),
        "image_gradient_is_finite": bool(torch.isfinite(image_vectors.grad).all().item()),
        "image_to_text_retrieval": i2t,
        "text_to_image_retrieval": t2i,
        "training_performed": False,
        "image_files_loaded": False,
        "pretrained_model_loaded": False,
        "model_downloaded": False,
        "device": "cpu",
        "claim_boundary": "fixed 8x8 tensor and synthetic embedding fixture; not a ViT forward pass or a real retrieval evaluation",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline image-patch and alignment-metric lab")
    parser.add_argument("--mode", choices=("audit", "demo"), required=True)
    parser.add_argument("--fixture", type=Path, default=Path(__file__).with_name("sample_embeddings.json"))
    parser.add_argument("--output", type=Path, required=True, help="write JSON report outside the source tree")
    args = parser.parse_args(argv)
    try:
        payload, source_bytes = load_fixture(args.fixture)
        result = audit_fixture(payload, source_bytes) if args.mode == "audit" else run_demo(payload)
        result["python_version"] = sys.version.split()[0]
        result["torch_version"] = torch.__version__
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "run.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

---

# فصل ۵۲: گفتار، مدل‌های صوتی و ارزیابی

**فصل محلی ۶ جلد چهارم = فصل سراسری ۵۲**\
**The Art & Science of Building Intelligence | Babak & Ai**\
**تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶**

> مرز موضوع: فصل ۳۹ اتصال چندمدالیته، waveform، embedding و روش‌های fusion را در یک تصویر کلی معرفی کرد؛ این فصل در چرخهٔ گفتار عمیق می‌شود: قرارداد صوت، بازشناسی گفتار، تولید گفتار، مدل‌های Audio-Language و ارزیابی. فصل ۵۱ دربارهٔ رمزگذار تصویر و متن–تصویر بود؛ فصل ۵۳ تولید تصویر/ویدئو و Diffusion است. این فصل ادعای کیفیت گفتار فارسی یا عملکرد یک مدل خاص را نمی‌کند.

## ۱. خروجی را پیش از انتخاب مدل تعریف کنید

«مدل صوتی» یک وظیفهٔ واحد نیست. اگر هدف را مبهم بگذاریم، ممکن است transcript بخواهیم ولی به embedding صوتی بسنده کنیم؛ یا از مدلِ توصیف صدای محیط انتظار داشته باشیم کلمات گفتار را دقیق بازشناسی کند. دست‌کم چهار پرسش جدا هستند:

1. **بازشناسی گفتار خودکار (ASR):** چه واژه‌هایی گفته شده‌اند؟ خروجی معمولاً متن، گاهی همراه timestamp و برچسب گوینده است.
2. **فهم گفتار:** منظور، پاسخ به سؤال، دستور یا رابطهٔ معنایی چیست؟ پاسخ ممکن است خلاصه یا structured output باشد، نه transcript لفظ‌به‌لفظ.
3. **فهم صوت عمومی:** چه رخداد، موسیقی، زنگ یا صدای محیطی شنیده می‌شود؟ خروجی caption، برچسب یا پاسخ است و لزوماً متنِ گفته‌شده نیست.
4. **تولید گفتار (TTS) و گفت‌وگوی صوتی:** متن/قصد/سبک چگونه به waveform یا توکن صوت تبدیل می‌شود؟ در گفت‌وگوی دوطرفه، سامانه باید هم‌زمان گوش دهد، نوبت را مدیریت کند و پاسخ دهد.

پیش از پیاده‌سازی، «ورودی» و «خروجی» را همراه با زبان، نوع transcript، تأخیر، کیفیت لازم و هزینهٔ خطا بنویسید. مدلِ درست برای فرمان کوتاه در میکروفون نزدیک الزاماً بهترین انتخاب برای مکالمهٔ چندگوینده، صداهای پس‌زمینه یا گفتار بسیار طولانی نیست.

![شکل ۴-۶-۱ — دو مسیر ASR و TTS از waveform تا متن و از متن تا گفتار، همراه با نمایش صوت، مدل Audio-Language و سنجه‌های چندبُعدی؛ نمودار شماتیک است و مدل یا نتیجهٔ آزمون واقعی را نشان نمی‌دهد.](book-engineering/diagrams/v4-ch06-audio.svg)

## ۲. قرارداد waveform: sample rate فقط یک برچسب نیست

موج صوتی دیجیتال دنباله‌ای از دامنه‌هاست. اگر نرخ نمونه‌برداری `fₛ` نمونه در ثانیه و مدت `T` ثانیه باشد، شمار تقریبی sampleها چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="تعداد نمونه برابر نرخ نمونه‌برداری ضرب‌در مدت سیگنال است">
  <mrow><mi>N</mi><mo>=</mo><msub><mi>f</mi><mi>s</mi></msub><mo>·</mo><mi>T</mi></mrow>
</math>

**متن جایگزین فرمول:** `N = f_s × T`؛ برای صدای تک‌کانالهٔ ۱۶ کیلوهرتز و مدت ۵ ثانیه، ۸۰٬۰۰۰ نمونه لازم است.

مثلاً waveform پنج‌ثانیه‌ای با نرخ ۱۶ kHz در یک کانال ۸۰٬۰۰۰ sample دارد؛ stereo در صورت ذخیرهٔ دو کانال ۱۶۰٬۰۰۰ مقدار دارد. فرکانس‌های بالاتر از نصف نرخ نمونه‌برداری، بدون فیلتر پیش از نمونه‌برداری، می‌توانند alias شوند:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="فرکانس Nyquist برابر نصف نرخ نمونه‌برداری است">
  <mrow><msub><mi>f</mi><mtext>Nyquist</mtext></msub><mo>=</mo><mfrac><msub><mi>f</mi><mi>s</mi></msub><mn>2</mn></mfrac></mrow>
</math>

**متن جایگزین فرمول:** `f_Nyquist = f_s / 2`؛ این مرز نظری نمونه‌برداری است، نه تضمین کیفیت ضبط یا frontend مدل.

نکتهٔ عملی: اگر فایل ۴۸ kHz را به مدلی با قرارداد ۱۶ kHz بدهید، صرفاً metadata را از «۴۸» به «۱۶» تغییر ندهید. **Resampling** باید نمونه‌های تازه را از سیگنال پیوستهٔ تقریبی برآورد کند و در downsampling فیلتر ضد-alias داشته باشد. تغییر عدد metadata بدون resampling، زمان و pitch مؤثر را عوض می‌کند.

## ۳. از نمونه به ویژگی: پنجره، گام و نمایش زمان–فرکانس

طول یک گفتار معمولاً از چند صد هزار نمونه بیشتر است؛ پردازش در پنجره‌های کوتاه امکان دیدن تغییرات فرکانسی در طول زمان را می‌دهد. اگر طول پنجره `L` و فاصلهٔ شروع پنجره‌ها `H` باشد، پنجره‌ها می‌توانند هم‌پوشانی داشته باشند. STFT برای هر پنجره ضرایب فرکانسی را محاسبه می‌کند:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="تبدیل فوریهٔ کوتاه‌زمان روی پنجرهٔ m، جمع نمونه‌های پنجره‌شده با نمای مختلط است">
  <mrow>
    <msub><mi>X</mi><mi>m</mi></msub><mo>(</mo><mi>k</mi><mo>)</mo><mo>=</mo>
    <munderover><mo>∑</mo><mrow><mi>n</mi><mo>=</mo><mn>0</mn></mrow><mrow><mi>L</mi><mo>−</mo><mn>1</mn></mrow></munderover>
    <mi>x</mi><mo>[</mo><mi>n</mi><mo>+</mo><mi>mH</mi><mo>]</mo>
    <mi>w</mi><mo>[</mo><mi>n</mi><mo>]</mo>
    <msup><mi>e</mi><mrow><mo>−</mo><mi>j</mi><mn>2</mn><mi>π</mi><mi>kn</mi><mo>/</mo><mi>N</mi></mrow></msup>
  </mrow>
</math>

**متن جایگزین فرمول:** در پنجرهٔ زمانی `m`، نمونه‌های `x[n+mH]` در پنجرهٔ `w[n]` ضرب و برای bin فرکانسی `k` جمع می‌شوند؛ مقدارهای `L`، `H` و `N` جزو قرارداد preprocessing هستند.

**Log-Mel** پس از ساخت طیف، توان را روی فیلترهایی با فاصله‌بندی Mel جمع و معمولاً لگاریتم می‌گیرد. این ویژگی‌ها ورودی رایجی برای برخی مدل‌ها هستند، اما همهٔ گفتارمدل‌ها Mel یکسان، تعداد bin یکسان یا نرخ نمونهٔ یکسان ندارند. [۲] برای نمونه، مقالهٔ Whisper ورودی طیف log-Mel با تعداد bin مشخص خود را توصیف می‌کند؛ همان تنظیم را به همهٔ معماری‌ها تعمیم ندهید.

## ۴. مشخصات ورودی باید کنار checkpoint بماند

برای هر درخواست یا نمونهٔ آموزشی این metadata را نگه دارید: نرخ نمونه‌برداری، تعداد کانال، تعداد sample، مدت، dtype و scale، روش resampling، سیاست تبدیل stereo به mono، میزان clipping، crop و padding، frame/hop، نوع ویژگی و نسخهٔ frontend. شکل تنسور مانند `[B, F, T]` به‌تنهایی این اطلاعات را بیان نمی‌کند.

Normalize کردن دامنه، حذف سکوت، تشخیص گفتار (VAD) و تبدیل stereo به mono ممکن است برای یک pipeline مناسب باشد و برای pipeline دیگر اطلاعات حذف کند. VAD پیش‌پردازش یا ماژولی برای مرزبندی فعالیت صوتی است؛ خودش transcript نیست. اگر ورودی خالی یا خیلی کوتاه است، به‌جای تولید متن ظاهراً مطمئن، رفتار خطا/خروجی خالی را صریح تعریف کنید.

## ۵. نقشهٔ کارهای گفتاری و صوتی

| کار | پرسش | خروجی معمول | آزمون اصلی |
|---|---|---|---|
| ASR | چه گفته شد؟ | واژه، جمله، timestamp | WER/CER و خطای نام/عدد |
| گفتاربه‌متن ترجمه | گفتار در زبان دیگر چه می‌گوید؟ | متن ترجمه‌شده | کیفیت ترجمه و پوشش معنا |
| درک گفتار | پاسخ/قصد/نکته چیست؟ | پاسخ، خلاصه یا ساختار | صحت معنا، شاهد و پیروی از دستور |
| diarization | چه کسی در چه بازه‌ای حرف زد؟ | قطعهٔ زمانی و شناسهٔ گوینده | خطای مرزبندی و گوینده |
| فهم صوت عمومی | چه رخداد یا صدایی وجود دارد؟ | caption یا برچسب | طبقه‌بندی، زمان‌مندی و شاهد |
| TTS | متن چگونه گفته شود؟ | waveform یا token صوت | intelligibility، کیفیت شنیداری و control |
| گفت‌وگوی گفتاری | چه وقت گوش دهیم/پاسخ دهیم؟ | جریان گفتار تعاملی | turn-taking، interruption و latency |

معیار یک ردیف پاسخ ردیف دیگر را اثبات نمی‌کند. مثلاً transcript درست به‌تنهایی طبیعی‌بودن صدای تولیدشده را نمی‌سنجد؛ و caption صوتی خوب لزوماً واژه‌های دقیق گفتار را بازیابی نمی‌کند.

## ۶. مسیر رایج ASR: encoder، alignment و decoder

یک pipeline پایه waveform را به ویژگی‌های زمانی تبدیل می‌کند، encoder نمایش صوتی می‌سازد و decoder توکن‌های متن را پیش‌بینی می‌کند. برای batch، طول‌های متفاوت معمولاً padding می‌شوند؛ mask طول واقعی باید حفظ شود تا padding به‌اشتباه به‌عنوان سکوت یا محتوای صوت وارد attention نشود.

سه خانوادهٔ متداول هدف/رمزگشایی را از هم بشناسید:

- **CTC** روی هر گام زمانی برچسب می‌دهد و احتمال مسیرهای هم‌تراز با transcript را جمع می‌کند؛ blank و collapse توکن‌های تکراری، نیاز به alignment صریح frame/حرف را کم می‌کنند.
- **Transducer / RNN-T** وابستگی به ورودی صوت و پیشوند خروجی را مدل می‌کند و برای رمزگشایی افزایشی طراحی شده است؛ اما streaming بودن به تنهایی تأخیر کم یا کیفیت مناسب را تضمین نمی‌کند.
- **Encoder–decoder autoregressive** با attention متن را شرطی بر نمایش صوت تولید می‌کند. می‌تواند متن بلند و چند وظیفه را یکپارچه کند، ولی هزینهٔ decode و اثر prior زبانی باید آزموده شود.

انتخاب بین این‌ها فقط برچسب معماری نیست. طول context، محدودیت stream، تعداد به‌روزرسانی در ثانیه، حافظه، beam search، tokenizer و روش تقسیم chunk بر نتیجه اثر می‌گذارند.

## ۷. نمایش‌های پیش‌آموخته: از صوت بی‌برچسب تا transcript

wav2vec 2.0 نمایش latent صوت را با پنهان‌کردن بخش‌هایی از ورودی و هدف contrastive یاد می‌گیرد؛ سپس در مقاله با دادهٔ transcript‌دار برای ASR سازگار می‌شود [۱]. این الگو نشان می‌دهد که **پیش‌آموزش بدون transcript** می‌تواند representation مفیدی بسازد، اما آموزش نظارت‌شده و کیفیت دادهٔ آزمون همچنان اهمیت دارند.

Whisper راه دیگری را گزارش کرد: آموزش روی مجموعهٔ بزرگ جفت‌های صوت–متن گردآوری‌شده از وب و یادگیری چندزبانه/چندوظیفه‌ای، سپس ارزیابی انتقالی [۲]. عددها و دستاوردهای مقاله به data curation، توزیع زبان‌ها، decoding و benchmarkهای همان کار وابسته‌اند؛ «چندزبانه» یا «zero-shot» تضمین کیفیت هر زبان، گویش یا محیط نیست.

نمایش‌های صوتی می‌توانند پیوسته باشند یا به کدهای گسسته نگاشت شوند. نوع نمایش، نرخ frame و tokenizer تعیین می‌کنند که مدل چه جزئیاتی را دریافت می‌کند و در هر ثانیه چند گام باید پردازش/تولید کند.

## ۸. Decode و prior زبانی: متن محتمل با متن شنیده‌شده فرق دارد

Greedy decoding، beam search، language model rescoring و تنظیم دما/توقف می‌توانند transcriptها را عوض کنند. prior زبانی ممکن است نام پرتکرار را ترجیح دهد، واژهٔ نادر را جایگزین کند یا روی audio مبهم، کلمه‌ای سازگار ولی شنیده‌نشده بسازد. بنابراین log probability بالا یا متن روان، شاهد کافی برای صحت آکوستیکی نیست.

سناریوهای شکست را جداگانه log کنید: سکوت، گفتار کوتاه، صدای پس‌زمینه، جابه‌جایی زبان، نام خاص، عدد، acronym، گفتار بریده‌شده، repetition، hallucination در سکوت، و خطای VAD. نسخهٔ decoder، prompt زبان، طول chunk و تنظیم beam را همراه مدل ثبت کنید؛ بدون آن مقایسهٔ WER قابل‌بازتولید نیست.

## ۹. Streaming، chunk و زمان‌مندی

در مدل آفلاین، کل فایل پیش از پاسخ موجود است؛ در streaming، صوت تدریجی می‌رسد. Chunk کوچک‌تر ممکن است زمان شروع را کم کند اما context، coarticulation یا مرز جمله را بشکند. Chunk بزرگ‌تر context بیشتری می‌دهد اما حافظه و زمان انتظار را افزایش می‌دهد. overlap، buffer و state بین chunkها را صریح مشخص کنید.

برای ارزیابی streaming، فقط زمان پایان فایل را ثبت نکنید. حداقل زمان اولین خروجی، تأخیر هر chunk، تأخیر end-of-turn، ثبات transcript در بازنگری‌ها، حذف/تکرار مرز chunk، throughput و نسبت زمان اجرا به مدت صوت را گزارش کنید. Timestamp باید با نرخ نمونه و preprocessing سازگار بماند؛ resample/crop می‌تواند رابطهٔ offset و زمان را جابه‌جا کند.

## ۱۰. دادهٔ گفتار: splitter بر اساس گوینده و منبع

یک manifest قابل ممیزی شناسهٔ نمونه، منبع، مجوز/شرایط استفاده، زبان/گویش در حد annotation مجاز، گویندهٔ pseudonymous، شرایط ضبط، نرخ نمونه، متن، timestamp و preprocessing را نگه می‌دارد. فایل خام، transcript و دادهٔ مشتق‌شده را با access و retention جدا مدیریت کنید.

تقسیم تصادفیِ قطعه‌ها می‌تواند صدای یک گوینده یا یک جلسه را هم در train و هم در test بگذارد. برای سنجش تعمیم به گوینده/منبع تازه، split را در سطح مناسب group کنید و near-duplicate را بررسی کنید. توافق annotation، policy نویز، حذف حساسیت‌ها، دادهٔ code-switch و پوشش لهجه را ثبت کنید. این کنترل‌ها کیفیت یا پاکی داده را تضمین نمی‌کنند، اما خطاهای قابل‌کشف را آشکارتر می‌سازند.

## ۱۱. بازشناسی گفتار را چگونه امتیاز بدهیم؟

برای ASR، WER از حداقل تعداد substitution، deletion و insertion در سطح واژه نسبت به تعداد واژه‌های مرجع ساخته می‌شود:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="نرخ خطای واژه برابر مجموع جانشینی، حذف و درج تقسیم بر تعداد واژه‌های مرجع است">
  <mrow><mi>WER</mi><mo>=</mo><mfrac><mrow><mi>S</mi><mo>+</mo><mi>D</mi><mo>+</mo><mi>I</mi></mrow><msub><mi>N</mi><mtext>ref</mtext></msub></mfrac></mrow>
</math>

**متن جایگزین فرمول:** `WER = (S + D + I) / N_ref`؛ صورت تعداد خطاهای ویرایشی و مخرج تعداد واحدهای مرجع است.

WER تجمیعی معمولاً ابتدا شمار خطاها و واژه‌های مرجع را روی کل مجموعه جمع می‌کند و بعد تقسیم می‌کند؛ میانگین سادهٔ درصد هر utterance معیار دیگری است و به نمونه‌های کوتاه وزن بیشتری می‌دهد. WER می‌تواند از ۱۰۰٪ بیشتر شود، چون درج‌ها محدود به طول مرجع نیستند.

## ۱۲. WER در چندزبانگی: normalization را پنهان نکنید

برای مقایسه، باید پیش از scoring سیاست متن را تثبیت کنید: بزرگ/کوچک‌نویسی، نشانه‌گذاری، اعداد، قراردادهای املایی، شکل کوتاه‌شده، tokenization و segmentation. MLPerf برای benchmark گفتار نمونه‌هایی از اثر این تصمیم‌ها و روش normalization را مستند می‌کند [۱۹]. normalization پس از دیدن نتیجه و برای بهترکردن یک مدل، مقایسه را سوگیرانه می‌کند.

CER در سطح نویسه تعریف می‌شود:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="نرخ خطای نویسه برابر مجموع جانشینی، حذف و درج در سطح نویسه تقسیم بر تعداد نویسه‌های مرجع است">
  <mrow><mi>CER</mi><mo>=</mo><mfrac><mrow><msub><mi>S</mi><mi>c</mi></msub><mo>+</mo><msub><mi>D</mi><mi>c</mi></msub><mo>+</mo><msub><mi>I</mi><mi>c</mi></msub></mrow><msub><mi>N</mi><mi>c</mi></msub></mfrac></mrow>
</math>

**متن جایگزین فرمول:** `CER = (S_c + D_c + I_c) / N_c`؛ همهٔ شمارها در واحد نویسهٔ تعریف‌شده‌اند.

در زبان‌هایی با مرز واژهٔ مبهم یا morphology غنی، CER می‌تواند مکمل مفیدی باشد. پژوهش NAACL 2025 با ارزیابی انسانی در Malayalam، English و Arabic استدلال می‌کند که CER در تنظیم خودش با قضاوت انسانی همبستگی بیشتری داشته است [۱۲]. این یافته حکم همگانی نیست: نتیجه به متن نرمال‌شده، script، تعریف «نویسه» و هدف کار وابسته است. برای فارسی، نیم‌فاصله، ک/ك، ی/ي، اعراب و عددها سیاست scoring جدا می‌خواهند؛ CER سادهٔ کد این فصل معیار کیفیت فارسی نیست.

## ۱۳. متن تولیدی فراتر از transcript لفظ‌به‌لفظ

مدل‌های speech-language ممکن است پاسخ سؤال، خلاصه یا transcript بازنویسی‌شده تولید کنند. در این حالت یک transcript مرجع یگانه همیشه همهٔ خروجی‌های درست را پوشش نمی‌دهد؛ اما آزادی بازنویسی می‌تواند hallucination یا جزئیات افزوده را هم پنهان کند.

پیش‌چاپ GSR-Bench در ۳۰ اکتبر ۲۰۲۶، مسئله را به «خروجی معناییِ مستند به صوت» گسترش می‌دهد و سطح‌هایی از transcription لفظی تا ساختاردهی متن را جدا می‌کند [۱۸]. این کار در تاریخ بازبینی هنوز پیش‌چاپ است. درس عمومیِ قابل‌استفاده: برای پاسخ آزاد، معیار exact string را با ارزیابی grounding، unsupported content، پیروی از دستور و بازبینی انسانی تکمیل کنید؛ قضاوت یک LLM به‌تنهایی حقیقت مرجع نیست.

## ۱۴. کارهای گفتاری نزدیک اما متفاوت: ترجمه، درک و diarization

- **گفتاربه‌متن ترجمه** باید هم محتوا را حفظ کند و هم زبان هدف را رعایت کند. WER روی زبان مبدأ به‌تنهایی کیفیت ترجمه را نمی‌سنجد؛ معیارهای ترجمه و ارزیابی انسانی لازم‌اند.
- **Spoken question answering** باید پاسخ را به اطلاعات شنیده‌شده وصل کند. آزمون متن‌محور نمی‌سنجد که ASR چه چیزی را اشتباه شنیده است.
- **Diarization** مرز زمانی و هویت گوینده را تخمین می‌زند؛ ترتیب رفت‌وبرگشت، overlap و speaker error از واژهٔ transcript جدا هستند.
- **Emotion / prosody / voice traits** از ویژگی‌های آکوستیکی استفاده می‌کنند. خروجی متنی ممکن است آن‌ها را حذف یا ساده‌سازی کند؛ transcript زیبا الزاماً شنیدن دقیق نیست.
- **Audio captioning** می‌تواند گفتار و صدای پس‌زمینه را توصیف کند؛ اگر پرسش به timestamp یا منبع صدا نیاز دارد، ارزیابی کلیدیپ کافی نیست.

هر هدف به دادهٔ برچسب‌خورده و معیار خودش نیاز دارد؛ جمع‌کردن چند وظیفه زیر عنوان «درک صوت» آن‌ها را هم‌ارز نمی‌کند.

## ۱۵. ورودی TTS: متن را بدون preprocessing پنهان نکنید

سامانهٔ TTS ابتدا باید متن نوشتاری را به واحدهای قابل‌تلفظ تبدیل کند. اعداد، واحدها، اختصارها، اسم‌ها، punctuation، code-switch و تاریخ می‌توانند چند تلفظ معتبر داشته باشند. Frontend ممکن است text normalization، grapheme-to-phoneme، lexicon، phoneme tokenization و کنترل زبان داشته باشد.

برای مثال `04/05` بدون قرارداد locale می‌تواند تاریخ یا نسبت باشد؛ `Dr.` ممکن است عنوان یا مخفف خوانده شود. متن مرجع و متن TTS را برای ارزیابی، همراه با تلفظ مورد انتظار، نسخهٔ normalizer، لغت‌نامه و زبان ثبت کنید. اگر model output شنیدنی ولی با املای benchmark متفاوت است، اختلاف فقط به مدل نسبت داده نشود.

## ۱۶. معماری تولید: نمایش پیوسته، mel و waveform

در pipeline کلاسیک، مدل duration/alignment را می‌آموزد، ویژگی آکوستیکی مانند Mel را پیش‌بینی می‌کند و vocoder آن را به waveform تبدیل می‌کند. خطا می‌تواند از متن، alignment، prosody، acoustic model یا vocoder بیاید. مدل‌های end-to-end برخی مرزها را یکپارچه می‌کنند؛ این امر اشکال‌زدایی را همیشه ساده‌تر نمی‌کند.

در برخی معماری‌های جدید، مدل به‌جای رگرسیون مستقیم موج، توکن‌های codec را به‌صورت شرطی تولید می‌کند. VALL-E این ایده را به‌عنوان conditional language modeling روی کدهای codec بررسی کرد [۵]. در مدل‌های diffusion یا flow، مسیر تولید/رفع نویز با چند گام و شرایط متن/گوینده صورت می‌گیرد. تفاوت AR، diffusion، flow و vocoder در latency، تعداد مرحله، کنترل‌پذیری و کیفیت خروجی ظاهر می‌شود؛ رتبه‌بندی بدون پروتکل مشترک معنادار نیست.

## ۱۷. Codec و token صوت: فشرده‌سازی مساوی معنا نیست

Neural codec یک encoder/decoder یادگرفتنی دارد که waveform را به نمایش فشرده و قابل‌بازسازی تبدیل می‌کند. SoundStream از quantizer برداری باقیمانده و معماری end-to-end استفاده کرد [۳]؛ EnCodec کیفیت صوت فشرده را با آزمون‌های عینی و شنیداری مطالعه می‌کند [۴]. Tokenizer صوت می‌تواند در هر گام چند codebook داشته باشد؛ rate پایین‌تر، گام‌های autoregressive کمتری می‌دهد ولی trade-off بازسازی، جزئیات و ظرفیت دارد.

«Semantic token» و «acoustic token» همیشه مرز کاملاً جدا ندارند. یک code ممکن است هم اطلاعات واجی، هم timbre/پروسودی را حمل کند. برای ادعا دربارهٔ codec، bitrate، sample rate، codebook count، frame rate، delay، بازسازی waveform و مجموعهٔ آزمون را کنار هم بخوانید. پروژهٔ این فصل codec نمی‌سازد.

## ۱۸. کنترل سبک و صدای مرجع

تولید گفتار می‌تواند با speaker embedding، prompt صوتی، شناسهٔ voice، برچسب سبک یا دستور زبانی شرطی شود. مقایسه کنید چه چیز ثابت می‌ماند: واژه‌ها، گوینده، سرعت، هیجان، زبان یا محیط ضبط. «speaker similarity» برابر طبیعی‌بودن نیست؛ و حفظ timbre تضمین نمی‌کند تلفظ و معنا درست باشند.

Voice cloning از صدای مرجع، حتی در چند ثانیه، می‌تواند انتساب نادرست هویت یا سوءاستفاده بسازد. کیفیتِ تقلید را فقط وقتی بسنجید که رضایت، منشأ فایل، مجوز استفاده و سیاست نگهداری مشخص باشند. کنترل prompt یا watermark ممکن است ریسک را کم کند، اما به‌تنهایی رضایت، اختیار یا استفادهٔ مجاز را اثبات نمی‌کند.

## ۱۹. Cascade در برابر مدل Audio-Language بومی

**Pipeline آبشاری** معمولاً ASR → LLM متنی → TTS است. هر جزء را می‌توان جداگانه عوض/ممیزی کرد و transcript میانی برای debug در دسترس است؛ در عوض خطای ASR به LLM می‌رسد، paralinguistic information ممکن است در متن حذف شود و latency اجزا جمع می‌شود.

**مدل Audio-Language یکپارچه** می‌تواند نمایش صوت را مستقیم به مدل زبانی وصل کند، audio token بخواند/بسازد یا چند stream هم‌زمان را مدل کند. مزیت بالقوه: دسترسی مستقیم به نشانه‌های آکوستیکی و پاسخ گفتاری یکپارچه. هزینه/ریسک: ارزیابی و attribution دشوارتر، توکن‌های پرحجم، کنترل دشوارتر و نیاز به دادهٔ صوتی دقیق‌تر. «End-to-end» یعنی اجزای بیشتری با هم آموزش/اجرا می‌شوند، نه اینکه خطا، bias یا نیاز به audit ناپدید شود.

## ۲۰. نمونه‌های پژوهشی ۲۰۲۴–۲۰۲۶، با مرز ادعا

- Moshi مسیر گفت‌وگوی speech-to-speech و streamهای هم‌زمان را با codec Mimi بررسی می‌کند؛ مقاله برای پیاده‌سازی خودش latency نظری و عملی گزارش می‌دهد [۶]. آن اعداد قابل‌انتقال به دستگاه، backend یا شرایط شبکهٔ دیگر نیستند.
- Qwen3-Omni معماری Thinker–Talker و تولید streaming گفتار در کنار ورودی‌های متن/تصویر/صوت/ویدئو را گزارش می‌کند [۷]. شمار زبان، benchmark و ادعای کیفیت همان گزارش را به یک تضمین برای محصول دلخواه تبدیل نکنید.
- Qwen3-TTS از دو tokenizer گفتار و مسیر autoregressive برای تولید کنترل‌پذیر/streaming گزارش می‌دهد [۸]. latency اولین packet و نتایج چندزبانه به مدل و setup همان مقاله تعلق دارند.
- گزارش Qwen-Audio-3.0-TTS در ۲۰۲۶ معماری چندمرحله‌ای و کنترل متنی/برچسبی را برای تولید گفتار بررسی می‌کند [۹]. مدل‌ها، زبان‌ها و معیارها را پیش از مقایسه با مقالهٔ دیگر هم‌تراز کنید.
- نسخهٔ سوم گزارش StepAudio 3 Realtime تا ۱۲ اکتبر ۲۰۲۶، full-duplex، مدیریت interruption و تولید گفتار هم‌زمان با reasoning را شرح می‌دهد [۱۰]. نمره‌های benchmark خود گزارش نشان‌دهندهٔ برتری در همهٔ کاربردها یا سخت‌افزار محلی نیستند.

این نمونه‌ها نشان می‌دهند که فضای طراحی از ASR یک‌طرفه به streamهای صوت/متن و گفت‌وگوی هم‌زمان گسترش یافته است؛ فهرست کامل مدل‌ها یا ranking ثابت ارائه نمی‌شود.

## ۲۱. طرح ارزیابی: یک score برای همهٔ وظایف وجود ندارد

پروتکل را پیش از اجرای مدل بنویسید: هدف، dataset و نسخه، زبان/گویش، split، normalization، مدل و revision، prompt، decoding، طول/کانال صوت، معیارها، تعداد اجرا و عدم‌قطعیت. آلودگی داده، sampleهای مشابه، selection bias و آزمون انسانی را ثبت کنید. نتیجهٔ benchmark فقط به task و split همان protocol مربوط است.

AudioBench (NAACL 2025) هشت task و ۲۶ dataset را در speech understanding، audio scene و voice understanding دسته‌بندی می‌کند و گزارش می‌دهد که در تنظیم آن، یک مدل در همهٔ taskها برنده نیست [۱۱]. SEA-SpeechBench (مقالهٔ پذیرفته‌شدهٔ EMNLP 2026) مجموعهٔ چندوظیفه‌ای برای ۱۱ زبان آسیای جنوب‌شرقی معرفی می‌کند و شکاف‌هایی را برای task/زبان گزارش می‌دهد [۱۶]. این دو مرجع مثال‌هایی از گسترش ارزیابی‌اند، نه پوشش کامل همهٔ زبان‌ها.

SEA-HELM Audio در پیش‌چاپ اکتبر ۲۰۲۶، نتیجهٔ ورودی صوت را با متن برای چندزبانگی مقایسه می‌کند و «speech gap» را جدا می‌سنجد [۱۷]. این ایده هشدار می‌دهد که benchmark متنی به‌تنهایی رفتار voice agent را پیش‌بینی نمی‌کند. برای محصول، ارزیابی speech-in و text-in را با همان سؤال‌ها، verifierها و splitها مقایسه کنید.

## ۲۲. TTS را با چند بُعد مکمل بسنجید

| بُعد | نمونهٔ سنجه/روش | چه چیزی را به‌تنهایی نمی‌گوید |
|---|---|---|
| intelligibility | transcript با ASR مستقل، WER/CER، بازبینی نمونه | طبیعی‌بودن یا درستی همهٔ واج‌ها |
| naturalness / quality | MOS، MUSHRA یا آزمون شنیداری کنترل‌شده | علت دقیق artifact یا کیفیت همهٔ زبان‌ها |
| speaker similarity | مدل embedding گوینده و مقایسهٔ انسانی | رضایت، هویت قانونی یا طبیعی‌بودن |
| prosody / style | F0، duration، rubric برای کنترل دستور | درک انسانی از لحن در همهٔ فرهنگ‌ها |
| acoustic artifacts | سیگنال‌متریک و آزمون گوش‌دادن | درستی واژه و تناسب لحن |
| streaming | first-packet، chunk delay، RTF و ثبات بلندمدت | کیفیت مکالمه یا حریم خصوصی |

TTSDS2 در ICLR 2026، benchmark چندزبانه و metric توزیعی را در کنار مجموعه‌ای از ratings انسانی معرفی می‌کند [۱۳]. پژوهش «Beyond Naturalness» (پذیرفته‌شده در EMNLP 2026) می‌سنجد که ارزیاب‌های MOS و Audio-LLM تا چه حد ابعاد زبانی/آکوستیکی مختلف را می‌گیرند و گزارش می‌دهد که هیچ‌یک دامنهٔ کامل خطا را پوشش نمی‌دهند [۱۴]. بنابراین MOS خودکار، WER با ASR، speaker embedding یا یک judge زبانی را به‌تنهایی معادل قضاوت شنونده نگیرید.

## ۲۳. آکوستیک غیرواژگانی و زمان‌مندی را هم بسنجید

مدل ممکن است واژه‌ها را درست بگیرد ولی زیر و بمی، مکث، گوینده یا صدای پس‌زمینه را اشتباه تشخیص دهد. VocalGrad (پیش‌چاپ NeurIPS 2026) تغییرات کنترل‌شدهٔ آکوستیکی را از استدلال واژگانی جدا می‌کند و برای مدل‌های بررسی‌شده محدودیت‌هایی گزارش می‌دهد [۱۵]. این نتیجه ادعای عملکرد همهٔ Audio-Language modelها نیست؛ ارزش روش‌شناختی آن جداسازی «شنیدن ویژگی آکوستیکی» از «دانستن پاسخ زبانی» است.

برای هر task، آزمون‌هایی بسازید که acoustic cue را نگه دارند و transcript/معنا را تغییر ندهند، یا برعکس؛ سپس ببینید مدل کدام را دنبال می‌کند. برای timestamp، ثبت واحد زمانی و tolerance؛ برای speaker، آزمون‌های هم‌پوشانی و تغییر میکروفون؛ برای emotion/style، برچسب انسانی و توافق annotator؛ برای متن، معیار transcript. اگر یک utterance چند هدف دارد، نتیجهٔ هر هدف جدا بماند.

## ۲۴. latency و full-duplex را به اجزای واقعی بشکنید

Real-Time Factor را به‌شکل زمان اجرای محاسبه‌شده نسبت به مدت صوت تعریف کنید:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="عامل زمان واقعی برابر زمان اجرا تقسیم بر مدت صوت است">
  <mrow><mi>RTF</mi><mo>=</mo><mfrac><msub><mi>t</mi><mtext>wall</mtext></msub><msub><mi>T</mi><mtext>audio</mtext></msub></mfrac></mrow>
</math>

**متن جایگزین فرمول:** `RTF = t_wall / T_audio`؛ قرارداد اندازه‌گیری و مسیر اجرا را باید کنار عدد بنویسید.

RTF کمتر از یک فقط می‌گوید آن run در آن setup سریع‌تر از مدت ورودی تمام شده است؛ تأخیر شروع، صف، شبکه، VAD و buffering ممکن است همچنان نامناسب باشد. برای مکالمه، first-packet latency، time-to-first-token، pause handling، turn taking، backchannel، interruption و end-of-turn را جدا بسنجید.

Full-duplex یعنی سامانه در زمان گفتارِ کاربر می‌تواند هم گوش دهد و هم در صورت نیاز گفتار تولید کند؛ مدیریت نوبت، لغو/اصلاح گفته و ادامهٔ پاسخ را باید در protocol مدل کنید. Benchmarkهای full-duplex با benchmark ASR یا MOS یکی نیستند.

## ۲۵. ایمنی، رضایت و دادهٔ صوتی

صوت می‌تواند واژه، گوینده، محل، سلامت یا شرایط خصوصی را آشکار کند. دسترسی به فایل خام، مدت نگهداری، حذف، ثبت log و انتقال به سرویس را محدود کنید. برای صدای مرجع، speaker adaptation و voice cloning، رضایت روشن و provenance نگه دارید و سناریوی سوءاستفاده/جعل هویت را ارزیابی کنید. مدل‌کارت و مجوز checkpoint، مجوز ضبط یا رضایت گوینده را ثابت نمی‌کند.

در محصولات حساس، ASR باید در برابر سکوت/نویز، prompt-injection صوتی، false activation، اشتباه در نام/عدد و نابرابری لهجه آزموده شود. خروجی برای عمل پرهزینه یا برگشت‌ناپذیر را با تأیید انسان یا محدودیت دامنه کنترل کنید. این فصل راهنمای حقوقی یا تضمین حریم خصوصی نیست؛ الزامات واقعی به نوع داده، محل استفاده و قرارداد بستگی دارند.

## ۲۶. آزمایشگاه CPU فصل: قرارداد پنجره و خطای متن

پروژهٔ `projects/52-audio-lab/` دو مسئلهٔ کوچک را از هم جدا می‌کند:

1. درون حافظه یک سینوس ۴۴۰ Hz با نرخ ۱۶ kHz ساخته می‌شود و با پنجرهٔ ۲۵ ms و گام ۱۰ ms به frame و طیف DFT ساده تبدیل می‌شود.
2. fixture سه جفت متنِ ساختگی دارد؛ برنامه WER/CER و اختلاف بین WER تجمیعی corpus و میانگین WER جمله‌ای را محاسبه می‌کند.

فایل‌های fixture، آزمون و نتیجه فقط با Python standard library اجرا می‌شوند. نمونهٔ ورودی، audio یا خروجی ASR ندارد. دستورهای اجرا و نتایج در [README پروژه](book-engineering/projects/52-audio-lab/README.md) آمده‌اند؛ پاسخ تمرین‌ها در [پاسخ‌نامهٔ فصل ۵۲](book-engineering/answers/52-audio-models-fa.md) است.

در اجرای ثبت‌شده، ۱۰۰ ms سینوس ۱۶٬۰۰۰ sample داشت و ۸ frame کامل ساخته شد. WER تجمیعی روی ۱۱ واژهٔ مرجع `3/11 = 0.2727272727272727` و میانگین جمله‌ای `0.21666666666666667` شد. این اعداد صحت پیاده‌سازی metric در fixture را نشان می‌دهند، نه کیفیت گفتار یا مدل.

## ۲۷. تمرین‌ها

1. waveform تک‌کانالهٔ ۲۴ kHz با مدت ۷٫۵ ثانیه چند sample دارد؟ اگر به‌اشتباه فقط sample rate metadata را ۱۶ kHz کنید، چه خطایی رخ می‌دهد؟
2. یک ثانیه صوت با window برابر ۲۵ ms و hop برابر ۱۰ ms چند frame کاملِ بدون padding می‌دهد؟ قرارداد مرز آخر را توضیح دهید.
3. در `reference = "turn left at the bridge"` و `hypothesis = "turn right at bridge"`، تعداد substitution/deletion/insertion و WER را به‌دست آورید.
4. چرا corpus WERِ سه utterance الزاماً برابر میانگین سادهٔ WER هر utterance نیست؟ برای هر انتخاب چه سؤال آماری/محصولی مطرح است؟
5. در فارسی، سه انتخاب normalization را مثال بزنید که می‌تواند WER/CER را تغییر دهد. چه نسخه‌ای را پیش‌ثبت می‌کنید؟
6. یک نمونهٔ ASR خام و یک پاسخ spoken-QA مدل بسازید که هر دو از یک فایل باشند ولی معیار مناسبشان متفاوت باشد. دلیل را بنویسید.
7. برای TTS سه معیار مکمل انتخاب کنید که به‌ترتیب intelligibility، naturalness و speaker identity را هدف بگیرند؛ محدودیت هر یک را هم ذکر کنید.
8. برای گفت‌وگوی full-duplex، سناریویی با مکث، backchannel و interruption طراحی کنید؛ eventها، timestampها و success condition را تعریف کنید.
9. طرح split بدهید که یک گوینده و جلسه میان train/test نشت نکنند؛ provenance، مجوز و retention را نیز ثبت کنید.
10. پروژه را اجرا کنید و تعداد frame، peak bin، WER تجمیعی و macro-WER را با خروجی ثبت‌شده مقایسه کنید. سپس بنویسید کدام نتیجه دربارهٔ ASR یا فارسی از آن **قابل استنتاج نیست**.

## ۲۸. جمع‌بندی و مسیر ادامه

گفتار یک waveform زمان‌مند است؛ contract نمونه‌برداری و frontend در ورودی اثر دارد، نمایش latent یا codec اطلاعات را فشرده می‌کند، decoder خروجی متن یا audio token را می‌سازد، و evaluation باید همان task را هدف بگیرد. ASR، TTS، spoken QA، audio captioning و full-duplex interaction را با یک معیار نسنجید.

در ASR، normalization و corpus aggregation را ثبت کنید؛ CER می‌تواند مکمل WER باشد، نه حکم واحد برای همهٔ زبان‌ها. در TTS، intelligibility، کیفیت شنیداری، speaker similarity، prosody، style control و streaming را جدا ببینید. در Audio-Language مدل‌ها، متن میانی، audio token و جریان گفت‌وگو مصالحه‌های متفاوتی دارند. پیش از deployment، provenance، رضایت، privacy و شکست‌های گروهی را با دادهٔ مجاز و split مستقل ارزیابی کنید.

فصل بعدی در نقشه فصل ۵۳ است: تولید تصویر و ویدئو و Diffusion؛ آن فصل خروجی تصویری/ویدئویی را از تولید گفتار این فصل جدا می‌کند.

## منابع و تاریخ بازبینی

مراجعه و بازبینی: **۶ نوامبر ۲۰۲۶**. ادعاهای تجربی به داده، مدل، نسخه و پروتکل همان منبع محدودند؛ تازه‌بودن فهرست به معنای پوشش کامل ادبیات نیست.

1. Baevski et al., “wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations,” NeurIPS 2020, [arXiv:2006.11477](https://arxiv.org/abs/2006.11477).
2. Radford et al., “Robust Speech Recognition via Large-Scale Weak Supervision,” 2022, [arXiv:2212.04356](https://arxiv.org/abs/2212.04356).
3. Zeghidour et al., “SoundStream: An End-to-End Neural Audio Codec,” 2021, [arXiv:2107.03312](https://arxiv.org/abs/2107.03312).
4. Défossez et al., “High Fidelity Neural Audio Compression,” 2022, [arXiv:2210.13438](https://arxiv.org/abs/2210.13438).
5. Wang et al., “Neural Codec Language Models are Zero-Shot Text to Speech Synthesizers,” 2023, [arXiv:2301.02111](https://arxiv.org/abs/2301.02111).
6. Défossez et al., “Moshi: a speech-text foundation model for real-time dialogue,” arXiv v2, 2 October 2024, [arXiv:2410.00037](https://arxiv.org/abs/2410.00037).
7. Xu et al., “Qwen3-Omni Technical Report,” 2025, [arXiv:2509.17765](https://arxiv.org/abs/2509.17765).
8. Hu et al., “Qwen3-TTS Technical Report,” 2026, [arXiv:2601.15621](https://arxiv.org/abs/2601.15621).
9. Xiang et al., “Qwen-Audio-3.0-TTS: Freely Controllable and Highly Robust Speech Synthesis with Multi-Stage Training Paradigm,” 2026, [arXiv:2607.23938](https://arxiv.org/abs/2607.23938).
10. StepFun-Audio Team, “StepAudio 3 Realtime Technical Report,” arXiv v3, 12 October 2026, [arXiv:2609.14005](https://arxiv.org/abs/2609.14005).
11. Wang et al., “AudioBench: A Universal Benchmark for Audio Large Language Models,” NAACL 2025, DOI [10.18653/v1/2025.naacl-long.218](https://doi.org/10.18653/v1/2025.naacl-long.218), [ACL Anthology](https://aclanthology.org/2025.naacl-long.218/).
12. Thennal D K et al., “Advocating Character Error Rate for Multilingual ASR Evaluation,” Findings of NAACL 2025, pp. 4941–4950, DOI [10.18653/v1/2025.findings-naacl.277](https://doi.org/10.18653/v1/2025.findings-naacl.277), [ACL Anthology](https://aclanthology.org/2025.findings-naacl.277/).
13. Minixhofer, Klejch & Bell, “TTSDS2: Resources and Benchmark for Evaluating Human-Quality Text to Speech Systems,” ICLR 2026 Oral, [OpenReview](https://openreview.net/forum?id=uGai5lYHlV).
14. Bamgbose et al., “Beyond Naturalness: Probing Automated Text-To-Speech Evaluators on Linguistically Grounded Dimensions,” arXiv v2, accepted EMNLP 2026, [arXiv:2608.09930](https://arxiv.org/abs/2608.09930).
15. Ryu & Yanaka, “VocalGrad: Evaluating Acoustic Perception in Audio Language Models,” arXiv:2610.23745, NeurIPS 2026 Evaluations & Datasets Track, [arXiv](https://arxiv.org/abs/2610.23745).
16. Liao et al., “SEA-SpeechBench: A Large-Scale Multitask Benchmark for Speech Understanding Across Southeast Asia,” arXiv:2609.09672, accepted EMNLP 2026, [arXiv](https://arxiv.org/abs/2609.09672).
17. Adila et al., “SEA-HELM Audio: Evaluating Multilingual ASR-LLM Pipeline Performance Across SEA-HELM Subsets,” arXiv v2, 16 October 2026, [arXiv:2610.19869](https://arxiv.org/abs/2610.19869).
18. Wang et al., “From Transcription to Reformulation: Defining and Benchmarking Grounded Generative Speech Recognition,” arXiv v1, 30 October 2026, [arXiv:2610.41292](https://arxiv.org/abs/2610.41292). در تاریخ بازبینی، این کار پیش‌چاپ است.
19. MLCommons, “Whisper: An MLPerf Inference Benchmark for Automatic Speech Recognition (ASR),” 9 September 2025, [MLCommons](https://mlcommons.org/2025/09/whisper-inferencev5-1/).

## ۲۹. پیوست اجرایی: کد کامل پروژه

فایل زیر همان کدی است که در `projects/52-audio-lab/audio_lab.py` آزموده می‌شود. آزمون‌ها و ورودی fixture در همان پوشه‌اند.

```python
"""Small, standard-library-only audio framing and transcript-metric fixtures.

This is not an ASR, TTS, codec, or audio-language model. It generates one
analytic sine tone for framing/spectrum demonstrations and scores synthetic
text pairs to test evaluation code paths.
"""
from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
import platform
import sys
import unicodedata
from pathlib import Path
from typing import Iterable, Mapping, Sequence

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_FIXTURE = PROJECT_DIR / "sample_transcripts.json"


def validate_signal(samples: Sequence[float], sample_rate: int) -> None:
    if isinstance(sample_rate, bool) or not isinstance(sample_rate, int) or sample_rate <= 0:
        raise ValueError("sample_rate must be a positive integer in samples per second")
    if isinstance(samples, (str, bytes)) or not isinstance(samples, Sequence) or not samples:
        raise ValueError("samples must be a non-empty numeric sequence")
    for index, sample in enumerate(samples):
        if isinstance(sample, bool) or not isinstance(sample, (int, float)) or not math.isfinite(float(sample)):
            raise ValueError(f"sample {index} must be a finite number")


def make_synthetic_tone(
    sample_rate: int = 16_000,
    duration_ms: int = 100,
    frequency_hz: float = 440.0,
    amplitude: float = 0.5,
) -> list[float]:
    if isinstance(sample_rate, bool) or not isinstance(sample_rate, int) or sample_rate <= 0:
        raise ValueError("sample_rate must be a positive integer")
    if isinstance(duration_ms, bool) or not isinstance(duration_ms, int) or duration_ms <= 0:
        raise ValueError("duration_ms must be a positive integer")
    if not math.isfinite(frequency_hz) or not 0 < frequency_hz < sample_rate / 2:
        raise ValueError("frequency_hz must be finite and strictly below Nyquist")
    if not math.isfinite(amplitude) or not 0 < amplitude <= 1:
        raise ValueError("amplitude must be finite and in (0, 1]")
    sample_count = sample_rate * duration_ms // 1_000
    if sample_count <= 0:
        raise ValueError("duration is shorter than one sample")
    return [
        amplitude * math.sin(2.0 * math.pi * frequency_hz * index / sample_rate)
        for index in range(sample_count)
    ]


def frame_signal(
    samples: Sequence[float],
    sample_rate: int,
    frame_ms: float = 25.0,
    hop_ms: float = 10.0,
    *,
    pad_end: bool = False,
) -> list[list[float]]:
    validate_signal(samples, sample_rate)
    if not math.isfinite(frame_ms) or frame_ms <= 0:
        raise ValueError("frame_ms must be finite and positive")
    if not math.isfinite(hop_ms) or hop_ms <= 0:
        raise ValueError("hop_ms must be finite and positive")
    if not isinstance(pad_end, bool):
        raise ValueError("pad_end must be a bool")
    frame_length = round(sample_rate * frame_ms / 1_000)
    hop_length = round(sample_rate * hop_ms / 1_000)
    if frame_length <= 0 or hop_length <= 0:
        raise ValueError("frame_ms and hop_ms must each span at least one sample")

    values = [float(sample) for sample in samples]
    if pad_end:
        starts = range(0, len(values), hop_length)
    else:
        if len(values) < frame_length:
            return []
        starts = range(0, len(values) - frame_length + 1, hop_length)

    frames: list[list[float]] = []
    for start in starts:
        frame = values[start : start + frame_length]
        if len(frame) < frame_length:
            if not pad_end:
                break
            frame.extend([0.0] * (frame_length - len(frame)))
        frames.append(frame)
    return frames


def root_mean_square(samples: Sequence[float]) -> float:
    if not samples:
        raise ValueError("RMS requires at least one sample")
    if any(not math.isfinite(float(sample)) for sample in samples):
        raise ValueError("RMS samples must be finite")
    return math.sqrt(math.fsum(float(sample) ** 2 for sample in samples) / len(samples))


def hann_window(length: int) -> list[float]:
    if isinstance(length, bool) or not isinstance(length, int) or length <= 0:
        raise ValueError("window length must be a positive integer")
    if length == 1:
        return [1.0]
    return [0.5 - 0.5 * math.cos(2.0 * math.pi * index / (length - 1)) for index in range(length)]


def single_sided_power_spectrum(
    frame: Sequence[float], sample_rate: int, n_fft: int | None = None
) -> list[float]:
    validate_signal(frame, sample_rate)
    if n_fft is None:
        n_fft = len(frame)
    if isinstance(n_fft, bool) or not isinstance(n_fft, int) or n_fft <= 0:
        raise ValueError("n_fft must be a positive integer")
    if n_fft < len(frame):
        raise ValueError("n_fft cannot be shorter than the input frame")
    window = hann_window(len(frame))
    weighted = [float(sample) * weight for sample, weight in zip(frame, window)]
    scale = float(n_fft * n_fft)
    power: list[float] = []
    for bin_index in range(n_fft // 2 + 1):
        coefficient = sum(
            (weighted[index] * cmath.exp(-2j * math.pi * bin_index * index / n_fft)
             for index in range(len(weighted))),
            0j,
        )
        power.append((coefficient.real * coefficient.real + coefficient.imag * coefficient.imag) / scale)
    return power


def normalize_words(text: str) -> list[str]:
    if not isinstance(text, str):
        raise TypeError("transcript must be a string")
    return unicodedata.normalize("NFC", text).casefold().split()


def normalize_characters(text: str) -> list[str]:
    if not isinstance(text, str):
        raise TypeError("transcript must be a string")
    normalized = unicodedata.normalize("NFC", text).casefold()
    return [character for character in normalized if not character.isspace()]


def edit_counts(reference: Sequence[str], hypothesis: Sequence[str]) -> dict[str, int]:
    """Return one minimum-edit alignment with deterministic tie-breaking.

    Ties prefer substitution, then deletion, then insertion. The total edit
    distance is the Levenshtein distance; operation-level counts can differ
    between equally short alignments.
    """
    rows, columns = len(reference), len(hypothesis)
    distance = [[0] * (columns + 1) for _ in range(rows + 1)]
    back = [[""] * (columns + 1) for _ in range(rows + 1)]
    for row in range(1, rows + 1):
        distance[row][0] = row
        back[row][0] = "D"
    for column in range(1, columns + 1):
        distance[0][column] = column
        back[0][column] = "I"

    priority = {"S": 0, "D": 1, "I": 2}
    for row in range(1, rows + 1):
        for column in range(1, columns + 1):
            if reference[row - 1] == hypothesis[column - 1]:
                distance[row][column] = distance[row - 1][column - 1]
                back[row][column] = "M"
            else:
                candidates = [
                    (distance[row - 1][column - 1] + 1, "S"),
                    (distance[row - 1][column] + 1, "D"),
                    (distance[row][column - 1] + 1, "I"),
                ]
                distance[row][column], back[row][column] = min(
                    candidates, key=lambda item: (item[0], priority[item[1]])
                )

    substitutions = deletions = insertions = 0
    row, column = rows, columns
    while row or column:
        operation = back[row][column]
        if operation == "M":
            row -= 1
            column -= 1
        elif operation == "S":
            substitutions += 1
            row -= 1
            column -= 1
        elif operation == "D":
            deletions += 1
            row -= 1
        elif operation == "I":
            insertions += 1
            column -= 1
        else:
            raise RuntimeError("could not trace edit alignment")
    return {
        "substitutions": substitutions,
        "deletions": deletions,
        "insertions": insertions,
        "edit_distance": substitutions + deletions + insertions,
    }


def _rate_stats(reference: Sequence[str], hypothesis: Sequence[str]) -> dict[str, int | float]:
    if not reference:
        raise ValueError("error rate is undefined for an empty reference")
    counts = edit_counts(reference, hypothesis)
    total = counts["substitutions"] + counts["deletions"] + counts["insertions"]
    return {
        **counts,
        "reference_units": len(reference),
        "error_rate": total / len(reference),
    }


def word_error_stats(reference: str, hypothesis: str) -> dict[str, int | float]:
    return _rate_stats(normalize_words(reference), normalize_words(hypothesis))


def character_error_stats(reference: str, hypothesis: str) -> dict[str, int | float]:
    return _rate_stats(normalize_characters(reference), normalize_characters(hypothesis))


def corpus_word_error_stats(records: Sequence[Mapping[str, str]]) -> dict[str, int | float]:
    if not records:
        raise ValueError("at least one transcript pair is required")
    combined = {"substitutions": 0, "deletions": 0, "insertions": 0, "reference_units": 0}
    for record in records:
        stats = word_error_stats(record["reference"], record["hypothesis"])
        for key in combined:
            combined[key] += int(stats["reference_units"] if key == "reference_units" else stats[key])
    errors = combined["substitutions"] + combined["deletions"] + combined["insertions"]
    combined["edit_distance"] = errors
    combined["error_rate"] = errors / combined["reference_units"]
    return combined


def sentence_macro_word_error_rate(records: Sequence[Mapping[str, str]]) -> float:
    if not records:
        raise ValueError("at least one transcript pair is required")
    return math.fsum(
        float(word_error_stats(record["reference"], record["hypothesis"])["error_rate"])
        for record in records
    ) / len(records)


def load_fixture(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("fixture root must be a JSON object")
    metadata = payload.get("metadata")
    records = payload.get("records")
    if not isinstance(metadata, dict) or metadata.get("fixture_kind") != "synthetic_transcript_examples":
        raise ValueError("fixture must identify itself as synthetic transcript examples")
    if metadata.get("audio_recordings_included") is not False:
        raise ValueError("fixture must explicitly state that no audio recordings are included")
    if metadata.get("model_outputs_included") is not False:
        raise ValueError("fixture must explicitly state that no model outputs are included")
    if not isinstance(records, list) or not records:
        raise ValueError("fixture must contain at least one transcript record")
    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"record {index} must be an object")
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in seen:
            raise ValueError(f"record {index} must have a unique, non-empty id")
        seen.add(identifier)
        if record.get("label_source") != "synthetic_fixture":
            raise ValueError(f"record {identifier} is not marked as a synthetic fixture")
        if not isinstance(record.get("reference"), str) or not isinstance(record.get("hypothesis"), str):
            raise ValueError(f"record {identifier} must contain string reference and hypothesis fields")
        if not normalize_words(record["reference"]):
            raise ValueError(f"record {identifier} has an empty reference transcript")
    return payload


def audit_fixture(path: Path) -> dict:
    payload = load_fixture(path)
    return {
        "status": "synthetic_transcript_fixture_audit_complete",
        "training_performed": False,
        "audio_recordings_loaded": False,
        "speech_model_loaded": False,
        "model_downloaded": False,
        "device": "cpu",
        "fixture": {
            "path": "sample_transcripts.json",
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "records": len(payload["records"]),
            "audio_recordings_included": False,
            "model_outputs_included": False,
            "label_source": "synthetic_fixture",
        },
    }


def run_demo(path: Path) -> dict:
    audit = audit_fixture(path)
    payload = load_fixture(path)
    records = payload["records"]

    sample_rate = 16_000
    tone = make_synthetic_tone(sample_rate=sample_rate, duration_ms=100, frequency_hz=440.0)
    frames = frame_signal(tone, sample_rate, frame_ms=25.0, hop_ms=10.0, pad_end=False)
    spectrum = single_sided_power_spectrum(frames[0], sample_rate)
    peak_bin = max(range(len(spectrum)), key=spectrum.__getitem__)
    word_metrics = corpus_word_error_stats(records)
    character_metrics = {
        "substitutions": 0,
        "deletions": 0,
        "insertions": 0,
        "reference_units": 0,
    }
    for record in records:
        stats = character_error_stats(record["reference"], record["hypothesis"])
        for key in character_metrics:
            character_metrics[key] += int(stats["reference_units"] if key == "reference_units" else stats[key])
    character_errors = (
        character_metrics["substitutions"]
        + character_metrics["deletions"]
        + character_metrics["insertions"]
    )
    character_metrics["edit_distance"] = character_errors
    character_metrics["error_rate"] = character_errors / character_metrics["reference_units"]

    per_record = []
    for record in records:
        per_record.append({
            "id": record["id"],
            "wer": word_error_stats(record["reference"], record["hypothesis"]),
            "cer": character_error_stats(record["reference"], record["hypothesis"]),
        })
    return {
        "status": "synthetic_audio_framing_and_transcript_metric_demo_complete",
        "training_performed": False,
        "audio_recordings_loaded": False,
        "speech_model_loaded": False,
        "model_downloaded": False,
        "device": "cpu",
        "fixture": audit["fixture"],
        "analytic_tone": {
            "source": "generated_sine_not_recorded_speech",
            "sample_rate_hz": sample_rate,
            "duration_ms": 100,
            "sample_count": len(tone),
            "frequency_hz": 440.0,
            "frame_ms": 25.0,
            "hop_ms": 10.0,
            "frame_length_samples": len(frames[0]),
            "hop_length_samples": round(sample_rate * 10.0 / 1_000),
            "complete_frames_without_tail_padding": len(frames),
            "tail_padding": False,
            "first_frame_rms": root_mean_square(frames[0]),
            "first_frame_peak_bin": peak_bin,
            "first_frame_peak_frequency_hz": peak_bin * sample_rate / len(frames[0]),
            "feature_type": "hann_windowed_single_sided_power_spectrum_not_log_mel",
        },
        "transcript_metrics": {
            "normalization": "NFC, casefold, whitespace splitting; punctuation retained",
            "wer": word_metrics,
            "cer": {
                **character_metrics,
                "normalization": "NFC, casefold; whitespace removed; Unicode code points counted",
            },
            "sentence_macro_wer": sentence_macro_word_error_rate(records),
            "per_record": per_record,
        },
        "claim_boundary": "Synthetic tone and synthetic text pairs only; no speech, ASR, TTS, codec, benchmark, Persian quality, or model performance was evaluated.",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CPU-only synthetic audio and transcript-metric lab")
    parser.add_argument("--mode", choices=("audit", "demo"), required=True)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    result = audit_fixture(args.fixture) if args.mode == "audit" else run_demo(args.fixture)
    result["environment"] = {
        "python": platform.python_version(),
        "platform": sys.platform,
        "dependencies": "Python standard library only",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    output_file = args.output / "run.json"
    output_file.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
