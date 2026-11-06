"""Browser, MathML, code-appendix and offline checks for volume 4 chapter 47."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BOOK_ID = "art-science-intelligence-v4"
TITLE = "هنر و علم ساخت هوش — جلد چهارم"
CACHE_NAME = "fa-academy-v77"
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
]


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT.parent)))
    Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/{ROOT.name}/"
    expected_code = (ROOT / "book-engineering/projects/47-instruction-tuning/sft_experiment.py").read_text(encoding="utf-8").rstrip()
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
                  return {{
                    chapters:book.chapters.length,
                    chapterId:book.chapters[0].id,
                    sectionIds:book.chapters[0].sections.map(section=>section.id),
                    titles:book.chapters[0].sections.map(section=>section.title),
                    mathIndexes:book.chapters[0].sections.map((section,index)=>section.html.includes('<math')?index:-1).filter(index=>index>=0),
                    answerIndexes:book.chapters[0].sections.map((section,index)=>section.html.includes('answers/47-posttraining-fa.md')?index:-1).filter(index=>index>=0),
                    sectionCount:book.chapters[0].sections.length
                  }};
                }}''')
                assert metadata["chapters"] == 1 and metadata["chapterId"] == "art-science-v4-ch01", metadata
                assert metadata["sectionCount"] >= 15 and len(set(metadata["sectionIds"])) == metadata["sectionCount"], metadata
                assert metadata["sectionIds"][0] == "art-science-v4-ch01-s01", metadata

                page.evaluate(f"openItem('{BOOK_ID}','book')")
                headers = page.locator(".chapter-header")
                assert headers.count() == 1
                headers.first.click()
                first_section = page.locator("#item-ch-0 .section-item").first
                assert first_section.count() == 1
                first_section.click()
                page.wait_for_selector(".reader-content")
                image = page.locator(".reader-content img").first
                alt = image.get_attribute("alt")
                assert all(term in alt for term in ("شکل ۴-۱-۱", "Continued Pretraining", "SFT", "−۱۰۰", "benchmark")), alt
                page.wait_for_function("""() => {
                    const img=document.querySelector('.reader-content img');
                    return img && img.complete && img.naturalWidth===1600 && img.naturalHeight===1000;
                }""")

                assert metadata["mathIndexes"], "accessible MathML section missing"
                math_index = metadata["mathIndexes"][0]
                page.evaluate(f"openSec('{BOOK_ID}',0,{math_index})")
                math_count = page.locator(".reader-content math").count()
                assert math_count == 1
                math = page.locator(".reader-content math").first
                assert math.get_attribute("aria-label") and "زیان SFT" in math.get_attribute("aria-label")
                # The reader keeps MathML and prose/captions outside each other's typography rules.
                assert page.locator(".reader-content").evaluate("e => e.scrollWidth <= e.clientWidth + 2")

                assert metadata["answerIndexes"], "independent answer-key link section missing"
                answer_index = metadata["answerIndexes"][0]
                page.evaluate(f"openSec('{BOOK_ID}',0,{answer_index})")
                answer_link = page.locator(".reader-content a[href='book-engineering/answers/47-posttraining-fa.md']")
                assert answer_link.count() == 1
                appendix_index = next(i for i, title in enumerate(metadata["titles"]) if title.startswith("پیوست اجرایی"))
                page.evaluate(f"openSec('{BOOK_ID}',0,{appendix_index})")
                code = page.locator(".reader-content pre code").last.text_content().rstrip("\n")
                assert code == expected_code, "rendered appendix differs from tested project bytes"
                assert not errors, errors

                await_worker = page.evaluate("navigator.serviceWorker.ready.then(() => true)")
                assert await_worker
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
                offline_answer = page.evaluate("fetch('book-engineering/answers/47-posttraining-fa.md').then(r => r.ok ? r.text() : '')")
                assert "پاسخ‌نامهٔ تشریحی فصل ۴۷" in offline_answer
                offline_source = page.evaluate("fetch('book-engineering/chapters/47-posttraining.md').then(r => r.ok ? r.text() : '')")
                assert "Continued Pretraining" in offline_source and "تاریخ بازبینی منابع" in offline_source
                print(f"PASS volume 4 chapter 47 at {width}px: {metadata['sectionCount']} sections, accessible MathML, exact code appendix, {len(OFFLINE_PATHS)} offline assets")
                context.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
