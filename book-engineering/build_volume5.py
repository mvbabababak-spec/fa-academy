"""Append authored volume 5 chapters without rewriting an existing chapter."""
from __future__ import annotations

import json
import posixpath
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import mistune

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data.json"
SW_PATH = ROOT / "sw.js"
VOLUME_ID = "art-science-intelligence-v5"
PLANNED_CHAPTERS = 12
COVER_PATH = "assets/images/covers/volume-5-cover.png"
COVER_SHA256 = "0a462880584e9f5190f0a16f0e89ea479e20eae3f78c02ed026843c0f035d754"
PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
RENDER = mistune.create_markdown(escape=False, plugins=["table"])

# Local volume numbering 1–12 maps to roadmap chapters 62–73.
SPECS = [
    (1, 62, "62-benchmarking-evaluation", "Benchmarking، طراحی آزمون، معیارها، ارزیابی انسانی، عدم‌قطعیت و آلودگی بنچمارک", "◉"),
    (2, 63, "63-hallucination-bias-robustness", "توهم، سوگیری، استحکام، تبیین‌پذیری و تفسیرپذیری", "⌕"),
    (3, 64, "64-red-teaming-security", "Red Teaming، حملات خصمانه، Prompt Injection، مسموم‌سازی داده، استخراج مدل و حریم خصوصی", "⚑"),
    (4, 65, "65-alignment-governance", "هم‌ترازی، حاکمیت، مستندسازی، مدل‌کارت، داده‌کارت و مدیریت ریسک", "◇"),
    (5, 66, "66-ai-product-api", "API و FastAPI، Backend، Frontend، برنامهٔ وب و موبایل؛ قرارداد داده و آزمایش", "⌘"),
    (6, 67, "67-model-serving-operations", "سرو مدل، بهینه‌سازی استنتاج، Cache، صف، تأخیر و توان عملیاتی", "⇢"),
    (7, 68, "68-product-security-monitoring", "احراز هویت، محدودیت نرخ، ثبت رخداد، پایش، حریم خصوصی و پاسخ به رخداد", "▣"),
    (8, 69, "69-deployment-cicd", "استقرار ابری و محلی، نسخه‌بندی، CI/CD، مقیاس‌پذیری، بازگشت نسخه و هزینهٔ نگه‌داری", "↗"),
    (9, 70, "70-reading-papers-reproduction", "خواندن مقاله، بررسی ادعا و روش، تحلیل معماری و بازتولید نتایج", "⌗"),
    (10, 71, "71-research-design-statistics", "طراحی آزمایش، فرضیه و معیار، ساخت دیتاست، مقایسهٔ مدل‌ها و تحلیل آماری", "∴"),
    (11, 72, "72-research-architecture-community", "توسعهٔ معماری، نوشتن مقاله، مشارکت متن‌باز، تشکیل تیم و برنامهٔ پژوهشی بلندمدت", "⌂"),
    (12, 73, "73-capstone-responsible-model", "پروژهٔ نهایی: طراحی، آموزش، ارزیابی و انتشار مسئولانهٔ مدل مستقل با گزارش قابل‌بازتولید", "✦"),
]

APPENDIX_PROJECTS = {
    62: "book-engineering/projects/62-evaluation-lab/evaluation_lab.py",
    63: "book-engineering/projects/63-model-behavior-lab/model_behavior_lab.py",
    64: "book-engineering/projects/64-red-team-lab/red_team_lab.py",
    65: "book-engineering/projects/65-governance-lab/governance_check.py",
    66: "book-engineering/projects/66-ai-product-api/app.py",
}
DIAGRAMS = {
    62: "book-engineering/diagrams/v5-ch01-evaluation-protocol.svg",
    63: "book-engineering/diagrams/v5-ch02-behavior-audit.svg",
    64: "book-engineering/diagrams/v5-ch03-red-team-pipeline.svg",
    65: "book-engineering/diagrams/v5-ch04-governance-cycle.svg",
    66: "book-engineering/diagrams/v5-ch05-api-contract.svg",
}
ANSWER_KEYS = {
    62: "book-engineering/answers/62-benchmarking-evaluation-fa.md",
    63: "book-engineering/answers/63-hallucination-bias-robustness-fa.md",
    64: "book-engineering/answers/64-red-teaming-security-fa.md",
    65: "book-engineering/answers/65-alignment-governance-fa.md",
    66: "book-engineering/answers/66-ai-product-api-fa.md",
}
PROJECT_DIRS = {
    62: "book-engineering/projects/62-evaluation-lab",
    63: "book-engineering/projects/63-model-behavior-lab",
    64: "book-engineering/projects/64-red-team-lab",
    65: "book-engineering/projects/65-governance-lab",
    66: "book-engineering/projects/66-ai-product-api",
}


