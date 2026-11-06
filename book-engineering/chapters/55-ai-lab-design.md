# جلد چهارم، فصل ۹ — طراحی آزمایشگاه یادگیری ماشین: از میز شخصی تا زیرساخت سازمانی

> **جایگاه در نقشه:** فصل محلی ۹ از ۱۵ فصل جلد چهارم؛ فصل سراسری ۵۵. جلد چهارم طبق نقشهٔ راه ۱۵ فصل دارد.
>
> **مرز موضوعی:** فصل ۵۴ نیاز حافظه و محاسبه را برآورد می‌کند؛ این فصل آن نیاز را به معماری و اجزای یک آزمایشگاه شخصی، حرفه‌ای یا سازمانی ترجمه می‌کند. فصل ۵۶ بودجه، خرید در برابر اجاره و هزینهٔ مالکیت را بررسی می‌کند؛ در این فصل قیمت و توصیهٔ خرید نداریم.
>
> **حد ادعا:** آزمایشگاه یعنی مجموعه‌ای از سخت‌افزار، برق، خنک‌کاری، ذخیره‌سازی، شبکه و عملیات. نمونه‌های پروژه ساختگی‌اند و هیچ SKU، نصب، اندازه‌گیری، benchmark یا تأیید ایمنی ارائه نمی‌کنند. نام «کم‌هزینه» یک ردهٔ آموزشی نسبی است، نه ادعای قیمت روز.
>
> **تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶.**

## ۱. آزمایشگاه را «یک کارت گرافیک» تعریف نکنید

اگر مدل روی GPU اجرا شود، آیا آزمایشگاه همان GPU است؟ نه. برای بار واقعی، میزبان، حافظهٔ سیستم، درایور، نرم‌افزار، فضای داده، برق ورودی، دفع گرما، اتصال شبکه، پشتیبان‌گیری و کسی که خرابی را پیگیری می‌کند نیز جزو سامانه‌اند. گلوگاه ممکن است هیچ ربطی به تعداد هسته‌های شتاب‌دهنده نداشته باشد.

این فصل یک روش برای طراحی **سامانهٔ محاسباتی قابل نگه‌داری** می‌دهد. ابتدا workload و محدودیت محل را می‌نویسیم؛ بعد شکل استقرار را برمی‌گزینیم؛ سپس سازگاری اجزا، توان، گرما، شبکه و بازیابی را روی کاغذ کنترل می‌کنیم. طراحی کاغذی نقطهٔ شروع اجرای آزمایشی است، نه گواهی اینکه سیستم واقعاً کار می‌کند.

![شکل ۴-۹-۱: سه ردهٔ آزمایشگاه شخصی تک‌گره، workstation مستقل حرفه‌ای و کلاستر سازمانی چندگره را با اجزای میزبان، ذخیره‌سازی، برق، خنک‌کاری، شبکه و عملیات مقایسه می‌کند؛ مسیر پایین شکل workload، بازبینی سندها، تأیید تأسیسات، آزمون کوچک و ثبت/بازیابی را نشان می‌دهد.](book-engineering/diagrams/v4-ch09-lab-design.svg)

شکل ۴-۹-۱ — سه ردهٔ آزمایشگاه با نیازها و مسئولیت‌های متفاوت؛ مسیر راه‌اندازی از تعریف workload تا بازیابی را نشان می‌دهد.

## ۲. خروجی فصل قبل را به الزام‌های قابل بررسی تبدیل کنید

فصل ۵۴ دفتر محاسبه می‌سازد؛ حالا هر برآورد را به نیاز یک جزء تبدیل کنید. به‌جای «یک GPU قوی می‌خواهم» این پرسش‌ها را ثبت کنید:

- **کار:** inference، fine-tuning، آموزش، preprocessing یا چند کار متفاوت؟
- **شکل کار:** حافظهٔ لازم برای هر شتاب‌دهنده چقدر است؟ چند شتاب‌دهنده در هر node و چند node لازم‌اند؟
- **زمان‌بندی:** run کوتاه و آموزشی است یا دستگاه باید شبانه‌روز در دسترس بماند؟
- **داده:** اندازهٔ دادهٔ فعال، تعداد کپی‌های کاری، checkpointها، scratch و نسخهٔ backup چقدر است؟
- **نرم‌افزار:** سیستم‌عامل، driver/runtime، framework، kernelها و روش توزیع‌شده کدام‌اند؟
- **محل:** ظرفیت تخصیص‌یافتهٔ برق و سرمایش، فضا، نویز، تهویه، دسترسی و اتصال شبکه را چه کسی تأیید می‌کند؟
- **معیار:** هدف فقط اجرای یک آزمایش کوچک است، یا تأخیر، توان عملیاتی، uptime و چندکاربره‌بودن هم الزام‌اند؟
- **ریسک:** دادهٔ حساس است؟ backup کجاست؟ چه کسی دسترسی فیزیکی و مدیریتی دارد؟ اگر SSD یا node از کار بیفتد، مسیر بازیابی چیست؟

در جدول نیازمندی‌ها، هر عدد باید **واحد، مبنا، منبع و صاحب تأیید** داشته باشد. برای مثال، «۴۸ GB حافظه» بدون مشخص‌کردن GPU، واحد GB/GiB، حافظهٔ قابل‌استفاده، بارهای دیگر و روش تقسیم مدل، نیازمندی کامل نیست. برآورد فصل ۵۴ را به‌ازای هر device/rank نگه دارید؛ حافظهٔ چند GPU فقط وقتی جمع‌پذیر است که sharding و ارتباط مدل واقعاً اجازه دهد.

## ۳. سه الگوی آزمایشگاه، نه سه رتبهٔ سرعت

«شخصی»، «حرفه‌ای مستقل» و «سازمانی» سه پروفایل نیاز و عملیات‌اند؛ تضمین کارایی یا کیفیت مدل نیستند. یک workstation حرفه‌ایِ چندGPU در اتاقی با برق یا تهویهٔ نامناسب از یک سرور کوچک تک‌گره‌ای ضعیف‌تر عمل می‌کند.

| الگو | وقتی مناسب است | شکل رایج معماری | وابستگی‌ای که زود باید سنجید |
|---|---|---|---|
| **شخصی، کم‌هزینه به معنای نسبی** | یادگیری، inference یا آزمایش کوچکِ تک‌نفره؛ استفاده از دستگاه موجود | یک میزبان، یک شتاب‌دهنده یا مسیر CPU، ذخیره‌سازی محلی، شبکهٔ عادی | حافظهٔ قابل‌استفاده، سازگاری نرم‌افزار، برق محل، گرما و نویز اتاق |
| **حرفه‌ای مستقل** | runهای تکرارپذیر، preprocessing و چند آزمایش موازی | workstation/tower تک‌گره‌ای؛ گاهی چند accelerator؛ scratch سریع و backup جدا | خطوط PCIe و فاصلهٔ کارت‌ها، RAM، پاور/کانکتور، هوای ورودی، نسخهٔ driver و ثبت آزمایش |
| **سازمانی** | تیم، صف کار، دادهٔ مشترک، چند node یا نیاز عملیاتی | nodeهای محاسبه، شبکهٔ مدیریت، fabric داده/collective، ذخیره‌سازی مشترک، scheduler و پایش | برق و سرمایش تأییدشده، مسیر/سوئیچ شبکه، کنترل دسترسی، backup/restore و نقطه‌های شکست |

