# Validação do pacote editorial

**Rodada 32–35:** quatro fontes, resumos e pareceres aplicados, com atualização
do parecer de 31. Suíte: 1.664 aprovados, quatro avisos, 8,37 s.
Lint não executado após a orientação do autor: reservado ao fechamento da revisão.
19 originais, 244 protegidos e 238 symlinks conferidos; recibo no backup.
Quatro perfis editoriais adicionados; 54 fichas, sem inventário exaustivo.
Verificação conjunta: 33 documentos e 301 links locais; 37 backups de duas épocas.
Sem build, mídia ou publicação. Detalhes: [32–35](revisao-032-035.md).

**Rodada 29, 30, 30.5 e 31:** quatro fontes, resumos e pareceres aplicados.
Suíte: 1.664 aprovados, quatro avisos, 18,95 s. Lint de 12 documentos passou
antes da orientação de deixar o lint restante para o fechamento da revisão.
238 links relativos, 18 originais e 244 protegidos conferidos antes da rodada
seguinte; títulos/menu, UTF-8 e teto de linhas verificados. Build não repetido.
Detalhes e limites: [revisão de 29–31](revisao-029-031.md).

**Rodada 23–28:** seis fontes, resumos e pareceres aplicados; 238 symlinks
relativos íntegros. Suíte final: 1.664 aprovados, quatro avisos, 8,76 s. Lint:
26 documentos, zero problemas. 312 links locais, UTF-8, newline, títulos contra
menu e teto de 150 linhas conferidos. 25 backups e 242 protegidos por hash.
Build em sequência passou em 63,70 s; seis downloads idênticos às fontes e
seis páginas HTML confirmadas com a prosa nova. Diff sem problemas.
A primeira tentativa de build falhou com EPERM ao limpar um arquivo de dist,
enquanto a suíte também lia essa pasta. O handle específico não foi identificado;
a repetição sequencial passou, seguida da suíte final. Sem alteração de código.
Detalhes, notas, inventário e pendências: [revisão de 23–28](revisao-023-028.md).

**Rodada 19–22 e espelhos:** 1.664 testes aprovados, quatro avisos, 9,41 s.
Ruff passou. Build final do site passou em 77,38 s, com avisos npm e de tamanho
de chunks. Os 238 espelhos são links relativos; as 424 versões anteriores foram
preservadas, incluindo dez divergências. core.symlinks local agora é true.
Há três testes novos do migrador; o total também cresce com a parametrização
de links ao acrescentar os 52 espelhos que faltavam e suas saídas no build.
A triagem mecânica cobre 238 fontes; não comprova D4/D5 ou leitura integral.
Lint: 22 documentos, zero problemas; 415 links locais existentes, UTF-8, newline,
limite de linhas, backups e fontes fora do escopo conferidos. Diff sem problemas.
Quatro downloads Markdown conferidos contra fontes; o de 21 foi sincronizado
após remoção de brancos finais. HTML de 22 contém a prosa nova. Recibo no backup.
Detalhes: [19–22](revisao-019-022.md) e [symlinks](espelhos-symlinks.md).

**Rodada 12–18, base 2730f6c:** 1.557 testes aprovados, quatro avisos; lint de
35 arquivos, zero problemas. Sete pares fonte/espelho idênticos, 33 backups e
58 arquivos protegidos conferidos por hash; 171 links locais existentes.
UTF-8, newline, teto de 150 linhas, títulos contra menu e diff conferidos.
Contagens de prosa excluem metadados, H1 e pontuação isolada. O MD025 deixa de
contar o campo YAML title como H1; a exigência de um único H1 continua ativa.
O relatório de qualidade preexistente não foi regravado. Nenhuma mídia gerada.
Evidências e limites: [revisão de 12–18](revisao-012-018.md).

**Rodada 8–11, base `2730f6c`:** 1.552 testes aprovados, quatro avisos, 4,87 s.
Lint dos 51 arquivos alterados/novos sob responsabilidade desta revisão: zero
problemas. Quatro pares novos de fonte/espelho idênticos; 32 backups conferidos
contra manifesto e 24 arquivos protegidos mantidos byte a byte. UTF-8, links,
newlines, limite de 150 linhas, base e `git diff --check` conferidos.
Resultados narrativos e pendências: [revisão de 8–11](revisao-008-011.md).

