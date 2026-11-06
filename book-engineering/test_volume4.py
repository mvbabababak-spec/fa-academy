"""Browser, accessibility, exact-appendix and offline checks for volume 4."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BOOK_ID = "art-science-intelligence-v4"
TITLE = "هنر و علم ساخت هوش — جلد چهارم"
CACHE_NAME = "fa-academy-v86"
OFFLINE_PATHS = [
    "assets/images/covers/volume-1-cover.webp",
    "assets/images/covers/volume-2-cover.webp",
    "assets/images/covers/volume-3-cover.webp",
    "assets/images/covers/volume-4-cover.webp",
    "assets/images/covers/microsoft-ai-for-beginners-cover.webp",
    "assets/images/covers/microsoft-generative-ai-for-beginners-cover.webp",
    "assets/images/covers/microsoft-ml-for-beginners-cover.webp",
    "assets/images/covers/microsoft-data-science-for-beginners-cover.webp",
    "volume-4-full-fa.md",
    "book-engineering/diagrams/v4-ch01-posttraining.svg",
    "book-engineering/chapters/47-posttraining.md",
    "book-engineering/chapters/47-audit-report-fa.md",
    "book-engineering/answers/47-posttraining-fa.md",
    "book-engineering/projects/47-instruction-tuning/README.md",
    "book-engineering/projects/47-instruction-tuning/sft_experiment.py",
    "book-engineering/projects/47-instruction-tuning/test_sft_experiment.py",
    "book-engineering/projects/47-instruction-tuning/sample_sft.jsonl",
    "book-engineering/projects/47-instruction-tuning/requirements-model-demo.txt",
    "book-engineering/diagrams/v4-ch02-peft.svg",
    "book-engineering/chapters/48-peft.md",
    "book-engineering/chapters/48-audit-report-fa.md",
    "book-engineering/answers/48-peft-fa.md",
    "book-engineering/projects/48-peft-lab/README.md",
    "book-engineering/projects/48-peft-lab/peft_lab.py",
    "book-engineering/projects/48-peft-lab/test_peft_lab.py",
    "book-engineering/projects/48-peft-lab/sample_layers.json",
    "book-engineering/diagrams/v4-ch03-preference.svg",
    "book-engineering/chapters/49-preference-optimization.md",
    "book-engineering/chapters/49-audit-report-fa.md",
    "book-engineering/answers/49-preference-optimization-fa.md",
    "book-engineering/projects/49-preference-lab/README.md",
    "book-engineering/projects/49-preference-lab/preference_lab.py",
    "book-engineering/projects/49-preference-lab/test_preference_lab.py",
    "book-engineering/projects/49-preference-lab/sample_preferences.jsonl",
    "book-engineering/projects/49-preference-lab/results.json",
    "book-engineering/diagrams/v4-ch04-synthetic-reasoning.svg",
    "book-engineering/chapters/50-synthetic-reasoning.md",
    "book-engineering/chapters/50-audit-report-fa.md",
    "book-engineering/answers/50-synthetic-reasoning-fa.md",
    "book-engineering/projects/50-synthetic-reasoning/README.md",
    "book-engineering/projects/50-synthetic-reasoning/reasoning_lab.py",
    "book-engineering/projects/50-synthetic-reasoning/test_reasoning_lab.py",
    "book-engineering/projects/50-synthetic-reasoning/sample_traces.jsonl",
    "book-engineering/projects/50-synthetic-reasoning/results.json",
    "book-engineering/diagrams/v4-ch05-vision.svg",
    "book-engineering/chapters/51-vision-models.md",
    "book-engineering/chapters/51-audit-report-fa.md",
    "book-engineering/answers/51-vision-models-fa.md",
    "book-engineering/projects/51-vision-lab/README.md",
    "book-engineering/projects/51-vision-lab/vision_lab.py",
    "book-engineering/projects/51-vision-lab/test_vision_lab.py",
    "book-engineering/projects/51-vision-lab/sample_embeddings.json",
    "book-engineering/projects/51-vision-lab/results.json",
    "book-engineering/diagrams/v4-ch06-audio.svg",
    "book-engineering/chapters/52-audio-models.md",
    "book-engineering/chapters/52-audit-report-fa.md",
    "book-engineering/answers/52-audio-models-fa.md",
    "book-engineering/projects/52-audio-lab/README.md",
    "book-engineering/projects/52-audio-lab/audio_lab.py",
    "book-engineering/projects/52-audio-lab/test_audio_lab.py",
    "book-engineering/projects/52-audio-lab/sample_transcripts.json",
    "book-engineering/projects/52-audio-lab/results.json",
    "book-engineering/diagrams/v4-ch07-diffusion.svg",
    "book-engineering/chapters/53-image-video-generation.md",
    "book-engineering/chapters/53-audit-report-fa.md",
    "book-engineering/answers/53-image-video-generation-fa.md",
    "book-engineering/projects/53-diffusion-lab/README.md",
    "book-engineering/projects/53-diffusion-lab/diffusion_lab.py",
    "book-engineering/projects/53-diffusion-lab/test_diffusion_lab.py",
    "book-engineering/projects/53-diffusion-lab/sample_mixture.json",
    "book-engineering/projects/53-diffusion-lab/results.json",
]


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT.parent)))
    Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/{ROOT.name}/"
    project47 = (ROOT / "book-engineering/projects/47-instruction-tuning/sft_experiment.py").read_text(encoding="utf-8").rstrip()
    project48 = (ROOT / "book-engineering/projects/48-peft-lab/peft_lab.py").read_text(encoding="utf-8").rstrip()
    project49 = (ROOT / "book-engineering/projects/49-preference-lab/preference_lab.py").read_text(encoding="utf-8").rstrip()
    project50 = (ROOT / "book-engineering/projects/50-synthetic-reasoning/reasoning_lab.py").read_text(encoding="utf-8").rstrip()
    project51 = (ROOT / "book-engineering/projects/51-vision-lab/vision_lab.py").read_text(encoding="utf-8").rstrip()
    project52 = (ROOT / "book-engineering/projects/52-audio-lab/audio_lab.py").read_text(encoding="utf-8").rstrip()
    project53 = (ROOT / "book-engineering/projects/53-diffusion-lab/diffusion_lab.py").read_text(encoding="utf-8").rstrip()
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
                metadata = page.evaluate(f'''() => {{
                  const book=DATA.books.find(item=>item.id==="{BOOK_ID}");
                  return {{chapters:book.chapters.map(ch=>({{
                    id:ch.id,
                    sectionIds:ch.sections.map(section=>section.id),
                    titles:ch.sections.map(section=>section.title),
                    mathIndexes:ch.sections.map((section,index)=>section.html.includes('<math')?index:-1).filter(index=>index>=0),
                    mathCount:ch.sections.reduce((count,section)=>count+(section.html.match(/<math/g)||[]).length,0),
                    answerIndexes:ch.sections.map((section,index)=>section.html.includes('answers/')?index:-1).filter(index=>index>=0),
                    sectionCount:ch.sections.length
                  }}))}};
                }}''')
                assert len(metadata["chapters"]) == 7, metadata
                c47, c48, c49, c50, c51, c52, c53 = metadata["chapters"]
                assert [c["id"] for c in metadata["chapters"]] == [
                    "art-science-v4-ch01", "art-science-v4-ch02", "art-science-v4-ch03", "art-science-v4-ch04", "art-science-v4-ch05", "art-science-v4-ch06", "art-science-v4-ch07"
                ], metadata
                for chapter in metadata["chapters"]:
                    assert chapter["sectionCount"] >= 15
                    assert chapter["sectionIds"][0].endswith("-s01")
                    assert len(set(chapter["sectionIds"])) == chapter["sectionCount"]

                # Chapter 47: SFT figure, accessible MathML, answer and exact appendix.
                page.evaluate(f"openItem('{BOOK_ID}','book')")
                headers = page.locator(".chapter-header")
                assert headers.count() == 7
                headers.nth(0).click()
                page.evaluate(f"openSec('{BOOK_ID}',0,0)")
                page.wait_for_selector(".reader-content")
                image47 = page.locator(".reader-content img").first
                alt47 = image47.get_attribute("alt")
                assert all(term in alt47 for term in ("شکل ۴-۱-۱", "Continued Pretraining", "SFT", "−۱۰۰", "benchmark")), alt47
                page.wait_for_function("""() => {
                    const img=document.querySelector('.reader-content img');
                    return img && img.complete && img.naturalWidth===1600 && img.naturalHeight===1000;
                }""")
                assert c47["mathIndexes"], "chapter 47 MathML missing"
                math47_index = c47["mathIndexes"][0]
                page.evaluate(f"openSec('{BOOK_ID}',0,{math47_index})")
                math47 = page.locator(".reader-content math").first
                assert page.locator(".reader-content math").count() == 1
                assert math47.get_attribute("aria-label") and "زیان SFT" in math47.get_attribute("aria-label")
                assert page.locator(".reader-content").evaluate("e => e.scrollWidth <= e.clientWidth + 2")
                assert c47["answerIndexes"], "chapter 47 answer link missing"
                page.evaluate(f"openSec('{BOOK_ID}',0,{c47['answerIndexes'][0]})")
                assert page.locator(".reader-content a[href='book-engineering/answers/47-posttraining-fa.md']").count() == 1
                appendix47 = next(i for i, title in enumerate(c47["titles"]) if "پیوست اجرایی" in title)
                page.evaluate(f"openSec('{BOOK_ID}',0,{appendix47})")
                assert page.locator(".reader-content pre code").last.text_content().rstrip("\n") == project47

                # Chapter 48: PEFT figure, MathML, independent answer and exact appendix.
                page.evaluate(f"openItem('{BOOK_ID}','book')")
                headers = page.locator(".chapter-header")
                assert headers.count() == 7
                headers.nth(1).click()
                page.evaluate(f"openSec('{BOOK_ID}',1,0)")
                image48 = page.locator(".reader-content img").first
                alt48 = image48.get_attribute("alt")
                assert all(term in alt48 for term in ("شکل ۴-۲-۱", "adapter", "LoRA", "QLoRA")), alt48
                page.wait_for_function("""() => {
                    const img=document.querySelector('.reader-content img');
                    return img && img.complete && img.naturalWidth===1600 && img.naturalHeight===1000;
                }""")
                assert c48["mathIndexes"], "chapter 48 MathML missing"
                math48_index = c48["mathIndexes"][0]
                page.evaluate(f"openSec('{BOOK_ID}',1,{math48_index})")
                math48 = page.locator(".reader-content math").first
                assert page.locator(".reader-content math").count() == 1
                assert math48.get_attribute("aria-label") and "وزن مؤثر" in math48.get_attribute("aria-label")
                assert page.locator(".reader-content").evaluate("e => e.scrollWidth <= e.clientWidth + 2")
                assert c48["answerIndexes"], "chapter 48 answer link missing"
                page.evaluate(f"openSec('{BOOK_ID}',1,{c48['answerIndexes'][0]})")
                assert page.locator(".reader-content a[href='book-engineering/answers/48-peft-fa.md']").count() == 1
                appendix48 = next(i for i, title in enumerate(c48["titles"]) if "پیوست اجرایی" in title)
                page.evaluate(f"openSec('{BOOK_ID}',1,{appendix48})")
                assert page.locator(".reader-content pre code").last.text_content().rstrip("\n") == project48

                # Chapter 49: preference diagram, MathML, independent answer and exact tested code.
                page.evaluate(f"openItem('{BOOK_ID}','book')")
                headers = page.locator(".chapter-header")
                assert headers.count() == 7
                headers.nth(2).click()
                page.evaluate(f"openSec('{BOOK_ID}',2,0)")
                image49 = page.locator(".reader-content img").first
                alt49 = image49.get_attribute("alt")
                assert all(term in alt49 for term in ("شکل ۴-۳-۱", "RLHF", "DPO", "GRPO", "RLAIF")), alt49
                page.wait_for_function("""() => {
                    const img=document.querySelector('.reader-content img');
                    return img && img.complete && img.naturalWidth===1600 && img.naturalHeight===1000;
                }""")
                assert c49["mathIndexes"], "chapter 49 MathML missing"
                math49_index = c49["mathIndexes"][0]
                page.evaluate(f"openSec('{BOOK_ID}',2,{math49_index})")
                math49 = page.locator(".reader-content math").first
                assert page.locator(".reader-content math").count() == 1
                assert math49.get_attribute("aria-label") and "احتمال ترجیح" in math49.get_attribute("aria-label")
                assert page.locator(".reader-content").evaluate("e => e.scrollWidth <= e.clientWidth + 2")
                assert c49["answerIndexes"], "chapter 49 answer link missing"
                page.evaluate(f"openSec('{BOOK_ID}',2,{c49['answerIndexes'][0]})")
                assert page.locator(".reader-content a[href='book-engineering/answers/49-preference-optimization-fa.md']").count() == 1
                appendix49 = next(i for i, title in enumerate(c49["titles"]) if "پیوست اجرایی" in title)
                page.evaluate(f"openSec('{BOOK_ID}',2,{appendix49})")
                assert page.locator(".reader-content pre code").last.text_content().rstrip("\n") == project49

                # Chapter 50: synthetic-data diagram, accessible MathML, answer and exact project code.
                page.evaluate(f"openItem('{BOOK_ID}','book')")
                headers = page.locator(".chapter-header")
                assert headers.count() == 7
                headers.nth(3).click()
                page.evaluate(f"openSec('{BOOK_ID}',3,0)")
                image50 = page.locator(".reader-content img").first
                alt50 = image50.get_attribute("alt")
                assert all(term in alt50 for term in ("شکل ۴-۴-۱", "دادهٔ مصنوعی", "teacher", "student", "curriculum")), alt50
                page.wait_for_function("""() => {
                    const img=document.querySelector('.reader-content img');
                    return img && img.complete && img.naturalWidth===1600 && img.naturalHeight===1000;
                }""")
                assert len(c50["mathIndexes"]) >= 4, "chapter 50 MathML missing"
                math50_index = c50["mathIndexes"][0]
                page.evaluate(f"openSec('{BOOK_ID}',3,{math50_index})")
                math50 = page.locator(".reader-content math").first
                assert page.locator(".reader-content math").count() == 2
                assert math50.get_attribute("aria-label") and "دما" in math50.get_attribute("aria-label")
                assert page.locator(".reader-content").evaluate("e => e.scrollWidth <= e.clientWidth + 2")
                assert c50["answerIndexes"], "chapter 50 independent answer link missing"
                page.evaluate(f"openSec('{BOOK_ID}',3,{c50['answerIndexes'][0]})")
                assert page.locator(".reader-content a[href='book-engineering/answers/50-synthetic-reasoning-fa.md']").count() == 1
                appendix50 = next(i for i, title in enumerate(c50["titles"]) if "پیوست اجرایی" in title)
                page.evaluate(f"openSec('{BOOK_ID}',3,{appendix50})")
                assert page.locator(".reader-content pre code").last.text_content().rstrip("\n") == project50
                # Chapter 51: ViT figure, patch MathML, independent answer and exact tested code.
                page.evaluate(f"openItem('{BOOK_ID}','book')")
                headers = page.locator(".chapter-header")
                assert headers.count() == 7
                headers.nth(4).click()
                page.evaluate(f"openSec('{BOOK_ID}',4,0)")
                image51 = page.locator(".reader-content img").first
                alt51 = image51.get_attribute("alt")
                assert all(term in alt51 for term in ("شکل ۴-۵-۱", "Vision Transformer", "وصله", "retrieval")), alt51
                page.wait_for_function("""() => {
                    const img=document.querySelector('.reader-content img');
                    return img && img.complete && img.naturalWidth===1600 && img.naturalHeight===1000;
                }""")
                assert len(c51["mathIndexes"]) >= 4, "chapter 51 MathML missing"
                math51_index = c51["mathIndexes"][0]
                page.evaluate(f"openSec('{BOOK_ID}',4,{math51_index})")
                math51 = page.locator(".reader-content math").first
                assert page.locator(".reader-content math").count() >= 1
                assert math51.get_attribute("aria-label") and "تعداد وصله" in math51.get_attribute("aria-label")
                assert page.locator(".reader-content").evaluate("e => e.scrollWidth <= e.clientWidth + 2")
                assert c51["answerIndexes"], "chapter 51 independent answer link missing"
                page.evaluate(f"openSec('{BOOK_ID}',4,{c51['answerIndexes'][0]})")
                assert page.locator(".reader-content a[href='book-engineering/answers/51-vision-models-fa.md']").count() == 1
                appendix51 = next(i for i, title in enumerate(c51["titles"]) if "پیوست اجرایی" in title)
                page.evaluate(f"openSec('{BOOK_ID}',4,{appendix51})")
                assert page.locator(".reader-content pre code").last.text_content().rstrip("\n") == project51

                # Chapter 52: speech/audio diagram, accessible framing/metric MathML, answer and exact tested code.
                page.evaluate(f"openItem('{BOOK_ID}','book')")
                headers = page.locator(".chapter-header")
                assert headers.count() == 7
                headers.nth(5).click()
                page.evaluate(f"openSec('{BOOK_ID}',5,0)")
                image52 = page.locator(".reader-content img").first
                alt52 = image52.get_attribute("alt")
                assert all(term in alt52 for term in ("شکل ۴-۶-۱", "ASR", "TTS", "Audio-Language")), alt52
                page.wait_for_function("""() => {
                    const img=document.querySelector('.reader-content img');
                    return img && img.complete && img.naturalWidth===1600 && img.naturalHeight===1000;
                }""")
                assert len(c52["mathIndexes"]) >= 5, "chapter 52 accessible MathML missing"
                math52_index = c52["mathIndexes"][0]
                page.evaluate(f"openSec('{BOOK_ID}',5,{math52_index})")
                math52 = page.locator(".reader-content math").first
                assert math52.get_attribute("aria-label") and "تعداد نمونه" in math52.get_attribute("aria-label")
                assert page.locator(".reader-content").evaluate("e => e.scrollWidth <= e.clientWidth + 2")
                assert c52["answerIndexes"], "chapter 52 independent answer link missing"
                page.evaluate(f"openSec('{BOOK_ID}',5,{c52['answerIndexes'][0]})")
                assert page.locator(".reader-content a[href='book-engineering/answers/52-audio-models-fa.md']").count() == 1
                appendix52 = next(i for i, title in enumerate(c52["titles"]) if "پیوست اجرایی" in title)
                page.evaluate(f"openSec('{BOOK_ID}',5,{appendix52})")
                assert page.locator(".reader-content pre code").last.text_content().rstrip("\n") == project52
                # Chapter 53: conditional diffusion diagram, MathML, independent answer and exact tested code.
                page.evaluate(f"openItem('{BOOK_ID}','book')")
                headers = page.locator(".chapter-header")
                assert headers.count() == 7
                headers.nth(6).click()
                page.evaluate(f"openSec('{BOOK_ID}',6,0)")
                image53 = page.locator(".reader-content img").first
                alt53 = image53.get_attribute("alt")
                assert all(term in alt53 for term in ("شکل ۴-۷-۱", "diffusion شرطی", "cross-attention", "provenance")), alt53
                page.wait_for_function("""() => {
                    const img=document.querySelector('.reader-content img');
                    return img && img.complete && img.naturalWidth===1600 && img.naturalHeight===1000;
                }""")
                assert c53["mathCount"] >= 9 and c53["mathIndexes"], "chapter 53 MathML missing"
                math53_index = c53["mathIndexes"][0]
                page.evaluate(f"openSec('{BOOK_ID}',6,{math53_index})")
                math53 = page.locator(".reader-content math").first
                assert page.locator(".reader-content math").count() == 1
                assert math53.get_attribute("aria-label") and "گام پیش‌رو" in math53.get_attribute("aria-label")
                assert page.locator(".reader-content").evaluate("e => e.scrollWidth <= e.clientWidth + 2")
                assert c53["answerIndexes"], "chapter 53 independent answer link missing"
                page.evaluate(f"openSec('{BOOK_ID}',6,{c53['answerIndexes'][0]})")
                assert page.locator(".reader-content a[href='book-engineering/answers/53-image-video-generation-fa.md']").count() == 1
                appendix53 = next(i for i, title in enumerate(c53["titles"]) if "پیوست اجرایی" in title)
                page.evaluate(f"openSec('{BOOK_ID}',6,{appendix53})")
                assert page.locator(".reader-content pre code").last.text_content().rstrip("\n") == project53

                assert not errors, errors

                assert page.evaluate("navigator.serviceWorker.ready.then(() => true)")
                page.wait_for_timeout(250)
                cache_check = page.evaluate("""async arg => {
                  const cache=await caches.open(arg.cacheName), bad=[];
                  for(const path of arg.paths){
                    const url=new URL(path,location.href).href;
                    const response=await cache.match(url);
                    if(!response || !response.ok) bad.push(path);
                  }
                  return bad;
                }""", {"cacheName": CACHE_NAME, "paths": OFFLINE_PATHS})
                assert cache_check == [], cache_check

                context.set_offline(True)
                offline47 = page.evaluate("fetch('book-engineering/answers/47-posttraining-fa.md').then(r => r.ok ? r.text() : '')")
                offline48 = page.evaluate("fetch('book-engineering/answers/48-peft-fa.md').then(r => r.ok ? r.text() : '')")
                offline49 = page.evaluate("fetch('book-engineering/answers/49-preference-optimization-fa.md').then(r => r.ok ? r.text() : '')")
                offline50 = page.evaluate("fetch('book-engineering/answers/50-synthetic-reasoning-fa.md').then(r => r.ok ? r.text() : '')")
                offline51 = page.evaluate("fetch('book-engineering/answers/51-vision-models-fa.md').then(r => r.ok ? r.text() : '')")
                offline52 = page.evaluate("fetch('book-engineering/answers/52-audio-models-fa.md').then(r => r.ok ? r.text() : '')")
                offline53 = page.evaluate("fetch('book-engineering/answers/53-image-video-generation-fa.md').then(r => r.ok ? r.text() : '')")
                source51 = page.evaluate("fetch('book-engineering/chapters/51-vision-models.md').then(r => r.ok ? r.text() : '')")
                source52 = page.evaluate("fetch('book-engineering/chapters/52-audio-models.md').then(r => r.ok ? r.text() : '')")
                source53 = page.evaluate("fetch('book-engineering/chapters/53-image-video-generation.md').then(r => r.ok ? r.text() : '')")
                report53 = page.evaluate("fetch('book-engineering/chapters/53-audit-report-fa.md').then(r => r.ok ? r.text() : '')")
                source49 = page.evaluate("fetch('book-engineering/chapters/49-preference-optimization.md').then(r => r.ok ? r.text() : '')")
                source50 = page.evaluate("fetch('book-engineering/chapters/50-synthetic-reasoning.md').then(r => r.ok ? r.text() : '')")
                assert "پاسخ‌نامهٔ تشریحی فصل ۴۷" in offline47
                assert "پاسخ‌نامهٔ تشریحی فصل ۴۸" in offline48
                assert "پاسخ‌نامهٔ تشریحی فصل ۴۹" in offline49
                assert "پاسخ‌نامهٔ تشریحی فصل ۵۰" in offline50
                assert "پاسخ‌نامهٔ تشریحی فصل ۵۱" in offline51
                assert "پاسخ‌نامهٔ تشریحی فصل ۵۲" in offline52
                assert "پاسخ‌نامهٔ تشریحی فصل ۵۳" in offline53
                assert "Diffusion" in source53 and "C2PA" in source53 and "VBench" in source53
                assert "نتایج اجرای واقعی" in report53 and "synthetic_diffusion_fixture_audit_complete" in report53
                assert "DPO" in source49 and "TRL v1.17.1" in source49
                assert "synthetic_fixture" in source50 and "محاسبهٔ زمان آزمون" in source50
                assert "Vision Transformer" in source51 and "SigLIP" in source51
                assert "Qwen3-TTS" in source52 and "VocalGrad" in source52 and "آزمایشگاه CPU" in source52
                print(f"PASS volume 4 chapters 47–53 at {width}px: sections={[c47['sectionCount'],c48['sectionCount'],c49['sectionCount'],c50['sectionCount'],c51['sectionCount'],c52['sectionCount'],c53['sectionCount']]}, MathML/appendices exact, {len(OFFLINE_PATHS)} offline assets")
                context.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
