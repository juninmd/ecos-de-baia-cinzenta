// Dados e comandos do Terminal Lázaro. Tudo filtra pelo capítulo mais avançado já lido,
// para o terminal nunca entregar o que o leitor ainda não chegou a ver.
export const BOOKS = [
  [1, 106, 'Livro 1: O Dilúvio'],
  [107, 186, 'Livro 2: A Ascensão'],
  [187, 240, 'Livro 3: A Prova'],
  [241, 999, 'Livro 4: O Contraditório'],
]

const REVEAL = { genesis: 106, bercario: 106, dante: 106, mesa: 245 }

// Estados por capítulo, conferidos nos dossiês (docs/personagens/*.md).
export const CAST = [
  { nome: 'MORETTI, GABRIEL', desde: 1, estados: [
    { de: 1, rotulo: 'ATIVO', tom: 'text', papel: 'Detetive Particular' },
    { de: 245, rotulo: 'RÉU DA MESA', tom: 'warning', papel: 'Primeiro réu da Carta' }] },
  { nome: 'CRUZ, VALÉRIA', desde: 3, estados: [{ de: 3, rotulo: null, tom: 'text', papel: 'Analista de redes' }] },
  { nome: 'ARIA', desde: 2, estados: [
    { de: 2, rotulo: 'SISTEMA', tom: 'text', papel: 'Entidade Digital' },
    { de: 170, rotulo: 'DESTRUÍDA', tom: 'danger', papel: 'Entidade Digital' }] },
  { nome: 'VILAR, CAPITÃO', desde: 3, estados: [
    { de: 3, rotulo: 'ATIVO', tom: 'text', papel: 'Resistência' },
    { de: 252, rotulo: 'FALECIDO', tom: 'danger', papel: 'Resistência' }] },
  { nome: 'RANGEL, INSPETOR', desde: 2, estados: [
    { de: 2, rotulo: 'ATIVO', tom: 'text', papel: 'Polícia' },
    { de: 152, rotulo: 'FALECIDO', tom: 'danger', papel: 'Polícia' }] },
  { nome: 'MORETTI, MARCO', desde: 4, estados: [
    { de: 4, rotulo: 'ATIVO', tom: 'text', papel: 'Administrador' },
    { de: 244, rotulo: 'RÉU DA MESA', tom: 'warning', papel: 'Doze co-assinaturas' }] },
  { nome: 'MORETTI, DANTE (original)', desde: 3, estados: [
    { de: 3, rotulo: 'DESAPARECIDO', tom: 'warning', papel: 'Ex-comissário' },
    { de: 27, rotulo: 'FALECIDO', tom: 'danger', papel: 'Ex-comissário' }] },
  { nome: 'BIO-DANTE', desde: 105, estados: [
    { de: 105, rotulo: 'ATIVO', tom: 'warning', papel: 'Cópia (biohost)' },
    { de: 254, rotulo: 'FALECIDO', tom: 'danger', papel: 'Cópia (biohost)' }] },
  { nome: 'MORETTI, ELENA', desde: 14, estados: [
    { de: 14, rotulo: 'ATIVA', tom: 'text', papel: 'Jornalista' },
    { de: 239, rotulo: 'FALECIDA', tom: 'danger', papel: 'Jornalista' }] },
  { nome: 'PRADO, TERESA "TÊ"', desde: 245, estados: [{ de: 245, rotulo: 'ATIVA', tom: 'text', papel: 'Preside a Mesa' }] },
]

export function bookAt(chapter) {
  return (BOOKS.find(([a, b]) => chapter >= a && chapter <= b) ?? BOOKS[0])[2]
}

export function stateAt(person, chapter) {
  return [...person.estados].reverse().find((s) => chapter >= s.de) ?? null
}

const denied = (need) => ({ lines: [
  { type: 'error', text: 'ACESSO NEGADO: nível de leitura insuficiente.' },
  { type: 'info', text: `Arquivo liberado a partir do capítulo ${need}. Continue lendo.` }] })

export const COMMAND_NAMES = ['help', 'status', 'personagens', 'genesis', 'bercario', 'dante', 'mesa', 'ir', 'clear', 'exit']
const ALIAS = { ajuda: 'help', sair: 'exit', limpar: 'clear', ls: 'personagens' }

