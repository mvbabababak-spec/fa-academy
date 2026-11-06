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

    source49 = ROOT / "book-engineering/chapters/49-preference-optimization.md"
    answer49 = ROOT / "book-engineering/answers/49-preference-optimization-fa.md"
    report49 = ROOT / "book-engineering/chapters/49-audit-report-fa.md"
    diagram49 = ROOT / "book-engineering/diagrams/v4-ch03-preference.svg"
    project49 = ROOT / "book-engineering/projects/49-preference-lab"
    for path in (source49, answer49, report49, diagram49, project49 / "README.md", project49 / "preference_lab.py", project49 / "test_preference_lab.py", project49 / "sample_preferences.jsonl", project49 / "results.json"):
        _require(path.is_file(), f"missing chapter 49 deliverable: {path.relative_to(ROOT)}")
    source49_text = source49.read_text(encoding="utf-8")
    _require("فصل محلی ۳ جلد چهارم = فصل سراسری ۴۹" in source49_text, "chapter 49 local/global mapping missing")
    _require("تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶" in source49_text, "chapter 49 source review date missing")
    _require(bool(re.search(r"^##\s+.*منابع و تاریخ بازبینی", source49_text, flags=re.MULTILINE)), "chapter 49 dated bibliography missing")
    _require(all(term in source49_text for term in ("RLHF", "PPO", "DPO", "GRPO", "RLAIF", "Constitutional AI")), "chapter 49 roadmap topics missing")
    _require("فصل ۴۸" in source49_text and "فصل بعد" in source49_text, "chapter 49 adjacent-chapter boundaries missing")
    _require("TRL v1.17.1" in source49_text and "PPOTrainer" in source49_text and "v1.13.0" in source49_text, "chapter 49 versioned TRL caveat missing")
    _require("GPU/NCCL" in source49_text and "کیفیت" in source49_text, "chapter 49 claim boundaries missing")
    math49 = re.findall(r"<math\b[^>]*>", source49_text)
    _require(len(math49) >= 4, "chapter 49 should explain the core objectives with MathML")
    _require(all("aria-label=" in node for node in math49), "chapter 49 MathML needs aria-label")
    _require(source49_text.count("**متن جایگزین فرمول:**") >= len(math49), "chapter 49 formulas need visible alternatives")
    figure49 = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source49_text)
    _require(bool(figure49), "chapter 49 figure missing")
    for alt, image_path in figure49:
        _require(bool(alt.strip()), "chapter 49 figure alternative text must be non-empty")
        _require((ROOT / image_path).is_file(), f"missing chapter 49 figure: {image_path}")
    svg49 = ET.parse(diagram49).getroot()
    _require(svg49.attrib.get("width") == "1600" and svg49.attrib.get("height") == "1000", "chapter 49 SVG dimensions mismatch")
    _require("aria-labelledby" in svg49.attrib, "chapter 49 SVG must expose title and description")
    answer49_text = answer49.read_text(encoding="utf-8")
    _require("پاسخ‌نامهٔ تشریحی فصل ۴۹" in answer49_text and len(answer49_text.split()) >= 250, "chapter 49 independent answer key missing or too short")
    report49_text = report49.read_text(encoding="utf-8")
    _require("نتایج اجرای واقعی" in report49_text, "chapter 49 audit report must distinguish actual tests")
    _require("۲۲/۲۲ آزمون موفق" in report49_text, "chapter 49 report must record the actual unit-test result")
    _require("629b48e6a9c3f3a8d6c336eadbb1f3833b988348c1b11f1022221db121fc21bb" in report49_text, "chapter 49 report must record the fixture hash")
    _require("0.12939360737800598" in report49_text and "0.9999496936798096" in report49_text, "chapter 49 report must record exact toy outcomes")
    _require("test_volume4.py" in report49_text and "test_mobile_layout.py" in report49_text, "chapter 49 report must record browser/mobile results")
    code49 = (project49 / "preference_lab.py").read_text(encoding="utf-8").rstrip()
    blocks49 = re.findall(r"```python\n(.*?)\n```", source49_text, flags=re.DOTALL)
    _require(bool(blocks49) and blocks49[-1] == code49, "chapter 49 appendix and tested project must match byte-for-byte")
    rows49 = [json.loads(line) for line in (project49 / "sample_preferences.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    _require(len(rows49) == 12 and all(row["label_source"] == "synthetic_fixture" for row in rows49), "chapter 49 synthetic preference fixture changed")
    results49 = json.loads((project49 / "results.json").read_text(encoding="utf-8"))
    _require(results49["unit_tests"]["passed"] == 22 and results49["unit_tests"]["failed"] == 0, "chapter 49 result manifest test count mismatch")
    _require(results49["audit"]["sha256"] == "629b48e6a9c3f3a8d6c336eadbb1f3833b988348c1b11f1022221db121fc21bb", "chapter 49 result manifest fixture hash mismatch")

    source50 = ROOT / "book-engineering/chapters/50-synthetic-reasoning.md"
    answer50 = ROOT / "book-engineering/answers/50-synthetic-reasoning-fa.md"
    report50 = ROOT / "book-engineering/chapters/50-audit-report-fa.md"
    diagram50 = ROOT / "book-engineering/diagrams/v4-ch04-synthetic-reasoning.svg"
    project50 = ROOT / "book-engineering/projects/50-synthetic-reasoning"
    for path in (source50, answer50, report50, diagram50, project50 / "README.md", project50 / "reasoning_lab.py", project50 / "test_reasoning_lab.py", project50 / "sample_traces.jsonl", project50 / "results.json"):
        _require(path.is_file(), f"missing chapter 50 deliverable: {path.relative_to(ROOT)}")
    source50_text = source50.read_text(encoding="utf-8")
    _require("فصل محلی ۴ جلد چهارم = فصل سراسری ۵۰" in source50_text, "chapter 50 local/global mapping missing")
    _require("تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶" in source50_text, "chapter 50 source review date missing")
    _require(bool(re.search(r"^##\s+.*منابع و تاریخ بازبینی", source50_text, flags=re.MULTILINE)), "chapter 50 dated bibliography missing")
    _require(all(term in source50_text for term in ("دادهٔ مصنوعی", "تقطیر", "Curriculum Learning", "محاسبهٔ زمان آزمون", "DeepSeek-R1")), "chapter 50 roadmap topics missing")
    _require("فصل ۴۹" in source50_text and "فصل بعد" in source50_text, "chapter 50 adjacent-chapter boundaries missing")
    math50 = re.findall(r"<math\b[^>]*>", source50_text)
    _require(len(math50) >= 4, "chapter 50 should explain core formulas with MathML")
    _require(all("aria-label=" in node for node in math50), "chapter 50 MathML needs aria-label")
    _require(source50_text.count("**متن جایگزین فرمول:**") >= len(math50), "chapter 50 formulas need visible alternatives")
    figures50 = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source50_text)
    _require(bool(figures50), "chapter 50 figure missing")
    for alt, image_path in figures50:
        _require(bool(alt.strip()), "chapter 50 figure alternative text must be non-empty")
        _require((ROOT / image_path).is_file(), f"missing chapter 50 figure: {image_path}")
    svg50 = ET.parse(diagram50).getroot()
    _require(svg50.attrib.get("width") == "1600" and svg50.attrib.get("height") == "1000", "chapter 50 SVG dimensions mismatch")
    _require("aria-labelledby" in svg50.attrib, "chapter 50 SVG must expose title and description")
    answer50_text = answer50.read_text(encoding="utf-8")
    _require("پاسخ‌نامهٔ تشریحی فصل ۵۰" in answer50_text and len(answer50_text.split()) >= 250, "chapter 50 independent answer key missing or too short")
    report50_text = report50.read_text(encoding="utf-8")
    _require("نتایج اجرای واقعی" in report50_text, "chapter 50 audit report must distinguish actual tests")
    _require("۲۶/۲۶ آزمون موفق" in report50_text, "chapter 50 report must record the actual unit-test result")
    _require("1654621020c9dd2175cf0d7f66cb14ed78a3d192667c7e79ce7571219f47a075" in report50_text, "chapter 50 report must record the fixture hash")
    _require("0.2875792384147644" in report50_text and "125" in report50_text, "chapter 50 report must record exact demo outputs")
    _require("test_volume4.py" in report50_text and "test_mobile_layout.py" in report50_text, "chapter 50 report must record browser/mobile results")
    _require("GPU" in report50_text and "کیفیت فارسی" in report50_text, "chapter 50 report must state its claim limits")
    code50 = (project50 / "reasoning_lab.py").read_text(encoding="utf-8").rstrip()
    blocks50 = re.findall(r"```python\n(.*?)\n```", source50_text, flags=re.DOTALL)
    _require(bool(blocks50) and blocks50[-1] == code50, "chapter 50 appendix and tested project must match byte-for-byte")
    rows50 = [json.loads(line) for line in (project50 / "sample_traces.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    _require(len(rows50) == 12 and all(row["label_source"] == "synthetic_fixture" for row in rows50), "chapter 50 synthetic fixture changed")
    results50 = json.loads((project50 / "results.json").read_text(encoding="utf-8"))
    _require(results50["unit_tests"]["passed"] == 26 and results50["unit_tests"]["failed"] == 0, "chapter 50 result manifest test count mismatch")
    _require(results50["fixture"]["sha256"] == "1654621020c9dd2175cf0d7f66cb14ed78a3d192667c7e79ce7571219f47a075", "chapter 50 result manifest fixture hash mismatch")

    source51 = ROOT / "book-engineering/chapters/51-vision-models.md"
    answer51 = ROOT / "book-engineering/answers/51-vision-models-fa.md"
    report51 = ROOT / "book-engineering/chapters/51-audit-report-fa.md"
    diagram51 = ROOT / "book-engineering/diagrams/v4-ch05-vision.svg"
    project51 = ROOT / "book-engineering/projects/51-vision-lab"
    for path in (source51, answer51, report51, diagram51, project51 / "README.md", project51 / "vision_lab.py", project51 / "test_vision_lab.py", project51 / "sample_embeddings.json", project51 / "results.json"):
        _require(path.is_file(), f"missing chapter 51 deliverable: {path.relative_to(ROOT)}")
    source51_text = source51.read_text(encoding="utf-8")
    _require("فصل محلی ۵ جلد چهارم = فصل سراسری ۵۱" in source51_text, "chapter 51 local/global mapping missing")
    _require("تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶" in source51_text, "chapter 51 source review date missing")
    _require(bool(re.search(r"^##\s+.*منابع و تاریخ بازبینی", source51_text, flags=re.MULTILINE)), "chapter 51 dated bibliography missing")
    _require(all(term in source51_text for term in ("Vision Transformer", "image encoder", "CLIP", "SigLIP", "Recall@k", "DINOv3")), "chapter 51 roadmap topics missing")
    _require("فصل ۵۰" in source51_text and "فصل ۵۲" in source51_text, "chapter 51 adjacent-chapter boundaries missing")
    math51 = re.findall(r"<math\b[^>]*>", source51_text)
    _require(len(math51) >= 4, "chapter 51 should explain core formulas with MathML")
    _require(all("aria-label=" in node for node in math51), "chapter 51 MathML needs aria-label")
    _require(source51_text.count("**متن جایگزین فرمول:**") >= len(math51), "chapter 51 formulas need visible alternatives")
    figures51 = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source51_text)
    _require(bool(figures51), "chapter 51 figure missing")
    for alt, image_path in figures51:
        _require(bool(alt.strip()), "chapter 51 figure alternative text must be non-empty")
        _require((ROOT / image_path).is_file(), f"missing chapter 51 figure: {image_path}")
    svg51 = ET.parse(diagram51).getroot()
    _require(svg51.attrib.get("width") == "1600" and svg51.attrib.get("height") == "1000", "chapter 51 SVG dimensions mismatch")
    _require("aria-labelledby" in svg51.attrib, "chapter 51 SVG must expose title and description")
    answer51_text = answer51.read_text(encoding="utf-8")
    _require("پاسخ‌نامهٔ تشریحی فصل ۵۱" in answer51_text and len(answer51_text.split()) >= 250, "chapter 51 independent answer key missing or too short")
    report51_text = report51.read_text(encoding="utf-8")
    _require("نتایج اجرای واقعی" in report51_text, "chapter 51 audit report must distinguish actual test results")
    _require("۲۶/۲۶ آزمون موفق" in report51_text, "chapter 51 report must record the actual unit-test result")
    _require("aba309bb1b3e69443802190b988a21e0432109c01b777f4f58fe11f992936522" in report51_text, "chapter 51 report must record the fixture hash")
    _require("0.00024217297323048115" in report51_text and "15.878404493802984" in report51_text, "chapter 51 report must record exact synthetic demo outputs")
    _require("test_volume4.py" in report51_text and "test_mobile_layout.py" in report51_text, "chapter 51 report must record browser/mobile integration results")
    _require("GPU" in report51_text and "کیفیت فارسی" in report51_text, "chapter 51 report must state its claim limits")
    code51 = (project51 / "vision_lab.py").read_text(encoding="utf-8").rstrip()
    blocks51 = re.findall(r"```python\n(.*?)\n```", source51_text, flags=re.DOTALL)
    _require(bool(blocks51) and blocks51[-1] == code51, "chapter 51 appendix and tested project must match byte-for-byte")
    fixture51 = json.loads((project51 / "sample_embeddings.json").read_text(encoding="utf-8"))
    _require(len(fixture51["images"]) == 4 and len(fixture51["texts"]) == 4, "chapter 51 synthetic fixture row count changed")
    _require(all(row["label_source"] == "synthetic_fixture" for kind in ("images", "texts") for row in fixture51[kind]), "chapter 51 fixture source labels changed")
    results51 = json.loads((project51 / "results.json").read_text(encoding="utf-8"))
    _require(results51["unit_tests"]["passed"] == 26 and results51["unit_tests"]["failed"] == 0, "chapter 51 result manifest test count mismatch")
    _require(results51["audit"]["sha256"] == "aba309bb1b3e69443802190b988a21e0432109c01b777f4f58fe11f992936522", "chapter 51 result manifest fixture hash mismatch")
    _require(results51["demo"]["training_performed"] is False and results51["demo"]["image_files_loaded"] is False, "chapter 51 result manifest must disclaim training and image loading")

    source52 = ROOT / "book-engineering/chapters/52-audio-models.md"
    answer52 = ROOT / "book-engineering/answers/52-audio-models-fa.md"
    report52 = ROOT / "book-engineering/chapters/52-audit-report-fa.md"
    diagram52 = ROOT / "book-engineering/diagrams/v4-ch06-audio.svg"
    project52 = ROOT / "book-engineering/projects/52-audio-lab"
    for path in (source52, answer52, report52, diagram52, project52 / "README.md", project52 / "audio_lab.py", project52 / "test_audio_lab.py", project52 / "sample_transcripts.json", project52 / "results.json"):
        _require(path.is_file(), f"missing chapter 52 deliverable: {path.relative_to(ROOT)}")
    source52_text = source52.read_text(encoding="utf-8")
    _require("فصل محلی ۶ جلد چهارم = فصل سراسری ۵۲" in source52_text, "chapter 52 local/global mapping missing")
    _require("تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶" in source52_text, "chapter 52 source review date missing")
    _require(bool(re.search(r"^##\s+.*منابع و تاریخ بازبینی", source52_text, flags=re.MULTILINE)), "chapter 52 dated bibliography missing")
    _require(all(term in source52_text for term in ("ASR", "TTS", "Audio-Language", "WER", "CER", "Moshi", "Qwen3-TTS", "AudioBench")), "chapter 52 roadmap topics missing")
    _require("فصل ۳۹" in source52_text and "فصل ۵۱" in source52_text and "فصل ۵۳" in source52_text, "chapter 52 boundaries with neighboring material missing")
    math52 = re.findall(r"<math\b[^>]*>", source52_text)
    _require(len(math52) >= 5, "chapter 52 should explain core formulas with MathML")
    _require(all("aria-label=" in node for node in math52), "chapter 52 MathML needs aria-label")
    _require(source52_text.count("**متن جایگزین فرمول:**") >= len(math52), "chapter 52 formulas need visible alternatives")
    figures52 = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source52_text)
    _require(bool(figures52), "chapter 52 figure missing")
    for alt, image_path in figures52:
        _require(bool(alt.strip()), "chapter 52 figure alternative text must be non-empty")
        _require((ROOT / image_path).is_file(), f"missing chapter 52 figure: {image_path}")
    svg52 = ET.parse(diagram52).getroot()
    _require(svg52.attrib.get("width") == "1600" and svg52.attrib.get("height") == "1000", "chapter 52 SVG dimensions mismatch")
    _require("aria-labelledby" in svg52.attrib, "chapter 52 SVG must expose title and description")
    answer52_text = answer52.read_text(encoding="utf-8")
    _require("پاسخ‌نامهٔ تشریحی فصل ۵۲" in answer52_text and len(answer52_text.split()) >= 250, "chapter 52 independent answer key missing or too short")
    report52_text = report52.read_text(encoding="utf-8")
    _require("نتایج اجرای واقعی" in report52_text, "chapter 52 audit report must distinguish actual test results")
    _require("۳۹/۳۹ آزمون موفق" in report52_text, "chapter 52 report must record the actual unit-test result")
    fixture52_hash = "46abd6b35e1481e0b3796522056d25168f7cc1823e0059fafc9a544dd5fdf347"
    _require(fixture52_hash in report52_text, "chapter 52 report must record the fixture hash")
    _require("0.2727272727272727" in report52_text and "0.21666666666666667" in report52_text and ("440 Hz" in report52_text or "۴۴۰ Hz" in report52_text), "chapter 52 report must record exact demo outcomes")
    _require("test_volume4.py" in report52_text and "test_mobile_layout.py" in report52_text, "chapter 52 report must record browser/mobile integration results")
    _require("مدل" in report52_text and "فارسی" in report52_text and "آموزش" in report52_text, "chapter 52 report must state its claim limits")
    code52 = (project52 / "audio_lab.py").read_text(encoding="utf-8").rstrip()
    blocks52 = re.findall(r"```python\n(.*?)\n```", source52_text, flags=re.DOTALL)
    _require(bool(blocks52) and blocks52[-1] == code52, "chapter 52 appendix and tested project must be byte-for-byte equal")
    fixture52 = json.loads((project52 / "sample_transcripts.json").read_text(encoding="utf-8"))
    _require(len(fixture52["records"]) == 3 and all(row["label_source"] == "synthetic_fixture" for row in fixture52["records"]), "chapter 52 synthetic fixture rows changed")
    _require(fixture52["metadata"]["audio_recordings_included"] is False and fixture52["metadata"]["model_outputs_included"] is False, "chapter 52 fixture must disclaim audio/model outputs")
    results52 = json.loads((project52 / "results.json").read_text(encoding="utf-8"))
    _require(results52["unit_tests"]["passed"] == 39 and results52["unit_tests"]["failed"] == 0, "chapter 52 result manifest test count mismatch")
    _require(results52["audit"]["fixture"]["sha256"] == fixture52_hash and results52["demo"]["fixture"]["sha256"] == fixture52_hash, "chapter 52 result manifest fixture hash mismatch")
    _require(results52["demo"]["training_performed"] is False and results52["demo"]["audio_recordings_loaded"] is False and results52["demo"]["speech_model_loaded"] is False, "chapter 52 result manifest must disclaim training, audio, and model loading")
    _require(results52["demo"]["analytic_tone"]["sample_count"] == 1600 and results52["demo"]["analytic_tone"]["complete_frames_without_tail_padding"] == 8, "chapter 52 result manifest framing values mismatch")
    _require(results52["demo"]["transcript_metrics"]["wer"]["error_rate"] == 3 / 11 and results52["demo"]["transcript_metrics"]["sentence_macro_wer"] == 0.21666666666666667, "chapter 52 result manifest metric values mismatch")

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
    _require("fa-academy-v83" in sw and "v82" not in sw.splitlines()[0], "service worker cache version was not advanced")
    cover_paths = {
        f"art-science-intelligence-v{volume}": f"assets/images/covers/volume-{volume}-cover.webp"
        for volume in range(1, 5)
    }
    for volume_id, expected_cover in cover_paths.items():
        rows = [item for item in data.get("books", []) if item.get("id") == volume_id]
        _require(len(rows) == 1 and rows[0].get("cover") == expected_cover,
                 f"{volume_id} must reference its mapped local cover {expected_cover}")
        cover_file = ROOT / expected_cover
        _require(cover_file.is_file() and cover_file.stat().st_size > 0,
                 f"missing cover image {expected_cover}")
    required_cache_paths = (
        "./assets/images/covers/volume-1-cover.webp",
        "./assets/images/covers/volume-2-cover.webp",
        "./assets/images/covers/volume-3-cover.webp",
        "./assets/images/covers/volume-4-cover.webp",
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
        "./book-engineering/diagrams/v4-ch03-preference.svg",
        "./book-engineering/chapters/49-preference-optimization.md",
        "./book-engineering/chapters/49-audit-report-fa.md",
        "./book-engineering/answers/49-preference-optimization-fa.md",
        "./book-engineering/projects/49-preference-lab/README.md",
        "./book-engineering/projects/49-preference-lab/preference_lab.py",
        "./book-engineering/projects/49-preference-lab/test_preference_lab.py",
        "./book-engineering/projects/49-preference-lab/sample_preferences.jsonl",
        "./book-engineering/projects/49-preference-lab/results.json",
        "./book-engineering/diagrams/v4-ch04-synthetic-reasoning.svg",
        "./book-engineering/chapters/50-synthetic-reasoning.md",
        "./book-engineering/chapters/50-audit-report-fa.md",
        "./book-engineering/answers/50-synthetic-reasoning-fa.md",
        "./book-engineering/projects/50-synthetic-reasoning/README.md",
        "./book-engineering/projects/50-synthetic-reasoning/reasoning_lab.py",
        "./book-engineering/projects/50-synthetic-reasoning/test_reasoning_lab.py",
        "./book-engineering/projects/50-synthetic-reasoning/sample_traces.jsonl",
        "./book-engineering/projects/50-synthetic-reasoning/results.json",
        "./book-engineering/diagrams/v4-ch05-vision.svg",
        "./book-engineering/chapters/51-vision-models.md",
        "./book-engineering/chapters/51-audit-report-fa.md",
        "./book-engineering/answers/51-vision-models-fa.md",
        "./book-engineering/projects/51-vision-lab/README.md",
        "./book-engineering/projects/51-vision-lab/vision_lab.py",
        "./book-engineering/projects/51-vision-lab/test_vision_lab.py",
        "./book-engineering/projects/51-vision-lab/sample_embeddings.json",
        "./book-engineering/projects/51-vision-lab/results.json",
        "./book-engineering/diagrams/v4-ch06-audio.svg",
        "./book-engineering/chapters/52-audio-models.md",
        "./book-engineering/chapters/52-audit-report-fa.md",
        "./book-engineering/answers/52-audio-models-fa.md",
        "./book-engineering/projects/52-audio-lab/README.md",
        "./book-engineering/projects/52-audio-lab/audio_lab.py",
        "./book-engineering/projects/52-audio-lab/test_audio_lab.py",
        "./book-engineering/projects/52-audio-lab/sample_transcripts.json",
        "./book-engineering/projects/52-audio-lab/results.json",
    )
    for item in required_cache_paths:
        _require(item in sw, f"service worker does not precache {item}")

    print(
        f"PASS volume 4: {len(book['chapters'])}/{builder.PLANNED_CHAPTERS} chapters, "
        f"{sum(len(ch['sections']) for ch in book['chapters'])} sections, "
        f"{len(math_nodes) + len(math48) + len(math49) + len(math50) + len(math51) + len(math52)} accessible MathML expressions, exact appendices, reports/answers/fixtures present"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL volume 4: {exc}", file=sys.stderr)
        raise
