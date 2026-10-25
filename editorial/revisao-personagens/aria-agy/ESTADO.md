# Aria: estado da geração pelo Antigravity

**Rodada atual, 23/10/2026:** onze imagens selecionadas aplicadas a doze destinos.
Novo retrato `aria_3.png`; a tentativa abaixo é histórico de 22/10, não o resultado
atual. [Recibo e homologação](../aria-imagens-20261023.md).

Atualização: 22/10/2026. A direção vigente é **mulher adulta como holograma
volumétrico**, com rosto estável, cabelo platinado, heterocromia azul/âmbar e
jaqueta de malha de dados escura. Não substituir a personagem por grandes telas.

## Decisão e correção

O autor rejeitou as composições que colocavam Aria em monitores, televisores ou
terminais gigantes. Elas não são arte aprovada. As cinco capas geradas nessa
direção nunca foram aplicadas; a cena do Cobalt foi restaurada ao original.
A apresentação em visor foi retirada das referências da galeria. Os arquivos
anteriores e os resultados rejeitados permanecem preservados, sem promoção.

A referência adulta `aria_2.png` permanece como guia de identidade; o Antigravity
deve produzir um novo retrato holográfico antes de gerar o restante do lote.

## Inventário visual

Foram inspecionadas 374 imagens de capas, cenas, caches e cenários em 16 pranchas,
com ampliação dos casos ambíguos e consulta aos capítulos correspondentes.
Isso ampliou a triagem inicial de 15 cenas selecionadas apenas pelo elenco.

- Retrato e apresentação: duas imagens.
- Capas com Aria: capítulos 2, 59, 67, 74 e 96.
- Cenas do capítulo 2: 2, 4, 5, 7 e 10.
- A cena 4 e a apresentação antiga eram cópias idênticas, verificadas por SHA-256;
  devem compartilhar a nova arte. São 12 destinos e 11 gerações distintas.
- A mulher de branco em 26 é Bia; a de vermelho em 55 é Isadora. Não substituir.
- A imagem de mulher física em 32 não foi atribuída a Aria: a prosa mantém a IA
  offline. A consistência das outras personagens pertence à revisão geral.

O lote é restrito às aparições de Aria identificadas. Não é homologação do acervo
completo: há outras inconsistências visuais que pertencem à revisão geral.

## Pedido executado e impedimento real

Conversa criada no Antigravity: `ac715505-6df7-4946-b9c9-b4c6fd219013`.
Briefing: [PEDIDO.md](PEDIDO.md). Prompts, fontes e seeds: [lote.json](lote.json).
O CLI recebeu o pedido e acionou o gerador nativo para o primeiro retrato.

Resultado do serviço: **429 QUOTA_EXHAUSTED** em `gemini-3.1-flash-image`.
Retorno registrado: `quota will reset after 48h32m19s`, às 00:22 de 22/10/2026
(America/Sao_Paulo), aproximadamente 24/10/2026 às 00:55.
É uma estimativa baseada na resposta do serviço, sujeita a nova verificação.

**Produção pelo agy: 0 de 11 imagens.** A tentativa do retrato falhou e as dez
seguintes não foram iniciadas. Evidência: [resultado.json](resultado.json).
Não houve publicação, envio por Telegram, cobrança ou troca de provedor.

A lista de `agy models` expôs modelos de texto. A consulta específica sobre outro
modelo de imagem expirou sem resposta após dois minutos; nenhuma alternativa
de geração foi confirmada. O campo `SUCCESS` do CLI não prova geração: os arquivos
de saída permanecem ausentes e o resultado do serviço registra o bloqueio.

## Retomada e aceite

Retomar a mesma conversa com o briefing, após confirmar a capacidade do gerador.
Os candidatos devem ser salvos nesta pasta, fora dos arquivos públicos ativos.
Depois: verificar identidade adulta, transparência e pose; medir qualidade; só
então promover os arquivos aos 12 destinos, preservando os originais.

As 444 entradas futuras que incluem Aria foram atualizadas para a direção
holográfica. A investigação de sua evolução autônoma continua planejada em
[Aria](../../../docs/aria.md), sem inventar plantios já publicados.

## Validação local

1.557 testes passaram, com quatro avisos; Ruff e lint dos seis documentos novos
ou editoriais alterados passaram. Os três documentos antigos mantêm 924 problemas
de lint que já existiam antes da mudança. `git diff --check` passou.
Os hashes protegidos não apresentaram alterações inesperadas. A cena do Cobalt
foi restaurada byte a byte; as 444 mudanças da fila atingem apenas entradas com
Aria, preservando capítulo, cena, destino, ação e seed. Isso valida a preparação;
não homologa imagens que o Antigravity ainda não conseguiu produzir.
