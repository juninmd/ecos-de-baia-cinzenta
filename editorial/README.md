# editorial/

Notas de trabalho de revisão. **Não é cânone.** O texto oficial são os capítulos em
`docs/capitulo-N.md` e os dossiês em `docs/personagens/`.

## O que vive aqui

| Caminho | O que é |
| --- | --- |
| `auditoria-2026-10-23/` | Auditoria de continuidade e agência: relatórios por tema, mapas de descida e as três planilhas de fontes (`fontes-0*.csv`) |
| `revisao-personagens/revisao-capitulos-1-35.md` | Sete relatórios de lote consolidados em um só (caps. 1–35) |
| `revisao-personagens/` (demais) | Diagnóstico, cobertura, estrutura, validação e os cadastros de personagens por grupo |
| `revisao-personagens/aria-agy/` | Notas do experimento de arte da Aria (`ESTADO.md`, `PEDIDO.md`) |
| `REVISAO-historico.md` | Registro histórico da revisão editorial, capítulo a capítulo (488 KB). Saiu de `docs/` em 31/10/2026: era a maior página do site e não estava no menu |

## O que foi removido em 31/10/2026

- **285 arquivos do aparelho antigo de análise**: `analise_capitulo_*` em `docs/`, `docs/public/` e `Cronologia/`, mais o checklist `REVISÃO.md` e o ranking manual. Eles eram a saída do processo descrito no próprio checklist: um parecer por capítulo, escrito à mão. Hoje esse trabalho é medido por `scripts/quality_gate.py` e publicado em `docs/qualidade_capitulos.md`.
- **20 imagens de candidatos e rejeitadas** do experimento `aria-agy` (52 MB). O retrato aprovado já está em `docs/public/personagens/aria_3.png`.
- **Saídas de máquina** (JSON de triagem, cobertura, verificação e lotes) que os relatórios `.md` já resumem e que `quality_gate.py` regenera.

## Duplicatas de imagem

`docs/public/personagens/variacoes/` era uma **cópia byte a byte** de 50 cenas já existentes em `docs/public/cenas/` (mesmo blob no git, 36,6 MB no checkout). Como `AGENTS.md` define `docs/public/cenas/` como cache canônico da arte, as cópias foram removidas e a galeria `docs/variacoes_personagens.md` passou a apontar para as cenas — 50 referências reescritas, nenhuma imagem perdida.

Sobraram **três grupos de imagens repetidas** que são decisão de conteúdo, não arquivo órfão:

| Arquivos | Situação |
| --- | --- |
| `capitulo_105-108.jpg`, `cidade.jpg`, `raizes-amargas.jpg` | mesma arte usada como capa de capítulos sem imagem própria |
| `personagens/lux.jpg`, `personagens/vale.jpg` | retratos ainda apontando para a arte genérica da cidade |
| `personagens/krell.jpg`, `personagens/cirurgiao.jpg` | **mesma imagem para dois personagens** — retrato de Krell errado |

Os dois últimos são dívida de arte, não duplicata de arquivo: unificar o caminho só esconderia o problema.

## Processo vigente

```powershell
uv run --no-sync python scripts/quality_gate.py        # notas e portões duros
uv run --no-sync python scripts/auditoria_repeticao.py # repetição entre capítulos
uv run --no-sync python scripts/auditoria_tiques.py    # densidade de tiques
```

Relatórios: `docs/qualidade_capitulos.md`, `docs/auditoria_repeticao.md`,
`docs/auditoria_tiques.md`, `docs/comparativo_literario.md`, `docs/parecer_revisao.md`.
