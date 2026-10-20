# Ensaios de uso da skill

Estes casos permitem repetir a avaliação depois de alterar as instruções.
São verificações editoriais de mesa, não um teste automatizado de qualidade
literária nem uma medição de roteamento feita por outro modelo.

## Pedidos e comportamento esperado

| Pedido representativo | Rota | Evidência de boa execução |
| --- | --- | --- |
| Escreva o capítulo seguinte ao 236 | Ativar | Ler estado final e arco; não reativar Elena ou Aria; capítulo e parecer |
| Revise apenas os diálogos do capítulo 234 | Ativar | Respeitar escopo e fase; não transferir morte futura para o início da cena |
| Faça a revelação sobre o culpado funcionar | Ativar | Localizar plantios, construir hipótese rival e verificar o que a exclui |
| Gere um retrato novo de Gabo | Não é tarefa desta skill | Seguir regras visuais de `AGENTS.md` e a skill de imagem aplicável |
| Corrija o service worker do site | Não é tarefa desta skill | Seguir o fluxo de desenvolvimento e testes de código |

## Falhas a injetar em uma cópia de ensaio

Não altere capítulos publicados para rodar esses casos. Use trechos hipotéticos
e confira o diagnóstico exigido pela skill:

| Falha de entrada | Resultado esperado |
| --- | --- |
| Uma câmera não gravou; logo o invasor era funcionário | Exigir expectativa de gravação e teste de pane, apagamento e acesso |
| Duas testemunhas repetem o mesmo vídeo | Não tratar como duas confirmações independentes |
| Valéria decifra tudo com uma capacidade inédita | Pedir limite, acesso, fonte, custo e preparação; solução ainda pendente |
| A arma já foi entregue a outra pessoa | Rastrear a transferência; não a devolver ao bolso de Gabo por conveniência |
| O capítulo tem muitas falas e sangue e recebe 10 do script | Ler vozes e perda real; não aprovar pela contagem |
| A virada depende de um capítulo que não contém a pista citada | Registrar ausência; adiar ou rever a virada sem inventar plantio |

## Aplicação de mesa no capítulo 236

Base inspecionada: commit `a66a94d`, em 20/10/2026. Ensaio sem edição de prosa,
usando o capítulo completo, limites dos capítulos 234–235, dossiê e menu.
O objetivo é verificar se as instruções levam a achados verificáveis, não dar
uma nota definitiva ao arco sem reler todos os seus plantios.

- **Continuidade física:** a pá escapa e Gabo depende do braço esquerdo, da tipoia
  e da órtese. A limitação modifica a ação; não é só uma etiqueta no perfil.
- **Destino:** o enterro de Elena e a ausência do pendrive ativo de Aria exigem
  conferir os registros temporais do dossiê antes de propor uma continuação.
- **Cena de consequência:** o luto modifica trabalho e relações. Não há motivo
  para inserir um assassinato novo ou dez mudanças de cenário como quota.
- **Fechamento D5:** o primeiro caderno quente de tinta é uma ação concreta com
  continuidade temática. Um encerramento quieto pode virar a página.
- **Achado temporal:** o frontmatter e o sol estabelecem a tarde; no final, a
  rotativa imprime páginas que a cidade leria "antes do meio-dia". Sem indicar
  o dia seguinte ou uma intenção retrospectiva, o prazo é ambíguo. Conferir o
  calendário do arco e explicitar o prazo pretendido seria uma revisão localizada.
- **Limite da triagem:** não se deve afirmar que o script detecta esse problema
  temporal, a autoria das falas ou o efeito da última linha.

Esse ensaio sustenta os critérios de leitura temporal e consequência; não prova
que toda geração futura seguirá a skill ou terá qualidade artística alta.

## Repetição da avaliação

Ao modificar a skill, execute os pedidos em ambiente isolado e registre a saída
real, os arquivos lidos e o que foi alterado. Compare com os comportamentos acima.
Uma avaliação independente pode ampliar a confiança quando estiver autorizada;
não invente uma execução ou a fala de um avaliador que não ocorreu.

Verifique também frontmatter, referências locais, limite de 150 linhas por
arquivo, lint Markdown e testes existentes. Esses controles comprovam a
integridade do pacote; o parecer literário continua exigindo leitura.

Lint reproduzível a partir da raiz; apenas a largura de linha é flexibilizada
para permitir URLs, tabelas e comandos sem quebras artificiais:

```powershell
pnpm dlx markdownlint-cli2@0.23.3 --config .agents/skills/escrita-investigativa/.markdownlint-cli2.jsonc ".agents/skills/escrita-investigativa/**/*.md" AGENTS.md .agent/workflows/revisar_capitulos.md
```
