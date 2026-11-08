# جلد پنجم، فصل ۷ — امنیت عملیاتی، پایش و حریم خصوصی محصول هوش مصنوعی

**نگاشت:** فصل محلی ۷ جلد پنجم = فصل سراسری ۶۸. **تاریخ بازبینی منابع: ۴ نوامبر ۲۰۲۶.** فصل ۶۵ دربارهٔ حکمرانی، مالکیت ریسک و شواهد سازمانی است؛ فصل ۶۶ قرارداد API و رابط محصول را می‌سازد؛ فصل ۶۷ صف، cache، زمان پاسخ و ظرفیت سرویس را تحلیل می‌کند. این فصل کنترل هویت، مجوز، محدودیت درخواست، ثبت رخداد، پایش و پاسخ به رخداد را در مرز محصول دنبال می‌کند. طراحی استقرار، CI/CD، نسخه‌بندی محیط و بازگشت نسخه برای فصل ۶۹ است؛ ارزیابی مدل و Red Teaming در فصل‌های ۶۲ تا ۶۴ می‌مانند. پروژهٔ همراه فقط یک سیاست‌سنج قطعی روی fixture ساختگی است؛ نه سامانهٔ احراز هویت یا امنیت تولیدی.

**پیش‌نیاز:** قرارداد فصل ۶۶، تمایز صف محصول از محدودیت نرخ در فصل ۶۷، و آشنایی مقدماتی با HTTP و آزمون نرم‌افزار. **خروجی:** بتوانید مرز احراز هویت و مجوز را طراحی کنید، محدودیت درخواست را با هویت و هزینهٔ کار هماهنگ کنید، رخداد امنیتی را بدون ثبت محتوای حساس پایش کنید، و یک playbook را با نقش و شواهدِ روشن تمرین کنید.

![شکل ۵-۷-۱ — مسیر از کاربر یا سرویس به درگاه ورودی می‌رسد؛ هویت معتبر از credential بررسی‌شده به دست می‌آید، سپس محدودیت نرخ و مجوز tenant/object اعمال می‌شود و فقط نتیجهٔ کمینه به رویداد ممیزی می‌رود. مسیر مشاهده‌پذیری از شمارنده‌های کم‌جزئیات، log ساخت‌یافتهٔ پالایش‌شده و trace هم‌بسته تشکیل می‌شود؛ alert به triage و playbook رخداد می‌رسد. مسیر دادهٔ prompt و credential وارد log ممیزی نمی‌شود. برچسب‌ها و پیکان‌ها رابطه را نشان می‌دهند، نه رنگ؛ نمودار مفهومی است و پیاده‌سازی یا ایمنی یک محصول واقعی را ثابت نمی‌کند.](../diagrams/v5-ch07-product-security-flow.svg)

**شکل ۵-۷-۱ —** مرز هویت، مجوز، سهمیه و پایشِ حریم‌خصوصی‌محور در یک محصول AI؛ محتوای prompt و credential از مسیر log امنیتی خارج می‌ماند.

## ۱. جایگاه فصل و مرز موضوعی

فصل ۶۶ می‌پرسید کلاینت و backend بر سر چه request و responseای توافق می‌کنند. فصل ۶۷ می‌پرسید درخواست معتبر چه‌طور در صف و worker سرو می‌شود. فصل حاضر می‌پرسد «چه کسی یا چه سرویسی این درخواست را فرستاده، به کدام داده و عمل مجاز است، چه مقدار از منابع می‌تواند مصرف کند، چه رخدادی را ثبت می‌کنیم و اگر کنترل شکست خورد چه کسی چه می‌کند؟»

احراز هویت یعنی سنجیدن ادعای هویت؛ مجوز یعنی تصمیم‌گیری دربارهٔ عمل مشخص روی منبع مشخص؛ محدودیت نرخ، بودجه و concurrency مصرف را کنترل می‌کنند؛ پایش سیگنال می‌دهد که رفتار سامانه از انتظار خارج شده است. هیچ‌کدام جای ارزیابی کیفیت یا حملهٔ مجاز فصل‌های ۶۲ تا ۶۴ را نمی‌گیرد. فصل ۶۵ سیاست و پاسخ‌گویی کلان را طرح می‌کند؛ اینجا آن سیاست به کنترل‌های اجرایی و شواهد عملیاتی ترجمه می‌شود. فصل ۶۹ انتشار نسخه و زیرساخت را ادامه می‌دهد.

## ۲. مرز اعتماد را پیش از انتخاب ابزار رسم کنید

در یک برنامهٔ مکالمه‌محور، داده از مرورگر یا موبایل، درگاه API، سرویس برنامه، ارائه‌دهندهٔ هویت، صف یا runtime، پایگاه داده، vector store و گاهی provider بیرونی عبور می‌کند. هر مرز می‌تواند هویت، داده یا خطای متفاوتی داشته باشد. مرورگرِ خود کاربر محیط قابل‌اعتماد backend نیست؛ فیلد `tenant_id`، نام نقش یا `is_admin` در JSON ورودی به‌تنهایی مدرک هویت و مجوز نیست.

نقشهٔ جریان داده باید برای هر مرحله نشان دهد چه داده‌ای وارد می‌شود، چه تصمیمی گرفته می‌شود، کجا ذخیره یا ارسال می‌شود، چه نقش‌هایی به آن دسترسی دارند و چه زمانی حذف می‌شود. اگر یک component متن prompt را برای debug می‌گیرد، همان log sink یک مخزن دادهٔ حساس شده است. مرز را با نمودار ساده شروع کنید، اما پیکان‌ها و برچسب‌ها را با configuration واقعی و providerهای قراردادشده تطبیق دهید.

## ۳. سه پرسش مستقل: هویت، اختیار و سهمیه

برای هر درخواست جداگانه پاسخ دهید: **هویت** از کدام credential تأییدشده به دست آمده است؟ **اختیار** برای این action و این object با چه policy سنجیده شده است؟ **سهمیه** بر اساس کدام principal، tenant، route یا مصرف محاسباتی اعمال می‌شود؟ موفقیت در یکی، دو مورد دیگر را ثابت نمی‌کند.

در محصول چندمستأجری ممکن است یک bearer token از نظر رمزنگاری معتبر باشد، اما برای API مخاطب دیگری صادر شده باشد؛ یا برای خواندن یک پرونده مجوز داشته باشد، اما برای export همهٔ tenantها نه. همچنین کاربری که احراز هویت شده، می‌تواند از نظر quota عبور کند. هر کنترل را در نقطهٔ مناسب، با failure mode و لاگ امن خودش آزمون کنید؛ پاسخ ۲۰۰، ثبت یک log یا وجود یک limiter به‌تنهایی شواهدِ پایان کار نیست.

## ۴. احراز هویت با مجوز یکی نیست

احراز هویت (authentication) بررسی می‌کند credential به کدام principal وابسته است و آیا هنوز معتبر است. مجوز (authorization) می‌سنجد آن principal، با نقش و context موجود، اجازهٔ انجام همین عملیات را روی همین منبع دارد یا نه. برای نمونه، پاسخ API می‌تواند در نبود یا نامعتبر بودن credential با `401` و challenge مناسب رد شود؛ `403` یعنی سرور درخواست را فهمیده اما دسترسی را مجاز نمی‌داند [۴]. جزئیات خطا نباید وجود حساب، tenant یا منبع محرمانه را به مهاجم آشکار کند.

برای API فقط پذیرشِ token به معنی مجوز نیست. هر route و object باید policy خود را اجرا کند؛ بررسی در frontend یا مخفی‌کردن دکمهٔ admin کنترل سمت سرور را جایگزین نمی‌کند. در فصل ۶۶ semantics پاسخ و schema بررسی شد؛ این فصل دربارهٔ تصمیم واقعیِ مجوز و حفاظت از منابع است.

## ۵. هویت دیجیتال را به provider آزموده‌شده بسپارید

