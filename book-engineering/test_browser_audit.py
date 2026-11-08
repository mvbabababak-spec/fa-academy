"""Chromium smoke checks, including offline reload under a subdirectory.
Requires playwright + Chromium. Start from repository root.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from io import BytesIO
from PIL import Image
from threading import Thread
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parent.parent


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT.parent)))
    Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/{ROOT.name}/'
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=['--no-sandbox'])
            for width in (390, 1440):
                context = browser.new_context(viewport={'width': width, 'height': 900}, permissions=['clipboard-read', 'clipboard-write'])
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(url, wait_until='networkidle')
                page.wait_for_selector('#loading.hidden')
                def no_overflow():
                    dimensions = page.evaluate('({view:innerWidth,scroll:document.documentElement.scrollWidth})')
                    assert dimensions['scroll'] <= dimensions['view'], dimensions
                no_overflow()
                card = page.locator('.book-card').first
                card.focus()
                page.keyboard.press('Enter')
                chapter = page.locator('.chapter-header').first
                chapter.focus()
                page.keyboard.press('Space')
                section = page.locator('.section-item').first
                section.focus()
                page.keyboard.press('Enter')
                page.wait_for_selector('.reader-content')
                no_overflow()
                assert page.locator('.toc-section[aria-current="location"]').count() == 1
                if width == 390:
                    toggle = page.locator('.reader-toc-toggle')
                    assert toggle.is_visible()
                    toggle.focus()
                    page.keyboard.press('Space')
                    assert toggle.get_attribute('aria-expanded') == 'true'
                    assert page.locator('#readerToc').is_visible()
                page.reload(wait_until='networkidle')
                page.wait_for_selector('.reader-content')  # stable hash deep link
                page.get_by_label('بزرگ کردن متن').click()
                assert page.locator('.reader-content').evaluate("e => e.style.fontSize") == '17px'
                page.evaluate("openSec(getSource().id, 2, 5)")
                page.locator('.copy-code').first.click()
                expect(page.locator('.copy-code').first).to_have_text('کپی شد')
                assert page.evaluate('navigator.clipboard.readText()').strip()
                page.evaluate("openSec(getSource().id, 0, getSource().chapters[0].sections.length-1);nextSec()")
                assert page.evaluate('curChapterIndex') == 1 and page.evaluate('curSectionIndex') == 0
                page.evaluate('prevSec()')
                assert page.evaluate('curChapterIndex') == 0
                page.evaluate("openSec(getSource().id, 20, 9)")
                assert page.locator('.reader-nav-btn').last.is_disabled() is False  # later controls follow navigation
                assert page.locator('button[onclick="nextSec()"]').is_disabled()
                page.evaluate("navTo('search')")
                counts = []
                for term in ('یادگیری‌ماشین', 'یادگیری ماشین'):
                    page.locator('#searchPageInput').fill(term)
                    page.locator('#searchPageInput').press('Enter')
                    counts.append(page.locator('.search-result').count())
                assert counts[0] == counts[1] and counts[0] > 0, counts
                assert page.locator('.search-result').first.evaluate('e => e.tagName') == 'BUTTON'
                page.evaluate('navigator.serviceWorker.ready')
                page.wait_for_timeout(500)
                context.set_offline(True)
                page.goto(url, wait_until='domcontentloaded')
                page.wait_for_selector('#loading.hidden')
                page.get_by_text('هنر و علم ساخت هوش — جلد اول', exact=True).click()
                page.locator('.chapter-header').first.click()
                page.locator('.section-item').first.click()
                page.wait_for_selector('.reader-content')
                no_overflow()
                page.evaluate('''() => {let c=getSource().chapters[16];let i=c.sections.findIndex(s=>s.html.includes('ch17-matrix.webp'));openSec(getSource().id,16,i)}''')
                img = page.locator('.reader-content img').first
                img.wait_for(state='visible')
                assert img.evaluate('e => e.complete && e.naturalWidth > 0'), 'chapter 17 image unavailable offline'
                assert not errors, errors
                if width == 390:
                    out = ROOT/'book-engineering/reports/browser-mobile.webp'
                    out.parent.mkdir(parents=True,exist_ok=True)
                    Image.open(BytesIO(page.screenshot())).convert('RGB').save(out, 'WEBP', quality=80)
                print(f'PASS {width}px home, reader, keyboard, search, hash and offline under subdirectory')
                context.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
