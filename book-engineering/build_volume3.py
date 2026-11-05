"""Safely append authored volume 3 chapters; never rewrite a published chapter.

Only contiguous chapter sources present in chapters/ are eligible for append.
The source document remains authoritative; a mismatch with existing data.json is
an error that requires explicit review rather than silent replacement.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import mistune

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data.json"
VOLUME_ID = "art-science-intelligence-v3"
PLANNED_CHAPTERS = 14
RENDER = mistune.create_markdown(escape=False, plugins=["table"])

# Local volume numbering 1–14 maps exactly to global roadmap chapters 33–46.
SPECS = [
    (1, 33, "33-tokenization", "توکن‌سازی، واژگان و توکن‌های ویژه", "◈"),
    (2, 34, "34-attention", "Attention، Query/Key/Value و پیاده‌سازی ماتریسی", "⌘"),
    (3, 35, "35-self-attention", "Self-Attention، چندسری و ماسک علّی", "◉"),
    (4, 36, "36-position-normalization", "موقعیت، RoPE، اتصال باقیمانده و LayerNorm", "↔"),
    (5, 37, "37-encoder-decoder", "Encoder، Decoder و مدل‌های Encoder–Decoder", "⇄"),
    (6, 38, "38-long-context", "زمینه بلند، KV Cache، GQA، Sparse Attention و MoE", "⤢"),
    (7, 39, "39-multimodal-transformer", "Transformer چندوجهی و هم‌ترازی تصویر و صوت", "▧"),
    (8, 40, "40-small-data-project", "پروژه داده کوچک و آماده‌سازی مجاز متن", "▤"),
    (9, 41, "41-first-language-model", "نخستین مدل زبانی کوچک: آموزش، ارزیابی و تولید", "✦"),
    (10, 42, "42-mini-gpt", "طراحی Mini GPT و بودجه آموزش", "◌"),
    (11, 43, "43-corpus", "Corpus، مجوز، کیفیت و جلوگیری از آلودگی ارزیابی", "▦"),
    (12, 44, "44-pretraining", "پیش‌آموزش، برنامه نرخ یادگیری و Checkpoint", "↗"),
    (13, 45, "45-precision", "دقت عددی، BF16، FP16، FP8 و Quantization", "±"),
    (14, 46, "46-scale-training", "آموزش توزیع‌شده، حافظه و بازتولید آزمایش", "⌁"),
]


def build_chapter(spec: tuple[int, int, str, str, str]) -> dict:
    local_num, global_num, slug, title, icon = spec
    relative = f"book-engineering/chapters/{slug}.md"
    source = ROOT / relative
    if not source.is_file():
        raise FileNotFoundError(source)
    text = source.read_text(encoding="utf-8")
    parts = re.split(r"^## (.+)$", text, flags=re.MULTILINE)
    if len(parts) < 3:
        raise ValueError(f"chapter {global_num} must contain at least one H2 section")
    sections = []
    section_no = 0
    for index in range(1, len(parts), 2):
        section_no += 1
        body = (parts[0] + "\n" if index == 1 else "") + "## " + parts[index] + "\n" + parts[index + 1]
        html = RENDER(body)
        if not html.strip():
            raise ValueError(f"empty rendered section {global_num}.{section_no}")
        sections.append({
            "id": f"art-science-v3-ch{local_num:02}-s{section_no:02}",
            "title": parts[index].strip(),
            "file": relative,
            "html": html,
        })
    return {
        "num": local_num,
        "id": f"art-science-v3-ch{local_num:02}",
        "title": title,
        "icon": icon,
        "sections": sections,
    }


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    available = [spec for spec in SPECS if (ROOT / "book-engineering/chapters" / f"{spec[2]}.md").is_file()]
    if not available:
        raise RuntimeError("no authored volume 3 chapter source found")
    expected_nums = list(range(1, len(available) + 1))
    if [spec[0] for spec in available] != expected_nums:
        raise RuntimeError("volume 3 source chapters must be authored in order without gaps")
    chapters = [build_chapter(spec) for spec in available]

    matches = [book for book in data["books"] if book.get("id") == VOLUME_ID]
    if len(matches) > 1:
        raise RuntimeError("duplicate volume 3 book records")
    subtitle = f"Transformer و مهندسی مدل زبانی | ۱۴ فصل در نقشه؛ {len(chapters)} فصل منتشرشده"
    changed = False
    if matches:
        book = matches[0]
        existing = book.get("chapters", [])
        if len(existing) > len(chapters):
            raise RuntimeError("a published chapter source is missing; refusing to remove it")
        for index, old_chapter in enumerate(existing):
            if old_chapter != chapters[index]:
                raise RuntimeError(f"published chapter {index + 1} differs from its source; refusing to overwrite")
        if len(existing) < len(chapters):
            book["chapters"] = existing + chapters[len(existing):]
            changed = True
        if book.get("subtitle") != subtitle:
            book["subtitle"] = subtitle
            changed = True
    else:
        v2_index = next((index for index, book in enumerate(data["books"]) if book.get("id") == "art-science-intelligence-v2"), None)
        if v2_index is None:
            raise RuntimeError("volume 2 book record not found")
        book = {
            "id": VOLUME_ID,
            "title": "هنر و علم ساخت هوش — جلد سوم",
            "subtitle": subtitle,
            "author": "Babak & Ai",
            "cover": "assets/images/art-science-cover.webp",
            "chapters": chapters,
        }
        data["books"].insert(v2_index + 1, book)
        changed = True

    if changed:
        DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    contents = [
        "# هنر و علم ساخت هوش — جلد سوم",
        "",
        "**The Art & Science of Building Intelligence | Babak & Ai**",
        "",
        f"وضعیت: ۱۴ فصل در نقشه؛ {len(chapters)} فصل از ۱۴ فصل تا این انتشار نگارش و آزموده شده‌اند. این فایل Markdown است؛ PDF و EPUB تولید نشده‌اند.",
        "",
        "## فهرست فصل‌های منتشرشده",
        "",
    ]
    for chapter in chapters:
        _, global_num, slug, title, _ = SPECS[chapter["num"] - 1]
        contents.append(f"- فصل {chapter['num']} (سراسری {global_num}) — {title}")
    contents.append("")
    for chapter, spec in zip(chapters, available):
        source_path = ROOT / "book-engineering/chapters" / f"{spec[2]}.md"
        contents.extend(["---", "", source_path.read_text(encoding="utf-8").rstrip(), ""])
    output = "\n".join(contents).rstrip() + "\n"
    full_path = ROOT / "volume-3-full-fa.md"
    if not full_path.is_file() or full_path.read_text(encoding="utf-8") != output:
        full_path.write_text(output, encoding="utf-8")
    action = "updated" if changed else "already matches"
    print(f"Volume 3 {action}: {len(chapters)}/{PLANNED_CHAPTERS} chapters; sections={[len(c['sections']) for c in chapters]}")


if __name__ == "__main__":
    main()
