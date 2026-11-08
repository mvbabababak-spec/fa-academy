# مخزن Git و venv موقت

**هدف:** مخزن Git و venv موقت با داده ساختگی.

**پیش‌نیاز:** Python 3.13؛ Git روی PATH. نصب بسته اضافی الزامی نیست.

از همین پوشه: `python local_workflow.py`.

**خروجی ثبت‌شده در محیط آزمایش:**

```text
commit= First practice commit
worktree_clean= True
venv_ignored= .venv
network=not used
```

**آزمون:** `python -m unittest discover -v` از همین پوشه.

**محدودیت:** به Git روی PATH نیاز دارد؛ بدون شبکه و بدون دستکاری مخزن فعلی.
