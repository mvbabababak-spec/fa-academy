# پروژهٔ فصل ۵۲ — قرارداد صوت و سنجه‌های transcript

این آزمایشگاه کوچک و فقط با کتابخانهٔ استاندارد Python اجرا می‌شود. یک سینوس تحلیلیِ ساختگی برای بررسی نرخ نمونه، پنجره‌بندی، RMS و طیف ساخته می‌شود؛ سه جفت متن ساختگی نیز مسیر محاسبهٔ WER/CER و تفاوت تجمیع corpus با میانگین جمله‌ای را می‌آزمایند. **فایل ضبط‌شده، گفتار، ASR، TTS، codec، مدل Audio-Language یا benchmark وجود ندارد.**

## اجرا

از ریشهٔ مخزن:

```bash
(cd book-engineering/projects/52-audio-lab && python -m unittest discover -v)
python book-engineering/projects/52-audio-lab/audio_lab.py \
  --mode audit --fixture book-engineering/projects/52-audio-lab/sample_transcripts.json \
  --output /tmp/ch52-audit
python book-engineering/projects/52-audio-lab/audio_lab.py \
  --mode demo --fixture book-engineering/projects/52-audio-lab/sample_transcripts.json \
  --output /tmp/ch52-demo
```

برای اجرای ثبت‌شده Python 3.13.16 به کار رفت؛ پروژه dependency یا شبکه نمی‌خواهد. اگر در ریشهٔ مخزن virtual environment به نام `.venv` دارید، دستور unittest از داخل پوشهٔ پروژه با `../../../.venv/bin/python -m unittest discover -v` اجرا می‌شود؛ دستورهای CLI که از ریشه اجرا می‌شوند را می‌توان با `.venv/bin/python` آغاز کرد. از خود پوشهٔ پروژه، مسیر `.venv/bin/python` به venv ریشه اشاره نمی‌کند.

## ورودی ساختگی و نتایج ثبت‌شده

`sample_transcripts.json` سه جفت reference/hypothesis با `label_source=synthetic_fixture` دارد؛ همه متن‌ها نمونهٔ مهندسیِ دستی‌اند، نه transcript صوت واقعی. فایل هیچ waveform یا خروجی مدل ندارد. در اجرای demo:

- سینوس ۴۴۰ هرتز، ۱۶ kHz و ۱۰۰ ms در حافظه ساخته شد: ۱۶۰۰ sample.
- پنجرهٔ ۲۵ ms و گام ۱۰ ms به ۸ frame کاملِ بدون padding انجامید؛ طیف DFT پنجره‌شده قله را در bin ۱۱ (۴۴۰ Hz) یافت. این طیف log-Mel نیست و tail پنج میلی‌ثانیه‌ای عمداً pad نشد.
- از ۱۱ واژهٔ reference و سه خطای ویرایشی، WER تجمیعی `3/11 = 0.2727272727272727` شد. میانگین سادهٔ WER جمله‌ها `0.21666666666666667` است و با WER تجمیعی تفاوت دارد.
- CER روی نویسه‌های Unicode پس از NFC/casefold و حذف فاصله‌های معمولی محاسبه می‌شود؛ این سیاست آموزشی ساده است و tokenizer/گرافیم‌کلاستر یا سیاست benchmark زبانی نیست.
- هر ۳۹ آزمون unit موفق شد؛ CER ساختگی `15/43 = 0.3488372093023256` بود. نتیجهٔ دقیق، فرمان‌ها و hash در `results.json` و محدودیت‌ها در `../../chapters/52-audit-report-fa.md` ثبت است.

## مرز ادعا

این پروژه نه گفتار می‌سازد و نه تشخیص/تولید گفتار را می‌آزماید؛ الگوریتمی برای resampling یا Mel filterbank هم پیاده‌سازی نمی‌کند. نتیجه‌ها کیفیت ASR/TTS، کیفیت فارسی، تعمیم، مدل، latency، سخت‌افزار، مجوز، privacy، رضایت گوینده یا benchmark را نشان نمی‌دهند. WER/CER فقط روی متن‌های ساختگی محاسبه می‌شوند. برای سامانهٔ واقعی لازم است preprocessing و normalization از پیش ثبت شود و دادهٔ آزمون از گوینده/منبع/جلسهٔ آموزش جدا بماند.
