# پروژهٔ نهایی: ساخت، ارزیابی و انتشار مسئولانهٔ یک مدل مستقل

**پیش‌نیاز:** ارزیابی، طراحی آزمایش، مستندسازی داده و مدل، انتشار نرم‌افزار و مسیر پژوهش در فصل‌های ۶۵ و ۶۹ تا ۷۲. **خروجی:** یک بستهٔ مستقل و آزمون‌پذیر شامل داده‌کارت، کد، checkpoint، ارزیابی، مدل‌کارت، گزارش محیط و تصمیم انتشار.

فصل محلی ۱۲ جلد پنجم = فصل سراسری ۷۳. **تاریخ بازبینی منابع: ۴ نوامبر ۲۰۲۶.** این فصل پروژهٔ نهایی را در یک بستهٔ کوچک و مستقل اجرا می‌کند؛ نتایج نمونه، شواهد عملکرد واقعی نیستند.

![شکل ۵-۱۲-۱ — زنجیرهٔ تحویل پروژه از تعریف مرز کاربرد و نمونهٔ دادهٔ ساختگی، به ثبت برنامه و آموزش فقط با دادهٔ آموزش، سپس نقطهٔ ذخیرهٔ مدل و سنجه‌های جداگانه؛ داده‌کارت و مدل‌کارت به بسته افزوده می‌شوند و دروازهٔ حقوق، خطر و بازتولید تصمیم می‌گیرد. خروجی آموزشی می‌تواند منتشر شود، اما مسیر استقرار مدل در این مثال متوقف است. هر گام با عنوان و شماره مشخص شده و معنا به رنگ وابسته نیست.](../diagrams/v5-ch12-capstone-release.svg)

## ۱. پایان جلد، نه بازگویی فصل‌های پیشین

پروژهٔ نهایی قرار نیست دوباره آموزشِ خواندن مقاله، طراحی آماری، معماری سامانه، نوشتن مقاله یا استقرار محصول باشد. این مفاهیم را از فصل‌های مجاور برمی‌داریم و به‌صورت ورودی، سند یا گیت قابل‌بررسی کنار هم قرار می‌دهیم. ارزش این فصل در زنجیرهٔ تحویل است: هر ادعا باید به داده، کد، وزن، سنجه، محدودیت و تصمیم انتشار متصل شود.

در پروژهٔ نمونه یک رگرسیون لجستیکِ دوویژگی را از صفر روی چند ردیف ساختگی آموزش می‌دهیم. اندازهٔ کوچک آن عمدی است: آزمون سریع، قابل‌تکرار و بی‌نیاز از GPU یا شبکه می‌ماند، درحالی‌که اجزای یک تحویل واقعی را نشان می‌دهد. نتیجه دربارهٔ عملکرد هوش مصنوعی در جهان واقعی نیست.

## ۲. مرز با فصل‌های ۷۰ تا ۷۲

فصل ۷۰ ادعا را به شاهد و artifact پیوند می‌دهد؛ اینجا همین انضباط را در بستهٔ خودمان به‌کار می‌بریم، نه اینکه مقالهٔ بیرونی را دوباره بازسازی کنیم. فصل ۷۱ طراحی آزمایش، split، معیار و استنباط را توضیح می‌دهد؛ اینجا پیکربندی محدود را پیشاپیش ثبت می‌کنیم و از چهار نمونهٔ test نتیجهٔ آماری نمی‌گیریم. فصل ۷۲ معماری پژوهش، مقاله، مشارکت و نقشهٔ راه را می‌سازد؛ اینجا یک پروژهٔ مستقل را تحویل‌پذیر می‌کنیم، نه اینکه آن packet را دوباره طراحی کنیم.

از جلدهای پیشین نیز خروجی مناسب را مصرف می‌کنیم: حکمرانی و مستندسازی از فصل ۶۵، CI/CD از فصل ۶۹، و امنیت و عملیات از فصل ۶۸. ارجاع به یک گیت به‌معنای اجرای دوبارهٔ همهٔ درس‌ها یا تأیید محصول نیست.

## ۳. قرارداد تحویل نهایی

| جزء | پرسش بازبینی | شاهد پروژه |
|---|---|---|
| دامنه و هدف | برای چه کسی و چه کاری ساخته شده است؟ | شرح فصل و `run_card.json` |
| داده و منشأ | ردیف‌ها از کجا آمده‌اند و چه چیزهایی نیستند؟ | `synthetic_fixture.json` و `data_card.md` |
| کد و محیط | آیا اجرا و وابستگی‌ها روشن‌اند؟ | `capstone.py` و `environment.json` |
| مدل | چه چیزی آموزش دیده و با چه ورودی‌ای؟ | `checkpoint.json` |
| ارزیابی | چه split و مخرجی واقعاً سنجیده شد؟ | `results.json` |
| مستندسازی مدل | استفادهٔ مناسب و محدودیت چیست؟ | `model_card.md` |
| انتشار | چه چیزی منتشر می‌شود و چه چیزی مسدود است؟ | `release_decision.json` و `release_manifest.json` |

بسته زمانی قابل‌قبول است که اجزای لازم موجود، به هم ارجاع‌پذیر و آزموده باشند؛ قبول‌شدن ساختار با ارزش علمی، ایمنی یا آمادگی تولید برابر نیست.

## ۴. از brief تا ادعای محدود

در brief یک جمله برای هدف، یک جمله برای کاربر فرضی، و یک جمله برای کاربرد خارج از دامنه بنویسید. مثال این فصل فقط می‌گوید: «یک طبقه‌بند خطی می‌تواند برچسب‌های ساختگیِ تعریف‌شده با قاعدهٔ `x1 + x2 > 0` را روی همین fixture بازتولید کند.» واژه‌هایی مانند «بهتر»، «هوشمند»، «منصف» یا «آمادهٔ استفاده» به‌خودی‌خود هدف آزمون‌پذیر نیستند.

اگر پروژهٔ واقعی شما هدفی مانند کمک به تصمیم استخدام، تشخیص بیماری یا رتبه‌بندی مشتری دارد، از این fixture آموزشی برای استنتاج دربارهٔ آن استفاده نکنید. پیش از آموزش، مسئله و مسیر اثر بر افراد را با ذی‌نفعان، مالک داده و مسئول حقوقی یا ایمنیِ مربوط بازبینی کنید؛ گاهی نتیجهٔ درستِ گیت «ساخته نشود» است.

## ۵. واحد تحویل و مرز سامانه

بستهٔ این فصل شامل یک اسکریپت آموزش/ارزیابی، یک fixture نسخه‌دار، یک نقطهٔ وارسی کوچک، دو کارت مستندات، سه فایل خروجی و آزمون‌های واحد است. سرویس وب، API، صف، telemetry، رابط کاربر یا deployment ندارد. این مرز مهم است: مرور یک checkpoint محلی، ارزیابی رفتار محصولی یا زیرساخت را پوشش نمی‌دهد.

در پروژهٔ بزرگ‌تر مرز را از ورودی خام تا اثر تصمیم دنبال کنید: پیش‌پردازش، مدل پایه، post-processing، رابط کاربر، مسیر بازبینی انسانی و مصرف‌کنندهٔ نتیجه ممکن است همگی بخشی از سامانه باشند. مدل‌کارتِ وزن‌ها جای مستنداتِ سامانهٔ کامل را نمی‌گیرد.

## ۶. خروجی‌های قابل‌قبول را از ابتدا تعیین کنید

قبل از اجرا فهرست تحویل و معیار پذیرش را ثبت کنید. این پروژه قبول می‌شود اگر fixture با manifest منطبق باشد؛ splitها ردیف مشترک نداشته باشند؛ مدل فقط از train وزن بگیرد؛ اجرای دوم checkpoint و نتیجهٔ یکسان بسازد؛ مخرج هر سنجه معلوم باشد؛ فایل محیط وابستگی‌ها و محدودیت را ثبت کند؛ و تصمیم انتشار deployment را صریحاً تأیید نکند.

