// Corta um parágrafo em frases para a narração, guardando onde cada uma começa e termina.
// As posições servem para marcar a frase exata no texto enquanto ela é lida.
const SENTENCE = /[^.?!…:;]+(?:[.?!…:;]+["”’»)]*|$)/g

export function splitSentences(text) {
  const out = []
  for (const match of String(text ?? '').matchAll(SENTENCE)) {
    const raw = match[0]
    const lead = raw.length - raw.trimStart().length
    const body = raw.trim()
    // Pontuação solta ou travessão sozinho não vira frase falada.
    if (!/[\p{L}\p{N}]/u.test(body)) continue
    const start = match.index + lead
    out.push({ text: body, start, end: start + body.length })
  }
  return out
}

// Texto falado: travessão de diálogo vira pausa curta em vez de "menos".
export function speakable(text) {
  return String(text ?? '').replace(/\s*—\s*/g, ', ').replace(/^,\s*/, '').replace(/\s+/g, ' ').trim()
}
