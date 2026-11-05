# جلد سوم، فصل ۷ — Transformer چندوجهی: اتصال رمزگذارهای تصویر و صوت

**The Art & Science of Building Intelligence | Babak & Ai | فصل سراسری ۳۹ از نقشهٔ پنج‌جلدی**

**تاریخ مرجع و بازبینی منابع: ۵ نوامبر ۲۰۲۶.** این فصل بخش ۷ جلد سوم را می‌بندد؛ فصل بعدی در نقشه، پروژهٔ دادهٔ کوچک است و هنوز جزو این فصل نیست.

**پیش‌نیاز:** تعبیه و توکن‌سازی از فصل ۳۳، Attention و Q/K/V از فصل ۳۴، ماسک از فصل ۳۵، بلوک Transformer از فصل ۳۶، معماری Encoder/Decoder از فصل ۳۷ و ملاحظات زمینه/هزینه از فصل ۳۸. **هدف:** تبدیل هر سیگنال به توکن‌های مناسب، ساختن بازنمایی‌های قابل‌مقایسه، انتخاب میان هم‌ترازی و ادغام، و تشخیص جاهایی که «نزدیک بودن embedding» را نباید فهم یا استدلال فرض کرد.

![شکل ۳-۷-۱ — مسیرهای چندوجهی: تصویر به وصله‌های ViT، صوت به فریم‌های log-Mel و متن به توکن‌ها تبدیل می‌شوند؛ encoderهای جدا با InfoNCE در فضای embedding هم‌تراز می‌شوند، یا توکن‌های یک مدالیته با cross-attention از مدالیتهٔ دیگر اطلاعات می‌گیرند.](assets/images/babak-ai/v3-ch07-multimodal-bridge.webp)

**شکل ۳-۷-۱ — دو هدف جدا: هم‌ترازی بردارهای خلاصه برای جست‌وجو، و تبادل اطلاعات میان توکن‌ها برای وظیفهٔ مشترک.** نمودار مفهومی است؛ اندازهٔ بلوک‌ها یا طول پیکان‌ها مقیاس، کیفیت یا سرعت مدل واقعی را اندازه‌گیری نمی‌کند.

## ۱. چرا یک Transformer را به بیش از یک نوع داده وصل می‌کنیم؟

مدلی که تنها متن می‌بیند از عکس، گفتار، صدای محیط یا ویدئو به شکل مستقیم اطلاعات ندارد. در یک مدل چندوجهی (multimodal)، هر ورودی ابتدا به بازنمایی‌ای تبدیل می‌شود که مدل بتواند محاسبه کند؛ بعد باید تصمیم بگیریم بازنمایی‌ها فقط قابل‌مقایسه باشند یا هنگام حل وظیفه با هم تعامل کنند. این دو نیاز متفاوت‌اند: **retrieval** می‌خواهد «کدام متن با این عکس/صوت جورتر است؟» را پاسخ دهد؛ **پرسش‌وپاسخ** ممکن است لازم داشته باشد چند ناحیهٔ تصویر و چند واژهٔ پرسش به‌صورت مرحله‌ای به هم توجه کنند.

مسیر کلی فصل چنین است: (الف) سیگنال‌ها را به توالیِ مناسب هر رمزگذار ببریم؛ (ب) یک فضای مشترک بسازیم و زیان هم‌ترازی را بفهمیم؛ (ج) تفاوت embeddingِ دوسویه با cross-attention را ببینیم؛ (د) زمان، داده، آزمون و محدودیت‌ها را در طراحی وارد کنیم. «چندوجهی» به‌تنهایی نه معماری یگانه‌ای است، نه تضمین فهم همه‌چیز.

## ۲. هر مدالیته باید قرارداد ورودی خودش را داشته باشد

**مدالیته** (modality) نوعی سیگنال با ساختار و واحد ویژهٔ خود است. متن معمولاً به شناسه‌های توکن تبدیل می‌شود؛ تصویر ممکن است به وصله‌های پیکسلی یا ویژگی‌های چندمقیاسی شکسته شود؛ صوت از موج نمونه‌برداری‌شده یا ویژگی‌هایی مانند log-Mel به فریم‌ها/توکن‌ها می‌رسد. برای Transformer نهایی، همه می‌توانند توالیِ بردار باشند؛ اما تبدیل اولیه و معنای موقعیت در هرکدام یکی نیست.

| ورودی | نمونهٔ نمایش خام/میانی | توالی‌ای که encoder می‌بیند | قراردادهایی که باید ثبت شوند |
|---|---|---|---|
| متن | رشته، شناسهٔ توکن | `[B,L,d]` | tokenizer، زبان، نشانه‌های ویژه، padding و ماسک |
| تصویر | RGB یا کانال‌های دیگر | `[B,N_v,d]` | اندازه/نسبت تصویر، patch/crop، normalization و ترتیب وصله‌ها |
| صوت | waveform یا log-Mel | `[B,N_a,d]` | نرخ نمونه‌برداری، کانال، پنجره/گام، مدت، VAD و padding |
| ویدئو | فریم‌ها همراه timestamp؛ گاهی audio track | `[B,N_t,d]` یا توالی interleaved | fps، timestamp، هم‌زمان‌سازی، نرخ فریم و نگه‌داشتن قطعه‌ها |

این شکل‌ها شماتیک‌اند و batch، padding یا tokenهای ویژه را ساده کرده‌اند. اگر دو نمونه از یک صحنه باشند اما timestamp، crop یا transcript ناسازگار داشته باشند، صرفاً هم‌شکل بودن تنسورها جفت معناییِ درست نمی‌سازد.

## ۳. تصویر به توالی: وصله‌های ViT

در Vision Transformer (ViT) ساده، تصویر `H×W` به مربع‌های `p×p` شکسته می‌شود؛ هر وصله مسطح/پروجکت می‌شود تا یک بردار بسازد و به آن موقعیت داده می‌شود. تعداد وصله‌ها، در نبود padding و crop، چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="تعداد وصله‌های تصویر برابر ارتفاع تقسیم بر اندازهٔ وصله ضرب در عرض تقسیم بر اندازهٔ وصله است؛ attention متراکم روی N وصله تقریباً با N به توان دو رشد می‌کند"><mrow><mi>N</mi><mo>=</mo><mfrac><mi>H</mi><mi>p</mi></mfrac><mo>×</mo><mfrac><mi>W</mi><mi>p</mi></mfrac><mo>,</mo><mspace width="1em"/><mi>Cost</mi><mo>(</mo><mi>attention</mi><mo>)</mo><mo>≈</mo><mi>O</mi><mo>(</mo><msup><mi>N</mi><mn>2</mn></msup><mi>d</mi><mo>)</mo></mrow></math>

برای تصویر `224×224` و `p=16` داریم `14×14=196` وصله. دو برابر کردن هر بُعد به `448×448` تعداد وصله‌ها را چهار برابر (`784`) و جفت‌های dense را حدود شانزده برابر می‌کند، اگر معماری و mask ثابت بمانند. این نسبت هزینهٔ نظری توجه است، نه پیش‌بینی latency کل؛ patch embedding، MLP، batching، kernel و سخت‌افزار نیز دخیل‌اند. ViT نشان داد Transformer می‌تواند دنبالهٔ وصله‌های تصویر را پردازش کند؛ پیش‌آموزش، داده و انتقال به وظیفه هم در نتیجهٔ آن کار اهمیت داشتند [۱].

**پیام مهندسی:** وضوح را فقط برای «جزئیات بیشتر» بالا نبرید. OCR، نمودار و تصویر سند ممکن است به crop/وضوح بیشتری نیاز داشته باشند؛ طبقه‌بندی کلی شاید با وضوح کمتر کافی باشد. ثبت تعداد وصله‌ها، cropها و معیار خطا کمک می‌کند معلوم شود هزینه کجا صرف شده است.

