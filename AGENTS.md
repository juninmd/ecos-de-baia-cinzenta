# 🧠 AGENTS.md - Meu Livro Intelligence System

## 👤 AI Personas

### 1. Jules-Architect (System Architect)
- **Role**: Designing the core architecture and orchestrating logic.
- **Focus**: Scalability, process integrity, and high-level design.
- **Vibe**: Direct, analytical, and strategic.

### 2. Spark-Frontend (UI/UX Expert)
- **Role**: Crafting the visual identity and user interactions.
- **Focus**: Aesthetics, responsiveness, and accessibility.
- **Vibe**: Creative, detail-oriented, and user-focused.

### 3. Bolt-Automation (DevOps)
- **Role**: Managing CI/CD, scripts, and automation.
- **Focus**: Build pipelines, testing, and deployment.
- **Vibe**: Fast, technical, and "automation-first".

## 📜 Development Rules (Antigravity)

1. **Size Limit**: **Max 150 lines per file**.
2. **Clean Logic**: Separation of concerns enforced across all layers.
3. **Validation**: All changes require successful tests and linting.
4. **Security**: Sensitive data must be excluded from context.

## 🎭 Regras de Consistência Visual (OBRIGATÓRIAS)

> **Regra Zero: a fisionomia e a aparência dos personagens NUNCA mudam.**
> Um personagem gerado hoje tem que ser reconhecível como o mesmo de 200 capítulos atrás.
> Qualquer geração de imagem ou vídeo que viole isso deve ser descartada, não publicada.

1. **Âncora de imagem antes de texto.** Se o personagem tem retrato em
   `docs/public/personagens/`, a cena **tem** que ser gerada a partir dele (image-to-image /
   FLUX Kontext), nunca só por descrição textual. Texto sozinho reinventa o rosto a cada geração.
   O peso da âncora se ajusta ao plano (alto em close, baixo em plano aberto): peso fixo alto
   trava a identidade mas transforma toda cena em retrato frontal.
2. **`docs/personagens.md` é a fonte da verdade.** Vestuário, cabelo, olhos, porte e marcas
   distintivas vão sempre no prompt, com **vestuário primeiro** — é o traço que os modelos mais
   trocam por conta própria.
   - **Todo personagem tem retrato.** Perfil novo entra com `![Nome](/personagens/slug.png)` e
     um campo `**Prompt Visual:**` — a descrição física traduzida para inglês, porque o CLIP é
     treinado em inglês e ignora metade do português. Depois é só rodar
     `python -m scripts.art_gen.portraits`, que gera só o que falta, com seed determinística.
   - **O `Prompt Visual` tem que caber em 77 tokens.** É onde os dois encoders do SDXL cortam;
     acima disso os últimos traços somem em silêncio. O gerador avisa quando estoura.
   - `tests/test_personagens_dossie.py` trava as duas coisas: perfil sem retrato no disco ou
     sem campo visual obrigatório quebra a build.
3. **Retrato de referência é imutável.** Nunca sobrescreva um arquivo de
   `docs/public/personagens/`. Novo visual canônico = arquivo novo com sufixo
   (`elena_2.png`) + registro na "Linha do Tempo e Evolução Visual" do personagem.
4. **Seed determinística.** Mesma cena de mesmo capítulo tem que produzir a mesma imagem:
   `seed = numero_do_capitulo * 100 + indice_da_cena`. Nada de seed aleatória.
5. **Uma âncora por cena.** Escolha o personagem com mais menções reais no trecho e trave a
   identidade nele. Ignore aliases com menos de 4 caracteres — "O" de "O Taxidermista" casa com
   todo artigo em português e sequestra o ranking.
6. **Arte é cache, não descartável.** Toda cena gerada é commitada em
   `docs/public/cenas/capitulo_N/`. Regerar uma cena que já existe é proibido: gasta cota e
   introduz variação de aparência sem necessidade. A única exceção é a cena reprovada na
   homologação — refugo não é arte aprovada e não ocupa lugar de cena.
7. **Degradar sem quebrar a identidade.** Ordem de fallback: Kontext local → Kontext em Space →
   texto-para-imagem com descritor canônico → arte já existente do capítulo. Só se cai para o
   penúltimo nível é aceitável perder fidelidade — e a cena deve ser regerada depois, quando
   houver GPU/cota.
8. **Identidade sonora também é canônica.** Cada personagem tem uma voz fixa em
   `scripts/daily_telegram/voices.py`. A voz de um personagem nunca muda entre capítulos, e
   figurante nunca recebe o timbre de um protagonista — trocar a voz confunde tanto quanto
   trocar o rosto.
