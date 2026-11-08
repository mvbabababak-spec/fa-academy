# جلد چهارم، فصل ۷ — تولید تصویر و ویدئو، Diffusion و شرط‌گذاری چندوجهی

**فصل محلی ۷ از ۱۵ فصل جلد چهارم = فصل سراسری ۵۳**\
**The Art & Science of Building Intelligence | Babak & Ai**\
**تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶**

> **مرز موضوع:** فصل ۵۱ رمزگذار تصویر و هم‌ترازی متن–تصویر را بررسی کرد؛ فصل ۵۲ چرخهٔ صوت و گفتار بود. این فصل از «فهم تصویر» به «ساخت تصویر/ویدئو» می‌رود: فرایند diffusion، sampling، latent، cross-attention و مدل‌های چندوجهی، سپس ارزیابی، حقوق و ایمنی محتوا. فصل ۵۴ دربارهٔ برآورد منابع است و هزینهٔ سخت‌افزاری را به‌صورت پروژهٔ مستقل ادامه می‌دهد. این فصل نه آموزش مدل واقعی است و نه توصیهٔ حقوقی.

## ۱. اول خروجی و شرط را تعریف کنید

«تولید تصویر» یک وظیفهٔ واحد نیست. سامانه ممکن است از متن تصویر بسازد، تصویر موجود را با متن ویرایش کند، بخشی از تصویر را بازسازی کند، یا از تصویر و متن یک کلیپ بسازد. در تولید ویدئو علاوه بر شباهت به prompt، ترتیب زمانی و پایداری اشیا نیز اهمیت دارد.

| وظیفه | شرط ورودی | خروجی | پرسش ارزیابی نمونه |
|---|---|---|---|
| text-to-image | متن، اندازه و گاهی seed | یک تصویر | آیا اشیای خواسته‌شده و رابطهٔ میانشان درست‌اند؟ |
| image-to-image / edit | تصویر مرجع و دستور | تصویر ویرایش‌شده | آیا تغییر خواسته‌شده انجام شد و بخش‌های دیگر حفظ شدند؟ |
| inpainting | تصویر، mask و گاهی متن | ناحیهٔ بازسازی‌شده | آیا مرز وصله و سازگاری با زمینه مناسب است؟ |
| text-to-video | متن، مدت و تنظیمات نمونه‌گیری | دنبالهٔ فریم‌ها | آیا رخدادها در ترتیب و زمان درست اتفاق می‌افتند؟ |
| image-to-video | تصویر آغازین و دستور حرکت | کلیپ | آیا حرکت افزوده شد بی‌آنکه هویت و ترکیب ناخواسته عوض شود؟ |

![شکل ۴-۷-۱ — مسیر شماتیک diffusion شرطی از latent نویزی تا تصویر یا چند فریم؛ مسیر پیش‌رو، cross-attention و نقاط جداگانهٔ ارزیابی، حقوق، ایمنی و provenance را نشان می‌دهد.](book-engineering/diagrams/v4-ch07-diffusion.svg)

شکل ۴-۷-۱ — دیاگرام آموزشی است، نه تصویر تولیدشده با مدل یا نتیجهٔ آزمایش کیفیت.

برای طراحی سامانه، ورودی، خروجی، محدودیت اندازه/مدت، مجوز استفاده، مخاطب و هزینهٔ خطا را پیش از انتخاب checkpoint ثبت کنید. «عکس زیباست» معیار کافی نیست اگر وظیفه حفظ نوشته، شمار اشیا، ترتیب رویداد، هویت یک فرد یا رضایت صاحب تصویر را می‌طلبد.

## ۲. Diffusion به‌صورت فرایند پیش‌رو و معکوس

در یک فرایند گسستهٔ رایج، گام پیش‌رو از دادهٔ پاک کمی نویز Gaussian می‌سازد. در نمادگذاری DDPM، β<sub>t</sub> مقدار نویزِ افزوده‌شده در گام t و α<sub>t</sub>=1−β<sub>t</sub> ضریب باقی‌ماندهٔ سیگنال است. حاصل‌ضرب ᾱ<sub>t</sub> نشان می‌دهد تا آن گام چه سهمی از سیگنال اصلی باقی مانده است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="در هر گام پیش‌رو، x با میانگین ریشهٔ آلفا ضرب‌در x قبلی و واریانس بتا نویزی می‌شود؛ آلفا برابر یک منهای بتا و آلفا بار حاصل‌ضرب تجمعی آلفاست">
  <mrow>
    <mi>q</mi><mo>(</mo><msub><mi>x</mi><mi>t</mi></msub><mo>|</mo><msub><mi>x</mi><mrow><mi>t</mi><mo>−</mo><mn>1</mn></mrow></msub><mo>)</mo>
    <mo>=</mo><mi mathvariant="normal">𝒩</mi><mo>(</mo>
    <msqrt><msub><mi>α</mi><mi>t</mi></msub></msqrt><msub><mi>x</mi><mrow><mi>t</mi><mo>−</mo><mn>1</mn></mrow></msub><mo>,</mo>
    <msub><mi>β</mi><mi>t</mi></msub><mi mathvariant="normal">I</mi><mo>)</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** `q(x_t | x_{t−1}) = N(√α_t x_{t−1}, β_t I)`، با `α_t = 1−β_t` و `ᾱ_t = ∏_{s=1}^{t} α_s`. در این نگارش، `β_t` باید بین صفر و یک باشد.

با تکرار گام‌ها، نسخهٔ پرنویزتر به‌دست می‌آید. مدل در جهت معکوس، از یک prior نویزی شروع می‌کند و طی چند گام مقدار قبلی را تخمین می‌زند. این صورت‌بندی یک چارچوب احتمالاتی است؛ خودِ آن نه تضمین می‌کند خروجی واقعی باشد و نه تضمین می‌کند prompt را کامل بفهمد. [۱]

## ۳. نمونه‌گیری مستقیم از هر سطح نویز

برای آموزش لازم نیست هزار گام کوچک را برای هر نمونه اجرا کنیم. با ترکیب گام‌های Gaussian می‌توان مستقیماً نمونهٔ زمان t را ساخت:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="نمونهٔ نویزی x در زمان t برابر ریشهٔ آلفا بار ضرب‌در دادهٔ پاک، به‌علاوهٔ ریشهٔ یک منهای آلفا بار ضرب‌در نویز استاندارد اپسیلون است">
  <mrow>
    <msub><mi>x</mi><mi>t</mi></msub><mo>=</mo>
    <msqrt><msub><mover><mi>α</mi><mo>¯</mo></mover><mi>t</mi></msub></msqrt><msub><mi>x</mi><mn>0</mn></msub>
    <mo>+</mo>
    <msqrt><mrow><mn>1</mn><mo>−</mo><msub><mover><mi>α</mi><mo>¯</mo></mover><mi>t</mi></msub></mrow></msqrt><mi>ε</mi>
  </mrow>
</math>

**متن جایگزین فرمول:** `x_t = √ᾱ_t x_0 + √(1−ᾱ_t) ε`؛ `ε` از نرمال استاندارد گرفته می‌شود. در انتهای طیف نویز، `x_t` بیشتر شبیه نویز می‌شود، اما میزان نزدیکی به prior به schedule و داده وابسته است.

این رابطه برای آزمودن shape، dtype و صحت داده مفید است: یک تصویر واقعی را در زمان تصادفی انتخاب کنید، نویز معلوم بسازید و `x_t` را مستقیم محاسبه کنید. در آموزش، هدف معمول آن است که شبکه از `x_t`، زمان t و شرط c، متغیری مرتبط با نویز یا دادهٔ پاک را پیش‌بینی کند.

## ۴. تابع هدف و پارامتردهی مدل