قبول نمی‌شود اگر خروجی test برای انتخاب ابرپارامتر مصرف شده باشد، دادهٔ ورودی بی‌منشأ باشد، کارت مدل سنجه را بدون شمارش گزارش کند، hashها کهنه باشند، یا README از دقت مصنوعی ادعای کیفیت واقعی بسازد. همهٔ این‌ها را می‌توان پیش از دیدن عدد نهایی به آزمون تبدیل کرد.

## ۷. داده‌کارت، بخشی از قرارداد پروژه

داده‌کارت می‌گوید مجموعه برای چه هدفی ساخته شده، چه فیلدهایی دارد، منشأ و تبدیل آن چیست، splitها چگونه تعریف شده‌اند، چه استفاده‌ای مناسب یا نامناسب است و مجوز یا نگه‌داری چه وضعی دارد. چارچوب‌های مستندسازی داده پرسش‌های سازنده و مصرف‌کننده را کنار هم می‌آورند [۱]. قالب مشخص ممکن است بین سازمان‌ها فرق کند؛ الزام اصلی این است که خواننده بتواند بفهمد چه چیزی را دریافت کرده و چه چیزی از آن نباید نتیجه بگیرد.

در fixture ما منشأ روشن است: مقدارها دستی و ساختگی‌اند؛ دو ویژگی عددی و یک برچسب دارند؛ برچسب از قاعدهٔ اعلام‌شده می‌آید؛ دادهٔ شخصی یا بیرونی ندارند. این گزاره‌ها در `data_card.md` و metadata خود fixture ثبت شده‌اند تا تنها در prose پراکنده نمانند.

## ۸. منشأ را از fingerprint جدا کنید

منشأ می‌گوید داده چگونه و از کجا تولید شده، چه مجوز یا رضایتی لازم دارد و چه تبدیل‌هایی روی آن انجام شده است. fingerprint مانند SHA-256 فقط به شما می‌گوید bytes امروز با bytes ثبت‌شده برابر است یا نه. digest نمی‌گوید فایل معتبر، مجاز، نماینده، بی‌سوگیری یا درست است؛ اگر فایل از آغاز نادرست باشد، hash آن هم صرفاً به‌طور دقیق همان نادرستی را fingerprint می‌کند.

برای fixture این پروژه، `fixture_manifest.json` digest و شمار ردیف‌ها را ثبت می‌کند و کارت داده توضیح انسانیِ منشأ را می‌دهد. برای دادهٔ واقعی باید علاوه بر hash، منبع، نسخه، مالکیت، اجازهٔ استفاده، گردآوری، پاک‌سازی، حذف، دادهٔ تهی و محدودیت دسترسی را مستند کنید.

## ۹. دادهٔ ساختگی هم نیازمند توصیف است

در این مثال، «ساختگی» یعنی مقدارها از یک قاعدهٔ آموزشی و با دست ساخته شده‌اند، نه اینکه دادهٔ واقعی را ناشناس‌سازی کرده باشیم. این تفاوت را بنویسید؛ برچسب synthetic به‌تنهایی منشأ یا خطر را روشن نمی‌کند. دادهٔ مصنوعیِ تولیدشده از رکوردهای واقعی ممکن است الگو یا اطلاعات حساس را نگه دارد و به ارزیابی جداگانه نیاز دارد.

Fixture ما ۱۶ ردیف دارد: ۸ train، ۴ validation و ۴ test. تعداد کم آن برای فهم اجرای کد کافی است، نه برای تخمین عملکرد. هیچ شخص، زبان، حوزه، گروه آسیب‌پذیر یا محیط طبیعی را مدل نمی‌کند.

## ۱۰. split را به مدل متصل نگه دارید

شناسه‌های ردیف باید یکتا باشند و هدف ارزیابی پیش از آموزش معلوم باشد. اگر یک فرد، سند، گفت‌وگو یا نسخهٔ نزدیک از یک نمونه در دو split دیده شود، نشت می‌تواند نتیجه را خوش‌بینانه کند. در پروژهٔ حاضر هر ردیف شناسهٔ ساختگی دارد؛ checker هم یکتایی را می‌سنجد و هم قاعدهٔ برچسب را.

جزئیات نمونه‌گیری، واحد مستقل، طرح جفت‌شده، توان و تحلیل را از فصل ۷۱ بگیرید؛ اینجا بازتدریس نمی‌شوند. قاعدهٔ سادهٔ پروژه فقط می‌گوید `train` برای به‌روزرسانی وزن‌هاست، `validation` و `test` پس از fit گزارش می‌شوند و هیچ‌کدام برای انتخاب پارامتر مصرف نمی‌شوند.

## ۱۱. run card را پیش از اجرا ثابت کنید

`run_card.json` پیکربندی، split مجاز، معیارها، baseline، آستانهٔ تصمیم و مرز تفسیر را ثبت می‌کند. برای نمونه، ۲۰۰ دور گرادیان‌کاهشی دسته‌ای، نرخ یادگیری ۰٫۵، مقداردهی اولیهٔ صفر و آستانهٔ ۰٫۵ از ابتدا ثابت شده‌اند. اجرای قطعی و بدون seed تصادفی، تغییر fixture یا انتخاب نتیجه پس از مشاهده را پنهان نمی‌کند.

اگر پس از دیدن test عددهای پیکربندی را تغییر دهید، همان test دیگر مجموعهٔ نگه‌داشته‌شدهٔ بی‌طرف برای تصمیم تازه نیست. تغییر را با نسخهٔ تازهٔ طرح و داده ثبت کنید؛ اگر پرسش تازه است، split تازه‌ای که قبلاً برای تنظیم مصرف نشده لازم است.

## ۱۲. انتخاب مدل به اندازهٔ مسئله

مدل نمونه رگرسیون لجستیک دودویی با دو وزن و یک بایاس است؛ احتمال کلاس یک از `sigmoid(w1*x1 + w2*x2 + b)` به‌دست می‌آید. این مدل به‌دلیل کوچکی و قابلیت ممیزی انتخاب شده، نه به‌علت برتری پژوهشی. هیچ مدل pretrained، شبکهٔ بزرگ یا سرویس بیرونی در کار نیست.

در کاربرد واقعی معماری باید از محدودیت داده، latency، خطر، حریم خصوصی، قابلیت نگه‌داری و گزینهٔ ساده‌تر پیروی کند. «بزرگ‌تر» یا «جدیدتر» خود معیار موفقیت نیست؛ این فصل هم ادعای بهترین معماری یا سهم نوآورانه مطرح نمی‌کند.

## ۱۳. آموزش را به split مجاز محدود کنید

کد در هر epoch فقط gradient ردیف‌های `train` را میانگین می‌گیرد و وزن‌ها و بایاس را با همان مقدار ثابت به‌روز می‌کند. هیچ متغیر validation یا test به تابع `train_model` داده نمی‌شود. این مرزبندی در نام تابع و آزمون‌ها هم روشن است؛ صرفاً توضیح README نیست.

وقتی مدل واقعی‌تر می‌شود، باید پیش‌پردازش آموخته‌شده، انتخاب checkpoint، توقف زودهنگام، تصادفی‌سازی، seed، batch، optimizer و hardware را نیز ثبت کنید. هر تصمیمی که از validation استفاده می‌کند بخشی از فرایند انتخاب مدل است؛ آن را در گزارش پنهان نکنید.

## ۱۴. خط پایه و سنجهٔ مستقیم