برای آزمایش تک‌گره‌ای، شبکهٔ پرسرعت بین nodeها ممکن است هیچ گلوگاهی را رفع نکند؛ در آموزش چندگره‌ای، ارتباط می‌تواند به‌اندازهٔ accelerator مهم شود. به همین ترتیب، cluster کوچک بدون مالک نگه‌داری، وصله‌کردن و پایش، لزوماً از workstation ساده قابل‌اعتمادتر نیست. «کم‌هزینه» را به‌جای قیمت، با **کمینه‌کردن قابلیت‌های غیرضروری برای workload** تعریف کنید؛ قیمت‌ها و مقایسهٔ خرید/اجاره به فصل ۵۶ تعلق دارد.

## ۴. شتاب‌دهنده را با نرم‌افزار و حافظهٔ هر device انتخاب‌پذیر کنید

فضای حافظهٔ روی accelerator در بسیاری از workloadها قید اول است، اما عدد درج‌شده روی مشخصات برابر با حافظهٔ آزاد برای مدل نیست: runtime، driver، kernel، بافرها و فرایندهای دیگر هم سهم می‌گیرند. برای یک screen ساده، می‌توان سهم فرضی را چنین نوشت:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="حافظهٔ قابل‌استفادهٔ تخمینی برابر است با سهم فرضی ضرب‌در حافظهٔ دستگاه">
  <mrow><msub><mi>M</mi><mtext>usable</mtext></msub><mo>=</mo><mi>f</mi><mo>·</mo><msub><mi>M</mi><mtext>device</mtext></msub></mrow>
</math>

**متن جایگزین فرمول:** `M_usable = f × M_device`؛ سهم `f` باید از workload/runtime واقعی یا یک فرض آشکار بیاید، نه از قانون همگانی. برای نمونه، اگر سناریوی فصل ۵۴ به ۴۲ GiB برای **هر** device نیاز دارد، دو device با ۲۴ GiB را به‌عنوان «۴۸ GiB» جمع نزنید؛ صرفاً جمع ظرفیت فیزیکی، مدل را روی یک device جا نمی‌دهد و به‌خودی‌خود مدل موازی را هم راه نمی‌اندازد.

این موارد را از سند همان سامانه بررسی کنید:

- حافظهٔ هر accelerator، نوع آن، شیوهٔ تقسیم مدل، و kernelهایی که workload لازم دارد؛
- پشتیبانی واقعیِ چارچوب از معماری، دقت عددی، driver، runtime و سیستم‌عامل؛
- توان ورودی/حد توان کل **سیستم**، فرم‌فکتور، تعداد/عرض slot و محدودیت دمای کاری؛
- ارتباط درون‌گره‌ای، topology و اینکه deviceها peer-to-peer را پشتیبانی می‌کنند یا خیر؛
- نسخه‌بندی و مسیر دریافت وصلهٔ امنیتی و driver.

از روی نام یک معماری، وجود kernel یا سازگاری framework را قطعی فرض نکنید؛ ماتریس پشتیبانیِ نسخه‌دار را برای workload خود کنترل کنید. نمونهٔ سامانهٔ یکپارچهٔ NVIDIA DGX B200 نشان می‌دهد یک node سازمانی می‌تواند چند GPU، چند PSU، شبکه و ذخیره‌سازی تخصصی داشته باشد و راهنمای همان محصول قواعد ایمنی و محدودیت‌های خودش را تعریف می‌کند؛ اعداد یا کابل آن را به workstation سفارشی تعمیم ندهید [3]. این اشاره endorsement یا پیشنهاد خرید نیست.

## ۵. میزبان، RAM و مسیر فیزیکی کارت‌ها

GPU روی مادربردی نصب نمی‌شود که در خلأ قرار دارد. تعداد خط‌های PCIe، نسل و پهنای اتصال، اشتراک laneها با NVMe یا NIC، تعداد socketهای CPU و توپولوژی NUMA می‌توانند مسیر داده و ارتباط را تغییر دهند. تعداد ظاهری slotها کافی نیست: کارت بلند یا ضخیم ممکن است slot مجاور را بپوشاند یا به کابل و جریان هوا برخورد کند. سند board، chassis، CPU و accelerator را در کنار هم بخوانید و فضای سرویس‌کاری را هم لحاظ کنید.

RAM میزبان برای loader، تبدیل داده، صفحه‌بندی/offload، cache و فرایندهای کنار مدل لازم است؛ «VRAM کافی» جای آن را نمی‌گیرد. بررسی کنید که ظرفیت کل، تعداد channel، نوع پشتیبانی‌شده، امکان ارتقا و چیدمان DIMM با motherboard/CPU مطابقت داشته باشند. اگر workload از NUMA یا حافظهٔ pinned استفاده می‌کند، اندازه‌گیری همان workload و topology همان سیستم را لازم دارد؛ این فصل عدد کارایی برای آن نمی‌سازد.

## ۶. ذخیره‌سازی: دادهٔ فعال، checkpoint و backup را جدا ببینید

حجم «یک مجموعه‌داده» مساوی فضای آزاد لازم نیست. یک نسخهٔ کاری، نسخهٔ پاک‌شده، cache، checkpointهای متعدد، logها و یک کپی پشتیبان ممکن است هم‌زمان فضا بگیرند. تخمین کاغذی ساده:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="فضای برنامه‌ریزی‌شده برابر است با تعداد کپی‌های کاری ضرب‌در دادهٔ مجموعه، به‌علاوهٔ تعداد نسخه‌های checkpoint ضرب‌در اندازهٔ هر checkpoint، به‌علاوهٔ scratch و backup و log">
  <mrow><msub><mi>S</mi><mtext>plan</mtext></msub><mo>=</mo><mi>c</mi><mo>·</mo><mi>D</mi><mo>+</mo><mi>v</mi><mo>·</mo><mi>C</mi><mo>+</mo><msub><mi>S</mi><mtext>scratch</mtext></msub><mo>+</mo><msub><mi>S</mi><mtext>backup</mtext></msub><mo>+</mo><msub><mi>S</mi><mtext>logs</mtext></msub></mrow>
</math>

**متن جایگزین فرمول:** `S_plan = c×D + v×C + S_scratch + S_backup + S_logs`؛ این جمع، فشرده‌سازی، metadata، فضای رزرو و رشد آینده را خودکار حدس نمی‌زند.

سیستم‌عامل، scratch موقت، دادهٔ کاری و checkpointهای لازم برای resume را در طرح ذخیره‌سازی از هم متمایز کنید. اگر ذخیره‌سازی مشترک است، throughput، latency، شبکه، دسترسی هم‌زمان و ظرفیت واقعی بعد از RAID/metadata را از سندها و آزمون‌ها استخراج کنید. RAID یا mirror می‌تواند بخشی از دسترس‌پذیری را کمک کند، اما کپی جدا و آزمون بازگردانی را حذف نمی‌کند. برای دادهٔ قابل‌حفاظت، سیاست backup، رمزگذاری و مالک بازیابی را تعیین کنید؛ برای خارج‌کردن media از چرخه، NIST SP 800-88 Rev. 2 فرایند sanitization را بر مبنای حساسیت داده توضیح می‌دهد [6]. نام ابزار به‌تنهایی پاک‌شدن داده را تضمین نمی‌کند.

