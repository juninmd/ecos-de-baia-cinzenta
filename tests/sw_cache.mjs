// Pins the service worker caching rules: only same-origin 2xx responses enter the cache.
import { fileURLToPath, pathToFileURL } from 'node:url'
import { dirname, resolve } from 'node:path'

const here = dirname(fileURLToPath(import.meta.url))
const swPath = resolve(here, '..', 'docs', 'public', 'sw.js')

const handlers = {}
const store = new Map()
globalThis.self = {
  addEventListener: (type, fn) => { handlers[type] = fn },
  skipWaiting() {},
  clients: { claim() {} },
  location: new URL('https://site.test/'),
}
globalThis.caches = {
  open: async () => ({ addAll: async () => {}, put: async (req, res) => { store.set(req.url, res) } }),
  keys: async () => [],
  delete: async () => true,
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
]

let failed = 0
for (const [name, expected, makeResponse, url] of cases) {
  const cached = await fetchAndCheckCache(url, makeResponse)
  const pass = cached === expected
  if (!pass) failed++
  console.log(`${pass ? 'PASS' : 'FAIL'} ${name} (cached=${cached})`)
}
process.exit(failed ? 1 : 0)
