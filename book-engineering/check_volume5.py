"""Structural, editorial, appendix, and offline-cache checks for Volume 5."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import struct
import unicodedata
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import build_volume5 as builder

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data.json"
CJK_RANGES = (
    (0x2E80, 0x2FFF), (0x3040, 0x30FF), (0x3400, 0x9FFF),
    (0xF900, 0xFAFF), (0xAC00, 0xD7AF),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def local_links(text: str, source: Path) -> list[str]:
    missing = []
    for target in re.findall(r"\]\(([^)]+)\)", text):
        target = target.strip()
        parsed = urlparse(target)
        if parsed.scheme or target.startswith("#") or target.startswith("mailto:"):
            continue
        target_path = Path(parsed.path)
        if target_path.parts and target_path.parts[0] in {"book-engineering", "assets", "volume-5-full-fa.md"}:
            path = (ROOT / target_path).resolve()
        else:
            path = (source.parent / target_path).resolve()
        if not path.is_file():
            missing.append(target)
    return missing


def cjk_chars(text: str) -> list[str]:
    return [char for char in set(text) if any(low <= ord(char) <= high for low, high in CJK_RANGES)]


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    books = [book for book in data.get("books", []) if book.get("id") == builder.VOLUME_ID]
    require(len(books) == 1, "data.json must contain exactly one volume 5 record")
    book = books[0]
    require(book.get("title") == "هنر و علم ساخت هوش — جلد پنجم", "volume 5 title mismatch")
    require(book.get("subtitle") == "ارزیابی، محصول و پژوهش | ۱۲ فصل", "volume 5 card subtitle mismatch")
    require(book.get("author") == "Babak Moradvand", "volume 5 author metadata mismatch")
    require(book.get("cover") == builder.COVER_PATH, "volume 5 cover path mismatch")
    ids = [item.get("id") for item in data.get("books", [])]
    require(ids.index(builder.VOLUME_ID) == ids.index("art-science-intelligence-v4") + 1,
            "volume 5 must immediately follow volume 4")
    for number in range(1, 5):
        legacy = next(item for item in data["books"] if item.get("id") == f"art-science-intelligence-v{number}")
        require(legacy.get("cover") == f"assets/images/covers/volume-{number}-cover.webp",
                f"legacy volume {number} cover reference changed")

    specs = builder.available_specs()
    require(bool(specs), "at least one volume 5 chapter must be authored")
    expected_chapters = [builder.build_chapter(spec) for spec in specs]
    require(book.get("chapters") == expected_chapters, "volume 5 data does not match immutable Markdown sources")
    require(len(expected_chapters) <= builder.PLANNED_CHAPTERS, "volume 5 exceeds the roadmap chapter count")
    require([chapter.get("num") for chapter in book["chapters"]] == list(range(1, len(specs) + 1)),
            "volume 5 local chapter numbering is not contiguous")

    for _, global_num, slug, _, _ in specs:
        source = ROOT / "book-engineering/chapters" / f"{slug}.md"
        answer_relative = builder.ANSWER_KEYS.get(global_num, f"book-engineering/answers/{slug}-fa.md")
        answer = ROOT / answer_relative
        report = ROOT / f"book-engineering/chapters/{global_num}-audit-report-fa.md"
        project_relative = builder.PROJECT_DIRS.get(global_num, f"book-engineering/projects/{global_num}-evaluation-lab")
        project_dir = ROOT / project_relative
        for path in (source, answer, report, project_dir / "README.md"):
            require(path.is_file(), f"missing chapter {global_num} deliverable: {path.relative_to(ROOT)}")
        source_text = source.read_text(encoding="utf-8")
        require(f"فصل محلی {fa_num(global_num - 61)} جلد پنجم = فصل سراسری {fa_num(global_num)}" in source_text,
                f"chapter {global_num} local/global mapping missing")
        require("تاریخ بازبینی منابع: ۷ نوامبر ۲۰۲۶" in source_text, f"chapter {global_num} source date missing")
        require(bool(re.search(r"^##\s+.*منابع و تاریخ بازبینی", source_text, flags=re.MULTILINE)), f"chapter {global_num} dated bibliography missing")
        require(bool(re.search(r"^##\s+.*تمرین‌ها", source_text, flags=re.MULTILINE)) and bool(re.search(r"^##\s+.*جمع‌بندی", source_text, flags=re.MULTILINE)), f"chapter {global_num} needs exercises and summary")
        require("پاسخ‌نامهٔ مستقل" in source_text and "پروژهٔ فصل" in source_text and "گزارش ممیزی" in source_text,
                f"chapter {global_num} must link its independent companion files")
        require(not local_links(source_text.split("## پیوست اجرایی", 1)[0], source),
                f"chapter {global_num} contains a broken local link: {local_links(source_text, source)}")
        require(not local_links(answer.read_text(encoding="utf-8"), answer),
                f"chapter {global_num} answer key contains a broken local link")
        math_nodes = re.findall(r"<math\b[^>]*>", source_text)
        require(all("aria-label=" in node for node in math_nodes), f"chapter {global_num} MathML lacks aria-label")
        require(source_text.count("**متن جایگزین فرمول:**") >= len(math_nodes),
                f"chapter {global_num} must provide a visible text alternative for each formula")
        images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source_text)
        require(bool(images), f"chapter {global_num} has no figure")
        for alt, image_path in images:
            require(bool(alt.strip()), f"chapter {global_num} figure has empty alt text")
            require((ROOT / image_path).is_file(), f"chapter {global_num} missing figure {image_path}")
        if global_num in (62, 63):
            questions = re.findall(r"(?m)^([۱-۸])\. (.+)$", source_text.split("## پیوست اجرایی", 1)[0])
            answer_questions = re.findall(r"(?m)^\*\*صورت پرسش:\*\* (.+)$", answer.read_text(encoding="utf-8"))
            require(len(questions) == 8 and [question for _, question in questions] == answer_questions,
                    f"chapter {global_num} answer key must preserve all eight question texts exactly")
        if global_num == 62:
            require(len(book["chapters"][0]["sections"]) == 26, "chapter 62 expected 26 sections")
        if global_num == 63:
            require(len(book["chapters"][1]["sections"]) == 34, "chapter 63 expected 34 sections")

        diagram_relative = builder.DIAGRAMS.get(global_num)
        if diagram_relative:
            diagram = ROOT / diagram_relative
            svg_root = ET.parse(diagram).getroot()
            require(svg_root.attrib.get("role") == "img", f"chapter {global_num} diagram must use role=img")
            require("aria-labelledby" in svg_root.attrib and svg_root.attrib.get("{http://www.w3.org/XML/1998/namespace}lang") == "fa",
                    f"chapter {global_num} SVG needs linked accessible title/description and Persian language")
            svg_ids = {element.attrib["id"] for element in svg_root.iter() if "id" in element.attrib}
            for element_id in svg_root.attrib["aria-labelledby"].split():
                require(element_id in svg_ids, f"chapter {global_num} SVG references missing ID {element_id}")

    cover_bytes = (ROOT / builder.COVER_PATH).read_bytes()
    require(cover_bytes.startswith(b"\x89PNG\r\n\x1a\n") and len(cover_bytes) >= 24,
            "volume 5 cover must be a valid PNG")
    require(hashlib.sha256(cover_bytes).hexdigest() == builder.COVER_SHA256,
            "volume 5 cover bytes do not match the supplied image")
    require(struct.unpack(">II", cover_bytes[16:24]) == (1024, 1536),
            "volume 5 supplied cover dimensions must remain 1024 by 1536")

    markdown_path = ROOT / "volume-5-full-fa.md"
    require(markdown_path.is_file(), "volume-5-full-fa.md is missing")
    require(markdown_path.read_text(encoding="utf-8") == builder.expected_markdown(expected_chapters, specs),
            "full Markdown does not match the chapter sources")

    sw = (ROOT / "sw.js").read_text(encoding="utf-8")
    cache_match = re.search(r"(?m)^const CACHE_NAME = 'fa-academy-v(\d+)';$", sw)
    header_match = re.search(r"Service Worker v(\d+)", sw.splitlines()[0])
    require(cache_match and header_match and cache_match.group(1) == header_match.group(1),
            "service-worker header and cache name must share a version")
    require(int(cache_match.group(1)) >= 97, "service-worker cache version was not advanced for volume 5")
    array_match = re.search(r"const CORE_FILES = \[(.*?)\n\];", sw, flags=re.DOTALL)
    require(array_match is not None, "service worker CORE_FILES list missing")
    cache_paths = re.findall(r"['\"](\./[^'\"]+)['\"]", array_match.group(1))
    require(len(cache_paths) == len(set(cache_paths)), "service worker CORE_FILES has duplicates")
    required = ["./" + path for path in builder._v5_offline_paths(specs)]
    require(set(required).issubset(cache_paths), f"service worker is missing volume 5 offline paths: {set(required)-set(cache_paths)}")
    for relative in builder._v5_offline_paths(specs):
        path = ROOT / relative
        require(path.is_file() and path.stat().st_size > 0, f"offline asset missing or empty: {relative}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        found = cjk_chars(text)
        require(not found, f"unexpected CJK codepoints in {relative}: {sorted(found)}")

    print(
        f"PASS volume 5 structure: {len(expected_chapters)}/{builder.PLANNED_CHAPTERS} chapters; "
        f"sections={[len(ch['sections']) for ch in expected_chapters]}; "
        f"accessible SVG/MathML, exact answer prompts and code appendix, Markdown, legacy covers, "
        f"{len(required)} offline paths; Service Worker v{cache_match.group(1)}"
    )


def fa_num(value: int) -> str:
    return str(value).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


if __name__ == "__main__":
    main()