یک هدف متداول، کمینه‌کردن خطای مربعی میان نویز افزوده‌شده و پیش‌بینی شبکه است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="زیان سادهٔ diffusion امید ریاضی خطای مربعی میان نویز واقعی اپسیلون و پیش‌بینی شبکه از x در زمان t با شرط c است">
  <mrow>
    <msub><mi>ℒ</mi><mtext>simple</mtext></msub><mo>=</mo>
    <msub><mi>𝔼</mi><mrow><msub><mi>x</mi><mn>0</mn></msub><mo>,</mo><mi>ε</mi><mo>,</mo><mi>t</mi><mo>,</mo><mi>c</mi></mrow></msub>
    <mo>[</mo><msup><mrow><msub><mo>∥</mo><mn>2</mn></msub>
    <mrow><mi>ε</mi><mo>−</mo><msub><mi>ε</mi><mi>θ</mi></msub><mo>(</mo><msub><mi>x</mi><mi>t</mi></msub><mo>,</mo><mi>t</mi><mo>,</mo><mi>c</mi><mo>)</mo></mrow>
    <msub><mo>∥</mo><mn>2</mn></msub></mrow><mn>2</mn></msup><mo>]</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** `L_simple = E_{x0, ε, t}[ || ε − ε_θ(x_t, t, c) ||² ]`. صورت دقیق loss، وزن‌دهی به زمان‌ها، متغیر هدف و شرط‌دهی میان پیاده‌سازی‌ها فرق می‌کند.

بعضی مدل‌ها نویز `ε` را پیش‌بینی می‌کنند؛ برخی `x₀` یا پارامتردهی‌ای مانند velocity را به‌کار می‌گیرند. این تغییر صرفاً عوض‌کردن نام خروجی نیست: هدف آموزشی و فرمول تبدیل پیش‌بینی به گام معکوس با هم سازگار می‌شوند. برای مقایسهٔ دو مقاله یا checkpoint باید هدف آموزش، prediction type، schedule و sampler را کنار هم دید.

## ۵. Score و میانگین گام معکوس

Score گرادیان لگاریتم چگالی در نقطهٔ جاری است. در حالت Gaussian، رابطهٔ آن با نویز شرطی کمک می‌کند خروجی یک مدل نویز‌پیش‌بین را به حرکت معکوس تبدیل کنیم:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="score توزیع نویزی در زمان t برابر منفی امید نویز شرطی بر x_t تقسیم بر ریشهٔ یک منهای آلفا بار است">
  <mrow>
    <msub><mi>∇</mi><msub><mi>x</mi><mi>t</mi></msub></msub>
    <mi>log</mi><msub><mi>q</mi><mi>t</mi></msub><mo>(</mo><msub><mi>x</mi><mi>t</mi></msub><mo>)</mo>
    <mo>=</mo><mo>−</mo>
    <mfrac><mrow><msub><mi>𝔼</mi><mi>ε</mi></msub><mo>[</mo><mi>ε</mi><mo>|</mo><msub><mi>x</mi><mi>t</mi></msub><mo>]</mo></mrow>
      <msqrt><mrow><mn>1</mn><mo>−</mo><msub><mover><mi>α</mi><mo>¯</mo></mover><mi>t</mi></msub></mrow></msqrt>
    </mfrac>
  </mrow>
</math>

**متن جایگزین فرمول:** `∇_{x_t} log q_t(x_t) = −E[ε | x_t] / √(1−ᾱ_t)`. این رابطه از فرض فرایند Gaussian پیش‌رو می‌آید؛ در عمل شبکه مقدار شرطی را تقریب می‌زند.

در DDPM، میانگین یک گام reverse را می‌توان با پیش‌بینی نویز نوشت:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="میانگین reverse در DDPM برابر یک تقسیم بر ریشهٔ آلفا ضرب‌در x_t منهای بتا تقسیم بر ریشهٔ یک منهای آلفا بار، ضرب‌در نویز پیش‌بینی‌شده است">
  <mrow>
    <msub><mi>μ</mi><mi>θ</mi></msub><mo>(</mo><msub><mi>x</mi><mi>t</mi></msub><mo>,</mo><mi>t</mi><mo>,</mo><mi>c</mi><mo>)</mo><mo>=</mo>
    <mfrac><mn>1</mn><msqrt><msub><mi>α</mi><mi>t</mi></msub></msqrt></mfrac>
    <mo>(</mo><msub><mi>x</mi><mi>t</mi></msub><mo>−</mo>
    <mfrac><msub><mi>β</mi><mi>t</mi></msub><msqrt><mrow><mn>1</mn><mo>−</mo><msub><mover><mi>α</mi><mo>¯</mo></mover><mi>t</mi></msub></mrow></msqrt></mfrac>
    <msub><mi>ε</mi><mi>θ</mi></msub><mo>(</mo><msub><mi>x</mi><mi>t</mi></msub><mo>,</mo><mi>t</mi><mo>,</mo><mi>c</mi><mo>)</mo><mo>)</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** `μ_θ = 1/√α_t · (x_t − β_t/√(1−ᾱ_t) · ε_θ(x_t,t,c))`. مدل، posterior را با توزیع reverse پارامتردهی‌شده تقریب می‌زند؛ sample نهایی تابع sampler و نویزهای گام‌های معکوس نیز هست.

در یک قرارداد رایج، واریانس posterior شرطیِ `q(x_{t−1} | x_t, x₀)` چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="واریانس بتا tilde در posterior دی دی پی ام برابر بتا در زمان t ضرب‌در یک منهای آلفا بار در زمان t منهای یک، تقسیم بر یک منهای آلفا بار در زمان t است">
  <mrow>
    <msub><mover><mi>β</mi><mo>˜</mo></mover><mi>t</mi></msub><mo>=</mo>
    <mfrac>
      <mrow><msub><mi>β</mi><mi>t</mi></msub><mo>(</mo><mn>1</mn><mo>−</mo><msub><mover><mi>α</mi><mo>¯</mo></mover><mrow><mi>t</mi><mo>−</mo><mn>1</mn></mrow></msub><mo>)</mo></mrow>
      <mrow><mn>1</mn><mo>−</mo><msub><mover><mi>α</mi><mo>¯</mo></mover><mi>t</mi></msub></mrow>
    </mfrac>
  </mrow>
</math>

**متن جایگزین فرمول:** `β̃_t = β_t (1−ᾱ_{t−1})/(1−ᾱ_t)`, با `ᾱ₀=1`؛ بنابراین واریانس گام آخر `t=1` صفر است. این واریانسِ posterior با هر انتخاب ممکن برای variance مدل reverse یکی نیست.

فرمول‌های این فصل از `t=1` تا `T` شماره‌گذاری می‌شوند؛ کد آموزشی شاخص آرایه را از صفر می‌گیرد. پس شاخص کد `i` متناظر گام ریاضی `t=i+1` است و `t=0` در کد، همان گام نهاییِ بدون نویزِ فرمولی است.

## ۶. DDPM، DDIM و برنامهٔ نمونه‌گیری

DDPM برای reverse transition از میانگین تخمینی و واریانس تعیین‌شده استفاده می‌کند؛ در گام آخر معمولاً noise تازه افزوده نمی‌شود. DDIM مسیر نمونه‌گیری دیگری را برای همان خانوادهٔ مدل‌های آموزش‌دیده صورت‌بندی می‌کند و در حالت‌های رایج می‌تواند با تعداد گام کمتر اجرا شود. نتیجه به schedule، تعداد گام، پارامتردهی شبکه و نسخهٔ sampler وابسته است؛ «گام کمتر» به‌تنهایی تضمین کیفیت یا سرعتِ سرراست نیست. [۲]

در مستندات آزمایش، دست‌کم model/checkpoint و revision، tokenizer یا text encoder، resolution، seed، scheduler، شمار گام‌ها، guidance و تنظیمات decode را ثبت کنید. بدون این مشخصات، دو نمونهٔ ظاهراً مشابه ممکن است آزمایش قابل‌مقایسه‌ای نباشند.

## ۷. شرط‌دهی و Classifier-Free Guidance

برای متن‌به‌تصویر، مدل معمولاً یک پیش‌بینی بی‌شرط و یک پیش‌بینی شرطی می‌سازد و آن‌ها را ترکیب می‌کند. یک convention رایج برای classifier-free guidance چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="در یک قرارداد رایج CFG، پیش‌بینی guided برابر پیش‌بینی بی‌شرط به‌علاوهٔ s ضرب‌در اختلاف پیش‌بینی شرطی و بی‌شرط است">
  <mrow>
    <msub><mi>ε</mi><mtext>guided</mtext></msub><mo>=</mo>
    <msub><mi>ε</mi><mtext>uncond</mtext></msub><mo>+</mo>
    <mi>s</mi><mo>(</mo><msub><mi>ε</mi><mtext>cond</mtext></msub><mo>−</mo><msub><mi>ε</mi><mtext>uncond</mtext></msub><mo>)</mo>
  </mrow>
