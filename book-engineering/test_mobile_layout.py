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
                chapter60 = page.evaluate("""() => {
                  const book=DATA.books.find(item=>item.id==='art-science-intelligence-v4');
                  const chapter=book&&book.chapters[13];
                  const previous=book&&book.chapters[12];
                  return {count:book&&book.chapters.length,id:chapter&&chapter.id,sections:chapter&&chapter.sections.length,previousId:previous&&previous.id,previousSections:previous&&previous.sections.length};
                }""")
                assert chapter60 == {'count':15,'id':'art-science-v4-ch14','sections':24,'previousId':'art-science-v4-ch13','previousSections':22}, chapter60
                chapter61 = page.evaluate("""() => {
                  const book=DATA.books.find(item=>item.id==='art-science-intelligence-v4');
                  const chapter=book&&book.chapters[14];
                  const previous=book&&book.chapters[13];
                  return {count:book&&book.chapters.length,id:chapter&&chapter.id,sections:chapter&&chapter.sections.length,previousId:previous&&previous.id,previousSections:previous&&previous.sections.length};
                }""")
                assert chapter61 == {'count':15,'id':'art-science-v4-ch15','sections':25,'previousId':'art-science-v4-ch14','previousSections':24}, chapter61
                chapter62 = page.evaluate("""() => {
                  const book=DATA.books.find(item=>item.id==='art-science-intelligence-v5');
                  const chapter=book&&book.chapters[0];
                  return {count:book&&book.chapters.length,id:chapter&&chapter.id,sections:chapter&&chapter.sections.length,
                    firstSection:chapter&&chapter.sections[0].id,lastSection:chapter&&chapter.sections.at(-1).id};
                }""")
                assert chapter62 == {'count':8,'id':'art-science-v5-ch01','sections':26,'firstSection':'art-science-v5-ch01-s01','lastSection':'art-science-v5-ch01-s26'}, chapter62
                chapter63 = page.evaluate("""() => {
                  const book=DATA.books.find(item=>item.id==='art-science-intelligence-v5');
                  const chapter=book&&book.chapters[1];
                  return {count:book&&book.chapters.length,id:chapter&&chapter.id,sections:chapter&&chapter.sections.length,
                    firstSection:chapter&&chapter.sections[0].id,lastSection:chapter&&chapter.sections.at(-1).id};
                }""")
                assert chapter63['count'] == 8 and chapter63['id'] == 'art-science-v5-ch02', chapter63
                assert chapter63['sections'] == 34 and chapter63['firstSection'] == 'art-science-v5-ch02-s01', chapter63
                assert chapter63['lastSection'] == 'art-science-v5-ch02-s34', chapter63
                chapter64 = page.evaluate("""() => {
                  const book=DATA.books.find(item=>item.id==='art-science-intelligence-v5');
                  const chapter=book&&book.chapters[2];
                  return {count:book&&book.chapters.length,id:chapter&&chapter.id,sections:chapter&&chapter.sections.length,
                    firstSection:chapter&&chapter.sections[0].id,lastSection:chapter&&chapter.sections.at(-1).id};
                }""")
                assert chapter64 == {'count':8,'id':'art-science-v5-ch03','sections':39,
                  'firstSection':'art-science-v5-ch03-s01','lastSection':'art-science-v5-ch03-s39'}, chapter64
                chapter65 = page.evaluate("""() => {
                  const book=DATA.books.find(item=>item.id==='art-science-intelligence-v5');
                  const chapter=book&&book.chapters[3];
                  return {count:book&&book.chapters.length,id:chapter&&chapter.id,sections:chapter&&chapter.sections.length,
                    firstSection:chapter&&chapter.sections[0].id,lastSection:chapter&&chapter.sections.at(-1).id};
                }""")
                assert chapter65 == {'count':8,'id':'art-science-v5-ch04','sections':41,
                  'firstSection':'art-science-v5-ch04-s01','lastSection':'art-science-v5-ch04-s41'}, chapter65
                chapter66 = page.evaluate("""() => {
                  const book=DATA.books.find(item=>item.id==='art-science-intelligence-v5');
                  const chapter=book&&book.chapters[4];
                  return {count:book&&book.chapters.length,id:chapter&&chapter.id,sections:chapter&&chapter.sections.length,
                    firstSection:chapter&&chapter.sections[0].id,lastSection:chapter&&chapter.sections.at(-1).id};
                }""")
                assert chapter66 == {'count':8,'id':'art-science-v5-ch05','sections':40,
                  'firstSection':'art-science-v5-ch05-s01','lastSection':'art-science-v5-ch05-s40'}, chapter66
                chapter67 = page.evaluate("""() => {
                  const book=DATA.books.find(item=>item.id==='art-science-intelligence-v5');
                  const chapter=book&&book.chapters[5];
                  return {count:book&&book.chapters.length,id:chapter&&chapter.id,sections:chapter&&chapter.sections.length,
                    firstSection:chapter&&chapter.sections[0].id,lastSection:chapter&&chapter.sections.at(-1).id};
                }""")
                assert chapter67 == {'count':8,'id':'art-science-v5-ch06','sections':28,
                  'firstSection':'art-science-v5-ch06-s01','lastSection':'art-science-v5-ch06-s28'}, chapter67
                chapter68 = page.evaluate("""() => {
                  const book=DATA.books.find(item=>item.id==='art-science-intelligence-v5');
                  const chapter=book&&book.chapters[6];
                  return {count:book&&book.chapters.length,id:chapter&&chapter.id,sections:chapter&&chapter.sections.length,
                    firstSection:chapter&&chapter.sections[0].id,lastSection:chapter&&chapter.sections.at(-1).id};
                }""")
                assert chapter68 == {'count':8,'id':'art-science-v5-ch07','sections':37,
                  'firstSection':'art-science-v5-ch07-s01','lastSection':'art-science-v5-ch07-s37'}, chapter68
                chapter69 = page.evaluate("""() => {
                  const book=DATA.books.find(item=>item.id==='art-science-intelligence-v5');
                  const chapter=book&&book.chapters[7];
                  return {count:book&&book.chapters.length,id:chapter&&chapter.id,sections:chapter&&chapter.sections.length,
                    firstSection:chapter&&chapter.sections[0].id,lastSection:chapter&&chapter.sections.at(-1).id};
                }""")
                assert chapter69 == {'count':8,'id':'art-science-v5-ch08','sections':29,
                  'firstSection':'art-science-v5-ch08-s01','lastSection':'art-science-v5-ch08-s29'}, chapter69
                assert page.locator('.home-hero > p').first.inner_text() == 'مجموعه‌ای جامع از کتاب‌ها و دوره‌های آموزشی هوش مصنوعی — با دسترسی آفلاین'
                page.evaluate("document.querySelectorAll('.book-card--volume img,.book-card--microsoft img').forEach(img => img.loading='eager')")
                page.wait_for_function("""() => {
                  const imgs=Array.from(document.querySelectorAll('.book-card--volume img'));
                  const loaded=img=>img.complete && (img.currentSrc.includes('volume-5-cover.png')
                    ? img.naturalWidth===1024 && img.naturalHeight===1536
                    : img.naturalWidth===848 && img.naturalHeight===1264);
                  return imgs.length===5 && imgs.every(loaded);
                }""")
                card = page.locator('.book-card--volume').first
                assert card.locator('.book-card-english').inner_text() == 'The Art & Science of Building Intelligence'
                cover_checks = page.evaluate("""() => {
                  const expected={
                    'art-science-intelligence-v1':{path:'assets/images/covers/volume-1-cover.webp',subtitle:'از صفر مطلق تا طراحی هوش مصنوعی | ۲۱ فصل',dimensions:[848,1264]},
                    'art-science-intelligence-v2':{path:'assets/images/covers/volume-2-cover.webp',subtitle:'یادگیری ماشین و شبکه‌های عصبی | جلد دوم: ۱۱ فصل',dimensions:[848,1264]},
                    'art-science-intelligence-v3':{path:'assets/images/covers/volume-3-cover.webp',subtitle:'Transformer و مهندسی مدل زبانی | ۱۴ فصل',dimensions:[848,1264]},
                    'art-science-intelligence-v4':{path:'assets/images/covers/volume-4-cover.webp',subtitle:'پس‌آموزش، چندوجهی و زیرساخت | ۱۵ فصل',dimensions:[848,1264]},
                    'art-science-intelligence-v5':{path:'assets/images/covers/volume-5-cover.png',subtitle:'ارزیابی، محصول و پژوهش | ۱۲ فصل',dimensions:[1024,1536]}
                  };
                  return Object.entries(expected).map(([id,copy])=>{
                    const path=copy.path;
                    const item=DATA.books.find(book=>book.id===id);
                    const bookCard=Array.from(document.querySelectorAll('.book-card--volume'))
                      .find(el=>el.getAttribute('onclick')===`openItem('${id}','book')`);
                    const img=bookCard&&bookCard.querySelector('img');
                    const cover=bookCard&&bookCard.querySelector('.book-card-cover');
                    const rect=cover&&cover.getBoundingClientRect();
                    return {id,path,expectedSubtitle:copy.subtitle,expectedDimensions:copy.dimensions,subtitle:item&&item.subtitle,author:item&&item.author,
                      cover:item&&item.cover,src:img&&new URL(img.currentSrc).pathname,
                      dimensions:img&&[img.naturalWidth,img.naturalHeight],fit:img&&getComputedStyle(img).objectFit,
                      ratio:rect&&rect.width/rect.height};
                  });
                }""")
                assert len(cover_checks) == 5, cover_checks
                for result_cover in cover_checks:
                    assert result_cover['cover'] == result_cover['path'], result_cover
                    assert result_cover['subtitle'] == result_cover['expectedSubtitle'], result_cover
                    assert result_cover['author'] == 'Babak Moradvand', result_cover
                    assert result_cover['src'].endswith(result_cover['path']), result_cover
                    assert result_cover['dimensions'] == result_cover['expectedDimensions'], result_cover
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
                  const loadedVolumes=volumes.every(img=>img.complete && (img.currentSrc.includes('volume-5-cover.png')
                    ? img.naturalWidth===1024 && img.naturalHeight===1536
                    : img.naturalWidth===848 && img.naturalHeight===1264));
                  const loadedMicrosoft=microsoft.every(img=>img.complete && img.naturalWidth===848 && img.naturalHeight===1264);
                  return volumes.length===5 && microsoft.length===4 && loadedVolumes && loadedMicrosoft;
                }""")
                offline_images = page.locator('.book-card--volume img')
                offline_microsoft_images = page.locator('.book-card--microsoft img')
                assert offline_images.count() == 5, 'expected all five volume covers offline'
                assert offline_microsoft_images.count() == 4, 'expected all four Microsoft covers offline'
                v5_answer_offline = page.evaluate("fetch('book-engineering/answers/62-benchmarking-evaluation-fa.md').then(r => r.ok ? r.text() : '')")
                v5_source_offline = page.evaluate("fetch('book-engineering/chapters/62-benchmarking-evaluation.md').then(r => r.ok ? r.text() : '')")
                v5_diagram_offline = page.evaluate("fetch('book-engineering/diagrams/v5-ch01-evaluation-protocol.svg').then(r => r.ok ? r.text() : '')")
                v5_answer63_offline = page.evaluate("fetch('book-engineering/answers/63-hallucination-bias-robustness-fa.md').then(r => r.ok ? r.text() : '')")
                v5_source63_offline = page.evaluate("fetch('book-engineering/chapters/63-hallucination-bias-robustness.md').then(r => r.ok ? r.text() : '')")
                v5_report63_offline = page.evaluate("fetch('book-engineering/chapters/63-audit-report-fa.md').then(r => r.ok ? r.text() : '')")
                v5_diagram63_offline = page.evaluate("fetch('book-engineering/diagrams/v5-ch02-behavior-audit.svg').then(r => r.ok ? r.text() : '')")
                v5_project63_offline = page.evaluate("fetch('book-engineering/projects/63-model-behavior-lab/results.json').then(r => r.ok ? r.text() : '')")
                v5_answer64_offline = page.evaluate("fetch('book-engineering/answers/64-red-teaming-security-fa.md').then(r => r.ok ? r.text() : '')")
                v5_source64_offline = page.evaluate("fetch('book-engineering/chapters/64-red-teaming-security.md').then(r => r.ok ? r.text() : '')")
                v5_report64_offline = page.evaluate("fetch('book-engineering/chapters/64-audit-report-fa.md').then(r => r.ok ? r.text() : '')")
                v5_diagram64_offline = page.evaluate("fetch('book-engineering/diagrams/v5-ch03-red-team-pipeline.svg').then(r => r.ok ? r.text() : '')")
                v5_project64_offline = page.evaluate("fetch('book-engineering/projects/64-red-team-lab/results.json').then(r => r.ok ? r.text() : '')")
                v5_fixture64_offline = page.evaluate("fetch('book-engineering/projects/64-red-team-lab/synthetic_security_fixture.json').then(r => r.ok ? r.text() : '')")
                v5_answer65_offline = page.evaluate("fetch('book-engineering/answers/65-alignment-governance-fa.md').then(r => r.ok ? r.text() : '')")
                v5_source65_offline = page.evaluate("fetch('book-engineering/chapters/65-alignment-governance.md').then(r => r.ok ? r.text() : '')")
                v5_report65_offline = page.evaluate("fetch('book-engineering/chapters/65-audit-report-fa.md').then(r => r.ok ? r.text() : '')")
                v5_diagram65_offline = page.evaluate("fetch('book-engineering/diagrams/v5-ch04-governance-cycle.svg').then(r => r.ok ? r.text() : '')")
                v5_project65_offline = page.evaluate("fetch('book-engineering/projects/65-governance-lab/results.json').then(r => r.ok ? r.text() : '')")
                v5_answer66_offline = page.evaluate("fetch('book-engineering/answers/66-ai-product-api-fa.md').then(r => r.ok ? r.text() : '')")
                v5_source66_offline = page.evaluate("fetch('book-engineering/chapters/66-ai-product-api.md').then(r => r.ok ? r.text() : '')")
                v5_report66_offline = page.evaluate("fetch('book-engineering/chapters/66-audit-report-fa.md').then(r => r.ok ? r.text() : '')")
                v5_diagram66_offline = page.evaluate("fetch('book-engineering/diagrams/v5-ch05-api-contract.svg').then(r => r.ok ? r.text() : '')")
                v5_project66_offline = page.evaluate("fetch('book-engineering/projects/66-ai-product-api/results.json').then(r => r.ok ? r.text() : '')")
                v5_fixture66_offline = page.evaluate("fetch('book-engineering/projects/66-ai-product-api/synthetic_fixture.json').then(r => r.ok ? r.text() : '')")
                v5_answer67_offline = page.evaluate("fetch('book-engineering/answers/67-model-serving-operations-fa.md').then(r => r.ok ? r.text() : '')")
                v5_source67_offline = page.evaluate("fetch('book-engineering/chapters/67-model-serving-operations.md').then(r => r.ok ? r.text() : '')")
                v5_report67_offline = page.evaluate("fetch('book-engineering/chapters/67-audit-report-fa.md').then(r => r.ok ? r.text() : '')")
                v5_diagram67_offline = page.evaluate("fetch('book-engineering/diagrams/v5-ch06-serving-pipeline.svg').then(r => r.ok ? r.text() : '')")
                v5_project67_offline = page.evaluate("fetch('book-engineering/projects/67-serving-lab/results.json').then(r => r.ok ? r.text() : '')")
                v5_fixture67_offline = page.evaluate("fetch('book-engineering/projects/67-serving-lab/synthetic_serving_trace.json').then(r => r.ok ? r.text() : '')")
                v5_answer68_offline = page.evaluate("fetch('book-engineering/answers/68-product-security-monitoring-fa.md').then(r => r.ok ? r.text() : '')")
                v5_source68_offline = page.evaluate("fetch('book-engineering/chapters/68-product-security-monitoring.md').then(r => r.ok ? r.text() : '')")
                v5_report68_offline = page.evaluate("fetch('book-engineering/chapters/68-audit-report-fa.md').then(r => r.ok ? r.text() : '')")
                v5_diagram68_offline = page.evaluate("fetch('book-engineering/diagrams/v5-ch07-product-security-flow.svg').then(r => r.ok ? r.text() : '')")
                v5_project68_offline = page.evaluate("fetch('book-engineering/projects/68-product-security-lab/results.json').then(r => r.ok ? r.text() : '')")
                v5_fixture68_offline = page.evaluate("fetch('book-engineering/projects/68-product-security-lab/synthetic_security_events.json').then(r => r.ok ? r.text() : '')")
                v5_environment68_offline = page.evaluate("fetch('book-engineering/projects/68-product-security-lab/environment.json').then(r => r.ok ? r.text() : '')")
                v5_answer69_offline = page.evaluate("fetch('book-engineering/answers/69-deployment-cicd-fa.md').then(r => r.ok ? r.text() : '')")
                v5_source69_offline = page.evaluate("fetch('book-engineering/chapters/69-deployment-cicd.md').then(r => r.ok ? r.text() : '')")
                v5_report69_offline = page.evaluate("fetch('book-engineering/chapters/69-audit-report-fa.md').then(r => r.ok ? r.text() : '')")
                v5_diagram69_offline = page.evaluate("fetch('book-engineering/diagrams/v5-ch08-release-pipeline.svg').then(r => r.ok ? r.text() : '')")
                v5_project69_offline = page.evaluate("fetch('book-engineering/projects/69-deployment-cicd-lab/results.json').then(r => r.ok ? r.text() : '')")
                v5_fixture69_offline = page.evaluate("fetch('book-engineering/projects/69-deployment-cicd-lab/synthetic_release_scenarios.json').then(r => r.ok ? r.text() : '')")
                v5_environment69_offline = page.evaluate("fetch('book-engineering/projects/69-deployment-cicd-lab/environment.json').then(r => r.ok ? r.text() : '')")
                v5_markdown_offline = page.evaluate("fetch('volume-5-full-fa.md').then(r => r.ok ? r.text() : '')")
                v5_cover_dimensions_offline = page.evaluate("""async () => {
                  const response=await fetch('assets/images/covers/volume-5-cover.png');
                  if(!response.ok)return null;
                  const bitmap=await createImageBitmap(await response.blob());
                  const result={width:bitmap.width,height:bitmap.height};bitmap.close();return result;
                }""")
                assert v5_cover_dimensions_offline == {'width':1024,'height':1536}, v5_cover_dimensions_offline
                assert 'پاسخ‌نامهٔ مستقل فصل ۶۲' in v5_answer_offline
                assert 'فصل سراسری ۶۲' in v5_source_offline and 'زنجیره' in v5_diagram_offline
                assert 'پاسخ‌نامهٔ مستقل فصل ۶۳' in v5_answer63_offline
                assert 'فصل سراسری ۶۳' in v5_source63_offline and 'فصل سراسری ۶۳' in v5_report63_offline
                assert 'ممیزی چندمحوره' in v5_diagram63_offline and 'synthetic' in v5_project63_offline
                assert 'پاسخ‌نامهٔ مستقل فصل ۶۴' in v5_answer64_offline
                assert 'فصل محلی ۳ جلد پنجم = فصل سراسری ۶۴' in v5_source64_offline
                assert 'فصل سراسری ۶۴' in v5_report64_offline
                assert 'فرایند آزمون خصمانه' in v5_diagram64_offline
                assert 'synthetic' in v5_project64_offline and 'v5-ch03-red-team-synthetic-v1' in v5_fixture64_offline
                assert 'پاسخ‌نامهٔ مستقل فصل ۶۵' in v5_answer65_offline
                assert 'فصل محلی ۴ جلد پنجم = فصل سراسری ۶۵' in v5_source65_offline
                assert 'فصل سراسری ۶۵' in v5_report65_offline and 'حکمرانی' in v5_diagram65_offline
                assert 'v5-ch04-governance-pack-synthetic-v1' in v5_project65_offline
                assert 'پاسخ‌نامهٔ مستقل فصل ۶۶' in v5_answer66_offline
                assert 'فصل محلی ۵ جلد پنجم = فصل سراسری ۶۶' in v5_source66_offline
                assert 'فصل سراسری ۶۶' in v5_report66_offline
                assert 'قرارداد مشترک API' in v5_diagram66_offline
                assert 'api_cases_passed' in v5_project66_offline and 'v5-ch05-api-contract-synthetic-v1' in v5_fixture66_offline
                assert 'پاسخ‌نامهٔ مستقل فصل ۶۷' in v5_answer67_offline
                assert 'فصل محلی ۶ جلد پنجم = فصل سراسری ۶۷' in v5_source67_offline
                assert 'فصل سراسری ۶۷' in v5_report67_offline
                assert 'سرو در سطح محصول' in v5_diagram67_offline
                assert 'v5-ch06-serving-synthetic-v1' in v5_fixture67_offline
                assert 'response_cache_hits' in v5_project67_offline
                assert 'پاسخ‌نامهٔ مستقل فصل ۶۸' in v5_answer68_offline
                assert 'فصل محلی ۷ جلد پنجم = فصل سراسری ۶۸' in v5_source68_offline
                assert 'فصل سراسری ۶۸' in v5_report68_offline
                assert 'prompt / token / PII' in v5_diagram68_offline
                assert 'AUTH_FAILURE_BURST' in v5_project68_offline and '"allowed": 6' in v5_project68_offline
                assert '"audit_date": "2026-11-08"' in v5_environment68_offline
                assert 'v5-ch07-security-ops-synthetic-v1' in v5_fixture68_offline
                assert 'پاسخ‌نامهٔ مستقل فصل ۶۹' in v5_answer69_offline
                assert 'فصل محلی ۸ جلد پنجم = فصل سراسری ۶۹' in v5_source69_offline
                assert 'فصل سراسری ۶۹' in v5_report69_offline
                assert 'digest پایدارِ پیشین' in v5_diagram69_offline and 'پیکان خط‌چین' in v5_diagram69_offline
                assert '"rolled_back": 1' in v5_project69_offline and '"decision": "blocked"' in v5_project69_offline
                assert 'v5-ch08-deployment-cicd-synthetic-v1' in v5_fixture69_offline
                assert '"audit_date": "2026-11-04"' in v5_environment69_offline
                assert all(term in v5_markdown_offline for term in ('جلد پنجم', 'فصل ۶۲', 'فصل ۶۳', 'فصل ۶۴', 'فصل ۶۵', 'فصل ۶۶', 'فصل ۶۷', 'فصل ۶۸', 'فصل ۶۹'))
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
                chapter60_offline = page.evaluate("fetch('book-engineering/chapters/60-mlops.md').then(r => r.ok ? r.text() : '')")
                answer60_offline = page.evaluate("fetch('book-engineering/answers/60-mlops-fa.md').then(r => r.ok ? r.text() : '')")
                diagram60_offline = page.evaluate("fetch('book-engineering/diagrams/v4-ch14-mlops.svg').then(r => r.ok ? r.text() : '')")
                chapter61_offline = page.evaluate("fetch('book-engineering/chapters/61-inference-serving.md').then(r => r.ok ? r.text() : '')")
                answer61_offline = page.evaluate("fetch('book-engineering/answers/61-inference-serving-fa.md').then(r => r.ok ? r.text() : '')")
                diagram61_offline = page.evaluate("fetch('book-engineering/diagrams/v4-ch15-inference-serving.svg').then(r => r.ok ? r.text() : '')")
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
                assert 'MLflow' in chapter60_offline and 'W&B' in chapter60_offline, 'chapter 60 unavailable offline'
                assert 'پاسخ‌نامهٔ مستقل' in answer60_offline, 'chapter 60 answer key unavailable offline'
                assert '<svg' in diagram60_offline, 'chapter 60 diagram unavailable offline'
                assert all(term in chapter61_offline for term in ('vLLM', 'llama.cpp', 'Ollama', 'TensorRT-LLM')), 'chapter 61 unavailable offline'
                assert 'پاسخ‌نامهٔ مستقل' in answer61_offline, 'chapter 61 answer key unavailable offline'
                assert '<svg' in diagram61_offline, 'chapter 61 diagram unavailable offline'
                typography_summary=', '.join(
                    f"{book_id}: {stats['paragraphs']} justified prose paragraphs, {stats['indented']} indented, {stats['formulas']} MathML, {stats['captions']} captions"
                    for book_id,stats in result['typography'].items()
                )
                print(f"PASS {width}px: covers online/offline, chapters 55–69 source/answer/diagram offline, text, header, RTL navigation, locked viewport and {result['count']} sections; {typography_summary}")
                context.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