روی همین fixture خط پایه، برچسب پرتکرار train را برای همهٔ test پیش‌بینی می‌کند؛ در صورت تساوی، کلاس صفر انتخاب می‌شود. گزارش دقت مدل را کنار خط پایه می‌آورد و confusion matrix، شمار درست، تعداد و cross-entropy را برای هر split نگه می‌دارد. این انتخاب فقط به خواننده کمک می‌کند مثال محاسباتی را دنبال کند.

برای مسئلهٔ واقعی معیار را از هزینهٔ خطا و کاربرد هدف استخراج کنید؛ accuracy ممکن است برای دادهٔ نامتوازن یا خطای نامتقارن گمراه‌کننده باشد. فصل ۷۱ دربارهٔ انتخاب معیار و تحلیل است؛ خروجی ۴/۴ این fixture توجیهی برای انتخاب معیار در محصول نیست.

## ۱۵. مخرج را کنار عدد بخوانید

دقت test در این اجرای ثبت‌شده ۴ از ۴ است و خط پایه ۲ از ۴. مخرج چهار، معنای عدد را محدود می‌کند؛ نوشتن «۱۰۰٪» بدون شمارش، دامنه را بزرگ‌تر از آنچه آزموده شده نشان می‌دهد. `results.json` برای هر split شمار درست، کل ردیف، دقت، cross-entropy و ماتریس خطا را کنار هم ذخیره می‌کند.

سنجه‌های train و validation هم به‌صورت توصیفی ثبت شده‌اند؛ این سه عدد فاصلهٔ تعمیم را تخمین نمی‌زنند. در fixture ما همهٔ برچسب‌ها از رابطهٔ مستقیم همان دو ویژگی ساخته شده‌اند، پس هم‌خوانی مدل و برچسب تا حد زیادی پیامد ساخت مثال است.

## ۱۶. چه چیزی از ارزیابی نتیجه نمی‌شود

این اجرا آزمون فرضیه، بازهٔ اطمینان، ارزیابی بیرونی، بررسی subgroup، آزمون robustness، مطالعهٔ انسانی یا مقایسهٔ علمی نیست. `statistical_inference_authorized` عمداً false ثبت شده است. یک test کوچک را با تکرار تصادفی یا بازچینی گزارش، به شاهد مستقل تبدیل نکنید.

برای هر ادعای محصولی باید جمعیت و محیط مربوط، خطاهای پرهزینه، شرایط عملیاتی، مقایسه‌گر و روش جمع‌آوری داده معلوم باشد. اگر این اطلاعات ندارید، وضعیت را «ارزیابی‌نشده» بنویسید؛ عدد مصنوعی جای دادهٔ واقعی را نمی‌گیرد.

## ۱۷. خطاها را قابل‌ردیابی کنید

چهار نمونهٔ test در این مثال همه درست پیش‌بینی می‌شوند؛ چون همان قواعد ساده برای تولید داده و ارزیابی استفاده شده‌اند، این موفقیت از پیش برای نشان‌دادن مسیر محاسبه مناسب است. اگر یک نمونه غلط بود، شناسه، ویژگی، برچسب، score و نسخهٔ کد را گزارش می‌کردیم؛ داده را بی‌صدا حذف یا برچسب را پس از دیدن خروجی اصلاح نمی‌کردیم.

در کاربرد واقعی، خطا را به مسیر علّیِ محتمل نسبت ندهید مگر اینکه شواهد داشته باشید. دسته‌بندی خطا، بازبینی کیفی و سنجه‌های زیرگروهی نیازمند طرح و دسترسی مجازند؛ هر کدام را پیش از جمع‌آوری داده و انتشار در نقشهٔ ارزیابی ثبت کنید.

## ۱۸. checkpoint یک artifact است، نه نتیجهٔ کامل

`checkpoint.json` وزن‌ها، بایاس، ویژگی‌ها، آستانه، الگوریتم و پارامترهای آموزش را ثبت می‌کند. همچنین digest fixture، کد و run card را نگه می‌دارد تا خواننده بتواند ورودی و نسخهٔ اجرا را به هم وصل کند. فایل کوچک آن مدل مستقل همین پروژه است؛ با مدل ازپیش‌آموزش‌دیده یا وزن بیرونی اشتباه نشود.

checkpoint به‌تنهایی نمی‌گوید استفادهٔ مناسب چیست، داده از کجا آمده یا چه آسیب‌هایی ممکن است. برای همین همراه کارت داده، مدل‌کارت، نتایج، محیط و تصمیم انتشار بسته‌بندی می‌شود. انتشار وزن بدون قرارداد اجرا و محدودیت، انتقال مسئولیت به کاربر است.

## ۱۹. محیط و وابستگی‌ها را صریح ثبت کنید

`environment.json` در اجرای audit، CPython 3.13.16، وابستگی ثالث صفر، شبکهٔ صفر و GPU استفاده‌نشده را ثبت می‌کند. همچنین می‌گوید آموزش واقعاً روی fixture انجام شده و ادعای عملکرد واقعی، fairness یا آمادگی deployment وجود ندارد. اگر محیط شما فرق کند، نسخهٔ runtime را تغییر دهید؛ فایل snapshot را به‌عنوان حقیقت همیشگی کپی نکنید.

برای پروژهٔ بزرگ‌تر علاوه بر نسخهٔ زبان، lockfile یا digest image، سخت‌افزار، نسخهٔ کتابخانه، متغیرهای مؤثر، سیاست seed، فرمان کامل، وضعیت network و علت skip را ثبت کنید. نام محیط به‌تنهایی بازتولید را تضمین نمی‌کند.

## ۲۰. بازتولیدپذیری را به آزمون تبدیل کنید

اجرای تکراریِ همین کد روی همین bytes در همین محیط باید `checkpoint.json`، `results.json` و manifest یکسان تولید کند. آزمون‌های پروژه این پایداری را بررسی می‌کنند. نتیجه فقط می‌گوید این مثال محاسباتی دوباره ساخته شد؛ اجرای مستقل روی دادهٔ تازه یا بازتولید یک ادعای مقاله نیست.

`release_manifest.json` برای فایل‌های انتخاب‌شدهٔ source و output digest جداگانه ثبت می‌کند. این manifest برای کشف تغییر ناخواسته سودمند است، اما امضا، زنجیرهٔ اعتماد، مالکیت، دسترسی‌پذیری، صحت علمی یا سلامت همهٔ سامانه را اثبات نمی‌کند.

## ۲۱. آزمون‌ها، قراردادهای شکست و CI

۲۵ آزمون واحد fixture، قواعد برچسب، شناسه‌های یکتا، split، پایداری آموزش، مخرج سنجه، baseline، تصمیم منع deployment و تشخیص دست‌کاری فایل را بررسی می‌کنند. آزمون واحد یک مسیر کد را می‌سنجد؛ نه اینکه مدل را در دامنهٔ واقعی معتبر یا عادلانه اعلام کند.

در مخزن بزرگ‌تر گیت انتشار باید builder/checker کتاب، آزمون پروژه، اعتبارسنجی artifact، لینک‌ها، آزمون مرورگر و آفلاین را اجرا کند. مرحله‌های حساس را در CI بدون secret و بدون دسترسی شبکه تا جای ممکن نگه دارید؛ اگر برای یک مرحله credential لازم است، آن را جدا و با کمترین دسترسی محافظت کنید.

## ۲۲. کارت داده و مدل‌کارت جای هم نیستند

داده‌کارت ساخت و ویژگی‌های داده را توصیف می‌کند؛ مدل‌کارت الگوریتم، پیکربندی آموزش، کاربرد هدف، ارزیابی، محدودیت و احتیاط مدل را. این اسناد به هم ارجاع می‌دهند اما یکی را نمی‌توان با دیگری جایگزین کرد. مدل‌کارت در اصل برای شفاف‌کردن زمینهٔ کاربرد و مشخصات ارزیابی مدل پیشنهاد شد [۲].

