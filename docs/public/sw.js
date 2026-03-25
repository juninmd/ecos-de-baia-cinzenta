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

// Install event - cache essential assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_NAME);
      await cache.addAll(PRECACHE_ASSETS);
    })()
  );
  self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames
          .filter((cacheName) => cacheName !== CACHE_NAME)
          .map((cacheName) => caches.delete(cacheName))
      );
    })()
  );
  self.clients.claim();
});

async function handleFetch(request) {
  try {
    const response = await fetch(request);

    // Clone response to cache it
    const responseToCache = response.clone();
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, responseToCache);

    return response;
  } catch (error) {
    // Network failed, try cache
    const cachedResponse = await caches.match(request);

    // Return offline page for navigation requests if cache misses
    const offlineResponse = request.mode === 'navigate'
      ? await caches.match(OFFLINE_URL)
      : null;

    return cachedResponse || offlineResponse || new Response('Offline', { status: 503 });
  }
}

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  // Skip chrome extensions
  if (event.request.url.startsWith('chrome-extension://')) return;

  event.respondWith(handleFetch(event.request));
});
