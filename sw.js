const CACHE_NAME='fa-academy-v1';
const ASSETS=['./','./index.html','./manifest.json','./assets/css/style.css','./assets/js/app.js','./assets/js/book-data.js'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE_NAME).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE_NAME).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(r=>{if(e.request.url.includes('github.io')&&r.status===200){const clone=r.clone();caches.open(CACHE_NAME).then(c=>c.put(e.request,clone)).catch(()=>{})}return r})).catch(()=>caches.match('./index.html')))});
