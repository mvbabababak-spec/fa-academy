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
