# Parecer da revisão de prosa

Alvo: 36 capítulos do arco Necrópole/Usina e da rua. Diagnóstico e comparação literária em [Comparativo literário](/comparativo_literario.md).

**Alvo e escopo:** 36 capítulos (116, 122, 129, 132, 140–165 intercalados, 181–200) —
descrição, gesto e gatilho sensorial. Nenhuma cena foi reescrita, nenhuma trama alterada.

**Portões duros nos capítulos tocados:**

| Portão | Resultado |
| --- | --- |
| D1 — Extensão (≥600, alvo 1.100–1.600) | Nenhum abaixo do portão de 600. **7 abaixo do alvo de 1.100**, dos quais 4 foram tocados por esta revisão (145, 147, 150, 158) — listados como pendência |
| D2 — Título/H1 | Inalterados |
| D3 — Metadados | Inalterados; Localização e Personagens conferem com a cena |
| D4 — Cânone | Preservado: braço direito na tipoia, órtese no joelho, Modo de Segurança de Val, Gabo não fuma |
| D5 — Fechamento | Função preservada em todos: imagem, decisão ou ameaça. Em 129 e 154 a frase final foi reescrita sem trocar a função |

**Notas (régua do `AGENTS.md`, leitura manual, não saída do script):**

| Capítulo | Atmosfera | Custo | Voz | Ritmo | Consequência | Nota |
| --- | --- | --- | --- | --- | --- | --- |
| 116 | 2 | 2 | 2 | 2 | 2 | 10 |
| 129 | 2 | 2 | 2 | 2 | 2 | 10 |
| 140 | 2 | 2 | 2 | 2 | 2 | 10 |
| 152 | 2 | 2 | 2 | 2 | 2 | 10 |
| 154 | 2 | 2 | 2 | 2 | 2 | 10 |

Justificativa curta: 116 cobra o abandono de Rangel e deixa a ordem no registro; 129
registra a mão de Gabo na alavanca antes de matar quem talvez estivesse vivo; 140 troca
o resumo de narrador por fala e mantém as mãos queimadas; 152 preserva o frio como
antagonista e a morte de Rangel como ausência; 154 fratura o braço de forma permanente
e não oferece compensação mecânica.

**Comandos executados:**

```powershell
uv run --no-sync python scripts/auditoria_repeticao.py   # 239 capítulos, 4 grupos em 4 capítulos
uv run --no-sync python scripts/auditoria_tiques.py       # média 1,55 tique/mil
uv run --no-sync python scripts/quality_gate.py           # 239 capítulos, 0 reprovados, média 8,9
uv run --no-sync python -m pytest tests/ -q               # 1287 passed
git diff --check                                          # sem erro de espaço
```

**Limites desta revisão:** a auditoria mede repetição de superfície, não tédio. Um capítulo
com zero tiques pode continuar sem conflito; a nota da tabela acima é juízo de leitura, não
consequência do contador. As pendências da §5 continuam abertas e não foram declaradas
resolvidas.

**Veredito:** revisado e publicável. A obra sai melhor que a média do gênero nos quatro
pontos estruturais e deixa de se copiar na superfície. Não é obra-prima pela régua —
faltam as duas coisas que nenhuma revisão de frase resolve: Aria precisa errar, e o trauma
precisa de uma cena de origem em vez de dezesseis repetições.
