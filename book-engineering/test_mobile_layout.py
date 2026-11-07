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
                chapter59 = page.evaluate("""() => {
                  const book=DATA.books.find(item=>item.id==='art-science-intelligence-v4');
                  const chapter=book&&book.chapters[12];
                  const previous=book&&book.chapters[11];
                  return {count:book&&book.chapters.length,id:chapter&&chapter.id,sections:chapter&&chapter.sections.length,previousId:previous&&previous.id,previousSections:previous&&previous.sections.length};
                }""")
                assert chapter59 == {'count':13,'id':'art-science-v4-ch13','sections':22,'previousId':'art-science-v4-ch12','previousSections':22}, chapter59
                assert page.locator('.home-hero > p').first.inner_text() == 'مجموعه‌ای جامع از کتاب‌ها و دوره‌های آموزشی هوش مصنوعی — با دسترسی آفلاین'
                page.evaluate("document.querySelectorAll('.book-card--volume img,.book-card--microsoft img').forEach(img => img.loading='eager')")
                page.wait_for_function("""() => {
                  const imgs=Array.from(document.querySelectorAll('.book-card--volume img'));
                  return imgs.length===4 && imgs.every(img=>img.complete && img.naturalWidth===848 && img.naturalHeight===1264);
                }""")
                card = page.locator('.book-card--volume').first
                assert card.locator('.book-card-english').inner_text() == 'The Art & Science of Building Intelligence'
                cover_checks = page.evaluate("""() => {
                  const expected={
                    'art-science-intelligence-v1':{path:'assets/images/covers/volume-1-cover.webp',subtitle:'از صفر مطلق تا طراحی هوش مصنوعی | ۲۱ فصل'},
                    'art-science-intelligence-v2':{path:'assets/images/covers/volume-2-cover.webp',subtitle:'یادگیری ماشین و شبکه‌های عصبی | جلد دوم: ۱۱ فصل'},
                    'art-science-intelligence-v3':{path:'assets/images/covers/volume-3-cover.webp',subtitle:'Transformer و مهندسی مدل زبانی | ۱۴ فصل'},
                    'art-science-intelligence-v4':{path:'assets/images/covers/volume-4-cover.webp',subtitle:'پس‌آموزش، چندوجهی و زیرساخت | ۱۵ فصل'}
                  };
                  return Object.entries(expected).map(([id,copy])=>{
                    const path=copy.path;
                    const item=DATA.books.find(book=>book.id===id);
                    const bookCard=Array.from(document.querySelectorAll('.book-card--volume'))
                      .find(el=>el.getAttribute('onclick')===`openItem('${id}','book')`);
                    const img=bookCard&&bookCard.querySelector('img');
                    const cover=bookCard&&bookCard.querySelector('.book-card-cover');
                    const rect=cover&&cover.getBoundingClientRect();
                    return {id,path,expectedSubtitle:copy.subtitle,subtitle:item&&item.subtitle,author:item&&item.author,
                      cover:item&&item.cover,src:img&&new URL(img.currentSrc).pathname,
                      dimensions:img&&[img.naturalWidth,img.naturalHeight],fit:img&&getComputedStyle(img).objectFit,
                      ratio:rect&&rect.width/rect.height};
                  });
                }""")
                assert len(cover_checks) == 4, cover_checks
                for result_cover in cover_checks:
                    assert result_cover['cover'] == result_cover['path'], result_cover
                    assert result_cover['subtitle'] == result_cover['expectedSubtitle'], result_cover
                    assert result_cover['author'] == 'Babak Moradvand', result_cover
                    assert result_cover['src'].endswith(result_cover['path']), result_cover
                    assert result_cover['dimensions'] == [848, 1264], result_cover
                    assert result_cover['fit'] == 'contain' and 0.65 < result_cover['ratio'] < 0.68, result_cover
                microsoft_covers = page.evaluate("""() => {
                  const expected={
                    'ai':'assets/images/covers/microsoft-ai-for-beginners-cover.webp',
                    'genai':'assets/images/covers/microsoft-generative-ai-for-beginners-cover.webp',
                    'ml':'assets/images/covers/microsoft-ml-for-beginners-cover.webp',
                    'datascience':'assets/images/covers/microsoft-data-science-for-beginners-cover.webp'
                  };
                  return Object.entries(expected).map(([id,path])=>{
                    const item=DATA.books.find(book=>book.id===id);
                    const card=document.querySelector(`.book-card--microsoft[data-book-id="${id}"]`);
                    const img=card&&card.querySelector('img');
                    const cover=card&&card.querySelector('.book-card-cover');
                    const rect=cover&&cover.getBoundingClientRect();
                    return {id,path,cover:item&&item.cover,title:item&&item.title,
                      src:img&&new URL(img.currentSrc).pathname,
                      dimensions:img&&[img.naturalWidth,img.naturalHeight],
                      fit:img&&getComputedStyle(img).objectFit,ratio:rect&&rect.width/rect.height,
                      portrait:card&&card.classList.contains('book-card--portrait-cover')};
                  });
                }""")
                assert len(microsoft_covers) == 4, microsoft_covers
                for result_cover in microsoft_covers:
                    assert result_cover['cover'] == result_cover['path'], result_cover
                    assert result_cover['src'].endswith(result_cover['path']), result_cover
                    assert result_cover['dimensions'] == [848, 1264], result_cover
                    assert result_cover['fit'] == 'contain' and result_cover['portrait'], result_cover
                    assert 0.65 < result_cover['ratio'] < 0.68, result_cover
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
                page.evaluate("document.querySelectorAll('.book-card--volume img,.book-card--microsoft img').forEach(img => img.loading='eager')")
                page.wait_for_function("""() => {
                  const volumes=Array.from(document.querySelectorAll('.book-card--volume img'));
                  const microsoft=Array.from(document.querySelectorAll('.book-card--microsoft img'));
                  const good=imgs=>imgs.length===4 && imgs.every(img=>img.complete && img.naturalWidth===848 && img.naturalHeight===1264);
                  return good(volumes) && good(microsoft);
                }""")
                offline_images = page.locator('.book-card--volume img')
                offline_microsoft_images = page.locator('.book-card--microsoft img')
                assert offline_images.count() == 4, 'expected all four volume covers offline'
                assert offline_microsoft_images.count() == 4, 'expected all four Microsoft covers offline'
                answer = page.evaluate("fetch('book-engineering/answers/01-intelligence-answers-fa.md').then(r => r.ok ? r.text() : '')")
                assert 'پاسخ‌نامه فصل ۱' in answer, 'answer key unavailable offline'
                chapter55_offline = page.evaluate("fetch('book-engineering/chapters/55-ai-lab-design.md').then(r => r.ok ? r.text() : '')")
                answer55_offline = page.evaluate("fetch('book-engineering/answers/55-ai-lab-design.md').then(r => r.ok ? r.text() : '')")
                diagram55_offline = page.evaluate("fetch('book-engineering/diagrams/v4-ch09-lab-design.svg').then(r => r.ok ? r.text() : '')")
                chapter56_offline = page.evaluate("fetch('book-engineering/chapters/56-ai-compute-budget.md').then(r => r.ok ? r.text() : '')")
                answer56_offline = page.evaluate("fetch('book-engineering/answers/56-ai-compute-budget-fa.md').then(r => r.ok ? r.text() : '')")
                diagram56_offline = page.evaluate("fetch('assets/images/babak-ai/v4-ch10-tco-timeline.svg').then(r => r.ok ? r.text() : '')")
                chapter57_offline = page.evaluate("fetch('book-engineering/chapters/57-ml-frameworks.md').then(r => r.ok ? r.text() : '')")
                answer57_offline = page.evaluate("fetch('book-engineering/answers/57-ml-frameworks-fa.md').then(r => r.ok ? r.text() : '')")
                diagram57_offline = page.evaluate("fetch('book-engineering/diagrams/v4-ch11-framework-selection.svg').then(r => r.ok ? r.text() : '')")
                chapter58_offline = page.evaluate("fetch('book-engineering/chapters/58-huggingface-stack.md').then(r => r.ok ? r.text() : '')")
                answer58_offline = page.evaluate("fetch('book-engineering/answers/58-huggingface-stack-fa.md').then(r => r.ok ? r.text() : '')")
                diagram58_offline = page.evaluate("fetch('book-engineering/diagrams/v4-ch12-huggingface-stack.svg').then(r => r.ok ? r.text() : '')")
                chapter59_offline = page.evaluate("fetch('book-engineering/chapters/59-gpu-systems.md').then(r => r.ok ? r.text() : '')")
                answer59_offline = page.evaluate("fetch('book-engineering/answers/59-gpu-systems-fa.md').then(r => r.ok ? r.text() : '')")
                diagram59_offline = page.evaluate("fetch('book-engineering/diagrams/v4-ch13-gpu-systems.svg').then(r => r.ok ? r.text() : '')")
                assert 'طراحی آزمایشگاه' in chapter55_offline, 'chapter 55 unavailable offline'
                assert 'پاسخ‌نامهٔ مستقل' in answer55_offline, 'chapter 55 answer key unavailable offline'
                assert '<svg' in diagram55_offline, 'chapter 55 diagram unavailable offline'
                assert 'بودجه و هزینهٔ مالکیت' in chapter56_offline, 'chapter 56 unavailable offline'
                assert 'پاسخ‌نامهٔ مستقل' in answer56_offline, 'chapter 56 answer key unavailable offline'
                assert '<svg' in diagram56_offline, 'chapter 56 diagram unavailable offline'
                assert 'Python' in chapter57_offline and 'PyTorch' in chapter57_offline, 'chapter 57 unavailable offline'
                assert 'پاسخ‌نامهٔ مستقل' in answer57_offline, 'chapter 57 answer key unavailable offline'
                assert '<svg' in diagram57_offline, 'chapter 57 diagram unavailable offline'
                assert 'Transformers' in chapter58_offline and 'Accelerate' in chapter58_offline, 'chapter 58 unavailable offline'
                assert 'پاسخ‌نامهٔ مستقل' in answer58_offline, 'chapter 58 answer key unavailable offline'
                assert '<svg' in diagram58_offline, 'chapter 58 diagram unavailable offline'
                assert 'CUDA' in chapter59_offline and 'Triton' in chapter59_offline, 'chapter 59 unavailable offline'
                assert 'پاسخ‌نامهٔ مستقل' in answer59_offline, 'chapter 59 answer key unavailable offline'
                assert '<svg' in diagram59_offline, 'chapter 59 diagram unavailable offline'
                typography_summary=', '.join(
                    f"{book_id}: {stats['paragraphs']} justified prose paragraphs, {stats['indented']} indented, {stats['formulas']} MathML, {stats['captions']} captions"
                    for book_id,stats in result['typography'].items()
                )
                print(f"PASS {width}px: cover online/offline, chapters 56–59 source/answer/diagram offline, text, header, RTL navigation, locked viewport and {result['count']} sections; {typography_summary}")
                context.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
