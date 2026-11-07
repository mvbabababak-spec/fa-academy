"""Browser and offline-cache checks for the authored chapters in Volume 5."""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from threading import Thread

from playwright.sync_api import sync_playwright

import build_volume5 as builder

ROOT = Path(__file__).resolve().parent.parent
BOOK_ID = builder.VOLUME_ID
TITLE = "هنر و علم ساخت هوش — جلد پنجم"
CHAPTER_TITLE = "Benchmarking، طراحی آزمون، معیارها، ارزیابی انسانی، عدم‌قطعیت و آلودگی بنچمارک"
PROJECT_CODE = (ROOT / builder.APPENDIX_PROJECTS[62]).read_text(encoding="utf-8").rstrip("\n")
SW_TEXT = (ROOT / "sw.js").read_text(encoding="utf-8")
CACHE_NAME = re.search(r"const CACHE_NAME = '([^']+)'", SW_TEXT).group(1)
OFFLINE_PATHS = ["./" + path for path in builder._v5_offline_paths(builder.available_specs())]


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT.parent)))
    Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/{ROOT.name}/"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=["--no-sandbox"])
            for width in (320, 390, 768, 1440):
                context = browser.new_context(viewport={"width": width, "height": 900})
                page = context.new_page()
                errors: list[str] = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_selector("#loading.hidden")
                assert page.get_by_text(TITLE, exact=True).count() == 1
                metadata = page.evaluate(f"""() => {{
                  const book=DATA.books.find(item=>item.id==='{BOOK_ID}');
                  const chapter=book&&book.chapters[0];
                  return {{count:book&&book.chapters.length,cover:book&&book.cover,subtitle:book&&book.subtitle,
                    chapterId:chapter&&chapter.id,title:chapter&&chapter.title,
                    sectionIds:chapter&&chapter.sections.map(section=>section.id),
                    sectionTitles:chapter&&chapter.sections.map(section=>section.title),
                    sectionCount:chapter&&chapter.sections.length,
                    mathCount:chapter&&chapter.sections.reduce((n,section)=>n+(section.html.match(/<math/g)||[]).length,0)}};
                }}""")
                assert metadata["count"] == 1, metadata
                assert metadata["cover"] == "assets/images/covers/volume-5-cover.svg", metadata
                assert metadata["subtitle"] == "ارزیابی، محصول و پژوهش | ۱۲ فصل", metadata
                assert metadata["chapterId"] == "art-science-v5-ch01", metadata
                assert metadata["title"] == CHAPTER_TITLE, metadata
                assert metadata["sectionCount"] == 26, metadata
                assert metadata["sectionIds"][0] == "art-science-v5-ch01-s01", metadata
                assert metadata["sectionIds"][-1] == "art-science-v5-ch01-s26", metadata
                assert metadata["mathCount"] == 1, metadata

                # Confirm the portrait cover and the first section's accessible figure.
                page.locator(".book-card--volume img").last.evaluate("img => img.loading='eager'")
                page.wait_for_function("""() => {
                  const img=Array.from(document.querySelectorAll('.book-card--volume img'))
                    .find(node=>node.currentSrc.includes('volume-5-cover.svg'));
                  return img&&img.complete&&img.naturalWidth===848&&img.naturalHeight===1264;
                }""")
                page.evaluate(f"openItem('{BOOK_ID}','book');openSec('{BOOK_ID}',0,0)")
                if width <= 768:
                    breadcrumb_title = page.locator(".reader-breadcrumb>span:first-child")
                    assert breadcrumb_title.evaluate("e=>getComputedStyle(e).whiteSpace") == "nowrap"
                    assert page.locator(".reader-breadcrumb").evaluate("e=>e.getBoundingClientRect().height<=32")
                content = page.locator(".reader-content")
                image = content.locator("img").first
                assert image.get_attribute("alt") and "شکل ۵-۱-۱" in image.get_attribute("alt")
                page.wait_for_function("""() => {
                  const img=document.querySelector('.reader-content img');
                  return img&&img.complete&&img.naturalWidth===1200&&img.naturalHeight===680;
                }""")
                assert content.evaluate("e=>e.scrollWidth<=e.clientWidth+2")

                # MathML carries an accessible label; the content itself stays within the viewport.
                page.evaluate(f"openSec('{BOOK_ID}',0,7)")
                math = page.locator(".reader-content math").first
                assert math.count() == 1 and math.get_attribute("aria-label")
                assert page.locator(".reader-content").evaluate("e=>e.scrollWidth<=e.clientWidth+2")

                # The independent answer link is root-relative for the in-app reader.
                summary_index = next(i for i, title in enumerate(metadata["sectionTitles"]) if "جمع‌بندی" in title)
                page.evaluate(f"openSec('{BOOK_ID}',0,{summary_index})")
                assert page.locator(".reader-content a[href='book-engineering/answers/62-benchmarking-evaluation-fa.md']").count() == 1
                assert page.locator(".reader-content a[href='book-engineering/projects/62-evaluation-lab/README.md']").count() == 1
                assert page.locator(".reader-content a[href='book-engineering/chapters/62-audit-report-fa.md']").count() == 1

                appendix_index = next(i for i, title in enumerate(metadata["sectionTitles"]) if "پیوست اجرایی" in title)
                page.evaluate(f"openSec('{BOOK_ID}',0,{appendix_index})")
                assert page.locator(".reader-content pre code").last.text_content().rstrip("\n") == PROJECT_CODE

                # All authored chapter files are present in the active offline cache.
                sw_ready = page.evaluate("""async () => await Promise.race([
                  navigator.serviceWorker.ready.then(() => true),
                  new Promise(resolve => setTimeout(() => resolve(false), 30000))
                ])""")
                assert sw_ready, "service worker did not become ready within 30 seconds"
                page.wait_for_timeout(250)
                cache_misses = page.evaluate("""async arg => {
                  const cache=await caches.open(arg.cacheName), missing=[];
                  for(const path of arg.paths){
                    const response=await cache.match(new URL(path,location.href).href);
                    if(!response||!response.ok) missing.push(path);
                  }
                  return missing;
                }""", {"cacheName": CACHE_NAME, "paths": OFFLINE_PATHS})
                assert cache_misses == [], cache_misses
                context.set_offline(True)
                offline_answer = page.evaluate("fetch('book-engineering/answers/62-benchmarking-evaluation-fa.md').then(r=>r.ok?r.text():'')")
                assert "پاسخ‌نامهٔ مستقل فصل ۶۲" in offline_answer
                offline_full_text = page.evaluate("fetch('volume-5-full-fa.md').then(r=>r.ok?r.text():'')")
                assert "جلد پنجم" in offline_full_text and "فصل ۶۲" in offline_full_text
                assert not errors, errors
                print(f"PASS volume 5 chapter 62 browser/offline checks at {width}px: 26 sections, accessible MathML/SVG, exact appendix, {len(OFFLINE_PATHS)} offline paths")
                context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
