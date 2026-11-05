"""Volume 2 structural, browser, mobile and first-visit offline checks."""
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent.parent

def main():
    data=json.loads((ROOT/'data.json').read_text())
    matches=[b for b in data['books'] if b['id']=='art-science-intelligence-v2']
    assert len(matches)==1
    b=matches[0]; assert [c['num'] for c in b['chapters']]==[1,2,3,4,5,6,7,8,9,10,11]
    assert [len(c['sections']) for c in b['chapters']]==[9,9,11,9,9,9,9,9,9,9,9]
    ids=[s['id'] for c in b['chapters'] for s in c['sections']]
    assert len(ids)==len(set(ids))==101
    assert all(s['html'] and (ROOT/s['file']).is_file() for c in b['chapters'] for s in c['sections'])
    for img in ['v2-ch01-split.webp','v2-ch02-regression.webp','v2-ch03-cross-validation.webp','v2-ch04-unsupervised.webp','v2-ch05-validation.webp','v2-ch06-mlp.webp','v2-ch07-backprop.webp','v2-ch08-optimizers.webp','v2-ch09-network.webp','v2-ch10-cnn.webp','v2-ch11-representations.webp']:
        with Image.open(ROOT/'assets/images/babak-ai'/img) as im: assert im.format=='WEBP' and im.width>=1000
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT.parent)))
    Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_port}/{ROOT.name}/'
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(args=['--no-sandbox'])
            for width in [320,390,1440]:
                ctx=browser.new_context(viewport={'width':width,'height':900})
                page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(url,wait_until='networkidle');page.wait_for_selector('#loading.hidden')
                assert page.get_by_text('هنر و علم ساخت هوش — جلد دوم',exact=True).count()==1
                card=page.locator('.book-card').filter(has_text='هنر و علم ساخت هوش — جلد دوم')
                assert '11 فصل' in card.inner_text() and '101 بخش' in card.inner_text()
                card.click();assert page.locator('.chapter-header').count()==11
                page.locator('.chapter-header').first.click();page.locator('.section-item').first.click()
                page.wait_for_selector('.reader-content');assert page.locator('.reader-content').get_by_text('Babak & Ai').count()==1
                page.evaluate("openSec(getSource().id,0,7)")
                math=page.locator('.reader-content math').first
                assert math.count()==1 and math.is_visible() and math.get_attribute('aria-label')
                assert page.locator('.reader-content').get_by_text('دقت برابر تعداد نمونه‌های درست تقسیم بر کل نمونه‌هاست.').count()==1
                page.evaluate("openSec(getSource().id,1,1)")
                assert page.locator('.reader-content math').count()==1 and page.locator('.reader-content math').first.is_visible()
                page.evaluate("openSec(getSource().id,1,3)")
                assert page.locator('.reader-content math').count()==3
                assert all(page.locator('.reader-content math').nth(i).is_visible() for i in range(3))
                page.evaluate("openSec(getSource().id,0,8);nextSec()")
                assert page.evaluate('[curChapterIndex,curSectionIndex]')==[1,0]
                page.evaluate('prevSec()');assert page.evaluate('[curChapterIndex,curSectionIndex]')==[0,8]
                page.evaluate("openSec(getSource().id,2,10);nextSec()")
                assert page.evaluate('[curChapterIndex,curSectionIndex]')==[3,0]
                page.evaluate("openSec(getSource().id,10,8)")
                page.reload(wait_until='networkidle');assert page.evaluate('[curChapterIndex,curSectionIndex]')==[10,8]
                assert page.locator('button[onclick="nextSec()"]').is_disabled()
                page.evaluate("navTo('search');doSearch('ناخالصی جینی')")
                assert page.evaluate("window_searchResults.some(r=>r.sourceId==='art-science-intelligence-v2' || JSON.stringify(r).includes('art-science-intelligence-v2'))")
                page.evaluate("doSearch('پس‌انتشار')")
                assert page.evaluate("window_searchResults.some(r=>JSON.stringify(r).includes('art-science-intelligence-v2'))")
                page.evaluate("openItem('art-science-intelligence-v2','book')")
                bad=page.evaluate('''() => {let bad=[];getSource().chapters.forEach((c,ci)=>c.sections.forEach((s,si)=>{openSec(getSource().id,ci,si);let e=document.querySelector('.reader-content'); if (document.documentElement.scrollWidth>innerWidth||e.scrollWidth>e.clientWidth+2)bad.push(s.id)}));return bad}''')
                assert not bad,(width,bad)
                page.evaluate('navigator.serviceWorker.ready')
                ctx.set_offline(True)
                page.goto(url,wait_until='domcontentloaded');page.wait_for_selector('#loading.hidden')
                assert page.get_by_text('هنر و علم ساخت هوش — جلد دوم',exact=True).count()==1
                page.evaluate("openItem('art-science-intelligence-v2','book')")
                result=page.evaluate('''async () => {let paths=[];for(let c of getSource().chapters) for(let s of c.sections){let el=document.createElement('div');el.innerHTML=s.html; for(let i of el.querySelectorAll('img'))paths.push(i.getAttribute('src'));for(let a of el.querySelectorAll('a[href*="book-engineering/answers/"]'))paths.push(a.getAttribute('href'));} let bad=[];for(let path of [...new Set(paths)]){try{let r=await fetch(path);if(!r.ok||!(await r.arrayBuffer()).byteLength)bad.push(path)}catch(e){bad.push(path)}}return {count:new Set(paths).size,bad}}''')
                assert result=={'count':22,'bad':[]},result
                page.evaluate("openSec(getSource().id,2,6)")
                assert page.locator('.reader-content img').evaluate('e=>e.complete && e.naturalWidth>0')
                for chapter,section in [(3,2),(4,1),(5,4),(6,2),(7,1),(8,2),(9,1),(10,2)]:
                    page.evaluate(f"openSec(getSource().id,{chapter},{section})")
                    assert page.locator('.reader-content img').evaluate('e=>e.complete && e.naturalWidth>0')
                assert not errors,errors
                print(f'PASS volume 2 {width}px: 101 sections, home, navigation, hash, search and 22 offline assets')
                ctx.close()
            browser.close()
    finally: server.shutdown()
if __name__=='__main__':main()