## ۴. متن هم یک encoder دارد، نه یک رشتهٔ جادویی

در مسیر تصویر–متن، tokenizer متن را به شناسه‌ها تبدیل می‌کند؛ embedding و Transformer بازنمایی توکن‌ها را می‌سازند؛ سپس یک pooling rule (مثلاً end-of-text، توکن ویژه یا میانگین masked) و projection، یک بردار خلاصه تولید می‌کنند. جزئیات انتخاب pooling و tokenizer بخشی از checkpoint است؛ تعویضشان بدون ارزیابی ممکن است فضای embedding را ناسازگار کند.

در CLIP، رمزگذار تصویر و رمزگذار متن جداگانه بازنمایی می‌سازند و با جفت‌های تصویر–شرح آموزش می‌بینند؛ همین طراحی، محاسبهٔ متن‌ها و تصاویر را جدا می‌کند و برای جست‌وجو مناسب است [۲]. مدل متن در چنین سامانه‌ای لزوماً یک LLM مولد نیست. همچنین «بردار متن با بردار تصویر مقایسه شد» به این معنا نیست که مدل توانسته متن را با ناحیهٔ دقیق تصویر یا ترتیب چند رویداد پیوند دهد.

برای متن فارسی، باید tokenizer، داده، نیم‌فاصله، خط، نویسه‌های مخلوط، زبان شرح و شیوهٔ pooling را جدا آزمود. پشتیبانی از چند زبان در مدل‌کارت یا مقاله جایگزین آزمون روی پرس‌وجوها و تصاویر موردنیاز شما نیست.

## ۵. فضای embedding مشترک: نزدیک‌بودن را با چه چیزی می‌سنجیم؟

فرض کنید encoder تصویر بردار `hᵛ` و encoder متن بردار `hᵗ` می‌سازد. projectionهای جدا آن‌ها را به بُعد مشترک می‌برند و معمولاً نرمال‌سازی L2 می‌کنند. شباهت cosine میان بردارهای نرمال‌شده برابر ضرب داخلی آن‌ها است؛ عدد بزرگ‌تر یعنی مدل در فضای آموخته‌شده آن جفت را نزدیک‌تر گذاشته است، نه اینکه یک احتمالِ کالیبره‌شده یا داوریِ انسانی باشد.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="بردار تعبیهٔ واحد برابر projection بر طول اقلیدسی آن است؛ شباهت کسینوسی دو بردار نرمال‌شده برابر ضرب داخلی آن‌هاست"><mrow><mi>z</mi><mo>=</mo><mfrac><mrow><mi>W</mi><mi>h</mi></mrow><msub><mrow><mo>∥</mo><mi>W</mi><mi>h</mi><mo>∥</mo></mrow><mn>2</mn></msub></mfrac><mo>,</mo><mspace width="1em"/><mi>sim</mi><mo>(</mo><msub><mi>z</mi><mi>i</mi></msub><mo>,</mo><msub><mi>z</mi><mi>j</mi></msub><mo>)</mo><mo>=</mo><msubsup><mi>z</mi><mi>i</mi><mi>⊤</mi></msubsup><msub><mi>z</mi><mi>j</mi></msub></mrow></math>

با داشتن یک پرس‌وجوی تصویری، می‌توان embedding آن را با embedding شرح‌های ازپیش‌محاسبه‌شده مقایسه کرد و top-k را بازیابی کرد. در reverse retrieval، متن query است و تصاویر candidate. این سازوکار **هم‌ترازی سراسری** را بهینه می‌کند؛ ممکن است «یک سگ روی کاناپه» و «یک سگ در پارک» را به‌خاطر واژهٔ مشترک نزدیک بگذارد، هرچند رابطهٔ فضایی متفاوت باشد.

## ۶. InfoNCE: جفت درست را میان جفت‌های دسته پیدا کن

در دسته‌ای با `B` جفت متن–تصویر، encoderها ماتریس شباهت `B×B` می‌سازند. قطر ماتریس جفت‌های مثبتِ داده‌شده است؛ خانه‌های دیگر در حالت ساده منفی فرض می‌شوند. دما/مقیاس logits بر تیزی توزیع اثر دارد. زیان contrastiveِ متن‌به‌تصویر و تصویر‌به‌متن میانگین گرفته می‌شود:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="لوگیت تصویر متن برابر مقیاس ضربدر ضرب داخلی embeddingهای نرمال‌شده است؛ هدف هر سطر جایگاه مثبت روی قطر ماتریس شباهت است"><mrow><msub><mi>s</mi><mrow><mi>i</mi><mi>j</mi></mrow></msub><mo>=</mo><mi>α</mi><mo>·</mo><msubsup><mi>z</mi><mi>i</mi><mi>image</mi></msubsup><msubsup><mi>z</mi><mi>j</mi><mi>text</mi></msubsup><mo>,</mo><mspace width="0.8em"/><msub><mi>y</mi><mi>i</mi></msub><mo>=</mo><mi>i</mi></mrow></math>

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="زیان تصویر به متن منفی میانگین لگاریتم احتمال کلاس جفت درست است؛ زیان دوطرفه میانگین مسیر تصویر به متن و متن به تصویر است"><mrow><msub><mi>L</mi><mrow><mi>i</mi><mo>→</mo><mi>t</mi></mrow></msub><mo>=</mo><mo>−</mo><mfrac><mn>1</mn><mi>B</mi></mfrac><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>B</mi></munderover><mi>log</mi><mfrac><mrow><mi>exp</mi><mo>(</mo><msub><mi>s</mi><mrow><mi>i</mi><mi>i</mi></mrow></msub><mo>)</mo></mrow><mrow><munderover><mo>∑</mo><mrow><mi>j</mi><mo>=</mo><mn>1</mn></mrow><mi>B</mi></munderover><mi>exp</mi><mo>(</mo><msub><mi>s</mi><mrow><mi>i</mi><mi>j</mi></mrow></msub><mo>)</mo></mrow></mfrac><mo>,</mo><mspace width="0.8em"/><mi>L</mi><mo>=</mo><mfrac><mrow><msub><mi>L</mi><mrow><mi>i</mi><mo>→</mo><mi>t</mi></mrow></msub><mo>+</mo><msub><mi>L</mi><mrow><mi>t</mi><mo>→</mo><mi>i</mi></mrow></msub></mrow><mn>2</mn></mfrac></mrow></math>

این یک نمونهٔ هدف است، نه تنها راه آموزش چندوجهی. کد پروژه برای هر جفت modality همین زیان متقارن را روی batch کوچک اجرا می‌کند. اگر چند caption واقعاً دربارهٔ یک تصویر باشند، فرض «فقط قطر مثبت است» می‌تواند هم‌معناها را به‌اشتباه منفی بخواند؛ کیفیت داده و ساخت loss را همراه با مدل طراحی کنید.

## ۷. مثبت و منفی را خود داده تعیین نمی‌کند

«مثبت» و «منفی» برچسب‌های آموزشی‌اند، نه حقیقت جهان. دو شرح متفاوت ممکن است هر دو درست باشند؛ دو تصویر متفاوت ممکن است هر دو یک شیء یا مفهوم را نشان دهند. در مقابل، شرح کلی می‌تواند با تصویر جور باشد اما رنگ، شمار، نسبت فضایی یا زمان را جا بیندازد. جفت‌های اشتباه یا شرح‌های کم‌کیفیت به مدل یاد می‌دهند shortcutهای آماری را دنبال کند.

