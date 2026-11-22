// Corta um parágrafo em frases para a narração, guardando onde cada uma começa e termina.
// As posições servem para marcar a frase exata no texto enquanto ela é lida.
const SENTENCE = /[^.?!…:;]+(?:[.?!…:;]+["”’»)]*|$)/g

// Ponto entre dígitos (3.500, 2.0) ou depois de título (Dra. Nádia) não encerra a frase.
const TITLE = /(?:^|[^\p{L}])(?:Dr|Dra|Sr|Sra|Srta|Prof|Profa)\.$/u
const continues = (src, end) =>
  (/\d\.$/.test(src.slice(0, end)) && /^\d/.test(src.slice(end))) || TITLE.test(src.slice(0, end))

export function splitSentences(text) {
  const src = String(text ?? '')
  const out = []
  let from = null
  for (const match of src.matchAll(SENTENCE)) {
    from ??= match.index
    const end = match.index + match[0].length
    if (end < src.length && continues(src, end)) continue
    const raw = src.slice(from, end)
    from = null
    const lead = raw.length - raw.trimStart().length
    const body = raw.trim()
    // Pontuação solta ou travessão sozinho não vira frase falada.
    if (!/[\p{L}\p{N}]/u.test(body)) continue
    const start = end - raw.length + lead
    out.push({ text: body, start, end: start + body.length })
  }
  return out
}

// Texto falado: travessão de diálogo vira pausa curta em vez de "menos".
export function speakable(text) {
  return String(text ?? '').replace(/\s*—\s*/g, ', ').replace(/^,\s*/, '').replace(/\s+/g, ' ').trim()
}
