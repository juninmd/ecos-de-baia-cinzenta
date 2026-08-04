---
title: "Plano de Revisão"
description: "O checklist que guia a revisão da obra, capítulo a capítulo."
---

# Plano de Revisão

> Este é o documento que guia o trabalho. Marque a caixinha quando o capítulo
> estiver revisado. Os diagnósticos vieram da régua do `AGENTS.md`, aplicada em
> `docs/qualidade_capitulos.md`.

## Situação atual

| | Capítulos |
|---|---|
| Reprovados em portão duro (< 600 palavras ou traço violado) | ~~55~~ → **0** ✅ |
| No padrão | **234** |
| **Total** | **234** |

**Progresso:** nota média de 8,2 → **8,6**. `scripts/quality_gate.py` sai com **zero reprovados**;
`scripts/analyze_coherence.py` sai com **"Coerência validada"**; `pytest` passa (1237 testes,
exceto a falha ambiental conhecida do `pydub`).

**Capítulos reescritos nesta rodada (39):** 18, 28, 32, 33, 35, 37, 38, 39, 42, 43, 44, 46, 49,
50, 56, 58, 59, 61, 62, 63, 64, 65, 69, 71, 72, 73, 74, 75, 78, 79, 80, 81, 82, 83, 84, 85, 86,
87, 88, 89, 90, 91, 92, 93, 94, 95, 97, 131, 169, 178, 204, 209, 214.

O bolsão estava concentrado no **arco do Dilúvio (18–60)** e no **arco do Jardim (78–97)** — era
ali que a obra virava sinopse. Os dois foram reescritos inteiros sob a régua.

---

## 🎯 A grande correção estrutural: um vilão fora da lore

Todos os antagonistas da obra pertencem à mesma engrenagem: Krell criou a Aeterna, a Aeterna criou o Gamemaster, o Jardim, o Sentinel, o Taxidermista solto e o Marco administrador. Isso dá coerência, mas cobra um preço caro: **nenhuma ameaça é pessoal e nenhuma é imprevisível.** Tudo que ameaça Gabo é consequência de uma decisão corporativa tomada há sessenta anos, e o leitor sente isso como distância.

**Anselmo Braga, "O Justo"**, existe para quebrar isso. Não conhece Krell, não quer o arquivo, não pode ser comprado nem ameaçado, e não pode ser preso porque não há mais prisão. Ele cobra uma dívida que é **do Gabo, não da cidade**: o inquérito que Gabo forjou catorze anos atrás para prender um homem que era culpado, mas que ia sair.

E a armadilha que o separa de todos os outros: **ele não quer matar Gabo — quer ser morto por ele.** Desarmado, rendido, sem reação. Porque no segundo em que Gabo executar um homem imobilizado, a diferença entre os dois deixa de existir, e Braga ganha a única discussão que veio ter.

Perfil completo em `docs/personagens.md`.

### Plantio necessário nos capítulos existentes

| ✔ | Onde | O que plantar |
|---|---|---|
| [x] | Cap. 1 | Pasta **BRAGA, A.** na gaveta de baixo, e o eco de *"certifique-se de ter um culpado, e rápido"* |
| [x] | Cap. 4 | Na sessão com a Dra. Weiss, Gabo começa *"em catorze anos eu cruzei uma linha"* e desconversa |
| [x] | Dossiê da Bia | O motivo real do término: o inquérito forjado, não violência genérica |

### Arco de Braga

| ✔ | Cap. | Título | Função |
|---|---|---|---|
| [x] | 229 | O Homem no Portão | Braga se apresenta. Educado. Explica a conta. Mata alguém que não devia, e diz isso. |
| [x] | 230 | A Conta Antiga | Gabo confessa a Elena; a Dra. Vance aponta que ela e ele fizeram a mesma coisa em escalas diferentes. |
| [x] | 231 | Catraca | A armadilha funciona e vira o problema. Braga revela que sabe da Aria — pelo pátio do presídio, não por arquivo. |
| [x] | 232 | O Justo | Gabo o mata rendido, depois de tirar dele a única mentira que o consolava. E manda Elena publicar. |

