// Classifica os erros da Web Speech API. Só "interrompido/cancelado" é normal (nós mesmos
// cancelamos); erro de uma frase isolada pula a frase; o resto para a narração com aviso,
// em vez de "pular" o capítulo inteiro em segundos quando o aparelho não tem voz.
const IGNORE = new Set(['interrupted', 'canceled'])
const SKIP = new Set(['text-too-long', 'invalid-argument'])

const MESSAGES = {
  'not-allowed': 'O navegador bloqueou o áudio. Toque em ▶ de novo para começar.',
  'audio-busy': 'O áudio do aparelho está ocupado por outro app. Feche-o e toque em ▶.',
  'audio-hardware': 'Não encontrei saída de áudio neste aparelho.',
  network: 'A voz escolhida precisa de internet e a conexão falhou. Escolha outra voz ou tente de novo.',
}
export const NO_VOICE = 'Este navegador não tem voz instalada para narrar. Instale uma voz em português nas configurações do sistema e recarregue a página.'

export function speechErrorAction(code) {
  if (IGNORE.has(code)) return { action: 'ignore' }
  if (SKIP.has(code)) return { action: 'skip' }
  return { action: 'stop', message: MESSAGES[code] ?? NO_VOICE }
}

// Depois de algumas falhas seguidas, mesmo as "puláveis" viram parada: nunca varrer o capítulo.
export const MAX_SKIPS_IN_A_ROW = 3