در این پروژه کارت مدل می‌گوید وزن‌ها روی هشت ردیف ساختگی آموزش دیده‌اند، test چهار ردیف دارد، و استفاده از این مدل برای تصمیم دربارهٔ انسان‌ها خارج از دامنه است. کارت داده هم می‌گوید هر برچسب با چه قاعده‌ای ساخته شده است؛ ترکیب این دو، منشأ و تفسیر را روشن‌تر می‌کند.

## ۲۳. مدل‌کارت را برای مخاطب واقعی بنویسید

مخاطب باید پیش از دانلود وزن بداند مدل چه می‌کند، چه نمی‌کند، روی چه داده‌ای سنجیده شده، چه معیار و مخرجی دارد، چه محدودیت‌هایی ثبت شده و برای چه استفاده‌هایی مناسب نیست. «عملکرد خوب» را جای عدد، split و دامنه ننویسید؛ کارت، تضمین کیفیت یا مهر تأیید نیست.

اگر مدل به چند زبان، گروه سنی، محیط سخت‌افزاری یا نسخهٔ داده مربوط است، فقط زیرگروه‌های موجه و قابل‌سنجش را گزارش کنید. نبود دادهٔ مجاز برای یک گروه یعنی وضعیت «ارزیابی‌نشده»، نه اینکه اختلاف وجود ندارد. افشای محدودیت‌ها بخشی از تحویل است، نه جمله‌ای برای رفع مسئولیت.

## ۲۴. دروازهٔ خطر را در چرخه نگه دارید

چارچوب مدیریت ریسک هوش مصنوعی NIST فعالیت‌ها را در کارکردهای حکمرانی، زمینه‌یابی، سنجش و مدیریت سازمان می‌دهد؛ خود NIST آن را راهنمای داوطلبانه معرفی کرده و در صفحهٔ رسمیِ بازبینی‌شده در ۴ نوامبر ۲۰۲۶ نوشته است که نسخهٔ ۱٫۰ در حال بازنگری است [۳]. این چارچوب قانون، استاندارد محصولیِ یگانه یا گواهی ایمنی نیست.

برای پروژهٔ واقعی، با توجه به دامنه و توان تیم، خطرهای اشخاص و جامعه، امنیت، حریم خصوصی، شفافیت، پایداری و پایش را map کنید، شواهد قابل‌سنجش انتخاب کنید و مالک اقدام اصلاحی تعیین کنید. این مثال فقط وجود یک تصمیم مستند را نشان می‌دهد؛ ممیزی NIST یا ارزیابی خطرِ یک کاربرد واقعی انجام نداده است.

## ۲۵. حریم خصوصی، انصاف و ایمنی را با «ساختگی» خلاصه نکنید

fixture دستیِ این فصل رکورد شخصی ندارد؛ بنابراین نمی‌توان از آن نتیجه گرفت که کاربردی بر کاربران واقعی بی‌خطر است. در یک پروژهٔ واقعی، منشأ داده، رضایت یا مجوز، حداقل‌سازی، نگه‌داری، حذف، دسترسی، احتمال بازشناسایی، گروه‌های اثرپذیر، خطاهای نامتقارن و مسیر اعتراض را بررسی کنید.

اگر دادهٔ حساس یا اثر پرخطر وجود دارد، پیش از آموزش مسیر بررسی ethics، حقوقی، امنیت و نمایندگان ذی‌نفعان را فعال کنید. افزایش اندازهٔ test یا افزودن واژهٔ «مسئولانه» به README جای این بررسی‌ها را نمی‌گیرد.

## ۲۶. مجوز، حقوق و نگه‌داری

بستهٔ موجود در مخزن در خودش مجوز مستقل برای بازاستفاده یا توزیع downstream تعریف نمی‌کند. پیش از انتشار وزن یا دادهٔ واقعی باید مجوز کد، داده، مدل پایه، اسناد، علامت تجاری و اجزای مشتق را جداگانه بررسی کنید؛ license یک فایل، حقوق فایل دیگر را اعطا نمی‌کند.

در `release_decision.json` وضعیت مجوز مستقل «بررسی‌نشده» می‌ماند. این وضعیت مانع از آن است که کاربر از دسترسی عمومی به فایل‌ها، اجازهٔ استفادهٔ تجاری یا حقوقی را برداشت کند. مالک نگه‌داری، نشانی گزارش آسیب‌پذیری و فرایند نسخه‌برداری نیز در انتشار واقعی باید معلوم باشند.

## ۲۷. دو تصمیم متفاوت: انتشار بسته و deployment مدل

انتشار یک بستهٔ تعلیمی در مخزن با تأیید مدل برای مصرف محصولی یکی نیست. بستهٔ ما شامل code، fixture ساختگی، آزمون و مستندات است و برای آموزش مسیر بازتولید منتشر می‌شود؛ اما `release_decision.json` deployment را تأیید نمی‌کند. تفکیک این دو، از تبدیل یک آزمایش کوچک به توصیهٔ استفاده جلوگیری می‌کند.

برای هر نسخه تصمیم را با مخاطب، artifact، دامنه، مالک، تاریخ، وابستگی‌ها، وضعیت حقوق و معیار بازبینی ثبت کنید. اگر یکی از گیت‌های پرخطر هنوز پاسخ ندارد، وضعیت را «متوقف/در انتظار» بگذارید و بگویید چه کسی و چه شاهدی برای ادامه لازم است.

## ۲۸. stop/go را بر پایهٔ شواهد بنویسید

در این پروژه، go فقط برای نگه‌داشتن و اجرای آموزشیِ بستهٔ نمونه صادر شده است. no-go برای deployment، تصمیم دربارهٔ انسان‌ها، ادعای تعمیم، انصاف، ایمنی و بازتوزیع بدون بررسی حقوقی ثبت شده است. این نمونه نشان می‌دهد خروجی صحیحِ پروژه می‌تواند یک مدلِ آموزش‌دیده و در عین حال تصمیم «به کاربر ندهید» باشد.

در محصول واقعی سطح خطر، مسیر توقف، استثناها، مالک تصمیم و تاریخ بازبینی را متناسب تعیین کنید. «همهٔ تست‌ها پاس شدند» یک شرط فنی است؛ به‌تنهایی مجوز انتشار یا پذیرش ریسک نیست.

## ۲۹. بستهٔ انتشار و manifest

بسته خروجی‌های ضروری و اسناد را در کنار هم نگه می‌دارد: checkpoint، نتیجه، محیط، داده‌کارت، مدل‌کارت، تصمیم انتشار، کد، fixture و manifest. `release_manifest.json` برای فایل‌های فهرست‌شده hash دارد و خود manifest را hash نمی‌کند تا ارجاع دوری نسازد. برای ریشهٔ اعتماد قوی‌تر به امضا و نگه‌داری امن نیاز است.

در سامانهٔ بزرگ‌تر، manifest می‌تواند commit کد، نسخهٔ container، شناسهٔ artifact store، tokenizer، پیکربندی، فایل داده یا نسخهٔ دسترسی‌پذیر، و digestهای مدل پایه را نیز ثبت کند. فایل گم‌شده را با placeholder یا هش حدسی پر نکنید؛ وضعیت آن باید صریح باشد.

## ۳۰. README دستور اجرا را بی‌ابهام می‌کند

