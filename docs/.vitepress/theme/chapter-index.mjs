// Ordem dos capítulos lida do menu: a navegação nunca depende de um limite fixo.
const CHAPTER_LINK = /^\/capitulo-(\d+)\/?$/

export function buildChapterIndex(sidebar) {
  const found = new Map()
  const walk = (nodes) => {
    for (const node of Array.isArray(nodes) ? nodes : []) {
      const match = typeof node?.link === 'string' && CHAPTER_LINK.exec(node.link)
      if (match) found.set(Number(match[1]), { number: Number(match[1]), title: node.text, link: `/capitulo-${match[1]}` })
      walk(node?.items)
    }
  }
  walk(Array.isArray(sidebar) ? sidebar : Object.values(sidebar ?? {}).flat())
  return [...found.values()].sort((a, b) => a.number - b.number)
}

export function neighbors(index, number) {
  const pos = index.findIndex((c) => c.number === number)
  if (pos === -1) return { prev: null, next: null }
  return { prev: index[pos - 1] ?? null, next: index[pos + 1] ?? null }
}
