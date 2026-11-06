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