InfoNCE معمولی برای هر جفت، بقیهٔ اعضای همان batch را منفی می‌گیرد. وقتی batch بزرگ‌تر می‌شود، سیگنال منفی بیشتری داریم، ولی احتمال جفت‌های هم‌معنا/تکراری یا false negative هم بالا می‌رود. زیان sigmoid خانوادهٔ SigLIP برای جفت‌ها هدف دودویی را به‌کار می‌گیرد و به نرمال‌سازی سراسری softmax روی ماتریس شباهت به همان شکل CLIP وابسته نیست؛ این یک تغییر تابع زیان است، نه تضمین پاک‌بودن برچسب‌ها یا برتری روی همهٔ داده‌ها [۳].

کنترل‌های عملی: تکرار تصویر و متن را پیدا کنید؛ شرح‌های چندگانه را نگه دارید؛ جفت‌های مبهم را جدا برچسب بزنید؛ در صورت امکان چند مثبت برای یک نمونه ثبت کنید؛ و روی گروه‌هایی با محتوای مشابه معیار بگیرید. افزایش batch به‌تنهایی جای پاک‌سازی، اسناد داده و تحلیل false negative را نمی‌گیرد.

## ۸. Dual-encoder یا cross-encoder: جست‌وجو با فهم جفت فرق دارد

**Dual-encoder:** هر تصویر/متن را یک بار مستقل encode می‌کند؛ سپس شباهت بردارها را برای مقایسهٔ تعداد زیادی candidate می‌سنجد. embeddingهای corpus را می‌توان پیش‌محاسبه و در index جست‌وجو کرد. به همین دلیل این طرح معمولاً مرحلهٔ نخستِ مقیاس‌پذیر برای retrieval است.

**Cross-encoder:** دو ورودی را با هم وارد لایه‌های تعامل می‌کند؛ مثلاً توکن‌های متن مستقیماً به توکن‌های تصویر توجه می‌کنند. از آن‌جا که تعامل هر جفت باید جدا محاسبه شود، معمولاً آن را روی shortlistی که dual-encoder بازیابی کرده اجرا می‌کنند. Cross-encoder ممکن است به رابطهٔ جزئی‌تری پاسخ دهد، اما اگر به تصویر/شرح دقیق وابسته باشد همچنان می‌تواند شکست بخورد؛ اسم معماری کیفیت را تضمین نمی‌کند.

| پرسش محصول | انتخاب اولیهٔ معقول | آنچه باید سنجید |
|---|---|---|
| «از صدها هزار تصویر کدام‌ها با این query می‌خوانند؟» | Dual-encoder + index + reranker اختیاری | Recall@k، latency، زبان/دامنهٔ query |
| «به پرسش دربارهٔ ناحیه یا رابطه پاسخ بده» | encoder تصویری با تعامل متنی، localization یا decoder | شواهد ناحیه‌ای، خطای OCR، grounded answer |
| «جملهٔ شنیده‌شده را از آرشیو صدا پیدا کن» | audio–text encoder یا زنجیرهٔ ASR + retrieval | نویز، لهجه، زبان، طول و زمان‌بندی |

## ۹. Cross-attention: پل میان توکن‌ها

برای queryهای متن، `Q` از توکن‌های متن و `K,V` از توکن‌های تصویر (یا صوت) می‌آیند؛ وزن‌ها تعیین می‌کنند هر query چه بخشی از حافظه را بخواند. باقیمانده، نرمال‌سازی و شبکهٔ پیش‌خور، خروجی را دوباره در مسیر Transformer قرار می‌دهند. اگر متن چند پرسش دارد، هر توکن پرسش می‌تواند به جاهای متفاوتی از تصویر توجه کند؛ این تعامل از یک شباهت میان دو بردار خلاصه غنی‌تر است، ولی به‌تنهایی grounding درست را تضمین نمی‌کند.

BLIP-2 یک نمونه از پل کم‌پارامتر میان encoder تصویری منجمد و LLM منجمد است: Querying Transformer (Q-Former) از encoder تصویر اطلاعات می‌گیرد و به مسیر زبانی می‌رساند [۹]. Flamingo نیز اتصال مدل دیداری و زبانی ازپیش‌آموزش‌دیده و ورودی‌های متن/تصویر درهم‌تنیده را بررسی کرد [۱۰]. این‌ها نمونهٔ طراحی‌اند؛ تفاوت مرحلهٔ آموزش، تعداد پارامترهای قابل‌آموزش و داده را در مقایسه‌ها نگه دارید.

در پروژهٔ این فصل، توکن‌های متن query دو ماژول cross-attention مستقل‌اند: یکی حافظهٔ تصویر را می‌خواند و دیگری صوت را. نسخهٔ آموزشی به دلایل وضوح، temporal mask یا decoder مولد ندارد. پس آن را نمونهٔ **اتصال اطلاعات** بدانید، نه بازسازی معماری BLIP-2 یا Flamingo.

## ۱۰. صوت: از waveform تا فریم‌های قابل‌پردازش

موج دیجیتال دنباله‌ای از دامنهٔ سیگنال در نرخ نمونه‌برداری مشخص است. طول waveform به ثانیه و نرخ نمونه بستگی دارد؛ با تبدیل STFT می‌توان پنجره‌های کوتاه را به طیف و معمولاً فیلترهای Mel را به ویژگی‌های کم‌بعدتر تبدیل کرد. با پنجرهٔ ۲۵ms و گام ۱۰ms، فریم‌ها هر ۱۰ms جابه‌جا می‌شوند؛ مرز دقیق و نرخ‌ها وابسته به مدل و preprocessing است، نه استاندارد واحد همهٔ encoderها.

**نرخ نمونه‌برداری مهم است.** بازتفسیر waveform با نرخ دیگری—بدون resampling—سرعت و pitch مؤثر را عوض می‌کند. همچنین stereo-to-mono، clipping، normalization، silence/VAD و مدت crop روی نتیجه اثر دارند. شکل ورودی «`[B,mel,T]`» فقط قرارداد تنسور است؛ تعداد mel bins، window, hop, sample rate و normalization را باید در metadata مدل ثبت کرد.

کد پروژه waveform نمی‌خواند. ورودی آن feature ساختگیِ شبیه log-Mel است که چند فریم را با Conv1d گروه‌بندی می‌کند؛ این میان‌بُر آموزشی برای نشان‌دادن توکن‌های صوت است و جایگزین frontend صوت واقعی نیست.

## ۱۱. سه وظیفهٔ صوتی را یکی نگیریم

**بازنمایی گفتار:** wav2vec 2.0 روی صوتِ بدون متن، نمایش‌های latent را با هدف خودنظارتی/contrastive می‌آموزد و سپس برای کارهایی چون بازشناسی گفتار fine-tune می‌شود [۵]. **بازشناسی گفتار (ASR):** Whisper یک مسیر نظارت‌شدهٔ ضعیف‌برچسب‌خورده برای پیش‌بینی transcript و کارهای مرتبط بررسی کرد [۶]. **توصیف/جست‌وجوی صوت:** CLAP متن و صوت را برای retrieval و classification صفرنمونه‌ای در آزمایش‌های خودش هم‌تراز کرد [۷].

این دسته‌ها می‌توانند در یک محصول ترکیب شوند، اما برچسب و خروجی یکسان ندارند: transcript حرف‌ها را هدف می‌گیرد؛ embedding صوتی ممکن است ویژگی‌های رویداد را نگه دارد؛ caption می‌تواند «صدای زنگ و ترمز» را توصیف کند؛ تولید گفتار وظیفهٔ دیگری است. یک مدل speech encoder لزوماً صدای موتور، موسیقی یا هم‌زمانی دو گوینده را به‌خوبی تحلیل نمی‌کند.

پیش از انتخاب، پرسش را دقیق بنویسید: آیا به متن پیاده‌شده نیاز است، رخداد صوتی، speaker، زمان شروع رویداد، caption، یا پیوند audio و تصویر؟ سپس encoder، داده، معیار و سیاست حفظ فایل خام را با همین هدف تطبیق دهید.