export function runCommand(raw, { chapter = 1, total = 1, hacked = false } = {}) {
  const [word, ...rest] = raw.trim().toLowerCase().split(/\s+/)
  const name = ALIAS[word] ?? word
  if (REVEAL[name] && chapter < REVEAL[name]) return denied(REVEAL[name])
  switch (name) {
    case 'help':
      return { lines: [{ type: 'info', text: 'Comandos Disponíveis:' }, ...[
        'status       - Onde você está na história',
        'personagens  - Cidadãos que você já conheceu',
        'ir <número>  - Abrir um capítulo (ex.: ir 250)',
        'genesis      - [RESTRITO] Arquivos do projeto',
        'mesa         - [RESTRITO] Mesa de Fé Pública',
        'clear / exit - Limpar / encerrar'].map((text) => ({ type: 'cmd-list', text: '  ' + text })),
        { type: 'info', text: 'Dica: Tab completa o comando; ↑ e ↓ repetem os anteriores.' }] }
    case 'status':
      return { lines: [{ type: 'success', text: '>> ANALISANDO SISTEMAS...' },
        { type: 'text', text: `Leitura registrada: capítulo ${chapter} de ${total}` },
        { type: 'text', text: bookAt(chapter) },
        ...(chapter < 107 ? [{ type: 'danger', text: 'Ameaça Biológica: DETECTADA (Setor 4)' }] : [])] }
    case 'personagens': {
      const lines = CAST.filter((p) => chapter >= p.desde).map((p) => {
        const s = stateAt(p, chapter)
        return { type: s.tom, text: `${p.nome}${s.rotulo ? ` [${s.rotulo}]` : ''} - ${s.papel}` }
      })
      return { lines: [{ type: 'info', text: '>> ACESSANDO ARQUIVOS DA POLÍCIA...' }, ...lines] }
    }
    case 'genesis':
      return { lines: [{ type: 'danger', text: '>> ALERTA DE SEGURANÇA: ACESSO RESTRITO' }, { type: 'text', text: 'Descriptografando...' },
        { type: 'system', text: 'O Projeto Genesis não era sobre salvar a cidade.' },
        { type: 'system', text: 'Era sobre transformar a carne em armazenamento.' },
        { type: 'system', text: 'Nós somos o backup.' }] }
    case 'bercario':
      return { lines: [{ type: 'success', text: '>> ACESSO CONCEDIDO: NÍVEL 0' },
        { type: 'danger', text: 'AVISO: CONTAMINAÇÃO BIOLÓGICA DETECTADA' },
        { type: 'system', text: 'Localização: Subsolo da Linha Vermelha' }, { type: 'text', text: 'Status dos Tanques: ATIVOS' },
        { type: 'warning', text: 'Mensagem de Elara Vance: "Eles têm fome."' }, { type: 'text', text: 'Dica: O silêncio é a chave.' }] }
    case 'mesa':
      return { lines: [{ type: 'info', text: '>> MESA DE FÉ PÚBLICA // REGISTRO' },
        { type: 'text', text: 'Presidente: Teresa "Tê" Prado.' },
        { type: 'text', text: 'Réus: Gabo (primeiro réu da Carta) e Marco (doze co-assinaturas).' },
        ...(chapter >= 255 ? [{ type: 'warning', text: 'Marco: julgado sem voto e sem selo próprio.' }] : []),
        { type: 'system', text: 'Nenhum papel se autentica sozinho.' }] }
    case 'dante':
      return { hacked: true, lines: [{ type: 'danger', text: '>> PROTOCOLO DE SUBSTITUIÇÃO INICIADO' },
        { type: 'system', text: 'Acessando infraestrutura da cidade...' }, { type: 'success', text: '[OK] Câmeras de Vigilância' },
        { type: 'success', text: '[OK] Controle de Tráfego' }, { type: 'success', text: '[OK] Redes Elétricas' },
        { type: 'warning', text: 'Dante Moretti: "A ordem foi restaurada. Não há necessidade de medo. Apenas obediência."' },
        { type: 'system', text: 'Modo Administrador: ATIVO' }] }
    case 'protocolo_final':
      return hacked
        ? { lines: [{ type: 'danger', text: '>> EXECUTANDO O SILÊNCIO DE CONCRETO...' },
          { type: 'text', text: 'Todos os canais de comunicação não-governamentais serão encerrados em T-minus 10...' }] }
        : { lines: [{ type: 'error', text: 'Acesso Negado. Requer privilégios de Administrador (Dante).' }] }
    case 'ir': {
      const n = Number(rest[0])
      return Number.isInteger(n) && n >= 1 && n <= Math.min(chapter + 1, total)
        ? { go: n, lines: [{ type: 'success', text: `>> Abrindo capítulo ${n}...` }] }
        : { lines: [{ type: 'error', text: `Capítulo inválido ou ainda não lido. Use: ir 1 a ${Math.min(chapter + 1, total)}.` }] }
    }
    case 'clear': return { clear: true, lines: [] }
    case 'exit': return { close: true, lines: [] }
    default: return { lines: [{ type: 'error', text: `Comando não reconhecido: ${word}` }] }
  }
}

export function complete(prefix) {
  const p = prefix.trim().toLowerCase()
  return p ? COMMAND_NAMES.filter((c) => c.startsWith(p)) : []
}
