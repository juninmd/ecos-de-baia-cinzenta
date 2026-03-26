// Service Worker for Ecos de Baía Cinzenta PWA
const CACHE_VERSION = 'v1.0.0';
const CACHE_NAME = `baia-cinzenta-${CACHE_VERSION}`;
const OFFLINE_URL = '/offline.html';

// Assets to cache immediately
const PRECACHE_ASSETS = [
  '/',
  '/capitulo-1',
  '/cidade.jpg',
  '/manifest.json'
];

async function installCache() {
  const cache = await caches.open(CACHE_NAME);
  await cache.addAll(PRECACHE_ASSETS);
  await self.skipWaiting();
}

async function cleanOldCaches() {
  const cacheNames = await caches.keys();
  const cachesToDelete = cacheNames.filter((cacheName) => cacheName !== CACHE_NAME);
  await Promise.all(cachesToDelete.map((cacheName) => caches.delete(cacheName)));
  await self.clients.claim();
}

async function fetchWithFallback(request) {
  try {
    const response = await fetch(request);
    const responseToCache = response.clone();
    const cache = await caches.open(CACHE_NAME);
    await cache.put(request, responseToCache);
    return response;
  } catch (error) {
    const cachedResponse = await caches.match(request);

    // To respect SonarCloud complexity limits, we use flat logic here.
    const isNavigation = request.mode === 'navigate';
    const offlineResponse = isNavigation && await caches.match(OFFLINE_URL);

    return cachedResponse || offlineResponse || new Response('Offline', { status: 503 });
  }
}

// Install event - cache essential assets
self.addEventListener('install', (event) => {
  event.waitUntil(installCache());
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(cleanOldCaches());
});

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  const isGet = event.request.method === 'GET';
  const isChromeExtension = event.request.url.startsWith('chrome-extension://');

  if (!isGet || isChromeExtension) return;

  event.respondWith(fetchWithFallback(event.request));
});
