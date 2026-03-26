// Service Worker for Ecos de Baía Cinzenta PWA
const CACHE_VERSION = 'v1.0.0';
const CACHE_NAME = `baia-cinzenta-${CACHE_VERSION}`;
const OFFLINE_URL = '/offline.html';

const PRECACHE_ASSETS = [
  '/',
  '/capitulo-1',
  '/cidade.jpg',
  '/manifest.json'
];

async function installWorker() {
  const cache = await caches.open(CACHE_NAME);
  await cache.addAll(PRECACHE_ASSETS);
  self.skipWaiting();
}

self.addEventListener('install', (event) => {
  event.waitUntil(installWorker());
});

async function activateWorker() {
  const cacheNames = await caches.keys();
  await Promise.all(
    cacheNames.filter(name => name !== CACHE_NAME).map(name => caches.delete(name))
  );
  self.clients.claim();
}

self.addEventListener('activate', (event) => {
  event.waitUntil(activateWorker());
});

async function handleFetchEvent(request) {
  try {
    const response = await fetch(request);

    // Background cache put to not block response
    const responseToCache = response.clone();
    (async () => {
        const cache = await caches.open(CACHE_NAME);
        await cache.put(request, responseToCache);
    })();

    return response;
  } catch (err) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    const isNavigation = request.mode === 'navigate';
    if (isNavigation) {
      return await caches.match(OFFLINE_URL);
    }
    return new Response('Offline', { status: 503 });
  }
}

self.addEventListener('fetch', (event) => {
  const isGet = event.request.method === 'GET';
  const isExtension = event.request.url.startsWith('chrome-extension://');
  if (!isGet || isExtension) return;

  event.respondWith(handleFetchEvent(event.request));
});
