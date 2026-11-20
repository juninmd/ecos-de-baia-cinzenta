import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { portraitGalleries } from '../docs/.vitepress/theme/portrait-galleries.mjs'

test('retratos adicionais existem e têm descrição', () => {
  for (const [anchor, images] of Object.entries(portraitGalleries)) {
    const paths = [anchor, ...images.map(image => image.src)]
    assert.equal(new Set(paths).size, paths.length, anchor)
    assert.ok(anchor.startsWith('/personagens/'), anchor)
    for (const path of paths) {
      // Variações apontam para a cena original em /cenas/ (as cópias em personagens/variacoes saíram no #596)
      assert.ok(/^\/(personagens|cenas)\//.test(path), path)
      assert.ok(existsSync(`docs/public${path}`), path)
    }
    for (const image of images) assert.ok(image.label.trim(), image.src)
  }
})

test('personagens com múltiplos retratos usam o componente e preservam a âncora', () => {
  const index = readFileSync('docs/personagens.md', 'utf8')
  const profiles = [...index.matchAll(/<!--@include: \.\/(personagens\/[^ ]+\.md) -->/g)]
    .map(match => readFileSync(`docs/${match[1]}`, 'utf8'))
  for (const portrait of Object.keys(portraitGalleries)) {
    const matches = profiles.filter(profile => profile.includes(`portrait="${portrait}"`))
    assert.equal(matches.length, 1, portrait)
    assert.ok(matches[0].includes(`](${portrait})`), portrait)
  }
})
