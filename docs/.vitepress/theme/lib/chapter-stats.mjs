// Lê um capítulo-fonte e devolve o que a home precisa: número, título, palavras e capa.
const FRONTMATTER = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/

export function chapterStats(file, source) {
  const n = Number(/capitulo-(\d+)\.md$/.exec(file)?.[1])
  if (!Number.isInteger(n)) return null
  const fm = FRONTMATTER.exec(source)
  const body = fm ? source.slice(fm[0].length) : source
  const image = fm && /^image:\s*["']?([^"'\s]+)/m.exec(fm[1])?.[1]
  const title = /^#\s+Cap[íi]tulo\s+\d+\s*:\s*(.+)$/m.exec(body)?.[1]?.trim() ?? `Capítulo ${n}`
  const words = body.replace(/^#.*$/gm, '').split(/\s+/).filter((w) => /[\p{L}\p{N}]/u.test(w)).length
  return { n, title, words, image: image || null }
}
