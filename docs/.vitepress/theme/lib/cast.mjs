// Elenco visível do site: une o estado por capítulo do Lázaro (terminal-lore) ao retrato canônico
// do dossiê. Nada aqui aparece antes do capítulo em que o personagem entra (trava de spoiler).
import { CAST, stateAt } from '../terminal-lore.mjs'

// Retratos conferidos em docs/personagens/*.md; fases seguem a "Linha do Tempo e Evolução Visual".
export const PORTRAITS = {
  'MORETTI, GABRIEL': { nome: 'Gabriel "Gabo" Moretti', anchor: 'gabriel-gabo-moretti', alias: ['Gabo'], fases: [[1, '/personagens/gabo.jpg']] },
  'CRUZ, VALÉRIA': { nome: 'Valéria "Val" Cruz', anchor: 'valeria-val-cruz', alias: ['Valéria'], fases: [[1, '/personagens/val.png']] },
  ARIA: { nome: 'Aria', anchor: 'aria', alias: ['Aria'], fases: [[1, '/personagens/aria_3.png']] },
  'VILAR, CAPITÃO': { nome: 'Capitão Jonas Vilar', anchor: 'capitao-jonas-vilar', alias: ['Vilar'], fases: [[1, '/personagens/jonas.jpg']] },
  'RANGEL, INSPETOR': { nome: 'Inspetor Rangel', anchor: 'inspetor-rangel', alias: ['Rangel'], fases: [[1, '/personagens/rangel.png']] },
  'MORETTI, MARCO': { nome: 'Marco Moretti', anchor: 'marco-moretti', alias: ['Marco'], fases: [[1, '/personagens/marco.png']] },
  'MORETTI, DANTE (original)': { nome: 'Dante Moretti', anchor: 'dante-moretti', alias: ['Dante Moretti'], ate: 104, fases: [[1, '/personagens/dante.jpg']] },
  'BIO-DANTE': { nome: 'Bio-Dante', anchor: 'bio-dante', alias: ['Bio-Dante'], fases: [[1, '/personagens/bio_dante.png']] },
  'MORETTI, ELENA': { nome: 'Elena Moretti', anchor: 'elena-moretti', alias: ['Elena'], fases: [[1, '/personagens/elena.png'], [104, '/personagens/elena_2.png']] },
  'PRADO, TERESA "TÊ"': { nome: 'Teresa "Tê" Prado', anchor: 'teresa-te-prado', alias: ['Teresa'], fases: [[1, '/personagens/te.png']] },
}

const portraitAt = (fases, chapter) => [...fases].reverse().find(([de]) => chapter >= de)?.[1] ?? fases[0][1]

// Todo o elenco, com estado no capítulo e flag de bloqueio (ainda não apareceu).
export function castAt(chapter) {
  return CAST.filter((p) => PORTRAITS[p.nome]).map((p) => {
    const meta = PORTRAITS[p.nome]
    const state = stateAt(p, chapter)
    return {
      key: p.nome, nome: meta.nome, anchor: meta.anchor, desde: p.desde,
      locked: chapter < p.desde,
      rotulo: state?.rotulo ?? null, tom: state?.tom ?? 'text', papel: state?.papel ?? '',
      retrato: portraitAt(meta.fases, chapter),
      alias: meta.ate && chapter > meta.ate ? [] : meta.alias,
    }
  })
}

// Primeira menção de cada personagem já apresentado, para o cartão ao toque no texto.
// Apelidos com menos de 4 letras ficam de fora (AGENTS.md: "O" sequestra o ranking).
export function aliasPattern(cast) {
  const names = cast.filter((c) => !c.locked).flatMap((c) => c.alias).filter((a) => a.length >= 4)
  if (!names.length) return null
  const alt = names.sort((a, b) => b.length - a.length).map((a) => a.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')
  return new RegExp(`(?<![\\p{L}-])(${alt})(?![\\p{L}-])`, 'u')
}