README پروژه از مسیر خود، Python لازم، dependencyهای ثالث، command، فایل ورودی و مقصد خروجی می‌گوید. هر فرمان در سطر جداگانه است و continuation یا `\` ندارد. اجرای نمونه در پوشهٔ موقت انجام می‌شود تا فایل‌های مرجع tracked بی‌صدا جایگزین نشوند؛ سپس `cmp` نتیجه و checkpoint را با snapshot مقایسه می‌کند.

README باید پیش‌نیاز شبکه یا وزن بزرگ را هم اعلام کند. اگر استفاده از token، storage خصوصی یا نصب افزونه لازم است، فرمان‌های آن را از اجرای آفلاین جدا کنید و هرگز secret را در fixture، log یا صفحهٔ کتاب وارد نکنید.

## ۳۱. پروژه را از مسیر واقعی اجرا کنید

فایل‌های آزمایشگاه در [پوشهٔ پروژهٔ نهایی](../projects/73-capstone-responsible-model/README.md) هستند. پروژه با کتابخانهٔ استاندارد Python اجرا می‌شود؛ شبکه، GPU، credential، دادهٔ واقعی و مدل پایه نمی‌خواهد. آزمون‌ها و خروجی مرجع در همان پوشه‌اند تا reader بتواند شرح فصل را به artifact واقعی وصل کند.

ابتدا آزمون‌ها را اجرا کنید، سپس CLI را به پوشهٔ موقت هدایت کنید. مقایسهٔ بایت‌به‌بایت `checkpoint.json` و `results.json` پایداری محاسبات را می‌سنجد. چون `environment.json` نسخهٔ واقعی runtime را ثبت می‌کند و manifest هش آن را نیز نگه می‌دارد، در محیط متفاوت این دو را با snapshot مقایسه نکنید؛ `--verify-only` را روی manifest همان اجرا بزنید. اگر checkpoint یا نتیجه متفاوت شد، کد، fixture، plan، نسخهٔ کتابخانه و فرمان را بررسی کنید.

## ۳۲. نتیجه را با تصمیم انتشار بخوانید

در فایل `results.json` دقت test برابر ۱٫۰ روی ۴ نمونه و baseline برابر ۰٫۵ روی همان ۴ نمونه است. ماتریس خطا و cross-entropy هم ثبت شده‌اند. این عدد در هیچ leaderboard یا معیار بیرونی مقایسه نشده و از نمونه‌ای که با قاعدهٔ ساده تولید شده به دست آمده است.

در فایل `environment.json` نسخهٔ Python، وابستگی صفر، آزمون‌ها و محدودیت‌ها آمده است. در فایل `release_manifest.json` hashهای بسته قرار دارند. هیچ‌کدام به‌تنهایی مجوز انتشار، کیفیت مدل، صحت تمام زنجیره یا تعمیم را ثابت نمی‌کنند؛ معنی هر فایل را فقط در دامنهٔ خودش تفسیر کنید.

## ۳۳. چرا deployment این مدل متوقف می‌شود

test چهار ردیف دارد، دادهٔ بیرونی ندارد، مسئلهٔ واقعی را نمایندگی نمی‌کند، subgroup یا خطای پرهزینه را نمی‌سنجد و مسیر عملیاتی ندارد. حقوق بازاستفاده هم مستقل بررسی نشده است. بنابراین حتی با نتیجهٔ محاسباتی درست، تصمیم حرفه‌ای deployment برابر «تأیید نشده» است.

این تصمیم شکست پروژه نیست. پروژه به هدف آموزشی خود رسیده: مدل را آموزش داده، خروجی‌ها را قابل‌ردیابی کرده، محدودیت را مستند و مرز انتشار را حفظ کرده است. پروژهٔ کاربردی برای ادامه نیازمند تعریف جمعیت و پیامد، دادهٔ مجاز، ارزیابی متناسب، آزمون خطر، مالک عملیات و بازبینی انسانی است.

## ۳۴. بازتولید مستقل با اجرای دوباره یکی نیست

اجرای دوبارهٔ command توسط نویسنده یا خواننده، پایداری همان input و code را می‌سنجد. اگر artifact دیگری برای همان ادعا بسازید، طراحی تازه، منشأ و معیار باید گزارش شود؛ اگر دادهٔ تازه یا محیط تازه دارید، دامنهٔ ادعا هم عوض می‌شود. این واژگان را با فصل ۷۰ هماهنگ کنید و برای این پروژه ادعای بازتولید پژوهش بیرونی ننویسید.

برای بازبینی مستقل، از بازبین بخواهید commit، digestها، فرمان، Python و محدودیت شبکه را ثبت کند؛ سپس خروجی را با معیار ازپیش‌اعلام‌شده مقایسه کند. بازبین باید بتواند بگوید چه چیزی اجرا نشد و کدام نتیجه هنوز باز است.

## ۳۵. تیم، مشارکت و تحویل مالکیت

در تیم واقعی مسئول داده، مالک آموزش، بازبین ارزیابی، مسئول حقوق/ایمنی و نگه‌دارندهٔ انتشار را مشخص کنید. نقش‌ها می‌توانند هم‌پوشان باشند، اما تصمیم حساس باید صاحب پاسخ‌گو و مسیر escalation داشته باشد. فصل ۷۲ دربارهٔ همکاری و نقش‌های مشارکت است؛ اینجا فقط می‌خواهیم در artifact نهایی هیچ مسئولیتی میان «تیم» گم نشود.

برای handoff، README، issueهای باز، تاریخ بازبینی، محدودیت‌های شناخته‌شده، مالک artifact و روش بازگشت نسخه را تحویل دهید. مشارکت در کد یا داده به‌تنهایی دربارهٔ نویسندگی، اعتبار علمی یا اختیار deployment حکم نمی‌دهد.

## ۳۶. گیت پذیرش پروژهٔ نهایی

ارزیابی نهایی را بر completeness و مرزبندی بسنجید: آیا هدف و out-of-scope روشن‌اند؟ آیا داده و مجوز منشأ دارند؟ آیا train/validation/test جدا و ثبت شده‌اند؟ آیا checkpoint به code و fixture متصل است؟ آیا سنجه مخرج و baseline دارد؟ آیا مدل‌کارت از ادعا فراتر نمی‌رود؟ آیا گیت حقوق/خطر تصمیم deployment را ثبت می‌کند؟ آیا اجرای clean در CI و گزارش محیط موجود است؟

یک rubric ساده می‌تواند برای هر مورد «پاس»، «نیازمند اصلاح» یا «ارزیابی‌نشده» بگذارد. «ارزیابی‌نشده» را به «پاس» تبدیل نکنید تا جدول سبزتر به نظر برسد؛ هر مورد مسدود باید مالک، علت و شرطِ بازگشایی داشته باشد.

## ۳۷. نمونهٔ معیار قبولی و توقف

| مورد | نمونهٔ قبولی | نمونهٔ توقف |
|---|---|---|
| منشأ | fixture و manifest منطبق‌اند | دادهٔ بی‌منشأ یا hash منقضی |
| آموزش | فقط train در update وزن مصرف شد | test در تنظیم مدل به‌کار رفت |
| ارزیابی | شمار و سنجه در `results.json` هستند | دقت بی‌مخرج یا ادعای تعمیم |
| مستندات | کاربرد و بیرون‌ازدامنه روشن‌اند | کارت فقط تبلیغ قابلیت است |
| حقوق و خطر | وضعیت و مالک بازبینی ثبت‌اند | «عمومی است» به‌جای بررسی مجوز |
| انتشار | تصمیم آموزشی از deployment جداست | بستهٔ نمونه به‌عنوان محصول معرفی شده |

این جدول معیار پژوهشی یا قانونی عام نیست؛ قرارداد تمرینیِ همین پروژه است. کاربرد واقعی نیازمند معیارهای تخصصی و ذی‌نفعان واقعی است.

## ۳۸. خطاهای رایج در تحویل capstone

۱. دقت مصنوعی را به‌عنوان نتیجهٔ بیرونی نقل می‌کنند. ۲. manifest را به‌جای داده‌کارت می‌گذارند. ۳. checkpoint را بدون نسخهٔ پیش‌پردازش تحویل می‌دهند. ۴. مجموعهٔ test را چندبار نگاه می‌کنند و همچنان «دست‌نخورده» می‌نامند. ۵. کارت مدل را از روی template پر می‌کنند اما نتیجه و محدودیت را به‌روز نمی‌کنند. ۶. «تست‌ها سبز شدند» را با تأیید ایمنی یکی می‌گیرند. ۷. وضعیت مجوز را خالی می‌گذارند و عمومی‌بودن repository را مجوز تلقی می‌کنند.

راه‌حل این نیست که فرم‌های بیشتری به‌صورت صوری اضافه کنیم. برای هر artifact بنویسید چه تصمیمی را پشتیبانی می‌کند، چه چیزی را نمی‌گوید و چه کسی باید آن را بازبینی کند.

## ۳۹. چک‌لیست handoff

- مسئله، مخاطب، کاربرد مجاز و بیرون‌ازدامنه نوشته شده‌اند.
- fixture یا منبع داده و مجوز آن قابل‌پیگیری است.
- split، plan، baseline، معیار، مخرج و محدودیت پیش از گزارش روشن‌اند.
- code، checkpoint، environment و result به نسخه و digest مرتبط‌اند.
- داده‌کارت و مدل‌کارت همراه artifact هستند و با خروجی هماهنگ‌اند.
- خطر، حریم خصوصی، امنیت، انصاف و حقوق متناسب با دامنه بازبینی شده‌اند یا «ارزیابی‌نشده» مانده‌اند.
- تصمیم انتشار، deployment، پایش، مالکیت و تاریخ بازبینی جداگانه ثبت شده‌اند.
- فرمان clean، آزمون‌ها، CI و محدودیت‌های اجرا در README آمده‌اند.

برای مثال همین فصل، هر بند را با artifact واقعی بررسی کنید؛ صرفاً چون این چک‌لیست در یک فایل است، همهٔ گیت‌ها پاس نمی‌شوند.

## ۴۰. جمع‌بندی و پایان مسیر پنج‌جلدی

در این جلد ارزیابی، حکمرانی، محصول، عملیات و پژوهش را جداگانه آموختیم؛ capstone آن‌ها را در یک زنجیرهٔ قابل‌ردیابی جمع می‌کند. خروجی نهایی نه بزرگ‌ترین مدل، بلکه پروژه‌ای است که معلوم می‌کند چه داده‌ای وارد شد، چه کدی اجرا شد، چه چیزی اندازه‌گیری شد، چه محدودیتی باقی ماند و چرا انتشار یا deployment اجازه دارد یا ندارد.

از همین نقطه می‌توان پروژهٔ تازه‌ای طراحی کرد؛ اما پیش از جایگزینی fixture با دادهٔ واقعی، باید مرز و مالکیت را دوباره تعریف کرد. محصول جلد پنجم وب/PWA و Markdown است؛ PDF و EPUB تولید و آزموده نشده‌اند.

پاسخ‌های تشریحی در [پاسخ‌نامهٔ مستقل فصل ۷۳](../answers/73-capstone-responsible-model-fa.md)، پروژهٔ فصل ۷۳ در [آزمایشگاه فصل ۷۳](../projects/73-capstone-responsible-model/README.md)، و جزئیات بررسی در [گزارش ممیزی فصل ۷۳](73-audit-report-fa.md) آمده‌اند.

## ۴۱. منابع و تاریخ بازبینی

منابع مستندات داده و مدل و چارچوب خطر در ۴ نوامبر ۲۰۲۶ بازبینی شدند. NIST در صفحهٔ رسمی می‌گوید چارچوب نسخهٔ ۱٫۰ داوطلبانه است و در حال بازنگری قرار دارد؛ این فصل از آن به‌عنوان زبان مشترک برای گیت‌های خطر استفاده می‌کند، نه گواهی انطباق.

۱. Gebru, T. et al. (2021).
*Datasheets for Datasets.*
*Communications of the ACM, 64*(12), 86–92. [DOI: 10.1145/3458723](https://doi.org/10.1145/3458723).

۲. Mitchell, M. et al. (2019).
*Model Cards for Model Reporting.*
Proceedings of the ACM Conference on Fairness, Accountability, and Transparency, pp. 220–229. [DOI: 10.1145/3287560.3287596](https://doi.org/10.1145/3287560.3287596). [نسخهٔ نویسندگان در arXiv](https://arxiv.org/abs/1810.03993).

۳. National Institute of Standards and Technology (2023).
*Artificial Intelligence Risk Management Framework (AI RMF 1.0).* NIST AI 100-1. [DOI: 10.6028/NIST.AI.100-1](https://doi.org/10.6028/NIST.AI.100-1). [صفحهٔ رسمی چارچوب](https://www.nist.gov/itl/ai-risk-management-framework)، بازبینی‌شده در ۴ نوامبر ۲۰۲۶.

## ۴۲. تمرین‌ها

۱. برای یک مدل واقعی که می‌شناسید، یک جملهٔ هدف، یک کاربرد مجاز و دو کاربرد بیرون از دامنه بنویسید؛ مشخص کنید کدام‌یک هنوز به تأیید ذی‌نفع نیاز دارد.
۲. در fixture این فصل، قاعدهٔ برچسب، منشأ، اندازهٔ هر split و محدودیت تعمیم را در چهار گزارهٔ جداگانه خلاصه کنید.
۳. توضیح دهید چرا برابر بودن SHA-256 fixture با manifest، مجوز استفاده یا اعتبار علمی داده را اثبات نمی‌کند.
۴. دقت ۴ از ۴ مدل و ۲ از ۴ خط پایه را تفسیر کنید و دو دلیل بنویسید که چرا این اختلاف شاهد کیفیت در کاربرد واقعی نیست.
۵. اگر checkpoint با نتیجه سازگار باشد ولی مجوز دادهٔ پایه نامعلوم بماند، چه چیزی را می‌توان منتشر کرد و کدام تصمیم باید متوقف بماند؟
۶. برای یک checkpoint قابل‌بازتولید، چهار فیلد لازم را از میان شناسهٔ مدل، digest داده، پیکربندی آموزش، برچسب تبلیغاتی، نسخهٔ کد و رنگ نمودار انتخاب و دلیل بیاورید.
۷. یک پروژهٔ حساس را نام ببرید و برای پیش از deployment، یک خطر، یک ارزیابی لازم، یک مالک پاسخ‌گو و یک شرط توقف پیشنهاد کنید.
۸. با شواهد همین فصل یک تصمیم انتشارِ دوگانه بنویسید: آیا بستهٔ آموزشی قابل‌انتشار است و آیا مدل برای تصمیم‌گیری دربارهٔ انسان‌ها تأیید شده است؟


## ۴۳. پیوست اجرایی

کد زیر همان `capstone.py` آزموده‌شدهٔ پروژه است؛ نسخهٔ همراه آن در مخزن نگه‌داری می‌شود تا پیوند متن، اجرا و آزمون قابل‌بررسی بماند.

```python
"""Train and package a tiny deterministic logistic model on a synthetic fixture."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from pathlib import Path
from typing import Any

PROJECT_ID = "v5-ch12-capstone-responsible-model-synthetic-v1"
ROOT = Path(__file__).resolve().parent
FIXTURE_NAME = "synthetic_fixture.json"
MANIFEST_NAME = "fixture_manifest.json"
PLAN_NAME = "run_card.json"
STATIC_FILES = (
    "README.md",
    "capstone.py",
    FIXTURE_NAME,
    MANIFEST_NAME,
    PLAN_NAME,
    "data_card.md",
    "model_card.md",
    "release_decision.json",
    "requirements.txt",
    "test_capstone.py",
)
OUTPUT_FILES = ("checkpoint.json", "results.json", "environment.json")


class CapstoneError(ValueError):
    """Raised when an input packet violates the declared project contract."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CapstoneError(f"expected a JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def validate_fixture(fixture: dict[str, Any]) -> None:
    if fixture.get("schema_version") != 1:
        raise CapstoneError("unsupported fixture schema_version")
    if fixture.get("project_id") != PROJECT_ID or fixture.get("synthetic") is not True:
        raise CapstoneError("fixture identity or synthetic declaration mismatch")
    provenance = fixture.get("provenance")
    if not isinstance(provenance, dict):
        raise CapstoneError("fixture provenance is missing")
    if provenance.get("real_records") is not False or provenance.get("personal_data") is not False:
        raise CapstoneError("this teaching run accepts only the declared non-personal fixture")
    if provenance.get("real_model_outputs") is not False or provenance.get("external_source") is not None:
        raise CapstoneError("fixture must not claim external data or model outputs")
    if fixture.get("features") != ["x1", "x2"] or fixture.get("target") != "toy_label":
        raise CapstoneError("unexpected feature or target schema")

    splits = fixture.get("splits")
    if not isinstance(splits, dict) or set(splits) != {"train", "validation", "test"}:
        raise CapstoneError("fixture must define exactly train, validation, and test splits")
    expected_sizes = {"train": 8, "validation": 4, "test": 4}
    all_ids: set[str] = set()
    for split_name, expected_size in expected_sizes.items():
        rows = splits[split_name]
        if not isinstance(rows, list) or len(rows) != expected_size:
            raise CapstoneError(f"{split_name} must contain exactly {expected_size} rows")
        split_labels: set[int] = set()
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"id", "x1", "x2", "toy_label"}:
                raise CapstoneError(f"invalid row schema in {split_name}")
            row_id = row["id"]
            if not isinstance(row_id, str) or not row_id or row_id in all_ids:
                raise CapstoneError("row ids must be non-empty and unique across splits")
            all_ids.add(row_id)
            for feature in ("x1", "x2"):
                value = row[feature]
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                    raise CapstoneError(f"{feature} must be a finite number")
            label = row["toy_label"]
            if isinstance(label, bool) or label not in (0, 1):
                raise CapstoneError("toy_label must be the integer 0 or 1")
            expected_label = int(row["x1"] + row["x2"] > 0)
            if label != expected_label:
                raise CapstoneError(f"label rule mismatch for {row_id}")
            split_labels.add(label)
        if split_labels != {0, 1}:
            raise CapstoneError(f"{split_name} must contain both toy labels")


