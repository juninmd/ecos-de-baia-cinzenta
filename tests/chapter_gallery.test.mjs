import assert from 'node:assert/strict'
import { mkdirSync, mkdtempSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import test from 'node:test'
import { chapterImages } from '../docs/.vitepress/chapter-gallery.mjs'

function fixture(files, regerar) {
  const root = mkdtempSync(join(tmpdir(), 'gallery-'))
  for (const f of files) {
    mkdirSync(join(root, 'cenas', ...f.split('/').slice(0, -1)), { recursive: true })
    writeFileSync(join(root, 'cenas', f), 'x')
  }
  if (regerar) writeFileSync(join(root, 'cenas', 'regerar.txt'), regerar)
  return root
}

test('capa vem primeiro e as cenas seguem em ordem numérica (cena_10 depois de cena_2)', () => {
  const publicDir = fixture(['capitulo_7/cena_10.jpg', 'capitulo_7/cena_2.jpg', 'capitulo_7/cena_1.jpg'])
  const got = chapterImages({ publicDir, relativePath: 'capitulo-7.md', cover: '/capitulo_7.jpg' })
  assert.deepEqual(got, ['/capitulo_7.jpg', '/cenas/capitulo_7/cena_1.jpg', '/cenas/capitulo_7/cena_2.jpg', '/cenas/capitulo_7/cena_10.jpg'])
})

test('subpastas comparativas, arquivos alheios e cenas reprovadas ficam de fora', () => {
  const publicDir = fixture(
    ['capitulo_13/cena_1.jpg', 'capitulo_13/cena_5.jpg', 'capitulo_13/local/cena_2.jpg', 'capitulo_13/qwen_edit/cena_3.jpg', 'capitulo_13/notas.txt'],
    '# reprovadas\ndocs/public/cenas/capitulo_13/cena_5.jpg\n',
  )
  const got = chapterImages({ publicDir, relativePath: 'capitulo-13.md', cover: '/capitulo_13.jpg' })
  assert.deepEqual(got, ['/capitulo_13.jpg', '/cenas/capitulo_13/cena_1.jpg'])
})

test('capítulo sem pasta de cenas devolve só a capa; sem nada devolve vazio', () => {
  const publicDir = fixture(['capitulo_1/cena_1.jpg'])
  assert.deepEqual(chapterImages({ publicDir, relativePath: 'capitulo-2.md', cover: '/capitulo_2.jpg' }), ['/capitulo_2.jpg'])
  assert.deepEqual(chapterImages({ publicDir, relativePath: 'capitulo-2.md' }), [])
})

test('páginas que não são capítulo não ganham galeria, nem com pasta de cenas parecida', () => {
  const publicDir = fixture(['capitulo_1/cena_1.jpg'])
  for (const relativePath of ['arcos.md', 'personagens/aria.md', 'capitulo-1-rascunho.md', undefined]) {
    assert.deepEqual(chapterImages({ publicDir, relativePath, cover: '/x.jpg' }), [], String(relativePath))
  }
})

test('respeita o base do deploy sem duplicar o prefixo', () => {
  const publicDir = fixture(['capitulo_1/cena_1.jpg'])
  const base = '/ecos-de-baia-cinzenta/'
  const got = chapterImages({ publicDir, relativePath: 'capitulo-1.md', cover: `${base}capitulo_1.jpg`, base })
  assert.deepEqual(got, [`${base}capitulo_1.jpg`, `${base}cenas/capitulo_1/cena_1.jpg`])
})