---

## ✅ Reprovados — encerrado (era 55, hoje 0)

Ordem de ataque **por importância narrativa**, não por número. Capítulo de travessia curto incomoda; capítulo de virada curto estraga o livro.

### Bloco A — as viradas que estão curtas demais

| ✔ | Capítulo | Palavras | O que fazer |
|---|---|---|---|
| [x] | Cap. 47 — O Mecanismo da Queda | 570 → **1.633** | ✅ Set piece da Torre do Relógio: mecanismo plantado antes de disparar, Taxidermista com método visível, a dor chegando como silêncio antes de chegar como dor. Nota 9. |
| [x] | Cap. 41 — Maré Alta | 279 → **1.317** | ✅ O Dilúvio ganhou escala e crime: os diques sem manutenção desde o ano 41, o resgate do ônibus escolar com uma criança perdida e recuperada, e a revelação do funcionário da Companhia de Águas — *"as comportas abriram, sequenciadas; aquilo foi operado"*. Planta o Dilúvio como atentado, não acidente. |
| [x] | Cap. 45 — Protocolo N.O.A. | 275 → **1.240** | ✅ Reescrito. Arthur Vance vira **pai da Elara e do Silas**, o que amarra três personagens soltos e explica por que uma "consultora externa" mandava no arquivo. E os Leviatãs deixam de ser fio solto: das 38 unidades, 18 apodreceram alagadas, 9 emperraram, 3 pararam na subida — **oito partiram**. O Imperador acordou para conquistar uma cidade já devorada por um predador melhor. |
| [x] | Cap. 43 — Água Negra | 279 → **1.744** | ✅ O Dilúvio deixa de ser enchente e vira **rota de entrega**: a sequência das comportas leva a coluna d'água por dentro dos tanques da Aeterna. E a menina do casaco amarelo que a Elena tirou do rio no cap. 41 morre envenenada três dias depois — o resgate era o custo, não a vitória. Nota 9. |
| [x] | Cap. 92 — A Praga de Ferro | 317 → **1.605** | ✅ A ferrugem deixa de ser arma e vira **recibo**: é a resposta dos Jardineiros ao preço que Vilar recusou nove dias antes. Ele perde a prótese, o tenente e 214 pessoas — e o texto sustenta que ele decidiu sozinho, sem consultar ninguém. Nota 9. |
| [x] | Cap. 18 — A Queda | 467 → **1.908** | ✅ Gabo ganha e perde no mesmo capítulo: ombro deslocado permanente, implante da Val frito, e a plateia virtual **aplaudindo** — ele entrega ao Gamemaster o melhor episódio da temporada e sai com um núcleo que o inimigo deixou levar. Nota 9. |
| [x] | Cap. 28 — O Último Suspiro da Torre | 575 → **1.761** | ✅ Escala (3.847 crachás ativos às 3h10, creche no 40º) e um nome: **Neide R. Santos, conservação**, que sabia o caminho dos dutos e morre porque Gabo gritou "direita" para quem sabia mais que ele. O Gênesis tem carimbo de aprovação humana. Nota **10**. |

### Fio aberto herdado do cap. 45

O Imperador acorda, manda subir oito Leviatãs, e a **Fase 2 nunca se completa**. Hoje o fio morre no cap. 48 e não volta.

