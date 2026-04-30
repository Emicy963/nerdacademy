const CACHE = 'matrika-v1';

const STATIC = [
  '/css/global.css',
  '/css/layout.css',
  '/js/api.js',
  '/js/i18n.js',
  '/js/layout.js',
  '/js/config.js',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(STATIC)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const { request } = e;
  const url = new URL(request.url);

  // Never intercept API calls — they need live data
  if (url.pathname.startsWith('/api/')) return;

  // For navigation and static assets: cache-first, network fallback
  e.respondWith(
    caches.match(request).then(cached => {
      if (cached) return cached;
      return fetch(request).then(res => {
        // Cache successful GET responses for static assets
        if (res.ok && request.method === 'GET' &&
            (url.pathname.endsWith('.css') || url.pathname.endsWith('.js'))) {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(request, clone));
        }
        return res;
      });
    })
  );
});