def load_fixture(fixture_path: Path, manifest_path: Path | None = None) -> tuple[dict[str, Any], str]:
    fixture_bytes = fixture_path.read_bytes()
    fixture_hash = sha256_bytes(fixture_bytes)
    manifest_path = manifest_path or fixture_path.with_name(MANIFEST_NAME)
    manifest = read_json(manifest_path)
    if manifest.get("project_id") != PROJECT_ID or manifest.get("synthetic") is not True:
        raise CapstoneError("fixture manifest identity mismatch")
    if manifest.get("fixture_sha256") != fixture_hash:
        raise CapstoneError("fixture SHA-256 does not match fixture_manifest.json")
    fixture = json.loads(fixture_bytes.decode("utf-8"))
    if not isinstance(fixture, dict):
        raise CapstoneError("fixture must be a JSON object")
    validate_fixture(fixture)
    return fixture, fixture_hash


def load_plan(project_root: Path) -> dict[str, Any]:
    plan = read_json(project_root / PLAN_NAME)
    if plan.get("project_id") != PROJECT_ID:
        raise CapstoneError("run card project_id mismatch")
    config = plan.get("configuration")
    expected = {
        "epochs": 200,
        "learning_rate": 0.5,
        "l2": 0.0,
        "decision_threshold": 0.5,
        "tie_rule": "score equal to threshold predicts class 0",
        "initial_weights": [0.0, 0.0],
        "initial_bias": 0.0,
        "randomness": "none",
    }
    if config != expected:
        raise CapstoneError("run card configuration differs from the tested reference plan")
    if plan.get("training_split") != "train only":
        raise CapstoneError("training must use only the declared train split")
    if plan.get("validation_split") != "report descriptive metrics after fitting; do not update weights":
        raise CapstoneError("validation split contract mismatch")
    if plan.get("test_split") != "report descriptive metrics once after fitting; do not select parameters":
        raise CapstoneError("test split contract mismatch")
    return plan