## ۱۲. اتصال چند مدالیته: فضای مشترک همه‌به‌همه لازم نیست

یک راه ساده، ساخت جفت متن–تصویر و جداگانه متن–صوت است و نگاشت هر encoder به بُعد مشترک. سپس تصویر و صوت هم از طریق متن در گراف جفت‌ها قابل مقایسه می‌شوند، اما کیفیت این مسیر به پوشش مفاهیم و زبان در پیوندها وابسته است. ImageBind نشان داد در تنظیم مقالهٔ آن می‌توان شش مدالیته—تصویر، متن، صوت، عمق، حرارتی و IMU—را به فضای embedding مشترک برد، بدون اینکه هر ترکیب دوتایی مستقیماً دادهٔ paired داشته باشد [۸]. این ادعا به روش و آزمایش همان مقاله محدود است؛ جفت‌شدن از راه یک anchor همهٔ رابطه‌های ظریف یا modal gap را از میان نمی‌برد.

در طراحی داده، می‌توان جفت‌ها را به شکل گراف دید: گره‌ها modality/encoderها و یال‌ها نمونه‌های paired و هدف‌های آموزشی‌اند. یال کم‌پوشش یا نویزی روی مسیرهای چندمرحله‌ای اثر می‌گذارد. بنابراین علاوه بر کیفیت هر جفت، سؤال کنید هر مفهوم، زبان، طول، کانال صوت و شرایط تصویری با چه مسیرهایی به فضای مشترک می‌رسد.

## ۱۳. صوت و تصویر زمان‌مندند؛ هم‌ترازی فقط یک cosine نیست

در تصویر ثابت و جملهٔ کوتاه می‌توان یک embedding برای هر نمونه در نظر گرفت؛ اما ویدئو/صوت دنباله‌های زمان‌مند با نرخ‌های مختلف‌اند. یک ثانیهٔ ویدئو می‌تواند چندین frame داشته باشد و صوت در هر ثانیه هزاران نمونه؛ پس لازم است timestampها، chunkها و موقعیت‌های زمان‌محور را به توکن‌ها نسبت دهیم. هم‌ترازی سراسری شاید «صدای پارس و سگ» را نزدیک کند، ولی نمی‌گوید پارس دقیقاً کدام لحظه/فریم رخ داده است.

Qwen2.5-Omni در گزارش خود، برای ورودی ویدئو/صوت هم‌زمان از chunking encoderها و TMRoPE (Time-aligned Multimodal RoPE) برای موقعیت زمانی یاد می‌کند؛ در همان گزارش Thinker/Talker وظایف فهم/متن و تولید گفتار را در معماری مرتبط می‌کند [۱۳]. پژوهش TaRoPE در ۲۰۲۶ به mismatch نرخ فریم صوت/ویدئو و هم‌ترازی ویژگی‌های زمانی در یک وظیفهٔ خاصِ تشخیص هیجان صوتی–دیداری می‌پردازد؛ نتیجه‌اش را به همهٔ وظایف تعمیم ندهید [۱۵].

پروتکل پایه: timestamp یک رویداد را با دقت معلوم ثبت کنید؛ از frameهای نزدیک و قطعه‌های صوت هم‌زمان نمونه بگیرید؛ بررسی کنید resampling، crop و buffering زمان‌ها را جابه‌جا نکرده باشد؛ سپس هم retrieval کل کلیپ و هم تشخیص زمان رویداد را جدا ارزیابی کنید. بخش ۱۸ نمونه‌های تازه‌تر را مرور می‌کند.

## ۱۴. سه الگوی ادغام و جایی که تعامل رخ می‌دهد

| راهبرد | محل تعامل | مزیت معمول | هزینه/ریسک معمول |
|---|---|---|---|
| **Early fusion** | توکن‌های چند مدالیته زود در یک توالی ادغام می‌شوند | امکان مدل‌کردن وابستگی‌های مشترک در لایه‌ها | طول توالی/ماسک پیچیده‌تر؛ کمبود داده paired می‌تواند مشکل‌ساز شود |
| **Late fusion** | هر encoder جدا کار می‌کند؛ بردار یا score در پایان ترکیب می‌شود | محاسبهٔ مستقل و cache/index ساده‌تر | جزئیات ناحیه‌ای یا زمانی ممکن است در pooling گم شود |
| **Bridge / cross-attention** | چند query یا لایهٔ connector به encoder دیگر دسترسی دارد | راهی برای اتصال encoderهای ازپیش‌آموزش‌دیده و کاهش آموزش کامل | انتخاب تعداد query، اطلاعات حذف‌شده و bias encoder پایه مهم است |
| **Hybrid** | ترکیبی از late/bridge و ادغام در چند مرحله | امکان توازن هزینه و تعامل | دشوارتر برای ablation، اشکال‌زدایی و attribution خطا |

این‌ها خانواده‌های طراحی‌اند، نه ranking. نیاز محصول، نوع داده و بودجه تعیین می‌کند چه چیزی بسازیم. یک ablation منصفانه ثابت نگه می‌دارد: داده، split، pretrained checkpoint، optimizer، تعداد update و معیار؛ سپس فقط محل/نوع fusion را تغییر می‌دهد.

## ۱۵. Encoder را منجمد کنیم یا آموزش دهیم؟

اگر encoderهای ازپیش‌آموزش‌دیده داریم، **freeze** کردن وزن آن‌ها و آموزش یک projection/connector سبک می‌تواند آزمایش را ارزان‌تر و ساده‌تر کند. اما اگر زبان، دامنهٔ تصویر، sampling یا وظیفه با دادهٔ پایه فرق کند، نمای ثابت ممکن است اطلاعات لازم را نداشته باشد. در **partial unfreezing** لایه‌های بالایی یا adapterها آموزش می‌بینند؛ **full fine-tuning** آزادی بیشتری دارد، اما داده/حافظه و خطر forgetting و overfit را هم بالا می‌برد.

یک آزمایش مرحله‌ای: ابتدا baseline منجمد؛ بعد connector/LoRA؛ سپس unfreeze کنترل‌شده؛ همه با validation/test پاک و جدا. هزینه را با trainable parameters تنها نسنجید: activation، optimizer state، decoder و اندازهٔ sequence هم مصرف دارند. دقت روی دادهٔ train یا چند prompt دستی معیار انتخاب نهایی نیست.

## ۱۶. ارزیابی: retrieval، جزئیات و استدلال سه آزمون‌اند

**Retrieval:** Recall@k، MRR یا nDCG را روی gallery ثابت بسنجید؛ هم text→image و image→text، هم زبان‌ها/دامنه‌های جدا. **Local grounding:** برای اینکه تصویر/فریم کدام ناحیه شاهد پاسخ است، IoU/grounding یا بررسی انسانیِ ناحیه‌ای لازم است. **ASR:** WER/CER و خطا برحسب لهجه، نویز و زبان. **زمان‌مندی:** onset/segment، timestamp tolerance و رویداد هم‌زمان. **پرسش‌وپاسخ:** correctness باید همراه با شاهد و خطای hallucination بررسی شود؛ امتیاز embedding similarity جای پاسخ مستند نیست.

MMMU نمونه‌ای از benchmark چندرشته‌ای است که پرسش‌های تصویرمحور و استدلالی در موضوعات دانشگاهی را هدف می‌گیرد [۱۲]. چنین benchmarkی retrieval ساده را با VQA و grounding یکی نمی‌کند. پیش از استناد به امتیاز، نسخهٔ داده، split، روش prompt، ابزار کمکی، metric، آلودگی احتمالی و شرایط اجرای همان paper را ثبت کنید؛ یک بنچمارک به‌تنهایی همهٔ محصول را پوشش نمی‌دهد.

## ۱۷. «هم‌ترازی» چه چیزی را حل نمی‌کند؟

