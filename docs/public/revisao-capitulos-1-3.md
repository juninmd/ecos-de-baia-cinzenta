# Aplicação editorial nos capítulos 1–3

Data: 20/10/2026. Escopo: capítulos iniciais, seus espelhos, pareceres e a
passagem imediata ao capítulo 4.
Fonte narrativa oficial: `docs/capitulo-N.md`. Base: commit `2f7db7e`.

## Critérios e preservação

- Skill `escrita-investigativa`: D1–D5, cinco eixos editoriais, pistas, custódia,
  cronologia, limites tecnológicos e passagem ao capítulo seguinte.
- Nove originais preservados em backup local temporário, fora do repositório, com
  SHA-256 da origem e da cópia conferidos antes da edição. O histórico Git é a
  cópia durável; o diretório temporário pode ser limpo pelo sistema.
- O capítulo 4 foi lido para conferir a passagem. Sua prosa recebeu apenas os
  reparos exigidos por esta revisão: Localização no frontmatter, mão direita
  ferida, Aria no comunicador e localização no beco.
- Arte, áudio, publicação automática e revisão de todo o arco ficam fora do recorte.
- Symlinks foram pedidos e depois adiados pelo usuário: o ensaio no Windows
  retornou WinError 1314. Os quatro espelhos ainda são cópias idênticas, não links.
  A fonte oficial e o destino previsto estão registrados no `AGENTS.md`.
- Revisão pelo mesmo agente, seguida de revisão independente de código e de
  segurança. Não é avaliação humana.

## Medidas e pareceres

Contagem por separação de palavras, retirando frontmatter e H1; pareceres não
contam como narrativa. As três versões estão entre 1.100 e 1.600 palavras.

| Capítulo | Palavras narrativas | Nota editorial | Parecer e caderno de pistas |
| --- | --- | --- | --- |
| 1 — Olhos de Vidro | 1.588 | 8/10 | [Diagnóstico e correções](analise_capitulo-1.md) |
| 2 — Náufragos de Concreto | 1.339 | 8/10 | [Diagnóstico e correções](analise_capitulo-2.md) |
| 3 — Teatro de Carne | 1.587 | 9/10 | [Diagnóstico e correções](analise_capitulo-3.md) |

A triagem lexical anterior dava 10, 10 e 9, sem portões duros reprovados. Ela
não detectava a localização ausente, a custódia contraditória ou os saltos de
dedução. As notas acima são leitura editorial justificada, não saída do script.
O ranking global foi atualizado apenas para os capítulos 1–3; o relatório global
de qualidade não foi regravado fora do escopo.

## Correções da revisão independente

| Achado | Correção aplicada |
| --- | --- |
| Primeira foto em dois lugares na custódia | O original fica no compartimento do carro; só a reprodução da segunda foto vai ao comunicador |
| Chamado do Setor 4 não aparecia no capítulo 2 | Despacho passa a ser mostrado antes de o GPS exibir a rota |
| Promessa dos armazéns não cumprida no capítulo 4 | Saída do 3 passa a confrontar as duas fotografias, o que o 4 entrega |
| Capítulo 4 sem `Localização` (D3) | Frontmatter separa local, elenco físico e memória |
| Ferimento da mão direita sumia no capítulo 4 | Capítulo 4 usa a mão esquerda e reconhece a queimadura sob a gaze |
| Aria ficava no painel e aparecia no comunicador | O módulo é recolhido ao fim do 3 e acoplado ao comunicador |
| "Amante" contradizia o dossiê de Bia | Passa a "ex-parceira, o amor que não voltou" |
| Resumos dos capítulos 1–3 estavam desatualizados | Passagens alteradas foram sincronizadas |
| Comando de lint baixava versão sem fixar | `markdownlint-cli2@0.23.3` |

## Validação

Verificações locais executadas:

- `uv run --no-sync python -m pytest tests/ -q --disable-warnings`:
  **1.146 testes aprovados**, sem falhas; quatro avisos existentes.
- Markdownlint sobre 21 arquivos — capítulos 1–4 e espelhos, três pareceres,
  registro, `AGENTS.md`, workflow e sete arquivos da skill: **zero problemas**.
  Apenas largura de linha é flexibilizada. `docs/ranking_qualidade_capitulos.md`
  e `docs/resumos/cap-00N.md` mantêm dívida de lint anterior a esta rodada e não
  foram normalizados.
- Frontmatter da skill validado como YAML. O aviso "Skill is valid!" de
  ferramenta externa não é reproduzível por comando versionado no repositório.
- Verificação estrutural dos 27 arquivos da alteração: UTF-8, newline final,
  até 150 linhas por arquivo novo. Links locais de `docs/` cobertos por
  `tests/test_links.py`; links da skill conferidos manualmente.
- Quatro títulos iguais ao menu, metadados conferidos, contagens acima e
  quatro pares de espelhos com conteúdo idêntico. Não são symlinks.
- Revisão de causalidade/custódia, continuidade e voz concluída após os reparos.
  A aprovação literária permanece limitada às passagens lidas; testes
  automatizados não medem qualidade artística.

## Pendências fora do recorte

- A aritmética de carreira entre `docs/cronologia.md`, `docs/personagens.md` e o
  capítulo 1 continua exigindo decisão editorial.
- O capítulo 4 tem 2.241 palavras, acima do alvo de 1.600, e seus erros internos
  antigos seguem para a revisão do arco junto da dívida de `docs/REVISAO.md`.