def fa_digits(value: int) -> str:
    return str(value).translate(PERSIAN_DIGITS)


def _verify_code_appendix(global_num: int, text: str) -> None:
    relative = APPENDIX_PROJECTS.get(global_num)
    if relative is None:
        return
    project_path = ROOT / relative
    if not project_path.is_file():
        raise FileNotFoundError(project_path)
    marker = b"\n```python\n"
    _, found, tail = text.encode("utf-8").rpartition(marker)
    closing = tail.rfind(b"```")
    project_code = project_path.read_bytes()
    if not found or closing < 0 or tail[:closing] != project_code or tail[closing + 3:] not in (b"", b"\n"):
        raise ValueError(f"chapter {global_num} executable appendix must match the tested project byte-for-byte")


def rewrite_reader_links(html: str, source_relative: str) -> str:
    """Resolve source-relative links for sections injected into the site root.

    The Markdown files keep ordinary portable relative links. The web reader
    injects rendered sections into a page rooted above ``book-engineering``, so
    relative href/src values must be rewritten for that view only.
    """
    source_dir = posixpath.dirname(source_relative)

    def rewrite(match: re.Match[str]) -> str:
        value = match.group(2)
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return match.group(0)
        if parsed.path.startswith(("book-engineering/", "assets/", "volume-5-full-fa.md")):
            return match.group(0)
        normalized = posixpath.normpath(posixpath.join(source_dir, parsed.path))
        if normalized == ".." or normalized.startswith("../"):
            return match.group(0)
        resolved = urlunsplit(("", "", normalized, parsed.query, parsed.fragment))
        return f'{match.group(1)}="{resolved}"'

    return re.sub(r'\b(href|src)="([^"]*)"', rewrite, html)


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
        if global_num >= 66:
            html = rewrite_reader_links(html, relative)
        if not html.strip():
            raise ValueError(f"empty rendered section {global_num}.{section_no}")
        sections.append({
            "id": f"art-science-v5-ch{local_num:02}-s{section_no:02}",
            "title": parts[index].strip(),
            "file": relative,
            "html": html,
        })
    return {
        "num": local_num,
        "id": f"art-science-v5-ch{local_num:02}",
        "title": title,
        "icon": icon,
        "sections": sections,
    }


def available_specs() -> list[tuple[int, int, str, str, str]]:
    authored = [spec for spec in SPECS if (ROOT / "book-engineering/chapters" / f"{spec[2]}.md").is_file()]
    expected = list(range(1, len(authored) + 1))
    if [spec[0] for spec in authored] != expected:
        raise RuntimeError("volume 5 source chapters must be authored in order without gaps")
    return authored