1. **سطحی‌بودن برچسب:** caption کوتاه ممکن است جزئیات ریز، روابط، نفی، تعداد یا ترتیب رخداد را نگوید.
2. **false negative و چند مثبت:** جفت‌های مشابه می‌توانند در batch به‌غلط منفی شوند؛ score یادگرفته‌شده حقیقت قطعی نیست.
3. **سوگیری پوشش:** وب‌داده ممکن است بعضی زبان‌ها/فرهنگ‌ها، صداها، چهره‌ها، اسناد یا شرایط ضبط را بیش/کم‌تر نمایندگی کند. «multilingual» در عنوان paper تضمین برابری برای زبان/وظیفهٔ شما نیست؛ SigLIP 2 مثلاً recipe و ارزیابی چندزبانهٔ خودش را گزارش می‌کند [۴].
4. **leakage و مجوز:** near-duplicate میان train/test، حق استفادهٔ تصویر/صوت، رضایت و دادهٔ حساس باید بررسی شود. مقالهٔ DataComp توجه پژوهش را صریحاً به ساخت/فیلتر مجموعه‌داده و ارزیابی استاندارد می‌برد [۱۱]؛ این کار جایگزین بررسی حقوقی dataset مشخص نیست.
5. **shortcut و تغییر دامنه:** پس‌زمینه یا watermark می‌تواند label را لو بدهد؛ تغییر دوربین/نویز/زبان retrieval را عوض می‌کند.
6. **اعتماد کاذب:** نزدیک‌ترین vector ممکن است نامرتبط باشد، و مدل مولد می‌تواند با اطمینان پاسخ نادرست بسازد. threshold باید با calibration و هزینهٔ خطای محصول سنجیده شود.

برای تصمیم عملی، نمونه‌های خطا را به علت دسته‌بندی کنید: preprocessing، coverage، label, geometry/time, model capacity, evaluation leakage یا prompt. تا وقتی منبع خطا مشخص نیست، اضافه‌کردن داده و پارامتر صرفاً هزینه را زیاد می‌کند.

## ۱۸. پژوهش‌های تازه تا ۵ نوامبر ۲۰۲۶: نشانه‌اند، نه نسخهٔ نهایی

**SigLIP 2 (۲۰۲۵)** خانواده‌ای از encoderهای چندزبانهٔ تصویر–متن را با recipe شامل captioning، self-supervision و data curation گزارش می‌کند و localization/dense feature را هم ارزیابی می‌کند [۴]. **Qwen2.5-Omni (۲۰۲۵)** به stream چندوجهی متن، تصویر، صوت و ویدئو و تولید هم‌زمان متن/گفتار می‌پردازد [۱۳]. این‌ها دو سطح متفاوت‌اند: encoder embedding برای retrieval با سیستم end-to-end که چند نوع خروجی/وظیفه دارد یکی نیست.

**WAVE** در ICLR 2026، از مدل زبانی چندوجهی برای embeddingهای متن، صوت، ویدئو و ورودی صوتی–دیداری، feature fusion سلسله‌مراتبی و آموزش مشترک استفاده می‌کند؛ مقالهٔ خودش retrieval هر-به-هر و embedding وابسته به prompt را در benchmarkهای خودش گزارش می‌کند [۱۴]. این نتیجه را «هر مدل بزرگ خودبه‌خود audio/video را خوب embed می‌کند» تعبیر نکنید.

**Virtual Encoders in Multimodal Transformers** (نسخهٔ ۱۹ اکتبر ۲۰۲۶، مقالهٔ کارگاهی ACCV 2026) بررسی می‌کند که Transformer مشترک، وقتی encoder ادراکیِ کامل جداگانه ندارد، ممکن است در لایه‌های ابتدایی/میانی محاسبهٔ encoderمانندی انجام دهد [۱۶]. این یک تحلیل پژوهشی تازه دربارهٔ مرز عملکردیِ perception است، نه راهنمای قطعی برای حذف همهٔ encoderهای اختصاصی. ادبیات چندوجهی سریع تغییر می‌کند؛ تاریخ نسخه و محدودیت همان کار را کنار هر نتیجه نگه دارید.

## ۱۹. پروژهٔ کوچک، آزمون‌ها و مسیر تصمیم‌گیری

در `projects/39-multimodal-transformer/` سه encoder تصادفی با PyTorch ساخته شده‌اند: وصله‌های تصویر، توکن‌های متن و ویژگی‌های شبیه log-Mel. سه projection به بُعد مشترک می‌رسند؛ زیان سه‌طرفهٔ InfoNCE جفت‌های image–text، image–audio و text–audio را مقایسه می‌کند؛ شاخهٔ جداگانه‌ای نیز توکن‌های متن را با cross-attention به تصویر و صوت وصل می‌کند. خروجی مورد انتظار: embeddingهای `[4,16]`، توکن‌های متنِ ادغام‌شده `[4,6,32]`، loss متناهی و گرادیان.

```bash
cd book-engineering/projects/39-multimodal-transformer
python -m unittest discover -v
python multimodal_alignment.py
```

۱۵ آزمون shape، قرارداد ماسک، طول معتبر صوت، نرمال‌سازی، جفت مرتب/به‌هم‌ریخته، گرادیان شاخه‌ها و ورودی نامعتبر را بررسی می‌کنند. وزن تصادفی و دادهٔ مصنوعی‌اند؛ این پروژه **retrieval، آموزش معنادار، کیفیت alignment، سرعت، waveform واقعی یا تولید زبان را نشان نمی‌دهد**. کد کامل در بخش ۲۰ و توضیح اجرا در [README پروژه](book-engineering/projects/39-multimodal-transformer/README.md) است.

### تمرین و پروژهٔ تکمیلی

1. تصویر `384×256` با وصلهٔ `16×16` چند وصله دارد؟ اگر هر دو بُعد دو برابر شوند، نسبت تعداد وصله و جفت‌های dense چه می‌شود؟ فرض‌های مرزی را بنویسید.
2. در batch چهار، چرا InfoNCE ساده سه عضو دیگر را منفی می‌گیرد؟ یک مثال بیاورید که این فرض false negative بسازد و یک اصلاح داده/loss پیشنهاد کنید.
3. برای جست‌وجوی میلیون تصویر، چرا dual-encoder را می‌توان مرحلهٔ نخست گرفت؟ cross-encoder را در چه مرحله‌ای به‌کار می‌برید؟ هزینه و metric هر مرحله را جدا کنید.
4. نمونهٔ گفتار با نرخ 16 kHz را می‌خواهید برای مدلی با frontend تعریف‌شده در 24 kHz آماده کنید. چرا تغییر برچسب sample rate بدون resampling نادرست است؟ دست‌کم چهار metadata لازم را فهرست کنید.
5. ویدئویی از آشپزی دارید که یک صدای کوتاه هم‌زمان با یک فریم رخ می‌دهد. چه دادهٔ زمانی، fusion و metric لازم است تا رویداد را پیدا کنید، نه فقط کلیپ مشابه را؟
6. طرح dataset متن–تصویر–صوت کوچک بسازید: مجوز/رضایت، چند caption، split براساس منبع، حذف duplicate، annotation خطا و test زبان/گروه‌ها را مستند کنید.
7. در کد، اگر متن هم‌تراز با تصویر است ولی فایل صوتی از کلیپ دیگری آمده، کدام lossها جفت غلط را تشویق می‌کنند؟ چه guard در dataset pipeline اضافه می‌کنید؟
8. پروژهٔ تکمیلی: frozen encoderهای pretrained را جایگزین encoderهای toy کنید؛ retrieval دوطرفه، false negative، زمان استنتاج و دقت روی یک set جدا را گزارش کنید. مدل‌کارت و محدودیت مجوز را ضمیمه کنید.

