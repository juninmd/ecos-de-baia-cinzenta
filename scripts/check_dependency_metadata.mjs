import { readFile } from 'node:fs/promises'

// Frozen installs verify resolution, but pnpm 10 does not recheck release age.
const minimumAgeMs = 24 * 60 * 60 * 1000
const lock = (await readFile(new URL('../pnpm-lock.yaml', import.meta.url), 'utf8')).replace(/\r\n/g, '\n')
const packages = lock.split('\npackages:\n')[1]?.split('\nsnapshots:\n')[0]
if (!packages) throw new Error('Cannot locate locked packages')
const entries = [...packages.matchAll(/^  '?((?:@[^/\s]+\/)?[^@\s':]+)@([^'\s:]+)'?:\n    resolution: \{integrity: ([^}]+)\}/gm)]
const expectedEntries = (packages.match(/^  \S.*:\n/gm) ?? []).length
if (!entries.length || entries.length !== expectedEntries) {
  throw new Error(`Unsupported lock entries: parsed ${entries.length}/${expectedEntries}`)
}
const groups = new Map()
for (const [, name, version, integrity] of entries) {
  if (!groups.has(name)) groups.set(name, [])
  groups.get(name).push({ version, integrity })
}
const pending = [...groups]
let verified = 0
const sourceLimits = []
async function worker() {
  while (pending.length) {
    const [name, versions] = pending.pop()
    const response = await fetch(`https://registry.npmjs.org/${encodeURIComponent(name)}`, {
      signal: AbortSignal.timeout(60_000),
    })
    if (!response.ok) throw new Error(`Registry ${response.status}: ${name}`)
    const metadata = await response.json()
    for (const { version, integrity } of versions) {
      const release = metadata.versions?.[version]
      const published = Date.parse(metadata.time?.[version])
      const label = `${name}@${version}`
      if (!release || !Number.isFinite(published)) throw new Error(`Unknown release: ${label}`)
      if (Date.now() - published < minimumAgeMs) throw new Error(`Release younger than 24h: ${label}`)
      if (release.dist?.integrity !== integrity) throw new Error(`Integrity mismatch: ${label}`)
      const repository = release.repository ?? metadata.repository
      if (!repository && !release.gitHead) sourceLimits.push(label)
      verified++
    }
  }
}
await Promise.all(Array.from({ length: Math.min(6, groups.size) }, worker))
console.log(`Verified ${verified} locked releases: registry integrity and minimum age 24h.`)
if (sourceLimits.length) {
  console.warn(`Source repository metadata unavailable: ${sourceLimits.join(', ')}`)
  process.exitCode = 1
}
