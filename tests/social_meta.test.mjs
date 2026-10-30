// Pina as meta tags de compartilhamento: og:image precisa ser URL absoluta.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { socialMeta, SITE_ORIGIN } from '../docs/.vitepress/social-meta.mjs'

const tagsFor = (ctx) => Object.fromEntries(
  socialMeta(ctx).map(([, attrs]) => [attrs.property ?? attrs.name, attrs.content]),
)

test('capítulo com capa: og:image absoluta e card grande', () => {
  const tags = tagsFor({
    page: 'capitulo-1.md',
    title: 'Capítulo 1: Chuva',
    description: 'Primeiro capítulo',
    pageData: { frontmatter: { image: '/capitulo_1.jpg' } },
  })
  assert.equal(tags['og:image'], `${SITE_ORIGIN}/capitulo_1.jpg`)
  assert.equal(tags['og:url'], `${SITE_ORIGIN}/capitulo-1`)
  assert.equal(tags['og:title'], 'Capítulo 1: Chuva')
  assert.equal(tags['twitter:card'], 'summary_large_image')
})

test('página sem capa: sem og:image e card pequeno', () => {
  const tags = tagsFor({ page: 'arcos.md', title: 'Arcos', description: '', pageData: { frontmatter: {} } })
  assert.equal('og:image' in tags, false)
  assert.equal(tags['twitter:card'], 'summary')
  assert.equal(tags['og:title'], 'Arcos')
})

test('index.md vira a raiz do site', () => {
  const tags = tagsFor({ page: 'index.md', title: 'Início', description: '', pageData: { frontmatter: {} } })
  assert.equal(tags['og:url'], `${SITE_ORIGIN}/`)
})

 test('capa com prefixo do Pages mantém URL social correta', () => {
  const tags = tagsFor({ page: 'capitulo-1.md', title: '', description: '', pageData: { frontmatter: { image: '/ecos-de-baia-cinzenta/capitulo_1.jpg' } } })
  assert.equal(tags['og:image'], `${SITE_ORIGIN}/capitulo_1.jpg`)
})