برای پاسخ تشریحی به [پاسخ‌نامهٔ فصل ۳۹](book-engineering/answers/39-multimodal-transformer-fa.md) رجوع کنید. فصل بعدی طبق نقشه، فصل سراسری ۴۰ است؛ موضوع آن دادهٔ کوچک و آماده‌سازی آن خواهد بود و این فصل آن محتوا را پیشاپیش نمی‌نویسد.

### راهنمای انتخاب در یک دقیقه

- **پیداکردن/مرتب‌کردن تعداد زیادی نمونه:** dual-encoder، embeddingهای cacheشدنی و معیار retrieval.
- **گفت‌وگوی دقیق دربارهٔ ناحیه/جزئیات:** cross-attention یا مدل grounding، همراه با آزمون ناحیه‌ای و شاهد.
- **گفتار به متن:** ASR و معیار transcript؛ **رویداد صوتی به شرح:** audio–text alignment و معیار retrieval/caption.
- **رویداد audio–video زمان‌مند:** timestamp، chunk alignment و آزمون زمانی؛ یک embedding سراسری کافی نیست.
- **مدل موجود را به دامنهٔ تازه ببر:** ابتدا split و خط پایه، سپس connector/adapter و در پایان unfreeze کنترل‌شده.

### منابع بیرونی و تاریخ بازبینی

منابع اولیه/مقالات:

