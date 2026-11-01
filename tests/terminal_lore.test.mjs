import assert from 'node:assert/strict'
import test from 'node:test'
import { CAST, bookAt, complete, runCommand, stateAt } from '../docs/.vitepress/theme/terminal-lore.mjs'

const text = (r) => r.lines.map((l) => l.text).join('\n')
const person = (nome) => CAST.find((p) => p.nome.startsWith(nome))

test('arquivos restritos ficam negados até o capítulo liberado (sem spoiler)', () => {
  assert.match(text(runCommand('genesis', { chapter: 10 })), /ACESSO NEGADO/)
  assert.doesNotMatch(text(runCommand('genesis', { chapter: 10 })), /backup/)
  assert.match(text(runCommand('genesis', { chapter: 106 })), /backup/)
  assert.match(text(runCommand('mesa', { chapter: 244 })), /ACESSO NEGADO/)
  assert.match(text(runCommand('mesa', { chapter: 245 })), /Tê/)
})

test('personagens só lista quem o leitor já conheceu e no estado daquele capítulo', () => {
  const cedo = text(runCommand('personagens', { chapter: 10 }))
  assert.doesNotMatch(cedo, /ELENA|BIO-DANTE|PRADO/)
  assert.match(cedo, /VILAR, CAPITÃO \[ATIVO\]/)
  const fim = text(runCommand('personagens', { chapter: 256 }))
  assert.match(fim, /VILAR, CAPITÃO \[FALECIDO\]/)
  assert.match(fim, /MORETTI, MARCO \[RÉU DA MESA\]/)
  assert.doesNotMatch(fim, /MARCO \[FALECIDO\]/)
})

test('mortes viram status exatamente no capítulo dos dossiês', () => {
  const rotulo = (n, ch) => stateAt(person(n), ch).rotulo
  assert.equal(rotulo('VILAR', 251), 'ATIVO')
  assert.equal(rotulo('VILAR', 252), 'FALECIDO')
  assert.equal(rotulo('RANGEL', 151), 'ATIVO')
  assert.equal(rotulo('RANGEL', 152), 'FALECIDO')
  assert.equal(rotulo('MORETTI, MARCO', 243), 'ATIVO')
  assert.equal(rotulo('MORETTI, MARCO', 244), 'RÉU DA MESA')
  assert.equal(rotulo('BIO-DANTE', 254), 'FALECIDO')
})

test('cada personagem começa a existir no primeiro estado declarado', () => {
  for (const p of CAST) assert.equal(p.estados[0].de, p.desde, p.nome)
})

test('ir só abre capítulo já lido ou o próximo, nunca o futuro', () => {
  assert.equal(runCommand('ir 4', { chapter: 3, total: 256 }).go, 4)
  assert.equal(runCommand('ir 5', { chapter: 3, total: 256 }).go, undefined)
  assert.equal(runCommand('ir abc', { chapter: 3, total: 256 }).go, undefined)
  assert.equal(runCommand('ir 999', { chapter: 999, total: 256 }).go, undefined)
})

test('protocolo_final exige o modo administrador; sair e limpar são aliases', () => {
  assert.match(text(runCommand('protocolo_final', { chapter: 200 })), /Acesso Negado/)
  assert.match(text(runCommand('protocolo_final', { hacked: true })), /SILÊNCIO/)
  assert.equal(runCommand('sair').close, true)
  assert.equal(runCommand('limpar').clear, true)
  assert.match(text(runCommand('xyz')), /não reconhecido/)
})

test('livro atual e autocompletar', () => {
  assert.equal(bookAt(1), 'Livro 1: O Dilúvio')
  assert.equal(bookAt(241), 'Livro 4: O Contraditório')
  assert.deepEqual(complete('pe'), ['personagens'])
  assert.deepEqual(complete(''), [])
})
