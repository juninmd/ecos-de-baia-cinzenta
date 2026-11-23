# Revisão para publicação - 23/11/2026

## Aria só aparece em luz três vezes

Decisão do autor: a IA de Gabo não aparece visualmente, exceto em no máximo três
hologramas, e o primeiro o assusta.

| Capítulo | Holograma |
| --- | --- |
| 57 | Primeira vez. Surge do console do *Cobalt* sem aviso; Gabo recua, leva a mão ao coldre e manda desligar. Pede que ela avise antes da próxima. |
| 136 | Depois do reinício, ela avisa e projeta o próprio rosto diante da réplica de Bia, para as câmeras do Taxidermista. |
| 168 | Despedida do tamanho de uma mão, no deck de Val, antes do terminal. Gabo não recua. |

Também mudou: o rosto no visor da cabine (2) virou onda sonora; 169 e 228 passam a
dizer "três vezes". O dossiê (`docs/aria.md`, `docs/personagens/aria.md`) e o
pipeline de arte (`scripts/art_gen/aria_visual.py`) seguem a regra: fora de 57, 136
e 168, nenhuma cena ou capa usa o retrato da Aria, e o prompt manda mostrar só o drive.
Os manifestos de cenas e capas pendentes foram regenerados com a regra.

## Varredura de erros (1-256)

- Ortografia por dicionário (palavras raras fora do léxico) e padrões mecânicos
  (palavra repetida, espaços, pontuação dupla, crase, "haviam/fazem"): o texto está
  limpo. Corrigidos: "sorda" (206), "zumbeou" (176), "encrustada" (203),
  "autofalante" (183), "tecleando" (113), "tipóia" → "tipoia" (4 casos).
- `quality_gate.py`: 0 reprovados, média 8,8; capítulo 244 é o único em "revisar".

## O que ainda impede chamar de pronto

1. **Prosa desigual.** 111-227 tem cerca de 5x mais clichês de intensidade
   ("brutal", "visceral", "a hacker", "o detetive", "inferno"...) por 10 mil palavras
   do que 1-110 e 228-256. Esse trecho precisa de uma revisão de linha como a que o
   início e o Livro 4 já receberam.
2. **Narrador muda** de terceira para primeira pessoa no 172. É intencional
   (`REVISAO-historico.md`), mas o leitor não recebe sinal disso; uma abertura de
   parte ou um prólogo de Gabo resolveria.
3. **Tamanho.** ~342 mil palavras. Publicar em quatro volumes (1-106, 107-186,
   187-240, 241-256) é mais viável que um livro só; o Livro 4 é curto e de outro
   gênero (tribunal).
4. **Voz da Aria em 140-169** às vezes soa robótica ("sem qualquer modulação
   emocional"), em atrito com o dossiê (serena, humor seco).
5. Não houve leitura linear integral nesta passada: as checagens foram automáticas,
   mais leitura dos trechos alterados, da abertura e do final.

## Revisão de linha 111-227 (pedido do autor, mesmo dia)

- Cerca de 490 trechos reescritos em 107 capítulos: intensificadores ("brutal",
  "visceral", "colossal", "absoluto", "violentamente", "freneticamente", "inferno"),
  epítetos ("a hacker", "o detetive", "olhos prateados" de 49 para 5), verbos de
  fala exagerados ("rosnou", "berrou", "cuspiu") e símiles de efeito.
- Voz da Aria em 136-169: tirados "monótona", "sem qualquer modulação emocional",
  "frieza cirúrgica/matemática"; ela volta a soar calma, não robótica.
- 172: uma linha explícita marca a passagem para a primeira pessoa
  ("Dali em diante, quem conta sou eu").
- Foi uma passada por padrões, frase a frase nos trechos marcados; não reescreveu
  cenas inteiras nem mudou trama.
