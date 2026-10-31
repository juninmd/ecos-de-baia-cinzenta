# Revisão de ganchos - 31/10/2026

## Escopo e método

Leitura dos 239 capítulos com uma triagem nova (`scripts/auditoria_ganchos.py`) que mede
duas coisas por capítulo: a abertura (prende na primeira frase?) e o fecho (vira a página
sem resumir o que acabou de acontecer?). O relatório completo fica em
`docs/auditoria_ganchos.md`.

A triagem é heurística: ela marca fórmulas de abertura ("o silêncio não era X; era Y"),
travessias no fecho, resumos de percepção e fechos longos. Uma nota baixa não reescreve
um capítulo sozinha; ela só indica onde a leitura manual começa. Dos 44 capítulos
marcados na primeira passada, 19 continuam marcados - quase todos por abertura longa,
não por gancho fraco. Foram corrigidos os que tinham fecho genérico ou abertura travada
por metadado.

## O que mudou

| Cap. | Antes | Depois |
| --- | --- | --- |
| 73 | Terminava na logística do elevador de manutenção. | Termina nos 182 andares que separam Gabo do helicóptero. |
| 81 | Explicação temática de Gabo sobre a evolução. | Termina na pergunta de Vilar - "Quantos prédios?" - sem resposta. |
| 90 | Abertura em um parágrafo único de 169 palavras. | Mesma matéria, dividida em três parágrafos com respiração. |
| 119 | "Três sobreviventes... mancando na escuridão". | O peso do cilindro de Aria e as luzes da Prometeu que não voltam. |
| 125 | Ordem logística sobre a maca de Rangel. | Termina na revelação: "A energia não voltou. A *Ordem* voltou." |
| 126 | "O dia estava apenas começando". | Rangel para de responder antes da segunda curva. |
| 130 | Bloco de metadados repetindo o frontmatter. | Abre na usina ainda trabalhando; fecha na fala de Aria. |
| 140 | "O fogo real da subida mal havia começado". | Fecha na correção de Aria: a saída é subir, e a rede tem assinatura. |
| 144 | Abertura e fecho presos na fórmula do silêncio. | Abre no mosquetão que puxa o cinto; mantém o custo físico. |
| 156 | "A verdadeira caçada ainda não havia começado". | Fecha no destino concreto: a curadoria prometida do Taxidermista. |
| 157 | "A caçada não acabou". | Fecha na ordem de Gabo: "Ainda não chegamos no topo." |
| 161 | Fecho em "o pesadelo ainda não acabou". | Fecha na ordem de Val e no corredor que engole a lanterna. |
| 165 | Abertura na negação "não era a escuridão...". | Abre em cinco graus acima de zero e no breu matemático. |
| 170 | "Só restava a conta a pagar na superfície". | Fecha no pé de cabra torto e no silêncio do Setor Alfa-Sete. |
| 181 | Abertura descrevendo a escuridão. | Abre na fala de Val: "Parou." |
| 207 | Abertura na negação "não era apenas falta de luz". | Abre no duto de um metro e vinte. |
| 212 | Abertura descritiva antes de qualquer fala. | Abre na fala de Val sobre o vão fechado. |

## Evidência

```powershell
uv run --no-sync python scripts/auditoria_ganchos.py   # 239 capítulos, 19 marcados
uv run --no-sync python scripts/quality_gate.py        # 239 capítulos, 0 reprovados, média 8,9
uv run --no-sync python -m pytest tests/ -q            # 1025 passed
git diff --check                                       # sem erro de espaço
```

## Limites

- A triagem não mede tensão dramática; ela mede superfície. Um capítulo marcado pode ter
  um gancho bom e uma abertura longa, e foi mantido quando a leitura não encontrou problema.
- A revisão não reescreveu cenas nem mudou acontecimentos, mortes, ferimentos ou pistas.
- Fechos de arco (119, 151) continuam sendo fechos de arco; a correção foi tornar a imagem
  concreta, não inventar uma reviravolta nova.
