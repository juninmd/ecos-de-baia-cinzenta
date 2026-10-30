# Revisão de Valéria, Aria e Elena

## Decisões e alcance

- Valéria tem 28 anos durante a narrativa. O dossiê e as menções explícitas nos capítulos 45, 48, 49, 64, 65, 74, 89 e 95 foram atualizados. O evento aos 19 anos citado no capítulo 95 continua anterior; a mudança de idade não prova uma nova data para ele.
- A origem, a voz e a memória de Aria não derivam de Bia. A alteração alcança a explicação da origem (69 e 75.5), as conversas com Rangel e Val (109 e 112), a usina (115 e 117), o reparo e a falha de saída (125–128), o ataque no Ateliê (133–134), suas consequências (137 e 176) e o relato de Gabo a Elena (226). A réplica que o Taxidermista usa contra Gabo continua sendo uma mentira sobre Bia; a intrusão no canal de Aria vem do transmissor do Ateliê.
- Após a morte de Bia, Elena e Gabo investigaram o caso. Gabo abordou uma fonte usando o nome de Elena sem avisá-la. A entrevista foi cancelada; fotos deixadas na redação constituem uma ameaça, mas não identificam o responsável. Ele então tentou fazê-la abandonar a apuração. Elena explica que rompeu o casamento pela quebra de confiança e pela tentativa de controlar sua escolha. O capítulo 21 planta a lembrança; o 226 dá a versão dela e a resposta de Gabo.

## Continuidade e limites

O capítulo 1 já estabelece a morte de Bia e o avistamento de Miranda no beco, sem prova suficiente. O novo episódio anterior à separação usa somente essa suspeita: não antecipa a responsabilidade revelada posteriormente nem a fraude confessada no capítulo 230. Elena era amiga de Bia e testemunha do casamento em 75.5; o casamento com Gabo ocorre depois da morte dela. A investigação de Elena continua escolha profissional própria, não consequência exclusivamente do casamento.

A triagem de 25 capítulos alterados não encontrou reprovação nos portões automáticos. Os capítulos 112, 125 e 126 ficaram abaixo do alvo de 1.100 palavras, mas acima do mínimo automático. A triagem não confere sozinha o título no menu, a causalidade, o fechamento, as vozes ou a qualidade literária. As leituras concentraram-se nas passagens modificadas e nos pontos de continuidade identificados; não constituem releitura integral de todos os capítulos vizinhos nem atribuição de nota literária global.

Os 25 espelhos dos capítulos alterados continuam sendo links relativos para as fontes oficiais. Testes: `uv run --no-sync python -m pytest tests/ -q` (1.272 passaram, quatro avisos); `git diff --check` passou. O projeto não declara configuração de lint Markdown. A verificação adicional com `markdownlint-cli2` nos 17 arquivos examinados ainda aponta regras anteriores, sobretudo limite de linha; na comparação com `origin/master`, a contagem total caiu de 520 para 509. A checagem de espaços não substitui o lint de linguagem.

## Complemento: revisão das relações

- O capítulo 95 situa também aos 28 anos a morte dos três homens no corredor, em continuidade com o capítulo 49.
- A gravação de Elena no capítulo 235 mantém o medo de perder Gabo, mas reconhece a quebra de confiança e sua escolha profissional; ela queria voltar, e não apresenta a morte como condição necessária para a trajetória dele.
- Os dossiês de Val e Elena registram a cooperação mostrada nos capítulos 27, 35 e 236, sem impor uma rivalidade romântica que aquelas cenas não demonstram. A amizade entre Val e Gabo continua tendo afeto e divergências.
- As conversas sobre café no capítulo 8 e sobre descanso no 75.5 acrescentam hábitos, humor e limites próprios a Aria. Ela depende da informação dada por Gabo para comentar o café; o canal de emergência permanece ligado no encontro com Val.

A triagem dos capítulos 8, 75.5, 95 e 235 não apontou reprovações automáticas; os quatro espelhos continuam links relativos para suas fontes. A leitura das cenas não substitui uma avaliação integral de todos os vínculos da obra.

Verificação após o complemento: `uv run --no-sync python -m pytest tests/ -q` passou (1.272 testes; quatro avisos), e `git diff --check` passou. O `markdownlint-cli2` ainda reporta 164 ocorrências nos seis arquivos examinados; os mesmos arquivos em `origin/master` apresentam 167. A comparação por arquivo e regra não mostrou aumento na contagem, mas o lint completo segue reprovado.