**Rodada de aplicação, base `2730f6c`:** 1.552 testes aprovados, quatro avisos,
4,85 s; lint dos 34 arquivos conferidos com zero problemas. Cinco pares de
fonte/espelho idênticos. UTF-8, links, newline final e limite de 150 linhas
conferidos nos 34 arquivos; `git diff --check` sem problemas. O hash exato do
relatório preexistente foi preservado e a base permaneceu estável. Prosa, resumos,
pareceres e pendências atuais: [revisão de 4–7](revisao-004-007.md).

Os recibos e resultados abaixo descrevem a primeira etapa de perfis, anterior
à aplicação. Não são hashes de preservação das fontes deliberadamente revisadas.

Escopo inicial: proposta e parecer em `editorial/revisao-personagens/`.
Não é validação de todos os capítulos nem promoção das propostas a cânone.

## Resultados técnicos

- `uv run --no-sync python -m pytest tests/ -q --disable-warnings`:
  **1.552 aprovados, quatro avisos, 4,94 s** na execução após as fichas e pareceres.
  Os testes não avaliam interesse do elenco nem coerência narrativa integral.
- `pnpm dlx markdownlint-cli2@0.23.3 --config .agents/skills/escrita-investigativa/.markdownlint-cli2.jsonc "editorial/revisao-personagens/**/*.md"`:
  **zero problemas** nos 14 documentos então existentes; largura de linha
  flexibilizada pela configuração da skill. Reexecução final: **15 documentos,
  zero problemas**, incluindo este registro.
- Execução final da suíte após o registro: **1.552 aprovados, quatro avisos,
  4,83 s**. Checagem dos 15 documentos: UTF-8, newline final, no máximo 150 linhas,
  links locais existentes, 36 perfis cobrindo as 35 entradas e 238 capítulos sem
  duplicação no inventário. Agregado atual das fontes reconferido e estável.
- Quatro fontes iniciais: H1 único e idêntico ao menu; espelhos idênticos byte a
  byte. Contagens de prosa e pendências D1–D5 constam do parecer.
- Nenhum capítulo foi editado; nenhum espelho precisou ser sincronizado.
- Nenhuma navegação ou componente mudou; build do site não se aplica a esta etapa.

## Verificação de preservação e resultado negativo

A primeira comparação do agregado de hashes com o recibo inicial falhou. O
relatório preexistente manteve seu hash exato; as demais 243 fontes foram
comparadas a `HEAD`, normalizando apenas finais de linha CRLF/LF, sem divergência
textual. A causa da diferença de agregado não foi determinada. Portanto, este
pacote **não alega prova de igualdade byte a byte com o primeiro recibo**.

O novo agregado está registrado em [estado](estado.md), permitindo reconferir o
conteúdo atual no fechamento. O diff rastreado continua limitado à alteração
preexistente do relatório de qualidade. Todos os documentos produzidos são aditivos.

## Revisão do conteúdo e alcance

Passagem de conteúdo: conferidas as 35 entradas do dossiê contra a presença nas
fichas; Enzo e Sofia têm propostas separadas. As oito participações adicionais
não se apresentam como inventário exaustivo. Fato publicado, descrição de dossiê
e proposta permanecem distintos. Não há novas fisionomias, retratos ou biografias
apresentadas como já publicadas.

Passagem de alegações: P01–P10 continuam abertos na obra; busca não conta como
leitura integral; leitura para perfis não conta como revisão corrigida. O modelo
de datas é condicional, incluindo o intervalo de quatro anos. Verificações
técnicas não tornam obrigatório aprovar decisões artísticas.

Essas são passagens do próprio autor da proposta, sem independência. O pacote
pode ser entregue como proposta fundamentada; a revisão integral permanece
**não convergida**. Não há publicação, envio externo ou alteração do cânone.
