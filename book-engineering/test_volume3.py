"""Chromium checks for volume 3 chapter 1, responsive layout, search and offline files."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BOOK_ID = "art-science-intelligence-v3"
TITLE = "هنر و علم ساخت هوش — جلد سوم"
OFFLINE_PATHS = [
    "volume-3-full-fa.md",
    "assets/images/babak-ai/v3-ch01-tokenization.webp",
    "book-engineering/answers/33-tokenization-fa.md",
    "book-engineering/chapters/33-tokenization.md",
    "book-engineering/projects/33-tokenization/README.md",
    "book-engineering/projects/33-tokenization/tokenizer_bpe.py",
    "book-engineering/projects/33-tokenization/test_tokenizer_bpe.py",
    "book-engineering/projects/33-tokenization/test_embedding_lookup.py",
]


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
                assert card.count() == 1 and "1 فصل" in card.inner_text() and "11 بخش" in card.inner_text()
                assert page.locator(".book-card").count() >= 3

                page.evaluate(f"openItem('{BOOK_ID}','book')")
                assert page.locator(".chapter-header").count() == 1
                assert "فصل 1" in page.locator(".chapter-header").first.inner_text()
                assert page.locator(".section-item").count() == 11
                page.locator(".chapter-header").first.click()
                page.locator(".section-item").first.click()
                page.wait_for_selector(".reader-content")
                assert page.locator(".reader-content math").count() == 1
                assert page.locator(".reader-content math").first.get_attribute("aria-label")
                image = page.locator(".reader-content img").first
                assert "شکل ۳-۱-۱" in image.get_attribute("alt") and "BPE" in image.get_attribute("alt")
                page.wait_for_function("""() => {
                    const img=document.querySelector('.reader-content img');
                    return img && img.complete && img.naturalWidth === 1600 && img.naturalHeight === 1000;
                }""")
                assert image.evaluate("e => e.complete && e.naturalWidth === 1600 && e.naturalHeight === 1000")

                # Visit every section to check MathML exposure and horizontal overflow.
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
                assert result["count"] == 11 and not result["bad"], (width, result)
                assert len(result["math"]) >= 5 and all(item["label"] and item["visible"] for item in result["math"]), result["math"]

                page.evaluate(f"openItem('{BOOK_ID}','book');openSec('{BOOK_ID}',0,0);nextSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [0, 1]
                page.evaluate("prevSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [0, 0]
                page.reload(wait_until="networkidle")
                page.wait_for_selector(".reader-content")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [0, 0]
                page.evaluate("navTo('search');doSearch('توکن‌سازی')")
                assert page.evaluate(f"window_searchResults.some(r=>JSON.stringify(r).includes('{BOOK_ID}'))")

                page.evaluate("navigator.serviceWorker.ready")
                page.wait_for_timeout(900)
                context.set_offline(True)
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_selector("#loading.hidden")
                assert page.get_by_text(TITLE, exact=True).count() == 1
                page.evaluate(f"openItem('{BOOK_ID}','book');openSec('{BOOK_ID}',0,0)")
                assert page.locator(".reader-content img").first.evaluate("e => e.complete && e.naturalWidth === 1600")
                offline = page.evaluate('''async paths => {
                    const bad=[];
                    for (const path of paths) {
                      try { const response=await fetch(path); if(!response.ok || !(await response.arrayBuffer()).byteLength) bad.push(path); }
                      catch(error) { bad.push(path); }
                    }
                    const answer=await (await fetch(paths[2])).text();
                    const markdown=await (await fetch(paths[0])).text();
                    return {bad,answer:answer.includes('پاسخ‌نامه تشریحی جلد سوم'),markdown:markdown.includes('بازبینی شدند')};
                }''', OFFLINE_PATHS)
                assert offline == {"bad": [], "answer": True, "markdown": True}, offline
                assert not errors, errors
                print(f"PASS volume 3 chapter 1 at {width}px: 11 sections, MathML, WebP, search, hash, navigation and {len(OFFLINE_PATHS)} offline files")
                context.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