</math>

**متن جایگزین فرمول:** `ε_guided = ε_uncond + s(ε_cond − ε_uncond)`. این یکی از قراردادهای رایج است؛ مقدار `s` را با نام و معنای همان پیاده‌سازی گزارش کنید. [۳]

افزایش guidance اغلب فشار شرط را بیشتر می‌کند، اما می‌تواند تنوع نمونه یا تعادل بصری را تغییر دهد. مقدار بزرگ‌تر تضمین نمی‌کند همهٔ روابط پیچیده، واژه‌های داخل تصویر یا الزامات ایمنی رعایت شوند. CFG ابزار کنترلِ sampling است، نه جایگزین آزمون prompt و سیاست ایمنی.

## ۸. Latent diffusion: کاهش محاسبه در برابر جزئیات

Latent Diffusion Model تصویر را با autoencoder به نمایش فشرده‌تر می‌برد، diffusion را در latent اجرا می‌کند و در انتها latent را decode می‌کند. این کار معمولاً فضای نمونه‌گیری را کوچک می‌کند، اما کیفیت خروجی به decoder، فشرده‌سازی و جزئیات نمایش وابسته می‌ماند. مدل latent ممکن است جزئیاتی را که encoder حذف کرده، دقیق بازسازی نکند؛ artifactهای VAE هم می‌توانند از artifactهای denoiser جداگانه باشند. [۴]

پس برای عیب‌یابی خروجی، سه مرحله را از هم جدا کنید: (۱) کیفیت ورودی و encoding، (۲) کیفیت latent و denoising، (۳) decode، upscale و post-processing. رزولوشن بالاتر را صرفاً با برچسب «latent» ارزان فرض نکنید؛ شمار tokenها، فضای attention و حافظهٔ فعال‌سازی‌ها همچنان مهم‌اند.

## ۹. Cross-Attention: واردکردن متن به مسیر تصویر

در cross-attention، queryها می‌توانند از tokenهای تصویر/latent بیایند، در حالی که key و value از نمایش متن ساخته می‌شوند. در یک لایهٔ رایج:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="توجه متقاطع برابر softmax ماتریس Q ضرب‌در ترانهادهٔ K، تقسیم بر ریشهٔ d، سپس ضرب‌در V است؛ Q از latent و K و V از شرط می‌آیند">
  <mrow>
    <mtext>CrossAttn</mtext><mo>(</mo><mi>Q</mi><mo>,</mo><mi>K</mi><mo>,</mo><mi>V</mi><mo>)</mo><mo>=</mo>
    <mi>softmax</mi><mo>(</mo>
    <mfrac><mrow><mi>Q</mi><msup><mi>K</mi><mi>T</mi></msup></mrow><msqrt><mi>d</mi></msqrt></mfrac>
    <mo>)</mo><mi>V</mi>
  </mrow>
</math>

**متن جایگزین فرمول:** `CrossAttn(Q,K,V) = softmax(QKᵀ / √d)V`؛ معمولاً `Q` از tokenهای تصویری/latent و `K,V` از embeddingهای شرط می‌آیند. شکل دقیق لایه و مسیر تبادل اطلاعات به معماری بستگی دارد.

این اتصال، متن را در چند لایه به فرایند تصویری می‌رساند؛ به معنای «ترجمهٔ دقیق prompt به پیکسل» نیست. اگر tokenizer یک نام یا رابطه را خوب بازنمایی نکند، یا مدل دادهٔ کافی برای مفهوم نداشته باشد، cross-attention نیز به‌تنهایی آن را حل نمی‌کند. LDMها از cross-attention برای شرط‌هایی مانند متن و bounding box استفاده کردند، اما معماری‌های بعدی می‌توانند attention مشترک یا راه‌های شرط‌دهی دیگری داشته باشند. [۴]

## ۱۰. U-Net، Diffusion Transformer و تبادل چندوجهی

در U-Net، نمایش‌های مکانی در چند مقیاس پایین و بالا می‌روند و skip connectionها جزئیات را میان مسیرها جابه‌جا می‌کنند. در Diffusion Transformer، تصویر یا latent به patch/token تبدیل و در بلوک‌های transformer پردازش می‌شود؛ timestep و شرط نیز به‌صورت embedding یا token وارد مدل می‌شوند. DiT مقالهٔ Peebles و Xie نشان می‌دهد که transformer را می‌توان به backbone مدل diffusion در فضای latent تبدیل کرد؛ نتیجهٔ آن مقاله را به همهٔ مدل‌ها یا داده‌ها تعمیم ندهید. [۵]

برخی معماری‌های چندوجهی برای تصویر و متن پارامترها یا مسیرهای جدا دارند و تبادل را با joint attention انجام می‌دهند. MM-DiT در گزارش نویسندگان مدل‌های خانوادهٔ Flux، از جریان اطلاعات میان tokenهای متن و تصویر استفاده می‌کند؛ این نمونه را نباید با loss کلاسیک DDPM یکی گرفت، چون گزارش آن از rectified flow استفاده می‌کند. [۶]

## ۱۱. ویدئو: زمان، هویت و ترتیب رخداد

ویدئو یک stack از تصویرهای مستقل نیست. اگر مدل هر فریم را جداگانه تولید کند، ممکن است شیء میان فریم‌ها تغییر شکل یا هویت دهد؛ اگر همهٔ فریم‌ها را به مدل بدهد، طول دنبالهٔ token و محاسبه بیشتر می‌شود. معماری‌ها ممکن است ابتدا ویدئو را در latent زمانی/مکانی فشرده کنند، سپس آن را به patchهای فضا–زمان تبدیل کنند یا attention مکانی و زمانی را جداگانه اعمال کنند.

گزارش فنی Sora، مدل نویسندگان را diffusion transformer روی patchهای latent فضا–زمان توصیف می‌کند و تصاویر را حالت تک‌فریمی می‌گیرد. همان گزارش محدودیت‌هایی مانند ناسازگاری فیزیکی، تغییر نادرست حالت اشیا و ناپیوستگی بعضی نمونه‌های طولانی را نیز بیان می‌کند؛ «ظاهر واقع‌نما» به معنی شبیه‌ساز معتبر فیزیک نیست. [۷] HunyuanVideo و Wan نیز گزارش‌های فنی خود را دربارهٔ latent و معماری video transformer منتشر کرده‌اند؛ مشخصات، وزن‌ها، مجوز و نیازمندی اجرایی را برای نسخهٔ دقیق همان مخزن/مدل بخوانید. [۸، ۹]

## ۱۲. Flow Matching و Rectified Flow با DDPM یکی نیستند

بسیاری از مدل‌های جدید همچنان از توزیع noise و مسیر تدریجی استفاده می‌کنند، اما آموزشِ vector field می‌تواند بر پایهٔ flow matching یا rectified flow باشد. Flow matching یک میدان سرعت را روی مسیرهای احتمال رگرس می‌کند؛ rectified flow تلاش می‌کند مسیر انتقال داده و نویز را مستقیم‌تر کند. این‌ها با مدل diffusion کلاسیک هم‌پوشانی مفهومی دارند، اما objective، مسیر و sampler را نباید صرفاً با واژهٔ «DDPM» یکی دانست. [۱۰، ۱۱]

در گزارش یا کد پژوهشی، نام دقیق objective، نوع target، solver و زمان‌بندی را ثبت کنید. مقایسهٔ تعداد گام‌ها بدون یکسان‌کردن یا توضیح این موارد می‌تواند گمراه‌کننده باشد.

## ۱۳. کنترل، ویرایش و ورودی مرجع

