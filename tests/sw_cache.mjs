// Pins the service worker caching rules: only same-origin 2xx responses enter the cache.
import { fileURLToPath, pathToFileURL } from 'node:url'
import { dirname, resolve } from 'node:path'

const here = dirname(fileURLToPath(import.meta.url))
const swPath = resolve(here, '..', 'docs', 'public', 'sw.js')

const handlers = {}
const store = new Map()
const deleted = []
let precached = []
globalThis.self = {
  addEventListener: (type, fn) => { handlers[type] = fn },
  skipWaiting() {},
  clients: { claim() {} },
  location: new URL('https://site.test/'),
  registration: { scope: 'https://site.test/ecos/' },
}
globalThis.caches = {
  open: async () => ({ addAll: async (urls) => { precached = urls }, put: async (req, res) => { store.set(req.url, res) } }),
  keys: async () => ['another-app', 'baia-cinzenta-%2Fecos%2F-v1', 'baia-cinzenta-%2Fother%2F-v1'],
  delete: async (name) => { deleted.push(name); return true },
  match: async (req) => store.get(typeof req === 'string' ? req : req.url),
}
let upstream
globalThis.fetch = async (req) => upstream(req)

await import(pathToFileURL(swPath).href)

// Browsers report same-origin fetches as 'basic' and cross-origin ones as 'cors'.
const withType = (res, type) => Object.defineProperty(res, 'type', { value: type })

async function fetchAndCheckCache(url, makeResponse) {
  upstream = async () => makeResponse()
  let pending
  await handlers.fetch({ request: new Request(url), respondWith(p) { pending = p } })
  await pending
  await new Promise((r) => setTimeout(r, 20))
  return store.has(url)
}

const cases = [
  ['same-origin 200 is cached', true,
    () => withType(new Response('ok', { status: 200 }), 'basic'), 'https://site.test/capitulo-2'],
  ['same-origin 404 is not cached', false,
    () => withType(new Response('nf', { status: 404 }), 'basic'), 'https://site.test/nao-existe'],
  ['cross-origin 200 is not cached', false,
    () => withType(new Response('x', { status: 200 }), 'cors'), 'https://cdn.other.test/x.js'],
  ['hashed asset miss goes to network and is cached', true,
    () => withType(new Response('js', { status: 200 }), 'basic'), 'https://site.test/ecos/assets/novo.def456.js'],
]

let failed = 0
let lifecycle
handlers.install({ waitUntil(p) { lifecycle = p } })
await lifecycle
handlers.activate({ waitUntil(p) { lifecycle = p } })
await lifecycle
const expectedPrecache = ['/ecos/', '/ecos/capitulo-1.html', '/ecos/cidade.jpg', '/ecos/manifest.json', '/ecos/offline.html']
if (JSON.stringify(precached) !== JSON.stringify(expectedPrecache) || JSON.stringify(deleted) !== JSON.stringify(['baia-cinzenta-%2Fecos%2F-v1'])) {
  console.error('FAIL scoped precache or cache cleanup', { precached, deleted })
  failed++
} else console.log('PASS scoped precache and cache cleanup')
for (const [name, expected, makeResponse, url] of cases) {
  const cached = await fetchAndCheckCache(url, makeResponse)
  const pass = cached === expected
  if (!pass) failed++
  console.log(`${pass ? 'PASS' : 'FAIL'} ${name} (cached=${cached})`)
}
// Assets com hash no nome (/assets/) não mudam de conteúdo: servidos do cache sem rede.
{
  const hashed = 'https://site.test/ecos/assets/app.abc123.js'
  store.set(hashed, new Response('cached-bundle'))
  let networkCalls = 0
  upstream = async () => { networkCalls++; return withType(new Response('network-bundle', { status: 200 }), 'basic') }
  let pending
  await handlers.fetch({ request: new Request(hashed), respondWith(p) { pending = p } })
  const body = await (await pending).text()
  const pass = networkCalls === 0 && body === 'cached-bundle'
  if (!pass) failed++
  console.log(`${pass ? 'PASS' : 'FAIL'} hashed asset served from cache (network=${networkCalls}, body=${body})`)
}

process.exit(failed ? 1 : 0)
