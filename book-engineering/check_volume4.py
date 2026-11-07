"""Structural, source, appendix, output and offline-cache checks for volume 4."""
from __future__ import annotations

import hashlib
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
    _require(book.get("author") == "Babak Moradvand", "volume 4 author metadata mismatch")
    v3_index = next((i for i, item in enumerate(data["books"]) if item.get("id") == "art-science-intelligence-v3"), None)
    v4_index = next((i for i, item in enumerate(data["books"]) if item.get("id") == BOOK_ID), None)
    _require(v3_index is not None and v4_index == v3_index + 1, "volume 4 must follow volume 3 in the reader")

    specs = builder.available_specs()
    expected_chapters = [builder.build_chapter(spec) for spec in specs]
    _require(bool(specs), "at least one volume 4 chapter must be authored")
    _require(book.get("chapters") == expected_chapters, "volume 4 data chapters do not match immutable Markdown sources")
    _require(len(book["chapters"]) <= builder.PLANNED_CHAPTERS, "more chapters than the roadmap defines")
    _require(book.get("subtitle") == "پس‌آموزش، چندوجهی و زیرساخت | ۱۵ فصل", "volume 4 card subtitle mismatch")

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

    source53 = ROOT / "book-engineering/chapters/53-image-video-generation.md"
    answer53 = ROOT / "book-engineering/answers/53-image-video-generation-fa.md"
    report53 = ROOT / "book-engineering/chapters/53-audit-report-fa.md"
    diagram53 = ROOT / "book-engineering/diagrams/v4-ch07-diffusion.svg"
    project53 = ROOT / "book-engineering/projects/53-diffusion-lab"
    for path in (source53, answer53, report53, diagram53, project53 / "README.md", project53 / "diffusion_lab.py", project53 / "test_diffusion_lab.py", project53 / "sample_mixture.json", project53 / "results.json"):
        _require(path.is_file(), f"missing chapter 53 deliverable: {path.relative_to(ROOT)}")
    source53_text = source53.read_text(encoding="utf-8")
    _require("فصل محلی ۷ از ۱۵ فصل جلد چهارم = فصل سراسری ۵۳" in source53_text, "chapter 53 local/global mapping or 15-chapter roadmap missing")
    _require("۱۵ فصل" in source53_text and "تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶" in source53_text, "chapter 53 roadmap or source-review date missing")
    _require("فصل ۵۱" in source53_text and "فصل ۵۲" in source53_text and "فصل ۵۴" in source53_text, "chapter 53 boundaries with adjacent chapters missing")
    _require(all(term in source53_text for term in ("DDPM", "DDIM", "Classifier-Free Guidance", "Latent Diffusion", "Diffusion Transformer", "Flow Matching", "C2PA", "VBench")), "chapter 53 roadmap topics missing")
    math53_nodes = re.findall(r"<math\b[^>]*>", source53_text)
    math53_blocks = re.findall(r"<math\b.*?</math>", source53_text, flags=re.DOTALL)
    _require(len(math53_nodes) >= 9 and len(math53_blocks) == len(math53_nodes), "chapter 53 core MathML missing or malformed")
    _require(all("aria-label=" in node for node in math53_nodes), "chapter 53 MathML needs aria-label")
    _require(source53_text.count("**متن جایگزین فرمول:**") >= len(math53_nodes), "chapter 53 formulas need visible alternatives")
    for math_markup in math53_blocks:
        _require(ET.fromstring(math_markup).tag.endswith("math"), "chapter 53 contains invalid MathML XML")
    figures53 = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source53_text)
    _require(bool(figures53), "chapter 53 figure missing")
    for alt, image_path in figures53:
        _require(bool(alt.strip()), "chapter 53 figure alternative text must be non-empty")
        _require((ROOT / image_path).is_file(), f"missing chapter 53 figure: {image_path}")
    _require(all(term in figures53[0][0] for term in ("diffusion شرطی", "cross-attention", "provenance")), "chapter 53 figure alt text misses key stages")
    svg53 = ET.parse(diagram53).getroot()
    _require(svg53.attrib.get("width") == "1600" and svg53.attrib.get("height") == "1000", "chapter 53 SVG dimensions mismatch")
    _require("aria-labelledby" in svg53.attrib, "chapter 53 SVG must expose title and description")
    answer53_text = answer53.read_text(encoding="utf-8")
    _require("پاسخ‌نامهٔ تشریحی فصل ۵۳" in answer53_text and len(answer53_text.split()) >= 250, "chapter 53 independent answer key missing or too short")
    report53_text = report53.read_text(encoding="utf-8")
    _require("نتایج اجرای واقعی" in report53_text and "۴۰/۴۰ آزمون موفق" in report53_text, "chapter 53 report must record actual unit tests")
    _require("7646ab0c0d8cee8fdbf3e29ac88ce9e37b181859e0ff34935f6af7bbe28b208b" in report53_text, "chapter 53 report must record fixture SHA-256")
    _require("test_volume4.py" in report53_text and "test_mobile_layout.py" in report53_text and "۷۱ دارایی آفلاین" in report53_text and "۹۷۲ بخش" in report53_text, "chapter 53 report must record browser/mobile results and coverage")
    _require("مدل واقعی" in report53_text and "کیفیت فارسی" in report53_text and "نتیجهٔ حقوقی" in report53_text, "chapter 53 report must state claim limits")
    code53 = (project53 / "diffusion_lab.py").read_text(encoding="utf-8").rstrip()
    blocks53 = re.findall(r"```python\n(.*?)\n```", source53_text, flags=re.DOTALL)
    _require(bool(blocks53) and blocks53[-1] == code53, "chapter 53 appendix and tested project must be byte-for-byte equal")
    fixture_path53 = project53 / "sample_mixture.json"
    fixture53 = json.loads(fixture_path53.read_text(encoding="utf-8"))
    fixture53_hash = hashlib.sha256(fixture_path53.read_bytes()).hexdigest()
    _require(fixture53["label_source"] == "synthetic_fixture" and len(fixture53["components"]) == 4, "chapter 53 fixture must remain a four-component synthetic mixture")
    _require(all(component["weight"] == 0.25 for component in fixture53["components"]), "chapter 53 fixture component weights changed")
    _require(fixture53["metadata"]["image_files_included"] is False and fixture53["metadata"]["video_files_included"] is False and fixture53["metadata"]["trained_weights_included"] is False, "chapter 53 fixture must disclaim real media and trained weights")
    results53 = json.loads((project53 / "results.json").read_text(encoding="utf-8"))
    _require(results53["unit_tests"]["passed"] == 40 and results53["unit_tests"]["failed"] == 0 and results53["unit_tests"]["python"] == "3.13.16", "chapter 53 result manifest test result mismatch")
    _require(results53["audit"]["fixture"]["sha256"] == fixture53_hash and results53["demo"]["fixture"]["sha256"] == fixture53_hash, "chapter 53 result manifest fixture SHA mismatch")
    _require(results53["audit"]["training_performed"] is False and results53["audit"]["neural_model_loaded"] is False and results53["demo"]["image_files_loaded"] is False and results53["demo"]["video_files_loaded"] is False, "chapter 53 result manifest must disclaim model training and real media")
    _require(results53["demo"]["sampling"]["terminal_alpha_bar"] == 0.002080618226191632 and results53["demo"]["nearest_synthetic_center_counts"] == {"southwest": 19, "northwest": 17, "southeast": 16, "northeast": 12}, "chapter 53 deterministic demo values changed")

    source54 = ROOT / "book-engineering/chapters/54-resource-estimation.md"
    answer54 = ROOT / "book-engineering/answers/54-resource-estimation-fa.md"
    report54 = ROOT / "book-engineering/chapters/54-audit-report-fa.md"
    diagram54 = ROOT / "book-engineering/diagrams/v4-ch08-resource-estimation.svg"
    project54 = ROOT / "book-engineering/projects/54-resource-estimation"
    for path in (source54, answer54, report54, diagram54, project54 / "README.md", project54 / "resource_estimator.py", project54 / "test_resource_estimator.py", project54 / "sample_profiles.json", project54 / "results.json"):
        _require(path.is_file(), f"missing chapter 54 deliverable: {path.relative_to(ROOT)}")
    source54_text = source54.read_text(encoding="utf-8")
    _require("فصل محلی ۸ از ۱۵ فصل جلد چهارم؛ فصل سراسری ۵۴" in source54_text, "chapter 54 local/global mapping or 15-chapter roadmap missing")
    _require("فصل ۵۳" in source54_text and "فصل ۵۵" in source54_text and "فصل ۵۶" in source54_text, "chapter 54 boundaries with adjacent chapters missing")
    _require(all(term in source54_text for term in ("Fine-tuning", "KV cache", "gradient", "optimizer", "ZeRO", "6ND", "۴۵/۴۵ آزمون unit موفق", "benchmark نیست")), "chapter 54 scope, methods, results, or limitations missing")
    math54_nodes = re.findall(r"<math\b[^>]*>", source54_text)
    math54_blocks = re.findall(r"<math\b.*?</math>", source54_text, flags=re.DOTALL)
    _require(len(math54_nodes) >= 10 and len(math54_blocks) == len(math54_nodes), "chapter 54 core MathML missing or malformed")
    _require(all("aria-label=" in node for node in math54_nodes), "chapter 54 MathML needs aria-label")
    _require(source54_text.count("**متن جایگزین فرمول:**") >= len(math54_nodes), "chapter 54 formulas need visible alternatives")
    for math_markup in math54_blocks:
        _require(ET.fromstring(math_markup).tag.endswith("math"), "chapter 54 contains invalid MathML XML")
    figures54 = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source54_text)
    _require(bool(figures54), "chapter 54 figure missing")
    for alt, image_path in figures54:
        _require(bool(alt.strip()), "chapter 54 figure alternative text must be non-empty")
        _require((ROOT / image_path).is_file(), f"missing chapter 54 figure: {image_path}")
    _require(all(term in figures54[0][0] for term in ("شکل ۴-۸-۱", "استنتاج", "Fine-tuning", "آموزش از صفر", "activation")), "chapter 54 figure alt text misses workload branches")
    svg54 = ET.parse(diagram54).getroot()
    _require(svg54.attrib.get("width") == "1600" and svg54.attrib.get("height") == "1000", "chapter 54 SVG dimensions mismatch")
    _require("aria-labelledby" in svg54.attrib, "chapter 54 SVG must expose title and description")
    answer54_text = answer54.read_text(encoding="utf-8")
    _require("پاسخ‌نامهٔ تشریحی فصل ۵۴" in answer54_text and len(answer54_text.split()) >= 300, "chapter 54 independent answer key missing or too short")
    report54_text = report54.read_text(encoding="utf-8")
    _require("نتایج اجرای واقعی" in report54_text and "۴۵/۴۵ آزمون unit موفق" in report54_text, "chapter 54 report must record actual unit tests")
    _require("9648418ea1cd039a5554d489d79e5d688314240f7c254d2d5215d03e372a4a57" in report54_text, "chapter 54 report must record fixture SHA-256")
    _require("test_volume4.py" in report54_text and "test_mobile_layout.py" in report54_text and "۸۰ دارایی آفلاین" in report54_text, "chapter 54 report must record integration checks and offline coverage")
    _require("مدل واقعی" in report54_text and "سخت‌افزار" in report54_text and "benchmark" in report54_text, "chapter 54 report must state claim limits")
    code54 = (project54 / "resource_estimator.py").read_text(encoding="utf-8").rstrip()
    blocks54 = re.findall(r"```python\n(.*?)\n```", source54_text, flags=re.DOTALL)
    _require(bool(blocks54) and blocks54[-1] == code54, "chapter 54 appendix and tested project must be byte-for-byte equal")
    fixture_path54 = project54 / "sample_profiles.json"
    fixture54 = json.loads(fixture_path54.read_text(encoding="utf-8"))
    fixture54_hash = hashlib.sha256(fixture_path54.read_bytes()).hexdigest()
    _require(fixture54["label_source"] == "synthetic_fixture" and len(fixture54["profiles"]) == 4, "chapter 54 fixture must remain four arithmetic-only scenarios")
    _require(all(fixture54["metadata"][field] is False for field in ("real_model_weights_included", "real_hardware_measurements_performed", "training_performed", "benchmark_performed")), "chapter 54 fixture must disclaim real models, measurements, training, and benchmarks")
    results54 = json.loads((project54 / "results.json").read_text(encoding="utf-8"))
    _require(results54["unit_tests"]["passed"] == 45 and results54["unit_tests"]["failed"] == 0 and results54["unit_tests"]["python"] == "3.13.16", "chapter 54 result manifest test result mismatch")
    _require(results54["fixture"]["sha256"] == fixture54_hash, "chapter 54 result manifest fixture SHA mismatch")
    _require(results54["scope"]["real_model_loaded"] is False and results54["scope"]["real_hardware_measured"] is False and results54["scope"]["training_performed"] is False and results54["scope"]["benchmark_performed"] is False, "chapter 54 result manifest must disclaim real model, measurement, training, and benchmark")
    scenarios54 = {row["profile_id"]: row for row in results54["scenarios"]}
    _require(scenarios54["synthetic-gqa-inference"]["estimate"]["total_estimate"]["bytes"] == 18364967296, "chapter 54 inference scenario result changed")
    _require(scenarios54["synthetic-full-training"]["estimate"]["total_estimate_per_rank"]["bytes"] == 130924967296, "chapter 54 full-training scenario result changed")
    _require(scenarios54["synthetic-adapter-training"]["estimate"]["total_estimate_per_rank"]["bytes"] == 18924967296, "chapter 54 adapter scenario result changed")
    _require(scenarios54["synthetic-zero-stage3-four-ranks"]["estimate"]["total_estimate_per_rank"]["bytes"] == 35952467296, "chapter 54 ZeRO scenario result changed")

    source55 = ROOT / "book-engineering/chapters/55-ai-lab-design.md"
    answer55 = ROOT / "book-engineering/answers/55-ai-lab-design.md"
    report55 = ROOT / "book-engineering/chapters/55-audit-report-fa.md"
    diagram55 = ROOT / "book-engineering/diagrams/v4-ch09-lab-design.svg"
    project55 = ROOT / "book-engineering/projects/55-ai-lab-design"
    for path in (source55, answer55, report55, diagram55, project55 / "README.md", project55 / "lab_design_planner.py", project55 / "test_lab_design_planner.py", project55 / "sample_labs.json", project55 / "results.json"):
        _require(path.is_file(), f"missing chapter 55 deliverable: {path.relative_to(ROOT)}")
    source55_text = source55.read_text(encoding="utf-8")
    _require("فصل محلی ۹ از ۱۵ فصل جلد چهارم؛ فصل سراسری ۵۵" in source55_text, "chapter 55 local/global mapping or 15-chapter roadmap missing")
    _require("تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶" in source55_text, "chapter 55 source-review date missing")
    _require(bool(re.search(r"^##\s+.*منابع و تاریخ بازبینی", source55_text, flags=re.MULTILINE)), "chapter 55 dated bibliography missing")
    _require("فصل ۵۴" in source55_text and "فصل ۵۶" in source55_text, "chapter 55 boundaries with adjacent chapters missing")
    _require(all(term in source55_text for term in ("شخصی", "حرفه‌ای مستقل", "سازمانی", "GPU", "PCIe", "RAM", "storage", "شبکه", "برق", "خنک", "backup", "paper_feasible", "قیمت")), "chapter 55 roadmap topics or claim limits missing")
    math55_nodes = re.findall(r"<math\b[^>]*>", source55_text)
    math55_blocks = re.findall(r"<math\b.*?</math>", source55_text, flags=re.DOTALL)
    _require(len(math55_nodes) >= 5 and len(math55_blocks) == len(math55_nodes), "chapter 55 core MathML missing or malformed")
    _require(all("aria-label=" in node for node in math55_nodes), "chapter 55 MathML needs aria-label")
    _require(source55_text.count("**متن جایگزین فرمول:**") >= len(math55_nodes), "chapter 55 formulas need visible alternatives")
    for math_markup in math55_blocks:
        _require(ET.fromstring(math_markup).tag.endswith("math"), "chapter 55 contains invalid MathML XML")
    figures55 = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source55_text)
    _require(bool(figures55), "chapter 55 figure missing")
    _require(all(term in figures55[0][0] for term in ("شکل ۴-۹-۱", "شخصی", "workstation", "کلاستر", "خنک")), "chapter 55 figure alt text misses architecture tiers")
    for alt, image_path in figures55:
        _require(bool(alt.strip()), "chapter 55 figure alternative text must be non-empty")
        _require((ROOT / image_path).is_file(), f"missing chapter 55 figure: {image_path}")
    svg55 = ET.parse(diagram55).getroot()
    _require(svg55.attrib.get("width") == "1600" and svg55.attrib.get("height") == "1000", "chapter 55 SVG dimensions mismatch")
    _require("aria-labelledby" in svg55.attrib, "chapter 55 SVG must expose title and description")
    answer55_text = answer55.read_text(encoding="utf-8")
    _require("پاسخ‌نامهٔ مستقل" in answer55_text and "فصل ۵۵" in answer55_text and len(answer55_text.split()) >= 250, "chapter 55 independent answer key missing or too short")
    report55_text = report55.read_text(encoding="utf-8")
    _require("نتایج اجرای واقعی" in report55_text and "۵۷/۵۷ آزمون موفق" in report55_text, "chapter 55 audit report must record actual unit tests")
    _require("f3fc9ec6961b3655a05e8a9436b52963bbfa38e48bd58e94ce09c1dcf9f34689" in report55_text, "chapter 55 report must record fixture SHA-256")
    _require("test_volume4.py" in report55_text and "test_mobile_layout.py" in report55_text and "۸۹ دارایی آفلاین" in report55_text, "chapter 55 report must record browser/mobile and offline checks")
    _require("benchmark" in report55_text and "سخت‌افزار واقعی" in report55_text and "تضمین ایمنی" in report55_text, "chapter 55 report must state claim limits")
    project_code55 = (project55 / "lab_design_planner.py").read_bytes()
    appendix_marker55 = b"\n```python\n"
    _, appendix_found55, appendix_tail55 = source55.read_bytes().rpartition(appendix_marker55)
    appendix_close55 = appendix_tail55.rfind(b"```")
    _require(bool(appendix_found55) and appendix_close55 >= 0 and appendix_tail55[:appendix_close55] == project_code55, "chapter 55 appendix and project must match byte-for-byte")
    fixture_path55 = project55 / "sample_labs.json"
    fixture55 = json.loads(fixture_path55.read_text(encoding="utf-8"))
    fixture55_hash = hashlib.sha256(fixture_path55.read_bytes()).hexdigest()
    _require(fixture55["fixture_id"] == "v4-ch09-synthetic-lab-design-v1" and fixture55["label_source"] == "synthetic_fixture" and len(fixture55["profiles"]) == 4, "chapter 55 synthetic fixture identity or row count changed")
    _require(all(value is False for value in fixture55["metadata"].values()), "chapter 55 fixture must disclaim measurements, SKUs, prices, benchmarks, installation and training")
    results55 = json.loads((project55 / "results.json").read_text(encoding="utf-8"))
    _require(results55["unit_tests"]["passed"] == 57 and results55["unit_tests"]["failed"] == 0 and results55["unit_tests"]["python"] == "3.13.16", "chapter 55 result manifest test result mismatch")
    _require(results55["fixture"]["sha256"] == fixture55_hash, "chapter 55 result manifest fixture hash mismatch")
    _require(results55["summary"] == {"profiles": 4, "paper_feasible": 3, "needs_revision": 1}, "chapter 55 deterministic screen summary changed")

    source56 = ROOT / "book-engineering/chapters/56-ai-compute-budget.md"
    answer56 = ROOT / "book-engineering/answers/56-ai-compute-budget-fa.md"
    report56 = ROOT / "book-engineering/chapters/56-audit-report-fa.md"
    diagram56 = ROOT / "assets/images/babak-ai/v4-ch10-tco-timeline.svg"
    project56 = ROOT / "book-engineering/projects/56-ai-compute-budget"
    for path in (source56, answer56, report56, diagram56, project56 / "README.md", project56 / "budget_model.py", project56 / "test_budget_model.py", project56 / "sample_budget.json", project56 / "results.json"):
        _require(path.is_file(), f"missing chapter 56 deliverable: {path.relative_to(ROOT)}")
    source56_text = source56.read_text(encoding="utf-8")
    _require("فصل محلی ۱۰ از ۱۵ فصل جلد چهارم؛ فصل سراسری ۵۶" in source56_text, "chapter 56 local/global mapping missing")
    _require("تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶" in source56_text, "chapter 56 dated review note missing")
    _require(bool(re.search(r"^##\s+.*منابع و تاریخ بازبینی", source56_text, flags=re.MULTILINE)) and bool(re.search(r"^##\s+.*پیوست اجرایی", source56_text, flags=re.MULTILINE)), "chapter 56 bibliography or executable appendix missing")
    _require("فصل ۵۴" in source56_text and "فصل ۵۵" in source56_text and "فصل ۵۷" in source56_text, "chapter 56 boundaries with adjacent chapters missing")
    _require(all(term in source56_text for term in ("TCO", "NPV", "خرید", "اجاره", "Iowa", "us-central1", "Texas statewide", "synthetic_fixture", "NIST SP 1326", "GAO-20-195G")), "chapter 56 budget, market, or supply-risk scope missing")
    math56_nodes = re.findall(r"<math\b[^>]*>", source56_text)
    math56_blocks = re.findall(r"<math\b.*?</math>", source56_text, flags=re.DOTALL)
    _require(len(math56_nodes) >= 5 and len(math56_blocks) == len(math56_nodes), "chapter 56 core MathML missing or malformed")
    _require(all("aria-label=" in node for node in math56_nodes), "chapter 56 MathML needs aria-label")
    _require(source56_text.count("**متن جایگزین فرمول:**") >= len(math56_nodes), "chapter 56 formulas need visible alternatives")
    for math_markup in math56_blocks:
        _require(ET.fromstring(math_markup).tag.endswith("math"), "chapter 56 contains invalid MathML XML")
    figures56 = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source56_text)
    _require(bool(figures56) and all(term in figures56[0][0] for term in ("شکل ۴-۱۰-۱", "خرید", "اجاره", "ابر", "TCO")), "chapter 56 figure alt text misses TCO decision boundaries")
    for alt, image_path in figures56:
        _require(bool(alt.strip()) and (ROOT / image_path).is_file(), f"missing or inaccessible chapter 56 figure: {image_path}")
    svg56 = ET.parse(diagram56).getroot()
    _require(svg56.attrib.get("width") == "1600" and svg56.attrib.get("height") == "1000", "chapter 56 SVG dimensions mismatch")
    _require("aria-labelledby" in svg56.attrib, "chapter 56 SVG must expose title and description")
    answer56_text = answer56.read_text(encoding="utf-8")
    _require("پاسخ‌نامهٔ مستقل" in answer56_text and "فصل ۵۶" in answer56_text and len(answer56_text.split()) >= 300, "chapter 56 independent answer key missing or too short")
    report56_text = report56.read_text(encoding="utf-8")
    _require("13/13 آزمون unit موفق" in report56_text and "Ran 13 tests" in report56_text, "chapter 56 audit report must record the actual project test result")
    _require("test_volume4.py" in report56_text and "test_mobile_layout.py" in report56_text and "۹۸ دارایی آفلاین" in report56_text, "chapter 56 report must record browser/mobile and offline checks")
    _require("benchmark" in report56_text and "سخت‌افزار واقعی" in report56_text and "تضمین ایمنی" in report56_text, "chapter 56 report must state actual claim limits")
    project_code56 = (project56 / "budget_model.py").read_bytes()
    appendix_marker56 = b"\n```python\n"
    _, appendix_found56, appendix_tail56 = source56.read_bytes().rpartition(appendix_marker56)
    appendix_close56 = appendix_tail56.rfind(b"```")
    _require(bool(appendix_found56) and appendix_close56 >= 0 and appendix_tail56[:appendix_close56] == project_code56, "chapter 56 appendix and project must match byte-for-byte")
    fixture_path56 = project56 / "sample_budget.json"
    fixture56 = json.loads(fixture_path56.read_text(encoding="utf-8"))
    fixture56_hash = hashlib.sha256(fixture_path56.read_bytes()).hexdigest()
    _require(fixture56["fixture_id"] == "v4-ch10-synthetic-budget-v1" and fixture56["label_source"] == "synthetic_fixture" and len(fixture56["scenarios"]) == 3, "chapter 56 fixture identity or scenario count changed")
    _require(all(row["quote_status"] == "synthetic_not_a_vendor_quote" for row in fixture56["scenarios"]), "chapter 56 purchase/lease rows must remain synthetic")
    _require(fixture56["assumptions"]["performance_parity_measured"] is False and fixture56["market_snapshot"]["cloud_compute"]["region"] == "us-central1 (Iowa, US)" and fixture56["market_snapshot"]["electricity"]["region"] == "Texas statewide; not Dallas-specific", "chapter 56 fixture market or parity boundary changed")
    results56 = json.loads((project56 / "results.json").read_text(encoding="utf-8"))
    _require(results56["fixture_sha256"] == fixture56_hash and results56["horizon_years"] == 3 and results56["annual_discount_rate"] == "0.05", "chapter 56 result manifest fixture or assumptions mismatch")
    _require(results56["comparison_status"]["performance_parity_measured"] is False and results56["comparison_status"]["complete_invoice_or_cost_estimate"] is False and results56["comparison_status"]["purchase_and_lease_amounts_are_vendor_quotes"] is False, "chapter 56 result manifest must retain scope limitations")
    results_by_id56 = {row["id"]: row for row in results56["scenarios"]}
    _require(results_by_id56["buy-synthetic"]["nominal_tco_usd"] == "8595.14" and results_by_id56["buy-synthetic"]["npv_tco_usd"] == "8577.77", "chapter 56 buy arithmetic changed")
    _require(results_by_id56["lease-synthetic"]["nominal_tco_usd"] == "14005.14" and results_by_id56["cloud-snapshot-illustration"]["nominal_tco_usd"] == "12149.82", "chapter 56 lease/cloud arithmetic changed")
    _require(results55["scope"]["real_hardware_measured"] is False and results55["scope"]["prices_included"] is False and results55["scope"]["benchmark_performed"] is False and results55["scope"]["installation_performed"] is False, "chapter 55 result manifest scope limits changed")

    source57 = ROOT / "book-engineering/chapters/57-ml-frameworks.md"
    answer57 = ROOT / "book-engineering/answers/57-ml-frameworks-fa.md"
    report57 = ROOT / "book-engineering/chapters/57-audit-report-fa.md"
    diagram57 = ROOT / "book-engineering/diagrams/v4-ch11-framework-selection.svg"
    project57 = ROOT / "book-engineering/projects/57-framework-lab"
    for path in (source57, answer57, report57, diagram57, project57 / "README.md", project57 / "framework_compare.py", project57 / "test_framework_compare.py", project57 / "sample_problem.json", project57 / "results.json"):
        _require(path.is_file(), f"missing chapter 57 deliverable: {path.relative_to(ROOT)}")
    source57_text = source57.read_text(encoding="utf-8")
    _require("فصل محلی ۱۱ از ۱۵ جلد چهارم؛ فصل سراسری ۵۷" in source57_text, "chapter 57 local/global mapping missing")
    _require("تاریخ بازبینی منابع: ۶ نوامبر ۲۰۲۶" in source57_text, "chapter 57 dated review note missing")
    _require(bool(re.search(r"^##\s+.*منابع و تاریخ بازبینی", source57_text, flags=re.MULTILINE)) and bool(re.search(r"^##\s+.*پیوست اجرایی", source57_text, flags=re.MULTILINE)), "chapter 57 bibliography or executable appendix missing")
    _require(all(term in source57_text for term in ("فصل ۵۶", "فصل ۵۸", "فصل ۵۹", "PyTorch", "JAX", "TensorFlow", "3.12", "2.15.0", "0.12.0.1", "2.21.0", "CUDA 13", "synthetic_fixture")), "chapter 57 framework/version/scope or adjacent chapter boundary missing")
    math57_nodes = re.findall(r"<math\b[^>]*>", source57_text)
    math57_blocks = re.findall(r"<math\b.*?</math>", source57_text, flags=re.DOTALL)
    _require(len(math57_nodes) >= 1 and len(math57_blocks) == len(math57_nodes), "chapter 57 accessible MathML missing or malformed")
    _require(all("aria-label=" in node for node in math57_nodes), "chapter 57 MathML needs aria-label")
    _require(source57_text.count("**متن جایگزین فرمول:**") >= len(math57_nodes), "chapter 57 formula needs a visible alternative")
    for math_markup in math57_blocks:
        _require(ET.fromstring(math_markup).tag.endswith("math"), "chapter 57 contains invalid MathML XML")
    figures57 = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source57_text)
    _require(bool(figures57) and all(term in figures57[0][0] for term in ("شکل ۴-۱۱-۱", "PyTorch", "JAX", "TensorFlow", "benchmark")), "chapter 57 figure alt text misses scope and frameworks")
    for alt, image_path in figures57:
        _require(bool(alt.strip()) and (ROOT / image_path).is_file(), f"missing or inaccessible chapter 57 figure: {image_path}")
    svg57 = ET.parse(diagram57).getroot()
    _require(svg57.attrib.get("width") == "1600" and svg57.attrib.get("height") == "1000", "chapter 57 SVG dimensions mismatch")
    _require("aria-labelledby" in svg57.attrib, "chapter 57 SVG must expose title and description")
    answer57_text = answer57.read_text(encoding="utf-8")
    _require("پاسخ‌نامهٔ مستقل" in answer57_text and "فصل ۵۷" in answer57_text and len(answer57_text.split()) >= 300, "chapter 57 independent answer key missing or too short")
    report57_text = report57.read_text(encoding="utf-8")
    _require("نتایج اجرای واقعی" in report57_text and "test_volume4.py" in report57_text and "test_mobile_layout.py" in report57_text, "chapter 57 audit report is incomplete")
    _require("framework_compare.py" in report57_text and "sample_problem.json" in report57_text and "synthetic_fixture" in report57_text, "chapter 57 report must identify the tested project and synthetic fixture")
    _require("سخت‌افزار واقعی" in report57_text and "benchmark" in report57_text and "مدل ازپیش‌آموزش‌دیده" in report57_text, "chapter 57 report must state claim limits")
    project_code57 = (project57 / "framework_compare.py").read_bytes()
    appendix_marker57 = b"\n```python\n"
    _, appendix_found57, appendix_tail57 = source57.read_bytes().rpartition(appendix_marker57)
    appendix_close57 = appendix_tail57.rfind(b"```")
    _require(bool(appendix_found57) and appendix_close57 >= 0 and appendix_tail57[:appendix_close57] == project_code57, "chapter 57 appendix and project must match byte-for-byte")
    fixture_path57 = project57 / "sample_problem.json"
    fixture57 = json.loads(fixture_path57.read_text(encoding="utf-8"))
    fixture57_hash = hashlib.sha256(fixture_path57.read_bytes()).hexdigest()
    _require(fixture57["fixture_id"] == "v4-ch11-synthetic-gradient-v1" and fixture57["label_source"] == "synthetic_fixture" and all(value is False for value in fixture57["metadata"].values()), "chapter 57 fixture identity or scope changed")
    results57 = json.loads((project57 / "results.json").read_text(encoding="utf-8"))
    _require(results57["fixture_sha256"] == fixture57_hash and results57["fixture_id"] == fixture57["fixture_id"], "chapter 57 result manifest fixture identity/hash mismatch")
    _require(results57["reference"] == {"loss": 2.5, "gradient_weight": -2.0, "gradient_bias": -3.0}, "chapter 57 reference arithmetic changed")
    _require(all(value is False for value in results57["scope"].values()), "chapter 57 result manifest must retain all claim limits")
    _require(results57["summary"]["failed"] == [], "chapter 57 project reports a failed framework adapter")

    source58 = ROOT / "book-engineering/chapters/58-huggingface-stack.md"
    answer58 = ROOT / "book-engineering/answers/58-huggingface-stack-fa.md"
    report58 = ROOT / "book-engineering/chapters/58-audit-report-fa.md"
    diagram58 = ROOT / "book-engineering/diagrams/v4-ch12-huggingface-stack.svg"
    project58 = ROOT / "book-engineering/projects/58-huggingface-stack"
    for path in (source58, answer58, report58, diagram58, project58 / "README.md", project58 / "pipeline_demo.py", project58 / "test_pipeline_demo.py", project58 / "sample_data.jsonl", project58 / "fixture_manifest.json", project58 / "environment.json", project58 / "results.json", project58 / "requirements.txt", project58 / "requirements-cpu.txt", project58 / "requirements-lock-linux-py313.txt"):
        _require(path.is_file(), f"missing chapter 58 deliverable: {path.relative_to(ROOT)}")
    source58_text = source58.read_text(encoding="utf-8")
    _require("فصل محلی ۱۲ از ۱۵ جلد چهارم؛ فصل سراسری ۵۸" in source58_text, "chapter 58 local/global mapping missing")
    _require("تاریخ بازبینی منابع و آزمون محیط: ۶ نوامبر ۲۰۲۶" in source58_text, "chapter 58 dated review note missing")
    _require(all(term in source58_text for term in ("فصل ۵۷", "فصل ۵۹", "Transformers", "Datasets", "Tokenizers", "Accelerate", "5.22.2", "5.1.0", "0.23.3", "1.15.0", "trust_remote_code", "safetensors", "synthetic_fixture", "Trainer", "Accelerator")), "chapter 58 package/version/security/scope boundary missing")
    _require(len(re.findall(r"^##\s+", source58_text, flags=re.MULTILINE)) >= 20, "chapter 58 needs a complete section structure")
    math58_nodes = re.findall(r"<math\b[^>]*>", source58_text)
    math58_blocks = re.findall(r"<math\b.*?</math>", source58_text, flags=re.DOTALL)
    _require(len(math58_nodes) >= 1 and len(math58_blocks) == len(math58_nodes), "chapter 58 accessible MathML missing or malformed")
    _require(all("aria-label=" in node for node in math58_nodes) and source58_text.count("**متن جایگزین فرمول:**") >= len(math58_nodes), "chapter 58 MathML needs aria-label and a visible alternative")
    for math_markup in math58_blocks:
        _require(ET.fromstring(math_markup).tag.endswith("math"), "chapter 58 contains invalid MathML XML")
    figures58 = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source58_text)
    _require(bool(figures58) and all(term in figures58[0][0] for term in ("شکل ۴-۱۲-۱", "Hugging Face", "benchmark")), "chapter 58 diagram alt text misses identity or claim boundary")
    for alt, image_path in figures58:
        _require(bool(alt.strip()) and (ROOT / image_path).is_file(), f"missing or inaccessible chapter 58 figure: {image_path}")
    svg58 = ET.parse(diagram58).getroot()
    _require(svg58.attrib.get("width") == "1600" and svg58.attrib.get("height") == "1000" and "aria-labelledby" in svg58.attrib, "chapter 58 SVG dimensions/accessibility mismatch")
    answer58_text = answer58.read_text(encoding="utf-8")
    _require("پاسخ‌نامهٔ مستقل" in answer58_text and "فصل ۵۸" in answer58_text and len(answer58_text.split()) >= 300, "chapter 58 independent answer key missing or too short")
    report58_text = report58.read_text(encoding="utf-8")
    _require("نتایج اجرای واقعی" in report58_text and "12" in report58_text and "pip check" in report58_text and "accelerate launch" in report58_text, "chapter 58 audit report is incomplete")
    _require("model quality" in report58_text.lower() and "pretrained" in report58_text.lower() and "synthetic_fixture" in report58_text, "chapter 58 audit report must retain data/model/quality limits")
    project_code58 = (project58 / "pipeline_demo.py").read_bytes()
    appendix_marker58 = b"\n```python\n"
    _, appendix_found58, appendix_tail58 = source58.read_bytes().rpartition(appendix_marker58)
    appendix_close58 = appendix_tail58.rfind(b"```")
    _require(bool(appendix_found58) and appendix_close58 >= 0 and appendix_tail58[:appendix_close58] == project_code58, "chapter 58 appendix and project must match byte-for-byte")
    rows58 = [json.loads(line) for line in (project58 / "sample_data.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    manifest58 = json.loads((project58 / "fixture_manifest.json").read_text(encoding="utf-8"))
    fixture58_hash = hashlib.sha256((project58 / "sample_data.jsonl").read_bytes()).hexdigest()
    _require(len(rows58) == 12 and manifest58["fixture_id"] == "v4-ch12-synthetic-text-pipeline-v1" and manifest58["label_source"] == "synthetic_fixture" and manifest58["sha256"] == fixture58_hash, "chapter 58 fixture identity/hash/count changed")
    _require(manifest58["split_record_counts"] == {"train": 8, "validation": 4} and manifest58["split_group_counts"] == {"train": 4, "validation": 2}, "chapter 58 fixture split/group counts changed")
    results58 = json.loads((project58 / "results.json").read_text(encoding="utf-8"))
    _require(results58["fixture_id"] == manifest58["fixture_id"] and results58["fixture_sha256"] == fixture58_hash and results58["data"]["group_overlap"] == [], "chapter 58 result fixture hash or group-split contract mismatch")
    _require(results58["environment"]["packages"] == {"torch": "2.15.0+cpu", "transformers": "5.22.2", "datasets": "5.1.0", "tokenizers": "0.23.3", "accelerate": "1.15.0"} and results58["environment"]["accelerator_device"] == "cpu", "chapter 58 tested environment versions/device changed")
    _require(results58["tokenizer"]["trained_on_split"] == "train" and len(results58["tokenizer"]["training_example_ids"]) == 8 and results58["model"]["pretrained_weights_loaded"] is False, "chapter 58 tokenizer/model provenance boundary changed")
    _require(results58["training"]["steps"] == 2 and results58["training"]["all_gradients_finite"] is True and len(results58["training"]["validation_loss_smoke_only"]) == 2, "chapter 58 CPU smoke run changed")
    _require(all(value is False for value in results58["scope"].values()), "chapter 58 result manifest must retain all claim limits")
    environment58 = json.loads((project58 / "environment.json").read_text(encoding="utf-8"))
    _require(environment58["pip_check"].startswith("passed") and environment58["fixture_sha256"] == fixture58_hash and environment58["device"] == "CPU only", "chapter 58 environment manifest mismatch")

    source59 = ROOT / "book-engineering/chapters/59-gpu-systems.md"
    answer59 = ROOT / "book-engineering/answers/59-gpu-systems-fa.md"
    report59 = ROOT / "book-engineering/chapters/59-audit-report-fa.md"
    diagram59 = ROOT / "book-engineering/diagrams/v4-ch13-gpu-systems.svg"
    project59 = ROOT / "book-engineering/projects/59-gpu-systems"
    for path in (source59, answer59, report59, diagram59, project59 / "README.md", project59 / "gpu_systems_demo.py", project59 / "test_gpu_systems_demo.py", project59 / "sample_layout.json", project59 / "fixture_manifest.json", project59 / "environment.json", project59 / "results.json", project59 / "requirements.txt", project59 / "requirements-cpu.txt", project59 / "requirements-lock-linux-py313.txt"):
        _require(path.is_file(), f"missing chapter 59 deliverable: {path.relative_to(ROOT)}")
    source59_text = source59.read_text(encoding="utf-8")
    _require("فصل محلی ۱۳ از ۱۵ جلد چهارم؛ فصل سراسری ۵۹" in source59_text, "chapter 59 local/global mapping missing")
    _require("فصل ۵۷" in source59_text and "فصل ۵۸" in source59_text and "فصل ۶۰" in source59_text and "فصل ۶۱" in source59_text, "chapter 59 adjacent-chapter boundaries missing")
    _require("تاریخ بازبینی منابع:** ۷ نوامبر ۲۰۲۶" in source59_text, "chapter 59 dated source review missing")
    _require(all(term in source59_text for term in ("CUDA", "ROCm", "Triton", "DeepSpeed", "FSDP", "Megatron", "NCCL", "RCCL", "synthetic_fixture", "2.15.0", "3.9.0", "0.19.9", "0.20.0")), "chapter 59 roadmap topics or version snapshot missing")
    _require(len(re.findall(r"^##\s+", source59_text, flags=re.MULTILINE)) >= 20, "chapter 59 needs a complete section structure")
    math59_nodes = re.findall(r"<math\b[^>]*>", source59_text)
    math59_blocks = re.findall(r"<math\b.*?</math>", source59_text, flags=re.DOTALL)
    _require(len(math59_nodes) >= 1 and len(math59_blocks) == len(math59_nodes), "chapter 59 accessible MathML missing or malformed")
    _require(all("aria-label=" in node for node in math59_nodes) and source59_text.count("**متن جایگزین فرمول:**") >= len(math59_nodes), "chapter 59 MathML needs aria-label and visible alternatives")
    for math_markup in math59_blocks:
        _require(ET.fromstring(math_markup).tag.endswith("math"), "chapter 59 contains invalid MathML XML")
    figures59 = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source59_text)
    _require(bool(figures59) and all(term in figures59[0][0] for term in ("شکل ۴-۱۳-۱", "PyTorch", "CUDA", "ROCm", "benchmark")), "chapter 59 figure alt text misses relationships or limitations")
    for alt, image_path in figures59:
        _require(bool(alt.strip()) and (ROOT / image_path).is_file(), f"missing or inaccessible chapter 59 figure: {image_path}")
    svg59 = ET.parse(diagram59).getroot()
    _require(svg59.attrib.get("width") == "1600" and svg59.attrib.get("height") == "1000" and "aria-labelledby" in svg59.attrib, "chapter 59 SVG dimensions/accessibility mismatch")
    for text_node in svg59.iter():
        if text_node.tag.endswith("text"):
            visible_label = "".join(text_node.itertext())
            has_rtl = any("\u0600" <= char <= "\u06ff" for char in visible_label)
            has_latin = any(("a" <= char <= "z") or ("A" <= char <= "Z") for char in visible_label)
            _require(not (has_rtl and has_latin), "chapter 59 figure must place English labels on separate lines from Persian")
    answer59_text = answer59.read_text(encoding="utf-8")
    _require("پاسخ‌نامهٔ مستقل" in answer59_text and "فصل ۵۹" in answer59_text and len(answer59_text.split()) >= 300, "chapter 59 independent answer key missing or too short")
    exercise59_match = re.search(r"^##\s+۱۹\.\s+تمرین‌ها\s*\n(.*?)(?=^##\s+|\Z)", source59_text, flags=re.MULTILINE | re.DOTALL)
    _require(exercise59_match is not None, "chapter 59 exercise section missing")
    for question in re.findall(r"^\d+\. (.+)$", exercise59_match.group(1), flags=re.MULTILINE):
        _require(question in answer59_text, f"chapter 59 answer key changed question text: {question}")
    report59_text = report59.read_text(encoding="utf-8")
    _require("نتایج اجرای واقعی" in report59_text and "۲۳/۲۳ آزمون unit موفق" in report59_text, "chapter 59 report must record actual unit-test result")
    _require("1edb63d0caa8eedbadf77de3a086c6d61cc1a7dc072601f97046066eb95e7fa0" in report59_text and "all_reduce_sum" in report59_text, "chapter 59 report must identify fixture and Gloo result")
    _require("test_volume4.py" in report59_text and "test_mobile_layout.py" in report59_text and "مدل‌سنجی" in report59_text, "chapter 59 report must record integration checks and limitations")
    project_code59 = (project59 / "gpu_systems_demo.py").read_bytes()
    appendix_marker59 = b"\n```python\n"
    _, appendix_found59, appendix_tail59 = source59.read_bytes().rpartition(appendix_marker59)
    appendix_close59 = appendix_tail59.rfind(b"```")
    _require(bool(appendix_found59) and appendix_close59 >= 0 and appendix_tail59[:appendix_close59] == project_code59, "chapter 59 appendix and project must be byte-for-byte equal")
    fixture59 = json.loads((project59 / "sample_layout.json").read_text(encoding="utf-8"))
    manifest59 = json.loads((project59 / "fixture_manifest.json").read_text(encoding="utf-8"))
    fixture59_hash = hashlib.sha256((project59 / "sample_layout.json").read_bytes()).hexdigest()
    _require(fixture59["fixture_id"] == "v4-ch13-synthetic-dense-layout-v1" and fixture59["label_source"] == "synthetic_fixture" and manifest59["sha256"] == fixture59_hash and manifest59["fixture_id"] == fixture59["fixture_id"], "chapter 59 synthetic layout fixture identity/hash changed")
    _require(fixture59["world_size"] == 16 and fixture59["dense_parallelism"] == {"dp": 2, "tp": 2, "pp": 2, "cp": 2} and all(value is False for value in fixture59["metadata"].values()), "chapter 59 synthetic layout or scope changed")
    results59 = json.loads((project59 / "results.json").read_text(encoding="utf-8"))
    _require(results59["fixture_id"] == fixture59["fixture_id"] and results59["fixture_sha256"] == fixture59_hash, "chapter 59 results fixture identity/hash mismatch")
    _require(results59["unit_tests"] == {"passed": 23, "failed": 0, "command": "python -m unittest discover -v"} and results59["pip_check"] == "passed", "chapter 59 results must record tests and pip check")
    _require(results59["environment"]["torch"] == "2.6.0+cpu" and results59["environment"]["device"] == "CPU only" and results59["environment"]["gloo_available"] is True and results59["environment"]["nccl_available"] is False, "chapter 59 tested environment/device mismatch")
    _require(results59["layout_validation"]["world_size"] == 16 and results59["layout_validation"]["dimension_product"] == 16, "chapter 59 layout arithmetic changed")
    _require(results59["gloo_smoke"]["process_group"]["backend"] == "gloo" and results59["gloo_smoke"]["process_group"]["world_size"] == 2 and results59["gloo_smoke"]["collective"]["observed"] == 3 and results59["gloo_smoke"]["collective"]["passed"] is True, "chapter 59 Gloo collective result changed")
    _require(all(value is False for value in results59["scope"].values()), "chapter 59 result manifest must retain all GPU/backend/training claim limits")
    environment59 = json.loads((project59 / "environment.json").read_text(encoding="utf-8"))
    _require(environment59["pip_check"].startswith("passed") and environment59["packages"]["torch"] == "2.6.0+cpu" and environment59["accelerator"] == "CPU only", "chapter 59 environment manifest mismatch")

    source60 = ROOT / "book-engineering/chapters/60-mlops.md"
    answer60 = ROOT / "book-engineering/answers/60-mlops-fa.md"
    report60 = ROOT / "book-engineering/chapters/60-audit-report-fa.md"
    diagram60 = ROOT / "book-engineering/diagrams/v4-ch14-mlops.svg"
    project60 = ROOT / "book-engineering/projects/60-mlops"
    files60 = (
        source60, answer60, report60, diagram60,
        project60 / "README.md", project60 / "experiment_ops.py", project60 / "test_experiment_ops.py",
        project60 / "sample_experiment.json", project60 / "fixture_manifest.json",
        project60 / "environment.json", project60 / "results.json",
        project60 / "requirements.txt", project60 / "requirements-cpu.txt",
        project60 / "requirements-lock-linux-py313.txt", project60 / "Dockerfile",
        project60 / "job.yaml", project60 / ".dockerignore", project60 / ".gitignore",
    )
    for path in files60:
        _require(path.is_file(), f"missing chapter 60 deliverable: {path.relative_to(ROOT)}")
    source60_text = source60.read_text(encoding="utf-8")
    _require("فصل محلی ۱۴ از ۱۵ جلد چهارم؛ فصل سراسری ۶۰" in source60_text, "chapter 60 local/global mapping missing")
    _require(all(term in source60_text for term in ("فصل ۵۷", "فصل ۵۸", "فصل ۵۹", "فصل ۶۱")), "chapter 60 adjacent-chapter boundaries missing")
    _require("تاریخ بازبینی منابع: ۷ نوامبر ۲۰۲۶" in source60_text, "chapter 60 dated source review missing")
    _require(all(term in source60_text for term in ("MLflow", "W&B", "Docker", "Kubernetes", "Git", "fixture_manifest.json", "wandb-offline", "lockfile")), "chapter 60 MLOps scope topics missing")
    _require(len(re.findall(r"^##\s+", source60_text, flags=re.MULTILINE)) >= 22, "chapter 60 needs a complete section structure")
    math60_nodes = re.findall(r"<math\b[^>]*>", source60_text)
    math60_blocks = re.findall(r"<math\b.*?</math>", source60_text, flags=re.DOTALL)
    _require(len(math60_nodes) >= 2 and len(math60_blocks) == len(math60_nodes), "chapter 60 accessible MathML missing or malformed")
    _require(all("aria-label=" in node for node in math60_nodes) and source60_text.count("**متن جایگزین فرمول:**") >= len(math60_nodes), "chapter 60 MathML needs aria-label and visible alternatives")
    for math_markup in math60_blocks:
        _require(ET.fromstring(math_markup).tag.endswith("math"), "chapter 60 contains invalid MathML XML")
    figures60 = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source60_text)
    _require(bool(figures60) and all(term in figures60[0][0] for term in ("شکل ۴-۱۴-۱", "MLflow", "W&B", "run.json", "کیفیت مدل", "benchmark")), "chapter 60 figure alt text misses relationships or limits")
    for alt, image_path in figures60:
        _require(bool(alt.strip()) and (ROOT / image_path).is_file(), f"missing or inaccessible chapter 60 figure: {image_path}")
    svg60 = ET.parse(diagram60).getroot()
    _require(svg60.attrib.get("width") == "1600" and svg60.attrib.get("height") == "1000" and "aria-labelledby" in svg60.attrib, "chapter 60 SVG dimensions/accessibility mismatch")
    for text_node in svg60.iter():
        if text_node.tag.endswith("text"):
            visible_label = "".join(text_node.itertext())
            has_rtl = any("\u0600" <= char <= "\u06ff" for char in visible_label)
            has_latin = any(("a" <= char <= "z") or ("A" <= char <= "Z") for char in visible_label)
            _require(not (has_rtl and has_latin), "chapter 60 figure must place English labels on separate lines from Persian")
    answer60_text = answer60.read_text(encoding="utf-8")
    _require("پاسخ‌نامهٔ مستقل" in answer60_text and "فصل ۶۰" in answer60_text and len(answer60_text.split()) >= 300, "chapter 60 independent answer key missing or too short")
    exercise60_match = re.search(r"^##\s+۲۱\.\s+تمرین‌ها\s*\n(.*?)(?=^##\s+|\Z)", source60_text, flags=re.MULTILINE | re.DOTALL)
    _require(exercise60_match is not None, "chapter 60 exercise section missing")
    questions60 = re.findall(r"^\d+\. (.+)$", exercise60_match.group(1), flags=re.MULTILINE)
    _require(len(questions60) == 6, "chapter 60 must retain all six exercise prompts")
    for question in questions60:
        _require(question in answer60_text, f"chapter 60 answer key changed question text: {question}")
    report60_text = report60.read_text(encoding="utf-8")
    _require("نتایج اجرای واقعی" in report60_text and "۱۶/۱۶ آزمون unit موفق" in report60_text, "chapter 60 report must record actual unit-test result")
    _require("81989e3ae534cade6f4e77742cb3fae01649247956962559720e75b093f1a260" in report60_text and "0.09078731868784178" in report60_text, "chapter 60 report must record fixture hash and exact synthetic metric")
    _require(all(term in report60_text for term in ("mlflow", "wandb-offline", "Docker", "Kubernetes", "آزموده نشده")), "chapter 60 report must record tracking outcomes and deployment limits")
    project_code60 = (project60 / "experiment_ops.py").read_bytes()
    appendix_marker60 = b"\n```python\n"
    _, appendix_found60, appendix_tail60 = source60.read_bytes().rpartition(appendix_marker60)
    appendix_close60 = appendix_tail60.rfind(b"```")
    _require(bool(appendix_found60) and appendix_close60 >= 0 and appendix_tail60[:appendix_close60] == project_code60 and appendix_tail60[appendix_close60 + 3:] in (b"", b"\n"), "chapter 60 appendix and project must be byte-for-byte equal")
    fixture60 = json.loads((project60 / "sample_experiment.json").read_text(encoding="utf-8"))
    manifest60 = json.loads((project60 / "fixture_manifest.json").read_text(encoding="utf-8"))
    fixture60_hash = hashlib.sha256((project60 / "sample_experiment.json").read_bytes()).hexdigest()
    _require(fixture60["fixture_id"] == "v4-ch14-synthetic-linear-v1" and fixture60["label_source"] == "synthetic_fixture" and manifest60["sha256"] == fixture60_hash and manifest60["fixture_id"] == fixture60["fixture_id"] and manifest60["record_count"] == 4, "chapter 60 synthetic fixture identity/hash/count changed")
    _require(fixture60["scope"]["synthetic_only"] is True and all(fixture60["scope"][key] is False for key in ("real_data_used", "pretrained_model_used", "gpu_used", "benchmark_claim", "model_quality_claim", "production_claim")), "chapter 60 fixture scope must remain synthetic-only")
    results60 = json.loads((project60 / "results.json").read_text(encoding="utf-8"))
    _require(results60["fixture_id"] == fixture60["fixture_id"] and results60["fixture_sha256"] == fixture60_hash, "chapter 60 results fixture identity/hash mismatch")
    _require(results60["unit_tests"] == {"passed": 16, "failed": 0, "command": "python -m unittest -v"} and results60["pip_check"] == "passed", "chapter 60 results must record tests and pip check")
    _require(results60["toy_run"]["initial_mse"] == 21.0 and results60["toy_run"]["final_mse"] == 0.09078731868784178 and results60["toy_run"]["training_points"] == 4 and results60["toy_run"]["synthetic_only"] is True, "chapter 60 toy results changed")
    _require(results60["tracking_integrations"]["mlflow"]["status"] == "passed" and results60["tracking_integrations"]["wandb"]["mode"] == "offline" and results60["tracking_integrations"]["wandb"]["online_sync_performed"] is False, "chapter 60 local/offline tracking evidence mismatch")
    _require(all(value is False for key, value in results60["scope"].items() if key != "synthetic_fixture_only") and results60["scope"]["synthetic_fixture_only"] is True, "chapter 60 result manifest must retain its non-claims")
    environment60 = json.loads((project60 / "environment.json").read_text(encoding="utf-8"))
    _require(environment60["packages"] == {"mlflow": "3.18.0", "wandb": "0.31.0", "PyYAML": "6.0.3"} and environment60["requirements"]["pip_check"] == "passed", "chapter 60 tested dependency versions or pip check mismatch")
    _require(environment60["fixture"]["sha256"] == fixture60_hash and environment60["container_reference"]["manifest_list_digest"] == "sha256:cf50a4f6ac4f026458b08d5222023d700ac806410dff5e9ca8728fa44f2b850f", "chapter 60 fixture/environment manifest digest mismatch")
    _require(environment60["validation_tools"]["docker"] == "unavailable" and environment60["validation_tools"]["kubectl"] == "unavailable", "chapter 60 must preserve Docker/Kubernetes execution limitation")

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
    _require("fa-academy-v95" in sw and "v94" not in sw.splitlines()[0], "service worker cache version was not advanced")
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
        "./assets/images/covers/microsoft-ai-for-beginners-cover.webp",
        "./assets/images/covers/microsoft-generative-ai-for-beginners-cover.webp",
        "./assets/images/covers/microsoft-ml-for-beginners-cover.webp",
        "./assets/images/covers/microsoft-data-science-for-beginners-cover.webp",
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
        "./book-engineering/diagrams/v4-ch07-diffusion.svg",
        "./book-engineering/chapters/53-image-video-generation.md",
        "./book-engineering/chapters/53-audit-report-fa.md",
        "./book-engineering/answers/53-image-video-generation-fa.md",
        "./book-engineering/projects/53-diffusion-lab/README.md",
        "./book-engineering/projects/53-diffusion-lab/diffusion_lab.py",
        "./book-engineering/projects/53-diffusion-lab/test_diffusion_lab.py",
        "./book-engineering/projects/53-diffusion-lab/sample_mixture.json",
        "./book-engineering/projects/53-diffusion-lab/results.json",
        "./book-engineering/diagrams/v4-ch08-resource-estimation.svg",
        "./book-engineering/chapters/54-resource-estimation.md",
        "./book-engineering/chapters/54-audit-report-fa.md",
        "./book-engineering/answers/54-resource-estimation-fa.md",
        "./book-engineering/projects/54-resource-estimation/README.md",
        "./book-engineering/projects/54-resource-estimation/resource_estimator.py",
        "./book-engineering/projects/54-resource-estimation/test_resource_estimator.py",
        "./book-engineering/projects/54-resource-estimation/sample_profiles.json",
        "./book-engineering/projects/54-resource-estimation/results.json",
        "./book-engineering/diagrams/v4-ch09-lab-design.svg",
        "./book-engineering/chapters/55-ai-lab-design.md",
        "./book-engineering/chapters/55-audit-report-fa.md",
        "./book-engineering/answers/55-ai-lab-design.md",
        "./book-engineering/projects/55-ai-lab-design/README.md",
        "./book-engineering/projects/55-ai-lab-design/lab_design_planner.py",
        "./book-engineering/projects/55-ai-lab-design/test_lab_design_planner.py",
        "./book-engineering/projects/55-ai-lab-design/sample_labs.json",
        "./book-engineering/projects/55-ai-lab-design/results.json",
        "./assets/images/babak-ai/v4-ch10-tco-timeline.svg",
        "./book-engineering/chapters/56-ai-compute-budget.md",
        "./book-engineering/chapters/56-audit-report-fa.md",
        "./book-engineering/answers/56-ai-compute-budget-fa.md",
        "./book-engineering/projects/56-ai-compute-budget/README.md",
        "./book-engineering/projects/56-ai-compute-budget/budget_model.py",
        "./book-engineering/projects/56-ai-compute-budget/test_budget_model.py",
        "./book-engineering/projects/56-ai-compute-budget/sample_budget.json",
        "./book-engineering/projects/56-ai-compute-budget/results.json",
        "./book-engineering/diagrams/v4-ch11-framework-selection.svg",
        "./book-engineering/chapters/57-ml-frameworks.md",
        "./book-engineering/chapters/57-audit-report-fa.md",
        "./book-engineering/answers/57-ml-frameworks-fa.md",
        "./book-engineering/projects/57-framework-lab/README.md",
        "./book-engineering/projects/57-framework-lab/framework_compare.py",
        "./book-engineering/projects/57-framework-lab/test_framework_compare.py",
        "./book-engineering/projects/57-framework-lab/sample_problem.json",
        "./book-engineering/projects/57-framework-lab/results.json",
        "./book-engineering/diagrams/v4-ch12-huggingface-stack.svg",
        "./book-engineering/chapters/58-huggingface-stack.md",
        "./book-engineering/chapters/58-audit-report-fa.md",
        "./book-engineering/answers/58-huggingface-stack-fa.md",
        "./book-engineering/projects/58-huggingface-stack/README.md",
        "./book-engineering/projects/58-huggingface-stack/pipeline_demo.py",
        "./book-engineering/projects/58-huggingface-stack/test_pipeline_demo.py",
        "./book-engineering/projects/58-huggingface-stack/sample_data.jsonl",
        "./book-engineering/projects/58-huggingface-stack/fixture_manifest.json",
        "./book-engineering/projects/58-huggingface-stack/environment.json",
        "./book-engineering/projects/58-huggingface-stack/results.json",
        "./book-engineering/projects/58-huggingface-stack/requirements.txt",
        "./book-engineering/projects/58-huggingface-stack/requirements-cpu.txt",
        "./book-engineering/projects/58-huggingface-stack/requirements-lock-linux-py313.txt",
        "./book-engineering/diagrams/v4-ch13-gpu-systems.svg",
        "./book-engineering/chapters/59-gpu-systems.md",
        "./book-engineering/chapters/59-audit-report-fa.md",
        "./book-engineering/answers/59-gpu-systems-fa.md",
        "./book-engineering/projects/59-gpu-systems/README.md",
        "./book-engineering/projects/59-gpu-systems/gpu_systems_demo.py",
        "./book-engineering/projects/59-gpu-systems/test_gpu_systems_demo.py",
        "./book-engineering/projects/59-gpu-systems/sample_layout.json",
        "./book-engineering/projects/59-gpu-systems/fixture_manifest.json",
        "./book-engineering/projects/59-gpu-systems/environment.json",
        "./book-engineering/projects/59-gpu-systems/results.json",
        "./book-engineering/projects/59-gpu-systems/requirements.txt",
        "./book-engineering/projects/59-gpu-systems/requirements-cpu.txt",
        "./book-engineering/projects/59-gpu-systems/requirements-lock-linux-py313.txt",
        "./book-engineering/diagrams/v4-ch14-mlops.svg",
        "./book-engineering/chapters/60-mlops.md",
        "./book-engineering/chapters/60-audit-report-fa.md",
        "./book-engineering/answers/60-mlops-fa.md",
        "./book-engineering/projects/60-mlops/README.md",
        "./book-engineering/projects/60-mlops/experiment_ops.py",
        "./book-engineering/projects/60-mlops/test_experiment_ops.py",
        "./book-engineering/projects/60-mlops/sample_experiment.json",
        "./book-engineering/projects/60-mlops/fixture_manifest.json",
        "./book-engineering/projects/60-mlops/environment.json",
        "./book-engineering/projects/60-mlops/results.json",
        "./book-engineering/projects/60-mlops/requirements.txt",
        "./book-engineering/projects/60-mlops/requirements-cpu.txt",
        "./book-engineering/projects/60-mlops/requirements-lock-linux-py313.txt",
        "./book-engineering/projects/60-mlops/Dockerfile",
        "./book-engineering/projects/60-mlops/job.yaml",
    )
    for item in required_cache_paths:
        _require(item in sw, f"service worker does not precache {item}")

    print(
        f"PASS volume 4: {len(book['chapters'])}/{builder.PLANNED_CHAPTERS} chapters, "
        f"{sum(len(ch['sections']) for ch in book['chapters'])} sections, "
        f"{len(math_nodes) + len(math48) + len(math49) + len(math50) + len(math51) + len(math52) + len(math53_nodes) + len(math54_nodes) + len(math55_nodes) + len(math56_nodes) + len(math57_nodes) + len(math58_nodes) + len(math59_nodes) + len(math60_nodes)} accessible MathML expressions, exact appendices, reports/answers/fixtures present"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL volume 4: {exc}", file=sys.stderr)
        raise