کنترل ممکن است از prompt، تصویر مرجع، mask، depth/pose، edge، تصویر آغازین یا tokenهای شرط دیگر بیاید. در image-to-image مقدار نویز افزوده‌شده به ورودی معمولاً توازن میان حفظ ساختار و تغییر را کنترل می‌کند؛ در inpainting مرز mask و روش ترکیب ناحیهٔ بازسازی‌شده اهمیت دارد. مدل‌های video-editing می‌توانند از فریم‌های مرجع یا clip قبلی شرط بگیرند، اما حفظ هویت و جزئیات در همهٔ زمان‌ها تضمین نمی‌شود.

پروتکل آزمون باید بگوید چه چیزی باید تغییر کند و چه چیزی نباید تغییر کند. برای مثال، در ویرایش یک شیء، prompt پیروی از دستور، حفظ هویت، سازگاری پس‌زمینه و artifact روی مرز را جدا بسنجید؛ یک امتیاز کلی ممکن است شکست در شرط «حفظ» را پنهان کند.

## ۱۴. هزینهٔ استنتاج را به اجزا بشکنید

برای تصویر، تعداد tokenها با رزولوشن و patch/latent stride تغییر می‌کند؛ برای ویدئو، تعداد فریم‌ها نیز وارد می‌شود. یک تقریب ساده برای شمار tokenهای تصویری این است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="تعداد tokenهای تصویر تقریباً برابر تعداد patchها در راستای ارتفاع ضرب‌در تعداد patchها در راستای عرض است">
  <mrow>
    <msub><mi>N</mi><mtext>image</mtext></msub><mo>≈</mo>
    <mfrac><mi>H</mi><msub><mi>p</mi><mi>h</mi></msub></mfrac>
    <mo>×</mo>
    <mfrac><mi>W</mi><msub><mi>p</mi><mi>w</mi></msub></mfrac>
  </mrow>
</math>

**متن جایگزین فرمول:** `N_image ≈ (H / p_h) × (W / p_w)`؛ این شمارش سادهٔ patch است، نه مدل دقیق حافظه یا زمان اجرا.

اگر attention سراسری متراکم روی N token باشد، ماتریس جفتی آن می‌تواند مرتبهٔ `N²` داشته باشد؛ معماری‌های واقعی ممکن است پنجره، فاکتورگیری مکانی/زمانی، sparse attention یا routing به‌کار گیرند. ویدئو با T فریم و tokenهای مکانی-زمانی می‌تواند دنباله‌ای بسیار بزرگ‌تر بسازد. هزینهٔ عملی علاوه بر denoiser شامل text encoder، VAE، decoder، تعداد گام‌ها، batch و انتقال داده است. برای سخت‌افزار و benchmark به فصل ۵۴ و اندازه‌گیری واقعی همان محیط مراجعه کنید.

## ۱۵. ارزیابی تصویر: وظیفه را به سنجه وصل کنید

هیچ معیار تصویری منفردی «کیفیت» را کامل نمی‌سنجد. FID توزیع ویژگی‌های مجموعه‌ای از نمونه‌ها را با مرجع مقایسه می‌کند؛ به‌تنهایی پیروی prompt، صحت رابطه‌های مکانی، نوشتهٔ خوانا یا ارزش کاربری یک تصویر را اثبات نمی‌کند. شباهت embedding متنی–تصویری می‌تواند با هم‌ترازی کلی مرتبط باشد، اما جزئیات شمارش، negation، ترتیب و متن درون تصویر را ممکن است از دست بدهد.

برای ارزیابی هدف‌محور، معیارها را تفکیک کنید: هم‌ترازی مفهومی، اشیای خواسته/ناخواسته، رابطهٔ مکانی، خوانایی متن، کیفیت فنی، تنوع، حفظ مرجع در ویرایش و قضاوت انسانیِ blind. promptها، seedها، نسخهٔ مدل و پارامترهای sampling را از پیش ثبت کنید؛ اگر metric یا judge خودش مدل است، نسخه، bias و خطای آن را هم گزارش دهید. نتیجهٔ یک prompt یا یک seed شاهد قابل‌اتکا برای مدل نیست.

## ۱۶. ارزیابی ویدئو: کیفیت زمانی را جدا بسنجید

برای کلیپ، پرسش‌هایی مانند هویت و ظاهر شیء در طول زمان، یکنواختی حرکت، flicker، زمان رخداد، سازگاری camera motion، پیروی از prompt و plausibility فیزیکی جدا هستند. VBench++ ابعاد متعددی از کیفیت ویدئو را تجزیه می‌کند؛ VBench-2.0 بر «intrinsic faithfulness» مانند فیزیک و commonsense تمرکز می‌کند. این benchmarkها ابزارهای سنجش‌اند، نه قاضی نهایی؛ پوشش prompt، evaluator و نسخهٔ benchmark را گزارش کنید. [۱۲، ۱۳]

در مقایسهٔ مدل‌ها، طول کلیپ، FPS، رزولوشن، seed و شرایط نمونه‌گیری را یکسان یا صریح ثبت کنید. نمونه‌های انتخاب‌شده برای نمایش را از مجموعهٔ آزمون تفکیک کنید و نتایج را بر حسب دستهٔ prompt و نوع شکست نیز نشان دهید. اگر کاربرد به ترتیب یا زمان وابسته است، یک امتیاز زیبایی‌شناختی جایگزین آزمون زمانی نیست.

## ۱۷. داده، حقوق و زنجیرهٔ نگه‌داری

دادهٔ آموزش ممکن است تصویر، ویدئو، caption، metadata و اطلاعات چهره/مکان داشته باشد. قبل از استفاده، مالکیت یا مجوز مجموعه، محدودیت بازتوزیع، رضایت اشخاص، provenance، حذف duplicate، کیفیت caption و سیاست نگه‌داری را بررسی کنید. مجوز وزن مدل، خودبه‌خود مجوز تک‌تک نمونه‌های training یا حق استفاده از likeness افراد را اثبات نمی‌کند؛ شرایط سرویس و نسخهٔ مدل هم ممکن است تغییر کنند.

ثبت منشأ داده، filterهای اعمال‌شده، تاریخ و version dataset، حذف‌ها و تغییرات preprocess به بازبینی کمک می‌کند؛ اما به‌تنهایی اثبات نمی‌کند که هیچ محتوای مشکل‌داری در داده یا خروجی نیست. اگر مدل برای محصول است، مسئولیت review و پاسخ به شکایت، علاوه بر انتخاب checkpoint، بخشی از طراحی است.

## ۱۸. Copyright: آموزش، خروجی و مجوز را قاطی نکنید

سه پرسش جدا وجود دارد: آیا استفاده از اثر برای آموزش مجاز بوده است؟ آیا خروجی یا بخش‌هایی از آن حقوق شخص یا اثر دیگری را درگیر می‌کند؟ و چه نوع حمایتی بر تغییرات انسانیِ خروجی اعمال می‌شود؟ پاسخ به این پرسش‌ها به jurisdiction، واقعیت‌ها، قرارداد و قانون جاری وابسته است؛ یک توضیح فنی یا مجوز مدل پاسخ حقوقی نمی‌دهد.

صفحهٔ رسمی U.S. Copyright Office گزارش Part 2 دربارهٔ copyrightability خروجی‌های هوش مولد را در ۲۹ ژانویهٔ ۲۰۲۵ منتشرشده معرفی می‌کند؛ Part 3 دربارهٔ آموزش روی آثار دارای copyright را در نسخهٔ **pre-publication** مورخ ۹ مه ۲۰۲۵ فهرست می‌کند و می‌گوید نسخهٔ نهایی در آینده خواهد آمد. این وضعیت را به نظر حقوقی قطعی برای هر پرونده تبدیل نکنید و پیش از استفادهٔ تجاری، وضعیت فعلی منبع، قوانین و مشاور واجدصلاحیت را بررسی کنید. [۱۴، ۱۵]

در کار عملی، منبع و نسخهٔ مدل، شرایط مجوز، روش تولید، و هر ویرایش انسانی را مستند کنید؛ از بازتولید عمدی اثر مشخص یا likeness حساس بدون مجوز/رضایت خودداری کنید. این توصیهٔ احتیاطی است، نه حکم دربارهٔ قانونی‌بودن یک prompt یا خروجی خاص.

