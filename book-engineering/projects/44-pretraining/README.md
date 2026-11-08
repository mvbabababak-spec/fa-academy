# پروژهٔ فصل ۴۴: حلقهٔ پیش‌آموزش، نرخ یادگیری و Checkpoint

این پروژه **مدل را دوباره پیاده نمی‌کند**: کلاس `TinyFeedForwardLM`، tokenizer، قرارداد داده و ارزیابی را از پروژهٔ فصل ۴۱ reuse می‌کند؛ دادهٔ کوچک نیز از pipeline فصل ۴۰ می‌آید. موضوع پروژهٔ تازه، برنامه‌ریزی برحسب optimizer update، linear warmup + cosine decay، gradient accumulation با میانگین صحیح روی targetها، ثبت وضعیت و ادامهٔ دقیق یک run قطع‌شده است. نمودار SVG زیان هم مستقیماً از `history.json` همان اجرا ساخته می‌شود و به کتابخانهٔ رسم بیرونی نیاز ندارد.

## نیازمندی و اجرا

- Python 3.11+، PyTorch 2.6.x و CPU؛ GPU لازم نیست.
- هیچ سایت، مدل، داده یا checkpoint از شبکه دریافت نمی‌شود.
- ابتدا fixture مجازِ خودنوشتهٔ فصل ۴۰ را بسازید و سپس run فصل ۴۴ را اجرا کنید:

```bash
python book-engineering/projects/40-small-data-project/small_corpus.py \
  --manifest book-engineering/projects/40-small-data-project/sample_corpus.jsonl \
  --output /tmp/ch44-data --seed 40

python book-engineering/projects/44-pretraining/pretraining_run.py \
  --data-dir /tmp/ch44-data --output-dir /tmp/ch44-run \
  --total-updates 12 --microbatch-size 8 \
  --gradient-accumulation-steps 2 --peak-lr 0.01 \
  --warmup-updates 3 --min-lr-ratio 0.1 \
  --evaluation-every 3 --checkpoint-every 4 --seed 44
```

برای تمرین قطع و ادامه، ابتدا همان تنظیمات را با `--stop-after 6` اجرا کنید. سپس بدون تغییر داده یا تنظیمات، همان مسیر خروجی و آرگومان‌ها را همراه `--resume /tmp/ch44-run/checkpoint-latest.pt` بدهید. `--stop-after` فقط توقف کنترل‌شدهٔ آموزشی برای آزمون recovery است؛ `SIGKILL` یا قطع برق را شبیه‌سازی نمی‌کند. اگر خاموشی میان دو checkpoint رخ دهد، حداکثر به آخرین checkpoint نوشته‌شده برمی‌گردید.

۱۰ آزمون واحد:

```bash
cd book-engineering/projects/44-pretraining
python -m unittest discover -v
```

## برنامه و واحدها

`total_updates` شمار **optimizer.step**هاست، نه epoch و نه تعداد microbatch. در یک process، سقف targetها در هر به‌روزرسانی `microbatch_size × gradient_accumulation_steps × target_tokens_per_example` است؛ آخرین microbatch هر گذر می‌تواند کوچک‌تر باشد. پروژه مجموع loss را روی تمام targetهای update جمع و بر تعداد واقعی targetها تقسیم می‌کند، سپس گرادیان‌ها را accumulate می‌کند؛ بنابراین microbatch ناقص را مانند batch کامل وزن نمی‌دهد.

برنامهٔ نمونه با شمارهٔ یک‌مبنای update `t` تعریف می‌شود. در warmup، نرخ تا peak خطی بالا می‌رود؛ سپس به cosine decay می‌رسد و در update نهایی نسبت `min_lr_ratio` را می‌گیرد. برای resume، total updates، warmup و hash ورودی‌ها بخشی از قراردادند؛ اگر برنامه عوض شده باشد checkpoint رد می‌شود. ادامه‌دادنِ compute با schedule تازه مسئله‌ای جداست و با `--resume` پنهانی انجام نمی‌شود.

`checkpoint-latest.pt` شامل `model_state_dict`، AdamW state، موقعیت schedule/update، permutation و cursor داده، generator نمونه‌گیری، RNG مربوط به PyTorch، تاریخچه، config و hash فایل‌های train/validation/test است. در مرز update به فایل موقت همان پوشه نوشته و با `os.replace` جایگزین می‌شود؛ این الگو از دیده‌شدن فایل نیمه‌نوشته در قطع حین save می‌کاهد، اما دوام دیسک/شبکه یا صحت سخت‌افزار را تضمین نمی‌کند. برای بارگذاری `weights_only=True` و `map_location='cpu'` به‌کار می‌رود؛ بااین‌حال checkpoint ناشناس را قابل‌اعتماد فرض نکنید.

Checkpoint کامل، همزمان برای inference و resume نیست: inference معمولاً به وزن و قرارداد مدل/tokenizer نیاز دارد؛ ادامهٔ آموزش به وضعیت optimizer، scheduler، RNG، ترتیب داده، config و provenance هم نیازمند است. این fixture در پایان `checkpoint-final.pt` می‌سازد. ارزیابی validation برای پایش در فاصله‌های ثابت است؛ test فقط پس از تکمیل run خوانده می‌شود و در `metrics.json` با `test_once_after_training=1` ثبت می‌گردد. Resume از checkpoint کامل metric ذخیره‌شده را برمی‌گرداند و test را دوباره اجرا نمی‌کند.

## خروجی‌ها و محدودیت

- `checkpoint-latest.pt` — آخرین state کامل‌شده در مرز optimizer update.
- `checkpoint-final.pt` — state پایان run، پس از ارزیابی نهایی.
- `history.json` — نرخ واقعی، batch NLL، تعداد target، norm گرادیان و validationهای دوره‌ای.
- `loss_curve.svg` — نمودار NLL آموزش و validation، ساخته‌شده از history ثبت‌شده (نه از اعداد ساختگی یا snapshot جداگانه).
- `metrics.json` و `run_card.md` — وضعیت partial/complete، hash داده‌ها و نتیجهٔ نهایی.

این یک CPU smoke exercise روی corpus ساختگی ۱۶رکوردی و مدل بسیار کوچک فصل ۴۱ است. نه سرعت، مقیاس، کیفیت زبان یا schedule مناسب برای مدل واقعی را ارزیابی می‌کند، نه checkpoint بین نسخه‌ها/سخت‌افزارهای مختلف را تضمین می‌کند. برابری resume در آزمون فقط در محیط ثابت Python/PyTorch و CPU بررسی می‌شود. فایل‌های `build/` و checkpoint وارد Git نمی‌شوند.