## ۷. شبکه: management، ذخیره‌سازی و collective یک کار نیستند

در یک workstation، NIC برای شبکهٔ اداری/دسترسی و شاید ذخیره‌سازی کافی است؛ در cluster، دست‌کم این مسیرها را مفهومی جدا کنید:

1. **مدیریت:** SSH یا کنسول، inventory، مانیتورینگ و مدیریت سخت‌افزار؛ فقط از شبکه و هویت مجاز.
2. **داده و ذخیره‌سازی:** انتقال corpus، checkpoint و artifact؛ ظرفیت و رقابت آن با بقیهٔ ترافیک را بسنجید.
3. **Collective بین nodeها:** تبادل گرادیان/پارامتر در DDP/FSDP و روش‌های مشابه؛ topology، NIC، switch و oversubscription اهمیت دارند.

سرعت اسمی پورت را throughput تضمین‌شده نخوانید. حد پایینِ انتقال یک فایل در لینک ایدئال فقط مرتبهٔ نظری است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="زمان حد پایین نظری بر حسب ثانیه برابر است با هشت ضرب‌در تعداد بایت فایل تقسیم بر نرخ اسمی لینک به گیگابیت در ثانیه ضرب‌در یک میلیارد">
  <mrow><msub><mi>t</mi><mtext>floor</mtext></msub><mo>=</mo><mfrac><mrow><mn>8</mn><mo>·</mo><mi>B</mi></mrow><mrow><msup><mn>10</mn><mn>9</mn></msup><mo>·</mo><mi>R</mi></mrow></mfrac><mtext> seconds</mtext></mrow>
</math>

**متن جایگزین فرمول:** `t_floor = 8×B_bytes/(10^9×R_Gbit/s)`؛ protocol overhead، اشتراک لینک، I/O ذخیره‌سازی، latency و رفتار برنامه در آن نیست.

برای مثال، NCCL مستند می‌کند که در stack خودش topology و ابزارهایی مانند `nvidia-smi topo -m` و `nvbandwidth` برای دیدن مسیر/سنجش ارتباط به کار می‌روند؛ آزمون inter-node نیز باید روی شبکهٔ واقعی انجام شود [4]. این ابزارها عمومی برای همهٔ شتاب‌دهنده‌ها نیستند. نتیجهٔ لینک در fixture یا محاسبهٔ line-rate، سنجش NCCL، latency یا کارایی آموزش نیست.

## ۸. برق: حداکثر ورودی را از توان خروجی PSU جدا کنید

نام توان GPU، TDP، ظرفیت خروجی پاور و توان AC سیستم چهار عدد یکسان نیستند. برای برآورد اولیه، جمع **توان ورودی سیستم‌ها طبق سند معتبر/طرح facility** را از بارهای دیگر جدا نگه دارید:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="توان ورودی برنامه‌ریزی‌شدهٔ سایت برابر است با جمع تعداد هر نوع سیستم ضرب‌در بیشینه توان ورودی مستند همان سیستم، به‌علاوه توان شبکه و سایر بارهای فناوری اطلاعات">
  <mrow><msub><mi>P</mi><mtext>site</mtext></msub><mo>=</mo><munderover><mo>∑</mo><mrow><mi>i</mi></mrow><mrow><mi>types</mi></mrow></munderover><msub><mi>n</mi><mi>i</mi></msub><mo>·</mo><msub><mi>P</mi><mrow><mi>i</mi><mo>,</mo><mtext>max,in</mtext></mrow></msub><mo>+</mo><msub><mi>P</mi><mtext>network</mtext></msub><mo>+</mo><msub><mi>P</mi><mtext>other IT</mtext></msub></mrow>
</math>

**متن جایگزین فرمول:** `P_site = Σ_i (n_i × P_i,max,input) + P_network + P_other_IT`؛ جمع برنامه‌ریزی با اندازه‌گیری watt-meter یکی نیست.

برای هر node علاوه بر توان سیستم، سوئیچ، ذخیره‌ساز، نمایشگر و تجهیزات جانبی را بشمارید. ظرفیت خروجی DC پاور با ورودی AC دیوار قابل‌جایگزینی نیست؛ بازده، ضریب توان، وضعیت بار، تعداد PSU، افزونگی و محدودیت دمایی در مدل دقیق اثر دارند. از «وات روی جعبهٔ GPU» برای سایزکردن کل مدار استفاده نکنید.

**این فصل ظرفیت مدار شاخه، کابل، سیم‌کشی، ارت، PDU یا UPS را سایز نمی‌کند.** تخصیص برق محل و هر تغییر در تأسیسات باید با کد محلی، مستند محصول و برق‌کار/مهندس واجد صلاحیت هماهنگ شود؛ OSHA برای محیط کار در 29 CFR 1910.333 کار روی بخش برق‌دار را به افراد qualified محدود می‌کند [7]. راهنمای سازنده نیز بر کابل و الزامات مخصوص همان دستگاه تقدم دارد [3].

## ۹. خنک‌کاری: بار گرما فقط دمای اتاق نیست

تقریبِ تبدیل توان گرمایی به واحد رایج HVAC چنین است:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="بار گرمایی معادل بر حسب بی‌تی‌یو بر ساعت تقریباً برابر است با توان ورودی بر حسب وات ضرب‌در سه ممیز چهارصد و دوازده بی‌تی‌یو بر ساعت به‌ازای هر وات">
  <mrow><msub><mi>Q</mi><mtext>heat</mtext></msub><mo>≈</mo><mn>3.412141633</mn><mtext> Btu/h per W</mtext><mo>·</mo><msub><mi>P</mi><mtext>input</mtext></msub></mrow>
</math>

**متن جایگزین فرمول:** `Q_heat [Btu/h] ≈ 3.412141633 × P_input [W]`؛ این تبدیل واحد است، نه ظرفیت پیشنهادی کولر. ضریب از رابطهٔ ژول و Btu در راهنمای SI گرفته شده است [8].

گرمای محاسباتی فقط یکی از اجزای بار فضاست. گرمای افراد و روشنایی، جریان هوای ورودی/برگشتی، بازچرخش هوای داغ، دمای بیرون، رطوبت، dust/filter، ارتفاع، راندمان HVAC، برقِ تجهیزات سرمایش و هم‌زمانی بارها نتیجه را تغییر می‌دهند. رتبهٔ cooling روی label هم الزاماً سرمایش قابل‌تحویل در محل و شرایط شما نیست.

راهنمای DOE/FEMP مدیریت مسیر هوای سرد و گرم، کابل‌کشی و سنجش در ورودی تجهیزات را از اجزای طراحی مرکز داده می‌داند؛ آن توصیه را مستقیم به اتاق خانه یا همهٔ workstationها تعمیم ندهید [1]. در راهنمای حرارتی ASHRAE TC 9.9، بازهٔ توصیه‌شده برای گروهی از تجهیزات air-cooled با حدود مجاز یکسان نیست؛ برای تجهیزات متراکم H1 نیز بازهٔ جداگانه تعریف شده است. دما را در **inlet دستگاه** و بر اساس کلاس و سند همان وسیله بررسی کنید، نه با یک عدد جهان‌شمول روی thermostat [2].