اگر محصول login یا federation دارد، معمولاً از identity provider و کتابخانهٔ شناخته‌شدهٔ پروتکل استفاده می‌کنید، نه این‌که رمزنگاری، OAuth یا مدیریت گذرواژه را از صفر بنویسید. OAuth چارچوب واگذاری دسترسی است؛ OpenID Connect لایهٔ هویت را روی آن می‌افزاید. OAuth 2.0 Security BCP در RFC 9700 روش‌های ناامن یا قدیمی را محدود می‌کند و راهنمایی‌هایی مانند اتصال امن authorization code، کنترل redirect URI و حفاظت از token را به‌روز می‌کند [۱]. پیکربندی واقعی باید با نوع client، provider، threat model و مقررات سازمان شما تطبیق داشته باشد.

NIST SP 800-63-4 راهنمای هویت دیجیتال برای سامانه‌هایی است که در دامنهٔ کاربرد آن قرار می‌گیرند؛ سطح assurance را بر اساس ریسک و کاربرد انتخاب می‌کند و همهٔ وب‌اپ‌ها را خودکار ملزم به یک روش واحد نمی‌سازد [۲]. یک نمونهٔ آموزشی یا چک‌لیست عمومی نیز جای آزمون integration، بررسی تغییر provider و بازبینی امنیتی را نمی‌گیرد.

## ۶. Token را نه decode ساده، نه رازِ بی‌خطر فرض کنید

در API مبتنی بر bearer token، هر کسی که token را به‌دست آورد ممکن است بتواند آن را تا زمان انقضا یا ابطال replay کند. Resource server باید امضا یا سازوکار اعتبارسنجی تعریف‌شده را با الگوریتم مجاز بررسی کند، issuer و audience را تطبیق دهد، زمان‌های `exp` و `nbf` را در صورت وجود درست تفسیر کند، scope یا claim لازم را بررسی کند و خطا را به تصمیم مجوز پیوند دهد. صرفاً base64-decode کردن JWT، اعتبارسنجی نیست.

کلیدهای signing و API secrets باید در محل مدیریت راز با دسترسی محدود نگهداری شوند، نه در source، URL، screenshot، ticket یا log. برای clientهای public، secret پنهان‌پذیر فرض نشود؛ برای server-to-server، هر credential scope و مقصد محدود، عمر مشخص، چرخش و مسیر ابطال داشته باشد. بازیابی یا rotation را دوره‌ای تمرین کنید؛ صرف انقضا تضمین نمی‌کند token دزدیده‌شده پیش از آن بی‌خطر باشد.

## ۷. هویت workload را از هویت کاربر جدا نگه دارید

یک agent یا backend ممکن است با هویت سرویس به provider مدل، vector store یا API داخلی وصل شود. این workload identity با هویت انسانی که درخواست را آغاز کرده یکی نیست. در audit trail، زنجیره را به‌صورت «principal انسانی → سرویسِ اقدام‌کننده → resource» با شناسه‌های حداقلی نشان دهید؛ token کاربر را در همهٔ سرویس‌ها کپی نکنید مگر معماری delegation و مرز اعتماد آن صریحاً طراحی و آزموده شده باشد.

برای هر سرویس credential جدا، حداقل دسترسی و امکان revoke مستقل داشته باشید. از key ثابتِ مشترک در همهٔ محیط‌ها دوری کنید؛ اگر یک کلید مشترک لو رفت، تشخیص این‌که کدام سرویس یا محیط از آن استفاده کرده دشوار می‌شود. جزئیات تزریق secret به pipeline و deployment به فصل ۶۹ واگذار می‌شود؛ اینجا فقط قرارداد هویت و اختیار سرویس را مشخص می‌کنیم.

## ۸. اصل حداقل دسترسی و رد پیش‌فرض

Policy باید برای هر action صریح باشد: چه role، scope یا attributeای لازم است؟ حالت پیش‌فرض، deny است؛ نبود policy یا خطای بارگذاری آن نباید ناخواسته دسترسی بدهد. role-based control برای نقش‌های پایدار ساده است؛ attribute-based policy می‌تواند contextهایی مانند tenant، نوع داده، هدف پردازش یا وضعیت درخواست را هم بسنجد. این ابزارها خودبه‌خود درست نیستند؛ policy را کوچک، قابل‌فهم، نسخه‌مند و قابل‌آزمون نگه دارید.

اصل حداقل دسترسی را برای کاربر، اپراتور، service account، پشتیبانی و سامانهٔ log جدا اعمال کنید. اگر یک role برای export لازم نیست، داشتن دسترسی به API نباید export را هم مجاز کند. تغییر role یا grant پرقدرت باید رخداد امنیتی قابل‌ممیزی باشد و مسیر اضطراری آن مالک، مدت و بازبینی داشته باشد.

## ۹. مجوز object، field و function را جدا بسنجید

در یک API می‌توان برای یک record مجوز داشت، اما بعضی propertyهای آن را ندید یا تغییر نداد؛ همچنین مجوز خواندن الزاماً مجوز export، delete یا تغییر تنظیمات نیست. OWASP API Security Top 10:2023 به Broken Object Level Authorization، Broken Object Property Level Authorization و Broken Function Level Authorization به‌عنوان دسته‌های جدا اشاره می‌کند [۳]. هر بار که شناسهٔ object از request می‌آید، کنترل دسترسی به خود object را در backend انجام دهید.

در tenant isolation، tenant مؤثر را از context هویتی معتبر به‌دست آورید، نه از `tenant_id` ارسالی کاربر. اگر resource واقعاً متعلق به tenant دیگری است، باید پیش از خواندن یا تغییر داده رد شود. آزمون منفی را با دو tenant ساختگی بسازید: کاربر A با تغییر شناسه، به resource B دسترسی نگیرد؛ response نیز نباید دادهٔ B را در error، cache، log یا trace نشت دهد.

## ۱۰. Policy باید به request context متصل باشد

یک تصمیم مجوز فقط «role=admin» نیست. آن را با principal، action، object، tenant، scope، purpose، state و نسخهٔ policy بسنجید. احراز هویت موفق می‌تواند context را در یک شیء داخلیِ تغییرناپذیر بسازد؛ routeهای پایین‌دستی همان context را دریافت می‌کنند و دوباره از body یا header نامطمئن principal نمی‌سازند.

برای هر تصمیم، outcome و reason code پایدار داشته باشید؛ متن خام policy، token یا attribute محرمانه را به کلاینت بازنگردانید. `decision_id` یا `request_id` تولیدشده در server می‌تواند مسیر میان API، policy engine و audit event را هم‌بسته کند. مقدار هم‌بستگی نباید token، email یا prompt را در خود کد کند.

## ۱۱. ردِ مجوز و ردِ سهمیه را از هم جدا کنید

`403` به‌تنهایی علت فنی یا policy را برای کلاینت روشن نمی‌کند؛ پیام عمومی بدهید و reason code داخلیِ کم‌جزئیات ثبت کنید. `429` برای محدودیت نرخ یا سهمیهٔ یک client/tenant است، نه برای هر overload عمومیِ backend. `503` می‌تواند وضعیت موقتیِ خود سرویس را نشان دهد [۴]؛ قرارداد پاسخ و retry باید با فصل ۶۶ و رفتار صف در فصل ۶۷ هماهنگ باشد.

همهٔ ردها یکسان نیستند: credential نامعتبر، تجاوز از quota، object خارج از tenant و سرویس ناتوان از پاسخ، تصمیم‌های متفاوت‌اند و پاسخ کلاینت و alert متفاوتی می‌خواهند. اگر همه را به ۵۰۰ تبدیل کنید، می‌توانید عیب را مبهم کنید؛ اگر جزئیات بیش‌ازحد برگردانید، امکان enumeration یا افشای سیاست می‌سازید.

## ۱۲. محدودیت نرخ با صف و ظرفیت یکی نیست

Rate limit سهم مصرف یک principal، tenant، endpoint یا بازهٔ زمانی را محدود می‌کند؛ quota می‌تواند سقف دوره‌ای مانند روزانه یا ماهانه باشد؛ concurrency cap تعداد عملیات هم‌زمان را مهار می‌کند؛ backpressure و صف فصل ۶۷ بار ورودی را با ظرفیت جاری هماهنگ می‌کنند. یک محصول ممکن است هر چهار مورد را لازم داشته باشد.

Limiter به‌تنهایی جلوی درخواست گران یا ورودی بسیار بزرگ را نمی‌گیرد، مگر اندازه و هزینه را هم لحاظ کند. برعکس، صف محدود لزوماً مانع یک client نمی‌شود که سهم دیگران را مصرف کند. OWASP API4:2023 دربارهٔ مصرف بی‌مهار منابع به bandwidth، CPU، حافظه، storage و هزینهٔ provider اشاره می‌کند [۳]. کنترل را بر اساس دارایی و الگوی سوءاستفاده انتخاب کنید، نه فقط یک عدد درخواست بر ثانیه.

