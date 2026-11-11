import assert from 'node:assert/strict'
import test from 'node:test'
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { splitSentences, speakable } from '../docs/.vitepress/theme/lib/sentences.mjs'
import { normalizePrefs, stepSize, DEFAULTS } from '../docs/.vitepress/theme/lib/reader-prefs.mjs'
import { aliasPattern, castAt } from '../docs/.vitepress/theme/lib/cast.mjs'
import { archivePages, chapterTitle, searchPalette } from '../docs/.vitepress/theme/lib/palette-search.mjs'
import { chapterStats } from '../docs/.vitepress/theme/lib/chapter-stats.mjs'

const THEME = new URL('../docs/.vitepress/theme/', import.meta.url).pathname

test('frases guardam a posição exata no parágrafo (o marcador realça o trecho certo)', () => {
  const text = 'A chuva não lavava nada. — Pare aí! Ele hesitou… e foi.'
  const parts = splitSentences(text)
  assert.deepEqual(parts.map((p) => p.text), ['A chuva não lavava nada.', '— Pare aí!', 'Ele hesitou…', 'e foi.'])
  for (const p of parts) assert.equal(text.slice(p.start, p.end), p.text)
  assert.deepEqual(splitSentences(' — '), [])
  assert.equal(speakable('— Pare aí. — Gabo segurou.'), 'Pare aí., Gabo segurou.')
})

test('preferências do leitor ficam dentro dos limites do tema anterior (70–150%)', () => {
  assert.deepEqual(normalizePrefs(null), DEFAULTS)
  assert.equal(normalizePrefs({ size: 400 }).size, 150)
  assert.equal(normalizePrefs({ size: 10 }).size, 70)
  assert.equal(normalizePrefs({ skin: 'neon', face: 'comic' }).skin, 'auto')
  assert.equal(normalizePrefs({ lineHeight: 'x' }).lineHeight, DEFAULTS.lineHeight)
  assert.equal(stepSize(150, 1), 150)
  assert.equal(stepSize(120, 0), 100)
})

test('elenco não revela quem ainda não apareceu e segue a fase visual', () => {
  const cedo = castAt(10)
  assert.ok(cedo.find((p) => p.nome === 'Bio-Dante').locked)
  assert.ok(!cedo.find((p) => p.nome.includes('Gabo')).locked)
  assert.equal(cedo.find((p) => p.nome === 'Elena Moretti').retrato, '/personagens/elena.png')
  assert.equal(castAt(104).find((p) => p.nome === 'Elena Moretti').retrato, '/personagens/elena_2.png')
  assert.equal(castAt(152).find((p) => p.nome === 'Inspetor Rangel').rotulo, 'FALECIDO')
  for (const p of castAt(999)) assert.ok(readdirSync(join(THEME, '../../public/personagens')).includes(p.retrato.split('/').pop()), p.retrato)
})

test('cartão no texto só casa nome inteiro e já apresentado', () => {
  const re = aliasPattern(castAt(1))
  assert.match('Gabo olhou', re)
  assert.doesNotMatch('Gabolândia', re)
  assert.doesNotMatch('Bio-Dante falou', re) // ainda bloqueado no cap. 1
  assert.match('Bio-Dante falou', aliasPattern(castAt(200)))
})

test('paleta Lázaro busca sem spoiler', () => {
  const chapters = [1, 2, 3, 4].map((n) => ({ number: n, title: ['Olhos de Vidro', 'Náufragos', 'Teatro de Carne', 'A Torre'][n - 1] }))
  const opts = { chapters, cast: castAt(2), pages: [{ text: 'Cronologia e Resumo', link: '/cronologia' }], furthest: 2 }
  assert.equal(searchPalette('', opts)[0].run, 'ir 2')
  assert.deepEqual(searchPalette('vidro', opts).map((i) => i.run), ['ir 1'])
  assert.equal(searchPalette('torre', opts).length, 0)
  assert.equal(searchPalette('4', opts)[0].kind, 'locked')
  assert.equal(searchPalette('ir 3', opts)[0].run, 'ir 3')
  assert.equal(searchPalette('naufragos', opts)[0].label, 'Cap. 2 · Náufragos')
  assert.equal(searchPalette('crono', opts)[0].link, '/cronologia')
  assert.ok(searchPalette('aria', opts).some((i) => i.kind === 'person'))
  assert.equal(chapterTitle('Capítulo 12: Shadowban'), 'Shadowban')
  const pages = archivePages([{ items: [{ text: 'Capítulo 1: X', link: '/capitulo-1' }, { text: 'Lore', link: '/lore-do-livro' }] }])
  assert.deepEqual(pages, [{ text: 'Lore', link: '/lore-do-livro' }])
})

test('estatística do capítulo vem do arquivo-fonte', () => {
  const src = readFileSync(join(THEME, '../../capitulo-1.md'), 'utf8')
  const s = chapterStats('/x/docs/capitulo-1.md', src)
  assert.equal(s.n, 1)
  assert.equal(s.title, 'Olhos de Vidro')
  assert.equal(s.image, '/capitulo_1.jpg')
  assert.ok(s.words > 600)
  assert.equal(chapterStats('/x/docs/index.md', ''), null)
})

test('arquivos do tema Sódio respeitam o limite de 150 linhas', () => {
  const dirs = ['sodio', 'lib', 'composables', 'components']
  const legacy = new Set(['ChapterCarousel.vue']) // anterior ao redesign
  for (const dir of dirs) {
    for (const f of readdirSync(join(THEME, dir)).filter((f) => !legacy.has(f))) {
      const lines = readFileSync(join(THEME, dir, f), 'utf8').trimEnd().split('\n').length
      assert.ok(lines <= 150, `${dir}/${f} tem ${lines} linhas`)
    }
  }
  assert.ok(readFileSync(join(THEME, 'Layout.vue'), 'utf8').split('\n').length <= 150)
})
