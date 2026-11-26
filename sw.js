/* K-iNSURE service worker: makes the app work offline.
   IMPORTANT: change CACHE_VERSION every time you publish an update,
   so installed apps download the new files. */
const CACHE_VERSION = 'kinsure-v1.6.9';

const APP_FILES = [
  './',
  './index.html',
  './mobile.html',
  './whats-new.html',
  './mobile.webmanifest',
  './manifest.webmanifest',
  './modules/motor.html',
  './modules/fire.html',
  './modules/health.html',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/maskable-512.png',
  './icons/apple-touch-icon.png',
  './icons/favicon-32.png'
];

/* Install: always download fresh copies (skip the browser's own HTTP cache). */
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then((cache) => cache.addAll(APP_FILES.map((u) => new Request(u, { cache: 'reload' }))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function isPage(url, req) {
  return req.mode === 'navigate' || /\.(html|webmanifest|js)$/.test(url.pathname) || url.pathname.endsWith('/');
}

/* Pages and calculators: online = fresh copy from the website (and saved for offline);
   offline or very slow network = the saved copy.
   Icons: saved copy first. */
self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;

  if (isPage(url, req)) {
    event.respondWith(
      caches.open(CACHE_VERSION).then((cache) => {
        const network = fetch(req.url, { cache: 'no-cache', credentials: 'same-origin' })
          .then((res) => { if (res && res.ok) cache.put(req.url, res.clone()); return res; });
        const timeout = new Promise((resolve) => setTimeout(resolve, 5000));
        return Promise.race([network.catch(() => null), timeout]).then((res) =>
          res || cache.match(req, { ignoreSearch: true }).then((cached) => cached || network)
        );
      })
    );
    return;
  }

  event.respondWith(
    caches.open(CACHE_VERSION).then((cache) =>
      cache.match(req, { ignoreSearch: true }).then((cached) => {
        const network = fetch(req).then((res) => { if (res && res.ok) cache.put(req, res.clone()); return res; }).catch(() => cached);
        return cached || network;
      })
    )
  );
});