## ۱۳. واحد شمارش را با هزینهٔ واقعی مرتبط کنید

محدودیت می‌تواند بر تعداد درخواست، اندازهٔ body، تعداد token ورودی/خروجی، تعداد فایل، طول context، عملیات جست‌وجو، زمان پردازش، هزینهٔ provider یا ترکیبی از آن‌ها اعمال شود. دو درخواست HTTP ممکن است هزینهٔ بسیار متفاوت داشته باشند؛ یک prompt کوتاه و یک درخواست با context بلند نباید لزوماً یک بودجهٔ یکسان بسوزانند.

هزینه را بر اساس تخمین server-side و policy نسخه‌مند حساب کنید، نه عددی که client خودش برای سهمیه می‌فرستد. سقف تعداد token و حجم ورودی را پیش از فراخوانی provider بررسی کنید و output را نیز محدود کنید. برای مدل‌های مختلف قیمت/سهمیه ممکن است متفاوت باشد؛ در این فصل قیمت ثابت نمی‌دهیم، چون قرارداد provider و بازار تغییر می‌کند. فصل ۵۶ برای قیمت و بودجهٔ محاسبات تاریخ و بازار مشخص می‌خواهد.

## ۱۴. الگوریتم را با نیاز burst و انصاف هماهنگ کنید

Fixed window پیاده‌سازی ساده‌ای دارد، اما در مرز دو پنجره می‌تواند burst نزدیک به دو برابر سقف ایجاد کند. Sliding window شمارش را نرم‌تر می‌کند ولی ممکن است state بیشتری بخواهد. Token bucket ظرفیت burst را با refill پایدار ترکیب می‌کند؛ leaky bucket یا صف زمان‌بندی‌شده خروجی را هموار می‌کند، اما می‌تواند انتظار بسازد. انتخاب به هدف latency، fairness، محل state و هزینهٔ پیاده‌سازی وابسته است.

در token bucket با ظرفیت `C` و نرخ بازپرکردن `r`، مقدار اعتبار در زمان `t` از مقدار پیشین بالا می‌رود تا از `C` فراتر نرود. درخواست با هزینهٔ `c` فقط وقتی پذیرفته می‌شود که اعتبار دست‌کم `c` باشد؛ سپس `c` واحد کم می‌شود. این رابطه مدل آموزشی است؛ threshold تولیدی را بدون بارنمایی، threat model و اندازه‌گیری انتخاب نکنید.

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="اعتبار سطل در زمان t برابر کمینهٔ ظرفیت C و اعتبار قبلی به‌علاوهٔ نرخ بازپرکردن r ضربدر زمان سپری‌شده است؛ درخواست فقط وقتی پذیرفته می‌شود که اعتبار از هزینهٔ server-side آن کمتر نباشد."><mtable><mtr><mtd><mrow><mi>T</mi><mo>(</mo><mi>t</mi><mo>)</mo><mo>=</mo><mo>min</mo><mo>(</mo><mi>C</mi><mo>,</mo><mi>T</mi><mo>(</mo><msub><mi>t</mi><mi>0</mi></msub><mo>)</mo><mo>+</mo><mi>r</mi><mo>(</mo><mi>t</mi><mo>−</mo><msub><mi>t</mi><mi>0</mi></msub><mo>)</mo><mo>)</mo></mrow></mtd></mtr><mtr><mtd><mrow><mi>accept</mi><mo>⇔</mo><mi>T</mi><mo>(</mo><mi>t</mi><mo>)</mo><mo>≥</mo><mi>c</mi></mrow></mtd></mtr></mtable></math>

**متن جایگزین فرمول:** اعتبار به‌اندازهٔ نرخ `r` در زمان سپری‌شده بازمی‌گردد اما سقف آن ظرفیت `C` است؛ درخواست با هزینهٔ server-side `c` فقط در صورت داشتن اعتبار کافی پذیرفته می‌شود. این فرمول به‌تنهایی تنظیم مناسب یا تضمین انصاف را ثابت نمی‌کند.

## ۱۵. محل و کلید limiter مهم‌اند

اگر هر worker limiter مستقل و memory-local داشته باشد، کاربری که بین چند replica جابه‌جا می‌شود ممکن است از مجموع سهمیهٔ چند worker استفاده کند. state مشترک یا تقسیم دقیق سهمیه لازم می‌شود، اما خود store مشترک نقطهٔ شکست، latency، race condition، partition و نیازهای fail-open/fail-closed می‌آورد. مشخص کنید اگر store از دسترس خارج شد، کدام endpoint و کدام داده باید چگونه رفتار کنند.

محدودکردن فقط بر اساس IP ممکن است چند کاربر پشت NAT را با هم جریمه کند یا با چرخاندن IP دور زده شود. از identity معتبر، tenant، endpoint و هزینهٔ server-side، متناسب با ریسک، استفاده کنید؛ IP را فقط با سیاست روشن و دادهٔ حداقلی نگه دارید. Headerهایی مثل `X-Forwarded-For` فقط وقتی trusted هستند که مسیر proxy و مرزهای اعتماد آن صریح باشد؛ client می‌تواند header دلخواه بسازد.

## ۱۶. پاسخ 429 و رفتار retry

RFC 6585 status `429 Too Many Requests` را برای درخواست‌های بیش‌ازحد در یک بازه تعریف می‌کند؛ representation باید وضعیت را توضیح دهد، `Retry-After` می‌تواند پیشنهاد شود و پاسخ 429 نباید در cache ذخیره شود [۴]. RFC 9110 برای `Retry-After` مقدار ثانیه یا تاریخ HTTP را تعریف می‌کند [۴]. این RFCها آستانهٔ quota یا کلید شمارش را تعیین نمی‌کنند؛ آن سیاست با سرویس است.

کلاینت باید `Retry-After` معتبر را رعایت کند؛ اگر وجود ندارد، retry محدود با backoff و jitter و سقف تعداد تلاش‌ها طراحی شود. retry خودکار روی عملیات غیر-idempotent بدون کلید idempotency می‌تواند کار را دوباره انجام دهد. retry فوری همهٔ clientها پس از بازشدن quota، خود یک burst می‌سازد. `429` را با `503` اشتباه نگیرید و پاسخ نرخ‌محدود را در proxy cache نکنید.

## ۱۷. «چه چیزی رخ داد؟» را از «چرا؟» جدا کنید

Metrics تعداد و روند را برای سرویس یا policy نشان می‌دهند؛ logs رخدادهای جزئی را برای بازبینی و investigation ثبت می‌کنند؛ traces یک مسیر درخواست را در چند سرویس هم‌بسته می‌کنند. Security audit trail برای انتساب actionهای حساس است و ممکن است نیازهای دسترسی، نگه‌داری و integrity متفاوتی از debug log داشته باشد. OWASP توصیه می‌کند کاربردهای operational و security logging را با هدف و مقدار دادهٔ مناسب طراحی کنید [۵].

برای نمونه، metric کم‌جزئیات `auth_failure_total` می‌گوید تعداد شکست‌ها بالا رفته؛ audit event می‌گوید actionی با outcome رد شده؛ trace نشان می‌دهد مسیر درخواست از کدام component گذشته است. هیچ‌کدام به‌تنهایی علت ریشه‌ای را ثابت نمی‌کند. با timestamp هماهنگ و request ID سرورساخته می‌توانید شواهد را کنار هم ببینید؛ هرکدام را جداگانه از نظر retention و دسترسی حفاظت کنید.

## ۱۸. Audit event را ساخت‌یافته و کمینه بسازید

برای یک رویداد امنیتی، معمولاً timestamp، request/correlation ID، principal یا pseudonymous reference، tenant لازم، action، resource type، outcome، reason code، نسخهٔ policy و سرویسِ اجراکننده مفیدند. برای deny هم باید تصمیم ثبت شود تا مسیر سوءاستفاده یا اشکال policy قابل بررسی باشد. دادهٔ user-supplied را trust نکنید؛ متن حاوی newline یا control character ممکن است log را جعل کند.