1. Dosovitskiy et al., “An Image is Worth 16×16 Words: Transformers for Image Recognition at Scale,” ICLR 2021, [arXiv:2010.11929](https://arxiv.org/abs/2010.11929). مراجعه: ۵ نوامبر ۲۰۲۶.
2. Radford et al., “Learning Transferable Visual Models From Natural Language Supervision,” 2021, [arXiv:2103.00020](https://arxiv.org/abs/2103.00020). مراجعه: ۵ نوامبر ۲۰۲۶.
3. Zhai et al., “Sigmoid Loss for Language Image Pre-Training,” ICCV 2023, [arXiv:2303.15343](https://arxiv.org/abs/2303.15343). مراجعه: ۵ نوامبر ۲۰۲۶.
4. Tschannen et al., “SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features,” 2025, [arXiv:2502.14786](https://arxiv.org/abs/2502.14786). مراجعه: ۵ نوامبر ۲۰۲۶.
5. Baevski et al., “wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations,” NeurIPS 2020, [arXiv:2006.11477](https://arxiv.org/abs/2006.11477). مراجعه: ۵ نوامبر ۲۰۲۶.
6. Radford et al., “Robust Speech Recognition via Large-Scale Weak Supervision,” 2022, [arXiv:2212.04356](https://arxiv.org/abs/2212.04356). مراجعه: ۵ نوامبر ۲۰۲۶.
7. Wu et al., “Large-scale Contrastive Language-Audio Pretraining with Feature Fusion and Keyword-to-Caption Augmentation,” ICASSP 2023, [arXiv:2211.06687](https://arxiv.org/abs/2211.06687). مراجعه: ۵ نوامبر ۲۰۲۶.
8. Girdhar et al., “ImageBind: One Embedding Space To Bind Them All,” CVPR 2023, [arXiv:2305.05665](https://arxiv.org/abs/2305.05665). مراجعه: ۵ نوامبر ۲۰۲۶.
9. Li et al., “BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models,” ICML 2023, [arXiv:2301.12597](https://arxiv.org/abs/2301.12597). مراجعه: ۵ نوامبر ۲۰۲۶.
10. Alayrac et al., “Flamingo: a Visual Language Model for Few-Shot Learning,” NeurIPS 2022, [arXiv:2204.14198](https://arxiv.org/abs/2204.14198). مراجعه: ۵ نوامبر ۲۰۲۶.
11. Gadre et al., “DataComp: In search of the next generation of multimodal datasets,” NeurIPS 2023 Datasets and Benchmarks, [arXiv:2304.14108](https://arxiv.org/abs/2304.14108). مراجعه: ۵ نوامبر ۲۰۲۶.
12. Yue et al., “MMMU: A Massive Multi-discipline Multimodal Understanding and Reasoning Benchmark for Expert AGI,” CVPR 2024 Oral, [arXiv:2311.16502](https://arxiv.org/abs/2311.16502). مراجعه: ۵ نوامبر ۲۰۲۶.
13. Xu et al., “Qwen2.5-Omni Technical Report,” 2025, [arXiv:2503.20215](https://arxiv.org/abs/2503.20215). مراجعه: ۵ نوامبر ۲۰۲۶.
14. Tang et al., “WAVE: Learning Unified & Versatile Audio-Visual Embeddings with Multimodal LLM,” ICLR 2026، [صفحهٔ رسمی ICLR](https://www.iclr.cc/virtual/2026/poster/10009925)، [arXiv:2509.21990](https://arxiv.org/abs/2509.21990)، [پروژهٔ رسمی](https://github.com/TCL606/WAVE). مراجعه: ۵ نوامبر ۲۰۲۶.
15. Koo et al., “Multimodal Self-Attention Network with Temporal Alignment for Audio-Visual Emotion Recognition,” پذیرفته‌شده در ICASSP 2026، [arXiv:2603.11095](https://arxiv.org/abs/2603.11095). مراجعه: ۵ نوامبر ۲۰۲۶.
16. Ogata & Nakashima, “Virtual Encoders in Multimodal Transformers,” نسخهٔ ۱۹ اکتبر ۲۰۲۶؛ مقالهٔ کارگاهی ACCV 2026، [arXiv:2609.26513](https://arxiv.org/abs/2609.26513). مراجعه: ۵ نوامبر ۲۰۲۶.

ادعاهای تجربی در متن به وظیفه، checkpoint، benchmark و شرایط گزارش‌شده در همان منبع محدودند. «آخرین تحولات» به معنی پوشش کامل همهٔ آثار تا آن تاریخ نیست.

## ۲۰. پیوست: کد کامل پروژه

فایل زیر همان کدی است که در پروژه آزموده می‌شود؛ برای اجرا و آزمون به‌روزرسانی‌های منبع را در `projects/39-multimodal-transformer/` ببینید.

```python
"""Tiny CPU-friendly encoders for image, text, and audio alignment.

This pedagogical model demonstrates patch/token encoders, a shared embedding
space, symmetric contrastive learning, and text-query cross-attention to visual
and audio context. It uses random weights and synthetic features: it is not a
pretrained model, dataset, benchmark, or production multimodal assistant.
"""
from __future__ import annotations

import math

import torch
import torch.nn.functional as F
from torch import Tensor, nn


def _positive_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


def _masked_mean(tokens: Tensor, padding_mask: Tensor | None = None) -> Tensor:
    """Mean-pool [B,T,D], ignoring positions where a bool mask is True."""
    if padding_mask is None:
        return tokens.mean(dim=1)
    weights = (~padding_mask).unsqueeze(-1).to(tokens.dtype)
    return (tokens * weights).sum(dim=1) / weights.sum(dim=1).clamp_min(1.0)


def _transformer(d_model: int, num_heads: int, depth: int) -> nn.TransformerEncoder:
    layer = nn.TransformerEncoderLayer(
        d_model=d_model,
        nhead=num_heads,
        dim_feedforward=4 * d_model,
        dropout=0.0,
        activation="gelu",
        batch_first=True,
        norm_first=True,
    )
    return nn.TransformerEncoder(layer, num_layers=depth, enable_nested_tensor=False)


class VisionPatchEncoder(nn.Module):
    """Patchify a fixed-size batch of images and encode the patch sequence."""

    def __init__(
        self,
        d_model: int,
        num_heads: int,
        *,
        patch_size: int = 8,
        image_channels: int = 3,
        max_patches: int = 256,
        depth: int = 1,
    ) -> None:
        super().__init__()
        _positive_int(d_model, "d_model")
        _positive_int(num_heads, "num_heads")
        _positive_int(patch_size, "patch_size")
        _positive_int(image_channels, "image_channels")
        _positive_int(max_patches, "max_patches")
        _positive_int(depth, "depth")
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        self.image_channels = image_channels
        self.patch_size = patch_size
        self.max_patches = max_patches
        self.patch_projection = nn.Conv2d(
            image_channels, d_model, kernel_size=patch_size, stride=patch_size
        )
        self.position = nn.Parameter(torch.zeros(1, max_patches, d_model))
        nn.init.normal_(self.position, std=0.02)
        self.encoder = _transformer(d_model, num_heads, depth)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, images: Tensor) -> Tensor:
        if not isinstance(images, Tensor) or images.ndim != 4:
            raise ValueError("images must have shape [B,C,H,W]")
        if not images.is_floating_point():
            raise ValueError("images must be floating-point tensors")
        batch, channels, height, width = images.shape
        p = self.patch_size
        if batch < 1 or channels != self.image_channels or height < p or width < p:
            raise ValueError("images need a non-empty batch, configured channels, and at least one patch")
        if height % p or width % p:
            raise ValueError("image height and width must be divisible by patch_size")
        patches = self.patch_projection(images).flatten(2).transpose(1, 2)
        if patches.shape[1] > self.max_patches:
            raise ValueError("image produces more patches than max_patches")
        patches = self.encoder(patches + self.position[:, : patches.shape[1]])
        return self.norm(patches)


class TextTokenEncoder(nn.Module):
    """Encode token IDs with a padding-aware bidirectional Transformer."""

    def __init__(
        self,
        vocab_size: int,
        d_model: int,
        num_heads: int,
        *,
        pad_id: int = 0,
        max_length: int = 64,
        depth: int = 1,
    ) -> None:
        super().__init__()
        _positive_int(vocab_size, "vocab_size")
        _positive_int(d_model, "d_model")
        _positive_int(num_heads, "num_heads")
        _positive_int(max_length, "max_length")
        _positive_int(depth, "depth")
        if isinstance(pad_id, bool) or not isinstance(pad_id, int) or not 0 <= pad_id < vocab_size:
            raise ValueError("pad_id must be a token ID in the vocabulary")
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        self.vocab_size = vocab_size
        self.pad_id = pad_id
        self.max_length = max_length
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=pad_id)
        self.position = nn.Embedding(max_length, d_model)
        self.encoder = _transformer(d_model, num_heads, depth)
        self.norm = nn.LayerNorm(d_model)

    def forward(
        self,
        token_ids: Tensor,
        padding_mask: Tensor | None = None,
    ) -> tuple[Tensor, Tensor]:
        if not isinstance(token_ids, Tensor) or token_ids.ndim != 2:
            raise ValueError("token_ids must have shape [B,L]")
        if token_ids.dtype != torch.long:
            raise ValueError("token_ids must use torch.long")
        batch, length = token_ids.shape
        if batch < 1 or length < 1 or length > self.max_length:
            raise ValueError("token batch must be non-empty and no longer than max_length")
        if bool(((token_ids < 0) | (token_ids >= self.vocab_size)).any()):
            raise ValueError("token_ids contain an ID outside the vocabulary")
        if padding_mask is None:
            padding_mask = token_ids.eq(self.pad_id)
        elif (
            not isinstance(padding_mask, Tensor)
            or padding_mask.dtype != torch.bool
            or tuple(padding_mask.shape) != tuple(token_ids.shape)
            or padding_mask.device != token_ids.device
        ):
            raise ValueError("padding_mask must be bool [B,L] on the token device; True means padding")
        if bool(padding_mask.all(dim=1).any()):
            raise ValueError("each text row must contain at least one unmasked token")
        positions = torch.arange(length, device=token_ids.device).unsqueeze(0)
        x = self.embedding(token_ids) + self.position(positions)
        x = self.encoder(x, src_key_padding_mask=padding_mask)
        x = self.norm(x).masked_fill(padding_mask.unsqueeze(-1), 0.0)
        return x, padding_mask


class AudioFrameEncoder(nn.Module):
    """Encode log-Mel-like [B,n_mels,T] features in fixed-size frame groups."""

    def __init__(
        self,
        n_mels: int,
        d_model: int,
        num_heads: int,
        *,
        frame_stride: int = 4,
        max_audio_tokens: int = 256,
        depth: int = 1,
    ) -> None:
        super().__init__()
        _positive_int(n_mels, "n_mels")
        _positive_int(d_model, "d_model")
        _positive_int(num_heads, "num_heads")
        _positive_int(frame_stride, "frame_stride")
        _positive_int(max_audio_tokens, "max_audio_tokens")
        _positive_int(depth, "depth")
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        self.n_mels = n_mels
        self.frame_stride = frame_stride
        self.max_audio_tokens = max_audio_tokens
        self.frame_projection = nn.Conv1d(
            n_mels, d_model, kernel_size=frame_stride, stride=frame_stride
        )
        self.position = nn.Embedding(max_audio_tokens, d_model)
        self.encoder = _transformer(d_model, num_heads, depth)
        self.norm = nn.LayerNorm(d_model)

    def forward(
        self,
        features: Tensor,
        lengths: Tensor | None = None,
    ) -> tuple[Tensor, Tensor]:
        if not isinstance(features, Tensor) or features.ndim != 3:
            raise ValueError("audio features must have shape [B,n_mels,T]")
        if not features.is_floating_point():
            raise ValueError("audio features must be floating-point tensors")
        batch, n_mels, frames = features.shape
        stride = self.frame_stride
        if batch < 1 or n_mels != self.n_mels or frames < stride:
            raise ValueError("audio features need a non-empty batch, configured n_mels, and enough frames")
        if lengths is None:
            lengths = torch.full((batch,), frames, dtype=torch.long, device=features.device)
        elif (
            not isinstance(lengths, Tensor)
            or lengths.dtype != torch.long
            or tuple(lengths.shape) != (batch,)
            or lengths.device != features.device
        ):
            raise ValueError("lengths must be torch.long [B] on the feature device")
        if bool(((lengths < stride) | (lengths > frames)).any()):
            raise ValueError("each valid audio length must be between frame_stride and T")
        x = self.frame_projection(features).transpose(1, 2)
        if x.shape[1] > self.max_audio_tokens:
            raise ValueError("audio produces more tokens than max_audio_tokens")
        valid_tokens = torch.div(lengths, stride, rounding_mode="floor")
        padding_mask = (
            torch.arange(x.shape[1], device=features.device).unsqueeze(0)
            >= valid_tokens.unsqueeze(1)
        )
        positions = torch.arange(x.shape[1], device=features.device).unsqueeze(0)
        x = self.encoder(x + self.position(positions), src_key_padding_mask=padding_mask)
        x = self.norm(x).masked_fill(padding_mask.unsqueeze(-1), 0.0)
        return x, padding_mask


class TextCrossModalFusion(nn.Module):
    """Let text queries read image and audio token sequences via cross-attention."""

    def __init__(self, d_model: int, num_heads: int) -> None:
        super().__init__()
        _positive_int(d_model, "d_model")
        _positive_int(num_heads, "num_heads")
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        self.image_attention = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.audio_attention = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.norm1 = nn.LayerNorm(d_model)
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Linear(4 * d_model, d_model)
        )
        self.norm2 = nn.LayerNorm(d_model)

    def forward(
        self,
        text_tokens: Tensor,
        image_tokens: Tensor,
        audio_tokens: Tensor,
        text_padding_mask: Tensor,
        audio_padding_mask: Tensor,
    ) -> Tensor:
        image_context, _ = self.image_attention(
            text_tokens, image_tokens, image_tokens, need_weights=False
        )
        audio_context, _ = self.audio_attention(
            text_tokens,
            audio_tokens,
            audio_tokens,
            key_padding_mask=audio_padding_mask,
            need_weights=False,
        )
        fused = self.norm1(text_tokens + image_context + audio_context)
        fused = self.norm2(fused + self.feed_forward(fused))
        return fused.masked_fill(text_padding_mask.unsqueeze(-1), 0.0)


class TinyMultimodalAligner(nn.Module):
    """Three encoders with a shared space plus text-to-image/audio fusion.

    Inputs are normalized image tensors, text token IDs and log-Mel-like audio
    features. The returned shared embeddings suit contrastive retrieval demos;
    ``fused_text_tokens`` illustrates cross-attention but is not a generator.
    """

    def __init__(
        self,
        vocab_size: int = 64,
        *,
        pad_id: int = 0,
        n_mels: int = 16,
        d_model: int = 32,
        embed_dim: int = 16,
        num_heads: int = 4,
        patch_size: int = 8,
        max_image_patches: int = 256,
        max_text_length: int = 64,
        audio_frame_stride: int = 4,
        max_audio_tokens: int = 256,
        depth: int = 1,
    ) -> None:
        super().__init__()
        for name, value in (
            ("vocab_size", vocab_size), ("n_mels", n_mels), ("d_model", d_model),
            ("embed_dim", embed_dim), ("num_heads", num_heads), ("depth", depth),
        ):
            _positive_int(value, name)
        if d_model % num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        self.vision = VisionPatchEncoder(
            d_model, num_heads, patch_size=patch_size,
            max_patches=max_image_patches, depth=depth,
        )
        self.text = TextTokenEncoder(
            vocab_size, d_model, num_heads, pad_id=pad_id,
            max_length=max_text_length, depth=depth,
        )
        self.audio = AudioFrameEncoder(
            n_mels, d_model, num_heads, frame_stride=audio_frame_stride,
            max_audio_tokens=max_audio_tokens, depth=depth,
        )
        self.fusion = TextCrossModalFusion(d_model, num_heads)
        self.image_projection = nn.Linear(d_model, embed_dim)
        self.text_projection = nn.Linear(d_model, embed_dim)
        self.audio_projection = nn.Linear(d_model, embed_dim)
        self.fused_projection = nn.Linear(d_model, embed_dim)

    def forward(
        self,
        images: Tensor,
        token_ids: Tensor,
        audio_features: Tensor,
        *,
        text_padding_mask: Tensor | None = None,
        audio_lengths: Tensor | None = None,
    ) -> dict[str, Tensor]:
        if not all(isinstance(value, Tensor) for value in (images, token_ids, audio_features)):
            raise ValueError("all modality inputs must be tensors")
        if images.ndim != 4 or token_ids.ndim != 2 or audio_features.ndim != 3:
            raise ValueError("inputs must be images [B,C,H,W], tokens [B,L], and audio [B,F,T]")
        batch = images.shape[0]
        if token_ids.shape[0] != batch or audio_features.shape[0] != batch or batch < 1:
            raise ValueError("image, text, and audio batches must have the same non-zero size")
        if images.device != token_ids.device or images.device != audio_features.device:
            raise ValueError("all modalities must be on the same device")

        image_tokens = self.vision(images)
        text_tokens, text_mask = self.text(token_ids, text_padding_mask)
        audio_tokens, audio_mask = self.audio(audio_features, audio_lengths)
        image_pooled = image_tokens.mean(dim=1)
        text_pooled = _masked_mean(text_tokens, text_mask)
        audio_pooled = _masked_mean(audio_tokens, audio_mask)
        fused_text_tokens = self.fusion(
            text_tokens, image_tokens, audio_tokens, text_mask, audio_mask
        )
        fused_text_pooled = _masked_mean(fused_text_tokens, text_mask)

        return {
            "image_tokens": image_tokens,
            "text_tokens": text_tokens,
            "audio_tokens": audio_tokens,
            "audio_padding_mask": audio_mask,
            "text_padding_mask": text_mask,
            "fused_text_tokens": fused_text_tokens,
            "image_embedding": F.normalize(self.image_projection(image_pooled), dim=-1),
            "text_embedding": F.normalize(self.text_projection(text_pooled), dim=-1),
            "audio_embedding": F.normalize(self.audio_projection(audio_pooled), dim=-1),
            "fused_embedding": F.normalize(self.fused_projection(fused_text_pooled), dim=-1),
        }


def symmetric_info_nce(
    first: Tensor,
    second: Tensor,
    *,
    logit_scale: float = 10.0,
) -> Tensor:
    """Symmetric in-batch InfoNCE for aligned [B,D] pairs, with B >= 2.

    The diagonal entries are the positive pairs; other entries are negatives
    for this batch. ``logit_scale`` is a positive multiplier, not log(scale).
    """
    if not isinstance(first, Tensor) or not isinstance(second, Tensor):
        raise ValueError("first and second must be tensors")
    if first.ndim != 2 or second.ndim != 2 or first.shape != second.shape:
        raise ValueError("embeddings must share the same [B,D] shape")
    if first.shape[0] < 2 or first.shape[1] < 1:
        raise ValueError("InfoNCE needs at least two paired examples and one feature")
    if not first.is_floating_point() or not second.is_floating_point():
        raise ValueError("embeddings must be floating point")
    if first.device != second.device or first.dtype != second.dtype:
        raise ValueError("embeddings must share device and dtype")
    if (
        isinstance(logit_scale, bool)
        or not isinstance(logit_scale, (int, float))
        or not math.isfinite(logit_scale)
        or logit_scale <= 0
    ):
        raise ValueError("logit_scale must be a finite positive number")
    a = F.normalize(first, dim=-1)
    b = F.normalize(second, dim=-1)
    logits = logit_scale * (a @ b.transpose(0, 1))
    labels = torch.arange(first.shape[0], device=first.device)
    return (F.cross_entropy(logits, labels) + F.cross_entropy(logits.T, labels)) / 2


def three_way_contrastive_loss(
    image_embeddings: Tensor,
    text_embeddings: Tensor,
    audio_embeddings: Tensor,
    *,
    logit_scale: float = 10.0,
) -> Tensor:
    """Average symmetric image-text, image-audio and text-audio objectives."""
    return (
        symmetric_info_nce(image_embeddings, text_embeddings, logit_scale=logit_scale)
        + symmetric_info_nce(image_embeddings, audio_embeddings, logit_scale=logit_scale)
        + symmetric_info_nce(text_embeddings, audio_embeddings, logit_scale=logit_scale)
    ) / 3.0


def demo() -> None:
    torch.manual_seed(39)
    model = TinyMultimodalAligner(d_model=32, embed_dim=16, num_heads=4)
    images = torch.rand(4, 3, 32, 32)
    token_ids = torch.tensor([
        [1, 7, 8, 0, 0, 0],
        [1, 9, 10, 11, 0, 0],
        [1, 12, 13, 0, 0, 0],
        [1, 14, 15, 16, 17, 0],
    ], dtype=torch.long)
    audio = torch.randn(4, 16, 64)  # synthetic log-Mel-like features, not waveforms
    audio_lengths = torch.tensor([64, 56, 48, 40], dtype=torch.long)
    output = model(images, token_ids, audio, audio_lengths=audio_lengths)
    loss = three_way_contrastive_loss(
        output["image_embedding"], output["text_embedding"], output["audio_embedding"]
    )
    loss.backward()
    print(f"shared embeddings: {tuple(output['image_embedding'].shape)} per modality")
    print(f"fused text tokens: {tuple(output['fused_text_tokens'].shape)}")
    print(f"synthetic three-way InfoNCE: {loss.item():.4f}")
    print(f"finite loss and gradients: {bool(torch.isfinite(loss)) and model.vision.patch_projection.weight.grad is not None}")


if __name__ == "__main__":
    demo()
```
