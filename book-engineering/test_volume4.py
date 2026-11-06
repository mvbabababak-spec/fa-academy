"""Browser, accessibility, exact-appendix and offline checks for volume 4."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BOOK_ID = "art-science-intelligence-v4"
TITLE = "هنر و علم ساخت هوش — جلد چهارم"
CACHE_NAME = "fa-academy-v79"
OFFLINE_PATHS = [
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
]


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT.parent)))
    Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/{ROOT.name}/"
    project47 = (ROOT / "book-engineering/projects/47-instruction-tuning/sft_experiment.py").read_text(encoding="utf-8").rstrip()
    project48 = (ROOT / "book-engineering/projects/48-peft-lab/peft_lab.py").read_text(encoding="utf-8").rstrip()
    project49 = (ROOT / "book-engineering/projects/49-preference-lab/preference_lab.py").read_text(encoding="utf-8").rstrip()
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
                    answerIndexes:ch.sections.map((section,index)=>section.html.includes('answers/')?index:-1).filter(index=>index>=0),
                    sectionCount:ch.sections.length
                  }}))}};
                }}''')
                assert len(metadata["chapters"]) == 3, metadata
                c47, c48, c49 = metadata["chapters"]
                assert [c["id"] for c in metadata["chapters"]] == [
                    "art-science-v4-ch01", "art-science-v4-ch02", "art-science-v4-ch03"
                ], metadata
                for chapter in metadata["chapters"]:
                    assert chapter["sectionCount"] >= 15
                    assert chapter["sectionIds"][0].endswith("-s01")
                    assert len(set(chapter["sectionIds"])) == chapter["sectionCount"]

                # Chapter 47: SFT figure, accessible MathML, answer and exact appendix.
                page.evaluate(f"openItem('{BOOK_ID}','book')")
                headers = page.locator(".chapter-header")
                assert headers.count() == 3
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
                assert headers.count() == 3
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
                assert headers.count() == 3
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
                source49 = page.evaluate("fetch('book-engineering/chapters/49-preference-optimization.md').then(r => r.ok ? r.text() : '')")
                assert "پاسخ‌نامهٔ تشریحی فصل ۴۷" in offline47
                assert "پاسخ‌نامهٔ تشریحی فصل ۴۸" in offline48
                assert "پاسخ‌نامهٔ تشریحی فصل ۴۹" in offline49
                assert "DPO" in source49 and "TRL v1.17.1" in source49
                print(f"PASS volume 4 chapters 47–49 at {width}px: sections={[c47['sectionCount'],c48['sectionCount'],c49['sectionCount']]}, MathML/appendices exact, {len(OFFLINE_PATHS)} offline assets")
                context.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