از schema ساخت‌یافته و allowlist field استفاده کنید؛ blacklist ناقص از یک body دلخواه شکننده‌تر است. مقدار resource را تا حد نیاز کمینه کنید: ثبت `record.read` ممکن است برای audit کافی باشد و شناسهٔ کامل record ضرورتی نداشته باشد. رشتهٔ خام خطا، stack trace یا متن ورودی را به event عمومی نچسبانید. در صورت نیاز به دادهٔ حساس‌تر برای investigation، مسیر مجزا با مالک و مجوز محدود تعریف کنید.

## ۱۹. چه چیزی را به log راه ندهیم

Password، session token، API key، header کامل `Authorization`، private key، connection string، محتوای prompt، فایل آپلودی، پاسخ مدل، دادهٔ شخصی و متن حساس کاربر نباید به‌طور پیش‌فرض در log عمومی ذخیره شوند. Prompt می‌تواند password، پرونده، دادهٔ سلامت، code یا راز سازمانی داشته باشد؛ نبود فیلد «نام» در schema، آن را بی‌خطر نمی‌کند. OWASP Logging Cheat Sheet نمونه‌هایی از داده‌های حساسِ نامناسب برای ثبت مستقیم را فهرست می‌کند و حذف، masking، sanitization یا pseudonymization را بسته به نیاز پیشنهاد می‌کند [۵].

Allowlist ساده‌تر است: رخداد فقط مقدارهایی را می‌نویسد که برای آن تصمیم مشخصاً مجاز شده‌اند. اگر debugging به نمونهٔ محتوا نیاز دارد، جمع‌آوری باید انتخابی، آگاهانه، مدت‌دار، محدود به محیط امن و پس از ارزیابی privacy باشد؛ قرار دادن raw prompt در metrics یا alert راه‌حل کم‌هزینه‌ای نیست. حذف در log application کافی نیست اگر proxy، analytics یا provider همان محتوا را جدا ثبت می‌کند.

## ۲۰. Pseudonymization، حریم خصوصی و نگه‌داری

شناسهٔ جایگزین می‌تواند اتصال رخدادها را ممکن کند، اما اگر کلید نگاشت یا راه بازشناسی وجود دارد، داده ناشناس نشده است. hash سادهٔ email نیز ممکن است با حدس‌زدن ورودی‌ها برگشت‌پذیر باشد. جدا نگه‌داشتن جدول نگاشت، دسترسی محدود، چرخش شناسه و کاهش عمر داده می‌تواند ریسک را کم کند؛ اثر دقیق به داده، threat model و قانون مربوط وابسته است.

برای هر data field، هدف، basis/شرط جمع‌آوری، خواننده، گیرندهٔ ثالث، محل پردازش، نگه‌داری و حذف را روشن کنید. NIST Privacy Framework ابزار داوطلبانه‌ای برای مدیریت ریسک privacy است؛ صفحهٔ جاری NIST نسخهٔ ۱٫۱ را در وضعیت Initial Public Draft نشان می‌دهد، پس آن را final نخوانید [۶]. تصمیم حقوقی دربارهٔ consent، retention یا notification به حوزهٔ قضایی، قرارداد و مشاور ذی‌صلاح وابسته است؛ این متن راهنمای حقوقی نیست.

## ۲۱. از لاگ محافظت کنید؛ خودِ لاگ هم دارایی حساس است

Log store باید دسترسی خواندن، نوشتن، حذف و پیکربندی را تفکیک کند. سرویس محصول شاید اجازهٔ append داشته باشد، اما پاک‌کردن یا تغییر رخدادهای قدیمی باید محدود و قابل‌ردیابی باشد. انتقال امن، رمزنگاری در حال سکون، retention و حذف کنترل‌شده، نسخهٔ پشتیبان، ساعت همگام، دسترس‌پذیری و سلامت pipeline را بررسی کنید. رمزنگاری storage به‌تنهایی دسترسی نامجازِ کاربری که کلید دارد یا overcollection را حل نمی‌کند.

اگر log pipeline متوقف یا پر شود، امنیت و قابلیت تشخیص هر دو تحت تأثیرند. اندازهٔ صف، افت event، تاخیر دریافت و شکست parse را monitor کنید؛ برای رخدادهای حیاتی مسیر fail behavior تعریف کنید. «Append-only» یا «tamper-proof» را فقط وقتی ادعا کنید که پیکربندی و آزمون فنی آن را نشان داده باشد، نه چون سرویس log نام audit دارد.

## ۲۲. Metric کم‌جزئیات و قابل‌اقدام انتخاب کنید

برای داشبورد آغازین می‌توان نرخ درخواست، latency و error class را در سطح endpoint یا سرویس دید؛ برای کنترل امنیتی شمارش 401، 403، 429، شکست validation، تغییر role و عملیات حساس را با دسته‌های ثابت دنبال کرد. Google SRE چهار signal متداول برای سرویس کاربرمحور—latency، traffic، errors و saturation—را به‌عنوان شروع مطرح می‌کند، نه فهرست کامل همهٔ ریسک‌های امنیتی [۹]. فصل ۶۷ جزئیات latency و صف را پوشش می‌دهد؛ اینجا از آن‌ها برای تشخیص رخداد سرویس بهره می‌گیریم، نه تکرار benchmark.

برچسب metric را کم‌کاردینال نگه دارید. `user_id`، `tenant_id`، prompt hash، request ID و IP روی هر سری زمانی می‌توانند هم هزینه و cardinality را بالا ببرند و هم شناسهٔ پیوندپذیر بسازند. برای بررسی یک درخواست از trace/log با دسترسی کنترل‌شده استفاده کنید، نه این‌که همهٔ شناسه‌ها را در label metric تکثیر کنید. `429` به‌تنهایی حمله را ثابت نمی‌کند؛ می‌تواند کاربر پرترافیک، تنظیم نامناسب quota یا retry storm باشد.

## ۲۳. Alert باید مالک، آستانه و اقدام داشته باشد

هر alert باید پرسشی را جواب دهد: چه signal از چه حدی خارج شده، چه کسی مسئول triage است، چه زمان/شدتی دارد و اولین اقدام امن چیست؟ Alert روی هر 401 ممکن است انبوه false positive بسازد؛ شکست‌های مکرر از یک زمینه، تغییر ناگهانی الگو یا چند نوع کنترل کنار هم ممکن است با بررسی انسان ارزشمندتر شوند. Threshold را از baseline و هزینهٔ missed detection انتخاب کنید و آن را پس از تغییر ترافیک بازبینی کنید.

Pager، ticket و dashboard سطح فوریت متفاوت دارند. موردی که فقط باید فردا بررسی شود نباید همان page اضطراری outage باشد. Rule و route را با دادهٔ ساختگی یا تمرین کنترل‌شده بیازمایید؛ اگر تست alert بدون عبور از مسیر واقعیِ log/metric اجرا شود، شاید wiring اصلی هنوز خراب باشد. پس از incident alertهای پرصدا را tune کنید، نه این‌که شواهد را به‌طور خودکار حذف کنید.

## ۲۴. Observability در مسیر AI با privacy پیوند دارد

در یک گردش‌کار AI، prompt ممکن است از فرم، فایل، retrieval، ابزار یا پیام چندمستأجری بیاید؛ بخشی از آن به provider بیرونی می‌رود و ممکن است در کنترل‌های retention یا monitoring provider نیز قرار گیرد. خروجی مدل هم می‌تواند اطلاعات حساس، نقل‌قول متن ورودی یا دادهٔ یک tenant را بازتاب دهد. مشخص کنید چه کسی متن را می‌بیند، کجا پردازش می‌شود، چه telemetry به provider می‌رسد و چه policy برای حذف یا نگه‌داری وجود دارد.

استفاده از provider خصوصی، feature «عدم آموزش»، TLS یا تشخیص خودکار PII به‌تنهایی privacy را اثبات نمی‌کند. قراردادها، subprocessors، محل داده، مدت نگه‌داری، سطح دسترسی و مسیر درخواست حذف را بررسی کنید؛ آن‌ها با عوض‌شدن مدل یا تنظیمات می‌توانند تغییر کنند. در صورت امکان، داده را پیش از ارسال کمینه کنید و policyهای logging را در هر hop اعمال کنید. پروفایل NIST AI 600-1 ریسک‌های مولد را در چارچوب مدیریت ریسک سازمانی طرح می‌کند؛ در این فصل فقط منبع زمینه است و دستورالعمل اختصاصی برای log یا تضمین privacy نیست [۸]. ارزیابی privacy برنامه‌ای به فصل ۶۵ و آزمون prompt/دادهٔ خصمانه به فصل ۶۴ ارجاع دارد.

