/* RADIO DVA — Service Worker v1.0 */
const CACHE = 'radio-dva-v1';
const ASSETS = [
  '/',
  '/index.html',
  '/advert.html',
  '/css/style.css',
  '/js/data.js',
  '/js/player.js',
  '/js/main.js',
  '/assets/icons/icon-192.svg',
  '/assets/icons/icon-512.svg'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then(cached =>
      cached || fetch(e.request).catch(() => {
        // Offline fallback
        if (e.request.mode === 'navigate') {
          return caches.match('/index.html');
        }
      })
    )
  );
});

// Background sync for messages when offline
self.addEventListener('sync', (e) => {
  if (e.tag === 'sync-messages') {
    // Retry sending queued messages
  }
});
