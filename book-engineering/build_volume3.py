"""Safely append authored volume 3 chapters; never rewrite a published chapter.

Only contiguous chapter sources present in chapters/ are eligible for append.
Published chapters are immutable. After independently confirming that the final
existing chapter is still absent from the remote branch, --refresh-last-draft
may replace only that local draft and only when all of its stable IDs are intact.
"""
from __future__ import annotations

import argparse
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
    (4, 36, "36-position-normalization", "موقعیت، RoPE، اتصال باقیمانده، LayerNorm و FFN", "↔"),
    (5, 37, "37-encoder-decoder", "Encoder، Decoder و مدل‌های Encoder–Decoder", "⇄"),
    (6, 38, "38-long-context", "زمینه بلند، KV Cache، GQA، Sparse Attention و MoE", "⤢"),
    (7, 39, "39-multimodal-transformer", "Transformer چندوجهی: اتصال رمزگذارهای تصویر و صوت", "▧"),
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
    if global_num == 44:
        project_code_path = ROOT / "book-engineering/projects/44-pretraining/pretraining_run.py"
        if not project_code_path.is_file():
            raise FileNotFoundError(project_code_path)
        code_blocks = re.findall(r"```python\n(.*?)\n```", text, flags=re.DOTALL)
        project_code = project_code_path.read_text(encoding="utf-8").rstrip()
        if not code_blocks or code_blocks[-1] != project_code:
            raise ValueError("chapter 44 executable appendix must match the tested pretraining project")
    if global_num == 45:
        project_code_path = ROOT / "book-engineering/projects/45-precision/precision_lab.py"
        if not project_code_path.is_file():
            raise FileNotFoundError(project_code_path)
        code_blocks = re.findall(r"```python\n(.*?)\n```", text, flags=re.DOTALL)
        project_code = project_code_path.read_text(encoding="utf-8").rstrip()
        if not code_blocks or code_blocks[-1] != project_code:
            raise ValueError("chapter 45 executable appendix must match the tested precision project")
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
    parser = argparse.ArgumentParser(description="Safely build authored volume 3 chapters")
    parser.add_argument(
        "--refresh-last-draft",
        action="store_true",
        help=("refresh only the last existing chapter after verifying it is not "
              "present on the remote branch; stable chapter/section IDs must match"),
    )
    args = parser.parse_args()
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
    refreshed_draft = None
    if matches:
        book = matches[0]
        existing = book.get("chapters", [])
        if len(existing) > len(chapters):
            raise RuntimeError("a published chapter source is missing; refusing to remove it")
        for index, old_chapter in enumerate(existing):
            if old_chapter != chapters[index]:
                same_stable_ids = (
                    old_chapter.get("id") == chapters[index].get("id")
                    and [section.get("id") for section in old_chapter.get("sections", [])]
                    == [section.get("id") for section in chapters[index]["sections"]]
                )
                is_last_existing_and_authored = (
                    index == len(existing) - 1 and index == len(chapters) - 1
                )
                if not (args.refresh_last_draft and same_stable_ids and is_last_existing_and_authored):
                    raise RuntimeError(
                        f"chapter {index + 1} differs from its source; only an explicitly refreshed "
                        "last local draft with unchanged stable IDs may be replaced"
                    )
                book["chapters"][index] = chapters[index]
                changed = True
                refreshed_draft = index + 1
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
    if refreshed_draft is not None:
        print(f"Refreshed only local draft chapter {refreshed_draft}; chapter and section IDs were unchanged.")


if __name__ == "__main__":
    main()