## ۲۵. دادهٔ عملیاتی را از محتوای محصول جدا کنید

Audit event می‌تواند بگوید `assistant.generate` برای tenant ساختگی انجام شد، outcome چه بود و کدام policy revision اجرا شد، بی‌آن‌که prompt یا پاسخ کامل ذخیره شود. اگر برای quality review نمونهٔ محتوا لازم باشد، آن را در مخزن دیگری با sampling محدود، دسترسی reviewer، مدت نگه‌داری مشخص و مسیر حذف نگه دارید. از log عادی backend به‌عنوان آرشیو دائمی مکالمه استفاده نکنید.

همچنین cache پاسخ، provider trace و incident evidence را یک مخزن واحد تلقی نکنید؛ هرکدام purpose، freshness و دسترسی متفاوت دارند. اگر کاربر درخواست حذف داده دارد، mapping میان شناسهٔ pseudonymous و دادهٔ اصلی باید در فرآیند حذف تعریف شود؛ hash بی‌نام‌شده را «غیرشخصی» فرض نکنید.

## ۲۶. از alert به incident با فرضیه، نه نتیجه‌گیری قطعی

Alert یک signal برای بررسی است؛ incident طبقه‌بندی‌شده‌ای است که اثر و پاسخ سازمانی می‌خواهد. ابتدا زمان، سامانه، credential family، tenantهای احتمالی، action، مدل/provider و دادهٔ در معرض خطر را از شواهد مجاز جمع کنید. زمان را UTC و مسیر درخواست را با ID هم‌بسته دنبال کنید. هم‌بستگی دو log علت را ثابت نمی‌کند؛ clock skew، sampling، missing events و منبع غیرقابل‌اعتماد را نیز در نظر بگیرید.

NIST SP 800-61 Rev. 3 پاسخ به رخداد را در مدیریت ریسک و CSF 2.0 جای می‌دهد؛ آماده‌سازی با Govern, Identify و Protect پشتیبانی می‌شود، کار اصلی رخداد بر Detect, Respond و Recover تمرکز دارد و improvement پیوسته است [۷]. این نسخه را با lifecycle قدیمی چهارمرحله‌ای یکی نگیرید؛ سازمان می‌تواند playbook عملی خود را داشته باشد، اما باید آن را با چارچوب منتخب و نقش‌های واقعی سازگار کند.

## ۲۷. نقش‌ها و کانال ارتباط را از قبل مشخص کنید

Incident commander هماهنگی و اولویت را نگه می‌دارد؛ responder فنی containment و شواهد را انجام می‌دهد؛ privacy/legal/security به بررسی دامنه و الزام‌های اطلاع‌رسانی کمک می‌کنند؛ مالک محصول تصمیم‌های اثر بر کاربر را می‌گیرد. یک نفر نباید هم‌زمان تمام این نقش‌ها را بپذیرد، مگر تیم کوچک آن را آگاهانه ثبت کرده باشد. contact list، escalation path و deputy را بیرون از سامانهٔ درگیر نیز در دسترس بگذارید.

برای پیام داخلی/کاربر، فقط facts تأییدشده، دامنهٔ نامعلوم، اقدام انجام‌شده و زمان به‌روزرسانی را بگویید. وعدهٔ «هیچ داده‌ای لو نرفته» را از نبود log یا نبود alert نتیجه نگیرید. مهلت قانونی یا قراردادی اطلاع‌رسانی را مشاور مسئول بر اساس محل، نقش پردازش و نوع داده تعیین می‌کند.

## ۲۸. Playbook: credential مشکوک یا افشاشده

۱) مسیر استفاده را محدود یا credential را revoke کنید؛ کلید تازه را از مسیر امن و با scope محدود بسازید. ۲) زمان و بازهٔ احتمالی افشا، service، audience، مجوز و درخواست‌های مربوط را با log پالایش‌شده بررسی کنید. ۳) شواهد لازم را حفظ کنید، اما token خام یا prompt را در ticket و پیام تیمی کپی نکنید. ۴) scope آسیب را برای tenantها، عملیات و providerهای وابسته برآورد کنید؛ uncertainty را مشخص کنید. ۵) بهبود key rotation، secret scanning، access review یا alert rule را مالک‌دار کنید و پس از recovery آزمون کنید.

Rotation بدون revoke نسخهٔ قبلی ممکن است credential درزکرده را فعال بگذارد؛ revoke بدون بررسی scope ممکن است کاربر بی‌گناه را ناخواسته قطع کند. ترتیب باید با provider و threat model سنجیده شود. هر action، زمان، مسئول و evidence reference را در incident record نگه دارید؛ secret را وارد record نکنید.

## ۲۹. Playbook: دسترسی بین‌مستأجری یا prompt leak

ابتدا endpoint، feature، cache، retrieval، log sink و نسخه‌های درخواست‌پذیرِ درگیر را شناسایی کنید. اگر exposure ادامه دارد، مسیر را محدود یا feature را غیرفعال کنید؛ عوض‌کردن prompt یا پیام کاربری، جای containment را نمی‌گیرد. سپس tenantهای احتمالاً درگیر، نوع و مدت داده، actorهای دسترسی‌دار، providerهای دریافت‌کننده و logهای موجود را با privacy/security تیم بررسی کنید.

مدرک‌های لازم را با دسترسی محدود حفظ کنید و raw content را به کانال عمومی تکثیر نکنید. اشکال را با آزمون tenant-isolation و fixture ساختگی بازتولید کنید؛ آزمون تولیدی را بدون مجوز و با دادهٔ واقعی انجام ندهید. پس از اصلاح، cache و indexهای کپی‌شده، log retention و درخواست حذف را هم ارزیابی کنید؛ بازیابی سرویس بدون بررسی اثر بر فرد یا سازمان، پایان incident نیست.

## ۳۰. Containment، recovery و improvement شواهد می‌خواهند

Containment می‌تواند revoke، محدودسازی scope، کاهش access یا disable feature باشد؛ recovery یعنی کنترل اصلاح‌شده را با آزمون و مانیتورینگ معتبر فعال کنید؛ closure باید مسئول، دامنهٔ اثر، تصمیم‌های اطلاع‌رسانی، شواهد و اقدام‌های باقیمانده را ثبت کند. این phaseها در پروژهٔ همراه فقط state transition ساختگی‌اند و اجرای واقعیِ disable، rotation یا اطلاع‌رسانی را انجام نمی‌دهند.

Post-incident review را برای یادگیری و اصلاح سیستم به‌کار ببرید، نه سرزنش فرد. Root cause ممکن است ترکیب نقص policy، فرض نادرست در data flow، log ناقص و قرارداد provider باشد. اقدام اصلاحی باید مالک، مهلت و آزمون اثربخشی داشته باشد؛ در غیر این صورت درس‌آموخته در سند باقی می‌ماند و ریسک تغییر نمی‌کند.

## ۳۱. پروژهٔ فصل: آزمایشگاه کنترل دسترسی و ممیزی امن

`book-engineering/projects/68-product-security-lab/` یک trace دست‌ساز را با credential registry ساختگی، کنترل tenant و role، token bucket، audit allowlist، metric کم‌جزئیات، detector ساده و state machine رخداد تحلیل می‌کند. شناسه‌ها، prompt markerها و credential markerها همه ساختگی‌اند؛ fixture نه token قابل‌استفاده دارد، نه PII، شبکه، مدل، provider یا storage بیرونی. پروژه صحت یک policy کوچک را می‌آزماید، نه انطباق یا امنیت محصول واقعی را.