برای پروفایل ساختگی پروژه، `cooling_design_factor = 1.20` فقط فرض آموزشی است. این ضریب معیار ASHRAE، توصیهٔ مکانیکی یا ضریب طراحی برای ساختمان نیست. طراحی HVAC، آب/مایع‌خنک‌کاری و تخمین ظرفیت اتاق نیازمند اندازه‌گیری و متخصص تأسیسات است؛ دستگاه را با درِ باز، جریان هوای مسدود یا راهکار دست‌ساز مایع‌خنک‌کاری راه‌اندازی نکنید.

## ۱۰. فضا، فرم‌فکتور، کابل و نویز را روی نقشه بیاورید

پیش از نصب، شکل فیزیکی مجموعه را کنترل کنید:

- footprint، وزن، عمق، فضای سرویس، بازشدن درها، محل خروج اضطراری و دسترسی به کلید قطع؛
- جهت ورود/خروج هوا، فاصله از دیوار و منبع گرما، فیلتر و مسیر تعویض قطعه؛
- طول و نوع کابل‌های داده و برق، شعاع خم، مسیر عبور و جداسازی کابل‌ها طبق مقررات محل؛
- صدای فن و تهویه در بار واقعی، گردوغبار، لرزش و شرایط محیطی؛
- در rack، ارتفاع U، وزن بار، rail kit، grounding/bonding و محل نگه‌داری ابزار.

این‌ها را از نقشهٔ motherboard/chassis/vendor یا اندازه‌گیری محل بگیرید، نه از عکس محصول. یک server سنگین یا rack-mounted را تنها جابه‌جا نکنید؛ راهنمای محصول روی کمک مکانیکی و روش‌های ایمنی جابه‌جایی تأکید می‌کند [3].

## ۱۱. پایداری، بازیابی و امنیت، بخشی از طرح‌اند

خاموشی برق، خرابی SSD، به‌روزرسانی ناموفق، ریزش آب، دمای نامناسب یا گم‌شدن credential ممکن است کل آزمایش را از دسترس خارج کند. قبل از خرید، برای هر داده/سرویس مشخص کنید:

- کدام خروجی باید قابل بازیابی باشد و چه checkpointی واقعاً آزموده شده است؟
- آیا backup از دستگاه و شبکهٔ اصلی جداست؟ آیا restore را روی مسیر آزمایشی انجام داده‌اید؟
- کدام حساب‌ها، کنسول‌های مدیریتی و پورت‌های شبکه لازم‌اند؟ چه کسی مجوز دارد؟
- چه کسی driver/firmware را patch و log/دما/توان را مرور می‌کند؟
- چه چیزی باید بماند، حذف یا از media خارج شود و چه کسی deletion را تأیید می‌کند؟

NIST SP 800-53 Rev. 5 Release 5.2.0 کنترل‌های سازمانی برای backup، حفاظت فیزیکی و پایش شرایط محیطی را فهرست می‌کند؛ انتخاب و tailored کردن کنترل به ریسک و سازمان بستگی دارد و خواندن یک استاندارد، انطباق را ثابت نمی‌کند [5]. راهنمای CISA نیز backup آفلاین/رمزشده و آزمون restore را برای تاب‌آوری در برابر ransomware توصیه می‌کند [9]. برای دسترسی فیزیکی محدود و مدیریت secrets اصول را متناسب با محیط اجرا کنید؛ «آزمایشگاه خصوصی» به معنی privacy یا امنیت تضمین‌شده نیست.

## ۱۲. فهرست اجزا را به ماتریس سازگاری تبدیل کنید

به‌جای انتخاب چند قطعهٔ مشهور، از ستون «الزام»، «سند لازم»، «مالک بررسی» و «آزمون پذیرش» استفاده کنید:

| ردیف سامانه | چه چیزی را باید ثبت کرد؟ | روش کنترل پیش از اجرا |
|---|---|---|
| شتاب‌دهنده | حافظه/device، form factor، توان، runtime و kernel | datasheet و ماتریس پشتیبانی همان نسخه؛ بعد از نصب، شناسایی و آزمون محدود |
| CPU و مادربرد | socket، تعداد lane، تقسیم lane، NUMA، BIOS/firmware | manual برد/CPU و نقشهٔ اسلات؛ نه فقط تعداد slot چاپ‌شده |
| RAM | ظرفیت، channel/DIMM، پشتیبانی برد و حد workload | لیست پشتیبانی و آزمون حافظه در پیکربندی واقعی |
| PSU و ورودی | خروجی DC، کانکتور، redundancy و input power سیستم | مشخصات کل سیستم؛ ظرفیت محل را فرد واجد صلاحیت تأیید کند |
| chassis یا rack | ابعاد، تعداد/عرض جایگاه، clearance، وزن، airflow | راهنمای شاسی/ریل و اندازه‌گیری فضا |
| SSD / ذخیره‌ساز | ظرفیت usable، عمر/گارانتی، پروتکل، queue و backup | اندازهٔ واقعی داده؛ آزمون IO برای workload؛ آزمون restore |
| NIC و switch | نرخ اسمی، تعداد مسیر، نوع کابل و topology | manual تجهیز؛ آزمون link/latency/throughput پس از نصب |
| HVAC و پایش | ظرفیت قابل‌تحویل، مسیر هوا، inlet sensors، هشدار | محاسبه/commissioning تأسیسات؛ آزمون در محل و در بار |
| software stack | OS، driver، runtime، framework، package و kernel | ماتریس نسخه و آزمایش smoke روی محیط جدا |
| عملیات | دسترسی، patch، inventory، log، backup و مالک رسیدگی | runbook، دسترسی حداقلی و تمرین بازیابی |

«فهرست قطعات» در این فصل یعنی این کلاس‌ها، رابط‌ها و شرط‌های سازگاری؛ انتخاب SKU، تاریخ بازار و قیمت را به فصل ۵۶ واگذار می‌کنیم. حتی یک سرور یکپارچه باید طبق سند همان مدل و wiring/site plan همان محل پذیرفته شود؛ مرجع فروشگاه آنلاین برای ایمنی نصب کافی نیست [3].

## ۱۳. یک node یا چند node؟ با اندازه‌گیری تصمیم بگیرید

توزیع‌شدن هزینه‌هایی هم دارد: ترافیک collective، synchronization، storage مشترک، scheduler، نصب/patch چند سیستم، لاگ‌های چندمنبعه و failure modeهای جدید. اگر workload با یک node انجام می‌شود، افزودن شبکهٔ سریع یا cluster مدیریت‌شده ممکن است پیچیدگی بیفزاید بدون اینکه هدف را بهتر کند.

در مقابل، چند node زمانی معنا دارد که workload واقعاً به حافظه، تعداد شتاب‌دهنده، throughput موازی یا ظرفیت عملیاتی بیشتری نیاز دارد و کد/چارچوب شیوهٔ تقسیم را پشتیبانی می‌کند. قبل از scale-out کوچک‌ترین پروفایل workload را با benchmark داخلی خود اجرا و bottleneck را طبقه‌بندی کنید: compute، memory bandwidth، VRAM، I/O، شبکه یا CPU. نتیجه به workload شما مربوط است، نه رتبه‌بندی عمومیِ قطعات.

