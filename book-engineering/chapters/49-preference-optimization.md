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
