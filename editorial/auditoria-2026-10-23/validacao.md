# Método, cobertura e validação

> Histórico da versão anterior às correções. Para o estado atual, consulte [correções aplicadas](correcoes-concluidas.md). As passagens e os números de linha abaixo documentam a auditoria original.

23/10/2026. Escopo: diagnóstico literário e linha do tempo da versão local; nenhuma reescrita, geração de mídia, publicação ou alteração de navegação.

## Autoridade e preservação

Fontes: capítulos oficiais em `docs/capitulo-N.md`, dossiê, calendário, arcos, `AGENTS.md`, `GEMINI.md` e skill de escrita investigativa. Relatórios antigos foram usados para localizar participações, não como prova da qualidade atual.

A raiz possui integração e arquivos novos deste diretório. Revisores possuem apenas leitura e achados. Mutação dos capítulos, runtime e promoção: não aplicáveis. O checkout já continha muitas alterações, inclusive nos 238 capítulos e espelhos; não houve troca de branch, restauração ou normalização dessas alterações.

Os hashes completos das 238 fontes foram registrados antes da consolidação. Os recibos em `fontes-01.csv`, `fontes-02.csv` e `fontes-03.csv` vinculam capítulo, contagem aproximada e hash SHA-256. São identidade da versão, não certificado de leitura ou de valor artístico.

## Cobertura de leitura declarada pelos revisores

| Unidade | Fontes lidas integralmente | Observação |
| --- | --- | --- |
| leitura_1 | 1–48, 30.5; depois 49–64 e 193–206 | Saídas agrupadas truncadas foram recuperadas por capítulo; transições e participações também consultadas. |
| leitura_2 | 74, 75.5, 92–96 confirmados | Restante do bloco original foi leitura por passagens; não contado como integral. |
| leitura_3 | 97–144, vizinhos 96/145; depois 65–80, 75.5 e 207–219 | Corrigiu interpretação inicial do cubo no 100; última faixa lida em lotes de dois sem truncamento. |
| leitura_4 | 145–192, vizinhos 144/193; depois 81–96 | Cecília e Elias conferidos também fora do bloco. |
| leitura_5 | 220–236, em reconferência integral | Retirou a declaração inicial de leitura integral de 193–219; outros revisores cobriram a lacuna. O 227 foi relido após truncamento. |
| raiz | Fontes dos principais achados, começo/final, documentos canônicos e triagem das 238 fontes | Integração e checagem de alegações; não apresentada como segunda leitura integral independente. |

União da leitura integral declarada após as complementações: **238 capítulos**, incluindo 30.5 e 75.5. As lacunas dos pareceres iniciais em 49–96 e 193–219 foram cobertas por outros revisores; 220–236 tiveram reconferência integral. As mensagens de correção e execução estão nesta sessão. Os recibos de hash identificam a versão; não substituem a declaração de alcance nem provam atenção humana ou recepção artística.

Os perfis oficiais foram distribuídos e consolidados em 36 avaliações, pois Enzo/Sofia foram separados; Operativo e Shadowban são perfis representativos. Participações adicionais estão em documento próprio. A leitura não sustenta um censo exaustivo de todo nome incidental.

## Triagem reproduzida sem sobrescrever relatório anterior

- 238 fontes; aproximadamente **326.279 palavras** de corpo narrativo.
- Contagem por espaços após retirar frontmatter, H1, separadores e imagens Markdown; não é tokenização linguística nem paginação editorial.
- Mediana: **1.294,5 palavras**; mínimo **1.012**, máximo **2.317**.
- Nenhuma abaixo de 600; uma abaixo do alvo de 1.100; 35 acima de 1.600. O teto é alvo, não reprovação automática.
- Um H1 com número/formato correto, localização e elenco em todas as fontes.
- Os 238 espelhos são symlinks e seus conteúdos conferem com as fontes. Conferência do alvo relativo e títulos do menu registrada no recibo de verificações.
- `scripts.quality_gate.avalia()` não apontou falhas nos portões que automatiza. A função não grava `docs/qualidade_capitulos.md`.
- Essa triagem não aprova D4/D5, vozes, plantio, causalidade ou qualidade literária. Achados 1/19, 149/151 e 154 demonstram por que leitura continua necessária.

## Portões e juízo editorial

| Critério | Conclusão limitada à evidência |
| --- | --- |
| D1 | Mínimo atendido pela contagem aproximada em todas as fontes. |
| D2 | Formato e número atendidos; comparação com menu é verificação separada abaixo. |
| D3 | Campos presentes; compatibilidade de todo elenco não é garantida por presença dos campos. Em 114 há mistura de presença remota/mencionada que merece padronização. |
| D4 | **Não aprovado globalmente**: contradições de aparência, identidade/estado narrado e memória precisam de reparo. |
| D5 | Sem aprovação individual de todos os fechos registrada nesta rodada. O final 236 oferece ação/imagem de continuidade; isso não aprova os outros 237 por extensão. |

Não foi atribuída nota literária individual aos 238 capítulos. A régua de cinco eixos orientou a leitura, mas converter a média lexical em “obra-prima” apagaria os problemas encontrados. Pontos fortes e prioridades têm passagens citadas nos pareceres.

## Comandos e checagem final

- `uv run --no-sync python -m pytest tests/ -q`: **1.272 passaram, 4 avisos**, em 22,61 s. Três avisos são testes PWA retornando valor; outro é depreciação de `audioop`.
- Markdownlint-cli2 0.24.0: **12 arquivos Markdown, zero problemas**.
- Links Markdown locais: todos os arquivos de destino existem; âncoras não foram renderizadas em build.
- Todos os 16 arquivos novos têm no máximo 150 linhas; três recibos CSV permitem preservar os hashes completos sem ultrapassar o limite.
- As 238 fontes continuam com os hashes registrados no início; todos os títulos correspondem ao menu e todos os espelhos têm alvo relativo `../capitulo-N.md` e conteúdo igual à fonte. Recibo: [verificações](verificacoes.json).
- `git diff --check` no diretório novo: sucesso; por serem arquivos ainda não rastreados, a checagem real de Markdown é a execução do lint acima.
- Build do site não requerido: não houve alteração de site/navegação nem afirmação de publicação.

## Estado da avaliação

Modo de diagnóstico; rodada limitada à leitura, checagem dos achados e auditoria da síntese. Há achados abertos e nenhuma versão corrigida. **Não convergiu para aprovação**; não há duas passagens limpas sobre uma versão corrigida congelada. A aceitação artística do autor permanece distinta de teste técnico e parecer de agente.

Dois revisores que não escreveram os relatórios finais conferiram a síntese contra as fontes. Confirmaram os achados centrais de Dante, Aria, lastro, Braga e final, e a distinção entre plantio temático e regra nova em 228. Mantiveram o calendário como inferência condicional; a auditoria também corrigiu declarações de cobertura excessivas. Esse controle melhora a precisão do parecer, sem converter os achados abertos em aprovação da obra.
