# Continuidade por capítulo

## Fontes e divergências

`AGENTS.md` fixa as restrições editoriais e de identidade. `GEMINI.md` orienta o
tom; `docs/personagens.md` é a fonte da verdade para personagens, inclusive suas
linhas de evolução. `docs/arcos.md` organiza o desenho do livro. Consulte também
`docs/cronologia.md`, mas confirme eventos nos capítulos correspondentes.

Resumos não têm necessariamente a mesma data de atualização. No estado examinado
em 2026-10-20, `GEMINI.md` contém uma tabela intitulada pós-capítulo 109 que também
inclui a morte de Elena no 235, além de descrições divergentes da fase de Valéria.
Não transforme a posição de um parágrafo ou a palavra "atual" em regra temporal.

Quando houver conflito, registre as duas afirmações e suas passagens; confira a
linha de evolução do dossiê e a cena publicada. Uma contradição não vira licença
para escolher silenciosamente a versão mais conveniente. Se a evidência não
resolver um fato essencial, continue apenas o trabalho que não depende dele e
peça a decisão editorial específica. Não reescreva o passado inteiro por inferência.

## Estado de entrada e de saída

Para o capítulo N, leia N−1 e N; em revisão, leia também N+1 quando existir.
Inclua intercalações, como `capitulo-75.5.md`, na ordem real. Leia os capítulos
anteriores citados por uma revelação, mesmo que estejam longe desse intervalo.

| Dimensão | Registrar com capítulo e passagem |
| --- | --- |
| Tempo e espaço | Dia, hora relativa, duração, deslocamento, marés ou prazos relevantes |
| Corpo | Ferimentos, amputação, braço funcional, órtese, tipoia, exoesqueleto, fadiga |
| Identidade | Aparência canônica, fase do corpo e marcas distintivas |
| Recursos | Armas, munição, documentos, hardware, energia, posse e transferência |
| Conhecimento | Quem descobriu o quê; quem apenas suspeita; acesso ao registro |
| Vínculos | Confiança, dívida, promessa, medo ou perda que altera a próxima escolha |
| Investigação | Pistas abertas, hipóteses derrubadas, provas e ameaça em andamento |

Escreva a transição `entrada -> evento demonstrado -> saída`. Toda recuperação,
transferência de objeto ou conhecimento precisa de uma causa e de tempo possível.
O parecer pode usar referências ao futuro para preservar a continuidade da revisão;
o personagem e a prosa não podem conhecer esse futuro.

## Invariantes que exigem leitura de época

- Gabo nunca fuma. Distinguir recusa, lembrança e fumaça ambiente de uma ação dele.
- Caronte e Leviatã são os nomes canônicos das armas. Ter uma arma no inventário
  de referência não significa que Gabo ainda a possui naquela cena.
- Aria opera em hardware físico: verificar conexão, energia e fase. O dossiê marca
  a destruição do pendrive no capítulo 167; referências posteriores não permitem
  devolver a assistente ativa ao grupo sem uma mudança canônica expressamente autorizada.
- Bio-Dante não equivale ao Dante original. Verificar limites de memória e fatos
  que ele teve oportunidade de aprender, em vez de lhe dar conhecimento universal.
- Elena tem um destino registrado nos capítulos 234–236. Uma revisão anterior
  não a trata como morta antes do acontecimento; uma continuação posterior não
  a põe agindo viva no presente. Memória, gravação e flashback precisam ser legíveis.

Não memorize esta lista como retrato permanente da obra: volte ao dossiê e aos
capítulos quando o projeto avançar. As referências acima indicam onde verificar.

## Checagem de tempo e causalidade

Construa uma linha curta dos eventos antes de conferir adjetivos ou frases:

```text
Hora/dia de entrada:
Viagem e duração:
Ação e recuperação necessárias:
Hora/dia de saída:
Prazo mencionado:
O prazo ainda é possível? Evidência:
```

Procure relações como tarde/amanhecer, hoje/amanhã, antes/depois, distância/tempo.
Uma frase isolada pode parecer correta e contradizer a hora estabelecida na cena.
Não corrija um marcador sem verificar se ele é literal, retrospectivo ou figurado.

## Forma do capítulo

O arquivo é `docs/capitulo-N.md`, com exatamente um H1 no formato
`# Capítulo N: Título`. Compare seu texto ao item correspondente em
`docs/.vitepress/config.ts`. Ao criar um capítulo, adicione seu item no arco certo;
não renumere os já publicados nem use os caminhos antigos de instruções defasadas.

O bloco de metadados precisa de `Localização` e `Personagens Presentes`.
Preserve o frontmatter e seus ativos na revisão. Não invente caminho de imagem
nem rode geração visual para satisfazer uma tarefa apenas literária.
Declaração de elenco não é lista de toda pessoa citada: diferencie presença
física, comunicação e lembrança, respeitando o padrão adotado para a cena.

Conte as palavras da narrativa sem frontmatter, título e notas editoriais:
mínimo de 600; alvo de 1.100–1.600. Expanda conflito, observação e consequência,
não recapitulações nem descrições redundantes para atingir uma contagem.

Se precisar registrar plantios ou mudanças, acrescente somente fatos confirmados
ao dossiê apropriado. Não apague detalhes anteriores nem altere retratos de
referência. Identidade visual e sonora seguem o `AGENTS.md` quando fizerem parte
do trabalho solicitado.
