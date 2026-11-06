"""Structural, accessibility, source, image, answer-key and project-sync checks."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import json
import re

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BOOK_ID = "art-science-intelligence-v3"
PLANNED = 14


class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images: list[dict[str, str | None]] = []
        self.math: list[dict[str, str | None]] = []
        self.links: list[dict[str, str | None]] = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "img":
            self.images.append(values)
        elif tag == "math":
            self.math.append(values)
        elif tag == "a":
            self.links.append(values)


data = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
books = [book for book in data["books"] if book.get("id") == BOOK_ID]
assert len(books) == 1, "exactly one volume 3 book record is required"
book = books[0]
chapters = book.get("chapters", [])
assert 1 <= len(chapters) <= PLANNED
assert [chapter.get("num") for chapter in chapters] == list(range(1, len(chapters) + 1))
assert book.get("author") == "Babak & Ai"
assert "۱۴ فصل" in book.get("subtitle", "")

all_ids: list[str] = []
inspector = Inspector()
section_count = 0
source_files: set[str] = set()
for local_number, chapter in enumerate(chapters, 1):
    global_number = local_number + 32
    assert chapter.get("id") == f"art-science-v3-ch{local_number:02}"
    all_ids.append(chapter["id"])
    assert chapter.get("sections"), chapter["id"]
    file_names = {section.get("file") for section in chapter["sections"]}
    assert len(file_names) == 1, (chapter["id"], file_names)
    relative_source = next(iter(file_names))
    assert relative_source.startswith(f"book-engineering/chapters/{global_number}-"), relative_source
    source = ROOT / relative_source
    assert source.is_file(), source
    source_text = source.read_text(encoding="utf-8")
    source_files.add(relative_source)
    expected_sections = len(re.findall(r"^## .+$", source_text, flags=re.MULTILINE))
    assert len(chapter["sections"]) == expected_sections
    for section_index, section in enumerate(chapter["sections"], 1):
        assert section["id"] == f"art-science-v3-ch{local_number:02}-s{section_index:02}"
        assert section.get("html", "").strip(), section["id"]
        all_ids.append(section["id"])
        inspector.feed(section["html"])
        section_count += 1

assert len(all_ids) == len(set(all_ids)), "duplicate chapter or section ID"
assert len(inspector.images) >= len(chapters), "each current chapter must have a checked image"
for image in inspector.images:
    src = image.get("src") or ""
    alt = image.get("alt") or ""
    assert src.startswith("assets/images/") and src.endswith(".webp") and ".." not in Path(src).parts, src
    assert alt.strip() and "شکل" in alt, alt
    if "v3-ch01-tokenization.webp" in src:
        assert "BPE" in alt and "تعبیه" in alt, alt
    if "v3-ch02-attention.webp" in src:
        assert all(term in alt for term in ("Q/K/V", "Lq×Lk", "Lq×dv")), alt
    if "v3-ch03-self-attention.webp" in src:
        assert all(term in alt for term in ("Self-Attention", "Q/K/V", "j≤i", "j>i")), alt
    if "v3-ch04-position-block.webp" in src:
        assert all(term in alt for term in ("PE", "RoPE", "LayerNorm", "FFN")), alt
    if "v3-ch05-architecture-matrix.webp" in src:
        assert all(term in alt for term in ("Encoder-only", "Decoder-only", "Encoder–Decoder", "cross-attention", "True=مسدود")), alt
    if "v3-ch06-efficiency-map.webp" in src:
        assert all(term in alt for term in ("KV Cache", "GQA", "Sparse Attention", "FlashAttention", "MoE", "RULER", "NoLiMa", "OOLONG")), alt
    if "v3-ch07-multimodal-bridge.webp" in src:
        assert all(term in alt for term in ("ViT", "log-Mel", "InfoNCE", "embedding", "cross-attention")), alt
    if "v3-ch08-data-pipeline.webp" in src:
        assert all(term in alt for term in ("مجوز", "manifest", "group_id", "train", "validation", "test", "tokenizer")), alt
    if "v3-ch09-training-loop.webp" in src:
        assert all(term in alt for term in ("شکل ۳-۹-۱", "train", "validation", "test", "Embedding", "MLP", "logits", "cross-entropy", "گرادیان")), alt
    if "v3-ch10-mini-gpt-budget.webp" in src:
        assert all(term in alt for term in ("شکل ۳-۱۰-۱", "Decoder-only", "۱۱۷٬۳۵۰", "score-equivalent", "MiB")), alt
    if "v3-ch11-corpus-audit.webp" in src:
        assert all(term in alt for term in ("شکل ۳-۱۱-۱", "منشأ", "کیفیت", "تکرار", "ارزیابی", "مجوز")), alt
    path = ROOT / src
    assert path.is_file(), path
    with Image.open(path) as im:
        assert im.format == "WEBP" and im.width >= 1000 and im.height >= 600, (src, im.format, im.size)

minimum_math = {1: 5, 2: 7, 3: 10, 4: 15, 5: 18}.get(len(chapters), 24)
assert len(inspector.math) >= minimum_math, f"expected at least {minimum_math} MathML blocks, found {len(inspector.math)}"
assert all((math.get("aria-label") or "").strip() for math in inspector.math)

answer_paths = [
    href for link in inspector.links
    if (href := link.get("href")) and "book-engineering/answers/" in href
]
assert len(answer_paths) == len(chapters), answer_paths
for chapter, href in zip(chapters, answer_paths):
    source_stem = Path(chapter["sections"][0]["file"]).stem
    expected = f"book-engineering/answers/{source_stem}-fa.md"
    assert href == expected, (href, expected)
    answer = ROOT / href
    assert answer.is_file() and len(re.findall(r"\S+", answer.read_text(encoding="utf-8"))) >= 300, href

# Chapter 33's source code remains byte-for-byte aligned with its tested project.
source = ROOT / "book-engineering/chapters/33-tokenization.md"
code = (ROOT / "book-engineering/projects/33-tokenization/tokenizer_bpe.py").read_text(encoding="utf-8").rstrip()
blocks = re.findall(r"```python\n(.*?)\n```", source.read_text(encoding="utf-8"), flags=re.DOTALL)
assert blocks and blocks[-1] == code, "chapter 33 executable tokenizer differs from tested project"
for project_file in [
    "tokenizer_bpe.py", "test_tokenizer_bpe.py", "test_embedding_lookup.py", "README.md"
]:
    assert (ROOT / "book-engineering/projects/33-tokenization" / project_file).is_file(), project_file

if len(chapters) >= 2:
    source = ROOT / "book-engineering/chapters/34-attention.md"
    project = ROOT / "book-engineering/projects/34-attention"
    code = (project / "attention.py").read_text(encoding="utf-8").rstrip()
    blocks = re.findall(r"```python\n(.*?)\n```", source.read_text(encoding="utf-8"), flags=re.DOTALL)
    assert blocks and blocks[-1] == code, "chapter 34 executable attention code differs from tested project"
    for project_file in ["attention.py", "test_attention.py", "README.md"]:
        assert (project / project_file).is_file(), project_file
    assert (ROOT / "book-engineering/create_v3_ch02_image.py").is_file()
    assert (ROOT / "book-engineering/chapters/34-audit-report-fa.md").is_file()

if len(chapters) >= 3:
    source = ROOT / "book-engineering/chapters/35-self-attention.md"
    project = ROOT / "book-engineering/projects/35-self-attention"
    code = (project / "causal_multihead.py").read_text(encoding="utf-8").rstrip()
    blocks = re.findall(r"```python\n(.*?)\n```", source.read_text(encoding="utf-8"), flags=re.DOTALL)
    assert blocks and blocks[-1] == code, "chapter 35 executable attention code differs from tested project"
    for project_file in ["causal_multihead.py", "test_causal_multihead.py", "README.md"]:
        assert (project / project_file).is_file(), project_file
    assert (ROOT / "book-engineering/create_v3_ch03_image.py").is_file()
    assert (ROOT / "book-engineering/chapters/35-audit-report-fa.md").is_file()

if len(chapters) >= 4:
    source = ROOT / "book-engineering/chapters/36-position-normalization.md"
    project = ROOT / "book-engineering/projects/36-position-normalization"
    code = (project / "transformer_block.py").read_text(encoding="utf-8").rstrip()
    blocks = re.findall(r"```python\n(.*?)\n```", source.read_text(encoding="utf-8"), flags=re.DOTALL)
    assert blocks and blocks[-1] == code, "chapter 36 executable code differs from tested project"
    for project_file in ["transformer_block.py", "test_transformer_block.py", "README.md"]:
        assert (project / project_file).is_file(), project_file
    assert (ROOT / "book-engineering/create_v3_ch04_image.py").is_file()
    assert (ROOT / "book-engineering/chapters/36-audit-report-fa.md").is_file()

if len(chapters) >= 5:
    source = ROOT / "book-engineering/chapters/37-encoder-decoder.md"
    project = ROOT / "book-engineering/projects/37-encoder-decoder"
    code = (project / "transformer_architectures.py").read_text(encoding="utf-8").rstrip()
    blocks = re.findall(r"```python\n(.*?)\n```", source.read_text(encoding="utf-8"), flags=re.DOTALL)
    assert blocks and blocks[-1] == code, "chapter 37 executable architecture code differs from tested project"
    for project_file in ["transformer_architectures.py", "test_transformer_architectures.py", "README.md"]:
        assert (project / project_file).is_file(), project_file
    assert (ROOT / "book-engineering/create_v3_ch05_image.py").is_file()
    assert (ROOT / "book-engineering/chapters/37-audit-report-fa.md").is_file()

if len(chapters) >= 6:
    source = ROOT / "book-engineering/chapters/38-long-context.md"
    project = ROOT / "book-engineering/projects/38-long-context"
    code = (project / "efficient_attention.py").read_text(encoding="utf-8").rstrip()
    blocks = re.findall(r"```python\n(.*?)\n```", source.read_text(encoding="utf-8"), flags=re.DOTALL)
    assert blocks and blocks[-1] == code, "chapter 38 executable code differs from tested project"
    for project_file in ["efficient_attention.py", "test_efficient_attention.py", "README.md"]:
        assert (project / project_file).is_file(), project_file
    assert (ROOT / "book-engineering/create_v3_ch06_image.py").is_file()
    assert (ROOT / "book-engineering/chapters/38-audit-report-fa.md").is_file()

if len(chapters) >= 7:
    source = ROOT / "book-engineering/chapters/39-multimodal-transformer.md"
    project = ROOT / "book-engineering/projects/39-multimodal-transformer"
    code = (project / "multimodal_alignment.py").read_text(encoding="utf-8").rstrip()
    blocks = re.findall(r"```python\n(.*?)\n```", source.read_text(encoding="utf-8"), flags=re.DOTALL)
    assert blocks and blocks[-1] == code, "chapter 39 executable code differs from tested project"
    for project_file in ["multimodal_alignment.py", "test_multimodal_alignment.py", "README.md"]:
        assert (project / project_file).is_file(), project_file
    assert (ROOT / "book-engineering/create_v3_ch07_image.py").is_file()
    assert (ROOT / "book-engineering/chapters/39-audit-report-fa.md").is_file()

if len(chapters) >= 8:
    source = ROOT / "book-engineering/chapters/40-small-data-project.md"
    project = ROOT / "book-engineering/projects/40-small-data-project"
    code = (project / "small_corpus.py").read_text(encoding="utf-8").rstrip()
    blocks = re.findall(r"```python\n(.*?)\n```", source.read_text(encoding="utf-8"), flags=re.DOTALL)
    assert blocks and blocks[-1] == code, "chapter 40 executable code differs from tested project"
    for project_file in ["small_corpus.py", "test_small_corpus.py", "sample_corpus.jsonl", "README.md"]:
        assert (project / project_file).is_file(), project_file
    assert (ROOT / "book-engineering/create_v3_ch08_image.py").is_file()
    assert (ROOT / "book-engineering/chapters/40-audit-report-fa.md").is_file()

if len(chapters) >= 9:
    source = ROOT / "book-engineering/chapters/41-first-language-model.md"
    project = ROOT / "book-engineering/projects/41-first-language-model"
    code = (project / "tiny_lm.py").read_text(encoding="utf-8").rstrip()
    blocks = re.findall(r"```python\n(.*?)\n```", source.read_text(encoding="utf-8"), flags=re.DOTALL)
    assert blocks and blocks[-1] == code, "chapter 41 executable code differs from tested project"
    for project_file in ["tiny_lm.py", "test_tiny_lm.py", "README.md", ".gitignore"]:
        assert (project / project_file).is_file(), project_file
    assert (ROOT / "book-engineering/create_v3_ch09_image.py").is_file()
    assert (ROOT / "book-engineering/diagrams/v3-ch09-training-loop.svg").is_file()
    assert (ROOT / "book-engineering/chapters/41-audit-report-fa.md").is_file()

if len(chapters) >= 10:
    source = ROOT / "book-engineering/chapters/42-mini-gpt.md"
    project = ROOT / "book-engineering/projects/42-mini-gpt-design"
    code = (project / "mini_gpt_design.py").read_text(encoding="utf-8").rstrip()
    blocks = re.findall(r"```python\n(.*?)\n```", source.read_text(encoding="utf-8"), flags=re.DOTALL)
    assert blocks and blocks[-1] == code, "chapter 42 executable code differs from tested project"
    for project_file in ["mini_gpt_design.py", "test_mini_gpt_design.py", "README.md"]:
        assert (project / project_file).is_file(), project_file
    assert (ROOT / "book-engineering/create_v3_ch10_image.py").is_file()
    assert (ROOT / "book-engineering/diagrams/v3-ch10-mini-gpt-budget.svg").is_file()
    assert (ROOT / "book-engineering/chapters/42-audit-report-fa.md").is_file()

if len(chapters) >= 11:
    source = ROOT / "book-engineering/chapters/43-corpus.md"
    project = ROOT / "book-engineering/projects/43-corpus-audit"
    code = (project / "corpus_audit.py").read_text(encoding="utf-8").rstrip()
    blocks = re.findall(r"```python\n(.*?)\n```", source.read_text(encoding="utf-8"), flags=re.DOTALL)
    assert blocks and blocks[-1] == code, "chapter 43 executable audit code differs from tested project"
    for project_file in [
        "corpus_audit.py", "test_corpus_audit.py", "sample_corpus.jsonl",
        "sample_evaluation.jsonl", "README.md", ".gitignore"
    ]:
        assert (project / project_file).is_file(), project_file
    assert (ROOT / "book-engineering/create_v3_ch11_image.py").is_file()
    assert (ROOT / "book-engineering/diagrams/v3-ch11-corpus-audit.svg").is_file()
    assert (ROOT / "book-engineering/chapters/43-audit-report-fa.md").is_file()

full_text = ROOT / "volume-3-full-fa.md"
assert full_text.is_file()
full_text_value = full_text.read_text(encoding="utf-8")
for relative_source in source_files:
    assert (ROOT / relative_source).read_text(encoding="utf-8").strip() in full_text_value
print(f"PASS volume 3: {len(chapters)}/{PLANNED} chapters, {section_count} sections, {len(inspector.images)} local WebP images with semantic alt, {len(answer_paths)} detailed answer keys, {len(inspector.math)} accessible MathML blocks")
