"""Chromium checks for volume 3 chapters, MathML, responsive layout and offline files."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BOOK_ID = "art-science-intelligence-v3"
TITLE = "هنر و علم ساخت هوش — جلد سوم"
CACHE_NAME = "fa-academy-v78"
OFFLINE_PATHS = [
    "volume-3-full-fa.md",
    "assets/images/babak-ai/v3-ch01-tokenization.webp",
    "book-engineering/chapters/33-tokenization.md",
    "book-engineering/chapters/33-audit-report-fa.md",
    "book-engineering/answers/33-tokenization-fa.md",
    "book-engineering/projects/33-tokenization/README.md",
    "book-engineering/projects/33-tokenization/tokenizer_bpe.py",
    "book-engineering/projects/33-tokenization/test_tokenizer_bpe.py",
    "book-engineering/projects/33-tokenization/test_embedding_lookup.py",
    "assets/images/babak-ai/v3-ch02-attention.webp",
    "book-engineering/chapters/34-attention.md",
    "book-engineering/chapters/34-audit-report-fa.md",
    "book-engineering/answers/34-attention-fa.md",
    "book-engineering/projects/34-attention/README.md",
    "book-engineering/projects/34-attention/attention.py",
    "book-engineering/projects/34-attention/test_attention.py",
    "assets/images/babak-ai/v3-ch03-self-attention.webp",
    "book-engineering/chapters/35-self-attention.md",
    "book-engineering/chapters/35-audit-report-fa.md",
    "book-engineering/answers/35-self-attention-fa.md",
    "book-engineering/projects/35-self-attention/README.md",
    "book-engineering/projects/35-self-attention/causal_multihead.py",
    "book-engineering/projects/35-self-attention/test_causal_multihead.py",
    "assets/images/babak-ai/v3-ch04-position-block.webp",
    "book-engineering/chapters/36-position-normalization.md",
    "book-engineering/chapters/36-audit-report-fa.md",
    "book-engineering/answers/36-position-normalization-fa.md",
    "book-engineering/projects/36-position-normalization/README.md",
    "book-engineering/projects/36-position-normalization/transformer_block.py",
    "book-engineering/projects/36-position-normalization/test_transformer_block.py",
    "assets/images/babak-ai/v3-ch05-architecture-matrix.webp",
    "book-engineering/chapters/37-encoder-decoder.md",
    "book-engineering/chapters/37-audit-report-fa.md",
    "book-engineering/answers/37-encoder-decoder-fa.md",
    "book-engineering/projects/37-encoder-decoder/README.md",
    "book-engineering/projects/37-encoder-decoder/transformer_architectures.py",
    "book-engineering/projects/37-encoder-decoder/test_transformer_architectures.py",
    "assets/images/babak-ai/v3-ch06-efficiency-map.webp",
    "book-engineering/chapters/38-long-context.md",
    "book-engineering/chapters/38-audit-report-fa.md",
    "book-engineering/answers/38-long-context-fa.md",
    "book-engineering/projects/38-long-context/README.md",
    "book-engineering/projects/38-long-context/efficient_attention.py",
    "book-engineering/projects/38-long-context/test_efficient_attention.py",
    "assets/images/babak-ai/v3-ch07-multimodal-bridge.webp",
    "book-engineering/chapters/39-multimodal-transformer.md",
    "book-engineering/chapters/39-audit-report-fa.md",
    "book-engineering/answers/39-multimodal-transformer-fa.md",
    "book-engineering/projects/39-multimodal-transformer/README.md",
    "book-engineering/projects/39-multimodal-transformer/multimodal_alignment.py",
    "book-engineering/projects/39-multimodal-transformer/test_multimodal_alignment.py",
    "assets/images/babak-ai/v3-ch08-data-pipeline.webp",
    "book-engineering/chapters/40-small-data-project.md",
    "book-engineering/chapters/40-audit-report-fa.md",
    "book-engineering/answers/40-small-data-project-fa.md",
    "book-engineering/projects/40-small-data-project/README.md",
    "book-engineering/projects/40-small-data-project/small_corpus.py",
    "book-engineering/projects/40-small-data-project/test_small_corpus.py",
    "book-engineering/projects/40-small-data-project/sample_corpus.jsonl",
    "assets/images/babak-ai/v3-ch09-training-loop.webp",
    "book-engineering/chapters/41-first-language-model.md",
    "book-engineering/chapters/41-audit-report-fa.md",
    "book-engineering/answers/41-first-language-model-fa.md",
    "book-engineering/projects/41-first-language-model/README.md",
    "book-engineering/projects/41-first-language-model/tiny_lm.py",
    "book-engineering/projects/41-first-language-model/test_tiny_lm.py",
    "book-engineering/create_v3_ch09_image.py",
    "book-engineering/diagrams/v3-ch09-training-loop.svg",
    "assets/images/babak-ai/v3-ch10-mini-gpt-budget.webp",
    "book-engineering/chapters/42-mini-gpt.md",
    "book-engineering/chapters/42-audit-report-fa.md",
    "book-engineering/answers/42-mini-gpt-fa.md",
    "book-engineering/projects/42-mini-gpt-design/README.md",
    "book-engineering/projects/42-mini-gpt-design/mini_gpt_design.py",
    "book-engineering/projects/42-mini-gpt-design/test_mini_gpt_design.py",
    "book-engineering/create_v3_ch10_image.py",
    "book-engineering/diagrams/v3-ch10-mini-gpt-budget.svg",
    "assets/images/babak-ai/v3-ch11-corpus-audit.webp",
    "book-engineering/chapters/43-corpus.md",
    "book-engineering/chapters/43-audit-report-fa.md",
    "book-engineering/answers/43-corpus-fa.md",
    "book-engineering/projects/43-corpus-audit/README.md",
    "book-engineering/projects/43-corpus-audit/corpus_audit.py",
    "book-engineering/projects/43-corpus-audit/test_corpus_audit.py",
    "book-engineering/projects/43-corpus-audit/sample_corpus.jsonl",
    "book-engineering/projects/43-corpus-audit/sample_evaluation.jsonl",
    "book-engineering/create_v3_ch11_image.py",
    "book-engineering/diagrams/v3-ch11-corpus-audit.svg",
    "assets/images/babak-ai/v3-ch12-pretraining.webp",
    "book-engineering/chapters/44-pretraining.md",
    "book-engineering/chapters/44-audit-report-fa.md",
    "book-engineering/answers/44-pretraining-fa.md",
    "book-engineering/projects/44-pretraining/README.md",
    "book-engineering/projects/44-pretraining/pretraining_run.py",
    "book-engineering/projects/44-pretraining/test_pretraining_run.py",
    "book-engineering/create_v3_ch12_image.py",
    "book-engineering/diagrams/v3-ch12-pretraining.svg",
    "assets/images/babak-ai/v3-ch13-precision.webp",
    "book-engineering/chapters/45-precision.md",
    "book-engineering/chapters/45-audit-report-fa.md",
    "book-engineering/answers/45-precision-fa.md",
    "book-engineering/projects/45-precision/README.md",
    "book-engineering/projects/45-precision/precision_lab.py",
    "book-engineering/projects/45-precision/test_precision_lab.py",
    "book-engineering/create_v3_ch13_image.py",
    "book-engineering/diagrams/v3-ch13-precision.svg",
    "assets/images/babak-ai/v3-ch14-scale-training.webp",
    "book-engineering/chapters/46-scale-training.md",
    "book-engineering/chapters/46-audit-report-fa.md",
    "book-engineering/answers/46-scale-training-fa.md",
    "book-engineering/projects/46-scale-training/README.md",
    "book-engineering/projects/46-scale-training/scaling_lab.py",
    "book-engineering/projects/46-scale-training/test_scaling_lab.py",
    "book-engineering/create_v3_ch14_image.py",
    "book-engineering/diagrams/v3-ch14-scale-training.svg",
]


def wait_for_current_figure(page):
    page.wait_for_function("""() => {
        const img=document.querySelector('.reader-content img');
        return img && img.complete && img.naturalWidth === 1600 && img.naturalHeight === 1000;
    }""")


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT.parent)))
    Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/{ROOT.name}/"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=["--no-sandbox"])
            for width in (320, 390, 1440):
                context = browser.new_context(viewport={"width": width, "height": 900})
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(url, wait_until="networkidle")
                page.wait_for_selector("#loading.hidden")
                assert page.get_by_text(TITLE, exact=True).count() == 1
                assert page.get_by_text("نسخه PDF و EPUB تولید نشده است.", exact=False).count() == 1
                card = page.locator(".book-card").filter(has_text=TITLE)
                assert card.count() == 1 and "14 فصل" in card.inner_text() and "265 بخش" in card.inner_text()
                assert page.locator(".book-card").count() >= 3

                page.evaluate(f"openItem('{BOOK_ID}','book')")
                headers = page.locator(".chapter-header")
                assert headers.count() == 14
                for index, count in enumerate((11, 13, 13, 16, 16, 20, 20, 20, 20, 20, 21, 21, 27, 27)):
                    assert f"فصل {index + 1}" in headers.nth(index).inner_text()
                    assert f"{count} بخش" in headers.nth(index).inner_text()

                # Chapter 33: first image and accessible MathML.
                headers.nth(0).click()
                assert page.locator("#item-ch-0 .section-item").count() == 11
                page.locator("#item-ch-0 .section-item").first.click()
                page.wait_for_selector(".reader-content")
                assert page.locator(".reader-content math").count() == 1
                assert page.locator(".reader-content math").first.get_attribute("aria-label")
                image = page.locator(".reader-content img").first
                assert "شکل ۳-۱-۱" in image.get_attribute("alt") and "BPE" in image.get_attribute("alt")
                wait_for_current_figure(page)

                # Chapter 34: matrix figure and Q/K/V equation.
                page.evaluate(f"openSec('{BOOK_ID}',1,2)")
                assert page.locator(".reader-content math").count() == 1
                math_label = page.locator(".reader-content math").first.get_attribute("aria-label")
                assert math_label and "کیو" in math_label and "وی" in math_label
                image = page.locator(".reader-content img").first
                assert all(term in image.get_attribute("alt") for term in ("شکل ۳-۲-۱", "Q/K/V", "Lq×Lk", "Lq×dv"))
                wait_for_current_figure(page)

                # Chapter 35: causal diagram and equation.
                page.evaluate(f"openSec('{BOOK_ID}',2,0)")
                image = page.locator(".reader-content img").first
                assert all(term in image.get_attribute("alt") for term in ("شکل ۳-۳-۱", "Self-Attention", "Q/K/V", "j≤i", "j>i"))
                wait_for_current_figure(page)
                page.evaluate(f"openSec('{BOOK_ID}',2,1)")
                assert page.locator(".reader-content math").count() == 1
                assert page.locator(".reader-content math").first.get_attribute("aria-label")

                # Chapter 36: image, sinusoidal PE, RoPE, LayerNorm and FFN equations.
                page.evaluate(f"openSec('{BOOK_ID}',3,0)")
                image = page.locator(".reader-content img").first
                assert all(term in image.get_attribute("alt") for term in ("شکل ۳-۴-۱", "PE", "RoPE", "LayerNorm", "FFN"))
                wait_for_current_figure(page)
                for section, expected_count in ((2, 1), (4, 1), (7, 1), (8, 1), (9, 1)):
                    page.evaluate(f"openSec('{BOOK_ID}',3,{section})")
                    assert page.locator(".reader-content math").count() == expected_count
                    assert page.locator(".reader-content math").first.get_attribute("aria-label")

                # Chapter 37: architecture comparison diagram and equations.
                page.evaluate(f"openSec('{BOOK_ID}',4,0)")
                image = page.locator(".reader-content img").first
                assert all(term in image.get_attribute("alt") for term in ("شکل ۳-۵-۱", "Encoder-only", "Decoder-only", "Encoder–Decoder", "cross-attention"))
                wait_for_current_figure(page)
                for section in (1, 3, 4):
                    page.evaluate(f"openSec('{BOOK_ID}',4,{section})")
                    assert page.locator(".reader-content math").count() == 1
                    assert page.locator(".reader-content math").first.get_attribute("aria-label")

                # Chapter 38: long-context efficiency map and core equations.
                page.evaluate(f"openSec('{BOOK_ID}',5,0)")
                image = page.locator(".reader-content img").first
                assert all(term in image.get_attribute("alt") for term in (
                    "شکل ۳-۶-۱", "KV Cache", "GQA", "Sparse Attention",
                    "FlashAttention", "MoE", "RULER", "NoLiMa", "OOLONG"
                ))
                wait_for_current_figure(page)
                for section in (2, 3, 5, 7, 9, 10):
                    page.evaluate(f"openSec('{BOOK_ID}',5,{section})")
                    assert page.locator(".reader-content math").count() == 1
                    assert page.locator(".reader-content math").first.get_attribute("aria-label")

                # Chapter 39: distinct image/text/audio encoders, shared alignment and cross-attention.
                page.evaluate(f"openSec('{BOOK_ID}',6,0)")
                image = page.locator(".reader-content img").first
                assert all(term in image.get_attribute("alt") for term in (
                    "شکل ۳-۷-۱", "ViT", "log-Mel", "InfoNCE", "embedding", "cross-attention"
                ))
                wait_for_current_figure(page)
                for section, expected_count in ((2, 1), (4, 1), (5, 2)):
                    page.evaluate(f"openSec('{BOOK_ID}',6,{section})")
                    assert page.locator(".reader-content math").count() == expected_count
                    assert all(label for label in page.locator(".reader-content math").evaluate_all("els => els.map(e => e.getAttribute('aria-label'))"))

                # Chapter 40: permission/provenance gate, group-aware splits and train-only vocabulary.
                page.evaluate(f"openSec('{BOOK_ID}',7,0)")
                image = page.locator(".reader-content img").first
                assert all(term in image.get_attribute("alt") for term in (
                    "شکل ۳-۸-۱", "مجوز", "manifest", "group_id", "train", "validation", "test", "tokenizer"
                ))
                wait_for_current_figure(page)
                for section in (9, 10, 11):
                    page.evaluate(f"openSec('{BOOK_ID}',7,{section})")
                    assert page.locator(".reader-content math").count() == 1
                    assert page.locator(".reader-content math").first.get_attribute("aria-label")

                # Chapter 41: embedding, fixed-context training, evaluation and generation.
                page.evaluate(f"openSec('{BOOK_ID}',8,0)")
                assert page.locator(".reader-content a[href='book-engineering/chapters/40-small-data-project.md']").count() == 1
                image = page.locator(".reader-content img").first
                assert all(term in image.get_attribute("alt") for term in (
                    "شکل ۳-۹-۱", "train", "validation", "test", "Embedding", "MLP", "logits", "cross-entropy", "گرادیان"
                ))
                wait_for_current_figure(page)
                for section in (1, 4, 6, 7, 8, 9, 12):
                    page.evaluate(f"openSec('{BOOK_ID}',8,{section})")
                    assert page.locator(".reader-content math").count() == 1
                    assert page.locator(".reader-content math").first.get_attribute("aria-label")
                page.evaluate(f"openSec('{BOOK_ID}',8,17)")
                assert page.locator(".reader-content a[href='book-engineering/answers/41-first-language-model-fa.md']").count() == 1

                # Chapter 42: reuse the tested decoder while checking budget and shape claims.
                page.evaluate(f"openSec('{BOOK_ID}',9,0)")
                image = page.locator(".reader-content img").first
                assert all(term in image.get_attribute("alt") for term in (
                    "شکل ۳-۱۰-۱", "Decoder-only", "۱۱۷٬۳۵۰", "۴٫۴۰ MiB", "score-equivalent"
                ))
                wait_for_current_figure(page)
                for section in (3, 4, 6, 7, 10):
                    page.evaluate(f"openSec('{BOOK_ID}',9,{section})")
                    assert page.locator(".reader-content math").count() == 1
                    assert page.locator(".reader-content math").first.get_attribute("aria-label")
                page.evaluate(f"openSec('{BOOK_ID}',9,17)")
                assert page.locator(".reader-content a[href='book-engineering/answers/42-mini-gpt-fa.md']").count() == 1
                page.evaluate(f"openSec('{BOOK_ID}',9,19)")
                code = page.locator(".reader-content pre code").last.inner_text()
                assert "def parameter_breakdown" in code and "def context_sweep" in code

                # Chapter 43: provenance-aware audit, duplicate candidates and evaluation overlap.
                page.evaluate(f"openSec('{BOOK_ID}',10,0)")
                image = page.locator(".reader-content img").first
                assert all(term in image.get_attribute("alt") for term in (
                    "شکل ۳-۱۱-۱", "منشأ", "مجوز", "کیفیت", "تکرار", "هم‌پوشانی ارزیابی"
                ))
                wait_for_current_figure(page)
                for section in (5, 7, 9, 12):
                    page.evaluate(f"openSec('{BOOK_ID}',10,{section})")
                    assert page.locator(".reader-content math").count() == 1
                    assert page.locator(".reader-content math").first.get_attribute("aria-label")
                page.evaluate(f"openSec('{BOOK_ID}',10,19)")
                assert page.locator(".reader-content a[href='book-engineering/answers/43-corpus-fa.md']").count() == 1
                page.evaluate(f"openSec('{BOOK_ID}',10,20)")
                code = page.locator(".reader-content pre code").last.inner_text()
                assert "def audit_records" in code and "def evaluation_overlap_candidates" in code

                # Chapter 44: update-based schedule, checkpoint/resume and generated loss-curve output.
                page.evaluate(f"openSec('{BOOK_ID}',11,0)")
                image = page.locator(".reader-content img").first
                assert all(term in image.get_attribute("alt") for term in (
                    "شکل ۳-۱۲-۱", "microbatch", "optimizer update", "warmup", "cosine", "checkpoint", "test"
                ))
                wait_for_current_figure(page)
                for section in (1, 3, 4, 7):
                    page.evaluate(f"openSec('{BOOK_ID}',11,{section})")
                    assert page.locator(".reader-content math").count() == 1
                    assert page.locator(".reader-content math").first.get_attribute("aria-label")
                page.evaluate(f"openSec('{BOOK_ID}',11,19)")
                assert page.locator(".reader-content a[href='book-engineering/answers/44-pretraining-fa.md']").count() == 1
                page.evaluate(f"openSec('{BOOK_ID}',11,20)")
                code = page.locator(".reader-content pre code").last.inner_text()
                assert "def train_pretraining" in code and "def _loss_curve_svg" in code

                # Chapter 45: dtype tradeoffs, accessible equations, quantization and tested appendix.
                page.evaluate(f"openSec('{BOOK_ID}',12,0)")
                image = page.locator(".reader-content img").first
                assert all(term in image.get_attribute("alt") for term in (
                    "شکل ۳-۱۳-۱", "FP32", "FP16", "BF16", "E4M3/E5M2",
                    "AMP per-op", "Quantization", "scale/zero-point", "validation", "سخت‌افزار"
                ))
                wait_for_current_figure(page)
                for section in (1, 2, 7, 11, 13, 14):
                    page.evaluate(f"openSec('{BOOK_ID}',12,{section})")
                    assert page.locator(".reader-content math").count() == 1
                    assert page.locator(".reader-content math").first.get_attribute("aria-label")
                page.evaluate(f"openSec('{BOOK_ID}',12,24)")
                assert page.locator(".reader-content a[href='book-engineering/answers/45-precision-fa.md']").count() == 1
                page.evaluate(f"openSec('{BOOK_ID}',12,26)")
                code = page.locator(".reader-content pre code").last.inner_text()
                assert "def calculate_qparams" in code and "def cpu_autocast_probe" in code

                # Chapter 46: activation recomputation, uneven-shard DDP and byte-matched code.
                page.evaluate(f"openSec('{BOOK_ID}',13,0)")
                image = page.locator(".reader-content img").first
                assert all(term in image.get_attribute("alt") for term in (
                    "شکل ۳-۱۴-۱", "AllReduce", "activation recomputation", "sharding", "snapshot", "run record"
                ))
                wait_for_current_figure(page)
                for section in (6, 7, 19):
                    page.evaluate(f"openSec('{BOOK_ID}',13,{section})")
                    assert page.locator(".reader-content math").count() == 1
                    assert page.locator(".reader-content math").first.get_attribute("aria-label")
                page.evaluate(f"openSec('{BOOK_ID}',13,24)")
                assert page.locator(".reader-content a[href='book-engineering/answers/46-scale-training-fa.md']").count() == 1
                page.evaluate(f"openSec('{BOOK_ID}',13,26)")
                code = page.locator(".reader-content pre code").last.inner_text()
                assert "def activation_checkpoint_probe" in code and "def distributed_gradient_probe" in code

                # Visit every section for overflow and accessible MathML.
                result = page.evaluate(f'''() => {{
                    const book=DATA.books.find(b=>b.id==="{BOOK_ID}"), math=[], bad=[];
                    book.chapters.forEach((chapter,ci)=>chapter.sections.forEach((section,si)=>{{
                      openSec(book.id,ci,si);
                      const content=document.querySelector('.reader-content');
                      content.querySelectorAll('math').forEach(m=>math.push({{section:section.id,label:m.getAttribute('aria-label'),visible:!!(m.offsetWidth||m.offsetHeight||m.getClientRects().length)}}));
                      if(document.documentElement.scrollWidth>innerWidth || content.scrollWidth>content.clientWidth+2) bad.push(section.id);
                    }}));
                    return {{count:book.chapters.reduce((n,c)=>n+c.sections.length,0),math,bad}};
                }}''')
                assert result["count"] == 265 and not result["bad"], (width, result)
                assert len(result["math"]) >= 36 and all(item["label"] and item["visible"] for item in result["math"]), result["math"]

                # Cross-chapter navigation in both directions.
                page.evaluate(f"openItem('{BOOK_ID}','book');openSec('{BOOK_ID}',0,10);nextSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [1, 0]
                page.evaluate("prevSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [0, 10]
                page.evaluate(f"openSec('{BOOK_ID}',1,12);nextSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [2, 0]
                page.evaluate("prevSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [1, 12]
                page.evaluate(f"openSec('{BOOK_ID}',2,12);nextSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [3, 0]
                page.evaluate("prevSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [2, 12]

                # Cross-chapter navigation into chapters 37 and 38 and back.
                page.evaluate(f"openSec('{BOOK_ID}',3,15);nextSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [4, 0]
                page.evaluate("prevSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [3, 15]
                page.evaluate(f"openSec('{BOOK_ID}',4,15);nextSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [5, 0]
                page.evaluate("prevSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [4, 15]
                page.evaluate(f"openSec('{BOOK_ID}',5,19);nextSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [6, 0]
                page.evaluate("prevSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [5, 19]
                page.evaluate(f"openSec('{BOOK_ID}',6,19);nextSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [7, 0]
                page.evaluate("prevSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [6, 19]
                page.evaluate(f"openSec('{BOOK_ID}',7,19);nextSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [8, 0]
                page.evaluate("prevSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [7, 19]
                page.evaluate(f"openSec('{BOOK_ID}',8,19);nextSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [9, 0]
                page.evaluate("prevSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [8, 19]
                page.evaluate(f"openSec('{BOOK_ID}',9,19);nextSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [10, 0]
                page.evaluate("prevSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [9, 19]
                page.evaluate(f"openSec('{BOOK_ID}',10,20);nextSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [11, 0]
                page.evaluate("prevSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [10, 20]
                page.evaluate(f"openSec('{BOOK_ID}',11,20);nextSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [12, 0]
                page.evaluate("prevSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [11, 20]

                # Stable chapter-42 section IDs survive reload; its design terms are searchable.
                page.evaluate(f"openItem('{BOOK_ID}','book');openSec('{BOOK_ID}',9,10)")
                page.reload(wait_until="networkidle")
                page.wait_for_selector(".reader-content")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [9, 10]
                page.evaluate("navTo('search');doSearch('score-equivalent')")
                assert page.evaluate(f"window_searchResults.some(r=>JSON.stringify(r).includes('{BOOK_ID}'))")
                page.evaluate(f"openItem('{BOOK_ID}','book');openSec('{BOOK_ID}',10,12)")
                page.reload(wait_until="networkidle")
                page.wait_for_selector(".reader-content")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [10, 12]
                page.evaluate("navTo('search');doSearch('Jaccard')")
                assert page.evaluate(f"window_searchResults.some(r=>JSON.stringify(r).includes('{BOOK_ID}'))")
                page.evaluate(f"openItem('{BOOK_ID}','book');openSec('{BOOK_ID}',11,19)")
                page.reload(wait_until="networkidle")
                page.wait_for_selector(".reader-content")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [11, 19]
                page.evaluate("navTo('search');doSearch('loss_curve.svg')")
                assert page.evaluate(f"window_searchResults.some(r=>JSON.stringify(r).includes('{BOOK_ID}'))")
                page.evaluate(f"openItem('{BOOK_ID}','book');openSec('{BOOK_ID}',12,10)")
                page.reload(wait_until="networkidle")
                page.wait_for_selector(".reader-content")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [12, 10]
                page.evaluate("navTo('search');doSearch('E4M3')")
                assert page.evaluate(f"window_searchResults.some(r=>JSON.stringify(r).includes('{BOOK_ID}'))")

                # Every chapter asset is cached and retrievable after going offline.
                page.evaluate("navigator.serviceWorker.ready")
                page.wait_for_function("""args => caches.open(args.cacheName).then(async cache => {
                    for (const path of args.paths) {
                      const response = await cache.match(new URL(path, location.href).href);
                      if (!response) return false;
                    }
                    return true;
                })""", arg={"cacheName": CACHE_NAME, "paths": OFFLINE_PATHS}, timeout=30000)
                context.set_offline(True)
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_selector("#loading.hidden")
                assert page.get_by_text(TITLE, exact=True).count() == 1
                page.evaluate(f"openItem('{BOOK_ID}','book');openSec('{BOOK_ID}',5,0)")
                assert page.locator(".reader-content img").first.evaluate("e => e.complete && e.naturalWidth === 1600")
                page.evaluate(f"openSec('{BOOK_ID}',6,0)")
                assert page.locator(".reader-content img").first.evaluate("e => e.complete && e.naturalWidth === 1600")
                page.evaluate(f"openSec('{BOOK_ID}',7,0)")
                assert page.locator(".reader-content img").first.evaluate("e => e.complete && e.naturalWidth === 1600")
                page.evaluate(f"openSec('{BOOK_ID}',8,0)")
                assert page.locator(".reader-content img").first.evaluate("e => e.complete && e.naturalWidth === 1600 && e.naturalHeight === 1000")
                page.evaluate(f"openSec('{BOOK_ID}',9,0)")
                assert page.locator(".reader-content img").first.evaluate("e => e.complete && e.naturalWidth === 1600 && e.naturalHeight === 1000")
                page.evaluate(f"openSec('{BOOK_ID}',10,0)")
                assert page.locator(".reader-content img").first.evaluate("e => e.complete && e.naturalWidth === 1600 && e.naturalHeight === 1000")
                page.evaluate(f"openSec('{BOOK_ID}',11,0)")
                assert page.locator(".reader-content img").first.evaluate("e => e.complete && e.naturalWidth === 1600 && e.naturalHeight === 1000")
                page.evaluate(f"openSec('{BOOK_ID}',12,0)")
                assert page.locator(".reader-content img").first.evaluate("e => e.complete && e.naturalWidth === 1600 && e.naturalHeight === 1000")
                page.evaluate(f"openSec('{BOOK_ID}',13,0)")
                assert page.locator(".reader-content img").first.evaluate("e => e.complete && e.naturalWidth === 1600 && e.naturalHeight === 1000")
                offline = page.evaluate('''async paths => {
                    const bad=[];
                    for (const path of paths) {
                      try { const response=await fetch(path); if(!response.ok || !(await response.arrayBuffer()).byteLength) bad.push(path); }
                      catch(error) { bad.push(path); }
                    }
                    const answer33=await (await fetch(paths[4])).text();
                    const answer34=await (await fetch(paths[12])).text();
                    const answer35=await (await fetch(paths[19])).text();
                    const answer36=await (await fetch(paths[26])).text();
                    const answer37=await (await fetch(paths[33])).text();
                    const chapter38=await (await fetch(paths[38])).text();
                    const answer38=await (await fetch(paths[40])).text();
                    const chapter39=await (await fetch(paths[45])).text();
                    const answer39=await (await fetch(paths[47])).text();
                    const chapter40=await (await fetch(paths[52])).text();
                    const answer40=await (await fetch(paths[54])).text();
                    const chapter41=await (await fetch(paths[60])).text();
                    const answer41=await (await fetch(paths[62])).text();
                    const project41=await (await fetch(paths[64])).text();
                    const chapter42=await (await fetch(paths[69])).text();
                    const answer42=await (await fetch(paths[71])).text();
                    const project42=await (await fetch(paths[73])).text();
                    const chapter43=await (await fetch(paths[78])).text();
                    const answer43=await (await fetch(paths[80])).text();
                    const project43=await (await fetch(paths[81])).text();
                    const chapter44=await (await fetch(paths[89])).text();
                    const answer44=await (await fetch(paths[91])).text();
                    const project44=await (await fetch(paths[93])).text();
                    const chapter45=await (await fetch(paths[98])).text();
                    const answer45=await (await fetch(paths[100])).text();
                    const project45=await (await fetch(paths[102])).text();
                    const chapter46=await (await fetch(paths[107])).text();
                    const answer46=await (await fetch(paths[109])).text();
                    const project46=await (await fetch(paths[111])).text();
                    const markdown=await (await fetch(paths[0])).text();
                    return {bad,answer33:answer33.includes('پاسخ‌نامه تشریحی جلد سوم'),answer34:answer34.includes('جواب‌نامهٔ تشریحی'),answer35:answer35.includes('جواب‌نامهٔ تشریحی'),answer36:answer36.includes('پاسخ‌نامهٔ تشریحی'),answer37:answer37.includes('پاسخ‌نامهٔ تشریحی'),chapter38:chapter38.includes('KV Cache'),answer38:answer38.includes('پاسخ‌نامهٔ تشریحی'),chapter39:chapter39.includes('Transformer چندوجهی'),answer39:answer39.includes('پاسخ‌نامهٔ تشریحی'),chapter40:chapter40.includes('پروژهٔ دادهٔ کوچک'),answer40:answer40.includes('پاسخ‌نامهٔ تشریحی'),chapter41:chapter41.includes('نخستین مدل زبانی کوچک'),answer41:answer41.includes('پاسخ‌نامهٔ تشریحی'),project41:project41.includes('weights_only=True'),chapter42:chapter42.includes('طراحی Mini GPT'),answer42:answer42.includes('پاسخ‌نامهٔ تشریحی'),project42:project42.includes('def parameter_breakdown'),chapter43:chapter43.includes('آلودگی ارزیابی'),answer43:answer43.includes('پاسخ‌نامهٔ تشریحی'),project43:project43.includes('دفتر ممیزی'),chapter44:chapter44.includes('پیش‌آموزش'),answer44:answer44.includes('پاسخ‌نامهٔ تشریحی'),project44:project44.includes('def _loss_curve_svg'),chapter45:chapter45.includes('Quantization'),answer45:answer45.includes('پاسخ‌نامهٔ تشریحی'),project45:project45.includes('def calculate_qparams'),chapter46:chapter46.includes('Gradient Checkpointing'),answer46:answer46.includes('پاسخ‌نامهٔ فصل ۴۶'),project46:project46.includes('def distributed_gradient_probe'),markdown:markdown.includes('بازبینی منابع')};
                }''', OFFLINE_PATHS)
                assert offline == {"bad": [], "answer33": True, "answer34": True, "answer35": True, "answer36": True, "answer37": True, "chapter38": True, "answer38": True, "chapter39": True, "answer39": True, "chapter40": True, "answer40": True, "chapter41": True, "answer41": True, "project41": True, "chapter42": True, "answer42": True, "project42": True, "chapter43": True, "answer43": True, "project43": True, "chapter44": True, "answer44": True, "project44": True, "chapter45": True, "answer45": True, "project45": True, "chapter46": True, "answer46": True, "project46": True, "markdown": True}, offline
                assert not errors, errors
                print(f"PASS volume 3 chapters 1–14 at {width}px: 265 sections, {len(result['math'])} MathML blocks, fourteen WebP figures, navigation, search and {len(OFFLINE_PATHS)} offline files")
                context.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
