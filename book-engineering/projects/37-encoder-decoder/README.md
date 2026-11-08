# پروژهٔ فصل ۳۷: مقایسهٔ سه معماری Transformer

این نمونهٔ کوچکِ CPU‌پسند سه مسیر را کنار هم می‌گذارد: Encoder دوسویه با سر طبقه‌بندی، Decoder-only با ماسک علّی و پیش‌بینی توکن بعدی، و Encoder–Decoder با حافظهٔ منبع و cross-attention. هدف، آموزش یک مدل زبانی نیست؛ کد فقط شکل‌ها، جهت دسترسی attention و مسیر گرادیان را نشان می‌دهد.

## نیازمندی و اجرا

- Python 3.11 یا جدیدتر
- PyTorch 2.6.x؛ CPU کافی است و CUDA لازم نیست.

از همین پوشه:

```bash
python transformer_architectures.py
python -m unittest discover -v
```

خروجی نمونه باید این شکل‌ها را نشان دهد:

```text
encoder-only logits: (2, 3)
decoder-only next-token logits: (2, 4, 16)
encoder-decoder logits: (2, 3, 16)
decoder input: [[1, 8, 9], [1, 10, 11]]
all outputs finite: True
```

## قراردادها

- همهٔ token IDها از نوع `torch.long` و شکلشان `[batch, length]` است.
- `make_padding_mask` در جایگاه padding مقدار `True` می‌دهد.
- `causal_mask(T)` یک ماتریس بولی `[T,T]` می‌سازد که در آن `True` آینده را می‌بندد؛ این با قرارداد `nn.MultiheadAttention` در PyTorch 2.6 سازگار است.
- `shift_right(target, bos_id)` هدف را برای teacher forcing به `[BOS, y0, …, y(T−2)]` تبدیل می‌کند.
- logits خروجی Decoder در هر جایگاه توزیع خام روی واژگان‌اند؛ برای آموزش می‌توان آن‌ها را با `CrossEntropyLoss` و برچسب‌های یک‌خانه جلوتر مقایسه کرد.

## چه چیزی آزموده می‌شود؟

۱۳ آزمون، ماسک padding و علّی، شیفت هدف، شکل Encoder و classifier، اثر بافت راست در Encoder، شکل logits هر سه معماری، عدم نشت توکن آینده در Decoder-only، گرادیان از خروجی seq2seq به embedding منبع، و رد ورودی/پیکربندی نامعتبر را می‌سنجند.

## مرزهای نمونه

وزن‌ها تصادفی‌اند؛ آموزش، beam search، tokenizer واقعی، dropout، cache استنتاجی، position encoding نسبی و سنجش کیفیت/سرعت پوشش داده نشده‌اند. میانگین‌گیریِ masked برای classifier یکی از headهای ممکن است، نه ادعایی دربارهٔ همهٔ BERTها. در پروژه، همهٔ بلوک‌ها Pre-LN هستند؛ پیاده‌سازی‌های واقعی ممکن است چینش دیگری داشته باشند. پاسخ‌نامه و توضیح این محدودیت‌ها در فصل ۳۷ آمده‌اند.