9. **Continuidade temporal.** Respeite a fase do personagem (`Linha do Tempo e Evolução Visual`
   em `docs/personagens.md`): Gabo com exoesqueleto no cap. 105 não pode aparecer sem ele.
   `scripts/art_gen/continuidade.py` lê essa linha do tempo e injeta a fase correta no prompt;
   o vestuário com fases declaradas (Dante) é escolhido pelo capítulo, nunca mandado inteiro.
10. **Dez cenas por capítulo.** O alvo da obra é `CENAS_POR_CAPITULO = 10` em
   `scripts/build_scene_manifest.py` — 2.350 imagens. Três imagens não cobrem um capítulo de
   1.100 palavras e faziam o livro inteiro repetir o mesmo trio de planos.
11. **Nenhuma imagem entra sem homologação.** `python scripts/homologar_cenas.py --realimentar`
   mede resolução, nitidez, contraste, arquivo chapado, texto queimado e cena repetida, escreve
   `docs/qualidade_imagens.md` e devolve as reprovadas para `docs/public/cenas/regerar.txt`.
   Fidelidade de rosto é auditada com visão (`--visao N`). O ciclo completo está em
   `docs/pipeline_imagens.md`.

## 📏 Padrão de Qualidade por Capítulo (OBRIGATÓRIO)

> Todo capítulo é avaliado nesta régua antes de ser considerado pronto.
> `python scripts/quality_gate.py` mede o que é mensurável e gera
> `docs/qualidade_capitulos.md`. O que a máquina não mede, o revisor lê.

### Portões duros (reprovam sozinhos)

| # | Portão | Limite |
|---|---|---|
| D1 | **Extensão** | ≥ 600 palavras (reprova abaixo disso: é cena, não capítulo). **Alvo: 1.100–1.600.** A mediana histórica da obra é 900, e capítulo curto é a causa número um de arco que não respira. |
| D2 | **Título** | Exatamente um H1, no formato `# Capítulo N: Título`, idêntico ao menu. |
| D3 | **Elenco declarado** | Bloco de metadados com Localização e Personagens Presentes. |
| D4 | **Traços canônicos** | Zero violações: Gabo nunca fuma; morto não age; fase física correta (exoesqueleto, prótese, braço amputado). |
| D5 | **Fechamento** | A última linha vira a página — imagem, decisão ou ameaça. Nunca resumo do que acabou de acontecer. |

### Régua de qualidade (0 a 2 por eixo, máximo 10)

| Eixo | 0 | 1 | 2 |
|---|---|---|---|
| **Atmosfera noir** | Só descrição visual | Dois sentidos | **Três ou mais sentidos**, e o ambiente tem opinião sobre os personagens |
| **Custo** | Ninguém perde nada | Perda reversível | **Perda permanente**: corpo, pessoa, crença ou opção |
| **Voz e personagem** | Todos falam igual | Protagonista tem voz | **Cada personagem fala do jeito dele** e o silêncio de alguém significa algo |
| **Ritmo** | Bloco único de exposição | Alterna diálogo e ação | **A informação chega por conflito**, nunca por alguém explicando |
| **Consequência** | Episódio isolado | Referencia o anterior | **Muda o que o leitor entende** de algo que já leu |

**Notas de corte:** 9–10 obra-prima · 7–8 publicável · 5–6 revisar · ≤4 reescrever.

### Regras de escrita que a régua cobra

1. **Sem solução fácil.** Se o problema se resolve por competência sem preço, o capítulo está errado. Gabo ganha quebrado ou não ganha.
2. **Exposição é conflito.** Ninguém explica lore para quem já sabe. Se dois personagens conversam sobre algo que ambos conhecem, é para o leitor — e isso se corta.
3. **Nada de segunda cena de travessia.** Descer túnel, atravessar duto e subir escada só valem quando terminam em porta que muda o gênero da história. Duas seguidas viram rotina.
4. **A dor tem contabilidade.** Ferimento aberto num capítulo aparece no próximo. Personagem não se cura entre cenas.
5. **Revelação precisa de plantio.** Toda reviravolta tem que se sustentar em material já publicado. Cite o capítulo de plantio no dossiê.

## 🤝 Interaction Protocol
- Follow the **Plan -> Act -> Validate** cycle for every task.
- Consult `GEMINI.md` for project-specific instructions.
