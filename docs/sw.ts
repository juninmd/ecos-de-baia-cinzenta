/// <reference lib="webworker" />

const sw = self as unknown as ServiceWorkerGlobalScope;

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

async function installWorker(): Promise<void> {
  const cache = await caches.open(CACHE_NAME);
  await cache.addAll(PRECACHE_ASSETS);
  sw.skipWaiting();
}

async function updateCache(request: Request, response: Response): Promise<void> {
  try {
    const cache = await caches.open(CACHE_NAME);
    await cache.put(request, response);
  } catch {
    console.error('Falha ao atualizar o cache');
  }
}

sw.addEventListener('install', (event: ExtendableEvent) => {
  event.waitUntil(installWorker());
});

async function activateWorker(): Promise<void> {
  const cacheNames = await caches.keys();
  await Promise.all(
    cacheNames.filter(name => name !== CACHE_NAME).map(name => caches.delete(name))
  );
  sw.clients.claim();
}

sw.addEventListener('activate', (event: ExtendableEvent) => {
  event.waitUntil(activateWorker());
});

async function getOfflineResponse(): Promise<Response> {
  const offlineResponse = await caches.match(OFFLINE_URL);
  if (offlineResponse) {
    return offlineResponse;
  }
  return new Response('Offline', { status: 503 });
}

async function handleNavigationFallback(request: Request): Promise<Response> {
  const isNavigation = request.mode === 'navigate';
  if (!isNavigation) {
    return new Response('Offline', { status: 503 });
  }
  return getOfflineResponse();
}

async function handleFetchFallback(request: Request): Promise<Response> {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  return handleNavigationFallback(request);
}

async function handleFetchEvent(request: Request): Promise<Response> {
  try {
    const response = await fetch(request);

    // Background cache put to not block response
    const responseToCache = response.clone();
    updateCache(request, responseToCache);

    return response;
  } catch {
    return handleFetchFallback(request);
  }
}

sw.addEventListener('fetch', (event: FetchEvent) => {
  const isGet = event.request.method === 'GET';
  const isExtension = event.request.url.startsWith('chrome-extension://');
  if (!isGet || isExtension) return;

  event.respondWith(handleFetchEvent(event.request));
});
