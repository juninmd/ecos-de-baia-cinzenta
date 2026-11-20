import { test } from 'node:test'
import assert from 'node:assert/strict'
import { browsing, recall } from '../docs/.vitepress/theme/lib/command-history.mjs'

const history = ['help', 'ir 12', 'status']

test('↑ repetido percorre o histórico inteiro, do mais novo ao mais antigo', () => {
  let cursor = history.length
  const seen = []
  for (let i = 0; i < 4; i++) {
    const r = recall(history, cursor, -1)
    cursor = r.cursor
    seen.push(r.text)
  }
  assert.deepEqual(seen, ['status', 'ir 12', 'help', 'help'])
})

test('↓ volta para o mais novo e termina no prompt vazio', () => {
  assert.deepEqual(recall(history, 1, 1), { cursor: 2, text: 'status' })
  assert.deepEqual(recall(history, 2, 1), { cursor: 3, text: '' })
})

test('só navega o histórico enquanto o texto não foi editado', () => {
  assert.equal(browsing(history, 1, 'ir 12'), true)
  assert.equal(browsing(history, 1, 'ir 13'), false)
  assert.equal(browsing(history, history.length, ''), false)
})