| ✔ | O que fazer |
|---|---|
| [x] | Fechar o destino dos oito Leviatãs — **feito no cap. 46**: um afunda reto no canal, outro encalha num banco de areia que não existia quando a Arca dormiu, e o que chega à Orla Norte sobe o aterro mancando com seis pernas boas e vazando óleo. Oito viram seis por decrepitude, sem que ninguém dispare um tiro |
| [x] | Dar desfecho ao Arthur Vance — **feito no cap. 46/72**: ele nunca chega à cidade. Fala com Baía Cinzenta por transmissão, perguntando pelo filho Silas, e a Arca N.O.A. é vaporizada no cap. 72 por três hastes de tungstênio que o próprio Gabo redireciona |
| [x] | **Cap. 233 — "Ponto Zero"** (10/10): o eco do 72, cobrado 161 capítulos depois. Elara encontra a transcrição das transmissões da Arca e descobre que o pai passou 96 dias fazendo chamada nominal para máquinas afundadas, com uma cápsula de ascensão operacional ao lado que ele nunca usou. E que **Gabo foi quem apertou** — sem saber que havia um homem no alvo. Ela se recusa a condená-lo (*"o senhor trocou quarenta mil por uma"*) e se recusa a aceitar a absolvição que o pai deixou na última linha |

### Bloco B — o arco do Dilúvio (caps. 32–65) — ✅ concluído

Reescritos: 32, 33, 35, 37, 38, 39, 42, 44, 46, 49, 50, 56, 58, 59, 61, 62, 63, 64, 65.

O que o bloco ganhou:

- **A conta do método do Gabo começa aqui.** No cap. 35 ele executa um rapaz que já tinha
  largado a arma, e a Elena vê. É o plantio direto do arco do Braga (229–232).
- **O Dilúvio deixa de ser desastre e vira negócio.** No cap. 56 o rodapé da placa da Nova Baía
  traz a data de emissão do levantamento planialtimétrico: 12 de fevereiro. As comportas
  abriram em 19 de março. A água não destruiu patrimônio — limpou título.
- **O Colar de Sol ganha origem** (cap. 50): Helena Moretti morre do outro lado do cerco
  enquanto o filho está aberto numa mesa, e a Clara paga a cremação com o relógio do Dante.
- **Os Puros, o Otávio e o Éder**: nomes de gente comum que a obra passa a dever, e que
  alimentam a lista que o Gabo carrega até o fim.

### Bloco C — o arco do Jardim (caps. 78–97) — ✅ concluído

Reescritos: 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 93, 94, 95, 97.

O arco inteiro passou a sustentar uma tese em vez de uma sequência de monstros: o Jardim não é
invasão, é a **Aeterna trocando de substrato** — trinta anos de saturação pela água, um Dilúvio
para hidratar, um Apagão que só desligou a camada de silício que atrapalhava. Cada vez que o
Gabo achou que estava atrapalhando um plano, ele cumpriu o cronograma no prazo.

### Bloco D — isolados — ✅ concluído

Reescritos: 131, 169, 178, 204, 209, 214. O cap. 131 passou a plantar a origem da Aeterna
(uma administradora de cemitério comprada em 1934), e o 169 mostra a assinatura do Dante
autorizando corpos de indigentes — a "planta baixa" que o Taxidermista só encontrou.

---

## Como saber que acabou

1. ✅ `scripts/quality_gate.py` sai com **zero reprovados em portão duro** (era 55).
2. ✅ `scripts/analyze_coherence.py` sai com **"Coerência validada"**.
3. ✅ `pytest` passa — 1.237 testes, exceto a falha ambiental conhecida do `pydub`.
4. 🟡 A nota média subiu de **8,2** para **8,6**. O alvo de 9,0 depende da terceira onda:
   os capítulos que passam nos portões mas ainda ficam abaixo do alvo de 1.100 palavras.

## Próxima onda (opcional)

Nenhum capítulo reprova mais. O que resta é elevação, não conserto: subir de "publicável" (7–8)
para "obra-prima" (9–10) nos capítulos que hoje pontuam baixo em **atmosfera** (menos de três
sentidos em cena) e em **custo** (perda reversível em vez de permanente). O relatório
`docs/qualidade_capitulos.md` já ordena a fila.
