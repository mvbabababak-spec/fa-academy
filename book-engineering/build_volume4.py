"""Append contiguous, authored volume 4 chapters without rewriting published ones.

Volume 4 maps local chapters 1–15 to roadmap chapters 47–61. Existing chapter
payloads are immutable by default. After independently verifying that the final
existing chapter is not on the remote branch, --refresh-last-draft may replace
only that local draft, and only when all stable IDs remain unchanged.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import mistune

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data.json"
VOLUME_ID = "art-science-intelligence-v4"
PLANNED_CHAPTERS = 15
PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
RENDER = mistune.create_markdown(escape=False, plugins=["table"])


def fa_digits(value: int) -> str:
    return str(value).translate(PERSIAN_DIGITS)


# Local volume numbering 1–15 maps to roadmap chapters 47–61.
SPECS = [
    (1, 47, "47-posttraining", "Continued Pretraining، Instruction Tuning و SFT", "↻"),
    (2, 48, "48-peft", "PEFT، Adapter، LoRA و QLoRA", "⌁"),
    (3, 49, "49-preference-optimization", "مدل پاداش، RLHF، PPO، DPO، GRPO و RLAIF", "◇"),
    (4, 50, "50-synthetic-reasoning", "دادهٔ مصنوعی، تقطیر و محاسبهٔ زمان آزمون", "∴"),
    (5, 51, "51-vision-models", "مدل‌های تصویر و هم‌ترازی متن–تصویر", "▧"),
    (6, 52, "52-audio-models", "مدل‌های صوت و گفتار", "♫"),
    (7, 53, "53-image-video-generation", "تولید تصویر و ویدئو و Diffusion", "▨"),
    (8, 54, "54-resource-estimation", "برآورد منابع استنتاج، Fine-tuning و آموزش", "⌗"),
    (9, 55, "55-ai-lab-design", "طراحی آزمایشگاه کم‌هزینه تا سازمانی", "⌂"),
    (10, 56, "56-ai-compute-budget", "بودجه و هزینهٔ مالکیت محاسبات", "¤"),
    (11, 57, "57-ml-frameworks", "Python، PyTorch، JAX و TensorFlow", "⚙"),
    (12, 58, "58-huggingface-stack", "اکوسیستم Hugging Face", "⬡"),
    (13, 59, "59-gpu-systems", "CUDA، ROCm، Triton و مقیاس‌پذیری", "⇧"),
    (14, 60, "60-mlops", "ردیابی آزمایش و ابزارهای MLOps", "⌘"),
    (15, 61, "61-inference-serving", "سرو و بهینه‌سازی استنتاج", "⇢"),
]


APPENDIX_PROJECTS = {
    47: "book-engineering/projects/47-instruction-tuning/sft_experiment.py",
    48: "book-engineering/projects/48-peft-lab/peft_lab.py",
    49: "book-engineering/projects/49-preference-lab/preference_lab.py",
    50: "book-engineering/projects/50-synthetic-reasoning/reasoning_lab.py",
    51: "book-engineering/projects/51-vision-lab/vision_lab.py",
    52: "book-engineering/projects/52-audio-lab/audio_lab.py",
    53: "book-engineering/projects/53-diffusion-lab/diffusion_lab.py",
    54: "book-engineering/projects/54-resource-estimation/resource_estimator.py",
    55: "book-engineering/projects/55-ai-lab-design/lab_design_planner.py",
    56: "book-engineering/projects/56-ai-compute-budget/budget_model.py",
    57: "book-engineering/projects/57-framework-lab/framework_compare.py",
    58: "book-engineering/projects/58-huggingface-stack/pipeline_demo.py",
}


def _verify_code_appendix(global_num: int, text: str) -> None:
    relative = APPENDIX_PROJECTS.get(global_num)
    if relative is None:
        return
    project_code_path = ROOT / relative
    if not project_code_path.is_file():
        raise FileNotFoundError(project_code_path)
    if global_num in {55, 56, 57, 58}:
        # Recent chapter appendices include every source byte and final newline.
        marker = b"\n```python\n"
        _, found, tail = text.encode("utf-8").rpartition(marker)
        closing = tail.rfind(b"```")
        project_code = project_code_path.read_bytes()
        if not found or closing < 0 or tail[:closing] != project_code or tail[closing + 3:] not in (b"", b"\n"):
            raise ValueError(f"chapter {global_num} executable appendix must match its tested project byte-for-byte")
        return
    code_blocks = re.findall(r"```python\n(.*?)\n```", text, flags=re.DOTALL)
    project_code = project_code_path.read_text(encoding="utf-8").rstrip()
    if not code_blocks or code_blocks[-1] != project_code:
        raise ValueError(f"chapter {global_num} executable appendix must match its tested project byte-for-byte")


def build_chapter(spec: tuple[int, int, str, str, str]) -> dict:
    local_num, global_num, slug, title, icon = spec
    relative = f"book-engineering/chapters/{slug}.md"
    source = ROOT / relative
    if not source.is_file():
        raise FileNotFoundError(source)
    text = source.read_text(encoding="utf-8")
    _verify_code_appendix(global_num, text)
    parts = re.split(r"^## (.+)$", text, flags=re.MULTILINE)
    if len(parts) < 3:
        raise ValueError(f"chapter {global_num} must contain at least one H2 section")
    sections = []
    for section_no, index in enumerate(range(1, len(parts), 2), 1):
        body = (parts[0] + "\n" if index == 1 else "") + "## " + parts[index] + "\n" + parts[index + 1]
        html = RENDER(body)
        if not html.strip():
            raise ValueError(f"empty rendered section {global_num}.{section_no}")
        sections.append({
            "id": f"art-science-v4-ch{local_num:02}-s{section_no:02}",
            "title": parts[index].strip(),
            "file": relative,
            "html": html,
        })
    return {
        "num": local_num,
        "id": f"art-science-v4-ch{local_num:02}",
        "title": title,
        "icon": icon,
        "sections": sections,
    }


def available_specs() -> list[tuple[int, int, str, str, str]]:
    authored = [spec for spec in SPECS if (ROOT / "book-engineering/chapters" / f"{spec[2]}.md").is_file()]
    expected = list(range(1, len(authored) + 1))
    if [spec[0] for spec in authored] != expected:
        raise RuntimeError("volume 4 source chapters must be authored in order without gaps")
    return authored


def expected_markdown(chapters: list[dict], specs: list[tuple[int, int, str, str, str]]) -> str:
    contents = [
        "# هنر و علم ساخت هوش — جلد چهارم",
        "",
        "**The Art & Science of Building Intelligence | Babak & Ai**",
        "",
        f"وضعیت: ۱۵ فصل در نقشه؛ {fa_digits(len(chapters))} فصل از ۱۵ فصل تا این انتشار نگارش، آزموده و منتشر شده‌اند. این فایل Markdown است؛ PDF و EPUB تولید و آزموده نشده‌اند.",
        "",
        "## فهرست فصل‌های منتشرشده",
        "",
    ]
    for chapter, spec in zip(chapters, specs):
        _, global_num, _, title, _ = spec
        contents.append(f"- فصل {fa_digits(chapter['num'])} (سراسری {fa_digits(global_num)}) — {title}")
    contents.append("")
    for spec in specs:
        source_path = ROOT / "book-engineering/chapters" / f"{spec[2]}.md"
        contents.extend(["---", "", source_path.read_text(encoding="utf-8").rstrip(), ""])
    return "\n".join(contents).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Safely build authored volume 4 chapters")
    parser.add_argument(
        "--refresh-last-draft",
        action="store_true",
        help=("refresh only the last local draft after verifying it is absent from the remote branch; "
              "chapter and section IDs must remain unchanged"),
    )
    args = parser.parse_args()
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    specs = available_specs()
    if not specs:
        raise RuntimeError("no authored volume 4 chapter source found")
    chapters = [build_chapter(spec) for spec in specs]

    matches = [book for book in data["books"] if book.get("id") == VOLUME_ID]
    if len(matches) > 1:
        raise RuntimeError("duplicate volume 4 book records")
    subtitle = "پس‌آموزش، چندوجهی و زیرساخت | ۱۵ فصل"
    changed = False
    refreshed_draft = None
    if matches:
        book = matches[0]
        existing = book.get("chapters", [])
        if len(existing) > len(chapters):
            raise RuntimeError("a published volume 4 chapter source is missing; refusing to remove it")
        for index, old_chapter in enumerate(existing):
            if old_chapter != chapters[index]:
                same_stable_ids = (
                    old_chapter.get("id") == chapters[index].get("id")
                    and [section.get("id") for section in old_chapter.get("sections", [])]
                    == [section.get("id") for section in chapters[index].get("sections", [])]
                )
                is_last_existing_and_authored = index == len(existing) - 1 and index == len(chapters) - 1
                if not (args.refresh_last_draft and same_stable_ids and is_last_existing_and_authored):
                    raise RuntimeError(
                        f"published volume 4 chapter {index + 1} differs from its source; refusing to rewrite it"
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
        if book.get("author") != "Babak Moradvand":
            book["author"] = "Babak Moradvand"
            changed = True
    else:
        v3_index = next(
            (index for index, book in enumerate(data["books"])
             if book.get("id") == "art-science-intelligence-v3"),
            None,
        )
        if v3_index is None:
            raise RuntimeError("volume 3 book record not found; refusing to place volume 4 out of sequence")
        book = {
            "id": VOLUME_ID,
            "title": "هنر و علم ساخت هوش — جلد چهارم",
            "subtitle": subtitle,
            "author": "Babak Moradvand",
            "cover": "assets/images/art-science-cover.webp",
            "chapters": chapters,
        }
        data["books"].insert(v3_index + 1, book)
        changed = True

    if changed:
        DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    markdown = expected_markdown(chapters, specs)
    output_path = ROOT / "volume-4-full-fa.md"
    if not output_path.is_file() or output_path.read_text(encoding="utf-8") != markdown:
        output_path.write_text(markdown, encoding="utf-8")
    print(
        f"Volume 4 {'updated' if changed else 'already matches'}: "
        f"{len(chapters)}/{PLANNED_CHAPTERS} chapters; sections={[len(ch['sections']) for ch in chapters]}"
    )
    if refreshed_draft is not None:
        print(f"Refreshed only local unpublished draft chapter {refreshed_draft}; stable IDs were unchanged.")


if __name__ == "__main__":
    main()
