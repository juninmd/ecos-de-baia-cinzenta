import assert from 'node:assert/strict'
import test from 'node:test'
import { buildChapterIndex, neighbors } from '../docs/.vitepress/theme/chapter-index.mjs'

const sidebar = [
  { text: 'Livro', items: [{ text: 'Parte', items: [
    { text: 'Capítulo 241: A Chave', link: '/capitulo-241' },
    { text: 'Capítulo 3: O Terceiro', link: '/capitulo-3' },
    { text: 'Capítulo 256: Oito Portas', link: '/capitulo-256' },
  ] }] },
  { text: 'Arquivos', items: [{ text: 'Arcos', link: '/arcos' }] },
]

test('indexa capítulos além de 114, em ordem numérica, ignorando páginas que não são capítulos', () => {
  const index = buildChapterIndex(sidebar)
  assert.deepEqual(index.map((c) => c.number), [3, 241, 256])
})

test('o último capítulo do menu não tem próximo; vizinhos respeitam a ordem do menu', () => {
  const index = buildChapterIndex(sidebar)
  assert.equal(neighbors(index, 256).next, null)
  assert.equal(neighbors(index, 241).next.number, 256)
  assert.equal(neighbors(index, 241).prev.number, 3)
})

test('capítulo desconhecido e sidebar vazio não quebram', () => {
  assert.deepEqual(neighbors(buildChapterIndex(sidebar), 999), { prev: null, next: null })
  assert.deepEqual(buildChapterIndex(undefined), [])
})

test('aceita sidebar em formato de objeto por rota', () => {
  assert.equal(buildChapterIndex({ '/': sidebar }).length, 3)
})
