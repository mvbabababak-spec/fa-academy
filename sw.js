// ===== فا-اکدمی Service Worker v37 =====
const CACHE_NAME = 'fa-academy-v37';
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
  './book-engineering/LEARNING_PATH_FA.md',
  './book-engineering/answers/01-intelligence-answers-fa.md',
  './book-engineering/answers/18-calculus-answers-fa.md',
  './book-engineering/answers/17-linear-algebra-answers-fa.md',
  './book-engineering/answers/16-algebra-functions-answers-fa.md',
  './book-engineering/answers/15-data-analysis-answers-fa.md',
  './book-engineering/answers/14-debug-testing-sql-security-answers-fa.md',
  './book-engineering/answers/13-linux-git-environments-answers-fa.md',
  './book-engineering/answers/12-classes-files-json-api-answers-fa.md',
  './book-engineering/answers/11-functions-data-structures-answers-fa.md',
  './book-engineering/answers/10-python-basics-answers-fa.md',
  './book-engineering/answers/09-first-program-answers-fa.md',
  './book-engineering/answers/02-ai-families-answers-fa.md',
  './book-engineering/answers/03-model-lifecycle-answers-fa.md',
  './book-engineering/answers/04-history-answers-fa.md',
  './book-engineering/answers/05-computer-foundations-answers-fa.md',
  './book-engineering/answers/06-gpu-parallelism-answers-fa.md',
  './book-engineering/answers/07-compute-ecosystems-answers-fa.md',
  './book-engineering/answers/08-distributed-infrastructure-answers-fa.md',
  './assets/images/babak-ai/ch02-families.webp',
  './assets/images/babak-ai/ch02-token-cycle.webp',
  './assets/images/babak-ai/ch03-lifecycle.webp',
  './assets/images/babak-ai/ch03-splits.webp',
  './assets/images/babak-ai/ch04-timeline.webp',
  './assets/images/babak-ai/ch05-data-path.webp',
  './assets/images/babak-ai/ch05-capacity.webp',
  './assets/images/babak-ai/ch06-parallel.webp',
  './assets/images/babak-ai/ch07-stack.webp',
  './assets/images/babak-ai/ch07-selection.webp',
  './assets/images/babak-ai/ch08-distributed.webp',
  './assets/images/babak-ai/ch09-flow.webp',
  './assets/images/babak-ai/ch10-condition.webp',
  './assets/images/babak-ai/ch11-function.webp',
  './assets/images/babak-ai/ch12-object.webp',
  './assets/images/babak-ai/ch13-git.webp',
  './assets/images/babak-ai/ch14-tests.webp',
  './assets/images/babak-ai/ch15-study-chart.webp',
  './assets/images/babak-ai/ch16-graph.webp',
  './assets/images/babak-ai/ch14-testing.webp',
  './assets/images/babak-ai/ch15-study.webp',
  './assets/images/babak-ai/ch16-linear.webp',
  './assets/images/babak-ai/ch17-matrix.webp',
  './assets/images/babak-ai/ch18-derivative.webp',
  './assets/images/babak-ai/ch19-bayes.webp',
  './assets/images/babak-ai/ch20-descent.webp',
  './assets/images/babak-ai/ch21-entropy.webp'
];

// ===== INSTALL: Cache core files =====
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        // Keep the previous worker active if the offline shell cannot be cached.
        return cache.addAll(['./', './index.html', './data.json']).then(function() {
          return Promise.allSettled(CORE_FILES.slice(3).map(function(url) {
            return cache.add(url).catch(function(err) { console.warn('Failed to cache:', url, err); });
          }));
        });
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
          if (key.indexOf('fa-academy-') === 0 && cacheWhitelist.indexOf(key) === -1) {
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
          return caches.match(event.request, {ignoreSearch:true}).then(function(cached) {
            if (cached) return cached;
            if (url.pathname.endsWith('/data.json')) return caches.match('./data.json');
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