## ۱۴. راه‌اندازی را مرحله‌ای و قابل بازگشت انجام دهید

یک runbook کوتاه می‌تواند مراحل را چنین نگه دارد:

1. **ثبت طراحی:** workload، نام قطعات انتخاب‌شده، نسخهٔ سندها، ظرفیت‌های محل و تغییرهای تأییدشده.
2. **بازبینی ایمنی و فضا:** پیش از برق‌دادن، شخص واجد صلاحیت محل و نصب را بررسی کند؛ این کتاب جای چک‌لیست سازنده و مقررات را نمی‌گیرد.
3. **راه‌اندازی پایه:** firmware/OS/driver از منبع رسمی، patch مشخص، حساب کم‌دسترسی و شبکهٔ محدود.
4. **تأیید inventory:** CPU/RAM/SSD/accelerator/NIC شناخته می‌شوند؛ خطای firmware یا دمای idle بررسی می‌شود.
5. **تأیید topology:** تنها ابزار متناسب با stack خود را به کار ببرید؛ برای نمونه در مسیر NVIDIA، NCCL docs ابزار topology و آزمون ارتباط را شرح می‌دهد [4].
6. **آزمون کم‌خطر:** ابتدا حافظه/دادهٔ ساختگی و کار کوچک؛ سپس مدت و بار را مرحله‌ای بالا ببرید و توان/دما/خطا را ثبت کنید.
7. **آزمون بازیابی:** از فایل checkpoint یا پشتیبان مجاز، restore کنید؛ موفقیت backup قبل از آزمون restore ثابت نیست.
8. **ثبت خروجی:** نسخهٔ نرم‌افزار، تنظیمات، ابعاد کار، ورودی/خروجی، خطا، نمونهٔ مصرف و محدودیت‌ها را ثبت کنید.

فقط پس از این آزمون می‌توان دربارهٔ رفتار همان سیستم و همان workload عددی نوشت. آزمون واحد پروژهٔ همراه، آزمایش سخت‌افزار یا network fabric نیست.

## ۱۵. از ابتدا مسیر ارتقا و نقطهٔ توقف را تعریف کنید

پیش از شروع مشخص کنید چه چیزی را «ارتقا» می‌نامید: RAM، فضای ذخیره‌سازی، accelerator، node، شبکه یا اتاق/تأسیسات. برای هر گزینه سؤال کنید:

- آیا برد، firmware، slot/lanes، chassis و PSU واقعاً جا و پشتیبانی دارند؟
- آیا سرمایش و تخصیص برق محل هم در همان مرحله رشد می‌کنند؟
- آیا فریم‌ورک/مدل از افزایش device یا node سود می‌برد؟
- هزینهٔ عملیات، خرابی احتمالی و ظرفیت تیم چیست؟ فصل ۵۶ برای هزینهٔ چرخهٔ عمر است.
- آیا checkpoint/داده روی storage تازه قابل‌خواندن و قابل‌بازیابی می‌ماند؟

اگر یک قطعهٔ تازه در خانه جا شود، الزاماً ارتقای ایمن یا پشتیبانی‌شده نیست. در طرح سازمانی، مسئله ممکن است منبع تغذیه، switch، مجوز شبکه، UPS، فضای rack، آب یا زمان تحویل تأسیسات باشد، نه GPU.

## ۱۶. دفتر طراحی نمونهٔ فصل را چطور بخوانیم؟

پروژهٔ همراه ظرفیت‌ها را از fixture JSON می‌گیرد و قیود را با arithmetic ساده بررسی می‌کند. «نیاز حافظه به‌ازای هر accelerator»، «حافظهٔ میزبان»، ذخیره‌سازی موردنیاز و ظرفیت‌های اظهارشده را جدا مقایسه می‌کند. بار حرارتی را از توان ورودی برنامه‌ریزی‌شده به Btu/h تبدیل می‌کند؛ نرخ شبکهٔ اسمی را با حداقل ورودی workload می‌سنجد؛ و اعلامیهٔ PSU/stack را با ورودی‌های طرح چک می‌کند.

این پروژه پاسخ نمی‌دهد کدام قطعه را بخرید. حتی وضعیت `paper_feasible` یعنی فقط همان اعداد از همان fixture با فرض `۰٫۹` برای VRAM قابل‌استفاده و ضریب آموزشی `۱٫۲` برای screen سرمایش سازگارند. هیچ‌یک قانون فنی همگانی، ظرفیت محصول واقعی، تأیید سیم‌کشی یا نتیجهٔ benchmark نیست.

## ۱۷. خروجی محلی پروژه و مرز آن

Fixture `v4-ch09-synthetic-lab-design-v1` در Python 3.13.16 و فقط با کتابخانهٔ استاندارد اجرا شد؛ **۵۷/۵۷ آزمون unit موفق** بود. در چهار profile نمونه، سه طرح از screen عددی fixture عبور کردند و طرح چهارم نیاز به بازنگری داشت:

| پروفایل ساختگی | VRAM مؤثر/نیاز هر accelerator | ذخیره‌سازی لازم/اعلام‌شده | توان ورودی برنامه‌ریزی‌شدهٔ کل سایت | نیاز سرمایشِ screen با ضریب fixture | نتیجه |
|---|---:|---:|---:|---:|---|
| شخصی تک‌گره | ۲۱٫۶ / ۱۹ GiB | ۵٫۱ / ۸ TB | ۵۴۵ W | ۲٬۲۳۱٫۵۴ Btu/h | `paper_feasible` |
| حرفه‌ای مستقل | ۴۳٫۲ / ۴۲ GiB | ۱۸٫۲ / ۲۴ TB | ۲٬۱۵۰ W | ۸٬۸۰۳٫۳۳ Btu/h | `paper_feasible` |
| کلاستر سازمانی سه‌گره | ۷۲ / ۷۰ GiB | ۲۳۶ / ۳۰۰ TB | ۱۸٬۱۰۰ W | ۷۴٬۱۱۱٫۷۲ Btu/h | `paper_feasible` |
| طرح عمداً ناکافی | ۵۷٫۶ / ۶۰ GiB | ۱۰۶ / ۸۰ TB | ۱۳٬۱۰۰ W | ۵۳٬۶۳۸٫۸۷ Btu/h | `needs_revision` |

در پروفایل آخر، کمبود VRAM قابل‌استفاده، host RAM، storage و PSU، تجاوز از تخصیص ورودی سایت، سرمایش پایین‌تر از screen، شبکهٔ اسمی کم‌تر و پشتیبانی اعلام‌شدهٔ ناقص ثبت شدند. این جدول فقط حساب همان ورودی‌هاست. هیچ قطعهٔ واقعی وصل نشده؛ هیچ محیط، مدار، PSU، HVAC، شبکه، workload یا دمایی اندازه‌گیری نشده است. هیچ benchmark، قیمت، نصب، آموزش مدل یا توصیهٔ خرید انجام نشده.