## ۱۹. ایمنی محتوا و رضایت

مولدهای تصویر و ویدئو می‌توانند برای جعل هویت، تصویر صمیمیِ بدون رضایت، فریب، آزار، محتوای خشونت‌آمیز یا آسیب به افراد به‌کار روند. سامانهٔ مسئول باید **چند لایه** داشته باشد: سیاست روشن، مدیریت دسترسی، بازبینی input/output متناسب با ریسک، رسیدگی انسانی، راه گزارش/اعتراض، ثبت رخدادِ حداقلی و حفاظت از داده. برای محتوای حساسِ مربوط به شخص واقعی، رضایت و حق استفاده از تصویر/صدا را پیش از تولید/انتشار بررسی کنید.

فیلتر خودکار هم false positive و هم false negative دارد؛ آن را تضمین ایمنی ننامید. همچنین watermark، برچسب «ساخته‌شده با AI» یا C2PA به‌تنهایی محتوای زیان‌بار را بی‌خطر، قانونی یا درست نمی‌کند. دسترسی محدودتر و review بیشتر را برای پیامدهای بالقوهٔ شدید در نظر بگیرید.

## ۲۰. Provenance: C2PA چه چیزی را ثبت می‌کند؟

C2PA سازوکاری برای ذخیره و دسترسی به manifestهای منشأ محتوا با امضاهای دیجیتال و شواهدِ تغییرناپذیریِ دستکاری است. چنین credentialی می‌تواند اعلام کند چه ابزار/اقدامی به زنجیرهٔ منشأ اضافه شده و آیا manifest با کلید/اعتماد تعریف‌شده قابل‌بررسی است. specification آن، «trustworthiness» را در یک trust model تعریف‌شده ارزیابی می‌کند؛ این با اثبات حقیقت صحنه یا صحت ادعای متن روی تصویر فرق دارد. [۱۶]

manifest ممکن است در تبدیل یا انتشار حذف شود و همهٔ فایل‌ها نیز الزاماً credential ندارند. **وجود امضای معتبر** می‌تواند شاهدی دربارهٔ امضاکننده و دست‌کاری manifest باشد؛ **نبود credential** به‌تنهایی نشان نمی‌دهد فایل جعلی است. برای محصول، منشأ را همراه با consent، policy و انسانی که برای مخاطب لازم است توضیح دهید.

## ۲۱. چند نمونهٔ پژوهشی جدید، با مرز ادعا

- گزارش OpenAI دربارهٔ Sora مدل را diffusion transformer روی patchهای latent ویدئو/تصویر توصیف می‌کند؛ گزارش به‌صراحت برخی محدودیت‌های فیزیک و تداوم را نیز می‌پذیرد. این یک گزارش فنیِ سازنده است و جزئیات پیاده‌سازی کامل را منتشر نمی‌کند. [۷]
- گزارش HunyuanVideo و مقاله/مخزن Wan خانواده‌هایی از معماری‌های ویدئویی و وزن‌های متن‌باز را توصیف می‌کنند. از هر مدل فقط مشخصات همان revision و license را بخوانید؛ عنوان «open» به معنی مناسب‌بودن خودکار برای هر استفاده نیست. [۸، ۹]
- **Motif-Video 2B** و **Temporal Specification Guidance** نمونه‌های preprint در ۲۰۲۶ هستند: اولی specialization معماری/attention را گزارش می‌کند؛ دومی قیدهای زمانی را هنگام sampling می‌آزماید. اعداد یا مقایسه‌های benchmark، ادعای نویسندگان روی setup خودشان‌اند و در این فصل بازتولید نشده‌اند. [۱۷، ۱۸]
- **Mage-Flow** نیز در ۲۰۲۶ به‌صورت preprint یک pipeline تصویر مبتنی بر rectified flow و transformer را گزارش می‌کند. claims مربوط به throughput یا latency را به hardware، resolution، نسخه و آزمایش نویسندگان محدود کنید؛ این فصل آن‌ها را اندازه‌گیری نکرده است. [۱۹]

برای مقالهٔ جدید، ابتدا سؤال پژوهش، داده و split، نسخهٔ مدل، معیار و baseline را بررسی کنید. عنوانی مانند «world model» یا «fast» خودش شاهد تعمیم، صحت فیزیکی، کیفیت زبان یا تناسب حقوقی نیست.

## ۲۲. آزمایشگاه CPU: sampler تحلیلی، نه مولد تصویر

پروژهٔ این فصل در [`projects/53-diffusion-lab/README.md`](book-engineering/projects/53-diffusion-lab/README.md) قرار دارد. fixture، چهار Gaussian دوبعدی با مرکزهای متقارن و واریانس مشخص دارد. برنامهٔ `diffusion_lab.py` schedule خطی می‌سازد، noising بسته‌بسته را آزمون می‌کند، score دقیق چگالی معلوم را محاسبه می‌کند و از آن برای گام‌های معکوس DDPM استفاده می‌کند. وزن شبکه‌ای آموزش داده نشده است؛ score معلوم از ساختار fixture می‌آید.

این انتخاب عمدی است: می‌توان رابطهٔ `score ↔ ε` و واریانس posterior را با آزمون مستقل بررسی کرد، بی‌آنکه download مدل، GPU، دادهٔ تصویر یا ویدئو لازم باشد. در نمونه‌گیری واقعی، score از شبکهٔ آموزش‌دیده تقریب زده می‌شود و دیگر این oracle تحلیلی در دسترس نیست. بخش عملی پروژه برای فهم یک حلقهٔ ریاضی است، نه بازتولید یک مولد متن‌به‌تصویر.

## ۲۳. نتیجهٔ ثبت‌شده و مرز آن

روی Python 3.13.16 و فقط کتابخانهٔ استاندارد، ۴۰/۴۰ آزمون unit پروژه موفق شد. fixture با SHA-256 برابر `7646ab0c0d8cee8fdbf3e29ac88ce9e37b181859e0ff34935f6af7bbe28b208b` audit شد. اجرای demo با `۲۰۰` گام، `۶۴` نقطه و seed برابر `۵۳` به شمار نزدیک‌ترین مرکزهای ساختگی `[۱۹، ۱۷، ۱۶، ۱۲]` رسید؛ `ᾱ_T = 0.002080618226191632` بود. این‌ها خلاصهٔ یک اجرای deterministic روی توزیع کوچکِ تعریف‌شده‌اند، نه metric کیفیت.

آزمون‌ها schedule، معکوس‌سازی جبری با noise معلوم، score تحلیلی، posterior variance، seed، schema و خروجی JSON را می‌سنجند. نه training شبکه، inference مدل واقعی، خواندن تصویر/ویدئو، latency/benchmark، تعمیم، کیفیت فارسی، حقوق، ایمنی، privacy یا سخت‌افزار اجرا نشده است. همهٔ نقاط صرفاً fixture مصنوعی‌اند. جزئیات و فرمان‌ها در [`53-audit-report-fa.md`](53-audit-report-fa.md) و `projects/53-diffusion-lab/results.json` ثبت شده‌اند.

## ۲۴. تمرین‌ها

۱. برای `β₁=0.1` و `x₀=2`، اگر `ε=0` باشد، `x₁` را از رابطهٔ بسته محاسبه کنید. سپس توضیح دهید چرا با `ε≠0` یک مشاهدهٔ منفرد دیگر به‌تنهایی x₀ را تعیین نمی‌کند.

۲. اگر `ᾱ_t=0.25` و `x₀=4` باشد، مقدار `x_t` را برای `ε=1` بیابید. در این مثال سهم سیگنال و noise هرکدام چه اندازه‌اند؟

۳. رابطهٔ تبدیل پیش‌بینی نویز به `x₀` را بنویسید و بگویید چرا وقتی `ᾱ_t` بسیار کوچک است، خطای کوچک در noise prediction می‌تواند مسئله‌ساز شود.

۴. در CFG اگر `ε_uncond=0.2`، `ε_cond=0.8` و `s=2` باشد، مقدار guided چیست؟ چرا نمی‌توان از این مقدار نتیجه گرفت که تصویر از نظر همهٔ معیارها بهتر خواهد شد؟

