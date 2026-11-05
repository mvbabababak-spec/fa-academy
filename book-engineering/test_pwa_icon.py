"""Verify the PWA manifest and Apple home-screen icon, including offline assets.

This is a browser/HTTP check, not a physical Android or iOS installation test.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import json
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
NAME = 'The Art & Science of Building Intelligence'


def main():
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    assert manifest['name'] == manifest['short_name'] == NAME
    for icon in manifest['icons']:
        image = Image.open(ROOT / icon['src'])
        assert image.format == 'PNG'
        assert f'{image.width}x{image.height}' == icon['sizes']
    assert Image.open(ROOT/'assets/icons/intelligence-180-v2.png').size == (180, 180)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT.parent)))
    Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/{ROOT.name}/'
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=['--no-sandbox'])
            context = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
            page = context.new_page()
            page.goto(url, wait_until='networkidle')
            page.wait_for_selector('#loading.hidden')
            assert page.title() == NAME
            assert page.locator('meta[name="application-name"]').get_attribute('content') == NAME
            assert page.locator('meta[name="apple-mobile-web-app-title"]').get_attribute('content') == NAME
            assert page.locator('link[rel="apple-touch-icon"]').get_attribute('href') == 'assets/icons/intelligence-180-v2.png'
            assert page.locator('link[rel="manifest"]').get_attribute('href') == 'manifest.json?v=2'
            cdp = context.new_cdp_session(page)
            cdp.send('Page.enable')
            manifest_response = cdp.send('Page.getAppManifest')
            assert not manifest_response.get('errors'), manifest_response
            parsed = json.loads(manifest_response['data'])
            assert parsed['name'] == parsed['short_name'] == NAME
            installability = cdp.send('Page.getInstallabilityErrors')
            assert not installability['installabilityErrors'], installability
            page.evaluate('navigator.serviceWorker.ready')
            context.set_offline(True)
            page.goto(url, wait_until='domcontentloaded')
            page.wait_for_selector('#loading.hidden')
            result = page.evaluate('''async () => {
              let paths=['manifest.json?v=2','assets/icons/intelligence-180-v2.png',
                         'assets/icons/intelligence-192-v2.png','assets/icons/intelligence-512-v2.png'];
              let out=[];for(let path of paths){try{let r=await fetch(path);out.push([path,r.ok,(await r.arrayBuffer()).byteLength])}catch(e){out.push([path,false,0])}}
              return out;
            }''')
            assert all(ok and length > 0 for _, ok, length in result), result
            print('PASS manifest, Apple metadata, PNG dimensions, Chromium installability and offline assets')
            context.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
