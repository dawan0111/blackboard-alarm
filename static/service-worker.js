self.addEventListener('install', function(e) {
  console.log('[Service Worker] Install');
});
  
self.addEventListener('fetch', function(e) {
    e.respondWith(
      caches.match(e.request).then(function(response) {
        return response || fetch(e.request);
      })
    )
});