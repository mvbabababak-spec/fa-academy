"""Structural, source, appendix, output and offline-cache checks for volume 4."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

import build_volume4 as builder

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data.json"
BOOK_ID = builder.VOLUME_ID


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    books = [book for book in data.get("books", []) if book.get("id") == BOOK_ID]
    _require(len(books) == 1, "data.json must contain exactly one volume 4 record")
    book = books[0]
    _require(book.get("title") == "هنر و علم ساخت هوش — جلد چهارم", "volume 4 title mismatch")
    _require(book.get("author") == "Babak & Ai", "volume 4 author metadata mismatch")
    v3_index = next((i for i, item in enumerate(data["books"]) if item.get("id") == "art-science-intelligence-v3"), None)
    v4_index = next((i for i, item in enumerate(data["books"]) if item.get("id") == BOOK_ID), None)
    _require(v3_index is not None and v4_index == v3_index + 1, "volume 4 must follow volume 3 in the reader")

    specs = builder.available_specs()
    expected_chapters = [builder.build_chapter(spec) for spec in specs]
    _require(bool(specs), "at least one volume 4 chapter must be authored")
    _require(book.get("chapters") == expected_chapters, "volume 4 data chapters do not match immutable Markdown sources")
    _require(len(book["chapters"]) <= builder.PLANNED_CHAPTERS, "more chapters than the roadmap defines")
    _require("۱۵ فصل در نقشه" in book.get("subtitle", ""), "volume 4 roadmap count missing")
    _require(f"{builder.fa_digits(len(book['chapters']))} فصل منتشرشده" in book.get("subtitle", ""), "published chapter count mismatch")

    source = ROOT / "book-engineering/chapters/47-posttraining.md"
    answer = ROOT / "book-engineering/answers/47-posttraining-fa.md"
    report = ROOT / "book-engineering/chapters/47-audit-report-fa.md"
    project = ROOT / "book-engineering/projects/47-instruction-tuning"
    for path in (source, answer, report, project / "README.md", project / "sft_experiment.py", project / "test_sft_experiment.py", project / "sample_sft.jsonl", project / "requirements-model-demo.txt"):
        _require(path.is_file(), f"missing chapter deliverable: {path.relative_to(ROOT)}")
    source_text = source.read_text(encoding="utf-8")
    _require("فصل محلی ۱ جلد چهارم = فصل سراسری ۴۷" in source_text, "local/global chapter mapping missing")
    _require("تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶" in source_text, "source review date missing")
    _require("## منابع و تاریخ بازبینی" in source_text, "dated bibliography missing")
    _require("## پیوست اجرایی" in source_text, "executable appendix heading missing")
    _require("cf967c0a9a04383db6f7b1108d86b2962634b4ac" in source_text, "pinned model revision missing")
    _require("کیفیت فارسی" in source_text and "هیچ ادعای کیفیت فارسی" in source_text, "model language limitation not explicit")
    _require("مخلوط‌کردن نام «SFT» با «RLHF»" in source_text, "scope boundary with chapter 49 missing")
    _require("فصل ۴۳" in source_text and "فصل ۴۴" in source_text, "prior-chapter boundaries missing")

    math_nodes = re.findall(r"<math\b[^>]*>", source_text)
    _require(bool(math_nodes), "chapter 47 must include accessible MathML")
    _require(all("aria-label=" in node for node in math_nodes), "every MathML expression needs aria-label")
    _require(source_text.count("**متن جایگزین فرمول:**") >= len(math_nodes), "every formula needs visible alternative text")
    image_matches = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source_text)
    _require(bool(image_matches), "chapter figure missing")
    for alt, image_path in image_matches:
        _require(bool(alt.strip()), "figure alternative text must be non-empty")
        _require((ROOT / image_path).is_file(), f"missing figure asset: {image_path}")
    svg_path = ROOT / "book-engineering/diagrams/v4-ch01-posttraining.svg"
    svg_root = ET.parse(svg_path).getroot()
    _require(svg_root.attrib.get("width") == "1600" and svg_root.attrib.get("height") == "1000", "SVG dimensions must be 1600x1000")
    _require("aria-labelledby" in svg_root.attrib, "SVG should expose its title/description")

    answer_text = answer.read_text(encoding="utf-8")
    _require("پاسخ‌نامهٔ تشریحی فصل ۴۷" in answer_text, "independent answer key heading missing")
    _require(len(answer_text.split()) >= 250, "answer key is too short to stand independently")
    report_text = report.read_text(encoding="utf-8")
    _require("نتایج اجرای واقعی" in report_text, "audit report must distinguish actual test results")

    source48 = ROOT / "book-engineering/chapters/48-peft.md"
    answer48 = ROOT / "book-engineering/answers/48-peft-fa.md"
    report48 = ROOT / "book-engineering/chapters/48-audit-report-fa.md"
    project48 = ROOT / "book-engineering/projects/48-peft-lab"
    for path in (source48, answer48, report48, project48 / "README.md", project48 / "peft_lab.py", project48 / "test_peft_lab.py", project48 / "sample_layers.json"):
        _require(path.is_file(), f"missing chapter 48 deliverable: {path.relative_to(ROOT)}")
    source48_text = source48.read_text(encoding="utf-8")
    _require("فصل محلی ۲ جلد چهارم = فصل سراسری ۴۸" in source48_text, "chapter 48 local/global mapping missing")
    _require("تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶" in source48_text, "chapter 48 source review date missing")
    _require(bool(re.search(r"^##\s+.*منابع و تاریخ بازبینی", source48_text, flags=re.MULTILINE)), "chapter 48 dated bibliography missing")
    _require("PEFT" in source48_text and "Adapter" in source48_text and "QLoRA" in source48_text, "chapter 48 scope terms missing")
    _require("فصل ۴۷" in source48_text and "فصل ۴۹" in source48_text, "chapter 48 boundaries with adjacent chapters missing")
    math48 = re.findall(r"<math\b[^>]*>", source48_text)
    _require(bool(math48), "chapter 48 must include accessible MathML")
    _require(all("aria-label=" in node for node in math48), "chapter 48 MathML needs aria-label")
    _require(source48_text.count("**متن جایگزین فرمول:**") >= len(math48), "chapter 48 formulas need visible alternatives")
    for alt, image_path in re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source48_text):
        _require(bool(alt.strip()), "chapter 48 figure alternative text must be non-empty")
        _require((ROOT / image_path).is_file(), f"missing chapter 48 figure: {image_path}")
    svg48 = ET.parse(ROOT / "book-engineering/diagrams/v4-ch02-peft.svg").getroot()
    _require(svg48.attrib.get("width") == "1600" and svg48.attrib.get("height") == "1000", "chapter 48 SVG dimensions mismatch")
    _require("aria-labelledby" in svg48.attrib, "chapter 48 SVG must have accessible title/description")
    answer48_text = answer48.read_text(encoding="utf-8")
    _require("پاسخ‌نامهٔ تشریحی فصل ۴۸" in answer48_text and len(answer48_text.split()) >= 250, "chapter 48 independent answer key missing or too short")
    report48_text = report48.read_text(encoding="utf-8")
    _require("نتایج اجرای واقعی" in report48_text, "chapter 48 audit report must distinguish actual tests")
    _require("۱۴ آزمون از ۱۴ آزمون موفق" in report48_text, "chapter 48 report must record the actual unit-test result")
    _require(all(value in report48_text for value in ("۵٬۱۲۰", "۸۳۲", "۲٬۵۶۰")), "chapter 48 report must record fixture counts and payload lower bound")
    _require("1.0780806292132183e-07" in report48_text and "2.086162567138672e-07" in report48_text, "chapter 48 report must record exact synthetic demo outcomes")
    _require("test_volume4.py" in report48_text and "test_mobile_layout.py" in report48_text, "chapter 48 report must record browser/mobile integration results")
    _require("GPU/NCCL" in report48_text and "کیفیت" in report48_text, "chapter 48 report must state its claim limits")
    code48 = (project48 / "peft_lab.py").read_text(encoding="utf-8").rstrip()
    blocks48 = re.findall(r"```python\n(.*?)\n```", source48_text, flags=re.DOTALL)
    _require(bool(blocks48) and blocks48[-1] == code48, "chapter 48 appendix and tested project must match byte-for-byte")
    rows48 = json.loads((project48 / "sample_layers.json").read_text(encoding="utf-8"))
    _require(len(rows48) == 3, "chapter 48 synthetic shape fixture row count changed")

    code = (project / "sft_experiment.py").read_text(encoding="utf-8").rstrip()
    blocks = re.findall(r"```python\n(.*?)\n```", source_text, flags=re.DOTALL)
    _require(bool(blocks) and blocks[-1] == code, "chapter appendix and tested project must be byte-for-byte equal")
    sample_rows = [line for line in (project / "sample_sft.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    _require(len(sample_rows) == 15, "fixture row count changed; update the documented and tested counts")
    for line_no, line in enumerate(sample_rows, 1):
        row = json.loads(line)
        _require(all(isinstance(row.get(field), str) and row[field].strip() for field in ("id", "source_id", "group_id", "prompt", "completion")), f"invalid fixture row {line_no}")

    markdown_path = ROOT / "volume-4-full-fa.md"
    _require(markdown_path.is_file(), "volume-4-full-fa.md missing")
    _require(markdown_path.read_text(encoding="utf-8") == builder.expected_markdown(expected_chapters, specs), "full Markdown does not match chapter sources")
    sw = (ROOT / "sw.js").read_text(encoding="utf-8")
    _require("fa-academy-v78" in sw and "v77" not in sw.splitlines()[0], "service worker cache version was not advanced")
    required_cache_paths = (
        "./volume-4-full-fa.md",
        "./book-engineering/diagrams/v4-ch01-posttraining.svg",
        "./book-engineering/chapters/47-posttraining.md",
        "./book-engineering/chapters/47-audit-report-fa.md",
        "./book-engineering/answers/47-posttraining-fa.md",
        "./book-engineering/projects/47-instruction-tuning/README.md",
        "./book-engineering/projects/47-instruction-tuning/sft_experiment.py",
        "./book-engineering/projects/47-instruction-tuning/test_sft_experiment.py",
        "./book-engineering/projects/47-instruction-tuning/sample_sft.jsonl",
        "./book-engineering/projects/47-instruction-tuning/requirements-model-demo.txt",
        "./book-engineering/diagrams/v4-ch02-peft.svg",
        "./book-engineering/chapters/48-peft.md",
        "./book-engineering/chapters/48-audit-report-fa.md",
        "./book-engineering/answers/48-peft-fa.md",
        "./book-engineering/projects/48-peft-lab/README.md",
        "./book-engineering/projects/48-peft-lab/peft_lab.py",
        "./book-engineering/projects/48-peft-lab/test_peft_lab.py",
        "./book-engineering/projects/48-peft-lab/sample_layers.json",
    )
    for item in required_cache_paths:
        _require(item in sw, f"service worker does not precache {item}")

    print(
        f"PASS volume 4: {len(book['chapters'])}/{builder.PLANNED_CHAPTERS} chapters, "
        f"{sum(len(ch['sections']) for ch in book['chapters'])} sections, "
        f"{len(math_nodes) + len(math48)} accessible MathML expressions, exact appendices, reports/answers/fixtures present"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL volume 4: {exc}", file=sys.stderr)
        raise
