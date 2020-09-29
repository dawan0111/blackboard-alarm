
self.addEventListener('install', function(e) {
  console.log('aa');
 e.waitUntil(
   caches.open('airhorner').then(function(cache) {
     return cache.addAll(['/']);
   })
 );
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

async function cacheFirst(req){
  const cachedResponse = caches.match(req);
  return cachedResponse || fetch(req);
}

async function newtorkFirst(req){
  const cache = await caches.open('dynamic-cache');
  const url = new URL(req.url);
  try {
      const res = await fetch(req);

      if (url.pathname.indexOf('/assignment') != 0) {
        cache.put(req, res.clone());
      }
      return res;
  } catch (error) {
      return await cache.match(req);
  }
}

self.addEventListener('fetch', event => {
  const req = event.request;

  if(url.origin === location.url){
      event.respondWith(cacheFirst(req));
  } else {
      event.respondWith(newtorkFirst(req));
  }
});

/*
self.addEventListener('fetch', (event) => {
  const cacheFirst = new workbox.strategies.CacheFirst();
  event.respondWith(cacheFirst.handle({request: event.request}));
});
*/
/*
self.addEventListener('install', async function(e) {
  e.waitUntil(
    caches.open('static-cache').then(function(cache) {
      return cache.addAll([
        '/',
        '/static/main.js',
        '/static/main.css',
        '/static/images/icon-512x512.png',
        '/static/images/loading.svg'
      ]);
    })
  );
});

async function cacheFirst(req){
  const cachedResponse = caches.match(req);
  return cachedResponse || fetch(req);
}

async function newtorkFirst(req){
  const cache = await caches.open('dynamic-cache');

  try {
      const res = await fetch(req);
      cache.put(req, res.clone());
      return res;
  } catch (error) {
      return await cache.match(req);
  }
}
  
self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);

  if(url.origin === location.url){
      event.respondWith(cacheFirst(req));
  } else {
      event.respondWith(newtorkFirst(req));
  }
});
*/