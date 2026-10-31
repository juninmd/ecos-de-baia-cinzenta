# Revisão de continuidade - 31/10/2026

## Método

Quatro leitores independentes cobriram os 239 capítulos em blocos (1-60, 61-120,
121-180, 181-236). Cada um leu o cânone antes da prosa: `GEMINI.md`, `docs/cronologia.md`,
`docs/personagens.md` e os dossiês, `docs/arcos.md` e as decisões já fechadas em
`editorial/auditoria-2026-10-23/correcoes-estado.md`.

Regra de aceitação: só entrou o que pudesse ser citado no texto e confrontado com outro
capítulo ou com a ficha. Fato ambíguo, hipérbole de personagem e margem de leitura foram
descartados. Cada correção preservou acontecimento, morte, ferimento e pista; nenhuma
cena foi inventada para "explicar" o que o texto já sustentava.

## Correções aplicadas

| # | Onde | Contradição | Correção |
| --- | --- | --- | --- |
| C01 | 47 x 41 | O 47 dizia que o Dilúvio "arrombou os diques"; o 41 estabelece que o dique não rompeu e que as comportas foram **operadas**. | "abriu as comportas do Distrito Baixo". |
| C02 | 47-54 | A *Caronte* fica no fosso da torre no 47 e reaparece na mão de Gabo no 54, sem cena de recuperação. | No 48, Val desce com a arma recuperada pela equipe de resgate. |
| C03 | 30.5-58 | Miranda é levado vivo por Silas no interlúdio e voltapreso no 58 com prótese nova, sem ponte. | No 58, a soltura duas semanas depois e a dívida com Silas. |
| C04 | 50-52 | O contrato de Clara é assinado quatro dias antes da morte de Helena, quando o anel norte já estava fechado. | O 51 explicita o coletor que subiu ao apartamento. |
| C05 | 2, 33, 41 | O *Cobalt* é a hidrogênio no 2, cheira a gasolina no 33 e a diesel no 41. | "Óleo quente" e "óleo queimado", sem trocar o motor. |
| C06 | 62, 70, 71 | O Santo mede 2,10 m no 62 e no 71 e 2,50 m no 70. | 2,10 m nos três. |
| C07 | 72, 73, 74 | A Torre tem 200 andares no 72, 182 no 73 e o heliponto a 230 m no 74. | 182 andares e heliponto a 630 m. |
| C08 | 80-81 | O registro de Nise marca 18h04 e o capítulo seguinte abre às 18h05, sem tempo para a fuga. | 18h20. |
| C09 | 96-103 | Silas é engolido pela árvore no 96 e aparece íntegro no Berçário no 103. | Silas paga a fala do 96: "Você me deixou uma raiz. Ela fez o resto." |
| C10 | 97-124 | A saída de voz de Aria é chamada de "reparada" no 113, antes do reparo do 124. | "Falhas da saída". |
| C11 | 120 | O drive de Aria está no estojo de Val e no bolso de Gabo na mesma cena; o palito de Rangel volta à boca depois de cair no 104. | O bolso é o do sobretudo; a boca está vazia, sem o palito. |
| C12 | 154-174 | A fratura é de antebraço fechada no 154/155, vira úmero no 170 e "exposta" no 173/174. | Antebraço no 170; fratura sem "exposta" nos dois últimos. |
| C13 | 161 | Gabo diz que Aria pesa 200 g; a ficha e o 170 dizem 45 g. | 45 g. |
| C14 | 148-162 | Val passa por um duto de 45 cm no 148 e objeta que precisaria deslocar os ombros no 162. | A objeção passa a ser equipamento e exaustão, não impossibilidade. |
| C15 | 162-163 | Os olhos de Val, prateados no 168, ficam "escuros" no 162/163. | Prateados nos dois. |
| C16 | 227 | Krell entra em 2024, aos 18; a empresa tinha 29 anos, não 27. | "Vinte e nove anos". |
| C17 | 233 x 45 | A distância entre Arca Zero e Ponto Zero era de 120 km; o Ponto Zero está a 200 km da costa. | "Duzentos quilômetros". |
| C18 | 233 x 72 | O ataque orbital é lembrado num "poço de ventilação do Distrito Industrial"; o 72 situa o poço no subsolo da Torre, no Distrito Central. | "Subsolo da Torre Aeterna". |

## Fichas alinhadas à prosa

- **Kiko Vibe:** a ficha dizia morte na Parte IV e transmissão ao vivo; o capítulo 8 diz
  que a transmissão não começou e situa a morte na Parte III. A ficha passou a registrar
  a gravação pelos implantes, não uma transmissão que o texto nega.
- **Silas Vance:** o interlúdio 30.5 é a primeira aparição, em flash-forward. A ficha
  agora diz isso, em vez de apresentá-lo como estreia na Parte XII.

## Achados examinados e mantidos

| Onde | Por que não mudou |
| --- | --- |
| 190 x 191 | "Centenas" de corpos suspensos e "dezenas" de bio-baterias ativas são conjuntos distintos; o texto não iguala os dois. |
| 229 | Braga saber do término de Bia é sustentado pela fala dele ("cadeia é cheia de gente com tempo") e por inimigos de Gabo; não é conhecimento impossível. |
| 148 | Val é descrita como leve e passa pelo duto; o 162 agora cobra o equipamento, não a anatomia. |
| 45 | Ponto Zero a 200 km da costa permanece a âncora; o 233 foi corrigido para ela. |

## Evidência

```powershell
uv run --no-sync python scripts/quality_gate.py   # 239 capítulos, 0 reprovados, média 8,9
uv run --no-sync python -m pytest tests/ -q       # 1024 passed
git diff --check                                  # sem erro de espaço
```

## Limites

- A leitura foi dividida entre quatro revisores; ela cobre os 239 capítulos, mas não
  substitui uma leitura linear única do livro inteiro.
- As correções são mínimas: nenhuma trama, morte, ferimento ou pista foi alterada.
- O que ficou aberto é decisão editorial, não erro demonstrado - e está listado acima
  para não ser confundido com aprovação silenciosa.
