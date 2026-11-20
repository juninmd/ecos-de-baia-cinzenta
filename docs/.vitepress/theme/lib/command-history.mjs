// Histórico de comandos do Lázaro, como num shell: ↑ volta, ↓ avança e termina no prompt vazio.
export function recall(history, cursor, dir) {
  const next = Math.min(Math.max(cursor + dir, 0), history.length)
  return { cursor: next, text: history[next] ?? '' }
}

/** O texto do prompt é o próprio item do histórico em que o cursor está (o usuário não editou). */
export const browsing = (history, cursor, text) => cursor < history.length && text === history[cursor]
