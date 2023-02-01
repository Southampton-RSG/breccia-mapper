var staticCacheName = "django-pwa-v" + new Date().getTime();
var filesToCache = [
    '/offline',
    '/css/django-pwa-app.css',
    '/media/icon-72x72.png',
    '/media/icon-96x96.png',
    '/media/icon-128x128.png',
    '/media/icon-144x144.png',
    '/media/icon-152x152.png',
    '/media/icon-192x192.png',
    '/media/icon-384x384.png',
    '/media/icon-512x512.png',
    '/static/media/splash-640x1136.png',
    '/static/media/splash-750x1334.png',
    '/static/media/splash-1242x2208.png',
    '/static/media/splash-1125x2436.png',
    '/static/media/splash-828x1792.png',
    '/static/media/splash-1242x2688.png',
    '/static/media/splash-1536x2048.png',
    '/static/media/splash-1668x2224.png',
    '/static/media/splash-1668x2388.png',
    '/static/media/splash-2048x2732.png'
];

// Cache on install
self.addEventListener("install", event => {
    this.skipWaiting();
    event.waitUntil(
        caches.open(staticCacheName)
            .then(cache => {
                return cache.addAll(filesToCache);
            })
    )
});

// Clear cache on activate
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(cacheName => (cacheName.startsWith("django-pwa-")))
                    .filter(cacheName => (cacheName !== staticCacheName))
                    .map(cacheName => caches.delete(cacheName))
            );
        })
    );
});

// Serve from Cache
self.addEventListener("fetch", event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                return response || fetch(event.request);
            })
            .catch(() => {
                return caches.match('offline');
            })
    )
});