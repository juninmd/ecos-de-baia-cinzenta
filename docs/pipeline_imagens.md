# Pipeline das imagens de capítulo

> **Alvo da obra: 10 cenas por capítulo, 235 capítulos, 2.350 imagens.**
> Estado atual medido em `docs/qualidade_imagens.md`.

A quota de imagem é o recurso escasso, e a Regra Zero (`AGENTS.md`) diz que fisionomia
não muda. As duas coisas juntas definem o desenho: nada de gerar duas vezes a mesma cena,
nada de gastar quota lendo capítulo, e nenhuma imagem entra no repositório sem passar por
um portão que mede o que dá para medir.

## O ciclo

```
build_scene_manifest.py  →  lote_cenas.py  →  geração  →  homologar_cenas.py
        ↑                                                        │
        └──────────────── regerar.txt ←──────────────────────────┘
```

1. **`python scripts/build_scene_manifest.py`** — varre os 235 capítulos, divide cada um
   em 10 blocos narrativos e monta a fila do que falta. Cada linha já sai com prompt
   pronto, retratos de referência, vestuário canônico, seed determinística e a fase física
   do personagem naquele capítulo. Cena que já tem arquivo não entra na fila.
2. **`python scripts/lote_cenas.py --tamanho 40 --briefing lote.md`** — corta a fila no
   tamanho da quota do dia. O briefing é markdown: dá para colar direto no CLI do Gemini /
   antigravity, que só precisa gerar e gravar no caminho indicado.
3. **Geração.** Duas portas, mesma fila:
   - manual/CLI, consumindo o briefing acima;
   - `python scripts/gerar_cenas_manifesto.py --tamanho 20`, que chama o Gemini direto
     (`NANO_BANANA_API_KEY` ou `GEMINI_API_KEY`), homologa cada imagem na hora e **apaga o
     refugo** — cena reprovada volta para a fila sozinha na rodada seguinte.
4. **`python scripts/homologar_cenas.py --realimentar`** — mede o acervo inteiro, escreve
   `docs/qualidade_imagens.md` e devolve as reprovadas para `docs/public/cenas/regerar.txt`,
   que o passo 1 lê. O ciclo se fecha sem ninguém anotar nada à mão.

## O que trava a fidelidade do personagem

| Trava | Onde | Por quê |
|---|---|---|
| Retrato de referência de **todo** o elenco da cena | `prompt_cena.montar_elenco` | Âncora só no protagonista deixava a Val sair de cabelo rosa. |
| Cláusula explícita de "estes rostos são canônicos" | `prompt_cena.REFERENCIAS` | Sem ela o modelo trata o retrato como inspiração e devolve um sósia. |
| Vestuário repetido no fecho do prompt | `vestuario.reforco` | É a última instrução lida, e roupa é o traço que mais escapa em cena de ação. |
| Fase do vestuário por capítulo | `vestuario.na_fase` | Dante usa fedora até o 103 e macacão técnico do 104 em diante. |
| Fase física por capítulo | `continuidade.clausula` | Regra 9 do `AGENTS.md`: exoesqueleto no 105, prótese no 180, maneta no 225. |
| Seed determinística (`capítulo × 100 + cena`) | `prompt_cena.seed_da_cena` | Regra 4: a mesma cena tem que produzir a mesma imagem. |
| Proibição de texto e de traço de ilustração | `prompt_cena.SEM_TEXTO` / `ESTILO` | O acervo tinha "SOLARIS TOWER — CHAPTER 9" queimado dentro da arte. |

## O portão de homologação

`scripts/art_gen/homologacao.py` mede cada arquivo com Pillow + numpy — sem dependência
nova. Os cortes foram calibrados sobre as 118 cenas canônicas já publicadas, sempre com
folga abaixo do pior arquivo aprovado, para reprovar defeito e não estilo:

| Medida | Corte | Pior aprovado no acervo |
|---|---|---|
| Resolução | 1024×576 | 1376×768 |
| Proporção | 1,25 a 2,10 | 1,79 |
| Tamanho do arquivo | 120 KB | 592 KB |
| Nitidez (variância do laplaciano) | 120 | 166 |
| Contraste (desvio da luminância) | 18 | 21,3 |
| Faixa suspeita de texto | alerta em 2,3× a mediana | 1,6× (mediana do acervo) |
| Cena repetida (distância dHash) | ≤ 6 no mesmo capítulo | — |

Reprovação é hard: a cena volta para a fila. Alerta é para o olho humano — o corte de
2,3× pegou exatamente as duas imagens do acervo com legenda queimada.

### Fidelidade de rosto

Resolução se mede com numpy; fisionomia não. `scripts/art_gen/fidelidade.py` manda a cena
e os retratos canônicos para um modelo de visão e pede um veredito em JSON (`fiel`,
`personagens[].confere`, `texto_na_imagem`, `nota`). Roda em dois lugares:

- dentro do runner, antes de aceitar a imagem;
- por amostra no acervo: `python scripts/homologar_cenas.py --visao 30`.

Sem chave configurada, o portão mecânico continua funcionando sozinho e a auditoria de
visão se declara indisponível em vez de quebrar a rodada.
