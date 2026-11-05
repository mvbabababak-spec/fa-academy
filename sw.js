// ===== فا-اکدمی Service Worker v11 =====
const CACHE_NAME = 'fa-academy-v11';
const CORE_FILES = [
  './',
  './index.html',
  './data.json',
  './manifest.json',
  './sw.js',
  './assets/icons/icon-192.png',
  './assets/icons/icon-512.png',
  './assets/icons/apple-touch-icon.png',
  './assets/icons/favicon-32.png',
  './assets/images/art-science-cover.webp',
  './assets/images/babak-ai/ch02-families.webp',
  './assets/images/babak-ai/ch02-token-cycle.webp',
  './assets/images/babak-ai/ch03-lifecycle.webp',
  './assets/images/babak-ai/ch03-splits.webp',
  './assets/images/babak-ai/ch04-timeline.webp',
  './assets/images/babak-ai/ch05-data-path.webp',
  './assets/images/babak-ai/ch05-capacity.webp',
  './assets/images/babak-ai/ch06-parallel.webp',
  './assets/images/babak-ai/ch07-stack.webp',
  './assets/images/babak-ai/ch07-selection.webp'
];

// ===== INSTALL: Cache core files =====
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return Promise.allSettled(
          CORE_FILES.map(function(url) {
            return cache.add(url).catch(function(err) {
              console.warn('Failed to cache:', url, err);
            });
          })
        );
      })
      .then(function() {
        return self.skipWaiting();
      })
  );
});

// ===== ACTIVATE: Clean old caches =====
self.addEventListener('activate', function(event) {
  var cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.map(function(key) {
          if (cacheWhitelist.indexOf(key) === -1) {
            return caches.delete(key);
          }
        })
      );
    }).then(function() {
      return self.clients.claim();
    })
  );
});

// ===== FETCH: Network-first for HTML/data, cache-first for assets =====
self.addEventListener('fetch', function(event) {
  var url = new URL(event.request.url);

  if (event.request.method !== 'GET') return;
  if (url.origin !== self.location.origin) return;

  // ===== Network-first for HTML, data.json, and navigation =====
  // Use endsWith to handle subdirectory deployments (e.g. /fa-academy/)
  if (event.request.mode === 'navigate' ||
      url.pathname.endsWith('/data.json') ||
      url.pathname.endsWith('/index.html')) {

    event.respondWith(
      fetch(event.request)
        .then(function(response) {
          if (response.ok) {
            var responseClone = response.clone();
            caches.open(CACHE_NAME).then(function(cache) {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        })
        .catch(function(err) {
          return caches.match(event.request).then(function(cached) {
            if (cached) return cached;
            if (event.request.mode === 'navigate') {
              return caches.match('./index.html').then(function(r) {
                if (r) return r;
                return new Response('Offline - please check your connection', {
                  status: 503,
                  statusText: 'Offline',
                  headers: {'Content-Type': 'text/plain'}
                });
              });
            }
            return new Response('Offline', {status: 503, statusText: 'Offline'});
          });
        })
    );
    return;
  }

  // ===== Cache-first for static assets =====
  event.respondWith(
    caches.match(event.request).then(function(cached) {
      if (cached) return cached;
      return fetch(event.request).then(function(response) {
        if (response.ok) {
          var responseClone = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      }).catch(function() {
        return new Response('Resource not available offline', {
          status: 404,
          statusText: 'Not Found'
        });
      });
    })
  );
});

// ===== MESSAGE: Trigger update =====
self.addEventListener('message', function(event) {
  if (event.data === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
