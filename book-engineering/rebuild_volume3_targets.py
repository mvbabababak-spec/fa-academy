"""Safely rebuild the currently approved Volume 3 source corrections.

The explicit target range is global chapters 33–46 (local chapters 1–14). This
release only applies reviewed metadata, glossary, accessibility, and targeted
project/content corrections. It never adds/removes chapters or sections, changes
stable IDs, or changes project files; executable appendices are checked by
check_volume3.py. Default mode is read-only validation. Pass --write to refresh
data.json, then run build_volume3.py to regenerate the standalone Markdown file.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

import mistune

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data.json"
VOLUME_ID = "art-science-intelligence-v3"
APPROVED_GLOBAL_CHAPTERS = tuple(range(33, 47))
RENDER = mistune.create_markdown(escape=False, plugins=["table"])


def render_sections(source_text: str, relative_path: str, old_sections: list[dict]) -> list[dict]:
    """Render reviewed sources while preserving each section's identity."""
    parts = re.split(r"^## (.+)$", source_text, flags=re.MULTILINE)
    if (len(parts) - 1) // 2 != len(old_sections):
        raise ValueError(f"H2 count changed in {relative_path}; refusing to modify published IDs")
    new_sections: list[dict] = []
    for index, old in enumerate(old_sections):
        part_index = 2 * index + 1
        title = parts[part_index].strip()
        body = (parts[0] + "\n" if index == 0 else "") + "## " + parts[part_index] + "\n" + parts[part_index + 1]
        section = dict(old)
        if section.get("file") != relative_path:
            raise ValueError(f"source path changed in existing section {section.get('id')}")
        section["title"] = title
        section["html"] = RENDER(body)
        if not section["html"].strip():
            raise ValueError(f"empty rendered section {section.get('id')}")
        new_sections.append(section)
    return new_sections


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate or rebuild only the approved Volume 3 corrections")
    parser.add_argument("--write", action="store_true", help="write refreshed section HTML to data.json")
    args = parser.parse_args()

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    books = [book for book in data.get("books", []) if book.get("id") == VOLUME_ID]
    if len(books) != 1:
        raise SystemExit("expected exactly one published Volume 3 book record")
    book = books[0]
    chapters = book.get("chapters", [])
    if len(chapters) != len(APPROVED_GLOBAL_CHAPTERS):
        raise SystemExit("expected local chapters 1–14 / global chapters 33–46; refusing partial rebuild")

    changes: list[tuple[int, list[dict]]] = []
    for local_number, global_number in enumerate(APPROVED_GLOBAL_CHAPTERS, 1):
        chapter = chapters[local_number - 1]
        if chapter.get("num") != local_number or chapter.get("id") != f"art-science-v3-ch{local_number:02}":
            raise SystemExit(f"unexpected chapter identity at local {local_number}; refusing rebuild")
        if not chapter.get("sections"):
            raise SystemExit(f"chapter {global_number} has no sections")
        relative_files = {section.get("file") for section in chapter["sections"]}
        if len(relative_files) != 1:
            raise SystemExit(f"chapter {global_number} does not have exactly one source file")
        relative_path = next(iter(relative_files))
        if not relative_path.startswith(f"book-engineering/chapters/{global_number}-"):
            raise SystemExit(f"chapter {global_number} points to unexpected source {relative_path!r}")
        source_path = ROOT / relative_path
        if not source_path.is_file():
            raise SystemExit(f"missing chapter source: {source_path}")
        refreshed = render_sections(source_path.read_text(encoding="utf-8"), relative_path, chapter["sections"])
        for old, new in zip(chapter["sections"], refreshed):
            if old.get("id") != new.get("id"):
                raise SystemExit(f"stable section ID changed in {relative_path}; refusing rebuild")
        if refreshed != chapter["sections"]:
            changes.append((local_number, refreshed))

    if not changes:
        print("PASS Volume 3 targeted rebuild check: all 14 source chapters match data.json; stable IDs unchanged.")
        return

    if not args.write:
        changed = ", ".join(str(number) for number, _ in changes)
        raise SystemExit(f"source-render mismatch in local chapters {changed}; review diffs, then rerun with --write")

    for local_number, refreshed in changes:
        chapters[local_number - 1]["sections"] = refreshed
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(
        "Updated reviewed Volume 3 section HTML for local chapters "
        + ", ".join(str(number) for number, _ in changes)
        + "; chapter/section IDs and counts were preserved. Run build_volume3.py next."
    )


if __name__ == "__main__":
    main()
