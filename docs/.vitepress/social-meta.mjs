// Origem pública do site (README). og:image e og:url precisam de URL absoluta.
export const SITE_ORIGIN = 'https://juninmd.github.io/ecos-de-baia-cinzenta'
const SITE_NAME = 'Ecos de Baía Cinzenta'

export function socialMeta({ page, title, description, pageData }) {
  const image = pageData.frontmatter?.image
  const path = page.replace(/(^|\/)index\.md$/, '$1').replace(/\.md$/, '')
  const site = new URL(`${SITE_ORIGIN}/`)
  const absoluteImage = image ? new URL(image.startsWith(site.pathname) || image.startsWith('//') ? image : image.replace(/^\//, ''), site).href : null

  const tags = [
    ['meta', { property: 'og:site_name', content: SITE_NAME }],
    ['meta', { property: 'og:title', content: title || SITE_NAME }],
    ['meta', { property: 'og:description', content: description || '' }],
    ['meta', { property: 'og:url', content: `${SITE_ORIGIN}/${path}` }],
    ['meta', { name: 'twitter:card', content: absoluteImage ? 'summary_large_image' : 'summary' }],
  ]
  if (absoluteImage) tags.push(['meta', { property: 'og:image', content: absoluteImage }])
  return tags
}