سیاست‌سنج tenant را از credential registry می‌گیرد و `claimed_tenant_ref` در request را برای اعطای دسترسی نادیده می‌گیرد. درخواست‌های فاقد credential یا با credential ناشناخته/غیرفعال 401 می‌گیرند؛ سپس محدودیت نرخ بر اساس tenantِ احرازشده بررسی می‌شود؛ بعد role و tenant منبع ارزیابی می‌شوند. Audit event از allowlist فیلدهای محدود ساخته می‌شود؛ raw prompt، token marker، email و IP در آن نیستند. در fixture، سه شکست احراز هویت در پنجرهٔ زمانی ساختگی یک alert می‌سازند و سه evidence reference ساختگی یک incident را تا closed می‌برند.

## ۳۲. اجرا و خواندن نتیجهٔ آزمایشگاه

از ریشهٔ repository:

```bash
(cd book-engineering/projects/68-product-security-lab && python -m unittest -v)
python book-engineering/projects/68-product-security-lab/security_ops.py \
  --fixture book-engineering/projects/68-product-security-lab/synthetic_security_events.json \
  --output /tmp/ch68-results.json
cmp /tmp/ch68-results.json book-engineering/projects/68-product-security-lab/results.json
```

`results.json` تعداد درخواست‌های allow/deny/429، تعداد audit eventها، alertها و وضعیت نهایی playbook را گزارش می‌کند. خروجی fixture برای policy نسخهٔ `synthetic-v1` قطعی است. تعداد 401 یا 429 در ۱۴ رکورد ساختگی، نرخ حمله یا حد مناسب production نیست. Retry timer در fixture میلی‌ثانیه‌ای و deterministic است؛ توزیع واقعی بار، race condition، shared store، token validation cryptographic و latency network بررسی نمی‌شود.

## ۳۳. دامنهٔ نتیجه و ضدالگوها

این آزمایشگاه سیستم auth، OAuth/OIDC، JWT، API server، limiter توزیع‌شده، secret store، log sink، SIEM، privacy workflow یا on-call pager نمی‌سازد. تست role و tenant فقط منطق fixture را نشان می‌دهد. Alert ساده ممکن است false positive یا false negative داشته باشد؛ schema امن نیز به معنی storage امن، حذف موفق یا مجوز قانونی نیست. هیچ مدل، کیفیت خروجی، fairness، privacy کامل، انطباق یا آمادگی حادثه تأیید نمی‌شود.

از این ضدالگوها دوری کنید: `tenant_id` ارسالی client را مرجع مجوز بگیرید؛ هر 401 را attack بدانید؛ فقط با IP quota را اعمال کنید؛ prompt یا full bearer token را برای debug ذخیره کنید؛ log redaction را فقط در dashboard انجام دهید؛ `403`، `429` و `503` را یکی کنید؛ alert بسازید که مالک و اقدام ندارد؛ incident را به‌خاطر نبود شواهد «منتفی» اعلام کنید؛ یا rotation را بدون revoke و بررسی scope تمام‌شده بدانید.

## ۳۴. منابع و تاریخ بازبینی منابع

منابع زیر در ۴ نوامبر ۲۰۲۶ بازبینی شدند. استاندارد یا چارچوب عمومی جای threat model، آزمون و بازبینی حقوقی کاربرد شما را نمی‌گیرد.

۱) Lodderstedt و همکاران، [RFC 9700: Best Current Practice for OAuth 2.0 Security](https://www.rfc-editor.org/rfc/rfc9700.html)، IETF، ژانویهٔ ۲۰۲۵؛ BCP 240.
۲) NIST، [SP 800-63-4: Digital Identity Guidelines](https://csrc.nist.gov/pubs/sp/800/63/4/final)، نسخهٔ نهایی، ژوئیهٔ ۲۰۲۵؛ راهنمای دامنه‌مند هویت دیجیتال.
۳) OWASP، [API Security Top 10 — 2023](https://api-security.owasp.org/editions/2023/en/0x11-t10/)، شامل ریسک‌های authorization و مصرف منابع API.
۴) Nottingham و Fielding، [RFC 6585 §4](https://www.rfc-editor.org/rfc/rfc6585.html#section-4)، آوریل ۲۰۱۲؛ status `429` و رفتار cache. Fielding و همکاران، [RFC 9110 §10.2.3](https://www.rfc-editor.org/rfc/rfc9110.html#section-10.2.3)، ژوئن ۲۰۲۲؛ قالب `Retry-After`.
۵) OWASP, [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)، راهنمای پیوستهٔ logging امنیتی؛ تاریخ دسترسی: ۴ نوامبر ۲۰۲۶.
۶) NIST، [Privacy Framework](https://www.nist.gov/privacy-framework)، نسخهٔ ۱٫۰ نهایی؛ [CSWP 40: Privacy Framework 1.1 Initial Public Draft](https://csrc.nist.gov/pubs/cswp/40/nist-privacy-framework-11/ipd)، پیش‌نویس اولیهٔ عمومی در زمان بازبینی.
۷) Nelson و همکاران، [SP 800-61 Rev. 3: Incident Response Recommendations and Considerations](https://csrc.nist.gov/pubs/sp/800/61/r3/final)، آوریل ۲۰۲۵؛ پروفایل CSF 2.0.
۸) NIST، [AI 600-1: Generative Artificial Intelligence Profile](https://doi.org/10.6028/NIST.AI.600-1)، ژوئیهٔ ۲۰۲۴؛ منبع زمینه برای ریسک‌ها و incident disclosure در کاربردهای GAI.
۹) Ewaschuk، [Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)، Google SRE Book، فصل ۶؛ چهار signal به‌عنوان نقطهٔ آغاز پایش، نه فهرست امنیت کامل.

## ۳۵. تمرین‌ها

۱. یک request دارای token معتبر اما `audience` نادرست است. کدام مرحله باید آن را رد کند و چرا پاسخ موفق endpoint دیگری مجوز دسترسی به این API نیست؟

۲. یک کاربر A شناسهٔ record متعلق به tenant B را در request قرار می‌دهد. سه نقطه‌ای را نام ببرید که باید object-level authorization را کنترل کنند و بگویید `tenant_id` ارسالی client را چگونه تفسیر می‌کنید.

۳. برای یک endpoint تولید تصویر، سه محدودیت متفاوت پیشنهاد کنید: یکی بر تعداد درخواست، یکی بر concurrency و یکی بر هزینهٔ server-side. توضیح دهید چرا یک limit بر اساس IP کافی نیست.

۴. Token bucket ظرفیت ۵ واحد دارد، با نرخ ۲ واحد بر ثانیه بازپر می‌شود و اکنون ۱ واحد دارد. پس از ۱٫۵ ثانیه، آیا درخواست با هزینهٔ ۴ پذیرفته می‌شود؟ فرض‌ها و سقف ظرفیت را نشان دهید.

۵. یک API سه 429 و یک 503 در یک دقیقه ثبت کرده است. چه اطلاعاتی برای تشخیص quota فردی از overload کل سرویس لازم دارید؟ چرا شمارش خام به‌تنهایی حمله را ثابت نمی‌کند؟

۶. برای یک request دارای prompt، token، tenant، action و response size، یک audit event کمینه طراحی کنید. چه فیلدهایی را ثبت نمی‌کنید و چه شناسه‌ای را برای correlation به‌کار می‌برید؟

۷. پس از مشاهدهٔ credential مشکوک، ترتیب containment، بررسی دامنه، rotation، recovery و اطلاع‌رسانی را بنویسید. کدام تصمیم‌ها به threat model و قانون/قرارداد وابسته‌اند؟

۸. Alert یک log pipeline متوقف شده را نشان می‌دهد، اما درخواست‌ها ظاهراً پاسخ می‌گیرند. چه شواهدی را جمع می‌کنید، چه چیزی را فرض نمی‌کنید و چگونه مشخص می‌کنید incident بسته شده است؟

## ۳۶. جمع‌بندی

امنیت محصول با «هویت معتبر» تمام نمی‌شود: هر action باید authorization object/tenant و محدودیت مصرف مناسب داشته باشد. Rate limit از quota و صف جداست؛ eventهای امنیتی باید با schema قابل‌بررسی و دادهٔ حداقلی ثبت شوند؛ prompt، token و PII را از logهای عادی بیرون نگه دارید. Metrics و alertها signal می‌دهند، نه حکم قطعی. برای رخداد، مالک، containment، recovery، اطلاع‌رسانی و improvement را پیشاپیش تعریف کنید و شواهد واقعی را از fixture یا فرض جدا گزارش دهید.

