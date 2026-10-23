import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { test } from 'node:test'

const checkerSource = readFileSync(new URL('./check_dependency_metadata.mjs', import.meta.url), 'utf8')
const lock = "lockfileVersion: '9.0'\n\npackages:\n  example@1.0.0:\n    resolution: {integrity: sha512-example}\nsnapshots:\n"
const release = {
  versions: { '1.0.0': { repository: { url: 'https://example.org/source' }, dist: { integrity: 'sha512-example' } } },
  time: { '1.0.0': '2020-01-01T00:00:00Z' },
}
function check(metadata = release, input = lock) {
  const directory = mkdtempSync(join(tmpdir(), 'dependency-metadata-test-'))
  const scriptDirectory = join(directory, 'scripts')
  mkdirSync(scriptDirectory)
  writeFileSync(join(scriptDirectory, 'check_dependency_metadata.mjs'), checkerSource)
  writeFileSync(join(directory, 'pnpm-lock.yaml'), input)
  const script = pathToFileURL(join(scriptDirectory, 'check_dependency_metadata.mjs')).href
  const code = `
    globalThis.fetch = async () => ({ ok: true, json: async () => (${JSON.stringify(metadata)}) });
    await import(${JSON.stringify(script)});
  `
  const result = spawnSync(process.execPath, ['--input-type=module', '-e', code], { encoding: 'utf8' })
  rmSync(directory, { recursive: true, force: true })
  return result
}
test('accepts exact old releases with matching integrity and known source', () => {
  const result = check()
  assert.equal(result.status, 0, result.stderr)
  assert.match(result.stdout, /Verified 1 locked releases/)
  assert.equal(check(release, lock.replace(/\n/g, '\r\n')).status, 0)
})
test('rejects recent releases despite a matching lock integrity', () => {
  const metadata = structuredClone(release)
  metadata.time['1.0.0'] = new Date().toISOString()
  const result = check(metadata)
  assert.notEqual(result.status, 0)
  assert.match(result.stderr, /younger than 24h/)
})
test('rejects registry archives that differ from the lock', () => {
  const metadata = structuredClone(release)
  metadata.versions['1.0.0'].dist.integrity = 'sha512-other'
  const result = check(metadata)
  assert.notEqual(result.status, 0)
  assert.match(result.stderr, /Integrity mismatch/)
})
test('rejects unknown timestamps and unsupported lock records', () => {
  const metadata = structuredClone(release)
  delete metadata.time['1.0.0']
  assert.match(check(metadata).stderr, /Unknown release/)
  assert.match(check(release, lock.replace('integrity: sha512-example', 'tarball: https://example.org/file')).stderr, /Unsupported lock entries/)
})
test('rejects missing repository and source revision metadata', () => {
  const metadata = structuredClone(release)
  delete metadata.versions['1.0.0'].repository
  const result = check(metadata)
  assert.notEqual(result.status, 0)
  assert.match(result.stderr, /Source repository metadata unavailable/)
})