## ۱۸. تمرین‌ها

۱. در جدول نیازمندی‌ها، برای یک workload آموزشی کوچک پنج الزام بنویسید؛ برای هرکدام واحد، منبع/فرض و کسی را که باید آن را تأیید کند مشخص کنید.
۲. در پروفایل شخصی، `working_copies` داده را از ۲ به ۳ تغییر دهید. فضای storage لازم چقدر می‌شود؟ آیا نتیجه به قیمت SSD اشاره دارد؟
۳. اگر memory لازم هر accelerator از ۴۲ به ۴۴ GiB برسد، چرا profile workstation از screen فعلی عبور نمی‌کند؟ تغییر «دو GPU داریم» پاسخ مسئله است یا نه؟
۴. برای یک workload تک‌گره‌ای، یک دلیل برای استفاده‌نکردن از cluster و یک شرط لازم برای توجیه scale-out بنویسید.
۵. توان ورودی سیستم و ظرفیت خروجی DC پاور چه تفاوتی دارند؟ دو منبع رسمی سازنده که برای یک طرح واقعی باید خواند نام ببرید.
۶. چرا `Btu/h` محاسبه‌شده از وات، ظرفیت کولر اتاق را تعیین نمی‌کند؟ دست‌کم سه ورودی HVAC/ساختمان را که در پروژه نیستند فهرست کنید.
۷. برای شبکهٔ چندگره‌ای خود، سه benchmark/آزمون متناسب با stack را از مستند همان نسخه پیدا کنید؛ line-rate اسمی و نتیجهٔ واقعی را جدا در گزارش بنویسید.
۸. برای دادهٔ حساس، محل backup، جداسازی، مالک restore و آزمون recovery را در runbook مشخص کنید؛ مدعی compliance نشوید.
۹. در پروفایل «سازمانی»، فرض کنید capacity برق محل هنوز توسط facility تأیید نشده است. چرا status `paper_feasible` نباید برای شروع deployment کافی باشد؟

پاسخ‌نامهٔ مستقل تمرین‌ها در [پاسخ‌نامهٔ فصل ۵۵](book-engineering/answers/55-ai-lab-design.md) آمده است.

## ۱۹. جمع‌بندی و پیوند به فصل بعد

آزمایشگاه از workload شروع می‌شود و تنها پس از طراحی نرم‌افزار، حافظه، توپولوژی، storage، برق، گرما، امنیت و عملیات معنا پیدا می‌کند. سطوح شخصی، حرفه‌ای و سازمانی الگوهای تصمیم‌اند، نه نردبان benchmark. ابتدا سند و ظرفیت محل را بگیرید؛ بعد طرح را مرور کنید؛ سپس با متخصص محل نصب را تأیید کنید و workload کوچک را اندازه بگیرید. قیمت، خرید/اجاره و هزینهٔ مالکیت فصل بعد است.

## ۲۰. منابع و تاریخ بازبینی

تاریخ بررسی منابع: **۶ نوامبر ۲۰۲۶**. برای سندهای آنلاین، مشخصات و نسخهٔ جاریِ تجهیز/نرم‌افزار پیش از طراحی واقعی دوباره کنترل شود.

