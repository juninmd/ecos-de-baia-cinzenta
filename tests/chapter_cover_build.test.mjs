import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, existsSync } from 'node:fs'
import { prefixCoverPath } from '../docs/.vitepress/cover-path.mjs'

const base = '/ecos-de-baia-cinzenta/'

test('chapter covers respect deployment base without changing external URLs', () => {
  assert.equal(prefixCoverPath('/capitulo_1.jpg', base), `${base}capitulo_1.jpg`)
  assert.equal(prefixCoverPath(`${base}capitulo_1.jpg`, base), `${base}capitulo_1.jpg`)
  assert.equal(prefixCoverPath('/capitulo_1.jpg', '/'), '/capitulo_1.jpg')
  assert.equal(prefixCoverPath('https://example.com/cover.jpg', base), 'https://example.com/cover.jpg')
  assert.equal(prefixCoverPath('//example.com/cover.jpg', base), '//example.com/cover.jpg')
})

test('production HTML contains a working cover and canonical social image', () => {
  const html = readFileSync('docs/.vitepress/dist/capitulo-1.html', 'utf8')
  const prefix = process.env.VITEPRESS_BASE || base
  assert.match(html, new RegExp(`<img[^>]*src="${prefix}capitulo_1\\.jpg"[^>]*class="chapter-cover"`))
  assert.ok(existsSync('docs/.vitepress/dist/capitulo_1.jpg'))
  assert.match(html, /property="og:image" content="https:\/\/juninmd\.github\.io\/ecos-de-baia-cinzenta\/capitulo_1\.jpg"/)
})
