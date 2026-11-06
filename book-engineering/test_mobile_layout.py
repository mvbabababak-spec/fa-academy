"""Mobile layout and navigation checks; requires Playwright and Chromium.

Runs a local server under a subdirectory. Scroll locking is checked on the
outer document, while code blocks and tables keep their own scrolling.
"""
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
            for width in (320, 390, 414, 768, 1440):
                context = browser.new_context(viewport={'width': width, 'height': 900}, is_mobile=width < 768, has_touch=width < 768)
                page = context.new_page()
                page.goto(url, wait_until='networkidle')
                page.wait_for_selector('#loading.hidden')
                page.evaluate("document.querySelectorAll('.book-card--volume img').forEach(img => img.loading='eager')")
                page.wait_for_function("""() => {
                  const imgs=Array.from(document.querySelectorAll('.book-card--volume img'));
                  return imgs.length===4 && imgs.every(img=>img.complete && img.naturalWidth===848 && img.naturalHeight===1264);
                }""")
                card = page.locator('.book-card--volume').first
                assert card.locator('.book-card-english').inner_text() == 'The Art & Science of Building Intelligence'
                cover_checks = page.evaluate("""() => {
                  const expected={
                    'art-science-intelligence-v1':'assets/images/covers/volume-1-cover.webp',
                    'art-science-intelligence-v2':'assets/images/covers/volume-2-cover.webp',
                    'art-science-intelligence-v3':'assets/images/covers/volume-3-cover.webp',
                    'art-science-intelligence-v4':'assets/images/covers/volume-4-cover.webp'
                  };
                  return Object.entries(expected).map(([id,path])=>{
                    const item=DATA.books.find(book=>book.id===id);
                    const bookCard=Array.from(document.querySelectorAll('.book-card--volume'))
                      .find(el=>el.getAttribute('onclick')===`openItem('${id}','book')`);
                    const img=bookCard&&bookCard.querySelector('img');
                    const cover=bookCard&&bookCard.querySelector('.book-card-cover');
                    const rect=cover&&cover.getBoundingClientRect();
                    return {id,path,cover:item&&item.cover,src:img&&new URL(img.currentSrc).pathname,
                      dimensions:img&&[img.naturalWidth,img.naturalHeight],fit:img&&getComputedStyle(img).objectFit,
                      ratio:rect&&rect.width/rect.height};
                  });
                }""")
                assert len(cover_checks) == 4, cover_checks
                for result_cover in cover_checks:
                    assert result_cover['cover'] == result_cover['path'], result_cover
                    assert result_cover['src'].endswith(result_cover['path']), result_cover
                    assert result_cover['dimensions'] == [848, 1264], result_cover
                    assert result_cover['fit'] == 'contain' and 0.65 < result_cover['ratio'] < 0.68, result_cover
                dims = page.evaluate('''() => ({viewport: innerWidth, root: document.documentElement.scrollWidth,
                    header: document.querySelector('.header-nav').scrollWidth,
                    headerVisible: document.querySelector('.header-nav').clientWidth})''')
                assert dims['root'] == dims['viewport'] and dims['header'] <= dims['headerVisible'] + 1, dims
                page.evaluate("openItem('art-science-intelligence-v1','book');openSec('art-science-intelligence-v1',0,0)")
                prev = page.locator('button[onclick="prevSec()"]')
                next_button = page.locator('button[onclick="nextSec()"]')
                assert prev.is_disabled() and not next_button.is_disabled()
                assert next_button.bounding_box()['x'] > prev.bounding_box()['x'], 'next button should be visually to the right of previous'
                next_button.click()
                assert page.evaluate('curChapterIndex') == 0 and page.evaluate('curSectionIndex') == 1
                page.locator('button[onclick="prevSec()"]').click()
                assert page.evaluate('curChapterIndex') == 0 and page.evaluate('curSectionIndex') == 0
                page.evaluate('window.scrollTo(500,0)')
                assert page.evaluate('window.scrollX') == 0
                if width < 768:
                    cdp = context.new_cdp_session(page)
                    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': width // 2, 'y': 300}]})
                    cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': width - 10, 'y': 300}]})
                    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
                    assert page.evaluate('window.scrollX') == 0
                result = page.evaluate('''() => {
                  let bad=[],count=0,typographyFailures=[],typography={};
                  const isVolumeId=id=>/^art-science-intelligence-v[1-5]$/.test(id);
                  const targetBooks=DATA.books.filter(item=>isVolumeId(item.id));
                  targetBooks.forEach(item=>typography[item.id]={sections:0,paragraphs:0,justified:0,indented:0,formulas:0,captions:0});
                  ['books','courses'].forEach(type => DATA[type].forEach(item => {
                    const itemType=type==='books'?'book':'course';
                    const isTargetBook=itemType==='book'&&isVolumeId(item.id);
                    openItem(item.id,itemType);
                    (item.chapters||[]).forEach((ch,ci)=>(ch.sections||[]).forEach((sec,si)=>{
                      openSec(item.id,ci,si);
                      const content=document.querySelector('.reader-content');
                      const nav=document.querySelector('.reader-nav');
                      const rect=content.getBoundingClientRect();
                      if(content.scrollWidth>content.clientWidth+2 || nav.scrollWidth>nav.clientWidth+2 || rect.left < -1 || rect.right > innerWidth+1 || document.documentElement.scrollWidth>innerWidth) {
                        bad.push({id:item.id,chapter:ci+1,section:si+1, content:[content.scrollWidth,content.clientWidth],nav:[nav.scrollWidth,nav.clientWidth],rect:[rect.left,rect.right]});
                      }
                      const hasProseClass=content.classList.contains('reader-content--book-prose');
                      if(hasProseClass!==isTargetBook) typographyFailures.push({id:item.id,chapter:ci+1,section:si+1,reason:'scope class'});
                      if(isTargetBook){
                        const stats=typography[item.id];stats.sections++;
                        const paragraphs=Array.from(content.querySelectorAll('p:not(:has(math)):not(.reader-caption)')).filter(p=>p.textContent.trim());
                        stats.paragraphs+=paragraphs.length;
                        paragraphs.forEach(p=>{
                          const s=getComputedStyle(p);
                          if(s.direction!=='rtl'||s.textAlign!=='justify'||s.textAlignLast!=='start'||s.textJustify!=='inter-word'){
                            if(typographyFailures.length<30)typographyFailures.push({id:item.id,chapter:ci+1,section:si+1,reason:'prose alignment',direction:s.direction,align:s.textAlign,last:s.textAlignLast,justify:s.textJustify});
                          }else stats.justified++;
                          if(parseFloat(s.textIndent)>0)stats.indented++;
                        });
                        const headingLeads=content.querySelectorAll('h1+p,h2+p,h3+p,h4+p,h5+p,h6+p');
                        headingLeads.forEach(p=>{
                          if(parseFloat(getComputedStyle(p).textIndent)>0&&typographyFailures.length<30)typographyFailures.push({id:item.id,chapter:ci+1,section:si+1,reason:'first paragraph after heading indented'});
                        });
                        const formulaParagraphs=content.querySelectorAll('p:has(math)');
                        formulaParagraphs.forEach(p=>{
                          if(getComputedStyle(p).textAlign==='justify'&&typographyFailures.length<30)typographyFailures.push({id:item.id,chapter:ci+1,section:si+1,reason:'MathML paragraph was justified'});
                        });
                        content.querySelectorAll('math').forEach(math=>{
                          stats.formulas++;
                          if(getComputedStyle(math).textAlign==='justify'&&typographyFailures.length<30)typographyFailures.push({id:item.id,chapter:ci+1,section:si+1,reason:'MathML alignment inherited justification'});
                        });
                        const captions=content.querySelectorAll('p.reader-caption');
                        stats.captions+=captions.length;
                        captions.forEach(p=>{
                          const s=getComputedStyle(p);
                          if((s.textAlign==='justify'||parseFloat(s.textIndent)>0)&&typographyFailures.length<30)typographyFailures.push({id:item.id,chapter:ci+1,section:si+1,reason:'caption received prose formatting',align:s.textAlign,indent:s.textIndent});
                        });
                        content.querySelectorAll('li:not(:has(math))').forEach(li=>{
                          const s=getComputedStyle(li);
                          if((s.textAlign!=='justify'||s.textAlignLast!=='start')&&typographyFailures.length<30)typographyFailures.push({id:item.id,chapter:ci+1,section:si+1,reason:'list alignment',align:s.textAlign,last:s.textAlignLast});
                        });
                      }
                      count++;
                    }));
                  }));
                  const expected=DATA.books.concat(DATA.courses).reduce((total,item)=>total+(item.chapters||[]).reduce((n,ch)=>n+(ch.sections||[]).length,0),0);
                  const typographyMissing=targetBooks.filter(item=>{
                    const t=typography[item.id];
                    return !t||t.sections===0||t.paragraphs===0||t.paragraphs!==t.justified||t.indented===0||t.formulas===0||t.captions===0;
                  }).map(item=>({id:item.id,stats:typography[item.id]}));
                  return {count,expected,bad,typographyFailures,typographyMissing,typography};
                }''')
                assert result['count'] == result['expected'] and not result['bad'], result
                assert not result['typographyFailures'] and not result['typographyMissing'], result
                page.evaluate('navigator.serviceWorker.ready')
                page.wait_for_timeout(250)
                context.set_offline(True)
                page.goto(url, wait_until='domcontentloaded')
                page.wait_for_selector('#loading.hidden')
                page.evaluate("document.querySelectorAll('.book-card--volume img').forEach(img => img.loading='eager')")
                page.wait_for_function("""() => {
                  const imgs=Array.from(document.querySelectorAll('.book-card--volume img'));
                  return imgs.length===4 && imgs.every(img=>img.complete && img.naturalWidth===848 && img.naturalHeight===1264);
                }""")
                offline_images = page.locator('.book-card--volume img')
                assert offline_images.count() == 4, 'expected all four book covers offline'
                answer = page.evaluate("fetch('book-engineering/answers/01-intelligence-answers-fa.md').then(r => r.ok ? r.text() : '')")
                assert 'پاسخ‌نامه فصل ۱' in answer, 'answer key unavailable offline'
                typography_summary=', '.join(
                    f"{book_id}: {stats['paragraphs']} justified prose paragraphs, {stats['indented']} indented, {stats['formulas']} MathML, {stats['captions']} captions"
                    for book_id,stats in result['typography'].items()
                )
                print(f"PASS {width}px: cover online/offline, text, header, RTL navigation, locked viewport and {result['count']} sections; {typography_summary}")
                context.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
