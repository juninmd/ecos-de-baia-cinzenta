---
name: escrita-investigativa
description: >-
  Planeje e escreva novos capítulos ou revise a prosa de Ecos de Baía Cinzenta,
  com mistério investigativo, noir, cyberpunk e continuidade comprovada.
  Use em pedidos como escrever o próximo capítulo, revisar este capítulo,
  fortalecer as pistas ou preparar uma revelação. Arte, áudio e manutenção
  de código seguem seus próprios fluxos.
---

# Escrita investigativa de Baía Cinzenta

Produza prosa original em português brasileiro, com investigação que o leitor
consiga reconstruir e consequências que sobrevivam à cena. As referências
literárias fornecem técnicas; a voz e o cânone pertencem a esta obra.

## Escolha o percurso

| Pedido | Preparação | Entrega |
| --- | --- | --- |
| Capítulo novo | Estado de entrada, pergunta dramática e ficha do caso | Capítulo, registro de continuidade e parecer |
| Revisão | Diagnóstico com passagens e impacto nos capítulos vizinhos | Prosa corrigida no escopo pedido e parecer |
| Planejamento de mistério | Verdade do crime e distribuição das pistas | Ficha do caso, sem inventar prosa publicada |
| Avaliação sem edição | Leitura e verificações autorizadas | Achados com evidência e correções propostas |

Não transforme um pedido de revisão em continuação da história. Determine o
capítulo e o arco pelos arquivos; pergunte apenas se o alvo continuar ambíguo.

## Planejar

1. Leia `AGENTS.md` e `GEMINI.md` na raiz. Consulte o dossiê em
   `docs/personagens.md`, o arco em `docs/arcos.md` e os capítulos vizinhos.
   Abra os capítulos de plantio, em vez de confiar apenas nos resumos.
2. Monte o estado temporal conforme [continuidade](references/continuidade.md).
   Resolva divergências de época antes de transportar uma condição física,
   uma morte ou um conhecimento para a cena.
3. Para investigação ou revelação, preencha a ficha de
   [construção do mistério](references/investigacao.md). Para uma cena de luto
   ou consequência, registre o que muda na investigação e o que permanece aberto;
   ela não precisa introduzir um novo crime.
4. Defina desejo imediato, resistência, descoberta ou escolha, custo e saída.
   Calibre a extensão pelo trabalho dramático necessário, sem preencher palavras.

## Escrever ou revisar

- Aplique [voz, noir e cyberpunk](references/voz-noir-cyberpunk.md).
  Faça a cidade interferir nas decisões e a tecnologia obedecer a limites visíveis.
- Aproxime cada inferência de uma observação acessível ao leitor. Um especialista
  pode interpretar a pista; não pode fornecer na solução uma regra inédita
  indispensável para ela funcionar.
- Faça interrogatórios colidirem interesses: cada pessoa quer obter ou esconder
  algo. Diferencie mentira, erro de memória e interpretação equivocada.
- Registre plantio por capítulo e passagem. Se não existe, adie ou redimensione
  a revelação; não alegue que ela sempre esteve publicada.
- Preserve intenção, ponto de vista e fatos estabelecidos ao revisar. Corrija
  primeiro causalidade e continuidade; depois cenas, diálogos e frases.
- Atualize dossiê e arco somente pelo que a versão final realmente estabelece.
  Planos e hipóteses editoriais não se tornam cânone automaticamente.

## Validar

Use [revisão e entrega](references/revisao.md) para aplicar D1–D5 e os cinco
eixos do `AGENTS.md`, acrescentando auditoria de pistas, cronologia e tecnologia.
Uma nota automática alta não dispensa leitura nem sana uma dedução impossível.

Comandos a partir da raiz, usando o ambiente existente:

```powershell
uv run --no-sync python -m pytest tests/ -q
git diff --check
```

Para a triagem de um capítulo sem reescrever o relatório do livro inteiro:

```powershell
uv run --no-sync python -c "from pathlib import Path; from scripts.quality_gate import avalia; print(avalia(Path('docs/capitulo-240.md')))"
```

Substitua o arquivo pelo alvo real. `python scripts/quality_gate.py` avalia todos
os capítulos e grava `docs/qualidade_capitulos.md`; use-o ao atualizar a avaliação
global e diferencie problemas anteriores dos introduzidos pela revisão.
Execute também o lint disponível para os arquivos alterados; `git diff --check`
verifica espaços, não substitui lint de linguagem nem revisão literária.

## Armadilhas específicas

- `GEMINI.md` reúne estados de épocas diferentes; um rótulo "atual" não é uma data.
- `quality_gate.py` procura expressões: não confere o título contra o menu, toda
  a localização, a causalidade, todos os traços canônicos ou o fechamento D5.
  Contar travessões não demonstra vozes distintas; contar sangue não demonstra custo.
- A prova pode existir sem haver justiça. Um impasse institucional precisa de
  causa concreta; corrupção não autoriza todos a ignorarem uma prova óbvia.
- Não converta dez imagens desejadas por capítulo em dez cenas narrativas forçadas.
  Se houver arte ou áudio, siga os fluxos e identidades canônicas do `AGENTS.md`.

## Recursos e evidência

- [Pesquisa e leituras](references/pesquisa-leituras.md): fontes, alcance da leitura
  e distinção entre observação literária e adaptação editorial; consulte ao justificar técnicas.
- [Ensaios de uso](references/ensaios.md): cenários para verificar o comportamento
  da skill e limites da validação; consulte ao modificá-la.

Ao entregar, indique o que mudou, evidências de continuidade e pistas, portões,
notas justificadas, verificações executadas e pendências. Não declare pronto
quando um portão duro falhar ou a prova decisiva depender de informação ausente.
