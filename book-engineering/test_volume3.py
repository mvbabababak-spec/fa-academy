"""Chromium checks for volume 3 chapters, MathML, responsive layout and offline files."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BOOK_ID = "art-science-intelligence-v3"
TITLE = "هنر و علم ساخت هوش — جلد سوم"
CACHE_NAME = "fa-academy-v61"
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
                assert card.count() == 1 and "3 فصل" in card.inner_text() and "37 بخش" in card.inner_text()
                assert page.locator(".book-card").count() >= 3

                page.evaluate(f"openItem('{BOOK_ID}','book')")
                headers = page.locator(".chapter-header")
                assert headers.count() == 3
                for index, count in enumerate((11, 13, 13)):
                    assert f"فصل {index + 1}" in headers.nth(index).inner_text()
                    assert f"{count} بخش" in headers.nth(index).inner_text()
                headers.nth(0).click()
                assert page.locator("#item-ch-0 .section-item").count() == 11
                page.locator("#item-ch-0 .section-item").first.click()
                page.wait_for_selector(".reader-content")
                assert page.locator(".reader-content math").count() == 1
                assert page.locator(".reader-content math").first.get_attribute("aria-label")
                image = page.locator(".reader-content img").first
                assert "شکل ۳-۱-۱" in image.get_attribute("alt") and "BPE" in image.get_attribute("alt")
                page.wait_for_function("""() => {
                    const img=document.querySelector('.reader-content img');
                    return img && img.complete && img.naturalWidth === 1600 && img.naturalHeight === 1000;
                }""")

                # Chapter 34's matrix figure and accessible MathML must render locally.
                page.evaluate(f"openSec('{BOOK_ID}',1,2)")
                assert page.locator(".reader-content math").count() == 1
                math_label = page.locator(".reader-content math").first.get_attribute("aria-label")
                assert math_label and "کیو" in math_label and "وی" in math_label
                image = page.locator(".reader-content img").first
                assert all(term in image.get_attribute("alt") for term in ("شکل ۳-۲-۱", "Q/K/V", "Lq×Lk", "Lq×dv"))
                page.wait_for_function("""() => {
                    const img=document.querySelector('.reader-content img');
                    return img && img.complete && img.naturalWidth === 1600 && img.naturalHeight === 1000;
                }""")

                # Chapter 35: causal diagram, accessible equation, and explicit false future weights.
                page.evaluate(f"openSec('{BOOK_ID}',2,0)")
                image = page.locator(".reader-content img").first
                assert all(term in image.get_attribute("alt") for term in ("شکل ۳-۳-۱", "Self-Attention", "Q/K/V", "j≤i", "j>i"))
                page.wait_for_function("""() => {
                    const img=document.querySelector('.reader-content img');
                    return img && img.complete && img.naturalWidth === 1600 && img.naturalHeight === 1000;
                }""")
                page.evaluate(f"openSec('{BOOK_ID}',2,1)")
                assert page.locator(".reader-content math").count() == 1
                assert page.locator(".reader-content math").first.get_attribute("aria-label")

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
                assert result["count"] == 37 and not result["bad"], (width, result)
                assert len(result["math"]) >= 10 and all(item["label"] and item["visible"] for item in result["math"]), result["math"]

                # Test navigation across chapter boundaries in both directions.
                page.evaluate(f"openItem('{BOOK_ID}','book');openSec('{BOOK_ID}',0,10);nextSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [1, 0]
                page.evaluate("prevSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [0, 10]
                page.evaluate(f"openSec('{BOOK_ID}',1,12);nextSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [2, 0]
                page.evaluate("prevSec()")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [1, 12]

                # Stable section IDs must survive reload.
                page.evaluate(f"openItem('{BOOK_ID}','book');openSec('{BOOK_ID}',2,1)")
                page.reload(wait_until="networkidle")
                page.wait_for_selector(".reader-content")
                assert page.evaluate("[curChapterIndex,curSectionIndex]") == [2, 1]
                page.evaluate("navTo('search');doSearch('توکن‌سازی')")
                assert page.evaluate(f"window_searchResults.some(r=>JSON.stringify(r).includes('{BOOK_ID}'))")

                # Wait for all explicit chapter assets to be stored before going offline.
                page.evaluate("navigator.serviceWorker.ready")
                page.wait_for_function("""paths => caches.open('fa-academy-v61').then(async cache => {
                    for (const path of paths) {
                      const response = await cache.match(new URL(path, location.href).href);
                      if (!response) return false;
                    }
                    return true;
                })""", arg=OFFLINE_PATHS, timeout=30000)
                context.set_offline(True)
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_selector("#loading.hidden")
                assert page.get_by_text(TITLE, exact=True).count() == 1
                page.evaluate(f"openItem('{BOOK_ID}','book');openSec('{BOOK_ID}',2,0)")
                assert page.locator(".reader-content img").first.evaluate("e => e.complete && e.naturalWidth === 1600")
                offline = page.evaluate('''async paths => {
                    const bad=[];
                    for (const path of paths) {
                      try { const response=await fetch(path); if(!response.ok || !(await response.arrayBuffer()).byteLength) bad.push(path); }
                      catch(error) { bad.push(path); }
                    }
                    const answer33=await (await fetch(paths[4])).text();
                    const answer34=await (await fetch(paths[12])).text();
                    const answer35=await (await fetch(paths[19])).text();
                    const markdown=await (await fetch(paths[0])).text();
                    return {bad,answer33:answer33.includes('پاسخ‌نامه تشریحی جلد سوم'),answer34:answer34.includes('جواب‌نامهٔ تشریحی'),answer35:answer35.includes('جواب‌نامهٔ تشریحی'),markdown:markdown.includes('بازبینی شدند')};
                }''', OFFLINE_PATHS)
                assert offline == {"bad": [], "answer33": True, "answer34": True, "answer35": True, "markdown": True}, offline
                assert not errors, errors
                print(f"PASS volume 3 chapters 1–3 at {width}px: 37 sections, accessible MathML, three WebP figures, navigation, search and {len(OFFLINE_PATHS)} offline files")
                context.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
