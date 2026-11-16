// Ponte entre a narração e o DOM da página: coleta frases, marca parágrafos e realça a frase lida.
import { splitSentences } from './sentences.mjs'

const SKIP = '.tts-marker, .cast-card'
const HIGHLIGHT = 'tts-sentence'

// Nós de texto do parágrafo, sem o botão ▶ e sem cartões de personagem.
export function textNodes(el) {
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, {
    acceptNode: (n) => (n.parentElement?.closest(SKIP) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT),
  })
  const nodes = []
  for (let n = walker.nextNode(); n; n = walker.nextNode()) nodes.push(n)
  return nodes
}

export function readableText(el) {
  return textNodes(el).map((n) => n.data).join('')
}

export function collectSegments(root = document) {
  const segments = []
  root.querySelectorAll('.vp-doc p').forEach((p) => {
    if (p.closest('.chapter-meta, .cast-dossier')) return
    splitSentences(readableText(p)).forEach((s) => segments.push({ ...s, element: p }))
  })
  return segments
}

// Converte posições de caractere no texto do parágrafo num Range do DOM.
export function rangeFor(el, start, end) {
  const range = document.createRange()
  let pos = 0
  let started = false
  for (const node of textNodes(el)) {
    const next = pos + node.data.length
    if (!started && start <= next) { range.setStart(node, Math.max(0, start - pos)); started = true }
    if (started && end <= next) { range.setEnd(node, Math.max(0, end - pos)); return range }
    pos = next
  }
  return started ? range : null
}

export function highlight(segment) {
  clearHighlight()
  if (!segment?.element) return
  segment.element.classList.add('active-reading')
  if (typeof CSS !== 'undefined' && CSS.highlights && typeof Highlight !== 'undefined') {
    const range = rangeFor(segment.element, segment.start, segment.end)
    if (range) CSS.highlights.set(HIGHLIGHT, new Highlight(range))
  }
}

export function clearHighlight() {
  if (typeof document === 'undefined') return
  document.querySelectorAll('.active-reading').forEach((el) => el.classList.remove('active-reading'))
  if (typeof CSS !== 'undefined' && CSS.highlights) CSS.highlights.delete(HIGHLIGHT)
}

// Marcador ▶ em cada parágrafo: "ouvir a partir daqui".
export function attachMarkers(segments, onPick) {
  const seen = new Set()
  segments.forEach((seg) => {
    if (seen.has(seg.element)) return
    seen.add(seg.element)
    if (seg.element.querySelector(':scope > .tts-marker')) return
    const marker = document.createElement('button')
    marker.type = 'button'
    marker.className = 'tts-marker'
    marker.textContent = '▶'
    marker.title = 'Ouvir a partir daqui'
    marker.setAttribute('aria-label', 'Ouvir a partir deste parágrafo')
    marker.addEventListener('click', (e) => { e.stopPropagation(); onPick(seg.element) })
    seg.element.appendChild(marker)
  })
}
