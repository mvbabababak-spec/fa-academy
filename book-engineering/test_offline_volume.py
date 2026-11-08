"""Check locally that volume 1 images and linked answer keys survive offline reload."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent

def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT.parent)))
    Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/{ROOT.name}/'
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=['--no-sandbox'])
            ctx = browser.new_context()
            page = ctx.new_page()
            page.goto(url, wait_until='networkidle')
            page.wait_for_selector('#loading.hidden')
            page.evaluate('navigator.serviceWorker.ready')
            ctx.set_offline(True)
            page.goto(url, wait_until='domcontentloaded')
            page.wait_for_selector('#loading.hidden')
            result = page.evaluate('''async () => {
              let b=DATA.books.find(x=>x.id==='art-science-intelligence-v1'), paths=[];
              for (let c of b.chapters) for (let s of c.sections) {
                let el=document.createElement('div');el.innerHTML=s.html;
                for (let a of el.querySelectorAll('a[href*="book-engineering/answers/"]')) paths.push(a.getAttribute('href'));
                for (let img of el.querySelectorAll('img[src^="assets/images/"]')) paths.push(img.getAttribute('src'));
              }
              paths=[...new Set(paths)];let bad=[];
              for (let path of paths) try {let r=await fetch(path);if (!r.ok || !(await r.arrayBuffer()).byteLength) bad.push([path,r.status])}
              catch(e) {bad.push([path,String(e)])}
              return {count:paths.length,bad};
            }''')
            assert result['count'] == 48 and not result['bad'], result
            print('PASS offline: 21 answer keys and 27 volume images')
            ctx.close()
            browser.close()
    finally:
        server.shutdown()

if __name__ == '__main__':
    main()