۵. سه مرحلهٔ latent diffusion را مشخص کنید. برای هر مرحله یک نوع خطا یا artifact که ممکن است در آن ایجاد شود، نام ببرید.

۶. در cross-attention تصویر–متن، `Q`, `K`, `V` معمولاً از کدام tokenها می‌آیند؟ اگر طول متن L و طول تصویر M باشد، ماتریس `QKᵀ` چه شکل دارد؟

۷. برای یک تصویر `1024×1024` با patch `16×16`، tokenهای مکانیِ ساده را بشمارید. اگر فریم‌ها ۲۴ تا باشند و همین شمارش برای هر فریم تکرار شود، دنبالهٔ خام تقریباً چند token می‌شود؟ بگویید چرا این محاسبه به‌تنهایی حافظهٔ واقعی مدل را پیش‌بینی نمی‌کند.

۸. دو سنجهٔ مناسب برای text-to-image و دو بُعد زمانی برای text-to-video پیشنهاد کنید. برای هرکدام یک شکست مهمی را توضیح دهید که آن سنجه نمی‌سنجد.

۹. با زبان خود توضیح دهید چرا manifest معتبر C2PA اثبات نمی‌کند که صحنهٔ داخل تصویر واقعی است؛ نبود manifest نیز چه معنایی را به‌تنهایی ثابت نمی‌کند؟

۱۰. برای ساخت یک نمونهٔ تصویری تبلیغاتی با چهرهٔ فرد واقعی، پیش از استفاده چه بررسی‌های حقوق، رضایت، ایمنی و افشا را انجام می‌دهید؟ پاسخ باید مرز میان توصیهٔ فنی و نظر حقوقی را حفظ کند.

پاسخ‌های تشریحی مستقل در [`answers/53-image-video-generation-fa.md`](book-engineering/answers/53-image-video-generation-fa.md) آمده‌اند.

## ۲۵. جمع‌بندی و مسیر فصل بعد

Diffusion با schedule نویز و reverse sampler تعریف می‌شود؛ prediction type، شرط‌دهی و solver را باید صریح ثبت کرد. Latentها و Transformerها محاسبه را با نمایش‌های فشرده یا tokenها سازمان می‌دهند، اما کیفیت به داده، decoder، معماری و شرایط اجرا وابسته است. ویدئو بعد زمانی و سنجش ثبات/ترتیب را اضافه می‌کند. ارزیابی، حقوق، رضایت، ایمنی و provenance پرسش‌های جداگانه‌اند و هیچ metric یا credential به‌تنهایی پاسخ همه را نمی‌دهد.

پروژهٔ CPU این فصل فقط یک توزیع دوبعدی ساختگی و score تحلیلی را می‌آزماید؛ آن را نمونهٔ مدل تصویر/ویدئو معرفی نکنید. فصل بعد، سراسری ۵۴، از همین مرز عبور می‌کند و برآورد وزن‌ها، فعال‌سازی‌ها، gradientها و حالت optimizer را برای workloadهای واقعی به‌صورت مرحله‌ای بررسی خواهد کرد.

## ۲۶. منابع و تاریخ بازبینی

**تاریخ بررسی لینک‌ها و وضعیت منابع: ۶ نوامبر ۲۰۲۶.** مقاله‌های arXiv با عنوان «preprint» گزارش/پیش‌چاپ‌اند؛ جدول‌های عملکرد و benchmark به setup نویسندگان همان منبع محدودند.

۱. Ho, J., Jain, A., و Abbeel, P. “Denoising Diffusion Probabilistic Models,” NeurIPS 2020, arXiv:2006.11239. <https://arxiv.org/abs/2006.11239>

۲. Song, J., Meng, C., و Ermon, S. “Denoising Diffusion Implicit Models,” ICLR 2021, arXiv:2010.02502. <https://arxiv.org/abs/2010.02502>

۳. Ho, J. و Salimans, T. “Classifier-Free Diffusion Guidance,” arXiv:2207.12598, 2022. <https://arxiv.org/abs/2207.12598>

۴. Rombach, R. و همکاران. “High-Resolution Image Synthesis with Latent Diffusion Models,” CVPR 2022, arXiv:2112.10752. <https://arxiv.org/abs/2112.10752>

۵. Peebles, W. و Xie, S. “Scalable Diffusion Models with Transformers,” ICCV 2023, arXiv:2212.09748. <https://arxiv.org/abs/2212.09748>

۶. Esser, P. و همکاران. “Scaling Rectified Flow Transformers for High-Resolution Image Synthesis,” arXiv:2403.03206, 2024. <https://arxiv.org/abs/2403.03206>

۷. OpenAI. “Video generation models as world simulators,” گزارش فنی دربارهٔ Sora، ۱۵ فوریهٔ ۲۰۲۴. <https://openai.com/index/video-generation-models-as-world-simulators/>

۸. Kong, W. و همکاران. “HunyuanVideo: A Systematic Framework For Large Video Generative Models,” arXiv:2412.03603, v6, ۲۰۲۵. <https://arxiv.org/abs/2412.03603>

