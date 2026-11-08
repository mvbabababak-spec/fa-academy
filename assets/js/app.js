const App={data:null,courses:null,state:{currentBook:null,currentSection:null,readingProgress:0},
init(){
if(!window.BOOK_DATA){document.getElementById('app').innerHTML='<div class="loading">خطای بارگذاری...</div>';return}
this.data=window.BOOK_DATA;
this.courses=window.COURSES_DATA?window.COURSES_DATA.books:[];
this.loadState();this.applyTheme();this.applyReaderStyles();this.bindEvents();this.renderHome();this.renderCourses();this.renderSettings();this.renderBookmarks();this.renderNotes();this.initSearch();this.handleHash();
window.addEventListener('hashchange',()=>this.handleHash());
window.addEventListener('beforeunload',()=>this.saveReadingPosition());
if('serviceWorker'in navigator)navigator.serviceWorker.register('sw.js').catch(()=>{})
},
loadState(){
var d={completed:{},bookmarks:[],notes:{},settings:{theme:'light',fontSize:16,lineHeight:1.8,contentWidth:680},lastRead:{bookId:null,sectionId:null,scroll:0}};
var s=JSON.parse(localStorage.getItem('fa_academy_state')||'null');
this.state=s?Object.assign(d,s):d;
if(!this.state.settings)this.state.settings=d.settings;
if(!this.state.completed)this.state.completed={};
if(!this.state.lastRead)this.state.lastRead=d.lastRead;
},
saveState(){localStorage.setItem('fa_academy_state',JSON.stringify(this.state))},
applyTheme(){document.documentElement.setAttribute('data-theme',this.state.settings.theme);var m=document.querySelector('meta[name="theme-color"]');if(m)m.content=this.state.settings.theme==='dark'?'#0a0a0a':'#fafaf9'},
toggleTheme(){this.state.settings.theme=this.state.settings.theme==='light'?'dark':'light';this.applyTheme();this.saveState();this.renderSettings()},
applyReaderStyles(){var r=document.documentElement;r.style.setProperty('--reader-font-size',this.state.settings.fontSize+'px');r.style.setProperty('--reader-line-height',this.state.settings.lineHeight);r.style.setProperty('--reading-width',this.state.settings.contentWidth+'px')},
bindEvents(){window.addEventListener('scroll',()=>this.updateReadingProgress(),{passive:true});var back=document.getElementById('header-back');if(back)back.addEventListener('click',()=>this.goBack())},
handleHash(){var h=window.location.hash.slice(1);if(h.startsWith('read/'))this.openSection(h.slice(5));else this.goHome()},
showScreen(name){document.querySelectorAll('.screen').forEach(function(s){s.classList.remove('active')});var sc=document.getElementById('screen-'+name);if(sc)sc.classList.add('active');document.querySelectorAll('.nav-item').forEach(function(n){n.classList.remove('active')});var n=document.querySelector('.nav-item[data-screen="'+name+'"]');if(n)n.classList.add('active');window.scrollTo(0,0);var tp=document.getElementById('top-progress');if(tp)tp.style.display='none'},
goHome(){window.location.hash='';this.showScreen('home');this.renderHome();this.renderCourses();document.getElementById('header-title').textContent='آکادمی هوش مصنوعی';document.getElementById('header-back').style.display='none'},
goBack(){if(this.state.currentBook){this.showScreen('home');this.renderHome();this.renderCourses();this.state.currentBook=null;this.state.currentSection=null;document.getElementById('header-title').textContent='آکادمی هوش مصنوعی';document.getElementById('header-back').style.display='none'}else this.showScreen('home')},
renderHome(){
var books=this.data.books;
var totalChapters=books.reduce(function(s,b){return s+b.chapters.length},0);
var totalSections=books.reduce(function(s,b){return s+b.chapters.reduce(function(s2,c){return s2+c.sections.length},0)},0);
var totalDone=Object.keys(this.state.completed).filter(function(k){return this.state.completed[k]},this).length;
var self=this;
var pct=Math.round((totalDone/totalSections)*100);
document.getElementById('home-stats').innerHTML='<div class="home-stat"><div class="home-stat-num">'+books.length+'</div><div class="home-stat-label">کتاب</div></div><div class="home-stat"><div class="home-stat-num">'+(this.courses?this.courses.length:0)+'</div><div class="home-stat-label">دوره</div></div><div class="home-stat"><div class="home-stat-num">'+totalChapters+'</div><div class="home-stat-label">جلد</div></div><div class="home-stat"><div class="home-stat-num">'+pct+'٪</div><div class="home-stat-label">پروش</div></div>';
var icons={'vol1':'🧠','vol2':'📈','vol3':'🔄','vol4':'⚡','vol5':'🎯','ai':'🧠','genai':'🤖','ml':'📊','datascience':'📈'};
var grid=document.getElementById('home-books');
grid.innerHTML=books.map(function(b,i){
var total=b.chapters.reduce(function(s,c){return s+c.sections.length},0);
var done=0;
b.chapters.forEach(function(ch){ch.sections.forEach(function(s){if(self.state.completed[s.id])done++})});
var cp=total>0?Math.round((done/total)*100):0;
var rd=2*Math.PI*16;var ro=rd*(1-cp/100);
var icon=icons[b.id]||'📄';
return '<div class="book-card" style="animation-delay:'+(i*0.1)+'s" onclick="App.openBook(\''+b.id+'\')"><div class="book-cover"><div class="book-cover-bg"></div><div class="book-cover-content"><div class="book-cover-icon">'+icon+'</div><div class="book-cover-title">'+b.title+'</div><div class="book-cover-subtitle">'+b.subtitle+'</div></div></div><div class="book-info"><div class="book-title">'+b.title+'</div><div class="book-meta"><span class="book-chapter-count">'+b.chapters.length+' جلد • '+total+' بخش</span><div class="book-progress-ring"><svg width="44" height="44"><circle cx="22" cy="22" r="16" fill="none" stroke="var(--bg2)" stroke-width="4"/><circle cx="22" cy="22" r="16" fill="none" stroke="var(--primary)" stroke-width="4" stroke-dasharray="'+rd+'" stroke-dashoffset="'+ro+'" stroke-linecap="round" style="transition:stroke-dashoffset .5s"/></svg><div class="pt">'+cp+'٪</div></div></div></div></div>';
}).join('');
},
renderCourses(){
var courses=this.courses;
if(!courses||courses.length===0)return;
var grid=document.getElementById('courses-grid');
if(!grid)return;
var icons={'dlai':'🎓','nvidia':'⚡','hf':'🤗','openai':'🟢'};
var levelLabels={'beginner':'مبتدی','intermediate':'متوسط','advanced':'پیشرفته'};
var self=this;
grid.innerHTML=courses.map(function(c,i){
var total=c.chapters.reduce(function(s,ch){return s+ch.sections.length},0);
var icon=icons[c.id.split('-')[0]]||'📚';
var level=c.level||'beginner';
var levelLabel=levelLabels[level]||level;
return '<div class="book-card" style="animation-delay:'+(i*0.05)+'s" onclick="App.openCourse(\''+c.id+'\')"><div class="book-cover"><div class="book-cover-bg"></div><div class="book-cover-content"><div class="book-cover-icon">'+icon+'</div><div class="book-cover-title">'+c.title+'</div><div class="book-cover-subtitle">'+levelLabel+' • '+total+' بخش</div></div></div><div class="book-info"><div class="book-title">'+c.title+'</div><div class="book-meta"><span class="book-chapter-count">'+c.chapters.length+' جلد • '+total+' بخش</span><span style="font-size:var(--fs-xs);padding:.2rem .5rem;border-radius:9999px;background:var(--bg2);color:var(--text2)">'+levelLabel+'</span></div></div></div>';
}).join('');
},
openBook(id){var book=this.data.books.find(function(b){return b.id===id});if(!book)return;this.state.currentBook=book;document.getElementById('header-title').textContent=book.title;document.getElementById('header-back').style.display='flex';this.showScreen('book');this.renderBook(book)},
openCourse(id){var course=this.courses.find(function(c){return c.id===id});if(!course)return;this.state.currentBook=course;document.getElementById('header-title').textContent=course.title;document.getElementById('header-back').style.display='flex';this.showScreen('book');this.renderBook(course)},
renderBook(book){
var icons={'ai':'🧠','genai':'🤖','ml':'📊','datascience':'📈','dlai':'🎓','nvidia':'⚡','hf':'🤗','openai':'🟢'};
var icon=icons[book.id.split('-')[0]]||'📄';
var h=document.getElementById('book-header');
h.innerHTML='<div class="book-header-icon">'+icon+'</div><div class="book-header-title">'+book.title+'</div><div class="book-header-subtitle">'+book.subtitle+'</div>';
var c=document.getElementById('book-content');
var self=this;
c.innerHTML=book.chapters.map(function(ch){
var cs=ch.sections;
var cd=cs.filter(function(s){return self.state.completed[s.id]}).length;
var cp=cs.length>0?Math.round((cd/cs.length)*100):0;
var rd=2*Math.PI*14;var ro=rd*(1-cp/100);
var isLast=self.state.lastRead&&self.state.lastRead.bookId===book.id&&cs.some(function(s){return s.id===self.state.lastRead.sectionId});
return '<div class="chapter-card '+(isLast?'expanded':'')+'" onclick="App.toggleChapter(this)"><div class="chapter-card-header"><div class="chapter-icon">'+ch.icon+'</div><div class="chapter-info"><div class="chapter-title">'+ch.title+'</div><div class="chapter-meta"><span>'+cs.length+' بخش</span><span>•</span><span>'+cd+' خوانده‌شده</span></div></div><div class="chapter-progress-ring"><svg width="36" height="36"><circle cx="18" cy="18" r="14" fill="none" stroke="var(--bg2)" stroke-width="4"/><circle cx="18" cy="18" r="14" fill="none" stroke="var(--primary)" stroke-width="4" stroke-dasharray="'+rd+'" stroke-dashoffset="'+ro+'" stroke-linecap="round" style="transition:stroke-dashoffset .5s"/></svg><div class="pt">'+cp+'٪</div></div><div class="chapter-chevron"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg></div></div><div class="chapter-sections">'+cs.map(function(s){var isDone=self.state.completed[s.id];var isCur=self.state.lastRead&&self.state.lastRead.bookId===book.id&&s.id===self.state.lastRead.sectionId;return '<div class="section-item '+(isDone?'completed':'')+(isCur?' current':'')+'" onclick="event.stopPropagation();App.openSection(\''+s.id+'\')"><div class="check">'+(isDone?'✓':'')+'</div><span>'+s.title+'</span>'+(isCur?'<span style="font-size:.7rem;color:var(--primary)"> ادامه...</span>':'')+'</div>'}).join('')+'</div></div>';
}).join('');
},
toggleChapter(el){el.classList.toggle('expanded')},
findSection(id){
for(var i=0;i<this.data.books.length;i++){var b=this.data.books[i];for(var j=0;j<b.chapters.length;j++){var ch=b.chapters[j];for(var k=0;k<ch.sections.length;k++){if(ch.sections[k].id===id)return{section:ch.sections[k],chapter:ch,book:b}}}}
if(this.courses){for(var i2=0;i2<this.courses.length;i2++){var b2=this.courses[i2];for(var j2=0;j2<b2.chapters.length;j2++){var ch2=b2.chapters[j2];for(var k2=0;k2<ch2.sections.length;k2++){if(ch2.sections[k2].id===id)return{section:ch2.sections[k2],chapter:ch2,book:b2}}}}
return null;
},
getAllSections(bookId){
var all=[];
var sources=this.data.books.concat(this.courses||[]);
sources.forEach(function(b){b.chapters.forEach(function(ch){ch.sections.forEach(function(s){all.push({section:s,chapter:ch,book:b})})})});
return all;
},
openSection(id){
var f=this.findSection(id);if(!f){this.goHome();return}
this.state.currentSection=f.section;this.state.currentBook=f.book;
var h=document.getElementById('reader-header');
h.innerHTML='<div class="reader-chapter">'+f.chapter.icon+' '+f.chapter.title+'</div><div class="reader-title">'+f.section.title+'</div>';
document.getElementById('reader-content').innerHTML=f.section.html;
var all=this.getAllSections(f.book.id);
var idx=all.findIndex(function(s){return s.section.id===id});
var prev=idx>0?all[idx-1]:null;var next=idx<all.length-1?all[idx+1]:null;
var rp=document.getElementById('reader-prev');var rn=document.getElementById('reader-next');
rp.disabled=!prev;rn.disabled=!next;
if(prev){rp.onclick=function(){App.openSection(prev.section.id)}};
if(next){rn.onclick=function(){App.openSection(next.section.id)}};
this.showScreen('reader');
document.getElementById('top-progress').style.display='block';
document.getElementById('header-title').textContent=f.book.title;
document.getElementById('header-back').style.display='flex';
if(this.state.lastRead&&this.state.lastRead.sectionId===id&&this.state.lastRead.scroll>0){setTimeout(function(){window.scrollTo(0,App.state.lastRead.scroll);App.updateReadingProgress()},100)}else{window.scrollTo(0,0);this.updateReadingProgress()}
this.state.lastRead={bookId:f.book.id,sectionId:id,scroll:0};this.saveState();
},
updateReadingProgress(){if(!this.state.currentSection)return;var scrollable=document.documentElement.scrollHeight-window.innerHeight;var scrolled=Math.min(Math.max(-document.getElementById('reader-body').getBoundingClientRect().top,0),scrollable);var pct=scrollable>0?Math.min(100,Math.round((scrolled/scrollable)*100)):0;this.state.readingProgress=pct;var fp=document.querySelector('.top-progress-bar');if(fp)fp.style.width=pct+'%';this.state.lastRead.scroll=window.scrollY;if(pct>=85&&!this.state.completed[this.state.currentSection.id]){this.state.completed[this.state.currentSection.id]=true;this.saveState();this.showCompletionToast();this.renderBook(this.state.currentBook);this.renderHome();this.renderCourses();this.renderProgress()}},
saveReadingPosition(){if(this.state.currentSection){this.state.lastRead.scroll=window.scrollY;this.saveState()}},
showCompletionToast(){var t=document.createElement('div');t.style.cssText='position:fixed;top:60px;left:50%;transform:translateX(-50%);background:var(--success);color:#fff;padding:.75rem 1.5rem;border-radius:9999px;font-weight:600;z-index:2000;box-shadow:0 4px 15px rgba(0,0,0,.15);animation:toastIn .3s';t.textContent='✅ بخش کامل شد!';document.body.appendChild(t);setTimeout(function(){t.style.opacity='0';t.style.transition='opacity .3s'},2000);setTimeout(function(){t.remove()},2500)},
prevSection(){var all=this.getAllSections(this.state.currentBook.id);var idx=all.findIndex(function(s){return s.section.id===this.state.currentSection.id},this);if(idx>0)this.openSection(all[idx-1].section.id)},
nextSection(){var all=this.getAllSections(this.state.currentBook.id);var idx=all.findIndex(function(s){return s.section.id===this.state.currentSection.id},this);if(idx<all.length-1)this.openSection(all[idx+1].section.id);else this.showToast('آخرین بخش تمام شد! 🎉')},
renderBookmarks(){var c=document.getElementById('bookmarks-list');if(this.state.bookmarks.length===0){c.innerHTML='<div class="empty-state"><div class="empty-state-icon">🔖</div>هنوز علامت‌گذاری‌ای ندارد</div>';return}var self=this;c.innerHTML=this.state.bookmarks.map(function(b){var f=self.findSection(b.sectionId);if(!f)return'';var note=self.state.notes[b.sectionId]||'';return '<div class="bookmark-item" onclick="App.openSection(\''+b.sectionId+'\')"><div class="bookmark-chapter">'+f.chapter.icon+' '+f.chapter.title+'</div><div class="bookmark-title">'+f.section.title+'</div>'+(note?'<div class="bookmark-note">'+note+'</div>':'')+'<div class="bookmark-actions"><button class="bookmark-btn" onclick="event.stopPropagation();App.addNote(\''+b.sectionId+'\')">✏️ یادداشت</button><button class="bookmark-btn" onclick="event.stopPropagation();App.openSection(\''+b.sectionId+'\')">📖 خواندن</button><button class="bookmark-btn danger" onclick="event.stopPropagation();App.deleteBookmark(\''+b.sectionId+'\')">حذف</button></div></div>'}).join('')},
deleteBookmark(id){this.state.bookmarks=this.state.bookmarks.filter(function(b){return b.sectionId!==id});this.saveState();this.renderBookmarks()},
addNote(id){var n=prompt('یادداشت خود را بنویسید:');if(n!==null){this.state.notes[id]=n;this.saveState();this.renderBookmarks();this.renderNotes();this.showToast('یادداشت ذخیره شد')}},
renderNotes(){var c=document.getElementById('notes-list');var keys=Object.keys(this.state.notes).filter(function(k){return this.state.notes[k]},this);if(keys.length===0){c.innerHTML='<div class="empty-state"><div class="empty-state-icon">📝</div>هنوز یادداشت‌ی ذخیره نشده</div>';return}var self=this;c.innerHTML=keys.map(function(k){var f=self.findSection(k);if(!f)return'';return '<div class="bookmark-item"><div class="bookmark-chapter">'+f.chapter.icon+' '+f.chapter.title+'</div><div class="bookmark-title">'+f.section.title+'</div><div class="bookmark-note">'+self.state.notes[k]+'</div><div class="bookmark-actions"><button class="bookmark-btn" onclick="App.openSection(\''+k+'\')">📖 خواندن</button><button class="bookmark-btn danger" onclick="App.deleteNote(\''+k+'\')">حذف</button></div></div>'}).join('')},
deleteNote(id){delete this.state.notes[id];this.saveState();this.renderNotes();this.renderBookmarks()},
initSearch(){var input=document.getElementById('search-input');if(!input)return;input.addEventListener('input',function(e){var q=e.target.value;var res=App.search(q);var c=document.getElementById('search-results');if(q.length<2){c.innerHTML='';return}if(res.length===0){c.innerHTML='<div class="search-empty">هیچ نتیجه‌ی یافت نشد</div>';return}c.innerHTML=res.map(function(r){return '<div class="search-result" onclick="App.openSection(\''+r.section.id+'\')"><div class="search-result-title">'+r.section.chapter.icon+' '+r.section.title+'</div><div class="search-result-snippet">'+r.snippet+'</div></div>'}).join('')})},
search(query){var res=[];var q=query.toLowerCase().trim();if(q.length<2)return[];var all=this.getAllSections();for(var i=0;i<all.length;i++){var s=all[i].section;if(s.title.toLowerCase().includes(q)){res.push({section:s,snippet:s.title});continue}var text=s.html.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();if(text.toLowerCase().includes(q)){var idx=text.toLowerCase().indexOf(q);var st=Math.max(0,idx-40);res.push({section:s,snippet:'...'+text.substring(st,idx+q.length+60).trim()+'...'})}}return res},
renderProgress(){var all=this.getAllSections();var total=all.length;var done=0;all.forEach(function(s){if(App.state.completed[s.section.id])done++});var pct=Math.round((done/total)*100);var rd=2*Math.PI*50;var ro=rd*(1-pct/100);var c=document.getElementById('progress-content');var self=this;var icons={'ai':'🧠','genai':'🤖','ml':'📊','datascience':'📈','dlai':'🎓','nvidia':'⚡','hf':'🤗','openai':'🟢'};var html='<div class="progress-overview"><div class="progress-overview-ring"><svg width="120" height="120"><circle cx="60" cy="60" r="50" fill="none" stroke="var(--bg2)" stroke-width="10"/><circle cx="60" cy="60" r="50" fill="none" stroke="var(--primary)" stroke-width="10" stroke-dasharray="'+rd+'" stroke-dashoffset="'+ro+'" stroke-linecap="round" style="transition:stroke-dashoffset .5s"/></svg><div class="pn">'+pct+'٪</div></div><div class="progress-overview-label">'+done+' از '+total+' بخش خوانده‌شده</div></div>';
this.data.books.concat(this.courses||[]).forEach(function(b){
html+='<div style="font-size:var(--fs-sm);font-weight:700;color:var(--text2);margin:1.5rem 0 .75rem;padding-top:1rem;border-top:1px solid var(--border)">'+(icons[b.id.split('-')[0]]||'📄')+' '+b.title+'</div>';
b.chapters.forEach(function(ch){var cs=ch.sections;var cd=cs.filter(function(s){return self.state.completed[s.id]}).length;var cp=cs.length>0?Math.round((cd/cs.length)*100):0;html+='<div class="progress-chapter" onclick="App.openSection(\''+cs[0].id+'\')"><div class="progress-chapter-header"><span style="font-size:1.25rem">'+ch.icon+'</span><span class="progress-chapter-title">'+ch.title+'</span><span style="font-size:var(--fs-sm);color:var(--text2)">'+cd+'/'+cs.length+'</span></div><div class="progress-bar"><div class="progress-bar-fill" style="width:'+cp+'%"></div></div></div>'})});
c.innerHTML=html;
},
renderSettings(){var s=this.state.settings;document.getElementById('settings-content').innerHTML='<div class="setting-group"><div class="setting-group-title">نمایش</div><div class="setting-item"><span class="setting-label">حالت تاریک</span><div class="toggle '+(s.theme==='dark'?'active':'')+'" onclick="App.toggleTheme()"></div></div></div><div class="setting-group"><div class="setting-group-title">قلم</div><div class="setting-item"><span class="setting-label">سایز قلم</span><div class="range-wrapper"><input type="range" min="14" max="22" value="'+s.fontSize+'" onchange="App.setFontSize(this.value)"><span class="range-value">'+s.fontSize+'px</span></div></div><div class="setting-item"><span class="setting-label">فاصله ردیف</span><div class="range-wrapper"><input type="range" min="1.4" max="2.2" step=".1" value="'+s.lineHeight+'" onchange="App.setLineHeight(this.value)"><span class="range-value">'+s.lineHeight+'</span></div></div><div class="setting-item"><span class="setting-label">عرض خواندن</span><div class="range-wrapper"><input type="range" min="500" max="900" step="20" value="'+s.contentWidth+'" onchange="App.setContentWidth(this.value)"><span class="range-value">'+s.contentWidth+'px</span></div></div></div><div class="setting-group"><div class="setting-group-title">درباره</div><div class="setting-item"><span class="setting-label">کتاب</span><span style="color:var(--text2);font-size:var(--fs-sm)">'+this.data.books.length+'</span></div><div class="setting-item"><span class="setting-label">دوره</span><span style="color:var(--text2);font-size:var(--fs-sm)">'+(this.courses?this.courses.length:0)+'</span></div><div class="setting-item"><span class="setting-label">جلد</span><span style="color:var(--text2);font-size:var(--fs-sm)">'+this.data.books.concat(this.courses||[]).reduce(function(a,b){return a+b.chapters.length},0)+'</span></div><div class="setting-item"><span class="setting-label">بخش</span><span style="color:var(--text2);font-size:var(--fs-sm)">'+this.data.books.concat(this.courses||[]).reduce(function(a,b){return a+b.chapters.reduce(function(s,c){return s+c.sections.length},0)},0)+'</span></div></div><button class="setting-item" style="width:100%;justify-content:center;color:var(--danger);font-weight:600;cursor:pointer;border:none;background:none;border-radius:var(--radius)" onclick="App.resetProgress()">ریست پیشرفت خواندن</button>'},
setFontSize(v){this.state.settings.fontSize=parseInt(v);this.applyReaderStyles();this.saveState()},
setLineHeight(v){this.state.settings.lineHeight=parseFloat(v);this.applyReaderStyles();this.saveState()},
setContentWidth(v){this.state.settings.contentWidth=parseInt(v);this.applyReaderStyles();this.saveState()},
resetProgress(){if(confirm('پرورش خواندن و علامت‌گذاری‌ها حذف شود؟')){this.state.completed={};this.state.bookmarks=[];this.state.notes={};this.state.lastRead={bookId:null,sectionId:null,scroll:0};this.saveState();this.renderHome();this.renderCourses();this.renderBookmarks();this.renderNotes();this.renderProgress();this.showToast('پرورشريست شد')}},
showToast(msg){var t=document.createElement('div');t.style.cssText='position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:var(--text);color:var(--bg);padding:.65rem 1.25rem;border-radius:9999px;font-weight:600;z-index:2000;box-shadow:0 4px 15px rgba(0,0,0,.15);font-size:var(--fs-sm);animation:toastIn .2s';t.textContent=msg;document.body.appendChild(t);setTimeout(function(){t.style.opacity='0';t.style.transition='opacity .3s'},2000);setTimeout(function(){t.remove()},2500)}
};
document.addEventListener('DOMContentLoaded',function(){App.init()});
