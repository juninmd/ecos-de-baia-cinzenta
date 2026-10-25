// Pina a regra de preload: diagramas saem das páginas, o resto do preload fica.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { mkdtemp, mkdir, readFile, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { stripDiagramHints } from '../docs/.vitepress/preload-hints.mjs'

test('remove hints de diagramas e mantém o preload do resto', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'preload-hints-'))
  await mkdir(join(dir, 'sub'))
  const page = [
    '<link rel="modulepreload" href="/assets/chunks/framework.abc.js">',
    '<link rel="modulepreload" href="/assets/chunks/swimlanes-5IMT.js">',
    '<link rel="prefetch" href="/assets/chunks/cytoscape.esm.js">',
    '<link rel="modulepreload" href="/assets/capitulo-1.md.lean.js">',
  ].join('\n')
  await writeFile(join(dir, 'capitulo-1.html'), page)
  await writeFile(join(dir, 'sub', 'arcos.html'), '<link rel="modulepreload" href="/assets/chunks/katex.js">')
  await writeFile(join(dir, 'notas.txt'), '<link rel="modulepreload" href="/assets/chunks/katex.js">')

  await stripDiagramHints(dir)

  const out = await readFile(join(dir, 'capitulo-1.html'), 'utf8')
  assert.equal(out.includes('swimlanes'), false, 'diagrama precisa sair do preload')
  assert.equal(out.includes('cytoscape'), false, 'prefetch de diagrama também sai')
  assert.equal(out.includes('framework.abc.js'), true, 'preload da página precisa ficar')
  assert.equal(out.includes('capitulo-1.md.lean.js'), true, 'chunk da página precisa ficar')
  assert.equal((await readFile(join(dir, 'sub', 'arcos.html'), 'utf8')).includes('katex'), false)
  assert.equal((await readFile(join(dir, 'notas.txt'), 'utf8')).includes('katex'), true, 'só .html é reescrito')
})