def sigmoid(value: float) -> float:
    if value >= 0:
        exponent = math.exp(-min(value, 700.0))
        return 1.0 / (1.0 + exponent)
    exponent = math.exp(max(value, -700.0))
    return exponent / (1.0 + exponent)


def train_model(rows: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    if not rows:
        raise CapstoneError("training split must not be empty")
    labels = {row["toy_label"] for row in rows}
    if labels != {0, 1}:
        raise CapstoneError("training split must contain both labels")
    weights = [float(value) for value in config["initial_weights"]]
    bias = float(config["initial_bias"])
    learning_rate = float(config["learning_rate"])
    regularization = float(config["l2"])
    epochs = int(config["epochs"])
    if len(weights) != 2 or epochs <= 0 or learning_rate <= 0 or regularization < 0:
        raise CapstoneError("invalid logistic-regression configuration")

    for _ in range(epochs):
        gradient_weights = [0.0, 0.0]
        gradient_bias = 0.0
        for row in rows:
            score = bias + weights[0] * row["x1"] + weights[1] * row["x2"]
            error = sigmoid(score) - row["toy_label"]
            gradient_weights[0] += error * row["x1"]
            gradient_weights[1] += error * row["x2"]
            gradient_bias += error
        scale = 1.0 / len(rows)
        weights = [
            weight - learning_rate * (gradient * scale + regularization * weight)
            for weight, gradient in zip(weights, gradient_weights)
        ]
        bias -= learning_rate * gradient_bias * scale

    return {"weights": weights, "bias": bias}


def probability(row: dict[str, Any], model: dict[str, Any]) -> float:
    score = model["bias"] + model["weights"][0] * row["x1"] + model["weights"][1] * row["x2"]
    return sigmoid(score)


def _rounded(value: float) -> float:
    return round(float(value), 12)


def evaluate_rows(
    rows: list[dict[str, Any]],
    model: dict[str, Any],
    threshold: float = 0.5,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not rows:
        raise CapstoneError("evaluation split must not be empty")
    if not 0.0 < threshold < 1.0:
        raise CapstoneError("decision threshold must be strictly between zero and one")
    confusion = {"tn": 0, "fp": 0, "fn": 0, "tp": 0}
    predictions: list[dict[str, Any]] = []
    losses: list[float] = []
    correct = 0
    for row in rows:
        score = probability(row, model)
        predicted = int(score > threshold)
        actual = row["toy_label"]
        correct += int(predicted == actual)
        if actual == 0 and predicted == 0:
            confusion["tn"] += 1
        elif actual == 0 and predicted == 1:
            confusion["fp"] += 1
        elif actual == 1 and predicted == 0:
            confusion["fn"] += 1
        else:
            confusion["tp"] += 1
        clipped = min(max(score, 1e-12), 1.0 - 1e-12)
        losses.append(-(actual * math.log(clipped) + (1 - actual) * math.log(1 - clipped)))
        predictions.append({
            "id": row["id"],
            "expected": actual,
            "predicted": predicted,
            "score": _rounded(score),
        })
    metrics = {
        "count": len(rows),
        "correct": correct,
        "accuracy": _rounded(correct / len(rows)),
        "binary_cross_entropy": _rounded(sum(losses) / len(losses)),
        "confusion_matrix": confusion,
    }
    return metrics, predictions


def evaluate_majority_baseline(
    rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if not training_rows:
        raise CapstoneError("baseline requires a non-empty training split")
    if not rows:
        raise CapstoneError("baseline evaluation split must not be empty")
    positives = sum(row["toy_label"] for row in training_rows)
    negatives = len(training_rows) - positives
    label = 1 if positives > negatives else 0
    confusion = {"tn": 0, "fp": 0, "fn": 0, "tp": 0}
    correct = 0
    for row in rows:
        actual = row["toy_label"]
        correct += int(actual == label)
        if actual == 0 and label == 0:
            confusion["tn"] += 1
        elif actual == 0 and label == 1:
            confusion["fp"] += 1
        elif actual == 1 and label == 0:
            confusion["fn"] += 1
        else:
            confusion["tp"] += 1
    return {
        "policy": "training-split majority; ties resolve to class 0",
        "label": label,
        "count": len(rows),
        "correct": correct,
        "accuracy": _rounded(correct / len(rows)),
        "confusion_matrix": confusion,
    }


def _manifest_file_map(project_root: Path, output_dir: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for name in STATIC_FILES:
        path = project_root / name
        if not path.is_file():
            raise CapstoneError(f"release source file missing: {name}")
        mapping[f"source/{name}"] = sha256_file(path)
    for name in OUTPUT_FILES:
        path = output_dir / name
        if not path.is_file():
            raise CapstoneError(f"release output file missing: {name}")
        mapping[f"output/{name}"] = sha256_file(path)
    return mapping


def verify_release(manifest_path: Path, project_root: Path, output_dir: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    if manifest.get("project_id") != PROJECT_ID:
        raise CapstoneError("release manifest project_id mismatch")
    expected = _manifest_file_map(project_root, output_dir)
    if manifest.get("files") != expected:
        raise CapstoneError("release manifest contains a missing, changed, or unexpected file hash")
    return manifest


def run_project(
    fixture_path: Path,
    output_dir: Path,
    project_root: Path = ROOT,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    fixture, fixture_hash = load_fixture(fixture_path)
    plan = load_plan(project_root)
    config = plan["configuration"]
    code_hash = sha256_file(project_root / "capstone.py")
    run_card_hash = sha256_file(project_root / PLAN_NAME)
    model_parameters = train_model(fixture["splits"]["train"], config)
    model = {
        "weights": [_rounded(value) for value in model_parameters["weights"]],
        "bias": _rounded(model_parameters["bias"]),
    }
    checkpoint = {
        "format_version": 1,
        "project_id": PROJECT_ID,
        "model_id": "v5-ch12-logistic-toy-demo-v1",
        "algorithm": "binary logistic regression; full-batch gradient descent",
        "features": fixture["features"],
        "target": fixture["target"],
        "weights": model["weights"],
        "bias": model["bias"],
        "threshold": config["decision_threshold"],
        "training_config": {
            "epochs": config["epochs"],
            "learning_rate": config["learning_rate"],
            "l2": config["l2"],
            "decision_threshold": config["decision_threshold"],
            "tie_rule": config["tie_rule"],
            "initial_weights": config["initial_weights"],
            "initial_bias": config["initial_bias"],
            "randomness": config["randomness"],
            "split_used_for_weight_updates": "train",
        },
        "fixture_sha256": fixture_hash,
        "source_code_sha256": code_hash,
        "run_card_sha256": run_card_hash,
    }
    checkpoint_path = output_dir / "checkpoint.json"
    write_json(checkpoint_path, checkpoint)
    checkpoint_hash = sha256_file(checkpoint_path)

    split_metrics: dict[str, Any] = {}
    test_predictions: list[dict[str, Any]] = []
    for split_name in ("train", "validation", "test"):
        metrics, predictions = evaluate_rows(
            fixture["splits"][split_name], model, float(config["decision_threshold"])
        )
        split_metrics[split_name] = metrics
        if split_name == "test":
            test_predictions = predictions
    baseline = evaluate_majority_baseline(fixture["splits"]["test"], fixture["splits"]["train"])
    results = {
        "project_id": PROJECT_ID,
        "model_id": checkpoint["model_id"],
        "fixture_sha256": fixture_hash,
        "source_code_sha256": code_hash,
        "run_card_sha256": run_card_hash,
        "checkpoint_sha256": checkpoint_hash,
        "synthetic_fixture_only": True,
        "real_data_used": False,
        "pretrained_model_used": False,
        "external_api_calls": 0,
        "training": {
            "split": "train",
            "row_count": len(fixture["splits"]["train"]),
            "epochs": config["epochs"],
            "learning_rate": config["learning_rate"],
            "l2": config["l2"],
            "randomness": "none",
        },
        "metrics": split_metrics,
        "majority_baseline_test": baseline,
        "test_predictions": test_predictions,
        "claims": {
            "real_world_quality_established": False,
            "generalization_established": False,
            "fairness_assessed_for_real_groups": False,
            "safety_or_security_approved": False,
            "statistical_inference_authorized": False,
            "deployment_approved": False,
        },
        "interpretation": "Descriptive execution results on one deterministic synthetic fixture only.",
    }
    results_path = output_dir / "results.json"
    write_json(results_path, results)

    environment = {
        "project_id": PROJECT_ID,
        "audit_date": "2026-11-08",
        "runtime": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "platform": sys.platform,
        },
        "dependencies": [],
        "input": {
            "fixture_sha256": fixture_hash,
            "source_code_sha256": code_hash,
            "run_card_sha256": run_card_hash,
        },
        "execution": {
            "unit_tests": "25/25 passed",
            "training_executed": True,
            "external_network_requests": 0,
            "external_api_calls": 0,
            "gpu_used": False,
            "real_data_used": False,
            "personal_data_used": False,
            "pretrained_model_used": False,
            "randomness_used": False,
            "result_reproduced_from_saved_fixture": True,
        },
        "interpretation_limits": {
            "synthetic_fixture_only": True,
            "real_world_quality_assessed": False,
            "generalization_assessed": False,
            "fairness_for_real_groups_assessed": False,
            "safety_or_security_reviewed_for_deployment": False,
            "deployment_authorized": False,
        },
    }
    environment_path = output_dir / "environment.json"
    write_json(environment_path, environment)

    release_files = _manifest_file_map(project_root, output_dir)
    release_manifest = {
        "format_version": 1,
        "project_id": PROJECT_ID,
        "decision": "educational_source_packet_only",
        "deployment_approved": False,
        "hash_algorithm": "SHA-256",
        "files": release_files,
        "self_hash_included": False,
    }
    manifest_path = output_dir / "release_manifest.json"
    write_json(manifest_path, release_manifest)
    verify_release(manifest_path, project_root, output_dir)
    return {
        "checkpoint": checkpoint,
        "results": results,
        "environment": environment,
        "release_manifest": release_manifest,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=ROOT / FIXTURE_NAME)
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.verify_only:
            verify_release(args.output_dir / "release_manifest.json", ROOT, args.output_dir)
            print("release packet hashes verified; deployment remains unapproved")
            return 0
        packet = run_project(args.fixture, args.output_dir, ROOT)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError, CapstoneError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    test = packet["results"]["metrics"]["test"]
    baseline = packet["results"]["majority_baseline_test"]
    print(
        "synthetic teaching run only: "
        f"test_accuracy={test['correct']}/{test['count']}; "
        f"majority_baseline={baseline['correct']}/{baseline['count']}; "
        "deployment_approved=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
