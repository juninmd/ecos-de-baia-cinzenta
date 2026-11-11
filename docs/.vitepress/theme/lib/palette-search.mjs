// Busca da paleta Lázaro: comandos do terminal, capítulos, personagens e páginas de arquivo.
// Respeita a mesma trava do terminal: capítulos só até o seguinte ao mais avançado já lido.
import { COMMAND_NAMES } from '../terminal-lore.mjs'

export const COMMAND_HINTS = {
  help: 'Lista de comandos', status: 'Onde você está na história', personagens: 'Cidadãos que você já conheceu',
  ir: 'Abrir um capítulo · ir 12', genesis: '[RESTRITO] Arquivos do projeto', bercario: '[RESTRITO] Subsolo',
  dante: '[RESTRITO] Protocolo de substituição', mesa: '[RESTRITO] Mesa de Fé Pública',
  clear: 'Limpar a tela', exit: 'Fechar o Lázaro',
}

export const fold = (s) => String(s ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim()
const LIMIT = 8

export function searchPalette(query, { chapters = [], cast = [], pages = [], furthest = 1 } = {}) {
  const q = fold(query)
  const limit = Math.min(furthest + 1, chapters.at(-1)?.number ?? furthest + 1)
  const open = (c) => c.number <= limit
  if (!q) {
    const resume = chapters.find((c) => c.number === furthest)
    return [
      ...(resume ? [{ group: 'Sugestões', kind: 'chapter', label: `Continuar · Cap. ${resume.number}`, hint: resume.title, run: `ir ${resume.number}` }] : []),
      { group: 'Sugestões', kind: 'command', label: 'status', hint: COMMAND_HINTS.status, run: 'status' },
      { group: 'Sugestões', kind: 'command', label: 'help', hint: COMMAND_HINTS.help, run: 'help' },
    ]
  }
  const [word, ...rest] = q.split(/\s+/)
  const out = COMMAND_NAMES.filter((c) => c.startsWith(word))
    .map((c) => ({ group: 'Comandos', kind: 'command', label: rest.length && c === word ? q : c, hint: COMMAND_HINTS[c] ?? '', run: rest.length && c === word ? q : c }))
  if (/^\d+$/.test(q)) {
    const c = chapters.find((ch) => ch.number === Number(q))
    if (c) out.push(open(c)
      ? { group: 'Capítulos', kind: 'chapter', label: `Cap. ${c.number} · ${c.title}`, hint: 'Abrir', run: `ir ${c.number}` }
      : { group: 'Capítulos', kind: 'locked', label: `Cap. ${c.number} · ainda não lido`, hint: 'Bloqueado', run: `ir ${c.number}` })
  } else {
    chapters.filter((c) => open(c) && fold(c.title).includes(q)).slice(0, LIMIT)
      .forEach((c) => out.push({ group: 'Capítulos', kind: 'chapter', label: `Cap. ${c.number} · ${c.title}`, hint: `Capítulo ${c.number}`, run: `ir ${c.number}` }))
  }
  cast.filter((p) => !p.locked && fold(p.nome).includes(q)).forEach((p) =>
    out.push({ group: 'Personagens', kind: 'person', label: p.nome, hint: p.papel, link: `/personagens#${p.anchor}` }))
  pages.filter((p) => fold(p.text).includes(q)).forEach((p) =>
    out.push({ group: 'Arquivos', kind: 'page', label: p.text, hint: 'Página', link: p.link }))
  return out
}

// Título do menu vem como "Capítulo 12: Shadowban"; a paleta mostra só o nome.
export const chapterTitle = (text) => String(text ?? '').replace(/^Cap[íi]tulo\s+\d+\s*:\s*/i, '')

// Páginas de arquivo (tudo no menu que não é capítulo), para a busca da paleta.
export function archivePages(sidebar) {
  const out = []
  const walk = (nodes) => (Array.isArray(nodes) ? nodes : []).forEach((n) => {
    if (typeof n?.link === 'string' && !/^\/capitulo-\d+/.test(n.link)) out.push({ text: n.text, link: n.link })
    walk(n?.items)
  })
  walk(Array.isArray(sidebar) ? sidebar : Object.values(sidebar ?? {}).flat())
  return out.filter((p, i) => out.findIndex((q) => q.link === p.link) === i)
}