def expected_markdown(chapters: list[dict], specs: list[tuple[int, int, str, str, str]]) -> str:
    contents = [
        "# هنر و علم ساخت هوش — جلد پنجم",
        "",
        "**The Art & Science of Building Intelligence | Babak & Ai**",
        "",
        f"وضعیت: ۱۲ فصل در نقشه؛ {fa_digits(len(chapters))} فصل تا این انتشار نگارش و آزموده شده‌اند. این فایل Markdown است؛ PDF و EPUB تولید و آزموده نشده‌اند.",
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


def _v5_offline_paths(specs: list[tuple[int, int, str, str, str]]) -> list[str]:
    paths = [COVER_PATH, "volume-5-full-fa.md"]
    for _, global_num, slug, _, _ in specs:
        paths.append(f"book-engineering/chapters/{slug}.md")
        paths.append(f"book-engineering/chapters/{global_num}-audit-report-fa.md")
        diagram = DIAGRAMS.get(global_num)
        if diagram:
            paths.append(diagram)
        answer = ANSWER_KEYS.get(global_num)
        if answer:
            paths.append(answer)
        else:
            candidate = ROOT / "book-engineering/answers" / f"{slug}-fa.md"
            if candidate.is_file():
                paths.append(candidate.relative_to(ROOT).as_posix())
        project_dir_relative = PROJECT_DIRS.get(global_num)
        project_dir = ROOT / project_dir_relative if project_dir_relative else None
        if project_dir and project_dir.is_dir():
            for path in sorted(project_dir.rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts:
                    paths.append(path.relative_to(ROOT).as_posix())
    return list(dict.fromkeys(paths))


def update_service_worker(relative_paths: list[str]) -> bool:
    text = SW_PATH.read_text(encoding="utf-8")
    version_match = re.search(r"(?m)^const CACHE_NAME = 'fa-academy-v(\d+)';$", text)
    array_match = re.search(r"(const CORE_FILES = \[)(.*?)(\n\];)", text, flags=re.DOTALL)
    if not version_match or not array_match:
        raise RuntimeError("unrecognized service-worker cache structure; refusing to edit it")
    old_version = int(version_match.group(1))
    body = array_match.group(2)
    current = set(re.findall(r"['\"](\./[^'\"]+)['\"]", body))
    desired = ["./" + path.lstrip("./") for path in relative_paths]
    missing = [path for path in desired if path not in current]
    if not missing:
        return False
    for relative in relative_paths:
        if not (ROOT / relative).is_file():
            raise FileNotFoundError(ROOT / relative)
    if len(current) != len(re.findall(r"['\"](\./[^'\"]+)['\"]", body)):
        raise RuntimeError("duplicate paths found in service worker CORE_FILES")
    existing_body = body.rstrip("\n")
    if existing_body and not existing_body.rstrip().endswith(","):
        existing_body += ","
    new_body = existing_body + "\n" + "\n".join(f"  '{path}'," for path in missing)
    updated = text[:array_match.start(2)] + new_body + text[array_match.end(2):]
    new_version = old_version + 1
    updated = re.sub(r"fa-academy-v\d+", f"fa-academy-v{new_version}", updated)
    updated = re.sub(r"Service Worker v\d+", f"Service Worker v{new_version}", updated, count=1)
    SW_PATH.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    specs = available_specs()
    if not specs:
        raise RuntimeError("no authored volume 5 chapter source found")
    chapters = [build_chapter(spec) for spec in specs]
    matches = [book for book in data.get("books", []) if book.get("id") == VOLUME_ID]
    if len(matches) > 1:
        raise RuntimeError("duplicate volume 5 book records")

    subtitle = "ارزیابی، محصول و پژوهش | ۱۲ فصل"
    changed = False
    v4_index = next((index for index, book in enumerate(data["books"]) if book.get("id") == "art-science-intelligence-v4"), None)
    if v4_index is None:
        raise RuntimeError("volume 4 record not found; refusing to place volume 5 out of sequence")
    if matches:
        book = matches[0]
        book_index = data["books"].index(book)
        if book_index != v4_index + 1:
            raise RuntimeError("volume 5 record must immediately follow volume 4")
        existing = book.get("chapters", [])
        if len(existing) > len(chapters):
            raise RuntimeError("a volume 5 chapter source is missing; refusing to remove it")
        for index, old_chapter in enumerate(existing):
            if old_chapter != chapters[index]:
                raise RuntimeError(f"existing volume 5 chapter {index + 1} differs from its source; refusing to rewrite it")
        if len(existing) < len(chapters):
            book["chapters"] = existing + chapters[len(existing):]
            changed = True
        for key, value in (("subtitle", subtitle), ("author", "Babak Moradvand"), ("cover", COVER_PATH)):
            if book.get(key) != value:
                if key == "cover" and book.get("cover") not in (None, value):
                    raise RuntimeError("volume 5 cover changed unexpectedly; refusing to replace it")
                book[key] = value
                changed = True
    else:
        data["books"].insert(v4_index + 1, {
            "id": VOLUME_ID,
            "title": "هنر و علم ساخت هوش — جلد پنجم",
            "subtitle": subtitle,
            "author": "Babak Moradvand",
            "cover": COVER_PATH,
            "chapters": chapters,
        })
        changed = True

    if changed:
        DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    markdown = expected_markdown(chapters, specs)
    output_path = ROOT / "volume-5-full-fa.md"
    if not output_path.is_file() or output_path.read_text(encoding="utf-8") != markdown:
        output_path.write_text(markdown, encoding="utf-8")
    offline_paths = _v5_offline_paths(specs)
    sw_changed = update_service_worker(offline_paths)
    sw = SW_PATH.read_text(encoding="utf-8")
    version = re.search(r"fa-academy-v(\d+)", sw).group(1)
    print(
        f"Volume 5 {'updated' if changed else 'already matches'}: "
        f"{len(chapters)}/{PLANNED_CHAPTERS} chapters; "
        f"sections={[len(ch['sections']) for ch in chapters]}; "
        f"service worker {'advanced' if sw_changed else 'already includes these paths'} (v{version})"
    )


if __name__ == "__main__":
    main()
