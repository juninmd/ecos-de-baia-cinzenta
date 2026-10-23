# Estado final da revisão

Atualização: 23/10/2026. **Revisão integral aplicada às 238 fontes**, incluindo 30.5 e 75.5. Abertura, trajetórias e desfecho foram lidos e corrigidos; não resta um lote de capítulos por iniciar.

## Resultado

- 238 fontes e 238 títulos de menu correspondentes.
- 238 espelhos públicos como symlinks relativos, com destino resolvido para a fonte oficial.
- Todas as fontes com localização e elenco, um H1, pelo menos 600 palavras e no máximo 150 linhas. Mínimo observado no recibo estrutural: 990 palavras.
- Dossiê, cronologia, arcos, resumos e análises alinhados à revisão. As fichas são incluídas pela página canônica e lidas também pelo gerador de continuidade.
- Decisões e limites no [fechamento integral](fechamento-integral.md); versões por capítulo nas três tabelas de cobertura.

## Validação final

| Verificação | Resultado |
| --- | --- |
| pytest, fontes e código | 1.268 aprovados; quatro avisos |
| Markdown lint | Zero problemas; conjunto final inclui os recibos editoriais |
| git diff --check | Aprovado, código de saída 0 |
| pnpm docs:build | Aprovado; 61,17 segundos na última execução |
| HTML gerado | Dossiê e capítulos 62,225,236 conferidos; [recibo](renderizacao-final.json) |
| Triagem lexical | 238 fontes, nenhum portão sinalizado; uma abaixo do alvo de 1.100 palavras, acima do mínimo obrigatório |

A coleta de links ignora .vitepress, que contém saída gerada e caches. Um teste específico garante que os Markdown da build não sejam tratados como fontes. O total não é diretamente comparável ao de rodadas antigas que incluíam cópias geradas. Os quatro avisos do pytest e o aviso de tamanho de chunks da build não interromperam a validação.

Lint e testes foram executados no fechamento, conforme a instrução do autor. O lint não atribui qualidade literária. A [triagem](triagem-final.md) registra notas lexicais, sem chamá-las de parecer artístico ou revisão independente. Leitura e edição foram do agente raiz, sem delegação.

## Preservação e entrega

Checkout existente master, base `2730f6c`, sem troca de branch, commit ou publicação. O relatório docs/qualidade_capitulos.md, que já estava alterado, mantém o hash original registrado em [verificacao-final.json](verificacao-final.json). Não foi sobrescrito pelo quality_gate.

Backups, candidatos e saídas completas: C:/Users/jr_ac/AppData/Local/Temp/ecos-revisao-integral-ljqdojc1. Recibos no repositório: cobertura-final-01/02/03.md e .json, verificacao-final.json, renderizacao-final.json e triagem-final-01/02/03.json.

As propostas e pareceres de rodadas anteriores permanecem como histórico. O pedido anterior de imagens tem seu [registro separado](aria-agy/ESTADO.md); não houve geração de arte nesta etapa de revisão textual.