برای ادامه، [پاسخ‌نامهٔ مستقل فصل ۶۸](../answers/68-product-security-monitoring-fa.md)، [README آزمایشگاه](../projects/68-product-security-lab/README.md)، [fixture ساختگی](../projects/68-product-security-lab/synthetic_security_events.json)، [نتایج](../projects/68-product-security-lab/results.json) و [گزارش ممیزی](68-audit-report-fa.md) را ببینید. فصل ۶۹ به استقرار و CI/CD می‌پردازد. محصول این milestone وب/PWA و Markdown است؛ PDF و EPUB تولید یا آزموده نشده‌اند.

## پیوست اجرایی — سیاست‌سنج و شبیه‌ساز رخداد

```python
"""Synthetic policy audit for identity, tenant checks, quotas, safe logs, and response."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

PROJECT_ID = "v5-ch07-security-ops-synthetic-v1"
ALLOWED_ACTIONS = {
    "record.read": {"reader", "security-admin"},
    "audit.export": {"security-admin"},
}
ALLOWED_RESOURCE_TYPES = {"record", "audit-log"}
SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
REASON_CODES = {
    "policy_allow",
    "missing_credential",
    "invalid_credential",
    "rate_limit_exceeded",
    "tenant_boundary",
    "role_required",
    "action_not_permitted",
}
RESPONSE_TRANSITIONS = {
    "open": ("contain", "contained", "credential_revocation_record"),
    "contained": ("recover", "recovered", "rotation_verified"),
    "recovered": ("close", "closed", "postmortem_reviewed"),
}


class TokenBucket:
    """A deterministic per-key token bucket; this is not distributed state."""

    def __init__(self, capacity: int, refill_units_per_second: int):
        if type(capacity) is not int or capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        if type(refill_units_per_second) is not int or refill_units_per_second <= 0:
            raise ValueError("refill rate must be a positive integer")
        self.capacity = capacity
        self.refill_rate = refill_units_per_second
        self.tokens = float(capacity)
        self.updated_ms: int | None = None

    def consume(self, timestamp_ms: int, cost: int) -> tuple[bool, int]:
        if type(timestamp_ms) is not int or timestamp_ms < 0:
            raise ValueError("timestamp_ms must be a non-negative integer")
        if type(cost) is not int or cost <= 0 or cost > self.capacity:
            raise ValueError("cost must be a positive integer no greater than capacity")
        if self.updated_ms is None:
            self.updated_ms = timestamp_ms
        else:
            if timestamp_ms < self.updated_ms:
                raise ValueError("timestamps for one bucket must be monotonic")
            elapsed_ms = timestamp_ms - self.updated_ms
            self.tokens = min(
                float(self.capacity),
                self.tokens + (elapsed_ms * self.refill_rate / 1000.0),
            )
            self.updated_ms = timestamp_ms
        if self.tokens + 1e-12 >= cost:
            self.tokens = max(0.0, self.tokens - cost)
            return True, 0
        seconds_to_refill = (cost - self.tokens) / self.refill_rate
        retry_after_ms = max(1, math.ceil(seconds_to_refill * 1000.0 - 1e-9))
        return False, retry_after_ms


def validate_fixture(fixture: dict[str, Any]) -> None:
    """Validate the fixed schema and synthetic-only scope before evaluation."""
    if not isinstance(fixture, dict) or fixture.get("fixture_id") != PROJECT_ID:
        raise ValueError("unexpected fixture id")
    if fixture.get("synthetic") is not True:
        raise ValueError("fixture must be explicitly marked synthetic")
    if fixture.get("contains_personal_data") is not False:
        raise ValueError("fixture must declare no personal data")
    if fixture.get("contains_real_credentials") is not False:
        raise ValueError("fixture must declare no real credentials")
    policy = fixture.get("policy")
    if not isinstance(policy, dict) or not isinstance(policy.get("version"), str) or not SAFE_REQUEST_ID.fullmatch(policy["version"]):
        raise ValueError("policy version must be a safe non-empty identifier")
    if type(policy.get("bucket_capacity")) is not int or policy["bucket_capacity"] <= 0:
        raise ValueError("bucket_capacity must be a positive integer")
    if type(policy.get("refill_units_per_second")) is not int or policy["refill_units_per_second"] <= 0:
        raise ValueError("refill rate must be a positive integer")
    if type(policy.get("auth_failure_threshold")) is not int or policy["auth_failure_threshold"] < 2:
        raise ValueError("auth failure threshold must be at least two")
    if type(policy.get("auth_failure_window_ms")) is not int or policy["auth_failure_window_ms"] <= 0:
        raise ValueError("auth failure window must be a positive integer")

    credentials = fixture.get("credential_registry")
    if not isinstance(credentials, dict) or not credentials:
        raise ValueError("credential_registry must be a non-empty object")
    for credential_ref, identity in credentials.items():
        if not isinstance(credential_ref, str) or not SAFE_REQUEST_ID.fullmatch(credential_ref):
            raise ValueError("credential references must be safe non-empty identifiers")
        if not isinstance(identity, dict):
            raise ValueError("credential entry must be an object")
        for key in ("principal_ref", "tenant_ref"):
            if not isinstance(identity.get(key), str) or not SAFE_REQUEST_ID.fullmatch(identity[key]):
                raise ValueError(f"credential entry needs a safe {key}")
        if not isinstance(identity.get("roles"), list) or not all(isinstance(role, str) and SAFE_REQUEST_ID.fullmatch(role) for role in identity["roles"]):
            raise ValueError("credential roles must be a safe string list")
        if not isinstance(identity.get("active"), bool):
            raise ValueError("credential active flag must be boolean")

    events = fixture.get("events")
    if not isinstance(events, list) or not events:
        raise ValueError("events must be a non-empty list")
    event_ids: set[str] = set()
    prior_timestamp = -1
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("each event must be an object")
        event_id = event.get("event_id")
        request_id = event.get("request_id")
        timestamp_ms = event.get("timestamp_ms")
        if not isinstance(event_id, str) or not SAFE_REQUEST_ID.fullmatch(event_id) or event_id in event_ids:
            raise ValueError("event ids must be safe and unique")
        if not isinstance(request_id, str) or not SAFE_REQUEST_ID.fullmatch(request_id):
            raise ValueError("request_id must use the safe fixture identifier alphabet")
        if type(timestamp_ms) is not int or timestamp_ms < 0 or timestamp_ms < prior_timestamp:
            raise ValueError("event timestamps must be non-negative and monotonic")
        if not isinstance(event.get("action"), str) or not event["action"]:
            raise ValueError("action is required")
        if event.get("resource_type") not in ALLOWED_RESOURCE_TYPES:
            raise ValueError("resource_type is outside the fixed example schema")
        if type(event.get("estimated_cost_units")) is not int or not 1 <= event["estimated_cost_units"] <= policy["bucket_capacity"]:
            raise ValueError("estimated_cost_units must be within the server-side bucket capacity")
        event_ids.add(event_id)
        prior_timestamp = timestamp_ms

    steps = fixture.get("response_steps")
    if not isinstance(steps, list):
        raise ValueError("response_steps must be a list")
    for step in steps:
        if not isinstance(step, dict) or not all(isinstance(step.get(key), str) and SAFE_REQUEST_ID.fullmatch(step[key]) for key in ("incident_id", "phase", "evidence_type", "evidence_ref")):
            raise ValueError("response steps require safe incident, phase, evidence type, and evidence reference identifiers")


def _audit_event(
    event: dict[str, Any],
    identity: dict[str, Any] | None,
    outcome: str,
    status_code: int,
    reason_code: str,
    policy_version: str,
) -> dict[str, Any]:
    """Construct an event from an allowlist; never copy arbitrary request fields."""
    if reason_code not in REASON_CODES:
        raise ValueError("reason code is not in the fixed low-cardinality set")
    action = event.get("action")
    safe_action = action if action in ALLOWED_ACTIONS else "unknown_action"
    resource_type = event.get("resource_type")
    safe_resource_type = resource_type if resource_type in ALLOWED_RESOURCE_TYPES else "other"
    return {
        "timestamp_ms": event["timestamp_ms"],
        "request_id": event["request_id"],
        "actor_ref": identity["principal_ref"] if identity else "unknown",
        "tenant_ref": identity["tenant_ref"] if identity else "unknown",
        "action": safe_action,
        "resource_type": safe_resource_type,
        "outcome": outcome,
        "status_code": status_code,
        "reason_code": reason_code,
        "policy_version": policy_version,
    }


def _advance_incident(incident: dict[str, Any], step: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(incident)
    current_state = updated["state"]
    transition = RESPONSE_TRANSITIONS.get(current_state)
    if transition is None:
        raise ValueError("incident is already closed or in an unknown state")
    expected_phase, next_state, expected_evidence = transition
    if step.get("incident_id") != updated["incident_id"]:
        raise ValueError("response step references a different incident")
    if step.get("phase") != expected_phase:
        raise ValueError(f"expected incident phase {expected_phase}")
    if step.get("evidence_type") != expected_evidence or not step.get("evidence_ref"):
        raise ValueError(f"phase {expected_phase} requires evidence type {expected_evidence}")
    updated["state"] = next_state
    updated["timeline"].append({
        "phase": expected_phase,
        "state": next_state,
        "evidence_ref": step["evidence_ref"],
    })
    return updated


def simulate(fixture: dict[str, Any], fixture_sha256: str) -> dict[str, Any]:
    validate_fixture(fixture)
    policy = fixture["policy"]
    credentials = fixture["credential_registry"]
    buckets: dict[str, TokenBucket] = {}
    decisions: list[dict[str, Any]] = []
    audit_events: list[dict[str, Any]] = []
    auth_failure_times: list[tuple[int, str]] = []
    alerts: list[dict[str, Any]] = []
    alert_emitted = False

    for event in fixture["events"]:
        credential_ref = event.get("credential_ref")
        identity = credentials.get(credential_ref) if isinstance(credential_ref, str) else None
        if identity is None or not identity.get("active"):
            reason_code = "missing_credential" if credential_ref is None else "invalid_credential"
            decision = {
                "event_id": event["event_id"],
                "request_id": event["request_id"],
                "outcome": "denied",
                "status_code": 401,
                "reason_code": reason_code,
                "retry_after_ms": 0,
            }
            auth_failure_times.append((event["timestamp_ms"], event["request_id"]))
            cutoff = event["timestamp_ms"] - policy["auth_failure_window_ms"]
            auth_failure_times = [(ts, rid) for ts, rid in auth_failure_times if ts >= cutoff]
            if not alert_emitted and len(auth_failure_times) >= policy["auth_failure_threshold"]:
                window_events = auth_failure_times[-policy["auth_failure_threshold"]:]
                alerts.append({
                    "alert_code": "AUTH_FAILURE_BURST",
                    "severity": "review",
                    "count": len(window_events),
                    "window_ms": policy["auth_failure_window_ms"],
                    "evidence_request_ids": [request_id for _, request_id in window_events],
                    "source_ip_logged": False,
                    "credential_value_logged": False,
                })
                alert_emitted = True
            audit_events.append(_audit_event(event, None, "denied", 401, reason_code, policy["version"]))
            decisions.append(decision)
            continue

        tenant_ref = identity["tenant_ref"]
        bucket = buckets.setdefault(
            tenant_ref,
            TokenBucket(policy["bucket_capacity"], policy["refill_units_per_second"]),
        )
        admitted, retry_after_ms = bucket.consume(event["timestamp_ms"], event["estimated_cost_units"])
        if not admitted:
            decision = {
                "event_id": event["event_id"],
                "request_id": event["request_id"],
                "outcome": "rate_limited",
                "status_code": 429,
                "reason_code": "rate_limit_exceeded",
                "retry_after_ms": retry_after_ms,
            }
            audit_events.append(_audit_event(event, identity, "rate_limited", 429, "rate_limit_exceeded", policy["version"]))
            decisions.append(decision)
            continue

        roles = set(identity["roles"])
        allowed_roles = ALLOWED_ACTIONS.get(event["action"])
        if allowed_roles is None:
            outcome, status_code, reason_code = "denied", 403, "action_not_permitted"
        elif event.get("resource_tenant_ref") != tenant_ref:
            outcome, status_code, reason_code = "denied", 403, "tenant_boundary"
        elif roles.isdisjoint(allowed_roles):
            outcome, status_code, reason_code = "denied", 403, "role_required"
        else:
            outcome, status_code, reason_code = "allowed", 200, "policy_allow"
        decision = {
            "event_id": event["event_id"],
            "request_id": event["request_id"],
            "outcome": outcome,
            "status_code": status_code,
            "reason_code": reason_code,
            "retry_after_ms": 0,
        }
        audit_events.append(_audit_event(event, identity, outcome, status_code, reason_code, policy["version"]))
        decisions.append(decision)

    incidents: list[dict[str, Any]] = []
    if alert_emitted:
        incident = {
            "incident_id": "incident-001",
            "alert_code": "AUTH_FAILURE_BURST",
            "state": "open",
            "timeline": [],
        }
        for step in fixture["response_steps"]:
            if step["incident_id"] == incident["incident_id"]:
                incident = _advance_incident(incident, step)
        incidents.append(incident)
    elif fixture["response_steps"]:
        raise ValueError("fixture contains response steps but did not trigger a matching alert")

    reason_counts: dict[str, int] = {}
    for event in audit_events:
        reason_counts[event["reason_code"]] = reason_counts.get(event["reason_code"], 0) + 1
    outcome_counts = {
        "allowed": sum(item["outcome"] == "allowed" for item in decisions),
        "denied": sum(item["outcome"] == "denied" for item in decisions),
        "rate_limited": sum(item["outcome"] == "rate_limited" for item in decisions),
    }
    return {
        "project_id": PROJECT_ID,
        "fixture_id": fixture["fixture_id"],
        "fixture_sha256": fixture_sha256,
        "synthetic": True,
        "request_count": len(fixture["events"]),
        "decision_counts": outcome_counts,
        "reason_counts": dict(sorted(reason_counts.items())),
        "decisions": decisions,
        "auth_failure_count": sum(item["status_code"] == 401 for item in decisions),
        "authorization_denial_count": sum(item["status_code"] == 403 for item in decisions),
        "rate_limited_count": sum(item["status_code"] == 429 for item in decisions),
        "audit_event_count": len(audit_events),
        "audit_events": audit_events,
        "alerts": alerts,
        "incident_count": len(incidents),
        "incidents": incidents,
        "metrics": {
            "request_count": len(decisions),
            "allowed": outcome_counts["allowed"],
            "denied": outcome_counts["denied"],
            "rate_limited": outcome_counts["rate_limited"],
            "alert_count": len(alerts),
            "private_fields_logged": 0,
            "dimension_fields": ["outcome", "reason_code"],
        },
        "external_http_requests": 0,
        "live_auth_provider_calls": 0,
        "live_model_calls": 0,
        "gpu_used": False,
        "personal_records": 0,
        "real_credentials_used": False,
        "scope": "Synthetic deterministic policy simulation; not an authentication implementation, production limiter, security audit, or incident-response service.",
        "limitations": [
            "All identities, tenants, credentials, request times, resource references, and canary strings are invented; no user or production trace is represented.",
            "Credential references select synthetic registry entries; no OAuth, OIDC, JWT signature validation, password verifier, identity provider, or cryptographic key is implemented.",
            "The token bucket is single-process deterministic state; it does not model distributed consistency, real network latency, concurrent races, or provider quotas.",
            "Audit events are assembled by a fixed allowlist for this fixture; this does not prove that another logger, proxy, provider, or storage system is privacy-safe.",
            "The alert threshold and response evidence are synthetic policy choices; they are not an attack probability, compliance finding, or proof of actual credential revocation/recovery.",
            "No legal review, human incident response, notification decision, model-quality evaluation, penetration test, or production security control was performed."
        ],
    }


def run_file(fixture_path: Path) -> dict[str, Any]:
    raw = fixture_path.read_bytes()
    fixture = json.loads(raw.decode("utf-8"))
    return simulate(fixture, hashlib.sha256(raw).hexdigest())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_fixture = Path(__file__).with_name("synthetic_security_events.json")
    default_output = Path(__file__).with_name("results.json")
    parser.add_argument("--fixture", type=Path, default=default_fixture)
    parser.add_argument("--output", type=Path, default=default_output)
    args = parser.parse_args(argv)
    result = run_file(args.fixture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