۹. Team Wan و همکاران. “Wan: Open and Advanced Large-Scale Video Generative Models,” arXiv:2503.20314, v2, ۲۰۲۵؛ [مخزن رسمی Wan2.2](https://github.com/Wan-Video/Wan2.2), بازبینی‌شده در ۶ نوامبر ۲۰۲۶.

۱۰. Lipman, Y. و همکاران. “Flow Matching for Generative Modeling,” ICLR 2023, arXiv:2210.02747. <https://arxiv.org/abs/2210.02747>

۱۱. Liu, X., Gong, C. و Liu, Q. “Flow Straight and Fast: Learning to Generate and Transfer Data with Rectified Flow,” arXiv:2209.03003, 2022. <https://arxiv.org/abs/2209.03003>

۱۲. Huang, Z. و همکاران. “VBench++: Comprehensive and Versatile Benchmark Suite for Video Generative Models,” arXiv:2411.13503, 2024. <https://arxiv.org/abs/2411.13503>

۱۳. Zheng, D. و همکاران. “VBench-2.0: Advancing Video Generation Benchmark Suite for Intrinsic Faithfulness,” arXiv:2503.21755, v2, ۲۰۲۵. <https://arxiv.org/abs/2503.21755>

۱۴. U.S. Copyright Office. “Copyright and Artificial Intelligence, Part 2: Copyrightability,” اطلاعیهٔ انتشار، ۲۹ ژانویهٔ ۲۰۲۵. <https://www.copyright.gov/newsnet/2025/1060.html>

۱۵. U.S. Copyright Office. “Copyright and Artificial Intelligence, Part 3: Generative AI Training,” صفحهٔ رسمی و نسخهٔ pre-publication مورخ ۹ مهٔ ۲۰۲۵؛ وضعیت صفحه در تاریخ بازبینی همچنان pre-publication بود. <https://www.copyright.gov/ai/> و <https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-3-Generative-AI-Training-Report-Pre-Publication-Version.pdf>

۱۶. C2PA. “Content Credentials, Technical Specification 2.5.” <https://spec.c2pa.org/specifications/specifications/2.5/specs/ContentCredentials.html>

۱۷. Lim, J. و همکاران. “Motif-Video 2B: Technical Report,” arXiv:2604.16503, v2, ۲۰۲۶؛ preprint. <https://arxiv.org/abs/2604.16503>

۱۸. Khare, A. و همکاران. “Temporal Specification Guidance for Text-to-Video Generation,” arXiv:2610.20822, ۲۰۲۶؛ preprint. <https://arxiv.org/abs/2610.20822>

۱۹. Zhang, X. و همکاران. “Mage-Flow: An Efficient Native-Resolution Foundation Model for Image Generation and Editing,” arXiv:2607.19064, v2, ۲۰۲۶؛ preprint. <https://arxiv.org/abs/2607.19064>

## ۲۷. پیوست اجرایی: فایل آزموده‌شدهٔ پروژه

این پیوست باید با `projects/53-diffusion-lab/diffusion_lab.py` بایت‌به‌بایت یکسان بماند. برنامه مستقل و فقط با Python standard library است.

```python
"""A tiny DDPM sampler using the exact score of a synthetic 2-D mixture.

This is an analytic teaching fixture, not a trained neural image/video model.
It uses only Python's standard library and writes a JSON audit/demo record.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


DEFAULT_FIXTURE = Path(__file__).with_name("sample_mixture.json")
BETA_START = 0.0005
BETA_END = 0.06
DEFAULT_STEPS = 200
DEFAULT_SAMPLES = 64
DEFAULT_SEED = 53


@dataclass(frozen=True)
class DiffusionSchedule:
    betas: tuple[float, ...]
    alphas: tuple[float, ...]
    alpha_bars: tuple[float, ...]


def _time_index(t: int, steps: int) -> int:
    if isinstance(t, bool) or not isinstance(t, int) or not 0 <= t < steps:
        raise ValueError(f"t must be an integer in [0, {steps - 1}]")
    return t


def _finite_vector(values: Sequence[float], name: str) -> tuple[float, ...]:
    if isinstance(values, (str, bytes)):
        raise ValueError(f"{name} must be a numeric sequence")
    try:
        result = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a numeric sequence") from exc
    if not result or not all(math.isfinite(value) for value in result):
        raise ValueError(f"{name} must contain finite values")
    return result


def validate_fixture(fixture: Any) -> None:
    """Validate the deliberately narrow, synthetic 2-D fixture schema."""
    if not isinstance(fixture, dict):
        raise ValueError("fixture must be a JSON object")
    if fixture.get("schema_version") != 1:
        raise ValueError("unsupported fixture schema_version")
    if fixture.get("label_source") != "synthetic_fixture":
        raise ValueError("fixture label_source must be synthetic_fixture")
    if fixture.get("dimension") != 2:
        raise ValueError("this teaching sampler accepts only dimension=2")

    variance = fixture.get("component_variance")
    if isinstance(variance, bool) or not isinstance(variance, (int, float)):
        raise ValueError("component_variance must be numeric")
    if not math.isfinite(float(variance)) or float(variance) <= 0:
        raise ValueError("component_variance must be finite and positive")

    components = fixture.get("components")
    if not isinstance(components, list) or len(components) < 2:
        raise ValueError("fixture must contain at least two components")
    identifiers: list[str] = []
    weights: list[float] = []
    for component in components:
        if not isinstance(component, dict):
            raise ValueError("each component must be an object")
        identifier = component.get("id")
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("each component needs a non-empty id")
        if identifier in identifiers:
            raise ValueError("component ids must be unique")
        identifiers.append(identifier)
        mean = _finite_vector(component.get("mean", ()), "component mean")
        if len(mean) != 2:
            raise ValueError("each component mean must have two coordinates")
        weight = component.get("weight")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise ValueError("component weight must be numeric")
        weight = float(weight)
        if not math.isfinite(weight) or weight < 0:
            raise ValueError("component weights must be finite and non-negative")
        weights.append(weight)
    if not math.isclose(sum(weights), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("component weights must sum to 1")
    if not any(weight > 0 for weight in weights):
        raise ValueError("at least one component weight must be positive")

    metadata = fixture.get("metadata")
    required_false = (
        "image_files_included",
        "video_files_included",
        "real_world_observations_included",
        "trained_weights_included",
    )
    if not isinstance(metadata, dict):
        raise ValueError("fixture metadata is required")
    if any(metadata.get(field) is not False for field in required_false):
        raise ValueError("fixture must explicitly exclude images, videos, observations, and trained weights")


def load_fixture(path: str | Path) -> tuple[dict[str, Any], str]:
    fixture_path = Path(path)
    raw = fixture_path.read_bytes()
    try:
        fixture = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"fixture is not valid UTF-8 JSON: {fixture_path.name}") from exc
    validate_fixture(fixture)
    return fixture, hashlib.sha256(raw).hexdigest()


def linear_beta_schedule(
    steps: int = DEFAULT_STEPS,
    beta_start: float = BETA_START,
    beta_end: float = BETA_END,
) -> DiffusionSchedule:
    """Create a linear beta schedule and its alpha / cumulative-alpha values."""
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 2:
        raise ValueError("steps must be an integer of at least 2")
    if not math.isfinite(beta_start) or not math.isfinite(beta_end):
        raise ValueError("beta endpoints must be finite")
    if not 0 < beta_start <= beta_end < 1:
        raise ValueError("beta endpoints must satisfy 0 < start <= end < 1")
    betas = tuple(
        beta_start + (beta_end - beta_start) * index / (steps - 1)
        for index in range(steps)
    )
    alphas = tuple(1.0 - beta for beta in betas)
    cumulative = 1.0
    alpha_bars: list[float] = []
    for alpha in alphas:
        cumulative *= alpha
        alpha_bars.append(cumulative)
    return DiffusionSchedule(betas, alphas, tuple(alpha_bars))


def q_sample(
    x0: Sequence[float],
    noise: Sequence[float],
    t: int,
    schedule: DiffusionSchedule,
) -> tuple[float, ...]:
    """Draw x_t from the closed-form forward marginal, given explicit noise."""
    t = _time_index(t, len(schedule.betas))
    clean = _finite_vector(x0, "x0")
    epsilon = _finite_vector(noise, "noise")
    if len(clean) != len(epsilon):
        raise ValueError("x0 and noise must have the same dimension")
    alpha_bar = schedule.alpha_bars[t]
    signal_scale = math.sqrt(alpha_bar)
    noise_scale = math.sqrt(1.0 - alpha_bar)
    return tuple(signal_scale * value + noise_scale * eps for value, eps in zip(clean, epsilon))


def predict_x0_from_epsilon(
    x_t: Sequence[float],
    epsilon_prediction: Sequence[float],
    t: int,
    schedule: DiffusionSchedule,
) -> tuple[float, ...]:
    """Invert the forward marginal when the noise value is known exactly."""
    t = _time_index(t, len(schedule.betas))
    noisy = _finite_vector(x_t, "x_t")
    epsilon = _finite_vector(epsilon_prediction, "epsilon_prediction")
    if len(noisy) != len(epsilon):
        raise ValueError("x_t and epsilon_prediction must have the same dimension")
    alpha_bar = schedule.alpha_bars[t]
    return tuple(
        (value - math.sqrt(1.0 - alpha_bar) * eps) / math.sqrt(alpha_bar)
        for value, eps in zip(noisy, epsilon)
    )


def ddpm_posterior_variance(t: int, schedule: DiffusionSchedule) -> float:
    """Return beta-tilde for q(x_(t-1) | x_t, x_0); it is zero at t=0."""
    t = _time_index(t, len(schedule.betas))
    previous_alpha_bar = 1.0 if t == 0 else schedule.alpha_bars[t - 1]
    current_alpha_bar = schedule.alpha_bars[t]
    denominator = 1.0 - current_alpha_bar
    variance = schedule.betas[t] * (1.0 - previous_alpha_bar) / denominator
    return max(0.0, variance)


def gaussian_mixture_score(
    x_t: Sequence[float],
    t: int,
    fixture: dict[str, Any],
    schedule: DiffusionSchedule,
) -> tuple[float, float]:
    """Compute the exact score of the noised fixture mixture, not a learned score."""
    validate_fixture(fixture)
    t = _time_index(t, len(schedule.betas))
    point = _finite_vector(x_t, "x_t")
    if len(point) != 2:
        raise ValueError("the fixture score is defined for two-dimensional points")

    alpha_bar = schedule.alpha_bars[t]
    mean_scale = math.sqrt(alpha_bar)
    variance_t = alpha_bar * float(fixture["component_variance"]) + (1.0 - alpha_bar)
    log_constant = -0.5 * 2 * math.log(2.0 * math.pi * variance_t)

    log_probabilities: list[float] = []
    scaled_means: list[tuple[float, float]] = []
    for component in fixture["components"]:
        mean = tuple(mean_scale * value for value in component["mean"])
        scaled_means.append((mean[0], mean[1]))
        weight = float(component["weight"])
        if weight == 0:
            log_probabilities.append(-math.inf)
            continue
        squared_distance = sum((value - center) ** 2 for value, center in zip(point, mean))
        log_probabilities.append(
            math.log(weight) + log_constant - squared_distance / (2.0 * variance_t)
        )

    maximum = max(log_probabilities)
    unnormalized = [math.exp(value - maximum) for value in log_probabilities]
    normalizer = sum(unnormalized)
    posterior_weights = [value / normalizer for value in unnormalized]
    score = tuple(
        sum(
            posterior_weight * (component_mean[axis] - point[axis]) / variance_t
            for posterior_weight, component_mean in zip(posterior_weights, scaled_means)
        )
        for axis in range(2)
    )
    return score[0], score[1]


def epsilon_from_score(
    score: Sequence[float],
    t: int,
    schedule: DiffusionSchedule,
) -> tuple[float, ...]:
    """Use score(x_t) = -E[epsilon | x_t] / sqrt(1-alpha_bar_t)."""
    t = _time_index(t, len(schedule.betas))
    gradient = _finite_vector(score, "score")
    scale = -math.sqrt(1.0 - schedule.alpha_bars[t])
    return tuple(scale * value for value in gradient)


def ddpm_reverse_step(
    x_t: Sequence[float],
    epsilon_prediction: Sequence[float],
    t: int,
    schedule: DiffusionSchedule,
    noise: Sequence[float] | None = None,
) -> tuple[float, ...]:
    """Apply one epsilon-parameterized DDPM reverse step."""
    t = _time_index(t, len(schedule.betas))
    noisy = _finite_vector(x_t, "x_t")
    epsilon = _finite_vector(epsilon_prediction, "epsilon_prediction")
    if len(noisy) != len(epsilon):
        raise ValueError("x_t and epsilon_prediction must have the same dimension")
    alpha_bar = schedule.alpha_bars[t]
    beta = schedule.betas[t]
    alpha = schedule.alphas[t]
    mean = tuple(
        (value - beta * eps / math.sqrt(1.0 - alpha_bar)) / math.sqrt(alpha)
        for value, eps in zip(noisy, epsilon)
    )
    variance = ddpm_posterior_variance(t, schedule)
    if t == 0:
        if noise is not None:
            raise ValueError("the final t=0 reverse step has zero posterior variance")
        return mean
    if noise is None:
        raise ValueError("noise is required when t > 0")
    random_noise = _finite_vector(noise, "noise")
    if len(random_noise) != len(mean):
        raise ValueError("reverse-step noise must match the point dimension")
    noise_scale = math.sqrt(variance)
    return tuple(value + noise_scale * eps for value, eps in zip(mean, random_noise))


def sample_mixture(
    fixture: dict[str, Any],
    schedule: DiffusionSchedule,
    count: int = DEFAULT_SAMPLES,
    seed: int = DEFAULT_SEED,
) -> tuple[tuple[float, float], ...]:
    """Sample from the toy mixture with an analytic-score DDPM reverse chain."""
    validate_fixture(fixture)
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise ValueError("count must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    rng = random.Random(seed)
    points: list[tuple[float, float]] = [
        (rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0)) for _ in range(count)
    ]
    for t in reversed(range(len(schedule.betas))):
        updated: list[tuple[float, float]] = []
        for point in points:
            score = gaussian_mixture_score(point, t, fixture, schedule)
            epsilon = epsilon_from_score(score, t, schedule)
            step_noise = None if t == 0 else (rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0))
            result = ddpm_reverse_step(point, epsilon, t, schedule, step_noise)
            updated.append((result[0], result[1]))
        points = updated
    return tuple(points)


def nearest_component_counts(
    samples: Sequence[Sequence[float]],
    fixture: dict[str, Any],
) -> dict[str, int]:
    """Count nearest synthetic centers; this is a demo summary, not an evaluator."""
    validate_fixture(fixture)
    counts = {component["id"]: 0 for component in fixture["components"]}
    for sample in samples:
        point = _finite_vector(sample, "sample")
        if len(point) != 2:
            raise ValueError("samples must be two-dimensional")
        nearest = min(
            fixture["components"],
            key=lambda component: sum(
                (point[axis] - float(component["mean"][axis])) ** 2 for axis in range(2)
            ),
        )
        counts[nearest["id"]] += 1
    return counts


def _fixture_record(fixture: dict[str, Any], fixture_hash: str, path: Path) -> dict[str, Any]:
    return {
        "path": path.name,
        "sha256": fixture_hash,
        "fixture_id": fixture["fixture_id"],
        "label_source": fixture["label_source"],
        "dimension": fixture["dimension"],
        "components": len(fixture["components"]),
        "image_files_included": fixture["metadata"]["image_files_included"],
        "video_files_included": fixture["metadata"]["video_files_included"],
        "real_world_observations_included": fixture["metadata"]["real_world_observations_included"],
        "trained_weights_included": fixture["metadata"]["trained_weights_included"],
    }


def run_audit(fixture: dict[str, Any], fixture_hash: str, fixture_path: Path) -> dict[str, Any]:
    return {
        "status": "synthetic_diffusion_fixture_audit_complete",
        "mode": "audit",
        "training_performed": False,
        "neural_model_loaded": False,
        "model_downloaded": False,
        "image_files_loaded": False,
        "video_files_loaded": False,
        "device": "CPU; Python standard library only",
        "fixture": _fixture_record(fixture, fixture_hash, fixture_path),
        "claims_not_supported": [
            "quality of a trained image or video model",
            "Persian-language output quality",
            "hardware performance or benchmark results",
            "copyright clearance, privacy compliance, or legal conclusions",
        ],
    }


def run_demo(
    fixture: dict[str, Any],
    fixture_hash: str,
    fixture_path: Path,
    steps: int = DEFAULT_STEPS,
    sample_count: int = DEFAULT_SAMPLES,
    seed: int = DEFAULT_SEED,
    beta_start: float = BETA_START,
    beta_end: float = BETA_END,
) -> dict[str, Any]:
    schedule = linear_beta_schedule(steps, beta_start, beta_end)
    samples = sample_mixture(fixture, schedule, sample_count, seed)
    means = [sum(sample[axis] for sample in samples) / len(samples) for axis in range(2)]
    return {
        "status": "analytic_synthetic_mixture_ddpm_demo_complete",
        "mode": "demo",
        "training_performed": False,
        "neural_model_loaded": False,
        "model_downloaded": False,
        "image_files_loaded": False,
        "video_files_loaded": False,
        "analytic_score_used": True,
        "score_source": "closed_form_density_of_known_synthetic_gaussian_mixture",
        "device": "CPU; Python standard library only",
        "fixture": _fixture_record(fixture, fixture_hash, fixture_path),
        "sampling": {
            "method": "epsilon-parameterized DDPM reverse updates",
            "initial_prior": "standard-normal approximation at the terminal timestep",
            "timesteps": steps,
            "beta_start": beta_start,
            "beta_end": beta_end,
            "terminal_alpha_bar": schedule.alpha_bars[-1],
            "sample_count": sample_count,
            "seed": seed,
            "posterior_noise_added_at_t0": False,
        },
        "nearest_synthetic_center_counts": nearest_component_counts(samples, fixture),
        "sample_mean": means,
        "samples": [list(sample) for sample in samples],
        "interpretation_limit": "Toy 2-D distribution only; not image/video generation or model evaluation.",
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit a synthetic diffusion fixture or run its analytic toy sampler")
    parser.add_argument("--mode", choices=("audit", "demo"), required=True)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, required=True, help="directory for run.json")
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--beta-start", type=float, default=BETA_START)
    parser.add_argument("--beta-end", type=float, default=BETA_END)
    args = parser.parse_args(argv)

    fixture, fixture_hash = load_fixture(args.fixture)
    if args.mode == "audit":
        result = run_audit(fixture, fixture_hash, args.fixture)
    else:
        result = run_demo(
            fixture,
            fixture_hash,
            args.fixture,
            steps=args.steps,
            sample_count=args.samples,
            seed=args.seed,
            beta_start=args.beta_start,
            beta_end=args.beta_end,
        )
    result["python"] = ".".join(map(str, sys.version_info[:3]))
    output_file = args.output / "run.json"
    _write_json(output_file, result)
    print(json.dumps({"status": result["status"], "output": str(output_file), "fixture_sha256": fixture_hash}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
