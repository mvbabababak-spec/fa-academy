# پروژهٔ فصل ۵۱ — قرارداد وصله و سنجه‌های متن–تصویر

این آزمایشگاه CPU-only چند قرارداد محدود را برای تصویر و embedding امتحان می‌کند: شمار شبکهٔ وصله‌های ViT، ترتیب patchify/unpatchify، loss contrastive متقارن و معیارهای retrieval بر اساس `group_id`. fixture فقط بردارهای دستی چهاربعدی دارد؛ **فایل تصویر، tokenizer، image encoder، ViT forward pass یا مدل pretrained بارگیری نمی‌شود**.

## اجرا

از ریشهٔ مخزن، پس از نصب وابستگی‌های ثبت‌شده در `requirements.txt`:

```bash
(cd book-engineering/projects/51-vision-lab && python -m unittest discover -v)
python book-engineering/projects/51-vision-lab/vision_lab.py \
  --mode audit --fixture book-engineering/projects/51-vision-lab/sample_embeddings.json \
  --output /tmp/ch51-audit
python book-engineering/projects/51-vision-lab/vision_lab.py \
  --mode demo --fixture book-engineering/projects/51-vision-lab/sample_embeddings.json \
  --output /tmp/ch51-demo
```

برای اجرای ثبت‌شده، Python 3.13.16 و PyTorch 2.6.0+cpu به کار رفتند. دستورات روی CPU اجرا می‌شوند؛ checkpoint یا دادهٔ بیرونی دانلود نمی‌شود. در مخزن این محیط، در صورت نیاز `python` را با `.venv/bin/python` جایگزین کنید.

## Fixture و نتایج ثبت‌شده

`sample_embeddings.json` شامل چهار رکورد تصویر و چهار رکورد متن در بُعد ۴ و چهار گروه ساختگی است. رشته‌های caption placeholder هستند و هیچ نمونهٔ تصویری پشت بردارها نیست. SHA-256 فایل fixture:

```text
aba309bb1b3e69443802190b988a21e0432109c01b777f4f58fe11f992936522
```

در run ثبت‌شده:

- `audit`: چهار بردار تصویر، چهار بردار متن، چهار گروه و بُعد ۴ را گزارش کرد؛ training/model/image file بارگیری نشد.
- `demo`: tensor ساختگی `[3,8,8]` به `[4,48]` patch تبدیل و دقیق بازسازی شد. برای `224×224` با patch16 شمار توالی `197` و جفت‌های attention در هر head `38,809` است؛ برای `448×448` این شمار `785` و `616,225` شد (نسبت `15.878404493802984`).
- loss ساختگی `0.00024217297323048115` بود؛ Recall@1 و MRR هر دو جهت `1.0` و گرادیان متناهی شد، چون بردارهای fixture از پیش با گروه درست جور شده‌اند. هیچ train یا retrieval روی تصویر/مدل واقعی انجام نشده است.
- تمام **۲۶ آزمون** unit موفق شدند. جزئیات محیط، hash، خروجی JSON و مرز ادعا در `results.json` و `../../chapters/51-audit-report-fa.md` ثبت است.

## محدودیت ادعا

این پروژه ViT یا image encoder آموزش‌دیده نیست و کیفیت فهم تصویر، embedding، retrieval واقعی، zero-shot classification، localization، زبان فارسی، benchmark، fairness، robustness، حقوق/مجوز، privacy، GPU، latency، انرژی یا هزینهٔ محصول را نمی‌سنجد. Recall کامل روی چهار جفت ساختگی نتیجهٔ toy است، نه معیار عملکرد مدل. Split واقعی، provenance و ارزیابی باید در سطح تصویر/منبع/گروه مرتبط طراحی شوند؛ آزمون schema این کار را برای دادهٔ بیرونی انجام نمی‌دهد.