1. U.S. Department of Energy, Federal Energy Management Program, **Best Practices Guide for Energy-Efficient Data Center Design**, revised July 2024. این راهنما دربارهٔ سامانهٔ مرکز داده است؛ توصیه‌های جریان هوا و سرمایش را بی‌واسطه به هر اتاق کوچک تعمیم ندهید. [PDF رسمی](https://www.energy.gov/sites/default/files/2024-07/best-practice-guide-data-center-design_0.pdf).
2. ASHRAE TC 9.9, **Thermal Guidelines for Data Processing Environments**, 5th edition reference card, accessed 6 November 2026. ردهٔ محیط، محل سنجش و سند هر دستگاه مهم‌اند. [Reference card](https://www.ashrae.org/file%20library/technical%20resources/bookstore/supplemental%20files/therm-gdlns-5th-r-e-refcard.pdf)؛ [Publication errata/updates](https://resourcecenter.ashrae.org/technical-resources/publication-errata-and-updates).
3. NVIDIA, **DGX B200 User Guide**, current online safety and system documentation, accessed 6 November 2026. نمونه‌ای از سند اختصاصی محصول و شرط پیروی از manual همان تجهیز؛ نه توصیهٔ خرید یا منبعی برای تعمیم مشخصات به PC. [Introduction](https://docs.nvidia.com/dgx/dgxb200-user-guide/introduction-to-dgxb200.html) · [Safety](https://docs.nvidia.com/dgx/dgxb200-user-guide/safety.html).
4. NVIDIA, **NCCL 2.32.3 User Guide: Performance and tuning**, current online documentation accessed 6 November 2026. توپولوژی و آزمون ارتباطی باید روی stack/سیستم واقعی بررسی شود. [Guide](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/performance_and_tuning.html).
5. NIST, **SP 800-53 Rev. 5, Security and Privacy Controls for Information Systems and Organizations**, Release 5.2.0 minor release note published 27 August 2025; controls are risk-tailored. [NIST page](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) · [DOI](https://doi.org/10.6028/NIST.SP.800-53r5).
6. NIST, **SP 800-88 Rev. 2, Guidelines for Media Sanitization**, final published 26 September 2025. [NIST publication page](https://csrc.nist.gov/pubs/sp/800/88/r2/final) · [DOI](https://doi.org/10.6028/NIST.SP.800-88r2).
7. U.S. Occupational Safety and Health Administration, **29 CFR 1910.333 — Selection and use of work practices**, current online regulation accessed 6 November 2026. دامنه و اجرای مقررات را با حوزهٔ محل کار/مرجع محلی تطبیق دهید؛ این فصل دستور سیم‌کشی نمی‌دهد. [OSHA](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.333).
8. NIST, **Guide to the SI, Appendix B.9: Conversion factors**, web page updated 18 August 2025, accessed 6 November 2026. تبدیل مشتق‌شدهٔ W به Btu/h صرفاً تبدیل واحد است. [Appendix B.9](https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b9).
9. CISA and partner agencies, **#StopRansomware Guide**, online guide accessed 6 November 2026. برای backup رمز‌شده و جدا و آزمون restore؛ این راهنما امنیت یک آزمایشگاه مشخص را تأیید نمی‌کند. [CISA guide](https://www.cisa.gov/stopransomware/ransomware-guide).

## ۲۱. پیوست اجرایی: فایل آزموده‌شدهٔ پروژه

فایل بعدی عیناً از `book-engineering/projects/55-ai-lab-design/lab_design_planner.py` درج شده است. آزمون سازنده نیز برابری byte-for-byte آن را کنترل می‌کند.

```python
"""Arithmetic-only lab design checks using synthetic, user-declared profiles.

This tool is not a hardware selector, benchmark, electrical-code checker, or
engineering approval. It compares supplied requirements with supplied design
limits and reports the assumptions it used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "v4-ch09-lab-design-v1"
BTU_PER_HOUR_PER_WATT = 3.412141633
DEFAULT_FIXTURE = Path(__file__).with_name("sample_labs.json")
REQUIRED_FALSE_METADATA = (
    "real_hardware_measured",
    "real_workload_run",
    "vendor_skus_included",
    "prices_included",
    "benchmark_performed",
    "electrical_code_checked",
    "installation_performed",
    "training_performed",
)
ALLOWED_TIERS = {
    "personal-low-cost",
    "independent-professional",
    "organizational-cluster",
    "synthetic-underprovisioned",
}


class DesignInputError(ValueError):
    """Raised when a lab-design fixture is malformed or unsafe to interpret."""


def _mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DesignInputError(f"{path} must be an object")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DesignInputError(f"{path} must be a non-empty string")
    return value.strip()


def _number(value: Any, path: str, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DesignInputError(f"{path} must be a number")
    number = float(value)
    if not math.isfinite(number) or number < minimum:
        raise DesignInputError(f"{path} must be finite and at least {minimum}")
    return number


def _integer(value: Any, path: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise DesignInputError(f"{path} must be an integer at least {minimum}")
    return value


def _string_list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list):
        raise DesignInputError(f"{path} must be a list")
    result = [_string(item, f"{path}[{index}]") for index, item in enumerate(value)]
    if len(set(result)) != len(result):
        raise DesignInputError(f"{path} must not contain duplicates")
    return result


def _validate_storage(storage: Any, path: str) -> None:
    storage = _mapping(storage, path)
    for field in ("dataset_tb", "checkpoint_size_tb", "scratch_tb", "backup_tb"):
        _number(storage.get(field), f"{path}.{field}")
    _integer(storage.get("working_copies"), f"{path}.working_copies", minimum=1)
    _integer(storage.get("checkpoint_versions"), f"{path}.checkpoint_versions", minimum=0)


def validate_fixture(fixture: Any) -> None:
    """Validate schema and explicit boundaries; this never verifies real equipment."""
    fixture = _mapping(fixture, "fixture")
    if fixture.get("schema_version") != SCHEMA_VERSION:
        raise DesignInputError(f"fixture.schema_version must equal {SCHEMA_VERSION}")
    _string(fixture.get("fixture_id"), "fixture.fixture_id")
    if fixture.get("label_source") != "synthetic_fixture":
        raise DesignInputError("fixture.label_source must be synthetic_fixture")

    metadata = _mapping(fixture.get("metadata"), "fixture.metadata")
    for field in REQUIRED_FALSE_METADATA:
        if metadata.get(field) is not False:
            raise DesignInputError(f"fixture.metadata.{field} must be false")

    policy = _mapping(fixture.get("policy"), "fixture.policy")
    usable_fraction = _number(policy.get("usable_vram_fraction"), "fixture.policy.usable_vram_fraction")
    if not 0 < usable_fraction <= 1:
        raise DesignInputError("fixture.policy.usable_vram_fraction must be in (0, 1]")
    _number(policy.get("cooling_design_factor"), "fixture.policy.cooling_design_factor", minimum=1.0)
    _string(policy.get("policy_note"), "fixture.policy.policy_note")

    profiles = fixture.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise DesignInputError("fixture.profiles must be a non-empty list")
    identifiers: set[str] = set()
    for index, raw_profile in enumerate(profiles):
        path = f"fixture.profiles[{index}]"
        profile = _mapping(raw_profile, path)
        identifier = _string(profile.get("profile_id"), f"{path}.profile_id")
        if identifier in identifiers:
            raise DesignInputError(f"duplicate profile_id: {identifier}")
        identifiers.add(identifier)
        tier = _string(profile.get("tier"), f"{path}.tier")
        if tier not in ALLOWED_TIERS:
            raise DesignInputError(f"{path}.tier is not an allowed synthetic tier")
        _string(profile.get("topology"), f"{path}.topology")

        workload = _mapping(profile.get("workload"), f"{path}.workload")
        _integer(workload.get("minimum_nodes"), f"{path}.workload.minimum_nodes", minimum=1)
        _integer(workload.get("accelerators_per_node"), f"{path}.workload.accelerators_per_node", minimum=1)
        _number(workload.get("minimum_vram_gib_per_accelerator"), f"{path}.workload.minimum_vram_gib_per_accelerator", minimum=0.000001)
        _number(workload.get("minimum_host_ram_gib"), f"{path}.workload.minimum_host_ram_gib", minimum=0.000001)
        _validate_storage(workload.get("storage"), f"{path}.workload.storage")
        _number(workload.get("minimum_nominal_interconnect_gbps"), f"{path}.workload.minimum_nominal_interconnect_gbps")
        _string_list(workload.get("required_runtime_stack"), f"{path}.workload.required_runtime_stack")

        design = _mapping(profile.get("design"), f"{path}.design")
        _integer(design.get("node_count"), f"{path}.design.node_count", minimum=1)
        _integer(design.get("accelerators_per_node"), f"{path}.design.accelerators_per_node", minimum=1)
        _number(design.get("vram_gib_per_accelerator"), f"{path}.design.vram_gib_per_accelerator", minimum=0.000001)
        _number(design.get("host_ram_gib"), f"{path}.design.host_ram_gib", minimum=0.000001)
        _integer(design.get("documented_accelerator_positions_per_node"), f"{path}.design.documented_accelerator_positions_per_node", minimum=0)
        _number(design.get("usable_storage_tb"), f"{path}.design.usable_storage_tb")
        _number(design.get("estimated_component_dc_load_w_per_node"), f"{path}.design.estimated_component_dc_load_w_per_node")
        _number(design.get("psu_dc_capacity_w_per_node"), f"{path}.design.psu_dc_capacity_w_per_node", minimum=0.000001)
        _number(design.get("system_peak_input_w_per_node"), f"{path}.design.system_peak_input_w_per_node")
        _number(design.get("network_gear_input_w_total"), f"{path}.design.network_gear_input_w_total")
        _number(design.get("other_it_input_w_total"), f"{path}.design.other_it_input_w_total")
        _number(design.get("site_approved_input_capacity_w"), f"{path}.design.site_approved_input_capacity_w", minimum=0.000001)
        _number(design.get("cooling_capacity_btu_per_hour"), f"{path}.design.cooling_capacity_btu_per_hour", minimum=0.000001)
        _number(design.get("nominal_interconnect_gbps"), f"{path}.design.nominal_interconnect_gbps")
        _string_list(design.get("declared_runtime_stack"), f"{path}.design.declared_runtime_stack")
        _string(design.get("basis_note"), f"{path}.design.basis_note")


def load_fixture(path: str | Path = DEFAULT_FIXTURE) -> tuple[dict[str, Any], str]:
    """Load, hash and validate a UTF-8 JSON fixture."""
    fixture_path = Path(path)
    try:
        raw = fixture_path.read_bytes()
        fixture = json.loads(raw.decode("utf-8"))
    except FileNotFoundError as exc:
        raise DesignInputError(f"fixture not found: {fixture_path}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DesignInputError(f"fixture is not valid UTF-8 JSON: {fixture_path}") from exc
    validate_fixture(fixture)
    return fixture, hashlib.sha256(raw).hexdigest()


def required_storage_tb(storage: dict[str, Any]) -> float:
    """Sum user-declared active data, working copies, checkpoints, scratch and backups."""
    _validate_storage(storage, "storage")
    return (
        float(storage["dataset_tb"]) * int(storage["working_copies"])
        + float(storage["checkpoint_size_tb"]) * int(storage["checkpoint_versions"])
        + float(storage["scratch_tb"])
        + float(storage["backup_tb"])
    )


def _check(name: str, passed: bool, **details: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), **details}


def evaluate_profile(profile: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    """Compare the profile's declared arithmetic inputs; never probe a device."""
    workload = profile["workload"]
    design = profile["design"]
    node_count = int(design["node_count"])
    usable_vram = float(design["vram_gib_per_accelerator"]) * float(policy["usable_vram_fraction"])
    required_storage = required_storage_tb(workload["storage"])
    total_site_input = (
        node_count * float(design["system_peak_input_w_per_node"])
        + float(design["network_gear_input_w_total"])
        + float(design["other_it_input_w_total"])
    )
    heat_load = total_site_input * BTU_PER_HOUR_PER_WATT
    cooling_required = heat_load * float(policy["cooling_design_factor"])
    required_stack = set(workload["required_runtime_stack"])
    declared_stack = set(design["declared_runtime_stack"])

    checks = [
        _check(
            "minimum_nodes",
            node_count >= int(workload["minimum_nodes"]),
            required=int(workload["minimum_nodes"]), available=node_count,
        ),
        _check(
            "accelerators_per_node",
            int(design["accelerators_per_node"]) >= int(workload["accelerators_per_node"]),
            required=int(workload["accelerators_per_node"]), available=int(design["accelerators_per_node"]),
        ),
        _check(
            "per_accelerator_memory",
            usable_vram >= float(workload["minimum_vram_gib_per_accelerator"]),
            required_gib=round(float(workload["minimum_vram_gib_per_accelerator"]), 6),
            declared_capacity_gib=round(float(design["vram_gib_per_accelerator"]), 6),
            usable_capacity_gib=round(usable_vram, 6),
            usable_fraction=float(policy["usable_vram_fraction"]),
        ),
        _check(
            "host_ram",
            float(design["host_ram_gib"]) >= float(workload["minimum_host_ram_gib"]),
            required_gib=round(float(workload["minimum_host_ram_gib"]), 6),
            available_gib=round(float(design["host_ram_gib"]), 6),
        ),
        _check(
            "documented_accelerator_positions",
            int(design["documented_accelerator_positions_per_node"]) >= int(design["accelerators_per_node"]),
            required=int(design["accelerators_per_node"]),
            declared_available=int(design["documented_accelerator_positions_per_node"]),
        ),
        _check(
            "usable_storage",
            float(design["usable_storage_tb"]) >= required_storage,
            required_tb=round(required_storage, 6),
            available_tb=round(float(design["usable_storage_tb"]), 6),
        ),
        _check(
            "declared_psu_output_capacity",
            float(design["psu_dc_capacity_w_per_node"]) >= float(design["estimated_component_dc_load_w_per_node"]),
            estimated_component_load_w_per_node=round(float(design["estimated_component_dc_load_w_per_node"]), 6),
            declared_psu_output_w_per_node=round(float(design["psu_dc_capacity_w_per_node"]), 6),
            arithmetic_headroom_w_per_node=round(
                float(design["psu_dc_capacity_w_per_node"]) - float(design["estimated_component_dc_load_w_per_node"]), 6
            ),
        ),
        _check(
            "site_input_power_allocation",
            total_site_input <= float(design["site_approved_input_capacity_w"]),
            planned_input_w=round(total_site_input, 6),
            user_declared_approved_capacity_w=round(float(design["site_approved_input_capacity_w"]), 6),
            arithmetic_margin_w=round(float(design["site_approved_input_capacity_w"]) - total_site_input, 6),
        ),
        _check(
            "cooling_capacity_screen",
            float(design["cooling_capacity_btu_per_hour"]) >= cooling_required,
            estimated_it_heat_btu_per_hour=round(heat_load, 6),
            fixture_policy_factor=float(policy["cooling_design_factor"]),
            screened_requirement_btu_per_hour=round(cooling_required, 6),
            user_declared_capacity_btu_per_hour=round(float(design["cooling_capacity_btu_per_hour"]), 6),
        ),
        _check(
            "nominal_interconnect_rate",
            float(design["nominal_interconnect_gbps"]) >= float(workload["minimum_nominal_interconnect_gbps"]),
            minimum_nominal_gbps=round(float(workload["minimum_nominal_interconnect_gbps"]), 6),
            declared_nominal_gbps=round(float(design["nominal_interconnect_gbps"]), 6),
        ),
        _check(
            "declared_runtime_stack",
            required_stack.issubset(declared_stack),
            required=sorted(required_stack),
            declared=sorted(declared_stack),
            missing=sorted(required_stack - declared_stack),
        ),
    ]
    passed = all(item["passed"] for item in checks)
    return {
        "profile_id": profile["profile_id"],
        "tier": profile["tier"],
        "topology": profile["topology"],
        "status": "paper_feasible" if passed else "needs_revision",
        "inputs_are_synthetic": True,
        "derived": {
            "required_storage_tb": round(required_storage, 6),
            "total_site_input_power_w": round(total_site_input, 6),
            "estimated_it_heat_btu_per_hour": round(heat_load, 6),
            "screened_cooling_requirement_btu_per_hour": round(cooling_required, 6),
            "per_accelerator_usable_vram_gib": round(usable_vram, 6),
        },
        "checks": checks,
        "limitations": [
            "Declared capacities and compatibility notes were not checked against physical devices.",
            "Nominal network rate is not measured throughput or application performance.",
            "Power, cooling and storage calculations are first-order screens, not code or engineering approval.",
        ],
    }


def run_demo(fixture_path: str | Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    """Return deterministic results for all synthetic lab profiles."""
    fixture, digest = load_fixture(fixture_path)
    policy = fixture["policy"]
    profiles = [evaluate_profile(profile, policy) for profile in fixture["profiles"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "fixture": {
            "fixture_id": fixture["fixture_id"],
            "sha256": digest,
            "label_source": fixture["label_source"],
        },
        "scope": {
            "real_hardware_measured": False,
            "real_workload_run": False,
            "vendor_skus_included": False,
            "prices_included": False,
            "benchmark_performed": False,
            "electrical_code_checked": False,
            "installation_performed": False,
            "training_performed": False,
            "claim": "synthetic declared-capacity arithmetic only; not a bill of materials or deployment approval",
        },
        "policy": {
            "usable_vram_fraction": float(policy["usable_vram_fraction"]),
            "cooling_design_factor": float(policy["cooling_design_factor"]),
            "policy_note": policy["policy_note"],
        },
        "summary": {
            "profiles": len(profiles),
            "paper_feasible": sum(profile["status"] == "paper_feasible" for profile in profiles),
            "needs_revision": sum(profile["status"] == "needs_revision" for profile in profiles),
        },
        "profiles": profiles,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check declared lab-design capacity arithmetic")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, help="write JSON report to a file (default: stdout)")
    args = parser.parse_args(argv)
    try:
        result = run_demo(args.fixture)
    except DesignInputError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2
    serialized = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
        print(f"Wrote synthetic design screen: {args.output}")
    else:
        sys.stdout.write(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
